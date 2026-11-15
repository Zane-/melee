"""Versus's game modes online: two native clients, checked off screen.

    python tests/client/online_modes.py [--shots DIR]

Two clients on their own virtual displays (as tests/client/online.py),
each driven from its own thread. First Alpha chooses Tug of War and Beta
Unlimited: they hear each other, and each is told the other chose another
mode. Then Beta chooses Tug of War too (win by 2): they meet and play it
with rollback netcode, Alpha's Fox standing, Beta's Marth walking off the
stage's left edge again and again (KOs made by the players' own inputs,
the same in both games: a command into one game would put the two apart).
Each fall pulls the rope toward Fox; at two the game ends the match itself
in both games (src/host/rules.c: GAME!, the same frame on both sides),
and both show the results, Fox winning. Checked: the rope's score the same
on both sides, no desync, the results on both, back to the online screen.
The owner, 2026-11-14: "can you ensure all game modes work with online
play as well?".
"""
import argparse
import os
import sys
import tempfile
import threading
import time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))

os.environ["MELEE_ONLINE_NO_STUN"] = "1"

import client  # noqa: E402
import modes  # noqa: E402
import window  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""), flush=True)


class Side:
    def __init__(self, name, char, port):
        self.name, self.char = name, char
        tmp = tempfile.mkdtemp(prefix="melee-online-modes-")
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

    def choose_mode(self, ident):
        """On the mode select: the stick to `ident`, A, and A through its
        options (as they are kept)."""
        c = self.c
        want = [m.ident for m in modes.MODES].index(ident)
        for _ in range(len(modes.MODES) * 2):
            if c.mode_at == want:
                break
            self.tap("Right" if c.mode_at < want else "Left")
        self.tap("x")
        if c.screen == "mopts":
            self.tap("x")

    def choose_char(self):
        c = self.c
        for _ in range(40):
            if c.roster[c.at]["id"] == self.char:
                break
            self.tap("Right", after=2)
            if c.roster[c.at]["id"] != self.char and c.at % 9 == 8:
                self.tap("Down", after=2)
        self.tap("x", after=10)                     # the online screen

    def to_online(self, ident):
        self.frames(6)
        self.tap("Left")                            # to Versus
        self.tap("x")                               # Local or Online
        self.tap("Right")
        self.tap("x")                               # Online: the modes
        self.choose_mode(ident)
        self.choose_char()
        return self.c.screen == "online" and self.c.lobby is not None

    def back_to_modes(self):
        for _ in range(4):
            if self.c.screen == "modes":
                return True
            self.tap("z", after=8)
        return self.c.screen == "modes"


def paste(side, budget=900):
    """Paste the friend's code and frames until the match or a word."""
    for _ in range(6):                  # to "Paste a friend's code"
        if side.c.online_rows()[side.c.online_at][0] == "paste":
            break
        side.tap("Down")
    side.w.key("x")
    side.frames(2)
    side.w.key("x", False)
    for _ in range(budget):
        side.c.frame()
        if side.c.screen == "online_match":
            break


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    args = ap.parse_args()
    a = b = None
    try:
        a = Side("Alpha", "fox", 47731)
        b = Side("Beta", "marth", 47732)
        ok = a.to_online("tug-of-war"), b.to_online("unlimited")
        check("both reach the online screen through the mode select",
              all(ok), "%s %s" % (a.c.screen, b.c.screen))
        if not all(ok):
            return 1
        a.c.read_clipboard = lambda: b.c.lobby.code
        b.c.read_clipboard = lambda: a.c.lobby.code
        ta = threading.Thread(target=paste, args=(a,))
        tb = threading.Thread(target=paste, args=(b,))
        ta.start()
        tb.start()
        ta.join()
        tb.join()
        sa = getattr(a.c, "online_status", "")
        sb = getattr(b.c, "online_status", "")
        check("different modes: no match, each told what the other chose",
              a.c.screen == "online" and b.c.screen == "online" and
              "Unlimited" in sa and "Tug of War (Win by 2)" in sb,
              "%r / %r" % (sa, sb))

        # Beta goes back and chooses Tug of War too
        a.c.close_lobby()
        a.tap("z", after=8)                 # Alpha: back to the characters
        a.tap("x", after=10)                # and the online screen again
        ok_b = b.back_to_modes()
        b.choose_mode("tug-of-war")
        b.choose_char()
        check("both on the online screen again, the same mode chosen",
              ok_b and a.c.screen == "online" and b.c.screen == "online" and
              a.c.versus_mode == b.c.versus_mode == "tug-of-war",
              "%s %s" % (a.c.screen, b.c.screen))
        a.c.read_clipboard = lambda: b.c.lobby.code
        b.c.read_clipboard = lambda: a.c.lobby.code

        def play(side, hold):
            try:
                paste(side)
                side.seen["screen"] = side.c.screen
                if side.c.screen != "online_match":
                    return
                if hold:
                    side.w.key(hold)
                t0 = time.time()
                while time.time() - t0 < 90:
                    side.c.frame()
                    m = side.c.game_mode
                    if side.c.screen == "online_match" and m is not None:
                        side.seen["lead"] = m.lead
                    if side.c.screen == "results":
                        break
                if hold:
                    side.w.key(hold, False)
                side.seen["end"] = side.c.screen
                side.seen["stats"] = side.w.net("stats")
            except Exception as e:
                side.error = e

        ta = threading.Thread(target=play, args=(a, None))
        tb = threading.Thread(target=play, args=(b, "Left"))
        ta.start()
        tb.start()
        ta.join()
        tb.join()
        check("both meet and play Tug of War online",
              a.seen.get("screen") == b.seen.get("screen") ==
              "online_match", "%s %s %s %s; %r / %r" % (
                  a.seen.get("screen"), b.seen.get("screen"), a.error,
                  b.error, getattr(a.c, "online_status", None),
                  getattr(b.c, "online_status", None)))
        ma = getattr(a.c, "game_mode", None)
        mb = getattr(b.c, "game_mode", None)
        if ma is None or mb is None:
            return 1
        check("Marth walks off twice: the game ends the match in both, "
              "and both show the results",
              a.seen.get("end") == b.seen.get("end") == "results",
              "%s %s" % (a.seen.get("end"), b.seen.get("end")))
        check("the same score on both sides: Fox two ahead, Fox wins",
              ma.winner is not None and mb.winner is not None and
              ma.winner == mb.winner and ma.lead == mb.lead and
              abs(ma.lead) == 2 and
              a.c.port == ma.winner and b.c.port != mb.winner,
              "A: port %d lead %d winner %s; B: port %d lead %d winner %s"
              % (a.c.port, ma.lead, ma.winner, b.c.port, mb.lead,
                 mb.winner))
        sa, sb = a.seen.get("stats"), b.seen.get("stats")
        check("no desync", sa and sb and not sa["desync"] and
              not sb["desync"], "%s / %s" % (
                  sa and sa["checks"], sb and sb["checks"]))
        if args.shots:
            a.w.shot(os.path.join(args.shots, "online-results-a.png"))
            b.w.shot(os.path.join(args.shots, "online-results-b.png"))
        a.tap("x", after=10)
        b.tap("x", after=10)
        check("A on the results goes back to the online screen, both",
              a.c.screen == "online" and b.c.screen == "online",
              "%s %s" % (a.c.screen, b.c.screen))
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
