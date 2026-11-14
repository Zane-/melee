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

/* From the patch tools/aurora32/build.sh applies (this file is compiled
   against Aurora's own headers, as ui.cpp is). */
void aurora_set_present_hold(bool value);

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
/// A quiet stretch (host_window_quiet): unpaced, and the picture held; 1:
/// nothing drawn, 2: frames drawn but not shown.
static int quiet;

/// What each live port's person is holding, whether or not the game is
/// allowed to see it: while a menu is up ("capture") the game gets a pad at
/// rest, so that a press meant for the menu does not also reach whatever
/// the game is showing underneath.
static HostPad seen[4];
static int captured;
/// Buttons of the live ports the game does not see (the client's own: its
/// pause on START, its D-pad shortcuts); `pads` still reports them.
static unsigned masked;
/// Live ports whose person is read (`pads`) while the game takes the
/// driver's pad: a demonstration plays for them and they can still stop it.
static int scripted[4];

void host_window_scripted(int port, int on)
{
    if (port >= 0 && port < 4) {
        scripted[port] = on;
    }
}

/* Input delay, as Slippi plays online: what a live port's person holds
 * reaches the game this many frames after it is read, so that practice
 * keeps the timing of online play (Slippi's default is 2 frames). `seen`
 * is not held back: the client's menus answer at once. A netplay session
 * delays the local pad itself (net.c), so while one runs this adds
 * nothing. */
#define DELAY_MAX 15
static int delay_frames;
static HostPad held_back[4][DELAY_MAX + 1];
static unsigned held_next[4];

int host_window_delay(int frames)
{
    if (frames >= 0) {
        if (frames > DELAY_MAX) {
            frames = DELAY_MAX;
        }
        if (frames != delay_frames) {
            /* what was held back goes: the game keeps what it has */
            for (int port = 0; port < 4; port++) {
                for (int i = 0; i <= DELAY_MAX; i++) {
                    held_back[port][i] = host.pads[port];
                }
            }
        }
        delay_frames = frames;
    }
    return delay_frames;
}

/// The pad to give the game this frame, when it would be #give with no
/// delay.
static HostPad hold_back(int port, const HostPad* give)
{
    unsigned at = held_next[port]++ % (DELAY_MAX + 1);

    held_back[port][at] = *give;
    if (delay_frames == 0 || host_net_active()) {
        return *give;
    }
    return held_back[port][(at + DELAY_MAX + 1 - (unsigned) delay_frames) %
                           (DELAY_MAX + 1)];
}

/* Rumble: the game's motor commands (PADControlMotor, hw.c) reach the
 * controller a live port reads, a GameCube controller on the adapter or
 * another controller through SDL. A port's rumble can be switched off (a
 * setting of the client's), it stops while a menu is up, and a test pulse
 * runs it whatever the game says. */
static int rumble_off[4];
static int rumble_test[4]; ///< frames of test pulse left
static int rumble_on[4];   ///< what the port's controller was last told
static unsigned rumble_frames;

/* Volumes, the player's (the client's Sound settings): music and sound
 * effects, 0 to 100, as the mixer's gains (audio.c). Outside the game's
 * state: both sides of a netplay session play one game whatever each
 * hears. */
static int gain_sound = 256, gain_music = 256;

void host_window_volume(int music, int sound)
{
    music = music < 0 ? 0 : music > 100 ? 100 : music;
    sound = sound < 0 ? 0 : sound > 100 ? 100 : sound;
    gain_music = (music * 256 + 50) / 100;
    gain_sound = (sound * 256 + 50) / 100;
}

int host_window_gain(int kind)
{
    return kind ? gain_music : gain_sound;
}

void host_window_rumble(int port, int on)
{
    rumble_off[port & 3] = !on;
}

void host_window_rumble_test(int port, int frames)
{
    rumble_test[port & 3] = frames;
}

