#ifndef MELEE_TM_MISC_MISC_H
#define MELEE_TM_MISC_MISC_H

#include <Runtime/platform.h>

/**
 * @file
 * Native ports of TM-CE's ASM/training-mode/Misc injections. Hook entries
 * are in config/GALE01/tm_hooks/misc.txt; each names the .asm it replaces.
 */

/// @name src/tmce/misc_bridge.c (MexTK side)
/// @{

/// Index into TM-CE's RNGControl (events.h): which override the Lab menu
/// chose for a piece of character randomness. 0 = vanilla randomness.
enum TmMiscRng {
    TM_MISC_RNG_PEACH_ITEM = 0,
    TM_MISC_RNG_PEACH_FSMASH = 1,
    TM_MISC_RNG_LUIGI_MISFIRE = 2,
    TM_MISC_RNG_GNW_HAMMER = 3,
    TM_MISC_RNG_NANA_THROW = 4,
};

/// Returns event_vars->rng[@p which], or 0 before TM-CE is loaded.
int tmce_misc_GetRng(int which);

/// Port of Misc/Display Stick Info When Paused (Create / Remove).
void tmce_misc_PauseStickCreate(void);
void tmce_misc_PauseStickRemove(void);

/// Port of Misc/Display Tweet Message And Version Number.asm.
void tmce_misc_CrashMessage(void);
/// @}

/// Port of Misc/Better VS Mode Frame Counter: frames of the current VS
/// match scene, counted from match start. TM-CE keeps it at r13-0x49A8
/// (vanilla mnCharSel_804D6CF8, CSS-only data); only TM-CE's legacy
/// assembly events read it.
extern int tm_misc_game_frame_counter;

#endif
