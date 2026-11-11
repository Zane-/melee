#ifndef MELEE_TM_EVENT_H
#define MELEE_TM_EVENT_H

#include <Runtime/platform.h>

#include "tm_menu.h"

#include <melee/gm/forward.h>
#include <sysdolphin/baselib/forward.h>

/**
 * @file
 * Event framework. Port of the lifecycle half of TM-CE `src/events.c`
 * (`EventLoad`, `EventUpdate`, `Hazards_Disable`) and of `EventDesc`.
 *
 * An event is a `const` #TmEventDesc compiled into the overlay. TM-CE loads
 * each event from its own `.dat` and resolves four entry points at runtime;
 * here they are plain function pointers in the descriptor.
 *
 * Events are chosen on the event select screen (tm_ess.c) and then run
 * through vanilla Training mode's CSS -> SSS -> match flow
 * (#tm_Hook_TrainingMatchEnter).
 *
 * Not ported yet: the player half of `EventInit` (forced characters, CPU
 * setup, forced stage), the HUD drawing helpers, messages, tips, savestates
 * and OSDs.
 */

/// Size of the zeroed per-event data block (the event GObj's user data).
/// Like TM-CE's `EVENT_DATASIZE`; this block is what savestates will cover.
#define TM_EVENT_DATASIZE 512

/// File on the disc holding TM-CE's menu art (its `dats/eventMenu.dat`),
/// with the public symbol `eventMenu` (#TmMenuAssets).
#define TM_MENU_ASSET_FILE "TmMenu.dat"
#define TM_MENU_ASSET_SYMBOL "eventMenu"

/// Values of #TmEventMatchData::timer.
enum {
    TM_TIMER_FROZEN = 0,
    TM_TIMER_HIDE = 1,
    TM_TIMER_COUNTDOWN = 2,
    TM_TIMER_COUNTUP = 3
};

/// Values of #TmEventMatchData::match_type.
enum { TM_MATCHTYPE_TIME = 0, TM_MATCHTYPE_STOCK = 1, TM_MATCHTYPE_COIN = 2 };

/// Match settings of an event. Same fields as TM-CE's `EventMatchData`.
typedef struct TmEventMatchData {
    u8 timer;      ///< TM_TIMER_*
    u8 match_type; ///< TM_MATCHTYPE_*
    u8 hide_go;
    u8 hide_ready;
    u8 create_hud; ///< show stocks, percents and timer
    u8 timer_run_on_pause;
    u8 check_for_z_retry;
    u8 show_score;
    u8 run_stock_logic;
    u8 disable_hit;
    u32 timer_seconds;
} TmEventMatchData;

typedef struct TmEventDesc {
    const char* name;
    /// Shown on the event select screen; lines separated by '\n'.
    const char* description;
    u8 disable_hazards;   ///< removes stage hazards (#tmEvent_DisableHazards)
    u8 callback_priority; ///< GObj proc priority of #think
    /// Runs once at match start, after the event GObj and menu exist.
    void (*init)(HSD_GObj* event_gobj);
    /// Runs every engine frame before GObj procs, even while paused.
    void (*update)(void);
    /// GObj proc of the event GObj; runs with the game simulation.
    void (*think)(HSD_GObj* event_gobj);
    /// Root pause menu, or NULL for no menu.
    const TmMenuDesc* menu;
    /// Match settings, or NULL to keep vanilla Training mode's.
    const TmEventMatchData* match_data;
} TmEventDesc;

/// A page of the event select screen.
typedef struct TmEventPage {
    const char* name;
    int event_num;
    const TmEventDesc* const* events;
} TmEventPage;

/// Pages in display order. Append events within a page; do not reorder.
extern const TmEventPage tm_event_pages[];
extern const int tm_event_page_num;

/// Descriptor of the event selected in #tm_persist, or NULL if the stored
/// selection is out of range.
const TmEventDesc* tmEvent_GetSelected(void);

/// Zeroed #TM_EVENT_DATASIZE block of the running event.
void* tmEvent_GetData(void);

/// Removes hazards from the current stage. Port of TM-CE `Hazards_Disable`.
void tmEvent_DisableHazards(void);

/// Menu `on_select` handler that ends the match and leaves the event.
/// Port of the `Event_Exit` every TM-CE event defines.
void tmEvent_Exit(HSD_GObj* menu_gobj);

/// Match-start callback (`StartMeleeRules::on_match_start`): creates the
/// event GObj, the pause menu and installs the per-frame update.
void tmEvent_Load(void);

/// Applies an event's #TmEventMatchData to a match's start data. Port of
/// the rules half of TM-CE `EventInit`.
void tmEvent_ApplyMatchData(struct StartMeleeData* data,
                            const TmEventDesc* desc);

/// `pointer` hook target replacing the on_enter of vanilla Training mode's
/// match state (`gm_801B1F70`). Calls it and, when an event was chosen on
/// the event select screen, routes the match into the event framework.
/// Plain Training mode is left untouched otherwise.
void tm_Hook_TrainingMatchEnter(GameModeState* state);

#endif
