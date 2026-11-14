"""Fullscreen in the native client: the picture keeps its shape, centred,
in a window of another shape; F11 and the remembered choice.

    python tests/client/fullscreen.py [--shots DIR]

Going fullscreen gives the window the size of the screen. On a screen that
is not 16:9 (an ultrawide one) the client's 16:9 picture must stay 16:9 in
the middle with black at the sides. That part is checked here by giving
the window those shapes on a virtual display and looking at pictures: the
main menu must be the same picture, moved to the middle, and in a match
the game must sit at the left of that frame.

What cannot be checked here: the switch to fullscreen itself. It is the
window manager that does it and a virtual display has none; this checks
that the request is made (by command and by F11), remembered, and does no
harm.
"""
import argparse
import os
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))

import client  # noqa: E402
import window  # noqa: E402
import pausekeys  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def mean(path, crop):
    """How bright a part of a picture is, 0 (black) to 1."""
    out = subprocess.run(["magick", path, "-crop", crop, "+repage",
                          "-colorspace", "Gray", "-format", "%[fx:mean]",
                          "info:"], capture_output=True, text=True).stdout
    return float(out or -1)


def differ(a, b, crop):
    """How far part `crop` of picture b is from picture a, 0 to 1."""
    part = b + ".part.png"
    subprocess.run(["magick", b, "-crop", crop, "+repage", part], check=True)
    r = subprocess.run(["magick", "compare", "-metric", "RMSE", a, part,
                        "null:"], capture_output=True, text=True)
    os.unlink(part)
    try:
        return float(r.stderr.split("(")[1].split(")")[0])
    except (IndexError, ValueError):
        return 1.0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    args = ap.parse_args()
    shots = args.shots or tempfile.mkdtemp(prefix="melee-shots-")
    state = tempfile.mkdtemp(prefix="melee-state-")
    kept = os.path.join(state, "tmp", "melee-window-xdg", "aurora",
                        "fullscreen")
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
        return str(w.shot(os.path.join(shots, name + ".png")))

    try:
        # a screen with room for a wider and for a taller window
        w = window.Window(window=(1280, 720), size=(1800, 960),
                          state_dir=state)
        w.step(30)
        c = client.Client(w, source="keyboard",
                          out=tempfile.mkdtemp(prefix="melee-ui-"),
                          save=os.path.join(tempfile.mkdtemp(), "s.json"))
        w.pace(False)
        frames(8)
        at = w.where()
        check("a 1280 by 720 window: the frame is the window, not "
              "fullscreen", at["size"] == [1280, 720] and
              at["frame"] == [0, 0, 1280, 720] and at["asked"] == 0,
              str(at))
        usual = shot("menu")

        # ---- a wider window: what fullscreen is on an ultrawide screen -------
        w.resize(1720, 720)
        frames(12)
        at = w.where()
        check("made 1720 wide: the frame is 1280 by 720 in the middle",
              at["size"] == [1720, 720] and
              at["frame"] == [220, 0, 1280, 720], str(at))
        wide = shot("menu-wide")
        sides = (mean(wide, "220x720+0+0"), mean(wide, "220x720+1500+0"))
        check("black at both sides", max(sides) < 0.004,
              "%.3f and %.3f" % sides)
        d = differ(usual, wide, "1280x720+220+0")
        check("and between them the same menu as before", d < 0.01,
              "differs by %.4f" % d)

        # ---- a taller window: bars above and below ----------------------------
        w.resize(1280, 900)
        frames(12)
        at = w.where()
        check("made 900 high: the frame is 90 down",
              at["frame"] == [0, 90, 1280, 720], str(at))
        tall = shot("menu-tall")
        bars = (mean(tall, "1280x90+0+0"), mean(tall, "1280x90+0+810"))
        d = differ(usual, tall, "1280x720+0+90")
        check("black above and below, the same menu between",
              max(bars) < 0.004 and d < 0.01,
              "bars %.3f %.3f, differs by %.4f" % (bars + (d,)))
        w.resize(1280, 720)
        frames(12)
        d = differ(usual, shot("menu-again"), "1280x720+0+0")
        check("and back to 1280 by 720: as it began", d < 0.01,
              "differs by %.4f" % d)

        # ---- the game's picture in the frame ----------------------------------
        w.resize(1720, 720)
        frames(12)
        tap("Right")
        tap("x")
        tap("x")
        tap("x", after=30)
        frames(120)
        check("a match in the Lab", c.screen == "versus", c.screen)
        match = shot("match-wide")
        sides = (mean(match, "220x720+0+0"), mean(match, "220x720+1500+0"))
        game = mean(match, "960x720+220+0")
        rail = mean(match, "320x720+1180+0")
        check("in a match too: black at the sides, the game at the left "
              "of the frame and the column at its right",
              max(sides) < 0.004 and game > 0.02 and rail > 0.02,
              "sides %.3f %.3f, game %.3f, column %.3f" % (
                  sides + (game, rail)))
        pausekeys.leave(c, w, "main", frames)
        tap("Left")
        check("back at the main menu", c.screen == "main" and
              c.focus == "train", "%s %s" % (c.screen, c.focus))
        w.resize(1280, 720)
        frames(12)

        # ---- asking for fullscreen ---------------------------------------------
        at = w.fullscreen(True)
        frames(10)
        check("fullscreen by command is asked for and remembered",
              at["asked"] == 1 and open(kept).read().strip() == "1",
              str(at))
        at = w.fullscreen(False)
        frames(10)
        check("and off again", at["asked"] == 0 and
              open(kept).read().strip() == "0", str(at))
        tap("F11", after=10)
        at = w.where()
        check("F11 asks for it", at["asked"] == 1 and
              open(kept).read().strip() == "1", str(at))
        frames(30)
        check("the game goes on", c.screen == "main")
        bad = [line.strip()[:160] for line in w.log
               if "aurora" in line and ("warn" in line or "error" in line)]
        check("nothing warned", not bad, "; ".join(bad[:3]))
        w.close()
        w = c = None

        # ---- the next start ----------------------------------------------------
        w = window.Window(window=(1280, 720), state_dir=state,
                          fullscreen="remembered")
        w.step(5)
        check("the next start asks for fullscreen by itself",
              w.where()["asked"] == 1)
        w.close()
        w = window.Window(window=(1280, 720), state_dir=state,
                          fullscreen=False)
        w.step(5)
        check("unless told to start in a window", w.where()["asked"] == 0)
    finally:
        if w is not None:
            w.close()
        left = window.leftovers()
        check("nothing left running", not left, str(left))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
