/**
 * @file
 * Port of TM-CE's Misc/Character Randomness/: the Lab's "character
 * randomness" options (TM-CE RNGControl, set from lab.c) override the
 * random choices below. Setting 0 always means vanilla randomness.
 */
#include "misc.h"

#include <melee/ft/fighter.h>
#include <melee/ft/ftcpuattack.h>
#include <melee/ft/inlines.h>
#include <melee/ft/kinds/ftGameWatch/types.h>
#include <melee/ft/kinds/ftPeach/types.h>
#include <melee/ft/types.h>
#include <melee/it/forward.h>
#include <melee/it/kinds/itpeachturnip.h>
#include <sysdolphin/baselib/random.h>

/// Replaces ftGw_SpecialS_GetRandomInt (`function` hook), Mr. Game &
/// Watch's Judge roll.
///
/// Port of GnW Hammer.asm (+0xCC): with a setting of 1-9, the result is
/// that number. The roll still happens, so the random seed advances as in
/// vanilla.
int tm_misc_GwJudgeRoll(HSD_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    ftGameWatchAttributes* sa = getFtSpecialAttrs(fp);
    ftGameWatchJudge gw_judge0;
    ftGameWatchJudge gw_judge1;
    size_t i;
    int rand;
    int result;
    int setting;

    {
        int const judge_max = 9;
        int judge = judge_max;

        for (judge -= judge_max, i = 0, rand = 0; judge < judge_max; judge++) {
            if (judge != fp->u.gw.x222C_judgeVar1 &&
                judge != fp->u.gw.x2230_judgeVar2)
            {
                gw_judge0.rollVar[i] = judge;
                rand += sa->x34_GAMEWATCH_JUDGE_ROLL[judge];
                gw_judge1.rollVar[i] = rand;
                i++;
            }
        }
    }

    rand = HSD_Randi(rand);

    for (i = 0; i < ARRAY_SIZE(gw_judge1.rollVar); i++) {
        /* As vanilla: if never hit, result is whatever was there. */
        if (rand < gw_judge1.rollVar[i]) {
            result = gw_judge0.rollVar[i];
            break;
        }
    }

    setting = tmce_misc_GetRng(TM_MISC_RNG_GNW_HAMMER);
    if (setting != 0) {
        result = setting - 1;
    }

    fp->u.gw.x2230_judgeVar2 = fp->u.gw.x222C_judgeVar1;
    fp->u.gw.x222C_judgeVar1 = result;
    return result;
}

/// Wraps the `HSD_Randi` call in ftLg_SpecialS_SetVars (+0x84), Luigi's
/// side-B misfire roll (0 = misfire).
///
/// Port of Luigi Misfire.asm: setting 1 always misfires, 2 never does.
s32 tm_misc_LuigiMisfireRoll(s32 max_val)
{
    int setting = tmce_misc_GetRng(TM_MISC_RNG_LUIGI_MISFIRE);
    if (setting == 0) {
        return HSD_Randi(max_val);
    }
    return setting == 1 ? 0 : 1;
}

/// Replaces ftPe_AttackS4_Enter (`function` hook), Peach's forward smash.
///
/// Port of Peach FSmash.asm (+0x34): with a setting of 1-3 the item is
/// club / pan / racket. The "last item" is forgotten first so the reroll
/// loop accepts a repeat.
void tm_misc_PeachFSmashEnter(HSD_GObj* gobj)
{
    Fighter* fp = GET_FIGHTER(gobj);
    int setting = tmce_misc_GetRng(TM_MISC_RNG_PEACH_FSMASH);

    fp->allow_interrupt = false;
    fp->cmd_vars[0] = 0;
    {
        FtMotionId msid;
        do {
            int const min = ftPe_MS_AttackS4Club;
            int const max = ftPe_MS_AttackS4Racket;
            if (setting != 0) {
                fp->u.pe.attacks4_motion_id = -1;
                msid = setting - 1 + min;
            } else {
                msid = HSD_Randi(max - min + 1) + min;
            }
        } while (msid == fp->u.pe.attacks4_motion_id);
        fp->u.pe.attacks4_motion_id = msid;
        Fighter_ChangeMotionState(gobj, msid, Ft_MF_None, 0, 1, 0, NULL);
    }
    ftAnim_8006EBA4(gobj);
}

