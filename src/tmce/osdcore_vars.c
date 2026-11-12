/*
 * TM-CE OSD core, MexTK side (osdcore area). Ports of:
 *
 *   Onscreen Display/Additional Playerblock Variables/** (FighterData.TM)
 *   Onscreen Display/Generic Per Frame.asm
 *   Onscreen Display/Act OoWait/Act OOWait- Standalone.asm (0x8000551C)
 *   Onscreen Display/Additional Playerblock Variables/Fastfall Timer/
 *       Display FF Timing.asm
 *
 * Called from the native hooks in src/melee/tm/osdcore/ (decomp side), which
 * pass the fighter as void*. Fighter fields outside FighterData.TM are read
 * at the raw offsets the assembly uses (named below), so the logic matches
 * the assembly one to one.
 */
#include "events.h"
#include <stddef.h>

/* src/melee/tm/osdcore/osd_core.c */
int tm_osd_IsFollower(void* fp);

/* ---- raw FighterData offsets used by the assembly ---------------------- */
#define FT_U8(fp, off) (*(u8*) ((u8*) (fp) + (off)))
#define FT_S8(fp, off) (*(s8*) ((u8*) (fp) + (off)))
#define FT_INT(fp, off) (*(int*) ((u8*) (fp) + (off)))
#define FT_FLOAT(fp, off) (*(float*) ((u8*) (fp) + (off)))
#define FT_PTR(fp, off) (*(void**) ((u8*) (fp) + (off)))

#define FT_KIND 0x4           /* internal fighter kind */
#define FT_PLY 0xC            /* u8 player slot (message queue) */
#define FT_STATE 0x10         /* current action state */
#define FT_AIR_STATE 0xE0     /* 1 = airborne */
#define FT_JUMP_STARTUP 0x148 /* float, jump squat length (attributes) */
#define FT_MAX_JUMPS 0x168    /* int (attributes) */
#define FT_ANIM_DATA 0x590    /* animation; +0x8 = float length */
#define FT_PAD_INDEX 0x618    /* u8 */
#define FT_LSTICK_Y 0x624     /* float */
#define FT_BUTTONS_DOWN 0x668 /* u32, pressed this frame */
#define FT_TIMER_TILT_Y 0x671 /* u8 */
#define FT_TIMER_SMASH_Y 0x674 /* u8 */
#define FT_TIMER_JUMP 0x685    /* u8 */
#define FT_ANIM_FRAME 0x894    /* float */
#define FT_JUMPS_USED 0x1968   /* u8 */
#define FT_HURT_SCRIPT 0x1988  /* int, hurt kind set by the script */
#define FT_INTANG_LEDGE 0x1990 /* int, timer intangibility */
#define FT_DMG_INSTANCE 0x18EC /* u16, last attack instance hit by */
#define FT_FLAGS_2219 0x2219   /* 0x04 = frozen (hitlag) */

/* ftCommonData (stc_ftcommon) offsets read by CheckForJumpCancel. */
#define CO_JUMP_STICK_Y 0x70 /* float */
#define CO_JUMP_TIMER 0x74   /* int */

/* Internal fighter kinds (Globals.s Fox.Int etc.). */
#define TM_FT_FOX 0x1
#define TM_FT_SHEIK 0x7
#define TM_FT_PEACH 0x9
#define TM_FT_YOSHI 0xE
#define TM_FT_FALCO 0x16

/* Globals.s ASID_* */
enum {
    TM_AS_REBIRTHWAIT = 0x0D,
    TM_AS_WAIT = 0x0E,
    TM_AS_WALKSLOW = 0x0F,
    TM_AS_WALKMIDDLE = 0x10,
    TM_AS_WALKFAST = 0x11,
    TM_AS_TURN = 0x12,
    TM_AS_JUMPF = 0x19,
    TM_AS_JUMPB = 0x1A,
    TM_AS_SQUAT = 0x27,
    TM_AS_SQUATWAIT = 0x28,
    TM_AS_LANDING = 0x2A,
    TM_AS_LANDINGFALLSPECIAL = 0x2B,
    TM_AS_ATTACKLW3 = 0x39,
    TM_AS_ATTACKLW4 = 0x40,
    TM_AS_ATTACKAIRN = 0x41,
    TM_AS_ATTACKAIRLW = 0x45,
    TM_AS_LANDINGAIRN = 0x46,
    TM_AS_LANDINGAIRLW = 0x4A,
    TM_AS_GUARDON = 0xB2,
    TM_AS_DOWNBOUNDU = 0xB7,
    TM_AS_PASSIVESTANDB = 0xC9,
    TM_AS_THROWF = 0xDB,
    TM_AS_THROWLW = 0xDE,
};

