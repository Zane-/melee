/**
 * @file
 * TM-CE legacy event Reaction (Custom Event Code - Rewrite.asm, lines
 * 275-536): a CPU Fox shines after a random 3-7 seconds; press anything as
 * soon as it does. The reaction time is shown in frames.
 */
#include "../legacy.h"

#include <melee/ft/fighter.h>
#include <melee/ft/ftcoll.h>
#include <melee/ft/types.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/mn/types.h>
#include <melee/tm/osdcore/osd.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>
#include <sysdolphin/baselib/sislib.h>

/// asm `branchl r12, 0x800e8560` (Fox down special).
void ftFx_SpecialLw_Enter(HSD_GObj* gobj);

#define FOX_EXT 0x2
#define STAGE_FINAL_DESTINATION 0x20

#define SHINE_TIMER_MAX (7 * 60)
#define SHINE_TIMER_MIN (3 * 60)
#define RESET_TIMER (1 * 60)

/* event data offsets */
#define OFST_SHINE_TIMER 0x0    /* u16 */
#define OFST_RESET_TIMER 0x2    /* u16 */
#define OFST_REACTION_TIMER 0x4 /* s16, -1 = not running */

static void NewShineTimer(u8* data)
{
    LG_U16(data, OFST_SHINE_TIMER) =
        HSD_Randi(SHINE_TIMER_MAX - SHINE_TIMER_MIN) + SHINE_TIMER_MIN;
}

/// "Reaction THINK FUNCT".
static void ReactionThink(HSD_GObj* event)
{
    u8* data = event->user_data;
    HSD_GObj* gobj[4];
    Fighter* fp[4];
    u16 t;

    tm_legacy_GetAllPlayerPointers(gobj, fp);

    if (tm_legacy_CheckIfFirstFrame()) {
        tm_legacy_PlacePlayersCenterStage(tm_legacy_StageGetGroundID_Main());
        tm_legacy_SaveState_Save(
            (TmLegacySaveState*) (data + LG_EVDATA_SAVESTATE), true);
        NewShineTimer(data);
        LG_S16(data, OFST_REACTION_TIMER) = -1;
        lbAudioAx_80025064(0, 2); /* stop music */
    }

    tm_legacy_StoreCPUTypeAndZeroInputs(fp[1]);
    ftColl_8007B760(gobj[0], 1); /* intangible */
    ftColl_8007B760(gobj[1], 1);

    /* after a result: count down, then reset */
    t = LG_U16(data, OFST_RESET_TIMER);
    if (t > 0) {
        t--;
        LG_U16(data, OFST_RESET_TIMER) = t;
        if (t == 0) {
            tm_legacy_SaveState_Load(
                (TmLegacySaveState*) (data + LG_EVDATA_SAVESTATE));
            NewShineTimer(data);
            LG_U16(data, OFST_RESET_TIMER) = 0;
            LG_S16(data, OFST_REACTION_TIMER) = -1;
        }
        return;
    }

    /* waiting for the shine */
    t = LG_U16(data, OFST_SHINE_TIMER);
    if (t > 0) {
        t--;
        LG_U16(data, OFST_SHINE_TIMER) = t;
        if (t > 0) {
            if (LG_S32(fp[0], LG_FT_STATE) != LG_ASID_WAIT) {
                /* acted early */
                tm_legacy_PlaySFX(0xAF);
                LG_U16(data, OFST_RESET_TIMER) = RESET_TIMER - 40;
            }
            return;
        }
        ftFx_SpecialLw_Enter(gobj[1]);
        LG_S16(data, OFST_REACTION_TIMER) = 0;
        return;
    }

    /* timing the reaction */
    if (LG_S16(data, OFST_REACTION_TIMER) >= 0 &&
        HSD_PadGameStatus[LG_U8(fp[0], LG_FT_PORT)].trigger != 0)
    {
        HSD_Text* text = tm_osd_TextCreate(fp[0], 120, 0, TM_OSD_MISCELLANEOUS);
        u16 frames = LG_U16(data, OFST_REACTION_TIMER);

        LG_U32(text, 0x30) = frames <= 15 ? TM_OSD_RGBA_GREEN : TM_OSD_RGBA_RED;
        HSD_SisLib_803A6B98(text, LG_TEXT_X, LG_TEXT_X, "Reaction Time:");
        HSD_SisLib_803A6B98(text, LG_TEXT_X, LG_TEXT_LINE2_Y, "%d Frames",
                            frames + 1);
        LG_U16(data, OFST_RESET_TIMER) = RESET_TIMER;
        return;
    }
    LG_U16(data, OFST_REACTION_TIMER)++;
}

/// "Reaction LOAD FUNCT".
static void ReactionLoad(void)
{
    StartOSDs();
    tm_legacy_CreateEventThinkFunction(ReactionThink, 3, NULL, NULL);
}

/// "Reaction HIJACK INFO".
void tm_legacy_ev_Reaction(TmLegacySetup* s)
{
    LG_U8(LG_EVENT_INFO, 0xB) &= ~0x02; /* score: KOs, not time */
    tm_legacy_InitializeMatch(s->event, s->md, FOX_EXT,
                              STAGE_FINAL_DESTINATION, 0, false);
    s->md->rules.on_match_start = ReactionLoad;
}
