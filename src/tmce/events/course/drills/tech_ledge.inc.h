/*
 * universal-ledgedash, fox-ledge-stall (start on the ledge) and
 * universal-shield-drop (start on a platform). Specs: data/courses/fox.md
 * (Tech 7, 11, 15). Included by ../event.c.
 *
 * These reset after every verdict: the start position is the drill.
 */

static int lg_OnLedge(int state)
{
    return state == ASID_CLIFFCATCH || state == ASID_CLIFFWAIT;
}

/* Getting up, attacking, rolling or jumping from the ledge. */
static int lg_IsLedgeOption(int state)
{
    return state >= ASID_CLIFFCLIMBSLOW && state <= ASID_CLIFFJUMPQUICK2;
}

static int lg_Intangible(CourseCtx* c)
{
    return c->hd->hurt.intang_frames.ledge;
}

#define LG_TIMEOUT 200

/* ---- universal-ledgedash -------------------------------------------------- */

enum { LD_OPT_NEED };
enum { LD_HANG, LD_OFF, LD_LAND };

static const char* ld_opt_need[] = { "1", "5", "10", "15" };
static const int ld_needs[] = { 1, 5, 10, 15 };

static EventOption ld_options[] = {
    [LD_OPT_NEED] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(ld_opt_need),
        .name = "Intangible Frames",
        .desc = { "How many intangible frames you must still have",
                  "when you can act on the stage." },
        .values = ld_opt_need,
    },
};

static struct {
    int frame;  /* frames since letting go of the ledge */
    int jumped; /* used the double jump */
} ld;

/* Timings from a sweep in the simulator (2026-11-12): with Fox, jump 1 and
 * air dodge 4 frames after the drop land in 15 frames. */
#define LD_REF_DROP 4  /* script frame of the drop */
#define LD_REF_JUMP 1   /* jump this many frames after the drop */
#define LD_REF_DODGE 4  /* air dodge this many frames after the drop */

static const CourseRefInput ld_reference[] = {
    { 0, LD_REF_DROP, 1, -127, 0, 0, 0, 0, 0, 0 },
    { 0, LD_REF_DROP + LD_REF_JUMP, 1, 127, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, LD_REF_DROP + LD_REF_DODGE, 2, 110, -65, 0, 0, PAD_TRIGGER_R, 140,
      0 },
    { COURSE_REF_END },
};

static void ld_Setup(CourseCtx* c)
{
    course_PlaceOnLedge(c);
    ld.frame = 0;
    ld.jumped = 0;
}

static void ld_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Hanging on the ledge you cannot be hit for a");
    sprintf(g->line[n++], "moment. A ledgedash carries that onto the");
    sprintf(g->line[n++], "stage: you act while still intangible.");
    sprintf(g->line[n++], "1. Let go: stick down or away from the stage.");
    sprintf(g->line[n++], "2. Double jump at once, toward the stage.");
    sprintf(g->line[n++], "3. Air dodge down and forward onto the stage.");
    sprintf(g->line[n++], "The verdict shows the intangible frames you");
    sprintf(g->line[n++], "had left when you could act.");
    g->line_count = n;
}

static void ld_Think(CourseCtx* c)
{
    int need = ld_needs[Options_Main[OPT_COMMON_COUNT + LD_OPT_NEED].val];

    switch (c->phase) {
    case LD_HANG:
        if (lg_OnLedge(c->state) || c->state < 0) {
            break;
        }
        if (lg_IsLedgeOption(c->state)) {
            course_Result(c, 0, "A ledge option, not a dash\n"
                                "let go: stick down or away",
                          0, 0);
            break;
        }
        course_Phase(c, LD_OFF);
        ld.frame = 0;
        ld.jumped = 0;
        /* fallthrough */
    case LD_OFF:
        ld.frame++;
        if (fst_IsDoubleJump(c->state)) {
            ld.jumped = 1;
        }
        if (c->state == ASID_LANDINGFALLSPECIAL) {
            course_Phase(c, LD_LAND);
        } else if (lg_OnLedge(c->state)) {
            course_Result(c, 0, "Back on the ledge", 0, 0);
        } else if (c->state == ASID_LANDING || c->state == ASID_WAIT) {
            course_Report("galint", lg_Intangible(c));
            course_Result(c, 0, "Landed without the air dodge\n"
                                "%d intangible frames left",
                          lg_Intangible(c), 0);
        } else if (course_Fell(c) || ld.frame > LG_TIMEOUT) {
            course_Result(c, 0, ld.jumped ? "Fell: air dodge sooner"
                                          : "Fell: jump right after\n"
                                            "letting go",
                          0, 0);
        }
        break;

    case LD_LAND:
        ld.frame++;
        if (c->state == ASID_LANDINGFALLSPECIAL) {
            break;
        }
        {
            int left = lg_Intangible(c);
            course_Measure(left, need);
            course_Report("galint", left);
            course_Report("total", ld.frame);
            if (left >= need) {
                course_Result(c, 1, "Ledgedash! %d intangible\n"
                                    "frames left, %d in all",
                              left, ld.frame);
            } else if (left > 0) {
                course_Result(c, 0, "Only %d intangible frames\n"
                                    "left, need %d",
                              left, need);
            } else {
                course_Result(c, 0, "No intangibility left\n"
                                    "%d frames: be faster",
                              ld.frame, 0);
            }
        }
        break;
    }
}

