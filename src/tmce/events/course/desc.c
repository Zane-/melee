/*
 * Course event: its EventDesc and what is known about each drill before the
 * match. Linked globally (src/tmce/events/<name>/desc.c is glue in
 * tools/overlay_build.py). See course.h.
 */
#include "course.h"

/* src/tmce/events/shineoos/desc.c: the opponents and attacks of the Shine
 * OoS event, reused as the deck of fox-shine-oos. */
extern const TmRotDeck ShineOos_Deck;

/* ---- fox-whiff-punish: the attacks ----------------------------------------
 *
 * Reach, hit and recovery frames measured against a standing Fox in the
 * simulator sandbox and checked against data/framedata (2026-11-12):
 *   Marth forward smash: hits out to 34 units, hitbox frames 10-13, acts
 *     again on 48.
 *   Marth dash attack (8 frames of dash, then A): from 29 out to 58,
 *     hitbox 12-15 of the attack, interruptible from 40. (Marth down tilt
 *     was tried and dropped: 11 frames between its hitbox and its IASA
 *     are not a realistic whiff punish.)
 *   Sheik and Peach dash attack (8 frames of dash, then A): out to 46-47;
 *     hitbox 6-12 (Sheik) and 6-20 (Peach) of the attack, acts again on 36.
 * `reach` is a little inside the measured reach, so standing there is hit.
 */
#define WP_END { -1 }
static const CourseInput wp_fsmash[] = { { 0, 1, 0, 0, 127, 0, 0 }, WP_END };
static const CourseInput wp_dash_attack[] = {
    { 0, 9, 127, 0, 0, 0, 0 },
    { 8, 1, 127, 0, 0, 0, PAD_BUTTON_A },
    WP_END,
};

/* demo_back: when the demonstration starts back in, tuned in the simulator
 * so that it arrives after the hitbox and up smashes before `faf`. */
/*                                             reach  inputs  hit_end faf back */
static const WhiffScenario wp_marth_fsmash = { 31.0F, wp_fsmash, 13, 48, 3 };
static const WhiffScenario wp_marth_dash = { 50.0F, wp_dash_attack, 23, 48,
                                             9 };
static const WhiffScenario wp_sheik_dash = { 42.0F, wp_dash_attack, 20, 44,
                                             10 };
static const WhiffScenario wp_peach_dash = { 42.0F, wp_dash_attack, 28, 44,
                                             12 };

static const TmRotEntry wp_entries[] = {
    { CKIND_MARTH, 0, &wp_marth_fsmash, "Marth - Forward Smash" },
    { CKIND_MARTH, 0, &wp_marth_dash, "Marth - Dash Attack" },
    { CKIND_SHEIK, 0, &wp_sheik_dash, "Sheik - Dash Attack" },
    { CKIND_PEACH, 0, &wp_peach_dash, "Peach - Dash Attack" },
};

const TmRotDeck WhiffPunish_Deck = { wp_entries, countof(wp_entries) };

/* ---- jump-in approaches ---------------------------------------------------
 *
 * Frame 0 is the jump input. Measured against a standing Fox in the
 * simulator sandbox (2026-11-12); "lands" and "acts" are for the attack
 * missing. No L-cancel: the landing lag is the window being taught.
 *
 * Short hops, for fox-wavedash-back-punish (scripts as in the Shine OoS
 * deck, src/tmce/events/shineoos/desc.c, without its L-cancel):
 *   Falcon nair from 30: hits a Fox within 36 on frame 33; lands 35, acts 54.
 *   Falco dair from 20: within 22, frame 18-21; lands 30, acts 48.
 *   Marth fair from 26: within 31, frame 29; lands 42, acts 57.
 * Full hops, for fox-anti-air:
 *   Falcon nair from 47: hits on frame 51; lands 53-61.
 *   Falcon dair from 45: frame 51; lands 52-59.
 *   Jigglypuff fair from 60: frame 46; lands 56-62.
 *   Peach fair from 50: frame 52; lands 64-71.
 */
