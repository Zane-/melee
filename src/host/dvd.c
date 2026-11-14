/** @file
 * DVD: the disc is a directory of extracted files.
 *
 * Entry numbers index a table built once from the directory, names compared
 * without case as the disc's file system does. A read completes at once and
 * its callback is delivered as a completion. Each read is remembered, so the
 * archive loader can ask which file a buffer came from.
 */
#include "host.h"

#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/stat.h>

#include <dolphin/dvd.h>

typedef struct DiscFile {
    char* path; ///< relative to the disc's root, no leading slash
    char* host_path;
    uint32_t size;
    /// Bytes from the start that are 32-bit words, given to the game in
    /// the host's byte order (see words_until).
    uint32_t words;
    int words_known;
    /// A music stream (.hps): where its block headers are (see hps_heads).
    uint32_t* heads;
    int nheads;
} DiscFile;

static DiscFile* files;
static int nfiles, files_cap;

static int by_path(const void* a, const void* b)
{
    return strcasecmp(((const DiscFile*) a)->path,
                      ((const DiscFile*) b)->path);
}

static void scan(const char* root, const char* rel)
{
    char dir[1024];
    struct dirent* e;
    DIR* d;

    snprintf(dir, sizeof dir, "%s/%s", root, rel);
    d = opendir(dir);
    if (d == NULL) {
        return;
    }
    while ((e = readdir(d)) != NULL) {
        char sub[1024], full[2048];
        struct stat st;
        if (e->d_name[0] == '.') {
            continue;
        }
        snprintf(sub, sizeof sub, "%s%s%s", rel, rel[0] ? "/" : "",
                 e->d_name);
        snprintf(full, sizeof full, "%s/%s", root, sub);
        if (stat(full, &st) != 0) {
            continue;
        }
        if (S_ISDIR(st.st_mode)) {
            scan(root, sub);
        } else {
            if (nfiles == files_cap) {
                files_cap = files_cap ? files_cap * 2 : 1024;
                files = realloc(files, files_cap * sizeof *files);
            }
            files[nfiles].path = strdup(sub);
            files[nfiles].host_path = strdup(full);
            files[nfiles].size = (uint32_t) st.st_size;
            nfiles++;
        }
    }
    closedir(d);
}

void host_disc_init(const char* root)
{
    char dir[1024];
    snprintf(dir, sizeof dir, "%s/files", root);
    scan(dir, "");
    if (nfiles == 0) {
        host_fatal("no disc files under %s", dir);
    }
    /* Sorted, so entry numbers do not depend on directory order. */
    qsort(files, nfiles, sizeof *files, by_path);
}

void DVDInit(void) {}

s32 DVDConvertPathToEntrynum(const char* path)
{
    while (*path == '/') {
        path++;
    }
    for (int i = 0; i < nfiles; i++) {
        if (strcasecmp(files[i].path, path) == 0) {
            return i;
        }
    }
    return -1;
}

BOOL DVDFastOpen(s32 entrynum, DVDFileInfo* info)
{
    if (entrynum < 0 || entrynum >= nfiles) {
        return 0;
    }
    memset(info, 0, sizeof *info);
    info->startAddr = (u32) entrynum;
    info->length = files[entrynum].size;
    return 1;
}

BOOL DVDOpen(const char* name, DVDFileInfo* info)
{
    return DVDFastOpen(DVDConvertPathToEntrynum(name), info);
}

BOOL DVDClose(DVDFileInfo* info)
{
    (void) info;
    return 1;
}

BOOL DVDCheckDisk(void)
{
    return 1;
}

/// Every wait loop in the game spins on an idle function that asks for the
/// drive's status (lb_800192A8). Time passes here and completions are
/// delivered, so waits on alarms, reads and transfers end.
s32 DVDGetDriveStatus(void)
{
    host_advance(2000);
    host_deliver();
    return 0; /* DVD_STATE_END */
}

/* --- where buffers came from -------------------------------------------- */

#define MAX_ORIGINS 4096
static struct Origin {
    uintptr_t addr;
    uint32_t length;
    int file;
    uint32_t offset;
} origins[MAX_ORIGINS];
static int origin_next;

static void remember(void* addr, uint32_t length, int file, uint32_t offset)
{
    struct Origin* o = &origins[origin_next];
    origin_next = (origin_next + 1) % MAX_ORIGINS;
    o->addr = (uintptr_t) addr;
    o->length = length;
    o->file = file;
    o->offset = offset;
}

void host_origin_set(void* addr, uint32_t length, int file, uint32_t offset)
{
    remember(addr, length, file, offset);
}

int host_origin_find(const void* addr, uint32_t* offset)
{
    uintptr_t at = (uintptr_t) addr;
    for (int n = 1; n <= MAX_ORIGINS; n++) {
        const struct Origin* o =
            &origins[(origin_next - n + MAX_ORIGINS) % MAX_ORIGINS];
        if (o->length != 0 && at >= o->addr && at < o->addr + o->length) {
            if (offset != NULL) {
                *offset = o->offset + (uint32_t) (at - o->addr);
            }
            return o->file;
        }
    }
    return -1;
}

/// The path of disc file number `file` (as host_origin_find gives), or
/// NULL.
const char* host_file_path(int file)
{
    return file < 0 || file >= nfiles ? NULL : files[file].path;
}

const char* host_disc_origin(const void* addr, uint32_t* offset)
{
    int file = host_origin_find(addr, offset);
    return file < 0 ? NULL : files[file].path;
}

uint32_t host_origin_room(const void* addr)
{
    uintptr_t at = (uintptr_t) addr;
    for (int n = 1; n <= MAX_ORIGINS; n++) {
        const struct Origin* o =
            &origins[(origin_next - n + MAX_ORIGINS) % MAX_ORIGINS];
        if (o->length != 0 && at >= o->addr && at < o->addr + o->length) {
            return (uint32_t) (o->addr + o->length - at);
        }
    }
    return 0;
}

