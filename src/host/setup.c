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
#include <melee/ft/ft_0881.h>
#include <melee/ft/ft_0D4D.h>
#include <melee/ft/ftcamera.h>
#include <melee/ft/ftcliffcommon.h>
#include <melee/ft/ftcolanimlist.h>
#include <melee/ft/ftcoll.h>
#include <melee/ft/kinds/ftCommon/ftCo_CliffWait.h>
#include <melee/ft/kinds/ftCommon/ftCo_Damage.h>
#include <melee/ft/kinds/ftCommon/ftCo_DamageFall.h>
#include <melee/ft/ftcommon.h>
#include <melee/ft/inlines.h>
#include <melee/ft/kinds/ftCommon/ftCo_Fall.h>
#include <melee/ft/kinds/ftCommon/ftCo_Throw.h>
#include <melee/ft/types.h>
#include <melee/if/ifstatus.h>
#include <melee/if/types.h>
#include <melee/it/forward.h>
#include <melee/it/inlines.h>
#include <melee/it/item.h>
#include <melee/it/types.h>
#include <melee/lb/forward.h>
#include <melee/mp/mpcoll.h>
#include <melee/mp/mplib.h>
#include <melee/pl/player.h>
#include <melee/pl/plstale.h>
#include <melee/sfx/crowdsfx.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjplink.h>
#include <sysdolphin/baselib/jobj.h>
#include <sysdolphin/baselib/psstructs.h>
#include <sysdolphin/baselib/random.h>

extern HSD_Particle* hsd_804D0908[16]; /* particle.c: the particle lists */

/// How far below the point asked for a floor is looked for.
#define FLOOR_REACH 400.0F

/// Where the Ice Climbers' partner goes with its leader (partner).
enum {
    BESIDE_GROUND,   ///< standing where the leader stands
    BESIDE_AIR,      ///< falling with it
    BESIDE_LEDGE,    ///< the leader hangs: standing at the ledge's end
    BESIDE_PLATFORM, ///< on the respawn platform with it
};

static void wake(HSD_GObj* gobj, Fighter* fp);
static void partner(HSD_GObj* leader, int how, const Vec3* ledge);

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

/// Facing that way, with no speed. The ground speed too: a fighter placed
/// in the middle of a move slid on from where it was put (Fox after a jab
/// out of a run, 3.7 units in four frames), and the Ice Climbers' partner
/// walked after it.
static void still(Fighter* fp, float facing)
{
    static const Vec3 zero = { 0.0F, 0.0F, 0.0F };

    fp->facing_dir = facing < 0.0F ? -1.0F : 1.0F;
    fp->self_vel = zero;
    fp->x74_self_accel = zero;
    fp->x8c_kb_vel = zero;
    fp->gr_vel = 0.0F;
    /* and no L or R pressed lately, as a spawn leaves it (Fighter's input
       timers, 255: never): the game techs on a press within 20 frames
       that had none in the 40 before it (ftCo_800986B0), and a press late
       in one attempt locked out the tech of the next, begun at once
       (universal-tech's proof, 2026-11-25) */
    fp->x680 = 255;
    fp->x684 = 255;
    /* and not frozen in a hit: a fighter placed in the middle of its
       hitlag stood frozen for what was left of it in the next attempt (a
       try judged at a hit and reset at once: fox-aerial-confirm's proof,
       2026-11-25, where the opponent then counted as hit and ran its
       answer before anything touched it). Ended as the game ends it
       (Fighter_procUpdate). */
    if (fp->dmg.x195c_hitlag_frames > 0.0F) {
        fp->dmg.x195c_hitlag_frames = 0.0F;
        if (fp->x221A_b3) {
            ftCo_80090718(fp);
            fp->x221A_b3 = 0;
        }
        if (!fp->dmg.x1954 && !fp->x2219_b7) {
            Fighter_8006D10C(fp->gobj);
        }
        fp->allow_sdi = 0;
    }
}

