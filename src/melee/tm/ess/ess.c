#include "ess.h"

#include <dolphin/gx.h>
#include <dolphin/pad.h>
#include <melee/gm/gm_1601.h>
#include <melee/gm/gm_1A36.h>
#include <melee/gm/gmevent.h>
#include <melee/gm/gmmain_lib.h>
#include <melee/lb/lb_00F9.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/lb/lblanguage.h>
#include <melee/mn/inlines.h>
#include <melee/mn/mnmain.h>
#include <melee/mn/mnstagesw.h>
#include <melee/mn/types.h>
#include <melee/tm/tmce.h>
#include <sysdolphin/baselib/archive.h>
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

/* ---- vanilla statics of mn/mnevent.c (unique names) -------------------- */

extern HSD_GObj* mnEvent_804D6C60; ///< the ESS gobj (menu model + texts)
extern u8 mnEvent_804D6C64;        ///< frames to wait before input
extern u8 mnEvent_804D6C65;        ///< event to open on
extern AnimLoopSettings mnEvent_803EF740;
extern AnimLoopSettings mnEvent_803EF758;
extern Vec3 mnEvent_803EF764; ///< "Lv. N" text offset from the row
extern Vec3 mnEvent_803EF770; ///< name text offset from the row
extern GXColor mnEvent_804D5028;
extern StaticModelDesc MenMainConEv;
void mnEvent_8024E1B4(HSD_GObj* gobj);

/* gm/gm_1A36.c: static; layout as there. */
struct EssPadMap {
    /* 00 */ u64 button;
    /* 08 */ u64 trigger;
    /* 10 */ u64 repeat;
    /* 18 */ u64 release;
    /* 20 */ u64 repeat2;
    /* 28 */ s32 repeat_timer;
    /* 2C */ s32 x2C;
};
extern struct {
    struct EssPadMap x0[PAD_MAX_CONTROLLERS + 1];
} controller_map;

/* ---- TM-CE ESS state ------------------------------------------------------
 * TM-CE keeps these in vanilla r13 slots (-0x4EB4/-0x4EB0/-0x4EAC) and in
 * data words inside its code. Statics are fine here (offline menu). */

static HSD_Text* ess_text_main;  ///< page name, L/R hints, version
static HSD_Text* ess_text_left;  ///< "<"
static HSD_Text* ess_text_right; ///< ">"
static u8 ess_prev_analog_l;
static u8 ess_prev_analog_r;
static HSD_GObj* ess_help_gobj;
static HSD_Text* ess_help_text;
static u8 ess_help_cooldown;

#define ESS_ANALOG_TRIGGER_THRESHOLD 43 /* Globals.s */
#define ESS_CURSOR_ROW_STEP -1.32F      /* jump cursor Y per row */

static inline u8* essCard(void)
{
    return (u8*) gmMainLib_804D3EE0;
}

static inline int essPage(void)
{
    return essCard()[TMCE_CARD_EVENT_PAGE];
}

static inline MnEventData* essData(void)
{
    return mnEvent_804D6C60->user_data;
}

/// Texts created like TM-CE's `Text_CreateTextStruct(0, 0)` for the ESS.
static HSD_Text* essCreateText(void)
{
    HSD_Text* text = HSD_SisLib_803A6754(0, 0);
    text->default_kerning = 1;
    text->default_alignment = 1;
    text->pos_z = 17.0F;
    text->font_size.x = 0.035F;
    text->font_size.y = 0.035F;
    return text;
}

static void essRemoveText(HSD_Text** text)
{
    if (*text != NULL) {
        HSD_SisLib_803A5CC4(*text);
        *text = NULL;
    }
}

/// Jump Down/Up - Update Cursor.asm: the highlight follows the row.
static void essSetCursorY(f32 y)
{
    HSD_JObj* jobj;
    lb_80011E24(mnEvent_804D6C60->hsd_obj, &jobj, 0xB, -1);
    HSD_JObjSetTranslateY(jobj, y);
}

/* ---- mnEvent_8024CE74 ------------------------------------------------------
 * Unlock Event 1.asm (+0x50, skip the unlock count) and
 * OnlyDisplayEventsOnPage.asm (+0x188, the result): the furthest scroll
 * offset is the page's last event index minus 8. */
