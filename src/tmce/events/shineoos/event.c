/*
 * Shine Out of Shield training.
 *
 * The CPU (a different character per scenario, see desc.c and
 * src/melee/tm/rotation/tm_rotation.h) attacks once you hold shield. Shine
 * out of shield and hit it; optionally follow up (any hit, up smash, or
 * waveshine into up smash).
 *
 * Controls in the match: D-pad left/right = previous/next scenario,
 * D-pad down = reset now. Pause for the options.
 */
#include "shineoos.h"
#include <stddef.h>

/* Fox and Falco: SpecialLwStart .. SpecialAirLwTurn (ftFox/forward.h). */
#define SHINE_FIRST 0x168
#define SHINE_LAST 0x171
#define MSG_KIND 0x5348 /* any unique id; replaces our previous message */
/* Player 1's message area. TM-CE looks the queue up as a player slot, so
 * MSGQUEUE_GENERAL (6) asserts in Player_GetPtrForSlot. */
#define MSG_QUEUE 0

void Event_Exit(GOBJ* menu);
static void OnScenarioChange(GOBJ* menu, int value);

enum {
    OPT_SCENARIO,
    OPT_SWITCH,
    OPT_SUCCESS,
    OPT_SIDE,
    OPT_DELAY,
    OPT_PERCENT,
    OPT_RESET_DELAY,
    OPT_HELP,
    OPT_EXIT,
};

enum { SWITCH_EVERY, SWITCH_ON_SUCCESS, SWITCH_MANUAL };
enum { GOAL_SHINE, GOAL_ANY_HIT, GOAL_USMASH, GOAL_WAVESHINE_USMASH };
enum { SIDE_RANDOM, SIDE_LEFT, SIDE_RIGHT };
enum { DELAY_RANDOM, DELAY_SHORT, DELAY_LONG };

#define MAX_SCENARIOS 32
static const char* scenario_names[MAX_SCENARIOS + 1] = { "Random" };

static const char* opt_switch[] = { "Every Attempt", "On Success",
                                    "Manual (D-Pad)" };
static const char* opt_success[] = { "Shine Hits", "Shine + Any Hit",
                                     "Shine + Up Smash",
                                     "Waveshine Up Smash" };
static const char* opt_side[] = { "Random", "Left", "Right" };
static const char* opt_delay[] = { "Random", "Short", "Long" };
static const char* opt_reset_delay[] = { "Fast", "Normal", "Slow" };
static const int reset_delay_frames[] = { 20, 45, 90 };

static EventOption Options_Main[] = {
    {
        .kind = OPTKIND_STRING,
        .value_num = 1, /* set in Event_Init from the deck */
        .name = "Scenario",
        .desc = { "Practice one attack, or a random mix.",
                  "D-Pad left/right cycles in the match." },
        .values = scenario_names,
        .OnChange = OnScenarioChange,
    },
    {
        .kind = OPTKIND_STRING,
        .value_num = countof(opt_switch),
        .name = "Switch Scenario",
        .desc = { "When a random mix moves on to the next attack." },
        .values = opt_switch,
    },
    {
        .kind = OPTKIND_STRING,
        .value_num = countof(opt_success),
        .name = "Success",
        .desc = { "What counts as a success: the shine hitting,",
                  "or the shine and a follow-up." },
        .values = opt_success,
    },
    {
        .kind = OPTKIND_STRING,
        .value_num = countof(opt_side),
        .name = "CPU Side",
        .desc = { "Which side the CPU attacks from." },
        .values = opt_side,
    },
    {
        .kind = OPTKIND_STRING,
        .value_num = countof(opt_delay),
        .name = "Attack Delay",
        .desc = { "How long the CPU waits after you shield." },
        .values = opt_delay,
    },
    {
        .kind = OPTKIND_INT,
        .value_num = 151,
        .val = 20,
        .name = "CPU Percent",
        .desc = { "The CPU's damage at the start of each attempt." },
        .format = "%d%%",
    },
    {
        .kind = OPTKIND_STRING,
        .value_num = countof(opt_reset_delay),
        .val = 1,
        .name = "Reset Delay",
        .desc = { "How long the result shows before the next attempt." },
        .values = opt_reset_delay,
    },
    {
        .kind = OPTKIND_INFO,
        .name = "HELP",
        .desc = { "Hold shield. When the attack hits your shield, jump out",
                  "of shield and shine on the first frame of the jump.",
                  "D-Pad left/right: change scenario. D-Pad down: reset." },
    },
    {
        .kind = OPTKIND_FUNC,
        .name = "Exit",
        .desc = { "Return to the Event Select Screen." },
        .OnSelect = Event_Exit,
    },
};

