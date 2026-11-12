/*
 * Test runner (src/melee/tm/test/tmtest.h), TM-CE side. Test builds only:
 * the test_ prefix ties this file to the "test" area (TM_TEST=1).
 */
#include "events.h"
#include "tmce_registry.h"
#include "test/tmtest.h"

/* src/tmce/events/course/desc.c */
void Course_Select(int drill);
#include <stddef.h>

/* Set option `index` of event `file`'s main menu (Event_Menu, the 4th
 * evFunction export). TM-CE menus are static, so this holds until the
 * event reads them. */
int tmce_test_SetOption(const char* file, int index, int value)
{
    int i;
    if (index == TM_TEST_OPT_DRILL && strcmp(file, "course") == 0) {
        /* Not a menu option: which drill the course event runs. Has to be
         * known before the match loads (src/tmce/events/course/course.h). */
        Course_Select(value);
        return 1;
    }
    for (i = 0; i < tmce_module_count; i++) {
        const TmceModule* m = &tmce_modules[i];
        EventMenu** menu_ptr;
        if (strcmp(m->name, file) != 0 || m->count < 4 || m->funcs[3] == NULL)
        {
            continue;
        }
        menu_ptr = (EventMenu**) m->funcs[3];
        if (*menu_ptr == NULL || index < 0 || index >= (*menu_ptr)->option_num)
        {
            return 0;
        }
        (*menu_ptr)->options[index].val = value;
        if ((*menu_ptr)->options[index].name == NULL) {
            /* Marks the slot as set for events that fill their menu in
             * at init (the course engine's MergeOption). */
            (*menu_ptr)->options[index].name = "";
        }
        return 1;
    }
    return 0;
}
