/** @file
 * Sound: Nintendo's AX voice library, as the game uses it, and the mixing
 * the console's DSP does for it.
 *
 * The game's own sound code (sysdolphin's AXDriver and synth, Melee's
 * lbAudio) is decompiled and runs as it is. Below it the console has AX:
 * 64 voices whose parameter blocks the DSP reads every 5 ms, decoding
 * DSP-ADPCM samples from audio RAM, resampling them to 32 kHz and mixing
 * them into the stereo output. That part is here: the AX calls the game
 * makes (about twenty-five), a mixer run every 5 ms of game time from the
 * frame boundary, and the result sent to the window's audio device
 * (window.c) or, for tests, to a file (MELEE_AUDIO_RAW: 16-bit stereo at
 * 32 kHz). Not done: the aux buses (reverb, chorus, delay: AXFX), the
 * surround channel, ITD (the slight left/right delay), interpolation
 * better than linear.
 *
 * Sound is on in the window build (MELEE_AUDIO=0 turns it off) and off in
 * the headless one unless a file is asked for. Off, every voice asked for
 * is one block nobody listens to, as the headless build always did, and
 * nothing is mixed. Nothing here touches the game's random numbers or its
 * fighters.
 *
 * The parameter blocks the game passes come from two places. Those it
 * builds itself (volume, mix) are ordinary structs. Those from sound files
 * (a sound's addresses and ADPCM settings, a music stream's headers) are
 * arrays of 32-bit words the disc layer swapped to the host's order (see
 * dvd.c), so a pair of 16-bit fields is one word whose first field is its
 * top half: they are read here as the game reads them, by the word. The
 * game also writes and reads some pairs as one word itself (the
 * resampling ratio, a voice's current address).
 */
#include "host.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <melee/lb/lbaudio_ax.h>
#include <sysdolphin/baselib/axdriver.h>

#include <dolphin/ai.h>
#include <dolphin/ax.h>
#include <dolphin/axfx.h>

#define AX_RATE 32000
#define AX_FRAME 160 /* samples in 5 ms */

#define FORMAT_ADPCM 0x00
#define FORMAT_PCM16 0x0A
#define FORMAT_PCM8 0x19

/// What the mixer keeps for a voice besides its parameter block.
typedef struct HostVoice {
    int on;           ///< playing: started, not yet past its end
    int primed;       ///< the first two samples are read
    u16 format, loop; ///< from the address block
    /// Addresses: nibbles (ADPCM), samples (PCM16), bytes (PCM8).
    u32 loop_addr, end_addr, cur;
    s16 coef[16];
    u16 ps;
    s16 yn1, yn2;
    u16 loop_ps;
    s16 loop_yn1, loop_yn2;
    u32 ratio; ///< input samples per output sample, 16.16
    u32 frac;
    s16 prev, last; ///< the two input samples the output falls between
} HostVoice;

static AXVPB voices[AX_MAX_VOICES];
/// Sound off: every voice is this block, which nothing writes to (the
/// synth then sees each sound as ended at once, as it always did here).
static AXVPB nobody;
static HostVoice hv[AX_MAX_VOICES];
static void (*frame_callback)(void);
static int sound = -1; /* -1 not decided yet */
static FILE* raw;
static uint64_t due; /* in 1/60000ths of a sample, see host_audio_frame */

static int sound_on(void)
{
    if (sound < 0) {
        const char* path = getenv("MELEE_AUDIO_RAW");
        const char* on = getenv("MELEE_AUDIO");
        sound = 0;
#ifdef HOST_WINDOW
        sound = on == NULL || strcmp(on, "0") != 0;
#else
        (void) on;
#endif
        if (path != NULL && path[0] != '\0') {
            raw = fopen(path, "wb");
            sound = raw != NULL;
        }
    }
    return sound;
}

static u32 word_at(const void* p)
{
    u32 v;
    memcpy(&v, p, 4);
    return v;
}

#define HI(w) ((u16) ((w) >> 16))
#define LO(w) ((u16) ((w) & 0xFFFF))

static HostVoice* host_of(const AXVPB* p)
{
    return &hv[p->index];
}

