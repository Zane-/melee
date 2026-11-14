/** @file
 * Lookahead: the next frames played with a planned pad, seen, and undone.
 *
 * "ahead PORT TARGET STOP N BUTTONS LX LY CX CY L R [N ...]": port PORT
 * holds each pad for its N frames, in turn; every other port keeps holding
 * what it holds now (a person's live pad included: the guess rollback
 * netcode makes too). The game plays those frames at once, undrawn and
 * unheard, then goes back to where the command was read, and the reply
 * says what happened, frame by frame. Which is how the Melee Actor asks
 * "if I jump now and nair 14 frames later, does it connect?" of the game
 * itself (tools/melee_actor/ahead.py), in a few milliseconds, every frame,
 * in a match a person is playing.
 *
 * STOP: 0 plays every frame asked for; S > 0 stops S frames after the
 * first contact (the target hit or in hitlag, or PORT hit).
 *
 * The reply: "@ ok MS ROW;ROW;..." with one row per frame played, the
 * state after it:
 *   a.state a.x a.y a.air a.percent a.hitlag a.hitbox a.facing
 *   t.state t.x t.y t.air t.percent t.shield t.hitlag gap gx
 * `gap`: how far PORT's nearest active hitbox is from TARGET's hurtboxes,
 * edge to edge (negative: they overlap; 999 with no hitbox out). `gx`:
 * where that hitbox is past the target's centre, along PORT's facing
 * (negative: short of it). Both are for steering; whether it connected is
 * the game's to say (percent, hitlag, shieldstun).
 *
 * How it goes back: the rollback records (rollback.c). A mark where the
 * command is read, the frames, a mark, and one record undone; only the
 * pages the frames wrote are copied. The frames are run by the scene loop
 * as ever: lb_80019894 (main.c) asks host_ahead_boundary at each boundary;
 * at the last it undoes them, and the boundary the command came in goes
 * on reading commands (host_control_resume) as if the command had just
 * replied. The C stack at every boundary is the same, which is what
 * rollback relies on too.
 *
 * This file's statics are not the game's state (tools/native_build.py's
 * GAME_STATE_HOST does not list it), so what the frames showed survives
 * their undoing.
 */
#include "host.h"

#include <math.h>
#include <stdint.h>
#include <sys/types.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include <melee/ft/inlines.h>
#include <melee/ft/types.h>
#include <melee/lb/types.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/gobj.h>

#define AHEAD_MAX 180 /* frames one lookahead may play */
#define SEGS 16
#define NO_GAP 999.0F

typedef struct Seg {
    int frames;
    HostPad pad;
} Seg;

typedef struct Row {
    int a_state, a_air, a_hitbox, t_state, t_air;
    float a_x, a_y, a_percent, a_hitlag, a_facing;
    float t_x, t_y, t_percent, t_shield, t_hitlag;
    float gap, gx;
} Row;

static struct {
    int active;
    int port, target, stop;
    Seg segs[SEGS];
    int nsegs, total;
    int played;        ///< frames played so far
    int contact_at;    ///< the frame of the first contact, or -1
    float a_percent0, t_percent0;
    Row rows[AHEAD_MAX];
    struct timespec t0;
    pid_t rb_pid;      ///< the process rollback was started in by us
} ahead;

int host_ahead_active(void)
{
    return ahead.active;
}

static Fighter* fighter_of(int slot)
{
    HSD_GObj* gobj = Player_GetEntity(slot);
    if (gobj == NULL || !host_live_fighter(gobj)) {
        return NULL;
    }
    return GET_FIGHTER(gobj);
}

/// Distance from point (px, py) to the segment a-b, in the stage's plane.
static float seg_dist(float px, float py, const Vec3* a, const Vec3* b)
{
    float dx = b->x - a->x, dy = b->y - a->y;
    float len2 = dx * dx + dy * dy, t = 0.0F;
    if (len2 > 1e-6F) {
        t = ((px - a->x) * dx + (py - a->y) * dy) / len2;
        t = t < 0.0F ? 0.0F : t > 1.0F ? 1.0F : t;
    }
    dx = a->x + t * dx - px;
    dy = a->y + t * dy - py;
    return sqrtf(dx * dx + dy * dy);
}

