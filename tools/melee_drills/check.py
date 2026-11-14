"""The proof of a drill in the drill format (docs/ai/drill-format.md):

    python tools/melee_drills/check.py universal-short-hop [--chars fox,marth]

For every character the drill allows (or those named), headless:
- the tutorial's example and each part's example pass that part's checks;
- each mistake fails, on the check it names;
- the words a player would read for each, printed once (for a person to
  read: the format cannot check that they are clear).

A drill is done when this passes and the owner has played it.
"""
import argparse
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


def play(session, drill, inputs, part):
    """`inputs` played as the demonstration, judged as part `part`."""
    drill.set_part(part)
    drill.build_reference = lambda c, i=inputs: inputs_to_refs(
        i, drill.nums(c))
    try:
        return session.run(demo=True)
    finally:
        del drill.build_reference


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("drill")
    ap.add_argument("--chars", help="characters, comma separated")
    ap.add_argument("--quiet", action="store_true",
                    help="only failures and the totals")
    args = ap.parse_args()
    spec = F.load(args.drill)
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
            cases = [("tutorial example", spec["tutorial"]["example"],
                      len(spec["parts"]) - 1, None)]
            cases += [("part %d example" % (i + 1), p["example"], i, None)
                      for i, p in enumerate(spec["parts"])]
            # a mistake is judged as the first part that counts its check
            cases += [("mistake: " + m["name"], m["inputs"],
                       next(i for i, p in enumerate(spec["parts"])
                            if m["fails"] in p.get("checks", [])),
                       m["fails"])
                      for m in spec.get("mistakes", [])]
            for what, inputs, part, fails in cases:
                total += 1
                r = play(s, drill, inputs, part)
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
