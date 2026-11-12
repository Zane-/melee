/*
 * universal-short-hop: leave the ground with a short hop.
 * Spec: data/courses/universal.md. Included by ../event.c.
 *
 * A jump is a short hop when the jump button is no longer held on the last
 * frame of jump squat. The drill counts the frames the button was held and
 * reads the result off the first airborne frame's upward speed (short hop
 * and full hop speeds from the generated table).
 */

enum { SHOP_WAIT, SHOP_SQUAT };

static struct {
    int held; /* frames X/Y were held during jump squat */
} shop;

/* Jump at frame 10, held for 2 frames: short for every character (the
 * shortest jump squat is 3). */
static const CourseRefInput shop_reference[] = {
    { 0, 10, 2, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { COURSE_REF_END },
};

static void shop_Setup(CourseCtx* c)
{
    course_PlaceSolo(c, 0);
    shop.held = 0;
}

static void shop_Guide(CourseCtx* c, CourseGuide* g)
{
    const CourseFighterData* me = course_Fighter(c->hd);
    int n = 0;
    sprintf(g->line[n++], "A short hop is a jump whose button you let go");
    sprintf(g->line[n++], "before your character leaves the ground.");
    sprintf(g->line[n++], "Your jump squat is %d frames: release X or Y",
            me->jump_squat);
    sprintf(g->line[n++], "within %d frames of pressing it.",
            me->jump_squat - 1);
    sprintf(g->line[n++], "Tap the button. Do not hold it down.");
    g->line_count = n;
}

static void shop_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    const CourseFighterData* me = course_Fighter(hd);

    switch (c->phase) {
    case SHOP_WAIT:
        if (c->state == ASID_KNEEBEND) {
            course_Phase(c, SHOP_SQUAT);
            shop.held = 0;
        } else {
            break;
        }
        /* fallthrough: count this frame too */
    case SHOP_SQUAT:
        if (c->state == ASID_KNEEBEND) {
            if (c->held & (PAD_BUTTON_X | PAD_BUTTON_Y)) {
                shop.held++;
            }
        } else if (c->state == ASID_JUMPF || c->state == ASID_JUMPB) {
            int limit = me->jump_squat - 1;
            course_Measure(shop.held, limit);
            course_Report("held", shop.held);
            if (hd->phys.self_vel.Y < (me->hop_v + me->jump_v) / 2) {
                course_Result(c, 1, "Short hop!\nheld %d frames", shop.held,
                              0);
            } else {
                course_Result(c, 0, "Full hop\nheld %d, release by %d",
                              shop.held, limit);
            }
        } else {
            /* left jump squat some other way (hit, special...) */
            course_Phase(c, SHOP_WAIT);
        }
        break;
    }
}

static const CourseDrill Drill_TechShortHop = {
    .flow = 1,
    .Setup = shop_Setup,
    .Think = shop_Think,
    .help = { "Short hop: tap X or Y and let go before you leave",
              "the ground. D-Pad up: guide. D-Pad down: reset." },
    .reference = shop_reference,
    .Guide = shop_Guide,
};
