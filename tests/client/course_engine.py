"""A drill on the course engine in the native client, checked off screen.

    python tests/client/course_engine.py [--shots DIR]

Fox's course, Punish, "Shine out of shield": a drill ported from the
overlay's course engine (tools/melee_course). D-pad up opens its guide in
the column; D-pad right there plays a demonstration, which must be graded a
success (the shine on out-of-shield frame 4, as in the overlay); then a try
by someone who only holds shield must fail, and be counted; holding START
leaves, and the try is in the save.
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
from pausekeys import Chooser, leave  # noqa: E402

DRILL = "fox-shine-oos"
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    args = ap.parse_args()
    save = os.path.join(tempfile.mkdtemp(prefix="melee-client-"),
                        "client.json")
    w = c = None

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
        c = client.Client(w, source="keyboard", save=save,
                          out=tempfile.mkdtemp(prefix="melee-ui-"))
        w.pace(False)
        frames(6)
        tap("x")
        tap("x")
        frames(6)
        check("the drill plays on the course engine",
              c.here.get(DRILL) == courses.COURSE)
        # find the part with the drill and open it
        for _ in range(4):
            if c.screen == "hub" and DRILL in [
                    d["id"] for d in c.course["parts"][
                        courses.PARTS[int(c.hub_at[1:])]]]:
                break
            tap("Right")
        tap("x")
        while c.drills()[c.row[c.part]]["id"] != DRILL:
            tap("Down")
        check("Shine out of shield is in the list", c.screen == "list")

        seen = dict(guide=False, demo=None, tries=[], step=0, wait=0)

        def press(game, key, frames_held=2):
            seen["hold"] = (key, frames_held)
            game.key(key)

        def person(game, frame):
            # one frame of the test's player; `frame` -1 between attempts,
            # -2 in the guide
            if seen.get("hold"):
                key, left = seen["hold"]
                if left <= 1:
                    game.key(key, False)
                    seen["hold"] = None
                else:
                    seen["hold"] = (key, left - 1)
                return
            step = seen["step"]
            if step == 0 and frame == 0 and not seen.get("let_go"):
                game.key("x", False)             # the A that started it
                seen["let_go"] = True
            if step == 0 and frame >= 0:
                seen["wait"] += 1
                if seen["wait"] > 20:
                    press(game, "t")             # D-pad up: the guide
                    seen["step"] = 1
            elif step == 1 and c.in_guide:
                seen["guide"] = True
                shot("course-guide")
                press(game, "h")                 # D-pad right: watch
                seen["step"] = 2
            elif step == 2 and c.last_result and c.last_result.get("demo"):
                seen["demo"] = dict(c.last_result)
                seen["step"] = 3
                seen["wait"] = 0
            elif step == 3 and frame >= 0:
                game.key("s")                    # hold shield, nothing else
                if c.results_now():
                    seen["tries"] = list(c.results_now())
                    game.key("s", False)
                    seen["step"] = 4
            elif step == 4:
                seen.setdefault("out", Chooser(c, "list"))(game)

        c.person = person
        tap("x", after=0)
        for _ in range(3000):
            if c.screen != "drill" and seen["step"] == 4:
                break
            frames(1)
        w.key("Return", False)
        frames(6)
        demo = seen["demo"] or {}
        check("D-pad up opens the guide", seen["guide"])
        check("D-pad right there plays a demonstration: a success on "
              "frame 4", demo.get("success") is True and
              demo.get("measured") == 4 and demo.get("target") == 4,
              demo.get("full_words", "none"))
        check("a try holding only shield fails and is counted",
              seen["tries"] == [False], str(seen["tries"]))
        check("holding START goes back to the list", c.screen == "list")
        p = c.progress.drill(DRILL)
        check("the try is in the save", p.get("tries") == 1, str(p))
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
