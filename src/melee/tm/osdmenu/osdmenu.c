/**
 * @file
 * Port of TM-CE's ASM/training-mode/Onscreen Display/Toggle UI/: the OSD
 * toggle menu. TM-CE reuses the rules menu's random stage select screen
 * (mn/mnstagesw.c): each stage row toggles one OSD bit in the save data
 * (MemcardData+0x1F24), and two extra texts replace the stage names.
 *
 * Entry: L on the VS rules menu (tm_osdmenu_RulesButtons) or on the event
 * select screen (src/melee/tm/ess/ess.c). Leaving goes back where it came
 * from. See osdmenu.h for the entering_menu values that mark OSD mode.
 */
#include "osdmenu.h"

#include <melee/gm/forward.h>
#include <melee/gm/gm_1601.h>
#include <melee/gm/gm_1A36.h>
#include <melee/gm/gm_1A3F.h>
#include <melee/gm/gmmain_lib.h>
#include <melee/gm/types.h>
#include <melee/lb/lbaudio_ax.h>
#include <melee/lb/lbcardgame.h>
#include <melee/lb/lbspdisplay.h>
#include <melee/mn/inlines.h>
#include <melee/mn/mnevent.h>
#include <melee/mn/mnmain.h>
#include <melee/mn/mnmainrule.h>
#include <melee/mn/mnruleplus.h>
#include <melee/mn/mnstagesw.h>
#include <melee/mn/types.h>
#include <sysdolphin/baselib/controller.h>
#include <sysdolphin/baselib/gobj.h>
#include <sysdolphin/baselib/gobjplink.h>
#include <sysdolphin/baselib/jobj.h>
#include <sysdolphin/baselib/sislib.h>

/* ------------------------------------------------------------------------
 * Vanilla mn/mnstagesw.c pieces (statics with unique names; the overlay
 * linker resolves them). MnStageSwData is private to that file; same layout.
 * ---------------------------------------------------------------------- */

#define NUM_STAGES 29

typedef struct MnStageSwData {
    u8 x0;
    u8 x1;
    u8 x2[NUM_STAGES];
    u8 x1F;
    HSD_JObj* x20;
    HSD_JObj* x24;
    HSD_JObj* x28;
    HSD_JObj* x2C;
    HSD_JObj* x30;
    HSD_JObj* x34;
    u8 pad_38[8];
    HSD_Text* x40[NUM_STAGES];
} MnStageSwData;

extern AnimLoopSettings mnStageSw_803ED488[5];
extern HSD_GObj* mnStageSw_804D6BF0;
extern s8 mnStageSw_804D6BF4;
void mnStageSw_8023593C(HSD_GObj* gobj);
void mnStageSw_802359C8(MnStageSwData* data);
void mnStageSw_80235DC8(const u8* user_data, s32 buttons);
void mnStageSw_80236178(MnStageSwData* data, u8 idx);
HSD_JObj* mnStageSw_802364A0(MnStageSwData* data, u8 idx);
void mnStageSw_80236548(HSD_GObj* gobj, u8 arg1, u8 arg2);

/// Same as the static inline in gm/gmevent.c: the event data block in the
/// save data. unk_535 is the last selected event (TM-CE: MemcardData+0x535).
static inline struct EventData* osdmenuEventData(void)
{
    return &gmMainLib_804D3EE0->vs.unk_530;
}

static inline bool osdmenuActive(void)
{
    return mn_804A04F0.entering_menu >= TM_OSDMENU_FROM_RULES;
}

/* ------------------------------------------------------------------------
 * Texts. TM-CE kept these in the screen's MnStageSwData.x40[0..2], which
 * vanilla uses for the stage names it no longer creates in OSD mode.
 * ---------------------------------------------------------------------- */

static HSD_Text* osdmenu_left_text;
static HSD_Text* osdmenu_right_text;
static s32 osdmenu_position_subtext;
static HSD_Text* osdmenu_rules_indicator;

/// Load Alt Text When Loaded With L.asm: TextASCIILeft / TextASCIIRight.
/// Row i of each column is OSD id mnStageSw_803ED4C4[i] (left: rows 0-14,
/// right: rows 15-28); the strings are TM-CE's, including the empty ones
/// and the extra first entry it draws above the first row.
static const char* const osdmenu_left_names[16] = {
    "",
    "Wavedash Info",
    "L-Cancel",
    "",
    "Act OoS Frame",
    "",
    "Dashback",
    "",
    "",
    "Fighter-specific Tech",
    "Powershield Frame",
    "",
    "SDI Inputs",
    "Grab Breakout",
    "Ledgedash Info",
    "Act OoHitstun",
};

