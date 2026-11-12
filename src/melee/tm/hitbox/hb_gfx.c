/**
 * @file
 * TM-CE "Hide Player GFX When Hitboxes Enabled/" (Additional Codes): while a
 * fighter's (or item's) hitbox display is on (`x21FC_flag.x0.b6`, the flag
 * the Lab's "Hitboxes" option sets as FighterData.show_hit), effects spawned
 * on it and the hit sparks on it are not created, so they do not cover the
 * hitbox and hurtbox capsules.
 *
 * Both are edited copies of a whole vanilla function behind a `function`
 * hook (config/GALE01/tm_hooks/hitbox.txt); Slippi patches neither, and no
 * other hook sits inside them. The bodies are the decomp's C, unchanged apart
 * from the marked TM-CE checks.
 *
 * - tm_hitbox_efSync_Spawn: efSync_Spawn (ef/efsync.c), plus Hide GFX When
 *   Hitboxes Enabled.asm (+0x54). It is variadic and has ~275 callers, so
 *   neither a `call` hook nor a wrapper that calls the original works.
 * - tm_hitbox_ApplyHits: ftColl_8007A06C (ft/ftcoll.c), plus Hide OnHit GFX
 *   When Hitboxes Enabled.asm (+0x114) and ...Enabled 2.asm (+0x3C4). The hit
 *   sparks are spawned with no parent gobj, so the efSync_Spawn check above
 *   does not catch them; both sites are inside the same inlined helper.
 */
#include <melee/ef/forward.h>
#include <melee/ft/forward.h>
#include <melee/it/forward.h>

#include <math.h>
#include <placeholder.h>
#include <stdarg.h>

#include "hitbox.h"
#include <melee/ef/efalt.h>
#include <melee/ef/efasync.h>
#include <melee/ef/efdata.h>
#include <melee/ef/eflib.h>
#include <melee/ef/efsync.h>
#include <melee/ef/inlines.h>
#include <melee/ef/types.h>
#include <melee/ft/fighter.h>
#include <melee/ft/ftcoll.h>
#include <melee/ft/ftlib.h>
#include <melee/ft/inlines.h>
#include <melee/ft/types.h>
#include <melee/gm/gm_unsplit.h>
#include <melee/it/inlines.h>
#include <melee/it/it_3F14.h>
#include <melee/it/types.h>
#include <melee/lb/lbcollision.h>
#include <melee/lb/types.h>
#include <melee/pl/pl_040D.h>
#include <melee/pl/player.h>
#include <melee/pl/plbonuslib.h>
#include <sysdolphin/baselib/generator.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/jobj.h>
#include <sysdolphin/baselib/psstructs.h>
#include <sysdolphin/baselib/random.h>

/// Hide GFX When Hitboxes Enabled.asm: true when @p gobj is a fighter or an
/// item whose hitboxes are being displayed.
static bool tm_hitbox_HidesGfx(HSD_GObj* gobj)
{
    if (gobj == NULL) {
        return false;
    }
    switch (gobj->classifier) {
    case HSD_GOBJ_CLASS_FIGHTER:
        return GET_FIGHTER(gobj)->x21FC_flag.x0.b6;
    case HSD_GOBJ_CLASS_ITEM:
        return GET_ITEM(gobj)->xDAA.xDAA_flag.x0.b6;
    default:
        return false;
    }
}

