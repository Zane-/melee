#!/usr/bin/env python3
"""Build the training overlay: compile mod sources, link, patch, check.

    tools/overlay_build.py            # build build/overlay/main.dol
    tools/overlay_build.py --clean
    tools/overlay_build.py --tm-debug # TM-CE units with TM_DEBUG (console, logs)

Steps:
  1. Requires an up-to-date matching build (build/GALE01/main.elf, main.dol).
     Run `ninja` in matching mode first; this script verifies the SHA-1.
  2. Compiles every .c under the native mod directories (decomp headers,
     MWCC 1.2.5n) into build/overlay/obj/.
  3. TM-CE: copies ../TrainingMode/{src,MexTK} (or $TMCE_DIR) to
     build/overlay/tmce/, applies src/tmce/patches/*.patch, compiles the units
     in src/tmce/units.txt plus src/tmce/*.c (MexTK headers, MWCC GC/3.0a5.2
     in C99 mode), renames each event's exports and generates the unit
     registry. See docs/ai/tmce-native.md.
  4. tools/overlay_link.py with config/GALE01/tm_hooks.txt, resolving MexTK
     names through MexTK/melee.link.
  5. tools/overlay_check.py on the result.

See docs/ai/overlay-build.md.
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from overlay_wrapper import compiler_prefix  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
# OVERLAY_OUT: build somewhere else (parallel work in one tree).
OUT = ROOT / os.environ.get("OVERLAY_OUT", "build/overlay")
MOD_DIRS = ["src/melee/tm", "src/melee/ai"]
HOOKS = ROOT / "config" / "GALE01" / "tm_hooks.txt"
# Per-area hook tables, config/GALE01/tm_hooks/<area>.txt. An area's code
# lives in src/melee/tm/<area>/. TM_EXCLUDE=area1,area2 leaves both out.
HOOKS_DIR = ROOT / "config" / "GALE01" / "tm_hooks"
EXCLUDE = [a for a in os.environ.get("TM_EXCLUDE", "").split(",") if a]
# The test runner (src/melee/tm/test, src/tmce/test_*.c, tm_hooks/test.txt)
# is only in test builds: TM_TEST=1 (tools/tmtest.py) also defines TM_TEST.
TM_TEST = os.environ.get("TM_TEST", "") not in ("", "0")
if not TM_TEST:
    EXCLUDE.append("test")
SYMBOLS = ROOT / "config" / "GALE01" / "tm_symbols.txt"
BASE_DOL = ROOT / "build" / "GALE01" / "main.dol"
BASE_SHA1 = (ROOT / "config" / "GALE01" / "build.sha1").read_text().split()[0]
BINUTILS = ROOT / "build" / "binutils"

# The vanilla __ArenaLo. overlay_link.py raises the arena past the overlay.
OVERLAY_ORIGIN = 0x804F0C00

MWCC = "build/compilers/GC/1.2.5n/mwcceppc.exe"

# The game's flags (configure.py cflags_base + optimized), without
# -DMUST_MATCH, plus the overlay flags.
CFLAGS = [
    "-nowraplines", "-cwd", "source", "-Cpp_exceptions", "off", "-proc", "gekko",
    "-fp", "hardware", "-align", "powerpc", "-nosyspath", "-fp_contract", "on",
    "-multibyte", "-enum", "int", "-nodefaults", "-pragma", "cats off",
    "-pragma", "warn_notinlined off", "-RTTI", "off",
    "-DBUILD_VERSION=0", "-DVERSION_GALE01", "-DTM_OVERLAY",
    "-maxerrors", "8", "-msgstyle", "gcc", "-warn", "off", "-requireprotos",
    "-i", "src", "-i", "libs/doldecomp/include", "-i", "src/MSL",
    "-i", "libs/dolphin/include", "-i", "build/GALE01/include",
    "-lang=c", "-O4,p", "-DNDEBUG=1", "-inline", "auto", "-sym", "off",
    # overlay-specific
    "-i", "src/melee/tm", "-prefix", "overlay_prefix.h",
    "-sdata", "0", "-sdata2", "0", "-str", "reuse,readonly",
]

# --- TM-CE (vendored C, built against MexTK) -------------------------------
TMCE_DIR = Path(os.environ.get("TMCE_DIR", ROOT.parent / "TrainingMode"))
TMCE_OURS = ROOT / "src" / "tmce"
TMCE_OUT = OUT / "tmce"
# TM-CE is C99 (gcc). 1.2.5n has no C99 mode; 3.0a5.2 does. Mod code does not
# have to match, so the newer compiler is fine.
TMCE_MWCC = "build/compilers/GC/3.0a5.2/mwcceppc.exe"
TMCE_TABLES = {"event": "evFunction", "css": "cssFunction"}


def extra_defines():
    """TM_DEFINES='A=1 B=x': extra -D flags for every mod file (test builds)."""
    import shlex
    out = ["-DTM_TEST=1"] if TM_TEST else []
    for d in shlex.split(os.environ.get("TM_DEFINES", "")):
        out += ["-D" + d]
    return out


def tmce_cflags(debug):
    rel = lambda p: str(p.relative_to(ROOT))  # noqa: E731
    return [
        "-nowraplines", "-cwd", "source", "-proc", "gekko", "-fp", "hardware",
        "-align", "powerpc", "-nosyspath", "-enum", "int", "-nodefaults",
        "-pragma", "cats off", "-Cpp_exceptions", "off", "-char", "unsigned",
        "-lang=c99", "-O4,p",
        "-inline", "auto",
        "-maxerrors", "8", "-msgstyle", "gcc", "-warn", "off",
        "-DTM_OVERLAY", *(["-DTM_DEBUG=1"] if debug else []), *extra_defines(),
        "-i", rel(TMCE_OURS / "include"), "-i", rel(TMCE_OURS),
        "-i", rel(TMCE_OUT / "src"), "-i", rel(TMCE_OUT / "MexTK" / "include"),
        "-i", rel(TMCE_OUT / "MexTK"),
        # overlay-specific (overlay_prefix.h lives in src/melee/tm)
        "-i", "src/melee/tm", "-prefix", "overlay_prefix.h",
        "-sdata", "0", "-sdata2", "0", "-str", "reuse,readonly",
    ]


def newest_mtime(dirs, pattern):
    newest = 0.0
    for d in dirs:
        for p in Path(d).rglob(pattern):
            newest = max(newest, p.stat().st_mtime)
    return newest


def compile_one(cc, flags, src: Path, obj: Path, dep_mtime: float, force: bool):
    obj.parent.mkdir(parents=True, exist_ok=True)
    if (not force and obj.exists() and obj.stat().st_mtime > src.stat().st_mtime
            and obj.stat().st_mtime > dep_mtime):
        return obj, None
    cmd = [*compiler_prefix(), cc, *flags, "-c", str(src.relative_to(ROOT)),
           "-o", str(obj.relative_to(ROOT))]
    if obj.exists():
        obj.unlink()
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    msg = (r.stdout + r.stderr).strip()
    if r.returncode != 0 or not obj.exists():
        return obj, f"{src.relative_to(ROOT)}:\n{msg}" if msg else \
            f"{src}: compiler failed with code {r.returncode}"
    if msg:
        print(msg)
    return obj, None


def compile_all(jobs, pool_size):
    with ThreadPoolExecutor(pool_size) as pool:
        results = list(pool.map(lambda j: compile_one(*j), jobs))
    failed = [m for _, m in results if m]
    for msg in failed:
        print(msg, file=sys.stderr)
    if failed:
        sys.exit(f"{len(failed)} of {len(jobs)} files failed to compile")
    return [o for o, _ in results]


def read_units():
    units = []
    for line in (TMCE_OURS / "units.txt").read_text().splitlines():
        line = line.split("#")[0].split()
        if not line:
            continue
        kind, name, *rest = line
        art = rest[-1]
        units.append(dict(kind=kind, name=name, sources=rest[:-1],
                          art=None if art == "-" else art))
    return units


def prepare_tmce_tree():
    """Copy TM-CE's sources and MexTK into the build dir and patch them."""
    for d in ("src", "MexTK"):
        if not (TMCE_DIR / d).is_dir():
            sys.exit(f"TM-CE checkout not found at {TMCE_DIR} (set TMCE_DIR)")
    stamp = TMCE_OUT / "tree.stamp"
    patches = sorted((TMCE_OURS / "patches").glob("*.patch"))
    newest = max([newest_mtime([TMCE_DIR / "src", TMCE_DIR / "MexTK"], "*")]
                 + [p.stat().st_mtime for p in patches])
    if stamp.exists() and stamp.stat().st_mtime > newest:
        return
    for d in ("src", "MexTK"):
        shutil.rmtree(TMCE_OUT / d, ignore_errors=True)
        shutil.copytree(TMCE_DIR / d, TMCE_OUT / d)
    for p in patches:
        r = subprocess.run(["patch", "-p1", "-s", "-d", str(TMCE_OUT), "-i", str(p)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"patch {p.name} does not apply to {TMCE_DIR}:\n{r.stdout}{r.stderr}")
    stamp.write_text("")


def binutil(tool, *args):
    r = subprocess.run([str(BINUTILS / f"powerpc-eabi-{tool}"), *map(str, args)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"{tool} failed: {r.stderr}")
    return r.stdout


def defined_symbols(obj):
    out = set()
    for line in binutil("nm", "--defined-only", obj).splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1].isupper():
            out.add(parts[2])
    return out


def mex_name_clashes():
    """MexTK names that vanilla uses for a different address.

    TM-CE means the MexTK function. Its objects get the name renamed to
    mex__NAME, which overlay_link.py resolves through melee.link.
    """
    mex = {}
    for line in (TMCE_OUT / "MexTK" / "melee.link").read_text().splitlines():
        addr, sep, name = line.strip().partition(":")
        if sep:
            mex[name.strip()] = int(addr, 16)
    clashes = []
    for line in binutil("nm", "--defined-only", "-g",
                        ROOT / "build" / "GALE01" / "main.elf").splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[2] in mex and int(parts[0], 16) != mex[parts[2]]:
            clashes.append(parts[2])
    return sorted(clashes)


def build_tmce(args):
    """Compile TM-CE; returns the object files to link."""
    prepare_tmce_tree()
    units = read_units()
    flags = tmce_cflags(args.tm_debug)
    dep = max(newest_mtime([TMCE_OUT / "src", TMCE_OUT / "MexTK", TMCE_OURS,
                            ROOT / "src" / "melee" / "tm"], "*.h"),
              (TMCE_OUT / "tree.stamp").stat().st_mtime)
    obj_dir = TMCE_OUT / "obj"

    jobs, unit_objs = [], {}
    for u in units:
        for s in u["sources"]:
            # "src/..." is a repo path (our own events, src/tmce/events);
            # anything else is a TM-CE source file.
            src_path = ROOT / s if s.startswith("src/") else TMCE_OUT / "src" / s
            stem = Path(s).stem
            if s.startswith("src/"):  # name objects after the unit (maps)
                stem = u["name"] if stem == "event" else f"{u['name']}_{stem}"
            obj = obj_dir / u["name"] / f"{stem}.o"
            jobs.append((TMCE_MWCC, flags, src_path, obj, dep, args.force))
            unit_objs.setdefault(u["name"], []).append(obj)
    # Area glue is src/tmce/<area>_*.c; TM_EXCLUDE leaves it out too.
    glue = sorted(p for p in TMCE_OURS.glob("*.c")
                  if not any(p.stem.startswith(a + "_") for a in EXCLUDE))
    # Custom events' EventDesc and data (src/tmce/events/<name>/desc.c).
    glue += sorted(TMCE_OURS.glob("events/*/desc.c"))
    def glue_obj(s):
        name = s.with_suffix(".o").name
        if s.parent != TMCE_OURS:  # events/<name>/desc.c
            name = f"{s.parent.name}_{name}"
        return obj_dir / "glue" / name

    for s in glue:
        jobs.append((TMCE_MWCC, flags, s, glue_obj(s),
                     dep, args.force))
    compile_all(jobs, args.j)

    # Each event/css unit was its own relocatable file in TM-CE and they all
    # export the same names. Keep only the table exports, renamed per unit.
    registry = []
    final = []
    clash_args = []
    for name in mex_name_clashes():
        clash_args += ["--redefine-sym", f"{name}=mex__{name}"]
    for u in units:
        objs = unit_objs[u["name"]]
        if u["kind"] == "core":
            for obj in objs:
                out = obj.with_suffix(".final.o")
                binutil("objcopy", *clash_args, obj, out)
                final.append(out)
            continue
        table = TMCE_TABLES[u["kind"]]
        exports = (TMCE_DIR / "MexTK" / f"{table}.txt").read_text().split()
        renamed = {e: f"tmce_{u['name']}_{e}" for e in exports}
        have = set()
        for obj in objs:
            out = obj.with_suffix(".final.o")
            cmd = list(clash_args)
            for old, new in renamed.items():
                cmd += ["--redefine-sym", f"{old}={new}", "-G", new]
            binutil("objcopy", *cmd, obj, out)
            have |= defined_symbols(out) & set(renamed.values())
            final.append(out)
        registry.append((u["name"], table, [renamed[e] if renamed[e] in have else None
                                             for e in exports]))

    # Generated registry (see src/tmce/tmce_registry.h).
    lines = ['#include "tmce_registry.h"', ""]
    for _, _, syms in registry:
        lines += [f"extern char {s}[];" for s in syms if s]
    lines += ["", "const TmceModule tmce_modules[] = {"]
    for name, table, syms in registry:
        funcs = ", ".join(s or "0" for s in syms)
        lines.append(f'    {{ "{name}", "{table}", {len(syms)}, {{ {funcs} }} }},')
    lines += ["};", f"const int tmce_module_count = {len(registry)};", ""]
    reg_c = TMCE_OUT / "tmce_registry.c"
    text = "\n".join(lines)
    if not reg_c.exists() or reg_c.read_text() != text:
        reg_c.write_text(text)
    final += compile_all([(TMCE_MWCC, flags, reg_c, obj_dir / "tmce_registry.o",
                           dep, args.force)], 1)
    final += [glue_obj(s) for s in glue]
    return final


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--force", action="store_true", help="recompile everything")
    ap.add_argument("--tm-debug", action="store_true",
                    help="build TM-CE units with TM_DEBUG")
    ap.add_argument("--no-tmce", action="store_true", help="native mod code only")
    ap.add_argument("-j", type=int, default=os.cpu_count())
    args = ap.parse_args()

    if args.clean:
        shutil.rmtree(OUT, ignore_errors=True)
        return 0

    if not BASE_DOL.exists():
        sys.exit("no matching build: run `ninja` in matching mode first")
    if hashlib.sha1(BASE_DOL.read_bytes()).hexdigest() != BASE_SHA1:
        sys.exit(f"{BASE_DOL} is not the retail DOL (wrong SHA-1). The overlay "
                 "must be laid over a matching build: reconfigure without "
                 "--non-matching and run ninja.")

    excluded = [ROOT / "src" / "melee" / "tm" / a for a in EXCLUDE]
    sources = sorted(p for d in MOD_DIRS for p in (ROOT / d).rglob("*.c")
                     if not any(x in p.parents for x in excluded))
    hdr = newest_mtime([ROOT / d for d in MOD_DIRS], "*.h")
    jobs = [(MWCC, CFLAGS + extra_defines(), s, OUT / "obj" / s.relative_to(ROOT).with_suffix(".o"),
             hdr, args.force) for s in sources]
    objs = compile_all(jobs, args.j)
    if not args.no_tmce:
        objs += build_tmce(args)
    if not objs:
        sys.exit("no mod sources")

    link = [sys.executable, "tools/overlay_link.py", "-o", str(OUT.relative_to(ROOT)),
            "--origin", hex(OVERLAY_ORIGIN), *[str(o.relative_to(ROOT)) for o in objs]]
    hook_files = [HOOKS] + sorted(p for p in HOOKS_DIR.glob("*.txt")
                                  if p.stem not in EXCLUDE)
    for hp in hook_files:
        if hp.exists():
            link += ["--hooks", str(hp.relative_to(ROOT))]
    if SYMBOLS.exists():
        link += ["--symbols", str(SYMBOLS.relative_to(ROOT))]
    if not args.no_tmce:
        link += ["--mex-link", str((TMCE_OUT / "MexTK" / "melee.link").relative_to(ROOT))]
    if subprocess.run(link, cwd=ROOT).returncode != 0:
        return 1
    check = [sys.executable, "tools/overlay_check.py", str(OUT / "main.dol"),
             "--patches", str(OUT / "patches.txt")]
    r = subprocess.run(check, cwd=ROOT, capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[-1] if r.returncode == 0 else r.stdout)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
