# Our own peer-to-peer rollback netcode: feasibility

Asked by the owner on 2026-11-12: "I will eventually want to build our own peer to peer
rollback netcode (serverless); please conduct feasibility of this or if we need a central
server (we will need a central server for ranked games, but let's see if peer to peer is
feasible for simple tandem training and connecting and playing together!)"

Status: a study (2026-11-12), and since 2026-11-13 **an implementation**: "Built" below.
Network facts come from a source-reading pass on 2026-11-12 (sources at the end; none
re-checked by a second reader). The owner, 2026-11-13: "Let's start implementing rollback
p2p netcode now and get testing", choosing the STUN way of connecting over plain IP and
port.

## Answer

**Yes for playing together, with no server of ours.** Two players can connect directly using
a free public STUN server to learn their own public address and a short code pasted to each
other over any chat. That is the design Slippi's direct connect uses, minus its accounts and
its pairing server. The price: on published measurements, **roughly 15 to 30% of pairs cannot
connect that way** (both behind a symmetric NAT or carrier-grade NAT) and need a fallback:
forwarding a port, IPv6, a VPN overlay such as Tailscale or ZeroTier, or a relay.

**It belongs to the native build, not to the build that runs in Dolphin.** A game inside
stock Dolphin has no sockets, and Slippi Dolphin only speaks Slippi's protocol. The native
build (`native-port.md`) can open sockets and copy its own memory, and it re-simulates so fast
that rollback costs almost nothing. It is not playable yet: it has no graphics.

**A server of ours is needed only for what the owner already expects** (ranked play,
matchmaking, identity) and optionally to make connecting nicer (codes without pasting) or
universal (a relay).

## Built (2026-11-13)

The rollback core runs on the native build and is proven headless: two games over UDP on
one machine, through a simulated network, stay identical to each other and to an offline
game fed the same inputs.

