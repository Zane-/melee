/** @file
 * The game's archive loader on the generated readers.
 *
 * Upstream's adapter (tools/dat-cli/native/src/hsd.c) converts an archive's
 * data to native objects only for symbols the game looks up with a type
 * (HSD_ArchiveGetPublicAs). Most of the game loads symbols without one
 * (lbArchive_LoadSymbols and friends, through HSD_ArchiveGetPublicAddress)
 * and would get the file's big-endian bytes. This version gives those the
 * type the schema records for the symbol's name, so every lookup returns
 * converted data. It replaces that adapter in the link.
 */
#include "host.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "melee_dat.h"

#include <dat/reader-internal.h>
#include <sysdolphin/baselib/archive.h>

static uint32_t be32(const u8* p)
{
    return (uint32_t) p[0] << 24 | (uint32_t) p[1] << 16 |
           (uint32_t) p[2] << 8 | p[3];
}

/* --- symbol name -> the schema's roots of that name ---------------------- */

typedef struct NameEntry {
    const char* name;
    const DatRoot* root;
    const DatFileRoots* file;
    struct NameEntry* next; ///< another root of the same name
} NameEntry;

static NameEntry** name_table;
static uint32_t name_mask;

static uint32_t hash(const char* s)
{
    uint32_t h = 2166136261u;
    while (*s) {
        h = (h ^ (uint8_t) *s++) * 16777619u;
    }
    return h;
}

static void build_names(void)
{
    uint32_t count = 0, size = 1024;
    const DatSchema* s = &melee_dat_schema;

    for (uint32_t i = 0; i < s->nmodules; i++) {
        for (uint32_t j = 0; j < s->modules[i].nfiles; j++) {
            count += s->modules[i].files[j].nroots;
        }
    }
    while (size < count * 2) {
        size *= 2;
    }
    name_mask = size - 1;
    name_table = calloc(size, sizeof *name_table);
    for (uint32_t i = 0; i < s->nmodules; i++) {
        for (uint32_t j = 0; j < s->modules[i].nfiles; j++) {
            const DatFileRoots* f = &s->modules[i].files[j];
            for (uint32_t k = 0; k < f->nroots; k++) {
                NameEntry* e;
                uint32_t at;
                if (f->roots[k].alias) {
                    continue;
                }
                e = malloc(sizeof *e);
                e->name = f->roots[k].name;
                e->root = &f->roots[k];
                e->file = f;
                e->next = NULL;
                at = hash(e->name) & name_mask;
                while (name_table[at] != NULL &&
                       strcmp(name_table[at]->name, e->name) != 0)
                {
                    at = (at + 1) & name_mask;
                }
                e->next = name_table[at];
                name_table[at] = e;
            }
        }
    }
}

static const NameEntry* find_name(const char* name)
{
    uint32_t at;
    if (name_table == NULL) {
        build_names();
    }
    at = hash(name) & name_mask;
    while (name_table[at] != NULL) {
        if (strcmp(name_table[at]->name, name) == 0) {
            return name_table[at];
        }
        at = (at + 1) & name_mask;
    }
    return NULL;
}

/* --- which file each open archive came from ------------------------------ */

#define MAX_OPEN 512
static struct {
    const DatArchive* native;
    char file[64];
} open_archives[MAX_OPEN];

static const char* base_name(const char* path)
{
    const char* slash = strrchr(path, '/');
    return slash ? slash + 1 : path;
}

static void note_open(const DatArchive* native, const void* src)
{
    const char* path = host_disc_origin(src, NULL);
    for (int i = 0; i < MAX_OPEN; i++) {
        if (open_archives[i].native == NULL) {
            open_archives[i].native = native;
            snprintf(open_archives[i].file, sizeof open_archives[i].file,
                     "%s", path ? base_name(path) : "");
            return;
        }
    }
}

static const char* file_of(const DatArchive* native)
{
    for (int i = 0; i < MAX_OPEN; i++) {
        if (open_archives[i].native == native) {
            return open_archives[i].file;
        }
    }
    return "";
}

static void note_close(const DatArchive* native)
{
    for (int i = 0; i < MAX_OPEN; i++) {
        if (open_archives[i].native == native) {
            open_archives[i].native = NULL;
        }
    }
}

/* --- the loader ----------------------------------------------------------- */

s32 HSD_ArchiveParse(HSD_Archive* archive, u8* src, size_t size)
{
    const char* error = NULL;
    DatArchive* native;
    DatArchiveData* raw;

    if (archive == NULL) {
        return -1;
    }
    memset(archive, 0, sizeof(*archive));
    native = dat_open(&melee_dat_schema, src, size, &error);
    if (native == NULL) {
        host_log("archive from %s does not parse: %s",
                 host_disc_origin(src, NULL), error ? error : "?");
        return -1;
    }
    note_open(native, src);
    raw = native->archive;
    archive->native_data = native;
    archive->header.file_size = be32(src);
    archive->header.data_size = raw->size;
    archive->header.nb_reloc = raw->nrelocs;
    archive->header.nb_public = raw->npublics;
    archive->header.nb_extern = raw->nexterns;
    memcpy(archive->header.version, src + 0x14, 4);
    archive->header.pad[0] = be32(src + 0x18);
    archive->header.pad[1] = be32(src + 0x1C);
    /* The game frees its input allocation through this address. */
    archive->data = src + sizeof(HSD_ArchiveHeader);
    archive->top_ptr = src;
    archive->flags = HSD_ARCHIVE_DONT_FREE;
    archive->symbols = (char*) raw->names;
    archive->reloc_info = calloc(raw->nrelocs, sizeof(*archive->reloc_info));
    archive->public_info =
        calloc(raw->npublics, sizeof(*archive->public_info));
    archive->extern_info =
        calloc(raw->nexterns, sizeof(*archive->extern_info));
    for (uint32_t i = 0; i < raw->nrelocs; i++) {
        archive->reloc_info[i].offset = raw->relocs[i];
    }
    for (uint32_t i = 0; i < raw->npublics; i++) {
        archive->public_info[i].offset = raw->publics[i].offset;
        archive->public_info[i].symbol = raw->publics[i].name - raw->names;
    }
    for (uint32_t i = 0; i < raw->nexterns; i++) {
        archive->extern_info[i].offset = raw->externs[i].offset;
        archive->extern_info[i].symbol = raw->externs[i].name - raw->names;
    }
    return 0;
}