static const char* const osdmenu_right_names[15] = {
    "",
    "Lockout Timers",
    "Item Throw Interrupts",
    "Boost Grab",
    "", /* reserved for custom events */
    "Act OoLag",
    "",
    "Act OoAirborne",
    "Jump Cancel Timing",
    "Fastfall Timing",
    "Frame Advantage",
    "Combo Counter",
    "",
    "",
    "",
};

#define OSDMENU_POSITION_COUNT 4

static const char* const osdmenu_position_names[OSDMENU_POSITION_COUNT] = {
    "HUD", "Sides", "Top Left", "Top Right",
};

/* TextProperties in Load Alt Text When Loaded With L.asm. */
#define OSDMENU_TEXT_X (-4.5F)
#define OSDMENU_TEXT_Y (-7.25F)
#define OSDMENU_TEXT_Z (17.5F) /* vanilla constant, rtoc-0x3B30 */
#define OSDMENU_TEXT_SCALE (0.022F)
#define OSDMENU_ROW_HEIGHT (50.0F)
#define OSDMENU_LEFT_X (0.0F) /* vanilla constant, rtoc-0x35FC */
#define OSDMENU_RIGHT_X (655.0F)
#define OSDMENU_TITLE_X (300.0F)
#define OSDMENU_TITLE_Y (-43.0F)
#define OSDMENU_POSITION_X (0.0F)
#define OSDMENU_POSITION_Y (-43.0F)
#define OSDMENU_XY_X (-120.0F)
#define OSDMENU_XY_Y (-7.25F)

static const char* osdmenuPositionName(u8 pos)
{
    /* TM-CE: "Fix value if invalid from removed max osd setting". */
    if (pos >= OSDMENU_POSITION_COUNT) {
        pos = 0;
    }
    return osdmenu_position_names[pos];
}

static HSD_Text* osdmenuCreateColumn(void)
{
    HSD_Text* text = HSD_SisLib_803A6754(0, mn_804D6BB5);
    text->pos_x = OSDMENU_TEXT_X;
    text->pos_y = OSDMENU_TEXT_Y;
    text->pos_z = OSDMENU_TEXT_Z;
    text->default_alignment = 2;
    text->default_fitting = 1;
    text->default_kerning = 1;
    text->font_size.x = OSDMENU_TEXT_SCALE;
    text->font_size.y = OSDMENU_TEXT_SCALE;
    return text;
}

static void osdmenuWriteColumn(HSD_Text* text, const char* const* names,
                               int count, f32 x)
{
    int i;
    for (i = 0; i < count; i++) {
        HSD_SisLib_803A6B98(text, x,
                            OSDMENU_TEXT_Y + OSDMENU_ROW_HEIGHT * (f32) i,
                            "%s", names[i]);
    }
}

/// Port of Load Alt Text When Loaded With L.asm (fn_80236998+0x1A8, in
/// place of mnStageSw_802359C8): OSD names in two columns, the "OSD Menu"
/// title, the OSD position and its "(X/Y)" hint.
static void osdmenuCreateTexts(void)
{
    GXColor title_color = { 0xFF, 0x75, 0x75, 0xFF };
    GXColor position_color = { 0x8D, 0xFF, 0x6E, 0xFF };
    HSD_Text* text;
    s32 sub;

    text = osdmenuCreateColumn();
    osdmenu_left_text = text;
    osdmenuWriteColumn(text, osdmenu_left_names, 16, OSDMENU_LEFT_X);

    sub = HSD_SisLib_803A6B98(text, OSDMENU_TITLE_X, OSDMENU_TITLE_Y,
                              "OSD Menu");
    HSD_SisLib_803A74F0(text, sub, &title_color);

    sub = HSD_SisLib_803A6B98(text, OSDMENU_POSITION_X, OSDMENU_POSITION_Y,
                              "OSD Position: %s",
                              osdmenuPositionName(*tmce_osdmenu_Position()));
    osdmenu_position_subtext = sub;
    HSD_SisLib_803A74F0(text, sub, &position_color);

    sub = HSD_SisLib_803A6B98(text, OSDMENU_XY_X, OSDMENU_XY_Y, "(X/Y)");
    HSD_SisLib_803A74F0(text, sub, &position_color);

    text = osdmenuCreateColumn();
    osdmenu_right_text = text;
    osdmenuWriteColumn(text, osdmenu_right_names, 15, OSDMENU_RIGHT_X);
}

