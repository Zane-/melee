---
schema: melee-technique/v1
id: wavedash
name: Wavedash
aliases: [WD, wavedashing, wavesmash, wavesurf, wavedrop, waveshine movement, wavedash back, wavedash out of shield]
category: movement
difficulty: 2
related: [waveland, jump-cancel, short-hop, out-of-shield, ledgedash, dash-dance, edgeguarding]
characters: all
summary: Jumping and immediately air dodging diagonally into the ground converts the air dodge's speed into a ground slide during which the character counts as standing and can do any grounded action.
---

# Wavedash

## What it is

An air dodge gives the character a burst of speed in the stick direction. If the character
touches the ground during it, the air dodge ends in the special landing state and the
horizontal speed is kept, so the character slides, slowed only by traction. The game treats
the sliding character as standing: after the landing lag they can jab, tilt, smash, grab,
shield, jump or dash, facing the same way as before. A wavedash is that slide done straight
out of a grounded jump [wiki:Wavedash].

Named variants [wiki:Wavedash]:

- **Wavedash back / forward:** slide away or toward while keeping facing.
- **Wavesmash, wavegrab, etc.:** attack during the slide.
- **Wavesurf:** dash, then wavedash (the dash speed carries through jump squat).
- **Wavedrop:** air dodge straight down: no slide, just the landing.
- **[Waveland](waveland.md):** the same slide from an existing jump or fall instead of
  from the ground.

## Inputs

1. Press X or Y (jump). The character enters jump squat (`KneeBend`).
2. On the first airborne frame, press L or R fully (air dodge needs the digital press
   [wiki:Air_dodge]) with the control stick held diagonally down-left or down-right.
3. The character lands at once in `LandingFallSpecial` and slides.

The stick can be moved to the diagonal during jump squat. Tap jump works but is harder.
From a crouch the stick is already down, which is an easy way to learn [wiki:Wavedash].

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Jump squat before the air dodge can start | 3-8 frames by character (table below) | [wiki:Jump] |
| Landing lag after the air dodge lands | 10 frames (`LandingFallSpecial`) | [wiki:Landing_lag] [wiki:Wavedash] |
| Total time before acting | jump squat + the airborne frame(s) + 10; with a 3-frame jump squat about 14 frames, with 8 about 19 (derived; the exact off-by-one was not verified) | derived |
| Angle for maximum length | 17.1 degrees below horizontal with perfect timing; riskier than a steeper angle because small errors miss the ground | [wiki:Wavedash] |
| What sets the length | initial air dodge speed along the ground, then traction; lower traction = longer slide | [wiki:Wavedash] |
| Traction doubling | in landing states (including `LandingFallSpecial`) traction is doubled while horizontal speed exceeds the character's maximum walk speed, so a higher walk speed also lengthens the slide | [wiki:Traction] |
| Air dodge too late | full air dodge (49 frames for most) ending in helpless fall | [wiki:Air_dodge] |

### Jump squat

| Frames | Characters |
|-|-|
| 3 | Fox, Ice Climbers, Kirby, Pichu, Pikachu, Samus, Sheik |
| 4 | Captain Falcon, Dr. Mario, Luigi, Mario, Marth, Mr. Game & Watch, Ness, Young Link |
| 5 | Donkey Kong, Falco, Jigglypuff, Mewtwo, Peach, Roy, Yoshi |
| 6 | Ganondorf, Link, Zelda |
| 8 | Bowser |

[wiki:Jump]

### Traction

| Traction | Characters |
|-|-|
| 0.1 | Link, Peach, Pichu, Zelda |
| 0.09 | Jigglypuff, Pikachu |
| 0.08 | Captain Falcon, Donkey Kong, Falco, Fox, Kirby, Sheik, Young Link |
| 0.07 | Ganondorf |
| 0.06 | Bowser, Dr. Mario, Mario, Marth, Mr. Game & Watch, Ness, Roy, Samus, Yoshi |
| 0.04 | Mewtwo |
| 0.035 | Ice Climbers |
| 0.025 | Luigi |

[wiki:Traction]

### Wavedash length ranking (longest first, best angle)

1 Luigi, 2 Ice Climbers, 3 Mewtwo, 4 Marth, 5 Yoshi, 6-9 Dr. Mario / Mario /
Mr. Game & Watch / Samus, 10 Roy, 11 Ness, 12 Bowser, 13 Fox, 14 Falco, 15 Ganondorf,
16 Young Link, 17-18 Donkey Kong / Sheik, 19-21 Pikachu / Kirby / Captain Falcon,
22 Jigglypuff, 23 Pichu, 24 Link, 25-26 Peach / Zelda [wiki:Wavedash]. Distances in units
were not given by the source.

## Why it matters

- Movement with all grounded options available: unlike a dash, the character can smash,
  tilt, jab or standing-grab at any point of the slide and can move backward while facing
  forward [wiki:Wavedash].
