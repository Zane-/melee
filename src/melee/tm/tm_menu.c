#include "tm_menu.h"

#include "tm.h"

#include <string.h>
#include <dolphin/gx.h>
#include <melee/gm/gmscene.h>
#include <melee/if/ifall.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/lb/lbspdisplay.h>
#include <sysdolphin/baselib/archive.h>
#include <sysdolphin/baselib/cobj.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/debug.h>
#include <sysdolphin/baselib/dobj.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjgxlink.h>
#include <sysdolphin/baselib/gobjobject.h>
#include <sysdolphin/baselib/gobjplink.h>
#include <sysdolphin/baselib/gobjuserdata.h>
#include <sysdolphin/baselib/jobj.h>
#include <sysdolphin/baselib/memory.h>
#include <sysdolphin/baselib/mobj.h>
#include <sysdolphin/baselib/sislib.h>

/* Stick directions reported as buttons in HSD_PadStatus (no vanilla names). */
#define PAD_STICK_UP (1 << 16)
#define PAD_STICK_DOWN (1 << 17)
#define PAD_STICK_LEFT (1 << 18)
#define PAD_STICK_RIGHT (1 << 19)

#define PAD_UP (PAD_STICK_UP | HSD_PAD_DPADUP)
#define PAD_DOWN (PAD_STICK_DOWN | HSD_PAD_DPADDOWN)
#define PAD_LEFT (PAD_STICK_LEFT | HSD_PAD_DPADLEFT)
#define PAD_RIGHT (PAD_STICK_RIGHT | HSD_PAD_DPADRIGHT)

/* GX link arguments */
#define GXLINK_MENUMODEL 12
#define GXPRI_MENUMODEL 80
#define GXLINK_MENUTEXT 12
#define GXPRI_MENUTEXT (GXPRI_MENUMODEL + 1)
#define GXPRI_POPUPMODEL (GXPRI_MENUTEXT + 1)
#define GXPRI_POPUPTEXT (GXPRI_POPUPMODEL + 1)
#define MENUCAM_GXPRI 9

/* Layout, in TM-CE's units */
#define MENU_CANVASSCALE 0.05F
#define MENU_TITLEXPOS -430.0F
#define MENU_TITLEYPOS -366.0F
#define MENU_TITLESCALE 2.3F
#define MENU_TITLEASPECT 870.0F
#define MENU_DESCXPOS -21.5F
#define MENU_DESCYPOS 12.0F
#define MENU_DESCTXTASPECT 885.0F
#define MENU_DESCYOFFSET 30.0F
#define MENU_OPTIONNAMEXPOS -430.0F
#define MENU_OPTIONNAMEYPOS -230.0F
#define MENU_NAMEASPECT 440.0F
#define MENU_OPTIONVALXPOS 250.0F
#define MENU_OPTIONVALYPOS -230.0F
#define MENU_TEXTYOFFSET 50.0F
#define MENU_VALASPECT 280.0F
#define MENUSCROLL_SCALE 2.0F
#define MENUSCROLL_SCALEY (1.105F * MENUSCROLL_SCALE)
#define MENUSCROLL_X 22.5F
#define MENUSCROLL_Y 12.0F
#define MENUSCROLL_MAXLENGTH 10.0F
#define ROWBOX_HEIGHT 2.3F
#define ROWBOX_WIDTH 18.0F
#define ROWBOX_X 12.5F
#define ROWBOX_Y 10.8F
#define ROWBOX_YOFFSET -2.5F
#define MENUHIGHLIGHT_HEIGHT ROWBOX_HEIGHT
#define MENUHIGHLIGHT_WIDTH 43.175F
#define MENUHIGHLIGHT_X 0.0F
#define MENUHIGHLIGHT_Y ROWBOX_Y
#define MENUHIGHLIGHT_YOFFSET ROWBOX_YOFFSET

#define SFX_BACK 0
#define SFX_SELECT 1
#define SFX_MOVE 2
#define SFX_ERROR 4
#define SFX_PAUSE 5

