# The address-preserving overlay build

Decision (2026-11-11): the training build keeps every vanilla 1.02 address in place and adds
code as an overlay, so stock Slippi Dolphin works with it. Background: `slippi-tandem.md`.

Status (2026-11-11): **the build-time half works; nothing has been booted.** A test file
compiles into overlay sections, links against vanilla symbols, is appended to the matching DOL
with hooks applied, and passes the layout check. Whether that DOL runs, and runs under Slippi,
is untested. `python tools/overlay_build.py` runs the whole overlay build (compile mod
sources, link, hook, check) on top of a matching build; it is not part of ninja.

## The invariant

> In the built DOL, every vanilla section has its retail address, size and bytes, except at
> **declared patch sites**, and no patch site touches an address Slippi patches.

`tools/overlay_check.py BUILT.dol --patches patches.txt` enforces this. It also checks `.bss`,
the entry point, and that new sections sit above the vanilla image and stack.

Vanilla layout facts (from the retail DOL and the linker script):

| Range | What |
|-|-|
| `0x80003100–0x803B7240` | `.init`, `.text` |
| `0x803B7240–0x804DEC00` | data, `.bss`, small data. Saved by Slippi rollback |
| `0x804DEC00–0x804EEC00` | stack |
| `0x804EEC00–0x804F0C00` | debug-monitor stack. On a retail disc `OSInit` starts the arena at `0x804EEC00` |
| `0x804F0C00` | `__ArenaLo` link symbol; **overlay origin** |

## How the overlay build works

```
vanilla sources ──matching build──▶ build/GALE01/main.elf + main.dol   (SHA-checked, never relinked)
mod sources ──mwcc + overlay flags──▶ *.o with only .tmtext / .tmrodata
                 tools/overlay_link.py
                   1. reject objects with vanilla-named or writable sections
                   2. resolve their undefined symbols to addresses from main.elf
                   3. link them alone at 0x804F0C00 (generated linker script)
                   4. append the sections to a copy of main.dol (spare DOL slots)
                   5. patch OSInit so the arena starts after the overlay
                   6. apply the hook table
                 ──▶ out/main.dol, patches.txt, overlay_symbols.txt, overlay.map
tools/overlay_check.py out/main.dol --patches out/patches.txt
```

The vanilla image is never relinked, so it cannot drift: it is the matching DOL plus the
listed 4-byte patches.

### Compiling a mod file

```sh
mwcceppc <the normal flags, without -DMUST_MATCH> \
  -i src/melee/tm -prefix overlay_prefix.h \
  -sdata 0 -sdata2 0 -str reuse,readonly -c src/melee/tm/foo.c
```

- `src/melee/tm/overlay_prefix.h` routes code to `.tmtext` and constants to `.tmrodata`.
- `-sdata 0 -sdata2 0` keeps floats and short strings out of the small-data sections;
  `-str reuse,readonly` puts string literals in `.tmrodata`.
- Anything writable (a non-`const` static or global, initialised or not) lands in `.tmdata` /
  `.tmbss`, and `overlay_link.py` refuses the object. Mutable state goes on the heap.
- Includes use full paths as in vanilla files: `<sysdolphin/baselib/gobj.h>`,
  `<melee/ft/types.h>`, `<dolphin/os.h>`.

### Calling vanilla from the overlay

Ordinary C. Undefined symbols are resolved by name from `main.elf`:

- any vanilla global function or variable;
- a vanilla `static` function or variable too, if its name is unique in the whole game
  (declare it `extern` in the mod file). Ambiguous names (`onEnterVs` exists in several
  files) are rejected; reach those another way.

Vanilla small-data globals are read with absolute addressing (the overlay does not use r13),
so nothing special is needed.

### Hooks: calling the overlay from vanilla

A hook table file, one line per hook, passed as `--hooks`:

```
# kind     site                          target         note
call       fn_801695BC+0x108             tm_Randi       wrap one HSD_Randi call
function   gm_AnyControllerPressedZ      tm_FrameAdv    replace whole function
word       Fighter_800679B0+0xC          0x38802524     allocation size immediate
```

