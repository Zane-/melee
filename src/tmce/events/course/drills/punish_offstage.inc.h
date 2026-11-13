/*
 * Fox's offstage Punish drills: fox-shine-spike and fox-edgeguard-onstage.
 * Specs: data/courses/fox.md (Punish 9, 10). Included by ../event.c after
 * the Defense files.
 *
 * Marth starts in the air off the left ledge with his double jump and
 * recovers by himself (os_CpuRecover): either high (jump at once, up B to
 * land on the stage) or low (fall, jump late, up B to the ledge). The
 * player stands near the ledge.
 */

enum { OS_OPT_CHOICE, OS_OPT_PERCENT };
enum { OS_HIGH, OS_LOW, OS_CHOICES };
enum { OS_EDGEGUARD, OS_RETURN };

#define OS_CPU_OUT 58.0F   /* Marth starts this far outside the ledge */
#define OS_CPU_UP 6.0F     /* and this far above it */
#define OS_PLAYER_IN 18.0F /* the player this far inside it */
#define OS_BACK 25         /* frames Marth stands on the stage = recovered */
#define OS_TIMEOUT 700
#define OS_HANG 15         /* frames he hangs before getting up */

static const char* os_opt_choice[] = { "Random", "High", "Low" };

static EventOption os_options[] = {
    [OS_OPT_CHOICE] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(os_opt_choice),
        .name = "CPU Recovery",
        .desc = { "High: jumps at once and up Bs onto the stage.",
                  "Low: falls, jumps late and up Bs to the ledge." },
        .values = os_opt_choice,
    },
    [OS_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 201,
        .val = 80,
        .name = "CPU Percent",
        .desc = { "The CPU's damage at the start of each attempt." },
        .format = "%d%%",
    },
};

static struct {
    Vec3 ledge;
    int choice;
    int jumped;
    int upb;
    float last_y;   /* Marth's height last frame */
    int on_stage;   /* frames Marth has stood on the stage */
    int hang;       /* frames he has hung on the ledge */
    int frame;
    int shined;     /* the shine hit him off the stage */
    int left_stage; /* the player went out past the ledge */
} os;

static void os_Setup(CourseCtx* c)
{
    int opt = Options_Main[OPT_COMMON_COUNT + OS_OPT_CHOICE].val;
    float percent =
        (float) Options_Main[OPT_COMMON_COUNT + OS_OPT_PERCENT].val;

    memset(&os, 0, sizeof(os));
    if (!course_LedgePos(&os.ledge)) {
        return;
    }
    course_PlaceOnPlatform(c, os.ledge.X + OS_PLAYER_IN, os.ledge.Y + 20.0F);
    c->hd->facing_direction = -1.0F; /* looking out at him */
    course_PlaceInAir(Fighter_GetGObj(1), os.ledge.X - OS_CPU_OUT,
                      os.ledge.Y + OS_CPU_UP, 1.0F, percent);
    os.choice = opt > 0 ? opt - 1 : HSD_Randi(OS_CHOICES);
    os.last_y = os.ledge.Y + OS_CPU_UP;
}

/* Marth's recovery. One input per decision; the stick stays toward the
 * stage. */
static void os_CpuRecover(CourseCtx* c)
{
    FighterData* cd = c->cd;
    float dy = cd->phys.pos.Y - os.ledge.Y;
    int falling = cd->phys.pos.Y < os.last_y;
    float jump_below = os.choice == OS_HIGH ? 8.0F : -28.0F;
    float upb_below = os.choice == OS_HIGH ? -2.0F : -18.0F;

    os.last_y = cd->phys.pos.Y;
    if (cd->phys.air_state == 0) {
        os.on_stage++;
        return;
    }
    os.on_stage = 0;
    if (lg_OnLedge(cd->state_id)) {
        if (++os.hang > OS_HANG) {
            cd->cpu.lstickX = 127; /* get up */
        }
        return;
    }
    os.hang = 0;
    cd->cpu.lstickX = 127;
    if (cd->flags.hitstun) {
        os.upb = 0; /* hit out of it: he may up B again */
        return;
    }
    if (!os.jumped && dy < jump_below) {
        cd->cpu.held |= PAD_BUTTON_X;
        os.jumped = 1;
    } else if (os.jumped && !os.upb && falling && dy < upb_below) {
        cd->cpu.lstickX = 40;
        cd->cpu.lstickY = 127;
        cd->cpu.held |= PAD_BUTTON_B;
        os.upb = 1;
    }
}

