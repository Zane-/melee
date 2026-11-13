"""The Melee Actor against a target that fights back.

    ~/Games/Melee/slippi-ai/venv/bin/python tests/sim/actor_vs_policy.py

Marth is the actor with the "up tilt the target" script of
actor_uptilt.py. Fox is played by a trained slippi-ai policy. The script is
run several times from different moments of the same match.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..",
                                "tools"))
from melee_actor import policy as pol                       # noqa: E402
from melee_actor.actor import Actor                         # noqa: E402
from sim import Sim                                         # noqa: E402

SCRIPT = [
    {"do": "approach", "range": 9, "tolerance": 4, "timeout": 900},
    {"do": "wait", "until": "target_grounded", "timeout": 300},
    {"do": "face"},
    {"do": "attack", "move": "utilt"},
    {"expect": "target_hit"},
]


def main():
    s = Sim.match("lab", "fox", "marth", free=True)
    s.step(30)
    fox = pol.PolicyPlayer(s, 0, 1, os.path.join(
        pol.SLIPPI_AI, "deployed_models", "fox_d18_vs_marth_v3.1"))
    passed = 0
    runs = 5
    for i in range(runs):
        actor = Actor(s, port=1, target=0, other=lambda sim, f: fox.act())
        m0 = s.fighter(1).percent
        result = actor.run(SCRIPT)
        last = result["steps"][-1]
        attack = [st for st in result["steps"]
                  if st["step"].get("do") == "attack"]
        print("run %d: %s after %3d frames; %s; Marth took %.0f%% meanwhile"
              % (i + 1, "ok  " if result["success"] else "FAIL",
                 result["frames"],
                 last.get("detail") or last.get("failed") or
                 ("attack states %s" % attack[0]["states"] if attack else ""),
                 s.fighter(1).percent - m0))
        passed += result["success"]
        # let the match go on a little before the next try
        for _ in range(60):
            fox.act()
            s.pad(1)
            s.step()
    print("%d of %d passed" % (passed, runs))


if __name__ == "__main__":
    main()
