#include "tm_rotation.h"

#include <melee/gm/gmvs.h>
#include <melee/gm/types.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/lb/lbdvd.h>
#include <melee/lb/types.h>
#include <melee/mn/types.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/random.h>

/**
 * @file
 * Character rotation (see tm_rotation.h).
 *
 * Preloading uses the game cache the way All-Star mode loads its next
 * opponents (gmallstar.c): characters go into free entries of
 * lbDvd_GetPreloadCacheScene()->game_cache, lbDvd_80018254 commits them, and
 * the sound banks are requested with lbAudioAx_8002702C. The scene then
 * waits for them before the match starts.
 *
 * Swapping uses the functions vanilla VS/Event mode uses to remove and add a
 * fighter mid-match: fn_8016EF98 and gm_8016EDDC.
 */

#define ROT_MAX_ENTRIES 64
#define CACHE_ENTRIES 8

typedef struct RotState {
    const TmRotDeck* deck;
    int stkind;
    int loaded[TM_ROT_MAX_CHARS + 2]; ///< ckinds loaded this session
    int loaded_num;
    u8 bag[ROT_MAX_ENTRIES];          ///< shuffled entry indices
    int bag_num;
    int bag_pos;
} RotState;

static RotState rot;

static bool rotIsLoaded(int ckind)
{
    int i;
    for (i = 0; i < rot.loaded_num; i++) {
        if (rot.loaded[i] == ckind) {
            return true;
        }
    }
    return false;
}

static void rotShuffle(void)
{
    int i;
    rot.bag_num = 0;
    rot.bag_pos = 0;
    if (rot.deck == NULL) {
        return;
    }
    for (i = 0; i < rot.deck->count && i < ROT_MAX_ENTRIES; i++) {
        if (tm_rot_IsUsable(i)) {
            rot.bag[rot.bag_num++] = i;
        }
    }
    /* Fisher-Yates */
    for (i = rot.bag_num - 1; i > 0; i--) {
        int j = HSD_Randi(i + 1);
        u8 t = rot.bag[i];
        rot.bag[i] = rot.bag[j];
        rot.bag[j] = t;
    }
}

void tm_rot_Preload(const TmRotDeck* deck, int stkind)
{
    struct GameCache* gc = &lbDvd_GetPreloadCacheScene()->game_cache;
    int wanted[ROT_MAX_ENTRIES];
    int wanted_num = 0;
    int extra_num = 0;
    int i, j;

    rot.deck = deck;
    rot.loaded_num = 0;
    if (deck == NULL) {
        rotShuffle();
        return;
    }

    /* Characters already in the cache (the player's, the event's CPU)
     * count as loaded. */
    for (i = 0; i < CACHE_ENTRIES; i++) {
        if (gc->entries[i].char_id != ChKind_None &&
            rot.loaded_num < TM_ROT_MAX_CHARS + 2)
        {
            rot.loaded[rot.loaded_num++] = gc->entries[i].char_id;
        }
    }

    /* Distinct deck characters not loaded yet. */
    for (i = 0; i < deck->count; i++) {
        int ckind = deck->entries[i].ckind;
        bool dup = rotIsLoaded(ckind);
        for (j = 0; j < wanted_num && !dup; j++) {
            dup = wanted[j] == ckind;
        }
        if (!dup && wanted_num < ROT_MAX_ENTRIES) {
            wanted[wanted_num++] = ckind;
        }
    }

    /* Random subset if there are more than fit (Fisher-Yates prefix). */
    for (i = 0; i < wanted_num && i < TM_ROT_MAX_CHARS; i++) {
        int k = i + HSD_Randi(wanted_num - i);
        int t = wanted[i];
        wanted[i] = wanted[k];
        wanted[k] = t;
    }

    for (i = 0; i < CACHE_ENTRIES && extra_num < wanted_num &&
                extra_num < TM_ROT_MAX_CHARS;
         i++)
    {
        if (gc->entries[i].char_id == ChKind_None) {
            int ckind = wanted[extra_num++];
            int color = 0;
            for (j = 0; j < deck->count; j++) {
                if (deck->entries[j].ckind == ckind) {
                    color = deck->entries[j].color;
                    break;
                }
            }
            gc->entries[i].char_id = ckind;
            gc->entries[i].color = color;
            rot.loaded[rot.loaded_num++] = ckind;
        }
    }
    lbDvd_80018254();

    /* Sound banks are NOT preloaded: Melee's sound memory only fits a normal
     * match ("FGM load size is over"). tm_rot_SetCpu swaps them instead. */
    rot.stkind = stkind;
    rotShuffle();
}

/// Request the sound banks of the fighters now in the match and the stage,
/// the way All-Star does between rounds; the old CPU's bank is dropped.
static void rotLoadSounds(void)
{
    u64 audio = 0;
    int slot;
    for (slot = 0; slot < 6; slot++) {
        if (Player_GetEntity(slot) != NULL) {
            audio |= lbAudioAx_80026E84(Player_GetPlayerCharacter(slot));
        }
    }
    audio |= lbAudioAx_80026EBC(rot.stkind);
    lbAudioAx_80026F2C(0x1C);
    lbAudioAx_8002702C(0xC, audio);
    lbAudioAx_80027168();
}

const TmRotDeck* tm_rot_Deck(void)
{
    return rot.deck;
}

int tm_rot_IsUsable(int index)
{
    if (rot.deck == NULL || index < 0 || index >= rot.deck->count) {
        return false;
    }
    return rotIsLoaded(rot.deck->entries[index].ckind);
}

int tm_rot_Next(int previous)
{
    int tries;
    for (tries = 0; tries < 2; tries++) {
        if (rot.bag_pos >= rot.bag_num) {
            rotShuffle();
            if (rot.bag_num == 0) {
                return -1;
            }
        }
        if (rot.bag[rot.bag_pos] == previous && rot.bag_num > 1) {
            /* Avoid an immediate repeat across a reshuffle. */
            int k = rot.bag_pos + 1 < rot.bag_num ? rot.bag_pos + 1 : 0;
            u8 t = rot.bag[rot.bag_pos];
            rot.bag[rot.bag_pos] = rot.bag[k];
            rot.bag[k] = t;
        }
        return rot.bag[rot.bag_pos++];
    }
    return -1;
}

int tm_rot_SetCpu(int slot, int ckind, int color)
{
    struct PlayerInitData init = { 0 };

    if (Player_GetPlayerCharacter(slot) == ckind &&
        (int) Player_GetCostumeId(slot) == color)
    {
        return 0;
    }
    if (!rotIsLoaded(ckind)) {
        return -1;
    }

    init.ckind = ckind;
    init.slot_type = Gm_PKind_Cpu;
    init.stocks = Player_GetStocks(slot);
    init.color = color;
    init.slot = Player_GetPadPort(slot) + 1;
    init.spawn_pos = slot;
    init.sub_color = 0;
    init.handicap = Player_GetHandicap(slot);
    init.team = Player_GetTeam(slot);
    init.nametag = Player_GetNametagSlotID(slot);
    init.cpu_kind = Player_GetCpuType(slot);
    init.cpu_level = Player_GetCpuLevel(slot);
    init.damage1 = Player_GetDamage(slot);
    init.attack_ratio = Player_GetAttackRatio(slot);
    init.defense_ratio = Player_GetDefenseRatio(slot);
    init.model_scale = 1.0F;

    if (!fn_8016EF98(slot)) {
        return -1;
    }
    if (!gm_8016EDDC(slot, &init)) {
        return -1;
    }
    rotLoadSounds();
    return 1;
}
