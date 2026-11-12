/**
 * @file
 * Legacy event player and stage helpers: GetAllPlayerPointers,
 * CheckIfPlayerHasAFollower, UpdateAllGFX, GiveInvincibility,
 * GiveFullShields, StoreCPUTypeAndZeroInputs, ClearNanaInputs,
 * CurrentInputsAsLastFramesInputs, InitializePositions,
 * GetDirectionInRelationToP1, IsAnyoneDead, ResetStaleMoves,
 * CheckForActiveHitboxes, PerformAerialThink, RandFloat,
 * Custom_InterruptRebirthWait, UpdatePosition, GetGroundCenter,
 * StageGetGroundID_*, PlacePlayersCenterStage, FindGround*,
 * PlacePlayerOnGround, PlaySFX, UpdateCameraBox, RemoveFirstFrameInputs,
 * GetDistance, GetLedgeCoordinates, EnterKnockback, PlaybackInputSequence,
 * PlaceOnLedge, GetInputStruct and ConvertAngle from
 * ../TrainingMode/ASM/training-mode/Custom Events/
 * Custom Event Code - Rewrite.asm. See legacy.h.
 */
#include "legacy.h"

#include <math.h>
#include <melee/cm/camera.h>
#include <melee/ft/fighter.h>
#include <melee/ft/ftcamera.h>
#include <melee/ft/ftcliffcommon.h>
#include <melee/ft/ftcoll.h>
#include <melee/ft/ftcommon.h>
#include <melee/ft/inlines.h>
#include <melee/ft/types.h>
#include <melee/gr/ground.h>
#include <melee/lb/lb_00B0.h>
#include <melee/mp/mpcoll.h>
#include <melee/mp/mplib.h>
#include <melee/mp/types.h>
#include <melee/pl/player.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/random.h>

/// Vanilla statics with unique names (resolved by the overlay linker).
extern CollLine* groundCollLine; ///< -0x51E4(r13)
extern CollVtx* groundCollVtx;   ///< -0x51E8(r13)
extern u8 ftMapping_list[];      ///< pdLoadCommonData, 3 bytes per char
extern ftCommonData* p_ftCommonData;

/// Functions the decomp declares in headers this file does not include.
void ftCo_800C0408(HSD_GObj* gobj);
void ftCo_800D4F24(HSD_GObj* gobj, int index);
void ftCo_Fall_Enter(HSD_GObj* gobj);
bool ftCo_800CB870(HSD_GObj* gobj);
void ftCo_8009A804(HSD_GObj* gobj);
void ftCo_CliffCatch_Phys(HSD_GObj* gobj);
void ft_8008A2BC(HSD_GObj* gobj);
void ft_80084280(HSD_GObj* gobj);
void Ground_801C53EC(u32 sfx);
void Camera_8002F3AC(void);
void ftCamera_UpdateCameraBox(HSD_GObj* gobj);
f32 cosf(f32);
f32 sinf(f32);

#define LG_COMMON ((u8*) p_ftCommonData)

void tm_legacy_GetAllPlayerPointers(HSD_GObj* gobj[4], Fighter* fp[4])
{
    int i;
    for (i = 0; i < 4; i++) {
        gobj[i] = Player_GetEntity(i);
        fp[i] = gobj[i] != NULL ? gobj[i]->user_data : NULL;
    }
}

HSD_GObj* tm_legacy_CheckIfPlayerHasAFollower(HSD_GObj* gobj, Fighter** fp)
{
    Fighter* main_fp = gobj->user_data;
    HSD_GObj* sub;
    Fighter* sub_fp;

    /* the asm passes the slot as the player number */
    if (tm_legacy_SaveState_GetPlayerDataPointer(LG_U8(main_fp, LG_FT_SLOT),
                                                 true, &sub, &sub_fp) == 0xFF)
    {
        goto none;
    }
    /* a sub-fighter is a follower unless the character transforms */
    if (ftMapping_list[Player_GetPlayerCharacter(LG_U8(sub_fp, LG_FT_SLOT)) *
                           3 +
                       2] != 0)
    {
        goto none;
    }
    *fp = sub_fp;
    return sub;

none:
    *fp = NULL;
    return NULL;
}

