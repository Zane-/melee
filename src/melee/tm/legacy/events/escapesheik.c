/**
 * @file
 * TM-CE legacy event Escape Sheik (Custom Event Code - Rewrite.asm, lines
 * 7673-8599): a CPU Sheik down-throws you on Final Destination and chases
 * your tech option with a regrab or jab; escape with a well-timed shine.
 * A mistimed down-B shows how many frames early or late it was.
 */
#include "../legacy.h"

#include <math.h>
#include <melee/ft/ftdata.h>
#include <melee/ft/kinds/ftCommon/ftCo_Attack100.h>
#include <melee/ft/kinds/ftCommon/ftCo_CapturePulled.h>
#include <melee/ft/kinds/ftCommon/ftCo_CatchPull.h>
#include <melee/ft/types.h>
#include <melee/pl/player.h>
#include <melee/tm/osdcore/osd.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>
#include <sysdolphin/baselib/sislib.h>

/// asm AS_Guard (0x800939B4): static in ft/kinds/ftCommon/ftCo_Guard.c,
/// resolved by name by the overlay linker.
void ftCo_800939B4(HSD_GObj* gobj);

#define SHEIK_EXT 0x13
#define STAGE_FINAL_DESTINATION 0x20

#define ASID_WAIT 0x0E
#define ASID_TURN 0x12
#define ASID_DASH 0x14
#define ASID_RUN 0x15
#define ASID_DAMAGE_HI1 0x4B
#define ASID_DAMAGE_FLY_ROLL 0x5B
#define ASID_DOWN_BOUND_U 0xB7
#define ASID_DOWN_BOUND_D 0xBF
#define ASID_PASSIVE 0xC7
#define ASID_PASSIVE_STAND_F 0xC8
#define ASID_PASSIVE_STAND_B 0xC9
#define ASID_CATCH 0xD4
#define ASID_CAPTURE_PULLED_HI 0xDF
#define ASID_CAPTURE_WAIT_HI 0xE0
#define ASID_CAPTURE_PULLED_LW 0xE2
#define ASID_CAPTURE_WAIT_LW 0xE3
#define ASID_CAPTURE_FOOT 0xE8

#define BTN_R 0x20
#define BTN_A 0x100
#define BTN_B 0x200

#define RESET_TIMER 40
#define PERCENT_LO 0
#define PERCENT_HI 40
#define THROW_TIMER_LO 30
#define THROW_TIMER_HI 60
#define REACT_FRAME 12
#define JAB_FRAME_LO 15
#define JAB_FRAME_HI 20
#define JAB2_FRAME_LO 6
#define JAB2_FRAME_HI 18

/* event data offsets */
#define OFST_STATE 0x0         /* u8 */
#define OFST_TIMER 0x1         /* u8 */
#define OFST_THROW_TIMER 0x2   /* u16 */
#define OFST_JAB_FRAME 0x4     /* u8 */
#define OFST_IS_JAB_TWICE 0x5  /* u8 */
#define OFST_JAB2_FRAME 0x6    /* u8 */
#define OFST_JAB2_TIMER 0x7    /* u8 */
#define OFST_DISPLAYED 0x8     /* u8 */

enum {
    STATE_THROW_DELAY,
    STATE_THROW_ENDLAG,
    STATE_CHASE,
    STATE_JAB2,
    STATE_RESET,
};

/* fighter fields only this event uses (asm offsets) */
#define FT_MOTION_ID 0x14       /* s32 */
#define FT_SELF_VEL_X 0xC8      /* f32 */
#define FT_GFX 0x60C            /* pointer */
#define FT_GRABSTUN 0x1A4C      /* f32 */
#define FT_GRAB_VICTIM 0x1A58   /* HSD_GObj* */
#define FT_GRAB_VICTIM2 0x1A5C  /* HSD_GObj* */
#define FT_FLAGS_221A 0x221A    /* u8, 0x20 = in hitlag */
#define FT_TM_PREV_FRAMES (LG_FT_TM_PREV_STATES + 0xC) /* u16[6] */

