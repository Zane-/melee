/**
 * @file
 * Legacy event dispatch and match setup: "LegacyEvent" (asm lines 22-123),
 * P1Struct/P2Struct, CreateEventThinkFunction, OptionMenuThink and the option
 * window (RAndDPadChangesEventOption), ClearToggledOptions,
 * InitializeHighScore/Event_ExitFunction, CheckIfFirstFrame, InitializeMatch
 * and DisableHazards from ../TrainingMode/ASM/training-mode/Custom Events/
 * Custom Event Code - Rewrite.asm. See legacy.h.
 */
#include "legacy.h"

#include <string.h>
#include <melee/gm/gmscene.h>
#include <melee/gm/gmevent.h>
#include <melee/gm/gmmain_lib.h>
#include <melee/gm/gmscdata.h>
#include <melee/gm/types.h>
#include <melee/gr/ground.h>
#include <melee/gr/stage.h>
#include <melee/if/ifstock.h>
#include <melee/lb/lb_00B0.h>
#include <melee/lb/lb_00F9.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/lb/lbdvd.h>
#include <melee/mn/types.h>
#include <melee/tm/osdcore/osd.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjgxlink.h>
#include <sysdolphin/baselib/gobjproc.h>
#include <sysdolphin/baselib/gobjuserdata.h>
#include <sysdolphin/baselib/memory.h>
#include <sysdolphin/baselib/sislib.h>

/// TM-CE events.c.
int GetJumpTableOffset(int page, int event);

/// Vanilla statics with unique names (resolved by the overlay linker).
extern u8 controller[];         ///< 0x8046B6A0: +1 pausing port, +0x2518 exit cb
extern u16 staffInfo[2];        ///< -0x4EA8(r13): event score (staffInfo[1])
extern s32 ft_804D6578;         ///< -0x5128(r13): wind hazard count

/* ---- the jump table ----------------------------------------------------- */

TmLegacySetupFunc const tm_legacy_events[TM_LEGACY_EVENT_COUNT] = {
    tm_legacy_ev_AmsahTech,   tm_legacy_ev_AttackOnShield,
    tm_legacy_ev_ComboTraining, tm_legacy_ev_EscapeSheik,
    tm_legacy_ev_GrabMashOut, tm_legacy_ev_LedgeStall,
    tm_legacy_ev_Ledgetech,   tm_legacy_ev_LedgetechCounter,
    tm_legacy_ev_Multishine,  tm_legacy_ev_Reaction,
    tm_legacy_ev_Reversal,    tm_legacy_ev_SDITraining,
    tm_legacy_ev_ShieldDrop,  tm_legacy_ev_SlideOff,
    tm_legacy_ev_WaveshineSDI,
};

/* ---- P1Struct / P2Struct (asm blrl data, gm_801BAB40_src) ---------------- */

/// external char, player type, stocks, costume / spawn point, subcolor,
/// team, voice pitch / player flag / level and % / atk, def ratio, scale.
static u32 P1Struct[7] = {
    0x01000200, 0xFF000400, 0x00040700, 0x00000000,
    0x3F800000, 0x3F800000, 0x3F800000,
};
static const u32 P2Struct[7] = {
    0x01010200, 0xFF000400, 0x00040700, 0x00000000,
    0x3F800000, 0x3F800000, 0x3F800000,
};

/* ---- LegacyEvent -------------------------------------------------------- */

