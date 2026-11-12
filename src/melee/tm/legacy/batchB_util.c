/**
 * @file
 * Batch B legacy event helpers: Ledgetech's stage side selection and
 * Ledgetech_InitializePositions (asm lines 3360-3480, also used by
 * LedgetechCounter) and SDI Training's Event_EnterGrab (lines 1477-1540).
 * See batchB.h.
 */
#include "batchB.h"

#include <melee/ft/ft_081B.h>
#include <melee/ft/ft_0892.h>
#include <melee/ft/ftcommon.h>
#include <melee/ft/types.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>

/// Vanilla functions by TM-CE name (Globals.s); statics resolve by address.
void ftCo_800D4FF4(HSD_GObj* gobj); ///< AS_Rebirth
void ftCo_800D5600(HSD_GObj* gobj); ///< AS_RebirthWait
void fn_800D54A4(HSD_GObj* gobj);   ///< RebirthPlatform_UpdatePosition
void fn_800D9CE8(HSD_GObj* gobj);   ///< AS_GrabOpponent
void fn_800DAADC(HSD_GObj* gobj, HSD_GObj* grabber); ///< AS_Grabbed
void fn_800DA1D8(HSD_GObj* gobj);   ///< AS_CatchWait

int tm_legacyB_StageSideFromMenu(const u8* menu)
{
    switch (LG_MENU_OPTION(menu, 0)) {
    case 1:
        return 0;
    case 2:
        return 1;
    default:
        return HSD_Randi(2);
    }
}

/// asm BlrFunctionPointer: an empty physics callback.
static void BlrFunctionPointer(HSD_GObj* gobj) {}

void tm_legacyB_Ledgetech_InitializePositions(int side, HSD_GObj* p1,
                                              HSD_GObj* p2)
{
    u8* p1d = p1->user_data;
    u8* p2d = p2->user_data;
    Vec3 ledge;
    f32 gx, gy;
    int ground;
    u32 facing;

    /* face each other across the ledge */
    if (side == 0) {
        LG_F32(p1d, LG_FT_FACING) = 1.0F;
        LG_F32(p2d, LG_FT_FACING) = -1.0F;
    } else {
        LG_F32(p1d, LG_FT_FACING) = -1.0F;
        LG_F32(p2d, LG_FT_FACING) = 1.0F;
    }
    tm_legacy_GetLedgeCoordinates(side, &ledge);

    /* P2 a few Mm behind the ledge, on the ground under it */
    LG_F32(p2d, LG_FT_POS_X) = ledge.x - 10.0F * LG_F32(p2d, LG_FT_FACING);
    LG_F32(p2d, LG_FT_POS_Y) = ledge.y;
    if (tm_legacy_FindGroundNearPlayer(p2, 0.0F, 0.0F, &gx, &gy, &ground)) {
        LG_F32(p2d, LG_FT_POS_X) = gx;
        LG_F32(p2d, LG_FT_POS_Y) = gy;
        LG_S32(p2d, LG_FT_GROUND_ID) = ground;
    }
    ft_8008A2BC(p2); /* AS_Wait */
    tm_legacy_UpdatePosition(p2);
    ft_80084280(p2); /* ECB for the ground line */
    ftCommon_8007D6A4((Fighter*) p2d); /* grounded */
    tm_legacy_UpdateCameraBox(p2);

    /* P1 on a rebirth platform out in front (Rebirth resets the facing) */
    facing = LG_U32(p1d, LG_FT_FACING);
    ftCo_800D4FF4(p1);
    LG_U32(p1d, LG_FT_FACING) = facing;
    LG_F32(p1d, LG_FT_POS_X) = ledge.x - 60.0F * LG_F32(p1d, LG_FT_FACING);
    LG_F32(p1d, LG_FT_POS_Y) = ledge.y;
    ftCo_800D5600(p1); /* AS_RebirthWait */
    tm_legacy_UpdatePosition(p1);
    LG_PTR(p1d, 0x21A4) = (void*) BlrFunctionPointer; /* physics */
    LG_PTR(p1d, 0x219C) = (void*) tm_legacy_Custom_InterruptRebirthWait;
    fn_800D54A4(p1); /* move the platform with P1 */
    tm_legacy_UpdateCameraBox(p1);
}

/// Move @p gobj (and its follower) to (x, y).
static void MoveWithFollower(HSD_GObj* gobj, f32 x, f32 y)
{
    u8* fp = gobj->user_data;
    Fighter* sub_fp;
    HSD_GObj* sub;

    LG_F32(fp, LG_FT_POS_X) = x;
    LG_F32(fp, LG_FT_POS_Y) = y;
    tm_legacy_UpdatePosition(gobj);
    sub = tm_legacy_CheckIfPlayerHasAFollower(gobj, &sub_fp);
    if (sub != NULL) {
        /* the asm stores through r5, which CheckIfPlayerHasAFollower does
         * not return (its r4 is the follower); the follower is meant */
        LG_F32(sub_fp, LG_FT_POS_X) = x;
        LG_F32(sub_fp, LG_FT_POS_Y) = y;
        tm_legacy_UpdatePosition(sub);
    }
}

void tm_legacyB_EnterGrab(const f32* xy, HSD_GObj* p1, HSD_GObj* p2)
{
    u8* p2d = p2->user_data;

    MoveWithFollower(p1, xy[0], xy[1]);
    MoveWithFollower(p2, xy[2], xy[3]);

    LG_PTR(p2d, 0x1A58) = p1; /* P2's grab victim */
    fn_800D9CE8(p2);          /* P2: Catch */
    fn_800DAADC(p1, p2);      /* P1: CapturePulled, by P2 */
    fn_800DA1D8(p2);          /* P2: CatchWait */
    ftCommon_8007D7FC((Fighter*) p2d); /* grounded */
    LG_PTR(p2d, 0x60C) = NULL; /* drop the GFX pointer that crashes */
}
