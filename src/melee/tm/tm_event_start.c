#include "tm.h"

#include "tmce.h"
#include "legacy/legacy.h"
#include "rotation/tm_rotation.h"

#include <melee/gm/gm_1601.h>
#include <melee/gm/gm_16A2.h>
#include <melee/gm/gm_1A3F.h>
#include <melee/gm/gm_1B03.h>
#include <melee/gm/gmevent.h>
#include <melee/gm/gmmain_lib.h>
#include <melee/gm/gmvs.h>
#include <melee/gm/types.h>
#include <melee/lb/lbarchive.h>
#include <melee/lb/lbdvd.h>
#include <melee/mn/types.h>

/// Vanilla `onEnterVs` in gm/gmevent.c, the event mode's match state
/// on_enter. Static there and its name is not unique, so it is named in
/// config/GALE01/tm_symbols.txt.
void gmEvent_onEnterVs(GameModeState* state);

/// Statics in gm/gmevent.c (unique names, resolved by the overlay linker).
extern struct gm_804D6900_t** gm_804D6900[2];
void fn_801BBFE8(void);
void gm_801BAB40(PlayerInitData* dst, struct gm_801BAB40_src* src);
s32 gm_801BAC9C(GameModeState* state, s32 player);

/// Same as the static inline in gm/gmevent.c.
static inline struct EventData* gm_GetEventData(void)
{
    return &gmMainLib_804D3EE0->vs.unk_530;
}

/// Same as the static inline in gm/gmevent.c.
static inline u8 gm_GetNextColor(u8 color)
{
    if (color <= 2) {
        color++;
    } else {
        color = 0;
    }
    return color;
}

/// Vanilla onEnterVs up to +0x3B8 (where TM-CE's Custom Event Code
/// injects): the match rules from GmEvent.dat for event index @p level.
static struct gm_804D6900_t** EnterVsRules(GameModeState* arg0,
                                           struct EventData* ev, u8 level,
                                           StartMeleeData** out_md)
{
    StartMeleeData* md = gm_GetGameModeStateEnterData(arg0);
    struct gm_804D6900_t** levels;

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
    *out_md = md;
    return levels;
}

