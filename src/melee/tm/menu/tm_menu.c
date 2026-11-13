#include "tm_menu.h"

#include "../controls/controls.h"
#include "../ucf/ucf.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#include <dolphin/gx.h>
#include <dolphin/mtx.h>
#include <melee/gm/gm_1601.h>
#include <melee/gm/gm_1A3F.h>
#include <melee/gm/gmmain_lib.h>
#include <melee/gm/gmscene.h>
#include <melee/gm/types.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/lb/lbcardgame.h>
#include <melee/lb/lbcardnew.h>
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
/// Height of a line of text at size 1.0, in screen units (measured).
#define TEXT_LINE 36.0F

/// What an item does. Items with a value show it after their label; A (or
/// R) moves to the next value and L to the previous one.
typedef enum Action {
    Act_None,
    Act_Train,
    Act_Lab,
    Act_Events,
    Act_Controls,
    Act_Names,
    Act_Back,
    Act_Delay,   ///< value: frames of input delay
    Act_Layout,  ///< value: the layout being edited
    Act_Port,    ///< value: the layout port `arg` plays with
    Act_Bind,    ///< value: what input `arg` does in the layout being edited
    Act_Name,    ///< value: the layout nickname row `arg` carries
    Act_Ucf,     ///< value (fixed): whose UCF is running
    Act_Count
} Action;

typedef struct Item {
    const char* label;
    const char* desc;
    s16 x, y, w, h; ///< the panel, in screen units
    u8 action;
    u8 colour; ///< index into #palette
    u8 arg;
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
      190, Act_Train, 0, 0, 1.35F },
    { "Lab", "Free practice with any character and situation.", 386, 84, 214,
      90, Act_Lab, 1, 0, 0.9F },
    { "Events", "Training Mode's own events, page by page.", 386, 184, 214,
      90, Act_Events, 1, 0, 0.9F },
    { "Controls", "Input delay and button layouts.", 40, 290, 560, 92,
      Act_Controls, 3, 0, 0.9F },
};

#define ROW_H 24
#define ROW_STEP 27
#define ROW(n) (78 + (n) * ROW_STEP)
#define ROW_TEXT 0.5F
#define LEFT_X 36
#define LEFT_W 272
#define RIGHT_X 332
#define RIGHT_W 272

/// Shown at the top right of a page whose items have values.
#define VALUE_HINT "A or R: next   L: previous   B: back"

