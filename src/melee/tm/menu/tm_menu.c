#include "tm_menu.h"

#include "../controls/controls.h"

#include <math.h>

#include <dolphin/gx.h>
#include <dolphin/mtx.h>
#include <melee/gm/gm_1601.h>
#include <melee/gm/gm_1A3F.h>
#include <melee/gm/gmscene.h>
#include <melee/gm/types.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/mn/inlines.h>
#include <melee/mn/mnmain.h>
#include <sysdolphin/baselib/cobj.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjgxlink.h>
#include <sysdolphin/baselib/gobjproc.h>
#include <sysdolphin/baselib/sislib.h>
#include <sysdolphin/baselib/state.h>

/// src/tmce/addcodes_bridge.c
int tmce_ac_FindEvent(const char* file, int* page, int* event);
void tmce_ac_SetEventPage(int page);
/// gm/gmevent.c: choose the event the event mode will run.
void gm_801BEB74(u8 event);

/* The text canvas's camera looks at a 640 by 480 screen, y down. */
#define SCREEN_W 640.0F
#define SCREEN_H 480.0F
#define TEXT_GX_LINK 14
#define CORNER_STEPS 6
#define MAX_ITEMS 8
/// Height of a line of text at size 1.0, in screen units (measured).
#define TEXT_LINE 36.0F

typedef enum Action {
    Act_None,
    Act_Train,
    Act_Lab,
    Act_Events,
    Act_Versus,
    Act_Controls,
    Act_Back,
    Act_Delay,
    Act_Count
} Action;

typedef struct Item {
    const char* label;
    const char* desc;
    s16 x, y, w, h; ///< the panel, in screen units
    u8 action;
    u8 colour; ///< index into #palette
    f32 text_size;
} Item;

typedef struct Page {
    const char* title;
    const Item* items;
    int count;
} Page;

static const GXColor backdrop_top = { 14, 22, 46, 255 };
static const GXColor backdrop_bottom = { 34, 54, 92, 255 };
static const GXColor bar_colour = { 8, 12, 26, 220 };
static const GXColor edge_dark = { 6, 10, 22, 255 };
static const GXColor edge_light = { 255, 240, 170, 255 };
static const GXColor text_white = { 255, 255, 255, 255 };
static const GXColor text_dim = { 190, 200, 220, 255 };

/// Panel fills: train, practice, versus, settings.
static const GXColor palette[4] = {
    { 228, 122, 44, 255 },
    { 44, 150, 170, 255 },
    { 190, 62, 70, 255 },
    { 86, 96, 132, 255 },
};

/* No Versus panel yet: the vanilla Versus character select runs out of
   memory in the overlay build (docs/ai/training-courses.md, "Main menu"). */
static const Item main_items[] = {
    { "Train", "Pick a character and work through its course.", 40, 84, 330,
      190, Act_Train, 0, 1.35F },
    { "Lab", "Free practice with any character and situation.", 386, 84, 214,
      90, Act_Lab, 1, 0.9F },
    { "Events", "Training Mode's own events, page by page.", 386, 184, 214,
      90, Act_Events, 1, 0.9F },
    { "Controls", "Input delay and button layouts.", 40, 290, 560, 92,
      Act_Controls, 3, 0.9F },
};

static const Item controls_items[] = {
    { "Input delay", "Left, right: frames each pad is held back in a match.",
      60, 96, 520, 64, Act_Delay, 3, 0.75F },
    { "Back", "Return to the main menu.", 60, 300, 180, 64, Act_Back, 3,
      0.75F },
};

enum { Page_Main, Page_Controls, Page_Count };

static const Page pages[Page_Count] = {
    { "Main Menu", main_items, sizeof(main_items) / sizeof(main_items[0]) },
    { "Controls", controls_items,
      sizeof(controls_items) / sizeof(controls_items[0]) },
};

static struct {
    int page;
    int cursor;
    int frame;   ///< frames since the scene began, for the highlight's pulse
    int leaving; ///< an action was taken: ignore input until the scene ends
    HSD_Text* labels[MAX_ITEMS];
    HSD_Text* title;
    HSD_Text* desc;
} menu;

/* --- drawing -------------------------------------------------------------- */

static void Vertex(f32 x, f32 y)
{
    GXPosition3f32(x, -y, 0.0F);
}

