"""The pause menu's icons: line drawings on a 24 by 24 grid (the canvas's
"Paused: icons and the input display", approved by the owner 2026-11-13),
made into pictures in build/ui/icons with rsvg-convert, white, for the menu
to tint (RmlUi's image-color).

    python tools/melee_client/icons.py

Without rsvg-convert the menu has no icons; nothing else changes.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "build" / "ui" / "icons"
VERSION = 1
SIZE = 48          # pixels: drawn at 20 to 24 dp

# name -> (path, filled): stroked lines unless filled
ICON = {
    "play": ("M6 4l14 8-14 8z", False),
    "restart": ("M3 12a9 9 0 1 0 3-6.7M3 4v5h5", False),
    "shuffle": ("M3 7h4l10 10h4M3 17h4l3-3M14 10l3-3h4M18 4l3 3-3 3M18 14l3 "
                "3-3 3", False),
    "leniency": ("M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M14 4v4M8 10v4M16 16v4",
                 False),
    "coach": ("M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c.7.7 1 1.5 1 2.5h6c0-1 "
              ".3-1.8 1-2.5A6 6 0 0 0 12 3z", False),
    "input": ("M6 9h12a4 4 0 0 1 4 4v1a3 3 0 0 1-5.4 1.8L15 14H9l-1.6 1.8A3 3 "
              "0 0 1 2 14v-1a4 4 0 0 1 4-4zM7 11v3M5.5 12.5h3M16 12h.01M18 "
              "13.5h.01", False),
    "guide": ("M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4zM20 4h-6a3 3 0 0 0-3 "
              "3v13a2 2 0 0 1 2-2h7z", False),
    "sidebar": ("M3 4h18v16H3zM15 4v16", False),
    "menu": ("M4 6h16M4 12h16M4 18h16", False),
    "course": ("M4 20V10l8-6 8 6v10zM10 20v-6h4v6", False),
    "home": ("M3 11l9-7 9 7M5 9v11h14V9", False),
    "delay": ("M12 7v5l3 2M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z", False),
    # beyond the canvas's: the drill's own options, the CPU's side, the
    # stage, the demonstration, the opponent, leaving
    "options": ("M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M14 4v4M8 10v4M16 16v4",
                False),
    "side": ("M4 12h16M8 8l-4 4 4 4M16 8l4 4-4 4", False),
    "stage": ("M2 15h20M5 15l2 5h10l2-5M7 10h4M13 7h4", False),
    "demo": ("M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM10 8.5l5.5 3.5-5.5 3.5z",
             False),
    "person": ("M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0",
               False),
    "leave": ("M15 4h4v16h-4M10 8l-4 4 4 4M6 12h11", False),
    # the arrows either side of a value
    "left": ("M16 4L7 12l9 8z", True),
    "right": ("M8 4l9 8-9 8z", True),
}


def _svg(path, filled):
    paint = ('fill="#FFFFFF" stroke="none"' if filled else
             'fill="none" stroke="#FFFFFF" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round"')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
            'viewBox="0 0 24 24"><path d="%s" %s/></svg>' % (path, paint))


def ensure():
    """{name: picture}, made the first time (and when VERSION changes);
    {} without rsvg-convert."""
    tool = shutil.which("rsvg-convert")
    out = {}
    if tool is None:
        return out
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = OUT / "VERSION"
    fresh = stamp.exists() and stamp.read_text().strip() == str(VERSION)
    for name, (path, filled) in ICON.items():
        png = OUT / (name + ".png")
        if not fresh or not png.exists():
            svg = OUT / (name + ".svg")
            svg.write_text(_svg(path, filled))
            try:
                subprocess.run([tool, "-w", str(SIZE), "-h", str(SIZE), "-o",
                                str(png), str(svg)], check=True,
                               capture_output=True, timeout=30)
            except (subprocess.SubprocessError, OSError):
                continue
        out[name] = png
    stamp.write_text(str(VERSION))
    return out


if __name__ == "__main__":
    made = ensure()
    print("%d icons in %s" % (len(made), OUT))
    sys.exit(0 if made else 1)
