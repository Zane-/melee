/*
 * Defense drills, second file: fox-ledgedash-attack (getting off the
 * ledge) and fox-escape-chaingrab. Specs: data/courses/fox.md (Defense 11, 6). Included by ../event.c
 * after defense.inc.h.
 *
 * fox-escape-chaingrab is at the end of this file. Its first version, a
 * Marth that walked to stand under the falling player, never landed a
 * regrab: the player came down inside his grab's reach, and he is only
 * free about 15 frames before the landing.
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

/* ---- fox-escape-chaingrab -------------------------------------------------
 *
 * Marth grabs the player, up throws, and grabs again as the player comes
 * down, for as long as it works. The player holds a DI direction through
 * each throw and, if hitstun ends before the grab arrives, jumps or shines
 * away.
 *
 * Marth is only free about 15 frames before the player lands, so he does
 * not reposition: he turns round if the player is coming down behind him,
 * runs in if they are out of reach, and presses grab EC_GRAB_LEAD frames
 * before they reach the ground.
 */

enum { EC_OPT_PERCENT };
enum { EC_MARK_FREE = 1, EC_MARK_LOW };
enum { EC_FIRST, EC_AIR, EC_HELD };

#define EC_MAX_REGRABS 3
#define EC_SAFE 30        /* frames free and ungrabbed that count as out */
#define EC_REACH 14.0F    /* his grab reaches a player this far in front */
#define EC_GRAB_LEAD 8.0F /* frames before the ground he presses grab */

static EventOption ec_options[] = {
    [EC_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 151,
        .val = 10,
        .name = "Your Percent",
        .desc = { "Your damage at the start of each attempt.",
                  "The chain is tightest at low percent." },
        .format = "%d%%",
    },
};

static struct {
    int regrabs;
    int free;     /* frames the player has been acting on their own */
    int pressed;  /* Marth has pressed grab for this throw */
    int smashed;
    int down;     /* frames the player has lain on the floor */
    int acted;    /* the player has given an input since the throw */
    float last_y;
} ec;

/* The demonstration: hold the stick away from Marth from the grab on, and
 * tech away as Fox comes down (at low percent the stun outlasts the fall,
 * so jumping out is not possible: a jump at the end of the stun was tried
 * and Fox was already on the floor). */
static const CourseRefInput ec_reference[] = {
    { 0, TG_GRAB_AT + 8, 600, -127, 0, 0, 0, 0, 0, 0 },
    { EC_MARK_LOW, 1, 1, -127, 0, 0, 0, PAD_TRIGGER_R, 140, 0 },
    { COURSE_REF_END },
};

static void ec_Setup(CourseCtx* c)
{
    tg_Setup(c, (float) Options_Main[OPT_COMMON_COUNT + EC_OPT_PERCENT].val,
             127);
    memset(&ec, 0, sizeof(ec));
}

