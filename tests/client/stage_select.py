"""The stage select, the menus' faded drawings, and Versus without the
sidebar, checked on a virtual display with keys pressed on it.

    python tests/client/stage_select.py [--shots DIR]

The stage select comes after the characters (Versus > Local here): six
panels with the native build's pictures of the stages (drawn first if they
are not yet: half a minute), the card with the stage whole, the game's name
logo, its width and blast zones as the game reads them; the arrows move
three to a row and the card follows; X picks one at random and starts the
match. Every main menu panel and course part has its faded drawing. A
Versus match starts with the sidebar put away, START held brings it back
without changing what the player keeps, and the Lab (training) keeps it.
--shots saves a picture of each step (under build/shots/ they stay out of
the repository).
"""
import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "melee_client"))
sys.path.insert(0, str(ROOT / "tools" / "melee_native"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import client  # noqa: E402
import marks  # noqa: E402
import pausekeys  # noqa: E402
import stages  # noqa: E402
import window  # noqa: E402

checks = []
HOLD = client.HOLD_COLUMN + 10      # frames: START held puts the column away


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def spread(path, boxes):
    """How much the colour varies in each (x, y, width, height) of a
    1280x720 picture: none in a box of one colour."""
    raw = subprocess.run(["magick", str(path), "-crop", "1280x720+0+0",
                          "+repage", "rgb:-"], check=True,
                         capture_output=True).stdout
    img = np.frombuffer(raw, np.uint8).reshape(720, 1280, 3).astype(float)
    return [img[y:y + h, x:x + w].std() for x, y, w, h in boxes]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for a picture of each step")
    args = ap.parse_args()
    out = Path(tempfile.mkdtemp(prefix="melee-ui-"))
    save = Path(tempfile.mkdtemp(prefix="melee-save-")) / "client.json"
    pic = out / "shot.png"
    w = None

    def frames(n):
        for _ in range(n):
            c.frame()

    def tap(key, after=6):
        w.key(key)
        frames(2)
        w.key(key, False)
        frames(after)

    def hold_start():
        w.key("Return")
        frames(HOLD)
        w.key("Return", False)
        frames(10)

    def shot(name):
        if args.shots:
            w.shot(os.path.join(args.shots, name + ".png"))

    def text(name):
        path = out / name
        return path.read_text() if path.exists() else ""

    try:
        stages.ensure()
        if stages.missing():
            print("drawing the stages first (half a minute)")
            stages.render(log=lambda *a: None)
        w = window.Window(window=(1280, 720))
        w.step(30)
        c = client.Client(w, source="keyboard", save=save, out=out)
        w.pace(False)
        frames(10)

        # ---- the menus' faded drawings -----------------------------------
        page = text("main.rml")
        have = bool(marks.ensure())
        check("every main menu panel has its faded drawing",
              not have or all("marks/%s.png" % m in page
                              for m in ("versus", "train", "settings")),
              "rsvg-convert" if have else "no rsvg-convert: none")
        tap("x")
        tap("x")
        hub = text("hub.rml")
        check("and every part of a course, and the Lab",
              c.screen == "hub" and (not have or all(
                  "marks/%s.png" % m in hub
                  for m in ("tech", "punish", "defense", "neutral", "lab"))))
        shot("hub")
        tap("z")
        tap("z")

        # ---- the stage select ---------------------------------------------
        tap("Left")
        tap("x")                      # Versus: Local or Online
        tap("x")                      # Local: the characters
        tap("x")                      # Fox
        tap("x")                      # Marth, the opponent
        check("after the characters, the stage select",
              c.screen == "stages" and c.mode == "versus")
        page = text("stages.rml")
        check("its six panels are the native build's pictures of the stages",
              all("stage/%s-tile.png" % s["id"] in page
                  for s in stages.STAGES))
        check("the card: the stage whole and the game's name logo",
              "stage/battlefield-preview.png" in page and
              "stage/battlefield-name.png" in page)
        check("Battlefield's width and blast zones, as the game reads them",
              "136.8" in page and "108.8" in page and ">224<" in page)
        w.shot(pic)
        shot("stages")
        boxes = [(60 + 256 * (i % 3) + 80, 120 + 256 * (i // 3) + 60, 80,
                  110) for i in range(6)]
        least = min(spread(pic, boxes))
        card = spread(pic, [(860, 130, 360, 70)])[0]
        check("and they are drawn: no panel is one colour, nor the card's "
              "picture", least > 8 and card > 8,
              "least %.1f, card %.1f" % (least, card))
        tap("Right")
        tap("Down")
        card = text("part-card.rml")
        check("the arrows move three to a row and the card follows",
              client.STAGE_ORDER[c.stage_at] == "fountain-of-dreams" and
              "stage/fountain-of-dreams-preview.png" in card and
              "126.7" in card, client.STAGE_ORDER[c.stage_at])
        shot("stages-fountain")
        tap("v", after=40)
        check("X: a stage at random, and the match starts",
              c.screen == "versus" and
              w.match_info["stage"] in client.STAGE_ORDER,
              str(w.match_info.get("stage")))

        # ---- Versus without the sidebar ------------------------------------
        frames(30)
        kept = c.settings["sidebar"]
        check("a Versus match starts with the sidebar put away",
              c.column_hidden and kept)
        shot("versus")
        hold_start()
        check("START held brings it back for the match",
              not c.column_hidden and c.screen == "versus")
        hold_start()
        check("and away again, what the player keeps unchanged",
              c.column_hidden and c.settings["sidebar"] == kept)
        pausekeys.leave(c, w, "main", frames)
        check("out of the match, the sidebar as kept",
              c.screen == "main" and c.column_hidden == (not kept))

        # ---- the Lab keeps it ---------------------------------------------
        tap("Right")
        tap("x")
        tap("x")
        tap("Down")
        tap("x")
        tap("x")
        tap("x", after=40)
        check("the Lab (training) keeps the sidebar",
              c.screen == "versus" and c.mode == "lab" and
              not c.column_hidden)
        shot("lab")
        pausekeys.leave(c, w, "main", frames)
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
