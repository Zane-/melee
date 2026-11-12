/*
 * Course engine: the event unit that runs any course drill.
 * See course.h and docs/ai/training-courses.md.
 *
 * Per attempt: Reset() picks a scenario (the drill's opponent deck), brings
 * in that CPU character and calls the drill's Setup; then the drill's Think
 * runs every frame until it calls course_Result (counted) or course_Retry
 * (not counted: the setup failed, not the player); the result shows for the
 * reset delay; repeat.
 *
 * Controls in the match: D-pad left/right = previous/next scenario,
 * D-pad down = reset now. Pause for the options.
 *
 * Extracted from src/tmce/events/shineoos/event.c, which stays as the
 * standalone event it was until the hub replaces the event pages.
 */
#include "course.h"
#include <stddef.h>

#define MSG_KIND 0x4352 /* unique id; a new message replaces our last */
/* Player 1's message area. TM-CE looks the queue up as a player slot, so
 * MSGQUEUE_GENERAL (6) asserts in Player_GetPtrForSlot. */
#define MSG_QUEUE 0

#define MAX_SCENARIOS 32
#define MAX_OPTIONS 24
#define MAX_DRILL_OPTIONS 12

/* ---- what a drill sees ------------------------------------------------- */

typedef struct CourseCtx {
    GOBJ* hmn;
    GOBJ* cpu;
    FighterData* hd;
    FighterData* cd;
    int phase;    ///< the drill's own phase; 0 after every reset
    int timer;    ///< frames in the current phase (1 on its first Think)
    int scenario; ///< deck index, 0 without a deck
    const TmRotEntry* entry; ///< deck entry of the scenario, or NULL
    float side;   ///< +1: the CPU is on the player's right, -1: left
    float toward; ///< +1/-1: the player's direction seen from the CPU
    int hmn_hit;  ///< the player took damage this frame
    int cpu_hit;  ///< the CPU took damage this frame
    /* The player at the end of the previous frame, sampled after every
     * fighter proc has run (Sample). Think itself runs part-way through the
     * fighter's frame: read there, a state entered by an input or a landing
     * shows up a frame later than one entered by an animation ending, and
     * frame counts between the two come out one off. Count frames with
     * these, not with hd->state_id. */
    int state;        ///< action state
    int prev_state;   ///< the state before that one
    int state_frames; ///< frames in `state` (1 = entered that frame)
    int held;         ///< buttons held that frame
    int down;         ///< buttons pressed that frame
    int cpu_state;    ///< the CPU's action state, sampled the same way
} CourseCtx;

/* The inputs that solve a drill, relative to marks: moments of an attempt
 * the drill announces with course_Mark (mark 0 is the attempt's first
 * frame). One script, three uses: the demonstration, the guide's timeline,
 * and the automated proof that the drill can be won (a test build plays it
 * and expects a success).
 *
 * A demonstration runs the attempt twice with the same random numbers:
 * first only the mark-0 inputs (the player's part of the setup, like
 * holding shield) to see on which frames the marks fall, then everything,
 * each input placed against its mark's frame. That is how an input can
 * land on the exact frame of something the drill only observes a frame
 * later, and why `frame` may be negative. */
#define COURSE_REF_END 0xFF
#define COURSE_REF_LEAD 3 /* neutral frames before the script starts */
#define COURSE_MAX_MARKS 8
typedef struct CourseRefInput {
    u8 mark;     ///< COURSE_REF_END ends the list
    s16 frame;   ///< frames after the mark
    u16 hold;    ///< frames held (0 = 1)
    s8 lx, ly;   ///< main stick, -127..127, X toward the opponent
    s8 cx, cy;   ///< C-stick
    u16 buttons; ///< PAD_BUTTON_* | PAD_TRIGGER_*
    u8 trigger;  ///< analog R, 0..140
    s8 js;       ///< `frame` is this many jump squats later (the player's)
} CourseRefInput;

/* What the guide overlay shows for a drill. The drill fills the text (with
 * numbers from the generated frame data table, not typed in); the engine
 * adds the input timeline from the reference script and the controls. */
#define COURSE_GUIDE_LINES 8
#define COURSE_GUIDE_COLS 60
typedef struct CourseGuide {
    char line[COURSE_GUIDE_LINES][COURSE_GUIDE_COLS];
    int line_count;
    /// Caption of the timeline: what frame 0 of it is.
    const char* timeline_from;
    /// No timeline: the reference is a stick motion, not button presses.
    int hide_timeline;
} CourseGuide;

typedef struct CourseDrill {
    /// Once per match, before the first attempt.
    void (*Init)(void);
    /// Place the fighters for an attempt and reset the drill's own state.
    void (*Setup)(CourseCtx* c);
    /// Every frame of an attempt.
    void (*Think)(CourseCtx* c);
    /// The drill's own options, shown after the common ones.
    EventOption* options;
    int option_count;
    /// Up to three lines for the HELP entry of the pause menu.
    const char* help[3];
    /// The inputs that solve it (see CourseRefInput), or NULL.
    const CourseRefInput* reference;
    /// Fill the guide overlay's text for the current attempt, or NULL.
    void (*Guide)(CourseCtx* c, CourseGuide* g);
    /// Instead of `reference`: build the script for this attempt (called
    /// after Setup). For scripts that depend on the character or change
    /// from one demonstration to the next (course_DemoCount).
    const CourseRefInput* (*BuildReference)(CourseCtx* c);
    /// The reference's marked inputs all come after their mark (frame >= 1)
    /// and can be played in the attempt that announces it: no observing
    /// pass.
    int live_marks;
    /// A result does not end the attempt: it is counted and shown, and the
    /// drill starts again from phase 0 where the player stands. For
    /// technique practice, where being put back after every try breaks the
    /// rhythm. D-pad down still resets.
    int flow;
} CourseDrill;

/* Engine services for drills. */
static void course_Phase(CourseCtx* c, int phase);
static void course_Place(CourseCtx* c, float hmn_x, float cpu_x,
                         int cpu_faces_away, float cpu_percent);
static void course_PlaceSolo(CourseCtx* c, float x);
static void course_CpuShield(CourseCtx* c);
static void course_PlaceOnLedge(CourseCtx* c);
static void course_PlaceOnPlatform(CourseCtx* c, float x, float above_y);
static int course_Fell(CourseCtx* c);
static int course_DemoCount(void);
static int course_IsDemo(void);
static int course_Leniency(int option);
static void course_Script(CourseCtx* c, const CourseInput* in, int frame);
static void course_Message(int color, char* fmt, const char* a, int b,
                           int c);
static void course_Mark(CourseCtx* c, int mark);
static void course_Measure(int measured, int target);
static void course_Report(const char* key, int value);
static void course_ReportF(const char* key, float value);
static void course_Result(CourseCtx* c, int success, char* fmt, int a,
                          int b);
static void course_Retry(CourseCtx* c, char* fmt);

/* ---- options ------------------------------------------------------------ */

void Event_Exit(GOBJ* menu);
static void OnScenarioChange(GOBJ* menu, int value);

