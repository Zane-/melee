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
    slippi-word SITE VALUE  [note]   same, but SITE must be a Slippi injection
                                     whose required code makes the same change
                                     (e.g. unlock-all). Only for plain Dolphin:
                                     Slippi applies its codes after the DOL
                                     loads, so its version wins under Slippi
    pointer   SITE  TARGET  [note]   store TARGET's address in the data word at SITE
    inject    SITE  TARGET  [note]   replace the instruction at SITE with a branch
                                     to a generated trampoline that calls
                                     `void TARGET(TmRegs*)`, then runs the
                                     displaced instruction and returns
SITE is `vanilla_symbol`, `vanilla_symbol+0xOFF` or a hex address. TARGET is an
overlay global. For `call`, the overlay function must have the signature of
the function originally called, and normally calls it itself.

Outputs in OUT_DIR: overlay.lcf, overlay.elf, overlay.map, main.dol,
overlay_symbols.txt (name -> address of every overlay global), patches.txt
(every vanilla address changed; feed it to tools/overlay_check.py --patches).

Mod objects must be compiled so that nothing lands in vanilla section names:
    -prefix overlay_prefix.h -i src/melee/tm    (src/melee/tm/overlay_prefix.h)
    -sdata 0 -sdata2 0 -str reuse,readonly
Accepted input sections: .tmtext, .tmrodata, .tmdata, .tmbss. Writable statics
are allowed (decided 2026-11-11) but are NOT saved by Slippi's rollback: code
that runs during netplay keeps its state under the tm_state heap root.
.tmbss is emitted as zero-filled data.

