# Native build for Linux: probe

Asked by the owner 2026-11-12, after the Melee Actor research showed that a full-size
instructable model cannot run on a GameCube (`melee-actor.md`). A native build removes
that ceiling. This file records what a first probe found. Nothing here is built into the
project's normal workflow yet.

## What upstream already has

`doldecomp/melee`, which this repository is forked from, is working toward it:

- `CMakePresets.json` has a `native` preset: "32-bit host build against aurora". 32-bit
  because the game's code assumes 4-byte pointers (`cmake/i686-gcc.cmake`). Aurora
  (`github:r-burns/aurora`, pinned in `flake.nix`) reimplements the GameCube's GX, VI and
  PAD libraries for PC.
- `cmake/MeleeConfig.cmake` builds all of `src/melee` and `src/sysdolphin` with
  `TARGET_PC`, leaving out 13 files (memory card, THP video, debug console, fog table,
  fonts read from the DOL, `pobj.c`, `video.c`). Its own comment calls it a smoke test.
- `tools/dat-cli/native`: generated readers that load the game's big-endian `.dat`
  archives into host types, whatever the host's byte order and pointer size (upstream
  commits of October 2026). They are generated from the types of a PowerPC DWARF build
  (`ppc-dwarf` preset, clang, newlib headers).

## Probe (2026-11-12)

Without Nix, on this machine (gcc with `-m32`, cmake, Aurora's source fetched at the
pinned revision for its headers):

```sh
export AURORA_SRC=<aurora checkout>
cmake --preset native
ninja -C build/native -k 0
```

- **1,015 of 1,020 source files compile** for 32-bit Linux, in about 2 seconds of wall
  time. The five that fail are all ours (`src/melee/tm/`: `tm_css.c`, `tm_css_screen.c`,
  `ess.c`, `tmtest.c`, `tm_fighter.c`), for include paths and prototypes that only the
  GameCube build exercises. Every original game file that upstream includes compiles.
- The objects define 26,163 symbols and need **409 from outside**:

  | Group | Count | Who would provide it |
  |-|-|-|
  | GX | 93 | Aurora (or stubs, headless) |
  | AX, AI (audio) | 39 | to write, or stub |
  | OS | 27 | to write: arena, alarms, time, interrupts as no-ops |
  | MTX / VEC | 21 | Aurora or a few lines each |
  | CARD | 13 | stub: no card |
  | DVD, AR, PAD, VI | 20 | file reads from the extracted disc; pad from the host |
  | HSD and game functions from the 13 excluded files | about 80 | port those files |
  | libc math and the rest | about 110 | libm; TM-CE glue our files expect |

  That list is nearly the list of SDK objects the Python simulator already replaces
  (`tools/melee_sim/hle.py`): the same boundary, drawn by someone else.

## Not established

- **Nothing was linked or run.** The build makes object files; there is no executable.
- **Archives.** The readers need the DWARF build and the `melee-dat` tool, a chain the Nix
  dev shell sets up (clang 22, newlib headers). Not attempted without Nix.
- **Whether Aurora itself builds for 32-bit Linux** and how complete its GX is for
  this game.
- **Exactness.** x86 floating point against the GameCube's paired singles: the drill
  specs (`tests/tmtest/course/`, 230 of them, each with numbers from the PowerPC build)
  are the test for it once something runs.
- **Our mod code on the native target.** Five native files fail to compile; TM-CE's own
  sources (MexTK headers) were not in this build at all.

## Why it matters, and what it does not replace

- A native process has no 24 MB and no 486 MHz: a Phillip-sized policy, or an
  instructable one, can run in the game's own process.
- A native headless core would replace the PowerPC interpreter under the simulator
  (about 100 frames a second) with compiled code, which is what training needs.
- It does **not** replace the overlay build: Slippi netplay is against people running
  Dolphin, and only an address-preserving DOL can join them (`slippi-tandem.md`).

## Next steps

1. Nix dev shell (`nix develop`), then the `ppc-dwarf` build, `melee-dat`, the generated
   readers and their tests, as upstream intends.
2. A headless link: the 1,015 objects plus C versions of the simulator's SDK
   replacements, booting to a match with no window. Then run the drill specs on it.
3. Our five files, then TM-CE and the course engine, on the native target.
4. Only then graphics (Aurora), audio and input for a playable build.
