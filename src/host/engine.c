/** @file
 * The search engine: a chess engine's search, on the real game.
 *
 * "search PORT TARGET HORIZON BUDGET DEPTH [KEY=VALUE ...]": from the frame
 * the command is read at, PORT's possible lines of play are tried in the
 * game itself, frame by frame, against TARGET holding what it holds now
 * (or a given input sequence: "engine player ..."), each line scored, and
 * the best line from each first move reported; then the game is put back
 * as it was. docs/ai/melee-engine.md is the design; tools/melee_engine/ the
 * Python side.
 *
 * Lines are made of macros (a dash, a short hop with a nair on the first
 * airborne frame, a forward smash, a shield grab...), each played from the
 * state it starts in and followed until the fighter can act again: a
 * branch point. At a branch point every macro the state allows is tried
 * once, to rank it; the rest of the node's budget (simulated frames) goes
 * to the best of them by halves (half to the best, a quarter to the next),
 * each searched again from its own branch point, deeper, while the horizon
 * and the depth allow. So the search goes deep where it found something,
 * and always ends (4Stockfish's budget split, `melee-engine.md`).
 *
 * Going back: the rollback records (rollback.c). A mark at each branch
 * point, a rewind to return to it; only the pages the frames wrote are
 * copied. The search code is a coroutine with its own stack: it plays a
 * frame by setting the pads and switching back to the game, which runs the
 * frame through its own scene loop and switches back at the next boundary
 * (lb_80019894, main.c). Frames are run as a lookahead's are (ahead.c):
 * undrawn, unheard, never ending the scene.
 *
 * The score of a line, from PORT's side, at its end: damage dealt and
 * taken, a stock taken or lost, place on the stage (centre good, past the
 * ledge bad, hitstun still left bad), the target's hitstun left, holding
 * the target (a grab is worth something before its throw), and the goal
 * terms a drill asks for (contact, on the shield, a spacing).
 *
 * The reply: "@ ok MS TRIALS FRAMES NLINES" and then, per line, best first,
 * "@ line VALUE DMG TAKEN KO CONTACT CONTACT_FRAME ADV POS DIST LEN FIRST
 * AIR STATE NAMES PADS": FIRST the frames of the first move (to where the
 * fighter can act again), AIR 1 if the target was in the air at the first
 * contact, STATE PORT's action state then (what hit: an up smash, a dash
 * attack),
 * NAMES the macros joined by "+", PADS the frames as "N BUTTONS LX LY CX CY
 * L R" segments joined by ",". Then "@ end". KEY=VALUE: the score's
 * weights (dmg taken ko pos adv contact shield hit held close dist),
 * lcancel=0|1, moves=PREFIX,... for the first moves allowed, then=PREFIX,...
 * for the moves allowed after the first (a line made only of a drill's
 * moves), split=N to report the best line from each of the first N moves
 * (by default from each first move; at most LINES_MAX lines), and ms=N to
 * stop after N milliseconds with the best found so far.
 *
 * The timing scan ("scan=STEP"): lines of one shape, [FIRST] + HOLD for K
 * frames + LAST, every K (a multiple of STEP) tried. FIRST one of moves=
 * (a jump; none if moves= is not given or none is possible), HOLD one of
 * hold= (the stick in, none, out, walking in or out; ff_ for a fast fall
 * on the way down), LAST one of then= (an aerial, an up smash). The
 * branch point moves forward along the hold one frame at a time (its
 * rollback records merged into one), so all the timings cost about one
 * playout each. It finds the frames an aerial lands on (a jump-in) or an
 * anti-air meets it, which the macro tree, stepping 6 frames at a time,
 * misses. Its lines are named "FIRST+hold_KIND:K+LAST"; stop=1 ends each
 * at its first contact, trial=N N frames after LAST is pressed, near=D
 * presses only with the fighters within D of each other, from=K only after
 * K frames of the hold, enough=N stops
 * the scan once N lines connect (an answer exists: enough=1), counting only
 * contacts made in one of PORT's action states want=S,S... if given. eval=1 scores
 * the pre-roll ("engine preroll") alone as one line, "plan": what a plan
 * does against the target's inputs as given (the lookahead's question,
 * with "engine player").
 *
 * A forked game ("engine fork IN OUT"): the process forks at the frame
 * boundary, and the copy reads its commands from the pipe IN and replies on
 * OUT, the game standing at that frame for as long as it is asked: searches,
 * lookaheads, the state. It plays no frame for real, draws nothing (the
 * scene loop's render calls are skipped in it: a window's graphics are the
 * game's it was forked from), and leaves when IN closes. The game it came
 * from goes on at once: what the opponent thinks about, it thinks about in
 * the copy, while a person plays (tools/melee_engine/fork.py).
 *
 * This file's statics are not the game's state: what the search found
 * survives its rewinds.
 */
#include "host.h"

#include <fcntl.h>
#include <math.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <ucontext.h>
#include <unistd.h>

#include <melee/ft/inlines.h>
#include <melee/ft/types.h>
#include <melee/lb/types.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/initialize.h>
#include <sysdolphin/baselib/video.h>

#define HORIZON_MAX 600
#define DEPTH_MAX 8
#define PLAYER_MAX 600
#define LINES_MAX 64
#define NAMES_MAX 160
#define STACK_SIZE (512 * 1024)
#define SETTLE_MAX 90 /* frames a macro is followed until its fighter can act */
#define MIN_BUDGET 40 /* a child is searched deeper with at least this many */
/* A move ranked low still gets this much (4Stockfish's reduced budget for
 * late moves): a grab scores little until its throw is found. */
#define REDUCED_BUDGET 160
#define WIDE 12 /* moves of a node searched deeper at most */
#define MARK_COST 8   /* a mark and a rewind cost about as much as 8 frames */

/* buttons (HostPad.buttons, as the protocol's) */
#define B_A 0x0100
#define B_B 0x0200
#define B_X 0x0400
#define B_Z 0x0010
#define B_R 0x0020
#define B_L 0x0040

/* common action states (src/melee/ft/kinds/ftCommon/forward.h) */
#define MS_DEAD_LAST 10
#define MS_WAIT 14
#define MS_WALK_FIRST 15
#define MS_WALK_LAST 17
#define MS_TURN 18
#define MS_DASH 20
#define MS_RUN 21
#define MS_KNEEBEND 24
#define MS_JUMP_FIRST 25
#define MS_FALL_LAST 34
#define MS_SQUAT_FIRST 39
#define MS_SQUAT_LAST 41
#define MS_AIR_ATTACK_FIRST 65
#define MS_AIR_ATTACK_LAST 69
#define MS_GUARD_ON 178
#define MS_GUARD 179
#define MS_GUARD_OFF 180
#define MS_GUARD_STUN 181
#define MS_GUARD_REFLECT 182
#define MS_CATCH_WAIT 216
#define MS_CAPTURE_FIRST 223 /* being held: pulled, waiting, pummelled... */
#define MS_CAPTURE_LAST 228

/* ---- macros ------------------------------------------------------------- */

