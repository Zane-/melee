# Melee decomp — agent guide

This repo is the matching decompilation of Super Smash Bros. Melee (NTSC 1.02, `GALE01`).
This fork's goal is a **custom training build** organised as **character courses** (owner
decision 2026-11-12): pick your character, then train it through Tech, Neutral, Punish and
Defense drills that teach in game (guide, demonstration, timing feedback, statistics). The
courses are built on Training Mode (TM-CE, source in `../TrainingMode`) ported to native C;
its Lab and generic events stay as free practice. Later: an in-game AI coach driven by
Claude, and tandem training over Slippi direct connect. Read `docs/ai/README.md` for the doc
index and `docs/ai/training-courses.md` for the course architecture and its status.

**Where new work starts (owner decision 2026-11-13): the native Linux build**, "because we
want to build in direct AI integration and the actor system to build AI-driven training".
The overlay build below is what can be played today and stays correct, but scripts,
policies and models that drive the game are built against the native build first:
`docs/ai/native-ai.md`. Its window variant draws, runs at the console's speed and reads
a controller or the keyboard (`python tools/melee_native/play.py`), but that has only
been checked on a virtual display, it has no sound, and no drills run on it yet.

## Facts that shape every task

- **Everything is decompiled.** All 1,117 objects in `configure.py` are `Matching`. There is no
  hand-written game asm left. Any vanilla behaviour can be read and changed in C.
- **About half the functions are still address-named** (`gm_801A4510`, `fn_8018A000`,
  `HSD_SisLib_803A70A0`). A name ending in 8 hex digits means "matched but not understood yet".
  The address in the name is the vanilla address; use it to cross-reference other Melee docs.
- **The DOL is shiftable, but this project does not shift it.** Slippi compatibility requires
  the vanilla layout (see Architecture below).
- **The matching build must always pass.** It reproduces the retail DOL byte-for-byte
  (`-DMUST_MATCH` is defined) and is the base the overlay is laid over.

## Architecture: address-preserving overlay (decided 2026-11-11)

Stock Slippi Dolphin injects its netplay code at vanilla addresses and savestates hardcoded
memory ranges. So the training build **must not move, grow or shrink any vanilla code or
data**. Mod code is an overlay above the vanilla image; vanilla calls into it through
post-link patches. Full design and its unproven parts: `docs/ai/overlay-build.md`.

What this means for every change:

- Never edit a vanilla function to add a call, a branch or a field access. Not even behind
  `#ifdef`. Hooks go in the hook table and are applied as patches.
- Writable statics are allowed (owner decision 2026-11-11, so TM-CE's C can be used as is),
  but they are **not** saved by Slippi's rollback. Code that runs during netplay (tandem
  drills) keeps its mutable state on the heap under the `tm_state` root.
- Never replace or patch at an address Slippi patches (`config/GALE01/slippi_injections.txt`).
- `tools/overlay_check.py` must pass on any DOL meant to run.
- `--non-matching` (freely shifted) builds are for local experiments only.
- **No assembly (project goal, set by the owner 2026-11-11).** Mod code is C. Port TM-CE's
  assembly injections by understanding what they do and writing C against the decomp, usually
  as an edited copy of the vanilla function behind a `function` or `call` hook
  (`src/melee/tm/tm_event_start.c` is an example). Do not add `.s` files or inline asm. The `inject` hook kind (a generated register-saving trampoline) is a last resort; if
  you think you need it, look for a `call`, `function` or `pointer` hook first and say why
  none works.

## TM-CE port (decided 2026-11-11)

TM-CE's own C (`../TrainingMode/src`, ~26k lines) is compiled nearly unmodified against its
MexTK headers and linked into the overlay; only its assembly (~300 injections) is rewritten as
native C hooks. Small patches to TM-CE live in `src/tmce/patches/`; m-ex runtime replacements
in `src/tmce/`. Full design, porting recipe and status: `docs/ai/tmce-native.md`. The older
plan to reimplement TM-CE against the decomp (`training-mode-port.md`) is superseded; its
MexTK ↔ decomp notes are still useful.