s32 tm_Ess_MaxScroll(void)
{
    s32 last = GetPageEventNum(essPage());
    if (last >= 8) {
        return last - 8;
    }
    return last;
}

/* ---- mnEvent_8024D15C: one row of the list --------------------------------
 * Spoof All Events as Not Played.asm (+0x12C): no "cleared" mark.
 * SkipDisplayingEventNames.asm (+0x28C): rows past the page's last event
 * stay empty.
 * Display Custom Event Names on ESS.asm (+0x314): the second text is the
 * TM-CE event name (grey if the event has no C file) instead of the vanilla
 * SIS name. */
void tm_Ess_DrawRow(s32 idx, s32 event_id)
{
    static const GXColor no_file_color = { 180, 180, 180, 255 };
    HSD_JObj* jobj_0A;
    HSD_JObj* jobj_0C;
    Vec3 pos;
    MnEventData* data = essData();
    HSD_JObj* tree = mnEvent_804D6C60->hsd_obj;
    HSD_Text* text;
    f32 spacing;
    int page = essPage();

    lb_80011E24(tree, &jobj_0A, 0xA, -1);
    lb_80011E24(tree, &jobj_0C, 0xC, -1);
    spacing = HSD_JObjGetTranslationY(jobj_0A);
    spacing = HSD_JObjGetTranslationY(jobj_0C) - spacing;
    HSD_JObjGetTranslation(jobj_0A, &pos);
    pos.y = -(((f32) idx * spacing) + pos.y);

    if (data->gobjs[idx] != NULL) {
        HSD_GObjFree(data->gobjs[idx]);
        data->gobjs[idx] = NULL;
    }
    /* vanilla: cleared mark if gmMainLib_8015CEFC(event_id); TM-CE: never */

    if (data->texts[idx] != NULL) {
        HSD_SisLib_803A5CC4(data->texts[idx]);
    }
    if (event_id > GetPageEventNum(page)) {
        data->texts[idx] = NULL;
        essRemoveText(&data->icons[idx]);
        return;
    }

    text = HSD_SisLib_803A6754(0, 1);
    data->texts[idx] = text;
    text->font_size.x = 0.035F;
    text->font_size.y = 0.035F;
    text->pos_x = pos.x + mnEvent_803EF764.x;
    text->pos_y = pos.y + mnEvent_803EF764.y;
    text->pos_z = 17.0F;
    text->default_kerning = 1;
    text->text_color = mnEvent_804D5028;
    HSD_SisLib_803A6B98(text, 0.0F, 0.0F, "Ｌｖ． %d", event_id + 1);

    if (data->icons[idx] != NULL) {
        HSD_SisLib_803A5CC4(data->icons[idx]);
    }
    text = HSD_SisLib_803A6754(0, 0);
    data->icons[idx] = text;
    text->pos_x = pos.x + mnEvent_803EF770.x;
    text->pos_y = pos.y + mnEvent_803EF770.y;
    text->pos_z = 17.0F;
    text->box_size_x = 364.68332F;
    text->box_size_y = 38.38772F;
    text->font_size.x = 0.035F;
    text->font_size.y = 0.035F;
    text->default_fitting = 1;
    text->default_kerning = 1;
    HSD_SisLib_803A6B98(text, 0.0F, 0.0F, "%s", GetEventName(page, event_id));
    if (GetEventFile(page, event_id) == NULL) {
        HSD_SisLib_803A74F0(text, 0, (GXColor*) &no_file_color);
    }
}

/* ---- mnEvent_8024D7E0: description box ------------------------------------
 * Display Custom Event Descriptions.asm (+0x2C): the TM-CE description,
 * converted to menu text and written into the text's buffer behind TM-CE's
 * own SIS header (color 0xAAAAAA, scale 0xB3).
 * Toggle Tutorial Text.asm (+0x6C): hide "<" on the first page and ">" on
 * the last one. The `idx` argument (vanilla's SIS event index) is unused. */
