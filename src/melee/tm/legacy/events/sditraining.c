/**
 * @file
 * TM-CE legacy event SDITraining (Custom Event Code - Rewrite.asm, lines
 * 1084-1569): a CPU Fox on Final Destination up-throws P1 and chases with
 * up-airs; SDI out of the up-air to score (KO counter = streak). P1 starts
 * at a per-character percent.
 */
#include "../batchB.h"

#include <melee/if/ifstock.h>
#include <melee/gm/types.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>

/// Vanilla statics with unique names.
extern u8 player_slots[];  ///< 0x80453080, P1's static player block
extern u16 staffInfo[2];   ///< -0x4EA8(r13): [0] streak, [1] best

#define FOX_EXT 0x2
#define STAGE_FINAL_DESTINATION 0x20

#define ASID_WAIT 0x0E
#define ASID_DASH 0x14
#define ASID_KNEE_BEND 0x18
#define ASID_JUMP_F 0x19
#define ASID_JUMP_B 0x1A
#define ASID_ATTACK_AIR_HI 0x44
#define ASID_DAMAGE_FALL 0x55 /* hit out of hitstun: SDI'd the up-air */

/* event data offsets */
#define TIMER 0x4       /* s32, frames since (re)start, negative = delay */
#define STATE 0x8       /* u8 */
#define RESET_TIMER 0x9 /* u8 */
#define SDI_FLAG 0xA    /* u8, already scored this attempt */

enum {
    STATE_UP_THROW,
    STATE_FOLLOW,
    STATE_JUMP,
    STATE_UP_AIR,
    STATE_CHECK_RESET,
};

/// SDITrainingStartingPercents, by internal character id.
static const u8 StartingPercents[28] = {
    0x08, 0x5F, 0x80, 0x40, 0x00, 0x30, 0x19, 0x0F, 0x00, 0x00,
    0x00, 0x00, 0x08, 0x05, 0x0F, 0x00, 0x00, 0x00, 0x18, 0x00,
    0x19, 0x08, 0x5F, 0x00, 0x00, 0x2D, 0x3A, 0x00,
};

/// SDITrainingFloats: P1 X, P1 Y, P2 X, P2 Y.
static const u32 GrabPositions[4] = {
    0xC02CCCCD, 0x00000000, 0x4144CCCD, 0x00000000,
};

/// asm SDITrainingInputTowardsOpponent: true if within @p range on X,
/// otherwise push P2's stick towards P1.
static bool InputTowardsOpponent(Fighter* p1, Fighter* p2, int range)
{
    f32 dx = LG_F32(p2, LG_FT_POS_X) - LG_F32(p1, LG_FT_POS_X);

    if ((dx < 0.0F ? -dx : dx) <= (f32) range) {
        return true;
    }
    LG_S8(p2, LG_FT_CPU_ANALOG_X) =
        -tm_legacy_GetDirectionInRelationToP1(p1, p2) * 127;
    return false;
}

static f32 AbsDiffY(Fighter* a, Fighter* b)
{
    f32 d = LG_F32(b, LG_FT_POS_Y) - LG_F32(a, LG_FT_POS_Y);
    return d < 0.0F ? -d : d;
}

/// asm SDITrainingCheckForReset.
static void CheckForReset(u8* data, TmLegacySaveState* ss)
{
    if (LG_U8(data, RESET_TIMER) == 0) {
        return;
    }
    if (--LG_U8(data, RESET_TIMER) != 0) {
        return;
    }
    tm_legacy_SaveState_Load(ss);
    tm_legacy_SaveState_Load(ss);
    LG_S32(data, TIMER) = -HSD_Randi(60);
    LG_U8(data, STATE) = STATE_UP_THROW;
    LG_U8(data, SDI_FLAG) = 0;
}

/// asm SDITrainingUpAirThink.
static void UpAirThink(u8* data, TmLegacySaveState* ss, Fighter* p1,
                       Fighter* p2)
{
    if (LG_F32(p2, LG_FT_ANIM_FRAME) < 12.0F) {
        InputTowardsOpponent(p1, p2, 5);
        if (LG_S32(p2, LG_FT_AIRBORNE) == 0) {
            LG_U8(data, STATE) = STATE_CHECK_RESET;
        }
    }
    CheckForReset(data, ss);
}

/// asm SDITrainingJumpThink.
static void JumpThink(u8* data, TmLegacySaveState* ss, Fighter* p1,
                      Fighter* p2)
{
    s32 state;

    InputTowardsOpponent(p1, p2, 5);
    if (AbsDiffY(p1, p2) <= 35.0F) {
        LG_S8(p2, LG_FT_CPU_CSTICK_Y) = 127; /* up-air */
        LG_U8(data, RESET_TIMER) = 60;
        LG_U8(data, STATE) = STATE_UP_AIR;
        UpAirThink(data, ss, p1, p2);
        return;
    }
    /* double jump on frame 4 of the jump */
    state = LG_S32(p2, LG_FT_STATE);
    if ((state == ASID_JUMP_F || state == ASID_JUMP_B) &&
        LG_F32(p2, LG_FT_ANIM_FRAME) == 4.0F)
    {
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x800;
    }
}