--mex-link FILE resolves MexTK names (TM-CE code) through MexTK's melee.link,
but only to addresses where a vanilla symbol starts.
See docs/ai/overlay-build.md.
"""

import argparse
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from overlay_wrapper import wrapper  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MWLD = ROOT / "build" / "compilers" / "GC" / "1.3.2" / "mwldeppc.exe"
SLIPPI = ROOT / "config" / "GALE01" / "slippi_injections.txt"

# output section name -> DOL slot kind
OVERLAY_SECTIONS = [(".tmtext", "text"), (".tmrodata", "data"),
                    (".tmdata", "data"), (".tmbss", "data")]
ALLOWED_INPUT = {name for name, _ in OVERLAY_SECTIONS}
SHT_SYMTAB, SHT_NOBITS, SHF_ALLOC = 2, 8, 2
STB_LOCAL, STB_GLOBAL = 0, 1
STT_FUNC = 2


# (address of `lis r3, X@ha`, expected vanilla words for lis/addi) in OSInit.
ARENA_SITES = [
    (0x80343094, (0x3C60804F, 0x38630C00)),  # &__ArenaLo
    (0x803430CC, (0x3C60804F, 0x3863EC00)),  # &_stack_addr (retail debug flag)
]


INJECT_FRAME = 0x110


def inject_trampoline(at, target, displaced, resume, branch):
    """Machine code for an `inject` hook.

    Saves r0, LR, CR, CTR, XER, r3-r31 and f0-f13 in a stack frame, calls
    `void target(TmRegs* regs)` (see src/melee/tm/tm_hook.h) with a pointer to
    the saved registers, restores them (so the target may edit them), runs the
    displaced instruction and branches back to the instruction after the site.
    """
    c = [
        0x94210000 | (-INJECT_FRAME & 0xFFFF),  # stwu r1,-0x110(r1)
        0x90010008,  # stw r0,0x08(r1)
        0x7C0802A6, 0x9001000C,  # mflr r0 ; stw r0,0x0C(r1)
        0x7C000026, 0x90010010,  # mfcr r0 ; stw r0,0x10(r1)
        0x7C0902A6, 0x90010014,  # mfctr r0 ; stw r0,0x14(r1)
        0x7C0102A6, 0x90010018,  # mfxer r0 ; stw r0,0x18(r1)
        0xBC610020,  # stmw r3,0x20(r1)
    ]
    c += [0xD8010000 | (n << 21) | (0x98 + 8 * n) for n in range(14)]  # stfd fN
    c.append(0x38610008)  # addi r3,r1,8
    c.append(branch(at + 4 * len(c), target, True))
    c += [0xC8010000 | (n << 21) | (0x98 + 8 * n) for n in range(14)]  # lfd fN
    c += [
        0x80010010, 0x7C0FF120,  # lwz r0,0x10(r1) ; mtcr r0
        0x80010014, 0x7C0903A6,  # lwz r0,0x14(r1) ; mtctr r0
        0x80010018, 0x7C0103A6,  # lwz r0,0x18(r1) ; mtxer r0
        0x8001000C, 0x7C0803A6,  # lwz r0,0x0C(r1) ; mtlr r0
        0xB8610020,  # lmw r3,0x20(r1)
        0x80010008,  # lwz r0,0x08(r1)
        0x38210000 | INJECT_FRAME,  # addi r1,r1,0x110
        displaced,
    ]
    c.append(branch(at + 4 * len(c), resume, False))
    return c


# EABI register save/restore helpers. Compilers with a C99 mode (GC 3.0+, used
# for the TM-CE units) call _savegpr_N/_restgpr_N/_savefpr_N/_restfpr_N in
# prologues and epilogues; vanilla Melee never does, so its DOL has none.
# Same sequences as src/Runtime/eabi_save_restore.s, generated here so the
# overlay needs no assembly source. r11 points just past the save area.
RUNTIME_KINDS = [  # (name prefix, opcode, slot size)
    ("_savegpr_", 0x90000000, 4), ("_restgpr_", 0x80000000, 4),  # stw / lwz
    ("_savefpr_", 0xD8000000, 8), ("_restfpr_", 0xC8000000, 8),  # stfd / lfd
]


def runtime_helpers(base):
    """Returns (machine words, {symbol: address}) for the block at base."""
    words, syms = [], {}
    for prefix, op, size in RUNTIME_KINDS:
        for n in range(14, 32):
            syms[f"{prefix}{n}"] = base + 4 * len(words)
            off = -size * (32 - n)
            words.append(op | (n << 21) | (11 << 16) | (off & 0xFFFF))
        words.append(0x4E800020)  # blr
    return words, syms


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
    ap.add_argument("--hooks", type=Path, action="append", default=[],
                    help="hook table (see module docstring); may be repeated")
    ap.add_argument("--symbols", type=Path,
                    help="extra absolute symbols for the overlay, lines of NAME ADDRESS")
    ap.add_argument("--mex-link", type=Path,
                    help="MexTK melee.link (ADDRESS:NAME lines) for TM-CE code")
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
            if s["flags"] & SHF_ALLOC and s["size"] and s["name"] not in ALLOWED_INPUT:
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
    extra = {}
    if args.symbols and args.symbols.exists():
        for line in args.symbols.read_text().splitlines():
            line = line.split("#")[0].split()
            if len(line) >= 2:
                extra[line[0]] = int(line[1], 16)
    clash = sorted(set(extra) & (set(globals_) | set(defined)))
    if clash:
        sys.exit("extra symbols clash with existing ones: " + ", ".join(clash))
    globals_.update(extra)
    mex = {}
    if args.mex_link:
        starts = {val for name, val, sz, bind, typ, shndx in base.symbols
                  if name and shndx != 0}
        for line in args.mex_link.read_text().splitlines():
            addr, sep, name = line.strip().partition(":")
            if sep:
                mex[name.strip()] = (int(addr, 16), int(addr, 16) in starts)
    resolved, missing = {}, []
    runtime_words = []
    link_origin = args.origin
    if any(n.startswith(tuple(k[0] for k in RUNTIME_KINDS)) for n in undefined):
        runtime_words, rt_syms = runtime_helpers(args.origin)
        link_origin = (args.origin + 4 * len(runtime_words) + 0x1F) & ~0x1F
        for name in list(undefined):
            if name in rt_syms:
                resolved[name] = rt_syms[name]
                undefined.discard(name)
    for name in sorted(undefined):
        if name in globals_:
            resolved[name] = globals_[name]
            if name in mex and mex[name][0] != globals_[name]:
                errors.append(f"{name}: melee.link says {mex[name][0]:08X}, "
                              f"vanilla has it at {globals_[name]:08X}")
        elif name in mex or (name.startswith("mex__") and name[5:] in mex):
            addr, is_start = mex[name[5:] if name.startswith("mex__") else name]
            if not is_start:
                missing.append(f"{name} (melee.link {addr:08X} is not a vanilla "
                               "symbol; m-ex code? reimplement it in src/tmce)")
            resolved[name] = addr
        elif name in locals_ and len(locals_[name]) == 1:
            resolved[name] = next(iter(locals_[name]))  # unique vanilla static
        else:
            why = "ambiguous static" if name in locals_ else "not in vanilla"
            missing.append(f"{name} ({why})")
    if errors:
        sys.exit("\n".join(errors))
    if missing:
        sys.exit("unresolved overlay references: " + ", ".join(missing))
    # 3. Linker script.
    keep = args.keep if args.keep is not None else sorted(defined)
    if not keep:
        sys.exit("overlay defines no global symbols")
    lcf = ["MEMORY", "{", f"    overlay : origin = 0x{link_origin:08X}", "}", "",
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
    cmd = [*wrapper(), str(MWLD), "-fp", "hardware", "-nodefaults", "-warn", "off",
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

    def append_section(name, kind, addr, data):
        if not free[kind]:
            sys.exit(f"no free DOL {kind} slot for {name}")
        slot = free[kind].pop(0)
        while len(dol) % 0x20:
            dol.append(0)
        data = bytes(data) + b"\0" * (-len(data) % 0x20)
        h[slot], h[18 + slot], h[36 + slot] = len(dol), addr, len(data)
        dol.extend(data)
        placed.append((name, addr, len(data)))

    if runtime_words:
        append_section(".tmrt", "text", args.origin,
                       struct.pack(f">{len(runtime_words)}I", *runtime_words))
    for s in linked.sections:
        if s["name"] not in kinds or not s["size"]:
            continue
        data = (bytes(s["size"]) if s["type"] == SHT_NOBITS
                else linked.section_data(s))
        append_section(s["name"], kinds[s["name"]], s["addr"], data)
    if not placed:
        sys.exit("overlay link produced no sections (everything dead-stripped?)")

    # 6. Hooks. Patches are collected first and written at the end, because
    # `inject` hooks add a trampoline section that moves the overlay end.
    patches = []  # (addr, [words], note)
    trampolines = bytearray()
    tramp_base = (max(a + n for _, a, n in placed) + 0x1F) & ~0x1F
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
        text_ranges = [(h[18 + i], h[18 + i] + h[36 + i]) for i in range(7)
                       if h[36 + i] and h[18 + i] < args.origin]

        def vanilla(text):
            sym, _, offs = text.partition("+")
            if not offs and len(sym) == 8:
                try:
                    return int(sym, 16)
                except ValueError:
                    pass
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

        seen = {}
        hook_lines = [(f"{hp}:{ln}", line) for hp in args.hooks
                      for ln, line in enumerate(hp.read_text().splitlines(), 1)]
        for where, line in hook_lines:
            line = line.split("#")[0].strip()
            if not line:
                continue
            parts = line.split(None, 3)
            if len(parts) < 3:
                sys.exit(f"{where}: expected KIND SITE TARGET [note]")
            kind, site_s, target = parts[:3]
            note = parts[3] if len(parts) > 3 else ""
            site = vanilla(site_s)
            if site in seen:
                sys.exit(f"{where}: {site_s} already hooked at {seen[site]}")
            seen[site] = where
            old = struct.unpack_from(">I", dol, dol_offset(h, site))[0]
            in_text = any(a <= site < b for a, b in text_ranges)
            if kind == "slippi-word":
                if site not in slippi:
                    sys.exit(f"{where}: {site_s} ({site:08X}) is not a Slippi site; "
                             "use `word`")
            elif site in slippi:
                sys.exit(f"{where}: {site_s} ({site:08X}) is patched by Slippi "
                         f"({slippi[site]})")
            if kind in ("word", "slippi-word"):
                new = int(target, 0)
            elif target not in ov:
                sys.exit(f"{where}: {target} is not an overlay global")
            elif kind == "pointer":
                if in_text:
                    sys.exit(f"{where}: {site_s} is code; `pointer` is for data slots")
                new = ov[target]
            elif not in_text:
                sys.exit(f"{where}: {site_s} ({site:08X}) is not in vanilla code")
            elif kind == "call":
                if old >> 26 != 18 or old & 3 != 1:
                    sys.exit(f"{where}: {site_s} ({site:08X}) is {old:08X}, not a `bl`")
                new = branch(site, ov[target], True)
            elif kind == "function":
                size = sizes.get(site, 0)
                if not size:
                    sys.exit(f"{where}: {site_s} is not the start of a vanilla function")
                inside = [x for x in slippi if site <= x < site + size]
                if inside:
                    sys.exit(f"{where}: cannot replace {site_s}: Slippi patches inside "
                             "it at " + ", ".join(f"{x:08X}" for x in sorted(inside))
                             + ". Use a `call` or `inject` hook instead.")
                new = branch(site, ov[target], False)
            elif kind == "inject":
                op = old >> 26
                if op in (16, 18) or (op == 19 and (old >> 1) & 0x3FF in (16, 528)):
                    sys.exit(f"{where}: {site_s} ({site:08X}) is a branch ({old:08X}); "
                             "inject on a neighbouring instruction or use `call`")
                at = tramp_base + len(trampolines)
                code = inject_trampoline(at, ov[target], old, site + 4, branch)
                trampolines.extend(struct.pack(f">{len(code)}I", *code))
                new = branch(site, at, False)
            else:
                sys.exit(f"{where}: unknown hook kind {kind}")
            patches.append((site, [new], f"{kind} {site_s} -> {target} {note}".strip()))

    if trampolines:
        append_section(".tmtramp", "text", tramp_base, trampolines)

    # 7. Raise the arena start past the overlay. OSInit sets the arena low
    # bound from __ArenaLo, or from _stack_addr when the disc's debug flag is
    # below 2 (the retail case). Point both at the end of the overlay,
    # otherwise the heaps are created on top of it and OSInit zeroes it.
    end = max(a + n for _, a, n in placed)
    new_lo = (end + 0x1F) & ~0x1F
    for site, old in ARENA_SITES:
        have = struct.unpack_from(">II", dol, dol_offset(h, site))
        if have != old:
            sys.exit(f"arena site {site:08X}: expected {old[0]:08X} {old[1]:08X}, "
                     f"found {have[0]:08X} {have[1]:08X}")
        hi = ((new_lo + 0x8000) >> 16) & 0xFFFF
        words = [(old[0] & 0xFFFF0000) | hi, (old[1] & 0xFFFF0000) | (new_lo & 0xFFFF)]
        patches.append((site, words, f"arena low -> {new_lo:08X}"))

    dol[:0xE4] = struct.pack(">57I", *h)
    for site, words, note in patches:
        struct.pack_into(f">{len(words)}I", dol, dol_offset(h, site), *words)
    (out / "main.dol").write_bytes(dol)
    (out / "patches.txt").write_text(
        "# Patch sites applied by tools/overlay_link.py\n"
        + "".join(f"{a:08X} {4 * len(w)} {note}\n" for a, w, note in sorted(patches))
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
