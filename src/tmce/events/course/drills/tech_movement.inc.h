/*
 * universal-l-cancel, universal-shffl, universal-dash-dance,
 * universal-jc-grab. Specs: data/courses/universal.md. Included by
 * ../event.c.
 *
 * Measured with Fox in the simulator (2026-11-12):
 *   - Neutral air landing lasts 15 frames, 7 when L-cancelled (the table's
 *     `land` / `land_l`). The trigger press counts when it is 0 to 6 frames
 *     before the frame the landing begins; 7 before is too early.
 *   - Holding down while falling lands a short hop down air 5 frames
 *     sooner (fast fall).
 *   - Dash turns into run after 11 frames of holding the stick; reversing
 *     earlier gives one frame of Turn and a new Dash.
 *   - Running, jump then Z 1 or 2 frames later: jump squat into the
 *     standing grab (Catch). Z on the same frame as jump is the dash grab
 *     (CatchDash); Z 3 frames later comes out as an aerial.
 */

static int mv_IsAerial(int state)
{
    return state >= ASID_ATTACKAIRN && state <= ASID_ATTACKAIRLW;
}

static int mv_IsAerialLanding(int state)
{
    return state >= ASID_LANDINGAIRN && state <= ASID_LANDINGAIRLW;
}

/* The landing of aerial `landing_state` was L-cancelled if it lasted
 * `frames`. */
static int mv_WasLCancelled(CourseCtx* c, int landing_state, int frames)
{
    const CourseMoveData* m =
        &course_Fighter(c->hd)
             ->move[CMOVE_NAIR + (landing_state - ASID_LANDINGAIRN)];
    return frames * 2 < m->land + m->land_l;
}

#define MV_TRIGGERS (PAD_TRIGGER_L | PAD_TRIGGER_R | PAD_TRIGGER_Z)
/* Latest and earliest frames before landing a trigger press counts. */
#define MV_LCANCEL_WINDOW 6
#define MV_AIR_TIMEOUT 150
/* When the demonstrations start their aerial, in frames from the landing. */
#define MV_REF_AERIAL_AT (-10)

/* ---- universal-l-cancel --------------------------------------------------- */

enum { LC_MARK_LAND = 1 };
enum { LC_WAIT, LC_AIR, LC_LAND };

static struct {
    int air_frame;   /* frames since the aerial began */
    int press_frame; /* air_frame of the last trigger press, -1 = none */
    int land_frame;  /* air_frame the landing began */
    int land_state;
    int lag;         /* frames of landing so far */
} lc;

/* A stick-down tap every third frame from 6 frames after takeoff: the
 * first one after the top of the hop is the fast fall, whatever the
 * character's hop lasts. In both passes, so the landing is the same. */
#define SF_TAP(n) { 0, 16 + 3 * (n), 1, 0, -127, 0, 0, 0, 0, 1 }

/* Short hop and fast fall in both passes; the observing pass finds the
 * landing, and the second pass puts an up air (C-stick) 10 frames and the
 * trigger 4 frames before it. The aerial is timed against the landing
 * because no aerial started at takeoff is still out when every character
 * lands, and up air because most down airs autocancel that close to their
 * start. Checked for all 26 characters in the simulator (2026-11-12):
 * this demonstration fails for Kirby and Sheik (and the SHFFL one for
 * Mr. Game & Watch, whose up air cannot be L-cancelled); they need their
 * own aerial when their courses are built. */