enum {
    OPT_SCENARIO,
    OPT_SWITCH,
    OPT_SIDE,
    OPT_RESET_DELAY,
    OPT_DEMO,
    OPT_COMMON_COUNT, /* the drill's options start here */
};

enum { DEMO_OFF, DEMO_ONCE, DEMO_ALWAYS };

enum { SWITCH_EVERY, SWITCH_ON_SUCCESS, SWITCH_MANUAL };
enum { SIDE_RANDOM, SIDE_LEFT, SIDE_RIGHT };

static const char* scenario_names[MAX_SCENARIOS + 1] = { "Random" };
static const char* opt_switch[] = { "Every Attempt", "On Success",
                                    "Manual (D-Pad)" };
static const char* opt_side[] = { "Random", "Left", "Right" };
static const char* opt_reset_delay[] = { "Fast", "Normal", "Slow" };
static const int reset_delay_frames[] = { 20, 45, 90 };
static const char* opt_demo[] = { "Off", "Show Once", "Keep Showing" };

/* For drills graded on frames: how many frames late still counts. A drill
 * puts COURSE_OPT_LENIENCY in its options and reads it with
 * course_Leniency(index of that option). */
static const char* opt_leniency[] = { "Frame Perfect", "1 Frame", "2 Frames",
                                      "4 Frames" };
static const int leniency_frames[] = { 0, 1, 2, 4 };
#define COURSE_OPT_LENIENCY                                                   \
    {                                                                         \
        .kind = OPTKIND_STRING, .value_num = countof(opt_leniency), .val = 2, \
        .name = "Leniency",                                                   \
        .desc = { "How many frames late still counts as a success." },        \
        .values = opt_leniency,                                               \
    }

static EventOption Options_Common[OPT_COMMON_COUNT] = {
    {
        .kind = OPTKIND_STRING,
        .value_num = 1, /* set in Event_Init from the deck */
        .name = "Scenario",
        .desc = { "Practice one scenario, or a random mix.",
                  "D-Pad left/right cycles in the match." },
        .values = scenario_names,
        .OnChange = OnScenarioChange,
    },
    {
        .kind = OPTKIND_STRING,
        .value_num = countof(opt_switch),
        .name = "Switch Scenario",
        .desc = { "When a random mix moves on to the next scenario." },
        .values = opt_switch,
    },
    {
        .kind = OPTKIND_STRING,
        .value_num = countof(opt_side),
        .name = "CPU Side",
        .desc = { "Which side of you the CPU starts on." },
        .values = opt_side,
    },
    {
        .kind = OPTKIND_STRING,
        .value_num = countof(opt_reset_delay),
        .val = 1,
        .name = "Reset Delay",
        .desc = { "How long the result shows before the next attempt." },
        .values = opt_reset_delay,
    },
    {
        .kind = OPTKIND_STRING,
        .value_num = countof(opt_demo),
        .name = "Demonstration",
        .desc = { "The game plays the drill for you: first the",
                  "situation, then the answer. Not counted." },
        .values = opt_demo,
    },
};

/* Common options, the drill's, HELP and Exit: filled in Event_Init. */
static EventOption Options_Main[MAX_OPTIONS];

/* option_num is the real count from Event_Init on. Before the first match
 * it is the capacity, so a test build can store option values by index
 * (tmce_test_SetOption) before the menu exists. */
static EventMenu Menu_Main = {
    .name = "Course Drill",
    .option_num = MAX_OPTIONS,
    .options = Options_Main,
};

EventMenu* Event_Menu = &Menu_Main;

/* ---- state -------------------------------------------------------------- */

typedef struct Stats {
    u16 attempts;
    u16 successes;
    u16 streak;
    u16 best_streak;
    s32 error_sum; ///< sum of |measured - target| over measured attempts
    u16 measured;
} Stats;

enum { RUN_ATTEMPT, RUN_RESULT, RUN_GUIDE };

static struct {
    const CourseDrillInfo* info;
    const CourseDrill* drill;
    const TmRotDeck* deck;
    CourseCtx ctx;
    int run;          /* RUN_ATTEMPT / RUN_RESULT */
    int result_timer; /* frames left of RUN_RESULT */
    int last_success;
    float hmn_percent;
    float cpu_percent;
    int has_measure;
    int measured;
    int target;
    int attempt_frame; /* Thinks since the attempt's reset (0 = first) */
    int marks[COURSE_MAX_MARKS]; /* attempt_frame of each mark, -1 = not yet */
    int demo;          /* 0 = off, 1 = observing pass, 2 = playing pass */
    int demo_marks[COURSE_MAX_MARKS]; /* from the observing pass */
    u32 demo_seed;     /* RNG seed both passes start from */
    int demo_scenario;
    int demo_count;    /* demonstrations started so far */
    const CourseRefInput* ref; /* this attempt's reference script, or NULL */
    CourseGuide guide;  /* text of the open guide (run == RUN_GUIDE) */
    char report[160]; /* extra JSON fields of the current attempt */
    int report_len;
    Stats total;
    Stats stats[MAX_SCENARIOS];
} en;

/* ---- frame data ---------------------------------------------------------- */

#include "gen/framedata.inc.h"

/* The player's or CPU's numbers, by the fighter in the match. */
static const CourseFighterData* course_Fighter(FighterData* fd)
{
    int kind = fd->kind;
    if (kind < 0 || kind >= (int) countof(course_fd)) {
        kind = 0;
    }
    return &course_fd[kind];
}

/* ---- drills ------------------------------------------------------------- */

/* Drills are headers by name only (`.inc.h`): the build rechecks units when
 * a header changes, and would miss an edit to an included .c file. */
#include "drills/fox_shine_oos.inc.h"
#include "drills/tech_short_hop.inc.h"
#include "drills/tech_wavedash.inc.h"
#include "drills/fox_shine_tech.inc.h"
#include "drills/tech_movement.inc.h"
#include "drills/fox_specials.inc.h"
#include "drills/fox_pressure.inc.h"
#include "drills/tech_ledge.inc.h"
#include "drills/fox_neutral.inc.h"
#include "drills/fox_neutral_reads.inc.h"

