/**
 * @file
 * TM-CE legacy event Multishine (Custom Event Code - Rewrite.asm, lines
 * 134-273): shine as many times as possible in 10 seconds on Final
 * Destination; each frame-1 shine counts as a KO.
 */
#include "../legacy.h"

#include <melee/ft/types.h>
#include <melee/gm/gmvs.h>
#include <melee/gm/types.h>
#include <melee/if/ifstock.h>
#include <melee/mn/types.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/gobj.h>

/// gm/gmevent.c static (EventMatch_OnWinCondition).
void gm_801BC4F4(HSD_GObj* gobj);

#define STAGE_FINAL_DESTINATION 0x20
#define ASID_SHINE_GROUND_START 0x168
#define ASID_SHINE_AIR_START 0x16D

/// "Multishine THINK FUNCT".
static void MultishineThink(HSD_GObj* event)
{
    HSD_GObj* gobj[4];
    Fighter* fp[4];
    s32 state;

    tm_legacy_GetAllPlayerPointers(gobj, fp);

    if (tm_legacy_CheckIfFirstFrame()) {
        tm_legacy_PlacePlayersCenterStage(tm_legacy_StageGetGroundID_Main());
    }

    /* a grounded or aerial shine on its first frame scores */
    state = LG_S32(fp[0], LG_FT_STATE);
    if ((state == ASID_SHINE_GROUND_START || state == ASID_SHINE_AIR_START) &&
        LG_U16(fp[0], LG_FT_TM_STATE_FRAMES) == 0)
    {
        Player_UpdateKOsBySlot(0, false, 5);
    }

    /* time up */
    if (gm_8016AEEC() == 0 && gm_8016AEFC() == 59) {
        gm_801BC4F4(event);
    }

    ifStock_802FA2D0(Player_GetKOsByPlayerIndex(0, 5)); /* HUD score */
}

/// "Multishine LOAD FUNCT".
static void MultishineLoad(void)
{
    StartOSDs();
    tm_legacy_CreateEventThinkFunction(MultishineThink, 17, NULL, NULL);
    tm_legacy_InitializeHighScore();
}

/// "Multishine HIJACK INFO".
void tm_legacy_ev_Multishine(TmLegacySetup* s)
{
    u8* md = (u8*) s->md;

    LG_U8(md, 0x0) = 0x6;   /* count down */
    LG_U32(md, 0x10) = 10;  /* 10 seconds */
    LG_U8(md, 0x1) = 0x80;  /* READY, GO! */
    LG_U8(LG_EVENT_INFO, 0xB) &= ~0x02; /* score: KOs, not time */

    tm_legacy_InitializeMatch(s->event, s->md, -1, STAGE_FINAL_DESTINATION,
                              0, false);
    LG_U8(s->event, 0x1) = 0x20; /* 1 player */
    s->md->rules.on_match_start = MultishineLoad;
}
