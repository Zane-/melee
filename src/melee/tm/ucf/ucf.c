#include "ucf.h"

#include "../osdact/osdact.h"
#include "../osdtech/osdtech.h"

#include <math.h>
#include <dolphin/pad.h>
#include <melee/ft/fighter.h>
#include <melee/ft/inlines.h>
#include <melee/ft/kinds/ftCommon/ftCo_0A01.h>
#include <melee/ft/kinds/ftCommon/ftCo_AppealS.h>
#include <melee/ft/kinds/ftCommon/ftCo_Attack1.h>
#include <melee/ft/kinds/ftCommon/ftCo_Attack100.h>
#include <melee/ft/kinds/ftCommon/ftCo_AttackHi3.h>
#include <melee/ft/kinds/ftCommon/ftCo_AttackHi4.h>
#include <melee/ft/kinds/ftCommon/ftCo_AttackLw3.h>
#include <melee/ft/kinds/ftCommon/ftCo_AttackLw4.h>
#include <melee/ft/kinds/ftCommon/ftCo_AttackS3.h>
#include <melee/ft/kinds/ftCommon/ftCo_AttackS4.h>
#include <melee/ft/kinds/ftCommon/ftCo_Damage.h>
#include <melee/ft/kinds/ftCommon/ftCo_DamageFall.h>
#include <melee/ft/kinds/ftCommon/ftCo_Escape.h>
#include <melee/ft/kinds/ftCommon/ftCo_Guard.h>
#include <melee/ft/kinds/ftCommon/ftCo_HammerWait.h>
#include <melee/ft/kinds/ftCommon/ftCo_Jump.h>
#include <melee/ft/kinds/ftCommon/ftCo_Pass.h>
#include <melee/ft/kinds/ftCommon/ftCo_SpecialS.h>
#include <melee/ft/kinds/ftCommon/ftCo_SquatRv.h>
#include <melee/ft/kinds/ftCommon/ftCo_Turn.h>
#include <melee/ft/kinds/ftCommon/types.h>
#include <melee/ft/kinds/ftZelda/forward.h>
#include <melee/ft/types.h>
#include <melee/lb/lb_00CE.h>
#include <melee/mp/mpcoll.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/controller.h>

/* File-local in the vanilla sources. */
void ftCo_SquatRv_Enter(Fighter_GObj* gobj);
void ftCo_80099894(Fighter_GObj* gobj);

u8 tm_ucf_off;

/* --- whose UCF ------------------------------------------------------------ */

/// The instruction at @p off in vanilla function @p fn.
#define SITE(fn, off) (*(u32*) ((u8*) (fn) + (off)))

/// The eight places UCF's assembly goes, and what the game has there.
bool tm_ucf_Active(void)
{
    if (tm_ucf_off) {
        return false;
    }
#ifdef TARGET_PC
    /* The native build (tools/native_build.py): its functions are this
       machine's code, and nobody injects anything into them. */
    return true;
#endif
    return SITE(Fighter_procInput, 0x750) == 0x887F0678 &&         /* lbz */
           SITE(ftCo_Turn_IASA, 0x4C) == 0xD01F002C &&             /* stfs */
           SITE(ftCo_SquatRv_CheckInput, 0x14) == 0xC0040094 &&    /* lfs */
           SITE(ftCo_Damage_OnEveryHitlag, 0x5C) == 0x7C002800 &&  /* cmpw */
           SITE(ftCo_80093240, 0x54) == 0x7C030000 &&              /* cmpw */
           SITE(ftCo_DamageFall_IASA, 0xCC) == 0x7C030000 &&       /* cmpw */
           SITE(ftCo_8009A080, 0x38) == 0x4C401382 &&              /* cror */
           SITE(ftCo_80099894, 0x10) == 0x8083002C;                /* lwz */
}

/* --- the stick's recent past ---------------------------------------------- */

/// What UCF keeps for each controller port.
typedef struct UcfPort {
    s8 xy[4][2]; ///< the raw stick in the last four frames, newest at #at
    u8 at;
    /// Frames the stick has now been at the rim below the shield drop line,
    /// counted from a fast move down; 0 if it got there slowly.
    u8 drop;
} UcfPort;

static UcfPort hist[4];

/// The fighter Fighter_procInput is working on.
static Fighter* input_fp;

