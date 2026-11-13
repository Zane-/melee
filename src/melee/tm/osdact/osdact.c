/**
 * @file
 * TM-CE "act out of" on-screen displays, native side (osdact area).
 *
 * Every TM-CE file here injects right after an interrupt check, or at the
 * end of a state's IASA function, and passes the check's result (r3) to a
 * static display function. The hooks wrap that check (`call`) or, where the
 * site is a function epilogue with no call before it, replace the function
 * with an edited copy (`function`) that tracks the same r3 value. Display
 * logic: src/tmce/osdact_osds.c. Hook table: config/GALE01/tm_hooks/osdact.txt.
 */
#include "osdact.h"

#include "../ucf/ucf.h"

#include <melee/ft/ft_0DF0.h>
#include <melee/ft/ft_0DF1.h>
#include <melee/ft/ft_0CDD.h>
#include <melee/ft/ftanim.h>
#include <melee/ft/inlines.h>
#include <melee/ft/kinds/ftCommon/ftCo_AirCatch.h>
#include <melee/ft/kinds/ftCommon/ftCo_AppealS.h>
#include <melee/ft/kinds/ftCommon/ftCo_Attack1.h>
#include <melee/ft/kinds/ftCommon/ftCo_Attack100.h>
#include <melee/ft/kinds/ftCommon/ftCo_AttackAir.h>
#include <melee/ft/kinds/ftCommon/ftCo_AttackHi3.h>
#include <melee/ft/kinds/ftCommon/ftCo_AttackHi4.h>
#include <melee/ft/kinds/ftCommon/ftCo_AttackLw3.h>
#include <melee/ft/kinds/ftCommon/ftCo_AttackLw4.h>
#include <melee/ft/kinds/ftCommon/ftCo_AttackS3.h>
#include <melee/ft/kinds/ftCommon/ftCo_AttackS4.h>
#include <melee/ft/kinds/ftCommon/ftCo_Dash.h>
#include <melee/ft/kinds/ftCommon/ftCo_Escape.h>
#include <melee/ft/kinds/ftCommon/ftCo_Fall.h>
#include <melee/ft/kinds/ftCommon/ftCo_Guard.h>
#include <melee/ft/kinds/ftCommon/ftCo_HammerFall.h>
#include <melee/ft/kinds/ftCommon/ftCo_ItemThrow.h>
#include <melee/ft/kinds/ftCommon/ftCo_Jump.h>
#include <melee/ft/kinds/ftCommon/ftCo_JumpAerial.h>
#include <melee/ft/kinds/ftCommon/ftCo_Pass.h>
#include <melee/ft/kinds/ftCommon/ftCo_SpecialAir.h>
#include <melee/ft/kinds/ftCommon/ftCo_SpecialS.h>
#include <melee/ft/kinds/ftCommon/ftCo_Squat.h>
#include <melee/ft/kinds/ftCommon/ftCo_Turn.h>
#include <melee/ft/kinds/ftCommon/ftCo_Walk.h>
#include <melee/ft/kinds/ftFox/ftfoxappeals.h>
#include <melee/ft/types.h>
#include <melee/it/it_26B1.h>

/// Static in ft/kinds/ftPeach/ftpeachfloatattack.c (unique name).
void ftPe_8011BF34(HSD_GObj* gobj);

/* ======================================================================
 * Act OoAirborne/ (static function 0x8000550C). Each TM-CE file sits on
 * the `cmpwi r3,0` after one interrupt check in a jump / double jump /
 * fall / platform drop IASA function and passes that check's result.
 */

#define OSD_ACTOOAIRBORNE 18
#define OSD_MISCELLANEOUS 15

/// Special Out of Jump.asm (ftCo_Jump_IASA+0x20)
bool tm_osdact_SpecialOoJump(Fighter_GObj* gobj)
{
    bool r = ftCo_SpecialAir_CheckInput(gobj);
    tmce_osdact_OoAirborne(r, gobj, "Special OoJump\nFrame %d",
                           OSD_ACTOOAIRBORNE);
    return r;
}

/// Aerial Out of Jump.asm (ftCo_Jump_IASA+0x74)
bool tm_osdact_AerialOoJump(Fighter_GObj* gobj)
{
    bool r = ftCo_AttackAir_CheckItemThrowInput(gobj);
    tmce_osdact_OoAirborne(r, gobj, "Aerial OoJump\nFrame %d",
                           OSD_ACTOOAIRBORNE);
    return r;
}

/// DoubleJump Out of Jump.asm (ftCo_Jump_IASA+0xCC). TM-CE uses the
/// Miscellaneous message kind so it can show next to Aerial OoJump.
bool tm_osdact_DblJumpOoJump(Fighter_GObj* gobj)
{
    bool r = ftCo_800CB870(gobj);
    tmce_osdact_OoAirborne(r, gobj, "DblJump OoJump\nFrame %d",
                           OSD_MISCELLANEOUS);
    return r;
}

