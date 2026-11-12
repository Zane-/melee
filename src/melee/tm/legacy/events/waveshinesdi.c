/**
 * @file
 * TM-CE legacy event Waveshine SDI (Custom Event Code - Rewrite.asm, lines
 * 5663-6121): a CPU Fox drills you on Final Destination and then waveshines
 * you across the stage; SDI out. Resets when Fox reaches the edge, grabs,
 * or teeters, with sides swapped.
 */
#include "../legacy.h"

#include <math.h>
#include <melee/ft/types.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>

#define FOX_EXT 0x2
#define STAGE_FINAL_DESTINATION 0x20

#define ASID_WAIT 0x0E
#define ASID_WALK_SLOW 0x0F
#define ASID_WALK_FAST 0x11
#define ASID_JUMP_F 0x19
#define ASID_ATTACK_AIR_LW 0x45 /* dair (drill) */
#define ASID_CATCH_WAIT 0xD8    /* Fox is holding P1 */
#define ASID_OTTOTTO 0xF5       /* teeter */
#define ASID_FOX_SHINE_LOOP 0x169

#define BTN_B 0x200
#define BTN_X 0x400
#define BTN_LR 0xC0

/* event data offsets */
#define OFST_FIRST_FRAME 0x0  /* u8 */
#define OFST_TIMER 0x4        /* s32, starts negative */
#define OFST_PHASE 0x8        /* u8: 0 drill, 1 start waveshine, 2 waveshining */
#define OFST_JC_FRAME 0x9     /* u8 */
#define OFST_RESET_TIMER 0xC  /* s32 */
#define OFST_P1_BACKUP (LG_EVDATA_SAVESTATE + 0x0)
#define OFST_P2_BACKUP (LG_EVDATA_SAVESTATE + 0x8)

/// "WaveshineSDI_Floats".
static const f32 floats[7] = {
    -70.0F,     /* P1 X */
    -76.090668F, /* P2 X (0xC2982E6C) */
    0.0001F,    /* P1 Y */
    0.0001F,    /* P2 Y */
    5.0F,       /* L-cancel height */
    7.5F,       /* distance to shine from */
    80.0F,      /* X where Fox stops */
};
#define FL_LCANCEL_HEIGHT 4
#define FL_SHINE_DISTANCE 5
#define FL_MAX_X 6

/// Fighter fields only this event uses (asm offsets).
#define FT_LAST_GROUND_Y 0x834 /* f32 */
#define FT_PREV_STICK_X 0x620  /* f32, previous analog X */
#define FT_FLAGS_2219 0x2219   /* u8, 0x04 = frozen */
#define FT_FLAGS_221A 0x221A   /* u8, 0x08 = fastfalling */

static int FacingInt(Fighter* fp)
{
    return (int) LG_F32(fp, LG_FT_FACING);
}

static void Shine(u8* data, Fighter* p2)
{
    LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -127;
    LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_B;
    LG_U8(data, OFST_JC_FRAME) = HSD_Randi(3);
}

/// "WaveshineSDIWaveshine_FollowOpponent".
static void FollowOpponent(u8* data, Fighter* p1, Fighter* p2)
{
    f32 dist = LG_F32(p1, LG_FT_POS_X) - LG_F32(p2, LG_FT_POS_X);
    f32 near = floats[FL_SHINE_DISTANCE];
    bool walk = dist >= 0.0F ? dist > near : dist < -near;

    if (!walk) {
        Shine(data, p2);
        return;
    }
    /* walk towards (and keep the analog smash counter from dashing) */
    LG_S8(p2, LG_FT_CPU_ANALOG_X) = 127 * FacingInt(p2);
    LG_F32(p2, FT_PREV_STICK_X) = LG_F32(p2, LG_FT_FACING);
}

/// "WaveshineSDIRestoreState": swap sides and restore.
static void RestoreState(u8* data)
{
    u8* b1 = LG_PTR(data, OFST_P1_BACKUP);
    u8* b2 = LG_PTR(data, OFST_P2_BACKUP);

    LG_F32(b1, LG_FT_FACING) = -LG_F32(b1, LG_FT_FACING);
    LG_F32(b2, LG_FT_FACING) = -LG_F32(b2, LG_FT_FACING);
    LG_F32(b1, LG_FT_POS_X) = -LG_F32(b1, LG_FT_POS_X);
    LG_F32(b2, LG_FT_POS_X) = -LG_F32(b2, LG_FT_POS_X);
    tm_legacy_SaveState_Load((TmLegacySaveState*) (data + LG_EVDATA_SAVESTATE));
    LG_S32(data, OFST_TIMER) = -HSD_Randi(60);
    LG_U8(data, OFST_PHASE) = 0;
}

static void StartResetTimer(u8* data)
{
    if (LG_S32(data, OFST_RESET_TIMER) <= 0) {
        LG_S32(data, OFST_RESET_TIMER) = 60;
    }
}

