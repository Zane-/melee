/** @file
 * The game's whole state, saved and brought back inside the process: what
 * rollback netcode needs every frame.
 *
 * Three regions hold it all:
 *  - the arena, at the console's addresses (the game's heaps);
 *  - the game's statics, gathered by the linker into one section
 *    (tools/native_build.py, game_state_script: the game's library, the
 *    readers, and the host files whose state is the game's timeline);
 *  - the game heap, where archive data is converted (gameheap.c), up to
 *    its top.
 * Audio RAM is not copied: it is written when sound banks and archives are
 * loaded, not while a match plays.
 *
 * A save and a load are made at the same place, the frame boundary (the
 * control protocol's commands run there), so the call stack above them is
 * the same and holds nothing that differs between frames (gmscene.c's
 * scene loop keeps its state in statics).
 */
#include "host.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern char __game_state_start[], __game_state_end[];
void host_game_heap_extent(void** start, uint32_t* length);

#define SLOTS 32

typedef struct Snapshot {
    uint8_t* data;
    size_t capacity;
    uint32_t heap_length;
    uint32_t frame;
    int valid;
} Snapshot;

static Snapshot slots[SLOTS];

#define ARENA ((uint8_t*) (uintptr_t) HOST_ARENA_LO)
#define ARENA_SIZE ((size_t) (HOST_ARENA_HI - HOST_ARENA_LO))
#define STATICS ((uint8_t*) __game_state_start)
#define STATICS_SIZE ((size_t) (__game_state_end - __game_state_start))

/// Bytes a snapshot takes now.
size_t host_state_size(void)
{
    void* heap;
    uint32_t heap_length;
    host_game_heap_extent(&heap, &heap_length);
    return ARENA_SIZE + STATICS_SIZE + heap_length;
}

/// The regions' sizes, for reports.
void host_state_sizes(size_t* arena, size_t* statics, size_t* heap)
{
    void* base;
    uint32_t length;
    host_game_heap_extent(&base, &length);
    *arena = ARENA_SIZE;
    *statics = STATICS_SIZE;
    *heap = length;
}

int host_state_save(int slot)
{
    Snapshot* s;
    void* heap;
    uint32_t heap_length;
    size_t need;
    uint8_t* at;

    if (slot < 0 || slot >= SLOTS) {
        return -1;
    }
    s = &slots[slot];
    host_game_heap_extent(&heap, &heap_length);
    need = ARENA_SIZE + STATICS_SIZE + heap_length;
    if (s->capacity < need) {
        /* room to grow, so a slot is not reallocated every frame */
        size_t capacity = need + need / 4;
        uint8_t* data = realloc(s->data, capacity);
        if (data == NULL) {
            host_fatal("no memory for a %zu-byte snapshot", capacity);
        }
        s->data = data;
        s->capacity = capacity;
    }
    at = s->data;
    memcpy(at, ARENA, ARENA_SIZE);
    at += ARENA_SIZE;
    /* the statics include this file's caller's notion of nothing: the
       snapshot table lives outside them (state.o is not gathered) */
    memcpy(at, STATICS, STATICS_SIZE);
    at += STATICS_SIZE;
    memcpy(at, heap, heap_length);
    s->heap_length = heap_length;
    s->frame = host.frame;
    s->valid = 1;
    return 0;
}

int host_state_load(int slot)
{
    Snapshot* s;
    void* heap;
    uint32_t heap_length;
    const uint8_t* at;
    int draw;

    if (slot < 0 || slot >= SLOTS || !slots[slot].valid) {
        return -1;
    }
    s = &slots[slot];
    host_game_heap_extent(&heap, &heap_length);
    draw = host.draw;
    at = s->data;
    memcpy(ARENA, at, ARENA_SIZE);
    at += ARENA_SIZE;
    memcpy(STATICS, at, STATICS_SIZE);
    at += STATICS_SIZE;
    /* the heap's own bookkeeping (its top) comes back with it; what lies
       past that top is free */
    memcpy(heap, at, s->heap_length);
    /* Whether the draw pass runs is the host's (a quiet stretch turns it
       off, control.c), not the game's: `host` is among the statics, and a
       state saved while drawing, loaded in a stretch that does not draw,
       had the game drawing again with no frame of Aurora's begun. Its
       commands piled up until the next frame took them all at once, past
       Aurora's 24 MB of uniforms a frame: an abort (the owner's replay in
       the coach, 2026-11-14). */
    host.draw = draw;
    return 0;
}

