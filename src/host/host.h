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
    /// Further characters loaded with the match (CharacterKind), so that a
    /// CPU can become one of them at once (host_match_swap): a drill whose
    /// scenarios have different opponents, as the overlay's character
    /// rotation does it (src/melee/tm/rotation). Not all may fit.
    int preload[8];
    int preloads;
    /// Matches the game ended itself (L+R+A+Start in its pause, the end of
    /// a stock match), as opposed to a driver asking for another. Each is
    /// followed at once by the same match again, never by the game's own
    /// boot scenes (`state`'s "ended").
    unsigned ended;
} HostMatch;

extern HostMatch host_match;
/// End the process (control.c): without exit()'s teardown in the window
/// build.
void host_quit(void);
/// Whether a fighter's object still exists (the player table keeps it after
/// its match has ended).
int host_live_fighter(const void* gobj);
/// Each frame: keeps the host's mode override installed.
void host_match_install(void);
/// End the current scene and enter the match described by host_match.
void host_match_start(void);
/// Make the fighter in `slot` one of `ckind` in the same frame, if the
/// match loaded that character: 1 replaced, 0 it already was, -1 not
/// loaded.
int host_match_swap(int slot, int ckind);
/// The characters this match can swap to, as "ck ck ..." into `out`.
void host_match_loaded(char* out, size_t size);

/// Put player `slot`'s fighter standing on the floor at or below (x, y), or
/// (air) falling from there, facing `facing`, at `percent` damage
/// (setup.c). Returns NULL, or why not.
/// The stage's left ledge (the left end of the floor under the middle of the
/// stage, followed left): its floor line, or -1, and where it is.
int host_left_ledge(float* x, float* y);
/// Player `slot` hanging on that ledge, as after a fresh grab of it (full
/// ledge intangibility), with that much damage.
const char* host_ledge(int slot, float percent);
const char* host_rebirth(int slot, float x, float y);
const char* host_anchor(int slot, int on);
void host_anchor_frame(void);
const char* host_set_shield(int slot, float health);
/// What TM-CE does round loading a savestate (savestate_v1.c), for a new
/// attempt: the fighters' sounds and the crowd's stopped, the particles,
/// camera shakes and fighters' items gone, colour overlays off.
void host_clean(void);
/// Frames nobody sees or hears until host_quiet(0): no draw pass, no sound,
/// and (the window) no pacing and the last picture kept. Coming back, the
/// sounds those frames started are stopped and music they started begins
/// again from its start.
void host_quiet(int on);
int host_quiet_now(void);
void host_audio_quiet(int on);
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
void host_window_quiet(int on);
void host_window_capture(int on);
void host_window_mask(unsigned buttons);
void host_window_scripted(int port, int on);
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
/* audio.c: sound */
void host_audio_frame(void);
const uint8_t* host_aram_peek(uint32_t addr);
void host_window_audio(const int16_t* frames, int count);
const char* host_song(void);
/* state.c: the game's whole state, saved and loaded (rollback) */
size_t host_state_size(void);
void host_state_sizes(size_t* arena, size_t* statics, size_t* heap);
int host_state_save(int slot);
int host_state_load(int slot);
int host_state_dump(const char* path);
long host_state_frame(int slot);
uint64_t host_state_hash(void);
long host_state_diff(int slot, int* region);
uintptr_t host_state_address(int region, long offset);
void host_game_heap_stats(uint32_t* used, uint32_t* top, uint32_t* peak);
/* rollback.c: what each frame changed, for going back */
const char* host_rb_start(void);
void host_rb_stop(void);
int host_rb_running(void);
int host_rb_mark(void);
int host_rb_rewind(int frames);
int host_rb_kept(void);
void host_rb_report(char* out, size_t size);
/* net.c: rollback netcode */
int host_net_active(void);
int host_net_resimulating(void);
int host_net_boundary(void);
const char* host_net_start(int local, int bind_port, const char* peer_ip,
                           int peer_port, int delay, int lag, int loss,
                           int jitter);
void host_net_stop(void);
void host_net_report(char* out, size_t size);
uint64_t host_net_hash(void);
int host_net_inputs(uint32_t frame, char* out, size_t size);
int host_net_rng(uint32_t frame, char* out, size_t size);
void host_window_idle(void);
void host_window_delay_frame(void);
void host_window_clipboard(char* out, size_t size);
void host_window_set_clipboard(const char* text);
void host_control_frame(void);
/* ahead.c: the next frames played with a planned pad, then undone */
int host_ahead_active(void);
const char* host_ahead_begin(const char* line);
int host_ahead_boundary(void);
void host_frame_tick_rest(void);
void host_control_resume(void);

#endif
