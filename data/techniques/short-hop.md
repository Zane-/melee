---
schema: melee-technique/v1
id: short-hop
name: Short hop
aliases: [SH, shorthop, short hop aerial, short hop laser, SHL, full hop]
category: movement
difficulty: 2
related: [shffl, fast-fall, l-cancel, jump-cancel, auto-cancel, wavedash]
characters: all
summary: Releasing the jump button before jump squat ends gives a lower jump, which lets aerials hit grounded opponents and land quickly.
---

# Short hop

## What it is

Every grounded jump starts with jump squat (`KneeBend`). If the jump input (button or stick)
is no longer held when jump squat ends, the character does a short hop: a jump with lower
initial speed and therefore less height and airtime than a full hop [wiki:Short_hop].

## Inputs

- Press X or Y and release it before the last frame of jump squat. Tap jump works the same
  way with the stick [wiki:Short_hop].
- Then, optionally, an aerial, a special (short hop laser), an air dodge
  ([waveland](waveland.md)) or a double jump.

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Window to release | jump squat length minus 1 frame. Fox (3-frame jump squat) must release before the 3rd frame: a 2-frame window | [wiki:Short_hop] |
| Jump squat lengths | 3: Fox, Ice Climbers, Kirby, Pichu, Pikachu, Samus, Sheik. 4: Captain Falcon, Dr. Mario, Luigi, Mario, Marth, Mr. Game & Watch, Ness, Young Link. 5: Donkey Kong, Falco, Jigglypuff, Mewtwo, Peach, Roy, Yoshi. 6: Ganondorf, Link, Zelda. 8: Bowser | [wiki:Jump] |
| Actions during jump squat | up smash, up B, grab ([jump cancel](jump-cancel.md)) | [wiki:Jump-canceling] |

So the release windows are 2 frames (3-frame jump squat), 3, 4, 5 and 7 frames (Bowser).

### Short hop height

Units are game units; "% of full hop" is the wiki's comparison column [wiki:Short_hop].

| Character | Short hop height | % of full hop |
|-|-|-|
| Samus | 21.05 | 65.0 |
| Sheik | 18.03 | 57.6 |
| Zelda | 16.74 | 57.4 |
| Yoshi | 16.53 | 51.1 |
| Peach | 15.21 | 52.2 |
| Ganondorf | 14.40 | 58.3 |
| Luigi | 13.51 | 33.3 |
| Kirby | 13.32 | 55.5 |
| Captain Falcon | 12.95 | 36.6 |
| Marth | 12.50 | 38.2 |
| Pikachu, Pichu | 12.30 | 41.8 |
| Donkey Kong | 12.01 | 34.2 |
| Ness | 11.76 | 35.1 |
| Mewtwo | 11.26 | 36.2 |
| Falco | 9.69 | 20.4 |
| Mario, Dr. Mario, Mr. Game & Watch | 9.63 | 36.1 |
| Link | 9.49 | 34.9 |
| Young Link | 9.49 | 31.7 |
| Roy | 9.13 | 32.2 |
| Ice Climbers | 9.11 | 28.0 |
| Bowser | 9.06 | 31.5 |
| Fox | 8.57 | 31.0 |
| Jigglypuff | 8.10 | about 42 |

Airtime of a short hop (frames from leaving the ground to landing) per character is not in
the sources read; it can be measured in engine or computed from jump force, gravity and
fall speed. It decides which aerials [auto-cancel](auto-cancel.md) in a short hop: per the
wiki only Ness, Luigi, Samus, Peach and Zelda can auto-cancel all their aerials in a short
hop [wiki:L-canceling].

## Why it matters

- Aerials are the main attacks in Melee; a short hop puts them at the height of a standing
  opponent and returns the character to the ground quickly ([SHFFL](shffl.md)).
- Short hop projectiles: [Falco](../characters/falco.md) and [Fox](../characters/fox.md)
  lasers, [Sheik](../characters/sheik.md) needles.
- Short hop is the entry to many character techniques (double lasers, short hop double
  aerials for Marth, Sheik, Captain Falcon and others).
- Characters with 3-frame jump squats have the hardest short hop (2-frame window); Fox's is
  the standard example.

## Common errors

- Holding the button too long: full hop. In game: the aerial goes over the opponent and the
  character is airborne and punishable for much longer.
- Compensating by pressing too lightly and missing the press.
- Short hop but late aerial: the hitbox comes out too late or the character lands first.
- Using short hop where a full hop is needed (e.g. to clear a projectile).

## How to detect it in a training mode

- At the end of `KneeBend`, the game picks short or full hop from whether jump is still
  held. Observable: initial vertical velocity on the first airborne frame (`JumpF`/`JumpB`)
  equals the character's short hop or full hop jump force; or apex height.
- Input feedback: frames the jump button was held, compared with the window (jump squat
  minus 1).
- For short hop aerial drills: frame the aerial started relative to leaving the ground, and
  whether the hitbox was out before landing.

## Drill seeds

### Short hop consistency

- **id:** `short-hop-reps`
- **Goal:** Short hop 20 times in a row.
- **Player:** any; hardest with [Fox](../characters/fox.md), [Sheik](../characters/sheik.md), [Pikachu](../characters/pikachu.md), [Samus](../characters/samus.md), [Ice Climbers](../characters/ice-climbers.md)
- **CPU:** none
- **Setup:** Flat stage.
- **CPU behaviour:** None.
- **Success:** Each jump is a short hop; display frames held.
- **Fail:** Full hop.
- **Variations:** Out of a dash; out of shield; alternating short and full hops on prompt.
- **Data needed:** Jump squat length.

### Short hop laser

- **id:** `short-hop-laser-height`
- **Goal:** Short hop laser at a controlled height and land without lag.
- **Player:** [Falco](../characters/falco.md), [Fox](../characters/fox.md)
- **CPU:** any, standing at range
- **Setup:** Final Destination, far apart.
- **CPU behaviour:** Stands, or walks forward shielding.
- **Success:** Laser hits the CPU at the prompted height (high or low) and the player lands with the laser's landing auto-cancelled.
- **Fail:** Full hop, no laser, or landing lag.
- **Variations:** Approaching and retreating lasers; double laser.
- **Data needed:** Laser startup, short hop airtime.

### Short hop aerial spacing

- **id:** `short-hop-aerial-tipper`
- **Goal:** Hit a shield with the tip of a short hop aerial and land out of grab range.
- **Player:** [Marth](../characters/marth.md), [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md)
- **CPU:** any, shielding
- **Setup:** Mid range.
- **CPU behaviour:** Shield grab after blocking.
- **Success:** Aerial connects with the shield and the grab whiffs.
- **Fail:** Grabbed or aerial missed.
- **Variations:** Retreating aerial with drift back.
- **Data needed:** Aerial hitbox reach, CPU grab range ([grab-and-throw](grab-and-throw.md)).

## Sources

- SSBWiki: Short hop, Jump (jump squat table), Jump-canceling, L-canceling
  (https://www.ssbwiki.com/Short_hop).
- `[decomp]`: state names from this repository.
