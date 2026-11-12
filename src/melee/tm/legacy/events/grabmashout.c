/**
 * @file
 * TM-CE legacy event Grab Mash Out (Custom Event Code - Rewrite.asm, lines
 * 6746-7088): a CPU Marth grabs you after a random delay on Final
 * Destination; mash out. P1's controls are locked until the grab connects.
 */
#include "../legacy.h"

#include <melee/ft/ft_0892.h>
#include <melee/ft/types.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>

#define MARTH_EXT 0x9
#define STAGE_FINAL_DESTINATION 0x20

#define ASID_CAPTURE_PULLED_HI 0xDF
#define ASID_CAPTURE_WAIT_HI 0xE0
#define ASID_CAPTURE_PULLED_LW 0xE2
#define ASID_CAPTURE_WAIT_LW 0xE3
#define ASID_CAPTURE_CUT 0xE5
#define ASID_CAPTURE_JUMP 0xE6

#define BTN_A 0x100
#define BTN_R 0x20

#define RESET_TIMER 80
#define PERCENT_LO 0
#define PERCENT_HI 80
#define THROW_TIMER_LO 40
#define THROW_TIMER_HI 100

/* event data offsets */
#define OFST_STATE 0x0        /* u8 */
#define OFST_TIMER 0x1        /* u8 */
#define OFST_THROW_TIMER 0x2  /* u16 */
#define OFST_GRAB_BREAKOUT 0x4 /* f32 */

enum { STATE_THROW_DELAY, STATE_MASH_OUT, STATE_RESET };

/// Grab escape timer of the grabbed fighter (asm 0x2354).
#define FT_GRAB_BREAKOUT 0x2354

/// "GrabMashOutThink_Constants": P1 X/Y, P2 X/Y.
static const f32 positions[4] = { -8.0F, 0.0F, 8.0F, 0.0F };

/// "GrabMashOut_InitializePositions".
static void InitializePositions(HSD_GObj* p1g, HSD_GObj* p2g, u8* data)
{
    Fighter* p1 = p1g->user_data;
    Fighter* p2 = p2g->user_data;
    int facing = HSD_Randi(2) == 0 ? 1 : -1;

    LG_F32(p1, LG_FT_FACING) = (f32) facing;
    LG_F32(p2, LG_FT_FACING) = (f32) -facing;

    /* the left fighter at (P1X, P1Y), the right one at (P2X, P2Y) */
    if (facing >= 0) {
        LG_F32(p1, LG_FT_POS_X) = positions[0];
        LG_F32(p1, LG_FT_POS_Y) = positions[1];
        LG_F32(p2, LG_FT_POS_X) = positions[2];
        LG_F32(p2, LG_FT_POS_Y) = positions[3];
    } else {
        LG_F32(p2, LG_FT_POS_X) = positions[0];
        LG_F32(p2, LG_FT_POS_Y) = positions[1];
        LG_F32(p1, LG_FT_POS_X) = positions[2];
        LG_F32(p1, LG_FT_POS_Y) = positions[3];
    }
    tm_legacy_PlacePlayerOnGround(p1g);
    tm_legacy_UpdateCameraBox(p1g);
    tm_legacy_PlacePlayerOnGround(p2g);
    tm_legacy_UpdateCameraBox(p2g);

    ft_8008A2BC(p1g); /* Wait */
    LG_U8(p1, LG_FT_PORT) = 2; /* locked: P1 reads port 3 until grabbed */
    ft_8008A2BC(p2g);

    Player_SetHUDDamage(LG_U8(p1, LG_FT_SLOT),
                        HSD_Randi(PERCENT_HI - PERCENT_LO) + PERCENT_LO);

    LG_U8(data, OFST_STATE) = STATE_THROW_DELAY;
    LG_U8(data, OFST_TIMER) = 0;
    LG_U16(data, OFST_THROW_TIMER) =
        HSD_Randi(THROW_TIMER_HI - THROW_TIMER_LO) + THROW_TIMER_LO;
}

/// "Grab Mash Out THINK FUNCT".
static void GrabMashOutThink(HSD_GObj* event)
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

    state = LG_S32(p1, LG_FT_STATE);
    switch (LG_U8(data, OFST_STATE)) {
    case STATE_THROW_DELAY:
        t = LG_U16(data, OFST_THROW_TIMER) - 1;
        LG_U16(data, OFST_THROW_TIMER) = t;
        if (t == 0) {
            LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_A | BTN_R; /* grab */
        }
        if (state == ASID_CAPTURE_WAIT_LW || state == ASID_CAPTURE_WAIT_HI) {
            LG_F32(data, OFST_GRAB_BREAKOUT) = LG_F32(p1, FT_GRAB_BREAKOUT);
            LG_U8(data, OFST_STATE) = STATE_MASH_OUT;
        } else if (state == ASID_CAPTURE_PULLED_LW ||
                   state == ASID_CAPTURE_PULLED_HI)
        {
            LG_U8(p1, LG_FT_PORT) = 0; /* unlock P1 */
        }
        break;
    case STATE_MASH_OUT:
        if (state == ASID_CAPTURE_JUMP || state == ASID_CAPTURE_CUT) {
            LG_U8(data, OFST_TIMER) = RESET_TIMER;
            LG_U8(data, OFST_STATE) = STATE_RESET;
        }
        break;
    case STATE_RESET:
    default:
        break;
    }

    /* "GrabMashOutThink_CheckTimer" */
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

/// "Grab Mash Out LOAD FUNCT".
static void GrabMashOutLoad(void)
{
    StartOSDs();
    tm_legacy_CreateEventThinkFunction(GrabMashOutThink, 3, NULL, NULL);
}

/// "Grab Mash Out HIJACK INFO".
void tm_legacy_ev_GrabMashOut(TmLegacySetup* s)
{
    tm_legacy_InitializeMatch(s->event, s->md, MARTH_EXT,
                              STAGE_FINAL_DESTINATION, 0, true);
    s->md->rules.on_match_start = GrabMashOutLoad;
}
