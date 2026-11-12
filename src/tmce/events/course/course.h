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

#endif
