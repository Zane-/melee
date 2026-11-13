"""Scenarios on the native build: a situation, both sides scripted, a
verdict (tools/melee_actor/scenario.py).

    python tools/native_build.py
    python tests/actor/scenarios.py
"""
import os
import sys
import time

sys.path.insert(0, "tools")
from melee_actor import scenario  # noqa: E402

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenarios")
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


def main():
    punish = scenario.load(os.path.join(HERE, "whiff_punish.json"))
    early = scenario.load(os.path.join(HERE, "too_early.json"))

    with scenario.Session(punish) as s:
        a = s.run()
        check("the punish: waits for the swing, runs in, hits, is not hit",
              a["success"], "; ".join(c["detail"] for c in a["checks"]))
        waited = a["player"]["steps"][0].get("waited", 0)
        check("the wait ended because the swing did, not on a frame count",
              40 < waited < 70, "after %d frames" % waited)
        b = s.run()
        check("the same run again is the same", a == b)
        t = time.time()
        many = [s.run(jitter=2.0, run=i) for i in range(40)]
        took = time.time() - t
        good = sum(r["success"] for r in many)
        check("moved about by up to 2 units either way, it still works",
              good == 40, "%d of 40" % good)
        frames = sum(r["frames"] for r in many)
        check("forty runs take about a second", took < 5.0,
              "%d frames in %.2f s" % (frames, took))
        wide = [s.run(jitter=8.0, run=i) for i in range(40)]
        print("      (moved by up to 8: %d of 40. From about 35 units the tip "
              "of the sword reaches: no longer a whiff)"
              % sum(r["success"] for r in wide))

    with scenario.Session(early) as s:
        r = s.run()
        check("going at the start of the swing gets the player hit",
              r["success"] and r["checks"][0]["expect"] == "hit",
              r["checks"][0]["detail"])

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
