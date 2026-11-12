/*
 * MexTK-side helpers for src/melee/tm/addcodes/ (TM-CE Additional Codes).
 */
#include "events.h"
#include <stddef.h>

/* events.c */
EventDesc* GetEventDesc(int page, int event);
int GetPageNum(void);
int GetPageEventNum(int page);

/* Find the event whose file is `file` (e.g. "lab") in TM-CE's pages. */
int tmce_ac_FindEvent(const char* file, int* page, int* event)
{
    int p, e;
    for (p = 0; p <= GetPageNum(); p++) { /* GetPageNum = last index */
        for (e = 0; e <= GetPageEventNum(p); e++) { /* last index too */
            EventDesc* desc = GetEventDesc(p, e);
            if (desc != NULL && desc->eventFile != NULL &&
                strcmp(desc->eventFile, file) == 0)
            {
                *page = p;
                *event = e;
                return 1;
            }
        }
    }
    return 0;
}

/* TM-CE's selected event page (save data 0x1F29). */
void tmce_ac_SetEventPage(int page)
{
    stc_memcard->TM_EventPage = page;
}

/* Force Game Loop.asm: event_vars->flags & EventVarsFlag_ForceGameLoop. */
int tmce_ac_ForceGameLoop(void)
{
    return event_vars != NULL &&
           (event_vars->flags & EventVarsFlag_ForceGameLoop) != 0;
}
