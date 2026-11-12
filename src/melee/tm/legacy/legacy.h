#ifndef MELEE_TM_LEGACY_LEGACY_H
#define MELEE_TM_LEGACY_LEGACY_H

#include <Runtime/platform.h>

#include <dolphin/mtx.h>
#include <melee/ft/forward.h>
#include <melee/gm/forward.h>
#include <melee/mn/forward.h>
#include <sysdolphin/baselib/forward.h>

/**
 * @file
 * TM-CE's assembly-only ("legacy") events, ported to C.
 *
 * Source: ../TrainingMode/ASM/training-mode/Custom Events/
 * Custom Event Code - Rewrite.asm (injected at onEnterVs+0x3B8). Lines
 * 1-133 dispatch; 134-8599 the 15 events; 8600-12371 the shared library
 * this header exposes. Functions are named after the asm labels
 * (`tm_legacy_<Label>`), take the registers the asm read implicitly as
 * explicit parameters, and keep the asm's raw fighter offsets (LG_FT_*).
 *
 * ## How an event runs
 *
 * 1. src/melee/tm/tm_event_start.c (event match setup, an edited copy of
 *    vanilla onEnterVs) sees a TM-CE event without a C file. It runs vanilla
 *    up to +0x3B8, then tm_legacy_Setup(), then the rest of vanilla
 *    onEnterVs (the player setup from the GmEvent.dat level entry, with the
 *    css/ess `word` patches of that code applied).
 * 2. tm_legacy_Setup() (asm "LegacyEvent") applies the common match changes,
 *    asks TM-CE (GetJumpTableOffset) which legacy event this is and calls its
 *    setup function from tm_legacy_events[] (asm EventJumpTable order,
 *    TM-CE events.h `enum JumpTableIndex`).
 * 3. The setup function ("<Event> HIJACK INFO" in the asm) edits the match
 *    (TmLegacySetup::md) and the level entry (TmLegacySetup::event), calls
 *    tm_legacy_InitializeMatch(), and stores its load function in
 *    md->rules.on_match_start (asm `stw r3, 0x44(r26)`).
 * 4. The load function ("<Event> LOAD FUNCT", runs at match start) calls
 *    StartOSDs() and tm_legacy_CreateEventThinkFunction() with its think
 *    function, priority and option menu.
 * 5. The think function ("<Event> THINK FUNCT") is a GObj proc. Its user
 *    data is the 0x50-byte event data block (LG_EVDATA_*); the savestate
 *    struct lives inside it at LG_EVDATA_SAVESTATE.
 *
 * ## Porting one event (recipe)
 *
 * - One file, src/melee/tm/legacy/events/<name>.c, replacing its stub;
 *   define `void tm_legacy_ev_<Name>(TmLegacySetup* s)` (already declared
 *   below and wired into tm_legacy_events[]).
 * - Port "HIJACK INFO", "LOAD FUNCT", "THINK FUNCT" and the event's own
 *   helpers as static functions; constants and `.set OFST_*` offsets as
 *   #defines; `blrl` data blocks (option text, floats) as static const data.
 * - asm register conventions: after `bl GetAllPlayerPointers` the asm keeps
 *   P1GObj/P1Data/P2GObj/P2Data in r28/r27/r30/r29 and library calls read
 *   them implicitly. Here they are parameters (see each function).
 * - `bl StageGetGroundID_Main` + `bl PlacePlayersCenterStage` =
 *   tm_legacy_PlacePlayersCenterStage(tm_legacy_StageGetGroundID_Main()).
 * - Message windows: `branchl r12, TextCreateFunction` = tm_osd_TextCreate()
 *   (src/melee/tm/osdcore/osd.h); `Text_InitializeSubtext` =
 *   HSD_SisLib_803A6B98, `Text_ChangeTextColor` = HSD_SisLib_803A74F0,
 *   `Text_UpdateSubtextSize` = HSD_SisLib_803A7548. `lfs fN, -0x37B4(rtoc)`
 *   is LG_TEXT_X (0.0), `-0x37B0(rtoc)` is LG_TEXT_LINE2_Y (40.0).
 * - Vanilla calls by TM-CE name: look the name up in ../TrainingMode/ASM/
 *   Globals.s, then `python tools/mex_symbols.py 0x<addr>` for the decomp
 *   name. `TM_FramesinCurrentAS(rN)` is LG_FT_TM_STATE_FRAMES, and
 *   `TM_GameFrameCounter(r13)` is tm_misc_game_frame_counter.
 * - Event state goes in the event data block (static per-event state the
 *   asm kept in its code area may be a C static).
 */

