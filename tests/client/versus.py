"""Versus and the Lab in the native client, with a trained slippi-ai model
on the other side, checked without a person or a desktop.

    python tests/client/versus.py [--shots DIR]

Versus: Fox, the opponent screen (who plays the opponent), the stage
select, a match against Falco played by the model trained for that
pairing: it has to load, answer nearly every frame without the game
waiting for it, and play (move about, change state). Then the same Falco
played by the game's CPU, on the stage chosen. The Lab, in Train: an
opponent nobody plays, its damage set and both put back from the D-pad. Needs a slippi-ai checkout
with its models (~/Games/Melee/slippi-ai); without one the model's part is
skipped and says so.
"""
import argparse
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))

import client  # noqa: E402
import opponents  # noqa: E402
import window  # noqa: E402
import pausekeys  # noqa: E402

WAIT = 14
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    args = ap.parse_args()
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

    def leave():
        pausekeys.leave(c, w, "opp", frames)

    try:
        w = window.Window(window=(1280, 720))
        w.step(30)
        c = client.Client(w, source="keyboard",
                          out=tempfile.mkdtemp(prefix="melee-ui-"),
                          save=os.path.join(tempfile.mkdtemp(), "s.json"))
        w.pace(False)
        frames(6)
        tap("Left")                 # Versus, the main menu's big panel
        tap("x")
        check("Versus opens on Local or Online", c.screen == "vmenu" and
              c.vfocus == "vlocal", c.screen)
        shot("versus-menu")
        tap("x")
        tap("x")
        check("Local: your character, then the opponent screen",
              c.mode == "versus" and c.screen == "opp" and
              c.me["id"] == "fox")
        for key in ("Up", "Left", "Left"):
            tap(key)
        players = c.players()
        check("the opponent can be played by the game's CPU or nobody",
              c.roster[c.opp_at]["id"] == "falco" and
              [p[0] for p in players[-2:]] == [client.CPU, client.NOBODY])
        shot("opponent")
        tap("x")
        check("A on the opponent screen opens the stage select, "
              "Battlefield first", c.screen == "stages" and
              client.STAGE_ORDER[c.stage_at] == "battlefield")
        shot("stages")
        tap("Right")
        tap("Down")
        check("the stick moves over the stages, three to a row",
              client.STAGE_ORDER[c.stage_at] == "fountain-of-dreams",
              client.STAGE_ORDER[c.stage_at])
        tap("Up")
        tap("Left")
        tap("z")
        check("B goes back to the opponent", c.screen == "opp")

        if opponents.available() and len(players) > 2:
            names = [p[1] for p in players[:-2]]
            check("the models by name and difficulty, the ranks first, "
                  "then the specialists for this pairing only",
                  names[:5] == ["Gold", "Platinum", "Diamond", "Master",
                                "Grandmaster"] and
                  "Fox Specialist" in names and
                  all(n == "Fox Specialist" for n in names
                      if n.endswith("Specialist")) and
                  not any("_" in n for n in names), ", ".join(names))
            tap("x")
            tap("x", after=10)
            w.pace(True)
            for _ in range(900):          # the model loads beside the match
                c.frame()
                if c.bot is not None and c.bot.ready() is not None:
                    break
            check("the match starts and the model loads beside it",
                  c.screen == "versus" and c.bot is not None and
                  c.bot.ready() is True, c.bot.error if c.bot else "")
            seen, xs = set(), []
            for f in range(420):
                c.frame()
                g = w.fighter(1)
                seen.add(g.state)
                xs.append(g.pos[0])
                if f == 300:
                    shot("versus")
            bot = c.bot
            check("it answers nearly every frame",
                  bot.answered >= 0.9 * bot.asked and bot.asked >= 400,
                  "%d of %d" % (bot.answered, bot.asked))
            check("and plays: it moves and does different things",
                  len(seen) >= 6 and max(xs) - min(xs) > 20,
                  "%d states, moved over %.0f" % (len(seen),
                                                  max(xs) - min(xs)))
            w.pace(False)
            leave()
            check("holding START comes back, and the model is let go",
                  c.screen == "opp" and c.bot is None and
                  bot.p.poll() is not None)
        else:
            print("      (no slippi-ai with models here: the trained "
                  "opponent was not tried)")

        # ---- the game's own CPU ----------------------------------------------
        for _ in range(len(c.players())):
            if c.players()[c.who][0] == client.CPU:
                break
            tap("v", after=2)
        tap("x")
        for key in ("Down", "Right", "Right"):
            tap(key)
        tap("x", after=20)
        seen = set()
        for _ in range(360):
            c.frame()
            seen.add(w.fighter(1).state)
        check("against the game's CPU: it plays, with no model running",
              c.screen == "versus" and c.bot is None and len(seen) >= 3,
              "%d states" % len(seen))
        check("on the stage chosen", w.match_info["stage"] ==
              "pokemon-stadium", w.match_info["stage"])
        leave()

        # ---- the client's pause menu ---------------------------------------------
        # START is the client's: its pause menu over the frozen match, never
        # the game's own pause (whose L+R+A+Start once took the native game
        # into its memory card screen: the owner, 2026-11-13).
        for _ in range(len(c.players())):
            if c.players()[c.who][0] == client.NOBODY:
                break
            tap("v", after=2)
        tap("x")
        tap("x", after=20)
        frames(60)
        before = w.state().get("ended", 0)
        seen = dict(open=False, still=None)
        resume = pausekeys.Chooser(c, "resume")
        x0 = w.fighter(0).pos[0]

        def during(game, frame):
            if c.pause_open:
                seen["open"] = True
                game.key("Right")            # a frozen match does not move
                seen["still"] = abs(game.fighter(0).pos[0] - x0) < 0.01
                game.key("Right", False)
            resume(game)

        c.person = during
        for _ in range(60):
            if resume.done:
                break
            if not c.pause_open:
                resume(w)
            frames(1)
        c.person = None
        check("START opens the client's pause menu, the match frozen "
              "under it", seen["open"] and seen["still"] is True)
        w.key("Right")
        frames(20)
        w.key("Right", False)
        check("Resume: the match goes on (not the game's own pause)",
              abs(w.fighter(0).pos[0] - x0) > 5,
              "moved %.1f" % abs(w.fighter(0).pos[0] - x0))
        leave()
        st = w.state()
        check("Back to the opponent in the pause menu", c.screen == "opp" and
              st.get("ended") == before, "%s, ended %s" % (
                  c.screen, st.get("ended")))

        # ---- the Lab ---------------------------------------------------------
        tap("z")
        tap("z")
        check("B from the character select goes back to Local or Online",
              c.screen == "vmenu", c.screen)
        tap("z")
        tap("Right")
        check("back at the main menu, on Train",
              c.screen == "main" and c.focus == "train", c.focus)
        tap("x")
        tap("x")
        tap("Down")
        check("the Lab is in Train, in Fox's course hub",
              c.screen == "hub" and c.hub_at == "lab", c.hub_at)
        tap("x")
        check("in the Lab nobody plays the opponent unless asked",
              c.mode == "lab" and c.screen == "opp" and
              c.players()[c.who][0] == client.NOBODY)
        tap("x")
        tap("x", after=20)
        frames(200)
        other = w.fighter(1)
        check("it stands still", c.screen == "versus" and
              other.state == WAIT and c.bot is None,
              "state %d" % other.state)
        tap("h")
        tap("h")
        frames(10)
        check("D-pad right twice: 20 damage on it",
              abs(w.fighter(1).percent - 20) < 0.5,
              "%.0f" % w.fighter(1).percent)
        tap("g")
        frames(10)
        a, b = w.fighter(0), w.fighter(1)
        check("D-pad down puts both back, the damage kept",
              abs(a.pos[0] + 20) < 1 and abs(b.pos[0] - 20) < 1 and
              abs(b.percent - 20) < 0.5,
              "%.0f and %.0f, %.0f%%" % (a.pos[0], b.pos[0], b.percent))
        shot("lab")
        leave()
        check("and out again", c.screen == "opp")
        bad = [line.strip()[:160] for line in w.log
               if "aurora" in line and ("warn" in line or "error" in line)]
        check("the interface raised no warnings", not bad,
              "; ".join(bad[:3]))
    finally:
        if c is not None and c.bot is not None:
            c.bot.close()
        if w is not None:
            w.close()
        left = window.leftovers()
        check("nothing left running", not left, str(left))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
