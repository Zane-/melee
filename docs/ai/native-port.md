# Native build for Linux

The game compiled for 32-bit x86 Linux and run as an ordinary process, with no emulator
and no window. Asked for by the owner on 2026-11-12, after the Melee Actor research
showed that a full-size instructable model cannot run on a GameCube (`melee-actor.md`).

Status, 2026-11-12: **it boots, starts a match without menus, and plays the same game as
the console's code, frame for frame, in most of what was tested.** It is the vanilla game
only: no overlay, no TM-CE, no courses. Nothing is drawn or heard.

```sh
. .venv/bin/activate
python tools/native_build.py                    # build/native/melee_headless (about 10 s)
build/native/melee_headless --match 2,9,32 --frames 600 --trace 60   # Fox, Marth, FD
python tools/melee_native/compare.py --tolerance 1e-4 --random 3     # against the simulator
```

## What it is not, and what it does not replace

- **Not the overlay build.** Slippi netplay is against people running Dolphin, and only an
  address-preserving DOL can join them (`slippi-tandem.md`). The training build stays an
  overlay on the retail image. The native build is a second target for the same source.
- **Not yet a place to run drills.** Hooks are post-link patches to the DOL; none of them
  exist here. TM-CE's own sources (MexTK headers) have never been compiled for it.
- **Not exact to the last bit.** See "How close it is".

## Pieces

