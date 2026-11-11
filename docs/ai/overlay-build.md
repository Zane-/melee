# The address-preserving overlay build

Decision (2026-11-11): the training build keeps every vanilla 1.02 address in place and adds
code as an overlay, so stock Slippi Dolphin works with it. Background: `slippi-tandem.md`.

Status: **design. Nothing below has been compiled or booted.** The compiler cannot run on this
machine until Rosetta 2 is installed. Each numbered experiment must pass before the section
that depends on it is treated as fact. Tools marked *works* have been run.

## The invariant

> In the built DOL, every vanilla section has its retail address, size and bytes, except at
> **declared patch sites**, and no patch site touches an address Slippi patches.

`tools/overlay_check.py BUILT.dol --patches <list>` enforces this (*works*; tested on the
retail DOL and on a synthetic modified one). It also checks `.bss`, the entry point, and that
new sections sit above the vanilla image and stack.

Vanilla layout facts (from the retail DOL and the linker script):

| Range | What |
|-|-|
| `0x80003100–0x803B7240` | `.init`, `.text` |
| `0x803B7240–0x804DEC00` | data, `.bss`, small data. Saved by Slippi rollback |
| `0x804DEC00–0x804F0C00` | stack and debug stack |
| `0x804F0C00` | vanilla `__ArenaLo`; heaps are carved upward from here at boot |

## Three build modes

| Mode | Vanilla objects | Mod objects | Result |
|-|-|-|-|
| matching | compiled with `MUST_MATCH` | not linked | retail DOL, SHA-checked |
| overlay (the training build) | compiled exactly as in matching mode | linked into overlay sections, patches applied post-link | layout-checked DOL |
| shifted (`--non-matching`) | may be edited freely | linked anywhere | dev/debug only, never for netplay |

The shifted mode stays useful for quick experiments and for `--debug` builds. Nothing meant to
ship may depend on it.

## Design

### 1. Where mod code and constants live

Mod objects put code, constants and string literals into dedicated sections, linked at a fixed
address at the vanilla `__ArenaLo` (`0x804F0C00`) and stored as extra DOL sections (the DOL
format has 5 spare text and 3 spare data slots). The arena start is then raised past the
overlay, the same net effect as m-ex, which claims its memory at arena-low during
`HSD_OSInit` and is known to run under Slippi (Akaneia).

- Experiment 1: can Metrowerks C route a whole file's code / const / string data to custom
  sections (`#pragma section`, a forced prefix header), with small data disabled
  (`-sdata 0 -sdata2 0`) so nothing lands in `.sdata` / `.sdata2`?
- Experiment 2: can the linker script place those sections at a fixed address after the stack
  without moving anything else, and does dtk's ELF → DOL step emit them?
- Experiment 3: how is the arena raised? Either the `__ArenaLo` link symbol moves (changes
  two instruction immediates in vanilla code; declare them as patch sites) or a boot patch
  calls `OSSetArenaLo`. Check neither site is a Slippi injection.
- Experiment 4: boot under Slippi Dolphin and confirm its bootloader, heap 5 and rollback still
  work with the arena raised. Slippi hardcodes one savestate range inside the arena
  (`0x8065C000–0x8071B000`, described in its source as "unknown region"); m-ex shifts the
  arena too, so this is expected to be fine, but it is the main risk.

### 2. Where mod state lives

- All mutable state: heap allocations made after boot (`HSD_MemAlloc`), reached from **one
  root pointer**.
- The root pointer must itself be inside a saved range. Options: a few bytes of unused vanilla
  `.bss` / `.sbss` (to be identified), or a slot in a vanilla struct that is unused.
  Experiment 5: pick and verify the slot.
