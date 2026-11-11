/**
 * @file
 * Event select screen for training events.
 *
 * Replaces the vanilla Event Match select screen (melee/mn/mnevent.c) with a
 * version that lists #tm_event_pages. It is an edited copy of that file's C,
 * entered through one `function` hook on `mnEvent_8024E838`; every other
 * function of the vanilla screen is only reachable from that entry, so no
 * other hook is needed. This covers what TM-CE does with about 25 assembly
 * injections under `ASM/training-mode/Custom Events/Event Select Screen`.
 *
 * Behaviour kept from TM-CE:
 * - rows show event names; the description box shows the event description;
 * - L / R (digital or analog) change page, with the page name on screen;
 * - the list never scrolls past the events of the page;
 * - X / Y jump a screenful;
 * - any character may be used: the character panel shows "select character".
 *
 * Not ported yet: high scores, the OSD settings screen on Left / Right, the
 * tutorial text toggle and the version / QR code panel.
 *
 * Confirming stores the selection in #tm_persist and enters vanilla Training
 * mode, whose match start is routed to the event (tm_event.c).
 */

#include "tm.h"
#include "tm_event.h"

#include <string.h>
#include <melee/gm/forward.h>
#include <melee/gm/gm_1601.h>
#include <melee/lb/lbarchive.h>
#include <melee/lb/lbspdisplay.h>
#include <melee/mn/inlines.h>
#include <melee/mn/mnevent.h>
#include <melee/mn/mnmain.h>
#include <melee/mn/types.h>
#include <melee/sc/types.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjgxlink.h>
#include <sysdolphin/baselib/gobjobject.h>
#include <sysdolphin/baselib/gobjplink.h>
#include <sysdolphin/baselib/gobjproc.h>
#include <sysdolphin/baselib/gobjuserdata.h>
#include <sysdolphin/baselib/jobj.h>
#include <sysdolphin/baselib/memory.h>
#include <sysdolphin/baselib/sislib.h>

#define ESS_ROWS 9
#define ESS_MENU_ID 7 ///< value of MenuFlow::cur_menu for this screen
#define ESS_DESC_LINES 4
#define ESS_DESC_LINE_LEN 64
#define ESS_TRIGGER_THRESHOLD 43

/* Layout values to tune by eye once the screen has been seen running. */
#define ESS_DESC_TEXT_SCALE 0.7F
#define ESS_DESC_LINE_HEIGHT 30.0F
#define ESS_PAGE_TEXT_X -9.5F
#define ESS_PAGE_TEXT_Y -7.8F
#define ESS_PAGE_TEXT_SCALE 0.045F

/// The vanilla screen's user data, extended. The vanilla part comes first so
/// the copied code reads the same.
typedef struct TmEssData {
    MnEventData v;
    HSD_Text* page_text;
    u8 analog_l_prev; ///< an analog L was past the threshold last frame
    u8 analog_r_prev;
} TmEssData;

/* State and data of the vanilla screen (static in melee/mn/mnevent.c), reused
 * so this file needs no writable statics of its own. */
extern HSD_GObj* mnEvent_804D6C60;         ///< the screen's GObj
extern u8 mnEvent_804D6C64;                ///< frames to wait before input
extern AnimLoopSettings mnEvent_803EF740;  ///< intro animation
extern AnimLoopSettings mnEvent_803EF74C;  ///< outro animation
extern AnimLoopSettings mnEvent_803EF758;  ///< idle animation
extern StaticModelDesc MenMainConEv;

static const Vec3 row_text_offset = { -3.8F, -0.6F, 0.0F };
static const GXColor row_text_color = { 0xCA, 0xBC, 0x9F, 0xFF };
static const GXColor desc_text_color = { 0xAA, 0xAA, 0xAA, 0xFF };

static void ess_Input(HSD_GObj* gobj);
static void ess_Create(void);
static void ess_ProcIntro(HSD_GObj* gobj);
static void ess_ProcIdle(HSD_GObj* gobj);
static void ess_ProcOutro(HSD_GObj* gobj);

static const TmEventPage* currentPage(void)
{
    if (tm_persist.event_page >= tm_event_page_num) {
        tm_persist.event_page = 0;
    }
    return &tm_event_pages[tm_persist.event_page];
}

/// Largest scroll offset: the list never scrolls past the page's events.
static s32 maxFirstEvent(void)
{
    s32 num = currentPage()->event_num;
    return num > ESS_ROWS ? num - ESS_ROWS : 0;
}

