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
 *   fp SLOT                       address of a fighter's data, for "r"
 *   ucf [0|1]                     UCF 0.84 off or on (on by default)
 *   freeze 0|1                    the match stands still, still drawn
 *   mask HEX                      live ports' buttons kept from the game
 *   ledge [P [PERCENT]]           the stage's left ledge: where; P hanging
 *   shield P HEALTH               a fighter's shield health
 *   ui ...                        the client's interface (ui.cpp)
 *   window [fullscreen 0|1|toggle | size W H]
 *                                 the window: its size, the frame the
 *                                 picture keeps to, fullscreen (F11 too)
 *   pads                          what the live ports' people are holding
 *   capture 0|1                   keep those presses from the game (menus)
 *   devices                       the GameCube adapter's state, SDL's pads
 *   gcc HEX | gcc forget          decode an adapter report (a test)
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
#include <time.h>
#include <sys/mman.h>
#include <unistd.h>

#include <melee/cm/camera.h>
#include <melee/ft/fighter.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/lb/lbvector.h>
#include <melee/ft/inlines.h>
#include <melee/gm/gmscene.h>
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

/// Slots 4 to 7 are the second fighter of ports 0 to 3 (the Ice Climbers'
/// partner; Zelda's other form).
/// Whether `gobj` is one of the fighters that exist now. The player table
/// keeps a fighter's object after its match has ended and the object has
/// been freed; reading it then reads freed memory.
int host_live_fighter(const void* gobj)
{
    for (HSD_GObj* cur = HSD_GObjPLinkHead[HSD_GOBJ_PLINK_FIGHTER];
         cur != NULL; cur = cur->next)
    {
        if (cur == gobj) {
            return 1;
        }
    }
    return 0;
}

/// End the process. The window build does not run exit()'s teardown: the
/// graphics libraries' never returned (see host_window_frame).
void host_quit(void)
{
    fflush(stdout);
    fflush(stderr);
#ifdef HOST_WINDOW
    _exit(0);
#else
    exit(0);
#endif
}

