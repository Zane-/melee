#!/usr/bin/env python3
"""Build the native (32-bit Linux) headless game: build/native/melee_headless.

The game's own sources are compiled for the host by upstream's CMake preset
(`native`), into libmelee.a, with the generated archive readers. This script
adds what a program needs on top:

- the vanilla files that preset leaves out, compiled unchanged with a shim
  header (src/host/shim.h) for the SDK declarations they need;
- the host platform layer (src/host/): memory, time, disc, pads, and
  graphics and audio as no-ops;
- Aurora's C matrix and vector functions;
- a generated stub, returning 0, for every SDK function still missing.

Needs (see docs/ai/native-port.md): a multilib gcc, the Aurora headers, and
the archive tool and type table built through Nix:

    nix build .#melee-dwarf -o build/nix/dwarf
    nix build .#melee-dat   -o build/nix/melee-dat
    build/nix/melee-dat/bin/melee-dat types export \\
        -o build/GALE01/dat/types.bin --dwarf build/nix/dwarf/melee.elf

Usage: python tools/native_build.py [--opt LEVEL] [--no-cmake]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "native"
OBJ = OUT / "host"
AURORA = Path(os.environ.get("AURORA_SRC", ROOT / "build/deps/aurora"))
MELEE_DAT = ROOT / "build/nix/melee-dat/bin/melee-dat"

# Floating point is done in SSE, in the precision the source asks for, as
# the console's FPU does; x87 would compute everything in extended precision.
BASE_FLAGS = [
    "-m32", "-std=gnu2x", "-g", "-fno-pie", "-fno-strict-aliasing",
    "-fwrapv", "-fno-delete-null-pointer-checks", "-fno-omit-frame-pointer",
    "-msse2", "-mfpmath=sse", "-ffp-contract=off", "-w",
]
DEFINES = ["-DTARGET_PC", "-Dbool=int"]

# Vanilla files built here, unchanged: the ones upstream's preset excludes,
# and any file one of whose functions the host layer replaces. A
# `-Dname=name_vanilla` renames that function so src/host/ can supply its
# own: the native counterpart of the overlay's `function` hook. (An object
# linked here defines everything its copy in libmelee.a does, so that copy
# is never pulled in.)
VANILLA = {
    "melee/gm/gmmain.c": ["-Dmain=game_main"],
    "melee/lb/lb_0195.c": ["-Dlb_80019894=lb_80019894_vanilla"],
    "melee/lb/lbcardnew.c": [],
    "sysdolphin/baselib/fog.c": [],
    "sysdolphin/baselib/pobj.c": [],
    "sysdolphin/baselib/sislib_font.c": [],
    "sysdolphin/baselib/hsd_3915.c": [],
    "sysdolphin/baselib/video.c": [
        "-DHSD_VICopyXFBAsync=HSD_VICopyXFBAsync_vanilla",
        "-DHSD_VIWaitXFBFlush=HSD_VIWaitXFBFlush_vanilla",
    ],
    # The draw pass is optional (--draw): src/host/cuts.c.
    "sysdolphin/baselib/gobj.c": [
        "-DHSD_GObj_80390FC0=HSD_GObj_80390FC0_vanilla",
    ],
    # Headless: no particles (src/host/cuts.c).
    "sysdolphin/baselib/particle.c": [
        "-DpsInitDataBankLocate=psInitDataBankLocate_vanilla",
        "-DpsInitDataBankLoad=psInitDataBankLoad_vanilla",
        "-DpsInitDataBank=psInitDataBank_vanilla",
    ],
}

# Source patches: exact text replaced in a copy of a vanilla file before it
# is compiled here (the file in the repository is not touched). For the few
# places where the game's code depends on how the console lays data out in
# memory and no function boundary separates that from the rest. A patch
# whose text is no longer found stops the build.
PATCHES = {
    # A script's goto and subroutine targets are offsets in the file.
    "melee/lb/lbcommand.c": [
        ("info->x8.u = info->x8.u->Command_05.ptr;",
         "info->x8.u = host_script_target(info->x8.u);"),
        ("info->x8.u = info->x8.u->Command_07.ptr;",
         "info->x8.u = host_script_target(info->x8.u);"),
    ],
    # The nth animation joint of a stage model: the next n in the file.
    "melee/gr/granime.c": [
        ("aj = &aj[arg2];", "aj = host_dat_element(aj, arg2, 0x14);"),
        ("mj = &mj[arg2];", "mj = host_dat_element(mj, arg2, 0xC);"),
        ("sj = &sj[arg2];", "sj = host_dat_element(sj, arg2, 0xC);"),
    ],
}

AURORA_C = ["mtx.c", "mtx44.c", "mtxvec.c", "quat.c", "vec.c"]

# Stubs that must not simply return 0 in eax: these return a float.
FLOAT_STUBS = set()


def run(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], cwd=ROOT, **kw)


def includes():
    return [
        f"-I{AURORA}/include", f"-I{ROOT}/src",
        f"-I{ROOT}/libs/doldecomp/include",
        f"-I{OUT}/dat-readers/schema",
        f"-I{ROOT}/tools/dat-cli/native/include",
        f"-I{ROOT}/build/GALE01/include",
    ]


def cmake(flags):
    """libmelee.a and the readers, through upstream's preset."""
    for need in (AURORA / "include/dolphin/os.h", MELEE_DAT,
                 ROOT / "build/GALE01/dat/types.bin"):
        if not need.exists():
            sys.exit(f"missing {need}: see docs/ai/native-port.md")
    cflags = " ".join(flags)
    stamp = OUT / "host_flags.txt"
    if not (OUT / "build.ninja").exists() or not stamp.exists() or \
            stamp.read_text() != cflags:
        env = dict(os.environ, AURORA_SRC=str(AURORA))
        r = run(["cmake", "--preset", "native", "-DMELEE_DAT_READERS=ON",
                 f"-DMELEE_DAT={MELEE_DAT}", f"-DCMAKE_C_FLAGS={cflags}"],
                env=env, capture_output=True, text=True)
        if r.returncode:
            sys.exit(r.stdout + r.stderr)
        OUT.mkdir(parents=True, exist_ok=True)
        stamp.write_text(cflags)
    r = run(["ninja", "-C", OUT, "melee", "dat_melee", "dat_native"],
            capture_output=True, text=True)
    if r.returncode:
        sys.exit("\n".join((r.stdout + r.stderr).splitlines()[-40:]))


