---
schema: melee-technique/v1
id: out-of-shield
name: Out of shield options
aliases: [OoS, shield grab, up B out of shield, up smash out of shield, wavedash out of shield, nair out of shield, shine out of shield]
category: defense
difficulty: 3
related: [shield, powershield, shield-drop, jump-cancel, wavedash, shield-pressure, grab-and-throw, shffl]
characters: all
summary: The actions that can be started directly from shield (grab, jump and everything a jump allows, roll, spot dodge, shield drop) and how fast each character's are, which decides what can be punished after blocking.
---

# Out of shield options

## What it is

A shielding character cannot attack directly. Releasing the shield costs 15 frames
(16 for [Yoshi](../characters/yoshi.md)) [wiki:Out_of_shield]. The following actions skip
that and start on the first frame after shieldstun:

| Option | How | Notes | Source |
|-|-|-|-|
| Shield grab | Press A (or Z) while holding shield | Standing grab, see [grab-and-throw](grab-and-throw.md) | [wiki:Shield] |
| Jump | X/Y or tap up | Leads to aerials, [wavedash](wavedash.md), double jump | [wiki:Out_of_shield] |
| Up B out of shield | Jump, then up B during jump squat ([jump cancel](jump-cancel.md)) | Cannot be input on the same frame as the jump: the jump must exist for 1 frame first | [wiki:Out_of_shield] |
| Up smash out of shield | Jump, then up + A (or C-stick up) during jump squat | Same 1-frame rule | [wiki:Out_of_shield] |
| Roll / spot dodge | Smash the stick sideways / down, or C-stick | Intangibility data in [teching](teching.md) is for techs; rolls are below | [wiki:Shield] |
| [Shield drop](shield-drop.md) | Platform only | Fastest aerial from a platform | [wiki:Shield_drop] |
| Shine out of shield | [Fox](../characters/fox.md)/[Falco](../characters/falco.md): jump, down B on the first airborne frame | A pseudo jump cancel | [wiki:Out_of_shield] |

Characters who can jump out of shield can also jump during the 15-frame shield release
animation (`GuardOff`) [wiki:Out_of_shield]. [Yoshi](../characters/yoshi.md) cannot jump out
of shield at all (except in the first frames of a digital shield press) [wiki:Shield].

## Inputs

- All options must be input **after** shieldstun ends; Melee has no general input buffer.
  Exception: holding the C-stick during shieldstun buffers jump (up), roll (sideways) or
  spot dodge (down) for the first possible frame [wiki:Shieldstun].
- Aerial out of shield: jump, wait for jump squat to end, press the aerial; usually with
  [fast fall](fast-fall.md) and [L-cancel](l-cancel.md).
- Wavedash out of shield: jump, air dodge diagonally down on the first airborne frame
  (see [wavedash](wavedash.md)).
- Up B / usmash out of shield: jump and the attack input 1 frame apart or more, within
  jump squat.

## Frame data and formulas

### How to compute an out-of-shield frame

- Aerial: jump squat frames + aerial's first hit frame. Example: Fox jump squat 3
  [wiki:Jump], nair hits on frame 4, so nair out of shield hits on frame 7
  [lib:Out of Shield Options Frame Data].
- Up B or usmash: 1 (jump frame) + the move's first hit frame. Example: Marth up B hits on
  frame 5 and is frame 6 out of shield [wiki:Out_of_shield].
- Shield grab: the grab's first active frame (frame 7 for most characters, table in
  [grab-and-throw](grab-and-throw.md)).
- Whether a punish is guaranteed: attacker's remaining lag after the hit must exceed
  (shieldstun minus the hitlag difference, normally 0) + the out-of-shield frame, and the
  option must reach after pushback. Shieldstun formula is in [shield](shield.md).

### Jump squat (frames on the ground before leaving it)

| Frames | Characters |
|-|-|
| 3 | Fox, Ice Climbers, Kirby, Pichu, Pikachu, Samus, Sheik |
| 4 | Captain Falcon, Dr. Mario, Luigi, Mario, Marth, Mr. Game & Watch, Ness, Young Link |
| 5 | Donkey Kong, Falco, Jigglypuff, Mewtwo, Peach, Roy, Yoshi |
| 6 | Ganondorf, Link, Zelda |
| 8 | Bowser |

[wiki:Jump]

