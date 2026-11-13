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
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include "host.h"
#include <aurora/aurora.h>
#include <aurora/event.h>
#include <dolphin/gx.h>
#include <dolphin/pad.h>
#include <SDL3/SDL.h>
#include <sys/stat.h>

static int in_frame;
static int started;

static void on_log(AuroraLogLevel level, const char* module,
                   const char* message, unsigned int len)
{
    static const char* const names[] = { "debug", "info", "warning", "error",
                                         "fatal" };
    (void) len;
    /* while starting, also what Aurora says it chose (the graphics
       backend and the adapter) */
    if (level >= LOG_WARNING || host.verbose ||
        (!started && level == LOG_INFO))
    {
        fprintf(stderr, "[aurora %s] %s: %s\n", names[level], module, message);
    }
    if (level == LOG_FATAL) {
        host_fatal("aurora: %s: %s", module, message);
    }
}

void host_window_init(void)
{
    /* MELEE_WINDOW_SIZE=1280x720: the client's window. The game's picture
       keeps its four-by-three shape in it (the viewport policy below). */
    static char name[] = "melee";
    char* argv[] = { name, NULL };
    int width = 640, height = 480;
    const char* wanted = getenv("MELEE_WINDOW_SIZE");
    AuroraConfig config = {
        .appName = "Melee",
        .logCallback = on_log,
        .windowWidth = 640,
        .windowHeight = 480,
        /* a software renderer will do: tests run on one */
        .allowCpuAdapter = true,
        /* input reaches the game whether or not its window has the focus
           (a trainer window beside it must not freeze the player) */
        .allowJoystickBackgroundEvents = true,
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
    {
        /* Aurora's own files (settings, its shader cache) go beside the
           executable, not into the home directory. */
        static char state[4096];
        ssize_t n = readlink("/proc/self/exe", state, sizeof state - 8);
        char* slash;

        if (n > 0) {
            state[n] = '\0';
            slash = strrchr(state, '/');
            if (slash != NULL) {
                strcpy(slash, "/state");
                mkdir(state, 0755);
                config.userPath = state;
                config.cachePath = state;
            }
        }
    }
    {
        /* MELEE_VSYNC=1: present with the display's refresh. Off by
           default: the game is paced by its own clock (host_window_pace)
           and shown as soon as it is drawn. */
        const char* v = getenv("MELEE_VSYNC");
        config.vsync = v != NULL && *v != '\0' && *v != '0';
    }
    if (wanted != NULL && sscanf(wanted, "%dx%d", &width, &height) == 2 &&
        width >= 320 && height >= 240)
    {
        config.windowWidth = (uint32_t) width;
        config.windowHeight = (uint32_t) height;
    }
    aurora_initialize(1, argv, &config);
    /* the game's picture keeps its shape in a window of another shape */
    AuroraSetViewportPolicy(AURORA_VIEWPORT_FIT);
    host_ui_init();
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
                     "archive (first of its kind): not set",
                     (int) attr);
        }
        return;
    }
    GXSetArray(attr, data, m->size, stride, false);
}

/// GXInitTlutObj for a palette that may be a converted archive object:
/// Aurora reads entries as the console stores them, so it gets the file's
/// own bytes.
void host_GXInitTlutObj(GXTlutObj* obj, void* lut, GXTlutFmt fmt, u16 entries)
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

/* --- a person at the controls ---------------------------------------------
 *
 * A port can be "live": its pad is read from a controller or the keyboard
 * at each frame boundary, into the same host.pads[] a script writes to, so
 * the game and whoever drives it over the control pipe see one kind of
 * input. Aurora has a controller layer of its own (PADRead and bindings);
 * it is not used, because it would replace the host's PADRead that scripted
 * runs depend on.
 */

enum {
    LIVE_OFF,
    LIVE_AUTO,
    LIVE_KEYBOARD,
    LIVE_GAMEPAD /* + which */
};

static int live[4];
static int paced;

/// What each live port's person is holding, whether or not the game is
/// allowed to see it: while a menu is up ("capture") the game gets a pad at
/// rest, so that a press meant for the menu does not also reach whatever
/// the game is showing underneath.
static HostPad seen[4];
static int captured;

void host_window_capture(int on)
{
    captured = on;
}

const HostPad* host_window_seen(int port)
{
    return &seen[port & 3];
}

/// "off", "auto" (the first controller, or the keyboard if there is none),
/// "keyboard", "pad" or "padN" (the Nth controller, from 0).
const char* host_window_live(int port, const char* source)
{
    if (port < 0 || port > 3) {
        return "no such port";
    }
    if (strcmp(source, "off") == 0) {
        live[port] = LIVE_OFF;
    } else if (strcmp(source, "auto") == 0) {
        live[port] = LIVE_AUTO;
    } else if (strcmp(source, "keyboard") == 0) {
        live[port] = LIVE_KEYBOARD;
    } else if (strncmp(source, "pad", 3) == 0) {
        live[port] = LIVE_GAMEPAD + atoi(source + 3);
    } else {
        return "a source is off, auto, keyboard, pad or padN";
    }
    host.pads[port].connected = 1;
    return NULL;
}

