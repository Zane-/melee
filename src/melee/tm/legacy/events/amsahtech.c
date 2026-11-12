/**
 * @file
 * TM-CE legacy event AmsahTech (Custom Event Code - Rewrite.asm, lines
 * 3536-3929): P1 at 120% taunts to place an intangible CPU Marth in front;
 * after the Up B timer Marth up-Bs, and P1 Amsah-techs it. Resets after the
 * reset timer or if anyone dies.
 */
#include "../legacy.h"

#include <melee/ft/ft_081B.h>
#include <melee/ft/ft_0892.h>
#include <melee/ft/ftcommon.h>
#include <melee/gm/types.h>
#include <sysdolphin/baselib/gobj.h>

/// Vanilla statics with unique names.
extern u8 player_slots[]; ///< 0x80453080, P1's static player block

#define MARTH_EXT 0x9

#define ASID_APPEAL_R 0x108
#define ASID_APPEAL_L 0x109
#define CHAR_YLINK 0x14
#define CHAR_DRMARIO 0x15
#define ASID_DRMARIO_APPEAL 0x155
#define ASID_YLINK_APPEAL 0x156

/// AmsahTech_Floats[4]: distance to place Marth from P1 for the up-B.
#define MARTH_DISTANCE 16.0F

/* event data offsets */
#define RESET_TIMER 0x4 /* s32 */
#define UPB_TIMER 0x8   /* s32 */

/* options */
#define OPT_UPB_TIMER 0
#define OPT_RESET_TIMER 1

/// AmsahTechWindowInfo: 2 windows, Up B Timer 2 options, Reset Timer 3.
static const u8 WindowInfo[4] = { 0x01, 0x01, 0x02, 0x00 };
/// AmsahTechWindowText.
static const char WindowText[] = "Up B Timer Frame\0" "30\0" "50\0"
                                 "Reset Timer Frame\0" "120\0" "180\0"
                                 "240";

static bool IsTaunting(Fighter* p1)
{
    s32 state = LG_S32(p1, LG_FT_STATE);
    s32 kind = LG_S32(p1, 0x4);

    if (state == ASID_APPEAL_R || state == ASID_APPEAL_L) {
        return true;
    }
    if (kind == CHAR_DRMARIO && state == ASID_DRMARIO_APPEAL) {
        return true;
    }
    return kind == CHAR_YLINK && state == ASID_YLINK_APPEAL;
}

/// Copy position, facing and ground line into a savestate backup.
static void StoreToBackup(u8* backup, Fighter* fp)
{
    LG_F32(backup, LG_FT_POS_X) = LG_F32(fp, LG_FT_POS_X);
    LG_F32(backup, LG_FT_POS_Y) = LG_F32(fp, LG_FT_POS_Y);
    LG_F32(backup, LG_FT_FACING) = LG_F32(fp, LG_FT_FACING);
    LG_S32(backup, LG_FT_GROUND_ID) = LG_S32(fp, LG_FT_GROUND_ID);
}

/// asm AmsahTechIsTaunting: place Marth 10 Mm in front of P1, set the up-B
/// timer and make this the reset position.
static void PlaceMarth(u8* data, TmLegacySaveState* ss, u8* menu,
                       HSD_GObj* p1g, Fighter* p1, HSD_GObj* p2g, Fighter* p2)
{
    f32 x, y;
    int ground;
    HSD_GObj* sub;
    Fighter* sub_fp;

    if (!tm_legacy_FindGroundNearPlayer(
            NULL,
            10.0F * LG_F32(p1, LG_FT_FACING) + LG_F32(p1, LG_FT_POS_X),
            LG_F32(p1, LG_FT_POS_Y), &x, &y, &ground))
    {
        tm_legacy_PlaySFX(0xAF); /* error */
        return;
    }
    LG_F32(p2, LG_FT_POS_X) = x;
    LG_F32(p2, LG_FT_POS_Y) = y;
    LG_S32(p2, LG_FT_GROUND_ID) = ground;
    LG_F32(p2, LG_FT_FACING) = -LG_F32(p1, LG_FT_FACING);
    ft_8008A2BC(p2g); /* AS_Wait */
    tm_legacy_UpdatePosition(p2g);
    ft_80084280(p2g);
    ftCommon_8007D6A4(p2);

    LG_S32(data, UPB_TIMER) =
        LG_MENU_OPTION(menu, OPT_UPB_TIMER) == 1 ? 50 : 30;

    /* the savestate restores to here from now on */
    StoreToBackup(ss->backup[1][0], p2);
    StoreToBackup(ss->backup[0][0], p1);
    sub = tm_legacy_CheckIfPlayerHasAFollower(p1g, &sub_fp);
    if (sub != NULL) {
        u8* b = ss->backup[0][1];
        LG_F32(b, LG_FT_POS_X) = LG_F32(sub_fp, LG_FT_POS_X);
        LG_F32(b, LG_FT_FACING) = LG_F32(sub_fp, LG_FT_FACING);
    }
}