void HSD_ArchiveReleaseNative(HSD_Archive* archive)
{
    if (archive == NULL || archive->native_data == NULL) {
        return;
    }
    note_close(archive->native_data);
    dat_close(archive->native_data);
    archive->native_data = NULL;
    archive->top_ptr = NULL;
    free(archive->reloc_info);
    free(archive->public_info);
    free(archive->extern_info);
    archive->reloc_info = NULL;
    archive->public_info = NULL;
    archive->extern_info = NULL;
    archive->symbols = NULL;
}

/// The type the schema gives the symbol `name`: the root of that name in
/// the archive's own file if there is one, else the type every root of that
/// name shares.
static int32_t type_by_name(const DatArchive* native, const char* name)
{
    const NameEntry* first = find_name(name);
    const char* file = file_of(native);
    int32_t type = DAT_NONE;

    for (const NameEntry* e = first; e != NULL; e = e->next) {
        if (file[0] != '\0' && strcmp(e->file->file, file) == 0) {
            return e->root->type;
        }
    }
    for (const NameEntry* e = first; e != NULL; e = e->next) {
        int32_t t = dat_reader_resolve(native, e->root->type);
        if (type == DAT_NONE) {
            type = t;
        } else if (type != t) {
            return DAT_NONE; /* the name means different things */
        }
    }
    return type;
}

void* HSD_ArchiveGetPublicAddress(HSD_Archive* archive, const char* name)
{
    static int warned;
    const DatArchiveData* raw;
    const DatSymbol* symbol;
    int32_t type;

    if (archive == NULL || archive->native_data == NULL) {
        return NULL;
    }
    raw = archive->native_data->archive;
    symbol = dat_archive_public(raw, name);
    if (symbol == NULL) {
        return NULL;
    }
    type = type_by_name(archive->native_data, name);
    if (type != DAT_NONE) {
        void* native = dat_public(archive->native_data, name, type);
        if (native != NULL) {
            return native;
        }
    }
    if (warned < 40) {
        warned++;
        host_log("no type for symbol %s of %s: left as raw bytes", name,
                 file_of(archive->native_data));
    }
    return raw->data + symbol->offset;
}

void* HSD_ArchiveGetPublicTyped(HSD_Archive* archive, const char* name,
                                const char* type)
{
    int32_t index;
    if (archive == NULL || archive->native_data == NULL) {
        return NULL;
    }
    index = melee_dat_type(type);
    return index == DAT_NONE ? NULL
                             : dat_public(archive->native_data, name, index);
}

char* HSD_ArchiveGetExtern(HSD_Archive* archive, int index)
{
    const DatArchiveData* raw;
    if (archive == NULL || archive->native_data == NULL) {
        return NULL;
    }
    raw = archive->native_data->archive;
    return index < 0 || (uint32_t) index >= raw->nexterns
               ? NULL
               : (char*) raw->externs[index].name;
}

void HSD_ArchiveLocateExtern(HSD_Archive* archive, const char* name,
                             void* address)
{
    if (archive != NULL && archive->native_data != NULL) {
        dat_link_extern(archive->native_data, name, address);
    }
}

/* --- the file's own layout ------------------------------------------------
 * The readers give every object its own place. Where the game steps from
 * one object to "the nth after it" (animation joints of a stage model are
 * indexed that way), the neighbour is found through the archive: where the
 * object is in the file, n console-sized elements on, and the native object
 * for that place.
 */
void* host_dat_element(void* native, int n, uint32_t console_size)
{
    if (native == NULL || n == 0) {
        return native;
    }
    for (int i = 0; i < MAX_OPEN; i++) {
        const DatArchive* a = open_archives[i].native;
        if (a == NULL) {
            continue;
        }
        for (size_t k = 0; k < a->natives.cap; k++) {
            uint64_t key = a->natives.keys[k];
            uint64_t there;
            if (key == UINT64_MAX ||
                a->natives.values[k] != (uintptr_t) native)
            {
                continue;
            }
            if (map_get(&a->natives,
                        key2((uint32_t) (key >> 32) + n * console_size,
                             (uint32_t) key),
                        &there))
            {
                return (void*) (uintptr_t) there;
            }
            host_fatal("element %d after offset %x of %s was never read", n,
                       (uint32_t) (key >> 32), open_archives[i].file);
        }
    }
    host_fatal("host_dat_element: %p is not an archive object", native);
}

/// The script a goto or subroutine command jumps to. In the archive's data
/// the command's second word is still an offset into that data (the
/// readers leave scripts as they are on the disc); `word` is its address.
/// A script that is not from an archive holds a pointer already.
void* host_script_target(const void* word)
{
    const uint8_t* at = word;
    for (int i = 0; i < MAX_OPEN; i++) {
        const DatArchive* a = open_archives[i].native;
        if (a != NULL && at >= a->archive->data &&
            at < a->archive->data + a->archive->size)
        {
            return a->archive->data + be32(at);
        }
    }
    return *(void* const*) word;
}
