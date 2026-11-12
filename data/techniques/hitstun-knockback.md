---
schema: melee-technique/v1
id: hitstun-knockback
name: Knockback, hitstun and hitlag
aliases: [knockback formula, launch speed, hitstun, hitlag, freeze frames, tumble, stale moves, Sakurai angle, knockback stacking]
category: mechanics
difficulty: 1
related: [di, sdi, asdi, crouch-cancel, teching, shield, jab-reset, meteor-cancel, grab-and-throw, chain-grab]
characters: all
summary: The formulas that turn a hit into hitlag, launch speed, launch angle and hitstun, and the thresholds (tumble, knockdown, Sakurai angle) every combo, kill and drill depends on.
---

# Knockback, hitstun and hitlag

## What it is

Every hit in Melee is resolved in this order:

1. **Hitlag** (freeze frames): attacker and victim freeze for a number of frames that depends
   on damage. The victim can [SDI](sdi.md) during it.
2. On the last frame of hitlag the game reads the victim's stick for [DI](di.md) and
   [ASDI](asdi.md).
3. The victim is launched with a **launch speed** proportional to **knockback** (KB) at the
   hitbox's angle (modified by DI) and is in **hitstun** (cannot act) for a number of frames
   proportional to KB.
4. If KB is above the **tumble** threshold the victim is knocked down when they reach the
   ground unless they [tech](teching.md). Below it they land on their feet.

A training mode needs these formulas to decide which percents a scenario works at, what the
CPU can do after being hit and when.

## Inputs

None. This is a game mechanic, not a player technique. The player-controlled parts are
[DI](di.md), [SDI](sdi.md), [ASDI](asdi.md), [crouch cancel](crouch-cancel.md) and
[teching](teching.md).

## Frame data and formulas

### Knockback

```
KB = ( ( ( (p/10 + p*d/20) * 200/(w+100) * 1.4 ) + 18 ) * s ) + b ) * r
```
[wiki:Knockback]

| Symbol | Meaning | Source |
|-|-|-|
| p | Victim percent after the hit's damage is added. In Melee: floored percent before the hit plus the damage dealt that frame, staling included | [wiki:Knockback] |
| d | Damage of the hitbox. In Melee this is the unstaled damage, except for projectiles, which use staled damage | [wiki:Knockback] |
| w | Victim weight. Set to 100 for weight-independent hits; all throws use 100 | [wiki:Knockback] [wiki:Throw] |
| s | Knockback growth / 100 | [wiki:Knockback] |
| b | Base knockback | [wiki:Knockback] |
| r | Product of ratios: crouch cancel 0.666667, hitting a smash charge 1.2, frozen victim 0.25, handicap, launch rate, etc. | [wiki:Knockback] |

- **Set knockback** (`weightDepKb` in the frame data dump): if a hitbox has a fixed knockback
  value, d is replaced by that value and p is always 10. The result does not depend on
  percent, damage or staling, but still depends on weight and r [wiki:Knockback].
- **Launch speed** = KB x 0.03 units per frame. It decays by 0.051 per frame. While it lasts,
  air friction is off but gravity/fall speed still applies, which is why fastfallers survive
  vertical hits longer than their weight suggests [wiki:Knockback].
- **Bouncing** off a floor from a downward hit removes 20% of the vertical speed; bouncing off
  a wall or ceiling removes 20% of total speed. Hitstun is not reduced [wiki:Knockback].
- Knockback of 160 or more flashes the screen white [wiki:Knockback].

### Hitstun and tumble

- **Hitstun frames = floor(KB x 0.4)** [wiki:Hitstun].
- **Tumble** (state `DamageFly*`, then `DamageFall`): happens when a hit gives 32 or more
  frames of hitstun before modifiers, that is KB above 80 (the wiki table lists 80.0001 as
  the minimum) [wiki:Tumbling] [wiki:Knockback]. Only a tumbling character can
  [tech](teching.md) or be knocked down.
- **Landing cancels non-tumble hitstun.** If a character in non-tumble hitstun touches the
  ground with launch speed above 0.5 (16.67 KB), hitstun is replaced by the normal landing
  animation (4 frames for most characters) [wiki:Hitstun]. This is why
  [ASDI down](asdi.md) and [crouch cancel](crouch-cancel.md) work.
- **Reeling** (`DamageFlyRoll`): a tumble hit on a victim at 100% or more has a 30% chance of
  using the spinning animation. Cosmetic for most purposes [wiki:Tumbling].
- A tumbling character cannot air dodge in Melee; they can jump, attack, special, or tap
  left/right to exit tumble once hitstun ends [wiki:Tumbling].

### Hitlag

```
hitlag = floor( floor( floor(d/3 + 3) * e ) * c )
```
[wiki:Hitlag]

- d = damage dealt (staled). e = 1.5 for electric hits, **victim only** in Melee.
  c = 0.666667 if the victim is crouch cancelling, victim only [wiki:Hitlag].
- Cap: 20 frames [wiki:Hitlag].
- Examples computed from the formula: 4% gives 4 frames, 9% gives 6, 12% and 13% give 7,
  15% gives 8, 20% gives 9.
- A hit with zero knockback gives the victim no hitlag [wiki:Hitlag].
- Throws inflict no hitlag on release, so thrown characters cannot SDI the throw itself; hits
  that happen inside a throw animation do have hitlag [wiki:Hitlag].
- Projectiles put only the victim in hitlag, not the character who fired [wiki:Hitlag].
- SDI is impossible if hitlag is shorter than 2 frames [wiki:Smash_directional_influence].

