/** @file
 * The game's state frame by frame, for rollback: what each frame changed,
 * kept for the last frames so any of them can be gone back to.
 *
 * A full snapshot (state.c) is 70 MB, most of it converted archive data
 * that a frame does not touch. Here only the pages a frame wrote are kept.
 * The kernel marks every page written since its marks were cleared (the
 * soft-dirty bit: /proc/self/clear_refs, /proc/self/pagemap). A mirror holds
 * the game's memory as it was at the last frame boundary. At each boundary
 * the pages written since are looked up; their mirror copies (what they were
 * before the frame) go into that frame's undo record, and their new contents
 * into the mirror. Going back N frames writes the last N records' old pages
 * back, newest first, into the game's memory and the mirror.
 *
 * The memory is state.c's three regions (the arena, the gathered statics,
 * the game heap) and the console's low memory. The game heap is followed as
 * far as it has ever reached.
 *
 * Which pages were written, two ways (Linux):
 *
 * - the watched regions alone (2026-11-24): they are write-protected through
 *   userfaultfd in its asynchronous mode (the kernel lifts a page's
 *   protection by itself at the first write to it: no handler), and a frame
 *   boundary asks for the pages whose protection is gone and has them
 *   protected again in the same call (the pagemap's PAGEMAP_SCAN, Linux
 *   6.7). What it costs follows the 70 MB watched;
 * - soft-dirty, where that is not to be had (an older kernel; MELEE_RB=
 *   softdirty asks for it): the marks are cleared for the whole process
 *   (/proc/self/clear_refs has no ranges), so every boundary and every
 *   going back costs by all the process has mapped. Measured in the window
 *   build (950 MB, most of it the graphics'): 0.9 ms a boundary and 0.8 ms
 *   a going back, 107 of the 154 ms one of an opponent's answers took to
 *   search; the same search headless (85 MB): 84 ms.
 *
 * A forked copy of a game (engine.c, "engine fork") whose rollback was
 * running, its mirror the game's memory as it stood, keeps that mirror: the
 * fork shares its pages, and only the pages a copy goes on to write are
 * copied. (Each copy made its own until 2026-11-24: 70 MB copied page by
 * page, 33 ms a copy, sixteen of them at once for one table of answers.)
 * host_rb_unsync says when the memory has changed behind the mirror's back
 * (a frame played for real, a command that places or changes something).
 *
 * host_rb_start says when neither way is there (CONFIG_MEM_SOFT_DIRTY).
 */
#define _GNU_SOURCE /* mremap */
#include "host.h"

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>
#ifndef _WIN32
#include <linux/fs.h>
#include <linux/userfaultfd.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#endif

extern char __game_state_start[], __game_state_end[];
void host_game_heap_extent(void** start, uint32_t* length);
void host_game_heap_stats(uint32_t* used, uint32_t* top, uint32_t* peak);

#define PAGE 4096u
#define SOFT_DIRTY (1ull << 55)
#define DEPTH 24      /* frames that can be gone back */
#define HEAP_TRACK (256u << 20)
#define HEAP_SLACK (16u << 20) /* tracked past the heap's peak */
/* the heap's mirror: room past what is followed, grown (remapped) when the
   heap passes it; not HEAP_TRACK at once, which the 32-bit window build
   once had no room for ("no memory for a 268435456-byte mirror") */
#define HEAP_ROOM (64u << 20)

typedef struct Region {
    uint8_t* start;
    size_t length;  ///< followed now (the heap's grows)
    uint8_t* mirror;
    size_t cap;     ///< the mirror's size (the heap's grows with it)
} Region;

enum { LOW, ARENA, STATICS, HEAP, NREGIONS };

typedef struct Record {
    uint32_t count;     ///< pages
    uint32_t capacity;
    uint8_t** pages;    ///< where each is in the game's memory
    uint8_t* data;      ///< what each held before the frame
} Record;

