"""Melee Actor proof: one script, "up tilt the player", four situations.

The script names no frames and no positions. The actor (Marth, port 2) has to
find Fox wherever he is and whatever he does first.

    python tests/actor/uptilt.py            # on the native build (default)
    python tests/actor/uptilt.py --sim      # on the Python simulator

The two start the match differently (the native build has the vanilla game
only: a VS match with the fighters 120 apart; the simulator runs the
overlay's Lab), so the frame counts differ. The script is the same.
"""
import json
import sys
import time

sys.path.insert(0, "tools")
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


CASES = (("target stands still", stands),
         ("target walks away first", walks_away),
         ("target runs past the actor", runs_past),
         ("target keeps jumping", jumps_about))


def open_game(backend):
    if backend == "sim":
        sys.path.insert(0, "tools/melee_sim")
        from sim import Sim
        s = Sim.match("lab", "fox", "marth", free=True)
        s.step(30)
        return s
    sys.path.insert(0, "tools/melee_native")
    from native import Native
    return Native().start("fox", "marth")


def main(backend="native"):
    s = open_game(backend)
    base = s.snapshot()
    failures, frames, started = 0, 0, time.time()
    for name, other in CASES:
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
        frames += result["frames"]
    took = time.time() - started
    print("%d of %d passed on %s: %d frames in %.2f s" % (
        len(CASES) - failures, len(CASES), backend, frames, took))
    if hasattr(s, "close"):
        s.close()
    return failures


if __name__ == "__main__":
    sys.exit(main("sim" if "--sim" in sys.argv[1:] else "native"))
