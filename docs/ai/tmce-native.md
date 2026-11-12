# TM-CE native port

Decided 2026-11-11 by the owner: the training build is **TM-CE, faithfully**, with custom
character drills added later on the same machinery. TM-CE's own C is compiled nearly
unmodified and linked into the overlay; its assembly is rewritten as native C hooks.

This replaces the earlier plan in `training-mode-port.md` of reimplementing TM-CE against the
decomp (the reimplemented menu engine, event select screen and Laser Land were deleted).

## How TM-CE works (what we replace)

TM-CE = vanilla disc + m-ex's `Start.dol` + `codes.gct` (all of `ASM/`, as Gecko codes) +
`TM/*.dat`. Each `TM/*.dat` is an art archive with relocatable code merged in by `hmex`:

- `TM/eventMenu.dat`: the core (`events.c menu.c osds.c savestate_v1.c`) and menu art. Loaded at
  boot by `Misc/Load eventMenu.dat.asm`; its `tmFunction` table is copied to r2-relative slots
  that the assembly calls (`rtocbl r12, TM_*`).
- `TM/<event>.dat`: one event (`evFunction` table: `Event_Init`, `Event_Update`, `Event_Think`,
  `Event_Menu`), loaded by `EventLoad` through m-ex's `MEX_LoadRelArchive`.
- `TM/labCSS.dat`: `lab_css.c` (`cssFunction`: `OnCSSLoad`), loaded by `Hooks/OnCSSLoad.asm`.
- Event code reaches the core through `event_vars` (`EventVars`, function pointers inside).
- Settings live in unused vanilla save data (`MemcardData` +0x1F24.., `TM_EventPage` 0x1F29).

## How the native build does it

| Piece | Where |
|-|-|
| TM-CE C, compiled as-is | `../TrainingMode/src` (or `$TMCE_DIR`), copied to `build/overlay/tmce/` and patched |
| Patches to TM-CE (keep tiny) | `src/tmce/patches/*.patch` |
| Units (mirrors `build.sh`) | `src/tmce/units.txt` |
| m-ex runtime replacements (`calloc`, `MEX_LoadRelArchive`, `blr2`, `strrchr`, `event_vars`) | `src/tmce/mex_runtime.c` |
| Boot loading, bridge functions for native code | `src/tmce/boot.c`, declared in `src/melee/tm/tmce.h` |
| libc shims for the C99 compiler | `src/tmce/include/` |
| Native hooks replacing TM-CE assembly | `src/melee/tm/` and `src/melee/tm/<area>/` |
| Hook tables | `config/GALE01/tm_hooks.txt`, `config/GALE01/tm_hooks/<area>.txt` |
| Disc prep (art dats → `files/TM/`) | `tools/tmce_disc.py` |

Build details (`tools/overlay_build.py`):

- TM-CE units compile with **MWCC GC/3.0a5.2 `-lang=c99`** (1.2.5n has no C99) against the
  MexTK headers, with the overlay prefix, `-sdata 0 -sdata2 0` (vanilla owns r2/r13) and
  `-Cpp_exceptions off`.
- Event and css units each defined the same names; `objcopy` renames their table exports to
  `tmce_<unit>_<export>` and localises everything else. A generated registry
  (`build/overlay/tmce/tmce_registry.c`, `src/tmce/tmce_registry.h`) maps `TM/<unit>.dat` to
  those functions; `MEX_LoadRelArchive` looks it up and loads the art archive if the file exists.
- MexTK names resolve through `MexTK/melee.link`, only to addresses where a vanilla symbol starts.
  MexTK names that vanilla uses for a different address are renamed `mex__NAME` in TM-CE objects.
- The C99 compilers call `_savegpr_N`/`_restgpr_N`; vanilla has none. `overlay_link.py`
  generates them as machine code at the overlay origin (`.tmrt`).
- Writable statics are allowed (owner decision 2026-11-11). They are not rollback-saved, so
  anything that runs during netplay keeps its state under `tm_state`.
- Size: ~295 KB at `0x804F0C00`; the arena starts after it.

