/** @file
 * The game's past pictures, for the client's coach (tools/melee_client):
 * what a try looked like, played again in the coach's card next to what it
 * should have looked like (the owner, 2026-11-14: "doesn't seem we have a
 * robust animation system ... Need to ensure this is generic and works
 * across the board"). Whatever the drill, its pictures are the game's own.
 *
 * Each frame drawn, while a ring is recording, the part of the picture
 * where the fighters are is copied out of the game's frame buffer
 * (GXCopyTex). Aurora keeps each copy as a texture on the GPU under the
 * address it was "copied to"; nothing is written there. The addresses are
 * this file's: a ring is SLOTS of them, reused in turn, so a ring holds the
 * last SLOTS frames. RmlUi draws one where a document says "gxcopy://VIEW"
 * (tools/aurora32's second patch). Copies to these addresses keep one size
 * at any window size (aurora_set_copy_exact): 1 MB each, 480 MB for both
 * rings full.
 *
 * The part copied follows the fighters as a camera would (follow): it takes
 * them all in with room round them (above their heads most), wide enough
 * for the 16:9 panels to show them from the middle of its 4:3, and no closer
 * than about three times the game's own view; it widens at once and narrows
 * slowly. At first the whole picture was copied, at 480x360, and the panels
 * showed a part of it enlarged: "Looks like 240p resolution!" (the owner,
 * 2026-11-14). Now a part a third of the picture across is copied at about
 * the window's own resolution.
 *
 *   frames rec RING [M]    copy each frame drawn into ring RING (0 or 1),
 *                          following the fighters of the ports in mask M
 *                          (bit 0 port 1; all if not given); -1: none. The
 *                          reply: the frame number now
 *   frames clear RING      forget a ring's pictures
 *   frames range RING      "LO HI": the oldest and newest frames kept, or
 *                          "-1 -1"
 *   frames view V RING F   RmlUi's view V shows ring RING's picture of
 *                          frame F; the reply: 1, or 0 (none kept: the view
 *                          shows nothing). "frames view V -1": nothing
 *   frames box RING F [M]  "X0 Y0 X1 Y1": where the fighters of the ports
 *                          in mask M (bit 0 port 1; all if not given) were
 *                          in that picture (their feet, and a point 20 units
 *                          above them), in the game's 640x480; "-1" if none
 *                          or not kept. For a crop that follows the action.
 *
 * A frame's number is host.frame at the boundary after it was drawn: the
 * number a driver is told after stepping it, so what it reads of the game
 * then is what the picture shows. The rings are not part of the game's
 * state: a state loaded leaves them alone.
 */
#include <stdio.h>
#include <string.h>

#include "host.h"

#ifdef HOST_WINDOW
#include <dolphin/gx.h>
#include <melee/cm/camera.h>
#include <melee/ft/fighter.h>
#include <melee/ft/inlines.h>
#include <melee/ft/types.h>
#include <melee/lb/lbvector.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/gobj.h>

#define RINGS 2
#define SLOTS 240
#define WIDTH 576 /* a copy's size, in pixels: 4:3 */
#define HEIGHT 432
#define CLOSEST 224.0F /* the narrowest part copied, of the game's 640 */
#define ROOM 44.0F     /* round the fighters, in the game's units */

void aurora_rmlui_copy_view(int view, const void* dest);
void aurora_set_copy_exact(const void* begin, const void* end);

/// The addresses copies are made "to": one byte each, never written
static char keys[RINGS][SLOTS];

static struct {
    uint32_t frame[SLOTS];  ///< the frame each slot holds
    float box[SLOTS][4][4]; ///< where each port's fighter was (x0 < 0:
                            ///< none)
    int count;              ///< slots used (up to SLOTS)
    int next;               ///< the slot the next copy goes to
} ring[RINGS];

static int recording = -1;
static int follow = 15; ///< the ports the part copied follows

/// The part of the picture each ring copies: its middle and width (its
/// height is three quarters of that); `on` 0 until its first copy.
static struct {
    float cx, cy, w;
    int on;
} view[RINGS];

