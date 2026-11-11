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
| Compiler wrapper | `build/tools/wibo-macos` runs | See below |
| Rosetta 2 (Apple Silicon) | `arch -x86_64 /usr/bin/true` exits 0 | The user must install it: `softwareupdate --install-rosetta`. Do not install it yourself |

The Metrowerks compiler is a Windows program. On this Mac it runs through `wibo-macos`
(x86_64, from the `decompals/wibo` releases), passed with `--wrapper`. Without Rosetta every
compile step fails with `Bad CPU type in executable`. On Linux x86_64 the build downloads its
own wibo and needs no `--wrapper`.

The first `ninja` downloads the pinned tools (dtk, objdiff-cli, compilers, sjiswrap) into
`build/`. That is expected.

## Commands

Matching build (the default; must reproduce the retail DOL):

```sh
.venv/bin/python configure.py --wrapper build/tools/wibo-macos --ninja .venv/bin/ninja
.venv/bin/ninja
```

The shipping training build is the address-preserving overlay (`docs/ai/overlay-build.md`).
Its build mode does not exist yet. When it does, a build is good only if
`python tools/overlay_check.py build/GALE01/main.dol --patches <patch list>` passes.

Shifted dev build (links `Equivalent` mod objects anywhere; experiments only, breaks Slippi):

```sh
.venv/bin/python configure.py --wrapper build/tools/wibo-macos --ninja .venv/bin/ninja --non-matching --map
.venv/bin/ninja
```

Other useful flags: `--debug` (`-O0`, implies non-matching), `--max-errors 0`, `--warn all`.

A full build compiles ~1,100 objects; run it in the background if it may exceed two minutes.
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