static const CourseInput ap_falcon_sh_nair[] = {
    { 0, 1, 0, 0, 0, 0, PAD_BUTTON_X },
    { 5, 30, 127, 0, 0, 0, 0 },
    { 20, 1, 127, 0, 0, 0, PAD_BUTTON_A },
    WP_END,
};
static const CourseInput ap_falco_sh_dair[] = {
    { 0, 1, 0, 0, 0, 0, PAD_BUTTON_X },
    { 6, 20, 127, 0, 0, 0, 0 },
    { 14, 1, 127, 0, 0, -127, 0 },
    WP_END,
};
static const CourseInput ap_marth_sh_fair[] = {
    { 0, 1, 0, 0, 0, 0, PAD_BUTTON_X },
    { 5, 30, 127, 0, 0, 0, 0 },
    { 24, 1, 127, 0, 127, 0, 0 },
    WP_END,
};
static const CourseInput ap_falcon_fh_nair[] = {
    { 0, 8, 0, 0, 0, 0, PAD_BUTTON_X },
    { 5, 45, 127, 0, 0, 0, 0 },
    { 38, 1, 127, 0, 0, 0, PAD_BUTTON_A },
    WP_END,
};
static const CourseInput ap_falcon_fh_dair[] = {
    { 0, 8, 0, 0, 0, 0, PAD_BUTTON_X },
    { 5, 45, 127, 0, 0, 0, 0 },
    { 36, 1, 127, 0, 0, -127, 0 },
    WP_END,
};
static const CourseInput ap_puff_fh_fair[] = {
    { 0, 8, 0, 0, 0, 0, PAD_BUTTON_X },
    { 6, 60, 127, 0, 0, 0, 0 },
    { 40, 1, 127, 0, 127, 0, 0 },
    WP_END,
};
static const CourseInput ap_peach_fh_fair[] = {
    { 0, 8, 0, 0, 0, 0, PAD_BUTTON_X },
    { 6, 60, 127, 0, 0, 0, 0 },
    { 34, 1, 127, 0, 127, 0, 0 },
    WP_END,
};

/* demo_out / demo_back tuned in the simulator: see the drills. */
/*                                       start inputs  lands acts back out */
static const WhiffScenario wb_falcon = { 30.0F, ap_falcon_sh_nair, 35, 54,
                                         30, 6 };
static const WhiffScenario wb_falco = { 20.0F, ap_falco_sh_dair, 30, 48, 22,
                                        3 };
static const WhiffScenario wb_marth = { 26.0F, ap_marth_sh_fair, 42, 57, 34,
                                        6 };
static const TmRotEntry wb_entries[] = {
    { CKIND_FALCON, 0, &wb_falcon, "Falcon - Nair" },
    { CKIND_FALCO, 0, &wb_falco, "Falco - Dair" },
    { CKIND_MARTH, 0, &wb_marth, "Marth - Fair" },
};
const TmRotDeck WavedashBack_Deck = { wb_entries, countof(wb_entries) };

static const WhiffScenario aa_falcon_nair = { 47.0F, ap_falcon_fh_nair, 61,
                                              80, 0, 40 };
static const WhiffScenario aa_falcon_dair = { 45.0F, ap_falcon_fh_dair, 59,
                                              83, 0, 40 };
static const WhiffScenario aa_puff_fair = { 60.0F, ap_puff_fh_fair, 62, 82, 0,
                                            35 };
static const WhiffScenario aa_peach_fair = { 50.0F, ap_peach_fh_fair, 71, 96,
                                             0, 41 };
static const TmRotEntry aa_entries[] = {
    { CKIND_FALCON, 0, &aa_falcon_nair, "Falcon - Full Hop Nair" },
    { CKIND_FALCON, 0, &aa_falcon_dair, "Falcon - Full Hop Dair" },
    { CKIND_JIGGLYPUFF, 0, &aa_puff_fair, "Jigglypuff - Fair" },
    { CKIND_PEACH, 0, &aa_peach_fair, "Peach - Fair" },
};
const TmRotDeck AntiAir_Deck = { aa_entries, countof(aa_entries) };