static const CourseDrill Drill_TechLedgedash = {
    .Setup = ld_Setup,
    .Think = ld_Think,
    .options = ld_options,
    .option_count = countof(ld_options),
    .help = { "Ledgedash: let go of the ledge, double jump, and",
              "air dodge onto the stage.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = ld_reference,
    .Guide = ld_Guide,
};

/* ---- fox-ledge-stall ------------------------------------------------------ */

/* Fire Fox, ground and air, start to landing (ftFox/forward.h: between
 * the Illusion's states and the shine's). */
#define LS_FIREFOX_FIRST 0x161
#define LS_FIREFOX_LAST 0x167

enum { LS_OPT_COUNT };
enum { LS_HANG, LS_OFF };

static const char* ls_opt_count[] = { "1", "3", "5" };
static const int ls_counts[] = { 1, 3, 5 };

static EventOption ls_options[] = {
    [LS_OPT_COUNT] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(ls_opt_count),
        .name = "Stalls",
        .desc = { "How many stalls in a row count as a success." },
        .values = ls_opt_count,
    },
};

static struct {
    int stalls;
    int frame;      /* frames since letting go */
    int firefox;    /* Fire Fox was used since letting go */
    int vulnerable; /* frames without intangibility, over the whole chain */
    int hang;       /* frames on the ledge before this drop */
} ls;

/* Drop, up+B on the next frame; Fox is back on the ledge 30 frames after
 * the drop and can let go again 8 frames later. Five cycles, for the
 * largest "Stalls" setting (period found in the simulator, 2026-11-12). */
#define LS_REF_DROP 4
#define LS_REF_PERIOD 39
#define LS_CYCLE(n)                                                           \
    { 0, LS_REF_DROP + LS_REF_PERIOD * (n), 1, -127, 0, 0, 0, 0, 0, 0 },      \
    { 0, LS_REF_DROP + LS_REF_PERIOD * (n) + 1, 1, 0, 127, 0, 0,              \
      PAD_BUTTON_B, 0, 0 }

static const CourseRefInput ls_reference[] = {
    LS_CYCLE(0), LS_CYCLE(1), LS_CYCLE(2), LS_CYCLE(3), LS_CYCLE(4),
    { COURSE_REF_END },
};

static void ls_Setup(CourseCtx* c)
{
    course_PlaceOnLedge(c);
    memset(&ls, 0, sizeof(ls));
}

static void ls_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Every ledge grab makes you intangible again.");
    sprintf(g->line[n++], "Drop and Fire Fox straight back to the ledge");
    sprintf(g->line[n++], "to stay there safely while the opponent waits.");
    sprintf(g->line[n++], "1. Let go: stick down or away from the stage.");
    sprintf(g->line[n++], "2. Up+B at once. Fox rises back to the ledge.");
    sprintf(g->line[n++], "Drop as soon as the grab allows to keep the");
    sprintf(g->line[n++], "time you can be hit short: the verdict shows it.");
    g->line_count = n;
}

static void ls_End(CourseCtx* c, char* fmt)
{
    int want = ls_counts[Options_Main[OPT_COMMON_COUNT + LS_OPT_COUNT].val];
    course_Measure(ls.stalls, want);
    course_Report("stalls", ls.stalls);
    course_Report("vulnerable", ls.vulnerable);
    course_Result(c, 0, fmt, ls.stalls, want);
}

static void ls_Think(CourseCtx* c)
{
    int want = ls_counts[Options_Main[OPT_COMMON_COUNT + LS_OPT_COUNT].val];

    switch (c->phase) {
    case LS_HANG:
        if (lg_OnLedge(c->state) || c->state < 0) {
            ls.hang++;
            break;
        }
        if (lg_IsLedgeOption(c->state)) {
            ls_End(c, "A ledge option at %d of %d\n"
                      "let go: stick down or away");
            break;
        }
        course_Phase(c, LS_OFF);
        ls.frame = 0;
        ls.firefox = 0;
        /* fallthrough */
    case LS_OFF:
        ls.frame++;
        if (lg_Intangible(c) <= 0) {
            ls.vulnerable++;
        }
        if (c->state >= LS_FIREFOX_FIRST && c->state <= LS_FIREFOX_LAST) {
            ls.firefox = 1;
        }
        if (lg_OnLedge(c->state)) {
            if (!ls.firefox) {
                ls_End(c, "Regrab without Fire Fox\nat %d of %d");
                break;
            }
            ls.stalls++;
            if (ls.stalls >= want) {
                course_Measure(ls.stalls, want);
                course_Report("stalls", ls.stalls);
                course_Report("vulnerable", ls.vulnerable);
                course_Report("hang", ls.hang);
                course_Result(c, 1, "%d stalls\nhittable for %d frames",
                              ls.stalls, ls.vulnerable);
            } else {
                course_Phase(c, LS_HANG);
                ls.hang = 0;
            }
        } else if (course_Fell(c) || ls.frame > LG_TIMEOUT) {
            ls_End(c, ls.firefox ? "Missed the ledge at %d of %d"
                                 : "Fell at %d of %d\nup+B right after the drop");
        } else if (c->state == ASID_WAIT || c->state == ASID_LANDING ||
                   c->state == ASID_LANDINGFALLSPECIAL)
        {
            ls_End(c, "Landed on stage at %d of %d");
        }
        break;
    }
}

