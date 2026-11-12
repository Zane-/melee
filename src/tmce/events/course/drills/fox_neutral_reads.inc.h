/*
 * Fox's Neutral drills, second file: fox-approach-nair-dair,
 * fox-vs-crouch-cancel, fox-running-shine, fox-laser-forcing,
 * fox-shield-then-punish. Specs: data/courses/fox.md (Neutral). Included
 * by ../event.c after fox_neutral.inc.h.
 */

static float nr_Dist(CourseCtx* c)
{
    return fabs(c->cd->phys.pos.X - c->hd->phys.pos.X);
}

static int nr_PlayerGrabbed(CourseCtx* c)
{
    return c->state >= ASID_CAPTUREPULLEDHI && c->state <= ASID_CAPTUREFOOT;
}

/* ---- fox-approach-nair-dair and fox-vs-crouch-cancel ----------------------
 *
 * The CPU stands, crouches or shields, and changes every second or so.
 * What it is doing when the player's move arrives decides the verdict:
 * anything hits a standing opponent; a croucher crouch-cancels everything
 * weak, so it takes down air, shine or a grab; a shield takes a grab.
 * fox-vs-crouch-cancel is the same with the CPU always crouching.
 */

enum { ST_STAND, ST_CROUCH, ST_SHIELD, ST_COUNT };
enum { ST_MARK_NEAR = 1, ST_MARK_GRAB };

#define ST_START 45.0F
#define ST_NEAR 30.0F      /* the demonstration jumps from here */
#define ST_GRAB_FROM 22.0F /* and starts its jump-cancelled grab here */
#define ST_SWITCH_MIN 50
#define ST_SWITCH_SPAN 60

static struct {
    int stance;
    int next;        /* frames until the CPU changes stance */
    int always_crouch;
} st;

enum { ST_OPT_STANCE };
static const char* st_opt_stance[] = { "Changing", "Standing", "Crouching",
                                       "Shielding" };
static EventOption st_options[] = {
    [ST_OPT_STANCE] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(st_opt_stance),
        .name = "CPU Stance",
        .desc = { "What the CPU does: one thing, or changing",
                  "between the three." },
        .values = st_opt_stance,
    },
};

/* The stance the option fixes, or -1 for changing. */
static int st_Fixed(void)
{
    if (st.always_crouch) {
        return ST_CROUCH;
    }
    return Options_Main[OPT_COMMON_COUNT + ST_OPT_STANCE].val - 1;
}

static void st_Pick(CourseCtx* c)
{
    if (st_Fixed() >= 0) {
        st.stance = st_Fixed();
    } else if (course_IsDemo()) {
        /* one stance per demonstration, each in turn */
        st.stance = (course_DemoCount() + ST_COUNT - 1) % ST_COUNT;
    } else {
        st.stance = HSD_Randi(ST_COUNT);
    }
    st.next = ST_SWITCH_MIN + HSD_Randi(ST_SWITCH_SPAN);
}

static void st_Place(CourseCtx* c)
{
    float hmn_x = -c->side * ST_START / 2;
    course_Place(c, hmn_x, hmn_x + c->side * ST_START, 0, 20.0F);
    st_Pick(c);
}

static void st_Setup(CourseCtx* c)
{
    st.always_crouch = 0;
    st_Place(c);
}

static void cc_Setup(CourseCtx* c)
{
    st.always_crouch = 1;
    st_Place(c);
}

static CourseRefInput st_ref[8];

/* The demonstration: run in; against a shield, a jump-cancelled grab;
 * otherwise a short hop from ST_NEAR with neutral air (standing) or down
 * air (crouching) out as Fox leaves the ground. */
