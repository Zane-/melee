/**
 * @file
 * TM-CE Additional Codes that change debug drawing: Display Ungrabbable
 * Hurtboxes/ and Collision Link Draw Order Fix [Punkline]/.
 */
#include "addcodes.h"

#include <dolphin/gx.h>
#include <dolphin/mtx.h>
#include <melee/cm/camera.h>
#include <melee/lb/forward.h>
#include <melee/lb/lb_00B0.h>
#include <melee/lb/lbcollision.h>
#include <melee/lb/types.h>
#include <melee/mp/mplib.h>
#include <sysdolphin/baselib/jobj.h>
#include <sysdolphin/baselib/mtx.h>

/// lb/lbcollision.c: the hurtbox colour table (static, unique name).
extern struct {
    GXColor* pad;
    GXColor* pad_x;
} lbColl_803B9928[];

/// Display Ungrabbable Hurtboxes/Main.asm: the colour for a vulnerable
/// hurtbox that cannot be grabbed (translucent, so it is drawn in the
/// translucent pass).
static GXColor ac_ungrabbable_color = { 0xAB, 0x27, 0xFF, 0x80 };

/// Stands in for the `lbColl_8000A244` call that draws a fighter's
/// hurtboxes. ftDrawCommon_800805C8 is replaced by the hitbox area's copy
/// (src/melee/tm/hitbox/hb_draw.c), which calls this at that point.
///
/// Display Ungrabbable Hurtboxes/Main.asm (lbColl_8000A244+0x40): a
/// vulnerable (state 0) hurtbox that is not grabbable is drawn purple.
/// TM-CE patched lbColl_8000A244 itself and read "grabbable" at +0x48 for
/// every caller, which for item hurtboxes (itdraw.c) is the next capsule's
/// state; here only fighter hurtboxes are affected. The body is vanilla
/// lbColl_8000A244 with the colour swap and lbColl_DrawHitResult inlined.
bool tm_ac_DrawHurtbox(HurtCapsule* hurt, u32 arg1, Mtx arg2, float arg3)
{
    Mtx sp9C;
    Vec3 sp90;
    Vec3 sp84;
    Vec3 a;
    Vec3 b;
    Mtx inv;
    float temp_f31;
    MtxPtr var_r28;
    GXColor* temp_r31_2;
    u32 var_r0;
    GXColor* temp_r3;

    temp_r3 = lbColl_803B9928[hurt->state].pad;
    if (hurt->state == 0 && !((FighterHurtCapsule*) hurt)->is_grabbable) {
        temp_r3 = &ac_ungrabbable_color;
    }
    if (temp_r3->a == 0xFF) {
        var_r0 = 0;
    } else {
        var_r0 = 2;
    }
    if (var_r0 == arg1) {
        if (!hurt->skip_update_pos) {
            lb_8000B1CC(hurt->bone, &hurt->a_offset, &hurt->a_pos);
            lb_8000B1CC(hurt->bone, &hurt->b_offset, &hurt->b_pos);
            if (arg2 != NULL) {
                hurt->b_pos.z = arg3;
                hurt->a_pos.z = arg3;
            }
            hurt->skip_update_pos = 1;
        }
        if (arg2 != NULL) {
            PSMTXConcat(arg2, HSD_JObjGetMtxPtr(hurt->bone), sp9C);
        }
        temp_f31 = hurt->scale;
        temp_r31_2 = lbColl_803B9928[hurt->state].pad_x;
        sp84 = hurt->b_pos;
        sp90 = hurt->a_pos;
        if (arg2 != NULL) {
            var_r28 = sp9C;
        } else {
            var_r28 = HSD_JObjGetMtxPtr(hurt->bone);
        }
        HSD_MtxInverse(var_r28, inv);
        PSMTXMultVec(inv, &sp90, &a);
        PSMTXMultVec(inv, &sp84, &b);
        lbColl_800096B4(var_r28, a, b, temp_r3, temp_r31_2, temp_f31);
        return true;
    }
    return false;
}

/// Wraps `Camera_800310A0(2)` in fn_800301D0 (+0xB4).
///
/// Collision Link Draw Order Fix/New Draw Location.asm (+0xB8): draw the
/// collision links (when shown) here, before the players, instead of after
/// post-processing. The original call is removed by a `word` hook
/// (Remove Original Draw.asm, mpLib_8005A2DC+0x10).
void tm_ac_DrawCollisionLinks(u8 arg0)
{
    Camera_800310A0(arg0);
    if (Camera_80030A78()) {
        mpLib_80059E60();
    }
}
