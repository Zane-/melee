"""Every Versus game mode against the standard format (docs/ai/game-modes.md),
with no game: a second.

    python tests/client/modes_format.py

modes.check holds each mode in MODES to the format (its words, ident,
icon and colours; its options; its score played through random runs of
KOs with every setting). Then Tug of War's rules, by hand: a KO pulls the
rope a point toward the side that took it, `lead` ahead wins, the HUD's
stocks the lead of the side ahead.
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))

import icons  # noqa: E402
import modes  # noqa: E402
import native  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def main():
    for ident, problems in modes.check_all(
            set(icons.ICON), native.CHARACTERS, native.STAGES).items():
        check("%s is in the format" % ident, not problems,
              "; ".join(problems))

    # a mode that breaks the format is caught
    class Broken(modes.TugOfWar):
        ident = "Broken Mode"
        colour = "orange"

        def ko(self, port):
            self.winner = 2
    problems = modes.check(Broken, set(icons.ICON))
    check("a mode out of the format is caught", len(problems) >= 2,
          "; ".join(problems))

    names = ["Fox", "Falco"]
    for lead in (2, 3, 4, 5):
        m = modes.TugOfWar(lead=lead)
        seen = [(m.stocks(), m.status(names))]
        for _ in range(lead):
            m.ko(1)
            seen.append((m.stocks(), m.status(names)))
        check("win by %d: %d of your KOs win, a stock more each" % (
            lead, lead), m.winner == 0 and
            [s for s, _ in seen] == [(k, 0) for k in range(lead + 1)] and
            seen[0][1] == "Even" and seen[1][1] == "Fox +1" and
            seen[-1][1] == "Game: Fox", str(seen))
    m = modes.TugOfWar(lead=3)
    for port in (1, 0, 0, 1, 1, 0):
        m.ko(port)
    check("trades pull it back and forth: even after three each",
          m.lead == 0 and m.stocks() == (0, 0) and m.winner is None)
    m.ko(0)
    check("their KO from even: a stock in their HUD, none in yours",
          m.stocks() == (0, 1) and m.status(names) == "Falco +1")
    check("a setting out of its values falls back to the default",
          modes.TugOfWar(lead=9).settings == {"lead": 2})
    o = modes.TugOfWar.options[0]
    check("left and right stop at the ends",
          o.step(2, -1) == 2 and o.step(5, 1) == 5 and o.step(3, 1) == 4)
    check("the options' words", o.words(1) == "1 stock" and
          o.words(3) == "3 stocks" and
          modes.TugOfWar(lead=4).line() == "Start even. Win by 4 stocks.")
    # what a mode fixes has to be the native build's
    class Elsewhere(modes.ShineBattle):
        ident = "elsewhere"
        fighters = ("fox", "somebody")
        stage = "the-moon"
    problems = modes.check(Elsewhere, set(icons.ICON), characters=native.
                           CHARACTERS, stage_ids=native.STAGES)
    check("fixed fighters and a stage the native build lacks are caught",
          len(problems) == 2, "; ".join(problems))

    # Shine Battle: a stock match, shine only
    m = modes.ShineBattle()
    check("Shine Battle: Fox against Fox on Jungle Japes, 4 stocks each "
          "from the start, shine only", m.fighters == ("fox", "fox") and
          m.stage == "jungle-japes" and m.stocks() == (4, 4) and
          m.moves() == "shine" and m.winner is None)
    m.ko(0)
    check("a KO is a stock less", m.stocks() == (3, 4) and
          m.status(names) == "Stocks 3 – 4")
    for _ in range(4):
        m.ko(1)
    check("the last stock lost loses", m.winner == 0 and
          m.stocks() == (3, 0) and m.result(names) ==
          "Fox wins, 3 stocks left")
    check("its settings: stocks, Firefox and Illusion",
          modes.ShineBattle(stocks=2).stocks() == (2, 2) and
          modes.ShineBattle(recovery="On").moves() == "recovery" and
          modes.ShineBattle.options[1].words("Off") == "Off")
    m = modes.ShineBattle()
    stand = dict(state=14, percent=0.0)
    m.tick([dict(state=360, percent=0.0), stand])
    m.tick([dict(state=361, percent=0.0), dict(state=75, percent=5.0)])
    m.tick([dict(state=361, percent=0.0), dict(state=75, percent=5.0)])
    m.tick([stand, dict(state=14, percent=5.0)])
    m.tick([dict(state=365, percent=0.0), dict(state=14, percent=5.0)])
    check("its stats: shines started, and the ones that hurt the other",
          m.shines == [2, 0] and m.landed == [1, 0],
          "%s %s" % (m.shines, m.landed))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
