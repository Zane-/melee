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

Everything upstream's native preset is meant to produce builds here.

```sh
# once: Nix (Arch package `nix`, daemon running, flakes enabled in ~/.config/nix/nix.conf)
nix build .#melee-dwarf -o build/nix/dwarf        # PowerPC build with DWARF: melee.elf
nix build .#melee-dat   -o build/nix/melee-dat    # the archive tool
build/nix/melee-dat/bin/melee-dat types export -o build/GALE01/dat/types.bin \
    --dwarf build/nix/dwarf/melee.elf

export AURORA_SRC=<aurora checkout at the revision in flake.nix>
cmake --preset native -DMELEE_DAT_READERS=ON \
    -DMELEE_DAT=$PWD/build/nix/melee-dat/bin/melee-dat
ninja -C build/native                              # libmelee.a and the readers

# the readers alone, with their tests on the game's files
cmake -S tools/dat-cli/native -B build/native-readers -G Ninja \
    -DMELEE_DAT=$PWD/build/nix/melee-dat/bin/melee-dat \
    -DCMAKE_TOOLCHAIN_FILE=$PWD/tools/dat-cli/native/toolchains/i686.cmake
ninja -C build/native-readers && ctest --test-dir build/native-readers
```

Do not enter the flake's dev shells (`nix develop`) in this checkout: their shell hook
runs `./configure.py` and installs pre-commit hooks, which would replace this fork's build
configuration. The packages above are enough.

Results:

- **All 1,020 source files compile for 32-bit Linux** (gcc `-m32`), in about 2 seconds of
  wall time, into `build/native/libmelee.a`. At first 1,015 did: the five failures were
  all ours (`src/melee/tm/`), for a missing include, an include path, a prototype
  declared before its struct, and a draw callback's parameter type. Fixed; the matching
  build, the overlay and the specs are unaffected.
- **The archive readers build and pass their tests**: schema for 2,374 types, 18,438
  roots in 7,050 archives, "0 members without a native place"; 6 of 6 tests, including the
  end-to-end walk of `orig/GALE01/files` on a little-endian host.
- **The PowerPC DWARF build succeeds** with our mod files in it (after the same fixes).
- The game objects define about 26,000 symbols and need **409 from outside** (counted
  before the readers were linked in):

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

- **Nothing was linked into a program or run.** There are libraries, no executable, no
  main loop.
- **Whether Aurora itself builds for 32-bit Linux** and how complete its GX is for
  this game. Only its headers were used.
- **Exactness.** x86 floating point against the GameCube's paired singles: the drill
  specs (`tests/tmtest/course/`, 230 of them, each with numbers from the PowerPC build)
  are the test for it once something runs.
- **TM-CE's own sources** (MexTK headers) were not in this build; only our native
  `src/melee/tm/` files were.

## Why it matters, and what it does not replace

- A native process has no 24 MB and no 486 MHz: a Phillip-sized policy, or an
  instructable one, can run in the game's own process.
- A native headless core would replace the PowerPC interpreter under the simulator
  (about 100 frames a second) with compiled code, which is what training needs.
- It does **not** replace the overlay build: Slippi netplay is against people running
  Dolphin, and only an address-preserving DOL can join them (`slippi-tandem.md`).

## Next steps

1. (done) The toolchain: DWARF build, `melee-dat`, generated readers and their tests,
   `libmelee.a`.
2. A headless link: `libmelee.a` plus C versions of the simulator's SDK replacements and
   the 13 excluded files' functions, booting to a match with no window. Then run the
   drill specs on it.
3. TM-CE and the course engine on the native target.
4. Only then graphics (Aurora), audio and input for a playable build.
