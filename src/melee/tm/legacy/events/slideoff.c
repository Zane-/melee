/**
 * @file
 * TM-CE legacy event Slide Off (Custom Event Code - Rewrite.asm, lines
 * 6122-6745): a CPU Marth up-throws you onto Pokemon Stadium's platform;
 * slide off it. If you tech or get up within reach, Marth up-tilts on your
 * vulnerable frame; below the platform he shields. Resets when Marth gets
 * hit, when you get hit again, or when you fly too high.
 */
#include "../legacy.h"

#include <melee/ft/fighter.h>
#include <melee/ft/ftcoll.h>
#include <melee/ft/types.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>

/* keep the asm's separate multiply and add (knockback scaling) */
#pragma fp_contract off

#define MARTH_EXT 0x9
#define STAGE_POKEMON_STADIUM 0x3

#define ASID_WAIT 0x0E
#define ASID_LANDING 0x2A
#define ASID_DAMAGE_HI1 0x4B
#define ASID_DAMAGE_FLY_TOP 0x5A
#define ASID_DAMAGE_FLY_ROLL 0x5B
#define ASID_DOWN_BOUND_U 0xB7
#define ASID_DOWN_WAIT_U 0xB8
#define ASID_DOWN_BOUND_D 0xBF
#define ASID_DOWN_WAIT_D 0xC0
#define ASID_PASSIVE_STAND_B 0xC9
#define ASID_THROW_HI 0xDD

#define BTN_R 0x20

#define RESET_TIMER 40
#define ANGLE_LO 83
#define ANGLE_HI 100
#define MAG_LO 65
#define MAG_HI 75
#define HITLAG_FRAMES 12
#define PERCENT_LO 40
#define PERCENT_HI 40
#define FRAMES_BEFORE_HITBOX 7

/* event data offsets */
#define OFST_STATE 0x0        /* u8 */
#define OFST_TIMER 0x1        /* u8 */
#define OFST_P1_STATE 0x2     /* u8 */
#define OFST_ATTACK_TIMER 0x3 /* u8 */

enum {
    STATE_HITSTUN,
    STATE_DETERMINE_ATTACK,
    STATE_ATTACK_THINK,
    STATE_SHIELD,
};

/* fighter fields only this event uses (asm offsets) */
#define FT_ATTRIBUTES 0x10C    /* ftData*, first word: attributes */
#define FT_WEIGHT 0x16C        /* f32 */
#define FT_LCANCEL 0x67F       /* u8 */
#define FT_HITLAG_FRAMES 0x195C /* f32 */
#define FT_FLAGS_2219 0x2219   /* u8, 0x04 */
#define FT_FLAGS_221A 0x221A   /* u8, 0x20 = in hitlag */
#define FT_FLAGS_221C 0x221C   /* u8, 0x02 = in hitstun */
#define FT_LANDING_INTERRUPT 0x1F4 /* f32 */
#define FT_LANDING_VAR 0x2340  /* s32 */

/// "SlideOffThink_Constants".
static const struct {
    f32 p1_x, p1_y, p2_x, p2_y;
    f32 uthrow_start_frame;
    f32 damage_fly_top_start_frame;
    f32 mag_scalar, mag_scalar2, mag_scalar3;
    f32 trigger_x_min, trigger_x_max, trigger_y_min, trigger_y_max;
} k = {
    -37.7F, 21.2F, -41.1F, 0.0F, 13.0F, 2.0F,
    0.1F,   1.0F,  0.4F,   -8.0F, 20.0F, 18.0F, 30.0F,
};

/// Vulnerable frame of each state from DownBoundU (0xB7) to PassiveStandB.
static const u8 vuln_frames[19] = {
    23,      /* DownBoundU */
    0,       /* DownWaitU */
    0,       /* DownDamageU */
    23,      /* DownStandU */
    27,      /* DownAttackU */
    20 - 1,  /* DownForwardU */
    30 - 3,  /* DownBackU */
    0xFF,    /* DownSpotU (unused state) */
    23,      /* DownBoundD */
    0,       /* DownWaitD */
    0,       /* DownDamageD */
    23,      /* DownStandD */
    27,      /* DownAttackD */
    20 - 1,  /* DownForwardD */
    30 - 3,  /* DownBackD */
    0xFF,    /* DownSpotD (unused state) */
    24 - 4,  /* Passive */
    23,      /* PassiveStandF */
    23,      /* PassiveStandB */
};

/// "SlideOffThink_AttackInputs": up tilt, then fastfall and L-cancel.
static const u8 attack_inputs[] = {
    0,  0x00, 0x00, 0x04, 0x00, 0,    0,    0, 0,   /* X */
    4,  0x00, 0x00, 0x00, 0x00, 0,    0,    0, 127, /* C-stick up */
    26, 0x00, 0x00, 0x00, 0x40, 0, 0x81, 0, 0,      /* L, down */
    0xFF,
};