static UcfPort* Port(Fighter* fp)
{
    /* UCF indexes by the pad port with no check; only 0..3 exist. */
    return &hist[fp->pad_port & 3];
}

/// How far the raw stick moved on axis @p axis over the last two frames.
static int Moved(UcfPort* h, int axis)
{
    return h->xy[h->at][axis] - h->xy[(h->at - 2) & 3][axis];
}

/// A stick value in the game's units (1/80), by UCF's rounding, plus the 2
/// its rim test adds.
static int Units(float v)
{
    return (int) (fabsf(v) * 80.0F - 0.0001F) + 2;
}

/// Whether the stick is at the rim: more than 80 units from the centre
/// after UCF's rounding.
static bool AtRim(float a, float b)
{
    int ia = Units(a);
    int ib = Units(b);
    return ia * ia + ib * ib > 6400;
}

/* --- Fighter_procInput+0x750: pad buffer, 1.0 cardinals ------------------- */

/// A raw stick pushed fully along one axis (80 or more) and no more than 6
/// off it reads exactly 1.0 on that axis and 0 on the other.
static void Cardinal(s8 x, s8 y, Vec2* out)
{
    if (x < -79 || x > 79) {
        if (y < -6 || y > 6) {
            return;
        }
        out->x = x < 0 ? -1.0F : 1.0F;
        out->y = 0.0F;
    } else if (y < -79 || y > 79) {
        if (x < -6 || x > 6) {
            return;
        }
        out->x = 0.0F;
        out->y = y < 0 ? -1.0F : 1.0F;
    }
}

static void PadBuffer(Fighter* fp)
{
    PadLibData* p = &HSD_PadLibData;
    PADStatus* raw;
    UcfPort* h;
    u8 drop = 0;

    if (ftCo_IsCpuControlled(fp)) {
        return;
    }
    /* The sample the game just read: the one before the queue's read
       position (UCF takes the queue to hold five). */
    raw = &p->queue[p->qread == 0 ? 4 : p->qread - 1].stat[fp->pad_port & 3];
    h = Port(fp);
    h->at = (h->at + 1) & 3;
    h->xy[h->at][0] = raw->stickX;
    h->xy[h->at][1] = raw->stickY;

    /* Not while Zelda aims Farore's Wind. */
    if (!(fp->kind == Ft_Kind_Zelda &&
          fp->motion_id == ftZd_MS_SpecialHiStart_0))
    {
        Cardinal(raw->stickX, raw->stickY, &fp->input.lstick[0]);
        Cardinal(raw->substickX, raw->substickY, &fp->input.cstick[0]);
    }

    /* Shield drop: count the frames the stick is at the rim below the
       line, starting only if it got there by moving down more than 44 in
       two frames. */
    if (!(fp->input.lstick[0].y > -0.609375F) &&
        AtRim(fp->input.lstick[0].x, fp->input.lstick[0].y))
    {
        if (h->drop != 0) {
            drop = h->drop + 1;
        } else if (fp->active_timer.lstick.y <= 1) {
            int dy = Moved(h, 1);
            if (dy * dy > 1936) {
                drop = 1;
            }
        }
    }
    h->drop = drop;
}

/// `call` hook, Fighter_procInput+0xC4: the first call in the block that
/// reads the pad. Remembers the fighter for #tm_ucf_8000D148, which is not
/// given it.
bool tm_ucf_IsCpuControlled(Fighter* fp)
{
    input_fp = fp;
    return ftCo_IsCpuControlled(fp);
}

/// `call` hook, Fighter_procInput+0x738: the call before UCF's site
/// (+0x750). Between the two the game only clears two timers that UCF
/// neither reads nor writes, so this is the same point.
s32 tm_ucf_8000D148(float a, float b, float c, float d, float e, float f,
                    float g)
{
    s32 r = lb_8000D148(a, b, c, d, e, f, g);
    Fighter* fp = input_fp;

    input_fp = NULL;
    if (fp != NULL && tm_ucf_Active()) {
        PadBuffer(fp);
    }
    return r;
}

/* --- ftCo_Turn_IASA+0x4C: dash back --------------------------------------- */

