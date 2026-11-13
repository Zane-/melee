#include "controls.h"

#include <string.h>

#include <stddef.h>
#include <dolphin/pad.h>
#include <melee/gm/forward.h>
#include <melee/gm/gm_1A3F.h>
#include <melee/gm/gmmain_lib.h>
#include <melee/gm/types.h>
#include <melee/pl/forward.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/controller.h>

TmCtlSettings tm_ctl;

/// What each action is on the standard controller.
static const u16 action_button[TmCtlAct_Count] = {
    0,           /* None */
    PAD_BUTTON_A, /* Attack */
    PAD_BUTTON_B, /* Special */
    PAD_BUTTON_X, /* Jump */
    PAD_TRIGGER_R, /* Shield */
    PAD_TRIGGER_Z, /* Grab */
    PAD_BUTTON_UP, /* Taunt */
};

static const u16 input_button[TmCtlIn_Count] = {
    PAD_BUTTON_A,    PAD_BUTTON_B,    PAD_BUTTON_X,    PAD_BUTTON_Y,
    PAD_TRIGGER_Z,   PAD_TRIGGER_L,   PAD_TRIGGER_R,   PAD_BUTTON_UP,
    PAD_BUTTON_DOWN, PAD_BUTTON_LEFT, PAD_BUTTON_RIGHT,
};

static const u8 standard_map[TmCtlIn_Count] = {
    TmCtlAct_Attack, TmCtlAct_Special, TmCtlAct_Jump,  TmCtlAct_Jump,
    TmCtlAct_Grab,   TmCtlAct_Shield,  TmCtlAct_Shield, TmCtlAct_Taunt,
    TmCtlAct_None,   TmCtlAct_None,    TmCtlAct_None,
};

/// Every bit a profile can assign: the rest (START) pass through.
#define MAPPED_BUTTONS                                                        \
    (PAD_BUTTON_A | PAD_BUTTON_B | PAD_BUTTON_X | PAD_BUTTON_Y |              \
     PAD_TRIGGER_Z | PAD_TRIGGER_L | PAD_TRIGGER_R | PAD_BUTTON_UP |          \
     PAD_BUTTON_DOWN | PAD_BUTTON_LEFT | PAD_BUTTON_RIGHT)

/// Raw samples of the last frames, newest at #ring_at.
static PADStatus ring[TM_CTL_MAX_DELAY + 1][4];
static int ring_at;
static int ring_count;
static bool in_match;
static u8 active_profile[4];

void tm_ctl_ResetProfile(int index, const char* name)
{
    TmCtlProfile* p = &tm_ctl.profiles[index];
    int i;

    memset(p, 0, sizeof(*p));
    for (i = 0; i < TM_CTL_NAME_LEN && name[i] != '\0'; i++) {
        p->name[i] = name[i];
    }
    for (i = 0; i < TmCtlIn_Count; i++) {
        p->map[i] = standard_map[i];
    }
    p->tap_jump = true;
    p->used = true;
}

void tm_ctl_Init(void)
{
    int i;

    memset(&tm_ctl, 0, sizeof(tm_ctl));
    tm_ctl_ResetProfile(0, "Standard");
    for (i = 1; i < TM_CTL_PROFILE_COUNT; i++) {
        tm_ctl_ResetProfile(i, "");
        tm_ctl.profiles[i].used = false;
    }
}

/* --- on the memory card --------------------------------------------------- */

#define SAVE_SLOT (GM_NAMETAG_BANK_COUNT * GM_NAMETAG_BANK_SIZE - 1)
#define SAVE_MAGIC 0x544D4331 /* "TMC1": bump when TmCtlSettings changes */
/// The settings sit in front of the slot's name, which stays empty.
#define SAVE_ROOM offsetof(struct NameTagData, namedata)

typedef char
    tm_ctl_SaveFits[(sizeof(u32) + sizeof(TmCtlSettings) <= 0x198) ? 1 : -1];

static u8* SaveArea(void)
{
    return (u8*) GetPersistentNameData(SAVE_SLOT);
}