#define MENU_ASSERT(cond, msg)                                                \
    ((cond) ? ((void) 0) : __assert("tm_menu.c", __LINE__, msg))

/// Vanilla pad library defaults (sysdolphin/baselib/controller.c); it has no
/// declaration in a header.
extern PadLibData default_libinfo_data;

static const GXColor rowbox_color = { 25, 25, 45, 255 };
static const GXColor rowbox_on_color = { 25, 225, 25, 255 };
static const GXColor highlight_color = { 255, 211, 0, 255 };
static const GXColor scroll_color = { 255, 211, 0, 255 };
static const GXColor text_enabled_color = { 255, 255, 255, 255 };
static const GXColor text_disabled_color = { 128, 128, 128, 0 };

static TmMenu* instantiate(TmMenuData* data, const TmMenuDesc* desc);
static void createModel(HSD_GObj* gobj);
static void createText(HSD_GObj* gobj);
static void menuThink(HSD_GObj* gobj, TmMenu* menu);
static void runFuncOption(HSD_GObj* gobj, TmOption* option);
static void menuGX(HSD_GObj* gobj, intptr_t pass);
static void textGX(HSD_GObj* gobj, intptr_t pass);

static inline TmMenuData* getData(HSD_GObj* gobj)
{
    return gobj->user_data;
}

static inline HSD_Material* boxMaterial(HSD_JObj* jobj)
{
    return jobj->u.dobj->next->mobj->mat;
}

static TmMenu* findMenu(TmMenuData* data, const TmMenuDesc* desc)
{
    int i;
    for (i = 0; i < data->menu_count; i++) {
        if (data->menus[i]->desc == desc) {
            return data->menus[i];
        }
    }
    return NULL;
}

/// Builds the live copy of @p desc and, recursively, of its submenus. A
/// definition reachable from several places gets one live copy.
static TmMenu* instantiate(TmMenuData* data, const TmMenuDesc* desc)
{
    TmMenu* menu;
    int i;

    menu = findMenu(data, desc);
    if (menu != NULL) {
        return menu;
    }
    MENU_ASSERT(data->menu_count < TM_MENU_MAXMENUS, "Too many menus");

    menu = HSD_MemAlloc(sizeof(TmMenu));
    memset(menu, 0, sizeof(TmMenu));
    menu->desc = desc;
    menu->options = HSD_MemAlloc(desc->option_num * sizeof(TmOption));
    memset(menu->options, 0, desc->option_num * sizeof(TmOption));
    data->menus[data->menu_count++] = menu;

    for (i = 0; i < desc->option_num; i++) {
        TmOption* option = &menu->options[i];
        option->d = desc->options[i];
        option->val = option->d.value_default;
        option->val_prev = option->d.value_default;
        if (option->d.kind == TM_OPTKIND_MENU && option->d.menu != NULL) {
            option->submenu = instantiate(data, option->d.menu);
        }
    }
    return menu;
}

