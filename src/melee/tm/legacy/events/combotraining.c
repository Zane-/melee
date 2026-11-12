/**
 * @file
 * TM-CE legacy event Combo Training (Custom Event Code - Rewrite.asm, lines
 * 3930-5662): combo the CPU. Options set how it DIs, SDIs, techs, acts out
 * of hitstun and mashes out of grabs; it resets 30 frames after it escapes.
 * D-pad right saves a new start (CPU in Wait), left loads it, down moves the
 * CPU in front of you, L + D-pad changes its percent. The score is the
 * current combo; the best combo is kept as the high score.
 */
#include "../legacy.h"

#include <melee/ft/ftcolanimlist.h>
#include <melee/ft/ftcoll.h>
#include <melee/ft/kinds/ftCommon/ftCo_0A01.h>
#include <melee/ft/types.h>
#include <melee/if/ifstock.h>
#include <melee/mn/types.h>
#include <melee/pl/pl_040D.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>

/// gm/gmevent.c static (-0x4EA8(r13)): [0] current score, [1] best this
/// session (saved as the event's high score by the framework's exit
/// function).
extern u16 staffInfo[2];

/* fighter offsets not in legacy.h */
#define OFST_FT_KIND 0x4         /* s32 internal character id */
#define OFST_FT_LAND_IASA 0x1F4  /* f32 landing interrupt frame */
#define OFST_FT_STICK_X 0x620    /* f32 */
#define OFST_FT_STICK_Y 0x624    /* f32 */
#define OFST_FT_PREV_STICK_X 0x628
#define OFST_FT_PREV_STICK_Y 0x62C
#define OFST_FT_PREV_BUTTONS 0x65C
#define OFST_FT_TRIGGER 0x668    /* u32 buttons pressed this frame */
#define OFST_FT_STICK_TIMER 0x670 /* u8 */
#define OFST_FT_LR_FRAMES 0x680  /* u8 frames since L/R pressed */
#define OFST_FT_LR_LOCKOUT 0x684 /* u8 */
#define OFST_FT_THROW_ANGLE 0xE14 /* s32, P1 throw hitbox (0xDF4 + 0x20) */
#define OFST_FT_KB_ANGLE 0x1848  /* s32 */
#define OFST_FT_INTANG 0x1988    /* s32 */
#define OFST_FT_STICK_FIRST 0x1A50 /* s8 */
#define OFST_FT_HITLAG_LEFT 0x195C /* f32 */
#define OFST_FT_FLAGS_221A 0x221A /* 0x20: in hitlag */
#define OFST_FT_FLAGS_221C 0x221C /* 0x02: in hitstun */

#define CKIND_FOX 0x1
#define CKIND_DK 0x3
#define CKIND_JIGGLYPUFF 0xF
#define CKIND_FALCO 0x16

#define ASID_JUMP_AERIAL_F 0x1B
#define ASID_JUMP_AERIAL_B 0x1C
#define ASID_FALL 0x1D
#define ASID_DAMAGE_FALL 0x26
#define ASID_LANDING 0x2A
#define ASID_DAMAGE_HI1 0x4B
#define ASID_DAMAGE_FLY_ROLL 0x5B
#define ASID_DAMAGE_FALL_LIGHT 0x56
#define ASID_DOWN_WAIT_U 0xB8
#define ASID_DOWN_WAIT_D 0xC0
#define ASID_GUARD 0xB6
#define ASID_CAPTURE_PULLED_HI 0xDF
#define ASID_CAPTURE_FOOT 0xE8
#define ASID_ESCAPE_AIR 0xEC
#define ASID_THROWN_F 0xEF
#define ASID_THROWN_LW_WOMEN 0xF3
#define ASID_OTTOTTO 0xF5
#define ASID_CLIFF_WAIT 0xFD
#define ASID_SHOULDERED_WAIT 0x10A
#define ASID_SHOULDERED_TURN 0x10E
#define ASID_THROWN_FF 0x10F
#define ASID_THROWN_F_LW 0x112
#define ASID_CAPTURE_KOOPA 0x116
#define ASID_CAPTURE_WAIT_KOOPA 0x118
#define ASID_CAPTURE_KOOPA_AIR 0x11B
#define ASID_CAPTURE_WAIT_KOOPA_AIR 0x11D
#define ASID_PURIN_JUMP 0x155
#define ASID_FOX_SHINE_GROUND 0x168
#define ASID_PURIN_REST 0x171