/// The voice's current address where the game reads it: one word at
/// currentAddressHi (synth.c reads it so, to follow a stream).
static void show_address(AXVPB* p)
{
    memcpy(&p->pb.addr.currentAddressHi, &host_of(p)->cur, 4);
}

/* --- voices --------------------------------------------------------------- */

void AXInit(void)
{
    memset(voices, 0, sizeof voices);
    memset(hv, 0, sizeof hv);
    for (int i = 0; i < AX_MAX_VOICES; i++) {
        voices[i].index = (u32) i;
    }
    frame_callback = NULL;
}

void AXQuit(void) {}

void AXRegisterCallback(void (*callback)())
{
    frame_callback = (void (*)(void)) callback;
}

static void reset(AXVPB* p)
{
    u32 index = p->index;
    memset(&p->pb, 0, sizeof p->pb);
    memset(&hv[index], 0, sizeof hv[index]);
    p->sync = 0;
    p->depop = 0;
}

AXVPB* AXAcquireVoice(u32 priority, void (*callback)(void*), u32 userContext)
{
    AXVPB* got = NULL;

    if (!sound_on()) {
        /* as the headless build always did: the synth's sounds start and
           end on their own clock, unheard (an acquire that failed would
           take other paths in the game's sound code) */
        (void) callback;
        (void) userContext;
        nobody.priority = (int) priority;
        return &nobody;
    }
    for (int i = 0; i < AX_MAX_VOICES && got == NULL; i++) {
        if (voices[i].priority == 0) {
            got = &voices[i];
        }
    }
    if (got == NULL) {
        /* the lowest priority below this one is dropped for it */
        for (int i = 0; i < AX_MAX_VOICES; i++) {
            if ((u32) voices[i].priority < priority &&
                (got == NULL || voices[i].priority < got->priority))
            {
                got = &voices[i];
            }
        }
        if (got == NULL) {
            return NULL;
        }
        if (got->callback != NULL) {
            got->callback(got);
        }
    }
    reset(got);
    got->priority = (int) priority;
    got->callback = callback;
    got->userContext = userContext;
    return got;
}

void AXFreeVoice(AXVPB* p)
{
    if (p == &nobody) {
        return;
    }
    reset(p);
    p->priority = 0;
    p->callback = NULL;
}

void AXSetVoicePriority(AXVPB* p, u32 priority)
{
    if (p == &nobody) {
        return;
    }
    p->priority = (int) priority;
}

void AXSetVoiceState(AXVPB* p, u16 state)
{
    if (p == &nobody) {
        return;
    }
    HostVoice* h = host_of(p);
    p->pb.state = state;
    if (state != 0 && !h->on) {
        h->on = 1;
        h->primed = 0;
        h->frac = 0;
    } else if (state == 0) {
        h->on = 0;
    }
}

void AXSetVoiceType(AXVPB* p, u16 type)
{
    if (p == &nobody) {
        return;
    }
    p->pb.type = type;
}

void AXSetVoiceSrcType(AXVPB* p, u32 type)
{
    if (p == &nobody) {
        return;
    }
    p->pb.srcSelect = (u16) type;
}

void AXSetVoiceMix(AXVPB* p, AXPBMIX* mix)
{
    if (p == &nobody) {
        return;
    }
    p->pb.mix = *mix;
}

void AXSetVoiceVe(AXVPB* p, AXPBVE* ve)
{
    if (p == &nobody) {
        return;
    }
    p->pb.ve = *ve;
}

void AXSetVoiceVeDelta(AXVPB* p, s16 delta)
{
    if (p == &nobody) {
        return;
    }
    p->pb.ve.currentDelta = delta;
}

void AXSetVoiceItdOn(AXVPB* p)
{
    if (p == &nobody) {
        return;
    }
    p->pb.itd.flag = 1;
}

void AXSetVoiceItdTarget(AXVPB* p, u16 lShift, u16 rShift)
{
    if (p == &nobody) {
        return;
    }
    p->pb.itd.targetShiftL = lShift;
    p->pb.itd.targetShiftR = rShift;
}

void AXSetVoiceAddr(AXVPB* p, AXPBADDR* addr)
{
    if (p == &nobody) {
        return;
    }
    HostVoice* h = host_of(p);
    u32 w = word_at(&addr->loopFlag);
    h->loop = HI(w);
    h->format = LO(w);
    h->loop_addr = word_at(&addr->loopAddressHi);
    h->end_addr = word_at(&addr->endAddressHi);
    h->cur = word_at(&addr->currentAddressHi);
    memcpy(&p->pb.addr, addr, sizeof p->pb.addr);
    show_address(p);
}