/* ---- raw access (the asm's offsets) ------------------------------------ */

#define LG_U8(p, off) (*(u8*) ((u8*) (p) + (off)))
#define LG_S8(p, off) (*(s8*) ((u8*) (p) + (off)))
#define LG_U16(p, off) (*(u16*) ((u8*) (p) + (off)))
#define LG_S16(p, off) (*(s16*) ((u8*) (p) + (off)))
#define LG_U32(p, off) (*(u32*) ((u8*) (p) + (off)))
#define LG_S32(p, off) (*(s32*) ((u8*) (p) + (off)))
#define LG_F32(p, off) (*(f32*) ((u8*) (p) + (off)))
#define LG_PTR(p, off) (*(void**) ((u8*) (p) + (off)))

/// Fighter (player data) offsets the asm uses.
#define LG_FT_SLOT 0x0C            ///< u8 player slot
#define LG_FT_STATE 0x10           ///< s32 action state (ASID_*)
#define LG_FT_FACING 0x2C          ///< f32 facing direction
#define LG_FT_VEL_X 0x80           ///< f32
#define LG_FT_VEL_Y 0x84           ///< f32
#define LG_FT_POS_X 0xB0           ///< f32
#define LG_FT_POS_Y 0xB4           ///< f32
#define LG_FT_POS_Z 0xB8           ///< f32
#define LG_FT_AIRBORNE 0xE0        ///< s32, 0 grounded
#define LG_FT_PORT 0x618           ///< u8 controller port
#define LG_FT_GROUND_ID 0x83C      ///< s32 ground line id
#define LG_FT_CAMBOX 0x890         ///< camera box pointer
#define LG_FT_ANIM_FRAME 0x894     ///< f32
#define LG_FT_ANIM_SPEED 0x89C     ///< f32
#define LG_FT_HITSTUN 0x2340       ///< f32 (also ledge id when on ledge)
#define LG_FT_CPU_BUTTONS 0x1A88   ///< u32 CPU_HeldButtons
#define LG_FT_CPU_ANALOG_X 0x1A8C  ///< s8 CPU_AnalogX
#define LG_FT_CPU_ANALOG_Y 0x1A8D  ///< s8 CPU_AnalogY
#define LG_FT_CPU_CSTICK_X 0x1A8E  ///< s8 CPU_CStickX
#define LG_FT_CPU_CSTICK_Y 0x1A8F  ///< s8 CPU_CStickY
#define LG_FT_FLAGS_221F 0x221F    ///< u8: 0x08 sub-fighter, 0x40 dead
/// TM-CE FighterData.TM (m-ex Header.s TM_*), past vanilla's 0x23EC.
#define LG_FT_TM_STATE_FRAMES 0x23F8 ///< s16 TM_FramesinCurrentAS
#define LG_FT_TM_SHIELD_FRAMES 0x23FA ///< s16 TM_ShieldFrames
#define LG_FT_TM_PREV_STATES 0x23FC  ///< u16[6] TM_PrevASStart (OneASAgo...)

#define LG_ASID_WAIT 0x0E

/// Event GObj data block (asm EventData_*), 0x50 bytes, zeroed.
#define LG_EVDATA_SIZE 0x50
#define LG_EVDATA_SAVESTATE 0x10 ///< TmLegacySaveState (6 slots x 2 ptrs)
#define LG_EVDATA_MENU 0x4C      ///< u8* menu data block, or NULL

/// Option menu GObj data block (asm MenuData_*), 0x50 bytes, zeroed.
#define LG_MENU_SIZE 0x50
#define LG_MENU_WINDOW_INFO 0x00 ///< const u8*: [count-1, max0, max1, ...]
#define LG_MENU_ASCII 0x04       ///< const char*: title\0opt\0opt\0title...
#define LG_MENU_MEMORY 0x08      ///< u8[]: cursor, scroll, selection[n]
#define LG_MENU_TOGGLED 0x28     ///< u8[]: set when option n was changed
#define LG_MENU_EVDATA 0x4C      ///< u8* event data block

/// Selected value of option @p n of an event's menu.
#define LG_MENU_OPTION(menu, n) LG_U8(menu, LG_MENU_MEMORY + 2 + (n))
/// Toggled flag of option @p n (cleared by tm_legacy_ClearToggledOptions).
#define LG_MENU_IS_TOGGLED(menu, n) LG_U8(menu, LG_MENU_TOGGLED + (n))

