/*
 * fox-shdl (short hop double laser) and fox-illusion-shorten.
 * Specs: data/courses/fox.md (Tech). Included by ../event.c.
 *
 * Measured with Fox in the simulator (2026-11-12). Frame 1 is the frame of
 * the input.
 *   - Laser in the air: 4 frames of start, then a 10-frame loop per shot;
 *     B pressed during a loop queues the next one. A short hop leaves the
 *     ground for 19 frames.
 *   - Illusion on the ground: 19 frames of start, then up to 4 frames of
 *     dash covering 18.7 units each after a first 23. B pressed 19 to 22
 *     frames after the side-B ends the dash early: 23, 23, 42 or 61 units
 *     instead of 79. A press 18 frames after or earlier does nothing.
 */

/* Fox's blaster and Illusion states (ftFox/forward.h): three ground laser
 * states from 0x155, three in the air, then Illusion start, dash, end. */
#define FSP_LASER_AIR_START 0x158
#define FSP_LASER_AIR_END 0x15A
#define FSP_ILLUSION_START 0x15B
#define FSP_ILLUSION_DASH 0x15C
#define FSP_ILLUSION_END 0x15D
#define FSP_ILLUSION_AIR_FIRST 0x15E
#define FSP_ILLUSION_AIR_LAST 0x160

/* Items in play that belong to the player (lasers, here). */
static int fsp_OwnItems(CourseCtx* c)
{
    GOBJ* g;
    int n = 0;
    for (g = (*stc_gobj_lookup)[MATCHPLINK_ITEM]; g != NULL; g = g->next) {
        ItemData* id = g->userdata;
        if (id != NULL && id->fighter_gobj == c->hmn) {
            n++;
        }
    }
    return n;
}

/* ---- fox-shdl ------------------------------------------------------------- */

enum { SHDL_WAIT, SHDL_SQUAT, SHDL_AIR };

static struct {
    int short_hop;
    int frame;       /* airborne frame */
    int first_laser; /* airborne frame the first laser state began, 0 = none */
    int lasers;
    int items;       /* own items last frame */
} shdl;

/* Jump, B as Fox leaves the ground, B again during the first shot. */
static const CourseRefInput shdl_reference[] = {
    { 0, 10, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 13, 1, 0, 0, 0, 0, PAD_BUTTON_B, 0, 0 },
    { 0, 20, 1, 0, 0, 0, 0, PAD_BUTTON_B, 0, 0 },
    { COURSE_REF_END },
};

static void shdl_Setup(CourseCtx* c)
{
    course_PlaceSolo(c, 0);
    memset(&shdl, 0, sizeof(shdl));
}

static void shdl_Guide(CourseCtx* c, CourseGuide* g)
{
    const CourseFighterData* me = course_Fighter(c->hd);
    int n = 0;
    sprintf(g->line[n++], "Two lasers from one short hop: Fox's way to");
    sprintf(g->line[n++], "make an opponent come to him.");
    sprintf(g->line[n++], "1. Short hop: release jump within %d frames.",
            me->jump_squat - 1);
    sprintf(g->line[n++], "2. B as you leave the ground (%d frames later).",
            me->jump_squat);
    sprintf(g->line[n++], "3. B again while the first laser is out.");
    sprintf(g->line[n++], "Keep the stick still: a direction with B is");
    sprintf(g->line[n++], "a different move.");
    g->line_count = n;
}

static void shdl_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    const CourseFighterData* me = course_Fighter(hd);
    int items = fsp_OwnItems(c);

    switch (c->phase) {
    case SHDL_WAIT:
        if (c->state == ASID_KNEEBEND) {
            course_Phase(c, SHDL_SQUAT);
        }
        break;

    case SHDL_SQUAT:
        if (c->state == ASID_KNEEBEND) {
            break;
        }
        memset(&shdl, 0, sizeof(shdl));
        shdl.short_hop = hd->phys.self_vel.Y < (me->hop_v + me->jump_v) / 2;
        shdl.items = items;
        course_Phase(c, SHDL_AIR);
        /* fallthrough */
    case SHDL_AIR:
        shdl.frame++;
        if (items > shdl.items) {
            shdl.lasers += items - shdl.items;
        }
        if (shdl.first_laser == 0 && c->state >= FSP_LASER_AIR_START &&
            c->state <= FSP_LASER_AIR_END)
        {
            shdl.first_laser = shdl.frame;
        }
        if (c->state == ASID_LANDING || c->state == ASID_WAIT ||
            shdl.frame > MV_AIR_TIMEOUT)
        {
            course_Measure(shdl.lasers, 2);
            course_Report("lasers", shdl.lasers);
            course_Report("first", shdl.first_laser);
            course_Report("short_hop", shdl.short_hop);
            if (!shdl.short_hop) {
                course_Result(c, 0, "Full hop\nrelease jump within %d frames",
                              me->jump_squat - 1, 0);
            } else if (shdl.lasers >= 2) {
                course_Result(c, 1, "Double laser!\n"
                                    "first on airborne frame %d",
                              shdl.first_laser, 0);
            } else if (shdl.lasers == 1) {
                course_Result(c, 0, "One laser: first B on\n"
                                    "airborne frame %d, B again",
                              shdl.first_laser, 0);
            } else {
                course_Phase(c, SHDL_WAIT); /* a plain jump: ignore */
            }
        }
        break;
    }
    shdl.items = items;
}