| Piece | Where | What |
|-|-|-|
| The game's whole state in three regions | `src/host/state.c`, `src/host/gameheap.c`, `tools/native_build.py` (`game_state_script`, `gameheap.h`) | The arena (the console's addresses), every static of the game's timeline gathered by the linker into one section (`.game_state`: the game's library, the readers, and the host files whose state is the game's: emulated time, completions, alarms, the disc's and audio RAM's bookkeeping, the AX voices, the archive tables), and a game heap: what was converted object by object from the C library's heap (49 MB of archive data in a match) now comes from one region whose allocator keeps its bookkeeping inside it. Save, load, hash, dump |
| What each frame changed | `src/host/rollback.c` | A mirror of those regions; at each frame boundary the pages written since (the kernel's soft-dirty bits) go into the frame's undo record with what they held. A frame writes about 120 pages (0.5 MB); recording takes 0.4 ms, going back 0.2 ms. 24 frames kept |
| The session | `src/host/net.c` | Inputs by frame with an input delay, sent over UDP until acknowledged; the other side's guessed (its last input) until it arrives; a wrong guess goes back to that frame and plays the frames since again as quick loop iterations (no window present, no pacing, their sound discarded) within the same frame of real time; never more than 7 frames past the last input received (the side ahead waits); time sync on the two sides' frame advantage; every 30th frame a hash of the fighters and the random seed, compared once final |
| Commands | `control.c` | `save`/`load`/`hash`/`dump`, `rb start|stop|mark|back N|stats`, `net start LOCAL BIND PEER_IP PEER_PORT DELAY [LAG LOSS JITTER]`, `net stop|stats|hash|input F|rng F`, `draw 0|1` |

Tests: `tests/native/state.py` (8: a load brings back every byte; the same inputs replay the
same game for 600 frames, the same whole state), `tests/native/rollback.py` (6: going back
any number of frames equals the full snapshot there; rolling back 1 to 7 frames after every
frame and playing them again ends where straight play does), `tests/native/netplay.py`
(11: no lag, and 4 frames' lag with 3 jitter and 10% loss: about 300 rollbacks a side up to
7 frames deep, 66 desync checks passed, both sides and the offline game identical).

Found on the way:

- **The session's first frame.** `net start` comes in the middle of an ordinary frame; that
  frame must not run, or each side plays one more frame with its own pads before the
  session (main.c).
- **Drawing changes the game.** A frame played again was first left undrawn. The two sides
  then drew different frames, and a desync followed: the effect loader and the particles it
  starts (their scripts draw from the game's one random-number stream) depend on what was
  drawn (`efAsync`, `hsd_8039930C`). Found by logging who drew random numbers each frame on
  both sides (`net rng`) after a memory diff of the two (`dump`). A frame played again is
  now drawn too, so both sides have drawn every frame once; the window shows only the last.
  Headless that costs nothing; in the window build it is GPU commands that are never shown.
- A false desync: a hash compared after a wrong guess was known but before the frame was
  played again. A hash counts once every input before it is known and no rollback before
  it is pending.

**Connecting** (`tools/melee_client/online.py`, the same day): a UDP socket asks a public
STUN server (Google's, then Cloudflare's) for its outside address; that and the LAN address
become a 21-character code (13 bytes in base32) the players paste to each other; a plain
`ip:port` works as a code too. Both sides send to each other at once (hole punching), then a
small lobby over the path that worked settles who is port 1 (the lower random nonce), the
characters, the stage, the seed and the input delay; each closes the socket and the game
opens the same local port for the session. The client uses port 47700 each time, so a
router that keeps ports gives the same code every time (this machine's does: 45938 mapped to
45938). `tests/client/online_lobby.py` (9, one real STUN query with `--stun`).

**In the client** (`client.py`): Versus, your character, then "a friend, online" as who
plays the opponent: the online screen shows your code (A copies it to the clipboard), pastes
a friend's code, and lists friends met before (saved by the nickname they sent, with their
code). Both games then start the agreed match with nobody's input for 10 frames, and the
session begins with the person's controller on the port the lobby gave them. START opens a
menu that does not stop the game (stopping one side would desync it): resume, the column,
leave the match. The friend is told when the other leaves and goes back to the online
screen. The window build paces as usual; when its side is ahead, time sync moves the next
frame a frame period later (`host_window_delay_frame`); while it waits for the other side's
inputs it keeps the window alive without presenting (`host_window_idle`).
`tests/client/online.py`: two clients in two windows, each driven by its own thread.

Not built yet: sound across rollbacks (sound effects of frames played again are dropped, not
merged), Windows (soft-dirty is Linux's), a relay for the pairs hole punching cannot join,
spectators, more than two players.

## Where the netcode can live

| Host | Own netcode? | Why |
|-|-|-|
| The overlay DOL in stock Dolphin | Not realistic | Dolphin emulates the Broadband Adapter hardware (TAP, XLink Kai, tapserver, built-in, IPC). The game would need its own adapter driver, an IP stack and rollback snapshots, all in PowerPC code; this decomp has no network library |
| The overlay DOL in Slippi Dolphin | Slippi's only | Slippi's netplay is a custom device in its Dolphin fork plus code injected into the game. That is the route `slippi-tandem.md` studies; it needs a Slippi account and Slippi's pairing server |
| A Dolphin fork of ours | Possible | We would maintain and ship an emulator fork, and rollback would be emulator savestates, as in Slippi |
| **The native build** | **Yes** | Sockets from C; the game's whole state is memory we own; one frame of game logic takes well under a tenth of a millisecond |

Players of our netcode can only meet other players of our build. It does not interoperate
with Slippi.

## Rollback on the native build

Rollback needs three things: the same inputs must give the same game on both machines, the
game's state must be saved and restored, and frames must be re-simulated fast.

**Speed (measured 2026-11-12, this machine):**

| | |
|-|-|
| One frame of a match, headless | about 0.064 ms optimised (15,600 a second), 0.105 ms unoptimised |
| The game's state | the arena, 20 MB; statics, 1.1 MB; converted archive data on the host's heap (size not measured); audio RAM, 16 MB, written only when something loads |
| Copying 26 MB | 0.83 ms |

So even the plainest scheme fits a 16.7 ms frame: copy the state every frame (about 1 ms),
and for a rollback of 7 frames (Slippi's maximum) restore once and run 7 frames again (about
1.5 ms). Copying only the pages that changed would make it cheaper still but is not needed
to start. In Dolphin a rollback costs seven emulated frames; here it costs less than one
tenth of one.

**State that is not yet copyable.** Converted archive data is allocated from the C library's
heap, object by object, and a fighter's animation archive is replaced at every change of
animation. A snapshot has to cover it, so those allocations must first come from one region
of our own. The host layer's own state (emulated time, queued completions) is already in
statics.

**Determinism.** Within one binary on one machine a run is repeatable (time is emulated,
nothing reads the clock; `compare.py` relies on it). Across machines the same binary computes
the same basic float operations, but: the build uses fused multiply-add, so both CPUs must
have it; the C library's `sinf`, `cosf`, `atan2f` come from the system's glibc and may differ
between versions. Shipping one static binary, or using the console's own math routines from
`src/MSL`, removes that. Different compilers or operating systems would not be bit-identical
without more work. Checksums of the state exchanged every so often detect a desync either way.

**Shown since (2026-11-13):** the game's state can be captured and brought back exactly.
`tests/native/env.py` restores snapshots and gets the same game from the same inputs. Those
snapshots are forks of the process (`native-ai.md`), which is not what rollback will use:
it needs the copy in one process, described above.

**Not shown yet:** that in-process save and restore, and two instances kept in step over a
socket. Both can be proven headless, before graphics exist.

## Connecting without a server of ours

How Slippi's direct connect does it (as merged 2026-10-22; whether that has shipped was not
checked): the client asks third-party STUN servers for its public address and NAT type, sends
its connect code and candidate addresses to `matchmaking.slippi.gg`, receives the opponent's
public and LAN address, and both sides then connect to each other over UDP (ENet) from the
same port. **There is no relay**: gameplay never passes through Slippi's servers, and pairs
whose NATs cannot be punched do not connect.

The server's part there is identity and the exchange of two addresses. Without it:

1. Each game asks a public STUN server what its address looks like from outside.
   Cloudflare documents `stun.cloudflare.com` as "free and unlimited"; Google's
   `stun.l.google.com:19302` is used by Slippi and by Valve's example, with no published terms.
2. The game shows that as a short code. The players paste their codes to each other over
   Discord or any chat (established practice: "serverless WebRTC" demos exchange their
   offers by hand the same way).
3. Both games send to each other at once, which opens both NATs.

| | Works for |
|-|-|
| Hole punching with public STUN | 70 to 85% of pairs: 82% of NATs in Ford et al. (2005); 70% of 4.4 million attempts in Trautwein et al. (2026); 82.9% for port-restricted NATs and about 40% for symmetric ones in ProbeLab (2026) |
| Fails | Symmetric NAT on both sides; two players behind one carrier-grade NAT without hairpinning |
| Same network (LAN) | Always: address by broadcast, no code needed |
| Port forwarding, UPnP | Works where the router allows it; no trustworthy adoption figure (one 2012 study reportedly saw UPnP answer in about 35% of homes) |
| IPv6 | About half of users have it (Google 50%, APNIC 42%, April 2026). Routers are told to drop unsolicited inbound traffic (RFC 6092), so it still needs the simultaneous send; expected to raise the success rate, not measured |
| VPN overlay (Tailscale, ZeroTier) | Makes any pair a LAN. No code of ours, but the players install it and a third party's servers coordinate (free tiers: 6 users, 10 devices) |
| Relay | Every pair. Needs a server: ours, or a paid service whose secret must not ship in the client |

A public DHT (BitTorrent's) could replace the pasting with a shared word: `announce_peer`
stores a peer's NAT-mapped address under a key. It depends on other people's bootstrap nodes
and its small C library says of itself "nothing works well across NATs". Not recommended as
the first way in.

**Traffic is tiny.** From Slippi's packet layout: about 97 bytes per input packet and 44 per
acknowledgement at 60 a second, about 68 kbit/s per player. A relay carrying a whole match
forwards about 60 MB an hour; Cloudflare's TURN gives 1,000 GB a month free, about 16,000
pair-hours. The cost of a relay is the server that hands out its credentials, not bandwidth.

## What would be built from

| | Licence | Role |
|-|-|-|
| libjuice | MPL-2.0, plain C, no dependencies | STUN and hole punching (ICE); includes a small TURN server |
| ENet | MIT, plain C | Reliable and unreliable packets over UDP; Slippi's transport. Optional: input packets with redundancy need nothing more than raw UDP |
| GGPO | MIT; last commit 2019, builds on Windows only | The reference design for rollback (input queues, prediction, confirmed frames). Read, not linked |
| Our own | | Snapshot and restore, the input protocol, desync checksums, the connect-code screen |

## What needs a server

| Need | Server? |
|-|-|
| Two friends playing or training together | No (with the 15 to 30% caveat) |
| Connect codes without pasting | A rendezvous: a few lines of code on any small host |
| Every pair connects | A relay |
| Ranked play, matchmaking, accounts, trusted results | Yes. Results also need protecting: either the server replays submitted inputs or both clients sign what they saw |

## Risks and unknowns

- ~~The native build has no graphics, audio or real controller input.~~ It has all three
  since 2026-11-13 (`native-ai.md`).
- **32-bit only.** The game's code assumes 4-byte pointers. Linux and Windows run 32-bit
  programs; current macOS does not.
- ~~Drills are not on the native build.~~ They are (`tools/melee_course/`); tandem training
  still needs a session that a drill runs in.
- **Exactness across machines** as above. Two copies of one binary is the supported case.
- The native build still differs from the console in known ways (`native-port.md`). Both
  players would share those differences, so they do not desync, but it is not yet the game.
- Fightcade's connection method was not verified; Slippi's rollback design was read from
  source, no write-up was found.

## Order of work

1. **Now, no new code:** two people can already train together through Slippi's direct
   connect with the overlay build (`slippi-tandem.md`), if both have Slippi accounts.
2. **Snapshot and restore, headless:** done 2026-11-13 ("Built").
3. **A playable native build:** done 2026-11-13.
4. **Connect codes:** STUN, the code screen, simultaneous send, LAN discovery, desync
   detection.
5. **Optional small server:** rendezvous, relay, then ranked.

## Sources

Read 2026-11-12 by a research pass; each is where the claim above comes from.

- Slippi: `project-slippi/Ishiiruka` (branch `slippi`, `Source/Core/Core/Slippi`:
  `SlippiNetplay`, `SlippiMatchmaking`), `project-slippi/slippi-rust-extensions`
  (`matchmaking/src`); maximum rollback 7 frames, delay default 2, range 1 to 9.
- NAT traversal: Ford, Srisuresh, Kegel, "Peer-to-Peer Communication Across Network Address
  Translators" (https://bford.info/pub/net/p2pnat/); Trautwein et al.
  (https://arxiv.org/abs/2604.12484); https://probelab.io/blog/can-libp2p-punch-through-nats/ ;
  https://tailscale.com/blog/how-nat-traversal-works
- STUN and TURN: https://developers.cloudflare.com/realtime/turn/faq/ ,
  https://developers.cloudflare.com/realtime/turn/generate-credentials/ ,
  https://www.metered.ca/tools/openrelay/
- IPv6: https://blog.apnic.net/2026/04/28/google-hits-50-ipv6 ,
  https://www.rfc-editor.org/rfc/rfc6092.txt
- Signalling by hand and DHT: https://github.com/cjb/serverless-webrtc ,
  https://dolphin-emu.org/docs/guides/netplay-guide/ ,
  https://github.com/pond3r/ggpo/blob/master/doc/DeveloperGuide.md ,
  https://www.bittorrent.org/beps/bep_0005.html , https://github.com/jech/dht
- Libraries: the READMEs of `pond3r/ggpo`, `gschup/ggrs`, `paullouisageneau/libjuice`,
  `paullouisageneau/libdatachannel`, `lsalzman/enet`, `ValveSoftware/GameNetworkingSockets`;
  https://tailscale.com/pricing , https://www.zerotier.com/pricing/
- Dolphin: https://wiki.dolphin-emu.org/index.php?title=Broadband_Adapter ,
  `dolphin-emu/dolphin` `Source/Core/Core/HW/EXI/EXI_Device.h`
