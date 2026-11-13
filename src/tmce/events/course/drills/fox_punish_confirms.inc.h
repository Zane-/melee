/*
 * Fox's Punish drills that follow a landed hit: fox-aerial-confirm and
 * fox-shine-knockdown. Specs: data/courses/fox.md (Punish 7, 4). Included
 * by ../event.c after the other Punish files.
 */

/* ---- fox-aerial-confirm ---------------------------------------------------
 *
 * Marth stands or crouches (one or the other for the whole attempt). The
 * player lands an aerial on him and has to follow it up:
 *   - standing, he is in hitstun and then jumps away after his reaction
 *     time (th_CpuEscape): the next hit or grab has to come first;
 *   - crouching, he crouch cancels and shields as soon as he can, so a
 *     shine or up smash is blocked and the grab is the follow-up.
 * (A croucher who grabs on his first free frame was tried first: he grabs
 * Fox out of his landing lag whatever Fox does, which leaves nothing to
 * choose. Not landing that aerial at all is fox-approach-nair-dair.)
 */

enum { AC_OPT_STANCE, AC_OPT_PERCENT, AC_OPT_ESCAPE };
enum { AC_MARK_NEAR = 1, AC_MARK_LAND };
enum { AC_APPROACH, AC_FOLLOW };

#define AC_TIMEOUT 90

static const char* ac_opt_stance[] = { "Random", "Standing", "Crouching" };

static EventOption ac_options[] = {
    [AC_OPT_STANCE] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(ac_opt_stance),
        .name = "CPU Stance",
        .desc = { "Whether the CPU stands or crouches (and crouch",
                  "cancels your aerial)." },
        .values = ac_opt_stance,
    },
    [AC_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 151,
        .val = 20,
        .name = "CPU Percent",
        .desc = { "The CPU's damage at the start of each attempt." },
        .format = "%d%%",
    },
    [AC_OPT_ESCAPE] = TH_OPT_ESCAPE,
};

static struct {
    int crouch;
    int frame; /* frames since the aerial hit */
    int odd;
} ac;

/* The demonstration: run in, short hop from ST_NEAR with neutral air
 * (down air on a croucher), L-cancel (two presses, as in
 * fox-shield-pressure), and shine as the landing lag ends. */
static CourseRefInput ac_ref[10];

static const CourseRefInput* ac_BuildReference(CourseCtx* c)
{
    static const CourseRefInput end = { COURSE_REF_END };
    int js = course_Fighter(c->hd)->jump_squat;
    int n = 0;

    memset(ac_ref, 0, sizeof(ac_ref));
    ac_ref[n].frame = 5;
    ac_ref[n].hold = 400;
    ac_ref[n++].lx = 127;
    /* let go of the stick from the jump on, or Fox sails past */
    ac_ref[n].mark = AC_MARK_NEAR;
    ac_ref[n].frame = 1;
    ac_ref[n].hold = 200;
    ac_ref[n++].lx = 1;
    ac_ref[n].mark = AC_MARK_NEAR;
    ac_ref[n].frame = 1;
    ac_ref[n].hold = 1;
    ac_ref[n++].buttons = PAD_BUTTON_X;
    ac_ref[n].mark = AC_MARK_NEAR;
    ac_ref[n].frame = 1 + js;
    ac_ref[n].hold = 1;
    if (ac.crouch) {
        ac_ref[n++].cy = -127;
    } else {
        ac_ref[n++].buttons = PAD_BUTTON_A;
    }
    ac_ref[n].mark = AC_MARK_NEAR;
    ac_ref[n].frame = 1 + js + 16;
    ac_ref[n].hold = 1;
    ac_ref[n++].buttons = PAD_TRIGGER_Z;
    ac_ref[n].mark = AC_MARK_NEAR;
    ac_ref[n].frame = 1 + js + 21;
    ac_ref[n].hold = 1;
    ac_ref[n++].buttons = PAD_TRIGGER_Z;
    /* AC_MARK_LAND is announced when the landing lag is over */
    ac_ref[n].mark = AC_MARK_LAND;
    ac_ref[n].frame = 1;
    ac_ref[n].hold = 1;
    if (ac.crouch) {
        ac_ref[n++].buttons = PAD_TRIGGER_Z; /* grab the shield */
    } else {
        ac_ref[n].ly = -127;
        ac_ref[n++].buttons = PAD_BUTTON_B;
    }
    ac_ref[n] = end;
    return ac_ref;
}

static void ac_Setup(CourseCtx* c)
{
    int stance = Options_Main[OPT_COMMON_COUNT + AC_OPT_STANCE].val;
    float hmn_x = -c->side * ST_START / 2;
    course_Place(c, hmn_x, hmn_x + c->side * ST_START, 0,
                 (float) Options_Main[OPT_COMMON_COUNT + AC_OPT_PERCENT].val);
    if (stance != 0) {
        ac.crouch = stance == 2;
    } else if (course_IsDemo()) {
        ac.crouch = (course_DemoCount() + 1) % 2; /* standing first */
    } else {
        ac.crouch = HSD_Randi(2);
    }
    ac.frame = 0;
    ac.odd = 0;
    th.free = 0;
    th.jumped = 0;
    th.odd = 0;
    th.di = 0;
    th.react = th_escapes[course_IsDemo()
                              ? 1
                              : Options_Main[OPT_COMMON_COUNT + AC_OPT_ESCAPE]
                                    .val];
}

