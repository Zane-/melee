"""The GameCube controller's buttons as the client draws them: SmashWiki's
button icons (Category:Button icons (GCN)), fetched once into
build/ui/buttons/ and turned into pictures there.

    python tools/melee_client/buttons.py

The owner, 2026-11-13: "make sure that the GCC buttons are more realistic
... use these directly for accuracy in all our menus". The icons carry no
free licence (SmashWiki marks them only as used on the wiki), so they are
not part of the repository: each machine fetches them, as the typefaces
(fonts.py). Nothing is sent but the requests for these files. The SVGs
become PNGs with rsvg-convert (librsvg); without it, or offline, the client
draws its own stand-ins (screens.key).

Made from them, beside them: START cropped to its button and its label (the
whole icon leaves the label unreadable at button size), once as it is and
once with the label light, for the dark panels ("start-light"); and the
D-pad with left and right both lit ("d-side"), which the wiki has not.

And the input display's controller (screens.pad_display; the owner,
2026-11-14: "use the official button icons so it looks more like an actual
gamecube controller"): each stick in two, its gate and its cap, so that the
cap moves in the gate; START as its button alone; the D-pad and its four
lit arms cut to one box, so that they lie on each other; and the
controller's body, drawn here (BODY: ours, not the wiki's, to the owner's
references of the controller's shape).
"""
import json
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "build" / "ui" / "buttons"
API = "https://www.ssbwiki.com/api.php"
AGENT = "melee-training-client/0.1"
SIZE = 128         # pixels, before the empty room round each is cut off
# the client's button names -> the icon's file on SmashWiki
FILES = {
    "A": "ButtonIcon-GCN-A.svg", "B": "ButtonIcon-GCN-B.svg",
    "X": "ButtonIcon-GCN-X.svg", "Y": "ButtonIcon-GCN-Y.svg",
    "Z": "ButtonIcon-GCN-Z.svg", "L": "ButtonIcon-GCN-L.svg",
    "R": "ButtonIcon-GCN-R.svg", "START": "ButtonIcon-GCN-Start-Pause.svg",
    "C": "ButtonIcon-GCN-C-Stick.svg",
    "STICK": "ButtonIcon-GCN-Control_Stick.svg",
    "D-PAD": "ButtonIcon-GCN-D-Pad.svg",
    "D-UP": "ButtonIcon-GCN-D-Pad-U.svg",
    "D-DOWN": "ButtonIcon-GCN-D-Pad-D.svg",
    "D-LEFT": "ButtonIcon-GCN-D-Pad-L.svg",
    "D-RIGHT": "ButtonIcon-GCN-D-Pad-R.svg",
}


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def _urls():
    """{file name: where it is}, from the wiki's API."""
    titles = "|".join("File:" + f for f in FILES.values())
    query = urllib.parse.urlencode(dict(
        action="query", titles=titles, prop="imageinfo", iiprop="url",
        format="json"))
    pages = json.loads(_get(API + "?" + query))["query"]["pages"]
    out = {}
    for p in pages.values():
        info = p.get("imageinfo")
        if info:
            out[p["title"][5:].replace(" ", "_")] = info[0]["url"]
    return out


# made here: name -> (what from)
MADE = {"START-LIGHT": "START", "D-SIDE": ("D-LEFT", "D-RIGHT")}
START_VIEW = 'viewBox="24 50 208 164"'
# the input display's controller (_make_pad): name -> (what from)
PAD = {"PAD-BODY": None, "STICK-GATE": "STICK", "STICK-CAP": "STICK",
       "C-GATE": "C", "C-CAP": "C", "PAD-START": "START",
       "PAD-D": "D-PAD", "PAD-D-UP": "D-UP", "PAD-D-DOWN": "D-DOWN",
       "PAD-D-LEFT": "D-LEFT", "PAD-D-RIGHT": "D-RIGHT"}
PAD_VERSION = 2     # made again when this changes
# what of each stick's icon is its cap (the rest is the gate); the C-stick's
# cap is one group
CAP = {"STICK": ("circle4351", "circle4353", "circle4178", "circle4180",
                 "circle4182", "path4367", "path4437", "path4463"),
       "C": ("g4321",)}
GATE = "path3399"
# START's button alone, without its label
START_BUTTON = 'viewBox="82 114 92 92"'
# The controller's shell, ours, drawn on 300 by 220 (screens.PAD_W by
# PAD_H) to the owner's references of the GameCube controller (2026-11-14:
# "the shape of the controller is very off ... Ensure the shell looks like
# this so we have a realistic controller!"): the top's long arch, the
# shoulders, the grips, the lobes round the D-pad and the C-stick and the
# arch between them. Its left half, from the top's middle round to the
# arch's middle, as cubic curves (first handle, second handle, end); the
# right half is it mirrored.
SHELL_LEFT = (
    ((108, 1), (80, 6), (64, 13)),          # the top
    ((36, 5), (26, 22), (24, 32)),          # the shoulder
    ((-6, 52), (0, 82), (1, 98)),           # the side round the stick
    ((-1, 150), (0, 218), (26, 218)),       # the grip, out and down
    ((53, 218), (54, 162), (55, 148)),      # its end, its inside up
    ((61, 166), (70, 190), (103, 185)),     # the lobe round the D-pad
    ((143, 180), (143, 128), (115, 104)),
    ((122, 99), (138, 97), (150, 97)))      # the arch