static const CourseRefInput* st_BuildReference(CourseCtx* c)
{
    static const CourseRefInput end = { COURSE_REF_END };
    int js = course_Fighter(c->hd)->jump_squat;
    int n = 0;

    memset(st_ref, 0, sizeof(st_ref));
    st_ref[n].frame = 5;
    st_ref[n].hold = 400;
    st_ref[n++].lx = 127;
    if (st.stance == ST_SHIELD) {
        st_ref[n].mark = ST_MARK_GRAB;
        st_ref[n].frame = 1;
        st_ref[n].hold = 1;
        st_ref[n++].buttons = PAD_BUTTON_X;
        st_ref[n].mark = ST_MARK_GRAB;
        st_ref[n].frame = 2;
        st_ref[n].hold = 1;
        st_ref[n++].buttons = PAD_TRIGGER_Z;
    } else {
        st_ref[n].mark = ST_MARK_NEAR;
        st_ref[n].frame = 1;
        st_ref[n].hold = 1;
        st_ref[n++].buttons = PAD_BUTTON_X;
        st_ref[n].mark = ST_MARK_NEAR;
        st_ref[n].frame = 1 + js;
        st_ref[n].hold = 1;
        if (st.stance == ST_CROUCH) {
            st_ref[n++].cy = -127;
        } else {
            st_ref[n++].buttons = PAD_BUTTON_A;
        }
    }
    st_ref[n] = end;
    return st_ref;
}

