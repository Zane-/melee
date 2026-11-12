/**
 * @file
 * Legacy event savestates and the helpers that edit them: SaveState_Save,
 * SaveState_Load, SaveState_GetPlayerDataPointer, CheckForSaveAndLoad,
 * DPadCPUPercent, Randomize_LeftorRightSide, MoveCPU and
 * AdjustResetDistance from ../TrainingMode/ASM/training-mode/Custom Events/
 * Custom Event Code - Rewrite.asm. These are the asm's own whole-player-
 * block savestates, not TM-CE's C savestate_v1. See legacy.h.
 */
#include "legacy.h"

#include <string.h>
#include <melee/ft/fighter.h>
#include <melee/ft/ftanim.h>
#include <melee/ft/ftcommon.h>
#include <melee/ft/inlines.h>
#include <melee/ft/types.h>
#include <melee/ft/ft_081B.h>
#include <melee/ft/ft_0881.h>
#include <melee/ft/ft_0892.h>
#include <melee/ft/ft_0D4D.h>
#include <melee/gm/gmvs.h>
#include <melee/lb/lb_00B0.h>
#include <melee/if/ifstatus.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/memory.h>
#include <sysdolphin/baselib/objalloc.h>
#include <sysdolphin/baselib/random.h>

/// pl/player.c static (0x80453080), 0xE90 bytes per slot.
extern u8 player_slots[];
#define LG_STATIC_BLOCK(slot) (player_slots + 0xE90 * (slot))

/// asm SFXManager_StopSFXIfPlaying, HUD_PlayerCreate_Prefunction.
void un_80321CE8(void);
void ifStatus_802F6E1C(int slot);

int tm_legacy_SaveState_GetPlayerDataPointer(int n, bool sub,
                                             HSD_GObj** gobj, Fighter** fp)
{
    u8 order[8];
    int count = 0;
    int i, slot;
    HSD_GObj* g;

    memset(order, 0xFF, sizeof(order));
    for (i = 0; i < 6; i++) {
        /* an inactive static block has 0 at +0 */
        if (LG_U32(LG_STATIC_BLOCK(i), 0) != 0) {
            order[count++] = i;
        }
    }
    slot = order[n];
    if (slot == 0xFF) {
        return 0xFF;
    }
    g = LG_PTR(LG_STATIC_BLOCK(slot), sub ? 0xB4 : 0xB0);
    if (g == NULL) {
        return 0xFF;
    }
    *gobj = g;
    *fp = g->user_data;
    return slot;
}

void tm_legacy_SaveState_Save(TmLegacySaveState* ss, bool skip_failsafe)
{
    int total = gm_8016B558();
    int n, sub;
    HSD_GObj* g;
    Fighter* fp;

    if (!skip_failsafe) {
        n = 0;
        do {
            for (sub = 0; sub < 2; sub++) {
                if (tm_legacy_SaveState_GetPlayerDataPointer(n, sub, &g, &fp) ==
                    0xFF)
                {
                    continue;
                }
                /* on-death callbacks, held items, respawn platform */
                if (LG_U32(fp, 0x21E0) != 0 || LG_U32(fp, 0x21E4) != 0 ||
                    LG_U32(fp, 0x21E8) != 0 || LG_U32(fp, 0x1974) != 0 ||
                    LG_U32(fp, 0x1978) != 0 || LG_U32(fp, 0x20A0) != 0)
                {
                    tm_legacy_PlaySFX(0xAF);
                    tm_legacy_PlaySFX(0xAF);
                    return;
                }
            }
            n++;
        } while (n < total);
    }

    n = 0;
    do {
        for (sub = 0; sub < 2; sub++) {
            void** backup = &ss->backup[n][sub];
            int slot;
            u32 size;
            u8* buf;

            if (*backup != NULL) {
                HSD_Free(*backup);
                /* the asm keeps the freed pointer if the player is gone */
                *backup = NULL;
            }
            slot = tm_legacy_SaveState_GetPlayerDataPointer(n, sub, &g, &fp);
            if (slot == 0xFF) {
                continue;
            }
            size = fighter_alloc_data.size;
            buf = HSD_MemAlloc(size + 0x100 + 0x10);
            *backup = buf;
            memcpy(buf, fp, size);
            if (!sub) {
                memcpy(buf + size, LG_STATIC_BLOCK(slot), 0x100);
            }
            /* camera flag */
            LG_U32(buf, size + 0x100) = LG_U32(LG_PTR(fp, LG_FT_CAMBOX), 0x8);
        }
        n++;
    } while (n < total);
}