# the wells: round the control stick and the face buttons, under the D-pad
# and the C-stick
SHELL_WELLS = ((53.6, 76.3, 35), (246.4, 73, 40), (96.8, 146.2, 25),
               (201.2, 144.7, 25))
SHELL_W, SHELL_H, SHELL_EDGE = 300, 220, 4   # the picture's room round it


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


# an edge drawn under the shell, the shell over it (only its outline
# shows), the wells on it
BODY = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
    'viewBox="%d %d %d %d"><path d="%s" fill="#5B52A6" stroke="#5B52A6" '
    'stroke-width="7" stroke-linejoin="round"/><path d="%s" fill="#2E2A5E"/>'
    '<g fill="#262252" stroke="#4A4392" stroke-width="2">%s</g></svg>' % (
        SHELL_W + 2 * SHELL_EDGE, SHELL_H + 2 * SHELL_EDGE, -SHELL_EDGE,
        -SHELL_EDGE, SHELL_W + 2 * SHELL_EDGE, SHELL_H + 2 * SHELL_EDGE,
        _shell(), _shell(), "".join(
            '<circle cx="%g" cy="%g" r="%g"/>' % w for w in SHELL_WELLS)))


def path(name):
    return OUT / (name.lower() + ".png")


def _render(tool, svg, out, width, height):
    subprocess.run([tool, "-w", str(width), "-h", str(height), "-o",
                    str(out), str(svg)], check=True, capture_output=True,
                   timeout=30)


def _hide(text, ids):
    """An SVG with these elements not drawn."""
    for i in ids:
        text = text.replace('id="%s"' % i, 'id="%s" visibility="hidden"' % i,
                            1)
    return text