static const CourseDrill* const drills[DRILL_COUNT] = {
    [DRILL_FOX_SHINE_OOS] = &Drill_FoxShineOos,
    [DRILL_TECH_SHORT_HOP] = &Drill_TechShortHop,
    [DRILL_TECH_WAVEDASH] = &Drill_TechWavedash,
    [DRILL_TECH_L_CANCEL] = &Drill_TechLCancel,
    [DRILL_TECH_SHFFL] = &Drill_TechShffl,
    [DRILL_TECH_DASH_DANCE] = &Drill_TechDashDance,
    [DRILL_TECH_JC_GRAB] = &Drill_TechJcGrab,
    [DRILL_FOX_WAVESHINE] = &Drill_FoxWaveshine,
    [DRILL_FOX_JC_SHINE] = &Drill_FoxJcShine,
    [DRILL_FOX_MULTISHINE] = &Drill_FoxMultishine,
    [DRILL_FOX_SHINE_GRAB] = &Drill_FoxShineGrab,
    [DRILL_FOX_NAIR_SHINE] = &Drill_FoxNairShine,
    [DRILL_FOX_WHIFF_PUNISH] = &Drill_FoxWhiffPunish,
    [DRILL_FOX_WAVEDASH_BACK] = &Drill_FoxWavedashBack,
    [DRILL_FOX_ANTI_AIR] = &Drill_FoxAntiAir,
    [DRILL_FOX_SHIELD_THEN_PUNISH] = &Drill_FoxShieldThenPunish,
    [DRILL_FOX_APPROACH] = &Drill_FoxApproach,
    [DRILL_FOX_RUNNING_SHINE] = &Drill_FoxRunningShine,
    [DRILL_FOX_LASER_FORCING] = &Drill_FoxLaserForcing,
    [DRILL_FOX_VS_CROUCH_CANCEL] = &Drill_FoxVsCrouchCancel,
    [DRILL_FOX_SHDL] = &Drill_FoxShdl,
    [DRILL_TECH_SHIELD_DROP] = &Drill_TechShieldDrop,
    [DRILL_TECH_LEDGEDASH] = &Drill_TechLedgedash,
    [DRILL_FOX_LEDGE_STALL] = &Drill_FoxLedgeStall,
    [DRILL_FOX_ILLUSION_SHORTEN] = &Drill_FoxIllusionShorten,
};

/* ---- engine ------------------------------------------------------------- */

static int ScenarioCount(void)
{
    int n = en.deck != NULL ? en.deck->count : 1;
    return n > MAX_SCENARIOS ? MAX_SCENARIOS : n;
}

static int ScenarioUsable(int i)
{
    return en.deck != NULL ? tm_rot_IsUsable(i) : i == 0;
}

static int NextScenario(int previous)
{
    return en.deck != NULL ? tm_rot_Next(previous) : 0;
}

static const char* ScenarioName(int i)
{
    return en.deck != NULL ? en.deck->entries[i].name : en.info->name;
}

static void course_Message(int color, char* fmt, const char* a, int b, int c)
{
    event_vars->Message_Display(MSG_KIND, MSG_QUEUE, color, fmt, a, b, c);
}

static void course_Phase(CourseCtx* c, int phase)
{
    c->phase = phase;
    c->timer = 0;
}

/* From powershield.c: put a fighter on the stage's main floor. */
static void PutOnGround(GOBJ* ft, float x)
{
    FighterData* ft_data = ft->userdata;
    Vec3 pos = { x, 0, 0 };

    ft_data->coll_data.ground_index = 1;
    ft_data->phys.pos = pos;
    ft_data->coll_data.topN_Curr = pos;
    ft_data->coll_data.topN_CurrCorrect = pos;
    ft_data->coll_data.topN_Prev = pos;
    ft_data->coll_data.topN_Proj = pos;
    ft_data->coll_data.coll_test = *stc_colltest;

    JOBJ* jobj = ft->hsd_object;
    jobj->trans = pos;
    JOBJ_SetMtxDirtySub(jobj);
    Fighter_SetPosition(ft_data->ply, ft_data->flags.ms, &ft_data->phys.pos);

    EnvironmentCollision_WaitLanding(ft);
    Fighter_SetGrounded(ft_data);
}

/* Let go of whoever this fighter holds, and of it if it is held, the
 * way the game ends a grab (ftCo_800DC920). Without this a reset in the
 * middle of a grab leaves the two linked: the victim was put in the floor
 * and the next grab did not take (seen on Shine OoS, 2026-11-12). */
static void ReleaseGrab(GOBJ* ft)
{
    FighterData* fd = ft->userdata;
    if (fd->grab.victim != NULL) {
        Fighter_BreakGrab(ft, fd->grab.victim);
    }
    if (fd->grab.attacker != NULL) {
        Fighter_BreakGrab(fd->grab.attacker, ft);
    }
}

static void ResetFighter(GOBJ* ft, float x, float facing, float percent)
{
    FighterData* fd = ft->userdata;
    ReleaseGrab(ft);
    fd->facing_direction = facing;
    fd->phys.self_vel.X = 0;
    fd->phys.self_vel.Y = 0;
    fd->phys.anim_vel.X = 0;
    fd->phys.anim_vel.Y = 0;
    PutOnGround(ft, x);
    Fighter_EnterWait(ft);
    fd->dmg.percent = percent;
    Fighter_SetHUDDamage(fd->ply, (u16) percent);
    Fighter_UpdateCameraBox(ft);
}

/* Both fighters standing on the main floor, the player facing the CPU and
 * at 0%. The CPU faces the player unless `cpu_faces_away`. */
static void course_Place(CourseCtx* c, float hmn_x, float cpu_x,
                         int cpu_faces_away, float cpu_percent)
{
    float s = c->side;
    ResetFighter(Fighter_GetGObj(0), hmn_x, s, 0);
    ResetFighter(Fighter_GetGObj(1), cpu_x, cpu_faces_away ? s : -s,
                 cpu_percent);
    Match_CorrectCamera();
}

/* Drills without an opponent: the player standing at x, facing right.
 * Reference scripts' positive stick X is then forward. */
static void course_PlaceSolo(CourseCtx* c, float x)
{
    c->side = 1.0F;
    c->toward = -1.0F;
    ResetFighter(Fighter_GetGObj(0), x, 1.0F, 0);
    Match_CorrectCamera();
}

#include "ledge.inc.h"

/* The player hanging on the stage's left ledge, as after a fresh grab
 * (full ledge intangibility). Positive stick X in a reference script is
 * toward the stage. The placement is TM-CE's (ledgedash.c
 * Fighter_PlaceOnLedge). */
static void course_PlaceOnLedge(CourseCtx* c)
{
    GOBJ* hmn = Fighter_GetGObj(0);
    FighterData* hd = hmn->userdata;
    FtCliffCatch* ft_state = (void*) &hd->state_var;
    float ledge_dir;
    int line = course_LedgeFind(-1, 0, &ledge_dir);

    c->side = 1.0F;
    c->toward = -1.0F;
    if (line == -1) {
        return;
    }
    ReleaseGrab(hmn);
    hd->phys.self_vel.X = 0;
    hd->phys.self_vel.Y = 0;
    hd->flags.used_tether = 0;
    Fighter_EnterSleep(hmn, 0);
    Fighter_EnterRebirth(hmn);
    hd->facing_direction = ledge_dir;
    ft_state->ledge_index = line;
    Fighter_EnterCliffWait(hmn);
    ft_state->timer = 0;
    Fighter_SetAirborne(hd);
    Fighter_EnableCollUpdate(hd);
    Coll_CheckLedge(&hd->coll_data);
    Fighter_MoveToCliff(hmn);
    course_UpdatePosition(hmn);
    Fighter_ApplyIntang(hmn, (*stc_ftcommon)->cliff_invuln_time + 1);
    hd->dmg.percent = 0;
    Fighter_SetHUDDamage(hd->ply, 0);
    Fighter_UpdateCameraBox(hmn);
    Match_CorrectCamera();
}

/* The player standing on the floor or platform found straight below
 * (x, above_y), facing right. */
