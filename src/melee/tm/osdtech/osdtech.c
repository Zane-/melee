/**
 * @file
 * Native hooks for TM-CE's Dashback, Ledge Codes, Wavedash Display and SDI
 * Display OSDs (../TrainingMode/ASM/training-mode/Onscreen Display/).
 *
 * TM-CE injects mid-function. Each site here sits right before or after a
 * call that is the only way into or out of it, so a `call` hook on that
 * call runs the OSD at the same point; the comments say why it is
 * equivalent. The display logic is in src/tmce/osdtech_osd.c (MexTK types).
 */
#include "osdtech.h"

#include "../ucf/ucf.h"

/* tm_osdtech_PreHitlagCallback recomputes vanilla's SDI stick magnitude;
 * vanilla rounds each multiply and the add separately (no fused madd). */
#pragma fp_contract off

#include <Runtime/platform.h>
#include <math.h>
#include <melee/ft/fighter.h>
#include <melee/ft/ft_0877.h>
#include <melee/ft/ft_0892.h>
#include <melee/ft/ftanim.h>
#include <melee/ft/ftcoll.h>
#include <melee/ft/ftcommon.h>
#include <melee/ft/kinds/ftCommon/ftCo_Attack100.h>
#include <melee/ft/kinds/ftCommon/ftCo_Damage.h>
#include <melee/ft/kinds/ftCommon/ftCo_Dash.h>
#include <melee/ft/kinds/ftCommon/ftCo_Fall.h>
#include <melee/ft/kinds/ftCommon/ftCo_Landing.h>
#include <melee/ft/kinds/ftCommon/types.h>
#include <melee/ft/types.h>

/// @name src/tmce/osdtech_osd.c (MexTK side; fighters and GObjs as void*)
/// @{
void tmce_osdtech_TurnToDash(void* gobj);
void tmce_osdtech_CliffWaitFall(void* fp);
void tmce_osdtech_Ledgestall(void* fp);
void tmce_osdtech_GalintAerialInterrupt(void* gobj);
void tmce_osdtech_GalintLaserLand(void* gobj);
void tmce_osdtech_GalintLedgedash(void* gobj);
void tmce_osdtech_GalintNoImpactLand(void* gobj);
void tmce_osdtech_SaveAirdodge(void* fp, float angle);
void tmce_osdtech_WavedashLand(void* gobj);
void tmce_osdtech_SdiReset(void* gobj);
void tmce_osdtech_SdiHitlag(void* fp, float stick_sq, float min_sq);
/// @}

/* ---- Dashback ----------------------------------------------------------- */

/// Wraps `ftCo_Dash_Enter` in ftCo_Turn_IASA (+0x194).
///
/// Dashback/Run Out of Tilt Turn.asm injects at +0x190, the `li r4,0` that
/// sets up this call (it ends by redoing `mr r3,r30; li r4,0`); nothing
/// branches there, so running the OSD first here is the same point.
void tm_osdtech_DashEnter(Fighter_GObj* gobj, int arg1)
{
    tmce_osdtech_TurnToDash(gobj);
    ftCo_Dash_Enter(gobj, arg1);
}

/* ---- Ledge Codes -------------------------------------------------------- */

/// Wraps `ftCo_Fall_Enter` in ftCo_8009AAFC (+0x80), dropping from the ledge.
///
/// Ledge Codes/Frames Spent in CliffWait.asm injects at +0x7C, the store
/// right before this call; nothing branches between them. The OSD reads
/// the CliffWait frame count, so it runs before Fall_Enter changes state.
void tm_osdtech_CliffFallEnter(Fighter_GObj* gobj)
{
    tmce_osdtech_CliffWaitFall(GET_FIGHTER(gobj));
    ftCo_Fall_Enter(gobj);
}

/// Wraps `ft_PlaySFX` in ftCliffCommon_80081370 (+0x178), the ledge grab.
///
/// Ledge Codes/Ledgestall/Ledgestall Display.asm injects at +0x17C, the
/// epilogue right after this call; nothing branches there.
void tm_osdtech_CliffCatchSFX(Fighter* fp, enum_t id, u8 vol, u8 pan)
{
    ft_PlaySFX(fp, id, vol, pan);
    tmce_osdtech_Ledgestall(fp);
}

/// Wraps `ftCo_Landing_Enter_Basic` in ftCo_LandingAir_EnterWithLag
/// (+0xF8). GALINT Aerail Interrupt.asm replaces that `bl` with its code
/// followed by the same call; it reads the fighter from r5, which on every
/// path to this call is still the fighter (only the L-cancel path reloads
/// r5, and that path takes the other branch).
void tm_osdtech_LandingAirBasic(Fighter_GObj* gobj)
{
    tmce_osdtech_GalintAerialInterrupt(gobj);
    ftCo_Landing_Enter_Basic(gobj);
}

/// Wraps `ft_8008A2BC` in ftCo_AirCatchHit_Coll (+0xCC). GALINT Laser
/// Land.asm injects at +0xC8, the `mr r3,r28` for this call; only the
/// fall-through reaches it.
void tm_osdtech_AirCatchLand(Fighter_GObj* gobj)
{
    tmce_osdtech_GalintLaserLand(gobj);
    ft_8008A2BC(gobj);
}