/// Vanilla save data (0x8045A6C0; MemcardData(r13) points at it).
extern u8 gmMainLib_8045A6C0[];
/// asm `lwz rN, MemcardData(r13)`: TM-CE settings live at +0x1F24...
#define LG_MEMCARD (gmMainLib_8045A6C0)
/// asm `load rN, 0x8045abf0`: the current event info (event id at +5,
/// score behaviour byte at +0xB: bit 0x02 = timed score).
#define LG_EVENT_INFO (gmMainLib_8045A6C0 + 0x530)

/// gr/stage.c `selected_stage` (struct StageSelection is private there):
/// the asm's `lwz rN, StageID_External(r13)`, the internal stage kind.
typedef struct TmLegacyStageSelection {
    s32 stkind;
    void* entry;
} TmLegacyStageSelection;
extern TmLegacyStageSelection selected_stage;

/// rtoc floats the asm loads for text placement.
#define LG_TEXT_X 0.0F       ///< -0x37B4(rtoc), default subtext X/Y
#define LG_TEXT_LINE2_Y 40.0F ///< -0x37B0(rtoc), second line Y

/* ---- dispatch ----------------------------------------------------------- */

typedef struct TmLegacySetup {
    /// The event's GmEvent.dat level entry (asm `lwz r9, 0(r29)`).
    struct gm_804D6900_t* event;
    StartMeleeData* md; ///< asm r26
    int event_id;       ///< asm r25, the event index on its page
    int page;           ///< MemcardData+0x1F29
} TmLegacySetup;

typedef void (*TmLegacySetupFunc)(TmLegacySetup* s);

/// Number of entries in TM-CE's EventJumpTable.
#define TM_LEGACY_EVENT_COUNT 15

/// Setup functions in EventJumpTable order (TM-CE `enum JumpTableIndex`).
extern TmLegacySetupFunc const tm_legacy_events[TM_LEGACY_EVENT_COUNT];

/// asm "LegacyEvent" (lines 22-123). Returns false if TM-CE has no legacy
/// event at (page, event_id) ("EventNoExist"); the common changes are
/// applied either way, as in the asm.
bool tm_legacy_Setup(TmLegacySetup* s);

/// The 15 setup functions (src/melee/tm/legacy/events/*.c).
void tm_legacy_ev_AmsahTech(TmLegacySetup* s);
void tm_legacy_ev_AttackOnShield(TmLegacySetup* s);
void tm_legacy_ev_ComboTraining(TmLegacySetup* s);
void tm_legacy_ev_EscapeSheik(TmLegacySetup* s);
void tm_legacy_ev_GrabMashOut(TmLegacySetup* s);
void tm_legacy_ev_LedgeStall(TmLegacySetup* s);
void tm_legacy_ev_Ledgetech(TmLegacySetup* s);
void tm_legacy_ev_LedgetechCounter(TmLegacySetup* s);
void tm_legacy_ev_Multishine(TmLegacySetup* s);
void tm_legacy_ev_Reaction(TmLegacySetup* s);
void tm_legacy_ev_Reversal(TmLegacySetup* s);
void tm_legacy_ev_SDITraining(TmLegacySetup* s);
void tm_legacy_ev_ShieldDrop(TmLegacySetup* s);
void tm_legacy_ev_SlideOff(TmLegacySetup* s);
void tm_legacy_ev_WaveshineSDI(TmLegacySetup* s);

/* ---- match setup (legacy_core.c) ---------------------------------------- */

/// asm InitializeMatch: 2 players (P2 from a heap copy of P2Struct),
/// @p cpu_kind (external id, -1 = the CSS's CPU, Zelda becomes Sheik),
/// @p stage (-1 = the CSS's stage), OR @p osds into the OSD toggles unless
/// TM_OSDRecommended (0x1F2A) is 1, and Sopo for Ice Climbers if
/// @p use_sopo. @p event is TmLegacySetup::event.
void tm_legacy_InitializeMatch(struct gm_804D6900_t* event,
                               StartMeleeData* md, int cpu_kind, int stage,
                               u32 osds, bool use_sopo);

/// TM-CE events.c: the OSD think GObj (asm `rtocbl r12, TM_StartOSDs`).
void StartOSDs(void);

/// asm CreateEventThinkFunction: event GObj with @p think at @p priority
/// and a zeroed 0x50-byte data block; if @p window_info is not NULL, the
/// pause option menu GObj (OptionMenuThink); then DisableHazards. Returns
/// the event GObj.
HSD_GObj* tm_legacy_CreateEventThinkFunction(void (*think)(HSD_GObj*),
                                             int priority,
                                             const u8* window_info,
                                             const char* ascii);

