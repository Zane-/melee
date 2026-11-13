"""Measure, for every character, how far away a running fighter has to
start each rush move for it to connect, and write data/actor/reach.json.

    python tools/melee_actor/calibrate.py [character ...]

A running grab slides a long way before its grab box is out; started too
close it ends up behind the target. So for each move there is a band of
distances that work, and the actor starts the move in the middle of it. The
band is found by trying: the actor runs at a standing Marth from 60 units
away and gives the input at each distance in turn, a few thousand frames a
character, on the native build.

The target matters (its width, and whether it stands or leans): these are
numbers for a standing Marth. Scenarios with other targets should be run
with --jitter to see if they hold.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(HERE, "..", "melee_native"))
sys.path.insert(0, os.path.join(HERE, ".."))
from native import CHARACTERS, Native, NativeError  # noqa: E402
from melee_actor import actor as act               # noqa: E402

OUT = os.path.join(ROOT, "data", "actor", "reach.json")
DISTANCES = range(5, 46)


def band(good):
    """The longest run of consecutive distances that worked: (lo, hi)."""
    best, run = None, []
    for d in DISTANCES:
        if d in good:
            run.append(d)
            if best is None or len(run) > best[1] - best[0] + 1:
                best = (run[0], run[-1])
        else:
            run = []
    return best


def measure(name):
    out = {}
    with Native() as n:
        n.start(name, "marth")
        n.place(0, -40.0, 0.0, facing=1)
        n.place(1, 20.0, 0.0, facing=-1)
        n.step()
        base = n.snapshot()
        for move in act.RUSH:
            good = set()
            for d in DISTANCES:
                n.restore(base)
                r = act.Actor(n, 0, 1).run([{"do": "rush", "move": move,
                                             "reach": d, "timeout": 150}])
                step = r["steps"][0]
                if step.get("grabbed") or step.get("damage", 0) > 0:
                    good.add(d)
            b = band(good)
            if b is not None and b[1] - b[0] >= 3:
                out[move] = dict(reach=round((b[0] + b[1]) / 2.0, 1),
                                 band=list(b))
    return out


def main():
    names = sys.argv[1:] or sorted(CHARACTERS, key=CHARACTERS.get)
    try:
        with open(OUT) as f:
            data = json.load(f)
    except (OSError, ValueError):
        data = dict(reach={}, bands={}, names={})
    for name in names:
        try:
            m = measure(name)
        except NativeError as e:
            print("%-18s failed: %s" % (name, str(e).splitlines()[0]))
            continue
        kind = str(CHARACTERS[name])
        data["reach"][kind] = {mv: v["reach"] for mv, v in m.items()}
        data["bands"][kind] = {mv: v["band"] for mv, v in m.items()}
        data["names"][kind] = name
        print("%-18s %s" % (name, "  ".join(
            "%s %g (%d-%d)" % (mv, v["reach"], v["band"][0], v["band"][1])
            for mv, v in m.items()) or "nothing connected"))
    data["about"] = ("How far from a standing Marth a running fighter starts "
                     "each move for it to connect: the middle of the band of "
                     "distances that worked. Made by "
                     "tools/melee_actor/calibrate.py on the native build.")
    data["measured"] = datetime.date.today().isoformat()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
