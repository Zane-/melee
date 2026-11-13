"""Does anything in a match depend on a variable the code never assigns?

The decompiled C matches the console's code even where that code reads a
local variable it did not assign: on the console the register holds
something definite, natively the stack holds whatever was there. The
compiler lists about two hundred places where that may happen. This test
asks which of them matter in play: the game is built twice, with every
unassigned local starting as zero and as bytes of 0xFE
(`tools/native_build.py --auto-init zero|pattern`), and the two are given
the same matches with the same random inputs. If nothing read depends on
an unassigned variable, they play the same game, frame for frame.

    python tools/native_build.py --auto-init zero
    python tools/native_build.py --auto-init pattern
    python tests/native/uninit.py [--frames N] [--matches N]

It can only speak for what the matches exercised.
"""
import argparse
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "melee_native"))
from native import CHARACTERS, STAGES, Native, NativeError  # noqa: E402

BUILDS = {
    "zero": ROOT / "build/native-init-zero/melee_headless",
    "pattern": ROOT / "build/native-init-pattern/melee_headless",
    "plain": ROOT / "build/native/melee_headless",
}


def play(exe, p1, p2, stage, seed, frames):
    """Every frame's state under random inputs; and why it stopped early,
    if it did."""
    rng = random.Random(seed)
    out = []
    try:
        with Native(exe=exe) as n:
            n.start(p1, p2, stage, seed=seed)
            for _ in range(frames):
                for port in (0, 1):
                    if rng.random() < 0.25:
                        n.pad(port,
                              buttons=[b for b in "ABXYZLR"
                                       if rng.random() < 0.12],
                              stick=(rng.choice((-1, -0.5, 0, 0.5, 1)),
                                     rng.choice((-1, -0.5, 0, 0, 1))),
                              cstick=(rng.choice((-1, 0, 0, 0, 1)),
                                      rng.choice((-1, 0, 0, 0, 1))),
                              l=rng.choice((0, 0, 0, 0.5, 1)))
                n.step()
                s = n.state()
                out.append((s["rng"], s["p"], s["items"]))
    except NativeError as e:
        return out, str(e).strip().splitlines()[-1][:160]
    return out, None


def first_difference(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            what = []
            if x[0] != y[0]:
                what.append("the random stream")
            for port, (f, g) in enumerate(zip(x[1], y[1])):
                keys = [k for k in f if f.get(k) != g.get(k)]
                if keys:
                    what.append("player %d: %s" % (port + 1,
                                                   ", ".join(keys[:6])))
            if x[2] != y[2]:
                what.append("items")
            return i, "; ".join(what)
    if len(a) != len(b):
        return min(len(a), len(b)), "one stopped"
    return None, ""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--frames", type=int, default=1500)
    ap.add_argument("--matches", type=int, default=12)
    args = ap.parse_args()
    for name in ("zero", "pattern"):
        if not BUILDS[name].exists():
            sys.exit("build it first: python tools/native_build.py "
                     "--auto-init " + name)
    pick = random.Random(2026)
    names = sorted(CHARACTERS)
    stages = sorted(STAGES)
    bad = 0
    for m in range(args.matches):
        p1, p2 = pick.choice(names), pick.choice(names)
        stage = pick.choice(stages)
        seed = pick.randrange(1, 1 << 30)
        runs = {name: play(exe, p1, p2, stage, seed, args.frames)
                for name, exe in BUILDS.items() if exe.exists()}
        notes = []
        for name, (frames, stopped) in runs.items():
            if stopped:
                notes.append("%s stopped at frame %d: %s" % (
                    name, len(frames), stopped))
        for other in ("pattern", "plain"):
            if other not in runs:
                continue
            at, what = first_difference(runs["zero"][0], runs[other][0])
            if at is not None:
                notes.append("zero and %s differ from frame %d (%s)" % (
                    other, at, what))
        ok = not notes
        bad += not ok
        print("%s  %s against %s on %s, seed %d, %d frames%s" % (
            "ok  " if ok else "FAIL", p1, p2, stage, seed,
            len(runs["zero"][0]), "".join("\n        " + n for n in notes)))
    print("%d of %d matches the same in every build" % (
        args.matches - bad, args.matches))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
