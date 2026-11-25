"""The damage a drill's example holds at.

A scenario gives the player a damage; a hit's knockback grows with it, so
what a drill teaches against that hit (ASDI down, a DI angle, an SDI out
of a multi-hit attack) holds only up to some damage. For each scenario and
character this finds the range around the scenario's own damage in which
a part's example still passes that part's checks in a demonstration: the
scenario is played with the damage fixed, searched down to --lo and up to
--hi (a binary search each way: the range is taken to be one stretch).
--step N tries every N-th damage from the scenario's own outward instead
and ends the range before the first that fails: for a hit whose outcome
does not grow evenly with the damage (which hits of a multi-hit attack
connect changes from one damage to the next: against Falco, Jigglypuff's
down air held at the edge the binary search found and failed below it).

    python tools/melee_drills/percent_range.py DRILL|FILE [--part N]
        [--lo 0] [--hi 200] [--step N] [--chars a,b] [--scenarios i,j]
        [--jobs N] [--out FILE]

Prints, per scenario, the range that holds for every character and the
characters that set its ends; --out writes {scenario: {character: [lo,
hi]}} (null: the example fails at the scenario's own damage). A drill
draws a try's damage inside it: `"percent": [LO, HI]` in the scenario's
player, a number of the scenario or, per character, of its `numbers_for`
(docs/ai/drill-format.md). A demonstration plays the top of such a range,
so `check.py` proves the hardest end; this is where the ends come from.
"""
import argparse
import copy
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))


def characters():
    return sorted(f[:-5] for f in os.listdir(
        os.path.join(ROOT, "data", "framedata")) if f.endswith(".json"))


def measure(job):
    """One character's ranges: {scenario name: [lo, hi] or None}."""
    spec, part, ch, scen, lo_end, hi_end, step = job
    from native import Native
    from melee_course import engine
    from melee_drills import format as F
    from melee_drills.drill import JsonDrill, inputs_to_refs
    spec = copy.deepcopy(spec)
    drill = JsonDrill(spec)
    example = F.pick(spec["parts"][part], "example", ch)
    out = {}
    with Native() as game:
        s = engine.Session(drill, game, character=ch, live=False, seed=1,
                           dpad=False)

        def holds(k, pct):
            if pct is not None:
                spec["scenarios"][k]["player"]["percent"] = pct
            drill.set_part(part)
            drill.strict = False
            drill.scenario_at = k
            at = drill._part_scenarios().index(k)
            s.scenario = at
            drill.build_reference = lambda c: inputs_to_refs(
                example, drill.nums(c), drill.ref_start)
            try:
                r = s.run(demo=True, scenario=at)
            finally:
                del drill.build_reference
            return bool(r.get("success"))

        def edge(k, good, bad):
            """The last damage from `good` toward `bad` that holds (`bad`
            itself fails)."""
            while abs(bad - good) > 1:
                mid = (good + bad) // 2
                if holds(k, mid):
                    good = mid
                else:
                    bad = mid
            return good

        def walk(k, own, end):
            """The last damage from `own` toward `end`, every `step`-th
            tried, before the first that fails."""
            good = p = own
            while p != end:
                p = max(end, p - step) if end < own else min(end, p + step)
                if not holds(k, p):
                    break
                good = p
            return good

        for k in scen:
            name = spec["scenarios"][k]["name"]
            if not holds(k, None):      # (as the drill has it: its top)
                out[name] = None
                continue
            own = int(round(drill.percent))
            if step:
                out[name] = [walk(k, own, min(lo_end, own)),
                             walk(k, own, max(hi_end, own))]
                continue
            lo = lo_end if own <= lo_end or holds(k, lo_end) else \
                edge(k, own, lo_end)
            hi = hi_end if own >= hi_end or holds(k, hi_end) else \
                edge(k, own, hi_end)
            out[name] = [min(lo, own), max(hi, own)]
    return ch, out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("drill", help="a drill's id, or a drill file's path")
    ap.add_argument("--part", type=int, default=None,
                    help="the part (0 the first); by default the last")
    ap.add_argument("--lo", type=int, default=0)
    ap.add_argument("--hi", type=int, default=200)
    ap.add_argument("--step", type=int, default=0,
                    help="try every N-th damage outward instead of a "
                         "binary search (a multi-hit attack)")
    ap.add_argument("--chars", help="characters, comma separated (by "
                                    "default all the drill is for)")
    ap.add_argument("--scenarios", help="scenario indexes, comma separated")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--out", help="a JSON file for the ranges")
    args = ap.parse_args()
    from melee_drills import format as F
    spec = json.load(open(args.drill)) if args.drill.endswith(".json") \
        else copy.deepcopy(F.load(args.drill))
    part = len(spec["parts"]) - 1 if args.part is None else args.part
    P = spec["parts"][part]
    scen = P["scenario"] if isinstance(P.get("scenario"), list) else \
        [P.get("scenario", 0)]
    if args.scenarios:
        scen = [int(i) for i in args.scenarios.split(",")]
    own = spec.get("characters", "all")
    chars = args.chars.split(",") if args.chars else (
        characters() if own == "all" else list(own))
    jobs = [(spec, part, ch, scen, args.lo, args.hi, args.step)
            for ch in chars]
    table = {}
    with ProcessPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        for ch, got in pool.map(measure, jobs):
            for name, r in got.items():
                table.setdefault(name, {})[ch] = r
    print("%s, part %d (%s): the damage its example holds at" % (
        spec["id"], part + 1, P["name"]))
    for k in scen:
        name = spec["scenarios"][k]["name"]
        got = table[name]
        bad = sorted(ch for ch, r in got.items() if r is None)
        ok = {ch: r for ch, r in got.items() if r is not None}
        if not ok:
            print("%-40s fails as it is for every character" % name[:40])
            continue
        lo = max(r[0] for r in ok.values())
        hi = min(r[1] for r in ok.values())
        print("%-40s %3d to %3d%%  (%s; %s)%s" % (
            name[:40], lo, hi,
            "from: " + ", ".join(sorted(c for c, r in ok.items()
                                        if r[0] == lo)[:3]),
            "to: " + ", ".join(sorted(c for c, r in ok.items()
                                      if r[1] == hi)[:3]),
            "  FAILS as it is: " + ", ".join(bad) if bad else ""),
            flush=True)
    if args.out:
        json.dump(table, open(args.out, "w"), indent=1, sort_keys=True)
        print("wrote", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