/* event data offsets */
#define OFST_TIMER 0x4 /* s32, reset countdown (0 = none) */
#define OFST_STATE 0x8 /* u8 event state */

enum { STATE_IDLE, STATE_DI_AND_TECH, STATE_POST_HITSTUN };

/* menu options */
#define OPT_DI 0
#define OPT_SDI 1
#define OPT_TECH 2
#define OPT_POST_HITSTUN 3
#define OPT_GRAB_MASH 4

enum {
    DI_RANDOM,
    DI_SURVIVAL,
    DI_COMBO,
    DI_SLIGHT_RANDOM,
    DI_SLIGHT_INWARDS,
    DI_DOWN_AND_AWAY,
    DI_NONE,
};
enum { SDI_33, SDI_66, SDI_ALWAYS, SDI_NONE };

/// asm ComboTrainingWindowInfo: 5 windows; DI 7 options, SDI 4, Tech 5,
/// Post Hitstun 3, Grab Mash-Out 3.
static const u8 window_info[] = { 0x04, 0x06, 0x03, 0x04, 0x02, 0x02, 0x00,
                                  0x00 };

/// asm ComboTrainingWindowText. 0x8193 is a full-width '%' and 0x815E a
/// full-width '/' (Shift JIS), as in the asm.
static const char window_text[] = "DI Behavior\0"
                                  "Random DI\0"
                                  "Survival DI\0"
                                  "Combo DI\0"
                                  "Slight DI Random\0"
                                  "Slight DI Towards\0"
                                  "Down and Away DI\0"
                                  "No DI\0"
                                  "SDI Behavior\0"
                                  "33\x81\x93"
                                  " Chance to SDI\0"
                                  "66\x81\x93"
                                  " Chance to SDI\0"
                                  "Always SDI\0"
                                  "No SDI\0"
                                  "Tech Option\0"
                                  "Random\0"
                                  "Missed Tech\0"
                                  "Tech In Place\0"
                                  "Tech In\0"
                                  "Tech Away\0"
                                  "Post Hitstun Action\0"
                                  "Airdodge\x81\x5e"
                                  "Spotdodge\0"
                                  "Invincible\0"
                                  "Attack\0"
                                  "Grab Mash-Out\0"
                                  "Random Mash\0"
                                  "Frame Perfect\0"
                                  "No Mash-Out\0";

/// asm ComboTrainingAttackList: per internal character (the CPU), the
/// out-of-hitstun attack; high nibble grounded, low nibble aerial.
/// 0 A, 1 forward A, 2 back A, 3 down A, 4 up A, 5 down smash, 6 up B,
/// 7 down B.
static const u8 attack_list[] = {
    0x00, 0x70, 0x04, 0x66, 0x02, 0x66, 0x00, 0x00, 0x30, 0x00,
    0x03, 0x03, 0x04, 0x66, 0x00, 0x73, 0x30, 0x00, 0x01, 0x52,
    0x00, 0x00, 0x70, 0x00, 0x66, 0x04, 0x00, 0xFF,
};

static bool InHitlag(Fighter* fp)
{
    return (LG_U8(fp, OFST_FT_FLAGS_221A) & 0x20) != 0;
}

static bool InHitstun(Fighter* fp)
{
    return (LG_U8(fp, OFST_FT_FLAGS_221C) & 0x02) != 0;
}

static bool InRange(s32 v, s32 lo, s32 hi)
{
    return v >= lo && v <= hi;
}