void tm_Ess_DrawDescription(HSD_GObj* gobj, s32 idx)
{
    static const u8 header[11] = { 0x16, 0x0C, 0xAA, 0xAA, 0xAA, 0x0E,
                                   0x00, 0xB3, 0x00, 0xB3, 0x18 };
    MnEventData* data = gobj->user_data;
    u8 converted[0x1C0];
    HSD_Text* text;
    SisBuffer* alloc;
    s32 len;
    u32 need;
    int page = essPage();

    if (data->desc_text != NULL) {
        HSD_SisLib_803A5CC4(data->desc_text);
    }

    text = HSD_SisLib_803A6754(0, 0);
    data->desc_text = text;
    text->pos_x = -9.5F;
    text->pos_y = 8.0F;
    text->pos_z = 17.0F;
    text->box_size_x = 364.68332F;
    text->box_size_y = 38.38772F;
    text->font_size.x = 0.0521F;
    text->font_size.y = 0.0521F;

    len = HSD_SisLib_803A67EC(
        converted,
        (u8*) GetEventDescription(page, data->page + data->first_event));

    /* Grow the buffer the way HSD_SisLib_803A6B98 does. */
    alloc = text->alloc_data;
    need = (alloc->end - alloc->data) + 17 + len;
    if (alloc->size < need) {
        u8* old = alloc->data;
        u8* buf;
        s32 used = alloc->end - old;
        s32 i;

        alloc->size += (((need - alloc->size) >> 7) + 1) << 7;
        buf = HSD_SisLib_Alloc(alloc->size);
        for (i = 0; i < used + 1; i++) {
            buf[i] = old[i];
        }
        alloc->data = buf;
        text->sis_buffer = buf;
        alloc->end = buf + used;
        HSD_SisLib_Free(old);
    }
    memcpy(text->sis_buffer, header, sizeof(header));
    memcpy(text->sis_buffer + sizeof(header), converted, len);
    text->sis_buffer[sizeof(header) + len] = 0x19;
    text->sis_buffer[sizeof(header) + len + 1] = 0x00;

    if (ess_text_left != NULL) {
        ess_text_left->hidden = page == 0;
    }
    if (ess_text_right != NULL) {
        ess_text_right->hidden = page == GetPageNum();
    }
}

/* ---- Custom ESS Button Actions.asm (mnEvent_8024D864+0xC8) ---------------
 */

/* 37x37 QR code linking TM-CE's tutorial video series; a clear bit is a
 * dark square. */
static const u32 ess_qr[43] = {
    0x018AE33C, 0x03EBF3BA, 0xAF9142D6, 0xDD448A26, 0x655A245A, 0xE02D513E,
    0xCC5ADAF8, 0x05555550, 0x1FE8309A, 0xFF7D156E, 0x898EF548, 0xDFE14117,
    0x127251C4, 0x7BCC9765, 0xDCA7E6DB, 0x5F3E3731, 0x5E26316F, 0x9885FAAF,
    0xBD51D980, 0xD095D3D4, 0xDBFF1461, 0x2C521334, 0x5454FBF5, 0xED023351,
    0x95BF1517, 0x65AB0082, 0xD7809260, 0xA19B07D5, 0x55A771F2, 0x139E8795,
    0xD4301AD0, 0x289F2A9C, 0xE72686A8, 0x4201FF87, 0xB173B006, 0xF023D5CF,
    0xB13FCCEF, 0x45DAC900, 0x4A2FAD85, 0xEC916FFE, 0x65E0FB84, 0xCFEA6017,
    0x3A672F7F,
};

static inline void essQuad(f32 x0, f32 y0, f32 x1, f32 y1, u32 color)
{
    GXWGFifo.f32 = x0;
    GXWGFifo.f32 = y0;
    GXWGFifo.u32 = color;
    GXWGFifo.f32 = x1;
    GXWGFifo.f32 = y0;
    GXWGFifo.u32 = color;
    GXWGFifo.f32 = x1;
    GXWGFifo.f32 = y1;
    GXWGFifo.u32 = color;
    GXWGFifo.f32 = x0;
    GXWGFifo.f32 = y1;
    GXWGFifo.u32 = color;
}

