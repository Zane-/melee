/*
 * fox-shine-grab and fox-shffl-nair-shine: Fox's two basic ways through
 * and onto a shield. Specs: data/courses/fox.md (Tech 9, 10). Included by
 * ../event.c.
 *
 * The CPU (Marth) stands next to the player and holds a shield that does
 * not shrink (course_CpuShield).
 *
 * Measured with Fox on Marth's shield in the simulator (2026-11-12).
 * Frame 1 is the frame of the down-B:
 *   - the shine's hit on shield freezes Fox for 3 frames, so the earliest
 *     jump out of it is frame 7, not 4; a jump on frame 6 is ignored;
 *   - jump on 7, Z on 8: the standing grab starts on frame 8 and takes
 *     Marth 6 frames later. Marth's shieldstun ends on frame 9.
 */

/* Distance between the two at the start: the shine reaches the shield and
 * the grab still reaches after the shine's pushback. */
#define FPR_DISTANCE 6.7F
#define FPR_TIMEOUT 60

static int fpr_CpuGrabbed(CourseCtx* c)
{
    return c->cpu_state >= ASID_CAPTUREPULLEDHI &&
           c->cpu_state <= ASID_CAPTUREFOOT;
}

static void fpr_Place(CourseCtx* c)
{
    float hmn_x = -c->side * (FPR_DISTANCE / 2);
    course_Place(c, hmn_x, hmn_x + c->side * FPR_DISTANCE, 0, 0);
}

/* ---- fox-shine-grab ------------------------------------------------------- */

#define SG_GRAB_FRAME 8 /* the grab's first frame when frame perfect */

enum { SG_OPT_LENIENCY };
enum { SG_WAIT, SG_SHINE, SG_SQUAT, SG_GRAB };

static EventOption sg_options[] = {
    [SG_OPT_LENIENCY] = COURSE_OPT_LENIENCY,
};

static struct {
    int frame;      /* 1 = the shine came out */
    int on_shield;  /* the shine hit the shield */
    int grab_frame; /* frame the grab started */
} sg;

static const CourseRefInput sg_reference[] = {
    { 0, 20, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { 0, 26, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 27, 1, 0, 0, 0, 0, PAD_TRIGGER_Z, 0, 0 },
    { COURSE_REF_END },
};

static void sg_Setup(CourseCtx* c)
{
    fpr_Place(c);
    memset(&sg, 0, sizeof(sg));
}

static void sg_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "A shield blocks the shine, but not a grab.");
    sprintf(g->line[n++], "Shine the shield, jump-cancel the shine, and");
    sprintf(g->line[n++], "grab during jump squat (a jump-cancelled grab).");
    sprintf(g->line[n++], "On shield the shine freezes you for 3 frames:");
    sprintf(g->line[n++], "the jump works from frame %d, not 4.",
            SG_GRAB_FRAME - 1);
    sprintf(g->line[n++], "Perfect: down+B, jump on %d, Z on %d.",
            SG_GRAB_FRAME - 1, SG_GRAB_FRAME);
    g->line_count = n;
}