/// Where each port's fighter is in the picture: its feet, a point above
/// them and, in the air above the stage's floor, the floor below it (a
/// part that followed only the fighter rose with a jump, and a full hop
/// looked no higher than a short one), through the match camera (as
/// "project" in control.c).
static void fighters_box(float (*boxes)[4])
{
    HSD_GObj* cam = Camera_80030A50();
    int port, k;

    for (port = 0; port < 4; port++) {
        float* box = boxes[port];
        HSD_GObj* gobj = Player_GetEntity(port);
        Fighter* fp;
        box[0] = box[1] = 1e9F;
        box[2] = box[3] = -1e9F;
        if (cam == NULL || cam->hsd_obj == NULL || gobj == NULL ||
            !host_live_fighter(gobj) || (fp = GET_FIGHTER(gobj)) == NULL)
        {
            box[0] = -1.0F;
            continue;
        }
        for (k = 0; k < 3; k++) {
            Vec3 at = { fp->cur_pos.x, fp->cur_pos.y + 20.0F * k,
                        fp->cur_pos.z };
            if (k == 2) {
                if (fp->cur_pos.y <= 0.0F) {
                    break;
                }
                at.y = 0.0F; /* the main floor of every legal stage */
            }
            Vec3 out;
            if (lbVector_WorldToScreen(cam->hsd_obj, &at, &out, 0) == NULL) {
                continue;
            }
            box[0] = out.x < box[0] ? out.x : box[0];
            box[1] = out.y < box[1] ? out.y : box[1];
            box[2] = out.x > box[2] ? out.x : box[2];
            box[3] = out.y > box[3] ? out.y : box[3];
        }
        if (box[0] > box[2]) {
            box[0] = -1.0F;
        }
    }
}

static float clampf(float v, float lo, float hi)
{
    return v < lo ? lo : v > hi ? hi : v;
}

/// Where ring `r` copies from this frame (left, top, width, height in the
/// game's 640x480): the fighters followed, as a camera follows them.
static void follow_them(int r, float (*boxes)[4], float* out)
{
    float x0 = 1e9F, y0 = 1e9F, x1 = -1e9F, y1 = -1e9F, w, cx, cy;
    int port, any = 0;

    for (port = 0; port < 4; port++) {
        const float* b = boxes[port];
        if (!(follow & (1 << port)) || b[0] < 0.0F) {
            continue;
        }
        x0 = b[0] < x0 ? b[0] : x0;
        y0 = b[1] < y0 ? b[1] : y0;
        x1 = b[2] > x1 ? b[2] : x1;
        y1 = b[3] > y1 ? b[3] : y1;
        any = 1;
    }
    if (any) {
        x0 -= ROOM;
        x1 += ROOM;
        y0 -= ROOM * 0.9F;
        y1 += ROOM * 1.6F; /* the panel's tags and input display */
        w = x1 - x0;
        if ((y1 - y0) * 16.0F / 9.0F > w) {
            w = (y1 - y0) * 16.0F / 9.0F;
        }
        w = clampf(w, CLOSEST, 640.0F);
        cx = (x0 + x1) * 0.5F;
        cy = (y0 + y1) * 0.5F;
    } else {
        w = 640.0F;
        cx = 320.0F;
        cy = 240.0F;
    }
    if (!view[r].on) {
        view[r].cx = cx;
        view[r].cy = cy;
        view[r].w = w;
        view[r].on = 1;
    } else {
        /* wider at once, narrower slowly; the middle eased */
        view[r].w = w > view[r].w ? w : view[r].w + (w - view[r].w) * 0.06F;
        view[r].cx += (cx - view[r].cx) * 0.25F;
        view[r].cy += (cy - view[r].cy) * 0.25F;
        if (any) {
            /* the fighters kept in, whatever the easing */
            float half = view[r].w * 0.5F, band = view[r].w * 0.28125F;
            view[r].cx = clampf(view[r].cx, x1 - half, x0 + half);
            view[r].cy = clampf(view[r].cy, y1 - band, y0 + band);
        }
    }
    out[2] = (float) ((int) view[r].w & ~1);
    out[3] = (float) ((int) (out[2] * 0.75F) & ~1);
    out[0] = clampf(view[r].cx - out[2] * 0.5F, 0.0F, 640.0F - out[2]);
    out[1] = clampf(view[r].cy - out[3] * 0.5F, 0.0F, 480.0F - out[3]);
}

