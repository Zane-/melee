/**
 * @file
 * TM-CE on-screen displays that hang off a single vanilla site (osdmisc
 * area): L-Cancel, Powershield, Jump Cancel, Grab Breakout, Boost Grab,
 * Glide Toss, Airdodge Item Throw, Yoshi Egg Toss, Bowser Fortress NIL.
 *
 * Each function names the TM-CE file
 * (../TrainingMode/ASM/training-mode/Onscreen Display/) and its injection
 * site. The hooks run the OSD at the same point relative to vanilla code:
 * a `call` hook on the call just before or after the site, or an edited
 * copy of the function. config/GALE01/tm_hooks/osdmisc.txt has the sites.
 */
#include "osdmisc.h"

#include "../osdcore/osd.h"

#include <math.h>
#include <string.h>
#include <dolphin/gx.h>
#include <melee/ft/fighter.h>
#include <melee/ft/ft_0892.h>
#include <melee/ft/ftanim.h>
#include <melee/ft/ftchangeparam.h>
#include <melee/ft/ftcoll.h>
#include <melee/ft/inlines.h>
#include <melee/ft/kinds/ftCommon/ftCo_Attack100.h>
#include <melee/ft/kinds/ftCommon/ftCo_ItemThrow.h>
#include <melee/ft/kinds/ftCommon/ftCo_KneeBend.h>
#include <melee/ft/kinds/ftCommon/ftCo_Landing.h>
#include <melee/ft/kinds/ftYoshi/ftyoshi.h>
#include <melee/ft/kinds/ftYoshi/ftyoshispecialhi.h>
#include <melee/ft/kinds/ftYoshi/types.h>
#include <melee/ft/types.h>
#include <melee/it/kinds/ityoshieggthrow.h>
#include <melee/lb/lb_00B0.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/sislib.h>

/// ft/kinds/ftCommon/ftCo_CatchPull.c (global, not in a header).
void fn_800DA054(Fighter_GObj* gobj);

/// TM-CE motion state numbers the files compare against (Globals.s ASID_*
/// and character-specific states).
enum {
    TM_AS_KNEEBEND = 0x18,
    TM_AS_GUARDON = 178,
    TM_AS_GUARDREFLECT = 182,
    TM_AS_YOSHI_GUARDON = 341,
    TM_AS_YOSHI_GUARDREFLECT = 345,
    TM_AS_KOOPA_SPECIALAIRHI = 360, ///< Whirling Fortress (air)
};

static void setColor(HSD_Text* text, int subtext, u32 rgba)
{
    GXColor c;
    c.r = rgba >> 24;
    c.g = rgba >> 16;
    c.b = rgba >> 8;
    c.a = rgba;
    HSD_SisLib_803A74F0(text, subtext, &c);
}

/* ---- L Cancel Display NEW.asm (ftCo_LandingAir_EnterWithMsidLag+0x68) -- */

/// Successful / total L-cancels per player slot. TM-CE keeps them at
/// 0x804A1FA8 (inside the score display block un_804A1F58, which
/// un_802FF498 zeroes at the start of every match); here they are statics,
/// reset at the same point (tm_osdmisc_ScoreInitZero).
static struct {
    u16 success;
    u16 total;
} lc_stats[6];

static int lcRate(int slot)
{
    /* GetLCRate: successful / total * 100, single precision, truncated */
    return (int) (((float) lc_stats[slot].success /
                   (float) lc_stats[slot].total) *
                  100.0F);
}

static void lcancelDisplay(Fighter* fp)
{
    HSD_GObj* msg;
    int slot = fp->player_idx;
    int frames = fp->x67F;
    int color;
    int rate;

    if (!tm_osd_IsEnabled(TM_OSD_LCANCEL) || tm_osd_IsFollower(fp)) {
        return;
    }
    if (frames < 7) {
        color = TM_MSGCOLOR_GREEN;
        lc_stats[slot].success++;
    } else {
        color = TM_MSGCOLOR_RED;
    }
    lc_stats[slot].total++;
    rate = lcRate(slot);

    if (frames <= 40) {
        msg = Message_Display(TM_OSD_LCANCEL, slot, color,
                              "L-Cancel %d%%\nFrame %d/7", rate, frames + 1);
    } else {
        msg = Message_Display(TM_OSD_LCANCEL, slot, color,
                              "L-Cancel %d%%\nNo Press", rate, frames + 1);
    }
    setColor(tm_osd_MessageText(msg), 0, TM_OSD_RGBA_WHITE);
}

