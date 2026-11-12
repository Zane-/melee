/*
 * Fox's Punish drills (after fox-shine-oos). Specs: data/courses/fox.md
 * (Punish). Included by ../event.c after the Tech and Neutral files.
 */

/* ---- fox-waveshine-usmash -------------------------------------------------
 *
 * Marth stands next to Fox. Shine him (at low percent he slides away on
 * his feet), jump out of the shine, wavedash after him and up smash.
 * From the moment the shine hits, the CPU holds shield: if the up smash is
 * a true follow-up it lands, if not it is blocked.
 */

enum { WU_OPT_PERCENT };
enum { WU_MARK_HIT = 1 };
enum { WU_WAIT, WU_COMBO };

#define WU_TIMEOUT 70

static EventOption wu_options[] = {
    [WU_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 151,
        .val = 30,
        .name = "CPU Percent",
        .desc = { "The CPU's damage at the start of each attempt." },
        .format = "%d%%",
    },
};

static struct {
    int frame; /* frames since the shine hit */
} wu;

/* Found with a sweep in the simulator (2026-11-12): jump 6 or 7 frames
 * after the down-B, air dodge 3 later at stick (127, -40) of 127, up smash
 * 10 to 12 after that. Marth slides 44 units from the shine, so only a
 * long wavedash catches him: angles of -30 and -50 both miss. */
