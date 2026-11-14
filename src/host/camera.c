/** @file
 * The match camera, as a drill sets it (tools/melee_drills, a scenario's
 * "camera"): the game's own camera modes.
 *
 *   camera normal                 the match camera (both fighters framed)
 *   camera stage                  the whole stage, still
 *   camera follow PORT DIST [H]   the game's free camera (the pause
 *                                 camera's) on PORT, its eye DIST in front
 *                                 of the fighter and H above (Training
 *                                 Mode's "Zoom" is 140 and 10): one fighter
 *                                 alone, framed without the normal camera's
 *                                 close zoom on a lone fighter
 *
 * Followed, the camera is eased (the owner, 2026-11-14: "really jarring.
 * It picks up every little motion from the character including the
 * landing and shock absorption of the impact ... make it smoother so it
 * literally doesn't 100% track the character"). The free camera aims at
 * a bone of the fighter and goes half the way to it every frame, so it
 * dips with every crouch and landing. Here it aims instead at a point
 * that follows the fighter's position (its feet, not a bone: no landing
 * squash), held still while the fighter is within a margin of it and
 * eased towards the fighter beyond it: a short hop does not move it, a
 * dash is followed smoothly.
 */
#include "host.h"

#include <stdio.h>
#include <string.h>

#include <melee/cm/camera.h>
#include <melee/cm/types.h>
#include <melee/ft/fighter.h>
#include <melee/ft/inlines.h>
#include <melee/ft/types.h>
#include <melee/pl/player.h>

Camera* host_game_camera(void); /* camera.c, as the native build patches it */
void host_camera_subject(Vec3* pos, int slot); /* called by camera.c too */
void fn_801650E8(void);         /* the match camera (Match_SetNormalCamera) */
void gm_80165290(int);          /* the fixed camera (Match_SetFixedCamera) */

static char said[96];

/// The margin around the point aimed at within which the fighter moves
/// the camera not at all (game units: a short hop rises about 10, a full
/// jump about 30; the picture at distance 220 is about 200 wide, 150
/// high), and the part of the way beyond it the point goes each frame.
#define STILL_X 12.0F
#define STILL_Y 20.0F
#define EASE_X 0.10F
#define EASE_Y 0.05F

/// The eased point the followed camera aims at: on (a port followed),
/// fresh (taken from the fighter on the next frame: the command was just
/// given, after a drill's reset), where, and how far above the fighter's
/// feet the bone it replaces was when standing.
static struct {
    int on, fresh;
    s8 port;
    float x, y, lift;
} aim;

static float eased(float at, float want, float still, float rate)
{
    float d = want - at;
    if (d > still) {
        return at + (d - still) * rate;
    }
    if (d < -still) {
        return at + (d + still) * rate;
    }
    return at;
}

/// Called by the free camera's update (camera.c, as the native build
/// patches it) with the bone it aims at: replaced by the eased point while
/// a drill's camera follows that fighter.
void host_camera_subject(Vec3* pos, int slot)
{
    HSD_GObj* gobj;
    Fighter* fp;
    float x, y;

    if (!aim.on || slot != aim.port) {
        return;
    }
    gobj = Player_GetEntity(slot);
    if (gobj == NULL || !host_live_fighter(gobj) ||
        (fp = GET_FIGHTER(gobj)) == NULL)
    {
        return;
    }
    if (aim.fresh) {
        float lift = pos->y - fp->cur_pos.y;
        aim.lift = lift < 0.0F ? 0.0F : lift > 20.0F ? 20.0F : lift;
        aim.x = fp->cur_pos.x;
        aim.y = fp->cur_pos.y + aim.lift;
        aim.fresh = 0;
    }
    x = fp->cur_pos.x;
    y = fp->cur_pos.y + aim.lift;
    aim.x = eased(aim.x, x, STILL_X, EASE_X);
    aim.y = eased(aim.y, y, STILL_Y, EASE_Y);
    pos->x = aim.x;
    pos->y = aim.y;
}

const char* host_camera_command(const char* line)
{
    char how[16] = "";
    int used = 0;
    sscanf(line, "%15s%n", how, &used);
    line += used;
    if (strcmp(how, "normal") == 0) {
        aim.on = 0;
        fn_801650E8();
        Camera_8002F3AC();
        return "ok normal";
    }
    if (strcmp(how, "stage") == 0) {
        aim.on = 0;
        gm_80165290(0);
        Camera_8002F3AC();
        return "ok stage";
    }
    if (strcmp(how, "follow") == 0) {
        int port = 0;
        float dist = 140.0F, height = 10.0F;
        Camera* cam;
        if (sscanf(line, "%d %f %f", &port, &dist, &height) < 2 ||
            port < 0 || port > 3)
        {
            return NULL;
        }
        if (Player_GetEntity(port) == NULL) {
            return NULL;
        }
        Camera_8002F9E4((s8) port, 3);
        cam = host_game_camera();
        cam->pause_eye_offset.y = height;
        cam->pause_eye_offset.z = dist;
        aim.on = 1;
        aim.fresh = 1;
        aim.port = (s8) port;
        Camera_8002F3AC();
        snprintf(said, sizeof said, "ok follow %d %.1f %.1f", port,
                 (double) dist, (double) height);
        return said;
    }
    return NULL;
}
