/*
 * The parts of m-ex's runtime that TM-CE's C code calls, reimplemented for
 * the native build. Compiled with the TM-CE units (MexTK headers), not with
 * the decomp headers.
 *
 * m-ex lives in TM-CE's modified Start.dol at 0x803D7000+, on top of vanilla
 * data. The native build keeps the vanilla image intact, so these are plain
 * overlay functions instead.
 */
#include "events.h"
#include <stddef.h>
#include "tmce_registry.h"

/* events.h (patch 0001) points event_vars here instead of at 0x803D7054. */
EventVars* tmce_event_vars;

/* m-ex calloc (0x803D706C): HSD_MemAlloc, zeroed. */
void* calloc(int size)
{
    void* p = HSD_MemAlloc(size);
    memset(p, 0, size);
    return p;
}

/* Not in vanilla; MexTK's __FILENAME__ uses it. */
char* strrchr(const char* s, int c)
{
    const char* last = NULL;
    for (;; s++) {
        if (*s == (char) c) {
            last = s;
        }
        if (*s == '\0') {
            return (char*) last;
        }
    }
}

static const TmceModule* findModule(const char* name, int len,
                                    const char* table)
{
    int i;
    for (i = 0; i < tmce_module_count; i++) {
        const TmceModule* m = &tmce_modules[i];
        if (strncmp(m->name, name, len) == 0 && m->name[len] == '\0' &&
            strcmp(m->table, table) == 0)
        {
            return m;
        }
    }
    return NULL;
}

/*
 * m-ex MEX_LoadRelArchive (0x803D7080): load file, relocate the code in it
 * and copy the exported function table named `symbol` into `functions`.
 *
 * Here the code is already linked in. `file` is "TM/<unit>.dat": the table
 * comes from tmce_modules, and the file on disc (if any) holds only the
 * unit's art, which is loaded as a normal archive.
 */
HSD_Archive* MEX_LoadRelArchive(char* file, void* functions, char* symbol)
{
    const char* name = file;
    const TmceModule* m;
    int len = 0;

    if (strncmp(name, "TM/", 3) == 0) {
        name += 3;
    }
    while (name[len] != '\0' && name[len] != '.') {
        len++;
    }

    m = findModule(name, len, symbol);
    if (m != NULL) {
        memcpy(functions, (void*) m->funcs, m->count * sizeof(void*));
    } else {
        OSReport("tmce: no linked unit for %s (%s)\n", file, symbol);
    }

    if (DVDConvertPathToEntrynum(file) == -1) {
        return NULL;
    }
    return Archive_LoadFile(file);
}

/* m-ex blr2 (0x803230A4, a bare `blr`): an opaque call TM-CE puts in busy
 * loops so the compiler keeps re-reading memory. */
void blr2(void) {}

/* m-ex MEX_RelocRelArchive (0x803D7074). Only referenced by MEX_InitRELDAT in
 * MexTK's mex.h, which TM-CE never calls: units are linked in, nothing is
 * relocated at runtime. */
void MEX_RelocRelArchive(void* xFunction)
{
    OSReport("tmce: MEX_RelocRelArchive(%p) called; not supported\n",
             xFunction);
}
