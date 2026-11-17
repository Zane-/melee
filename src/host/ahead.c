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
 * A frame played ahead must not end the scene (a match timing out, the
 * pause menu's quit): the scene loop checks its exit flag before it waits
 * for the next frame, and would be in the next scene, its callers' locals
 * with it, by the time the lookahead could be undone. The two functions
 * that set the flag are the host's here (tools/native_build.py renames the
 * game's): while a lookahead runs they only note it, and the lookahead
 * stops at the next boundary.
 *
 * A route ("route PORT TARGET HORIZON N BUTTONS LX LY CX CY L R [N ...]
 * [| N BUTTONS LX LY CX CY L R ...]"): a way back to the stage played
 * ahead, to where it is decided, and undone. PORT plays its pads (the last
 * held on), TARGET the pads after the "|" (the last held on; none: what it
 * holds now), until PORT has caught the ledge, has landed and can act
 * again, is hit or grabbed, is lost (dead, or under the stage's lower
 * blast line), or HORIZON frames have passed. The opponent that recovers
 * (tools/melee_engine/recover.py) asks it of every way back it considers,
 * against what the player is expected to do. The reply:
 * "@ ok MS END FRAME X Y STATE AIR TAKEN LAND FREE NEAR NEAR_AT GAP GAP_AT
 * TOP LOW TX TY TSTATE LEDGE LEDGE_AT": END 0 still in the air at the horizon, 1 the
 * ledge caught, 2 landed and free again, 3 hit (or grabbed), 4 lost;
 * FRAME the frame it was decided on (1 the first played); X Y STATE AIR
 * PORT's then; TAKEN its damage taken; LAND the frame it landed on (0:
 * not), FREE the first frame it could act on the ground (0: not); NEAR
 * the least distance between the two fighters and its frame; GAP the
 * least gap from TARGET's active hitboxes to PORT's hurtboxes, edge to
 * edge (999: none out), and its frame; TOP and LOW the highest and lowest
 * PORT was; TX TY TSTATE the target at the end; LEDGE the least distance
 * PORT came to the ledge on its side of the stage, and its frame (how near
 * a route that fell short came).
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
#include <melee/gr/stage.h>
#include <melee/lb/types.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/gobj.h>

#define AHEAD_MAX 180 /* frames one lookahead may play */
#define ROUTE_MAX 600 /* frames one route may play */
/* frames a route is followed after it landed, for the fighter to be free */
#define ROUTE_LANDED 70
/* a route's end */
enum { ROUTE_AIR, ROUTE_LEDGE, ROUTE_STAGE, ROUTE_HIT, ROUTE_LOST };
/* action states (ftCo_MS_*) a route reads */
#define RS_DEAD_LAST 10
#define RS_WAIT 14
#define RS_WALK_FIRST 15
#define RS_TURN 18
#define RS_DASH 20
#define RS_RUN 21
#define RS_SQUAT_FIRST 39
#define RS_SQUAT_LAST 41
#define RS_LANDING 42
#define RS_LANDING_FALL_SPECIAL 43
#define RS_GUARD_ON 178
#define RS_GUARD 179
#define RS_CAPTURE_FIRST 223
#define RS_CAPTURE_LAST 232
#define RS_CLIFF_CATCH 252
#define RS_CLIFF_WAIT 253
#define RS_CLIFF_LAST 263 /* CliffJumpQuick2: the ledge's own states */
/* pads (segments) one lookahead takes: a body's dash dances and a
   line's L-cancel pulses made more than 16 (behave.stun_over); 48 of them
   fit in the command loop's 2,048 characters with room */
#define SEGS 48
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
    int scene_end;     ///< a frame played ahead asked to end the scene
    float a_percent0, t_percent0;
    Row rows[AHEAD_MAX];
    struct timespec t0;
    pid_t rb_pid;      ///< the process rollback was started in by us
    /* a route ("route ..."): TARGET's pads, and what came of it */
    int route;
    Seg tsegs[SEGS];
    int ntsegs;
    int end, end_at, land_at, free_at, near_at, gap_at;
    int end_state, end_air, t_state;
    float end_x, end_y, taken, near, gap, top, low, t_x, t_y;
    /* the stage's ledges, and the least distance PORT came to the one on
       its side (its frame) */
    float ledge_x[2], ledge_y[2], ledge_d;
    int ledges, ledge_at;
    /* "routep": PORT's place frame by frame, in the reply too */
    int with_path;
    float path_x[ROUTE_MAX], path_y[ROUTE_MAX];
    unsigned char path_i[ROUTE_MAX]; /* intangible or invincible then */
    /* PORT has been off the ledge on this route (it began there: a route
       from the ledge ends on the ledge only once it has left it) */
    int off_ledge;
    /* "hitboxes": PORT's active hitboxes frame by frame, as the reply */
    char hb[32768];
    int hb_len;
} ahead;