/// asm InputStruct offsets (HSD_PadStatus).
#define INPUT_INSTANT_BUTTONS 0x8 /* u32 */
#define INPUT_LEFT_ANALOG_Y 0x19  /* s8 */

/// "EscapeSheikThink_Constants".
static const struct {
    f32 p1_x, p1_y, p2_x, p2_y;
    f32 grab_distance;
    f32 hold_shield_velocity;
    f32 run_distance;
} k = { -8.0F, 0.0F, 8.0F, 0.0F, 14.0F, 1.1F, 23.0F };

static int FacingInt(Fighter* fp)
{
    return (int) LG_F32(fp, LG_FT_FACING);
}

/// 1 if @p fp moves right, else -1 (asm "BUT is he coming to me?").
static int MovingDir(Fighter* fp)
{
    return LG_F32(fp, FT_SELF_VEL_X) > 0.0F ? 1 : -1;
}

static void Catch(u8* data, HSD_GObj* p2g)
{
    ftCo_800D8C54(p2g, ASID_CATCH);
    LG_U8(data, OFST_STATE) = STATE_RESET;
}

static void Guard(HSD_GObj* p2g, Fighter* p2)
{
    ftCo_800939B4(p2g);
    LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_R;
}

/// "EscapeSheik_InitializePositions": Sheik already holding P1.
static void InitializePositions(HSD_GObj* p1g, HSD_GObj* p2g, u8* data)
{
    Fighter* p1 = p1g->user_data;
    Fighter* p2 = p2g->user_data;
    int facing = HSD_Randi(2) == 0 ? 1 : -1;

    LG_F32(p1, LG_FT_FACING) = (f32) facing;
    LG_F32(p2, LG_FT_FACING) = (f32) -facing;

    /* TM-CE stores P1's coordinates into both fighters whichever way they
     * face (its second block reloads P1X/P1Y and falls through). The grab
     * below positions them anyway; kept as in the asm. */
    LG_F32(p2, LG_FT_POS_X) = k.p1_x;
    LG_F32(p2, LG_FT_POS_Y) = k.p1_y;
    LG_F32(p1, LG_FT_POS_X) = k.p1_x;
    LG_F32(p1, LG_FT_POS_Y) = k.p1_y;
    tm_legacy_PlacePlayerOnGround(p1g);
    tm_legacy_UpdateCameraBox(p1g);
    tm_legacy_PlacePlayerOnGround(p2g);
    tm_legacy_UpdateCameraBox(p2g);

    /* Sheik grabs P1 */
    LG_PTR(p2, FT_GRAB_VICTIM) = p1g;
    LG_PTR(p2, FT_GRAB_VICTIM2) = p1g;
    LG_PTR(p1, FT_GRAB_VICTIM) = NULL;
    LG_PTR(p1, FT_GRAB_VICTIM2) = NULL;
    LG_PTR(p2, FT_GFX) = NULL;
    fn_800D9CE8(p2g);       /* CatchPull */
    fn_800DAADC(p1g, p2g);  /* CapturePulled */
    fn_800DA1D8(p2g);       /* CatchWait */
    LG_F32(p1, FT_GRABSTUN) = 999.0F;

    Player_SetHUDDamage(LG_U8(p1, LG_FT_SLOT),
                        HSD_Randi(PERCENT_HI - PERCENT_LO) + PERCENT_LO);

    LG_U8(data, OFST_STATE) = STATE_THROW_DELAY;
    LG_U8(data, OFST_TIMER) = 0;
    LG_U8(data, OFST_JAB_FRAME) = 0;
    LG_U16(data, OFST_THROW_TIMER) =
        HSD_Randi(THROW_TIMER_HI - THROW_TIMER_LO) + THROW_TIMER_LO;
    LG_U8(data, OFST_DISPLAYED) = 0;
}

