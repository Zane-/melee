"""Drive the native headless game (build/native/melee_headless).

    from native import Native
    with Native() as n:
        n.start("fox", "marth")            # a match, both pads ours, no menus
        n.pad(0, stick=(1, 0)); n.step(40)
        print(n.fighter(0).pos, n.fighter(1).percent)
        here = n.snapshot()                # the whole game, as it is now
        n.pad(0, buttons=["A"]); n.step(30)
        n.restore(here)                    # ...and back, as often as wanted

The interface follows tools/melee_sim/sim.py where the two overlap, so code
written for one runs on the other (the Melee Actor does): pad() holds a
controller state until changed, step() advances whole frames, fighter()
reads a player's fighter. One step is one exchange with the process (the
`tick` command of src/host/control.c): pads in, the frame's state out.

The game is a 32-bit process, so it cannot be loaded into Python; anything
that decides inputs (a script, a trained policy, a model) lives on this side
of the pipe.
"""
import json
import os
import re
import select
import signal
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "build/native/melee_headless"

BUTTONS = {"LEFT": 0x0001, "RIGHT": 0x0002, "DOWN": 0x0004, "UP": 0x0008,
           "Z": 0x0010, "R": 0x0020, "L": 0x0040, "A": 0x0100, "B": 0x0200,
           "X": 0x0400, "Y": 0x0800, "START": 0x1000}
# CharacterKind (src/melee/ft/forward.h), by data/ character id
CHARACTERS = {
    "captain-falcon": 0x00, "donkey-kong": 0x01, "fox": 0x02,
    "mr-game-and-watch": 0x03, "kirby": 0x04, "bowser": 0x05, "link": 0x06,
    "luigi": 0x07, "mario": 0x08, "marth": 0x09, "mewtwo": 0x0A,
    "ness": 0x0B, "peach": 0x0C, "pikachu": 0x0D, "ice-climbers": 0x0E,
    "jigglypuff": 0x0F, "samus": 0x10, "yoshi": 0x11, "zelda": 0x12,
    "sheik": 0x13, "falco": 0x14, "young-link": 0x15, "dr-mario": 0x16,
    "roy": 0x17, "pichu": 0x18, "ganondorf": 0x19,
}
STAGES = {"fountain-of-dreams": 0x02, "pokemon-stadium": 0x03,
          "yoshis-story": 0x08, "dream-land": 0x1C, "battlefield": 0x1F,
          "final-destination": 0x20}


def _json(text):
    # C prints nan and inf; JSON's spelling is NaN and Infinity.
    text = re.sub(r"-?nan", "NaN", text)
    text = re.sub(r"(-?)inf", r"\1Infinity", text)
    return json.loads(text)


class NativeError(RuntimeError):
    pass


class Fighter:
    """A player's fighter in the last frame's state. The same attributes as
    tools/melee_sim/sim.py's Fighter."""

    def __init__(self, d):
        self.d = d
        self.fp = 1 if d else 0          # truthy when the fighter exists

    kind = property(lambda s: s.d["kind"])            # internal fighter kind
    ckind = property(lambda s: s.d["ckind"])          # the roster's number
    state = property(lambda s: s.d["state"])
    state_frame = property(lambda s: s.d["frame"])
    facing = property(lambda s: s.d["facing"])
    pos = property(lambda s: (s.d["x"], s.d["y"]))
    vel = property(lambda s: (s.d["vx"], s.d["vy"]))
    airborne = property(lambda s: bool(s.d["air"]))
    percent = property(lambda s: s.d["percent"])
    hitlag = property(lambda s: s.d["hitlag"])
    hitstun = property(lambda s: s.d["hitstun"])
    shield = property(lambda s: s.d["shield"])
    jumps_used = property(lambda s: s.d["jumps"])
    invulnerable = property(lambda s: bool(s.d["invuln"]))
    stocks = property(lambda s: s.d["stocks"])
    # one of its attack's hitboxes is out this frame
    hitbox = property(lambda s: bool(s.d["hitbox"]))

    def summary(self):
        if not self.fp:
            return "(no fighter)"
        return "state %d f%.0f pos (%.1f, %.1f) %s %.0f%%" % (
            self.state, self.state_frame, self.pos[0], self.pos[1],
            "air" if self.airborne else "ground", self.percent)


class _Pads:
    """What each controller is holding, as the simulator keeps it
    (`sim.h.pads`), for code that reads the pads back."""

    def __init__(self):
        self.pads = [dict(buttons=0, lx=0, ly=0, cx=0, cy=0, lt=0, rt=0,
                          connected=(i == 0)) for i in range(4)]


