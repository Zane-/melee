/** @file
 * Force-included when compiling the vanilla files upstream's native build
 * leaves out, for the SDK functions Aurora's headers declare differently
 * from the console SDK or not at all. The files themselves are unchanged.
 */
#ifndef HOST_SHIM_H
#define HOST_SHIM_H

#include <dolphin/card.h>
#include <dolphin/gx.h>
#include <dolphin/os.h>
#include <dolphin/pad.h>
#include <dolphin/vi.h>

/* The console's CARDInit takes no arguments. */
void host_CARDInit(void);
#define CARDInit() host_CARDInit()

/* The console's GXSetArray has no size or byte order; files upstream has
   adapted pass Aurora's five arguments. Either way nothing is drawn. */
void host_GXSetArray(GXAttr attr, const void* data, ...);
#define GXSetArray(...) host_GXSetArray(__VA_ARGS__)

void PADSetSamplingRate(u32 msec);
s32 CARDFormatAsync(s32 chan, CARDCallback callback);
void GXWaitDrawDone(void);
void GXInitFogAdjTable(GXFogAdjTable* table, u16 width,
                       const f32 projmtx[4][4]);
#ifndef VIPadFrameBufferWidth
#define VIPadFrameBufferWidth(width) ((u16) (((u16) (width) + 15) & ~15))
#endif

/* For source patches (tools/native_build.py, PATCHES). */
void* host_dat_element(void* native, int n, unsigned console_size);
void* host_script_target(const void* word);

/* Where a square root is stored and read back (source patches): the
   vanilla code names a stack slot outside its own variables. */
static volatile f32 host_scratch_f32;

/* A 16- or 32-bit value in a script word, which is in disc order. */
static inline u16 host_be_u16(const void* word, int index)
{
    const u8* b = (const u8*) word + 2 * index;
    return (u16) (b[0] << 8 | b[1]);
}

static inline s16 host_be_s16(const void* word, int index)
{
    return (s16) host_be_u16(word, index);
}

static inline u32 host_be_u32(const void* word)
{
    const u8* b = word;
    return (u32) b[0] << 24 | (u32) b[1] << 16 | (u32) b[2] << 8 | b[3];
}

#endif
