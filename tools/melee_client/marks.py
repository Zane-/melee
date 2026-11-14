"""The menu panels' large faded drawings (the owner, 2026-11-14: "ensure all
menu items have a faded icon like in the mockups": Controls' controller on
the canvas's Settings board, drawn large, thin and faint, running off the
panel's edge). Line drawings, made into pictures in build/ui/marks with
rsvg-convert, white, for each panel to tint faint in its own ink
(RmlUi's image-color).

    python tools/melee_client/marks.py

Without rsvg-convert the panels have none; nothing else changes.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "build" / "ui" / "marks"
VERSION = 1
WIDTH = 512        # pixels: drawn at 190 to 470 dp

# name -> (view box width, height, the drawing's SVG elements)
MARK = {
    # Versus: two swords crossed
    "versus": (24, 24, '<path d="M3 3h3l9 9-3 3-9-9z"/><path d="M11 17l6-6"/>'
               '<path d="M15.5 15.5l4 4"/><circle cx="20.5" cy="20.5" r="1"/>'
               '<path d="M21 3h-3l-9 9 3 3 9-9z"/><path d="M13 17l-6-6"/>'
               '<path d="M8.5 15.5l-4 4"/><circle cx="3.5" cy="20.5" r="1"/>'),
    # Train: a target
    "train": (24, 24, '<circle cx="12" cy="12" r="9"/><circle cx="12" '
              'cy="12" r="5.5"/><circle cx="12" cy="12" r="2"/>'
              '<path d="M12 1v4M12 19v4M1 12h4M19 12h4"/>'),
    "settings": (24, 24, '<path d="M4 7h9M19 7h1M4 17h1M11 17h9"/><circle '
                 'cx="16" cy="7" r="2.5"/><circle cx="8" cy="17" r="2.5"/>'),
    "controller": (26, 20, '<path d="M7 3h12a5 5 0 0 1 4.7 3.3l1.8 5.4A3.6 '
                   '3.6 0 0 1 19 15l-2.2-2.4H9.2L7 15a3.6 3.6 0 0 1-6.5-'
                   '3.3l1.8-5.4A5 5 0 0 1 7 3Z"/><circle cx="7" cy="8" r="2"/>'
                   '<circle cx="18.6" cy="7.4" r="1.1"/><circle cx="20.8" '
                   'cy="9.6" r="0.8"/><circle cx="16.4" cy="10.4" r="1"/>'),
    "globe": (24, 24, '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 '
              '3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>'),
    "speaker": (24, 24, '<path d="M3.5 9.5h4l5-4v13l-5-4h-4z"/><path d="M16 '
                '9a4.5 4.5 0 0 1 0 6"/><path d="M18.5 6.5a8 8 0 0 1 0 11"/>'),
    "monitor": (24, 24, '<rect x="2.5" y="4.5" width="19" height="12" rx="1"/>'
                '<path d="M8 20h8M12 16.5V20M15.5 4.5v12"/>'),
    # the Lab: a flask
    "lab": (24, 24, '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 '
            '2-3l-5-9V3"/><path d="M7.5 15h9"/>'),
    # the course's parts: Tech a stopwatch (frames), Punish a burst,
    # Defense a shield, Neutral the space between two
    "tech": (24, 24, '<circle cx="12" cy="13.5" r="8"/><path d="M12 13.5V9M12 '
             '13.5l3 2M10 2.5h4M12 2.5v3M19 6l1.5-1.5"/>'),
    "punish": (24, 24, '<polygon points="12,2 13.72,7.84 19.07,4.93 16.16,'
               '10.28 22,12 16.16,13.72 19.07,19.07 13.72,16.16 12,22 10.28,'
               '16.16 4.93,19.07 7.84,13.72 2,12 7.84,10.28 4.93,4.93 10.28,'
               '7.84"/>'),
    "defense": (24, 24, '<path d="M12 2.5l8 3v6.5c0 5-3.4 8.6-8 10-4.6-1.4-8-'
                '5-8-10V5.5z"/>'),
    "neutral": (24, 24, '<path d="M2.5 12h19M6.5 8l-4 4 4 4M17.5 8l4 4-4 4"/>'
                '<circle cx="12" cy="12" r="2.2"/>'),
}


def _svg(width, height, body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 %d %d" fill="none" stroke="#FFFFFF" '
            'stroke-width="0.5" stroke-linecap="round" '
            'stroke-linejoin="round">%s</svg>' % (width, height, width,
                                                  height, body))


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
    for name, (width, height, body) in MARK.items():
        png = OUT / (name + ".png")
        if not fresh or not png.exists():
            svg = OUT / (name + ".svg")
            svg.write_text(_svg(width, height, body))
            try:
                subprocess.run([tool, "-w", str(WIDTH), "-h",
                                str(WIDTH * height // width), "-o", str(png),
                                str(svg)], check=True, capture_output=True,
                               timeout=30)
            except (subprocess.SubprocessError, OSError):
                continue
        out[name] = png
    stamp.write_text(str(VERSION))
    return out


if __name__ == "__main__":
    made = ensure()
    print("%d marks in %s" % (len(made), OUT))
    sys.exit(0 if made else 1)
