# Adding native code

Status: this workflow follows the upstream README's "Modding" section and the build scripts.
It has **not yet been exercised end-to-end on this machine** (the compiler could not run when
this was written). Update this line once a mod object has linked and booted.

**Scope: shifted dev builds only.** The project's shipping architecture is the
address-preserving overlay (`overlay-build.md`). The inline-hook workflow below moves vanilla
addresses, so a build made this way cannot use Slippi netplay. Use it for throwaway
experiments and debugging. "Add a translation unit" and the compiler notes apply to overlay
mod files too.

Rules that hold in every build:

- Keep mutable mod state in heap allocations (`HSD_MemAlloc`), reached through one pointer,
  not in file-level statics.
- Keep every hook a single call into a mod function.
- Never let display or coach code write simulation state.
- Do not commit inline hooks in vanilla files.

## Principles

1. **Mod code is additive.** New translation units go in `src/melee/tm/` (training mode) and
   `src/melee/ai/` (coach link). They are `Equivalent` objects, so they are compiled and linked
   only in `--non-matching` builds.
2. **Vanilla files change as little as possible.** A hook is one guarded call. Logic lives in
   the mod file. This keeps upstream merges small (upstream renames things constantly) and keeps
   the matching build byte-identical.
3. **The matching build is the safety net.** If the default build still reports the retail
   SHA-1, vanilla behaviour is provably untouched when hooks are compiled out.
4. **No raw addresses.** Call functions and reference globals by symbol. If a global has no
   declaration yet, add an `extern` in the right header instead of casting a literal.

## Add a translation unit

1. Create `src/melee/tm/tm_example.c` and `tm_example.h`.
2. Register it in `configure.py`, in `config.libs`, after the last `MeleeLib` (the `sfx` one):
   ```py
   MeleeLib(
       "tm (Training Mode)",
       [
           Object(Equivalent, "melee/tm/tm_example.c"),
       ],
   ),
   ```
   `Equivalent` evaluates to `True` only with `--non-matching`. In non-matching mode the link
   order comes from `configure.py` order.
3. Reconfigure and build:
   ```sh
   python configure.py --wrapper tools/wibo_macos_wrapper.py --non-matching --map
   ninja
   ```
4. New files do not need entries in `splits.txt` or `symbols.txt`; those describe the retail DOL.

Compiler notes for new code:

- The compiler is Metrowerks C for PowerPC, version GC/1.2.5n: C89 with extensions.
  Declare variables at the top of a block. No designated initialisers, no compound literals,
  no `//`-incompatible issues (`//` comments are fine).
- `-requireprotos` is on: every function needs a prototype in scope, and file-local functions
  must be `static`.
- `int` is 32-bit, enums are `int` (`-enum int`), `bool` is the project typedef.
- Use the project's `u8`/`s16`/`u32`/`f32` types (`<platform.h>`).
- Strings are pooled (`-str reuse`); do not write to string literals.

## Hook vanilla code

```c
// in a vanilla .c file
#ifndef MUST_MATCH
#include "tm/tm_hooks.h"
#endif

void gm_801A4BD4(void)
{
    ...
#ifndef MUST_MATCH
    tm_OnSceneChange();
#endif
}
```

- `MUST_MATCH` is defined by `configure.py` exactly when the build is *not* `--non-matching`.
- Put the hook where the TM-CE injection address points; `tools/mex_symbols.py 0x<addr>` gives
  the function and the offset inside it. Then read the split asm for that function under
  `build/GALE01/asm/` to find the matching C statement.
- Prefer existing extension points over new hooks:
  - `gm_SetPreGObjProcCallback(cb)`: a per-frame callback before GObj procs.
  - A GObj with `HSD_GObj_SetupProc`: per-frame logic at a chosen priority.
  - `GameMode` / `GameModeState` / `GameScene` tables: new modes without touching existing ones.
  - Fighter per-state callbacks (`fp->input_cb`, `take_dmg_cb`, …).

## Grow a vanilla struct

```c
struct Fighter {
    ...
#ifndef MUST_MATCH
    /* fp+23EC */ struct TmFighterVars tm; ///< training-mode per-fighter data
#endif
};
```

Before growing a struct, check:

- `ASSERT_SIZE(struct X, ...)` after it. Guard the assert too.
- How it is allocated. `Fighter` uses `HSD_ObjAllocInit(&fighter_alloc_data, sizeof(Fighter), 4)`
  in `ft/fighter.c`, so it grows safely. A struct embedded in another struct, saved to the
  memory card, or copied with a hardcoded size does not.
- Only append. Inserting shifts offsets that data files and savestates may depend on.

## Change vanilla behaviour

When a TM-CE code changes what the game does (not just observes it), write both paths:

```c
#ifdef MUST_MATCH
    original_statement();
#else
    if (tm_IsEnabled(TM_OPT_X)) {
        new_behaviour();
    } else {
        original_statement();
    }
#endif
```

Keep vanilla behaviour reachable at runtime where practical. A build that can still play a
normal match identically is required for Slippi determinism checks and makes regressions easy
to bisect.

## Verify

| Check | Command | Proves |
|-|-|-|
| Matching build | `python configure.py --wrapper tools/wibo_macos_wrapper.py && ninja` | Hooks compile out; vanilla untouched |
| Training build links | `python configure.py --wrapper tools/wibo_macos_wrapper.py --non-matching --map && ninja` | Mod code compiles and links |
| Boots | Copy `build/GALE01/main.dol` into a full disc extract's `sys/` and open it in Dolphin | It runs |

Always switch back to the mode you were asked to leave the tree in, and say which checks ran.
