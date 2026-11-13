/** @file
 * Driving the game from outside: a line protocol on stdin and stdout.
 *
 * With `--control`, the game stops at each frame boundary until told to go
 * on. Commands, one per line; replies start with "@ ":
 *
 *   step [N]                      run N frames (default 1): "@ frame F"
 *   pad P BUTTONS LX LY CX CY L R hold a controller state (BUTTONS in hex,
 *                                 sticks -127..127, triggers 0..255)
 *   match C1 C2 STAGE [H2] [SEED] start a match: character kinds, stage
 *                                 id, whether player 2 is a human, the
 *                                 random seed it is set up with
 *   state                         frame, random seed and both fighters
 *   rng                           callers of the last frame's random draws
 *   fighter I                     one line of JSON about player I's fighter
 *   seed N                        set the game's random seed
 *   r ADDR LEN / w ADDR HEX       read or write memory
 *   quit
 */
#include "host.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <melee/ft/fighter.h>
#include <melee/ft/inlines.h>
#include <melee/ft/types.h>
#include <melee/it/types.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>

static int steps_left;
int host_control_enabled;

void host_fighter_json(int slot, char* out, size_t size)
{
    HSD_GObj* gobj = Player_GetEntity(slot);
    Fighter* fp;

    if (gobj == NULL || (fp = GET_FIGHTER(gobj)) == NULL) {
        snprintf(out, size, "null");
        return;
    }
    snprintf(out, size,
             "{\"ckind\":%d,\"state\":%d,\"frame\":%.9g,\"x\":%.9g,"
             "\"y\":%.9g,\"vx\":%.9g,\"vy\":%.9g,\"facing\":%.9g,"
             "\"air\":%d,\"percent\":%.9g,\"hitlag\":%.9g,"
             "\"hitstun\":%.9g,\"shield\":%.9g,\"gvel\":%.9g}",
             (int) Player_GetPlayerCharacter(slot), (int) fp->motion_id,
             fp->cur_anim_frame, fp->cur_pos.x, fp->cur_pos.y, fp->self_vel.x,
             fp->self_vel.y, fp->facing_dir, (int) fp->ground_or_air,
             fp->dmg.x1830_percent, fp->dmg.x195c_hitlag_frames,
             fp->x221C_b6 ? *(float*) &fp->mv : 0.0F, fp->shield_health,
             fp->gr_vel);
}

/// Every item, in the order of the game's item list.
static void print_items(void)
{
    int first = 1;
    printf("[");
    for (HSD_GObj* gobj = HSD_GObjPLinkHead[9]; gobj != NULL;
         gobj = gobj->next)
    {
        Item* ip = gobj->user_data;
        if (ip == NULL) {
            continue;
        }
        printf("%s{\"kind\":%d,\"state\":%d,\"x\":%.9g,\"y\":%.9g,"
               "\"vx\":%.9g,\"vy\":%.9g}",
               first ? "" : ",", (int) ip->kind, (int) ip->msid, ip->pos.x,
               ip->pos.y, ip->x40_vel.x, ip->x40_vel.y);
        first = 0;
    }
    printf("]");
}

static void command(char* line)
{
    char cmd[32] = "";
    int used = 0;

    sscanf(line, "%31s%n", cmd, &used);
    line += used;
    if (strcmp(cmd, "step") == 0) {
        int n = 1;
        sscanf(line, "%d", &n);
        steps_left = n > 0 ? n : 1;
    } else if (strcmp(cmd, "pad") == 0) {
        int p = 0, lx = 0, ly = 0, cx = 0, cy = 0, lt = 0, rt = 0;
        unsigned buttons = 0;
        sscanf(line, "%d %x %d %d %d %d %d %d", &p, &buttons, &lx, &ly, &cx,
               &cy, &lt, &rt);
        if (p >= 0 && p < 4) {
            HostPad* pad = &host.pads[p];
            pad->connected = 1;
            pad->buttons = (uint16_t) buttons;
            pad->lx = (int8_t) lx;
            pad->ly = (int8_t) ly;
            pad->cx = (int8_t) cx;
            pad->cy = (int8_t) cy;
            pad->lt = (uint8_t) lt;
            pad->rt = (uint8_t) rt;
        }
        printf("@ ok\n");
    } else if (strcmp(cmd, "match") == 0) {
        int c1 = 2, c2 = 9, stage = 0x20, h2 = 1;
        unsigned seed = 1;
        sscanf(line, "%d %d %d %d %u", &c1, &c2, &stage, &h2, &seed);
        host_match.seed = seed;
        host_match.ckind[0] = c1;
        host_match.ckind[1] = c2;
        host_match.stage = stage;
        host_match.human[1] = h2;
        host.pads[1].connected = 1;
        host_match_start();
        printf("@ ok\n");
    } else if (strcmp(cmd, "state") == 0) {
        char a[512], b[512];
        host_fighter_json(0, a, sizeof a);
        host_fighter_json(1, b, sizeof b);
        printf("@ {\"frame\":%u,\"rng\":%u,\"p\":[%s,%s],\"items\":",
               host.frame, (unsigned) *HSD_RandSeedPtr, a, b);
        print_items();
        printf("}\n");
    } else if (strcmp(cmd, "rng") == 0) {
        host_rng_print();
    } else if (strcmp(cmd, "fighter") == 0) {
        char buf[512];
        int i = 0;
        sscanf(line, "%d", &i);
        host_fighter_json(i, buf, sizeof buf);
        printf("@ %s\n", buf);
    } else if (strcmp(cmd, "seed") == 0) {
        unsigned seed = 0;
        sscanf(line, "%u", &seed);
        *HSD_RandSeedPtr = seed;
        printf("@ ok\n");
    } else if (strcmp(cmd, "r") == 0) {
        unsigned addr = 0, len = 0;
        sscanf(line, "%x %u", &addr, &len);
        printf("@ ");
        for (unsigned i = 0; i < len; i++) {
            printf("%02x", ((uint8_t*) (uintptr_t) addr)[i]);
        }
        printf("\n");
    } else if (strcmp(cmd, "w") == 0) {
        unsigned addr = 0;
        char hex[1024] = "";
        sscanf(line, "%x %1023s", &addr, hex);
        for (size_t i = 0; i + 1 < strlen(hex); i += 2) {
            unsigned byte = 0;
            sscanf(hex + i, "%2x", &byte);
            ((uint8_t*) (uintptr_t) addr)[i / 2] = (uint8_t) byte;
        }
        printf("@ ok\n");
    } else if (strcmp(cmd, "quit") == 0) {
        host_stub_report();
        exit(0);
    } else if (cmd[0] != '\0') {
        printf("@ error unknown command %s\n", cmd);
    }
    fflush(stdout);
}

void host_control_frame(void)
{
    char line[2048];

    if (!host_control_enabled) {
        return;
    }
    if (steps_left > 0 && --steps_left > 0) {
        return;
    }
    printf("@ frame %u\n", host.frame);
    fflush(stdout);
    while (steps_left == 0) {
        if (fgets(line, sizeof line, stdin) == NULL) {
            host_stub_report();
            exit(0);
        }
        command(line);
    }
}
