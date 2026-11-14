"""Two native clients playing each other online, checked off screen.

    python tests/client/online.py [--shots DIR]

Two clients, each in its own window on its own virtual display, each driven
from its own thread as a person would: Versus, a character (Fox, Marth),
Versus, Online, a character (Fox, Marth); each copies its code and the
other pastes it (the codes go through each display's clipboard); they meet
(LAN addresses: MELEE_ONLINE_NO_STUN, nothing sent outside), start the same
match and play it with rollback netcode (src/host/net.c) for ten seconds,
each pressing its own keys. Checked: both connect and play the agreed
match, each sees its own character on its own port, the session's desync
checks all agree, rollbacks happened and stayed shallow; then one leaves
through its pause menu and the other is told and goes back.
"""
import argparse
import os
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))

os.environ["MELEE_ONLINE_NO_STUN"] = "1"

import client  # noqa: E402
import window  # noqa: E402
from pausekeys import Chooser  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


class Side:
    def __init__(self, name, char, port):
        self.name, self.char, self.port = name, char, port
        tmp = tempfile.mkdtemp(prefix="melee-online-")
        self.w = window.Window(window=(1280, 720))
        self.w.step(30)
        self.c = client.Client(self.w, source="keyboard",
                               save=os.path.join(tmp, "client.json"),
                               out=os.path.join(tmp, "ui"))
        self.c.progress.data["nickname"] = name
        self.c.progress.data["online_port"] = port
        self.w.pace(False)
        self.error = None
        self.seen = {}

    def frames(self, n):
        for _ in range(n):
            self.c.frame()

    def tap(self, key, after=6):
        self.w.key(key)
        self.frames(2)
        self.w.key(key, False)
        self.frames(after)

    def to_online(self):
        c = self.c
        self.frames(6)
        self.tap("Left")                            # to Versus
        self.tap("x")                               # Local or Online
        self.tap("Right")
        self.tap("x")                               # Online: characters
        for _ in range(40):
            if c.roster[c.at]["id"] == self.char:
                break
            self.tap("Right", after=2)
            if c.roster[c.at]["id"] != self.char and c.at % 9 == 8:
                self.tap("Down", after=2)
        self.tap("x", after=10)                     # the online screen
        return c.screen == "online" and c.lobby is not None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    args = ap.parse_args()
    a = b = None
    try:
        a = Side("Alpha", "fox", 47711)
        b = Side("Beta", "marth", 47712)
        ok_a, ok_b = a.to_online(), b.to_online()
        check("both reach the online screen with a code", ok_a and ok_b,
              "%s %s" % (a.c.screen, b.c.screen))
        if not (ok_a and ok_b):
            return 1
        # the code is drawn: light text on its dark ticket, the first line
        # of groups (once it was set in a typeface the client does not
        # load, and drew as nothing)
        shot = os.path.join(tempfile.mkdtemp(), "online.png")
        a.w.shot(shot)
        bright = subprocess.run(
            ["magick", shot, "-crop", "380x40+88+192", "+repage",
             "-colorspace", "Gray", "-threshold", "70%", "-format",
             "%[fx:mean]", "info:"], capture_output=True,
            text=True).stdout
        check("the code is drawn on the online screen",
              float(bright or 0) > 0.05, "light share %s" % bright)
        # each pastes the other's code. The virtual displays' clipboards
        # do not keep SDL's text (checked: SDL_HasClipboardText is false
        # right after setting it), so the clipboard hands each the other's
        # code; on a desktop the client uses SDL's or xclip's.
        a.c.read_clipboard = lambda: b.c.lobby.code
        b.c.read_clipboard = lambda: a.c.lobby.code

        def play(side, keys):
            try:
                side.tap("Down")                    # "Paste a friend's code"
                side.w.key("x")
                side.frames(2)
                side.w.key("x", False)
                for _ in range(600):                # the meeting, the load
                    side.c.frame()
                    if side.c.screen == "online_match":
                        break
                side.seen["screen"] = side.c.screen
                if side.c.screen != "online_match":
                    return
                side.seen["start"] = time.time()
                t0 = time.time()
                k = 0
                while time.time() - t0 < 10:
                    key = keys[(k // 20) % len(keys)]
                    if k % 20 == 0:
                        side.w.key(key)
                    if k % 20 == 10:
                        side.w.key(key, False)
                    side.c.frame()
                    k += 1
                side.seen["stats"] = side.w.net("stats")
                side.seen["fighters"] = [side.w.fighter(p).ckind
                                         for p in (0, 1)]
            except Exception as e:
                side.error = e

        ta = threading.Thread(target=play, args=(a, ["Right", "c", "x"]))
        tb = threading.Thread(target=play, args=(b, ["Left", "z", "s"]))
        ta.start()
        tb.start()
        ta.join()
        tb.join()
        check("both meet and start the online match",
              a.seen.get("screen") == "online_match" and
              b.seen.get("screen") == "online_match",
              "%s %s %s %s; %r / %r" % (
                  a.seen.get("screen"), b.seen.get("screen"), a.error,
                  b.error, getattr(a.c, "online_status", None),
                  getattr(b.c, "online_status", None)))
        sa, sb = a.seen.get("stats"), b.seen.get("stats")
        if sa and sb:
            check("the same match on both sides: the same characters on the "
                  "same ports",
                  a.seen["fighters"] == b.seen["fighters"],
                  "%s / %s" % (a.seen["fighters"], b.seen["fighters"]))
            # two software-drawn windows: under 60 frames a second here
            check("ten seconds played on both sides",
                  sa["frame"] > 300 and sb["frame"] > 300,
                  "%d and %d frames" % (sa["frame"], sb["frame"]))
            check("no desync in %d checks" % (sa["checks"] + sb["checks"]),
                  not sa["desync"] and not sb["desync"] and
                  sa["checks"] + sb["checks"] >= 10)
            check("rollbacks stayed within 8 frames",
                  max(sa["max_rollback"], sb["max_rollback"]) <= 8,
                  "%d rollbacks and %d, deepest %d" % (
                      sa["rollbacks"], sb["rollbacks"],
                      max(sa["max_rollback"], sb["max_rollback"])))
            if args.shots:
                a.w.shot(os.path.join(args.shots, "online-a.png"))
                b.w.shot(os.path.join(args.shots, "online-b.png"))
            # Alpha leaves through its pause menu; Beta is told
            out = {}

            def leave():
                ch = Chooser(a.c, "back")
                # inside the pause menu the client calls its person each
                # frame (as in a drill): the choosing happens there
                a.c.person = lambda game, frame: ch(game)
                # (frames are unpaced: under load the key presses and the
                # menu take more of them, so the budget is generous)
                for _ in range(900):
                    ch(a.w)
                    a.c.frame()
                    if a.c.screen == "online":
                        break
                a.c.person = None
                out["a"] = a.c.screen

            def wait():
                for _ in range(1200):
                    b.c.frame()
                    if b.c.screen == "online":
                        break
                out["b"] = b.c.screen
            t1 = threading.Thread(target=leave)
            t2 = threading.Thread(target=wait)
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            check("leaving through the pause menu goes back to the online "
                  "screen, and the friend is told and goes back too",
                  out.get("a") == "online" and out.get("b") == "online",
                  str(out))
            check("each saved the other as a friend, by their nickname",
                  [f["name"] for f in a.c.progress.data.get("friends", [])]
                  == ["Beta"] and [f["name"] for f in
                                   b.c.progress.data.get("friends", [])] ==
                  ["Alpha"])
    finally:
        for side in (a, b):
            if side is not None:
                side.c.close_lobby()
                side.w.close()
        left = window.leftovers()
        check("nothing left running", not left, str(left))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
