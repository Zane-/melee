#include "tm.h"

#include "tmce.h"

#include <string.h>
#include <sysdolphin/baselib/objalloc.h>

/**
 * @file
 * The per-fighter block TM-CE expects: vanilla's Fighter (0x23EC) followed by
 * m-ex's 0xC bytes and TM-CE's 0x138 (MexTK FighterData.TM: state frames,
 * shield frames, previous states, input history, ...), zeroed on creation.
 *
 * Ports m-ex's Custom Playerdata Variables/Adjust Size.asm and the two
 * Initialize Extended Playerblock Values files. Their own sites
 * (Fighter_800679B0+0xC, Fighter_Create+0x54) are Slippi Recording
 * injections, so these hooks wrap the neighbouring calls instead.
 *
 * Under Slippi, its Recording code also grows this block. The larger size
 * wins here, but whether Slippi's extra fields overlap FighterData.TM is not
 * checked yet (see docs/ai/tmce-native.md).
 */

/// Wraps the first `HSD_ObjAllocInit` call in Fighter_800679B0 (+0x28),
/// which sets up fighter_alloc_data.
void tm_Hook_FighterAllocInit(HSD_ObjAllocData* data, size_t size, u32 align)
{
    size_t want = tmce_FighterDataSize();
    HSD_ObjAllocInit(data, size > want ? size : want, align);
}

/// Wraps the `HSD_ObjAlloc(&fighter_alloc_data)` calls in Fighter_Create
/// (+0x50) and ftDemo_CreateFighter (+0x4C): zero the whole block, so the
/// m-ex and TM-CE fields start at 0.
void* tm_Hook_FighterAlloc(HSD_ObjAllocData* data)
{
    void* fp = HSD_ObjAlloc(data);
    if (fp != NULL) {
        memset(fp, 0, data->size);
    }
    return fp;
}