bool tm_legacy_Setup(TmLegacySetup* s)
{
    u8* ev = (u8*) s->event;
    u8* md = (u8*) s->md;
    u8* css = gm_Mode_Event_States[0].info.enter_data; /* css_data */
    int idx;

    /* 1 player, no items, time counting up */
    LG_U32(ev, 0x18) = 0; /* player_init[1..5] */
    LG_U32(ev, 0x1C) = 0;
    LG_U32(ev, 0x20) = 0;
    LG_U32(ev, 0x24) = 0;
    LG_U32(ev, 0x28) = 0;
    LG_U8(ev, 0x0) = 0; /* kind: disable All-Star */
    LG_PTR(ev, 0x14) = P1Struct;

    LG_U32(md, 0x0) = 0x0BB0027C; /* HUD and timer behaviour */
    LG_U32(md, 0x4) = 0x90800000;
    LG_U8(md, 0xB) = 0xFF;  /* items off */
    LG_U32(md, 0x10) = 0;   /* time */
    LG_U8(md, 0x62) = 0xFF; /* P1 unlimited stocks */
    LG_U8(md, 0x6C) = 0;    /* fall flag */
    LG_U8(md, 0x8) = 0;     /* FFA */
    LG_S16(md, 0xE) = LG_S16(css, 0x1E); /* SSS stage */

    idx = GetJumpTableOffset(s->page, s->event_id);
    if (idx < 0 || idx >= TM_LEGACY_EVENT_COUNT) {
        return false; /* EventNoExist (the table ends in -1) */
    }
    tm_legacy_events[idx](s);
    return true;
}

void tm_legacy_InitializeMatch(struct gm_804D6900_t* event,
                               StartMeleeData* md_, int cpu_kind, int stage,
                               u32 osds, bool use_sopo)
{
    u8* ev = (u8*) event;
    u8* md = (u8*) md_;
    u8* p2;

    /* TM_OSDRecommended != 1: add the event's OSDs */
    if (LG_U8(LG_MEMCARD, 0x1F2A) != 1) {
        LG_U32(LG_MEMCARD, 0x1F24) |= osds;
    }

    LG_U8(ev, 0x1) = 0x40; /* 2 players */
    p2 = HSD_MemAlloc(32);
    memcpy(p2, P2Struct, 0x1C);
    LG_PTR(ev, 0x18) = p2;

    if (cpu_kind != -1) {
        LG_U8(p2, 0x0) = cpu_kind;
    } else {
        u8* preload = (u8*) lbDvd_GetPreloadCacheScene();
        s32 kind = LG_S32(preload, 0x18);
        if (kind == 0x12) { /* Zelda: make her Sheik */
            kind = 0x13;
        }
        LG_U8(p2, 0x0) = kind;
        LG_U8(p2, 0x3) = LG_U8(preload, 0x1C); /* costume */
        LG_U8(p2, 0x1) = 1;                    /* CPU */
    }

    if (stage != -1) {
        LG_U16(md, 0xE) = stage;
    } else {
        u8* preload = (u8*) lbDvd_GetPreloadCacheScene();
        LG_U16(md, 0xE) = LG_U32(preload, 0xC);
    }

    if (use_sopo) {
        u8* backup = LG_MEMCARD + 1328;
        if (LG_U8(backup, 0x2) == 0xE) { /* Ice Climbers */
            LG_U8(backup, 0x2) = 0x20;   /* Sopo */
        }
    }
}

/* ---- option menu --------------------------------------------------------- */

static const char* GetNextString(const char* s)
{
    const char* p = s + strlen(s);
    while (*++p == '\0') {
    }
    return p;
}

/// asm RAndDPadChangesEventOption_GetOptionASCII (r21 = window info).
static void GetOptionASCII(const char* ascii, const u8* info, int window,
                           int sel, const char** title, const char** text)
{
    const char* p = ascii;
    int k, j;

    for (k = 0; k != window; k++) {
        p = GetNextString(p); /* title */
        for (j = 0; j != info[1 + k] + 1; j++) {
            p = GetNextString(p);
        }
    }
    *title = p;
    p = GetNextString(p);
    for (j = 0; j != sel; j++) {
        p = GetNextString(p);
    }
    *text = p;
}

