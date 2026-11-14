/** @file
 * The host platform layer of the native (Linux) build.
 *
 * The game's own code is compiled unchanged for the host; this directory
 * stands in for the console underneath it, at the level of the SDK's
 * functions: memory, time, interrupts, the disc, audio RAM, pads, video
 * timing, and graphics and audio as no-ops. It is the C counterpart of
 * `tools/melee_sim/hle.py` and draws the same boundary.
 *
 * Nothing here is part of the GameCube build or the overlay.
 */
#ifndef HOST_H
#define HOST_H

#include <stddef.h>
#include <stdint.h>

/// Bus clock ticks per video frame, as the Python simulator counts them.
#define HOST_TICKS_PER_FRAME 675000

/// The console's arena, at the console's addresses.
#define HOST_ARENA_LO 0x804F0C00u
#define HOST_ARENA_HI 0x817F8AC0u
#define HOST_ARAM_SIZE 0x1000000u
#define HOST_ARAM_BASE 0x4000u

typedef struct HostPad {
    uint16_t buttons;
    int8_t lx, ly, cx, cy;
    uint8_t lt, rt;
    int connected;
} HostPad;

typedef struct HostState {
    const char* disc_root; ///< directory holding the disc's `files/`
    int verbose;           ///< print the game's own reports
    int draw;              ///< run the draw pass (into no-op graphics)
    uint32_t frame;        ///< video frames since boot
    int64_t ticks;         ///< emulated time
    int int_enabled;       ///< emulated interrupt enable
    int delivering;        ///< inside a completion callback
    HostPad pads[4];
    uint32_t max_frames; ///< stop after this many (0: never)
    /// Called once per frame, before the pads are sampled.
    void (*on_frame)(void);
} HostState;

extern HostState host;

/// A line on stderr from the host layer itself.
void host_log(const char* fmt, ...);
/// The same, then a backtrace and exit(2).
_Noreturn void host_fatal(const char* fmt, ...);
void host_backtrace(void);

/// Queue a completion callback, delivered like an interrupt: the next time
/// the game enables interrupts, idles, or ends a frame.
void host_post(void (*func)(intptr_t, intptr_t), intptr_t a, intptr_t b);
/// Deliver everything queued, if interrupts are enabled.
void host_deliver(void);
/// Move emulated time forward, queuing alarms that came due.
void host_advance(int64_t ticks);

void host_memory_init(void);
void host_disc_init(const char* root);
/// The file a buffer was read from, or NULL: `offset` is where in it.
const char* host_disc_origin(const void* addr, uint32_t* offset);
/// The same as a file index (-1: unknown), and recording one, for buffers
/// that travel through audio RAM.
int host_origin_find(const void* addr, uint32_t* offset);
void host_origin_set(void* addr, uint32_t length, int file, uint32_t offset);
/// How many bytes of the buffer that holds `addr` follow it (0: unknown).
uint32_t host_origin_room(const void* addr);

/// The match the next host_match_start() sets up.
typedef struct HostMatch {
    int ckind[4]; ///< CharacterKind, or -1 for an empty slot
    int human[4]; ///< a human (reads its pad) or a CPU
    int stage;    ///< stage id as in the match rules (0x20: FD)
    unsigned seed; ///< the game's random seed as the match is set up
    int stocks;    ///< stocks each; 0: an endless time match (the default)
    /// Matches entered so far (`state`'s "match").
    unsigned entered;
    /// Matches the game ended itself (L+R+A+Start in its pause, the end of
    /// a stock match), as opposed to a driver asking for another. Each is
    /// followed at once by the same match again, never by the game's own
    /// boot scenes (`state`'s "ended").
    unsigned ended;
} HostMatch;

extern HostMatch host_match;
/// Whether a fighter's object still exists (the player table keeps it after
/// its match has ended).
int host_live_fighter(const void* gobj);
/// Each frame: keeps the host's mode override installed.
void host_match_install(void);
/// End the current scene and enter the match described by host_match.
void host_match_start(void);

/// Put player `slot`'s fighter standing on the floor at or below (x, y), or
/// (air) falling from there, facing `facing`, at `percent` damage
/// (setup.c). Returns NULL, or why not.
/// The stage's left ledge (the left end of the floor under the middle of the
/// stage, followed left): its floor line, or -1, and where it is.
int host_left_ledge(float* x, float* y);
/// Player `slot` hanging on that ledge, as after a fresh grab of it (full
/// ledge intangibility), with that much damage.
const char* host_ledge(int slot, float percent);
const char* host_set_shield(int slot, float health);
const char* host_place(int slot, float x, float y, float facing, int air,
                       float percent);
/// The control protocol (control.c), when enabled.
extern int host_control_enabled;
void host_control_frame(void);
void host_fighter_json(int slot, char* out, size_t size);

/// The file's own bytes behind an archive object (archive.c).
void* host_dat_raw(const void* native);
void* host_dat_raw_room(const void* native, uint32_t* room);
uint32_t host_dat_blob_size(const void* at, uint32_t element);
/// The window build remembers some answers about archives by address
/// (window.c): an archive opened, one closed.
void host_window_opened(void);
void host_window_forget(const void* data, size_t size);

/// The window build only (window.c): a port played by a person, and
/// running at the console's speed instead of as fast as it goes.
const char* host_window_live(int port, const char* source);
void host_window_pace(int on);
void host_window_capture(int on);
const HostPad* host_window_seen(int port);

/// The last frame's wait for the driver on the control pipe, in ms.
extern double host_driver_ms;

/// A GameCube controller adapter, read directly (gcadapter.c).
void host_gcc_start(void);
void host_gcc_forget(void);
int host_gcc_decode(const uint8_t* report, int port, HostPad* pad);
int host_gcc_pad(int port, HostPad* pad);
int host_gcc_first(void);
void host_gcc_status(char* out, size_t size);
void host_window_devices(char* out, size_t size);
void host_gcc_take(void);
void host_gcc_counts(unsigned long* reports, unsigned long* errors,
                     unsigned long* opened, double* age);
/// Fullscreen on (1), off (0), the other of what it is (2); anything else
/// only asks. Returns what was last asked for.
int host_window_fullscreen(int want);
/// Another size for the window (not fullscreen). NULL, or why not.
const char* host_window_resize(int width, int height);
/// The window as JSON: its size in pixels, the frame the picture keeps to
/// in it, whether it is fullscreen and whether that was asked for.
void host_window_describe(char* out, size_t size);

/// The client's interface (ui.cpp): documents drawn over the window.
void host_ui_init(int width, int height);
void host_ui_frame(void);
const char* host_ui_command(const char* line);
/// An archive's data is going away (particles.c).
void host_particles_forget(const uint8_t* data, uint32_t size);

/// Random draws since the frame boundary (debug.c).
void host_rng_frame(void);
void host_rng_print(void);

/// Count a call of a generated stub.
void host_stub_hit(int index);
void host_stub_report(void);

/// One frame boundary: called by the game loop's pad poll.
void host_frame_tick(void);
/// The window build only (window.c): open the window; end one drawn frame
/// and begin the next.
void host_window_init(void);
void host_window_frame(void);

#endif
