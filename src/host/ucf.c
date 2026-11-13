/** @file
 * UCF in the native build: src/melee/tm/ucf/ucf.c, the overlay's UCF 0.84
 * in C, compiled here too and reached the same way (tools/native_build.py:
 * the calls and table entries the overlay hooks are renamed or patched in
 * the copies of the vanilla files compiled here).
 *
 * Without it the native game reads the stick as the vanilla game does: a
 * dash back done at the speed hands do it often comes out as a slow turn,
 * which is what UCF was made for. Slippi (and so everyone's netplay, and
 * the games slippi-ai learned from) runs UCF 0.84; so does this, unless the
 * driver says `ucf 0` (tools/melee_native/compare.py does: the console's
 * code it compares with is vanilla).
 *
 * The overlay's copies of three functions call display wrappers of the
 * Training Mode port (osdtech, osdact) where the vanilla bodies call the
 * game; there is no such display here, so those names stand for the game's
 * functions themselves.
 */
#include "host.h"

#include <melee/ft/fighter.h>
#include <melee/ft/forward.h>
#include <melee/ft/kinds/ftCommon/ftCo_Dash.h>
#include <melee/ft/kinds/ftCommon/ftCo_Fall.h>
#include <melee/ft/kinds/ftCommon/ftCo_ItemThrow.h>

void ftCo_Dash_Enter(Fighter_GObj* gobj, int arg1);
bool ftCo_SpecialAir_CheckInput(Fighter_GObj* gobj);
bool ftCo_800D7100(Fighter_GObj* gobj);
bool ftCo_800C3B10(Fighter_GObj* gobj);
bool ftCo_AttackAir_CheckItemThrowInput(Fighter_GObj* gobj);
bool ftCo_800D705C(Fighter_GObj* gobj);
bool ftCo_800CB870(Fighter_GObj* gobj);
bool ftCo_800C5DDC(Fighter_GObj* gobj);
bool ftCo_800C5CD4(Fighter_GObj* gobj);

/// UCF's crouch turn ends as the vanilla check does, in this function,
/// which is `static` in ftCo_SquatRv.c (the overlay reaches it by its
/// console address, 0x800D6620). The same one line.
void ftCo_SquatRv_Enter(Fighter_GObj* gobj)
{
    Fighter_ChangeMotionState(gobj, ftCo_MS_SquatRv, Ft_MF_None, 0.0F, 1.0F,
                              0.0F, NULL);
}

void tm_osdtech_DashEnter(Fighter_GObj* gobj, int arg1)
{
    ftCo_Dash_Enter(gobj, arg1);
}

bool tm_osdact_DFSpecialAir(Fighter_GObj* gobj)
{
    return ftCo_SpecialAir_CheckInput(gobj);
}

bool tm_osdact_DF80095328(Fighter_GObj* gobj, bool* arg1)
{
    return ftCo_80095328(gobj, arg1);
}

bool tm_osdact_DF800D7100(Fighter_GObj* gobj)
{
    return ftCo_800D7100(gobj);
}

bool tm_osdact_DF800C3B10(Fighter_GObj* gobj)
{
    return ftCo_800C3B10(gobj);
}

bool tm_osdact_DFAttackAir(Fighter_GObj* gobj)
{
    return ftCo_AttackAir_CheckItemThrowInput(gobj);
}

bool tm_osdact_DF800D705C(Fighter_GObj* gobj)
{
    return ftCo_800D705C(gobj);
}

bool tm_osdact_DF800CB870(Fighter_GObj* gobj)
{
    return ftCo_800CB870(gobj);
}

void tm_osdact_DFFallEnter(Fighter_GObj* gobj)
{
    ftCo_Fall_Enter(gobj);
}

bool tm_osdact_DF800C5DDC(Fighter_GObj* gobj)
{
    return ftCo_800C5DDC(gobj);
}

bool tm_osdact_DF800C5CD4(Fighter_GObj* gobj)
{
    return ftCo_800C5CD4(gobj);
}