/// Let go of whoever it holds, and of it if it is held, the way the game
/// ends a grab when one of the two leaves it (ftCo_800DD100, as a fighter
/// is KO'd): the other one is back to standing or falling
/// (ftCommon_8007D92C). Otherwise the two stay linked; and a holder left in
/// its grab's state with nobody to hold reads the missing victim in that
/// state's callback (fn_800DA054, from Fighter_procAccessory): the Ice
/// Climbers' partner holding the opponent as the next attempt placed the
/// opponent, and the game fell over (signal 11).
static void release(HSD_GObj* gobj, Fighter* fp)
{
    if (fp->victim_gobj != NULL) {
        ftCo_800DD100(gobj);
    }
    /* x1A5C alone: the one holding it, or the partner Popo's side special
       takes along (ftpopospecials.c) */
    if (fp->x1A5C != NULL) {
        HSD_GObj* other = fp->x1A5C;
        ftCo_800DC920(other, gobj);
        if (host_live_fighter(other)) {
            ftCommon_8007D92C(other);
        }
    }
}

static int find_ledge(Vec3* pos, int right);

static int left_ledge(Vec3* pos)
{
    return find_ledge(pos, 0);
}

/// The stage's left or `right` ledge: the end of the floor under the
/// middle of the stage, followed that way (a floor line's v0 is its left
/// end, v1 its right).
static int find_ledge(Vec3* pos, int right)
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
        int next = right ? mpLineGetNext(line) : mpLineGetPrev(line);
        if (next < 0 || (lines[next].flags & LINE_FLAG_KIND) != CollLine_Floor)
        {
            break;
        }
        line = next;
    }
    if (right) {
        mpLib_80053DA4_Floor(line, pos);
    } else {
        mpLib_80053ECC_Floor(line, pos);
    }
    return line;
}

const char* host_ledge(int slot, float percent)
{
    return host_ledge_side(slot, percent, 0);
}

const char* host_ledge_side(int slot, float percent, int right)
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
    wake(gobj, fp); /* from host_sleep, its damage display too */
    line = find_ledge(&pos, right);
    if (line < 0) {
        return "no ledge found";
    }
    /* As the course engine does it (src/tmce/events/course/event.c,
       course_PlaceOnLedge, TM-CE's Fighter_PlaceOnLedge): as if it had
       just come back, then hanging, then put where hanging puts it. */
    release(gobj, fp);
    still(fp, right ? -1.0F : 1.0F);
    fp->used_tether = 0;
    ftCo_800D4F24(gobj, 0);
    ftCo_800D4FF4(gobj);
    /* facing the stage: right on the left ledge, left on the right */
    fp->facing_dir = right ? -1.0F : 1.0F;
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
    partner(gobj, BESIDE_LEDGE, &pos);
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

/* --- the Ice Climbers' partner -------------------------------------------- */

/// The partner of the player whose fighter this is (Nana, the Ice
/// Climbers' second fighter), or NULL: none, or not one that follows (Zelda
/// and Sheik's second fighter is the other form).
static HSD_GObj* partner_of(HSD_GObj* leader)
{
    Fighter* lp = GET_FIGHTER(leader);
    HSD_GObj* gobj;

    if (lp->is_sub_fighter) {
        return NULL;
    }
    gobj = Player_GetEntityAtIndex(lp->player_idx, 1);
    if (gobj == NULL || gobj == leader || !host_live_fighter(gobj) ||
        GET_FIGHTER(gobj)->kind != Ft_Kind_Nana)
    {
        return NULL;
    }
    return gobj;
}

/// The partner, standing on the floor under (x, y) no more than `reach`
/// below it; 0 if there is none.
static int partner_stand(HSD_GObj* gobj, Fighter* fp, float x, float y,
                         float reach)
{
    Vec3 pos, normal;
    int line = -1;
    u32 flags = 0;

    if (!mpCheckFloor(x, y + 10.0F, x, y - reach, 0.0F, &pos, &line, &flags,
                      &normal, -1, -1, -1, NULL, NULL))
    {
        return 0;
    }
    fp->coll_data.floor.index = line;
    fp->cur_pos = pos;
    moved(gobj, fp);
    ft_80084280(gobj);     /* take the floor found */
    ftCommon_8007D6A4(fp); /* grounded */
    ft_8008A2BC(gobj);     /* standing */
    still(fp, fp->facing_dir);
    /* (that left her 12.5 below the floor, on collision data from before
       the respawn, until the next frame put her back on it) */
    fp->cur_pos = pos;
    moved(gobj, fp);
    return 1;
}

