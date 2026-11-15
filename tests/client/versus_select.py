"""Versus's classic character select, checked without a person or a
desktop (keys pressed on a virtual display).

    python tests/client/versus_select.py [--shots DIR]

The owner, 2026-11-14: "build it more like the classic character
selection where there is a single grid of characters and then the port
cards below it! This should allow me to add CPUs at will ... the stock CPU
selector doesn't have a way to select the level. Also the AI model should
start to get preloaded as soon as the characters are locked in and we go
to stage selection". Versus > Local > Unlimited opens one grid of the
characters (nine to a row) and a card per port below it: P1 yours, P2 a
level 9 CPU at first. A in the grid gives the character to the port in
turn; A on a card opens it (who plays it, the CPU's level, the model, the
character); the card after the ports adds a player, up to four. START
with every port's character goes to the stage select; a match then has
every port: three players here, the CPUs at their levels. A model starts
loading as the characters are locked in. A 1v1 mode (Tug of War) keeps to
two cards.
"""
import argparse
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import client  # noqa: E402
import native  # noqa: E402
import opponents  # noqa: E402
import pausekeys  # noqa: E402
import vselkeys as vk  # noqa: E402
import window  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    args = ap.parse_args()
    if args.shots:
        os.makedirs(args.shots, exist_ok=True)
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

    def page():
        return open(os.path.join(c.out, "vselect.rml")).read()

    try:
        w = window.Window(window=(1280, 720))
        w.step(30)
        c = client.Client(w, source="keyboard",
                          out=tempfile.mkdtemp(prefix="melee-ui-"),
                          save=os.path.join(tempfile.mkdtemp(), "s.json"))
        w.pace(False)
        frames(6)
        tap("Left")                 # Versus
        tap("x")
        tap("x")                    # Local: the modes
        tap("x", after=10)          # Unlimited
        check("Versus > Local > Unlimited: the classic select, one grid "
              "of the 26 places nine to a row, P1 yours and P2 a level 9 "
              "CPU", c.screen == "vsel" and
              [s["kind"] for s in c.vslots] == ["you", "cpu"] and
              c.vslots[1]["level"] == 9 and page().count('class="vrrow"')
              == 3 and 'id="vpadd"' in page(), c.screen)
        vk.pick(c, tap, 0, "fox")
        check("A in the grid: your card's character, then the cursor on "
              "the next card without one", c.vslots[0]["char"]["id"] ==
              "fox" and c.vactive == 1, str(c.vactive))
        vk.pick(c, tap, 1, "marth")
        check("and P2's", c.vslots[1]["char"]["id"] == "marth" and
              "P2" in page())
        vk.set_level(c, tap, 1, 6)
        check("P2's card opened: its CPU's level, 6",
              c.vslots[1]["level"] == 6 and "CPU 6" in page(),
              str(c.vslots[1]["level"]))
        vk.add(c, tap)
        check("the card after the ports: a player more, a level 9 CPU, "
              "the grid choosing for it", len(c.vslots) == 3 and
              c.vslots[2]["kind"] == "cpu" and c.vactive == 2 and
              c.varea == "grid", str(len(c.vslots)))
        vk.pick(c, tap, 2, "pikachu")
        vk.add(c, tap)
        vk.pick(c, tap, 3, "kirby")
        check("four players, and no card to add a fifth",
              len(c.vslots) == 4 and 'id="vpadd"' not in page() and
              c.vready(), str(len(c.vslots)))
        shot("vsel-four")
        vk.remove(c, tap, 3)
        check("Player: Remove takes a port out", len(c.vslots) == 3)
        shot("vsel-three")
        tap("Return", after=10)     # START
        check("START, every port with its character: the stage select",
              c.screen == "stages", c.screen)
        tap("z", after=10)
        check("B: back on the select, the ports as they were",
              c.screen == "vsel" and len(c.vslots) == 3 and
              c.vslots[1]["level"] == 6)
        tap("Return", after=10)
        tap("x", after=20)          # Battlefield
        frames(60)
        p = w.state()["p"]
        check("a match of the three: Fox, Marth, Pikachu, the CPUs at "
              "their levels", c.screen == "versus" and len(p) == 3 and
              [f["ckind"] for f in p] == [native.CHARACTERS[x] for x in
                                          ("fox", "marth", "pikachu")] and
              w.match_info["levels"] == (9, 6) and
              w.match_info["others"] == (("pikachu", False, 9),),
              "%s %s" % (c.screen, [f and f["ckind"] for f in p]))
        frames(240)
        p = w.state()["p"]
        check("and they fight: the CPUs move", any(
            abs(f["x"]) > 1 for f in p[1:]), str([round(f["x"]) for f in
                                                   p]))
        shot("match-three")
        pausekeys.leave(c, w, "opp", frames)
        check("the pause menu's Characters: back on the select",
              c.screen == "vsel" and len(c.vslots) == 3, c.screen)
        before = [(f["x"], f["y"], f["frame"], f["state"])
                  for f in w.state()["p"]]
        frames(90)
        after = [(f["x"], f["y"], f["frame"], f["state"])
                 for f in w.state()["p"]]
        check("the match left behind stands still under the select (the "
              "owner: \"I can still hear moves and such going out\")",
              before == after, "%s -> %s" % (before[1], after[1]))

        # a model, loading as the characters are locked in
        models = opponents.models("marth", "fox")
        if models:
            vk.set_kind(c, tap, 1, "model")
            check("P2's card: a trained model, the first for the pairing",
                  c.vslots[1]["kind"] == "model" and
                  c.vslots[1]["model"] == models[0][0],
                  str(c.vslots[1].get("model")))
            tap("Return", after=10)
            check("locked in: the model's process starts on the stage "
                  "select, before the match", c.screen == "stages" and
                  1 in getattr(c, "vbots", {}) and
                  c.vbots[1].model == models[0][0])
            bot = c.vbots[1]
            for _ in range(1800):
                if bot.ready() is not None:
                    break
                frames(1)
            check("and it loads there", bot.ready() is True,
                  bot.error[:80])
            tap("x", after=20)
            frames(60)
            check("the match uses the model already loaded",
                  c.screen == "versus" and c.vplaying.get(1) is bot and
                  getattr(bot, "stage_told", None) == "battlefield")
            pausekeys.leave(c, w, "opp", frames)
            vk.set_kind(c, tap, 1, "cpu")
        else:
            print("(no trained model for Marth against Fox: the preload is "
                  "not checked)")

        # a 1v1 mode keeps to two cards
        tap("z", after=8)           # the modes
        for _ in range(4):
            if c.screen == "modes" and c.mode_at == 1:
                break
            tap("Right" if c.screen == "modes" else "z", after=6)
        tap("x", after=8)           # Tug of War's options
        tap("x", after=10)          # the select
        check("Tug of War: two cards, and none to add a third",
              c.screen == "vsel" and len(c.vslots) == 2 and
              'id="vpadd"' not in page(), "%s %d" % (c.screen,
                                                       len(c.vslots)))
    finally:
        if w is not None:
            w.close()
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