def _make_pad(tool):
    """The input display's controller (PAD), made again when PAD_VERSION
    changes."""
    import numpy as np
    sys.path.insert(0, str(ROOT / "tools" / "melee_client"))
    import art
    stamp = OUT / "PAD_VERSION"
    if stamp.exists() and stamp.read_text().strip() == str(PAD_VERSION) \
            and all(path(n).exists() for n in PAD):
        return
    body = OUT / "pad-body.svg"
    body.write_text(BODY)
    _render(tool, body, path("PAD-BODY"), 2 * (SHELL_W + 2 * SHELL_EDGE),
            2 * (SHELL_H + 2 * SHELL_EDGE))
    for stick in ("STICK", "C"):
        src = OUT / FILES[stick]
        if not src.exists():
            continue
        text = src.read_text()
        for part, hidden in (("GATE", CAP[stick]), ("CAP", (GATE,))):
            name = "%s-%s" % (stick, part)
            svg = OUT / (name.lower() + ".svg")
            svg.write_text(_hide(text, hidden))
            _render(tool, svg, path(name), SIZE, SIZE)
            _trim(path(name))
    src = OUT / FILES["START"]
    if src.exists():
        svg = OUT / "pad-start.svg"
        svg.write_text(src.read_text().replace(
            'viewBox="0 0 256 256"', START_BUTTON).replace(
            'height="256" width="256"', 'height="92" width="92"'))
        _render(tool, svg, path("PAD-START"), 96, 96)
        _trim(path("PAD-START"))
    # the D-pad and its lit arms, cut alike (each lit arm reaches out a
    # little further than the plain one)
    dirs = [n for n in ("D-PAD", "D-UP", "D-DOWN", "D-LEFT", "D-RIGHT")
            if (OUT / FILES[n]).exists()]
    if len(dirs) == 5:
        whole = {}
        for n in dirs:
            tmp = OUT / (FILES[n][:-4] + "-whole.png")
            _render(tool, OUT / FILES[n], tmp, SIZE, SIZE)
            whole[n] = _read(tmp)
        seen = np.zeros(whole["D-PAD"].shape[:2], bool)
        for img in whole.values():
            seen |= img[..., 3] > 8
        ys, xs = np.nonzero(seen)
        for n, img in whole.items():
            cut = img[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            out = np.zeros((cut.shape[0] + 4, cut.shape[1] + 4, 4), np.uint8)
            out[2:-2, 2:-2] = cut
            art.write_png(path("PAD-D" if n == "D-PAD" else "PAD-" + n), out)
    stamp.write_text(str(PAD_VERSION))


def _make(tool):
    """START cropped, light and dark; the D-pad lit left and right; the
    input display's controller."""
    src = OUT / FILES["START"]
    if src.exists() and not path("START-LIGHT").exists():
        text = src.read_text().replace('viewBox="0 0 256 256"', START_VIEW)
        text = text.replace('height="256" width="256"',
                            'height="164" width="208"')
        dark = OUT / "start-cropped.svg"
        dark.write_text(text)
        _render(tool, dark, path("START"), 163, 128)
        _trim(path("START"))
        light = OUT / "start-light.svg"
        light.write_text(text.replace("opacity:0.25;fill:#000000",
                                      "opacity:0.8;fill:#ffffff"))
        _render(tool, light, path("START-LIGHT"), 163, 128)
        _trim(path("START-LIGHT"))
    svgs = [OUT / FILES[n] for n in ("D-PAD", "D-LEFT", "D-RIGHT")]
    if not path("D-SIDE").exists() and all(f.exists() for f in svgs):
        import numpy as np
        sys.path.insert(0, str(ROOT / "tools" / "melee_client"))
        import art
        whole = []          # untrimmed, so that they line up
        for f in svgs:
            tmp = OUT / (f.stem + "-whole.png")
            _render(tool, f, tmp, SIZE, SIZE)
            whole.append(_read(tmp))
        plain, left, right = whole
        side = left.copy()
        lit = np.abs(right.astype(int) - plain.astype(int)).max(-1) > 8
        side[lit] = right[lit]
        art.write_png(path("D-SIDE"), side)
        _trim(path("D-SIDE"))
    _make_pad(tool)


def _read(png):
    """An RGBA PNG as rsvg-convert writes it."""
    import struct
    import zlib
    import numpy as np
    data = png.read_bytes()
    w, h = struct.unpack_from(">II", data, 16)
    i, idat = 8, b""
    while i < len(data):
        n = struct.unpack_from(">I", data, i)[0]
        if data[i + 4:i + 8] == b"IDAT":
            idat += data[i + 8:i + 8 + n]
        i += 12 + n
    raw = np.frombuffer(zlib.decompress(idat), np.uint8).reshape(
        h, w * 4 + 1)
    rows, out = raw[:, 0], np.zeros((h, w * 4), np.int32)
    for y in range(h):          # PNG's row filters, for 4-byte pixels
        line = raw[y, 1:].astype(np.int32)
        up = out[y - 1] if y else np.zeros(w * 4, np.int32)
        f = rows[y]
        if f == 0:
            out[y] = line
        elif f == 2:
            out[y] = (line + up) & 255
        else:
            cur = np.zeros(w * 4, np.int32)
            for x in range(w * 4):
                a = cur[x - 4] if x >= 4 else 0
                b = up[x]
                c = up[x - 4] if x >= 4 else 0
                if f == 1:
                    p = a
                elif f == 3:
                    p = (a + b) >> 1
                else:
                    pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                    p = a if pa <= pb and pa <= pc else b if pb <= pc else c
                cur[x] = (line[x] + p) & 255
            out[y] = cur
    return out.astype(np.uint8).reshape(h, w, 4)


def _trim(png):
    """The picture cut to what is drawn in it, with 2 clear pixels round it
    (the renderer wraps a picture's edges: see art.PAD)."""
    import numpy as np
    sys.path.insert(0, str(ROOT / "tools" / "melee_client"))
    import art
    img = _read(png)
    ys, xs = np.nonzero(img[..., 3] > 8)
    if len(ys) == 0:
        return
    cut = img[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    out = np.zeros((cut.shape[0] + 4, cut.shape[1] + 4, 4), np.uint8)
    out[2:-2, 2:-2] = cut
    art.write_png(png, out)


def ensure():
    """{button: picture} for the icons there are (fetched and made the
    first time); {} if they cannot be had."""
    names = list(FILES) + list(MADE) + list(PAD)
    have = {n: path(n) for n in names if path(n).exists()}
    stamp = OUT / "PAD_VERSION"
    if len(have) == len(names) and stamp.exists() and \
            stamp.read_text().strip() == str(PAD_VERSION):
        return have
    tool = shutil.which("rsvg-convert")
    if tool is None:
        return have
    try:
        if all(path(n).exists() for n in FILES):
            _make(tool)         # only what is made here is missing
            return {n: path(n) for n in names if path(n).exists()}
        urls = _urls()
        OUT.mkdir(parents=True, exist_ok=True)
        for name, file in FILES.items():
            if path(name).exists() or file not in urls:
                continue
            svg = _get(urls[file])
            if b"<svg" not in svg[:2000]:
                continue
            src = OUT / file
            src.write_bytes(svg)
            if name != "START":         # START is made cropped (_make)
                _render(tool, src, path(name), SIZE, SIZE)
                _trim(path(name))
        _make(tool)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as e:
        print("buttons: %s" % e, file=sys.stderr)
    return {n: path(n) for n in names if path(n).exists()}


if __name__ == "__main__":
    got = ensure()
    every = list(FILES) + list(MADE) + list(PAD)
    for name in every:
        print("%-11s %s" % (name, got.get(name, "missing")))
    sys.exit(0 if len(got) == len(every) else 1)
