/**
 * @file
 * TM-CE legacy event LedgetechCounter (Custom Event Code - Rewrite.asm,
 * lines 7089-7672): P1 starts on a rebirth platform off a ledge with a CPU
 * Marth near it; when P1 recovers to the ledge (action state 356) within
 * range, Marth counters, and P1 wall-techs the counter. A message reports
 * when L/R was pressed relative to the counter's hitlag. D-pad left resets.
 */
#include "../batchB.h"

#include <melee/if/ifstock.h>
#include <melee/tm/osdcore/osd.h>
#include <melee/gm/types.h>
#include <sysdolphin/baselib/gobj.h>

/// Vanilla statics with unique names.
extern u16 staffInfo[2]; ///< -0x4EA8(r13): [0] score

#define MARTH_EXT 0x9

#define ASID_REBIRTH_WAIT 0x0D
#define ASID_PASSIVE_WALL 0xCA
#define ASID_PASSIVE_WALL_JUMP 0xCB
#define ASID_RECOVERING 356             /* P1's up-B toward the ledge */
#define ASID_MARTH_SPECIAL_LW_HIT 0x172 /* counter connected */


/* LedgetechCounter_Constants */
#define COUNTER_RANGE 40.0F   /* Mm from P1 to start the counter */
#define MARTH_FORWARD 5.0F    /* Mm to move Marth forward from the ledge */
#define P1_DOWN -15.0F        /* Mm to move P1 down */

/* event data offsets */
#define EVENT_STATE 0x0 /* u8 */
#define STATE_ON_REBIRTH_PLAT 0
#define STATE_RECOVERING 1
#define STATE_TECH_SUCCEEDED 2
#define MARTH_STATE 0x1 /* u8: 0 waiting, 1 attacked */
#define TIMER 0x2       /* u8 */
#define MARTH_COUNTER_FRAME 0x40 /* s32 game frame Marth's counter hit */
#define TECH_INPUT_FRAME 0x44    /* s32 game frame of P1's L/R */
#define RELATIVE_TECH_FRAME 0x48 /* s8 */
#define MESSAGE_SHOWN 0x49       /* u8 */

/// LedgetechCounterWindowInfo: 1 window, Stage Side has 3 options.
static const u8 WindowInfo[4] = { 0x00, 0x02, 0x00, 0x00 };
/// LedgetechCounterWindowText.
static const char WindowText[] = "Stage Side\0Random\0Left\0Right";

/// asm LedgetechCounterThink_SetupStageSideAndPositions.
static void SetupStageSideAndPositions(u8* menu, HSD_GObj* p1g,
                                       HSD_GObj* p2g)
{
    u8* p1 = p1g->user_data;
    u8* p2 = p2g->user_data;

    tm_legacyB_Ledgetech_InitializePositions(
        tm_legacyB_StageSideFromMenu(menu), p1g, p2g);
    LG_F32(p2, LG_FT_POS_X) += LG_F32(p2, LG_FT_FACING) * MARTH_FORWARD;
    LG_F32(p1, LG_FT_POS_Y) += P1_DOWN;
}

/// asm LedgetechCounter_DetermineTechInputTimingMessageCategory and
/// LedgetechCounter_DisplayTimingMessage. @p rel is the L/R frame relative
/// to the first frame of the counter (SpecialLwHit): 11 frames of the
/// counter's own ("reaction") hitlag, 2 frames, then 5 frames of P1's
/// ("attack") hitlag from frame 13.
static void DisplayTimingMessage(Fighter* p1, int rel)
{
    char* fmt;
    int color;
    int value;

    if (rel <= -6) { /* locked out */
        fmt = "Too Early LR\n%dF Before Hitlag";
        color = TM_MSGCOLOR_RED;
        value = -(rel - 13);
    } else if (rel <= -1 || (rel >= 11 && rel <= 12)) { /* buffered */
        fmt = "Buffered LR\n%dF Before Hitlag";
        color = TM_MSGCOLOR_GREEN;
        value = -(rel - 13);
    } else if (rel <= 10) { /* during the counter's hitlag: no buffer */
        fmt = "LR on Reaction\nHitlag: %d/11";
        color = rel == 10 ? TM_MSGCOLOR_GREEN : TM_MSGCOLOR_RED;
        value = rel + 1;
    } else if (rel <= 17) { /* during P1's hitlag: tech + SDI */
        fmt = "LR on Attack\nHitlag: %d/5";
        color = rel == 13 ? TM_MSGCOLOR_RED : TM_MSGCOLOR_GREEN;
        value = rel - 12;
    } else {
        fmt = "Too Late LR\n%dF After Hitlag Ends";
        color = TM_MSGCOLOR_RED;
        value = rel - 17;
    }
    Message_Display(4, LG_U8(p1, LG_FT_SLOT), color, fmt, value);
}