void host_fighter_json(int slot, char* out, size_t size)
{
    HSD_GObj* gobj = slot >= 4 && slot < 8
                         ? Player_GetEntityAtIndex(slot - 4, 1)
                         : Player_GetEntity(slot);
    Fighter* fp;

    if (gobj == NULL || !host_live_fighter(gobj) ||
        (fp = GET_FIGHTER(gobj)) == NULL)
    {
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
    printf("@ {\"frame\":%u,\"rng\":%u,\"match\":%u,\"ended\":%u,"
           "\"p\":[%s,%s],\"items\":",
           host.frame, (unsigned) *HSD_RandSeedPtr, host_match.entered,
           host_match.ended, a, b);
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

double host_driver_ms;

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
    } else if (strcmp(cmd, "ledge") == 0) {
        /* "ledge": where the stage's left ledge is ("@ x y", or an error);
           "ledge P [PERCENT]": player P hanging on it */
        int p = -1;
        float percent = 0.0F, x, y;
        if (sscanf(line, "%d %f", &p, &percent) >= 1) {
            const char* why = host_ledge(p, percent);
            if (why != NULL) {
                printf("@ error %s\n", why);
                fflush(stdout);
                return;
            }
        }
        if (host_left_ledge(&x, &y) < 0) {
            printf("@ error no ledge found\n");
        } else {
            printf("@ %.9g %.9g\n", x, y);
        }
    } else if (strcmp(cmd, "clip") == 0) {
        /* "clip": the clipboard's text, on one line; "clip set TEXT" */
#ifdef HOST_WINDOW
        char text[512];
        if (strncmp(line, "set ", 4) == 0) {
            host_window_set_clipboard(line + 4);
            printf("@ ok\n");
        } else {
            host_window_clipboard(text, sizeof text);
            for (char* c = text; *c; c++) {
                if (*c == '\n' || *c == '\r') {
                    *c = ' ';
                }
            }
            printf("@ ok %s\n", text);
        }
#else
        printf("@ error clip needs the window build\n");
#endif
    } else if (strcmp(cmd, "dump") == 0) {
        /* "dump PATH": the whole state into a file (state.c) */
        char path[512] = "";
        sscanf(line, "%511s", path);
        if (host_state_dump(path) < 0) {
            printf("@ error cannot write %s\n", path);
        } else {
            printf("@ ok\n");
        }
    } else if (strcmp(cmd, "draw") == 0) {
        /* "draw 1|0": run the draw pass or not (tests) */
        int on = 1;
        sscanf(line, "%d", &on);
        host.draw = on;
        printf("@ ok\n");
    } else if (strcmp(cmd, "net") == 0) {
        /* "net start LOCAL BIND PEER_IP PEER_PORT DELAY [LAG LOSS
           JITTER]", "net stop", "net stats", "net hash" (net.c) */
        char what[16] = "", ip[64] = "";
        int local = 0, bind_port = 0, peer_port = 0, delay = 2;
        int lag = 0, loss = 0, jitter = 0;
        sscanf(line, "%15s", what);
        if (strcmp(what, "start") == 0) {
            const char* why;
            sscanf(line, "%15s %d %d %63s %d %d %d %d %d", what, &local,
                   &bind_port, ip, &peer_port, &delay, &lag, &loss, &jitter);
            why = host_net_start(local, bind_port, ip, peer_port, delay,
                                 lag, loss, jitter);
            if (why != NULL) {
                printf("@ error %s\n", why);
            } else {
                printf("@ ok\n");
            }
        } else if (strcmp(what, "stop") == 0) {
            host_net_stop();
            printf("@ ok\n");
        } else if (strcmp(what, "stats") == 0) {
            char out[256];
            host_net_report(out, sizeof out);
            printf("@ ok %s\n", out);
        } else if (strcmp(what, "hash") == 0) {
            printf("@ ok %016llx\n", (unsigned long long) host_net_hash());
        } else if (strcmp(what, "rng") == 0) {
            char out[1024];
            unsigned f = 0;
            sscanf(line, "%15s %u", what, &f);
            if (host_net_rng(f, out, sizeof out) < 0) {
                printf("@ error no draws kept for frame %u\n", f);
            } else {
                printf("@ ok %s\n", out);
            }
        } else if (strcmp(what, "input") == 0) {
            char out[256];
            unsigned f = 0;
            sscanf(line, "%15s %u", what, &f);
            if (host_net_inputs(f, out, sizeof out) < 0) {
                printf("@ error no input for frame %u\n", f);
            } else {
                printf("@ ok %s\n", out);
            }
        } else {
            printf("@ error net start|stop|stats|hash\n");
        }
    } else if (strcmp(cmd, "rb") == 0) {
        /* "rb start", "rb stop", "rb mark" (a frame boundary: its undo
           record), "rb back N" (N boundaries back), "rb stats" */
        char what[16] = "";
        int n = 0;
        sscanf(line, "%15s %d", what, &n);
        if (strcmp(what, "start") == 0) {
            const char* why = host_rb_start();
            if (why != NULL) {
                printf("@ error %s\n", why);
            } else {
                printf("@ ok\n");
            }
        } else if (strcmp(what, "stop") == 0) {
            host_rb_stop();
            printf("@ ok\n");
        } else if (strcmp(what, "mark") == 0) {
            printf("@ ok %d\n", host_rb_mark());
        } else if (strcmp(what, "back") == 0) {
            if (host_rb_rewind(n) < 0) {
                printf("@ error cannot go %d back (%d kept)\n", n,
                       host_rb_kept());
            } else {
                printf("@ ok %u\n", host.frame);
            }
        } else if (strcmp(what, "stats") == 0) {
            char line_out[256];
            host_rb_report(line_out, sizeof line_out);
            printf("@ ok %s\n", line_out);
        } else {
            printf("@ error rb start|stop|mark|back N|stats\n");
        }
    } else if (strcmp(cmd, "save") == 0) {
        /* "save N": the game's whole state into slot N (state.c) */
        int n = 0;
        sscanf(line, "%d", &n);
        if (host_state_save(n) < 0) {
            printf("@ error no slot %d\n", n);
        } else {
            printf("@ ok %zu\n", host_state_size());
        }
    } else if (strcmp(cmd, "load") == 0) {
        /* "load N": the state saved in slot N, back */
        int n = 0;
        sscanf(line, "%d", &n);
        if (host_state_load(n) < 0) {
            printf("@ error nothing in slot %d\n", n);
        } else {
            printf("@ ok %u\n", host.frame);
        }
    } else if (strcmp(cmd, "hash") == 0) {
        /* "hash": the whole state's hash; "hash N": where the state
           differs first from slot N ("@ ok same", or region, offset and
           address) */
        int n = -1, region = -1;
        long off;
        if (sscanf(line, "%d", &n) == 1) {
            off = host_state_diff(n, &region);
            if (off == -2) {
                printf("@ error nothing in slot %d\n", n);
            } else if (off < 0) {
                printf("@ ok same\n");
            } else {
                printf("@ ok %d %ld %#lx\n", region, off,
                       (unsigned long) host_state_address(region, off));
            }
        } else {
            size_t a, s, h;
            uint32_t used, top, peak;
            host_state_sizes(&a, &s, &h);
            host_game_heap_stats(&used, &top, &peak);
            printf("@ ok %016llx %zu %zu %zu %u %u\n",
                   (unsigned long long) host_state_hash(), a, s, h, used,
                   peak);
        }
    } else if (strcmp(cmd, "sfx") == 0) {
        /* "sfx N": the game's menu sound N (0 to 10: lbAudioAx_80024030,
           what its menus play: moving, choosing, going back...) */
        int n = 0;
        sscanf(line, "%d", &n);
        if (n < 0 || n > 10) {
            printf("@ error menu sounds are 0 to 10\n");
        } else {
            lbAudioAx_80024030(n);
            printf("@ ok\n");
        }
    } else if (strcmp(cmd, "sound") == 0) {
        /* "sound ID [VOLUME [PAN]]": sound effect ID, as the game plays
           one (volume 0 to 127, pan 0 to 127, 64 the middle) */
        int id = 0, vol = 0x7F, pan = 0x40;
        sscanf(line, "%d %d %d", &id, &vol, &pan);
        printf("@ ok %d\n", lbAudioAx_800237A8(id, vol, pan));
    } else if (strcmp(cmd, "bgm") == 0) {
        /* "bgm N": music N of the game's list (lbaudio_ax.c, hps_files:
           52 is the main menu's); "bgm -1": the music stops */
        int n = -1;
        if (sscanf(line, "%d", &n) != 1) {
            /* "bgm": the music the game started last */
            printf("@ %s\n", host_song()[0] ? host_song() : "-");
            fflush(stdout);
            return;
        }
        if (n < 0) {
            lbAudioAx_800236DC();
        } else {
            lbAudioAx_80023F28(n);
        }
        printf("@ ok\n");
    } else if (strcmp(cmd, "anchor") == 0) {
        /* "anchor P 1": player P is held where it stands (nothing pushes
           it sideways) until "anchor P 0" or another match; "anchor -1"
           lets every one go */
        int p = -1, on = 1;
        const char* why;
        sscanf(line, "%d %d", &p, &on);
        why = host_anchor(p, on);
        if (why != NULL) {
            printf("@ error %s\n", why);
        } else {
            printf("@ ok\n");
        }
    } else if (strcmp(cmd, "rebirth") == 0) {
        /* "rebirth P X Y": player P waiting on a respawn platform at
           (X, Y), as after losing a stock */
        int p = 0;
        float x = 0.0F, y = 0.0F;
        const char* why;
        sscanf(line, "%d %f %f", &p, &x, &y);
        why = host_rebirth(p, x, y);
        if (why != NULL) {
            printf("@ error %s\n", why);
        } else {
            printf("@ ok\n");
        }
    } else if (strcmp(cmd, "shield") == 0) {
        int p = 0;
        float health = 60.0F;
        const char* why;
        sscanf(line, "%d %f", &p, &health);
        why = host_set_shield(p, health);
        if (why != NULL) {
            printf("@ error %s\n", why);
        } else {
            printf("@ ok\n");
        }
    } else if (strcmp(cmd, "match") == 0) {
        int c1 = 2, c2 = 9, stage = 0x20, h2 = 1, stocks = 0;
        unsigned seed = 1;
        sscanf(line, "%d %d %d %d %u %d", &c1, &c2, &stage, &h2, &seed,
               &stocks);
        host_match.seed = seed;
        host_match.stocks = stocks;
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
    } else if (strcmp(cmd, "fp") == 0) {
        /* where a fighter's data is (0 if none), for "r": slots as for
           "fighter" */
        int i = 0;
        HSD_GObj* gobj;
        sscanf(line, "%d", &i);
        gobj = i >= 4 && i < 8 ? Player_GetEntityAtIndex(i - 4, 1)
                               : Player_GetEntity(i);
        printf("@ %x\n", (unsigned) (uintptr_t) (
                              gobj != NULL && host_live_fighter(gobj)
                                  ? GET_FIGHTER(gobj)
                                  : NULL));
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
    } else if (strcmp(cmd, "devices") == 0 || strcmp(cmd, "gcc") == 0) {
#ifdef HOST_WINDOW
        if (cmd[0] == 'd') {
            char text[600];
            host_window_devices(text, sizeof text);
            printf("@ %s\n", text);
        } else {
            /* "gcc HEX": a report as the adapter sends it, decoded for
               each of its ports ("gcc forget": the rest positions go) */
            char hex[128] = "";
            uint8_t report[37] = { 0 };
            sscanf(line, "%127s", hex);
            if (strcmp(hex, "forget") == 0) {
                host_gcc_forget();
                printf("@ ok\n");
            } else {
                for (size_t i = 0; i < sizeof report && hex[i * 2]; i++) {
                    unsigned byte = 0;
                    sscanf(hex + i * 2, "%2x", &byte);
                    report[i] = (uint8_t) byte;
                }
                printf("@");
                for (int p = 0; p < 4; p++) {
                    HostPad pad;
                    int there = host_gcc_decode(report, p, &pad);
                    printf(" %d %x %d %d %d %d %d %d", there, pad.buttons,
                           pad.lx, pad.ly, pad.cx, pad.cy, pad.lt, pad.rt);
                }
                printf("\n");
            }
        }
#else
        printf("@ error %s needs the window build\n", cmd);
#endif
    } else if (strcmp(cmd, "ui") == 0 || strcmp(cmd, "pads") == 0 ||
               strcmp(cmd, "capture") == 0)
    {
#ifdef HOST_WINDOW
        if (cmd[0] == 'u') {
            const char* why = host_ui_command(line);
            if (why != NULL) {
                printf("@ error %s\n", why);
            } else {
                printf("@ ok\n");
            }
        } else if (cmd[0] == 'p') {
            /* what the people at the live ports hold: "BUTTONS LX LY CX CY
               L R" for each of the four ports */
            printf("@");
            for (int p = 0; p < 4; p++) {
                const HostPad* pad = host_window_seen(p);
                printf(" %x %d %d %d %d %d %d", pad->buttons, pad->lx,
                       pad->ly, pad->cx, pad->cy, pad->lt, pad->rt);
            }
            printf("\n");
        } else {
            int on = 1;
            sscanf(line, "%d", &on);
            host_window_capture(on);
            printf("@ ok\n");
        }
#else
        printf("@ error %s needs the window build\n", cmd);
#endif
    } else if (strcmp(cmd, "live") == 0 || strcmp(cmd, "pace") == 0) {
#ifdef HOST_WINDOW
        if (cmd[0] == 'l') {
            int p = 0;
            char source[16] = "auto";
            const char* why;
            sscanf(line, "%d %15s", &p, source);
            why = host_window_live(p, source);
            if (why != NULL) {
                printf("@ error %s\n", why);
            } else {
                printf("@ ok\n");
            }
        } else {
            int on = 1;
            sscanf(line, "%d", &on);
            host_window_pace(on);
            printf("@ ok\n");
        }
#else
        printf("@ error %s needs the window build\n", cmd);
#endif
    } else if (strcmp(cmd, "project") == 0) {
        /* "project X Y [Z]": where a point of the stage is in the picture,
           in the game's 640x480 (y down), through the match camera, as the
           name tags over the fighters are placed (ifnametag.c) */
        float x = 0, y = 0, z = 0;
        HSD_GObj* cam = Camera_80030A50();
        sscanf(line, "%f %f %f", &x, &y, &z);
        if (cam == NULL || cam->hsd_obj == NULL) {
            printf("@ error no camera\n");
        } else {
            Vec3 at = { x, y, z };
            Vec3 out;
            if (lbVector_WorldToScreen(cam->hsd_obj, &at, &out, 0) == NULL) {
                printf("@ error not projected\n");
            } else {
                printf("@ ok %.2f %.2f\n", out.x, out.y);
            }
        }
    } else if (strcmp(cmd, "freeze") == 0) {
        /* "freeze 1": the match stands still and goes on being drawn (the
           game's developers' pause, without its menu); "freeze 0" */
        int on = 1;
        sscanf(line, "%d", &on);
        if (on) {
            gm_SetDbPauseFlag(0);
        } else {
            gm_ClearDbPauseFlag(0);
        }
        printf("@ ok\n");
    } else if (strcmp(cmd, "script") == 0) {
#ifdef HOST_WINDOW
        /* "script P 1": live port P is read, but the game takes the
           driver's pad (a demonstration); "script P 0" */
        int p = 0, on = 1;
        sscanf(line, "%d %d", &p, &on);
        host_window_scripted(p, on);
        printf("@ ok\n");
#else
        printf("@ error script needs the window build\n");
#endif
    } else if (strcmp(cmd, "mask") == 0) {
#ifdef HOST_WINDOW
        /* "mask HEX": buttons of the live ports kept from the game */
        unsigned buttons = 0;
        sscanf(line, "%x", &buttons);
        host_window_mask(buttons);
        printf("@ ok\n");
#else
        printf("@ error mask needs the window build\n");
#endif
    } else if (strcmp(cmd, "ucf") == 0) {
        /* "ucf 0" or "ucf 1": UCF 0.84 off or on (on from the start);
           "ucf": which */
        extern u8 tm_ucf_off;
        int on;
        if (sscanf(line, "%d", &on) == 1) {
            tm_ucf_off = on ? 0 : 1;
        }
        printf("@ %d\n", tm_ucf_off ? 0 : 1);
    } else if (strcmp(cmd, "window") == 0) {
#ifdef HOST_WINDOW
        /* "window": its size, the frame the picture keeps to, fullscreen
           or not, as JSON. "window fullscreen 0|1|toggle", "window size W
           H": the same after the change was asked for. */
        char what[16] = "", arg[16] = "", text[200];
        const char* why = NULL;
        int w = 0, h = 0;

        sscanf(line, "%15s %15s", what, arg);
        if (strcmp(what, "fullscreen") == 0) {
            host_window_fullscreen(strcmp(arg, "toggle") == 0 ? 2
                                                              : arg[0] == '1');
        } else if (strcmp(what, "size") == 0) {
            why = sscanf(line, "%*s %d %d", &w, &h) == 2
                      ? host_window_resize(w, h)
                      : "window size W H";
        } else if (what[0] != '\0') {
            why = "window [fullscreen 0|1|toggle | size W H]";
        }
        if (why != NULL) {
            printf("@ error %s\n", why);
        } else {
            host_window_describe(text, sizeof text);
            printf("@ %s\n", text);
        }
#else
        printf("@ error %s needs the window build\n", cmd);
#endif
    } else if (strcmp(cmd, "quit") == 0) {
        snap_drop_all();
        host_stub_report();
        host_quit();
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
    {
        /* how long the game stood still for whoever drives it: the reply
           above to the command that lets the next frame go */
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        while (steps_left == 0) {
            if (!read_line(line, sizeof line)) {
                snap_drop_all();
                host_stub_report();
                host_quit();
            }
            command(line);
        }
        clock_gettime(CLOCK_MONOTONIC, &t1);
        host_driver_ms = (t1.tv_sec - t0.tv_sec) * 1000.0 +
                         (t1.tv_nsec - t0.tv_nsec) / 1e6;
    }
}