#define WU_REF_JUMP 5 /* frames after the hit is seen */
static const CourseRefInput wu_reference[] = {
    { 0, 10, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { WU_MARK_HIT, WU_REF_JUMP, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { WU_MARK_HIT, WU_REF_JUMP + 3, 2, 127, -40, 0, 0, PAD_TRIGGER_R, 140,
      0 },
    { WU_MARK_HIT, WU_REF_JUMP + 14, 1, 0, 0, 0, 127, 0, 0, 0 },
    { COURSE_REF_END },
};

static void wu_Setup(CourseCtx* c)
{
    float hmn_x = -c->side * (FPR_DISTANCE / 2);
    course_Place(c, hmn_x, hmn_x + c->side * FPR_DISTANCE, 0,
                 (float) Options_Main[OPT_COMMON_COUNT + WU_OPT_PERCENT].val);
    wu.frame = 0;
}

static void wu_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Shine pushes a standing opponent away with");
    sprintf(g->line[n++], "enough stun for Fox to catch up and up smash:");
    sprintf(g->line[n++], "his most reliable way to a kill move.");
    sprintf(g->line[n++], "1. Shine.");
    sprintf(g->line[n++], "2. Jump out of it and wavedash toward them,");
    sprintf(g->line[n++], "   nearly flat: they slide a long way.");
    sprintf(g->line[n++], "3. Up smash as the wavedash ends.");
    sprintf(g->line[n++], "They shield as soon as they can: blocked");
    sprintf(g->line[n++], "means the waveshine was too slow.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void wu_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;

    switch (c->phase) {
    case WU_WAIT:
        if (c->cpu_hit && fst_IsShine(hd->state_id)) {
            course_Mark(c, WU_MARK_HIT);
            course_Phase(c, WU_COMBO);
            wu.frame = 0;
        } else if (c->cpu_hit || fpr_CpuGrabbed(c)) {
            course_Result(c, 0, "Start with the shine", 0, 0);
        }
        break;

    case WU_COMBO:
        wu.frame++;
        course_CpuShield(c);
        if (c->cpu_hit && hd->state_id == ASID_ATTACKHI4) {
            course_Measure(wu.frame, wu.frame);
            course_Report("frame", wu.frame);
            course_Result(c, 1, "Waveshine up smash!\n"
                                "%d frames after the shine",
                          wu.frame, 0);
        } else if (c->cpu_state == ASID_GUARDSETOFF) {
            course_Report("frame", wu.frame);
            course_Result(c, 0, "Blocked: %d frames after\n"
                                "the shine is too slow",
                          wu.frame, 0);
        } else if (c->cpu_hit || fpr_CpuGrabbed(c)) {
            course_Result(c, 0, "Not the up smash", 0, 0);
        } else if (wu.frame > WU_TIMEOUT) {
            course_Result(c, 0, "No up smash", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_FoxWaveshineUsmash = {
    .Setup = wu_Setup,
    .Think = wu_Think,
    .options = wu_options,
    .option_count = countof(wu_options),
    .help = { "Shine, wavedash after them, up smash before they",
              "can shield.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = wu_reference,
    .live_marks = 1,
    .Guide = wu_Guide,
};

/* ---- fox-shield-pressure --------------------------------------------------
 *
 * Marth shields, and from the first hit on tries to grab out of shield on
 * every frame he is free. Each hit on the shield counts; a gap long enough
 * for the grab ends the attempt. Hitting him out of the grab's startup is
 * the pressure working.
 */

enum { PR_OPT_HITS };
enum { PR_MARK_LAND = 1 };

#define PR_IDLE 90 /* frames without a hit before the pressure has stopped */

static const char* pr_opt_hits[] = { "3", "5", "8" };
static const int pr_hits[] = { 3, 5, 8 };

static EventOption pr_options[] = {
    [PR_OPT_HITS] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(pr_opt_hits),
        .name = "Hits",
        .desc = { "How many hits on the shield in a row count",
                  "as a success." },
        .values = pr_opt_hits,
    },
};

static struct {
    int hits;
    int idle;      /* frames since the last hit */
    int in_hitlag; /* the CPU was in shield hitlag last frame */
    int frame;
} pr;

/* The demonstration: short hop neutral air (L-cancelled: two presses, as
 * the landing moves with the shield's hitlag), shine as the landing lag
 * ends, jump out of the shine and shine again on the first airborne
 * frame. */
static const CourseRefInput pr_reference[] = {
    { 0, 10, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 25, 1, 0, 0, 0, 0, PAD_BUTTON_A, 0, 0 }, /* late: hits low */
    { 0, 30, 1, 0, 0, 0, 0, PAD_TRIGGER_Z, 0, 0 },
    { 0, 35, 1, 0, 0, 0, 0, PAD_TRIGGER_Z, 0, 0 },
    { PR_MARK_LAND, 6, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { PR_MARK_LAND, 12, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { PR_MARK_LAND, 15, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { COURSE_REF_END },
};

static void pr_Setup(CourseCtx* c)
{
    fpr_Place(c);
    memset(&pr, 0, sizeof(pr));
}

static void pr_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "A shielding opponent wants one thing: a gap");
    sprintf(g->line[n++], "long enough to grab you (7 frames). Do not");
    sprintf(g->line[n++], "give it.");
    sprintf(g->line[n++], "Aerial low on the shield, L-cancel, shine at");
    sprintf(g->line[n++], "once, jump out of the shine, and again.");
    sprintf(g->line[n++], "If they try to grab and your next hit beats it,");
    sprintf(g->line[n++], "the pressure has done its job.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void pr_Think(CourseCtx* c)
{
    FighterData* cd = c->cd;
    int want = pr_hits[Options_Main[OPT_COMMON_COUNT + PR_OPT_HITS].val];
    int hitlag = cd->flags.hitlag && cd->state_id == ASID_GUARDSETOFF;

    pr.frame++;
    course_CpuShield(c);
    if (pr.hits > 0 && (pr.frame & 1)) {
        cd->cpu.held |= PAD_BUTTON_A; /* A in shield: grab */
    }
    if (mv_IsAerialLanding(c->state)) {
        course_Mark(c, PR_MARK_LAND);
    }

    if (hitlag && !pr.in_hitlag) {
        pr.hits++;
        pr.idle = 0;
    }
    pr.in_hitlag = hitlag;
    if (pr.hits > 0) {
        pr.idle++;
    }

    if (nr_PlayerGrabbed(c)) {
        course_Measure(pr.hits, want);
        course_Report("hits", pr.hits);
        course_Result(c, 0, "Shield grabbed after %d hits\n"
                            "the gap was too long",
                      pr.hits, 0);
    } else if (c->hmn_hit) {
        course_Result(c, 0, "Got hit", 0, 0);
    } else if (c->cpu_hit) {
        course_Measure(pr.hits, want);
        course_Report("hits", pr.hits);
        course_Result(c, 1, "They went for the grab\n"
                            "and you hit them first",
                      0, 0);
    } else if (pr.hits >= want) {
        course_Measure(pr.hits, want);
        course_Report("hits", pr.hits);
        course_Result(c, 1, "%d hits, no gap", pr.hits, 0);
    } else if (pr.idle > PR_IDLE) {
        course_Measure(pr.hits, want);
        course_Report("hits", pr.hits);
        course_Result(c, 0, "Pressure stopped after %d hits", pr.hits, 0);
    }
}

static const CourseDrill Drill_FoxShieldPressure = {
    .Setup = pr_Setup,
    .Think = pr_Think,
    .options = pr_options,
    .option_count = countof(pr_options),
    .help = { "Hit the shield again and again without leaving a",
              "gap they can grab you in.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = pr_reference,
    .live_marks = 1,
    .Guide = pr_Guide,
};

/* ---- fox-oos-choice -------------------------------------------------------
 *
 * The Shine OoS scenarios (ShineOos_Deck), but from farther away some of
 * the time, so that the shine does not always reach. Any hit or grab
 * before the CPU has recovered counts, and the verdict names the option
 * and how early it was. Once it has recovered the CPU shields.
 */

enum { OC_MARK_STUN_END = 1 };
enum { OC_WAIT_SHIELD, OC_ATTACK, OC_PUNISH };

#define OC_BUSY_MIN 20
#define OC_TIMEOUT 120
#define OC_CPU_REACT 4 /* frames the CPU takes to shield once it can */

static struct {
    int attack_frame;
    int delay;
    int stun_end; /* attack_frame when shieldstun ended, -1 = not yet */
    int cpu_free; /* the CPU has recovered */
    int free_frames;
    float extra;
} oc;

/* Hold shield; jump the frame after shieldstun is seen to end and shine
 * as Fox leaves the ground: a frame later than perfect, which the CPU's
 * reaction time allows. (Placing the jump on the exact frame needs the
 * observing pass of fox-shine-oos; tried here, it went wrong against the
 * multi-hit aerials.) */
static const CourseRefInput oc_reference[] = {
    { 0, 0, 600, 0, 0, 0, 0, PAD_TRIGGER_R, 140, 0 },
    { OC_MARK_STUN_END, 1, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { OC_MARK_STUN_END, 4, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { COURSE_REF_END },
};

static void oc_Setup(CourseCtx* c)
{
    const OosScenario* sc = c->entry->data;
    float hmn_x = -c->side * 10.0F;
    /* the demonstration shines, so it gets the shine's spacing */
    oc.extra = course_IsDemo() ? 0 : 4.0F * HSD_Randi(3);
    course_Place(c, hmn_x, hmn_x + c->side * (sc->distance + oc.extra),
                 sc->face_away, 20.0F);
    oc.delay = 10 + HSD_Randi(30);
    oc.attack_frame = 0;
    oc.stun_end = -1;
    oc.cpu_free = 0;
    oc.free_frames = 0;
}

static void oc_Guide(CourseCtx* c, CourseGuide* g)
{
    const CourseFighterData* me = course_Fighter(c->hd);
    int n = 0;
    sprintf(g->line[n++], "Out of shield, the right answer depends on how");
    sprintf(g->line[n++], "far away they end up and how long they are stuck.");
    sprintf(g->line[n++], "Shine: frame %d, but only when they are touching.",
            me->jump_squat + 1);
    sprintf(g->line[n++], "Up smash: frame %d, reaches further.",
            me->jump_squat + me->move[CMOVE_USMASH].hit);
    sprintf(g->line[n++], "Neutral air: frame %d, reaches in front.",
            me->jump_squat + me->move[CMOVE_NAIR].hit);
    sprintf(g->line[n++], "Grab: frame %d, only close and in front.",
            me->move[CMOVE_GRAB].hit);
    sprintf(g->line[n++], "Wavedash out when nothing reaches in time.");
    g->line_count = n;
    g->hide_timeline = 1;
}

/* The verdict for the option that connected. */
static char* oc_Option(FighterData* hd)
{
    if (fst_IsShine(hd->state_id)) {
        return "Shine out of shield\nframe %d";
    }
    switch (hd->state_id) {
    case ASID_ATTACKHI4:
        return "Up smash out of shield\nframe %d";
    case ASID_ATTACKAIRN:
        return "Neutral air out of shield\nframe %d";
    case ASID_CATCH:
    case ASID_CATCHPULL:
    case ASID_CATCHWAIT:
        return "Grab out of shield\nframe %d";
    default:
        return "Punished out of shield\nframe %d";
    }
}

static void oc_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    const OosScenario* sc = c->entry->data;

    hd->shield.health = 60; /* the player's shield does not shrink */
    if (c->phase >= OC_ATTACK) {
        if (!oc.cpu_free) {
            course_Script(c, (const CourseInput*) sc->inputs,
                          oc.attack_frame);
        } else {
            course_CpuShield(c);
        }
        oc.attack_frame++;
        /* it shields a few frames after it can: nobody is frame perfect */
        if (oc.attack_frame > OC_BUSY_MIN && c->cpu_state == ASID_WAIT &&
            ++oc.free_frames > OC_CPU_REACT)
        {
            oc.cpu_free = 1;
        }
    }

    switch (c->phase) {
    case OC_WAIT_SHIELD:
        if (hd->state_id == ASID_GUARD || hd->state_id == ASID_GUARDON) {
            if (c->timer >= oc.delay) {
                course_Phase(c, OC_ATTACK);
                oc.attack_frame = 0;
            }
        } else {
            c->timer = 0;
        }
        break;

    case OC_ATTACK:
        if (hd->state_id == ASID_GUARDSETOFF) {
            course_Phase(c, OC_PUNISH);
        } else if (c->hmn_hit) {
            course_Result(c, 0, "Hit through your shield", 0, 0);
        } else if (c->timer > sc->attack_timeout + 30) {
            course_Retry(c, "Attack missed\nresetting");
        }
        break;

    case OC_PUNISH:
        if (oc.stun_end < 0 && hd->state_id != ASID_GUARDSETOFF) {
            oc.stun_end = oc.attack_frame;
            course_Mark(c, OC_MARK_STUN_END);
        }
        if (c->hmn_hit || nr_PlayerGrabbed(c)) {
            course_Result(c, 0, "Got hit", 0, 0);
        } else if (c->cpu_hit || fpr_CpuGrabbed(c)) {
            int frame = oc.stun_end >= 0 ? oc.attack_frame - oc.stun_end : 0;
            course_Measure(frame, frame);
            course_Report("frame", frame);
            course_ReportF("extra", oc.extra);
            course_Result(c, 1, oc_Option(hd), frame, 0);
        } else if (c->cpu_state == ASID_GUARDSETOFF) {
            course_Result(c, 0, "Too slow: blocked\npick a faster option", 0,
                          0);
        } else if (c->timer > OC_TIMEOUT) {
            course_Result(c, 0, "No punish", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_FoxOosChoice = {
    .Setup = oc_Setup,
    .Think = oc_Think,
    .help = { "Shield the attack, then punish with whatever",
              "reaches in time: shine, up smash, nair or grab.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = oc_reference,
    .live_marks = 1,
    .Guide = oc_Guide,
};