void AXSetVoiceLoop(AXVPB* p, u16 loop)
{
    if (p == &nobody) {
        return;
    }
    host_of(p)->loop = loop;
}

void AXSetVoiceLoopAddr(AXVPB* p, u32 addr)
{
    if (p == &nobody) {
        return;
    }
    host_of(p)->loop_addr = addr;
    memcpy(&p->pb.addr.loopAddressHi, &addr, 4);
}

void AXSetVoiceEndAddr(AXVPB* p, u32 addr)
{
    if (p == &nobody) {
        return;
    }
    host_of(p)->end_addr = addr;
    memcpy(&p->pb.addr.endAddressHi, &addr, 4);
}

void AXSetVoiceCurrentAddr(AXVPB* p, u32 addr)
{
    if (p == &nobody) {
        return;
    }
    host_of(p)->cur = addr;
    show_address(p);
}

void AXSetVoiceAdpcm(AXVPB* p, AXPBADPCM* adpcm)
{
    if (p == &nobody) {
        return;
    }
    HostVoice* h = host_of(p);
    const u16* a = &adpcm->a[0][0];
    u32 w;
    for (int i = 0; i < 8; i++) {
        w = word_at(a + 2 * i);
        h->coef[2 * i] = (s16) HI(w);
        h->coef[2 * i + 1] = (s16) LO(w);
    }
    w = word_at(&adpcm->gain);
    h->ps = LO(w);
    w = word_at(&adpcm->yn1);
    h->yn1 = (s16) HI(w);
    h->yn2 = (s16) LO(w);
    memcpy(&p->pb.adpcm, adpcm, sizeof p->pb.adpcm);
}

void AXSetVoiceAdpcmLoop(AXVPB* p, AXPBADPCMLOOP* loop)
{
    if (p == &nobody) {
        return;
    }
    HostVoice* h = host_of(p);
    u32 w0 = word_at(&loop->loop_pred_scale);
    u32 w1 = word_at(&loop->loop_yn2);
    h->loop_ps = HI(w0);
    h->loop_yn1 = (s16) LO(w0);
    h->loop_yn2 = (s16) HI(w1);
    memcpy(&p->pb.adpcmLoop, loop, sizeof p->pb.adpcmLoop);
}

void AXSetVoiceSrc(AXVPB* p, AXPBSRC* src)
{
    if (p == &nobody) {
        return;
    }
    HostVoice* h = host_of(p);
    /* the game writes the ratio as one word at ratioHi */
    h->ratio = word_at(&src->ratioHi);
    memcpy(&p->pb.src, src, sizeof p->pb.src);
}

void AXSetVoiceSrcRatio(AXVPB* p, float ratio)
{
    if (p == &nobody) {
        return;
    }
    HostVoice* h = host_of(p);
    if (ratio < 0.0F) {
        ratio = 0.0F;
    }
    h->ratio = (u32) (65536.0F * ratio);
    memcpy(&p->pb.src.ratioHi, &h->ratio, 4);
}

/* --- aux buses and effects: not mixed ------------------------------------- */

void AXRegisterAuxACallback(void (*callback)(void*, void*), void* context)
{
    (void) callback;
    (void) context;
}

void AXRegisterAuxBCallback(void (*callback)(void*, void*), void* context)
{
    (void) callback;
    (void) context;
}

void AXFXSetHooks(void* (*alloc_hook)(size_t), void (*free_hook)(void*))
{
    (void) alloc_hook;
    (void) free_hook;
}

int AXFXReverbHiInit(struct AXFX_REVERBHI* rev)
{
    (void) rev;
    return 1;
}

int AXFXReverbHiShutdown(struct AXFX_REVERBHI* rev)
{
    (void) rev;
    return 1;
}

int AXFXReverbStdInit(struct AXFX_REVERBSTD* rev)
{
    (void) rev;
    return 1;
}

int AXFXReverbStdShutdown(struct AXFX_REVERBSTD* rev)
{
    (void) rev;
    return 1;
}

