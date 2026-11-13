#!/usr/bin/env python3
"""Does the native build play the same game as the console's code?

Runs one match twice with the same inputs: in the Python simulator
(tools/melee_sim, the retail PowerPC code in a CPU emulator, already checked
against Dolphin) and in the native build. Both enter it the same way, through
the game's debug VS mode, with the same random seed. Each frame the random
seed and both fighters are compared; the first difference is reported.

    python tools/melee_native/compare.py                 # a scripted exchange
    python tools/melee_native/compare.py --random 3 --frames 600
    python tools/melee_native/compare.py --p1 marth --p2 fox

Needs the matching build (build/GALE01/main.dol) and the native build
(python tools/native_build.py).
"""
import argparse
import random
import struct
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools/melee_sim"))

from native import Native, CHARACTERS, STAGES  # noqa: E402

FIELDS = ("state", "frame", "x", "y", "vx", "vy", "facing", "air", "percent",
          "hitlag", "hitstun", "shield", "gvel")
# Compared exactly even with --tolerance: what the game decides, as opposed
# to where rounding has put a fighter.
EXACT = ("state", "frame", "facing", "air", "hitlag", "hitstun")
TOLERANCE = 0.0


class SimSide:
    """The retail code, entering debug VS the way src/host/match.c does."""

    def __init__(self):
        from sim import Sim
        self.s = Sim(dol=ROOT / "build/GALE01/main.dol")
        self.s.boot()
        self.m = self.s.m
        self.requested = False
        self.setup = None
        m = self.m
        self.ovr = self.s.h.scratch + 0x3000
        m.write(self.ovr, struct.pack(">I", 0x4E800020))
        decide = m.sym.addr("lbCardGame_DecideGameMode")

        def override(mm):
            if self.requested:
                self.requested = False
                return 0x0E          # GM_DEBUG_VS
            mm.tail_call(decide)
        m.hook(self.ovr, override)

        # The mode's own state (onEnterDebugVs) fills the start data and
        # ends with gm_LoadAnnouncer: the host's choices go in there.
        body = self.s._relocate_entry(m.sym.addr("gm_LoadAnnouncer"))
        start = m.sym.addr("gmVsMelee_StartData")

        def announcer(mm):
            if self.setup is not None:
                p1, p2, stage, seed, p2_human = self.setup
                self.setup = None
                mm.write(start + 0x60, bytes([p1]))
                mm.write(start + 0x60 + 0x24, bytes([p2]))
                mm.write(start + 0x60 + 0x24 + 1,
                         bytes([0 if p2_human else 1]))
                mm.write(start + 0x0E, struct.pack(">H", stage))
                mm.write(mm.u32(mm.sym.addr("HSD_RandSeedPtr")),
                         struct.pack(">I", seed))
            mm.pc = body
        m.hook("gm_LoadAnnouncer", announcer)

    def match(self, p1, p2, stage, seed, p2_human=True):
        self.setup = (CHARACTERS[p1], CHARACTERS[p2], STAGES[stage], seed,
                      p2_human)
        self.requested = True
        self.s.h.pads[1]["connected"] = True

    def step(self):
        # What host_match_install does at each frame boundary.
        self.s.call("gm_SetGameModeOverride", self.ovr)
        if self.requested:
            self.s.call("gm_801A4B60")
        self.s.step()

    def pad(self, *a, **k):
        self.s.pad(*a, **k)

    def state(self):
        m = self.m
        out = {"rng": m.u32(m.u32(m.sym.addr("HSD_RandSeedPtr"))), "p": []}
        for i in range(2):
            f = self.s.fighter(i)
            if not f.fp:
                out["p"].append(None)
                continue
            x, y = f.pos
            vx, vy = f.vel
            out["p"].append({
                "state": f.state, "frame": f.state_frame, "x": x, "y": y,
                "vx": vx, "vy": vy, "facing": f.facing,
                "air": int(f.airborne), "percent": f.percent,
                "hitlag": f.hitlag, "hitstun": f.hitstun,
                "shield": f.shield, "gvel": f._f32(0xEC)})
        return out


class NativeSide:
    def __init__(self):
        self.n = Native()

    def match(self, p1, p2, stage, seed, p2_human=True):
        self.n.match(p1, p2, stage, seed, p2_human)

    def step(self):
        self.n.step()

    def pad(self, *a, **k):
        self.n.pad(*a, **k)

    def state(self):
        return self.n.state()


def scripted():
    """(frame after the fighters appear, port, pad arguments)."""
    return [
        (150, 0, dict(stick=(1, 0))),              # Fox runs at Marth
        (190, 0, dict()),
        (215, 0, dict(buttons=["A"])),             # jab
        (218, 0, dict()),
        (250, 0, dict(stick=(0, 1), buttons=["A"])),   # up smash
        (253, 0, dict()),
        (300, 1, dict(buttons=["X"])),             # Marth jumps
        (303, 1, dict()),
        (310, 1, dict(stick=(-1, 0), buttons=["A"])),  # forward air
        (313, 1, dict()),
        (360, 0, dict(buttons=["B"], stick=(0, -1))),  # shine
        (363, 0, dict()),
        (400, 0, dict(r=1.0, buttons=["R"])),      # shield
        (430, 0, dict()),
        (440, 1, dict(cstick=(-1, 0))),            # Marth forward smash
        (443, 1, dict()),
    ]