/// Wraps the last call in ftCo_LandingAir_EnterWithMsidLag (+0x64,
/// ftAnim_SetAnimRate). TM-CE injects at the next instruction (+0x68).
void tm_osdmisc_LandingAirSetAnimRate(Fighter_GObj* gobj, float rate)
{
    ftAnim_SetAnimRate(gobj, rate);
    lcancelDisplay(GET_FIGHTER(gobj));
}

/// Wraps the memzero in un_802FF498 (+0x20), which clears the score display
/// block at match start; TM-CE's L-cancel counters lived in that block.
void tm_osdmisc_ScoreInitZero(void* mem, ssize_t size)
{
    memzero(mem, size);
    memset(lc_stats, 0, sizeof(lc_stats));
}

/* ---- Powershield.asm (ftColl_80077688+0x18) ---------------------------- */

static void powershieldDisplay(Fighter* fp)
{
    HSD_GObj* msg;
    int slot = fp->player_idx;

    if (!tm_osd_IsEnabled(TM_OSD_POWERSHIELD) || tm_osd_IsFollower(fp)) {
        return;
    }
    switch (fp->motion_id) {
    case TM_AS_GUARDON:
    case TM_AS_YOSHI_GUARDON:
        msg = Message_Display(TM_OSD_POWERSHIELD, slot, TM_MSGCOLOR_RED,
                              "Missed Powershield\nNo Hard Press");
        break;
    case TM_AS_GUARDREFLECT:
    case TM_AS_YOSHI_GUARDREFLECT:
        if (fp->reflecting) {
            msg = Message_Display(TM_OSD_POWERSHIELD, slot, TM_MSGCOLOR_RED,
                                  "Missed Powershield\nEarly: %df",
                                  (int) fp->mv.co.guard.x0 + 1);
        } else {
            /* TM-CE also stores 0xFFA20000 at 0x30 off the caller's r29
             * here (a stray write into whatever the caller held); dropped. */
            msg = Message_Display(TM_OSD_POWERSHIELD, slot, TM_MSGCOLOR_RED,
                                  "Missed Powershield\nReflect Ended: %df",
                                  (int) fp->mv.co.guard.x0 - 1);
        }
        break;
    default:
        return;
    }
    setColor(tm_osd_MessageText(msg), 0, TM_OSD_RGBA_WHITE);
}

/// Wraps the only call to ftColl_80077688 (ftColl_8007925C+0x618), an item
/// hitbox hitting a fighter's shield. TM-CE injects at the start of the
/// callee (+0x18), before anything it does.
void tm_osdmisc_ShieldHitByItem(Item* item, HitCapsule* hit, Fighter* fp,
                                Vec3* pos, f32 val)
{
    powershieldDisplay(fp);
    ftColl_80077688(item, hit, fp, pos, val);
}

/* ---- Jump Cancel.asm (ftCo_KneeBend_IASA+0x9C) ------------------------- */

/// Replaces ftData_MotionStateList[KneeBend].iasa_cb (`pointer` hook).
/// TM-CE injects at the shared epilogue of ftCo_KneeBend_IASA, which every
/// path reaches, so running after the original is the same.
void tm_osdmisc_KneeBendIASA(Fighter_GObj* gobj)
{
    Fighter* fp;
    int frames;

    ftCo_KneeBend_IASA(gobj);

    fp = GET_FIGHTER(gobj);
    /* only when jump squat was left (grab, up smash, up special...) */
    if (fp->motion_id == TM_AS_KNEEBEND) {
        return;
    }
    if (!tm_osd_IsEnabled(TM_OSD_ACTOOJUMPSQUAT) || tm_osd_IsFollower(fp)) {
        return;
    }
    frames = tmce_osdmisc_PrevStateFrames(fp);
    Message_Display(TM_OSD_ACTOOJUMPSQUAT, fp->player_idx,
                    frames == 1 ? TM_MSGCOLOR_GREEN : TM_MSGCOLOR_RED,
                    "Jump Cancel\nFrame %d", frames);
}

/* ---- Grab Breakout.asm (fn_800DA054+0x28) ------------------------------ */

/// TM-CE keeps these inside its code. One set for all players, as in TM-CE
/// ("doesn't work for simultaneous grabs in doubles").
static float grab_initial_timer;
static float grab_frames;
static int grab_last_match_frame;