/// asm ComboTrainingCheckForThrowAngle: P1's throw angle while the CPU is
/// in a normal Thrown state, else -1.
static s32 CheckForThrowAngle(Fighter* p1, Fighter* p2)
{
    if (InRange(LG_S32(p2, LG_FT_STATE), ASID_THROWN_F,
                ASID_THROWN_LW_WOMEN))
    {
        return LG_S32(p1, OFST_FT_THROW_ANGLE);
    }
    return -1;
}

/// asm ComboTrainingCheckExitStates: the CPU is actionable again.
static bool CheckExitStates(Fighter* p2)
{
    s32 state = LG_S32(p2, LG_FT_STATE);

    switch (state) {
    case LG_ASID_WAIT:
    case ASID_FALL:
    case ASID_JUMP_AERIAL_F:
    case ASID_CLIFF_WAIT:
    case ASID_OTTOTTO:
    case ASID_JUMP_AERIAL_B:
        return true;
    case ASID_LANDING:
        if (LG_F32(p2, LG_FT_ANIM_FRAME) >= LG_F32(p2, OFST_FT_LAND_IASA)) {
            return true;
        }
        break;
    }
    return LG_S32(p2, OFST_FT_KIND) == CKIND_JIGGLYPUFF &&
           state == ASID_PURIN_JUMP;
}

/// The asm's "point towards the opponent" step: dir * (stick X as an
/// unsigned byte), stored as a byte.
static void PointTowardsP1(Fighter* p1, Fighter* p2)
{
    s32 dir = tm_legacy_GetDirectionInRelationToP1(p1, p2);
    LG_S8(p2, LG_FT_CPU_ANALOG_X) =
        (s8) (dir * (s32) LG_U8(p2, LG_FT_CPU_ANALOG_X));
}

/// Random magnitude in [min, min + range) with a random sign.
static s8 RandomAxis(int range, int min)
{
    s32 v = HSD_Randi(range) + min;
    if (HSD_Randi(2) != 0) {
        v = -v;
    }
    return (s8) v;
}

/// asm ComboTrainingDecideStickAngle.
static void DecideStickAngle(Fighter* p1, Fighter* p2, int di)
{
    s32 angle, orig, x, y;

    LG_S8(p2, LG_FT_CPU_ANALOG_X) = 0;
    LG_S8(p2, LG_FT_CPU_ANALOG_Y) = 0;

    if (di < DI_RANDOM || di > DI_NONE) {
        di = DI_RANDOM;
    }
    if (di == DI_RANDOM) {
        switch (HSD_Randi(6)) {
        case 0: /* truly random */
            LG_S8(p2, LG_FT_CPU_ANALOG_X) = RandomAxis(127 - 36, 36);
            LG_S8(p2, LG_FT_CPU_ANALOG_Y) = RandomAxis(127 - 36, 36);
            return;
        case 1:
            di = DI_COMBO;
            break;
        case 2:
            di = DI_SURVIVAL;
            break;
        case 3:
            di = DI_SLIGHT_RANDOM;
            break;
        case 4:
            di = DI_DOWN_AND_AWAY;
            break;
        default:
            return; /* no DI */
        }
    }

    switch (di) {
    case DI_SLIGHT_RANDOM:
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = RandomAxis(66 - 36, 36);
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = RandomAxis(66 - 36, 36);
        return;

    case DI_SLIGHT_INWARDS:
        /* 86-104 against P1's facing direction */
        x = HSD_Randi(19) + 86;
        LG_S8(p2, LG_FT_CPU_ANALOG_X) =
            (s8) (x * (s32) -LG_F32(p1, LG_FT_FACING));
        return;

    case DI_SURVIVAL:
        angle = CheckForThrowAngle(p1, p2);
        if (angle == -1) {
            angle = LG_S32(p2, OFST_FT_KB_ANGLE);
        }
        if (angle == 361) { /* Sakurai angle */
            angle = 45;
        }
        if (angle >= 90 && angle < 269) {
            angle -= 90;
            if (angle <= 0) {
                angle += 360;
            }
        } else {
            angle += 90;
            if (angle >= 360) {
                angle -= 360;
            }
        }
        tm_legacy_ConvertAngle(angle, &x, &y);
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = (s8) x;
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = (s8) y;
        PointTowardsP1(p1, p2);
        return;

    case DI_COMBO:
        angle = CheckForThrowAngle(p1, p2);
        if (angle == -1) {
            angle = LG_S32(p2, OFST_FT_KB_ANGLE);
        }
        orig = angle; /* before the Sakurai angle fix, as in the asm */
        if (angle == 361) {
            angle = 45;
        }
        if (angle >= 90 && angle < 269) {
            angle += 90;
            if (angle >= 360) {
                angle -= 360;
            }
        } else {
            angle -= 90;
            if (angle <= 0) {
                angle += 360;
            }
        }
        tm_legacy_ConvertAngle(angle, &x, &y);
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = (s8) x;
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = (s8) y;

        if (InRange(LG_S32(p2, LG_FT_STATE), ASID_THROWN_F,
                    ASID_THROWN_LW_WOMEN))
        {
            /* In a throw: X along (angle < 90) or against P1's facing
             * direction. The asm's "angle >= 90 and < 269" test compares
             * the action state instead of the angle, so >= 90 is always
             * "against"; kept. */
            s32 ax = LG_S8(p2, LG_FT_CPU_ANALOG_X);
            bool facing_right = LG_F32(p1, LG_FT_FACING) > 0.0F;
            bool along = orig < 90;
            if (ax < 0) {
                ax = -ax;
            }
            if (along != facing_right) {
                ax = -ax;
            }
            LG_S8(p2, LG_FT_CPU_ANALOG_X) = (s8) ax;
        } else {
            PointTowardsP1(p1, p2);
        }
        return;

    case DI_DOWN_AND_AWAY:
        LG_S8(p2, LG_FT_CPU_ANALOG_X) =
            (s8) (tm_legacy_GetDirectionInRelationToP1(p1, p2) * 89);
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -89;
        LG_S8(p2, LG_FT_CPU_CSTICK_Y) = -127;
        return;

    default: /* DI_NONE */
        return;
    }
}