void tm_ctl_Load(void)
{
    u8* at = SaveArea();
    TmCtlSettings in;
    u32 magic;
    int i, j;

    memcpy(&magic, at, sizeof(magic));
    if (magic != SAVE_MAGIC) {
        /* A save that has never held settings. Put the current ones there
           without asking for a write, so that tm_ctl_Store only reports a
           change once the player has made one. */
        magic = SAVE_MAGIC;
        memcpy(at, &magic, sizeof(magic));
        memcpy(at + sizeof(magic), &tm_ctl, sizeof(tm_ctl));
        return;
    }
    memcpy(&in, at + sizeof(magic), sizeof(in));

    /* Anything out of range means the bytes are not ours: keep what we
       have. */
    if (in.delay > TM_CTL_MAX_DELAY) {
        return;
    }
    for (i = 0; i < TM_CTL_PROFILE_COUNT; i++) {
        in.profiles[i].name[TM_CTL_NAME_LEN] = '\0';
        for (j = 0; j < TmCtlIn_Count; j++) {
            if (in.profiles[i].map[j] >= TmCtlAct_Count) {
                return;
            }
        }
    }
    tm_ctl = in;
    tm_ctl_ResetProfile(0, "Standard");
    for (i = 0; i < 4; i++) {
        if (tm_ctl.port_profile[i] >= TM_CTL_PROFILE_COUNT ||
            !tm_ctl.profiles[tm_ctl.port_profile[i]].used)
        {
            tm_ctl.port_profile[i] = 0;
        }
    }
    /* A nickname that was deleted since takes its link with it. */
    for (i = 0; i < TM_CTL_NAMETAG_COUNT; i++) {
        if (tm_ctl.name_profile[i] >= TM_CTL_PROFILE_COUNT ||
            !tm_ctl.profiles[tm_ctl.name_profile[i]].used ||
            GetPersistentNameData(i)->namedata[0] == '\0')
        {
            tm_ctl.name_profile[i] = 0;
        }
    }
}

bool tm_ctl_Store(void)
{
    u8* at = SaveArea();
    u32 magic = SAVE_MAGIC;

    if (memcmp(at, &magic, sizeof(magic)) == 0 &&
        memcmp(at + sizeof(magic), &tm_ctl, sizeof(tm_ctl)) == 0)
    {
        return false;
    }
    memcpy(at, &magic, sizeof(magic));
    memcpy(at + sizeof(magic), &tm_ctl, sizeof(tm_ctl));
    return true;
}

void tm_ctl_SetNameProfile(int nametag, int profile)
{
    if (nametag >= 0 && nametag < TM_CTL_NAMETAG_COUNT && profile >= 0 &&
        profile < TM_CTL_PROFILE_COUNT)
    {
        tm_ctl.name_profile[nametag] = profile;
    }
}

/// The profile each port plays with: its player's nickname's if that
/// nickname carries one, else the port's own. The players are not set up
/// yet when the match start hook runs, so this is worked out as pads are
/// read.
static void ResolveProfiles(void)
{
    int slot;
    int port;

    for (port = 0; port < 4; port++) {
        active_profile[port] = tm_ctl.port_profile[port];
        if (active_profile[port] >= TM_CTL_PROFILE_COUNT ||
            !tm_ctl.profiles[active_profile[port]].used)
        {
            active_profile[port] = 0;
        }
    }
    for (slot = 0; slot < 4; slot++) {
        int nametag;
        if (Player_GetPlayerSlotType(slot) != Gm_PKind_Human) {
            continue;
        }
        port = Player_GetPadPort(slot);
        nametag = Player_GetNametagSlotID(slot);
        if (port >= 0 && port < 4 && nametag >= 0 &&
            nametag < TM_CTL_NAMETAG_COUNT &&
            tm_ctl.name_profile[nametag] != 0 &&
            tm_ctl.name_profile[nametag] < TM_CTL_PROFILE_COUNT &&
            tm_ctl.profiles[tm_ctl.name_profile[nametag]].used)
        {
            active_profile[port] = tm_ctl.name_profile[nametag];
        }
    }
}