def compile_one(job):
    src, obj, extra = job
    obj.parent.mkdir(parents=True, exist_ok=True)
    dep = obj.with_suffix(".d")
    if obj.exists() and dep.exists():
        newest = obj.stat().st_mtime
        deps = dep.read_text().replace("\\\n", " ").split(":", 1)[-1].split()
        key = obj.with_suffix(".cmd")
        if key.exists() and key.read_text() == " ".join(extra) and all(
                Path(d).exists() and Path(d).stat().st_mtime <= newest
                for d in deps):
            return None
    cmd = ["gcc", *extra, "-MMD", "-MF", str(dep), "-c", str(src), "-o",
           str(obj)]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        return f"{src}:\n{r.stderr[-3000:]}"
    obj.with_suffix(".cmd").write_text(" ".join(extra))
    return None


def compile_all(jobs):
    with ThreadPoolExecutor(os.cpu_count()) as pool:
        errors = [e for e in pool.map(compile_one, jobs) if e]
    if errors:
        sys.exit("\n".join(errors))


def symbol_kinds():
    """name -> ('function' | 'object', size) from the matching build."""
    kinds = {}
    pat = re.compile(r"^(\S+) = \.\w+:0x[0-9A-Fa-f]+; // type:(\w+)"
                     r"(?: size:0x([0-9A-Fa-f]+))?")
    for line in (ROOT / "config/GALE01/symbols.txt").read_text().splitlines():
        m = pat.match(line)
        if m:
            kinds[m.group(1)] = (m.group(2), int(m.group(3) or "0", 16))
    return kinds


def link(objs, out, capture=False):
    libs = [OUT / "libmelee.a", OUT / "dat-readers/libdat_melee.a",
            OUT / "dat-readers/libdat_native.a"]
    cmd = ["gcc", "-m32", "-no-pie", "-rdynamic", "-o", out, *objs,
           "-Wl,--start-group", *libs, "-Wl,--end-group", "-lm"]
    return run(cmd, capture_output=True, text=True)