/// Port of Remove Text When Leaving Custom RSS.asm (fn_80236998+0x224).
static void osdmenuRemoveTexts(void)
{
    if (osdmenu_left_text != NULL) {
        HSD_SisLib_803A5CC4(osdmenu_left_text);
        osdmenu_left_text = NULL;
    }
    if (osdmenu_right_text != NULL) {
        HSD_SisLib_803A5CC4(osdmenu_right_text);
        osdmenu_right_text = NULL;
    }
}

/// Port of XY To Adjust OSD Position.asm (fn_80235F80+0x178): Y and X step
/// the OSD position forward and back, wrapping, and update its text.
static void osdmenuPositionInput(void)
{
    u32 trigger = (u32) gm_GetButtonsTriggered(4);
    u8* pos = tmce_osdmenu_Position();
    s32 value;

    if (trigger & HSD_PAD_Y) {
        value = *pos + 1;
        if (value >= OSDMENU_POSITION_COUNT) {
            value = 0;
        }
    } else if (trigger & HSD_PAD_X) {
        value = *pos - 1;
        if (value < 0) {
            value = OSDMENU_POSITION_COUNT - 1;
        }
    } else {
        return;
    }
    *pos = value;
    if (osdmenu_left_text != NULL) {
        HSD_SisLib_803A70A0(osdmenu_left_text, osdmenu_position_subtext,
                            "OSD Position: %s", osdmenuPositionName(value));
    }
    sfxMove();
}

/// Where B (and, from the event select screen, Start) leaves to.
/// Port of Return to First Page When Loaded With L.asm (fn_80235F80+0x64).
static void osdmenuReturn(void)
{
    u8 from = mn_804A04F0.entering_menu;

    if (from < TM_OSDMENU_FROM_RULES) {
        mn_802339FC();
    } else if (from == TM_OSDMENU_FROM_EVENTS) {
        mnEvent_8024E838(osdmenuEventData()->unk_535, true);
    } else {
        mn_8023164C();
    }
}

/* ------------------------------------------------------------------------
 * Edited copies of the screen's two procs
 * ---------------------------------------------------------------------- */

static inline s32 osdmenuCountEnabled(const u8* user_data)
{
    s32 i;
    s32 count = 0;

    for (i = 0; i < NUM_STAGES; i++) {
        if (user_data[i + 2] != 0) {
            count += 1;
        }
    }
    return count;
}

static inline void osdmenuSaveSettings(void)
{
    mnStageSw_8023593C(mnStageSw_804D6BF0);
    lbCardGame_SaveChanges();
}

/**
 * Replaces fn_80235F80 (`function` hook), the screen's input proc.
 * Vanilla, plus:
 * - Set Flag on Leaving Custom RSS.asm (+0x4C): B keeps entering_menu in OSD
 *   mode, so the return path and the text removal still see it.
 * - Return to First Page When Loaded With L.asm (+0x64): osdmenuReturn.
 * - Can Disable All Toggles in Custom RSS.asm (+0xE4): in OSD mode the last
 *   enabled row can be turned off too.
 * - Disable Save to Bitfield Every Change.asm (+0x160): A no longer writes
 *   the toggles back on every change (any mode); they are saved on leaving.
 * - XY To Adjust OSD Position.asm (+0x178).
 * - Return to Event Screen When Pressing Start.asm (+0x1A8).
 */
void tm_osdmenu_Think(HSD_GObj* gobj)
{
    s32 enabled;
    u32 buttons;
    u8* user_data;
    u8* confirmed;

    user_data = mnStageSw_804D6BF0->user_data;
    buttons = mn_804A04F0.buttons = mn_80229624(4U);
    if (buttons & MenuInput_Back) {
        sfxBack();
        if (!osdmenuActive()) {
            mn_804A04F0.entering_menu = 0;
        }
        osdmenuSaveSettings();
        mn_804D6BC8.cooldown = 5;
        osdmenuReturn();
        HSD_GObjFree(gobj);
        return;
    }
    if ((u8) mnStageSw_804D6BF4 != 0) {
        return;
    }
    if (buttons & MenuInput_AButton) {
        if (mn_804A04F0.hovered_selection < NUM_STAGES) {
            confirmed = &mn_804A04F0.confirmed_selection;
            if (*confirmed != 0) {
                if (osdmenuCountEnabled(user_data) > 1 || osdmenuActive()) {
                    enabled = 0;
                } else {
                    enabled = 1;
                }
                if (enabled != 0) {
                    lbAudioAx_80024030(3);
                } else {
                    sfxMove();
                    *confirmed = 0;
                }
            } else {
                sfxMove();
                *confirmed = 1;
            }
            return;
        }
    } else {
        if (osdmenuActive()) {
            osdmenuPositionInput();
        }
        if (buttons & MenuInput_StartButton) {
            sfxForward();
            switch (gm_GetCurrentGameMode()) {
            case GM_MENU:
                osdmenuSaveSettings();
                if (mn_804A04F0.entering_menu == TM_OSDMENU_FROM_EVENTS) {
                    HSD_GObjFree(gobj);
                    mnEvent_8024E838(osdmenuEventData()->unk_535, true);
                    return;
                }
                mn_80229860(GM_VS);
                return;
            default:
                osdmenuSaveSettings();
                mn_8022F4CC();
                return;
            }
        }
    }
    if (buttons & 0xF) {
        sfxMove();
        mnStageSw_80235DC8(user_data, buttons);
    }
}

