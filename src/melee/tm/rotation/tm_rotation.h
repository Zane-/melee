#ifndef MELEE_TM_ROTATION_TM_ROTATION_H
#define MELEE_TM_ROTATION_TM_ROTATION_H

/*
 * Character rotation: one event, many opponents.
 *
 * An event lists scenarios in a deck. Each entry names the CPU character it
 * needs. When the match loads, the deck's characters are preloaded (up to
 * TM_ROT_MAX_CHARS, a random subset if there are more), so switching the
 * CPU's character between scenarios is instant: the old fighter is removed
 * and a new one spawned, the way vanilla Event Match brings in CPUs.
 *
 * Usage (TM-CE-style event, see src/tmce/events/shineoos.c):
 *   1. Define a `const TmRotDeck` and point the EventDesc's `.rotation` at
 *      it (src/tmce/custom_pages.c). Match setup preloads its characters.
 *   2. Pick the next entry: tm_rot_Next() (shuffle bag, every loaded entry
 *      once before any repeats), or choose one yourself.
 *   3. tm_rot_SetCpu(slot, entry->ckind, entry->color). If it returns 1 the
 *      CPU is a new fighter: re-fetch its GObj, re-place it, and take a new
 *      savestate before relying on old ones.
 *
 * This header is shared by native code (decomp headers) and TM-CE code
 * (MexTK headers), so it only uses plain C types. Character kinds are
 * external character ids (CKIND_* in MexTK, CharacterKind in the decomp).
 *
 * State is in overlay statics: not rollback-safe (offline events only).
 */

/// Characters preloaded per session besides the player's and the event's
/// own CPU: 4 different fighters in all, what a 4-player VS match loads.
/// 3 extra overflows the preload heap ("memp_kouho" in lbmemory.c) while
/// the files stream in (found with tools/tmtest.py soak runs).
#define TM_ROT_MAX_CHARS 2

typedef struct TmRotEntry {
    int ckind;        ///< external character id (CKIND_*)
    int color;        ///< costume
    const void* data; ///< event-specific scenario data
    const char* name; ///< shown in menus, e.g. "Marth - Down Tilt"
} TmRotEntry;

typedef struct TmRotDeck {
    const TmRotEntry* entries;
    int count;
} TmRotDeck;

/// Called by match setup (src/melee/tm/tm_event_start.c) for an event whose
/// EventDesc has a deck: picks this session's characters and preloads their
/// fighter files. Sound banks do not fit all at once; each swap loads the
/// new CPU's (and `stkind`'s). Also resets the shuffle bag.
void tm_rot_Preload(const TmRotDeck* deck, int stkind);

/// The deck of the current session, or NULL.
const TmRotDeck* tm_rot_Deck(void);

/// Whether entry `index` can be used this session (its character loaded).
int tm_rot_IsUsable(int index);

/// Next entry index from the shuffle bag, never the same as `previous`
/// unless it is the only usable entry. -1 if none is usable.
int tm_rot_Next(int previous);

/// Make `slot` a CPU of `ckind`/`color`. Returns 1 if the fighter was
/// replaced, 0 if it already was that character, -1 if the character is
/// not loaded. Keeps the slot's CPU level, team, stocks and damage.
int tm_rot_SetCpu(int slot, int ckind, int color);

#endif
