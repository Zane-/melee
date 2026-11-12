/*
 * TM-CE "act out of" on-screen displays, MexTK side (osdact area). Ports of
 * ../TrainingMode/ASM/training-mode/Onscreen Display/:
 *
 *   Act OoAirborne/Display Act OoAirborne Frame Count - Static Function.asm
 *       (0x8000550C)                       -> tmce_osdact_OoAirborne
 *   Act OOS Frame Display/Display OOS Frame Count Standalone.asm
 *       (0x80005508)                       -> tmce_osdact_OoShield
 *   Act OOS Frame Display/Count During ShieldWait.asm, Count During
 *       GuardOff.asm, Init Frame Count.asm -> tmce_osdact_ShieldFrames*
 *   Act OOTumble/Static Function - Display Frames Spent Post Hitstun.asm
 *       (0x80005504)                       -> tmce_osdact_OoHitstun
 *   Act OOTumble/Increment Post Hitstun Count.asm
 *                                          -> tmce_osdact_PostHitstunCount
 *   Act Oo Float.asm                       -> tmce_osdact_OoFloat
 *
 * Called from the native hooks in src/melee/tm/osdact/ (decomp side), which
 * pass the fighter GObj as void*. Fighter fields outside FighterData.TM are
 * read at the raw offsets the assembly uses, so the logic matches it one to
 * one.
 */
#include "events.h"
#include <stddef.h>

/* src/melee/tm/osdcore/osd_core.c */
int tm_osd_IsFollower(void* fp);
/* src/tmce/osdcore_vars.c: the "CHECK IF ENABLED" bit test. */
int tmce_osd_IsEnabled(int osd);

#define FT_U8(fp, off) (*(u8*) ((u8*) (fp) + (off)))
#define FT_U16(fp, off) (*(u16*) ((u8*) (fp) + (off)))
#define FT_INT(fp, off) (*(int*) ((u8*) (fp) + (off)))
#define FT_FLOAT(fp, off) (*(float*) ((u8*) (fp) + (off)))

#define FT_PLY 0xC          /* u8 player slot (message queue) */
#define FT_STATE 0x10       /* current action state */
#define FT_JUMP_V0 0x150    /* float, jump_v_initial_velocity */
#define FT_AIRJUMP_MUL 0x160 /* float, air_jump_v_multiplier */
#define FT_MAX_JUMPS 0x168  /* int */
#define FT_GRAVITY 0x16C    /* float */
#define FT_HITSTUN 0x221C   /* u8; bit 0x02 = in hitstun */

/* m-ex/Header.s TM_PostHitstunFrameCount: a word in FighterData.TM
 * (post_hitstun_frames, 0x241C) that the assembly reads and writes as a
 * halfword, i.e. its upper 16 bits. Kept that way. */
#define TM_POST_HITSTUN(fp) FT_U16(fp, 0x241C)

/* Globals.s OSD.* */
#define OSD_ACTOOS 3
#define OSD_FIGHTERSPECIFICTECH 8
#define OSD_ACTOOAIRBORNE 18
#define OSD_ACTOOHITSTUN 28

/* Globals.s ASID_* */
#define AS_JUMPF 0x19
#define AS_JUMPB 0x1A
#define AS_JUMPAERIALF 0x1B
#define AS_JUMPAERIALB 0x1C
#define AS_FALL 0x1D
#define AS_ATTACKAIRN 0x41
#define AS_ATTACKAIRF 0x42
#define AS_ATTACKAIRB 0x43
#define AS_ATTACKAIRHI 0x44
#define AS_ATTACKAIRLW 0x45
#define AS_GUARDOFF 0xB4
#define AS_GUARDSETOFF 0xB5
#define AS_PASS 0xF4
#define AS_BARRELCANNONWAIT 0x154
#define AS_MULTIJUMP_FIRST 0x155 /* Kirby / Jigglypuff aerial jumps */
#define AS_MULTIJUMP_LAST 0x159

/* ---- Act OoAirborne static function (0x8000550C) ------------------------
 * After an aerial / special / double jump interrupt out of a jump, double
 * jump, fall or platform drop: how many frames the previous state lasted.
 * @p kind is the message kind (OSD.ActOoAirborne, or OSD.Miscellaneous for
 * DblJump OoJump); the enable bit is always OSD.ActOoAirborne. */
