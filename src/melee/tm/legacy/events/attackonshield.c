/**
 * @file
 * TM-CE legacy event Attack On Shield (Custom Event Code - Rewrite.asm,
 * lines 2604-3016): the CPU holds shield on Final Destination; when it gets
 * out of shieldstun it does the out-of-shield option chosen in the pause
 * menu, then the positions reset (P1 at a random distance, random side).
 */
#include "../legacy.h"

#include <melee/ft/types.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>

#define STAGE_FINAL_DESTINATION 0x20

#define ASID_KNEE_BEND 0x18
#define ASID_JUMP_F 0x19
#define ASID_DAMAGE_HI1 0x4B
#define ASID_DAMAGE_FLY_ROLL 0x5B
#define ASID_GUARD 0xB3        /* ShieldWait */
#define ASID_GUARD_SET_OFF 0xB5 /* shieldstun */

#define BTN_A 0x100
#define BTN_B 0x200
#define BTN_LR 0xC0 /* asm "Hit L"/"Press R": both shoulder bits */

#define RESET_TIMER 48

/* event data offsets */
#define OFST_FIRST_FRAME 0x0 /* u8 */
#define OFST_TIMER 0x4       /* s32 */

/* option 0 of the menu */
enum {
    OOS_GRAB,
    OOS_NAIR,
    OOS_UPB,
    OOS_UPSMASH,
    OOS_SHINE,
    OOS_SPOTDODGE,
    OOS_ROLL_AWAY,
    OOS_ROLL_TOWARDS,
    OOS_WAVEDASH,
    OOS_NONE,
};

/// "AttackOnShield_Floats": P1 X, P2 X, P1 Y, P2 Y; then the random P1 X
/// range (bytes 0x14, 0x46: 20 to 70).
static const f32 positions[4] = { -20.0F, 20.0F, 0.0001F, 0.0001F };
#define RAND_X_START 20
#define RAND_X_END 70

/// "AttackOnShieldWindowInfo": one option with 10 values.
static const u8 window_info[4] = { 0x00, 0x09, 0xFF, 0xFF };
/// "AttackOnShieldWindowText".
static const char window_text[] = "OoS Option\0"
                                  "Grab\0"
                                  "Nair\0"
                                  "Up B\0"
                                  "Up Smash\0"
                                  "Shine\0"
                                  "Spotdodge\0"
                                  "Roll Away\0"
                                  "Roll Towards\0"
                                  "Wavedash Away";

static void SetTimer(u8* data)
{
    LG_S32(data, OFST_TIMER) = RESET_TIMER;
}

/// "AttackOnShieldShieldWait" onwards: hold shield, react to shieldstun.
/// Returns false when the think should exit straight away (no timer step).
static bool ShieldWait(u8* data, u8* menu, Fighter* p1, Fighter* p2)
{
    s32 state = LG_S32(p2, LG_FT_STATE);

    LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_LR; /* always hold L */

    /* shield poked: in hitlag and in a damage state */
    if ((LG_U8(p2, 0x221A) & 0x20) && state >= ASID_DAMAGE_HI1 &&
        state <= ASID_DAMAGE_FLY_ROLL)
    {
        SetTimer(data);
        return false;
    }

    /* just left shieldstun into ShieldWait */
    if (state != ASID_GUARD ||
        LG_U16(p2, LG_FT_TM_PREV_STATES) != ASID_GUARD_SET_OFF)
    {
        return true;
    }

    switch (LG_MENU_OPTION(menu, 0)) {
    default:
    case OOS_GRAB:
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0x1C0; /* R + A */
        break;
    case OOS_NAIR:
    case OOS_SHINE:
    case OOS_WAVEDASH:
        LG_U32(p2, LG_FT_CPU_BUTTONS) = 0xCC0; /* jump (X/Y) */
        break;
    case OOS_UPB:
    case OOS_UPSMASH:
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = 127;
        break;
    case OOS_SPOTDODGE:
        LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -127;
        LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_LR;
        break;
    case OOS_ROLL_AWAY:
        LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_LR;
        LG_S8(p2, LG_FT_CPU_ANALOG_X) =
            tm_legacy_GetDirectionInRelationToP1(p1, p2) * 127;
        break;
    case OOS_ROLL_TOWARDS:
        LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_LR;
        LG_S8(p2, LG_FT_CPU_ANALOG_X) =
            tm_legacy_GetDirectionInRelationToP1(p1, p2) * -127;
        break;
    case OOS_NONE:
        return false;
    }
    SetTimer(data);
    return false;
}