void host_window_pace(int on)
{
    paced = on;
}

static SDL_Gamepad* nth_gamepad(int n)
{
    int count = 0;
    SDL_JoystickID* ids = SDL_GetGamepads(&count);
    SDL_Gamepad* pad = NULL;

    if (ids != NULL && n >= 0 && n < count) {
        pad = SDL_GetGamepadFromID(ids[n]);
        if (pad == NULL) {
            pad = SDL_OpenGamepad(ids[n]);
        }
    }
    SDL_free(ids);
    return pad;
}

static int8_t stick(int value, int full)
{
    int v = value * full / 32767;
    return (int8_t) (v > 127 ? 127 : v < -127 ? -127 : v);
}

/// SDL names buttons by where they are. A GameCube controller's A is the
/// one at the bottom, B to its left, X to its right and Y above, and SDL's
/// own mapping of the GameCube adapter follows that; other controllers get
/// the same places. SDL has already rescaled a GameCube controller's sticks
/// (it takes 88 steps from the centre as a full push), so the numbers the
/// game gets are close to the controller's own, not equal to them.
static void read_gamepad(SDL_Gamepad* g, HostPad* p)
{
    static const struct {
        SDL_GamepadButton from;
        uint16_t to;
    } buttons[] = {
        { SDL_GAMEPAD_BUTTON_SOUTH, PAD_BUTTON_A },
        { SDL_GAMEPAD_BUTTON_WEST, PAD_BUTTON_B },
        { SDL_GAMEPAD_BUTTON_EAST, PAD_BUTTON_X },
        { SDL_GAMEPAD_BUTTON_NORTH, PAD_BUTTON_Y },
        { SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER, PAD_TRIGGER_Z },
        { SDL_GAMEPAD_BUTTON_LEFT_SHOULDER, PAD_TRIGGER_Z },
        { SDL_GAMEPAD_BUTTON_START, PAD_BUTTON_START },
        { SDL_GAMEPAD_BUTTON_DPAD_UP, PAD_BUTTON_UP },
        { SDL_GAMEPAD_BUTTON_DPAD_DOWN, PAD_BUTTON_DOWN },
        { SDL_GAMEPAD_BUTTON_DPAD_LEFT, PAD_BUTTON_LEFT },
        { SDL_GAMEPAD_BUTTON_DPAD_RIGHT, PAD_BUTTON_RIGHT },
    };
    int gamecube = SDL_GetGamepadType(g) == SDL_GAMEPAD_TYPE_GAMECUBE;
    int full = gamecube ? 88 : 100;
    int lt = SDL_GetGamepadAxis(g, SDL_GAMEPAD_AXIS_LEFT_TRIGGER);
    int rt = SDL_GetGamepadAxis(g, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER);

    p->buttons = 0;
    for (size_t i = 0; i < sizeof buttons / sizeof buttons[0]; i++) {
        if (SDL_GetGamepadButton(g, buttons[i].from)) {
            p->buttons |= buttons[i].to;
        }
    }
    p->lx = stick(SDL_GetGamepadAxis(g, SDL_GAMEPAD_AXIS_LEFTX), full);
    p->ly = stick(-SDL_GetGamepadAxis(g, SDL_GAMEPAD_AXIS_LEFTY), full);
    p->cx = stick(SDL_GetGamepadAxis(g, SDL_GAMEPAD_AXIS_RIGHTX), full);
    p->cy = stick(-SDL_GetGamepadAxis(g, SDL_GAMEPAD_AXIS_RIGHTY), full);
    if (gamecube) {
        /* the trigger's travel and, separately, the click at its end */
        p->lt = (uint8_t) (lt > 0 ? 40 + lt * 176 / 32767 : 0);
        p->rt = (uint8_t) (rt > 0 ? 40 + rt * 176 / 32767 : 0);
        if (SDL_GetGamepadButton(g, SDL_GAMEPAD_BUTTON_MISC3)) {
            p->buttons |= PAD_TRIGGER_L;
        }
        if (SDL_GetGamepadButton(g, SDL_GAMEPAD_BUTTON_MISC4)) {
            p->buttons |= PAD_TRIGGER_R;
        }
    } else {
        /* no click: the last tenth of the travel stands for it */
        p->lt = (uint8_t) (lt * 255 / 32767);
        p->rt = (uint8_t) (rt * 255 / 32767);
        if (lt > 29500) {
            p->buttons |= PAD_TRIGGER_L;
        }
        if (rt > 29500) {
            p->buttons |= PAD_TRIGGER_R;
        }
    }
}