HSD_GObj* tmMenu_Init(const TmMenuDesc* start_menu, const TmMenuAssets* assets)
{
    HSD_CObjDesc*** scene_data;
    HSD_GObj* cam_gobj;
    HSD_GObj* gobj;
    TmMenuData* data;

    MENU_ASSERT(start_menu != NULL, "No menu");
    MENU_ASSERT(assets != NULL, "No menu assets");

    /* Camera for the menu, from the HUD archive like TM-CE does. */
    scene_data = HSD_ArchiveGetPublicAddress(*ifAll_GetArchive(),
                                               "ScInfDmg_scene_data");
    cam_gobj = GObj_Create(19, 20, 0);
    HSD_GObjObject_80390A70(cam_gobj, HSD_GObj_CameraKind,
                            HSD_CObjLoadDesc(scene_data[1][0]));
    GObj_SetupGXLinkMax(cam_gobj, HSD_GObj_803910D8, MENUCAM_GXPRI);
    cam_gobj->gxlink_prios = (1 << GXLINK_MENUMODEL) | (1 << GXLINK_MENUTEXT);

    gobj = GObj_Create(0, 0, 0);
    data = HSD_MemAlloc(sizeof(TmMenuData));
    memset(data, 0, sizeof(TmMenuData));
    GObj_InitUserData(gobj, 4, HSD_Free, data);
    data->assets = assets;

    GObj_SetupGXLink(gobj, HSD_GObj_JObjCallback, GXLINK_MENUMODEL,
                     GXPRI_MENUMODEL);

    data->canvas_menu = HSD_SisLib_803A611C(2, cam_gobj, 9, 13, 0,
                                            GXLINK_MENUTEXT, GXPRI_MENUTEXT,
                                            MENUCAM_GXPRI);
    data->canvas_popup = HSD_SisLib_803A611C(2, cam_gobj, 9, 13, 0,
                                             GXLINK_MENUTEXT, GXPRI_POPUPTEXT,
                                             MENUCAM_GXPRI);
    data->curr_menu = instantiate(data, start_menu);
    data->curr_menu->shortcuts = start_menu->shortcuts;

    if (tm_state != NULL) {
        tm_state->menu_gobj = gobj;
    }

    createModel(gobj);
    createText(gobj);
    data->hide_menu = 1;

    return gobj;
}

TmMenu* tmMenu_Find(HSD_GObj* gobj, const TmMenuDesc* desc)
{
    return findMenu(getData(gobj), desc);
}

TmOption* tmMenu_Options(HSD_GObj* gobj, const TmMenuDesc* desc)
{
    TmMenu* menu = findMenu(getData(gobj), desc);
    MENU_ASSERT(menu != NULL, "Menu is not part of the tree");
    return menu->options;
}

void tmMenu_EnterMenu(HSD_GObj* gobj)
{
    TmMenuData* data = getData(gobj);

    data->mode = TM_MENUMODE_PAUSED;
    tmMenu_UpdateText(gobj);

    /* Speed up repeat behaviour (defaults are 8 and 45). */
    HSD_PadLibData.repeat_interval = TM_MENU_RAPID_INTERVAL;
    HSD_PadLibData.repeat_start = TM_MENU_RAPID_START;

    /* Freeze the game. */
    gm_SetDbPauseFlag(1);
    lbAudioAx_80024030(SFX_PAUSE);
    ifAll_802F3394();
    lbAudioAx_80024E84(true);
}

void tmMenu_ExitMenu(HSD_GObj* gobj)
{
    TmMenuData* data = getData(gobj);

    data->mode = TM_MENUMODE_NORMAL;
    data->hide_menu = 1;

    /* Let a custom submenu clean itself up before we exit. */
    if (data->custom_gobj_destroy != NULL) {
        data->custom_gobj_destroy(data->custom_gobj);
        data->custom_gobj = NULL;
        data->custom_gobj_think = NULL;
        data->custom_gobj_destroy = NULL;
    }

    HSD_PadLibData.repeat_interval = default_libinfo_data.repeat_interval;
    HSD_PadLibData.repeat_start = default_libinfo_data.repeat_start;

    /* Unfreeze the game. */
    gm_ClearDbPauseFlag(1);
    ifAll_802F33CC();
    lbAudioAx_80024E84(false);
}

void tmMenu_PrevMenu(HSD_GObj* gobj)
{
    TmMenuData* data = getData(gobj);
    TmMenu* menu = data->curr_menu;

    MENU_ASSERT(menu->prev != NULL, "No previous menu");

    /* Reset the cursor so it starts at the top on re-entry. */
    menu->scroll = 0;
    menu->cursor = 0;

    data->curr_menu = menu->prev;
    tmMenu_UpdateText(gobj);
}

