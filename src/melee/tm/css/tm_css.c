#include "tm_css.h"

#ifdef TM_TEST
#include "test/tmtest.h"
#endif

#include "../tm.h"
#include "../tmce.h"

#include <melee/ft/forward.h>
#include <melee/gm/gm_1601.h>
#include <melee/gm/gm_16A2.h>
#include <melee/gm/gm_16F1.h>
#include <melee/gm/gm_1A36.h>
#include <melee/gm/gm_1A3F.h>
#include <melee/gm/gm_1B03.h>
#include <melee/gm/gmevent.h>
#include <melee/gm/gmmain_lib.h>
#include <melee/gm/gmmenumode.h>
#include <melee/gm/gmscdata.h>
#include <melee/gm/types.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/lb/lbdvd.h>
#include <melee/lb/types.h>
#include <melee/mn/types.h>
#include <sysdolphin/baselib/controller.h>

/*
 * Event mode game-mode states and their callbacks, as TM-CE has them.
 *
 * TM-CE ("Add SSS To Event Match Scene List.asm", runGameMode+0x11C)
 * repoints the event mode's state list at its own three-state list
 * (CSS, match, SSS) and the main menu's at a two-state list (menu,
 * credits), and patches the CSS and match states' callbacks in place.
 *
 * Here the lists are overlay data installed with `pointer` hooks on the mode
 * table (config/GALE01/tm_hooks/css.txt), and the patched callbacks are C
 * copies of the vanilla ones. The vanilla states' scene data (css_data,
 * vs_enter_data, ...) are statics with ambiguous names, so each list is
 * filled from the vanilla list when its mode loads (`on_load` hooks).
 */

/// Training mode's SSS state on_enter (static in gm/gmtrainingmode.c).
void gm_801B1EB8(GameModeState* state);
/// gm/gmevent.c, no header declaration.
void gm_801BBB64(void);

static void tm_css_onEnterCss(GameModeState* state);
static void tm_css_onExitCss(GameModeState* state);
static void tm_css_onExitVs(GameModeState* state);
static void tm_css_onExitSss(GameModeState* state);
static void tm_css_onExitCredits(GameModeState* state);

/* State ids: 0 CSS, 1 match, 2 SSS (gm_SetNextGameModeStateId). */
enum { TM_STATE_CSS, TM_STATE_MATCH, TM_STATE_SSS };

GameModeState tm_css_EventStates[] = {
    {
        TM_STATE_CSS,
        lbDvdPreload_3,
        0,
        tm_css_onEnterCss,
        tm_css_onExitCss,
        { GS_CSS, NULL, NULL }, /* css_data, set by tm_css_EventModeLoad */
    },
    {
        TM_STATE_MATCH,
        lbDvdPreload_3,
        0,
        tm_Hook_EventEnterVs, /* src/melee/tm/tm_event_start.c */
        tm_css_onExitVs,
        { GS_VS, NULL, NULL }, /* vs_enter_data, vs_exit_data */
    },
    {
        TM_STATE_SSS,
        lbDvdPreload_3,
        0,
        gm_801B1EB8,
        tm_css_onExitSss,
        { GS_SSS, NULL, NULL }, /* css_data (as SSSData) */
    },
    { -1 },
};

GameModeState tm_css_MenuStates[] = {
    { 0 }, /* vanilla gm_Mode_Menu_States[0], copied by tm_css_MenuModeLoad */
    {
        1,
        lbDvdPreload_3,
        0,
        NULL,
        tm_css_onExitCredits,
        { GS_STAFFROLL, NULL, NULL },
    },
    { -1 },
};

/// `pointer` hook on the event mode's on_load (modes[GM_EVENT]).
void tm_css_EventModeLoad(void)
{
    GameModeState* van = gm_Mode_Event_States;

    tm_css_EventStates[TM_STATE_CSS].info = van[0].info;
    tm_css_EventStates[TM_STATE_MATCH].info = van[1].info;
    /* TM-CE's SSS state uses the CSS data block for both directions. */
    tm_css_EventStates[TM_STATE_SSS].info.enter_data = van[0].info.enter_data;
    tm_css_EventStates[TM_STATE_SSS].info.exit_data = van[0].info.enter_data;
    gm_Mode_Event_OnLoad();
#ifdef TM_TEST
    /* Test builds: skip the CSS (src/melee/tm/test/tmtest.h). */
    tm_test_OnEventModeLoad();
#endif
}

