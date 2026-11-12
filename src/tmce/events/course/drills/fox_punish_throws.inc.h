/*
 * Fox's Punish drills that start from a grab or end in a kill:
 * fox-uthrow-uair, fox-uthrow-chaingrab, fox-kill-confirm. Specs:
 * data/courses/fox.md (Punish 5, 6, 11). Included by ../event.c.
 *
 * The CPU stands in grab range. Once thrown or hit it holds a DI direction
 * (random each time) and presses jump every other frame, so it leaves on
 * the first frame it can: a follow-up that is not true does not land.
 */

static int th_IsThrow(int state)
{
    return state >= ASID_THROWF && state <= ASID_THROWLW;
}

static int th_CpuDead(CourseCtx* c)
{
    return c->cd->state_id <= ASID_DEADUPFALLHITCAMERAICE;
}

/* The CPU got away: it double jumped, or it is back on the ground
 * (standing, or lying there: a downed opponent cannot be grabbed). */
static int th_CpuEscaped(CourseCtx* c)
{
    return fst_IsDoubleJump(c->cpu_state) || c->cd->phys.air_state == 0;
}

/* How long after it could first act the CPU jumps away. Instant is what a
 * perfect opponent does; measured in the simulator, up throw up air on
 * Marth does not land against that at any percent from 60 to 130, which
 * is the real game: it works on the opponent's reaction. */
static const char* th_opt_escape[] = { "Slow (20)", "Normal (12)",
                                       "Fast (6)", "Instant" };
static const int th_escapes[] = { 20, 12, 6, 0 };
#define TH_OPT_ESCAPE                                                         \
    {                                                                         \
        .kind = OPTKIND_STRING, .value_num = countof(th_opt_escape),          \
        .val = 1, .name = "CPU Escape",                                       \
        .desc = { "Frames after it can first act before the CPU",             \
                  "jumps away." },                                            \
        .values = th_opt_escape,                                              \
    }

static struct {
    int di;    /* stick X the CPU holds, -127, 0 or 127 (toward-positive) */
    int frame; /* frames since the throw or first hit */
    int odd;
    int free;  /* frames the CPU has been able to act */
    int react; /* frames it waits before jumping */
    int jumped; /* it has jumped away since it was last stuck */
} th;

static void th_PickDi(void)
{
    th.di = course_IsDemo() ? 0 : (HSD_Randi(3) - 1) * 127;
}

/* DI, and jump once it has been able to for `th.react` frames. */
static void th_CpuEscape(CourseCtx* c)
{
    FighterData* cd = c->cd;
    int stuck = cd->flags.hitstun ||
                (cd->state_id >= ASID_CAPTUREPULLEDHI &&
                 cd->state_id <= ASID_THROWNLWWOMEN);

    /* DI only matters while it is stuck; held afterwards it would walk or
     * drift the CPU off the stage (it did, and "killed" Marth). One jump
     * away, then it stays where it lands. */
    if (stuck) {
        cd->cpu.lstickX = (s8) (th.di * c->toward);
        th.free = 0;
        th.jumped = 0;
        return;
    }
    th.free++;
    if (fst_IsDoubleJump(cd->state_id) || fst_IsJump(cd->state_id)) {
        th.jumped = 1;
    }
    if (!th.jumped && th.free > th.react && (th.odd ^= 1)) {
        cd->cpu.held |= PAD_BUTTON_X;
    }
}

/* Marks shared by the three drills' demonstrations: the grab, the end of
 * the throw animation, the opponent in reach, the jump nearly spent. */
#define TH_MARK_APEX 4

/* For the demonstrations: the opponent is in reach of an up air. */
#define UA_REACH_X_ 12.0F
static void th_MarkReach(CourseCtx* c, int mark)
{
    float dx = fabs(c->cd->phys.pos.X - c->hd->phys.pos.X);
    float dy = c->cd->phys.pos.Y - c->hd->phys.pos.Y;
    if (c->hd->phys.air_state == 0) {
        return;
    }
    if (dx < UA_REACH_X_ && dy < 30.0F) {
        course_Mark(c, mark);
    } else if (c->hd->phys.self_vel.Y < 0.6F && c->hd->phys.pos.Y > 15.0F) {
        /* the first jump is nearly spent and they are still too high */
        course_Mark(c, TH_MARK_APEX);
    }
}