static const CourseDrill Drill_FoxShdl = {
    .flow = 1,
    .Setup = shdl_Setup,
    .Think = shdl_Think,
    .help = { "Short hop double laser: short hop, B as you leave",
              "the ground, B again.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = shdl_reference,
    .Guide = shdl_Guide,
};

/* ---- fox-illusion-shorten ------------------------------------------------- */

#define ILL_DASH_FULL 4    /* dash frames of an Illusion not shortened */
#define ILL_PRESS_FIRST 19 /* frames after side-B the press works from */
#define ILL_PRESS_LAST 22
#define ILL_TIMEOUT 120

enum { ILL_WAIT, ILL_START, ILL_DASH };

static struct {
    int frame;   /* frame of the move (1 = side-B) */
    int press;   /* frames after side-B of the first B press, 0 = none */
    int dash;    /* dash frames seen */
} ill;

/* Side-B, then B 20 frames later: the shortest Illusion. */
static const CourseRefInput ill_reference[] = {
    { 0, 10, 1, 127, 0, 0, 0, PAD_BUTTON_B, 0, 0 },
    { 0, 30, 1, 0, 0, 0, 0, PAD_BUTTON_B, 0, 0 },
    { COURSE_REF_END },
};

static void ill_Setup(CourseCtx* c)
{
    course_PlaceSolo(c, 0);
    memset(&ill, 0, sizeof(ill));
}

static void ill_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Fox Illusion (side+B) always travels the same");
    sprintf(g->line[n++], "distance unless you press B again as the dash");
    sprintf(g->line[n++], "begins. Then it stops short: aim it at the");
    sprintf(g->line[n++], "ledge or the stage and be harder to predict.");
    sprintf(g->line[n++], "Press B %d to %d frames after the side+B.",
            ILL_PRESS_FIRST, ILL_PRESS_LAST);
    sprintf(g->line[n++], "The earlier in that window, the shorter.");
    sprintf(g->line[n++], "Earlier than that, the press is ignored.");
    g->line_count = n;
    g->timeline_from = "frames (1 = side+B, the second B comes after 15)";
}

static void ill_Think(CourseCtx* c)
{
    if (c->phase != ILL_WAIT) {
        ill.frame++;
        if (ill.press == 0 && (c->down & PAD_BUTTON_B)) {
            ill.press = ill.frame - 1;
        }
    }
    switch (c->phase) {
    case ILL_WAIT:
        if (c->state == FSP_ILLUSION_START && c->state_frames == 1) {
            course_Phase(c, ILL_START);
            ill.frame = 1;
            ill.press = 0;
            ill.dash = 0;
        } else if (c->state == FSP_ILLUSION_AIR_FIRST &&
                   c->state_frames == 1)
        {
            course_Result(c, 0, "Use it on the ground here", 0, 0);
        }
        break;

    case ILL_START:
        if (c->state == FSP_ILLUSION_START) {
            if (ill.frame > ILL_TIMEOUT) {
                course_Result(c, 0, "Illusion did not finish", 0, 0);
            }
            break;
        }
        course_Phase(c, ILL_DASH);
        /* fallthrough */
    case ILL_DASH:
        if (c->state == FSP_ILLUSION_DASH) {
            ill.dash++;
            break;
        }
        {
            if (ill.press != 0) {
                /* how far from the earliest press that works */
                course_Measure(ill.press, ILL_PRESS_FIRST);
            }
            course_Report("dash", ill.dash);
            course_Report("press", ill.press);
            if (c->state != FSP_ILLUSION_END) {
                course_Result(c, 0, "Illusion interrupted", 0, 0);
            } else if (ill.dash >= ILL_DASH_FULL) {
                if (ill.press == 0) {
                    course_Result(c, 0, "Full length: no B press\n"
                                        "B %d to %d frames after",
                                  ILL_PRESS_FIRST, ILL_PRESS_LAST);
                } else if (ill.press < ILL_PRESS_FIRST) {
                    course_Result(c, 0, "Too early: B %d frames after\n"
                                        "want %d or later",
                                  ill.press, ILL_PRESS_FIRST);
                } else {
                    course_Result(c, 0, "Too late: B %d frames after\n"
                                        "want %d or sooner",
                                  ill.press, ILL_PRESS_LAST);
                }
            } else if (ill.dash <= 1) {
                course_Result(c, 1, "Shortest Illusion\nB %d frames after",
                              ill.press, 0);
            } else {
                course_Result(c, 1, "Shortened: %d of 4 dash\n"
                                    "frames, B %d after",
                              ill.dash, ill.press);
            }
        }
        break;
    }
}

static const CourseDrill Drill_FoxIllusionShorten = {
    .flow = 1,
    .Setup = ill_Setup,
    .Think = ill_Think,
    .help = { "Shortened Illusion: side+B, then B again as the",
              "dash begins (19 to 22 frames later).",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = ill_reference,
    .Guide = ill_Guide,
};