int host_ahead_active(void)
{
    return ahead.active;
}

/// Frames are being played ahead, by a lookahead or a search (engine.c):
/// nothing of them is heard or reaches the real-time side.
int host_predicting(void)
{
    return ahead.active || host_engine_active();
}

void gm_801A4B60_vanilla(void);
void gm_801A4B74_vanilla(void);

/// The scene ends (gmscene.c), unless this is a frame played ahead.
void gm_801A4B60(void)
{
    if (ahead.active) {
        ahead.scene_end = 1;
        return;
    }
    if (host_engine_active()) {
        host_engine_note_scene_end();
        return;
    }
    gm_801A4B60_vanilla();
}

void gm_801A4B74(void)
{
    if (ahead.active) {
        ahead.scene_end = 1;
        return;
    }
    if (host_engine_active()) {
        host_engine_note_scene_end();
        return;
    }
    gm_801A4B74_vanilla();
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

/// The pad of `segs` held on frame `n` (past its end: the last one).
static const HostPad* seg_pad(const Seg* segs, int nsegs, int n)
{
    for (int s = 0; s < nsegs; s++) {
        if (n < segs[s].frames) {
            return &segs[s].pad;
        }
        n -= segs[s].frames;
    }
    return &segs[nsegs - 1].pad;
}

/// The pad PORT holds on frame `n` of the lookahead.
static const HostPad* pad_for(int n)
{
    return seg_pad(ahead.segs, ahead.nsegs, n);
}

/// Pads read from `*line` into `segs` ("N BUTTONS LX LY CX CY L R" each),
/// up to a "|" or the line's end; how many, or -1 (too many, a length
/// under 1). `*total`: their frames.
static int read_segs(const char** line, Seg* segs, int* total)
{
    int nsegs = 0, used = 0;
    *total = 0;
    for (;;) {
        int n = 0, lx, ly, cx, cy, lt, rt;
        unsigned buttons;
        Seg* s;
        if (sscanf(*line, "%d %x %d %d %d %d %d %d%n", &n, &buttons, &lx,
                   &ly, &cx, &cy, &lt, &rt, &used) < 8)
        {
            break;
        }
        *line += used;
        if (n <= 0 || nsegs == SEGS) {
            return -1;
        }
        s = &segs[nsegs++];
        memset(&s->pad, 0, sizeof s->pad);
        s->frames = n;
        s->pad.buttons = (uint16_t) buttons;
        s->pad.lx = (int8_t) lx;
        s->pad.ly = (int8_t) ly;
        s->pad.cx = (int8_t) cx;
        s->pad.cy = (int8_t) cy;
        s->pad.lt = (uint8_t) lt;
        s->pad.rt = (uint8_t) rt;
        s->pad.connected = 1;
        *total += n;
    }
    return nsegs;
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
    ahead.route = 0;
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
            return "each pad is held 1 frame or more, 48 pads at most";
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
    ahead.scene_end = 0;
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
static int route_boundary(void);
static int hitboxes_boundary(void);

int host_ahead_boundary(void)
{
    Row* row;
    if (ahead.route == 2) {
        return hitboxes_boundary();
    }
    if (ahead.route) {
        return route_boundary();
    }
    row = &ahead.rows[ahead.played];
    record(row);
    ahead.played++;
    if (ahead.contact_at < 0 &&
        (row->t_hitlag > 0 || row->t_percent > ahead.t_percent0 ||
         row->a_percent > ahead.a_percent0))
    {
        ahead.contact_at = ahead.played;
    }
    if (ahead.played < ahead.total && !ahead.scene_end &&
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

/* ---- a route: a way back to the stage, played to where it is decided ---- */

/// Can a fighter on the ground act (standing, moving, crouching,
/// shielding, or its landing's lag over: ftCo_Landing_IASA, as engine.c's
/// can_act reads it)?
static int ground_free(Fighter* fp)
{
    int m = (int) fp->motion_id;
    if (fp->dmg.x195c_hitlag_frames > 0) {
        return 0;
    }
    if ((m == RS_LANDING || m == RS_LANDING_FALL_SPECIAL) &&
        fp->mv.co.landing.allow_interrupt &&
        fp->cur_anim_frame >= fp->co_attrs.normal_landing_lag)
    {
        return 1;
    }
    return m == RS_WAIT || (m >= RS_WALK_FIRST && m <= RS_TURN) ||
           m == RS_DASH || m == RS_RUN ||
           (m >= RS_SQUAT_FIRST && m <= RS_SQUAT_LAST) || m == RS_GUARD ||
           m == RS_GUARD_ON;
}

/// "route ..." read at a frame boundary (control.c), as host_ahead_begin.
/// `path`: "routep", the reply ends with "|" and PORT's place after each
/// frame and whether it could be hit there, "X Y I" (I: 1 intangible or
/// invincible) joined by ";". A route that begins on the ledge (a getup, a
/// drop and a jump back on) ends on the ledge only once it has left it.
const char* host_route_begin(const char* line, int path)
{
    int used = 0, horizon = 0, total = 0, ttotal = 0;
    Fighter *a, *t;

    ahead.with_path = path;
    if (ahead.active || host_engine_active()) {
        return "a search or lookahead is already running";
    }
    if (host_net_active()) {
        return "not during a netplay session";
    }
    if (sscanf(line, "%d %d %d%n", &ahead.port, &ahead.target, &horizon,
               &used) < 3 ||
        ahead.port < 0 || ahead.port > 3 || ahead.target < 0 ||
        ahead.target > 3 || horizon <= 0)
    {
        return "route PORT TARGET HORIZON N BUTTONS LX LY CX CY L R ... "
               "[| N BUTTONS LX LY CX CY L R ...]";
    }
    line += used;
    ahead.nsegs = read_segs(&line, ahead.segs, &total);
    if (ahead.nsegs <= 0) {
        return "each pad is held 1 frame or more, 48 pads at most";
    }
    ahead.ntsegs = 0;
    while (*line == ' ') {
        line++;
    }
    if (*line == '|') {
        line++;
        ahead.ntsegs = read_segs(&line, ahead.tsegs, &ttotal);
        if (ahead.ntsegs < 0) {
            return "each pad is held 1 frame or more, 48 pads at most";
        }
    }
    ahead.total = horizon > ROUTE_MAX ? ROUTE_MAX : horizon;
    a = fighter_of(ahead.port);
    t = fighter_of(ahead.target);
    if (a == NULL || t == NULL) {
        return "no fighter there";
    }
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
    ahead.scene_end = 0;
    ahead.end = ROUTE_AIR;
    ahead.end_at = ahead.land_at = ahead.free_at = 0;
    ahead.near_at = ahead.gap_at = 0;
    ahead.near = ahead.gap = NO_GAP;
    ahead.top = ahead.low = a->cur_pos.y;
    ahead.ledges = host_ledge_at(0, &ahead.ledge_x[0], &ahead.ledge_y[0]) >=
                       0 &&
                   host_ledge_at(1, &ahead.ledge_x[1], &ahead.ledge_y[1]) >= 0;
    ahead.ledge_d = NO_GAP;
    ahead.ledge_at = 0;
    ahead.off_ledge = !((int) a->motion_id >= RS_CLIFF_CATCH &&
                        (int) a->motion_id <= RS_CLIFF_LAST);
    ahead.taken = 0.0F;
    ahead.route = 1;
    ahead.active = 1;
    host.draw = 0; /* undone with the rest */
    host.pads[ahead.port] = *pad_for(0);
    if (ahead.ntsegs > 0) {
        host.pads[ahead.target] = *seg_pad(ahead.tsegs, ahead.ntsegs, 0);
    }
    return NULL;
}

/// The frame just played, read: 1 while the route is undecided.
static int route_note(void)
{
    Fighter* a = fighter_of(ahead.port);
    Fighter* t = fighter_of(ahead.target);
    int n = ahead.played + 1, m, end = ROUTE_AIR;
    float d, gap, gx;

    if (a == NULL) {
        ahead.end = ROUTE_LOST;
        ahead.end_at = n;
        return 0;
    }
    m = (int) a->motion_id;
    ahead.end_x = a->cur_pos.x;
    ahead.end_y = a->cur_pos.y;
    if (ahead.played < ROUTE_MAX) {
        ahead.path_x[ahead.played] = a->cur_pos.x;
        ahead.path_y[ahead.played] = a->cur_pos.y;
        ahead.path_i[ahead.played] =
            (unsigned char) (a->x1988 != 0 || a->x198C != 0);
    }
    if (!(m >= RS_CLIFF_CATCH && m <= RS_CLIFF_LAST)) {
        ahead.off_ledge = 1;
    }
    ahead.end_state = m;
    ahead.end_air = (int) a->ground_or_air;
    ahead.taken = a->dmg.x1830_percent - ahead.a_percent0;
    if (a->cur_pos.y > ahead.top) {
        ahead.top = a->cur_pos.y;
    }
    if (a->cur_pos.y < ahead.low) {
        ahead.low = a->cur_pos.y;
    }
    if (ahead.ledges) {
        int right = a->cur_pos.x >= 0.0F;
        float dx = a->cur_pos.x - ahead.ledge_x[right];
        float dy = a->cur_pos.y - ahead.ledge_y[right];
        d = sqrtf(dx * dx + dy * dy);
        if (d < ahead.ledge_d) {
            ahead.ledge_d = d;
            ahead.ledge_at = n;
        }
    }
    if (t != NULL) {
        float dx = t->cur_pos.x - a->cur_pos.x;
        float dy = t->cur_pos.y - a->cur_pos.y;
        ahead.t_x = t->cur_pos.x;
        ahead.t_y = t->cur_pos.y;
        ahead.t_state = (int) t->motion_id;
        d = sqrtf(dx * dx + dy * dy);
        if (d < ahead.near) {
            ahead.near = d;
            ahead.near_at = n;
        }
        hit_gap(t, a, &gap, &gx);
        if (gap < ahead.gap) {
            ahead.gap = gap;
            ahead.gap_at = n;
        }
    }
    if (m <= RS_DEAD_LAST ||
        a->cur_pos.y < Stage_GetBlastZoneBottomOffset() + 4.0F)
    {
        end = ROUTE_LOST;
    } else if (ahead.taken > 0.0F ||
               (m >= RS_CAPTURE_FIRST && m <= RS_CAPTURE_LAST))
    {
        end = ROUTE_HIT;
    } else if ((m == RS_CLIFF_CATCH || m == RS_CLIFF_WAIT) &&
               ahead.off_ledge)
    {
        end = ROUTE_LEDGE;
    } else if (a->ground_or_air == GA_Ground) {
        if (ahead.land_at == 0) {
            ahead.land_at = n;
        }
        if (ground_free(a)) {
            ahead.free_at = n;
            end = ROUTE_STAGE;
        } else if (n - ahead.land_at >= ROUTE_LANDED) {
            end = ROUTE_STAGE;
        }
    } else if (ahead.land_at != 0) {
        ahead.land_at = 0; /* off the ground again (slid off, a hop) */
    }
    if (end != ROUTE_AIR) {
        ahead.end = end;
        ahead.end_at = n;
        return 0;
    }
    ahead.end_at = n;
    return 1;
}

static void route_reply(void)
{
    struct timespec t1;
    double ms;
    clock_gettime(CLOCK_MONOTONIC, &t1);
    ms = (t1.tv_sec - ahead.t0.tv_sec) * 1000.0 +
         (t1.tv_nsec - ahead.t0.tv_nsec) / 1e6;
    printf("@ ok %.3f %d %d %.3f %.3f %d %d %.2f %d %d %.2f %d %.2f %d %.2f "
           "%.2f %.3f %.3f %d %.2f %d",
           ms, ahead.end, ahead.end_at, ahead.end_x, ahead.end_y,
           ahead.end_state, ahead.end_air, ahead.taken, ahead.land_at,
           ahead.free_at, ahead.near, ahead.near_at, ahead.gap, ahead.gap_at,
           ahead.top, ahead.low, ahead.t_x, ahead.t_y, ahead.t_state,
           ahead.ledge_d, ahead.ledge_at);
    if (ahead.with_path) {
        int k = ahead.played < ROUTE_MAX ? ahead.played : ROUTE_MAX;
        printf(" |");
        for (int i = 0; i < k; i++) {
            printf("%s%.1f %.1f %d", i ? ";" : "", ahead.path_x[i],
                   ahead.path_y[i], (int) ahead.path_i[i]);
        }
    }
    printf("\n");
    fflush(stdout);
}

/* ---- where a fighter's hitboxes would be ---------------------------------- */

/// "hitboxes PORT FRAMES N BUTTONS LX LY CX CY L R [N ...]": PORT plays
/// its pads (the last held on) for FRAMES frames, the others holding
/// theirs, and the frames are undone. The reply, "@ ok MS ROW;ROW;...":
/// for each frame on which one of its hitboxes was out, "F X Y R [X Y R
/// ...]": the frame (1 the first played) and each active hitbox's two ends
/// (where it is and where it was a frame before: the game sweeps between
/// them) with its radius. What the player could strike, and when
/// (tools/melee_engine/recover.py, `threats`).
const char* host_hitboxes_begin(const char* line)
{
    int used = 0, horizon = 0, total = 0;
    Fighter* a;

    if (ahead.active || host_engine_active()) {
        return "a search or lookahead is already running";
    }
    if (host_net_active()) {
        return "not during a netplay session";
    }
    if (sscanf(line, "%d %d%n", &ahead.port, &horizon, &used) < 2 ||
        ahead.port < 0 || ahead.port > 3 || horizon <= 0)
    {
        return "hitboxes PORT FRAMES N BUTTONS LX LY CX CY L R ...";
    }
    line += used;
    ahead.nsegs = read_segs(&line, ahead.segs, &total);
    if (ahead.nsegs <= 0) {
        return "each pad is held 1 frame or more, 48 pads at most";
    }
    ahead.ntsegs = 0;
    ahead.target = ahead.port;
    ahead.total = horizon > AHEAD_MAX ? AHEAD_MAX : horizon;
    a = fighter_of(ahead.port);
    if (a == NULL) {
        return "no fighter there";
    }
    if (!host_rb_running() || ahead.rb_pid != getpid()) {
        const char* why = host_rb_start();
        if (why != NULL) {
            return why;
        }
        ahead.rb_pid = getpid();
    }
    clock_gettime(CLOCK_MONOTONIC, &ahead.t0);
    host_rb_mark();
    ahead.played = 0;
    ahead.contact_at = -1;
    ahead.scene_end = 0;
    ahead.hb_len = 0;
    ahead.hb[0] = '\0';
    ahead.route = 2;
    ahead.active = 1;
    host.draw = 0; /* undone with the rest */
    host.pads[ahead.port] = *pad_for(0);
    return NULL;
}

/// The frame just played: PORT's active hitboxes, written down.
static void hitboxes_note(void)
{
    Fighter* a = fighter_of(ahead.port);
    int n = ahead.played + 1, any = 0;
    if (a == NULL) {
        return;
    }
    for (int h = 0; h < 4; h++) {
        HitCapsule* hit = &a->x914[h];
        int room = (int) sizeof ahead.hb - ahead.hb_len;
        int w;
        if (hit->state == HitCapsule_Disabled || room < 96) {
            continue;
        }
        if (!any) {
            w = snprintf(ahead.hb + ahead.hb_len, (size_t) room, "%s%d",
                         ahead.hb_len ? ";" : "", n);
            ahead.hb_len += w;
            room -= w;
            any = 1;
        }
        w = snprintf(ahead.hb + ahead.hb_len, (size_t) room,
                     " %.1f %.1f %.1f %.1f %.1f %.1f", hit->x4C.x,
                     hit->x4C.y, hit->scale, hit->x58.x, hit->x58.y,
                     hit->scale);
        ahead.hb_len += w;
    }
}

static int hitboxes_boundary(void)
{
    hitboxes_note();
    ahead.played++;
    if (ahead.played < ahead.total && !ahead.scene_end) {
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
        host_fatal("hitboxes: could not go back");
    }
    ahead.active = 0;
    ahead.route = 0;
    {
        struct timespec t1;
        clock_gettime(CLOCK_MONOTONIC, &t1);
        printf("@ ok %.3f %s\n",
               (t1.tv_sec - ahead.t0.tv_sec) * 1000.0 +
                   (t1.tv_nsec - ahead.t0.tv_nsec) / 1e6,
               ahead.hb);
        fflush(stdout);
    }
    return 0;
}

static int route_boundary(void)
{
    int go = route_note();
    ahead.played++;
    if (go && ahead.played < ahead.total && !ahead.scene_end) {
        host.int_enabled = 1;
        host_deliver();
        host.frame++;
        host_advance(HOST_TICKS_PER_FRAME);
        host_match_install();
        host_anchor_frame();
        host_rng_frame();
        host.pads[ahead.port] = *pad_for(ahead.played);
        if (ahead.ntsegs > 0) {
            host.pads[ahead.target] =
                *seg_pad(ahead.tsegs, ahead.ntsegs, ahead.played);
        }
        return 1;
    }
    host_rb_mark();
    if (host_rb_rewind(1) < 0) {
        host_fatal("route: could not go back");
    }
    ahead.active = 0;
    ahead.route = 0;
    route_reply();
    return 0;
}
