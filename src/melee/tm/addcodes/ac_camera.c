/**
 * @file
 * TM-CE Additional Codes: Enable C Stick Always/ (the camera half) and
 * Better Camera/. The one-word parts are in config/GALE01/tm_hooks/
 * addcodes.txt.
 *
 * Develop-mode camera (db/dbcamera.c): the C-stick only takes over the
 * camera while D-pad Down is held, and R held slows pan, rotate and zoom.
 * Pause camera (cm/camera.c): the C-stick pans it, it is not clamped to the
 * stage while the pausing player is alive, and in non-Training modes its
 * angle limits are lifted.
 */
#include "addcodes.h"

#include <math.h>
#include <dolphin/mtx.h>
#include <melee/cm/camera.h>
#include <melee/cm/types.h>
#include <melee/db/db.h>
#include <melee/ft/fighter.h>
#include <melee/ft/types.h>
#include <melee/gm/gm_unsplit.h>
#include <melee/gm/gmvs.h>
#include <melee/gm/types.h>
#include <melee/gr/stage.h>
#include <melee/lb/lbvector.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/cobj.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/gobj.h>

/// cm/camera.c, gm/gmvs.c, db/dbcamera.c statics (unique names).
extern Camera game_camera;
extern VsSceneController controller;
extern u8 db_CameraInfoDisplayTimer;
void fn_80227B64(HSD_GObj* camera, f32 x, f32 y);

/// The pad bit TM-CE tests for "D-pad Down" (rlwinm 29,29).
#define AC_PAD_DPADDOWN 0x0004
/// PAD_TRIGGER_R.
#define AC_PAD_R 0x0020

static inline bool acDpadDown(int port)
{
    return (HSD_PadMasterStatus[(u8) port].button & AC_PAD_DPADDOWN) != 0;
}

/// TM-CE's Slow Camera With R: any of the four pads holding R.
static inline bool acAnyPadR(void)
{
    u32 buttons = 0;
    int i;
    for (i = 0; i < 4; i++) {
        buttons |= HSD_PadMasterStatus[i].button;
    }
    return (buttons & AC_PAD_R) != 0;
}

static inline f32 acCstickThreshold(f32 cstick, f32 val)
{
    if (ABS(cstick) < val) {
        return 0;
    }
    return cstick;
}

/// Wraps the only call of fn_CheckCameraInfo (db_RunEveryFrame+0x1B4).
///
/// Enable C Stick Always/Rotate Camera with Dpad Down and C Stick -
/// Initiate.asm (fn_CheckCameraInfo+0x6C): the C-stick only switches to the
/// develop camera while D-pad Down is held; otherwise TM-CE jumps to the
/// D-pad Up check. The stick values are only used by that test, so passing
/// zero is the same thing.
void tm_ac_CheckCameraInfo(int player, int buttons_down, int buttons_pressed,
                           f32 cstick_x, f32 cstick_y)
{
    if (!acDpadDown(player)) {
        cstick_x = 0.0F;
        cstick_y = 0.0F;
    }
    fn_CheckCameraInfo(player, buttons_down, buttons_pressed, cstick_x,
                       cstick_y);
}

/// Replaces fn_80227904 (`function` hook; "Debug_UpdateCamera").
///
/// Enable C Stick Always/Rotate Camera with Dpad Down and C Stick.asm
/// (fn_80227B64+0xC): free-camera rotation only while D-pad Down is held.
/// fn_80227B64 has no other caller, so the check sits here, where the port
/// is known (TM-CE read it from the caller's r5).
void tm_ac_DebugUpdateCamera(HSD_GObj* camera, int port)
{
    f32 cstick_x;
    f32 cstick_y;
    u32 buttons;

    port &= 0xFF;

    cstick_x =
        acCstickThreshold(HSD_PadMasterStatus[port].nml_subStickX, 0.2F);
    cstick_y =
        acCstickThreshold(HSD_PadMasterStatus[port].nml_subStickY, 0.2F);

    buttons = HSD_PadMasterStatus[port].button;

    if (buttons & 1) {
        tm_ac_FreecamDolly(camera, cstick_y);
    } else if (buttons & 2) {
        tm_ac_FreecamPosition(camera, -cstick_x, -cstick_y);
    } else if (acDpadDown(port)) {
        fn_80227B64(camera, cstick_x, cstick_y);
    }
    db_CameraInfoDisplayTimer = 0x3C;
}