/* Globals.s OSD.* bit numbers in MemcardData+0x1F24 */
#define TM_OSD_FIGHTERSPECIFICTECH 8
#define TM_OSD_LOCKOUTTIMERS 12
#define TM_OSD_ACTOOWAIT 16
#define TM_OSD_FASTFALL 20
#define TM_OSD_FIGHTERSPECIFICTECHALT 64

#define TM_COLOR_GREEN 0x8dff6eff
#define TM_COLOR_RED 0xffa2baff

#define BUTTON_B 0x200
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

/* The "CHECK IF ENABLED" block every OSD starts with. */
int tmce_osd_IsEnabled(int osd)
{
    return (stc_memcard->TM_OSDEnabled >> osd) & 1;
}

/* MemcardData+0x1F28, used as the window count by Display Message 2.0. */
int tmce_osd_MaxWindows(void)
{
    return stc_memcard->TM_OSDPosition;
}

/* ---- StatesAndTimers/ShiftStates.asm (Fighter_ChangeMotionState+0x40) ---
 * Runs before the new state is stored: push the state being left and its
 * frame count onto the six-entry history, reset the current frame count. */
void tmce_osd_ShiftStates(FighterData* fp)
{
    int i;
    for (i = 6 - 2; i >= 0; i--) {
        fp->TM.state_prev[i + 1] = fp->TM.state_prev[i];
    }
    fp->TM.state_prev[0] = FT_INT(fp, FT_STATE);
    for (i = 6 - 2; i >= 0; i--) {
        fp->TM.state_prev_frames[i + 1] = fp->TM.state_prev_frames[i];
    }
    fp->TM.state_prev_frames[0] = fp->TM.state_frame;
    fp->TM.state_frame = 0;
}

/* ---- Fastfall Timer/Initialize Fastfall Variable.asm
 * (Fighter_ChangeMotionState+0x51C, where fall_fast is cleared). */
void tmce_osd_ResetFastfall(FighterData* fp)
{
    fp->TM.can_fastfall_frames = 0;
}

/* ---- StatesAndTimers/IncFrameCounts.asm (Fighter_procAnim+0x818) ------- */
void tmce_osd_IncFrameCounts(FighterData* fp)
{
    HSD_Pad* pad;
    u8* in;

    /* Don't run during hitlag */
    if (FT_U8(fp, FT_FLAGS_2219) & 0x04) {
        return;
    }

    fp->TM.state_frame++;

    /* Tangible frames: reset while intangible from a timer, or when the
     * script makes the fighter intangible before any tangible frame. */
    if (FT_INT(fp, FT_INTANG_LEDGE) > 0 ||
        (fp->TM.vuln_frames == 0 && FT_INT(fp, FT_HURT_SCRIPT) == 2))
    {
        fp->TM.vuln_frames = 0;
    } else {
        fp->TM.vuln_frames++;
    }

    /* Input history: newest first, 32 entries of 8 bytes. */
    memmove(&fp->TM.inputs[1], &fp->TM.inputs[0], 0xF8);
    pad = &stc_engine_pads->pad[FT_U8(fp, FT_PAD_INDEX)];
    in = (u8*) &fp->TM.inputs[0];
    *(u16*) in = pad->held; /* sth of the held word: low 16 bits */
    in[2] = pad->stickX;
    in[3] = pad->stickY;
    in[4] = pad->substickX;
    in[5] = pad->substickY;
    in[6] = pad->triggerLeft;
    in[7] = pad->triggerRight;
}

/* ---- Fastfall Timer/Increment Fastfall Variable.asm
 * (ftCommon_CheckFallFast+0x28: not fastfalling and moving down). */
void tmce_osd_IncFastfall(FighterData* fp)
{
    fp->TM.can_fastfall_frames++;
}

/* ---- Fastfall Timer/Display FF Timing.asm (ftCommon_CheckFallFast+0x54,
 * the frame fastfall starts). */
