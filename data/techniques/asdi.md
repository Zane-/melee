---
schema: melee-technique/v1
id: asdi
name: Automatic smash DI (ASDI)
aliases: [ASDI, ASDI down, floorhugging, automatic smash directional influence, C-stick DI]
category: defense
difficulty: 2
related: [sdi, di, crouch-cancel, teching, amsah-tech, hitstun-knockback, jab-reset]
characters: all
summary: On the first frame after hitlag the character is shifted 3 units in the direction held on the C-stick (or control stick); holding down puts a grounded character back on the floor, cancelling non-tumble hitstun.
---

# Automatic smash DI (ASDI)

## What it is

A small automatic position shift applied once, on the first frame after hitlag ends, in the
direction the stick is **held** (no tap needed). It is the weak, automatic sibling of
[SDI](sdi.md). The C-stick has priority over the control stick, so a player can hold the
control stick one way for [DI](di.md) and the C-stick another way for ASDI
[wiki:Smash_directional_influence] [lib:A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling].

The important special case is **ASDI down**: unlike SDI, ASDI is allowed to move an airborne
character into the ground. A grounded character hit by a move that lifts them slightly is
pushed back onto the floor on that frame. If the hit did not cause tumble, the character
lands at once: the landing lasts as long as the hitstun but can be left for an attack, a grab
or a shine after the normal landing lag (4 frames for most characters: `ftCo_Landing_IASA`;
seen on the native build, 2026-11-13). If it did cause tumble but the first frame's rise is
less than the ASDI distance, the character hits the floor at once and can [tech](teching.md)
there, or is knocked down at the attacker's feet; a bigger rise launches them as usual
[wiki:Smash_directional_influence] [wiki:Hitstun].

## Inputs

- Hold the C-stick (or, if the C-stick is neutral, the control stick) in the wanted
  direction on the last frame of hitlag. Holding earlier is fine; only that frame is read.
- ASDI down: hold down. From a standing position this is not a crouch cancel (no 2/3
  knockback factor) unless the character was actually in a crouch state when hit; see
  [crouch-cancel](crouch-cancel.md).
- ASDI down tech: hold the control stick down or neutral, C-stick down, and press L/R
  **before** the hit (during hitlag is too late, see [teching](teching.md))
  [wiki:Tech].

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| ASDI distance | 3 units (half of an SDI input, which is 6) | [wiki:Smash_directional_influence] |
| When applied | first frame after hitlag, from the stick position on the last hitlag frame | [wiki:Directional_influence] [lib:A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling] |
| Stick priority | C-stick overrides control stick | [wiki:Smash_directional_influence] |
| Air-to-ground allowed? | Yes for ASDI (not for SDI) | [wiki:Smash_directional_influence] |
| Result on non-tumble hit | landing animation (4 frames for most) replaces hitstun, if launch speed at touchdown is above 0.5 | [wiki:Hitstun] |
| Result on tumble hit | immediate floor contact: tech or missed-tech bounce | [lib:A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling] |
| Shield ASDI | half of shield SDI, horizontal only, applied on the first frame of shieldstun | [wiki:Smash_directional_influence] |
| Grounded victim of a downward, non-techable hit | stays stunned on the ground whatever is held ("forbidden" case) | [lib:A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling] |

ASDI down has three bands as the percent rises (`ftCo_8008DCE0`, `ftCo_Damage.c`; research
of 2026-11-13):

1. knockback under 80: the character lands at once and can act after the normal landing lag;
2. knockback 80 or more, but a first-frame rise (`0.03 * KB * sin(angle) - gravity`) of 3
   units or less: the floor is touched in tumble, a tech or a knockdown at the attacker's
   feet, not a launch;
3. a bigger rise: launched as usual.