/// asm OptionWindow (RAndDPadChangesEventOption): r3 option memory
/// (cursor, scroll, selections), r4 window info, r5 option text. Returns the
/// toggled bool (r3) and the toggled window (r4).
static int OptionWindow(u8* mem, const u8* info, const char* ascii,
                        int* toggled_option)
{
    static const f32 floats[5] = { 16.0F, 63.0F, 94.0F, -900.0F, -1350.0F };
    static const GXColor grey = { 0xDF, 0xDF, 0xDF, 0x00 };
    static const GXColor yellow = { 0xF7, 0xFF, 0x27, 0x00 };
    int toggled = 0;
    int n = info[0];
    u32 trigger;
    HSD_Text* text;
    int i;

    *toggled_option = -1;
    if (n > 2) {
        n = 2;
    }
    trigger = HSD_PadMasterStatus[controller[1]].trigger;

    if (trigger == 0x04) { /* down */
        int c = mem[0] + 1;
        mem[0] = c;
        if (c > n) {
            mem[0] = n;
            if (n + mem[1] >= info[0]) {
                goto display;
            }
            mem[1]++;
        }
    } else if (trigger == 0x08) { /* up */
        int c = mem[0] - 1;
        mem[0] = c;
        if (c < 0) {
            mem[0] = 0;
            if (mem[1] <= 0) {
                goto display;
            }
            mem[1]--;
        }
    } else if (trigger == 0x02) { /* right: next value */
        int w = mem[0] + mem[1];
        int v = mem[2 + w] + 1;
        toggled = 1;
        *toggled_option = w;
        mem[2 + w] = v;
        if (v > info[1 + w]) {
            mem[2 + w] = 0;
        }
    } else if (trigger == 0x01) { /* left: previous value */
        int w = mem[0] + mem[1];
        int v = mem[2 + w] - 1;
        toggled = 1;
        *toggled_option = w;
        mem[2 + w] = v;
        if (v < 0) {
            mem[2 + w] = info[1 + w];
        }
    } else {
        goto display;
    }
    lbAudioAx_80024030(2);

display:
    /* the asm passes a stale r27 as the fighter; area 2 never reads it */
    text = tm_osd_TextCreate(NULL, 1, 2, 0);

    if (n != 0) {
        HSD_SisLib_803A7548(text, 0, floats[0], floats[1 + (n - 1)]);
        HSD_SisLib_803A746C(text, 0, LG_TEXT_X, floats[3 + (n - 1)]);
        if (mem[1] != 0) {
            HSD_SisLib_803A6B98(text, -210.0F, -20.0F, "^");
        }
        if (info[0] >= 2 && info[0] - mem[1] > 2) {
            HSD_SisLib_803A6B98(text, -210.0F, 320.0F, "v");
        }
    }

    for (i = 0;; i++) {
        int window = mem[1] + i;
        const char* title;
        const char* value;
        GXColor color;
        int sub;

        GetOptionASCII(ascii, info, window, mem[2 + window], &title, &value);
        /* the asm passes the option strings as format strings */
        sub = HSD_SisLib_803A6B98(text, LG_TEXT_X, LG_TEXT_X + 120 * i,
                                  (char*) title);
        color = grey;
        HSD_SisLib_803A74F0(text, sub, &color);
        sub = HSD_SisLib_803A6B98(text, LG_TEXT_X, LG_TEXT_LINE2_Y + 120 * i,
                                  (char*) value);
        if (mem[0] == i) {
            color = yellow;
            HSD_SisLib_803A74F0(text, sub, &color);
        }
        if (!(i < n)) {
            break;
        }
    }
    return toggled;
}

/// asm OptionMenuThink (priority 22): the option window while paused.
static void OptionMenuThink(HSD_GObj* gobj)
{
    u8* menu = gobj->user_data;
    int option;

    if (!gm_GetDbPauseFlag(1)) {
        return;
    }
    if (OptionWindow(menu + LG_MENU_MEMORY, LG_PTR(menu, LG_MENU_WINDOW_INFO),
                     LG_PTR(menu, LG_MENU_ASCII), &option))
    {
        LG_U8(menu, LG_MENU_TOGGLED + option) = 1;
    }
}

void tm_legacy_ClearToggledOptions(u8* menu)
{
    const u8* info = LG_PTR(menu, LG_MENU_WINDOW_INFO);
    int i;
    for (i = info[0]; i >= 0; i--) {
        LG_U8(menu, LG_MENU_TOGGLED + i) = 0;
    }
}

