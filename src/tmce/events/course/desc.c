/*
 * Course event: its EventDesc and what is known about each drill before the
 * match. Linked globally (src/tmce/events/<name>/desc.c is glue in
 * tools/overlay_build.py). See course.h.
 */
#include "course.h"

/* src/tmce/events/shineoos/desc.c: the opponents and attacks of the Shine
 * OoS event, reused as the deck of fox-shine-oos. */
extern const TmRotDeck ShineOos_Deck;

const CourseDrillInfo Course_Drills[DRILL_COUNT] = {
    [DRILL_FOX_SHINE_OOS] = {
        .id = "fox-shine-oos",
        .name = "Shine Out of Shield",
        .goal = "Punish a shielded move with a frame 4 shine",
        .part = COURSE_PUNISH,
        .characters = CSSID_FOX | CSSID_FALCO,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_MARTH,
        .deck = &ShineOos_Deck,
    },
};

int Course_Current = DRILL_FOX_SHINE_OOS;
CourseStats Course_Stats[DRILL_COUNT];
int Course_HubPart = COURSE_PUNISH;
int Course_HubCursor;
int Course_HubReturn;
int Course_HubCkind = -1;
int Course_HubColor;

static EventMatchData Course_MatchData = {
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

/* The fields that depend on the drill hold drill 0's values and are
 * rewritten by Course_Select. */
EventDesc Course_Desc = {
    .eventName = "Character Course\n",
    .eventDescription = "Pick your character, then train it:\nTech, Neutral, Punish, Defense.\n",
    .eventFile = "course",
    .jumpTableIndex = -1,
    /* the hub: a menu in the character select scene (hub_css.c) */
    .eventCSSFile = "TM/hubCSS.dat",
    .CSSType = SLCHRKIND_EVENT,
    /* Every character can be picked: the character comes first, and the
     * hub then lists the drills that character has. */
    .allowed_characters = { .hmn = -1, .cpu = -1 },
    .cpuKind = CKIND_MARTH,
    .stage = GRKINDEXT_FD,
    .disable_hazards = true,
    .force_sopo = false,
    .scoreType = SCORETYPE_KO,
    .callbackPriority = 3,
    .matchData = &Course_MatchData,
    .rotation = &ShineOos_Deck,
};

void Course_Select(int drill)
{
    const CourseDrillInfo* d;
    if (drill < 0 || drill >= DRILL_COUNT) {
        return;
    }
    d = &Course_Drills[drill];
    Course_Current = drill;
    Course_Desc.cpuKind = d->cpu_kind;
    Course_Desc.stage = d->stage;
    Course_Desc.rotation = d->deck;
}

/* For native code (src/melee/tm/tmce.h): the event match's exit routing. */
int tmce_CourseHubReturn(void)
{
    return Course_HubReturn;
}