/// HelpGX: draws the QR code on pass 2, with whatever vertex format the
/// previous drawing on this link left set (as TM-CE does): XY f32, color.
static void essHelpDraw(HSD_GObj* gobj, int pass)
{
    const f32 x_min = 210.0F;
    const f32 y_min = 50.0F;
    const f32 sq = 6.0F;
    const u32 black = 0x101010FF;
    const u32 white = 0xE0E0E0FF;
    const u32* qr = ess_qr;
    s32 bit = 31;
    s32 xi;
    s32 yi;
    f32 x;
    f32 y;

    if (pass != 2) {
        return;
    }
    /* background plus the 681 dark squares, four vertices each */
    GXBegin(GX_QUADS, GX_VTXFMT0, 2728);
    essQuad(x_min - 3.0F * sq, y_min - 3.0F * sq, x_min + 40.0F * sq,
            y_min + 40.0F * sq, white);
    y = y_min;
    for (yi = 0; yi < 37; yi++) {
        x = x_min;
        for (xi = 0; xi < 37; xi++) {
            if (bit < 0) {
                qr++;
                bit = 31;
            }
            if (((*qr >> bit) & 1) == 0) {
                essQuad(x, y, x + sq, y + sq, black);
            }
            bit--;
            x += sq;
        }
        y += sq;
    }
}

static void essCloseHelp(void)
{
    HSD_GObjFree(ess_help_gobj);
    HSD_SisLib_803A5CC4(ess_help_text);
    ess_help_gobj = NULL;
    ess_help_text = NULL;
}

/// R: "TM-CE Tips / Tutorial Video Series" panel with a QR code.
static void essOpenHelp(bool hard_r)
{
    HSD_Text* text;
    s32 sub;

    if (!hard_r) {
        /* analog press: ignore the digital click that usually follows */
        ess_help_cooldown = 15;
    }
    ess_help_gobj = GObj_Create(0, 0, 0);
    GObj_SetupGXLink(ess_help_gobj, essHelpDraw, 17, 0);

    text = HSD_SisLib_803A6754(0, 1);
    ess_help_text = text;
    text->default_kerning = 1;
    text->text_color.r = 0x10;
    text->text_color.g = 0x10;
    text->text_color.b = 0x10;
    text->text_color.a = 0xFF;
    text->bg_color.r = 0xE0;
    text->bg_color.g = 0xE0;
    text->bg_color.b = 0xE0;
    text->bg_color.a = 0xFF;
    text->font_size.x = 0.0306F;
    text->font_size.y = 0.0306F;
    text->pos_x = -9.69F;
    text->pos_y = -7.0F;
    sub = HSD_SisLib_803A6B98(text, 90.0F, 350.0F, "TM-CE Tips");
    HSD_SisLib_803A7548(text, sub, 2.0F, 2.0F);
    sub = HSD_SisLib_803A6B98(text, 115.0F, 430.0F, "Tutorial Video Series");
    HSD_SisLib_803A7548(text, sub, 1.0F, 1.0F);
}

/// L: open the OSD toggles (the rules menu's "random stage select" screen
/// with entering_menu = 3; the OSD menu itself is TM-CE's Onscreen Display
/// assembly, not ported yet).
static void essOpenOsdMenu(void)
{
    MnEventData* data = essData();

    sfxForward();
    mn_804A04F0.entering_menu = 3;
    mn_804D6BC8.cooldown = 5;
    gm_801BEB74(data->page + data->first_event);
    mnStageSw_80237410();
    HSD_GObjFree(HSD_GObj_CurrentInvokedProcGObj);
}

/// L/R (D-pad or stick) change the TM-CE event page.
static void essSwitchPage(s32 dir)
{
    MnEventData* data;
    s32 last = GetPageNum();
    s32 page = essCard()[TMCE_CARD_EVENT_PAGE] + dir;
    s32 i;

    essCard()[TMCE_CARD_EVENT_PAGE] = page;
    if (page > last) {
        essCard()[TMCE_CARD_EVENT_PAGE] = page - 1;
        return;
    }
    if (page < 0) {
        essCard()[TMCE_CARD_EVENT_PAGE] = 0;
        return;
    }

    HSD_SisLib_803A70A0(ess_text_main, 0, "%s", GetPageName(page));

    data = essData();
    data->first_event = 0;
    data->page = 0;
    for (i = 0; i < 9; i++) {
        tm_Ess_DrawRow(i, i);
    }
    tm_Ess_DrawDescription(mnEvent_804D6C60, 0);
    mnEvent_8024D5B0(mnEvent_804D6C60, 0);
    essSetCursorY(0.0F);
    sfxMove();
}