/// Slippi runs its online matches in this otherwise unused game mode (its
/// SCENE_ONLINE_* are all minors of major 8, slippi-ssbm-asm Online/Online.s,
/// read 2026-11-13). There its Dolphin supplies every frame's pads and runs
/// frames again on a rollback: rewriting or delaying them here, from state
/// that is not rolled back, would desync the match.
static bool Online(void)
{
    return gm_GetCurrentGameMode() == GM_HANYU_CSS;
}

void tm_ctl_OnStartMelee(void)
{
    ring_count = 0;
    in_match = true;
}

void tm_ctl_OnSceneChange(void)
{
    in_match = false;
    ring_count = 0;
}

bool tm_ctl_TapJump(int port)
{
    if (!in_match || Online() || port < 0 || port >= 4) {
        return true;
    }
    return tm_ctl.profiles[active_profile[port]].tap_jump;
}

/// Rewrite one pad's buttons and triggers by its profile.
static void Remap(PADStatus* pad, const TmCtlProfile* p)
{
    u16 held = pad->button;
    u16 out = held & ~MAPPED_BUTTONS;
    u8 shield = 0;
    bool trigger_shields = false;
    int i;

    for (i = 0; i < TmCtlIn_Count; i++) {
        int act = p->map[i];
        if (act == TmCtlAct_Shield) {
            /* A trigger keeps its travel: light shield still works. */
            if (i == TmCtlIn_L) {
                trigger_shields = true;
                if (pad->triggerLeft > shield) {
                    shield = pad->triggerLeft;
                }
            } else if (i == TmCtlIn_R) {
                trigger_shields = true;
                if (pad->triggerRight > shield) {
                    shield = pad->triggerRight;
                }
            }
        }
        if (held & input_button[i]) {
            out |= action_button[act];
            if (act == TmCtlAct_Shield && i != TmCtlIn_L && i != TmCtlIn_R) {
                shield = 0xFF; /* a button is all the way down */
            }
        }
    }
    (void) trigger_shields;
    pad->button = out;
    pad->triggerLeft = 0;
    pad->triggerRight = shield;
}

static bool IsStandard(const TmCtlProfile* p)
{
    int i;
    for (i = 0; i < TmCtlIn_Count; i++) {
        if (p->map[i] != standard_map[i]) {
            return false;
        }
    }
    return true;
}

void tm_ctl_PadRenewMaster(void)
{
    PadLibData* lib = &HSD_PadLibData;

    if (in_match && !Online() && lib->qcount != 0) {
        PADStatus* head = &lib->queue->stat[lib->qread * 4];
        int delay = tm_ctl.delay;
        int i;

        if (delay > TM_CTL_MAX_DELAY) {
            delay = TM_CTL_MAX_DELAY;
        }
        ResolveProfiles();
        for (i = 0; i < 4; i++) {
            const TmCtlProfile* p = &tm_ctl.profiles[active_profile[i]];
            if (head[i].err == PAD_ERR_NONE && p->used && !IsStandard(p)) {
                Remap(&head[i], p);
            }
        }
        /* Remember this frame's sample; hand the game the one from `delay`
           frames ago (nothing held, until that many are remembered). */
        ring_at = (ring_at + 1) % (TM_CTL_MAX_DELAY + 1);
        memcpy(ring[ring_at], head, sizeof(ring[ring_at]));
        if (ring_count <= TM_CTL_MAX_DELAY) {
            ring_count++;
        }
        if (delay > 0) {
            if (ring_count > delay) {
                int from = (ring_at + TM_CTL_MAX_DELAY + 1 - delay) %
                           (TM_CTL_MAX_DELAY + 1);
                for (i = 0; i < 4; i++) {
                    if (head[i].err == PAD_ERR_NONE) {
                        s8 err = head[i].err;
                        head[i] = ring[from][i];
                        head[i].err = err;
                    }
                }
            } else {
                for (i = 0; i < 4; i++) {
                    if (head[i].err == PAD_ERR_NONE) {
                        memset(&head[i], 0, sizeof(head[i]));
                    }
                }
            }
        }
    }
    HSD_PadRenewMasterStatus();
}