static void course_PlaceOnPlatform(CourseCtx* c, float x, float above_y)
{
    GOBJ* hmn = Fighter_GetGObj(0);
    FighterData* hd = hmn->userdata;
    Vec3 pos, angle;
    int index, kind;

    c->side = 1.0F;
    c->toward = -1.0F;
    ResetFighter(hmn, x, 1.0F, 0);
    if (GrColl_RaycastGround(&pos, &index, &kind, &angle, -1, -1, -1, 0, x,
                             above_y, x, above_y - 60.0F, 0))
    {
        JOBJ* jobj = hmn->hsd_object;
        hd->coll_data.ground_index = index;
        hd->phys.pos = pos;
        hd->coll_data.topN_Curr = pos;
        hd->coll_data.topN_CurrCorrect = pos;
        hd->coll_data.topN_Prev = pos;
        hd->coll_data.topN_Proj = pos;
        jobj->trans = pos;
        JOBJ_SetMtxDirtySub(jobj);
        Fighter_SetPosition(hd->ply, hd->flags.ms, &hd->phys.pos);
        EnvironmentCollision_WaitLanding(hmn);
        Fighter_SetGrounded(hd);
        Fighter_EnterWait(hmn);
        Fighter_UpdateCameraBox(hmn);
    }
    Match_CorrectCamera();
}

/* The player is dead or far below the stage. */
static int course_Fell(CourseCtx* c)
{
    return c->hd->state_id <= ASID_DEADUPFALLHITCAMERAICE ||
           c->hd->phys.pos.Y < -70.0F;
}

/* A target that shields: call every frame of the attempt. The CPU holds
 * full shield and the shield never shrinks. */
#define COURSE_SHIELD_FULL 60.0F
static void course_CpuShield(CourseCtx* c)
{
    c->cd->cpu.held |= PAD_TRIGGER_R;
    c->cd->shield.health = COURSE_SHIELD_FULL;
}

/* How many demonstrations have started, this one included: lets a built
 * reference show something different each time. */
static int course_DemoCount(void)
{
    return en.demo_count;
}

/* The attempt is a demonstration, not the player's. */
static int course_IsDemo(void)
{
    return en.demo != 0;
}

/* Frames of lateness the drill's Leniency option (its index among the
 * drill's own options) allows. */
static int course_Leniency(int option)
{
    return leniency_frames[Options_Main[OPT_COMMON_COUNT + option].val];
}

/* Apply the script entries active on `frame` to the CPU's pad. The engine
 * zeroes the CPU's inputs every frame first. */
static void course_Script(CourseCtx* c, const CourseInput* in, int frame)
{
    FighterData* cpu = c->cd;
    for (; in->frame >= 0; in++) {
        int hold = in->hold ? in->hold : 1;
        if (frame < in->frame || frame >= in->frame + hold) {
            continue;
        }
        cpu->cpu.lstickX = (s8) (in->lx * c->toward);
        cpu->cpu.lstickY = in->ly;
        cpu->cpu.cstickX = (s8) (in->cx * c->toward);
        cpu->cpu.cstickY = in->cy;
        cpu->cpu.held |= in->buttons;
    }
}

/* Announce a moment the reference script can place inputs against. Only
 * the first call per attempt counts. */
static void course_Mark(CourseCtx* c, int mark)
{
    if (mark > 0 && mark < COURSE_MAX_MARKS && en.marks[mark] < 0) {
        en.marks[mark] = en.attempt_frame;
    }
}

/* Write this frame's pad for the player's fighter, the way the Lab's
 * playback does (lab.c Record_SetInputs): the engine pad the fighter reads
 * and the raw reading UCF looks at. Sticks arrive as -127..127 and the
 * engine pad counts to 80. */
static void SetPlayerPad(FighterData* hd, int lx, int ly, int cx, int cy,
                         int buttons, int trigger)
{
    HSD_Pad* pad = PadGetEngine(hd->pad_index);
    PADStatus* stat = PadGetRaw(hd->pad_index);

    pad->held = buttons;
    pad->stickX = (s8) (lx * 80 / 127);
    pad->stickY = (s8) (ly * 80 / 127);
    pad->substickX = (s8) (cx * 80 / 127);
    pad->substickY = (s8) (cy * 80 / 127);
    pad->fstickX = (float) pad->stickX / 80;
    pad->fstickY = (float) pad->stickY / 80;
    pad->fsubstickX = (float) pad->substickX / 80;
    pad->fsubstickY = (float) pad->substickY / 80;
    pad->triggerRight = trigger;
    pad->triggerLeft = 0;
    pad->ftriggerRight = (float) trigger / 140;
    pad->ftriggerLeft = 0;

    stat->button = buttons;
    stat->stickX = pad->stickX;
    stat->stickY = pad->stickY;
    stat->substickX = pad->substickX;
    stat->substickY = pad->substickY;
    stat->triggerRight = trigger;
    stat->triggerLeft = 0;
    stat->analogA = 0;
    stat->analogB = 0;
}

/* During a demonstration the player's pad is the reference script. */
static void PlayReference(CourseCtx* c)
{
    const CourseRefInput* in = en.ref;
    int lx = 0, ly = 0, cx = 0, cy = 0, buttons = 0, trigger = 0;

    if (in == NULL) {
        return;
    }

    /* Both passes must start from the same pad state: whatever was held
     * when the attempt began (by the player, or by the pass before) is let
     * go for COURSE_REF_LEAD frames first, so every button of the script
     * is a fresh press. */
    if (en.run != RUN_ATTEMPT || en.attempt_frame < COURSE_REF_LEAD) {
        SetPlayerPad(c->hd, 0, 0, 0, 0, 0, 0);
        return;
    }
    for (; in->mark != COURSE_REF_END; in++) {
        int hold = in->hold ? in->hold : 1;
        int base, t;
        if (in->mark == 0) {
            base = COURSE_REF_LEAD;
        } else if (en.drill->live_marks) {
            /* a mark of this very attempt: inputs from the frame after it */
            if (en.marks[in->mark] < 0) {
                continue;
            }
            base = en.marks[in->mark];
        } else if (en.demo == 2 && en.demo_marks[in->mark] >= 0) {
            base = en.demo_marks[in->mark];
        } else {
            continue;
        }
        t = en.attempt_frame -
            (base + in->frame + in->js * course_Fighter(c->hd)->jump_squat);
        if (t < 0 || t >= hold) {
            continue;
        }
        if (in->lx != 0 || in->ly != 0) {
            lx = (int) (in->lx * -c->toward); /* toward the opponent */
            ly = in->ly;
        }
        if (in->cx != 0 || in->cy != 0) {
            cx = (int) (in->cx * -c->toward);
            cy = in->cy;
        }
        buttons |= in->buttons;
        if (in->trigger > trigger) {
            trigger = in->trigger;
        }
    }
    SetPlayerPad(c->hd, lx, ly, cx, cy, buttons, trigger);
}

/* What the attempt measured against what was needed (frames, usually):
 * shown in the statistics and the test report. Call before course_Result. */
static void course_Measure(int measured, int target)
{
    en.has_measure = 1;
    en.measured = measured;
    en.target = target;
}