void tmce_osd_DisplayFastfall(FighterData* fp)
{
    GOBJ* msg;

    if (!tmce_osd_IsEnabled(TM_OSD_FASTFALL)) {
        return;
    }
    if (tm_osd_IsFollower(fp)) {
        return;
    }
    /* falling from a respawn platform */
    if (fp->TM.state_prev[0] == TM_AS_REBIRTHWAIT) {
        return;
    }
    msg = Message_Display(7, FT_U8(fp, FT_PLY), MSGCOLOR_WHITE,
                          "Fastfall\nFrame %d", fp->TM.can_fastfall_frames);
    if (fp->TM.can_fastfall_frames == 1) {
        SetColor(MessageText(msg), 1, TM_COLOR_GREEN);
    }
}

/* ---- Frame Advantage/Save Pointer to Shield Owner On Hit.asm
 * (ftColl_80076CBC+0x1F0): attacker's hitbox hit shield_owner's shield. */
void tmce_osd_SetShieldOwner(FighterData* attacker, FighterData* shield_owner)
{
    attacker->TM.fighter_hurt_shield = shield_owner;
}

/* ---- Previous Move Instance Hit By/Backup Previous Move Instance Player
 * was Hit By.asm (pl_80038144+0xC8), before the victim's attack instance
 * is updated.
 *
 * Deliberate fix: TM-CE stores to a hard-coded 0x2418 (can_fastfall_frames),
 * so TM_PreviousMoveInstanceHitBy (0x2414, read by the SDI display) was
 * always 0. This stores where the SDI display reads. */
void tmce_osd_BackupMoveInstance(FighterData* victim)
{
    victim->TM.last_move_hurt = *(u16*) ((u8*) victim + FT_DMG_INSTANCE);
}

/* ---- Act OoWait/Act OOWait- Standalone.asm (0x8000551C) ---------------- */
void tmce_osd_ActOoWait(GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    char* text;
    int frames;
    int before;
    int kind;
    int i;
    int j;
    GOBJ* msg;

    if (tm_osd_IsFollower(fp)) {
        return;
    }

    for (i = 0;; i++) {
        int s = fp->TM.state_prev[i];
        if (s == TM_AS_WAIT) {
            text = "Act OoWait\nFrame: %d";
            frames = 1;
            break;
        }
        if (s == TM_AS_LANDING) {
            text = "Act OoAutocancel\nFrame: %d";
            frames = -3;
            break;
        }
        if (i + 1 >= 6) {
            return;
        }
    }

    /* State before Wait. For i == 5 the assembly reads the next halfword,
     * state_prev_frames[0]; kept. */
    before = (i + 1 < 6) ? fp->TM.state_prev[i + 1]
                         : fp->TM.state_prev_frames[0];

    for (j = i; j >= 0; j--) {
        int s = fp->TM.state_prev[j];
        if (s == TM_AS_TURN) {
            frames--; /* one unavoidable frame */
        }
        if (s == TM_AS_WAIT) {
            frames--; /* pseudo Wait frame */
        }
        frames += fp->TM.state_prev_frames[j];
    }

    if (frames > 13) {
        return;
    }

    /* Only from throws, aerial landings, techs/getups, wavedashes, lasers,
     * needles, Peach's float-cancel aerials and aerials. */
    kind = FT_INT(fp, FT_KIND);
    if (!((before >= TM_AS_LANDINGAIRN && before <= TM_AS_LANDINGAIRLW) ||
          (before >= TM_AS_THROWF && before <= TM_AS_THROWLW) ||
          (before >= TM_AS_DOWNBOUNDU && before <= TM_AS_PASSIVESTANDB) ||
          before == TM_AS_LANDINGFALLSPECIAL ||
          (before >= 341 && before <= 346 &&
           (kind == TM_FT_FOX || kind == TM_FT_FALCO)) ||
          (before >= 341 && before <= 348 && kind == TM_FT_SHEIK) ||
          (before >= 344 && before <= 348 && kind == TM_FT_PEACH) ||
          (before >= TM_AS_ATTACKAIRN && before <= TM_AS_ATTACKAIRLW)))
    {
        return;
    }

    msg = Message_Display(5, FT_U8(fp, FT_PLY), MSGCOLOR_WHITE, text, frames);
    SetColor(MessageText(msg), 1,
             frames == 1 ? TM_COLOR_GREEN : TM_COLOR_RED);
}

/* ---- Generic Per Frame.asm (Fighter_procInput+0xAE4) ------------------- */