static int ScaledMagnitude(Fighter* p1, int mag)
{
    f32 m = (f32) mag;
    f32 s = (LG_F32(p1, FT_WEIGHT) / k.mag_scalar - k.mag_scalar2) *
            k.mag_scalar3 * m;
    return (int) (m + s);
}

static void SetHitlag(Fighter* fp)
{
    LG_F32(fp, FT_HITLAG_FRAMES) = (f32) HITLAG_FRAMES;
    LG_U8(fp, FT_FLAGS_221A) |= 0x20;
    LG_U8(fp, FT_FLAGS_2219) |= 0x04;
}

/// "SlideOff_InitializePositions": Marth mid up-throw, P1 flying up out of
/// it with knockback scaled by weight, both in hitlag.
static void InitializePositions(HSD_GObj* p1g, Fighter* p1, HSD_GObj* p2g,
                                Fighter* p2)
{
    f32 weight;
    f32 speed;
    int mag_lo, mag_hi;

    LG_F32(p1, LG_FT_FACING) = -1.0F;
    LG_F32(p2, LG_FT_FACING) = 1.0F;

    LG_F32(p1, LG_FT_POS_X) = k.p1_x;
    LG_F32(p1, LG_FT_POS_Y) = k.p1_y;
    tm_legacy_UpdatePosition(p1g);
    tm_legacy_UpdateCameraBox(p1g);

    LG_F32(p2, LG_FT_POS_X) = k.p2_x;
    LG_F32(p2, LG_FT_POS_Y) = k.p2_y;
    tm_legacy_PlacePlayerOnGround(p2g);
    tm_legacy_UpdateCameraBox(p2g);

    /* up throw, its speed from P1's weight */
    weight = LG_F32(LG_PTR(LG_PTR(p1, FT_ATTRIBUTES), 0), 0x88);
    speed = 1.0F / (weight * LG_F32(p_ftCommonData, 0x37C));
    Fighter_ChangeMotionState(p2g, ASID_THROW_HI, 0, k.uthrow_start_frame,
                              speed, 0.0F, NULL);

    Fighter_ChangeMotionState(p1g, ASID_DAMAGE_FLY_TOP, 0x40,
                              k.damage_fly_top_start_frame, 1.0F, 0.0F, NULL);

    mag_lo = ScaledMagnitude(p1, MAG_LO);
    mag_hi = ScaledMagnitude(p1, MAG_HI);
    tm_legacy_EnterKnockback(p1g, ANGLE_LO, ANGLE_HI, mag_lo, mag_hi);
    LG_F32(p1, LG_FT_HITSTUN) = 50.0F;

    SetHitlag(p1);
    SetHitlag(p2);

    Player_SetHUDDamage(LG_U8(p1, LG_FT_SLOT),
                        HSD_Randi(PERCENT_HI - PERCENT_LO) + PERCENT_LO);
}

/// "SlideOffThink_DetermineAttackorShield".
static void DetermineAttackOrShield(u8* data, Fighter* p1, Fighter* p2)
{
    f32 p2_y = LG_F32(p2, LG_FT_POS_Y);
    f32 p1_y = LG_F32(p1, LG_FT_POS_Y);
    s32 state;
    int vuln;

    if (p1_y >= p2_y + k.trigger_y_max) {
        /* above the trigger box: reset soon */
        if (LG_U8(data, OFST_TIMER) <= 0) {
            LG_U8(data, OFST_TIMER) = 10;
        }
        return;
    }
    if (!(p1_y >= p2_y + k.trigger_y_min)) {
        /* below it: shield */
        LG_U8(data, OFST_STATE) = STATE_SHIELD;
        LG_U8(data, OFST_TIMER) = RESET_TIMER;
        LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_R;
        return;
    }

    state = LG_S32(p1, LG_FT_STATE);
    if (state >= ASID_DOWN_BOUND_U && state <= ASID_PASSIVE_STAND_B) {
        if (state == ASID_DOWN_WAIT_D || state == ASID_DOWN_WAIT_U ||
            state == ASID_DOWN_BOUND_D || state == ASID_DOWN_BOUND_U)
        {
            return;
        }
        /* attack so the up tilt hits on P1's vulnerable frame */
        vuln = vuln_frames[state - ASID_DOWN_BOUND_U] - FRAMES_BEFORE_HITBOX;
        if ((int) LG_U16(p1, LG_FT_TM_STATE_FRAMES) < vuln) {
            return;
        }
    }
    LG_U8(data, OFST_STATE) = STATE_ATTACK_THINK;
}