/// Lowest cursor row that still holds an event.
static s32 maxCursorRow(void)
{
    s32 num = currentPage()->event_num;
    if (num <= 0) {
        return 0;
    }
    return num > ESS_ROWS ? ESS_ROWS - 1 : num - 1;
}

static inline TmEssData* getData(void)
{
    return mnEvent_804D6C60->user_data;
}

/// Scroll arrows. From mnEvent_8024D014.
static void updateArrows(TmEssData* data)
{
    HSD_JObj* tree = mnEvent_804D6C60->hsd_obj;
    HSD_JObj* jobj;

    lb_80011E24(tree, &jobj, 3, -1);
    if (data->v.first_event == 0) {
        HSD_JObjSetFlagsAll(jobj, JOBJ_HIDDEN);
    } else {
        HSD_JObjClearFlagsAll(jobj, JOBJ_HIDDEN);
    }

    lb_80011E24(tree, &jobj, 2, -1);
    if (data->v.first_event == maxFirstEvent()) {
        HSD_JObjSetFlagsAll(jobj, JOBJ_HIDDEN);
    } else {
        HSD_JObjClearFlagsAll(jobj, JOBJ_HIDDEN);
    }
}

/// Character panel: always the "select character" picture (frame 25), as
/// with TM-CE's "Choose Any Character for Events". From mnEvent_8024D0CC.
static void updateCharacterPanel(void)
{
    HSD_JObj* jobj;

    lb_80011E24(mnEvent_804D6C60->hsd_obj, &jobj, 4, -1);
    HSD_JObjReqAnimAll(jobj, 25.0F);
    HSD_JObjAnimAll(jobj);
}

/// One list row: the event name, or nothing past the end of the page.
/// From mnEvent_8024D15C, without the "cleared" icon and the title text.
static void drawRow(s32 idx, s32 event_idx)
{
    TmEssData* data = getData();
    const TmEventPage* page = currentPage();
    HSD_JObj* tree = mnEvent_804D6C60->hsd_obj;
    HSD_JObj* jobj_0A;
    HSD_JObj* jobj_0C;
    HSD_Text* text;
    Vec3 pos;
    f32 spacing;

    if (data->v.texts[idx] != NULL) {
        HSD_SisLib_803A5CC4(data->v.texts[idx]);
        data->v.texts[idx] = NULL;
    }
    if (event_idx >= page->event_num) {
        return;
    }

    lb_80011E24(tree, &jobj_0A, 0xA, -1);
    lb_80011E24(tree, &jobj_0C, 0xC, -1);
    spacing = HSD_JObjGetTranslationY(jobj_0C) -
              HSD_JObjGetTranslationY(jobj_0A);
    HSD_JObjGetTranslation(jobj_0A, &pos);
    pos.y = -(((f32) idx * spacing) + pos.y);

    text = HSD_SisLib_803A6754(0, 1);
    data->v.texts[idx] = text;
    text->font_size.x = 0.035F;
    text->font_size.y = 0.035F;
    text->pos_x = pos.x + row_text_offset.x;
    text->pos_y = pos.y + row_text_offset.y;
    text->pos_z = 17.0F;
    text->default_kerning = 1;
    text->text_color = row_text_color;
    HSD_SisLib_803A6B98(text, 0.0F, 0.0F, "%s",
                        page->events[event_idx]->name);
}

static void drawRows(TmEssData* data)
{
    s32 i;
    for (i = 0; i < ESS_ROWS; i++) {
        drawRow(i, data->v.first_event + i);
    }
}

