"""Shadow games (tools/melee_engine/shadow.py): a headless copy of a live
window-build match, kept in step, and the engine opponent thinking in it
while the live game runs at 60 frames a second.

    python tools/native_build.py && python tools/native_build.py --window
    python tests/native/shadow.py
"""
import random
import sys
import time

sys.path.insert(0, "tools/melee_native")
sys.path.insert(0, "tools")
sys.path.insert(0, "tests/actor")
from window import Window  # noqa: E402
from melee_engine.shadow import LiveMind, Mirrored, Shadow  # noqa: E402
from react import standin  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


def drain(game, shadow):
    t = time.time()
    while shadow.applied < game.frames and time.time() - t < 10:
        time.sleep(0.01)
    time.sleep(0.2)


def main():
    t0 = time.time()
    rng = random.Random(3)
    with Window() as live, Shadow() as shadow:
        game = Mirrored(live, shadow)
        game.start("fox", "captain-falcon", seed=5)
        for f in range(1200):
            if f % 12 == 0:
                pads = [dict(buttons=rng.choice([[], ["A"], ["B"], ["X"],
                                                 ["Z"], ["R"]]),
                             stick=(rng.choice([-1, -0.5, 0, 0.5, 1]),
                                    rng.choice([-1, 0, 1])))
                        for _ in (0, 1)]
            for p in (0, 1):
                game.pad(p, **pads[p])
            game.step()
        drain(game, shadow)
        check("the shadow stays the live game: random inputs, 1,200 frames",
              shadow.desync is None and shadow.checks >= 9 and
              shadow.error is None,
              "%d hash checks, desync at %s" % (shadow.checks,
                                                shadow.desync))

        live._cmd("pace 1")
        results = []
        for kind in ("stand", "dash_dance", "walk_out", "dash_in"):
            game.place(0, -15, 0, 1)
            game.place(1, 15, 0, -1)
            for p in (0, 1):
                game.pad(p)
            game.step()
            mind = LiveMind(shadow, 1, 0, goal=dict(contact=40),
                            moves="sh_,fh_,dash_,walk_,wait,wavedash_,hop_",
                            budget=1200, rng=random.Random(1))
            other = standin(kind)
            pct, hits = live.fighter(0).percent, 0
            t = time.time()
            for f in range(300):
                other(game, f)
                b, lx, ly, cx, cy, lt, rt = mind.pad()
                live.h.pads[1].update(buttons=b, lx=lx, ly=ly, cx=cx, cy=cy,
                                      lt=lt, rt=rt, connected=True)
                live._dirty.add(1)
                game.step()
                if live.fighter(0).percent > pct:
                    hits += 1
                    pct = live.fighter(0).percent
            results.append((kind, hits, mind.late, len(mind.decisions),
                            300 / (time.time() - t)))
        check("live, the engine opponent lands hits against each stand-in",
              all(r[1] > 0 for r in results),
              ", ".join("%s %d" % (r[0], r[1]) for r in results))
        check("its decisions come back in time",
              sum(r[2] for r in results) <= 2,
              "%d late of %d" % (sum(r[2] for r in results),
                                 sum(r[3] for r in results)))
        check("the live game keeps its 60 frames a second",
              min(r[4] for r in results) > 57,
              ", ".join("%.0f" % r[4] for r in results))
        drain(game, shadow)
        check("and stays in step with its shadow throughout",
              shadow.desync is None and shadow.error is None,
              "%d hash checks" % shadow.checks)
    print("%d of %d checks passed (%.0f s)" % (sum(checks), len(checks),
                                                time.time() - t0))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
