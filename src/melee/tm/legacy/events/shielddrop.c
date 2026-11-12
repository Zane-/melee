/**
 * @file
 * TM-CE legacy event Shield Drop (Custom Event Code - Rewrite.asm, lines
 * 2352-2603): on Battlefield's top platform, the CPU does a random aerial
 * at you and then shields; practise shield dropping through the platform.
 * D-pad left/right moves the reset positions apart/together.
 */
#include "../legacy.h"

#include <melee/ft/types.h>
#include <melee/mn/types.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>

#define STAGE_BATTLEFIELD 0x1F

/* event data offsets */
#define OFST_FIRST_FRAME 0x0 /* u8, set once frame 1 ran */
#define OFST_TIMER 0x4       /* s32 */
#define OFST_AERIAL 0x8      /* PerformAerialThink state (word) */

/* menu options */
#define OPT_FACING 0 /* 0 towards, 1 away */

/// asm ShieldDrop_Floats: P1 X, P2 X, P1 Y, P2 Y (Battlefield top platform),
/// as the asm's exact bit patterns (-7.8, 7.8, ~54.4, ~54.4). Its two extra
/// floats (Y velocity to attack, L-cancel distance) are never read.
static const u32 floats[4] = { 0xC0F9999A, 0x40F9999A, 0x425999B4,
                               0x425999B4 };

/// asm ShieldDropWindowInfo: 1 window, Facing Direction has 2 options.
static const u8 window_info[] = { 0x00, 0x01, 0xFF, 0xFF };

/// asm ShieldDropWindowText.
static const char window_text[] = "Facing Direction\0"
                                  "Towards\0"
                                  "Away\0";

/// "Shield Drop THINK FUNCT".
static void ShieldDropThink(HSD_GObj* event)
{
    u8* data = event->user_data;
    u8* menu = LG_PTR(data, LG_EVDATA_MENU);
    TmLegacySaveState* ss = (TmLegacySaveState*) (data + LG_EVDATA_SAVESTATE);
    HSD_GObj* gobj[4];
    Fighter* fp[4];
    s32 timer;

    tm_legacy_GetAllPlayerPointers(gobj, fp);
    tm_legacy_StoreCPUTypeAndZeroInputs(fp[1]);

    if (tm_legacy_CheckIfFirstFrame()) {
        LG_U8(data, OFST_FIRST_FRAME) = 1;
        tm_legacy_InitializePositions((const f32*) floats, gobj[0], gobj[1]);
        tm_legacy_RemoveFirstFrameInputs();
        /* last known Y position = Y position */
        LG_F32(fp[1], 0x834) = LG_F32(fp[1], LG_FT_POS_Y);
        tm_legacy_SaveState_Save(ss, true);
        LG_S32(data, OFST_TIMER) = -60;
    }

    tm_legacy_GiveFullShields();

    /* the asm checks the same toggle twice */
    if (LG_MENU_IS_TOGGLED(menu, OPT_FACING)) {
        goto reset;
    }
    if (tm_legacy_AdjustResetDistance(ss, fp[0], fp[1]) != -1) {
        goto reset;
    }

    timer = LG_S32(data, OFST_TIMER) + 1;
    LG_S32(data, OFST_TIMER) = timer;

    if (LG_S32(fp[1], LG_FT_STATE) == LG_ASID_WAIT) {
        tm_legacy_GiveInvincibility(gobj[1], 2);
    }

    if (timer < 40) {
        goto exit;
    }

    tm_legacy_PerformAerialThink(gobj[1], data + OFST_AERIAL, 0);

    /* aerial sequence done: hold shield */
    if (LG_U8(data, OFST_AERIAL) != 0) {
        LG_U32(fp[1], LG_FT_CPU_BUTTONS) = 0xC0;
    }

    if (timer != 140) {
        goto exit;
    }

reset:
    tm_legacy_Randomize_LeftorRightSide(data, true);
    if (LG_MENU_OPTION(menu, OPT_FACING) == 1) {
        /* P1 faces away: invert the saved facing direction */
        u8* p1 = ss->backup[0][0];
        LG_F32(p1, LG_FT_FACING) = -LG_F32(p1, LG_FT_FACING);
    }
    /* The asm means to keep P1's analog timers (0x620/0x624) across the
     * load, but loads them back from the same place; a no-op, dropped. */
    tm_legacy_SaveState_Load(ss);
    LG_S32(data, OFST_TIMER) = -HSD_Randi(50);
    LG_U32(data, OFST_AERIAL) = 0;

exit:
    tm_legacy_ClearToggledOptions(menu);
    tm_legacy_UpdateAllGFX(gobj[1]);
}

/// "Shield Drop LOAD FUNCT".
static void ShieldDropLoad(void)
{
    StartOSDs();
    tm_legacy_CreateEventThinkFunction(ShieldDropThink, 3, window_info,
                                       window_text);
}

/// "Shield Drop HIJACK INFO".
void tm_legacy_ev_ShieldDrop(TmLegacySetup* s)
{
    tm_legacy_InitializeMatch(s->event, s->md, -1, STAGE_BATTLEFIELD, 0,
                              false);
    s->md->rules.on_match_start = ShieldDropLoad;
}
