/*
 * Fox's shine technique drills: fox-jc-shine, fox-waveshine, fox-multishine.
 * Specs: data/courses/fox.md (Tech). Included by ../event.c.
 *
 * Frame facts, measured with Fox in the simulator (2026-11-12) and agreeing
 * with SSBWiki's Reflector page (data/characters/fox.md, "Multishine").
 * Frame 1 is the frame down-B is pressed and the shine comes out:
 *   - the earliest jump out of shine is on frame 4; a jump on frame 3 is
 *     ignored;
 *   - jump on 4, air dodge on 7 (first airborne frame after Fox's 3-frame
 *     jump squat): special landing from frame 7, actionable on frame 17;
 *   - jump on 4, shine again on 7: that shine is airborne at ground level,
 *     Fox is grounded again on frame 11 and can jump on 12 (a jump on 10
 *     or 11 is the double jump), third shine on 15: one shine per 8 frames
 *     after the first gap of 6.
 * These are Fox's numbers: Falco's jump squat is 5 and his shine differs, so
 * the drills are offered to Fox only until Falco's are measured.
 */

/* Fox's shine states (ftFox/forward.h, ftFx_MS_SpecialLwStart = 0x168):
 * ground start, loop, hit, end, turn; then the same five in the air. */
#define FST_GROUND_START 0x168
#define FST_GROUND_LAST 0x16C
#define FST_AIR_START 0x16D
#define FST_AIR_LAST 0x171

#define FST_JC_FRAME 4         /* earliest jump out of shine */
#define FST_WAVESHINE_LAND 7   /* special landing begins, perfect waveshine */
#define FST_WAVESHINE_FREE 17  /* actionable again, perfect waveshine */
#define FST_GAP_FIRST 6        /* shine 1 -> shine 2 */
#define FST_GAP_NEXT 8         /* every later shine */
#define FST_TIMEOUT 40         /* frames after the shine before giving up */

static int fst_IsShine(int state)
{
    return state >= FST_GROUND_START && state <= FST_AIR_LAST;
}

static int fst_IsJump(int state)
{
    return state == ASID_JUMPF || state == ASID_JUMPB;
}

static int fst_IsDoubleJump(int state)
{
    return state == ASID_JUMPAERIALF || state == ASID_JUMPAERIALB;
}

/* ---- fox-jc-shine --------------------------------------------------------- */

enum { JCS_OPT_LENIENCY };
enum { JCS_WAIT, JCS_SHINE };

static EventOption jcs_options[] = {
    [JCS_OPT_LENIENCY] = COURSE_OPT_LENIENCY,
};

static struct {
    int frame;       /* frame of the shine (1 = the frame it came out) */
    int first_press; /* shine frame of the first jump press, 0 = none */
} jcs;

