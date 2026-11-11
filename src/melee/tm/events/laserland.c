/**
 * @file
 * Laser Land training. Port of TM-CE `src/laserland.c`.
 *
 * Fox / Falco: start an aerial laser as the peak of a double jump lines up
 * with a platform, to land with no lag. The event watches the player's
 * action states and reports timing and success rate.
 *
 * Differences from TM-CE: the result strings live in the event data block
 * instead of writable statics, and the readout is a plain text panel until
 * TM-CE's HUD drawing helpers (`HUD_DrawInfoPanel`) are ported.
 */

#include "tm.h"
#include "tm_event.h"

#include <stdio.h>
#include <dolphin/gx.h>
#include <melee/ft/inlines.h>
#include <melee/ft/kinds/ftCommon/forward.h>
#include <melee/ft/types.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/axdriver.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/sislib.h>

#define LL_SUCCESS_FRAMES_THRESHOLD 9

/* Fox / Falco aerial laser motion states. */
#define LL_MS_LASER_AIR_START 344
#define LL_MS_LASER_AIR_LOOP 345
#define LL_MS_LASER_AIR_END 346

#define LL_SFX_FAIL 3
#define LL_SFX_SUCCESS 303

typedef struct LLData {
    int success_count;
    int total_count;
    int frames_in_laserstart;
    int laserstart_counter;
    bool in_laserstart;
    bool in_f0_laserstart;
    HSD_Text* panel;
    char attempt_text[24];
    char frames_text[24];
    char success_rate_text[24];
} LLData;

static const TmOptionDesc options_main[] = {
    {
        TM_OPTKIND_INFO,
        0,
        0,
        0,
        0,
        "Help",
        { "To laser land, start a laser as the peak of your",
          "double jump aligns with the height of a platform.",
          "Done successfully, you will appear to warp onto the",
          "platform with no landing lag." },
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
    },
    {
        TM_OPTKIND_FUNC,
        0,
        0,
        0,
        0,
        "Exit",
        { "Return to the Event Selection Screen." },
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        tmEvent_Exit,
    },
};

static const TmMenuDesc menu_main = {
    "Laser Land Training",
    sizeof(options_main) / sizeof(options_main[0]),
    options_main,
    NULL,
};

static void updatePanel(LLData* data)
{
    HSD_SisLib_803A70A0(data->panel, 0, "Last Attempt: %s",
                        data->attempt_text);
    HSD_SisLib_803A70A0(data->panel, 1, "Timing: %s", data->frames_text);
    HSD_SisLib_803A70A0(data->panel, 2, "Success Rate: %s",
                        data->success_rate_text);
}

static bool inLaserstart(int motion_id)
{
    return motion_id == LL_MS_LASER_AIR_START ||
           motion_id == LL_MS_LASER_AIR_LOOP;
}

static void failWith(LLData* data, const char* msg)
{
    sprintf(data->attempt_text, "Failed");
    sprintf(data->frames_text, "%s", msg);
    lbAudioAx_80024030(LL_SFX_FAIL);
}

static void laserland_Init(HSD_GObj* gobj)
{
    LLData* data = gobj->user_data;
    HSD_Text* text;
    int canvas;
    int i;

    /* The data block starts zeroed; only the strings need a value. */
    sprintf(data->attempt_text, "-");
    sprintf(data->frames_text, "-");
    sprintf(data->success_rate_text, "-");

    canvas = HSD_SisLib_803A611C(10, NULL, 9, 13, 0, 14, 0, 10);
    text = HSD_SisLib_803A6754(10, canvas);
    text->default_kerning = 1;
    text->font_size.x = 0.5F;
    text->font_size.y = 0.5F;
    text->pos_x = 30.0F;
    text->pos_y = 60.0F;
    for (i = 0; i < 3; i++) {
        HSD_SisLib_803A6B98(text, 0.0F, i * 40.0F, "");
    }
    data->panel = text;
    updatePanel(data);
}

static void laserland_Think(HSD_GObj* gobj)
{
    LLData* data = gobj->user_data;
    HSD_GObj* hmn = Player_GetEntity(0);
    Fighter* fp;
    int motion_id;

    if (hmn == NULL) {
        return;
    }
    fp = GET_FIGHTER(hmn);
    motion_id = fp->motion_id;

    /* Leaving laser start straight into Wait is a success; anything else
     * is a failure. */
    if ((!inLaserstart(motion_id) && data->in_laserstart) ||
        (data->in_f0_laserstart && motion_id == ftCo_MS_Wait))
    {
        float success_rate;

        data->total_count++;
        data->frames_in_laserstart = data->laserstart_counter;

        /* Laser lands slower than about 6f are worse than wavelands, but a
         * slightly slow landing is not really a failure. */
        if (motion_id == ftCo_MS_Wait &&
            data->frames_in_laserstart <= LL_SUCCESS_FRAMES_THRESHOLD)
        {
            data->success_count++;
            sprintf(data->attempt_text, "Success");
            if (data->in_f0_laserstart) {
                sprintf(data->frames_text, "Perfect");
            } else {
                sprintf(data->frames_text, "%df", data->frames_in_laserstart);
            }
            HSD_AudioSFXStartParam(LL_SFX_SUCCESS, 255, 128, 20, 3);
        } else if (data->frames_in_laserstart > LL_SUCCESS_FRAMES_THRESHOLD) {
            failWith(data, "Early");
        } else {
            switch (motion_id) {
            case LL_MS_LASER_AIR_END:
                failWith(data, "Early");
                break;
            case ftCo_MS_Landing:
                failWith(data, "Bad height");
                break;
            default:
                failWith(data, "N/A");
                break;
            }
        }

        success_rate = (float) data->success_count * 100.0F /
                       (float) data->total_count;
        sprintf(data->success_rate_text, "%d (%.2f%%)", data->success_count,
                success_rate);

        data->in_laserstart = false;
        data->laserstart_counter = 0;
        updatePanel(data);
    }

    data->in_f0_laserstart = false;

    if (inLaserstart(motion_id)) {
        data->in_laserstart = true;
        data->laserstart_counter++;
    } else if (fp->input.pressed_buttons & HSD_PAD_B) {
        /* A laser land on "frame 0" skips the laser start state and goes
         * straight to Wait. */
        if (motion_id == ftCo_MS_Landing) {
            failWith(data, "Late");
            updatePanel(data);
        }
        data->in_f0_laserstart = true;
    }
}

static const TmEventMatchData match_data = {
    TM_TIMER_HIDE,     /* timer */
    TM_MATCHTYPE_TIME, /* match_type */
    true,              /* hide_go */
    true,              /* hide_ready */
    false,             /* create_hud */
    false,             /* timer_run_on_pause */
    true,              /* check_for_z_retry */
    false,             /* show_score */
    false,             /* run_stock_logic */
    false,             /* disable_hit */
    0,                 /* timer_seconds */
};

const TmEventDesc tm_event_laserland = {
    "Laser Land Training",
    "Use a laser to board platforms instantly!",
    true, /* disable_hazards */
    15,   /* callback_priority */
    laserland_Init,
    NULL,
    laserland_Think,
    &menu_main,
    &match_data,
};
