/*
 * TM-CE OSDs, MexTK side (osdtech area). Ports of, under
 * ../TrainingMode/ASM/training-mode/Onscreen Display/:
 *
 *   Dashback/Run Out of Tilt Turn.asm
 *   Dashback/Dashback Display - Static Function.asm (0x80005518)
 *   Ledge Codes/Frames Spent in CliffWait.asm
 *   Ledge Codes/Ledgestall/Ledgestall Display.asm
 *   Ledge Codes/GALINT/*.asm (Standalaone - GALINT Display.asm = 0x80005514)
 *   Wavedash Display/Save Airdodge Y Angle.asm
 *   Wavedash Display/Wavedash Timing Display.asm
 *   SDI Display/Initialize Total SDI Inputs Variable.asm
 *   SDI Display/SDI Display Main.asm
 *
 * Called from the native hooks in src/melee/tm/osdtech/osdtech.c, which
 * pass fighters and GObjs as void*. Fighter fields outside FighterData.TM
 * are read at the raw offsets the assembly uses (named below), as in
 * src/tmce/osdcore_vars.c.
 */
#include "events.h"
#include <stddef.h>

/* src/melee/tm/osdcore/osd_core.c, src/tmce/osdcore_vars.c */
int tm_osd_IsFollower(void* fp);
int tmce_osd_IsEnabled(int osd);

/* Vanilla un_804A1F58 (if/if_2FF2.c, the score display's 0x80 bytes),
 * zeroed by un_802FF498 at the start of every match. TM-CE keeps the
 * dashback success counters at +0x70 (asm: 0x804a1fc8, 4 bytes per player),
 * which is what resets them per match; kept there for that reason. */
extern u8 un_804A1F58[];
#define TM_DB_RATES_OFFSET 0x70

/* ---- raw FighterData offsets used by the assembly ---------------------- */
#define FT_U8(fp, off) (*(u8*) ((u8*) (fp) + (off)))
#define FT_U16(fp, off) (*(u16*) ((u8*) (fp) + (off)))
#define FT_INT(fp, off) (*(int*) ((u8*) (fp) + (off)))
#define FT_FLOAT(fp, off) (*(float*) ((u8*) (fp) + (off)))
#define FT_PTR(fp, off) (*(void**) ((u8*) (fp) + (off)))

#define FT_PLY 0xC            /* u8 player slot (message queue) */
#define FT_STATE 0x10         /* current action state */
#define FT_LANDING_LAG 0x1F4  /* float, read by the GALINT aerial path */
#define FT_TIMER_LSTICK_X 0x670 /* u8 */
#define FT_TIMER_LSTICK_Y 0x671 /* u8 */
#define FT_TIMER_JUMP 0x685   /* u8 */
#define FT_ANIM_FRAME_HI 0x894 /* u16, high half of the animation frame */
#define FT_DMG_SOURCE 0x1868  /* GOBJ*, what hit the fighter */
#define FT_HITLAG_LEFT 0x195C /* float */
#define FT_LEDGE_INTANG 0x1990 /* int, ledge intangibility left */
#define FT_ATTACK_INSTANCE 0x2088 /* u16, attacker's current instance */
#define FT_STATE_VAR1 0x2340  /* int */
#define FT_TURN_FLAG 0x2350   /* int, 0 = smash turn */
#define IT_ATTACK_INSTANCE 0xDA8 /* u16, item's current attack instance */

/* ftCommonData (stc_ftcommon) offsets read by the SDI display. */
#define CO_SDI_WINDOW 0x4B4 /* int */

/* GObj entity classes (asm: lhz r0,0(gobj)). */
#define GOBJ_FIGHTER 4
#define GOBJ_ITEM 6

/* Globals.s ASID_* */
#define TM_AS_JUMPF 0x19
#define TM_AS_JUMPB 0x1A
#define TM_AS_DASH 0x14
#define TM_AS_SQUATWAIT 0x28
#define TM_AS_ESCAPEAIR 0xEC
#define TM_AS_CLIFFWAIT 0xFD

/* Globals.s OSD.* bit numbers in MemcardData+0x1F24 */
#define TM_OSD_WAVEDASH 0
#define TM_OSD_DASHBACK 5
#define TM_OSD_SDI 10
#define TM_OSD_LEDGE 26

#define TM_COLOR_GREEN 0x8dff6eff
#define TM_COLOR_YELLOW 0xfff000ff
#define TM_COLOR_RED 0xffa2baff /* 255, 162, 186, 255 */

#define BUTTON_XY 0xC00

