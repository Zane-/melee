"""Versus and the Lab in the native client, with a trained slippi-ai model
on the other side, checked without a person or a desktop.

    python tests/client/versus.py [--shots DIR]

Versus: Local's game mode (Unlimited; Tug of War has tests/client/
versus_modes.py), the classic select (Fox; Falco on P2's card, who plays
it; tests/client/versus_select.py has the rest), the stage select, a match
against Falco played by the model trained for that pairing, loaded since
the characters were locked in: it has to answer nearly every frame
without the game waiting for it, and play (move about, change state). Then the same Falco
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vselkeys as vk  # noqa: E402

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
        check("Local: the game mode first (modes.py), Unlimited in focus",
              c.screen == "modes" and c.mode_at == 0, c.screen)
        tap("x", after=10)
        check("Local, Unlimited: the classic select, your card first",
              c.mode == "versus" and c.screen == "vsel" and
              c.vslots[0]["kind"] == "you" and c.vactive == 0, c.screen)
        vk.pick(c, tap, 0, "fox")
        vk.pick(c, tap, 1, "falco")
        check("Fox, and Falco for P2, who can be the game's CPU, a trained "
              "model, a dummy or a second controller",
              [sl["char"]["id"] for sl in c.vslots] == ["fox", "falco"] and
              c.VKINDS[:4] == ("cpu", "model", "dummy", "human"))
        shot("select")
        vk.to_card(c, tap, 1)
        tap("c", after=6)
        page = open(os.path.join(c.out, "vselect.rml")).read()
        check("Y on P2's card: Falco's next costume, its picture on the "
              "card", c.vslots[1]["costume"] == 1 and
              "portrait/falco-1.png" in page, str(c.vslots[1]["costume"]))
        tap("Return", after=10)
        check("START opens the stage select, Battlefield first",
              c.screen == "stages" and c.stage_id() == "battlefield")
        shot("stages")
        tap("Right")
        tap("Down")
        check("the stick moves over the stages, three to a row",
              c.stage_id() == "fountain-of-dreams", c.stage_id())
        tap("Up")
        tap("Left")
        tap("z", after=8)
        check("B goes back to the select", c.screen == "vsel")

        models = c.vmodels(1)
        if opponents.available() and models:
            names = [m[1] for m in models]
            check("the models by name and difficulty, the ranks first, "
                  "then the specialists for this pairing only",
                  names[:5] == ["Gold", "Platinum", "Diamond", "Master",
                                "Grandmaster"] and
                  "Fox Specialist" in names and
                  all(n == "Fox Specialist" for n in names
                      if n.endswith("Specialist")) and
                  not any("_" in n for n in names), ", ".join(names))
            vk.set_kind(c, tap, 1, "model")
            tap("Return", after=10)
            tap("x", after=10)
            w.pace(True)
            bot = c.vbots.get(1)
            for _ in range(900):          # loaded since the select
                c.frame()
                if bot is not None and bot.ready() is not None:
                    break
            check("the match starts, the model loaded since the "
                  "characters were locked in", c.screen == "versus" and
                  bot is not None and bot.ready() is True and
                  c.vplaying.get(1) is bot, bot.error if bot else "")
            seen, xs = set(), []
            for f in range(420):
                c.frame()
                g = w.fighter(1)
                seen.add(g.state)
                xs.append(g.pos[0])
                if f == 300:
                    shot("versus")
            check("it answers nearly every frame",
                  bot.answered >= 0.9 * bot.asked and bot.asked >= 400,
                  "%d of %d" % (bot.answered, bot.asked))
            check("and plays: it moves and does different things",
                  len(seen) >= 6 and max(xs) - min(xs) > 20,
                  "%d states, moved over %.0f" % (len(seen),
                                                  max(xs) - min(xs)))
            w.pace(False)
            leave()
            check("out of the match: the select, the model kept loaded for "
                  "the next one", c.screen == "vsel" and
                  not c.vplaying and bot.p.poll() is None,
                  "%s %s %s area %s" % (c.screen, c.vplaying, bot.p.poll(),
                                        getattr(c, "varea", None)))
        else:
            bot = None
            print("      (no slippi-ai with models here: the trained "
                  "opponent was not tried)")

        # ---- the game's own CPU ----------------------------------------------
        vk.set_kind(c, tap, 1, "cpu")
        tap("Return", after=10)
        for key in ("Down", "Right", "Right"):
            tap(key)
        tap("x", after=20)
        seen = set()
        for _ in range(360):
            c.frame()
            seen.add(w.fighter(1).state)
        check("against the game's CPU: it plays, with no model running",
              c.screen == "versus" and not c.match_bots() and
              len(seen) >= 3, "%d states" % len(seen))
        check("on the stage chosen", w.match_info["stage"] ==
              "pokemon-stadium", w.match_info["stage"])
        check("Falco in the costume chosen for him",
              w.state()["p"][1]["costume"] == 1,
              str(w.state()["p"][1]["costume"]))
        leave()

        # ---- the client's pause menu ---------------------------------------------
        # START is the client's: its pause menu over the frozen match, never
        # the game's own pause (whose L+R+A+Start once took the native game
        # into its memory card screen: the owner, 2026-11-13).
        vk.set_kind(c, tap, 1, "dummy")
        tap("Return", after=10)
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
        check("Characters in the pause menu: back on the select",
              c.screen == "vsel" and st.get("ended") == before, "%s, ended "
              "%s" % (c.screen, st.get("ended")))

        # ---- the Lab ---------------------------------------------------------
        tap("z")
        check("B from the select goes back to the modes",
              c.screen == "modes", c.screen)
        tap("z")
        check("and B again to Local or Online", c.screen == "vmenu",
              c.screen)
        tap("z")
        check("out of Versus: the models loaded for it are let go",
              bot is None or bot.p.poll() is not None)
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