static void sg_Think(CourseCtx* c)
{
    int lenient = course_Leniency(SG_OPT_LENIENCY);

    course_CpuShield(c);
    if (c->phase != SG_WAIT) {
        sg.frame++;
        if (c->cpu_state == ASID_GUARDSETOFF && sg.frame <= 3) {
            sg.on_shield = 1;
        }
    }
    switch (c->phase) {
    case SG_WAIT:
        if (c->state == FST_GROUND_START && c->state_frames == 1) {
            course_Phase(c, SG_SHINE);
            sg.frame = 1;
            sg.on_shield = c->cpu_state == ASID_GUARDSETOFF;
        } else if (c->state == ASID_CATCH || c->state == ASID_CATCHDASH) {
            course_Result(c, 0, "Grab without the shine\nshine first", 0, 0);
        }
        break;

    case SG_SHINE:
        if (c->state == ASID_KNEEBEND) {
            course_Phase(c, SG_SQUAT);
        } else if (!fst_IsShine(c->state) || sg.frame > FPR_TIMEOUT) {
            course_Result(c, 0, "No jump out of shine", 0, 0);
        }
        break;

    case SG_SQUAT:
        if (c->state == ASID_KNEEBEND) {
            break;
        }
        if (c->state != ASID_CATCH) {
            course_Result(c, 0, "Jumped: Z too late\nZ right after the jump",
                          0, 0);
            break;
        }
        sg.grab_frame = sg.frame;
        course_Phase(c, SG_GRAB);
        /* fallthrough */
    case SG_GRAB:
        if (fpr_CpuGrabbed(c) || c->state == ASID_CATCHPULL ||
            c->state == ASID_CATCHWAIT)
        {
            int late = sg.grab_frame - SG_GRAB_FRAME;
            course_Measure(sg.grab_frame, SG_GRAB_FRAME);
            course_Report("on_shield", sg.on_shield);
            if (!sg.on_shield) {
                course_Result(c, 0, "The shine missed the shield", 0, 0);
            } else if (late > lenient) {
                course_Result(c, 0, "Slow: grab on frame %d\nwant frame %d",
                              sg.grab_frame, SG_GRAB_FRAME);
            } else if (late <= 0) {
                course_Result(c, 1, "Perfect shine-grab\ngrab on frame %d",
                              sg.grab_frame, 0);
            } else {
                course_Result(c, 1, "Shine-grab, %d late\ngrab on frame %d",
                              late, sg.grab_frame);
            }
        } else if (c->state != ASID_CATCH) {
            course_Measure(sg.grab_frame, SG_GRAB_FRAME);
            course_Result(c, 0, "The grab missed", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_FoxShineGrab = {
    .Setup = sg_Setup,
    .Think = sg_Think,
    .options = sg_options,
    .option_count = countof(sg_options),
    .help = { "Shine-grab: shine the shield, jump, and press Z",
              "during jump squat.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = sg_reference,
    .Guide = sg_Guide,
};

/* ---- fox-shffl-nair-shine ------------------------------------------------- */

enum { NS_MARK_LAND = 1 };
enum { NS_OPT_LENIENCY };
enum { NS_WAIT, NS_AIR, NS_LAND, NS_AFTER };

static EventOption ns_options[] = {
    [NS_OPT_LENIENCY] = COURSE_OPT_LENIENCY,
};

static struct {
    int frame;      /* frames since the aerial began */
    int on_shield;  /* the aerial hit the shield */
    int land_frame;
    int land_state;
    int lag;
    int wait;       /* frames after the landing ended without a shine */
    int stun_end;   /* frame the CPU's shieldstun ended, 0 = still in it */
} ns;

/* Short hop, neutral air at once, fast fall; trigger and shine against
 * the landing the observing pass saw. */
static const CourseRefInput ns_reference[] = {
    { 0, 20, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 23, 1, 0, 0, 0, 0, PAD_BUTTON_A, 0, 0 },
    { NS_MARK_LAND, -4, 1, 0, 0, 0, 0, PAD_TRIGGER_Z, 0, 0 },
    { NS_MARK_LAND, 6, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { COURSE_REF_END },
};

static void ns_Setup(CourseCtx* c)
{
    fpr_Place(c);
    memset(&ns, 0, sizeof(ns));
}

static void ns_Guide(CourseCtx* c, CourseGuide* g)
{
    const CourseMoveData* m = &course_Fighter(c->hd)->move[CMOVE_NAIR];
    int n = 0;
    sprintf(g->line[n++], "The start of Fox's shield pressure: an aerial");
    sprintf(g->line[n++], "on the shield, then shine the moment you can.");
    sprintf(g->line[n++], "1. Short hop neutral air onto the shield.");
    sprintf(g->line[n++], "2. L-cancel: %d frames of landing, not %d.",
            m->land_l, m->land);
    sprintf(g->line[n++], "3. Down+B on the first frame after them.");
    sprintf(g->line[n++], "The verdict shows how many frames the opponent");
    sprintf(g->line[n++], "had between shieldstun and your shine. Attack");
    sprintf(g->line[n++], "later in the hop to make that smaller.");
    g->line_count = n;
    g->timeline_from = "frames around the landing (1 = you land)";
}

static void ns_Think(CourseCtx* c)
{
    int lenient = course_Leniency(NS_OPT_LENIENCY);

    course_CpuShield(c);
    if (c->phase != NS_WAIT) {
        ns.frame++;
        if (c->state == FST_GROUND_START) {
            /* the shine's own hit on the shield is not the aerial's */
        } else if (c->cpu_state == ASID_GUARDSETOFF) {
            ns.on_shield = 1;
            ns.stun_end = 0;
        } else if (ns.on_shield && ns.stun_end == 0) {
            ns.stun_end = ns.frame;
        }
    }
    switch (c->phase) {
    case NS_WAIT:
        if (mv_IsAerial(c->state)) {
            course_Phase(c, NS_AIR);
            memset(&ns, 0, sizeof(ns));
            ns.frame = 1;
        } else if (c->state == ASID_LANDING) {
            course_Mark(c, NS_MARK_LAND);
        } else if (c->state == FST_GROUND_START && c->state_frames == 1 &&
                   c->prev_state != ns.land_state)
        {
            /* once per shine: without a reset this is seen every frame */
            course_Result(c, 0, "Shine without the aerial\njump in first",
                          0, 0);
        }
        break;

    case NS_AIR:
        if (mv_IsAerialLanding(c->state)) {
            course_Mark(c, NS_MARK_LAND);
            course_Phase(c, NS_LAND);
            ns.land_frame = ns.frame;
            ns.land_state = c->state;
            ns.lag = 1;
        } else if (!mv_IsAerial(c->state)) {
            course_Result(c, 0, "Landed after the attack\nattack later", 0,
                          0);
        } else if (ns.frame > MV_AIR_TIMEOUT) {
            course_Result(c, 0, "Did not land", 0, 0);
        }
        break;

    case NS_LAND:
        if (c->state == ns.land_state) {
            ns.lag++;
            break;
        }
        course_Phase(c, NS_AFTER);
        ns.wait = 0;
        /* fallthrough */
    case NS_AFTER:
        if (c->state == FST_GROUND_START) {
            /* frames the CPU was out of shieldstun before the shine;
             * 0 or less: none */
            int open = ns.stun_end > 0 ? ns.frame - ns.stun_end : 0;
            int lcancel = mv_WasLCancelled(c, ns.land_state, ns.lag);
            course_Measure(ns.wait, 0);
            course_Report("on_shield", ns.on_shield);
            course_Report("l_cancel", lcancel);
            course_Report("lag", ns.lag);
            course_Report("open", open);
            if (!ns.on_shield) {
                course_Result(c, 0, "The aerial missed the shield", 0, 0);
            } else if (!lcancel) {
                course_Result(c, 0, "No L-cancel: %d frames lag\n"
                                    "L, R or Z as you land",
                              ns.lag, 0);
            } else if (ns.wait > lenient) {
                course_Result(c, 0, "Shine %d frames late\n"
                                    "opponent had %d frames",
                              ns.wait, open);
            } else if (ns.wait == 0) {
                course_Result(c, 1, "Perfect: shine at once\n"
                                    "opponent had %d frames",
                              open, 0);
            } else {
                course_Result(c, 1, "Shine %d late\nopponent had %d frames",
                              ns.wait, open);
            }
        } else if (++ns.wait > 20) {
            if (!mv_WasLCancelled(c, ns.land_state, ns.lag)) {
                course_Result(c, 0, "No L-cancel: %d frames lag
"
                                    "L, R or Z as you land",
                              ns.lag, 0);
            } else {
                course_Result(c, 0, "No shine after landing", 0, 0);
            }
        }
        break;
    }
}

static const CourseDrill Drill_FoxNairShine = {
    .flow = 1,
    .Setup = ns_Setup,
    .Think = ns_Think,
    .options = ns_options,
    .option_count = countof(ns_options),
    .help = { "Aerial into shine: short hop neutral air on the",
              "shield, L-cancel, shine as you land.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = ns_reference,
    .Guide = ns_Guide,
};
