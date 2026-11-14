"""The input display's controller, composed as one picture (the owner,
2026-11-14: "This feels like a patchwork job of different components where
it should feel like a cohesive controller component, not random PNGs
spliced together!", then "I like the realistic buttons ... build them in
with the body so it doesn't just look like random floating buttons above a
controller shell").

    python tools/melee_client/padart.py

A GameCube controller seen from the front, on a frame of SHELL_W by
SHELL_H (screens.PAD_W by PAD_H at 0.52): a flat shell of our own drawing,
to the owner's references of the controller's shape (not in the
repository), with SmashWiki's button icons (buttons.py fetches them) set
into it: each in a socket of its own outline cut into the shell, with a
shadow under it, all lit from above alike; at rest a button is shaded, held
it is bright with a light round it. L and R sit behind the shoulders along
their slope, Z on the top edge above X and Y.

Each part that changes is a layer of the same frame, made into a picture
of the same size (rsvg-convert, into build/ui/pad/), so that the layers lie
on each other exactly: the shell with every button set in it at rest; over
it, a button bright while held; the sticks' caps, which move; the triggers
behind the shell, which go in under it, a bright copy over each showing as
it is pressed. Without rsvg-convert or the icons there is no controller.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import buttons  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "build" / "ui" / "pad"
VERSION = 4             # made again when this changes
SHELL_W, SHELL_H, EDGE = 300, 220, 4    # the frame, and room round it
SCALE = 2               # pixels per unit of the frame

# The shell's left half, from the top's middle round to the arch's middle,
# as cubic curves (first handle, second handle, end); the right half is it
# mirrored: the top's long arch, the shoulders, the grips, the lobes round
# the D-pad and the C-stick and the arch between them.
SHELL_LEFT = (
    ((108, 1), (80, 6), (64, 13)),          # the top
    ((36, 5), (26, 22), (24, 32)),          # the shoulder
    ((-6, 52), (0, 82), (1, 98)),           # the side round the stick
    ((-1, 150), (0, 218), (26, 218)),       # the grip, out and down
    ((53, 218), (54, 162), (55, 148)),      # its end, its inside up
    ((61, 166), (70, 190), (103, 185)),     # the lobe round the D-pad
    ((143, 180), (143, 128), (115, 104)),
    ((122, 99), (138, 97), (150, 97)))      # the arch
# the controller's own indigo, its edge a little darker (the owner's
# photo of the controller: "the triggers are inside the controller, the Z
# button is flat and blue")
SHELL, SHELL_EDGE, SOCKET = "#5A54B4", "#3C378A", "#2A2668"
# Z: flat, blue, on the top edge by R (drawn here, not the wiki's icon):
# its middle, length, thickness, slant; at rest and held
Z_BAR = (262, 15, 30, 9, 33)
Z_REST, Z_HELD = "#3346C8", "#6F86FF"

# Each icon as it is drawn: (SmashWiki's icon, its elements not drawn, a
# view of it other than its whole). The sticks' icons are cut in two.
CAP_IDS = {"STICK": ("circle4351", "circle4353", "circle4178",
                     "circle4180", "circle4182", "path4367", "path4437",
                     "path4463"),
           "C": ("g4321",)}
GATE_ID = "path3399"
ICONS = {
    "A": ("A", (), None), "B": ("B", (), None), "X": ("X", (), None),
    "Y": ("Y", (), None), "L": ("L", (), None),
    "R": ("R", (), None),
    "START": ("START", (), "82 114 92 92"),     # the button, no label
    "STICK-GATE": ("STICK", CAP_IDS["STICK"], None),
    "STICK-CAP": ("STICK", (GATE_ID,), None),
    "C-GATE": ("C", CAP_IDS["C"], None),
    "C-CAP": ("C", (GATE_ID,), None),
    "D-PAD": ("D-PAD", (), None), "D-UP": ("D-UP", (), None),
    "D-DOWN": ("D-DOWN", (), None), "D-LEFT": ("D-LEFT", (), None),
    "D-RIGHT": ("D-RIGHT", (), None),
}
# Where each sits on the frame: its middle, its width (or None: its
# height), its height (or None), its turn in degrees.
PLACE = {
    "STICK-GATE": (53.6, 76.3, 46, None, 0),
    "STICK-CAP": (53.6, 76.3, 27, None, 0),
    "C-GATE": (201.2, 144.7, 31, None, 0),
    "C-CAP": (201.2, 144.7, 18, None, 0),
    "D-PAD": (96.8, 146.2, 30, None, 0),
    "START": (150, 74, 11, None, 0),
    "A": (246.4, 75.6, None, 31, 0),
    "B": (211, 100, None, 19, 0),
    "X": (277, 70, None, 33, 0),
    "Y": (236, 47, 32, None, 0),
    # behind the shell's top corners, a rim of each showing
    "L": (30, 13, 56, None, -24),
    "R": (270, 13, 56, None, 24),
}
for _d in ("D-UP", "D-DOWN", "D-LEFT", "D-RIGHT"):
    PLACE[_d] = PLACE["D-PAD"]
# how far each stick's cap goes at full tilt, how far a trigger goes in
TRAVEL = {"S": 10.0, "C": 6.5}
PRESS = 7.0

# the layers, in the order they are drawn (screens.pad_display), and the
# icon each held one shows
BEHIND = ("L", "L-LIT", "R", "R-LIT")
LIT = {"A": "A", "B": "B", "X": "X", "Y": "Y", "Z": None, "ST": "START",
       "DU": "D-UP", "DD": "D-DOWN", "DL": "D-LEFT", "DR": "D-RIGHT"}
CAPS = {"S": "STICK-CAP", "C": "C-CAP"}
LAYERS = BEHIND + ("BODY",) + tuple(LIT) + tuple(CAPS)

# set into the shell: a socket of the part's outline a little wider than
# it, a shadow under it; shaded at rest; a light round it while held
FILTERS = (
    '<filter id="socket" x="-20%" y="-20%" width="140%" height="140%">'
    '<feMorphology in="SourceAlpha" operator="dilate" radius="1.7" '
    'result="d"/><feFlood flood-color="SOCKET"/>'
    '<feComposite in2="d" operator="in"/></filter>'
    '<filter id="shadow" x="-30%" y="-30%" width="160%" height="170%">'
    '<feMorphology in="SourceAlpha" operator="dilate" radius="1.7" '
    'result="d"/><feGaussianBlur in="d" stdDeviation="1.4"/>'
    '<feOffset dy="2" result="b"/><feFlood flood-color="#000000" '
    'flood-opacity="0.55"/><feComposite in2="b" operator="in"/></filter>'
    '<filter id="shade" x="0%" y="0%" width="100%" height="100%">'
    '<feFlood flood-color="#0E0C26" flood-opacity="0.42"/>'
    '<feComposite in2="SourceAlpha" operator="in"/></filter>'
    '<filter id="glow" x="-40%" y="-40%" width="180%" height="180%">'
    '<feMorphology in="SourceAlpha" operator="dilate" radius="1.3" '
    'result="d"/><feGaussianBlur in="d" stdDeviation="1.1" result="g"/>'
    '<feFlood flood-color="#FFFFFF" flood-opacity="0.9"/>'
    '<feComposite in2="g" operator="in"/></filter>').replace("SOCKET", SOCKET)

_text = {}
_bounds = {}
_count = [0]


def _source(icon):
    """An icon's SVG, its insides only (the wiki's metadata left out)."""
    file, hidden, view = ICONS[icon]
    if icon not in _text:
        text = (buttons.OUT / buttons.FILES[file]).read_text()
        for i in hidden:
            text = text.replace('id="%s"' % i,
                                'id="%s" visibility="hidden"' % i, 1)
        text = re.sub(r"<metadata.*?</metadata>", "", text, flags=re.S)
        text = re.sub(r"<\?xml.*?\?>|<!--.*?-->", "", text, flags=re.S)
        inner = text[text.index(">", text.index("<svg")) + 1:
                     text.rindex("</svg>")]
        _text[icon] = (inner, view or "0 0 256 256")
    return _text[icon]


def _nest(icon, prefix):
    """The icon as a nested <svg> of its own coordinates, its ids made
    its own (an icon is drawn more than once in a picture)."""
    inner, view = _source(icon)
    inner = re.sub(r'id="([^"]+)"', r'id="%s\1"' % prefix, inner)
    inner = re.sub(r"url\(#([^)]+)\)", r"url(#%s\1)" % prefix, inner)
    inner = re.sub(r'href="#([^"]+)"', r'href="#%s\1"' % prefix, inner)
    return inner, view


def _measure(tool, icon):
    """Where an icon is drawn in its own coordinates: (x, y, w, h)."""
    if icon in _bounds:
        return _bounds[icon]
    inner, view = _source(icon)
    vx, vy, vw, vh = (float(v) for v in view.split())
    px = 512
    svg = OUT / ("measure-%s.svg" % icon.lower())
    png = OUT / ("measure-%s.png" % icon.lower())
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink='
                   '"http://www.w3.org/1999/xlink" width="%d" height="%d" '
                   'viewBox="%s">%s</svg>' % (px, px * vh / vw, view, inner))
    subprocess.run([tool, "-o", str(png), str(svg)], check=True,
                   capture_output=True, timeout=30)
    import numpy as np
    img = buttons._read(png)
    ys, xs = np.nonzero(img[..., 3] > 8)
    k = vw / px
    pad = 2 * k             # its edges' last soft pixels kept
    _bounds[icon] = (vx + xs.min() * k - pad, vy + ys.min() * k - pad,
                     (xs.max() - xs.min() + 1) * k + 2 * pad,
                     (ys.max() - ys.min() + 1) * k + 2 * pad)
    return _bounds[icon]


def _box(icon, place_as=None):
    """Where an icon goes on the frame: x, y, w, h, turn, and the part of
    its own coordinates to show there."""
    bx, by, bw, bh = _bounds[place_as or icon]
    cx, cy, w, h, turn = PLACE[icon]
    if w is None:
        w = h * bw / bh
    if h is None:
        h = w * bh / bw
    return cx - w / 2, cy - h / 2, w, h, turn, (bx, by, bw, bh)


def _icon(icon, place_as=None, filt=None, opacity=None):
    """An icon set on the frame (through a filter, or faded)."""
    x, y, w, h, turn, (bx, by, bw, bh) = _box(icon, place_as)
    _count[0] += 1
    inner, _ = _nest(icon, "i%d_" % _count[0])
    out = ('<svg x="%.2f" y="%.2f" width="%.2f" height="%.2f" viewBox="%.2f '
           '%.2f %.2f %.2f">%s</svg>' % (
               x, y, w, h, bx, by, bw, bh, inner))
    attrs = ""
    if turn:
        attrs += ' transform="rotate(%g %g %g)"' % (turn, x + w / 2,
                                                    y + h / 2)
    if filt:
        out = '<g filter="url(#%s)">%s</g>' % (filt, out)
    if opacity is not None:
        out = '<g opacity="%g">%s</g>' % (opacity, out)
    return "<g%s>%s</g>" % (attrs, out)


def _set_in(icon, place_as=None, shaded=True):
    """An icon set into the shell: its shadow, its socket, it, shaded."""
    out = (_icon(icon, place_as, "shadow") + _icon(icon, place_as, "socket")
           + _icon(icon, place_as))
    if shaded:
        out += _icon(icon, place_as, "shade")
    return out


def _held(icon, place_as=None):
    """An icon bright, a light round it."""
    return _icon(icon, place_as, "glow") + _icon(icon, place_as)


def _z(held):
    """Z: a flat blue bar with rounded ends, set into the top edge."""
    x, y, length, thick, turn = Z_BAR
    bar = ('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s"/>'
           % (-length / 2, -thick / 2, length, thick, thick / 2,
              Z_HELD if held else Z_REST))
    g = '<g transform="translate(%g %g) rotate(%g)">%%s</g>' % (x, y, turn)
    if held:
        return (g % ('<g filter="url(#glow)">%s</g>' % bar)) + g % bar
    return (g % ('<g filter="url(#shadow)">%s</g>' % bar) +
            g % ('<g filter="url(#socket)">%s</g>' % bar) + g % bar)


def _shell():
    pts = [(150, 0)] + [e for _, _, e in SHELL_LEFT]
    d = ["M150,0"]
    for c1, c2, e in SHELL_LEFT:
        d.append("C%g,%g %g,%g %g,%g" % (c1 + c2 + e))
    for i in range(len(SHELL_LEFT) - 1, -1, -1):
        c1, c2, _ = SHELL_LEFT[i]
        d.append("C%g,%g %g,%g %g,%g" % (
            SHELL_W - c2[0], c2[1], SHELL_W - c1[0], c1[1],
            SHELL_W - pts[i][0], pts[i][1]))
    return " ".join(d) + "Z"


def layer(name):
    """The inside of one layer's picture."""
    if name in ("L", "R"):         # light grey, as the controller's
        return _icon(name) + _icon(name, filt="shade", opacity=0.55)
    if name in ("L-LIT", "R-LIT"):
        return _held(name[0])
    if name == "BODY":
        shell = _shell()
        out = ('<path d="%s" fill="%s" stroke="%s" stroke-width="7" '
               'stroke-linejoin="round"/><path d="%s" fill="%s"/>' % (
                   shell, SHELL_EDGE, SHELL_EDGE, shell, SHELL))
        out += _set_in("STICK-GATE", shaded=False)
        out += _set_in("C-GATE", shaded=False)
        out += _set_in("D-PAD")
        for b in ("START", "B", "A", "X", "Y"):
            out += _set_in(b)
        return out + _z(False)
    if name == "Z":
        return _z(True)
    if name in LIT:
        icon = LIT[name]
        return _held(icon, "D-PAD" if icon.startswith("D-") else None)
    if name in CAPS:
        icon = CAPS[name]
        return _icon(icon, filt="shadow") + _icon(icon)
    raise KeyError(name)