/* Shared bookkeeping. Returns 0 when the attempt has been decided. */
static int os_Advance(CourseCtx* c)
{
    FighterData* hd = c->hd;

    os.frame++;
    if (c->phase == OS_EDGEGUARD) {
        os_CpuRecover(c);
    }
    if (hd->phys.pos.X < os.ledge.X - 12.0F) {
        os.left_stage = 1;
    }
    if (c->cpu_hit && fst_IsShine(hd->state_id) &&
        c->cd->phys.pos.X < os.ledge.X)
    {
        os.shined = 1;
    }
    course_Report("choice", os.choice);
    course_Report("shined", os.shined);
    if (df_PlayerDead(c)) {
        course_Result(c, 0, c->phase == OS_RETURN
                                ? "Got the stock, lost yours\n"
                                  "save your jump to get back"
                                : "You fell",
                      0, 0);
        return 0;
    }
    if (c->hmn_hit) {
        course_Result(c, 0, "Hit by the recovery", 0, 0);
        return 0;
    }
    if (c->phase == OS_EDGEGUARD && os.on_stage > OS_BACK) {
        course_Result(c, 0, os.choice == OS_HIGH
                                ? "He made it back: high\n"
                                  "he lands on the stage"
                                : "He made it back: low\n"
                                  "he goes for the ledge",
                      0, 0);
        return 0;
    }
    if (os.frame > OS_TIMEOUT) {
        course_Result(c, 0, "Out of time", 0, 0);
        return 0;
    }
    return 1;
}

/* ---- fox-shine-spike ------------------------------------------------------ */

static void ss_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Off the stage the shine sends them sideways");
    sprintf(g->line[n++], "and down with their jump gone: one touch ends");
    sprintf(g->line[n++], "the stock.");
    sprintf(g->line[n++], "1. Go out to them: run off, or jump out.");
    sprintf(g->line[n++], "2. Down+B when you touch them.");
    sprintf(g->line[n++], "3. Jump out of the shine and get back: keep");
    sprintf(g->line[n++], "   your double jump for that.");
    sprintf(g->line[n++], "High recovery or low: watch which he picks.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void ss_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;

    if (!os_Advance(c)) {
        return;
    }
    switch (c->phase) {
    case OS_EDGEGUARD:
        if (th_CpuDead(c)) {
            course_Phase(c, OS_RETURN);
        }
        break;

    case OS_RETURN:
        if (lg_OnLedge(c->state) ||
            (hd->phys.air_state == 0 && hd->phys.pos.X > os.ledge.X))
        {
            course_Report("shined", os.shined);
            if (os.shined) {
                course_Result(c, 1, "Shine spike!\nand back on the stage", 0,
                              0);
            } else {
                course_Result(c, 0, "The stock, but no shine\n"
                                    "that is the Edgeguard drill",
                              0, 0);
            }
        }
        break;
    }
}

static const CourseDrill Drill_FoxShineSpike = {
    .Setup = os_Setup,
    .Think = ss_Think,
    .options = os_options,
    .option_count = countof(os_options),
    .help = { "Go out, shine him off the stage, and get back.",
              "",
              "D-Pad up: guide. D-Pad down: reset." },
    .Guide = ss_Guide,
};

/* ---- fox-edgeguard-onstage ------------------------------------------------ */

static void eg_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "You do not have to leave the stage to stop a");
    sprintf(g->line[n++], "recovery. Watch which way he comes:");
    sprintf(g->line[n++], "High, landing on the stage: hit him as he");
    sprintf(g->line[n++], "  arrives (back air, up smash, down smash).");
    sprintf(g->line[n++], "Low, to the ledge: take the ledge yourself so");
    sprintf(g->line[n++], "  he cannot, or down smash as he grabs it.");
    sprintf(g->line[n++], "The stock has to go: one hit is often not");
    sprintf(g->line[n++], "enough, so be ready for the second try.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void eg_Think(CourseCtx* c)
{
    if (!os_Advance(c)) {
        return;
    }
    if (th_CpuDead(c)) {
        course_Report("left_stage", os.left_stage);
        course_Measure(os.frame, os.frame);
        course_Result(c, 1, os.left_stage ? "Stock taken\n"
                                            "but you went out for it"
                                          : "Edgeguarded from the stage",
                      0, 0);
    }
}

static const CourseDrill Drill_FoxEdgeguard = {
    .Setup = os_Setup,
    .Think = eg_Think,
    .options = os_options,
    .option_count = countof(os_options),
    .help = { "Stop his recovery without leaving the stage: hit",
              "him as he lands, or take the ledge.",
              "D-Pad up: guide. D-Pad down: reset." },
    .Guide = eg_Guide,
};
