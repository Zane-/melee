"""No loading screens in the native client: situations change the way
TM-CE's savestates change them, in a frame, and a match that must be loaded
is loaded unseen and unheard.

    python tests/client/loading.py [--shots DIR]

Off screen:
- the window: a match loaded in a quiet stretch (`quiet`) leaves the last
  picture on screen until the new match's first frame, with no black frame
  and nothing of the load shown; it takes a fraction of what a drawn load
  takes, and only the stretch's first 150 ms of sound is written;
- a drill whose scenarios have different opponents (Fox's whiff punish:
  Marth, Sheik, Peach) plays attempt after attempt against them, the
  opponent swapped in place, no match loaded;
- the next drill against one of them on the same stage keeps the match;
- the interface raised no warnings (a held frame once dropped the window's
  surface, and the game fell over).
"""
import argparse
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
from pausekeys import Chooser  # noqa: E402

checks = []
TAIL_BYTES = 30 * 160 * 4  # 150 ms of 16-bit stereo at 32 kHz


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def same_picture(a, b):
    """Two pictures with the same pixels (ImageMagick's count of those that
    differ)."""
    import subprocess
    out = subprocess.run(["magick", "compare", "-metric", "AE", a, b,
                          "null:"], capture_output=True, text=True)
    try:
        return float((out.stderr or out.stdout).split()[0]) == 0
    except (ValueError, IndexError):
        return False


def mean(path):
    import subprocess
    out = subprocess.run(["magick", path, "-colorspace", "Gray", "-format",
                          "%[fx:mean]", "info:"], capture_output=True,
                         text=True).stdout
    return float(out or -1)


def window_checks(shots):
    raw = os.path.join(tempfile.mkdtemp(prefix="melee-sound-"), "out.raw")
    w = window.Window(sound_file=raw)
    try:
        w.pace(False)
        t = time.time()
        w.start("fox", "sheik", "final-destination", seed=3)
        drawn = time.time() - t
        w.step(20)
        size = os.path.getsize(raw)
        t = time.time()
        w.quiet(True)
        held = []
        w.step(2)
        held.append(os.path.join(shots, "quiet-held0.png"))
        w.shot(held[-1])
        w.match("fox", "marth", "battlefield", seed=5)
        w.step(40)
        held.append(os.path.join(shots, "quiet-held1.png"))
        w.shot(held[-1])
        w.start("fox", "marth", "battlefield", seed=5)
        held.append(os.path.join(shots, "quiet-held2.png"))
        w.shot(held[-1])
        heard = os.path.getsize(raw) - size
        w.quiet(False)
        quiet = time.time() - t
        before = held[0]
        check("a quiet load leaves the last picture on screen",
              all(same_picture(held[0], p) for p in held[1:]) and
              mean(held[0]) > 0.02, "%.3f" % mean(held[0]))
        check("and takes a fraction of a drawn one", quiet < drawn / 2,
              "%.2f s, drawn %.2f s" % (quiet, drawn))
        check("only its first 150 ms of sound is heard", heard == TAIL_BYTES,
              "%d bytes, the tail is %d" % (heard, TAIL_BYTES))
        darkest = 1.0
        for i in range(4):
            w.step()
            path = os.path.join(shots, "quiet-after%d.png" % i)
            w.shot(path)
            darkest = min(darkest, mean(path))
        check("then the new match, with no black frame between",
              not same_picture(before, path) and darkest > 0.02,
              "darkest %.3f" % darkest)
        bad = [line.strip()[:160] for line in w.log
               if "aurora" in line and ("warn" in line or "error" in line)]
        check("the window raised no warnings", not bad, "; ".join(bad[:3]))
    finally:
        w.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    args = ap.parse_args()
    shots = args.shots or tempfile.mkdtemp(prefix="melee-shots-")
    os.makedirs(shots, exist_ok=True)
    window_checks(shots)

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
        course, started (A held: the drill lets it go)."""
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

        # ---- one drill, its opponents swapped in -------------------------
        seen = dict(n=0, cpus=[], matches=set(), attempts=0)

        def whiff(game, frame):
            seen["n"] += 1
            if seen["n"] == 1:
                game.key("x", False)
            s = c.session
            if frame == 0:
                seen["cpus"].append(s.cpu_char)
                seen["matches"].add(game.state()["match"])
            if len(seen["cpus"]) >= 7 and "out" not in seen:
                seen["out"] = Chooser(c, "list")
            if "out" in seen:
                seen["out"](game)

        c.person = whiff
        open_drill("fox-whiff-punish")
        for _ in range(40):
            c.frame()
            if c.screen == "list" and "out" in seen:
                break
        w.key("x", False)
        check("whiff punish: attempt after attempt against its opponents",
              len(set(seen["cpus"])) >= 2, ", ".join(map(str,
                                                         seen["cpus"])))
        check("swapped in place: the same match all along",
              len(seen["matches"]) == 1, str(sorted(seen["matches"])))
        before = w.state()["match"]

        # ---- the next drill keeps the match ------------------------------
        seen = dict(n=0)

        def aerial(game, frame):
            seen["n"] += 1
            if seen["n"] == 1:
                game.key("x", False)
            if frame == 0 and "match" not in seen:
                seen["match"] = game.state()["match"]
                seen["cpu"] = c.session.cpu_char
                game.shot(os.path.join(shots, "next-drill.png"))
                seen["out"] = Chooser(c, "list")
            if "out" in seen:
                seen["out"](game)

        c.person = aerial
        open_drill("fox-approach-nair-dair")
        for _ in range(40):
            c.frame()
            if c.screen == "list" and "out" in seen:
                break
        w.key("x", False)
        check("the next drill against Marth on the same stage keeps the "
              "match", seen.get("cpu") == "marth" and
              seen.get("match") == before, "match %s -> %s" % (
                  before, seen.get("match")))
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
