/**
 * @file
 * TM-CE's hitbox visualizer (Additional Codes/Hitbox Visualizer/).
 *
 * - tm_hitbox_FighterDrawColl replaces ftDrawCommon_800805C8 (`function`
 *   hook), which draws a fighter's hitboxes, hurtboxes and other debug
 *   capsules. It is the decomp's C plus Reverse Hitbox ID Order.asm (+0x4C),
 *   Color Changes Based On Damage.asm (inside lbColl_80009F54, called from
 *   here) and Main.asm (+0x70). Neither site is a call, and the damage
 *   colour needs the hitbox ID, which TM-CE read from the caller's loop
 *   register. The copy keeps calling tm_ac_DrawHurtbox (addcodes, Display
 *   Ungrabbable Hurtboxes) where vanilla has that area's `call` hook (+0x110),
 *   which is dead while this replacement is active.
 * - tm_hitbox_DrawItemHit replaces lbColl_80009F54 (`function` hook) for its
 *   only other caller, item hitbox drawing (it_8026ECE0).
 * - tm_hitbox_ItemTopN and tm_hitbox_DrawSnapping (`call` hooks) are Always
 *   Draw TopN For Items.asm and Display Chain ECBs - GObj 7.asm, in
 *   mpLib_DrawSnapping (the ECB display of "collision" drawing).
 */

#include <melee/ft/kinds/ftPopo/forward.h>

#include <placeholder.h>

#include "hitbox.h"
#include <dolphin/gx/GXGeometry.h>
#include <dolphin/gx/GXStruct.h>
#include <dolphin/gx/GXVert.h>
#include <dolphin/mtx.h>
#include <melee/cm/camera.h>
#include <melee/ft/ft_0C88.h>
#include <melee/ft/ftafterimage.h>
#include <melee/ft/ftcommon.h>
#include <melee/ft/ftdata.h>
#include <melee/ft/ftdrawcommon.h>
#include <melee/ft/ftlib.h>
#include <melee/ft/ftparts.h>
#include <melee/ft/inlines.h>
#include <melee/ft/kinds/ftCommon/ftCo_09F4.h>
#include <melee/ft/kinds/ftCommon/ftCo_0A01.h>
#include <melee/ft/kinds/ftLink/types.h>
#include <melee/ft/kinds/ftPopo/types.h>
#include <melee/it/inlines.h>
#include <melee/it/it_26B1.h>
#include <melee/it/itCharItems.h>
#include <melee/it/itemattrs.h>
#include <melee/it/types.h>
#include <melee/lb/lb_00F9.h>
#include <melee/lb/lb_0146.h>
#include <melee/lb/lbcollision.h>
#include <melee/lb/lbgx.h>
#include <melee/lb/types.h>
#include <melee/mp/mpcoll.h>
#include <melee/mp/mplib.h>
#include <melee/tm/addcodes/addcodes.h>
#include <sysdolphin/baselib/cobj.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/state.h>

/// @name Hitbox colours
/// Color Changes Based On Damage.asm
/// @{

/// Hitbox ID colour used for item hitboxes, see tm_hitbox_DrawItemHit.
#define TM_HITBOX_ID_OTHER 3

/// The lightest shade (all other channels at this value) is for a hitbox of
/// at most 5 damage, the darkest (other channels 0) for 18 or more.
#define TM_HITBOX_SHADE_MAX 180.0F
#define TM_HITBOX_SHADE_DMG_LIGHT 5.0F
#define TM_HITBOX_SHADE_DMG_DARK 18.0F

/// lb/lbcollision.c: vanilla's hitbox colours (statics with unique names).
extern GXColor lbColl_804D36A4; ///< grab hitboxes
extern GXColor lbColl_804D36A8; ///< hitbox outline
extern GXColor lbColl_804D36DC; ///< inert hitboxes

