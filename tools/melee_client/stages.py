"""The stage select's pictures and facts (the canvas's "A · Stage select:
grid and card", chosen by the owner 2026-11-14).

- The game's own name logos for the six stages ("Special Stages /
  Battlefield"), read off the disc (MnSlMap.usd, the stage select's file) as
  art.py reads the character select's art.
- Each stage drawn by the native build, empty (the one fighter put to
  sleep: no fighter, no damage display) and seen by the studio camera:
  whole and straight on for the card, and from above and to one side for
  its panel. The disc's own icons are 58 by 50 pixels, soft at a panel's
  size (the owner asked for "higher resolution images ... native angled
  screenshots"); these are drawn at the size they are shown, twice over.
- Its blast zones and ledge, read from the running game as it draws it
  ("studio stage": the game's own getters).

All of it under build/ui/art/stage, never in the repo.

    python tools/melee_client/stages.py            # what is missing
    python tools/melee_client/stages.py --render   # draw them all again
"""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

import art

ROOT = art.ROOT
OUT = art.ART / "stage"
VERSION = 2    # of the pictures drawn: a change draws them again

# In the order of the stage select. `logo`: its name logo's place among the
# disc's 30 (by where they are in the file: the vanilla select's order).
# `cam`: the studio camera for the panel, (distance, height looked at,
# from the side in degrees, from above in degrees, and optionally where
# along the stage it looks: left of the middle puts the stage further
# right in the panel); `view`: for the card, straight on (eye, looked at,
# field of view).
STAGES = [
    dict(id="battlefield", name="Battlefield", logo=24, platforms=3,
         about="Three platforms, the highest centred over the stage.",
         cam=(225, 10, -22, 24, -16), view=(0, 40, 245, 0, 18, 0, 30)),
    dict(id="final-destination", name="Final Destination", logo=25,
         platforms=0,
         about="Flat, with no platforms: nowhere to land but the stage.",
         cam=(330, -12, -22, 24), view=(0, 38, 285, 0, -6, 0, 30)),
    dict(id="dream-land", name="Dream Land", logo=26, platforms=3,
         about="Three platforms and the widest blast zones of the six. "
               "Whispy Woods blows wind.",
         cam=(265, 18, -22, 24), view=(0, 50, 300, 0, 20, 0, 30)),
    dict(id="yoshis-story", name="Yoshi's Story", logo=8, platforms=3,
         about="The smallest of the six. Randall the cloud passes under "
               "the ledges.",
         cam=(215, 8, -22, 24), view=(0, 40, 250, 0, 10, 0, 30)),
    dict(id="fountain-of-dreams", name="Fountain of Dreams", logo=10,
         platforms=3,
         about="The two side platforms rise and sink; the highest stays.",
         cam=(275, 10, -22, 24), view=(0, 45, 260, 0, 12, 0, 30)),
    dict(id="pokemon-stadium", name="Pokémon Stadium", logo=14,
         platforms=2,
         about="Two platforms. Turns to fire, grass, rock and water, and "
               "back.",
         cam=(275, 6, -22, 24), view=(0, 50, 320, 0, 10, 0, 30)),
]
BY_ID = {s["id"]: s for s in STAGES}
LOGO = (224, 56)
LOGOS = 30
# what is drawn, in pixels: twice the size shown (a panel's picture is
# 292 by 210 dp, the card's 388 by 218)
TILE = (584, 420)
PREVIEW = (776, 436)
RENDER = (1280, 920)   # the window drawn in (a panel's shape)


# ---- off the disc ------------------------------------------------------------------

