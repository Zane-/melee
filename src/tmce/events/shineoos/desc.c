/*
 * Shine Out of Shield: EventDesc and scenario deck. Linked globally (not
 * part of the event unit) so the event page and match setup can see them.
 *
 * Only attacks that Fox's shine out of shield (frame 4: 3 frames of jump
 * squat, then the frame 1 shine) beats, spaced close enough for the shine's
 * 8-unit hitbox to reach after shield pushback. Advantages are from
 * `python tools/melee_data/query.py shield <cpu> <move> fox` (first active
 * frame for ground moves). Aerials are only -2..0 on shield in the best case
 * (L-cancelled, landing right after the hit), so they are scripted to hit
 * the shield early, well before landing, which is when shine OoS punishes
 * them. Distances and aerial frames are tuned with tools/test_shineoos.py,
 * whose test build shines on the frame-4 timing and checks that it hits.
 * Dropped: Peach down smash (-26, but its multi-hit pushback leaves Peach
 * ~28 units away even from point blank: out of shine range).
 */
#include "shineoos.h"

#define END { -1 }
#define TOWARD 127
#define AWAY (-127)

/* Grounded tilts and smashes: the Lab's CPU inputs (lab.h): stick at 80 for
 * tilts, C-stick for smashes. */
static const OosInput in_dtilt[] = { { 0, 1, 0, -80, 0, 0, PAD_BUTTON_A }, END };
static const OosInput in_utilt[] = { { 0, 1, 0, 80, 0, 0, PAD_BUTTON_A }, END };
static const OosInput in_fsmash[] = { { 0, 1, 0, 0, TOWARD, 0, 0 }, END };
/* Dash toward the player, dash attack. */
static const OosInput in_dash_attack[] = {
    { 0, 8, TOWARD, 0, 0, 0, 0 },
    { 8, 1, TOWARD, 0, 0, 0, PAD_BUTTON_A },
    END,
};

/* Short-hop aerials that hit the shield early. Frame 0 = jump input; the
 * jump squat and landing frames are from `query.py jump <cpu>`. No fast
 * fall, L-cancel pressed shortly before the estimated landing (shield
 * hitlag delays it, so the L-cancel may be missed: that only makes the
 * aerial more punishable). */
/* Marth: airborne frame 5, lands frame 41; fair hitbox from 4 frames after
 * the input. */
static const OosInput in_marth_fair[] = {
    { 0, 1, 0, 0, 0, 0, PAD_BUTTON_X },
    { 5, 30, TOWARD, 0, 0, 0, 0 },
    { 24, 1, TOWARD, 0, TOWARD, 0, 0 },
    { 38, 1, 0, 0, 0, 0, PAD_TRIGGER_R },
    END,
};
/* Falcon: airborne frame 5, lands frame 35; nair hits 7 frames after. */
static const OosInput in_falcon_nair[] = {
    { 0, 1, 0, 0, 0, 0, PAD_BUTTON_X },
    { 5, 30, TOWARD, 0, 0, 0, 0 },
    { 20, 1, TOWARD, 0, 0, 0, PAD_BUTTON_A },
    { 33, 1, 0, 0, 0, 0, PAD_TRIGGER_R },
    END,
};
/* Falco: airborne frame 6, lands frame 29; dair hits 5 frames after. */
static const OosInput in_falco_dair[] = {
    { 0, 1, 0, 0, 0, 0, PAD_BUTTON_X },
    { 6, 20, TOWARD, 0, 0, 0, 0 },
    { 14, 1, TOWARD, 0, 0, -127, 0 },
    { 27, 1, 0, 0, 0, 0, PAD_TRIGGER_R },
    END,
};
/* Jigglypuff, facing away: airborne frame 6, lands frame 39; bair (C-stick
 * away from the player = behind her) hits 6 frames after. */
