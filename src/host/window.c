/** @file
 * The window: Aurora (GX on WebGPU, an SDL window) under the game's
 * graphics calls. Only in the window build (`tools/native_build.py
 * --window`, HOST_WINDOW); the headless build has no-op graphics instead.
 *
 * A frame of the game is everything between two frame boundaries
 * (host_frame_tick), so one Aurora frame is opened at each boundary and
 * closed at the next.
 */
#ifdef HOST_WINDOW
#include "host.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include <aurora/aurora.h>
#include <aurora/event.h>
#include <dolphin/gx.h>

static int in_frame;
static int started;

static void on_log(AuroraLogLevel level, const char* module,
                   const char* message, unsigned int len)
{
    static const char* const names[] = { "debug", "info", "warning", "error",
                                         "fatal" };
    (void) len;
    if (level >= LOG_WARNING || host.verbose) {
        fprintf(stderr, "[aurora %s] %s: %s\n", names[level], module,
                message);
    }
    if (level == LOG_FATAL) {
        host_fatal("aurora: %s: %s", module, message);
    }
}

void host_window_init(void)
{
    static char name[] = "melee";
    char* argv[] = { name, NULL };
    AuroraConfig config = {
        .appName = "Melee",
        .logCallback = on_log,
        .windowWidth = 640,
        .windowHeight = 480,
        /* a software renderer will do: tests run on one */
        .allowCpuAdapter = true,
        /* the game's memory is the host layer's own (os.c) */
        .mem1Size = 0,
        .mem2Size = 0,
    };

    /* MELEE_BACKEND=gles|vulkan chooses the graphics API; by default
       Aurora takes the best there is. */
    {
        const char* want = getenv("MELEE_BACKEND");
        if (want != NULL && strcmp(want, "gles") == 0) {
            config.desiredBackend = BACKEND_OPENGLES;
        } else if (want != NULL && strcmp(want, "vulkan") == 0) {
            config.desiredBackend = BACKEND_VULKAN;
        }
    }
    aurora_initialize(1, argv, &config);
    started = 1;
}

/// Which archive an address belongs to and where a blob ends are slow to
/// find (a walk over an archive's objects), and a match asks about the same
/// few hundred addresses every frame: the answers are kept until an archive
/// is opened or closed.
#define MEMO_SIZE 4096
typedef struct Memo {
    const void* key;
    uint32_t arg;
    const void* raw;
    uint32_t size;
} Memo;

static Memo* memo_slot(Memo* table, const void* key, uint32_t arg, int* hit)
{
    static uint32_t generation;
    static Memo* tables[2];
    Memo* m;

    if (generation != host_dat_generation) {
        generation = host_dat_generation;
        for (int i = 0; i < 2; i++) {
            if (tables[i] != NULL) {
                memset(tables[i], 0, MEMO_SIZE * sizeof(Memo));
            }
        }
    }
    if (tables[0] != table && tables[1] != table) {
        tables[tables[0] != NULL] = table;
    }
    m = &table[(((uintptr_t) key >> 2) * 2654435761u) >> 20];
    *hit = m->key == key && m->arg == arg;
    m->key = key;
    m->arg = arg;
    return m;
}

/// The console's GXSetArray(attr, data, stride), for Aurora, which also
/// wants to know how much data there is and its byte order. A model's
/// vertex data is a blob of an archive: big-endian, and as long as the
/// archive's own pointers leave room for (Aurora copies all of it into the
/// frame, so the bound has to be a close one).
void host_GXSetArray3(GXAttr attr, const void* data, u8 stride)
{
    static Memo table[MEMO_SIZE];
    int hit;
    Memo* m = memo_slot(table, data, stride, &hit);

    if (!hit) {
        m->size = host_dat_blob_size(data, stride);
    }
    if (m->size == 0) {
        static int told;
        if (!told++) {
            host_log("GXSetArray: the data of attribute %d is in no open "
                     "archive (first of its kind): not set", (int) attr);
        }
        return;
    }
    GXSetArray(attr, data, m->size, stride, false);
}

/// GXInitTlutObj for a palette that may be a converted archive object:
/// Aurora reads entries as the console stores them, so it gets the file's
/// own bytes.
void host_GXInitTlutObj(GXTlutObj* obj, void* lut, GXTlutFmt fmt,
                        u16 entries)
{
    static Memo table[MEMO_SIZE];
    int hit;
    Memo* m = memo_slot(table, lut, 0, &hit);

    if (!hit) {
        uint32_t room = 0;
        m->raw = host_dat_raw_room(lut, &room);
    }
    GXInitTlutObj(obj, m->raw != NULL ? (void*) m->raw : lut, fmt, entries);
}

static double now_ms(void)
{
    struct timespec t;

    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1000.0 + t.tv_nsec / 1e6;
}

/// MELEE_TIMING=1: every 60 frames, where a frame's time went. "game" is
/// everything between two frame boundaries (the game's own work and its
/// graphics calls, which Aurora only records); "end" is Aurora drawing and
/// presenting the frame; "begin" is events and opening the next frame.
static void timing(double game, double end, double begin)
{
    static int on = -1, n;
    static double sum[3];

    if (on < 0) {
        const char* e = getenv("MELEE_TIMING");
        on = e != NULL && *e != '\0' && *e != '0';
    }
    if (!on) {
        return;
    }
    sum[0] += game;
    sum[1] += end;
    sum[2] += begin;
    if (++n == 60) {
        host_log("timing: a frame takes %.1f ms: game %.1f, end %.1f, "
                 "begin %.1f",
                 (sum[0] + sum[1] + sum[2]) / n, sum[0] / n, sum[1] / n,
                 sum[2] / n);
        n = 0;
        sum[0] = sum[1] = sum[2] = 0;
    }
}

void host_window_frame(void)
{
    static double last;
    const AuroraEvent* event;
    double t0, t1, t2;

    if (!started) {
        return;
    }
    t0 = now_ms();
    if (in_frame) {
        aurora_end_frame();
        in_frame = 0;
    }
    t1 = now_ms();
    for (event = aurora_update();
         event != NULL && event->type != AURORA_NONE; event++)
    {
        if (event->type == AURORA_EXIT) {
            fflush(stdout);
            host_log("the window was closed");
            exit(0);
        }
    }
    in_frame = aurora_begin_frame();
    t2 = now_ms();
    if (last != 0) {
        timing(t0 - last, t1 - t0, t2 - t1);
    }
    last = t2;
}
#endif
