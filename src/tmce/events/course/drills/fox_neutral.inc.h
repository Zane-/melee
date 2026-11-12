/*
 * Fox's Neutral drills. Specs: data/courses/fox.md (Neutral). Included by
 * ../event.c.
 *
 * fox-whiff-punish: the CPU stands at the edge of an attack's reach and
 * throws it once the player has been inside that reach for its reaction
 * time. The player steps in, steps out so the attack misses, and hits or
 * grabs the CPU before it can act again. The reaction time is the
 * difficulty. Scenarios: WhiffPunish_Deck (../desc.c).
 */

enum { WP_MARK_TRIGGER = 1, WP_MARK_ATTACK, WP_MARK_CLOSE };
enum { WP_OPT_REACTION, WP_OPT_PERCENT };
enum { WP_BAIT, WP_REACT, WP_ATTACK };

/* The player starts this far outside the attack's reach. */
#define WP_START_GAP 14.0F
/* Where the demonstration starts its jump-cancelled up smash: Fox is
 * running and slides in while it comes out. */
#define WP_CLOSE 16.0F

static const char* wp_opt_reaction[] = { "Slow (20)", "Normal (14)",
                                         "Fast (9)" };
static const int wp_reactions[] = { 20, 14, 9 };

static EventOption wp_options[] = {
    [WP_OPT_REACTION] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(wp_opt_reaction),
        .val = 1,
        .name = "CPU Reaction",
        .desc = { "Frames the CPU takes to attack once you are",
                  "inside its range. Faster is harder to bait." },
        .values = wp_opt_reaction,
    },
    [WP_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 151,
        .val = 20,
        .name = "CPU Percent",
        .desc = { "The CPU's damage at the start of each attempt." },
        .format = "%d%%",
    },
};

static struct {
    int attack_frame; /* script frame of the CPU's attack */
} wp;

static const WhiffScenario* wp_Scenario(CourseCtx* c)
{
    return c->entry->data;
}

/* The demonstration's timings are tuned for the Normal reaction, so it is
 * always shown at that. */
static int wp_Reaction(void)
{
    if (course_IsDemo()) {
        return wp_reactions[1];
    }
    return wp_reactions[Options_Main[OPT_COMMON_COUNT + WP_OPT_REACTION].val];
}

/* The demonstration: dash in; once the CPU has noticed, dash back out
 * (ten frames of stick: the dash itself carries Fox about 40 units), let
 * go until the scenario's `demo_back`, dash in again and up smash when
 * close. All timed against marks of the same attempt. */
static CourseRefInput wp_ref[8];

static const CourseRefInput* wp_BuildReference(CourseCtx* c)
{
    static const CourseRefInput end = { COURSE_REF_END };
    const WhiffScenario* sc = wp_Scenario(c);
    int out = 10;
    int wait = wp_Reaction() + sc->demo_back - out;
    int n = 0;

    memset(wp_ref, 0, sizeof(wp_ref));
    wp_ref[n].frame = 5; /* toward the CPU whenever nothing else says */
    wp_ref[n].hold = 400;
    wp_ref[n++].lx = 127;
    wp_ref[n].mark = WP_MARK_TRIGGER;
    wp_ref[n].frame = 1;
    wp_ref[n].hold = out;
    wp_ref[n++].lx = -127;
    if (wait > 0) {
        wp_ref[n].mark = WP_MARK_TRIGGER;
        wp_ref[n].frame = 1 + out;
        wp_ref[n].hold = wait;
        wp_ref[n++].lx = 1; /* inside the dead zone: stand still */
    }
    /* Up smash out of a run has to be jump-cancelled. */
    wp_ref[n].mark = WP_MARK_CLOSE;
    wp_ref[n].frame = 1;
    wp_ref[n].hold = 1;
    wp_ref[n++].buttons = PAD_BUTTON_X;
    wp_ref[n].mark = WP_MARK_CLOSE;
    wp_ref[n].frame = 2;
    wp_ref[n].hold = 1;
    wp_ref[n++].cy = 127;
    wp_ref[n] = end;
    return wp_ref;
}

static void wp_Setup(CourseCtx* c)
{
    float gap = wp_Scenario(c)->reach + WP_START_GAP;
    float hmn_x = -c->side * gap / 2;
    course_Place(c, hmn_x, hmn_x + c->side * gap, 0,
                 (float) Options_Main[OPT_COMMON_COUNT + WP_OPT_PERCENT].val);
    wp.attack_frame = 0;
}