/// On the second frame of a turn, a stick that is past the dash threshold
/// and moved more than 75 in two frames was flicked: finish the turn now,
/// which lets the function below start the dash.
static void Dashback(Fighter* fp)
{
    HSD_GObj* partner;
    int dx;

    if (fp->is_sub_fighter) {
        return;
    }
    if (fp->cur_anim_frame != 2.0F) {
        return;
    }
    if (fp->facing_dir * fp->input.lstick[0].x <
        p_ftCommonData->dash_smash_stick_threshold)
    {
        return;
    }
    if (fp->active_timer.lstick.x > 1) {
        return;
    }
    dx = Moved(Port(fp), 0);
    if (dx * dx <= 5625) {
        return;
    }
    fp->mv.co.turn.has_turned = true;
    fp->mv.co.turn.just_turned = true;

    /* The Ice Climbers' partner copies inputs a few frames late: give the
       newest one the same direction. */
    partner = Player_GetEntityAtIndex(fp->player_idx, 1);
    if (partner != NULL) {
        Fighter* pfp = GET_FIGHTER(partner);
        pfp->cpu.x444->facing_dir = fp->facing_dir;
        pfp->cpu.x444->lstick.x = fp->facing_dir < 0.0F ? -128 : 127;
    }
}

/// `pointer` hook on the Turn state's entry in ftData_MotionStateList.
/// ftCo_Turn_IASA with #Dashback where UCF puts it, and osdtech's wrapper
/// of the dash (its `call` hook is in the vanilla body).
void tm_ucf_Turn_IASA(Fighter_GObj* gobj)
{
    Fighter* fp;

    if (!tm_ucf_Active()) {
        ftCo_Turn_IASA(gobj);
        return;
    }
    fp = GET_FIGHTER(gobj);

    if (fp->mv.co.turn.just_turned) {
        fp->input.pressed_buttons |= fp->mv.co.turn.x1C;
    }
    if (!fp->mv.co.turn.has_turned) {
        fp->facing_dir = -fp->facing_dir;
        Dashback(fp);
    }

    RETURN_IF(ftCo_SpecialS_CheckInput(gobj));
    RETURN_IF(ftCo_800D68C0(gobj));
    RETURN_IF(ftCo_Attack100_CheckInput(gobj));
    RETURN_IF(ftCo_Catch_CheckInput(gobj));
    RETURN_IF(ftCo_AttackS4_CheckInput(gobj));
    RETURN_IF(ftCo_AttackHi4_CheckInput(gobj));
    RETURN_IF(ftCo_AttackLw4_CheckInput(gobj));
    RETURN_IF(ftCo_AttackS3_CheckInput(gobj));
    RETURN_IF(ftCo_AttackHi3_CheckInput(gobj));
    RETURN_IF(ftCo_AttackLw3_CheckInput(gobj));
    RETURN_IF(ftCo_Attack1_CheckInput(gobj));

    if (!fp->mv.co.turn.has_turned) {
        fp->facing_dir = -fp->facing_dir;
    }

    RETURN_IF(ftCo_80091A4C(gobj));
    RETURN_IF(ftCo_800DE9D8(gobj));
    RETURN_IF(ftCo_Jump_CheckInput(gobj));

    fn_800C9C2C(gobj);
    if (fp->mv.co.turn.just_turned && fp->mv.co.turn.x8) {
        if (fp->input.lstick[0].x * fp->mv.co.turn.facing_after >=
            p_ftCommonData->dash_smash_stick_threshold)
        {
            tm_osdtech_DashEnter(gobj, 0);
        }
    }

    if (fp->input.pressed_buttons & HSD_PAD_A) {
        fp->mv.co.turn.x1C |= HSD_PAD_A;
    }

    if (fp->input.pressed_buttons & HSD_PAD_B) {
        fp->mv.co.turn.x1C |= HSD_PAD_B;
    }

    if (fp->mv.co.turn.just_turned) {
        fp->mv.co.turn.just_turned = false;
    }
}

/* --- ftCo_SquatRv_CheckInput+0x14: dash back out of crouch ---------------- */

/// In place of ftCo_SquatRv_CheckInput at its one call
/// (ftCo_SquatWait_IASA+0xF4). A stick that has only just left the centre
/// sideways and is already at the rim stands the fighter up from a lower
/// position (0.59) than usual, so a flick sideways out of a crouch is not
/// held in the crouch by a stick that dips on the way.
bool tm_ucf_SquatRv_CheckInput(Fighter_GObj* gobj)
{
    Fighter* fp;
    float line;

    if (!tm_ucf_Active()) {
        return ftCo_SquatRv_CheckInput(gobj);
    }
    fp = GET_FIGHTER(gobj);
    line = p_ftCommonData->x94;
    if (fp->active_timer.lstick.x < 1 &&
        AtRim(fp->input.lstick[0].x, fp->input.lstick[0].y))
    {
        line = 0.59F;
    }
    if (fp->input.lstick[0].y > -line) {
        ftCo_SquatRv_Enter(gobj);
        return true;
    }
    return false;
}