void tmMenu_NextMenu(HSD_GObj* gobj, TmMenu* next_menu)
{
    TmMenuData* data = getData(gobj);

    MENU_ASSERT(next_menu != NULL, "Missing next menu");

    /* Shortcuts propagate forward from the base menu. */
    next_menu->shortcuts = data->curr_menu->shortcuts;
    next_menu->prev = data->curr_menu;
    data->curr_menu = next_menu;

    tmMenu_UpdateText(gobj);
}

void tmMenu_ChangeOptionVal(HSD_GObj* gobj, TmOption* option, int val)
{
    switch (option->d.kind) {
    case TM_OPTKIND_STRING:
    case TM_OPTKIND_INT:
        MENU_ASSERT(val >= option->d.value_min &&
                        val - option->d.value_min < option->d.value_num,
                    "Illegal option value");
        break;
    case TM_OPTKIND_TOGGLE:
        MENU_ASSERT(val == 0 || val == 1, "Illegal option value");
        break;
    default:
        MENU_ASSERT(false, "Option kind has no value");
        break;
    }

    option->val_prev = option->val;
    option->val = val;
    if (option->d.on_change != NULL) {
        option->d.on_change(gobj, val);
    }

    tmMenu_UpdateText(gobj);
}

static void runShortcuts(HSD_GObj* gobj, HSD_PadStatus* pad)
{
    TmMenuData* data = getData(gobj);
    const TmShortcutList* shortcuts = data->curr_menu->shortcuts;
    int i;

    for (i = 0; i < shortcuts->count; i++) {
        const TmShortcut* shortcut = &shortcuts->list[i];
        TmMenu* owner;
        TmOption* option;

        MENU_ASSERT(shortcut->menu != NULL && shortcut->button_mask != 0,
                    "Invalid shortcut definition");
        if (!(pad->trigger & shortcut->button_mask)) {
            continue;
        }
        owner = findMenu(data, shortcut->menu);
        MENU_ASSERT(owner != NULL, "Shortcut menu is not part of the tree");
        option = &owner->options[shortcut->option_index];

        if (option->d.disable) {
            lbAudioAx_80024030(SFX_ERROR);
            continue;
        }

        if (option->d.kind == TM_OPTKIND_TOGGLE) {
            tmMenu_ChangeOptionVal(gobj, option, !option->val);
            lbAudioAx_80024030(option->val ? SFX_MOVE : SFX_BACK);
        } else if (option->d.kind == TM_OPTKIND_FUNC) {
            runFuncOption(gobj, option);
        } else if (option->d.kind == TM_OPTKIND_STRING ||
                   option->d.kind == TM_OPTKIND_INT)
        {
            int val = (option->val + 1 - option->d.value_min) %
                          option->d.value_num +
                      option->d.value_min;
            tmMenu_ChangeOptionVal(gobj, option, val);
            lbAudioAx_80024030(SFX_MOVE);
        } else if (option->d.kind == TM_OPTKIND_MENU) {
            if (data->curr_menu == option->submenu) {
                continue;
            }
            /* Rewind to the top-level menu before opening the target. */
            while (data->curr_menu->prev != NULL) {
                tmMenu_PrevMenu(gobj);
            }
            tmMenu_NextMenu(gobj, option->submenu);
            lbAudioAx_80024030(SFX_SELECT);
        } else {
            MENU_ASSERT(false, "Invalid shortcut option kind");
        }
        break;
    }
}