/// Fills @p color for a damaging hitbox: the channel(s) of the ID's hue at
/// 255, the others shaded by damage, alpha 200.
static void tm_hitbox_DamageColor(GXColor* color, float damage, int id)
{
    int shade;

    if (damage >= TM_HITBOX_SHADE_DMG_DARK) {
        shade = 0;
    } else if (damage <= TM_HITBOX_SHADE_DMG_LIGHT) {
        shade = (int) TM_HITBOX_SHADE_MAX;
    } else {
        shade =
            (int) (TM_HITBOX_SHADE_MAX -
                   (damage - TM_HITBOX_SHADE_DMG_LIGHT) *
                       (TM_HITBOX_SHADE_MAX / (TM_HITBOX_SHADE_DMG_DARK -
                                               TM_HITBOX_SHADE_DMG_LIGHT)));
    }

    switch (id) {
    case 0: // red
        color->r = 255;
        color->g = shade;
        color->b = shade;
        break;
    case 1: // green
        color->r = shade;
        color->g = 255;
        color->b = shade;
        break;
    case 2: // blue
        // TM-CE subtracts 10 here and lets it wrap below 0, which turned
        // blue hitboxes of about 17.3 damage or more near white. Clamped.
        shade -= 10;
        if (shade < 0) {
            shade = 0;
        }
        color->r = shade;
        color->g = shade;
        color->b = 255;
        break;
    default: // magenta
        color->r = 255;
        color->g = shade;
        color->b = 255;
        break;
    }
    color->a = 200;
}

/// lbColl_80009F54 (lb/lbcollision.c) with Color Changes Based On
/// Damage.asm (+0x50): a damaging hitbox (not grab, not inert) is coloured
/// by its ID and damage instead of vanilla's red. TM-CE rewrote vanilla's
/// colour static in place; a local is equivalent, as only this function
/// reads it.
static bool tm_hitbox_DrawHit(HitCapsule* hit, u32 arg1, float arg8, int id)
{
    GXColor* var_r5;
    GXColor damage_color;
    float var_f1;
    u32 var_r0;

    if (hit->state != HitCapsule_Disabled && !hit->x43_b2) {
        switch (hit->element) {
        case HitElement_Catch:
            var_r5 = &lbColl_804D36A4;
            break;
        case HitElement_Inert:
            var_r5 = &lbColl_804D36DC;
            break;
        default:
            tm_hitbox_DamageColor(&damage_color, hit->damage, id);
            var_r5 = &damage_color;
            break;
        }

        if (var_r5->a == 0xFF) {
            var_r0 = 0;
        } else {
            var_r0 = 2;
        }
        if (var_r0 == arg1) {
            if (hit->x43_b1) {
                var_f1 = hit->scale;
            } else {
                var_f1 = hit->scale * arg8;
            }
            lbColl_80008FC8(hit->x58, hit->x4C, var_r5, &lbColl_804D36A8,
                            var_f1);
            return 1;
        }
    }
    return 0;
}

/// Replaces lbColl_80009F54 (`function` hook); its only caller now is item
/// hitbox drawing (it_8026ECE0).
///
/// TM-CE picked the colour from r25, which is ftDrawCommon_800805C8's hitbox
/// loop index but, for items, a register of the GObj render loop
/// (HSD_GObj_80390ED0: the high word of the camera's GX link mask, shifted)
/// that is most likely 0. 0 selects the last ("other") branch, magenta, so
/// that is used for every item hitbox. Guess; change TM_HITBOX_ID_OTHER's
/// use here if TM-CE draws item hitboxes in another colour.
bool tm_hitbox_DrawItemHit(HitCapsule* hit, u32 arg1, float scale)
{
    return tm_hitbox_DrawHit(hit, arg1, scale, TM_HITBOX_ID_OTHER);
}

/// @}

/// @name Main.asm: extra spheres for Link and the Ice Climbers
/// @{

static const GXColor tm_hitbox_bubble_color = { 255, 255, 255, 128 };
static const GXColor tm_hitbox_bubble_outline = { 128, 0, 0, 128 };

/// Main.asm's DrawBubble: a sphere of @p radius at @p pos.
static void tm_hitbox_DrawBubble(Vec3* pos, float radius)
{
    lbColl_80008FC8(*pos, *pos, (GXColor*) &tm_hitbox_bubble_color,
                    (GXColor*) &tm_hitbox_bubble_outline, radius);
}

