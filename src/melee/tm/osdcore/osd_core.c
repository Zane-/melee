/**
 * @file
 * TM-CE OSD core, native side (osdcore area). See osd.h for the API and
 * config/GALE01/tm_hooks/osdcore.txt for the hooks. The FighterData.TM
 * bookkeeping and Generic Per Frame are in src/tmce/osdcore_vars.c.
 */
#include "osd.h"

#include <string.h>
#include <melee/ft/ftcoll.h>
#include <melee/ft/ftcommon.h>
#include <melee/ft/fighter.h>
#include <melee/ft/inlines.h>
#include <melee/ft/types.h>
#include <melee/if/ifall.h>
#include <melee/lb/lb_00B0.h>
#include <melee/pl/player.h>
#include <melee/pl/pltrick.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjproc.h>
#include <sysdolphin/baselib/memory.h>
#include <sysdolphin/baselib/sislib.h>

/// @name src/tmce/osdcore_vars.c (MexTK side; fighters as void*)
/// @{
int tmce_osd_IsEnabled(int osd);
int tmce_osd_MaxWindows(void);
void tmce_osd_IncFrameCounts(void* fp);
void tmce_osd_SetShieldOwner(void* attacker, void* shield_owner);
void tmce_osd_BackupMoveInstance(void* victim);
void tmce_osd_GenericPerFrame(HSD_GObj* gobj);
void tmce_osd_ActOoWait(HSD_GObj* gobj);
/// @}

/// pl/player.c: per-character table (internal kinds, has_transformation).
typedef struct TmFtMapping {
    /* 0 */ s8 internal_id;
    /* 1 */ s8 extra_internal_id;
    /* 2 */ s8 has_transformation;
} TmFtMapping;
extern TmFtMapping ftMapping_list[];

/// @name Hook targets (config/GALE01/tm_hooks/osdcore.txt)
/// @{
int tm_osd_Hook_ScoreCanvas(int arg0, HSD_GObj* arg1, u16 arg2, u8 arg3,
                            u8 arg4, u8 arg5, u8 arg6, u32 arg7);
void tm_osd_Hook_ProcAnim(Fighter_GObj* gobj);
void tm_osd_Hook_ProcInput(Fighter_GObj* gobj);
void tm_osd_Hook_HitShield(Fighter* fp0, HitCapsule* hit0, Fighter* fp1);
void tm_osd_Hook_TrickHit(HSD_GObj* attacker, HSD_GObj* victim, s32 arg2,
                          ft_800898B4_t* arg3, u16 attack_instance, s32 arg5,
                          s32 arg6);
/// @}

/* ---- API ---------------------------------------------------------------- */

bool tm_osd_IsEnabled(int osd)
{
    return tmce_osd_IsEnabled(osd);
}

bool tm_osd_IsFollower(Fighter* fp)
{
    if (!fp->is_sub_fighter) {
        return false;
    }
    /* A sub-fighter is a follower unless its character transforms
     * (Zelda/Sheik use the sub slot too). */
    return ftMapping_list[Player_GetPlayerCharacter(fp->player_idx)]
               .has_transformation == 0;
}

HSD_Text* tm_osd_MessageText(HSD_GObj* msg)
{
    return *(HSD_Text**) msg->user_data;
}

void tm_osd_ActOoWait(HSD_GObj* gobj)
{
    tmce_osd_ActOoWait(gobj);
}

/* ---- Message Display System --------------------------------------------- */

/*
 * Message areas (Create Message Struct.asm): 0x300 bytes from the match
 * heap, three areas of 0x100. Areas 0 and 1 hold a queue of five windows
 * (0x28 bytes) per player, area 2 a single window. The asm kept the block's
 * pointer in un_804A1F58+4 (the score display's padding).
 */
#define TM_MSG_AREA_SIZE 0x100
#define TM_MSG_QUEUE_LEN 5 /* 0x28 / sizeof(TmOsdWindow) */

typedef struct TmOsdWindow {
    /* 0 */ HSD_Text* text;
    /* 4 */ u16 timer; ///< frames left
    /* 6 */ u16 id;    ///< overlay (OSD) ID
} TmOsdWindow;

static u8* msg_areas;
static int msg_canvas; ///< un_804A1F58.x0, the score display's text canvas

static TmOsdWindow* MsgArea(int area)
{
    return (TmOsdWindow*) (msg_areas + area * TM_MSG_AREA_SIZE);
}

/// Text placement per area (TextProperties in Display Message 2.0.asm).
typedef struct TmOsdTextProps {
    /* 00 */ f32 hud_x; ///< != 0: x from the player's HUD; areas 0-1
    /* 04 */ f32 y;
    /* 08 */ f32 x;     ///< x when hud_x == 0 (area 2)
    /* 0C */ f32 size;
    /* 10 */ f32 bg_y;
    /* 14 */ f32 bg_stretch_x;
    /* 18 */ f32 bg_stretch_y;
} TmOsdTextProps;

