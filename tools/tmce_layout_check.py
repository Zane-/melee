#!/usr/bin/env python3
"""Check that MWCC lays out TM-CE's structs like gcc does.

TM-CE is normally built with gcc (devkitPPC); the native build compiles it
with MWCC GC/3.0a5.2. This compiles sizeof and offsetof of every non-bitfield
field of every struct reachable from events.h, lab_common.h and savestate.h
with both clang --target=powerpc-none-eabi (gcc's ABI) and MWCC, and lists
the differences. Needs clang and a prior tools/overlay_build.py run.

Known result (2026-11-11): only struct FtScript differs (packed; used only
through a pointer).
"""
import json, os, re, struct, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overlay_wrapper import compiler_prefix
S = "build/overlay/tmce/layout"
os.makedirs(S, exist_ok=True)
T = 'build/overlay/tmce'
inc = ['src/tmce/include', 'src/tmce', f'{T}/src', f'{T}/MexTK/include', f'{T}/MexTK']
open(S + '/all.c', 'w').write('#include "events.h"\n#include "lab_common.h"\n#include "savestate.h"\n')
cl = ['clang', '--target=powerpc-none-eabi', '-std=gnu99', '-nostdinc', '-w', '-fno-builtin'] + \
     sum([['-I', i] for i in inc], [])
r = subprocess.run(cl + ['-Xclang', '-ast-dump=json', '-fsyntax-only', S + '/all.c'],
                   capture_output=True, text=True)
if r.returncode: print(r.stderr[:3000]); sys.exit(1)
ast = json.loads(r.stdout)
typedef_of = {}  # record id -> typedef name
for d in ast['inner']:
    if d.get('kind') == 'TypedefDecl':
        for c in d.get('inner', []):
            t = c.get('ownedTagDecl') or (c.get('inner', [{}])[0].get('decl') if c.get('kind') == 'ElaboratedType' else None)
            if c.get('kind') == 'ElaboratedType' and 'ownedTagDecl' in c:
                typedef_of[c['ownedTagDecl']['id']] = d['name']
recs = {}
for d in ast['inner']:
    if d.get('kind') != 'RecordDecl' or not d.get('completeDefinition'): continue
    f = d.get('loc', {}).get('file') or ''
    name = ('struct ' + d['name']) if d.get('name') else typedef_of.get(d['id'])
    if not name or d.get('tagUsed') != 'struct': continue
    fields = [c['name'] for c in d.get('inner', []) if c.get('kind') == 'FieldDecl'
              and c.get('name') and not c.get('isBitfield')]
    recs[name] = fields
exprs = []
for name, fields in sorted(recs.items()):
    exprs.append((name, '<size>', f'sizeof({name})'))
    for fl in fields:
        exprs.append((name, fl, f'__builtin_offsetof({name}, {fl})'))
def build(cc_cmd, out):
    src = ['#include "events.h"', '#include "lab_common.h"', '#include "savestate.h"',
           '#include <stddef.h>', 'const unsigned int tmce_offs[] = {']
    src += [f'    (unsigned int)({e}),' for _, _, e in exprs] + ['0};']
    open(S + '/lay.c', 'w').write('\n'.join(src).replace('__builtin_offsetof', 'offsetof') + '\n')
    r = subprocess.run(cc_cmd + [S + '/lay.c' if 'clang' in cc_cmd[0] else os.path.relpath(S + '/lay.c'),
                       '-o', out if 'clang' in cc_cmd[0] else os.path.relpath(out)], capture_output=True, text=True)
    if r.returncode: print(r.stdout[:2000], r.stderr[:2000]); sys.exit(1)
    subprocess.run(['build/binutils/powerpc-eabi-objcopy', '-O', 'binary', '--only-section=.rodata', out, out + '.bin'], check=True)
    b = open(out + '.bin', 'rb').read()
    return struct.unpack(f'>{len(exprs)}I', b[:4 * len(exprs)])
mw = ["-nowraplines","-proc","gekko","-fp","hardware","-align","powerpc","-nosyspath","-enum","int",
      "-nodefaults","-pragma","cats off","-Cpp_exceptions","off","-lang=c99","-O0","-maxerrors","3",
      "-msgstyle","gcc","-warn","off"] + sum([['-i', i] for i in inc], [])
a = build(cl + ['-c', '-O0', '-fno-common'], S + '/lay_clang.o')
b = build(compiler_prefix() + ['build/compilers/GC/3.0a5.2/mwcceppc.exe'] + mw + ['-c'], S + '/lay_mw.o')
bad = [(n, f, x, y) for (n, f, _), x, y in zip(exprs, a, b) if x != y]
print(f'{len(recs)} structs, {len(exprs)} values compared, {len(bad)} differ')
seen = set()
for n, f, x, y in bad:
    print(f'  {n}.{f}: gcc-ABI 0x{x:X}, MWCC 0x{y:X}')