void tm_legacy_UpdateAllGFX(HSD_GObj* gobj)
{
    Fighter* fp;
    HSD_GObj* sub;

    ftCo_800C0408(gobj);
    sub = tm_legacy_CheckIfPlayerHasAFollower(gobj, &fp);
    if (sub != NULL) {
        ftCo_800C0408(sub);
    }
}

void tm_legacy_GiveInvincibility(HSD_GObj* gobj, int frames)
{
    Fighter* fp;
    HSD_GObj* sub;

    ftColl_8007B7A4(gobj, frames);
    sub = tm_legacy_CheckIfPlayerHasAFollower(gobj, &fp);
    if (sub != NULL) {
        ftColl_8007B7A4(sub, frames);
    }
}

void tm_legacy_GiveFullShields(void)
{
    HSD_GObj* g;
    for (g = HSD_GObjPLinkHead[8]; g != NULL; g = g->next) {
        LG_F32(g->user_data, 0x1998) = LG_F32(LG_COMMON, 0x260);
    }
}

void tm_legacy_StoreCPUTypeAndZeroInputs(Fighter* p2)
{
    LG_U32(p2, 0x1A88) = 0;
    LG_U32(p2, 0x1A8C) = 0;
    LG_U16(p2, 0x1A90) = 0;
}

void tm_legacy_ClearNanaInputs(HSD_GObj* p1, HSD_GObj* p2)
{
    Fighter* fp;

    if (tm_legacy_CheckIfPlayerHasAFollower(p1, &fp) != NULL) {
        LG_U32(fp, 0x1A88) = 0;
        LG_U32(fp, 0x1A8C) = 0;
    }
    if (tm_legacy_CheckIfPlayerHasAFollower(p2, &fp) != NULL) {
        LG_U32(fp, 0x1A88) = 0;
        LG_U32(fp, 0x1A8C) = 0;
    }
}

void tm_legacy_CurrentInputsAsLastFramesInputs(Fighter* p1)
{
    /* the asm reads port 0 (InputStructStart), whatever P1's port */
    u32 v = HSD_PadGameStatus[0].button;
    LG_U32(p1, 0x65C) = v;
    LG_U32(p1, 0x664) = v;
    if (v & 0x10) { /* Z */
        v |= 0x80000000 | 0x100;
        LG_U32(p1, 0x65C) = v;
        LG_U32(p1, 0x664) = v;
    }
}

/// Wait at (x, y), then update the ECB and camera (InitializePositions).
static void PlaceAt(HSD_GObj* g, f32 x, f32 y)
{
    Fighter* fp = g->user_data;
    ft_8008A2BC(g); /* AS_Wait */
    LG_F32(fp, LG_FT_POS_X) = x;
    LG_F32(fp, LG_FT_POS_Y) = y;
    tm_legacy_UpdatePosition(g);
    tm_legacy_UpdateCameraBox(g);
}

void tm_legacy_InitializePositions(const f32* xy, HSD_GObj* p1, HSD_GObj* p2)
{
    Fighter* fp;
    HSD_GObj* sub;

    PlaceAt(p1, xy[0], xy[2]);
    sub = tm_legacy_CheckIfPlayerHasAFollower(p1, &fp);
    if (sub != NULL) {
        PlaceAt(sub, xy[0], xy[2]);
    }
    PlaceAt(p2, xy[1], xy[3]);
    sub = tm_legacy_CheckIfPlayerHasAFollower(p2, &fp);
    if (sub != NULL) {
        PlaceAt(sub, xy[1], xy[3]);
    }
    tm_legacy_ClearNanaInputs(p1, p2);
    tm_legacy_CurrentInputsAsLastFramesInputs(p1->user_data);
}

