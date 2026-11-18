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
- Its blast zones, ledge and camera limits, read from the running game as
  it draws it ("studio stage": the game's own getters); the camera limits
  frame the stages not set by hand.

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
VERSION = 3    # of the pictures drawn: a change draws them again
BATCH = 4      # stages drawn in one window: the 32-bit window build's
               # graphics memory gives out after some 25 stage loads

# In the order of the stage select. `logo`: its name logo's place among the
# disc's 30 (by where they are in the file: the vanilla select's order).
# `cam`: the studio camera for the panel, (distance, height looked at,
# from the side in degrees, from above in degrees, and optionally where
# along the stage it looks: left of the middle puts the stage further
# right in the panel); `view`: for the card, straight on (eye, looked at,
# field of view).
LEGAL = [
    dict(legal=True, id="battlefield", name="Battlefield", logo=24,
         cam=(225, 10, -22, 24, -16), view=(0, 40, 245, 0, 18, 0, 30)),
    dict(legal=True, id="final-destination", name="Final Destination", logo=25,
         cam=(330, -12, -22, 24), view=(0, 38, 285, 0, -6, 0, 30)),
    dict(legal=True, id="dream-land", name="Dream Land", logo=26,
         cam=(265, 18, -22, 24), view=(0, 50, 300, 0, 20, 0, 30)),
    dict(legal=True, id="yoshis-story", name="Yoshi's Story", logo=8,
         cam=(215, 8, -22, 24), view=(0, 40, 250, 0, 10, 0, 30)),
    dict(legal=True, id="fountain-of-dreams", name="Fountain of Dreams", logo=10,
         cam=(275, 10, -22, 24), view=(0, 45, 260, 0, 12, 0, 30)),
    dict(legal=True, id="pokemon-stadium", name="Pokémon Stadium", logo=14,
         cam=(275, 6, -22, 24), view=(0, 50, 320, 0, 10, 0, 30)),
]

# The rest of the game's VS select (the owner, 2026-11-14: "add support for
# all stages in melee in the same way we supported the legal stages"), in
# its own order. `cam` and `view` None: framed from the stage's camera
# limits as the game reads them (`_auto`; `zoom` above 1 from further,
# `wait` frames before the pictures, for a stage that arrives).
OTHERS = [
    dict(id="peachs-castle", name="Peach's Castle", logo=0),
    dict(id="rainbow-cruise", name="Rainbow Cruise", logo=1),
    dict(id="kongo-jungle", name="Kongo Jungle", logo=2),
    dict(id="jungle-japes", name="Jungle Japes", logo=3),
    dict(id="great-bay", name="Great Bay", logo=4),
    dict(id="hyrule-temple", name="Hyrule Temple", logo=5),
    dict(id="brinstar", name="Brinstar", logo=6),
    dict(id="brinstar-depths", name="Brinstar Depths", logo=7),
    dict(id="yoshis-island", name="Yoshi's Island", logo=9),
    dict(id="green-greens", name="Green Greens", logo=11),
    dict(id="corneria", name="Corneria", logo=12, zoom=1.35),
    dict(id="venom", name="Venom", logo=13, zoom=1.35),
    dict(id="poke-floats", name="Poké Floats", logo=15, wait=300,
         # its balloons float low in its camera's limits: set by hand
         cam_set=((560, -70, -22, 24, 0), (0, -40, 600, 0, -70, 0, 30))),
    dict(id="mute-city", name="Mute City", logo=16),
    dict(id="big-blue", name="Big Blue", logo=17),
    dict(id="onett", name="Onett", logo=18),
    dict(id="fourside", name="Fourside", logo=19),
    dict(id="mushroom-kingdom", name="Mushroom Kingdom", logo=20),
    dict(id="mushroom-kingdom-ii", name="Mushroom Kingdom II", logo=21),
    dict(id="icicle-mountain", name="Icicle Mountain", logo=22, zoom=1.4),
    dict(id="flat-zone", name="Flat Zone", logo=23, zoom=1.5),
    dict(id="yoshis-island-64", name="Yoshi's Island (64)", logo=27),
    dict(id="kongo-jungle-64", name="Kongo Jungle (64)", logo=28),
]
for _s in OTHERS:
    _cam, _view = _s.pop("cam_set", (None, None))
    _s.update(legal=False, cam=_cam, view=_view)
# Every stage, in the game's own select order (its name logos' order).
STAGES = sorted(LEGAL + OTHERS, key=lambda s: s["logo"])
BY_ID = {s["id"]: s for s in STAGES}
def name(ident):
    """A stage's name."""
    if ident in BY_ID:
        return BY_ID[ident]["name"]
    return ident.replace("-", " ").title()
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


def _auto(bounds, zoom=1.0):
    """The panel's camera and the card's view for a stage framed from its
    camera limits (left, right, top, bottom: the area the match camera
    keeps to), as the six legal stages' hand-set ones come out: looked at
    a little over a third of the way up, from about the width away (a
    tall stage from its height)."""
    left, right, top, bottom = bounds
    width = max(right - left, 1.3 * (top - bottom)) * zoom
    x = (left + right) / 2
    cam = (1.15 * width, bottom + 0.36 * (top - bottom), -22, 24, x)
    y = bottom + 0.38 * (top - bottom)
    view = (x, y + 25, 1.05 * width, x, y, 0, 30)
    return cam, view


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
    """Draw the stages (`only`: their ids; about 5 seconds each), BATCH to
    a window."""
    todo = [s for s in STAGES if not only or s["id"] in only]
    for i in range(0, len(todo), BATCH):
        _render(root, [s["id"] for s in todo[i:i + BATCH]], log)


def _render(root, only, log):
    sys.path.insert(0, str(ROOT / "tools" / "melee_native"))
    from window import Window   # noqa: E402

    root.mkdir(parents=True, exist_ok=True)
    known = facts(root)
    try:
        drawn = json.loads((root / "drawn.json").read_text())
    except (OSError, ValueError):
        drawn = {}
    # the game draws at 4:3 at the window's left: only that is cut from
    # (the window's whole width left a black strip down the pictures'
    # right side)
    width = min(RENDER[0], round(RENDER[1] * 4 / 3))
    height = RENDER[1]
    # the panel's picture: its shape out of the game's, a band across it
    tall = round(width * TILE[1] / TILE[0])
    panel = (width, tall, 0, (height - tall) // 2)
    # the card's picture: 16:9 out of the game's middle, a little high
    wide = (width, width * 9 // 16, 0, (height - width * 9 // 16) // 2 - 10)
    with Window(window=RENDER) as w:
        for s in STAGES:
            if only and s["id"] not in only:
                continue
            w.start("fox", None, stage=s["id"])
            w.sleep(0)              # nobody on it, no damage display
            w.step(s.get("wait", 4))
            reply = w.studio("stage").split()
            cam, view = s["cam"], s["view"]
            if reply[0] == "ok":
                v = [float(x) for x in reply[1:11]]
                left, right, top, bottom, ledge = v[:5]
                has_ledge = len(reply) > 11 and reply[11] == "1"
                known[s["id"]] = dict(
                    blast=[round(-left, 2), round(right, 2), round(top, 2),
                           round(-bottom, 2)],
                    ledge=round(abs(ledge), 2) if has_ledge else None,
                    camera=[round(c, 2) for c in v[6:10]])
                if cam is None or view is None:
                    auto = _auto(v[6:10], s.get("zoom", 1.0))
                    cam, view = cam or auto[0], view or auto[1]
            _picture(w, root / (s["id"] + "-tile.png"), _eye(cam), panel,
                     TILE)
            _picture(w, root / (s["id"] + "-preview.png"), view, wide,
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
    if sys.platform == "win32":
        # Drawn on a virtual display and photographed from it (window.shot),
        # which Windows does not have yet: each panel keeps the stage's name
        # logo (docs/ai/windows.md).
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
