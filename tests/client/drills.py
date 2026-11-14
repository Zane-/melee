"""The drill changes from the owner's play session, in the native client.

    python tests/client/drills.py [--shots DIR]

Off screen: Fox's dash dance shows a light ray on the stage where its
target is (the game's camera places it) and a status line; the shield drop
changes stage with R held 5 s (the column says which) and the match is on
that stage; a timing drill's verdict brings its timeline to the column.
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

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def column_mean(path, x, y0, y1):
    """The picture's mean brightness in a 6-pixel column at x."""
    out = subprocess.run(["magick", path, "-crop", "6x%d+%d+%d" % (
        y1 - y0, x - 3, y0), "+repage", "-colorspace", "Gray", "-format",
        "%[fx:mean]", "info:"], capture_output=True, text=True).stdout
    return float(out or -1)


def main():
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

    def open_drill(ident):
        """From the main menu or a drill list to drill `ident` of Fox's
        course, started (A held: the drill's hook lets it go)."""
        if c.screen == "main":
            tap("x")
            tap("x")
        if c.screen == "list":
            tap("z")                             # back to the course hub
        for _ in range(4):
            if ident in [d["id"] for d in c.course["parts"][
                    courses.PARTS[int(c.hub_at[1:])]]]:
                break
            tap("Right")
        tap("x")
        for _ in range(40):
            if c.drills()[c.row[c.part]]["id"] == ident:
                break
            tap("Down")
        if c.screen != "list" or c.drills()[c.row[c.part]]["id"] != ident:
            raise RuntimeError("no way to %s from %s" % (ident, c.screen))
        w.key("x")

    try:
        w = window.Window(window=(1280, 720))
        w.step(30)
        c = client.Client(w, source="keyboard", save=save,
                          out=tempfile.mkdtemp(prefix="melee-ui-"))
        w.pace(False)
        frames(6)

        # ---- the dash dance's light ray ----------------------------------
        seen = dict(n=0)

        def dance(game, frame):
            seen["n"] += 1
            if seen["n"] == 1:
                game.key("x", False)
            if seen["n"] == 40:
                d = c.session.d
                seen["target"] = d.target
                seen["rays"] = c.rays_html
                seen["status"] = c.status_text
                if d.target is not None:
                    sx, sy = game.project(d.target, 0.0)
                    path = str(game.shot(os.path.join(shots, "ray.png")))
                    # the picture is the window's 1280x720; the game's
                    # 640x480 is its left 960x720
                    x, y = int(sx * 1.5), int(sy * 1.5)
                    seen["on"] = column_mean(path, x, 40, max(41, y - 20))
                    seen["off"] = column_mean(path, min(950, x + 60), 40,
                                              max(41, y - 20))
            if seen["n"] == 45:
                seen["out"] = Chooser(c, "list")
            if "out" in seen:
                seen["out"](game)

        c.person = dance
        open_drill("universal-dash-dance")
        for _ in range(20):
            c.frame()
            if c.screen == "list" and "out" in seen:
                break
        w.key("x", False)
        check("dash dance: a light ray is drawn where the target is",
              seen.get("rays") and seen.get("on", 0) > seen.get("off", 1) +
              0.15, "target %s, column %.2f vs %.2f beside it" % (
                  seen.get("target"), seen.get("on", -1),
                  seen.get("off", -1)))
        check("and the status line counts the rays reached",
              (seen.get("status") or "").startswith("Rays reached"),
              str(seen.get("status")))

        # ---- the shield drop's stages ------------------------------------
        seen = dict(n=0)

        def stages(game, frame):
            seen["n"] += 1
            if seen["n"] == 1:
                game.key("x", False)
                seen["first"] = c.session.d.stage
            elif seen["n"] == 20:
                game.key("s")                    # hold R 5 s
            elif seen["n"] == 20 + 310:
                game.key("s", False)
            elif seen["n"] == 20 + 310 + 90:
                seen["second"] = c.session.d.stage
                seen["status"] = c.status_text
                seen["out"] = Chooser(c, "list")
            if "out" in seen:
                seen["out"](game)

        c.person = stages
        open_drill("universal-shield-drop")
        for _ in range(30):
            c.frame()
            if c.screen == "list" and "out" in seen:
                break
        w.key("x", False)
        w.key("s", False)
        check("shield drop: R held 5 s goes to the next stage",
              seen.get("first") == "battlefield" and
              seen.get("second") == "yoshis-story", "%s -> %s" % (
                  seen.get("first"), seen.get("second")))
        check("and its status line names the platform and the start",
              "platform" in (seen.get("status") or ""),
              str(seen.get("status")))
        check("and the match was loaded on it", w.match_info.get("stage")
              == "yoshis-story" if hasattr(w, "match_info") else True,
              str(getattr(w, "match_info", {}).get("stage")))

        # ---- a timing drill's timeline -----------------------------------
        seen = dict(n=0)

        def jc(game, frame):
            seen["n"] += 1
            if seen["n"] == 1:
                game.key("x", False)
            elif seen["n"] == 30:
                game.key("Down")                 # shine: down+B
                game.key("z")
            elif seen["n"] == 32:
                game.key("z", False)
                game.key("Down", False)
            elif seen["n"] == 35:
                game.key("c")                    # jump 3 later: frame 4
            elif seen["n"] == 37:
                game.key("c", False)
            if c.results_now() and "tl" not in seen:
                seen["tl"] = (c.last_result or {}).get("timeline")
                seen["at"] = seen["n"]
            if "at" in seen and seen["n"] == seen["at"] + 5:
                game.shot(os.path.join(shots, "timeline.png"))
                seen["out"] = Chooser(c, "list")
            if "out" in seen:
                seen["out"](game)

        c.person = jc
        open_drill("fox-jc-shine")
        for _ in range(30):
            c.frame()
            if c.screen == "list" and "out" in seen:
                break
        for key in ("x", "z", "c", "Down"):
            w.key(key, False)
        tl = seen.get("tl") or {}
        check("JC shine: the verdict brings its timeline to the column",
              [r["label"] for r in tl.get("rows", [])] ==
              ["Shine", "Jump", "Jumped"], str(tl.get("rows")))
        rows = {r["label"]: r["you"] for r in tl.get("rows", [])}
        check("and a press is on the frame of what it starts (a live pad "
              "as a scripted one)", rows.get("Shine") == [1] and
              rows.get("Jump") and rows.get("Jump") == rows.get("Jumped"),
              str(rows))
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