/// Left: settings and who uses which layout. Right: the buttons of the
/// layout being edited.
static const Item controls_items[] = {
    { "Input delay", "Frames each pad is held back in a match.",
      LEFT_X, ROW(0), LEFT_W, ROW_H, Act_Delay, 3, 0, ROW_TEXT },
    { "Port 1", "The layout port 1 plays with.", LEFT_X, ROW(2),
      LEFT_W, ROW_H, Act_Port, 3, 0, ROW_TEXT },
    { "Port 2", "The layout port 2 plays with.", LEFT_X, ROW(3),
      LEFT_W, ROW_H, Act_Port, 3, 1, ROW_TEXT },
    { "Port 3", "The layout port 3 plays with.", LEFT_X, ROW(4),
      LEFT_W, ROW_H, Act_Port, 3, 2, ROW_TEXT },
    { "Port 4", "The layout port 4 plays with.", LEFT_X, ROW(5),
      LEFT_W, ROW_H, Act_Port, 3, 3, ROW_TEXT },
    { "Nicknames", "Give a nickname its own layout.", LEFT_X, ROW(7), LEFT_W,
      ROW_H, Act_Names, 1, 0, ROW_TEXT },
    { "UCF 0.84", "Universal Controller Fix: always on. Slippi brings its own.",
      LEFT_X, ROW(8), LEFT_W, ROW_H, Act_Ucf, 3, 0, ROW_TEXT },
    { "Back", "Return to the main menu.", LEFT_X, ROW(10), LEFT_W, ROW_H,
      Act_Back, 3, 0, ROW_TEXT },
    { "Edit", "The layout the buttons on this side belong to.",
      RIGHT_X, ROW(0), RIGHT_W, ROW_H, Act_Layout, 0, 0, ROW_TEXT },
    { "A", "What A does.", RIGHT_X, ROW(1), RIGHT_W, ROW_H,
      Act_Bind, 3, TmCtlIn_A, ROW_TEXT },
    { "B", "What B does.", RIGHT_X, ROW(2), RIGHT_W, ROW_H,
      Act_Bind, 3, TmCtlIn_B, ROW_TEXT },
    { "X", "What X does.", RIGHT_X, ROW(3), RIGHT_W, ROW_H,
      Act_Bind, 3, TmCtlIn_X, ROW_TEXT },
    { "Y", "What Y does.", RIGHT_X, ROW(4), RIGHT_W, ROW_H,
      Act_Bind, 3, TmCtlIn_Y, ROW_TEXT },
    { "Z", "What Z does.", RIGHT_X, ROW(5), RIGHT_W, ROW_H,
      Act_Bind, 3, TmCtlIn_Z, ROW_TEXT },
    { "L", "What L does.", RIGHT_X, ROW(6), RIGHT_W, ROW_H,
      Act_Bind, 3, TmCtlIn_L, ROW_TEXT },
    { "R", "What R does.", RIGHT_X, ROW(7), RIGHT_W, ROW_H,
      Act_Bind, 3, TmCtlIn_R, ROW_TEXT },
    { "D-pad up", "What up on the D-pad does.", RIGHT_X, ROW(8),
      RIGHT_W, ROW_H, Act_Bind, 3, TmCtlIn_DpadUp, ROW_TEXT },
    { "D-pad down", "What down on the D-pad does.", RIGHT_X,
      ROW(9), RIGHT_W, ROW_H, Act_Bind, 3, TmCtlIn_DpadDown, ROW_TEXT },
    { "D-pad left", "What left on the D-pad does.", RIGHT_X,
      ROW(10), RIGHT_W, ROW_H, Act_Bind, 3, TmCtlIn_DpadLeft, ROW_TEXT },
    { "D-pad right", "What right on the D-pad does.", RIGHT_X,
      ROW(11), RIGHT_W, ROW_H, Act_Bind, 3, TmCtlIn_DpadRight, ROW_TEXT },
};

#define NAME_ROWS 10

/// One row per nickname the game has stored; rows without one are hidden.
static const Item names_items[] = {
    { "", "The layout this nickname plays with.", 120, ROW(0),
      400, ROW_H, Act_Name, 3, 0, ROW_TEXT },
    { "", "The layout this nickname plays with.", 120, ROW(1),
      400, ROW_H, Act_Name, 3, 1, ROW_TEXT },
    { "", "The layout this nickname plays with.", 120, ROW(2),
      400, ROW_H, Act_Name, 3, 2, ROW_TEXT },
    { "", "The layout this nickname plays with.", 120, ROW(3),
      400, ROW_H, Act_Name, 3, 3, ROW_TEXT },
    { "", "The layout this nickname plays with.", 120, ROW(4),
      400, ROW_H, Act_Name, 3, 4, ROW_TEXT },
    { "", "The layout this nickname plays with.", 120, ROW(5),
      400, ROW_H, Act_Name, 3, 5, ROW_TEXT },
    { "", "The layout this nickname plays with.", 120, ROW(6),
      400, ROW_H, Act_Name, 3, 6, ROW_TEXT },
    { "", "The layout this nickname plays with.", 120, ROW(7),
      400, ROW_H, Act_Name, 3, 7, ROW_TEXT },
    { "", "The layout this nickname plays with.", 120, ROW(8),
      400, ROW_H, Act_Name, 3, 8, ROW_TEXT },
    { "", "The layout this nickname plays with.", 120, ROW(9),
      400, ROW_H, Act_Name, 3, 9, ROW_TEXT },
    { "Back", "Return to the controls.", 120, ROW(11), 400, ROW_H,
      Act_Controls, 3, 0, ROW_TEXT },
};

enum { Page_Main, Page_Controls, Page_Names, Page_Count };

static const Page pages[Page_Count] = {
    { "Main Menu", main_items, sizeof(main_items) / sizeof(main_items[0]) },
    { "Controls", controls_items,
      sizeof(controls_items) / sizeof(controls_items[0]) },
    { "Nicknames", names_items,
      sizeof(names_items) / sizeof(names_items[0]) },
};

