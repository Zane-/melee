/**
 * @file
 * TM-CE legacy event Reversal (Custom Event Code - Rewrite.asm, lines
 * 1570-2351): the players reset on random sides of each other and the CPU
 * attacks (option: smash, aerial, tilt, dash attack or getup attack); punish
 * it with a reversal. D-pad left/right moves the reset positions
 * apart/together; the Position option rebuilds the savestate on a platform.
 */
#include "../legacy.h"

#include <melee/ft/kinds/ftCommon/ftCo_DownBound.h>
#include <melee/ft/types.h>
#include <melee/mn/types.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>

/* fighter offsets not in legacy.h */
#define OFST_FT_KIND 0x4       /* s32 internal character id */
#define OFST_FT_CPU_TYPE 0x1A94 /* u8 */
#define OFST_FT_FLAGS_2218 0x2218

#define ASID_SQUAT_RV 0x29
#define ASID_DOWN_BOUND_U 183

/* event data offsets */
#define OFST_FIRST_FRAME 0x0 /* u8 */
#define OFST_TIMER 0x4       /* s32 */
#define OFST_AERIAL 0x20     /* PerformAerialThink state (word); byte 0 =
                                attack done, byte 1 = dash counter */

/* menu options */
#define OPT_CPU_ATTACK 0
#define OPT_P1_FACING 1
#define OPT_CPU_FACING 2
#define OPT_POSITION 3

enum {
    ATK_RANDOM_SMASH,
    ATK_FSMASH,
    ATK_DSMASH,
    ATK_USMASH,
    ATK_RANDOM_AERIAL,
    ATK_FAIR,
    ATK_NAIR,
    ATK_DAIR,
    ATK_FTILT,
    ATK_DTILT,
    ATK_UTILT,
    ATK_DASH_ATTACK,
    ATK_GETUP_STOMACH,
    ATK_GETUP_BACK,
};

/// asm Reversal_Blacklist: per internal character, {FSmash, USmash, DSmash}
/// (1 = never picked by Random Smash Attack).
static const u8 blacklist[][4] = {
    { 0, 0, 0, 0 }, /* Mario */
    { 1, 0, 0, 0 }, /* Fox */
    { 0, 0, 0, 0 }, /* Captain Falcon */
    { 0, 1, 0, 0 }, /* DK */
    { 0, 0, 0, 0 }, /* Kirby */
    { 0, 1, 0, 0 }, /* Bowser */
    { 0, 0, 0, 0 }, /* Link */
    { 1, 0, 0, 0 }, /* Sheik */
    { 0, 1, 1, 0 }, /* Ness */
    { 0, 1, 0, 0 }, /* Peach */
    { 0, 0, 0, 0 }, /* Popo */
    { 0, 0, 0, 0 }, /* Nana */
    { 0, 0, 0, 0 }, /* Pikachu */
    { 0, 1, 0, 0 }, /* Samus */
    { 0, 1, 0, 0 }, /* Yoshi */
    { 0, 1, 0, 0 }, /* Jigglypuff */
    { 0, 1, 0, 0 }, /* Mewtwo */
    { 0, 0, 0, 0 }, /* Luigi */
    { 0, 1, 0, 0 }, /* Marth */
    { 0, 1, 0, 0 }, /* Zelda */
    { 0, 0, 0, 0 }, /* Young Link */
    { 0, 0, 0, 0 }, /* Dr. Mario */
    { 1, 0, 0, 0 }, /* Falco */
    { 0, 0, 0, 0 }, /* Pichu */
    { 0, 0, 1, 0 }, /* Game & Watch */
    { 0, 0, 0, 0 }, /* Ganondorf */
    { 0, 1, 0, 0 }, /* Roy */
};

/// asm ReversalWindowInfo: 4 windows; CPU Attack has 14 options, the
/// facing directions and Position 2 each.
static const u8 window_info[] = { 0x03, 0x0D, 0x01, 0x01, 0x01, 0x00, 0x00,
                                  0x00 };

/// asm ReversalWindowText.
static const char window_text[] = "CPU Attack\0"
                                  "Random Smash Attack\0"
                                  "Forward Smash\0"
                                  "Down Smash\0"
                                  "Up Smash\0"
                                  "Random Aerial\0"
                                  "Fair\0"
                                  "Nair\0"
                                  "Dair\0"
                                  "FTilt\0"
                                  "DTilt\0"
                                  "UTilt\0"
                                  "Dash Attack\0"
                                  "Getup Attack (Stomach)\0"
                                  "Getup Attack (Back)\0"
                                  "P1 Facing Direction\0"
                                  "Towards\0"
                                  "Away\0"
                                  "CP Facing Direction\0"
                                  "Towards\0"
                                  "Away\0"
                                  "Position\0"
                                  "Ground\0"
                                  "Platform\0";

