/**
 * @file
 * TM-CE Combo Counter (osdmisc area): Onscreen Display/Combo Counter/ and
 * its Better Combo Counter/ changes to vanilla's combo statistics.
 *
 * | TM-CE file | Here |
 * |-|-|
 * | Combo Counter - On Combo Increment.asm (pl_80040ED4+0xD0) | tm_osdmisc_ComboStat, after the call |
 * | Pummels and Multi-Hits Increment Total Damage But Not Combo Counter.asm (pl_80040ED4+0x30) | tm_osdmisc_ComboStat, before the call |
 * | Skip Original Combo End Check.asm (Fighter_procAnim+0x7E4) | `word` hook |
 * | Custom Function Blrl + Keep Combo Counter Going For Missed Techs+Getups.asm (Fighter_procAnim+0x828) | procAnim, installed by tm_osdmisc_SetupProcAnim |
 * | Keep Combo Counter Going For Missed Techs+Getups.asm (Fighter_procAnim+0x7E8) | not ported: unreachable in TM-CE (Skip Original Combo End Check branches over it) |
 * | Disregard Projectile Hitboxes w Same Move ID.asm (ftColl_80078998+0x48) | tm_osdmisc_ItemHitStats |
 * | Interrupting Move with Same Move Gives a Unique ID.asm (ft_800895E0+0x30) | tm_osdmisc_SetAttackInstance |
 * | Throw Hitboxes Update Variable in Playerblock.asm (ftCo_800DDDE4+0x84) | tm_osdmisc_ThrowHit |
 * | Disregard Throw Hitboxes.asm.bak | not ported: not built by TM-CE (.bak) |
 */
#include "osdmisc.h"

#include "../osdcore/osd.h"

#include <melee/ft/fighter.h>
#include <melee/ft/ft_0892.h>
#include <melee/ft/ftcoll.h>
#include <melee/ft/ftlib.h>
#include <melee/ft/types.h>
#include <melee/it/it_26B1.h>
#include <melee/it/types.h>
#include <melee/pl/pl_040D.h>
#include <melee/pl/plattack.h>
#include <melee/pl/player.h>
#include <melee/pl/plbonuslib.h>
#include <melee/pl/plstale.h>
#include <melee/pl/types.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjproc.h>

/// Message kind of the combo message. TM-CE writes `mr r3, 13`, which
/// assembles as "copy r13" (the small-data base), so its kind is a value
/// no other OSD uses; only equality matters (Message_Add replaces a
/// message of the same kind). Any such value behaves the same.
#define TM_OSDMISC_COMBO_KIND 0x10000

/// Move ID that vanilla pl_80040ED4 does not count as a combo hit.
#define TM_MOVE_NO_COMBO 76

/// TM-CE motion state numbers (Globals.s ASID_*).
enum {
    TM_AS_LANDING = 0x2A,
    TM_AS_DOWNBOUNDU = 0xB7,
    TM_AS_PASSIVESTANDB = 0xC9,
    TM_AS_CATCH_FIRST = 0xDF,
    TM_AS_CATCH_LAST = 0xE8,
    TM_AS_THROW_FIRST = 0xEF,
    TM_AS_THROW_LAST = 0xF3,
    TM_AS_MISSFOOT = 0xFB,
    TM_AS_SPECIALTHROW_FIRST = 0x10A,
    TM_AS_SPECIALTHROW_LAST = 0x130,
};

/* ---- combo end ---------------------------------------------------------- */

/// The combo continues while in hitstun, missfoot, landing before its IASA,
/// a missed tech, tech, getup or getup attack, a grab or a throw (TM-CE's
/// replacement for vanilla's "not in hitstun" check).
static bool comboContinues(Fighter* fp)
{
    int state;

    if (fp->x221C_b6) {
        return true;
    }
    state = fp->motion_id;
    if (state == TM_AS_MISSFOOT) {
        return true;
    }
    if (state == TM_AS_LANDING &&
        fp->cur_anim_frame < fp->co_attrs.normal_landing_lag)
    {
        return true;
    }
    if (state >= TM_AS_DOWNBOUNDU && state <= TM_AS_PASSIVESTANDB) {
        return true;
    }
    if (state >= TM_AS_CATCH_FIRST && state <= TM_AS_CATCH_LAST) {
        return true;
    }
    if (state >= TM_AS_THROW_FIRST && state <= TM_AS_THROW_LAST) {
        return true;
    }
    if (state >= TM_AS_SPECIALTHROW_FIRST && state <= TM_AS_SPECIALTHROW_LAST)
    {
        return true;
    }
    return false;
}

