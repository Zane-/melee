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
 */
#include "host.h"

#include <stdio.h>
#include <string.h>

#include <melee/cm/camera.h>
#include <melee/cm/types.h>
#include <melee/pl/player.h>

Camera* host_game_camera(void); /* camera.c, as the native build patches it */
void fn_801650E8(void);         /* the match camera (Match_SetNormalCamera) */
void gm_80165290(int);          /* the fixed camera (Match_SetFixedCamera) */

static char said[96];

const char* host_camera_command(const char* line)
{
    char how[16] = "";
    int used = 0;
    sscanf(line, "%15s%n", how, &used);
    line += used;
    if (strcmp(how, "normal") == 0) {
        fn_801650E8();
        Camera_8002F3AC();
        return "ok normal";
    }
    if (strcmp(how, "stage") == 0) {
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
        Camera_8002F3AC();
        snprintf(said, sizeof said, "ok follow %d %.1f %.1f", port,
                 (double) dist, (double) height);
        return said;
    }
    return NULL;
}