/// `pointer` hook on the menu mode's on_load (modes[GM_MENU]; vanilla NULL).
void tm_css_MenuModeLoad(void)
{
    tm_css_MenuStates[0] = gm_Mode_Menu_States[0];
}

static inline struct EventData* tm_css_GetEventData(void)
{
    return &gmMainLib_804D3EE0->vs.unk_530;
}

/*
 * TM-CE's character backup for its events: the save data's Training-mode
 * CSS block (save + 0xD10), so the Lab and vanilla Training share HMN / CPU
 * choices. Byte offsets as used by the TM-CE assembly.
 */
#define TM_BACKUP_BASE 0xD10
#define TM_BACKUP_HMN_CKIND 104
#define TM_BACKUP_HMN_COLOR 107
#define TM_BACKUP_HMN_NAMETAG 114
#define TM_BACKUP_CPU_CKIND 140
#define TM_BACKUP_CPU_COLOR 143
#define TM_BACKUP_CPU_NAMETAG 150

static inline u8* tm_css_Backup(void)
{
    return (u8*) gmMainLib_804D3EE0 + TM_BACKUP_BASE;
}

/* TM-CE CSSID bit order (events.h) -> external character kind. */
static const u8 tm_css_CSSIDToCKind[25] = {
    CKind_DrMario,  CKind_Mario,   CKind_Luigi,    CKind_Koopa,
    CKind_Peach,    CKind_Yoshi,   CKind_Donkey,   CKind_Captain,
    CKind_Ganon,    CKind_Falco,   CKind_Fox,      CKind_Ness,
    CKind_PopoNana, CKind_Kirby,   CKind_Samus,    CKind_Zelda,
    CKind_Link,     CKind_CLink,   CKind_Pichu,    CKind_Pikachu,
    CKind_Purin,    CKind_Mewtwo,  CKind_GameWatch, CKind_Mars,
    CKind_Emblem,
};

/// Ko counter block the vanilla CSS reads through CSSData::ko_counts.
extern u8 ko_counts[6];

/**
 * Event CSS on_enter: vanilla `onEnterCss` (gm/gmevent.c) with
 * - Load CSS + Preload CPU.asm (+0x20): CSS kind from the event, KO counter
 *   pointer, the event's fixed CPU and stage into the preload cache;
 * - Restore Event CPU.asm (+0x38): HMN and CPU picks from TM-CE's backup,
 *   the CPU forced to the first allowed character if the event has a list;
 * - Disable Event Preload - CSS Enter.asm (+0x48): no gm_801BA938 preload.
 */
static void tm_css_onEnterCss(GameModeState* arg0)
{
    struct EventData* ev = tm_css_GetEventData();
    CSSData* css = gm_GetGameModeStateEnterData(arg0);
    u8* bk = tm_css_Backup();
    int page = tmce_GetEventPage();
    int event = ev->unk_535;
    PreloadedGameModeState* preload;
    int* allowed;
    u8 css_type;
    s8 cpu;
    s8 stage;
    s8 cpu_ckind;
    s8 cpu_color;

    css->ko_counts = ko_counts;
    css_type = GetCSSType(page, event);
    cpu = GetCPUFighter(page, event);
    stage = (s8) GetStage(page, event); /* TM-CE sign-extends a byte */
    preload = lbDvd_GetPreloadCacheScene();
    if (cpu != -1) {
        preload->game_cache.entries[1].char_id = cpu;
    }
    if (stage != -1) {
        preload->game_cache.stkind = stage;
    }

    gm_801B06B0(css, css_type, bk[TM_BACKUP_HMN_CKIND], 0,
                bk[TM_BACKUP_HMN_COLOR], bk[TM_BACKUP_HMN_NAMETAG], 0,
                ev->x6);

    allowed = GetEventCharList(event, page);
    if (allowed[1] != -1 && (allowed[1] & 0x1FFFFFF) != 0) {
        /* TM-CE scans without a bound; an empty list would hang. */
        int i = 0;
        while (!(allowed[1] & (1 << i))) {
            i++;
        }
        cpu_ckind = tm_css_CSSIDToCKind[i];
        cpu_color = 0;
    } else {
        cpu_color = bk[TM_BACKUP_CPU_COLOR];
        cpu_ckind = bk[TM_BACKUP_CPU_CKIND];
        if (cpu_ckind == CKind_Seak) {
            cpu_ckind = CKind_Zelda;
        }
    }
    gm_801B07B4(css, cpu_ckind, 1, cpu_color, bk[TM_BACKUP_CPU_NAMETAG], 0,
                ev->x6);
}

