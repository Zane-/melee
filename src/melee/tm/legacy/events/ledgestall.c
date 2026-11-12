/**
 * @file
 * TM-CE legacy event LedgeStall (Custom Event Code - Rewrite.asm, lines
 * 538-1083): on Brinstar, ledge stall while the lava rises. Time spent below
 * the lava surface (intangible on the ledge) is the score; getting hit or
 * dying ends the run, and a positive score is checked against the record.
 */
#include "../legacy.h"

#include <melee/cm/camera.h>
#include <melee/gm/gmmain_lib.h>
#include <melee/gm/gmvs.h>
#include <melee/gr/ground.h>
#include <melee/gr/types.h>
#include <melee/gm/types.h>
#include <sysdolphin/baselib/gobjplink.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjproc.h>
#include <sysdolphin/baselib/jobj.h>

/// gm/gmmain_lib / ifstatus statics with unique names.
extern u8 controller[]; ///< 0x8046B6A0: +0x28 timer seconds, +0x2C subseconds

#define STAGE_BRINSTAR 0x6
#define ASID_DAMAGE_HI1 0x4B
#define ASID_DAMAGE_FLY_ROLL 0x5B

#define MAP_GOBJ_PLATFORM 6
#define MAP_GOBJ_LAVA 8

/* LedgeStallThink_Constants */
#define LAVA_RISE_RATE 0.4F
#define LAVA_MAX_Y 10.0F

/* constants */
#define RESET_TIMER 30
#define LAVA_START_Y -100
#define LAVA_START_TIMER 123
#define SURVIVAL_SFX_INTERVAL 5

/* event data offsets */
#define EVENT_STATE 0x0 /* u8 */
#define STATE_LAVA_DELAY 0
#define STATE_LAVA_RISE 1
#define STATE_RESET 2
#define TIMER 0x1         /* u8 */
#define LAVA_TIMER 0x2    /* u16 */
#define SURVIVAL_TIME 0x4 /* s32 */
#define LAVA_POSITION 0x8 /* f32 */

/// asm Ledgestall_UpdateLavaPosition (f1 = lava Y).
static void UpdateLavaPosition(f32 y)
{
    HSD_JObj* jobj =
        Ground_801C3FA4((HSD_GObj*) Ground_GetMapGObj(MAP_GOBJ_LAVA), 0);

    /* the model sits 55 below where the lava surface is */
    LG_F32(jobj, 0x3C) = 55.0F + y;
    HSD_JObjSetMtxDirtySub(jobj);
    Ground_801C438C(y); /* hitbox */
}

/// asm LedgeStall_InitializePositions.
static void InitializePositions(HSD_GObj* p1, u8* data)
{
    tm_legacy_PlaceOnLedge(p1, 0);
    tm_legacy_UpdateCameraBox(p1);

    LG_F32(data, LAVA_POSITION) = (f32) LAVA_START_Y;
    UpdateLavaPosition(LG_F32(data, LAVA_POSITION));

    LG_U8(data, EVENT_STATE) = STATE_LAVA_DELAY;
    LG_U8(data, TIMER) = 0;
    LG_S32(data, SURVIVAL_TIME) = 0;
    LG_U16(data, LAVA_TIMER) = LAVA_START_TIMER;
}

/// Match timer back to 0:00.
static void ClearMatchTimer(void)
{
    LG_U32(controller, 0x28) = 0;
    LG_U16(controller, 0x2C) = 0;
}

/// asm LedgeStallThink_CheckTimer: count down after a hit, then end the
/// match with a result.
static void CheckTimer(HSD_GObj* event, u8* data)
{
    s32 score;
    s32 id;

    if (LG_U8(data, TIMER) == 0) {
        return;
    }
    if (--LG_U8(data, TIMER) > 0) {
        return;
    }

    gm_SetGameSpeed(1.0F);
    score = LG_S32(data, SURVIVAL_TIME);
    if (score <= 0) {
        gm_8016B33C(6);   /* Failure + SFX */
        gm_8016B364(328); /* crowd sigh */
        gm_8016B378(40);
        gm_8016B328(); /* end the match */
    } else {
        id = LG_U8(LG_MEMCARD, 0x535);
        if (score > gmMainLib_8015CF5C(id)) {
            gm_8016B33C(2); /* Success + SFX */
            gm_8016B350(0x9C40);
            gm_8016B364(325); /* crowd cheer */
            gm_8016B328();
            gmMainLib_8015CF70(id, score);
            gmMainLib_8015CEB4(id); /* played */
        } else {
            gm_8016B33C(2);
            gm_8016B364(324);
            gm_8016B328();
        }
    }
    HSD_GObjFree(event);
}

