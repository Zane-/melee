#!/usr/bin/env python3
"""Cross-reference MexTK (m-ex / Training Mode) names with decomp symbols.

MexTK's `melee.link` maps `ADDR:Name` for vanilla GALE01 1.02 functions.
The decomp's `config/GALE01/symbols.txt` names the same addresses differently.
This tool translates between the two so Training Mode code can be ported.

Usage:
    tools/mex_symbols.py                       # write the full TSV to stdout
    tools/mex_symbols.py Fighter_GetGObj ...   # look up MexTK names
    tools/mex_symbols.py 0x80034110            # look up an address
    tools/mex_symbols.py --used SRC_DIR        # only names referenced in SRC_DIR

Options:
    --link PATH   path to melee.link
                  (default: ../TrainingMode/MexTK/melee.link)
"""

import argparse
import bisect
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYMBOLS = ROOT / "config" / "GALE01" / "symbols.txt"
DEFAULT_LINK = ROOT.parent / "TrainingMode" / "MexTK" / "melee.link"

SYM_RE = re.compile(
    r"^(\S+) = (\.\w+):0x([0-9A-Fa-f]{8}); // (.*)$",
)


def load_symbols():
    """Returns sorted [(addr, name, section, size, type)]."""
    out = []
    for line in SYMBOLS.read_text().splitlines():
        m = SYM_RE.match(line)
        if not m:
            continue
        name, section, addr, attrs = m.groups()
        size = re.search(r"size:0x([0-9A-Fa-f]+)", attrs)
        kind = re.search(r"type:(\w+)", attrs)
        out.append(
            (
                int(addr, 16),
                name,
                section,
                int(size.group(1), 16) if size else 0,
                kind.group(1) if kind else "",
            )
        )
    out.sort()
    return out


def load_link(path: Path):
    """Returns [(addr, mex_name)] in file order."""
    out = []
    for line in path.read_text().splitlines():
        line = line.split("#")[0].strip()
        if ":" not in line:
            continue
        addr, name = line.split(":", 1)
        try:
            out.append((int(addr, 16), name.strip()))
        except ValueError:
            continue
    return out


class Resolver:
    def __init__(self):
        self.syms = load_symbols()
        self.addrs = [s[0] for s in self.syms]

    def resolve(self, addr: int):
        """Returns (decomp_name, section, note)."""
        i = bisect.bisect_right(self.addrs, addr) - 1
        if i < 0:
            return ("?", "", "below first symbol")
        base, name, section, size, _ = self.syms[i]
        if base == addr:
            return (name, section, "")
        if addr < base + size:
            return (name, section, f"+0x{addr - base:X} (inside)")
        return ("?", "", "no symbol (m-ex injected or unknown)")


def find_source(name: str):
    """Best-effort: the header under src/ that declares `name`."""
    pat = re.compile(r"\b" + re.escape(name) + r"\s*\(")
    for sub in ("src", "libs/dolphin/include"):
        for h in sorted((ROOT / sub).rglob("*.h")):
            try:
                if pat.search(h.read_text(errors="ignore")):
                    return str(h.relative_to(ROOT))
            except OSError:
                pass
    return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("queries", nargs="*", help="MexTK names or 0x addresses")
    ap.add_argument("--link", type=Path, default=DEFAULT_LINK)
    ap.add_argument("--used", type=Path, help="only names referenced here")
    ap.add_argument(
        "--headers", action="store_true", help="also locate declaring header"
    )
    args = ap.parse_args()

    if not args.link.exists():
        sys.exit(f"melee.link not found at {args.link}; pass --link")
    link = load_link(args.link)
    res = Resolver()

    rows = link
    if args.queries:
        rows = []
        by_name = {n: a for a, n in link}
        by_addr = {}
        for a, n in link:
            by_addr.setdefault(a, n)
        for q in args.queries:
            if q.lower().startswith("0x") or re.fullmatch(r"8[0-9a-fA-F]{7}", q):
                a = int(q, 16)
                rows.append((a, by_addr.get(a, "-")))
            elif q in by_name:
                rows.append((by_name[q], q))
            else:
                print(f"{q}\tnot in melee.link", file=sys.stderr)
    elif args.used:
        text = "\n".join(
            p.read_text(errors="ignore")
            for p in args.used.rglob("*")
            if p.suffix in (".c", ".h")
        )
        words = set(re.findall(r"[A-Za-z_]\w*", text))
        rows = [(a, n) for a, n in link if n in words]

    print("addr\tmex_name\tdecomp_name\tsection\tnote" + ("\theader" if args.headers else ""))
    for addr, mex in rows:
        name, section, note = res.resolve(addr)
        line = f"0x{addr:08X}\t{mex}\t{name}\t{section}\t{note}"
        if args.headers and name != "?":
            line += "\t" + find_source(name)
        print(line)


if __name__ == "__main__":
    main()