static void Quad(f32 x0, f32 y0, f32 x1, f32 y1)
{
    GXBegin(GX_QUADS, GX_VTXFMT0, 4);
    Vertex(x0, y0);
    Vertex(x1, y0);
    Vertex(x1, y1);
    Vertex(x0, y1);
    GXEnd();
}

/// A quarter disc centred on (cx, cy), from angle a0, as a fan.
static void Corner(f32 cx, f32 cy, f32 r, f32 a0)
{
    int i;

    GXBegin(GX_TRIANGLEFAN, GX_VTXFMT0, CORNER_STEPS + 2);
    Vertex(cx, cy);
    for (i = 0; i <= CORNER_STEPS; i++) {
        f32 a = a0 + 1.5707964F * (f32) i / (f32) CORNER_STEPS;
        Vertex(cx + r * cosf(a), cy - r * sinf(a));
    }
    GXEnd();
}

static void SetColour(const GXColor* c)
{
    GXSetChanMatColor(GX_COLOR0A0, *c);
}

static void RoundRect(f32 x, f32 y, f32 w, f32 h, f32 r, const GXColor* c)
{
    SetColour(c);
    Quad(x + r, y, x + w - r, y + h);
    Quad(x, y + r, x + r, y + h - r);
    Quad(x + w - r, y + r, x + w, y + h - r);
    Corner(x + w - r, y + r, r, 0.0F);
    Corner(x + r, y + r, r, 1.5707964F);
    Corner(x + r, y + h - r, r, 3.1415927F);
    Corner(x + w - r, y + h - r, r, 4.712389F);
}

static void Shade(GXColor* out, const GXColor* in, f32 k)
{
    f32 r = in->r * k, g = in->g * k, b = in->b * k;
    out->r = r > 255.0F ? 255 : (u8) r;
    out->g = g > 255.0F ? 255 : (u8) g;
    out->b = b > 255.0F ? 255 : (u8) b;
    out->a = in->a;
}

static void Draw(HSD_GObj* gobj, int pass)
{
    const Page* page = &pages[menu.page];
    HSD_CObj* cobj = HSD_CObjGetCurrent();
    int i;

    (void) gobj;
    if (pass != 0 || cobj == NULL) {
        return;
    }
    GXSetNumChans(1);
    GXSetChanCtrl(GX_COLOR0A0, GX_FALSE, GX_SRC_REG, GX_SRC_REG, 0,
                  GX_DF_NONE, GX_AF_NONE);
    GXSetNumTexGens(0);
    GXSetNumTevStages(1);
    GXSetTevOrder(GX_TEVSTAGE0, GX_TEXCOORD_NULL, GX_TEXMAP_NULL,
                  GX_COLOR0A0);
    GXSetTevOp(GX_TEVSTAGE0, GX_PASSCLR);
    GXSetZMode(GX_FALSE, GX_ALWAYS, GX_FALSE);
    GXSetCullMode(GX_CULL_NONE);
    GXSetAlphaCompare(GX_ALWAYS, 0, GX_AOP_OR, GX_ALWAYS, 0);
    GXSetBlendMode(GX_BM_BLEND, GX_BL_SRCALPHA, GX_BL_INVSRCALPHA,
                   GX_LO_CLEAR);
    GXClearVtxDesc();
    GXSetVtxAttrFmt(GX_VTXFMT0, GX_VA_POS, GX_POS_XYZ, GX_F32, 0);
    GXSetVtxDesc(GX_VA_POS, GX_DIRECT);
    GXLoadPosMtxImm(HSD_CObjGetViewingMtxPtrDirect(cobj), GX_PNMTX0);
    GXSetCurrentMtx(GX_PNMTX0);

    /* Backdrop: two bands, then the title and description bars. */
    SetColour(&backdrop_top);
    Quad(0.0F, 0.0F, SCREEN_W, SCREEN_H * 0.5F);
    SetColour(&backdrop_bottom);
    Quad(0.0F, SCREEN_H * 0.5F, SCREEN_W, SCREEN_H);
    RoundRect(-20.0F, 24.0F, 300.0F, 40.0F, 20.0F, &bar_colour);
    RoundRect(40.0F, 396.0F, 560.0F, 40.0F, 12.0F, &bar_colour);

    for (i = 0; i < page->count; i++) {
        const Item* it = &page->items[i];
        GXColor fill;
        f32 x = it->x, y = it->y, w = it->w, h = it->h;
        f32 r = h * 0.28F;
        bool selected = i == menu.cursor;

        if (selected) {
            /* The highlighted panel grows a little and its edge pulses. */
            f32 pulse = 0.5F + 0.5F * sinf(menu.frame * 0.12F);
            GXColor edge;
            Shade(&edge, &edge_light, 0.75F + 0.25F * pulse);
            x -= 4.0F;
            y -= 4.0F;
            w += 8.0F;
            h += 8.0F;
            RoundRect(x - 5.0F, y - 5.0F, w + 10.0F, h + 10.0F, r + 5.0F,
                      &edge);
            Shade(&fill, &palette[it->colour], 1.12F);
        } else {
            RoundRect(x - 3.0F, y - 3.0F, w + 6.0F, h + 6.0F, r + 3.0F,
                      &edge_dark);
            Shade(&fill, &palette[it->colour], 0.82F);
        }
        RoundRect(x, y, w, h, r, &fill);
        /* A lighter band across the top third gives the panel some depth. */
        {
            GXColor sheen;
            Shade(&sheen, &fill, 1.18F);
            sheen.a = 90;
            RoundRect(x + 6.0F, y + 5.0F, w - 12.0F, h * 0.34F, r * 0.6F,
                      &sheen);
        }
    }
    HSD_StateInvalidate(-1);
}

