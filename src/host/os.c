/** @file
 * OS: reports, asserts, emulated time, interrupts and alarms, the arena.
 *
 * There are no real interrupts. A completion (a disc read, an audio RAM
 * transfer, an alarm) is a queued callback, delivered when the game enables
 * interrupts, when it idles, and at the frame boundary. Time is emulated,
 * so runs are deterministic.
 */
#include "host.h"

#include <execinfo.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>

#include <dolphin/os.h>

HostState host;

/* --- reports --------------------------------------------------------- */

void host_log(const char* fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    fputs("[host] ", stderr);
    vfprintf(stderr, fmt, ap);
    fputc('\n', stderr);
    va_end(ap);
}

void host_backtrace(void)
{
    void* frames[48];
    int n = backtrace(frames, 48);
    fflush(stdout);
    backtrace_symbols_fd(frames, n, 2);
}

_Noreturn void host_fatal(const char* fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    fflush(stdout);
    fputs("[host] FATAL: ", stderr);
    vfprintf(stderr, fmt, ap);
    fputc('\n', stderr);
    va_end(ap);
    host_backtrace();
    host_stub_report();
    if (host_control_enabled) {
        /* Whoever drives the game is waiting for a reply; with snapshots
           asleep, stdout stays open after this process is gone. */
        printf("@ fatal\n");
        fflush(stdout);
    }
    exit(2);
}

void OSVReport(const char* msg, va_list list)
{
    if (host.verbose) {
        fputs("[game] ", stdout);
        vprintf(msg, list);
    }
}

void OSReport(const char* msg, ...)
{
    va_list ap;
    va_start(ap, msg);
    OSVReport(msg, ap);
    va_end(ap);
}

void OSPanic(const char* file, int line, const char* msg, ...)
{
    va_list ap;
    va_start(ap, msg);
    fflush(stdout);
    fprintf(stderr, "[game] PANIC %s:%d: ", file, line);
    vfprintf(stderr, msg, ap);
    fputc('\n', stderr);
    va_end(ap);
    host_fatal("OSPanic");
}

/* sysdolphin/baselib/debug.c is not built natively (PowerPC registers). */
void __assert(const char* file, u32 line, const char* cond)
{
    host_fatal("assert %s:%u: %s", file, line, cond);
}

void HSD_Panic(const char* file, u32 line, const char* msg)
{
    host_fatal("HSD_Panic %s:%u: %s", file, line, msg);
}

void HSD_LogInit(void) {}

/* Constants of the console's C library that the game reads directly. */
float MSL_TrigF_80400770[1] = { __builtin_nanf("0x3fffff") }; /* 7FFFFFFF */
float MSL_TrigF_80400774[1] = { __builtin_inff() };

/* --- time -------------------------------------------------------------- */

OSTime OSGetTime(void)
{
    host.ticks += 64;
    return host.ticks;
}

OSTick OSGetTick(void)
{
    host.ticks += 64;
    return (OSTick) host.ticks;
}

