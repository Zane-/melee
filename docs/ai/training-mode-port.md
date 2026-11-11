# Porting Training Mode (TM-CE) to native code

Source: `../TrainingMode` (TM-CE v1.4 d2). Its own docs: `CLAUDE.md`, `DEVELOPMENT.md`,
`docs/ADDING_SCENARIOS.md`. This doc is a plan; nothing below has been ported yet.

## What TM-CE is made of

| Part | Size | What it is |
|-|-|-|
| `src/*.c, *.h` | 27,156 lines | C compiled by MexTK into relocatable `.dat` modules loaded at runtime |
| `ASM/**/*.asm` | 307 files, ~26k lines | Gecko injections into vanilla functions |
| `MexTK/include` | 18k lines | Hand-written headers describing vanilla structs and functions |
| `MexTK/melee.link` | 1,094 entries | Name → vanilla address map for the linker |
| `dats/*.dat` | 4 files | Art assets: menu, lab HUD, CSS, wavedash |
| `Build TM Start.dol` | xdelta patch | Patches the DOL to load the Gecko code file at boot |

The C side is split into:

- `eventMenu.dat`: `events.c` (event registry, lifecycle, HUD and message helpers), `menu.c`
  (pause menu engine), `osds.c`, `savestate_v1.c`. Loaded at boot, always resident.
- One `.dat` per event: `lab.c` (7,156 lines, the Training Lab), `ledgedash.c`, `lcancel.c`,
  `wavedash.c`, `techchase.c`, `powershield.c`, `edgeguard.c` + `recovery.c`, `shineoos.c`,
  `dthrowknee.c`, `sweetspot.c`, `slalom.c`, `eggs.c`, `fc.c`, `laserland.c`.
- `lab_css.c`: recording import menu on the character select screen.

14 events are C. 15 are legacy ASM inside one file
(`ASM/training-mode/Custom Events/Custom Event Code - Rewrite.asm`, 12,371 lines).

## Why a native port is simpler than the mod

| TM-CE mechanism | Native replacement |
|-|-|
| m-ex loader, relocation tables, function table at `rtoc-0xC8` | Gone. Events are ordinary functions linked into the DOL |
| m-ex `calloc` and loader living on top of vanilla result-screen data (`0x803D7038…`) | Gone. Use `HSD_MemAlloc` |
| `melee.link` and MexTK headers | The decomp's own headers. Map names with `tools/mex_symbols.py` |
| ASM that grows `FighterData` by 0x138 and fills it | Fields appended to `struct Fighter` (one `word` patch for the size), filled through hook-table entries |
| Runtime instruction patches (e.g. `*(u32*)0x801d463c = ...`) | A build-time hook-table entry |
| Hardcoded addresses of callback tables, particle pools, floats | Symbols |
| Hijacked Event Mode (scene `0x2B`) and Rules screen | A new `GM_` mode with its own state list, or a custom stage for netplay drills (decision below) |

`docs/ai/tm-symbol-map.tsv` lists the 256 vanilla functions TM-CE's C calls with their decomp
names. 255 resolve. 110 are still address-named in the decomp; the MexTK name is the best
available description of those.

## Where TM-CE's hooks land in the decomp

| TM-CE hook (address) | Purpose | Decomp location |
|-|-|-|
| `OnBoot` (801BFA28) | One-time init | `bootOnLeave`, `gm/gmboot.c` |
| `OnSceneChange` (801A4C94) | Per-scene init (watermark, console) | `gm_801A4BD4`, `gm/gmscene.c` |
| `OnStartMelee` (8016E8C8) | Per-match init (messages, tips) | `fn_8016E730`, `gm/gmvs.c` |
| `OnCSSLoad` (80266810) | Load CSS extras for an event | `mnCharSel_802640A0`, `mn/mncharsel.c` |
| Event init dispatch (801BB128) | Fill match settings from the event descriptor | static `onEnterVs` (0x801BAD70) of Event Mode, `gm/gmevent.c` |
| CSS / SSS for events (801BAA80, 801BAB28) | Choose CSS type, preload CPU | static `onEnterCss` (0x801BAA60) and neighbours, `gm/gmevent.c` |
| Event select screen (8024D92C, ~25 files) | Pages, names, descriptions | `mnEvent_8024D864`, `mn/mnevent.c` |
| Fighter struct size (800679BC) | Extra per-fighter vars | `Fighter_800679B0` / `sizeof(Fighter)` in `ft/fighter.c` |
| State and frame counters (8006AB78, 800693EC) | `TM.state_frame`, `state_prev`, … | `Fighter_procAnim`; motion-state change |
| Per-frame OSD (8006B7F4) | Generic per-frame checks | `Fighter_procInput` |
| Frame advance (8016BBB4, 8016BBD4) | Custom advance button, hold-to-repeat | `gm_AnyControllerPressedZ` |
| Update loop tweaks (801A4B14, 801A4C08, 801A4DF4, 801A4E48, 801A501C) | Pause and frame advance without debug level; force game loop for fast-forward | `gm_SetDbPauseInputHandlers`, `gm_801A4BD4`, `gm_801A4D34` |
| Skip asserts (8006D494, 800D5524, 8007D8E8) | Allow savestate restores | `Fighter_procCollResolve`, `fn_800D54A4`, `ftCommon_8007D7FC` |
| OSD triggers (80099D7C, 8008D770, 8008E52C, ~65 more) | Wavedash timing, L-cancel, SDI, … | `ftCo_80099D70`, `ftCo_LandingAir_EnterWithMsidLag`, `ftCo_Damage_OnEveryHitlag`, … |
| Hitbox display (80080638) | Recolour by ID | `ftDrawCommon_800805C8` |
| Character RNG (8014C780, 80142AE0, …) | Force G&W hammer, misfire, turnips | Each character's file under `ft/kinds/` |
| OSD toggle UI (80235xxx–80236xxx) | Reuses the Rules menu | `fn_80234C24` and neighbours, `mn/` |
| Boot tasks (801B02EC) | Defaults after memory card load | `gm_Scene_MemCard_OnEnter` |

