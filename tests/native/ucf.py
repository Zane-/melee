"""UCF in the native build against the UCF that Slippi ships, frame by frame.

    python tests/native/ucf.py [--seeds N] [--frames N]

The same controller input goes to three games each frame:

    slippi   the console's code in the simulator (tools/melee_sim) with
             Slippi's eight UCF codes injected where its Dolphin puts them
    native   the native build, UCF on (src/host/ucf.c, the overlay's C)
    vanilla  the native build, UCF off

First, what a player feels: Fox standing, the stick flicked back through a
halfway point. With UCF the dash starts after one frame of Turn; without
it, after five (four frames stuck turning).

Then "native" has to equal "slippi" on every frame: state, facing, hitlag and
hitstun exactly, and animation frame, position, speed, damage and shield
of both fighters to within rounding (--tolerance, as compare.py), and the
random seed. "vanilla" has to part from them somewhere,
and the injected code is watched to count how often each rule fired: a
rule that never fired is a failure, because then the input proved nothing
about it.

The input is tests/sim/ucf.py's (flicks through a halfway point, crouching
and out to the rim, shielding on a platform, flicks in hitlag, tumbling, a
random stick), with what that test writes into memory left out: here
nothing is moved, healed or given damage, so the fighters walk to where
each part happens. A match that ends early ends that seed's run.

Slippi's codes are read from a Slippi Launcher install; without one this
says so and stops. Needs the matching build (build/GALE01/main.dol) and the
native build. About half a minute a seed; the default six are what it
takes for every rule to fire (the two SDI ones are rare).
"""
import argparse
import importlib.util
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "tools/melee_native"))
sys.path.insert(0, str(ROOT / "tools/melee_sim"))

import compare  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "sim_ucf", ROOT / "tests/sim/ucf.py")
sim_ucf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim_ucf)


class Fighter:
    """A fighter as compare.py's state() gives it, under the names the
    script reads."""

    def __init__(self, p):
        self.fp = p is not None
        if p is None:
            return
        self.pos = (p["x"], p["y"])
        self.state, self.state_frame = p["state"], p["frame"]
        self.hitlag, self.hitstun = p["hitlag"], p["hitstun"]
        self.facing, self.air = p["facing"], p["air"]
        self.percent = p["percent"]


class NoMemory:
    """The script's writes into the game (damage, shield, position) are
    left out: they would have to be made the same way in two layouts."""

    def w32(self, *a):
        pass

    def wf32(self, *a):
        pass


class View:
    """What the script is given each frame: the fighters, and somewhere to
    put the pads."""

    def __init__(self, state):
        self.p = [Fighter(p) for p in state["p"]]
        self.m = NoMemory()
        self.h = type("Pads", (), {})()
        self.h.pads = [{"lx": 0, "ly": 0}, {"lx": 0, "ly": 0}]
        self.buttons = [[], []]

    def fighter(self, i):
        return self.p[i]

    def pad(self, i, buttons):
        self.buttons[i] = list(buttons)


class Script(sim_ucf.Script):
    @staticmethod
    def airborne(s, f):
        return bool(f.air)

    @staticmethod
    def put(s, f, x, y):
        pass

    def platform(self, s, a, d):
        # on the floor away from the left platform: walk under it first
        if not a.air and a.pos[1] < 20 and abs(a.pos[0] - PLATFORM_X) > 5:
            self.c, self.stood = 0, True
            return (-60 if a.pos[0] > PLATFORM_X else 60), 0, []
        return super().platform(s, a, d)


PLATFORM_X = sim_ucf.PLATFORM[0]