/// A stick's value as the partner's log keeps it (inlineM0 in
/// ftCo_0A01.c).
static s8 log_stick(float v)
{
    return (s8) (int) (v >= 0.0F ? 127.0F * v : 128.0F * v);
}

/// Her log of the leader (ftCo_800B0918 writes an entry a frame from him;
/// she plays the one five behind): every entry what he is and holds now,
/// as if she had followed him standing there. The respawn's reset
/// (ftCo_800A101C) leaves the C-stick of the last attempt in it, and she
/// down-smashed the opponent with it as the next attempt began
/// (universal-asdi, whose examples hold the C-stick down). TM-CE's
/// savestate load fills it with his position and facing. And what she
/// holds is what he holds: her CPU's pad is the log's (ftCo_800B0AF4 sets
/// it so) and her input record his, so that a stick he holds through the
/// reset (a person's: the drills leave a live pad as it is) is not a new
/// press for her either, a smash attack he does not do.
static void partner_log(Fighter* lp, Fighter* fp)
{
    struct CpuFighter* cpu = &fp->cpu;

    for (size_t i = 0; i < sizeof cpu->xFC / sizeof cpu->xFC[0]; i++) {
        struct Fighter_x1A88_xFC_t* e = &cpu->xFC[i];
        e->lstick.x = log_stick(lp->input.lstick[0].x);
        e->lstick.y = log_stick(lp->input.lstick[0].y);
        e->cstick.x = log_stick(lp->input.cstick[0].x);
        e->cstick.y = log_stick(lp->input.cstick[0].y);
        e->x4 = (u8) lp->input.triggers[0];
        e->x5 = (u8) lp->input.triggers[0];
        e->x0 = lp->input.held_buttons[0];
        e->cur_pos = lp->cur_pos;
        e->facing_dir = lp->facing_dir;
    }
    cpu->lstick = cpu->xFC[0].lstick;
    cpu->cstick = cpu->xFC[0].cstick;
    cpu->buttons = cpu->xFC[0].x0;
    cpu->ltrigger = cpu->xFC[0].x4;
    cpu->rtrigger = cpu->xFC[0].x5;
    fp->input = lp->input;
}

