/**
 * @file
 * Smaller TM-CE Additional Codes: Initialize Stage Data, On Crash/Clear
 * Bootup OSReports, Disable FoD Reflection.
 */
#include "addcodes.h"

#include <string.h>
#include <melee/db/db.h>
#include <melee/ft/ftdrawcommon.h>
#include <melee/ft/ftlib.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjplink.h>
#include <sysdolphin/baselib/memory.h>

/// sysdolphin/baselib/hsd_393C.c: the on-screen OSReport console state
/// (static, unique name). Word 3 (+0xC) is its write position.
extern u32 hsd_804CF7E8[];

/// Wraps `HSD_MemAlloc(516)` in Ground_GetStageGObj (+0x5C).
///
/// Initialize Stage Data.asm (+0x7C, a Slippi Recording site whose code is
/// the same): the stage GObj's 516-byte data block starts zeroed. TM-CE
/// also "zeroed" the OSReport return value when the allocation failed; here
/// a NULL block is left alone.
void* tm_ac_StageDataAlloc(u32 size)
{
    void* data = HSD_MemAlloc(size);
    if (data != NULL) {
        memset(data, 0, size);
    }
    return data;
}

/// On Crash/Clear Bootup OSReports.asm (main+0x2A0): forget the OSReports
/// printed during boot, so the crash screen only shows the crash. Runs at
/// the next call on either path (db_DisableItemSpawns / db_EnableItemSpawns,
/// main+0x2B4 / +0x2BC); nothing in between reads the console.
void tm_ac_BootDisableItemSpawns(void)
{
    hsd_804CF7E8[3] = 0;
    db_DisableItemSpawns();
}

void tm_ac_BootEnableItemSpawns(void)
{
    hsd_804CF7E8[3] = 0;
    db_EnableItemSpawns();
}

/// Replaces ftDrawCommon_80081140 (`function` hook), which turns on every
/// fighter's reflection render callback (Fountain of Dreams).
///
/// Disable FoD Reflection.asm (+0xC): with four or more fighters, no
/// reflection is drawn.
void tm_ac_FighterReflections(void)
{
    HSD_GObj* gobj = HSD_GObjPLinkHead[HSD_GOBJ_PLINK_FIGHTER];
    void* cb = ftLib_CountFighters() >= 4 ? NULL : (void*) ftDrawCommon_80080C28;
    while (gobj != NULL) {
        gobj->render_cb = cb;
        gobj = gobj->next;
    }
}
