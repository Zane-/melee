# Runtime architecture

Names ending in 8 hex digits are not yet named upstream and may be renamed; look them up by
address in `config/GALE01/symbols.txt` if a grep fails. MexTK / community names are given in
*italics* where they help.

## Boot

`main()` is in `src/melee/gm/gmmain.c`. In order it:

1. Initialises the SDK (OS, VI, DVD, PAD, CARD).
2. Sets `DbLevel` from `/develop.ini` and held buttons (`gmMain_8015FDA4`). Debug tools in `db/`
   only run when `DbLevel >= DbLKind_DebugRom`.
3. Calls `HSD_InitComponent` and the `lb` inits (memory, heaps, DVD, ARAM, memory card, snapshots, SIS text).
4. Calls `gm_801A4510()` (*Scene_Main*), which never returns.

## Modes and scenes

Melee has two levels. The community calls them major and minor scenes; the code calls them
game modes and scenes.

| Concept | Struct (`gm/types.h`) | Table | Enum (`gm/forward.h`) |
|-|-|-|-|
| Game mode (major): VS, Training, Event, … | `GameMode` | `modes[]` in `gm/gmscdata.c` | `GameModeKind` (`GM_*`, `GM_TRAINING = 0x1C`, `GM_EVENT = 0x2B`, `GM_COUNT = 0x2D`) |
| One step in a mode's flow (CSS → SSS → match) | `GameModeState` | one `gm_Mode_<X>_States[]` per mode, ended by `id == 0xFF` | — |
| Scene implementation (minor): CSS, SSS, VS match, results | `GameScene` | `scenes[]` in `gm/gmscdata.c` | `GameSceneKind` (`GS_*`, `GS_VS = 2`, `GS_TRAINING = 4`, `GS_CSS = 8`, `GS_SSS = 9`) |

- `GameMode` has `on_load`, `on_unload`, `on_init` and a pointer to its `GameModeState` list.
- `GameModeState` has `id`, `preload`, `on_enter(GameModeState*)`, `on_exit(GameModeState*)` and a
  `GameSceneInfo {scene_kind, enter_data, exit_data}`.
- `GameScene` has `on_frame(void)`, `on_enter(void* enter_data)`, `on_exit(void* exit_data)`.

`gm/gm_1A3F.c` runs the state machine: `gm_801A4510` loops on `runGameMode` → `gm_801A4014`,
which runs the state's `on_enter`, resets the GObj system (`gm_801A4BD4`), calls the scene's
`on_enter`, runs the frame loop, then the `on_exit`s.

Changing mode or step from game code (`gm/gm_1A3F.h`):

- `gm_ChangeGameModeAfterCurrentScene(GM_x)`
- `gm_SetNextGameModeStateId(id)`
- `gm_801A4B60()` ends the current scene.

**All GObjs are destroyed on every scene change.** Anything that must persist across scenes
lives in static data or a persistent heap, not in a GObj.

### Adding a mode

1. Add `GM_<NEW>` before `GM_COUNT` (and a `GS_` value only if no existing scene fits).
2. Add a `GameMode` entry in `modes[]` and write a `GameModeState[]` list. Copy
   `gm/gmtrainingmode.c`: it is the smallest complete example (CSS → SSS → match).
3. Enter it with `gm_ChangeGameModeAfterCurrentScene`.
4. Grep for code indexed by `GameModeKind` before relying on a new value.

In the overlay build the new table entries live in mod data and are wired in with `pointer`
patches rather than by editing `gmscdata.c` (see `overlay-build.md`). The mode and scene
lookups scan the tables for a matching kind, so check how the table end is found before
assuming a slot can be appended.

### Modes that matter for this project

| Mode | Files | Notes |
|-|-|-|
| VS | `gm/gmvs.c` | `gm_Scene_Vs_*`; the match scene most others reuse |
| Vanilla Training | `gm/gmtrainingmode.c`, `gm/gmvs.c` (`gm_Scene_Training_OnEnter` / `OnFrame`), `gm/gm_1884.c` (menu, `TrainingModeState lbl_80473700`) | Shows how a match scene adds a pause menu, CPU control, item spawns and game speed |
| Event | `gm/gmevent.c`, `mn/mnevent.c` | TM-CE hijacks this mode (scene `0x2B`) |
| Debug menu | `gm/gmdebugmode.c`, `if/if_2FF2.c`, `if/textlib.h` | A text-only menu engine already in the game |

## Frame loop

`gm_801A4D34(on_frame, info)` in `gm/gmscene.c`. Per engine frame:

1. Poll pads (`lb_800195D0`, `lb_800198E0`).
2. If `DbLevel` allows, read debug inputs. Decide whether this frame is paused
   (`gm_GetDbPauseFlag`, *Pause_CheckStatus*) and whether frame-advance fires.
3. `gm_EvaluateAllControllerInputs()`, then the scene's `on_frame()`.
4. `pre_gobj_proc()` if set (`gm_SetPreGObjProcCallback`).
5. `HSD_GObj_RunProcs()` — all gameplay happens here.
6. Render (`HSD_GObj_80390FC0`), copy to XFB.

The loop state is `gm_80479D58` (`struct gm_80479D58_t`; MexTK calls it *stc_hsd_update* and
TM-CE installs `onFrame`, `checkPause` and `checkAdvance` callbacks into it).

## GObj system

A `HSD_GObj` (`sysdolphin/baselib/gobj.h`) is an entity with an optional scene-graph object,
user data, per-frame procs and a render callback.

