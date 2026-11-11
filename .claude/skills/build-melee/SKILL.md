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
run the matching build, compile mod files with the overlay flags, then
`python tools/overlay_link.py -o OUT objs... --hooks hooks.txt` and
`python tools/overlay_check.py OUT/main.dol --patches OUT/patches.txt`. This is not in ninja
yet.

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

## Run in Dolphin

Unverified on this machine; update this section after the first successful boot.

1. Extract the full disc once (git-ignored): `build/tools/dtk disc extract <iso> orig/GALE01`
   (`files/` and `sys/` appear).
2. Copy `build/GALE01/main.dol` over a **copy** of the extract's `sys/main.dol`; keep
   `orig/GALE01/sys/main.dol` retail, the build reads it.
3. Open that folder's `sys/main.dol` in Dolphin (`/Applications/Dolphin.app`), or add the
   folder to Dolphin's game paths.
4. With `--map`, load `build/GALE01/main.elf.MAP` as Dolphin's symbol map for debugging.

## Report

State which of these ran and their result: matching SHA check, non-matching link, boot test.
