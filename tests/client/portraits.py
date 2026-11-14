"""The character select's pictures, costumes and the place Zelda and Sheik
share, checked on a virtual display with keys pressed on it.

    python tests/client/portraits.py [--shots DIR]

The game's own portraits and emblems are in the documents (art.py reads
them off the disc; Sheik's are drawn from her model, the first time). 25
places, Zelda's holding Sheik. Y changes the costume on the card; X turns
Sheik into Zelda and back, on her panel and on the card; A starts a match
as the character shown, in the costume chosen. On the opponent screen Y
turns that place too. --shots saves a picture of each step (under
build/shots/ they stay out of the repository).
"""
import argparse
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "melee_client"))
sys.path.insert(0, str(ROOT / "tools" / "melee_native"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import art  # noqa: E402
import characters  # noqa: E402
import client  # noqa: E402
import pausekeys  # noqa: E402
import window  # noqa: E402
from native import CHARACTERS  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for a picture of each step")
    args = ap.parse_args()
    out = Path(tempfile.mkdtemp(prefix="melee-ui-"))
    w = None

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

    def goto(target, which="at"):
        """Arrows until the place in focus (`which`) is `target`."""
        for _ in range(20):
            at = getattr(c, which)
            if at == target:
                return True
            row, col = divmod(at, client.COLUMNS)
            trow, tcol = divmod(target, client.COLUMNS)
            if row < trow and at + client.COLUMNS < len(c.roster):
                tap("Down", after=3)
            elif row > trow:
                tap("Up", after=3)
            elif col < tcol:
                tap("Right", after=3)
            elif col > tcol:
                tap("Left", after=3)
            else:
                tap("Down", after=3)
        return getattr(c, which) == target

    def text(name):
        path = out / name
        return path.read_text() if path.exists() else ""

    try:
        art.ensure()
        if art.sheik_missing():
            print("drawing Sheik first (half a minute)")
            art.render_sheik(log=lambda *a: None)
        w = window.Window(window=(1280, 720))
        w.step(30)
        c = client.Client(w, source="keyboard", out=out)
        w.pace(False)
        frames(10)

        tap("x")
        page = text("characters.rml")
        check("A on Train opens the character select at Fox",
              c.screen == "chars" and c.roster[c.at]["id"] == "fox")
        check("its panels show the game's portraits and emblems",
              "portrait/fox-0.png" in page and
              "emblem/star-fox.png" in page and
              page.count('class="face"') == 25)
        check("25 places: Zelda and Sheik share one",
              len(c.roster) == 25 and 'id="c24"' in page and
              'id="c25"' not in page)
        shot("characters-fox")

        tap("c")
        tap("c")
        card = text("part-card.rml")
        check("Y puts Fox in his next costumes, on the card",
              c.dressed() == 2 and "portrait/fox-2.png" in card and
              card.count("cchip on") == 1, str(c.dressed()))
        shot("characters-fox-costume")

        place, sheik = characters.find(c.roster, "sheik")
        check("the place is Sheik's first",
              c.roster[place]["id"] == "sheik")
        check("and the arrows reach it", goto(place), str(c.at))
        card = text("part-card.rml")
        check("her card shows her portrait, drawn from her model, and "
              "Zelda one button away",
              "portrait/sheik-0.png" in card and ">Zelda<" in card)
        shot("characters-sheik")

        tap("v")
        card = text("part-card.rml")
        tile = text("part-c%d.rml" % place)
        check("X turns her into Zelda: her panel and the card",
              c.roster[c.at]["id"] == "zelda" and
              "portrait/zelda-0.png" in tile and
              "portrait/zelda-0.png" in card and ">Sheik<" in card)
        shot("characters-zelda")
        tap("v")
        check("and X again, back into Sheik",
              c.roster[c.at]["id"] == "sheik" and
              "portrait/sheik-0.png" in text("part-c%d.rml" % place))

        tap("v")
        tap("c")
        tap("x", after=40)
        me = w.fighter(0)
        check("A starts a match as Zelda, in the costume chosen",
              c.screen == "match" and me.ckind == CHARACTERS["zelda"] and
              me.costume == 1,
              "ckind %d, costume %d" % (me.ckind, me.costume))
        frames(60)
        shot("match-zelda")
        pausekeys.leave(c, w, "back", frames)
        check("back on the character select, the place is still Zelda",
              c.screen == "chars" and c.roster[c.at]["id"] == "zelda")

        tap("v")
        tap("x", after=40)
        me = w.fighter(0)
        check("and as Sheik, in her default costume",
              c.screen == "match" and me.ckind == CHARACTERS["sheik"] and
              me.costume == 0,
              "ckind %d, costume %d" % (me.ckind, me.costume))
        pausekeys.leave(c, w, "main", frames)

        # the Lab: Fox against someone
        tap("Right")
        tap("x")
        goto(characters.find(c.roster, "fox")[0])
        tap("x", after=10)
        check("the Lab: the opponent screen", c.screen == "opp")
        goto(place, "opp_at")
        before = c.roster[c.opp_at]["id"]
        tap("c")
        card = text("part-card.rml")
        check("Y there turns the shared place too",
              before == "sheik" and c.roster[c.opp_at]["id"] == "zelda" and
              "portrait/zelda-0.png" in card,
              "%s -> %s" % (before, c.roster[c.opp_at]["id"]))
        shot("opponent-zelda")
    finally:
        if w is not None:
            w.close()
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
