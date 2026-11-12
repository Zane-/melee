/**
 * @file
 * Ports of TM-CE's Misc injections around matches and scenes:
 *
 * - Better VS Mode Frame Counter/Init Counter.asm, Inc Counter.asm
 * - Allow light press in LRAS.asm
 * - Corneria - Move Ship on Stage Init.asm
 * - Display Stick Info When Paused/ (the vanilla-side half; the text is in
 *   src/tmce/misc_bridge.c)
 * - Display Tweet Message And Version Number.asm (vanilla-side half)
 */
#include "misc.h"

#include <melee/gm/gmscene.h>
#include <melee/gm/gmvs.h>
#include <melee/gr/ground.h>
#include <melee/gr/inlines.h>
#include <melee/gr/types.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/jobj.h>

/* ---- Better VS Mode Frame Counter ------------------------------------ */

int tm_misc_game_frame_counter;

/// Wraps the `gm_SetPreGObjProcCallback` call at match start
/// (fn_8016E730+0x38).
///
/// Port of Init Counter.asm (fn_8016E730+0x14, in the prologue; the calls
/// in between, db_Setup and gm_SetDbPauseInputHandlers, do not read it).
void tm_misc_MatchStartPreGObjProc(Event cb)
{
    gm_SetPreGObjProcCallback(cb);
    tm_misc_game_frame_counter = 0;
}

/// Wraps the `fn_8016CFE0` call in gm_Scene_Vs_OnFrame (+0x58), the VS
/// match frame.
///
/// Port of Inc Counter.asm (fn_8016CFE0+0x330, its epilogue, which every
/// return path reaches): one more frame after each call.
void tm_misc_VsFrame(void)
{
    fn_8016CFE0();
    tm_misc_game_frame_counter++;
}

/* ---- Allow light press in LRAS ---------------------------------------- */

/// TM-CE's analog trigger threshold (Globals.s AnalogTriggerThreshold).
#define TM_MISC_ANALOG_TRIGGER 43

static bool triggerHeld(HSD_PadStatus* pad, u8 analog, u32 digital)
{
    return analog >= TM_MISC_ANALOG_TRIGGER || (pad->button & digital);
}

/// Wraps the second `gm_GetButtonsPressed` call in fn_8016CFE0 (+0x204),
/// the "are all of L+R+A+Start held" half of the paused-match quit check
/// (it runs only once one of them was just pressed).
///
/// Port of Allow light press in LRAS.asm (fn_8016CFE0+0x218): instead of
/// the pauser's digital buttons, any controller holding Start and A with
/// L and R pressed lightly or fully counts. The caller tests
/// `(mask & result) == mask`, so all-ones means yes and 0 means no.
///
/// TM-CE scans six 0x44-byte entries from HSD_PadMasterStatus; there are
/// four pads, so the last two read past the array. Only four are checked.
u64 tm_misc_LrasButtons(u8 slot)
{
    int i;
    (void) slot;
    for (i = 0; i < PAD_MAX_CONTROLLERS; i++) {
        HSD_PadStatus* pad = &HSD_PadMasterStatus[i];
        if ((pad->button & HSD_PAD_START) && (pad->button & HSD_PAD_A) &&
            triggerHeld(pad, pad->analogL, HSD_PAD_L) &&
            triggerHeld(pad, pad->analogR, HSD_PAD_R))
        {
            return ~0ULL;
        }
    }
    return 0;
}

/* ---- Corneria ----------------------------------------------------------- */

/// Wraps the last call in grCorneria_801DD674 (+0x304), Corneria's stage
/// init: `gr->u.corneria.x12C = Ground_801C3FA4(gobj, 8)`.
///
/// Port of Corneria - Move Ship on Stage Init.asm (+0x30C, after that
/// store): update the ship's collision now instead of on its first frame,
/// so TM-CE's spawn-over-ground lookups (savestates, event setup) see the
/// stage where it really is, not inside the blast zone. The store is done
/// here too so the order matches.
HSD_JObj* tm_misc_CorneriaInitShip(HSD_GObj* gobj, int depth)
{
    HSD_JObj* jobj = Ground_801C3FA4(gobj, depth);
    Ground* gr = GET_GROUND(gobj);
    gr->u.corneria.x12C = jobj;
    Ground_UpdateMapColl(gobj);
    return jobj;
}

/* ---- Display Stick Info When Paused ---------------------------------- */

/// Wraps the last call in gm_801A0FEC (+0xF8), which shows the pause
/// screen. Port of Create Text on Pause.asm (+0xFC).
void tm_misc_PauseShow(HSD_JObj* jobj)
{
    HSD_JObjAnimAll(jobj);
    tmce_misc_PauseStickCreate();
}

/// Wraps the last call in gm_801A10FC (+0x24), which hides the pause
/// screen. Port of Remove Text on UnPause.asm (+0x28).
void tm_misc_PauseHide(HSD_JObj* jobj, u32 flags)
{
    HSD_JObjSetFlagsAll(jobj, flags);
    tmce_misc_PauseStickRemove();
}

/* ---- Display Tweet Message And Version Number ------------------------ */

/// Wraps the first `OSReport` call in Exception_ReportStackTrace (+0x28),
/// whose only argument is a fixed string.
///
/// Port of Display Tweet Message And Version Number.asm (+0x24, the
/// instruction before). 0x80394A74, the next instruction, is a Slippi
/// injection; this call is not.
void tm_misc_CrashReport(const char* msg)
{
    tmce_misc_CrashMessage();
    OSReport(msg);
}

/* ---- SearchStringTable ------------------------------------------------ */

/// Port of Misc/SearchStringTable.asm, an m-ex helper (not an injection)
/// that TM-CE's OSD code calls at 0x80005530: the @p id-th string of a
/// block of NUL-terminated strings.
char* tm_misc_SearchStringTable(int id, char* names)
{
    while (id-- > 0) {
        while (*names != '\0') {
            names++;
        }
        names++;
    }
    return names;
}