/* --- ftCo_80099894+0x10: shield drop, no spot dodge ----------------------- */

/// Whether a stick held down in shield is a shield drop: on a platform, the
/// stick at the rim but above the spot dodge line's usual reach (-0.8), not
/// a spot dodge from the C-stick, and held sideways long enough.
///
/// UCF checks this as the spot dodge is about to start and, if it holds,
/// makes the function that decided on it return false: no spot dodge, and
/// the checks after it (the drop through the platform among them) run.
static bool ShieldDrop(Fighter* fp)
{
    if (!(fp->input.cstick[0].y > p_ftCommonData->x314)) {
        return false;
    }
    if (fp->active_timer.lstick.x < p_ftCommonData->x320) {
        return false;
    }
    if (!(fp->input.lstick[0].y > -0.8F)) {
        return false;
    }
    if (fp->coll_data.floor.index == -1 ||
        !(fp->coll_data.floor.flags & 0x100))
    {
        return false;
    }
    return AtRim(fp->input.lstick[0].y, fp->input.lstick[0].x);
}

/// In place of ftCo_80099794 (spot dodge with a shield button held) at each
/// call.
bool tm_ucf_80099794(Fighter_GObj* gobj)
{
    if (tm_ucf_Active() && ShieldDrop(GET_FIGHTER(gobj))) {
        return false;
    }
    return ftCo_80099794(gobj);
}

/// In place of ftCo_8009980C (spot dodge out of shield) at each call.
bool tm_ucf_8009980C(Fighter_GObj* gobj)
{
    if (tm_ucf_Active() && ShieldDrop(GET_FIGHTER(gobj))) {
        return false;
    }
    return ftCo_8009980C(gobj);
}

/* --- ftCo_8009A080+0x38: shield drop from a held rim position ------------- */

/// In place of ftCo_8009A080 (drop through a platform out of shield) at
/// each call: the stick being far enough down, or having sat at the rim
/// below the line for more than a frame after a fast move down.
bool tm_ucf_8009A080(Fighter_GObj* gobj)
{
    Fighter* fp;

    if (!tm_ucf_Active()) {
        return ftCo_8009A080(gobj);
    }
    fp = GET_FIGHTER(gobj);
    if (fp->input.held_buttons[0] & HSD_PAD_LR &&
        (fp->input.lstick[0].y <= -p_ftCommonData->x464 ||
         Port(fp)->drop > 1) &&
        fp->active_timer.lstick.y < p_ftCommonData->x468 &&
        mpColl_IsOnPlatform(&fp->coll_data))
    {
        ftCo_8009A228(gobj);
        return true;
    }
    return false;
}

/* --- hitlag: SDI (ftCo_Damage_OnEveryHitlag+0x5C), shield SDI
 *     (ftCo_80093240+0x54) ------------------------------------------------- */

/*
 * Both vanilla callbacks move the fighter when the stick is far enough out
 * and has been for fewer frames than a window, then stamp the stick's timer
 * so one push counts once. UCF adds a second way in: the timer has run out,
 * but the raw stick moved more than 62 in two frames from inside the SDI
 * circle.
 *
 * Neither callback can be replaced, and they are only reached through
 * `fp->hitlag_cb`. So for the frames UCF adds, the callback is run with the
 * timer set to 0: the vanilla test passes, the same move is made and the
 * timer is stamped as UCF would leave it. If the callback's other tests
 * refuse (the timer is then still 0), the timer is put back.
 */

static bool Flicked(Fighter* fp, bool both_axes)
{
    UcfPort* h = Port(fp);
    int dx = Moved(h, 0);
    int d = dx * dx;

    if (both_axes) {
        int dy = Moved(h, 1);
        d += dy * dy;
    }
    return d > 3844;
}