static const TmOsdTextProps text_props[3] = {
    { -21.0F, 11.0F, 14.0F, 0.04F, -410.0F, 12.0F, 28.0F },  /* above HUD */
    { -21.0F, -20.0F, 14.0F, 0.04F, -410.0F, 9.5F, 28.0F },  /* top */
    { 0.0F, -15.0F, 19.0F, 0.04F, -410.0F, 13.5F, 28.0F },   /* popup */
};

/// Y moves when a window shifts back (ShiftQueue_Floats) or forward
/// (CheckForDuplicates_Floats / MessageThink_Floats), per area.
static const f32 shift_back_y[2] = { -4.5F, 4.5F };
static const f32 shift_fwd_y[2] = { 4.5F, -4.5F };

static void ClearWindow(TmOsdWindow* w)
{
    w->text = NULL;
    w->timer = 0;
    w->id = 0;
}

static void MoveY(HSD_Text* text, f32 dy)
{
    text->pos_y = dy + text->pos_y;
}

/// MessageThink_Updater (Create Message Struct.asm).
static void UpdateWindows(int area, int ply)
{
    TmOsdWindow* q = MsgArea(area);
    int n = 1;
    int i;
    int k;

    if (area < 2) {
        q += ply * TM_MSG_QUEUE_LEN;
        n = TM_MSG_QUEUE_LEN;
    }
    for (i = 0; i < n; i++) {
        int t;
        if (q[i].text == NULL) {
            continue;
        }
        /* The asm compares the zero-extended timer with -1, which never
         * matches, so 0xFFFF counts down too. Kept. */
        t = q[i].timer - 1;
        q[i].timer = t;
        if (t > 0) {
            continue;
        }
        HSD_SisLib_803A5CC4(q[i].text);
        ClearWindow(&q[i]);
        if (area >= 2) {
            continue;
        }
        /* shift the rest forward */
        for (k = i + 1; k < TM_MSG_QUEUE_LEN; k++) {
            q[k - 1] = q[k];
            if (q[k - 1].text != NULL) {
                MoveY(q[k - 1].text, shift_fwd_y[area]);
            }
        }
        /* The asm leaves the last window in place too, so it is listed
         * twice and its text later freed twice. Clear it. */
        ClearWindow(&q[TM_MSG_QUEUE_LEN - 1]);
    }
}

/// MessageThink (Create Message Struct.asm): timers for every window.
static void MessageThink(HSD_GObj* gobj)
{
    int i;
    for (i = 0; i < 4; i++) {
        UpdateWindows(0, i);
    }
    for (i = 0; i < 4; i++) {
        UpdateWindows(1, i);
    }
    UpdateWindows(2, 0);
}

/// Wraps the `HSD_SisLib_803A611C` call in un_802FF498 (+0x48), the score
/// display's per-match setup (ifAll HUD init).
///
/// Port of Create Message Struct.asm (un_802FF498+0x50, the function's
/// epilogue): allocate the message areas and the think GObj.
int tm_osd_Hook_ScoreCanvas(int arg0, HSD_GObj* arg1, u16 arg2, u8 arg3,
                            u8 arg4, u8 arg5, u8 arg6, u32 arg7)
{
    HSD_GObj* gobj;
    int canvas =
        HSD_SisLib_803A611C(arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7);

    msg_canvas = canvas;
    msg_areas = HSD_MemAlloc(3 * TM_MSG_AREA_SIZE);
    memzero(msg_areas, 3 * TM_MSG_AREA_SIZE);
    gobj = GObj_Create(0xE, 7, 0);
    HSD_GObj_SetupProc(gobj, MessageThink, 0);
    return canvas;
}

/// CheckForDuplicates (Display Message 2.0.asm): remove the first window
/// with @p id among the first @p max and move the ones after it forward.
static void RemoveDuplicate(TmOsdWindow* q, int area, int id, int max)
{
    int i = 0;
    int k;

    do {
        /* the stored ID is zero-extended: TM_OSD_NULL (-1) never matches */
        if (q[i].text != NULL && (int) q[i].id == id) {
            HSD_SisLib_803A5CC4(q[i].text);
            ClearWindow(&q[i]);
            k = i + 1;
            do {
                q[k - 1] = q[k];
                ClearWindow(&q[k]);
                if (q[k - 1].text != NULL) {
                    MoveY(q[k - 1].text, shift_fwd_y[area]);
                }
                k++;
            } while (k < max);
            return;
        }
        i++;
    } while (i < max);
}