/// Description box. Same box as mnEvent_8024D7E0, filled with the event's
/// own text (one sub-text per '\n'-separated line) instead of a SIS entry.
static void drawDescription(TmEssData* data, const TmEventDesc* desc)
{
    char line[ESS_DESC_LINE_LEN];
    const char* src;
    HSD_Text* text;
    s32 line_num = 0;

    if (data->v.desc_text != NULL) {
        HSD_SisLib_803A5CC4(data->v.desc_text);
        data->v.desc_text = NULL;
    }
    if (desc == NULL || desc->description == NULL) {
        return;
    }

    text = HSD_SisLib_803A5ACC(0, 1, -9.5F, 8.0F, 17.0F, 364.68332F,
                               38.38772F);
    data->v.desc_text = text;
    text->font_size.x = 0.0521F;
    text->font_size.y = 0.0521F;

    src = desc->description;
    while (*src != '\0' && line_num < ESS_DESC_LINES) {
        s32 len = 0;
        s32 subtext;

        while (*src != '\0' && *src != '\n') {
            if (len < ESS_DESC_LINE_LEN - 1) {
                line[len++] = *src;
            }
            src++;
        }
        if (*src == '\n') {
            src++;
        }
        line[len] = '\0';

        subtext = HSD_SisLib_803A6B98(text, 0.0F,
                                      line_num * ESS_DESC_LINE_HEIGHT, "%s",
                                      line);
        HSD_SisLib_803A7548(text, subtext, ESS_DESC_TEXT_SCALE,
                            ESS_DESC_TEXT_SCALE);
        HSD_SisLib_803A74F0(text, subtext, (GXColor*) &desc_text_color);
        line_num++;
    }
}

static void drawPageName(TmEssData* data)
{
    HSD_Text* text;

    if (data->page_text != NULL) {
        HSD_SisLib_803A5CC4(data->page_text);
    }
    text = HSD_SisLib_803A6754(0, 1);
    data->page_text = text;
    text->font_size.x = ESS_PAGE_TEXT_SCALE;
    text->font_size.y = ESS_PAGE_TEXT_SCALE;
    text->pos_x = ESS_PAGE_TEXT_X;
    text->pos_y = ESS_PAGE_TEXT_Y;
    text->pos_z = 17.0F;
    text->default_kerning = 1;
    text->text_color = row_text_color;
    if (tm_event_page_num > 1) {
        HSD_SisLib_803A6B98(text, 0.0F, 0.0F, "< L   %s   R >",
                            currentPage()->name);
    } else {
        HSD_SisLib_803A6B98(text, 0.0F, 0.0F, "%s", currentPage()->name);
    }
}

/// Moves the highlight to the cursor row. From mnEvent_SetPageCursorY.
static void updateCursor(TmEssData* data)
{
    HSD_JObj* tree = mnEvent_804D6C60->hsd_obj;
    HSD_JObj* jobj_0A;
    HSD_JObj* jobj_0B;
    HSD_JObj* jobj_0C;
    f32 y_a;
    f32 y_b;

    lb_80011E24(tree, &jobj_0A, 0xA, -1);
    lb_80011E24(tree, &jobj_0C, 0xC, -1);
    y_a = HSD_JObjGetTranslationY(jobj_0A);
    y_b = HSD_JObjGetTranslationY(jobj_0C);
    lb_80011E24(tree, &jobj_0B, 0xB, -1);
    HSD_JObjSetTranslateY(jobj_0B, (f32) data->v.page * (y_b - y_a));
}

/// Refreshes everything that depends on the selected event. From
/// mnEvent_ShowSelected; the score panel is left on its first frame.
static void showSelected(TmEssData* data)
{
    const TmEventPage* page = currentPage();
    s32 selected = data->v.first_event + data->v.page;
    HSD_JObj* jobj_09;

    updateCharacterPanel();
    drawDescription(data, selected < page->event_num ? page->events[selected]
                                                     : NULL);
    lb_80011E24(mnEvent_804D6C60->hsd_obj, &jobj_09, 9, -1);
    HSD_JObjReqAnimAll(jobj_09, 0.0F);
    HSD_JObjAnimAll(jobj_09);
    updateArrows(data);
}

static void changePage(TmEssData* data, s32 delta)
{
    s32 page = tm_persist.event_page + delta;

    if (page < 0 || page >= tm_event_page_num) {
        return;
    }
    sfxMove();
    tm_persist.event_page = page;
    data->v.first_event = 0;
    data->v.page = 0;
    drawPageName(data);
    drawRows(data);
    updateCursor(data);
    showSelected(data);
}

/// L / R presses this frame, digital or analog on any controller. The menu
/// input mask has no analog triggers, so they are edge-detected here.
static void readTriggers(TmEssData* data, u32 inputs, bool* l, bool* r)
{
    u8 analog_l = 0;
    u8 analog_r = 0;
    s32 i;

    for (i = 0; i < 4; i++) {
        HSD_PadStatus* pad = &HSD_PadCopyStatus[i];
        if (pad->err != 0) {
            continue;
        }
        if (pad->analogL >= ESS_TRIGGER_THRESHOLD) {
            analog_l = 1;
        }
        if (pad->analogR >= ESS_TRIGGER_THRESHOLD) {
            analog_r = 1;
        }
    }
    *l = (inputs & MenuInput_LTrigger) || (analog_l && !data->analog_l_prev);
    *r = (inputs & MenuInput_RTrigger) || (analog_r && !data->analog_r_prev);
    data->analog_l_prev = analog_l;
    data->analog_r_prev = analog_r;
}