static void th_Place(CourseCtx* c, float percent, int escape_option)
{
    th.free = 0;
    /* demonstrations are shown against the Normal reaction */
    if (escape_option < 0) {
        th.react = 0; /* a true combo: the CPU acts as soon as it can */
    } else {
        th.react =
            th_escapes[course_IsDemo()
                           ? 1
                           : Options_Main[OPT_COMMON_COUNT + escape_option]
                                 .val];
    }
    float hmn_x = -c->side * (FPR_DISTANCE / 2);
    course_Place(c, hmn_x, hmn_x + c->side * FPR_DISTANCE, 0, percent);
    th.frame = 0;
    th.odd = 0;
    th.jumped = 0;
    th_PickDi();
}

/* ---- fox-uthrow-uair ------------------------------------------------------ */

enum { UA_OPT_PERCENT, UA_OPT_ESCAPE };
enum { UA_MARK_GRAB = 1, UA_MARK_RELEASE, UA_MARK_REACH, UA_MARK_APEX };
enum { UA_WAIT, UA_THROW, UA_CHASE };

#define UA_TIMEOUT 120

static EventOption ua_options[] = {
    [UA_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 151,
        .val = 90,
        .name = "CPU Percent",
        .desc = { "The CPU's damage at the start of each attempt." },
        .format = "%d%%",
    },
    [UA_OPT_ESCAPE] = TH_OPT_ESCAPE,
};

/* Grab, up throw, full hop as Fox comes out of the throw and up air. The
 * demonstration's CPU does not DI. Against DI the player has to dash under
 * the opponent first: with Marth at 90% and full DI away, a 6-frame dash,
 * jump and up air 8 frames later connects 23 frames after the throw
 * animation ends, and he can first act on frame 21 (simulator sweeps,
 * 2026-11-12). */
