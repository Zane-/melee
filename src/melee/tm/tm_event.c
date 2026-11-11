#include "tm_event.h"

#include "tm.h"

#include <string.h>
#include <dolphin/dvd.h>
#include <melee/db/db.h>
#include <melee/ft/ftdevice.h>
#include <melee/gm/gm_1A3F.h>
#include <melee/gm/gmscene.h>
#include <melee/gm/gmvs.h>
#include <melee/gm/types.h>
#include <melee/gr/ground.h>
#include <melee/gr/stage.h>
#include <melee/gr/types.h>
#include <melee/lb/lb_00F9.h>
#include <melee/lb/lbarchive.h>
#include <melee/mn/types.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjplink.h>
#include <sysdolphin/baselib/gobjproc.h>
#include <sysdolphin/baselib/gobjuserdata.h>
#include <sysdolphin/baselib/memory.h>

/// Vanilla on_enter of Training mode's match state (gm/gmtrainingmode.c).
void gm_801B1F70(GameModeState* state);

extern const TmEventDesc tm_event_laserland;

/* TM-CE's three pages. Events are added as they are ported. */
static const TmEventDesc* const page_character_events[] = {
    &tm_event_laserland,
};

const TmEventPage tm_event_pages[] = {
    { "Character-specific Tech",
      sizeof(page_character_events) / sizeof(page_character_events[0]),
      page_character_events },
};
const int tm_event_page_num =
    sizeof(tm_event_pages) / sizeof(tm_event_pages[0]);

static void tmEvent_Update(void);

void* tmEvent_GetData(void)
{
    if (tm_state == NULL || tm_state->event_gobj == NULL) {
        return NULL;
    }
    return tm_state->event_gobj->user_data;
}

const TmEventDesc* tmEvent_GetSelected(void)
{
    const TmEventPage* page;

    if (tm_persist.event_page >= tm_event_page_num) {
        return NULL;
    }
    page = &tm_event_pages[tm_persist.event_page];
    if (tm_persist.event_index >= page->event_num) {
        return NULL;
    }
    return page->events[tm_persist.event_index];
}

void tmEvent_ApplyMatchData(StartMeleeData* data, const TmEventDesc* desc)
{
    StartMeleeRules* rules = &data->rules;
    const TmEventMatchData* md = desc->match_data;

    /* Defaults TM-CE sets for every event. The comments give TM-CE's
     * (MexTK MatchInit) name for each still-unnamed vanilla bit. */
    rules->x1_0 = 0;            /* timer_unk2 */
    rules->friendly_fire = 1;   /* unk2 */
    rules->x2_5 = 1;            /* unk7 */
    rules->is_vs = 1;           /* isCheckStockSteal */
    rules->x4_5 = 0;            /* unk1f = 3 */
    rules->x4_6 = 1;
    rules->x4_7 = 1;
    rules->x5_0 = 1;            /* no_check_end */
    rules->item_freq = -1;      /* items off */
    rules->x3_4 = 1;            /* isCheckForLRAStart */
    rules->x3_6 = 1;            /* isHidePauseHUD */
    rules->disable_pausing = 1; /* the event menu owns Start */

    if (md == NULL) {
        return;
    }
    rules->timer_enabled = (md->timer >> 1) & 1;
    rules->timer_counts_up = md->timer & 1;
    rules->match_kind = md->match_type;
    rules->x1_3 = md->hide_go;
    rules->x1_2 = md->hide_ready;
    rules->x2_6 = md->create_hud;
    rules->x3_7 = md->timer_run_on_pause;
    rules->x3_2 = md->check_for_z_retry;
    rules->x3_0 = md->show_score;
    rules->x4_2 = md->run_stock_logic;
    rules->x5_2 = md->disable_hit;
    rules->time_limit = md->timer_seconds;
}

void tmEvent_Exit(HSD_GObj* menu_gobj)
{
    gmVs_GetSceneState()->unk_0 = 3;
    fn_8016C7F0();
}