/// asm ComboTrainingGetChanceToTech and the tech options.
static void Tech(Fighter* p1, Fighter* p2, u8* menu)
{
    int option = LG_MENU_OPTION(menu, OPT_TECH);

    if (option < 0 || option > 4) {
        option = 0;
    }
    if (option == 0) { /* random */
        LG_U8(p2, OFST_FT_LR_FRAMES) = 1;
        LG_U8(p2, OFST_FT_LR_LOCKOUT) = 0xFF;
        if (InHitlag(p2)) {
            return;
        }
        switch (HSD_Randi(4)) {
        case 0: /* in place */
            LG_S8(p2, LG_FT_CPU_ANALOG_X) = 0;
            LG_S8(p2, LG_FT_CPU_ANALOG_Y) = 0;
            return;
        case 1:
            LG_S8(p2, LG_FT_CPU_ANALOG_X) = -127;
            return;
        case 2:
            LG_S8(p2, LG_FT_CPU_ANALOG_X) = 127;
            return;
        default:
            option = 1; /* miss */
            break;
        }
    }
    if (option == 1) { /* miss: no L, tech window spent */
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0;
        LG_U8(p2, OFST_FT_LR_FRAMES) = 0xFF;
        LG_U8(p2, OFST_FT_LR_LOCKOUT) = 0;
        return;
    }

    /* tech in place / towards / away: hold L, keep the window open */
    LG_U32(p2, LG_FT_CPU_BUTTONS) = 0xC0;
    LG_U8(p2, OFST_FT_LR_FRAMES) = 0;
    LG_U8(p2, OFST_FT_LR_LOCKOUT) = 0xFF;
    if (InHitlag(p2)) {
        return;
    }
    switch (option) {
    case 2:
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = 0;
        break;
    case 3:
        LG_S8(p2, LG_FT_CPU_ANALOG_X) =
            (s8) (-tm_legacy_GetDirectionInRelationToP1(p1, p2) * 127);
        break;
    case 4:
        LG_S8(p2, LG_FT_CPU_ANALOG_X) =
            (s8) (tm_legacy_GetDirectionInRelationToP1(p1, p2) * 127);
        break;
    }
}

