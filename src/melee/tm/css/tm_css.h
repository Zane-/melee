#ifndef MELEE_TM_CSS_TM_CSS_H
#define MELEE_TM_CSS_TM_CSS_H

#include <Runtime/platform.h>

#include <melee/gm/forward.h>
#include <melee/gm/types.h> // GameModeState is used as an array element
#include <sysdolphin/baselib/forward.h>

/**
 * @file
 * TM-CE event character / stage select flow (area `css`, see
 * docs/ai/tmce-native.md). Replaces ../TrainingMode/ASM/training-mode/
 * Custom Events/{CSS and SSS, Custom Event Preload Behavior,
 * A+B to Reset Event} and Hooks/OnCSSLoad.asm. Hooks are in
 * config/GALE01/tm_hooks/css.txt.
 */

/// @name TM-CE events.c (MexTK side; pointers to its types as void*)
/// @{
char* GetEventName(int page, int event);
char* GetCSSFile(int page, int event);
u8 GetCSSType(int page, int event);
u8 GetIsSelectStage(int page, int event);
s8 GetCPUFighter(int page, int event);
s16 GetStage(int page, int event);
/// Returns AllowedCharacters* ({ int hmn; int cpu; }, CSSID bit masks,
/// -1 = any). Note the argument order.
void* GetEventCharList(int eventID, int pageID);
/// @}

/// m-ex MEX_LoadRelArchive, reimplemented in src/tmce/mex_runtime.c.
/// Returns HSD_Archive*.
void* MEX_LoadRelArchive(char* file, void* functions, char* symbol);

/// @name Hook targets (tm_css.c, tm_css_screen.c)
/// @{
/// Event mode states (CSS, match, SSS), installed by a `pointer` hook.
extern GameModeState tm_css_EventStates[];
/// Main menu states (menu, credits), installed by a `pointer` hook.
extern GameModeState tm_css_MenuStates[];
void tm_css_EventModeLoad(void);
void tm_css_MenuModeLoad(void);
void tm_css_JObjAnimAll(HSD_JObj* jobj);
void tm_css_GObjObject(HSD_GObj* gobj, u8 kind, void* obj);
void tm_css_UpdateRulesText(void);
void tm_css_8025EE8C(u8 idx);
/// @}

#endif
