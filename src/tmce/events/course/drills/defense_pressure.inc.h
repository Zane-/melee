/*
 * Defense drills, third file: universal-sdi, fox-escape-pressure and
 * fox-recovery-mixup. Specs: data/courses/fox.md (Defense 4, 7, 10).
 * Included by ../event.c after punish_offstage.inc.h.
 */

/* ---- universal-sdi --------------------------------------------------------
 *
 * Fox short hops a down air (the drill: up to seven weak hits; three land
 * from this short hop) onto the standing player and shines as he lands. Each hit freezes both for a moment, and
 * every fresh push of the stick during a freeze moves the player a little
 * (smash DI). Enough pushes away and the later hits, or the shine, miss.
 */

enum { SX_MARK_HIT = 1 };
enum { SX_WAIT, SX_DRILL, SX_SHINE };

#define SX_START 12.0F
#define SX_SHINE_REACH 14.0F /* the CPU only shines a player this close */
#define SX_TAPS 14

static const CourseInput sx_dair[] = {
    { 0, 1, 0, 0, 0, 0, PAD_BUTTON_X },
    { 4, 8, 127, 0, 0, 0, 0 },
    { 10, 1, 0, 0, 0, -127, 0 },
    { 22, 1, 0, 0, 0, 0, PAD_TRIGGER_Z },
    { 26, 1, 0, 0, 0, 0, PAD_TRIGGER_Z },
    { -1 },
};

static struct {
    int wait;
    int frame;      /* script frame of the down air */
    int hits;       /* hits taken */
    float start_x;  /* where the player stood */
    int landed;     /* the CPU has landed */
    int shine_frame; /* frames since the CPU shined, 0 = not yet */
} sx;

static CourseRefInput sx_ref[SX_TAPS + 1];

/* The demonstration: from the first hit, push the stick away from the CPU
 * on every other frame, so that each push is a fresh one. */
static const CourseRefInput* sx_BuildReference(CourseCtx* c)
{
    static const CourseRefInput end = { COURSE_REF_END };
    int i;
    memset(sx_ref, 0, sizeof(sx_ref));
    for (i = 0; i < SX_TAPS; i++) {
        sx_ref[i].mark = SX_MARK_HIT;
        sx_ref[i].frame = 1 + 2 * i;
        sx_ref[i].hold = 1;
        sx_ref[i].lx = -127;
    }
    sx_ref[SX_TAPS] = end;
    return sx_ref;
}

static void sx_Setup(CourseCtx* c)
{
    float hmn_x = -c->side * (SX_START / 2);
    course_Place(c, hmn_x, hmn_x + c->side * SX_START, 0, 20.0F);
    df_SetPercent(c, 20.0F);
    memset(&sx, 0, sizeof(sx));
    sx.wait = course_IsDemo() ? AP_WAIT_MIN
                              : AP_WAIT_MIN + HSD_Randi(AP_WAIT_SPAN);
    sx.start_x = hmn_x;
}

static void sx_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Every hit freezes you for a moment. Each time");
    sprintf(g->line[n++], "you push the stick to a new position during");
    sprintf(g->line[n++], "that freeze, you move a little: smash DI.");
    sprintf(g->line[n++], "Fox's down air hits over and over, then he");
    sprintf(g->line[n++], "shines. Take the first hit, then tap the");
    sprintf(g->line[n++], "stick away from him again and again (or roll");
    sprintf(g->line[n++], "it between away and diagonal) until you are");
    sprintf(g->line[n++], "out. Holding it still does nothing.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void sx_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    FighterData* cd = c->cd;
    float moved = fabs(hd->phys.pos.X - sx.start_x);

    switch (c->phase) {
    case SX_WAIT:
        if (moved > 4.0F) {
            course_Retry(c, "Stand still\ntake the first hit");
        } else if (c->timer >= sx.wait) {
            course_Phase(c, SX_DRILL);
            sx.frame = 0;
        }
        break;

    case SX_DRILL:
        course_Script(c, sx_dair, sx.frame);
        sx.frame++;
        if (c->hmn_hit) {
            sx.hits++;
            course_Mark(c, SX_MARK_HIT);
        }
        if (hd->state_id == ASID_GUARDSETOFF) {
            course_Result(c, 0, "Shielded it\ntake the hit and SDI", 0, 0);
        } else if (sx.frame > 12 && cd->phys.air_state == 0) {
            sx.landed = 1;
            if (sx.hits == 0) {
                course_Retry(c, "The down air missed\nstand still for it");
            } else if (c->cpu_state == ASID_WAIT) {
                /* out of landing lag: shine if the player is still there */
                if (nr_Dist(c) < SX_SHINE_REACH) {
                    cd->cpu.lstickY = -127;
                    cd->cpu.held |= PAD_BUTTON_B;
                    course_Phase(c, SX_SHINE);
                    sx.shine_frame = 0;
                } else {
                    course_Measure(sx.hits, 1);
                    course_Report("hits", sx.hits);
                    course_ReportF("moved", moved);
                    course_Result(c, 1, "Out of the drill!\ntook %d hits",
                                  sx.hits, 0);
                }
            }
        } else if (sx.frame > 120) {
            course_Retry(c, "Resetting");
        }
        break;

    case SX_SHINE:
        sx.shine_frame++;
        if (c->hmn_hit) {
            course_Measure(sx.hits, 1);
            course_Report("hits", sx.hits);
            course_ReportF("moved", moved);
            course_Result(c, 0, "%d hits and the shine\n"
                                "tap away during the hits",
                          sx.hits, 0);
        } else if (sx.shine_frame > 8) {
            course_Measure(sx.hits, 1);
            course_Report("hits", sx.hits);
            course_ReportF("moved", moved);
            course_Result(c, 1, "The shine missed!\ntook %d hits", sx.hits,
                          0);
        }
        break;
    }
}