/// "EscapeSheikThink_CheckForMistimedShine": a down-B pressed during the
/// tech (early) or the regrab (late) shows the timing once.
static void CheckForMistimedShine(u8* data, Fighter* p1)
{
    u8* in;
    const char* when;
    int frames;
    s32 state;
    int i;

    if (LG_U8(data, OFST_STATE) < STATE_CHASE ||
        LG_U8(data, OFST_DISPLAYED) != 0)
    {
        return;
    }
    in = tm_legacy_GetInputStruct(LG_U8(p1, LG_FT_PORT));
    if (!(LG_U32(in, INPUT_INSTANT_BUTTONS) & BTN_B) ||
        LG_S8(in, INPUT_LEFT_ANALOG_Y) > -44)
    {
        return;
    }

    state = LG_S32(p1, LG_FT_STATE);
    if (state == ASID_PASSIVE || state == ASID_PASSIVE_STAND_B ||
        state == ASID_PASSIVE_STAND_F)
    {
        /* frames left in the tech animation */
        void* tree = ftData_80085E50(p1, LG_S32(p1, FT_MOTION_ID));
        when = "Early";
        frames = (int) LG_F32(tree, 0x8) -
                 LG_U16(p1, LG_FT_TM_STATE_FRAMES);
    } else if (state == ASID_CAPTURE_PULLED_LW ||
               state == ASID_CAPTURE_PULLED_HI ||
               state == ASID_CAPTURE_WAIT_LW || state == ASID_CAPTURE_WAIT_HI)
    {
        /* frames since P1 last stood in Wait */
        when = "Late";
        frames = LG_U16(p1, LG_FT_TM_STATE_FRAMES);
        for (i = 0;; i++) {
            if (i >= 6) {
                return;
            }
            if (LG_U16(p1, LG_FT_TM_PREV_STATES + 2 * i) == ASID_WAIT) {
                break;
            }
            frames += LG_U16(p1, FT_TM_PREV_FRAMES + 2 * i);
        }
    } else {
        return;
    }

    {
        HSD_Text* text =
            tm_osd_TextCreate(p1, 120, 0, TM_OSD_MISCELLANEOUS);
        HSD_SisLib_803A6B98(text, LG_TEXT_X, LG_TEXT_X, "Down B Input");
        HSD_SisLib_803A6B98(text, LG_TEXT_X, LG_TEXT_LINE2_Y, "%df %s",
                            frames, when);
    }
    LG_U8(data, OFST_DISPLAYED) = 1;
}

/// P1 in a tech roll or tech in place ("PassiveThink").
static void PassiveThink(u8* data, HSD_GObj* p2g, Fighter* p1, Fighter* p2,
                         f32 dist, int dir)
{
    f32 adist = fabsf(dist);

    if (dir <= 0) {
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = FacingInt(p2) * dir * 100;
    }
    if (adist > k.grab_distance) {
        LG_S8(p2, LG_FT_CPU_ANALOG_X) =
            FacingInt(p2) * dir * (adist > k.run_distance ? 127 : 100);
    }
    if (!(adist > k.grab_distance)) {
        s32 state = LG_S32(p2, LG_FT_STATE);
        if (state == ASID_DASH || state == ASID_RUN) {
            Guard(p2g, p2);
        }
    }
    if (LG_U16(p1, LG_FT_TM_STATE_FRAMES) >= 20) {
        Catch(data, p2g);
    }
}

