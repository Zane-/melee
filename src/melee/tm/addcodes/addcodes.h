#ifndef MELEE_TM_ADDCODES_H
#define MELEE_TM_ADDCODES_H

#include <Runtime/platform.h>

#include <dolphin/mtx.h>
#include <melee/gm/forward.h>
#include <sysdolphin/baselib/forward.h>

/**
 * @file
 * TM-CE's Additional Codes (../TrainingMode/ASM/Additional Codes) and m-ex's
 * UCF, ported to C. Hook table: config/GALE01/tm_hooks/addcodes.txt.
 */

/// Boot straight into the Training Lab (Event Match, TM-CE page "General
/// Tech", Lab's character select) instead of the menus. An extension of
/// TM-CE's Boot to Event Mode codes, asked for by the owner. Set to 0 for
/// TM-CE's behaviour (boot to the main menu, cursor on Event Match).
/// Either way, holding X at boot goes to the VS character select (TM-CE),
/// and holding Y goes to the main menu.
#ifndef TM_AC_BOOT_TO_LAB
#define TM_AC_BOOT_TO_LAB 1
#endif

/// Event file (EventDesc.eventFile) to boot into when TM_AC_BOOT_TO_LAB is
/// set. Test builds override it with a bare token (quotes do not survive
/// the compiler wrapper), e.g.
/// `TM_DEFINES='TM_AC_BOOT_EVENT=shineoos' tools/overlay_build.py`.
#define TM_AC_STR_(x) #x
#define TM_AC_STR(x) TM_AC_STR_(x)
#ifdef TM_AC_BOOT_EVENT
#define TM_AC_BOOT_EVENT_FILE TM_AC_STR(TM_AC_BOOT_EVENT)
#else
#define TM_AC_BOOT_EVENT_FILE "course"
#endif

/// @name Hook targets: ac_camera.c (Enable C Stick Always, Better Camera)
/// @{
void tm_ac_CheckCameraInfo(int player, int buttons_down, int buttons_pressed,
                           f32 cstick_x, f32 cstick_y);
void tm_ac_DebugUpdateCamera(HSD_GObj* camera, int port);
void tm_ac_FreecamPosition(HSD_GObj* camera, f32 cstick_x, f32 cstick_y);
void tm_ac_OrbitAroundInterest(HSD_GObj* camera, Vec3* camera_pos,
                               Vec3* camera_interest, f32 cstick_x,
                               f32 cstick_y);
void tm_ac_FreecamDolly(HSD_GObj* camera, f32 cstick_y);
void tm_ac_PauseCamInputs(void* inputs, s8 slot);
f32 tm_ac_PauseCamZPosMax(void);
int tm_ac_PauserOnscreen(Vec3* pos, int arg1);
void tm_ac_PauseCamClamp(void* params);
/// @}

/// @name Hook targets: ac_draw.c (debug drawing)
/// @{
struct HurtCapsule;
bool tm_ac_DrawHurtbox(struct HurtCapsule* hurt, u32 arg1, Mtx arg2,
                       float arg3);
void tm_ac_DrawCollisionLinks(u8 arg0);
/// @}

/// @name Hook targets: ac_engine.c (frame loop)
/// @{
struct TmRegs;
void tm_ac_ForceGameLoop(struct TmRegs* regs);
/// @}

/// @name Hook targets: ac_misc.c
/// @{
void* tm_ac_StageDataAlloc(u32 size);
void tm_ac_BootDisableItemSpawns(void);
void tm_ac_BootEnableItemSpawns(void);
void tm_ac_FighterReflections(void);
/// @}

/// @name Hook targets: ac_boot.c (Boot to Event Mode, boot to the Lab)
/// @{
void tm_ac_BootChangeMode(u8 mode);
void tm_ac_MemCardExit(int arg0);
void tm_ac_MemCardEnter(void);
/// @}

#endif
