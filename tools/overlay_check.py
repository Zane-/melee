#!/usr/bin/env python3
"""Check that a built DOL preserves the retail (vanilla) memory layout.

The training build must keep every vanilla address in place so that stock
Slippi Dolphin's injected netplay code and hardcoded savestate ranges still
apply (see docs/ai/slippi-tandem.md). This tool compares a built DOL against
the retail DOL in *address space* and fails when:

  1. a vanilla section moved, shrank or grew, or .bss / entry changed;
  2. vanilla bytes differ outside the declared patch sites (--patches);
  3. a differing range overlaps an address Slippi patches
     (config/GALE01/slippi_injections.txt);
  4. a new section overlaps the vanilla image, its stack, or lies outside
     the range given by --overlay-range.

Usage:
    tools/overlay_check.py BUILT.dol
    tools/overlay_check.py BUILT.dol --patches build/GALE01/tm_patches.txt
    tools/overlay_check.py BUILT.dol --json

Patch file format, one site per line ('#' comments allowed):
    ADDRESS LENGTH [note...]        e.g.  801A4C94 4 OnSceneChange hook

Exit status: 0 = layout preserved, 1 = violations, 2 = usage error.
"""

import argparse
import bisect
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RETAIL = ROOT / "orig" / "GALE01" / "sys" / "main.dol"
SYMBOLS = ROOT / "config" / "GALE01" / "symbols.txt"
SLIPPI = ROOT / "config" / "GALE01" / "slippi_injections.txt"

# Vanilla 1.02: image ends at 0x804DEC00, then 0x10000 of stack and 0x2000 of
# debug stack (see build/GALE01/ldscript.lcf). __ArenaLo is 0x804F0C00.
VANILLA_IMAGE_END = 0x804DEC00
VANILLA_ARENA_LO = 0x804F0C00
SLIPPI_PATCH_LEN = 4


class Dol:
    def __init__(self, path: Path):
        data = path.read_bytes()
        h = struct.unpack(">57I", data[:0xE4])
        self.sections = []  # (kind, index, addr, bytes)
        for i in range(18):
            off, addr, size = h[i], h[18 + i], h[36 + i]
            if size:
                kind = "text" if i < 7 else "data"
                idx = i if i < 7 else i - 7
                self.sections.append((kind, idx, addr, data[off : off + size]))
        self.bss = (h[54], h[55])
        self.entry = h[56]

    def find(self, addr):
        for s in self.sections:
            if s[2] <= addr < s[2] + len(s[3]):
                return s
        return None


def load_symbols():
    pat = re.compile(r"^(\S+) = \.\w+:0x([0-9A-Fa-f]{8}); // (.*)$")
    out = []
    for line in SYMBOLS.read_text().splitlines():
        m = pat.match(line)
        if m:
            size = re.search(r"size:0x([0-9A-Fa-f]+)", m.group(3))
            out.append(
                (int(m.group(2), 16), m.group(1), int(size.group(1), 16) if size else 0)
            )
    out.sort()
    return out


class Namer:
    def __init__(self):
        self.syms = load_symbols()
        self.addrs = [s[0] for s in self.syms]

    def name(self, addr):
        i = bisect.bisect_right(self.addrs, addr) - 1
        if i < 0:
            return "?"
        base, name, size = self.syms[i]
        if addr == base:
            return name
        if addr < base + max(size, 1):
            return f"{name}+0x{addr - base:X}"
        return "?"


def load_ranges(path: Path, default_len=None):
    """Returns sorted [(start, end, note)]."""
    out = []
    for line in path.read_text().splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        parts = line.split(None, 2)
        addr = int(parts[0], 16)
        if default_len is not None:
            length, note = default_len, " ".join(parts[1:])
        else:
            length = int(parts[1], 0)
            note = parts[2] if len(parts) > 2 else ""
        out.append((addr, addr + length, note))
    out.sort()
    return out


def overlaps(ranges, start, end):
    return [r for r in ranges if r[0] < end and start < r[1]]