/// asm ComboTrainingMashOutOfGrab.
static void MashOutOfGrab(Fighter* p2, u8* menu)
{
    int option = LG_MENU_OPTION(menu, OPT_GRAB_MASH);
    bool analog = false;

    if (option == 2) { /* no mash */
        return;
    }
    if (option == 1) { /* frame perfect */
        analog = true;
    } else {
        /* random: 0-7 nothing, 8 button, 9 stick and button */
        s32 r = HSD_Randi(10);
        if (r <= 7) {
            return;
        }
        analog = r != 8;
    }
    if (analog) {
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = 127;
        LG_S8(p2, OFST_FT_STICK_FIRST) = -1; /* stick pushed this frame */
    }
    LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x100;
    LG_U32(p2, OFST_FT_PREV_BUTTONS) = 0;
}

/// The CPU state checks that send it to MashOutOfGrab.
static bool IsGrabbed(Fighter* p1, s32 state)
{
    if (InRange(state, ASID_SHOULDERED_WAIT, ASID_SHOULDERED_TURN)) {
        return true;
    }
    if (LG_S32(p1, OFST_FT_KIND) == CKIND_DK &&
        (state == ASID_THROWN_F || state == ASID_THROWN_FF))
    {
        return true;
    }
    return InRange(state, ASID_CAPTURE_KOOPA, ASID_CAPTURE_WAIT_KOOPA) ||
           InRange(state, ASID_CAPTURE_KOOPA_AIR,
                   ASID_CAPTURE_WAIT_KOOPA_AIR) ||
           InRange(state, ASID_CAPTURE_PULLED_HI, ASID_CAPTURE_FOOT);
}

static void SetTimerIfUnset(u8* data)
{
    if (LG_S32(data, OFST_TIMER) <= 0) {
        LG_S32(data, OFST_TIMER) = 30;
    }
}

/// asm ComboTrainingPostHitstun_GiveInvinc_ApplyInvinc.
static void ApplyInvincibility(HSD_GObj* p2g, u8* data)
{
    ftColl_8007B760((Fighter_GObj*) p2g, 30);
    ftCo_800C0408((Fighter_GObj*) p2g);
    SetTimerIfUnset(data);
}

/// asm ComboTrainingPostHitstun_Attack.
static void PostHitstunAttack(HSD_GObj* p2g, Fighter* p1, Fighter* p2,
                              u8* data)
{
    s32 kind = LG_S32(p2, OFST_FT_KIND);
    u8 entry = kind >= 0 && kind < (s32) sizeof(attack_list)
                   ? attack_list[kind]
                   : 0;
    int attack;

    LG_U32(p2, OFST_FT_PREV_BUTTONS) = 0;
    attack = LG_S32(p2, LG_FT_AIRBORNE) != 0 ? entry & 0xF : entry >> 4;

    switch (attack) {
    default: /* A */
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x100;
        break;
    case 1: /* forward A */
        LG_S8(p2, LG_FT_CPU_ANALOG_X) =
            (s8) (-tm_legacy_GetDirectionInRelationToP1(p1, p2) * 60);
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x100;
        break;
    case 2: /* back A */
        LG_S8(p2, LG_FT_CPU_ANALOG_X) =
            (s8) (tm_legacy_GetDirectionInRelationToP1(p1, p2) * 60);
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x100;
        break;
    case 3: /* "down A": the asm stores +60 (up), kept */
    case 4: /* up A */
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = 60;
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x100;
        break;
    case 5: /* down smash */
        LG_S8(p2, LG_FT_CPU_CSTICK_Y) = -127;
        break;
    case 6: /* up B */
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = 127;
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x200;
        break;
    case 7: /* down B */
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -127;
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x200;
        break;
    }

    /* invincible once the attack is out (hard-coded shine and rest) */
    if (tm_legacy_CheckForActiveHitboxes(p2g)) {
        ApplyInvincibility(p2g, data);
        return;
    }
    if ((kind == CKIND_FOX || kind == CKIND_FALCO) &&
        LG_S32(p2, LG_FT_STATE) == ASID_FOX_SHINE_GROUND)
    {
        ApplyInvincibility(p2g, data);
    } else if (kind == CKIND_JIGGLYPUFF &&
               LG_S32(p2, LG_FT_STATE) == ASID_PURIN_REST)
    {
        ApplyInvincibility(p2g, data);
    }
}