enum {
    /* on the ground */
    M_WAIT, M_WALK_IN, M_WALK_OUT, M_DASH_IN, M_DASH_OUT, M_JAB, M_FTILT,
    M_UTILT, M_DTILT, M_FSMASH, M_USMASH, M_DSMASH, M_GRAB, M_DASH_ATTACK,
    M_SHIELD, M_DOWN_B, M_NEUTRAL_B, M_SIDE_B, M_UP_B, M_WD_IN, M_WD_OUT,
    M_HOP_IN, M_HOP_OUT,
    /* full hops with no aerial yet (drifting in, none, out): the air's
       moves come next, an aerial pressed when the search finds it lands */
    M_JUMP_IN, M_JUMP, M_JUMP_OUT,
    /* short hops: 5 aerials x (in, none) */
    M_SH_FIRST,
    M_SH_LAST = M_SH_FIRST + 9,
    /* full hops, the aerial at the top: 5 aerials, drifting in */
    M_FH_FIRST,
    M_FH_LAST = M_FH_FIRST + 4,
    /* in the air: 5 aerials x (in, none, out), and moves */
    M_AIR_FIRST,
    M_AIR_LAST = M_AIR_FIRST + 14,
    M_DRIFT_IN, M_DRIFT_OUT, M_DRIFT_NONE, M_FASTFALL, M_DJ_IN, M_DJ_OUT,
    /* in shield */
    M_OOS_GRAB, M_OOS_USMASH, M_OOS_JUMP, M_SPOTDODGE, M_ROLL_IN,
    M_ROLL_OUT, M_SHIELD_HOLD, M_SHIELD_DROP,
    /* holding the target */
    M_THROW_F, M_THROW_B, M_THROW_U, M_THROW_D,
    M_COUNT
};

static const char* const AERIAL_NAME[5] = { "nair", "fair", "bair", "uair",
                                            "dair" };
static const char* const DRIFT_NAME[3] = { "in", "", "out" };

static char macro_names[M_COUNT][24];

static void name_macros(void)
{
    static const char* const fixed[] = {
        "wait", "walk_in", "walk_out", "dash_in", "dash_out", "jab",
        "ftilt", "utilt", "dtilt", "fsmash", "usmash", "dsmash", "grab",
        "dash_attack", "shield", "down_b", "neutral_b", "side_b", "up_b",
        "wavedash_in", "wavedash_out", "hop_in", "hop_out", "jump_in",
        "jump", "jump_out",
    };
    for (int i = 0; i < (int) (sizeof fixed / sizeof *fixed); i++) {
        snprintf(macro_names[i], sizeof macro_names[i], "%s", fixed[i]);
    }
    for (int a = 0; a < 5; a++) {
        for (int d = 0; d < 2; d++) {
            snprintf(macro_names[M_SH_FIRST + a * 2 + d], 24, "sh_%s%s%s",
                     AERIAL_NAME[a], d == 0 ? "_" : "", DRIFT_NAME[d]);
        }
        snprintf(macro_names[M_FH_FIRST + a], 24, "fh_%s_in", AERIAL_NAME[a]);
        for (int d = 0; d < 3; d++) {
            snprintf(macro_names[M_AIR_FIRST + a * 3 + d], 24, "%s%s%s",
                     AERIAL_NAME[a], d == 1 ? "" : "_", DRIFT_NAME[d]);
        }
    }
    static const char* const rest[] = {
        "drift_in", "drift_out", "drift_none", "fastfall", "dj_in", "dj_out",
        "oos_grab", "oos_usmash", "oos_jump", "spotdodge", "roll_in",
        "roll_out", "shield_hold", "shield_drop", "fthrow", "bthrow",
        "uthrow", "dthrow",
    };
    for (int i = 0; i < (int) (sizeof rest / sizeof *rest); i++) {
        snprintf(macro_names[M_DRIFT_IN + i], 24, "%s", rest[i]);
    }
}

/* ---- the search's state (not the game's) -------------------------------- */

typedef struct Weights {
    float dmg, taken, ko, pos, adv, contact, shield, hit, close, dist, held;
} Weights;

typedef struct Line {
    float value;
    float dmg, taken, adv, pos, dist;
    int ko, contact, contact_at, contact_air, contact_state, len;
    int first_len; /* frames of the first move, to its branch point */
    char names[NAMES_MAX];
    HostPad pads[HORIZON_MAX];
} Line;

static struct {
    int active, finished, scene_end, from_root;
    int port, target, horizon, depth_max;
    long budget, spent;
    int trials;
    Weights w;
    int lcancel;
    /* the player's inputs from the root, frame by frame (else held) */
    HostPad player[PLAYER_MAX];
    int nplayer;
    /* PORT's inputs before the search branches (its move still playing
       out: the search is for where that move ends), for the next search */
    HostPad preroll[PLAYER_MAX];
    int npreroll;
    int base; /* frames of pre-roll on the current path */
    /* the current path from the root */
    int t;
    HostPad path[HORIZON_MAX];
    int contact_at[HORIZON_MAX + 1]; /* first contact on the path by t */
    int contact_kind[HORIZON_MAX + 1];
    int contact_air[HORIZON_MAX + 1]; /* the target airborne at it */
    int contact_state[HORIZON_MAX + 1]; /* PORT's action state at it */
    int names[DEPTH_MAX + 1];
    int nnames;
    int first_len; /* frames the current line's first move took */
    unsigned char root_allowed[M_COUNT]; /* first moves allowed */
    unsigned char then_allowed[M_COUNT]; /* the moves after the first */
    double ms_limit; /* stop searching after this long (0: no limit) */
    int out_of_time;
    int marks; /* marks made since the root's, the root's included */
    /* the root */
    float pct_t, pct_a;
    int stocks_t, stocks_a;
    HostPad last; /* PORT's pad on the frame before */
    /* the best line from each first move (from each of its first `split`
       moves), the best LINES_MAX of them */
    Line lines[LINES_MAX];
    int keys[LINES_MAX][DEPTH_MAX];
    int nlines, split;
    /* the timing scan (scan=STEP; 0: the macro tree) */
    int scan_step, scan_first, stop_contact;
    int eval; /* eval=1: score the pre-roll alone, as one line */
    unsigned hold_allowed;
    float near;      /* press only with the fighters this close (0: any) */
    int from;        /* press only from this many frames of hold on */
    int trial;       /* frames a pressed move is followed (0: to the end) */
    int trial_end;   /* the frame the current one stops at (0: none) */
    int enough;      /* stop once this many lines connect (0: never) */
    int connected;
    /* want=S,S...: only a contact with PORT in one of these action states
       counts toward enough (what a drill counts as its answer) */
    int want[16], nwant;
    ucontext_t game, co;
    char* stack;
    struct timespec t0;
} eng;

int host_engine_active(void)
{
    return eng.active;
}

/* ---- a forked game -------------------------------------------------------- */

static int fork_child;
#define FORKS_MAX 16
static pid_t forks[FORKS_MAX];

int host_engine_forked(void)
{
    return fork_child;
}

/* The scene loop's render calls (gmscene.c is built with these names for
   them: tools/native_build.py): none in a forked game. */
void host_scene_start_render(HSD_RenderPass pass)
{
    if (!fork_child) {
        HSD_StartRender(pass);
    }
}

void host_scene_copy_xfb(HSD_RenderPass pass)
{
    if (!fork_child) {
        HSD_VICopyXFBAsync(pass);
    }
}

void GXInvalidateVtxCache(void);
void GXInvalidateTexAll(void);

void host_scene_invalidate_vtx(void)
{
    if (!fork_child) {
        GXInvalidateVtxCache();
    }
}

void host_scene_invalidate_tex(void)
{
    if (!fork_child) {
        GXInvalidateTexAll();
    }
}