static void essButtonActions(void)
{
    struct EssPadMap* pad = &controller_map.x0[PAD_MAX_CONTROLLERS];
    u32 trigger_lo = (u32) pad->trigger;
    u64 rapid;
    u8 max_l = 0;
    u8 max_r = 0;
    bool press_l;
    bool press_r;
    s32 i;

    /* Analog presses count too: track the strongest of all four pads. */
    for (i = 0; i < PAD_MAX_CONTROLLERS; i++) {
        if (HSD_PadMasterStatus[i].analogL >= max_l) {
            max_l = HSD_PadMasterStatus[i].analogL;
        }
        if (HSD_PadMasterStatus[i].analogR >= max_r) {
            max_r = HSD_PadMasterStatus[i].analogR;
        }
    }
    press_l = ess_prev_analog_l < ESS_ANALOG_TRIGGER_THRESHOLD &&
              max_l >= ESS_ANALOG_TRIGGER_THRESHOLD;
    press_r = ess_prev_analog_r < ESS_ANALOG_TRIGGER_THRESHOLD &&
              max_r >= ESS_ANALOG_TRIGGER_THRESHOLD;
    ess_prev_analog_l = max_l;
    ess_prev_analog_r = max_r;
    if (trigger_lo & PAD_TRIGGER_L) {
        press_l = true;
    }
    if (trigger_lo & PAD_TRIGGER_R) {
        press_r = true;
    }

    if (ess_help_gobj != NULL) {
        if (ess_help_cooldown != 0) {
            ess_help_cooldown--;
            if (trigger_lo & PAD_TRIGGER_R) {
                press_r = false;
            }
        }
        /* any menu button, L/R or release closes the panel */
        if (((u32) (pad->trigger >> 32) | press_l | press_r) != 0 ||
            (u32) (pad->release >> 32) != 0)
        {
            essCloseHelp();
        }
        return;
    }

    if (press_l) {
        essOpenOsdMenu();
        return;
    }
    if (press_r) {
        essOpenHelp((trigger_lo & PAD_TRIGGER_R) != 0);
        return;
    }

    rapid = gm_801A36C0(PAD_MAX_CONTROLLERS);
    if (rapid & PAD_ANY_LEFT) {
        essSwitchPage(-1);
    } else if (rapid & PAD_ANY_RIGHT) {
        essSwitchPage(1);
    }
}

/* ---- mnEvent_8024D864: per-frame input -------------------------------- */

static inline void essRefreshRows(s32 first_event)
{
    s32 i;
    for (i = 0; i < 9; i++) {
        tm_Ess_DrawRow(i, first_event + i);
    }
}

/// Vanilla mnEvent_ShowSelected, with `cursor` (Jump * - Update Cursor.asm)
/// applied before the scroll arrows are updated.
static void essShowSelected(MnEventData* data, bool cursor)
{
    HSD_JObj* jobj_09;
    s32 event = gm_801BEBA8((u8) (data->first_event + data->page));
    HSD_GObj* gobj = mnEvent_804D6C60;

    mnEvent_8024D0CC(gobj, (s8) gm_801BEBF8(event & 0xFF));
    tm_Ess_DrawDescription(gobj, event);
    mnEvent_8024D5B0(gobj, event);
    lb_80011E24(gobj->hsd_obj, &jobj_09, 9, -1);
    HSD_JObjReqAnimAll(jobj_09,
                       (f32) (u8) gm_801BEB8C(gm_801BEBC0((u8) event) & 0xFF));
    HSD_JObjAnimAll(jobj_09);
    if (cursor) {
        essSetCursorY((f32) data->page * ESS_CURSOR_ROW_STEP);
    }
    mnEvent_8024D014(gobj);
}