int AXFXChorusInit(struct AXFX_CHORUS* c)
{
    (void) c;
    return 1;
}

int AXFXChorusShutdown(struct AXFX_CHORUS* c)
{
    (void) c;
    return 1;
}

int AXFXDelayInit(struct AXFX_DELAY* delay)
{
    (void) delay;
    return 1;
}

int AXFXDelayShutdown(struct AXFX_DELAY* delay)
{
    (void) delay;
    return 1;
}

/* --- the audio interface: the output is the mixer's ----------------------- */

void AIInit(u8* stack)
{
    (void) stack;
}

void AISetDSPSampleRate(u32 rate)
{
    (void) rate;
}

void AISetStreamVolLeft(u8 vol)
{
    (void) vol;
}

void AISetStreamVolRight(u8 vol)
{
    (void) vol;
}

/* --- music ------------------------------------------------------------------ */

static char song[64];
/// The last start, as asked: one asked for in a quiet stretch is made when
/// the stretch ends (host_audio_quiet).
static char song_path[256];
static u8 song_volume;
static int song_track;
static int song_pending;
static int quiet;

/// The game's music starts here (lbaudio_ax.c's call, renamed by
/// tools/native_build.py): which one it was is kept for `song`.
bool host_pstream_start(const char* path, u8 volume, int track)
{
    const char* name = strrchr(path, '/');
    snprintf(song, sizeof song, "%s", name != NULL ? name + 1 : path);
    snprintf(song_path, sizeof song_path, "%s", path);
    song_volume = volume;
    song_track = track;
    if (quiet) {
        song_pending = 1;
        return true;
    }
    return HSD_AudioPStreamStartChParam(path, volume, track);
}

/// And it stops here (the same file's call): a start still waiting is
/// dropped.
bool host_axdriver_stop(void)
{
    song_pending = 0;
    return AXDriverStop();
}

/* --- quiet stretches -------------------------------------------------------
 * Frames played to set something up (a match loading, at full speed) are
 * not heard: the game's sound runs as ever, and its mix is dropped. Only
 * the first moment of a stretch goes through (QUIET_TAIL), as sound in
 * real time like any other: what was playing ends there instead of being
 * cut, and a menu's click that started the stretch is heard whole. What
 * the stretch started is not heard afterwards either: its sound effects
 * are keyed off, and music it asked for starts when it ends, from its
 * beginning, as a match's does when it is first seen. (Starting it again
 * then instead stopped a stream whose first read was still on its way,
 * and the stream's code fell over when the read came.) TM-CE's savestate
 * loads are silent the same way (Savestate_Silent, and the fighters'
 * sounds stopped). */

#define QUIET_TAIL 30 /* 5 ms audio frames: 150 ms */

static int quiet_tail;

void host_audio_quiet(int on)
{
    if (on && !quiet) {
        quiet = 1;
        quiet_tail = QUIET_TAIL;
        song_pending = 0;
    } else if (!on && quiet) {
        quiet = 0;
        lbAudioAx_80023694(); /* every sound effect (HSD_AudioSFXKeyOffAll) */
        if (song_pending) {
            song_pending = 0;
            HSD_AudioPStreamStartChParam(song_path, song_volume, song_track);
        }
    }
}

/// The music the game started last ("" for none yet).
const char* host_song(void)
{
    return song;
}

/* --- the mixer ------------------------------------------------------------ */

static s16 clamp16(s32 v)
{
    return (s16) (v < -32768 ? -32768 : v > 32767 ? 32767 : v);
}