| Piece | Where | What it does |
|-|-|-|
| The game | `build/native/libmelee.a` | Upstream's `native` CMake preset: all of `src/melee` and `src/sysdolphin` with `TARGET_PC`, against Aurora's SDK headers |
| Archive readers | `tools/dat-cli/native` (upstream), generated into `build/native/dat-readers` | Turn a big-endian `.dat` archive into host objects of the game's own types, from a schema taken from a PowerPC DWARF build |
| Host layer | `src/host/` | The console underneath the game, at the level of SDK functions: `os.c` (reports, emulated time, interrupts as queued completions, alarms, the arena at the console's addresses), `dvd.c` (the disc is `build/disc/files`), `hw.c` (audio RAM, pads, video timing, the few graphics answers the game uses), `archive.c` (the loader on the readers), `particles.c`, `match.c`, `control.c`, `debug.c`, `cuts.c` |
| Build | `tools/native_build.py` | Runs the preset, compiles the vanilla files upstream leaves out, the host layer, Aurora's C matrix functions and the SDK's own heap allocator, generates a stub for every SDK function still missing (222), links |
| Driver | `tools/melee_native/native.py` | `Native`: `step`, `pad`, `match`, `fighter`, `state`, over the line protocol of `src/host/control.c` |
| Comparison | `tools/melee_native/compare.py`, `survey.py`, `rngdiff.py` | The same match and inputs in the Python simulator and natively, compared every frame; the same over 19 matchups; which code drew random numbers differently |
| Sanitizer | `tools/native_build.py --asan`, `tools/melee_native/asan.py` | The game under AddressSanitizer, and its reports reduced to distinct places in the source |
| Crash traces | `tools/native_run.sh` | Runs the game and turns a crash backtrace into function names and lines |

One-time setup (the readers' tool and type table come from the flake):

```sh
# Nix: Arch package `nix`, daemon running, flakes enabled in ~/.config/nix/nix.conf
nix build .#melee-dwarf -o build/nix/dwarf        # PowerPC build with DWARF (8 s)
nix build .#melee-dat   -o build/nix/melee-dat    # the archive tool
build/nix/melee-dat/bin/melee-dat types export -o build/GALE01/dat/types.bin \
    --dwarf build/nix/dwarf/melee.elf
# Aurora's headers: github:r-burns/aurora at the revision in flake.lock, in build/deps/aurora
```

Repeat the first and third after changing a `DAT_*` annotation or an archive type.
Do not enter the flake's dev shells (`nix develop`) in this checkout: their shell hook
runs `./configure.py` and installs pre-commit hooks.

`melee_headless` options: `--match P1,P2,STAGE` (character kinds and the stage id of the
match rules), `--frames N`, `--trace N`, `--control` (commands on stdin, see
`control.c`), `--draw` (run the draw pass into the no-op graphics), `-v` (the game's own
reports), `--stubs` (which stubbed SDK functions were called), `--disc DIR`.
`native_build.py --opt 1` builds optimised (50 s). `--opt 2` crashed while a match loaded
when last tried, before one cause of such crashes was fixed; not retried.

## How a match starts

The game has a developers' mode that starts a match with no menus, `GM_DEBUG_VS`
(`gmvsmode.c`). `src/host/match.c` gives that mode a state table of its own at run time
(the mode table is data) and enters it through the game's mode override, the function the
game calls between scenes (its memory card prompts use it). `compare.py` does the same to
the retail code in the simulator, so both sides run the same setup.

One frame is one call of the scene loop's wait for a pad sample (`lb_80019894`), as in the
Python simulator; the host's version of that function is the frame boundary.

## How close it is

Checked 2026-11-12 with `compare.py`: the retail PowerPC code in the Python simulator
(`simulator.md`, itself checked against Dolphin) against the native build, same match,
same seed, same inputs, every frame: the random seed; for both fighters, state,
animation frame, position, speed, facing, airborne, damage, hitlag, hitstun, shield; and
every item's kind, state, position and speed.

- **`tools/melee_native/survey.py`**: 19 matchups (26 of the characters, the six
  tournament stages), random inputs, 600 frames. With two runs each, **17 matchups are
  identical in both runs** in every state, frame counter, hitlag and hitstun value, item
  and random number. The other two are in the table below.
- **Positions, speeds, damage and shield agree to rounding, not to the bit**
  (`--tolerance 1e-4`, the survey's default). Without the tolerance the first difference
  comes after 130 to 200 frames, in the last bit of a speed.
- **`tools/melee_native/asan.py`** (the AddressSanitizer build) reports no bad access in
  an idle match, and none in gameplay code over 15 of the survey's runs.
- Speed: about 9,500 frames a second in active play unoptimised, 15,600 with `--opt 1`
  (the Python simulator: 50 to 160), driven from Python.

Known differences, none investigated to the end:

| Where | What |
|-|-|
| Last-bit floats | The floor normal comes out 0.99999994 instead of 1: `PSVECNormalize` is the console's paired-single routine there, numpy in the simulator and Aurora's C here. Three implementations; only Dolphin or hardware is the reference. One exact comparison in the game (`scale != 1.0F`) showed how a last bit can flip a branch. Also: the C library's `sinf`, `sqrtf`... are glibc's, not the console's (`src/MSL` has the console's in C), `__frsqrte` is an exact reciprocal square root (as in the simulator, unlike hardware), and multiply-add fusing follows gcc's choices, which are not always the console compiler's |
| Sheik's chain | The chain item is in a different state from frame 212 of one run (`falco`/`sheik`, run 1) |
| Sheik, Zelda | Transform: the fighter is in a different state while the other loads (how long a disc read takes is the host's choice) |
| Ice Climbers | The partner diverges in one run (run 2, frame 183: a solo side special where the console has the pair's). Her inputs come from the CPU code, which nothing here compares |
| Big Blue, Venom | Three flag unions there are read through pointers and were left as they were |
| CPU players | Not compared: both players are driven by pads in every run |
| Menus, other modes | Only the memory card prompt and the debug VS match have run |
| `--draw` | Asserts in the first frame (a position out of range) |
| Audio | Sound files are loaded with their headers in host order; nothing plays, nothing was checked |

## What made it work: six kinds of dependence on the console

The source matches the retail binary on the console's compiler. On another machine it
depends on things that compiler and machine provided. Each kind met so far, and the tool
for it:

1. **Data from archives.** Upstream's loader converted only symbols looked up with a type
   (`HSD_ArchiveGetPublicAs`, 70 places); the other 190 load sites got raw big-endian
   bytes. `src/host/archive.c` gives every lookup the type the schema records for that
   symbol name. Where the types are wrong or missing, fix the annotation in the header
   (`DAT_COUNT`, `DAT_EXTENT`, `DAT_BIND`, a struct instead of `UNK_T`) and regenerate:
   done for a fighter's costume texture indices, the revival platform, the table of bones
   a character leaves out, the item throw table, the shake tables and the refraction
   parameters. A stage file's other language version (`GrPs.usd`) uses the schema entry
   of the `.dat`. An archive ends when its buffer is parsed again, as on the console,
   where it is that buffer.
2. **Bit and byte order in code.** A flags word written as a number and read as
   bit-fields, or copied from file data as an integer. `PPC_LAYOUT`
   (`src/Runtime/platform.h`) marks a struct or union to keep the console's layout (gcc's
   `scalar_storage_order`; nothing for the console's compiler, so the matching build is
   unchanged). 23 unions carry it. The address of a scalar member of such a type cannot be
   taken, which is why three were left out. When the readers load such a type they keep
   the file's bytes. Where one word has an integer view and a bit-field view in two
   structs, the bit-field view gets a little-endian layout under `TARGET_PC`
   (`ftData_80085FD4_ret`).
3. **Data that is code.** Command scripts (fighter actions, items, colour animations)
   stay in disc order and are read through bit-field structs: `PPC_LAYOUT_BEGIN`/`END`
   around those types. Their goto targets are file offsets, resolved by
   `host_script_target`. Particle banks are converted in place by `particles.c` for the
   game's own locate code; their byte code is read in disc order. Sound files are words,
   swapped at the disc boundary (`dvd.c`).
4. **The file's memory layout.** "The nth animation joint after this one" for stage
   models: `host_dat_element` finds the neighbour through the archive.
5. **The DOL's memory layout.** Globals addressed through their neighbours (a table as
   "what follows this other table", a struct laid over three globals): in fighter data,
   particles, the camera, trophies, the sound bank table. Each is named instead. The
   same goes for the stack: square roots stored to a slot outside the function's
   variables, a rotation read as four floats into a variable of three. The
   AddressSanitizer build finds the ones that run.
6. **Floating point.** SSE instead of x87, multiply-add fusing when optimising; see the
   differences above.

**Vanilla functions are not edited for any of this** (the rule in `CLAUDE.md`). Type
markers and annotations go in headers and expand to nothing in the matching build. Where
an expression inside a function has to differ, `tools/native_build.py` applies a source
patch to a copy of the file at build time (`PATCHES`: exact text, checked to occur the
expected number of times) or builds the file with one function renamed so `src/host/`
can supply it (`VANILLA`: the native counterpart of the overlay's `function` hook).

## Finding the next difference

```sh
python tools/melee_native/compare.py --p1 peach --p2 fox --random 2 --tolerance 1e-4 --show 3
python tools/melee_native/rngdiff.py 252        # who drew random numbers in frame 252
tools/native_run.sh --match 12,2,32 --frames 400   # a crash, with names
```

```sh
python tools/native_build.py --asan             # build/native-asan/melee_headless
python tools/melee_native/asan.py --match 2,9,32 --frames 600   # distinct bad accesses
python tools/melee_native/survey.py --runs 2    # the regression test (about 4 minutes)
```

The sanitizer run comes first: a read past the end of converted archive data is an array
whose count the readers were not told (`heap-buffer-overflow`), and a read or write past
a global or a stack variable is code that depends on the console's memory layout. Both
show up there with the source line, long before they change a fighter's state.

A difference in the random sequence usually means code that ran on one side only:
`rngdiff.py` names it. A crash or assert in the native build usually means data that was
not converted (kind 1 or 3) or a global addressed through another (kind 5): `gdb` works
on `melee_headless` (`break file.c:line`, `watch -l`), with `--control < file` for input.

## What upstream has

`doldecomp/melee` is working toward a native build: the `native` preset ("32-bit host
build against aurora"; its own comment calls it a smoke test), the generated readers
(October 2026), and Aurora (`github:r-burns/aurora`), which reimplements GX, VI and PAD
for PC. At the fork point (2026-11-04) it compiled but had never been linked into a
program; everything under "What made it work" was found here. Nothing here has been
offered upstream; its rules (no AI-chosen names, no AI-written PR text) apply to anything
that would be.

## Next steps

1. Work through the known differences; compare CPU players and more of the game's
   state (the Ice Climbers' partner shows that two pad-driven fighters are not all of
   it).
2. Exact floating point: the console's paired-single routines and C library in C, and a
   full-precision trace from Dolphin as the reference.
3. Hooks for the native target, so TM-CE, the course engine and the drill specs
   (`tests/tmtest/course/`, 230 with numbers from the PowerPC build) run on it.
4. Graphics, audio and input (Aurora, if it builds for 32-bit Linux) for a playable
   build.