static EventMenu Menu_Main = {
    .name = "Shine Out of Shield",
    .option_num = countof(Options_Main),
    .options = Options_Main,
};

EventMenu* Event_Menu = &Menu_Main;

enum Phase {
    PHASE_WAIT_SHIELD,
    PHASE_ATTACK,
    PHASE_PUNISH,
    PHASE_FOLLOWUP,
    PHASE_RESULT,
};

typedef struct Stats {
    u16 attempts;
    u16 successes;
} Stats;

static struct {
    int phase;
    int scenario;      /* deck index, -1 before the first reset */
    int last_success;
    int timer;         /* frames in the current phase */
    int attack_frame;  /* frames since the attack started */
    int delay;         /* frames to wait in shield before attacking */
    float toward;      /* +1/-1: the player's direction from the CPU */
    int stun_end;      /* attack_frame when shieldstun ended, -1 = not yet */
    int shine_frame;   /* attack_frame when the shine started, -1 = none */
    int wavedash;      /* went through airdodge/landing after the shine */
    float hmn_percent;
    float cpu_percent;
    float stun_distance; /* fighters' distance when shieldstun ended (tests) */
    Stats stats[MAX_SCENARIOS];
} ev;


static int IsShine(FighterData* fd)
{
    return (fd->kind == FTKIND_FOX || fd->kind == FTKIND_FALCO) &&
           fd->state_id >= SHINE_FIRST && fd->state_id <= SHINE_LAST;
}

static const OosScenario* Scenario(void)
{
    return ShineOos_Deck.entries[ev.scenario].data;
}

static void Message(int color, char* fmt, const char* a, int b, int c)
{
    event_vars->Message_Display(MSG_KIND, MSG_QUEUE, color, fmt, a,
                                b, c);
}

/* From powershield.c: put a fighter on Final Destination's main floor. */
static void PutOnGround(GOBJ* ft, float x)
{
    FighterData* ft_data = ft->userdata;
    Vec3 pos = { x, 0, 0 };

    ft_data->coll_data.ground_index = 1;
    ft_data->phys.pos = pos;
    ft_data->coll_data.topN_Curr = pos;
    ft_data->coll_data.topN_CurrCorrect = pos;
    ft_data->coll_data.topN_Prev = pos;
    ft_data->coll_data.topN_Proj = pos;
    ft_data->coll_data.coll_test = *stc_colltest;

    JOBJ* jobj = ft->hsd_object;
    jobj->trans = pos;
    JOBJ_SetMtxDirtySub(jobj);
    Fighter_SetPosition(ft_data->ply, ft_data->flags.ms, &ft_data->phys.pos);

    EnvironmentCollision_WaitLanding(ft);
    Fighter_SetGrounded(ft_data);
}

static void ResetFighter(GOBJ* ft, float x, float facing, float percent)
{
    FighterData* fd = ft->userdata;
    fd->facing_direction = facing;
    fd->phys.self_vel.X = 0;
    fd->phys.self_vel.Y = 0;
    fd->phys.anim_vel.X = 0;
    fd->phys.anim_vel.Y = 0;
    PutOnGround(ft, x);
    Fighter_EnterWait(ft);
    fd->dmg.percent = percent;
    Fighter_SetHUDDamage(fd->ply, (u16) percent);
    Fighter_UpdateCameraBox(ft);
}