Struct layout: `python tools/tmce_layout_check.py` compares every TM-CE/MexTK struct between
clang (gcc's PowerPC ABI, what TM-CE is normally built with) and MWCC. 327 structs, 9396
offsets/sizes: only `FtScript` differs (packed; only used through a pointer). MexTK's offset
comments are often wrong (absolute offsets inside sub-structs); trust the declarations.

Patches to TM-CE (`src/tmce/patches/`): 0001 `event_vars` global, 0002 MWCC can't copy a const
struct in an initializer, 0003 lab_css calls the core directly, 0004 `FtDataToID` rejects
non-RAM pointers (stale victim pointers in inactive hitboxes; TM-CE only gets away with it
because that memory happens to be zero in its build).

`slippi-word` hooks (`config/GALE01/tm_hooks/unlock.txt`): TM-CE's Unlock Everything sits on
Slippi's required General Codes sites with the same effect. They are applied for plain Dolphin;
under Slippi its codes are applied after the DOL loads and win. Only that kind may touch a
Slippi site.

Fighter block: TM-CE's `FighterData` is 0x2530 bytes (vanilla 0x23EC + m-ex 0xC + TM 0x138,
`FighterData.TM` at 0x23F8). `src/melee/tm/tm_fighter.c` sizes `fighter_alloc_data` to at
least `sizeof(FighterData)` and zeroes each block on creation (m-ex's Custom Playerdata
Variables). m-ex's own sites are Slippi Recording injections, so the hooks wrap the neighbouring
calls. Slippi Recording grows the block to 0x2600 and only uses byte 0x25FF (`LCancelStatus`;
slippi-ssbm-asm `Recording/Recording.s` at d0ce23a), so it does not overlap TM-CE's
0x23EC-0x2530. Under Slippi the hook keeps Slippi's larger size.

Known deviations from TM-CE kept on purpose:

- OSD and legacy ports fix more TM-CE bugs, each noted in the C: combo damage always read
  port 1; Powershield's stray store through r29; L-cancel counters overlapping vanilla's score
  display cache (now statics); legacy savestates kept a dangling backup pointer;
  PlacePlayersCenterStage read code bytes for slots 2-5; DisableHazards jumped through code
  bytes for stage kinds > 32.

- OSD core fixes TM-CE bugs: previous-move-instance is stored at `TM.last_move_hurt` (0x2414,
  which the SDI display reads) instead of 0x2418; the insta double jump table is indexed by
  the ply byte, not a word; expired message queue entries are cleared; the OSD window count
  (0x1F28) is clamped to 3.

- `lab.c` rewrites one vanilla instruction at runtime (Pokémon Stadium transformation,
  `0x801D463C`). Kept for fidelity; should become a `call` hook.
- TM-CE's OnSceneChange ran at `gm_801A4BD4+0xC0`; ours runs at `+0xF4` (three calls later).

## Porting a TM-CE assembly file

Work by area (parallel workers used this in the first round). Each area owns `src/melee/tm/<area>/`, `config/GALE01/tm_hooks/<area>.txt`
and optionally `src/tmce/<area>_*.c` (code that needs MexTK types). Areas in progress:

| Area | TM-CE assembly | 
|-|-|
| `ess` | `Custom Events/Event Select Screen/**`, `Custom Events/Unlock All Events/*` |
| `css` | `Custom Events/CSS and SSS/**`, `Custom Events/Custom Event Preload Behavior/*`, `Custom Events/A+B to Reset Event/*`, `Hooks/OnCSSLoad.asm` |
| `addcodes` | `Additional Codes/**` (except Unlock Everything: `config/GALE01/tm_hooks/unlock.txt`), `m-ex/UCF 0.84/` |
| `misc` | `Misc/**` except `Load eventMenu.dat.asm` (done) and `On No Save.asm` (Slippi already does it) |
| later | `Onscreen Display/**` (82), the 15 legacy events in `Custom Event Code - Rewrite.asm`, `Additional Codes/**` (pick per code; many duplicate Slippi) |

For each file:

1. Read the `.asm` and find its site's vanilla function (`python tools/mex_symbols.py 0x<addr>`).
   `python tools/tm_slippi_collisions.py` lists sites that are or share a function with a
   Slippi injection. An exact collision means Slippi already does it, or it cannot be ported as is.
2. Pick the hook, in this order: `word` (single-instruction patches, 2-line `.asm` files are
   usually this), `call` (wrap a `bl` near the site), `function` (edited copy of the whole
   vanilla function; not allowed when Slippi patches inside it), `pointer` (callback tables),
   and `inject` only with a written reason.