/// Peach item menu values (TM-CE Peach Item.asm / Peach Turnip.asm).
enum TmMiscPeachItem {
    PEACH_ITEM_TURNIP = 1, ///< 1-4: turnip, with face 1-4
    PEACH_ITEM_WINKY = 2,
    PEACH_ITEM_DOT_EYES = 3,
    PEACH_ITEM_STITCH = 4,
    PEACH_ITEM_SATURN = 5,
    PEACH_ITEM_BOBOMB = 6,
    PEACH_ITEM_BEAMSWORD = 7,
};

/// Wraps the `it_802BD4AC` call in spawnVeg (+0xA4), which spawns what
/// Peach pulls.
///
/// Port of Peach Item.asm (+0x8C): the setting picks the item kind.
Item_GObj* tm_misc_PeachPullItem(Item_GObj* gobj, Vec3* pos,
                                 Fighter_Part part, ItemKind kind, f32 dir)
{
    switch (tmce_misc_GetRng(TM_MISC_RNG_PEACH_ITEM)) {
    case 0:
        break;
    case PEACH_ITEM_BEAMSWORD:
        kind = It_Kind_Sword;
        break;
    case PEACH_ITEM_BOBOMB:
        kind = It_Kind_BombHei;
        break;
    case PEACH_ITEM_SATURN:
        kind = It_Kind_Dosei;
        break;
    default:
        kind = It_Kind_Peach_Turnip;
        break;
    }
    return it_802BD4AC(gobj, pos, part, kind, dir);
}

/// Wraps the `HSD_Randi` call in it_802BD32C (+0xC0), the turnip face
/// roll (index into the cumulative odds table).
///
/// Port of Peach Turnip.asm: settings 1-4 give the regular, winky,
/// dot-eyes and stitch-face turnip.
s32 tm_misc_PeachTurnipRoll(s32 max_val)
{
    switch (tmce_misc_GetRng(TM_MISC_RNG_PEACH_ITEM)) {
    case 0:
        return HSD_Randi(max_val);
    case PEACH_ITEM_TURNIP:
        return 0;
    case PEACH_ITEM_WINKY:
        return 52;
    case PEACH_ITEM_DOT_EYES:
        return 56;
    default:
        return 57;
    }
}

/// The fighter whose CPU attack logic (ftCo_800B683C) is running.
static Fighter* tm_misc_cpu_attack_fp;

/// Wraps the `ftCo_800B683C` call in ftCo_800B2790 (its only caller), so
/// the throw roll below knows which fighter it is for.
void tm_misc_CpuAttack(Fighter* fp)
{
    tm_misc_cpu_attack_fp = fp;
    ftCo_800B683C(fp);
    tm_misc_cpu_attack_fp = NULL;
}

/// Wraps the `HSD_Randf` call in ftCo_800B683C (+0x7B4): the CPU picks a
/// throw from a random float, [0,.25) up, [.25,.5) down, [.5,.75)
/// forward, [.75,1) back.
///
/// Port of Nana Throw.asm (+0x7B8), for Nana only: settings 1-4 force
/// forward / back / up / down; 5 is forward or down, 50/50.
f32 tm_misc_CpuThrowRoll(void)
{
    f32 roll = HSD_Randf();
    Fighter* fp = tm_misc_cpu_attack_fp;
    int setting;

    if (fp == NULL || fp->kind != Ft_Kind_Nana) {
        return roll;
    }
    setting = tmce_misc_GetRng(TM_MISC_RNG_NANA_THROW);
    switch (setting) {
    case 0:
        return roll;
    case 1:
        return 0.5F;
    case 2:
        return 0.75F;
    case 3:
        return 0.0F;
    case 4:
        return 0.25F;
    case 5:
        return roll >= 0.5F ? 0.5F : 0.25F;
    default:
        /* TM-CE: the roll is already zeroed here, so this is up throw. */
        return 0.0F;
    }
}