#ifdef TM_TEST
static void ReportAppend(const char* key, const char* value)
{
    /* No snprintf in the game: format into a buffer that fits any key
     * and value used here, then copy if there is room. */
    char buf[64];
    int n;
    if (strlen(key) + strlen(value) + 5 > sizeof(buf)) {
        return;
    }
    n = sprintf(buf, ",\"%s\":%s", key, value);
    if (n > 0 && en.report_len + n < (int) sizeof(en.report)) {
        memcpy(en.report + en.report_len, buf, n + 1);
        en.report_len += n;
    }
}
#endif

/* Extra fields for the attempt's test report line (test builds only). */
static void course_Report(const char* key, int value)
{
#ifdef TM_TEST
    char buf[16];
    sprintf(buf, "%d", value);
    ReportAppend(key, buf);
#endif
}

static void course_ReportF(const char* key, float value)
{
#ifdef TM_TEST
    char buf[24];
    sprintf(buf, "%.1f", value);
    ReportAppend(key, buf);
#endif
}

#ifdef TM_TEST
/* The message up to its first line break, for a JSON string. */
static char* Reason(char* fmt)
{
    static char buf[48];
    int i;
    for (i = 0; fmt[i] != '\0' && fmt[i] != '\n' && i < 47; i++) {
        buf[i] = fmt[i] == '"' ? '\'' : fmt[i];
    }
    buf[i] = '\0';
    return buf;
}

static void TestReport(CourseCtx* c, const char* result, char* fmt)
{
    OSReport("TMTEST {\"result\":\"%s\",\"drill\":\"%s\","
             "\"scenario\":\"%s\",\"cpu\":%d,\"measured\":%d,"
             "\"target\":%d,\"demo\":%d%s,\"why\":\"%s\"}\n",
             result, en.info->id, ScenarioName(c->scenario),
             c->entry != NULL ? c->entry->ckind : -1,
             en.has_measure ? en.measured : -1,
             en.has_measure ? en.target : -1, en.demo, en.report,
             Reason(fmt));
}
#endif

static void CountDrill(int success)
{
    CourseStats* st = &Course_Stats[Course_Current];
    st->attempts++;
    if (success) {
        st->successes++;
    }
    if (en.total.best_streak > st->best_streak) {
        st->best_streak = en.total.best_streak;
    }
}

static void Count(Stats* st, int success)
{
    st->attempts++;
    if (success) {
        st->successes++;
        st->streak++;
        if (st->streak > st->best_streak) {
            st->best_streak = st->streak;
        }
    } else {
        st->streak = 0;
    }
    if (en.has_measure) {
        int e = en.measured - en.target;
        st->error_sum += e < 0 ? -e : e;
        st->measured++;
    }
}

/* End the attempt: count it, show the verdict (a printf format with up to
 * two ints), and reset after the reset delay. */
static void course_Result(CourseCtx* c, int success, char* fmt, int a, int b)
{
#ifdef TM_TEST
    if (en.demo != 1) { /* the observing pass of a demonstration is silent */
        TestReport(c, success ? "success" : "fail", fmt);
    }
#endif
    if (en.demo == 1) {
        /* The observing pass is over: play it for real, at once. */
        memcpy(en.demo_marks, en.marks, sizeof(en.demo_marks));
        en.demo = 2;
        en.run = RUN_RESULT;
        en.result_timer = 1;
        return;
    }
    if (en.demo == 2) {
        /* Not the player's attempt: shown, not counted. */
        event_vars->Message_Display(MSG_KIND, MSG_QUEUE, MSGCOLOR_YELLOW,
                                    fmt, a, b);
        en.demo = 0;
        if (Options_Main[OPT_DEMO].val == DEMO_ONCE) {
            Options_Main[OPT_DEMO].val = DEMO_OFF;
        }
        en.run = RUN_RESULT;
        en.result_timer =
            reset_delay_frames[Options_Main[OPT_RESET_DELAY].val] + 30;
        return;
    }
    Count(&en.stats[c->scenario], success);
    Count(&en.total, success);
    CountDrill(success);
    en.last_success = success;
    event_vars->Message_Display(MSG_KIND, MSG_QUEUE,
                                success ? MSGCOLOR_GREEN : MSGCOLOR_RED, fmt,
                                a, b);
    if (en.drill->flow) {
        /* Counted; carry on from where the player is. */
        int i;
        c->phase = 0;
        c->timer = 0;
        for (i = 0; i < COURSE_MAX_MARKS; i++) {
            en.marks[i] = -1;
        }
        en.has_measure = 0;
        en.report[0] = '\0';
        en.report_len = 0;
        return;
    }
    en.run = RUN_RESULT;
    en.result_timer = reset_delay_frames[Options_Main[OPT_RESET_DELAY].val];
}

/* End the attempt without counting it: the scenario did not come about
 * (the CPU's attack missed...), which is not the player's doing. */
static void course_Retry(CourseCtx* c, char* fmt)
{
    course_Message(MSGCOLOR_YELLOW, fmt, 0, 0, 0);
#ifdef TM_TEST
    TestReport(c, "retry", fmt);
#endif
    en.run = RUN_RESULT;
    en.result_timer = 30;
}

/* The statistics card option (see OnStatsCard). */
static int stats_card = 1;
static const char* opt_off_on[] = { "Off", "On" };

/* ---- guide overlay -------------------------------------------------------- */

/* HUD camera units (TM-CE's hudcam): x right, y up, the screen is roughly
 * 60 wide and 45 tall around the origin. */
#define GUIDE_X (-25.0F)
#define GUIDE_Y (-10.5F) /* clear of the damage display below */
#define GUIDE_W 50.0F
#define GUIDE_H 32.5F
#define GUIDE_TEXT_X (GUIDE_X + 1.5F)
#define GUIDE_LINE_H 1.9F
#define GUIDE_TIMELINE_FROM (-2) /* frames shown before a marked script */
#define GUIDE_TIMELINE_SOLO 15  /* frames shown in all */

static void GuideOpen(CourseCtx* c)
{
    memset(&en.guide, 0, sizeof(en.guide));
    if (en.drill->Guide != NULL) {
        en.drill->Guide(c, &en.guide);
    } else {
        int i;
        for (i = 0; i < 3 && en.drill->help[i] != NULL; i++) {
            strncpy(en.guide.line[i], en.drill->help[i],
                    COURSE_GUIDE_COLS - 1);
        }
        en.guide.line_count = i;
    }
    en.demo = 0;
    en.run = RUN_GUIDE;
    SFX_PlayCommon(1);
}

/* TM-CE events.c (core unit; global). */
void HUD_DrawTextEx(const char* text, Rect* pos, float size,
                    GXColor text_color, GXColor border_color,
                    float border_offset, int align);

