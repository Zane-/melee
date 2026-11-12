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