static void Sdi(Fighter_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    int window = p_ftCommonData->sdi_stick_window;
    float min = p_ftCommonData->sdi_min_stick_mag;
    float yy = fp->input.lstick[1].y * fp->input.lstick[1].y;
    float was = fp->input.lstick[1].x * fp->input.lstick[1].x + yy;
    u8 saved = fp->active_timer.lstick.x;

    fp->hitlag_cb = ftCo_Damage_OnEveryHitlag;
    if (window > 0 && saved >= window &&
        fp->active_timer.lstick.y >= window &&
        (fp->active_sticky.lstick.x <= 1 ||
         fp->active_sticky.lstick.y <= 1) &&
        !(min * min <= was) && Flicked(fp, true))
    {
        fp->active_timer.lstick.x = 0;
        ftCo_Damage_OnEveryHitlag(gobj);
        if (fp->active_timer.lstick.x == 0) {
            fp->active_timer.lstick.x = saved;
        }
        return;
    }
    ftCo_Damage_OnEveryHitlag(gobj);
}

static void ShieldSdi(Fighter_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    int window = p_ftCommonData->sdi_stick_window;
    u8 saved = fp->active_timer.lstick.x;

    fp->hitlag_cb = ftCo_80093240;
    if (window > 0 && saved >= window && fp->active_sticky.lstick.x <= 1 &&
        !(fp->input.lstick[1].x >= p_ftCommonData->sdi_min_stick_mag) &&
        Flicked(fp, false))
    {
        fp->active_timer.lstick.x = 0;
        ftCo_80093240(gobj);
        if (fp->active_timer.lstick.x == 0) {
            fp->active_timer.lstick.x = saved;
        }
        return;
    }
    ftCo_80093240(gobj);
}

/// From osdtech's wrapper of the call just before `fp->hitlag_cb(gobj)` in
/// Fighter_procUpdate: have that call reach the functions above, which put
/// the vanilla callback back before anything else can see the difference.
void tm_ucf_PreHitlag(Fighter_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);

    if (!tm_ucf_Active()) {
        return;
    }
    if (fp->hitlag_cb == ftCo_Damage_OnEveryHitlag) {
        fp->hitlag_cb = Sdi;
    } else if (fp->hitlag_cb == ftCo_80093240) {
        fp->hitlag_cb = ShieldSdi;
    }
}

/* --- ftCo_DamageFall_IASA+0xCC: wiggle out of tumble ----------------------- */

/// UCF's window for the wiggle: the frame the stick crosses the line, or
/// the next one if on the frame before it was still inside and the raw
/// stick moved more than 75 in two frames.
static bool Wiggled(Fighter* fp)
{
    int dx;

    if (fp->active_timer.lstick.x < 1) {
        return true;
    }
    if (fp->active_timer.lstick.x > 1) {
        return false;
    }
    if (!(fabsf(fp->input.lstick[1].x) < p_ftCommonData->x210)) {
        return false;
    }
    dx = Moved(Port(fp), 0);
    return dx * dx > 5625;
}

/// In place of ftCo_DamageFall_IASA at its three calls and in
/// ftData_MotionStateList. The vanilla function with #Wiggled for its timer
/// test and osdact's wrappers for the calls (their `call` hooks are in the
/// vanilla body).
void tm_ucf_DamageFall_IASA(Fighter_GObj* gobj)
{
    Fighter* fp;

    if (!tm_ucf_Active()) {
        ftCo_DamageFall_IASA(gobj);
        return;
    }
    fp = GET_FIGHTER(gobj);
    if (!ftCo_800C5240(gobj)) {
        RETURN_IF(tm_osdact_DFSpecialAir(gobj));
        RETURN_IF(tm_osdact_DF80095328(gobj, 0));
        RETURN_IF(tm_osdact_DF800D7100(gobj));
        RETURN_IF(tm_osdact_DF800C3B10(gobj));
        RETURN_IF(tm_osdact_DFAttackAir(gobj));
        RETURN_IF(tm_osdact_DF800D705C(gobj));
        RETURN_IF(tm_osdact_DF800CB870(gobj));
        if (ABS(fp->input.lstick[0].x) >= p_ftCommonData->x210 &&
            Wiggled(fp))
        {
            tm_osdact_DFFallEnter(gobj);
            return;
        }
    }
    RETURN_IF(tm_osdact_DF800C5DDC(gobj));
    RETURN_IF(tm_osdact_DF800C5CD4(gobj));
}
