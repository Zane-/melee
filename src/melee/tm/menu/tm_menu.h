#ifndef MELEE_TM_MENU_TM_MENU_H
#define MELEE_TM_MENU_TM_MENU_H

#include <Runtime/platform.h>

/**
 * @file
 * The build's main menu: large panels chosen with the stick, a line at the
 * bottom saying what the highlighted one does.
 *
 * It is a scene of its own, in the scene table's one empty slot (GS_UNK10;
 * `pointer` hooks in config/GALE01/tm_hooks/menu.txt), and the first state
 * of the menu mode (tm_css_MenuStates, src/melee/tm/css/tm_css.c). Nothing
 * is loaded from disc: panels are flat shapes drawn with GX, labels are the
 * game's own text.
 */

/// The menu mode's state ids (tm_css_MenuStates).
enum {
    TM_MENU_STATE_MAIN = 0,    ///< this menu
    TM_MENU_STATE_CREDITS = 1, ///< TM-CE's credits
    TM_MENU_STATE_VANILLA = 2  ///< the original menus (the event list)
};

/// @name Scene callbacks (`pointer` hooks on `scenes`)
/// @{
void tm_menu_SceneEnter(void* data);
void tm_menu_SceneFrame(void);
/// @}

#endif
