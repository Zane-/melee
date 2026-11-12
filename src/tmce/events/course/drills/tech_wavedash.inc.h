/*
 * universal-wavedash: air dodge into the ground out of a jump.
 * Spec: data/courses/universal.md. Included by ../event.c.
 *
 * Perfect is an air dodge on the first airborne frame: the fighter never
 * shows a jump state and goes from jump squat straight to the special
 * landing (10 frames). Measured in the simulator with Fox (2026-11-12):
 * dodge one frame late = 1 frame of jump, then the air dodge, then the
 * landing; a dodge during jump squat does nothing and the jump comes out.
 */

/* Special landing after an air dodge: the wavedash's lag. */
#define WD_LANDING_FRAMES 10
/* Frames of jump without an air dodge before "no air dodge". */
#define WD_JUMP_TIMEOUT 12
/* Frames in the air dodge without landing before "too high". */
#define WD_DODGE_TIMEOUT 8
/* Ground covered below which it was a dodge straight down, not a dash. */
#define WD_MIN_SLIDE 4.0F

enum { WD_OPT_LENIENCY };
enum { WD_WAIT, WD_SQUAT, WD_JUMP, WD_DODGE, WD_LAND };

static EventOption wd_options[] = {
    [WD_OPT_LENIENCY] = COURSE_OPT_LENIENCY,
};

static struct {
    int jump_frames; /* frames of jump seen before the air dodge */
    float start_x;
} wd;

/* Jump, then R with the stick down and forward on the first airborne
 * frame: one jump squat later. */
static const CourseRefInput wd_reference[] = {
    { 0, 10, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 10, 2, 90, -90, 0, 0, PAD_TRIGGER_R, 140, 1 },
    { COURSE_REF_END },
};

static void wd_Setup(CourseCtx* c)
{
    course_PlaceSolo(c, 0);
    wd.jump_frames = 0;
    wd.start_x = 0;
}

static void wd_Guide(CourseCtx* c, CourseGuide* g)
{
    const CourseFighterData* me = course_Fighter(c->hd);
    int n = 0;
    sprintf(g->line[n++], "Jump, then air dodge diagonally into the ground");
    sprintf(g->line[n++], "the moment you leave it. You slide, and can act");
    sprintf(g->line[n++], "after %d frames of landing.", WD_LANDING_FRAMES);
    sprintf(g->line[n++], "1. Press X or Y.");
    sprintf(g->line[n++], "2. %d frames later: R (or L) with the stick",
            me->jump_squat);
    sprintf(g->line[n++], "   down and to the side.");
    sprintf(g->line[n++], "Too early and you only jump. Too late and you");
    sprintf(g->line[n++], "dodge in the air.");
    g->line_count = n;
}

static void wd_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    int lenient = course_Leniency(WD_OPT_LENIENCY);

    switch (c->phase) {
    case WD_WAIT:
        if (c->state == ASID_KNEEBEND) {
            course_Phase(c, WD_SQUAT);
            wd.jump_frames = 0;
            wd.start_x = hd->phys.pos.X;
        }
        break;

    case WD_SQUAT:
        if (c->state == ASID_KNEEBEND) {
            break;
        }
        course_Phase(c, WD_JUMP);
        /* fallthrough: classify the state that followed jump squat */
    case WD_JUMP:
        if (c->state == ASID_LANDINGFALLSPECIAL) {
            course_Phase(c, WD_LAND);
        } else if (c->state == ASID_ESCAPEAIR) {
            course_Phase(c, WD_DODGE);
        } else if (c->state == ASID_JUMPF || c->state == ASID_JUMPB) {
            wd.jump_frames++;
            if (wd.jump_frames > WD_JUMP_TIMEOUT) {
                /* a plain jump: not an attempt */
                course_Phase(c, WD_WAIT);
            }
        } else {
            course_Phase(c, WD_WAIT); /* an aerial, a special...: ignore */
        }
        break;

    case WD_DODGE:
        if (c->state == ASID_LANDINGFALLSPECIAL) {
            course_Phase(c, WD_LAND);
        } else if (c->state != ASID_ESCAPEAIR ||
                   c->timer > WD_DODGE_TIMEOUT)
        {
            course_Measure(wd.jump_frames + 1, 1);
            course_Result(c, 0, "Air dodged too high\n%d frames late",
                          wd.jump_frames, 0);
        }
        break;

    case WD_LAND:
        if (c->state == ASID_LANDINGFALLSPECIAL) {
            break;
        }
        {
            /* The air dodge came on airborne frame jump_frames + 1. */
            int frame = wd.jump_frames + 1;
            float slide = fabs(hd->phys.pos.X - wd.start_x);
            course_Measure(frame, 1);
            course_ReportF("slide", slide);
            if (slide < WD_MIN_SLIDE) {
                course_Result(c, 0, "No slide\nangle the stick sideways", 0,
                              0);
            } else if (frame - 1 > lenient) {
                course_Result(c, 0, "Late: airborne frame %d\nwant frame 1",
                              frame, 0);
            } else if (frame == 1) {
                course_Result(c, 1, "Perfect wavedash\nslid %d units",
                              (int) slide, 0);
            } else {
                course_Result(c, 1, "Wavedash, %d late\nslid %d units",
                              frame - 1, (int) slide);
            }
        }
        break;
    }
}

static const CourseDrill Drill_TechWavedash = {
    .flow = 1,
    .Setup = wd_Setup,
    .Think = wd_Think,
    .options = wd_options,
    .option_count = countof(wd_options),
    .help = { "Wavedash: jump, then air dodge diagonally into the",
              "ground as you leave it.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = wd_reference,
    .Guide = wd_Guide,
};
