#!/usr/bin/env python3
"""Prepare an extracted disc for booting the training overlay.

    tools/tmce_disc.py                 # updates build/disc
    tools/tmce_disc.py --disc DIR --iso path/to/GALE01.iso

- Extracts the retail disc into DIR with dtk if DIR does not exist yet.
- Copies build/overlay/main.dol to DIR/sys/main.dol.
- Copies TM-CE's art archives (../TrainingMode/dats, or $TMCE_DIR/dats) to
  DIR/files/TM/<unit>.dat, per src/tmce/units.txt. TM-CE ships the same
  files with its code merged in; the native build links the code instead.

Boot with `dolphin-emu -e DIR/sys/main.dol`.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TMCE_DIR = Path(os.environ.get("TMCE_DIR", ROOT.parent / "TrainingMode"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--disc", type=Path, default=ROOT / "build" / "disc")
    ap.add_argument("--iso", type=Path, help="retail GALE01 image, for the first extract")
    ap.add_argument("--dol", type=Path, default=ROOT / "build" / "overlay" / "main.dol")
    args = ap.parse_args()

    disc = args.disc
    if not (disc / "sys" / "main.dol").exists():
        if not args.iso:
            sys.exit(f"{disc} is not an extracted disc; pass --iso to extract one")
        dtk = ROOT / "build" / "tools" / "dtk"
        subprocess.run([str(dtk), "disc", "extract", str(args.iso), str(disc)], check=True)

    if not args.dol.exists():
        sys.exit(f"{args.dol} not found; run tools/overlay_build.py")
    shutil.copyfile(args.dol, disc / "sys" / "main.dol")
    print(f"{args.dol} -> {disc / 'sys' / 'main.dol'}")

    tm = disc / "files" / "TM"
    tm.mkdir(exist_ok=True)
    for line in (ROOT / "src" / "tmce" / "units.txt").read_text().splitlines():
        parts = line.split("#")[0].split()
        if not parts or parts[-1] == "-":
            continue
        name, art = parts[1], parts[-1]
        shutil.copyfile(TMCE_DIR / "dats" / art, tm / f"{name}.dat")
        print(f"dats/{art} -> files/TM/{name}.dat")

    stale = disc / "files" / "TmMenu.dat"  # from the pre-TM-CE native port
    if stale.exists():
        stale.unlink()


if __name__ == "__main__":
    main()
