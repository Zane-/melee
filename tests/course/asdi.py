"""ASDI down and crouch cancel, each actor of both drills, on the native
build (headless).

    python tests/course/asdi.py [-v]

For every move of the deck (tools/melee_course/drills/defense_asdi.py): the
drill's own demonstration (the hold, then a shine as soon as the player is
back on the floor) succeeds just under the percent the drill says the hold
works to ("Near its limit"), and fails a few percent past it: the actor
reaches the player from where it starts, and its limits are where the game
says they are.
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from native import Native  # noqa: E402
from melee_course import engine, registry  # noqa: E402
from melee_course.drills import defense_asdi as da  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def attempt(game, ident, k, at):
    """The demonstration of scenario `k` with the player at `at` percent
    (the drill's pick replaced)."""
    d = registry.get(ident)
    d.limit = lambda actor: at
    setup = d.setup

    def at_limit(c):
        c.randi = lambda n: n - 1           # "Near its limit": the limit
        setup(c)
    d.setup = at_limit
    s = engine.Session(d, game, live=False, seed=7,
                       options={da.OPT_PERCENT: da.PERCENT_EDGE},
                       common={engine.OPT_SCENARIO: k + 1})
    return s.run(demo=True)


def main():
    verbose = "-v" in sys.argv
    with Native() as game:
        for ident in ("universal-asdi-down", "universal-crouch-cancel"):
            d = registry.get(ident)
            for k, entry in enumerate(d.deck):
                top = d.limit(entry.data)
                r = attempt(game, ident, k, top)
                check("%s, %s: held at %d%% and punished"
                      % (ident, entry.name, top), r.get("success"),
                      r.get("words", ""))
                if verbose:
                    print("   ", r)
                if top >= 150:
                    continue                # holds at every percent tried
                r = attempt(game, ident, k, top + 8)
                check("%s, %s: at %d%% it no longer holds"
                      % (ident, entry.name, top + 8), not r.get("success"),
                      r.get("words", ""))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