/// "engine fork IN OUT": a copy of the game, standing at this frame, that
/// reads commands from IN and replies on OUT. Its pid, here; "@ ok fork"
/// on OUT, there.
static const char* engine_fork(const char* line)
{
    char in[256], out[256];
    static char reply[64];
    pid_t pid;
    int slot = -1;
    if (sscanf(line, "%255s %255s", in, out) != 2) {
        return "engine fork IN OUT";
    }
    if (fork_child) {
        return "a forked game does not fork";
    }
    /* the copies that have left */
    for (int i = 0; i < FORKS_MAX; i++) {
        if (forks[i] > 0 && waitpid(forks[i], NULL, WNOHANG) != 0) {
            forks[i] = 0;
        }
        if (forks[i] == 0 && slot < 0) {
            slot = i;
        }
    }
    if (slot < 0) {
        return "too many forked games";
    }
    fflush(stdout);
    fflush(stderr);
    pid = fork();
    if (pid < 0) {
        return "fork failed";
    }
    if (pid == 0) {
        int r = open(in, O_RDONLY), w = open(out, O_WRONLY);
        if (r < 0 || w < 0) {
            _exit(1);
        }
        dup2(r, 0);
        dup2(w, 1);
        close(r);
        close(w);
        fork_child = 1;
        /* whoever stops it, it goes quietly */
        signal(SIGPIPE, SIG_DFL);
        printf("@ ok fork\n");
        fflush(stdout);
        return "";
    }
    forks[slot] = pid;
    snprintf(reply, sizeof reply, "@ ok %d\n", (int) pid);
    fputs(reply, stdout);
    return "";
}

void host_engine_note_scene_end(void)
{
    eng.scene_end = 1;
}

/* ---- what the search sees ------------------------------------------------- */

static Fighter* fighter_of(int slot)
{
    HSD_GObj* gobj = Player_GetEntity(slot);
    if (gobj == NULL || !host_live_fighter(gobj)) {
        return NULL;
    }
    return GET_FIGHTER(gobj);
}

static float hitstun_of(Fighter* fp)
{
    return fp->x221C_b6 ? *(float*) &fp->mv : 0.0F;
}

static int airborne(Fighter* fp)
{
    return fp->ground_or_air != 0;
}

/// Can it take a new action now (not in hitlag, idle, or its move
/// interruptible)?
static int can_act(Fighter* fp)
{
    int m = (int) fp->motion_id;
    if (fp->dmg.x195c_hitlag_frames > 0) {
        return 0;
    }
    if (fp->allow_interrupt) {
        return 1;
    }
    return m == MS_WAIT || (m >= MS_WALK_FIRST && m <= MS_WALK_LAST) ||
           m == MS_TURN || m == MS_DASH || m == MS_RUN ||
           (m >= MS_JUMP_FIRST && m <= MS_FALL_LAST) ||
           (m >= MS_SQUAT_FIRST && m <= MS_SQUAT_LAST) || m == MS_GUARD ||
           m == MS_CATCH_WAIT;
}

static float toward(void)
{
    Fighter* a = fighter_of(eng.port);
    Fighter* t = fighter_of(eng.target);
    if (a == NULL || t == NULL) {
        return 1.0F;
    }
    return t->cur_pos.x >= a->cur_pos.x ? 1.0F : -1.0F;
}

/// Where a fighter stands, as 4Stockfish scores it: centre stage best, the
/// ledge nothing, past it worse and worse, each frame of hitstun left a
/// little worse, dead worst.
static float place_of(Fighter* fp, float half)
{
    float x = fabsf(fp->cur_pos.x), v;
    if ((int) fp->motion_id <= MS_DEAD_LAST) {
        return -1200.0F;
    }
    if (x <= half) {
        v = 200.0F * (1.0F - x / half);
    } else {
        v = -300.0F - 250.0F * (x - half) / half;
    }
    if (fp->cur_pos.y < -10.0F) {
        v -= 3.0F * (-10.0F - fp->cur_pos.y);
    }
    return v - 4.0F * hitstun_of(fp);
}

static float stage_half(void)
{
    float x = 0, y = 0;
    if (host_left_ledge(&x, &y)) {
        return fabsf(x) > 1.0F ? fabsf(x) : 60.0F;
    }
    return 60.0F;
}

/// The score of the path so far, from PORT's side.
static Line score(void)
{
    Line l;
    Fighter* a = fighter_of(eng.port);
    Fighter* t = fighter_of(eng.target);
    float half = stage_half();
    memset(&l, 0, sizeof l);
    l.len = eng.t - eng.base;
    l.contact = eng.contact_kind[eng.t];
    l.contact_at = eng.contact_at[eng.t];
    l.contact_air = eng.contact_air[eng.t];
    l.contact_state = eng.contact_state[eng.t];
    if (a == NULL || t == NULL) {
        l.value = -1e6F;
        return l;
    }
    l.dmg = t->dmg.x1830_percent - eng.pct_t;
    l.taken = a->dmg.x1830_percent - eng.pct_a;
    l.ko = (Player_GetStocks(eng.target) < eng.stocks_t ||
            (int) t->motion_id <= MS_DEAD_LAST) -
           (Player_GetStocks(eng.port) < eng.stocks_a ||
            (int) a->motion_id <= MS_DEAD_LAST);
    l.adv = hitstun_of(t) - hitstun_of(a);
    l.pos = place_of(a, half) - place_of(t, half);
    l.dist = fabsf(t->cur_pos.x - a->cur_pos.x);
    l.value = eng.w.dmg * l.dmg - eng.w.taken * l.taken + eng.w.ko * l.ko +
              eng.w.adv * l.adv + eng.w.pos * l.pos +
              eng.w.held * ((int) t->motion_id >= MS_CAPTURE_FIRST &&
                            (int) t->motion_id <= MS_CAPTURE_LAST) +
              eng.w.contact * (l.contact == 1 || l.contact == 2 ||
                               l.contact == 4) +
              eng.w.shield * (l.contact == 2) + eng.w.hit * (l.contact == 1);
    if (eng.w.close != 0) {
        l.value -= eng.w.close * fabsf(l.dist - eng.w.dist);
    }
    return l;
}

/* ---- playing frames --------------------------------------------------------- */

/// Run one frame with PORT holding `pad`: back to the game, which plays it
/// and comes back at the next boundary. Returns 0 when the line must stop
/// (horizon, the scene would have ended, a fighter is gone).
static int play(HostPad pad)
{
    Fighter* a;
    Fighter* t;
    if (eng.t >= eng.horizon || eng.scene_end ||
        (eng.trial_end > 0 && eng.t >= eng.trial_end))
    {
        return 0;
    }
    pad.connected = 1;
    /* not drawn; set every frame, after the marks, so that going back to
       the root brings the draw flag back as it was (set before the root's
       mark, a search once left a shadow game undrawn for good: it then
       drew random numbers differently, and fell out of step) */
    host.draw = 0;
    host.pads[eng.port] = pad;
    if (eng.nplayer > 0) {
        host.pads[eng.target] =
            eng.player[eng.t < eng.nplayer ? eng.t : eng.nplayer - 1];
    }
    eng.path[eng.t] = pad;
    eng.last = pad;
    swapcontext(&eng.co, &eng.game);
    /* the frame has been played */
    eng.t++;
    eng.spent++;
    a = fighter_of(eng.port);
    t = fighter_of(eng.target);
    eng.contact_at[eng.t] = eng.contact_at[eng.t - 1];
    eng.contact_kind[eng.t] = eng.contact_kind[eng.t - 1];
    eng.contact_air[eng.t] = eng.contact_air[eng.t - 1];
    eng.contact_state[eng.t] = eng.contact_state[eng.t - 1];
    if (a == NULL || t == NULL) {
        return 0;
    }
    if (eng.contact_kind[eng.t] == 0) {
        int m = (int) t->motion_id;
        if (t->dmg.x1830_percent > eng.pct_t) {
            eng.contact_kind[eng.t] = 1; /* hit */
            eng.contact_at[eng.t] = eng.t;
        } else if (m >= MS_CAPTURE_FIRST && m <= MS_CAPTURE_LAST) {
            eng.contact_kind[eng.t] = 4; /* grabbed */
            eng.contact_at[eng.t] = eng.t;
        } else if (t->dmg.x195c_hitlag_frames > 0 &&
                   m >= MS_GUARD_ON && m <= MS_GUARD_REFLECT)
        {
            eng.contact_kind[eng.t] = 2; /* on the shield */
            eng.contact_at[eng.t] = eng.t;
        }
    }
    if (a->dmg.x1830_percent > eng.pct_a && eng.contact_kind[eng.t] == 0) {
        eng.contact_kind[eng.t] = 3; /* hit first */
        eng.contact_at[eng.t] = eng.t;
    }
    if (eng.contact_at[eng.t] == eng.t && eng.contact_kind[eng.t] != 0) {
        eng.contact_air[eng.t] = airborne(t);
        eng.contact_state[eng.t] = (int) a->motion_id;
    }
    if (eng.stop_contact && eng.contact_kind[eng.t] != 0) {
        return 0; /* the line is decided */
    }
    return !eng.scene_end;
}

