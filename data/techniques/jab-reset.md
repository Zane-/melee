---
schema: melee-technique/v1
id: jab-reset
name: Jab reset
aliases: [reset, lock, missed tech reset, half-reset, forced getup]
category: punish
difficulty: 3
related: [teching, tech-chase, sdi, asdi, hitstun-knockback]
characters: all
summary: Hitting an opponent who missed a tech with a weak attack forces them into a standing getup they cannot choose or cancel, giving a free strong punish.
---

# Jab reset

## What it is

A character who misses a [tech](teching.md) bounces and then lies on the floor. If they are
hit during the bounce or while lying down by an attack that is weak enough, they do a small
hop and are then forced into a neutral getup instead of choosing a getup option. The attacker
knows exactly when and where they will stand and can prepare any punish (a charged smash, a
grab, [Jigglypuff](../characters/jigglypuff.md)'s Rest). Melee's version is called a reset;
later games call the similar mechanic a lock [wiki:Lock].

## Inputs

1. Cause a knockdown the opponent does not tech (states `DownBound*`, `DownWait*`).
2. Hit them with a qualifying weak move, usually jab, a weak tilt, or a weak projectile
   (for example [Falco](../characters/falco.md) laser, [Fox](../characters/fox.md) jab,
   [Sheik](../characters/sheik.md) jab or needle, [Marth](../characters/marth.md) jab or
   dtilt at low percent; character-specific choices are in the character files).
3. During the forced getup, position and hit with the strong punish as soon as they are
   vulnerable.

## Frame data and formulas

Rules as stated by the wiki [wiki:Lock]:

| Rule | Value |
|-|-|
| Damage limit | the attack may deal at most 7% (after staling) |
| Knockback limit | must not cause tumble: below 80 knockback |
| Full reset vs half-reset | attacks giving 13-30 frames of hitstun cause a "half-reset": the victim is put into the knocked-down state and then forced to stand, and during the knocked-down part they can still input a getup option (bufferable with the C-stick) before the forced stand. Attacks with 12 or fewer frames of hitstun give the plain reset |
| Reset hop | the victim does a small bounce and is airborne during it; the attacker has 12 frames to hit again for another reset |
| After the forced getup starts | the victim is vulnerable for a further 30 frames |
| Airborne exit | if the victim is still in the air when the reset bounce ends, they go into normal fall with all aerial actions instead of the forced getup |
| SDI counterplay | the victim can SDI the reset hit upward (a grounded victim hit during a reset counts as airborne, so upward SDI is allowed even on downward or horizontal hits) to be in the air when the bounce ends |

Using hitstun = floor(0.4 x KB) from [hitstun-knockback](hitstun-knockback.md): 12 frames of
hitstun corresponds to knockback below 32.5, and 30 frames to knockback below 77.5 (derived).

Related timings from Magus420's getup data [web:smashboards.com]:

| State | Frames |
|-|-|
| Missed tech bounce | 26, no intangibility |
| Neutral getup (what the reset forces) | 30 total; intangible on frames 1-23 for most characters when chosen normally |

Whether the forced getup after a reset keeps the normal getup intangibility is not stated in
the sources read. The wiki's "vulnerable for an additional 30 frames" implies it does not.
Treat as: the victim can be hit throughout the forced stand [wiki:Lock].

Uncertainty on the damage limit: the wiki says "a maximum of 7%". Community descriptions
often phrase the rule as "less than 7%". Magus420's write-up (referenced from the Library's
"How Jab Resets Work, and How to Smash DI Them" card) is the primary source and was not
readable here. A drill generator should test the exact boundary in engine.

## Why it matters

- It turns a missed tech into the attacker's best punish, at any percent where a weak move
  exists: this is why missing techs is so costly.
- It makes "no tech" a bad defensive mixup against players who watch for it, and it is the
  correct punish on platforms when an opponent misses a tech after a launcher.