/// "LedgeStall THINK FUNCT".
static void LedgeStallThink(HSD_GObj* event)
{
    u8* data = event->user_data;
    TmLegacySaveState* ss = (TmLegacySaveState*) (data + LG_EVDATA_SAVESTATE);
    HSD_GObj* gobj[4];
    Fighter* fp[4];
    u8* p1;
    s32 state;

    tm_legacy_GetAllPlayerPointers(gobj, fp);
    p1 = (u8*) fp[0];

    if (tm_legacy_CheckIfFirstFrame()) {
        InitializePositions(gobj[0], data);
        tm_legacy_RemoveFirstFrameInputs();
        tm_legacy_SaveState_Save(ss, true);
    }

    /* damaged or dead: start the reset timer once */
    state = LG_S32(p1, LG_FT_STATE);
    if ((state >= ASID_DAMAGE_HI1 && state <= ASID_DAMAGE_FLY_ROLL) ||
        (LG_U8(p1, LG_FT_FLAGS_221F) & 0x40))
    {
        if (LG_U8(data, TIMER) == 0) {
            LG_U8(data, TIMER) = RESET_TIMER;
            LG_U8(data, EVENT_STATE) = STATE_RESET;
        }
    }

    switch (LG_U8(data, EVENT_STATE)) {
    case STATE_LAVA_DELAY:
        ClearMatchTimer();
        if ((s32) LG_U16(data, LAVA_TIMER) - 1 > 0) {
            LG_U16(data, LAVA_TIMER)--;
            break;
        }
        LG_U16(data, LAVA_TIMER)--;
        LG_U8(data, EVENT_STATE) = STATE_LAVA_RISE;
        /* fall through */
    case STATE_LAVA_RISE:
        if (LG_F32(p1, LG_FT_POS_Y) < LG_F32(data, LAVA_POSITION)) {
            /* below the surface: score, with the HRC sound every 5 */
            s32 t = ++LG_S32(data, SURVIVAL_TIME);
            if ((t - 1) % SURVIVAL_SFX_INTERVAL == 0) {
                tm_legacy_PlaySFX(0xBB);
                tm_legacy_PlaySFX(0xBB);
            }
        } else {
            ClearMatchTimer();
            LG_S32(data, SURVIVAL_TIME) = 0;
        }
        if (LG_F32(data, LAVA_POSITION) < LAVA_MAX_Y) {
            LG_F32(data, LAVA_POSITION) += LAVA_RISE_RATE;
            UpdateLavaPosition(LG_F32(data, LAVA_POSITION));
        }
        break;
    case STATE_RESET:
        /* hold the match timer still */
        if (LG_U32(controller, 0x28) != 0 && LG_U16(controller, 0x2C) == 0) {
            LG_U16(controller, 0x2C) = 59;
            LG_U32(controller, 0x28)--;
        } else {
            LG_U16(controller, 0x2C)--;
        }
        break;
    default:
        break;
    }

    CheckTimer(event, data);
}

/// "LedgeStall LOAD FUNCT".
static void LedgeStallLoad(void)
{
    u8* cam;
    u8* item;
    Vec3 ledge;

    StartOSDs();
    tm_legacy_CreateEventThinkFunction(LedgeStallThink, 3, NULL, NULL);

    /* the lava stops rising and falling by itself */
    HSD_GObjProc_RemoveAllProcs((HSD_GObj*) Ground_GetMapGObj(MAP_GOBJ_LAVA));

    /* the platform's flesh item can't be hit */
    item = LG_PTR(Ground_GetMapGObj(MAP_GOBJ_PLATFORM), 0x2C);
    item = LG_PTR(item, 0xE4);
    item = LG_PTR(item, 0x2C);
    LG_U32(item, 0xACC) = 2;

    /* a camera box just behind the left ledge */
    cam = (u8*) Camera_80029020();
    tm_legacy_GetLedgeCoordinates(0, &ledge);
    LG_F32(cam, 0x10) = 35.0F + ledge.x;
    LG_F32(cam, 0x14) = 20.0F + ledge.y;
    LG_F32(cam, 0x40) = -10.0F;
    LG_F32(cam, 0x44) = 10.0F;
    LG_F32(cam, 0x48) = 10.0F;
    LG_F32(cam, 0x4C) = -10.0F;

    /* zoom the camera out more */
    LG_U32(&stage_info, 0x28) = 0x3FE66666; /* 1.8 */
}

/// "LedgeStall HIJACK INFO".
void tm_legacy_ev_LedgeStall(TmLegacySetup* s)
{
    LG_U8(s->md, 0x1) = 0x80; /* READY, GO! */
    tm_legacy_InitializeMatch(s->event, s->md, -1, STAGE_BRINSTAR, 0, true);
    LG_U8(s->event, 0x1) = 0x20; /* 1 player */
    s->md->rules.on_match_start = LedgeStallLoad;
}
