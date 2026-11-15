"""Versus's game modes in the native client: the selector, a mode's
options, and Tug of War, checked without a person or a desktop (keys
pressed on a virtual display).

    python tests/client/versus_modes.py [--shots DIR]

Versus > Local opens the mode select (Unlimited, Tug of War); a mode with
settings opens its options next (Tug of War: win by 2 to 5; the client
keeps them), then the characters. Tug of War, won by 3, against a fighter
nobody plays; KOs are made by dropping a fighter below the blast zone
(Native.place). The score is a tug of war: a KO pulls it a point toward the
side that took it, shown as the HUD's stocks (the side ahead has its lead
in icons, the other none; even, nothing); three ahead wins, the winning
stock shown, then the game stopping with the result over it. A plays it
again from even, B goes back to the stages. The owner, 2026-11-14:
"scoring works like tug of war ... at the start nothing shows up, then as
a player takes a stock, it either removes the opponent's stock or adds one
to theirs"; "rename it to Tug of War ... make sure that each game mode has
support for settings (i.e. win by 3 ...) ... select the mode, then
configure options, then start game!".
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
import window  # noqa: E402

checks = []
GONE = set(modes.DEAD) | {11, 12, 13}     # dead, asleep, coming back


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

    def stocks():
        p = w.state()["p"]
        return (p[0]["stocks"] if p[0] else None,
                p[1]["stocks"] if p[1] else None)

    def grey():
        """Whether each side's colourless stock shows (a mode with a board
        has none)."""
        out = []
        for i in (0, 1):
            try:
                out.append("on" in json.loads(w._cmd("ui look gs%d" % i))[
                    "class"].split())
            except window.NativeError:
                out.append(False)
        return tuple(out)

    def knot():
        """The rope's knot: (its node, whose icon rides it or "even")."""
        cls = json.loads(w._cmd("ui look twmark"))["class"].split()
        at = next(int(c[3:]) for c in cls if c.startswith("twk"))
        who = "even" if "even" in cls else "who0" if "who0" in cls else \
            "who1" if "who1" in cls else "?"
        return at, who

    def lit():
        """The rope's nodes lit in a side's colour: (P1's, P2's)."""
        out = [0, 0]
        for i in range(2 * c.game_mode.settings["lead"] + 1):
            cls = json.loads(w._cmd("ui look twn%d" % i))["class"].split()
            out[0] += "lit0" in cls
            out[1] += "lit1" in cls
        return tuple(out)

    def until_results(budget=400):
        """Frames until the game has ended the match (GAME!) and the
        results are up."""
        for _ in range(budget):
            if c.screen == "results":
                break
            frames(1)
        check("GAME! plays out, the game ends the match, then the "
              "results", c.screen == "results", c.screen)

    def to_mode(ident):
        """The selector's stick moved onto mode `ident`."""
        want = [m.ident for m in modes.MODES].index(ident)
        for _ in range(len(modes.MODES) * 2):
            if c.mode_at == want:
                return
            tap("Right" if c.mode_at < want else "Left")
        raise RuntimeError("the selector never reached %s" % ident)

    def rule(port):
        """The moves port `port` may use (src/host/moves.c)."""
        return w._cmd("moves %d" % port).split()[-1]

    def ko(port, budget=900):
        """Port `port` dropped below the blast zone once it is back in
        play; then frames until the client has seen the KO."""
        for _ in range(budget):
            f = w.state()["p"][port]
            if f and f["state"] not in GONE:
                break
            c.frame()
        else:
            raise RuntimeError("port %d never came back into play" % port)
        w.place(port, 0, -260, 1, air=True)
        frames(4)

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
        tap("x")                    # Local
        check("Versus > Local opens the mode select, Unlimited first",
              c.screen == "modes" and c.mode_at == 0 and
              [m.ident for m in modes.MODES][:2] ==
              ["unlimited", "tug-of-war"], c.screen)
        shot("modes-unlimited")
        tap("Right")
        check("the stick moves to Tug of War", c.mode_at == 1)
        shot("modes-tug")
        tap("z")
        check("B goes back to Local or Online", c.screen == "vmenu")
        tap("x")
        to_mode("tug-of-war")
        tap("x")
        check("A on Tug of War opens its options: win by 2 at first",
              c.screen == "mopts" and c.versus_mode == "tug-of-war" and
              c.mode_now.settings == {"lead": 2}, c.screen)
        tap("Right")
        tap("Right")
        tap("Left")
        check("left and right step win by, either way",
              c.mode_now.settings["lead"] == 3,
              str(c.mode_now.settings))
        shot("options-win-by-3")
        tap("z")
        check("B goes back to the modes, the card saying win by 3",
              c.screen == "modes" and
              c.make_mode(modes.TugOfWar).line().endswith("3 stocks."))
        tap("x")
        check("and the options keep it", c.screen == "mopts" and
              c.mode_now.settings["lead"] == 3)
        tap("x", after=10)
        check("A goes on to the character select (the classic one, two "
              "cards for a 1v1 mode)", c.screen == "vsel" and
              len(c.vslots) == 2, c.screen)
        tap("z")
        check("B from the characters goes back to the options",
              c.screen == "mopts")
        tap("x", after=10)
        vk.setup(c, tap, "fox", "marth", kind="dummy")
        tap("Return", after=10)     # START: the stage select
        tap("x", after=20)          # Battlefield: the match
        frames(90)
        check("the match is Tug of War won by 3, even",
              c.screen == "versus" and c.game_mode.ident == "tug-of-war" and
              c.game_mode.settings["lead"] == 3 and c.game_mode.lead == 0 and
              c.game_mode.status(c.sides()) == "Even")
        check("the rope over the game: 7 nodes, the knot in the middle",
              knot() == (3, "even") and lit() == (0, 0) and
              "twn6" in open(os.path.join(c.out, "versus.rml")).read() and
              "twn7" not in open(os.path.join(c.out, "versus.rml")).read(),
              str(knot()))
        check("the HUD left as the endless match's (its own stock icon by "
              "each %): no colourless ones", grey() == (False, False),
              "%s %s" % (stocks(), grey()))
        shot("even")

        ko(1)
        check("you take a stock: Fox +1, the knot a node toward you with "
              "your stock icon on it", c.game_mode.lead == 1 and
              knot() == (2, "who0") and lit() == (1, 0) and
              c.game_mode.status(c.sides()) == "Fox +1", str(knot()))
        frames(30)
        shot("you-plus-one")
        ko(0)
        check("they take one back: the knot back in the middle",
              c.game_mode.lead == 0 and knot() == (3, "even") and
              lit() == (0, 0), str(knot()))
        frames(6)
        shot("even-again")
        ko(0)
        check("they take another: the knot a node toward them, their "
              "icon on it", c.game_mode.lead == -1 and
              knot() == (4, "who1") and lit() == (0, 1), str(knot()))
        frames(400)
        check("the score holds through both coming back",
              knot() == (4, "who1") and c.screen == "versus", str(knot()))
        shot("them-plus-one")
        for want in (0, 1, 2):
            ko(1)
            check("you pull it to %+d" % want, c.game_mode.lead == want and
                  knot()[0] == 3 - want and c.screen == "versus",
                  "%d %s" % (c.game_mode.lead, knot()))
        frames(30)
        shot("you-plus-two")
        ko(1)
        check("three ahead wins: the knot on your goal", c.game_mode.winner
              == 0 and knot() == (0, "who0") and lit() == (3, 0),
              "%s %s" % (c.screen, knot()))
        f0 = w.state()["p"][0]
        frames(10)
        f1 = w.state()["p"][0]
        check("the game ends the match itself, as a stock match's last "
              "stock: everything stands still for its GAME!",
              (f0["x"], f0["y"], f0["frame"]) == (f1["x"], f1["y"],
                                                  f1["frame"]) and
              c.screen == "versus", c.screen)
        frames(20)
        shot("game")
        until_results()
        page = open(os.path.join(c.out, "results.rml")).read()
        check("then the results: the winner, each side's numbers, the "
              "mode's own first", c.screen == "results" and
              "Fox pulled it 3 ahead" in page and
              page.index("Biggest lead") < page.index("Damage dealt"),
              c.screen)
        check("the numbers: you took 5 stocks, they took 2; leads of 3 "
              "and 1; each pulled it back to even once",
              c.match_stats.taken == [5, 2] and
              c.game_mode.biggest == [3, 1] and
              c.game_mode.evened == [1, 1] and
              c.match_stats.dealt[0] >= 0,
              "%s %s %s" % (c.match_stats.taken, c.game_mode.biggest,
                            c.game_mode.evened))
        shot("results")
        tap("x", after=20)
        frames(60)
        check("A plays it again from even",
              c.screen == "versus" and c.game_mode.lead == 0 and
              c.game_mode.winner is None and stocks() == (0, 0),
              "%s %s" % (c.screen, stocks()))
        for _ in range(3):
            ko(0)
        check("they win by three the same way", c.game_mode.winner == 1
              and knot() == (6, "who1"), c.screen)
        until_results()
        tap("z", after=10)
        check("B goes back to the stages", c.screen == "stages", c.screen)
        check("leaving the match gives every move back",
              rule(0) == "all" and rule(1) == "all")

        # Shine Battle: Fox against Fox on Jungle Japes, shine only
        tap("z", after=8)           # the select
        tap("z", after=8)           # Tug of War's options
        tap("z", after=8)           # the modes
        to_mode("shine-battle")
        check("Shine Battle is third on the selector",
              c.screen == "modes" and c.mode_at == 2 and
              modes.MODES[c.mode_at].ident == "shine-battle", c.screen)
        shot("modes-shine")
        tap("x")
        check("its options: 4 stocks, Firefox and Illusion off",
              c.screen == "mopts" and c.mode_now.settings ==
              {"stocks": 4, "recovery": "Off"}, str(c.mode_now.settings))
        tap("Down")
        tap("Right")
        check("Firefox and Illusion turned on, the panel drawn (its value a "
              "word: it once crashed the client)", c.screen == "mopts" and
              c.mode_now.settings["recovery"] == "On" and ">On<" in open(
                  os.path.join(c.out, "part-spanel.rml")).read(),
              str(c.mode_now.settings))
        tap("Left")
        tap("Up")
        shot("options-shine")
        check("its A goes on to the opponent",
              "Choose opponent" in open(os.path.join(
                  c.out, "mopts.rml")).read())
        tap("x", after=10)
        check("A: the select with the characters fixed, Fox and Fox",
              c.screen == "vsel" and [sl["char"]["id"] for sl in
                                      c.vslots] == ["fox", "fox"], c.screen)
        tap("Right")
        tap("x", after=6)
        check("A in the grid does not change them",
              [sl["char"]["id"] for sl in c.vslots] == ["fox", "fox"])
        vk.set_kind(c, tap, 1, "dummy")
        shot("opponent-shine")
        tap("Return", after=20)     # START: the stage is the mode's
        frames(90)
        check("A starts the match: no stage select, Jungle Japes",
              c.screen == "versus" and c.stage_now == "jungle-japes" and
              w.match_info["stage"] == "jungle-japes" and
              w.match_info["p1"] == "fox" and w.match_info["p2"] == "fox",
              "%s %s" % (c.screen, w.match_info))
        check("both sides shine only", rule(0) == "shine" and
              rule(1) == "shine", "%s %s" % (rule(0), rule(1)))
        check("4 stocks each in the HUD from the start, and no rope",
              stocks() == (4, 4) and grey() == (False, False) and
              "twmark" not in open(os.path.join(c.out, "versus.rml")).read(),
              str(stocks()))
        shot("shine-start")
        ko(0)
        check("a KO: a stock less", stocks() == (3, 4) and
              c.game_mode.status(c.sides()) == "Stocks 3 – 4",
              str(stocks()))
        for _ in range(4):
            ko(1)
        check("their last stock lost: you win; the game's own stock match "
              "ends", c.game_mode.winner == 0 and stocks()[1] == 0,
              str(stocks()))
        until_results()
        page = open(os.path.join(c.out, "results.rml")).read()
        check("the results: 3 stocks left, the shines counted",
              c.screen == "results" and "3 stocks left" in page and
              "Shines that hit" in page and "Characters" in page,
              c.screen)
        worn = [w.state()["p"][i]["costume"] for i in (0, 1)]
        check("each Fox's stock icon in the costume it wore (the second "
              "in the game's next)", worn[0] != worn[1] and all(
                  "stock/fox-%d.png" % k in page for k in worn), str(worn))
        shot("results-shine")
        tap("z", after=10)
        check("B goes back to the select", c.screen == "vsel" and
              rule(0) == "all", c.screen)
        tap("z")
        check("and B again to the mode's options", c.screen == "mopts")
    finally:
        if w is not None:
            w.close()

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
