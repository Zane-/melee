"""Drive the native headless game (build/native/melee_headless).

    from native import Native
    n = Native()
    n.step(30)
    n.match("fox", "marth")            # the game's debug VS mode, no menus
    n.step(200)
    n.pad(0, stick=(1, 0)); n.step(40)
    print(n.fighter(0))

The interface follows tools/melee_sim/sim.py where the two overlap: pad()
holds a controller state until changed, step() advances whole frames,
fighter() reads a player's fighter. The process speaks the line protocol of
src/host/control.c.
"""
import json
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


class NativeError(RuntimeError):
    pass


class Native:
    def __init__(self, exe=EXE, disc=None, draw=False, verbose=False):
        cmd = [str(exe), "--control", "--disc",
               str(disc or ROOT / "build/disc")]
        if draw:
            cmd.append("--draw")
        if verbose:
            cmd.append("-v")
        self.log = []          # everything the process printed besides replies
        self.frame = 0
        self.p = subprocess.Popen(cmd, cwd=ROOT, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True)
        self._wait_frame()

    def _reply(self):
        while True:
            line = self.p.stdout.readline()
            if not line:
                raise NativeError("the game stopped:\n" +
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
        self.p.stdin.write(text + "\n")
        self.p.stdin.flush()
        return self._reply()

    def step(self, frames=1):
        self.p.stdin.write("step %d\n" % frames)
        self.p.stdin.flush()
        self._wait_frame()
        return self.frame

    def pad(self, port=0, buttons=(), stick=(0, 0), cstick=(0, 0), l=0, r=0):
        b = sum(BUTTONS[x.upper()] for x in buttons)
        lx, ly = (int(round(max(-1, min(1, v)) * 127)) for v in stick)
        cx, cy = (int(round(max(-1, min(1, v)) * 127)) for v in cstick)
        self._cmd("pad %d %x %d %d %d %d %d %d" % (
            port, b, lx, ly, cx, cy, int(l * 255), int(r * 255)))

    def match(self, p1="fox", p2="marth", stage="final-destination", seed=1,
              p2_human=True):
        self._cmd("match %d %d %d %d %d" % (
            CHARACTERS[p1], CHARACTERS[p2], STAGES[stage],
            1 if p2_human else 0, seed))

    def state(self):
        """Frame, random seed and both fighters (None before they exist)."""
        return json.loads(self._cmd("state"))

    def fighter(self, i):
        return json.loads(self._cmd("fighter %d" % i))

    def seed(self, value):
        self._cmd("seed %d" % value)

    def close(self):
        if self.p.poll() is None:
            try:
                self.p.stdin.write("quit\n")
                self.p.stdin.flush()
                self.p.wait(timeout=5)
            except Exception:
                self.p.kill()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