def run(seed, frames, codes, counts):
    """One seed. Returns (frames compared, first difference or None, the
    frame where vanilla parted or None, how it ended)."""
    sim = compare.SimSide()
    sim_ucf.inject(sim.s, codes, counts)
    native, plain = compare.NativeSide(), compare.NativeSide()
    sides = [sim, native, plain]
    try:
        if not native.n.ucf(True) or plain.n.ucf(False):
            return 0, ["the native switch did not answer as asked"], None, ""
        for side in sides:
            for _ in range(30):
                side.step()
            side.match("fox", "marth", "battlefield", seed)
        for side in sides:
            n = 0
            while side.state()["p"][0] is None:
                side.step()
                n += 1
                if n > 2000:
                    return 0, ["the match never started"], None, ""
        script = Script(seed)
        vanilla_parted = None
        for f in range(frames):
            st = [side.state() for side in sides]
            if st[0]["p"][0] is None or st[0]["p"][1] is None:
                return f, None, vanilla_parted, "the match ended"
            diff = compare.differences(st[0], st[1])
            if diff:
                return f, diff, vanilla_parted, ""
            if vanilla_parted is None and compare.differences(st[0], st[2]):
                vanilla_parted = f
            view = View(st[0])
            script.frame(view, f)
            for port in (0, 1):
                x, y = view.h.pads[port]["lx"], view.h.pads[port]["ly"]
                for side in sides:
                    side.pad(port, buttons=view.buttons[port],
                             stick=(x / 127.0, y / 127.0))
            for side in sides:
                side.step()
        return frames, None, vanilla_parted, ""
    finally:
        native.n.close()
        plain.n.close()


def dash_back(ucf):
    """Fox standing, facing right; the stick to the left the way a hand
    flicks it, part way (-40) for one frame and then all the way. How many
    frames he spends in Turn before the dash starts (None: no dash)."""
    from native import Native
    with Native() as n:
        n.ucf(ucf)
        n.start("fox", "marth", "final-destination")
        n.place(0, 0.0, 0.0, 1)
        n.pad(0)
        n.step(20)
        n.pad(0, stick=(-40 / 127.0, 0))
        n.step()
        turn = 1 if n.fighter(0).state == TURN else 0
        for _ in range(14):
            n.pad(0, stick=(-1.0, 0))
            n.step()
            f = n.fighter(0)
            if f.state == DASH and f.facing < 0:
                return turn
            turn += f.state == TURN
    return None


TURN, DASH = 18, 20


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--frames", type=int, default=2700)
    ap.add_argument("--tolerance", type=float, default=1e-4,
                    help="how far a position or speed may be from the "
                         "console's (rounding; compare.py's --tolerance). "
                         "States, frames, facing, hitlag and hitstun are "
                         "always compared exactly")
    args = ap.parse_args()
    compare.TOLERANCE = args.tolerance
    # Animation frame counters too: the native build can differ from the
    # console in their last bit, UCF or not (docs/ai/native-port.md, known
    # differences; met here once in six seeds, on player 2, whom UCF does
    # not move). A frame counter a whole frame off is still caught.
    compare.EXACT = tuple(k for k in compare.EXACT if k != "frame")
    if not sim_ucf.INI.exists():
        sys.exit("no Slippi Launcher install (%s): nothing to compare with"
                 % sim_ucf.INI)
    codes = sim_ucf.slippi_codes()
    if set(codes) != set(sim_ucf.SITES):
        sys.exit("Slippi's codes are not where expected")
    ok, counts, parted = True, {}, 0
    # what a player feels: three frames stuck turning, without UCF
    on, off = dash_back(True), dash_back(False)
    good = on == 1 and off is not None and off > on
    ok &= good
    print("%s  a dash back from standing, the stick part way for a frame: "
          "%s frame(s) in Turn with UCF, %s without" % (
              "ok  " if good else "FAIL", on, off))
    for seed in range(1, args.seeds + 1):
        t0 = time.time()
        n, diff, vfirst, how = run(seed, args.frames, codes, counts)
        parted += vfirst is not None
        if diff is None:
            print("ok    seed %d: identical to Slippi's UCF for %d frames%s; "
                  "the vanilla game %s  (%.0fs)" % (
                      seed, n, " (%s)" % how if how else "",
                      "parts from it at frame %d" % vfirst
                      if vfirst is not None else "never differs",
                      time.time() - t0))
        else:
            ok = False
            print("FAIL  seed %d: differs from Slippi's UCF at frame %d" %
                  (seed, n))
            for d in diff[:10]:
                print("        ", d)
    print("how often each rule fired in Slippi's code:")
    missing = []
    for addr, (rule, offs) in sim_ucf.SITES.items():
        for what in offs.values():
            k = counts.get(what, 0)
            print("   %-28s %d" % (what, k))
            if k == 0:
                missing.append(what)
    if parted == 0:
        ok = False
        print("FAIL  the vanilla game never differed: this input tests "
              "nothing")
    if missing:
        ok = False
        print("FAIL  never exercised: %s" % ", ".join(missing))
    print("PASS" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
