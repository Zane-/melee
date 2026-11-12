/**
 * @file
 * Edited copies of two vanilla fighter functions for TM-CE's per-fighter
 * variables (osdcore area). Both are `function` hooks in
 * config/GALE01/tm_hooks/osdcore.txt; Slippi patches neither.
 *
 * - tm_osd_ChangeMotionState: Fighter_ChangeMotionState (ft/fighter.c),
 *   plus StatesAndTimers/ShiftStates.asm (+0x40) and Fastfall Timer/
 *   Initialize Fastfall Variable.asm (+0x51C). Neither site is next to a
 *   call, and the state being left is overwritten right after the first.
 *   Any other hook inside vanilla Fighter_ChangeMotionState is dead while
 *   this is active.
 * - tm_osd_CheckFallFast: ftCommon_CheckFallFast (ft/ftcommon.c), plus
 *   Fastfall Timer/Increment Fastfall Variable.asm (+0x28) and Display FF
 *   Timing.asm (+0x54).
 *
 * The bodies are the decomp's C, unchanged apart from the marked TM-CE calls.
 */
#include "osd.h"

#include <melee/ft/fighter.h>
#include <math.h>
#include <placeholder.h>
#include <melee/ft/ft_07C1.h>
#include <melee/ft/ft_07C6.h>
#include <melee/ft/ft_0819.h>
#include <melee/ft/ft_081B.h>
#include <melee/ft/ft_0877.h>
#include <melee/ft/ft_0881.h>
#include <melee/ft/ft_0892.h>
#include <melee/ft/ft_0899.h>
#include <melee/ft/ft_0C31.h>
#include <melee/ft/ft_0C88.h>
#include <melee/ft/ft_0C8C.h>
#include <melee/ft/ft_0D31.h>
#include <melee/ft/ft_0DF0.h>
#include <melee/ft/ftaction.h>
#include <melee/ft/ftafterimage.h>
#include <melee/ft/ftanim.h>
#include <melee/ft/ftcamera.h>
#include <melee/ft/ftchangeparam.h>
#include <melee/ft/ftCo_800C7CA0.h>
#include <melee/ft/ftcolanimlist.h>
#include <melee/ft/ftcoll.h>
#include <melee/ft/ftcommon.h>
#include <melee/ft/ftdata.h>
#include <melee/ft/ftdevice.h>
#include <melee/ft/ftdrawcommon.h>
#include <melee/ft/ftdynamics.h>
#include <melee/ft/ftlib.h>
#include <melee/ft/ftmetal.h>
#include <melee/ft/ftparts.h>
#include <melee/ft/kinds/ftCommon/ftCo_09F4.h>
#include <melee/ft/kinds/ftCommon/ftCo_0A01.h>
#include <melee/ft/kinds/ftCommon/ftCo_0C35.h>
#include <melee/ft/kinds/ftCommon/ftCo_Attack100.h>
#include <melee/ft/kinds/ftCommon/ftCo_Bury.h>
#include <melee/ft/kinds/ftCommon/ftCo_Damage.h>
#include <melee/ft/kinds/ftCommon/ftCo_DamageFall.h>
#include <melee/ft/kinds/ftCommon/ftCo_FallSpecial.h>
#include <melee/ft/kinds/ftCommon/ftCo_HammerWait.h>
#include <melee/ft/kinds/ftCommon/ftCo_ItemThrow.h>
#include <melee/ft/kinds/ftCommon/ftCo_Jump.h>
#include <melee/ft/kinds/ftCommon/ftCo_KinokoGiantEnd.h>
#include <melee/ft/kinds/ftCommon/ftCo_KinokoGiantStart.h>
#include <melee/ft/kinds/ftCommon/ftCo_KinokoSmallEnd.h>
#include <melee/ft/kinds/ftCommon/ftCo_KinokoSmallStart.h>
#include <melee/ft/kinds/ftCommon/ftCo_Rebound.h>
#include <melee/ft/kinds/ftCommon/ftCo_ShieldBreakFly.h>
#include <melee/ft/kinds/ftCommon/ftCo_SpecialS.h>
#include <melee/ft/kinds/ftCrazyHand/ftcrazyhandwait10.h>
#include <melee/ft/kinds/ftKirby/ftkirby.h>
#include <melee/ft/kinds/ftMasterHand/ftmasterhandwait10.h>
#include <melee/ft/kinds/ftPeach/types.h>
#include <melee/ft/types.h>
#include <dolphin/gx.h>
#include <dolphin/mtx.h>
#include <melee/cm/camera.h>
#include <melee/db/db.h>
#include <melee/ef/efasync.h>
#include <melee/gm/gm_unsplit.h>
#include <melee/gr/ground.h>
#include <melee/gr/stage.h>
#include <melee/if/ifmagnify.h>
#include <melee/it/it_26B1.h>
#include <melee/it/it_279C.h>
#include <melee/it/item.h>
#include <melee/lb/lb_00B0.h>
#include <melee/lb/lb_00CE.h>
#include <melee/lb/lbanim.h>
#include <melee/lb/lbarchive.h>
#include <melee/lb/lbshadow.h>
#include <melee/lb/types.h>
#include <melee/mp/mpcoll.h>
#include <melee/mp/mplib.h>
#include <melee/pl/pl_040D.h>
#include <melee/pl/player.h>
#include <melee/pl/plbonuslib.h>
#include <melee/pl/pltrick.h>
#include <melee/sfx/crowdsfx.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/debug.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjgxlink.h>
#include <sysdolphin/baselib/gobjobject.h>
#include <sysdolphin/baselib/gobjproc.h>
#include <sysdolphin/baselib/gobjuserdata.h>
#include <sysdolphin/baselib/jobj.h>
#include <sysdolphin/baselib/lobj.h>
#include <sysdolphin/baselib/mtx.h>
#include <sysdolphin/baselib/random.h>
#include <melee/ft/inlines.h>

