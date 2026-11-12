#include "tm.h"

#include "tmce.h"

#include <melee/gm/gmmain_lib.h>
#include <melee/lb/lb_013B.h>
#include <melee/lb/lb_0219.h>

/// Wraps the `gmMainLib_8015FBA4()` call in `main`, after the SDK, HSD, lb
/// and disc layers are up and before the game-mode loop starts.
///
/// Replaces TM-CE's Misc/Load eventMenu.dat.asm (HSD_OSInit+0xAC) and
/// Hooks/OnBoot.asm (bootOnLeave+0x80; TM-CE's OnBoot is empty).
void tm_Hook_Boot(void)
{
    gmMainLib_8015FBA4();
    tmce_Boot();
}

/// Wraps the last call in `gm_801A4BD4`, which runs at the start of every
/// scene after the GObj system and the scene heap have been reset.
///
/// Replaces TM-CE's Hooks/OnSceneChange.asm (gm_801A4BD4+0xC0, three calls
/// earlier: gm_801A3E88, lbAudioAx_8002835C and lb_80014534 now run first).
void tm_Hook_SceneChange(void)
{
    lb_80014534();
    if (tmce_IsLoaded()) {
        OnSceneChange();
    }
}

/// Wraps the `lbBgFlash_Init` call in `fn_8016E730` (match start).
///
/// Replaces TM-CE's Hooks/OnStartMelee.asm, which runs at the instruction
/// after this call.
void tm_Hook_StartMelee(int arg)
{
    lbBgFlash_Init(arg);
    if (tmce_IsLoaded()) {
        OnStartMelee();
    }
}
