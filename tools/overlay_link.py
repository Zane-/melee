#!/usr/bin/env python3
"""Link mod objects as an overlay and append them to the matching DOL.

The vanilla image is never relinked. The overlay objects are linked on their
own at a fixed address above the vanilla image, with every vanilla symbol they
reference supplied as an absolute address taken from the matching ELF. The
resulting sections are appended to the matching DOL in spare section slots.

Usage:
    tools/overlay_link.py -o OUT_DIR OBJ [OBJ...]
        [--base-elf build/GALE01/main.elf] [--base-dol build/GALE01/main.dol]
        [--origin 0x804F0C00] [--keep SYMBOL ...]

Hook table (--hooks), one hook per line, '#' comments allowed:
    call      SITE  TARGET  [note]   retarget the `bl` at SITE to overlay TARGET
    function  SITE  TARGET  [note]   write `b TARGET` at SITE (a function entry)
    word      SITE  VALUE   [note]   overwrite the 32-bit word at SITE
SITE is `vanilla_symbol`, `vanilla_symbol+0xOFF` or a hex address. TARGET is an
overlay global. For `call`, the overlay function must have the signature of
the function originally called, and normally calls it itself.

Outputs in OUT_DIR: overlay.lcf, overlay.elf, overlay.map, main.dol,
overlay_symbols.txt (name -> address of every overlay global), patches.txt
(every vanilla address changed; feed it to tools/overlay_check.py --patches).

Mod objects must be compiled so that nothing lands in vanilla section names:
    -prefix overlay_prefix.h -i src/melee/tm    (src/melee/tm/overlay_prefix.h)
    -sdata 0 -sdata2 0 -str reuse,readonly
Only .tmtext and .tmrodata are accepted; writable statics are an error.
See docs/ai/overlay-build.md.
"""

import argparse
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WRAPPER = ROOT / "tools" / "wibo_macos_wrapper.py"
MWLD = ROOT / "build" / "compilers" / "GC" / "1.3.2" / "mwldeppc.exe"
SLIPPI = ROOT / "config" / "GALE01" / "slippi_injections.txt"

# output section name -> DOL slot kind
OVERLAY_SECTIONS = [(".tmtext", "text"), (".tmrodata", "data")]
ALLOWED_INPUT = {name for name, _ in OVERLAY_SECTIONS}
WRITABLE = {".tmdata", ".tmbss"}
SHT_SYMTAB, SHT_NOBITS, SHF_ALLOC = 2, 8, 2
STB_LOCAL, STB_GLOBAL = 0, 1
STT_FUNC = 2


# (address of `lis r3, X@ha`, expected vanilla words for lis/addi) in OSInit.
ARENA_SITES = [
    (0x80343094, (0x3C60804F, 0x38630C00)),  # &__ArenaLo
    (0x803430CC, (0x3C60804F, 0x3863EC00)),  # &_stack_addr (retail debug flag)
]


def dol_offset(h, addr):
    for i in range(18):
        if h[36 + i] and h[18 + i] <= addr < h[18 + i] + h[36 + i]:
            return h[i] + addr - h[18 + i]
    sys.exit(f"address {addr:08X} is not in the DOL")


