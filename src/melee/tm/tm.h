#ifndef MELEE_TM_TM_H
#define MELEE_TM_TM_H

#include <Runtime/platform.h>

#include <melee/gm/forward.h>

/**
 * @file
 * Native hooks that run TM-CE (../TrainingMode, linked into the overlay; see
 * docs/ai/tmce-native.md) from vanilla code. Every target here is wired in
 * config/GALE01/tm_hooks.txt; a `call` target has the signature of the
 * vanilla function it wraps and calls it.
 *
 * State: TM-CE keeps its state in statics, which is fine offline. Anything
 * that must survive Slippi rollback (netplay drills) hangs off #tm_state.
 */

/// Absolute symbol from config/GALE01/tm_symbols.txt: 4 spare bytes of
/// vanilla .sbss inside the range Slippi's rollback saves. Root for future
/// rollback-safe state; unused by the TM-CE port.
extern void* tm_state;

/// @name Hook targets (tm.c)
/// @{
void tm_Hook_Boot(void);
void tm_Hook_SceneChange(void);
void tm_Hook_StartMelee(int arg);
/// @}

/// @name Hook targets (tm_fighter.c)
/// @{
struct _HSD_ObjAllocData; // declared here so the prototypes below share it
void tm_Hook_FighterAllocInit(struct _HSD_ObjAllocData* data, size_t size,
                              u32 align);
void* tm_Hook_FighterAlloc(struct _HSD_ObjAllocData* data);
/// @}

/// @name Hook targets (tm_event_start.c)
/// @{
void tm_Hook_EventEnterVs(GameModeState* state);
/// @}

#endif
