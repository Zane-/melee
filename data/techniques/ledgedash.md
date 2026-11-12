---
schema: melee-technique/v1
id: ledgedash
name: Ledgedash
aliases: [ledge dash, invincible ledgedash, GALINT, grounded actionable ledge intangibility, haxdash, ledgestall, aerial interrupt ledgedash]
category: ledge
difficulty: 5
related: [ledge-options, waveland, wavedash, fast-fall, edgeguarding, recovery]
characters: all
summary: Dropping from the ledge, double jumping and air dodging onto the stage so the character is standing and actionable while still intangible from the ledge grab.
---

# Ledgedash

## What it is

Grabbing the ledge gives intangibility that continues after the character lets go
([ledge-options](ledge-options.md)). A ledgedash spends as little of it as possible getting
on stage: let go, double jump at once, and [waveland](waveland.md) onto the stage with an air
dodge. Whatever intangibility is left when the waveland's landing lag ends is **GALINT**
(grounded actionable ledge intangibility): frames in which the character can attack, grab or
move on stage and cannot be hit [wiki:Ledgedash] [wiki:Edge].

## Inputs

1. Hang on the ledge (`CliffWait`).
2. **Let go:** control stick or C-stick down or away from the stage. Earliest on frame 9
   after grabbing (frame 5 for [Link](../characters/link.md)).
3. **Double jump** immediately (X/Y), drifting toward the stage.
4. **Air dodge** diagonally down-toward the stage as soon as the character is high enough
   that the air dodge lands on the stage instead of hitting its side.
5. Act out of the 10-frame landing lag.

Some players fast fall for a frame or more after letting go to change the timing; exact
frames depend on character and on how the ledge was grabbed (ECB state)
[wiki:Ledgedash] [lib:How Pre-ledgegrab Body States Affect Your Ledgedash Timing].

## Frame data and formulas

### Ledge intangibility budget

| Fact | Value | Source |
|-|-|-|
| `CliffCatch` (grab animation) | 7 frames (Link 3) | [wiki:Ledgestall] |
| Ledge intangibility | lasts 30 frames longer than `CliffCatch`: 37 frames in total (Link 33) | [wiki:Ledgestall] [wiki:Ledgedash] |
| Earliest let-go | frame 9 (Link frame 5); letting go is only possible from `CliffWait`, not on the last `CliffCatch` frame | [wiki:Ledgedash] [wiki:Ledgestall] |
| Intangibility left after a frame-perfect let-go | 29 frames | [wiki:Ledgestall] |
| Ledge regrab lockout after letting go | 29 frames | [wiki:Ledgestall] |
| Air dodge landing lag (`LandingFallSpecial`) | 10 frames | [wiki:Landing_lag] |

GALINT = 29 - (frames from let-go until the character lands) - 10, for a perfect let-go.
Every frame of delay in any step costs one frame of GALINT.

### Maximum GALINT from a standard, frame-perfect ledgedash

[wiki:Ledgedash]

| Frames | Characters |
|-|-|
| 15 | Fox, Pichu |
| 14 | Dr. Mario, Falco |
| 13 | Ice Climbers, Luigi, Mario, Pikachu, Young Link |
| 12 | Kirby |
| 11 | Sheik |
| 10 | Captain Falcon |
| 9 | Jigglypuff, Link, Mr. Game & Watch |
| 8 | Bowser |
| 7 | Donkey Kong |
| 5 | Roy |
| 4 | Ganondorf, Marth, Ness, Samus |
| 2 | Yoshi, Zelda |
| 1 | Mewtwo |
| 0 | Peach |