- Spacing: wavedash back to make an attack miss, then punish; wavedash forward into grab or
  smash.
- Main movement for low-traction, slow-dash characters ([Luigi](../characters/luigi.md),
  [Ice Climbers](../characters/ice-climbers.md), [Mewtwo](../characters/mewtwo.md))
  [wiki:Wavedash].
- [Out of shield](out-of-shield.md): jump out of shield into wavedash to escape pressure.
- Wavedash back off the edge to grab the ledge instantly ([edgeguarding](edgeguarding.md)).
- After Fox/Falco down B (shine): jump-cancel the shine into a wavedash ("waveshine") to
  follow the opponent.
- Costs: the character is committed for jump squat plus 10 frames and cannot dash attack
  during the slide [wiki:Wavedash].

## Common errors

- **Air dodge too late:** the character rises and air dodges in the air (visible dodge,
  then helpless fall). Near the ledge this can be a self-destruct.
- **Air dodge too early (during jump squat):** L/R on the ground gives a shield or, with
  the stick sideways/down, a roll or spot dodge.
- **Stick too vertical:** short or no slide (a wavedrop).
- **Stick too horizontal:** the air dodge travels sideways above the ground and lands late
  or not at all.
- **Analog-only trigger press:** no air dodge; the character just jumps.
- Timing carried over from another character with a different jump squat.

## How to detect it in a training mode

- Success pattern: `KneeBend` (N frames) -> `JumpF`/`JumpB` (0-2 frames) -> `EscapeAir`
  -> `LandingFallSpecial` with non-zero horizontal ground speed [decomp].
- "Perfect": `EscapeAir` begins on the first airborne frame.
- Metrics: frames airborne before `EscapeAir`; air dodge stick angle; slide distance
  (position at the end of `LandingFallSpecial` minus position at its start); frames from
  jump press to first actionable frame.
- Failure classes: `EscapeAir` lasting more than a few frames without landing (late or
  flat); `GuardOn`/`EscapeF/B/N` right after `KneeBend` was expected (early); slide distance
  below a threshold (steep).

## Drill seeds

### Wavedash distance and consistency

- **id:** `wavedash-basic-reps`
- **Goal:** Frame-tight wavedashes of a target length in both directions.
- **Player:** any
- **CPU:** none
- **Setup:** Flat stage, markers at the target distance.
- **CPU behaviour:** None.
- **Success:** `EscapeAir` on the first or second airborne frame and slide distance within the target band, 10 times in a row alternating directions.
- **Fail:** Airborne air dodge, shield/roll, or short slide.
- **Variations:** Out of dash (wavesurf); out of shield; consecutive wavedashes; wavedash then immediate action (jab, grab).
- **Data needed:** Jump squat length, traction, expected maximum distance (measure in engine).

### Wavedash back punish

- **id:** `wavedash-back-whiff-punish`
- **Goal:** Dodge an approach by wavedashing back and punish its lag.
- **Player:** [Marth](../characters/marth.md), [Luigi](../characters/luigi.md), [Fox](../characters/fox.md), [Samus](../characters/samus.md), any
- **CPU:** [Captain Falcon](../characters/captain-falcon.md), [Sheik](../characters/sheik.md), [Fox](../characters/fox.md)
- **Setup:** Characters at mid range on Final Destination.
- **CPU behaviour:** After a random delay, dashes in with dash attack, grab, or SHFFL aerial aimed at the player's starting position.
- **Success:** CPU's move misses and the player hits or grabs the CPU during its lag.
- **Fail:** Player is hit, or no punish.
- **Variations:** CPU overshoots sometimes (player must shield or wavedash farther); smaller starting distance.
- **Data needed:** CPU move ranges and lag; player wavedash distance.

### Wavedash to ledge

- **id:** `wavedash-back-ledge-grab`
- **Goal:** Grab the ledge from the stage as fast as possible.
- **Player:** any
- **CPU:** none (or a recovering CPU, see [edgeguarding](edgeguarding.md))
- **Setup:** Player standing near the edge facing centre.
- **CPU behaviour:** None.
- **Success:** `CliffCatch` within N frames of the jump input.
- **Fail:** Slides short and stays on stage, or air dodges off stage.
- **Variations:** Start from a run toward the edge (turn, then wavedash back).
- **Data needed:** Distance to ledge, traction.

## Sources

- SSBWiki: Wavedash, Jump, Traction, Air dodge, Landing lag
  (https://www.ssbwiki.com/Wavedash).
- Melee Library cards on practice ("How to Practice Execution", Sycorax; "DIY Movement
  Drills", KirbyKaze; "Wavedash Out of Shield 2 Methods", PewPewU) were not read in detail;
  no numbers are taken from them.
- `[decomp]`: state names from this repository.