/// Hitbox Visualizer/Main.asm (ftDrawCommon_800805C8+0x70, after the
/// hitboxes): spheres for ranges that are not hitboxes.
///
/// - Link: while his boomerang is returning (item state 3), the radius
///   around him in which it is caught.
/// - Popo: on frame 4 of (air) up special, the radius in which Nana must be
///   for Belay.
///
/// TM-CE's commented-out hookshot and Pikachu thunder cases are not ported.
/// Like TM-CE, the spheres are drawn on every render pass this is called
/// for. Returns whether anything was drawn (TM-CE did not invalidate the GX
/// state cache after drawing these; the copy does, as vanilla does after
/// every capsule).
static bool tm_hitbox_DrawSpecialBubbles(Fighter* fp)
{
    Vec3 pos;

    switch (fp->kind) {
    case Ft_Kind_Link: {
        Item_GObj* boomerang = fp->u.lk.boomerang_gobj;
        Item* ip;
        if (boomerang == NULL) {
            break;
        }
        ip = GET_ITEM(boomerang);
        if (ip->msid != 3) {
            break;
        }
        pos.x = fp->cur_pos.x;
        pos.y = fp->cur_pos.y +
                ((ftLk_DatAttrs*) fp->dat_attrs)->specialhi_pos_y_offset;
        pos.z = fp->cur_pos.z;
        tm_hitbox_DrawBubble(
            &pos,
            ip->xC4_article_data->x4_specialAttributes->link_boomerang.x2C);
        return true;
    }
    case Ft_Kind_Popo:
        if ((fp->motion_id == ftPp_MS_SpecialHiStart_0 ||
             fp->motion_id == ftPp_MS_SpecialAirHiStart_0) &&
            fp->cur_anim_frame == 4.0F)
        {
            tm_hitbox_DrawBubble(
                &fp->cur_pos, ((ftIceClimberAttributes*) fp->dat_attrs)->x7C);
            return true;
        }
        break;
    default:
        break;
    }
    return false;
}

/// @}

/// @name ftDrawCommon_800805C8 copy
/// @{

/// ft/ftdrawcommon.c: item pickup range colours (statics, unique names).
extern U8Vec4 ftDrawCommon_804D3A88;
extern U8Vec4 ftDrawCommon_804D3A8C;
extern U8Vec4 ftDrawCommon_804D3A90;

static const GXColor ftDrawCommon_804D836C = { 0xFF, 0xFF, 0xFF, 0xFE };
static const GXColor ftDrawCommon_804D8370 = { 0xFF, 0xFF, 0xFF, 0xFF };

static inline void mtx_thing_2(MtxPtr mtx, Vec3* v, Vec3* v2)
{
    mtx[0][3] = v->x + v2->x;
    mtx[1][3] = v->y + v2->y;
    mtx[2][3] = v->z + v2->z;
}

static inline MtxPtr ftDrawCommon_8008051C_inline(HSD_GObj* gobj, Vec3* sp54,
                                                  Vec3* v, Mtx sp18, Mtx sp70)

{
    v->x = v->y = v->z = 0.0F;
    sp54->x = sp54->y = sp54->z = 0.0F;
    if (ftLib_GetShakeOffset(gobj, sp54)) {
        HSD_CObj* current = HSD_CObjGetCurrent();
        MtxPtr mtx = current->view_mtx;
        PSMTXIdentity(sp18);
        mtx_thing_2(sp18, sp54, v);
        PSMTXConcat(mtx, sp18, sp70);
        return sp70;
    }
    return NULL;
}