void tmMenu_Update(HSD_GObj* gobj)
{
    TmMenuData* data = getData(gobj);
    HSD_PadStatus* pad;
    bool pause_pressed = false;
    int pause_index = 0;
    int i;

    data->frames++;

    /* TM-CE: do not let events that skip the stage select pause on their
     * first frames, but always allow unpausing. */
    if (data->frames > 3 || data->mode == TM_MENUMODE_PAUSED) {
        for (i = 0; i < 4; i++) {
            if (HSD_PadMasterStatus[i].trigger & HSD_PAD_START) {
                pause_pressed = true;
                pause_index = i;
                break;
            }
        }
    }

    if (data->mode == TM_MENUMODE_NORMAL) {
        if (pause_pressed) {
            tmMenu_EnterMenu(gobj);
            data->controller_index = pause_index;
        }
        return;
    }
    if (data->custom_gobj_think != NULL) {
        /* Delegate to the custom submenu and hide the base menu meanwhile.
         * It returns nonzero when it allows unpausing. */
        data->hide_menu = 1;
        if (data->custom_gobj_think(data->custom_gobj) && pause_pressed) {
            tmMenu_ExitMenu(gobj);
        }
        return;
    }
    if (pause_pressed) {
        tmMenu_ExitMenu(gobj);
        return;
    }

    data->hide_menu = 0;
    pad = &HSD_PadMasterStatus[data->controller_index];

    if ((pad->button & HSD_PAD_Y) && data->curr_menu->shortcuts != NULL) {
        runShortcuts(gobj, pad);
    } else if (data->mode == TM_MENUMODE_PAUSED) {
        menuThink(gobj, data->curr_menu);
    }
}

static void menuGX(HSD_GObj* gobj, intptr_t pass)
{
    if (!getData(gobj)->hide_menu) {
        HSD_GObj_JObjCallback(gobj, pass);
    }
}

static void textGX(HSD_GObj* gobj, intptr_t pass)
{
    if (tm_state == NULL || tm_state->menu_gobj == NULL) {
        return;
    }
    if (!getData(tm_state->menu_gobj)->hide_menu) {
        HSD_SisLib_803A84BC(gobj, pass);
    }
}

static void runFuncOption(HSD_GObj* gobj, TmOption* option)
{
    MENU_ASSERT(option->d.on_select != NULL, "Missing menu function");
    option->d.on_select(gobj);

    tmMenu_UpdateText(gobj);
    lbAudioAx_80024030(SFX_SELECT);
}

static void menuThink(HSD_GObj* gobj, TmMenu* menu)
{
    TmMenuData* data = getData(gobj);
    HSD_PadStatus* pad = &HSD_PadMasterStatus[data->controller_index];
    u32 inputs = pad->repeat;
    s32 cursor = menu->cursor;
    s32 scroll = menu->scroll;
    s32 option_num = menu->desc->option_num;
    TmOption* curr;
    int i;

    /* Speed up scrolling while R is held. */
    if ((pad->button & HSD_PAD_R) ||
        pad->analogR >= TM_ANALOG_TRIGGER_THRESHOLD)
    {
        if (pad->repeat_count > TM_MENU_RAPID_R) {
            pad->repeat_count = TM_MENU_RAPID_R;
        }
    }

    curr = &menu->options[cursor + scroll];

    if (inputs & PAD_DOWN) {
        int step = 0;
        for (i = 1; cursor + scroll + i < option_num; i++) {
            if (!menu->options[cursor + scroll + i].d.disable) {
                step = i;
                break;
            }
        }
        if (step == 0) {
            return;
        }
        cursor += step;

        /* If the cursor went too far down, scroll to compensate. */
        if (cursor >= TM_MENU_MAXOPTION - TM_MENU_SCROLLOFF) {
            int max_scroll = option_num - TM_MENU_MAXOPTION - scroll;
            int want_scroll =
                cursor - TM_MENU_MAXOPTION + TM_MENU_SCROLLOFF + 1;
            int delta;
            if (max_scroll < 0) {
                max_scroll = 0;
            }
            delta = MIN(want_scroll, max_scroll);
            scroll += delta;
            cursor -= delta;
        }
        menu->cursor = cursor;
        menu->scroll = scroll;

        tmMenu_UpdateText(gobj);
        lbAudioAx_80024030(SFX_MOVE);
    } else if (inputs & PAD_UP) {
        int step = 0;
        for (i = 1; cursor + scroll - i >= 0; i++) {
            if (!menu->options[cursor + scroll - i].d.disable) {
                step = i;
                break;
            }
        }
        if (step == 0) {
            return;
        }
        cursor -= step;

        /* If the cursor went too far up, scroll to compensate. */
        if (cursor < TM_MENU_SCROLLOFF) {
            int delta = MIN(TM_MENU_SCROLLOFF - cursor, scroll);
            scroll -= delta;
            cursor += delta;
        }
        menu->cursor = cursor;
        menu->scroll = scroll;

        tmMenu_UpdateText(gobj);
        lbAudioAx_80024030(SFX_MOVE);
    } else if ((inputs & HSD_PAD_B) && menu->prev != NULL) {
        tmMenu_PrevMenu(gobj);
        lbAudioAx_80024030(SFX_BACK);
    } else if (curr->d.kind == TM_OPTKIND_TOGGLE &&
               (inputs & (PAD_LEFT | PAD_RIGHT | HSD_PAD_A)))
    {
        tmMenu_ChangeOptionVal(gobj, curr, !curr->val);
        lbAudioAx_80024030(SFX_MOVE);
    } else if (inputs & PAD_LEFT) {
        if ((curr->d.kind == TM_OPTKIND_STRING ||
             curr->d.kind == TM_OPTKIND_INT) &&
            curr->val > curr->d.value_min)
        {
            tmMenu_ChangeOptionVal(gobj, curr, curr->val - 1);
            lbAudioAx_80024030(SFX_MOVE);
        }
    } else if (inputs & PAD_RIGHT) {
        if ((curr->d.kind == TM_OPTKIND_STRING ||
             curr->d.kind == TM_OPTKIND_INT) &&
            curr->val - curr->d.value_min < curr->d.value_num - 1)
        {
            tmMenu_ChangeOptionVal(gobj, curr, curr->val + 1);
            lbAudioAx_80024030(SFX_MOVE);
        }
    } else if (inputs & HSD_PAD_A) {
        if (curr->d.kind == TM_OPTKIND_MENU) {
            tmMenu_NextMenu(gobj, curr->submenu);
            lbAudioAx_80024030(SFX_SELECT);
        } else if (curr->d.kind == TM_OPTKIND_FUNC) {
            runFuncOption(gobj, curr);
        }
    }
}

