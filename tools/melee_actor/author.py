"""Turn an instruction in words into a scenario that has been run, with Claude.

    python tools/melee_actor/author.py "Marth dash attacks from mid range. \
        I want to practise shielding it and grabbing him out of shield."
    python tools/melee_actor/author.py --p1 falco --p2 sheik --name tilt-punish "..."
    python tools/melee_actor/author.py --show-prompt        # what Claude is told

Claude is given the scenario format, the Melee Actor's vocabulary and three
tools: run a scenario on the native build (many runs, each moved about),
look up the knowledge base's frame data, and save. It writes a scenario,
runs it, reads what happened and revises. A scenario is only saved if its
last run passed: `save_scenario` refuses otherwise.

Credentials: the Anthropic SDK's own (ANTHROPIC_API_KEY, or a profile from
`ant auth login`). The model never drives the game frame by frame; it
writes scripts and reads verdicts (docs/ai/native-ai.md, N5).
"""
import argparse
import hashlib
import inspect
import json
import os
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for _p in (os.path.join(HERE, "..", "melee_native"), os.path.join(HERE, "..")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from melee_actor import actor as act       # noqa: E402
from melee_actor import scenario as scn    # noqa: E402
from native import CHARACTERS, STAGES      # noqa: E402

MODEL = "claude-opus-5-5"
SAVE_DIR = os.path.join(ROOT, "data", "scenarios")
#: A scenario may be saved when at least this share of its last runs passed.
PASS_SHARE = 0.9
MIN_RUNS = 10


# --- what Claude is told -----------------------------------------------------

def vocabulary():
    """The actor's steps, conditions and expectations, from its own code, so
    the prompt cannot drift from what runs."""
    lines = []
    for name in sorted(n for n in dir(act.Actor) if n.startswith("do_")):
        fn = getattr(act.Actor, name)
        params = [p for p in inspect.signature(fn).parameters
                  if p not in ("self", "_")]
        doc = " ".join((fn.__doc__ or "").split())
        lines.append('- {"do": "%s"} with %s. %s' % (
            name[3:], ", ".join(params) or "no parameters", doc))
    lines.append("- moves for attack: " + ", ".join(sorted(act.MOVES)))
    lines.append("- moves for rush: " + ", ".join(sorted(act.RUSH)))
    lines.append("- throw directions: " + ", ".join(sorted(act.THROWS)))
    return "\n".join(lines)


def system_prompt():
    return """\
You are writing practice scenarios for Super Smash Bros. Melee. A scenario \
will become a drill that a person plays against a computer opponent, so it \
has to set up a real situation, make the opponent do something specific, \
and say what the player has to achieve.

You do not control the game frame by frame. You write a scenario as JSON, \
run it with the run_scenario tool, read what happened, and revise it. The \
game is the real one (the vanilla game, running headless at thousands of \
frames a second), so what a run reports is what would happen.

## A scenario

```json
{
  "name": "Punish a whiffed forward smash",
  "about": "One or two sentences for the player: the situation and the idea.",
  "p1": "fox", "p2": "marth", "stage": "final-destination", "seed": 1,
  "setup": [{"place": 0, "x": -30, "facing": 1},
            {"place": 1, "x": 12, "facing": -1, "percent": 30}],
  "opponent": {"port": 1, "script": [{"do": "wait", "frames": 40},
                                     {"do": "attack", "move": "fsmash"},
                                     {"do": "hold", "frames": 90, "buttons": ["R"]}]},
  "player": {"port": 0, "script": [{"do": "wait", "until": "target_swung"},
                                   {"do": "rush", "move": "grab"},
                                   {"do": "throw", "direction": "up"}]},
  "frames": 400, "after": 10,
  "success": ["target_hit", "not_hit"]
}
```

- p1 is port 0 and p2 is port 1. Characters: %(characters)s. Stages: %(stages)s.
- setup places fighters: x (the centre of the stage is 0; Final Destination's \
floor runs from about -85 to 85), y (the fighter stands on the floor at or \
below it; 0 by default), facing 1 (right) or -1, percent, and "air": true to \
start falling from that point.
- opponent is what the computer will do in the drill. player is a stand-in \
for the person: a script that plays the situation correctly, which shows \
that it can be done and how. Each script only sees its own fighter and its \
target (the other one).
- success is judged from the player's side after both scripts end and \
`after` more frames: "target_hit", "target_not_hit", "hit" (the player was \
hit), "not_hit", "in_range:N".
- frames is the longest a run may take.

## What a script can say

A script is a list of steps. A step says what is to be achieved; the actor \
works out each frame's buttons from where the fighters are.

%(vocabulary)s
- {"expect": ...} may also appear inside a script, with the same words as \
success.
- {"choose": [script, script, ...], "weights": [...]} runs one of the \
branches in its place, a different one from run to run. Use it to make an \
opponent vary what it does after its attack (shield, jab, roll away), so \
the player's answer has to work against all of them.

## What makes a scenario good

- It works when the fighters are not exactly where you put them. Run with \
runs of 20 or more and a jitter of 2 or so (every placement moves sideways \
by up to that much, and the random seed changes) and read the failures.
- It is fair. If the opponent could have defended, give it a step that \
does (for example a hold with R after its attack, so its shield comes up as \
soon as it can act). A punish that only lands because the opponent stands \
still teaches the wrong thing.
- It tells right from wrong. When it is cheap, also run a version in which \
the player does the natural wrong thing (too early, too slow, the wrong \
move) and check that it does not meet the success conditions.
- It names no frame numbers where a condition would do. "wait until \
target_swung" survives a change of character; "wait 54 frames" does not. \
If the vocabulary lacks the step or condition the situation needs, use the \
nearest thing, and say in your final report what was missing: that list is \
how the vocabulary grows.

Use game_data for numbers you would otherwise guess (when a move hits, how \
long it lasts, what can punish it on shield). Distances are in the game's \
units; a character is roughly 10 wide.

When a scenario passes at least %(share)d%% of a jittered run, save it with \
save_scenario. Then finish with a short report: what the situation is, what \
the stand-in does, how many runs passed at what jitter, what you tried that \
did not work, and anything the vocabulary could not express. Do not claim \
more than the runs showed.""" % dict(
        characters=", ".join(sorted(CHARACTERS)),
        stages=", ".join(sorted(STAGES)),
        vocabulary=vocabulary(), share=int(PASS_SHARE * 100))


# --- the tools ---------------------------------------------------------------

class Workbench:
    """The three tools, and what they remember between calls."""

    def __init__(self, save_dir=SAVE_DIR, log=print):
        self.save_dir = save_dir
        self.log = log
        self.passed = {}        # scenario text digest -> (good, runs, jitter)
        self.saved = []

    @staticmethod
    def _digest(sc):
        return hashlib.sha1(json.dumps(sc, sort_keys=True).encode()).hexdigest()

    @staticmethod
    def _parse(text):
        try:
            sc = json.loads(text)
        except ValueError as e:
            raise ValueError("the scenario is not valid JSON: %s" % e)
        if not isinstance(sc, dict):
            raise ValueError("the scenario must be a JSON object")
        for key, table in (("p1", CHARACTERS), ("p2", CHARACTERS),
                           ("stage", STAGES)):
            if key in sc and sc[key] not in table:
                raise ValueError("unknown %s %r; choose from: %s" % (
                    key, sc[key], ", ".join(sorted(table))))
        if "player" not in sc and "opponent" not in sc:
            raise ValueError("a scenario needs a player or an opponent")
        for role in ("player", "opponent"):
            if role in sc and sc[role].get("port") not in (0, 1):
                raise ValueError('%s needs "port": 0 or 1' % role)
        return sc

    def run_scenario(self, scenario: str, runs: int = 20,
                     jitter: float = 2.0) -> str:
        """Run a scenario on the game and report how it went.

        Args:
            scenario: The scenario, as a JSON object in a string.
            runs: How many times to run it (1 to 100).
            jitter: Each run moves every placement sideways by up to this many units and changes the random seed. 0 runs it exactly as written.
        """
        try:
            sc = self._parse(scenario)
            runs = max(1, min(100, int(runs)))
            jitter = max(0.0, float(jitter))
            with scn.Session(sc) as session:
                results = [session.run(jitter=jitter, run=i)
                           for i in range(runs)]
        except Exception as e:  # the model reads this and tries again
            return "Error: %s" % (str(e).splitlines() or [repr(e)])[0]
        good = [r for r in results if r["success"]]
        self.passed[self._digest(sc)] = (len(good), runs, jitter)
        self.log("   ran %r: %d of %d (jitter %g)" % (
            sc.get("name", ""), len(good), runs, jitter))

        def brief(r):
            out = dict(frames=r["frames"], checks=r["checks"])
            for role in ("opponent", "player"):
                if role in r:
                    out[role] = [
                        {k: v for k, v in s.items() if k != "step"} |
                        {"step": s["step"]} for s in r[role].get("steps", [])]
                    if r[role].get("unfinished"):
                        out[role + "_unfinished"] = True
            return out
        report = dict(passed=len(good), runs=runs, jitter=jitter)
        bad = next((r for r in results if not r["success"]), None)
        if bad is not None:
            report["a_run_that_failed"] = brief(bad)
        if good:
            report["a_run_that_passed"] = brief(good[0])
        return json.dumps(report)

    def game_data(self, query: str) -> str:
        """Look up the knowledge base's frame data and calculators.

        Args:
            query: Arguments for the query tool, for example "marth fsmash" (one move: startup, active frames, damage), "fox" (a character's attributes and move names), "oos fox" (out-of-shield options, fastest first), "shield marth fsmash fox" (advantage on shield and what punishes it), "kb fox usmash marth 80" (knockback at 80 percent), "jump fox".
        """
        try:
            args = shlex.split(query)[:8]
            out = subprocess.run(
                [sys.executable, os.path.join(ROOT, "tools", "melee_data",
                                              "query.py")] + args,
                capture_output=True, text=True, timeout=30, cwd=ROOT)
        except Exception as e:
            return "Error: %s" % e
        text = (out.stdout or out.stderr).strip()
        return text[:6000] or "Error: nothing found for %r" % query

    def save_scenario(self, name: str, scenario: str) -> str:
        """Save a scenario that passed its last run, under a short name.

        Args:
            name: A short file name: lower-case words joined by hyphens, for example "whiff-punish-grab".
            scenario: The scenario exactly as it was last run, as a JSON object in a string.
        """
        try:
            sc = self._parse(scenario)
        except ValueError as e:
            return "Error: %s" % e
        good, runs, jitter = self.passed.get(self._digest(sc), (0, 0, 0.0))
        if runs < MIN_RUNS or good < PASS_SHARE * runs:
            return ("Error: not saved. This exact scenario has to pass at "
                    "least %d%% of a run of %d or more first; its last run "
                    "was %d of %d." % (int(PASS_SHARE * 100), MIN_RUNS, good,
                                       runs))
        slug = "".join(c if c.isalnum() else "-" for c in name.lower())
        slug = "-".join(p for p in slug.split("-") if p)[:60] or "scenario"
        os.makedirs(self.save_dir, exist_ok=True)
        path = os.path.join(self.save_dir, slug + ".json")
        sc["checked"] = dict(passed=good, runs=runs, jitter=jitter)
        with open(path, "w") as f:
            json.dump(sc, f, indent=2)
            f.write("\n")
        self.saved.append(path)
        self.log("   saved %s" % os.path.relpath(path, ROOT))
        return "Saved as %s (%d of %d runs at jitter %g)." % (
            os.path.relpath(path, ROOT), good, runs, jitter)


# --- the conversation --------------------------------------------------------

def author(instruction, p1=None, p2=None, stage=None, model=MODEL,
           effort="high", max_iterations=40, save_dir=SAVE_DIR, log=print):
    """Have Claude write and test a scenario for `instruction`. Returns
    (final report text, [paths saved])."""
    import anthropic
    from anthropic import beta_tool

    bench = Workbench(save_dir, log)
    ask = instruction.strip()
    given = [("The player's character", p1), ("The opponent's character", p2),
             ("The stage", stage)]
    for label, value in given:
        if value:
            ask += "\n%s: %s." % (label, value)
    client = anthropic.Anthropic()
    runner = client.beta.messages.tool_runner(
        model=model,
        max_tokens=16000,
        system=system_prompt(),
        cache_control={"type": "ephemeral"},
        output_config={"effort": effort},
        tools=[beta_tool(bench.run_scenario), beta_tool(bench.game_data),
               beta_tool(bench.save_scenario)],
        messages=[{"role": "user", "content": ask}],
        max_iterations=max_iterations,
        # If a safety classifier declines the request, the API reruns it on
        # a fallback model instead of stopping.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    last = None
    for message in runner:
        last = message
        for block in message.content:
            if block.type == "text" and block.text.strip() and \
                    message.stop_reason == "tool_use":
                log("   " + block.text.strip().splitlines()[0][:150])
    if last is None:
        return "No reply.", bench.saved
    if last.stop_reason == "refusal":
        return "The request was declined (%s)." % getattr(
            last.stop_details, "category", None), bench.saved
    text = "\n".join(b.text for b in last.content if b.type == "text").strip()
    if last.stop_reason == "max_tokens":
        text += "\n(The reply was cut off at the token limit.)"
    elif last.stop_reason == "tool_use":
        text += "\n(Stopped after %d steps without finishing.)" % max_iterations
    return text, bench.saved


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("instruction", nargs="?")
    ap.add_argument("--p1", choices=sorted(CHARACTERS),
                    help="the player's character")
    ap.add_argument("--p2", choices=sorted(CHARACTERS),
                    help="the opponent's character")
    ap.add_argument("--stage", choices=sorted(STAGES))
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--effort", default="high",
                    choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--out", default=SAVE_DIR,
                    help="where scenarios are saved (default data/scenarios)")
    ap.add_argument("--show-prompt", action="store_true",
                    help="print what Claude is told, and stop")
    args = ap.parse_args()
    if args.show_prompt:
        print(system_prompt())
        return 0
    if not args.instruction:
        ap.error("an instruction is needed")

    import anthropic
    try:
        report, saved = author(args.instruction, args.p1, args.p2, args.stage,
                               args.model, args.effort, save_dir=args.out)
    except anthropic.AuthenticationError:
        print("No valid Anthropic credentials: set ANTHROPIC_API_KEY or run "
              "`ant auth login`.", file=sys.stderr)
        return 2
    except anthropic.RateLimitError as e:
        print("Rate limited; retry after %s s." %
              e.response.headers.get("retry-after", "a while"),
              file=sys.stderr)
        return 2
    except anthropic.APIStatusError as e:
        print("The API answered %d: %s" % (e.status_code, e.message),
              file=sys.stderr)
        return 2
    except anthropic.APIConnectionError:
        print("Could not reach the API.", file=sys.stderr)
        return 2
    except TypeError as e:
        # the SDK's own message when no credential source is found
        if "api_key" in str(e) or "auth" in str(e).lower():
            print("No Anthropic credentials: set ANTHROPIC_API_KEY or run "
                  "`ant auth login`.", file=sys.stderr)
            return 2
        raise
    print()
    print(report)
    return 0 if saved else 1


if __name__ == "__main__":
    sys.exit(main())