static void ac_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "An aerial that lands is only the start. What");
    sprintf(g->line[n++], "comes next depends on how they took it:");
    sprintf(g->line[n++], "Standing: they are stunned. Shine, grab or up");
    sprintf(g->line[n++], "  smash before they jump away.");
    sprintf(g->line[n++], "Crouching: they crouch cancel and have their");
    sprintf(g->line[n++], "  shield up at once. Grab.");
    sprintf(g->line[n++], "L-cancel the aerial, or neither works.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void ac_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    FighterData* cd = c->cd;
    float dist = nr_Dist(c);
    int aerial = mv_IsAerial(hd->state_id) || mv_IsAerialLanding(hd->state_id);

    if (dist < ST_NEAR) {
        course_Mark(c, AC_MARK_NEAR);
    }
    if (mv_IsAerialLanding(c->prev_state) && !mv_IsAerialLanding(c->state)) {
        course_Mark(c, AC_MARK_LAND);
    }
    course_Report("crouch", ac.crouch);

    switch (c->phase) {
    case AC_APPROACH:
        if (ac.crouch) {
            cd->cpu.lstickY = -127;
        }
        if (c->cpu_hit && aerial) {
            course_Phase(c, AC_FOLLOW);
            ac.frame = 0;
        } else if (c->cpu_hit || fpr_CpuGrabbed(c)) {
            course_Result(c, 0, "Open with an aerial", 0, 0);
        }
        break;

    case AC_FOLLOW:
        ac.frame++;
        if (ac.crouch) {
            course_CpuShield(c); /* up as soon as the crouch cancel allows */
        } else {
            th_CpuEscape(c);
        }
        if (nr_PlayerGrabbed(c) || c->hmn_hit) {
            course_Result(c, 0, "Got hit", 0, 0);
        } else if (c->cpu_state == ASID_GUARDSETOFF) {
            course_Result(c, 0, "Blocked: they crouch cancelled
"
                                "and shielded. Grab instead",
                          0, 0);
        } else if (fpr_CpuGrabbed(c) || (c->cpu_hit && !aerial)) {
            course_Measure(ac.frame, ac.frame);
            course_Report("frame", ac.frame);
            if (fst_IsShine(hd->state_id)) {
                course_Result(c, 1, "Aerial into shine\n%d frames later",
                              ac.frame, 0);
            } else if (fpr_CpuGrabbed(c)) {
                course_Result(c, 1, "Aerial into grab\n%d frames later",
                              ac.frame, 0);
            } else {
                course_Result(c, 1, "Confirmed\n%d frames after the aerial",
                              ac.frame, 0);
            }
        } else if (!ac.crouch && ac.frame > 6 &&
                   (fst_IsDoubleJump(c->cpu_state) ||
                    fst_IsJump(c->cpu_state)))
        {
            course_Result(c, 0, "They jumped away\nfollow up sooner", 0, 0);
        } else if (ac.frame > AC_TIMEOUT) {
            course_Result(c, 0, "No follow-up", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_FoxAerialConfirm = {
    .Setup = ac_Setup,
    .Think = ac_Think,
    .options = ac_options,
    .option_count = countof(ac_options),
    .help = { "Land an aerial, then follow it up before they jump",
              "away, or before they grab you if they crouched.",
              "D-Pad up: guide. D-Pad down: reset." },
    .BuildReference = ac_BuildReference,
    .live_marks = 1,
    .Guide = ac_Guide,
};

/* ---- fox-shine-knockdown --------------------------------------------------
 *
 * Falco or Fox stands next to the player's Fox; the shine knocks light
 * characters off their feet (Captain Falcon, tried first, only slides).
 * As he reaches the ground he techs in place, techs away, techs toward
 * Fox, or misses the tech and then gets up, rolls or attacks. The player
 * has to hit or grab him before he is on his feet and free again (he
 * shields from then on). A hit while he lies there counts: that is the
 * jab reset.
 */

enum { KD_TECH_PLACE, KD_TECH_AWAY, KD_TECH_IN, KD_MISS, KD_COUNT };
enum { KD_OPT_CHOICE };
enum { KD_WAIT, KD_FALL, KD_GROUND };

#define KD_TIMEOUT 200
#define KD_GETUP_WAIT 25 /* frames lying down after a missed tech */

static const char* kd_opt_choice[] = { "Random", "Tech in Place",
                                       "Tech Away", "Tech In", "No Tech" };
static const char* const kd_names[KD_COUNT] = { "tech in place", "tech away",
                                                "tech in", "missed tech" };

static EventOption kd_options[] = {
    [KD_OPT_CHOICE] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(kd_opt_choice),
        .name = "CPU Tech",
        .desc = { "What the CPU does when it hits the ground." },
        .values = kd_opt_choice,
    },
};

static struct {
    int choice;
    int frame;   /* frames since the shine hit */
    int pressed; /* the tech has been pressed */
    int down;    /* frames on the ground */
    int getup;   /* 0 stand, 1 roll away, 2 roll in, 3 attack */
} kd;

static void kd_Setup(CourseCtx* c)
{
    int opt = Options_Main[OPT_COMMON_COUNT + KD_OPT_CHOICE].val;
    float hmn_x = -c->side * (FPR_DISTANCE / 2);
    course_Place(c, hmn_x, hmn_x + c->side * FPR_DISTANCE, 0, 30.0F);
    memset(&kd, 0, sizeof(kd));
    kd.choice = opt > 0 ? opt - 1 : HSD_Randi(KD_COUNT);
    kd.getup = HSD_Randi(4);
}

static void kd_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Shine knocks fast fallers off their feet. As");
    sprintf(g->line[n++], "they land they choose: tech in place, tech");
    sprintf(g->line[n++], "away, tech toward you, or no tech at all.");
    sprintf(g->line[n++], "Watch, then cover it: every tech has a moment");
    sprintf(g->line[n++], "at its end where they cannot act.");
    sprintf(g->line[n++], "No tech: hit them as they lie there (a weak");
    sprintf(g->line[n++], "hit stands them up helpless: the jab reset).");
    sprintf(g->line[n++], "Stay close after the shine. Do not guess early.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void kd_Think(CourseCtx* c)
{
    FighterData* cd = c->cd;
    int hit_cpu = c->cpu_hit || fpr_CpuGrabbed(c);

    switch (c->phase) {
    case KD_WAIT:
        if (c->cpu_hit && fst_IsShine(c->hd->state_id)) {
            course_Phase(c, KD_FALL);
            kd.frame = 0;
        } else if (hit_cpu) {
            course_Result(c, 0, "Start with the shine", 0, 0);
        }
        break;

    case KD_FALL:
        kd.frame++;
        /* tech: one press as he comes down, with the direction held */
        if (kd.choice != KD_MISS) {
            if (kd.choice == KD_TECH_AWAY) {
                cd->cpu.lstickX = (s8) (-127 * c->toward);
            } else if (kd.choice == KD_TECH_IN) {
                cd->cpu.lstickX = (s8) (127 * c->toward);
            }
            /* he is back on the ground 6 frames after the hit; the press
             * comes after the shine's hitlag and before that */
            if (!kd.pressed && kd.frame >= 5) {
                cd->cpu.held |= PAD_TRIGGER_R;
                kd.pressed = 1;
            }
        }
        if (hit_cpu && kd.frame > 2) {
            course_Result(c, 1, "Hit him before he landed", 0, 0);
        } else if (kd.frame > 6 && cd->phys.air_state == 0) {
            course_Phase(c, KD_GROUND);
            kd.down = 0;
        } else if (kd.frame > KD_TIMEOUT) {
            course_Retry(c, "No knockdown\nresetting");
        }
        break;

    case KD_GROUND:
        kd.frame++;
        kd.down++;
        if (kd.choice == KD_MISS && kd.down > KD_GETUP_WAIT) {
            /* get up: stand, roll away, roll in or attack */
            if (kd.getup == 0) {
                cd->cpu.lstickY = 127;
            } else if (kd.getup == 1) {
                cd->cpu.lstickX = (s8) (-127 * c->toward);
            } else if (kd.getup == 2) {
                cd->cpu.lstickX = (s8) (127 * c->toward);
            } else if (kd.down & 1) {
                cd->cpu.held |= PAD_BUTTON_A;
            }
        }
        if (c->cpu_state == ASID_WAIT || c->cpu_state == ASID_GUARD ||
            c->cpu_state == ASID_GUARDON)
        {
            course_CpuShield(c);
        }
        course_Report("choice", kd.choice);
        if (c->hmn_hit) {
            course_Result(c, 0, "Hit by the getup attack", 0, 0);
        } else if (hit_cpu) {
            course_Measure(kd.frame, kd.frame);
            course_Report("frame", kd.frame);
            course_Message(MSGCOLOR_GREEN, "Covered the %s", kd_names[kd.choice],
                           0, 0);
            course_Result(c, 1, "Tech chase!\n%d frames after the shine",
                          kd.frame, 0);
        } else if (c->cpu_state == ASID_GUARDSETOFF) {
            course_Message(MSGCOLOR_RED, "It was a %s", kd_names[kd.choice], 0,
                           0);
            course_Result(c, 0, "Blocked\nhe was up and shielding", 0, 0);
        } else if (kd.frame > KD_TIMEOUT) {
            course_Message(MSGCOLOR_RED, "It was a %s", kd_names[kd.choice], 0,
                           0);
            course_Result(c, 0, "No punish", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_FoxShineKnockdown = {
    .Setup = kd_Setup,
    .Think = kd_Think,
    .options = kd_options,
    .option_count = countof(kd_options),
    .help = { "Shine him off his feet, watch where he techs, and",
              "hit or grab him before he is free.",
              "D-Pad up: guide. D-Pad down: reset." },
    .Guide = kd_Guide,
};