/// Positions the four corner joints of a box model.
static void setBox(HSD_JObj* box, float x, float y, float w, float h)
{
    HSD_JObj* corners[4];

    lb_80011E24(box, corners, 2, 3, 4, 5, -1);
    corners[0]->translate.x = -(w / 2.0F) + x;
    corners[0]->translate.y = (h / 2.0F) + y;
    corners[1]->translate.x = (w / 2.0F) + x;
    corners[1]->translate.y = (h / 2.0F) + y;
    corners[2]->translate.x = -(w / 2.0F) + x;
    corners[2]->translate.y = -(h / 2.0F) + y;
    corners[3]->translate.x = (w / 2.0F) + x;
    corners[3]->translate.y = -(h / 2.0F) + y;
}

static void createModel(HSD_GObj* gobj)
{
    TmMenuData* data = getData(gobj);
    const TmMenuAssets* assets = data->assets;
    HSD_JObj* root;
    HSD_JObj* highlight;
    HSD_JObj* scroll;
    HSD_JObj* ends[2];
    int i;

    /* Options background. */
    root = HSD_JObjLoadJoint(assets->menu);
    HSD_GObjObject_80390A70(gobj, HSD_GObj_JObjKind, root);
    HSD_GObjGXLink_8039084C(gobj);
    GObj_SetupGXLink(gobj, menuGX, GXLINK_MENUMODEL, GXPRI_MENUMODEL);

    /* One rowbox per visible row: the background behind the option value. */
    for (i = 0; i < TM_MENU_MAXOPTION; i++) {
        HSD_JObj* rowbox = HSD_JObjLoadJoint(assets->popup);
        HSD_JObjAddChild(root, rowbox);
        setBox(rowbox, ROWBOX_X, ROWBOX_Y + i * ROWBOX_YOFFSET, ROWBOX_WIDTH,
               ROWBOX_HEIGHT);
        HSD_JObjSetFlags(rowbox, JOBJ_HIDDEN);
        HSD_DObjSetFlags(rowbox->u.dobj, DOBJ_HIDDEN);
        boxMaterial(rowbox)->alpha = 0.6F;
        boxMaterial(rowbox)->diffuse = rowbox_color;
        data->rowboxes[i] = rowbox;
    }

    /* Highlight bar. */
    highlight = HSD_JObjLoadJoint(assets->popup);
    HSD_JObjAddChild(root, highlight);
    HSD_DObjSetFlags(highlight->u.dobj, DOBJ_HIDDEN); /* remove outline */
    setBox(highlight, MENUHIGHLIGHT_X, MENUHIGHLIGHT_Y, MENUHIGHLIGHT_WIDTH,
           MENUHIGHLIGHT_HEIGHT);
    boxMaterial(highlight)->alpha = 0.4F;
    boxMaterial(highlight)->diffuse = highlight_color;
    data->highlight_menu = highlight;

    /* Scroll bar. */
    scroll = HSD_JObjLoadJoint(assets->scroll);
    HSD_JObjAddChild(root, scroll);
    lb_80011E24(scroll, ends, 2, 3, -1);
    scroll->scale.x = MENUSCROLL_SCALE;
    scroll->scale.y = MENUSCROLL_SCALEY;
    scroll->translate.x = MENUSCROLL_X;
    scroll->translate.y = MENUSCROLL_Y;
    data->scroll_top = ends[0];
    data->scroll_bot = ends[1];
    boxMaterial(scroll)->alpha = 0.6F;
    boxMaterial(scroll)->diffuse = scroll_color;
    data->scrollbar = scroll;
}

