#include "tmtest.h"

#include "rotation/tm_rotation.h"

#include <melee/ft/fighter.h>
#include <melee/gm/gmmain_lib.h>
#include <melee/gm/types.h>
#include <melee/ft/types.h>
#include <melee/lb/lb_0195.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/lb/lbdvd.h>
#include <melee/lb/types.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/random.h>
#include <stdio.h>

/**
 * @file
 * Test runner (see tmtest.h). Test builds only: tools/overlay_build.py
 * compiles this area and config/GALE01/tm_hooks/test.txt when TM_TEST=1.
 */

TmTestConfig tm_test_config = { 0 };

/// gm/gm_1A3F.c: `static struct stateMachine state_machine` (unique name).
/// routing.curr_state_id is byte 3.
extern u8 state_machine[0x14];
#define STATE_ID_OFFSET 3
/// The event mode's match state id (src/melee/tm/css/tm_css.c TM_STATE_MATCH).
#define EVENT_MATCH_STATE 1

/// mn/mncharsel.c: the CSS's human and CPU ports (TM-CE stc_css_hmnport /
/// stc_css_cpuport), read by TM-CE's EventInit.
extern s8 mnCharSel_804D6CF0;
extern s8 mnCharSel_804D6CF1;

/// Final Destination's external stage id (TM-CE GRKINDEXT_FD).
#define TEST_DEFAULT_STAGE 32

/// TM-CE events.c (tmFunction).
s8 GetCPUFighter(int page, int event);
s16 GetStage(int page, int event);
int tmce_GetEventPage(void);

typedef struct TestState {
    int frame;              ///< match frame, -1 outside a match
    int done;
    u16 prev_state[2];      ///< action state at the end of the last frame
    int armed[TM_TEST_MAX_INPUTS]; ///< frame the trigger fired, -1 = not yet
} TestState;

static TestState ts = { -1 };

static int Active(void)
{
    return tm_test_config.magic == TM_TEST_MAGIC;
}

int tm_test_Frame(void)
{
    return ts.frame;
}

/// Event mode on_load (css area, test builds): put the configured
/// characters in the preload cache, where the CSS would, and start the mode
/// at the match state so no CSS runs.
void tm_test_OnEventModeLoad(void)
{
    TmTestConfig* c = &tm_test_config;
    struct GameCache* gc = &lbDvd_GetPreloadCacheScene()->game_cache;
    u64 audio = 0;
    int i;

    if (!Active()) {
        return;
    }
    /* Options first: one of them may choose what the event is about to
     * load (a course drill: its CPU, stage and opponent deck are read from
     * the event's description below and by match setup). */
    for (i = 0; i < (int) c->option_count && i < TM_TEST_MAX_OPTIONS; i++) {
        tmce_test_SetOption(c->event, c->options[i].index,
                            c->options[i].value);
    }
    /* Start from an empty cache, as after a CSS: earlier scenes (title,
     * menus) may have left characters in it. */
    for (i = 0; i < 8; i++) {
        gc->entries[i].char_id = ChKind_None;
        gc->entries[i].color = 0;
    }
    if (c->hmn_ckind != TM_TEST_NONE) {
        gc->entries[0].char_id = c->hmn_ckind;
        gc->entries[0].color = c->hmn_color;
    }
    /* As the event CSS's on_enter does (tm_css_onEnterCss): the event's
     * fixed CPU and stage, unless the test names its own. No SSS runs, so
     * an event with a free stage gets Final Destination. */
    {
        int page = tmce_GetEventPage();
        int event = gmMainLib_804D3EE0->vs.unk_530.unk_535;
        int event_cpu = GetCPUFighter(page, event);
        int stage = c->stage != 0xFFFF ? c->stage : GetStage(page, event);
        if (event_cpu != -1) {
            /* The event's own CPU: EventInit creates it. A test's CPU goes
             * in the next slot, where character rotation counts it as
             * loaded (src/melee/tm/rotation). */
            gc->entries[1].char_id = event_cpu;
            gc->entries[1].color = 0;
            if (c->cpu_ckind != TM_TEST_NONE && c->cpu_ckind != event_cpu) {
                gc->entries[2].char_id = c->cpu_ckind;
                gc->entries[2].color = c->cpu_color;
            }
        } else if (c->cpu_ckind != TM_TEST_NONE) {
            gc->entries[1].char_id = c->cpu_ckind;
            gc->entries[1].color = c->cpu_color;
        }
        gc->stkind = stage != -1 ? stage : TEST_DEFAULT_STAGE;
    }
    mnCharSel_804D6CF0 = 0;
    mnCharSel_804D6CF1 = 1;

    /* Not committed here: the match state's preloadState (lbDvdPreload_3)
     * reconfigures and releases the preload heaps after on_load, then
     * commits these entries. tm_test_OnMatchEnter waits for them. */

    /* The CSS's on_exit loads the picked characters' sound banks. */
    for (i = 0; i < 2; i++) {
        if (gc->entries[i].char_id != ChKind_None) {
            audio |= lbAudioAx_80026E84(gc->entries[i].char_id);
        }
    }
    lbAudioAx_80026F2C(20);
    lbAudioAx_8002702C(4, audio);
    lbAudioAx_80027168();

    /* Seed now as well as at match start: match setup draws random numbers
     * too (character rotation picks its preload subset). */
    *HSD_RandSeedPtr = c->seed;
    tm_rot_SetSeed(c->seed);
    state_machine[STATE_ID_OFFSET] = EVENT_MATCH_STATE;
    OSReport("TMTEST {\"boot\":\"%s\",\"hmn\":%d,\"cpu\":%d,\"seed\":%u}\n",
             c->event, c->hmn_ckind, c->cpu_ckind, c->seed);
}

