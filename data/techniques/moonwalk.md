---
schema: melee-technique/v1
id: moonwalk
name: Moonwalk
aliases: [moonwalking, sticky walk, boost run]
category: movement
difficulty: 4
related: [dash-dance, pivot, wavedash, edgeguarding]
characters: [captain-falcon, marth, ganondorf, fox, falco, roy]
summary: Tilting the stick backward during the initial dash without triggering a dash back makes the character slide backward at dash speed while still facing forward.
---

# Moonwalk

## What it is

During the initial dash the control stick can change the dash's speed. If the stick is moved
to the backward side slowly enough (or along the lower gate) that the game does not read a
smash input for a dash back, the dash's velocity is driven backward while the character
stays in the forward-facing dash animation. The character slides backward, and can keep
sliding after the dash ends, especially with low traction [wiki:Moonwalk] [wiki:Dash].

## Inputs

Standard method [wiki:Moonwalk]:

1. Smash forward to start a dash.
2. Move the stick to the backward side without a fast horizontal flick: roll it along the
   bottom of the gate to the lower-back diagonal notch and hold it there for at least 2
   frames.
3. Then move it to straight back.

Passing through neutral or pointing straight down at any time during the dash is allowed, so
the notch can be reached in a straight line or with a half-circle motion.

Frame-perfect variant ("perfect moonwalk"): smash the stick backward within the first 3
frames of the dash, or tilt back on frame 3 and hold fully back on the next frame. Works only
from forward dashes, not from turnaround dashes; gives slightly longer moonwalks; essentially
TAS-only [wiki:Moonwalk].

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Time available | the initial dash length: 7 (Sheik) to 18 (Mewtwo) frames; 15 for Captain Falcon, Marth, Ganondorf, Roy; 11 for Fox and Falco | [wiki:Dash] |
| Backward speed reachable | up to the character's maximum dash speed, backward | [wiki:Moonwalk] |
| Required light tilt before full back | at least 2 frames | [wiki:Moonwalk] |
| Momentum carry | the velocity before the dash is added to the initial dash speed, so existing backward speed lengthens the moonwalk | [wiki:Moonwalk] |
| After the dash ends | the character keeps sliding; low-traction characters often slide farther than they travelled during the dash | [wiki:Moonwalk] |
| Dash acceleration | base + stick-scaled part; Captain Falcon 0.01 + 0.15, Marth 0 + 0.06, Fox 0.02 + 0.10 | [wiki:Dash] |

Distances per character are not given by the source. Characters with long initial dashes and
high stick-scaled acceleration moonwalk farthest; Captain Falcon is the standard example
(general knowledge).

## Why it matters

Mostly a niche and style technique, with a few practical uses:

- Moving backward off the edge while facing the stage to edgeguard with a forward-facing
  aerial (classic: [Captain Falcon](../characters/captain-falcon.md) moonwalk off stage into
  knee or reverse aerial; [Ganondorf](../characters/ganondorf.md) similar).
- Retreating while keeping facing, as an alternative to [wavedash](wavedash.md) back.
- Charging momentum for longer jumps ("boost run" and "sticky walk" are related stick
  techniques listed in the Library's "Tutorial: Moonwalking, Sticky Walking, and Boost Run";
  not viewable here).

It is rarely required for competitive play; treat drills as optional.

## Common errors

- Stick crosses to the back too fast: dash back (a dash dance) instead of a moonwalk.
- Stick only reaches straight down: the dash just slows or stops.
- Too slow: the initial dash ends before backward speed builds; character enters run or
  stops.
- Sliding off the edge unintentionally.

## How to detect it in a training mode

- The character stays in `Dash` with unchanged `facing_dir` while horizontal velocity has
  the opposite sign to the facing [decomp]. No `Turn` state occurs.
- Metric: backward distance travelled from the frame velocity changed sign until the
  character stops; peak backward speed.
- Failure: `Turn`/new `Dash` in the opposite direction (dash back), or velocity never
  reverses.

## Drill seeds

### Moonwalk distance

- **id:** `moonwalk-distance`
- **Goal:** Moonwalk a target distance.
- **Player:** [Captain Falcon](../characters/captain-falcon.md), [Marth](../characters/marth.md), [Ganondorf](../characters/ganondorf.md)
- **CPU:** none
- **Setup:** Final Destination, marker behind the player.
- **CPU behaviour:** None.
- **Success:** Backward travel past the marker while facing forward.
- **Fail:** Dash back, or short.
- **Variations:** Both directions; chained moonwalks.
- **Data needed:** Dash frames and speeds.

### Moonwalk edgeguard

- **id:** `moonwalk-offstage-aerial`
- **Goal:** Moonwalk off the edge and hit a recovering opponent with a forward-facing aerial.
- **Player:** [Captain Falcon](../characters/captain-falcon.md), [Ganondorf](../characters/ganondorf.md)
- **CPU:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Marth](../characters/marth.md), [Sheik](../characters/sheik.md)
- **Setup:** Player on stage near the edge with back to it; CPU recovering low.
- **CPU behaviour:** Standard recovery to the ledge.
- **Success:** Aerial hits and the CPU is KO'd; player returns.
- **Fail:** Miss or SD.
- **Variations:** Distance from the edge.
- **Data needed:** Aerial startup, player recovery range.

## Sources

- SSBWiki: Moonwalk, Dash (https://www.ssbwiki.com/Moonwalk).
- Melee Library: "Tutorial: Moonwalking, Sticky Walking, and Boost Run" (Jack Kenney, video;
  title only).
- `[decomp]`: state/field names from this repository.