/// PORT's active hitboxes against TARGET's hurtboxes: the smallest gap
/// edge to edge, and where along PORT's facing the hitbox that has it is.
static void hit_gap(Fighter* a, Fighter* t, float* gap, float* gx)
{
    *gap = NO_GAP;
    *gx = 0.0F;
    for (int h = 0; h < 4; h++) {
        HitCapsule* hit = &a->x914[h];
        if (hit->state == HitCapsule_Disabled) {
            continue;
        }
        for (int end = 0; end < 2; end++) {
            const Vec3* p = end == 0 ? &hit->x4C : &hit->x58;
            for (int i = 0; i < t->hurt_capsules_len && i < 15; i++) {
                HurtCapsule* hurt = &t->hurt_capsules[i].capsule;
                float d = seg_dist(p->x, p->y, &hurt->a_pos, &hurt->b_pos) -
                          hit->scale - hurt->scale;
                if (d < *gap) {
                    *gap = d;
                    *gx = (p->x - t->cur_pos.x) * a->facing_dir;
                }
            }
        }
    }
}

static int any_hitbox(Fighter* fp)
{
    for (int h = 0; h < 4; h++) {
        if (fp->x914[h].state != HitCapsule_Disabled) {
            return 1;
        }
    }
    return 0;
}

static void record(Row* row)
{
    Fighter* a = fighter_of(ahead.port);
    Fighter* t = fighter_of(ahead.target);
    memset(row, 0, sizeof *row);
    row->gap = NO_GAP;
    if (a == NULL || t == NULL) {
        return;
    }
    row->a_state = (int) a->motion_id;
    row->a_x = a->cur_pos.x;
    row->a_y = a->cur_pos.y;
    row->a_air = (int) a->ground_or_air;
    row->a_percent = a->dmg.x1830_percent;
    row->a_hitlag = a->dmg.x195c_hitlag_frames;
    row->a_hitbox = any_hitbox(a);
    row->a_facing = a->facing_dir;
    row->t_state = (int) t->motion_id;
    row->t_x = t->cur_pos.x;
    row->t_y = t->cur_pos.y;
    row->t_air = (int) t->ground_or_air;
    row->t_percent = t->dmg.x1830_percent;
    row->t_shield = t->shield_health;
    row->t_hitlag = t->dmg.x195c_hitlag_frames;
    hit_gap(a, t, &row->gap, &row->gx);
}

/// The pad PORT holds on frame `n` of the lookahead.
static const HostPad* pad_for(int n)
{
    for (int s = 0; s < ahead.nsegs; s++) {
        if (n < ahead.segs[s].frames) {
            return &ahead.segs[s].pad;
        }
        n -= ahead.segs[s].frames;
    }
    return &ahead.segs[ahead.nsegs - 1].pad;
}