static int is_leap(int year)
{
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

/// Ticks count from 2000-01-01, as on the console.
void OSTicksToCalendarTime(OSTime ticks, OSCalendarTime* td)
{
    static const int month_days[12] = { 31, 28, 31, 30, 31, 30,
                                        31, 31, 30, 31, 30, 31 };
    OSTime rate = OS_TIMER_CLOCK;
    OSTime sub = ticks % rate;
    OSTime secs;
    int days, year, month;

    if (sub < 0) {
        sub += rate;
    }
    td->usec = (int) (sub * 8 / (rate / 125000) % 1000);
    td->msec = (int) (sub / (rate / 1000));
    secs = (ticks - sub) / rate;
    days = (int) (secs / 86400);
    secs %= 86400;
    if (secs < 0) {
        secs += 86400;
        days--;
    }
    td->sec = (int) (secs % 60);
    td->min = (int) (secs / 60 % 60);
    td->hour = (int) (secs / 3600);
    td->wday = (days + 6) % 7; /* 2000-01-01 was a Saturday */
    for (year = 2000; days >= (is_leap(year) ? 366 : 365); year++) {
        days -= is_leap(year) ? 366 : 365;
    }
    td->year = year;
    td->yday = days;
    for (month = 0;; month++) {
        int len = month_days[month] + (month == 1 && is_leap(year));
        if (days < len) {
            break;
        }
        days -= len;
    }
    td->mon = month;
    td->mday = days + 1;
}

/* --- interrupts and completions ---------------------------------------- */

typedef struct Pending {
    void (*func)(intptr_t, intptr_t);
    intptr_t a, b;
} Pending;

#define MAX_PENDING 256
static Pending pending[MAX_PENDING];
static int pending_head, pending_count;

void host_deliver(void)
{
    if (host.delivering) {
        return;
    }
    while (pending_count > 0 && host.int_enabled) {
        Pending p = pending[pending_head];
        pending_head = (pending_head + 1) % MAX_PENDING;
        pending_count--;
        /* A handler runs with interrupts off, like the real one. */
        host.int_enabled = 0;
        host.delivering = 1;
        p.func(p.a, p.b);
        host.delivering = 0;
        host.int_enabled = 1;
    }
}

void host_post(void (*func)(intptr_t, intptr_t), intptr_t a, intptr_t b)
{
    if (pending_count == MAX_PENDING) {
        host_fatal("completion queue full");
    }
    pending[(pending_head + pending_count++) % MAX_PENDING] =
        (Pending){ func, a, b };
    /* Not delivered here: like the simulator, a completion arrives the next
       time the game enables interrupts, idles or ends a frame, never inside
       the call that started the work. */
}

BOOL OSDisableInterrupts(void)
{
    BOOL old = host.int_enabled;
    host.int_enabled = 0;
    return old;
}

BOOL OSEnableInterrupts(void)
{
    BOOL old = host.int_enabled;
    if (!host.delivering) {
        host.int_enabled = 1;
        host_deliver();
    }
    return old;
}

BOOL OSRestoreInterrupts(BOOL level)
{
    BOOL old = host.int_enabled;
    if (host.delivering) {
        return old;
    }
    host.int_enabled = level != 0;
    if (level) {
        host_deliver();
    }
    return old;
}

/* --- alarms ------------------------------------------------------------ */

#define MAX_ALARMS 32
static struct {
    OSAlarm* alarm;
    int64_t due;
    OSAlarmHandler handler;
} alarms[MAX_ALARMS];

void OSInitAlarm(void) {}

void OSCreateAlarm(OSAlarm* alarm)
{
    memset(alarm, 0, sizeof *alarm);
}

void OSCancelAlarm(OSAlarm* alarm)
{
    for (int i = 0; i < MAX_ALARMS; i++) {
        if (alarms[i].alarm == alarm) {
            alarms[i].alarm = NULL;
        }
    }
}

void OSSetAlarm(OSAlarm* alarm, OSTime tick, OSAlarmHandler handler)
{
    OSCancelAlarm(alarm);
    for (int i = 0; i < MAX_ALARMS; i++) {
        if (alarms[i].alarm == NULL) {
            alarms[i].alarm = alarm;
            alarms[i].due = host.ticks + tick;
            alarms[i].handler = handler;
            return;
        }
    }
    host_fatal("too many alarms");
}

/// The only periodic alarm is the pad sampler, which the frame boundary
/// drives itself (host_frame_tick).
void OSSetPeriodicAlarm(OSAlarm* alarm, OSTime start, OSTime period,
                        OSAlarmHandler handler)
{
    (void) alarm;
    (void) start;
    (void) period;
    (void) handler;
}

static void alarm_fire(intptr_t handler, intptr_t alarm)
{
    ((OSAlarmHandler) handler)((OSAlarm*) alarm, NULL);
}

void host_advance(int64_t ticks)
{
    host.ticks += ticks;
    for (;;) {
        int best = -1;
        for (int i = 0; i < MAX_ALARMS; i++) {
            if (alarms[i].alarm != NULL && alarms[i].due <= host.ticks &&
                (best < 0 || alarms[i].due < alarms[best].due))
            {
                best = i;
            }
        }
        if (best < 0) {
            break;
        }
        OSAlarm* alarm = alarms[best].alarm;
        alarms[best].alarm = NULL;
        host_post(alarm_fire, (intptr_t) alarms[best].handler,
                  (intptr_t) alarm);
    }
}

/* --- memory ------------------------------------------------------------ */

static uintptr_t arena_lo = HOST_ARENA_LO;
static uintptr_t arena_hi = HOST_ARENA_HI;

/// The arena lives at the console's addresses, so heap pointers look like
/// the console's (anything that tells pointers from numbers by their top
/// bit keeps working), and low memory holds the boot information.
void host_memory_init(void)
{
    uintptr_t start = HOST_ARENA_LO & ~0xFFFu;
    size_t size = 0x81800000u - start;
    void* p = mmap((void*) start, size, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED_NOREPLACE, -1, 0);
    if (p != (void*) start) {
        host_fatal("cannot map the arena at %p", (void*) start);
    }
    p = mmap((void*) 0x80000000u, 0x4000, PROT_READ | PROT_WRITE,
             MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED_NOREPLACE, -1, 0);
    if (p != (void*) 0x80000000u) {
        host_fatal("cannot map low memory");
    }
}

void OSInit(void) {}

void* OSGetArenaLo(void)
{
    return (void*) arena_lo;
}

void* OSGetArenaHi(void)
{
    return (void*) arena_hi;
}

void OSSetArenaLo(void* addr)
{
    arena_lo = (uintptr_t) addr;
}

void OSSetArenaHi(void* addr)
{
    arena_hi = (uintptr_t) addr;
}

void* OSAllocFromArenaHi(u32 size, u32 align)
{
    arena_hi = (arena_hi & ~(uintptr_t) (align - 1)) - size;
    arena_hi &= ~(uintptr_t) (align - 1);
    return (void*) arena_hi;
}

u32 OSGetConsoleSimulatedMemSize(void)
{
    return 0x01800000;
}

u32 OSGetPhysicalMemSize(void)
{
    return 0x01800000;
}

u32 OSGetSoundMode(void)
{
    return 1; /* stereo */
}

void OSResetSystem(int reset, u32 code, BOOL force_menu)
{
    (void) reset;
    (void) code;
    (void) force_menu;
    host_log("OSResetSystem: the game asked to reset; stopping");
    host_stub_report();
    exit(0);
}
