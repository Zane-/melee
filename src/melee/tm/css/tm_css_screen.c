#include "tm_css.h"

#include "../tmce.h"

#include <melee/gm/gm_1A3F.h>
#include <melee/gm/gmmain_lib.h>
#include <melee/gm/types.h>
#include <melee/lb/lbspdisplay.h>
#include <melee/mn/mncharsel.h>
#include <melee/mn/types.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjobject.h>
#include <sysdolphin/baselib/gobjplink.h>
#include <sysdolphin/baselib/gobjproc.h>
#include <sysdolphin/baselib/gobjuserdata.h>
#include <sysdolphin/baselib/jobj.h>
#include <sysdolphin/baselib/memory.h>
#include <sysdolphin/baselib/sislib.h>

/*
 * Character select screen hooks for TM-CE events. All four sites are in
 * mnCharSel_802640A0 (CSS setup), which Slippi also patches, so each is a
 * `call` hook on a nearby `bl` that Slippi does not touch
 * (config/GALE01/tm_hooks/css.txt).
 */

/// CSS data block of the current CSS (mn/mncharsel.c).
extern CSSData* mnCharSel_804D6CB0;
/// The CSS menu model; character icons are its children (mn/mncharsel.c).
extern HSD_JObj* mnCharSel_804D6CC0;
/// The 25 character icons (static `icons` in mn/mncharsel.c).
extern CSSIcon icons[];

/// Mirrors the start of `struct CSSCursorData`, local to mn/mncharsel.c.
typedef struct TmCssCursor {
    /* 0x00 */ HSD_GObj* gobj;
    /* 0x04 */ u8 x4;
    /* 0x05 */ u8 state; ///< 1 = holding a puck
    /* 0x06 */ u8 puck;  ///< puck held: 0 = P1's, 1 = the CPU's
} TmCssCursor;

/// Per-port cursors (mn/mncharsel.c).
extern TmCssCursor* mnCharSel_804A0BC0[4];

static inline bool tm_css_IsEventMode(void)
{
    return tmce_IsLoaded() && gm_GetCurrentGameMode() == GM_EVENT;
}

static inline int tm_css_Event(void)
{
    return gmMainLib_804D3EE0->vs.unk_530.unk_535;
}

/**
 * Display Event Name on CSS.asm (mnCharSel_802640A0+0x464): wraps the
 * `HSD_JObjAnimAll` call just before it and adds the event's name above
 * the character panel.
 */
void tm_css_JObjAnimAll(HSD_JObj* jobj)
{
    HSD_Text* text;
    int sub;

    HSD_JObjAnimAll(jobj);
    if (!tm_css_IsEventMode()) {
        return;
    }
    text = HSD_SisLib_803A6754(0, 0);
    text->default_kerning = 1;
    text->default_alignment = 1;
    text->font_size.x = 0.1F;
    text->font_size.y = 0.1F;
    sub = HSD_SisLib_803A6B98(text, 38.0F, -245.0F, "%s",
                              GetEventName(tmce_GetEventPage(),
                                           tm_css_Event()));
    HSD_SisLib_803A7548(text, sub, 0.65F, 0.65F);
}

/* Show only the whitelisted icons (CSSID bit i = icons[i]). */
static void tm_css_ShowIcons(int whitelist)
{
    int i;
    for (i = 24; i >= 0; i--) {
        CSSIcon* icon = &icons[i];
        bool visible = (whitelist & (1 << i)) != 0;
        HSD_JObj* jobj;

        lb_80011E24(mnCharSel_804D6CC0, &jobj, icon->joint_id_1p, -1);
        if (visible) {
            jobj->flags &= ~JOBJ_HIDDEN;
        } else {
            jobj->flags |= JOBJ_HIDDEN;
        }
        icon->state = visible ? 2 : 0;
    }
}

/* GObj proc: show the HMN or the CPU whitelist, by the puck P1 holds. */
static void tm_css_IconThink(HSD_GObj* gobj)
{
    int* allowed = *(int**) gobj->user_data; /* AllowedCharacters* */
    TmCssCursor* cursor = mnCharSel_804A0BC0[0];

    if (cursor->state != 1 || cursor->puck == 0) {
        tm_css_ShowIcons(allowed[0]);
    } else if (cursor->puck == 1) {
        tm_css_ShowIcons(allowed[1]);
    }
}

/**
 * Toggle CSS Icon Vibibility.asm (mnCharSel_802640A0+0x4D8): wraps the
 * `HSD_GObjObject_80390A70` call after it. In event mode, adds a GObj that
 * hides the characters the event does not allow, and if the human side has
 * a whitelist, clears P1's pick.
 */
void tm_css_GObjObject(HSD_GObj* gobj, u8 kind, void* obj)
{
    HSD_GObj* icon_gobj;
    void** data;
    int* allowed;

    HSD_GObjObject_80390A70(gobj, kind, obj);
    if (!tm_css_IsEventMode()) {
        return;
    }
    icon_gobj = GObj_Create(4, 5, 0);
    data = HSD_MemAlloc(8);
    GObj_InitUserData(icon_gobj, 14, HSD_Free, data);
    /* Priority 2: after the CSS input handler. */
    HSD_GObj_SetupProc(icon_gobj, tm_css_IconThink, 2);

    allowed = GetEventCharList(tm_css_Event(), tmce_GetEventPage());
    data[0] = allowed;
    if (allowed[0] != -1) {
        CSSData* css = mnCharSel_804D6CB0;
        /* CSSData +0x70: players' character kinds, 0x24 apart. */
        u8* player = (u8*) css + 0x70 + (css->unk_0x0 - 1) * 0x24;
        player[0] = ChKind_None;
    }
}

/**
 * Overwrite VS Text.asm (mnCharSel_802640A0+0x2274): replaces the
 * `mnCharSel_8025BD30` call (the rules text) and blanks that text in event
 * mode.
 */
void tm_css_UpdateRulesText(void)
{
    if (!tm_css_IsEventMode()) {
        mnCharSel_8025BD30();
        return;
    }
    HSD_SisLib_803A6530(0, 0x4A, 0);
    HSD_SisLib_803A660C(0, 0x4A, 0);
}

/**
 * Hooks/OnCSSLoad.asm (mnCharSel_802640A0+0x2770): wraps the
 * `mnCharSel_8025EE8C` call right after it. In event mode, loads the
 * event's CSS file and runs its cssFunction (labCSS's OnCSSLoad: recording
 * import) with the archive.
 */
void tm_css_8025EE8C(u8 idx)
{
    if (tm_css_IsEventMode()) {
        char* file = GetCSSFile(tmce_GetEventPage(), tm_css_Event());
        if (file != NULL) {
            void (*on_load)(void*) = NULL;
            void* archive = MEX_LoadRelArchive(file, &on_load, "cssFunction");
            if (on_load != NULL) {
                on_load(archive);
            }
        }
    }
    mnCharSel_8025EE8C(idx);
}