/// The whole state into a file: the arena, the statics, the heap, each
/// preceded by its address and length (tests: compare two processes).
int host_state_dump(const char* path)
{
    void* heap;
    uint32_t heap_length;
    FILE* f = fopen(path, "wb");
    const void* starts[3];
    size_t lengths[3];
    if (f == NULL) {
        return -1;
    }
    host_game_heap_extent(&heap, &heap_length);
    starts[0] = ARENA;
    lengths[0] = ARENA_SIZE;
    starts[1] = STATICS;
    lengths[1] = STATICS_SIZE;
    starts[2] = heap;
    lengths[2] = heap_length;
    for (int r = 0; r < 3; r++) {
        uint32_t head[2] = { (uint32_t) (uintptr_t) starts[r],
                             (uint32_t) lengths[r] };
        fwrite(head, sizeof head, 1, f);
        fwrite(starts[r], 1, lengths[r], f);
    }
    fclose(f);
    return 0;
}

/// The frame a slot was saved at, or -1.
long host_state_frame(int slot)
{
    if (slot < 0 || slot >= SLOTS || !slots[slot].valid) {
        return -1;
    }
    return (long) slots[slot].frame;
}

static uint64_t mix(uint64_t h, const uint8_t* p, size_t n)
{
    size_t i = 0;
    for (; i + 8 <= n; i += 8) {
        uint64_t w;
        memcpy(&w, p + i, 8);
        h = (h ^ w) * 0x100000001B3ull;
        h ^= h >> 29;
    }
    for (; i < n; i++) {
        h = (h ^ p[i]) * 0x100000001B3ull;
    }
    return h;
}

/// A hash of the whole state (tests: is it the same after a load?).
uint64_t host_state_hash(void)
{
    void* heap;
    uint32_t heap_length;
    uint64_t h = 0xCBF29CE484222325ull;
    host_game_heap_extent(&heap, &heap_length);
    h = mix(h, ARENA, ARENA_SIZE);
    h = mix(h, STATICS, STATICS_SIZE);
    h = mix(h, heap, heap_length);
    return h;
}

/// Where two states differ first, for finding what a load misses: the
/// region (0 arena, 1 statics, 2 heap) and offset of the first byte of the
/// live state unlike the slot's, or -1 if none.
long host_state_diff(int slot, int* region)
{
    Snapshot* s;
    void* heap;
    uint32_t heap_length;
    const uint8_t* at;
    const uint8_t* live[3];
    size_t len[3];

    if (slot < 0 || slot >= SLOTS || !slots[slot].valid) {
        return -2;
    }
    s = &slots[slot];
    host_game_heap_extent(&heap, &heap_length);
    live[0] = ARENA;
    len[0] = ARENA_SIZE;
    live[1] = STATICS;
    len[1] = STATICS_SIZE;
    live[2] = heap;
    len[2] = heap_length < s->heap_length ? heap_length : s->heap_length;
    at = s->data;
    for (int r = 0; r < 3; r++) {
        for (size_t i = 0; i < len[r]; i++) {
            if (live[r][i] != at[i]) {
                *region = r;
                return (long) i;
            }
        }
        at += r == 0 ? ARENA_SIZE : r == 1 ? STATICS_SIZE : 0;
    }
    if (heap_length != s->heap_length) {
        *region = 2;
        return (long) len[2];
    }
    return -1;
}

/// The address a region offset is at (for naming it with nm).
uintptr_t host_state_address(int region, long offset)
{
    void* heap;
    uint32_t heap_length;
    host_game_heap_extent(&heap, &heap_length);
    return (uintptr_t) (region == 0 ? ARENA : region == 1 ? STATICS
                                                         : (uint8_t*) heap) +
           (uintptr_t) offset;
}