void tm_legacy_SaveState_Load(TmLegacySaveState* ss)
{
    int total = gm_8016B558();
    int n = 0;
    int sub;

    do {
        for (sub = 0; sub < 2; sub++) {
            u8* bk = ss->backup[n][sub];
            HSD_GObj* g;
            Fighter* fp;
            int slot;
            u32 size, b620, b624, b65C, coll;

            if (bk == NULL) {
                continue;
            }
            slot = tm_legacy_SaveState_GetPlayerDataPointer(n, sub, &g, &fp);
            if (slot == 0xFF) {
                continue;
            }
            size = fighter_alloc_data.size;

            LG_U32(fp, LG_FT_FACING) = LG_U32(bk, LG_FT_FACING);
            ftCo_800D4F24(g, 0); /* AS_Sleep */
            LG_U32(fp, 0x21E4) = 0; /* on-death callbacks */
            LG_U32(fp, 0x21E8) = 0;
            Fighter_ChangeMotionState(g, LG_S32(bk, LG_FT_STATE), 0,
                                      LG_F32(bk, LG_FT_ANIM_FRAME),
                                      LG_F32(bk, LG_FT_ANIM_SPEED), 0.0F,
                                      NULL);

            /* keep this frame's previous buttons and collision toggles */
            b620 = LG_U32(fp, 0x620);
            b624 = LG_U32(fp, 0x624);
            b65C = LG_U32(fp, 0x65C);
            coll = LG_U32(fp, 0x21FC);

            memcpy(fp, bk, size);
            if (!sub) {
                memcpy(LG_STATIC_BLOCK(slot), bk + size, 0x100);
            }

            LG_U32(fp, 0x620) = b620;
            LG_U32(fp, 0x628) = b620;
            LG_U32(fp, 0x624) = b624;
            LG_U32(fp, 0x62C) = b624;
            LG_U32(fp, 0x65C) = b65C;
            LG_U32(fp, 0x660) = b65C;
            LG_U32(fp, 0x664) = b65C;
            LG_U32(fp, 0x21FC) = coll;

            LG_U32(fp, 0x5A8) = 0;  /* cached animation (fall anim bug) */
            LG_U32(fp, 0x20A0) = 0; /* respawn platform JObj */
            LG_U32(fp, 0x21B0) = 0; /* and its think */
            LG_U32(fp, 0x1974) = 0; /* held item */

            tm_legacy_UpdatePosition(g);
            ft_80088A50(fp); /* stop the fighter's SFX */
            un_80321CE8();   /* stop crowd SFX */
            ftCommon_8007DB24(g); /* remove GFX */

            LG_U32(LG_PTR(fp, LG_FT_CAMBOX), 0x8) = LG_U32(bk, size + 0x100);
            tm_legacy_UpdateCameraBox(g);

            /* remake the HUD of dead players */
            if (!sub) {
                u8* hud = (u8*) &ifStatus_HudInfo + 100 * slot;
                if (gm_8016B094() && Player_GetStocks(slot) == 0) {
                    LG_U8(hud, 0x10) = 0x80; /* remove percent */
                } else if (LG_U8(hud, 0x10) & 0x80) {
                    ifStatus_802F6E1C(slot);
                }
            }
        }
        n++;
    } while (n < total);
}

int tm_legacy_CheckForSaveAndLoad(TmLegacySaveState* ss)
{
    int i;
    for (i = 0; i < 4; i++) {
        HSD_PadStatus* pad;

        if (Player_GetEntity(i) == NULL) {
            continue;
        }
        pad = &HSD_PadGameStatus[i];
        /* nothing but the D-pad and Z held (lhz of the button word) */
        if ((pad->button & 0xFFFF) & ~0x1F) {
            continue;
        }
        if (pad->trigger & 2) { /* D-pad right */
            tm_legacy_SaveState_Save(ss, false);
            return 0;
        }
        if (pad->trigger & 1) { /* D-pad left */
            tm_legacy_SaveState_Load(ss);
            tm_legacy_SaveState_Load(ss);
            return 1;
        }
    }
    return -1;
}