/// asm ClearToggledOptions (r3 = menu data block).
void tm_legacy_ClearToggledOptions(u8* menu);

/// asm InitializeHighScore: KO counter HUD, score = 0, and the exit
/// function that saves the high score (Event_ExitFunction).
void tm_legacy_InitializeHighScore(void);

/// asm CheckIfFirstFrame: TM_GameFrameCounter == 1.
bool tm_legacy_CheckIfFirstFrame(void);

/// asm DisableHazards (per-stage hazard removal, for the selected stage).
void tm_legacy_DisableHazards(void);

/// misc area (src/melee/tm/misc/misc_match.c): TM_GameFrameCounter.
extern int tm_misc_game_frame_counter;

/* ---- savestates (legacy_state.c) ----------------------------------------- */

/// The asm savestate struct: per player number (spawn order), main and
/// sub-fighter backups (HSD_MemAlloc'd player block + 0x100 of the static
/// player block + camera flag).
typedef struct TmLegacySaveState {
    void* backup[6][2];
} TmLegacySaveState;

/// asm SaveState_Save. Unless @p skip_failsafe, refuses (error SFX twice)
/// while anyone has an on-death callback, holds an item or has a respawn
/// platform.
void tm_legacy_SaveState_Save(TmLegacySaveState* ss, bool skip_failsafe);
/// asm SaveState_Load.
void tm_legacy_SaveState_Load(TmLegacySaveState* ss);
/// asm SaveState_GetPlayerDataPointer: player number @p n (spawn order),
/// main or @p sub fighter. Returns the slot, or 0xFF if absent; fills
/// @p gobj and @p fp when present.
int tm_legacy_SaveState_GetPlayerDataPointer(int n, bool sub,
                                             HSD_GObj** gobj, Fighter** fp);
/// asm CheckForSaveAndLoad: D-pad right saves, left loads (twice), for any
/// port with nothing else held. Returns 0 saved, 1 loaded, or the last
/// value otherwise (the asm leaves r3 = 4); here -1 when nothing happened.
int tm_legacy_CheckForSaveAndLoad(TmLegacySaveState* ss);
/// asm DPadCPUPercent: holding L, D-pad changes P2's percent (+-1, +-10)
/// live and in its backup. @p pair is P2's {main, sub} backups: pass
/// ss->backup[1], as Combo Training does (EventData_SaveStateStruct + 8).
void tm_legacy_DPadCPUPercent(void** pair);
/// asm Randomize_LeftorRightSide (r31 = event data block).
void tm_legacy_Randomize_LeftorRightSide(u8* evdata, bool opposing);
/// asm MoveCPU: D-pad down with P1 in Wait moves P2 in front of P1, then
/// saves.
void tm_legacy_MoveCPU(HSD_GObj* p1, HSD_GObj* p2, TmLegacySaveState* ss);
/// asm AdjustResetDistance (r27 = P1 data, r29 = P2 data): D-pad
/// right/left move the saved positions apart/together. Returns 1 if changed,
/// -1 if not.
int tm_legacy_AdjustResetDistance(TmLegacySaveState* ss, Fighter* p1,
                                  Fighter* p2);

/* ---- players and stage (legacy_util.c) ------------------------------------ */

/// asm GetAllPlayerPointers: GObj and data of slots 0-3 (NULL if absent).
void tm_legacy_GetAllPlayerPointers(HSD_GObj* gobj[4], Fighter* fp[4]);
/// asm CheckIfPlayerHasAFollower: Nana for @p gobj's slot, or NULL.
HSD_GObj* tm_legacy_CheckIfPlayerHasAFollower(HSD_GObj* gobj, Fighter** fp);
/// asm UpdateAllGFX (r30 = gobj).
void tm_legacy_UpdateAllGFX(HSD_GObj* gobj);
/// asm GiveInvincibility (also the follower).
void tm_legacy_GiveInvincibility(HSD_GObj* gobj, int frames);
/// asm GiveFullShields (every fighter).
void tm_legacy_GiveFullShields(void);
/// asm StoreCPUTypeAndZeroInputs (r29 = P2 data): clear CPU inputs.
void tm_legacy_StoreCPUTypeAndZeroInputs(Fighter* p2);
/// asm ClearNanaInputs (r28 = P1 GObj, r30 = P2 GObj).
void tm_legacy_ClearNanaInputs(HSD_GObj* p1, HSD_GObj* p2);
/// asm CurrentInputsAsLastFramesInputs (r27 = P1 data).
void tm_legacy_CurrentInputsAsLastFramesInputs(Fighter* p1);
/// asm InitializePositions (r3 = {P1 X, P2 X, P1 Y, P2 Y}; r28/r27 P1,
/// r30/r29 P2).
void tm_legacy_InitializePositions(const f32* xy, HSD_GObj* p1,
                                   HSD_GObj* p2);
