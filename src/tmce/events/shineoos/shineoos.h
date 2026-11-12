#ifndef TMCE_EVENTS_SHINEOOS_H
#define TMCE_EVENTS_SHINEOOS_H

/*
 * Shine Out of Shield: shared by desc.c (EventDesc and scenario deck,
 * linked globally) and event.c (the event unit).
 */
#include "events.h"
#include "rotation/tm_rotation.h"

/// One CPU input, held for `hold` frames (0 counts as 1) from `frame`,
/// counted from the frame the attack starts. Stick and C-stick X are
/// relative to the player: positive is toward them.
typedef struct OosInput {
    s16 frame;    ///< -1 ends the list
    u8 hold;
    s8 lx, ly;
    s8 cx, cy;
    u32 buttons;  ///< PAD_BUTTON_* | PAD_TRIGGER_*
} OosInput;

typedef struct OosScenario {
    float distance;         ///< CPU start distance from the player
    const OosInput* inputs; ///< the attack, ended by frame -1
    s16 attack_timeout;     ///< frames to wait for the shield hit
    u8 face_away;           ///< CPU starts facing away (back aerials)
    s8 advantage;           ///< frame advantage on Fox's shield (data/)
} OosScenario;

extern const TmRotDeck ShineOos_Deck;
extern EventDesc ShineOos_Desc;

#endif
