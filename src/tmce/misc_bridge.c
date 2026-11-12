/*
 * MexTK-side parts of the `misc` area (src/melee/tm/misc/misc.h): things
 * that need TM-CE's types or MexTK's text and match API.
 */
#include "events.h"
#include <stddef.h>

/* events.c */
char* GetTMVersLong(void);
char* GetTMCompile(void);

/* ---- Character Randomness ------------------------------------------- */

int tmce_misc_GetRng(int which)
{
    if (event_vars == NULL || event_vars->rng == NULL) {
        return 0;
    }
    return ((u8*) event_vars->rng)[which];
}

/* ---- Display Stick Info When Paused ----------------------------------- */

/*
 * Port of Misc/Display Stick Info When Paused/Create Text on Pause.asm and
 * Remove Text on UnPause.asm. On the vanilla pause screen in Event Mode,
 * shows the pausing player's raw and normalised stick X and Y, green when
 * positive and red when negative.
 *
 * TM-CE keeps the text and updater GObj at 0x804A1F58+0x8/+0xC, which is
 * vanilla if_2FF2 data (un_804A1F58.x8[0]); here they are statics.
 */
static Text* pause_stick_text;
static GOBJ* pause_stick_gobj;

static char* const stick_x_fmt = "X: %4.4f \x81\x5e %d";
static char* const stick_y_fmt = "Y: %4.4f \x81\x5e %d";

static HSD_Pad* pausingPad(void)
{
    return &stc_engine_pads->pad[stc_match->pauser];
}

static void pauseStickUpdate(GOBJ* gobj)
{
    static const GXColor pos = {0x8D, 0xFF, 0x6E, 0xFF};
    static const GXColor neg = {0xFF, 0xA2, 0xBA, 0xFF};
    HSD_Pad* pad = pausingPad();
    Text* text = pause_stick_text;
    s8 x = pad->stickX;
    s8 y = pad->stickY;
    float fx = pad->fstickX;
    float fy = pad->fstickY;

    if (text == NULL) {
        return;
    }
    Text_SetColor(text, 1, (GXColor*) (x < 0 ? &neg : &pos));
    Text_SetText(text, 1, stick_x_fmt, fx < 0 ? -fx : fx, x < 0 ? -x : x);
    Text_SetColor(text, 2, (GXColor*) (y < 0 ? &neg : &pos));
    Text_SetText(text, 2, stick_y_fmt, fy < 0 ? -fy : fy, y < 0 ? -y : y);
}

void tmce_misc_PauseStickCreate(void)
{
    HSD_Pad* pad;
    Text* text;
    int sub;

    if (Scene_GetCurrentMajor() != MJRKIND_EVENT) {
        return;
    }

    text = Text_CreateText(2, *stc_match_canvas);
    pause_stick_text = text;
    pad = pausingPad();

    /* Background box: one full-width dash glyph stretched over the lines. */
    text->kerning = 0;
    text->align = 0;
    text->color = (GXColor){0, 0, 0, 0};
    sub = Text_AddSubtext(text, -29.0F, -8.0F, "\x81\x5b");
    Text_SetScale(text, sub, 0.50F, 1.08F);

    text->kerning = 1;
    /* TM-CE reads the raw byte unsigned here (lbz); the updater shows the
     * magnitude from the next frame on. */
    sub = Text_AddSubtext(text, -27.0F, -23.0F, stick_x_fmt, pad->fstickX,
                          (u8) pad->stickX);
    Text_SetScale(text, sub, 0.05F, 0.05F);
    sub = Text_AddSubtext(text, -27.0F, -21.0F, stick_y_fmt, pad->fstickY,
                          (u8) pad->stickY);
    Text_SetScale(text, sub, 0.05F, 0.05F);

    pause_stick_gobj = GObj_Create(6, 0, 128);
    GObj_AddProc(pause_stick_gobj, pauseStickUpdate, 10);
}

void tmce_misc_PauseStickRemove(void)
{
    if (Scene_GetCurrentMajor() != MJRKIND_EVENT) {
        return;
    }
    if (pause_stick_text != NULL) {
        Text_Destroy(pause_stick_text);
    }
    if (pause_stick_gobj != NULL) {
        GObj_Destroy(pause_stick_gobj);
    }
    pause_stick_text = NULL;
    pause_stick_gobj = NULL;
}

/* ---- Display Tweet Message And Version Number ------------------------- */

/*
 * Port of Misc/Display Tweet Message And Version Number.asm: before the
 * crash handler prints its stack trace, play a gasp and print TM-CE's
 * report-this banner and version.
 */
void tmce_misc_CrashMessage(void)
{
    SFX_Play(317);
    OSReport("\n");
    OSReport("#####################################################\n");
    OSReport("## TWEET A PICTURE OF THIS MESSAGE TO @rwing_aitch ##\n"
             "## After submitting, PRESS LRA-START to reboot ##\n");
    OSReport("#####################################################\n");
    OSReport("\n");
    OSReport("%s\n", GetTMVersLong());
    OSReport(GetTMCompile());
    OSReport("\n");
}
