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


def path(name):
    return OUT / (name.lower() + ".png")


def _render(tool, svg, out, width, height):
    subprocess.run([tool, "-w", str(width), "-h", str(height), "-o",
                    str(out), str(svg)], check=True, capture_output=True,
                   timeout=30)


def _make(tool):
    """START cropped, light and dark; the D-pad lit left and right."""
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
    names = list(FILES) + list(MADE)
    have = {n: path(n) for n in names if path(n).exists()}
    if len(have) == len(names):
        return have
    tool = shutil.which("rsvg-convert")
    if tool is None:
        return have
    try:
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
    for name in list(FILES) + list(MADE):
        print("%-11s %s" % (name, got.get(name, "missing")))
    sys.exit(0 if len(got) == len(FILES) + len(MADE) else 1)