static int PickScenario(void)
{
    int fixed = Options_Main[OPT_SCENARIO].val;
    if (fixed > 0 && tm_rot_IsUsable(fixed - 1)) {
        return fixed - 1;
    }
    if (ev.scenario < 0) {
        return tm_rot_Next(-1);
    }
    switch (Options_Main[OPT_SWITCH].val) {
    case SWITCH_ON_SUCCESS:
        return ev.last_success ? tm_rot_Next(ev.scenario) : ev.scenario;
    case SWITCH_MANUAL:
        return ev.scenario;
    default:
        return tm_rot_Next(ev.scenario);
    }
}

static void Reset(void)
{
    int idx = PickScenario();
    const TmRotEntry* entry;
    int side;

    if (idx < 0) {
        Message(MSGCOLOR_RED, "No scenarios loaded", 0, 0, 0);
        ev.phase = PHASE_RESULT;
        ev.timer = 600;
        return;
    }
    ev.scenario = idx;
    entry = &ShineOos_Deck.entries[idx];
    if (tm_rot_SetCpu(1, entry->ckind, entry->color) < 0) {
        Message(MSGCOLOR_RED, "Could not load\n%s", entry->name, 0, 0);
    }

    side = Options_Main[OPT_SIDE].val;
    if (side == SIDE_RANDOM) {
        side = HSD_Randi(2) ? SIDE_LEFT : SIDE_RIGHT;
    }
    /* `s`: the side the CPU is on. */
    float s = side == SIDE_LEFT ? -1.0F : 1.0F;
    float hmn_x = -s * 10.0F;
    float cpu_x = hmn_x + s * Scenario()->distance;
    ResetFighter(Fighter_GetGObj(0), hmn_x, s, 0);
    ResetFighter(Fighter_GetGObj(1), cpu_x, Scenario()->face_away ? s : -s,
                 (float) Options_Main[OPT_PERCENT].val);
    Match_CorrectCamera();

    switch (Options_Main[OPT_DELAY].val) {
    case DELAY_SHORT:
        ev.delay = 10;
        break;
    case DELAY_LONG:
        ev.delay = 40;
        break;
    default:
        ev.delay = 8 + HSD_Randi(40);
        break;
    }
    ev.phase = PHASE_WAIT_SHIELD;
    ev.timer = 0;
    ev.attack_frame = 0;
    ev.toward = -s;
    ev.stun_end = -1;
    ev.shine_frame = -1;
    ev.wavedash = 0;
    Message(MSGCOLOR_WHITE, "%s\n%d / %d", entry->name,
            ev.stats[idx].successes, ev.stats[idx].attempts);
}

static int OosFrame(void);

#ifdef TM_TEST
/* The message up to its first line break, for a JSON string. */
static char* Reason(char* fmt)
{
    static char buf[48];
    int i;
    for (i = 0; fmt[i] != '\0' && fmt[i] != '\n' && i < 47; i++) {
        buf[i] = fmt[i] == '"' ? '\'' : fmt[i];
    }
    buf[i] = '\0';
    return buf;
}
#endif

static void Result(int success, char* fmt, int a, int b)
{
    Stats* st = &ev.stats[ev.scenario];
    st->attempts++;
    if (success) {
        st->successes++;
    }
    ev.last_success = success;
#ifdef TM_TEST
    /* Test builds: one JSON result line (tools/tmtest.py). */
    OSReport("TMTEST {\"result\":\"%s\",\"scenario\":\"%s\","
             "\"cpu\":%d,\"shield_hit\":%d,\"stun_end\":%d,"
             "\"shine\":%d,\"oos_frame\":%d,\"distance\":%.1f,"
             "\"why\":\"%s\"}\n",
             success ? "success" : "fail",
             ShineOos_Deck.entries[ev.scenario].name,
             ShineOos_Deck.entries[ev.scenario].ckind,
             ev.phase >= PHASE_PUNISH, ev.stun_end, ev.shine_frame,
             ev.shine_frame >= 0 && ev.stun_end >= 0 ? OosFrame() : -1,
             ev.stun_distance, Reason(fmt));
#endif
    event_vars->Message_Display(MSG_KIND, MSG_QUEUE,
                                success ? MSGCOLOR_GREEN : MSGCOLOR_RED, fmt,
                                a, b);
    ev.phase = PHASE_RESULT;
    ev.timer = reset_delay_frames[Options_Main[OPT_RESET_DELAY].val];
}

