/** @file
 * Rollback netcode: two players, one on each of ports 0 and 1, each running
 * the game, sending each other their inputs over UDP.
 *
 * Each side plays its own inputs a few frames late (the input delay) and
 * the other side's as they arrive; a frame whose other-side input has not
 * arrived is played with a guess (the last one received). When the real
 * input differs from the guess, the game goes back to that frame
 * (rollback.c: what each frame changed) and plays the frames since again,
 * quickly, without drawing them, within the same frame of real time.
 *
 * The frame boundary. The scene loop (gmscene.c) waits for a pad sample in
 * lb_80019894 (main.c), then runs one frame of logic and draws it. In a
 * session that wait is host_net_boundary, which returns whether a frame is
 * to be run (a sample pushed) or not (a stall: the game waits, its state
 * untouched):
 *  - a frame of real time: the window (present the last picture, pace,
 *    read the controller) or the test driver's commands, the local input,
 *    the network;
 *  - then, for every frame run, the game's timeline: completions, emulated
 *    time, sound, as host_frame_tick does; the state is recorded
 *    (host_rb_mark); a misprediction goes back; the pads are set for the
 *    frame.
 * Frames played again run as their own loop iterations, the draw pass and
 * their sound left out, with no real-time part.
 *
 * Inputs carry the frame they are for; each packet repeats every input the
 * other side has not acknowledged, so a lost packet costs nothing but
 * time. The sides keep within MAX_PREDICT frames of the last input received
 * (else the side ahead waits), and even out their frame advantage (time
 * sync). Every HASH_EVERY frames whose inputs are all known each side
 * hashes the fighters and the random seed and sends it: a difference is a
 * desync.
 *
 * For tests, a simulated network: packets held a number of the sender's
 * real frames, some jitter, some lost (`net start ... LAG LOSS JITTER`).
 */
#include "host.h"

#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

void host_fighter_json(int slot, char* out, size_t size);
int host_rng_callers(void** out, int max);
void host_rng_frame(void);
#define RNG_LOG 64
#define RNG_KEEP 128
extern uint32_t* HSD_RandSeedPtr;

#define HIST 1024        /* frames of inputs kept (a ring) */
#define MAX_PREDICT 7    /* frames played past the last input received */
#define SEND_MAX 40      /* inputs in one packet at most */
#define HASH_EVERY 30
#define HASHES 32
#define MAGIC 0x4D4E4554u /* "MNET" */
#define SIM_QUEUE 512

enum { PKT_HELLO = 1, PKT_INPUTS = 2, PKT_BYE = 3 };

typedef struct NetPad {
    uint16_t buttons;
    int8_t lx, ly, cx, cy;
    uint8_t lt, rt;
} NetPad;

typedef struct Packet {
    uint32_t magic;
    uint8_t type;
    uint8_t count;   ///< inputs that follow
    uint16_t delay;  ///< the sender's input delay (hello)
    uint32_t frame;  ///< the sender's next frame to run
    int32_t ack;     ///< the last of our inputs it has, in order
    int32_t first;   ///< the frame of the first input that follows
    int32_t adv;     ///< the sender's frame advantage, in 1/16 frames
    int32_t hash_frame;
    uint32_t hash_lo, hash_hi;
    NetPad pads[SEND_MAX];
} Packet;

static struct {
    int active;
    int fd;
    struct sockaddr_in peer;
    int local;       ///< the local player's port (0 or 1)
    int delay;
    uint32_t frame;  ///< the next frame to run (a session frame)
    NetPad local_in[HIST], remote_in[HIST], used[HIST];
    uint32_t seed_at[HIST]; ///< the gameplay hash at each boundary (tests)
    uint8_t drawn[HIST];    ///< whether each frame was last played drawn
    /* tests: who drew random numbers in each recent frame */
    struct { uint32_t frame; int count; void* at[RNG_LOG]; } draws[RNG_KEEP];
    int64_t local_written; ///< the last local frame with an input
    int64_t confirmed;     ///< the last remote frame received, in order
    int64_t acked;         ///< the last local frame the peer has
    uint32_t remote_frame;
    int32_t remote_adv;
    int64_t first_wrong;   ///< the earliest frame played with a bad guess
    int resim_left, chain; ///< frames to play again; inside a rollback
    int hello;             ///< the peer has answered
    int rendered;          ///< a frame was drawn since the last present
    uint32_t ticks;        ///< frames of real time
    int since_sync;        ///< frames since the last time-sync wait
    double adv_avg;
    /* desync checks */
    struct { int32_t frame; uint64_t hash; int done; } mine[HASHES],
        theirs[HASHES];
    int desync;
    int32_t desync_frame;
    uint32_t checks;
    /* numbers */
    uint64_t rollbacks, rolled, stalls, sync_waits, sent, received;
    int max_rollback;
    int nodraw; ///< MELEE_NET_NODRAW: never draw (tests compare memory)
    int peer_left;              ///< the other side said goodbye
    uint32_t last_heard;        ///< the real frame it was last heard
    /* a simulated network */
    int lag, loss, jitter;
    uint32_t rng;
    struct { uint32_t due; int length; Packet p; } queue[SIM_QUEUE];
    int queued;
} net;