static const CourseDrill Drill_DefSdi = {
    .Setup = sx_Setup,
    .Think = sx_Think,
    .help = { "Take the first hit of the down air, then tap the",
              "stick away over and over to slide out of it.",
              "D-Pad up: guide. D-Pad down: reset." },
    .BuildReference = sx_BuildReference,
    .live_marks = 1,
    .Guide = sx_Guide,
};

/* ---- fox-escape-pressure --------------------------------------------------
 *
 * A CPU Fox pressures the player's shield: short hop, late neutral air,
 * L-cancel, wait, shine, jump out of the shine, and again. The wait before
 * each shine is the hole in it, set by an option. The player gets out by
 * hitting him in that hole (shine out of shield: jump, down+B) or by
 * leaving unhit.
 */

enum { EP_OPT_GAP };
enum { EP_MARK_HOLE = 1 };
enum { EP_WAIT_SHIELD, EP_PRESSURE };

#define EP_START 9.0F
#define EP_AERIAL_AT 13 /* airborne frame of the neutral air */
#define EP_SHINE_FRAMES 7 /* frames of shine before he jumps out */
#define EP_AWAY 32.0F   /* this far from him, unhit, is out */

static const char* ep_opt_gap[] = { "Wide (12)", "Medium (8)", "Tight (4)" };
static const int ep_gaps[] = { 12, 8, 4 };

static EventOption ep_options[] = {
    [EP_OPT_GAP] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(ep_opt_gap),
        .name = "Gap",
        .desc = { "Frames the CPU leaves between landing and",
                  "its shine." },
        .values = ep_opt_gap,
    },
};

static struct {
    int air;     /* frames airborne in this hop */
    int aerial;  /* the aerial has been pressed this hop */
    int cancel;  /* the L-cancel has been pressed this hop */
    int landed;  /* frames standing since the landing */
    int was_air;
    int shine;   /* frames in the shine */
    float last_y;
} ep;

static const CourseRefInput ep_reference[] = {
    { 0, 0, 900, 0, 0, 0, 0, PAD_TRIGGER_R, 140, 0 },
    { EP_MARK_HOLE, 1, 1, 0, 0, 0, 0, PAD_BUTTON_X, 0, 0 },
    { EP_MARK_HOLE, 4, 1, 0, -127, 0, 0, PAD_BUTTON_B, 0, 0 },
    { COURSE_REF_END },
};

static void ep_Setup(CourseCtx* c)
{
    float hmn_x = -c->side * (EP_START / 2);
    course_Place(c, hmn_x, hmn_x + c->side * EP_START, 0, 20.0F);
    memset(&ep, 0, sizeof(ep));
}

static void ep_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Aerial, shine, aerial, shine: on your shield");
    sprintf(g->line[n++], "it looks endless, but there is a hole between");
    sprintf(g->line[n++], "his landing and his shine.");
    sprintf(g->line[n++], "Hold shield and watch him land. Then:");
    sprintf(g->line[n++], "shine out of shield (jump, down+B), or roll");
    sprintf(g->line[n++], "or wavedash away.");
    sprintf(g->line[n++], "Too early or too late and you are hit out of");
    sprintf(g->line[n++], "it. The Gap option sets the size of the hole.");
    g->line_count = n;
    g->hide_timeline = 1;
}

