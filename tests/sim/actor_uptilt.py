"""Melee Actor proof: one script, "up tilt the player", four situations.

The script names no frames and no positions. The actor (Marth, port 2) has to
find Fox wherever he is and whatever he does first.

    python tests/sim/actor_uptilt.py
"""
import json
import sys

sys.path.insert(0, "tools/melee_sim")
sys.path.insert(0, "tools")
from sim import Sim                       # noqa: E402
from melee_actor.actor import Actor       # noqa: E402

SCRIPT = [
    {"do": "approach", "range": 9, "tolerance": 4},
    {"do": "wait", "until": "target_grounded"},
    {"do": "face"},
    {"do": "attack", "move": "utilt"},
    {"expect": "target_hit"},
]


def stands(sim, frame):
    sim.pad(0)


def walks_away(sim, frame):
    sim.pad(0, stick=(-0.4, 0) if frame < 50 else (0, 0))


def runs_past(sim, frame):
    # runs at the actor, past it, and stops on the other side
    sim.pad(0, stick=(1.0, 0) if frame < 58 else (0, 0))


def jumps_about(sim, frame):
    # full hops on the spot for a while: the actor has to wait for a landing
    sim.pad(0, buttons=["X"] if frame % 50 < 6 and frame < 160 else [])


def main():
    s = Sim.match("lab", "fox", "marth", free=True)
    s.step(30)
    base = s.snapshot()
    failures = 0
    for name, other in (("target stands still", stands),
                        ("target walks away first", walks_away),
                        ("target runs past the actor", runs_past),
                        ("target keeps jumping", jumps_about)):
        s.restore(base)
        fox0, marth0 = s.fighter(0).pos[0], s.fighter(1).pos[0]
        result = Actor(s, port=1, target=0, other=other).run(SCRIPT)
        fox, marth = s.fighter(0), s.fighter(1)
        print("%-28s %s in %3d frames; Fox x %.0f -> %.0f, Marth x %.0f -> %.0f"
              % (name, "ok  " if result["success"] else "FAIL",
                 result["frames"], fox0, fox.pos[0], marth0, marth.pos[0]))
        for st in result["steps"]:
            print("    ", json.dumps({k: v for k, v in st.items()}))
        failures += not result["success"]
    print("%d of 4 passed" % (4 - failures))
    return failures


if __name__ == "__main__":
    sys.exit(main())
