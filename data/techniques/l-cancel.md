---
schema: melee-technique/v1
id: l-cancel
name: L-cancel
aliases: [L-cancelling, lag cancel, smooth landing, Z-cancel, light shield L-cancel]
category: offense
difficulty: 3
related: [shffl, auto-cancel, fast-fall, short-hop, teching, shield-pressure]
characters: all
summary: Pressing L, R or Z up to 7 frames before landing during an aerial attack halves that aerial's landing lag.
---

# L-cancel

## What it is

When a character lands while an aerial attack is still in its landing-lag window, they go
into a move-specific landing animation that is much longer than a normal landing. If the
player pressed a shield button shortly before touching the ground, that animation plays at
double speed, halving the lag. There is no drawback to L-cancelling, so it is done on every
aerial that would land with lag [wiki:L-canceling].

## Inputs

- Press L, R or Z at most 7 frames before the character lands, during the aerial.
- The trigger press can be analog (light) or digital. A digital press also counts as a
  [tech](teching.md) input and starts the tech lockout; a light press or Z does not
  [wiki:L-canceling] [wiki:Tech] [lib:Light Shield L Cancel] (card description).
- When the aerial hits something, both characters freeze in hitlag first, so the landing
  happens later than on a whiff; press later, or press during hitlag (see below).

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Window | press 7 frames or fewer before landing | [wiki:L-canceling] |
| Effect | landing animation at double speed; lag halved, rounded down | [wiki:L-canceling] |
| Press during hitlag | extends the window: the L-cancel succeeds if the character lands up to 6 frames after the hitlag ends | [wiki:L-canceling] |
| Buttons | L, R (analog or digital) or Z | [wiki:L-canceling] |
| Side effect of a digital press | opens a tech window and triggers the 40-frame tech lockout | [wiki:Tech] |
| Landing during an auto-cancel window | normal landing (4 frames for most); L-cancel irrelevant | [wiki:Auto-canceling] [wiki:Landing_lag] |
| Per-move values | `landingLag` and `lcancelledLandingLag` in the frame data dump | [fd] |
| Hitlag that shifts the timing | floor(damage/3 + 3) frames on hit or on shield | [wiki:Hitlag] |

Examples from FightCore for [Fox](../characters/fox.md): nair 15 frames of landing lag, 7
L-cancelled; uair 18 / 9; bair 20 / 10; fair 22 / 11; dair 18 / 9 [web:fightcore.gg].

The timing differs in three situations a drill should separate:

1. **Whiff:** no hitlag; press just before landing.
2. **Hit on a character:** hitlag delays the landing.
3. **Hit on shield:** same hitlag as a hit (for a full shield); a light shield is larger
   so the aerial connects earlier in the fall.

## Why it matters

Halved landing lag is what makes aerials safe on shield and lets them combo into grounded
moves. A missed L-cancel is one of the most common reasons a player gets shield-grabbed or
drops a combo. It benefits characters with heavy aerials most
([Bowser](../characters/bowser.md), [Ganondorf](../characters/ganondorf.md))
[wiki:L-canceling], and it is part of the [SHFFL](shffl.md).

## Common errors

- **Too early** (more than 7 frames before landing): full lag. Typical when the aerial
  hits and hitlag delays the landing ("missed L-cancel on shield").
- **Too late:** pressed after landing; with L/R this produces a shield after the lag, or
  nothing.
- **Hard press habits:** digital presses cause tech lockout; being hit right after means a
  missed tech.
- Pressing twice (once for whiff timing, once for hit timing) is a valid option select with
  light presses or Z, but with digital presses it burns the tech window.
- L-cancelling when the aerial would auto-cancel anyway is harmless but, with a hard press,
  still starts tech lockout.

## How to detect it in a training mode

- The landing states are `LandingAirN`, `LandingAirF`, `LandingAirB`, `LandingAirHi`,
  `LandingAirLw` [decomp]. Success = the state lasts the L-cancelled number of frames
  (animation speed doubled); failure = full length. The game itself decides this from a
  per-fighter L-cancel input timer, which a mod can read directly.
- Input feedback: frames between the last L/R/Z press and the landing frame (1-7 good);
  for failures report "N frames early" or "pressed after landing".
- Report separately for whiff / hit / shield, detected by whether the aerial's hitbox
  connected and with what.
- A landing into `Landing` (normal) during an aerial means it auto-cancelled: not a failure.

## Drill seeds

### L-cancel rate by situation

- **id:** `l-cancel-whiff-hit-shield`
- **Goal:** L-cancel regardless of whether the aerial whiffs, hits or is shielded.
- **Player:** any
- **CPU:** any
- **Setup:** CPU standing at short range.
- **CPU behaviour:** Each repetition, randomly: shields (full or light), stands and gets hit, or steps back so the aerial whiffs.
- **Success:** L-cancelled landing; running success rate shown per situation.
- **Fail:** Full landing lag.
- **Variations:** Specific aerial prompts; fast fall required; platform landings.
- **Data needed:** Aerial landing lag values, hitlag formula.

### L-cancel into follow-up

- **id:** `l-cancel-into-jab-grab`
- **Goal:** Act on the first frame after L-cancelled lag.
- **Player:** any
- **CPU:** any, shielding
- **Setup:** CPU in shield.
- **CPU behaviour:** Shield grabs as early as possible.
- **Success:** Player's next action (jab, shine, grab, spot dodge) starts within 2 frames of lag ending and beats or avoids the grab.
- **Fail:** Grabbed.
- **Variations:** CPU characters with different grab speeds.
- **Data needed:** L-cancelled lag, shieldstun, CPU grab frame.

### Lockout-safe L-cancel

- **id:** `l-cancel-light-press`
- **Goal:** L-cancel with Z or a light press and keep the tech.
- **Player:** any
- **CPU:** any
- **Setup:** As above, but the CPU hits the player with a knockdown move just after landing.
- **CPU behaviour:** Counter-hit out of shield at a fixed delay.
- **Success:** L-cancel succeeds and the player techs the counter-hit.
- **Fail:** Missed tech due to lockout, or missed L-cancel.
- **Variations:** None.
- **Data needed:** Tech lockout rules ([teching](teching.md)).

## Sources

- SSBWiki: L-canceling, Auto-canceling, Landing lag, Tech, Hitlag
  (https://www.ssbwiki.com/L-canceling).
- FightCore (https://www.fightcore.gg/characters/224/fox) for Fox's landing lag values.
- Melee Library: "Light Shield L Cancel" (MikeHaze, video) and "How to Implement Option
  Selects in Melee" (Gravy, Reddit; not fetchable) by description only.
- `[fd]`: project frame data dump. `[decomp]`: state names from this repository.