/* One frame of the CPU's pressure. */
static void ep_Cpu(CourseCtx* c, int gap)
{
    FighterData* cd = c->cd;
    float dx = c->hd->phys.pos.X - cd->phys.pos.X;
    int falling = cd->phys.pos.Y < ep.last_y;
    int shining = fst_IsShine(cd->state_id);

    ep.last_y = cd->phys.pos.Y;
    if (shining) {
        if (++ep.shine == EP_SHINE_FRAMES) {
            cd->cpu.held |= PAD_BUTTON_X; /* jump out: the next hop */
        }
        return;
    }
    ep.shine = 0;
    if (cd->phys.air_state != 0) {
        ep.air++;
        ep.was_air = 1;
        ep.landed = 0;
        if (fabs(dx) > 6.0F) {
            cd->cpu.lstickX = dx > 0 ? 80 : -80; /* stay on top of them */
        }
        if (!ep.aerial && ep.air >= EP_AERIAL_AT) {
            cd->cpu.lstickX = 0;
            cd->cpu.held |= PAD_BUTTON_A;
            ep.aerial = 1;
        } else if (ep.aerial && !ep.cancel && falling &&
                   cd->phys.pos.Y < 8.0F)
        {
            cd->cpu.held |= PAD_TRIGGER_Z;
            ep.cancel = 1;
        }
        return;
    }
    ep.air = 0;
    ep.aerial = 0;
    ep.cancel = 0;
    if (cd->state_id != ASID_WAIT) {
        return; /* jump squat, landing lag */
    }
    if (!ep.was_air) {
        cd->cpu.held |= PAD_BUTTON_X; /* the first hop */
        return;
    }
    course_Mark(c, EP_MARK_HOLE);
    if (++ep.landed > gap) {
        cd->cpu.lstickY = -127;
        cd->cpu.held |= PAD_BUTTON_B;
    }
}

static void ep_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    int gap = course_IsDemo()
                  ? ep_gaps[1]
                  : ep_gaps[Options_Main[OPT_COMMON_COUNT + EP_OPT_GAP].val];
    int shielding = hd->state_id >= ASID_GUARDON &&
                    hd->state_id <= ASID_GUARDREFLECT;

    switch (c->phase) {
    case EP_WAIT_SHIELD:
        if (hd->state_id == ASID_GUARD && c->timer > 20) {
            course_Phase(c, EP_PRESSURE);
        } else if (hd->state_id != ASID_GUARD &&
                   hd->state_id != ASID_GUARDON)
        {
            c->timer = 0;
        }
        break;

    case EP_PRESSURE:
        ep_Cpu(c, gap);
        if (c->hmn_hit || nr_PlayerGrabbed(c)) {
            course_Result(c, 0, "Hit out of your shield\n"
                                "act in the hole, not before",
                          0, 0);
        } else if (hd->state_id == ASID_SHIELDBREAKFLY ||
                   hd->state_id == ASID_SHIELDBREAKFALL)
        {
            course_Result(c, 0, "Shield broken\ndo not wait that long", 0, 0);
        } else if (c->cpu_hit || fpr_CpuGrabbed(c)) {
            course_Result(c, 1, "Out: hit him in the hole", 0, 0);
        } else if (!shielding && nr_Dist(c) > EP_AWAY &&
                   hd->phys.air_state == 0)
        {
            course_Result(c, 1, "Out of the pressure", 0, 0);
        } else if (c->timer > 900) {
            course_Result(c, 0, "Still in shield", 0, 0);
        }
        break;
    }
}

static const CourseDrill Drill_DefEscapePressure = {
    .Setup = ep_Setup,
    .Think = ep_Think,
    .options = ep_options,
    .option_count = countof(ep_options),
    .help = { "Hold shield. Get out in the hole between his",
              "landing and his shine.",
              "D-Pad up: guide. D-Pad down: reset." },
    .reference = ep_reference,
    .live_marks = 1,
    .Guide = ep_Guide,
};

/* ---- fox-recovery-mixup ---------------------------------------------------
 *
 * The player starts in the air off the left ledge with a double jump.
 * Marth waits by the ledge. He forward smashes a player who comes in at
 * stage height, after his reaction time, and a player on the ledge as the
 * ledge intangibility runs out (as in fox-ledgedash-attack). Standing on
 * the stage unhit is the goal.
 */

enum { RM_OPT_REACTION };

#define RM_PLAYER_OUT 46.0F
#define RM_PLAYER_UP 8.0F
#define RM_CPU_IN 14.0F
#define RM_SWING_X 34.0F /* he swings at a player this close, at his height */
#define RM_SAFE 30

