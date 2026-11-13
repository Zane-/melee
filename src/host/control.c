/** @file
 * Driving the game from outside: a line protocol on stdin and stdout.
 *
 * With `--control`, the game stops at each frame boundary until told to go
 * on. Commands, one per line; replies start with "@ ":
 *
 *   step [N]                      run N frames (default 1): "@ frame F"
 *   tick N [P BUTTONS LX LY CX CY L R]...
 *                                 set those pads, run N frames and reply
 *                                 with what `state` prints: a whole frame
 *                                 of a driven match in one exchange
 *   place P X Y FACING AIR PERCENT
 *                                 put player P's fighter standing on the
 *                                 floor at or below (X, Y), or (AIR 1)
 *                                 falling from there (setup.c)
 *   snap                          keep the game as it is now: "@ snap ID"
 *   restore ID                    go back to it: "@ restored ID frame F"
 *   drop ID                       forget it
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
 *
 * One command per line, and the next only after the reply.
 *
 * Snapshots are forks. `snap` forks the process and the child sleeps,
 * holding the whole game (arena, statics, the host's own heap, audio RAM)
 * as it was, shared copy-on-write with the process that carries on.
 * `restore` wakes that child, which forks a copy of itself to take over
 * stdin and stdout, and the process that asked exits. A snapshot can be
 * restored any number of times. The sleepers leave when stdin closes.
 */
#define _GNU_SOURCE
#include "host.h"

#include <errno.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#include <melee/ft/fighter.h>
#include <melee/ft/inlines.h>
#include <melee/ft/types.h>
#include <melee/it/types.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>

static int steps_left;
static int reply_state; ///< the next stop answers with the state (`tick`)
int host_control_enabled;

/* --- snapshots -------------------------------------------------------------- */

#define MAX_SNAPS 256

/// Which process holds each snapshot. Shared by every process of a session,
/// whichever of them is running the game at the moment.
static struct Snap {
    pid_t pid;
    int alive;
}* snaps;

static volatile sig_atomic_t snap_wake; ///< 1: restore, 2: drop

static void on_snap_signal(int sig)
{
    snap_wake = sig == SIGUSR1 ? 1 : 2;
}

static void snaps_init(void)
{
    struct sigaction sa;

    snaps = mmap(NULL, MAX_SNAPS * sizeof *snaps, PROT_READ | PROT_WRITE,
                 MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if (snaps == MAP_FAILED) {
        host_fatal("cannot map the snapshot table");
    }
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_snap_signal;
    sigaction(SIGUSR1, &sa, NULL);
    sigaction(SIGUSR2, &sa, NULL);
    signal(SIGCHLD, SIG_IGN); /* nobody waits for sleepers or old runners */
}

/// Take a snapshot. Returns its id in the process that asked (-1: none
/// left, or fork failed) and -2 in a process that a restore has just
/// started from it.
static int snap_take(int* id_out)
{
    sigset_t block, old;
    pid_t pid;
    int id;

    for (id = 0; id < MAX_SNAPS; id++) {
        if (!snaps[id].alive || kill(snaps[id].pid, 0) != 0) {
            break;
        }
    }
    if (id == MAX_SNAPS) {
        return -1;
    }
    *id_out = id;
    fflush(stdout);
    fflush(stderr);
    sigemptyset(&block);
    sigaddset(&block, SIGUSR1);
    sigaddset(&block, SIGUSR2);
    sigprocmask(SIG_BLOCK, &block, &old);
    pid = fork();
    if (pid < 0) {
        sigprocmask(SIG_SETMASK, &old, NULL);
        return -1;
    }
    if (pid > 0) {
        snaps[id].pid = pid;
        snaps[id].alive = 1;
        sigprocmask(SIG_SETMASK, &old, NULL);
        return id;
    }
    /* The sleeper: wait for a signal, or for stdin to close. */
    snap_wake = 0;
    for (;;) {
        struct pollfd in = { 0, 0, 0 };
        int r = ppoll(&in, 1, NULL, &old);

        if (r > 0 && (in.revents & (POLLHUP | POLLERR | POLLNVAL))) {
            _exit(0);
        }
        if (snap_wake == 2) {
            _exit(0);
        }
        if (snap_wake == 1) {
            snap_wake = 0;
            pid = fork();
            if (pid == 0) {
                sigprocmask(SIG_SETMASK, &old, NULL);
                return -2;
            }
        }
    }
}

static void snap_drop_all(void)
{
    if (snaps == NULL) {
        return;
    }
    for (int id = 0; id < MAX_SNAPS; id++) {
        if (snaps[id].alive) {
            kill(snaps[id].pid, SIGUSR2);
            snaps[id].alive = 0;
        }
    }
}

/* --- reading commands -------------------------------------------------------- */

/* stdin is read with read(), not stdio: a process started from a snapshot
   must not find bytes in a buffer that another process has already acted
   on. */
static char in_buf[4096];
static size_t in_len;

/// The next line, without its newline. False at end of input.
static int read_line(char* out, size_t size)
{
    for (;;) {
        char* nl = memchr(in_buf, '\n', in_len);
        ssize_t got;

        if (nl != NULL) {
            size_t n = (size_t) (nl - in_buf);
            size_t keep = n < size - 1 ? n : size - 1;
            memcpy(out, in_buf, keep);
            out[keep] = '\0';
            in_len -= n + 1;
            memmove(in_buf, nl + 1, in_len);
            return 1;
        }
        if (in_len == sizeof in_buf) {
            in_len = 0; /* a line longer than any command: drop it */
        }
        got = read(0, in_buf + in_len, sizeof in_buf - in_len);
        if (got < 0 && errno == EINTR) {
            continue;
        }
        if (got <= 0) {
            return 0;
        }
        in_len += (size_t) got;
    }
}

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
             "\"hitstun\":%.9g,\"shield\":%.9g,\"gvel\":%.9g,"
             "\"kind\":%d,\"jumps\":%d,\"invuln\":%d,\"stocks\":%d,"
             "\"hitbox\":%d}",
             (int) Player_GetPlayerCharacter(slot), (int) fp->motion_id,
             fp->cur_anim_frame, fp->cur_pos.x, fp->cur_pos.y, fp->self_vel.x,
             fp->self_vel.y, fp->facing_dir, (int) fp->ground_or_air,
             fp->dmg.x1830_percent, fp->dmg.x195c_hitlag_frames,
             fp->x221C_b6 ? *(float*) &fp->mv : 0.0F, fp->shield_health,
             fp->gr_vel, (int) fp->kind, (int) fp->x1968_jumpsUsed,
             (fp->x1988 != 0 || fp->x198C != 0) ? 1 : 0,
             (int) Player_GetStocks(slot),
             (fp->x914[0].state != HitCapsule_Disabled ||
              fp->x914[1].state != HitCapsule_Disabled ||
              fp->x914[2].state != HitCapsule_Disabled ||
              fp->x914[3].state != HitCapsule_Disabled)
                 ? 1
                 : 0);
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