static inline void essSetPageCursorY(MnEventData* data)
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
    HSD_JObjSetTranslateY(jobj_0B, (f32) data->page * (y_b - y_a));
}

/// Jump Down.asm (X, +0x134): 9 events down, clamped to the page.
static void essJumpDown(MnEventData* data)
{
    s32 last = GetPageEventNum(essPage());
    s32 event = data->page + data->first_event;

    if (event >= last) {
        return;
    }
    if (event + 9 < last) {
        data->page += 9;
    } else if (last >= 9) {
        data->page = 8;
        data->first_event = last - 8;
    } else {
        data->page = last;
        data->first_event = 0;
    }
    if (data->page > 8) {
        data->first_event += data->page - 8;
        data->page = 8;
    }
    if (data->first_event > last - 8) {
        if (last > 8) {
            data->page = 8;
            data->first_event = last - 8;
        } else {
            data->page = last;
            data->first_event = 0;
        }
    }
    sfxMove();
    essRefreshRows(data->first_event);
    essShowSelected(data, true);
}

/// Jump Up.asm (Y, +0x258): 9 events up, clamped to the first.
static void essJumpUp(MnEventData* data)
{
    s32 event = data->page + data->first_event;
    s8 row;

    if (event <= 0) {
        return;
    }
    if (event - 9 <= 0) {
        data->page = 0;
        data->first_event = 0;
    } else {
        data->page -= 9;
    }
    row = (s8) data->page;
    if (row < 0) {
        data->first_event += row;
        data->page = 0;
    }
    sfxMove();
    essRefreshRows(data->first_event);
    essShowSelected(data, true);
}

void tm_Ess_Think(HSD_GObj* gobj)
{
    MnEventData* data;
    u64 inputs;

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
        tm_Ess_Create(mnEvent_804D6C65);
    }

    essButtonActions();

    data = mnEvent_804D6C60->user_data;
    if (inputs & MenuInput_Confirm) {
        sfxForward();
        gm_801BEB74(data->first_event + data->page);
        gm_801677E8(mn_802295AC());
        mn_80229860(GM_EVENT);
        return;
    }

    if (inputs & MenuInput_XButton) {
        essJumpDown(data);
    } else if (inputs & MenuInput_YButton) {
        essJumpUp(data);
    } else if (inputs & MenuInput_Up) {
        if (data->page != 0) {
            sfxMove();
            data->page -= 1;
            essSetPageCursorY(data);
            essShowSelected(data, false);
            return;
        }
        if (data->first_event != 0) {
            sfxMove();
            data->first_event -= 1;
            essRefreshRows(data->first_event);
            essShowSelected(data, false);
        }
    } else if (inputs & MenuInput_Down) {
        /* CannotScrollPastEventsOnPage.asm (+0x664) */
        if (data->page >= GetPageEventNum(essPage())) {
            return;
        }
        if (data->page < 8) {
            sfxMove();
            data->page += 1;
            essSetPageCursorY(data);
            essShowSelected(data, false);
            return;
        }
        if (data->first_event < tm_Ess_MaxScroll()) {
            sfxMove();
            data->first_event += 1;
            essRefreshRows(data->first_event);
            essShowSelected(data, false);
        }
    }
}

/* ---- mnEvent_8024E2A0 / mnEvent_8024E34C: leaving the screen --------------
 * Remove Version Indicator 1/2.asm (+0x64): remove TM-CE's texts too. */

static void essRemoveTexts(MnEventData* data)
{
    HSD_SisLib_803A5CC4(data->desc_text);
    essRemoveText(&ess_text_main);
    essRemoveText(&ess_text_left);
    essRemoveText(&ess_text_right);
    HSD_SisLib_803A5CC4(data->name_text);
}

void tm_Ess_LeaveA(HSD_GObj* gobj)
{
    HSD_GObjProc* proc;
    HSD_JObj* jobj;
    MnEventData* data = gobj->user_data;

    if (mn_804A04F0.cur_menu != 7) {
        HSD_GObjProc_RemoveProc(HSD_GObj_CurrentInvokedProc);
        proc = HSD_GObj_SetupProc(gobj, mnEvent_8024E1B4, 0);
        proc->flags_3 = HSD_GObj_804D783C;
        essRemoveTexts(data);
    } else {
        lb_80011E24(gobj->hsd_obj, &jobj, 1, -1);
        mn_8022ED6C(jobj, &mnEvent_803EF758);
    }
}

