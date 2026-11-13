/** @file
 * Setting up a situation: putting a fighter where a scenario needs it
 * instead of getting it there by play.
 *
 * The native counterpart of the course engine's placement
 * (src/tmce/events/course/event.c, which has it from TM-CE's events), on
 * the game's own functions. A fighter is put standing on whatever floor is
 * below a point, or falling from a point, and then is as a fresh one: not
 * holding or held, no speed, the damage asked for, a full shield.
 */
#include "host.h"

#include <stddef.h>

#include <melee/cm/camera.h>
#include <melee/ft/fighter.h>
#include <melee/ft/ft_081B.h>
#include <melee/ft/ft_0892.h>
#include <melee/ft/ft_0D4D.h>
#include <melee/ft/ftcamera.h>
#include <melee/ft/ftcommon.h>
#include <melee/ft/inlines.h>
#include <melee/ft/kinds/ftCommon/ftCo_Fall.h>
#include <melee/ft/kinds/ftCommon/ftCo_Throw.h>
#include <melee/ft/types.h>
#include <melee/mp/mpcoll.h>
#include <melee/mp/mplib.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/jobj.h>

/// How far below the point asked for a floor is looked for.
#define FLOOR_REACH 400.0F

/// Tell everything that keeps its own copy where the fighter now is.
static void moved(HSD_GObj* gobj, Fighter* fp)
{
    HSD_JObj* jobj = gobj->hsd_obj;

    fp->coll_data.cur_pos = fp->cur_pos;
    fp->coll_data.prev_pos = fp->cur_pos;
    fp->coll_data.last_pos = fp->cur_pos;
    fp->coll_data.x28_vec = fp->cur_pos;
    fp->coll_data.x38 = mpColl_804D64AC; /* this frame's collision pass */
    jobj->translate = fp->cur_pos;
    HSD_JObjSetMtxDirtySub(jobj);
    Player_80032828(fp->player_idx, fp->is_sub_fighter, &fp->cur_pos);
}

static void still(Fighter* fp, float facing)
{
    static const Vec3 zero = { 0.0F, 0.0F, 0.0F };

    fp->facing_dir = facing < 0.0F ? -1.0F : 1.0F;
    fp->self_vel = zero;
    fp->x74_self_accel = zero;
    fp->x8c_kb_vel = zero;
}

const char* host_place(int slot, float x, float y, float facing, int air,
                       float percent)
{
    HSD_GObj* gobj = Player_GetEntity(slot);
    Fighter* fp;

    if (gobj == NULL || (fp = GET_FIGHTER(gobj)) == NULL) {
        return "no such fighter";
    }
    /* Let go of whoever it holds, and of it if it is held, the way the game
       ends a grab; otherwise the two stay linked. */
    if (fp->victim_gobj != NULL) {
        ftCo_800DC920(gobj, fp->victim_gobj);
    }
    if (fp->x1A5C != NULL) {
        ftCo_800DC920(fp->x1A5C, gobj);
    }

    if (air) {
        ftCo_800D4F24(gobj, 0); /* as if it had just come back */
        ftCo_800D4FF4(gobj);
        still(fp, facing);
        fp->cur_pos.x = x;
        fp->cur_pos.y = y;
        moved(gobj, fp);
        ftCo_Fall_Enter(gobj);
        fp->x1968_jumpsUsed = 1;
    } else {
        Vec3 pos, normal;
        int line = -1;
        u32 flags = 0;

        if (!mpCheckFloor(x, y + 10.0F, x, y - FLOOR_REACH, 0.0F, &pos, &line,
                          &flags, &normal, -1, -1, -1, NULL, NULL))
        {
            return "no floor below that point";
        }
        still(fp, facing);
        fp->coll_data.floor.index = line;
        fp->cur_pos = pos;
        moved(gobj, fp);
        ft_80084280(gobj);       /* take the floor found */
        ftCommon_8007D6A4(fp);   /* grounded */
        ft_8008A2BC(gobj);       /* standing */
    }
    fp->dmg.x1830_percent = percent;
    Player_SetHUDDamage(fp->player_idx, (int) percent);
    fp->shield_health = p_ftCommonData->x260_startShieldHealth;
    ftCamera_UpdateCameraBox(gobj);
    Camera_8002F3AC();
    return NULL;
}