/// Forward (127 or -127) for the CPU's facing direction.
static s8 Forward(Fighter* p2, int magnitude)
{
    return (s8) (magnitude * (s32) LG_F32(p2, LG_FT_FACING));
}

/// asm ReversalDecideSmashAttack and the attacks it branches to. Sets the
/// CPU inputs; returns nothing (the asm then checks the reset timer).
static void Attack(HSD_GObj* p2g, Fighter* p2, u8* data, int attack)
{
    u8* aerial = data + OFST_AERIAL;

    if (attack == ATK_RANDOM_SMASH) {
        /* 0 = FSmash, 1 = USmash, 2 = DSmash; reroll blacklisted ones */
        s32 kind = LG_S32(p2, OFST_FT_KIND);
        s32 pick;
        do {
            pick = HSD_Randi(3);
        } while (kind >= 0 && kind < (s32) (sizeof(blacklist) / 4) &&
                 blacklist[kind][pick] == 1);
        attack = pick == 0   ? ATK_FSMASH
                 : pick == 1 ? ATK_USMASH
                             : ATK_DSMASH;
    }

    switch (attack) {
    case ATK_FSMASH:
        LG_S8(p2, LG_FT_CPU_CSTICK_X) = Forward(p2, 127);
        aerial[0] = 1;
        break;
    case ATK_USMASH:
        /* the asm branches out before marking the attack as done, so the
         * CPU keeps holding up on the C-stick */
        LG_S8(p2, LG_FT_CPU_CSTICK_Y) = 127;
        break;
    case ATK_DSMASH:
        LG_S8(p2, LG_FT_CPU_CSTICK_Y) = -127;
        aerial[0] = 1;
        break;
    case ATK_RANDOM_AERIAL:
        tm_legacy_PerformAerialThink(p2g, aerial, 0);
        break;
    case ATK_FAIR:
    case ATK_NAIR:
    case ATK_DAIR:
        /* PerformAerialThink: 1 fair, 2 nair, 3 dair */
        tm_legacy_PerformAerialThink(p2g, aerial, attack - 4);
        break;
    case ATK_FTILT:
        LG_S8(p2, LG_FT_CPU_ANALOG_X) = Forward(p2, 45);
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x100;
        aerial[0] = 1;
        break;
    case ATK_UTILT:
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = 45;
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x100;
        aerial[0] = 1;
        break;
    case ATK_DTILT:
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -45;
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x100;
        aerial[0] = 1;
        break;
    case ATK_DASH_ATTACK:
        if (aerial[1] == 4) {
            LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x100;
            aerial[0] = 1;
        } else {
            aerial[1]++;
            /* the asm also pushes the stick down (-45) while dashing */
            LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -45;
            LG_S8(p2, LG_FT_CPU_ANALOG_X) = Forward(p2, 127);
            aerial[0] = 0;
        }
        break;
    case ATK_GETUP_STOMACH:
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x100;
        aerial[0] = 1;
        break;
    case ATK_GETUP_BACK:
        /* hack: DownBoundU forces the back getup attack */
        LG_S32(p2, LG_FT_STATE) = ASID_DOWN_BOUND_U;
        ftCo_80097E8C((Fighter_GObj*) p2g);
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x100;
        aerial[0] = 1;
        break;
    }
}

