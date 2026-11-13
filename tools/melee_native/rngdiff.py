#!/usr/bin/env python3
"""Which code drew random numbers differently in one frame?

Replays compare.py's scripted exchange (or --random N) up to a frame and
lists, for the next frame, the callers of every random draw in the
simulator and in the native build, side by side from the first difference.

    python tools/melee_native/rngdiff.py 252
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compare  # noqa: E402
from native import EXE  # noqa: E402


def names(addrs):
    if not addrs:
        return []
    out = subprocess.run(["addr2line", "-f", "-e", str(EXE)] + addrs,
                         capture_output=True, text=True).stdout.split("\n")
    return out[0::2][:len(addrs)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("frame", type=int)
    ap.add_argument("--random", type=int, default=0)
    ap.add_argument("--frames", type=int, default=600)
    ap.add_argument("--p1", default="fox")
    ap.add_argument("--p2", default="marth")
    ap.add_argument("--stage", default="final-destination")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    script = (compare.random_script(args.random, args.frames)
              if args.random else compare.scripted())
    sides = [compare.SimSide(), compare.NativeSide()]
    try:
        for side in sides:
            for _ in range(30):
                side.step()
            side.match(args.p1, args.p2, args.stage, args.seed)
            while side.state()["p"][0] is None:
                side.step()
        events = sorted(script, key=lambda e: e[0])
        sim, nat = sides
        m = sim.m
        for t in range(args.frame + 1):
            while events and events[0][0] == t:
                _, port, kw = events.pop(0)
                for side in sides:
                    side.pad(port, **kw)
            if t == args.frame:
                for f in ("HSD_Rand", "HSD_Randf", "HSD_Randi"):
                    m.trace(f, 1)
                m.log.clear()
            for side in sides:
                side.step()
        a = [l.split(" from ")[1].split("+")[0] for l in m.log
             if not l.split(" from ")[1].startswith("HSD_Randi")]
        b = names(["0x" + x for x in nat.n._cmd("rng").split()])
    finally:
        sides[1].n.close()
    print("frame %d: %d draws in the simulator, %d native" % (
        args.frame, len(a), len(b)))
    first = next((i for i in range(max(len(a), len(b)))
                  if i >= len(a) or i >= len(b) or a[i] != b[i]), None)
    if first is None:
        print("the same callers in the same order")
        return
    print("the same for the first %d; then (simulator / native):" % first)
    for i in range(first, min(first + 12, max(len(a), len(b)))):
        print("  %3d  %-28s %s" % (i, a[i] if i < len(a) else "-",
                                   b[i] if i < len(b) else "-"))


if __name__ == "__main__":
    main()
