/** @file
 * The hardware nobody is listening to: audio RAM, pads, video timing, the
 * few graphics and audio calls whose results the game uses, and the memory
 * card (none inserted). Every other SDK function is a generated stub that
 * returns 0 (see tools/native_build.py).
 */
#include "host.h"

#include <stdlib.h>
#include <string.h>

#include <dolphin/ar.h>
#include <dolphin/card.h>
#include <dolphin/gx.h>
#include <dolphin/mtx.h>
#include <dolphin/pad.h>
#include <dolphin/vi.h>

/* --- audio RAM ---------------------------------------------------------- */

static uint8_t* aram;
static uint32_t aram_next = HOST_ARAM_BASE;

/// Which file each block of audio RAM was filled from: animation files sit
/// here and are fetched back one archive at a time.
#define MAX_ARAM_ORIGINS 1024
static struct {
    uint32_t addr, length;
    int file;
    uint32_t offset;
} aram_origins[MAX_ARAM_ORIGINS];
static int aram_origin_next;

static uint8_t* aram_at(uint32_t addr, uint32_t length)
{
    if (aram == NULL) {
        aram = calloc(1, HOST_ARAM_SIZE);
    }
    if (addr > HOST_ARAM_SIZE || length > HOST_ARAM_SIZE - addr) {
        host_fatal("audio RAM access out of range: %x + %x", addr, length);
    }
    return aram + addr;
}

u32 ARInit(u32* stack_index_addr, u32 num_entries)
{
    (void) stack_index_addr;
    (void) num_entries;
    return HOST_ARAM_BASE;
}

u32 ARGetSize(void)
{
    return HOST_ARAM_SIZE;
}

u32 ARGetBaseAddress(void)
{
    return HOST_ARAM_BASE;
}

u32 ARAlloc(u32 length)
{
    u32 addr = aram_next;
    aram_next += (length + 31) & ~31u;
    return addr;
}

void ARQInit(void) {}

static void arq_done(intptr_t callback, intptr_t request)
{
    ((ARQCallback) callback)((ARQRequest*) request);
}

void ARQPostRequest(ARQRequest* request, u32 owner, u32 type, u32 priority,
                    uintptr_t source, uintptr_t dest, u32 length,
                    ARQCallback callback)
{
    request->next = NULL;
    request->owner = owner;
    request->type = type;
    request->priority = priority;
    request->source = (u32) source;
    request->dest = (u32) dest;
    request->length = length;
    request->callback = callback;
    if (type == ARQ_TYPE_MRAM_TO_ARAM) {
        uint32_t offset;
        int file = host_origin_find((void*) source, &offset);
        memcpy(aram_at((u32) dest, length), (void*) source, length);
        aram_origins[aram_origin_next].addr = (u32) dest;
        aram_origins[aram_origin_next].length = file < 0 ? 0 : length;
        aram_origins[aram_origin_next].file = file;
        aram_origins[aram_origin_next].offset = offset;
        aram_origin_next = (aram_origin_next + 1) % MAX_ARAM_ORIGINS;
    } else {
        memcpy((void*) dest, aram_at((u32) source, length), length);
        for (int n = 1; n <= MAX_ARAM_ORIGINS; n++) {
            int i = (aram_origin_next - n + MAX_ARAM_ORIGINS) %
                    MAX_ARAM_ORIGINS;
            if (aram_origins[i].length != 0 &&
                source >= aram_origins[i].addr &&
                source < aram_origins[i].addr + aram_origins[i].length)
            {
                host_origin_set((void*) dest, length, aram_origins[i].file,
                                aram_origins[i].offset +
                                    (u32) (source - aram_origins[i].addr));
                break;
            }
        }
    }
    if (callback != NULL) {
        host_post(arq_done, (intptr_t) callback, (intptr_t) request);
    }
}

/* --- pads --------------------------------------------------------------- */

BOOL PADInit(void)
{
    return 1;
}

BOOL PADReset(u32 mask)
{
    (void) mask;
    return 1;
}

BOOL PADRecalibrate(u32 mask)
{
    (void) mask;
    return 1;
}