static int final_hash(int32_t frame);

int host_net_active(void)
{
    return net.active;
}

int host_net_resimulating(void)
{
    return net.active && net.chain;
}

static NetPad pad_of(const HostPad* h)
{
    NetPad p = { h->buttons, h->lx, h->ly, h->cx, h->cy, h->lt, h->rt };
    return p;
}

static void to_host(HostPad* h, const NetPad* p)
{
    h->buttons = p->buttons;
    h->lx = p->lx;
    h->ly = p->ly;
    h->cx = p->cx;
    h->cy = p->cy;
    h->lt = p->lt;
    h->rt = p->rt;
    h->connected = 1;
}

static uint32_t sim_rand(void)
{
    net.rng = net.rng * 1103515245u + 12345u;
    return net.rng >> 16;
}

/* --- packets --------------------------------------------------------------- */

static void send_now(const Packet* p, int length)
{
    if (sendto(net.fd, p, (size_t) length, 0, (struct sockaddr*) &net.peer,
               sizeof net.peer) == length)
    {
        net.sent++;
    }
}

static void send_packet(const Packet* p, int length)
{
    if (net.lag == 0 && net.loss == 0 && net.jitter == 0) {
        send_now(p, length);
        return;
    }
    if ((int) (sim_rand() % 100) < net.loss || net.queued == SIM_QUEUE) {
        return;
    }
    net.queue[net.queued].due =
        net.ticks + (uint32_t) net.lag +
        (net.jitter > 0 ? sim_rand() % (uint32_t) (net.jitter + 1) : 0);
    net.queue[net.queued].length = length;
    net.queue[net.queued].p = *p;
    net.queued++;
}

static void release_queue(void)
{
    int k = 0;
    for (int i = 0; i < net.queued; i++) {
        if (net.queue[i].due <= net.ticks) {
            send_now(&net.queue[i].p, net.queue[i].length);
        } else {
            net.queue[k++] = net.queue[i];
        }
    }
    net.queued = k;
}

static uint64_t gameplay_hash(void)
{
    char a[1024];
    uint64_t h = 0xCBF29CE484222325ull;
    for (int slot = 0; slot < 2; slot++) {
        host_fighter_json(slot, a, sizeof a);
        for (const char* c = a; *c; c++) {
            h = (h ^ (uint8_t) *c) * 0x100000001B3ull;
        }
    }
    h = (h ^ *HSD_RandSeedPtr) * 0x100000001B3ull;
    return h;
}

static void send_inputs(void)
{
    Packet p;
    int64_t from = net.acked + 1;
    int count;

    memset(&p, 0, sizeof p);
    p.magic = MAGIC;
    p.type = net.hello ? PKT_INPUTS : PKT_HELLO;
    p.delay = (uint16_t) net.delay;
    p.frame = net.frame;
    p.ack = (int32_t) net.confirmed;
    if (from < net.local_written - SEND_MAX + 1) {
        from = net.local_written - SEND_MAX + 1;
    }
    if (from < 0) {
        from = 0;
    }
    count = net.local_written >= from ? (int) (net.local_written - from + 1)
                                      : 0;
    p.first = (int32_t) from;
    p.count = (uint8_t) count;
    for (int i = 0; i < count; i++) {
        p.pads[i] = net.local_in[(from + i) % HIST];
    }
    p.adv = (int32_t) (net.adv_avg * 16.0);
    p.hash_frame = -1;
    for (int i = 0; i < HASHES; i++) {
        /* only a frame whose inputs are all known: final */
        if (net.mine[i].frame > p.hash_frame &&
            final_hash(net.mine[i].frame))
        {
            p.hash_frame = net.mine[i].frame;
            p.hash_lo = (uint32_t) net.mine[i].hash;
            p.hash_hi = (uint32_t) (net.mine[i].hash >> 32);
        }
    }
    send_packet(&p, (int) (offsetof(Packet, pads) +
                           (size_t) count * sizeof(NetPad)));
}

