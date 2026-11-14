"""Settings in the native client, checked on a virtual display with keys
pressed there: Settings from the main menu, Controls in it, and what each
of its rows does to the game process.

    python tests/client/settings_menu.py [--shots DIR]

Input delay: 2 frames unless changed (Slippi's default), changed with the
stick, given to the game at once and kept in the progress file, so that
the next client starts with it. Rumble: a port switched off and on, and
"Feel it" (the keyboard has no motor, and no adapter is opened: the live
port here is the keyboard). UCF: off and on. The progress file is a
temporary one, never the player's. --shots saves a picture of each screen
(under build/shots/ they stay out of the repository).
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
import window  # noqa: E402

os.environ["MELEE_ONLINE_NO_STUN"] = "1"   # no STUN server is asked

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for a picture of each screen")
    args = ap.parse_args()
    w = None
    save = os.path.join(tempfile.mkdtemp(prefix="melee-save-"), "client.json")
    out = tempfile.mkdtemp(prefix="melee-ui-")

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
        c = client.Client(w, source="keyboard", save=save, out=out)
        w.pace(False)
        frames(10)
        check("a new player starts with Slippi's 2 frames of input delay",
              c.settings["delay"] == 2 and w.delay() == 2,
              "client %d, game %d" % (c.settings["delay"], w.delay()))
        check("and rumble on for every port, UCF on",
              w.rumble()["allowed"] == [1, 1, 1, 1] and w.ucf())

        tap("Down")
        check("Settings is the main menu's panel under Train",
              c.focus == "settings")
        tap("x")
        check("A on it opens Settings, Controls in focus",
              c.screen == "settings" and c.sfocus == "scontrols")
        shot("settings")
        seen = []
        for key in ("Right", "Down", "Right", "Up", "Left"):
            tap(key)
            seen.append(c.sfocus)
        check("the focus moves over its panels",
              seen == ["sonline", "ssound", "sdisplay", "sonline",
                       "scontrols"], " ".join(seen))
        tap("x")
        check("A on Controls opens it on Input delay",
              c.screen == "controls" and c.ctl_at == 0)
        shot("controls-delay")

        tap("Right")
        check("right: one frame more, given to the game at once",
              c.settings["delay"] == 3 and w.delay() == 3,
              "client %d, game %d" % (c.settings["delay"], w.delay()))
        for _ in range(4):
            tap("Left")
        check("left: down to Off, and no further",
              c.settings["delay"] == 0 and w.delay() == 0)
        for _ in range(12):
            tap("Right", after=3)
        check("right: up to 9 frames, and no further",
              c.settings["delay"] == 9 and w.delay() == 9)
        for _ in range(5):
            tap("Left", after=3)
        saved = json.load(open(save))["settings"]
        check("the delay is kept in the progress file",
              saved["delay"] == 4, str(saved))

        tap("Down")
        check("down: Rumble, on the player's port",
              c.screen == "controls" and c.CTL_ROWS[c.ctl_at] == "rumble" and
              c.rport == 0)
        shot("controls-rumble")
        tap("x")
        check("A switches the port's rumble off",
              c.settings["rumble"][0] is False and
              w.rumble()["allowed"][0] == 0)
        tap("x")
        check("and on again", w.rumble()["allowed"][0] == 1)
        tap("Right")
        tap("x")
        check("right: the next port's card, switched on its own",
              c.rport == 1 and w.rumble()["allowed"] == [1, 0, 1, 1],
              str(w.rumble()["allowed"]))
        tap("x")
        tap("Left")
        tap("v")                    # X: feel it
        r = w.rumble()
        check("Feel it on the keyboard: no motor, nothing runs",
              r["running"] == [0, 0, 0, 0], str(r))
        check("no GameCube adapter was opened or told anything",
              r["adapter"] == [-1, -1, -1, -1], str(r))

        tap("Down")
        shot("controls-ucf")
        tap("Right")
        check("UCF: off", c.settings["ucf"] is False and not w.ucf())
        tap("Right")
        check("and on", c.settings["ucf"] is True and w.ucf())
        tap("Down")
        check("Button layouts: there, and said to be next",
              c.CTL_ROWS[c.ctl_at] == "layouts")
        shot("controls-layouts")
        tap("Down")
        check("down from the last row comes round to the first",
              c.ctl_at == 0)

        tap("z")
        check("B goes back to Settings", c.screen == "settings")

        # Sound
        tap("Right")
        tap("Down")
        tap("x")
        check("Sound opens on Music",
              c.screen == "sub" and c.sub == "ssound" and c.sub_at == 0)
        shot("sound")
        tap("Left")
        check("left: the music 10 quieter, given to the game at once",
              c.settings["music"] == 90 and w.volume() == (90, 100),
              str(w.volume()))
        tap("Down")
        tap("Left")
        tap("Left")
        check("the effects' volume is kept for matches: the menus' is on now",
              c.settings["effects"] == 80 and w.volume() == (90, 100),
              str(w.volume()))
        tap("Down")
        tap("Left")
        check("the menus' sounds: 10 quieter, at once",
              c.settings["menus"] == 90 and w.volume() == (90, 90),
              str(w.volume()))
        tap("z")

        # Display
        tap("Right")
        tap("x")
        check("Display opens on Window",
              c.screen == "sub" and c.sub == "sdisplay" and c.sub_at == 0)
        shot("display")
        was = c.fullscreen_now()
        tap("Right")
        check("right: fullscreen asked for", c.fullscreen_now() != was)
        tap("Right")
        check("and back", c.fullscreen_now() == was)
        tap("Down")
        tap("Right", after=20)
        check("Window size: the next size, given to the window",
              c.settings["size"] == [1600, 900] and
              w.where()["size"] == [1600, 900], str(w.where()["size"]))
        tap("Left", after=20)
        check("and back", w.where()["size"] == [1280, 720],
              str(w.where()["size"]))
        tap("Down")
        tap("Right")
        check("Sidebar: hidden", c.column_hidden and
              not c.settings["sidebar"])
        shot("display-hidden")
        tap("Right")
        check("and shown", not c.column_hidden and c.settings["sidebar"])
        tap("Down")
        check("Input display: off unless chosen",
              c.SUB["sdisplay"][2][c.sub_at] == "inputs" and
              c.settings["inputs"] == "off")
        tap("Right")
        tap("Right")
        check("right: you, then the opponent",
              c.settings["inputs"] == "opponent")
        tap("Left")
        tap("Left")
        check("left: back to off", c.settings["inputs"] == "off")
        tap("Down")
        check("Coach: after 3 misses unless changed",
              c.SUB["sdisplay"][2][c.sub_at] == "coach" and
              c.settings["coach"] == 3)
        tap("Right")
        check("right: after 4", c.settings["coach"] == 4)
        for _ in range(3):
            tap("Left")
        check("left past 2: off", c.settings["coach"] == 0)
        tap("Right")
        tap("Right")
        check("and back to 3", c.settings["coach"] == 3)
        tap("z")

        # Online
        tap("Up")
        tap("x")
        check("Online opens on Nickname",
              c.screen == "sub" and c.sub == "sonline" and c.sub_at == 0)
        # (a virtual display's clipboard does not keep text reliably:
        # tests/client/online.py hands the client its text the same way)
        c.read_clipboard = lambda: "Tester"
        tap("v")                    # X: paste
        check("X pastes the clipboard as the nickname",
              c.nickname() == "Tester", c.nickname())
        shot("online")
        tap("Down")
        tap("Right")
        check("the code's port: one up", c.online_port() == 47701)
        tap("Left")
        tap("Down")
        shot("online-friends")
        tap("Down")
        tap("x")
        check("Router: not checked in a test (no network)",
              c.router[0] == "Not checked", str(c.router))
        tap("z")
        tap("z")
        check("and B again to the main menu", c.screen == "main")
        saved = json.load(open(save))
        check("all of it kept in the progress file",
              saved["settings"]["music"] == 90 and
              saved["settings"]["effects"] == 80 and
              saved["nickname"] == "Tester", str(saved["settings"]))

        bad = [line.strip()[:160] for line in w.log
               if "aurora" in line and ("warn" in line or "error" in line)]
        check("the interface raised no warnings", not bad,
              "; ".join(bad[:3]))

        # a client started again starts with what was kept
        w.delay(0)
        c = client.Client(w, source="keyboard", save=save, out=out)
        frames(5)
        check("a client started again gives the game the kept delay",
              w.delay() == 4 and c.settings["delay"] == 4,
              "game %d" % w.delay())
        check("and the kept volumes", w.volume() == (90, 90),
              str(w.volume()))
    finally:
        if w is not None:
            w.close()
        left = window.leftovers()
        check("nothing left running", not left, str(left))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
