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
    /* Tech drills, in the course's order (the hub lists by this table). */
    [DRILL_TECH_SHORT_HOP] = {
        .id = "universal-short-hop",
        .name = "Short Hop",
        .goal = "Leave the ground with a short hop every time",
        .part = COURSE_TECH,
        .characters = 0,
        .stage = GRKINDEXT_FD,
        .cpu_kind = -1,
    },
    [DRILL_TECH_L_CANCEL] = {
        .id = "universal-l-cancel",
        .name = "L-Cancel",
        .goal = "Halve the landing lag of an aerial attack",
        .part = COURSE_TECH,
        .characters = 0,
        .stage = GRKINDEXT_FD,
        .cpu_kind = -1,
    },
    [DRILL_TECH_SHFFL] = {
        .id = "universal-shffl",
        .name = "SHFFL",
        .goal = "Short hop, aerial, fast fall, L-cancel in one motion",
        .part = COURSE_TECH,
        .characters = 0,
        .stage = GRKINDEXT_FD,
        .cpu_kind = -1,
    },
    [DRILL_TECH_WAVEDASH] = {
        .id = "universal-wavedash",
        .name = "Wavedash",
        .goal = "Air dodge into the ground on your first airborne frame",
        .part = COURSE_TECH,
        .characters = 0,
        .stage = GRKINDEXT_FD,
        .cpu_kind = -1,
    },
    [DRILL_TECH_DASH_DANCE] = {
        .id = "universal-dash-dance",
        .name = "Dash Dance",
        .goal = "Dash back and forth without ever running",
        .part = COURSE_TECH,
        .characters = 0,
        .stage = GRKINDEXT_FD,
        .cpu_kind = -1,
    },
    [DRILL_TECH_JC_GRAB] = {
        .id = "universal-jc-grab",
        .name = "Jump-Cancelled Grab",
        .goal = "Standing grab out of a run",
        .part = COURSE_TECH,
        .characters = 0,
        .stage = GRKINDEXT_FD,
        .cpu_kind = -1,
    },
    [DRILL_FOX_WAVESHINE] = {
        .id = "fox-waveshine",
        .name = "Waveshine",
        .goal = "Shine, jump, wavedash with no wasted frames",
        .part = COURSE_TECH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = -1,
    },
    [DRILL_FOX_JC_SHINE] = {
        .id = "fox-jc-shine",
        .name = "Frame-Perfect JC Shine",
        .goal = "Jump out of shine on the first possible frame",
        .part = COURSE_TECH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = -1,
    },
    [DRILL_FOX_MULTISHINE] = {
        .id = "fox-multishine",
        .name = "Multishine",
        .goal = "Consecutive shines without leaving the ground",
        .part = COURSE_TECH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = -1,
    },
    [DRILL_FOX_SHDL] = {
        .id = "fox-shdl",
        .name = "Short Hop Double Laser",
        .goal = "Two lasers out of every short hop",
        .part = COURSE_TECH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = -1,
    },
    [DRILL_FOX_ILLUSION_SHORTEN] = {
        .id = "fox-illusion-shorten",
        .name = "Shortened Illusion",
        .goal = "Stop Fox Illusion short with a second B press",
        .part = COURSE_TECH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = -1,
    },
};

int Course_Current = DRILL_FOX_SHINE_OOS;
CourseStats Course_Stats[DRILL_COUNT];
int Course_HubPart = COURSE_PUNISH;
int Course_HubCursor;
int Course_HubReturn;
int Course_HubCkind = -1;
int Course_HubColor;
int Course_FromHub;
int Course_ReloadCss;

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

/* gm/gmevent.h: the event index the event mode runs. */
void gm_801BEB74(u8 event);
/* src/tmce/addcodes_bridge.c */
int tmce_ac_FindEvent(const char* file, int* page, int* event);
void tmce_ac_SetEventPage(int page);

static void BackToCourse(void)
{
    int page, event;
    if (tmce_ac_FindEvent("course", &page, &event)) {
        tmce_ac_SetEventPage(page);
        gm_801BEB74(event);
    }
    Course_FromHub = 0;
    Course_HubReturn = 1;
}

/* For native code (src/melee/tm/tmce.h, the event mode's state callbacks in
 * src/melee/tm/css/tm_css.c): called where TM-CE would go to the main menu
 * or on to the match. Returns 1 when the character select should open
 * (again) instead, which is how every way out of a drill, and out of a
 * free-practice event started from the hub, leads back to the hub. */
int tmce_CourseRoute(int at, int page, int event)
{
    int is_course = GetEventDesc(page, event) == &Course_Desc;
    switch (at) {
    case COURSE_AT_MATCH_END:
        if (is_course) {
            Course_HubReturn = 1;
            return 1;
        }
        if (Course_FromHub) {
            BackToCourse();
            return 1;
        }
        return 0;
    case COURSE_AT_CSS_BACK:
        if (!is_course && Course_FromHub) {
            BackToCourse();
            return 1;
        }
        return 0;
    case COURSE_AT_CSS_START:
        if (Course_ReloadCss) {
            Course_ReloadCss = 0;
            return 1;
        }
        return 0;
    }
    return 0;
}
