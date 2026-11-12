---
schema: melee-technique/v1
id: auto-cancel
name: Auto-cancel
aliases: [autocancel, AC, auto-cancelled aerial, IASA, interruptible as soon as]
category: offense
difficulty: 2
related: [l-cancel, shffl, short-hop, fast-fall, waveland]
characters: all
summary: Landing during the first or last frames of an aerial, outside its landing-lag window, gives the normal short landing instead of the aerial's landing lag.
---

# Auto-cancel

## What it is

Each aerial has a range of frames during which landing triggers its special landing
animation (its landing lag). Landing before that range begins or after it ends gives the
ordinary landing instead, as if no attack had been used. That is an auto-cancel. No input is
required; it is purely a matter of when the character touches the ground
[wiki:Auto-canceling] [wiki:Landing_lag].

Related term: **IASA** ("interruptible as soon as") is the frame from which a move's
animation can be interrupted by another action while still in the air or on the ground. It
is separate from the auto-cancel window: an aerial can be past its IASA frame and still land
with lag, or the reverse.

## Inputs

None directly. The player arranges the jump so that landing falls in the window:

- Start the aerial early enough in the jump that it reaches its late auto-cancel frame
  before landing (often: aerial immediately out of a full hop or rising short hop, no
  fast fall, or a delayed fast fall).
- Or land during the early window, before the hitbox, which is rarely useful because early
  windows almost always end before the hitbox appears [wiki:Auto-canceling].

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Lag when auto-cancelled | the normal landing animation: 4 frames for most characters in Melee | [wiki:Landing_lag] |
| Lag when not auto-cancelled | the aerial's `landingLag`, or `lcancelledLandingLag` with [L-cancel](l-cancel.md) | [fd] |
| Window data | `autoCancelBefore` (landing before this frame auto-cancels) and `autoCancelAfter` (landing after this frame auto-cancels) per aerial | [fd] |
| Example | Fox nair: auto-cancels before frame 4 and after frame 36 of a 49-frame animation; bair before 4 / after 22; uair before 8 / after 25; dair before 5 / after 33; fair before 6 / after 48 | [web:fightcore.gg] |
| Characters able to auto-cancel all their aerials in a short hop | Ness, Luigi, Samus, Peach, Zelda | [wiki:L-canceling] |
| Compared with Smash 64 | windows are stricter and jumps shorter in Melee, so far fewer aerials auto-cancel from a short hop | [wiki:Auto-canceling] |

To decide whether aerial X auto-cancels from a jump: airtime of the jump (short or full,
with or without fast fall) minus the frame the aerial was started must exceed
`autoCancelAfter`. Airtimes are not in the sources read; measure in engine.

Special cases worth knowing (general knowledge, no numbers): projectiles fired in the air
such as [Falco](../characters/falco.md)'s laser land with normal landing when timed
correctly; [Peach](../characters/peach.md)'s float-cancelled aerials land with normal
landing lag through a different mechanic (see her character file).

## Why it matters

- A 4-frame landing is better than any L-cancelled landing (Fox's best is 7 frames
  [web:fightcore.gg]), so auto-cancelled aerials are the safest way to cover space:
  [Marth](../characters/marth.md) short hop fair/nair, [Sheik](../characters/sheik.md)
  nair/bair, [Captain Falcon](../characters/captain-falcon.md) uair/bair,
  [Fox](../characters/fox.md)/[Falco](../characters/falco.md) bair from full hop. Exact
  moves per character belong in the character files.
- It needs no L-cancel press, so there is no tech lockout risk.
- It interacts with [fast fall](fast-fall.md): fast falling may bring the landing inside
  the lag window.
- The Library's "Metagain: Autocancels" video (Sauc3) covers the same topic.

## Common errors

- Fast falling too early, landing inside the lag window (and not L-cancelling because the
  player expected an auto-cancel).
- Starting the aerial too late in the jump.
- Assuming a short hop is enough for an aerial that only auto-cancels from a full hop.
- Treating IASA as the auto-cancel frame.

## How to detect it in a training mode

- The character lands in `Landing` (normal) instead of `LandingAir*` although an
  `AttackAir*` state was active or had just been active [decomp].
- For feedback: the aerial's animation frame at the moment of landing compared with
  `autoCancelBefore` / `autoCancelAfter`; report "landed on frame F, auto-cancel from frame
  G: N frames early".
- Distinguish from a completed aerial (animation ended in the air, then normal landing).

## Drill seeds

### Auto-cancel timing

- **id:** `auto-cancel-aerial-timing`
- **Goal:** Land each aerial in its late auto-cancel window from the right jump.
- **Player:** any
- **CPU:** none, or a shielding CPU
- **Setup:** Flat stage; the drill names an aerial and a jump type (short or full hop).
- **CPU behaviour:** None / holds shield.
- **Success:** Landing state is `Landing` and the hitbox was active during the jump.
- **Fail:** `LandingAir*`.
- **Variations:** With a late fast fall; on platforms (shorter fall).
- **Data needed:** `autoCancelAfter` per aerial, jump airtimes.

### Safe poke on shield

- **id:** `auto-cancel-safe-on-shield`
- **Goal:** Hit a shield with an auto-cancelled aerial and avoid the shield grab.
- **Player:** [Marth](../characters/marth.md), [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md), [Jigglypuff](../characters/jigglypuff.md)
- **CPU:** any
- **Setup:** CPU shielding.
- **CPU behaviour:** Shield grabs when shieldstun ends.
- **Success:** Aerial hits the shield, player lands with normal landing and is out of range or acting before the grab.
- **Fail:** Grabbed, or landed with aerial lag.
- **Variations:** Retreating aerials.
- **Data needed:** Aerial data, shieldstun, grab range.

## Sources

- SSBWiki: Auto-canceling, Landing lag, L-canceling (https://www.ssbwiki.com/Auto-cancel).
- FightCore (https://www.fightcore.gg/characters/224/fox) for Fox's auto-cancel windows and
  landing lag.
- `[fd]`: project frame data dump. `[decomp]`: state names from this repository.