static void st_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Look before you go in. What the opponent is");
    sprintf(g->line[n++], "doing decides what works:");
    sprintf(g->line[n++], "Standing: short hop neutral air.");
    sprintf(g->line[n++], "Crouching: they crouch cancel a neutral air and");
    sprintf(g->line[n++], "  hit back. Down air, shine or grab instead.");
    sprintf(g->line[n++], "Shielding: an aerial is blocked and you get");
    sprintf(g->line[n++], "  grabbed. Grab them.");
    sprintf(g->line[n++], "They change. Go when you know what you see.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void cc_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "At low percent a crouching opponent barely");
    sprintf(g->line[n++], "moves when hit, and hits you back before you");
    sprintf(g->line[n++], "can act. That is the crouch cancel.");
    sprintf(g->line[n++], "It does not work against:");
    sprintf(g->line[n++], "Down air (it sends them down into the floor),");
    sprintf(g->line[n++], "shine (it knocks them off their feet),");
    sprintf(g->line[n++], "and grabs.");
    sprintf(g->line[n++], "Do not neutral air a croucher.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void st_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    float dist = nr_Dist(c);

    /* the CPU's stance */
    if (st_Fixed() < 0 && !course_IsDemo() && --st.next <= 0) {
        int was = st.stance;
        st_Pick(c);
        if (st.stance == was) {
            st.stance = (was + 1) % ST_COUNT;
        }
    }
    if (st.stance == ST_CROUCH) {
        c->cd->cpu.lstickY = -127;
    } else if (st.stance == ST_SHIELD) {
        course_CpuShield(c);
    }

    if (dist < ST_NEAR) {
        course_Mark(c, ST_MARK_NEAR);
    }
    if (dist < ST_GRAB_FROM) {
        course_Mark(c, ST_MARK_GRAB);
    }

    course_Report("stance", st.stance);
    if (fpr_CpuGrabbed(c)) {
        course_Result(c, 1, "Grab!\nworks on every stance", 0, 0);
    } else if (c->cpu_state == ASID_GUARDSETOFF) {
        course_Result(c, 0, "Blocked\ngrab a shielding opponent", 0, 0);
    } else if (c->cpu_hit) {
        int dair = hd->state_id == ASID_ATTACKAIRLW ||
                   hd->state_id == ASID_LANDINGAIRLW;
        int shine = fst_IsShine(hd->state_id);
        if (st.stance != ST_CROUCH) {
            course_Result(c, 1, "Hit them standing", 0, 0);
        } else if (dair) {
            course_Result(c, 1, "Down air beats the crouch", 0, 0);
        } else if (shine) {
            course_Result(c, 1, "Shine beats the crouch", 0, 0);
        } else {
            course_Result(c, 0, "Crouch cancelled\n"
                                "down air, shine or grab",
                          0, 0);
        }
    } else if (c->hmn_hit || nr_PlayerGrabbed(c)) {
        course_Result(c, 0, "Got hit", 0, 0);
    }
}

static const CourseDrill Drill_FoxApproach = {
    .Setup = st_Setup,
    .Think = st_Think,
    .options = st_options,
    .option_count = countof(st_options),
    .help = { "Standing: neutral air. Crouching: down air, shine",
              "or grab. Shielding: grab.",
              "D-Pad up: guide. D-Pad down: reset." },
    .BuildReference = st_BuildReference,
    .live_marks = 1,
    .Guide = st_Guide,
};

static const CourseDrill Drill_FoxVsCrouchCancel = {
    .Setup = cc_Setup,
    .Think = st_Think,
    .help = { "They crouch cancel: open them with down air, shine",
              "or a grab, never neutral air.",
              "D-Pad up: guide. D-Pad down: reset." },
    .BuildReference = st_BuildReference,
    .live_marks = 1,
    .Guide = cc_Guide,
};

/* ---- fox-running-shine ----------------------------------------------------
 *
 * The CPU dash dances on the spot and now and then short hops. The player
 * runs in and shines it: frame 1, so it catches a dash or the start of a
 * jump that a slower move would lose to.
 */

enum { RS_MARK_CLOSE = 1 };

#define RS_START 50.0F
#define RS_CLOSE 13.0F /* the demonstration shines from here */
#define RS_DASH 9      /* frames the CPU dashes each way */

static struct {
    int frame;
    int hop; /* frames left of a short hop the CPU is doing */
} rs;

static const CourseRefInput rs_reference[] = {
    { 0, 5, 400, 127, 0, 0, 0, 0, 0, 0 },
    { RS_MARK_CLOSE, 1, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { COURSE_REF_END },
};

static void rs_Setup(CourseCtx* c)
{
    float hmn_x = -c->side * RS_START / 2;
    course_Place(c, hmn_x, hmn_x + c->side * RS_START, 0, 20.0F);
    rs.frame = 0;
    rs.hop = 0;
}

static void rs_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Shine comes out on frame 1. Run at an opponent");
    sprintf(g->line[n++], "who is dash dancing or about to jump and shine:");
    sprintf(g->line[n++], "nothing they start now is faster.");
    sprintf(g->line[n++], "Run in, then down+B when you are touching them.");
    sprintf(g->line[n++], "The shine is small. Too early and it misses.");
    sprintf(g->line[n++], "Then jump out of it: waveshine, or up smash.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void rs_Think(CourseCtx* c)
{
    FighterData* cd = c->cd;

    /* the CPU: dash away, dash back, sometimes a short hop in between */
    rs.frame++;
    if (rs.hop > 0) {
        rs.hop--;
    } else if (rs.frame % (RS_DASH * 2) == 0 && !course_IsDemo() &&
               HSD_Randi(4) == 0)
    {
        cd->cpu.held |= PAD_BUTTON_X;
        rs.hop = 30;
    } else {
        int away = (rs.frame / RS_DASH) % 2;
        cd->cpu.lstickX = (s8) ((away ? -127 : 127) * c->toward);
    }

    if (nr_Dist(c) < RS_CLOSE) {
        course_Mark(c, RS_MARK_CLOSE);
    }
    if (c->cpu_hit) {
        if (fst_IsShine(c->hd->state_id)) {
            course_Result(c, 1, "Running shine!", 0, 0);
        } else {
            course_Result(c, 0, "Hit, but not with the shine", 0, 0);
        }
    } else if (fpr_CpuGrabbed(c)) {
        course_Result(c, 0, "A grab, not the shine", 0, 0);
    } else if (fst_IsShine(c->state) && c->state_frames == 12) {
        course_Result(c, 0, "The shine missed\nget closer first", 0, 0);
    }
}

static const CourseDrill Drill_FoxRunningShine = {
    .Setup = rs_Setup,
    .Think = rs_Think,
    .help = { "Running shine: run at the dash dancing opponent",
              "and shine when you touch them.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = rs_reference,
    .live_marks = 1,
    .Guide = rs_Guide,
};

/* ---- fox-laser-forcing ----------------------------------------------------
 *
 * The CPU (Marth) waits far away. Lasers do not flinch, but nobody lets
 * them add up: after a few it runs in with a dash attack (the whiff punish
 * drill's: reach 50, hitbox gone after script frame 23, acts again on 48).
 * The player answers that approach: any hit or grab that is not a laser,
 * before being hit.
 */

enum { LF_MARK_ATTACK = 1, LF_MARK_STUN_END };
enum { LF_LASER, LF_RUN, LF_ATTACK };

#define LF_START 90.0F
#define LF_REACH 50.0F
#define LF_FAF 48
#define LF_LASER_DAMAGE 3.5F /* a hit of at most this is a laser */

static const CourseInput lf_dash_attack[] = {
    { 0, 9, 127, 0, 0, 0, 0 },
    { 8, 1, 127, 0, 0, 0, PAD_BUTTON_A },
    { -1 },
};

static struct {
    int lasers;       /* lasers that have hit */
    int need;         /* lasers before the CPU comes */
    float percent;    /* the CPU's damage last frame */
    int attack_frame;
    int shielded;     /* the player was in shieldstun */
} lf;

/* The demonstration: one short hop double laser, shield the dash attack,
 * up smash out of shield (jump-cancelled) when shieldstun ends. */
static const CourseRefInput lf_reference[] = {
    { 0, 5, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { 0, 8, 1, 0, 0, 0, 0, PAD_BUTTON_B, 0, 0 },
    { 0, 15, 1, 0, 0, 0, 0, PAD_BUTTON_B, 0, 0 },
    { LF_MARK_ATTACK, 1, 60, 0, 0, 0, 0, PAD_TRIGGER_R, 140, 0 },
    { LF_MARK_STUN_END, 1, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { LF_MARK_STUN_END, 2, 1, 0, 0, 0, 127, 0, 0, 0 },
    { COURSE_REF_END },
};

static void lf_Setup(CourseCtx* c)
{
    float hmn_x = -c->side * LF_START / 2;
    course_Place(c, hmn_x, hmn_x + c->side * LF_START, 0, 0);
    memset(&lf, 0, sizeof(lf));
    lf.need = course_IsDemo() ? 2 : 2 + HSD_Randi(3);
}

static void lf_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Lasers do little damage and no hitstun, but an");
    sprintf(g->line[n++], "opponent cannot stand in them for ever. They");
    sprintf(g->line[n++], "have to come to you, and you know it.");
    sprintf(g->line[n++], "1. Short hop lasers from far away.");
    sprintf(g->line[n++], "2. After a few they run in and attack.");
    sprintf(g->line[n++], "3. Be ready: shield it and punish, or make it");
    sprintf(g->line[n++], "   miss and punish. Do not be mid-laser.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void lf_Think(CourseCtx* c)
{
    FighterData* cd = c->cd;
    float gained = cd->dmg.percent - lf.percent;
    int laser = c->cpu_hit && gained <= LF_LASER_DAMAGE;
    int real_hit = (c->cpu_hit && !laser) || fpr_CpuGrabbed(c);

    lf.percent = cd->dmg.percent;
    if (laser) {
        lf.lasers++;
    }

    switch (c->phase) {
    case LF_LASER:
        if (real_hit) {
            course_Result(c, 0, "Hit before it came\nlaser from far away", 0,
                          0);
        } else if (lf.lasers >= lf.need) {
            course_Phase(c, LF_RUN);
        }
        break;

    case LF_RUN:
        cd->cpu.lstickX = (s8) (127 * c->toward);
        if (nr_Dist(c) < LF_REACH) {
            course_Mark(c, LF_MARK_ATTACK);
            course_Phase(c, LF_ATTACK);
            lf.attack_frame = 0;
        }
        /* fallthrough: the hit checks apply while it runs in too */
    case LF_ATTACK:
        if (c->phase == LF_ATTACK) {
            course_Script(c, lf_dash_attack, lf.attack_frame);
            lf.attack_frame++;
        }
        if (c->hd->state_id == ASID_GUARDSETOFF) {
            lf.shielded = 1;
        } else if (lf.shielded) {
            course_Mark(c, LF_MARK_STUN_END);
        }
        if (c->hmn_hit) {
            course_Report("lasers", lf.lasers);
            course_Result(c, 0, "Got hit\nstop shooting when it comes", 0, 0);
        } else if (real_hit) {
            course_Measure(lf.lasers, lf.need);
            course_Report("lasers", lf.lasers);
            course_Report("shielded", lf.shielded);
            course_Result(c, 1, "Forced it and punished\nafter %d lasers",
                          lf.lasers, 0);
        } else if (c->phase == LF_ATTACK && lf.attack_frame >= LF_FAF) {
            course_Report("lasers", lf.lasers);
            course_Result(c, 0, "No punish\nit attacked and recovered", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_FoxLaserForcing = {
    .Setup = lf_Setup,
    .Think = lf_Think,
    .help = { "Laser from far away. When the opponent runs in,",
              "stop shooting and punish the approach.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = lf_reference,
    .live_marks = 1,
    .Guide = lf_Guide,
};

/* ---- fox-shield-then-punish -----------------------------------------------
 *
 * The CPU comes in with one of the jump-in aerials of the wavedash back
 * drill (WavedashBack_Deck), or, about one time in three, runs up and
 * grabs. The aerial is to be shielded and punished out of shield; the
 * grab cannot be shielded, so the player has to see which it is.
 */

enum { SP_MARK_ATTACK = 1, SP_MARK_STUN_END, SP_MARK_CLOSE };
enum { SP_WAIT, SP_ATTACK };

#define SP_GRAB_START 40.0F /* start distance when the CPU will grab */
#define SP_GRAB_FROM 14.0F  /* it presses Z this close */
#define SP_SHINE_FROM 15.0F /* the demonstration shines it from here */
#define SP_BUSY_MIN 20      /* frames before the CPU can count as done */

static struct {
    int grab;         /* this attempt is the grab */
    int wait;
    int attack_frame;
    int pressed;      /* the CPU has pressed Z */
    int shielded;
} sp;

static CourseRefInput sp_ref[8];

/* The demonstration. Aerial: hold shield, then jump and shine as
 * shieldstun ends. Grab: shine it as it arrives (a spot dodge was tried:
 * the dash grab carries the CPU through Fox and out of reach). */
static const CourseRefInput* sp_BuildReference(CourseCtx* c)
{
    static const CourseRefInput end = { COURSE_REF_END };
    int js = course_Fighter(c->hd)->jump_squat;
    int n = 0;

    memset(sp_ref, 0, sizeof(sp_ref));
    if (sp.grab) {
        /* hit it first: the shine is out on frame 1 */
        sp_ref[n].mark = SP_MARK_CLOSE;
        sp_ref[n].frame = 1;
        sp_ref[n].hold = 1;
        sp_ref[n].ly = -127;
        sp_ref[n++].buttons = PAD_BUTTON_B;
    } else {
        sp_ref[n].mark = SP_MARK_ATTACK;
        sp_ref[n].frame = 1;
        sp_ref[n].hold = 90;
        sp_ref[n].buttons = PAD_TRIGGER_R;
        sp_ref[n++].trigger = 140;
        sp_ref[n].mark = SP_MARK_STUN_END;
        sp_ref[n].frame = 1;
        sp_ref[n].hold = 1;
        sp_ref[n++].buttons = PAD_BUTTON_X;
        sp_ref[n].mark = SP_MARK_STUN_END;
        sp_ref[n].frame = 1 + js;
        sp_ref[n].hold = 1;
        sp_ref[n].ly = -127;
        sp_ref[n++].buttons = PAD_BUTTON_B;
    }
    sp_ref[n] = end;
    return sp_ref;
}

static void sp_Setup(CourseCtx* c)
{
    float gap, hmn_x;

    memset(&sp, 0, sizeof(sp));
    /* demonstrations alternate: aerial first */
    sp.grab = course_IsDemo() ? (course_DemoCount() + 1) % 2
                              : HSD_Randi(3) == 0;
    gap = sp.grab ? SP_GRAB_START : wp_Scenario(c)->reach;
    hmn_x = -c->side * gap / 2;
    course_Place(c, hmn_x, hmn_x + c->side * gap, 0, 20.0F);
    sp.wait = course_IsDemo() ? AP_WAIT_MIN
                              : AP_WAIT_MIN + HSD_Randi(AP_WAIT_SPAN);
}

static void sp_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Shielding an approach and hitting back out of");
    sprintf(g->line[n++], "shield is safe, so opponents mix in grabs.");
    sprintf(g->line[n++], "They jump: shield, then shine out of shield");
    sprintf(g->line[n++], "  (jump, down+B as you leave the ground).");
    sprintf(g->line[n++], "They run at you on the ground: that is the");
    sprintf(g->line[n++], "  grab. Hit them first (shine is frame 1), or");
    sprintf(g->line[n++], "  jump or dodge it and punish the miss.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void sp_Think(CourseCtx* c)
{
    FighterData* cd = c->cd;
    const WhiffScenario* sc = wp_Scenario(c);
    int hit_cpu = c->cpu_hit || fpr_CpuGrabbed(c);
    /* The CPU is done when it stands again: on shield its landing comes
     * later than the scenario's `faf`, which is for a miss. */
    int done = sp.attack_frame > SP_BUSY_MIN && c->cpu_state == ASID_WAIT &&
               (!sp.grab || sp.pressed);

    if (c->phase == SP_WAIT) {
        if (hit_cpu) {
            course_Result(c, 0, "Hit before it came\nwait for the approach",
                          0, 0);
        } else if (c->timer >= sp.wait) {
            course_Mark(c, SP_MARK_ATTACK);
            course_Phase(c, SP_ATTACK);
        }
        return;
    }

    /* the CPU */
    if (!sp.grab) {
        course_Script(c, sc->inputs, sp.attack_frame);
    } else if (!sp.pressed) {
        cd->cpu.lstickX = (s8) (127 * c->toward);
        if (nr_Dist(c) < SP_GRAB_FROM) {
            cd->cpu.held |= PAD_TRIGGER_Z;
            sp.pressed = 1;
        }
    }
    sp.attack_frame++;

    /* marks for the demonstration */
    if (sp.grab && nr_Dist(c) < SP_SHINE_FROM) {
        course_Mark(c, SP_MARK_CLOSE);
    }
    if (c->hd->state_id == ASID_GUARDSETOFF) {
        sp.shielded = 1;
    } else if (sp.shielded) {
        course_Mark(c, SP_MARK_STUN_END);
    }

    course_Report("grab", sp.grab);
    if (nr_PlayerGrabbed(c)) {
        course_Result(c, 0, "Grabbed\nit ran in: do not shield that", 0, 0);
    } else if (c->hmn_hit) {
        course_Result(c, 0, "Got hit\nit jumped: shield that", 0, 0);
    } else if (hit_cpu) {
        course_Measure(sp.attack_frame, sp.attack_frame);
        course_Report("shielded", sp.shielded);
        if (sp.grab) {
            course_Result(c, 1, "Saw the grab\nand punished it", 0, 0);
        } else if (sp.shielded) {
            course_Result(c, 1, "Shielded and punished", 0, 0);
        } else {
            course_Result(c, 1, "Punished without the shield", 0, 0);
        }
    } else if (done) {
        course_Result(c, 0, sp.grab ? "No punish\nthe grab missed, hit back"
                                    : "No punish\nhit back out of shield",
                      0, 0);
    }
}

static const CourseDrill Drill_FoxShieldThenPunish = {
    .Setup = sp_Setup,
    .Think = sp_Think,
    .help = { "A jump-in: shield it and shine out of shield.",
              "A run-up grab: dodge it, then punish.",
              "D-Pad up: guide. D-Pad down: reset." },
    .BuildReference = sp_BuildReference,
    .live_marks = 1,
    .Guide = sp_Guide,
};