static void GuideText(const char* text, float x, float y, float size,
                      GXColor color)
{
    /* w = 0: HUD_DrawTextEx anchors at the rect's centre. */
    Rect r = { x, y, 0, 0 };
    static const GXColor black = { 0, 0, 0, 255 };
    HUDCamData* cam = event_vars->hudcam_gobj->userdata;
    if (cam->text_cache_used >= countof(cam->text_cache)) {
        return; /* out of HUD texts: drawing one more stops the game */
    }
    /* Called directly: TM-CE leaves event_vars->HUD_DrawTextEx NULL (its
     * table initialiser in events.c omits it). */
    HUD_DrawTextEx(text, &r, size, color, black, 1.0F, 0);
    {
        /* HUD texts are made for short labels: they are squeezed to an
         * aspect width of 80. Widen the one just drawn (the cache hands
         * the same Text out in the same order every frame). */
        HUDCamData* hud = event_vars->hudcam_gobj->userdata;
        if (hud->text_cache_used > 0) {
            Text* t = hud->text_cache[hud->text_cache_used - 1];
            if (t != NULL) {
                t->aspect.X = 2000;
            }
        }
    }
}

/* A short name for what a reference entry presses. */
static const char* RefLabel(const CourseRefInput* in)
{
    static char buf[16];
    const char* dir = (in->ly < -60 && (in->lx > 60 || in->lx < -60))
                          ? "Diag+"
                      : in->ly < -60 ? "Down+"
                      : in->ly > 60  ? "Up+"
                      : in->lx > 60  ? "Fwd+"
                      : in->lx < -60 ? "Back+"
                                     : "";
    const char* btn = (in->buttons & PAD_BUTTON_A)    ? "A"
                      : (in->buttons & PAD_BUTTON_B)  ? "B"
                      : (in->buttons & PAD_BUTTON_X)  ? "X"
                      : (in->buttons & PAD_BUTTON_Y)  ? "Y"
                      : (in->buttons & PAD_TRIGGER_Z) ? "Z"
                      : (in->buttons & PAD_TRIGGER_R) ? "R"
                      : (in->buttons & PAD_TRIGGER_L) ? "L"
                                                      : "";
    if (btn[0] == '\0' && dir[0] == '\0' && (in->cx != 0 || in->cy != 0)) {
        return in->cy < -60 ? "C-Down" : in->cy > 60 ? "C-Up" : "C-Side";
    }
    sprintf(buf, "%s%s", dir, btn);
    if (btn[0] == '\0' && dir[0] != '\0') {
        buf[strlen(buf) - 1] = '\0'; /* a stick direction alone */
    }
    return buf;
}

/* The reference script's inputs, one box per frame: the ones placed
 * against a mark if it has any (frames around the mark), otherwise all of
 * it from its first input. */
static void GuideTimeline(float y)
{
    const CourseRefInput* ref = en.ref;
    const CourseRefInput* in;
    static const GXColor idle = { 70, 70, 80, 255 };
    static const GXColor press = { 255, 211, 0, 255 };
    static const GXColor white = { 255, 255, 255, 255 };
    static const GXColor grey = { 190, 190, 190, 255 };
    int js = course_Fighter(en.ctx.hd)->jump_squat;
    int marked = 0, origin = 0, from, to;
    float box = 2.2F, gap = 0.4F;
    float x0 = GUIDE_TEXT_X + 6.0F;
    const char* caption = en.guide.timeline_from;
    char buf[8];
    int f;

    if (ref == NULL || en.guide.hide_timeline) {
        return;
    }
    for (in = ref; in->mark != COURSE_REF_END; in++) {
        if (in->mark != 0) {
            marked = 1;
        }
    }
    if (marked) {
        /* from two frames before the earliest marked input */
        int first = 0;
        for (in = ref; in->mark != COURSE_REF_END; in++) {
            if (in->mark != 0 && in->frame + in->js * js < first) {
                first = in->frame + in->js * js;
            }
        }
        from = first + GUIDE_TIMELINE_FROM;
        to = from + GUIDE_TIMELINE_SOLO - 1;
    } else {
        origin = ref->frame + ref->js * js;
        from = 0;
        to = GUIDE_TIMELINE_SOLO - 1;
        if (caption == NULL) {
            caption = "frames (1 = your first input)";
        }
    }
    GuideText("Inputs", GUIDE_TEXT_X, y - 0.4F, 0.45F, white);
    for (f = from; f <= to; f++) {
        float x = x0 + (f - from) * (box + gap);
        Rect r = { x, y - box, box, box };
        GXColor color = idle;
        for (in = ref; in->mark != COURSE_REF_END; in++) {
            if ((in->mark != 0) == marked &&
                in->frame + in->js * js - origin == f)
            {
                color = press;
                const char* label = RefLabel(in);
                GuideText(label, x - (strlen(label) > 2 ? 1.0F : 0.3F),
                          y + 1.6F, 0.4F, press);
            }
        }
        event_vars->HUD_DrawRects(&r, &color, 1);
        /* Number the pressed frames, the first and every fifth: the HUD
         * has 32 texts in all. */
        if (color.r == press.r || f == from || (f + 1) % 5 == 0) {
            sprintf(buf, "%d", f + 1);
            GuideText(buf, x + 0.4F, y - box - 0.3F, 0.35F, grey);
        }
    }
    if (caption != NULL) {
        GuideText(caption, x0, y - box - 2.0F, 0.38F, grey);
    }
}

/* The drill's success rate, top left, while playing. */
#define CARD_X (-29.0F)
#define CARD_Y 16.0F
#define CARD_W 22.0F
#define CARD_H 6.6F
static void StatsCard(void)
{
    static const GXColor back = { 10, 12, 30, 170 };
    static const GXColor white = { 255, 255, 255, 255 };
    static const GXColor gold = { 255, 211, 0, 255 };
    static const GXColor grey = { 190, 190, 190, 255 };
    static char rate[40], streak[40];
    const Stats* st = &en.total;
    Rect r = { CARD_X, CARD_Y, CARD_W, CARD_H };
    GXColor color = back;

    event_vars->HUD_DrawRects(&r, &color, 1);
    GuideText(en.info->name, CARD_X + 0.8F, CARD_Y + CARD_H - 1.6F, 0.4F,
              gold);
    if (st->attempts > 0) {
        sprintf(rate, "%d / %d   %d%%", st->successes, st->attempts,
                st->successes * 100 / st->attempts);
    } else {
        sprintf(rate, "0 / 0");
    }
    GuideText(rate, CARD_X + 0.8F, CARD_Y + CARD_H - 3.8F, 0.5F, white);
    sprintf(streak, "Streak %d   Best %d", st->streak, st->best_streak);
    GuideText(streak, CARD_X + 0.8F, CARD_Y + CARD_H - 5.7F, 0.38F, grey);
}

static void Guide_GX(GOBJ* gobj, int pass)
{
    static const GXColor back = { 10, 12, 30, 225 };
    static const GXColor edge = { 255, 211, 0, 255 };
    static const GXColor white = { 255, 255, 255, 255 };
    static const GXColor gold = { 255, 211, 0, 255 };
    static const GXColor grey = { 190, 190, 190, 255 };
    Rect panel[2] = {
        { GUIDE_X - 0.3F, GUIDE_Y - 0.3F, GUIDE_W + 0.6F, GUIDE_H + 0.6F },
        { GUIDE_X, GUIDE_Y, GUIDE_W, GUIDE_H },
    };
    GXColor colors[2];
    float y = GUIDE_Y + GUIDE_H - 2.4F;
    int i;

    if (pass != 2) {
        return;
    }
    if (en.run != RUN_GUIDE) {
        if (stats_card) {
            StatsCard();
        }
        return;
    }
    colors[0] = edge;
    colors[1] = back;
    event_vars->HUD_DrawRects(panel, colors, 2);

    GuideText(en.info->name, GUIDE_TEXT_X, y, 0.6F, gold);
    y -= 3.0F;
    for (i = 0; i < en.guide.line_count; i++) {
        GuideText(en.guide.line[i], GUIDE_TEXT_X, y, 0.4F, white);
        y -= GUIDE_LINE_H;
    }
    GuideTimeline(GUIDE_Y + 7.6F);
    GuideText("D-Pad up: close    D-Pad right: watch a demonstration",
              GUIDE_TEXT_X, GUIDE_Y + 1.2F, 0.4F, grey);
}