static void grabBreakoutDisplay(Fighter* victim)
{
    int now;
    float timer;

    if (!tm_osd_IsEnabled(TM_OSD_GRABBREAKOUT) || tm_osd_IsFollower(victim))
    {
        return;
    }
    /* not exactly one frame after the previous run: a new grab */
    now = tmce_osdmisc_MatchFrames();
    if (grab_last_match_frame + 1 != now) {
        grab_initial_timer = victim->grab_timer;
        grab_frames = 0.0F;
    }
    grab_last_match_frame = now;

    grab_frames += 1.0F;
    timer = victim->grab_timer;
    Message_Display(TM_OSD_GRABBREAKOUT, victim->player_idx,
                    TM_MSGCOLOR_WHITE,
                    "Grab Breakout\nGrab Timer: %.0f\nMash Rate: %.1f/f",
                    timer, (grab_initial_timer - timer) / grab_frames);
}

/// Wraps the three calls to fn_800DA054 (fn_800DA190+0x34, fn_800DA4A0+0xC,
/// fn_800DA678+0xC; the grabber's per-frame hold check). TM-CE injects
/// after it loads the victim (+0x28), before anything else.
void tm_osdmisc_CatchPullPhys(Fighter_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    grabBreakoutDisplay(GET_FIGHTER(fp->victim_gobj));
    fn_800DA054(gobj);
}

/* ---- Boost Grab.asm, Glide Toss.asm ------------------------------------ */

static void interruptDisplay(Fighter* fp, int osd, char* text, int frames)
{
    if (!tm_osd_IsEnabled(osd) || tm_osd_IsFollower(fp)) {
        return;
    }
    Message_Display(osd, fp->player_idx, TM_MSGCOLOR_WHITE, text, frames);
}

/// Wraps the ftCo_800D8C54 call in ftCo_800D8AE0 (+0x80): a dash attack
/// being interrupted into a grab. TM-CE injects just before it (+0x78).
void tm_osdmisc_StartBoostGrab(Fighter_GObj* gobj, FtMotionId msid)
{
    Fighter* fp = GET_FIGHTER(gobj);
    interruptDisplay(fp, TM_OSD_BOOSTGRAB, "Boost Grab\nFrame %d",
                     tmce_osdmisc_StateFrames(fp));
    ftCo_800D8C54(gobj, msid);
}

/// Wraps the ftCo_800957F4 call in ftCo_8009563C (+0x88): a roll being
/// interrupted by an item throw. TM-CE injects just before it (+0x84).
void tm_osdmisc_StartGlideToss(Fighter_GObj* gobj, FtMotionId msid)
{
    Fighter* fp = GET_FIGHTER(gobj);
    interruptDisplay(fp, TM_OSD_ROLLAIRDODGEINTERRUPT, "Glide Toss\nFrame %d",
                     tmce_osdmisc_StateFrames(fp));
    ftCo_800957F4(gobj, msid);
}

/* ---- Airdodge Item Throw.asm (ftCo_EscapeAir_IASA+0x58) ---------------- */

/// Wraps the ftCo_80095328 call in ftCo_EscapeAir_IASA (+0x48). TM-CE
/// injects after it returned true (+0x58), with *is_throw in r0.
bool tm_osdmisc_EscapeAirItemCheck(Fighter_GObj* gobj, bool* is_throw)
{
    bool ret = ftCo_80095328(gobj, is_throw);
    if (ret) {
        Fighter* fp = GET_FIGHTER(gobj);
        if (*is_throw) {
            interruptDisplay(fp, TM_OSD_ROLLAIRDODGEINTERRUPT,
                             "Airdodge Item Throw\nFrame %d",
                             tmce_osdmisc_PrevStateFrames(fp));
        } else {
            interruptDisplay(fp, TM_OSD_ROLLAIRDODGEINTERRUPT,
                             "Airdodge Z-Drop\nFrame %d",
                             tmce_osdmisc_StateFrames(fp));
        }
    }
    return ret;
}

/* ---- Yoshi Egg Toss.asm (fn_8012E110+0xF8) ----------------------------- */

/// The throw angle ftYs_SpecialS_8012DF8C computes. TM-CE reads it from
/// f6 after that call: sinf's own argument, which sinf leaves in f6.
static float yoshiEggAngle(Fighter* fp)
{
    ftYs_DatAttrs* da = fp->dat_attrs;
    float mag;
    float angle;

    mag = ABS(fp->input.lstick[0].x) / da->xEC;
    if (mag > 1.0F) {
        mag = 1.0F;
    }
    mag *= da->xF0;
    if (mag < da->xF4) {
        mag = 0.0F;
    }
    mag *= getStickDirX(fp);
    if (fp->facing_dir == +1.0F) {
        angle = da->specialhi_base_angle - mag;
    } else {
        angle = M_PI - da->specialhi_base_angle - mag;
    }
    return angle;
}