def die_with_parent():
    """For Popen's preexec_fn: the child is killed when this process ends,
    however it ends (a `timeout` around a test kills the driver without
    letting it clean up; games were left running that way)."""
    import ctypes
    ctypes.CDLL("libc.so.6").prctl(1, signal.SIGKILL)  # PR_SET_PDEATHSIG


class Native:
    def __init__(self, exe=EXE, disc=None, draw=False, verbose=False,
                 timeout=120, env=None):
        cmd = [str(exe), "--control", "--disc",
               str(disc or ROOT / "build/disc")]
        if draw:
            cmd.append("--draw")
        if verbose:
            cmd.append("-v")
        self.log = []          # everything the process printed besides replies
        self.frame = 0
        self.timeout = timeout
        self.h = _Pads()
        self._dirty = set()    # ports whose pad the game has not been told
        self._state = None     # the last frame's state, if still current
        self._snaps = {}       # snapshot id -> (frame, pads) on this side
        # Its own process group: snapshots are further processes, and all
        # of them go when this object is closed.
        self.p = subprocess.Popen(cmd, cwd=ROOT, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True,
                                  start_new_session=True, env=env,
                                  preexec_fn=die_with_parent)
        self._out = self.p.stdout.fileno()
        self._pending = b""    # read from the game, not yet a whole line
        self._wait_frame()

    # ---- the pipe -------------------------------------------------------------

    def _line(self):
        """The game's next line, "" at the end of its output. Raises if it
        says nothing for `timeout` seconds: with snapshots asleep the pipe
        stays open after a crash, and a hung game says nothing either."""
        while b"\n" not in self._pending:
            if not select.select([self._out], [], [], self.timeout)[0]:
                raise NativeError("no reply in %d s:\n" % self.timeout +
                                  "".join(self.log[-40:]))
            chunk = os.read(self._out, 65536)
            if not chunk:
                rest, self._pending = self._pending, b""
                return rest.decode(errors="replace")
            self._pending += chunk
        line, _, self._pending = self._pending.partition(b"\n")
        return line.decode(errors="replace") + "\n"

    def _reply(self):
        while True:
            line = self._line()
            if not line or line.startswith("@ fatal"):
                how = ""
                if not line:
                    try:
                        code = self.p.wait(timeout=2)
                        how = (" (killed by signal %d)" % -code if code < 0
                               else " (exit status %d)" % code)
                    except Exception:
                        pass
                raise NativeError("the game stopped%s:\n" % how +
                                  "".join(self.log[-40:]))
            if line.startswith("@ "):
                return line[2:].rstrip("\n")
            self.log.append(line)

    def _wait_frame(self):
        reply = self._reply()
        if not reply.startswith("frame "):
            raise NativeError("expected a frame, got " + reply)
        self.frame = int(reply.split()[1])

    def _cmd(self, text):
        self._flush_pads()
        self._state = None
        self.p.stdin.write(text + "\n")
        self.p.stdin.flush()
        reply = self._reply()
        if reply.startswith("error"):
            raise NativeError(reply)
        return reply

    def _pad_words(self, port):
        p = self.h.pads[port]
        return "%d %x %d %d %d %d %d %d" % (
            port, p["buttons"], p["lx"], p["ly"], p["cx"], p["cy"], p["lt"],
            p["rt"])

    def _flush_pads(self):
        for port in sorted(self._dirty):
            self.p.stdin.write("pad " + self._pad_words(port) + "\n")
            self.p.stdin.flush()
            self._reply()
        self._dirty.clear()

    # ---- driving ------------------------------------------------------------------

    def pad(self, port=0, buttons=(), stick=(0, 0), cstick=(0, 0), l=0, r=0):
        """Set a controller's state until changed. Buttons by name
        (A B X Y Z L R START and D-pad UP DOWN LEFT RIGHT), sticks -1..1,
        analog triggers 0..1. Takes effect with the next step."""
        p = self.h.pads[port]
        p["connected"] = True
        p["buttons"] = sum(BUTTONS[x.upper()] for x in buttons)
        p["lx"], p["ly"] = (int(round(max(-1, min(1, v)) * 127))
                            for v in stick)
        p["cx"], p["cy"] = (int(round(max(-1, min(1, v)) * 127))
                            for v in cstick)
        p["lt"], p["rt"] = int(l * 255), int(r * 255)
        self._dirty.add(port)

    def step(self, frames=1):
        """Run whole frames with the pads as they are. Returns the frame
        number; state() and fighter() then cost nothing more."""
        words = " ".join(self._pad_words(port) for port in sorted(self._dirty))
        self._dirty.clear()
        self.p.stdin.write("tick %d %s\n" % (frames, words))
        self.p.stdin.flush()
        self._state = _json(self._reply())
        self.frame = self._state["frame"]
        return self.frame

    def match(self, p1="fox", p2="marth", stage="final-destination", seed=1,
              p2_human=True):
        """Ask for a match (the game's debug VS mode). It loads over the
        next frames; start() also waits for it."""
        self._cmd("match %d %d %d %d %d" % (
            CHARACTERS[p1], CHARACTERS[p2], STAGES[stage],
            1 if p2_human else 0, seed))
        self.match_info = dict(p1=p1, p2=p2, stage=stage, seed=seed,
                               p2_human=p2_human)

    def start(self, p1="fox", p2="marth", stage="final-destination", seed=1,
              p2_human=True, settle=True):
        """A match with both fighters standing on the stage, ready to act:
        boot, ask for the match, wait for the fighters, and (settle) for
        them to land from their entrance and the countdown to end."""
        self.step(30)
        # A match may already be running: its fighters go before the new
        # ones come, and "both fighters exist" must mean the new ones.
        had = bool(self.fighter(0).fp)
        self.match(p1, p2, stage, seed, p2_human)
        if had:
            for _ in range(300):
                self.step()
                if not self.fighter(0).fp:
                    break
        for _ in range(600):
            self.step()
            if self.fighter(0).fp and self.fighter(1).fp:
                break
        else:
            raise NativeError("the match never started")
        if settle:
            # the countdown holds every fighter in place; it is over when a
            # held jump gets one off the ground
            for _ in range(400):
                self.pad(0, buttons=["X"])
                self.step()
                if self.fighter(0).airborne and self.fighter(0).state in (
                        25, 26):
                    break
            self.pad(0)
            for _ in range(200):
                self.step()
                if not self.fighter(0).airborne and \
                        not self.fighter(1).airborne and \
                        self.fighter(0).state == 14 and \
                        self.fighter(1).state == 14:
                    break
        return self

    def place(self, port, x, y=0.0, facing=1, air=False, percent=0.0):
        """Put a fighter standing on the floor at or below (x, y), or (air)
        falling from there: not holding or held, no speed, that much
        damage, a full shield. Raises if there is no floor below."""
        self._cmd("place %d %.9g %.9g %d %d %.9g" % (
            port, x, y, 1 if facing >= 0 else -1, 1 if air else 0, percent))

    # ---- reading --------------------------------------------------------------------

    def state(self):
        """Frame, random seed, both fighters (None before they exist) and
        the items."""
        if self._state is None:
            self._state = _json(self._cmd("state"))
        return self._state

    def fighter(self, i):
        return Fighter(self.state()["p"][i])

    def seed(self, value):
        self._cmd("seed %d" % value)

    # ---- snapshots ------------------------------------------------------------------

    def snapshot(self):
        """Keep the game as it is now; returns a handle for restore(). A
        snapshot is a sleeping copy of the process, taken in well under a
        millisecond and sharing memory with the game until either changes
        it. drop() it when done; all are gone when this object closes."""
        reply = self._cmd("snap")
        snap = int(reply.split()[1])
        self._snaps[snap] = (self.frame, [dict(p) for p in self.h.pads])
        return snap

    def restore(self, snap):
        """Go back to a snapshot. It stays, and can be restored again."""
        if snap not in self._snaps:
            raise NativeError("no snapshot %r" % (snap,))
        reply = self._cmd("restore %d" % snap)
        if not reply.startswith("restored"):
            raise NativeError("restore: " + reply)
        self.frame, pads = self._snaps[snap]
        self.h.pads = [dict(p) for p in pads]
        self._dirty.clear()
        self._state = None

    def drop(self, snap):
        if self._snaps.pop(snap, None) is not None:
            self._cmd("drop %d" % snap)

    # ---- ending ---------------------------------------------------------------------

    def close(self):
        try:
            self.p.stdin.write("quit\n")
            self.p.stdin.flush()
        except Exception:
            pass
        for pipe in (self.p.stdin, self.p.stdout):
            try:
                pipe.close()
            except Exception:
                pass
        # the runner may be a later process than the one started; the group
        # is all of them
        try:
            os.killpg(self.p.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            self.p.wait(timeout=5)
        except Exception:
            self.p.kill()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def __del__(self):
        try:
            if self.p.poll() is None or self._snaps:
                self.close()
        except Exception:
            pass