/// asm ComboTrainingPostHitstun_AirdodgeSpotdodge.
static void PostHitstunDodge(Fighter* p2, u8* data)
{
    s32 state;

    if (LG_S32(p2, OFST_FT_INTANG) != 0) { /* dodge started */
        SetTimerIfUnset(data);
        return;
    }

    state = LG_S32(p2, LG_FT_STATE);
    if (CheckExitStates(p2) && state != ASID_FALL && state != ASID_LANDING &&
        state != LG_ASID_WAIT)
    {
        SetTimerIfUnset(data);
    }

    if (LG_S32(p2, LG_FT_AIRBORNE) != 0) {
        if (state != ASID_DAMAGE_FALL_LIGHT) {
            if (InRange(state, ASID_DAMAGE_HI1, ASID_DAMAGE_FLY_ROLL)) {
                LG_S8(p2, LG_FT_CPU_ANALOG_X) = 127; /* wiggle out */
                return;
            }
            if (state != ASID_FALL) {
                return;
            }
        }
        /* airdodge */
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = 0;
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0xC0;
        LG_U32(p2, OFST_FT_PREV_BUTTONS) = 0;
        return;
    }

    /* grounded and actionable: spotdodge */
    if (state != LG_ASID_WAIT && state != ASID_GUARD) {
        if (state != ASID_LANDING) {
            return;
        }
        if (LG_F32(p2, LG_FT_ANIM_FRAME) < LG_F32(p2, OFST_FT_LAND_IASA)) {
            return;
        }
    }
    LG_U32(p2, OFST_FT_PREV_BUTTONS) = 0;
    LG_U32(p2, LG_FT_CPU_BUTTONS) = 0xC0;
    LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -127;
}

/// asm ComboTrainingPostHitstun.
static void PostHitstun(HSD_GObj* p2g, Fighter* p1, Fighter* p2, u8* menu,
                        u8* data)
{
    switch (LG_MENU_OPTION(menu, OPT_POST_HITSTUN)) {
    case 0:
        PostHitstunDodge(p2, data);
        return;
    case 2:
        PostHitstunAttack(p2g, p1, p2, data);
        return;
    default: /* 1: invincible, jumping if in the air */
        if (LG_S32(p2, LG_FT_AIRBORNE) != 0) {
            LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x800;
            LG_U32(p2, OFST_FT_TRIGGER) = 0;
        }
        ApplyInvincibility(p2g, data);
        return;
    }
}