static Region regions[NREGIONS];
static Record records[DEPTH];
static int newest = -1; ///< the record of the last frame
static int kept;        ///< records that can be gone back through
static int running;
static int pagemap = -1, clear = -1;
static pid_t opened_by; ///< the process pagemap and clear are of
static int ranged;      ///< written pages: the watched regions' alone
static int uffd = -1;   ///< this process's userfaultfd (ranged)
static size_t heap_watched; ///< of the heap, write-protected so far (ranged)
/// The mirror is the game's memory as it is now: after a start, a mark, a
/// going back; not after anything else has changed the memory
/// (host_rb_unsync).
static int synced;
static uint64_t* entries;
static size_t entries_cap;
static struct {
    uint64_t marks, pages, max_pages, rewinds, rewound;
    double mark_ms, max_mark_ms, rewind_ms;
} stats;

static double now_ms(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e3 + t.tv_nsec / 1e6;
}

#ifdef _WIN32
/* Windows: the game's fixed mappings (low memory, the arena, the game heap)
   are made with MEM_WRITE_WATCH (src/host/win32/compat.c), and Windows
   lists the pages written in them since the last reset: Linux's soft-dirty
   bits, by another name. The statics are in the executable's image, which
   cannot be watched: every page of theirs is a candidate, and the mark's
   comparison with the mirror keeps only those that changed (1.1 MB, well
   under a millisecond a frame). */
long host_win32_written(void* base, size_t length, void** pages,
                        unsigned long max);
void host_win32_unwrite(void* base, size_t length);

static int watched(int region)
{
    return region != STATICS;
}

static int clear_marks(void)
{
    for (int i = 0; i < NREGIONS; i++) {
        if (watched(i) && regions[i].length != 0) {
            host_win32_unwrite(regions[i].start, regions[i].length);
        }
    }
    return 0;
}
#else
static int clear_marks(void)
{
    if (ranged) {
        return 0; /* (a mark's scan protects again what it reports) */
    }
    return pwrite(clear, "4", 1, 0) == 1 ? 0 : -1;
}
#endif

#if !defined(_WIN32) && defined(PAGEMAP_SCAN) && \
    defined(UFFD_FEATURE_WP_ASYNC) && defined(UFFD_FEATURE_WP_UNPOPULATED)
#define HAVE_RANGED 1
#define SCAN_VEC 512
static struct page_region scan_vec[SCAN_VEC];

/// This process's userfaultfd for write protection the kernel lifts by
/// itself, or -1: not in this kernel, not allowed, or not wanted
/// (MELEE_RB=softdirty). User-mode faults only: what an unprivileged
/// process may have, and all it needs (nothing waits on a handler).
static int ranged_open(void)
{
    struct uffdio_api api;
    const char* how = getenv("MELEE_RB");
    uint64_t need = UFFD_FEATURE_WP_ASYNC | UFFD_FEATURE_WP_UNPOPULATED;
    int fd;

    if (how != NULL && strcmp(how, "softdirty") == 0) {
        return -1;
    }
    fd = (int) syscall(SYS_userfaultfd, O_CLOEXEC | UFFD_USER_MODE_ONLY);
    if (fd < 0) {
        return -1;
    }
    memset(&api, 0, sizeof api);
    api.api = UFFD_API;
    api.features = need;
    if (ioctl(fd, UFFDIO_API, &api) < 0 || (api.features & need) != need) {
        close(fd);
        return -1;
    }
    return fd;
}

/// [start, start + length) watched from now: write-protected, a page's
/// protection gone at the first write to it.
static int ranged_watch(uint8_t* start, size_t length)
{
    struct uffdio_register reg;
    struct uffdio_writeprotect wp;

    if (length == 0) {
        return 0;
    }
    memset(&reg, 0, sizeof reg);
    reg.range.start = (uintptr_t) start;
    reg.range.len = length;
    reg.mode = UFFDIO_REGISTER_MODE_WP;
    if (ioctl(uffd, UFFDIO_REGISTER, &reg) < 0) {
        return -1;
    }
    memset(&wp, 0, sizeof wp);
    wp.range = reg.range;
    wp.mode = UFFDIO_WRITEPROTECT_MODE_WP;
    return ioctl(uffd, UFFDIO_WRITEPROTECT, &wp) < 0 ? -1 : 0;
}

