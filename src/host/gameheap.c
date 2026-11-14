/** @file
 * The game's own heap: what the host converts and allocates on the game's
 * behalf (archive data, the readers' objects) comes from one region of
 * memory whose bookkeeping is inside it.
 *
 * Rollback netcode saves the game's whole state every frame and brings an
 * old one back (state.c). The game's arena and statics are fixed regions;
 * converted archive data was allocated object by object from the C
 * library's heap, which a snapshot cannot cover: after a rollback the game
 * would point at animation data the abandoned frames had freed. Here every
 * such allocation is in one region, and the allocator's state (its free
 * lists, its top) is in that region's first bytes, so copying the region
 * up to its top is a complete snapshot of it.
 *
 * Code that allocates for the game is compiled with gameheap.h forced in
 * (tools/native_build.py: the game's library, the readers, archive.c), which
 * renames malloc, calloc, realloc and free to the functions here.
 *
 * The allocator: blocks with a header and a footer (sizes, an in-use bit),
 * free blocks in 128 size classes, first fit within a class, split and
 * coalesced; a free block at the top lowers the top, so the snapshot
 * stays as small as what is in use.
 */
#include "host.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>

#define RESERVE (512u << 20) /* address space; pages are used as needed */
#define ALIGN 16u
#define HEADER 8u /* size|used, and the previous block's size */
#define MIN_BLOCK 32u
#define NBINS 128
#define MAGIC 0x47484150u /* "GHAP" */

typedef struct Block {
    uint32_t prev_size; ///< the block before this one (0 at the start)
    uint32_t size;      ///< this block, header included; bit 0: in use
    struct Block* next; ///< free blocks only: the class's list
    struct Block* prev;
} Block;

typedef struct Heap {
    uint32_t magic;
    uint32_t top;   ///< offset of the first byte never handed out
    uint32_t used;  ///< bytes in blocks in use
    uint32_t peak;  ///< the highest top so far
    uint32_t last;  ///< the size of the block that ends at the top (0: none)
    Block* bins[NBINS];
} Heap;

static uint8_t* base;

#define FIRST ((uint32_t) ((sizeof(Heap) + ALIGN - 1) & ~(ALIGN - 1)))

static Heap* heap(void)
{
    if (base == NULL) {
        base = mmap(NULL, RESERVE, PROT_READ | PROT_WRITE,
                    MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0);
        if (base == MAP_FAILED) {
            base = NULL;
            host_fatal("game heap: no address space for %u MB",
                       RESERVE >> 20);
        }
        Heap* h = (Heap*) base;
        h->magic = MAGIC;
        h->top = FIRST;
    }
    return (Heap*) base;
}

static uint32_t size_of(const Block* b)
{
    return b->size & ~1u;
}

static int in_use(const Block* b)
{
    return b->size & 1u;
}

static Block* at(uint32_t offset)
{
    return (Block*) (base + offset);
}

static uint32_t offset_of(const Block* b)
{
    return (uint32_t) ((const uint8_t*) b - base);
}

static int bin_of(uint32_t size)
{
    /* four classes per power of two */
    int log = 31 - __builtin_clz(size);
    int sub = log >= 2 ? (int) ((size >> (log - 2)) & 3u) : 0;
    int bin = (log - 4) * 4 + sub;
    return bin < 0 ? 0 : bin >= NBINS ? NBINS - 1 : bin;
}

static void unlink_free(Heap* h, Block* b)
{
    if (b->prev != NULL) {
        b->prev->next = b->next;
    } else {
        h->bins[bin_of(size_of(b))] = b->next;
    }
    if (b->next != NULL) {
        b->next->prev = b->prev;
    }
}

static void link_free(Heap* h, Block* b)
{
    int bin = bin_of(size_of(b));
    b->prev = NULL;
    b->next = h->bins[bin];
    if (b->next != NULL) {
        b->next->prev = b;
    }
    h->bins[bin] = b;
}

/// The block after `b`, or NULL at the top.
static Block* after(Heap* h, Block* b)
{
    uint32_t next = offset_of(b) + size_of(b);
    return next < h->top ? at(next) : NULL;
}

static void set_size(Heap* h, Block* b, uint32_t size, int used)
{
    Block* next;
    b->size = size | (used ? 1u : 0u);
    next = after(h, b);
    if (next != NULL) {
        next->prev_size = size;
    }
}