static const CourseDrill Drill_FoxLedgeStall = {
    .Setup = ls_Setup,
    .Think = ls_Think,
    .options = ls_options,
    .option_count = countof(ls_options),
    .help = { "Ledge stall: let go of the ledge and up+B at once",
              "to grab it again.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = ls_reference,
    .Guide = ls_Guide,
};

/* ---- universal-shield-drop ------------------------------------------------ */

/* Battlefield's left platform. */
#define SD_PLATFORM_X (-38.8F)
#define SD_PLATFORM_ABOVE 40.0F
/* Frames after the drop in which an aerial is credited to it. */
#define SD_AERIAL_WINDOW 20

enum { SD_WAIT, SD_SHIELD, SD_DROP };

static struct {
    int frame; /* frames since the drop */
} sd;

static int sd_IsShield(int state)
{
    return state >= ASID_GUARDON && state <= ASID_GUARDREFLECT &&
           state != ASID_GUARDOFF;
}

/* The Axe method: shield, ease the stick to full right (a fast push is a
 * roll), then down to the diagonal notch, then an aerial. Swept in the
 * simulator with the stick at X 90. With UCF (2026-11-13; always on, the
 * build's own or Slippi's, docs/ai/ucf.md): Y -80 to about -119 (of 127)
 * drops, and only a stick pushed past the -0.8 line (-127) is a spot
 * dodge. Without UCF (2026-11-12): -80 to -88 drops, -89 and beyond is a
 * spot dodge. */
static const CourseRefInput sd_reference[] = {
    { 0, 10, 600, 0, 0, 0, 0, PAD_TRIGGER_R, 140, 0 },
    { 0, 20, 10, 50, 0, 0, 0, 0, 0, 0 },
    { 0, 30, 10, 127, 0, 0, 0, 0, 0, 0 },
    { 0, 40, 6, 90, -86, 0, 0, 0, 0, 0 },
    { 0, 43, 1, 0, 0, 0, 0, PAD_BUTTON_A, 0, 0 },
    { COURSE_REF_END },
};

static void sd_Setup(CourseCtx* c)
{
    course_PlaceOnPlatform(c, SD_PLATFORM_X, SD_PLATFORM_ABOVE);
    sd.frame = 0;
}

static void sd_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Fall through a platform straight out of");
    sprintf(g->line[n++], "shield, and attack whoever is below.");
    sprintf(g->line[n++], "The Axe method:");
    sprintf(g->line[n++], "1. In shield, ease the stick fully left or");
    sprintf(g->line[n++], "   right. A fast push is a roll.");
    sprintf(g->line[n++], "2. Roll it down along the rim to the diagonal");
    sprintf(g->line[n++], "   notch. You drop. Further down is a spot dodge.");
    sprintf(g->line[n++], "3. Attack as you fall.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void sd_Think(CourseCtx* c)
{
    switch (c->phase) {
    case SD_WAIT:
        if (sd_IsShield(c->state)) {
            course_Phase(c, SD_SHIELD);
        } else if (c->state == ASID_PASS && c->state_frames == 1) {
            course_Result(c, 0, "Dropped without the shield\nshield first",
                          0, 0);
        }
        break;

    case SD_SHIELD:
        if (sd_IsShield(c->state)) {
            break;
        }
        if (c->state == ASID_PASS) {
            course_Phase(c, SD_DROP);
            sd.frame = 0;
        } else if (c->state == ASID_ESCAPE) {
            course_Result(c, 0, "Spot dodge\nstop at the diagonal notch", 0,
                          0);
        } else if (c->state == ASID_ESCAPEF || c->state == ASID_ESCAPEB) {
            course_Result(c, 0, "Roll\nmove the stick sideways slower", 0, 0);
        } else if (c->state == ASID_KNEEBEND) {
            course_Result(c, 0, "Jumped out of shield", 0, 0);
        } else {
            course_Phase(c, SD_WAIT); /* let go of the shield */
        }
        break;

    case SD_DROP:
        sd.frame++;
        if (mv_IsAerial(c->state)) {
            course_Measure(sd.frame, 1);
            course_Report("aerial", sd.frame);
            course_Result(c, 1, "Shield drop!\naerial %d frames after",
                          sd.frame, 0);
        } else if (sd.frame > SD_AERIAL_WINDOW) {
            course_Report("aerial", 0);
            course_Result(c, 1, "Shield drop!\nnow add an aerial", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_TechShieldDrop = {
    .Setup = sd_Setup,
    .Think = sd_Think,
    .help = { "Shield drop: in shield, stick fully sideways, then",
              "down to the diagonal notch. Attack as you fall.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = sd_reference,
    .Guide = sd_Guide,
};
