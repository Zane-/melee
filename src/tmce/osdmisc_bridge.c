/*
 * osdmisc area, MexTK side: the FighterData.TM fields and TM-CE statics the
 * native ports in src/melee/tm/osdmisc/ read. Offsets in comments are the
 * m-ex/Header.s names the assembly uses.
 */
#include "events.h"

/* TM_FramesinCurrentAS */
int tmce_osdmisc_StateFrames(void* fp)
{
    return ((FighterData*) fp)->TM.state_frame;
}

/* TM_OneASAgo */
int tmce_osdmisc_PrevState(void* fp)
{
    return ((FighterData*) fp)->TM.state_prev[0];
}

/* TM_FramesInPrevASStart (TM_FramesinOneASAgo) */
int tmce_osdmisc_PrevStateFrames(void* fp)
{
    return ((FighterData*) fp)->TM.state_prev_frames[0];
}

/* TM_AnimCallback */
void* tmce_osdmisc_GetAnimCallback(void* fp)
{
    return ((FighterData*) fp)->TM.cb_anim;
}

void tmce_osdmisc_SetAnimCallback(void* fp, void* cb)
{
    ((FighterData*) fp)->TM.cb_anim = cb;
}

/* stc_match->time_frames (Grab Breakout.asm reads 0x8046B6A0 + 0x24) */
int tmce_osdmisc_MatchFrames(void)
{
    return stc_match->time_frames;
}