int tm_legacy_GetDirectionInRelationToP1(Fighter* p1, Fighter* p2)
{
    if (0.0F < LG_F32(p1, LG_FT_POS_X) - LG_F32(p2, LG_FT_POS_X)) {
        return -1;
    }
    return 1;
}

bool tm_legacy_IsAnyoneDead(void)
{
    HSD_GObj* g;
    for (g = HSD_GObjPLinkHead[8]; g != NULL; g = g->next) {
        u8 flags = LG_U8(g->user_data, LG_FT_FLAGS_221F);
        if (flags & 0x08) { /* follower */
            continue;
        }
        if (flags & 0x40) { /* dead */
            return true;
        }
    }
    return false;
}

void tm_legacy_ResetStaleMoves(void)
{
    HSD_GObj* g;
    for (g = HSD_GObjPLinkHead[8]; g != NULL; g = g->next) {
        memzero(Player_GetStaleMoveTableIndexPtr(
                    LG_U8(g->user_data, LG_FT_SLOT)),
                0x2C);
    }
}

bool tm_legacy_CheckForActiveHitboxes(HSD_GObj* gobj)
{
    u8* fp = gobj->user_data;
    int i;
    for (i = 0; i < 4; i++) {
        if (LG_U32(fp + i * 312, 0x914) != 0) {
            return true;
        }
    }
    return false;
}

