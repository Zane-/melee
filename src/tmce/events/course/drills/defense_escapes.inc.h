/*
 * Defense drills, second file: fox-ledgedash-attack (getting off the
 * ledge). Spec: data/courses/fox.md (Defense 11). Included by ../event.c
 * after defense.inc.h.
 *
 * fox-escape-chaingrab was written here and removed (2026-11-12): a Marth
 * that grabs, up throws, stands under the falling player and grabs again
 * never lands the regrab, at any timing tried, because the player comes
 * down inside his grab's reach. He has to space himself, turn and pivot
 * for it, which is CPU logic that does not exist yet; without it the
 * escape was free.
 */

/* ---- fox-ledgedash-attack -------------------------------------------------
 *
 * The player hangs on the ledge; Marth waits just inside it, facing out.
 * When the player leaves the ledge, by any option, Marth waits his
 * reaction time and forward smashes at the ledge. Getting onto the stage
 * unhit, or hitting him, is the goal: a ledgedash is still intangible when
 * the smash arrives, a slow getup is not, a roll ends up behind him.
 */

enum { LA_OPT_REACTION };
enum { LA_MARK_FREE = 1 };
enum { LA_HANG, LA_REACT, LA_SMASH };

#define LA_CPU_FROM_LEDGE 22.0F
#define LA_SAFE 40 /* frames standing on the stage unhit */
#define LA_SMASH_LEAD 8 /* he starts this long before the player can be hit */

static const char* la_opt_reaction[] = { "Slow (20)", "Normal (14)",
                                         "Fast (9)" };
static const int la_reactions[] = { 20, 14, 9 };

static EventOption la_options[] = {
    [LA_OPT_REACTION] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(la_opt_reaction),
        .val = 1,
        .name = "CPU Reaction",
        .desc = { "Frames the CPU takes to swing once you leave",
                  "the ledge." },
        .values = la_opt_reaction,
    },
};

static struct {
    int frame;  /* frames since the player left the ledge */
    int safe;   /* frames standing on the stage */
    int smashed;
} la;

/* The demonstration: the ledgedash of universal-ledgedash, then shine as
 * the landing ends. */
static const CourseRefInput la_reference[] = {
    { 0, LD_REF_DROP, 1, -127, 0, 0, 0, 0, 0, 0 },
    { 0, LD_REF_DROP + LD_REF_JUMP, 1, 127, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, LD_REF_DROP + LD_REF_DODGE, 2, 110, -65, 0, 0, PAD_TRIGGER_R, 140,
      0 },
    { LA_MARK_FREE, 1, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { COURSE_REF_END },
};

static void la_Setup(CourseCtx* c)
{
    float ledge_x;
    course_PlaceOnLedge(c);
    ledge_x = c->hd->phys.pos.X;
    /* Marth inside the ledge, facing it */
    course_PlaceCpu(c, ledge_x + LA_CPU_FROM_LEDGE, -1.0F, 20.0F);
    memset(&la, 0, sizeof(la));
}

static void la_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "On the ledge with someone waiting, every way");
    sprintf(g->line[n++], "up has a moment they can hit.");
    sprintf(g->line[n++], "Getup, getup attack, roll, jump: slow, and");
    sprintf(g->line[n++], "they see it coming.");
    sprintf(g->line[n++], "Ledgedash: you are on the stage, still");
    sprintf(g->line[n++], "intangible, before they can react. Then act:");
    sprintf(g->line[n++], "shine or grab them.");
    sprintf(g->line[n++], "Marth swings as your intangibility runs out.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void la_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    FighterData* cd = c->cd;
    int react = course_IsDemo()
                    ? la_reactions[1]
                    : la_reactions[Options_Main[OPT_COMMON_COUNT +
                                                LA_OPT_REACTION]
                                       .val];

    switch (c->phase) {
    case LA_HANG:
        if (lg_OnLedge(c->state) || c->state < 0) {
            break;
        }
        course_Phase(c, LA_REACT);
        la.frame = 0;
        /* fallthrough */
    case LA_REACT:
    case LA_SMASH:
        la.frame++;
        if (c->phase == LA_REACT && la.frame >= react) {
            course_Phase(c, LA_SMASH);
        }
        if (c->phase == LA_SMASH && !la.smashed &&
            lg_Intangible(c) <= LA_SMASH_LEAD && hd->hurt.kind_game == 0)
        {
            /* toward wherever the player is now, timed for the end of the
             * ledge intangibility (swinging on reaction alone missed a
             * plain getup, which is intangible longer) */
            cd->cpu.cstickX = hd->phys.pos.X < cd->phys.pos.X ? -127 : 127;
            la.smashed = 1;
        }
        if (c->state == ASID_WAIT && hd->phys.air_state == 0) {
            course_Mark(c, LA_MARK_FREE);
            la.safe++;
        }
        if (c->hmn_hit || nr_PlayerGrabbed(c)) {
            course_Report("frame", la.frame);
            course_Result(c, 0, "Hit on the way up\n%d frames off the ledge",
                          la.frame, 0);
        } else if (c->cpu_hit || fpr_CpuGrabbed(c)) {
            course_Measure(la.frame, la.frame);
            course_Report("frame", la.frame);
            course_Report("galint", lg_Intangible(c));
            course_Result(c, 1, "Off the ledge and hit him\n"
                                "%d frames after letting go",
                          la.frame, 0);
        } else if (la.safe > LA_SAFE) {
            course_Result(c, 1, "On the stage, unhit", 0, 0);
        } else if (lg_OnLedge(c->state) && la.frame > 10) {
            course_Result(c, 0, "Back on the ledge", 0, 0);
        } else if (course_Fell(c) || la.frame > 400) {
            course_Result(c, 0, "Fell", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_DefLedgeAttack = {
    .Setup = la_Setup,
    .Think = la_Think,
    .options = la_options,
    .option_count = countof(la_options),
    .help = { "Get from the ledge onto the stage past Marth, who",
              "swings when he sees you move.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = la_reference,
    .live_marks = 1,
    .Guide = la_Guide,
};
