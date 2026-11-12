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
    .eventName = "Course Drill\n",
    .eventDescription = "A drill of the character course.\n",
    .eventFile = "course",
    .jumpTableIndex = -1,
    .CSSType = SLCHRKIND_EVENT,
    .allowed_characters = { .hmn = CSSID_FOX | CSSID_FALCO, .cpu = -1 },
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
    Course_Desc.allowed_characters.hmn = d->characters != 0 ? d->characters
                                                            : -1;
    Course_Desc.cpuKind = d->cpu_kind;
    Course_Desc.stage = d->stage;
    Course_Desc.rotation = d->deck;
}