/// The voice's next input sample, then on to the one after (looping or
/// stopping at its end address, which is the last one it plays).
static s16 next_sample(HostVoice* h)
{
    const uint8_t* b;
    s16 out = 0;

    if (!h->on) {
        return 0;
    }
    switch (h->format) {
    case FORMAT_ADPCM: {
        s32 nib, val;
        int idx;
        if ((h->cur & 15) == 0) { /* a frame's header: its scale */
            b = host_aram_peek(h->cur >> 1);
            h->ps = b != NULL ? b[0] : 0;
            h->cur += 2;
        }
        b = host_aram_peek(h->cur >> 1);
        nib = b == NULL ? 0 : (h->cur & 1) ? (b[0] & 0xF) : (b[0] >> 4);
        if (nib >= 8) {
            nib -= 16;
        }
        idx = (h->ps >> 4) & 7;
        val = ((nib * (1 << (h->ps & 0xF))) << 11) +
              h->coef[2 * idx] * h->yn1 + h->coef[2 * idx + 1] * h->yn2;
        out = clamp16((val + 1024) >> 11);
        h->yn2 = h->yn1;
        h->yn1 = out;
        break;
    }
    case FORMAT_PCM16:
        b = host_aram_peek(h->cur * 2);
        out = b != NULL ? (s16) (b[0] << 8 | b[1]) : 0;
        break;
    case FORMAT_PCM8:
        b = host_aram_peek(h->cur);
        out = b != NULL ? (s16) ((s8) b[0] * 256) : 0;
        break;
    default:
        h->on = 0;
        return 0;
    }
    if (h->cur == h->end_addr) {
        if (h->loop) {
            h->cur = h->loop_addr;
            if (h->format == FORMAT_ADPCM) {
                h->ps = h->loop_ps;
                h->yn1 = h->loop_yn1;
                h->yn2 = h->loop_yn2;
            }
        } else {
            h->on = 0;
        }
    } else {
        h->cur++;
    }
    return out;
}

static void mix_voice(AXVPB* p, s32* left, s32* right)
{
    HostVoice* h = host_of(p);
    s32 vol = p->pb.ve.currentVolume;
    s32 dv = p->pb.ve.currentDelta;
    s32 vl = p->pb.mix.vL, vr = p->pb.mix.vR;

    if (!h->primed) {
        h->prev = next_sample(h);
        h->last = next_sample(h);
        h->primed = 1;
    }
    for (int n = 0; n < AX_FRAME && h->on; n++) {
        s32 s = h->prev + (((s32) (h->last - h->prev) * (s32) (h->frac >> 1)) >>
                           15);
        s32 sv = (s * vol) >> 15;
        left[n] += (sv * vl) >> 15;
        right[n] += (sv * vr) >> 15;
        vol += dv;
        vol = vol < 0 ? 0 : vol > 0xFFFF ? 0xFFFF : vol;
        h->frac += h->ratio;
        while (h->frac >= 0x10000 && h->on) {
            h->frac -= 0x10000;
            h->prev = h->last;
            h->last = next_sample(h);
        }
    }
    p->pb.ve.currentVolume = (u16) vol;
    show_address(p);
    if (!h->on) {
        p->pb.state = 0; /* the sound ended: the synth sees it stopped */
    }
}

static void ax_frame(void)
{
    s32 left[AX_FRAME], right[AX_FRAME];
    s16 out[AX_FRAME * 2];

    if (frame_callback != NULL) {
        frame_callback();
    }
    memset(left, 0, sizeof left);
    memset(right, 0, sizeof right);
    for (int i = 0; i < AX_MAX_VOICES; i++) {
        if (voices[i].priority != 0 && voices[i].pb.state != 0 && hv[i].on) {
            mix_voice(&voices[i], left, right);
        }
    }
    for (int n = 0; n < AX_FRAME; n++) {
        out[2 * n] = clamp16(left[n]);
        out[2 * n + 1] = clamp16(right[n]);
    }
    if (host_net_resimulating()) {
        return; /* a frame played again: it was heard the first time */
    }
    if (quiet) {
        if (quiet_tail == 0) {
            return; /* a frame nobody hears (host_audio_quiet) */
        }
        quiet_tail--;
    }
    if (raw != NULL) {
        fwrite(out, sizeof out[0], AX_FRAME * 2, raw);
    }
#ifdef HOST_WINDOW
    host_window_audio(out, AX_FRAME);
#endif
}

/// Once a frame (the console's 60000/1001 a second): the 5 ms audio
/// frames that time holds, 3.34 on average.
void host_audio_frame(void)
{
    if (sound <= 0 && !(sound < 0 && sound_on())) {
        return;
    }
    due += (uint64_t) AX_RATE * 1001;
    while (due >= (uint64_t) 60000 * AX_FRAME) {
        due -= (uint64_t) 60000 * AX_FRAME;
        ax_frame();
    }
    if (raw != NULL) {
        fflush(raw);
    }
}