static HostPad pad_of(int buttons, int lx, int ly, int cx, int cy, int rt)
{
    HostPad p;
    memset(&p, 0, sizeof p);
    p.buttons = (uint16_t) buttons;
    p.lx = (int8_t) lx;
    p.ly = (int8_t) ly;
    p.cx = (int8_t) cx;
    p.cy = (int8_t) cy;
    p.rt = (uint8_t) rt;
    p.connected = 1;
    return p;
}

static HostPad neutral(void)
{
    return pad_of(0, 0, 0, 0, 0, 0);
}

/// Follow the fighter until it can act again, the stick held at `lx`, L
/// pulsed during an aerial if L-cancelling. 0 if the line must stop.
static int settle(int lx)
{
    for (int i = 0; i < SETTLE_MAX; i++) {
        Fighter* a = fighter_of(eng.port);
        HostPad p;
        int m;
        if (a == NULL) {
            return 0;
        }
        if (i > 0 && can_act(a)) {
            return 1;
        }
        m = (int) a->motion_id;
        p = pad_of(0, airborne(a) ? lx : 0, 0, 0, 0, 0);
        if (eng.lcancel && airborne(a) && m >= MS_AIR_ATTACK_FIRST &&
            m <= MS_AIR_ATTACK_LAST && i % 6 == 3)
        {
            p.buttons |= B_R;
            p.rt = 255;
        }
        if (!play(p)) {
            return 0;
        }
    }
    return 1;
}

/// The aerial's input, `a` 0..4 (nair fair bair uair dair), facing `f`.
static HostPad aerial_pad(int a, float f, int lx)
{
    switch (a) {
    case 0:
        return pad_of(B_A, 0, 0, 0, 0, 0);
    case 1:
        return pad_of(0, lx, 0, (int) (127 * f), 0, 0);
    case 2:
        return pad_of(0, lx, 0, (int) (-127 * f), 0, 0);
    case 3:
        return pad_of(0, lx, 0, 0, 127, 0);
    default:
        return pad_of(0, lx, 0, 0, -127, 0);
    }
}

/// Press one input for a frame, then settle.
static int press(HostPad p)
{
    return play(p) && settle(0);
}

/// A dash needs the stick from the middle: a frame of nothing first if it
/// was held.
static int from_middle(void)
{
    if (eng.last.lx > 20 || eng.last.lx < -20) {
        return play(neutral());
    }
    return 1;
}

static int hold(HostPad p, int frames)
{
    for (int i = 0; i < frames; i++) {
        if (!play(p)) {
            return 0;
        }
    }
    return 1;
}

/// A hop (`full`: held through the squat), drifting `d` (-1 out, 0, 1 in),
/// the aerial `a` (-1: none) on the first airborne frame or at the top.
static int hop(int a, int d, int full)
{
    float t = toward();
    Fighter* me = fighter_of(eng.port);
    float f = me != NULL ? me->facing_dir : t;
    int lx = (int) (d * 127 * t), pressed = a < 0;
    for (int i = 0; i < SETTLE_MAX; i++) {
        Fighter* fp = fighter_of(eng.port);
        HostPad p = pad_of(i < (full ? 9 : 1) ? B_X : 0, lx, 0, 0, 0, 0);
        if (fp == NULL) {
            return 0;
        }
        if (!pressed && airborne(fp) &&
            (!full || fp->self_vel.y <= 0.0F))
        {
            HostPad q = aerial_pad(a, f, lx);
            q.buttons |= p.buttons;
            p = q;
            pressed = 1;
        }
        if (!play(p)) {
            return 0;
        }
        fp = fighter_of(eng.port);
        if (fp == NULL) {
            return 0;
        }
        if (a < 0 && airborne(fp)) {
            return 1; /* a hop with no aerial: on to the air's moves */
        }
        if (pressed && a >= 0 && i > 2) {
            return settle(lx);
        }
    }
    return 1;
}

/// A wavedash toward (`d` 1) or away (-1).
static int wavedash(int d)
{
    float t = toward();
    for (int i = 0; i < 20; i++) {
        Fighter* fp = fighter_of(eng.port);
        HostPad p = pad_of(i == 0 ? B_X : 0, 0, 0, 0, 0, 0);
        if (fp == NULL) {
            return 0;
        }
        if (airborne(fp)) {
            p = pad_of(B_R, (int) (d * 100 * t), -80, 0, 0, 255);
            if (!play(p)) {
                return 0;
            }
            return settle(0);
        }
        if (!play(p)) {
            return 0;
        }
    }
    return settle(0);
}