/* --- text ----------------------------------------------------------------- */

/// A text object at (x, y) on the screen. A text's size scales the
/// positions of its lines too, so each label is its own object, placed by
/// its position, with one line at the origin.
static HSD_Text* NewText(f32 x, f32 y, f32 size, int alignment)
{
    HSD_Text* text = HSD_SisLib_803A6754(0, 0);

    text->pos_x = x;
    text->pos_y = y;
    text->font_size.x = size;
    text->font_size.y = size;
    text->default_kerning = 1;
    text->default_alignment = alignment;
    HSD_SisLib_803A6B98(text, 0.0F, 0.0F, " ");
    return text;
}

static void Refresh(void)
{
    const Page* page = &pages[menu.page];
    int i;

    HSD_SisLib_803A70A0(menu.title, 0, "%s", page->title);
    for (i = 0; i < page->count; i++) {
        const Item* it = &page->items[i];
        if (it->action == Act_Delay) {
            HSD_SisLib_803A70A0(menu.labels[i], 0, "%s   <  %d  >",
                                it->label, tm_ctl.delay);
        } else {
            HSD_SisLib_803A70A0(menu.labels[i], 0, "%s", it->label);
        }
        HSD_SisLib_803A74F0(menu.labels[i], 0,
                            (GXColor*) (i == menu.cursor ? &text_white
                                                         : &text_dim));
    }
    HSD_SisLib_803A70A0(menu.desc, 0, "%s", page->items[menu.cursor].desc);
}

/// Put a label on each panel of the page.
static void Layout(void)
{
    const Page* page = &pages[menu.page];
    int i;

    for (i = 0; i < MAX_ITEMS; i++) {
        if (menu.labels[i] != NULL) {
            HSD_SisLib_803A5CC4(menu.labels[i]);
            menu.labels[i] = NULL;
        }
        if (i < page->count) {
            const Item* it = &page->items[i];
            menu.labels[i] =
                NewText(it->x + it->w * 0.5F,
                        it->y + it->h * 0.5F - it->text_size * TEXT_LINE * 0.5F,
                        it->text_size, 1);
        }
    }
    Refresh();
}

/* --- input ---------------------------------------------------------------- */

/// The item nearest to the cursor's in direction (dx, dy), or the cursor.
static int Neighbour(int dx, int dy)
{
    const Page* page = &pages[menu.page];
    const Item* from = &page->items[menu.cursor];
    f32 fx = from->x + from->w * 0.5F, fy = from->y + from->h * 0.5F;
    int best = menu.cursor;
    f32 best_score = 1.0e9F;
    int i;

    for (i = 0; i < page->count; i++) {
        const Item* it = &page->items[i];
        f32 x = it->x + it->w * 0.5F - fx, y = it->y + it->h * 0.5F - fy;
        f32 along = x * dx + y * dy;
        f32 across = x * dy - y * dx;
        f32 score;
        if (i == menu.cursor || along <= 1.0F) {
            continue;
        }
        if (across < 0.0F) {
            across = -across;
        }
        score = along + across * 2.0F;
        if (score < best_score) {
            best_score = score;
            best = i;
        }
    }
    return best;
}