u32 PADRead(PADStatus* status)
{
    u32 mask = 0;
    for (int i = 0; i < 4; i++) {
        const HostPad* p = &host.pads[i];
        memset(&status[i], 0, sizeof status[i]);
        if (p->connected) {
            status[i].button = p->buttons;
            status[i].stickX = p->lx;
            status[i].stickY = p->ly;
            status[i].substickX = p->cx;
            status[i].substickY = p->cy;
            status[i].triggerLeft = p->lt;
            status[i].triggerRight = p->rt;
            status[i].err = PAD_ERR_NONE;
            mask |= 0x80000000u >> i;
        } else {
            status[i].err = PAD_ERR_NO_CONTROLLER;
        }
    }
    return mask;
}

/* --- video timing ------------------------------------------------------- */

static VIRetraceCallback pre_retrace, post_retrace;

VIRetraceCallback VISetPreRetraceCallback(VIRetraceCallback cb)
{
    VIRetraceCallback old = pre_retrace;
    pre_retrace = cb;
    return old;
}

VIRetraceCallback VISetPostRetraceCallback(VIRetraceCallback cb)
{
    VIRetraceCallback old = post_retrace;
    post_retrace = cb;
    return old;
}

u32 VIGetRetraceCount(void)
{
    return host.frame;
}

u32 VIGetNextField(void)
{
    return host.frame & 1;
}

void VIWaitForRetrace(void)
{
    host.frame++;
    host.ticks += HOST_TICKS_PER_FRAME;
}

/* --- graphics: nothing is drawn, but these answers are used ------------
 * (The window build has Aurora's GX instead: window.c.) */
#ifndef HOST_WINDOW

GXRenderModeObj GXNtsc480IntDf = {
    0,   640, 480, 480, 40, 0, 640, 480, 1, 0, 0,
    { { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 },
      { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 } },
    { 8, 8, 10, 12, 10, 8, 8 },
};

GXRenderModeObj GXNtsc480Int = {
    0,   640, 480, 480, 40, 0, 640, 480, 1, 0, 0,
    { { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 },
      { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 } },
    { 0, 0, 21, 22, 21, 0, 0 },
};

GXRenderModeObj GXNtsc480Prog = {
    2,   640, 480, 480, 40, 0, 640, 480, 0, 0, 0,
    { { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 },
      { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 }, { 6, 6 } },
    { 0, 0, 21, 22, 21, 0, 0 },
};

static void tile_shift(u32 format, u32* sx, u32* sy)
{
    switch (format) {
    case GX_TF_I4:
    case GX_TF_C4:
    case GX_TF_CMPR:
    case GX_CTF_R4:
    case GX_CTF_Z4:
        *sx = 3;
        *sy = 3;
        break;
    case GX_TF_I8:
    case GX_TF_IA4:
    case GX_TF_C8:
    case GX_TF_Z8:
    case GX_CTF_RA4:
    case GX_CTF_A8:
    case GX_CTF_R8:
    case GX_CTF_G8:
    case GX_CTF_B8:
    case GX_CTF_Z8M:
    case GX_CTF_Z8L:
        *sx = 3;
        *sy = 2;
        break;
    default:
        *sx = 2;
        *sy = 2;
        break;
    }
}

u32 GXGetTexBufferSize(u16 width, u16 height, u32 format, GXBool mipmap,
                       u8 max_lod)
{
    u32 sx, sy, nx, ny, size, level;
    u32 tile = (format == GX_TF_RGBA8 || format == GX_TF_Z24X8) ? 64 : 32;

    tile_shift(format, &sx, &sy);
    if (mipmap == 1) {
        size = 0;
        for (level = 0; level < max_lod; level++) {
            nx = (width + (1u << sx) - 1) >> sx;
            ny = (height + (1u << sy) - 1) >> sy;
            size += tile * (nx * ny);
            if (width == 1 && height == 1) {
                break;
            }
            width = (width > 1) ? width >> 1 : 1;
            height = (height > 1) ? height >> 1 : 1;
        }
    } else {
        nx = (width + (1u << sx) - 1) >> sx;
        ny = (height + (1u << sy) - 1) >> sy;
        size = nx * ny * tile;
    }
    return size;
}

/// What the game reads back from a texture object.
typedef struct HostTexObj {
    const void* data;
    u16 width, height;
    u32 format;
    u32 tlut;
} HostTexObj;