/// Whether the hash kept for boundary `frame` is final: every input before
/// it is known, and no wrong guess before it waits to be played again.
static int final_hash(int32_t frame)
{
    return frame >= 0 && (int64_t) frame - 1 <= net.confirmed &&
           !(net.first_wrong >= 0 && net.first_wrong < frame);
}

/// Both sides' hashes of a frame, when both are known: a desync if they
/// differ. Each is compared once.
static void compare_hashes(int slot)
{
    if (net.mine[slot].frame < 0 || net.mine[slot].done ||
        net.mine[slot].frame != net.theirs[slot].frame ||
        !final_hash(net.mine[slot].frame))
    {
        return; /* not both, or mine may still be played again */
    }
    net.mine[slot].done = 1;
    net.checks++;
    if (net.mine[slot].hash != net.theirs[slot].hash && !net.desync) {
        net.desync = 1;
        net.desync_frame = net.mine[slot].frame;
        host_log("net: desync at frame %d", net.desync_frame);
    }
}

static void check_hash(int32_t frame, uint64_t hash)
{
    int slot;
    if (frame < 0 || frame % HASH_EVERY != 0) {
        return;
    }
    slot = (frame / HASH_EVERY) % HASHES;
    if (net.theirs[slot].frame == frame || net.mine[slot].frame > frame) {
        return; /* had it, or too old */
    }
    net.theirs[slot].frame = frame;
    net.theirs[slot].hash = hash;
    compare_hashes(slot);
}

static void receive(void)
{
    Packet p;
    for (;;) {
        ssize_t got = recv(net.fd, &p, sizeof p, 0);
        if (got < 0) {
            break;
        }
        if (got < (ssize_t) offsetof(Packet, pads) || p.magic != MAGIC ||
            got < (ssize_t) (offsetof(Packet, pads) +
                             (size_t) p.count * sizeof(NetPad)))
        {
            continue;
        }
        net.received++;
        net.last_heard = net.ticks;
        if (p.type == PKT_BYE) {
            if (!net.peer_left) {
                host_log("net: the other side left");
            }
            net.peer_left = 1;
            continue;
        }
        net.hello = 1;
        net.remote_frame = p.frame;
        net.remote_adv = p.adv;
        if (p.ack > net.acked) {
            net.acked = p.ack;
        }
        for (int i = 0; i < p.count; i++) {
            int64_t f = (int64_t) p.first + i;
            if (f != net.confirmed + 1) {
                continue; /* already have it, or a gap (not sent so) */
            }
            net.remote_in[f % HIST] = p.pads[i];
            net.confirmed = f;
            if (f < (int64_t) net.frame &&
                memcmp(&net.used[f % HIST], &p.pads[i], sizeof(NetPad)) != 0 &&
                (net.first_wrong < 0 || f < net.first_wrong))
            {
                net.first_wrong = f;
            }
        }
        check_hash(p.hash_frame,
                   (uint64_t) p.hash_lo | (uint64_t) p.hash_hi << 32);
    }
    for (int i = 0; i < HASHES; i++) {
        compare_hashes(i); /* those that became final */
    }
}

/* --- the session --------------------------------------------------------- */

const char* host_net_start(int local, int bind_port, const char* peer_ip,
                           int peer_port, int delay, int lag, int loss,
                           int jitter)
{
    struct sockaddr_in me;
    const char* why;

    if (net.active) {
        return "a session is on";
    }
    if (local != 0 && local != 1) {
        return "the local port is 0 or 1";
    }
    memset(&net, 0, sizeof net);
    net.fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (net.fd < 0) {
        return "no socket";
    }
    memset(&me, 0, sizeof me);
    me.sin_family = AF_INET;
    me.sin_port = htons((uint16_t) bind_port);
    me.sin_addr.s_addr = htonl(INADDR_ANY);
    if (bind(net.fd, (struct sockaddr*) &me, sizeof me) < 0) {
        close(net.fd);
        return "cannot bind that UDP port";
    }
    fcntl(net.fd, F_SETFL, O_NONBLOCK);
    memset(&net.peer, 0, sizeof net.peer);
    net.peer.sin_family = AF_INET;
    net.peer.sin_port = htons((uint16_t) peer_port);
    if (inet_pton(AF_INET, peer_ip, &net.peer.sin_addr) != 1) {
        close(net.fd);
        return "not an IPv4 address";
    }
    why = host_rb_start();
    if (why != NULL) {
        close(net.fd);
        return why;
    }
    net.local = local;
    net.delay = delay < 0 ? 0 : delay > 15 ? 15 : delay;
    net.local_written = -1;
    net.confirmed = -1;
    net.acked = -1;
    net.first_wrong = -1;
    net.lag = lag;
    net.loss = loss;
    net.jitter = jitter;
    net.rng = (uint32_t) (local + 1) * 2654435761u;
    for (int i = 0; i < HASHES; i++) {
        net.mine[i].frame = -1;
        net.theirs[i].frame = -1;
    }
    /* frames before the first input (the delay) are empty */
    for (int f = 0; f < net.delay; f++) {
        memset(&net.local_in[f], 0, sizeof(NetPad));
        net.local_written = f;
    }
    net.nodraw = getenv("MELEE_NET_NODRAW") != NULL;
    net.active = 1;
    return NULL;
}

