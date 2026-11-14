/** @file
 * The input display (the owner, 2026-11-13: "a gamecube controller overlay
 * that shows inputs ... TM-CE has this already so let's reuse it"; then,
 * 2026-11-14: "use the official button icons so it looks more like an
 * actual gamecube controller"). A controller per shown port, at the top
 * right of the game's picture, its sticks and triggers moving and its
 * buttons lit while held, from what the fighter read this frame (its
 * input record, after the input delay; a CPU's too): src/lab.c's
 * Inputs_Init and Inputs_Think, rewritten against the decomp.
 *
 * Drawn by the client's interface where its match screens have the
 * display (screens.pad_display: SmashWiki's icons as a controller): the
 * match's frame leaves each controller's pad in `pads`, and as the window's
 * frame ends host_inputs_ui gives them to the interface (ui.cpp,
 * host_ui_pad). Elsewhere (no client: tools/melee_native/play.py), TM-CE's
 * own model from its lab.dat (put on the disc as files/TM/lab.dat by
 * tools/tmce_disc.py, never in this repository), drawn by the match's HUD
 * camera.
 *
 *   inputs MASK    the ports shown: bit 0 port 1, bit 1 port 2 (0: none)
 *
 * The display is a GObj of the match: made at the first frame boundary
 * that has a match and a mask, gone with the match's scene. Everything it
 * needs is in it (its user data), so a state loaded from before it was
 * made, or from another time it was there, leaves nothing dangling: each
 * frame it is looked for among the match's GObjs, and made again if it is
 * missing. Only the mask, the player's choice, and what the interface was
 * last given are kept here.
 */
#include <stdio.h>
#include <string.h>

#include "host.h"
#include "melee_dat.h"
#include <dat/reader-internal.h>
#include <dolphin/dvd.h>
#include <dolphin/pad.h>
#include <melee/ft/fighter.h>
#include <melee/ft/inlines.h>
#include <melee/ft/kinds/ftCommon/ftCo_0A01.h>
#include <melee/ft/types.h>
#include <melee/gm/types.h>
#include <melee/lb/lbarchive.h>
#include <melee/lb/lbspdisplay.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/archive.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/dobj.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjgxlink.h>
#include <sysdolphin/baselib/gobjobject.h>
#include <sysdolphin/baselib/gobjplink.h>
#include <sysdolphin/baselib/gobjproc.h>
#include <sysdolphin/baselib/gobjuserdata.h>
#include <sysdolphin/baselib/jobj.h>
#include <sysdolphin/baselib/memory.h>
#include <sysdolphin/baselib/mobj.h>

/// The controller's model: lab.dat's public "lab" is TM-CE's Arch_LabData
/// (lab_common.h), the controller its fifth pointer. The native build turns
/// a symbol into native data by its type, and lab.dat is not one of the
/// game's files it knows: the pointer is read from the raw data and what it
/// points to converted as the HSD_Joint it is.
static HSD_Joint* controller_joint(void)
{
    HSD_Archive* arc = lbArchive_LoadArchive("TM/lab.dat");
    const DatSymbol* sym;
    const uint8_t* p;
    uint32_t at;
    int32_t type;

    if (arc == NULL || arc->native_data == NULL) {
        return NULL;
    }
    sym = dat_archive_public(arc->native_data->archive, "lab");
    if (sym == NULL) {
        return NULL;
    }
    p = dat_raw(arc->native_data, sym->offset + 4 * 4);
    at = (uint32_t) p[0] << 24 | (uint32_t) p[1] << 16 | (uint32_t) p[2] << 8 |
         p[3];
    type = melee_dat_type("HSD_Joint");
    if (type < 0) {
        return NULL;
    }
    return dat_at(arc->native_data, at, type, DAT_COUNT_ONE, 1);
}