/// asm ComboTrainingInputDIAndTech (the CPU is being comboed): DI, SDI,
/// tech, mash out of grabs, or move on to the post-hitstun state once it
/// can act.
static void InputDIAndTech(HSD_GObj* p2g, Fighter* p1, Fighter* p2, u8* menu,
                           u8* data)
{
    s32 state;

    if (CheckExitStates(p2)) {
        LG_U8(data, OFST_STATE) = STATE_POST_HITSTUN;
        PostHitstun(p2g, p1, p2, menu, data);
        return;
    }

    state = LG_S32(p2, LG_FT_STATE);
    if (state == ASID_DOWN_WAIT_U || state == ASID_DOWN_WAIT_D) {
        /* missed tech: getup attack, roll left/right or stand */
        switch (HSD_Randi(4)) {
        case 0:
            LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x100;
            break;
        case 1:
            LG_S8(p2, LG_FT_CPU_ANALOG_X) = -127;
            break;
        case 2:
            LG_S8(p2, LG_FT_CPU_ANALOG_X) = 127;
            break;
        default:
            LG_S8(p2, LG_FT_CPU_ANALOG_Y) = 127;
            break;
        }
        return;
    }

    if (IsGrabbed(p1, state)) {
        MashOutOfGrab(p2, menu);
        return;
    }

    if (InHitlag(p2)) {
        int di;
        int sdi;

        /* last frame of hitlag only */
        if (LG_F32(p2, OFST_FT_HITLAG_LEFT) != 1.0F) {
            return;
        }
        /* attacks never get "slight DI inwards"; it becomes random DI */
        di = LG_MENU_OPTION(menu, OPT_DI);
        if (di == DI_SLIGHT_INWARDS) {
            di = DI_RANDOM;
        }
        DecideStickAngle(p1, p2, di);

        sdi = LG_MENU_OPTION(menu, OPT_SDI);
        if (sdi == SDI_ALWAYS) {
            return;
        }
        if (sdi != SDI_NONE) {
            s32 limit = sdi == SDI_66 ? 1 : 0;
            if (HSD_Randi(3) <= limit) {
                Tech(p1, p2, menu);
                return;
            }
        }
        /* no SDI: the stick doesn't move this frame */
        LG_F32(p2, OFST_FT_STICK_X) = ftCo_GetCpuLStickX(p2);
        LG_F32(p2, OFST_FT_STICK_Y) = ftCo_GetCpuLStickY(p2);
        Tech(p1, p2, menu);
        return;
    }

    /* being thrown: DI the throw */
    if (!(LG_S32(p1, OFST_FT_KIND) == CKIND_DK &&
          (state == ASID_THROWN_F || state == ASID_THROWN_FF)) &&
        (InRange(state, ASID_THROWN_F, ASID_THROWN_LW_WOMEN) ||
         InRange(state, ASID_THROWN_FF, ASID_THROWN_F_LW)))
    {
        DecideStickAngle(p1, p2, LG_MENU_OPTION(menu, OPT_DI));
        return;
    }

    /* in a damage state */
    if (state != ASID_DAMAGE_FALL &&
        !InRange(state, ASID_DAMAGE_HI1, ASID_DAMAGE_FLY_ROLL))
    {
        return;
    }

    if (LG_S32(p2, LG_FT_AIRBORNE) != 0) {
        if (InHitstun(p2)) {
            Tech(p1, p2, menu);
            return;
        }
        /* out of hitstun in the air */
        if (LG_MENU_OPTION(menu, OPT_POST_HITSTUN) == 0) {
            /* wiggle out, then airdodge */
            LG_S8(p2, LG_FT_CPU_ANALOG_X) = 127;
            LG_U32(p2, OFST_FT_PREV_STICK_X) = 0;
            LG_U32(p2, OFST_FT_PREV_STICK_Y) = 0;
            LG_U8(p2, OFST_FT_STICK_TIMER) = 255;
        }
        LG_U8(data, OFST_STATE) = STATE_POST_HITSTUN;
        PostHitstun(p2g, p1, p2, menu, data);
        return;
    }

    /* grounded light damage */
    if (InHitstun(p2)) {
        return;
    }
    if (LG_MENU_OPTION(menu, OPT_POST_HITSTUN) == 0) { /* spotdodge */
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0xC0;
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -127;
    }
    LG_U8(data, OFST_STATE) = STATE_POST_HITSTUN;
    PostHitstun(p2g, p1, p2, menu, data);
}

