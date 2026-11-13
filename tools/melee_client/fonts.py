"""The client's typefaces, fetched once into build/ui/fonts/.

    python tools/melee_client/fonts.py

Barlow, Barlow Condensed (Jeremy Tribby) and IBM Plex Mono (IBM), all under
the SIL Open Font License, from the google/fonts repository at a fixed
commit. Their licence texts are fetched beside them. Nothing is sent but
the requests for these files.
"""
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "build" / "ui" / "fonts"
COMMIT = "29b4ec6df2522a8aee279414b78a07910b065874"
BASE = "https://raw.githubusercontent.com/google/fonts/%s/ofl/" % COMMIT
FILES = [
    "barlowcondensed/BarlowCondensed-SemiBold.ttf",
    "barlowcondensed/BarlowCondensed-Bold.ttf",
    "barlowcondensed/BarlowCondensed-ExtraBold.ttf",
    "barlowcondensed/BarlowCondensed-BoldItalic.ttf",
    "barlowcondensed/BarlowCondensed-ExtraBoldItalic.ttf",
    "barlowcondensed/OFL.txt",
    "barlow/Barlow-Regular.ttf",
    "barlow/Barlow-Medium.ttf",
    "barlow/Barlow-SemiBold.ttf",
    "barlow/Barlow-Bold.ttf",
    "barlow/OFL.txt",
    "ibmplexmono/IBMPlexMono-Medium.ttf",
    "ibmplexmono/IBMPlexMono-SemiBold.ttf",
    "ibmplexmono/OFL.txt",
]


def path(name):
    family, file = name.split("/")
    return OUT / (file if file.endswith(".ttf") else family + "-OFL.txt")


def fonts():
    """The font files, fetching any that are missing."""
    OUT.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        to = path(name)
        if to.exists() and to.stat().st_size > 1000:
            continue
        with urllib.request.urlopen(BASE + name, timeout=60) as r:
            data = r.read()
        if name.endswith(".ttf") and data[:4] != b"\x00\x01\x00\x00":
            raise SystemExit("not a font file: " + name)
        to.write_bytes(data)
    return [path(n) for n in FILES if n.endswith(".ttf")]


if __name__ == "__main__":
    for f in fonts():
        print(f.relative_to(ROOT), f.stat().st_size)
    sys.exit(0)