/// P1 teching in place facing or away ("PassiveStandThink").
static void PassiveStandThink(u8* data, HSD_GObj* p2g, Fighter* p1,
                              Fighter* p2, f32 dist, int dir)
{
    f32 adist = fabsf(dist);

    if (dir <= 0 && MovingDir(p1) == FacingInt(p2) * dir) {
        int speed = LG_U16(p1, LG_FT_TM_STATE_FRAMES) < 20 ? 127 : 100;
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = FacingInt(p2) * dir * speed;
    }

    if (adist > k.grab_distance) {
        bool decide = true;
        if (LG_S32(p2, LG_FT_STATE) == ASID_TURN &&
            LG_U16(p2, LG_FT_TM_STATE_FRAMES) >= 2)
        {
            decide = false;
        }
        if (decide && MovingDir(p1) == FacingInt(p2) * dir) {
            LG_S8(p2, LG_FT_CPU_ANALOG_X) = FacingInt(p2) * dir * 127;
        }
    }

    if (!(adist > k.grab_distance)) {
        s32 state = LG_S32(p2, LG_FT_STATE);
        if (state == ASID_DASH || state == ASID_RUN) {
            if (LG_U16(p1, LG_FT_TM_STATE_FRAMES) >= 28 ||
                !(fabsf(LG_F32(p1, FT_SELF_VEL_X)) > k.hold_shield_velocity))
            {
                Guard(p2g, p2);
            } else {
                LG_S8(p2, LG_FT_CPU_ANALOG_X) = FacingInt(p2) * dir * 127;
            }
        }
    }

    if (LG_U16(p1, LG_FT_TM_STATE_FRAMES) >= 34) {
        Catch(data, p2g);
    }
}

/// P1 missed the tech ("DownBoundThink"): walk up and jab once or twice.
static void DownBoundThink(u8* data, Fighter* p1, Fighter* p2, f32 dist,
                           int dir)
{
    f32 adist = fabsf(dist);

    if (LG_U8(data, OFST_JAB_FRAME) == 0) {
        LG_U8(data, OFST_JAB_FRAME) =
            HSD_Randi(JAB_FRAME_HI - JAB_FRAME_LO) + JAB_FRAME_LO;
        LG_U8(data, OFST_IS_JAB_TWICE) = HSD_Randi(2);
        LG_U8(data, OFST_JAB2_FRAME) =
            HSD_Randi(JAB2_FRAME_HI - JAB2_FRAME_LO) + JAB2_FRAME_LO;
        LG_U8(data, OFST_JAB2_TIMER) = 0;
    }
    if (dir <= 0) {
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = FacingInt(p2) * dir * 100;
    }
    if (adist > k.grab_distance) {
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = FacingInt(p2) * dir * 100;
    }
    if (!(adist > k.grab_distance) && dir == 1) {
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0;
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = 0;
    }

    if (LG_U16(p1, LG_FT_TM_STATE_FRAMES) < LG_U8(data, OFST_JAB_FRAME)) {
        return;
    }
    LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_A;
    LG_S8(p2, LG_FT_CPU_ANALOG_X) = 0;
    if (LG_U8(data, OFST_IS_JAB_TWICE) != 0) {
        LG_U8(data, OFST_JAB2_TIMER) = LG_U8(data, OFST_JAB2_FRAME);
        LG_U8(data, OFST_STATE) = STATE_JAB2;
    } else {
        LG_U8(data, OFST_STATE) = STATE_RESET;
        LG_U8(data, OFST_TIMER) = RESET_TIMER + 30;
    }
}

/// "EscapeSheikThink_Chase".
static void Chase(u8* data, HSD_GObj* p2g, Fighter* p1, Fighter* p2)
{
    f32 dist = (LG_F32(p1, LG_FT_POS_X) - LG_F32(p2, LG_FT_POS_X)) *
               LG_F32(p2, LG_FT_FACING);
    int dir = dist < 0.0F ? -1 : 1;
    s32 state = LG_S32(p1, LG_FT_STATE);

    if (state == ASID_DOWN_BOUND_D || state == ASID_DOWN_BOUND_U) {
        DownBoundThink(data, p1, p2, dist, dir);
        return;
    }
    if (LG_U16(p1, LG_FT_TM_STATE_FRAMES) < REACT_FRAME) {
        return;
    }
    if (state == ASID_PASSIVE) {
        PassiveThink(data, p2g, p1, p2, dist, dir);
    } else if (state == ASID_PASSIVE_STAND_B ||
               state == ASID_PASSIVE_STAND_F)
    {
        PassiveStandThink(data, p2g, p1, p2, dist, dir);
    }
}