/* Later than every fighter proc (TM-CE's own end-of-frame procs use 20). */
#define COURSE_SAMPLE_PRIORITY 19

/* End of frame: what the player's fighter ended up doing (see CourseCtx). */
static void Sample(GOBJ* gobj)
{
    CourseCtx* c = &en.ctx;
    GOBJ* hmn = Fighter_GetGObj(0);
    FighterData* hd;
    if (hmn == NULL || en.run != RUN_ATTEMPT) {
        return;
    }
    hd = hmn->userdata;
    if ((int) hd->state_id != c->state) {
        c->prev_state = c->state;
        c->state = hd->state_id;
        c->state_frames = 0;
    }
    c->state_frames++;
    c->held = hd->input.held;
    c->down = hd->input.down;
    if (Fighter_GetGObj(1) != NULL) {
        FighterData* cd = Fighter_GetGObj(1)->userdata;
        c->cpu_state = cd->state_id;
    }
}

static int PickScenario(void)
{
    int fixed = Options_Main[OPT_SCENARIO].val;
    if (en.demo == 2 && en.demo_scenario >= 0) {
        return en.demo_scenario; /* the pass that was just observed */
    }
    if (fixed > 0 && ScenarioUsable(fixed - 1)) {
        return fixed - 1;
    }
    if (en.ctx.scenario < 0) {
        return NextScenario(-1);
    }
    switch (Options_Main[OPT_SWITCH].val) {
    case SWITCH_ON_SUCCESS:
        return en.last_success ? NextScenario(en.ctx.scenario)
                               : en.ctx.scenario;
    case SWITCH_MANUAL:
        return en.ctx.scenario;
    default:
        return NextScenario(en.ctx.scenario);
    }
}

static int HasReference(void)
{
    return en.drill->reference != NULL || en.drill->BuildReference != NULL;
}

static void Reset(void)
{
    CourseCtx* c = &en.ctx;
    int idx;
    int side;
    int i;
    Stats* st;

    /* A demonstration is two attempts from the same random numbers. */
    if (en.demo == 0 && Options_Main[OPT_DEMO].val != DEMO_OFF &&
        HasReference())
    {
        en.demo = 1; /* or 2 at once, decided below when the script is known */
        en.demo_count++;
        en.demo_seed = **stc_rng_seed;
        en.demo_scenario = -1;
    }
    if (en.demo != 0) {
        **stc_rng_seed = en.demo_seed;
    }
    idx = PickScenario();

    if (idx < 0) {
        course_Message(MSGCOLOR_RED, "No scenarios loaded", 0, 0, 0);
        en.run = RUN_RESULT;
        en.result_timer = 600;
        return;
    }
    c->scenario = idx;
    c->entry = en.deck != NULL ? &en.deck->entries[idx] : NULL;
    if (c->entry != NULL &&
        tm_rot_SetCpu(1, c->entry->ckind, c->entry->color) < 0)
    {
        course_Message(MSGCOLOR_RED, "Could not load\n%s", c->entry->name, 0,
                       0);
    }
    /* The CPU may be a new fighter now. */
    c->hmn = Fighter_GetGObj(0);
    c->cpu = Fighter_GetGObj(1);
    c->hd = c->hmn->userdata;
    c->cd = c->cpu != NULL ? c->cpu->userdata : NULL;

    side = Options_Main[OPT_SIDE].val;
    if (side == SIDE_RANDOM) {
        side = HSD_Randi(2) ? SIDE_LEFT : SIDE_RIGHT;
    }
    c->side = side == SIDE_LEFT ? -1.0F : 1.0F;
    c->toward = -c->side;
    c->phase = 0;
    c->timer = 0;
    c->hmn_hit = 0;
    c->cpu_hit = 0;
    c->state = c->prev_state = -1;
    c->state_frames = 0;
    c->held = c->down = 0;
    c->cpu_state = -1;
    en.run = RUN_ATTEMPT;
    en.attempt_frame = 0;
    for (i = 0; i < COURSE_MAX_MARKS; i++) {
        en.marks[i] = -1;
    }
    if (en.demo != 0) {
        en.demo_scenario = idx;
    }
    en.has_measure = 0;
    en.report[0] = '\0';
    en.report_len = 0;

    en.drill->Setup(c);

    en.ref = en.drill->BuildReference != NULL ? en.drill->BuildReference(c)
                                              : en.drill->reference;
    if (en.demo == 1) {
        /* Nothing to observe if every input is placed against the start
         * of the attempt: play it straight away. */
        const CourseRefInput* in;
        en.demo = 2;
        for (in = en.ref; in->mark != COURSE_REF_END; in++) {
            if (in->mark != 0 && !en.drill->live_marks) {
                en.demo = 1;
            }
        }
    }

    en.hmn_percent = c->hd->dmg.percent;
    en.cpu_percent = c->cd != NULL ? c->cd->dmg.percent : 0;
    st = &en.stats[idx];
    if (en.demo == 1) {
        course_Message(MSGCOLOR_YELLOW, "Demo: watch\n%s",
                       ScenarioName(idx), 0, 0);
    } else if (en.demo == 2) {
        course_Message(MSGCOLOR_YELLOW, "Demo: answer\n%s",
                       ScenarioName(idx), 0, 0);
    } else {
        course_Message(MSGCOLOR_WHITE, "%s\n%d / %d", ScenarioName(idx),
                       st->successes, st->attempts);
    }
}

/* `def` with the value `cur` holds, if `cur` was built before or had a
 * value stored into it while still empty. */
/* The statistics card: kept here, not in its menu slot, because the slot
 * comes after the drill's own options and so moves from drill to drill. */

static void OnStatsCard(GOBJ* menu, int value)
{
    stats_card = value;
}

static void GuideOpen(CourseCtx* c);
void EventMenu_ExitMenu(GOBJ* gobj); /* TM-CE menu.c */

/* A on Help: leave the menu and open the guide. */
static void OnHelp(GOBJ* menu)
{
    EventMenu_ExitMenu(menu);
    if (en.run != RUN_GUIDE) {
        GuideOpen(&en.ctx);
    }
}

/* The drill whose options Options_Main holds, -1 before the first. */
static int options_drill = -1;

/* An option slot keeps its value when it has been set up before (or written
 * by a test: tmce_test_SetOption names the slot) and still means the same
 * thing: always for the common options, for a drill's own only while the
 * drill is the same. Otherwise it takes the default. */
