/*
 * Defense drills, first file: universal-tech, fox-escape-techchase,
 * fox-combo-shine, universal-asdi-down, universal-di-survival. Specs:
 * data/courses/fox.md (Defense). Included by ../event.c after the Punish
 * files. Here the CPU attacks and the player is graded on the answer.
 */

static int df_Down(int state)
{
    return state >= ASID_DOWNBOUNDU && state <= ASID_DOWNSPOTD;
}

static int df_Tech(int state)
{
    return state >= ASID_PASSIVE && state <= ASID_PASSIVESTANDB;
}

static int df_PlayerDead(CourseCtx* c)
{
    return c->hd->state_id <= ASID_DEADUPFALLHITCAMERAICE;
}

/* For the demonstrations' tech: the player has been sent flying for a few
 * frames and is on the way down. Sheik's down throw puts Fox on the ground
 * 23 frames after it lets go, so a press from here is inside the 20-frame
 * window (a mark by height was a frame too early). */
static int df_ComingDown(CourseCtx* c)
{
    return c->state >= ASID_DAMAGEFLYHI && c->state <= ASID_DAMAGEFLYROLL &&
           c->state_frames >= 8 && c->hd->phys.self_vel.Y < 0;
}

static void df_SetPercent(CourseCtx* c, float percent)
{
    c->hd->dmg.percent = percent;
    Fighter_SetHUDDamage(c->hd->ply, (u16) percent);
}

/* ---- the throw that starts universal-tech and fox-escape-techchase --------
 *
 * The CPU stands next to the player, grabs, and throws down. The player
 * is to let it. tg.thrown counts the frames since the throw let go.
 */

#define TG_GRAB_AT 20     /* attempt frame of the CPU's grab */
#define TG_THROW_AFTER 10 /* frames holding the player before the throw */
#define TG_GIVE_UP 150    /* no grab by then: the player avoided it */

static struct {
    int held;    /* frames the player has been held */
    int thrown;  /* frames since the throw began, 0 = not yet */
    int stick_y; /* the throw: -127 down, 127 up */
} tg;

static void tg_Setup(CourseCtx* c, float percent, int stick_y)
{
    float hmn_x = -c->side * (FPR_DISTANCE / 2);
    course_Place(c, hmn_x, hmn_x + c->side * FPR_DISTANCE, 0, 0);
    df_SetPercent(c, percent);
    tg.held = 0;
    tg.thrown = 0;
    tg.stick_y = stick_y;
}

/* Runs the grab and throw. Returns 1 from the frame the throw starts. */
static int tg_Advance(CourseCtx* c)
{
    FighterData* cd = c->cd;

    if (tg.thrown > 0) {
        tg.thrown++;
        return 1;
    }
    if (nr_PlayerGrabbed(c)) {
        tg.held++;
        if (tg.held >= TG_THROW_AFTER) {
            cd->cpu.lstickY = (s8) tg.stick_y;
        }
    } else if (tg.held > 0) {
        if (c->hd->state_id >= ASID_THROWNF &&
            c->hd->state_id <= ASID_THROWNLWWOMEN)
        {
            return 0; /* the throw's own animation, and its damage */
        }
        tg.thrown = 1; /* let go */
        return 1;
    } else if (c->timer == TG_GRAB_AT) {
        cd->cpu.held |= PAD_TRIGGER_Z;
    } else if (c->timer > TG_GIVE_UP) {
        course_Retry(c, "Stand still\nlet it grab you");
    }
    return 0;
}

/* ---- universal-tech ------------------------------------------------------- */

enum { DT_OPT_ASK, DT_OPT_PERCENT };
enum { DT_IN_PLACE, DT_AWAY, DT_IN, DT_COUNT };
enum { DT_MARK_LOW = 1 };
enum { DT_THROW, DT_AIR, DT_TECH };

#define DT_WINDOW 20  /* frames before the ground a press counts */
#define DT_TIMEOUT 200

static const char* dt_opt_ask[] = { "Random", "In Place", "Away", "In" };
static const char* const dt_names[DT_COUNT] = { "IN PLACE", "AWAY", "IN" };

static EventOption dt_options[] = {
    [DT_OPT_ASK] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(dt_opt_ask),
        .name = "Tech",
        .desc = { "Which tech the drill asks for." },
        .values = dt_opt_ask,
    },
    [DT_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 151,
        .val = 30,
        .name = "Your Percent",
        .desc = { "Your damage at the start of each attempt." },
        .format = "%d%%",
    },
};

