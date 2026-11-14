/** @file
 * A photo studio in a match: the camera put anywhere, everything but the
 * fighters left undrawn, the screen cleared to one colour. For pictures of
 * a fighter that the game has none of (Sheik has no select-screen portrait:
 * tools/melee_client/art.py draws her one, twice over, on black and on
 * white, and takes the difference for her outline).
 *
 *   studio cam EX EY EZ IX IY IZ FOV   the camera at E looking at I (the
 *                                      game's developer free camera)
 *   studio cam off                     the match camera again
 *   studio bg R G B                    the colour the screen is cleared to
 *   studio solo 1|0                    only the fighters drawn, or all
 *   studio list                        what is drawn: class, kind, link
 *   studio stage                       the stage's blast zones (left right
 *                                      top bottom, as the game's getters
 *                                      give them) and its left ledge (x y),
 *                                      for the stage select's card
 *
 * Only for pictures: nothing here is part of a match's state that rollback
 * or a snapshot keeps, and a match left in the studio stays odd until
 * "studio solo 0" and "studio cam off".
 */
#include "host.h"

#include <stdio.h>
#include <string.h>

#include <melee/cm/camera.h>
#include <melee/cm/types.h>
#include <melee/ft/forward.h>
#include <melee/gr/stage.h>
#include <sysdolphin/baselib/gobj.h>

/// What "solo" took away, to give back.
static struct {
    HSD_GObj* gobj;
    GObj_RenderFunc render;
} hidden[512];
static int hidden_count;

static void draw_nothing(HSD_GObj* gobj, intptr_t pass)
{
    (void) gobj;
    (void) pass;
}

/// Kept: the fighters, and what draws them (cameras, lights, fog).
static bool kept(HSD_GObj* gobj)
{
    return gobj->classifier == HSD_GOBJ_CLASS_FIGHTER ||
           gobj->obj_kind == HSD_GObj_CameraKind ||
           gobj->obj_kind == HSD_GObj_LightKind ||
           gobj->obj_kind == (u8) HSD_GObj_FogKind;
}

static void solo(bool on)
{
    int i;

    for (i = 0; i < hidden_count; i++) {
        hidden[i].gobj->render_cb = hidden[i].render;
    }
    hidden_count = 0;
    if (!on) {
        return;
    }
    for (i = 0; i < HSD_GObjLibInitData.gx_link_max; i++) {
        HSD_GObj* gobj;
        for (gobj = HSD_GObjGXLinkHead[i]; gobj != NULL;
             gobj = gobj->next_gx)
        {
            if (kept(gobj) || gobj->render_cb == NULL ||
                hidden_count == (int) (sizeof hidden / sizeof hidden[0]))
            {
                continue;
            }
            hidden[hidden_count].gobj = gobj;
            hidden[hidden_count].render = gobj->render_cb;
            hidden_count++;
            gobj->render_cb = draw_nothing;
        }
    }
}

/// The reply's text after "@ ": "ok", "ok ..." or "error ...".
const char* host_studio_command(const char* line)
{
    static char reply[4096];
    char what[16] = "";
    int n = 0;

    sscanf(line, "%15s%n", what, &n);
    line += n;
    if (strcmp(what, "cam") == 0) {
        Vec3 eye, at;
        float fov;
        char off[8] = "";
        if (sscanf(line, "%7s", off) == 1 && strcmp(off, "off") == 0) {
            Camera_800300F0();
            return "ok";
        }
        if (sscanf(line, "%f %f %f %f %f %f %f", &eye.x, &eye.y, &eye.z,
                   &at.x, &at.y, &at.z, &fov) != 7)
        {
            return "error studio cam EX EY EZ IX IY IZ FOV | off";
        }
        Camera_8003006C();
        cm_80453004.free_eye_pos = eye;
        cm_80453004.free_int_pos = at;
        cm_80453004.free_fov = fov;
        return "ok";
    }
    if (strcmp(what, "bg") == 0) {
        int r = 0, g = 0, b = 0;
        if (sscanf(line, "%d %d %d", &r, &g, &b) != 3) {
            return "error studio bg R G B";
        }
        Camera_SetBackgroundColor((u8) r, (u8) g, (u8) b);
        return "ok";
    }
    if (strcmp(what, "solo") == 0) {
        int on = 1;
        sscanf(line, "%d", &on);
        solo(on != 0);
        snprintf(reply, sizeof reply, "ok %d", hidden_count);
        return reply;
    }
    if (strcmp(what, "list") == 0) {
        int i, len = snprintf(reply, sizeof reply, "ok");
        for (i = 0; i < HSD_GObjLibInitData.gx_link_max; i++) {
            HSD_GObj* gobj;
            for (gobj = HSD_GObjGXLinkHead[i];
                 gobj != NULL && len < (int) sizeof reply - 40;
                 gobj = gobj->next_gx)
            {
                len += snprintf(reply + len, sizeof reply - len,
                                " %d:%d:%d%s", i, gobj->classifier,
                                gobj->obj_kind, kept(gobj) ? "+" : "");
            }
        }
        return reply;
    }
    if (strcmp(what, "stage") == 0) {
        float x, y;
        if (host_left_ledge(&x, &y) < 0) {
            return "error no ledge found";
        }
        snprintf(reply, sizeof reply, "ok %.9g %.9g %.9g %.9g %.9g %.9g",
                 Stage_GetBlastZoneLeftOffset(),
                 Stage_GetBlastZoneRightOffset(),
                 Stage_GetBlastZoneTopOffset(),
                 Stage_GetBlastZoneBottomOffset(), x, y);
        return reply;
    }
    return "error studio cam|bg|solo|list|stage";
}