/// Replaces ftDrawCommon_800805C8 (`function` hook). The decomp's C with
/// the marked TM-CE changes.
void tm_hitbox_FighterDrawColl(HSD_GObj* gobj, s32 arg1, bool arg2)
{
    GXColor spAC;
    GXColor spA8;
    int i;

    s32 fighter_2;
    Fighter* fighter;
    u32 phi_r24;
    u32 do_invalidate;
    Mtx sp78;
    Mtx sp18;
    MtxPtr mtx;
    u8 _pad[12];
    Vec3 sp54;
    Vec3 v;
    PAD_STACK(12);

    fighter = GET_FIGHTER(gobj);
    do_invalidate = false;
    if (fighter->x21FC_flag.x0.b6 != 0) {
        // TM-CE: Reverse Hitbox ID Order.asm (+0x4C): draw hitbox 3 first
        // and hitbox 0 last, so ID 0 is on top. Color Changes Based On
        // Damage.asm: each is shaded by its ID and damage.
        for (i = 0; i < ARRAY_SIZE(fighter->x914); i++) {
            int id = ARRAY_SIZE(fighter->x914) - 1 - i;
            if (tm_hitbox_DrawHit(&fighter->x914[id], arg1,
                                  fighter->x34_scale.y, id))
            {
                do_invalidate = true;
            }
        }
        // TM-CE: Hitbox Visualizer/Main.asm (+0x70).
        if (tm_hitbox_DrawSpecialBubbles(fighter)) {
            do_invalidate = true;
        }
        if (fighter->x221D_b6) {
            for (i = 0; i < (unsigned) fighter->hurt_capsules_len; i++) {
                if (lbColl_8000A584(&fighter->hurt_capsules[i].capsule, 1,
                                    arg1, ftCommon_8007F804(fighter),
                                    fighter->cur_pos.z) != 0)
                {
                    do_invalidate = true;
                }
            }
        } else {
            fighter_2 = fighter->x1988;
            if (fighter_2 == 0 && fighter->x198C == 0) {
                for (i = 0; i < (unsigned) fighter->hurt_capsules_len; i++) {
                    // addcodes: Display Ungrabbable Hurtboxes (the `call`
                    // hook vanilla has at +0x110).
                    if (tm_ac_DrawHurtbox(&fighter->hurt_capsules[i].capsule,
                                          arg1, ftCommon_8007F804(fighter),
                                          fighter->cur_pos.z))
                    {
                        do_invalidate = true;
                    }
                }
            } else {
                if (fighter->x198C == 2 || fighter_2 == 2) {
                    phi_r24 = 2;
                } else {
                    phi_r24 = 1;
                }
                for (i = 0; i < (unsigned) fighter->hurt_capsules_len; i++) {
                    if (lbColl_8000A584(
                            &fighter->hurt_capsules[i].capsule, phi_r24, arg1,
                            ftCommon_8007F804(fighter), fighter->cur_pos.z))
                    {
                        do_invalidate = true;
                    }
                }
            }
        }
        if (fighter->reflecting &&
            lbColl_8000A95C(&fighter->reflect_hit, arg1,
                            ftCommon_8007F804(fighter), fighter->cur_pos.z))
        {
            do_invalidate = true;
        }
        if (fighter->x2218_b6 &&
            lbColl_8000AB2C(&fighter->absorb_hit, arg1,
                            ftCommon_8007F804(fighter), fighter->cur_pos.z))
        {
            do_invalidate = true;
        }
        if (fighter->x221B.x221B_b0 &&
            lbColl_8000A78C(&fighter->shield_hit, arg1,
                            ftCommon_8007F804(fighter), fighter->cur_pos.z))
        {
            do_invalidate = true;
        }
    }
    if (fighter->x21FC_flag.x0.b5 != 0) {
        for (i = 0; i < (unsigned) fighter->x166C; i++) {
            if (lbColl_8000A460(&fighter->x1670[i], arg1)) {
                do_invalidate = true;
            }
        }
        for (i = 0; i < (unsigned) fighter->dynamics_num; i++) {
            spAC = ftDrawCommon_804D836C;
            spA8 = ftDrawCommon_804D8370;
            if (lb_800117F4(&fighter->dynamic_bone_sets[i].dyn_desc, &spAC,
                            &spA8, fighter->dynamic_bone_sets[i].bone_id,
                            arg1))
            {
                do_invalidate = true;
            }
        }
    }
    if (fighter->x21FC_flag.x0.b3 && (ftCo_800B395C(gobj, arg1) != 0)) {
        do_invalidate = true;
    }
    if (fighter->x21FC_flag.x0.b4 && fighter->x2223_b5 &&
        lb_80014770(&fighter->dmg.x1930.x0, arg1))
    {
        do_invalidate = true;
    }
    if (fighter->x21FC_flag.x0.b2 != 0) {
        itPickup* temp_r24 = &fighter->x294_itPickup;
        if (fighter->ground_or_air == 0) {
            if (lbGx_8001E2F8(&temp_r24->gr_light_offset, &fighter->cur_pos,
                              &ftDrawCommon_804D3A88, arg1,
                              fighter->facing_dir))
            {
                do_invalidate = true;
            }
            if (lbGx_8001E2F8(&temp_r24->gr_heavy_offset, &fighter->cur_pos,
                              &ftDrawCommon_804D3A90, arg1,
                              fighter->facing_dir))
            {
                do_invalidate = true;
            }
        } else if (lbGx_8001E2F8(&temp_r24->air_light_offset,
                                 &fighter->cur_pos, &ftDrawCommon_804D3A8C,
                                 arg1, fighter->facing_dir))
        {
            do_invalidate = true;
        }
    }
    if (fighter->x21FC_flag.x0.b1 && !fighter->x2227_b2 &&
        lbColl_8000A044(&fighter->x1064_thrownHitbox, arg1,
                        fighter->x34_scale.y))
    {
        do_invalidate = true;
    }
    if (fighter->x21FC_flag.x0.b0 && !fighter->x2229_b4) {
        for (i = 0; i < ARRAY_SIZE(fighter->x1614); i++) {
            if (lbColl_8000A1A8(&fighter->x1614[i], arg1,
                                fighter->x34_scale.y))
            {
                do_invalidate = true;
            }
        }
    }
    if (do_invalidate) {
        HSD_StateInvalidate(-1);
    }

    if (!fighter->x21FC_flag.x0.b7) {
        return;
    }

    if (!fighter->invisible && !fighter->x221E_b5 && arg2) {
        ftParts_800750C8(fighter, 1, 0);
        ftParts_800750C8(fighter, 4, 0);
        if (fighter->is_metal || fighter->x2226_b5 || fighter->x2227_b3) {
            ftParts_800750C8(fighter, 0, 0);
            ftParts_800750C8(fighter, 2, 1);
        } else {
            ftParts_800750C8(fighter, 2, 0);
            ftParts_800750C8(fighter, 0, 1);
        }
        ftCo_8009F5AC(fighter);
        fighter->x2223_b2 = false;
        fighter->x2227_b7 = true;
        fighter->x2228_b0 = false;

        mtx = ftDrawCommon_8008051C_inline(gobj, &sp54, &v, sp18, sp78);

        HSD_JObjDispAll(GET_JOBJ(gobj), mtx, HSD_GObj_80390EB8(arg1), 0);
        if (ftData_UnkMtxFunc0[fighter->kind] != NULL) {
            ftData_UnkMtxFunc0[fighter->kind](gobj, arg1, mtx);
        }
        ftCo_800C8AF0(fighter);
        ftCo_8009F7F8(fighter);
    }
    if (fighter->x20A0_accessory != NULL) {
        HSD_JObjDispAll(fighter->x20A0_accessory, NULL,
                        HSD_GObj_80390EB8(arg1), 0);
    }
    ftCo_800C2600(gobj, arg1);
}