/// Special Out of DoubleJump.asm (ftCo_JumpAerial_IASA+0x24)
bool tm_osdact_SpecialOoDblJump(Fighter_GObj* gobj)
{
    bool r = ftCo_SpecialAir_CheckInput(gobj);
    tmce_osdact_OoAirborne(r, gobj, "Special OoDblJump\nFrame %d",
                           OSD_ACTOOAIRBORNE);
    return r;
}

/// Aerial Out of DoubleJump.asm (ftCo_JumpAerial_IASA+0x78)
bool tm_osdact_AerialOoDblJump(Fighter_GObj* gobj)
{
    bool r = ftCo_AttackAir_CheckItemThrowInput(gobj);
    tmce_osdact_OoAirborne(r, gobj, "Aerial OoDblJump\nFrame %d",
                           OSD_ACTOOAIRBORNE);
    return r;
}

/// Special Out of Fall.asm (ftCo_Fall_IASA_Inner+0x18; that function is
/// shared by several aerial IASAs, as in TM-CE)
bool tm_osdact_SpecialOoFall(Fighter_GObj* gobj)
{
    bool r = ftCo_SpecialAir_CheckInput(gobj);
    tmce_osdact_OoAirborne(r, gobj, "Special OoFall\nFrame %d",
                           OSD_ACTOOAIRBORNE);
    return r;
}

/// Aerial Out of Fall.asm (ftCo_Fall_IASA_Inner+0x94)
bool tm_osdact_AerialOoFall(Fighter_GObj* gobj)
{
    bool r = ftCo_AttackAir_CheckItemThrowInput(gobj);
    tmce_osdact_OoAirborne(r, gobj, "Aerial OoFall\nFrame %d",
                           OSD_ACTOOAIRBORNE);
    return r;
}

/// Special Out of Drop.asm (ftCo_Pass_IASA+0x18)
bool tm_osdact_SpecialOoDrop(Fighter_GObj* gobj)
{
    bool r = ftCo_SpecialAir_CheckInput(gobj);
    tmce_osdact_OoAirborne(r, gobj, "Special OoDrop\nFrame %d",
                           OSD_ACTOOAIRBORNE);
    return r;
}

/// Aerial Out of Drop.asm (ftCo_Pass_IASA+0x6C)
bool tm_osdact_AerialOoDrop(Fighter_GObj* gobj)
{
    bool r = ftCo_AttackAir_CheckItemThrowInput(gobj);
    tmce_osdact_OoAirborne(r, gobj, "Aerial OoDrop\nFrame %d",
                           OSD_ACTOOAIRBORNE);
    return r;
}

/* ======================================================================
 * Act OOS Frame Display/ (static function 0x80005508).
 */

/// Wraps `ftCo_800925A4` in ftCo_Guard_Anim (+0x28), always called.
/// Count During ShieldWait.asm (ftCo_Guard_Anim+0x14) increments the shield
/// frame count at the top of the function; nothing in between reads it.
bool tm_osdact_GuardAnimCheck(Fighter_GObj* gobj)
{
    tmce_osdact_ShieldFramesInc(gobj);
    return ftCo_800925A4(gobj);
}

/// Wraps `ftAnim_IsFramesRemaining` in ftCo_GuardOff_Anim (+0x28), always
/// called. Count During GuardOff.asm (+0x3C) increments in the epilogue,
/// after a possible ft_8008A2BC; that call does not touch the count.
bool tm_osdact_GuardOffAnimCheck(Fighter_GObj* gobj)
{
    bool r = ftAnim_IsFramesRemaining(gobj);
    tmce_osdact_ShieldFramesInc(gobj);
    return r;
}

/// Wraps `ftAnim_IsFramesRemaining` in ftCo_GuardSetOff_Anim (+0x28). Init
/// Frame Count.asm (+0x34) runs only when it returns false (shield stun
/// animation over): reset the count.
bool tm_osdact_GuardSetOffAnimCheck(Fighter_GObj* gobj)
{
    bool r = ftAnim_IsFramesRemaining(gobj);
    if (!r) {
        tmce_osdact_ShieldFramesReset(gobj);
    }
    return r;
}