Resolve any other injection with `python tools/mex_symbols.py 0x<address>`.

## Vanilla data TM-CE leans on

| MexTK name | Decomp symbol | Notes |
|-|-|-|
| `stc_hsd_update` (80479D58) | `gm_80479D58` (`struct gm_80479D58_t`, `gm/types.h`) | TM-CE's `onFrame` / `checkPause` / `checkAdvance` slots are inside `unk_10`; fields are mostly unnamed |
| `stc_memcard` (8045A6C0) | `gmMainLib_8045A6C0` | TM-CE stores settings at +0x1F24…0x1F4F in unused save space |
| `stc_match` (8046B6A0) | starts at the `.bss` of the match TU; `symbols.txt` shows a local `controller` label there | Find the real struct through its accessors in `gm/` before use |
| `event_vars` pointer (803D7054) | none (m-ex) | Becomes a normal global |

## Design decisions to settle before porting

1. **Own mode vs. hijacking Event Mode.** Recommended: add `GM_TM` with its own
   `GameModeState` list and menu, and leave Event Mode vanilla. It removes ~45 ASM files of
   event-select and CSS patching from scope, keeps vanilla playable, and gives the AI coach a
   clean entry point ("start drill X with settings Y"). Cost: a new drill-select menu must be
   written instead of reusing the event select screen.
2. **Savestates.** `savestate_v1.c` copies selected `Fighter` sub-structs and rebuilds the rest.
   Port it first as-is, because every event depends on it. A second-generation savestate that
   is rollback-safe is a Slippi requirement (see `slippi-tandem.md`); design the API so the
   implementation can be swapped.
3. **Settings storage.** TM-CE writes into the vanilla save file. A native build can keep that
   layout for save compatibility or use its own save file. Decide before porting the OSD menu.
4. **Legacy ASM events.** 15 events exist only as assembly. Port them last, by rewriting each
   against the C event API using the ASM as the spec.
5. **Assets.** `dats/*.dat` are needed at runtime. They load with `lbArchive_LoadSymbols`; the
   disc image must contain them. Decide the disc-build step (TM-CE uses `gc_fst`).
6. **Licence.** TM-CE and UnclePunch Training Mode show no licence on GitHub; MexTK is MIT.
   Ask the authors before distributing a build that contains ported code.
7. **Slippi compatibility.** Decided: address-preserving overlay (`overlay-build.md`). Every
   hook in the table above becomes a hook-table entry, not a source edit. 42 TM-CE hooks sit
   on Slippi injection sites and 52 share a function with one
   (`tools/tm_slippi_collisions.py`). Most of the 42 are 'Additional Codes' that duplicate
   what Slippi ships; drop those. TM-CE's own savestates
   and local-settings-driven behaviour are not rollback-safe as they are.

## Suggested order

Each step should end with a build that boots.

1. **Toolchain proof.** Experiments 0–7 in `overlay-build.md`, ending with one overlay object
   that draws DevText in a match under Slippi Dolphin, with `overlay_check.py` passing.
2. **Core services** (`src/melee/tm/`): event descriptor types, event GObj lifecycle
   (`EventInit` / `EventLoad` / `EventUpdate`), per-fighter vars on `struct Fighter`, the
   scene and match hooks.
3. **Menu engine** (`menu.c`) and its art (`eventMenu.dat`).
4. **Savestates** (`savestate_v1.c`) with the three skip-assert changes.
5. **One small C event end to end.** `laserland.c` (152 lines) or `fc.c` (222 lines).
6. **Mode entry**: `GM_TM`, drill select, CSS / SSS flow.
7. **Messages, tips, OSD framework**, then OSDs in batches by hooked file.
8. **Remaining C events**, smallest first; `lab.c` last (recording, CPU scripting, info and
   input display, memory-card export).
9. **Frame advance and update-loop changes.**
10. **Legacy ASM events**, then the "Additional Codes" that are still wanted (UCF, unlock all,
    neutral spawns, hitbox colours).

Per-feature recipe: `.claude/skills/port-tm-feature/SKILL.md`.

## Translating MexTK code

| MexTK | Decomp |
|-|-|
| `GOBJ` | `HSD_GObj` |
| `FighterData* fd = gobj->userdata` | `Fighter* fp = GET_FIGHTER(gobj)` |
| `JOBJ`, `COBJ`, `Text` | `HSD_JObj`, `HSD_CObj`, `HSD_Text` |
| `GObj_AddProc` | `HSD_GObj_SetupProc` |
| `GObj_AddGXLink` | `GObj_SetupGXLink` |
| `Fighter_GetGObj(slot)` | `Player_GetEntity(slot)` |
| `Text_AddSubtext`, `Text_SetText` | `HSD_SisLib_803A6B98`, `HSD_SisLib_803A70A0` |
| `Pause_CheckStatus` | `gm_GetDbPauseFlag` |
| `fd->TM.state_frame` | new appended `Fighter` field |
| `calloc(n)` | `HSD_MemAlloc(n)` + `memset` |
| `static X* stc_y = 0x80…` | the decomp global, by symbol |

Field names differ everywhere (MexTK `fd->phys.self_vel` vs decomp `fp->self_vel`). MexTK
headers give offsets; match fields by offset comment in `ft/types.h`, not by name.