- Falco's laser and other weak projectiles can reset from a distance.
- The wiki notes resets are limited in Melee: few knockdowns are untechable, and the victim
  has counterplay (teching in the first place, SDI up, getup options during a half-reset)
  [wiki:Lock].

## Common errors

- Using a move that is too strong (over the damage limit or tumble knockback): the victim
  is launched normally and can tech or act.
- Hitting too late: the opponent has already started a getup option with intangibility.
- Reset succeeds but the punish is early (hits nothing useful) or late (victim is
  actionable again).
- Reset near an edge or with a move that pops the victim off the platform: they exit in
  the air and act.
- Failing to notice the opponent teched; the jab whiffs into an intangible tech.

## How to detect it in a training mode

- Precondition: victim in `DownBoundU/D` or `DownWaitU/D` [decomp].
- Reset: victim enters `DownDamageU/D` (hit while down) and then `DownStandU/D` without a
  getup input from the victim. A launch instead shows `DamageFly*`.
- Success for the full sequence: a second, strong hit connects during `DownStand*` (or
  within the 30-frame window) before the victim is actionable.
- Victim-side drill: displacement during hitlag (SDI up) and whether the victim exited via
  `Fall` instead of `DownStand*`.

## Drill seeds

### Jab reset punish

- **id:** `jab-reset-missed-tech-punish`
- **Goal:** Reset a missed tech and land the strongest punish.
- **Player:** any
- **CPU:** any
- **Setup:** CPU launched so it lands near the player and misses the tech.
- **CPU behaviour:** No tech; after landing waits a random time (within the lying duration) before choosing a getup.
- **Success:** Weak hit causes the forced stand, then a smash attack or grab connects before the CPU can act.
- **Fail:** CPU launched by a too-strong move, CPU gets up freely, or the punish misses.
- **Variations:** CPU techs 50% of the time (player must react: tech chase or reset); on platforms; CPU SDIs up.
- **Data needed:** Damage and knockback of the player's weak moves at the CPU's percent, getup timings.

### Reset or chase decision

- **id:** `jab-reset-or-tech-chase`
- **Goal:** React to tech versus missed tech.
- **Player:** [Sheik](../characters/sheik.md), [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Marth](../characters/marth.md), [Captain Falcon](../characters/captain-falcon.md)
- **CPU:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Captain Falcon](../characters/captain-falcon.md)
- **Setup:** CPU thrown or hit into a knockdown at mid percent.
- **CPU behaviour:** Random: tech in place, tech roll either way, or miss.
- **Success:** Correct punish for the option: regrab/hit after a tech, jab reset into punish after a miss.
- **Fail:** CPU becomes actionable.
- **Variations:** Laser reset from range (Falco).
- **Data needed:** [teching](teching.md) tables, reset rules above.

### Escape the reset

- **id:** `jab-reset-sdi-escape`
- **Goal:** As the victim, SDI the reset hit upward to avoid the forced getup, or choose a getup first.
- **Player:** any
- **CPU:** [Fox](../characters/fox.md), [Sheik](../characters/sheik.md), [Falco](../characters/falco.md)
- **Setup:** Player lying after a missed tech.
- **CPU behaviour:** Jabs after a random delay, then charges a smash.
- **Success:** Player avoids the smash (got up or rolled before the jab, or SDI'd into the air and acted).
- **Fail:** Hit by the smash.
- **Variations:** Delay range.
- **Data needed:** Jab hitlag (floor(d/3 + 3)) for the SDI window.

## Sources

- SSBWiki: Lock (Melee section; "Jab reset" redirects there) (https://www.ssbwiki.com/Lock).
- Magus420's techs/getups data (Smashboards, Wayback Machine copy), tagged
  `[web:smashboards.com]`.
- Melee Library: "How Jab Resets Work, and How to Smash DI Them" (Remix, video explaining
  Magus's write-up): title/description only.
- `[decomp]`: state names from this repository.
