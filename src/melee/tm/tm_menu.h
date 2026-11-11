#ifndef MELEE_TM_MENU_H
#define MELEE_TM_MENU_H

#include <Runtime/platform.h>

#include <sysdolphin/baselib/forward.h>

/**
 * @file
 * Pause-menu engine. Port of TM-CE `src/menu.c` / `menu.h`.
 *
 * TM-CE declares menus as writable static data and mutates them in place
 * (cursor, values, even labels). Overlay code may not have writable statics,
 * so a menu is split in two here:
 *
 * - #TmMenuDesc / #TmOptionDesc: `const` definitions, written by events.
 * - #TmMenu / #TmOption: the live copy, built on the heap by #tmMenu_Init.
 *   An option's live copy embeds a full copy of its definition (`d`), so
 *   code that edits labels or ranges at runtime (as TM-CE's lab does) edits
 *   the copy.
 *
 * @warning The engine reads the local master pad and freezes the game
 *          directly. That is fine offline. It is not rollback-safe and must
 *          not drive simulation state in a netplay session
 *          (docs/ai/slippi-tandem.md).
 */

#define TM_MENU_MAXOPTION 9
#define TM_MENU_DESCLINEMAX 4
#define TM_MENU_SCROLLOFF 2
#define TM_MENU_RAPID_INTERVAL 5
#define TM_MENU_RAPID_START 15
#define TM_MENU_RAPID_R 2
#define TM_MENU_MAXMENUS 64
#define TM_ANALOG_TRIGGER_THRESHOLD 43

typedef struct TmMenu TmMenu;
typedef struct TmMenuDesc TmMenuDesc;
typedef struct TmOption TmOption;

typedef enum TmOptionKind {
    /* 0 */ TM_OPTKIND_MENU,   ///< opens #TmOptionDesc::menu
    /* 1 */ TM_OPTKIND_STRING, ///< picks from #TmOptionDesc::values
    /* 2 */ TM_OPTKIND_INT,    ///< number shown with #TmOptionDesc::format
    /* 3 */ TM_OPTKIND_FUNC,   ///< runs #TmOptionDesc::on_select
    /* 4 */ TM_OPTKIND_INFO,   ///< read-only row
    /* 5 */ TM_OPTKIND_TOGGLE  ///< on / off
} TmOptionKind;

typedef enum TmMenuMode {
    /* 0 */ TM_MENUMODE_NORMAL,
    /* 1 */ TM_MENUMODE_PAUSED
} TmMenuMode;

/// Art loaded from the `eventMenu` symbol of TM-CE's menu asset file.
typedef struct TmMenuAssets {
    /* +00 */ HSD_Joint* menu;
    /* +04 */ HSD_Joint* popup;
    /* +08 */ HSD_Joint* scroll;
    /* +0C */ HSD_Joint* check;
    /* +10 */ HSD_Joint* arrow;
    /* +14 */ HSD_Joint* playback;
    /* +18 */ HSD_Joint* message;
    /* +1C */ HSD_CObjDesc* hud_cobjdesc;
    /* +20 */ HSD_Joint* tip_jobj;
    /* +24 */ void** tip_jointanim;
} TmMenuAssets;

/// Definition of one menu row. Declare arrays of these `static const`.
typedef struct TmOptionDesc {
    u8 kind;             ///< ::TmOptionKind
    u8 disable;          ///< starts greyed out
    s16 value_min;       ///< lowest value
    u16 value_num;       ///< number of values
    s16 value_default;   ///< initial value
    const char* name;
    const char* desc[TM_MENU_DESCLINEMAX];
    const TmMenuDesc* menu;      ///< #TM_OPTKIND_MENU: submenu
    const char* const* values;   ///< #TM_OPTKIND_STRING: one label per value
    const char* format;          ///< #TM_OPTKIND_INT: printf format
    const char* value_string;    ///< #TM_OPTKIND_FUNC / INFO: optional text
    void (*on_change)(HSD_GObj* menu_gobj, int value);
    void (*on_select)(HSD_GObj* menu_gobj);
} TmOptionDesc;

/// Button shortcut (hold Y + button) to an option of some menu.
typedef struct TmShortcut {
    int button_mask;
    const TmMenuDesc* menu; ///< menu that owns the option
    int option_index;       ///< index into that menu's options
} TmShortcut;

typedef struct TmShortcutList {
    int count;
    const TmShortcut* list;
} TmShortcutList;

/// Definition of a menu. Declare `static const`.
struct TmMenuDesc {
    const char* name;
    u8 option_num;
    const TmOptionDesc* options;
    const TmShortcutList* shortcuts; ///< used when this is the root menu
};

/// Live state of one row.
struct TmOption {
    TmOptionDesc d;  ///< editable copy of the definition
    s16 val;
    s16 val_prev;
    TmMenu* submenu; ///< live menu for #TM_OPTKIND_MENU
};

/// Live state of one menu.
struct TmMenu {
    const TmMenuDesc* desc;
    u8 scroll;
    u8 cursor;
    TmOption* options; ///< `desc->option_num` entries
    TmMenu* prev;      ///< menu to return to with B
    const TmShortcutList* shortcuts;
};

/// User data of the menu GObj.
typedef struct TmMenuData {
    TmMenu* curr_menu;
    const TmMenuAssets* assets;
    u16 canvas_menu;
    u16 canvas_popup;
    u8 hide_menu; ///< hides the base menu; used by custom submenus
    u8 mode;      ///< ::TmMenuMode
    u8 controller_index; ///< port that paused
    u8 menu_count;
    u32 frames; ///< frames since the menu GObj was created
    HSD_Text* text_name;
    HSD_Text* text_value;
    HSD_Text* text_title;
    HSD_Text* text_desc;
    HSD_JObj* rowboxes[TM_MENU_MAXOPTION];
    HSD_JObj* highlight_menu;
    HSD_JObj* scrollbar;
    HSD_JObj* scroll_top;
    HSD_JObj* scroll_bot;
    HSD_GObj* custom_gobj;
    /// Per-frame function of a custom submenu. Returns whether unpausing is
    /// allowed this frame.
    int (*custom_gobj_think)(HSD_GObj* custom_gobj);
    void (*custom_gobj_destroy)(HSD_GObj* custom_gobj);
    TmMenu* menus[TM_MENU_MAXMENUS]; ///< every live menu, for lookup
} TmMenuData;

/// Creates the menu GObj, its camera, models and text, and builds the live
/// menu tree from @p start_menu. The menu starts hidden and unpaused.
HSD_GObj* tmMenu_Init(const TmMenuDesc* start_menu,
                      const TmMenuAssets* assets);

/// Per-frame update. Call once per frame from the event's update.
void tmMenu_Update(HSD_GObj* gobj);

/// Redraws all text and the highlight after any state change.
void tmMenu_UpdateText(HSD_GObj* gobj);

/// Live menu for a definition, or NULL if it is not part of the tree.
TmMenu* tmMenu_Find(HSD_GObj* gobj, const TmMenuDesc* desc);

/// Live options array for a definition. Events keep this pointer and index
/// it with their option enums, like TM-CE indexes its static arrays.
TmOption* tmMenu_Options(HSD_GObj* gobj, const TmMenuDesc* desc);

void tmMenu_ChangeOptionVal(HSD_GObj* gobj, TmOption* option, int val);
void tmMenu_EnterMenu(HSD_GObj* gobj);
void tmMenu_ExitMenu(HSD_GObj* gobj);
void tmMenu_NextMenu(HSD_GObj* gobj, TmMenu* next_menu);
void tmMenu_PrevMenu(HSD_GObj* gobj);

#endif
