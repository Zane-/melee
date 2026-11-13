"""The native build as a place to run experiments: one exchange per frame,
and snapshots that bring the whole game back.

    python tools/native_build.py
    python tests/native/env.py
"""
import random
import subprocess
import sys
import time

sys.path.insert(0, "tools/melee_native")
from native import Native  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


def play(n, seed, frames):
    """Random pads for both players; every frame's state."""
    rng = random.Random(seed)
    out = []
    for _ in range(frames):
        for port in (0, 1):
            if rng.random() < 0.2:
                n.pad(port,
                      buttons=[b for b in "ABXZR" if rng.random() < 0.12],
                      stick=(rng.choice((-1, -0.5, 0, 0.5, 1)),
                             rng.choice((-1, 0, 0, 1))),
                      cstick=(rng.choice((-1, 0, 0, 0, 1)), 0),
                      r=1.0 if rng.random() < 0.1 else 0)
        n.step()
        s = n.state()
        out.append((s["rng"], s["p"], s["items"]))
    return out


def running():
    out = subprocess.run(["pgrep", "-c", "melee_headless"],
                         capture_output=True, text=True).stdout.strip()
    return int(out or 0)


def main():
    before = running()
    with Native() as n:
        n.start("fox", "marth")
        f0 = n.frame
        check("a match is up, both fighters standing",
              n.fighter(0).state == 14 and n.fighter(1).state == 14,
              "frame %d" % f0)

        t = time.time()
        a = n.snapshot()
        t_snap = time.time() - t
        first = play(n, 1, 600)
        check("ten seconds of random play happen", n.frame == f0 + 600 and
              first[-1][1] != first[0][1])

        t = time.time()
        n.restore(a)
        t_restore = time.time() - t
        check("a restore goes back to the frame of the snapshot",
              n.state()["frame"] == f0, "frame %d" % n.state()["frame"])
        again = play(n, 1, 600)
        same = next((i for i in range(600) if first[i] != again[i]), None)
        check("the same inputs from a snapshot give the same game",
              same is None, "" if same is None else "differs at frame %d" % same)

        n.restore(a)
        other = play(n, 2, 600)
        check("other inputs give another game", other != first)

        # a snapshot taken later, and going between the two
        n.restore(a)
        part = play(n, 1, 250)
        b = n.snapshot()
        rest = play(n, 1, 350)     # (not the same draws as frames 250..599)
        n.restore(b)
        rest2 = play(n, 1, 350)
        n.restore(a)
        third = play(n, 1, 600)
        n.restore(b)
        rest3 = play(n, 1, 350)
        check("two snapshots, restored in any order", part == first[:250] and
              rest == rest2 == rest3 and third == first)
        check("snapshots cost little", t_snap < 0.05 and t_restore < 0.05,
              "snapshot %.1f ms, restore %.1f ms" % (t_snap * 1e3,
                                                     t_restore * 1e3))
        n.drop(b)
        try:
            n.restore(b)
            dropped = False
        except Exception:
            dropped = True
        check("a dropped snapshot is gone", dropped)

        t = time.time()
        for _ in range(3000):
            n.step()
        fps = 3000 / (time.time() - t)
        check("thousands of frames a second, a state for each", fps > 2000,
              "%.0f frames a second" % fps)

    with Native() as n:
        n.start("fox", "marth")
        fresh = play(n, 1, 600)
    same = next((i for i in range(600) if first[i] != fresh[i]), None)
    check("a fresh process plays the same game as one with snapshots",
          same is None, "" if same is None else "differs at frame %d" % same)
    time.sleep(0.3)
    check("nothing is left running", running() == before,
          "%d processes" % running())

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