void GXInitTexObj(GXTexObj* obj, const void* data, u16 width, u16 height,
                  GXTexFmt format, GXTexWrapMode wrap_s, GXTexWrapMode wrap_t,
                  GXBool mipmap)
{
    HostTexObj* t = (HostTexObj*) obj;
    (void) wrap_s;
    (void) wrap_t;
    (void) mipmap;
    memset(obj, 0, sizeof *obj);
    t->data = data;
    t->width = width;
    t->height = height;
    t->format = format;
}

void GXInitTexObjCI(GXTexObj* obj, const void* data, u16 width, u16 height,
                    GXCITexFmt format, GXTexWrapMode wrap_s,
                    GXTexWrapMode wrap_t, GXBool mipmap, u32 tlut)
{
    GXInitTexObj(obj, data, width, height, (GXTexFmt) format, wrap_s, wrap_t,
                 mipmap);
    ((HostTexObj*) obj)->tlut = tlut;
}

GXTexFmt GXGetTexObjFmt(GXTexObj* obj)
{
    return (GXTexFmt) ((HostTexObj*) obj)->format;
}

u16 GXGetTexObjWidth(GXTexObj* obj)
{
    return ((HostTexObj*) obj)->width;
}

u16 GXGetTexObjHeight(GXTexObj* obj)
{
    return ((HostTexObj*) obj)->height;
}

static f32 proj_type;
static f32 proj[6];

void GXSetProjection(const void* mtx_, GXProjectionType type)
{
    const f32(*mtx)[4] = mtx_;
    proj_type = (f32) type;
    proj[0] = mtx[0][0];
    proj[2] = mtx[1][1];
    proj[4] = mtx[2][2];
    proj[5] = mtx[2][3];
    if (type == GX_ORTHOGRAPHIC) {
        proj[1] = mtx[0][3];
        proj[3] = mtx[1][3];
    } else {
        proj[1] = mtx[0][2];
        proj[3] = mtx[1][2];
    }
}

void GXGetProjectionv(f32* p)
{
    p[0] = proj_type;
    memcpy(&p[1], proj, sizeof proj);
}

void GXProject(f32 x, f32 y, f32 z, const f32 mtx[3][4], const f32* pm,
               const f32* vp, f32* sx, f32* sy, f32* sz)
{
    Vec peye;
    f32 xc, yc, zc, wc;

    peye.x =
        mtx[0][3] + ((mtx[0][2] * z) + ((mtx[0][0] * x) + (mtx[0][1] * y)));
    peye.y =
        mtx[1][3] + ((mtx[1][2] * z) + ((mtx[1][0] * x) + (mtx[1][1] * y)));
    peye.z =
        mtx[2][3] + ((mtx[2][2] * z) + ((mtx[2][0] * x) + (mtx[2][1] * y)));
    if (pm[0] == 0.0F) {
        xc = (peye.x * pm[1]) + (peye.z * pm[2]);
        yc = (peye.y * pm[3]) + (peye.z * pm[4]);
        zc = pm[6] + (peye.z * pm[5]);
        wc = 1.0F / -peye.z;
    } else {
        xc = pm[2] + (peye.x * pm[1]);
        yc = pm[4] + (peye.y * pm[3]);
        zc = pm[6] + (peye.z * pm[5]);
        wc = 1.0F;
    }
    *sx = (vp[2] / 2.0F) + (vp[0] + (wc * (xc * vp[2] / 2.0F)));
    *sy = (vp[3] / 2.0F) + (vp[1] + (wc * (-yc * vp[3] / 2.0F)));
    *sz = vp[5] + (wc * (zc * (vp[5] - vp[4])));
}
#endif /* !HOST_WINDOW */

/* --- audio: every voice is one block nobody listens to ------------------ */

static uint8_t voice[0x400];

void* AXAcquireVoice(u32 priority, void* callback, u32 user)
{
    (void) priority;
    (void) callback;
    (void) user;
    return voice;
}

/* --- memory card: none inserted ----------------------------------------- */

s32 CARDProbeEx(s32 chan, s32* mem_size, s32* sector_size)
{
    (void) chan;
    (void) mem_size;
    (void) sector_size;
    return CARD_RESULT_NOCARD;
}

void host_CARDInit(void) {}