The number depends on double jump speed and height and on the character's environmental
collision box (ECB). Peach gets 0 because her double jump dips before rising
[wiki:Ledgedash]. Slanted ledges (Yoshi's Story) allow a flatter air dodge and a longer
slide [wiki:Ledgedash].

### Variations with more GALINT

[wiki:Ledgedash]

| Character | Method | GALINT |
|-|-|-|
| Fox, Pichu / Falco / Pikachu / Sheik | double jump and regrab the ledge first, then ledgedash | 16 / 15 / 15 / 12 (Sheik 13 on Battlefield) |
| Captain Falcon | jump straight onto stage (no air dodge, no-impact land; fast fall 1 frame before jumping) | 12 |
| Ganondorf | jump straight onto stage (no-impact land) | 9 |
| Captain Falcon / Ganondorf | same, after grabbing the ledge at the apex of up B | 17 / 18 |
| Captain Falcon | bair aerial interrupt | 15 |
| Samus | uair aerial interrupt 10-11 frames after the double jump | 11 |
| Zelda | fair aerial interrupt | 13 |
| Mewtwo | nair interrupt on frame 12 of the double jump (11 on Battlefield) | 9 on Battlefield and Dream Land, 7 Yoshi's Story, 6 elsewhere |
| Yoshi | aerial interrupt exactly 16 frames after jumping / ECB set-up from double jump apex | 8 / 9 |
| Peach | sweetspot the ledge with up B before the parasol opens, then ledgedash | up to 9 |
| Bowser | regrab with down B first | 9 |
| Marth, Roy | up B apex sweetspot with delayed grab, then ledgedash upward-angled | up to 9 |
| Luigi | drop from Yoshi's Story side platform to ledge first | 15 |
| Fox | jump (frame 2 after let-go), shine (frame 4), jump (frame 7): semi-actionable intangibility | 22 Yoshi's Story, 20 Battlefield, 18 other stages |
| Falco | same with shine on frame 5, second jump frame 11 | 18 |

Kadano's note in the Library: grabbing the ledge from an un-fastfalled instant ledgehop
makes the fastest ledgedash 2 frames faster than grabbing it from a wavedash back to the
ledge, because the ECB differs; doing the same regrab before every ledgedash keeps the
timing constant [lib:How Pre-ledgegrab Body States Affect Your Ledgedash Timing].

### Related stalls

- **Ledgestall / haxdash:** let go and regrab so that intangibility is continuous; needs the
  let-go on the first possible frame because the regrab lockout (29) equals the remaining
  intangibility (29). [Fox](../characters/fox.md) and [Falco](../characters/falco.md) stall
  with up B (14-frame window to input up B after dropping and still be fully intangible).
  [Captain Falcon](../characters/captain-falcon.md) and
  [Ganondorf](../characters/ganondorf.md) can do fully intangible haxdashes (jump toward the
  stage, waveland backward to the ledge) at human level [wiki:Ledgestall].

## Why it matters

The ledge is normally a disadvantage. A good ledgedash reverses it: the returning player
gets an intangible grab, smash or combo starter, so the opponent cannot simply stand near
the ledge. It is a staple for Fox, Sheik and Captain Falcon; rare for Peach and Marth, whose
standard ledgedashes give almost nothing; Falco uses it less because his other ledge options
are strong; Jigglypuff rarely needs it [wiki:Ledgedash].

## Common errors

What each failure looks like [wiki:Ledgedash]:

- **Let-go input too early (before frame 9):** the stick input does nothing and the jump or
  shield press that follows performs a ledge jump ("tournament winner"), a normal getup or
  a ledge roll. Very punishable.
- **Air dodge too early** (character still below stage level): the air dodge goes into the
  side of the stage and the character falls helpless: a self-destruct.
- **Air dodge too late or too high:** a visible air dodge above the stage with no waveland;
  the character lands late with no intangibility left.
- **Slow double jump after letting go:** falls too low; either no stage contact or little
  GALINT.
- **Angle too vertical:** lands at the very edge with no slide, sometimes sliding back off.
- Using all the GALINT on movement and attacking after it has expired.

## How to detect it in a training mode

- Timeline to record from the `CliffCatch` start frame (t = 1): frame of leaving `CliffWait`
  (to `Fall`), frame of `JumpAerialF/B`, frame of `EscapeAir`, frame of
  `LandingFallSpecial` start, first actionable frame (landing + 10) [decomp].
- GALINT = (frame intangibility ends, t = 37, or 33 for Link) - (first actionable frame) + 1
  if positive. Display it.
- Failure classification by state: `CliffJumpQuick1/Slow1` (tournament winner),
  `CliffClimb*` or `CliffEscape*` (accidental getup/roll), `EscapeAir` ending in
  `FallSpecial` below the stage (SD), `EscapeAir` running long above stage (late).
- A stricter drill also requires an action (attack hitbox out, or grab) while intangibility
  is still active.

## Drill seeds

### GALINT counter

- **id:** `ledgedash-galint-reps`
- **Goal:** Consistent ledgedash with a minimum GALINT.
- **Player:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md), any
- **CPU:** none
- **Setup:** Player starts hanging on the ledge with fresh intangibility (state reset to the first `CliffCatch` frame, or dropped into a ledge grab for a fixed ECB).
- **CPU behaviour:** None.
- **Success:** Actionable on stage with GALINT of at least N (N chosen per character from the table, e.g. half the maximum).
- **Fail:** Less GALINT, wrong getup option, or SD.
- **Variations:** Different stages (ledge shape); both ledges; require the regrab set-up first; show per-step frame loss.
- **Data needed:** Intangibility timing above, character maximum GALINT.

### Invincible punish from ledge

- **id:** `ledgedash-intangible-attack`
- **Goal:** Hit an opponent who is covering the ledge, during GALINT.
- **Player:** [Fox](../characters/fox.md), [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md), [Falco](../characters/falco.md)
- **CPU:** [Marth](../characters/marth.md), [Sheik](../characters/sheik.md), [Peach](../characters/peach.md)
- **Setup:** Player on ledge; CPU standing at a ledge-trap distance.
- **CPU behaviour:** Throws a covering move (Marth dtilt/fsmash, Sheik ftilt, Peach dsmash) timed to hit a normal getup.
- **Success:** Player's grab or attack connects and the player takes no damage.
- **Fail:** Player is hit, or SD.
- **Variations:** CPU shields instead (player should grab); CPU stands farther away.
- **Data needed:** GALINT per character, player move startup, waveland slide distance.

### Mixed ledge options

- **id:** `ledgedash-option-mix`
- **Goal:** Use ledgedash as one option among several against a reacting opponent.
- **Player:** any
- **CPU:** any
- **Setup:** Player on ledge; CPU near.
- **CPU behaviour:** Randomly covers getup/roll (stand and react), covers ledgehop (aerial), or grabs ledge-ward space late.
- **Success:** Player reaches centre stage or lands a hit without being hit.
- **Fail:** Hit or SD.
- **Variations:** Player percent over 100 (slow getups).
- **Data needed:** [ledge-options](ledge-options.md) timings.

## Sources

- SSBWiki: Ledgedash, Ledgestall (Haxdash), Edge, Landing lag
  (https://www.ssbwiki.com/Ledgedash).
- Melee Library: "How Pre-ledgegrab Body States Affect Your Ledgedash Timing" (Kadano,
  Wayback Machine copy of the first post). "How to Efficiently Practice Ledgedashing"
  (Optimal Performance) is a video and was not viewable.
- `[decomp]`: state names from this repository.