static EventOption MergeOption(const EventOption* cur, const EventOption* def,
                               int is_common)
{
    EventOption out = *def;
    if (cur->name != NULL &&
        (is_common || options_drill == -1 ||
         options_drill == (int) Course_Current))
    {
        out.val = cur->val;
    }
    return out;
}

void Event_Init(GOBJ* gobj)
{
    int i, n, o = 0;

    memset(&en, 0, sizeof(en));
    en.info = &Course_Drills[Course_Current];
    en.drill = drills[Course_Current];
    en.deck = en.info->deck;
    en.ctx.scenario = -1;

    n = ScenarioCount();
    for (i = 0; i < n; i++) {
        scenario_names[i + 1] = ScenarioName(i);
    }

    /* The menu: common options, the drill's, HELP, Exit. Values survive a
     * rebuild (retry keeps the player's settings), and a value stored
     * before the first build (a test's) wins over the default. */
    for (i = 0; i < OPT_COMMON_COUNT; i++, o++) {
        Options_Main[o] =
            MergeOption(&Options_Main[o], &Options_Common[i], 1);
    }
    Options_Main[OPT_SCENARIO].value_num = n + 1;
    if (Options_Main[OPT_SCENARIO].val > n) {
        Options_Main[OPT_SCENARIO].val = 0; /* another drill's scenario */
    }
    for (i = 0; i < en.drill->option_count && i < MAX_DRILL_OPTIONS;
         i++, o++)
    {
        Options_Main[o] =
            MergeOption(&Options_Main[o], &en.drill->options[i], 0);
    }
    options_drill = Course_Current;
    Options_Main[o].kind = OPTKIND_STRING;
    Options_Main[o].name = "Stats Card";
    Options_Main[o].desc[0] = "Show your success rate on screen.";
    Options_Main[o].desc[1] = NULL;
    Options_Main[o].desc[2] = NULL;
    Options_Main[o].values = opt_off_on;
    Options_Main[o].value_num = countof(opt_off_on);
    Options_Main[o].val = stats_card;
    Options_Main[o].OnChange = OnStatsCard;
    Options_Main[o].OnSelect = NULL;
    o++;
    Options_Main[o].kind = OPTKIND_FUNC;
    Options_Main[o].name = "Help";
    Options_Main[o].OnChange = NULL;
    Options_Main[o].OnSelect = OnHelp;
    Options_Main[o].desc[0] = (char*) en.drill->help[0];
    Options_Main[o].desc[1] = (char*) en.drill->help[1];
    Options_Main[o].desc[2] = (char*) en.drill->help[2];
    o++;
    Options_Main[o].kind = OPTKIND_FUNC;
    Options_Main[o].name = "Exit";
    Options_Main[o].OnChange = NULL;
    Options_Main[o].desc[1] = NULL;
    Options_Main[o].desc[2] = NULL;
    Options_Main[o].desc[0] = "Return to the drill list.";
    Options_Main[o].OnSelect = Event_Exit;
    o++;
    Menu_Main.option_num = o;
    Menu_Main.name = (char*) en.info->name;

    if (en.drill->Init != NULL) {
        en.drill->Init();
    }

    /* The guide overlay draws with the HUD camera; the same object samples
     * the player after the fighters' procs. */
    {
        GOBJ* guide = GObj_Create(0, 0, 0);
        GObj_AddGXLink(guide, Guide_GX, 5, 0);
        GObj_AddProc(guide, Sample, COURSE_SAMPLE_PRIORITY);
    }
}

void Event_Think(GOBJ* event)
{
    CourseCtx* c = &en.ctx;
    GOBJ* hmn = Fighter_GetGObj(0);
    GOBJ* cpu = Fighter_GetGObj(1);
    FighterData* hd;
    FighterData* cd;

    if (hmn == NULL || (cpu == NULL && en.info->cpu_kind != -1)) {
        return;
    }
    if (event_vars->game_timer == 1) {
        Reset();
        return;
    }
    c->hmn = hmn;
    c->cpu = cpu;
    c->hd = hd = hmn->userdata;
    c->cd = cd = cpu != NULL ? cpu->userdata : NULL;

    if (cd != NULL) {
        cd->cpu.ai = 15; /* no CPU logic; scripts drive it */
        Fighter_ZeroCPUInputs(cd);
    }

    /* D-pad up: the guide. While it is open the drill waits; closing it
     * starts a fresh attempt, D-pad right a demonstration first. */
    if (en.run == RUN_GUIDE) {
        if (hd->input.down & (HSD_BUTTON_DPAD_UP | HSD_BUTTON_DPAD_RIGHT)) {
            if ((hd->input.down & HSD_BUTTON_DPAD_RIGHT) && HasReference())
            {
                Options_Main[OPT_DEMO].val = DEMO_ONCE;
            }
            SFX_PlayCommon(0);
            en.last_success = 0;
            Reset();
        }
        return;
    }
    if (hd->input.down & HSD_BUTTON_DPAD_UP) {
        GuideOpen(c);
        return;
    }

    /* D-pad: cycle scenario / reset. Either also stops a demonstration. */
    if (en.demo != 0 &&
        (hd->input.down & (HSD_BUTTON_DPAD_LEFT | HSD_BUTTON_DPAD_RIGHT |
                           HSD_BUTTON_DPAD_DOWN)))
    {
        en.demo = 0;
        Options_Main[OPT_DEMO].val = DEMO_OFF;
    }
    if (hd->input.down & (HSD_BUTTON_DPAD_LEFT | HSD_BUTTON_DPAD_RIGHT)) {
        int dir = (hd->input.down & HSD_BUTTON_DPAD_RIGHT) ? 1 : -1;
        int n = ScenarioCount(), i;
        int idx = c->scenario;
        for (i = 0; i < n; i++) {
            idx = (idx + dir + n) % n;
            if (ScenarioUsable(idx)) {
                break;
            }
        }
        if (Options_Main[OPT_SCENARIO].val > 0) {
            Options_Main[OPT_SCENARIO].val = idx + 1;
        } else {
            Options_Main[OPT_SWITCH].val = SWITCH_MANUAL;
        }
        c->scenario = idx;
        en.last_success = 0;
        Reset();
        return;
    }
    if (hd->input.down & HSD_BUTTON_DPAD_DOWN) {
        en.last_success = 0;
        Reset();
        return;
    }

    c->hmn_hit = hd->dmg.percent > en.hmn_percent;
    c->cpu_hit = cd != NULL && cd->dmg.percent > en.cpu_percent;
    en.hmn_percent = hd->dmg.percent;
    en.cpu_percent = cd != NULL ? cd->dmg.percent : 0;

    if (en.demo != 0) {
        PlayReference(c);
    }
    if (en.run == RUN_ATTEMPT) {
        c->timer++;
        en.drill->Think(c);
        en.attempt_frame++;
    } else if (--en.result_timer <= 0) {
        Reset();
    }
}

static void OnScenarioChange(GOBJ* menu, int value)
{
    en.last_success = 0;
}

void Event_Exit(GOBJ* menu)
{
    stc_match->state = 3;
    Match_EndVS();
}
