"""Closing the native client's window, checked off screen.

    python tests/client/close.py

The owner, 2026-11-13: closing the window left it "not responding"; the
game ran exit() from its frame loop and the graphics libraries' teardown
never returned. Here: a short hop drill with two tries, then the window is
asked to close as a desktop does (WM_DELETE_WINDOW): the game has to be
gone within a second, having said why, and the two tries have to be in the
save.
"""
import os
import sys
import tempfile
import time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))

import client  # noqa: E402
import courses  # noqa: E402
import window  # noqa: E402
from native import NativeError  # noqa: E402

DRILL = "universal-short-hop"
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def main():
    save = os.path.join(tempfile.mkdtemp(prefix="melee-client-"),
                        "client.json")
    # (the tutorial, which opens a drill the first time, is not this
    # test's subject: tests/client/short_hop.py)
    seen = courses.Progress(save)
    seen.drill(DRILL).update(tutorial=True, part=2)   # its last part
    seen.save()
    w = c = None
    try:
        w = window.Window(window=(1280, 720), timeout=20)
        w.step(30)
        c = client.Client(w, source="keyboard", save=save,
                          out=tempfile.mkdtemp(prefix="melee-ui-"))
        w.pace(False)
        for _ in range(6):
            c.frame()
        for key in ("x", "x", "x"):            # Fox, his hub, Tech
            w.key(key)
            c.frame()
            c.frame()
            w.key(key, False)
            for _ in range(6):
                c.frame()
        check("in Fox's Tech drills, on the short hop",
              c.screen == "list" and c.drills()[c.row[c.part]]["id"] == DRILL)

        state = dict(tries=0, press=0, idle=0, closed=None)

        def person(game, frame):
            if state["press"]:
                state["press"] -= 1
                if state["press"] == 0:
                    game.key("v", False)
                return
            if state["tries"] == 0 and frame == 0:
                game.key("x", False)
            if len(c.results_now()) >= 2 and state["closed"] is None:
                state["closed"] = time.time()
                game.close_window()
                return
            f = game.fighter(0)
            state["idle"] = state["idle"] + 1 if f.state == 14 else 0
            if state["idle"] >= 8 and state["tries"] == len(c.results_now()):
                game.key("v")
                state["press"] = 2
                state["tries"] += 1
                state["idle"] = 0

        c.person = person
        w.key("x")
        stopped = None
        try:
            for _ in range(20):
                c.frame()
        except NativeError as e:
            stopped = str(e)
        gone = None
        if state["closed"] is not None:
            for _ in range(20):
                if w.p.poll() is not None:
                    gone = time.time() - state["closed"]
                    break
                time.sleep(0.05)
        check("closing the window ends the game at once",
              gone is not None and gone < 1.0 and w.p.poll() == 0,
              "%s s, exit %s" % (None if gone is None else round(gone, 2),
                                 w.p.poll()))
        check("and says why", "the window was closed" in "".join(w.log) and
              stopped is not None)
        saved = courses.Progress(save).drill(DRILL)
        check("the two tries are in the save", saved.get("tries") == 2,
              str(saved))
    finally:
        if w is not None:
            w.close()
        left = window.leftovers()
        check("nothing left running", not left, str(left))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