/// At each frame boundary, before the frame is ended (window.c): the
/// picture just drawn, the part where the fighters are, into the ring
/// recording, if any.
void host_frames_capture(void)
{
    static int exact;
    int r = recording;
    float part[4];

    if (r < 0 || !host.draw) {
        return;
    }
    if (!exact) {
        aurora_set_copy_exact(keys, (const char*) keys + sizeof keys);
        exact = 1;
    }
    fighters_box(ring[r].box[ring[r].next]);
    follow_them(r, ring[r].box[ring[r].next], part);
    GXSetTexCopySrc((u16) part[0], (u16) part[1], (u16) part[2],
                    (u16) part[3]);
    GXSetTexCopyDst(WIDTH, HEIGHT, GX_TF_RGB565, GX_FALSE);
    GXCopyTex(&keys[r][ring[r].next], GX_FALSE);
    ring[r].frame[ring[r].next] = host.frame;
    ring[r].next = (ring[r].next + 1) % SLOTS;
    if (ring[r].count < SLOTS) {
        ring[r].count++;
    }
}

/// The slot of ring `r` that holds frame `f`, or -1.
static int slot_of(int r, uint32_t f)
{
    int i;

    for (i = 0; i < ring[r].count; i++) {
        int s = (ring[r].next - 1 - i + SLOTS) % SLOTS;
        if (ring[r].frame[s] == f) {
            return s;
        }
    }
    return -1;
}

const char* host_frames_command(const char* line)
{
    static char reply[64];
    char verb[16] = "";
    int used = 0, r = -1, v = -1;
    unsigned f = 0;

    sscanf(line, "%15s%n", verb, &used);
    line += used;
    if (strcmp(verb, "rec") == 0) {
        int mask = 15;
        sscanf(line, "%d %d", &r, &mask);
        recording = r >= 0 && r < RINGS ? r : -1;
        if (recording >= 0 && mask != follow) {
            view[recording].on = 0;
        }
        follow = mask;
        snprintf(reply, sizeof reply, "%u", host.frame);
        return reply;
    }
    if (sscanf(line, "%d", &r) != 1) {
        return "error frames rec|clear|range|view|box";
    }
    if (strcmp(verb, "view") == 0) {
        int s;
        v = r;
        r = -1;
        sscanf(line, "%*d %d %u", &r, &f);
        if (r < 0 || r >= RINGS) {
            aurora_rmlui_copy_view(v, NULL);
            return "0";
        }
        s = slot_of(r, f);
        aurora_rmlui_copy_view(v, s >= 0 ? &keys[r][s] : NULL);
        return s >= 0 ? "1" : "0";
    }
    if (r < 0 || r >= RINGS) {
        return "error no such ring";
    }
    if (strcmp(verb, "box") == 0) {
        int s, port, mask = 15, any = 0;
        float u[4] = { 1e9F, 1e9F, -1e9F, -1e9F };
        sscanf(line, "%*d %u %d", &f, &mask);
        s = slot_of(r, f);
        for (port = 0; s >= 0 && port < 4; port++) {
            const float* b = ring[r].box[s][port];
            if (!(mask & (1 << port)) || b[0] < 0.0F) {
                continue;
            }
            u[0] = b[0] < u[0] ? b[0] : u[0];
            u[1] = b[1] < u[1] ? b[1] : u[1];
            u[2] = b[2] > u[2] ? b[2] : u[2];
            u[3] = b[3] > u[3] ? b[3] : u[3];
            any = 1;
        }
        if (!any) {
            return "-1";
        }
        snprintf(reply, sizeof reply, "%.1f %.1f %.1f %.1f", u[0], u[1], u[2],
                 u[3]);
        return reply;
    }
    if (strcmp(verb, "clear") == 0) {
        ring[r].count = 0;
        ring[r].next = 0;
        view[r].on = 0;
        return "ok";
    }
    if (strcmp(verb, "range") == 0) {
        if (ring[r].count == 0) {
            return "-1 -1";
        }
        snprintf(reply, sizeof reply, "%u %u",
                 ring[r].frame[(ring[r].next - ring[r].count + SLOTS) % SLOTS],
                 ring[r].frame[(ring[r].next - 1 + SLOTS) % SLOTS]);
        return reply;
    }
    return "error frames rec|clear|range|view|box";
}

#else

void host_frames_capture(void) {}

const char* host_frames_command(const char* line)
{
    (void) line;
    return "error frames needs the window build";
}

#endif