static HSD_Text* newText(TmMenuData* data, float aspect)
{
    HSD_Text* text = HSD_SisLib_803A6754(2, data->canvas_menu);

    text->entity->render_cb = textGX;
    text->default_kerning = 1;
    text->default_fitting = 1;
    text->box_size_x = aspect;
    text->font_size.x = MENU_CANVASSCALE;
    text->font_size.y = MENU_CANVASSCALE;
    return text;
}

static void createText(HSD_GObj* gobj)
{
    TmMenuData* data = getData(gobj);
    HSD_Text* text;
    int subtext;
    int i;

    MENU_ASSERT(data->text_name == NULL && data->text_value == NULL &&
                    data->text_title == NULL && data->text_desc == NULL,
                "Menu text already created");

    /* Title */
    text = newText(data, MENU_TITLEASPECT);
    data->text_title = text;
    subtext = HSD_SisLib_803A6B98(text, MENU_TITLEXPOS, MENU_TITLEYPOS, "");
    HSD_SisLib_803A7548(text, subtext, MENU_TITLESCALE, MENU_TITLESCALE);

    /* Description */
    text = newText(data, MENU_DESCTXTASPECT);
    data->text_desc = text;
    text->pos_x = MENU_DESCXPOS;
    text->pos_y = MENU_DESCYPOS;
    for (i = 0; i < TM_MENU_DESCLINEMAX; i++) {
        HSD_SisLib_803A6B98(text, 0.0F, i * MENU_DESCYOFFSET, "");
    }

    /* Option names */
    text = newText(data, MENU_NAMEASPECT);
    data->text_name = text;
    for (i = 0; i < TM_MENU_MAXOPTION; i++) {
        HSD_SisLib_803A6B98(text, MENU_OPTIONNAMEXPOS,
                            MENU_OPTIONNAMEYPOS + i * MENU_TEXTYOFFSET, "");
    }

    /* Option values */
    text = newText(data, MENU_VALASPECT);
    data->text_value = text;
    text->default_alignment = 1;
    for (i = 0; i < TM_MENU_MAXOPTION; i++) {
        HSD_SisLib_803A6B98(text, MENU_OPTIONVALXPOS,
                            MENU_OPTIONVALYPOS + i * MENU_TEXTYOFFSET, "");
    }
}

