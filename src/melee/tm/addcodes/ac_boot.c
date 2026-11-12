/**
 * @file
 * TM-CE Additional Codes: Boot to Event Mode/, extended to boot straight
 * into the Training Lab (TM_AC_BOOT_TO_LAB in addcodes.h).
 *
 * Boot: TM-CE replaces the load of the boot scene's next mode
 * (bootOnLeave+0x78, a Slippi Online site) with "main menu, or the VS CSS
 * if X is held". Here the call that uses it (+0x7C) is wrapped instead, and
 * left alone when Slippi's boot code is installed at +0x78.
 *
 * Booting into the Lab sets what the event select screen would on confirm
 * (src/melee/tm/ess/ess.c): TM-CE's page in the save data, the event index
 * (gm_801BEB74) and the 1P port (gm_801677E8), then enters GM_EVENT, whose
 * first state is the event's character select. The memory card scene that
 * runs after boot loads the save over the page and index, so they are set
 * again when it exits. Leaving the Lab returns to the event select screen
 * as usual.
 */
#include "addcodes.h"

#include <melee/gm/forward.h>
#include <melee/gm/gm_1601.h>
#include <melee/gm/gm_1A3F.h>
#include <melee/gm/gm_1ADD.h>
#include <melee/gm/gmevent.h>
#include <melee/lb/lbaudio_ax.h>
#include <sysdolphin/baselib/controller.h>

/// src/tmce/addcodes_bridge.c
int tmce_ac_FindEvent(const char* file, int* page, int* event);
void tmce_ac_SetEventPage(int page);

/// gm/gm_1A3F.c state machine (static, unique name); byte 0 is
/// routing.curr_mode.
extern u8 state_machine[];

/// bootOnLeave+0x78: `lbz r3, 4(r31)` (the next mode). Slippi Online's boot
/// code replaces it.
#define AC_BOOTONLEAVE_SITE 0x78
#define AC_VANILLA_BOOTONLEAVE_SITE 0x887F0004

#define AC_PAD_X 0x0400
#define AC_PAD_Y 0x0800

/// Set when booting into the Lab, until the memory card scene has exited.
static bool ac_boot_lab_pending;

static u32 acAnyPadHeld(void)
{
    u32 buttons = 0;
    int i;
    for (i = 0; i < 4; i++) {
        buttons |= HSD_PadMasterStatus[i].button;
    }
    return buttons;
}

/// Select the Lab the way the event select screen does on confirm.
static bool acSelectLab(void)
{
    int page, event;
    if (!tmce_ac_FindEvent("lab", &page, &event)) {
        return false;
    }
    tmce_ac_SetEventPage(page);
    gm_801BEB74(event);
    gm_801677E8(0);
    return true;
}

/// Wraps `gm_ChangeGameModeAfterCurrentScene(scene_data->mode_id)` in
/// bootOnLeave (+0x7C).
///
/// Boot to Event Mode/Boot to Main Menu Or CSS.asm: X held boots to the VS
/// CSS (with TM-CE's menu sound), otherwise to the main menu. With
/// TM_AC_BOOT_TO_LAB the default is the Lab instead; Y held goes to the
/// main menu.
void tm_ac_BootChangeMode(u8 mode)
{
    extern void bootOnLeave(void);
    u32 site = *(u32*) ((u8*) bootOnLeave + AC_BOOTONLEAVE_SITE);
    u32 held;

    if (site != AC_VANILLA_BOOTONLEAVE_SITE) {
        /* Slippi's boot code chose the mode. */
        gm_ChangeGameModeAfterCurrentScene(mode);
        return;
    }

    held = acAnyPadHeld();
    if (held & AC_PAD_X) {
        lbAudioAx_80024030(1);
        mode = GM_VS;
    } else if (TM_AC_BOOT_TO_LAB && !(held & AC_PAD_Y) && acSelectLab()) {
        ac_boot_lab_pending = true;
        mode = GM_EVENT;
    } else {
        mode = GM_MENU;
    }
    gm_ChangeGameModeAfterCurrentScene(mode);
}

/// Wraps `gm_801AE848(0)` in gm_Scene_MemCard_OnExit (+0x30): the save has
/// been loaded by now, so select the Lab again if booting into it.
void tm_ac_MemCardExit(int arg0)
{
    gm_801AE848(arg0);
    if (ac_boot_lab_pending) {
        ac_boot_lab_pending = false;
        acSelectLab();
    }
}

/// Wraps `gm_801ADDD8()` in gm_Scene_MemCard_OnEnter (+0x74).
///
/// Boot to Event Mode/Main Menu Starts at Event Mode.asm (+0x78): make
/// Event Match the current (soon previous) mode, so the main menu opens with
/// its cursor on Event Match.
void tm_ac_MemCardEnter(void)
{
    gm_801ADDD8();
    state_machine[0] = GM_EVENT;
}