/// "Escape Sheik THINK FUNCT".
static void EscapeSheikThink(HSD_GObj* event)
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
        InitializePositions(gobj[0], gobj[1], data);
        tm_legacy_RemoveFirstFrameInputs();
        tm_legacy_SaveState_Save(ss, true);
    }

    if (tm_legacy_IsAnyoneDead()) {
        goto restore;
    }

    /* failed: regrabbed */
    state = LG_S32(p1, LG_FT_STATE);
    if (LG_U8(data, OFST_STATE) >= STATE_CHASE &&
        state >= ASID_CAPTURE_PULLED_HI && state <= ASID_CAPTURE_FOOT &&
        LG_U8(data, OFST_TIMER) <= 0)
    {
        LG_U8(data, OFST_TIMER) = RESET_TIMER;
        goto check_timer;
    }

    /* succeeded: Sheik got hit */
    state = LG_S32(p2, LG_FT_STATE);
    if (state >= ASID_DAMAGE_HI1 && state <= ASID_DAMAGE_FLY_ROLL &&
        LG_U8(data, OFST_TIMER) <= 0)
    {
        tm_legacy_PlaySFX(0xAD);
        LG_U8(data, OFST_TIMER) = RESET_TIMER + 60;
        goto check_timer;
    }

    CheckForMistimedShine(data, p1);

    switch (LG_U8(data, OFST_STATE)) {
    case STATE_THROW_DELAY:
        t = LG_U16(data, OFST_THROW_TIMER) - 1;
        LG_U16(data, OFST_THROW_TIMER) = t;
        if (t <= 0) {
            LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -127; /* down throw */
            LG_U8(data, OFST_STATE) = STATE_THROW_ENDLAG;
        }
        break;
    case STATE_THROW_ENDLAG:
        if (LG_S32(p2, LG_FT_STATE) != ASID_WAIT) {
            break;
        }
        state = LG_S32(p1, LG_FT_STATE);
        if ((state >= ASID_PASSIVE && state <= ASID_PASSIVE_STAND_B) ||
            state == ASID_DOWN_BOUND_D || state == ASID_DOWN_BOUND_U)
        {
            LG_U8(data, OFST_STATE) = STATE_CHASE;
            Chase(data, gobj[1], p1, p2);
        }
        break;
    case STATE_CHASE:
        Chase(data, gobj[1], p1, p2);
        break;
    case STATE_JAB2:
        if (LG_U8(data, OFST_JAB2_TIMER) == 0 ||
            (LG_U8(p2, FT_FLAGS_221A) & 0x20))
        {
            break;
        }
        t = LG_U8(data, OFST_JAB2_TIMER) - 1;
        LG_U8(data, OFST_JAB2_TIMER) = t;
        if (t > 0) {
            break;
        }
        LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_A;
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = 0;
        LG_U8(data, OFST_STATE) = STATE_RESET;
        LG_U8(data, OFST_TIMER) = RESET_TIMER + 30;
        break;
    case STATE_RESET:
        LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_R; /* hold shield */
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
    InitializePositions(gobj[0], gobj[1], data);
}

/// "Escape Sheik LOAD FUNCT".
static void EscapeSheikLoad(void)
{
    StartOSDs();
    tm_legacy_CreateEventThinkFunction(EscapeSheikThink, 3, NULL, NULL);
}

/// "Escape Sheik HIJACK INFO".
void tm_legacy_ev_EscapeSheik(TmLegacySetup* s)
{
    tm_legacy_InitializeMatch(s->event, s->md, SHEIK_EXT,
                              STAGE_FINAL_DESTINATION, 0, true);
    s->md->rules.on_match_start = EscapeSheikLoad;
}
