#!/usr/bin/env python3
"""Check that MWCC places TM-CE's struct bitfields where gcc does.

Companion to tools/tmce_layout_check.py, which only compares non-bitfield
offsets. For every bitfield in every named struct reachable from events.h,
lab_common.h and savestate.h, this compiles `const struct T v = { .path = -1 }`
with clang --target=powerpc-none-eabi (gcc's ABI) and with MWCC GC/3.0a5.2,
and compares which bits of the object end up set. Needs clang and a prior
tools/overlay_build.py run. Paths only go through unnamed nested structs;
named nested structs are checked in their own right.
"""
import os, re, struct, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overlay_wrapper import compiler_prefix

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
T = 'build/overlay/tmce'
S = T + '/layout'
os.makedirs(S, exist_ok=True)
INC = ['src/tmce/include', 'src/tmce', f'{T}/src', f'{T}/MexTK/include', f'{T}/MexTK']
HDR = '#include "events.h"\n#include "lab_common.h"\n#include "savestate.h"\n'
CLANG = ['clang', '--target=powerpc-none-eabi', '-std=gnu99', '-nostdinc', '-w',
         '-fno-builtin'] + sum([['-I', i] for i in INC], [])
MWCC = ["-nowraplines", "-proc", "gekko", "-fp", "hardware", "-align", "powerpc",
        "-nosyspath", "-enum", "int", "-nodefaults", "-pragma", "cats off",
        "-Cpp_exceptions", "off", "-lang=c99", "-O0", "-maxerrors", "3",
        "-msgstyle", "gcc", "-warn", "off", "-sdata", "0", "-sdata2", "0",
        "-char", "unsigned"] + sum([['-i', i] for i in INC], [])

# 1. Every struct tag, so clang dumps its layout.
open(S + '/bf_tags.c', 'w').write(HDR)
r = subprocess.run(CLANG + ['-E', S + '/bf_tags.c'], capture_output=True, text=True)
tags = sorted(set(re.findall(r'\bstruct\s+([A-Za-z_]\w*)\s*\{', r.stdout)))
src = HDR + ''.join(f'int sz_{t} = sizeof(struct {t});\n' for t in tags)
open(S + '/bf_dump.c', 'w').write(src)
r = subprocess.run(CLANG + ['-Xclang', '-fdump-record-layouts', '-fsyntax-only',
                            S + '/bf_dump.c'], capture_output=True, text=True)

# 2. Bitfield designator paths per named struct.
fields = []  # (tag, path)
for block in r.stdout.split('*** Dumping AST Record Layout')[1:]:
    lines = block.strip('\n').splitlines()
    m = re.match(r'\s*0 \| struct (\w+)$', lines[0])
    if not m:
        continue
    tag, stack = m.group(1), []  # stack of (indent, name or None)
    for line in lines[1:]:
        lm = re.match(r'\s*([\d:\-]+) \| (\s*)(.*)$', line)
        if not lm:
            continue
        pos, ind, decl = lm.group(1), len(lm.group(2)), lm.group(3)
        while stack and stack[-1][0] >= ind:
            stack.pop()
        rec = re.match(r'(struct|union) (.*)$', decl)
        if rec and not decl.endswith('*'):
            body = rec.group(2)
            named_type = not body.startswith('(')
            nm = re.search(r'\)\s*(\w+)$', body) if body.startswith('(') else \
                re.match(r'\w+\s+(\w+)$', body)
            stack.append((ind, nm.group(1) if nm else None, named_type, rec.group(1)))
            continue
        if ':' in pos and not any(s[2] or s[3] == 'union' for s in stack):
            name = decl.split()[-1]
            path = [s[1] for s in stack if s[1]] + [name]
            fields.append((tag, '.'.join(path)))

def build(cmd, src_path, obj):
    rr = subprocess.run(cmd + ['-c', src_path, '-o', obj], capture_output=True, text=True)
    if rr.returncode:
        print(rr.stdout[-2000:], rr.stderr[-2000:]); sys.exit(1)
    syms = {}
    for line in subprocess.run(['build/binutils/powerpc-eabi-nm', '-S', obj],
                               capture_output=True, text=True).stdout.splitlines():
        p = line.split()
        if len(p) == 4 and p[3].startswith('bf_'):
            syms[p[3]] = (int(p[0], 16), int(p[1], 16))
    # read each symbol's bytes from whichever section holds it
    out = {}
    secs = {}
    for line in subprocess.run(['build/binutils/powerpc-eabi-objdump', '-t', obj],
                               capture_output=True, text=True).stdout.splitlines():
        p = line.split()
        if p and p[-1].startswith('bf_') and len(p) >= 5:
            secs[p[-1]] = p[-3]
    cache = {}
    for k, (addr, n) in syms.items():
        sec = secs[k]
        if sec not in cache:
            subprocess.run(['build/binutils/powerpc-eabi-objcopy', '-O', 'binary',
                            f'--only-section={sec}', obj, obj + '.bin'], check=True)
            cache[sec] = open(obj + '.bin', 'rb').read()
        out[k] = cache[sec][addr:addr + n]
    return out

src = [HDR]
for k, (tag, path) in enumerate(fields):
    src.append(f'const struct {tag} bf_{k} = {{ .{path} = -1 }};')
open(S + '/bf.c', 'w').write('\n'.join(src) + '\n')
a = build(CLANG + ['-O0', '-fno-common'], S + '/bf.c', S + '/bf_clang.o')
b = build(compiler_prefix() + ['build/compilers/GC/3.0a5.2/mwcceppc.exe'] + MWCC,
          S + '/bf.c', S + '/bf_mw.o')

def bits(blob):
    return [i * 8 + (7 - j) for i, byte in enumerate(blob) for j in range(8) if byte >> j & 1]

bad = 0
for k, (tag, path) in enumerate(fields):
    x, y = a.get(f'bf_{k}'), b.get(f'bf_{k}')
    if x is None or y is None:
        print(f'  {tag}.{path}: missing object'); bad += 1; continue
    bx, by = bits(x), bits(y)
    if bx != by or len(x) != len(y):
        bad += 1
        fmt = lambda v: f'byte 0x{v[0] // 8:X} bits {[i % 8 for i in v]}' if v else 'none'
        print(f'  {tag}.{path}: gcc-ABI {fmt(bx)}, MWCC {fmt(by)}')
print(f'{len(fields)} bitfields in {len(set(t for t, _ in fields))} structs compared, {bad} differ')