### Fastest hit frame out of shield per character

Frame on which the hitbox is out, counted from the first frame the character may act.
All values from Wiseman's list [lib:Out of Shield Options Frame Data]; only each
character's most relevant options are shown.

| Character | Fast options (frame) |
|-|-|
| Mr. Game & Watch | up B 2, grab 7 |
| Fox | shine 4 (intangible on 4), nair 7, bair 7, grab 7, usmash 8, dair 8 |
| Dr. Mario | up B 4, grab 7, nair 7, uair 8, usmash 10 |
| Mario | up B 4, grab 7, nair 7, uair 8, usmash 10 |
| Donkey Kong | up B 4, grab 8, uair 11 |
| Samus | up B 5 (intangible 2-6), fair 7, nair 8, uair 8, grab 18 |
| Falco | shine 6, grab 7, usmash 8, nair 9, bair 9, dair 10 |
| Sheik | nair 6, grab 7, bair 7, fair 8, uair 8, usmash 13 |
| Marth | up B 6, grab 7, fair 8, uair 9, nair 10, dair 10 |
| Bowser | up B 6 (fully intangible 2-5), grab 9 |
| Jigglypuff | down B (Rest) 6, grab 7, usmash 8, dair 10, nair 11 |
| Pikachu | nair 6, uair 6, grab 7, bair 7, usmash 9 |
| Pichu | nair 6, grab 7, bair 7, uair 7, usmash 10 |
| Ice Climbers | dair 6, grab 7, nair 9, uair 9 |
| Zelda | usmash 6, bair 11, grab 12, nair 12 |
| Luigi | up B 7, grab 7, nair 7, uair 9, usmash 10 |
| Peach | up B 7, grab 7, nair 8, bair 11 |
| Captain Falcon | grab 7, uair 10, nair 11, up B 14 |
| Ganondorf | grab 7, uair 12, nair 13 |
| Roy | grab 7, up B 10, fair 10, uair 10 |
| Mewtwo | grab 7, usmash 10, nair 10, fair 10 |
| Kirby | grab 7, bair 9, nair 13, fair 13 |
| Ness | grab 8, nair 9, fair 12 |
| Young Link | bomb toss 7, nair 8, up B 9, uair 9, grab 11 |
| Link | bomb toss 7, up B 9, nair 10, grab 11 |
| Yoshi | grab 18 (no jump out of shield) |

The same list states that all spot dodges are intangible from frame 2 and all rolls from
frame 4 [lib:Out of Shield Options Frame Data]. Per-character dodge data from FightCore
agrees with exceptions: spot dodge is intangible from frame 2 (Captain Falcon and Zelda 3,
Bowser 4) and lasts 22 frames for most characters; rolls are intangible frames 4-19 and last
31 frames for most characters [web:fightcore.gg].

### Other facts

- A [powershield](powershield.md) on a physical hit adds every grounded attack to the list
  with a 1-frame delay [wiki:Perfect_shield].
- Wavedash straight down or back out of shield is faster than releasing shield for some
  characters [wiki:Out_of_shield]: jump squat + 10 frames of landing lag [wiki:Landing_lag]
  versus 15.
- Frame-advantage tables assume aerials hit the shield as late as possible and are
  L-cancelled; a hit high on the shield is less safe than listed [wiki:Out_of_shield].

## Why it matters

Out-of-shield speed defines each character's defense. Fox's frame 4 shine and
Mr. Game & Watch's frame 2 up B punish things that are safe against the rest of the cast;
characters whose best option is a frame 7 grab lose to well-spaced or well-timed aerials.
Most "X out of shield against Y" drills are built from this table plus shieldstun.

## Common errors

- Inputting during shieldstun: nothing happens, then the shield stays up (no buffer).
- Shield grabbing a spaced or crossed-up attack: the grab whiffs and has long lag.
- Up B / usmash input on the same frame as jump, or too late: the character jumps and does
  a rising aerial or an airborne up B instead.
- Shine out of shield one frame late: Fox rises and shines in the air, slower and higher.
- Aerial out of shield in the wrong direction after a cross-up.
- Rolling: rolls are intangible only from frame 4 and are reactable.

## How to detect it in a training mode

- Start of the measurement: last frame of `GuardSetOff` (shieldstun). The fastest possible
  action is the next frame.