void host_net_stop(void)
{
    if (!net.active) {
        return;
    }
    {
        Packet p;
        memset(&p, 0, sizeof p);
        p.magic = MAGIC;
        p.type = PKT_BYE;
        send_now(&p, (int) offsetof(Packet, pads));
    }
    close(net.fd);
    net.active = 0;
    host_rb_stop();
    host.draw = 1;
}

/// Whether this real frame should wait instead of running one.
static int should_wait(void)
{
    if (!net.hello) {
        return 1;
    }
    if ((int64_t) net.frame > net.confirmed + MAX_PREDICT) {
        return 1; /* too far past what the other side has sent */
    }
    /* time sync: half the difference of the two advantages is how far
       ahead this side is; wait a frame when that is over one, at most
       every few frames */
    {
        double mine = (double) net.frame - (double) net.remote_frame;
        net.adv_avg = net.adv_avg * 0.9 + mine * 0.1;
        double ahead = (net.adv_avg - net.remote_adv / 16.0) / 2.0;
        if (ahead > 1.0 && net.since_sync > 10) {
            net.since_sync = 0;
            net.sync_waits++;
#ifdef HOST_WINDOW
            /* in real time: the next frame comes a frame period later */
            host_window_delay_frame();
            return 0;
#else
            return 1; /* a test's frames: this one waits */
#endif
        }
    }
    return 0;
}

/// At a boundary every HASH_EVERY frames, played or played again: the
/// hash of the state there (final once the inputs before it are all known,
/// which compare_hashes and send_inputs wait for).
static void remember_hash(void)
{
    if (net.frame % HASH_EVERY != 0) {
        return;
    }
    {
        int slot = (int) ((net.frame / HASH_EVERY) % HASHES);
        net.mine[slot].frame = (int32_t) net.frame;
        net.mine[slot].hash = gameplay_hash();
        net.mine[slot].done = 0;
        compare_hashes(slot);
    }
}

