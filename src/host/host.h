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

/// Queue a completion callback, delivered like an interrupt: at once if
/// interrupts are enabled, else when the game enables them again.
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

/// The match the next host_match_start() sets up.
typedef struct HostMatch {
    int ckind[4]; ///< CharacterKind, or -1 for an empty slot
    int human[4]; ///< a human (reads its pad) or a CPU
    int stage;    ///< stage id as in the match rules (0x20: FD)
    int stocks;
} HostMatch;

extern HostMatch host_match;
/// Each frame: keeps the host's mode override installed.
void host_match_install(void);
/// End the current scene and enter the match described by host_match.
void host_match_start(void);

/// The control protocol (control.c), when enabled.
extern int host_control_enabled;
void host_control_frame(void);
void host_fighter_json(int slot, char* out, size_t size);

/// Count a call of a generated stub.
void host_stub_hit(int index);
void host_stub_report(void);

/// One frame boundary: called by the game loop's pad poll.
void host_frame_tick(void);

#endif