/// Replaces fn_80227FE0 (`function` hook; "Debug_UpdateFreecamPosition").
/// Better Camera/Slow Camera With R - Pan.asm (+0x6C): the 2.0 factor
/// becomes 0.2 while R is held.
void tm_ac_FreecamPosition(HSD_GObj* camera, f32 cstick_x, f32 cstick_y)
{
    Vec3 up_vec;
    Vec3 left_vec;
    f32 eye_dist;
    f32 scale_factor;
    f32 speed = acAnyPadR() ? 0.2F : 2.0F;
    HSD_CObj* cobj;

    if ((cstick_x != 0.0F) || (cstick_y != 0.0F)) {
        cobj = GET_COBJ(camera);
        eye_dist = HSD_CObjGetEyeDistance(cobj);
        scale_factor =
            0.03F *
            (speed * (eye_dist * tanf(MTXDegToRad(HSD_CObjGetFov(cobj)) / 2)));
        if (cstick_x != 0.0F) {
            HSD_CObjGetLeftVector(cobj, &left_vec);
            PSVECScale(&left_vec, &left_vec, scale_factor * cstick_x);
            PSVECAdd(&cm_80453004.free_int_pos, &left_vec,
                     &cm_80453004.free_int_pos);
            PSVECAdd(&cm_80453004.free_eye_pos, &left_vec,
                     &cm_80453004.free_eye_pos);
        }
        if (cstick_y != 0.0F) {
            HSD_CObjGetUpVector(cobj, &up_vec);
            PSVECScale(&up_vec, &up_vec, -scale_factor * cstick_y);
            PSVECAdd(&cm_80453004.free_int_pos, &up_vec,
                     &cm_80453004.free_int_pos);
            PSVECAdd(&cm_80453004.free_eye_pos, &up_vec,
                     &cm_80453004.free_eye_pos);
        }
    }
}

/// Replaces fn_802279E8 (`function` hook; "Debug_OrbitAroundInterest").
///
/// Better Camera/Slow Camera With R - Rotate.asm (+0xDC): the
/// degrees-to-radians factor becomes 0.001745 while R is held. TM-CE wrote
/// its value into the shared vanilla .sdata2 constant (and used 0.01745
/// rather than 0.017453292 when R is up); here it is a local, so no other
/// reader of that constant is affected.
void tm_ac_OrbitAroundInterest(HSD_GObj* camera, Vec3* camera_pos,
                               Vec3* camera_interest, f32 cstick_x,
                               f32 cstick_y)
{
    HSD_CObj* cobj;
    Mtx mtx;
    Vec3 forward_vec;
    Vec3 axis;
    f32 eye_dist;
    f32 pitch;
    f32 new_pitch;
    f32 to_rad = acAnyPadR() ? 0.001745F : 0.017453292F;

    cobj = GET_COBJ(camera);
    if ((cstick_x != 0.0F) || (cstick_y != 0.0F)) {
        Vec3 up_vec = { 0, 1, 0 };
        HSD_CObjGetEyeVector(cobj, &forward_vec);
        pitch = 57.29578F * acosf(PSVECDotProduct(&forward_vec, &up_vec));
        new_pitch = 2.0F * cstick_y;
        if ((pitch + new_pitch) > 179.0F) {
            new_pitch = 179.0F - pitch;
        }
        if ((pitch + new_pitch) < 1.0F) {
            new_pitch = 1.0F - pitch;
        }
        PSVECCrossProduct(&up_vec, &forward_vec, &axis);
        PSVECNormalize(&axis, &axis);
        PSMTXRotAxisRad(mtx, &axis, to_rad * new_pitch);
        PSMTXMultVec(mtx, &forward_vec, &forward_vec);
        eye_dist = HSD_CObjGetEyeDistance(cobj);
        PSMTXRotAxisRad(mtx, &up_vec, to_rad * (2.0F * cstick_x));
        PSMTXMultVec(mtx, &forward_vec, &forward_vec);
        PSVECScale(&forward_vec, &forward_vec, eye_dist);
        PSVECSubtract(camera_interest, &forward_vec, camera_pos);
    }
}

