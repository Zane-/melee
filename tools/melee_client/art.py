"""The character art the client shows: the game's own select-screen
portraits (every costume) and series emblems, read off the disc; and Sheik,
who has none (the game shows her in Zelda's slot), drawn from her model by
the window build.

    python tools/melee_client/art.py            # what is missing
    python tools/melee_client/art.py --sheik    # draw Sheik again

Everything goes to build/ui/art (git-ignored): the art is Nintendo's, read
from the owner's disc on their machine, and never part of the repository.

Stock icons (IfAll.usd, stock_icons): the HUD's texture animation of 130
24x24 CI4 images and palettes, a frame for each character and costume as
the game picks it (gm_80168B34: the character's place, Sheik 25, plus 30
for each costume), the frame's image and palette read from the
animation's keys.

Where it is on the disc (MnSlChr.usd): one texture animation of 118 frames,
136x188 CI8 with an RGB5A3 palette each; frames 0-24 are the default
costumes in the game's character order without Sheik, then costumes 1, 2
and 3 in the same order, then the fifth and sixth (EXTRA). The emblems are
the 13 I4 80x64 textures, white on black, here white with that as alpha.

Sheik (render_sheik): a match with her alone; the stage, the HUD and the
effects left undrawn, the camera close (src/host/studio.c); a picture on
black and one on white. Where the two differ is how much of the background
shows through, which gives her outline with its soft edges. Cropped and
shadowed as the game's own portraits are (the shadow measured on them: 10
pixels left, 9 down, black at about 45%).
"""
import argparse
import json
import struct
import subprocess
import sys
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "build" / "ui" / "art"
VERSION = 2   # of what is written here: a change makes it all again
STOCK_VERSION = 3   # the stock icons', apart (Sheik's portraits stay)
# the stock icons are written this many times their 24 pixels, each pixel a
# square: drawn at 24 dp on a large window, they are made smaller, not
# blurred larger ("the mode icons are blurry!", the owner, 2026-11-14)
STOCK_SCALE = 3
W, H = 136, 188
# Each portrait is written with this much transparent border: the renderer
# wraps a picture's edges round, which drew a line of the bottom edge (a
# cut through the body) over the top of the head.
PAD = 2

# The game's character order (external ids) without Sheik.
ORDER = ["captain-falcon", "donkey-kong", "fox", "mr-game-and-watch",
         "kirby", "bowser", "link", "luigi", "mario", "marth", "mewtwo",
         "ness", "peach", "pikachu", "ice-climbers", "jigglypuff", "samus",
         "yoshi", "zelda", "falco", "young-link", "dr-mario", "roy",
         "pichu", "ganondorf"]
# frames 100-117: fifth costumes, then three sixth, then five more fifth
EXTRA = ["captain-falcon", "donkey-kong", "kirby", "link", "mario", "samus",
         "yoshi", "zelda", "young-link", "dr-mario", "captain-falcon",
         "kirby", "yoshi", "peach", "marth", "jigglypuff", "ganondorf",
         "roy"]
# by where their pictures are in the file
EMBLEMS = ["game-and-watch", "f-zero", "donkey-kong", "fire-emblem",
           "star-fox", "ice-climber", "kirby", "mushroom", "earthbound",
           "pokemon", "metroid", "yoshi", "zelda"]
SHEIK_COSTUMES = 5


def disc_file(name):
    for d in (ROOT / "build" / "disc" / "files",
              ROOT / "orig" / "GALE01" / "files"):
        if (d / name).exists():
            return d / name
    raise FileNotFoundError("no %s: extract the disc into build/disc "
                            "(docs: build-melee skill)" % name)


# ---- pictures --------------------------------------------------------------------

def write_png(path, rgba):
    """`rgba`: h x w x 4 uint8."""
    h, w = rgba.shape[:2]
    raw = b"".join(b"\0" + rgba[y].tobytes() for y in range(h))

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data +
                struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(
        ">IIBBBBB", w, h, 8, 6, 0, 0, 0)) +
        chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))
    tmp.replace(path)     # never half a file, for a reader at the same time