/// Play macro `m` from where the line is. 0 if the line must stop.
static int run_macro(int m)
{
    float t = toward();
    int in = (int) (127 * t);
    if (m >= M_SH_FIRST && m <= M_SH_LAST) {
        int k = m - M_SH_FIRST;
        return hop(k / 2, k % 2 == 0 ? 1 : 0, 0);
    }
    if (m >= M_FH_FIRST && m <= M_FH_LAST) {
        return hop(m - M_FH_FIRST, 1, 1);
    }
    if (m >= M_AIR_FIRST && m <= M_AIR_LAST) {
        int k = m - M_AIR_FIRST, d = 1 - k % 3;
        Fighter* fp = fighter_of(eng.port);
        float f = fp != NULL ? fp->facing_dir : t;
        int lx = (int) (d * 127 * t);
        return play(aerial_pad(k / 3, f, lx)) && settle(lx);
    }
    switch (m) {
    case M_WAIT:
        return hold(neutral(), 6);
    case M_WALK_IN:
    case M_WALK_OUT:
        return hold(pad_of(0, (int) ((m == M_WALK_IN ? 45 : -45) * t), 0,
                           0, 0, 0),
                    8) &&
               settle(0);
    case M_DASH_IN:
    case M_DASH_OUT:
        return from_middle() &&
               hold(pad_of(0, m == M_DASH_IN ? in : -in, 0, 0, 0, 0), 8) &&
               settle(0);
    case M_JAB:
        return press(pad_of(B_A, 0, 0, 0, 0, 0));
    case M_FTILT:
        return hold(pad_of(0, (int) (50 * t), 0, 0, 0, 0), 3) &&
               press(pad_of(B_A, (int) (50 * t), 0, 0, 0, 0));
    case M_UTILT:
        return hold(pad_of(0, 0, 50, 0, 0, 0), 3) &&
               press(pad_of(B_A, 0, 50, 0, 0, 0));
    case M_DTILT:
        return hold(pad_of(0, 0, -50, 0, 0, 0), 3) &&
               press(pad_of(B_A, 0, -50, 0, 0, 0));
    case M_FSMASH:
        return press(pad_of(0, 0, 0, in, 0, 0));
    case M_USMASH:
        return press(pad_of(0, 0, 0, 0, 127, 0));
    case M_DSMASH:
        return press(pad_of(0, 0, 0, 0, -127, 0));
    case M_GRAB:
        return press(pad_of(B_Z, 0, 0, 0, 0, 0));
    case M_DASH_ATTACK:
        return press(pad_of(B_A, in, 0, 0, 0, 0));
    case M_SHIELD:
        return hold(pad_of(B_R, 0, 0, 0, 0, 255), 8);
    case M_DOWN_B:
        return press(pad_of(B_B, 0, -127, 0, 0, 0));
    case M_NEUTRAL_B:
        return press(pad_of(B_B, 0, 0, 0, 0, 0));
    case M_SIDE_B:
        return press(pad_of(B_B, in, 0, 0, 0, 0));
    case M_UP_B:
        return press(pad_of(B_B, 0, 127, 0, 0, 0));
    case M_WD_IN:
        return wavedash(1);
    case M_WD_OUT:
        return wavedash(-1);
    case M_HOP_IN:
        return hop(-1, 1, 0);
    case M_HOP_OUT:
        return hop(-1, -1, 0);
    case M_JUMP_IN:
        return hop(-1, 1, 1);
    case M_JUMP:
        return hop(-1, 0, 1);
    case M_JUMP_OUT:
        return hop(-1, -1, 1);
    case M_DRIFT_IN:
        return hold(pad_of(0, in, 0, 0, 0, 0), 6);
    case M_DRIFT_OUT:
        return hold(pad_of(0, -in, 0, 0, 0, 0), 6);
    case M_DRIFT_NONE:
        return hold(neutral(), 6);
    case M_FASTFALL: {
        for (int i = 0; i < SETTLE_MAX; i++) {
            Fighter* fp = fighter_of(eng.port);
            if (fp == NULL) {
                return 0;
            }
            if (fp->self_vel.y < 0.0F) {
                return play(pad_of(0, 0, -127, 0, 0, 0)) && settle(0);
            }
            if (!play(neutral())) {
                return 0;
            }
        }
        return 1;
    }
    case M_DJ_IN:
    case M_DJ_OUT:
        return play(pad_of(B_X, m == M_DJ_IN ? in : -in, 0, 0, 0, 0)) &&
               settle(m == M_DJ_IN ? in : -in);
    case M_OOS_GRAB:
        return press(pad_of(B_R | B_A, 0, 0, 0, 0, 255));
    case M_OOS_USMASH:
        return play(pad_of(B_X, 0, 0, 0, 0, 0)) &&
               press(pad_of(0, 0, 0, 0, 127, 0));
    case M_OOS_JUMP:
        return press(pad_of(B_X, 0, 0, 0, 0, 0));
    case M_SPOTDODGE:
        return press(pad_of(B_R, 0, -127, 0, 0, 255));
    case M_ROLL_IN:
        return press(pad_of(B_R, in, 0, 0, 0, 255));
    case M_ROLL_OUT:
        return press(pad_of(B_R, -in, 0, 0, 0, 255));
    case M_SHIELD_HOLD:
        return hold(pad_of(B_R, 0, 0, 0, 0, 255), 6);
    case M_SHIELD_DROP:
        return press(neutral());
    case M_THROW_F:
        return press(pad_of(0, in, 0, 0, 0, 0));
    case M_THROW_B:
        return press(pad_of(0, -in, 0, 0, 0, 0));
    case M_THROW_U:
        return press(pad_of(0, 0, 127, 0, 0, 0));
    case M_THROW_D:
        return press(pad_of(0, 0, -127, 0, 0, 0));
    default:
        return hold(neutral(), 6);
    }
}

/// The macros the fighter's state allows now.
static int moves_for(int* out)
{
    Fighter* a = fighter_of(eng.port);
    int n = 0, m;
    if (a == NULL) {
        return 0;
    }
    m = (int) a->motion_id;
    if (m == MS_CATCH_WAIT) {
        for (int i = M_THROW_F; i <= M_THROW_D; i++) {
            out[n++] = i;
        }
    } else if (m == MS_GUARD || m == MS_GUARD_ON) {
        for (int i = M_OOS_GRAB; i <= M_SHIELD_DROP; i++) {
            out[n++] = i;
        }
    } else if (!can_act(a)) {
        out[n++] = M_WAIT;
    } else if (airborne(a)) {
        for (int i = M_AIR_FIRST; i <= M_DJ_OUT; i++) {
            if ((i == M_DJ_IN || i == M_DJ_OUT) && a->x1968_jumpsUsed >= 2) {
                continue;
            }
            out[n++] = i;
        }
    } else {
        int running = m == MS_DASH || m == MS_RUN;
        for (int i = M_WAIT; i <= M_FH_LAST; i++) {
            if (i == M_DASH_ATTACK && !running) {
                continue;
            }
            if (running && (i == M_JAB || i == M_FTILT || i == M_UTILT ||
                            i == M_DTILT))
            {
                continue; /* out of a run, A is a dash attack */
            }
            out[n++] = i;
        }
    }
    return n;
}

/* ---- the search ------------------------------------------------------------- */

/// Past the search's time limit: what has been found is the answer.
static int out_of_time(void)
{
    struct timespec now;
    if (eng.ms_limit <= 0 || eng.out_of_time) {
        return eng.out_of_time;
    }
    clock_gettime(CLOCK_MONOTONIC, &now);
    if ((now.tv_sec - eng.t0.tv_sec) * 1000.0 +
            (now.tv_nsec - eng.t0.tv_nsec) / 1e6 >
        eng.ms_limit)
    {
        eng.out_of_time = 1;
    }
    return eng.out_of_time;
}

static void mark(void)
{
    host_rb_mark();
    eng.marks++;
}

/// Back to the branch point marked as `at` (marks counted from the root's,
/// 1), `t` frames from the root.
static void back_to(int at, int t)
{
    host_rb_mark();
    eng.marks++;
    if (host_rb_rewind(eng.marks - at) < 0) {
        host_fatal("engine: could not go back %d", eng.marks - at);
    }
    eng.marks = at;
    eng.t = t;
    eng.scene_end = 0;
    eng.last = t > 0 ? eng.path[t - 1] : neutral();
    eng.from_root = at == 1;
    eng.spent += MARK_COST;
}

/// The path so far as a line, named `name` (NULL: its macros joined),
/// kept if it is the best of its key (`key`, DEPTH_MAX numbers) and the
/// table has room or it beats the worst kept.
static void keep_as(Line* l, const int* key, const char* name)
{
    char* s;
    int slot = -1;
    for (int i = 0; i < eng.nlines; i++) {
        if (memcmp(eng.keys[i], key, sizeof eng.keys[i]) == 0) {
            slot = i;
            break;
        }
    }
    if (slot >= 0 && l->value <= eng.lines[slot].value) {
        return;
    }
    if (slot < 0) {
        if (eng.nlines < LINES_MAX) {
            slot = eng.nlines++;
        } else {
            int worst = 0;
            for (int i = 1; i < eng.nlines; i++) {
                if (eng.lines[i].value < eng.lines[worst].value) {
                    worst = i;
                }
            }
            if (l->value <= eng.lines[worst].value) {
                return;
            }
            slot = worst;
        }
        memcpy(eng.keys[slot], key, sizeof eng.keys[slot]);
    }
    s = l->names;
    s[0] = 0;
    if (name != NULL) {
        snprintf(s, NAMES_MAX, "%s", name);
    }
    for (int i = 0; name == NULL && i < eng.nnames; i++) {
        size_t used = strlen(s);
        snprintf(s + used, NAMES_MAX - used, "%s%s", i ? "+" : "",
                 macro_names[eng.names[i]]);
    }
    memcpy(l->pads, eng.path + eng.base, sizeof(HostPad) * (size_t) l->len);
    l->first_len = eng.first_len;
    eng.lines[slot] = *l;
}