/// Replaces fn_80227CAC (`function` hook; "Debug_UpdateFreecamDolly").
/// Better Camera/Slow Camera With R - Zoom.asm (+0x40): 0.05 becomes 0.005
/// while R is held.
void tm_ac_FreecamDolly(HSD_GObj* camera, f32 cstick_y)
{
    Vec3 forward;
    HSD_CObj* cobj;
    f32 speed = acAnyPadR() ? 0.005F : 0.05F;

    if (cstick_y != 0.0F) {
        cobj = GET_COBJ(camera);
        HSD_CObjGetEyeVector(cobj, &forward);
        {
            float dist = HSD_CObjGetEyeDistance(cobj);
            PSVECScale(&forward, &forward, dist * (1.0F - speed * cstick_y));
        }
        PSVECSubtract(&cm_80453004.free_int_pos, &forward,
                      &cm_80453004.free_eye_pos);
    }
}

/// The instruction after TM-CE's C-Stick Pans Camera site. Slippi's
/// required General Codes put their own "C-Stick Panning while Paused
/// [Achilles]" there (a C2 inject, so the word becomes a branch).
#define AC_CAMERA_8002CB0C_SLIPPI_SITE 0x28
#define AC_VANILLA_8002CB34 0x7C040774 /* extsb r4, r0 */

/// Wraps `Camera_8002B694(&inputs, pauser)` in Camera_8002CB0C (+0x38),
/// the pause camera update.
///
/// Better Camera/C-Stick Pans Camera.asm (+0x24): the pausing player's
/// C-stick pans the pause camera, scaled by its zoom. Skipped when Slippi's
/// own pause-camera C-stick pan is installed, so it never pans twice. TM-CE
/// ran this before the "nobody paused" check and then read pad 5 (past the
/// end); here it runs only for a real pauser.
void tm_ac_PauseCamInputs(void* inputs, s8 slot)
{
    if (*(u32*) ((u8*) Camera_8002CB0C + AC_CAMERA_8002CB0C_SLIPPI_SITE) ==
        AC_VANILLA_8002CB34)
    {
        HSD_PadStatus* pad = &HSD_PadMasterStatus[(u8) game_camera.x2C5];
        f32 deadzone = p_ftCommonData->horizontal_stick_deadzone;
        f32 scale = game_camera.pause_eye_distance / 125.0F;
        f32 stick;

        stick = pad->nml_subStickY;
        if (stick <= -deadzone || stick >= deadzone) {
            game_camera.x314.y += stick * scale;
        }
        stick = pad->nml_subStickX;
        if (stick <= -deadzone || stick >= deadzone) {
            game_camera.x314.x += stick * scale;
        }
    }
    Camera_8002B694(inputs, slot);
}

/// Wraps `Stage_GetPauseCamZPosMax()` in Camera_SetUpPauseCamera (+0xE0).
///
/// Better Camera/Unrestricted Camera.asm (+0xE8, the store of its result):
/// while debug pause flag 1 is set and the mode is not Training, the pause
/// camera's angle limits and its far zoom are 32768 and its near zoom 0.
f32 tm_ac_PauseCamZPosMax(void)
{
    f32 z_max = Stage_GetPauseCamZPosMax();

    if (gm_GetDbPauseFlag(1) && gm_GetCurrentGameMode() != GM_TRAINING) {
        game_camera.x2D0.angle_up = 32768.0F;
        game_camera.x2D0.angle_down = 32768.0F;
        game_camera.x2D0.angle_right = 32768.0F;
        game_camera.x2D0.angle_left = 32768.0F;
        game_camera.x2D0.unk28 = 0.0F;
        z_max = 32768.0F;
    }
    return z_max;
}

/// TM-CE's SnapToOffscreenPlayers test: the player whose port paused the
/// game exists and is not flagged dead (x221F bit 0x40).
static bool acPauserAlive(void)
{
    s8 pauser = controller.state.pauser;
    int slot;

    for (slot = 0; slot < 4; slot++) {
        HSD_GObj* gobj = Player_GetEntity(slot);
        if (gobj != NULL && Player_GetPadPort(slot) == pauser) {
            Fighter* fp = GET_FIGHTER(gobj);
            return !fp->x221F_b1;
        }
    }
    return false;
}

