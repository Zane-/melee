/*
 * TM-CE entry points for the native hooks (src/melee/tm/tm.c), and the
 * bridge functions declared in src/melee/tm/tmce.h. Compiled with the TM-CE
 * units (MexTK headers).
 */
#include "events.h"
#include <stddef.h>

/* events.c */
void OnFileLoad(HSD_Archive* archive);

#define TMCE_MENU_FILE "TM/eventMenu.dat"
/* TM-CE's dats/eventMenu.dat is 16.8 KB. */
#define TMCE_MENU_MAX 0x8000
/* TM-CE allocates 68 bytes for the archive header. */
#define TMCE_ARCHIVE_SIZE 0x44

static u8 menu_file[TMCE_MENU_MAX] __attribute__((aligned(32)));
static u32 menu_archive[TMCE_ARCHIVE_SIZE / 4];

/*
 * Port of Misc/Load eventMenu.dat.asm (HSD_OSInit+0xAC). TM-CE carves a heap
 * for the file out of the arena while HSD sets up its heaps, because the
 * file also holds TM-CE's core code. Here the code is linked in and the file
 * is only art, so it goes into a static buffer, loaded once the disc is up.
 */
void tmce_Boot(void)
{
    char* file = TMCE_MENU_FILE;
    int size;

    if (DVDConvertPathToEntrynum(file) == -1) {
        OSReport("tmce: %s is missing from the disc\n", file);
        return;
    }
    size = File_GetSize(file);
    if (size > TMCE_MENU_MAX) {
        OSReport("tmce: %s is %d bytes, buffer is %d\n", file, size,
                 TMCE_MENU_MAX);
        return;
    }
    Archive_LoadSync(file, menu_file, &size);
    Archive_Init((HSD_Archive*) menu_archive, menu_file, size);
    OnFileLoad((HSD_Archive*) menu_archive);
}

/* True once tmce_Boot has run OnFileLoad. */
int tmce_IsLoaded(void)
{
    return event_vars != NULL;
}

/* The selected event page (TM-CE keeps it in the save data, 0x1F29). */
int tmce_GetEventPage(void)
{
    return stc_memcard->TM_EventPage;
}

/* sizeof(FighterData) in MexTK terms: vanilla's 0x23EC plus m-ex's 0xC and
 * TM-CE's 0x138 (FighterData.TM). Used by src/melee/tm/tm_fighter.c. */
int tmce_FighterDataSize(void)
{
    return sizeof(FighterData);
}

/* EventDesc.rotation (patch 0005) of an event, or NULL. */
const void* tmce_GetEventRotation(int page, int event)
{
    EventDesc* desc = GetEventDesc(page, event);
    return desc != NULL ? desc->rotation : NULL;
}