static struct {
    int ask;
    int told;
    int press;   /* tg.thrown when L/R was last pressed, 0 = never */
    float tech_x; /* where the tech began */
} dt;

static CourseRefInput dt_ref[3];

/* The demonstration: R, with the stick held for the direction, as the
 * player comes down (DT_MARK_LOW). */
static const CourseRefInput* dt_BuildReference(CourseCtx* c)
{
    static const CourseRefInput end = { COURSE_REF_END };
    memset(dt_ref, 0, sizeof(dt_ref));
    dt_ref[0].mark = DT_MARK_LOW;
    dt_ref[0].frame = 1;
    dt_ref[0].hold = 30;
    /* positive X is toward the CPU */
    dt_ref[0].lx = dt.ask == DT_AWAY ? -127 : dt.ask == DT_IN ? 127 : 0;
    dt_ref[1].mark = DT_MARK_LOW;
    dt_ref[1].frame = 1;
    dt_ref[1].hold = 1;
    dt_ref[1].buttons = PAD_TRIGGER_R;
    dt_ref[1].trigger = 140;
    dt_ref[1].lx = dt_ref[0].lx;
    dt_ref[2] = end;
    return dt_ref;
}

static void dt_Setup(CourseCtx* c)
{
    int opt = Options_Main[OPT_COMMON_COUNT + DT_OPT_ASK].val;
    tg_Setup(c, (float) Options_Main[OPT_COMMON_COUNT + DT_OPT_PERCENT].val,
             -127);
    if (opt > 0) {
        dt.ask = opt - 1;
    } else if (course_IsDemo()) {
        dt.ask = (course_DemoCount() + DT_COUNT - 1) % DT_COUNT;
    } else {
        dt.ask = HSD_Randi(DT_COUNT);
    }
    dt.told = 0;
    dt.press = 0;
}

static void dt_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Thrown or knocked down, you choose how you");
    sprintf(g->line[n++], "land. Press L or R in the %d frames before you",
            DT_WINDOW);
    sprintf(g->line[n++], "touch the ground:");
    sprintf(g->line[n++], "Stick neutral: tech in place.");
    sprintf(g->line[n++], "Stick left or right: roll that way.");
    sprintf(g->line[n++], "A press too early locks you out for 40 frames:");
    sprintf(g->line[n++], "press once, as you come down.");
    sprintf(g->line[n++], "Stand still and let the opponent grab you.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void dt_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;

    if (!tg_Advance(c)) {
        if (tg.held > 0 && !dt.told) {
            dt.told = 1;
            course_Message(MSGCOLOR_WHITE, "Tech %s", dt_names[dt.ask], 0, 0);
        }
        return;
    }
    if (c->down & (PAD_TRIGGER_L | PAD_TRIGGER_R)) {
        dt.press = tg.thrown;
    }
    if (df_ComingDown(c)) {
        course_Mark(c, DT_MARK_LOW);
    }

    switch (c->phase) {
    case DT_THROW:
    case DT_AIR:
        if (df_Tech(c->state)) {
            dt.tech_x = hd->phys.pos.X;
            course_Phase(c, DT_TECH);
        } else if (df_Down(c->state)) {
            course_Report("ask", dt.ask);
            if (dt.press == 0) {
                course_Result(c, 0, "No tech\npress L or R as you land", 0,
                              0);
            } else {
                int early = tg.thrown - dt.press;
                course_Measure(early, DT_WINDOW);
                course_Result(c, 0, "Missed: pressed %d frames\n"
                                    "before landing, at most %d",
                              early, DT_WINDOW);
            }
        } else if (tg.thrown > DT_TIMEOUT) {
            course_Retry(c, "No knockdown\nresetting");
        }
        break;

    case DT_TECH:
        if (df_Tech(c->state)) {
            break;
        }
        {
            /* which way it went, seen from the CPU */
            float moved = (hd->phys.pos.X - dt.tech_x) * c->toward;
            int did = c->prev_state == ASID_PASSIVE ? DT_IN_PLACE
                      : moved > 0                   ? DT_AWAY
                                                    : DT_IN;
            course_Report("ask", dt.ask);
            course_Report("did", did);
            if (did == dt.ask) {
                course_Result(c, 1, "Tech!\njust what was asked", 0, 0);
            } else {
                course_Message(MSGCOLOR_RED, "Teched %s", dt_names[did], 0, 0);
                course_Result(c, 0, "A tech, but the wrong one", 0, 0);
            }
        }
        break;
    }
}

