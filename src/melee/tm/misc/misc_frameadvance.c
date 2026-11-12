/**
 * @file
 * Port of TM-CE's Misc/Frame Advance Rewrite.asm.
 */
#include "misc.h"

#include <melee/gm/types.h>
#include <sysdolphin/baselib/controller.h>

/// gm/gmscene.c (static with a unique name).
extern struct gm_80479D58_t gm_80479D58;

/// Frames Z has been held, across calls.
static int frame_advance_timer;

/// Replaces gm_AnyControllerPressedZ (`function` hook), the engine's
/// "advance one frame" check while frame-stepping.
///
/// TM-CE: holding Z advances one frame on the first frame it is held and
/// then every frame from the 30th on. The Z press is eaten so the game
/// does not see it. The first pad holding Z decides the result; unlike
/// vanilla, pads with an error are not skipped. Vanilla checked for a Z
/// press (trigger), this checks Z held.
bool tm_misc_AnyControllerPressedZ(void)
{
    int i;
    for (i = 0; i < PAD_MAX_CONTROLLERS; i++) {
        HSD_PadStatus* pad = &HSD_PadMasterStatus[(u8) i];
        if (!(pad->button & HSD_PAD_Z)) {
            continue;
        }
        frame_advance_timer++;
        if (frame_advance_timer == 1 || frame_advance_timer >= 30) {
            pad->button &= ~HSD_PAD_Z;
            pad->trigger &= ~HSD_PAD_Z;
            return true;
        }
        return false;
    }

    /* Z released everywhere: reset, and drop any pending frame-step. */
    frame_advance_timer = 0;
    gm_80479D58.unk_10.x2 &= ~1;
    return false;
}
