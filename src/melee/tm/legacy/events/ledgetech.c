/**
 * @file
 * TM-CE legacy event Ledgetech (Custom Event Code - Rewrite.asm, lines
 * 3017-3359): P1 (90%) starts on a rebirth platform off one ledge; a
 * crouching CPU Falco down-smashes when P1 comes close. Tech off the stage
 * wall to score (KO counter = streak). D-pad left resets.
 */
#include "../batchB.h"

#include <melee/ft/ftanim.h>
#include <melee/ft/ftcommon.h>
#include <melee/if/ifstock.h>
#include <melee/gm/types.h>
#include <sysdolphin/baselib/gobj.h>

/// Vanilla statics with unique names.
extern u8 player_slots[]; ///< 0x80453080, P1's static player block
extern u16 staffInfo[2];  ///< -0x4EA8(r13): [0] streak, [1] best

/// asm AS_SquatWait.
void fn_800D62C4(HSD_GObj* gobj);

#define FALCO_EXT 0x14

#define ASID_REBIRTH_WAIT 0x0D
#define ASID_SQUAT 0x27
#define ASID_SQUAT_WAIT 0x28
#define ASID_ATTACK_LW4 0x40
#define ASID_PASSIVE_WALL 0xCA
#define ASID_PASSIVE_WALL_JUMP 0xCB

/// Ledgetech_Floats: distance to start the down-smash.
#define DSMASH_DISTANCE 35.0F

/* event data offsets */
#define TIMER 0x4      /* s32 reset timer */
#define LEFT_PLAT 0x8  /* u8 P1 left the rebirth platform */
#define TECHED 0x9     /* u8 a wall tech to score */
#define GATEKEEPER 0xA /* u8 this tech already counted */

/// LedgetechWindowInfo: 1 window, Stage Side has 3 options.
static const u8 WindowInfo[4] = { 0x00, 0x02, 0x00, 0x00 };
/// LedgetechWindowText.
static const char WindowText[] = "Stage Side\0Random\0Left\0Right";

static bool IsWallTech(Fighter* fp)
{
    s32 state = LG_S32(fp, LG_FT_STATE);
    return state == ASID_PASSIVE_WALL || state == ASID_PASSIVE_WALL_JUMP;
}

/// Side from the menu, positions, Falco crouching.
static void SetupPositions(u8* menu, HSD_GObj* p1, HSD_GObj* p2)
{
    tm_legacyB_Ledgetech_InitializePositions(
        tm_legacyB_StageSideFromMenu(menu), p1, p2);
    fn_800D62C4(p2); /* SquatWait */
}

/// asm LedgetechRestoreState.
static void RestoreState(u8* data, TmLegacySaveState* ss, u8* menu,
                         HSD_GObj* p1, HSD_GObj* p2)
{
    tm_legacy_SaveState_Load(ss);
    SetupPositions(menu, p1, p2);
    LG_S32(data, TIMER) = 0;
    LG_U8(data, LEFT_PLAT) = 0;
    LG_U8(data, TECHED) = 0;
    LG_U8(data, GATEKEEPER) = 0;
    staffInfo[0] = 0;
}