class Elf:
    def __init__(self, path: Path):
        self.path = path
        d = self.data = path.read_bytes()
        if d[:4] != b"\x7fELF" or d[5] != 2:
            sys.exit(f"{path}: not a big-endian ELF")
        shoff = struct.unpack_from(">I", d, 0x20)[0]
        shentsize, shnum, shstrndx = struct.unpack_from(">HHH", d, 0x2E)
        self.sections = []
        for i in range(shnum):
            n, t, f, addr, off, size, link, info, al, es = struct.unpack_from(
                ">10I", d, shoff + i * shentsize
            )
            self.sections.append(
                dict(n=n, type=t, flags=f, addr=addr, off=off, size=size, link=link)
            )
        st = self.sections[shstrndx]
        strs = d[st["off"] : st["off"] + st["size"]]
        for s in self.sections:
            s["name"] = strs[s["n"] : strs.index(b"\0", s["n"])].decode()
        self.symbols = []  # (name, value, size, bind, type, shndx)
        for s in self.sections:
            if s["type"] != SHT_SYMTAB:
                continue
            st = self.sections[s["link"]]
            sd = d[st["off"] : st["off"] + st["size"]]
            for k in range(s["size"] // 16):
                nm, val, sz, info, _, shndx = struct.unpack_from(
                    ">IIIBBH", d, s["off"] + k * 16
                )
                name = sd[nm : sd.index(b"\0", nm)].decode("latin1")
                self.symbols.append((name, val, sz, info >> 4, info & 15, shndx))

    def section_data(self, s):
        return self.data[s["off"] : s["off"] + s["size"]]


def read_dol(path: Path):
    d = path.read_bytes()
    h = list(struct.unpack(">57I", d[:0xE4]))
    return d, h


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("objects", nargs="+", type=Path)
    ap.add_argument("-o", "--out-dir", type=Path, required=True)
    ap.add_argument("--base-elf", type=Path, default=ROOT / "build/GALE01/main.elf")
    ap.add_argument("--base-dol", type=Path, default=ROOT / "build/GALE01/main.dol")
    ap.add_argument("--origin", type=lambda x: int(x, 0), default=0x804F0C00)
    ap.add_argument("--hooks", type=Path, help="hook table (see module docstring)")
    ap.add_argument("--keep", nargs="*", default=None,
                    help="symbols to force-keep (default: all overlay globals)")
    args = ap.parse_args()
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    # 1. Inspect overlay objects: forbidden sections, defined and undefined symbols.
    defined, undefined, errors = {}, set(), []
    for path in args.objects:
        obj = Elf(path)
        for s in obj.sections:
            if s["size"] and s["name"] in WRITABLE:
                errors.append(
                    f"{path}: has writable static data ({s['name']}, 0x{s['size']:X} "
                    f"bytes). Overlay state must be heap-allocated; make tables const."
                )
            elif s["flags"] & SHF_ALLOC and s["size"] and s["name"] not in ALLOWED_INPUT:
                errors.append(
                    f"{path}: section {s['name']} (0x{s['size']:X} bytes) is not an "
                    f"overlay section; compile with the overlay prefix and -sdata 0 -sdata2 0 -str reuse,readonly"
                )
        for name, val, sz, bind, typ, shndx in obj.symbols:
            if not name:
                continue
            if shndx == 0:
                undefined.add(name)
            elif bind == STB_GLOBAL:
                if name in defined:
                    errors.append(f"duplicate overlay symbol {name}")
                defined[name] = path
    if errors:
        sys.exit("\n".join(errors))
    undefined -= set(defined)

    # 2. Resolve undefined symbols against the matching ELF.
    base = Elf(args.base_elf)
    globals_, locals_ = {}, {}
    for name, val, sz, bind, typ, shndx in base.symbols:
        if not name or shndx == 0:
            continue
        if bind == STB_GLOBAL:
            globals_[name] = val
        elif bind == STB_LOCAL:
            locals_.setdefault(name, set()).add(val)
    clash = sorted(set(defined) & set(globals_))
    if clash:
        sys.exit("overlay redefines vanilla symbols: " + ", ".join(clash[:10]))
    resolved, missing = {}, []
    for name in sorted(undefined):
        if name in globals_:
            resolved[name] = globals_[name]
        elif name in locals_ and len(locals_[name]) == 1:
            resolved[name] = next(iter(locals_[name]))  # unique vanilla static
        else:
            why = "ambiguous static" if name in locals_ else "not in vanilla"
            missing.append(f"{name} ({why})")
    if missing:
        sys.exit("unresolved overlay references: " + ", ".join(missing))
    # 3. Linker script.
    keep = args.keep if args.keep is not None else sorted(defined)
    if not keep:
        sys.exit("overlay defines no global symbols")
    lcf = ["MEMORY", "{", f"    overlay : origin = 0x{args.origin:08X}", "}", "",
           "SECTIONS", "{", "    GROUP:", "    {"]
    lcf += [f"        {name} ALIGN(0x20):{{}}" for name, _ in OVERLAY_SECTIONS]
    lcf += ["    } > overlay", ""]
    lcf += [f"    {name} = 0x{addr:08X};" for name, addr in resolved.items()]
    lcf += ["}", "", "FORCEACTIVE", "{"] + [f"    {k}" for k in keep] + ["}", ""]
    lcf_path = out / "overlay.lcf"
    lcf_path.write_text("\n".join(lcf))

    # 4. Link the overlay on its own.
    elf_path = out / "overlay.elf"
    rsp = out / "overlay.rsp"
    rsp.write_text("\n".join(str(o) for o in args.objects) + "\n")
    cmd = [str(WRAPPER), str(MWLD), "-fp", "hardware", "-nodefaults", "-warn", "off",
           "-msgstyle", "std",
           # The linker needs an entry symbol defined in an object; it is unused.
           "-main", keep[0], "-map", str(out / "overlay.map"),
           "-lcf", str(lcf_path), "-o", str(elf_path), f"@{rsp}"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.stdout.strip() or r.stderr.strip():
        print(r.stdout + r.stderr, file=sys.stderr)
    if r.returncode != 0 or not elf_path.exists():
        sys.exit("overlay link failed")

    # 5. Append overlay sections to the matching DOL.
    linked = Elf(elf_path)
    dol, h = read_dol(args.base_dol)
    dol = bytearray(dol)
    free = {
        "text": [i for i in range(0, 7) if h[36 + i] == 0],
        "data": [i for i in range(7, 18) if h[36 + i] == 0],
    }
    placed = []
    kinds = dict(OVERLAY_SECTIONS)
    for s in linked.sections:
        if s["name"] not in kinds or not s["size"]:
            continue
        if s["type"] == SHT_NOBITS:
            sys.exit(f"{s['name']} is uninitialised data; overlay state must be on the heap")
        if not free[kinds[s["name"]]]:
            sys.exit(f"no free DOL {kinds[s['name']]} slot for {s['name']}")
        slot = free[kinds[s["name"]]].pop(0)
        while len(dol) % 0x20:
            dol.append(0)
        data = linked.section_data(s)
        data += b"\0" * (-len(data) % 0x20)
        h[slot], h[18 + slot], h[36 + slot] = len(dol), s["addr"], len(data)
        dol += data
        placed.append((s["name"], s["addr"], len(data)))
    if not placed:
        sys.exit("overlay link produced no sections (everything dead-stripped?)")
    dol[:0xE4] = struct.pack(">57I", *h)

    # 6. Raise the arena start past the overlay. OSInit sets the arena low
    # bound from __ArenaLo, or from _stack_addr when the disc's debug flag is
    # below 2 (the retail case). Point both at the end of the overlay,
    # otherwise the heaps are created on top of it and OSInit zeroes it.
    end = max(a + n for _, a, n in placed)
    new_lo = (end + 0x1F) & ~0x1F
    patches = []
    for site, old in ARENA_SITES:
        off = dol_offset(h, site)
        have = struct.unpack_from(">II", dol, off)
        if have != old:
            sys.exit(f"arena site {site:08X}: expected {old[0]:08X} {old[1]:08X}, "
                     f"found {have[0]:08X} {have[1]:08X}")
        hi = ((new_lo + 0x8000) >> 16) & 0xFFFF
        lo = new_lo & 0xFFFF
        struct.pack_into(">II", dol, off, (old[0] & 0xFFFF0000) | hi,
                         (old[1] & 0xFFFF0000) | lo)
        patches.append((site, 8, f"arena low -> {new_lo:08X}"))
    # 7. Hooks.
    if args.hooks:
        ov = {name: val for name, val, sz, bind, typ, shndx in linked.symbols
              if bind == STB_GLOBAL and shndx not in (0, 0xFFF1)}

        slippi = {}
        if SLIPPI.exists():
            for line in SLIPPI.read_text().splitlines():
                if line.strip() and not line.startswith("#"):
                    addr, _, name = line.split(None, 2)
                    slippi[int(addr, 16)] = name
        sizes = {val: sz for name, val, sz, bind, typ, shndx in base.symbols
                 if typ == STT_FUNC and sz}

        def site_addr(text):
            sym, _, offs = text.partition("+")
            try:
                return int(sym, 16) if not offs and len(sym) == 8 else None
            except ValueError:
                return None

        def vanilla(text):
            raw = site_addr(text)
            if raw is not None:
                return raw
            sym, _, offs = text.partition("+")
            if sym in globals_:
                addr = globals_[sym]
            elif sym in locals_ and len(locals_[sym]) == 1:
                addr = next(iter(locals_[sym]))
            else:
                sys.exit(f"hook site {text}: unknown or ambiguous vanilla symbol")
            return addr + (int(offs, 0) if offs else 0)

        def branch(frm, to, link):
            d = to - frm
            if not -0x2000000 <= d < 0x2000000:
                sys.exit(f"branch {frm:08X} -> {to:08X} out of range")
            return 0x48000000 | (d & 0x03FFFFFC) | (1 if link else 0)

        for ln, line in enumerate(args.hooks.read_text().splitlines(), 1):
            line = line.split("#")[0].strip()
            if not line:
                continue
            parts = line.split(None, 3)
            if len(parts) < 3:
                sys.exit(f"{args.hooks}:{ln}: expected KIND SITE TARGET [note]")
            kind, site_s, target = parts[:3]
            note = parts[3] if len(parts) > 3 else ""
            site = vanilla(site_s)
            off = dol_offset(h, site)
            old = struct.unpack_from(">I", dol, off)[0]
            if kind == "word":
                new = int(target, 0)
            else:
                if target not in ov:
                    sys.exit(f"{args.hooks}:{ln}: {target} is not an overlay global")
                if kind == "call":
                    if old >> 26 != 18 or old & 3 != 1:
                        sys.exit(f"{args.hooks}:{ln}: {site_s} ({site:08X}) is "
                                 f"{old:08X}, not a `bl`")
                    new = branch(site, ov[target], True)
                elif kind == "function":
                    new = branch(site, ov[target], False)
                else:
                    sys.exit(f"{args.hooks}:{ln}: unknown hook kind {kind}")
            if site in slippi:
                sys.exit(f"{args.hooks}:{ln}: {site_s} ({site:08X}) is patched by "
                         f"Slippi ({slippi[site]})")
            if kind == "function":
                size = sizes.get(site, 0)
                inside = [x for x in slippi if site <= x < site + size]
                if inside:
                    sys.exit(f"{args.hooks}:{ln}: cannot replace {site_s}: Slippi "
                             "patches inside it at "
                             + ", ".join(f"{x:08X}" for x in sorted(inside))
                             + ". Use a `call` hook instead.")
                if not size:
                    sys.exit(f"{args.hooks}:{ln}: {site_s} is not the start of a "
                             "vanilla function")
            struct.pack_into(">I", dol, off, new)
            patches.append((site, 4, f"{kind} {site_s} -> {target} {note}".strip()))

    (out / "main.dol").write_bytes(dol)
    (out / "patches.txt").write_text(
        "# Patch sites applied by tools/overlay_link.py\n"
        + "".join(f"{a:08X} {n} {note}\n" for a, n, note in patches)
    )

    syms = sorted(
        (val, name) for name, val, sz, bind, typ, shndx in linked.symbols
        if bind == STB_GLOBAL and shndx not in (0, 0xFFF1) and name in defined
    )
    (out / "overlay_symbols.txt").write_text(
        "".join(f"{val:08X} {name}\n" for val, name in syms)
    )

    for name, addr, size in placed:
        print(f"{name:10s} {addr:08X}-{addr + size:08X}")
    print(f"overlay end {end:08X} ({end - args.origin} bytes), "
          f"{len(resolved)} vanilla refs, {len(syms)} overlay globals")
    print(f"arena low raised to {new_lo:08X}, {len(patches)} patch sites")
    print(f"wrote {out / 'main.dol'}")


if __name__ == "__main__":
    main()
