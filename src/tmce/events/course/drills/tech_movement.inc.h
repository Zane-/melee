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


/* ---- the demonstration for L-cancel and SHFFL --------------------------- */

/* Built for the character and the aerial: jump, the aerial, fast fall, the
 * trigger press. The landing is predicted from the hop speed, gravity and
 * fast-fall speed (the game's own recursion: y += v, v -= gravity), so no
 * scouting hop is needed; the simulator's traces put the landing one or two
 * frames after the predicted height crosses zero, and the L-cancel window
 * (7 frames) absorbs that. The aerial is timed to be a few frames past its
 * first hit when the fighter lands: started at takeoff, many aerials end
 * in the air or autocancel (Marth's neutral air, most slow down airs).
 * Each demonstration shows the next aerial: neutral, forward, back, up,
 * down. */
#define MV_REF_START 10       /* script frame of the jump press */
#define MV_REF_TAP_FROM 4     /* first airborne frame with a stick-down tap */
#define MV_REF_TAP_EVERY 3
#define MV_REF_PAST_HIT 4     /* aerial frames past its first hit at landing */
#define MV_REF_PRESS_BEFORE 2 /* trigger this long before the height is 0 */
#define MV_REF_MAX 40

static CourseRefInput mv_ref[MV_REF_MAX];

static int mv_IsTap(int k)
{
    return k >= MV_REF_TAP_FROM &&
           (k - MV_REF_TAP_FROM) % MV_REF_TAP_EVERY == 0;
}

static const CourseRefInput* mv_BuildAerialReference(CourseCtx* c)
{
    static const CourseRefInput aerial_input[5] = {
        { 0, 0, 1, 0, 0, 0, 0, PAD_BUTTON_A, 0, 0 }, /* neutral */
        { 0, 0, 1, 0, 0, 127, 0, 0, 0, 0 },          /* forward */
        { 0, 0, 1, 0, 0, -127, 0, 0, 0, 0 },         /* back */
        { 0, 0, 1, 0, 0, 0, 127, 0, 0, 0 },          /* up */
        { 0, 0, 1, 0, 0, 0, -127, 0, 0, 0 },         /* down */
    };
    static const CourseRefInput end = { COURSE_REF_END };
    FighterData* hd = c->hd;
    const CourseFighterData* me = course_Fighter(hd);
    int which = (course_DemoCount() + 4) % 5; /* the first one: neutral */
    const CourseMoveData* m = &me->move[CMOVE_NAIR + which];
    /* script frame of airborne frame 1 */
    int air0 = MV_REF_START + me->jump_squat;
    float v = me->hop_v, y = 0;
    int fast = 0, cross, aerial, k, n = 0;

    for (cross = 1; cross < 200; cross++) {
        if (!fast && v < 0 && mv_IsTap(cross)) {
            v = -hd->attr.fastfall_velocity;
            fast = 1;
        }
        y += v;
        if (y < 0) {
            break;
        }
        v -= hd->attr.gravity;
        if (v < -hd->attr.terminal_velocity && !fast) {
            v = -hd->attr.terminal_velocity;
        }
    }
    aerial = cross - (m->hit + MV_REF_PAST_HIT);
    if (aerial < 1) {
        aerial = 1;
    }

    memset(mv_ref, 0, sizeof(mv_ref));
    mv_ref[n] = aerial_input[0];
    mv_ref[n].buttons = PAD_BUTTON_X;
    mv_ref[n++].frame = MV_REF_START;
    mv_ref[n] = aerial_input[which];
    mv_ref[n++].frame = air0 + aerial - 1;
    for (k = MV_REF_TAP_FROM; k <= cross && n < MV_REF_MAX - 4; k++) {
        /* no tap on the aerial's frame: down with A is a down air */
        if (mv_IsTap(k) && k != aerial) {
            mv_ref[n].ly = -127;
            mv_ref[n].hold = 1;
            mv_ref[n++].frame = air0 + k - 1;
        }
    }
    /* Two presses five frames apart: for some characters (Mario, Luigi,
     * Peach, Zelda...) the landing comes up to six frames after the
     * prediction, past the first press's window. A press too early costs
     * nothing, and the second lands in the landing lag when the first was
     * right. */
    mv_ref[n].buttons = PAD_TRIGGER_Z;
    mv_ref[n].hold = 1;
    mv_ref[n++].frame = air0 + cross - 1 - MV_REF_PRESS_BEFORE;
    mv_ref[n].buttons = PAD_TRIGGER_Z;
    mv_ref[n].hold = 1;
    mv_ref[n++].frame = air0 + cross - 1 - MV_REF_PRESS_BEFORE + 5;
    mv_ref[n] = end;
    return mv_ref;
}

