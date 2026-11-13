"""A person training against a scenario on the native window build,
checked without a person: the game runs on a virtual display and the
"person" is key presses on that display, decided from what the fighter is
doing.

    python tests/actor/train.py

Three people try data/scenarios/shield-grab-dash-attack.json: one who
stands still, one who shields and then does nothing, and one who shields,
grabs when the hit has landed on the shield and hits. Only the last gets a
yes. Then the same through tools/melee_actor/train.py's own loop.
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import window  # noqa: E402
from melee_actor import scenario as scn  # noqa: E402
from melee_actor import train  # noqa: E402

GUARD, GUARD_STUN = 179, 181
CATCH_WAIT, CATCH_ATTACK = 216, 217
KEYS = ("a", "d", "x")           # shield (L), grab (Z), A

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


class Person:
    """Presses keys by what it sees. `plan`: "still", "shield" or "punish"."""

    def __init__(self, game, plan):
        self.game, self.plan = game, plan
        self.held = set()
        self.blocked = False
        self.seen = set()

    def hold(self, *keys):
        for k in KEYS:
            if (k in keys) != (k in self.held):
                self.game.key(k, k in keys)
        self.held = set(keys)

    def __call__(self, game, frame):
        me = game.fighter(0)
        if frame == 0:
            self.blocked = False                # a new attempt
        self.seen.add(me.state)
        if self.plan == "still":
            return
        if me.state == GUARD_STUN:
            self.blocked = True
        if self.plan == "shield" or not self.blocked:
            self.hold("a")
        elif me.state == GUARD_STUN:
            self.hold("a")
        elif me.state == GUARD:
            self.hold("a", "d")                 # grab out of shield
        elif me.state == CATCH_WAIT:
            self.hold("x") if frame % 2 else self.hold()   # hit them
        else:
            self.hold()

    def done(self):
        self.hold()


def main():
    sc = scn.load(os.path.join(ROOT, "data", "scenarios",
                               "shield-grab-dash-attack.json"))
    try:
        with window.Window() as w:
            session = scn.Session(sc, game=w, person=0)
            w.live(0, "keyboard")
            want = {"still": (False, ["target_hit", "not_hit"]),
                    "shield": (False, ["target_hit"]),
                    "punish": (True, [])}
            for i, plan in enumerate(("still", "shield", "punish", "still")):
                person = Person(w, plan)
                r = session.run(run=i, each_frame=person)
                person.done()
                w.step(30)
                failed = [c["expect"] for c in r["checks"] if not c["passed"]]
                ok, missing = want[plan]
                check("%s: %s" % (plan, train.verdict(r)),
                      r["success"] == ok and failed == missing,
                      "%d frames%s" % (r["frames"],
                                       ", grabbed" if CATCH_WAIT in
                                       person.seen else ""))
            check("a person's run leaves the player's script out",
                  "player" not in r and "opponent" in r)

            # the loop train.py runs, with its own words
            said = []
            person = Person(w, "punish")
            results = train.train(w, sc, port=0, reps=2, source="keyboard",
                                  pause=20, each_frame=person,
                                  say=said.append)
            person.done()
            w.pace(False)
            check("train.py's loop: two attempts, both yes, and a count",
                  [r["success"] for r in results] == [True, True] and
                  said[-1] == "2 of 2" and said[0] == sc["name"],
                  "; ".join(said[2:]))
    finally:
        left = window.leftovers()
        check("nothing left running", not left, str(left))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