def write_stubs(names, path):
    kinds = symbol_kinds()
    lines = ['/* Generated by tools/native_build.py: SDK and debug functions',
             '   nothing implements natively. Each returns 0. */',
             'void host_stub_hit(int index);', '']
    funcs, objects = [], []
    for name in sorted(names):
        kind, size = kinds.get(name, ("function", 0))
        (objects if kind == "object" else funcs).append((name, size))
    for name, size in objects:
        lines.append(f"char {name}[{max(size, 4)}] "
                     "__attribute__((aligned(8)));")
    lines.append("")
    for i, (name, _) in enumerate(funcs):
        if name in FLOAT_STUBS:
            lines.append(f"float {name}(void) {{ host_stub_hit({i}); "
                         "return 0.0F; }")
        else:
            lines.append(f"int {name}(void) {{ host_stub_hit({i}); "
                         "return 0; }")
    lines.append("")
    lines.append("const char* const host_stub_names[] = {")
    lines += [f'    "{name}",' for name, _ in funcs]
    lines.append('    "",')
    lines.append("};")
    lines.append(f"unsigned host_stub_hits[{len(funcs) + 1}];")
    lines.append(f"const int host_stub_count = {len(funcs)};")
    text = "\n".join(lines) + "\n"
    if not path.exists() or path.read_text() != text:
        path.write_text(text)
    return funcs, objects


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--opt", default="0",
                    help="optimisation level (default 0)")
    ap.add_argument("--no-cmake", action="store_true",
                    help="reuse libmelee.a as it is")
    args = ap.parse_args()

    flags = BASE_FLAGS + [f"-O{args.opt}"]
    if not args.no_cmake:
        cmake(flags)

    common = flags + DEFINES + includes()
    jobs = []
    shim = ["-include", str(ROOT / "src/host/shim.h")]
    for rel, extra in VANILLA.items():
        jobs.append((ROOT / "src" / rel,
                     OBJ / "vanilla" / (rel.replace("/", "_") + ".o"),
                     common + shim + extra))
    for rel, patches in PATCHES.items():
        text = (ROOT / "src" / rel).read_text()
        for old, new in patches:
            if text.count(old) != 1:
                sys.exit(f"patch for {rel}: expected exactly one "
                         f"{old!r}, found {text.count(old)}")
            text = text.replace(old, new)
        copy = OBJ / "patched" / rel
        copy.parent.mkdir(parents=True, exist_ok=True)
        if not copy.exists() or copy.read_text() != text:
            copy.write_text(text)
        jobs.append((copy, OBJ / "patched" / (rel.replace("/", "_") + ".o"),
                     common + shim
                     + ["-iquote", str((ROOT / "src" / rel).parent)]
                     + VANILLA.get(rel, [])))
    for src in sorted((ROOT / "src/host").glob("*.c")):
        jobs.append((src, OBJ / (src.stem + ".o"), common))
    for name in AURORA_C:
        jobs.append((AURORA / "lib/dolphin/mtx" / name,
                     OBJ / "aurora" / (name + ".o"),
                     flags + DEFINES + [f"-I{AURORA}/include"]))
    # The SDK's own heap allocator, as decompiled: the same blocks at the
    # same addresses as on the console.
    jobs.append((ROOT / "libs/dolphin/src/dolphin/os/OSAlloc.c",
                 OBJ / "sdk" / "OSAlloc.o",
                 flags + ["-include", "stdint.h", "-include", "stddef.h",
                          f"-I{ROOT}/libs/dolphin/include", f"-I{ROOT}/src",
                          f"-I{ROOT}/libs/doldecomp/include"]))
    compile_all(jobs)
    objs = [obj for _, obj, _ in jobs]

    # What is still missing becomes a stub.
    stub_c = OBJ / "stubs_gen.c"
    stub_o = OBJ / "stubs_gen.o"
    write_stubs([], stub_c)
    compile_all([(stub_c, stub_o, flags)])
    r = link(objs + [stub_o], OUT / "melee_headless.trial")
    missing = sorted(set(re.findall(r"undefined reference to `([^']+)'",
                                    r.stderr)))
    other = [l for l in r.stderr.splitlines()
             if "undefined reference" not in l and "error" in l.lower()
             and "ld returned" not in l]
    if other:
        sys.exit("\n".join(other[:30]))
    funcs, objects = write_stubs(missing, stub_c)
    compile_all([(stub_c, stub_o, flags)])
    exe = OUT / "melee_headless"
    r = link(objs + [stub_o], exe)
    if r.returncode:
        sys.exit("\n".join(r.stderr.splitlines()[-30:]))
    (OUT / "melee_headless.trial").unlink(missing_ok=True)
    (OBJ / "stubs.json").write_text(json.dumps(
        {"functions": [n for n, _ in funcs],
         "objects": [n for n, _ in objects]}, indent=1))
    print(f"OK: {exe.relative_to(ROOT)} "
          f"({len(funcs)} stubbed functions, {len(objects)} stubbed objects)")


if __name__ == "__main__":
    main()