- No writable statics in mod files. The overlay has no data or bss section for mutable data;
  the build should fail if a mod object emits one (checkable from the object's section sizes).
- State that must not roll back (coach link buffers, UI-only settings) is the exception. It
  can live in a separate unsaved allocation, and simulation code must never read it.

### 3. How mod code reaches vanilla, and vice versa

Mod → vanilla is ordinary linking: mod code calls vanilla functions and reads vanilla globals
by symbol.

Vanilla → mod uses post-link patches from a hook table. Planned kinds, cheapest first:

| Kind | Patch | Use |
|-|-|-|
| `pointer` | Store a mod function's address in a vanilla table slot | New game modes, scenes, stage and item callback tables |
| `call` | Retarget one `bl X` to `bl tm_X`, same signature; the mod wrapper calls `X` and adds behaviour | Most "do something before / after" hooks. Pure C, no register juggling |
| `function` | Write `b tm_F` at the entry of vanilla `F`; `tm_F` is an edited copy of the decomp's C | Behaviour changes inside a function |
| `inject` | Replace one instruction with a branch to a small asm trampoline | Last resort, when a value is only in a register mid-function |
| `word` | Overwrite a data word or an immediate | Constants, `sizeof(Fighter)` |

Constraints:

- `function` replacement is **forbidden for any function Slippi patches**; Slippi's injection
  would land in dead code. 31 functions that TM-CE hooks are in that set, including
  `Fighter_procInput`, `Fighter_procAnim`, `gm_801A4D34` (frame loop), `gm_801A4BD4`,
  `fn_8016E730` (match start) and the CSS. Use `call` or `inject` there.
- A replaced function that uses its file's `static` functions or data cannot be compiled in a
  separate mod file. Experiment 6: add the replacement to the vanilla source file under an
  overlay-only `#ifdef`, routed to the overlay section, and confirm the object's vanilla
  sections stay byte-identical.
- Growing `struct Fighter`: the allocation size is one immediate in `Fighter_800679B0`
  (TM-CE and m-ex patch the same instruction). Vanilla code compiled with the vanilla layout
  never touches appended fields, so appending is safe. Slippi patches `Fighter_Create+0x54`
  for recording; do not use that site to initialise the new fields.

The hook table is one file (planned: `config/GALE01/tm_hooks.txt`), each line
`kind  vanilla_symbol+offset  target_symbol  note`. The patcher resolves symbols from the
linked ELF, applies the patches, and writes the patch-site list that `overlay_check.py`
consumes. The patcher does not exist yet.

### 4. Conflicts between TM-CE's hooks and Slippi's

`tools/tm_slippi_collisions.py` (*works*) compares TM-CE's 288 injection addresses with
Slippi's 309 (`config/GALE01/slippi_injections.txt`, from `slippi-ssbm-asm` commit `d0ce23a`,
2026-11-02):

| Result | Count | Meaning |
|-|-|-|
| exact | 42 | Same address. 39 are "Additional Codes" that Slippi already ships (unlock everything, tournament defaults, neutral spawns, nametag length, CSS tweaks); drop them. The other three need care: per-fighter variable init at `Fighter_Create+0x54`, UCF dashback at `ftCo_Turn_IASA+0x4C` (Slippi ships UCF), and "On No Save" at `gm_Scene_MemCard_OnFrame+0x18C` |
| shared | 52 | Slippi patches elsewhere in the same function. Patch one site; never replace the function |
| free | 194 | No conflict |

Re-run both tools whenever Slippi updates its codeset.

## Experiments, in order

| # | Question | Blocks |
|-|-|-|
| 0 | Does the matching build pass on this machine? (needs Rosetta) | everything |
| 1 | Custom sections for a whole mod file, no small data | all mod code |
| 2 | Linker script places overlay; DOL contains it; `overlay_check.py` passes | all mod code |
| 3 | Raise the arena without touching a Slippi site | boot |
| 4 | Boots in Dolphin; boots in Slippi Dolphin; a direct-connect match between two local instances stays in sync with a no-op overlay | netplay |
| 5 | Root pointer slot inside a saved range | any mod state |
| 6 | Overlay-only function inside a vanilla source file leaves vanilla bytes identical | `function` hooks |
| 7 | Patcher: `pointer` and `call` kinds first | all hooks |

Record each result here, replacing the question with what was found.