int host_game_heap_owns(const void* p)
{
    return base != NULL && (const uint8_t*) p >= base &&
           (const uint8_t*) p < base + RESERVE;
}

void* game_malloc(size_t n)
{
    Heap* h = heap();
    uint32_t size;
    Block* b = NULL;

    if (n > RESERVE / 2) {
        return NULL;
    }
    size = (uint32_t) ((n + HEADER + ALIGN - 1) & ~(size_t) (ALIGN - 1));
    if (size < MIN_BLOCK) {
        size = MIN_BLOCK;
    }
    for (int bin = bin_of(size); bin < NBINS && b == NULL; bin++) {
        for (Block* c = h->bins[bin]; c != NULL; c = c->next) {
            if (size_of(c) >= size) {
                b = c;
                break;
            }
        }
    }
    if (b != NULL) {
        uint32_t have = size_of(b);
        unlink_free(h, b);
        if (have - size >= MIN_BLOCK) {
            Block* rest = (Block*) ((uint8_t*) b + size);
            set_size(h, b, size, 1);
            rest->prev_size = size;
            set_size(h, rest, have - size, 0);
            link_free(h, rest);
        } else {
            set_size(h, b, have, 1);
        }
    } else {
        if (h->top + size > RESERVE) {
            host_fatal("game heap full: %u bytes asked for, %u in use", size,
                       h->used);
        }
        b = at(h->top);
        b->prev_size = h->last;
        b->size = size | 1u;
        h->last = size;
        h->top += size;
        if (h->top > h->peak) {
            h->peak = h->top;
        }
    }
    h->used += size_of(b);
    return (uint8_t*) b + HEADER;
}

void game_free(void* p)
{
    Heap* h;
    Block* b;
    uint32_t size;

    if (p == NULL) {
        return;
    }
    if (!host_game_heap_owns(p)) {
        free(p); /* the C library's (allocated before any of this) */
        return;
    }
    h = heap();
    b = (Block*) ((uint8_t*) p - HEADER);
    if (!in_use(b)) {
        host_fatal("game heap: %p freed twice", p);
    }
    size = size_of(b);
    h->used -= size;
    /* merge with the next block if it is free */
    Block* next = after(h, b);
    if (next != NULL && !in_use(next)) {
        unlink_free(h, next);
        size += size_of(next);
    }
    /* and with the previous one */
    if (offset_of(b) > FIRST && b->prev_size != 0) {
        Block* prev = (Block*) ((uint8_t*) b - b->prev_size);
        if (offset_of(prev) >= FIRST && !in_use(prev) &&
            size_of(prev) == b->prev_size)
        {
            unlink_free(h, prev);
            size += size_of(prev);
            b = prev;
        }
    }
    if (offset_of(b) + size == h->top) {
        /* the top comes down; the block before is in use (a free one
           would have merged) and is the last now */
        h->top = offset_of(b);
        h->last = b->prev_size;
        return;
    }
    set_size(h, b, size, 0);
    link_free(h, b);
}

void* game_calloc(size_t count, size_t each)
{
    void* p;
    if (each != 0 && count > (RESERVE / 2) / each) {
        return NULL;
    }
    p = game_malloc(count * each);
    if (p != NULL) {
        memset(p, 0, count * each);
    }
    return p;
}

void* game_realloc(void* p, size_t n)
{
    Block* b;
    size_t have;
    void* q;

    if (p == NULL) {
        return game_malloc(n);
    }
    if (n == 0) {
        game_free(p);
        return NULL;
    }
    if (!host_game_heap_owns(p)) {
        return realloc(p, n);
    }
    b = (Block*) ((uint8_t*) p - HEADER);
    have = size_of(b) - HEADER;
    if (n <= have) {
        return p;
    }
    q = game_malloc(n);
    if (q != NULL) {
        memcpy(q, p, have);
        game_free(p);
    }
    return q;
}

/// The region a snapshot copies: its start and how far it is in use.
void host_game_heap_extent(void** start, uint32_t* length)
{
    Heap* h = heap();
    *start = base;
    *length = h->top;
}

/// Bytes in use and the highest the top has been.
void host_game_heap_stats(uint32_t* used, uint32_t* top, uint32_t* peak)
{
    Heap* h = heap();
    *used = h->used;
    *top = h->top;
    *peak = h->peak;
}