void tm_legacy_DPadCPUPercent(void** pair)
{
    u8* p2_static = LG_STATIC_BLOCK(1);
    Fighter* p1 = Player_GetEntity(0)->user_data;
    int pct = LG_U16(p2_static, 0x60);
    int sub = LG_U8(p2_static, 0xC);
    HSD_PadStatus* pad = &HSD_PadGameStatus[LG_U8(p1, LG_FT_PORT)];
    u32 rep;
    f32 f;
    u8* bk;

    if (!(pad->button & 0x40) && pad->analogL < 24) { /* L or lightshield */
        return;
    }
    rep = pad->repeat;
    if (rep & 2) {
        pct = pct < 999 ? pct + 1 : 999;
    } else if (rep & 1) {
        pct = pct > 0 ? pct - 1 : 0;
    } else if (rep & 8) {
        pct = pct < 989 ? pct + 10 : 999;
    } else if (rep & 4) {
        pct = pct > 9 ? pct - 10 : 0;
    } else {
        return;
    }

    LG_U16(p2_static, 0x60) = pct;
    f = pct;
    LG_F32(Player_GetEntity(1)->user_data, 0x1830) = f;
    LG_F32(pair[sub], 0x1830) = f;
    /* only the main fighter's backup has the static block */
    bk = (u8*) pair[0] + fighter_alloc_data.size;
    LG_U16(bk, 0x60) = pct;
    LG_U16(bk, 0x62) = pct;
}

void tm_legacy_Randomize_LeftorRightSide(u8* evdata, bool opposing)
{
    u8* p1 = LG_PTR(evdata, LG_EVDATA_SAVESTATE + 0x0);
    u8* p2 = LG_PTR(evdata, LG_EVDATA_SAVESTATE + 0x8);
    f32 x1 = LG_F32(p1, LG_FT_POS_X);
    f32 x2 = LG_F32(p2, LG_FT_POS_X);
    HSD_GObj* g;

    x1 = x1 < 0.0F ? -x1 : x1;
    x2 = x2 < 0.0F ? -x2 : x2;
    if (HSD_Randi(2) == 0) { /* left */
        LG_F32(p1, LG_FT_POS_X) = -x1;
        LG_F32(p2, LG_FT_POS_X) = opposing ? x2 : -x2;
        LG_F32(p1, LG_FT_FACING) = 1.0F;
        LG_F32(p2, LG_FT_FACING) = -1.0F;
    } else { /* right */
        LG_F32(p1, LG_FT_POS_X) = x1;
        LG_F32(p2, LG_FT_POS_X) = opposing ? -x2 : x2;
        LG_F32(p1, LG_FT_FACING) = -1.0F;
        LG_F32(p2, LG_FT_FACING) = 1.0F;
    }

    /* copy each main fighter's backup X and facing into its follower's */
    for (g = HSD_GObjPLinkHead[8]; g != NULL; g = g->next) {
        Fighter* fp = g->user_data;
        Fighter* sub_fp;
        u8* pair;

        if (LG_U8(fp, LG_FT_FLAGS_221F) & 0x08) { /* sub-fighter */
            continue;
        }
        if (tm_legacy_CheckIfPlayerHasAFollower(g, &sub_fp) == NULL) {
            continue;
        }
        /* indexed by slot, not by player number, as in the asm */
        pair = evdata + LG_EVDATA_SAVESTATE + LG_U8(fp, LG_FT_SLOT) * 8;
        LG_U32(LG_PTR(pair, 4), LG_FT_POS_X) =
            LG_U32(LG_PTR(pair, 0), LG_FT_POS_X);
        LG_U32(LG_PTR(pair, 4), LG_FT_FACING) =
            LG_U32(LG_PTR(pair, 0), LG_FT_FACING);
    }
}