void tm_Ess_LeaveB(HSD_GObj* gobj)
{
    HSD_GObjProc* proc;
    MnEventData* data = gobj->user_data;

    if (mn_804A04F0.cur_menu != 7) {
        HSD_GObjProc_RemoveProc(HSD_GObj_CurrentInvokedProc);
        proc = HSD_GObj_SetupProc(gobj, mnEvent_8024E1B4, 0);
        proc->flags_3 = HSD_GObj_804D783C;
        essRemoveTexts(data);
    } else {
        f32 frame = mn_8022EC18(gobj->hsd_obj, &mnEvent_803EF740, 0x80);
        if (frame == mnEvent_803EF740.end_frame) {
            HSD_GObjProc_RemoveProc(HSD_GObj_CurrentInvokedProc);
            proc = HSD_GObj_SetupProc(gobj, tm_Ess_LeaveA, 0);
            proc->flags_3 = HSD_GObj_804D783C;
        }
    }
}

/* ---- mnEvent_8024E420: initial cursor --------------------------------------
 * Never Scroll If Less than 9 Events on Page.asm (+0x18). */
void tm_Ess_InitData(MnEventData* data, s32 event_idx)
{
    s32 max_scroll;
    int i;

    if (GetPageEventNum(essPage()) < 9) {
        data->first_event = 0;
        data->page = event_idx;
    } else {
        max_scroll = tm_Ess_MaxScroll();
        if (event_idx < max_scroll) {
            data->first_event = event_idx;
            data->page = 0;
        } else {
            data->first_event = max_scroll;
            data->page = event_idx - max_scroll;
        }
    }

    data->desc_text = NULL;
    data->name_text = NULL;
    for (i = 0; i < 9; i++) {
        data->gobjs[i] = NULL;
        data->texts[i] = NULL;
        data->icons[i] = NULL;
    }
}

/* ---- mnEvent_8024E524: build the screen -----------------------------------
 * Event Code Version Indicator.asm (+0x44): page name, "L = OSD",
 * "R = Help", TM-CE version and the page arrows. */

static void essCreateIndicators(void)
{
    static const GXColor version_color = { 0x8D, 0xFF, 0x6E, 0xFF };
    HSD_Text* text;
    s32 sub;

    /* The help panel cannot be open here; drop pointers from an old scene. */
    ess_help_gobj = NULL;
    ess_help_text = NULL;

    text = essCreateText();
    ess_text_main = text;
    HSD_SisLib_803A6B98(text, 0.0F, -240.0F, "%s", GetPageName(essPage()));
    sub = HSD_SisLib_803A6B98(text, -310.0F, -230.0F, "L = OSD");
    HSD_SisLib_803A7548(text, sub, 0.8F, 0.8F);
    sub = HSD_SisLib_803A6B98(text, 310.0F, -230.0F, "R = Help");
    HSD_SisLib_803A7548(text, sub, 0.8F, 0.8F);
    sub = HSD_SisLib_803A6B98(text, 0.0F, -212.0F, "%s", GetTMVersLong());
    HSD_SisLib_803A7548(text, sub, 0.6F, 0.6F);
    HSD_SisLib_803A74F0(text, sub, (GXColor*) &version_color);

    text = essCreateText();
    ess_text_left = text;
    sub = HSD_SisLib_803A6B98(text, -210.0F, -215.0F, "<");
    HSD_SisLib_803A7548(text, sub, 0.7F, 0.7F);

    text = essCreateText();
    ess_text_right = text;
    sub = HSD_SisLib_803A6B98(text, 210.0F, -215.0F, ">");
    HSD_SisLib_803A7548(text, sub, 0.7F, 0.7F);
}