/// The drill and waveshine sequence. Returns true to restore right away
/// (Fox teetering), skipping the reset timer.
static bool Sequence(u8* data, Fighter* p1, Fighter* p2)
{
    s32 state = LG_S32(p2, LG_FT_STATE);

    /* Fox reached the edge: freeze him and reset soon */
    if (fabsf(LG_F32(p2, LG_FT_POS_X)) >= fabsf(floats[FL_MAX_X])) {
        LG_U8(p2, FT_FLAGS_2219) |= 0x04;
        StartResetTimer(data);
        return false;
    }

    /* Fox grabbed P1 */
    if (state == ASID_CATCH_WAIT) {
        StartResetTimer(data);
    }

    if (LG_U8(data, OFST_PHASE) < 1) {
        /* drill */
        if (state == ASID_WAIT) {
            LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_X;
        } else if (state == ASID_JUMP_F) {
            LG_S8(p2, LG_FT_CPU_CSTICK_Y) = -127;
        } else if (state == ASID_ATTACK_AIR_LW) {
            LG_S8(p2, LG_FT_CPU_ANALOG_X) = 36 * FacingInt(p2);
            if (!(LG_U8(p2, FT_FLAGS_221A) & 0x08)) {
                if (!(LG_F32(p2, LG_FT_VEL_Y) < 0.0F)) {
                    return false; /* not falling yet */
                }
                LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -127; /* fastfall */
            }
            /* L-cancel within 5 units of the ground */
            if (!(LG_F32(p2, LG_FT_POS_Y) - LG_F32(p2, FT_LAST_GROUND_Y) >
                  floats[FL_LCANCEL_HEIGHT]))
            {
                LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_LR;
                LG_U8(data, OFST_PHASE) = 1;
            }
        }
        return false;
    }

    /* waveshine */
    if (state == ASID_WAIT) {
        if (LG_U8(data, OFST_PHASE) == 2) {
            FollowOpponent(data, p1, p2);
        } else {
            LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -127;
            LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_B;
            LG_U8(data, OFST_PHASE) = 2;
            LG_U8(data, OFST_JC_FRAME) = HSD_Randi(3);
        }
    } else if (state == ASID_FOX_SHINE_LOOP) {
        if ((f32) LG_U8(data, OFST_JC_FRAME) == LG_F32(p2, LG_FT_ANIM_FRAME)) {
            LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_X;
        }
    } else if (state == ASID_JUMP_F) {
        s32 x, y;
        tm_legacy_ConvertAngle(HSD_Randi(30) + 310, &x, &y);
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = x * FacingInt(p2);
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = y;
        LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_LR;
    } else if (state >= ASID_WALK_SLOW && state <= ASID_WALK_FAST) {
        FollowOpponent(data, p1, p2);
    } else if (state == ASID_OTTOTTO) {
        return true;
    }
    return false;
}

/// "Waveshine SDI THINK FUNCT".
static void WaveshineSDIThink(HSD_GObj* event)
{
    u8* data = event->user_data;
    HSD_GObj* gobj[4];
    Fighter* fp[4];
    Fighter* p1;
    Fighter* p2;
    s32 t;

    tm_legacy_GetAllPlayerPointers(gobj, fp);
    p1 = fp[0];
    p2 = fp[1];
    tm_legacy_StoreCPUTypeAndZeroInputs(p2);

    if (tm_legacy_CheckIfFirstFrame()) {
        LG_U8(data, OFST_FIRST_FRAME) = 1;
        LG_F32(p2, LG_FT_FACING) = 1.0F;
        LG_F32(p1, LG_FT_FACING) = -1.0F;
        tm_legacy_InitializePositions(floats, gobj[0], gobj[1]);
        tm_legacy_RemoveFirstFrameInputs();
        LG_F32(p2, FT_LAST_GROUND_Y) = LG_F32(p2, LG_FT_POS_Y);
        tm_legacy_SaveState_Save(
            (TmLegacySaveState*) (data + LG_EVDATA_SAVESTATE), true);
        LG_S32(data, OFST_TIMER) = -60;
    }

    t = ++LG_S32(data, OFST_TIMER);
    if (t >= 0 && Sequence(data, p1, p2)) {
        RestoreState(data);
        return;
    }

    /* "WaveshineSDICheckToReset" */
    t = LG_S32(data, OFST_RESET_TIMER);
    if (t > 0) {
        t--;
        LG_S32(data, OFST_RESET_TIMER) = t;
        if (t == 0) {
            RestoreState(data);
        }
    }
}

/// "Waveshine SDI LOAD FUNCT". (The asm's commented-out "Long Destination"
/// stage edit is not ported.)
static void WaveshineSDILoad(void)
{
    StartOSDs();
    tm_legacy_CreateEventThinkFunction(WaveshineSDIThink, 3, NULL, NULL);
}

/// "Waveshine SDI HIJACK INFO".
void tm_legacy_ev_WaveshineSDI(TmLegacySetup* s)
{
    tm_legacy_InitializeMatch(s->event, s->md, FOX_EXT,
                              STAGE_FINAL_DESTINATION, 0, true);
    s->md->rules.on_match_start = WaveshineSDILoad;
}
