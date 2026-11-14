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
#include <string.h>

#include <melee/cm/camera.h>
#include <melee/ft/fighter.h>
#include <melee/ft/ft_081B.h>
#include <melee/ft/ft_0892.h>
#include <melee/ft/ft_0D4D.h>
#include <melee/ft/ftcamera.h>
#include <melee/ft/ftcliffcommon.h>
#include <melee/ft/ftcoll.h>
#include <melee/ft/kinds/ftCommon/ftCo_CliffWait.h>
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

/// Let go of whoever it holds, and of it if it is held, the way the game
/// ends a grab; otherwise the two stay linked.
static void release(HSD_GObj* gobj, Fighter* fp)
{
    if (fp->victim_gobj != NULL) {
        ftCo_800DC920(gobj, fp->victim_gobj);
    }
    if (fp->x1A5C != NULL) {
        ftCo_800DC920(fp->x1A5C, gobj);
    }
}

static int left_ledge(Vec3* pos)
{
    CollLine* lines = mpGetGroundCollLine();
    Vec3 hit, normal;
    int line = -1;
    u32 flags = 0;

    if (!mpCheckFloor(0.0F, 5.0F, 0.0F, -FLOOR_REACH, 0.0F, &hit, &line,
                      &flags, &normal, -1, -1, -1, NULL, NULL))
    {
        return -1;
    }
    for (int k = 0; k < 64; k++) {
        int prev = mpLineGetPrev(line);
        if (prev < 0 || (lines[prev].flags & LINE_FLAG_KIND) != CollLine_Floor)
        {
            break;
        }
        line = prev;
    }
    mpLib_80053ECC_Floor(line, pos);
    return line;
}

const char* host_ledge(int slot, float percent)
{
    HSD_GObj* gobj = Player_GetEntity(slot);
    Fighter* fp;
    Vec3 pos;
    int line;

    if (gobj == NULL || !host_live_fighter(gobj) ||
        (fp = GET_FIGHTER(gobj)) == NULL)
    {
        return "no such fighter";
    }
    line = left_ledge(&pos);
    if (line < 0) {
        return "no ledge found";
    }
    /* As the course engine does it (src/tmce/events/course/event.c,
       course_PlaceOnLedge, TM-CE's Fighter_PlaceOnLedge): as if it had
       just come back, then hanging, then put where hanging puts it. */
    release(gobj, fp);
    still(fp, 1.0F);
    fp->used_tether = 0;
    ftCo_800D4F24(gobj, 0);
    ftCo_800D4FF4(gobj);
    fp->facing_dir = 1.0F; /* a left ledge: facing the stage */
    fp->mv.co.cliff.ledge_id = line;
    ftCo_8009A804(gobj);
    fp->mv.co.cliff.x8 = 0; /* TM-CE's FtCliffCatch.timer (x4 is the
                               frames left before it lets go by itself) */
    ftCommon_8007D5D4(fp); /* airborne */
    ftCommon_UnlockECB(fp);
    mpColl_80048160(&fp->coll_data);
    ftCo_CliffCatch_Phys(gobj);
    moved(gobj, fp);
    ftColl_8007B760(gobj, p_ftCommonData->x49C + 1);
    fp->dmg.x1830_percent = percent;
    Player_SetHUDDamage(fp->player_idx, (int) percent);
    ftCamera_UpdateCameraBox(gobj);
    Camera_8002F3AC();
    return NULL;
}

/// The respawn wait's physics while it is a drill's start: the fighter
/// stays where it was put and the wait never runs out (TM-CE's
/// RebirthWait_Phys: "infinite time"). The game's own moves it toward the
/// player's spawn point.
static void rebirth_stay(HSD_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);

    fp->mv.co.common.x0 = 2;
    fp->self_vel.x = 0.0F;
    fp->self_vel.y = 0.0F;
}

/* --- fighters held in place ----------------------------------------------- */

