/** @file
 * The moves a fighter may use, for a Versus game mode that allows only some
 * (the client's Shine Battle; the owner, 2026-11-14: "shine only (any non
 * shine move disabled, only jumping, shield, air dodge, etc., no other
 * aerials, etc.)").
 *
 * Fighter_procInput calls host_moves_filter right after it reads a
 * fighter's buttons, the pad's for a person and a model, the CPU's for the
 * game's CPU (a patch, tools/native_build.py), so one rule holds for every
 * kind of player. It works on the inputs the game is about to read, not on
 * the actions: what is taken away is the press the game would have turned
 * into a move, as the game itself decides it.
 *
 *  - A and Z never reach the game: no jab, tilt, smash, aerial, grab or
 *    item throw (Z, with A and a light press of the shield it stands for,
 *    is taken before the game adds those).
 *  - The C-stick is still, except in hitlag (where it is the C-stick's
 *    ASDI): no smash attack or aerial from it. Twice: here, and again
 *    after UCF has read the pad (host_moves_sticks, later in
 *    Fighter_procInput: UCF's PadBuffer snaps a stick at the rim to the
 *    cardinal from the raw pad, which would put it back).
 *  - B reaches the game only as a new press with the control stick down,
 *    past the line the game's own down special takes (p_ftCommonData->x21C,
 *    ftCo_800D688C on the ground, ftCo_SpecialAir_CheckInput in the air),
 *    so it is always the down special; held, it stays (the reflector held).
 *    With `HOST_MOVES_RECOVERY` the up and side specials too (the stick
 *    out of the middle the same way), never the neutral one. On the ledge
 *    and lying down a new B is never let through: there it is the ledge
 *    attack and the getup attack (ftCo_CliffWait_IASA, ftCo_DownWait_IASA
 *    check those first).
 *
 * Jumping, shielding, rolls, spot dodges, air dodges, techs, ledge options
 * other than the attack and every movement are left as they are. The rule
 * is the host's, set per slot by the driver ("moves P RULE"), not part of
 * the game's state: a rollback or a game played ahead keeps it.
 */
#include "host.h"

#include <melee/ft/fighter.h>
#include <melee/ft/ftcommon.h>
#include <melee/ft/kinds/ftCommon/forward.h>
#include <melee/ft/types.h>

static int rules[4];

void host_moves_set(int slot, int rule)
{
    if (slot >= 0 && slot < 4) {
        rules[slot] = rule;
    }
}

int host_moves_get(int slot)
{
    return slot >= 0 && slot < 4 ? rules[slot] : HOST_MOVES_ALL;
}

/// Whether the stick, as the game reads it this frame, makes B one of the
/// specials the rule allows.
static bool special_allowed(Fighter* fp, int rule)
{
    float x = fp->input.lstick[0].x;
    float y = fp->input.lstick[0].y;
    float line = p_ftCommonData->x21C;

    if (y < -line) {
        return true;
    }
    if (rule == HOST_MOVES_RECOVERY) {
        return y >= line || (x < 0 ? -x : x) >= p_ftCommonData->x218;
    }
    return false;
}

void host_moves_sticks(Fighter* fp)
{
    if (host_moves_get(fp->player_idx) != HOST_MOVES_ALL &&
        !(fp->dmg.x195c_hitlag_frames > 0.0F))
    {
        fp->input.cstick[0].x = 0.0F;
        fp->input.cstick[0].y = 0.0F;
    }
}

void host_moves_filter(Fighter* fp)
{
    int rule = host_moves_get(fp->player_idx);
    HSD_Pad* held = &fp->input.held_buttons[0];

    if (rule == HOST_MOVES_ALL) {
        return;
    }
    *held &= ~(HSD_PAD_A | HSD_PAD_Z);
    host_moves_sticks(fp);
    if ((*held & HSD_PAD_B) && !(fp->input.held_buttons[1] & HSD_PAD_B)) {
        bool attack = fp->motion_id == ftCo_MS_CliffWait ||
                      fp->motion_id == ftCo_MS_DownWaitU ||
                      fp->motion_id == ftCo_MS_DownWaitD;
        if (attack || !special_allowed(fp, rule)) {
            *held &= ~HSD_PAD_B;
        }
    }
}
