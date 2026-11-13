#!/usr/bin/env python3
"""The native build against the console's code, across characters and stages.

One line per matchup: a run of compare.py with random inputs. The native
build's regression test.

    python tools/melee_native/survey.py              # the standard list
    python tools/melee_native/survey.py --frames 900 --runs 2
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

MATCHUPS = [
    ("fox", "marth", "final-destination"),
    ("falco", "sheik", "battlefield"),
    ("peach", "jigglypuff", "yoshis-story"),
    ("captain-falcon", "ganondorf", "dream-land"),
    ("marth", "fox", "fountain-of-dreams"),
    ("fox", "falco", "final-destination"),
    ("sheik", "marth", "battlefield"),
    ("captain-falcon", "peach", "dream-land"),
    ("jigglypuff", "fox", "pokemon-stadium"),
    ("ganondorf", "roy", "yoshis-story"),
    ("samus", "pikachu", "final-destination"),
    ("dr-mario", "luigi", "battlefield"),
    ("ice-climbers", "young-link", "dream-land"),
    ("zelda", "mewtwo", "fountain-of-dreams"),
    ("donkey-kong", "bowser", "final-destination"),
    ("link", "ness", "battlefield"),
    ("kirby", "yoshi", "dream-land"),
    ("mr-game-and-watch", "pichu", "final-destination"),
    ("mario", "marth", "pokemon-stadium"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--frames", type=int, default=600)
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--tolerance", type=float, default=1e-4)
    ap.add_argument("--only", default="",
                    help="only matchups naming this character or stage")
    args = ap.parse_args()
    clean = 0
    todo = [m for m in MATCHUPS if not args.only or args.only in m]
    for p1, p2, stage in todo:
        r = subprocess.run(
            [sys.executable, str(HERE / "compare.py"), "--p1", p1, "--p2", p2,
             "--stage", stage, "--tolerance", str(args.tolerance),
             "--random", str(args.runs), "--frames", str(args.frames)],
            capture_output=True, text=True, timeout=900)
        lines = [l.strip() for l in (r.stdout + r.stderr).splitlines()
                 if l.startswith("random") or "FATAL" in l
                 or l.startswith("    ") and "/" in l]
        ok = r.returncode == 0
        clean += ok
        print("%-4s %s / %s / %s%s" % (
            "ok" if ok else "DIFF", p1, p2, stage,
            "" if ok else ": " + " | ".join(lines[:3])[:150]))
        sys.stdout.flush()
    print("%d of %d matchups identical for %d frames" % (
        clean, len(todo), args.frames))
    sys.exit(0 if clean == len(todo) else 1)


if __name__ == "__main__":
    main()