void tm_Ess_Create(s32 event_idx)
{
    HSD_JObj* jobj_0A;
    HSD_JObj* jobj_0B;
    HSD_JObj* jobj_0C;
    HSD_GObj* gobj;
    HSD_GObjProc* proc;
    HSD_JObj* tree;
    MnEventData* user_data;
    StaticModelDesc* assets = &MenMainConEv;
    f32 y_a;
    f32 y_b;

    gobj = GObj_Create(6, 7, 0x80);
    mnEvent_804D6C60 = gobj;
    essCreateIndicators();
    tree = HSD_JObjLoadJoint(assets->joint);
    HSD_GObjObject_80390A70(gobj, HSD_GObj_JObjKind, tree);
    GObj_SetupGXLink(gobj, HSD_GObj_JObjCallback, 4, 0x80);
    HSD_JObjAddAnimAll(tree, assets->animjoint, assets->matanim_joint,
                       assets->shapeanim_joint);
    HSD_JObjReqAnimAll(tree, 0.0F);
    HSD_JObjAnimAll(tree);

    user_data = HSD_MemAlloc(sizeof(MnEventData));
    HSD_ASSERTREPORT(0x39B, user_data, "Can't get user_data.\n");
    tm_Ess_InitData(user_data, event_idx);
    GObj_InitUserData(gobj, 0, HSD_Free, user_data);

    lb_80011E24(tree, &jobj_0A, 0xA, -1);
    lb_80011E24(tree, &jobj_0C, 0xC, -1);
    y_a = HSD_JObjGetTranslationY(jobj_0A);
    y_b = HSD_JObjGetTranslationY(jobj_0C);
    lb_80011E24(tree, &jobj_0B, 0xB, -1);
    HSD_JObjSetTranslateY(jobj_0B, (f32) user_data->page * (y_b - y_a));

    proc = HSD_GObj_SetupProc(gobj, tm_Ess_LeaveB, 0);
    proc->flags_3 = HSD_GObj_804D783C;
    essRefreshRows(user_data->first_event);
    essShowSelected(user_data, false);
}

/* ---- Event High Scores
 * ------------------------------------------------------ Load/Save Event High
 * Scores.asm (gmMainLib_8015CF5C/8015CF70+0x4): one score slot per event
 * across all pages, from the vanilla array's start. */

static inline s32* essScoreSlot(s32 event)
{
    u8* card = essCard();
    s32 slot = GetPageEventOffset(card[TMCE_CARD_EVENT_PAGE]) + event;
    return (s32*) (card + TMCE_CARD_EVENT_SCORES) + slot;
}

s32 tm_Ess_GetScore(s32 event)
{
    return *essScoreSlot(event);
}

void tm_Ess_SetScore(s32 event, s32 score)
{
    *essScoreSlot(event) = score;
}

/* Custom Event Highscore Types.asm (gm_801BEB8C): score kind from the
 * TM-CE event instead of GmEvent.dat. */
bool tm_Ess_GetScoreType(u8 event)
{
    return GetScoreType(essPage(), event);
}

/* ---- Remove Event Texture.asm (mnMain_Scene_OnEnter+0x83C) ----------------
 * Make two main-menu materials transparent (alpha 0): the event
 * background and the subject table, US and JP variants. TM-CE finds the
 * file as `archive - 0x31 - file_size`, which (with the file buffer
 * allocated just before the HSD_Archive) is file start + pad - 0x11, pad
 * being the 32-byte round-up of the file. The +1 offsets are the JP file's
 * different padding. Kept as TM-CE computes it. Runs as a wrapper of the
 * `lbLang_IsSavedLanguageUS` call right after the archive is stored
 * (+0x840); the load call itself is variadic. */
bool tm_Ess_MainMenuLangUS(void)
{
    static const u32 offsets[4] = { 0x1E754, 0x1E755, 0x1EC88, 0x1EC89 };
    HSD_Archive* archive = mn_804D6BB8;
    u32 size = archive->header.file_size;
    u8* file = archive->data - sizeof(HSD_ArchiveHeader);
    u8* base = file + ((-size) & 0x1F) - 0x11;
    int i;

    for (i = 0; i < 4; i++) {
        u8* p = base + offsets[i] + 0xC;
        /* TM-CE stores a word; two of the four are unaligned */
        p[0] = 0;
        p[1] = 0;
        p[2] = 0;
        p[3] = 0;
    }
    return lbLang_IsSavedLanguageUS();
}