def random_script(seed, frames):
    rng = random.Random(seed)
    out = []
    t = 130
    while t < frames:
        port = rng.randrange(2)
        buttons = [b for b in ("A", "B", "X", "Z", "R", "L")
                   if rng.random() < 0.12]
        stick = (rng.choice((-1, -0.5, 0, 0, 0.5, 1)),
                 rng.choice((-1, -0.5, 0, 0, 0.5, 1)))
        cstick = (rng.choice((-1, 0, 0, 0, 1)), rng.choice((-1, 0, 0, 0, 1)))
        out.append((t, port, dict(buttons=buttons, stick=stick,
                                  cstick=cstick,
                                  r=1.0 if "R" in buttons else 0)))
        t += rng.randrange(1, 12)
    return out


def f32(v):
    """As a 32-bit float: the native side prints the shortest decimal that
    names its float, the simulator reads the float itself."""
    return struct.unpack("f", struct.pack("f", v))[0]


def differences(a, b):
    out = []
    if a["rng"] != b["rng"]:
        out.append("rng %d / %d" % (a["rng"], b["rng"]))
    for i in range(2):
        fa, fb = a["p"][i], b["p"][i]
        if (fa is None) != (fb is None):
            out.append("P%d exists %s / %s" % (i + 1, fa is not None,
                                               fb is not None))
            continue
        if fa is None:
            continue
        for k in FIELDS:
            va, vb = f32(fa[k]), f32(fb[k])
            if k in EXACT or TOLERANCE == 0:
                same = va == vb
            else:
                same = abs(va - vb) <= TOLERANCE * max(1.0, abs(va), abs(vb))
            if not same:
                out.append("P%d %s %r / %r" % (i + 1, k, fa[k], fb[k]))
    return out


def run(args, script, label):
    t0 = time.time()
    sides = [SimSide(), NativeSide()]
    try:
        for side in sides:
            for _ in range(30):
                side.step()
            side.match(args.p1, args.p2, args.stage, args.seed)
        # Until the fighters exist; the two may take different numbers of
        # frames to get there (loading is not the same work).
        started = []
        for side in sides:
            n = 0
            while side.state()["p"][0] is None:
                side.step()
                n += 1
                if n > 2000:
                    sys.exit("the match never started")
            started.append(n)
        events = sorted(script, key=lambda e: e[0])
        first = None
        same = 0
        history = []
        for t in range(args.frames):
            while events and events[0][0] == t:
                _, port, kw = events.pop(0)
                for side in sides:
                    side.pad(port, **kw)
            sa, sb = (side.state() for side in sides)
            history.append((t, sa, sb))
            del history[:-(args.show + 1)]
            diff = differences(sa, sb)
            if diff:
                first = (t, diff, sa, sb)
                break
            same += 1
            for side in sides:
                side.step()
    finally:
        sides[1].n.close()
    took = time.time() - t0
    if first is None:
        print("%s: identical for %d frames (frames to load: simulator %d, "
              "native %d; %.0fs)" % (label, same, started[0], started[1],
                                     took))
        return True
    t, diff, sa, sb = first
    print("%s: identical for %d frames, then at frame %d (simulator / "
          "native):" % (label, same, t))
    for d in diff[:12]:
        print("   ", d)
    for ht, ha, hb in history[:-1] if args.show else []:
        for name, st in (("sim", ha), ("nat", hb)):
            print("    %4d %s " % (ht, name) + "  ".join(
                "P%d st %d f %.9g x %.9g vx %.9g gvel %.9g" % (
                    i + 1, p["state"], f32(p["frame"]), f32(p["x"]),
                    f32(p["vx"]), f32(p["gvel"]))
                for i, p in enumerate(st["p"]) if p))
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--p1", default="fox")
    ap.add_argument("--p2", default="marth")
    ap.add_argument("--stage", default="final-destination")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--frames", type=int, default=520)
    ap.add_argument("--tolerance", type=float, default=0.0, metavar="T",
                    help="accept positions, speeds, damage and shield that "
                         "differ by less than this (relative); states, "
                         "frame counters and the random seed stay exact")
    ap.add_argument("--show", type=int, default=0, metavar="N",
                    help="print the N frames before the first difference")
    ap.add_argument("--random", type=int, default=0, metavar="N",
                    help="N runs of random inputs instead of the script")
    args = ap.parse_args()
    global TOLERANCE
    TOLERANCE = args.tolerance
    ok = True
    if args.random:
        for i in range(args.random):
            ok &= run(args, random_script(i + 1, args.frames),
                      "random %d" % (i + 1))
    else:
        ok = run(args, scripted(), "scripted")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