static void ec_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Marth's up throw drops a fast faller back into");
    sprintf(g->line[n++], "his hands, again and again, until percent or");
    sprintf(g->line[n++], "your DI ends it.");
    sprintf(g->line[n++], "Hold the stick left or right through every");
    sprintf(g->line[n++], "throw: he has to move to catch you.");
    sprintf(g->line[n++], "Then tech the landing (L or R as you come");
    sprintf(g->line[n++], "down), or jump out if the stun ends in the air.");
    sprintf(g->line[n++], "Stand still and let him grab you first.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void ec_End(CourseCtx* c, int success, char* fmt)
{
    course_Measure(ec.regrabs, 0);
    course_Report("regrabs", ec.regrabs);
    course_Result(c, success, fmt, ec.regrabs, 0);
}

/* Marth between throws: get the player in front of him, then grab. */
static void ec_Chase(CourseCtx* c)
{
    FighterData* hd = c->hd;
    FighterData* cd = c->cd;
    float dx = hd->phys.pos.X - cd->phys.pos.X;
    float fall = ec.last_y - hd->phys.pos.Y;
    /* how far in front of Marth the player is (negative: behind him) */
    float front = dx * cd->facing_direction;

    if (ec.pressed) {
        return;
    }
    if (front > EC_REACH) {
        cd->cpu.lstickX = dx > 0 ? 127 : -127; /* run to them */
    } else if (front < -2.0F) {
        cd->cpu.lstickX = dx > 0 ? 50 : -50; /* turn round */
    } else if (fall > 0 && hd->phys.pos.Y < fall * EC_GRAB_LEAD) {
        cd->cpu.held |= PAD_TRIGGER_Z;
        ec.pressed = 1;
    }
}

static void ec_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    FighterData* cd = c->cd;
    float dx = hd->phys.pos.X - cd->phys.pos.X;

    if (!tg_Advance(c)) {
        ec.last_y = hd->phys.pos.Y;
        return; /* the first grab and throw */
    }
    if (c->phase == EC_FIRST) {
        course_Phase(c, EC_AIR);
        ec.free = 0;
        ec.pressed = 0;
    }

    switch (c->phase) {
    case EC_AIR:
        if (df_Down(c->state)) {
            /* missed the tech and lies there: Marth stops (a smash does
             * not come out of a walk at once) and forward smashes */
            if (++ec.down > 8 && !ec.smashed) {
                cd->cpu.cstickX = dx > 0 ? 127 : -127;
                ec.smashed = 1;
            }
        } else {
            ec_Chase(c);
        }
        /* free: out of hitstun and doing something of the player's own */
        if (c->held != 0 || hd->input.lstick.X != 0 ||
            hd->input.lstick.Y != 0)
        {
            ec.acted = 1; /* doing nothing is not an escape */
        }
        if (ec.acted && !hd->flags.hitstun && c->timer > 6 &&
            !df_Down(c->state) && !df_Tech(c->state) &&
            c->state != ASID_DAMAGEFALL &&
            !(c->state >= ASID_DAMAGEHI1 && c->state <= ASID_DAMAGEFLYROLL))
        {
            ec.free++;
        }
        if (!hd->flags.hitstun && c->timer > 6) {
            course_Mark(c, EC_MARK_FREE);
        }
        {
            float fall = ec.last_y - hd->phys.pos.Y;
            if (fall > 0 && hd->phys.pos.Y < fall * 10.0F && c->timer > 6) {
                course_Mark(c, EC_MARK_LOW); /* about to land: tech now */
            }
        }
        if (nr_PlayerGrabbed(c)) {
            ec.regrabs++;
            if (ec.regrabs >= EC_MAX_REGRABS) {
                ec_End(c, 0, "Chain grabbed %d times\n"
                             "DI away and jump out");
            } else {
                course_Phase(c, EC_HELD);
            }
        } else if (c->hmn_hit && c->timer > 6) {
            ec_End(c, 0, "Hit out of the chain\nafter %d regrabs");
        } else if (c->cpu_hit) {
            ec_End(c, 1, "Out, and hit him!\nafter %d regrabs");
        } else if (ec.free > EC_SAFE) {
            ec_End(c, 1, "Out of the chain grab\nafter %d regrabs");
        } else if (c->timer > 400) {
            course_Retry(c, "Resetting");
        }
        break;

    case EC_HELD:
        /* held again: throw up after a moment, as tg_Advance does */
        if (nr_PlayerGrabbed(c)) {
            if (c->timer >= TG_THROW_AFTER) {
                cd->cpu.lstickY = 127;
            }
        } else if (hd->state_id < ASID_THROWNF ||
                   hd->state_id > ASID_THROWNLWWOMEN)
        {
            course_Phase(c, EC_AIR);
            ec.free = 0;
            ec.pressed = 0;
            ec.down = 0;
        }
        break;
    }
    ec.last_y = hd->phys.pos.Y;
}

static const CourseDrill Drill_DefChaingrab = {
    .Setup = ec_Setup,
    .Think = ec_Think,
    .options = ec_options,
    .option_count = countof(ec_options),
    .help = { "Marth chain grabs you. DI each throw and jump or",
              "shine out the moment you can.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = ec_reference,
    .live_marks = 1,
    .Guide = ec_Guide,
};