static void record_page(struct Record* rec, uint8_t* page,
                        const uint8_t* old);

/// The pages of `r` written since they were last protected, protected
/// again by the same call; those that changed into `rec` (NULL: only
/// counted) and the mirror. How many the kernel reported, or -1.
static long ranged_mark(Region* r, struct Record* rec)
{
    struct pm_scan_arg arg;
    long written = 0;

    memset(&arg, 0, sizeof arg);
    arg.size = sizeof arg;
    arg.flags = PM_SCAN_WP_MATCHING | PM_SCAN_CHECK_WPASYNC;
    arg.start = (uintptr_t) r->start;
    arg.end = (uintptr_t) r->start + (r->length & ~(size_t) (PAGE - 1));
    arg.vec = (uintptr_t) scan_vec;
    arg.vec_len = SCAN_VEC;
    arg.category_mask = PAGE_IS_WRITTEN;
    arg.return_mask = PAGE_IS_WRITTEN;
    while (arg.start < arg.end) {
        int n = ioctl(pagemap, PAGEMAP_SCAN, &arg);
        if (n < 0) {
            return -1;
        }
        for (int k = 0; k < n; k++) {
            uintptr_t a = (uintptr_t) scan_vec[k].start;
            uintptr_t e = (uintptr_t) scan_vec[k].end;
            for (; a < e; a += PAGE) {
                uint8_t* live = (uint8_t*) a;
                uint8_t* mirror = r->mirror + (live - r->start);
                written++;
                if (rec == NULL || memcmp(live, mirror, PAGE) == 0) {
                    continue; /* written with what it held */
                }
                record_page(rec, live, mirror);
                memcpy(mirror, live, PAGE);
            }
        }
        if (arg.walk_end == 0 || arg.walk_end >= arg.end) {
            break;
        }
        arg.start = arg.walk_end; /* the list was full: on from there */
    }
    return written;
}
#endif

static void* mirror_of(size_t length)
{
    void* m = mmap(NULL, length, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0);
    if (m == MAP_FAILED) {
        host_fatal("rollback: no memory for a %zu-byte mirror", length);
    }
    return m;
}

/// The game heap as far as it has ever reached (pages past its top that
/// were in use once hold whatever a later allocation will find there),
/// and HEAP_SLACK past that: frames that are gone back over (a lookahead,
/// a search: ahead.c, engine.c) may reach further, and what they wrote
/// there must be undone too, or a later allocation finds it where the game
/// that never played those frames finds what was there before (a shadow
/// game once took 1% more damage from it: melee-engine.md).
static size_t heap_length(void)
{
    uint32_t used, top, peak;
    size_t want;
    host_game_heap_stats(&used, &top, &peak);
    if (peak > HEAP_TRACK) {
        host_fatal("rollback: the game heap passed %u MB", HEAP_TRACK >> 20);
    }
    want = (size_t) peak + HEAP_SLACK; /* inside the heap's reservation */
    if (want > HEAP_TRACK) {
        want = HEAP_TRACK;
    }
    return (want + PAGE - 1) & ~(size_t) (PAGE - 1);
}

/// The heap's mirror for `length` followed: HEAP_ROOM more, at most
/// HEAP_TRACK.
static size_t heap_room(size_t length)
{
    size_t cap = (length + HEAP_ROOM + PAGE - 1) & ~(size_t) (PAGE - 1);
    return cap < HEAP_TRACK ? cap : HEAP_TRACK;
}

