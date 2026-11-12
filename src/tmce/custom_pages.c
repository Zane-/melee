/*
 * Event page for events written for this build (patch 0005 appends it to
 * TM-CE's EventPages). Each event lives in src/tmce/events/<name>/: desc.c
 * (its EventDesc, linked globally) and event.c (the event unit, listed in
 * src/tmce/units.txt). See the add-training-event skill.
 */
#include "events.h"

extern EventDesc ShineOos_Desc;
extern EventDesc Course_Desc; /* events/course: the course drill engine */

static EventDesc* Custom_Events[] = {
    &ShineOos_Desc,
    &Course_Desc,
};

EventPage Custom_Page = {
    .name = "Custom Drills",
    .eventNum = countof(Custom_Events),
    .events = Custom_Events,
};
