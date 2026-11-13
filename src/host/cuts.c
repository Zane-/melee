/** @file
 * Parts of the game the headless build leaves out, each replacing a vanilla
 * function that tools/native_build.py compiles under another name.
 *
 * Everything here is something nobody can see or hear without graphics and
 * sound, and whose data is byte code for a big-endian machine that the
 * generated readers do not convert. A build with graphics has to convert
 * that data instead.
 */
#include "host.h"

/* --- particles -------------------------------------------------------------
 * A particle bank is a block of words, 16-bit fields, floats and byte code,
 * with offsets into itself that psInitDataBankLocate turns into pointers.
 * No bank is ever registered here, so every request for a particle generator
 * finds its bank empty and returns NULL, which callers already handle (the
 * pools can run out on the console too).
 */
void psInitDataBankLocate(int* cmd_bank, int* tex_bank, int* form_bank)
{
    (void) cmd_bank;
    (void) tex_bank;
    (void) form_bank;
}

void psInitDataBankLoad(int bank, const int* cmd_bank, const int* tex_bank,
                        const unsigned* ref, const int* form_bank)
{
    (void) bank;
    (void) cmd_bank;
    (void) tex_bank;
    (void) ref;
    (void) form_bank;
}

void psInitDataBank(int bank, int* cmd_bank, int* tex_bank, unsigned* ref,
                    int* form_bank)
{
    (void) bank;
    (void) cmd_bank;
    (void) tex_bank;
    (void) ref;
    (void) form_bank;
}
