"""A scenario: a situation, what the opponent does in it, and what counts as
getting it right. The unit an AI-driven drill is made of.

    {
      "name": "Punish a whiffed forward smash",
      "p1": "fox", "p2": "marth", "stage": "final-destination", "seed": 1,
      "setup": [{"place": 0, "x": -30, "facing": 1},
                {"place": 1, "x": 12, "facing": -1}],
      "opponent": {"port": 1, "script": [{"do": "wait", "frames": 40},
                                         {"do": "attack", "move": "fsmash"}]},
      "player":   {"port": 0, "script": [...]},
      "frames": 600, "after": 20,
      "success": ["target_hit", "not_hit"]
    }

- `setup`: placements (Native.place), applied in order after the match is up.
- `opponent`, `player`: each a port and either a `script` (Melee Actor steps,
  actor.py) or a `policy` (a slippi-ai model's name, policy.py). A script
  may hold {"choose": [script, ...], "weights": [...]}: which branch is run
  depends on the run number, so an opponent can vary what it does. `player` is
  whoever is being trained: today a stand-in script, later a person, in
  which case it is left out and nothing here drives that pad.
- `success`: expectations judged from the player's side when the run ends
  ("target_hit", "target_not_hit", "hit", "not_hit", "in_range:<n>").
- `frames`: the longest a run may take; `after`: frames to let the last
  input play out before judging. A run ends when the player's script does;
  the opponent's script not finishing (it was grabbed, say) is not a
  failure.

Runs on the native build (docs/ai/native-ai.md). A situation is set up
once and kept as a snapshot; each run restores it, so runs are independent
and cost what their frames cost.
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(HERE, "..", "melee_native"), os.path.join(HERE, "..")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from melee_actor.actor import Actor  # noqa: E402


class Session:
    """A game with one scenario set up in it, ready to be run many times."""

    def __init__(self, scenario, game=None):
        from native import Native
        self.sc = scenario
        self.own = game is None
        self.n = game or Native()
        self.n.start(scenario.get("p1", "fox"), scenario.get("p2", "marth"),
                     scenario.get("stage", "final-destination"),
                     scenario.get("seed", 1))
        self.fresh = self.n.snapshot()

    def close(self):
        if self.own:
            self.n.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # ---- one run ----------------------------------------------------------------

    def _setup(self, jitter, rng):
        n = self.n
        n.restore(self.fresh)
        n.pad(0)
        n.pad(1)
        for item in self.sc.get("setup", []):
            dx = rng.uniform(-jitter, jitter) if jitter else 0.0
            n.place(item["place"], item.get("x", 0.0) + dx,
                    item.get("y", 0.0), item.get("facing", 1),
                    bool(item.get("air", False)), item.get("percent", 0.0))
        n.seed(self.sc.get("seed", 1) + rng.randrange(1 << 16)
               if jitter else self.sc.get("seed", 1))
        n.step()

    def _side(self, spec, run=0):
        """(actor, per-frame function returning True while it has more to
        do, function giving its result) for one side."""
        other = 1 - spec["port"]
        actor = Actor(self.n, spec["port"], other,
                      stage=self.sc.get("stage", "final-destination"),
                      rng=random.Random(run * 7919 + spec["port"]))
        if "policy" in spec:
            from melee_actor import policy as pol
            player = pol.PolicyPlayer(
                self.n, spec["port"], other,
                os.path.join(pol.SLIPPI_AI, "deployed_models", spec["policy"]),
                stage=self.sc.get("stage", "final-destination"))

            def act():
                player.act()
                return True
            return actor, act, lambda: dict(policy=spec["policy"])
        gen = actor.steps(spec.get("script", []))
        box = {}

        def act():
            if "result" in box:
                return False
            try:
                self.n.pad(spec["port"], **next(gen))
                return True
            except StopIteration as done:
                box["result"] = done.value
                self.n.pad(spec["port"])
                return False
        def result():
            if "result" in box:
                return box["result"]
            if actor.log:
                actor.log[-1]["cut_short"] = True
            return dict(success=False, unfinished=True, frames=actor.frame,
                        steps=actor.log)
        return actor, act, result

    def run(self, jitter=0.0, run=0):
        """Play the scenario once. `jitter` moves every placement sideways
        by up to that much and changes the seed, by run number: the same
        run number is the same game."""
        sc, n = self.sc, self.n
        self._setup(jitter, random.Random(run))
        sides = {}
        for role in ("opponent", "player"):
            if role in sc:
                sides[role] = self._side(sc[role], run)
        judge_port = sc.get("player", {}).get("port", 0)
        judge = Actor(n, judge_port, 1 - judge_port)
        since = dict(percent=judge.them().percent, own=judge.me().percent)
        start = n.frame
        # A run is over when the player's script is (the opponent's may
        # well be cut short by it), or, with no player script, when the
        # opponent's is.
        scripted = [r for r in sides if "policy" not in sc[r]]
        decides = ["player"] if "player" in scripted else scripted
        for _ in range(int(sc.get("frames", 600))):
            busy = {role: act() for role, (_a, act, _r) in sides.items()}
            if decides and not any(busy[r] for r in decides):
                break
            n.step()
        n.pad(0)
        n.pad(1)
        if sc.get("after", 0):
            n.step(int(sc["after"]))
        checks = []
        for what in sc.get("success", []):
            passed, detail = judge._expect(what, since)
            checks.append(dict(expect=what, passed=bool(passed),
                               detail=detail))
        results = {role: result() for role, (_a, _act, result) in
                   sides.items()}
        ok = all(c["passed"] for c in checks) and all(
            results[r].get("success", True) for r in decides)
        out = dict(name=sc.get("name", ""), success=ok,
                   frames=n.frame - start, checks=checks)
        out.update(results)
        return out


def load(path):
    with open(path) as f:
        return json.load(f)


def run_file(path, runs=1, jitter=0.0):
    """Run a scenario file `runs` times. Returns the list of results."""
    with Session(load(path)) as session:
        return [session.run(jitter=jitter, run=i) for i in range(runs)]