static const CourseDrill Drill_DefTech = {
    .Setup = dt_Setup,
    .Think = dt_Think,
    .options = dt_options,
    .option_count = countof(dt_options),
    .help = { "Let it throw you, then tech the way the drill asks:",
              "L or R as you land, stick for the direction.",
              "D-Pad up: guide. D-Pad down: reset." },
    .BuildReference = dt_BuildReference,
    .live_marks = 1,
    .Guide = dt_Guide,
};

/* ---- fox-escape-techchase -------------------------------------------------
 *
 * The same throw, but now the CPU chases: once it can see what the player
 * did on the ground it waits its reaction time, runs there and grabs. The
 * player gets away by being unpredictable is not something a CPU that
 * reacts can be fooled by; what works is acting on the first free frame
 * (jump, shine, spot dodge, attack) before the grab arrives, or a tech it
 * cannot reach in time.
 */

enum { TC_OPT_REACTION, TC_OPT_PERCENT };
enum { TC_MARK_LOW = 1, TC_MARK_FREE };
enum { TC_THROW, TC_SEEN, TC_CHASE };

#define TC_GRAB_FROM 14.0F
#define TC_SAFE 45 /* frames free and untouched that count as away */

static const char* tc_opt_reaction[] = { "Slow (24)", "Normal (16)",
                                         "Fast (10)" };
static const int tc_reactions[] = { 24, 16, 10 };

static EventOption tc_options[] = {
    [TC_OPT_REACTION] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(tc_opt_reaction),
        .name = "CPU Reaction",
        .desc = { "Frames the CPU takes to start after it sees",
                  "your tech." },
        .values = tc_opt_reaction,
    },
    [TC_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 151,
        .val = 30,
        .name = "Your Percent",
        .desc = { "Your damage at the start of each attempt." },
        .format = "%d%%",
    },
};

static struct {
    int seen;    /* frames since the player touched the ground */
    int pressed; /* the CPU has pressed its grab */
    int free;    /* frames the player has been free */
} tc;

/* The demonstration: tech away, then shine the moment the tech ends (a
 * jump was tried: Sheik's dash grab takes Fox out of his jump squat). */
static const CourseRefInput tc_reference[] = {
    { TC_MARK_LOW, 1, 30, -127, 0, 0, 0, 0, 0, 0 },
    { TC_MARK_LOW, 1, 1, -127, 0, 0, 0, PAD_TRIGGER_R, 140, 0 },
    { TC_MARK_FREE, 1, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { COURSE_REF_END },
};

static void tc_Setup(CourseCtx* c)
{
    tg_Setup(c, (float) Options_Main[OPT_COMMON_COUNT + TC_OPT_PERCENT].val,
             -127);
    memset(&tc, 0, sizeof(tc));
}

static void tc_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "After a throw the opponent watches where you");
    sprintf(g->line[n++], "tech and grabs you again there: a tech chase.");
    sprintf(g->line[n++], "Tech away from them to buy time, and act on");
    sprintf(g->line[n++], "your first free frame. Shine is frame 1: a");
    sprintf(g->line[n++], "jump is caught in its 3 frames on the ground.");
    sprintf(g->line[n++], "Not teching at all leaves you on the floor");
    sprintf(g->line[n++], "for them.");
    sprintf(g->line[n++], "Stand still and let the opponent grab you.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void tc_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    FighterData* cd = c->cd;
    int react = course_IsDemo()
                    ? tc_reactions[1]
                    : tc_reactions[Options_Main[OPT_COMMON_COUNT +
                                                TC_OPT_REACTION]
                                       .val];
    int busy;

    if (!tg_Advance(c)) {
        return;
    }
    if (df_ComingDown(c)) {
        course_Mark(c, TC_MARK_LOW);
    }
    busy = df_Tech(c->state) || df_Down(c->state) || hd->flags.hitstun ||
           nr_PlayerGrabbed(c) ||
           (c->state >= ASID_DAMAGEFLYHI && c->state <= ASID_DAMAGEFLYROLL);

    switch (c->phase) {
    case TC_THROW:
        if (tg.thrown > 3 && hd->phys.air_state == 0) {
            course_Phase(c, TC_SEEN);
            tc.seen = 0;
        }
        break;

    case TC_SEEN:
        if (++tc.seen >= react) {
            course_Phase(c, TC_CHASE);
        }
        break;

    case TC_CHASE:
        if (!tc.pressed) {
            float dx = hd->phys.pos.X - cd->phys.pos.X;
            cd->cpu.lstickX = dx > 0 ? 127 : -127;
            if (fabs(dx) < TC_GRAB_FROM) {
                if (df_Down(c->state)) {
                    cd->cpu.cstickY = -127; /* lying there: down smash */
                } else {
                    cd->cpu.held |= PAD_TRIGGER_Z;
                }
                tc.pressed = 1;
            }
        }
        break;
    }

    if (c->phase != TC_THROW) {
        if (!busy) {
            course_Mark(c, TC_MARK_FREE);
            tc.free++;
        }
        if (tg.thrown > 3 && (nr_PlayerGrabbed(c) || c->hmn_hit)) {
            course_Result(c, 0, tc.free > 0 ? "Caught after you were free\n"
                                              "act at once"
                                            : "Caught on the ground",
                          0, 0);
        } else if (c->cpu_hit) {
            course_Result(c, 1, "Hit them back!", 0, 0);
        } else if (tc.free > TC_SAFE ||
                   (tc.pressed && tc.free > 0 && c->cpu_state == ASID_WAIT))
        {
            course_Result(c, 1, "Got away", 0, 0);
        } else if (tg.thrown > 400) {
            course_Retry(c, "Resetting");
        }
    }
}

