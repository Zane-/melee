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
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include "host.h"
#include <aurora/aurora.h>
#include <aurora/event.h>
#include <aurora/gfx.h>
#include <dolphin/gx.h>
#include <dolphin/pad.h>
#include <SDL3/SDL.h>
#include <sys/stat.h>

static int in_frame;
static int started;
static SDL_Window* sdl_window;
static char state_dir[4096];    ///< Aurora's files, and what is remembered
static int fullscreen_asked;    ///< what was last asked for
static int made_w = 640, made_h = 480; ///< the size the window was made with

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

/* --- fullscreen ------------------------------------------------------------
   The window takes the whole of the screen it is on; the video mode is not
   changed. The interface and the game's picture keep the shape the window
   was made with (host_ui_init), centred: on a screen of another shape the
   rest is black. The choice is remembered beside Aurora's own files. */

static FILE* fullscreen_file(const char* mode)
{
    char path[sizeof state_dir + 16];

    if (state_dir[0] == '\0') {
        return NULL;
    }
    snprintf(path, sizeof path, "%s/fullscreen", state_dir);
    return fopen(path, mode);
}

static int fullscreen_remembered(void)
{
    FILE* f = fullscreen_file("r");
    int on = 0;

    if (f != NULL) {
        on = fgetc(f) == '1';
        fclose(f);
    }
    return on;
}

static int fullscreen_now(void)
{
    return sdl_window != NULL &&
           (SDL_GetWindowFlags(sdl_window) & SDL_WINDOW_FULLSCREEN) != 0;
}

int host_window_fullscreen(int want)
{
    FILE* f;

    if (sdl_window == NULL) {
        return 0;
    }
    if (want == 2) {
        want = !fullscreen_now();
    }
    if (want != 0 && want != 1) {
        return fullscreen_asked;
    }
    if (!SDL_SetWindowFullscreen(sdl_window, want != 0)) {
        host_log("fullscreen: %s", SDL_GetError());
        return fullscreen_asked;
    }
    fullscreen_asked = want;
    if (want) {
        SDL_HideCursor();
    } else {
        SDL_ShowCursor();
    }
    f = fullscreen_file("w");
    if (f != NULL) {
        fputs(want ? "1\n" : "0\n", f);
        fclose(f);
    }
    return fullscreen_asked;
}

const char* host_window_resize(int width, int height)
{
    if (sdl_window == NULL) {
        return "there is no window";
    }
    if (width < 320 || height < 240) {
        return "a window is at least 320 by 240";
    }
    return SDL_SetWindowSize(sdl_window, width, height) ? NULL
                                                        : SDL_GetError();
}

void host_window_describe(char* out, size_t size)
{
    int w = 0, h = 0, fw, fh;

    if (sdl_window != NULL) {
        SDL_GetWindowSizeInPixels(sdl_window, &w, &h);
    }
    /* the largest frame of the made shape that fits (as Aurora works out
       where a picture goes: calculate_present_viewport) */
    fw = w;
    fh = (int) lround((double) w * made_h / made_w);
    if (fh >= h) {
        fh = h;
        fw = (int) lround((double) h * made_w / made_h);
        if (fw > w) {
            fw = w;
        }
    }
    snprintf(out, size,
             "{\"size\": [%d, %d], \"frame\": [%d, %d, %d, %d], "
             "\"fullscreen\": %d, \"asked\": %d}",
             w, h, (w - fw) / 2, (h - fh) / 2, fw, fh, fullscreen_now(),
             fullscreen_asked);
}

void host_window_init(void)
{
    /* MELEE_WINDOW_SIZE=1280x720: the client's window. The game's picture
       keeps its four-by-three shape in it (the viewport policy below). */
    static char name[] = "melee";
    char* argv[] = { name, NULL };
    AuroraInfo info;
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
        const char* given = getenv("MELEE_STATE_DIR");
        ssize_t n = readlink("/proc/self/exe", state, sizeof state - 8);
        char* slash;

        if (given != NULL && *given != '\0' && strlen(given) < sizeof state)
        {
            /* a test's own, so that it and a client someone is playing do
               not share a shader cache (the cache is locked by one) */
            strcpy(state, given);
            mkdir(state, 0755);
            config.userPath = state;
            config.cachePath = state;
        } else if (n > 0) {
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
        made_w = width;
        made_h = height;
    }
    if (config.userPath != NULL) {
        snprintf(state_dir, sizeof state_dir, "%s", config.userPath);
    }
    {
        /* MELEE_FULLSCREEN=1 or 0; not set: as it was last left (F11) */
        const char* f = getenv("MELEE_FULLSCREEN");
        fullscreen_asked = f != NULL && *f != '\0' ? *f != '0'
                                                   : fullscreen_remembered();
        config.startFullscreen = fullscreen_asked != 0;
    }
    info = aurora_initialize(1, argv, &config);
    sdl_window = info.window;
    if (fullscreen_asked) {
        SDL_HideCursor();
    }
    /* the game's picture keeps its shape in a window of another shape */
    AuroraSetViewportPolicy(AURORA_VIEWPORT_FIT);
    host_ui_init(made_w, made_h);
    started = 1;
}

