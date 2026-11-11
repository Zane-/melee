---
name: add-native-code
description: Add new native C code to the Melee training build and hook it into vanilla code without breaking the matching build. Use when creating a new source file, adding a hook or callback to a vanilla function, adding a game mode, or appending fields to a vanilla struct.
---

# Add native code

Read `docs/ai/modding.md` for the reasoning. This is the checklist.

The shipping build is an address-preserving overlay (`docs/ai/overlay-build.md`): vanilla code
and data must not move. Put the file under `src/melee/tm/` or `src/melee/ai/`, add hooks to
`config/GALE01/tm_hooks.txt`, and run `python tools/overlay_build.py` (needs a matching build
first). No `configure.py` entry is needed for overlay files. No overlay DOL has been booted
yet. Use `src/melee/tm/tm.c` and `tm_menu.c` as models; state hangs off `tm_state` (per
match, rolled back) or `tm_persist` (session, not rolled back), see `tm.h`.

Hard rules for mod files:

- No writable file-level statics or globals. State goes in a heap-allocated struct reached
  from the mod's root pointer. `const` tables and string literals are fine.
- Call vanilla by symbol. No raw addresses.
- Display and coach code never write simulation state.

## New source file

1. Put it in `src/melee/tm/` (training) or `src/melee/ai/` (coach link). Prefix public
   functions with the file name: `tm_menu.c` → `tmMenu_Open`.
2. Header declares only that file's public symbols. Shared structs go in the module's
   `types.h`, typedefs and enums in `forward.h`.
3. No registration is needed: `tools/overlay_build.py` compiles every `.c` under those two
   directories. Do not touch `configure.py`, `splits.txt` or `symbols.txt`.

Template:

```c
#include "tm_menu.h"

#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjproc.h>

static void tmMenu_Think(HSD_GObj* gobj);

void tmMenu_Open(void)
{
    HSD_GObj* gobj;

    gobj = GObj_Create(HSD_GOBJ_CLASS_UI, 15, 0);
    HSD_GObj_SetupProc(gobj, tmMenu_Think, 17);
}

static void tmMenu_Think(HSD_GObj* gobj) {}
```

Check the include paths and the constants against a neighbouring vanilla file
(`src/melee/if/ifhazard.c` is a good model) before building; the template is a shape, not
verified code.

Compiler rules (Metrowerks C89): declarations at block start, prototypes required, no
designated initialisers or compound literals, float literals `1.0F`.

## Hook into a vanilla function

1. Find the site with the `find-symbol` skill.
2. Check Slippi: `python tools/tm_slippi_collisions.py --function <vanilla function>` and
   `grep -i <address> config/GALE01/slippi_injections.txt`.
   - Same address as Slippi: not allowed. Find another site or drop the hook (Slippi often
     already provides the behaviour).
   - Slippi patches elsewhere in the function: never replace the whole function.
3. Choose the cheapest hook kind that works (`overlay-build.md`, section 3): `pointer` →
   `call` → `function` → `inject` → `word`.
4. Write the mod-side function. For a `call` hook it has the same signature as the function it
   wraps and calls the original itself.
5. Add the hook as a line in `config/GALE01/tm_hooks.txt` (kind, `vanilla_symbol+offset`,
   target, note). The build rejects Slippi conflicts. Never edit the vanilla file.

For a throwaway shifted dev build only, an inline call guarded by `#ifndef MUST_MATCH` works
(`docs/ai/modding.md`). Do not commit it.

## Append to a vanilla struct

1. Append only, inside an overlay-only guard, and guard any `ASSERT_SIZE`.
2. Vanilla objects must still be compiled with the vanilla layout so their code is unchanged;
   only mod files see the new fields. This is unproven until the overlay build exists.
3. The allocation size becomes a `word` patch (for `Fighter`: the size immediate in
   `Fighter_800679B0`). Grep `src/` for the old size as a hex literal to find other copies.
4. Initialise the new fields from a hook, not at `Fighter_Create+0x54` (Slippi patches it).

## Add a game mode

Follow "Adding a mode" in `docs/ai/runtime.md`; copy `src/melee/gm/gmtrainingmode.c`.

## Verify, in this order

1. Matching build still reports the retail SHA (`build-melee` skill). Mandatory after any
   vanilla-file edit.
2. `python tools/overlay_build.py` ends with `OK: vanilla layout preserved`.
3. Boot test if the change is reachable; for anything gameplay-affecting, a two-instance
   Slippi direct-connect session with no desync.

Report exactly which of these ran.
