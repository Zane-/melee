"""The proof of a drill in the drill format (docs/ai/drill-format.md):

    python tools/melee_drills/check.py universal-short-hop [--chars fox,marth]
    python tools/melee_drills/check.py path/to/a-drill.json

For every character the drill allows (or those named), headless:
- the tutorial's example and each part's example pass that part's checks;
- each mistake fails, on the check it names;
- a part whose scenarios are a deck of opponents (each scenario another
  opponent: fox-shine-oos's deck) plays its example, its frame-perfect
  example and the mistakes judged as it in every scenario of the deck;
- the words a player would read for each, printed once (for a person to
  read: the format cannot check that they are clear).

A drill is done when this passes and the owner has played it.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "melee_native"))

from native import Native  # noqa: E402
from melee_course import engine  # noqa: E402
from melee_drills import format as F  # noqa: E402
from melee_drills.drill import JsonDrill, inputs_to_refs  # noqa: E402

ALL = sorted(f[:-5] for f in os.listdir(os.path.join(F.ROOT, "data",
                                                     "framedata"))
             if f.endswith(".json"))


def play(session, drill, inputs, part, strict=False, scenario=None):
    """`inputs` played as the demonstration, judged as part `part` (with
    frame-perfect timing: `strict`; in scenario `scenario` of the part's
    list)."""
    drill.set_part(part)
    drill.strict = strict
    drill.scenario_at = scenario
    session.scenario = -1 if scenario is None else \
        drill._part_scenarios().index(scenario)
    drill.build_reference = lambda c, i=inputs: inputs_to_refs(
        i, drill.nums(c), drill.ref_start)
    try:
        return session.run(demo=True)
    finally:
        del drill.build_reference


def deck(spec, part):
    """Is a part's list of scenarios a deck of opponents (each another
    opponent, or the same one with its own "numbers": another of its
    moves), not one situation from two sides (the ledges: no opponent, no
    numbers of their own)?"""
    sc = part.get("scenario")
    return isinstance(sc, list) and len(sc) > 1 and len(
        {_situation(spec["scenarios"][k]) for k in sc}) == len(sc)


def _situation(sc):
    """A scenario's opponent and its own numbers."""
    op = sc.get("opponent", "none")
    return (op["character"] if isinstance(op, dict) else op,
            json.dumps(sc.get("numbers", {}), sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("drill", help="a drill's id, or a drill file's path "
                    "(.json)")
    ap.add_argument("--chars", help="characters, comma separated")
    ap.add_argument("--quiet", action="store_true",
                    help="only failures and the totals")
    args = ap.parse_args()
    spec = F.load(path=args.drill) if args.drill.endswith(".json") else \
        F.load(args.drill)
    chars = args.chars.split(",") if args.chars else (
        ALL if spec.get("characters", "all") == "all"
        else spec["characters"])
    t0 = time.time()
    problems, shown = [], set()
    total = 0

    def say(key, line):
        if not args.quiet and key not in shown:
            shown.add(key)
            print("      " + line)

    for ch in chars:
        drill = JsonDrill(spec)
        with Native() as game:
            s = engine.Session(drill, game, character=ch, live=False,
                               seed=1, dpad=False)
            nums = drill.nums(s.c)
            cases = [("tutorial example", F.pick(spec["tutorial"], "example",
                                                 ch),
                      len(spec["parts"]) - 1, None)]
            cases += [("part %d example" % (i + 1), F.pick(p, "example", ch),
                       i, None)
                      for i, p in enumerate(spec["parts"])]
            # (what, inputs, part, the check it fails on or None, strict,
            # the scenario of the part's list or None)
            cases = [(w, x, part, None, False, None)
                     for w, x, part, _ in cases]
            # a part with a list of scenarios (the ledgedash's two
            # ledges): its example in each of the others too
            cases += [("part %d example, %s" % (i + 1, spec["scenarios"][k][
                "name"]), F.pick(p, "example", ch), i, None, False, k)
                for i, p in enumerate(spec["parts"])
                if isinstance(p.get("scenario"), list) and not deck(spec, p)
                for k in p["scenario"][1:]]
            # the examples are frame-perfect: they pass strict timing too
            strict_too = any("strict" in ck
                             for ck in spec["checks"].values())
            if strict_too:
                cases += [("part %d example, frame-perfect" % (i + 1),
                           F.pick(p, "example", ch), i, None, True, None)
                          for i, p in enumerate(spec["parts"])
                          if not deck(spec, p)]
            # a mistake is judged as the first part that counts its check
            judged = [(m, next(i for i, p in enumerate(spec["parts"])
                               if m["fails"] in p.get("checks", [])))
                      for m in spec.get("mistakes", [])]
            cases += [("mistake: " + m["name"], F.pick(m, "inputs", ch), i,
                       m["fails"], False, None)
                      for m, i in judged if not deck(spec, spec["parts"][i])]
            # a deck of opponents: all of it in every one of them
            for i, p in enumerate(spec["parts"]):
                if not deck(spec, p):
                    continue
                for k in p["scenario"]:
                    name = spec["scenarios"][k]["name"]
                    cases.append(("part %d example, %s" % (i + 1, name),
                                  F.pick(p, "example", ch), i, None, False,
                                  k))
                    if strict_too:
                        cases.append(("part %d example, frame-perfect, %s"
                                      % (i + 1, name), F.pick(
                                          p, "example", ch), i, None, True,
                                      k))
                    cases += [("mistake: %s, %s" % (m["name"], name),
                               F.pick(m, "inputs", ch), i, m["fails"],
                               False, k)
                              for m, j in judged if j == i]
            for what, inputs, part, fails, strict, scen in cases:
                total += 1
                r = play(s, drill, inputs, part, strict, scen)
                checks = {c["expect"]: c for c in r.get("checks", [])}
                if fails is None:
                    ok = r["success"]
                else:
                    want = F.text(spec["checks"][fails].get("expect", fails),
                                  nums)
                    c = checks.get(want)
                    ok = not r["success"] and c is not None and \
                        not c["passed"] and r.get("headline") == F.text(
                            spec["checks"][fails].get("headline", fails),
                            nums)
                if not ok:
                    problems.append("%s, %s: %s (%s)" % (
                        ch, what, r["words"], "should fail on %r" % fails
                        if fails else "should pass"))
                say(what, "%-34s %s%s" % (
                    what, r["words"], " | fix: " + r["fix"]
                    if r.get("fix") else ""))
        if not args.quiet:
            print("  %-16s J=%d  %s" % (ch, nums["J"], "ok" if not any(
                p.startswith(ch + ",") for p in problems) else "FAIL"))
    for p in problems:
        print("FAIL  " + p)
    print("%s: %d of %d cases right, %d characters (%.0f s)" % (
        args.drill, total - len(problems), total, len(chars),
        time.time() - t0))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