/// Where a blob of an archive ends is slow to find, and a match asks about
/// the same few hundred addresses every frame: the answers are kept, and
/// only the ones about an archive go when that archive is closed. (They
/// once all went whenever any archive was opened or closed, which a
/// fighter's animations do several times a second: every such frame then
/// asked everything again and was late.)
#define MEMO_SIZE 4096
typedef struct Memo {
    const void* key;
    uint32_t arg;
    const void* raw;
    uint32_t size;
} Memo;

static Memo array_memo[MEMO_SIZE], palette_memo[MEMO_SIZE];

static Memo* memo_slot(Memo* table, const void* key, uint32_t arg, int* hit)
{
    Memo* m = &table[(((uintptr_t) key >> 2) * 2654435761u) >> 20];

    *hit = m->key == key && m->arg == arg;
    m->key = key;
    m->arg = arg;
    return m;
}

static int within(const void* p, const void* data, size_t size)
{
    return (const uint8_t*) p >= (const uint8_t*) data &&
           (const uint8_t*) p < (const uint8_t*) data + size;
}

/// An archive's data is going: forget what was kept about it.
void host_window_forget(const void* data, size_t size)
{
    for (int i = 0; i < MEMO_SIZE; i++) {
        if (within(array_memo[i].key, data, size)) {
            memset(&array_memo[i], 0, sizeof(Memo));
        }
        if (within(palette_memo[i].raw, data, size)) {
            memset(&palette_memo[i], 0, sizeof(Memo));
        }
    }
}

/// An archive has been opened: an address that belonged to none before may
/// belong to it now.
void host_window_opened(void)
{
    for (int i = 0; i < MEMO_SIZE; i++) {
        if (array_memo[i].key != NULL && array_memo[i].size == 0) {
            memset(&array_memo[i], 0, sizeof(Memo));
        }
        if (palette_memo[i].key != NULL && palette_memo[i].raw == NULL) {
            memset(&palette_memo[i], 0, sizeof(Memo));
        }
    }
}