static int CheckForJumpCancel(FighterData* fp)
{
    u8* co = (u8*) *stc_ftcommon;
    if (FT_FLOAT(fp, FT_LSTICK_Y) >= *(float*) (co + CO_JUMP_STICK_Y) &&
        FT_U8(fp, FT_TIMER_TILT_Y) < *(int*) (co + CO_JUMP_TIMER))
    {
        return 1;
    }
    if (FT_INT(fp, FT_BUTTONS_DOWN) & BUTTON_XY) {
        return 1;
    }
    return 0;
}

static void FoxFalcoShineAirStartup(FighterData* fp)
{
    int i;
    int held;
    char* hop;
    int full;
    GOBJ* msg;
    Text* text;
    int prev = fp->TM.state_prev[0];

    /* ensure we just jumped from the ground */
    if (prev != TM_AS_JUMPF && prev != TM_AS_JUMPB) {
        return;
    }
    /* frames jump was held: newest input with X/Y or stick up */
    for (i = 0; i < 32; i++) {
        u8* in = (u8*) &fp->TM.inputs[i];
        if ((*(u16*) in & BUTTON_XY) || (s8) in[3] > 44) {
            break;
        }
    }
    if (i == 32) {
        return; /* longer than the input history */
    }
    held = FT_U8(fp, FT_TIMER_JUMP) - i + 1;

    if ((float) held < FT_FLOAT(fp, FT_JUMP_STARTUP)) {
        hop = "Short Hop";
        full = 0;
    } else {
        hop = "Full Hop";
        full = 1;
    }

    /* alt ID so that Act OoShine does not overwrite it */
    msg = Message_Display(TM_OSD_FIGHTERSPECIFICTECHALT, FT_U8(fp, FT_PLY),
                          MSGCOLOR_WHITE, "JC Shine\nFrame %d\n%s: %df",
                          fp->TM.state_prev_frames[0], hop, held);
    text = MessageText(msg);
    SetColor(text, 1,
             fp->TM.state_prev_frames[0] <= 2 ? TM_COLOR_GREEN : TM_COLOR_RED);
    SetColor(text, 2, full ? TM_COLOR_RED : TM_COLOR_GREEN);
}

static void FighterSpecificTech(FighterData* fp)
{
    int ply = FT_U8(fp, FT_PLY);
    int kind = FT_INT(fp, FT_KIND);
    int state = FT_INT(fp, FT_STATE);
    int pressed_b = FT_INT(fp, FT_BUTTONS_DOWN) & BUTTON_B;

    if (kind == TM_FT_FOX || kind == TM_FT_FALCO) {
        switch (state) {
        case 0x15B: /* side B start, ground */
        case 0x15E: /* side B start, air */
            if (pressed_b) {
                void* anim = FT_PTR(fp, FT_ANIM_DATA);
                int early = (int) *(float*) ((u8*) anim + 0x8) -
                            (u16) fp->TM.state_frame - 1;
                Message_Display(TM_OSD_FIGHTERSPECIFICTECH, ply, MSGCOLOR_RED,
                                "Shorten Press\n%df Early", early);
            }
            break;
        case 0x15C: /* side B */
        case 0x15F:
            if (pressed_b) {
                Message_Display(TM_OSD_FIGHTERSPECIFICTECH, ply,
                                MSGCOLOR_GREEN, "Shorten Press\nFrame %d/4",
                                (int) FT_FLOAT(fp, FT_ANIM_FRAME) + 1);
            }
            break;
        case 0x15D: /* side B end */
        case 0x160:
            if (pressed_b) {
                Message_Display(TM_OSD_FIGHTERSPECIFICTECH, ply, MSGCOLOR_RED,
                                "Shorten Press\nLate");
            }
            break;
        case 0x16D: /* air shine startup */
            FoxFalcoShineAirStartup(fp);
            break;
        case 0x16E: /* air shine loop: needs a jump left */
            if (FT_U8(fp, FT_JUMPS_USED) >= FT_INT(fp, FT_MAX_JUMPS)) {
                break;
            }
            /* fallthrough */
        case 0x169: /* ground shine loop */
            if (CheckForJumpCancel(fp)) {
                Message_Display(TM_OSD_FIGHTERSPECIFICTECH, ply,
                                (u16) fp->TM.state_frame == 1 ? MSGCOLOR_GREEN
                                                              : MSGCOLOR_RED,
                                "Act OoShine\nFrame %d",
                                (u16) fp->TM.state_frame);
            }
            break;
        }
    } else if (kind == TM_FT_YOSHI) {
        if (state == 0x159 && CheckForJumpCancel(fp)) { /* parry start */
            Message_Display(TM_OSD_FIGHTERSPECIFICTECH, ply, MSGCOLOR_WHITE,
                            "Jump OoParry\nFrame %d",
                            (u16) fp->TM.state_frame);
        }
    }
}