/// "Combo Training THINK FUNCT".
static void ComboTrainingThink(HSD_GObj* event)
{
    u8* data = event->user_data;
    u8* menu = LG_PTR(data, LG_EVDATA_MENU);
    TmLegacySaveState* ss = (TmLegacySaveState*) (data + LG_EVDATA_SAVESTATE);
    HSD_GObj* gobj[4];
    Fighter* fp[4];
    Fighter* p1;
    Fighter* p2;
    s32 state;
    s32 timer;

    tm_legacy_GetAllPlayerPointers(gobj, fp);
    p1 = fp[0];
    p2 = fp[1];
    tm_legacy_StoreCPUTypeAndZeroInputs(p2);

    if (tm_legacy_CheckIfFirstFrame()) {
        tm_legacy_PlacePlayersCenterStage(tm_legacy_StageGetGroundID_Main());
        tm_legacy_RemoveFirstFrameInputs();
        tm_legacy_SaveState_Save(ss, true);
        ifStock_802FA2D0(staffInfo[0]);
    }

    /* score = current combo; keep the best */
    staffInfo[0] = pl_8004134C(0);
    if (staffInfo[0] > staffInfo[1]) {
        staffInfo[1] = staffInfo[0];
    }
    if (staffInfo[0] >= 1) {
        ifStock_802FA2D0(staffInfo[0]);
    }

    /* D-pad right only saves while idle with the CPU in Wait */
    if (!(LG_U32(p1, OFST_FT_TRIGGER) & 0x2) ||
        (LG_U8(data, OFST_STATE) == STATE_IDLE &&
         LG_S32(p2, LG_FT_STATE) == LG_ASID_WAIT))
    {
        if (tm_legacy_CheckForSaveAndLoad(ss) == 1) {
            LG_U8(data, OFST_STATE) = STATE_IDLE;
            LG_S32(data, OFST_TIMER) = 0;
        }
    }

    if (LG_U8(data, OFST_STATE) == STATE_IDLE) {
        tm_legacy_MoveCPU(gobj[0], gobj[1], ss);
    }
    tm_legacy_DPadCPUPercent(ss->backup[1]);
    tm_legacy_GiveFullShields();

    if (tm_legacy_IsAnyoneDead()) {
        goto restore;
    }

    /* was the CPU (grabbed or) hit again? Not in the first 6 frames of an
     * airdodge. */
    state = LG_S32(p2, LG_FT_STATE);
    if (!(state == ASID_ESCAPE_AIR &&
          6.0F >= LG_F32(p2, LG_FT_ANIM_FRAME)) &&
        (InRange(state, ASID_CAPTURE_PULLED_HI, ASID_CAPTURE_FOOT) ||
         (InHitlag(p2) &&
          InRange(state, ASID_DAMAGE_HI1, ASID_DAMAGE_FLY_ROLL))))
    {
        LG_U8(data, OFST_STATE) = STATE_DI_AND_TECH;
        InputDIAndTech(gobj[1], p1, p2, menu, data);
    } else {
        switch (LG_U8(data, OFST_STATE)) {
        case STATE_DI_AND_TECH:
            InputDIAndTech(gobj[1], p1, p2, menu, data);
            break;
        case STATE_POST_HITSTUN:
            PostHitstun(gobj[1], p1, p2, menu, data);
            break;
        }
    }

    /* asm ComboTrainingCheckToReset */
    timer = LG_S32(data, OFST_TIMER);
    if (timer <= 0) {
        goto exit;
    }
    LG_S32(data, OFST_TIMER) = --timer;
    if (timer != 0) {
        goto exit;
    }

restore:
    /* the asm loads twice */
    tm_legacy_SaveState_Load(ss);
    tm_legacy_SaveState_Load(ss);
    LG_U8(data, OFST_STATE) = STATE_IDLE;

exit:
    tm_legacy_ClearToggledOptions(menu);
    tm_legacy_UpdateAllGFX(gobj[1]);
}

/// "Combo Training LOAD FUNCT".
static void ComboTrainingLoad(void)
{
    StartOSDs();
    tm_legacy_CreateEventThinkFunction(ComboTrainingThink, 3, window_info,
                                       window_text);
    tm_legacy_InitializeHighScore();
}

/// "Combo Training HIJACK INFO".
void tm_legacy_ev_ComboTraining(TmLegacySetup* s)
{
    tm_legacy_InitializeMatch(s->event, s->md, -1, -1, 0, false);
    s->md->rules.on_match_start = ComboTrainingLoad;
}