def diff_ranges(a: bytes, b: bytes, base: int):
    """Yields (start_addr, end_addr) of differing runs, word-aligned."""
    n = min(len(a), len(b))
    i = 0
    while i < n:
        if a[i : i + 4] != b[i : i + 4]:
            j = i
            while j < n and a[j : j + 4] != b[j : j + 4]:
                j += 4
            yield (base + i, base + min(j, n))
            i = j
        else:
            i += 4


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("built", type=Path)
    ap.add_argument("--retail", type=Path, default=RETAIL)
    ap.add_argument("--patches", type=Path, help="declared patch sites")
    ap.add_argument("--slippi", type=Path, default=SLIPPI)
    ap.add_argument(
        "--overlay-range",
        default=f"{VANILLA_ARENA_LO:08X}-81700000",
        help="START-END (hex) where new sections may live",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    for p in (args.built, args.retail):
        if not p.exists():
            print(f"missing: {p}", file=sys.stderr)
            return 2

    retail, built = Dol(args.retail), Dol(args.built)
    namer = Namer()
    patches = load_ranges(args.patches) if args.patches else []
    slippi = load_ranges(args.slippi, SLIPPI_PATCH_LEN) if args.slippi.exists() else []
    ov_lo, ov_hi = (int(x, 16) for x in args.overlay_range.split("-"))

    errors, diffs, overlay = [], [], []

    if built.entry != retail.entry:
        errors.append(f"entry point moved: {retail.entry:08X} -> {built.entry:08X}")
    if built.bss != retail.bss:
        errors.append(
            "bss changed: %08X+0x%X -> %08X+0x%X" % (*retail.bss, *built.bss)
        )

    retail_by_addr = {s[2]: s for s in retail.sections}
    for kind, idx, addr, data in retail.sections:
        b = built.find(addr)
        if b is None or b[2] != addr:
            errors.append(f"vanilla {kind} section at {addr:08X} missing or moved")
            continue
        if len(b[3]) != len(data):
            errors.append(
                f"vanilla {kind} section at {addr:08X} resized: "
                f"0x{len(data):X} -> 0x{len(b[3]):X}"
            )
        for start, end in diff_ranges(data, b[3], addr):
            declared = overlaps(patches, start, end)
            covered = all(
                any(p[0] <= a < p[1] for p in declared) for a in range(start, end, 4)
            )
            hits = overlaps(slippi, start, end)
            diffs.append(
                {
                    "start": f"{start:08X}",
                    "end": f"{end:08X}",
                    "symbol": namer.name(start),
                    "declared": covered,
                    "slippi": [f"{h[0]:08X} {h[2]}" for h in hits],
                }
            )
            if not covered:
                errors.append(
                    f"undeclared change {start:08X}-{end:08X} in {namer.name(start)}"
                )
            for h in hits:
                errors.append(
                    f"change {start:08X}-{end:08X} in {namer.name(start)} "
                    f"collides with Slippi injection {h[0]:08X} ({h[2]})"
                )

    for kind, idx, addr, data in built.sections:
        if addr in retail_by_addr:
            continue
        end = addr + len(data)
        overlay.append({"kind": kind, "start": f"{addr:08X}", "end": f"{end:08X}"})
        if addr < VANILLA_ARENA_LO:
            errors.append(
                f"new {kind} section {addr:08X}-{end:08X} is inside the vanilla "
                f"image or stack (below {VANILLA_ARENA_LO:08X})"
            )
        elif not (ov_lo <= addr and end <= ov_hi):
            errors.append(
                f"new {kind} section {addr:08X}-{end:08X} outside overlay range "
                f"{ov_lo:08X}-{ov_hi:08X}"
            )

    for p in patches:
        hits = overlaps(slippi, p[0], p[1])
        for h in hits:
            msg = f"declared patch {p[0]:08X} ({p[2]}) collides with Slippi injection {h[0]:08X}"
            if msg not in errors:
                errors.append(msg)

    result = {
        "ok": not errors,
        "errors": errors,
        "vanilla_diffs": diffs,
        "overlay_sections": overlay,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"vanilla sections: {len(retail.sections)}, changed ranges: {len(diffs)}")
        for d in diffs:
            flag = "ok " if d["declared"] and not d["slippi"] else "BAD"
            print(f"  [{flag}] {d['start']}-{d['end']} {d['symbol']}")
        for o in overlay:
            print(f"  overlay {o['kind']} {o['start']}-{o['end']}")
        if errors:
            print(f"FAIL: {len(errors)} violation(s)")
            for e in errors:
                print("  " + e)
        else:
            print("OK: vanilla layout preserved")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