/// HitstunMonitor (Combo Counter - On Combo Increment.asm), installed in the
/// victim's FighterData.TM.cb_anim and run every frame by procAnim.
///
/// When the combo ends, TM-CE looks for message ID 13 in the attacker's
/// Display Message 2.0 windows to turn it green and keep it 60 frames.
/// The combo message is made with Message_Display (a different message
/// system, and its kind is r13, not 13), so that search never finds it and
/// TM-CE only clears the callback. That effective behaviour is kept.
static void hitstunMonitor(HSD_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);

    if (ftLib_IsFighter(fp->dmg.x1868_source) && comboContinues(fp)) {
        return;
    }
    tmce_osdmisc_SetAnimCallback(fp, NULL);
}

/// Fighter_procAnim followed by Custom Function Blrl + Keep Combo Counter
/// Going For Missed Techs+Getups.asm, which TM-CE injects at
/// Fighter_procAnim+0x828: the join point of every path into the epilogue,
/// so after the function returns is the same place.
static void procAnim(HSD_GObj* gobj)
{
    Fighter* fp;
    HSD_GObjEvent cb;

    Fighter_procAnim(gobj);

    fp = GET_FIGHTER(gobj);
    cb = tmce_osdmisc_GetAnimCallback(fp);
    if (cb != NULL) {
        cb(gobj);
    }
    /* vanilla's check (skipped by the `word` hook at +0x7E4), extended */
    if (!comboContinues(fp)) {
        pl_800411C4(fp->player_idx, fp->is_sub_fighter);
    }
}

/// Wraps the HSD_GObj_SetupProc calls that install Fighter_procAnim
/// (Fighter_Create+0x33C, ftDemo_CreateFighter+0x298).
HSD_GObjProc* tm_osdmisc_SetupProcAnim(HSD_GObj* gobj, HSD_GObjEvent func,
                                       u8 pri)
{
    if (func == (HSD_GObjEvent) Fighter_procAnim) {
        func = procAnim;
    }
    return HSD_GObj_SetupProc(gobj, func, pri);
}

/* ---- combo increment ---------------------------------------------------- */

/// Pummels and Multi-Hits Increment Total Damage But Not Combo Counter.asm:
/// the move IDs that should add damage but not a hit are turned into one
/// vanilla already skips.
static int comboMoveId(int slot, int victim, int move_id)
{
    HSD_GObj* a_gobj = Player_GetEntity(slot);
    HSD_GObj* v_gobj = Player_GetEntity(victim);
    Fighter* a;
    Fighter* v;

    /* TM-CE dereferences these unchecked */
    if (a_gobj == NULL || v_gobj == NULL) {
        return move_id;
    }
    a = GET_FIGHTER(a_gobj);
    v = GET_FIGHTER(v_gobj);

    if (move_id == 0x34) { /* pummel */
        return TM_MOVE_NO_COMBO;
    }
    if (v->dmg.x18ec_instancehitby == a->x2074.x2088) {
        /* same move instance: only a throw's release hit counts */
        if (move_id < 0x35 || move_id > 0x38) {
            return TM_MOVE_NO_COMBO;
        }
        if (a->x1A6A != 0) {
            return TM_MOVE_NO_COMBO;
        }
        return move_id;
    }
    /* cliff attacks count */
    if (move_id == 0x3F || move_id == 0x3E) {
        return move_id;
    }
    /* mid-grab hitboxes don't (the attacker is grabbable once the throw
     * releases the victim) */
    if (a->x1A6A != 0) {
        return TM_MOVE_NO_COMBO;
    }
    return move_id;
}

static void comboDisplay(int slot, int hits)
{
    HSD_GObj* gobj;
    Fighter* fp;

    if (!tm_osd_IsEnabled(TM_OSD_COMBOCOUNTER)) {
        return;
    }
    gobj = Player_GetEntity(slot);
    if (gobj == NULL) {
        return;
    }
    fp = GET_FIGHTER(gobj);
    if (tm_osd_IsFollower(fp)) {
        return;
    }
    if (hits < 2) {
        return;
    }
    /* TM-CE calls pl_80041300 with r3 = 0 (left over from the follower
     * check), so it always showed port 1's combo damage. Fixed: the
     * attacker's. */
    Message_Display(TM_OSDMISC_COMBO_KIND, fp->player_idx, TM_MSGCOLOR_WHITE,
                    "Combo Count\n%d Hits / %d%", hits, pl_80041300(slot));

    /* watch the victim until the combo ends */
    if (ftLib_IsFighter(fp->x2094)) {
        tmce_osdmisc_SetAnimCallback(GET_FIGHTER(fp->x2094), hitstunMonitor);
    }
}

