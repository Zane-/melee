#!/usr/bin/env python3
"""List Training Mode (TM-CE) ASM hooks that conflict with Slippi's injections.

For every `# To be inserted at 8XXXXXXX` in TM-CE's ASM folder, report:
  exact  - Slippi patches the same address (the hook cannot be applied as is)
  shared - Slippi patches another address in the same vanilla function
           (the function must never be replaced whole; patch a single site)

Usage:
    tools/tm_slippi_collisions.py [--asm ../TrainingMode/ASM] [--function NAME]
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import overlay_check as oc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--asm", type=Path, default=ROOT.parent / "TrainingMode" / "ASM")
    ap.add_argument("--function", help="only show hooks in this vanilla function")
    args = ap.parse_args()

    namer = oc.Namer()

    def func(addr):
        return namer.name(addr).split("+")[0]

    slippi = {}
    for line in oc.SLIPPI.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        addr, _, name = line.split(None, 2)
        slippi[int(addr, 16)] = name
    by_func = {}
    for addr, name in slippi.items():
        by_func.setdefault(func(addr), []).append(addr)

    pat = re.compile(r"inserted at\s+(?:0x)?([0-9A-Fa-f]{8})")
    print("kind\taddr\tvanilla_site\ttm_file\tslippi")
    counts = {"exact": 0, "shared": 0, "free": 0}
    for path in sorted(args.asm.rglob("*.asm")):
        m = pat.search(path.read_text(errors="ignore")[:300])
        if not m:
            continue
        addr = int(m.group(1), 16)
        f = func(addr)
        if args.function and f != args.function:
            continue
        if addr in slippi:
            kind, info = "exact", slippi[addr]
        elif f != "?" and f in by_func:
            kind = "shared"
            info = ",".join(f"{a:08X}" for a in sorted(by_func[f]))
        else:
            kind, info = "free", ""
        counts[kind] += 1
        if kind != "free" or args.function:
            rel = path.relative_to(args.asm)
            print(f"{kind}\t{addr:08X}\t{namer.name(addr)}\t{rel}\t{info}")
    print(
        "# exact=%(exact)d shared=%(shared)d free=%(free)d" % counts, file=sys.stderr
    )


if __name__ == "__main__":
    main()
