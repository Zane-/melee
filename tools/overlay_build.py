#!/usr/bin/env python3
"""Build the training overlay: compile mod sources, link, patch, check.

    tools/overlay_build.py            # build build/overlay/main.dol
    tools/overlay_build.py --clean

Steps:
  1. Requires an up-to-date matching build (build/GALE01/main.elf, main.dol).
     Run `ninja` in matching mode first; this script verifies the SHA-1.
  2. Compiles every .c under the mod source directories with the overlay
     flags into build/overlay/obj/.
  3. tools/overlay_link.py with config/GALE01/tm_hooks.txt.
  4. tools/overlay_check.py on the result.

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
OUT = ROOT / "build" / "overlay"
MOD_DIRS = ["src/melee/tm", "src/melee/ai"]
HOOKS = ROOT / "config" / "GALE01" / "tm_hooks.txt"
SYMBOLS = ROOT / "config" / "GALE01" / "tm_symbols.txt"
BASE_DOL = ROOT / "build" / "GALE01" / "main.dol"
BASE_SHA1 = (ROOT / "config" / "GALE01" / "build.sha1").read_text().split()[0]

# 0x804F0C00-0x804F1C00 is reserved for TmPersist (TM_PERSIST_RESERVED in
# src/melee/tm/tm.h, tm_persist in config/GALE01/tm_symbols.txt).
OVERLAY_ORIGIN = 0x804F1C00

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


def newest_header_mtime():
    newest = 0.0
    for d in MOD_DIRS:
        for p in (ROOT / d).rglob("*.h"):
            newest = max(newest, p.stat().st_mtime)
    return newest


def compile_one(src: Path, hdr_mtime: float, force: bool):
    rel = src.relative_to(ROOT)
    obj = OUT / "obj" / rel.with_suffix(".o")
    obj.parent.mkdir(parents=True, exist_ok=True)
    if (not force and obj.exists() and obj.stat().st_mtime > src.stat().st_mtime
            and obj.stat().st_mtime > hdr_mtime):
        return obj, None
    cmd = [*compiler_prefix(), MWCC, *CFLAGS,
           "-c", str(rel), "-o", str(obj.parent.relative_to(ROOT)) + "/"]
    if obj.exists():
        obj.unlink()
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    msg = (r.stdout + r.stderr).strip()
    if r.returncode != 0 or not obj.exists():
        return obj, msg or f"compiler failed with code {r.returncode}"
    if msg:
        print(msg)
    return obj, None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--force", action="store_true", help="recompile everything")
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

    sources = sorted(p for d in MOD_DIRS for p in (ROOT / d).rglob("*.c"))
    if not sources:
        sys.exit("no mod sources found under " + ", ".join(MOD_DIRS))

    hdr = newest_header_mtime()
    with ThreadPoolExecutor(args.j) as pool:
        results = list(pool.map(lambda s: compile_one(s, hdr, args.force), sources))
    failed = [(o, m) for o, m in results if m]
    for obj, msg in failed:
        print(msg, file=sys.stderr)
    if failed:
        sys.exit(f"{len(failed)} of {len(sources)} files failed to compile")
    objs = [str(o.relative_to(ROOT)) for o, _ in results]

    link = [sys.executable, "tools/overlay_link.py", "-o", str(OUT.relative_to(ROOT)),
            "--origin", hex(OVERLAY_ORIGIN), *objs]
    if HOOKS.exists():
        link += ["--hooks", str(HOOKS.relative_to(ROOT))]
    if SYMBOLS.exists():
        link += ["--symbols", str(SYMBOLS.relative_to(ROOT))]
    if subprocess.run(link, cwd=ROOT).returncode != 0:
        return 1
    check = [sys.executable, "tools/overlay_check.py", str(OUT / "main.dol"),
             "--patches", str(OUT / "patches.txt")]
    r = subprocess.run(check, cwd=ROOT, capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[-1] if r.returncode == 0 else r.stdout)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
