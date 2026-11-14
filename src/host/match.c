/** @file
 * Starting a match without the menus.
 *
 * The game has a developers' mode for this, GM_DEBUG_VS, whose one state
 * fills the match's start data and enters the VS scene. The host gives that
 * mode its own state table at run time (the mode table is data), with the
 * characters and stage it was asked for, and enters the mode through the
 * game's mode override: the function the game calls between scenes to ask
 * whether another mode should interrupt (the memory card prompts use it).
 */
#include "host.h"

#include <melee/gm/gm_1601.h>
#include <melee/gm/gm_1A3F.h>
#include <melee/gm/gmscdata.h>
#include <melee/gm/gmscene.h>
#include <melee/gm/gmvsmelee.h>
#include <melee/gm/types.h>
#include <melee/lb/lbcardgame.h>
#include <melee/mn/types.h>
#include <melee/pl/forward.h>
#include <sysdolphin/baselib/random.h>

HostMatch host_match = {
    .ckind = { 2, 9, -1, -1 }, /* Fox, Marth */
    .human = { 1, 1, 0, 0 },
    .stage = 0x20, /* Final Destination */
    .seed = 1,
};

static int requested;
static int installed;
static int started; ///< a match has been asked for since the game booted

/// What the game's own state does (onEnterDebugVs, gmvsmode.c): a time
/// match with no items between two humans. Only the characters, the stage,
/// whether player 2 is a CPU and the random seed are the host's.
static void on_enter(GameModeState* state)
{
    StartMeleeData* start = gm_GetGameModeStateEnterData(state);

    gm_SetupRulesDefaults(&start->rules);
    start->rules.stkind = host_match.stage;
    start->rules.item_freq = -1;
    start->rules.sd_penalty = -1;
    start->rules.match_kind = MatchKind_Time;
    if (host_match.stocks > 0) {
        start->rules.match_kind = MatchKind_Stock;
        start->rules.is_stock = 1;
    }
    for (int i = 0; i < GM_MAX_PLAYERS; i++) {
        PlayerInitData* p = &start->players[i];
        gm_SetupPlayerDefaults(p);
        p->stocks = (u8) host_match.stocks;
        p->cpu_kind = 4;
        p->rumble_enabled = 0;
        if (i < 4 && host_match.ckind[i] >= 0) {
            p->ckind = (s8) host_match.ckind[i];
            p->slot_type = host_match.human[i] ? Gm_PKind_Human : Gm_PKind_Cpu;
        } else if (i < 4) {
            p->ckind = CKind_Link; /* as the game's own state leaves it */
        }
    }
    *HSD_RandSeedPtr = host_match.seed;
    host_match.entered++;
    gm_LoadAnnouncer();
    host_log("match: %d vs %d on stage %d, seed %u", host_match.ckind[0],
             host_match.ckind[1], host_match.stage, host_match.seed);
}

static GameModeState states[] = {
    {
        1,
        lbDvdPreload_2,
        0,
        on_enter,
        NULL,
        {
            GS_VS,
            &gmVsMelee_StartData,
            &gmVsMelee_VsExitInfo,
        },
    },
    { GM_GAMEMODESTATE_TERMINATE },
};

/// Which mode comes next, asked by the game between scenes. Before the first
/// match the game's own choice (it boots into its menus, which a driver
/// covers). After it, always the match again: when the game ends a match
/// itself (L+R+A+Start in its pause), its own choice would be the memory
/// card check and then its menus, scenes the host does not provide for (the
/// owner's client crashed there, 2026-11-13).
static u8 mode_override(void)
{
    if (requested) {
        requested = 0;
        return GM_DEBUG_VS;
    }
    if (started) {
        host_match.ended++;
        host_log("the game ended the match; it starts again");
        return GM_DEBUG_VS;
    }
    return lbCardGame_DecideGameMode();
}

void host_match_install(void)
{
    if (!installed) {
        GameMode* modes = gm_GetAllGameModes();
        for (int i = 0; modes[i].kind != GM_COUNT; i++) {
            if (modes[i].kind == GM_DEBUG_VS) {
                modes[i].states = states;
                installed = 1;
            }
        }
        if (!installed) {
            host_fatal("no debug VS mode in the mode table");
        }
    }
    /* Each frame: the boot mode installs the game's own on its way out. */
    gm_SetGameModeOverride(mode_override);
    if (requested) {
        /* Still waiting: the scene that ended went on to another mode
           before the override was asked. End that one too. */
        gm_801A4B60();
    }
}

void host_match_start(void)
{
    requested = 1;
    started = 1;
    host_match_install(); /* ends the current scene */
}