/// ShiftQueue (Display Message 2.0.asm): drop window @p max, move the
/// others back one.
static void ShiftQueue(TmOsdWindow* q, int area, int max)
{
    int i;

    if (q[max].text != NULL) {
        HSD_SisLib_803A5CC4(q[max].text);
        ClearWindow(&q[max]);
    }
    if (max == 0) {
        return;
    }
    for (i = max; i >= 0; i--) {
        q[i + 1] = q[i];
        ClearWindow(&q[i]);
        if (q[i + 1].text != NULL) {
            MoveY(q[i + 1].text, shift_back_y[area]);
        }
    }
}

HSD_Text* tm_osd_TextCreate(Fighter* fp, int timer, int area, int overlay_id)
{
    static const GXColor black = { 0, 0, 0, 0 };
    const TmOsdTextProps* props = &text_props[area];
    TmOsdWindow* q = MsgArea(area);
    HSD_Text* text;
    GXColor color;
    f32 x;
    int max = tmce_osd_MaxWindows();

    /* The queue holds 5 windows and ShiftQueue touches window max + 1;
     * above 3 the asm runs into the next player's queue. */
    if (max > 3) {
        max = 3;
    }

    if (area >= 2) {
        /* the popup area replaces its only window (the asm also does this
         * when it is empty, i.e. removes NULL) */
        if (q->text != NULL) {
            HSD_SisLib_803A5CC4(q->text);
        }
    } else {
        q += fp->player_idx * TM_MSG_QUEUE_LEN;
        RemoveDuplicate(q, area, overlay_id, max);
        ShiftQueue(q, area, max);
    }

    text = HSD_SisLib_803A6754(2, msg_canvas);
    q->text = text;
    q->timer = timer;
    q->id = overlay_id;

    text->default_alignment = 1;
    text->default_kerning = 1;

    if (props->hud_x != 0.0F) {
        x = ifAll_GetPlayerHUDPosition(fp->player_idx)->x;
    } else {
        x = props->x;
    }
    text->pos_x = x;
    text->pos_y = props->y;
    text->font_size.x = props->size;
    text->font_size.y = props->size;

    /* background: a long dash (Shift JIS 0x815B) */
    HSD_SisLib_803A6B98(text, 0.0F, props->bg_y, "\x81\x5B");
    color = black;
    HSD_SisLib_803A74F0(text, 0, &color);
    HSD_SisLib_803A7548(text, 0, props->bg_stretch_x, props->bg_stretch_y);
    return text;
}

/* ---- Additional Playerblock Variables hooks ------------------------------ */

/// Wraps `ftCommon_8007E0E4` in Fighter_procAnim (+0x81C).
///
/// Port of StatesAndTimers/IncFrameCounts.asm (Fighter_procAnim+0x818, the
/// instruction before this call; no branch lands between them).
void tm_osd_Hook_ProcAnim(Fighter_GObj* gobj)
{
    tmce_osd_IncFrameCounts(GET_FIGHTER(gobj));
    ftCommon_8007E0E4(gobj);
}

/// Wraps `Fighter_UnkIncrementCounters_8006ABEC` in Fighter_procInput
/// (+0xAE0).
///
/// Port of Generic Per Frame.asm (Fighter_procInput+0xAE4, the instruction
/// after this call).
void tm_osd_Hook_ProcInput(Fighter_GObj* gobj)
{
    Fighter_UnkIncrementCounters_8006ABEC(gobj);
    tmce_osd_GenericPerFrame(gobj);
}

/// Wraps the only `ftColl_80076CBC` call (ftColl_80078C70+0x428): fp0's
/// hitbox hit fp1's shield.
///
/// Port of Frame Advantage/Save Pointer to Shield Owner On Hit.asm
/// (ftColl_80076CBC+0x1F0, where both branches meet; nothing after it reads
/// the field).
void tm_osd_Hook_HitShield(Fighter* fp0, HitCapsule* hit0, Fighter* fp1)
{
    ftColl_80076CBC(fp0, hit0, fp1);
    tmce_osd_SetShieldOwner(fp0, fp1);
}

/// Wraps the only `pl_80038144` call (ftColl_8007861C+0xD4).
///
/// Port of Previous Move Instance Hit By/Backup Previous Move Instance
/// Player was Hit By.asm (pl_80038144+0xC8). Two paths branch straight to
/// that site, so it cannot wrap a call inside; nothing before it in
/// pl_80038144 changes the victim's attack instance, so this runs first.
void tm_osd_Hook_TrickHit(HSD_GObj* attacker, HSD_GObj* victim, s32 arg2,
                          ft_800898B4_t* arg3, u16 attack_instance, s32 arg5,
                          s32 arg6)
{
    tmce_osd_BackupMoveInstance(GET_FIGHTER(victim));
    pl_80038144(attacker, victim, arg2, arg3, attack_instance, arg5, arg6);
}