/// Per-frame input. From mnEvent_8024D864.
static void ess_Input(HSD_GObj* gobj)
{
    TmEssData* data;
    u32 inputs;
    bool l;
    bool r;

    if (mn_804D6BC8.cooldown != 0) {
        mn_804D6BC8.cooldown -= 1;
        mn_804D6BC8.x2 = 0;
        mn_804D6BC8.x4 = 0;
        return;
    }

    inputs = mn_804A04F0.buttons = mn_80229624(4);

    if (inputs & MenuInput_Back) {
        sfxBack();
        mn_804A04F0.entering_menu = 0;
        mn_80229894(1, 1, 3);
        return;
    }

    if (mnEvent_804D6C64 != 0) {
        mnEvent_804D6C64 -= 1;
        return;
    }

    if (mnEvent_804D6C60 == NULL) {
        ess_Create();
    }
    data = getData();
    readTriggers(data, inputs, &l, &r);

    if (inputs & MenuInput_Confirm) {
        s32 selected = data->v.first_event + data->v.page;
        if (selected >= currentPage()->event_num) {
            return;
        }
        sfxForward();
        tm_persist.event_index = selected;
        tm_persist.event_active = true;
        gm_801677E8(mn_802295AC());
        mn_80229860(GM_TRAINING);
        return;
    }

    if (l) {
        changePage(data, -1);
    } else if (r) {
        changePage(data, 1);
    } else if (inputs & MenuInput_XButton) {
        s32 max_first = maxFirstEvent();
        if (data->v.first_event != max_first) {
            sfxMove();
            data->v.first_event += ESS_ROWS;
            if (data->v.first_event > max_first) {
                data->v.first_event = max_first;
            }
            drawRows(data);
            showSelected(data);
        }
    } else if (inputs & MenuInput_YButton) {
        if (data->v.first_event != 0) {
            sfxMove();
            data->v.first_event -= ESS_ROWS;
            if (data->v.first_event < 0) {
                data->v.first_event = 0;
            }
            drawRows(data);
            showSelected(data);
        }
    } else if (inputs & MenuInput_Up) {
        if (data->v.page != 0) {
            sfxMove();
            data->v.page -= 1;
            updateCursor(data);
            showSelected(data);
        } else if (data->v.first_event != 0) {
            sfxMove();
            data->v.first_event -= 1;
            drawRows(data);
            showSelected(data);
        }
    } else if (inputs & MenuInput_Down) {
        if (data->v.page < maxCursorRow()) {
            sfxMove();
            data->v.page += 1;
            updateCursor(data);
            showSelected(data);
        } else if (data->v.first_event < maxFirstEvent()) {
            sfxMove();
            data->v.first_event += 1;
            drawRows(data);
            showSelected(data);
        }
    }
}

static void freeTexts(TmEssData* data)
{
    if (data->v.desc_text != NULL) {
        HSD_SisLib_803A5CC4(data->v.desc_text);
        data->v.desc_text = NULL;
    }
    if (data->page_text != NULL) {
        HSD_SisLib_803A5CC4(data->page_text);
        data->page_text = NULL;
    }
}

static void setProc(HSD_GObj* gobj, HSD_GObjEvent fn)
{
    HSD_GObjProc* proc = HSD_GObj_SetupProc(gobj, fn, 0);
    proc->flags_3 = HSD_GObj_804D783C;
}

/// Plays the outro, then frees the rows and the screen. From
/// mnEvent_8024E1B4.
static void ess_ProcOutro(HSD_GObj* gobj)
{
    TmEssData* data = gobj->user_data;
    s32 i;

    if (mn_8022EC18(gobj->hsd_obj, &mnEvent_803EF74C, 0x80) >=
        mnEvent_803EF74C.end_frame)
    {
        for (i = 0; i < ESS_ROWS; i++) {
            if (data->v.texts[i] != NULL) {
                HSD_SisLib_803A5CC4(data->v.texts[i]);
                data->v.texts[i] = NULL;
            }
        }
        HSD_GObjFree(gobj);
    }
}

