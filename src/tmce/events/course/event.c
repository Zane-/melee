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
} CourseCtx;

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
} CourseDrill;

/* Engine services for drills. */
static void course_Phase(CourseCtx* c, int phase);
static void course_Place(CourseCtx* c, float hmn_x, float cpu_x,
                         int cpu_faces_away, float cpu_percent);
static void course_Script(CourseCtx* c, const CourseInput* in, int frame);
static void course_Message(int color, char* fmt, const char* a, int b,
                           int c);
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
    OPT_COMMON_COUNT, /* the drill's options start here */
};

enum { SWITCH_EVERY, SWITCH_ON_SUCCESS, SWITCH_MANUAL };
enum { SIDE_RANDOM, SIDE_LEFT, SIDE_RIGHT };

static const char* scenario_names[MAX_SCENARIOS + 1] = { "Random" };
static const char* opt_switch[] = { "Every Attempt", "On Success",
                                    "Manual (D-Pad)" };
static const char* opt_side[] = { "Random", "Left", "Right" };
static const char* opt_reset_delay[] = { "Fast", "Normal", "Slow" };
static const int reset_delay_frames[] = { 20, 45, 90 };

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

enum { RUN_ATTEMPT, RUN_RESULT };

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
    char report[160]; /* extra JSON fields of the current attempt */
    int report_len;
    Stats total;
    Stats stats[MAX_SCENARIOS];
} en;

/* ---- drills ------------------------------------------------------------- */

/* Drills are headers by name only (`.inc.h`): the build rechecks units when
 * a header changes, and would miss an edit to an included .c file. */
#include "drills/fox_shine_oos.inc.h"

static const CourseDrill* const drills[DRILL_COUNT] = {
    [DRILL_FOX_SHINE_OOS] = &Drill_FoxShineOos,
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

static void ResetFighter(GOBJ* ft, float x, float facing, float percent)
{
    FighterData* fd = ft->userdata;
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
             "\"target\":%d%s,\"why\":\"%s\"}\n",
             result, en.info->id, ScenarioName(c->scenario),
             c->entry != NULL ? c->entry->ckind : -1,
             en.has_measure ? en.measured : -1,
             en.has_measure ? en.target : -1, en.report, Reason(fmt));
}
#endif

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
    Count(&en.stats[c->scenario], success);
    Count(&en.total, success);
    en.last_success = success;
#ifdef TM_TEST
    TestReport(c, success ? "success" : "fail", fmt);
#endif
    event_vars->Message_Display(MSG_KIND, MSG_QUEUE,
                                success ? MSGCOLOR_GREEN : MSGCOLOR_RED, fmt,
                                a, b);
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

static int PickScenario(void)
{
    int fixed = Options_Main[OPT_SCENARIO].val;
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

static void Reset(void)
{
    CourseCtx* c = &en.ctx;
    int idx = PickScenario();
    int side;
    Stats* st;

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
    en.run = RUN_ATTEMPT;
    en.has_measure = 0;
    en.report[0] = '\0';
    en.report_len = 0;

    en.drill->Setup(c);

    en.hmn_percent = c->hd->dmg.percent;
    en.cpu_percent = c->cd != NULL ? c->cd->dmg.percent : 0;
    st = &en.stats[idx];
    course_Message(MSGCOLOR_WHITE, "%s\n%d / %d", ScenarioName(idx),
                   st->successes, st->attempts);
}

/* `def` with the value `cur` holds, if `cur` was built before or had a
 * value stored into it while still empty. */
static EventOption MergeOption(const EventOption* cur,
                               const EventOption* def)
{
    EventOption out = *def;
    if (cur->name != NULL || cur->val != 0) {
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
        Options_Main[o] = MergeOption(&Options_Main[o], &Options_Common[i]);
    }
    Options_Main[OPT_SCENARIO].value_num = n + 1;
    for (i = 0; i < en.drill->option_count && i < MAX_DRILL_OPTIONS;
         i++, o++)
    {
        Options_Main[o] = MergeOption(&Options_Main[o],
                                      &en.drill->options[i]);
    }
    Options_Main[o].kind = OPTKIND_INFO;
    Options_Main[o].name = "HELP";
    Options_Main[o].desc[0] = (char*) en.drill->help[0];
    Options_Main[o].desc[1] = (char*) en.drill->help[1];
    Options_Main[o].desc[2] = (char*) en.drill->help[2];
    o++;
    Options_Main[o].kind = OPTKIND_FUNC;
    Options_Main[o].name = "Exit";
    Options_Main[o].desc[0] = "Return to the drill list.";
    Options_Main[o].OnSelect = Event_Exit;
    o++;
    Menu_Main.option_num = o;
    Menu_Main.name = (char*) en.info->name;

    if (en.drill->Init != NULL) {
        en.drill->Init();
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

    /* D-pad: cycle scenario / reset. */
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

    if (en.run == RUN_ATTEMPT) {
        c->timer++;
        en.drill->Think(c);
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