`python tools/overlay_build.py` compiles native mod code and TM-CE, links the overlay, applies
the hook tables (`config/GALE01/tm_hooks.txt` + `config/GALE01/tm_hooks/*.txt`) and runs the
layout check, on top of a matching build. `python tools/tmce_disc.py` installs the DOL and
TM-CE's art into `build/disc` for Dolphin. An overlay DOL has booted in Dolphin (2026-11-11,
before the TM-CE switch); see `overlay-build.md` for what is proven.

## Build

```sh
. .venv/bin/activate                      # ninja lives here
python configure.py                       # matching (Linux x86_64: no wrapper needed)
python configure.py --wrapper tools/wibo_macos_wrapper.py            # matching, macOS
python configure.py --non-matching --map  # shifted dev build, not for netplay
ninja
```

- Needs `orig/GALE01/sys/main.dol` (git-ignored; extract with `build/tools/dtk disc extract`).
  macOS also needs Rosetta 2 and `build/tools/wibo-macos`; the wrapper script replaces
  `sjiswrap.exe`, which does not load under wibo there.
- Verified 2026-11-11: the matching build reproduces the retail SHA-1 on macOS (about 2.5 min
  from clean) and on Linux (about 16 s). Fresh-machine setup: build-melee skill.
- Matching success = `build/GALE01/ok` and the final line reports the SHA-1 match.
- Output: `build/GALE01/main.dol`, `main.elf`, and `main.elf.MAP` with `--map`.
- Details and troubleshooting: `.claude/skills/build-melee/SKILL.md`.

## Rules for changing code

1. **Mod code lives in its own files** under `src/melee/tm/` (training mode) and `src/melee/ai/`
   (coach link). See `.claude/skills/add-native-code/SKILL.md`.
2. **Vanilla source files keep producing identical output.** The matching build is the proof:
   after touching any vanilla file (renames, comments, types), rebuild in matching mode and
   confirm the SHA.
3. **Find things by symbol, not by guess.** `config/GALE01/symbols.txt` is the source of truth
   for address ↔ name. Header address comments can be stale. Use
   `.claude/skills/find-symbol/SKILL.md`. In mod C code call vanilla by symbol; never write a
   raw address literal.
4. **Style** (enforced upstream, see `.github/CONTRIBUTING.md`): clang-format (4 spaces, 79 cols),
   `!= NULL` checks, float literals `1.0F`, struct offset comments, enums and typedefs in
   `forward.h`, struct bodies in `types.h`, TU headers declare only that TU's symbols.
5. **Upstream PR hygiene:** renames and cleanup of vanilla code may go upstream to
   `doldecomp/melee`; mod code never does. Upstream forbids AI-chosen names for struct fields and
   global identifiers and AI-written PR text. Keep rename work on separate branches from mod work.

## Where things are