/// "AmsahTech THINK FUNCT".
static void AmsahTechThink(HSD_GObj* event)
{
    u8* data = event->user_data;
    TmLegacySaveState* ss = (TmLegacySaveState*) (data + LG_EVDATA_SAVESTATE);
    u8* menu = LG_PTR(data, LG_EVDATA_MENU);
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
        tm_legacy_PlacePlayersCenterStage(tm_legacy_StageGetGroundID_Main());
        LG_U16(player_slots, 0x60) = 120; /* P1 at 120% */
        LG_F32(p1, 0x1830) = 120.0F;
        tm_legacy_RemoveFirstFrameInputs();
        tm_legacy_SaveState_Save(ss, true);
    }

    LG_U8(p2, 0x221D) |= 0x04; /* P2 is not nudged */
    tm_legacy_GiveInvincibility(gobj[1], 2);
    tm_legacy_UpdateAllGFX(gobj[1]);

    if (tm_legacy_IsAnyoneDead()) {
        goto restore;
    }

    if (LG_S32(data, RESET_TIMER) == 0 && IsTaunting(p1) &&
        LG_U16(p1, LG_FT_TM_STATE_FRAMES) == 1 &&
        LG_S32(data, UPB_TIMER) == 0 &&
        LG_S32(p2, LG_FT_STATE) == LG_ASID_WAIT)
    {
        PlaceMarth(data, ss, menu, gobj[0], p1, gobj[1], p2);
    } else if (LG_S32(data, UPB_TIMER) > 0) {
        if (--LG_S32(data, UPB_TIMER) == 0) {
            /* in front of P1 again, then up-B */
            LG_F32(p2, LG_FT_POS_X) =
                LG_F32(p1, LG_FT_POS_X) +
                LG_F32(p1, LG_FT_FACING) * MARTH_DISTANCE;
            LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x200;
            LG_S8(p2, LG_FT_CPU_ANALOG_Y) = 127;
            switch (LG_MENU_OPTION(menu, OPT_RESET_TIMER)) {
            case 1:
                LG_S32(data, RESET_TIMER) = 180;
                break;
            case 2:
                LG_S32(data, RESET_TIMER) = 240;
                break;
            default:
                LG_S32(data, RESET_TIMER) = 120;
                break;
            }
        }
    }

    t = LG_S32(data, RESET_TIMER);
    if (t <= 0) {
        return;
    }
    LG_S32(data, RESET_TIMER) = --t;
    if (t != 0) {
        return;
    }

restore:
    tm_legacy_SaveState_Load(ss);
    LG_S32(data, RESET_TIMER) = 0;
    LG_S32(data, UPB_TIMER) = 0;
}

/// "AmsahTech LOAD FUNCT".
static void AmsahTechLoad(void)
{
    StartOSDs();
    tm_legacy_CreateEventThinkFunction(AmsahTechThink, 3, WindowInfo,
                                       WindowText);
}

/// "AmsahTech HIJACK INFO".
void tm_legacy_ev_AmsahTech(TmLegacySetup* s)
{
    tm_legacy_InitializeMatch(s->event, s->md, MARTH_EXT, -1, 0, true);
    s->md->rules.on_match_start = AmsahTechLoad;
}