static inline void osdmenuFinishEnter(HSD_GObj* menu_gobj,
                                      MnStageSwData* data, HSD_JObj** child)
{
    MnStageSwData* d = menu_gobj->user_data;
    HSD_JObj* jobj;
    s32 i;

    data->x1F = 0;
    if (osdmenuActive()) {
        osdmenuCreateTexts();
    } else {
        mnStageSw_802359C8(data);
    }
    HSD_JObjClearFlagsAll(d->x2C, JOBJ_HIDDEN);
    HSD_JObjClearFlagsAll(d->x34, JOBJ_HIDDEN);
    for (i = 0; i < NUM_STAGES; i++) {
        jobj = mnStageSw_802364A0(d, i);
        if (i != d->x1) {
            lb_80011E24(jobj, child, 3, -1);
            HSD_JObjSetFlagsAll(*child, JOBJ_HIDDEN);
        }
    }
    mnStageSw_80236178(d, d->x1);
    mnStageSw_804D6BF4 = 0;
}

static inline void osdmenuFreeTexts(MnStageSwData* data)
{
    s32 i;

    if (osdmenuActive()) {
        osdmenuRemoveTexts();
        return;
    }
    for (i = 0; i < NUM_STAGES; i++) {
        HSD_SisLib_803A5CC4(data->x40[i]);
    }
}

static inline AnimLoopSettings* osdmenuStateAnim(u8 state)
{
    switch (state) {
    case 1:
        return &mnStageSw_803ED488[1];
    case 2:
        return &mnStageSw_803ED488[3];
    case 3:
        return &mnStageSw_803ED488[2];
    default:
        return &mnStageSw_803ED488[4];
    }
}

/**
 * Replaces fn_80236998 (`function` hook), the screen's animation / display
 * proc. Vanilla, plus Load Alt Text When Loaded With L.asm (+0x1A8) and
 * Remove Text When Leaving Custom RSS.asm (+0x224): in OSD mode the OSD
 * texts take the place of the 29 stage-name texts.
 */
void tm_osdmenu_Proc(HSD_GObj* gobj)
{
    MnStageSwData* data = gobj->user_data;
    AnimLoopSettings* anims;
    HSD_JObj* jobj;
    HSD_JObj* child;
    s32 changed_menu = 0;
    s32 changed_hovered = 0;
    s32 changed_confirmed = 0;
    u8 state = data->x1F;

    if ((state == 0 || state == 1 || state == 3) &&
        data->x0 != (u8) mn_804A04F0.cur_menu)
    {
        if (mn_804A04F0.entering_menu != 0) {
            data->x1F = 4;
        } else {
            data->x1F = 2;
        }
        anims = osdmenuStateAnim(data->x1F);
        jobj = data->x24;
        HSD_JObjReqAnim(jobj, anims->start_frame);
        HSD_JObjAnim(jobj);
        state = data->x1F;
        if (state == 0 || state == 1 || state == 3) {
            changed_menu = 1;
            changed_hovered = 1;
            changed_confirmed = 1;
        }
    }

    state = data->x1F;
    if (state != 0) {
        jobj = data->x24;
        anims = osdmenuStateAnim(state);
        if (mn_8022F298(jobj) >= anims->end_frame) {
            switch (data->x1F) {
            case 1:
            case 3:
                osdmenuFinishEnter(gobj, data, &child);
                return;
            case 2:
            case 4:
                osdmenuFreeTexts(data);
                HSD_GObjFree(gobj);
                return;
            }
        }
        HSD_JObjAnim(jobj);
    }

    state = data->x1F;
    if (state == 0 || state == 1 || state == 3) {
        if ((s32) data->x1 != (s32) mn_804A04F0.hovered_selection) {
            changed_hovered = 1;
        }
        if (data->x2[mn_804A04F0.hovered_selection] !=
            mn_804A04F0.confirmed_selection)
        {
            changed_confirmed = 1;
        }
    }

    mnStageSw_80236548(gobj, changed_hovered, changed_confirmed);
    if (changed_menu != 0) {
        data->x0 = mn_804A04F0.cur_menu;
    }
    if (changed_hovered != 0) {
        data->x1 = mn_804A04F0.hovered_selection;
    }
    if (changed_confirmed != 0) {
        data->x2[mn_804A04F0.hovered_selection] =
            mn_804A04F0.confirmed_selection;
    }
}

