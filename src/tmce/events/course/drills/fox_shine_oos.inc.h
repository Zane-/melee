/*
 * fox-shine-oos: punish a move on shield with shine out of shield.
 * Spec: data/courses/fox.md (Punish 1). Included by ../event.c (see there for the `.inc.h` name).
 *
 * The CPU (a scenario of the Shine OoS deck: a character, an attack, a
 * spacing) attacks once the player holds shield. The player jumps out of
 * shield and shines on the first airborne frame; optionally follows up.
 *
 * Behaviour is that of src/tmce/events/shineoos/event.c, moved onto the
 * engine. Its scenario data (OosScenario in shineoos.h) is used as is.
 */
/* Path relative to event.c, which includes this file. */
#include "../shineoos/shineoos.h"

/* Fox and Falco: SpecialLwStart .. SpecialAirLwTurn (ftFox/forward.h,
 * ftFx_MS_SpecialLwStart = 0x168). */
#define SOOS_SHINE_FIRST 0x168
#define SOOS_SHINE_LAST 0x171
/* Jump squat (3 frames for Fox) then the frame 1 shine:
 * `query.py oos fox` -> "frame 4 Down B (aerial)". Falco's jump squat is 5
 * (frame 6); the verdict reports the frame either way. */
#define SOOS_PERFECT_FRAME 4
/* Frames after shieldstun ends in which the punish has to start. */
#define SOOS_PUNISH_TIMEOUT 60
#define SOOS_FOLLOWUP_TIMEOUT 90

enum {
    SOOS_WAIT_SHIELD,
    SOOS_ATTACK,
    SOOS_PUNISH,
    SOOS_FOLLOWUP,
};

enum { SOOS_OPT_SUCCESS, SOOS_OPT_DELAY, SOOS_OPT_PERCENT };
enum {
    SOOS_GOAL_SHINE,
    SOOS_GOAL_ANY_HIT,
    SOOS_GOAL_USMASH,
    SOOS_GOAL_WAVESHINE_USMASH,
};
enum { SOOS_DELAY_RANDOM, SOOS_DELAY_SHORT, SOOS_DELAY_LONG };

static const char* soos_opt_success[] = { "Shine Hits", "Shine + Any Hit",
                                          "Shine + Up Smash",
                                          "Waveshine Up Smash" };
static const char* soos_opt_delay[] = { "Random", "Short", "Long" };

static EventOption soos_options[] = {
    [SOOS_OPT_SUCCESS] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(soos_opt_success),
        .name = "Success",
        .desc = { "What counts as a success: the shine hitting,",
                  "or the shine and a follow-up." },
        .values = soos_opt_success,
    },
    [SOOS_OPT_DELAY] = {
        .kind = OPTKIND_STRING,
        .value_num = countof(soos_opt_delay),
        .name = "Attack Delay",
        .desc = { "How long the CPU waits after you shield." },
        .values = soos_opt_delay,
    },
    [SOOS_OPT_PERCENT] = {
        .kind = OPTKIND_INT,
        .value_num = 151,
        .val = 20,
        .name = "CPU Percent",
        .desc = { "The CPU's damage at the start of each attempt." },
        .format = "%d%%",
    },
};

static struct {
    int attack_frame; /* frames since the attack started */
    int delay;        /* frames to hold shield before the CPU attacks */
    int stun_end;     /* attack_frame when shieldstun ended, -1 = not yet */
    int shine_frame;  /* attack_frame when the shine started, -1 = none */
    int wavedash;     /* went through airdodge/landing after the shine */
    float distance;   /* fighters' distance when shieldstun ended */
} soos;

static EventOption* soos_Opt(int i)
{
    return &Options_Main[OPT_COMMON_COUNT + i];
}

static const OosScenario* soos_Scenario(CourseCtx* c)
{
    return c->entry->data;
}

static int soos_IsShine(FighterData* fd)
{
    return (fd->kind == FTKIND_FOX || fd->kind == FTKIND_FALCO) &&
           fd->state_id >= SOOS_SHINE_FIRST &&
           fd->state_id <= SOOS_SHINE_LAST;
}

/* Frame N out of shield: 1 = the first frame the player could act, so a
 * frame-perfect jump-cancelled shine is frame 4. Think sees each state
 * change on the frame after it happens, for both values, so the difference
 * is already that count (calibrated in the Shine OoS event with
 * tools/tmtest.py: X on the frame shieldstun ends, down-B 3 frames later). */
static int soos_OosFrame(void)
{
    return soos.shine_frame - soos.stun_end;
}

static void soos_Setup(CourseCtx* c)
{
    float hmn_x = -c->side * 10.0F;
    float cpu_x = hmn_x + c->side * soos_Scenario(c)->distance;

    course_Place(c, hmn_x, cpu_x, soos_Scenario(c)->face_away,
                 (float) soos_Opt(SOOS_OPT_PERCENT)->val);

    switch (soos_Opt(SOOS_OPT_DELAY)->val) {
    case SOOS_DELAY_SHORT:
        soos.delay = 10;
        break;
    case SOOS_DELAY_LONG:
        soos.delay = 40;
        break;
    default:
        soos.delay = 8 + HSD_Randi(40);
        break;
    }
    soos.attack_frame = 0;
    soos.stun_end = -1;
    soos.shine_frame = -1;
    soos.wavedash = 0;
    soos.distance = 0;
}