/// @}

/// @name ECB display (mpLib_DrawSnapping)
/// @{

/// The GObj p-link of chain segments (class #HSD_GOBJ_CLASS_ITEMLINK, user
/// data #ItemLink): Link's hookshot, Sheik's chain, Samus' grapple beam, the
/// Ice Climbers' rope, Ness' yo-yo string.
#define TM_HITBOX_PLINK_ITEMLINK 10

/// The cross's colour. TM-CE copied mpLib_DrawEcbs' colour setup without its
/// `mr r3, r0`, so the colour came from whatever r3 held; this is the colour
/// the copied code put at the place r3 pointed to in mpLib_DrawEcbs (its
/// current-ECB orange).
static const GXColor tm_hitbox_topn_color = { 0xFF, 0xA0, 0x30, 0xFF };

/// Wraps the `itGetKind` call in mpLib_DrawSnapping's item loop (+0x2C0),
/// reached for every item with collision.
///
/// Always Draw TopN For Items.asm (+0x2BC): draw a cross at the item's
/// position (its TopN), whether or not its ECB is up to date, and skip
/// vanilla's hookshot ECB (Display Chain ECBs below draws every chain
/// segment instead). Returns a kind that is never It_Kind_Link_HShot, which
/// is how the hookshot case is skipped.
ItemKind tm_hitbox_ItemTopN(Item_GObj* gobj)
{
    Item* ip = GET_ITEM(gobj);

    mpLib_SetupDraw(tm_hitbox_topn_color);
    GXBegin(GX_LINES, GX_VTXFMT0, 4);
    GXPosition3f32(ip->pos.x - 1.0F, ip->pos.y, ip->pos.z);
    GXPosition3f32(1.0F + ip->pos.x, ip->pos.y, ip->pos.z);
    GXPosition3f32(ip->pos.x, ip->pos.y - 1.0F, ip->pos.z);
    GXPosition3f32(ip->pos.x, 1.0F + ip->pos.y, ip->pos.z);
    GXEnd();
    return (ItemKind) -1;
}

/// Wraps the `mpLib_DrawSnapping` call in mpLib_8005A2DC (+0xC).
///
/// Display Chain ECBs - GObj 7.asm (mpLib_DrawSnapping+0x2E8, its end):
/// afterwards, draw the ECB of every chain segment whose collision ran this
/// frame. Uses the GX setup mpLib_DrawSnapping made, as TM-CE does.
void tm_hitbox_DrawSnapping(void)
{
    HSD_GObj* gobj;

    mpLib_DrawSnapping();
    for (gobj = HSD_GObjPLinkHead[TM_HITBOX_PLINK_ITEMLINK]; gobj != NULL;
         gobj = gobj->next)
    {
        ItemLink* link = gobj->user_data;
        // Not in TM-CE; segments always have user data.
        if (link == NULL) {
            continue;
        }
        if (link->coll_data.x38 == mpColl_804D64AC) {
            mpLib_DrawEcbs(&link->coll_data);
        }
    }
}

/// @}