/// asm SDITrainingFollowOpponentThink.
static void FollowThink(u8* data, TmLegacySaveState* ss, Fighter* p1,
                        Fighter* p2)
{
    bool in_range;

    if (LG_S32(p2, LG_FT_AIRBORNE) == 1) {
        LG_U8(data, STATE) = STATE_JUMP;
        JumpThink(data, ss, p1, p2);
        return;
    }
    in_range = InputTowardsOpponent(
        p1, p2, LG_S32(p2, LG_FT_STATE) == ASID_DASH ? 15 : 10);
    if (LG_S32(p2, LG_FT_STATE) == ASID_KNEE_BEND) {
        /* already jumping: full hop unless P1 is within 32 on Y */
        if (AbsDiffY(p1, p2) < 32.0F) {
            return;
        }
    } else if (!in_range) {
        return;
    }
    LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x800; /* jump */
}

/// "SDITraining THINK FUNCT".
static void SDITrainingThink(HSD_GObj* event)
{
    u8* data = event->user_data;
    TmLegacySaveState* ss = (TmLegacySaveState*) (data + LG_EVDATA_SAVESTATE);
    HSD_GObj* gobj[4];
    Fighter* fp[4];
    Fighter* p1;
    Fighter* p2;

    tm_legacy_GetAllPlayerPointers(gobj, fp);
    p1 = fp[0];
    p2 = fp[1];

    LG_U32(p2, 0x1A94) = 0xF; /* CPU type */
    tm_legacy_StoreCPUTypeAndZeroInputs(p2);

    if (tm_legacy_CheckIfFirstFrame()) {
        u8 percent;

        tm_legacyB_EnterGrab((const f32*) GrabPositions, gobj[0], gobj[1]);
        LG_U32(p1, 0x1A4C) = 0x44610000; /* can't mash out */
        percent = StartingPercents[LG_S32(p1, 0x4)];
        LG_U16(player_slots, 0x60) = percent; /* HUD */
        LG_U16(player_slots, 0x62) = percent;
        LG_F32(p1, 0x1830) = (f32) percent;
        tm_legacy_RemoveFirstFrameInputs();
        tm_legacy_SaveState_Save(ss, true);
        LG_S32(data, TIMER) = -HSD_Randi(60);
    }

    LG_S32(data, TIMER)++;

    /* SDI'd out of the up-air: knocked out of hitstun */
    if (LG_U8(data, SDI_FLAG) != 1 &&
        LG_S32(p1, LG_FT_STATE) == ASID_DAMAGE_FALL &&
        !(LG_U8(p1, 0x221C) & 0x02))
    {
        LG_U8(data, SDI_FLAG) = 1;
        tm_legacy_PlaySFX(0xAD);
        staffInfo[0]++;
        if (staffInfo[0] > staffInfo[1]) {
            staffInfo[1] = staffInfo[0];
        }
    }

    /* missed: still in hitlag past frame 11 of Fox's up-air */
    if (LG_S32(p2, LG_FT_STATE) == ASID_ATTACK_AIR_HI &&
        (LG_U8(p1, 0x221A) & 0x20) && LG_F32(p2, LG_FT_ANIM_FRAME) >= 11.0F)
    {
        staffInfo[0] = 0;
    }

    ifStock_802FA2D0(staffInfo[0]);

    switch (LG_U8(data, STATE)) {
    case STATE_FOLLOW:
        FollowThink(data, ss, p1, p2);
        break;
    case STATE_JUMP:
        JumpThink(data, ss, p1, p2);
        break;
    case STATE_UP_AIR:
        UpAirThink(data, ss, p1, p2);
        break;
    case STATE_CHECK_RESET:
        CheckForReset(data, ss);
        break;
    default: /* STATE_UP_THROW, as the asm for any other value */
        if (LG_S32(data, TIMER) < 0) {
            break;
        }
        if (LG_S32(p2, LG_FT_STATE) == ASID_WAIT) {
            LG_U8(data, STATE) = STATE_FOLLOW;
            FollowThink(data, ss, p1, p2);
        } else {
            LG_S8(p2, LG_FT_CPU_ANALOG_Y) = 127; /* up-throw */
        }
        break;
    }
}

/// "SDITraining LOAD FUNCT".
static void SDITrainingLoad(void)
{
    StartOSDs();
    tm_legacy_InitializeHighScore();
    tm_legacy_CreateEventThinkFunction(SDITrainingThink, 3, NULL, NULL);
}

/// "SDITraining HIJACK INFO".
void tm_legacy_ev_SDITraining(TmLegacySetup* s)
{
    tm_legacy_InitializeMatch(s->event, s->md, FOX_EXT,
                              STAGE_FINAL_DESTINATION, 0, true);
    LG_U8(LG_PTR(s->event, 0x18), 0x3) = 0; /* P2 default color */
    s->md->rules.on_match_start = SDITrainingLoad;
}
