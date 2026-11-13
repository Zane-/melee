/** @file
 * Parts of the game the headless build can leave out, each replacing a
 * vanilla function that tools/native_build.py compiles under another name.
 */
#include "host.h"

/* --- the draw pass ---------------------------------------------------------
 * HSD_GObj_80390FC0 runs every object's draw callback. Graphics calls are
 * no-ops, so it costs little, and with --draw it runs, which exercises code
 * that only executes while drawing. Without it the pass is skipped, as in
 * the Python simulator.
 */
void HSD_GObj_80390FC0_vanilla(void);

void HSD_GObj_80390FC0(void)
{
    if (host.draw) {
        HSD_GObj_80390FC0_vanilla();
    }
}
