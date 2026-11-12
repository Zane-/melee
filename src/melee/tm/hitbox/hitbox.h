#ifndef MELEE_TM_HITBOX_H
#define MELEE_TM_HITBOX_H

#include <Runtime/platform.h>

#include <melee/ft/forward.h>
#include <melee/it/forward.h>
#include <melee/lb/forward.h>
#include <sysdolphin/baselib/forward.h>

/**
 * @file
 * TM-CE's hitbox visualizer (../TrainingMode/ASM/Additional Codes/Hitbox
 * Visualizer/ and Hide Player GFX When Hitboxes Enabled/), ported to C.
 * Hook table: config/GALE01/tm_hooks/hitbox.txt.
 *
 * Nothing here turns the display on: it is vanilla's per-fighter hitbox
 * flag (`Fighter::x21FC_flag.x0.b6`, MexTK FighterData.show_hit; items:
 * `Item::xDAA.xDAA_flag.x0.b6`), which the Lab's "Hitboxes" display option
 * sets (TM-CE lab.c) and develop mode toggles. These hooks only change how
 * hitboxes look while it is on.
 */

/// @name Hook targets: hb_draw.c (hitbox drawing)
/// @{
void tm_hitbox_FighterDrawColl(HSD_GObj* gobj, s32 arg1, bool arg2);
bool tm_hitbox_DrawItemHit(HitCapsule* hit, u32 arg1, float scale);
ItemKind tm_hitbox_ItemTopN(HSD_GObj* gobj);
void tm_hitbox_DrawSnapping(void);
/// @}

/// @name Hook targets: hb_gfx.c (Hide Player GFX When Hitboxes Enabled)
/// @{
void* tm_hitbox_efSync_Spawn(s32 gfx_id, HSD_GObj* gobj, ...);
void tm_hitbox_ApplyHits(Fighter_GObj* gobj, void* dmg_ptr, void* log,
                         size_t idx, int arg4);
/// @}

#endif
