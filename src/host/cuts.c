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
#ifdef HOST_WINDOW
    /* The window build: not into nothing. With no frame of Aurora's begun
       (one that could not be, or a quiet stretch) the graphics commands
       would wait in Aurora's queue for the next frame, and a few frames'
       worth of them overflow it (window.c). */
    if (!host_window_drawable()) {
        return;
    }
#endif
    if (host.draw) {
        HSD_GObj_80390FC0_vanilla();
    }
}
