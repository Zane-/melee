#include "tm.h"

#include <string.h>
#include <dolphin/gx.h>
#include <melee/gm/forward.h>
#include <melee/gm/gm_1A3F.h>
#include <melee/gm/gmmain_lib.h>
#include <melee/lb/lb_013B.h>
#include <melee/lb/lb_0219.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjplink.h>
#include <sysdolphin/baselib/gobjproc.h>
#include <sysdolphin/baselib/memory.h>
#include <sysdolphin/baselib/sislib.h>

static void tm_CreateWatermark(void);
static void tm_Match_Think(HSD_GObj* gobj);

/// Wraps the `gmMainLib_8015FBA4()` call in `main`, after the SDK, HSD and
/// lb layers are initialised and before the game-mode loop starts.
void tm_Hook_Boot(void)
{
    gmMainLib_8015FBA4();

    /* The reserved block is not part of the DOL and not zeroed by the OS. */
    memset(&tm_persist, 0, TM_PERSIST_RESERVED);
    tm_persist.magic = TM_PERSIST_MAGIC;
    tm_state = NULL;
}

/// Wraps the last call in `gm_801A4BD4`, which runs at the start of every
/// scene after the GObj system and the scene heap have been reset.
void tm_Hook_SceneChange(void)
{
    lb_80014534();

    if (tm_persist.magic != TM_PERSIST_MAGIC) {
        return;
    }
    /* Everything allocated in the previous scene is gone. */
    tm_state = NULL;
    tm_persist.watermark = NULL;
    tm_persist.scene_count++;
    /* Back in the menus: the chosen event no longer owns Training mode.
     * The event select screen sets the flag again on confirm. */
    if (gm_GetCurrentGameMode() == GM_MENU) {
        tm_persist.event_active = false;
    }
    tm_CreateWatermark();
}

/// Wraps the `lbBgFlash_Init` call in `fn_8016E730` (match start), the point
/// where TM-CE runs its OnStartMelee hook.
void tm_Hook_StartMelee(int arg)
{
    TmMatch* match;

    lbBgFlash_Init(arg);

    if (tm_persist.magic != TM_PERSIST_MAGIC) {
        return;
    }
    match = HSD_MemAlloc(sizeof(TmMatch));
    memset(match, 0, sizeof(TmMatch));
    match->think_gobj = GObj_Create(0, 7, 0);
    HSD_GObj_SetupProc(match->think_gobj, tm_Match_Think, 0);
    tm_state = match;
    tm_persist.match_count++;
}

static void tm_Match_Think(HSD_GObj* gobj)
{
    if (tm_state != NULL) {
        tm_state->frame++;
    }
}

/// Port of TM-CE `TM_CreateWatermark` (src/events.c): the version string in
/// the bottom-right corner of every scene, with a four-way drop shadow.
static void tm_CreateWatermark(void)
{
    static const float shadow[4][2] = {
        { 2.0F, 2.0F },
        { 2.0F, -2.0F },
        { -2.0F, 2.0F },
        { -2.0F, -2.0F },
    };
    GXColor shadow_color;
    HSD_Text* text;
    int canvas;
    int i;

    canvas = HSD_SisLib_803A611C(10, NULL, 9, 13, 0, 14, 0, 10);
    text = HSD_SisLib_803A6754(10, canvas);
    text->default_alignment = 2;
    text->default_kerning = 1;
    text->font_size.x = 0.4F;
    text->font_size.y = 0.4F;
    text->pos_x = 615.0F;
    text->pos_y = 446.0F;

    shadow_color.r = 0;
    shadow_color.g = 0;
    shadow_color.b = 0;
    shadow_color.a = 0;
    for (i = 0; i < 4; i++) {
        int idx = HSD_SisLib_803A6B98(text, shadow[i][0], shadow[i][1],
                                      TM_VERSION_SHORT);
        HSD_SisLib_803A74F0(text, idx, &shadow_color);
    }
    HSD_SisLib_803A6B98(text, 0.0F, 0.0F, TM_VERSION_SHORT);

    tm_persist.watermark = text;
}
