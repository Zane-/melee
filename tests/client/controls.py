"""The in-drill controls of the native client, checked off screen.

    python tests/client/controls.py [--shots DIR]

From the owner's play session (2026-11-13): START held 3 s puts the column
away (the game's picture in the middle) and back; a START tap opens the
client's pause menu over the frozen match, with the drill's settings (a
setting changed there is in force from the next try); the verdict in
colour (a failure red); D-pad right held 3 s goes to the next drill of the
course. Fox's "Shine out of shield" is the drill: its tutorial, on first
open, skipped with START; the setting its Timing (Lenient to
Frame-perfect); a failure a spot dodge in the shield.
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
import courses  # noqa: E402
import window  # noqa: E402
from pausekeys import Chooser  # noqa: E402

DRILL = "fox-shine-oos"
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def mean(path, crop):
    out = subprocess.run(["magick", path, "-crop", crop, "+repage",
                          "-colorspace", "Gray", "-format", "%[fx:mean]",
                          "info:"], capture_output=True, text=True).stdout
    return float(out or -1)


def colour_count(path, crop, rgb, tol=40):
    """Pixels in `crop` within `tol` of `rgb`."""
    out = subprocess.run(["magick", path, "-crop", crop, "+repage",
                          "txt:-"], capture_output=True, text=True).stdout
    n = 0
    for line in out.splitlines()[1:]:
        try:
            vals = line.split("(")[1].split(")")[0].split(",")
            r, g, b = (int(float(v)) for v in vals[:3])
        except (IndexError, ValueError):
            continue
        if abs(r - rgb[0]) < tol and abs(g - rgb[1]) < tol and \
                abs(b - rgb[2]) < tol:
            n += 1
    return n



def waiting_for(drills):
    """The drills this test plays that are not back yet: the drills were
    wiped 2026-11-14 and are rebuilt one at a time in the drill format
    (docs/ai/drill-format.md); this test moves onto the first rebuilt ones
    it can use."""
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(
        __file__)), "..", "..", "tools"))
    from melee_course import registry
    return [d for d in drills if not registry.has(d)]

def main():
    missing = waiting_for(['fox-shine-oos'])
    if missing:
        print("skip: plays %s, not rebuilt yet in the drill format"
              % ", ".join(missing))
        return 0
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    args = ap.parse_args()
    shots = args.shots or tempfile.mkdtemp(prefix="melee-shots-")
    save = os.path.join(tempfile.mkdtemp(prefix="melee-client-"),
                        "client.json")
    w = c = None

    def frames(n):
        for _ in range(n):
            c.frame()

    def tap(key, after=6):
        w.key(key)
        frames(2)
        w.key(key, False)
        frames(after)

    try:
        w = window.Window(window=(1280, 720))
        w.step(30)
        c = client.Client(w, source="keyboard", save=save,
                          out=tempfile.mkdtemp(prefix="melee-ui-"))
        w.pace(False)
        frames(6)
        tap("x")
        tap("x")
        for _ in range(4):
            if DRILL in [d["id"] for d in c.course["parts"][
                    courses.PARTS[int(c.hub_at[1:])]]]:
                break
            tap("Right")
        tap("x")
        while c.drills()[c.row[c.part]]["id"] != DRILL:
            tap("Down")
        first_row = c.row[c.part]

        seen = dict(step=0, n=0)

        def person(game, frame):
            if frame == -6:
                # the tutorial's card, on the drill's first open: START,
                # straight to the drill (once it is drawn)
                game.key("x", False)             # the A that started it
                seen["card"] = seen.get("card", 0) + 1
                if seen["card"] == 4:
                    game.key("Return")
                elif seen["card"] == 6:
                    game.key("Return", False)
                return
            seen["n"] += 1
            step = seen["step"]
            if step == 0:
                game.key("x", False)             # the A that started it
                game.key("Return", False)        # (the tutorial's START)
                seen.update(step=1, n=0)
            elif step == 1 and seen["n"] > 30:
                game.key("Return")               # hold START 3 s
                seen.update(step=2, n=0)
            elif step == 2 and seen["n"] > 190:
                game.key("Return", False)
                seen["hidden"] = c.column_hidden
                path = game.shot(os.path.join(shots, "column-away.png"))
                seen["sides"] = (mean(str(path), "150x720+0+0"),
                                 mean(str(path), "150x720+1130+0"),
                                 mean(str(path), "800x720+240+0"))
                seen.update(step=3, n=0)
            elif step == 3 and seen["n"] > 10:
                game.key("Return")               # and back
                seen.update(step=4, n=0)
            elif step == 4 and seen["n"] > 190:
                game.key("Return", False)
                seen["back"] = not c.column_hidden
                seen.update(step=5, n=0)
            elif step == 5 and seen["n"] > 10:
                # the pause menu: Timing from Lenient to Frame-perfect
                ch = seen.setdefault("pick", Chooser(c, "timing"))
                if not ch.done:
                    ch(game)
                if c.pause_open and ch.done and not seen.get("rights"):
                    seen["rights"] = 0
                if c.pause_open and "rights" in seen and \
                        seen["rights"] < 2:
                    # Right, one frame on and one off, once
                    if seen["rights"] % 2 == 0:
                        game.key("Right")
                    else:
                        game.key("Right", False)
                    seen["rights"] += 1
                elif c.pause_open and seen.get("rights") == 2 and \
                        not seen.get("pshot"):
                    game.shot(os.path.join(shots, "pause.png"))
                    seen["pshot"] = True
                elif c.pause_open and seen.get("rights") == 2:
                    seen["timing_row"] = [r for r in c.pause_rows("drill")
                                          if r[0] == "timing"][0][2]
                    game.key("z")                # B: back to the drill
                    seen["rights"] = 7
                elif seen.get("rights") == 7 and not c.pause_open:
                    game.key("z", False)
                    seen.update(step=6, n=0)
            elif step == 6:
                if "strict" not in seen:          # the new try's start
                    seen["strict"] = getattr(c.session.d, "strict", None)
                # the shield and the stick down in it: a spot dodge, a
                # failure
                game.key("s")
                if seen["n"] % 30 == 12:
                    game.key("Down")
                elif seen["n"] % 30 == 15:
                    game.key("Down", False)
                if c.results_now():
                    game.key("s", False)
                    game.key("Down", False)
                    seen.update(step=7, n=0)
            elif step == 7 and seen["n"] == 5:
                path = game.shot(os.path.join(shots, "failure.png"))
                seen["red"] = colour_count(str(path), "960x50+0+0",
                                           (0xF0, 0x64, 0x3C))
            elif step == 7 and seen["n"] > 20:
                game.key("h")                    # hold D-pad right 3 s
                seen.update(step=8, n=0)
            elif step == 8 and seen["n"] > 200:
                game.key("h", False)
                seen.update(step=9, n=0)
            elif step == 9:
                seen.setdefault("out", Chooser(c, "list"))(game)

        c.person = person
        w.key("x")
        for _ in range(20):
            c.frame()
            if c.screen == "list" and seen["step"] == 9:
                break
        for key in ("x", "s", "h", "Return", "z", "Right", "Down"):
            w.key(key, False)
        frames(6)
        check("START held 3 s puts the column away, the game in the middle",
              seen.get("hidden") is True and seen["sides"][0] < 0.01 and
              seen["sides"][1] < 0.01 and seen["sides"][2] > 0.02,
              "sides %.3f %.3f, middle %.3f" % seen.get("sides", (-1,) * 3))
        check("held again: the column is back", seen.get("back") is True)
        check("a setting in the pause menu: Timing Lenient to "
              "Frame-perfect", seen.get("timing_row") == "Frame-perfect",
              str(seen.get("timing_row")))
        check("and the next try has it (the drill judges frame-perfect)",
              seen.get("strict") is True, str(seen.get("strict")))
        check("a failure shows red on the banner", seen.get("red", 0) > 200,
              "%s red pixels" % seen.get("red"))
        drills = c.drills()
        # (the next that plays here: the client passes the drills not
        # built for it; in Punish only this one is rebuilt, and it opens
        # again)
        want = first_row
        for _ in range(len(drills)):
            want = (want + 1) % len(drills)
            if drills[want]["id"] in c.here:
                break
        check("D-pad right held 3 s went to the next drill that plays "
              "here, and the pause menu back to the list",
              c.screen == "list" and c.row[c.part] == want,
              "row %d -> %d (%s)" % (first_row, c.row[c.part],
                                     drills[c.row[c.part]]["id"]))
        bad = [line.strip()[:160] for line in w.log
               if "aurora" in line and ("warn" in line or "error" in line)]
        check("the interface raised no warnings", not bad,
              "; ".join(bad[:3]))
    finally:
        if w is not None:
            w.close()
        left = window.leftovers()
        check("nothing left running", not left, str(left))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