HSD_GObj* tm_legacy_CreateEventThinkFunction(void (*think)(HSD_GObj*),
                                             int priority,
                                             const u8* window_info,
                                             const char* ascii)
{
    HSD_GObj* gobj = GObj_Create(6, 7, 80);
    u8* data;

    HSD_GObj_SetupProc(gobj, think, priority);
    data = HSD_MemAlloc(LG_EVDATA_SIZE);
    GObj_InitUserData(gobj, 0, HSD_Free, data);
    memzero(data, LG_EVDATA_SIZE);

    if (window_info != NULL) {
        HSD_GObj* menu_gobj = GObj_Create(6, 0, 80);
        u8* menu;

        HSD_GObj_SetupProc(menu_gobj, OptionMenuThink, 22);
        menu = HSD_MemAlloc(LG_MENU_SIZE);
        GObj_InitUserData(menu_gobj, 0, HSD_Free, menu);
        memzero(menu, LG_MENU_SIZE);
        LG_PTR(menu, LG_MENU_WINDOW_INFO) = (void*) window_info;
        LG_PTR(menu, LG_MENU_ASCII) = (void*) ascii;
        LG_PTR(data, LG_EVDATA_MENU) = menu;
        LG_PTR(menu, LG_MENU_EVDATA) = data;
    }

    tm_legacy_DisableHazards();
    return gobj;
}

/* ---- high score ---------------------------------------------------------- */

/// asm Event_ExitFunction: save the score as the event's high score.
static void Event_ExitFunction(void)
{
    u8* info = LG_EVENT_INFO;
    s32 best;

    if (LG_U8(LG_MEMCARD, 0x53B) & 0x40) { /* no contest / retry */
        return;
    }
    best = gmMainLib_8015CF5C(info[5]);
    if (gmMainLib_8015CEFC(info[5]) && staffInfo[1] <= best) {
        return;
    }
    gmMainLib_8015CF70(info[5], staffInfo[1]);
    gmMainLib_8015CEB4(info[5]);
}

void tm_legacy_InitializeHighScore(void)
{
    ifStock_802FA5BC(0); /* KO counter HUD */
    *(u32*) staffInfo = 0;
    LG_PTR(controller, 0x2518) = Event_ExitFunction;
}

bool tm_legacy_CheckIfFirstFrame(void)
{
    return tm_misc_game_frame_counter == 1;
}

/* ---- DisableHazards ----------------------------------------------------- */

static void RagdollFixThink(HSD_GObj* gobj)
{
    lb_800115F4();
}

/// asm DisableHazards_RagdollFix: re-run the ragdoll/wind decay that lived
/// in the removed map think.
static void RagdollFix(void)
{
    HSD_GObj* gobj = GObj_Create(3, 5, 0);
    HSD_GObj_SetupProc(gobj, RagdollFixThink, 4);
}

void tm_legacy_DisableHazards(void)
{
    switch (selected_stage.stkind) {
    case 3: /* Pokemon Stadium: transformation */
        HSD_GObjProc_RemoveAllProcs(Ground_GetMapGObj(2));
        RagdollFix();
        break;
    case 8: /* Yoshi's Story: Shy Guys */
        HSD_GObjProc_RemoveAllProcs(Ground_GetMapGObj(3));
        RagdollFix();
        break;
    case 28: /* Dream Land N64: Whispy and its wind */
        Ground_801C4A08(Ground_GetMapGObj(7));
        HSD_GObjProc_RemoveAllProcs(Ground_GetMapGObj(6));
        ft_804D6578 = 0;
        break;
    case 29: /* Yoshi's Island N64: clouds */
        Ground_801C4A08(Ground_GetMapGObj(2));
        break;
    case 30: /* Kongo Jungle N64: barrel */
        Ground_801C4A08(Ground_GetMapGObj(1));
        break;
    default:
        break;
    }
}
