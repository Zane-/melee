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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

/// The console's GXSetArray(attr, data, stride), for Aurora, which also
/// wants to know how much data there is and its byte order. A model's
/// vertex data is a blob of an archive: big-endian, and as long as the
/// archive's own pointers leave room for (Aurora copies all of it into the
/// frame, so the bound has to be a close one).
void host_GXSetArray3(GXAttr attr, const void* data, u8 stride)
{
    uint32_t size = host_dat_blob_size(data, stride);

    if (size == 0) {
        static int told;
        if (!told++) {
            host_log("GXSetArray: the data of attribute %d is in no open "
                     "archive (first of its kind): not set", (int) attr);
        }
        return;
    }
    GXSetArray(attr, data, size, stride, false);
}

void host_window_frame(void)
{
    const AuroraEvent* event;

    if (!started) {
        return;
    }
    if (in_frame) {
        aurora_end_frame();
        in_frame = 0;
    }
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
}
#endif
