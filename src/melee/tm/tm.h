#ifndef MELEE_TM_TM_H
#define MELEE_TM_TM_H

#include <Runtime/platform.h>

#include <sysdolphin/baselib/forward.h>

/**
 * @file
 * Training-mode core: state roots and the vanilla entry points.
 *
 * Overlay code may not have writable statics (see docs/ai/overlay-build.md).
 * All state hangs off two roots:
 *
 * - #tm_persist: survives scene changes. Lives in a reserved block below the
 *   overlay that Slippi's rollback does NOT save. Only for things that never
 *   change during a match, or that are display-only.
 * - #tm_state: per-match state, allocated from the scene heap when a match
 *   starts, so rollback saves and restores it. NULL outside a match.
 */

#define TM_VERSION_SHORT "TM-Native v0.1"

#define TM_PERSIST_MAGIC 0x544D4E31 /* 'TMN1' */

/// Size reserved for #TmPersist by the overlay build (tools/overlay_build.py).
#define TM_PERSIST_RESERVED 0x1000

typedef struct TmPersist {
    /* +00 */ u32 magic;       ///< #TM_PERSIST_MAGIC once initialised
    /* +04 */ u32 scene_count; ///< scenes entered since boot
    /* +08 */ u32 match_count; ///< matches started since boot
    /* +0C */ HSD_Text* watermark; ///< valid for the current scene only
    /* +10 */ u8 event_page;   ///< selected page (index into tm_event_pages)
    /* +11 */ u8 event_index;  ///< selected event within the page
    /* +12 */ u8 event_active; ///< an event was chosen on the event select
                               ///< screen and owns the next Training match
    /* +13 */ u8 pad_13;
} TmPersist;

typedef struct TmMatch {
    /* +00 */ u32 frame;          ///< game frames since match start
    /* +04 */ HSD_GObj* think_gobj; ///< runs #tm_Match_Think every frame
    /* +08 */ HSD_GObj* menu_gobj;  ///< pause menu, or NULL (tm_menu.h)
    /* +0C */ HSD_GObj* event_gobj; ///< running event, or NULL (tm_event.h)
    /* +10 */ const struct TmEventDesc* event_desc;
} TmMatch;

/// Absolute symbol from config/GALE01/tm_symbols.txt.
extern TmPersist tm_persist;

/// Absolute symbol from config/GALE01/tm_symbols.txt (4 spare bytes of
/// vanilla .sbss inside the range Slippi's rollback saves).
extern TmMatch* tm_state;

/// @name Hook targets
/// Wired in config/GALE01/tm_hooks.txt. Each `call` target has the signature
/// of the vanilla function it wraps and calls it first.
/// @{
void tm_Hook_Boot(void);
void tm_Hook_SceneChange(void);
void tm_Hook_StartMelee(int arg);
/// @}

#endif
