/*
 * Save-data fields used by the OSD toggle menu (src/melee/tm/osdmenu/),
 * reached through MexTK's names. Compiled with the TM-CE units.
 */
#include "events.h"

/* MemcardData+0x1F24: one bit per OSD id, set = shown. */
u32* tmce_osdmenu_Enabled(void)
{
    return &stc_memcard->TM_OSDEnabled;
}

/* MemcardData+0x1F28: 0 HUD, 1 Sides, 2 Top Left, 3 Top Right. */
u8* tmce_osdmenu_Position(void)
{
    return &stc_memcard->TM_OSDPosition;
}