/// "AttackOnShield THINK FUNCT".
static void AttackOnShieldThink(HSD_GObj* event)
{
    u8* data = event->user_data;
    u8* menu = LG_PTR(data, LG_EVDATA_MENU);
    TmLegacySaveState* ss = (TmLegacySaveState*) (data + LG_EVDATA_SAVESTATE);
    HSD_GObj* gobj[4];
    Fighter* fp[4];
    Fighter* p1;
    Fighter* p2;
    s32 state;
    s32 t;

    tm_legacy_GetAllPlayerPointers(gobj, fp);
    p1 = fp[0];
    p2 = fp[1];
    tm_legacy_StoreCPUTypeAndZeroInputs(p2);

    if (tm_legacy_CheckIfFirstFrame()) {
        LG_U8(data, OFST_FIRST_FRAME) = 1;
        tm_legacy_InitializePositions(positions, gobj[0], gobj[1]);
        tm_legacy_RemoveFirstFrameInputs();
        tm_legacy_SaveState_Save(ss, true);
    }

    tm_legacy_GiveFullShields();

    if (tm_legacy_IsAnyoneDead()) {
        tm_legacy_SaveState_Load(ss);
        goto exit;
    }

    /* option changed: forget the last state so the CPU doesn't act now */
    if (LG_MENU_IS_TOGGLED(menu, 0)) {
        LG_U16(p2, LG_FT_TM_PREV_STATES) = 0;
    }

    state = LG_S32(p2, LG_FT_STATE);
    if (LG_S32(data, OFST_TIMER) > 0) {
        /* performing the out-of-shield option */
        switch (LG_MENU_OPTION(menu, 0)) {
        case OOS_NAIR:
            if (state == ASID_JUMP_F) {
                LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_A;
            }
            break;
        case OOS_UPB:
            if (state == ASID_KNEE_BEND) {
                LG_S8(p2, LG_FT_CPU_ANALOG_Y) = 127;
                LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_B;
            }
            break;
        case OOS_UPSMASH:
            if (state == ASID_KNEE_BEND) {
                LG_S8(p2, LG_FT_CPU_ANALOG_Y) = 127;
                LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_A;
            }
            break;
        case OOS_SHINE:
            if (state == ASID_JUMP_F) {
                LG_S8(p2, LG_FT_CPU_ANALOG_Y) = -127;
                LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_B;
            }
            break;
        case OOS_WAVEDASH:
            if (state == ASID_JUMP_F) {
                s32 x, y;
                tm_legacy_ConvertAngle(HSD_Randi(30) + 310, &x, &y);
                LG_S8(p2, LG_FT_CPU_ANALOG_X) =
                    tm_legacy_GetDirectionInRelationToP1(p1, p2) * x;
                LG_S8(p2, LG_FT_CPU_ANALOG_Y) = y;
                LG_U32(p2, LG_FT_CPU_BUTTONS) = BTN_LR;
            }
            break;
        default:
            if (!ShieldWait(data, menu, p1, p2)) {
                goto exit;
            }
            break;
        }
    } else if (!ShieldWait(data, menu, p1, p2)) {
        goto exit;
    }

    /* "AttackOnShieldCheckToReset" */
    t = LG_S32(data, OFST_TIMER);
    if (t > 0) {
        t--;
        LG_S32(data, OFST_TIMER) = t;
        if (t == 0) {
            /* random P1 distance, random side */
            u8* p1_backup = LG_PTR(data, LG_EVDATA_SAVESTATE);
            LG_F32(p1_backup, LG_FT_POS_X) =
                (f32) (HSD_Randi(RAND_X_END - RAND_X_START) + RAND_X_START);
            tm_legacy_Randomize_LeftorRightSide(data, true);
            tm_legacy_SaveState_Load(ss);
        }
    }

exit:
    tm_legacy_ClearToggledOptions(menu);
}

/// "Attack On Shield LOAD FUNCT".
static void AttackOnShieldLoad(void)
{
    StartOSDs();
    tm_legacy_CreateEventThinkFunction(AttackOnShieldThink, 3, window_info,
                                       window_text);
}

/// "Attack On Shield HIJACK INFO".
void tm_legacy_ev_AttackOnShield(TmLegacySetup* s)
{
    tm_legacy_InitializeMatch(s->event, s->md, -1, STAGE_FINAL_DESTINATION,
                              0, false);
    s->md->rules.on_match_start = AttackOnShieldLoad;
}