static void print_state(void)
{
    char a[512], b[512];

    host_fighter_json(0, a, sizeof a);
    host_fighter_json(1, b, sizeof b);
    printf("@ {\"frame\":%u,\"rng\":%u,\"p\":[%s,%s],\"items\":",
           host.frame, (unsigned) *HSD_RandSeedPtr, a, b);
    print_items();
    printf("}\n");
}

/// "P BUTTONS LX LY CX CY L R": hold a controller state. Returns how much
/// of the line it used (0: no pad there).
static int set_pad(const char* line)
{
    int p = 0, lx = 0, ly = 0, cx = 0, cy = 0, lt = 0, rt = 0, used = 0;
    unsigned buttons = 0;

    if (sscanf(line, "%d %x %d %d %d %d %d %d%n", &p, &buttons, &lx, &ly,
               &cx, &cy, &lt, &rt, &used) < 8)
    {
        return 0;
    }
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
    return used;
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
    } else if (strcmp(cmd, "tick") == 0) {
        int n = 1, used2 = 0;
        if (sscanf(line, "%d%n", &n, &used2) == 1) {
            line += used2;
            while ((used2 = set_pad(line)) != 0) {
                line += used2;
            }
        }
        steps_left = n > 0 ? n : 1;
        reply_state = 1;
    } else if (strcmp(cmd, "pad") == 0) {
        set_pad(line);
        printf("@ ok\n");
    } else if (strcmp(cmd, "place") == 0) {
        int p = 0, air = 0;
        float x = 0, y = 0, facing = 1, percent = 0;
        const char* why;
        sscanf(line, "%d %f %f %f %d %f", &p, &x, &y, &facing, &air,
               &percent);
        why = host_place(p, x, y, facing, air, percent);
        if (why != NULL) {
            printf("@ error %s\n", why);
        } else {
            printf("@ ok\n");
        }
    } else if (strcmp(cmd, "snap") == 0) {
        int id = -1;
        int r = in_len != 0 ? -3 : snap_take(&id);
        if (r == -2) {
            printf("@ restored %d frame %u\n", id, host.frame);
        } else if (r == -3) {
            printf("@ error commands are waiting: one per reply\n");
        } else if (r < 0) {
            printf("@ error no snapshot taken\n");
        } else {
            printf("@ snap %d\n", r);
        }
    } else if (strcmp(cmd, "restore") == 0) {
        int id = -1;
        sscanf(line, "%d", &id);
        if (id < 0 || id >= MAX_SNAPS || !snaps[id].alive || in_len != 0 ||
            kill(snaps[id].pid, SIGUSR1) != 0)
        {
            printf("@ error no such snapshot\n");
        } else {
            /* The sleeper's copy answers and carries on from here. */
            fflush(stdout);
            _exit(0);
        }
    } else if (strcmp(cmd, "drop") == 0) {
        int id = -1;
        sscanf(line, "%d", &id);
        if (id >= 0 && id < MAX_SNAPS && snaps[id].alive) {
            kill(snaps[id].pid, SIGUSR2);
            snaps[id].alive = 0;
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
        print_state();
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
        snap_drop_all();
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
    if (snaps == NULL) {
        snaps_init();
    }
    if (reply_state) {
        reply_state = 0;
        print_state();
    } else {
        printf("@ frame %u\n", host.frame);
    }
    fflush(stdout);
    while (steps_left == 0) {
        if (!read_line(line, sizeof line)) {
            snap_drop_all();
            host_stub_report();
            exit(0);
        }
        command(line);
    }
}
