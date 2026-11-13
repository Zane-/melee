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

/* The console's GXSetArray has no size or byte order. */
void host_GXSetArray(GXAttr attr, const void* data, u8 stride);
#define GXSetArray(attr, data, stride) host_GXSetArray(attr, data, stride)

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

#endif