/// "Ledgetech THINK FUNCT".
static void LedgetechThink(HSD_GObj* event)
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
        tm_legacy_RemoveFirstFrameInputs();
        SetupPositions(menu, gobj[0], gobj[1]);
        LG_U16(player_slots, 0x60) = 90; /* P1 at 90% */
        LG_U32(p1, 0x1830) = 0x42B40000;
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -127; /* crouch cancel */
        tm_legacy_SaveState_Save(ss, true);
    }

    tm_legacy_GiveFullShields();

    /* dead, or D-pad left: reset */
    if ((LG_U8(p1, LG_FT_FLAGS_221F) & 0x40) || (LG_U32(p1, 0x668) & 0x1)) {
        RestoreState(data, ss, menu, gobj[0], gobj[1]);
        return;
    }

    LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -127; /* always crouch cancel */

    /* start the timer when P1 leaves the rebirth platform */
    if (LG_U8(data, LEFT_PLAT) == 0) {
        if (LG_S32(p1, LG_FT_STATE) == ASID_REBIRTH_WAIT) {
            LG_U32(p1, 0x2340) = 2; /* stay on the platform */
        } else {
            LG_U8(data, LEFT_PLAT) = 1;
            LG_U32(p1, 0x198C) = 0; /* no more intangibility */
            LG_U32(p1, 0x1990) = 0;
            LG_U32(p1, 0x1994) = 0;
            ftCommon_8007DB24(gobj[0]); /* GFX_RemoveAll */
            LG_S32(data, TIMER) = 180;
        }
    }

    /* freeze Falco on frame 6 of his down-smash */
    if (LG_S32(p2, LG_FT_STATE) == ASID_ATTACK_LW4 &&
        LG_F32(p2, LG_FT_ANIM_FRAME) == 6.0F)
    {
        ftAnim_SetAnimRate(gobj[1], 0.0F);
    }

    /* a wall tech extends the timer, once per tech */
    if (LG_U8(data, GATEKEEPER) != 1 && IsWallTech(p1)) {
        LG_S32(data, TIMER) = 180;
        LG_U8(data, TECHED) = 1;
        LG_U8(data, GATEKEEPER) = 1;
    }
    if (IsWallTech(p1)) {
        if (LG_U8(data, TECHED) == 1) {
            LG_U8(data, TECHED) = 0;
            staffInfo[0]++;
            if (staffInfo[0] > staffInfo[1]) {
                staffInfo[1] = staffInfo[0];
            }
        }
    } else {
        LG_U8(data, GATEKEEPER) = 0;
    }
    ifStock_802FA2D0(staffInfo[0]);

    /* unfreeze Falco once his hitbox connected */
    if (LG_F32(p2, LG_FT_ANIM_SPEED) == 0.0F && LG_U32(p2, 0x988) != 0) {
        ftAnim_SetAnimRate(gobj[1], 1.0F);
    }

    /* down-smash when P1 comes close */
    state = LG_S32(p2, LG_FT_STATE);
    if ((state == ASID_SQUAT || state == ASID_SQUAT_WAIT) &&
        tm_legacy_GetDistance((const f32*) ((u8*) p2 + LG_FT_POS_X),
                              (const f32*) ((u8*) p1 + LG_FT_POS_X)) <=
            DSMASH_DISTANCE)
    {
        LG_S8(p2, LG_FT_CPU_CSTICK_Y) = -127;
        if (LG_S32(data, TIMER) == 0) {
            LG_S32(data, TIMER) = 60;
        }
    }

    /* reset when the timer runs out */
    if (LG_S32(data, TIMER) <= 0) {
        return;
    }
    if (--LG_S32(data, TIMER) != 0) {
        return;
    }
    RestoreState(data, ss, menu, gobj[0], gobj[1]);
}

/// "Ledgetech LOAD FUNCT".
static void LedgetechLoad(void)
{
    StartOSDs();
    tm_legacy_InitializeHighScore();
    tm_legacy_CreateEventThinkFunction(LedgetechThink, 3, WindowInfo,
                                       WindowText);
}

/// "Ledgetech HIJACK INFO".
void tm_legacy_ev_Ledgetech(TmLegacySetup* s)
{
    tm_legacy_InitializeMatch(s->event, s->md, FALCO_EXT, -1, 0, true);
    /* TM-CE then "buffs the defense ratio" with `stw 0x3F000000, 0x14(r20)`,
     * but r20 there is onEnterVs's GmEvent.dat level table, not the P2
     * struct: it overwrote levels[5]. Dropped; Falco's ratio stays 1.0, as
     * it effectively was. */
    s->md->rules.on_match_start = LedgetechLoad;
}