static void follow_heap(void)
{
    Region* r = &regions[HEAP];
    size_t want = heap_length();
    if (want > r->length) {
        if (want > HEAP_TRACK) {
            host_fatal("rollback: the game heap passed %u MB",
                       HEAP_TRACK >> 20);
        }
        if (want > r->cap) {
            /* the mirror grows; everything finds it through r->mirror */
            size_t cap = heap_room(want);
#ifdef _WIN32
            /* no mremap: a new mirror, what is followed copied over */
            void* m = mirror_of(cap);
            memcpy(m, r->mirror, r->length);
            munmap(r->mirror, r->cap);
#else
            void* m = mremap(r->mirror, r->cap, cap, MREMAP_MAYMOVE);
            if (m == MAP_FAILED) {
                host_fatal("rollback: no memory to grow the heap's mirror "
                           "to %zu bytes", cap);
            }
#endif
            r->mirror = m;
            r->cap = cap;
        }
        /* the new pages as they are now: their old contents for the
           frame that reached them */
        memcpy(r->mirror + r->length, r->start + r->length,
               want - r->length);
        r->length = want;
    }
#ifdef HAVE_RANGED
    if (ranged && r->length > heap_watched) {
        if (ranged_watch(r->start + heap_watched,
                         r->length - heap_watched) < 0)
        {
            host_fatal("rollback: the heap's new pages could not be "
                       "watched: %s", strerror(errno));
        }
        heap_watched = r->length;
    }
#endif
}

void host_rb_unsync(void)
{
    synced = 0;
}