static const CourseRefInput jcs_reference[] = {
    { 0, 10, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { 0, 13, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { COURSE_REF_END },
};

static void jcs_Setup(CourseCtx* c)
{
    course_PlaceSolo(c, 0);
    jcs.frame = 0;
    jcs.first_press = 0;
}

static void jcs_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Shine (down+B) can be cancelled by a jump, and");
    sprintf(g->line[n++], "everything Fox does out of shine starts there.");
    sprintf(g->line[n++], "The shine comes out on frame 1. The first frame");
    sprintf(g->line[n++], "a jump works is frame %d: %d frames after down+B.",
            FST_JC_FRAME, FST_JC_FRAME - 1);
    sprintf(g->line[n++], "A jump pressed earlier is ignored, so pressing");
    sprintf(g->line[n++], "both at once does nothing.");
    g->line_count = n;
}

static void jcs_Think(CourseCtx* c)
{
    int lenient = course_Leniency(JCS_OPT_LENIENCY);

    switch (c->phase) {
    case JCS_WAIT:
        if (c->state == FST_GROUND_START && c->state_frames == 1) {
            course_Phase(c, JCS_SHINE);
            jcs.frame = 1;
            jcs.first_press = 0;
        }
        break;

    case JCS_SHINE:
        jcs.frame++;
        if (jcs.first_press == 0 &&
            (c->down & (PAD_BUTTON_X | PAD_BUTTON_Y)))
        {
            jcs.first_press = jcs.frame;
        }
        if (c->state == ASID_KNEEBEND) {
            int jumped = jcs.frame;
            course_Measure(jumped, FST_JC_FRAME);
            if (jumped - FST_JC_FRAME > lenient) {
                course_Result(c, 0, "Late: jumped on frame %d\nwant frame %d",
                              jumped, FST_JC_FRAME);
            } else if (jumped == FST_JC_FRAME) {
                course_Result(c, 1, "Frame perfect\njump on frame %d", jumped,
                              0);
            } else {
                course_Result(c, 1, "Jump on frame %d\n%d late", jumped,
                              jumped - FST_JC_FRAME);
            }
        } else if (!fst_IsShine(c->state) || jcs.frame > FST_TIMEOUT) {
            if (jcs.first_press > 0 && jcs.first_press < FST_JC_FRAME) {
                course_Measure(jcs.first_press, FST_JC_FRAME);
                course_Result(c, 0, "Too early: frame %d\nwant frame %d",
                              jcs.first_press, FST_JC_FRAME);
            } else {
                course_Result(c, 0, "No jump out of shine", 0, 0);
            }
        }
        break;
    }
}

static const CourseDrill Drill_FoxJcShine = {
    .Setup = jcs_Setup,
    .Think = jcs_Think,
    .options = jcs_options,
    .option_count = countof(jcs_options),
    .help = { "Shine (down+B), then jump on the first frame the",
              "shine allows it: 3 frames later.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = jcs_reference,
    .Guide = jcs_Guide,
};

/* ---- fox-waveshine -------------------------------------------------------- */

enum { WSH_OPT_LENIENCY };
enum { WSH_WAIT, WSH_SHINE, WSH_SQUAT, WSH_AIR, WSH_LAND };

static EventOption wsh_options[] = {
    [WSH_OPT_LENIENCY] = COURSE_OPT_LENIENCY,
};

static struct {
    int frame;      /* frame of the sequence (1 = the shine came out) */
    int land_frame; /* frame the special landing began */
    float start_x;
} wsh;

static const CourseRefInput wsh_reference[] = {
    { 0, 10, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { 0, 13, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 16, 2, 90, -90, 0, 0, PAD_TRIGGER_R, 140, 0 },
    { COURSE_REF_END },
};

static void wsh_Setup(CourseCtx* c)
{
    course_PlaceSolo(c, 0);
    wsh.frame = 0;
    wsh.land_frame = 0;
}

static void wsh_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Shine, jump out of it, wavedash: Fox slides");
    sprintf(g->line[n++], "after the opponent the shine pushed away.");
    sprintf(g->line[n++], "1. Down+B                      (frame 1)");
    sprintf(g->line[n++], "2. Jump                        (frame %d)",
            FST_JC_FRAME);
    sprintf(g->line[n++], "3. R + stick down and sideways (frame %d)",
            FST_WAVESHINE_LAND);
    sprintf(g->line[n++], "Perfect: you can act again on frame %d.",
            FST_WAVESHINE_FREE);
    g->line_count = n;
}

static void wsh_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    int lenient = course_Leniency(WSH_OPT_LENIENCY);

    if (c->phase != WSH_WAIT) {
        wsh.frame++;
    }
    switch (c->phase) {
    case WSH_WAIT:
        if (c->state == FST_GROUND_START && c->state_frames == 1) {
            course_Phase(c, WSH_SHINE);
            wsh.frame = 1;
            wsh.start_x = hd->phys.pos.X;
        }
        break;

    case WSH_SHINE:
        if (c->state == ASID_KNEEBEND) {
            course_Phase(c, WSH_SQUAT);
        } else if (!fst_IsShine(c->state) || wsh.frame > FST_TIMEOUT) {
            course_Result(c, 0, "No jump out of shine", 0, 0);
        }
        break;

    case WSH_SQUAT:
        if (c->state == ASID_KNEEBEND) {
            break;
        }
        course_Phase(c, WSH_AIR);
        /* fallthrough */
    case WSH_AIR:
        if (c->state == ASID_LANDINGFALLSPECIAL) {
            wsh.land_frame = wsh.frame;
            course_Phase(c, WSH_LAND);
        } else if (fst_IsShine(c->state)) {
            course_Result(c, 0, "Shined again\nair dodge, do not shine", 0, 0);
        } else if (c->timer > WD_JUMP_TIMEOUT + WD_DODGE_TIMEOUT) {
            course_Result(c, 0, "No wavedash\nair dodge leaving the ground",
                          0, 0);
        }
        break;

    case WSH_LAND:
        if (c->state == ASID_LANDINGFALLSPECIAL) {
            break;
        }
        {
            float slide = fabs(hd->phys.pos.X - wsh.start_x);
            int late = wsh.land_frame - FST_WAVESHINE_LAND;
            course_Measure(wsh.land_frame, FST_WAVESHINE_LAND);
            course_Report("free", wsh.frame);
            course_ReportF("slide", slide);
            if (slide < WD_MIN_SLIDE) {
                course_Result(c, 0, "No slide\nangle the stick sideways", 0,
                              0);
            } else if (late > lenient) {
                course_Result(c, 0, "Slow: landed on frame %d\nwant frame %d",
                              wsh.land_frame, FST_WAVESHINE_LAND);
            } else if (late == 0) {
                course_Result(c, 1, "Perfect waveshine\nfree on frame %d",
                              wsh.frame, 0);
            } else {
                course_Result(c, 1, "Waveshine, %d late\nfree on frame %d",
                              late, wsh.frame);
            }
        }
        break;
    }
}

static const CourseDrill Drill_FoxWaveshine = {
    .Setup = wsh_Setup,
    .Think = wsh_Think,
    .options = wsh_options,
    .option_count = countof(wsh_options),
    .help = { "Waveshine: down+B, jump 3 frames later, air dodge",
              "into the ground 3 frames after that.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = wsh_reference,
    .Guide = wsh_Guide,
};

/* ---- fox-multishine ------------------------------------------------------- */

enum { MSH_OPT_LENIENCY, MSH_OPT_COUNT };
enum { MSH_WAIT, MSH_CHAIN };

static const char* msh_opt_count[] = { "2", "3", "5", "8" };
static const int msh_counts[] = { 2, 3, 5, 8 };

static EventOption msh_options[] = {
    [MSH_OPT_LENIENCY] = COURSE_OPT_LENIENCY,
    [MSH_OPT_COUNT] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(msh_opt_count),
        .val = 1,
        .name = "Shines",
        .desc = { "How many shines in a row count as a success." },
        .values = msh_opt_count,
    },
};

static struct {
    int shines;   /* shines so far in this chain */
    int since;    /* frames since the last shine came out (1 = that frame) */
    int worst;    /* most frames any shine was late */
    int air_time; /* consecutive frames seen in a jump state */
} msh;

/* Eight shines: after the first, jump 5 frames after each shine (once Fox
 * is grounded again) and shine 3 frames after each jump. */
static const CourseRefInput msh_reference[] = {
    { 0, 10, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { 0, 13, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 16, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { 0, 21, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 24, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { 0, 29, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 32, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { 0, 37, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 40, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { 0, 45, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 48, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { 0, 53, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 56, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { 0, 61, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 64, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { COURSE_REF_END },
};

static void msh_Setup(CourseCtx* c)
{
    course_PlaceSolo(c, 0);
    msh.shines = 0;
    msh.since = 0;
    msh.worst = 0;
    msh.air_time = 0;
}

static void msh_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Shine, jump, and shine again before Fox leaves");
    sprintf(g->line[n++], "the ground: he lands at once and can repeat.");
    sprintf(g->line[n++], "Shine 1: frame 1.   Jump: frame %d.", FST_JC_FRAME);
    sprintf(g->line[n++], "Shine 2: frame %d (first airborne frame).",
            1 + FST_GAP_FIRST);
    sprintf(g->line[n++], "Then wait for the landing: jump %d frames after",
            5);
    sprintf(g->line[n++], "each shine, shine 3 frames after each jump.");
    sprintf(g->line[n++], "A jump too soon is the double jump: Fox rises.");
    sprintf(g->line[n++], "Perfect: a shine every %d frames.", FST_GAP_NEXT);
    g->line_count = n;
}

static void msh_End(CourseCtx* c, char* fmt)
{
    int want = msh_counts[Options_Main[OPT_COMMON_COUNT + MSH_OPT_COUNT].val];
    course_Measure(msh.shines, want);
    course_Report("shines", msh.shines);
    course_Report("worst_late", msh.worst);
    course_Result(c, 0, fmt, msh.shines, want);
}

static void msh_Think(CourseCtx* c)
{
    int lenient = course_Leniency(MSH_OPT_LENIENCY);
    int want = msh_counts[Options_Main[OPT_COMMON_COUNT + MSH_OPT_COUNT].val];
    int new_shine = (c->state == FST_GROUND_START ||
                     c->state == FST_AIR_START) &&
                    c->state_frames == 1;

    switch (c->phase) {
    case MSH_WAIT:
        if (c->state == FST_GROUND_START && c->state_frames == 1) {
            course_Phase(c, MSH_CHAIN);
            msh.shines = 1;
            msh.since = 1;
            msh.worst = 0;
            msh.air_time = 0;
        }
        break;

    case MSH_CHAIN:
        msh.since++;
        if (new_shine) {
            /* `since` counted the frames from the last shine to this one */
            int gap = msh.since - 1;
            int late = gap - (msh.shines == 1 ? FST_GAP_FIRST : FST_GAP_NEXT);
            if (late > msh.worst) {
                msh.worst = late;
            }
            msh.shines++;
            msh.since = 1;
            msh.air_time = 0;
            if (late > lenient) {
                msh_End(c, "Shine %d of %d was slow");
                break;
            }
            if (msh.shines >= want) {
                course_Measure(msh.shines, want);
                course_Report("shines", msh.shines);
                course_Report("worst_late", msh.worst);
                if (msh.worst <= 0) {
                    course_Result(c, 1, "%d shines\nframe perfect",
                                  msh.shines, 0);
                } else {
                    course_Result(c, 1, "%d shines\nworst %d late",
                                  msh.shines, msh.worst);
                }
            }
        } else if (fst_IsDoubleJump(c->state)) {
            msh_End(c, "Double jump at %d of %d\njump after landing");
        } else if (fst_IsJump(c->state)) {
            /* Each frame of jump is a frame the shine is late. */
            if (++msh.air_time > lenient) {
                msh_End(c, "Left the ground at %d of %d\nshine sooner");
            }
        } else if (c->state == ASID_KNEEBEND || fst_IsShine(c->state)) {
            if (msh.since > FST_TIMEOUT) {
                msh_End(c, "Stopped at %d of %d");
            }
        } else {
            msh_End(c, "Chain ended at %d of %d");
        }
        break;
    }
}

static const CourseDrill Drill_FoxMultishine = {
    .Setup = msh_Setup,
    .Think = msh_Think,
    .options = msh_options,
    .option_count = countof(msh_options),
    .help = { "Multishine: shine, jump, shine as you leave the",
              "ground, wait to land, jump, shine...",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = msh_reference,
    .Guide = msh_Guide,
};