static void wp_Guide(CourseCtx* c, CourseGuide* g)
{
    const WhiffScenario* sc = c->entry != NULL ? wp_Scenario(c) : NULL;
    int n = 0;
    sprintf(g->line[n++], "An attack that misses leaves its user stuck.");
    sprintf(g->line[n++], "Make the opponent swing at nothing:");
    sprintf(g->line[n++], "1. Dash into their range. They react in %d",
            wp_Reaction());
    sprintf(g->line[n++], "   frames and attack.");
    sprintf(g->line[n++], "2. Dash back out before the attack reaches.");
    sprintf(g->line[n++], "3. Dash in and grab or hit before they recover.");
    if (sc != NULL) {
        sprintf(g->line[n++], "%s: hitbox gone after frame", c->entry->name);
        sprintf(g->line[n++], "%d, acts again on frame %d.", sc->hit_end,
                sc->faf);
    }
    g->line_count = n;
    g->hide_timeline = 1;
}

static void wp_Think(CourseCtx* c)
{
    const WhiffScenario* sc = wp_Scenario(c);
    float dist = fabs(c->cd->phys.pos.X - c->hd->phys.pos.X);
    int hit_cpu = c->cpu_hit || fpr_CpuGrabbed(c);

    switch (c->phase) {
    case WP_BAIT:
    case WP_REACT:
        if (hit_cpu) {
            course_Result(c, 0, "Hit before it swung\nbait the attack first",
                          0, 0);
        } else if (c->phase == WP_BAIT) {
            if (dist < sc->reach) {
                course_Mark(c, WP_MARK_TRIGGER);
                course_Phase(c, WP_REACT);
            }
        } else if (c->timer >= wp_Reaction()) {
            course_Mark(c, WP_MARK_ATTACK);
            course_Phase(c, WP_ATTACK);
            wp.attack_frame = 0;
        }
        break;

    case WP_ATTACK:
        course_Script(c, sc->inputs, wp.attack_frame);
        wp.attack_frame++;
        if (wp.attack_frame > sc->hit_end && dist < WP_CLOSE) {
            course_Mark(c, WP_MARK_CLOSE);
        }
        if (c->hmn_hit) {
            course_Report("frame", wp.attack_frame);
            course_Result(c, 0, "Got hit: still in range\nleave sooner", 0,
                          0);
        } else if (c->hd->state_id == ASID_GUARDSETOFF) {
            course_Result(c, 0, "Shielded it\nmake it miss instead", 0, 0);
        } else if (hit_cpu) {
            int spare = sc->faf - wp.attack_frame;
            course_Measure(wp.attack_frame, sc->hit_end + 1);
            course_Report("frame", wp.attack_frame);
            course_Report("spare", spare);
            course_Result(c, 1, "Whiff punish!\n%d frames to spare", spare,
                          0);
        } else if (wp.attack_frame >= sc->faf) {
            course_Result(c, 0, "Too slow\nit recovered on frame %d",
                          sc->faf, 0);
        }
        break;
    }
}

static const CourseDrill Drill_FoxWhiffPunish = {
    .Setup = wp_Setup,
    .Think = wp_Think,
    .options = wp_options,
    .option_count = countof(wp_options),
    .help = { "Whiff punish: dash into range, dash out so the",
              "attack misses, then punish before they recover.",
              "D-Pad up: guide. D-Pad down: reset." },
    .BuildReference = wp_BuildReference,
    .live_marks = 1,
    .Guide = wp_Guide,
};

/* ---- jump-in approaches: shared -------------------------------------------
 *
 * fox-wavedash-back-punish and fox-anti-air: the CPU stands at a scenario's
 * start distance and, after a wait the player cannot predict, jumps in
 * with an aerial. Scenarios are WhiffScenario too (../desc.c).
 */

enum { AP_MARK_ATTACK = 1, AP_MARK_CLOSE };
enum { AP_WAIT, AP_ATTACK };
enum { AP_OPT_PERCENT };

#define AP_WAIT_MIN 40
#define AP_WAIT_SPAN 60

static EventOption ap_options[] = {
    [AP_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 151,
        .val = 20,
        .name = "CPU Percent",
        .desc = { "The CPU's damage at the start of each attempt." },
        .format = "%d%%",
    },
};

static struct {
    int wait;         /* frames before the CPU jumps */
    int attack_frame; /* script frame of the approach */
    int wavedash;     /* the player has wavedashed since it began */
} ap;

static void ap_Setup(CourseCtx* c)
{
    float gap = wp_Scenario(c)->reach;
    float hmn_x = -c->side * gap / 2;
    course_Place(c, hmn_x, hmn_x + c->side * gap, 0,
                 (float) Options_Main[OPT_COMMON_COUNT + AP_OPT_PERCENT].val);
    /* a demonstration does not keep its viewer waiting */
    ap.wait = course_IsDemo() ? AP_WAIT_MIN
                              : AP_WAIT_MIN + HSD_Randi(AP_WAIT_SPAN);
    ap.attack_frame = 0;
    ap.wavedash = 0;
}