/// Replaces efSync_Spawn (`function` hook).
void* tm_hitbox_efSync_Spawn(s32 gfx_id, HSD_GObj* gobj, ...)
{
    va_list vlist;
    Vec3 translate;
    Vec3 scale;
    void* ret_obj;
    EF_Effect* effect;
    HSD_JObj* jobj_2;
    HSD_JObj* jobj_1;
    Vec3* va_vec3;
    f32 rotate_y;
    f32 rand_f32;
    f32 rand_param_x;
    f32 rand_param_y;
    f32 rand_rot_y;
    Fighter* fp;
    s32 cnt_2;
    f32 rand_rot_x;
    PAD_STACK(0x2C);

    // TM-CE: Hide GFX When Hitboxes Enabled.asm (+0x54): no effect on a
    // fighter or item whose hitboxes are shown.
    if (tm_hitbox_HidesGfx(gobj)) {
        return NULL;
    }

    efLib_AnimCount = efLib_LoadKind = (u32) (ret_obj = NULL);
    va_start(vlist, gobj);
    if ((gfx_id == 0x479) && (efAsync_DatEntries[1].data == NULL)) {
        gfx_id = 0x506;
    }
    if (gfx_id < 0x250) {
        va_vec3 = va_arg(vlist, Vec3*);
        return efLib_CreateGenerator(gfx_id, va_vec3);
    }
    if (gfx_id / 1000 == 0x1E) {
        va_vec3 = va_arg(vlist, Vec3*);
        return efLib_CreateGenerator(gfx_id, va_vec3);
    }
    if (gfx_id < 0x478) {
        return efAsync_Dispatch(gfx_id, gobj, vlist);
    }
    if (gfx_id < 0x4BA) {
        return efAlt_Spawn(gfx_id, gobj, vlist);
    }
    efLib_LoadKind = EF_LOADKIND_SYNC;
    switch (gfx_id) {
    case 0x4BB:
        ret_obj = efLib_Create_Attach_Scale_FacingDir(
            0x1770, gobj, va_arg(vlist, HSD_JObj*));
        if (ret_obj != NULL) {
            effect = ret_obj;
            effect->next = efLib_Create_AttachChild_Scale(
                0x1772, gobj, va_arg(vlist, HSD_JObj*));
        }
        break;
    case 0x4BC:
        ret_obj = efLib_Create_Attach_Scale_FacingDir(
            0x1771, gobj, va_arg(vlist, HSD_JObj*));
        if (ret_obj != NULL) {
            effect = ret_obj;
            effect->next = efLib_Create_AttachChild_Scale(
                0x1773, gobj, va_arg(vlist, HSD_JObj*));
        }
        break;
    case 0x4BD:
        ret_obj = hsd_8039EFAC(0, 7, 0x1B58, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4BE:
        ret_obj = hsd_8039EFAC(0, 7, 0x1B5C, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4BF:
        jobj_1 = va_arg(vlist, HSD_JObj*);
        ret_obj = hsd_8039EFAC(0, 7, 0x1B5D, jobj_1);
        hsd_8039EFAC(0, 0, 0x5F, jobj_1);
        break;
    case 0x4C0:
        ret_obj = efLib_Create_Attach(0x1B58U, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4C1:
        ret_obj = efLib_Create_Attach_Scale_FacingDir(
            0x1B59, gobj, va_arg(vlist, HSD_JObj*));
        if (ret_obj != NULL) {
            effect = ret_obj;
            Effect_SetRotationZ(effect, *va_arg(vlist, f32*));
        }
        break;
    case 0x4C2:
        ret_obj = efLib_Create_Attach_Scale_FacingDir(
            0x1B5A, gobj, va_arg(vlist, HSD_JObj*));
        if (ret_obj != NULL) {
            effect = ret_obj;
            Effect_SetRotationZ(effect, *va_arg(vlist, f32*));
        }
        break;
    case 0x4C3: {
        HSD_Generator* gen = efLib_CreateGenerator_AddAppSRT(0x24CU);
        if (gen != NULL) {
            Effect_SetGeneratorPos(gen, va_arg(vlist, Vec3*));
            ret_obj = gen;
        }
        break;
    }
    case 0x4C4:
        ret_obj = efLib_Create_Attach_Scale_FacingDir(
            0x1B5B, gobj, va_arg(vlist, HSD_JObj*));
        if (ret_obj != NULL) {
            effect = ret_obj;
            Effect_SetRotationZ(effect, *va_arg(vlist, f32*));
        }
        break;
    case 0x4C5:
        ret_obj = efLib_Create_Attach_Scale_FacingDir(
            0x1B5C, gobj, va_arg(vlist, HSD_JObj*));
        if (ret_obj != NULL) {
            effect = ret_obj;
            Effect_SetRotationZ(effect, *va_arg(vlist, f32*));
        }
        break;
    case 0x4C6:
        ret_obj = efLib_Create_Attach_Scale_FacingDir(
            0x1F40, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4C7:
        ret_obj = efLib_Create_Attach_Scale_FacingDir(
            0x1F41, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4C8:
        ret_obj =
            efLib_Create_Attach_Scale(0x1F42, gobj, va_arg(vlist, HSD_JObj*));
        effect = ret_obj;
        if (effect != NULL) {
            Effect_SetFacingDir(effect, *va_arg(vlist, f32*));
            jobj_2 = GET_JOBJ(effect->gobj);
            HSD_JObjAnimAll(jobj_2);
        }
        break;
    case 0x4C9:
        ret_obj =
            efLib_Create_Attach_Scale(0x1F43, gobj, va_arg(vlist, HSD_JObj*));
        effect = ret_obj;
        if (effect != NULL) {
            Effect_SetFacingDir(effect, *va_arg(vlist, f32*));
            jobj_2 = GET_JOBJ(effect->gobj);
            HSD_JObjAnimAll(jobj_2);
        }
        break;
    case 0x4CA:
        ret_obj =
            efLib_Create_Attach_Scale(0x1F44, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4CB:
        ret_obj =
            efLib_Create_Attach_Scale(0x1F45, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4CC:
        ret_obj = efLib_Create_Attach_Pos(0x1F46U, gobj, va_arg(vlist, Vec3*));
        if (ret_obj != NULL) {
            effect = ret_obj;
            HSD_JObjGetScale(jobj_1 = gobj->hsd_obj, &scale);
            HSD_JObjSetScale(GET_JOBJ(effect->gobj), &scale);
            effect->update = efLib_Cb_SetRotY_FromFighterDir;
        }
        break;
    case 0x4CD:
        ret_obj = efLib_Create_Attach(0x2328U, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4CE:
        ret_obj = efLib_CreateGenerator(0x2328U, va_arg(vlist, Vec3*));
        break;
    case 0x4CF:
    case 0x4D0: {
        EF_Effect* cur;
        EF_Effect* tail;
        s32 i;
        f32 scale_f32;
        scale_f32 = 1.0f;
        va_vec3 = va_arg(vlist, Vec3*);
        translate = *va_vec3;
        if (gfx_id == 0x4CF) {
            scale_f32 = *va_arg(vlist, f32*);
        }
        for (i = 0; i < 12; i++) {
            rand_f32 = HSD_Randf();
            if (rand_f32 < 0.5f) {
                if (gfx_id == 0x4D0) {
                    cur = efLib_Create_Attach_Pos(0x1CU, gobj, &translate);
                } else {
                    cur = efLib_Create_Attach_Pos(0x1EU, gobj, &translate);
                }
            } else if (gfx_id == 0x4D0) {
                cur = efLib_Create_Attach_Pos(0x1DU, gobj, &translate);
            } else {
                cur = efLib_Create_Attach_Pos(0x1FU, gobj, &translate);
            }
            if (cur == NULL) {
                break;
            }
            cur->update = efLib_Cb_SetOffset_FromParams;
            cur->lifetime = 0x32;
            rand_rot_y = M_TAU * HSD_Randf();
            rand_rot_x = M_TAU * HSD_Randf();
            jobj_1 = GET_JOBJ(cur->gobj);
            HSD_JObjSetScaleX(jobj_1, scale_f32);
            jobj_1 = GET_JOBJ(cur->gobj);
            HSD_JObjSetScaleY(jobj_1, scale_f32);
            jobj_1 = GET_JOBJ(cur->gobj);
            HSD_JObjSetScaleZ(jobj_1, scale_f32);
            jobj_1 = GET_JOBJ(cur->gobj);
            HSD_JObjSetRotationY(jobj_1, rand_rot_y);
            jobj_1 = GET_JOBJ(cur->gobj);
            HSD_JObjSetRotationX(jobj_1, rand_rot_x);
            rand_param_x = sinf(rand_rot_y);
            {
                f32 tmp = 2.0f * cosf(rand_rot_x);
                cur->params.x = tmp * rand_param_x;
            }
            cur->params.y = 2.0f * sinf(rand_rot_x);
            rand_param_y = cosf(rand_rot_y);
            {
                f32 tmp = 2.0f * cosf(rand_rot_x);
                cur->params.z = tmp * rand_param_y;
            }
            if (i != 0) {
                tail->next = cur;
                tail = tail->next;
            } else {
                ret_obj = tail = cur;
            }
        }
        break;
    }
    case 0x4EE:
        ret_obj = efLib_Create_Attach(0x2710U, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4EF:
        ret_obj = efLib_Create_Attach(0x2711U, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4F0:
        ret_obj =
            efLib_Create_Attach_Scale(0x2712, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4D5:
        ret_obj = hsd_8039EFAC(0, 0xB, 0x2AF8, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4D6:
        ret_obj =
            efLib_Create_Attach_Scale(0x2AF8, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4D7:
        ret_obj = hsd_8039EFAC(0, 0xB, 0x2AF9, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4D8: {
        HSD_Generator* generator = efLib_CreateGenerator_AddAppSRT(0x61U);
        if (generator != NULL) {
            Effect_SetGeneratorPos(generator, va_arg(vlist, Vec3*));
            HSD_JObjGetScale((jobj_2 = GET_JOBJ(gobj)), &scale);
            ret_obj = generator;
            Effect_SetGeneratorScale(generator, scale.y);
            generator->appsrt->rot.y = M_PI_2;
        }
        break;
    }
    case 0x4D9:
        ret_obj = efLib_Create_Attach_Pos(0x2EE0U, gobj, va_arg(vlist, Vec3*));
        if (ret_obj != NULL) {
            rotate_y = Effect_GetFacingRotationY(*va_arg(vlist, f32*));
            effect = ret_obj;
            jobj_2 = GET_JOBJ(effect->gobj);
            HSD_JObjSetRotationY(jobj_2, rotate_y);
            HSD_JObjGetScale((jobj_2 = GET_JOBJ(gobj)), &scale);
            jobj_2 = GET_JOBJ(effect->gobj);
            HSD_JObjSetScale(jobj_2, &scale);
        }
        break;
    case 0x4DA: {
        EF_Effect* child;
        jobj_2 = va_arg(vlist, HSD_JObj*);
        ret_obj = efLib_Create_Attach_Scale(0x2EE1, gobj, jobj_2);
        if (ret_obj != NULL) {
            effect = ret_obj;
            child = efLib_Create_Attach_Scale(0x2EE2, gobj, jobj_2);
            effect->next = child;
            if (child != NULL) {
                effect->update = efLib_Cb_ftKp_SpecialHi;
            }
        }
        break;
    }
    case 0x4DB:
        ret_obj = efLib_CreateGenerator_Attach_Scale(0x2EE5, vlist, gobj);
        break;
    case 0x4DC:
        ret_obj = efLib_CreateGenerator_Attach_Scale(0x2EE6, vlist, gobj);
        break;
    case 0x4DD:
        ret_obj = efLib_CreateGenerator_Attach_Scale(0x2EE7, vlist, gobj);
        break;
    case 0x4DE:
        ret_obj = efLib_CreateGenerator_Attach_Scale(0x2EE8, vlist, gobj);
        break;
    case 0x4DF:
        ret_obj = efLib_CreateGenerator_Attach_Scale(0x143, vlist, gobj);
        break;
    case 0x4E0:
        ret_obj = efLib_Create_Attach(0x32C8U, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4E1: {
        HSD_JObj* cursor;
        ret_obj = efLib_Create(0x32C9, gobj);
        if (ret_obj != NULL) {
            effect = ret_obj;
            jobj_1 = va_arg(vlist, HSD_JObj*);
            effect->attach_jobj = jobj_1;
            effect->update = efLib_Cb_SetOffsetY_FromParamY;
            cursor = jobj_1;
            while (HSD_JObjGetParent(cursor) != NULL) {
                jobj_1 = HSD_JObjGetParent(cursor);
                cursor = jobj_1;
            }
            HSD_JObjGetScale(cursor, &scale);
            effect->params = *va_arg(vlist, Vec3*);
            effect->params.y *= scale.y;
        }
        break;
    }
    case 0x4E2:
        ret_obj = efLib_Create_Attach_Pos(0x32CAU, gobj, va_arg(vlist, Vec3*));
        break;
    case 0x4E3:
        ret_obj = efLib_CreateGenerator(0x18AU, va_arg(vlist, Vec3*));
        break;
    case 0x4E4:
        ret_obj = efLib_CreateGenerator(0x194U, va_arg(vlist, Vec3*));
        break;
    case 0x4E5:
        ret_obj = hsd_8039EFAC(0, 0, 0x17D, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4E6:
        ret_obj = hsd_8039EFAC(0, 0, 0x17E, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4E7:
        ret_obj = efLib_CreateGenerator(0x196U, va_arg(vlist, Vec3*));
        break;
    case 0x4E8:
        ret_obj = efLib_Create_Attach_Pos(0x32CBU, gobj, va_arg(vlist, Vec3*));
        break;
    case 0x4E9:
        ret_obj = hsd_8039EFAC(0, 0xE, 0x36B0, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4EA:
        ret_obj = hsd_8039EFAC(0, 0xE, 0x36B1, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4EB:
        ret_obj = efLib_CreateGenerator_AppSRT_SetFacingDir(0x36B6, vlist);
        break;
    case 0x4EC:
        ret_obj = hsd_8039EFAC(0, 0xE, 0x36B7, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4ED:
        ret_obj =
            efLib_Create_AttachChild(0x36B0U, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4D1:
        ret_obj = hsd_8039EFAC(0, 0, 0x64, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4D2:
        ret_obj = efLib_Create_Attach_Pos(0x3A98U, gobj, va_arg(vlist, Vec3*));
        break;
    case 0x4D3:
        jobj_2 = va_arg(vlist, HSD_JObj*);
        ret_obj = efLib_CreateGenerator_Attach_AddAppSRT(0x172, jobj_2);
        if (ret_obj != NULL) {
            efLib_CreateGenerator_Attach_AddAppSRT(0x173, jobj_2);
        }
        break;
    case 0x4D4:
        ret_obj =
            efLib_CreateGenerator_Attach(0x11E, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4F1:
        ret_obj = efLib_CreateGenerator_AppSRT_SetFacingDir(0x3E80, vlist);
        break;
    case 0x4F2:
        ret_obj = efLib_Create_Attach_Scale_FacingDir(
            0x3E80, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4F3:
        ret_obj = efLib_Create_Attach_Scale_FacingDir(
            0x3E81, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4F4: {
        Vec3 effect_scale;

        ret_obj =
            efLib_Create_AttachChild(0x4268U, gobj, va_arg(vlist, HSD_JObj*));
        goto copy_gobj_scale;
    case 0x4F5:
        ret_obj =
            efLib_Create_AttachChild(0x4269U, gobj, va_arg(vlist, HSD_JObj*));
    copy_gobj_scale:
        if (ret_obj != NULL) {
            HSD_JObjGetScale((jobj_2 = GET_JOBJ(gobj)), &scale);
            effect = ret_obj;
            HSD_JObjGetScale(GET_JOBJ(effect->gobj), &effect_scale);
            jobj_2 = GET_JOBJ(effect->gobj);
            HSD_JObjSetScale(jobj_2, &scale);
        }
        break;
    }
    case 0x4F6:
        ret_obj =
            efLib_Create_Attach_Scale(0x426A, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4F7:
        ret_obj =
            efLib_Create_Attach_Scale(0x426B, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4F8:
        ret_obj = efLib_CreateGenerator_Attach_Scale(0x6E, vlist, gobj);
        break;
    case 0x4F9:
        ret_obj = efLib_CreateGenerator_Attach_Scale(0x1C8, vlist, gobj);
        break;
    case 0x4FA:
        ret_obj = efLib_CreateGenerator_Attach_Scale(0x166, vlist, gobj);
        break;
    case 0x4FB:
        ret_obj = hsd_8039EFAC(0, 0, 0x71, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4FE:
        ret_obj = efLib_Create_Attach(0x426CU, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4FF:
    case 0x500:
        ret_obj = efLib_Create_Attach_Scale(
            0x426D, gobj, GET_FIGHTER(gobj)->parts[FtPart_TransN].joint);
        break;
    case 0x501:
        fp = GET_FIGHTER(gobj);
        ret_obj = efLib_Create_Attach_Scale(
            0x426E, gobj, GET_FIGHTER(gobj)->parts[FtPart_TransN].joint);
        if (ret_obj != NULL) {
            effect = ret_obj;
            rotate_y = Effect_GetFacingRotationY(fp->facing_dir);
            jobj_2 = GET_JOBJ(effect->gobj);
            HSD_JObjSetRotationY(jobj_2, rotate_y);
            effect->attach_jobj = fp->parts[85].joint;
            effect->update = efLib_Cb_LifetimeEndSpawn;
            effect->lifetime = 6;
        }
        break;
    case 0x502:
        ret_obj = hsd_8039EFAC(0, 0, 0x1A6, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4FC:
        ret_obj = hsd_8039EFAC(0, 0x11, 0x426D, va_arg(vlist, HSD_JObj*));
        break;
    case 0x4FD:
        ret_obj = hsd_8039EFAC(0, 0x11, 0x4271, va_arg(vlist, HSD_JObj*));
        break;
    case 0x503:
        ret_obj = efLib_CreateGenerator(0x6AU, va_arg(vlist, Vec3*));
        break;
    case 0x504: {
        HSD_Generator* generator = efLib_CreateGenerator_AddAppSRT(0x6DU);
        if (generator != NULL) {
            Effect_SetGeneratorPos(generator, va_arg(vlist, Vec3*));
            HSD_JObjGetScale((jobj_2 = GET_JOBJ(gobj)), &scale);
            ret_obj = generator;
            Effect_SetGeneratorScale(generator, scale.y);
        }
        break;
    }
    case 0x505: {
        HSD_Generator* generator = efLib_CreateGenerator_AddAppSRT(0x79U);
        if (generator != NULL) {
            Effect_SetGeneratorPos(generator, va_arg(vlist, Vec3*));
            HSD_JObjGetScale((jobj_2 = gobj->hsd_obj), &scale);
            ret_obj = generator;
            Effect_SetGeneratorScale(generator, scale.y);
        }
        break;
    }
    case 0x506:
        ret_obj = efLib_CreateGenerator(0x4658U, va_arg(vlist, Vec3*));
        break;
    case 0x507:
        jobj_1 = va_arg(vlist, HSD_JObj*);
        ret_obj = efLib_Create_Attach(0x4650U, gobj, jobj_1);
        if (ret_obj != NULL) {
            effect = ret_obj;
            rotate_y = Effect_GetFacingRotationY(*va_arg(vlist, f32*));
            jobj_2 = GET_JOBJ(effect->gobj);
            HSD_JObjSetRotationY(jobj_2, rotate_y);
        }
        hsd_8039EFAC(0, 0x12, 0x4650, jobj_1);
        break;
    case 0x508:
        ret_obj = efLib_CreateGenerator(0x4652U, va_arg(vlist, Vec3*));
        break;
    case 0x509:
        ret_obj =
            efLib_Create_Attach_Scale(0x4651, gobj, va_arg(vlist, HSD_JObj*));
        if (ret_obj != NULL) {
            effect = ret_obj;
            effect->update = efLib_Cb_ftLg_SpecialLw;
        }
        break;
    case 0x50A:
        ret_obj = hsd_8039EFAC(0, 0, 0x5F, va_arg(vlist, HSD_JObj*));
        break;
    case 0x50B:
        ret_obj = efLib_Create_Attach_Scale_FacingDir(
            0x4A38, gobj, va_arg(vlist, HSD_JObj*));
        if (ret_obj != NULL) {
            effect = ret_obj;
            effect->next = efLib_Create_Attach_Scale_FacingDir(
                0x4A39, gobj, va_arg(vlist, HSD_JObj*));
        }
        break;
    case 0x50C:
        ret_obj = efLib_Create_Attach(0x4A3AU, gobj, va_arg(vlist, HSD_JObj*));
        if (ret_obj != NULL) {
            effect = ret_obj;
            effect->params.z = *va_arg(vlist, f32*);
            effect->update = efLib_Cb_SetRotYZ_FromParamZ_FighterDir;
        }
        break;
    case 0x50D:
        ret_obj = efLib_Create_Attach(0x4A3BU, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x50E:
        ret_obj =
            efLib_Create_Attach_Scale(0x4A3C, gobj, va_arg(vlist, HSD_JObj*));
        if (ret_obj != NULL) {
            effect = ret_obj;
            rotate_y = Effect_GetFacingRotationY(*va_arg(vlist, f32*));
            jobj_2 = GET_JOBJ(effect->gobj);
            HSD_JObjSetRotationY(jobj_2, rotate_y);
        }
        break;
    case 0x50F:
        ret_obj =
            efLib_Create_Attach_Scale(0x4A3D, gobj, va_arg(vlist, HSD_JObj*));
        if (ret_obj != NULL) {
            effect = ret_obj;
            rotate_y = Effect_GetFacingRotationY(*va_arg(vlist, f32*));
            jobj_2 = GET_JOBJ(effect->gobj);
            HSD_JObjSetRotationY(jobj_2, rotate_y);
        }
        break;
    case 0x510:
        ret_obj = efLib_CreateGenerator_AppSRT_SetFacingDir(0xBF68, vlist);
        break;
    case 0x511:
        ret_obj = efLib_Create_Attach_Scale_FacingDir(
            0xBF68, gobj, va_arg(vlist, HSD_JObj*));
        break;
    case 0x512:
        ret_obj = efLib_Create_Attach_Scale_FacingDir(
            0xBF69, gobj, va_arg(vlist, HSD_JObj*));
        break;
    }
    while (efLib_AnimCount != 0) {
        cnt_2 = efLib_AnimCount - 1;
        efLib_AnimCount = cnt_2;
        HSD_JObjAnimAll(efLib_AnimQueue[cnt_2]);
    }

    va_end(vlist);
    return ret_obj;
}

// ft/ftcoll.c's table (its name is not unique in the game, so it cannot
// be referenced from here).
// Effect IDs spawned on hit, indexed by HitElement (-1 = no effect)
static const int hit_effect_ids[] = {
    /* [HitElement_Normal]   */ Ef_Id_Unk1000,
    /* [HitElement_Fire]     */ Ef_Id_Unk1002,
    /* [HitElement_Electric] */ Ef_Id_Unk1001,
    /* [HitElement_Slash]    */ Ef_Id_Unk1004,
    /* [HitElement_Coin]     */ Ef_Id_Unk1145,
    /* [HitElement_Ice]      */ Ef_Id_Unk1005,
    /* [HitElement_Nap]      */ -1,
    /* [HitElement_Sleep]    */ -1,
    /* [HitElement_Catch]    */ -1,
    /* [HitElement_Ground]   */ Ef_Id_Unk1000,
    /* [HitElement_Cape]     */ Ef_Id_Unk1000,
    /* [HitElement_Inert]    */ -1,
    /* [HitElement_Disable]  */ -1,
    /* [HitElement_Dark]     */ Ef_Id_Unk1046,
    /* [HitElement_Scball]   */ -1,
    /* [HitElement_Lipstick] */ -1,
    /* [HitElement_Leadead]  */ 0,
};

// ft/ftcoll.c (static inline there).
static inline void spawnHitEffect(Fighter_GObj* gobj, int effect, Vec3* pos,
                                  u32 severity, u32 dmg, float kb)
{
    Fighter* fp = gobj->user_data;

    switch (effect) {
    case Ef_Id_Unk1000:
        ftColl_80078538(gobj, pos, severity, dmg, kb);
        break;
    case Ef_Id_Unk1001:
    case Ef_Id_Unk1002:
    case Ef_Id_Unk1004:
    case Ef_Id_Unk1046:
    case Ef_Id_Unk1145:
    case Ef_Id_Unk1255:
        efSync_Spawn(effect, 0, pos);
        break;
    case Ef_Id_Unk1005:
        efSync_Spawn(effect, 0, pos, &fp->facing_dir);
        break;
    case Ef_Id_Unk1003:
        break;
    }
}

struct DmgResult {
    /* 0x00 */ float dir;
    /* 0x04 */ int angle;
    /* 0x08 */ int hurt_height;
    /* 0x0C */ float kb;
    /* 0x10 */ Vec3 pos;
    /* 0x1C */ u32 element;
    /* 0x20 */ int sfx_severity;
    /* 0x24 */ HSD_GObj* source;
    /* 0x28 */ float damage;
};

struct ftColl_8007A06C_best_kb {
    float v;
};

/// Replaces ftColl_8007A06C (`function` hook).
void tm_hitbox_ApplyHits(Fighter_GObj* gobj, void* dmg_ptr, void* log,
                         size_t idx, int arg4)
{
    float angle;
    float dir;
    struct ftColl_8007A06C_best_kb best_kb;
    int angle_int;
    u32 element;
    ftCo_DatAttrs* co;
    DmgLogEntry* entry;
    DmgLogEntry* entries;
    struct DmgResult* out;
    Fighter* fp;
    int i;
    int best_idx;
    DmgLogEntry* best_entry;
    int sfx_severity;
    Item* ip;
    HitCapsule* hit;
    int unk_count;
    HSD_GObj* tail_owner_gobj;
    HitCapsule stack_hit;

    PAD_STACK(0x78);

    if (idx == 0) {
        return;
    }

    fp = (Fighter*) gobj->user_data;
    co = &fp->co_attrs;
    entries = (DmgLogEntry*) log;
    best_kb.v = -1.0F;

    for (i = 0, entry = entries; i < idx; entry++, i++) {
        float kb;

        switch (entry->x0) {
        case 1: {
            Fighter* attacker_fp;
            unk_count = entry->size_of_xC;
            attacker_fp = (Fighter*) entry->gobj->user_data;
            hit = entry->xC.hit0;
            kb = ftColl_80079C70(fp, attacker_fp, hit, unk_count);

            // TM-CE: Hide OnHit GFX When Hitboxes Enabled.asm (+0x114):
            // no hit spark on a fighter whose hitboxes are shown.
            if (arg4 != 0 && !fp->x21FC_flag.x0.b6) {
                u32 dmg = entry->x20;
                int effect = hit_effect_ids[entry->xC.hit0->element];
                spawnHitEffect(gobj, effect, &entry->pos,
                               entry->xC.hit0->sfx_severity, dmg, kb);
            }
            break;
        }

        case 2: {
            Item* item = (Item*) entry->gobj->user_data;
            HSD_GObj* owner = item->owner;
            float attack;

            if (ftLib_IsFighter(owner)) {
                attack = Player_GetAttackRatio(
                    ((Fighter*) owner->user_data)->player_idx);
            } else {
                attack = 1.0F;
            }
            kb = ftColl_80079AB0(
                fp, entry->xC.hit0, entry->size_of_xC, gm_8016B248(), attack,
                Player_GetDefenseRatio(fp->player_idx), co->weight);

            // TM-CE: Hide OnHit GFX When Hitboxes Enabled 2.asm (+0x3C4).
            if (arg4 != 0 && !fp->x21FC_flag.x0.b6) {
                u32 dmg = entry->x20;
                int effect = hit_effect_ids[entry->xC.hit0->element];
                spawnHitEffect(gobj, effect, &entry->pos,
                               entry->xC.hit0->sfx_severity, dmg, kb);
            }
            break;
        }

        case 3:
            lbColl_80008D30(&stack_hit, entry->xC.unk_anim0);
            kb = ftColl_80079AB0(
                fp, &stack_hit, stack_hit.unk_count, gm_8016B248(), 1.0F,
                Player_GetDefenseRatio(fp->player_idx), co->weight);
            break;
        default:
            break;
        }

        if (kb > best_kb.v) {
            if (entry->x0 == 1 && fp->victim_gobj != NULL &&
                !fp->x221B.x221B_b5 && fp->victim_gobj == entry->gobj)
            {
                fp->x221C_b0 = 1;
            } else {
                fp->x221C_b0 = 0;
            }
            best_kb.v = kb;
            best_idx = i;
        }
    }

    out = (struct DmgResult*) dmg_ptr;
    best_entry = &entries[best_idx];

    switch (best_entry->x0) {
    case 1: {
        Fighter* attacker_fp = (Fighter*) best_entry->gobj->user_data;

        dir = (fp->cur_pos.x > attacker_fp->cur_pos.x) ? -1.0F : 1.0F;
        {
            HitCapsule* hit = best_entry->xC.hit0;
            angle = (float) (u32) hit->kb_angle;
            element = hit->element;
            sfx_severity = hit->sfx_severity;
        }
        break;
    }

    case 2: {
        Item* item = (Item*) best_entry->gobj->user_data;
        float vel_x;

        vel_x = item->x40_vel.x;
        if (vel_x < 0.0F) {
            vel_x = -vel_x;
        }
        dir = (vel_x < it_804D6D28->x78_float)
                  ? ((fp->cur_pos.x > item->pos.x) ? -1.0F : 1.0F)
                  : ((item->x40_vel.x < 0.0F) ? 1.0F : -1.0F);
        {
            HitCapsule* hit = best_entry->xC.hit0;
            angle = (float) (u32) hit->kb_angle;
            element = hit->element;
            sfx_severity = hit->sfx_severity;
        }
        break;
    }

    case 3: {
        lbColl_80008D30_arg1* env = best_entry->xC.unk_anim0;

        dir = fp->facing_dir;
        sfx_severity = 0;
        angle = (float) (u32) env->kb_angle;
        element = env->element;
        break;
    }
    default:
        break;
    }

    if ((u32) best_entry->xC.hit0->kb_angle == 0x16A) {
        FighterHurtCapsule* hurt = best_entry->x10.hurt1;
        float dx, dy, abs_dx;

        dx = 0.5F * (hurt->capsule.a_pos.x + hurt->capsule.b_pos.x) -
             best_entry->pos.x;
        dy = 0.5F * (hurt->capsule.a_pos.y + hurt->capsule.b_pos.y) -
             best_entry->pos.y;

        dir = (dx < 0.0F) ? 1.0F : -1.0F;

        if (dx < 0.0F) {
            abs_dx = -dx;
        } else {
            abs_dx = dx;
        }

        if (abs_dx < 1e-5F) {
            angle_int = 0;
        } else {
            angle_int = (s32) MTXRadToDeg(atanf(dy / abs_dx));
        }
        angle = (float) angle_int;
    }

    out->dir = dir;
    out->angle = (int) angle;
    out->hurt_height = (int) best_entry->x10.hurt1->height;
    out->kb = best_kb.v;
    out->pos = best_entry->pos;
    out->element = element;
    out->source = best_entry->gobj;
    out->damage = best_entry->x20;
    out->sfx_severity = sfx_severity;

    switch (best_entry->x0) {
    case 1: {
        Fighter* attacker_fp = (Fighter*) best_entry->gobj->user_data;
        Fighter_GObj* attacker_gobj = attacker_fp->gobj;
        attacker_fp = (Fighter*) attacker_gobj->user_data;

        ftColl_8007861C(attacker_gobj, gobj, 1, attacker_fp->kind,
                        attacker_fp->x2070.x2070_int, &attacker_fp->x2074,
                        attacker_fp->x2074.x2088, dmg_ptr, 0);
        break;
    }

    case 2: {
        Item* item_sub = (Item*) best_entry->gobj->user_data;
        Fighter* victim_fp = (Fighter*) gobj->user_data;
        HSD_GObj* entity = item_sub->entity;
        ip = (Item*) entity->user_data;
        tail_owner_gobj = ip->owner;

        if (ip->kind == It_Kind_BombHei) {
            u32 b4 = victim_fp->is_sub_fighter;
            int player_id = victim_fp->player_idx;
            pl_80041B08(player_id, (UNK_T) (uintptr_t) b4, (u16) ip->x1C);
        }

        if (ftLib_IsFighter(tail_owner_gobj)) {
            ftColl_8007861C(tail_owner_gobj, gobj, 2, ip->kind,
                            ip->xD90.x2070_int, &ip->xD94, ip->xDA8_short,
                            dmg_ptr, 0);
        } else if (pl_8003D60C(ip->kind)) {
            ftColl_8007861C(NULL, gobj, 2, ip->kind, ip->xD90.x2070_int,
                            &ip->xD94, ip->xDA8_short, dmg_ptr, 1);
        } else {
            ftColl_8007861C(NULL, gobj, 2, ip->kind, ip->xD90.x2070_int,
                            &ip->xD94, ip->xDA8_short, dmg_ptr, 0);
        }
        break;
    }

    case 3: {
        int kind = best_entry->kind;
        ftColl_8007861C(NULL, gobj, 3, kind, 0, 0, 0, dmg_ptr, 1);
        break;
    }
    default:
        break;
    }

    if (out->element == HitElement_Electric) {
        fp->x1960_vibrateMult = p_ftCommonData->x1A4;
    }
}
