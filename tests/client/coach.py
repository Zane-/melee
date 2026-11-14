"""The pause menu's tabs, the input display, and the coach, in the native
client, checked off screen.

    python tests/client/coach.py [--shots DIR]

Fox's course, Punish, "Shine out of shield". The pause menu has the
drill's tab, the course's and the settings' (R goes round them), and Input
display there turns TM-CE's controller on (the game makes it). Then a
player who only holds shield misses three times in a row: the coach's card
opens, with the try's path and the demonstration's, and a headline. Y
replays the try from its start: it plays to the same verdict, a frame at a
time at the end; B goes back to the card, A to the drill.
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
from pausekeys import Chooser  # noqa: E402

DRILL = "fox-shine-oos"
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))



def waiting_for(drills):
    """The drills this test plays that are not back yet: the drills were
    wiped 2026-11-14 and are rebuilt one at a time in the drill format
    (docs/ai/drill-format.md); this test moves onto the first rebuilt ones
    it can use."""
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(
        __file__)), "..", "..", "tools"))
    from melee_course import registry
    return [d for d in drills if not registry.has(d)]

def main():
    missing = waiting_for(['fox-shine-oos'])
    if missing:
        print("skip: plays %s, not rebuilt yet in the drill format"
              % ", ".join(missing))
        return 0
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
        for _ in range(4):
            if c.screen == "hub" and DRILL in [
                    d["id"] for d in c.course["parts"][
                        courses.PARTS[int(c.hub_at[1:])]]]:
                break
            tap("Right")
        tap("x")
        while c.drills()[c.row[c.part]]["id"] != DRILL:
            tap("Down")

        seen = dict(step=0, wait=0, tabs=[], tries=[], card=None,
                    replay=[], frames=set())

        def press(game, key, frames_held=2):
            seen["hold"] = (key, frames_held)
            game.key(key)

        def person(game, frame):
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
                    press(game, "Return")        # START: the pause menu
                    seen["step"] = 1
            elif step == 1 and c.pause_open:
                seen["tabs"].append(c.pause_tab)
                seen["open"] = seen.get("open", 0) + 1
                if seen["open"] < 4:
                    return                       # drawn, then the picture
                if seen["open"] == 4:
                    shot("pause-drill")
                if c.pause_tab != "Settings":
                    press(game, "s")             # R: the next tab
                elif c.pause_focus != "inputs":
                    press(game, "Down")
                else:
                    press(game, "Right")         # Input display: You
                    seen["step"] = 2
            elif step == 2 and c.pause_open:
                shot("pause-settings")
                press(game, "z")                 # B: back to the drill
                seen["step"] = 3
                seen["wait"] = 0
            elif step == 3 and frame >= 0:
                game.key("s")                    # hold shield, nothing else
                seen["tries"] = list(c.results_now())
            elif step == 3 and frame == -4:      # the coach's card
                game.key("s", False)
                seen["card"] = dict(c.coach_now)
                seen["tries"] = list(c.results_now())
                seen["wait"] += 1
                if seen["wait"] > 4:
                    shot("coach")
                    press(game, "c")             # Y: replay the try
                    seen["step"] = 4
            elif step == 4 and frame == -5:      # the replay
                now = c.replay_now or {}
                seen["frames"].add(now.get("frame"))
                if now.get("frame") and not seen.get("rshot"):
                    shot("replay")
                    seen["rshot"] = True
                if c.replay_result is not None and now.get("paused"):
                    seen["replayed"] = dict(c.replay_result)
                    press(game, "z")             # B: back to the card
                    seen["step"] = 5
            elif step == 5 and frame == -4:
                press(game, "x")                 # A: on with the drill
                seen["step"] = 6
            elif step == 6:
                seen.setdefault("out", Chooser(c, "list"))(game)

        c.person = person
        tap("x", after=0)
        first = {}
        for _ in range(6000):
            if c.screen != "drill" and seen["step"] == 6:
                break
            if c.track is not None and not first and c.results_now():
                first.update(c.last_result or {})
            frames(1)
        w.key("Return", False)
        w.key("s", False)
        frames(6)
        check("the pause menu's tabs: the drill's, the course's, the "
              "settings'", seen["tabs"][:1] == ["Drill"] and
              "Course" in seen["tabs"] and "Settings" in seen["tabs"],
              str(seen["tabs"][:6]))
        check("Input display set to You there, and kept",
              c.settings["inputs"] == "you", c.settings["inputs"])
        made = [line.strip() for line in w.log if "inputs: " in line]
        check("the game made TM-CE's controller", bool(made) and
              "controller" in made[-1], made[-1] if made else "no line")
        card = seen["card"] or {}
        check("three misses in a row open the coach's card",
              seen["card"] is not None and len(seen["tries"]) >= 3 and
              not any(seen["tries"][:3]), str(seen["tries"]))
        check("the card has a headline, the try's path and the "
              "demonstration's", bool(card.get("headline")) and
              bool(card.get("you", [[]])[0]) and card.get("target") is not
              None and bool(card["target"][0]),
              "%r; %d and %s dots" % (
                  card.get("headline"), len(card.get("you", [[]])[0]),
                  len(card["target"][0]) if card.get("target") else None))
        replayed = seen.get("replayed") or {}
        check("Y replays the try to a verdict, frame by frame at the end",
              bool(replayed) and len(seen["frames"] - {None}) >= 3,
              "%s; frames %s" % (replayed.get("words"),
                                 sorted(f for f in seen["frames"] if f)))
        check("the replay ends as the try did", replayed.get("success") is
              False and bool(replayed.get("words")),
              replayed.get("words", "none"))
        check("B and A go back to the drill, and on to the list",
              c.screen == "list", c.screen)
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
