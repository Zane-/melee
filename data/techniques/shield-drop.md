---
schema: melee-technique/v1
id: shield-drop
name: Shield drop
aliases: [shield platform drop, shielddrop, Axe method, Sung method, Shai drop, shield drop notch]
category: defense
difficulty: 4
related: [shield, out-of-shield, shield-pressure, waveland, auto-cancel, sdi]
characters: all
summary: Falling through a soft platform directly from shield, which turns shielding on a platform into the fastest way to get an aerial out against anyone below or beside it.
---

# Shield drop

## What it is

While shielding on a pass-through platform, a downward stick input that is deep enough to
pass through the platform but not fast/deep enough to trigger a spot dodge makes the
character drop through the platform straight out of shield. The character is then airborne
under the platform and can use any aerial, jump or air dodge at once. "Shield drop" here does
**not** mean releasing the shield button [wiki:Shield_drop].

## Inputs

Three common methods:

1. **Axe / Sung method (most used):** while in shield, hold the stick fully left or right
   (rolling it there slowly, or holding it there during another action such as landing lag
   or shieldstun so that no roll comes out), then rotate it down to the adjacent diagonal
   notch (full left to down-left, or full right to down-right). The diagonal notch sits in
   the narrow range that drops without spot dodging [wiki:Shield_drop].
2. **Straight down tilt:** tilt the stick down slowly/partially to the drop value. Precise;
   too far and fast gives a spot dodge [wiki:Shield_drop].
3. **Buffered during another action:** push down during a dash or during shieldstun with
   timing such that the spot dodge window has closed but the drop window is open
   [wiki:Shield_drop]. A **Shai drop** uses this from a dash: hold the stick at a 45 degree
   downward angle, press shield, then press down; the dash is cancelled into a shield drop
   [wiki:Shield_drop].

