"""The native client's course screens and a drill, checked without a person
or a desktop: the client runs on a virtual display, keys are pressed there,
and the "player" in the drill is key presses decided from what the fighter
is doing (the one from tests/actor/train.py).

    python tests/client/course.py [--shots DIR]

Fox's course: the hub and its four parts, a part's drills from
data/courses/fox.md, every one of them playable here, a drill (the short
hop) judged attempt by attempt with the verdict shown, the numbers kept,
the done mark, where you left off, and all of it still there after the
client is started again. (A drill on the course engine, with its guide and
demonstration: tests/client/course_engine.py.)
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


DRILL = "universal-short-hop"
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for a picture of each screen")
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

    def shot(name):
        if args.shots:
            w.shot(os.path.join(args.shots, name + ".png"))

    try:
        w = window.Window(window=(1280, 720))
        w.step(30)
        c = client.Client(w, source="keyboard", save=save, out=tempfile.mkdtemp(prefix="melee-ui-"))
        w.pace(False)
        frames(6)
        tap("x")
        tap("x")
        frames(6)
        shot("hub")
        check("A on Fox opens the course hub with Tech in focus",
              c.screen == "hub" and c.hub_at == "p0" and
              c.course["id"] == "fox")
        seen = []
        for key in ("Right", "Right", "Right", "Right", "Down", "Up"):
            tap(key)
            seen.append(c.hub_at)
        check("the focus moves over the parts and to free play and back",
              seen == ["p1", "p2", "p3", "p3", "free", "p3"], " ".join(seen))

        tap("Left")
        tap("Left")
        tap("Left")
        tap("x")
        names = [d["name"] for d in c.drills()]
        check("A opens the part's drills, as the course file lists them",
              c.screen == "list" and courses.PARTS[c.part] == "Tech" and
              names[:3] == ["Short hop", "L-cancel", "SHFFL"] and
              len(names) == 16, "%d drills" % len(names))
        every = [d["id"] for part in c.course["parts"].values()
                 for d in part]
        missing = [d for d in every if d not in c.here]
        check("every drill of the course plays here", not missing and
              len(every) == 46, "%d drills, %d not" % (len(every),
                                                      len(missing)))
        row = c.row[c.part]
        shot("drills")

        # three short hops: tapped, tapped, held (a full hop); then out.
        # The jump is X, the V key.
        plans = [2, 2, 10]
        state = dict(tries=0, press=0, idle=0)

        def person(game, frame):
            if state["press"]:
                state["press"] -= 1
                if state["press"] == 0:
                    game.key("v", False)
                return
            if state["tries"] == 0 and frame == 0:
                game.key("x", False)        # the A that started the drill
            if len(c.results_now()) >= len(plans):
                state.setdefault("out", Chooser(c, "list"))(game)
                return
            f = game.fighter(0)
            state["idle"] = state["idle"] + 1 if f.state == 14 else 0
            if state["idle"] >= 8 and state["tries"] == len(c.results_now()):
                game.key("v")
                state["press"] = plans[state["tries"]]
                state["tries"] += 1
                state["idle"] = 0
                if state["tries"] == 2:
                    shot("drill")

        c.person = person
        w.key("x")
        for _ in range(20):    # the drill runs inside one of these frames,
            c.frame()          # the one that sees the press, until left
            if c.results is not None:
                break
        w.key("x", False)
        w.key("v", False)
        w.key("Return", False)
        c.person = None
        w.pace(False)
        frames(6)
        saved = courses.Progress(save).drill(DRILL)
        check("the drill judges each attempt: success, success, failure",
              c.results == [True, True, False], str(c.results))
        check("leaving comes back to the same row of the list",
              c.screen == "list" and c.row[c.part] == row)
        check("the numbers are kept on disk",
              saved["tries"] == 3 and saved["yes"] == 2 and
              saved["best"] == 2, str(saved))
        tap("c")
        shot("drills-done")
        check("Y marks the drill done, and that is kept too",
              courses.Progress(save).done(DRILL))
        tap("z")
        left = c.left_off()
        check("the hub knows where you left off",
              c.screen == "hub" and left is not None and
              left["id"] == DRILL)
        shot("hub-after")
        tap("Left")
        tap("v")
        check("X continues there",
              c.screen == "list" and
              c.drills()[c.row[c.part]]["id"] == DRILL)
        tap("s")
        tap("a")
        check("R and L turn to the next part and back",
              c.screen == "list" and courses.PARTS[c.part] == "Tech")
        tap("z")
        tap("Down")
        tap("x", after=20)
        check("free play starts from the hub",
              c.screen == "match" and w.fighter(0).fp)
        leave(c, w, "back", frames)
        check("and Back in the pause menu comes back to it",
              c.screen == "hub")

        again = client.Client(w, source="keyboard", save=save, out=tempfile.mkdtemp(prefix="melee-ui-"))
        check("started again, the client still has all of it",
              again.progress.done(DRILL) and
              again.progress.drill(DRILL)["tries"] == 3)
        bad = [line.strip()[:160] for line in w.log
               if "aurora" in line and ("warn" in line or "error" in line)]
        check("the interface raised no warnings", not bad,
              "; ".join(bad[:3]))
    finally:
        if w is not None:
            w.close()
        left_running = window.leftovers()
        check("nothing left running", not left_running, str(left_running))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