/// asm GetDirectionInRelationToP1 (r27 = P1 data, r29 = P2 data): 1 if
/// P1.x - P2.x <= 0, else -1.
int tm_legacy_GetDirectionInRelationToP1(Fighter* p1, Fighter* p2);
/// asm IsAnyoneDead (main fighters only).
bool tm_legacy_IsAnyoneDead(void);
/// asm ResetStaleMoves (every fighter).
void tm_legacy_ResetStaleMoves(void);
/// asm CheckForActiveHitboxes.
bool tm_legacy_CheckForActiveHitboxes(HSD_GObj* gobj);
/// asm PerformAerialThink: CPU jumps and does @p attack (0 random, 1 fair,
/// 2 nair, 3 dair) with fastfall and L-cancel; @p vars is 3 bytes of state
/// (performAerial, aerialAttack, attackFrame).
void tm_legacy_PerformAerialThink(HSD_GObj* gobj, u8* vars, int attack);
/// asm RandFloat: random float in [lo, hi + 1).
f32 tm_legacy_RandFloat(int lo, int hi);
/// asm Custom_InterruptRebirthWait (a fighter IASA callback).
void tm_legacy_Custom_InterruptRebirthWait(HSD_GObj* gobj);
/// asm UpdatePosition: copy the position into the ECB, model and static
/// player block.
void tm_legacy_UpdatePosition(HSD_GObj* gobj);
/// asm GetGroundCenter.
void tm_legacy_GetGroundCenter(int ground_id, f32* x, f32* y);
/// asm StageGetGroundID_Main / _Platform (Combo Training's tables; used by
/// several events). -1 (0xFFFF) for none.
int tm_legacy_StageGetGroundID_Main(void);
int tm_legacy_StageGetGroundID_Platform(void);
/// asm PlacePlayersCenterStage.
void tm_legacy_PlacePlayersCenterStage(int ground_id);
/// asm FindGroundNearPlayer: from @p gobj, or from (@p x, @p y) if @p gobj
/// is NULL. Returns true and the ground point and line id if found.
bool tm_legacy_FindGroundNearPlayer(HSD_GObj* gobj, f32 x, f32 y, f32* out_x,
                                    f32* out_y, int* out_ground);
/// asm FindGroundUnderCoordinate.
bool tm_legacy_FindGroundUnderCoordinate(f32 x, f32 y, f32* out_x,
                                         f32* out_y, int* out_ground);
/// asm PlacePlayerOnGround.
void tm_legacy_PlacePlayerOnGround(HSD_GObj* gobj);
/// asm PlaySFX.
void tm_legacy_PlaySFX(int sfx);
/// asm UpdateCameraBox.
void tm_legacy_UpdateCameraBox(HSD_GObj* gobj);
/// asm RemoveFirstFrameInputs.
void tm_legacy_RemoveFirstFrameInputs(void);
/// asm GetDistance (between two Vec2-like f32 pairs).
f32 tm_legacy_GetDistance(const f32* a, const f32* b);
/// asm GetLedgeCoordinates: @p side 0 left, 1 right.
void tm_legacy_GetLedgeCoordinates(int side, Vec3* out);
/// asm EnterKnockback: random angle/magnitude knockback with hitstun.
void tm_legacy_EnterKnockback(HSD_GObj* gobj, int angle_lo, int angle_hi,
                              int mag_lo, int mag_hi);
/// asm PlaybackInputSequence: 9-byte records {frame, buttons(4), analog
/// x/y, cstick x/y}, terminated by frame 0xFF; plays the record for
/// @p frame into the CPU inputs.
void tm_legacy_PlaybackInputSequence(Fighter* fp, const u8* seq, int frame);
/// asm PlaceOnLedge: @p side 0 left, 1 right.
void tm_legacy_PlaceOnLedge(HSD_GObj* gobj, int side);
/// asm GetInputStruct: HSD_PadGameStatus[@p port] (asm InputStructStart).
void* tm_legacy_GetInputStruct(int port);
/// asm ComboTrainingDecideStickAngle_ConvertAngle: stick X/Y (-127..127,
/// deadzone 36 clamped to 0) for @p angle degrees.
void tm_legacy_ConvertAngle(int angle, s32* x, s32* y);

#endif