static EventOption rm_options[] = {
    [RM_OPT_REACTION] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(la_opt_reaction),
        .val = 1,
        .name = "CPU Reaction",
        .desc = { "Frames the CPU takes to swing once you are",
                  "in reach." },
        .values = la_opt_reaction,
    },
};

static struct {
    Vec3 ledge;
    int seen;  /* frames the player has been in reach, high */
    int safe;
    int frame;
    int swung; /* frames since his last swing, 0 = ready */
} rm;

static void rm_Setup(CourseCtx* c)
{
    memset(&rm, 0, sizeof(rm));
    if (!course_LedgePos(&rm.ledge)) {
        return;
    }
    c->side = 1.0F;
    c->toward = -1.0F;
    course_PlaceInAir(Fighter_GetGObj(0), rm.ledge.X - RM_PLAYER_OUT,
                      rm.ledge.Y + RM_PLAYER_UP, 1.0F, 40.0F);
    course_PlaceCpu(c, rm.ledge.X + RM_CPU_IN, -1.0F, 20.0F);
}

static void rm_Guide(CourseCtx* c, CourseGuide* g)
{
    int n = 0;
    sprintf(g->line[n++], "Getting back is a guessing game you can tilt.");
    sprintf(g->line[n++], "Marth swings at what he sees coming.");
    sprintf(g->line[n++], "Illusion (side+B) straight at the stage: fast,");
    sprintf(g->line[n++], "  and the one he expects. Shorten it (B again)");
    sprintf(g->line[n++], "  to stop at the ledge.");
    sprintf(g->line[n++], "Fire Fox (up+B) from below to the ledge.");
    sprintf(g->line[n++], "From the ledge, the ledgedash.");
    sprintf(g->line[n++], "Mix them, and keep your double jump in hand.");
    g->line_count = n;
    g->hide_timeline = 1;
}

static void rm_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    FighterData* cd = c->cd;
    int react = la_reactions[Options_Main[OPT_COMMON_COUNT + RM_OPT_REACTION]
                                 .val];
    float dx = fabs(hd->phys.pos.X - cd->phys.pos.X);
    float dy = hd->phys.pos.Y - cd->phys.pos.Y;
    int on_ledge = lg_OnLedge(c->state);
    int in_reach = !on_ledge && dx < RM_SWING_X && dy > -6.0F && dy < 22.0F;

    rm.frame++;
    /* Marth */
    if (rm.swung > 0) {
        if (++rm.swung > 50) {
            rm.swung = 0;
        }
    } else if (on_ledge) {
        rm.seen = 0;
        /* once the player has hung for a moment: the intangibility
         * counter is not set yet while the ledge is being caught */
        if (c->state == ASID_CLIFFWAIT && c->state_frames > 4 &&
            lg_Intangible(c) <= LA_SMASH_LEAD)
        {
            cd->cpu.cstickX = hd->phys.pos.X < cd->phys.pos.X ? -127 : 127;
            rm.swung = 1;
        }
    } else if (in_reach) {
        if (++rm.seen >= react && hd->hurt.kind_game == 0) {
            cd->cpu.cstickX = hd->phys.pos.X < cd->phys.pos.X ? -127 : 127;
            rm.swung = 1;
            rm.seen = 0;
        }
    } else {
        rm.seen = 0;
    }

    if (hd->phys.air_state == 0 && hd->phys.pos.X > rm.ledge.X &&
        !hd->flags.hitstun)
    {
        rm.safe++;
    } else {
        rm.safe = 0;
    }
    if (df_PlayerDead(c)) {
        course_Result(c, 0, "Did not make it back", 0, 0);
    } else if (c->hmn_hit || nr_PlayerGrabbed(c)) {
        course_Result(c, 0, "Hit on the way in\nhe saw that one coming", 0,
                      0);
    } else if (c->cpu_hit || fpr_CpuGrabbed(c)) {
        course_Result(c, 1, "Back, and hit him!", 0, 0);
    } else if (rm.safe > RM_SAFE) {
        course_Measure(rm.frame, rm.frame);
        course_Result(c, 1, "Back on the stage\nafter %d frames", rm.frame,
                      0);
    } else if (rm.frame > 900) {
        course_Result(c, 0, "Out of time", 0, 0);
    }
}

static const CourseDrill Drill_DefRecovery = {
    .Setup = rm_Setup,
    .Think = rm_Think,
    .options = rm_options,
    .option_count = countof(rm_options),
    .help = { "Get back to the stage past Marth, who swings at",
              "what he sees coming.",
              "D-Pad up: guide. D-Pad down: reset." },
    .Guide = rm_Guide,
};