void tmMenu_UpdateText(HSD_GObj* gobj)
{
    TmMenuData* data = getData(gobj);
    TmMenu* menu = data->curr_menu;
    s32 cursor = menu->cursor;
    s32 scroll = menu->scroll;
    s32 option_num = menu->desc->option_num;
    TmOption* curr = &menu->options[cursor + scroll];
    GXColor color;
    int i;

    HSD_SisLib_803A70A0(data->text_title, 0, "%s", menu->desc->name);

    for (i = 0; i < TM_MENU_DESCLINEMAX; i++) {
        const char* line = curr->d.desc[i];
        HSD_SisLib_803A70A0(data->text_desc, i, "%s", line != NULL ? line : "");
    }

    for (i = 0; i < MIN(option_num, TM_MENU_MAXOPTION); i++) {
        TmOption* option = &menu->options[scroll + i];
        HSD_JObj* rowbox = data->rowboxes[i];

        HSD_SisLib_803A70A0(data->text_name, i, "%s", option->d.name);

        HSD_JObjClearFlags(rowbox, JOBJ_HIDDEN);
        boxMaterial(rowbox)->diffuse = rowbox_color;

        if (option->d.kind == TM_OPTKIND_STRING) {
            HSD_SisLib_803A70A0(data->text_value, i, "%s",
                                option->d.values[option->val]);
        } else if (option->d.kind == TM_OPTKIND_INT) {
            HSD_SisLib_803A70A0(data->text_value, i, (char*) option->d.format,
                                option->val);
        } else if (option->d.kind == TM_OPTKIND_TOGGLE) {
            if (option->val) {
                HSD_SisLib_803A70A0(data->text_value, i, "On");
                boxMaterial(rowbox)->diffuse = rowbox_on_color;
            } else {
                HSD_SisLib_803A70A0(data->text_value, i, "Off");
            }
        } else if ((option->d.kind == TM_OPTKIND_INFO ||
                    option->d.kind == TM_OPTKIND_FUNC) &&
                   option->d.value_string != NULL)
        {
            HSD_SisLib_803A70A0(data->text_value, i, "%s",
                                option->d.value_string);
        } else {
            HSD_SisLib_803A70A0(data->text_value, i, "");
            HSD_JObjSetFlags(rowbox, JOBJ_HIDDEN);
        }

        /* Grey out disabled options. */
        color = option->d.disable ? text_disabled_color : text_enabled_color;
        HSD_SisLib_803A74F0(data->text_name, i, &color);
        HSD_SisLib_803A74F0(data->text_value, i, &color);
    }

    /* Blank the rows past the end of the options. */
    for (i = option_num; i < TM_MENU_MAXOPTION; i++) {
        HSD_SisLib_803A70A0(data->text_name, i, "");
        HSD_SisLib_803A70A0(data->text_value, i, "");
        HSD_JObjSetFlags(data->rowboxes[i], JOBJ_HIDDEN);
    }

    data->highlight_menu->translate.y = cursor * MENUHIGHLIGHT_YOFFSET;

    if (option_num > TM_MENU_MAXOPTION) {
        float len;
        float space;
        float top;

        MENU_ASSERT(scroll <= option_num - TM_MENU_MAXOPTION,
                    "Invalid scroll position");
        len = ((float) TM_MENU_MAXOPTION / option_num) * MENUSCROLL_MAXLENGTH;
        space = MENUSCROLL_MAXLENGTH - len;
        top = space * scroll / (option_num - TM_MENU_MAXOPTION);

        /* The bar grows and moves in the negative Y direction. */
        data->scroll_top->translate.y = -top;
        data->scroll_bot->translate.y = -len;
        HSD_JObjClearFlags(data->scrollbar, JOBJ_HIDDEN);
    } else {
        HSD_JObjSetFlags(data->scrollbar, JOBJ_HIDDEN);
    }

    HSD_JObjSetMtxDirtySub(gobj->hsd_obj);
}