/// PerformAerial_FrameData: per character (internal id), {first, last}
/// frame to attack on for fair, nair, dair, uair, bair (and a pad pair).
static const u8 PerformAerial_FrameData[27][12] = {
    { 0x00, 0x04, 0x00, 0x12, 0x00, 0x10, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Mario */
    { 0x00, 0x09, 0x00, 0x0A, 0x00, 0x08, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Fox */
    { 0x00, 0x06, 0x00, 0x0E, 0x00, 0x04, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Falcon */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* DK */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Kirby */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Bowser */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Link */
    { 0x10, 0x14, 0x00, 0x18, 0x00, 0x00, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Sheik */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Ness */
    { 0x00, 0x0D, 0x00, 0x1A, 0x00, 0x0E, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Peach */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Popo */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Nana */
    { 0x00, 0x0C, 0x00, 0x0F, 0x00, 0x08, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Pikachu */
    { 0x00, 0x20, 0x00, 0x20, 0x08, 0x0D, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Samus */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Yoshi */
    { 0x00, 0x10, 0x00, 0x10, 0x00, 0x10, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Jigglypuff */
    { 0x00, 0x05, 0x00, 0x19, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Mewtwo */
    { 0x00, 0x17, 0x00, 0x1B, 0x00, 0x11, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Luigi */
    { 0x00, 0x16, 0x00, 0x13, 0x00, 0x12, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Marth */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Zelda */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Young Link */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Dr. Mario */
    { 0x07, 0x0B, 0x00, 0x0D, 0x00, 0x0C, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Falco */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Pichu */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Game & Watch */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Ganondorf */
    { 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0xFF, 0xFF }, /* Roy */
};

void tm_legacy_PerformAerialThink(HSD_GObj* gobj, u8* vars, int attack)
{
    Fighter* fp = gobj->user_data;
    int frame = (int) LG_F32(fp, LG_FT_ANIM_FRAME);
    int state;

    if (vars[0] != 0) { /* sequence over */
        return;
    }
    state = LG_S32(fp, LG_FT_STATE);

    if (state == 0xE) { /* Wait: jump, then pick the attack and frame */
        const u8* move;
        LG_U32(fp, LG_FT_CPU_BUTTONS) = 0x800;
        if (attack == 0) {
            goto random;
        }
        vars[1] = attack - 1;
        for (;;) {
            move = &PerformAerial_FrameData[LG_S32(fp, 0x4)][vars[1] * 2];
            if (move[0] != 0 || move[1] != 0) {
                break;
            }
        random: /* disabled for this character: pick another */
            vars[1] = HSD_Randi(3);
        }
        vars[2] = HSD_Randi(move[1] - move[0]) + move[0];
        return;
    }

    if (state == 0x19 || state == 0x1A) { /* jump */
        if (vars[2] == frame) {
            switch (vars[1]) {
            case 1: /* nair */
                LG_U32(fp, LG_FT_CPU_BUTTONS) = 0x100;
                break;
            case 2: /* dair */
                LG_S8(fp, LG_FT_CPU_CSTICK_Y) = -127;
                break;
            default: /* fair */
                LG_S8(fp, LG_FT_CPU_CSTICK_X) =
                    127 * (int) LG_F32(fp, LG_FT_FACING);
                break;
            }
        }
    } else if (state >= 0x41 && state <= 0x45) { /* attacking */
    } else if (state == 0x2A || (state >= 0x46 && state <= 0x4A)) {
        vars[0] = 1; /* landed: sequence over */
        return;
    } else {
        return;
    }

    /* fastfall (unless already, rising or about to nair) and L-cancel */
    if (!(LG_U8(fp, 0x221A) & 0x08) && LG_F32(fp, LG_FT_VEL_Y) < 0.0F &&
        LG_U32(fp, LG_FT_CPU_BUTTONS) != 0x100)
    {
        LG_S8(fp, LG_FT_CPU_ANALOG_Y) = -127;
    }
    LG_U8(fp, 0x67F) = 1; /* spoof mashing L */
}

f32 tm_legacy_RandFloat(int lo, int hi)
{
    f32 base = (f32) (HSD_Randi(hi - lo) + lo);
    return HSD_Randf() + base;
}

void tm_legacy_Custom_InterruptRebirthWait(HSD_GObj* gobj)
{
    Fighter* fp = gobj->user_data;
    f32 x;

    if (ftCo_800CB870(gobj)) { /* aerial jump */
        return;
    }
    if (LG_U8(fp, 0x670) < 2) { /* stick X just moved */
        x = LG_F32(fp, 0x620);
        if (x < 0.0F) {
            x = -x;
        }
        if (x >= LG_F32(LG_COMMON, 0x24)) {
            goto fall;
        }
    }
    if (LG_U8(fp, 0x671) < 4 && /* stick Y just moved down */
        LG_F32(fp, 0x624) < -LG_F32(LG_COMMON, 0x90))
    {
        goto fall;
    }
    return;
fall:
    ftCo_Fall_Enter(gobj);
}

void tm_legacy_UpdatePosition(HSD_GObj* gobj)
{
    u8* fp = gobj->user_data;
    u32 x = LG_U32(fp, LG_FT_POS_X);
    u32 y = LG_U32(fp, LG_FT_POS_Y);
    u32 z = LG_U32(fp, LG_FT_POS_Z);
    u8* jobj = gobj->hsd_obj;

    /* physics position into every ECB position */
    LG_U32(fp, 0x6F4) = x;
    LG_U32(fp, 0x700) = x;
    LG_U32(fp, 0x70C) = x;
    LG_U32(fp, 0x718) = x;
    LG_U32(fp, 0x6F8) = y;
    LG_U32(fp, 0x704) = y;
    LG_U32(fp, 0x710) = y;
    LG_U32(fp, 0x71C) = y;
    LG_U32(fp, 0x6FC) = z;
    LG_U32(fp, 0x708) = z;
    LG_U32(fp, 0x714) = z;
    LG_U32(fp, 0x720) = z;
    LG_S32(fp, 0x728) = mpColl_804D64AC; /* collision frame id */

    /* model position (as at 8006C324) */
    LG_U32(jobj, 0x38) = x;
    LG_U32(jobj, 0x3C) = y;
    LG_U32(jobj, 0x40) = z;

    Player_80032828(LG_U8(fp, LG_FT_SLOT),
                    (LG_U8(fp, LG_FT_FLAGS_221F) >> 3) & 1,
                    (Vec3*) (fp + LG_FT_POS_X));
}

void tm_legacy_GetGroundCenter(int ground_id, f32* x, f32* y)
{
    MapLine* line = groundCollLine[ground_id].inner;
    CollVtx* v0 = &groundCollVtx[line->v0_idx];
    CollVtx* v1 = &groundCollVtx[line->v1_idx];
    *x = (v0->pos.x + v1->pos.x) / 2.0F;
    *y = (v0->pos.y + v1->pos.y) / 2.0F;
}

/// StageGroundIDs_Main / _Platform (in the Combo Training asm), by stage.
static const u16 StageGroundIDs_Main[34] = {
    0xFFFF, 0xFFFF, 0x0005, 0x0022, 0x0005, 0x0037, 0x000B, 0x0012,
    0x0003, 0x0019, 0x0000, 0x0048, 0x0000, 0x0024, 0x0019, 0x0007,
    0x000E, 0x0026, 0x0004, 0x0003, 0x0004, 0x0000, 0x0001, 0x0105,
    0x00D9, 0x015B, 0x0000, 0x0064, 0x0004, 0x0009, 0x000B, 0x0001,
    0x0001, 0x0000,
};
static const u16 StageGroundIDs_Platform[34] = {
    0xFFFF, 0xFFFF, 0x0002, 0x0023, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,
    0x0004, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,
    0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,
    0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0x0002, 0xFFFF, 0xFFFF, 0x0003,
    0xFFFF, 0xFFFF,
};
/// LedgeCliffIDs: left ledge line in the high byte, right in the low byte.
static const u16 LedgeCliffIDs[34] = {
    0xFFFF, 0xFFFF, 0x0307, 0x3336, 0x030D, 0x2945, 0x0511, 0x091A,
    0x0206, 0x1517, 0x0000, 0x434C, 0x0000, 0x0000, 0x0E0D, 0x0000,
    0x0005, 0x1E2E, 0x0C0E, 0x0204, 0x0305, 0x0000, 0x0612, 0x0000,
    0xD7E2, 0x0000, 0x0000, 0x0000, 0x0305, 0x030B, 0x0610, 0x0005,
    0x0002, 0x0101,
};

int tm_legacy_StageGetGroundID_Main(void)
{
    return StageGroundIDs_Main[selected_stage.stkind];
}

int tm_legacy_StageGetGroundID_Platform(void)
{
    return StageGroundIDs_Platform[selected_stage.stkind];
}

/// PlacePlayersCenterStage_Constants: {facing, X offset} per slot. The asm
/// table has slots 0-1 only (later slots read the code after it); 0 here.
static const s8 CenterStageConstants[6][2] = {
    { 1, -6 }, { -1, 6 }, { 0, 0 }, { 0, 0 }, { 0, 0 }, { 0, 0 },
};

static void PlaceCenterStage(HSD_GObj* g, int ground_id)
{
    Fighter* fp = g->user_data;
    const s8* c = CenterStageConstants[LG_U8(fp, LG_FT_SLOT)];
    f32 cx, cy, x, y;
    int ground;

    Fighter_Spawn(g); /* so Nana knows where Popo is */
    tm_legacy_GetGroundCenter(ground_id, &cx, &cy);
    LG_F32(fp, LG_FT_FACING) = c[0];
    LG_F32(fp, LG_FT_POS_X) = (f32) c[1] + cx;
    LG_F32(fp, LG_FT_POS_Y) = cy;
    ft_8008A2BC(g); /* AS_Wait */
    if (tm_legacy_FindGroundNearPlayer(g, 0.0F, 0.0F, &x, &y, &ground)) {
        LG_F32(fp, LG_FT_POS_X) = x;
        LG_F32(fp, LG_FT_POS_Y) = y;
        LG_S32(fp, LG_FT_GROUND_ID) = ground;
    }
    tm_legacy_UpdatePosition(g);
    ft_80084280(g);
    ftCommon_8007D6A4(fp);
    tm_legacy_UpdateCameraBox(g);
}

void tm_legacy_PlacePlayersCenterStage(int ground_id)
{
    int i;
    for (i = 0; i < 6; i++) {
        HSD_GObj* g = Player_GetEntity(i);
        HSD_GObj* sub;
        Fighter* sub_fp;

        if (g == NULL) {
            continue;
        }
        sub = tm_legacy_CheckIfPlayerHasAFollower(g, &sub_fp);
        PlaceCenterStage(g, ground_id);
        if (sub != NULL) {
            PlaceCenterStage(sub, ground_id);
        }
    }
}

static bool CheckFloor(f32 ax, f32 ay, f32 bx, f32 by, f32* out_x,
                       f32* out_y, int* out_ground)
{
    Vec3 pos, normal;
    int line;
    u32 flags;

    if (!mpCheckFloor(ax, ay, bx, by, 0.0F, &pos, &line, &flags, &normal, -1,
                      -1, -1, NULL, NULL))
    {
        return false;
    }
    *out_x = pos.x;
    *out_y = pos.y;
    *out_ground = line;
    return true;
}

bool tm_legacy_FindGroundNearPlayer(HSD_GObj* gobj, f32 x, f32 y, f32* out_x,
                                    f32* out_y, int* out_ground)
{
    if (gobj == NULL) {
        /* from (x, y + 10) down to (x, y - 10) */
        return CheckFloor(x, y + 10.0F, x, y - 10.0F, out_x, out_y,
                          out_ground);
    } else {
        Fighter* fp = gobj->user_data;
        f32 px = LG_F32(fp, LG_FT_POS_X);
        f32 py = LG_F32(fp, LG_FT_POS_Y);
        /* TM-CE: the bottom Y is the player's X - 1000 (sic) */
        return CheckFloor(px, py + 10.0F, px, px - 1000.0F, out_x, out_y,
                          out_ground);
    }
}

bool tm_legacy_FindGroundUnderCoordinate(f32 x, f32 y, f32* out_x,
                                         f32* out_y, int* out_ground)
{
    return CheckFloor(x, y, x, y - 1000.0F, out_x, out_y, out_ground);
}

void tm_legacy_PlacePlayerOnGround(HSD_GObj* gobj)
{
    Fighter* fp = gobj->user_data;
    f32 x, y;
    int ground;

    if (tm_legacy_FindGroundNearPlayer(gobj, 0.0F, 0.0F, &x, &y, &ground)) {
        LG_F32(fp, LG_FT_POS_X) = x;
        LG_F32(fp, LG_FT_POS_Y) = y;
        LG_S32(fp, LG_FT_GROUND_ID) = ground;
    }
    tm_legacy_UpdatePosition(gobj);
    ft_80084280(gobj);
    ftCommon_8007D6A4(fp);
}

void tm_legacy_PlaySFX(int sfx)
{
    Ground_801C53EC(sfx);
}

void tm_legacy_UpdateCameraBox(HSD_GObj* gobj)
{
    u8* cambox = LG_PTR(gobj->user_data, LG_FT_CAMBOX);

    ftCamera_UpdateCameraBox(gobj);
    /* snap the box's direction tween */
    LG_F32(cambox, 0x2C) = LG_F32(cambox, 0x40);
    LG_F32(cambox, 0x30) = LG_F32(cambox, 0x44);
    Camera_8002F3AC();
}

void tm_legacy_RemoveFirstFrameInputs(void)
{
    HSD_GObj* g;
    for (g = HSD_GObjPLinkHead[8]; g != NULL; g = g->next) {
        u8* fp = g->user_data;
        LG_U8(fp, 0x221D) |= 0x10;
        LG_U32(fp, 0x65C) = HSD_PadGameStatus[LG_U8(fp, LG_FT_PORT)].button;
    }
}

f32 tm_legacy_GetDistance(const f32* a, const f32* b)
{
    f32 dx = b[0] - a[0];
    f32 dy = a[1] - b[1];
    f32 sq = dx * dx + dy * dy;
    /* frsqrte estimate, as the asm (not an exact sqrt) */
    return (f32) __frsqrte(sq) * sq;
}

void tm_legacy_GetLedgeCoordinates(int side, Vec3* out)
{
    u16 ids = LedgeCliffIDs[selected_stage.stkind];
    if (side == 0) {
        mpLib_80053ECC_Floor((ids >> 8) & 0xFF, out);
    } else {
        mpLib_80053DA4_Floor(ids & 0xFF, out);
    }
}

void tm_legacy_EnterKnockback(HSD_GObj* gobj, int angle_lo, int angle_hi,
                              int mag_lo, int mag_hi)
{
    Fighter* fp = gobj->user_data;
    f32 angle = (f32) (HSD_Randi(angle_hi - angle_lo) + angle_lo) *
                0.017453292F;
    f32 mag = tm_legacy_RandFloat(mag_lo, mag_hi);
    f32 kb = mag * LG_F32(LG_COMMON, 0x100);

    LG_F32(fp, 0x8C) = cosf(angle) * kb * -LG_F32(fp, LG_FT_FACING);
    LG_F32(fp, 0x90) = sinf(angle) * kb;
    /* hitstun frames = magnitude * 0.4, rounded down */
    LG_F32(fp, LG_FT_HITSTUN) = (f32) (int) (mag * LG_F32(LG_COMMON, 0x154));
    LG_U8(fp, 0x221C) |= 0x02;
    ftCommon_UnlockECB(fp);
}

void tm_legacy_PlaybackInputSequence(Fighter* fp, const u8* seq, int frame)
{
    for (;; seq += 9) {
        if ((s8) seq[0] == -1) {
            return;
        }
        if (frame == seq[0]) {
            break;
        }
        if (frame < seq[0]) {
            return;
        }
    }
    LG_U32(fp, LG_FT_CPU_BUTTONS) = (seq[1] << 24) | (seq[2] << 16) |
                                    (seq[3] << 8) | seq[4];
    LG_U8(fp, LG_FT_CPU_ANALOG_X) = seq[5];
    LG_U8(fp, LG_FT_CPU_ANALOG_Y) = seq[6];
    LG_U8(fp, LG_FT_CPU_CSTICK_X) = seq[7];
    LG_U8(fp, LG_FT_CPU_CSTICK_Y) = seq[8];
}

void tm_legacy_PlaceOnLedge(HSD_GObj* gobj, int side)
{
    Fighter* fp = gobj->user_data;
    u16 ids = LedgeCliffIDs[selected_stage.stkind];
    int ledge;

    if (side == 0) {
        ledge = (ids >> 8) & 0xFF;
        LG_F32(fp, LG_FT_FACING) = 1.0F;
    } else {
        ledge = ids & 0xFF;
        LG_F32(fp, LG_FT_FACING) = -1.0F;
    }
    LG_S32(fp, 0x2340) = ledge;
    ftCo_8009A804(gobj); /* AS_CliffWait */
    LG_S32(fp, 0x2348) = 1; /* as if a frame had passed */
    LG_S16(fp, LG_FT_TM_STATE_FRAMES) = 1;
    ftCommon_8007D5D4(fp); /* regain the jump, no ECB for 10 frames */
    ftCommon_UnlockECB(fp);
    mpColl_80048160((CollData*) ((u8*) fp + 0x6F0));
    ftCo_CliffCatch_Phys(gobj); /* move to the ledge */
    tm_legacy_UpdatePosition(gobj);
    LG_U32(fp, LG_FT_VEL_X) = 0;
    LG_U32(fp, LG_FT_VEL_Y) = 0;
    ftColl_8007B760(gobj, LG_S32(LG_COMMON, 0x49C)); /* intangibility */
}

void* tm_legacy_GetInputStruct(int port)
{
    return &HSD_PadGameStatus[port];
}

void tm_legacy_ConvertAngle(int angle, s32* x, s32* y)
{
    f32 rad = (f32) angle * 0.017453292F;
    s32 sx = (s32) (cosf(rad) * 127.0F);
    s32 sy = (s32) (sinf(rad) * 127.0F);

    if ((sx < 0 ? -sx : sx) < 36) {
        sx = 0;
    }
    if ((sy < 0 ? -sy : sy) < 36) {
        sy = 0;
    }
    *x = sx;
    *y = sy;
}