void tmEvent_DisableHazards(void)
{
    bool fix_wind = false;
    HSD_GObj* gobj;

    switch (Stage_8022519C(Stage_80225194())) {
    case Gr_Kind_Story:
        /* Stop the Shy Guys and remove Randall. */
        HSD_GObjProc_RemoveAllProcs(Ground_GetMapGObj(3));
        Ground_801C4A08(Ground_GetMapGObj(2));
        fix_wind = true;
        break;
    case Gr_Kind_PStadium:
        /* Stop transformations. */
        HSD_GObjProc_RemoveAllProcs(Ground_GetMapGObj(2));
        fix_wind = true;
        break;
    case Gr_Kind_OldPupupu:
        /* Stop Whispy and clear the wind hazard count. */
        HSD_GObjProc_RemoveAllProcs(Ground_GetMapGObj(7));
        HSD_GObjProc_RemoveAllProcs(Ground_GetMapGObj(6));
        ft_804D6578.x0 = 0;
        break;
    case Gr_Kind_Last: {
        /* Freeze the background: set the skip flag in the stage's vars
         * (Ground +0xC4) and drop the on-GO callback that would clear it. */
        struct OnGo {
            struct OnGo* next;
        }* on_go;

        gobj = Ground_GetMapGObj(3);
        *(int*) ((u8*) gobj->user_data + 0xC4) |= 0x40;

        on_go = stage_info.x6A4;
        stage_info.x6A4 = on_go->next;
        HSD_Free(on_go);
        break;
    }
    default:
        break;
    }

    /* Some stages decay wind inside the map proc that was just removed;
     * schedule it separately so knockback wind still works. */
    if (fix_wind) {
        gobj = GObj_Create(3, 5, 0);
        HSD_GObj_SetupProc(gobj, (HSD_GObjEvent) lb_800115F4, 4);
    }
}

void tmEvent_Load(void)
{
    const TmEventDesc* desc;
    const TmMenuAssets* assets = NULL;
    HSD_GObj* gobj;
    void* data;

    if (tm_state == NULL || tm_persist.magic != TM_PERSIST_MAGIC) {
        return;
    }
    desc = tmEvent_GetSelected();
    if (desc == NULL) {
        return;
    }
    tm_state->event_desc = desc;

    /* Event GObj with its zeroed data block. */
    gobj = GObj_Create(0, 7, 0);
    data = HSD_MemAlloc(TM_EVENT_DATASIZE);
    memset(data, 0, TM_EVENT_DATASIZE);
    GObj_InitUserData(gobj, 4, HSD_Free, data);
    if (desc->think != NULL) {
        HSD_GObj_SetupProc(gobj, desc->think, desc->callback_priority);
    }
    tm_state->event_gobj = gobj;

    if (desc->disable_hazards) {
        tmEvent_DisableHazards();
    }

    /* Per-frame update, replacing the vanilla pre-GObj callback
     * (db_RunEveryFrame), which tmEvent_Update chains to. */
    gm_SetPreGObjProcCallback(tmEvent_Update);

    /* Pause menu. Its art is optional so the build still runs on a disc
     * without the asset file. */
    if (desc->menu != NULL &&
        DVDConvertPathToEntrynum(TM_MENU_ASSET_FILE) != -1)
    {
        lbArchive_LoadSymbols(TM_MENU_ASSET_FILE, &assets,
                              TM_MENU_ASSET_SYMBOL, NULL);
        if (assets != NULL) {
            tmMenu_Init(desc->menu, assets);
        }
    }

    if (desc->init != NULL) {
        desc->init(gobj);
    }
}

static void tmEvent_Update(void)
{
    if (tm_state != NULL) {
        if (tm_state->menu_gobj != NULL) {
            tmMenu_Update(tm_state->menu_gobj);
        }
        if (tm_state->event_desc != NULL &&
            tm_state->event_desc->update != NULL)
        {
            tm_state->event_desc->update();
        }
    }

    /* The vanilla callback: develop-mode match hotkeys. */
    db_RunEveryFrame();
}

void tm_Hook_TrainingMatchEnter(GameModeState* state)
{
    const TmEventDesc* desc;
    StartMeleeData* data;

    gm_801B1F70(state);

    if (tm_persist.magic != TM_PERSIST_MAGIC || !tm_persist.event_active) {
        return; /* plain vanilla Training mode */
    }
    desc = tmEvent_GetSelected();
    if (desc == NULL) {
        return;
    }
    data = gm_GetGameModeStateEnterData(state);
    data->rules.on_match_start = tmEvent_Load;
    tmEvent_ApplyMatchData(data, desc);
}
