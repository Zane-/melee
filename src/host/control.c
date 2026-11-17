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
 *   ahead PORT TARGET STOP N BUTTONS LX LY CX CY L R [N ...]
 *                                 the next frames played with PORT's pads
 *                                 (others hold theirs), seen and undone:
 *                                 "@ ok MS ROW;..." (ahead.c)
 *   fp SLOT                       address of a fighter's data, for "r"
 *   ucf [0|1]                     UCF 0.84 off or on (on by default)
 *   freeze 0|1                    the match stands still, still drawn
 *   costume P N                   player P's costume in later matches
 *   studio cam|bg|solo|list ...   a fighter alone: camera, background,
 *                                 the rest undrawn (studio.c)
 *   inputs MASK                   TM-CE's input display for the ports in
 *                                 MASK (bit 0 port 1; inputs.c)
 *   frames rec|clear|range|view   the game's past pictures, kept for the
 *                                 client's coach (frames.c)
 *   mask HEX                      live ports' buttons kept from the game
 *   ledge [P [PERCENT]]           the stage's left ledge: where; P hanging
 *   launch P X Y PERCENT KB ANGLE DIR [JUMPS]
 *                                 fighter P knocked away from (X, Y) by
 *                                 the game's own launch: an edgeguard's
 *                                 start (setup.c)
 *   route PORT TARGET HORIZON N BUTTONS LX LY CX CY L R [N ...] [| N ...]
 *                                 a way back to the stage played ahead to
 *                                 where it is decided (the ledge, the
 *                                 stage, a hit, lost) and undone; routep:
 *                                 its path too (ahead.c)
 *   hitboxes PORT FRAMES N BUTTONS LX LY CX CY L R [N ...]
 *                                 where PORT's hitboxes would be, frame by
 *                                 frame, played ahead and undone (ahead.c)
 *   shield P HEALTH [KEEP]        a fighter's shield health; KEEP 1: kept
 *                                 at it every frame (searches too), 0: no
 *                                 longer; "shield -1 H 0": none kept
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
#include <melee/if/if_2F6E.h>
#include <melee/if/ifstock.h>
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
            if (host_engine_forked()) {
                _exit(0); /* a forked game (engine.c): its thinking is over */
            }
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
    host_gcc_motors_off(); /* the adapter keeps a motor running otherwise */
    _exit(0);
#else
    exit(0);
#endif
}

/// The match each player's HUD stock row was asked for in ("stocks"), so
/// that it is kept through respawns (stock_rows); 0: never.
static unsigned stock_row[4];

/* "gameend": whether GAME! has played out (its graphic's callback) */
static int game_end_done;

static void game_end_played(int index)
{
    (void) index;
    game_end_done = 1;
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
             "\"hitbox\":%d,\"costume\":%d,\"falls\":%d}",
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
                 : 0,
             (int) fp->costume_id, (int) Player_GetFalls(slot));
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
    char a[512], b[512], c[512], d[512];
    /* players 3 and 4 only when the match has them (`vsslots`): two
       fighters otherwise, as every drill and 1v1 reads it */
    int n = host_match.ckind[3] >= 0 ? 4 : host_match.ckind[2] >= 0 ? 3 : 2;

    host_fighter_json(0, a, sizeof a);
    host_fighter_json(1, b, sizeof b);
    if (n > 2) {
        host_fighter_json(2, c, sizeof c);
    }
    if (n > 3) {
        host_fighter_json(3, d, sizeof d);
    }
    printf("@ {\"frame\":%u,\"rng\":%u,\"match\":%u,\"ended\":%u,"
           "\"outcome\":%d,\"p\":[%s,%s%s%s%s%s],\"items\":",
           host.frame, (unsigned) *HSD_RandSeedPtr, host_match.entered,
           host_match.ended, host_match.outcome, a, b, n > 2 ? "," : "",
           n > 2 ? c : "", n > 3 ? "," : "", n > 3 ? d : "");
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

/* --- quiet stretches ---------------------------------------------------- */

static int quiet_now, draw_before;

