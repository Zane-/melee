"""Tech drills in the native client, checked without a person or a desktop:
keys are pressed on a virtual display by stand-ins that watch the fighter.

    python tests/client/tech.py [--shots DIR]

Fox's Tech part: Short hop played by someone who taps jump and then by
someone who holds it; Wavedash by someone who air dodges as Fox leaves the
ground and then by someone who only jumps. The verdicts, what they say, and
the numbers kept. (The judges themselves are tested to the frame, with
scripted inputs, in tests/actor/tech.py.)
"""
import argparse
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))

import client  # noqa: E402
import courses  # noqa: E402
import window  # noqa: E402

WAIT, SQUAT = 14, 24
KEYS = ("c", "s", "Down", "Right")
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


class Hopper:
    """Holds jump (C is Y) for `hold` frames once the fighter stands."""

    def __init__(self, hold):
        self.hold, self.i, self.still = hold, None, 0

    def __call__(self, game):
        f = game.fighter(0)
        if self.i is None:
            self.still = self.still + 1 if f.state == WAIT else 0
            if self.still < 12:
                return
            self.i = 0
            game.key("c")
        elif self.i == self.hold:
            game.key("c", False)
        self.i += 1


class Dasher:
    """Crouches, jumps, and presses R with the stick down and to the side
    on the frame before Fox leaves the ground (a key pressed now is read at
    the next frame)."""

    def __init__(self, squat=3):
        self.squat, self.i, self.still, self.seen = squat, None, 0, 0

    def __call__(self, game):
        f = game.fighter(0)
        if self.i is None:
            self.still = self.still + 1 if f.state == WAIT else 0
            if self.still < 12:
                return
            self.i = 0
            game.key("Down")
            return
        self.i += 1
        if self.i == 8:
            game.key("c")
        elif self.i == 9:
            game.key("c", False)
        if f.state == SQUAT:
            self.seen += 1
            if self.seen == self.squat - 1:
                game.key("Right")
                game.key("s")
        elif self.seen and self.i > 20:
            for k in ("s", "Right", "Down"):
                game.key(k, False)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    args = ap.parse_args()
    save = os.path.join(tempfile.mkdtemp(prefix="melee-client-"),
                        "client.json")
    w = None

    def frames(n):
        for _ in range(n):
            c.frame()

    def tap(key, after=6):
        w.key(key)
        frames(2)
        w.key(key, False)
        frames(after)

    def play(plans, shot_name):
        """Start the drill in focus and have these stand-ins try it, one
        attempt each. Returns what each attempt was told."""
        told = []
        state = dict(who=None, since=0)
        show = c.show_result

        def counted(result, results):
            told.append(result["words"])
            state["since"] = 0
            show(result, results)

        def person(game, frame):
            if state["who"] is None:
                game.key("x", False)    # the A that started the drill
            k = len(told)
            if k >= len(plans):
                for key in KEYS:
                    game.key(key, False)
                game.key("Return")      # hold START: leave
                return
            if state["who"] != k:
                for key in KEYS:
                    game.key(key, False)
                state["who"], state["stand_in"] = k, plans[k]()
            state["since"] += 1
            if k == 1 and state["since"] == 12 and args.shots:
                game.shot(os.path.join(args.shots, shot_name + ".png"))
            state["stand_in"](game)

        c.show_result = counted
        c.person = person
        c.results = None
        w.key("x")
        for _ in range(20):
            c.frame()
            if c.results is not None:
                break
        w.key("x", False)
        w.key("Return", False)
        c.person, c.show_result = None, show
        w.pace(False)
        frames(6)
        return told

    try:
        w = window.Window(window=(1280, 720))
        w.step(30)
        c = client.Client(w, source="keyboard", save=save)
        w.pace(False)
        frames(6)
        tap("x")
        tap("x")
        tap("x")
        first = c.drills()[c.row[c.part]]
        check("Tech opens on Short hop, and it plays here",
              c.screen == "list" and courses.PARTS[c.part] == "Tech" and
              first["id"] == "universal-short-hop" and first["id"] in c.here)

        told = play([lambda: Hopper(1), lambda: Hopper(12)], "short-hop")
        check("a tap is a short hop, a held jump a full hop",
              c.results == [True, False] and "Short hop" in told[0] and
              "Full hop" in told[1], "; ".join(told))
        saved = courses.Progress(save).drill("universal-short-hop")
        check("and both are counted", saved["tries"] == 2 and
              saved["yes"] == 1, str(saved))

        for _ in range(3):
            tap("Down")
        check("Wavedash is three rows down, and plays here",
              c.drills()[c.row[c.part]]["id"] == "universal-wavedash" and
              "universal-wavedash" in c.here)
        told = play([Dasher, lambda: Hopper(1)], "wavedash")
        check("an air dodge as Fox leaves the ground is a wavedash; a "
              "jump alone is not",
              c.results == [True, False] and
              ("Frame-perfect" in told[0] or "in the window" in told[0])
              and "No air dodge" in told[1], "; ".join(told))
        check("leaving comes back to Wavedash's row",
              c.screen == "list" and
              c.drills()[c.row[c.part]]["id"] == "universal-wavedash")
        bad = [line.strip()[:160] for line in w.log
               if "aurora" in line and ("warn" in line or "error" in line)]
        check("the interface raised no warnings", not bad,
              "; ".join(bad[:3]))
    finally:
        if w is not None:
            w.close()
        left = window.leftovers()
        check("nothing left running", not left, str(left))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
