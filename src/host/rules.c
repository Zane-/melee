/** @file
 * A Versus mode's end, decided inside the game (the client's Tug of War).
 *
 * gm_GetMatchOutcome asks host_rules_outcome each frame of a match, after
 * the timer and before the stocks (a patch, tools/native_build.py). With a
 * rule set, a match the rule says is won ends there as a stock match whose
 * last stock was lost does (OUTCOME_ELIMINATION): GAME! and the announcer,
 * everything standing still, then the scene's end, after which the host
 * starts the match again (match.c; `state`'s "ended").
 *
 * The rule reads only the game's own counters (each player's falls, which
 * count a self-destruct too), so it is part of the game's frame: two games
 * of an online session end on the same frame, and a rollback replays it.
 * The rule itself is the host's, set before the match by the driver
 * ("rules tug N") and the same on both sides of a session, like moves.c's.
 *
 *  - tug N: the lead is port 1's falls less port 0's; N either way wins
 *    (Tug of War: a KO pulls the rope a point toward the side that took
 *    it).
 */
#include "host.h"

#include <melee/gm/forward.h>
#include <melee/pl/player.h>

static int rule;
static int goal;

void host_rules_set(int kind, int n)
{
    rule = kind;
    goal = n;
}

int host_rules_get(int* n)
{
    if (n != NULL) {
        *n = goal;
    }
    return rule;
}

int host_rules_outcome(void)
{
    if (rule == HOST_RULES_TUG && goal > 0) {
        int lead = Player_GetFalls(1) - Player_GetFalls(0);
        if (lead >= goal || -lead >= goal) {
            return OUTCOME_ELIMINATION;
        }
    }
    return OUTCOME_NONE;
}
