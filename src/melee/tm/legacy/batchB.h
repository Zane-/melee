#ifndef MELEE_TM_LEGACY_BATCHB_H
#define MELEE_TM_LEGACY_BATCHB_H

#include <melee/tm/legacy/legacy.h>

/**
 * @file
 * Helpers shared by the batch B legacy events (Ledgetech, LedgetechCounter,
 * SDITraining). They live inside those events' blocks of
 * Custom Event Code - Rewrite.asm rather than in the shared library, and
 * read the event's player registers (r27-r30) implicitly; here those are
 * parameters. Defined in batchB_util.c.
 */

/// asm Ledgetech/LedgetechCounter "Select Side of Stage based on menu
/// option": option 0 of @p menu, 0 random (HSD_Randi(2)), 1 left, 2 right;
/// any other value is random. Returns 0 left, 1 right.
int tm_legacyB_StageSideFromMenu(const u8* menu);

/// asm Ledgetech_InitializePositions (r3 = side 0 left / 1 right; r27-r30
/// the player registers): P2 in Wait 10 Mm behind the ledge, facing away
/// from it; P1 on a rebirth platform 60 Mm out, facing the stage, with a
/// no-op physics callback and the custom RebirthWait interrupt.
void tm_legacyB_Ledgetech_InitializePositions(int side, HSD_GObj* p1,
                                              HSD_GObj* p2);

/// asm Event_EnterGrab (in the SDI Training block; r3 = {P1 X, P1 Y, P2 X,
/// P2 Y}): move both players (and their followers) there, then P2 grabs P1
/// and stands in CatchWait.
void tm_legacyB_EnterGrab(const f32* xy, HSD_GObj* p1, HSD_GObj* p2);

#endif
