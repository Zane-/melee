"""Versus's game modes in the native client: the selector and Tennis,
checked without a person or a desktop (keys pressed on a virtual display).

    python tests/client/versus_modes.py [--shots DIR]

Versus > Local opens the mode select (Unlimited, Tennis); Tennis against a
fighter nobody plays. KOs are made by dropping a fighter below the blast
zone (Native.place). The score is a tug of war: a KO pulls it a point
toward the side that took it, shown as the HUD's stocks (the side ahead
has its lead in icons, the other none; at deuce nothing); two ahead wins,
the game stopping with the result over it. A plays it again from deuce,
B goes back to the stages. The owner, 2026-11-14: "scoring works like tug
of war ... you have to win by +2 ... at the start nothing shows up, then as
a player takes a stock, it either removes the opponent's stock or adds one
to theirs".
"""
import argparse
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))

import client  # noqa: E402
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
              [m.ident for m in modes.MODES][:2] == ["unlimited", "tennis"],
              c.screen)
        shot("modes-unlimited")
        tap("Right")
        check("the stick moves to Tennis", c.mode_at == 1)
        shot("modes-tennis")
        tap("z")
        check("B goes back to Local or Online", c.screen == "vmenu")
        tap("x")
        tap("Right")
        tap("x")
        check("A chooses Tennis and opens the character select",
              c.screen == "chars" and c.versus_mode == "tennis")
        tap("z")
        check("B from the characters goes back to the modes",
              c.screen == "modes")
        tap("x")
        tap("x")                    # Fox
        for _ in range(len(c.players())):
            if c.players()[c.who][0] == client.NOBODY:
                break
            tap("h", after=2)
        tap("x")                    # the stage select
        tap("x", after=20)          # Battlefield: the match
        frames(90)
        check("the match is Tennis, at deuce: no stock in the HUD",
              c.screen == "versus" and c.game_mode.ident == "tennis" and
              c.game_mode.lead == 0 and stocks() == (0, 0) and
              c.game_mode.status(c.sides()) == "Deuce", str(stocks()))
        shot("deuce")

        ko(1)
        check("you take a stock: advantage you, one stock in your HUD",
              c.game_mode.lead == 1 and stocks() == (1, 0) and
              c.game_mode.status(c.sides()).startswith("Advantage Fox"),
              "%d %s" % (c.game_mode.lead, stocks()))
        frames(30)
        shot("advantage-you")
        ko(0)
        check("they take one back: deuce, your stock gone",
              c.game_mode.lead == 0 and stocks() == (0, 0),
              "%d %s" % (c.game_mode.lead, stocks()))
        frames(6)
        shot("deuce-again")
        ko(0)
        check("they take another: advantage them, a stock in theirs",
              c.game_mode.lead == -1 and stocks() == (0, 1),
              "%d %s" % (c.game_mode.lead, stocks()))
        frames(400)
        check("the score holds through both coming back",
              stocks() == (0, 1) and c.screen == "versus", str(stocks()))
        shot("advantage-them")
        ko(1)
        check("you take one back: deuce", c.game_mode.lead == 0 and
              stocks() == (0, 0), "%d %s" % (c.game_mode.lead, stocks()))
        ko(1)
        check("and another: advantage you", c.game_mode.lead == 1 and
              stocks() == (1, 0), "%d %s" % (c.game_mode.lead, stocks()))
        ko(1)
        check("the winning stock shows in the HUD first",
              c.screen == "versus" and stocks() == (2, 0), str(stocks()))
        frames(client.Client.GAME_SHOWN)
        check("two ahead wins: the game stops, the result over it",
              c.screen == "vover" and c.game_mode.winner == 0 and
              stocks() == (2, 0), "%s %s" % (c.screen, stocks()))
        frames(20)
        shot("game")
        tap("x", after=20)
        frames(60)
        check("A plays it again from deuce",
              c.screen == "versus" and c.game_mode.lead == 0 and
              c.game_mode.winner is None and stocks() == (0, 0),
              "%s %s" % (c.screen, stocks()))
        ko(0)
        ko(0)
        frames(client.Client.GAME_SHOWN)
        check("they win by two the same way", c.screen == "vover" and
              c.game_mode.winner == 1, c.screen)
        tap("z", after=10)
        check("B goes back to the stages", c.screen == "stages", c.screen)
    finally:
        if w is not None:
            w.close()

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