static const CourseRefInput lc_reference[] = {
    { 0, 10, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    SF_TAP(0),  SF_TAP(1),  SF_TAP(2),  SF_TAP(3),  SF_TAP(4),  SF_TAP(5),
    SF_TAP(6),  SF_TAP(7),  SF_TAP(8),  SF_TAP(9),  SF_TAP(10), SF_TAP(11),
    { LC_MARK_LAND, MV_REF_AERIAL_AT, 1, 0, 0, 0, 127, 0, 0, 0 },
    { LC_MARK_LAND, -4, 1, 0, 0, 0, 0, PAD_TRIGGER_Z, 0, 0 },
    { COURSE_REF_END },
};

static void lc_Setup(CourseCtx* c)
{
    course_PlaceSolo(c, 0);
    lc.press_frame = -1;
}

static void lc_Guide(CourseCtx* c, CourseGuide* g)
{
    const CourseMoveData* m = &course_Fighter(c->hd)->move[CMOVE_DAIR];
    int n = 0;
    sprintf(g->line[n++], "Landing during an aerial attack costs landing");
    sprintf(g->line[n++], "lag. Pressing L, R or Z just before you touch");
    sprintf(g->line[n++], "the ground halves it.");
    sprintf(g->line[n++], "Your down air: %d frames, %d with the cancel.",
            m->land, m->land_l);
    sprintf(g->line[n++], "The press counts in the last 7 frames of the");
    sprintf(g->line[n++], "fall. Jump, attack late, press as you land.");
    g->line_count = n;
    g->timeline_from = "frames before the landing (1 = you land)";
}

static void lc_Think(CourseCtx* c)
{
    switch (c->phase) {
    case LC_WAIT:
        if (c->state == ASID_LANDING) {
            /* a jump without an attack (the demonstration's first pass
             * does this to find the landing) */
            course_Mark(c, LC_MARK_LAND);
            course_Result(c, 0, "No aerial attack", 0, 0);
            break;
        }
        if (mv_IsAerial(c->state)) {
            course_Phase(c, LC_AIR);
            lc.air_frame = 0;
            lc.press_frame = -1;
        }
        break;

    case LC_AIR:
        lc.air_frame++;
        if (c->down & MV_TRIGGERS) {
            lc.press_frame = lc.air_frame;
        }
        if (mv_IsAerialLanding(c->state)) {
            course_Mark(c, LC_MARK_LAND);
            course_Phase(c, LC_LAND);
            lc.land_frame = lc.air_frame;
            lc.land_state = c->state;
            lc.lag = 1;
        } else if (!mv_IsAerial(c->state)) {
            course_Result(c, 0, "Landed after the attack\nattack later", 0,
                          0);
        } else if (lc.air_frame > MV_AIR_TIMEOUT) {
            course_Result(c, 0, "Did not land", 0, 0);
        }
        break;

    case LC_LAND:
        if (c->state == lc.land_state) {
            lc.lag++;
            if (lc.press_frame < 0 && (c->down & MV_TRIGGERS)) {
                lc.press_frame = lc.land_frame + lc.lag - 1;
            }
            break;
        }
        {
            int before = lc.land_frame - lc.press_frame;
            course_Report("lag", lc.lag);
            if (lc.press_frame >= 0) {
                course_Report("before", before);
            }
            if (mv_WasLCancelled(c, lc.land_state, lc.lag)) {
                if (lc.press_frame >= 0) {
                    course_Result(c, 1, "L-cancel! %d frames lag\n"
                                        "pressed %d before landing",
                                  lc.lag, before);
                } else {
                    course_Result(c, 1, "L-cancel! %d frames lag", lc.lag,
                                  0);
                }
            } else if (lc.press_frame < 0) {
                course_Result(c, 0, "No press: %d frames lag\n"
                                    "L, R or Z as you land",
                              lc.lag, 0);
            } else if (before > MV_LCANCEL_WINDOW) {
                course_Result(c, 0, "Too early: %d frames before\n"
                                    "landing, at most %d",
                              before, MV_LCANCEL_WINDOW);
            } else {
                course_Result(c, 0, "Too late: %d frames after\nlanding",
                              -before, 0);
            }
        }
        break;
    }
}

static const CourseDrill Drill_TechLCancel = {
    .Setup = lc_Setup,
    .Think = lc_Think,
    .help = { "L-cancel: jump, attack in the air, and press L, R",
              "or Z just before you land.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = lc_reference,
    .Guide = lc_Guide,
};

/* ---- universal-shffl ------------------------------------------------------ */

enum { SF_MARK_LAND = 1 };
enum { SF_WAIT, SF_SQUAT, SF_AIR, SF_LAND };

static struct {
    int short_hop;
    int aerial;      /* an aerial came out */
    int fast_fall;
    int frame;       /* frames since leaving the ground */
    int press_frame;
    int land_frame;
    int land_state;
    int lag;
} sf;

/* As lc_reference. */
static const CourseRefInput sf_reference[] = {
    { 0, 10, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    SF_TAP(0),  SF_TAP(1),  SF_TAP(2),  SF_TAP(3),  SF_TAP(4),  SF_TAP(5),
    SF_TAP(6),  SF_TAP(7),  SF_TAP(8),  SF_TAP(9),  SF_TAP(10), SF_TAP(11),
    { SF_MARK_LAND, MV_REF_AERIAL_AT, 1, 0, 0, 0, 127, 0, 0, 0 },
    { SF_MARK_LAND, -4, 1, 0, 0, 0, 0, PAD_TRIGGER_Z, 0, 0 },
    { COURSE_REF_END },
};

static void sf_Setup(CourseCtx* c)
{
    course_PlaceSolo(c, 0);
    memset(&sf, 0, sizeof(sf));
    sf.press_frame = -1;
}

static void sf_Guide(CourseCtx* c, CourseGuide* g)
{
    const CourseFighterData* me = course_Fighter(c->hd);
    int n = 0;
    sprintf(g->line[n++], "Short Hop, Fast Fall, L-cancel: the fastest way");
    sprintf(g->line[n++], "to put an aerial attack on the ground.");
    sprintf(g->line[n++], "1. Short hop: release jump within %d frames.",
            me->jump_squat - 1);
    sprintf(g->line[n++], "2. Attack in the air.");
    sprintf(g->line[n++], "3. Fast fall: tap down once you start falling.");
    sprintf(g->line[n++], "4. L-cancel: L, R or Z in the last 7 frames.");
    sprintf(g->line[n++], "The verdict names the first part you missed.");
    g->line_count = n;
    g->timeline_from = "frames before the landing (1 = you land)";
}

static void sf_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    const CourseFighterData* me = course_Fighter(hd);

    switch (c->phase) {
    case SF_WAIT:
        if (c->state == ASID_KNEEBEND) {
            course_Phase(c, SF_SQUAT);
        }
        break;

    case SF_SQUAT:
        if (c->state == ASID_KNEEBEND) {
            break;
        }
        memset(&sf, 0, sizeof(sf));
        sf.press_frame = -1;
        sf.short_hop = hd->phys.self_vel.Y < (me->hop_v + me->jump_v) / 2;
        course_Phase(c, SF_AIR);
        /* fallthrough */
    case SF_AIR:
        sf.frame++;
        if (c->down & MV_TRIGGERS) {
            sf.press_frame = sf.frame;
        }
        if (hd->flags.is_fastfall) {
            sf.fast_fall = 1;
        }
        if (mv_IsAerial(c->state)) {
            sf.aerial = 1;
        } else if (mv_IsAerialLanding(c->state)) {
            course_Mark(c, SF_MARK_LAND);
            course_Phase(c, SF_LAND);
            sf.land_frame = sf.frame;
            sf.land_state = c->state;
            sf.lag = 1;
        } else if (c->state == ASID_LANDING || c->state == ASID_WAIT) {
            course_Mark(c, SF_MARK_LAND);
            if (sf.aerial) {
                course_Result(c, 0, "Landed after the attack\nattack later",
                              0, 0);
            } else {
                course_Result(c, 0, "No aerial attack", 0, 0);
            }
        } else if (sf.frame > MV_AIR_TIMEOUT) {
            course_Result(c, 0, "Did not land", 0, 0);
        }
        break;

    case SF_LAND:
        if (c->state == sf.land_state) {
            sf.lag++;
            break;
        }
        {
            int lcancel = mv_WasLCancelled(c, sf.land_state, sf.lag);
            /* frames from leaving the ground to acting again */
            int total = sf.land_frame + sf.lag;
            course_Measure(sf.short_hop + sf.fast_fall + lcancel, 3);
            course_Report("short_hop", sf.short_hop);
            course_Report("fast_fall", sf.fast_fall);
            course_Report("l_cancel", lcancel);
            course_Report("total", total);
            if (!sf.short_hop) {
                course_Result(c, 0, "Full hop\nrelease jump within %d frames",
                              me->jump_squat - 1, 0);
            } else if (!sf.fast_fall) {
                course_Result(c, 0, "No fast fall\ntap down as you fall", 0,
                              0);
            } else if (!lcancel) {
                if (sf.press_frame < 0) {
                    course_Result(c, 0, "No L-cancel\nL, R or Z as you land",
                                  0, 0);
                } else {
                    course_Result(c, 0, "L-cancel missed: pressed\n"
                                        "%d frames before landing",
                                  sf.land_frame - sf.press_frame, 0);
                }
            } else {
                course_Result(c, 1, "SHFFL!\nacting again after %d frames",
                              total, 0);
            }
        }
        break;
    }
}

static const CourseDrill Drill_TechShffl = {
    .Setup = sf_Setup,
    .Think = sf_Think,
    .help = { "SHFFL: short hop, aerial attack, tap down to fast",
              "fall, L-cancel the landing.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = sf_reference,
    .Guide = sf_Guide,
};

/* ---- universal-dash-dance ------------------------------------------------- */

enum { DD_OPT_COUNT };
enum { DD_WAIT, DD_DANCE };

static const char* dd_opt_count[] = { "4", "6", "10", "20" };
static const int dd_counts[] = { 4, 6, 10, 20 };

static EventOption dd_options[] = {
    [DD_OPT_COUNT] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(dd_opt_count),
        .val = 1,
        .name = "Dashes",
        .desc = { "How many dashes in a row count as a success." },
        .values = dd_opt_count,
    },
};

static struct {
    int dashes;
    int length;  /* frames of the current dash */
    int longest;
    int idle;    /* frames standing between dashes */
} dd;

/* Seven frames each way, twenty times: short enough for every character's
 * dash. */
#define DD_PAIR(n)                                                            \
    { 0, 10 + 14 * (n), 7, 127, 0, 0, 0, 0, 0, 0 },                           \
    { 0, 17 + 14 * (n), 7, -127, 0, 0, 0, 0, 0, 0 }

static const CourseRefInput dd_reference[] = {
    DD_PAIR(0), DD_PAIR(1), DD_PAIR(2), DD_PAIR(3), DD_PAIR(4),
    DD_PAIR(5), DD_PAIR(6), DD_PAIR(7), DD_PAIR(8), DD_PAIR(9),
    { COURSE_REF_END },
};

static void dd_Setup(CourseCtx* c)
{
    course_PlaceSolo(c, 0);
    memset(&dd, 0, sizeof(dd));
}

static void dd_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Dash one way, then the other before the dash");
    sprintf(g->line[n++], "becomes a run. You stay mobile and can leave in");
    sprintf(g->line[n++], "either direction at any moment.");
    sprintf(g->line[n++], "Flick the stick fully left and right. Hold a");
    sprintf(g->line[n++], "direction too long and you run, and turning");
    sprintf(g->line[n++], "around out of a run is slow.");
    sprintf(g->line[n++], "The verdict shows your longest dash in frames.");
    g->line_count = n;
}

static void dd_Fail(CourseCtx* c, char* fmt)
{
    int want = dd_counts[Options_Main[OPT_COMMON_COUNT + DD_OPT_COUNT].val];
    course_Measure(dd.dashes, want);
    course_Report("dashes", dd.dashes);
    course_Result(c, 0, fmt, dd.dashes, want);
}

static void dd_Think(CourseCtx* c)
{
    int want = dd_counts[Options_Main[OPT_COMMON_COUNT + DD_OPT_COUNT].val];

    switch (c->phase) {
    case DD_WAIT:
        if (c->state == ASID_DASH) {
            course_Phase(c, DD_DANCE);
            dd.dashes = 1;
            dd.length = 1;
            dd.longest = 1;
            dd.idle = 0;
        }
        break;

    case DD_DANCE:
        if (c->state == ASID_DASH) {
            if (c->state_frames == 1) {
                dd.dashes++;
                dd.length = 0;
                if (dd.dashes >= want) {
                    course_Measure(dd.dashes, want);
                    course_Report("dashes", dd.dashes);
                    course_Report("longest", dd.longest);
                    course_Result(c, 1, "%d dashes\nlongest %d frames",
                                  dd.dashes, dd.longest);
                    break;
                }
            }
            dd.length++;
            dd.idle = 0;
            if (dd.length > dd.longest) {
                dd.longest = dd.length;
            }
        } else if (c->state == ASID_TURN) {
            /* the frame between two dashes */
        } else if (c->state == ASID_RUN) {
            dd_Fail(c, "Ran after %d of %d dashes\nturn sooner");
        } else if (c->state == ASID_WAIT && ++dd.idle <= 2) {
            /* a dash that ran out: allowed for a moment */
        } else {
            dd_Fail(c, "Stopped after %d of %d dashes");
        }
        break;
    }
}

static const CourseDrill Drill_TechDashDance = {
    .Setup = dd_Setup,
    .Think = dd_Think,
    .options = dd_options,
    .option_count = countof(dd_options),
    .help = { "Dash dance: dash left and right, turning before",
              "the dash becomes a run.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = dd_reference,
    .Guide = dd_Guide,
};

/* ---- universal-jc-grab ---------------------------------------------------- */

enum { JG_WAIT, JG_MOVING, JG_SQUAT };

static struct {
    int squat_frames;
} jg;

/* Dash for 14 frames, jump, Z on the next frame. */
static const CourseRefInput jg_reference[] = {
    { 0, 10, 16, 127, 0, 0, 0, 0, 0, 0 },
    { 0, 24, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 25, 1, 0, 0, 0, 0, PAD_TRIGGER_Z, 0, 0 },
    { COURSE_REF_END },
};

static void jg_Setup(CourseCtx* c)
{
    course_PlaceSolo(c, -30.0F);
    jg.squat_frames = 0;
}

static void jg_Guide(CourseCtx* c, CourseGuide* g)
{
    const CourseFighterData* me = course_Fighter(c->hd);
    const CourseMoveData* grab = &me->move[CMOVE_GRAB];
    const CourseMoveData* dash = &me->move[CMOVE_DASH_GRAB];
    int n = 0;
    sprintf(g->line[n++], "Grabbing while you run gives the slow dash grab.");
    sprintf(g->line[n++], "Jump first and grab during jump squat: the jump");
    sprintf(g->line[n++], "is cancelled and you get your standing grab.");
    sprintf(g->line[n++], "Standing grab: %d frames. Dash grab: %d.",
            grab->total, dash->total);
    sprintf(g->line[n++], "1. Dash or run.   2. Jump (X or Y).");
    sprintf(g->line[n++], "3. Z within %d frames after the jump.",
            me->jump_squat - 1);
    sprintf(g->line[n++], "Both at once is still the dash grab.");
    g->line_count = n;
}

static void jg_Think(CourseCtx* c)
{
    const CourseFighterData* me = course_Fighter(c->hd);

    switch (c->phase) {
    case JG_WAIT:
        if (c->state == ASID_DASH || c->state == ASID_RUN) {
            course_Phase(c, JG_MOVING);
        }
        break;

    case JG_MOVING:
        if (c->state == ASID_KNEEBEND) {
            course_Phase(c, JG_SQUAT);
            jg.squat_frames = 1;
        } else if (c->state == ASID_CATCHDASH) {
            course_Result(c, 0, "Dash grab\njump first, then Z", 0, 0);
        } else if (c->state == ASID_CATCH) {
            course_Result(c, 0, "Standing grab without a run\ndash first", 0,
                          0);
        } else if (c->state == ASID_WAIT) {
            course_Phase(c, JG_WAIT);
        }
        break;

    case JG_SQUAT:
        if (c->state == ASID_KNEEBEND) {
            jg.squat_frames++;
        } else if (c->state == ASID_CATCH) {
            /* Z came this many frames after the jump */
            course_Measure(jg.squat_frames, 1);
            course_Result(c, 1, "JC grab!\nZ %d after the jump",
                          jg.squat_frames, 0);
        } else {
            course_Result(c, 0, "Jumped: Z too late\nwithin %d frames",
                          me->jump_squat - 1, 0);
        }
        break;
    }
}

static const CourseDrill Drill_TechJcGrab = {
    .Setup = jg_Setup,
    .Think = jg_Think,
    .help = { "JC grab: while running, jump and press Z during",
              "jump squat for a standing grab.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = jg_reference,
    .Guide = jg_Guide,
};