/// Replaces ftCo_Guard_IASA (`function`). GuardWait - Display OOS Frame
/// Count.asm (+0xE0, the epilogue) passes r3: 1 when one of the checks
/// fired. The release-shield path leaves the fighter in GuardOff (or
/// Yoshi's shield release, with r3 from efAsync_Spawn), where TM-CE's
/// display exits, so it displays nothing here.
void tm_osdact_Guard_IASA(Fighter_GObj* gobj)
{
    Fighter* fp = gobj->user_data;
    bool r;

    /* inlineC0(gobj, ftCo_80092BE8) from ftCo_Guard.c */
    ftCo_80092BCC(gobj);
    if ((fp->mv.co.guard.xC && !fp->mv.co.guard.x10) ||
        (!fp->x221B.x221B_b0 && !fp->reflecting))
    {
        ftCo_80092BE8(gobj);
        return;
    }
    if (fp->mv.co.guard.x1C != 0) {
        --fp->mv.co.guard.x1C;
    }

    r = ftCo_8009515C(gobj) || tm_ucf_8009980C(gobj) ||
        ftCo_8009917C(gobj) || ftCo_Catch_CheckInput(gobj) ||
        ftCo_800CB024(gobj) || tm_ucf_8009A080(gobj);
    tmce_osdact_OoShield(r, gobj);
}

/// Replaces ftCo_GuardOff_IASA (`function`). GuardOff - Display OOS Frame
/// Count.asm (+0x100, the epilogue): r3 is 1 when a check fired, else the
/// result of the last check (ftCo_800CB024).
void tm_osdact_GuardOff_IASA(Fighter_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    bool r;

    if (fp->mv.co.guard.x1C &&
        (ftCo_SpecialS_CheckInput(gobj) || ftCo_Attack100_CheckInput(gobj) ||
         ftCo_800D6824(gobj) || ftCo_800D68C0(gobj) ||
         ftCo_Catch_CheckInput(gobj) || ftCo_AttackS4_CheckInput(gobj) ||
         ftCo_AttackHi4_CheckInput(gobj) || ftCo_AttackLw4_CheckInput(gobj) ||
         ftCo_AttackS3_CheckInput(gobj) || ftCo_AttackHi3_CheckInput(gobj) ||
         ftCo_AttackLw3_CheckInput(gobj) || ftCo_Attack1_CheckInput(gobj)))
    {
        r = true;
    } else {
        r = tm_ucf_8009980C(gobj) || ftCo_800CB024(gobj);
    }
    tmce_osdact_OoShield(r, gobj);
}

/* ======================================================================
 * Act OOTumble/ (static function 0x80005504, Act OoHitstun).
 */

/// Wraps `ftCo_800DEF38` in Fighter_procAnim (+0x7FC). Increment Post
/// Hitstun Count.asm runs at the next instruction (+0x800).
void tm_osdact_ProcAnimDamage(Fighter_GObj* gobj)
{
    ftCo_800DEF38(gobj);
    tmce_osdact_PostHitstunCount(gobj);
}

/// Wraps `ftCo_800CB870` (double jump) in ftCo_Damage_Anim (+0x108) and
/// ftCo_DamageFly_Anim (+0x178). DamageLightHit - Check For Interrupt -
/// Aerial Jump.asm (+0x10C) and DamageFlyTop - CheckForInterrupt.asm
/// (+0x17C) follow it.
bool tm_osdact_DamageDoubleJump(Fighter_GObj* gobj)
{
    bool r = ftCo_800CB870(gobj);
    tmce_osdact_OoHitstun(r, gobj);
    return r;
}

/// Wraps `ftCo_Fall_IASA_Inner` in ftCo_Damage_IASA (+0x9C). DamageLightHit
/// - Check ForInterrupt.asm (+0xA0) follows it.
bool tm_osdact_DamageFallIasa(Fighter_GObj* gobj)
{
    bool r = ftCo_Fall_IASA_Inner(gobj);
    tmce_osdact_OoHitstun(r, gobj);
    return r;
}

/// Replaces the `ftCo_Wait_IASA` call in ftCo_Damage_IASA (+0xA8).
/// DamageLightHit - Check ForInterrupt 2.asm (+0xAC) reads r3 after it:
/// ftCo_Wait_IASA is void, and leaves 1 in r3 when one of its checks fired,
/// else the last check's result. Same checks, same order, as vanilla
/// ftCo_Wait_IASA.
void tm_osdact_DamageWaitIasa(Fighter_GObj* gobj)
{
    bool r = ftCo_SpecialS_CheckInput(gobj) ||
             ftCo_Attack100_CheckInput(gobj) || ftCo_800D6824(gobj) ||
             ftCo_800D68C0(gobj) || ftCo_Catch_CheckInput(gobj) ||
             ftCo_AttackS4_CheckInput(gobj) ||
             ftCo_AttackHi4_CheckInput(gobj) ||
             ftCo_AttackLw4_CheckInput(gobj) ||
             ftCo_AttackS3_CheckInput(gobj) ||
             ftCo_AttackHi3_CheckInput(gobj) ||
             ftCo_AttackLw3_CheckInput(gobj) ||
             ftCo_Attack1_CheckInput(gobj) || tm_ucf_80099794(gobj) ||
             ftCo_80091A4C(gobj) || ftFx_AppealS_CheckInput(gobj) ||
             ftCo_800DE9D8(gobj) || ftCo_Jump_CheckInput(gobj) ||
             ftCo_Dash_CheckInput(gobj) || ftCo_800D5FB0(gobj) ||
             ftCo_Turn_CheckInput(gobj) || ftCo_Walk_CheckInput(gobj);
    tmce_osdact_OoHitstun(r, gobj);
}