### Sakurai angle (angle 361)

| Situation | Launch angle | Source |
|-|-|-|
| Grounded victim, KB below 32 | 0 degrees (slides along the ground) | [wiki:Sakurai_angle] |
| Grounded victim, KB 32.1 or more | 44 degrees | [wiki:Sakurai_angle] |
| Airborne victim | 45 degrees | [wiki:Sakurai_angle] |

### Staling

The game keeps a queue of the last 9 moves that connected. Each slot holding the move reduces
its damage: slot 1 (most recent) 0.09, then 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01
(0.45 in total). There is no freshness bonus in Melee [wiki:Stale-move_negation].
Because d in the knockback formula is unstaled for non-projectiles, staling barely changes
knockback; it mostly changes how much percent the hit adds [wiki:Stale-move_negation].

### Knockback stacking

If a second hit lands 10 or more frames after the first and the victim does not stay grounded,
the two launch vectors are merged per axis (same sign: the larger wins; opposite sign: they
are added). Otherwise the new knockback replaces the old. Hitstun is always that of the new
hit alone [wiki:Knockback].

### Reference knockback values

| KB | Meaning | Source |
|-|-|-|
| 32 / 32.1 | Sakurai angle switches from 0 to 44 degrees on grounded victims | [wiki:Sakurai_angle] |
| 80 | Tumble threshold | [wiki:Knockback] |
| about 186 | Kills from the centre of Final Destination at the Sakurai angle with no DI | [wiki:Knockback] |
| about 172.5 / 204.75 | Same, with DI down / DI away | [wiki:Knockback] |

## Why it matters

- Combos exist because hitstun (0.4 x KB) outlasts the attacker's remaining lag.
- "Knocks down at X%" and "breaks [crouch cancel](crouch-cancel.md) at X%" are both the
  percent where KB (after the 2/3 factor for crouch cancel) crosses 80.
- Weight changes KB; fall speed and gravity change the trajectory. Fastfallers are combo food
  because they fall back into range before hitstun ends.

## Common errors

- Treating a move's damage as its strength: base knockback and growth matter more.
- Forgetting that p is the percent **after** the hit. Published "knockdown percents" are
  usually quoted before the hit (see [asdi](asdi.md)).
- Assuming stale moves kill much later. They add less percent, but KB at a given
  post-hit percent is nearly unchanged.

## How to detect it in a training mode

- Hitlag: the fighter has a hitlag frame counter (`x195c_hitlag_frames` in this repo's
  `Fighter` struct [decomp]). Both fighters stop animating while it is positive.
- Hitstun: the victim is in a `Damage*` action state (`DamageHi1..3`, `DamageN1..3`,
  `DamageLw1..3`, `DamageAir1..3` for non-tumble; `DamageFlyHi/N/Lw/Top/Roll` for tumble)
  [decomp]. Remaining hitstun is a per-fighter counter set to floor(0.4 x KB).
- Applied knockback is stored on the fighter (`kb_applied` in the damage sub-struct [decomp]);
  compare with 80 to know whether the hit tumbled.
- "True combo": the next hit connects while the victim's hitstun counter is still positive.
- A drill generator can compute KB offline from the frame data dump (`damage`, `kbGrowth`,
  `baseKb`, `weightDepKb`, `angle`) plus the victim's weight and percent.

## Drill seeds

### Combo counter with hitstun check

- **id:** `hitstun-knockback-true-combo-check`
- **Goal:** Learn which follow-ups are true combos.
- **Player:** any
- **CPU:** any; most useful with [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Captain Falcon](../characters/captain-falcon.md)
- **Setup:** Final Destination, CPU standing at centre, percent chosen by the drill.
- **CPU behaviour:** Stands still; after each hit holds a chosen DI and techs randomly.
- **Success:** Every hit after the first connects while the CPU's hitstun counter is above 0.
- **Fail:** A hit connects after hitstun ended (display "not a true combo, N frames late").
- **Variations:** Percent sweep; DI in, away, none; random DI.
- **Data needed:** Knockback formula inputs for the moves, victim weight, hitstun counter.

### Knockdown percent quiz

- **id:** `hitstun-knockback-knockdown-threshold`
- **Goal:** Learn the percent where a move starts knocking down a given character.
- **Player:** any
- **CPU:** any
- **Setup:** CPU standing, percent stepped up by the drill each repetition.
- **CPU behaviour:** No DI, no tech.
- **Success:** Player presses a button to predict "knockdown / no knockdown" before hitting, and the prediction matches whether KB exceeded 80.
- **Fail:** Wrong prediction.
- **Variations:** CPU crouching (KB x 2/3); CPU holding down ([ASDI down](asdi.md)).
- **Data needed:** Knockback formula, weights.

## Sources

- SSBWiki: Knockback, Hitstun, Hitlag, Tumbling, Sakurai angle, Stale-move negation, Throw,
  Smash directional influence (https://www.ssbwiki.com/Knockback and sibling pages), read
  through the wikitext API.
- `[decomp]` tags refer to names in this repository (`src/melee/ft/types.h`, motion-state
  enum `ftCo_MS_*` in `src/melee/ft/forward.h`); they are field/state names, not sourced
  numbers.
- The Melee Library lists Strongbad's "Knockback, Launch Speed, Hitstun, Hitlag & Shieldstun
  Calculation" spreadsheet and Schmooblidon's ikneedata.com calculator as the community
  tools for these formulas; they were not readable in this session.