/// @name src/tmce/osdcore_vars.c (MexTK side; fighters as void*)
/// @{
void tmce_osd_ShiftStates(void* fp);
void tmce_osd_ResetFastfall(void* fp);
void tmce_osd_IncFastfall(void* fp);
void tmce_osd_DisplayFastfall(void* fp);
/// @}

void tm_osd_ChangeMotionState(Fighter_GObj* gobj, FtMotionId msid,
                              MotionFlags flags, f32 anim_start,
                              f32 anim_speed, f32 anim_blend,
                              Fighter_GObj* arg3);
bool tm_osd_CheckFallFast(Fighter* fp);

void tm_osd_ChangeMotionState(Fighter_GObj* gobj, FtMotionId msid,
                              MotionFlags flags, f32 anim_start,
                              f32 anim_speed, f32 anim_blend,
                              Fighter_GObj* arg3)
{
    HSD_JObj* jobj = GET_JOBJ(gobj);
    Fighter* fp = GET_FIGHTER(gobj);
    MotionState* new_motion_state;
    struct Fighter_WaitAnimData* unk_struct_x18;
    s32 bone_index;
    u8(*unk_byte_ptr)[2];
    bool animflags_bool;
    union Struct2070 x2070;

    /* TM-CE StatesAndTimers/ShiftStates.asm (+0x40): before the new state
     * is stored. */
    tmce_osd_ShiftStates(fp);

    fp->motion_id = msid;
    fp->facing_dir1 = fp->facing_dir;

    HSD_JObjSetTranslate(jobj, &fp->cur_pos);
    efAsync_QueueFlush(gobj, &fp->x60C);

    if ((flags & Ft_MF_SkipHit) == 0) {
        if (fp->x2219_b3 != 0) {
            ftColl_8007AFF8(gobj);
        }
        if (fp->x2219_b4 != 0) {
            ft_8007C114(gobj);
        }
    }

    if ((flags & Ft_MF_SkipThrowException) == 0) {
        fp->x1064_thrownHitbox.x134.owner = NULL;
    }

    if ((flags & Ft_MF_KeepColAnimHitStatus) == 0) {
        if (fp->x1988 != 0) {
            ftColl_8007B62C(gobj, 0);
        }
        if (fp->x221A_b5 != 0) {
            ftColl_8007B0C0(gobj, HurtCapsule_Enabled);
        }
    }

    if (fp->x221A_b6 != 0) {
        ftColl_8007B4E0(gobj);
    }

    if (((flags & Ft_MF_SkipModel) == 0) && (fp->x221D_b2 != 0U)) {
        ftParts_80074A8C(gobj);
    }

    if (((flags & Ft_MF_SkipMatAnim) == 0) && ((fp->x221E_b7) != 0)) {
        ftAnim_80070654(gobj);
    }

    if (!(flags & Ft_MF_SkipParasol)) {
        fp->x2221_b4 = false;
        if ((ftGetParasolStatus(gobj) != -1) &&
            (ftGetParasolStatus(gobj) != 6))
        {
            ftCommon_8007E83C(gobj, 6, 0.0f);
        }
    }

    ftAnim_80070F28(gobj);
    ftAnim_80070E74(gobj);
    ftCommon_8007ECD4(fp, 7);
    ftCommon_8007ECD4(fp, 8);
    ftCommon_8007ECD4(fp, 0x24);

    if ((flags & Ft_MF_SkipRumble) == 0) {
        ftCommon_8007ECD4(fp, 1);
        ftCommon_8007ECD4(fp, 0x19);
    }

    if (((flags & Ft_MF_KeepColAnimPartHitStatus) == 0) &&
        (fp->x2221_b1 != 0U))
    {
        ftColl_8007B6EC(gobj);
        ftColl_8007B760(gobj, p_ftCommonData->x134);
        fp->x2221_b1 = 0;
    }
    ftCommon_8007E2F4(fp, 0);

    if (fp->dmg.x18F4 != 0) {
        fp->dmg.x18F4 = 0;
        fp->x2220_b4 = 0;
    }

    if ((flags & Ft_MF_Unk19) == 0) {
        fp->x2222_b2 = 0;
    }

    if ((flags & Ft_MF_SkipMetalB) == 0) {
        fp->x2223_b4 = 0;
    }

    if ((flags & Ft_MF_Unk27) == 0) {
        fp->x2227_b2 = 0;
    }

    if (((flags & Ft_MF_SkipHitStun) == 0) && (fp->x221C_b6 != 0U)) {
        fp->x221C_b6 = 0;
        fp->x2098 = p_ftCommonData->x4CC;
    }

    fp->is_sleeping = false;
    fp->x2219_b1 = 0;
    fp->x2219_b2 = 0;

    fp->dmg.x182c_behavior = 1.0f;
    fp->dmg.kb_applied = 0.0f;
    fp->dmg.x18A8 = 0.0f;
    fp->dmg.armor1 = 0.0f;
    fp->dmg.x18a0 = 0.0f;

    fp->x221A_b7 = 0;
    fp->x221B.x221B_b0 = 0;
    fp->x221C_b3 = 0;

    fp->shield_unk0 = 0.0f;
    fp->shield_unk1 = 0.0f;

    fp->x221D_b5 = 0;
    fp->reflecting = false;
    fp->x2218_b6 = 0;
    fp->x221C_b4 = 0;

    fp->x1A6A = 0;

    fp->x221D_b7 = 0;
    fp->invisible = false;
    fp->x221E_b1 = 0;
    fp->x221E_b2 = 0;
    fp->x221F_b1 = 0;
    fp->x221E_b5 = 0;
    fp->x221E_b6 = 0;
    fp->x2220_b3 = 0;
    fp->x2220_b7 = 0;

    fp->x209C = 0;

    fp->x2223_b0 = 0;
    fp->x2222_b3 = 0;
    fp->x2224_b5 = 0;
    fp->x2225_b1 = 0;
    fp->x2225_b4 = 0;

    mpClearFloorSkip(&fp->coll_data);

    ftCo_800DEEA8(gobj);

    fp->smash_attrs.x2138_smashSinceHitbox = -1.0f;
    fp->x2224_b4 = false;

    if ((flags & Ft_MF_SkipItemVis) == 0) {
        fp->x221E_b3 = 1;
    } else if (fp->x221E_b3 == 0U) {
        ftCommon_8007F578(gobj);
    }

    if ((flags & Ft_MF_SkipModelPartVis) == 0) {
        fp->x221E_b4 = 1;
    }

    if ((flags & Ft_MF_SkipModelFlags) == 0) {
        fp->x2225_b2 = 1;
    }

    if ((flags & Ft_MF_KeepFastFall) == 0) {
        fp->fall_fast = 0;
        /* TM-CE Fastfall Timer/Initialize Fastfall Variable.asm (+0x51C) */
        tmce_osd_ResetFastfall(fp);
    }

    if ((flags & Ft_MF_SkipColAnim) == 0) {
        ftCo_800C0134(fp);
    }

    if (((flags & Ft_MF_KeepGfx) == 0) && (fp->x2219_b0 != 0U)) {
        ftCommon_8007DB24(gobj);
    }

    if (((flags & Ft_MF_KeepAccessory) == 0) &&
        ((u32) fp->x20A0_accessory != 0U))
    {
        HSD_JObjRemoveAll(fp->x20A0_accessory);
        fp->x20A0_accessory = 0U;
    }

    if (fp->ground_or_air == GA_Ground) {
        if (fp->kind == Ft_Kind_Peach) {
            fp->u.pe.has_float = true;
        }
        fp->x2221_b5 = false;
        fp->x2221_b7 = true;
        fp->x2221_b6 = true;
        fp->x2224_b1 = false;
        fp->x2227_b1 = false;
        fp->x213C = -1;

        if (fp->x2227_b4 != 0U) {
            pl_8003FE1C(fp->player_idx, fp->is_sub_fighter);
            fp->x2227_b4 = false;
        }
        fp->x2227_b5 = false;
        pl_80040330(fp->player_idx, fp->is_sub_fighter, fp->x2140);
        fp->x2140 = 0;
        fp->used_tether = false;
        fp->x2180 = 6;
    }

    if ((msid != 0xE) && (msid != 0xF) && (msid != 0x10) && (msid != 0x11)) {
        fp->hitlag_mul = 0.0f;
    }

    if ((flags & Ft_MF_KeepSfx) == 0) {
        ft_80088884(fp);
        ft_800888E0(fp);
        ft_800887CC(fp);
    }

    if ((flags & Ft_MF_KeepSwordTrail) == 0) {
        fp->x2100 = -1;
    }
    if ((flags & Ft_MF_SkipNametagVis) == 0) {
        fp->x209A = 0;
    }

    fp->x2222_b7 = 0;

    if ((flags & Ft_MF_UnkUpdatePhys) != 0) {
        fp->x100 = 0.0f;
    } else {
        fp->x100 = -1.0f;
    }

    if ((flags & Ft_MF_Unk24) == 0) {
        fp->x221C_u16_y = 0;
    }

    fp->lstick_angle = 0.0f;

    ftPartSetRotX(fp, 0, 0.0F);
    ftPartSetRotY(fp, 0, (M_PI_2 * fp->facing_dir));
    ftPartSetRotZ(fp, 0, 0.0F);

    if (msid >= fp->x18) {
        new_motion_state = &fp->x20_actionStateList[(msid - fp->x18)];
    } else {
        new_motion_state = &fp->x1C_actionStateList[msid];
    }

    if (fp->ground_or_air == GA_Ground) {
        if ((flags & 0x40) == 0) {
            if (new_motion_state->x8.x0.x1.x9_b1 != 0 && fp->dmg.x18C8 == -1) {
                if (p_ftCommonData->x814 > 0) {
                    fp->dmg.x18C8 = p_ftCommonData->x814;
                } else {
                    fp->dmg.x18C8 = 1;
                }
            }
        }
    }

    {
        // load in the union.
        x2070 = fp->x2070;
        ft_800890D0(fp, new_motion_state->x8.x0.move_id);
        ft_800895E0(fp, new_motion_state->x4_flags);
        fp->x2225_b3 = new_motion_state->x8.x0.x1.x9_b0;

        if (fp->x2226_b4) {
            if (fp->x2070.x0.x2071_b5) {
                ftCo_800C8B2C(fp, 0x7E, 0);
            }
            if (fp->x2070.x0.x2071_b6) {
                ftCo_800C8B2C(fp, 0x7F, 0);
            }
        }

        if (fp->x21EC != NULL) {
            fp->x21EC(gobj);
            fp->x21EC = NULL;
        }

        if (!(flags & Ft_MF_SkipAttackCount)) {
            pl_80037C60(gobj, x2070.x2070_int);
        }

        fp->anim_id = new_motion_state->anim_id;
        fp->frame_speed_mul = anim_speed;
        fp->x8A0_unk = anim_speed;

        fp->cur_anim_frame = (anim_start - fp->frame_speed_mul);
        fp->x898_unk = 0.0f;

        if ((fp->x594.x0.x594_b0) || (fp->x594.x0.x594_b5)) {
            animflags_bool = true;
        } else {
            animflags_bool = false;
        }

        if (fp->anim_id != -1) {
            Vec3 translation;
            Quaternion quat;

            bone_index = fp->x594.x0.x596_bits.x7;

            if ((flags & Ft_MF_FreezeState) != 0) {
                fp->x2223_b0 = 1;
                fp->x104 = 0x14;
                fp->frame_speed_mul = 0.0f;
                anim_speed = 0.0f;
            }

            if (arg3 != NULL) {
                unk_struct_x18 =
                    &((Fighter*) arg3->user_data)->x24[fp->anim_id];
                unk_byte_ptr = &((Fighter*) arg3->user_data)->x28[fp->anim_id];
            } else {
                unk_struct_x18 = &fp->x24[fp->anim_id];
                unk_byte_ptr = &fp->x28[fp->anim_id];
            }
            fp->x594.x594_s32 = unk_struct_x18->x10_animCurrFlags;
            ftCo_8009E7B4(fp, unk_byte_ptr);
            if ((flags & Ft_MF_SkipAnim) == 0) {
                if (arg3 != 0U) {
                    ftData_80085CD8(fp, GET_FIGHTER(arg3), fp->anim_id);
                    ftColl_8007B8CC(fp, arg3);
                } else {
                    ftData_80085CD8(fp, fp, fp->anim_id);
                }
                fp->x3E4_fighterCmdScript.x8.u = unk_struct_x18->xC;
                fp->x3E4_fighterCmdScript.loop_count = 0;

                if (anim_start) {
                    if (fp->x590 != 0U) {
                        ftAnim_8006EBE8(gobj, anim_start - anim_speed,
                                        anim_speed,
                                        (anim_blend == -1.0f) ? 0.0f
                                        : anim_blend ? anim_blend
                                                     : (*unk_byte_ptr)[0]);
                    }
                    ftAnim_8006E9B4(gobj);
                    if (fp->x594.x0.x594_b0 != 0U) {
                        fp->x6B0.x = fp->x6B0.y = fp->x6B0.z = 0.0F;
                        fp->x6A4_transNOffset.x = fp->x6A4_transNOffset.y =
                            fp->x6A4_transNOffset.z = 0.0F;
                        fp->x698 = fp->x68C_transNPos;
                    }

                    if (fp->x594.x0.x594_b5 != 0U) {
                        fp->x6E4.x = fp->x6E4.y = fp->x6E4.z = 0.0F;
                        fp->x6D8.x = fp->x6D8.y = fp->x6D8.z = 0.0F;
                        fp->x6CC = fp->x6C0;
                    }
                    fp->x3E4_fighterCmdScript.timer = -anim_start;
                } else {
                    if (fp->x590 != 0U) {
                        ftAnim_8006EBE8(gobj, anim_start, anim_speed,
                                        (anim_blend == -1.0f) ? 0.0f
                                        : anim_blend ? anim_blend
                                                     : (*unk_byte_ptr)[0]);
                    }
                    fp->x3E4_fighterCmdScript.timer = 0.0f;
                }

                ftAnim_8006E9B4(gobj);
                if ((bone_index != 0) && (*unk_byte_ptr)[0] != 0U) {
                    HSD_JObj* temp_joint = fp->parts[bone_index].x4_jobj2;

                    HSD_JObjGetTranslation(temp_joint, &translation);
                    HSD_JObjSetTranslate(fp->parts[bone_index].joint,
                                         &translation);
                    HSD_JObjGetRotation(temp_joint, &quat);
                    ftParts_JObjSetRotation(fp->parts[bone_index].joint,
                                            &quat);
                }

                if (fp->x594.x0.x594_b0 != 0U) {
                    if (!anim_start) {
                        float c = 0.0f;
                        fp->x6B0.x = fp->x6B0.y = fp->x6B0.z = c;
                        fp->x6A4_transNOffset.x = fp->x6A4_transNOffset.y =
                            fp->x6A4_transNOffset.z = c;
                        fp->x698 = fp->x68C_transNPos;
                    } else if (((flags & Ft_MF_SkipAnimVel) == 0) &&
                               (fp->ground_or_air == GA_Ground))
                    {
                        float temp_vel =
                            fp->x6A4_transNOffset.z * fp->facing_dir;
                        fp->self_vel.x = temp_vel;
                        fp->gr_vel = temp_vel;
                    }
                }

                if (fp->x594.x0.x594_b5 != 0U) {
                    if (!anim_start) {
                        float c = 0.0f;
                        fp->x6E4.x = fp->x6E4.y = fp->x6E4.z = c;
                        fp->x6D8.x = fp->x6D8.y = fp->x6D8.z = c;
                        fp->x6CC = fp->x6C0;
                    } else if (((flags & Ft_MF_SkipAnimVel) == 0) &&
                               (fp->ground_or_air == GA_Ground))
                    {
                        float temp_vel = fp->x6D8.z * fp->facing_dir;
                        fp->self_vel.x = temp_vel;
                        fp->gr_vel = temp_vel;
                    }
                }
                if ((flags & Ft_MF_UpdateCmd) != 0) {
                    ftAction_8007349C(gobj);
                } else if (anim_start) {
                    ftAction_80073354(gobj);
                } else {
                    ftCo_800C0408(gobj);
                    ftAction_80073240(gobj);
                }
            } else {
                fp->anim_id = -1;
            }
        }

        if (fp->anim_id == -1) {
            fp->x594.x594_s32 = 0;
            ftAnim_80070758(jobj);
            ftAnim_80070758(fp->x8AC_animSkeleton);
            fp->x3E4_fighterCmdScript.x8.u = NULL;
            fp->x8A4_animBlendFrames = 0;
            fp->x8A8_anim_frame = 0;
        }

        if (animflags_bool) {
            if (!fp->x594.x0.x594_b0 && !fp->x594.x0.x594_b0) {
                !fp;
                ftCommon_ClampGroundVel(fp, fp->co_attrs.dash_max_velocity);
            }
        }

        fp->anim_cb = new_motion_state->anim_cb;
        fp->input_cb = new_motion_state->input_cb;
        fp->phys_cb = new_motion_state->phys_cb;
        fp->coll_cb = new_motion_state->coll_cb;
        fp->cam_cb = new_motion_state->cam_cb;

        fp->accessory1_cb = NULL;
        fp->accessory4_cb = NULL;
        fp->deal_dmg_cb = NULL;
        fp->shield_hit_cb = NULL;
        fp->reflect_hit_cb = NULL;
        fp->hitlag_cb = NULL;
        fp->x21CC = NULL;
        fp->post_hitlag_cb = NULL;
        fp->pre_hitlag_cb = NULL;
        fp->take_dmg_cb = NULL;
        fp->take_dmg_2_cb = NULL;
        fp->hurtbox_detect_cb = NULL;
        fp->x21F8 = NULL;
        fp->death2_cb = NULL;
    }
}

bool tm_osd_CheckFallFast(Fighter* fp)
{
    if (!fp->fall_fast && fp->self_vel.y < 0) {
        /* TM-CE Increment Fastfall Variable.asm (+0x28) */
        tmce_osd_IncFastfall(fp);
        if (fp->input.lstick[0].y <= -p_ftCommonData->x88 &&
            fp->active_timer.lstick.y < p_ftCommonData->x8C)
        {
            /* TM-CE Display FF Timing.asm (+0x54) */
            tmce_osd_DisplayFastfall(fp);
            fp->fall_fast = true;
            fp->active_timer.lstick.y = 0xFE;
            ft_PlaySFX(fp, 0x96, 0x7F, 0x40);
            return true;
        }
    }
    return false;
}