| Kind | Patch | Use | State |
|-|-|-|-|
| `call` | Retargets one `bl X` to an overlay function with X's signature, which normally calls X itself | Most "before / after" hooks. Pure C | works |
| `function` | Writes `b target` at a vanilla function's entry | Behaviour changes; the target is an edited copy of the decomp's C | works |
| `word` | Overwrites one 32-bit word | Constants, immediates, table slots with known values | works |
| `pointer` | Stores an overlay symbol's address in a vanilla data slot | Mode, scene, stage and item callback tables | works |
| `inject` | Replaces one instruction with a branch to a generated trampoline that calls `void target(TmRegs*)` (`src/melee/tm/tm_hook.h`), restores registers, runs the displaced instruction and resumes | Last resort, when a value is only in a register mid-function. The target can read and edit registers | builds; trampoline disassembly checked; never executed |

The tool refuses:

- any site Slippi patches (`config/GALE01/slippi_injections.txt`);
- a `function` hook on a function Slippi patches anywhere inside (its injection would land in
  dead code). This covers `Fighter_procInput`, `Fighter_procAnim`, the frame loop
  `gm_801A4D34`, `gm_801A4BD4`, match start `fn_8016E730` and the CSS, among others. Use
  `call` there;
- a `call` hook on an instruction that is not a `bl`;
- an `inject` hook on a branch instruction, a `pointer` hook on code, two hooks on one site.

The project's hook table is `config/GALE01/tm_hooks.txt`.

Order of preference: `pointer`, `call`, `function`, `word`, and `inject` only as a last
resort. The project goal is no assembly: an `inject` hook is the one place machine code is
generated rather than compiled from C, and so far none is used. A whole vanilla screen or
subsystem can often be replaced with a single `function` hook on its entry point when the rest
of its functions are only reachable from there (see `src/melee/tm/tm_ess.c`).

### Where mod state lives

Overlay code has no writable statics (enforced at link time). There are two roots, both
absolute symbols from `config/GALE01/tm_symbols.txt`, declared in `src/melee/tm/tm.h`:

| Root | Address | Lifetime | Rolled back by Slippi | Use |
|-|-|-|-|-|
| `tm_state` (`TmMatch*`) | `0x804D646C`: 4 bytes of alignment padding at the end of `camera.c`'s `.sbss`, zeroed at boot, unused by Slippi, m-ex and TM-CE | Points at a `HSD_MemAlloc` block created at match start; NULL outside a match | Yes (pointer and block) | Everything that affects or follows the simulation |
| `tm_persist` (`TmPersist`) | `0x804F0C00`, 0x1000 bytes reserved below the overlay code (which is linked at `0x804F1C00`) | Whole session; cleared by the boot hook | **No** | Settings chosen outside a match, display-only data |

The scene heap is reset on every scene change, so anything allocated with `HSD_MemAlloc` dies
with the scene; `tm_Hook_SceneChange` clears the pointers.

### Struct growth

Appending fields to `struct Fighter` needs no vanilla recompilation: vanilla code never touches
the new fields, and the allocation size is a single immediate (a `word` hook; TM-CE and m-ex
patch the same instruction in `Fighter_800679B0`). Slippi patches `Fighter_Create+0x54`, so
initialise new fields elsewhere. Untested.

## Conflicts between TM-CE's hooks and Slippi's

`tools/tm_slippi_collisions.py` compares TM-CE's 288 injection addresses with Slippi's 309
(from `slippi-ssbm-asm` commit `d0ce23a`, 2026-11-02):

| Result | Count | Meaning |
|-|-|-|
| exact | 42 | Same address. 39 are "Additional Codes" Slippi already ships (unlock everything, tournament defaults, neutral spawns, nametag length, CSS tweaks); drop them. Three need care: per-fighter variable init at `Fighter_Create+0x54`, UCF dashback at `ftCo_Turn_IASA+0x4C` (Slippi ships UCF), and "On No Save" at `gm_Scene_MemCard_OnFrame+0x18C` |
| shared | 52 | Slippi patches elsewhere in the same function. Use `call`; never `function` |
| free | 194 | No conflict |

Re-run both tools and regenerate `slippi_injections.txt` whenever Slippi updates its codeset.

## Experiments