/**
 * Event CSS on_exit: vanilla `onExitCss` with
 * - Load Character ssm Files.asm (+0x34): queue every picked character's
 *   sound bank;
 * - Backup Event CPU.asm (+0x48): HMN and CPU picks to TM-CE's backup, the
 *   HMN pick also to the vanilla event backup;
 * - Load SSS For Certain Events.asm (+0x58): go to the SSS if the event has
 *   no fixed stage.
 */
static void tm_css_onExitCss(GameModeState* arg0)
{
    struct EventData* ev = tm_css_GetEventData();
    CSSData* css = gm_GetGameModeStateExitData(arg0);
    u8* bk = tm_css_Backup();
    u8* player;
    u64 mask = 0;
    int i;

    if (css->pending_scene_change == 2) {
        /* Not in TM-CE: B on the character select of an event started
         * from the course hub goes back to the hub. */
        if (tmce_CourseRoute(1, tmce_GetEventPage(), ev->unk_535)) {
            gm_SetNextGameModeStateId(TM_STATE_CSS);
            return;
        }
        gm_ChangeGameModeAfterCurrentScene(GM_MENU);
        return;
    }

    /* CSSData +0x70: player 0's character kind, players 0x24 apart. */
    player = (u8*) css + 0x70;
    for (i = 0; i < 6; i++, player += 0x24) {
        mask |= lbAudioAx_80026E84((s8) player[0]);
    }
    lbAudioAx_80026F2C(20);
    lbAudioAx_8002702C(4, mask);
    lbAudioAx_80027168();

    gm_801B0730(css, (s8*) &bk[TM_BACKUP_HMN_CKIND], NULL,
                &bk[TM_BACKUP_HMN_COLOR], &bk[TM_BACKUP_HMN_NAMETAG], NULL);
    gm_801B0730(css, &ev->x2, NULL, &ev->x3, &ev->nametag, NULL);
    gm_801B07E8(css, (s8*) &bk[TM_BACKUP_CPU_CKIND], NULL,
                (s8*) &bk[TM_BACKUP_CPU_COLOR],
                (s8*) &bk[TM_BACKUP_CPU_NAMETAG], NULL);
    ev->x8 = -1;
    ev->x9 = -1;
    ev->xA = -1;

    /* Not in TM-CE: the course hub switched to another event (the Lab):
     * that event's own character select comes next. */
    if (tmce_CourseRoute(2, tmce_GetEventPage(), ev->unk_535)) {
        gm_SetNextGameModeStateId(TM_STATE_CSS);
        return;
    }
    if (GetIsSelectStage(tmce_GetEventPage(), ev->unk_535)) {
        gm_SetNextGameModeStateId(TM_STATE_SSS);
    }
}

/// SSS_SceneDecide in Add SSS To Event Match Scene List.asm.
static void tm_css_onExitSss(GameModeState* arg0)
{
    SSSData* sss = gm_GetGameModeStateExitData(arg0);

    gm_SetNextGameModeStateId(sss->start_game ? TM_STATE_MATCH
                                              : TM_STATE_CSS);
}

/// Credits_SceneDecide in Add SSS To Event Match Scene List.asm: clear the
/// next state id (stored as id + 1, so 0xFF wraps to 0).
static void tm_css_onExitCredits(GameModeState* arg0)
{
    gm_SetNextGameModeStateId(0xFF);
}

/// A+B to Reset Event: A and B held on any controller.
static bool tm_css_IsResetHeld(void)
{
    u64 held = gm_GetButtonsPressed(4);
    return (held & HSD_PAD_A) && (held & HSD_PAD_B);
}

/**
 * Event match on_exit: vanilla `onExitVs` (gm/gmevent.c) with
 * Check for Reset on LRAStart.asm (+0xEC) and Check for Reset on Game
 * End.asm (+0x2E0): holding A+B when the match ends by LRA+Start, or when
 * it would return to the menu, restarts the event (the retry path, +0x48).
 */