/// Wraps the only call to pl_80040ED4 (pl_8003EB30+0xD4), vanilla's combo
/// statistics update for @p slot hitting @p victim.
void tm_osdmisc_ComboStat(int slot, int is_sub, int victim, int victim_sub,
                          int move_id, float damage)
{
    struct pl_x5EC_t* stats;
    int hits;

    /* TM-CE: pl_80040ED4+0x30, before the move ID is used */
    move_id = comboMoveId(slot, victim, move_id);

    pl_80040ED4(slot, is_sub, victim, victim_sub, move_id, damage);

    /* TM-CE: pl_80040ED4+0xD0, reading the hit count from r3. On the early
     * return for a sub-fighter victim r3 is still the victim's base, so
     * entry 0 is read. */
    stats = Player_GetUnk6A8Ptr(victim);
    hits = (u16) stats->x10[victim_sub == 1 ? 0 : slot].x4;
    comboDisplay(slot, hits);
}

/* ---- move instances ------------------------------------------------------ */

/// Replaces ftColl_80078998 (`function` hook; an item hitting a fighter).
/// Edited copy with Disregard Projectile Hitboxes w Same Move ID.asm: a
/// projectile from the move instance the victim was last hit by does not
/// update the combo statistics.
void tm_osdmisc_ItemHitStats(HSD_GObj* arg0, HSD_GObj* arg1, float arg2)
{
    Item* ip;

    plStale_UpdateStaleMovesFromItem(arg0, arg1);
    ftColl_8007646C(arg0, arg1);
    ip = arg0->user_data;
    if (ftLib_IsFighter(ip->owner)) {
        Fighter* owner_fp = GET_FIGHTER(ip->owner);
        Fighter* victim_fp = GET_FIGHTER(arg1);
        if (victim_fp->dmg.x18ec_instancehitby == ip->xDA8_short) {
            return;
        }
        pl_8003EB30(arg2, owner_fp->player_idx, owner_fp->is_sub_fighter,
                    victim_fp->player_idx, victim_fp->is_sub_fighter,
                    ip->xD90.x0.x2073);
    }
}

/// Replaces ft_800895E0 (`function` hook; called only by
/// Fighter_ChangeMotionState, now src/melee/tm/osdcore/osd_motion.c).
/// Edited copy with Interrupting Move with Same Move Gives a Unique ID.asm:
/// entering the motion state the fighter was just in (fp->motion_id ==
/// FighterData.TM.state_prev[0], already shifted by then) gets a new attack
/// instance even when the move ID is unchanged.
void tm_osdmisc_SetAttackInstance(Fighter* fp, int arg1)
{
    union Struct2070 val;
    union Struct2070 sp18;
    union Struct2070 sp14;

    val = *(union Struct2070*) &arg1;
    if (val.x0.x2073 == 0 ||
        (int) fp->motion_id == tmce_osdmisc_PrevState(fp) ||
        val.x0.x2073 != fp->x2070.x0.x2073)
    {
        fp->x2074.x2088 = plAttack_80037B08();
    }
    if (fp->kind == Ft_Kind_Luigi && val.x0.x2073 == 0x71) {
        sp18.x2070_int = 0x240063;
        val = sp18;
    }
    if (val.x0.x2073 == 0x62) {
        if (fp->item_gobj != NULL && it_8026B6C8(fp->item_gobj) != 0) {
            sp14.x2070_int = 0x44003D;
            val = sp14;
        }
    }
    fp->x2070.x2070_int = val.x2070_int;
    ft_80089768(&fp->x2074.x2074_vec);
    fp->x2074.x2074_vec.x = (s32) fp->dmg.x1830_percent;
    if (fp->is_metal) {
        fp->x2074.x10.x0.x2084_b1 = 1;
    }
    if (fp->x197C != NULL) {
        fp->x2074.x10.x0.x2084_b2 = 1;
    }
    if (fp->x221D_b6) {
        fp->x2074.x10.x0.x2084_b3 = 1;
    }
    if (fp->x2226_b4) {
        fp->x2074.x10.x0.x2084_b4 = 1;
    }
    if (fp->x2220_b5) {
        fp->x2074.x10.x0.x2084_b5 = 1;
    }
    if (fp->x2220_b6) {
        fp->x2074.x10.x0.x2084_b6 = 1;
    }
}

/// Wraps the ftColl_8007891C call in ftCo_800DDDE4 (+0x80; a throw's hitbox
/// hitting the thrown fighter). Throw Hitboxes Update Variable in
/// Playerblock.asm (+0x84): the victim's damage source becomes the thrower.
void tm_osdmisc_ThrowHit(Fighter_GObj* thrower, Fighter_GObj* victim,
                         float arg2)
{
    ftColl_8007891C(thrower, victim, arg2);
    GET_FIGHTER(victim)->dmg.x1868_source = thrower;
}
