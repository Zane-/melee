"""Saving and loading the game's whole state inside the process (the base of
rollback netcode), checked headless.

    python tests/native/state.py [--frames N] [--seed S]

A match of two fighters played by random inputs (both ports, so both
fighters move, attack, jump, shield and change animations, which converts
archive data all the time): the state is saved, the match played on, the
state loaded, and the same inputs played again. Checked: a load brings back
every byte (hash and first difference), the replay is the same game frame
by frame (both fighters' state, position, speed, damage) and ends in the
same whole state (hash), several saves can be kept and loaded out of order,
and a branch played from a load (other inputs) can be undone by loading
again.
"""
import argparse
import os
import random
import sys
import time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))

from native import Native  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


BUTTONS = ["A", "B", "X", "Z", "R", "L"]


def inputs(seed, frames):
    """Random pads for two ports, held a few frames each (as a person
    would), frame by frame."""
    rng = random.Random(seed)
    out = []
    held = [None, None]
    left = [0, 0]
    for _ in range(frames):
        frame = []
        for p in range(2):
            if left[p] == 0:
                held[p] = dict(
                    buttons=[b for b in BUTTONS if rng.random() < 0.15],
                    stick=(rng.choice([-1, -0.5, 0, 0.5, 1]),
                           rng.choice([-1, 0, 0, 1])),
                    cstick=(rng.choice([0, 0, 0, -1, 1]), 0))
                left[p] = rng.randint(1, 8)
            left[p] -= 1
            frame.append(held[p])
        out.append(frame)
    return out


def view(n):
    st = n.state()
    out = []
    for p in st["p"][:2]:
        out.append(None if p is None else (
            p["state"], round(p["x"], 6), round(p["y"], 6),
            round(p["vx"], 6), round(p["vy"], 6), round(p["percent"], 4)))
    return tuple(out)


def play(n, script):
    seen = []
    for frame in script:
        for p in range(2):
            n.pad(p, **frame[p])
        n.step()
        seen.append(view(n))
    return seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--frames", type=int, default=600)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    script = inputs(args.seed, args.frames)
    other = inputs(args.seed + 100, args.frames // 2)
    with Native() as n:
        # both ports human: the script plays both
        n.start("fox", "marth", "final-destination", args.seed)
        n.step(30)
        h0 = n.state_hash()
        t = time.time()
        size = n.save(0)
        took = time.time() - t
        print("     snapshot %.1f MB (arena %.1f, statics %.1f, heap %.1f, "
              "heap in use %.1f MB), saved in %.1f ms with the command" % (
                  size / 1e6, h0[1] / 1e6, h0[2] / 1e6, h0[3] / 1e6,
                  h0[4] / 1e6, took * 1000))

        first = play(n, script)
        h1 = n.state_hash()
        n.save(1)                         # the end of the first run
        moved = len(set(first))
        check("the random inputs play a varied match",
              moved > args.frames // 2, "%d distinct frames of %d" % (
                  moved, args.frames))

        n.load(0)
        check("a load brings back every byte", n.state_diff(0) is None and
              n.state_hash()[0] == h0[0], str(n.state_diff(0)))
        again = play(n, script)
        same = sum(1 for a, b in zip(first, again) if a == b)
        bad = next((i for i, (a, b) in enumerate(zip(first, again))
                    if a != b), None)
        check("the same inputs from it play the same game, frame by frame",
              same == len(first), "%d of %d frames the same%s" % (
                  same, len(first), "" if bad is None else
                  "; first difference at frame %d: %s / %s" % (
                      bad, first[bad], again[bad])))
        diff = n.state_diff(1)
        check("and end in the same whole state", diff is None and
              n.state_hash()[0] == h1[0], "first difference %s" % (diff,))

        # a branch: other inputs from the start, then undone
        n.load(0)
        branch = play(n, other)
        check("other inputs from the same state play another game",
              branch != first[:len(branch)])
        n.load(1)
        check("and loading the later save undoes that branch",
              n.state_diff(1) is None)
        n.load(0)
        check("saves are kept: the first one loads again after the others",
              n.state_diff(0) is None)
        # load, play half, save, load the start, load the half again
        half = play(n, script[:len(script) // 2])
        n.save(2)
        n.load(0)
        n.load(2)
        rest = play(n, script[len(script) // 2:])
        check("a save made after a load continues the same game",
              half + rest == first and n.state_diff(1) is None,
              "first difference %s" % (n.state_diff(1),))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
