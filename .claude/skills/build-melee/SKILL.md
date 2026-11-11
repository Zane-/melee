---
name: build-melee
description: Configure and build the Melee decomp (matching or the non-matching training build), check the result, and run it in Dolphin. Use when asked to build, rebuild, verify a change compiles or still matches, or boot the game.
---

# Build Melee

## Prerequisites (check, do not assume)

| Need | Check | If missing |
|-|-|-|
| ninja | `.venv/bin/ninja --version` | `python3 -m venv .venv && .venv/bin/pip install ninja` |
| Retail DOL | `shasum orig/GALE01/sys/main.dol` = `08e0bf20134dfcb260699671004527b2d6bb1a45` | Extract from a v1.02 ISO; ask the user where theirs is |
| wibo | `build/tools/wibo-macos` exists | Download `wibo-macos` from the `decompals/wibo` GitHub releases (1.2.0 is known to work); ask the user first |
| Rosetta 2 (Apple Silicon) | `arch -x86_64 /usr/bin/true` exits 0 | The user must install it: `softwareupdate --install-rosetta`. Do not install it yourself |

The Metrowerks compiler is a Windows program. On this Mac it runs through `wibo-macos`
(x86_64, needs Rosetta). Always pass `--wrapper tools/wibo_macos_wrapper.py`, not wibo itself:
the build normally runs the compiler through `sjiswrap.exe` to feed it Shift JIS, and
`sjiswrap.exe` does not load under wibo-macos 1.2.0. The wrapper script does the conversion
itself for the ~15 sources with Japanese text. Symptoms of using wibo directly:
`PeLoaderErr(GetProcAddressFail)` on every compile. Without Rosetta: `Bad CPU type in
executable`. On Linux x86_64 the build downloads its own wibo and needs no `--wrapper`.

The wrapper only converts the `.c` file being compiled. If a header ever gains non-ASCII text
outside a comment, the matching SHA check will fail; fix the wrapper then.

The first `ninja` downloads the pinned tools (dtk, objdiff-cli, compilers, sjiswrap) into
`build/`. That is expected.

## Commands

Matching build (the default; must reproduce the retail DOL):

```sh
.venv/bin/python configure.py --wrapper tools/wibo_macos_wrapper.py --ninja .venv/bin/ninja
.venv/bin/ninja
```

The shipping training build is the address-preserving overlay (`docs/ai/overlay-build.md`):
run the matching build with ninja, then `python tools/overlay_build.py`. It compiles the mod
sources, links the overlay, applies `config/GALE01/tm_hooks.txt`, runs the layout check and
writes `build/overlay/main.dol`. Its last line must be `OK: vanilla layout preserved`.

Shifted dev build (links `Equivalent` mod objects anywhere; experiments only, breaks Slippi):

```sh
.venv/bin/python configure.py --wrapper tools/wibo_macos_wrapper.py --ninja .venv/bin/ninja --non-matching --map
.venv/bin/ninja
```

Other useful flags: `--debug` (`-O0`, implies non-matching), `--max-errors 0`, `--warn all`.

A clean build compiles ~1,100 objects in about 2.5 minutes on this machine; run it in the
background.
Incremental builds are fast.

## Reading the result

- Matching mode succeeds only if the linked DOL has the retail SHA-1. A mismatch means a
  vanilla function changed: an edit to vanilla code that changed its output. Find the unit
  with `build/tools/objdiff-cli` or `ninja diff`.
- `-maxerrors 1` is the default, so the compiler stops at the first error per file.
- Errors like `function has no prototype` come from `-requireprotos`: add a prototype or `static`.
- Non-matching mode has no hash check. Success is `build/GALE01/main.dol` being rewritten.

`configure.py` mode is sticky: `build.ninja` remembers the flags. Say which mode you left the
tree in.

## Setting up on another machine (Linux)

Nothing under `build/`, `orig/` or `.venv/` is in git. On a fresh checkout:

1. `python3 -m venv .venv && .venv/bin/pip install ninja` (or use a system ninja).
2. Put the retail v1.02 `main.dol` at `orig/GALE01/sys/main.dol`
   (SHA-1 `08e0bf20134dfcb260699671004527b2d6bb1a45`). `build/tools/dtk disc extract <iso>
   orig/GALE01` extracts the whole disc once dtk has been downloaded by the first ninja run;
   or extract the system data with Dolphin.
3. `python configure.py && ninja` — on Linux x86_64 no `--wrapper` is needed; the build
   downloads its own wibo. Confirm the SHA-1 match.
4. `python tools/overlay_build.py` — picks the wrapper for the host
   (`tools/overlay_wrapper.py`; override with `MELEE_WRAPPER`). **Only verified on macOS so
   far.**

## Boot test

Not done yet on any machine; update this section with what actually happens.

1. Extract the full disc to a scratch folder outside `orig/` (for example
   `build/disc/`): `build/tools/dtk disc extract <iso> build/disc`.
2. Copy `build/overlay/main.dol` over `build/disc/sys/main.dol`.
3. Optional, for the pause menu: copy `../TrainingMode/dats/eventMenu.dat` to
   `build/disc/files/TmMenu.dat`.
4. Open `build/disc/sys/main.dol` in Dolphin (it boots extracted discs from that layout), or
   add `build/disc` to Dolphin's game paths.

What to look for, in order:

| Check | Proves |
|-|-|
| Game reaches the title screen | Overlay sections load, arena patch is sound |
| "TM-Native v0.1" in the bottom-right corner | Boot and scene hooks run; overlay code calls vanilla correctly |
| 1P → Event Match shows the training event list | `function` hook and `tm_ess.c` work |
| Confirm → CSS → SSS → match starts, Laser Land panel in the top-left | `pointer` hook, match data, event framework |
| Start opens the TM menu (only with `TmMenu.dat`) | Menu engine and its art |
| Same steps in Slippi Dolphin, then a direct-connect match between two instances | Slippi compatibility; watch for "DESYNC DETECTED" |

If it crashes, Dolphin's log shows the faulting address: look it up in
`build/overlay/overlay.map` (overlay code, `0x804F1C00` and up) or with
`python tools/mex_symbols.py 0x<addr>` (vanilla code). Load `build/overlay/overlay.map`
alongside the vanilla map for symbols.

## Report

State which of these ran and their result: matching SHA check, non-matching link, boot test.