/// TM-CE's tables (lab_common.h): each button's joint and DObj in the
/// controller, its colour at rest, its bit.
static const struct {
    u8 jobj, dobj;
    GXColor color;
    u32 bit;
} buttons[] = {
    { 1, 0, { 50, 180, 50, 255 }, PAD_BUTTON_A },
    { 2, 0, { 255, 50, 50, 255 }, PAD_BUTTON_B },
    { 3, 0, { 127, 127, 127, 255 }, PAD_BUTTON_X },
    { 4, 0, { 127, 127, 127, 255 }, PAD_BUTTON_Y },
    { 5, 0, { 192, 192, 192, 255 }, PAD_BUTTON_START },
    { 6, 1, { 192, 192, 192, 255 }, PAD_BUTTON_UP },
    { 6, 2, { 192, 192, 192, 255 }, PAD_BUTTON_RIGHT },
    { 6, 3, { 192, 192, 192, 255 }, PAD_BUTTON_LEFT },
    { 6, 4, { 192, 192, 192, 255 }, PAD_BUTTON_DOWN },
    { 11, 0, { 127, 127, 127, 255 }, PAD_TRIGGER_L },
    { 12, 0, { 127, 127, 127, 255 }, PAD_TRIGGER_R },
    { 13, 0, { 0, 0, 255, 255 }, PAD_TRIGGER_Z },
};
enum {
    BUTTON_L = 9,
    BUTTON_R = 10
};
#define JOINT_CSTICK 8
#define JOINT_LSTICK 10
/* TM-CE draws it on link 12, which its lab has a camera draw; the native
   build's match has no camera on 12 (its cameras' links, listed: 3, 4, 8,
   9, 10, 11, 15, 16, 17). Link 11 is the HUD's, drawn by the camera of
   the damage and stock display, in the same screen space. */
#define INPUT_GXLINK 11
#define INPUT_GXPRI 80
static const GXColor pressed = { 255, 255, 255, 255 };
/// TM-CE's places for the first and second controller shown
static const Vec2 places[2] = { { 13.0F, 20.0F }, { 23.0F, 20.0F } };

/// The display's user data: a controller per port with a fighter.
typedef struct Display {
    struct {
        HSD_JObj* jobj;
        Vec2 ltrig, rtrig; /* where the triggers rest */
    } ctl[4];
} Display;

static int mask; /* the player's choice: not the game's state */

static HSD_JObj* child(HSD_JObj* root, int index)
{
    HSD_JObj* out = NULL;
    lb_80011E24(root, &out, index, -1);
    return out;
}

static HSD_DObj* nth_dobj(HSD_JObj* jobj, int n)
{
    HSD_DObj* d = jobj->u.dobj;
    while (n-- > 0 && d != NULL) {
        d = d->next;
    }
    return d;
}

static bool shown(int port)
{
    HSD_GObj* fighter = Player_GetEntity(port);
    return (mask & (1 << port)) && fighter != NULL &&
           GET_FIGHTER(fighter) != NULL;
}

/// What the interface's input display shows (host_inputs_ui), set by
/// think() as the match's frame runs, cleared when the display goes: the
/// controllers shown, in their ports' order.
static struct {
    int on;
    int port;
    u32 held;
    float sx, sy, cx, cy, ltrig, rtrig;
} pads[2];
/// The interface draws the display (the client's match screens have it:
/// screens.pad_display); TM-CE's model is then hidden.
static int ui_draws;

static void hide(HSD_JObj* jobj)
{
    /* TM-CE hides it far behind the camera: the hidden flag did not work
       for it */
    jobj->translate.z = -99999.0F;
    HSD_JObjSetMtxDirtySub(jobj);
}