/// "SlideOffThink_AttackThink".
static void AttackThink(u8* data, HSD_GObj* p2g, Fighter* p2)
{
    s32 state;

    tm_legacy_PlaybackInputSequence(p2, attack_inputs,
                                    LG_U8(data, OFST_ATTACK_TIMER));
    LG_U8(p2, FT_LCANCEL) = 0; /* always L-cancel */
    /* hitboxes 1-3 make the slide off too hard */
    ftColl_8007AFC8(p2g, 1);
    ftColl_8007AFC8(p2g, 2);
    ftColl_8007AFC8(p2g, 3);

    if (LG_U8(data, OFST_ATTACK_TIMER) > 0) {
        state = LG_S32(p2, LG_FT_STATE);
        if (state == ASID_WAIT ||
            (state == ASID_LANDING && LG_S32(p2, FT_LANDING_VAR) != 0 &&
             (int) LG_U16(p2, LG_FT_TM_STATE_FRAMES) >=
                 (int) LG_F32(p2, FT_LANDING_INTERRUPT)))
        {
            LG_U8(data, OFST_STATE) = STATE_DETERMINE_ATTACK;
            LG_U8(data, OFST_ATTACK_TIMER) = 0;
            return;
        }
    }
    if (!(LG_U8(p2, FT_FLAGS_221A) & 0x20)) {
        LG_U8(data, OFST_ATTACK_TIMER)++;
    }
}

/// "Slide Off THINK FUNCT".
static void SlideOffThink(HSD_GObj* event)
{
    u8* data = event->user_data;
    TmLegacySaveState* ss = (TmLegacySaveState*) (data + LG_EVDATA_SAVESTATE);
    HSD_GObj* gobj[4];
    Fighter* fp[4];
    Fighter* p1;
    Fighter* p2;
    s32 state;
    int t;

    tm_legacy_GetAllPlayerPointers(gobj, fp);
    p1 = fp[0];
    p2 = fp[1];
    tm_legacy_StoreCPUTypeAndZeroInputs(p2);

    if (tm_legacy_CheckIfFirstFrame()) {
        InitializePositions(gobj[0], p1, gobj[1], p2);
        tm_legacy_RemoveFirstFrameInputs();
        tm_legacy_SaveState_Save(ss, true);
        LG_U8(data, OFST_STATE) = STATE_HITSTUN;
    }

    if (tm_legacy_IsAnyoneDead()) {
        goto restore;
    }

    /* failed: P1 back in hitstun (not hitlag) for 5+ frames */
    if (LG_U8(data, OFST_STATE) > STATE_HITSTUN &&
        !(LG_U8(p1, FT_FLAGS_221A) & 0x20) &&
        (LG_U8(p1, FT_FLAGS_221C) & 0x02) &&
        LG_U16(p1, LG_FT_TM_STATE_FRAMES) >= 5)
    {
        if (LG_U8(data, OFST_TIMER) > 0) {
            goto check_timer;
        }
        LG_U8(data, OFST_TIMER) = 10;
    }

    /* Marth got hit */
    state = LG_S32(p2, LG_FT_STATE);
    if (state >= ASID_DAMAGE_HI1 && state <= ASID_DAMAGE_FLY_ROLL &&
        LG_U8(data, OFST_TIMER) <= 0)
    {
        LG_U8(data, OFST_TIMER) = RESET_TIMER;
    }

    switch (LG_U8(data, OFST_STATE)) {
    case STATE_HITSTUN:
        if (LG_S32(p2, LG_FT_STATE) == ASID_THROW_HI) {
            break;
        }
        state = LG_S32(p1, LG_FT_STATE);
        if (state >= ASID_DOWN_BOUND_U && state <= ASID_PASSIVE_STAND_B) {
            LG_U8(data, OFST_STATE) = STATE_DETERMINE_ATTACK;
        }
        break;
    case STATE_DETERMINE_ATTACK:
        DetermineAttackOrShield(data, p1, p2);
        break;
    case STATE_ATTACK_THINK:
        AttackThink(data, gobj[1], p2);
        break;
    case STATE_SHIELD:
        LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_R;
        break;
    }

check_timer:
    t = LG_U8(data, OFST_TIMER);
    if (t <= 0) {
        return;
    }
    t--;
    LG_U8(data, OFST_TIMER) = t;
    if (t > 0) {
        return;
    }

restore:
    tm_legacy_SaveState_Load(ss);
    InitializePositions(gobj[0], p1, gobj[1], p2);
    LG_U8(data, OFST_STATE) = 0;
    LG_U8(data, OFST_TIMER) = 0;
    LG_U8(data, OFST_P1_STATE) = 0;
    LG_U8(data, OFST_ATTACK_TIMER) = 0;
}

/// "Slide Off LOAD FUNCT".
static void SlideOffLoad(void)
{
    StartOSDs();
    tm_legacy_CreateEventThinkFunction(SlideOffThink, 3, NULL, NULL);
}

/// "Slide Off HIJACK INFO".
void tm_legacy_ev_SlideOff(TmLegacySetup* s)
{
    tm_legacy_InitializeMatch(s->event, s->md, MARTH_EXT,
                              STAGE_POKEMON_STADIUM, 0, true);
    s->md->rules.on_match_start = SlideOffLoad;
}