static void SetPage(int page)
{
    menu.page = page;
    menu.cursor = 0;
    Layout();
}

static bool StartEvent(const char* file)
{
    int page, event;

    if (!tmce_ac_FindEvent(file, &page, &event)) {
        return false;
    }
    tmce_ac_SetEventPage(page);
    gm_801BEB74(event);
    gm_801677E8(0);
    gm_ChangeGameModeAfterCurrentScene(GM_EVENT);
    return true;
}

static void Leave(void)
{
    menu.leaving = true;
    gm_801A4B60();
}

static void Confirm(void)
{
    const Item* it = &pages[menu.page].items[menu.cursor];

    switch (it->action) {
    case Act_Train:
        if (StartEvent("course")) {
            Leave();
        }
        break;
    case Act_Lab:
        if (StartEvent("lab")) {
            Leave();
        }
        break;
    case Act_Events:
        gm_SetNextGameModeStateId(TM_MENU_STATE_VANILLA);
        Leave();
        break;
    case Act_Versus:
        gm_ChangeGameModeAfterCurrentScene(GM_VS);
        Leave();
        break;
    case Act_Controls:
        SetPage(Page_Controls);
        break;
    case Act_Back:
        SetPage(Page_Main);
        break;
    default:
        return;
    }
    lbAudioAx_80024030(1);
}

static void Adjust(int by)
{
    const Item* it = &pages[menu.page].items[menu.cursor];

    if (it->action == Act_Delay) {
        int v = tm_ctl.delay + by;
        if (v < 0) {
            v = 0;
        }
        if (v > TM_CTL_MAX_DELAY) {
            v = TM_CTL_MAX_DELAY;
        }
        if (v != tm_ctl.delay) {
            tm_ctl.delay = v;
            lbAudioAx_80024030(2);
            Refresh();
        }
    }
}

void tm_menu_SceneFrame(void)
{
    u32 in;
    int to;

    menu.frame++;
    if (menu.leaving) {
        return;
    }
    in = mn_80229624(4);
    to = menu.cursor;
    if (in & MenuInput_Up) {
        to = Neighbour(0, -1);
    } else if (in & MenuInput_Down) {
        to = Neighbour(0, 1);
    } else if (in & MenuInput_Left) {
        if (pages[menu.page].items[menu.cursor].action == Act_Delay) {
            Adjust(-1);
        } else {
            to = Neighbour(-1, 0);
        }
    } else if (in & MenuInput_Right) {
        if (pages[menu.page].items[menu.cursor].action == Act_Delay) {
            Adjust(1);
        } else {
            to = Neighbour(1, 0);
        }
    }
    if (to != menu.cursor) {
        menu.cursor = to;
        lbAudioAx_80024030(2);
        Refresh();
    }
    if (in & MenuInput_Confirm) {
        Confirm();
    } else if ((in & MenuInput_Back) && menu.page != Page_Main) {
        lbAudioAx_80024030(0);
        SetPage(Page_Main);
    }
}

void tm_menu_SceneEnter(void* data)
{
    HSD_GObj* gobj;
    int i;

    (void) data;
    menu.page = Page_Main;
    menu.cursor = 0;
    menu.frame = 0;
    menu.leaving = false;
    for (i = 0; i < MAX_ITEMS; i++) {
        menu.labels[i] = NULL;
    }

    /* The canvas brings its own camera: everything on its GX link is drawn
       in screen units. The panels go on the same link, before the text. */
    HSD_SisLib_803A611C(0, NULL, 9, 13, 0, TEXT_GX_LINK, 1, 19);
    gobj = GObj_Create(14, 15, 0);
    GObj_SetupGXLink(gobj, Draw, TEXT_GX_LINK, 0);

    menu.title = NewText(24.0F, 30.0F, 0.75F, 0);
    menu.desc = NewText(56.0F, 406.0F, 0.52F, 0);

    Layout();
}