/* Fields every result of this drill reports (test builds). */
static void soos_Result(CourseCtx* c, int success, char* fmt, int a, int b)
{
    int oos = soos.shine_frame >= 0 && soos.stun_end >= 0 ? soos_OosFrame()
                                                           : -1;
    if (oos >= 0) {
        course_Measure(oos, SOOS_PERFECT_FRAME);
    }
    course_Report("shield_hit", c->phase >= SOOS_PUNISH);
    course_Report("stun_end", soos.stun_end);
    course_Report("shine", soos.shine_frame);
    course_Report("oos_frame", oos);
    course_ReportF("distance", soos.distance);
    course_Result(c, success, fmt, a, b);
}

static void soos_Think(CourseCtx* c)
{
    FighterData* hd = c->hd;
    FighterData* cd = c->cd;

    hd->shield.health = 60;

    if (c->phase >= SOOS_ATTACK) {
        course_Script(c, (const CourseInput*) soos_Scenario(c)->inputs,
                      soos.attack_frame);
        soos.attack_frame++;
    }

    switch (c->phase) {
    case SOOS_WAIT_SHIELD:
        if (hd->state_id == ASID_GUARD || hd->state_id == ASID_GUARDON) {
            if (c->timer >= soos.delay) {
                course_Phase(c, SOOS_ATTACK);
                soos.attack_frame = 0;
            }
        } else {
            c->timer = 0;
        }
        break;

    case SOOS_ATTACK:
        if (hd->state_id == ASID_GUARDSETOFF) {
            course_Phase(c, SOOS_PUNISH);
        } else if (c->hmn_hit) {
            soos_Result(c, 0, "Hit through your shield", 0, 0);
        } else if (c->timer > soos_Scenario(c)->attack_timeout) {
            course_Retry(c, "Attack missed\nresetting");
        }
        break;

    case SOOS_PUNISH:
        if (soos.stun_end < 0 && hd->state_id != ASID_GUARDSETOFF) {
            soos.stun_end = soos.attack_frame;
            soos.distance = fabs(cd->phys.pos.X - hd->phys.pos.X);
        }
        if (soos.shine_frame < 0 && soos_IsShine(hd)) {
            soos.shine_frame = soos.attack_frame;
        }
        if (c->hmn_hit) {
            soos_Result(c, 0, "Got hit", 0, 0);
        } else if (c->cpu_hit && soos_IsShine(hd)) {
            if (soos_Opt(SOOS_OPT_SUCCESS)->val == SOOS_GOAL_SHINE) {
                soos_Result(c, 1, "Shine OoS!\nframe %d", soos_OosFrame(),
                            0);
            } else {
                course_Phase(c, SOOS_FOLLOWUP);
                course_Message(MSGCOLOR_WHITE,
                               "Shine on frame %d\nfollow up!", 0,
                               soos_OosFrame(), 0);
            }
        } else if (c->cpu_hit) {
            soos_Result(c, 0, "Hit, but not with the shine", 0, 0);
        } else if (c->timer > SOOS_PUNISH_TIMEOUT) {
            if (soos.shine_frame >= 0) {
                soos_Result(c, 0, "Shine missed\nframe %d", soos_OosFrame(),
                            0);
            } else {
                soos_Result(c, 0, "No shine", 0, 0);
            }
        }
        break;

    case SOOS_FOLLOWUP: {
        int goal = soos_Opt(SOOS_OPT_SUCCESS)->val;
        if (hd->state_id == ASID_ESCAPEAIR ||
            hd->state_id == ASID_LANDINGFALLSPECIAL)
        {
            soos.wavedash = 1;
        }
        if (c->hmn_hit) {
            soos_Result(c, 0, "Got hit", 0, 0);
        } else if (c->cpu_hit && !soos_IsShine(hd)) {
            int usmash = hd->state_id == ASID_ATTACKHI4;
            if (goal == SOOS_GOAL_ANY_HIT ||
                (goal == SOOS_GOAL_USMASH && usmash) ||
                (goal == SOOS_GOAL_WAVESHINE_USMASH && usmash &&
                 soos.wavedash))
            {
                soos_Result(c, 1, "Punished!", 0, 0);
            } else if (goal == SOOS_GOAL_WAVESHINE_USMASH && usmash) {
                soos_Result(c, 0, "Up smash, but no waveshine", 0, 0);
            } else {
                soos_Result(c, 0, "Wrong follow-up", 0, 0);
            }
        } else if (c->timer > SOOS_FOLLOWUP_TIMEOUT) {
            soos_Result(c, 0, "No follow-up", 0, 0);
        }
        break;
    }
    }
}

static const CourseDrill Drill_FoxShineOos = {
    .Setup = soos_Setup,
    .Think = soos_Think,
    .options = soos_options,
    .option_count = countof(soos_options),
    .help = { "Hold shield. When the attack hits your shield, jump out",
              "of shield and shine on the first frame of the jump.",
              "D-Pad left/right: change scenario. D-Pad down: reset." },
};