def logos(arc):
    """The 30 name logos (224x56, 4-bit intensity), in the file's order."""
    found = {}
    for r in arc.rel:
        o = arc.u32(r) if r + 4 <= len(arc.d) else None
        if o is not None and arc.is_image(o):
            p, w, h, fmt = arc.image(o)
            if (w, h, fmt) == (LOGO[0], LOGO[1], 0):
                found[p] = o
    if len(found) != LOGOS:
        raise ValueError("%d stage names, not %d" % (len(found), LOGOS))
    out = []
    for p in sorted(found):
        a = art.i4(arc.d[p:p + LOGO[0] * LOGO[1] // 2], LOGO[0], LOGO[1])
        rgba = np.full((LOGO[1], LOGO[0], 4), 255, np.uint8)
        rgba[..., 3] = a
        out.append(rgba)
    return out


def logo(sid, root=OUT):
    path = root / (sid + "-name.png")
    return path if path.exists() else None


def tile(sid, root=OUT):
    path = root / (sid + "-tile.png")
    return path if path.exists() else None


def preview(sid, root=OUT):
    path = root / (sid + "-preview.png")
    return path if path.exists() else None


def facts(root=OUT):
    """{id: {"blast": [left, right, top, bottom], "ledge": x}} as read
    from the game, for the stages drawn."""
    try:
        return json.loads((root / "facts.json").read_text())
    except (OSError, ValueError):
        return {}


def ensure(root=OUT):
    """The name logos off the disc, if they are not here yet. True if they
    are."""
    if all(logo(s["id"], root) for s in STAGES):
        return True
    try:
        names = logos(art.Archive(art.disc_file("MnSlMap.usd")))
    except (OSError, ValueError) as e:
        print("stages: %s" % e, file=sys.stderr)
        return False
    root.mkdir(parents=True, exist_ok=True)
    for s in STAGES:
        art.write_png(root / (s["id"] + "-name.png"), names[s["logo"]])
    return True


def missing(root=OUT):
    """Stages whose pictures are not drawn yet (or were drawn by another
    VERSION of this file)."""
    try:
        drawn = json.loads((root / "drawn.json").read_text())
    except (OSError, ValueError):
        drawn = {}
    return [s["id"] for s in STAGES
            if drawn.get(s["id"]) != VERSION or not tile(s["id"], root) or
            not preview(s["id"], root)]


# ---- drawn by the native build --------------------------------------------------

def _eye(cam):
    """The panel's camera: (eye x y z, looked at x y z, field of view)."""
    d, y, side, above = cam[:4]
    x = cam[4] if len(cam) > 4 else 0
    a, e = math.radians(side), math.radians(above)
    return (x + d * math.sin(a) * math.cos(e), y + d * math.sin(e),
            d * math.cos(a) * math.cos(e), x, y, 0, 30)


def _picture(w, path, camera, crop, size):
    """The studio camera at `camera`, a picture, cut to `crop` (width,
    height, left, top of the window) and made `size`."""
    w.studio("cam", *("%.3f" % v for v in camera))
    w.step(20)
    shot = w.shot(path.with_suffix(".ppm"))
    subprocess.run(["magick", str(shot), "-crop", "%dx%d+%d+%d" % crop,
                    "+repage", "-filter", "Lanczos", "-resize",
                    "%dx%d!" % size, "-depth", "8", str(path)], check=True,
                   capture_output=True, timeout=60)
    shot.unlink()


def render(root=OUT, only=None, log=print):
    """Draw the stages (`only`: their ids; about 5 seconds each)."""
    sys.path.insert(0, str(ROOT / "tools" / "melee_native"))
    from window import Window   # noqa: E402

    root.mkdir(parents=True, exist_ok=True)
    known = facts(root)
    try:
        drawn = json.loads((root / "drawn.json").read_text())
    except (OSError, ValueError):
        drawn = {}
    width, height = RENDER
    # the card's picture: 16:9 out of the window's middle, a little high
    wide = (width, width * 9 // 16, 0, (height - width * 9 // 16) // 2 - 10)
    with Window(window=RENDER) as w:
        for s in STAGES:
            if only and s["id"] not in only:
                continue
            w.start("fox", None, stage=s["id"])
            w.sleep(0)              # nobody on it, no damage display
            w.step(4)
            reply = w.studio("stage").split()
            if reply[0] == "ok":
                left, right, top, bottom, ledge, _ = (float(v)
                                                      for v in reply[1:7])
                known[s["id"]] = dict(
                    blast=[round(-left, 2), round(right, 2), round(top, 2),
                           round(-bottom, 2)],
                    ledge=round(abs(ledge), 2))
            _picture(w, root / (s["id"] + "-tile.png"), _eye(s["cam"]),
                     (width, height, 0, 0), TILE)
            _picture(w, root / (s["id"] + "-preview.png"), s["view"], wide,
                     PREVIEW)
            w.studio("cam", "off")
            drawn[s["id"]] = VERSION
            (root / "facts.json").write_text(json.dumps(known, indent=1))
            (root / "drawn.json").write_text(json.dumps(drawn, indent=1))
            log("stages: %s" % s["name"])


def render_later(root=OUT):
    """Draw what is missing in a process of its own, which dies with this
    one: a Popen to poll, or None if all is drawn."""
    if not missing(root):
        return None
    return subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "--root",
         str(root)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True, preexec_fn=art._die_with_parent)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--render", action="store_true",
                    help="draw every stage again")
    ap.add_argument("--only", action="append", help="a stage's id")
    ap.add_argument("--root", default=str(OUT), help=argparse.SUPPRESS)
    args = ap.parse_args()
    root = Path(args.root)
    if not ensure(root):
        return 1
    todo = args.only or (None if args.render else missing(root))
    if todo is None or todo:
        render(root, todo)
    print("stages: the pictures and facts are in %s" % root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