/// "ahead ..." read at a frame boundary (control.c). NULL when the frames
/// are under way: the command loop lets the frame go, and the reply comes
/// when they have been undone. Else why not.
const char* host_ahead_begin(const char* line)
{
    int used = 0;
    Fighter *a, *t;

    if (ahead.active) {
        return "a lookahead is already running";
    }
    if (host_net_active()) {
        return "not during a netplay session";
    }
    if (sscanf(line, "%d %d %d%n", &ahead.port, &ahead.target, &ahead.stop,
               &used) < 3 ||
        ahead.port < 0 || ahead.port > 3 || ahead.target < 0 ||
        ahead.target > 3)
    {
        return "ahead PORT TARGET STOP N BUTTONS LX LY CX CY L R ...";
    }
    line += used;
    ahead.nsegs = 0;
    ahead.total = 0;
    for (;;) {
        int n = 0, lx, ly, cx, cy, lt, rt;
        unsigned buttons;
        if (sscanf(line, "%d %x %d %d %d %d %d %d%n", &n, &buttons, &lx, &ly,
                   &cx, &cy, &lt, &rt, &used) < 8)
        {
            break;
        }
        line += used;
        if (n <= 0 || ahead.nsegs == SEGS) {
            return "each pad is held 1 frame or more, 16 pads at most";
        }
        Seg* s = &ahead.segs[ahead.nsegs++];
        s->frames = n;
        s->pad.buttons = (uint16_t) buttons;
        s->pad.lx = (int8_t) lx;
        s->pad.ly = (int8_t) ly;
        s->pad.cx = (int8_t) cx;
        s->pad.cy = (int8_t) cy;
        s->pad.lt = (uint8_t) lt;
        s->pad.rt = (uint8_t) rt;
        s->pad.connected = 1;
        ahead.total += n;
    }
    if (ahead.nsegs == 0) {
        return "no pads";
    }
    if (ahead.total > AHEAD_MAX) {
        ahead.total = AHEAD_MAX;
    }
    a = fighter_of(ahead.port);
    t = fighter_of(ahead.target);
    if (a == NULL || t == NULL) {
        return "no fighter there";
    }
    /* the records to go back with; started again in a process that came
       from a snapshot, whose marks are another process's */
    if (!host_rb_running() || ahead.rb_pid != getpid()) {
        const char* why = host_rb_start();
        if (why != NULL) {
            return why;
        }
        ahead.rb_pid = getpid();
    }
    clock_gettime(CLOCK_MONOTONIC, &ahead.t0);
    host_rb_mark();
    ahead.a_percent0 = a->dmg.x1830_percent;
    ahead.t_percent0 = t->dmg.x1830_percent;
    ahead.played = 0;
    ahead.contact_at = -1;
    ahead.active = 1;
    host.draw = 0; /* undone with the rest */
    host.pads[ahead.port] = *pad_for(0);
    return NULL;
}

static void reply(void)
{
    struct timespec t1;
    double ms;
    clock_gettime(CLOCK_MONOTONIC, &t1);
    ms = (t1.tv_sec - ahead.t0.tv_sec) * 1000.0 +
         (t1.tv_nsec - ahead.t0.tv_nsec) / 1e6;
    printf("@ ok %.3f ", ms);
    for (int i = 0; i < ahead.played; i++) {
        Row* r = &ahead.rows[i];
        printf("%s%d %.3f %.3f %d %.2f %.0f %d %.0f %d %.3f %.3f %d %.2f "
               "%.2f %.0f %.2f %.2f",
               i ? ";" : "", r->a_state, r->a_x, r->a_y, r->a_air,
               r->a_percent, r->a_hitlag, r->a_hitbox, r->a_facing,
               r->t_state, r->t_x, r->t_y, r->t_air, r->t_percent,
               r->t_shield, r->t_hitlag, r->gap, r->gx);
    }
    printf("\n");
    fflush(stdout);
}

/// A frame boundary while a lookahead runs (lb_80019894). Returns 1 when
/// another frame is to be played ahead (its pads are set); 0 when the
/// lookahead is over: the game is back where the command was read and the
/// reply has been printed.
int host_ahead_boundary(void)
{
    Row* row = &ahead.rows[ahead.played];
    record(row);
    ahead.played++;
    if (ahead.contact_at < 0 &&
        (row->t_hitlag > 0 || row->t_percent > ahead.t_percent0 ||
         row->a_percent > ahead.a_percent0))
    {
        ahead.contact_at = ahead.played;
    }
    if (ahead.played < ahead.total &&
        !(ahead.stop > 0 && ahead.contact_at >= 0 &&
          ahead.played >= ahead.contact_at + ahead.stop))
    {
        /* the game's timeline, as host_frame_tick runs it, without what
           happens in real time: the window, the driver, the sound */
        host.int_enabled = 1;
        host_deliver();
        host.frame++;
        host_advance(HOST_TICKS_PER_FRAME);
        host_match_install();
        host_anchor_frame();
        host_rng_frame();
        host.pads[ahead.port] = *pad_for(ahead.played);
        return 1;
    }
    host_rb_mark();
    if (host_rb_rewind(1) < 0) {
        host_fatal("ahead: could not go back");
    }
    ahead.active = 0;
    reply();
    return 0;
}