static void ApplyInputs(FighterData* cpu)
{
    const OosInput* in = Scenario()->inputs;
    int t = ev.attack_frame;
    for (; in->frame >= 0; in++) {
        int hold = in->hold ? in->hold : 1;
        if (t < in->frame || t >= in->frame + hold) {
            continue;
        }
        cpu->cpu.lstickX = (s8) (in->lx * ev.toward);
        cpu->cpu.lstickY = in->ly;
        cpu->cpu.cstickX = (s8) (in->cx * ev.toward);
        cpu->cpu.cstickY = in->cy;
        cpu->cpu.held |= in->buttons;
    }
}

/* Frame N out of shield: 1 = the first frame you could act, so a
 * frame-perfect jump-cancel shine is frame 4. Calibrated with
 * tools/tmtest.py: X on the frame shieldstun ends, down-B 3 frames later,
 * gives shine_frame - stun_end = 4 (this think sees each state change on
 * the frame after it happens, for both). */
static int OosFrame(void)
{
    return ev.shine_frame - ev.stun_end;
}

void Event_Init(GOBJ* gobj)
{
    int i, n = ShineOos_Deck.count;
    if (n > MAX_SCENARIOS) {
        n = MAX_SCENARIOS;
    }
    for (i = 0; i < n; i++) {
        scenario_names[i + 1] = ShineOos_Deck.entries[i].name;
    }
    Options_Main[OPT_SCENARIO].value_num = n + 1;
    memset(&ev, 0, sizeof(ev));
    ev.scenario = -1;
}