- Option taken = the first non-guard state: `Catch` (shield grab), `KneeBend` (jump),
  `EscapeF/B` (roll), `EscapeN` (spot dodge), `Pass` (shield drop), `GuardOff` (released)
  [decomp].
- Usmash / up B out of shield: `KneeBend` followed by `AttackHi4` or the up-special state
  before the character becomes airborne.
- "Frames lost" = (frame the option started) - (first actionable frame). Report it.
- Success for a punish drill: the player's hitbox or grab connects while the CPU is still in
  the lag of its move.

## Drill seeds

### Fastest option out of shield

- **id:** `out-of-shield-reaction-speed`
- **Goal:** Act on the first frame after shieldstun.
- **Player:** any
- **CPU:** any
- **Setup:** Player holding shield, CPU adjacent.
- **CPU behaviour:** Hits the shield with one move at a random time.
- **Success:** Player's chosen option starts within 2 frames of shieldstun ending.
- **Fail:** Later than that, or the wrong state (e.g. `GuardOff`).
- **Variations:** Different shieldstun lengths (weak jab vs strong smash); require a specific option.
- **Data needed:** Shieldstun formula, damage of the CPU move.

### Punish an unsafe aerial

- **id:** `out-of-shield-punish-unsafe-aerial`
- **Goal:** Choose and execute the option that reaches and is fast enough.
- **Player:** any; e.g. [Fox](../characters/fox.md) shine, [Marth](../characters/marth.md) grab/up B, [Sheik](../characters/sheik.md) nair/grab
- **CPU:** [Falco](../characters/falco.md), [Fox](../characters/fox.md), [Captain Falcon](../characters/captain-falcon.md), [Marth](../characters/marth.md)
- **Setup:** Player shielding at centre stage; CPU approaches with a SHFFL aerial.
- **CPU behaviour:** Aerial on shield, with or without L-cancel (randomised), then jab, shine, grab or shield.
- **Success:** Player hits or grabs the CPU before the CPU's next action comes out.
- **Fail:** Player is hit, grabbed, or does nothing punishing within the window.
- **Variations:** Cross-up vs in front; early vs late aerial; CPU follows with shine (Fox/Falco).
- **Data needed:** CPU aerial damage and landing lag, player's out-of-shield table.

### Up B / up smash out of shield timing

- **id:** `out-of-shield-jump-cancel-upb`
- **Goal:** Clean jump-cancelled up B or usmash from shield.
- **Player:** [Marth](../characters/marth.md), [Bowser](../characters/bowser.md), [Samus](../characters/samus.md), [Dr. Mario](../characters/dr-mario.md), [Mario](../characters/mario.md), [Fox](../characters/fox.md) (usmash), [Pikachu](../characters/pikachu.md) (usmash)
- **CPU:** any
- **Setup:** As above.
- **CPU behaviour:** Hits shield, stays in range.
- **Success:** Move starts from `KneeBend` (grounded) and hits.
- **Fail:** Character became airborne first, or no move.
- **Variations:** Speed requirement tightened to frame-perfect.
- **Data needed:** Jump squat length.

### Wavedash out of shield escape

- **id:** `out-of-shield-wavedash-escape`
- **Goal:** Reset spacing against pressure.
- **Player:** any; most useful for [Luigi](../characters/luigi.md), [Marth](../characters/marth.md), [Ice Climbers](../characters/ice-climbers.md), [Samus](../characters/samus.md)
- **CPU:** [Fox](../characters/fox.md), [Falco](../characters/falco.md)
- **Setup:** Player shielding; CPU pressures.
- **CPU behaviour:** Aerial then grab, or aerial then shine, randomly.
- **Success:** Player reaches `LandingFallSpecial` away from the CPU and is not hit or grabbed.
- **Fail:** Hit or grabbed.
- **Variations:** Wavedash back then punish.
- **Data needed:** Jump squat, traction.

## Sources

- SSBWiki: Out of shield, Shield, Shieldstun, Perfect shield, Jump (jump squat table),
  Landing lag (https://www.ssbwiki.com/Out_of_shield).
- Melee Library: "Out of Shield Options Frame Data" by Wiseman
  (http://smashboards.com/threads/out-of-shield-options-frame-data.294336/, read through
  the Wayback Machine).
- FightCore (https://www.fightcore.gg/) character pages for dodge and grab frames.
- `[decomp]`: state names from this repository.