/// A fighter a drill holds where it stands (the owner, 2026-11-13: in the
/// aerial-into-shine drill the player should not push the shielding
/// opponent around the stage). At every frame boundary its sideways
/// speeds, the shield pushback among them (gr_vel, set by a hit on the
/// shield, ftCo_80092F2C), are cleared and it is put back where it was
/// anchored.
static struct {
    HSD_GObj* gobj;
    float x;
} anchors[6];

const char* host_anchor(int slot, int on)
{
    HSD_GObj* gobj;

    if (slot < 0) {
        memset(anchors, 0, sizeof anchors);
        return NULL;
    }
    if (slot >= 6) {
        return "no such fighter";
    }
    gobj = Player_GetEntity(slot);
    if (!on) {
        anchors[slot].gobj = NULL;
        return NULL;
    }
    if (gobj == NULL || !host_live_fighter(gobj)) {
        return "no such fighter";
    }
    anchors[slot].gobj = gobj;
    anchors[slot].x = GET_FIGHTER(gobj)->cur_pos.x;
    return NULL;
}

void host_anchor_frame(void)
{
    for (int i = 0; i < 6; i++) {
        HSD_GObj* gobj = anchors[i].gobj;
        Fighter* fp;

        if (gobj == NULL) {
            continue;
        }
        if (Player_GetEntity(i) != gobj || !host_live_fighter(gobj)) {
            anchors[i].gobj = NULL; /* a new match, another fighter */
            continue;
        }
        fp = GET_FIGHTER(gobj);
        fp->gr_vel = 0.0F;
        fp->self_vel.x = 0.0F;
        fp->x8c_kb_vel.x = 0.0F;
        if (fp->cur_pos.x != anchors[i].x) {
            fp->cur_pos.x = anchors[i].x;
            moved(gobj, fp);
        }
    }
}

const char* host_rebirth(int slot, float x, float y)
{
    HSD_GObj* gobj = Player_GetEntity(slot);
    Fighter* fp;

    if (gobj == NULL || !host_live_fighter(gobj) ||
        (fp = GET_FIGHTER(gobj)) == NULL)
    {
        return "no such fighter";
    }
    /* As TM-CE's ledgedash event starts on the respawn platform (its
       OPTPOS_RESPAWNPLAT, ledgedash.c): the respawn, then the wait on the
       platform, which the fighter leaves by itself after a while or with
       any input; then where the platform is drawn. */
    release(gobj, fp);
    still(fp, x > 0.0F ? -1.0F : 1.0F); /* facing the middle */
    fp->used_tether = 0;
    ftCo_800D4F24(gobj, 0);
    ftCo_800D4FF4(gobj);
    fp->cur_pos.x = x;
    fp->cur_pos.y = y;
    fp->cur_pos.z = 0.0F;
    moved(gobj, fp);
    ftCo_800D5600(gobj);
    fp->phys_cb = rebirth_stay;
    fn_800D54A4(gobj);
    ftCamera_UpdateCameraBox(gobj);
    Camera_8002F3AC();
    return NULL;
}

int host_left_ledge(float* x, float* y)
{
    Vec3 pos;
    int line = left_ledge(&pos);
    *x = pos.x;
    *y = pos.y;
    return line;
}

const char* host_set_shield(int slot, float health)
{
    HSD_GObj* gobj = Player_GetEntity(slot);
    Fighter* fp;

    if (gobj == NULL || !host_live_fighter(gobj) ||
        (fp = GET_FIGHTER(gobj)) == NULL)
    {
        return "no such fighter";
    }
    fp->shield_health = health;
    return NULL;
}

const char* host_place(int slot, float x, float y, float facing, int air,
                       float percent)
{
    HSD_GObj* gobj = Player_GetEntity(slot);
    Fighter* fp;

    if (gobj == NULL || !host_live_fighter(gobj) ||
        (fp = GET_FIGHTER(gobj)) == NULL)
    {
        return "no such fighter";
    }
    release(gobj, fp);

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