static void SetColor(Text* text, int subtext, u32 rgba)
{
    GXColor c;
    c.r = rgba >> 24;
    c.g = rgba >> 16;
    c.b = rgba >> 8;
    c.a = rgba;
    Text_SetColor(text, subtext, &c);
}

static Text* MessageText(GOBJ* msg)
{
    /* lwz r3, 0x2C(r3); lwz r3, MsgData_Text(r3) */
    return *(Text**) msg->userdata;
}

/* ---- Dashback ----------------------------------------------------------- */

/* GetDBRate: successful / total * 100, truncated (single precision). */
static int DashbackRate(u16* rate)
{
    float ok = rate[0];
    float total = rate[1];
    float hundred = 100;
    return (int) (ok / total * hundred);
}

static u16* DashbackCounters(FighterData* fp)
{
    return (u16*) (un_804A1F58 + TM_DB_RATES_OFFSET + FT_U8(fp, FT_PLY) * 4);
}

/* Dashback Display - Static Function.asm (0x80005518). */
static void DisplayDashback(GOBJ* gobj, int dashed_back)
{
    FighterData* fp = gobj->userdata;
    u16* rate;
    char* text;
    u32 color;
    GOBJ* msg;

    if (!tmce_osd_IsEnabled(TM_OSD_DASHBACK)) {
        return;
    }
    if (tm_osd_IsFollower(fp)) {
        return;
    }

    rate = DashbackCounters(fp);
    if (dashed_back) {
        /* IncDBRate */
        rate[0]++;
        rate[1]++;
        if (FT_INT(fp, FT_TURN_FLAG) == 0) {
            text = "Vanilla Dashback\nSuccess Rate: %d%";
            color = TM_COLOR_GREEN;
        } else {
            text = "UCF Dashback\nSuccess Rate: %d%";
            color = TM_COLOR_YELLOW;
        }
    } else {
        /* DecDBRate */
        rate[1]++;
        text = "Failed Dashback\nSuccess Rate: %d%";
        color = TM_COLOR_RED;
    }

    msg = Message_Display(4, FT_U8(fp, FT_PLY), MSGCOLOR_WHITE, text,
                          DashbackRate(rate));
    SetColor(MessageText(msg), 0, color);
}

/* Run Out of Tilt Turn.asm (ftCo_Turn_IASA+0x190, before ftCo_Dash_Enter). */
void tmce_osdtech_TurnToDash(GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    u16 prev = fp->TM.state_prev[0];

    /* not coming from Dash or SquatWait */
    if (prev == TM_AS_DASH || prev == TM_AS_SQUATWAIT) {
        return;
    }
    /* dashed back: the turn's animation frame is exactly 2 (0x4000xxxx) */
    DisplayDashback(gobj, FT_U16(fp, FT_ANIM_FRAME_HI) == 0x4000);
}

/* ---- Ledge Codes -------------------------------------------------------- */

/* Frames Spent in CliffWait.asm (ftCo_8009AAFC+0x7C): dropping from
 * CliffWait into Fall. */
void tmce_osdtech_CliffWaitFall(FighterData* fp)
{
    u16 frames;
    int color;

    if (!tmce_osd_IsEnabled(TM_OSD_LEDGE)) {
        return;
    }
    if (tm_osd_IsFollower(fp)) {
        return;
    }
    frames = fp->TM.state_frame;
    if (frames > 20) {
        return;
    }
    color = frames - 1 == 1 ? MSGCOLOR_GREEN : MSGCOLOR_RED;
    Message_Display(13, FT_U8(fp, FT_PLY), color, "Frames in\nCliffwait: %d",
                    frames - 1);
}

/* Ledgestall Display.asm (ftCliffCommon_80081370+0x17C): grabbed the
 * ledge; how many frames the fighter was vulnerable. */
void tmce_osdtech_Ledgestall(FighterData* fp)
{
    int vuln;

    if (!tmce_osd_IsEnabled(TM_OSD_LEDGE)) {
        return;
    }
    if (tm_osd_IsFollower(fp)) {
        return;
    }
    vuln = fp->TM.vuln_frames - 1;
    if (vuln > 15) {
        return;
    }
    if (vuln <= 0) {
        Message_Display(19, FT_U8(fp, FT_PLY), MSGCOLOR_GREEN,
                        "Ledgestall\nPerfect", vuln);
    } else {
        Message_Display(19, FT_U8(fp, FT_PLY), MSGCOLOR_RED,
                        "Ledgestall\nVulnerable: %d", vuln);
    }
}

/* Standalaone - GALINT Display.asm (0x80005514): ledge intangibility left
 * when landing, minus the landing lag for an aerial interrupt. */