/// A line of the tree: its key is its first `split` moves (-1 past the end
/// of a shorter one).
static void keep(Line* l)
{
    int key[DEPTH_MAX];
    for (int i = 0; i < DEPTH_MAX; i++) {
        key[i] = i < eng.split && i < eng.nnames ? eng.names[i] : -1;
    }
    keep_as(l, key, NULL);
}

/// From the branch point marked `at`, `depth` macros deep: try every move
/// once, then search the best deeper with the rest of `budget`. Returns
/// the best score found below.
static float node(int at, int depth, long budget)
{
    int moves[M_COUNT], n = moves_for(moves), t0 = eng.t, order[M_COUNT];
    float val[M_COUNT], best = -1e9F;
    long start = eng.spent, left;

    {
        /* the moves the drill allows here; a fighter that cannot act
           still waits */
        const unsigned char* allowed =
            depth == 0 ? eng.root_allowed : eng.then_allowed;
        int k = 0;
        for (int i = 0; i < n; i++) {
            if (allowed[moves[i]] ||
                (depth > 0 && n == 1 && moves[i] == M_WAIT))
            {
                moves[k++] = moves[i];
            }
        }
        n = k;
    }
    if (n == 0) {
        return score().value;
    }
    for (int i = 0; i < n; i++) {
        Line l;
        if (i > 0 && out_of_time()) {
            n = i; /* the moves ranked so far */
            break;
        }
        if (i > 0) {
            back_to(at, t0);
        }
        eng.names[depth] = moves[i];
        eng.nnames = depth + 1;
        run_macro(moves[i]);
        if (depth == 0) {
            eng.first_len = eng.t - eng.base;
        }
        eng.trials++;
        l = score();
        val[i] = l.value;
        order[i] = i;
        keep(&l);
        if (l.value > best) {
            best = l.value;
        }
    }
    left = budget - (eng.spent - start);
    if (depth + 1 >= eng.depth_max || left < MIN_BUDGET) {
        return best;
    }
    /* the best first */
    for (int i = 1; i < n; i++) {
        int k = order[i], j = i;
        while (j > 0 && val[order[j - 1]] < val[k]) {
            order[j] = order[j - 1];
            j--;
        }
        order[j] = k;
    }
    /* Each of the best (up to WIDE) gets a reduced share first, the rest
       of the budget goes to the best by halves. */
    long wide = left / REDUCED_BUDGET, extra;
    if (wide > WIDE) {
        wide = WIDE;
    }
    if (wide > n) {
        wide = n;
    }
    if (wide == 0) {
        wide = 1;
    }
    extra = left - wide * REDUCED_BUDGET;
    if (extra < 0) {
        extra = 0;
    }
    for (int r = 0; r < wide; r++) {
        int i = order[r];
        long share = (wide == 1 && extra == 0 ? left : REDUCED_BUDGET) +
                     (extra >> (r + 1));
        int child;
        float v;
        if (share < MIN_BUDGET || out_of_time()) {
            break;
        }
        back_to(at, t0);
        eng.names[depth] = moves[i];
        eng.nnames = depth + 1;
        if (!run_macro(moves[i]) || eng.t >= eng.horizon) {
            left -= share;
            continue;
        }
        if (depth == 0) {
            eng.first_len = eng.t - eng.base;
        }
        mark();
        child = eng.marks;
        v = node(child, depth + 1, share);
        if (v > best) {
            best = v;
        }
        left -= share;
    }
    return best;
}

/* ---- the timing scan --------------------------------------------------- */

enum { H_IN, H_NONE, H_OUT, H_WALK_IN, H_WALK_OUT, H_FF_IN, H_FF_NONE,
       H_FF_OUT, H_COUNT };
static const char* const HOLD_NAME[H_COUNT] = {
    "in", "none", "out", "walk_in", "walk_out", "ff_in", "ff_none", "ff_out",
};

/// This frame's pad of hold `h`: the stick toward the target (as it is
/// now), none, or away; walking; ff_: and down once, the first frame the
/// fighter falls (`*ff` then set).
static HostPad hold_pad(int h, int* ff)
{
    static const int lx_of[H_COUNT] = { 127, 0, -127, 45, -45, 127, 0, -127 };
    Fighter* a = fighter_of(eng.port);
    HostPad p = pad_of(0, (int) (lx_of[h] * toward()), 0, 0, 0, 0);
    if (h >= H_FF_IN && !*ff && a != NULL && airborne(a) &&
        a->self_vel.y < 0.0F)
    {
        p.ly = -127;
        *ff = 1;
    }
    return p;
}

static int out_of_budget(void)
{
    return out_of_time() || (eng.budget > 0 && eng.spent > eng.budget) ||
           (eng.enough > 0 && eng.connected >= eng.enough);
}

/// Are the two fighters within `near` of each other (always, with 0)?
static int near_enough(void)
{
    Fighter* a = fighter_of(eng.port);
    Fighter* t = fighter_of(eng.target);
    float dx, dy;
    if (eng.near <= 0.0F) {
        return 1;
    }
    if (a == NULL || t == NULL) {
        return 0;
    }
    dx = a->cur_pos.x - t->cur_pos.x;
    dy = a->cur_pos.y - t->cur_pos.y;
    return dx * dx + dy * dy <= eng.near * eng.near;
}

static void scan(void)
{
    int firsts[M_COUNT], nf = 0, root = eng.marks, t_root = eng.t;
    if (eng.scan_first) {
        int moves[M_COUNT], n = moves_for(moves);
        for (int i = 0; i < n; i++) {
            if (eng.root_allowed[moves[i]]) {
                firsts[nf++] = moves[i];
            }
        }
    }
    if (nf == 0) {
        firsts[nf++] = -1;
    }
    for (int fi = 0; fi < nf && !out_of_budget(); fi++) {
        int f = firsts[fi], at_f, t_f;
        back_to(root, t_root);
        eng.nnames = 0;
        if (f >= 0) {
            eng.names[0] = f;
            eng.nnames = 1;
            if (!run_macro(f)) {
                continue;
            }
        }
        eng.first_len = eng.t - eng.base;
        mark();
        at_f = eng.marks;
        t_f = eng.t;
        for (int h = 0; h < H_COUNT && !out_of_budget(); h++) {
            int at_k = 0, ff = 0, flew = 0;
            if (!(eng.hold_allowed & (1u << h))) {
                continue;
            }
            back_to(at_f, t_f);
            for (int k = 0; eng.t < eng.horizon && !out_of_budget(); k++) {
                Fighter* a = fighter_of(eng.port);
                if (a == NULL) {
                    break;
                }
                if (airborne(a)) {
                    flew = 1;
                } else if (flew) {
                    break; /* landed: nothing more to press in the air */
                }
                if (k >= eng.from && k % eng.scan_step == 0 &&
                    near_enough())
                {
                    int moves[M_COUNT], n = moves_for(moves), t_k, tried = 0;
                    /* the branch point, here: one record from at_f */
                    mark();
                    if (at_k == 0) {
                        at_k = eng.marks;
                    } else {
                        host_rb_merge();
                        eng.marks--;
                    }
                    t_k = eng.t;
                    for (int i = 0; i < n && !out_of_budget(); i++) {
                        int m = moves[i], key[DEPTH_MAX];
                        char name[NAMES_MAX];
                        Line l;
                        if (!eng.then_allowed[m]) {
                            continue;
                        }
                        if (tried++ > 0) {
                            back_to(at_k, t_k);
                        }
                        eng.names[eng.nnames] = m;
                        eng.trial_end = eng.trial > 0 ? eng.t + eng.trial : 0;
                        run_macro(m);
                        eng.trial_end = 0;
                        eng.trials++;
                        l = score();
                        if (l.contact == 1 || l.contact == 2 || l.contact == 4) {
                            int counts = eng.nwant == 0;
                            for (int w = 0; w < eng.nwant; w++) {
                                counts |= l.contact_state == eng.want[w];
                            }
                            eng.connected += counts;
                        }
                        snprintf(name, sizeof name, "%s%shold_%s:%d+%s",
                                 f >= 0 ? macro_names[f] : "",
                                 f >= 0 ? "+" : "", HOLD_NAME[h], k,
                                 macro_names[m]);
                        memset(key, -1, sizeof key);
                        key[0] = f;
                        key[1] = h;
                        key[2] = k;
                        key[3] = m;
                        keep_as(&l, key, name);
                    }
                    if (tried > 0) {
                        back_to(at_k, t_k);
                    }
                }
                if (!play(hold_pad(h, &ff))) {
                    break;
                }
            }
        }
    }
}