/// Per port: 1 if its rumble is allowed, and whether its controller's
/// motor is running now.
void host_window_rumble_state(int allowed[4], int running[4])
{
    for (int i = 0; i < 4; i++) {
        allowed[i] = !rumble_off[i];
        running[i] = rumble_on[i];
    }
}

static void gamepad_rumble(SDL_Gamepad* g, int port, int want)
{
    /* the controller stops by itself after the duration, so a game that
       ends without stopping it does not leave it running: a running motor
       is told again before then */
    if (want != rumble_on[port] || (want && rumble_frames % 20 == 0)) {
        SDL_RumbleGamepad(g, want ? 0xC000 : 0, want ? 0x8000 : 0,
                          want ? 500 : 0);
    }
}

void host_window_capture(int on)
{
    captured = on;
}

void host_window_mask(unsigned buttons)
{
    masked = buttons;
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

/// Whether what the game draws now has a frame of Aurora's to go into
/// (cuts.c): before the window starts, Aurora takes no frames at all.
int host_window_drawable(void)
{
    return !started || in_frame;
}

static void audio_relead(void);

/// Frames nobody sees (host_quiet): they run as fast as they go and
/// nothing they make is shown: the window keeps the last picture (their
/// sound: audio.c). The first frame drawn after one is whole (the game
/// copies its picture out in the frame that draws it), so it is shown,
/// and the sound device, which has run dry meanwhile, waits for its lead
/// again.
///
/// `on` 2: the same, but the frames are drawn (into pictures nobody sees:
/// the coach's of a run played unseen, frames.c).
void host_window_quiet(int on)
{
    if (on && !quiet) {
        aurora_set_present_hold(true);
    } else if (!on && quiet) {
        quiet = 0;
        aurora_set_present_hold(false);
        if (started && !in_frame) {
            in_frame = aurora_begin_frame(); /* for the frame to come */
        }
        audio_relead();
        return;
    }
    quiet = on;
    if (on == 2 && started && !in_frame) {
        in_frame = aurora_begin_frame(); /* drawn, not shown */
    }
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
    int adapter_motor[4] = { 0, 0, 0, 0 };
    int adapter_used = 0;

    rumble_frames++;
    for (int port = 0; port < 4; port++) {
        SDL_Gamepad* g = NULL;
        int how = live[port];

        if (how == LIVE_OFF) {
            rumble_on[port] = 0;
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
            {
                int want = (host_motor(port) && !rumble_off[port] &&
                            !captured) ||
                           rumble_test[port] > 0;
                if (rumble_test[port] > 0) {
                    rumble_test[port]--;
                }
                if (adapter >= 0) {
                    adapter_motor[adapter] |= want;
                    adapter_used = 1;
                } else if (g != NULL) {
                    gamepad_rumble(g, port, want);
                } else {
                    want = 0; /* the keyboard has no motor */
                }
                rumble_on[port] = want;
            }
            if (scripted[port]) {
                /* the driver's pad stays the game's; the delay sees rest */
                hold_back(port, &rest);
                continue;
            }
            now.buttons &= (uint16_t) ~masked;
            host.pads[port] = hold_back(port, captured ? &rest : &now);
        }
    }
    if (adapter_used) {
        for (int i = 0; i < 4; i++) {
            host_gcc_motor(i, adapter_motor[i]);
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
/// When the next frame is due (pace_wait).
static struct timespec next;

/// The next frame a frame period later than due: netplay's time sync, on
/// the side that is ahead (net.c).
void host_window_delay_frame(void)
{
    if (next.tv_sec == 0) {
        return;
    }
    next.tv_nsec += 16683350;
    if (next.tv_nsec >= 1000000000) {
        next.tv_nsec -= 1000000000;
        next.tv_sec++;
    }
}

static void pace_wait(void)
{
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
    if (last != 0 && paced && !quiet) {
        double d = read_at - last;
        least = d < least ? d : least;
        most = d > most ? d : most;
        bunched += d < 12.0;
        gaps += d > 22.0;
    }
    last = quiet ? 0 : read_at; /* a quiet stretch is not a late reading */
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

/* --- sound ----------------------------------------------------------------
 * The mixer (audio.c) hands over 16-bit stereo at 32 kHz as the game's time
 * passes; SDL resamples it for the device. Off screen (a test, a harness)
 * SDL_AUDIO_DRIVER=dummy keeps it off the desktop's speakers. When the
 * device is behind by more than a fifth of a second (the game runs ahead of
 * it: unpaced, or a frame rate above 59.94), the new sound is dropped. */

static SDL_AudioStream* audio_out;
static int audio_failed, audio_started;

/// Bytes the device is given before it starts playing (64 ms): a frame
/// that comes late then does not leave it empty.
#define AUDIO_LEAD (32000 * 4 * 64 / 1000)

/// After a quiet stretch: if the device has (nearly) run dry, it waits for
/// its lead again, as when it first started, so that the sound that
/// follows does not start on an empty queue.
static void audio_relead(void)
{
    if (audio_out != NULL &&
        SDL_GetAudioStreamQueued(audio_out) < AUDIO_LEAD)
    {
        SDL_PauseAudioStreamDevice(audio_out);
        audio_started = 0;
    }
}

void host_window_audio(const int16_t* frames, int count)
{
    if (audio_out == NULL && !audio_failed) {
        SDL_AudioSpec spec = { SDL_AUDIO_S16, 2, 32000 };
        if (!SDL_InitSubSystem(SDL_INIT_AUDIO) ||
            (audio_out = SDL_OpenAudioDeviceStream(
                 SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK, &spec, NULL, NULL)) ==
                NULL)
        {
            host_log("no sound: %s", SDL_GetError());
            audio_failed = 1;
            return;
        }
    }
    if (audio_out == NULL) {
        return;
    }
    if (SDL_GetAudioStreamQueued(audio_out) > 32000 * 4 / 5) {
        return;
    }
    SDL_PutAudioStreamData(audio_out, frames, count * 4);
    if (!audio_started && SDL_GetAudioStreamQueued(audio_out) >= AUDIO_LEAD) {
        SDL_ResumeAudioStreamDevice(audio_out);
        audio_started = 1;
    }
}

/// The system clipboard's text into `out` ("" if none).
void host_window_clipboard(char* out, size_t size)
{
    char* text = SDL_GetClipboardText();
    snprintf(out, size, "%s", text != NULL ? text : "");
    SDL_free(text);
}

void host_window_set_clipboard(const char* text)
{
    if (!SDL_SetClipboardText(text)) {
        host_log("clipboard: %s", SDL_GetError());
    }
}

/// A frame of real time with nothing new to show (netplay waits for the
/// other side): the window's events, and a little sleep.
void host_window_idle(void)
{
    const AuroraEvent* event;
    if (!started) {
        return;
    }
    for (event = aurora_update(); event != NULL && event->type != AURORA_NONE;
         event++)
    {
        if (event->type == AURORA_EXIT) {
            fflush(stdout);
            host_gcc_motors_off();
            host_log("the window was closed");
            fflush(stderr);
            _exit(0);
        }
    }
    read_live();
    SDL_Delay(2);
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
        if (paced && !quiet) {
            present_wait();
        }
        host_frames_capture(); /* the picture, for the coach (frames.c) */
        aurora_end_frame();
        in_frame = 0;
    }
    presented = shown = now_ms();
    if (paced && !quiet) {
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
            /* Not exit(): its teardown of the graphics libraries (Dawn,
               SDL) never returned from here, and the window hung with
               "not responding" (the owner, 2026-11-13). The process ends
               now; the system frees the window and the GPU's memory. */
            fflush(stdout);
            host_gcc_motors_off();
            host_log("the window was closed");
            fflush(stderr);
            _exit(0);
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
    in_frame = quiet == 1 ? 0 : aurora_begin_frame();
    t2 = now_ms();
    if (last != 0 && !quiet) {
        timing(t0 - last, t1 - t0, t2 - t1, presented - shown_before);
    }
    last = quiet ? 0 : t2;
}
#endif