static void DisplayGalint(GOBJ* gobj, int aerial_interrupt)
{
    FighterData* fp = gobj->userdata;
    int galint;
    int color;
    int value;

    if (!tmce_osd_IsEnabled(TM_OSD_LEDGE)) {
        return;
    }
    if (tm_osd_IsFollower(fp)) {
        return;
    }
    /* TM_TangibleFrameCount: no more than 20 frames past GALINT */
    if (fp->TM.vuln_frames > 20) {
        return;
    }
    galint = FT_INT(fp, FT_LEDGE_INTANG);
    if (aerial_interrupt) {
        galint -= (int) FT_FLOAT(fp, FT_LANDING_LAG);
    }
    color = MSGCOLOR_RED;
    value = -fp->TM.vuln_frames;
    if (galint > 0) {
        color = MSGCOLOR_GREEN;
        value = galint;
    }
    Message_Display(19, FT_U8(fp, FT_PLY), color, "GALINT\nFrames: %d",
                    value);
}

/* GALINT Aerail Interrupt.asm (ftCo_LandingAir_EnterWithLag+0xF8). */
void tmce_osdtech_GalintAerialInterrupt(GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    if (fp->TM.state_prev[2] == TM_AS_CLIFFWAIT) {
        DisplayGalint(gobj, 1);
    }
}

/* GALINT Laser Land.asm (ftCo_AirCatchHit_Coll+0xC8): CliffWait in any of
 * the last six states. */
void tmce_osdtech_GalintLaserLand(GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    int i;
    for (i = 0; i <= 5; i++) {
        if (fp->TM.state_prev[i] == TM_AS_CLIFFWAIT) {
            DisplayGalint(gobj, 0);
            return;
        }
    }
}

/* GALINT Ledgedash.asm (ftCo_Landing_Anim+0x20): airdodge out of a ledge
 * drop. */
void tmce_osdtech_GalintLedgedash(GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    if (fp->TM.state_prev[0] == TM_AS_ESCAPEAIR &&
        fp->TM.state_prev[3] == TM_AS_CLIFFWAIT)
    {
        DisplayGalint(gobj, 0);
    }
}

/* GALINT No Impact Land.asm (ft_80082B1C+0x30). */
void tmce_osdtech_GalintNoImpactLand(GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    if (fp->TM.state_prev[1] == TM_AS_CLIFFWAIT) {
        DisplayGalint(gobj, 0);
    }
}

/* ---- Wavedash Display --------------------------------------------------- */

/* Save Airdodge Y Angle.asm (ftCo_80099A9C+0xD8): entering EscapeAir, before
 * state_var1 (the jump's short/full hop flag) is overwritten. @p angle is
 * Joystick_Angle_Retrieve(fp), radians. */
void tmce_osdtech_SaveAirdodge(FighterData* fp, float angle)
{
    int state = FT_INT(fp, FT_STATE);

    fp->TM.tm_union.wavedash.airdodge_angle = angle;
    if (state == TM_AS_JUMPF || state == TM_AS_JUMPB) {
        /* state_var1: 0 = full hop, 1 = short hop */
        fp->TM.tm_union.wavedash.hop_type = FT_INT(fp, FT_STATE_VAR1);
    } else {
        fp->TM.tm_union.wavedash.hop_type = 2;
    }
}

/* GetWavedashAngle: radians to degrees, floored to one decimal, folded into
 * 0-90 (angle from the ground). */
static float WavedashAngle(float rad)
{
    /* rtoc-0x3D10, 0x3C8EFA35 */
    float deg_per_rad = 0.017453292F;
    float a = rad / deg_per_rad;
    float ten = 10;
    int tenths = (int) (a * ten);

    a = (float) tenths / ten;
    if (a >= 0) {
        if (a > 90) {
            a = 180 - a;
        }
    } else if (a > -90) {
        a = -a;
    } else {
        a = 180 + a;
    }
    return a;
}

/* Wavedash Timing Display.asm (ftCo_80099D70+0xC): landing out of an
 * airdodge into LandingFallSpecial. */