/*
 * DamageFall - Check For Interrupt.asm (ftCo_DamageFall_IASA+0xFC, the
 * epilogue): r3 = 1 if a check fired, set to 1 if the fighter is now in
 * Fall, else the value left by the last call. Slippi patches inside
 * ftCo_DamageFall_IASA (+0xCC), so it cannot be replaced; instead each call
 * that can end the function is wrapped, and the display runs after the one
 * that does (nothing runs after it).
 */

/// A RETURN_IF check in ftCo_DamageFall_IASA: ends the function if true.
static bool damageFallCheck(Fighter_GObj* gobj, bool r)
{
    if (r) {
        tmce_osdact_OoHitstun(1, gobj);
    }
    return r;
}

/// ftCo_DamageFall_IASA+0x2C
bool tm_osdact_DFSpecialAir(Fighter_GObj* gobj)
{
    return damageFallCheck(gobj, ftCo_SpecialAir_CheckInput(gobj));
}

/// ftCo_DamageFall_IASA+0x40
bool tm_osdact_DF80095328(Fighter_GObj* gobj, bool* arg1)
{
    return damageFallCheck(gobj, ftCo_80095328(gobj, arg1));
}

/// ftCo_DamageFall_IASA+0x50
bool tm_osdact_DF800D7100(Fighter_GObj* gobj)
{
    return damageFallCheck(gobj, ftCo_800D7100(gobj));
}

/// ftCo_DamageFall_IASA+0x60
bool tm_osdact_DF800C3B10(Fighter_GObj* gobj)
{
    return damageFallCheck(gobj, ftCo_800C3B10(gobj));
}

/// ftCo_DamageFall_IASA+0x70
bool tm_osdact_DFAttackAir(Fighter_GObj* gobj)
{
    return damageFallCheck(gobj, ftCo_AttackAir_CheckItemThrowInput(gobj));
}

/// ftCo_DamageFall_IASA+0x80
bool tm_osdact_DF800D705C(Fighter_GObj* gobj)
{
    return damageFallCheck(gobj, ftCo_800D705C(gobj));
}

/// ftCo_DamageFall_IASA+0x90
bool tm_osdact_DF800CB870(Fighter_GObj* gobj)
{
    return damageFallCheck(gobj, ftCo_800CB870(gobj));
}

/// ftCo_DamageFall_IASA+0xD8: tumble wiggle into Fall, then return. r3 is
/// left as the fighter pointer by ftCo_Fall_Enter, so the asm displays only
/// because of its "now in Fall" check.
void tm_osdact_DFFallEnter(Fighter_GObj* gobj)
{
    ftCo_Fall_Enter(gobj);
    tmce_osdact_OoHitstun(tmce_osdact_IsInFall(gobj) ? 1 : 0, gobj);
}

/// ftCo_DamageFall_IASA+0xE4
bool tm_osdact_DF800C5DDC(Fighter_GObj* gobj)
{
    return damageFallCheck(gobj, ftCo_800C5DDC(gobj));
}

/// ftCo_DamageFall_IASA+0xF4, the last call: its result is r3 at the
/// epilogue either way.
bool tm_osdact_DF800C5CD4(Fighter_GObj* gobj)
{
    bool r = ftCo_800C5CD4(gobj);
    tmce_osdact_OoHitstun((r || tmce_osdact_IsInFall(gobj)) ? 1 : 0, gobj);
    return r;
}

/* ======================================================================
 * Act Oo Float.asm
 */

/// Replaces ftPe_8011BE80 (`function`), Peach's "aerial out of float" check.
/// Act Oo Float.asm runs at +0x3C: A pressed or a C-stick aerial, before
/// the float time check.
bool tm_osdact_PeachFloatAttack(HSD_GObj* gobj)
{
    u8 _[8];
    Fighter* fp = GET_FIGHTER(gobj);
    if (fp->input.pressed_buttons & HSD_PAD_A || ftCo_800DF478(fp)) {
        tmce_osdact_OoFloat(fp);
        if (fp->u.pe.x4 > 0) {
            if (ftCo_AttackAir_GetMsidFromCStick(fp) - 65U <= 1) {
                if (fp->item_gobj != NULL && it_8026B30C(fp->item_gobj) == 3)
                {
                    ftCo_800CDDA0(gobj);
                    return true;
                }
            }
            ftPe_8011BF34(gobj);
            return true;
        }
    }
    return false;
}