static const CourseDrill Drill_DefTechChase = {
    .Setup = tc_Setup,
    .Think = tc_Think,
    .options = tc_options,
    .option_count = countof(tc_options),
    .help = { "Let it throw you, tech, and get away before it",
              "grabs you again.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = tc_reference,
    .live_marks = 1,
    .Guide = tc_Guide,
};

/* ---- fox-combo-shine ------------------------------------------------------
 *
 * Marth jabs the player, steps in, and follows with a forward smash that
 * is not a true follow-up: there are some frames between the end of the
 * jab's hitstun (and the 4 frames of landing after it) and the smash's
 * hitbox. The shine (frame 1) fits in them.
 */

enum { CS_OPT_GAP, CS_OPT_PERCENT };
enum { CS_MARK_FREE = 1 };
enum { CS_WAIT, CS_JAB, CS_GAP };

#define CS_JAB_AT 30

/* Marth cannot smash sooner than about 26 frames after the jab input
 * (22 was tried: the input is lost in the jab), which leaves the player
 * some 20 free frames. Real strings are tighter, so the drill sets the
 * bar itself: the shine has to come within this many frames of being
 * free. */
static const char* cs_opt_gap[] = { "Wide (12)", "Medium (8)", "Tight (4)" };
static const int cs_gaps[] = { 12, 8, 4 };
#define CS_SMASH_AT 28 /* frames from the jab input to the smash input */

static EventOption cs_options[] = {
    [CS_OPT_GAP] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(cs_opt_gap),
        .name = "Gap",
        .desc = { "How many frames after you are free the shine",
                  "may come and still count." },
        .values = cs_opt_gap,
    },
    [CS_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 151,
        .val = 30,
        .name = "Your Percent",
        .desc = { "Your damage at the start of each attempt." },
        .format = "%d%%",
    },
};

static struct {
    int frame;      /* frames since the jab input */
    int was_stun;
    int free;       /* frames since hitstun ended, 0 = still in it */
    int shine_free; /* `free` when the shine came out */
} cs;