```c
HSD_GObj* gobj = GObj_Create(HSD_GOBJ_CLASS_UI, /*p_link*/ 15, /*priority*/ 0);
GObj_InitUserData(gobj, kind, free_fn, data);            // gobj->user_data
HSD_GObjObject_80390A70(gobj, HSD_GObj_JObjKind, jobj);  // gobj->hsd_obj
HSD_GObj_SetupProc(gobj, think_fn, /*pri*/ 17);          // per-frame, pri <= 0x18 in game
GObj_SetupGXLink(gobj, render_fn, /*gx_link*/ 11, /*prio*/ 0);
```

- Procs run in priority order 0 → max each frame. Fighter procs use: hitlag 0, anim 1, cpu 2,
  input 3, update 4, map collision 6, … attack collision 13, collision resolve 14, camera 18,
  player 22 (`Fighter_Create`, `ft/fighter.c`). Pick a priority relative to those.
- `HSD_GOBJ_CLASS_*` and `HSD_GOBJ_PLINK_*` constants are in each module's `forward.h`
  (fighter class 4 / p_link 8, item 6 / 9, UI 14, text 17, camera 19).
- A small complete HUD example: `if/ifhazard.c`.

## Fighters and players

- `struct Fighter` (`ft/types.h`, ~0x23EC bytes) is the user data of a fighter GObj.
  `Fighter* fp = GET_FIGHTER(gobj);`
- Useful fields: `kind`, `player_idx`, `motion_id` (action state), `facing_dir`, `self_vel`,
  `cur_pos`, `ground_or_air`, `input` (sticks, triggers, held / pressed buttons),
  `coll_data`, hitboxes, `hurt_capsules`, `dmg` (percent, hitlag), `cpu` (`struct CpuFighter`:
  the virtual controller the AI writes), and the per-state callbacks (`input_cb`, `anim_cb`,
  `phys_cb`, `coll_cb`, …).
- Action states: `Fighter_ChangeMotionState`; common state enum `ftCo_MS_*` in
  `ft/kinds/ftCommon/forward.h`; tables in `ft/ftmotionstates.c` and `ft/ftdata.c`.
- Player slots (`pl/player.h`): `Player_GetEntity(slot)` returns the fighter GObj
  (*Fighter_GetGObj*). Also `Player_GetDamage`, `Player_GetStocks`, `Player_GetPadPort`,
  `Player_SetPlayerAndEntityCpuLevel`, ….
- Prefer `ft/ftlib.h` getters (`ftLib_GetPos`, `ftLib_GetMotionId`, …) over poking fields.
- CPU AI: `Fighter_procCpu` → `ftCo_800B3900` in `ft/kinds/ftCommon/ftCo_0A01.c`; attacks in
  `ft/ftcpuattack.c`.
- Hitboxes and hurtboxes: `HitCapsule`, `HurtCapsule`, `FighterHurtCapsule` in `lb/types.h`.

## Input

- Raw: `HSD_PadMasterStatus[4]`, `HSD_PadCopyStatus[4]` (`HSD_PadStatus`, `baselib/controller.h`).
- Game level: `gm_GetButtonsPressed` / `gm_GetButtonsTriggered` (`gm/gm_1A36.h`).
- Per fighter: `fp->input` is filled by the input proc (priority 3) from the pad or from `fp->cpu`.

## Text

Two systems exist:

| System | API | Use for |
|-|-|-|
| SIS text (`baselib/sislib.h`, `HSD_Text`) | `HSD_SisLib_803A611C` (*Text_CreateCanvas*), `HSD_SisLib_803A6754` (*Text_CreateText*), `HSD_SisLib_803A6B98` (*Text_AddSubtext*, printf-style), `HSD_SisLib_803A70A0` (*Text_SetText*), `HSD_SisLib_803A5CC4` (*Text_Destroy*) | Styled menu and HUD text. TM-CE's whole UI uses this |
| DevText (`if/textlib.h`, `if/textdraw.h`) | `DevText_Create`, `DevText_Printf`, `DevText_SetXY`, `DevText_Show`, `DevText_Erase` | Fixed-width debug console text; cheapest way to print something |

A real SIS usage example: `fn_8018A000` in `gm/gm_1884.c`.

## Memory and files

- General allocation: `HSD_MemAlloc` / `HSD_Free` (`baselib/memory.h`). Freed with the scene heap.
- `lb/lbheap.h`: heap kinds Hsd 0, ARAM 1, Seq 2, Stay 3. Use the Stay heap for data that
  must outlive scenes.
- Archives (`.dat` / `.usd`): `lbArchive_LoadArchive`, `lbArchive_LoadSymbols(name, &ptr, "symbol", ..., 0)`
  (`lb/lbarchive.h`); `HSD_ArchiveGetPublicAddress` (`baselib/archive.h`).
- Raw files: `lb/lbfile.h`; preload cache `lb/lbdvd.h`.
- Memory card: `lb/lbcardgame.h`, `lb/lbcardnew.h`, `lb/lbsnap.h`; SDK `libs/dolphin/src/dolphin/card`.
  The save struct is `gmMainLib_8045A6C0` (*stc_memcard*).
- EXI (the port a coach link or Slippi uses): `libs/dolphin/src/dolphin/os/OSExi.c`, header
  `libs/dolphin/include/dolphin/exi.h` (`EXILock`, `EXISelect`, `EXIImm`, `EXIDma`, `EXISync`,
  `EXIDeselect`, `EXIUnlock`).
- RNG: `HSD_Randi`, `HSD_Randf` (`baselib/random.c`). Gameplay determinism depends on every
  client calling these in the same order.