/* Runs the wait and the CPU's script. Returns 1 while the approach is on. */
static int ap_Advance(CourseCtx* c)
{
    if (c->phase == AP_WAIT) {
        if (c->timer < ap.wait) {
            return 0;
        }
        course_Mark(c, AP_MARK_ATTACK);
        course_Phase(c, AP_ATTACK);
        ap.attack_frame = 0;
    }
    course_Script(c, wp_Scenario(c)->inputs, ap.attack_frame);
    ap.attack_frame++;
    return 1;
}

/* ---- fox-wavedash-back-punish -------------------------------------------- */

static CourseRefInput wb_ref[8];

/* The demonstration: wavedash back as the CPU jumps, dash in at the
 * scenario's `demo_back` and jump-cancel an up smash when close. Against
 * Marth it connects on the last frame that counts (he slides behind Fox
 * as he lands); a jump-cancelled grab was tried and is out of range in
 * all three. */
static const CourseRefInput* wb_BuildReference(CourseCtx* c)
{
    static const CourseRefInput end = { COURSE_REF_END };
    const WhiffScenario* sc = wp_Scenario(c);
    int js = course_Fighter(c->hd)->jump_squat;
    int n = 0;

    memset(wb_ref, 0, sizeof(wb_ref));
    wb_ref[n].mark = AP_MARK_ATTACK;
    wb_ref[n].frame = sc->demo_out;
    wb_ref[n].hold = 1;
    wb_ref[n++].buttons = PAD_BUTTON_X;
    wb_ref[n].mark = AP_MARK_ATTACK;
    wb_ref[n].frame = sc->demo_out + js;
    wb_ref[n].hold = 2;
    wb_ref[n].lx = -100;
    wb_ref[n].ly = -75;
    wb_ref[n].buttons = PAD_TRIGGER_R;
    wb_ref[n++].trigger = 140;
    wb_ref[n].mark = AP_MARK_ATTACK;
    wb_ref[n].frame = sc->demo_back;
    wb_ref[n].hold = 200;
    wb_ref[n++].lx = 127;
    wb_ref[n].mark = AP_MARK_CLOSE;
    wb_ref[n].frame = 1;
    wb_ref[n].hold = 1;
    wb_ref[n++].buttons = PAD_BUTTON_X;
    wb_ref[n].mark = AP_MARK_CLOSE;
    wb_ref[n].frame = 2;
    wb_ref[n].hold = 1;
    wb_ref[n++].cy = 127;
    wb_ref[n] = end;
    return wb_ref;
}

static void wb_Guide(CourseCtx* c, CourseGuide* g)
{
    const WhiffScenario* sc = c->entry != NULL ? wp_Scenario(c) : NULL;
    int n = 0;
    sprintf(g->line[n++], "An opponent who jumps at you has chosen where");
    sprintf(g->line[n++], "they land. Do not be there.");
    sprintf(g->line[n++], "1. When they jump, wavedash back: jump, then");
    sprintf(g->line[n++], "   air dodge down and away at once.");
    sprintf(g->line[n++], "2. Their attack lands in front of you.");
    sprintf(g->line[n++], "3. Dash in and punish the landing lag.");
    if (sc != NULL) {
        sprintf(g->line[n++], "%s: lands on frame %d,", c->entry->name,
                sc->hit_end);
        sprintf(g->line[n++], "acts again on frame %d.", sc->faf);
    }
    g->line_count = n;
    g->hide_timeline = 1;
}

static void wb_Think(CourseCtx* c)
{
    const WhiffScenario* sc = wp_Scenario(c);
    float dist = fabs(c->cd->phys.pos.X - c->hd->phys.pos.X);
    int hit_cpu = c->cpu_hit || fpr_CpuGrabbed(c);

    if (!ap_Advance(c)) {
        if (hit_cpu) {
            course_Result(c, 0, "Hit before it jumped\nwait for the approach",
                          0, 0);
        }
        return;
    }
    if (c->state == ASID_LANDINGFALLSPECIAL) {
        ap.wavedash = 1;
    }
    /* For the demonstration: its up smash takes a few frames, so it starts
     * a little before the landing. */
    if (ap.attack_frame > sc->hit_end - 4 && dist < WP_CLOSE) {
        course_Mark(c, AP_MARK_CLOSE);
    }
    if (c->hmn_hit) {
        course_Report("frame", ap.attack_frame);
        course_Result(c, 0, "Got hit\nwavedash back sooner", 0, 0);
    } else if (c->hd->state_id == ASID_GUARDSETOFF) {
        course_Result(c, 0, "Shielded it\nmove out of the way instead", 0, 0);
    } else if (hit_cpu) {
        int spare = sc->faf - ap.attack_frame;
        course_Report("frame", ap.attack_frame);
        course_Report("spare", spare);
        course_Report("wavedash", ap.wavedash);
        if (!ap.wavedash) {
            course_Result(c, 0, "Hit, but no wavedash back\n"
                                "that is the Anti-Air drill",
                          0, 0);
        } else {
            course_Measure(ap.attack_frame, sc->hit_end + 1);
            course_Result(c, 1, "Wavedash back punish!\n%d frames to spare",
                          spare, 0);
        }
    } else if (ap.attack_frame >= sc->faf) {
        course_Result(c, 0, "Too slow\nit recovered on frame %d", sc->faf, 0);
    }
}