/// Wait, position, ground, ECB and grounded state (MoveCPU's sequence).
static void MoveToGround(HSD_GObj* g, Fighter* fp)
{
    ft_8008A2BC(g); /* AS_Wait */
    tm_legacy_UpdatePosition(g);
    ft_80084280(g); /* ECB for the ground id */
    ftCommon_8007D6A4(fp); /* grounded */
}

void tm_legacy_MoveCPU(HSD_GObj* p1g, HSD_GObj* p2g, TmLegacySaveState* ss)
{
    Fighter* p1 = p1g->user_data;
    Fighter* p2 = p2g->user_data;
    HSD_PadStatus* pad = &HSD_PadGameStatus[LG_U8(p1, LG_FT_PORT)];
    HSD_GObj* sub;
    Fighter* sub_fp;
    f32 x, y;
    int ground;

    if (LG_S32(p1, LG_FT_STATE) != LG_ASID_WAIT) {
        return;
    }
    if (!(pad->repeat & 0x4)) { /* D-pad down */
        return;
    }
    if (pad->button & ~(0x4 | 0x10)) { /* anything but D-pad down and Z */
        return;
    }
    if (LG_S32(p1, LG_FT_AIRBORNE) != 0 ||
        !tm_legacy_FindGroundNearPlayer(
            NULL,
            10.0F * LG_F32(p1, LG_FT_FACING) + LG_F32(p1, LG_FT_POS_X),
            LG_F32(p1, LG_FT_POS_Y), &x, &y, &ground))
    {
        tm_legacy_PlaySFX(0xAF);
        return;
    }
    LG_F32(p2, LG_FT_POS_X) = x;
    LG_F32(p2, LG_FT_POS_Y) = y;
    LG_S32(p2, LG_FT_GROUND_ID) = ground;
    LG_F32(p2, LG_FT_FACING) = -LG_F32(p1, LG_FT_FACING);
    MoveToGround(p2g, p2);

    sub = tm_legacy_CheckIfPlayerHasAFollower(p2g, &sub_fp);
    if (sub != NULL) {
        Fighter_Spawn(sub); /* so Nana's CPU knows where Popo is */
        LG_F32(sub_fp, LG_FT_POS_X) = LG_F32(p2, LG_FT_POS_X);
        LG_F32(sub_fp, LG_FT_POS_Y) = LG_F32(p2, LG_FT_POS_Y);
        LG_S32(sub_fp, LG_FT_GROUND_ID) = LG_S32(p2, LG_FT_GROUND_ID);
        LG_F32(sub_fp, LG_FT_FACING) = LG_F32(p2, LG_FT_FACING);
        MoveToGround(sub, sub_fp);
    }

    tm_legacy_SaveState_Save(ss, true);
    tm_legacy_PlaySFX(0xDD);
}

int tm_legacy_AdjustResetDistance(TmLegacySaveState* ss, Fighter* p1,
                                  Fighter* p2)
{
    u16 held = LG_U16(p1, 0x662);
    u32 dpad = LG_U32(p1, 0x668);
    u8* b1 = ss->backup[0][0];
    u8* b2 = ss->backup[1][0];
    f32 dir, x1, x2, dist;

    if (!(held & 0x10) && held != 0) { /* something besides Z held */
        return -1;
    }
    dir = tm_legacy_GetDirectionInRelationToP1(p1, p2);
    if (dpad & 2) { /* apart */
        x1 = -dir + LG_F32(b1, LG_FT_POS_X);
        x2 = dir + LG_F32(b2, LG_FT_POS_X);
    } else if (dpad & 1) { /* together, no closer than 10 */
        x1 = dir + LG_F32(b1, LG_FT_POS_X);
        x2 = -dir + LG_F32(b2, LG_FT_POS_X);
        dist = x1 - x2;
        if (dist < 0.0F) {
            dist = -dist;
        }
        if (dist <= 10.0F) {
            return -1;
        }
    } else {
        return -1;
    }
    LG_F32(b1, LG_FT_POS_X) = x1;
    LG_F32(b2, LG_FT_POS_X) = x2;
    return 1;
}
