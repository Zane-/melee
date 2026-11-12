#ifndef MELEE_TM_TMCE_H
#define MELEE_TM_TMCE_H

#include <Runtime/platform.h>

/**
 * @file
 * TM-CE functions callable from native (decomp-header) code.
 *
 * TM-CE's own C (../TrainingMode/src) is compiled against MexTK headers and
 * linked into the same overlay (see docs/ai/tmce-native.md). Its types do not
 * exist on this side, so pointers to them are passed as void*.
 */

/// @name src/tmce/boot.c
/// @{
void tmce_Boot(void);
int tmce_IsLoaded(void);
int tmce_GetEventPage(void);
/// @}

/// @name TM-CE events.c (tmFunction table entries)
/// @{
void OnSceneChange(void);
void OnStartMelee(void);
/// MatchInit* in MexTK terms; StartMeleeData* here.
void EventInit(int page, int eventID, void* match_data);
char* GetEventFile(int page, int event);
char* GetCSSFile(int page, int event);
/// @}

#endif