/// asm LedgetechCounterThink_RecordTechInputFrame,
/// _RecordSpecialLwHitStartingFrame and _DisplayTechInputTimingMessage.
static void TrackTechTiming(u8* data, Fighter* p1, Fighter* p2)
{
    s32 rel;

    /* the asm tests only the top byte of the frame (`lbz`), so a later
     * L/R press overwrites the frame until the message has been shown */
    if (LG_U8(data, TECH_INPUT_FRAME) == 0 &&
        (LG_U32(p1, 0x668) & (PAD_TRIGGER_L | PAD_TRIGGER_R)))
    {
        LG_S32(data, TECH_INPUT_FRAME) = tm_misc_game_frame_counter;
    }

    if (LG_S32(data, MARTH_COUNTER_FRAME) == 0 &&
        LG_S32(p2, LG_FT_STATE) == ASID_MARTH_SPECIAL_LW_HIT)
    {
        LG_S32(data, MARTH_COUNTER_FRAME) = tm_misc_game_frame_counter;
    }

    if (LG_U8(data, MESSAGE_SHOWN) == 1 ||
        LG_S32(data, TECH_INPUT_FRAME) == 0 ||
        LG_S32(data, MARTH_COUNTER_FRAME) == 0)
    {
        return;
    }
    rel = LG_S32(data, TECH_INPUT_FRAME) - LG_S32(data, MARTH_COUNTER_FRAME);
    if (rel < -25 || rel > 28) {
        return;
    }
    LG_S8(data, RELATIVE_TECH_FRAME) = rel;
    DisplayTimingMessage(p1, LG_S8(data, RELATIVE_TECH_FRAME));
    LG_U8(data, MESSAGE_SHOWN) = 1;
}

/// asm LedgetechCounterThink_Restore.
static void Restore(u8* data, TmLegacySaveState* ss, u8* menu, HSD_GObj* p1g,
                    HSD_GObj* p2g)
{
    tm_legacy_SaveState_Load(ss);
    SetupStageSideAndPositions(menu, p1g, p2g);
    LG_U8(data, EVENT_STATE) = STATE_ON_REBIRTH_PLAT;
    LG_U8(data, MARTH_STATE) = 0;
    LG_U8(data, TIMER) = 0;
    LG_S32(data, MARTH_COUNTER_FRAME) = 0;
    LG_S32(data, TECH_INPUT_FRAME) = 0;
    LG_S8(data, RELATIVE_TECH_FRAME) = 0;
    LG_U8(data, MESSAGE_SHOWN) = 0;
}

/// "LedgetechCounter THINK FUNCT".
static void LedgetechCounterThink(HSD_GObj* event)
{
    u8* data = event->user_data;
    TmLegacySaveState* ss = (TmLegacySaveState*) (data + LG_EVDATA_SAVESTATE);
    u8* menu = LG_PTR(data, LG_EVDATA_MENU);
    HSD_GObj* gobj[4];
    Fighter* fp[4];
    Fighter* p1;
    Fighter* p2;
    s32 state;

    tm_legacy_GetAllPlayerPointers(gobj, fp);
    p1 = fp[0];
    p2 = fp[1];

    tm_legacy_StoreCPUTypeAndZeroInputs(p2);

    if (tm_legacy_CheckIfFirstFrame()) {
        SetupStageSideAndPositions(menu, gobj[0], gobj[1]);
        tm_legacy_RemoveFirstFrameInputs();
        tm_legacy_SaveState_Save(ss, true);
        ifStock_802FA2D0(staffInfo[0]);
    }

    /* anyone dead, or D-pad left: reset */
    if (tm_legacy_IsAnyoneDead() || (LG_U32(p1, 0x668) & 0x1)) {
        Restore(data, ss, menu, gobj[0], gobj[1]);
        return;
    }

    TrackTechTiming(data, p1, p2);

    switch (LG_U8(data, EVENT_STATE)) {
    case STATE_ON_REBIRTH_PLAT:
        if (LG_S32(p1, LG_FT_STATE) == ASID_REBIRTH_WAIT) {
            LG_U32(p1, 0x2340) = 2; /* stay on the platform */
        } else {
            LG_U8(data, EVENT_STATE) = STATE_RECOVERING;
        }
        break;
    case STATE_RECOVERING:
        if (LG_U8(data, MARTH_STATE) != 0) {
            LG_U8(data, EVENT_STATE) = STATE_TECH_SUCCEEDED;
            break;
        }
        if (LG_S32(p1, LG_FT_STATE) != ASID_RECOVERING) {
            break;
        }
        if (tm_legacy_GetDistance((const f32*) ((u8*) p1 + LG_FT_POS_X),
                                  (const f32*) ((u8*) p2 + LG_FT_POS_X)) >
            COUNTER_RANGE)
        {
            break;
        }
        /* in range: Marth counters */
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x200;
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -127;
        LG_U8(data, MARTH_STATE) = 1;
        LG_U8(data, TIMER) = 70;
        break;
    case STATE_TECH_SUCCEEDED:
        state = LG_S32(p1, LG_FT_STATE);
        if (state == ASID_PASSIVE_WALL || state == ASID_PASSIVE_WALL_JUMP) {
            LG_U8(data, TIMER) = 120;
        }
        break;
    default:
        break;
    }

    if (LG_U8(data, TIMER) == 0) {
        return;
    }
    if (--LG_U8(data, TIMER) != 0) {
        return;
    }
    Restore(data, ss, menu, gobj[0], gobj[1]);
}

/// "LedgetechCounter LOAD FUNCT".
static void LedgetechCounterLoad(void)
{
    StartOSDs();
    tm_legacy_CreateEventThinkFunction(LedgetechCounterThink, 3, WindowInfo,
                                       WindowText);
}

/// "LedgetechCounter HIJACK INFO".
void tm_legacy_ev_LedgetechCounter(TmLegacySetup* s)
{
    tm_legacy_InitializeMatch(s->event, s->md, MARTH_EXT, -1, 0, false);
    s->md->rules.on_match_start = LedgetechCounterLoad;
}