def svg(inner):
    w, h = SHELL_W + 2 * EDGE, SHELL_H + 2 * EDGE
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink='
            '"http://www.w3.org/1999/xlink" width="%d" height="%d" '
            'viewBox="%d %d %d %d"><defs>%s</defs>%s</svg>' % (
                w, h, -EDGE, -EDGE, w, h, FILTERS, inner))


def path(name):
    return OUT / ("%s.png" % name.lower())


def _prepare(tool):
    """The icons measured; the D-pad's five alike (its lit arms reach a
    little further out than the plain one: all shown in one box)."""
    for icon in ICONS:
        _measure(tool, icon)
    boxes = [_bounds[d] for d in ("D-PAD", "D-UP", "D-DOWN", "D-LEFT",
                                  "D-RIGHT")]
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes)
    y1 = max(b[1] + b[3] for b in boxes)
    _bounds["D-PAD"] = (x0, y0, x1 - x0, y1 - y0)


def ensure():
    """{layer: picture}, made the first time (and when VERSION changes);
    {} without rsvg-convert or the icons."""
    stamp = OUT / "VERSION"
    fresh = stamp.exists() and stamp.read_text().strip() == str(VERSION)
    if fresh and all(path(n).exists() for n in LAYERS):
        return {n: path(n) for n in LAYERS}
    tool = shutil.which("rsvg-convert")
    have = buttons.ensure()
    if tool is None or any(f not in have for f in
                           {f for f, _, _ in ICONS.values()}):
        return {}
    OUT.mkdir(parents=True, exist_ok=True)
    w, h = SHELL_W + 2 * EDGE, SHELL_H + 2 * EDGE
    try:
        _prepare(tool)
        for name in LAYERS:
            src = OUT / ("%s.svg" % name.lower())
            src.write_text(svg(layer(name)))
            subprocess.run([tool, "-w", str(w * SCALE), "-h",
                            str(h * SCALE), "-o", str(path(name)), str(src)],
                           check=True, capture_output=True, timeout=60)
    except (subprocess.SubprocessError, OSError, ValueError) as e:
        print("padart: %s" % e, file=sys.stderr)
        return {}
    stamp.write_text(str(VERSION))
    return {n: path(n) for n in LAYERS}


def whole(held=(), stick=(0, 0), cstick=(0, 0), ltrig=0.0, rtrig=0.0):
    """The controller as one SVG, some parts held (for looking at it;
    after ensure())."""
    def moved(name, dx, dy):
        return '<g transform="translate(%g %g)">%s</g>' % (dx, dy,
                                                            layer(name))
    out = ""
    for t, amount in (("L", ltrig), ("R", rtrig)):
        out += moved(t, 0, amount * PRESS)
        out += '<g opacity="%g">%s</g>' % (amount, moved(t + "-LIT", 0,
                                                          amount * PRESS))
    out += layer("BODY")
    for b in held:
        out += layer(b)
    out += moved("S", stick[0] * TRAVEL["S"], -stick[1] * TRAVEL["S"])
    out += moved("C", cstick[0] * TRAVEL["C"], -cstick[1] * TRAVEL["C"])
    return svg(out)


if __name__ == "__main__":
    made = ensure()
    print("%d layers in %s" % (len(made), OUT))
    sys.exit(0 if len(made) == len(LAYERS) else 1)