static void Lockout(FighterData* fp)
{
    int state = FT_INT(fp, FT_STATE);
    int t;
    int color;

    if (FT_INT(fp, FT_AIR_STATE) == 1) {
        return;
    }
    if (state == TM_AS_ATTACKLW3 || state == TM_AS_ATTACKLW4) {
        return;
    }
    if (FT_FLOAT(fp, FT_LSTICK_Y) >= 0.0F) {
        return;
    }
    t = FT_U8(fp, FT_TIMER_SMASH_Y);
    if (t < 4) {
        color = MSGCOLOR_RED;
    } else if (t < 25) {
        color = MSGCOLOR_GREEN;
    } else {
        return;
    }
    Message_Display(TM_OSD_LOCKOUTTIMERS, FT_U8(fp, FT_PLY), color,
                    "DTilt Lockout\nFrame %d", t + 1);
}

/* Per player: frames since the last jump input and the previous frame's
 * timer_jump (DJL_Data in the assembly, which lived in its code). */
static u8 djl_frames_since[6];
static u8 djl_prev_timer[6];

static void InstaDoubleJump(FighterData* fp)
{
    /* The assembly indexes with `lwz` of the ply byte (ply << 24 for ports
     * 2-4, writing far outside its table); the byte is meant. */
    int ply = FT_U8(fp, FT_PLY);
    int timer = FT_U8(fp, FT_TIMER_JUMP);
    int frames = djl_frames_since[ply];
    int prev = djl_prev_timer[ply];

    if (FT_INT(fp, FT_KIND) != TM_FT_PEACH) {
        return;
    }
    djl_prev_timer[ply] = timer;

    /* timer_jump stays 0 while jump is held: a jump was just pressed when it
     * becomes 0 */
    if (timer == 0 && prev != 0) {
        djl_frames_since[ply] = 0;
        if (frames < 10) {
            int f = frames + 1;
            Message_Display(TM_OSD_FIGHTERSPECIFICTECH, ply,
                            f == 5 ? MSGCOLOR_GREEN : MSGCOLOR_RED,
                            "Insta Double Jump\nFrame %d", f);
        }
        return;
    }
    if (frames != 255) {
        djl_frames_since[ply] = frames + 1;
    }
}

void tmce_osd_GenericPerFrame(GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;

    if (tmce_osd_IsEnabled(TM_OSD_ACTOOWAIT)) {
        int i;
        for (i = 0; i < 6; i++) {
            int s = fp->TM.state_prev[i];
            if (s == TM_AS_WAIT || s == TM_AS_LANDING) {
                break;
            }
            /* skip intermediate walk/turn/crouch states */
            if (s != TM_AS_WALKSLOW && s != TM_AS_WALKMIDDLE &&
                s != TM_AS_WALKFAST && s != TM_AS_TURN && s != TM_AS_SQUAT)
            {
                i = 6;
                break;
            }
        }
        if (i < 6) {
            /* not if the player buffered crouch, shield, walk or turn */
            int s = FT_INT(fp, FT_STATE);
            if (s != TM_AS_WAIT && s != TM_AS_WALKSLOW &&
                s != TM_AS_WALKMIDDLE && s != TM_AS_WALKFAST &&
                s != TM_AS_SQUAT && s != TM_AS_GUARDON && s != TM_AS_TURN &&
                s != TM_AS_SQUATWAIT)
            {
                tmce_osd_ActOoWait(gobj);
            }
        }
    }

    if (tmce_osd_IsEnabled(TM_OSD_FIGHTERSPECIFICTECH)) {
        FighterSpecificTech(fp);
    }
    if (tmce_osd_IsEnabled(TM_OSD_LOCKOUTTIMERS)) {
        Lockout(fp);
    }
    if (tmce_osd_IsEnabled(TM_OSD_FIGHTERSPECIFICTECH)) {
        InstaDoubleJump(fp);
    }
}