static const TmRotEntry cc_entries[] = {
    { CKIND_PEACH, 0, 0, "Peach - Crouching" },
    { CKIND_SAMUS, 0, 0, "Samus - Crouching" },
    { CKIND_MARTH, 0, 0, "Marth - Crouching" },
};
const TmRotDeck CrouchCancel_Deck = { cc_entries, countof(cc_entries) };

static const TmRotEntry floaty_entries[] = {
    { CKIND_MARTH, 0, 0, "Marth" },
    { CKIND_SHEIK, 0, 0, "Sheik" },
    { CKIND_PEACH, 0, 0, "Peach" },
    { CKIND_JIGGLYPUFF, 0, 0, "Jigglypuff" },
};
const TmRotDeck Floaty_Deck = { floaty_entries, countof(floaty_entries) };

static const TmRotEntry fastfaller_entries[] = {
    { CKIND_FALCO, 0, 0, "Falco" },
    { CKIND_FOX, 1, 0, "Fox" },
};
const TmRotDeck FastFaller_Deck = { fastfaller_entries,
                                    countof(fastfaller_entries) };

static const TmRotEntry killconfirm_entries[] = {
    { CKIND_MARTH, 0, 0, "Marth" },
    { CKIND_SHEIK, 0, 0, "Sheik" },
    { CKIND_JIGGLYPUFF, 0, 0, "Jigglypuff" },
};
const TmRotDeck KillConfirm_Deck = { killconfirm_entries,
                                     countof(killconfirm_entries) };

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
    [DRILL_FOX_OOS_CHOICE] = {
        .id = "fox-oos-choice",
        .name = "Out of Shield: Pick the Option",
        .goal = "Punish a shielded move with whatever reaches in time",
        .part = COURSE_PUNISH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_MARTH,
        .deck = &ShineOos_Deck,
    },
    [DRILL_FOX_WAVESHINE_USMASH] = {
        .id = "fox-waveshine-usmash",
        .name = "Waveshine to Up Smash",
        .goal = "Shine, wavedash after them, up smash before they act",
        .part = COURSE_PUNISH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_MARTH,
    },
    [DRILL_FOX_SHINE_KNOCKDOWN] = {
        .id = "fox-shine-knockdown",
        .name = "Shine Knockdown: Tech Chase",
        .goal = "Cover the tech or missed tech after a shine",
        .part = COURSE_PUNISH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_FALCO,
        .deck = &FastFaller_Deck,
    },
    [DRILL_FOX_UTHROW_UAIR] = {
        .id = "fox-uthrow-uair",
        .name = "Up Throw Up Air",
        .goal = "Up air them out of up throw before they jump away",
        .part = COURSE_PUNISH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_MARTH,
        .deck = &Floaty_Deck,
    },
    [DRILL_FOX_CHAINGRAB] = {
        .id = "fox-uthrow-chaingrab",
        .name = "Chain Grab Fastfallers",
        .goal = "Regrab Fox and Falco out of up throw",
        .part = COURSE_PUNISH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_FALCO,
        .deck = &FastFaller_Deck,
    },
    [DRILL_FOX_AERIAL_CONFIRM] = {
        .id = "fox-aerial-confirm",
        .name = "Aerial Hit Confirm",
        .goal = "Follow a landed aerial before they escape or grab",
        .part = COURSE_PUNISH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_MARTH,
    },
    [DRILL_FOX_SHIELD_PRESSURE] = {
        .id = "fox-shield-pressure",
        .name = "Shield Pressure",
        .goal = "Keep hitting a shield without a gap they can grab in",
        .part = COURSE_PUNISH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_MARTH,
    },
    [DRILL_FOX_KILL_CONFIRM] = {
        .id = "fox-kill-confirm",
        .name = "Kill Confirms",
        .goal = "Turn an opening into the stock at kill percent",
        .part = COURSE_PUNISH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_MARTH,
        .deck = &KillConfirm_Deck,
    },
    [DRILL_FOX_WHIFF_PUNISH] = {
        .id = "fox-whiff-punish",
        .name = "Whiff Punish",
        .goal = "Bait an attack, make it miss, punish its recovery",
        .part = COURSE_NEUTRAL,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_MARTH,
        .deck = &WhiffPunish_Deck,
    },
    [DRILL_FOX_WAVEDASH_BACK] = {
        .id = "fox-wavedash-back-punish",
        .name = "Wavedash Back Punish",
        .goal = "Wavedash out of an approach and punish its landing",
        .part = COURSE_NEUTRAL,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_FALCON,
        .deck = &WavedashBack_Deck,
    },
    [DRILL_FOX_SHIELD_THEN_PUNISH] = {
        .id = "fox-shield-then-punish",
        .name = "Shield, Then Punish",
        .goal = "Shield the jump-in and punish; do not shield the grab",
        .part = COURSE_NEUTRAL,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_FALCON,
        .deck = &WavedashBack_Deck,
    },
    [DRILL_FOX_APPROACH] = {
        .id = "fox-approach-nair-dair",
        .name = "Approach: Read the Stance",
        .goal = "Pick the move that beats what the opponent is doing",
        .part = COURSE_NEUTRAL,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_MARTH,
    },
    [DRILL_FOX_RUNNING_SHINE] = {
        .id = "fox-running-shine",
        .name = "Running Shine",
        .goal = "Catch a dash dance or a jump with shine",
        .part = COURSE_NEUTRAL,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_MARTH,
    },
    [DRILL_FOX_LASER_FORCING] = {
        .id = "fox-laser-forcing",
        .name = "Lasers Force the Approach",
        .goal = "Laser until they come, then punish the approach",
        .part = COURSE_NEUTRAL,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_MARTH,
    },
    [DRILL_FOX_ANTI_AIR] = {
        .id = "fox-anti-air",
        .name = "Anti-Air",
        .goal = "Beat a jump-in with up tilt, up smash or back air",
        .part = COURSE_NEUTRAL,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_FALCON,
        .deck = &AntiAir_Deck,
    },
    [DRILL_FOX_VS_CROUCH_CANCEL] = {
        .id = "fox-vs-crouch-cancel",
        .name = "Beat Crouch Cancel",
        .goal = "Open a crouching opponent with down air, shine or grab",
        .part = COURSE_NEUTRAL,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_PEACH,
        .deck = &CrouchCancel_Deck,
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
    [DRILL_TECH_SHIELD_DROP] = {
        .id = "universal-shield-drop",
        .name = "Shield Drop",
        .goal = "Fall through a platform straight out of shield",
        .part = COURSE_TECH,
        .characters = 0,
        .stage = GRKINDEXT_BATTLE,
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
    [DRILL_FOX_SHINE_GRAB] = {
        .id = "fox-shine-grab",
        .name = "Shine-Grab",
        .goal = "Shine a shield, jump-cancel, and grab it",
        .part = COURSE_TECH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_MARTH,
    },
    [DRILL_FOX_NAIR_SHINE] = {
        .id = "fox-shffl-nair-shine",
        .name = "Aerial into Shine",
        .goal = "SHFFL neutral air on shield, shine as you land",
        .part = COURSE_TECH,
        .characters = CSSID_FOX,
        .stage = GRKINDEXT_FD,
        .cpu_kind = CKIND_MARTH,
    },
    [DRILL_TECH_LEDGEDASH] = {
        .id = "universal-ledgedash",
        .name = "Ledgedash",
        .goal = "Onto the stage from the ledge, still intangible",
        .part = COURSE_TECH,
        .characters = 0,
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
    [DRILL_FOX_LEDGE_STALL] = {
        .id = "fox-ledge-stall",
        .name = "Fire Fox Ledge Stall",
        .goal = "Drop and Fire Fox back to the ledge",
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