static const CourseDrill Drill_FoxWavedashBack = {
    .Setup = ap_Setup,
    .Think = wb_Think,
    .options = ap_options,
    .option_count = countof(ap_options),
    .help = { "Wavedash back out of the jump-in, then dash in and",
              "punish the landing.",
              "D-Pad up: guide. D-Pad down: reset." },
    .BuildReference = wb_BuildReference,
    .live_marks = 1,
    .Guide = wb_Guide,
};

/* ---- fox-anti-air --------------------------------------------------------- */

static CourseRefInput aa_ref[3];

/* The demonstration: an up smash timed to meet the jump-in. */
static const CourseRefInput* aa_BuildReference(CourseCtx* c)
{
    static const CourseRefInput end = { COURSE_REF_END };
    memset(aa_ref, 0, sizeof(aa_ref));
    aa_ref[0].mark = AP_MARK_ATTACK;
    aa_ref[0].frame = wp_Scenario(c)->demo_out;
    aa_ref[0].hold = 1;
    aa_ref[0].cy = 127;
    aa_ref[1] = end;
    return aa_ref;
}

static void aa_Guide(CourseCtx* c, CourseGuide* g)
{
    const CourseFighterData* me = course_Fighter(c->hd);
    int n = 0;
    sprintf(g->line[n++], "A jump commits the opponent to an arc. Meet");
    sprintf(g->line[n++], "them at the end of it with a move that hits");
    sprintf(g->line[n++], "upward before their attack reaches you.");
    sprintf(g->line[n++], "Up tilt: hits on frame %d.",
            me->move[CMOVE_UTILT].hit);
    sprintf(g->line[n++], "Up smash: frame %d.   Back air: frame %d.",
            me->move[CMOVE_USMASH].hit, me->move[CMOVE_BAIR].hit);
    sprintf(g->line[n++], "Swing as they come down, not as they jump.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void aa_Think(CourseCtx* c)
{
    const WhiffScenario* sc = wp_Scenario(c);
    FighterData* hd = c->hd;

    if (!ap_Advance(c)) {
        if (c->cpu_hit || fpr_CpuGrabbed(c)) {
            course_Result(c, 0, "Hit before it jumped\nwait for the approach",
                          0, 0);
        }
        return;
    }
    if (c->hmn_hit) {
        course_Report("frame", ap.attack_frame);
        course_Result(c, 0, "Got hit\nswing earlier", 0, 0);
    } else if (hd->state_id == ASID_GUARDSETOFF) {
        course_Result(c, 0, "Shielded it\nbeat it instead", 0, 0);
    } else if (c->cpu_hit) {
        int anti = hd->state_id == ASID_ATTACKHI3 ||
                   hd->state_id == ASID_ATTACKHI4 ||
                   hd->state_id == ASID_ATTACKAIRB;
        course_Report("frame", ap.attack_frame);
        if (ap.attack_frame > sc->hit_end) {
            course_Result(c, 0, "Hit after they landed\nmeet them in the air",
                          0, 0);
        } else if (!anti) {
            course_Result(c, 0, "Hit, but not an anti-air\n"
                                "up tilt, up smash or back air",
                          0, 0);
        } else {
            course_Measure(ap.attack_frame, ap.attack_frame);
            course_Result(c, 1, "Anti-air!\non frame %d of the jump",
                          ap.attack_frame, 0);
        }
    } else if (ap.attack_frame >= sc->faf) {
        course_Result(c, 0, "No anti-air\nthey landed and recovered", 0, 0);
    }
}

static const CourseDrill Drill_FoxAntiAir = {
    .Setup = ap_Setup,
    .Think = aa_Think,
    .options = ap_options,
    .option_count = countof(ap_options),
    .help = { "Anti-air: beat the jump-in with up tilt, up smash",
              "or back air before it reaches you.",
              "D-Pad up: guide. D-Pad down: reset." },
    .BuildReference = aa_BuildReference,
    .live_marks = 1,
    .Guide = aa_Guide,
};
