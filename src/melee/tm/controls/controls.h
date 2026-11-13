#ifndef MELEE_TM_CONTROLS_CONTROLS_H
#define MELEE_TM_CONTROLS_CONTROLS_H

#include <Runtime/platform.h>

/**
 * @file
 * Control profiles and input delay.
 *
 * Both act on a raw pad sample just before the game turns it into its pad
 * status (the one place every later reader, menu or fighter, goes through),
 * and only during a match: menus always use the standard layout and no
 * delay.
 *
 * - A **profile** says what each physical button does. The player picks one
 *   by name; the nickname chosen on the character select screen can carry
 *   it (tm_ctl_SetNameProfile).
 * - **Input delay** holds every pad back a number of frames, the way a
 *   netplay client does, so that offline practice feels like online play.
 *
 * Not rollback state: none of this may run during Slippi netplay, where
 * Slippi itself supplies each frame's inputs. Both default to "off"
 * (standard layout, no delay).
 */

/// The most frames a pad can be held back.
#define TM_CTL_MAX_DELAY 10
#define TM_CTL_PROFILE_COUNT 8
#define TM_CTL_NAME_LEN 8
/// Nicknames the game can store (its name list).
#define TM_CTL_NAMETAG_COUNT 120

/// A physical input a profile assigns: indexes TmCtlProfile::map.
typedef enum TmCtlInput {
    TmCtlIn_A,
    TmCtlIn_B,
    TmCtlIn_X,
    TmCtlIn_Y,
    TmCtlIn_Z,
    TmCtlIn_L,
    TmCtlIn_R,
    TmCtlIn_DpadUp,
    TmCtlIn_DpadDown,
    TmCtlIn_DpadLeft,
    TmCtlIn_DpadRight,
    TmCtlIn_Count
} TmCtlInput;

/// What an input does in a match.
typedef enum TmCtlAction {
    TmCtlAct_None,
    TmCtlAct_Attack,  ///< the A button
    TmCtlAct_Special, ///< B
    TmCtlAct_Jump,    ///< X
    TmCtlAct_Shield,  ///< a trigger: analogue if the input is one
    TmCtlAct_Grab,    ///< Z
    TmCtlAct_Taunt,   ///< D-pad up
    TmCtlAct_Count
} TmCtlAction;

typedef struct TmCtlProfile {
    char name[TM_CTL_NAME_LEN + 1];
    u8 used;                ///< false: an empty slot
    u8 map[TmCtlIn_Count];  ///< ::TmCtlAction for each ::TmCtlInput
    u8 tap_jump;            ///< up on the stick jumps (the game's default)
} TmCtlProfile;

typedef struct TmCtlSettings {
    u8 delay;           ///< frames every pad is held back in a match
    u8 port_profile[4]; ///< profile used by each port; 0 is the standard one
    /// Profile carried by each of the game's nicknames; 0: none.
    u8 name_profile[TM_CTL_NAMETAG_COUNT];
    TmCtlProfile profiles[TM_CTL_PROFILE_COUNT];
} TmCtlSettings;

extern TmCtlSettings tm_ctl;

/// Put the standard layout in every profile slot and clear the rest.
void tm_ctl_Init(void);
/// The standard layout, under @p name, in slot @p index.
void tm_ctl_ResetProfile(int index, const char* name);
void tm_ctl_SetNameProfile(int nametag, int profile);

/// @name Called from the mod's own hooks (tm.c)
/// @{
/// A match is starting: give each port the profile of its player's
/// nickname, and start holding pads back.
void tm_ctl_OnStartMelee(void);
void tm_ctl_OnSceneChange(void);
/// @}

/// `call` hook on lb_800198E0's call of HSD_PadRenewMasterStatus.
void tm_ctl_PadRenewMaster(void);

/// Whether up on the stick may start a jump for the fighter on @p port.
bool tm_ctl_TapJump(int port);

#endif
