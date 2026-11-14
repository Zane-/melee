/** @file
 * Looking inside a run: which code drew random numbers this frame.
 *
 * The game's three random functions are built under other names and called
 * through these, which remember the caller of each draw since the frame
 * boundary. Two builds of the game that should play identically can then be
 * compared draw by draw (tools/melee_native/compare.py --rng).
 */
#include "host.h"

#include <stdio.h>

int HSD_Rand_vanilla(void);
float HSD_Randf_vanilla(void);
int HSD_Randi_vanilla(int max_val);

#define MAX_DRAWS 4096
static void* callers[MAX_DRAWS];
static int ndraws;

static void note(void* caller)
{
    if (ndraws < MAX_DRAWS) {
        callers[ndraws] = caller;
    }
    ndraws++;
}

int HSD_Rand(void)
{
    note(__builtin_return_address(0));
    return HSD_Rand_vanilla();
}

float HSD_Randf(void)
{
    note(__builtin_return_address(0));
    return HSD_Randf_vanilla();
}

int HSD_Randi(int max_val)
{
    note(__builtin_return_address(0));
    return HSD_Randi_vanilla(max_val);
}

void host_rng_frame(void)
{
    ndraws = 0;
}

/// This frame's draws so far: copies up to `max` return addresses, returns
/// how many there were.
int host_rng_callers(void** out, int max)
{
    int n = ndraws < MAX_DRAWS ? ndraws : MAX_DRAWS;
    for (int i = 0; i < n && i < max; i++) {
        out[i] = callers[i];
    }
    return ndraws;
}

/// The return addresses of this frame's draws, in order, on one line.
void host_rng_print(void)
{
    printf("@");
    for (int i = 0; i < ndraws && i < MAX_DRAWS; i++) {
        printf(" %x", (unsigned) (uintptr_t) callers[i]);
    }
    printf("\n");
}
