"""Run scenario files on the native build and say how they went.

    python tools/melee_actor/run.py tests/actor/scenarios/whiff_punish.json
    python tools/melee_actor/run.py FILE... --runs 20 --jitter 4   # moved about
    python tools/melee_actor/run.py FILE --json                    # everything

One line per scenario: how many runs met its `success`, and how long the
runs took in frames. With --steps, what each side's script did. The exit
status is the number of scenarios that failed in every run.

Scenario format: tools/melee_actor/scenario.py. What it runs on:
docs/ai/native-ai.md.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                ".."))
from melee_actor import scenario  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--jitter", type=float, default=0.0,
                    help="move each placement sideways by up to this much, "
                         "and change the seed, differently in every run")
    ap.add_argument("--json", action="store_true",
                    help="print every run's full result as JSON")
    ap.add_argument("--steps", action="store_true",
                    help="print what each script's steps did (first run)")
    args = ap.parse_args()

    failed, everything = 0, []
    for path in args.files:
        started = time.time()
        results = scenario.run_file(path, args.runs, args.jitter)
        took = time.time() - started
        good = sum(r["success"] for r in results)
        frames = sum(r["frames"] for r in results)
        failed += good == 0
        everything.append(dict(file=path, runs=results))
        if args.json:
            continue
        print("%-4s %s: %d of %d runs, %d frames in %.2f s" % (
            "ok" if good == len(results) else "FAIL" if good == 0 else "some",
            results[0]["name"] or path, good, len(results), frames, took))
        bad = next((r for r in results if not r["success"]), None)
        for c in (bad or results[0])["checks"]:
            print("       %s %s: %s" % ("yes" if c["passed"] else "NO ",
                                        c["expect"], c["detail"]))
        if args.steps:
            for role in ("opponent", "player"):
                for st in results[0].get(role, {}).get("steps", []):
                    print("       %-8s %s" % (role, json.dumps(st)))
    if args.json:
        print(json.dumps(everything, indent=1))
    return failed


if __name__ == "__main__":
    sys.exit(main())