/// Event match state on_enter (tm_event_start.c, test builds), before
/// anything else: the CSS commits its picks every frame so they have long
/// loaded by now; without a CSS, wait for the load, the way vanilla event
/// mode's onEnterVs does (lbDvd_80018254, lbDvd_80017700).
void tm_test_OnMatchEnter(void)
{
    if (Active()) {
        lbDvd_80018254();
        lbDvd_80017700(4);
    }
}

static u16 StateOf(int slot)
{
    HSD_GObj* gobj = Player_GetEntity(slot);
    if (gobj == NULL) {
        return 0xFFFF;
    }
    return GET_FIGHTER(gobj)->motion_id;
}

/// One line per call: Dolphin logs each OSReport call separately.
static void Trace(void)
{
    char buf[256];
    int n = sprintf(buf, "TMTEST {\"f\":%d,\"p\":[", ts.frame);
    int slot;
    for (slot = 0; slot < 2; slot++) {
        HSD_GObj* gobj = Player_GetEntity(slot);
        if (gobj != NULL) {
            Fighter* fp = GET_FIGHTER(gobj);
            n += sprintf(buf + n,
                         "%s{\"ck\":%d,\"st\":%d,\"x\":%.2f,\"y\":%.2f,"
                         "\"pct\":%.1f}",
                         slot ? "," : "", Player_GetPlayerCharacter(slot),
                         fp->motion_id, fp->cur_pos.x, fp->cur_pos.y,
                         fp->dmg.x1830_percent);
        }
    }
    sprintf(buf + n, "]}\n");
    OSReport("%s", buf);
}

/// Fire state triggers from the states at the end of the previous frame.
static void UpdateTriggers(void)
{
    TmTestConfig* c = &tm_test_config;
    u16 now[2];
    int i;

    now[0] = StateOf(0);
    now[1] = StateOf(1);
    for (i = 0; i < (int) c->input_count && i < TM_TEST_MAX_INPUTS; i++) {
        TmTestInput* in = &c->inputs[i];
        int p = in->port & 1;
        if (in->trigger == TM_TEST_ON_ENTER && now[p] == in->state &&
            ts.prev_state[p] != in->state)
        {
            ts.armed[i] = ts.frame;
        } else if (in->trigger == TM_TEST_ON_EXIT &&
                   ts.prev_state[p] == in->state && now[p] != in->state)
        {
            ts.armed[i] = ts.frame;
        }
    }
    ts.prev_state[0] = now[0];
    ts.prev_state[1] = now[1];
}

/// Port 1's scripted input for this frame.
static void ScriptedPad(PADStatus* out)
{
    TmTestConfig* c = &tm_test_config;
    int i;

    out->button = 0;
    out->stickX = out->stickY = 0;
    out->substickX = out->substickY = 0;
    out->triggerLeft = out->triggerRight = 0;
    out->analogA = out->analogB = 0;
    out->err = 0;

    for (i = 0; i < (int) c->input_count && i < TM_TEST_MAX_INPUTS; i++) {
        TmTestInput* in = &c->inputs[i];
        int start = in->trigger == TM_TEST_AT_FRAME ? 0 : ts.armed[i];
        int hold = in->hold != 0 ? in->hold : 1;
        int t;
        if (start < 0) {
            continue;
        }
        t = ts.frame - start - in->frame;
        if (t < 0 || t >= hold) {
            continue;
        }
        out->button |= in->buttons;
        if (in->lx != 0 || in->ly != 0) {
            out->stickX = in->lx;
            out->stickY = in->ly;
        }
        if (in->cx != 0 || in->cy != 0) {
            out->substickX = in->cx;
            out->substickY = in->cy;
        }
        if (in->l > out->triggerLeft) {
            out->triggerLeft = in->l;
        }
        if (in->r > out->triggerRight) {
            out->triggerRight = in->r;
        }
    }
}

static void BeginMatch(void)
{
    int i;
    ts.frame = 0;
    ts.done = 0;
    ts.prev_state[0] = ts.prev_state[1] = 0xFFFF;
    for (i = 0; i < TM_TEST_MAX_INPUTS; i++) {
        ts.armed[i] = -1;
    }
    *HSD_RandSeedPtr = tm_test_config.seed;
    OSReport("TMTEST {\"match\":\"start\"}\n");
}

/**
 * Wraps the `lb_800198E0` (HSD_PadRenewMasterStatus) call in the game loop
 * (gm_801A4D34+0xB4), which pops one raw pad reading per logic frame. In a
 * test match, port 1's reading is replaced by the script before it is
 * popped, so everything downstream (master, game status, fighters, TM-CE
 * menus) sees it as real controller input, frame-exactly.
 */
void tm_test_PadRenew(void)
{
    PadLibData* p = &HSD_PadLibData;
    int in_match = Active() && Player_GetEntity(0) != NULL;

    if (!in_match) {
        if (ts.frame >= 0) {
            OSReport("TMTEST {\"match\":\"end\",\"f\":%d}\n", ts.frame);
        }
        ts.frame = -1;
        lb_800198E0();
        return;
    }
    if (ts.frame < 0) {
        BeginMatch();
    } else {
        ts.frame++;
    }
    UpdateTriggers();

    if (p->qcount != 0 && !ts.done) {
        ScriptedPad(&p->queue->stat[p->qread * 4]);
    }
    lb_800198E0();

    if (!ts.done) {
        if (tm_test_config.trace != 0 &&
            ts.frame % tm_test_config.trace == 0)
        {
            Trace();
        }
        if (ts.frame >= (int) tm_test_config.max_frames) {
            ts.done = 1;
            OSReport("TMTEST {\"done\":true,\"f\":%d}\n", ts.frame);
        }
    }
}