/// The scene loop's wait for a frame, in a session: whether to run one.
int host_net_boundary(void)
{
    int replay = net.chain;

    if (!replay) {
        /* a frame of real time */
        net.ticks++;
        net.since_sync++;
#ifdef HOST_WINDOW
        if (net.rendered) {
            host_window_frame(); /* the last picture, pacing, the pads */
            net.rendered = 0;
        } else {
            host_window_idle();
        }
#endif
        host_control_frame();
        release_queue();
        receive();
        if (should_wait()) {
            net.stalls++;
            send_inputs();
            return 0;
        }
        /* the local input for its frame, the delay later */
        if ((int64_t) net.frame + net.delay > net.local_written) {
            net.local_written = (int64_t) net.frame + net.delay;
            net.local_in[net.local_written % HIST] =
                pad_of(&host.pads[net.local]);
        }
        send_inputs();
    }

    /* the game's timeline, as host_frame_tick runs it */
    host.int_enabled = 1;
    host_deliver();
    host.frame++;
    host_advance(HOST_TICKS_PER_FRAME);
    host_match_install();
    host_audio_frame();
    if (net.frame > 0) {
        /* the draws of the frame just played (and this boundary's) */
        uint32_t f = net.frame - 1;
        int slot = (int) (f % RNG_KEEP);
        net.draws[slot].frame = f;
        net.draws[slot].count = host_rng_callers(net.draws[slot].at, RNG_LOG);
    }
    host_rng_frame();
    host_rb_mark();

    if (!replay && net.first_wrong >= 0) {
        int back = (int) ((int64_t) net.frame - net.first_wrong);
        if (back > 0 && host_rb_rewind(back) == 0) {
            net.rollbacks++;
            net.rolled += (uint64_t) back;
            if (back > net.max_rollback) {
                net.max_rollback = back;
            }
            net.frame = (uint32_t) net.first_wrong;
            net.resim_left = back;
            net.chain = 1;
        } else if (back > 0) {
            host_log("net: cannot go back %d frames", back);
        }
        net.first_wrong = -1;
    }

    net.seed_at[net.frame % HIST] = (uint32_t) gameplay_hash();
    /* the pads for this frame */
    {
        uint32_t f = net.frame;
        int remote = 1 - net.local;
        NetPad guess;
        if ((int64_t) f <= net.confirmed) {
            guess = net.remote_in[f % HIST];
        } else if (net.confirmed >= 0) {
            guess = net.remote_in[net.confirmed % HIST];
        } else {
            memset(&guess, 0, sizeof guess);
        }
        net.used[f % HIST] = guess;
        to_host(&host.pads[net.local], &net.local_in[f % HIST]);
        to_host(&host.pads[remote], &guess);
    }

    if (net.nodraw) {
        host.draw = 0; /* tests: nothing drawn, so states compare */
        net.drawn[net.frame % HIST] = 0;
        remember_hash();
        if (net.chain && net.resim_left > 0) {
            net.resim_left--;
        } else {
            net.chain = 0;
            net.rendered = 1;
            remember_hash();
        }
        net.frame++;
        return 1;
    }
    if (net.chain && net.resim_left > 0) {
        /* Played again, and drawn as well: drawing changes the game's
           state (the effect loader and the particles it starts draw from
           the same random numbers as the fighters), so both sides must
           have drawn the same frames. A frame played again is drawn here
           once, as the other side drew it once. Nothing of it is shown:
           the last frame's drawing is what the window presents. */
        net.drawn[net.frame % HIST] = 1;
        host.draw = 1;
        net.resim_left--;
        remember_hash();
    } else {
        /* the last frame of a rollback, or an ordinary one: drawn */
        host.draw = 1;
        net.drawn[net.frame % HIST] = 1;
        net.chain = 0;
        net.rendered = 1;
        remember_hash();
    }
    net.frame++;
    return 1;
}

/// One line of numbers for `net stats`.
void host_net_report(char* out, size_t size)
{
    snprintf(out, size,
             "%u %lld %u %llu %llu %d %llu %llu %llu %llu %u %d %d %d %u",
             net.frame, (long long) net.confirmed, net.remote_frame,
             (unsigned long long) net.rollbacks,
             (unsigned long long) net.rolled, net.max_rollback,
             (unsigned long long) net.stalls,
             (unsigned long long) net.sync_waits,
             (unsigned long long) net.sent,
             (unsigned long long) net.received, net.checks, net.desync,
             net.desync_frame, net.peer_left,
             net.ticks - net.last_heard);
}

/// The inputs frame `frame` was (or will be) played with, as the session
/// knows them: the local one and the other side's (confirmed or not).
int host_net_inputs(uint32_t frame, char* out, size_t size)
{
    const NetPad* l = &net.local_in[frame % HIST];
    const NetPad* r = &net.remote_in[frame % HIST];
    if ((int64_t) frame > net.local_written ||
        (int64_t) frame + HIST <= net.local_written)
    {
        return -1;
    }
    snprintf(out, size, "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d",
             l->buttons, l->lx, l->ly, l->cx, l->cy, l->lt, l->rt,
             (int64_t) frame <= net.confirmed, r->buttons, r->lx, r->ly,
             r->cx, r->cy, r->lt, r->rt, net.local, (int) net.frame);
    {
        size_t at = strlen(out);
        snprintf(out + at, size - at, " %u %d", net.seed_at[frame % HIST],
                 net.drawn[frame % HIST]);
    }
    return 0;
}

/// Who drew random numbers in session frame `frame` (if still kept).
int host_net_rng(uint32_t frame, char* out, size_t size)
{
    int slot = (int) (frame % RNG_KEEP);
    size_t at = 0;
    if (net.draws[slot].frame != frame) {
        return -1;
    }
    at += (size_t) snprintf(out, size, "%d", net.draws[slot].count);
    for (int i = 0; i < net.draws[slot].count && i < RNG_LOG && at < size;
         i++)
    {
        at += (size_t) snprintf(out + at, size - at, " %x",
                                (unsigned) (uintptr_t) net.draws[slot].at[i]);
    }
    return 0;
}

/// The gameplay hash now (tests compare the two sides' at a frame).
uint64_t host_net_hash(void)
{
    return gameplay_hash();
}