def write_portrait(path, rgba):
    out = np.zeros((H + 2 * PAD, W + 2 * PAD, 4), np.uint8)
    out[PAD:PAD + H, PAD:PAD + W] = rgba
    write_png(path, out)


def read_ppm(path):
    data = Path(path).read_bytes()
    parts, at = [], 0
    while len(parts) < 4:
        while data[at:at + 1].isspace():
            at += 1
        if data[at:at + 1] == b"#":
            at = data.index(b"\n", at)
            continue
        end = at
        while not data[end:end + 1].isspace():
            end += 1
        parts.append(data[at:end])
        at = end
    w, h, top = int(parts[1]), int(parts[2]), int(parts[3])
    if top > 255:     # ImageMagick writes 16 bits a sample
        px = np.frombuffer(data, ">u2", w * h * 3, at + 1)
        return (px.astype(np.uint32) * 255 // top).astype(
            np.uint8).reshape(h, w, 3)
    return np.frombuffer(data, np.uint8, w * h * 3, at + 1).reshape(h, w, 3)


# ---- the archive -----------------------------------------------------------------

class Archive:
    def __init__(self, path):
        buf = Path(path).read_bytes()
        _, size, nrel, _, _ = struct.unpack_from(">5I", buf, 0)
        self.d = buf[0x20:0x20 + size]
        self.rel = set(struct.unpack_from(">%dI" % nrel, buf, 0x20 + size))

    def u32(self, o):
        return struct.unpack_from(">I", self.d, o)[0]

    def image(self, o):
        """(data offset, width, height, format) of an HSD_ImageDesc."""
        w, h = struct.unpack_from(">HH", self.d, o + 4)
        return self.u32(o), w, h, self.u32(o + 8)

    def is_image(self, o):
        if o % 4 or o + 0x18 > len(self.d) or o not in self.rel:
            return False
        p, w, h, fmt = self.image(o)
        return 0 < w <= 1024 and 0 < h <= 1024 and fmt in (0, 9) and \
            p < len(self.d)


def rgb5a3(v):
    v = v.astype(np.uint32)
    opaque = (v & 0x8000) != 0
    r5, g5, b5 = (v >> 10) & 31, (v >> 5) & 31, v & 31
    a3, r4, g4, b4 = (v >> 12) & 7, (v >> 8) & 15, (v >> 4) & 15, v & 15
    out = np.empty(v.shape + (4,), np.uint8)
    out[..., 0] = np.where(opaque, (r5 << 3) | (r5 >> 2), r4 * 17)
    out[..., 1] = np.where(opaque, (g5 << 3) | (g5 >> 2), g4 * 17)
    out[..., 2] = np.where(opaque, (b5 << 3) | (b5 >> 2), b4 * 17)
    out[..., 3] = np.where(opaque, 255, (a3 << 5) | (a3 << 2) | (a3 >> 1))
    return out


def ci8(data, w, h, palette):
    """8x4 blocks of palette indices."""
    bx, by = (w + 7) // 8, (h + 3) // 4
    idx = np.frombuffer(data, np.uint8, bx * by * 32).reshape(by, bx, 4, 8)
    idx = idx.transpose(0, 2, 1, 3).reshape(by * 4, bx * 8)[:h, :w]
    return palette[idx]


def i4(data, w, h):
    """8x8 blocks of 4-bit intensities, the high half first."""
    bx, by = (w + 7) // 8, (h + 7) // 8
    b = np.frombuffer(data, np.uint8, bx * by * 32).reshape(by, bx, 8, 4)
    px = np.stack([b >> 4, b & 15], -1).reshape(by, bx, 8, 8)
    return (px.transpose(0, 2, 1, 3).reshape(by * 8, bx * 8)[:h, :w] * 17
            ).astype(np.uint8)


