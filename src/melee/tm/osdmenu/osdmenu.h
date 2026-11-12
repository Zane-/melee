#ifndef MELEE_TM_OSDMENU_OSDMENU_H
#define MELEE_TM_OSDMENU_OSDMENU_H

#include <Runtime/platform.h>

#include <sysdolphin/baselib/forward.h>

/**
 * @file
 * TM-CE's OSD toggle menu: the rules menu's random stage select screen
 * (mn/mnstagesw.c) reused as a list of on-screen displays. Port of
 * ASM/training-mode/Onscreen Display/Toggle UI/. Hooks are in
 * config/GALE01/tm_hooks/osdmenu.txt.
 *
 * The screen is in OSD mode while mn_804A04F0.entering_menu is
 * #TM_OSDMENU_FROM_RULES (L on the VS rules menu) or #TM_OSDMENU_FROM_EVENTS
 * (L on the event select screen, src/melee/tm/ess/ess.c). Vanilla sets
 * entering_menu to 0 or 1, so values of 2 and up are free for this.
 */

#define TM_OSDMENU_FROM_RULES 2
#define TM_OSDMENU_FROM_EVENTS 3

/// @name src/tmce/osdmenu_bridge.c
/// @{
u32* tmce_osdmenu_Enabled(void);
u8* tmce_osdmenu_Position(void);
/// @}

/// @name Hook targets
/// @{
void tm_osdmenu_Think(HSD_GObj* gobj);
void tm_osdmenu_Proc(HSD_GObj* gobj);
bool tm_osdmenu_GetToggle(u16 id);
void tm_osdmenu_SetToggle(u8 id, u8 on);
u32 tm_osdmenu_RulesButtons(u32 slot);
HSD_GObj* tm_osdmenu_CreateRules(int mode);
void tm_osdmenu_RulesRemoveText(HSD_Text* text);
/// @}

#endif
