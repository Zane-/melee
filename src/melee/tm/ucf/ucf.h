#ifndef MELEE_TM_UCF_UCF_H
#define MELEE_TM_UCF_UCF_H

#include <Runtime/platform.h>
#include <melee/ft/forward.h>

/**
 * @file
 * UCF 0.84 (Universal Controller Fix), in C.
 *
 * UCF is eight small changes to how the game reads the control stick, so
 * that controllers whose sticks report slightly different values all get
 * the same dash back, shield drop, SDI, tumble wiggle and cardinal
 * directions. Tournaments and Slippi run it as assembly injected into eight
 * vanilla functions (Slippi's "Required: General Codes").
 *
 * This build must not patch those addresses, so the same rules are written
 * here in C, read from the code Slippi ships, and reached through the calls
 * and table slots that lead to those functions (config/GALE01/tm_hooks/
 * ucf.txt). When any of the eight sites does not hold the original
 * instruction, someone else (Slippi Dolphin) has put UCF there: everything
 * here then steps aside and the vanilla functions run with that code in
 * them, so the game is never fixed twice.
 *
 * tests/sim/ucf.py runs the same inputs through this code and through
 * Slippi's and compares the fighters frame by frame.
 */

/// Whether this file's UCF is the one in effect: all eight sites hold the
/// vanilla instruction and #tm_ucf_off is clear.
bool tm_ucf_Active(void);

/// Set to turn this file's UCF off (the vanilla game; tests use it). The
/// native build has this file too, on unless the driver's `ucf 0` says
/// otherwise (src/host/ucf.c).
extern u8 tm_ucf_off;

/// @name `call` hooks in Fighter_procInput
/// @{
bool tm_ucf_IsCpuControlled(Fighter* fp);
s32 tm_ucf_8000D148(float, float, float, float, float, float, float);
/// @}

/// @name In place of the vanilla function of the same name, wherever it is
/// called or listed
/// @{
void tm_ucf_Turn_IASA(Fighter_GObj* gobj);
void tm_ucf_DamageFall_IASA(Fighter_GObj* gobj);
bool tm_ucf_SquatRv_CheckInput(Fighter_GObj* gobj);
bool tm_ucf_80099794(Fighter_GObj* gobj);
bool tm_ucf_8009980C(Fighter_GObj* gobj);
bool tm_ucf_8009A080(Fighter_GObj* gobj);
/// @}

/// Called right before a fighter's hitlag callback (osdtech's wrapper of
/// the call before it): SDI and shield SDI.
void tm_ucf_PreHitlag(Fighter_GObj* gobj);

#endif