/// Inputs_Think: each controller follows its fighter's inputs. Those shown
/// fill TM-CE's places from the right: one alone is at the corner.
static void think(HSD_GObj* gobj)
{
    Display* d = gobj->user_data;
    int count = 0, k = 0;

    for (int port = 0; port < 4; port++) {
        count += shown(port);
    }
    if (count > 2) {
        count = 2; /* TM-CE's two places */
    }
    pads[0].on = pads[1].on = 0;
    for (int port = 0; port < 4; port++) {
        HSD_JObj* jobj = d->ctl[port].jobj;
        Fighter* fp;
        float ltrig, rtrig;
        u32 held;

        if (!shown(port) || k >= 2) {
            if (jobj != NULL) {
                hide(jobj);
            }
            continue;
        }
        fp = GET_FIGHTER(Player_GetEntity(port));
        /* the buttons as pressed: the fighter's own record has A and a
           light press of the triggers added while Z is held (fighter.c:
           Z grabs), which a display of the controller must not show */
        if (ftCo_IsCpuControlled(fp)) {
            held = ftCo_GetCpuButtons(fp);
        } else {
            held = HSD_PadGameStatus[fp->pad_port].button;
        }
        if (Player_GetPlayerSlotType(port) == Gm_PKind_Human) {
            /* the pad the fighters read (fighter.c's triggers) */
            ltrig = HSD_PadGameStatus[port].nml_analogL;
            rtrig = HSD_PadGameStatus[port].nml_analogR;
        } else if ((held & PAD_TRIGGER_Z) &&
                   !(held & (PAD_TRIGGER_L | PAD_TRIGGER_R)))
        {
            ltrig = rtrig = 0.0F; /* Z's light press, not the triggers */
        } else {
            ltrig = rtrig = fp->input.triggers[0];
        }
        pads[k].on = 1;
        pads[k].port = port;
        pads[k].held = held;
        pads[k].sx = fp->input.lstick[0].x;
        pads[k].sy = fp->input.lstick[0].y;
        pads[k].cx = fp->input.cstick[0].x;
        pads[k].cy = fp->input.cstick[0].y;
        /* a click all the way in is all the way in */
        pads[k].ltrig = (held & PAD_TRIGGER_L) ? 1.0F : ltrig;
        pads[k].rtrig = (held & PAD_TRIGGER_R) ? 1.0F : rtrig;
        if (jobj == NULL || ui_draws) {
            if (jobj != NULL) {
                hide(jobj);
            }
            k++;
            continue;
        }
        jobj->translate.x = places[2 - count + k].x;
        jobj->translate.y = places[2 - count + k].y;
        jobj->translate.z = 0.0F;
        k++;
        {
            HSD_JObj* j = child(jobj, JOINT_LSTICK);
            j->translate.x = fp->input.lstick[0].x * 2.3F;
            j->translate.y = fp->input.lstick[0].y * 2.3F;
            j = child(jobj, JOINT_CSTICK);
            j->translate.x = fp->input.cstick[0].x * 2.3F;
            j->translate.y = fp->input.cstick[0].y * 2.3F;
            j = child(jobj, buttons[BUTTON_L].jobj);
            j->translate.x = ltrig * 0.5F + d->ctl[port].ltrig.x;
            j->translate.z = ltrig * 1.5F + d->ctl[port].ltrig.y;
            j = child(jobj, buttons[BUTTON_R].jobj);
            j->translate.x = rtrig * -0.5F + d->ctl[port].rtrig.x;
            j->translate.z = rtrig * 1.5F + d->ctl[port].rtrig.y;
        }
        for (size_t i = 0; i < sizeof buttons / sizeof buttons[0]; i++) {
            HSD_DObj* d =
                nth_dobj(child(jobj, buttons[i].jobj), buttons[i].dobj);
            if (d != NULL && d->mobj != NULL && d->mobj->mat != NULL) {
                d->mobj->mat->diffuse = (held & buttons[i].bit)
                                            ? pressed
                                            : buttons[i].color;
            }
        }
        HSD_JObjSetMtxDirtySub(jobj);
    }
}

/// Its user data's remove function, which also marks it as the display.
static void gone(void* data)
{
    HSD_Free(data);
    pads[0].on = pads[1].on = 0;
}