/// Wraps `Camera_80029124(&subject->bone_pos, 0)` in Camera_8002CDDC
/// (+0x158), the "is the pauser on screen" test.
///
/// Better Camera/SnapToOffscreenPlayers/Always Onscreen.asm: TM-CE replaces
/// the call with "inside" (0) while the pausing player is alive, 1 otherwise.
int tm_ac_PauserOnscreen(Vec3* pos, int arg1)
{
    return acPauserAlive() ? CAM_BOUNDS_INSIDE : 1;
}

/// Replaces Camera_8002C5B4 (`function` hook), which clamps the pause
/// camera's focus and pan to the stage bounds and limits its angles.
///
/// - SnapToOffscreenPlayers/Snap.asm (+0x3C): while the pausing player is
///   alive, the focus (x308) is not clamped.
/// - CStickPanOffscreen/{Right,Left,Top,Bottom}.asm (+0xF4/+0x108/+0x11C/
///   +0x130): the clamps of focus + pan are not stored, so the C-stick can
///   pan off the stage.
/// The rest is vanilla (the unused eye-offset length is left out).
void tm_ac_PauseCamClamp(void* arg0)
{
    Vec3 temp_pos;
    Vec3 cross1;
    Vec3 cross2;
    Camera* cam = &game_camera;
    Camera_x2D0* params = arg0;
    Vec3* cam_pos = &cam->x308;
    Vec3* cam_offset = &cam->x314;
    Vec3* eye_offset;
    f32 xz_dist;
    f32 pitch;
    f32 yaw;

    if (params->callback != NULL) {
        params->callback(arg0);
    }

    if (!acPauserAlive()) {
        if (cam_pos->x > params->x_max) {
            cam_pos->x = params->x_max;
        } else if (cam_pos->x < params->x_min) {
            cam_pos->x = params->x_min;
        }
        if (cam_pos->y > params->y_max) {
            cam_pos->y = params->y_max;
        } else if (cam_pos->y < params->y_min) {
            cam_pos->y = params->y_min;
        }
        if (cam_pos->z > params->z_max) {
            cam_pos->z = params->z_max;
        } else if (cam_pos->z < params->z_min) {
            cam_pos->z = params->z_min;
        }
    }

    temp_pos = *cam_offset;
    lbVector_Add(&temp_pos, cam_pos);
    /* x and y clamps removed (CStickPanOffscreen). */
    if (temp_pos.z > params->z_max) {
        temp_pos.z = params->z_max;
    } else if (temp_pos.z < params->z_min) {
        temp_pos.z = params->z_min;
    }
    lbVector_Sub(&temp_pos, cam_pos);
    *cam_offset = temp_pos;

    eye_offset = &cam->pause_eye_offset;
    xz_dist = sqrtf(eye_offset->x * eye_offset->x +
                    eye_offset->z * eye_offset->z);

    PSVECCrossProduct(eye_offset, &cam->pause_up, &cross1);
    lbVector_Normalize(&cross1);
    PSVECCrossProduct(&cross1, eye_offset, &cross2);
    lbVector_Normalize(&cross2);

    pitch = atan2f(eye_offset->y, xz_dist);
    if (pitch > params->angle_down) {
        lbVector_RotateAboutUnitAxis(eye_offset, &cross1,
                                     params->angle_down - pitch);
    } else if (pitch < -params->angle_up) {
        lbVector_RotateAboutUnitAxis(eye_offset, &cross1,
                                     -params->angle_up - pitch);
    }

    yaw = atan2f(eye_offset->x, eye_offset->z);
    if (yaw > params->angle_right) {
        lbVector_RotateAboutUnitAxis(eye_offset, &cross2,
                                     params->angle_right - yaw);
    } else if (yaw < -params->angle_left) {
        lbVector_RotateAboutUnitAxis(eye_offset, &cross2,
                                     -params->angle_left - yaw);
    }
}
