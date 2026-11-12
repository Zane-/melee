#ifndef MELEE_TM_OSDACT_OSDACT_H
#define MELEE_TM_OSDACT_OSDACT_H

#include <Runtime/platform.h>

#include <melee/ft/forward.h>
#include <sysdolphin/baselib/forward.h>

/**
 * @file
 * TM-CE "act out of" on-screen displays (osdact area): Act OoAirborne, Act
 * OoShield, Act OoHitstun (Act OOTumble/) and Act OoFloat, from
 * ../TrainingMode/ASM/training-mode/Onscreen Display/. Hook targets for
 * config/GALE01/tm_hooks/osdact.txt; the display logic is MexTK-side, in
 * src/tmce/osdact_osds.c.
 */

/// @name src/tmce/osdact_osds.c (fighter GObj passed as void*)
/// @{
void tmce_osdact_OoAirborne(int interrupted, void* gobj, char* text,
                            int kind);
void tmce_osdact_ShieldFramesInc(void* gobj);
void tmce_osdact_ShieldFramesReset(void* gobj);
void tmce_osdact_OoShield(int interrupted, void* gobj);
void tmce_osdact_PostHitstunCount(void* gobj);
void tmce_osdact_OoHitstun(int interrupted, void* gobj);
int tmce_osdact_IsInFall(void* gobj);
void tmce_osdact_OoFloat(void* fp);
/// @}

/// @name Act OoAirborne (`call` hooks on the interrupt check before each
/// TM-CE site)
/// @{
bool tm_osdact_SpecialOoJump(Fighter_GObj* gobj);
bool tm_osdact_AerialOoJump(Fighter_GObj* gobj);
bool tm_osdact_DblJumpOoJump(Fighter_GObj* gobj);
bool tm_osdact_SpecialOoDblJump(Fighter_GObj* gobj);
bool tm_osdact_AerialOoDblJump(Fighter_GObj* gobj);
bool tm_osdact_SpecialOoFall(Fighter_GObj* gobj);
bool tm_osdact_AerialOoFall(Fighter_GObj* gobj);
bool tm_osdact_SpecialOoDrop(Fighter_GObj* gobj);
bool tm_osdact_AerialOoDrop(Fighter_GObj* gobj);
/// @}

/// @name Act OOS
/// @{
bool tm_osdact_GuardAnimCheck(Fighter_GObj* gobj);
bool tm_osdact_GuardOffAnimCheck(Fighter_GObj* gobj);
bool tm_osdact_GuardSetOffAnimCheck(Fighter_GObj* gobj);
void tm_osdact_Guard_IASA(Fighter_GObj* gobj);
void tm_osdact_GuardOff_IASA(Fighter_GObj* gobj);
/// @}

/// @name Act OoHitstun (Act OOTumble/)
/// @{
void tm_osdact_ProcAnimDamage(Fighter_GObj* gobj);
bool tm_osdact_DamageDoubleJump(Fighter_GObj* gobj);
bool tm_osdact_DamageFallIasa(Fighter_GObj* gobj);
void tm_osdact_DamageWaitIasa(Fighter_GObj* gobj);
bool tm_osdact_DFSpecialAir(Fighter_GObj* gobj);
bool tm_osdact_DF80095328(Fighter_GObj* gobj, bool* arg1);
bool tm_osdact_DF800D7100(Fighter_GObj* gobj);
bool tm_osdact_DF800C3B10(Fighter_GObj* gobj);
bool tm_osdact_DFAttackAir(Fighter_GObj* gobj);
bool tm_osdact_DF800D705C(Fighter_GObj* gobj);
bool tm_osdact_DF800CB870(Fighter_GObj* gobj);
void tm_osdact_DFFallEnter(Fighter_GObj* gobj);
bool tm_osdact_DF800C5DDC(Fighter_GObj* gobj);
bool tm_osdact_DF800C5CD4(Fighter_GObj* gobj);
/// @}

/// @name Act OoFloat
/// @{
bool tm_osdact_PeachFloatAttack(HSD_GObj* gobj);
/// @}

#endif
