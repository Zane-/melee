#ifndef MELEE_TM_OSDCORE_OSD_H
#define MELEE_TM_OSDCORE_OSD_H

#include <Runtime/platform.h>

#include <melee/ft/forward.h>
#include <sysdolphin/baselib/forward.h>

/**
 * @file
 * TM-CE on-screen display (OSD) foundation: the helpers TM-CE's OSD
 * assembly calls, for porting the remaining OSDs
 * (../TrainingMode/ASM/training-mode/Onscreen Display/) mechanically.
 *
 * How an OSD file maps onto this API:
 *
 * | asm | C |
 * |-|-|
 * | "CHECK IF ENABLED": `lwz r4,MemcardData(r13); lwz r4,0x1F24(r4)` + bit test | `tm_osd_IsEnabled(TM_OSD_x)` |
 * | `branchl r12, 0x80005510` (Check For ICs Static Function) | `tm_osd_IsFollower(fp)` |
 * | `Message_Display` macro (`crset 6; rtocbl r12, TM_MessageDisplay`): r3 kind, r4 queue (`lbz 0xC(fp)`), r5 MSGCOLOR_x, r6 format, r7.. args | `Message_Display(kind, queue, color, fmt, ...)` (TM-CE events.c) |
 * | after it: `lwz r3,0x2C(r3); lwz r3,MsgData_Text(r3)` | `tm_osd_MessageText(msg)` |
 * | `branchl r12, Text_ChangeTextColor` (r3 text, r4 subtext, r5 &color) | `HSD_SisLib_803A74F0` |
 * | `branchl r12, TextCreateFunction` (0x80005928, Display Message 2.0; only legacy events use it) | `tm_osd_TextCreate(...)` |
 * | `branchl r12, 0x8000551C` (Act OoWait static function) | `tm_osd_ActOoWait(gobj)` |
 * | FighterData.TM fields (TM_FramesinCurrentAS, TM_PrevASStart, TM_Inputs...) | MexTK `FighterData.TM` in src/tmce/*.c; kept up to date by this area |
 *
 * Fixed-address static functions that belong to single OSD folders (port
 * them with their folder; nothing in osdcore calls them):
 *
 * | address | file |
 * |-|-|
 * | 0x80005504 | Act OOTumble/Static Function - Display Frames Spent Post Hitstun.asm |
 * | 0x80005508 | Act OOS Frame Display/Display OOS Frame Count Standalone.asm |
 * | 0x8000550C | Act OoAirborne/Display Act OoAirborne Frame Count - Static Function.asm |
 * | 0x80005514 | Ledge Codes/GALINT/Standalaone - GALINT Display.asm |
 * | 0x80005518 | Dashback/Dashback Display - Static Function.asm |
 *
 * TM-CE state the assembly kept in vanilla memory is in C statics here: the
 * message areas (asm: HSD_MemAlloc'd block at un_804A1F58+4) and the insta
 * double jump table (asm: data inside its code). Statics are not saved by
 * Slippi rollback.
 */

/// OSD bit numbers in MemcardData+0x1F24 (TM-CE Globals.s `OSD.*`).
typedef enum TmOsdId {
    TM_OSD_WAVEDASH = 0,
    TM_OSD_LCANCEL = 1,
    TM_OSD_ACTOOS = 3,
    TM_OSD_DASHBACK = 5,
    TM_OSD_FIGHTERSPECIFICTECH = 8,
    TM_OSD_POWERSHIELD = 9,
    TM_OSD_SDI = 10,
    TM_OSD_LOCKOUTTIMERS = 12,
    TM_OSD_ROLLAIRDODGEINTERRUPT = 13,
    TM_OSD_BOOSTGRAB = 14,
    TM_OSD_MISCELLANEOUS = 15,
    TM_OSD_ACTOOWAIT = 16,
    TM_OSD_ACTOOAIRBORNE = 18,
    TM_OSD_ACTOOJUMPSQUAT = 19,
    TM_OSD_FASTFALL = 20,
    TM_OSD_FRAMEADVANTAGE = 21,
    TM_OSD_COMBOCOUNTER = 22,
    TM_OSD_GRABBREAKOUT = 24,
    TM_OSD_LEDGE = 26,
    TM_OSD_ACTOOHITSTUN = 28,
    /// Message ID only (not a toggle): never overwritten by FIGHTERSPECIFICTECH.
    TM_OSD_FIGHTERSPECIFICTECHALT = 64,
    /// Message ID only: always displays, never overwrites another OSD.
    TM_OSD_NULL = -1,
} TmOsdId;

/// Message colours (TM-CE `MSGCOLOR_*`, index into its colour table).
typedef enum TmMsgColor {
    TM_MSGCOLOR_WHITE = 0,
    TM_MSGCOLOR_GREEN = 1,
    TM_MSGCOLOR_RED = 2,
    TM_MSGCOLOR_YELLOW = 3,
} TmMsgColor;

/// Text colours the OSDs pass to Text_ChangeTextColor (RGBA).
#define TM_OSD_RGBA_GREEN 0x8DFF6EFF
#define TM_OSD_RGBA_RED 0xFFA2BAFF
#define TM_OSD_RGBA_WHITE 0xFFFFFFFF

/// "CHECK IF ENABLED": bit @p osd of MemcardData+0x1F24.
bool tm_osd_IsEnabled(int osd);

/// Check For ICs Static Function.asm (0x80005510). True for a sub-fighter
/// whose character does not transform: Nana. OSDs skip followers.
bool tm_osd_IsFollower(Fighter* fp);

/// TM-CE's message box (events.c Message_Display; the asm `Message_Display`
/// macro). @p kind is the OSD ID (TmOsdId; a newer message with the same
/// ID replaces the old one), @p queue the player slot (fp->player_idx),
/// @p color a TmMsgColor. Returns the message GObj.
HSD_GObj* Message_Display(int kind, int queue, int color, char* format, ...);

/// The text of a message returned by Message_Display (MsgData.text).
HSD_Text* tm_osd_MessageText(HSD_GObj* msg);

/// Display Message 2.0.asm (TextCreateFunction, 0x80005928), the older
/// per-player message windows legacy events use. @p area: 0 above the
/// player's HUD, 1 top of screen (both queue up to MemcardData+0x1F28
/// windows per player, newest first, replacing @p overlay_id), 2 the single
/// event popup. The window lives @p timer frames. Returns the text with one
/// subtext (the black background); callers add theirs.
HSD_Text* tm_osd_TextCreate(Fighter* fp, int timer, int area, int overlay_id);

/// Act OOWait- Standalone.asm (0x8000551C), for @p gobj (a fighter).
void tm_osd_ActOoWait(HSD_GObj* gobj);

#endif