static void tm_css_onExitVs(GameModeState* arg0)
{
    struct EventData* ev = tm_css_GetEventData();
    MatchExitInfo* exit = gm_GetGameModeStateExitData(arg0);
    u8 stage = ev->unk_535;
    u8 kind;
    s32 t;

    gm_8016A164();
    if (exit->match_end.outcome == OUTCOME_RETRY) {
        goto retry;
    }
    /* Not in TM-CE: a course drill (and a free-practice event started from
     * the course hub) ends at the character select, where the hub reopens
     * (src/tmce/events/course/hub_css.c), instead of at the main menu.
     * A+B held still restarts the event, as below. */
    if (!(exit->match_end.outcome == OUTCOME_NO_CONTEST &&
          tm_css_IsResetHeld()) &&
        tmce_CourseRoute(0, tmce_GetEventPage(), stage))
    {
        gm_SetNextGameModeStateId(TM_STATE_CSS);
        return;
    }
    if (exit->match_end.outcome == OUTCOME_NO_CONTEST) {
        if (tm_css_IsResetHeld()) {
            goto retry;
        }
        gm_ChangeGameModeAfterCurrentScene(GM_MENU);
        return;
    }
    ev->x3C += gm_80168940(&exit->match_end);
    ev->x40 += (s32) exit->match_end.frame_count;
    if (ev->xB_4 && ev->xB_2) {
        ev->x24 = exit->match_end.player_standings[0].stocks;
        ev->x28 = exit->match_end.player_standings[0].percent;
        ev->xB_2 = 0;
        ev->xB_5 = 0;
        t = ev->x20;
        ev->x20 = t + 1;
        gm_801BBB64();
        gm_SetNextGameModeStateId(1);
        return;
    }
    if (ev->xB_1) {
        u32 cur = ev->xC;
        u32 best = gmMainLib_8015CF5C(stage);
        s32 upd = 0;
        if (ev->xB_6) {
            if (best == 0 || cur < best) {
                best = cur;
                upd = 1;
            }
        } else if (cur > best) {
            best = cur;
            upd = 1;
        }
        if (upd != 0) {
            gmMainLib_8015CF70(stage, best);
        }
        gmMainLib_8015CEB4(stage);
    }
    gm_8016247C(ev->x3C);
    gm_80162968((u32) ev->x40 / 60);
    if (ev->xB_1) {
        kind = gm_801732D8(ev->unk_535);
    } else {
        kind = ChKind_Max;
    }
    if (ev->unk_535 == gm_801BEBC0(0x32) &&
        exit->match_end.player_standings[0].stocks == 3)
    {
        gmMainLib_8015CF84();
    }
    if (ev->xB_1) {
        u16 sid = gm_8017335C();
        if (sid != 0x148) {
            gm_80164504(sid);
        }
    }
    if (ev->xB_1) {
        gm_80173D3C(ev->unk_535);
    }
    gm_80173EEC();
    gm_80172898(0x10);
    if (kind != ChKind_Max) {
        gm_InitChallengerData(ev->x0, ev->x1, ev->x6, ev->nametag, kind,
                              GM_MENU);
        gm_ChangeGameModeAfterCurrentScene(GM_CHALLENGER_APPROACH);
        return;
    }
    if (gm_80173754(1, ev->x6) == 0) {
        if (tm_css_IsResetHeld()) {
            goto retry;
        }
        gm_ChangeGameModeAfterCurrentScene(GM_MENU);
    }
    return;

retry: {
    s32 do_save = 0;
    if (ev->x20 != 0) {
        do_save = 1;
    }
    if (stage == 0x31) {
        do_save = 0;
    }
    ev->xB_5 = 0;
    ev->x20 = 0;
    ev->x24 = 0;
    ev->x28 = 0;
    ev->x2C = 0;
    ev->x30 = 0;
    ev->x34 = 0;
    ev->x38 = 0x21;
    ev->x3C = 0;
    ev->x40 = 0;
    gm_801BBB64();
    if (do_save != 0) {
        struct GameCache* gc = &lbDvd_GetPreloadCacheScene()->game_cache;
        lbDvd_80018C6C();
        gc->entries[0].char_id = (s8) ev->x0;
        gc->entries[0].color = ev->x1;
        lbDvd_80018254();
        lbDvd_80017700(4);
    }
    gm_SetNextGameModeStateId(1);
}
}