/// Vanilla onEnterVs from +0x3B8 to the end (the players from the level
/// entry), with the patches TM-CE applies to that code:
/// - +0x440 nop (Event Select Screen/Choose Any Character for Events/
///   Always Copy CSS Character Info.asm; also `word 801BB1B0` in
///   config/GALE01/tm_hooks/ess.txt for vanilla's copy);
/// - +0x524 `b +0x30` (Custom Event Preload Behavior/Dont Adjust CPU Color
///   in Event Mode When Its Already in Use.asm; css.txt);
/// - +0x8D8 `li r0,-1` (Custom Event Preload Behavior/Disable Event
///   Preload - Match Enter.asm; css.txt): no preload case runs.
static void EnterVsPlayers(GameModeState* arg0, struct EventData* ev,
                           u8 level, struct gm_804D6900_t** levels,
                           StartMeleeData* md)
{
    gm_803DF94C_t** event_info = gm_803DF94C;
    s32 player_idx;
    int i;

    for (i = 0; i < 6; i++) {
        md->players[i].slot_type = Gm_PKind_NA;
    }

    for (player_idx = 0; player_idx < ((levels[level]->flags >> 5) & 7);
         player_idx++)
    {
        while (levels[level]->player_init[player_idx] == NULL) {
            player_idx++;
        }
        gm_801BAB40(&md->players[player_idx],
                    levels[level]->player_init[player_idx]);
        if (player_idx == 0) {
            u8 c;
            gm_801B05F4(md->players, ev->x6);
            ev->x7 = md->players[0].team;
            /* +0x440: always copy the CSS character */
            md->players[0].ckind = ev->x2;
            md->players[0].color = ev->x3;
            md->players[0].nametag = ev->nametag;
            c = md->players[0].ckind;
            ev->x0 = c;
            ev->x4C[0] = c;
            c = md->players[0].color;
            ev->x1 = c;
            ev->x50[0] = c;
            md->players[0].rumble_enabled =
                gm_RumbleEnabledForPlayer(ev->x6, md->players[0].nametag);
        } else {
            if (levels[level]->player_init[player_idx]->team == 0) {
                md->players[player_idx].team = md->players[0].team;
                md->players[player_idx].xD_b1 = 1;
            }
            if (levels[level]->player_init[player_idx]->c_kind == ChKind_None)
            {
                s8* t = &ev->x8 + player_idx - 1;
                s8 v = *t;
                if (v == -1) {
                    u8 nv = gm_801BAC9C(arg0, player_idx);
                    md->players[player_idx].ckind = nv;
                    *t = md->players[player_idx].ckind;
                } else {
                    md->players[player_idx].ckind = v;
                }
            }
            /* +0x524: the CPU keeps its color even when P1 uses it */
            if (md->players[0].ckind == CKind_Seak &&
                md->players[player_idx].ckind == CKind_Zelda)
            {
                u8 c = md->players[player_idx].color;
                if (c == md->players[0].color) {
                    md->players[player_idx].color = gm_GetNextColor(c);
                }
            }
            if (player_idx < 4) {
                ev->x4C[player_idx] = md->players[player_idx].ckind;
                ev->x50[player_idx] = md->players[player_idx].color;
            }
        }
    }

    if (levels[level]->kind == 2) {
        if (ev->x20 > 0) {
            s8 c;
            md->players[0].stocks = (s8) ev->x24;
            md->players[0].damage = ev->x28;
            md->players[0].xC_b1 = 0;
            c = ev->x38;
            if (c != 0x21) {
                md->players[0].ckind = c;
                ev->x0 = c;
                ev->x4C[0] = c;
            }
        }
        gm_801BAB40(&md->players[1],
                    levels[level]->evstage_table->entries[ev->x20]);
        if (md->players[1].ckind == md->players[0].ckind) {
            u8 c = md->players[1].color;
            if (c == md->players[0].color) {
                md->players[1].color = gm_GetNextColor(c);
            }
        }
        if (md->players[0].ckind == CKind_Seak &&
            md->players[1].ckind == CKind_Zelda)
        {
            u8 c = md->players[1].color;
            if (c == md->players[0].color) {
                md->players[1].color = gm_GetNextColor(c);
            }
        }
        ev->x4C[1] = md->players[1].ckind;
        ev->x50[1] = md->players[1].color;
    }
    if (level == 0x2B) {
        s32 c2 = ev->x4C[2];
        u8 c = ev->x50[2];
        if (ev->x4C[0] == c2 && ev->x50[0] == c) {
            ev->x50[2] = gm_GetNextColor(c);
        }
    }
    if (level == 0x31) {
        md->players[1].spawn_dir = 1;
        md->players[2].spawn_dir = -1;
        md->players[1].xD_b0 = 1;
        md->players[2].xD_b0 = 1;
        md->players[1].xD_b2 = 1;
        md->players[2].xD_b2 = 1;
    }
    if (levels[level]->kind == 1) {
        struct gm_evbonus* bonus;
        int x5_flag;
        s8 k;
        u8 color2;
        ev->xB_3 = 1;
        bonus = levels[level]->evbonus;
        if (bonus->x5 == 1) {
            x5_flag = 1;
            if ((s8) ev->x0 == bonus->c_kind) {
                u8 c;
                if (ev->x1 == (c = bonus->color)) {
                    ev->x50[1] = gm_GetNextColor(c);
                }
            }
        } else {
            x5_flag = 0;
        }
        bonus = levels[level]->evbonus;
        k = bonus->c_kind;
        if (k == 4) {
            color2 = bonus->x17;
        } else {
            color2 = 0;
        }
        gm_8016A22C(k, 0x21, 0x21, ev->x50[1], 0, 0, x5_flag, 0, color2,
                    ev->x0, ev->x1, bonus->x1, bonus->x2, bonus->x3, bonus->x4,
                    0, 1, bonus->x8, bonus->xC);
        gm_8016A414(levels[level]->evbonus->x10);
        gm_8016A21C(&md->rules);
        if ((levels[level]->evbonus->flags >> 7) & 1) {
            gm_8016A434();
        }
        if (event_info[level]->x4 != NULL) {
            gm_8016A404((s32) event_info[level]->x4);
        }
        if (levels[level]->evbonus->x15 != 0) {
            gm_8016A424(levels[level]->evbonus->x15);
        }
    }
    /* +0x8D8: the preload switch on ev->x44 never matches */
    lbDvd_GetPreloadCacheScene();
    gm_LoadRumbleEnabled(md);
    gm_80168F88();
}

/**
 * Replaces the event mode's match state on_enter (vanilla `onEnterVs`);
 * reached through the css area's event state list
 * (config/GALE01/tm_hooks/css.txt, tm_css_EventStates[1].on_enter).
 *
 * Port of TM-CE's "Custom Event Code - Rewrite.asm" (onEnterVs+0x3B8):
 * after vanilla's rules setup,
 * - a TM-CE event with a C file: EventInit for the players, stage and
 *   rules, then vanilla's last two calls (onEnterVs+0x9C8);
 * - any other TM-CE event (the 15 legacy assembly events): the legacy setup
 *   (src/melee/tm/legacy/), then vanilla's player setup (+0x3B8 onwards).
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
    levels = EnterVsRules(arg0, ev, level, &md);

    if (GetEventFile(page, level) != NULL) {
        /* TM-CE: players, stage and rules from the event's EventDesc. */
        EventInit(page, level, md);
        /* Character rotation: preload the deck's CPU characters
         * (src/melee/tm/rotation/tm_rotation.h). */
        if (tmce_GetEventRotation(page, level) != NULL) {
            tm_rot_Preload(tmce_GetEventRotation(page, level),
                           md->rules.stkind);
        }
        /* Vanilla onEnterVs from +0x9C8. */
        gm_LoadRumbleEnabled(md);
        gm_80168F88();
    } else {
        TmLegacySetup setup;
        setup.event = levels[level];
        setup.md = md;
        setup.event_id = level;
        setup.page = page;
        tm_legacy_Setup(&setup);
        EnterVsPlayers(arg0, ev, level, levels, md);
    }
}