/* --- audio files ---------------------------------------------------------
 * Archives are converted to native data by the generated readers. The audio
 * files are not archives: the game reads them as arrays of 32-bit words.
 * Those words are swapped here, so the game's own audio code runs
 * unchanged. Nothing listens to the sound data itself, which stays as it
 * is on the disc.
 */

static uint32_t be32(const uint8_t* p)
{
    return (uint32_t) p[0] << 24 | (uint32_t) p[1] << 16 |
           (uint32_t) p[2] << 8 | p[3];
}

static uint32_t words_until(DiscFile* f)
{
    const char* dot = strrchr(f->path, '.');
    if (!f->words_known) {
        f->words_known = 1;
        f->words = 0;
        if (dot != NULL && strcasecmp(dot, ".sem") == 0) {
            /* Sound effect tables and command words: all of it. */
            f->words = f->size;
        } else if (dot != NULL && strcasecmp(dot, ".ssm") == 0) {
            /* A sound bank: four words (the first is the length of the
               sound headers), the headers, then sample data. */
            uint8_t head[4];
            FILE* fp = fopen(f->host_path, "rb");
            if (fp != NULL && fread(head, 1, 4, fp) == 4) {
                f->words = 0x10 + be32(head);
            }
            if (fp != NULL) {
                fclose(fp);
            }
        }
    }
    return f->words;
}

/* A music stream (.hps, read by the synth's stream player, synth.c): a
 * 0x80-byte header (rate, channels, each channel's AX address and ADPCM
 * settings, read as words) and a chain of blocks, each a 0x20-byte header
 * of words (its size, end address, the next block's offset, each channel's
 * loop context) and sample data, which goes to audio RAM as it is. The
 * headers' offsets come from following the chain once. */
#define HPS_HEADER 0x80u
#define HPS_BLOCK_HEADER 0x20u

static void hps_heads(DiscFile* f)
{
    FILE* fp;
    uint32_t at = HPS_HEADER;
    int cap = 0;

    if (f->heads != NULL || f->nheads < 0) {
        return;
    }
    f->nheads = -1;
    fp = fopen(f->host_path, "rb");
    if (fp == NULL) {
        return;
    }
    f->nheads = 0;
    while (at != 0xFFFFFFFFu && at + HPS_BLOCK_HEADER <= f->size) {
        uint8_t head[HPS_BLOCK_HEADER];
        int seen = 0;
        for (int i = 0; i < f->nheads; i++) {
            seen |= f->heads[i] == at;
        }
        if (seen || fseek(fp, (long) at, SEEK_SET) != 0 ||
            fread(head, 1, sizeof head, fp) != sizeof head)
        {
            break; /* the loop back to the looping block, or the end */
        }
        if (f->nheads == cap) {
            cap = cap != 0 ? cap * 2 : 64;
            f->heads = realloc(f->heads, (size_t) cap * sizeof *f->heads);
        }
        f->heads[f->nheads++] = at;
        at = be32(head + 8);
    }
    fclose(fp);
}

static void swap_words(uint8_t* buf, uint32_t offset, uint32_t length,
                       uint32_t from, uint32_t to)
{
    for (uint32_t at = from; at + 4 <= to; at += 4) {
        if (at >= offset && at + 4 <= offset + length) {
            uint32_t v = be32(buf + (at - offset));
            memcpy(buf + (at - offset), &v, 4);
        }
    }
}

static void to_host_words(DiscFile* f, uint8_t* buf, uint32_t offset,
                          uint32_t length)
{
    const char* dot = strrchr(f->path, '.');
    uint32_t until;

    if (dot != NULL && strcasecmp(dot, ".hps") == 0) {
        hps_heads(f);
        swap_words(buf, offset, length, 0, HPS_HEADER);
        for (int i = 0; i < f->nheads; i++) {
            uint32_t h = f->heads[i];
            if (h < offset + length && h + HPS_BLOCK_HEADER > offset) {
                swap_words(buf, offset, length, h, h + HPS_BLOCK_HEADER);
            }
        }
        return;
    }
    until = words_until(f);
    for (uint32_t at = 0; at + 4 <= length && offset + at + 4 <= until;
         at += 4)
    {
        uint32_t v = be32(buf + at);
        memcpy(buf + at, &v, 4);
    }
}

static void read_done(intptr_t length, intptr_t info)
{
    DVDFileInfo* fi = (DVDFileInfo*) info;
    fi->callback((s32) length, fi);
}

BOOL DVDReadAsyncPrio(DVDFileInfo* info, void* addr, s32 length, s32 offset,
                      DVDCallback callback, s32 prio)
{
    DiscFile* f = &files[info->startAddr];
    FILE* fp = fopen(f->host_path, "rb");
    size_t got = 0;

    (void) prio;
    if (fp == NULL) {
        host_fatal("cannot open %s", f->host_path);
    }
    if (fseek(fp, offset, SEEK_SET) == 0) {
        got = fread(addr, 1, (size_t) length, fp);
    }
    fclose(fp);
    if (got < (size_t) length) {
        /* Reads are rounded up to 32 bytes past the end of the file. */
        memset((char*) addr + got, 0, (size_t) length - got);
    }
    to_host_words(f, addr, (uint32_t) offset, (uint32_t) got);
    remember(addr, (uint32_t) length, (int) info->startAddr,
             (uint32_t) offset);
    info->cb.state = 0; /* DVD_STATE_END */
    info->cb.transferredSize = (u32) length;
    info->callback = callback;
    if (callback != NULL) {
        host_post(read_done, length, (intptr_t) info);
    }
    return 1;
}
