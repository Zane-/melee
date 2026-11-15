"""The Rules every Versus mode is played by, in the native client, checked
without a person or a desktop (keys pressed on a virtual display).

    python tests/client/rules.py [--shots DIR]

The owner, 2026-11-14: "While selecting any game mode there should be
global options openable via Z which has basic settings like time, items,
random stage selection filters, etc. just like the original game!".

Z on the mode select opens the Rules (the D key is Z on the keyboard): a
time limit, items, the damage ratio, then the Item switch and the Random
stages, each a page of every item or stage that A switches (Y all on or
off; X the legal stages only). The client keeps them. Then Unlimited with
a one-minute limit, items at medium and the ratio at 1.5, on a stage the
Random of the stage select picks from the legal six: the match is played
by those rules (the host's), and at TIME! the results come up, the line
saying who won on time (or that it was a draw).
"""
import argparse
import json
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))

import client  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vselkeys as vk  # noqa: E402
import modes  # noqa: E402
import stages  # noqa: E402
import window  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    args = ap.parse_args()
    if args.shots:
        os.makedirs(args.shots, exist_ok=True)
    save = os.path.join(tempfile.mkdtemp(), "s.json")
    w = c = None

    def frames(n):
        for _ in range(n):
            c.frame()

    def tap(key, after=5):
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
        c = client.Client(w, source="keyboard",
                          out=tempfile.mkdtemp(prefix="melee-ui-"),
                          save=save)
        w.pace(False)
        frames(6)
        tap("Left")                 # Versus
        tap("x")
        tap("x")                    # Local
        check("Versus > Local: the mode select", c.screen == "modes")
        tap("d")                    # Z
        r = c.rules_edit if c.screen == "rules" else None
        check("Z opens the Rules: no time limit, no items, the ratio 1.0",
              r is not None and r.plain() and c.rules_at == 0, c.screen)
        shot("rules")
        tap("Right")                # time: 1 minute
        tap("Down")
        for _ in range(3):          # items: off, very low, low, medium
            tap("Right")
        tap("Down")
        for _ in range(5):          # ratio: 1.0 to 1.5
            tap("Right")
        kept = json.load(open(save)).get("rules", {})
        check("left and right change them, and the client keeps them",
              c.rules_edit.settings == dict(time=1, items=2, ratio=1.5) and
              kept.get("time") == 1 and kept.get("items") == 2 and
              kept.get("ratio") == 1.5, str(c.rules_edit.settings))
        shot("rules-set")

        tap("Down")                 # the Item switch
        tap("x")
        check("A on the Item switch opens every item",
              c.screen == "switch" and c.switch_page == "items", c.screen)
        tap("x")                    # the first off
        first = modes.ITEMS[0]
        off_one = set(c.rules_edit.items_off)
        tap("c")                    # Y: all on again
        all_on = set(c.rules_edit.items_off)
        tap("c")                    # Y: all off
        all_off = set(c.rules_edit.items_off)
        tap("c")                    # and all on
        check("A switches the item in focus; Y all on, then all off",
              off_one == {first[1]} and not all_on and
              len(all_off) == len(modes.ITEMS) and
              not c.rules_edit.items_off,
              "%s; %d; %d" % (off_one, len(all_on), len(all_off)))
        shot("items")
        tap("z")
        check("B goes back to the Rules, on the Item switch",
              c.screen == "rules" and c.rules_at == 3, c.screen)

        tap("Down")                 # the Random stages
        tap("x")
        tap("v")                    # X: the legal six only
        legal = {s["id"] for s in stages.LEGAL}
        on = {s["id"] for s in stages.STAGES} - c.rules_edit.stages_off
        check("the Random stages: X leaves the legal six on",
              c.screen == "switch" and on == legal, str(sorted(on)))
        shot("stages")
        tap("z")
        tap("z")
        check("B, B: back to the mode select", c.screen == "modes",
              c.screen)

        tap("x", after=10)          # Unlimited: the classic select
        vk.setup(c, tap, "fox", "marth", kind="dummy")
        tap("Return", after=10)     # START: the stage select
        check("on to the stage select", c.screen == "stages", c.screen)
        tap("v", after=20)          # X: Random
        frames(30)
        check("Random picks one of the stages the switch has on",
              c.screen == "versus" and c.stage_now in legal,
              "%s %s" % (c.screen, c.stage_now))
        want = dict(time=60, items=2, mask=c.vs_rules().mask(), ratio=1.5)
        check("the match is played by the Rules (the host's)",
              c.rules_now == want and
              w.match_info.get("rules") == want, str(c.rules_now))
        shot("match")
        for _ in range(60 * 75):    # the minute, the countdown, TIME!
            if c.screen == "results":
                break
            frames(1)
        page = open(os.path.join(c.out, "results.rml")).read() \
            if c.screen == "results" else ""
        check("at TIME! the results come up, won or drawn on time",
              c.screen == "results" and "on time" in page,
              "%s; %s" % (c.screen, c.game_mode.result_line(
                  c.sides()) if c.game_mode else ""))
        shot("results")
        tap("z", after=10)
        check("B from the results goes back to the stages",
              c.screen == "stages", c.screen)
    finally:
        if w is not None:
            w.close()
        left = window.leftovers()
        check("nothing left running", not left, str(left))

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