#define MAX_ITEMS 20

static const char* const action_names[TmCtlAct_Count] = {
    "Nothing", "Attack", "Special", "Jump", "Shield", "Grab", "Taunt",
};

static struct {
    int page;
    int cursor;
    int frame;   ///< frames since the scene began, for the highlight's pulse
    int leaving; ///< an action was taken: ignore input until the scene ends
    int layout;  ///< the layout the Controls page edits
    /// Nicknames page: the game's name slot shown in each row, -1 for none.
    s8 name_slot[NAME_ROWS];
    int name_scroll;
    HSD_Text* labels[MAX_ITEMS];
    HSD_Text* title;
    HSD_Text* hint;
    HSD_Text* desc;
} menu;

static bool Hidden(const Item* it)
{
    return it->action == Act_Name && menu.name_slot[it->arg] < 0;
}

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
    RoundRect(20.0F, 408.0F, 600.0F, 32.0F, 12.0F, &bar_colour);

    for (i = 0; i < page->count; i++) {
        const Item* it = &page->items[i];
        GXColor fill;
        f32 x = it->x, y = it->y, w = it->w, h = it->h;
        f32 r = h * 0.28F;
        f32 grow = h > 40.0F ? 4.0F : 2.0F;
        bool selected = i == menu.cursor;

        if (Hidden(it)) {
            continue;
        }
        if (selected) {
            /* The highlighted panel grows a little and its edge pulses. */
            f32 pulse = 0.5F + 0.5F * sinf(menu.frame * 0.12F);
            GXColor edge;
            Shade(&edge, &edge_light, 0.75F + 0.25F * pulse);
            x -= grow;
            y -= grow;
            w += grow * 2.0F;
            h += grow * 2.0F;
            RoundRect(x - grow, y - grow, w + grow * 2.0F, h + grow * 2.0F,
                      r + grow, &edge);
            Shade(&fill, &palette[it->colour], 1.12F);
        } else {
            RoundRect(x - 2.0F, y - 2.0F, w + 4.0F, h + 4.0F, r + 2.0F,
                      &edge_dark);
            Shade(&fill, &palette[it->colour], 0.82F);
        }
        RoundRect(x, y, w, h, r, &fill);
        /* A lighter band across the top third gives the panel some depth. */
        if (it->h > 40) {
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

/// The name a layout goes by: its own, or what it will be called once a
/// button in it is changed.
static void LayoutName(int index, char* out)
{
    const TmCtlProfile* p = &tm_ctl.profiles[index];

    if (p->used && p->name[0] != '\0') {
        sprintf(out, "%s", p->name);
    } else {
        sprintf(out, "Layout %d (new)", index);
    }
}

/// An item's value as text; false if it has none.
static bool ValueText(const Item* it, char* out)
{
    switch (it->action) {
    case Act_Delay:
        sprintf(out, "%d frame%s", tm_ctl.delay, tm_ctl.delay == 1 ? "" : "s");
        return true;
    case Act_Layout:
        LayoutName(menu.layout, out);
        return true;
    case Act_Port:
        LayoutName(tm_ctl.port_profile[it->arg], out);
        return true;
    case Act_Bind:
        sprintf(out, "%s",
                action_names[tm_ctl.profiles[menu.layout].map[it->arg]]);
        return true;
    case Act_Ucf:
        sprintf(out, "%s", tm_ucf_Active() ? "built in" : "Slippi's");
        return true;
    case Act_Name:
        if (tm_ctl.name_profile[menu.name_slot[it->arg]] == 0) {
            sprintf(out, "its port's layout");
        } else {
            LayoutName(tm_ctl.name_profile[menu.name_slot[it->arg]], out);
        }
        return true;
    default:
        return false;
    }
}

static void Refresh(void)
{
    const Page* page = &pages[menu.page];
    char value[40];
    char name[12];
    int i;

    HSD_SisLib_803A70A0(menu.title, 0, "%s", page->title);
    HSD_SisLib_803A70A0(menu.hint, 0, "%s",
                        menu.page == Page_Main ? "A: choose" : VALUE_HINT);
    for (i = 0; i < page->count; i++) {
        const Item* it = &page->items[i];
        const char* label = it->label;

        if (Hidden(it)) {
            HSD_SisLib_803A70A0(menu.labels[i], 0, " ");
            continue;
        }
        if (it->action == Act_Name) {
            /* The game stores a nickname as up to four two-byte characters. */
            memcpy(name, GetPersistentNameData(menu.name_slot[it->arg])->namedata,
                   8);
            name[8] = '\0';
            label = name;
        }
        if (ValueText(it, value)) {
            HSD_SisLib_803A70A0(menu.labels[i], 0, "%s:  %s", label, value);
        } else {
            HSD_SisLib_803A70A0(menu.labels[i], 0, "%s", label);
        }
        HSD_SisLib_803A74F0(menu.labels[i], 0,
                            (GXColor*) (i == menu.cursor ? &text_white
                                                         : &text_dim));
    }
    if (menu.page == Page_Names && menu.name_slot[0] < 0) {
        HSD_SisLib_803A70A0(menu.desc, 0,
                            "No nicknames yet: make one on a character "
                            "select screen.");
    } else {
        HSD_SisLib_803A70A0(menu.desc, 0, "%s",
                            page->items[menu.cursor].desc);
    }
}

/// Put a label on each panel of the page: centred on a large panel, at the
/// left of a row.
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
            f32 y = it->y + it->h * 0.5F - it->text_size * TEXT_LINE * 0.5F;
            if (it->h > 40) {
                menu.labels[i] =
                    NewText(it->x + it->w * 0.5F, y, it->text_size, 1);
            } else {
                menu.labels[i] = NewText(it->x + 12.0F, y, it->text_size, 0);
            }
        }
    }
    Refresh();
}