/// 1: unseen and unheard, not drawn; 2: drawn too, but not shown (the
/// coach's pictures of a run nobody watches, frames.c); 0: as usual.
void host_quiet(int on)
{
    if (on == quiet_now || on < 0 || on > 2) {
        return;
    }
    if (!quiet_now) {
        draw_before = host.draw;
        host_audio_quiet(1);
    }
    /* the draw pass is most of a frame's time */
    host.draw = on == 1 ? 0 : draw_before;
    if (!on) {
        host_audio_quiet(0);
    }
    quiet_now = on;
#ifdef HOST_WINDOW
    host_window_quiet(on);
#endif
}

int host_quiet_now(void)
{
    return quiet_now;
}

static void command(char* line)
{
    char cmd[32] = "";
    int used = 0;

    sscanf(line, "%31s%n", cmd, &used);
    line += used;
    if (host_engine_forked() &&
        (strcmp(cmd, "step") == 0 || strcmp(cmd, "tick") == 0 ||
         strcmp(cmd, "quit") == 0 || strcmp(cmd, "snap") == 0 ||
         strcmp(cmd, "restore") == 0))
    {
        /* a forked game stands at its frame and only thinks (engine.c) */
        if (strcmp(cmd, "quit") == 0) {
            fflush(stdout);
            _exit(0);
        }
        printf("@ error a forked game plays no frames\n");
        fflush(stdout);
        return;
    }
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
        /* "ledge [right]": where the stage's left (or right) ledge is
           ("@ x y", or an error); "ledge P [PERCENT [right]]": player P
           hanging on it */
        int p = -1, right = strstr(line, "right") != NULL;
        float percent = 0.0F, x, y;
        if (sscanf(line, "%d %f", &p, &percent) >= 1) {
            const char* why = host_ledge_side(p, percent, right);
            if (why != NULL) {
                printf("@ error %s\n", why);
                fflush(stdout);
                return;
            }
        }
        if (host_ledge_at(right, &x, &y) < 0) {
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
    } else if (strcmp(cmd, "ahead") == 0) {
        /* "ahead PORT TARGET STOP N BUTTONS LX LY CX CY L R [N ...]": the
           next frames played with PORT's planned pads, then undone; the
           reply, what they showed, comes when they have been (ahead.c) */
        const char* why = host_ahead_begin(line);
        if (why != NULL) {
            printf("@ error %s\n", why);
        } else {
            steps_left = 1; /* this boundary goes on: the frames run */
        }
    } else if (strcmp(cmd, "route") == 0 || strcmp(cmd, "routep") == 0) {
        /* "route PORT TARGET HORIZON N BUTTONS LX LY CX CY L R [N ...] [|
           N ...]": a way back to the stage played ahead to where it is
           decided (the ledge, the stage, a hit, lost), then undone;
           "routep": its path too (ahead.c) */
        const char* why = host_route_begin(line, cmd[5] == 'p');
        if (why != NULL) {
            printf("@ error %s\n", why);
        } else {
            steps_left = 1; /* this boundary goes on: the frames run */
        }
    } else if (strcmp(cmd, "hitboxes") == 0) {
        /* "hitboxes PORT FRAMES N BUTTONS LX LY CX CY L R [N ...]": where
           PORT's hitboxes would be, frame by frame, played ahead and
           undone (ahead.c) */
        const char* why = host_hitboxes_begin(line);
        if (why != NULL) {
            printf("@ error %s\n", why);
        } else {
            steps_left = 1;
        }
    } else if (strcmp(cmd, "launch") == 0) {
        /* "launch P X Y PERCENT KB ANGLE DIR [JUMPS]": fighter P knocked
           away from (X, Y) by KB units of knockback at ANGLE degrees above
           level, toward +x (DIR 1) or -x (-1), with PERCENT damage, JUMPS
           of its jumps used (1: the double jump left) (setup.c) */
        int p = 0, angle = 45, jumps = 1;
        float x = 0, y = 0, percent = 0, kb = 100, dir = 1;
        const char* why;
        sscanf(line, "%d %f %f %f %f %d %f %d", &p, &x, &y, &percent, &kb,
               &angle, &dir, &jumps);
        why = host_launch(p, x, y, percent, kb, angle, dir, jumps);
        if (why != NULL) {
            printf("@ error %s\n", why);
        } else {
            printf("@ ok\n");
        }
    } else if (strcmp(cmd, "search") == 0) {
        /* "search PORT TARGET HORIZON BUDGET DEPTH [KEY=VALUE ...]": PORT's
           lines of play tried in the game and scored (engine.c); the reply
           comes when they have been undone */
        const char* why = host_engine_begin(line);
        if (why != NULL) {
            printf("@ error %s\n", why);
        } else if (host_engine_playing()) {
            steps_left = 1; /* this boundary goes on: the frames run */
        }
    } else if (strcmp(cmd, "camera") == 0) {
        /* "camera normal|stage|follow PORT DIST [H]" (camera.c) */
        const char* r = host_camera_command(line);
        if (r == NULL) {
            printf("@ error camera normal | stage | follow PORT DIST "
                   "[HEIGHT]\n");
        } else {
            printf("@ %s\n", r);
        }
    } else if (strcmp(cmd, "engine") == 0) {
        /* "engine player ...", "engine macros" (engine.c) */
        const char* why = host_engine_command(line);
        if (why == NULL) {
            printf("@ ok\n");
        } else if (*why != 0) {
            printf("@ error %s\n", why);
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
        int p = 0, keep = -1;
        float health = 60.0F;
        const char* why;
        sscanf(line, "%d %f %d", &p, &health, &keep);
        why = keep >= 0 ? host_keep_shield(p, health, keep)
                        : host_set_shield(p, health);
        if (why != NULL) {
            printf("@ error %s\n", why);
        } else {
            printf("@ ok\n");
        }
    } else if (strcmp(cmd, "vsslots") == 0) {
        /* "vsslots L1 L2 [C3 H3 L3 [C4 H4 L4]]": the CPU levels of players
           1 and 2, and players 3 and 4 (a CharacterKind or -1 for none, a
           person or the CPU, its level) in the matches from now on; the
           driver sends it before each "match" (none: two players) */
        int v[8] = {9, 9, -1, 0, 9, -1, 0, 9};
        int got = sscanf(line, "%d %d %d %d %d %d %d %d", &v[0], &v[1],
                         &v[2], &v[3], &v[4], &v[5], &v[6], &v[7]);
        if (got < 2) {
            printf("@ error vsslots L1 L2 [C3 H3 L3 [C4 H4 L4]]\n");
        } else {
            int i;
            host_match.level[0] = v[0];
            host_match.level[1] = v[1];
            for (i = 0; i < 2; i++) {
                int ck = got >= 3 + 3 * i ? v[2 + 3 * i] : -1;
                host_match.ckind[2 + i] = ck;
                host_match.human[2 + i] = v[3 + 3 * i];
                host_match.level[2 + i] = v[4 + 3 * i];
                if (ck >= 0 && v[3 + 3 * i]) {
                    host.pads[2 + i].connected = 1;
                }
            }
            for (i = 0; i < 4; i++) {
                if (host_match.level[i] < 1 || host_match.level[i] > 9) {
                    host_match.level[i] = 9;
                }
            }
            printf("@ ok\n");
        }
    } else if (strcmp(cmd, "vsrules") == 0) {
        /* "vsrules SECONDS FREQ MASK RATIO": the rules the next match is
           played by (match.c): a time limit (0: none), the item frequency
           (-1: none, 0..4), the items on (hex, a bit per ItemKind), the
           damage ratio. The driver sends them before each "match" */
        int secs = 0, freq = -1;
        unsigned long long mask = ~0ULL;
        float ratio = 1.0F;
        sscanf(line, "%d %d %llx %f", &secs, &freq, &mask, &ratio);
        if (secs < 0 || secs > 99 * 60 || freq < -1 || freq > 4 ||
            ratio < 0.5F || ratio > 2.0F)
        {
            printf("@ error vsrules SECONDS FREQ MASK RATIO: SECONDS "
                   "0..5940, FREQ -1..4, RATIO 0.5..2\n");
        } else {
            host_match.time_limit = secs;
            host_match.item_freq = freq;
            host_match.item_mask = mask;
            host_match.damage_ratio = ratio;
            printf("@ ok\n");
        }
    } else if (strcmp(cmd, "match") == 0) {
        /* "match P1 P2 STAGE HUMAN2 SEED STOCKS [CK...]": the CKs are
           loaded with it, for "swap" */
        int c1 = 2, c2 = 9, stage = 0x20, h2 = 1, stocks = 0, used2 = 0;
        unsigned seed = 1;
        sscanf(line, "%d %d %d %d %u %d%n", &c1, &c2, &stage, &h2, &seed,
               &stocks, &used2);
        host_match.preloads = 0;
        if (used2 > 0) {
            char* rest = line + used2;
            int ck, n;
            while (host_match.preloads < 8 &&
                   sscanf(rest, "%d%n", &ck, &n) == 1)
            {
                host_match.preload[host_match.preloads++] = ck;
                rest += n;
            }
        }
        host_match.seed = seed;
        host_match.stocks = stocks;
        host_match.ckind[0] = c1;
        host_match.ckind[1] = c2;
        host_match.stage = stage;
        host_match.human[1] = h2;
        host.pads[1].connected = 1;
        host_match_start();
        printf("@ ok\n");
    } else if (strcmp(cmd, "costume") == 0) {
        /* "costume P N": player P wears costume N (0: the default) in the
           matches set up from now on */
        int p = 0, n = 0;
        sscanf(line, "%d %d", &p, &n);
        if (p < 0 || p >= 4 || n < 0 || n > 5) {
            printf("@ error costume P N: P 0..3, N 0..5\n");
        } else {
            host_match.color[p] = n;
            printf("@ ok\n");
        }
    } else if (strcmp(cmd, "stocks") == 0) {
        /* "stocks P N": player P has N stocks now. The HUD shows them as
           it shows stocks (ifstock.c: N icons up to 5, one breaking when
           N falls); in the endless time match they end nothing, so a
           mode keeps its score in them (the client's Tennis) */
        int p = 0, n = 0;
        sscanf(line, "%d %d", &p, &n);
        if (p < 0 || p >= 4 || n < 0 || n > 99) {
            printf("@ error stocks P N: P 0..3, N 0..99\n");
        } else {
            Player_SetStocks(p, n);
            if (stock_row[p] != host_match.entered) {
                ifStock_802F98E8((u8) p, 0);
                stock_row[p] = host_match.entered;
            }
            printf("@ ok\n");
        }
    } else if (strcmp(cmd, "swap") == 0) {
        /* "swap P CK": player P's fighter is now character CK, in this
           frame, if the match loaded CK ("match ... CK") */
        int p = 1, ck = -1, r;
        sscanf(line, "%d %d", &p, &ck);
        r = p >= 0 && p < 4 ? host_match_swap(p, ck) : -1;
        if (r < 0) {
            printf("@ error character %d is not loaded\n", ck);
        } else {
            printf("@ ok %d\n", r);
        }
    } else if (strcmp(cmd, "loaded") == 0) {
        /* "loaded": the characters the match can swap to */
        char out[128];
        host_match_loaded(out, sizeof out);
        printf("@ ok %s\n", out);
    } else if (strcmp(cmd, "sleep") == 0) {
        /* "sleep P": player P out of play until placed (setup.c) */
        int p = 1;
        const char* why;
        sscanf(line, "%d", &p);
        why = host_sleep(p);
        if (why != NULL) {
            printf("@ error %s\n", why);
        } else {
            printf("@ ok\n");
        }
    } else if (strcmp(cmd, "clean") == 0) {
        /* "clean": what an attempt left behind gone (setup.c) */
        host_clean();
        printf("@ ok\n");
    } else if (strcmp(cmd, "quiet") == 0) {
        /* "quiet 1": the frames until "quiet 0" run unseen and unheard, as
           fast as they go (a match loading); "quiet 2": the same, but drawn
           (the coach's pictures of a run nobody watches, frames.c) */
        int on = 1;
        sscanf(line, "%d", &on);
        host_quiet(on);
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
            const char* look = host_ui_look(line);
            const char* why = look != NULL ? NULL : host_ui_command(line);
            if (look != NULL) {
                printf("@ %s\n", look);
            } else if (why != NULL) {
                printf("@ error %s\n", why);
            } else {
                printf("@ ok\n");
            }
        } else if (cmd[0] == 'p') {
            /* what the people at the live ports hold: "BUTTONS LX LY CX CY
               L R" for each of the four ports; "pads game": what the game
               is given for the coming frame instead (after the input
               delay, the mask and a menu's capture) */
            char which[8] = "";
            sscanf(line, "%7s", which);
            printf("@");
            for (int p = 0; p < 4; p++) {
                const HostPad* pad = strcmp(which, "game") == 0
                                         ? &host.pads[p]
                                         : host_window_seen(p);
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
    } else if (strcmp(cmd, "gameend") == 0) {
        /* "gameend 1": the match ends as a stock match does on the frame
           its last stock is lost (gmvs.c, where the outcome is found):
           GAME! and the announcer's call (ifStatus_802F6EA4's GAME!, 5,
           which plays its own voice), the music let go
           (lbAudioAx_80024D50), rumble stopped, and everything but the
           interface standing still (the game's own end freeze, pause bit
           4). The match stays there instead of leaving for the game's
           results: a Versus mode's end, the client's results after it.
           "gameend 0": the freeze off and the graphic gone (before the
           next match). "gameend": 1 once GAME! has played out. */
        int on = -1;
        sscanf(line, "%d", &on);
        if (on == 1) {
            int i;
            game_end_done = 0;
            HSD_PadRumbleRemoveAll();
            for (i = 0; i < 4; i++) {
                HSD_PadRumbleOn(i);
            }
            /* the second callback: when the graphic has played out
               (if_802F74D0; the first is its first frame) */
            ifStatus_802F6EA4(5, -1, -1, 0, NULL, game_end_played);
            lbAudioAx_80024D50();
            gm_SetDbPauseFlag(4);
            printf("@ ok\n");
        } else if (on == 0) {
            gm_ClearDbPauseFlag(4);
            ifStatus_802F7220();
            game_end_done = 0;
            printf("@ ok\n");
        } else {
            printf("@ ok %d\n", game_end_done);
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
    } else if (strcmp(cmd, "item") == 0) {
        /* "item KIND X Y | list | fighter P | pokemon KIND | spawns 0|1 |
           remove ID": items on demand, for tests (items.c) */
        extern const char* host_item_command(const char* line);
        printf("@ %s\n", host_item_command(line));
    } else if (strcmp(cmd, "studio") == 0) {
        /* "studio cam|bg|solo|list ...": a fighter alone, for pictures
           (studio.c) */
        printf("@ %s\n", host_studio_command(line));
    } else if (strcmp(cmd, "frames") == 0) {
        /* "frames rec|clear|range|view ...": the game's past pictures, for
           the coach (frames.c) */
        printf("@ %s\n", host_frames_command(line));
    } else if (strcmp(cmd, "inputs") == 0) {
        /* "inputs MASK": TM-CE's input display for these ports
           (inputs.c) */
        printf("@ %s\n", host_inputs_command(line));
    } else if (strcmp(cmd, "didraw") == 0) {
        /* "didraw P on|off": TM-CE's DI display for port P (didraw.c) */
        printf("@ %s\n", host_didraw_command(line));
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
    } else if (strcmp(cmd, "delay") == 0) {
#ifdef HOST_WINDOW
        /* "delay N": every live port's input reaches the game N frames
           after it is read (Slippi's online delay; 0 to 15); "delay":
           how many */
        int frames = -1;
        sscanf(line, "%d", &frames);
        printf("@ ok %d\n", host_window_delay(frames));
#else
        printf("@ error delay needs the window build\n");
#endif
    } else if (strcmp(cmd, "volume") == 0) {
#ifdef HOST_WINDOW
        /* "volume MUSIC SOUND": the player's volumes, 0 to 100 each;
           "volume": what they are */
        int music = -1, sound = -1;
        if (sscanf(line, "%d %d", &music, &sound) == 2) {
            host_window_volume(music, sound);
        }
        printf("@ ok %d %d\n", (host_window_gain(1) * 100 + 128) / 256,
               (host_window_gain(0) * 100 + 128) / 256);
#else
        printf("@ error volume needs the window build\n");
#endif
    } else if (strcmp(cmd, "rumble") == 0) {
        /* "rumble": the game's motor command for each port (1 running),
           and with the window build each port's rumble allowed and its
           controller's motor running; "rumble P 1|0": port P's rumble on
           or off; "rumble P test [FRAMES]": run its motor that long (30) */
        int p = -1, frames = 30;
        char what[8] = "";
        int n = sscanf(line, "%d %7s %d", &p, what, &frames);
        if (n >= 2 && (p < 0 || p > 3)) {
            printf("@ error no such port\n");
        } else if (n >= 2) {
#ifdef HOST_WINDOW
            if (strcmp(what, "test") == 0) {
                host_window_rumble_test(p, frames);
            } else {
                host_window_rumble(p, atoi(what));
            }
            printf("@ ok\n");
#else
            printf("@ error rumble needs the window build\n");
#endif
        } else {
            printf("@ ok %d %d %d %d", host_motor(0), host_motor(1),
                   host_motor(2), host_motor(3));
#ifdef HOST_WINDOW
            {
                int allowed[4], running[4], told[4];
                host_window_rumble_state(allowed, running);
                host_gcc_motors(told);
                printf(" | %d %d %d %d | %d %d %d %d | %d %d %d %d",
                       allowed[0], allowed[1], allowed[2], allowed[3],
                       running[0], running[1], running[2], running[3],
                       told[0], told[1], told[2], told[3]);
            }
#endif
            printf("\n");
        }
    } else if (strcmp(cmd, "rules") == 0) {
        /* "rules none" or "rules tug N": how a match ends besides its
           stocks (rules.c), decided in the game's own frame; "rules":
           which */
        char kind[16] = "";
        int n = 0;
        int got = sscanf(line, "%15s %d", kind, &n);
        if (got < 1) {
            int g = 0;
            int k = host_rules_get(&g);
            if (k == HOST_RULES_TUG) {
                printf("@ ok tug %d\n", g);
            } else {
                printf("@ ok none\n");
            }
        } else if (strcmp(kind, "none") == 0) {
            host_rules_set(HOST_RULES_NONE, 0);
            printf("@ ok\n");
        } else if (strcmp(kind, "tug") == 0 && got == 2 && n > 0) {
            host_rules_set(HOST_RULES_TUG, n);
            printf("@ ok\n");
        } else {
            printf("@ error rules none | tug N\n");
        }
    } else if (strcmp(cmd, "moves") == 0) {
        /* "moves P RULE": the moves slot P may use (moves.c): all, shine
           (the down special and no attack), recovery (the down, up and
           side specials); "moves P": which */
        int p = -1;
        char rule[16] = "";
        static const char* names[] = {"all", "shine", "recovery"};
        int n = sscanf(line, "%d %15s", &p, rule);
        if (p < 0 || p >= 4) {
            printf("@ error moves P [all|shine|recovery]: P 0..3\n");
        } else if (n < 2) {
            printf("@ ok %s\n", names[host_moves_get(p)]);
        } else {
            int k = -1;
            for (int i = 0; i < 3; i++) {
                if (strcmp(rule, names[i]) == 0) {
                    k = i;
                }
            }
            if (k < 0) {
                printf("@ error moves: all, shine or recovery\n");
            } else {
                host_moves_set(p, k);
                printf("@ ok\n");
            }
        }
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

/// After a lookahead (ahead.c): the game is back at the boundary whose
/// "ahead" command started it, and the reply has been printed. Commands are
/// read on from there until one lets a frame go, as if "ahead" had replied
/// at once.
void host_control_resume(void)
{
    char line[2048];

    steps_left = 0;
    while (steps_left == 0) {
        if (!read_line(line, sizeof line)) {
            snap_drop_all();
            host_stub_report();
            host_quit();
        }
        command(line);
    }
}

/// The HUD's stock row for the players a mode keeps its score in stocks
/// for ("stocks"). The endless match's HUD shows one icon whatever the
/// count (ifStock_802F98E8's mode 1); the row is made again as a stock
/// match's (mode 0, which follows the count each frame) when the mode
/// first asks in a match, and each time the game makes the player's HUD
/// again: on a respawn (gm_1601.c), as the fighter enters Rebirth.
static void stock_rows(void)
{
    static int reborn_before[4];

    for (int p = 0; p < 4; p++) {
        HSD_GObj* g;
        int reborn;
        if (stock_row[p] == 0 || stock_row[p] != host_match.entered) {
            reborn_before[p] = 0;
            continue;
        }
        g = Player_GetEntity(p);
        reborn = g != NULL && host_live_fighter(g) &&
                 GET_FIGHTER(g) != NULL &&
                 GET_FIGHTER(g)->motion_id == 12; /* ftCo's Rebirth */
        if (reborn && !reborn_before[p]) {
            ifStock_802F98E8((u8) p, 0);
        }
        reborn_before[p] = reborn;
    }
}

void host_control_frame(void)
{
    char line[2048];

    stock_rows();

    host_inputs_frame(); /* the input display, made once a match is on */
    host_didraw_frame(); /* the DI display, the same */
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
