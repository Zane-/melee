"""The tools Claude is given for writing scenarios
(tools/melee_actor/author.py), exercised without Claude: no API call is
made here. The conversation itself needs credentials and is not tested.

    python tests/actor/author_tools.py
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, "tools")
from melee_actor import author  # noqa: E402

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenarios")
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


def main():
    prompt = author.system_prompt()
    steps = [n[3:] for n in dir(author.act.Actor) if n.startswith("do_")]
    check("the prompt lists every step the actor has",
          all('"do": "%s"' % s in prompt for s in steps), ", ".join(steps))

    with tempfile.TemporaryDirectory() as tmp:
        bench = author.Workbench(save_dir=tmp, log=lambda *_: None)
        good = open(os.path.join(HERE, "whiff_punish.json")).read()

        r = bench.save_scenario("too-soon", good)
        check("a scenario that has not been run is not saved",
              r.startswith("Error") and not os.listdir(tmp), r[:60])

        report = json.loads(bench.run_scenario(good, runs=20, jitter=2.0))
        check("running reports how many passed, and a passing run's steps",
              report["passed"] == 20 and report["runs"] == 20 and
              report["a_run_that_passed"]["player"][1]["grabbed"] is True,
              "%d of %d" % (report["passed"], report["runs"]))

        r = bench.save_scenario("Whiff punish (grab)", good)
        saved = os.listdir(tmp)
        check("then it is saved, with what it passed",
              saved == ["whiff-punish-grab.json"] and json.load(open(
                  os.path.join(tmp, saved[0])))["checked"] ==
              dict(passed=20, runs=20, jitter=2.0), r)

        slow = json.loads(open(os.path.join(HERE, "too_slow.json")).read())
        slow["success"] = ["target_hit"]       # what a drill would ask for
        report = json.loads(bench.run_scenario(json.dumps(slow), 12, 2.0))
        failed = report.get("a_run_that_failed", {})
        check("a failing scenario comes back with the check that failed",
              report["passed"] == 0 and failed["checks"][0]["passed"] is False
              and "a_run_that_passed" not in report,
              failed.get("checks", [{}])[0].get("detail", ""))
        r = bench.save_scenario("slow", json.dumps(slow))
        check("and is refused", r.startswith("Error") and len(
            os.listdir(tmp)) == 1, r[:70])

        for label, text in (
                ("broken JSON", "{not json"),
                ("an unknown character", '{"p1": "goku", "player": {"port": 0}}'),
                ("an unknown step", json.dumps(dict(
                    json.loads(good), player=dict(port=0, script=[
                        {"do": "teleport"}]))))):
            r = bench.run_scenario(text, 10, 0.0)
            ok = r.startswith("Error") or json.loads(r)["passed"] == 0
            check("%s is an answer, not a crash" % label, ok, r[:70])

        r = bench.game_data("marth fsmash")
        check("frame data can be looked up", "fsmash" in r.lower() and
              not r.startswith("Error"), r.splitlines()[0][:70])

    try:
        from anthropic import beta_tool
    except ImportError:
        print("      (anthropic is not installed: tool definitions not built)")
    else:
        bench = author.Workbench(log=lambda *_: None)
        d = beta_tool(bench.run_scenario).to_dict()
        check("the SDK builds a tool definition from each function",
              d["name"] == "run_scenario" and sorted(
                  d["input_schema"]["properties"]) ==
              ["jitter", "runs", "scenario"])

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