The percents below (DruggedFox's "breaks ASDI down") are where band 3 starts, the launch, not
band 2. Measured limits for the course's actors, where the hold still lets Fox punish, are in
`tools/melee_course/drills/defense_asdi.py` (`tests/course/asdi.py`).

### Sheik's moves: percent at which they break ASDI down

Percent of the victim **before** the hit, fresh moves, measured by DruggedFox for
[Sheik](../characters/sheik.md) attacking [lib:ASDI Down]:

| Sheik move | vs Fox | vs Falco | vs Captain Falcon |
|-|-|-|-|
| Usmash | 31 | 31 | 35 |
| Dash attack | 51 | 50 | 57 |
| Uair | 44 | 43 | 49 |
| Dair | 57 | 57 | 64 |
| Ftilt | 69 | 68 | 76 |
| Utilt | 73 | 74 | 83 |
| Dtilt (tip) | 84 | 84 | 93 |
| Dtilt (not tip) | 95 | 94 | 105 |
| Dsmash | 110 | 110 | 124 |

Against [Marth](../characters/marth.md) the same source lists the percent at which Sheik's
aerials knock him down: uair 23, dair 28 [lib:ASDI Down]. Stale moves shift these up by the
lost damage; a slightly charged smash shifts them down [lib:ASDI Down].

## Why it matters

- **Neutral:** at low percent a standing player can hold down, take a weak hit (a spaced
  aerial, a jab, a tilt) with only landing lag, and punish. It needs no crouch, so it works
  out of a dash dance or while walking.
- **Tech chase defence:** a character lying on the ground after a missed tech who holds
  down can be hit by a low-knockback move and immediately tech it, then punish. Example
  given by DruggedFox: Falco below 50% ASDI-down techs Sheik's dash attack and punishes
  [lib:ASDI Down]. If the victim's tech is locked out (they pressed L/R recently), ASDI down
  just grounds them.
- It is the mechanism behind [crouch cancel](crouch-cancel.md), [Amsah tech](amsah-tech.md)
  and slide-off DI on platforms.
- Sakurai-angle hits at certain percents cannot be crouch cancelled but can be ASDI'd down
  [wiki:Smash_directional_influence].
- Wall and ledge techs: ASDI toward the stage makes a character touch the wall at mid
  percents so the tech happens (see [wall-tech](wall-tech.md)).

## Common errors

- Holding down above the threshold percent: knocked down at the opponent's feet with no
  tech input ready.
- Holding down against a grab, a spike or a 0-degree hit.
- Holding down with the control stick against a strong horizontal hit: it also acts as DI
  down, which kills earlier. Use the C-stick for ASDI and the control stick for DI.
- Letting the C-stick return to neutral before hitlag ends.

## How to detect it in a training mode

- Read both sticks on the last frame of the victim's hitlag (hitlag counter about to reach
  0). C-stick outside its dead zone decides; else the control stick.
- ASDI down success on a non-tumble hit: victim transitions `Damage*` to `Landing` on the
  first post-hitlag frame while `ground_or_air` returns to grounded [decomp].
- ASDI down tech: victim transitions `DamageFly*` to `Passive`/`PassiveStandF`/`PassiveStandB`
  on the first post-hitlag frame.
- Failure: `DamageFly*` continues (no ASDI, popped up) or `DownBound*` (floor reached but
  no tech).

## Drill seeds

### ASDI down and punish

- **id:** `asdi-down-punish-low-percent`
- **Goal:** Absorb a weak hit by holding down and punish it.
- **Player:** any
- **CPU:** [Marth](../characters/marth.md), [Sheik](../characters/sheik.md), [Fox](../characters/fox.md)
- **Setup:** Player standing at 0-20%, CPU at mid range.
- **CPU behaviour:** Hits with a weak move (Marth late fair, Sheik ftilt, Fox nair weak hit), then shields when actionable.
- **Success:** Player lands (`Landing`) on the first frame after hitlag and hits/grabs the CPU before it shields.
- **Fail:** Player popped up, or punish too late.
- **Variations:** Percent ramps toward the break point; CPU sometimes grabs.
- **Data needed:** Knockback of the CPU move vs the player's weight, CPU lag.

### ASDI down tech from the floor

- **id:** `asdi-down-tech-vs-techchase`
- **Goal:** Tech a weak tech-chase hit while lying down.
- **Player:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Captain Falcon](../characters/captain-falcon.md)
- **CPU:** [Sheik](../characters/sheik.md)
- **Setup:** Player in missed-tech state (`DownWait*`) at a percent below the table value for the CPU's move; CPU standing nearby.
- **CPU behaviour:** Dash attack or dtilt on the lying player after a random delay.
- **Success:** Player enters a `Passive*` state on the hit and then hits the CPU.
- **Fail:** Player launched, or missed the tech.
- **Variations:** Percent above the threshold (player must get up or roll instead); CPU grabs instead.
- **Data needed:** The percent table above; tech window rules.

### Split sticks: DI with control stick, ASDI with C-stick

- **id:** `asdi-cstick-split`
- **Goal:** Hold survival DI on the control stick and ASDI toward the stage on the C-stick.
- **Player:** any
- **CPU:** [Marth](../characters/marth.md), [Fox](../characters/fox.md)
- **Setup:** Player at 80-120% near the ledge.
- **CPU behaviour:** Fsmash/usmash at a fixed time.
- **Success:** On the last hitlag frame the control stick is within the survival DI zone and the C-stick is held toward the stage (or down, per drill variant).
- **Fail:** Either stick wrong.
- **Variations:** Require a wall tech when hit off the ledge.
- **Data needed:** Launch angle of the CPU move.

## Sources

- SSBWiki: Smash directional influence (ASDI section), Directional influence, Hitstun, Tech
  (https://www.ssbwiki.com/Smash_directional_influence).
- Melee Library: "ASDI Down" by DruggedFox
  (https://portraitinsmash.blogspot.com/2015/05/asdi-down.html); "A Guide to DI, Smash DI,
  C-stick DI, Teching, and Crouch Cancelling" by Doraki (Wayback Machine copy).
- `[decomp]`: state/field names from this repository.
