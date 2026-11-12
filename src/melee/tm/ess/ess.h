#ifndef MELEE_TM_ESS_ESS_H
#define MELEE_TM_ESS_ESS_H

#include <Runtime/platform.h>

#include <sysdolphin/baselib/forward.h>

#include <melee/mn/mnevent.h>

/**
 * @file
 * TM-CE's event select screen (ESS), ported from the assembly under
 * ../TrainingMode/ASM/training-mode/Custom Events/Event Select Screen/ and
 * Custom Events/Unlock All Events/. Wired in config/GALE01/tm_hooks/ess.txt.
 *
 * The vanilla Event Match screen (mn/mnevent.c) stays; the functions TM-CE
 * injects into are replaced by edited copies (`function` hooks). Terms:
 * vanilla MnEventData::page is the cursor row (0-8), ::first_event the
 * scroll offset; the selected event is their sum. "Page" below is TM-CE's
 * event page (tabs switched with L/R on the D-pad/stick).
 */

/// @name TM-CE fields in the vanilla save data (MexTK memcard.h), as
/// offsets from the block gmMainLib_804D3EE0 points to.
/// @{
#define TMCE_CARD_EVENT_SCORES 0x1A70 ///< s32 per event, all pages
#define TMCE_CARD_EVENT_PAGE 0x1F29   ///< u8 TM_EventPage
/// @}

/// @name TM-CE events.c (linked in; see docs/ai/tmce-native.md)
/// @{
char* GetPageName(int page);
char* GetEventName(int page, int event);
char* GetEventDescription(int page, int event);
int GetPageEventNum(int page); ///< index of the page's last event
int GetPageNum(void);          ///< index of the last page
u8 GetScoreType(int page, int event);
int GetPageEventOffset(int page);
char* GetTMVersLong(void);
/// @}

/// @name Hook targets
/// @{
s32 tm_Ess_MaxScroll(void);
void tm_Ess_DrawRow(s32 idx, s32 event_id);
void tm_Ess_DrawDescription(HSD_GObj* gobj, s32 idx);
void tm_Ess_Think(HSD_GObj* gobj);
void tm_Ess_LeaveA(HSD_GObj* gobj);
void tm_Ess_LeaveB(HSD_GObj* gobj);
void tm_Ess_InitData(MnEventData* data, s32 event_idx);
void tm_Ess_Create(s32 event_idx);
s32 tm_Ess_GetScore(s32 event);
void tm_Ess_SetScore(s32 event, s32 score);
bool tm_Ess_GetScoreType(u8 event);
bool tm_Ess_MainMenuLangUS(void);
/// @}

#endif
