# Codebase map

## Source trees

| Path | What |
|-|-|
| `src/melee/` | The game (913 `.c`, 969 `.h`) |
| `src/sysdolphin/baselib/` | HAL's engine "HSD": scene graph, GObjs, pads, text, archives, particles |
| `libs/dolphin/` | Dolphin SDK: `src/dolphin/{os,pad,card,dvd,gx,vi,ai,ar,ax,mtx,thp,...}`, headers in `include/dolphin/` |
| `src/MSL`, `src/Runtime`, `src/MetroTRK` | C library, compiler runtime, debugger stub |
| `libs/doldecomp/include/` | `placeholder.h` (`UNK_T`, `PAD_STACK`), decomp macros |
| `config/GALE01/` | `symbols.txt` (address ↔ name), `splits.txt` (file ↔ address ranges), `config.yml`, `build.sha1` |
| `configure.py` | The object list and compiler flags. Every `.c` that links is listed here |
| `tools/` | Build generator and decomp tooling (see bottom) |
| `build/` | Generated: objects, `main.dol`, `main.elf`, split asm of the original under `build/GALE01/asm` |

## `src/melee` modules

| Dir | Files | Owns | Start with |
|-|-|-|-|
| `gm` | 167 | Game modes, scenes, match rules, results, save data | `gmmain.c` (`main`), `gm_1A3F.c` (mode state machine), `gmscene.c` (frame loop), `gmscdata.c` (mode and scene tables), `gmvs.c`, `gmevent.c`, `gmtrainingmode.c`, `gm_1884.c` (vanilla training menu) |
| `ft` | 917 | Fighters | `fighter.c` (create, per-frame procs), `types.h` (`struct Fighter`), `ftlib.h` (getters), `ftcoll.c`, `ftcommon.c`, `ftmotionstates.c`, `kinds/ftCommon/` (274 shared action-state files), `kinds/ft<Name>/` per character |
| `it` | 379 | Items and projectiles | `item.c`, `itcoll.c`, `kinds/` |
| `gr` | 157 | Stages | `ground.c`, `grlib.c`, `stage.h`, `gr<stage>.c` |
| `lb` | 68 | Library layer over HSD and the SDK | `lbheap`, `lbmemory`, `lbarchive`, `lbfile`, `lbdvd`, `lbcardgame`, `lbcardnew`, `lbsnap`, `lbcollision`, `lbaudio_ax`, `lbvector`; `types.h` has `HitCapsule` / `HurtCapsule` |
| `mn` | 54 | Menus | `mnmain.c`, `mncharsel.c` (CSS), `mnstagesel.c` (SSS), `mnevent.c` (event select) |
| `if` | 38 | HUD and debug text | `ifall.c`, `ifstatus.c` (percent), `ifstock.c`, `iftime.c`, `textlib.c` / `textdraw.c` (DevText), `if_2FF2.c` (debug menu engine) |
| `pl` | 18 | Player slots (stocks, percent, stale moves, bonuses) | `player.h` (`StaticPlayer`, `Player_*`), `plstale.c` |
| `mp` | 8 | Stage collision | `mpcoll.c`, `mplib.c` |
| `cm` | 6 | Camera | `camera.c` |
| `ef` | 13 | Effects | `efsync.c`, `eflib.c` |
| `db` | 14 | Developer debug tools (run when `DbLevel >= DbLKind_DebugRom`) | `dbinit.c`, `dbitem.c`, `dbcamera.c`, `dbcpu.c`, `dbscreenshot.c`, `dberror.c` |
| `vi` | 26 | Cutscenes | `vi0102.c` … |
| `ty` | 11 | Trophies | `toy.c` |
| `sfx` | 4 | Crowd sounds | `crowdsfx.c` |
| `sc` | 2 | Scene-model types only | `types.h` |

## `src/sysdolphin/baselib` (HSD)

- GObj system: `gobj.c/h`, `gobjproc`, `gobjgxlink`, `gobjplink`, `gobjobject`, `gobjuserdata`.
- Scene graph: `jobj` (joints), `dobj`, `mobj`, `tobj`, `pobj`, `aobj` / `fobj` (animation), `lobj` (lights), `cobj` (cameras).
- Input: `controller.c/h` (`HSD_PadStatus`, `HSD_PadMasterStatus[4]`, `HSD_PadCopyStatus[4]`).
- Memory: `memory.c` (`HSD_MemAlloc`, `HSD_Free`), `objalloc.c` (pool allocator).
- Data and text: `archive.c` (`.dat` parsing), `sislib.c` (menu text), `sislib_font.c`.
- Other: `random.c` (`HSD_Randi`, `HSD_Randf`), `particle`, `generator`, `video`, `initialize`, `debug` (asserts), `devcom` (async DVD/ARAM).

## Naming conventions

| Pattern | Meaning |
|-|-|
| `lbArchive_LoadArchive`, `Player_GetDamage` | Understood. File prefix + `UpperCamel` |
| `gm_801A4510`, `ftCo_800B3900`, `HSD_SisLib_803A70A0` | Matched, module known, purpose not named. The hex is the vanilla address |
| `fn_80xxxxxx` | Unnamed, usually static or a callback |
| `un_80xxxxxx` | Unnamed and module unknown (mostly `if/`, `vi/`) |
| `lbl_80xxxxxx`, `gm_804xxxxx` | Unnamed data |
| `x<hex>`, `x<hex>_<bit>` struct fields | Field at that offset, purpose unknown |
| `ft_0763.c`, `gm_1601.c`, `ftCo_0A01.c` | File named after the top hex digits of its start address |
| `ftFx_`, `ftKb_`, `ftCo_` | Character prefixes are short (Fox, Kirby, Common); directories use long names |

Per-module header roles:

- `types.h`: struct and union bodies only.
- `forward.h`: typedefs, enums, `#define` constants, `HSD_GOBJ_CLASS_*` / `HSD_GOBJ_PLINK_*`.
- `inlines.h`: shared inline functions.
- `<file>.h`: exactly the symbols of `<file>.c`, in address order.

Prototype comments such as `/* 1A4510 */` are the address minus `0x80000000`. Some are stale;
`config/GALE01/symbols.txt` wins.

## Scale of the naming gap

- 19,827 functions in `symbols.txt`; 9,267 still have an address in their name.
- Largest unnamed groups: `it_` 1,766, `ftCo_` 1,682, `fn_` 1,215, `gm_` 806, `HSD_` 676.
- Of the 256 vanilla functions Training Mode calls, 110 are still address-named here.
  `tools/mex_symbols.py` gives the community (MexTK) name for those.

## Tools

| Tool | Purpose |
|-|-|
| `configure.py` + `tools/project.py` | Generate `build.ninja`, `objdiff.json`, `compile_commands.json` |
| `tools/download_tool.py` | Fetch dtk, objdiff-cli, compilers, sjiswrap into `build/` |
| `tools/mex_symbols.py` | MexTK name or address → decomp symbol (added for this fork) |
| `tools/decomp.py`, `tools/m2ctx/`, `tools/decompctx.py` | m2c decompile and decomp.me context (matching work) |
| `tools/check/` | Style checks run by pre-commit |
| `tools/replace-symbols/`, `tools/functions.sh` | Mass renames |
| `tools/dat-cli/`, `tools/table-typer/` | Type `.dat` archives and function tables |
| `tools/dep_graph.py` | Object dependency graph |

ninja targets beyond the default: `progress`, `diff`, `apply`.