| Need | Look at |
|-|-|
| Module-by-module map, naming conventions | `docs/ai/codebase-map.md` |
| Boot → scene → frame loop, GObj, fighter, text, memory | `docs/ai/runtime.md` |
| Overlay build design, hook kinds, experiments | `docs/ai/overlay-build.md` |
| Shifted dev builds (experiments only) | `docs/ai/modding.md` |
| TM-CE native port: design, porting recipe, status | `docs/ai/tmce-native.md` |
| MexTK ↔ decomp mapping (older reimplementation plan) | `docs/ai/training-mode-port.md` |
| AI coach design | `docs/ai/ai-coach.md` |
| Slippi direct-connect tandem training research | `docs/ai/slippi-tandem.md` |
| Our own peer-to-peer rollback netcode: feasibility study | `docs/ai/netplay-p2p.md` |
| Control profiles and input delay (the pad sample hook) | `src/melee/tm/controls/`, `tests/sim/controls.py` |
| UCF 0.84 in C, and its comparison against Slippi's own code | `src/melee/tm/ucf/`, `docs/ai/ucf.md`, `tests/sim/ucf.py` |
| The main menu (panels, pages) | `src/melee/tm/menu/`, `tests/sim/menu.py`; "Main menu" in `docs/ai/training-courses.md` |
| A picture of a screen from a scripted headless run | `python tools/tmtest.py tests/tmtest/menu/boot.json --shots DIR`; `docs/ai/testing.md` |
| MexTK name → decomp name | `python tools/mex_symbols.py <name-or-0xaddr>` |
| Build the training overlay DOL | `python tools/overlay_build.py` → `build/overlay/main.dol` |
| Put it and TM-CE's art on the extracted disc | `python tools/tmce_disc.py` → boot `build/disc/sys/main.dol` |
| Test an event: scripted, deterministic, headless, JSON results | `python tools/tmtest.py tests/tmtest/...`; `docs/ai/testing.md` |
| Does a DOL keep the vanilla layout? | `python tools/overlay_check.py <dol> [--patches list]` |
| Does a TM-CE hook clash with Slippi? | `python tools/tm_slippi_collisions.py [--function NAME]` |
| Game knowledge: characters, techniques, frame data, community guides | `data/README.md`, skill `melee-knowledge` |
| Frame data lookups and knockback / on-shield calculators | `python tools/melee_data/query.py` (`--help`) |
| Course architecture: hub, drill engine, milestones | `docs/ai/training-courses.md` |
| Course curricula and drill specs | `data/courses/` (`README.md` for the format) |
| Plan a course / specify a drill / implement a drill | skills `plan-character-course`, `design-training-scenario`, `add-course-drill` |
| A scenario on the native build: both sides scripted or a policy, a verdict over many runs | `python tools/melee_actor/run.py FILE --runs N --jitter X`; skill `actor-scenario` |
| Claude writes a scenario from an instruction and tests it (needs API credentials; never run yet) | `python tools/melee_actor/author.py "..."`; "Claude writing scenarios" in `docs/ai/native-ai.md` |
| Run the game headless, test interactions in seconds | `tools/melee_sim/` (`docs/ai/simulator.md`), skill `melee-sim` |
| AI on the native build: the interface, snapshots, the plan | `docs/ai/native-ai.md`; `tools/melee_native/native.py`; `python tests/native/env.py` |
| Train against a scenario yourself on the native build (verdicts in the terminal) | `python tools/melee_actor/train.py data/scenarios/FILE.json`; `tests/actor/train.py` |
| Play the native build yourself (a window on your desktop; no sound yet) | `python tools/melee_native/play.py [p1] [p2] [--stage S] [--cpu] [--input keyboard]`; `tests/native/live.py` |
| A picture from the native build's window variant, off screen | `tools/aurora32/build.sh`, `python tools/native_build.py --window`, `python tools/melee_native/window.py --out DIR`; "The game draws" in `docs/ai/native-ai.md` |
| Scripts of intentions instead of frames (the Melee Actor), slippi-ai research | `docs/ai/melee-actor.md`, `tools/melee_actor/`; `python tests/actor/uptilt.py` |
| The game as a native Linux process (vanilla only, headless), and how close it is to the console | `python tools/native_build.py` → `build/native/melee_headless`; `docs/ai/native-port.md` |
| Does the native build play the same game as the console's code? | `python tools/melee_native/compare.py` (`--random N`, `--tolerance`) |
| Does a native match depend on a variable the game never assigns? | `python tools/native_build.py --auto-init zero` and `pattern`, then `python tests/native/uninit.py`; kind 7 in `docs/ai/native-port.md` |

## Verification status

Be honest in reports about which of these you actually ran:

- matching build SHA check (`ninja` in matching mode)
- overlay layout check (`tools/overlay_check.py`)
- shifted dev link (`ninja` after `--non-matching`)
- boots in Dolphin (needs a full disc extract with the new `main.dol` in `sys/`)
