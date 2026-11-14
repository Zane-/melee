/** @file
 * Entry point of the native headless game, and its frame boundary.
 *
 * The game's own `main` (gmmain.c, compiled as `game_main`) runs unchanged
 * and never returns: its scene loop waits each frame for a pad sample, in
 * lb_80019894. That wait is the frame boundary, as in the Python simulator:
 * one call is one frame.
 */
#include "host.h"

#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>

#include <dolphin/os.h>
#include <sysdolphin/baselib/controller.h>

int game_main(void);
void fn_800195FC(void);

/* --- generated stubs ------------------------------------------------------ */

extern const char* const host_stub_names[];
extern unsigned host_stub_hits[];
extern const int host_stub_count;
static int report_stubs;
static uint32_t match_at;    ///< frame at which --match starts its match
static uint32_t trace_every; ///< print both fighters every N frames

void host_stub_hit(int index)
{
    host_stub_hits[index]++;
}

void host_stub_report(void)
{
    if (!report_stubs) {
        return;
    }
    fprintf(stderr, "[host] stubs called:");
    for (int i = 0; i < host_stub_count; i++) {
        if (host_stub_hits[i] != 0) {
            fprintf(stderr, " %s:%u", host_stub_names[i], host_stub_hits[i]);
        }
    }
    fputc('\n', stderr);
}

/* --- the frame boundary --------------------------------------------------- */

void host_frame_tick(void)
{
    host.int_enabled = 1;
    host_deliver();
    host.frame++;
    host_advance(HOST_TICKS_PER_FRAME);
    host_match_install();
    if (match_at != 0 && host.frame == match_at) {
        host.pads[1].connected = 1;
        host_match_start();
    }
    if (trace_every != 0 && host.frame % trace_every == 0) {
        char a[512], b[512];
        host_fighter_json(0, a, sizeof a);
        host_fighter_json(1, b, sizeof b);
        printf("@ %u %s %s\n", host.frame, a, b);
    }
#ifdef HOST_WINDOW
    host_window_frame();
#endif
    host_control_frame();
    host_frame_tick_rest();
}

/// What a frame boundary does after the driver's commands. Also where a
/// boundary goes on once a lookahead (ahead.c), begun by one of those
/// commands, has been undone. The first frame of a lookahead runs it too,
/// without its sound and per-frame hook: those are real time's.
void host_frame_tick_rest(void)
{
    host_anchor_frame();
    if (!host_ahead_active()) {
        host_audio_frame();
    }
    host_rng_frame();
    if (host.on_frame != NULL && !host_ahead_active()) {
        host.on_frame();
    }
    if (host.max_frames != 0 && host.frame > host.max_frames) {
        fflush(stdout);
        host_log("stopped after %u frames", host.max_frames);
        host_stub_report();
        exit(0);
    }
}

/// The scene loop's wait for a pad sample (the vanilla function is built as
/// lb_80019894_vanilla and not used: it reads a queue filled by an alarm).
/// One frame passes, the pads are sampled, and the queue length is
/// reported.
u8 lb_80019894(void)
{
    if (host_ahead_active()) {
        /* a frame played ahead; or the lookahead is over, the game is back
           at the boundary its command was read at, and that boundary goes
           on: more commands, then the rest of it (ahead.c) */
        if (!host_ahead_boundary()) {
            host_control_resume();
            host_frame_tick_rest();
        }
        fn_800195FC();
        return HSD_PadGetRawQueueCount();
    }
    if (host_net_active()) {
        /* a netplay session (net.c): a frame, or a wait */
        if (!host_net_boundary()) {
            return 0;
        }
        fn_800195FC();
        return HSD_PadGetRawQueueCount();
    }
    host_frame_tick();
    if (host_net_active()) {
        /* a session began during this tick's commands: its first frame
           is the next tick's, on both sides */
        return 0;
    }
    fn_800195FC();
    return HSD_PadGetRawQueueCount();
}

static void on_fault(int sig, siginfo_t* info, void* context)
{
    (void) context;
    host_fatal("signal %d at address %p (frame %u)", sig, info->si_addr,
               host.frame);
}

/* --- entry ---------------------------------------------------------------- */

static void usage(void)
{
    fprintf(stderr,
            "usage: melee_headless [--disc DIR] [--frames N] [-v] "
            "[--stubs]\n"
            "       [--match P1,P2,STAGE] [--trace N] [--control]\n"
            "  --disc DIR   extracted disc (holds files/); default "
            "build/disc\n"
            "  --frames N   stop after N frames\n"
            "  -v           print the game's own reports\n"
            "  --stubs      list the stubbed SDK functions that were called\n"
            "  --match      start a match at frame 30: character kinds and "
            "stage id\n"
            "  --trace N    print both fighters every N frames\n"
            "  --control    obey commands on stdin (see control.c)\n"
            "  --draw       run the draw pass too (graphics are no-ops)\n");
    exit(1);
}

int main(int argc, char** argv)
{
    const char* disc = "build/disc";

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--disc") == 0 && i + 1 < argc) {
            disc = argv[++i];
        } else if (strcmp(argv[i], "--frames") == 0 && i + 1 < argc) {
            host.max_frames = (uint32_t) strtoul(argv[++i], NULL, 0);
        } else if (strcmp(argv[i], "-v") == 0) {
            host.verbose = 1;
        } else if (strcmp(argv[i], "--stubs") == 0) {
            report_stubs = 1;
        } else if (strcmp(argv[i], "--draw") == 0) {
            host.draw = 1;
        } else if (strcmp(argv[i], "--control") == 0) {
            host_control_enabled = 1;
        } else if (strcmp(argv[i], "--match") == 0 && i + 1 < argc) {
            /* P1,P2,STAGE as numbers, at frame 30 */
            sscanf(argv[++i], "%d,%d,%d", &host_match.ckind[0],
                   &host_match.ckind[1], &host_match.stage);
            match_at = 30;
        } else if (strcmp(argv[i], "--trace") == 0 && i + 1 < argc) {
            trace_every = (uint32_t) strtoul(argv[++i], NULL, 0);
        } else {
            usage();
        }
    }
    setvbuf(stdout, NULL, _IOLBF, 0);
    {
        struct sigaction sa;
        memset(&sa, 0, sizeof sa);
        sa.sa_sigaction = on_fault;
        sa.sa_flags = SA_SIGINFO | SA_RESETHAND;
        sigaction(SIGSEGV, &sa, NULL);
        sigaction(SIGBUS, &sa, NULL);
        sigaction(SIGFPE, &sa, NULL);
        sigaction(SIGILL, &sa, NULL);
        sigaction(SIGABRT, &sa, NULL); /* a library's abort() */
    }
    host.pads[0].connected = 1;
    host.int_enabled = 1;
    /* Before anything else maps memory: the arena has to be at the
       console's addresses. */
    if (getenv("MELEE_DEBUGGER") != NULL) {
        /* let a debugger that is not this process's parent attach (the
           kernel's default only allows a parent): for profiling */
        prctl(PR_SET_PTRACER, PR_SET_PTRACER_ANY, 0, 0, 0);
    }
    host_memory_init();
    host_disc_init(disc);
#ifdef HOST_WINDOW
    host.draw = 1;
    host_window_init();
#endif
    game_main();
    host_log("the game's main returned");
    return 0;
}
