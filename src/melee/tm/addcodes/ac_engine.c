/**
 * @file
 * TM-CE Additional Codes that change the engine's frame loop
 * (gm_801A4D34, which Slippi patches, so it cannot be replaced whole).
 */
#include "addcodes.h"

#include "../tm_hook.h"

/// src/tmce/addcodes_bridge.c: TM-CE's EventVarsFlag_ForceGameLoop is set.
int tmce_ac_ForceGameLoop(void);

/// `inject` at gm_801A4D34+0x2E8, the `cmpw r26, r27` that closes the
/// per-frame loop `for (i = 0; i < pad_queue_count; i++)` (r26 = i,
/// r27 = pad_queue_count).
///
/// Force Game Loop.asm: while TM-CE's ForceGameLoop flag is set (the Lab
/// sets it), the loop keeps running. TM-CE forces the compare to "less
/// than"; here r27 is raised past r26 before the displaced compare runs.
/// r27 is not used after the loop.
///
/// Why `inject`: the site is a compare, not a call, so no `call` hook can
/// reach r26/r27 (a wrapper must preserve them), and gm_801A4D34 cannot be
/// replaced because Slippi patches inside it (0x801A4DB4, 0x801A4DE4,
/// 0x801A5014, 0x801A5018).
void tm_ac_ForceGameLoop(TmRegs* regs)
{
    if (tmce_ac_ForceGameLoop()) {
        TM_REG(regs, 27) = TM_REG(regs, 26) + 1;
    }
}