3. Write the C: decomp headers in `src/melee/tm/<area>/`, or MexTK types in `src/tmce/<area>_*.c`.
   Cross the boundary with plain prototypes (`void*` for the other side's types), as `tmce.h` does.
4. Name the `.asm` file being replaced in a comment next to the hook entry and in the C.
5. Build: `OVERLAY_OUT=build/overlay-<area> TM_EXCLUDE=<other areas> python tools/overlay_build.py`.

## Status

See "Port status" below; update it as pieces are booted.

| Piece | State |
|-|-|
| TM-CE C (core + 14 events + labCSS) compiled and linked | Builds, layout check passes. Not booted |
| Boot (eventMenu.dat, OnFileLoad), OnSceneChange, OnStartMelee | Ported (`src/melee/tm/tm.c`, `src/tmce/boot.c`). Not booted |
| C-event match setup (`onEnterVs` + `EventInit`) | Ported (`src/melee/tm/tm_event_start.c`). Not booted |
| Event select screen (`ess`: 24 ported, 1 no-op dropped) | Ported, not booted. L (OSD menu) needs the OSD area |
| Event CSS/SSS flow (`css`: 21 ported, 1 no-op dropped). Event mode runs from a replacement state list (CSS → match → SSS) | Ported, not booted |
| Misc (`misc`: 37 ported, 4 dropped: On No Save = Slippi; Boot Up Tasks = dead; nametag save and save renaming = m-ex launcher only) | Ported, not booted |
| Unlock Everything (Additional Codes; trophies spoofed, save not filled) | Ported as `slippi-word`, not booted |
| Boot → ESS → Lab CSS → SSS → Lab match | **Booted 2026-11-11** (plain Dolphin, Linux). Savestate bad read fixed by patch 0004 |
| OSD toggle menu (`osdmenu`: Toggle UI, 13 files) | Ported, not booted |
| OSD core (`osdcore`: message system, FighterData.TM per-frame bookkeeping, fastfall, frame advantage, previous move instance, Generic Per Frame, IC follower check, Act OoWait). API in `src/melee/tm/osdcore/osd.h` | Ported, not booted. `Fighter_ChangeMotionState` and `ftCommon_CheckFallFast` are replaced by edited copies (hooks inside the vanilla bodies would be dead) |
| Individual OSDs: `osdact` (act out of airborne/shield/tumble/float, 24 + 3 statics, 1 dead dropped), `osdtech` (ledge codes/GALINT, dashback, wavedash, SDI; 13), `osdmisc` (combo counter, L-cancel, powershield, jump cancel, grab breakout, boost grab, glide toss, airdodge item throw, Yoshi egg, Bowser fortress; 17, 2 dead dropped) | Ported, not booted. All of Onscreen Display/ is now covered |
| Legacy events (`src/melee/tm/legacy`): dispatch from `tm_event_start.c`, shared library (lines 8600-12371), and all 15 events (Multishine, Reaction, Ledge Stall, Ledgetech, Ledgetech Counter, Amsah Tech, SDI Training, Combo Training, Reversal, Shield Drop, Escape Sheik, Slide Off, Waveshine SDI, Attack on Shield, Grab Mash Out) | Ported, not booted |
| Additional Codes (`addcodes`): Enable C Stick Always, Better Camera, Boot to Event Mode (extended: **boots straight into the Training Lab's CSS**; hold X at boot for VS CSS, Y for the main menu; `TM_AC_BOOT_TO_LAB` in `src/melee/tm/addcodes/addcodes.h` turns it off), Force Game Loop, develop-mode and debug-menu codes, On Crash, tournament defaults (`slippi-word`), ungrabbable hurtboxes, collision draw order, FoD reflection, and ~25 one-word codes | Ported, not booted |
| Hitbox Visualizer + Hide Player GFX When Hitboxes Enabled | In progress |
| Additional Codes dropped because Slippi provides them (the owner runs this build on Slippi Dolphin, decided 2026-11-11): UCF 0.84, Polling Drift Fix, Neutral Spawn/Respawn, Longer Nametags, Random CSS Music, Salty Runback, Hide Nametag When Invisible, Disable FoD in Doubles, L+R+A Returns to CSS, Lag Reduction Prompt, CSS door/rumble codes | Dropped on purpose |
| Additional Codes not done: Physics Display, Idle Screen, Display Animation Name, Enable 1P in VS No Time, Reboot With LRAStart | Not started |
| Skills for adding new events (owner request; after parity) | Not started |

Open questions from the area ports (check when booting):

- TM-CE's CPU/character backup area in the save data (`+0xD10`, raw offsets) is not mapped to
  decomp types.
- `Increase CSS SIS Text Heap` sits on a Slippi site; it is ported as a `call` hook on
  `preloadState+0x58` instead.
- The event select help panel writes its QR code straight into the GX FIFO, relying on the
  vertex format left by earlier drawing, as TM-CE does.
