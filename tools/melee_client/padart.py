"""The input display's controller: the owner's picture of a GameCube
controller, made into layers that light up as it is used (the owner,
2026-11-14: "I have a hyper resolution image ... If you can make it look
exactly like this, just slightly transparent with the interactive button
highlights on press I'd be very happy").

    python3 tools/melee_client/padart.py PICTURE    (once; needs Pillow)

PICTURE is that render (3556 by 2000, the controller on white); it is not
in the repository (Nintendo's), but copied to build/ui/pad/source.png, as
the disc's art is read from the owner's own copy. The layers, all of one
size so that they lie on each other exactly (build/ui/pad/):

- BASE: the controller cut from its white, the sticks' caps lifted out
  (under each, the gate's floor, darker toward the middle);
- S, C: the caps, which move with the sticks;
- A B X Y Z ST, DU DD DL DR (the D-pad's arms), L-LIT R-LIT: each part
  brightened with a light round it, shown while held (a trigger as far as
  it is pressed).

The client only reads the layers (ensure()); without them there is no
controller here, and the match shows TM-CE's own (src/host/inputs.c).
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "build" / "ui" / "pad"
SOURCE = OUT / "source.png"
VERSION = 10            # made again when this changes
SOURCE_SIZE = (3556, 2000)
# the part of the picture used: the controller with room for the lights
CROP = (742, 259, 2814, 1739)
WIDTH = 1200            # the layers' width in pixels
SHELL_W = CROP[2] - CROP[0]
SHELL_H = CROP[3] - CROP[1]

# Where each part is in the picture (its pixels): a window to look in and
# what colour it is ("light": the grey-white plastic; the others by hue).
PARTS = {
    "A": ("teal", (2230, 2480, 680, 920)),
    "B": ("red", (2060, 2230, 820, 990)),
    "X": ("light", (2490, 2660, 620, 880)),
    "Y": ("light", (2170, 2440, 480, 680)),
    "ST": ("light", (1720, 1815, 750, 845)),
    "D": ("light", (1320, 1600, 1070, 1350)),
    "L": ("light", (940, 1330, 280, 530)),
    "R": ("light", (2220, 2650, 280, 570)),
    "Z": ("blue", (2240, 2620, 330, 560)),
}
# a point inside each part: of what its colour finds in its window, only
# what is joined to this point is the part (a trigger's window takes in
# the light edge of the shell and the top of Y)
SEEDS = {"A": (2358, 797), "B": (2143, 906), "X": (2562, 742),
         "Y": (2290, 572), "ST": (1774, 793), "D": (1463, 1150),
         "L": (1120, 360), "R": (2470, 360), "Z": (2400, 430)}
DPAD_MIDDLE = (1463, 1218)
# the sticks' caps: middle and radius in the picture's pixels; how far a
# cap goes at full tilt (more than the gate would let it, so it shows)
CAPS = {"S": (1191, 784, 117), "C": (2088, 1220, 84)}
TRAVEL = {"S": 66.0, "C": 56.0}
PRESS = 0.0             # the triggers light; they do not move
# the port's label: its middle and foot, as shares of the box (between the
# logo and START/PAUSE)
LABEL = ((1767 - CROP[0]) / SHELL_W, (668 - CROP[1]) / SHELL_H)

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
    """The layers from the picture."""
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter

    src = Image.open(source).convert("RGB")
    if src.size != SOURCE_SIZE:
        raise ValueError("padart: the picture is %dx%d, not the %dx%d render "
                         "the parts were found on" % (src.size + SOURCE_SIZE))
    k = WIDTH / float(SHELL_W)
    height = round(SHELL_H * k)
    pic = src.crop(CROP).resize((WIDTH, height), Image.LANCZOS)
    rgb = np.asarray(pic).astype(np.float32)

    # the controller: all but the white connected to the corners
    flood = pic.copy()
    for pt in ((0, 0), (WIDTH - 1, 0), (0, height - 1),
               (WIDTH - 1, height - 1)):
        ImageDraw.floodfill(flood, pt, (255, 0, 255), thresh=14)
    f = np.asarray(flood)
    fg = ~((f[..., 0] == 255) & (f[..., 1] == 0) & (f[..., 2] == 255))
    alpha = Image.fromarray((fg * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(0.8))
    alpha = np.asarray(alpha).astype(np.float32) / 255.0

    def window(box):
        x0, x1, y0, y1 = box
        w = np.zeros(fg.shape, bool)
        w[round((y0 - CROP[1]) * k):round((y1 - CROP[1]) * k),
          round((x0 - CROP[0]) * k):round((x1 - CROP[0]) * k)] = True
        return w

    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hi = rgb.max(-1)
    lo = rgb.min(-1)
    colour = {
        # the white plastic, its shaded side too: grey of any lightness
        # (the shell is never this near grey)
        "light": (lo > 110) & (hi - lo < 35),
        "teal": (g > 120) & (g > r + 60) & (b > 100),
        "red": (r > 150) & (r > g + 80) & (r > b + 80),
        "blue": (b > 185) & (b - r > 105) & (abs(g - r) < 15),
    }

    def soft(mask, grow=1.0):
        m = Image.fromarray((mask * 255).astype(np.uint8))
        m = m.filter(ImageFilter.MaxFilter(3)).filter(
            ImageFilter.GaussianBlur(grow))
        return np.asarray(m).astype(np.float32) / 255.0

    def save(name, out_rgb, out_a):
        a = np.clip(out_a, 0, 1)
        # (nothing where nothing shows: the pictures stay small)
        img = np.dstack([np.clip(out_rgb, 0, 255) * (a > 0)[..., None],
                         a * 255]).astype(np.uint8)
        Image.fromarray(img, "RGBA").save(path(name))

    def lit(mask):
        """The part lit up: brightened toward white, a bright rim round it
        and a glow beyond, strong enough to read at the display's size."""
        part = soft(mask)
        m = Image.fromarray((mask * 255).astype(np.uint8))
        # (the display is about an eighth of the layers' size: a rim of
        # 10 pixels shows as one or two)
        rim = np.asarray(m.filter(ImageFilter.MaxFilter(21)).filter(
            ImageFilter.GaussianBlur(2))).astype(np.float32) / 255.0
        halo = np.asarray(m.filter(ImageFilter.MaxFilter(33)).filter(
            ImageFilter.GaussianBlur(14))).astype(np.float32) / 255.0
        bright = rgb * 0.55 + 255.0 * 0.45
        glow = np.array(GLOW, np.float32)
        # back to front: the glow, the rim, the part
        a = halo * 0.9
        out = glow[None, None, :] * np.ones_like(rgb)
        a = rim + a * (1 - rim)
        a = part + a * (1 - part)
        out = (bright * part[..., None] +
               glow * (1 - part)[..., None])
        return out, a * alpha

    masks = {}
    for name, (kind, box) in PARTS.items():
        masks[name] = colour[kind] & fg & window(box)
        if name in SEEDS:
            # (filled in colour: Pillow's fill leaves a one-channel
            # picture as it was)
            m = Image.fromarray((masks[name] * 255).astype(np.uint8)).convert(
                "RGB")
            sx = round((SEEDS[name][0] - CROP[0]) * k)
            sy = round((SEEDS[name][1] - CROP[1]) * k)
            if m.getpixel((sx, sy))[0] != 255:
                # (on a printed letter: the part's nearest pixel)
                ys, xs = np.nonzero(masks[name])
                if len(xs) == 0:
                    raise ValueError("padart: %s not found" % name)
                i = int(np.argmin((xs - sx) ** 2 + (ys - sy) ** 2))
                sx, sy = int(xs[i]), int(ys[i])
            ImageDraw.floodfill(m, (sx, sy), (128, 0, 0))
            part = Image.fromarray(
                ((np.asarray(m)[..., 0] == 128) * 255).astype(np.uint8))
            # closed: the printed letters and the seams in it filled
            part = part.filter(ImageFilter.MaxFilter(9)).filter(
                ImageFilter.MinFilter(9))
            masks[name] = (np.asarray(part) > 127) & fg
    # the D-pad's arms, by where they are from its middle
    mx = (DPAD_MIDDLE[0] - CROP[0]) * k
    my = (DPAD_MIDDLE[1] - CROP[1]) * k
    yy, xx = np.mgrid[0:height, 0:WIDTH]
    dx, dy = xx - mx, yy - my
    arm = {"DU": (dy < 0) & (abs(dx) < -dy), "DD": (dy > 0) & (abs(dx) < dy),
           "DL": (dx < 0) & (abs(dy) < -dx), "DR": (dx > 0) & (abs(dy) < dx)}
    for name, where in arm.items():
        masks[name] = masks["D"] & where & (np.hypot(dx, dy) > 5 * k)

    OUT.mkdir(parents=True, exist_ok=True)
    base = rgb.copy()
    # the caps lifted out: each a layer of its own; under it the gate's
    # floor (the colour just outside the cap, along the same line from its
    # middle), darker toward the middle, where the stick goes in
    for name, (cx, cy, rad) in CAPS.items():
        cx, cy, rad = (cx - CROP[0]) * k, (cy - CROP[1]) * k, rad * k
        d = np.hypot(xx - cx, yy - cy)
        cap_a = np.clip(rad + 1.0 - d, 0, 1)
        save(name, rgb, cap_a * alpha)
        inside = d < rad + 1.5
        ang = np.arctan2(yy - cy, xx - cx)
        reach = rad + 4.0
        ox = np.clip(np.round(cx + reach * np.cos(ang)), 0,
                     WIDTH - 1).astype(int)
        oy = np.clip(np.round(cy + reach * np.sin(ang)), 0,
                     height - 1).astype(int)
        floor = rgb[oy, ox] * (0.55 + 0.45 * np.clip(d / rad, 0, 1))[..., None]
        base[inside] = floor[inside]
    save("BASE", base, alpha)
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
