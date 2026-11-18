"""The input display's controller: the owner's drawing of a GameCube
controller, made into layers that light up as it is used (the owner,
2026-11-14: "make it look exactly like this, just slightly transparent with
the interactive button highlights on press"; then, of a render cut from a
white background, "it looks a bit choppy ... let's try it with that
instead": a drawing on a transparent background, its parts outlined).

    python3 tools/melee_client/padart.py PICTURE    (once; needs Pillow)

PICTURE is that drawing (600 by 425, transparent around it), kept in the
repository as tools/melee_client/pad/source.png with the layers made from
it (the owner, 2026-11-17: "build/ui/pad isn't pushed which is need for the
input display to work, can you commit and push that"), so a fresh clone
shows the controller with nothing to make; this script makes them again
when the drawing or VERSION changes. The layers, all of one size so that
they lie on each other exactly, made at twice the drawing's size so that
the lights' rims are smooth:

- BASE: the drawing, its edge as drawn, the sticks' caps lifted out
  (under each, its gate's colour);
- S, C: the caps, which move with the sticks;
- A B X Y Z ST, DU DD DL DR (the D-pad's arms), L-LIT R-LIT: each part
  brightened with a white rim and a glow, shown while held (a trigger as
  far as it is pressed).

Each part is found from a point inside it, filled out to its black
outline. The client only reads the layers (ensure()); without them there
is no controller here, and the match shows TM-CE's own
(src/host/inputs.c).
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tools" / "melee_client" / "pad"    # in the repository
SOURCE = OUT / "source.png"
VERSION = 13            # made again when this changes
SOURCE_SIZE = (600, 425)
MARGIN = 12             # room round the drawing for the lights
SCALE = 2               # the layers' pixels per the drawing's
SHELL_W = SOURCE_SIZE[0] + 2 * MARGIN     # the box, in the drawing's pixels
SHELL_H = SOURCE_SIZE[1] + 2 * MARGIN

# a point inside each part (the drawing's pixels): what is joined to it
# inside its black outline is the part
SEEDS = {"A": (470, 140), "B": (412, 185), "X": (565, 125),
         "Y": (460, 85), "ST": (300, 160), "D": (185, 290),
         "L": (80, 40), "R": (520, 40), "Z": (495, 38)}
DPAD_MIDDLE = (198.5, 296)
# the sticks' caps: middle and radius (with its outline); the colour under
# each (its gate's); how far a cap goes at full tilt (more than its gate
# would let it, so that it shows)
CAPS = {"S": (110.5, 157, 44.5), "C": (400, 296, 29.5)}
UNDER = {"S": (90, 90, 90), "C": (194, 194, 0)}
TRAVEL = {"S": 16.0, "C": 18.0}
PRESS = 0.0             # the triggers light; they do not move
# the port's label: its middle and foot, as shares of the box (above
# START/PAUSE)
LABEL = ((300 + MARGIN) / SHELL_W, (106 + MARGIN) / SHELL_H)

LIT = ("A", "B", "X", "Y", "Z", "ST", "DU", "DD", "DL", "DR")
LAYERS = ("BASE", "L-LIT", "R-LIT") + LIT + ("S", "C")
GLOW = (255, 255, 255)


def path(name):
    return OUT / ("%s.png" % name.lower())


def ensure():
    """{layer: picture} if they have been made (and are of this VERSION),
    else {} (made from source.png when Pillow is there)."""
    stamp = OUT / "VERSION"
    if stamp.exists() and stamp.read_text().strip() == str(VERSION) and \
            all(path(n).exists() for n in LAYERS):
        return {n: path(n) for n in LAYERS}
    if SOURCE.exists():
        try:
            make(SOURCE)
            return {n: path(n) for n in LAYERS}
        except ImportError:
            print("padart: Pillow is needed to make the controller's "
                  "layers (pip install pillow)", file=sys.stderr)
    return {}


def make(source):
    """The layers from the drawing."""
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter

    src = Image.open(source).convert("RGBA")
    if src.size != SOURCE_SIZE:
        raise ValueError("padart: the drawing is %dx%d, not the %dx%d one "
                         "the parts were found on" % (src.size + SOURCE_SIZE))
    canvas = Image.new("RGBA", (SHELL_W, SHELL_H), (0, 0, 0, 0))
    canvas.paste(src, (MARGIN, MARGIN))
    a = np.asarray(canvas).astype(np.int32)
    # inside an outline: not black, not the clear round it
    inside = (a[..., :3].max(-1) > 45) & (a[..., 3] > 128)
    flat = Image.fromarray((inside * 255).astype(np.uint8)).convert("RGB")

    def region(seed):
        m = flat.copy()
        x, y = seed[0] + MARGIN, seed[1] + MARGIN
        if m.getpixel((x, y))[0] != 255:
            raise ValueError("padart: %r is on an outline" % (seed,))
        ImageDraw.floodfill(m, (x, y), (128, 0, 0))
        return np.asarray(m)[..., 0] == 128

    def grow(mask, n=3):
        """With its outline (and on to the part's whole width)."""
        return np.asarray(Image.fromarray((mask * 255).astype(np.uint8))
                          .filter(ImageFilter.MaxFilter(n))) > 127

    masks = {n: grow(region(s)) for n, s in SEEDS.items()}
    yy, xx = np.mgrid[0:SHELL_H, 0:SHELL_W]
    dx = xx - (DPAD_MIDDLE[0] + MARGIN)
    dy = yy - (DPAD_MIDDLE[1] + MARGIN)
    arm = {"DU": (dy < 0) & (abs(dx) < -dy), "DD": (dy > 0) & (abs(dx) < dy),
           "DL": (dx < 0) & (abs(dy) < -dx), "DR": (dx > 0) & (abs(dy) < dx)}
    for name, where in arm.items():
        masks[name] = masks["D"] & where & (np.hypot(dx, dy) > 5)

    # twice the size: the drawing smooth, the masks with it
    W, H = SHELL_W * SCALE, SHELL_H * SCALE
    big = canvas.resize((W, H), Image.LANCZOS)
    rgba = np.asarray(big).astype(np.float32)
    rgb, alpha = rgba[..., :3], rgba[..., 3] / 255.0

    def up(mask):
        m = Image.fromarray((mask * 255).astype(np.uint8)).resize(
            (W, H), Image.BILINEAR)
        return np.asarray(m).astype(np.float32) / 255.0

    def save(name, out_rgb, out_a):
        a = np.clip(out_a, 0, 1)
        # (nothing where nothing shows: the pictures stay small)
        img = np.dstack([np.clip(out_rgb, 0, 255) * (a > 0)[..., None],
                         a * 255]).astype(np.uint8)
        Image.fromarray(img, "RGBA").save(path(name))

    def lit(mask):
        """The part lit up: brightened toward white, a bright rim round it
        and a glow beyond, strong enough to read at the display's size
        (about an eighth of the layers')."""
        part = up(mask)
        m = Image.fromarray((part * 255).astype(np.uint8))
        rim = np.asarray(m.filter(ImageFilter.MaxFilter(13)).filter(
            ImageFilter.GaussianBlur(1.5))).astype(np.float32) / 255.0
        halo = np.asarray(m.filter(ImageFilter.MaxFilter(25)).filter(
            ImageFilter.GaussianBlur(12))).astype(np.float32) / 255.0
        bright = rgb * 0.55 + 255.0 * 0.45
        glow = np.array(GLOW, np.float32)
        a = halo * 0.9
        a = rim + a * (1 - rim)
        a = part + a * (1 - part)
        out = bright * part[..., None] + glow * (1 - part)[..., None]
        return out, a

    OUT.mkdir(parents=True, exist_ok=True)
    base_rgb = rgb.copy()
    gy, gx = np.mgrid[0:H, 0:W]
    for name, (cx, cy, rad) in CAPS.items():
        cx = (cx + MARGIN) * SCALE
        cy = (cy + MARGIN) * SCALE
        rad *= SCALE
        d = np.hypot(gx - cx, gy - cy)
        cap_a = np.clip(rad + 1.0 - d, 0, 1)
        save(name, rgb, cap_a * alpha)
        # under it, its gate's colour (plain: the cap is see-through, and
        # anything drawn under it shows through)
        fill = np.broadcast_to(np.array(UNDER[name], np.float32), rgb.shape)
        inside_cap = d < rad + 2.5 * SCALE   # (its outline's last trace)
        base_rgb[inside_cap] = fill[inside_cap]
    save("BASE", base_rgb, alpha)
    for name in LIT:
        out, a = lit(masks[name])
        save(name, out, a)
    for t in ("L", "R"):
        out, a = lit(masks[t])
        save(t + "-LIT", out, a)
    (OUT / "VERSION").write_text(str(VERSION))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        OUT.mkdir(parents=True, exist_ok=True)
        if Path(sys.argv[1]).resolve() != SOURCE.resolve():
            shutil.copyfile(sys.argv[1], SOURCE)
        make(SOURCE)
    made = ensure()
    print("%d layers in %s" % (len(made), OUT))
    sys.exit(0 if len(made) == len(LAYERS) else 1)