static void reply(void)
{
    struct timespec t1;
    int order[LINES_MAX], n = 0;
    double ms;
    clock_gettime(CLOCK_MONOTONIC, &t1);
    ms = (t1.tv_sec - eng.t0.tv_sec) * 1000.0 +
         (t1.tv_nsec - eng.t0.tv_nsec) / 1e6;
    for (int i = 0; i < eng.nlines; i++) {
        int j = n++;
        while (j > 0 && eng.lines[order[j - 1]].value < eng.lines[i].value) {
            order[j] = order[j - 1];
            j--;
        }
        order[j] = i;
    }
    printf("@ ok %.3f %d %ld %d\n", ms, eng.trials, eng.spent, n);
    for (int r = 0; r < n; r++) {
        Line* l = &eng.lines[order[r]];
        printf("@ line %.3f %.2f %.2f %d %d %d %.2f %.2f %.2f %d %d %d %d %s ",
               l->value, l->dmg, l->taken, l->ko, l->contact, l->contact_at,
               l->adv, l->pos, l->dist, l->len, l->first_len,
               l->contact_air, l->contact_state, l->names);
        for (int i = 0; i < l->len;) {
            int j = i;
            while (j < l->len &&
                   memcmp(&l->pads[j], &l->pads[i], sizeof(HostPad)) == 0)
            {
                j++;
            }
            printf("%s%d %x %d %d %d %d %d %d", i ? "," : "", j - i,
                   l->pads[i].buttons, l->pads[i].lx, l->pads[i].ly,
                   l->pads[i].cx, l->pads[i].cy, l->pads[i].lt,
                   l->pads[i].rt);
            i = j;
        }
        printf("\n");
    }
    printf("@ end\n");
    fflush(stdout);
}

static void search_main(void)
{
    Fighter* a = fighter_of(eng.port);
    Fighter* t = fighter_of(eng.target);
    eng.pct_a = a->dmg.x1830_percent;
    eng.pct_t = t->dmg.x1830_percent;
    eng.stocks_a = Player_GetStocks(eng.port);
    eng.stocks_t = Player_GetStocks(eng.target);
    eng.last = host.pads[eng.port];
    eng.t = 0;
    eng.contact_at[0] = 0;
    eng.contact_kind[0] = 0;
    eng.contact_air[0] = 0;
    eng.contact_state[0] = 0;
    eng.marks = 0;
    eng.base = 0;
    mark(); /* the root: 1 */
    eng.from_root = 1;
    if (eng.npreroll > 0) {
        /* PORT's move still playing out first; the branching starts where
           it ends */
        int ok = 1;
        for (int i = 0; i < eng.npreroll && ok; i++) {
            ok = play(eng.preroll[i]);
        }
        eng.npreroll = 0;
        if (eng.eval) {
            /* a plan, scored as it is (against the target's inputs as
               given): "plan" */
            int key[DEPTH_MAX];
            Line l;
            eng.base = 0;
            eng.first_len = eng.t;
            l = score();
            memset(key, -1, sizeof key);
            keep_as(&l, key, "plan");
        } else if (ok) {
            eng.base = eng.t;
            mark();
            if (eng.scan_step > 0) {
                scan();
            } else {
                node(eng.marks, 0, eng.budget);
            }
        }
    } else if (eng.scan_step > 0) {
        scan();
    } else {
        node(1, 0, eng.budget);
    }
    back_to(1, 0);
    reply();
    eng.finished = 1;
    /* returns to eng.game (uc_link) */
}

/// "KEY=VALUE" in `line`, KEY a word of its own: "shield" is not found in
/// "moves=shield_hold" (it once was, and its weight then ignored).
static float parse_weight(const char* line, const char* key, float def)
{
    size_t n = strlen(key);
    float v = def;
    for (const char* p = strstr(line, key); p != NULL;
         p = strstr(p + 1, key))
    {
        if ((p == line || p[-1] == ' ') && p[n] == '=') {
            sscanf(p + n + 1, "%f", &v);
            break;
        }
    }
    return v;
}

/// "KEY=PREFIX,PREFIX...": the macros whose names start with one of them
/// into `allowed`; with no KEY, all of them.
static void parse_moves(const char* line, const char* key,
                        unsigned char* allowed)
{
    const char* m = NULL;
    size_t n = strlen(key);
    for (const char* p = strstr(line, key); p != NULL;
         p = strstr(p + 1, key))
    {
        if ((p == line || p[-1] == ' ') && p[n] == '=') {
            m = p + n + 1;
            break;
        }
    }
    memset(allowed, m == NULL, M_COUNT);
    if (m != NULL) {
        char list[512];
        sscanf(m, "%511s", list);
        for (char* tok = strtok(list, ","); tok != NULL;
             tok = strtok(NULL, ","))
        {
            for (int i = 0; i < M_COUNT; i++) {
                if (strncmp(macro_names[i], tok, strlen(tok)) == 0) {
                    allowed[i] = 1;
                }
            }
        }
    }
}