/* ---- universal-l-cancel --------------------------------------------------- */

enum { LC_WAIT, LC_AIR, LC_LAND };

static struct {
    int air_frame;   /* frames since the aerial began */
    int press_frame; /* air_frame of the last trigger press, -1 = none */
    int land_frame;  /* air_frame the landing began */
    int land_state;
    int lag;         /* frames of landing so far */
} lc;

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
}

static void lc_Think(CourseCtx* c)
{
    switch (c->phase) {
    case LC_WAIT:
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
            course_Phase(c, LC_LAND);
            lc.land_frame = lc.air_frame;
            lc.land_state = c->state;
            lc.lag = 1;
        } else if (!mv_IsAerial(c->state)) {
            if (c->state == ASID_LANDING) {
                course_Result(c, 0, "No landing lag to cancel\n"
                                    "attack later in the jump",
                              0, 0);
            } else {
                course_Phase(c, LC_WAIT); /* the aerial ended in the air */
            }
        } else if (lc.air_frame > MV_AIR_TIMEOUT) {
            course_Phase(c, LC_WAIT);
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
    .flow = 1,
    .Setup = lc_Setup,
    .Think = lc_Think,
    .help = { "L-cancel: jump, attack in the air, and press L, R",
              "or Z just before you land.",
              "D-Pad up: guide. D-Pad down: reset." },
    .BuildReference = mv_BuildAerialReference,
    .Guide = lc_Guide,
};

/* ---- universal-shffl ------------------------------------------------------ */

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
            course_Phase(c, SF_LAND);
            sf.land_frame = sf.frame;
            sf.land_state = c->state;
            sf.lag = 1;
        } else if (c->state == ASID_LANDING || c->state == ASID_WAIT) {
            if (sf.aerial) {
                course_Result(c, 0, "No landing lag to cancel\n"
                                    "attack later in the jump",
                              0, 0);
            } else {
                course_Phase(c, SF_WAIT); /* a plain jump: ignore */
            }
        } else if (sf.frame > MV_AIR_TIMEOUT) {
            course_Phase(c, SF_WAIT);
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
    .flow = 1,
    .Setup = sf_Setup,
    .Think = sf_Think,
    .help = { "SHFFL: short hop, aerial attack, tap down to fast",
              "fall, L-cancel the landing.",
              "D-Pad up: guide. D-Pad down: reset." },
    .BuildReference = mv_BuildAerialReference,
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
        } else if (c->state == ASID_RUN && dd.dashes < 2) {
            course_Phase(c, DD_WAIT); /* just running */
        } else if (c->state == ASID_RUN) {
            dd_Fail(c, "Ran after %d of %d dashes\nturn sooner");
        } else if (c->state == ASID_WAIT && ++dd.idle <= 2) {
            /* a dash that ran out: allowed for a moment */
        } else if (dd.dashes >= 2) {
            dd_Fail(c, "Stopped after %d of %d dashes");
        } else {
            course_Phase(c, DD_WAIT); /* one dash is not a dance */
        }
        break;
    }
}

static const CourseDrill Drill_TechDashDance = {
    .flow = 1,
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
        } else if (c->state != ASID_DASH && c->state != ASID_RUN &&
                   c->state != ASID_TURN && c->state != ASID_CATCHDASH)
        {
            course_Phase(c, JG_WAIT); /* did something else */
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
    .flow = 1,
    .Setup = jg_Setup,
    .Think = jg_Think,
    .help = { "JC grab: while running, jump and press Z during",
              "jump squat for a standing grab.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = jg_reference,
    .Guide = jg_Guide,
};
