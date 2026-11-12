#ifndef MELEE_TM_OSDMISC_OSDMISC_H
#define MELEE_TM_OSDMISC_OSDMISC_H

#include <Runtime/platform.h>

#include <dolphin/mtx.h>
#include <melee/ft/forward.h>
#include <melee/it/forward.h>
#include <sysdolphin/baselib/forward.h>

/**
 * @file
 * TM-CE on-screen displays (osdmisc area): Combo Counter, L-Cancel,
 * Powershield, Jump Cancel, Grab Breakout, Boost Grab, Glide Toss, Airdodge
 * Item Throw, Yoshi Egg Toss and Bowser Fortress NIL
 * (../TrainingMode/ASM/training-mode/Onscreen Display/). Hooks:
 * config/GALE01/tm_hooks/osdmisc.txt. Built on src/melee/tm/osdcore/osd.h.
 */

/// @name src/tmce/osdmisc_bridge.c (MexTK side; fighters as void*)
/// @{
int tmce_osdmisc_StateFrames(void* fp);
int tmce_osdmisc_PrevState(void* fp);
int tmce_osdmisc_PrevStateFrames(void* fp);
void* tmce_osdmisc_GetAnimCallback(void* fp);
void tmce_osdmisc_SetAnimCallback(void* fp, void* cb);
int tmce_osdmisc_MatchFrames(void);
/// @}

/// @name Hook targets, osdmisc_osds.c
/// @{
void tm_osdmisc_LandingAirSetAnimRate(Fighter_GObj* gobj, float rate);
void tm_osdmisc_ScoreInitZero(void* mem, ssize_t size);
void tm_osdmisc_ShieldHitByItem(Item* item, HitCapsule* hit, Fighter* fp,
                                Vec3* pos, f32 val);
void tm_osdmisc_KneeBendIASA(Fighter_GObj* gobj);
void tm_osdmisc_CatchPullPhys(Fighter_GObj* gobj);
void tm_osdmisc_StartBoostGrab(Fighter_GObj* gobj, FtMotionId msid);
void tm_osdmisc_StartGlideToss(Fighter_GObj* gobj, FtMotionId msid);
bool tm_osdmisc_EscapeAirItemCheck(Fighter_GObj* gobj, bool* is_throw);
void tm_osdmisc_YoshiEggAccessory(Fighter_GObj* gobj);
void tm_osdmisc_FallSpecialLand(Fighter_GObj* gobj);
/// @}

/// @name Hook targets, osdmisc_combo.c
/// @{
void tm_osdmisc_ComboStat(int slot, int is_sub, int victim, int victim_sub,
                          int move_id, float damage);
HSD_GObjProc* tm_osdmisc_SetupProcAnim(HSD_GObj* gobj, HSD_GObjEvent func,
                                       u8 pri);
void tm_osdmisc_ItemHitStats(HSD_GObj* item_gobj, HSD_GObj* victim_gobj,
                             float damage);
void tm_osdmisc_SetAttackInstance(Fighter* fp, int arg1);
void tm_osdmisc_ThrowHit(Fighter_GObj* thrower, Fighter_GObj* victim,
                         float arg2);
/// @}

#endif