/// Wraps `ft_8008A2BC` in ftCo_Landing_Anim (+0x24). GALINT Ledgedash.asm
/// injects at +0x20, the `mr r3,r31` for this call.
void tm_osdtech_LandingAnimLand(Fighter_GObj* gobj)
{
    tmce_osdtech_GalintLedgedash(gobj);
    ft_8008A2BC(gobj);
}

/// Wraps `ft_8008A2BC` in ft_80082B1C (+0x34). GALINT No Impact Land.asm
/// injects at +0x30, the `mr r3,r30` for this call; only the fall-through
/// reaches it.
void tm_osdtech_NoImpactLand(Fighter_GObj* gobj)
{
    tmce_osdtech_GalintNoImpactLand(gobj);
    ft_8008A2BC(gobj);
}

/* ---- Wavedash Display --------------------------------------------------- */

typedef enum cmd_var_idx {
    cmd_skip_decay,
} cmd_var_idx;

/// ftCo_EscapeAir.c's inlineA0.
static inline void escapeAirVel(Fighter* fp)
{
    fp->mv.co.escapeair.self_vel = fp->self_vel;
    if (ABS(fp->input.lstick[0].x) < p_ftCommonData->escapeair_deadzone.x) {
        if (ABS(fp->input.lstick[0].y) < p_ftCommonData->escapeair_deadzone.y)
        {
            fp->self_vel.y = 0;
            fp->self_vel.x = 0;
            return;
        }
    }
    {
        float angle = ftCommon_8007D9D4(fp);
        fp->self_vel.x = p_ftCommonData->escapeair_force * cosf(angle);
        fp->self_vel.y = p_ftCommonData->escapeair_force * sinf(angle);
    }
}

/// Replaces ftCo_80099A9C (`function` hook), entering EscapeAir.
///
/// Edited copy of the vanilla function with Wavedash Display/Save Airdodge
/// Y Angle.asm (+0xD8): it must run before `mv.co.escapeair.timer` (the
/// same word as the jump's state_var1, the short/full hop flag it reads)
/// is overwritten, which no call boundary allows.
void tm_osdtech_EscapeAirEnter(Fighter_GObj* gobj, int timer)
{
    u8 _[8];
    Fighter* fp = gobj->user_data;
    ftCo_800D705C(gobj);
    escapeAirVel(fp);
    fp->cmd_vars[cmd_skip_decay] = false;
    /* TM-CE: Joystick_Angle_Retrieve, hop type from state_var1 */
    tmce_osdtech_SaveAirdodge(fp, ftCommon_8007D9D4(fp));
    fp->mv.co.escapeair.timer = timer;
    Fighter_ChangeMotionState(gobj, ftCo_MS_EscapeAir, Ft_MF_None, 0, 1, 0,
                              NULL);
    ftAnim_8006EBA4(gobj);
    ftCommon_8007EBAC(fp, 23, 0);
}

/// Wraps `ftCo_LandingFallSpecial_Enter` in ftCo_80099D70 (+0x18), landing
/// from an airdodge. Wavedash Display/Wavedash Timing Display.asm injects
/// at +0xC, before the landing lag load that sets up this call (the only
/// call in the function).
void tm_osdtech_EscapeAirLand(Fighter_GObj* gobj, bool allow_interrupt,
                              float landing_lag)
{
    tmce_osdtech_WavedashLand(gobj);
    ftCo_LandingFallSpecial_Enter(gobj, allow_interrupt, landing_lag);
}

/* ---- SDI Display -------------------------------------------------------- */

/// Wraps the `ftCo_8008EC90` calls in Fighter_procCollResolve (+0x20C) and
/// ftKb_SpecialN_800F5C34 (+0x7C), the fighter getting hit.
///
/// SDI Display/Initialize Total SDI Inputs Variable.asm injects at
/// ftCo_8008EC90+0xA8C, the common exit every path reaches; after it the
/// function only calls ftCo_800C3598 (knockback velocity), which does not
/// touch what the reset reads. So running it after the call is equivalent.
void tm_osdtech_DamageEnter(Fighter_GObj* gobj)
{
    ftCo_8008EC90(gobj);
    tmce_osdtech_SdiReset(gobj);
}

/// Wraps `ftColl_80076528` in Fighter_procUpdate (+0x5D0), the call right
/// before `fp->hitlag_cb(gobj)`.
///
/// SDI Display/SDI Display Main.asm injects at ftCo_Damage_OnEveryHitlag
/// +0x3C, which runs on every hitlag frame that allows SDI, before vanilla
/// applies it. That function cannot be replaced (Slippi patches inside it)
/// and has no call before the site; it is only ever run through
/// `hitlag_cb`, called right after this. ftColl_80076528 only counts down
/// a combo timer, so this is the same point.
void tm_osdtech_PreHitlagCallback(Fighter_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);

    ftColl_80076528(gobj);
    if (fp->hitlag_cb == ftCo_Damage_OnEveryHitlag && fp->allow_sdi) {
        float x = fp->input.lstick[0].x;
        float y = fp->input.lstick[0].y;
        float min = p_ftCommonData->sdi_min_stick_mag;
        float xx = x * x;
        float yy = y * y;
        tmce_osdtech_SdiHitlag(fp, xx + yy, min * min);
    }
    /* Last, so the display above sees the vanilla callback. */
    tm_ucf_PreHitlag(gobj);
}
