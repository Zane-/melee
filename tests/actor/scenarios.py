"""Scenarios on the native build: a situation, both sides scripted, a
verdict (tools/melee_actor/scenario.py). One situation, three ways of
playing it, which is what a drill has to tell apart.

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


def step(result, role, do):
    return next(s for s in result[role]["steps"] if s["step"].get("do") == do)


def main():
    def load(name):
        return scenario.load(os.path.join(HERE, name + ".json"))

    # Left alone, when can Marth shield again? The slow punish shows it.
    with scenario.Session(load("too_slow")) as s:
        slow = s.run()
    shield_at = step(slow, "opponent", "hold")["at"]
    check("stopping next to him and up smashing meets his shield",
          slow["success"] and step(slow, "player", "attack")["damage"] == 0,
          "%s; his shield is up from frame %d, the up smash starts at %d"
          % (slow["checks"][0]["detail"], shield_at,
             step(slow, "player", "attack")["at"]))

    with scenario.Session(load("whiff_punish")) as s:
        a = s.run()
        check("the punish: waits for the swing, runs in, grabs, throws",
              a["success"], "; ".join(c["detail"] for c in a["checks"]))
        waited = step(a, "player", "wait").get("waited", 0)
        check("the wait ended because the swing did, not on a frame count",
              40 < waited < 70, "after %d frames" % waited)
        grab = step(a, "player", "rush")
        throw_at = step(a, "player", "throw")["at"]
        check("the grab has Marth before his shield could be up",
              grab["grabbed"] and throw_at < shield_at,
              "holding him at frame %d; he could have shielded from %d"
              % (throw_at, shield_at))
        b = s.run()
        check("the same run again is the same", a == b)
        t = time.time()
        many = [s.run(jitter=2.0, run=i) for i in range(40)]
        took = time.time() - t
        good = sum(r["success"] for r in many)
        check("moved about by up to 2 units either way, it still works",
              good == 40, "%d of 40" % good)
        frames = sum(r["frames"] for r in many)
        check("forty runs take a second or two", took < 6.0,
              "%d frames in %.2f s" % (frames, took))
        wide = [s.run(jitter=8.0, run=i) for i in range(40)]
        print("      (moved by up to 8: %d of 40. From about 35 units the tip "
              "of the sword reaches: no longer a whiff)"
              % sum(r["success"] for r in wide))

    with scenario.Session(load("too_early")) as s:
        r = s.run()
        check("going at the start of the swing gets the player hit",
              r["success"] and r["checks"][0]["expect"] == "hit",
              r["checks"][0]["detail"])

    # A second situation, written from the instruction "shield Marth's
    # dash attack and grab him out of shield" (data/scenarios/).
    drill = scenario.load(os.path.join(HERE, "..", "..", "..", "data",
                                       "scenarios",
                                       "shield-grab-dash-attack.json"))
    with scenario.Session(drill) as s:
        r = s.run()
        block = step(r, "player", "shield")
        grab = step(r, "player", "oos")
        check("shield grab: blocks the dash attack, grabs out of shield",
              r["success"] and block.get("blocked") and grab["grabbed"],
              "blocked after %d frames of shield; %s"
              % (block.get("held", -1),
                 "; ".join(c["detail"] for c in r["checks"])))
        many = [s.run(jitter=3.0, run=i) for i in range(40)]
        good = sum(x["success"] for x in many)
        check("moved about by up to 3 units, it still works", good == 40,
              "%d of 40" % good)
    bare = dict(drill, player=dict(port=0, script=[
        {"do": "wait", "frames": 120}]), success=["hit"])
    with scenario.Session(bare) as s:
        r = s.run()
        check("without the shield the dash attack hits", r["success"],
              r["checks"][0]["detail"])

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