void tmce_osdact_OoAirborne(int interrupted, GOBJ* gobj, char* text, int kind)
{
    FighterData* fp;
    int prev;
    int frames;
    int color;

    if (!interrupted) {
        return;
    }
    fp = gobj->userdata;
    if (!tmce_osd_IsEnabled(OSD_ACTOOAIRBORNE)) {
        return;
    }
    if (tm_osd_IsFollower(fp)) {
        return;
    }

    prev = fp->TM.state_prev[0];
    frames = fp->TM.state_prev_frames[0];
    if (prev == AS_PASS) {
        /* no cutoff */
    } else if (prev == AS_FALL) {
        int before = fp->TM.state_prev[1];
        if (frames > 10) {
            return;
        }
        /* states before the fall that need no OSD */
        if (before == AS_JUMPF || before == AS_JUMPB ||
            before == AS_ATTACKAIRN || before == AS_ATTACKAIRF ||
            before == AS_ATTACKAIRB || before == AS_ATTACKAIRHI ||
            before == AS_ATTACKAIRLW)
        {
            return;
        }
        /* mainly special moves */
        if (before > AS_BARRELCANNONWAIT) {
            return;
        }
    } else {
        float v;
        if (prev == AS_JUMPF || prev == AS_JUMPB) {
            v = FT_FLOAT(fp, FT_JUMP_V0);
        } else if (prev == AS_JUMPAERIALF || prev == AS_JUMPAERIALB ||
                   (FT_INT(fp, FT_MAX_JUMPS) > 2 &&
                    prev >= AS_MULTIJUMP_FIRST && prev <= AS_MULTIJUMP_LAST))
        {
            v = FT_FLOAT(fp, FT_JUMP_V0) * FT_FLOAT(fp, FT_AIRJUMP_MUL);
        } else {
            return;
        }
        /* past the jump's peak (+5 frames): no OSD */
        if (frames > (int) (v / FT_FLOAT(fp, FT_GRAVITY)) + 5) {
            return;
        }
    }

    color = frames == 1 ? MSGCOLOR_GREEN : MSGCOLOR_RED;
    Message_Display(kind, FT_U8(fp, FT_PLY), color, text, frames);
}

/* ---- Act OOS: shield frame counter ---------------------------------------
 * TM.shield_frame counts frames since shield stun ended: reset when the
 * shield stun (GuardSetOff) animation ends, incremented every frame of
 * shield (Guard) and shield release (GuardOff), capped at 0xFF. */
void tmce_osdact_ShieldFramesInc(GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    if ((u16) fp->TM.shield_frame != 0xFF) {
        fp->TM.shield_frame++;
    }
}

void tmce_osdact_ShieldFramesReset(GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    fp->TM.shield_frame = 0;
}

/* ---- Act OOS static function (0x80005508) --------------------------------
 * After an interrupt out of shield or shield release, if shield stun was two
 * or three states ago: frames since shield stun ended. */
void tmce_osdact_OoShield(int interrupted, GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    int color;

    if (!tmce_osd_IsEnabled(OSD_ACTOOS)) {
        return;
    }
    if (interrupted != 1) {
        return;
    }
    if (tm_osd_IsFollower(fp)) {
        return;
    }
    if (FT_INT(fp, FT_STATE) == AS_GUARDOFF) {
        return;
    }
    if (fp->TM.state_prev[1] != AS_GUARDSETOFF &&
        fp->TM.state_prev[2] != AS_GUARDSETOFF)
    {
        return;
    }
    color = (u16) fp->TM.shield_frame > 0 ? MSGCOLOR_WHITE : MSGCOLOR_GREEN;
    Message_Display(OSD_ACTOOS, FT_U8(fp, FT_PLY), color,
                    "Act OoShield\nFrame %d",
                    (u16) fp->TM.shield_frame + 1);
}

/* ---- Act OOTumble/Increment Post Hitstun Count.asm (Fighter_procAnim
 * +0x800): 0 while in hitstun, then +1 every frame. */
void tmce_osdact_PostHitstunCount(GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    if (FT_U8(fp, FT_HITSTUN) & 0x02) {
        TM_POST_HITSTUN(fp) = 0;
    } else {
        TM_POST_HITSTUN(fp)++;
    }
}

/* ---- Act OOTumble static function (0x80005504) ---------------------------
 * After an interrupt out of tumble / light hit / damage fall: frames since
 * hitstun ended. */
void tmce_osdact_OoHitstun(int interrupted, GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    int color;

    if (interrupted != 1) {
        return;
    }
    if (!tmce_osd_IsEnabled(OSD_ACTOOHITSTUN)) {
        return;
    }
    if (tm_osd_IsFollower(fp)) {
        return;
    }
    color = TM_POST_HITSTUN(fp) > 0 ? MSGCOLOR_WHITE : MSGCOLOR_GREEN;
    Message_Display(5, FT_U8(fp, FT_PLY), color, "Act OoHitstun\nFrame %d",
                    TM_POST_HITSTUN(fp) + 1);
}

/* True if @p gobj is in Fall (Act OOTumble/DamageFall - Check For
 * Interrupt.asm treats entering Fall as an interrupt). */
int tmce_osdact_IsInFall(GOBJ* gobj)
{
    FighterData* fp = gobj->userdata;
    return FT_INT(fp, FT_STATE) == AS_FALL;
}

/* ---- Act Oo Float.asm (ftPe_8011BE80+0x3C): Peach presses A / C-stick out
 * of float; frames spent in float, up to 15. */
void tmce_osdact_OoFloat(FighterData* fp)
{
    int frames;
    int color;

    if (!tmce_osd_IsEnabled(OSD_FIGHTERSPECIFICTECH)) {
        return;
    }
    if (tm_osd_IsFollower(fp)) {
        return;
    }
    frames = (u16) fp->TM.state_frame;
    if (frames > 15) {
        return;
    }
    color = frames == 1 ? MSGCOLOR_GREEN : MSGCOLOR_RED;
    Message_Display(OSD_FIGHTERSPECIFICTECH, FT_U8(fp, FT_PLY), color,
                    "Act OoFloat\nFrame %d", frames);
}