/// Idle loop until another menu is opened. From mnEvent_8024E2A0.
static void ess_ProcIdle(HSD_GObj* gobj)
{
    HSD_JObj* jobj;

    if (mn_804A04F0.cur_menu != ESS_MENU_ID) {
        HSD_GObjProc_RemoveProc(HSD_GObj_CurrentInvokedProc);
        setProc(gobj, ess_ProcOutro);
        freeTexts(gobj->user_data);
    } else {
        lb_80011E24(gobj->hsd_obj, &jobj, 1, -1);
        mn_8022ED6C(jobj, &mnEvent_803EF758);
    }
}

/// Intro animation. From mnEvent_8024E34C.
static void ess_ProcIntro(HSD_GObj* gobj)
{
    if (mn_804A04F0.cur_menu != ESS_MENU_ID) {
        HSD_GObjProc_RemoveProc(HSD_GObj_CurrentInvokedProc);
        setProc(gobj, ess_ProcOutro);
        freeTexts(gobj->user_data);
    } else if (mn_8022EC18(gobj->hsd_obj, &mnEvent_803EF740, 0x80) ==
               mnEvent_803EF740.end_frame)
    {
        HSD_GObjProc_RemoveProc(HSD_GObj_CurrentInvokedProc);
        setProc(gobj, ess_ProcIdle);
    }
}

/// Builds the screen. From mnEvent_8024E524 and mnEvent_8024E420.
static void ess_Create(void)
{
    const TmEventPage* page = currentPage();
    StaticModelDesc* assets = &MenMainConEv;
    HSD_GObj* gobj;
    HSD_JObj* tree;
    TmEssData* data;
    s32 selected;
    s32 max_first;

    gobj = GObj_Create(6, 7, 0x80);
    mnEvent_804D6C60 = gobj;
    tree = HSD_JObjLoadJoint(assets->joint);
    HSD_GObjObject_80390A70(gobj, HSD_GObj_JObjKind, tree);
    GObj_SetupGXLink(gobj, HSD_GObj_JObjCallback, 4, 0x80);
    HSD_JObjAddAnimAll(tree, assets->animjoint, assets->matanim_joint,
                       assets->shapeanim_joint);
    HSD_JObjReqAnimAll(tree, 0.0F);
    HSD_JObjAnimAll(tree);

    data = HSD_MemAlloc(sizeof(TmEssData));
    memset(data, 0, sizeof(TmEssData));
    GObj_InitUserData(gobj, 0, HSD_Free, data);

    /* Put the cursor back on the last selected event. */
    selected = tm_persist.event_index;
    if (selected >= page->event_num) {
        selected = 0;
    }
    max_first = maxFirstEvent();
    if (selected <= max_first) {
        data->v.first_event = selected;
        data->v.page = 0;
    } else {
        data->v.first_event = max_first;
        data->v.page = selected - max_first;
    }

    updateCursor(data);
    setProc(gobj, ess_ProcIntro);
    drawPageName(data);
    drawRows(data);
    showSelected(data);
}

/// `function` hook target replacing `mnEvent_8024E838`, the entry of the
/// vanilla Event Match select screen. @p event_idx (the vanilla event to
/// highlight) is ignored: the selection comes from #tm_persist.
void tm_Hook_EventSelectEnter(int event_idx, bool first_time)
{
    mn_804D6BC8.cooldown = 5;
    mn_804A04F0.prev_menu = mn_804A04F0.cur_menu;
    mn_804A04F0.cur_menu = ESS_MENU_ID;
    mn_804A04F0.hovered_selection = 0;

    mnEvent_804D6C64 = first_time ? 0x14 : 0;
    mnEvent_804D6C60 = NULL;

    /* The art of the vanilla screen; the "cleared" mark is not needed. */
    lbArchive_LoadSections(
        mn_804D6BB8, &MenMainConEv.joint, "MenMainConEv_Top_joint",
        &MenMainConEv.animjoint, "MenMainConEv_Top_animjoint",
        &MenMainConEv.matanim_joint, "MenMainConEv_Top_matanim_joint",
        &MenMainConEv.shapeanim_joint, "MenMainConEv_Top_shapeanim_joint", 0);

    if (!first_time) {
        ess_Create();
    }

    setProc(GObj_Create(0, 1, 0x80), ess_Input);
}
