"""The Item switch's pictures (the owner, 2026-11-14: "a little icon of the
item to the left of the name"): the game's own, read off the disc.

The game's Item Switch shows a picture of the item under its cursor: one
texture animation in MnMaAll.usd (the cursor's model, MenMainCursorIs_Top,
mnitemsw.c) of 34 pictures, 64x64 CMPR, one frame per item. Which frame is
whose is the game's own two tables: the switch's bit for each item kind
(gm_1601.c's lbl_803B7844, the bits Versus turns into its item mask) and
the frame of each bit (mnitemsw.c's mnItemSw_80233A98: its own order but
two, which outside Japan show the Motion-Sensor Bomb and the Cloaking
Device as redrawn for the other versions). Each picture is written as the
game has it, with a transparent border (the renderer wraps a picture's
edges round: see art.PAD).

Everything goes to build/ui/art/item (git-ignored): the art is Nintendo's,
read from the owner's disc, and never part of the repository.

    python tools/melee_client/items.py            # what is missing
    python tools/melee_client/items.py --again    # read them all again
"""
import argparse
import struct
import sys
from pathlib import Path

import numpy as np

import art

OUT = art.ART / "item"
VERSION = 1    # of what is written here: a change writes them again
SIZE = 64
PAD = 2
# gm_1601.c's lbl_803B7844: the Item Switch's bit -> its item (ItemKind);
# 0x23 is a bit for no item
SWITCH_ITEM = (0x06, 0x0B, 0x07, 0x19, 0x14, 0x12, 0x11, 0x0E, 0x1C, 0x18,
               0x08, 0x1A, 0x04, 0x10, 0x17, 0x22, 0x20, 0x13, 0x09, 0x21,
               0x0D, 0x0F, 0x1F, 0x16, 0x15, 0x1E, 0x0A, 0x0C, 0x23, 0x05,
               0x1D, 0x1B)
# mnitemsw.c's mnItemSw_AnimTable.items: a bit's frame of the animation,
# and mnItemSw_80233A98's two that differ outside Japan
SWITCH_FRAME = tuple(range(24)) + (25, 24, 26, 27, 29, 28, 30, 31)
NOT_JAPAN = {17: 0x28, 19: 0x27}
KINDS = sorted(k for k in SWITCH_ITEM if k != 0x23)


def icon(kind, root=OUT):
    """The game's picture of item `kind` (an ItemKind; the 31 of the Item
    Switch), as a path, or None. Read off the disc the first time one is
    asked for."""
    path = root / ("item-%02x.png" % kind)
    if not path.exists() and kind in KINDS and root not in _tried:
        _tried.add(root)
        ensure(root)
    return path if path.exists() else None


_tried = set()


def missing(root=OUT):
    """The items whose pictures are not here (or were written by another
    VERSION of this file)."""
    stamp = root / "VERSION"
    if not stamp.exists() or stamp.read_text().strip() != str(VERSION):
        return list(KINDS)
    return [k for k in KINDS if not (root / ("item-%02x.png" % k)).exists()]


def ensure(root=OUT):
    """The pictures read off the disc, if they are not here yet. True if
    they are."""
    if not missing(root):
        return True
    try:
        pics = pictures(art.Archive(art.disc_file("MnMaAll.usd")))
    except (OSError, ValueError, KeyError) as e:
        print("items: %s" % e, file=sys.stderr)
        return False
    root.mkdir(parents=True, exist_ok=True)
    for kind, rgba in pics.items():
        out = np.zeros((SIZE + 2 * PAD, SIZE + 2 * PAD, 4), np.uint8)
        out[PAD:PAD + SIZE, PAD:PAD + SIZE] = rgba
        art.write_png(root / ("item-%02x.png" % kind), out)
    (root / "VERSION").write_text("%d\n" % VERSION)
    return not missing(root)


def pictures(arc):
    """{ItemKind: 64x64 rgba} of the Item Switch's pictures."""
    d = arc.d
    for r in sorted(arc.rel):
        ta = r - 0xC                # a TexAnim: its image table's field
        if ta < 0 or ta + 0x18 > len(d) or (ta + 8) not in arc.rel:
            continue
        n = struct.unpack_from(">H", d, ta + 0x14)[0]
        if n != 34:
            continue
        images = arc.u32(ta + 0xC)
        if arc.image(arc.u32(images))[1:] != (SIZE, SIZE, 14):
            continue
        aobj = arc.u32(ta + 8)
        tracks, f = {}, arc.u32(aobj + 8)
        while f:
            tracks[d[f + 12]] = art.fobj_values(arc, f)
            f = arc.u32(f) if f in arc.rel else 0
        keys = tracks[1]                    # TIMG: the image of each frame
        out = {}
        for bit, kind in enumerate(SWITCH_ITEM):
            if kind == 0x23:
                continue
            frame = NOT_JAPAN.get(bit, SWITCH_FRAME[bit])
            p, w, h, fmt = arc.image(
                arc.u32(images + 4 * int(art.held(keys, frame))))
            out[kind] = cmpr(d, p, w, h)
        return out
    raise ValueError("no Item Switch pictures in this file")


def _rgb565(v):
    r, g, b = (v >> 11) & 31, (v >> 5) & 63, v & 31
    return np.stack([(r << 3) | (r >> 2), (g << 2) | (g >> 4),
                     (b << 3) | (b >> 2)], -1)


def cmpr(d, p, w, h):
    """GX's CMPR: 8x8 blocks of four 4x4 blocks (left to right, top to
    bottom), each two RGB565 colours and 2-bit indices, a row a byte; the
    first colour not above the second: the third colour their average and
    the fourth transparent."""
    bx, by = (w + 7) // 8, (h + 7) // 8
    raw = np.frombuffer(d, np.uint8, bx * by * 32, p).reshape(by, bx, 2, 2,
                                                                8)
    c0 = raw[..., 0].astype(np.int32) << 8 | raw[..., 1]
    c1 = raw[..., 2].astype(np.int32) << 8 | raw[..., 3]
    a, b = _rgb565(c0), _rgb565(c1)
    four = (c0 > c1)[..., None]
    pal = np.zeros(c0.shape + (4, 4), np.int32)
    pal[..., 0, :3], pal[..., 1, :3] = a, b
    pal[..., 2, :3] = np.where(four, (2 * a + b) // 3, (a + b) // 2)
    pal[..., 3, :3] = np.where(four, (a + 2 * b) // 3, 0)
    pal[..., :3, 3] = 255
    pal[..., 3, 3] = np.where(four[..., 0], 255, 0)
    bits = raw[..., 4:8]
    idx = np.stack([(bits >> s) & 3 for s in (6, 4, 2, 0)], -1)
    px = np.take_along_axis(pal[..., None, :, :].repeat(4, -3),
                            idx[..., None].repeat(4, -1).astype(np.intp),
                            axis=-2)
    img = px.transpose(0, 2, 4, 1, 3, 5, 6).reshape(by * 8, bx * 8, 4)
    return img[:h, :w].astype(np.uint8)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--again", action="store_true",
                    help="read every picture off the disc again")
    ap.add_argument("--root", default=str(OUT), help=argparse.SUPPRESS)
    args = ap.parse_args()
    root = Path(args.root)
    if args.again:
        (root / "VERSION").unlink(missing_ok=True)
    if not ensure(root):
        return 1
    print("items: the Item Switch's %d pictures are in %s" % (len(KINDS),
                                                            root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
