#include "tm.h"

#include "tmce.h"

#include <melee/gm/gm_1601.h>
#include <melee/gm/gm_16A2.h>
#include <melee/gm/gm_1A3F.h>
#include <melee/gm/gmevent.h>
#include <melee/gm/gmmain_lib.h>
#include <melee/gm/gmvs.h>
#include <melee/gm/types.h>
#include <melee/lb/lbarchive.h>

/// Vanilla `onEnterVs` in gm/gmevent.c, the event mode's match state
/// on_enter. Static there and its name is not unique, so it is named in
/// config/GALE01/tm_symbols.txt.
void gmEvent_onEnterVs(GameModeState* state);

/// Statics in gm/gmevent.c (unique names, resolved by the overlay linker).
extern struct gm_804D6900_t** gm_804D6900[2];
void fn_801BBFE8(void);

/// Same as the static inline in gm/gmevent.c.
static inline struct EventData* gm_GetEventData(void)
{
    return &gmMainLib_804D3EE0->vs.unk_530;
}

/**
 * Replaces the event mode's match state on_enter (vanilla `onEnterVs`),
 * through a `pointer` hook on gm_Mode_Event_States[1].
 *
 * Port of the C-event half of TM-CE's "Custom Event Code - Rewrite.asm"
 * (onEnterVs+0x3B8): vanilla sets up the match rules from GmEvent.dat for
 * the selected event index; for a TM-CE event with a C file, TM-CE then
 * calls EventInit for the players, stage and rules, and skips the vanilla
 * per-event player setup up to the last two calls (onEnterVs+0x9C8).
 *
 * The 15 legacy assembly-only TM-CE events (no event file) are not ported
 * yet; they get vanilla's setup for the same event index.
 */
void tm_Hook_EventEnterVs(GameModeState* arg0)
{
    struct EventData* ev = gm_GetEventData();
    StartMeleeData* md;
    u8 level = ev->unk_535;
    struct gm_804D6900_t** levels;
    int page;

    if (!tmce_IsLoaded()) {
        gmEvent_onEnterVs(arg0);
        return;
    }
    page = tmce_GetEventPage();
    if (GetEventFile(page, level) == NULL) {
        gmEvent_onEnterVs(arg0);
        return;
    }

    /* Vanilla onEnterVs up to +0x3B8. */
    md = gm_GetGameModeStateEnterData(arg0);
    lbArchive_LoadSymbols("GmEvent.dat", &gm_804D6900,
                          "sqEventInitDataLevelTbl", 0);
    levels = gm_804D6900[0];
    gm_SetupRulesDefaults(&md->rules);
    md->rules.match_kind = levels[level]->evinit->x0_0;
    md->rules.x0_3 = levels[level]->evinit->x0_3;
    md->rules.timer_enabled = levels[level]->evinit->x0_6;
    md->rules.timer_counts_up = levels[level]->evinit->x0_7;
    md->rules.x1_0 = 1;
    md->rules.x1_1 = 0;
    md->rules.x1_2 = 0;
    md->rules.x1_3 = 0;
    md->rules.timer_shows_hours = 0;
    md->rules.friendly_fire = levels[level]->evinit->x1_1;
    md->rules.x2_2 = 0;
    md->rules.single_button = 0;
    md->rules.disable_pausing = 0;
    md->rules.x2_5 = levels[level]->evinit->x1_2;
    md->rules.x3_1 = 1;
    md->rules.x3_2 = 1;
    md->rules.x3_3 = 1;
    md->rules.x3_4 = 1;
    md->rules.x3_5 = 1;
    md->rules.x3_7 = 0;
    md->rules.x4_2 = 0;
    md->rules.x4_3 = 1;
    md->rules.x4_4 = 0;
    md->rules.x4_6 = 0;
    md->rules.x4_7 = 0;
    md->rules.x5_0 = 1;
    md->rules.x5_1 = 0;
    md->rules.x5_2 = levels[level]->evinit->x1_3;
    md->rules.x5_3 = levels[level]->evinit->x1_4;
    md->rules.x7 = 0;
    md->rules.is_teams = levels[level]->evinit->is_teams;
    md->rules.x9 = 0;
    md->rules.xA = 0;
    md->rules.item_freq = levels[level]->evinit->item_freq;
    md->rules.sd_penalty = levels[level]->evinit->sd_penalty;
    md->rules.xD = 0x6E;
    md->rules.stkind = levels[level]->evinit->stkind;
    md->rules.time_limit = levels[level]->evinit->time_limit;
    md->rules.x14 = 0;
    md->rules.x18 = 0;
    md->rules.x20 = levels[level]->evinit->x10;
    md->rules.it_kind = levels[level]->evinit->x18;
    md->rules.x30 = levels[level]->evinit->x1C;
    md->rules.game_speed = levels[level]->evinit->game_speed;
    md->rules.on_match_start = fn_801BBFE8;
    if (md->rules.timer_counts_up & 1) {
        ev->xB_0 = 1;
    }
    if (levels[level]->evinit->x1_0) {
        ev->xB_6 = 1;
    }
    if (levels[level]->evinit->unk24 != 1.0F) {
        ev->x1C = levels[level]->evinit->unk24;
    }
    if (levels[level]->kind == 2) {
        u16 stage;
        ev->xB_4 = 1;
        stage = levels[level]->evstage_table->stage[ev->x20];
        md->rules.stkind = stage;
        ev->x48 = stage;
        if (ev->x20 > 0) {
            md->rules.x1_2 = 1;
            md->rules.x1_3 = 1;
            md->rules.time_limit = ev->x2C;
        }
        gm_8016A92C(&md->rules);
    }

    /* TM-CE: players, stage and rules from the event's EventDesc. */
    EventInit(page, level, md);

    /* Vanilla onEnterVs from +0x9C8. */
    gm_LoadRumbleEnabled(md);
    gm_80168F88();
}