/// The console's GXSetArray(attr, data, stride), for Aurora, which also
/// wants to know how much data there is and its byte order. A model's
/// vertex data is a blob of an archive: big-endian, and as long as the
/// archive's own pointers leave room for (Aurora copies all of it into the
/// frame, so the bound has to be a close one).
void host_GXSetArray3(GXAttr attr, const void* data, u8 stride)
{
    int hit;
    Memo* m = memo_slot(array_memo, data, stride, &hit);

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
    int hit;
    Memo* m = memo_slot(palette_memo, lut, 0, &hit);

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
    LIVE_GAMEPAD,     /* + which, as SDL lists them (up to 60) */
    LIVE_ADAPTER = 64 /* + which of the GameCube adapter's ports */
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

/// "off", "auto" (a GameCube controller on the adapter if there is one,
/// else the first controller SDL knows, else the keyboard), "keyboard",
/// "gcc" or "gccN" (the adapter's port N, from 1), "pad" or "padN" (the Nth
/// controller SDL lists, from 0).
const char* host_window_live(int port, const char* source)
{
    if (port < 0 || port > 3) {
        return "no such port";
    }
    if (strcmp(source, "off") == 0) {
        live[port] = LIVE_OFF;
    } else if (strcmp(source, "auto") == 0) {
        live[port] = LIVE_AUTO;
        host_gcc_start();
    } else if (strcmp(source, "keyboard") == 0) {
        live[port] = LIVE_KEYBOARD;
    } else if (strncmp(source, "gcc", 3) == 0) {
        int n = source[3] != '\0' ? atoi(source + 3) : 1;
        if (n < 1 || n > 4) {
            return "the adapter's ports are gcc1 to gcc4";
        }
        live[port] = LIVE_ADAPTER + n - 1;
        host_gcc_start();
    } else if (strncmp(source, "pad", 3) == 0) {
        int n = atoi(source + 3);
        live[port] = LIVE_GAMEPAD + (n < 0 || n > 59 ? 0 : n);
    } else {
        return "a source is off, auto, keyboard, gcc, gccN, pad or padN";
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
        int adapter = -1;

        if (how == LIVE_AUTO) {
            adapter = host_gcc_first();
            if (adapter < 0) {
                g = nth_gamepad(0);
            }
        } else if (how >= LIVE_ADAPTER) {
            adapter = how - LIVE_ADAPTER;
        } else if (how >= LIVE_GAMEPAD) {
            g = nth_gamepad(how - LIVE_GAMEPAD);
        }
        {
            HostPad now = { 0 };
            HostPad rest = { 0 };

            if (adapter >= 0) {
                host_gcc_pad(adapter, &now);
            } else if (g != NULL) {
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

/// What there is to play with, in a line: the adapter's state and the
/// controllers SDL knows.
void host_window_devices(char* out, size_t size)
{
    char adapter[240];
    int count = 0;
    SDL_JoystickID* ids = SDL_GetGamepads(&count);
    size_t used;

    host_gcc_start();
    host_gcc_status(adapter, sizeof adapter);
    snprintf(out, size, "GameCube adapter: %s. Other controllers: %d",
             adapter, ids != NULL ? count : 0);
    for (int i = 0; ids != NULL && i < count; i++) {
        const char* name = SDL_GetGamepadNameForID(ids[i]);
        used = strlen(out);
        snprintf(out + used, size - used, "%s pad%d %s", i ? "," : ":", i,
                 name != NULL ? name : "(unnamed)");
    }
    SDL_free(ids);
}

/// When the frame now being worked on began (the tick pace_wait() last
/// waited for).
static struct timespec frame_began;

/// Hold a finished picture until a fixed time after its frame began, so
/// that pictures are shown at even intervals however long each took to
/// make (the game's work and the driver's vary by milliseconds; shown as
/// soon as done, that variation is stutter). The time is as short as the
/// work allows: it is also how old the input is when it is seen.
/// MELEE_PRESENT_MS sets it (6 by default; 0: as soon as done).
static void present_wait(void)
{
    static long hold = -1;
    struct timespec at = frame_began;

    if (hold < 0) {
        const char* e = getenv("MELEE_PRESENT_MS");
        hold = (long) ((e != NULL && *e != '\0' ? atof(e) : 6.0) * 1e6);
        if (hold < 0 || hold > 16000000) {
            hold = 6000000;
        }
    }
    if (at.tv_sec == 0 || hold == 0) {
        return;
    }
    at.tv_nsec += hold;
    if (at.tv_nsec >= 1000000000) {
        at.tv_nsec -= 1000000000;
        at.tv_sec++;
    }
    clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &at, NULL);
}

/// Wait for the next sixtieth of a second (the console's 59.94 a second).
///
/// A frame that starts late does not make the next ones hurry. Each frame
/// reads the controller once, as it starts; frames run back to back to make
/// up lost time would read it a millisecond apart, and to the game a flick
/// across those readings is a slow one (a dash back that comes out as a
/// turn). So after more than 2 ms the schedule starts again from now: the
/// game falls behind the clock by that much, and readings are never closer
/// than about 14.7 ms. (It once caught up on up to 100 ms.) Less than 2 ms
/// is the ordinary lateness of waking up, made up on the next frame.
static void pace_wait(void)
{
    static struct timespec next;
    struct timespec now;
    long long late;

    clock_gettime(CLOCK_MONOTONIC, &now);
    late = (now.tv_sec - next.tv_sec) * 1000000000LL +
           (now.tv_nsec - next.tv_nsec);
    if (next.tv_sec == 0 || late > 2000000LL) {
        next = now;
    } else if (late < 0) {
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
    }
    frame_began = next;
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
/// MELEE_TIMING: how evenly the controller was read (the time between two
/// frames' readings), and the adapter's side of it.
static void input_timing(double read_at, int reset)
{
    static double last, least = 1e9, most, age_most;
    static int bunched, gaps, fallbacks;
    static unsigned long reports0, errors0, opened0;
    unsigned long reports, errors, opened;
    double age;

    if (reset) {
        host_gcc_counts(&reports, &errors, &opened, &age);
        if (live[0] != LIVE_OFF || live[1] != LIVE_OFF) {
            host_log("timing: input read every %.1f to %.1f ms, %d closer "
                     "than 12 ms, %d further than 22 ms; adapter: %lu "
                     "reports, %lu failed reads, opened %lu times, newest "
                     "report at most %.1f ms old when read; %d frames the "
                     "auto port found no adapter controller",
                     least, most, bunched, gaps, reports - reports0,
                     errors - errors0, opened - opened0, age_most,
                     fallbacks);
        }
        reports0 = reports;
        errors0 = errors;
        opened0 = opened;
        least = 1e9;
        most = age_most = 0;
        bunched = gaps = fallbacks = 0;
        return;
    }
    if (last != 0 && paced) {
        double d = read_at - last;
        least = d < least ? d : least;
        most = d > most ? d : most;
        bunched += d < 12.0;
        gaps += d > 22.0;
    }
    last = read_at;
    host_gcc_counts(&reports, &errors, &opened, &age);
    if (age > age_most) {
        age_most = age;
    }
    for (int port = 0; port < 4; port++) {
        if (live[port] == LIVE_AUTO && host_gcc_first() < 0 &&
            opened > 0)
        {
            fallbacks++;
            break;
        }
    }
}

static void timing(double game, double end, double begin, double shown)
{
    static int on = -1, n, late, empty;
    static double sum[3], driver, driver_max, worst, draws, uploads, top[2];
    static unsigned pipelines;

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
    if (game - host_driver_ms > top[0]) {
        top[0] = game - host_driver_ms;
    }
    if (begin > top[1]) {
        top[1] = begin;
    }
    driver += host_driver_ms;
    if (host_driver_ms > driver_max) {
        driver_max = host_driver_ms;
    }
    if (shown > worst) {
        worst = shown;
    }
    if (shown > 20.0) {
        late++;
    }
    {
        /* what the game asked to be drawn this frame */
        const AuroraStats* stats = aurora_get_stats();
        draws += stats->drawCallCount;
        if (stats->drawCallCount == 0) {
            empty++;
        }
        uploads += stats->lastTextureUploadSize;
        pipelines += stats->createdPipelines;
    }
    if (++n == 60) {
        /* "driver" is part of "game": the wait for whoever steps the game
           over the control pipe. "shown" is the time from one picture
           being presented to the next. */
        host_log("timing: slowest game %.1f ms, slowest begin %.1f ms",
                 top[0], top[1]);
        top[0] = top[1] = 0;
        host_log("timing: a frame takes %.1f ms: game %.1f (driver %.1f, "
                 "at most %.1f), end %.1f, begin %.1f; shown every %.1f ms "
                 "at worst, %d of 60 late; %.0f draws a frame, %d frames "
                 "with none, %.0f KB of textures sent a frame, %u pipelines "
                 "made",
                 (sum[0] + sum[1] + sum[2]) / n, sum[0] / n, driver / n,
                 driver_max, sum[1] / n, sum[2] / n, worst, late,
                 draws / n, empty, uploads / n / 1024.0, pipelines);
        input_timing(0, 1);
        n = late = empty = 0;
        draws = uploads = 0;
        pipelines = 0;
        sum[0] = sum[1] = sum[2] = driver = driver_max = worst = 0;
    }
}

void host_window_frame(void)
{
    static double last, shown;
    const AuroraEvent* event;
    double t0, t1, t2, presented, shown_before = shown;

    if (!started) {
        return;
    }
    t0 = now_ms();
    if (in_frame) {
        if (paced) {
            present_wait();
        }
        aurora_end_frame();
        in_frame = 0;
    }
    presented = shown = now_ms();
    if (paced) {
        pace_wait();
    }
    t1 = now_ms();
    /* the controller is read now, as the frame starts; the window's events
       can take a while (the keyboard and SDL's controllers need them, and
       are read after them) */
    host_gcc_take();
    {
        static int timing_on = -1;
        if (timing_on < 0) {
            const char* e = getenv("MELEE_TIMING");
            timing_on = e != NULL && *e != '\0' && *e != '0';
        }
        if (timing_on) {
            input_timing(t1, 0);
        }
    }
    for (event = aurora_update(); event != NULL && event->type != AURORA_NONE;
         event++)
    {
        if (event->type == AURORA_EXIT) {
            fflush(stdout);
            host_log("the window was closed");
            exit(0);
        }
        if (event->type == AURORA_SDL_EVENT &&
            event->sdl.type == SDL_EVENT_KEY_DOWN &&
            event->sdl.key.scancode == SDL_SCANCODE_F11 &&
            !event->sdl.key.repeat)
        {
            host_window_fullscreen(2);
        }
    }
    read_live();
    host_ui_frame();
    in_frame = aurora_begin_frame();
    t2 = now_ms();
    if (last != 0) {
        timing(t0 - last, t1 - t0, t2 - t1, presented - shown_before);
    }
    last = t2;
}
#endif