def portraits(arc):
    """[(frame, rgba)] of the select screen's portraits."""
    for r in sorted(arc.rel):
        if r + 12 > len(arc.d) or (r + 4) not in arc.rel:
            continue
        images, tluts = arc.u32(r), arc.u32(r + 4)
        n, m = struct.unpack_from(">HH", arc.d, r + 8)
        if n != 118 or m != 118 or images + 4 * n > len(arc.d):
            continue
        descs = [arc.u32(images + 4 * i) for i in range(n)]
        if not all(arc.is_image(o) and arc.image(o)[1:] == (W, H, 9)
                   for o in descs):
            continue
        out = []
        for k, o in enumerate(descs):
            tlut = arc.u32(tluts + 4 * k)
            lut, count = arc.u32(tlut), struct.unpack_from(
                ">H", arc.d, tlut + 12)[0]
            palette = rgb5a3(np.frombuffer(arc.d, ">u2", count, lut))
            p = arc.image(o)[0]
            out.append((k, ci8(arc.d[p:p + W * H], W, H, palette)))
        return out
    raise ValueError("no portraits in this file")


def emblems(arc):
    """{series: rgba} from the 13 80x64 emblems."""
    found = {}
    for r in arc.rel:
        o = arc.u32(r) if r + 4 <= len(arc.d) else None
        if o is not None and arc.is_image(o):
            p, w, h, fmt = arc.image(o)
            if (w, h, fmt) == (80, 64, 0):
                found[p] = o
    if len(found) != len(EMBLEMS):
        raise ValueError("%d emblems, not %d" % (len(found), len(EMBLEMS)))
    out = {}
    for name, p in zip(EMBLEMS, sorted(found)):
        a = i4(arc.d[p:p + 80 * 64 // 2], 80, 64)
        rgba = np.full((64, 80, 4), 255, np.uint8)
        rgba[..., 3] = a
        out[name] = rgba
    return out


def ci4(d, p, w, h, palette):
    """8x8 blocks of 4-bit palette indices, the high half first."""
    bx, by = (w + 7) // 8, (h + 7) // 8
    b = np.frombuffer(d, np.uint8, bx * by * 32, p).reshape(by, bx, 8, 4)
    px = np.stack([b >> 4, b & 15], -1).reshape(by, bx, 8, 8)
    return palette[px.transpose(0, 2, 1, 3).reshape(by * 8, bx * 8)[:h, :w]]


def fobj_values(arc, fobj):
    """{frame: value} at each key of an FObj (HSD fobj.c's key stream:
    a header of operation and count, then each key's value and wait); a
    frame between keys holds the last key's value (the stock icons' keys
    are constant)."""
    d = arc.d
    length, start = struct.unpack_from(">If", d, fobj + 4)
    fv = d[fobj + 13]
    p, end = arc.u32(fobj + 16), arc.u32(fobj + 16) + length
    kind, shift = fv & 0xE0, fv & 0x1F

    def value():
        nonlocal p
        fmt, size = {0x00: (">f", 4), 0x20: (">h", 2), 0x40: (">H", 2),
                     0x60: (">b", 1), 0x80: (">B", 1)}[kind]
        v = struct.unpack_from(fmt, d, p)[0]
        p += size
        return v if kind == 0 else v / float(1 << shift)

    def wait():
        nonlocal p
        w, sh = 0, 0
        while True:
            b = d[p]
            p += 1
            w |= (b & 0x7F) << sh
            sh += 7
            if not b & 0x80:
                return w

    out, t = {}, start
    while p < end and d[p] & 0x0F:
        op = d[p] & 0x0F
        n, sh = (d[p] >> 4) & 7, 3
        while d[p] & 0x80:
            p += 1
            n += (d[p] & 0x7F) << sh
            sh += 7
        p += 1
        for _ in range(n + 1):
            if op in (1, 2, 3):           # constant, linear, spline 0
                out[t] = value()
                t += wait()
            elif op == 4:                 # spline: value, slope, wait
                out[t] = value()
                value()
                t += wait()
            elif op == 5:                 # a slope alone
                value()
            elif op == 6:                 # a value alone
                out[t] = value()
    return out


def held(keys, frame):
    """The value a constant track holds at `frame`."""
    return keys[max(k for k in keys if k <= frame)]


STOCK = 24


def stock_icons(arc, count):
    """{(character, costume): rgba} of the HUD's stock icons; `count`:
    {character: costumes}."""
    d = arc.d
    for r in sorted(arc.rel):
        ta = r - 0xC                # a TexAnim: its image table's field
        if ta < 0 or ta + 0x18 > len(d) or (ta + 0x10) not in arc.rel or \
                (ta + 8) not in arc.rel:
            continue
        n, m = struct.unpack_from(">HH", d, ta + 0x14)
        if n != 130 or m != 130:
            continue
        images, tluts = arc.u32(ta + 0xC), arc.u32(ta + 0x10)
        first = arc.u32(images)
        if arc.image(first)[1:] != (STOCK, STOCK, 8):
            continue
        aobj = arc.u32(ta + 8)
        tracks, f = {}, arc.u32(aobj + 8)
        while f:
            tracks[d[f + 12]] = fobj_values(arc, f)
            f = arc.u32(f) if f in arc.rel else 0
        img_keys, tlut_keys = tracks[1], tracks[10]   # TIMG, TCLT
        out = {}
        for cid, costumes in count.items():
            base = 25 if cid == "sheik" else ORDER.index(cid)
            for c in range(costumes):
                frame = base + 30 * c
                o = arc.u32(images + 4 * int(held(img_keys, frame)))
                t = arc.u32(tluts + 4 * int(held(tlut_keys, frame)))
                p, w, h, fmt = arc.image(o)
                lut = arc.u32(t)
                k = struct.unpack_from(">H", d, t + 12)[0]
                palette = rgb5a3(np.frombuffer(d, ">u2", k, lut))
                out[(cid, c)] = ci4(d, p, w, h, palette)
        return out
    raise ValueError("no stock icons in this file")


def costume_of_frame():
    where, count = {}, {c: 0 for c in ORDER}
    for k in range(100):
        c = ORDER[k % 25]
        where[k] = (c, count[c])
        count[c] += 1
    for i, c in enumerate(EXTRA):
        where[100 + i] = (c, count[c])
        count[c] += 1
    return where, count


# ---- what is here ----------------------------------------------------------------

def portrait(cid, n=0, root=ART):
    """The picture of character `cid` in costume `n`, or None."""
    path = root / "portrait" / ("%s-%d.png" % (cid, n))
    return path if path.exists() else None


def stock(cid, n=0, root=ART, grey=False):
    """Character `cid`'s stock icon in costume `n` (the first costume's
    if that one has none; `grey`: without its colour), or None."""
    for k in (n, 0):
        path = root / "stock" / ("%s-%d%s.png" % (cid, k,
                                                  "-grey" if grey else ""))
        if path.exists():
            return path
    return None


def emblem(series, root=ART):
    path = root / "emblem" / (series + ".png")
    return path if path.exists() else None


def costumes(root=ART):
    """{character: how many costumes it has a picture of}."""
    try:
        return json.loads((root / "costumes.json").read_text())
    except (OSError, ValueError):
        return {}


def extracted(root=ART):
    try:
        return json.loads((root / "stamp.json").read_text()) == \
            {"version": VERSION}
    except (OSError, ValueError):
        return False


def extract(root=ART):
    """The disc's portraits and emblems, into `root` (a second or two)."""
    arc = Archive(disc_file("MnSlChr.usd"))
    where, count = costume_of_frame()
    for k, rgba in portraits(arc):
        cid, n = where[k]
        write_portrait(root / "portrait" / ("%s-%d.png" % (cid, n)), rgba)
    for name, rgba in emblems(arc).items():
        write_png(root / "emblem" / (name + ".png"), rgba)
    count["sheik"] = 0      # drawn again, to what this version writes
    (root / "costumes.json").write_text(json.dumps(count, indent=1))
    (root / "stamp.json").write_text(json.dumps({"version": VERSION}))


def extract_stocks(root=ART):
    """The HUD's stock icons, every character and costume, into `root`."""
    where, count = costume_of_frame()
    count["sheik"] = SHEIK_COSTUMES
    for (cid, n), rgba in stock_icons(Archive(disc_file("IfAll.usd")),
                                      count).items():
        k = STOCK_SCALE
        big = rgba.repeat(k, 0).repeat(k, 1)
        out = np.zeros((STOCK * k + 2 * PAD, STOCK * k + 2 * PAD, 4),
                       np.uint8)
        out[PAD:PAD + STOCK * k, PAD:PAD + STOCK * k] = big
        write_png(root / "stock" / ("%s-%d.png" % (cid, n)), out)
        # and without its colour: a side with no stock in a mode's score
        # (Tug of War: "a desaturated stock when the player has 0 score so
        # it is still easy to tell which % is who's", the owner)
        grey = out.copy()
        lum = (out[..., 0] * 0.3 + out[..., 1] * 0.59 + out[..., 2] * 0.11)
        grey[..., :3] = np.clip(lum * 0.85 + 20, 0, 255).astype(
            np.uint8)[..., None]
        write_png(root / "stock" / ("%s-%d-grey.png" % (cid, n)), grey)
    (root / "stock" / "VERSION").write_text(str(STOCK_VERSION))


def ensure(root=ART):
    """The disc's art extracted, if it is not yet. True if it is there."""
    try:
        if not extracted(root):
            extract(root)
        stamp = root / "stock" / "VERSION"
        if not stamp.exists() or stamp.read_text().strip() != \
                str(STOCK_VERSION):
            extract_stocks(root)
    except (OSError, ValueError) as e:
        print("art: %s" % e, file=sys.stderr)
        return False
    return True


def sheik_missing(root=ART):
    return costumes(root).get("sheik", 0) < SHEIK_COSTUMES


# ---- Sheik -------------------------------------------------------------------------

def _area(n_out, start, length, n_src):
    """Weights (n_out x n_src): each output cell the average of the source
    cells it covers, partly covered ones in part."""
    edges = start + np.arange(n_out + 1) * (length / n_out)
    lo, hi = edges[:-1, None], edges[1:, None]
    cells = np.arange(n_src)[None, :]
    cover = np.clip(np.minimum(hi, cells + 1) - np.maximum(lo, cells), 0,
                    None)
    return cover / cover.sum(1, keepdims=True)


def _blur(a, r):
    k = 2 * r + 1
    p = np.pad(a, r, mode="edge")
    c = np.cumsum(np.cumsum(p, 0), 1)
    c = np.pad(c, ((1, 0), (1, 0)))
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def matte(black, white):
    """(premultiplied rgb, alpha), 0..1, from the same picture on black
    and on white."""
    b = black.astype(float) / 255
    w = white.astype(float) / 255
    alpha = np.clip(1 - (w - b).mean(-1), 0, 1)
    return np.clip(b, 0, alpha[..., None]), alpha


def portrait_from(rgb, alpha, crop=0.6, room=0.44):
    """The 136x188 picture, cropped and shadowed as the game's own: the
    top `crop` of the figure's height, `room` of the width left of her
    middle."""
    rows = np.nonzero(alpha.max(1) > 0.1)[0]
    if len(rows) == 0:
        raise ValueError("nothing was drawn")
    top, bottom = rows[0], rows[-1]
    crop_h = crop * (bottom - top)
    y0 = top - 0.03 * crop_h
    crop_w = crop_h * W / H
    band = alpha[int(y0):int(y0 + crop_h)]
    cols = np.arange(alpha.shape[1])
    cx = (band.sum(0) * cols).sum() / band.sum()
    x0 = cx - crop_w * room
    wy = _area(H, y0, crop_h, alpha.shape[0])
    wx = _area(W, x0, crop_w, alpha.shape[1])
    a = wy @ alpha @ wx.T
    c = np.stack([wy @ rgb[..., i] @ wx.T for i in range(3)], -1)
    shadow = np.zeros_like(a)
    shadow[9:, :-10] = a[:-9, 10:]
    shadow = _blur(_blur(shadow, 1), 1) * 0.45
    out_a = a + shadow * (1 - a)
    color = np.where(out_a[..., None] > 0, c / np.maximum(out_a, 1e-6)[
        ..., None], 0)
    rgba = np.concatenate([color, out_a[..., None]], -1)
    return (np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8)


# Her standing pose, seen three-quarters from her front as Zelda's portrait
# is (the camera from her feet: eye x y z, looking at x y z, fov), the top
# 64% of her height. Her taunt turns her back to the camera; her needle
# charge and her attacks hunch her or cut badly at this crop.
CAMERA = (15, 12, 38, 0.5, 11, 0, 30)
CROP = (0.64, 0.48)


def render_sheik(root=ART, size=(1440, 1080), log=print,
                 which=range(SHEIK_COSTUMES), camera=CAMERA, crop=CROP,
                 pose=None):
    """Draw Sheik in each of her costumes (`which`; about 5 seconds each).
    `pose`: called with the game before the picture, to put her in one."""
    sys.path.insert(0, str(ROOT / "tools" / "melee_native"))
    from window import Window   # noqa: E402

    shots = root / "studio"
    shots.mkdir(parents=True, exist_ok=True)
    # no sound: it draws beside the client, whose music it would play over
    with Window(window=size, sound=False) as w:
        for n in which:
            w.costume(0, n)
            w.start("sheik", None, stage="final-destination")
            w.step(20)
            if pose is not None:
                pose(w)
            x, y = w.fighter(0).pos
            ex, ey, ez, ix, iy, iz, fov = camera
            w.freeze(True)
            w.studio("solo", 1)
            w.studio("cam", x + ex, y + ey, ez, x + ix, y + iy, iz, fov)
            pictures = []
            for bg in ((0, 0, 0), (255, 255, 255)):
                w.studio("bg", *bg)
                for _ in range(5):
                    w.step(3)
                    path = w.shot(shots / ("sheik-%d-%d.ppm" % (n, bg[0])))
                    img = read_ppm(path)
                    corners = img[[2, 2, -3, -3], [2, -3, 2, -3]]
                    if np.abs(corners.astype(int) - bg).max() < 8:
                        break
                else:
                    raise RuntimeError("the background never cleared")
                pictures.append(img)
            w.studio("solo", 0)
            w.studio("cam", "off")
            w.freeze(False)
            rgb, alpha = matte(*pictures)
            write_portrait(root / "portrait" / ("sheik-%d.png" % n),
                           portrait_from(rgb, alpha, *crop))
            log("art: Sheik, costume %d of %d" % (n + 1, SHEIK_COSTUMES))
    have = costumes(root)
    done = 0
    while done < SHEIK_COSTUMES and \
            portrait("sheik", done, root) is not None:
        done += 1
    have["sheik"] = done
    (root / "costumes.json").write_text(json.dumps(have, indent=1))


def render_sheik_later(root=ART):
    """Draw Sheik in a process of its own, which dies with this one: a
    Popen to poll, or None if she is drawn already."""
    if not sheik_missing(root):
        return None
    return _later([sys.executable, str(Path(__file__).resolve()), "--sheik",
                   "--root", str(root)])


def _later(cmd):
    """A drawing process of its own that dies with this one. (Windows: the
    game it starts opens a window of its own, off to the side of the
    client's, and window.shot photographs that: win32ui.py.)"""
    if sys.platform == "win32":
        sys.path.insert(0, str(ROOT / "tools" / "melee_native"))
        from native import die_with_parent_win32
        p = subprocess.Popen(
            [cmd[0], "-X", "utf8", *cmd[1:]], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        die_with_parent_win32(p.pid)
        return p
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            start_new_session=True,
                            preexec_fn=_die_with_parent)


def _die_with_parent():
    import ctypes
    import signal
    try:
        ctypes.CDLL("libc.so.6").prctl(1, signal.SIGTERM)   # PR_SET_PDEATHSIG
    except OSError:
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sheik", action="store_true",
                    help="draw Sheik's pictures again")
    ap.add_argument("--root", default=str(ART), help=argparse.SUPPRESS)
    args = ap.parse_args()
    root = Path(args.root)
    if not ensure(root):
        return 1
    print("art: the disc's portraits and emblems are in %s" % root)
    if args.sheik or sheik_missing(root):
        render_sheik(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
