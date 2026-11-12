/**
 * @file
 * Port of TM-CE's Misc/HSD_Update Tweak/ files (and Disable USB
 * Screenshot): let the engine's pause / frame-step handlers run in a retail
 * build, so TM-CE events can install their own (lab.c and ledgedash.c set
 * HSD_Update checkPause / checkAdvance), and keep vanilla's debug-only
 * handlers and the debug dump out of them.
 *
 * The one-instruction parts are `word` hooks in config/GALE01/tm_hooks/
 * misc.txt: Always Run Debug Update (gm_801A4D34+0xC0) and Allow Z in VS
 * While Paused (Fighter_procInput+0x3A4).
 */
#include "misc.h"

#include <melee/db/db.h>
#include <melee/gm/gm_1601.h>
#include <melee/gm/gmscene.h>
#include <melee/gm/types.h>
#include <melee/lb/lbheap.h>
#include <sysdolphin/baselib/class.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/initialize.h>
#include <sysdolphin/baselib/leak.h>

/// TM-CE compares the debug level against 3 (DbLKind_DebugRom).
#define TM_MISC_DEBUG_LEVEL 3

/// gm/gmscene.c (statics with unique names).
extern struct gm_80479D58_t gm_80479D58;
extern UNK_T gm_804D6728;
extern void (*gm_804D6724)(void);

/// Replaces gm_SetDbPauseInputHandlers (`function` hook).
///
/// Port of HSD_Update Tweak/Clear HSDUpdate for no Debug Melee.asm
/// (gm_SetDbPauseInputHandlers+0xC): below the debug level, nothing
/// installs the debug pause / frame-step handlers.
void tm_misc_SetDbPauseInputHandlers(Predicate check_db_pause,
                                     Predicate check_db_framestep)
{
    gm_80479D58.unk_10.db_input.check_pause = check_db_pause;
    gm_80479D58.unk_10.db_input.check_framestep = check_db_framestep;
    if (DbLevel < TM_MISC_DEBUG_LEVEL) {
        gm_80479D58.unk_10.db_input.check_pause = NULL;
        gm_80479D58.unk_10.db_input.check_framestep = NULL;
    }
}

/// Wraps the `HSD_GObjSetInitDefaults` call in gm_801A4BD4 (+0x74).
///
/// Port of HSD_Update Tweak/Clear HSDUpdate for no Debug.asm
/// (gm_801A4BD4+0x34). gm_801A4BD4 inlines gm_SetDbPauseInputHandlers, so
/// the function hook above does not cover it; clear the handlers here,
/// a few instructions later (nothing reads them in between).
void tm_misc_SceneSetInitDefaults(HSD_GObjLibInitDataType* data)
{
    HSD_GObjSetInitDefaults(data);
    if (DbLevel < TM_MISC_DEBUG_LEVEL) {
        gm_80479D58.unk_10.db_input.check_pause = NULL;
        gm_80479D58.unk_10.db_input.check_framestep = NULL;
    }
}

/// Replaces gm_801A4970 (`function` hook), the per-frame debug pause /
/// frame-step input check.
///
/// Port of HSD_Update Tweak/Check for DBLevel.asm (gm_801A4970+0x38):
/// below the debug level, skip the D-pad right + X memory dump loop and go
/// straight to the pause / frame-step handlers. Otherwise vanilla.
void tm_misc_DbPauseInput(struct gm_DbPauseInputHandlers* db_input)
{
    HSD_PadStatus* temp_r3;
    int i;

    if (DbLevel >= TM_MISC_DEBUG_LEVEL) {
        for (i = 0; i < PAD_MAX_CONTROLLERS; i++) {
            temp_r3 = &HSD_PadMasterStatus[(u8) i];
            if ((temp_r3->trigger & HSD_PAD_DPADRIGHT) &&
                (temp_r3->button & HSD_PAD_X))
            {
                lbHeap_80015DF8();
                OSReport("[hsdDumpClassStat] -- Report --\n");
                hsdDumpClassStat(NULL, 0, 1);
                OSReport("\n");
                OSReport("[HSD_ObjDumpStat] -- Report --\n");
                HSD_ObjDumpStat();
                OSReport("\n");
                db_PrintEntityCounts();
                db_PrintThreadInfo();
                HSD_Leak_80387DF8(0);
                if (gm_804D6728 != NULL) {
                    gm_801653C8(gm_804D6728);
                    gm_804D6728 = NULL;
                } else {
                    gm_804D6728 = gm_80165388(0x19, 0x3F, 0, 0xFE);
                    if (gm_804D6724 != NULL) {
                        gm_804D6724();
                    }
                }
            }
        }
    }

    if (db_input->check_pause != NULL && db_input->check_pause()) {
        if (gm_GetDbPauseFlag(0)) {
            gm_80479D58.unk_10.x0 &= ~1;
        } else {
            gm_80479D58.unk_10.x0 |= 1;
        }
    }
    if (gm_GetDbPauseFlag(0)) {
        if (db_input->check_framestep != NULL && db_input->check_framestep()) {
            gm_80479D58.unk_10.x2 |= 1;
        }
    }
}
