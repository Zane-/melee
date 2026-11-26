"""A drill's example against the opponent a person plays.

`check.py` proves a part's example against the demonstration's opponent,
which does one thing (its `example` script). A person plays against the
scenario's `script`: it moves, chooses its moment, comes from another
distance. This plays the example against that one, several times a
scenario (each run with a seed of its own: its choices change from one
run to the next), and says how often the part's checks pass and which
failed when they did not: whether what the drill teaches still works when
the situation arises from play.

    python tools/melee_drills/check_play.py DRILL|FILE [--part N]
        [--runs R] [--chars a,b] [--scenarios i,j] [--follow] [--quiet]

Only for an example timed from events (`"from": "start"`, a hit, a
distance): one timed from the demonstration's own first frame has nothing
to go by against an opponent that takes its time. --follow: until the try
begins the example's left and right follow the side the opponent is on (it
is written for an opponent on one side; one that plays footsies can cross
to the other, and a person turns to it: without this the example walks on
the old way. Once the try has begun its directions are the technique's: a
thrown opponent flies over Fox, and following the DI is not turning). An
example is still no person: against an opponent that roams it cannot
chase, and against one that thinks it shows one answer of several; what
it fails there says where the example is rigid, not that the drill is
wrong. A drill is not held to
every run (a thinking opponent can win), but a scenario that never passes
is one the drill teaches wrongly: found so, 2026-11-25, the engine's free
approach landing a jab from its full reach, where Fox's shine does not
reach back (fox-combo-shine), and attacks begun facing away or after a
walk that overshot (universal-crouch-cancel).
"""
import argparse
import copy
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))

from native import Native  # noqa: E402
from melee_course import engine  # noqa: E402
from melee_drills import format as F  # noqa: E402
from melee_drills.drill import JsonDrill, inputs_to_refs  # noqa: E402


def follow(s):
    """An each_frame for Session.run: the example's left and right kept
    toward the opponent until the try begins (the runtime's `toward`, set
    once when the try is set up, turned when the opponent is on the other
    side of the player from where it was then)."""
    was = {}

    def each(game, frame):
        if s.cpu_port is None:
            return
        me, op = game.fighter(s.person), game.fighter(s.cpu_port)
        if not me.fp or not op.fp:
            return
        right = op.pos[0] >= me.pos[0]
        if frame <= was.get("frame", frame + 1) - 2 or "base" not in was:
            # (a new pass, a new try: as it is set up)
            was.update(base=s.c.toward, right=right)
        was["frame"] = frame
        if s.c.phase:
            # (the try has begun: its directions are the technique's. A
            # thrown opponent flies over Fox, and following the DI is not
            # turning to it)
            return
        s.c.toward = was["base"] if right == was["right"] else -was["base"]
    return each


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("drill", help="a drill's id, or a drill file's path")
    ap.add_argument("--part", type=int, default=None,
                    help="the part (0 the first); by default the last")
    ap.add_argument("--runs", type=int, default=3,
                    help="runs of each scenario")
    ap.add_argument("--chars", help="characters, comma separated (by "
                                    "default the drill's first)")
    ap.add_argument("--scenarios", help="scenario indexes, comma separated")
    ap.add_argument("--follow", action="store_true",
                    help="the example's left and right follow the side the "
                         "opponent is on")
    ap.add_argument("--quiet", action="store_true",
                    help="only the scenarios with a run that failed, and "
                         "the total")
    args = ap.parse_args()
    spec = json.load(open(args.drill)) if args.drill.endswith(".json") \
        else copy.deepcopy(F.load(args.drill))
    for sc in spec["scenarios"]:
        if isinstance(sc.get("opponent"), dict):
            # (a demonstration then plays against the script itself)
            sc["opponent"].pop("example", None)
    part = len(spec["parts"]) - 1 if args.part is None else args.part
    P = spec["parts"][part]
    scen = P["scenario"] if isinstance(P.get("scenario"), list) else \
        [P.get("scenario", 0)]
    if args.scenarios:
        scen = [int(i) for i in args.scenarios.split(",")]
    own = spec.get("characters", "all")
    chars = args.chars.split(",") if args.chars else \
        ["fox" if own == "all" or "fox" in own else own[0]]
    total = good = 0
    for ch in chars:
        drill = JsonDrill(spec)
        example = F.pick(P, "example", ch)
        with Native() as game:
            s = engine.Session(drill, game, character=ch, live=False,
                               seed=1, dpad=False)
            for k in scen:
                won, said = 0, {}
                for n in range(args.runs):
                    drill.set_part(part)
                    drill.strict = False
                    drill.scenario_at = k
                    at = drill._part_scenarios().index(k)
                    s.scenario = at
                    drill.build_reference = lambda c: inputs_to_refs(
                        example, drill.nums(c), drill.ref_start)
                    try:
                        # (its own seed: a demonstration otherwise
                        # replays the last try's, the same run again)
                        r = s.run(demo=True, scenario=at,
                                  run=1000 * k + n,
                                  each_frame=follow(s) if args.follow
                                  else None)
                    finally:
                        del drill.build_reference
                    if r.get("success"):
                        won += 1
                    else:
                        w = r.get("words", "?").split(":")[0][:40]
                        said[w] = said.get(w, 0) + 1
                total += args.runs
                good += won
                if not args.quiet or won < args.runs:
                    print("%-14s %-46s %d of %d%s" % (
                        ch, spec["scenarios"][k]["name"][:46], won,
                        args.runs,
                        "  | " + "; ".join("%s x%d" % kv
                                           for kv in said.items())
                        if said else ""), flush=True)
    print("%s, part %d (%s): %d of %d runs right against the opponent a "
          "person plays" % (spec["id"], part + 1, P["name"], good, total),
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