#define UA_REF_JUMP 1
/* The up air is pressed at the UA_MARK_REACH mark (th_MarkReach). */
static const CourseRefInput ua_reference[] = {
    { 0, 10, 1, 0, 0, 0, 0, PAD_TRIGGER_Z, 0, 0 },
    { UA_MARK_GRAB, 6, 2, 0, 127, 0, 0, 0, 0, 0 },
    { UA_MARK_RELEASE, UA_REF_JUMP, 8, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { UA_MARK_APEX, 1, 2, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 }, /* double jump */
    { UA_MARK_REACH, 1, 1, 0, 0, 0, 127, 0, 0, 0 },
    { COURSE_REF_END },
};

static void ua_Setup(CourseCtx* c)
{
    th_Place(c, (float) Options_Main[OPT_COMMON_COUNT + UA_OPT_PERCENT].val,
             UA_OPT_ESCAPE);
}

static void ua_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Fox's up throw sends them straight up, and his");
    sprintf(g->line[n++], "up air kills off the top. Together they are");
    sprintf(g->line[n++], "his kill from a grab on floaty characters.");
    sprintf(g->line[n++], "1. Grab, then stick up.");
    sprintf(g->line[n++], "2. They drift left or right (DI): dash under");
    sprintf(g->line[n++], "   them first, then jump.");
    sprintf(g->line[n++], "3. Up air before they jump away. A perfect");
    sprintf(g->line[n++], "   opponent always can: this works on reaction.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void ua_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;

    if (fpr_CpuGrabbed(c)) {
        course_Mark(c, UA_MARK_GRAB);
    }
    switch (c->phase) {
    case UA_WAIT:
        if (c->state == ASID_THROWHI) {
            course_Phase(c, UA_THROW);
        } else if (th_IsThrow(c->state)) {
            course_Result(c, 0, "Use the up throw", 0, 0);
        } else if (c->cpu_hit) {
            course_Result(c, 0, "Start with a grab", 0, 0);
        }
        break;

    case UA_THROW:
        th_CpuEscape(c);
        if (c->state != ASID_THROWHI) {
            course_Mark(c, UA_MARK_RELEASE);
            course_Phase(c, UA_CHASE);
            th.frame = 0;
        }
        break;

    case UA_CHASE:
        th.frame++;
        th_CpuEscape(c);
        th_MarkReach(c, UA_MARK_REACH);
        if (c->cpu_hit && hd->state_id == ASID_ATTACKAIRHI) {
            course_Measure(th.frame, th.frame);
            course_Report("frame", th.frame);
            course_Report("di", th.di);
            course_Result(c, 1, "Up throw up air!\n%d frames after the throw",
                          th.frame, 0);
        } else if (c->cpu_hit) {
            course_Result(c, 0, "Hit, but not with up air", 0, 0);
        } else if (th.frame > 4 && th_CpuEscaped(c)) {
            course_Report("frame", th.frame);
            course_Report("di", th.di);
            course_Result(c, 0, "They got away after %d frames\n"
                                "jump and up air sooner",
                          th.frame, 0);
        } else if (th.frame > UA_TIMEOUT) {
            course_Result(c, 0, "No up air", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_FoxUthrowUair = {
    .Setup = ua_Setup,
    .Think = ua_Think,
    .options = ua_options,
    .option_count = countof(ua_options),
    .help = { "Grab, up throw, jump after them and up air before",
              "they can jump away.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = ua_reference,
    .live_marks = 1,
    .Guide = ua_Guide,
};

/* ---- fox-uthrow-chaingrab ------------------------------------------------- */

enum { CG_OPT_PERCENT, CG_OPT_COUNT };
enum { CG_MARK_GRAB = 1, CG_MARK_RELEASE };
enum { CG_WAIT, CG_HELD, CG_THROW, CG_CHASE };

static const char* cg_opt_count[] = { "1", "2", "3", "5" };
static const int cg_counts[] = { 1, 2, 3, 5 };

static EventOption cg_options[] = {
    [CG_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 151,
        .val = 20,
        .name = "CPU Percent",
        .desc = { "The CPU's damage at the start of each attempt." },
        .format = "%d%%",
    },
    [CG_OPT_COUNT] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(cg_opt_count),
        .name = "Regrabs",
        .desc = { "How many regrabs in a row count as a success." },
        .values = cg_opt_count,
    },
};

static struct {
    int regrabs;
} cg;

/* Grab, up throw, grab again. Offset from a sweep in the simulator. */
#define CG_REF_GRAB 5
static const CourseRefInput cg_reference[] = {
    { 0, 10, 1, 0, 0, 0, 0, PAD_TRIGGER_Z, 0, 0 },
    { CG_MARK_GRAB, 6, 2, 0, 127, 0, 0, 0, 0, 0 },
    { CG_MARK_RELEASE, CG_REF_GRAB, 1, 0, 0, 0, 0, PAD_TRIGGER_Z, 0, 0 },
    { COURSE_REF_END },
};

static void cg_Setup(CourseCtx* c)
{
    th_Place(c, (float) Options_Main[OPT_COMMON_COUNT + CG_OPT_PERCENT].val,
             -1);
    cg.regrabs = 0;
}

static void cg_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Fox and Falco fall so fast that an up throw");
    sprintf(g->line[n++], "puts them back on the ground before they can");
    sprintf(g->line[n++], "act. Grab them again as they land.");
    sprintf(g->line[n++], "1. Grab, then stick up.");
    sprintf(g->line[n++], "2. Watch which way they drift (DI) and move");
    sprintf(g->line[n++], "   under them. Turn round if they go behind.");
    sprintf(g->line[n++], "3. Grab just before they would be free.");
    sprintf(g->line[n++], "It stops working as their percent climbs.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void cg_End(CourseCtx* c, int success, char* fmt)
{
    int want = cg_counts[Options_Main[OPT_COMMON_COUNT + CG_OPT_COUNT].val];
    course_Measure(cg.regrabs, want);
    course_Report("regrabs", cg.regrabs);
    course_Report("di", th.di);
    course_Result(c, success, fmt, cg.regrabs, want);
}

static void cg_Think(CourseCtx* c)
{
    int want = cg_counts[Options_Main[OPT_COMMON_COUNT + CG_OPT_COUNT].val];

    switch (c->phase) {
    case CG_WAIT:
        if (fpr_CpuGrabbed(c)) {
            course_Mark(c, CG_MARK_GRAB);
            course_Phase(c, CG_HELD);
        } else if (c->cpu_hit) {
            course_Result(c, 0, "Start with a grab", 0, 0);
        }
        break;

    case CG_HELD:
        if (c->state == ASID_THROWHI) {
            course_Phase(c, CG_THROW);
            th_PickDi();
        } else if (th_IsThrow(c->state)) {
            cg_End(c, 0, "Use the up throw\n%d of %d regrabs");
        } else if (!fpr_CpuGrabbed(c) && c->timer > 3) {
            cg_End(c, 0, "They broke out\n%d of %d regrabs");
        }
        break;

    case CG_THROW:
        th_CpuEscape(c);
        if (c->state != ASID_THROWHI) {
            course_Mark(c, CG_MARK_RELEASE);
            course_Phase(c, CG_CHASE);
            th.frame = 0;
        }
        break;

    case CG_CHASE:
        th.frame++;
        th_CpuEscape(c);
        if (fpr_CpuGrabbed(c)) {
            cg.regrabs++;
            if (cg.regrabs >= want) {
                cg_End(c, 1, "Chain grab!\n%d regrabs");
            } else {
                course_Phase(c, CG_HELD);
            }
        } else if (c->cpu_hit) {
            cg_End(c, 0, "Hit, not a regrab\n%d of %d regrabs");
        } else if (th.frame > 4 && th_CpuEscaped(c)) {
            cg_End(c, 0, "They got away\n%d of %d regrabs");
        } else if (th.frame > UA_TIMEOUT) {
            cg_End(c, 0, "No regrab\n%d of %d regrabs");
        }
        break;
    }
}

static const CourseDrill Drill_FoxChaingrab = {
    .Setup = cg_Setup,
    .Think = cg_Think,
    .options = cg_options,
    .option_count = countof(cg_options),
    .help = { "Grab, up throw, and grab them again as they land,",
              "before they can jump away.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = cg_reference,
    .live_marks = 1,
    .Guide = cg_Guide,
};

/* ---- fox-kill-confirm ----------------------------------------------------- */

enum { KC_OPT_PERCENT, KC_OPT_ESCAPE };
enum { KC_MARK_GRAB = 1, KC_MARK_RELEASE };
enum { KC_WAIT, KC_COMBO };

#define KC_TIMEOUT 300

static EventOption kc_options[] = {
    [KC_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 201,
        .val = 110,
        .name = "CPU Percent",
        .desc = { "The CPU's damage at the start of each attempt." },
        .format = "%d%%",
    },
    [KC_OPT_ESCAPE] = TH_OPT_ESCAPE,
};

static struct {
    int hits;
    int thrown; /* an up throw has started */
} kc;

static void kc_Setup(CourseCtx* c)
{
    th_Place(c, (float) Options_Main[OPT_COMMON_COUNT + KC_OPT_PERCENT].val,
             KC_OPT_ESCAPE);
    kc.hits = 0;
}

static void kc_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "At kill percent every opening should end the");
    sprintf(g->line[n++], "stock. Fox's routes to his kill moves:");
    sprintf(g->line[n++], "Grab, up throw, up air (floaty characters).");
    sprintf(g->line[n++], "Shine, wavedash, up smash.");
    sprintf(g->line[n++], "Up tilt or dash attack, then up smash.");
    sprintf(g->line[n++], "They DI, and jump away a moment after they");
    sprintf(g->line[n++], "can (CPU Escape in the menu).");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void kc_Think(CourseCtx* c)
{
    if (fpr_CpuGrabbed(c)) {
        course_Mark(c, KC_MARK_GRAB);
    }
    switch (c->phase) {
    case KC_WAIT:
        if (fpr_CpuGrabbed(c) ||
            (c->cpu_hit &&
             (fst_IsShine(c->hd->state_id) ||
              c->hd->state_id == ASID_ATTACKHI3 ||
              c->hd->state_id == ASID_ATTACKDASH)))
        {
            course_Phase(c, KC_COMBO);
            th.frame = 0;
            kc.hits = 0;
            kc.thrown = 0;
        } else if (c->cpu_hit) {
            /* a kill move on a standing dummy is not a confirm */
            course_Result(c, 0, "Open with a grab, shine,
"
                                "up tilt or dash attack",
                          0, 0);
        }
        break;

    case KC_COMBO:
        th.frame++;
        th_CpuEscape(c);
        if (c->state == ASID_THROWHI) {
            th.frame = 0; /* the clock starts when the throw lets go */
            kc.thrown = 1;
        } else if (kc.thrown) {
            course_Mark(c, KC_MARK_RELEASE);
        }
        th_MarkReach(c, UA_MARK_REACH);
        if (c->cpu_hit && !th_IsThrow(c->state)) {
            kc.hits++;
        }
        if (th_CpuDead(c)) {
            course_Measure(th.frame, th.frame);
            course_Report("frame", th.frame);
            course_Report("hits", kc.hits);
            course_Result(c, 1, "Stock taken!\n%d frames after the opening",
                          th.frame, 0);
        } else if (th.frame > 30 && c->cpu_state == ASID_WAIT &&
                   !fpr_CpuGrabbed(c)) {
            course_Report("hits", kc.hits);
            course_Result(c, 0, "They survived\nand are back on the ground",
                          0, 0);
        } else if (th.frame > KC_TIMEOUT) {
            course_Result(c, 0, "No kill", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_FoxKillConfirm = {
    .Setup = kc_Setup,
    .Think = kc_Think,
    .options = kc_options,
    .option_count = countof(kc_options),
    .help = { "They are at kill percent: turn the opening into",
              "the stock.",
              "D-Pad up: guide. D-Pad down: reset." },
    /* No demonstration: the up throw up air one was tried and only
     * killed Marth at 150%; which route kills depends on the character
     * and the percent, which is the drill. */
    .Guide = kc_Guide,
};
