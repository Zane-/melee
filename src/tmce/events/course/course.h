#ifndef TMCE_EVENTS_COURSE_H
#define TMCE_EVENTS_COURSE_H

/*
 * Character courses: one event unit ("course") that runs any drill.
 * Design: docs/ai/training-courses.md. Curricula: data/courses/.
 *
 * A drill is two halves with the same index (enum CourseDrillId):
 *
 *  - CourseDrillInfo in desc.c: what has to be known before the match
 *    loads (name, part, player characters, stage, opponent deck). desc.c is
 *    linked globally; the hub and match setup read it.
 *  - CourseDrill in event.c (drills/<name>.inc.h, included there): the
 *    callbacks that run the drill. An event unit's symbols are local, so
 *    the engine and every drill are one translation unit.
 *
 * The engine owns the attempt loop, resets, scenario choice, CPU scripts,
 * statistics, messages, the options menu and the test report. A drill
 * places the fighters for an attempt and decides success or failure.
 */
#include "events.h"
#include "rotation/tm_rotation.h"

enum CoursePart {
    COURSE_TECH,
    COURSE_NEUTRAL,
    COURSE_PUNISH,
    COURSE_DEFENSE,
    COURSE_PART_COUNT,
};

enum CourseDrillId {
    DRILL_FOX_SHINE_OOS,
    DRILL_TECH_SHORT_HOP,
    DRILL_TECH_L_CANCEL,
    DRILL_TECH_SHFFL,
    DRILL_TECH_WAVEDASH,
    DRILL_TECH_DASH_DANCE,
    DRILL_TECH_JC_GRAB,
    DRILL_TECH_SHIELD_DROP,
    DRILL_FOX_WAVESHINE,
    DRILL_FOX_SHINE_GRAB,
    DRILL_FOX_NAIR_SHINE,
    DRILL_TECH_LEDGEDASH,
    DRILL_FOX_JC_SHINE,
    DRILL_FOX_MULTISHINE,
    DRILL_FOX_SHDL,
    DRILL_FOX_LEDGE_STALL,
    DRILL_FOX_ILLUSION_SHORTEN,
    DRILL_FOX_OOS_CHOICE,
    DRILL_FOX_WAVESHINE_USMASH,
    DRILL_FOX_SHINE_KNOCKDOWN,
    DRILL_FOX_UTHROW_UAIR,
    DRILL_FOX_CHAINGRAB,
    DRILL_FOX_AERIAL_CONFIRM,
    DRILL_FOX_SHIELD_PRESSURE,
    DRILL_FOX_KILL_CONFIRM,
    DRILL_FOX_WHIFF_PUNISH,
    DRILL_FOX_WAVEDASH_BACK,
    DRILL_FOX_SHIELD_THEN_PUNISH,
    DRILL_FOX_APPROACH,
    DRILL_FOX_RUNNING_SHINE,
    DRILL_FOX_LASER_FORCING,
    DRILL_FOX_ANTI_AIR,
    DRILL_FOX_VS_CROUCH_CANCEL,
    DRILL_DEF_TECH,
    DRILL_DEF_ASDI_DOWN,
    DRILL_DEF_DI_SURVIVAL,
    DRILL_DEF_TECH_CHASE,
    DRILL_DEF_COMBO_SHINE,
    DRILL_COUNT,
};

/// Known before the match (desc.c).
typedef struct CourseDrillInfo {
    const char* id;   ///< same as in data/courses/, e.g. "fox-shine-oos"
    const char* name; ///< menu title
    const char* goal; ///< one line, for the hub
    u8 part;          ///< CoursePart
    int characters;   ///< CSSID_* mask of player characters, 0 = any
    s16 stage;        ///< GRKINDEXT_*
    s8 cpu_kind;      ///< first opponent (CKIND_*), -1 = no CPU
    const TmRotDeck* deck; ///< opponent scenarios, NULL = single scenario
} CourseDrillInfo;

extern const CourseDrillInfo Course_Drills[DRILL_COUNT];
extern EventDesc Course_Desc;

/// Per-drill totals for this session, kept by the engine and shown in the
/// hub. (Not saved: see "Open decisions" in docs/ai/training-courses.md.)
typedef struct CourseStats {
    u16 attempts;
    u16 successes;
    u16 best_streak;
} CourseStats;
extern CourseStats Course_Stats[DRILL_COUNT];

/// Hub state that outlives the character select scene: the open section
/// and row, and whether to reopen the hub when the scene comes back (set
/// when a drill exits to it).
extern int Course_HubPart;
extern int Course_HubCursor;
extern int Course_HubReturn;
/// The character and costume the hub was last opened for (CKIND_*). The
/// event's character select does not keep the pick when the scene comes
/// back, so the hub does.
extern int Course_HubCkind;
extern int Course_HubColor;
/// Set by the hub when it starts a free-practice event (the Lab): that
/// event's own character select opens next, and leaving it or its match
/// comes back to the hub.
extern int Course_FromHub;
extern int Course_ReloadCss;

/// Where the event mode asks which state follows (src/melee/tm/tmce.h).
enum CourseRouteAt {
    COURSE_AT_MATCH_END, ///< an event match ended (not a retry)
    COURSE_AT_CSS_BACK,  ///< B on an event's character select
    COURSE_AT_CSS_START, ///< an event's character select was confirmed
};

/// The drill the next match runs. Set with Course_Select before the match
/// loads (the hub; tests): it also points Course_Desc at the drill's
/// characters, stage and deck, which match setup reads.
extern int Course_Current;
void Course_Select(int drill);

/// One scripted pad state for the CPU, held for `hold` frames (0 = 1) from
/// `frame` of the script. Stick and C-stick X are relative to the player:
/// positive is toward them. A list ends with frame -1. Same layout as the
/// Shine OoS event's OosInput, whose scenario data the first drill reuses.
typedef struct CourseInput {
    s16 frame;
    u8 hold;
    s8 lx, ly;
    s8 cx, cy;
    u32 buttons; ///< PAD_BUTTON_* | PAD_TRIGGER_*
} CourseInput;

/// A scenario of a whiff-punish drill: an attack the CPU throws once the
/// player has been inside its reach for its reaction time.
typedef struct WhiffScenario {
    float reach;              ///< the attack hits a standing player this near
    const CourseInput* inputs; ///< the attack; frame 0 = when the CPU commits
    s16 hit_end;              ///< script frame its last hitbox is gone after
    s16 faf;                  ///< script frame the CPU can act again
    s16 demo_back;            ///< script frame the demonstration goes back in
    s16 demo_out;             ///< script frame of its first move (approaches)
} WhiffScenario;

extern const TmRotDeck WhiffPunish_Deck;
/// Jump-in approaches, same scenario type: `reach` is the start distance,
/// `hit_end` the landing.
extern const TmRotDeck WavedashBack_Deck;
extern const TmRotDeck AntiAir_Deck;
/// Opponents that crouch cancel (no scenario data).
extern const TmRotDeck CrouchCancel_Deck;
/// Opponents by how they fall (no scenario data).
extern const TmRotDeck Floaty_Deck;
extern const TmRotDeck FastFaller_Deck;
extern const TmRotDeck KillConfirm_Deck;

#endif