/* ------------------------------------------------------------------------
 * Toggle storage
 * ---------------------------------------------------------------------- */

/// Wraps `gm_IsStageUnlocked` in mnStageSw_80236CBC (+0x144), which reads
/// each row's initial state. Port of Load Toggles When Loaded With L .asm:
/// in OSD mode the row's state is its bit in TM_OSDEnabled.
bool tm_osdmenu_GetToggle(u16 id)
{
    if (!osdmenuActive()) {
        return gm_IsStageUnlocked(id);
    }
    return (*tmce_osdmenu_Enabled() >> id) & 1;
}

/// Wraps `gm_801641E4` in mnStageSw_8023593C (+0x58), which writes the rows
/// back. Port of Save Toggles When Loaded With L.asm.
void tm_osdmenu_SetToggle(u8 id, u8 on)
{
    u32* bits;

    if (!osdmenuActive()) {
        gm_801641E4(id, on);
        return;
    }
    bits = tmce_osdmenu_Enabled();
    if (on != 0) {
        *bits |= 1U << id;
    } else {
        *bits &= ~(1U << id);
    }
}

/* ------------------------------------------------------------------------
 * VS rules menu entry
 * ---------------------------------------------------------------------- */

/**
 * Wraps the `mn_80229624` button read in fn_8022F538 (+0x2C), the rules
 * menu's input proc. Port of Load Random Stage Select On L Press.asm
 * (+0x40): L opens the screen in OSD mode and ends the rules menu's proc.
 * TM-CE then jumps to the end of the proc; returning no buttons does the
 * same, since the rest of the proc only acts on buttons.
 */
u32 tm_osdmenu_RulesButtons(u32 slot)
{
    u32 buttons = mn_80229624(slot);

    if (!(buttons & MenuInput_LTrigger)) {
        return buttons;
    }
    sfxForward();
    mn_804A04F0.entering_menu = TM_OSDMENU_FROM_RULES;
    mn_804D6BC8.cooldown = 5;
    mnStageSw_80237410();
    HSD_GObjFree(HSD_GObj_CurrentInvokedProcGObj);
    return 0;
}

/**
 * Wraps the `mn_80230E38` calls in mn_8023164C, mn_80231714 and
 * mn_80231804 (the rules menu's builders). Port of Press L for OSD
 * Indicator.asm (end of mn_80230E38): an "L = OSD" note on the rules menu.
 */
HSD_GObj* tm_osdmenu_CreateRules(int mode)
{
    HSD_GObj* gobj = mn_80230E38(mode);
    HSD_Text* text = HSD_SisLib_803A6754(0, 1);
    s32 sub;

    osdmenu_rules_indicator = text;
    text->default_kerning = 1;
    text->default_alignment = 1;
    text->pos_z = 17.0F;
    text->font_size.x = 0.035F;
    text->font_size.y = 0.035F;
    sub = HSD_SisLib_803A6B98(text, -250.0F, -241.0F, "L = OSD");
    HSD_SisLib_803A7548(text, sub, 0.8F, 0.8F);
    return gobj;
}

/**
 * Wraps the `HSD_SisLib_803A5CC4` call in mn_802308F0 (+0x7C) that removes
 * the rules menu's description text as the menu leaves. Port of Remove
 * Press L for OSD Indicator.asm (+0x84): the indicator goes with it.
 */
void tm_osdmenu_RulesRemoveText(HSD_Text* text)
{
    HSD_SisLib_803A5CC4(text);
    if (osdmenu_rules_indicator != NULL) {
        HSD_SisLib_803A5CC4(osdmenu_rules_indicator);
        osdmenu_rules_indicator = NULL;
    }
}
