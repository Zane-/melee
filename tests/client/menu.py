"""The native client's menus, checked without a person or a desktop: the
client runs on a virtual display and keys are pressed on that display.

    python tests/client/menu.py [--shots DIR]

Main menu: the focus moves between the panels the way the layout says, and
A on a panel that is not built says so and goes nowhere. Character select:
moving, the card following, B back, A starts a match as that character
with the game given the pad again. Holding START in the match comes back;
a second character can be played after the first. --shots saves a picture
of each screen (under build/shots/ they stay out of the repository).
"""
import argparse
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))

import client  # noqa: E402
import window  # noqa: E402
from native import CHARACTERS  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for a picture of each screen")
    args = ap.parse_args()
    w = None

    def frames(n):
        for _ in range(n):
            c.frame()

    def tap(key, after=6):
        w.key(key)
        frames(2)
        w.key(key, False)
        frames(after)

    def shot(name):
        if args.shots:
            w.shot(os.path.join(args.shots, name + ".png"))

    try:
        w = window.Window(window=(1280, 720))
        w.step(30)
        c = client.Client(w, source="keyboard", out=tempfile.mkdtemp(prefix="melee-ui-"))
        w.pace(False)
        frames(10)
        shot("main")
        check("it opens on the main menu with Train in focus",
              c.screen == "main" and c.focus == "train")

        seen = []
        for key in ("Right", "Down", "Right", "Down", "Left", "Up", "Left"):
            tap(key)
            seen.append(c.focus)
        check("the focus moves panel to panel",
              seen == ["lab", "events", "versus", "controls", "events",
                       "lab", "train"], " ".join(seen))
        tap("Right")
        tap("x")
        check("A on a panel that is not built goes nowhere",
              c.screen == "main" and c.focus == "lab")
        tap("Left")

        tap("x")
        check("A on Train opens the character select at Fox",
              c.screen == "chars" and c.roster[c.at]["id"] == "fox")
        shot("characters")
        tap("z")
        check("B goes back to the main menu", c.screen == "main")
        tap("x")

        tap("Down")
        tap("Right")
        name = c.roster[c.at]["id"]
        check("the stick moves over the roster", name == "marth", name)
        for key in ("Down", "Down", "Down", "Right", "Right", "Right",
                    "Right", "Right", "Right", "Right"):
            tap(key, after=2)
        check("and stops at its edges",
              c.roster[c.at]["id"] == "zelda", c.roster[c.at]["id"])
        tap("Up")
        tap("Up")
        tap("Up")
        tap("Left")
        tap("Left")
        tap("Left")
        tap("Left")
        tap("Left")
        pick = c.roster[c.at]["id"]
        shot("characters-" + pick)

        tap("x", after=30)
        me = w.fighter(0)
        check("A starts a match as that character",
              c.screen == "match" and me.ckind == CHARACTERS[pick],
              "%s, ckind %d" % (pick, me.ckind))
        frames(150)
        shot("match")
        x0 = w.fighter(0).pos[0]
        w.key("Right")
        frames(30)
        w.key("Right", False)
        frames(20)
        check("in the match the pad is the fighter's",
              abs(w.fighter(0).pos[0] - x0) > 10,
              "moved %.1f" % (w.fighter(0).pos[0] - x0))

        w.key("Return")
        frames(50)
        w.key("Return", False)
        frames(10)
        check("holding START comes back to the character select",
              c.screen == "chars" and c.roster[c.at]["id"] == pick)
        x1 = w.fighter(0).pos[0]
        tap("Right")
        tap("Right")
        frames(30)
        check("in the menu the pad is not the fighter's",
              abs(w.fighter(0).pos[0] - x1) < 0.01,
              "moved %.2f" % (w.fighter(0).pos[0] - x1))
        second = c.roster[c.at]["id"]
        tap("x", after=30)
        check("a second character can be played after the first",
              c.screen == "match" and second != pick and
              w.fighter(0).ckind == CHARACTERS[second],
              "%s, ckind %d" % (second, w.fighter(0).ckind))
        w.key("Return")
        frames(50)
        w.key("Return", False)
        frames(5)
        tap("z")
        check("and the main menu remembers who was played",
              c.screen == "main" and c.last["id"] == second)
        shot("main-after")
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