static void yoshiEggDisplay(Fighter* fp)
{
    float angle;

    if (!tm_osd_IsEnabled(TM_OSD_FIGHTERSPECIFICTECH)) {
        return;
    }
    angle = yoshiEggAngle(fp);
    /* mirror if facing left */
    if (!(fp->facing_dir > 0.0F)) {
        angle = 3.1415926F - angle;
    }
    /* f3 after the call: the press duration as a float */
    Message_Display(TM_OSD_FIGHTERSPECIFICTECH, fp->player_idx,
                    TM_MSGCOLOR_WHITE, "Egg Toss\nAngle: %.0f\nStrength: %.0f",
                    angle / 0.0174533F, (float) fp->mv.ys.specialhi.x4);
}

/// ft/kinds/ftYoshi/ftyoshispecialhi.c (static).
static void setDamageCallbacks(Fighter_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    if (fp->u.ys.x2238 != NULL) {
        fp->take_dmg_cb = ftYs_Init_8012BA8C;
        fp->death2_cb = ftYs_Init_8012BA8C;
    }
}

/// Replaces fn_8012E110 (`function` hook; Yoshi's egg throw accessory
/// callback, only reached through fp->accessory4_cb). Edited copy: the OSD
/// runs right after the angle is computed, as in TM-CE.
void tm_osdmisc_YoshiEggAccessory(Fighter_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    ftYs_DatAttrs* da = fp->dat_attrs;

    if (ftCheckThrowB0(fp)) {
        Vec3 sp30;
        lb_8000B1CC(fp->parts[31].joint, NULL, &sp30);
        fp->x1984_heldItemSpec = fp->u.ys.x2238 =
            it_802B2A10(gobj, &sp30, 0x1F, fp->facing_dir);
        setDamageCallbacks(gobj);
    }

    if (fp->cmd_vars[0] != 0U && fp->u.ys.x2238 != NULL) {
        Vec3 sp24;
        Vec3 sp18;
        fp->cmd_vars[0] = 0;
        fp->mv.ys.specialhi.x0 = 1;
        sp24.x = da->x104 * fp->facing_dir;
        sp24.y = da->x108;
        sp24.z = 0.0F;
        ftYs_SpecialS_8012DF8C(gobj, &sp18);
        yoshiEggDisplay(fp);
        {
            float x4 = fp->mv.ys.specialhi.x4;
            it_802B28C8(fp->u.ys.x2238, &sp18, &sp24, x4 * da->x110 + da->x10C,
                        x4);
        }
        fp->u.ys.x2238 = NULL;
        fp->take_dmg_cb = NULL;
        fp->death2_cb = NULL;
    }
}

/* ---- Bowser Fortress NIL.asm (ftCo_80096D28+0x1C) ---------------------- */

static void bowserNilDisplay(Fighter* fp)
{
    int frames;

    if (!tm_osd_IsEnabled(TM_OSD_FIGHTERSPECIFICTECH) ||
        tm_osd_IsFollower(fp))
    {
        return;
    }
    if (fp->kind != Ft_Kind_Koopa) {
        return;
    }
    /* special fall entered from Whirling Fortress (air) */
    if (tmce_osdmisc_PrevState(fp) != TM_AS_KOOPA_SPECIALAIRHI) {
        return;
    }
    frames = (int) fp->cur_anim_frame + 1;
    if (frames == 1) {
        Message_Display(TM_OSD_FIGHTERSPECIFICTECH, fp->player_idx,
                        TM_MSGCOLOR_GREEN, "Successful NIL\nSp Fall Frames: %d",
                        frames);
    } else {
        Message_Display(TM_OSD_FIGHTERSPECIFICTECH, fp->player_idx,
                        TM_MSGCOLOR_RED, "Missed NIL:\nSp Fall Frames: %d",
                        frames);
    }
}

/// Replaces ftCo_80096D28 (`function` hook; the special fall landing
/// callback, only passed to ft_80083090 by ftCo_FallSpecial's collision
/// callback). Edited copy: the OSD runs first, as TM-CE injects after the
/// fighter is loaded (+0x1C).
void tm_osdmisc_FallSpecialLand(Fighter_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    bowserNilDisplay(fp);
    if (fp->mv.co.fallspecial.x10 || fp->self_vel.y < ftCo_800D0EC8(fp)) {
        ftCo_LandingFallSpecial_Enter(gobj,
                                      fp->mv.co.fallspecial.allow_interrupt,
                                      fp->mv.co.fallspecial.landing_lag);
    } else {
        ft_8008A2BC(gobj);
    }
}