After the drop, input the aerial (or double jump, or [waveland](waveland.md) back onto the
platform).

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Width of the stick range that shield drops without spot dodging | 3 Y-axis values (controller dependent; many stock controllers hit it only on one side) | [wiki:Shield_drop] |
| Can it be done during shieldstun? | The stick position can be set up during shieldstun so the drop happens as soon as stun ends (effectively buffered) | [wiki:Shield_drop] |
| Frames from the drop to an aerial | An aerial can start about 2 frames after the drop, according to a note in Wiseman's out-of-shield list (stated there as second-hand, untested) | [lib:Out of Shield Options Frame Data] |
| Normal shield release, for comparison | 15 frames | [wiki:Out_of_shield] |
| Exact stick coordinates of the drop zone | Unknown here (Kadano's "Control Stick Input Maps" is an image album) | [lib:Control Stick Input Maps] |

Controller note: players add "shield drop notches" or pad the gate so the diagonal lands in
the 3-value range on both sides [wiki:Shield_drop].

## Why it matters

- Without it, a character shielding on a platform must jump (jump squat plus rise) or drop
  shield (15 frames). With it, a falling aerial comes out almost at once and hits opponents
  under or beside the platform. This punishes moves that are safe against every other
  [out-of-shield](out-of-shield.md) option.
- It gives [Yoshi](../characters/yoshi.md), who cannot jump out of shield, a fast option
  [wiki:Shield_drop].
- It is also a movement tool: run, shield, drop through to change levels quickly; platform
  tech chases; escaping [shield pressure](shield-pressure.md) on platforms.
- Characters with strong falling aerials benefit most: [Marth](../characters/marth.md)
  (fair, uair), [Sheik](../characters/sheik.md) (bair, fair, nair),
  [Captain Falcon](../characters/captain-falcon.md) (uair, knee),
  [Peach](../characters/peach.md), [Fox](../characters/fox.md) and
  [Falco](../characters/falco.md) (bair, dair, shine).

## Common errors

- **Spot dodge** instead of drop: stick went down too far or too fast. In game: the
  character sidesteps on the platform and is punished.
- **Roll** instead: the sideways part of the Axe method was too fast while in shield.
- **Shield just tilts down**: stick did not reach the drop value. Character stays in shield.
- Dropping but inputting the aerial late, so it comes out too low and lands with lag, or
  the character lands on the main stage before the hitbox.
- Wrong direction of drift: fell away from the opponent.

## How to detect it in a training mode

- Success: transition from `Guard` (or `GuardSetOff` ending) directly to `Pass` (the
  platform fall-through state) [decomp], with no `EscapeN` (spot dodge), `EscapeF/B` (roll)
  or `GuardOff` in between.
- Speed metric: frames between the end of shieldstun (last frame of `GuardSetOff`) and the
  first frame of `Pass`; and frames from `Pass` to the first frame of `AttackAir*`.
- Failure classes: entered `EscapeN` (too deep/fast), `EscapeF`/`EscapeB` (rolled), stayed
  in `Guard` for more than N frames after stun (too shallow), `GuardOff` (released trigger).
- Reporting the raw stick Y value on the frame of failure helps the player calibrate.

## Drill seeds

### Shield drop consistency

- **id:** `shield-drop-basic-reps`
- **Goal:** Shield drop within a few frames on both sides.
- **Player:** any
- **CPU:** none needed
- **Setup:** Player standing on a Battlefield side platform. Drill prompts "left" or "right".
- **CPU behaviour:** None.
- **Success:** `Guard` to `Pass` within N frames of the prompt, using the prompted side.
- **Fail:** Spot dodge, roll, or timeout.
- **Variations:** Start from a [waveland](waveland.md) onto the platform; start from a full hop landing; Shai drop from a dash.
- **Data needed:** State transitions only.

### Shield drop punish out of shieldstun

- **id:** `shield-drop-aerial-punish`
- **Goal:** Punish an attack on shield with shield drop aerial.
- **Player:** [Marth](../characters/marth.md), [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md), [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Peach](../characters/peach.md)
- **CPU:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Marth](../characters/marth.md), [Sheik](../characters/sheik.md)
- **Setup:** Player shielding on a side platform; CPU below or beside.
- **CPU behaviour:** Jumps and hits the shield with an aerial (e.g. Fox full hop nair, Marth uair from below), lands, then shields or jumps away after its lag.
- **Success:** Player's aerial hits the CPU before the CPU is actionable.
- **Fail:** No drop, drop too slow (CPU shields or escapes), or player is hit.
- **Variations:** CPU hits from below vs from the side; CPU double-hits the shield; Yoshi's Story platform heights vs Battlefield vs Pokemon Stadium.
- **Data needed:** CPU aerial damage (shieldstun), landing lag, platform heights, player aerial startup.

### Shield drop under pressure

- **id:** `shield-drop-vs-platform-pressure`
- **Goal:** Escape repeated up-airs or up-tilts on shield.
- **Player:** any
- **CPU:** [Marth](../characters/marth.md), [Captain Falcon](../characters/captain-falcon.md)
- **Setup:** Player shielding on a platform, shield at reduced health; CPU below.
- **CPU behaviour:** Repeats utilt/uair with random gaps.
- **Success:** Player leaves the platform by shield drop in a gap and is not hit for 60 frames.
- **Fail:** Shield poke, shield break, or hit after dropping.
- **Variations:** Require a counter-hit instead of only escaping.
- **Data needed:** Shield health formulas, CPU move timings.

## Sources

- SSBWiki: Shield drop (Shield platform drop), Out of shield
  (https://www.ssbwiki.com/Shield_drop).
- Melee Library: "Out of Shield Options Frame Data" (Wiseman; read through the Wayback
  Machine). Cards on this topic that could not be read (video/image/403): "How to Shield Drop
  Fast and Consistently" (Victra), "Shielddropping Tutorial" (SSBM Tutorials),
  "Shielddropping" (DashDanceDan), "Platforms 101" (Phanna), "Shai Drop" (Shai), "Control
  Stick Input Maps" (Kadano), "Do Anything Out of Shield" (Ambisinister).
- `[decomp]`: state names from this repository.