const char* host_rb_start(void)
{
    void* heap;
    uint32_t top;
    int inherit = 0;

    if (running && opened_by == getpid()) {
        if (!synced) {
            /* frames were played for real since, or something placed: the
               mirror catches up (a mark; nothing to go back to before it) */
            host_rb_mark();
            newest = -1;
            kept = 0;
        }
        return NULL;
    }
#ifdef _WIN32
    opened_by = getpid(); /* nothing to open: the mappings are watched */
#else
    /* a forked copy of a game whose rollback was running, its mirror the
       memory as it stood at the fork: the mirror came with the fork */
    inherit = running && synced && regions[HEAP].mirror != NULL &&
              opened_by != 0 && opened_by != getpid();
    if (pagemap < 0 || opened_by != getpid()) {
        /* /proc/self is the process that opened it: a process restored
           from a snapshot (control.c) or forked (engine.c) opens its own,
           and starts over; its userfaultfd is its own too */
        if (pagemap >= 0) {
            close(pagemap);
            close(clear);
        }
        if (uffd >= 0) {
            close(uffd); /* (the parent's: it keeps its own) */
            uffd = -1;
        }
        pagemap = open("/proc/self/pagemap", O_RDONLY);
        clear = open("/proc/self/clear_refs", O_WRONLY);
        if (pagemap < 0 || clear < 0) {
            return "no /proc/self/pagemap or clear_refs";
        }
        opened_by = getpid();
    }
#endif
    host_game_heap_extent(&heap, &top);
    regions[LOW].start = (uint8_t*) 0x80000000u;
    regions[LOW].length = 0x4000;
    regions[ARENA].start = (uint8_t*) (uintptr_t) (HOST_ARENA_LO & ~0xFFFu);
    regions[ARENA].length = 0x81800000u - (HOST_ARENA_LO & ~0xFFFu);
    regions[STATICS].start = (uint8_t*) __game_state_start;
    regions[STATICS].length =
        (size_t) (__game_state_end - __game_state_start);
    regions[HEAP].start = heap;
    if (!inherit) {
        regions[HEAP].length = 0;
        for (int i = 0; i < NREGIONS; i++) {
            size_t cap = i == HEAP ? heap_room(heap_length())
                                   : regions[i].length;
            if (regions[i].mirror == NULL) {
                regions[i].mirror = mirror_of(cap);
                regions[i].cap = cap;
            }
            if (i != HEAP) {
                memcpy(regions[i].mirror, regions[i].start,
                       regions[i].length);
            }
        }
    } else if (getenv("MELEE_RB_VERIFY") != NULL) {
        /* (a test's: the mirror kept is the memory, byte for byte) */
        for (int i = 0; i < NREGIONS; i++) {
            if (memcmp(regions[i].mirror, regions[i].start,
                       regions[i].length) != 0)
            {
                host_fatal("rollback: region %d's mirror, kept across a "
                           "fork, is not the game's memory", i);
            }
        }
    }
    ranged = 0;
    heap_watched = 0;
#ifdef HAVE_RANGED
    if (uffd >= 0) {
        close(uffd); /* (started again in this process: watched anew) */
    }
    uffd = ranged_open();
    if (uffd >= 0) {
        ranged = 1;
        for (int i = 0; i < NREGIONS && ranged; i++) {
            if (i != HEAP &&
                ranged_watch(regions[i].start,
                             regions[i].length & ~(size_t) (PAGE - 1)) < 0)
            {
                ranged = 0;
            }
        }
        if (ranged && regions[HEAP].length != 0) {
            /* (a kept mirror's heap: all of it; a new one's is watched
               as it is followed, below) */
            if (ranged_watch(regions[HEAP].start, regions[HEAP].length) < 0)
            {
                ranged = 0;
            } else {
                heap_watched = regions[HEAP].length;
            }
        }
        if (ranged) {
            /* it works: a page written now must be reported, once */
            volatile uint8_t* probe = regions[STATICS].start;
            probe[0] = probe[0];
            if (ranged_mark(&regions[STATICS], NULL) < 1 ||
                ranged_mark(&regions[STATICS], NULL) != 0)
            {
                ranged = 0;
            }
        }
        if (!ranged) {
            close(uffd); /* its protection goes with it */
            uffd = -1;
            heap_watched = 0;
        }
    }
#endif
    follow_heap();
    if (clear_marks() < 0) {
        return "clear_refs refused";
    }
#ifdef _WIN32
    /* write watching works: a page of the arena written now must show it */
    {
        volatile uint8_t* probe = regions[ARENA].start;
        void* page = NULL;
        probe[0] = probe[0];
        if (host_win32_written(regions[ARENA].start, PAGE, &page, 1) != 1) {
            return "the game's memory is not watched for writes "
                   "(MEM_WRITE_WATCH)";
        }
        clear_marks();
    }
#else
    /* soft-dirty works: a page written now must show it */
    if (!ranged) {
        volatile uint8_t* probe = regions[STATICS].start;
        uint64_t entry = 0;
        probe[0] = probe[0];
        if (pread(pagemap, &entry, 8,
                  (off_t) ((uintptr_t) probe / PAGE) * 8) != 8 ||
            !(entry & SOFT_DIRTY))
        {
            return "the kernel does not mark written pages "
                   "(CONFIG_MEM_SOFT_DIRTY, or userfaultfd's asynchronous "
                   "write protection)";
        }
        clear_marks();
    }
#endif
    newest = -1;
    kept = 0;
    memset(&stats, 0, sizeof stats);
    running = 1;
    synced = 1;
    return NULL;
}

void host_rb_stop(void)
{
    running = 0;
    kept = 0;
    newest = -1;
    synced = 0;
#ifndef _WIN32
    if (uffd >= 0) {
        close(uffd); /* the regions are no longer watched */
        uffd = -1;
    }
    ranged = 0;
    heap_watched = 0;
#endif
}

/// How the written pages are found: "ranged" (the watched regions alone),
/// "soft-dirty" (the whole process's marks), "watch" (Windows).
const char* host_rb_how(void)
{
#ifdef _WIN32
    return "watch";
#else
    return ranged ? "ranged" : "soft-dirty";
#endif
}

int host_rb_running(void)
{
    return running;
}