/// "search ..." read at a frame boundary (control.c). NULL when the
/// search is under way: the command loop lets the frame go; the reply
/// comes when it is over and undone. Else why not.
const char* host_engine_begin(const char* line)
{
    int used = 0;
    Fighter *a, *t;
    if (eng.active || host_ahead_active()) {
        return "a search or lookahead is already running";
    }
    if (host_net_active()) {
        return "not during a netplay session";
    }
    if (macro_names[0][0] == 0) {
        name_macros();
    }
    if (sscanf(line, "%d %d %d %ld %d%n", &eng.port, &eng.target,
               &eng.horizon, &eng.budget, &eng.depth_max, &used) < 5 ||
        eng.port < 0 || eng.port > 3 || eng.target < 0 || eng.target > 3)
    {
        return "search PORT TARGET HORIZON BUDGET DEPTH [KEY=VALUE ...]";
    }
    line += used;
    if (eng.horizon > HORIZON_MAX) {
        eng.horizon = HORIZON_MAX;
    }
    if (eng.depth_max > DEPTH_MAX) {
        eng.depth_max = DEPTH_MAX;
    }
    eng.w.dmg = parse_weight(line, "dmg", 1.0F);
    eng.w.taken = parse_weight(line, "taken", 1.2F);
    eng.w.ko = parse_weight(line, "ko", 1000.0F);
    eng.w.pos = parse_weight(line, "pos", 0.05F);
    eng.w.adv = parse_weight(line, "adv", 0.5F);
    eng.w.contact = parse_weight(line, "contact", 0.0F);
    eng.w.shield = parse_weight(line, "shield", 0.0F);
    eng.w.hit = parse_weight(line, "hit", 0.0F);
    eng.w.close = parse_weight(line, "close", 0.0F);
    eng.w.dist = parse_weight(line, "dist", 0.0F);
    /* holding the target: what a grab is worth before its throw */
    eng.w.held = parse_weight(line, "held", 20.0F);
    eng.lcancel = (int) parse_weight(line, "lcancel", 1.0F);
    /* "split=2": the best line from each pair of first moves */
    eng.split = (int) parse_weight(line, "split", 1.0F);
    if (eng.split < 1) {
        eng.split = 1;
    }
    if (eng.split > DEPTH_MAX) {
        eng.split = DEPTH_MAX;
    }
    /* "ms=N": stop after N milliseconds, with what has been found */
    eng.ms_limit = parse_weight(line, "ms", 0.0F);
    eng.out_of_time = 0;
    /* "moves=dash_,sh_,wait": the first moves allowed, by name prefix;
       "then=...": the moves after them */
    parse_moves(line, "moves", eng.root_allowed);
    parse_moves(line, "then", eng.then_allowed);
    /* the timing scan: "scan=STEP hold=in,none stop=1" */
    eng.scan_step = (int) parse_weight(line, "scan", 0.0F);
    eng.stop_contact = (int) parse_weight(line, "stop", 0.0F);
    eng.eval = (int) parse_weight(line, "eval", 0.0F);
    eng.scan_first = strstr(line, "moves=") != NULL;
    eng.near = parse_weight(line, "near", 0.0F);
    eng.from = (int) parse_weight(line, "from", 0.0F);
    eng.trial = (int) parse_weight(line, "trial", 0.0F);
    eng.enough = (int) parse_weight(line, "enough", 0.0F);
    eng.nwant = 0;
    {
        const char* w = strstr(line, " want=");
        if (w != NULL) {
            const char* p = w + 6;
            int v, used = 0;
            while (eng.nwant < 16 && sscanf(p, "%d%n", &v, &used) == 1) {
                eng.want[eng.nwant++] = v;
                p += used;
                if (*p != ',') {
                    break;
                }
                p++;
            }
        }
    }
    eng.connected = 0;
    eng.trial_end = 0;
    eng.hold_allowed = (1u << H_IN) | (1u << H_NONE);
    {
        const char* h = strstr(line, "hold=");
        if (h != NULL) {
            char list[256];
            eng.hold_allowed = 0;
            sscanf(h + 5, "%255s", list);
            for (char* tok = strtok(list, ","); tok != NULL;
                 tok = strtok(NULL, ","))
            {
                for (int i = 0; i < H_COUNT; i++) {
                    if (strcmp(HOLD_NAME[i], tok) == 0) {
                        eng.hold_allowed |= 1u << i;
                    }
                }
            }
        }
    }
    a = fighter_of(eng.port);
    t = fighter_of(eng.target);
    if (a == NULL || t == NULL) {
        return "no fighter there";
    }
    {
        /* (in a process restored from a snapshot it starts over) */
        const char* why = host_rb_start();
        if (why != NULL) {
            return why;
        }
    }
    if (eng.stack == NULL) {
        eng.stack = malloc(STACK_SIZE);
    }
    eng.nlines = 0;
    eng.trials = 0;
    eng.spent = 0;
    eng.finished = 0;
    eng.scene_end = 0;
    clock_gettime(CLOCK_MONOTONIC, &eng.t0);
    getcontext(&eng.co);
    eng.co.uc_stack.ss_sp = eng.stack;
    eng.co.uc_stack.ss_size = STACK_SIZE;
    eng.co.uc_link = &eng.game;
    makecontext(&eng.co, search_main, 0);
    eng.active = 1;
    swapcontext(&eng.game, &eng.co);
    /* the first frame's rest of the boundary comes as usual
       (host_frame_tick_rest) */
    eng.from_root = 0;
    if (eng.finished) {
        eng.active = 0; /* nothing was played; the reply is out */
    }
    return NULL;
}

/// Whether "search" left frames to play (so the command loop lets one go).
int host_engine_playing(void)
{
    return eng.active && !eng.finished;
}

/// A frame boundary while a search runs (lb_80019894). 1 when another
/// frame is to be played (its pads are set); 0 when the search is over:
/// the game is back where the command was read and the reply printed.
int host_engine_boundary(void)
{
    /* the game's timeline, as host_frame_tick runs it, without what
       happens in real time */
    host.int_enabled = 1;
    host_deliver();
    host.frame++;
    host_advance(HOST_TICKS_PER_FRAME);
    host_match_install();
    host_anchor_frame();
    host_rng_frame();
    swapcontext(&eng.game, &eng.co);
    if (eng.finished) {
        eng.active = 0;
        return 0;
    }
    if (eng.from_root) {
        /* back at the root, which is part-way through its boundary: the
           rest of it comes first, as it did the first time */
        eng.from_root = 0;
        host_anchor_frame();
        host_rng_frame();
    }
    return 1;
}

/// "engine player N BUTTONS LX LY CX CY L R ...": the target's inputs for
/// the next searches, frame by frame from the root ("engine player" alone:
/// it holds its pad). "engine preroll ...": PORT's inputs for the next
/// search's first frames, before it branches (the move it is still
/// playing); lines then start where they end.
const char* host_engine_command(const char* line)
{
    char what[16] = "";
    int used = 0;
    sscanf(line, "%15s%n", what, &used);
    line += used;
    if (strcmp(what, "player") == 0 || strcmp(what, "preroll") == 0) {
        int pre = what[1] == 'r';
        HostPad* out = pre ? eng.preroll : eng.player;
        int* count = pre ? &eng.npreroll : &eng.nplayer;
        *count = 0;
        for (;;) {
            int n = 0, lx, ly, cx, cy, lt, rt;
            unsigned buttons;
            if (sscanf(line, "%d %x %d %d %d %d %d %d%n", &n, &buttons, &lx,
                       &ly, &cx, &cy, &lt, &rt, &used) < 8)
            {
                break;
            }
            line += used;
            for (int i = 0; i < n && *count < PLAYER_MAX; i++) {
                HostPad* p = &out[(*count)++];
                p->buttons = (uint16_t) buttons;
                p->lx = (int8_t) lx;
                p->ly = (int8_t) ly;
                p->cx = (int8_t) cx;
                p->cy = (int8_t) cy;
                p->lt = (uint8_t) lt;
                p->rt = (uint8_t) rt;
                p->connected = 1;
            }
        }
        return NULL;
    }
    if (strcmp(what, "fork") == 0) {
        return engine_fork(line);
    }
    if (strcmp(what, "macros") == 0) {
        if (macro_names[0][0] == 0) {
            name_macros();
        }
        printf("@ ok");
        for (int i = 0; i < M_COUNT; i++) {
            printf(" %s", macro_names[i]);
        }
        printf("\n");
        return "";
    }
    return "engine player ... | engine preroll ... | engine macros | "
           "engine fork IN OUT";
}