| # | Question | Result |
|-|-|-|
| 0 | Matching build on this machine | **Pass.** Retail SHA-1 reproduced with `--wrapper tools/wibo_macos_wrapper.py` |
| 1 | Route a whole mod file to custom sections, no small data | **Pass.** `#pragma section` in a `-prefix` header plus `-sdata 0 -sdata2 0 -str reuse,readonly` leaves only `.tmtext` and `.tmrodata` |
| 2 | Place the overlay without moving vanilla | **Pass, by a different route than planned.** Linking mod objects together with the vanilla objects grows `.init` (the linker adds a ROM-copy table entry per section) and shifts the whole image by 0x20. Linking the overlay separately against absolute vanilla addresses and appending it to the matching DOL leaves vanilla untouched. Branch targets and data addresses in the output were decoded and are correct |
| 3 | Raise the arena without touching a Slippi site | **Pass at build level.** Two `lis`/`addi` pairs in `OSInit` (`0x80343094`, `0x803430CC`) are patched to the overlay end. Neither is a Slippi site. The second pair matters: on a retail disc the arena starts at `_stack_addr`, not `__ArenaLo`. Not booted |
| 7 | Patcher | **Done at build level.** All five hook kinds are implemented and checked against Slippi |
| 4 | Boots in Dolphin; boots in Slippi Dolphin; a direct-connect match between two local instances stays in sync with a do-nothing overlay | **Not run.** Needs a full disc extract and a visible test hook. Main risk: Slippi hardcodes one savestate range inside the arena (`0x8065C000–0x8071B000`, "unknown region" in its source) and the overlay shifts the arena up. m-ex shifts it too and runs under Slippi, so this is expected to work |
| 5 | Root pointer slot inside a saved range | **Chosen, not exercised:** `0x804D646C` (see "Where mod state lives") |
| 6 | Replacing a function that uses its file's `static`s | Mostly answered by experiment 2: the overlay can reference uniquely named vanilla statics directly. Ambiguous names remain a gap |
| 8 | One-command overlay build | **Done** as `tools/overlay_build.py` (outside ninja). It refuses to run unless `build/GALE01/main.dol` has the retail SHA-1 |

## Memory: what the overlay takes, and from where (2026-11-13)

The game carves three fixed heaps out of the arena (`lbHeap_803BA380`,
`src/melee/lb/lbheap.c`) and the **scene heap** (models, objects, everything
`HSD_MemAlloc` gives out) is what is left between them:

```
arena low ─ boot allocations ─ [Stay 5.2 MB] [scene heap] [match file cache 6.6 MB] ─ arena high
```

Raising the arena low past the overlay therefore shrank exactly the scene heap, by the
overlay's size (0.58 MB of 6.1). The Versus character select needs more than what was left
and asserted in `HSD_MemAlloc`, in Dolphin and in the simulator.

`overlay_link.py` (step 8) now makes the **match file cache** smaller by the overlay's
footprint instead (one data word, `lbHeap_803BA380+0x2C`; not a Slippi site), so the scene
heap is its vanilla size again. Shrinking "Stay" instead does not work: the boot preload
fills it. Slippi saves the scene heap by the bounds the game keeps (`slippi-tandem.md`), so
the boundary may move.

The cost. The cache holds a match's stage and fighter files; vanilla sizes it for the
largest case. Measured in use at match start, in the simulator, of 6.00 MB:

| Match | In use |
|-|-|
| Fox, Marth, Battlefield | 1.99 MB |
| Ice Climbers, Donkey Kong, Dream Land | 2.49 MB |
| Peach, Roy, Fountain of Dreams | 3.18 MB |
| Peach, Roy, Pokemon Stadium | 5.07 MB |

Pokemon Stadium is about 3.1 MB by itself (its transformations) and the heaviest fighters
about 1 MB each, so every two-player match fits, and every four-player match on the other
stages should (the largest other stage file is 2.3 MB). **Four players on Pokemon Stadium
with heavy characters would need up to 6.6 MB and will not fit**: the load asserts
(`memp_kouho` in `lbmemory.c`), there is no fallback. Not tried. Getting that back means
making the overlay smaller or not resident.