static void record_page(Record* rec, uint8_t* page, const uint8_t* old)
{
    if (rec->count == rec->capacity) {
        uint32_t cap = rec->capacity ? rec->capacity * 2 : 256;
        rec->pages = realloc(rec->pages, cap * sizeof *rec->pages);
        rec->data = realloc(rec->data, (size_t) cap * PAGE);
        if (rec->pages == NULL || rec->data == NULL) {
            host_fatal("rollback: no memory for an undo record");
        }
        rec->capacity = cap;
    }
    rec->pages[rec->count] = page;
    memcpy(rec->data + (size_t) rec->count * PAGE, old, PAGE);
    rec->count++;
}

/// At a frame boundary: what the frame since the last one changed becomes
/// its undo record. Returns the pages it wrote.
int host_rb_mark(void)
{
    Record* rec;
    double t0 = now_ms(), took;

    if (!running) {
        return -1;
    }
    follow_heap();
    newest = (newest + 1) % DEPTH;
    rec = &records[newest];
    rec->count = 0;
#ifdef _WIN32
    for (int i = 0; i < NREGIONS; i++) {
        Region* r = &regions[i];
        size_t pages = r->length / PAGE;
        long n;
        if (pages == 0) {
            continue;
        }
        if (!watched(i)) {
            /* every page; the comparison keeps the changed ones */
            for (size_t p = 0; p < pages; p++) {
                uint8_t* live = r->start + p * PAGE;
                uint8_t* mirror = r->mirror + p * PAGE;
                if (memcmp(live, mirror, PAGE) != 0) {
                    record_page(rec, live, mirror);
                    memcpy(mirror, live, PAGE);
                }
            }
            continue;
        }
        if (entries_cap < pages * 2) {
            /* (entries holds the written pages' addresses here) */
            entries = realloc(entries, pages * sizeof *entries);
            entries_cap = pages * 2;
        }
        n = host_win32_written(r->start, r->length, (void**) entries,
                               (unsigned long) pages);
        if (n < 0) {
            host_fatal("rollback: the written pages could not be read");
        }
        for (long k = 0; k < n; k++) {
            uint8_t* live = ((uint8_t**) entries)[k];
            uint8_t* mirror = r->mirror + (live - r->start);
            if (memcmp(live, mirror, PAGE) == 0) {
                continue; /* written with what it held */
            }
            record_page(rec, live, mirror);
            memcpy(mirror, live, PAGE);
        }
    }
#else
    for (int i = 0; i < NREGIONS; i++) {
        Region* r = &regions[i];
        size_t pages = r->length / PAGE;
        off_t first = (off_t) ((uintptr_t) r->start / PAGE);
#ifdef HAVE_RANGED
        if (ranged) {
            if (ranged_mark(r, rec) < 0) {
                host_fatal("rollback: the written pages could not be "
                           "read: %s", strerror(errno));
            }
            continue;
        }
#endif
        if (entries_cap < pages) {
            entries = realloc(entries, pages * sizeof *entries);
            entries_cap = pages;
        }
        if (pread(pagemap, entries, pages * 8, first * 8) !=
            (ssize_t) (pages * 8))
        {
            host_fatal("rollback: pagemap read failed: %s", strerror(errno));
        }
        for (size_t p = 0; p < pages; p++) {
            if (entries[p] & SOFT_DIRTY) {
                uint8_t* live = r->start + p * PAGE;
                uint8_t* mirror = r->mirror + p * PAGE;
                if (memcmp(live, mirror, PAGE) == 0) {
                    continue; /* written with what it held */
                }
                record_page(rec, live, mirror);
                memcpy(mirror, live, PAGE);
            }
        }
    }
#endif
    clear_marks();
    if (kept < DEPTH) {
        kept++;
    }
    took = now_ms() - t0;
    stats.mark_ms += took;
    if (took > stats.max_mark_ms) {
        stats.max_mark_ms = took;
    }
    stats.marks++;
    stats.pages += rec->count;
    if (rec->count > stats.max_pages) {
        stats.max_pages = rec->count;
    }
    synced = 1;
    return (int) rec->count;
}