static const CourseRefInput cs_reference[] = {
    { CS_MARK_FREE, 1, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { COURSE_REF_END },
};

static void cs_Setup(CourseCtx* c)
{
    float hmn_x = -c->side * (FPR_DISTANCE / 2);
    course_Place(c, hmn_x, hmn_x + c->side * FPR_DISTANCE, 0, 20.0F);
    df_SetPercent(c,
                  (float) Options_Main[OPT_COMMON_COUNT + CS_OPT_PERCENT].val);
    memset(&cs, 0, sizeof(cs));
}

static void cs_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Not every string is a true combo. Between two");
    sprintf(g->line[n++], "hits there is often a moment where you can");
    sprintf(g->line[n++], "act, and Fox's shine comes out on frame 1.");
    sprintf(g->line[n++], "Marth jabs, then forward smashes. Take the jab");
    sprintf(g->line[n++], "and press down+B the instant its stun ends.");
    sprintf(g->line[n++], "The verdict counts the frames you waited: the");
    sprintf(g->line[n++], "Gap option sets how many are allowed.");
    sprintf(g->line[n++], "Do not hold shield: this is about the gap.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void cs_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    FighterData* cd = c->cd;
    int limit = cs_gaps[Options_Main[OPT_COMMON_COUNT + CS_OPT_GAP].val];
    int gap = CS_SMASH_AT;

    switch (c->phase) {
    case CS_WAIT:
        if (c->timer >= CS_JAB_AT) {
            course_Phase(c, CS_JAB);
            cs.frame = 0;
        }
        break;

    case CS_JAB:
    case CS_GAP:
        if (cs.frame == 0) {
            cd->cpu.held |= PAD_BUTTON_A;
        } else if (cs.frame == gap) {
            cd->cpu.cstickX = (s8) (127 * c->toward);
        } else if (cs.frame > 8 && cs.frame < gap) {
            /* step in after the jab: it pushed the player out of reach */
            cd->cpu.lstickX = (s8) (60 * c->toward);
        }
        cs.frame++;
        if (c->phase == CS_JAB) {
            if (c->hmn_hit) {
                course_Phase(c, CS_GAP);
            } else if (cs.frame > 40) {
                course_Retry(c, "The jab missed\nstand still for it");
            }
            break;
        }
        /* free: out of hitstun and past the landing that follows it */
        if (hd->flags.hitstun) {
            cs.was_stun = 1;
        } else if (c->state == ASID_WAIT ||
                   (c->state == ASID_LANDING &&
                    c->state_frames > course_Fighter(hd)->landing_lag) ||
                   cs.free > 0)
        {
            cs.free++;
            course_Mark(c, CS_MARK_FREE);
        }
        if (cs.shine_free == 0 && fst_IsShine(hd->state_id)) {
            cs.shine_free = cs.free > 0 ? cs.free : 1;
        }
        if (c->cpu_hit && fst_IsShine(hd->state_id)) {
            course_Measure(cs.shine_free, 1);
            course_Report("frame", cs.shine_free);
            if (cs.shine_free > limit) {
                course_Result(c, 0, "Too slow: free frame %d\n"
                                    "a real gap is about %d",
                              cs.shine_free, limit);
            } else {
                course_Result(c, 1, "Shined out!\non your free frame %d",
                              cs.shine_free, 0);
            }
        } else if (c->hmn_hit && c->timer > 2) {
            course_Report("free", cs.free);
            course_Result(c, 0, "Hit again\nyou had %d frames to shine",
                          cs.free, 0);
        } else if (hd->state_id == ASID_GUARDSETOFF) {
            course_Result(c, 0, "Shielded it\nshine in the gap instead", 0,
                          0);
        } else if (c->cpu_hit || fpr_CpuGrabbed(c)) {
            course_Result(c, 1, "Out, but not with the shine", 0, 0);
        } else if (cs.frame > gap + 60) {
            course_Result(c, 0, "The smash missed\nshine him anyway", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_DefComboShine = {
    .Setup = cs_Setup,
    .Think = cs_Think,
    .options = cs_options,
    .option_count = countof(cs_options),
    .help = { "Take the jab, then shine before the forward smash",
              "arrives.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = cs_reference,
    .live_marks = 1,
    .Guide = cs_Guide,
};

/* ---- universal-asdi-down --------------------------------------------------
 *
 * Marth down tilts the player from close range. Crouching (or just holding
 * down as it hits) at low percent keeps the player on the ground with
 * little stun, in time to hit Marth before his down tilt can be
 * interrupted (frame 20). The CPU does not use that interrupt, so the
 * drill fails a hit that comes more than AD_SLACK frames after it. Against
 * this down tilt the crouch still holds at 120% (simulator, 2026-11-12);
 * the "knocked over" verdict is there for stronger hits and is untested.
 */

enum { AD_OPT_PERCENT };
enum { AD_MARK_FREE = 1 };
enum { AD_WAIT, AD_ATTACK, AD_PUNISH };

#define AD_IASA 20
#define AD_SLACK 4 /* frames past that still counted */

static EventOption ad_options[] = {
    [AD_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 151,
        .val = 20,
        .name = "Your Percent",
        .desc = { "Your damage at the start of each attempt.",
                  "Raise it to find where the crouch stops working." },
        .format = "%d%%",
    },
};

static struct {
    int wait;
    int frame;    /* frames since the down tilt input */
    int crouched; /* the player was crouching when hit */
    int free;
} ad;

static const CourseRefInput ad_reference[] = {
    { 0, 5, 300, 0, -127, 0, 0, 0, 0, 0 },
    { AD_MARK_FREE, 1, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { COURSE_REF_END },
};

static void ad_Setup(CourseCtx* c)
{
    float hmn_x = -c->side * (FPR_DISTANCE / 2);
    course_Place(c, hmn_x, hmn_x + c->side * FPR_DISTANCE, 0, 20.0F);
    df_SetPercent(c,
                  (float) Options_Main[OPT_COMMON_COUNT + AD_OPT_PERCENT].val);
    memset(&ad, 0, sizeof(ad));
    ad.wait = course_IsDemo() ? AP_WAIT_MIN
                              : AP_WAIT_MIN + HSD_Randi(AP_WAIT_SPAN);
}

static void ad_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Holding down when a weak hit lands keeps you");
    sprintf(g->line[n++], "on the ground with almost no stun: you act");
    sprintf(g->line[n++], "while they are still finishing their move.");
    sprintf(g->line[n++], "Crouch, take the down tilt, and hit back at");
    sprintf(g->line[n++], "once (shine, grab, down smash).");
    sprintf(g->line[n++], "Stronger hits and higher percent knock you");
    sprintf(g->line[n++], "over anyway: try Your Percent in the menu.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void ad_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    FighterData* cd = c->cd;

    switch (c->phase) {
    case AD_WAIT:
        if (c->cpu_hit || fpr_CpuGrabbed(c)) {
            course_Result(c, 0, "Hit before it attacked\ntake the hit first",
                          0, 0);
        } else if (c->timer >= ad.wait) {
            course_Phase(c, AD_ATTACK);
            ad.frame = 0;
        }
        break;

    case AD_ATTACK:
    case AD_PUNISH:
        if (ad.frame == 0) {
            cd->cpu.lstickY = -80;
            cd->cpu.held |= PAD_BUTTON_A;
        } else if (ad.frame >= AD_IASA) {
            course_CpuShield(c);
        }
        ad.frame++;
        if (c->phase == AD_ATTACK) {
            if (c->hmn_hit) {
                ad.crouched =
                    (c->state >= ASID_SQUAT && c->state <= ASID_SQUATRV) ||
                    (c->prev_state >= ASID_SQUAT &&
                     c->prev_state <= ASID_SQUATRV);
                course_Phase(c, AD_PUNISH);
            } else if (hd->state_id == ASID_GUARDSETOFF) {
                course_Result(c, 0, "Shielded it\ncrouch and take it", 0, 0);
            } else if (ad.frame > 50) {
                course_Retry(c, "The down tilt missed\nstay close");
            }
            break;
        }
        if (c->state == ASID_SQUATWAIT || c->state == ASID_SQUAT ||
            c->state == ASID_WAIT)
        {
            ad.free++;
            course_Mark(c, AD_MARK_FREE);
        }
        course_Report("crouched", ad.crouched);
        if (df_Down(c->state) || c->state == ASID_DAMAGEFALL ||
            (hd->state_id >= ASID_DAMAGEFLYHI &&
             hd->state_id <= ASID_DAMAGEFLYROLL))
        {
            course_Result(c, 0, "Knocked over\ntoo much percent for this", 0,
                          0);
        } else if (c->cpu_hit || fpr_CpuGrabbed(c)) {
            course_Measure(ad.frame, AD_IASA);
            course_Report("frame", ad.frame);
            if (ad.frame > AD_IASA + AD_SLACK) {
                /* the CPU does not use its early interrupt, a player would */
                course_Result(c, 0, "Hit on frame %d of his move
"
                                    "he can act from frame %d",
                              ad.frame, AD_IASA);
            } else {
                course_Result(c, 1, ad.crouched ? "Crouch cancel punish!\n"
                                                  "on frame %d of his move"
                                                : "Punished\non frame %d",
                              ad.frame, 0);
            }
        } else if (c->cpu_state == ASID_GUARDSETOFF) {
            course_Result(c, 0, ad.crouched ? "Too slow: blocked"
                                            : "Too slow: blocked\n"
                                              "hold down as it hits",
                          0, 0);
        } else if (ad.frame > 90) {
            course_Result(c, 0, "No punish", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_DefAsdiDown = {
    .Setup = ad_Setup,
    .Think = ad_Think,
    .options = ad_options,
    .option_count = countof(ad_options),
    .help = { "Crouch, take the down tilt, and hit back before",
              "he can shield.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = ad_reference,
    .live_marks = 1,
    .Guide = ad_Guide,
};

/* ---- universal-di-survival ------------------------------------------------
 *
 * Fox up smashes the player at a percent where it kills off the top
 * without DI and does not with it. The stick has to be held sideways on
 * the frame the hit's freeze ends.
 */

/* Found with a sweep in the simulator: see the drill's specs. */
#define DS_DEFAULT_PERCENT 90
enum { DS_OPT_PERCENT };
enum { DS_MARK_ATTACK = 1 };
enum { DS_WAIT, DS_ATTACK, DS_FLY };

#define DS_SURVIVE 150 /* frames alive after the hit that count as lived */

static EventOption ds_options[] = {
    [DS_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 201,
        .val = DS_DEFAULT_PERCENT,
        .name = "Your Percent",
        .desc = { "Your damage at the start of each attempt." },
        .format = "%d%%",
    },
};

static struct {
    int wait;
    int frame; /* frames since the up smash input */
    int fly;   /* frames since the hit */
} ds;

/* Hold the stick away from the CPU from just before the hit. */
static const CourseRefInput ds_reference[] = {
    { DS_MARK_ATTACK, 5, 40, -127, 0, 0, 0, 0, 0, 0 },
    { COURSE_REF_END },
};

static void ds_Setup(CourseCtx* c)
{
    float hmn_x = -c->side * (FPR_DISTANCE / 2);
    course_Place(c, hmn_x, hmn_x + c->side * FPR_DISTANCE, 0, 20.0F);
    df_SetPercent(c,
                  (float) Options_Main[OPT_COMMON_COUNT + DS_OPT_PERCENT].val);
    memset(&ds, 0, sizeof(ds));
    ds.wait = course_IsDemo() ? AP_WAIT_MIN
                              : AP_WAIT_MIN + HSD_Randi(AP_WAIT_SPAN);
}

static void ds_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "The stick, held as a hit's freeze ends, bends");
    sprintf(g->line[n++], "the path you are sent on (DI). You cannot slow");
    sprintf(g->line[n++], "down, only turn.");
    sprintf(g->line[n++], "Fox's up smash sends you straight up to the");
    sprintf(g->line[n++], "top. Hold left or right as it hits: the path");
    sprintf(g->line[n++], "leans toward the corner, which is further.");
    sprintf(g->line[n++], "Up or down does nothing here: DI works across");
    sprintf(g->line[n++], "the direction you are sent, not along it.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void ds_Think(CourseCtx* c)
{
    FighterData* cd = c->cd;

    switch (c->phase) {
    case DS_WAIT:
        if (c->timer >= ds.wait) {
            course_Mark(c, DS_MARK_ATTACK);
            course_Phase(c, DS_ATTACK);
            ds.frame = 0;
        }
        break;

    case DS_ATTACK:
        if (ds.frame == 0) {
            cd->cpu.cstickY = 127;
        }
        ds.frame++;
        if (c->hmn_hit) {
            course_Phase(c, DS_FLY);
            ds.fly = 0;
        } else if (c->hd->state_id == ASID_GUARDSETOFF) {
            course_Result(c, 0, "Shielded it\ntake the hit and DI", 0, 0);
        } else if (ds.frame > 50) {
            course_Retry(c, "The up smash missed\nstay close");
        }
        break;

    case DS_FLY:
        ds.fly++;
        if (df_PlayerDead(c)) {
            course_Measure(ds.fly, DS_SURVIVE);
            course_Result(c, 0, "Star KO after %d frames\n"
                                "hold left or right as it hits",
                          ds.fly, 0);
        } else if (ds.fly > DS_SURVIVE ||
                   (ds.fly > 30 && !c->hd->flags.hitstun &&
                    c->hd->phys.self_vel.Y <= 0))
        {
            course_Measure(ds.fly, ds.fly);
            course_Result(c, 1, "Survived!\nthe DI bent the path", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_DefDiSurvival = {
    .Setup = ds_Setup,
    .Think = ds_Think,
    .options = ds_options,
    .option_count = countof(ds_options),
    .help = { "Hold left or right as the up smash hits, and",
              "survive it.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = ds_reference,
    .live_marks = 1,
    .Guide = ds_Guide,
};