void tmce_osdtech_WavedashLand(GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    float angle;
    int frames;
    int hop;
    char* hop_text;
    int i;
    int held;
    int have_hop;
    GOBJ* msg;
    Text* text;

    if (!tmce_osd_IsEnabled(TM_OSD_WAVEDASH)) {
        return;
    }
    if (tm_osd_IsFollower(fp)) {
        return;
    }
    /* a wavedash: landed within 20 frames of the airdodge */
    if ((u16) fp->TM.state_frame > 20) {
        return;
    }

    angle = WavedashAngle(fp->TM.tm_union.wavedash.airdodge_angle);
    frames = fp->TM.state_prev_frames[0]; /* frames in the jump */

    /* asm: lwz + cmpwi (signed); 1 = short hop, other values <= 1 = full */
    hop = fp->TM.tm_union.wavedash.hop_type;
    have_hop = 0;
    if (hop <= 1) {
        hop_text = hop == 1 ? "Short Hop" : "Full Hop";
        /* frames the jump input was held: the newest input with X/Y or the
         * stick up */
        for (i = 0; i < 32; i++) {
            if ((fp->TM.inputs[i].buttons & BUTTON_XY) ||
                fp->TM.inputs[i].stick_y > 24)
            {
                held = FT_U8(fp, FT_TIMER_JUMP) - i + 1;
                have_hop = 1;
                break;
            }
        }
        /* no jump input in the history: wavedash took over 32 frames */
    }

    if (have_hop) {
        msg = Message_Display(0, FT_U8(fp, FT_PLY), MSGCOLOR_WHITE,
                              "Wavedash Frame: %d\nAngle: %2.1f\n%s: %df",
                              frames, (double) angle, hop_text, held);
        text = MessageText(msg);
        if (hop != 0) {
            SetColor(text, 2, TM_COLOR_GREEN);
        }
    } else {
        msg = Message_Display(0, FT_U8(fp, FT_PLY), MSGCOLOR_WHITE,
                              "Wavedash Frame: %d\nAngle: %2.1f", frames,
                              (double) angle);
        text = MessageText(msg);
    }

    if (fp->TM.state_prev_frames[0] == 1) {
        SetColor(text, 0, TM_COLOR_GREEN);
    }
    if (angle < 16.8F) {
        return;
    }
    if (angle < 23.7F) {
        SetColor(text, 1, TM_COLOR_GREEN);
    } else if (!(angle > 30.5F)) {
        SetColor(text, 1, TM_COLOR_YELLOW);
    }
}

/* ---- SDI Display -------------------------------------------------------- */

/* Initialize Total SDI Inputs Variable.asm (ftCo_8008EC90+0xA8C, the common
 * exit of the damage handler): a new move hitting the fighter resets the
 * SDI counters. */
void tmce_osdtech_SdiReset(GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    GOBJ* source = FT_PTR(fp, FT_DMG_SOURCE);
    u16 instance;

    /* no source: environmental damage (e.g. Break the Targets walls) */
    if (source != NULL) {
        u16 kind = *(u16*) source;
        if (kind == GOBJ_FIGHTER) {
            instance = FT_U16(source->userdata, FT_ATTACK_INSTANCE);
        } else if (kind == GOBJ_ITEM) {
            instance = FT_U16(source->userdata, IT_ATTACK_INSTANCE);
        } else {
            return;
        }
        /* instance 0: most likely a stage element (Corneria lasers) */
        if (instance != 0 && fp->TM.last_move_hurt == instance) {
            return;
        }
    }
    fp->TM.tm_union.sdi.successful_sdi_inputs = 0;
    fp->TM.tm_union.sdi.total_sdi_inputs = 0;
}

/* SDI Display Main.asm (ftCo_Damage_OnEveryHitlag+0x3C): every hitlag frame
 * that allows SDI, before vanilla applies it. @p stick_sq is the left
 * stick's squared magnitude and @p min_sq the squared SDI threshold, as
 * vanilla computes them (f1, f0 at the site). */
void tmce_osdtech_SdiHitlag(FighterData* fp, float stick_sq, float min_sq)
{
    int window;
    int color;

    if (!tmce_osd_IsEnabled(TM_OSD_SDI)) {
        return;
    }
    if (tm_osd_IsFollower(fp)) {
        return;
    }

    window = *(int*) ((u8*) *stc_ftcommon + CO_SDI_WINDOW);
    if (stick_sq >= min_sq && (FT_U8(fp, FT_TIMER_LSTICK_X) < window ||
                               FT_U8(fp, FT_TIMER_LSTICK_Y) < window))
    {
        fp->TM.tm_union.sdi.successful_sdi_inputs++;
    }
    fp->TM.tm_union.sdi.total_sdi_inputs++;

    color = fp->TM.tm_union.sdi.successful_sdi_inputs != 0 ? MSGCOLOR_GREEN
                                                           : MSGCOLOR_RED;
    /* only on the last hitlag frame (exactly 1.0) */
    if (FT_INT(fp, FT_HITLAG_LEFT) != 0x3F800000) {
        return;
    }
    Message_Display(-1, FT_U8(fp, FT_PLY), color, "SDI Inputs\n%d/%d",
                    fp->TM.tm_union.sdi.successful_sdi_inputs,
                    fp->TM.tm_union.sdi.total_sdi_inputs);
}
