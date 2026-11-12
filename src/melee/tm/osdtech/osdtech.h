#ifndef MELEE_TM_OSDTECH_OSDTECH_H
#define MELEE_TM_OSDTECH_OSDTECH_H

#include <Runtime/platform.h>

#include <melee/ft/forward.h>

/**
 * @file
 * TM-CE OSDs: Dashback, Ledge Codes (CliffWait, Ledgestall, GALINT),
 * Wavedash Display and SDI Display. Native hooks (osdtech.c, wired in
 * config/GALE01/tm_hooks/osdtech.txt); the display logic is TM-CE side in
 * src/tmce/osdtech_osd.c.
 */

/// @name Hook targets
/// Each `call` target has the signature of the vanilla function it wraps.
/// @{
void tm_osdtech_DashEnter(Fighter_GObj* gobj, int arg1);
void tm_osdtech_CliffFallEnter(Fighter_GObj* gobj);
void tm_osdtech_CliffCatchSFX(Fighter* fp, enum_t id, u8 vol, u8 pan);
void tm_osdtech_LandingAirBasic(Fighter_GObj* gobj);
void tm_osdtech_AirCatchLand(Fighter_GObj* gobj);
void tm_osdtech_LandingAnimLand(Fighter_GObj* gobj);
void tm_osdtech_NoImpactLand(Fighter_GObj* gobj);
void tm_osdtech_EscapeAirEnter(Fighter_GObj* gobj, int timer);
void tm_osdtech_EscapeAirLand(Fighter_GObj* gobj, bool allow_interrupt,
                              float landing_lag);
void tm_osdtech_DamageEnter(Fighter_GObj* gobj);
void tm_osdtech_PreHitlagCallback(Fighter_GObj* gobj);
/// @}

#endif