void Event_Think(GOBJ* event)
{
    GOBJ* hmn = Fighter_GetGObj(0);
    GOBJ* cpu = Fighter_GetGObj(1);
    if (hmn == NULL || cpu == NULL) {
        return;
    }
    FighterData* hd = hmn->userdata;
    FighterData* cd = cpu->userdata;

    if (event_vars->game_timer == 1) {
        Reset();
        return;
    }

    hd->shield.health = 60;
    cd->cpu.ai = 15; /* no CPU logic; the script drives it */
    Fighter_ZeroCPUInputs(cd);

    /* D-pad: cycle scenario / reset. */
    if (hd->input.down & (HSD_BUTTON_DPAD_LEFT | HSD_BUTTON_DPAD_RIGHT)) {
        int dir = (hd->input.down & HSD_BUTTON_DPAD_RIGHT) ? 1 : -1;
        int n = ShineOos_Deck.count, i;
        int idx = ev.scenario;
        for (i = 0; i < n; i++) {
            idx = (idx + dir + n) % n;
            if (tm_rot_IsUsable(idx)) {
                break;
            }
        }
        if (Options_Main[OPT_SCENARIO].val > 0) {
            Options_Main[OPT_SCENARIO].val = idx + 1;
        }
        ev.scenario = idx;
        ev.last_success = 0;
        Options_Main[OPT_SWITCH].val =
            Options_Main[OPT_SCENARIO].val > 0 ? Options_Main[OPT_SWITCH].val
                                               : SWITCH_MANUAL;
        Reset();
        return;
    }
    if (hd->input.down & HSD_BUTTON_DPAD_DOWN) {
        ev.last_success = 0;
        Reset();
        return;
    }

    float hmn_percent = hd->dmg.percent;
    float cpu_percent = cd->dmg.percent;
    int hmn_hit = hmn_percent > ev.hmn_percent;
    int cpu_hit = cpu_percent > ev.cpu_percent;
    ev.hmn_percent = hmn_percent;
    ev.cpu_percent = cpu_percent;

    if (ev.phase >= PHASE_ATTACK && ev.phase < PHASE_RESULT) {
        ApplyInputs(cd);
        ev.attack_frame++;
    }
    if (ev.phase != PHASE_RESULT) {
        ev.timer++; /* PHASE_RESULT counts down instead */
    }

    switch (ev.phase) {
    case PHASE_WAIT_SHIELD:
        if (hd->state_id == ASID_GUARD || hd->state_id == ASID_GUARDON) {
            if (ev.timer >= ev.delay) {
                ev.phase = PHASE_ATTACK;
                ev.timer = 0;
                ev.attack_frame = 0;
            }
        } else {
            ev.timer = 0;
        }
        break;

    case PHASE_ATTACK:
        if (hd->state_id == ASID_GUARDSETOFF) {
            ev.phase = PHASE_PUNISH;
            ev.timer = 0;
        } else if (hmn_hit) {
            Result(0, "Hit through your shield", 0, 0);
        } else if (ev.timer > Scenario()->attack_timeout) {
            /* The attack missed the shield: not the player's fault. */
            Message(MSGCOLOR_YELLOW, "Attack missed\nresetting", 0, 0, 0);
#ifdef TM_TEST
            OSReport("TMTEST {\"result\":\"attack_missed\","
                     "\"scenario\":\"%s\"}\n",
                     ShineOos_Deck.entries[ev.scenario].name);
#endif
            ev.phase = PHASE_RESULT;
            ev.timer = 30;
        }
        break;

    case PHASE_PUNISH:
        if (ev.stun_end < 0 && hd->state_id != ASID_GUARDSETOFF) {
            ev.stun_end = ev.attack_frame;
            ev.stun_distance = fabs(cd->phys.pos.X - hd->phys.pos.X);
        }
        if (ev.shine_frame < 0 && IsShine(hd)) {
            ev.shine_frame = ev.attack_frame;
        }
        if (hmn_hit) {
            Result(0, "Got hit", 0, 0);
        } else if (cpu_hit && IsShine(hd)) {
            if (Options_Main[OPT_SUCCESS].val == GOAL_SHINE) {
                Result(1, "Shine OoS!\nframe %d", OosFrame(), 0);
            } else {
                ev.phase = PHASE_FOLLOWUP;
                ev.timer = 0;
                Message(MSGCOLOR_WHITE, "Shine on frame %d\nfollow up!",
                        0, OosFrame(), 0);
            }
        } else if (cpu_hit) {
            Result(0, "Hit, but not with the shine", 0, 0);
        } else if (ev.timer > 60) {
            if (ev.shine_frame >= 0) {
                Result(0, "Shine missed\nframe %d", OosFrame(), 0);
            } else {
                Result(0, "No shine", 0, 0);
            }
        }
        break;

    case PHASE_FOLLOWUP: {
        int goal = Options_Main[OPT_SUCCESS].val;
        if (hd->state_id == ASID_ESCAPEAIR ||
            hd->state_id == ASID_LANDINGFALLSPECIAL)
        {
            ev.wavedash = 1;
        }
        if (hmn_hit) {
            Result(0, "Got hit", 0, 0);
        } else if (cpu_hit && !IsShine(hd)) {
            int usmash = hd->state_id == ASID_ATTACKHI4;
            if (goal == GOAL_ANY_HIT || (goal == GOAL_USMASH && usmash) ||
                (goal == GOAL_WAVESHINE_USMASH && usmash && ev.wavedash))
            {
                Result(1, "Punished!", 0, 0);
            } else if (goal == GOAL_WAVESHINE_USMASH && usmash) {
                Result(0, "Up smash, but no waveshine", 0, 0);
            } else {
                Result(0, "Wrong follow-up", 0, 0);
            }
        } else if (ev.timer > 90) {
            Result(0, "No follow-up", 0, 0);
        }
        break;
    }

    case PHASE_RESULT:
        if (--ev.timer <= 0) {
            Reset();
        }
        break;
    }
}

static void OnScenarioChange(GOBJ* menu, int value)
{
    ev.last_success = 0;
}

void Event_Exit(GOBJ* menu)
{
    stc_match->state = 3;
    Match_EndVS();
}