/// "Reversal THINK FUNCT".
static void ReversalThink(HSD_GObj* event)
{
    u8* data = event->user_data;
    u8* menu = LG_PTR(data, LG_EVDATA_MENU);
    TmLegacySaveState* ss = (TmLegacySaveState*) (data + LG_EVDATA_SAVESTATE);
    HSD_GObj* gobj[4];
    Fighter* fp[4];
    s32 timer;
    s32 state;

    tm_legacy_GetAllPlayerPointers(gobj, fp);

    LG_U8(fp[1], OFST_FT_CPU_TYPE) = 0xF;
    tm_legacy_StoreCPUTypeAndZeroInputs(fp[1]);

    if (tm_legacy_CheckIfFirstFrame()) {
        tm_legacy_PlacePlayersCenterStage(tm_legacy_StageGetGroundID_Main());
        tm_legacy_RemoveFirstFrameInputs();
        tm_legacy_SaveState_Save(ss, true);
        LG_U8(data, OFST_FIRST_FRAME) = 1;
        LG_S32(data, OFST_TIMER) = -60;
    }

    tm_legacy_GiveFullShields();

    if (LG_MENU_IS_TOGGLED(menu, OPT_P1_FACING) ||
        LG_MENU_IS_TOGGLED(menu, OPT_CPU_FACING) ||
        LG_MENU_IS_TOGGLED(menu, OPT_CPU_ATTACK))
    {
        goto reset;
    }
    if (LG_MENU_IS_TOGGLED(menu, OPT_POSITION)) {
        goto remake_savestate;
    }
    if (tm_legacy_AdjustResetDistance(ss, fp[0], fp[1]) != -1) {
        goto reset;
    }

    timer = LG_S32(data, OFST_TIMER) + 1;
    LG_S32(data, OFST_TIMER) = timer;

    /* invincible in Wait, SquatRv, or once the IASA flag is set */
    state = LG_S32(fp[1], LG_FT_STATE);
    if (state == LG_ASID_WAIT || state == ASID_SQUAT_RV ||
        (LG_U8(fp[1], OFST_FT_FLAGS_2218) & 0x80))
    {
        tm_legacy_GiveInvincibility(gobj[1], 2);
    }

    if (timer < 45) {
        goto exit;
    }
    if (LG_U8(data, OFST_AERIAL) == 0) {
        Attack(gobj[1], fp[1], data, LG_MENU_OPTION(menu, OPT_CPU_ATTACK));
    }
    if (timer < 150) {
        goto exit;
    }
    goto reset;

remake_savestate: {
    int ground = -1;
    if (LG_MENU_OPTION(menu, OPT_POSITION) != 0) {
        ground = tm_legacy_StageGetGroundID_Platform();
        if (ground >= 0x0FFF) {
            ground = -1;
        }
    }
    if (ground == -1) {
        ground = tm_legacy_StageGetGroundID_Main();
    }
    tm_legacy_PlacePlayersCenterStage(ground);
    tm_legacy_RemoveFirstFrameInputs();
    tm_legacy_SaveState_Save(ss, true);
    LG_U8(data, OFST_FIRST_FRAME) = 1;
    LG_S32(data, OFST_TIMER) = -60;
}

reset: {
    /* asm ReversalSwap: put the players at the saved left/right positions,
     * on a random side, facing each other */
    u8* p1 = ss->backup[0][0];
    u8* p2 = ss->backup[1][0];
    u8* left;
    u8* right;
    f32 lx, ly, rx, ry;

    if (LG_F32(p1, LG_FT_POS_X) > LG_F32(p2, LG_FT_POS_X)) {
        left = p2;
        right = p1;
    } else {
        left = p1;
        right = p2;
    }
    lx = LG_F32(left, LG_FT_POS_X);
    ly = LG_F32(left, LG_FT_POS_Y);
    rx = LG_F32(right, LG_FT_POS_X);
    ry = LG_F32(right, LG_FT_POS_Y);

    if (HSD_Randi(2) == 0) { /* P1 on the left */
        LG_F32(p1, LG_FT_FACING) = 1.0F;
        LG_F32(p1, LG_FT_POS_X) = lx;
        LG_F32(p1, LG_FT_POS_Y) = ly;
        LG_F32(p2, LG_FT_FACING) = -1.0F;
        LG_F32(p2, LG_FT_POS_X) = rx;
        LG_F32(p2, LG_FT_POS_Y) = ry;
    } else { /* P1 on the right */
        LG_F32(p2, LG_FT_FACING) = 1.0F;
        LG_F32(p2, LG_FT_POS_X) = lx;
        LG_F32(p2, LG_FT_POS_Y) = ly;
        LG_F32(p1, LG_FT_FACING) = -1.0F;
        LG_F32(p1, LG_FT_POS_X) = rx;
        LG_F32(p1, LG_FT_POS_Y) = ry;
    }

    if (LG_MENU_OPTION(menu, OPT_P1_FACING) == 1) {
        LG_F32(p1, LG_FT_FACING) = -LG_F32(p1, LG_FT_FACING);
    }
    if (LG_MENU_OPTION(menu, OPT_CPU_FACING) == 1) {
        LG_F32(p2, LG_FT_FACING) = -LG_F32(p2, LG_FT_FACING);
    }

    tm_legacy_SaveState_Load(ss);
    LG_S32(data, OFST_TIMER) = -HSD_Randi(30);
    LG_U32(data, OFST_AERIAL) = 0;

    /* getup attacks start from a knockdown */
    switch (LG_MENU_OPTION(menu, OPT_CPU_ATTACK)) {
    case ATK_GETUP_BACK:
        LG_S32(fp[1], LG_FT_STATE) = ASID_DOWN_BOUND_U;
        /* fallthrough */
    case ATK_GETUP_STOMACH:
        ftCo_80097E8C((Fighter_GObj*) gobj[1]);
        break;
    }
}

exit:
    tm_legacy_ClearToggledOptions(menu);
    tm_legacy_UpdateAllGFX(gobj[1]);
}

/// "Reversal LOAD FUNCT".
static void ReversalLoad(void)
{
    StartOSDs();
    tm_legacy_CreateEventThinkFunction(ReversalThink, 3, window_info,
                                       window_text);
}

/// "Reversal HIJACK INFO".
void tm_legacy_ev_Reversal(TmLegacySetup* s)
{
    tm_legacy_InitializeMatch(s->event, s->md, -1, -1, 0, false);
    s->md->rules.on_match_start = ReversalLoad;
}