/// Back `frames` frame boundaries (the state at the boundary that many
/// marks ago). The records gone back through are dropped: the frames are
/// played again and marked again.
int host_rb_rewind(int frames)
{
    double t0 = now_ms();

    if (!running || frames < 0 || frames > kept) {
        return -1;
    }
    for (int n = 0; n < frames; n++) {
        Record* rec = &records[newest];
        for (int32_t k = (int32_t) rec->count - 1; k >= 0; k--) {
            uint8_t* page = rec->pages[k];
            const uint8_t* old = rec->data + (size_t) k * PAGE;
            memcpy(page, old, PAGE);
            for (int i = 0; i < NREGIONS; i++) {
                Region* r = &regions[i];
                if (page >= r->start && page < r->start + r->length) {
                    memcpy(r->mirror + (page - r->start), old, PAGE);
                    break;
                }
            }
        }
        rec->count = 0;
        newest = (newest + DEPTH - 1) % DEPTH;
        kept--;
    }
    /* the writes above are not a frame's. (Ranged, the pages written back
       stay unprotected: the next mark compares them with the mirror,
       which they are, and that is cheaper than protecting them here.) */
    clear_marks();
    synced = 1;
    stats.rewind_ms += now_ms() - t0;
    stats.rewinds++;
    stats.rewound += (uint64_t) frames;
    return 0;
}

/// The last two records as one: going back over it is going back over
/// both. A search that moves its branch point forward along a line (the
/// engine's timing scan, engine.c) keeps one record for it, not one per
/// step, so it never runs out of records. A page in both keeps the older
/// record's copy (what it was before both); a page only in the newer is
/// added with its copy, which is what it was before both too.
int host_rb_merge(void)
{
    static uint8_t** seen;
    static uint32_t seen_cap;
    Record *older, *newer;
    uint32_t mask, have;

    if (!running || kept < 2) {
        return -1;
    }
    newer = &records[newest];
    older = &records[(newest + DEPTH - 1) % DEPTH];
    /* the older record's pages, in an open-addressing set */
    have = 64;
    while (have < older->count * 2 + 2) {
        have *= 2;
    }
    if (seen_cap < have) {
        seen = realloc(seen, have * sizeof *seen);
        if (seen == NULL) {
            host_fatal("rollback: no memory to merge records");
        }
        seen_cap = have;
    }
    memset(seen, 0, have * sizeof *seen);
    mask = have - 1;
    for (uint32_t k = 0; k < older->count; k++) {
        uint32_t h = (uint32_t) ((uintptr_t) older->pages[k] / PAGE) & mask;
        while (seen[h] != NULL) {
            h = (h + 1) & mask;
        }
        seen[h] = older->pages[k];
    }
    for (uint32_t k = 0; k < newer->count; k++) {
        uint8_t* page = newer->pages[k];
        uint32_t h = (uint32_t) ((uintptr_t) page / PAGE) & mask;
        int found = 0;
        while (seen[h] != NULL) {
            if (seen[h] == page) {
                found = 1;
                break;
            }
            h = (h + 1) & mask;
        }
        if (!found) {
            /* (the set is not grown: a page the newer record holds once
               is looked up once) */
            record_page(older, page, newer->data + (size_t) k * PAGE);
        }
    }
    newer->count = 0;
    newest = (newest + DEPTH - 1) % DEPTH;
    kept--;
    return 0;
}

int host_rb_kept(void)
{
    return kept;
}

/// A line of numbers: marks, pages recorded, the most in one frame,
/// rewinds, frames rewound, ms in marks (all, the longest), ms rewinding.
void host_rb_report(char* out, size_t size)
{
    snprintf(out, size, "%llu %llu %llu %llu %llu %.3f %.3f %.3f",
             (unsigned long long) stats.marks,
             (unsigned long long) stats.pages,
             (unsigned long long) stats.max_pages,
             (unsigned long long) stats.rewinds,
             (unsigned long long) stats.rewound, stats.mark_ms,
             stats.max_mark_ms, stats.rewind_ms);
}