/// The display among the match's GObjs, the first if a load brought back
/// more than one (the others are freed); NULL if there is none.
static HSD_GObj* find(void)
{
    HSD_GObj* found = NULL;
    HSD_GObj* g = HSD_GObjPLinkHead[0];
    while (g != NULL) {
        HSD_GObj* next = g->next;
        if (g->user_data_remove_func == gone) {
            if (found == NULL) {
                found = g;
            } else {
                HSD_GObjFree(g);
            }
        }
        g = next;
    }
    return found;
}

/// Inputs_Init: a controller from lab.dat for each fighter, under a root
/// drawn on the HUD camera's link.
static void make(void)
{
    static HSD_Joint root_desc;
    HSD_Joint* model;
    HSD_JObj* root;
    HSD_GObj* gobj;
    Display* d;
    int made = 0;

    if (DVDConvertPathToEntrynum("TM/lab.dat") < 0) {
        /* the client has not copied TM-CE's art: the interface's display
           alone (host_inputs_ui) */
        model = NULL;
    } else {
        model = controller_joint();
        if (model == NULL) {
            host_log("inputs: lab.dat has no controller");
        }
    }
    root_desc.flags = JOBJ_ROOT_XLU | JOBJ_ROOT_TEXEDGE;
    root_desc.scale.x = root_desc.scale.y = root_desc.scale.z = 1.0F;
    root = HSD_JObjLoadJoint(&root_desc);
    d = HSD_MemAlloc(sizeof *d);
    memset(d, 0, sizeof *d);
    for (int port = 0; port < 4; port++) {
        HSD_JObj* jobj;
        HSD_JObj* t;
        if (model == NULL || Player_GetEntity(port) == NULL) {
            continue;
        }
        jobj = HSD_JObjLoadJoint(model);
        jobj->translate.z = -99999.0F; /* placed by think() */
        HSD_JObjAddChild(root, jobj);
        d->ctl[port].jobj = jobj;
        t = child(jobj, buttons[BUTTON_L].jobj);
        d->ctl[port].ltrig.x = t->translate.x;
        d->ctl[port].ltrig.y = t->translate.z;
        t = child(jobj, buttons[BUTTON_R].jobj);
        d->ctl[port].rtrig.x = t->translate.x;
        d->ctl[port].rtrig.y = t->translate.z;
        made++;
    }
    gobj = GObj_Create(0, 0, 0);
    GObj_InitUserData(gobj, 4, gone, d);
    HSD_GObj_SetupProc(gobj, (HSD_GObjEvent) think, 4);
    HSD_GObjObject_80390A70(gobj, HSD_GObj_JObjKind, root);
    GObj_SetupGXLink(gobj, HSD_GObj_JObjCallback, INPUT_GXLINK, INPUT_GXPRI);
    think(gobj);
    host_log("inputs: %d controller(s)", made);
}

/// At each frame boundary: the display made if it is wanted, the match is
/// on and it is not there yet.
void host_inputs_frame(void)
{
    if (mask != 0 && Player_GetEntity(0) != NULL && find() == NULL) {
        make();
    }
}

const char* host_inputs_command(const char* line)
{
    int m = 0;
    while (*line == ' ') {
        line++;
    }
    if (sscanf(line, "%d", &m) != 1 || m < 0 || m > 15) {
        return "error inputs MASK: 0..15, bit 0 port 1";
    }
    mask = m;
    if (mask == 0) {
        pads[0].on = pads[1].on = 0;
    }
    host_inputs_frame();
    return "ok";
}

#ifdef HOST_WINDOW
/// As the window's frame ends, before the interface is drawn: the
/// interface's display given what the match's frame left in `pads`
/// (ui.cpp, host_ui_pad). Whether the document shown has the display
/// decides, for the next frame, whether TM-CE's model is drawn instead.
void host_inputs_ui(void)
{
    int has = 0;
    for (int k = 0; k < 2; k++) {
        has |= host_ui_pad(k, mask != 0 && pads[k].on, pads[k].port,
                           pads[k].held, pads[k].sx, pads[k].sy, pads[k].cx,
                           pads[k].cy, pads[k].ltrig, pads[k].rtrig);
    }
    ui_draws = has;
}
#endif