/* --- nicknames ------------------------------------------------------------ */

/// Fill the rows of the Nicknames page from the game's name list, skipping
/// `menu.name_scroll` names. Returns how many names there are.
static int FillNames(void)
{
    int slot, seen = 0, row = 0;

    for (row = 0; row < NAME_ROWS; row++) {
        menu.name_slot[row] = -1;
    }
    row = 0;
    for (slot = 0; slot < TM_CTL_NAMETAG_COUNT; slot++) {
        if (GetPersistentNameData(slot)->namedata[0] == '\0') {
            continue;
        }
        if (seen >= menu.name_scroll && row < NAME_ROWS) {
            menu.name_slot[row++] = slot;
        }
        seen++;
    }
    return seen;
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
        if (i == menu.cursor || along <= 1.0F || Hidden(it)) {
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
    /* Leaving a page is when its changes go to the memory card. The game
       writes them in the background and shows its own notice. */
    if (tm_ctl_Store()) {
        lbCardGame_SaveChanges();
    }
    menu.page = page;
    menu.cursor = 0;
    if (page == Page_Names) {
        menu.name_scroll = 0;
        if (FillNames() == 0) {
            menu.cursor = NAME_ROWS; /* only Back is there */
        }
    }
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

/// The next layout in use after `from`, going `by` (the standard one, 0,
/// always is).
static int NextUsed(int from, int by)
{
    int i = from;
    do {
        i = (i + by + TM_CTL_PROFILE_COUNT) % TM_CTL_PROFILE_COUNT;
    } while (!tm_ctl.profiles[i].used && i != from);
    return i;
}

/// Move an item's value `by` steps. Returns false if it has none or may
/// not change.
static bool Adjust(const Item* it, int by)
{
    switch (it->action) {
    case Act_Delay:
        tm_ctl.delay = (tm_ctl.delay + by + TM_CTL_MAX_DELAY + 1) %
                       (TM_CTL_MAX_DELAY + 1);
        return true;
    case Act_Layout:
        menu.layout = (menu.layout + by + TM_CTL_PROFILE_COUNT) %
                      TM_CTL_PROFILE_COUNT;
        return true;
    case Act_Port:
        tm_ctl.port_profile[it->arg] =
            NextUsed(tm_ctl.port_profile[it->arg], by);
        return true;
    case Act_Bind: {
        TmCtlProfile* p = &tm_ctl.profiles[menu.layout];
        char name[TM_CTL_NAME_LEN + 4];
        if (menu.layout == 0) {
            return false; /* the standard layout stays as it is */
        }
        if (!p->used) {
            sprintf(name, "Layout %d", menu.layout);
            tm_ctl_ResetProfile(menu.layout, name);
        }
        p->map[it->arg] = (p->map[it->arg] + by + TmCtlAct_Count) %
                          TmCtlAct_Count;
        return true;
    }
    case Act_Name: {
        int slot = menu.name_slot[it->arg];
        tm_ctl.name_profile[slot] = NextUsed(tm_ctl.name_profile[slot], by);
        return true;
    }
    default:
        return false;
    }
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
    case Act_Controls:
        SetPage(Page_Controls);
        break;
    case Act_Names:
        SetPage(Page_Names);
        break;
    case Act_Back:
        SetPage(Page_Main);
        break;
    default:
        if (Adjust(it, 1)) {
            lbAudioAx_80024030(2);
            Refresh();
        } else {
            lbAudioAx_80024030(0);
        }
        return;
    }
    lbAudioAx_80024030(1);
}

void tm_menu_SceneFrame(void)
{
    const Item* it;
    u32 in;
    int to;

    menu.frame++;
    if (menu.leaving) {
        return;
    }
    in = mn_80229624(4);
    it = &pages[menu.page].items[menu.cursor];
    to = menu.cursor;
    if (in & MenuInput_Up) {
        to = Neighbour(0, -1);
        if (to == menu.cursor && menu.page == Page_Names &&
            menu.name_scroll > 0)
        {
            menu.name_scroll--;
            FillNames();
            Refresh();
        }
    } else if (in & MenuInput_Down) {
        if (menu.page == Page_Names && it->action == Act_Name &&
            (it->arg == NAME_ROWS - 1) &&
            FillNames() > menu.name_scroll + NAME_ROWS)
        {
            menu.name_scroll++;
            FillNames();
            Refresh();
        } else {
            to = Neighbour(0, 1);
        }
    } else if (in & MenuInput_Left) {
        to = Neighbour(-1, 0);
    } else if (in & MenuInput_Right) {
        to = Neighbour(1, 0);
    }
    if (to != menu.cursor) {
        menu.cursor = to;
        lbAudioAx_80024030(2);
        Refresh();
    }
    if (in & MenuInput_Confirm) {
        Confirm();
    } else if (in & (MenuInput_RTrigger | MenuInput_LTrigger)) {
        if (Adjust(it, (in & MenuInput_RTrigger) ? 1 : -1)) {
            lbAudioAx_80024030(2);
            Refresh();
        }
    } else if ((in & MenuInput_Back) && menu.page != Page_Main) {
        lbAudioAx_80024030(0);
        SetPage(menu.page == Page_Names ? Page_Controls : Page_Main);
    }
}

void tm_menu_SceneEnter(void* data)
{
    HSD_GObj* gobj;
    int i;

    (void) data;
    /* Saving on, as every vanilla scene that saves does it: the work area
       for card operations and the "now saving" notice's art. */
    lbCardNew_AllocWorkArea();
    lbCardGame_LoadArchive(0);
    tm_ctl_Load();

    menu.page = Page_Main;
    menu.cursor = 0;
    menu.frame = 0;
    menu.leaving = false;
    menu.layout = 1;
    for (i = 0; i < MAX_ITEMS; i++) {
        menu.labels[i] = NULL;
    }

    /* The canvas brings its own camera: everything on its GX link is drawn
       in screen units. The panels go on the same link, before the text. */
    HSD_SisLib_803A611C(0, NULL, 9, 13, 0, TEXT_GX_LINK, 1, 19);
    gobj = GObj_Create(14, 15, 0);
    GObj_SetupGXLink(gobj, Draw, TEXT_GX_LINK, 0);

    menu.title = NewText(24.0F, 30.0F, 0.75F, 0);
    menu.hint = NewText(616.0F, 40.0F, 0.42F, 2);
    menu.desc = NewText(34.0F, 415.0F, 0.47F, 0);

    Layout();
}