static const OosInput in_puff_bair[] = {
    { 0, 1, 0, 0, 0, 0, PAD_BUTTON_X },
    { 6, 30, TOWARD, 0, 0, 0, 0 },
    { 22, 1, TOWARD, 0, AWAY, 0, 0 },
    { 36, 1, 0, 0, 0, 0, PAD_TRIGGER_R },
    END,
};

/*                                        distance inputs   timeout away adv */
static const OosScenario sc_marth_dtilt = { 6.0F, in_dtilt, 40, 0, -6 };
static const OosScenario sc_marth_fsmash = { 4.0F, in_fsmash, 40, 0, -27 };
static const OosScenario sc_marth_fair = { 26.0F, in_marth_fair, 60, 0, -4 };
static const OosScenario sc_sheik_utilt = { 6.0F, in_utilt, 40, 0, -15 };
static const OosScenario sc_sheik_dash_attack = { 19.0F, in_dash_attack, 60,
                                                  0, -23 };
static const OosScenario sc_falcon_dtilt = { 5.0F, in_dtilt, 40, 0, -17 };
static const OosScenario sc_falcon_nair = { 30.0F, in_falcon_nair, 60, 0, -4 };
static const OosScenario sc_peach_dtilt = { 5.0F, in_dtilt, 40, 0, -6 };
static const OosScenario sc_falco_dair = { 20.0F, in_falco_dair, 60, 0, -4 };
static const OosScenario sc_puff_bair = { 12.0F, in_puff_bair, 60, 1, -4 };

static const TmRotEntry entries[] = {
    { CKIND_MARTH, 0, &sc_marth_dtilt, "Marth - Down Tilt" },
    { CKIND_MARTH, 0, &sc_marth_fsmash, "Marth - Forward Smash" },
    { CKIND_MARTH, 0, &sc_marth_fair, "Marth - Fair (early)" },
    { CKIND_SHEIK, 0, &sc_sheik_utilt, "Sheik - Up Tilt" },
    { CKIND_SHEIK, 0, &sc_sheik_dash_attack, "Sheik - Dash Attack" },
    { CKIND_FALCON, 0, &sc_falcon_dtilt, "Falcon - Down Tilt" },
    { CKIND_FALCON, 0, &sc_falcon_nair, "Falcon - Nair (early)" },
    { CKIND_PEACH, 0, &sc_peach_dtilt, "Peach - Down Tilt" },
    { CKIND_FALCO, 0, &sc_falco_dair, "Falco - Dair (early)" },
    { CKIND_JIGGLYPUFF, 0, &sc_puff_bair, "Jigglypuff - Bair (early)" },
};

const TmRotDeck ShineOos_Deck = { entries, countof(entries) };

static EventMatchData ShineOos_MatchData = {
    .timer = MATCH_TIMER_HIDE,
    .matchType = MATCH_MATCHTYPE_TIME,
    .hideGo = true,
    .hideReady = true,
    .isCreateHUD = true,
    .timerRunOnPause = false,
    .isCheckForZRetry = false,
    .isShowScore = false,
    .isRunStockLogic = false,
    .isDisableHit = false,
    .useKOCounter = false,
    .timerSeconds = 0,
};

EventDesc ShineOos_Desc = {
    .eventName = "Shine Out of Shield\n",
    .eventDescription = "Shine attacks off your shield\nfrom a rotating cast of characters.\n",
    .eventFile = "shineoos",
    .jumpTableIndex = -1,
    .CSSType = SLCHRKIND_EVENT,
    .allowed_characters = { .hmn = CSSID_FOX | CSSID_FALCO, .cpu = -1 },
    .cpuKind = CKIND_MARTH,
    .stage = GRKINDEXT_FD,
    .disable_hazards = true,
    .force_sopo = false,
    .scoreType = SCORETYPE_KO,
    .callbackPriority = 3,
    .matchData = &ShineOos_MatchData,
    .rotation = &ShineOos_Deck,
};
