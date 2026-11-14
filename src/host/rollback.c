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
 * Linux only (soft-dirty is in the common distributions' kernels:
 * CONFIG_MEM_SOFT_DIRTY); host_rb_start says when it is not there.
 */
#include "host.h"

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

extern char __game_state_start[], __game_state_end[];
void host_game_heap_extent(void** start, uint32_t* length);
void host_game_heap_stats(uint32_t* used, uint32_t* top, uint32_t* peak);

#define PAGE 4096u
#define SOFT_DIRTY (1ull << 55)
#define DEPTH 24      /* frames that can be gone back */
#define HEAP_TRACK (256u << 20)
#define HEAP_SLACK (16u << 20) /* tracked past the heap's peak */

typedef struct Region {
    uint8_t* start;
    size_t length;  ///< followed now (the heap's grows)
    uint8_t* mirror;
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

static int clear_marks(void)
{
    return pwrite(clear, "4", 1, 0) == 1 ? 0 : -1;
}

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

static void follow_heap(void)
{
    Region* r = &regions[HEAP];
    size_t want = heap_length();
    if (want > r->length) {
        if (want > HEAP_TRACK) {
            host_fatal("rollback: the game heap passed %u MB",
                       HEAP_TRACK >> 20);
        }
        /* the new pages as they are now: their old contents for the
           frame that reached them */
        memcpy(r->mirror + r->length, r->start + r->length,
               want - r->length);
        r->length = want;
    }
}

const char* host_rb_start(void)
{
    void* heap;
    uint32_t top;

    if (running && opened_by == getpid()) {
        return NULL;
    }
    if (pagemap < 0 || opened_by != getpid()) {
        /* /proc/self is the process that opened it: a process restored
           from a snapshot (control.c) opens its own, and starts over */
        if (pagemap >= 0) {
            close(pagemap);
            close(clear);
        }
        pagemap = open("/proc/self/pagemap", O_RDONLY);
        clear = open("/proc/self/clear_refs", O_WRONLY);
        if (pagemap < 0 || clear < 0) {
            return "no /proc/self/pagemap or clear_refs";
        }
        opened_by = getpid();
    }
    host_game_heap_extent(&heap, &top);
    regions[LOW].start = (uint8_t*) 0x80000000u;
    regions[LOW].length = 0x4000;
    regions[ARENA].start = (uint8_t*) (uintptr_t) (HOST_ARENA_LO & ~0xFFFu);
    regions[ARENA].length = 0x81800000u - (HOST_ARENA_LO & ~0xFFFu);
    regions[STATICS].start = (uint8_t*) __game_state_start;
    regions[STATICS].length =
        (size_t) (__game_state_end - __game_state_start);
    regions[HEAP].start = heap;
    regions[HEAP].length = 0;
    for (int i = 0; i < NREGIONS; i++) {
        size_t cap = i == HEAP ? HEAP_TRACK : regions[i].length;
        if (regions[i].mirror == NULL) {
            regions[i].mirror = mirror_of(cap);
        }
        if (i != HEAP) {
            memcpy(regions[i].mirror, regions[i].start, regions[i].length);
        }
    }
    follow_heap();
    if (clear_marks() < 0) {
        return "clear_refs refused";
    }
    /* soft-dirty works: a page written now must show it */
    {
        volatile uint8_t* probe = regions[STATICS].start;
        uint64_t entry = 0;
        probe[0] = probe[0];
        if (pread(pagemap, &entry, 8,
                  (off_t) ((uintptr_t) probe / PAGE) * 8) != 8 ||
            !(entry & SOFT_DIRTY))
        {
            return "the kernel does not mark written pages "
                   "(CONFIG_MEM_SOFT_DIRTY)";
        }
        clear_marks();
    }
    newest = -1;
    kept = 0;
    memset(&stats, 0, sizeof stats);
    running = 1;
    return NULL;
}

void host_rb_stop(void)
{
    running = 0;
    kept = 0;
    newest = -1;
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
    for (int i = 0; i < NREGIONS; i++) {
        Region* r = &regions[i];
        size_t pages = r->length / PAGE;
        off_t first = (off_t) ((uintptr_t) r->start / PAGE);
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
    clear_marks(); /* the writes above are not a frame's */
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
