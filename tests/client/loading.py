"""No loading screens in the native client: situations change the way
TM-CE's savestates change them, in a frame, and a match that must be loaded
is loaded unseen and unheard.

    python tests/client/loading.py [--shots DIR]

Off screen:
- the window: a match loaded in a quiet stretch (`quiet`) leaves the last
  picture on screen until the new match's first frame, with no black frame
  and nothing of the load shown; it takes a fraction of what a drawn load
  takes, and only the stretch's first 150 ms of sound is written;
- the first drill from the menu loads its match with the course's other
  opponents: the shine out of shield's six are all there, and attempt after
  attempt is against them, the opponent swapped in place, no match loaded;
- a drill without an opponent keeps that match, its opponent asleep, and
  the next drill against Marth keeps it too, Marth back in play;
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
SLEEP = 11


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
        # (the first is taken two frames in: the picture shown as the load
        # began may reach the screen a frame late)
        check("a quiet load leaves the last picture on screen",
              same_picture(held[1], held[2]) and mean(held[1]) > 0.02,
              "%.3f" % mean(held[1]))
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
    missing = waiting_for(['fox-shine-oos', 'fox-multishine', 'fox-approach-nair-dair'])
    if missing:
        print("skip: plays %s, not rebuilt yet in the drill format"
              % ", ".join(missing))
        return 0
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
        part = next(i for i, p in enumerate(courses.PARTS)
                    if ident in [d["id"] for d in c.course["parts"][p]])
        if not c.hub_at.startswith("p"):
            tap("Up")
        for _ in range(6):
            at = int(c.hub_at[1:])
            if at == part:
                break
            tap("Right" if at < part else "Left")
        tap("x")
        for _ in range(40):
            if c.drills()[c.row[c.part]]["id"] == ident:
                break
            tap("Down")
        if c.screen != "list" or c.drills()[c.row[c.part]]["id"] != ident:
            raise RuntimeError("no way to %s from %s" % (ident, c.screen))
        seen["asked"] = time.time()
        w.key("x")

    def play(ident, attempts=1):
        """Drill `ident` until `attempts` attempts have begun, then back to
        its list: what it was like as each began."""
        seen.clear()
        seen.update(n=0, at=[])

        def person(game, frame):
            seen["n"] += 1
            if seen["n"] == 1:
                game.key("x", False)
            if frame == 0:
                s = c.session
                f = game.fighter(1 - c.port)
                seen["at"].append(dict(
                    match=game.state()["match"], cpu=s.cpu_char,
                    loaded=tuple(s.swappable), parked=s.parked,
                    state=f.state if f.fp else None,
                    deck={e.cpu for e in s.d.deck or () if e.cpu},
                    after=time.time() - seen["asked"]))
            if len(seen["at"]) >= attempts and "out" not in seen:
                seen["out"] = Chooser(c, "list")
            if "out" in seen:
                seen["out"](game)

        c.person = person
        open_drill(ident)
        for _ in range(60):
            c.frame()
            if c.screen == "list" and "out" in seen:
                break
        w.key("x", False)
        return seen["at"]

    seen = {}
    try:
        w = window.Window(window=(1280, 720))
        w.step(30)
        c = client.Client(w, source="keyboard", save=save,
                          out=tempfile.mkdtemp(prefix="melee-ui-"))
        w.pace(False)
        frames(6)

        # ---- a deck of six opponents, swapped in ------------------------
        at = play("fox-shine-oos", attempts=7)
        first = at[0]
        print("      (the first drill from the menu: its match in %.2f s, "
              "with %s)" % (first["after"], ", ".join(first["loaded"])))
        check("shine out of shield: its six opponents all loaded",
              first["deck"] <= set(first["loaded"]),
              "deck %s" % sorted(first["deck"]))
        check("attempt after attempt against them, swapped in place: the "
              "same match all along", len({a["match"] for a in at}) == 1 and
              len({a["cpu"] for a in at}) >= 2,
              ", ".join(a["cpu"] for a in at))
        before = at[0]["match"]

        # ---- a drill without an opponent keeps the match ----------------
        at = play("fox-multishine")
        check("a drill without an opponent keeps the match, its opponent "
              "asleep", at[0]["match"] == before and
              at[0]["parked"] is not None and at[0]["state"] == SLEEP,
              "match %s -> %s, state %s" % (before, at[0]["match"],
                                            at[0]["state"]))
        w.shot(os.path.join(shots, "solo.png"))

        # ---- and the next one with an opponent too ----------------------
        at = play("fox-approach-nair-dair")
        check("the next drill against Marth keeps it, Marth back in play",
              at[0]["match"] == before and at[0]["cpu"] == "marth" and
              at[0]["state"] not in (None, SLEEP), "match %s -> %s, "
              "state %s" % (before, at[0]["match"], at[0]["state"]))
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
