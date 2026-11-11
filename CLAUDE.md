# Melee decomp — agent guide

This repo is the matching decompilation of Super Smash Bros. Melee (NTSC 1.02, `GALE01`).
This fork's goal is a **custom training build**: Training Mode (UnclePunch / TM-CE, source in
`../TrainingMode`) ported to native C, an in-game AI coach driven by Claude, and
tandem training over Slippi direct connect. Read `docs/ai/README.md` for the doc index.

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
- No writable statics in mod code. Mutable state is heap-allocated and reached from one root
  pointer, so Slippi's rollback saves it.
- Never replace or patch at an address Slippi patches (`config/GALE01/slippi_injections.txt`).
- `tools/overlay_check.py` must pass on any DOL meant to run.
- `--non-matching` (freely shifted) builds are for local experiments only.
- **No assembly (project goal, set by the owner 2026-11-11).** Mod code is C. Port TM-CE's
  assembly injections by understanding what they do and writing C against the decomp, usually
  as an edited copy of the vanilla function behind a `function` or `call` hook
  (`src/melee/tm/tm_ess.c` replaces ~25 injections that way). Do not add `.s` files or inline
  asm. The `inject` hook kind (a generated register-saving trampoline) is a last resort; if
  you think you need it, look for a `call`, `function` or `pointer` hook first and say why
  none works.

The overlay toolchain works at build level: `python tools/overlay_build.py` compiles
`src/melee/tm` and `src/melee/ai`, links them as an overlay, applies
`config/GALE01/tm_hooks.txt` and runs the layout check, on top of a matching build. **No
overlay DOL has been booted yet.** See the experiment table in `overlay-build.md` for what is
proven, and "Port status" in `training-mode-port.md` for what has been ported.

## Build

```sh
. .venv/bin/activate                      # ninja lives here
python configure.py --wrapper tools/wibo_macos_wrapper.py            # matching
python configure.py --wrapper tools/wibo_macos_wrapper.py --non-matching --map   # shifted dev build, not for netplay
ninja
```

- Needs `orig/GALE01/sys/main.dol` (already extracted, git-ignored), Rosetta 2, and
  `build/tools/wibo-macos`. The wrapper script replaces `sjiswrap.exe`, which does not load
  under wibo on macOS.
- Verified 2026-11-11: the matching build reproduces the retail SHA-1 on this machine in
  about 2.5 minutes from clean.
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
| Training Mode port plan and MexTK ↔ decomp mapping | `docs/ai/training-mode-port.md` |
| AI coach design | `docs/ai/ai-coach.md` |
| Slippi direct-connect tandem training research | `docs/ai/slippi-tandem.md` |
| MexTK name → decomp name | `python tools/mex_symbols.py <name-or-0xaddr>` |
| Build the training overlay DOL | `python tools/overlay_build.py` → `build/overlay/main.dol` |
| Does a DOL keep the vanilla layout? | `python tools/overlay_check.py <dol> [--patches list]` |
| Does a TM-CE hook clash with Slippi? | `python tools/tm_slippi_collisions.py [--function NAME]` |

## Verification status

Be honest in reports about which of these you actually ran:

- matching build SHA check (`ninja` in matching mode)
- overlay layout check (`tools/overlay_check.py`)
- shifted dev link (`ninja` after `--non-matching`)
- boots in Dolphin (needs a full disc extract with the new `main.dol` in `sys/`)