/// Put the partner back with its leader, just placed, as the game brings
/// the two back on a respawn (Player_80032070: the leader's Rebirth brings
/// her back too). She follows a log of the leader's inputs and positions
/// over the last 30 frames (the CPU's xFC, TM-CE's leader_log); left as
/// she was, she walked back to where he had been and played what he had
/// done there: through the opponent, into its attack, onto it. So whatever
/// the last attempt left on her is gone, as a KO leaves it (a grab, what
/// she held, a hit: ftCo_800D4F24; nothing if she is asleep), she is fresh
/// as at a respawn (Fighter_Spawn, from ftCo_800D4FF4: her damage, shield,
/// jumps, her CPU's state), and her log is of the leader as he is now
/// (partner_log). Where: where she comes to rest by herself, on the
/// leader. The game starts a match with the two 10 apart (each at the
/// spawn point plus its own x40 along the facing: Popo 5 in front, Nana 5
/// behind, Fighter_UnkInitReset_80067C98), and she walks up to him within
/// a second; put 10 behind him, she walked too. She has the leader's
/// damage.
static void partner(HSD_GObj* leader, int how, const Vec3* ledge)
{
    Fighter* lp = GET_FIGHTER(leader);
    HSD_GObj* gobj = partner_of(leader);
    Fighter* fp;
    u32 seed;

    if (gobj == NULL) {
        return;
    }
    fp = GET_FIGHTER(gobj);
    release(gobj, fp);
    ftCo_800D4F24(gobj, 0);
    /* (her CPU's reset draws a random number; the attempt's are those the
       drill seeded) */
    seed = *HSD_RandSeedPtr;
    ftCo_800D4FF4(gobj);
    *HSD_RandSeedPtr = seed;
    if (how != BESIDE_PLATFORM) {
        ftCo_800C0200(fp, 9); /* not the respawn's flash */
    }
    still(fp, lp->facing_dir);
    fp->used_tether = 0;
    switch (how) {
    case BESIDE_GROUND:
        if (partner_stand(gobj, fp, lp->cur_pos.x, lp->cur_pos.y, 10.0F)) {
            break;
        }
        how = BESIDE_AIR; /* (no floor found: falling there) */
        /* fallthrough */
    case BESIDE_AIR:
    case BESIDE_PLATFORM:
        fp->cur_pos = lp->cur_pos;
        moved(gobj, fp);
        if (how == BESIDE_AIR) {
            ftCo_Fall_Enter(gobj);
            fp->x1968_jumpsUsed = lp->x1968_jumpsUsed;
        } else {
            /* waiting on the platform, as the leader, until it leaves
               (ftCo_RebirthWait_IASA: she goes when he does) */
            ftCo_800D5600(gobj);
            fp->phys_cb = rebirth_stay;
        }
        break;
    case BESIDE_LEDGE:
        /* Two cannot hang on one ledge (ft_80082E3C): she stands at its
           end, on the stage, and stays there */
        if (!partner_stand(gobj, fp, ledge->x, ledge->y, 10.0F)) {
            partner_stand(gobj, fp, ledge->x + 5.0F * lp->facing_dir, ledge->y,
                          10.0F);
        }
        break;
    }
    fp->dmg.x1830_percent = lp->dmg.x1830_percent;
    partner_log(lp, fp);
    ftCamera_UpdateCameraBox(gobj);
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

/* --- shields kept full ---------------------------------------------------- */

/// A fighter whose shield a drill keeps at a health (a drill's "shield":
/// "infinite": the owner, 2026-11-15). It is set again at every frame
/// boundary, as the anchors are: the frames played for real and those a
/// search or a lookahead plays (engine.c, ahead.c, forked games), so what
/// they foresee is what happens. Set only by the driver between frames, the
/// live shield was full and a searched one shrank: a light shield's worth
/// bigger, an attack met it frames sooner than the search said (Marth's
/// nair's first hit, its second foreseen), and the answer the search had
/// found no longer reached (tools/melee_engine/feel.py). Until "shield P H
/// 0", "shield -1" or another fighter in the slot.
static struct {
    HSD_GObj* gobj;
    float health;
} kept[6];

const char* host_keep_shield(int slot, float health, int on)
{
    HSD_GObj* gobj;

    if (slot < 0) {
        memset(kept, 0, sizeof kept);
        return NULL;
    }
    if (slot >= 6) {
        return "no such fighter";
    }
    gobj = Player_GetEntity(slot);
    if (!on) {
        kept[slot].gobj = NULL;
        return host_set_shield(slot, health);
    }
    if (gobj == NULL || !host_live_fighter(gobj)) {
        return "no such fighter";
    }
    kept[slot].gobj = gobj;
    kept[slot].health = health;
    return host_set_shield(slot, health);
}

static void keep_shields(void)
{
    for (int i = 0; i < 6; i++) {
        HSD_GObj* gobj = kept[i].gobj;

        if (gobj == NULL) {
            continue;
        }
        if (Player_GetEntity(i) != gobj || !host_live_fighter(gobj)) {
            kept[i].gobj = NULL; /* a new match, another fighter */
            continue;
        }
        GET_FIGHTER(gobj)->shield_health = kept[i].health;
    }
}

void host_anchor_frame(void)
{
    keep_shields();
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
    wake(gobj, fp); /* from host_sleep, its damage display too */
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
    partner(gobj, BESIDE_PLATFORM, NULL);
    ftCamera_UpdateCameraBox(gobj);
    Camera_8002F3AC();
    return NULL;
}

int host_left_ledge(float* x, float* y)
{
    return host_ledge_at(0, x, y);
}

int host_ledge_at(int right, float* x, float* y)
{
    Vec3 pos;
    int line = find_ledge(&pos, right);
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

static int is_fighter(HSD_GObj* gobj)
{
    for (int slot = 0; slot < 6; slot++) {
        if (gobj != NULL && (Player_GetEntityAtIndex(slot, 0) == gobj ||
                             Player_GetEntityAtIndex(slot, 1) == gobj))
        {
            return 1;
        }
    }
    return 0;
}

/// Whether a fighter still points at this item: one it holds or uses (a
/// held item, Fox's blaster, a charging shot), which the fighter's own code
/// lets go of (the blaster removes itself once Fox stands). Destroying it
/// under the fighter left a dangling pointer, and the game fell over in
/// the blaster's code. Any word of a fighter's data equal to the item's
/// object or its data counts.
static int held(HSD_GObj* item)
{
    const void* data = item->user_data;

    for (int slot = 0; slot < 6; slot++) {
        for (int sub = 0; sub < 2; sub++) {
            HSD_GObj* gobj = Player_GetEntityAtIndex(slot, sub);
            const uint32_t* w;
            if (gobj == NULL || !host_live_fighter(gobj)) {
                continue;
            }
            w = (const uint32_t*) gobj->user_data;
            for (size_t i = 0; i < sizeof(Fighter) / 4; i++) {
                if (w[i] == (uint32_t) (uintptr_t) item ||
                    w[i] == (uint32_t) (uintptr_t) data)
                {
                    return 1;
                }
            }
        }
    }
    return 0;
}

/// TM-CE's clean slate (Savestate_Load_v1, savestate_v1.c), for an attempt
/// that starts again in the middle of a match: what the last one left
/// behind is gone the frame the fighters are put back, and the moves are
/// fresh again (TM-CE puts back the stale-move queue it saved as the match
/// began), so a tenth attempt hits as hard as the first.
void host_clean(void)
{
    HSD_GObj* gobj;
    HSD_GObj* next;

    for (int slot = 0; slot < 6; slot++) {
        if (Player_GetEntity(slot) != NULL) {
            plStale_ResetStaleMoveTableForPlayer(slot);
        }
        for (int sub = 0; sub < 2; sub++) {
            gobj = Player_GetEntityAtIndex(slot, sub);
            if (gobj != NULL && host_live_fighter(gobj)) {
                Fighter* fp = GET_FIGHTER(gobj);
                ft_80088A50(fp);       /* its sounds (SFX_StopAllFighterSFX) */
                ftCo_800C0200(fp, 9);  /* its colour overlay */
            }
        }
    }
    un_80321CE8(); /* the crowd's cheering (SFX_StopCrowd) */
    /* the fighters' items let go of: a laser in flight, a thrown turnip
       (Item_Destroy); not what a fighter still holds */
    for (gobj = HSD_GObjPLinkHead[HSD_GOBJ_PLINK_ITEM]; gobj != NULL;
         gobj = next)
    {
        next = gobj->next;
        if (is_fighter(GET_ITEM(gobj)->owner) && !held(gobj)) {
            Item_8026A8EC(gobj);
        }
    }
    /* Particles: TM-CE frees them by hand; here each ends on its next
       update, this same frame, through the game's own delete
       (hsd_8039930C's life count). */
    for (int i = 0; i < 16; i++) {
        for (HSD_Particle* pp = hsd_804D0908[i]; pp != NULL; pp = pp->next) {
            pp->life = 1;
        }
    }
    /* Not TM-CE's camera shakes (class 3 on link 18): the stage's objects
       are class 3 too, and the camera keeps its looping shake
       (Camera_RequestQuake's quake_gobj); freeing them crashed the game a
       few attempts later. A one-shot shake ends by itself after 22 frames,
       before a verdict's pause is over. */
}

/// Out of play, as between a lost stock and the respawn (TM-CE's
/// Fighter_EnterSleep): not drawn, not hit, not followed by the camera,
/// and its damage display gone. A drill without an opponent keeps the
/// match's one this way instead of loading a match without it; placing it
/// brings it back (wake).
const char* host_sleep(int slot)
{
    HSD_GObj* gobj = Player_GetEntity(slot);
    Fighter* fp;

    if (gobj == NULL || !host_live_fighter(gobj) ||
        (fp = GET_FIGHTER(gobj)) == NULL)
    {
        return "no such fighter";
    }
    if (!fp->is_sleeping) {
        release(gobj, fp);
        ftCo_800D4F24(gobj, 0); /* Fighter_EnterSleep, no effect */
        ifStatus_802F6788((u8) slot);
        Camera_8002F3AC();
    }
    /* the Ice Climbers' partner with it (placing the leader brings her
       back: partner) */
    if ((gobj = partner_of(gobj)) != NULL && !GET_FIGHTER(gobj)->is_sleeping) {
        release(gobj, GET_FIGHTER(gobj));
        ftCo_800D4F24(gobj, 0);
    }
    return NULL;
}

/// Back in play from host_sleep, as a respawn starts (Fighter_EnterRebirth),
/// with its damage display again; the placement that follows puts it where
/// it is wanted.
static void wake(HSD_GObj* gobj, Fighter* fp)
{
    if (!fp->is_sleeping) {
        return;
    }
    ftCo_800D4FF4(gobj);
    if (ifStatus_GetHUDInfo()->players[fp->player_idx].HUD_parent_entity ==
        NULL)
    {
        ifStatus_802F6E1C(fp->player_idx);
    }
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
    wake(gobj, fp);
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
        /* no speed again: grounding gives it the last animation's own
           motion (ftCommon_8007D6A4, x6A4_transNOffset) */
        still(fp, facing);
    }
    fp->dmg.x1830_percent = percent;
    Player_SetHUDDamage(fp->player_idx, (int) percent);
    fp->shield_health = p_ftCommonData->x260_startShieldHealth;
    partner(gobj, air ? BESIDE_AIR : BESIDE_GROUND, NULL);
    ftCamera_UpdateCameraBox(gobj);
    Camera_8002F3AC();
    return NULL;
}

/// A fighter in the air knocked away by the game's own launch
/// (ftCo_8008DCE0, as a throw's release calls it: ftCo_Throw.c): the damage
/// state its knockback gives (DamageFly from about 80 units on), the
/// knockback's speed and decay, its hitstun, the tumble after it.
static void knock(HSD_GObj* gobj, Fighter* fp, float kb, int angle,
                  float dir)
{
    fp->dmg.kb_applied = kb;
    fp->dmg.x1848_kb_angle = angle;
    /* knocked the way it does not face */
    fp->dmg.facing_dir_1 = dir < 0.0F ? 1.0F : -1.0F;
    fp->dmg.x184c_damaged_hurtbox = 1;
    fp->dmg.x1860_element = HitElement_Normal;
    fp->dmg.x1838_percentTemp = 0.0F;
    fp->dmg.x18ac_time_since_hit = 0;
    ftCo_8008DCE0(gobj, -1, 0.0F);
    /* (the frame's damage step would launch it again) */
    fp->dmg.kb_applied = 0.0F;
}

/// A fighter knocked off its feet at (x, y), as a hit there would leave
/// it: an edgeguard's start (TM-CE's edgeguard event, Reset_CPU in
/// src/edgeguard.c, which writes the damage state, the speed and the
/// hitstun itself; here the game's own launch does). `kb` units of
/// knockback at `angle` degrees above level, toward +x (`dir` > 0) or -x;
/// `percent` its damage; `jumps` the jumps it has used (1: the double jump
/// left, 2: gone). No hitlag: it flies from the coming frame. The Ice
/// Climbers' partner is knocked away with its leader.
const char* host_launch(int slot, float x, float y, float percent, float kb,
                        int angle, float dir, int jumps)
{
    HSD_GObj* gobj = Player_GetEntity(slot);
    HSD_GObj* other;
    Fighter* fp;

    if (gobj == NULL || !host_live_fighter(gobj) ||
        (fp = GET_FIGHTER(gobj)) == NULL)
    {
        return "no such fighter";
    }
    if (kb <= 0.0F) {
        return "no knockback";
    }
    wake(gobj, fp);
    release(gobj, fp);
    ftCo_800D4F24(gobj, 0); /* as if it had just come back */
    ftCo_800D4FF4(gobj);
    still(fp, dir < 0.0F ? 1.0F : -1.0F);
    fp->cur_pos.x = x;
    fp->cur_pos.y = y;
    moved(gobj, fp);
    ftCo_Fall_Enter(gobj);
    fp->x1968_jumpsUsed = (u8) (jumps < 1 ? 1 : jumps);
    fp->dmg.x1830_percent = percent;
    Player_SetHUDDamage(fp->player_idx, (int) percent);
    fp->shield_health = p_ftCommonData->x260_startShieldHealth;
    partner(gobj, BESIDE_AIR, NULL);
    knock(gobj, fp, kb, angle, dir);
    other = partner_of(gobj);
    if (other != NULL) {
        knock(other, GET_FIGHTER(other), kb, angle, dir);
    }
    ftCamera_UpdateCameraBox(gobj);
    Camera_8002F3AC();
    return NULL;
}