/// The keyboard as a controller. Arrows: the stick (with left shift, a
/// light push). I J K L: the C stick. X: A. Z: B. C and V: Y and X.
/// A and S: L and R. D: Z. Return: Start. T F G H: the D-pad.
static void read_keyboard(HostPad* p)
{
    static const struct {
        SDL_Scancode from;
        uint16_t to;
    } keys[] = {
        { SDL_SCANCODE_X, PAD_BUTTON_A },
        { SDL_SCANCODE_Z, PAD_BUTTON_B },
        { SDL_SCANCODE_C, PAD_BUTTON_Y },
        { SDL_SCANCODE_V, PAD_BUTTON_X },
        { SDL_SCANCODE_A, PAD_TRIGGER_L },
        { SDL_SCANCODE_S, PAD_TRIGGER_R },
        { SDL_SCANCODE_D, PAD_TRIGGER_Z },
        { SDL_SCANCODE_RETURN, PAD_BUTTON_START },
        { SDL_SCANCODE_T, PAD_BUTTON_UP },
        { SDL_SCANCODE_G, PAD_BUTTON_DOWN },
        { SDL_SCANCODE_F, PAD_BUTTON_LEFT },
        { SDL_SCANCODE_H, PAD_BUTTON_RIGHT },
    };
    int count = 0;
    const bool* k = SDL_GetKeyboardState(&count);
    int push = k[SDL_SCANCODE_LSHIFT] ? 40 : 100;

    p->buttons = 0;
    for (size_t i = 0; i < sizeof keys / sizeof keys[0]; i++) {
        if (k[keys[i].from]) {
            p->buttons |= keys[i].to;
        }
    }
    p->lx = (int8_t) ((k[SDL_SCANCODE_RIGHT] - k[SDL_SCANCODE_LEFT]) * push);
    p->ly = (int8_t) ((k[SDL_SCANCODE_UP] - k[SDL_SCANCODE_DOWN]) * push);
    p->cx = (int8_t) ((k[SDL_SCANCODE_L] - k[SDL_SCANCODE_J]) * 100);
    p->cy = (int8_t) ((k[SDL_SCANCODE_I] - k[SDL_SCANCODE_K]) * 100);
    p->lt = (p->buttons & PAD_TRIGGER_L) ? 255 : 0;
    p->rt = (p->buttons & PAD_TRIGGER_R) ? 255 : 0;
}

static void read_live(void)
{
    for (int port = 0; port < 4; port++) {
        SDL_Gamepad* g = NULL;
        int how = live[port];

        if (how == LIVE_OFF) {
            continue;
        }
        if (how == LIVE_AUTO) {
            g = nth_gamepad(0);
        } else if (how >= LIVE_GAMEPAD) {
            g = nth_gamepad(how - LIVE_GAMEPAD);
        }
        {
            HostPad now = { 0 };
            HostPad rest = { 0 };

            if (g != NULL) {
                read_gamepad(g, &now);
            } else if (how == LIVE_AUTO || how == LIVE_KEYBOARD) {
                read_keyboard(&now);
            } /* else its controller is not there: neutral */
            now.connected = 1;
            rest.connected = 1;
            seen[port] = now;
            host.pads[port] = captured ? rest : now;
        }
    }
}

/// Wait for the next sixtieth of a second (the console's 59.94 a second).
/// Returns at once after a long stop, without trying to catch up.
static void pace_wait(void)
{
    static struct timespec next;
    struct timespec now;
    long long late;

    clock_gettime(CLOCK_MONOTONIC, &now);
    late = (now.tv_sec - next.tv_sec) * 1000000000LL +
           (now.tv_nsec - next.tv_nsec);
    if (next.tv_sec == 0 || late > 100000000LL) {
        next = now;
    } else if (late < 0) {
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
    }
    next.tv_nsec += 16683350;
    if (next.tv_nsec >= 1000000000) {
        next.tv_nsec -= 1000000000;
        next.tv_sec++;
    }
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
/// presenting the frame, and the wait for the next sixtieth of a second
/// when paced; "begin" is events, input and opening the next frame.
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
    if (paced) {
        pace_wait();
    }
    t1 = now_ms();
    for (event = aurora_update(); event != NULL && event->type != AURORA_NONE;
         event++)
    {
        if (event->type == AURORA_EXIT) {
            fflush(stdout);
            host_log("the window was closed");
            exit(0);
        }
    }
    read_live();
    host_ui_frame();
    in_frame = aurora_begin_frame();
    t2 = now_ms();
    if (last != 0) {
        timing(t0 - last, t1 - t0, t2 - t1);
    }
    last = t2;
}
#endif
