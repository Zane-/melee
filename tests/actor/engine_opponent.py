"""The engine as the opponent (tools/melee_engine/opponent.py, the actor's
`engine` step): after the player stands, shields, dashes, walks or dash
dances during its wait, it still lands an approach, and not the same one
every time.

    python tools/native_build.py
    python tests/actor/engine_opponent.py
"""
import random
import sys
import time

sys.path.insert(0, "tools/melee_native")
sys.path.insert(0, "tools")
sys.path.insert(0, "tests/actor")
from native import Native  # noqa: E402
from melee_actor.actor import Actor  # noqa: E402
from react import WAIT, match, standin  # noqa: E402

KINDS = ["stand", "shield", "dash_in", "dash_out", "walk_in", "walk_out",
         "run_in_late", "dash_dance"]
CASES = [("captain-falcon", 30.0), ("falco", 20.0), ("marth", 26.0)]
APPROACH = "sh_,fh_,dash_,walk_,wait,wavedash_,hop_"
SEEDS = 3
checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


def main():
    t0 = time.time()
    landed = total = 0
    varied = cases = 0
    misses = []
    decision_ms = []
    for character, gap in CASES:
        with Native() as n:
            snap = match(n, character, gap)
            for kind in KINDS:
                firsts = set()
                for seed in range(SEEDS):
                    n.restore(snap)
                    a = Actor(n, port=1, target=0, other=standin(kind),
                              rng=random.Random(seed))
                    r = a.run([dict(do="wait", frames=WAIT),
                               dict(do="engine", goal=dict(contact=40),
                                    moves=APPROACH, frames=240,
                                    budget=1500, depth=2)])
                    st = r["steps"][1]
                    total += 1
                    if st.get("contact") in ("hit", "shield"):
                        landed += 1
                    else:
                        misses.append("%s/%s/%d" % (character, kind, seed))
                    firsts.add(st.get("moves", ["?"])[0])
                    if st.get("decisions"):
                        decision_ms.append(st["search_ms"] /
                                           st["decisions"])
                cases += 1
                varied += len(firsts) > 1
    check("it lands an approach after anything the player does first",
          landed == total, "%d of %d%s" % (landed, total,
                                          "; missed " + ", ".join(misses)
                                          if misses else ""))
    check("it varies: different openings from run to run",
          varied >= cases // 2, "%d of %d situations saw more than one "
          "opening over %d runs" % (varied, cases, SEEDS))
    check("a decision takes well under a second headless",
          sum(decision_ms) / len(decision_ms) < 1000,
          "%.0f ms on average (unoptimised)" % (sum(decision_ms) /
                                                len(decision_ms)))
    print("%d of %d checks passed (%.0f s)" % (sum(checks), len(checks),
                                                time.time() - t0))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
