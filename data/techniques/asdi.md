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
band 2. Where band 1 ends, the limit a player who wants to act out of the landing plays by, is
measured for the top 11's tilts, jabs and dash attacks against every character in the next
section; the ASDI drill (`data/drills/universal-asdi.json`) draws a try's damage under it.

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

### Where ASDI down stops: measured

<!-- asdi-limits: python tools/melee_drills/cc_limits.py --asdi --table -->
Measured in this build (`python tools/melee_drills/cc_limits.py --asdi`, every character in
`data/actor/asdi_down.json`): the most damage, before the hit, at which a standing
character that holds the C-stick down through the hit's freeze is on the floor when the
freeze ends and stays on its feet: band 1 above. One percent more and the hit tumbles it
or lifts it. Listed for the distances (units between the two) the move hit all 26
characters from. "260+": still held at 260%, where the search stops (the weakest jabs);
"not at 0%": lifted or knocked down even at 0% (the Ice Climbers: the partner's hit
comes after the first). "Lifts at 0%": how many of the 26 the hit lifts off the floor at 0% when
they hold nothing; a hit that lifts none has nothing to ASDI down there (a Sakurai-angle
tilt at low damage).

| Opponent | Move | From | Fox holds to | Pichu | Bowser | Freeze (frames) | Lifts at 0% | By distance |
|-|-|-|-|-|-|-|-|-|
| Fox | down tilt | 10, 13, 16 | 17% | 13% | 23% | 6 | all | the same from each |
| Fox | forward tilt | 10, 13, 16 | 61% | 53% | 78% | 6 | none | the same from each |
| Fox | jab | 10, 13, 16 | 125% | 110% | 156% | 4 | all | the same from each |
| Fox | dash attack | 13, 16, 24, 30 | 37% | 32% | 48% | 5 | all | the same from each |
| Marth | down tilt | 10, 13, 16, 24 | 84% | 73% | 106% | 5 or 6 | all | up to 100 more from another |
| Marth | forward tilt | 10, 13, 16, 24 | 51% | 44% | 66% | 6 or 7 | all | up to 57 more from another |
| Marth | jab | 10, 13, 16, 24 | 208% | 184% | 259% | 4 or 5 | 0 to 8 of 26 | up to 128 more from another |
| Marth | dash attack | 30 | 55% | 48% | not at 0% | 6 | all | the same from each |
| Jigglypuff | down tilt | 10, 13, 16 | 110% | 96% | 138% | 6 | all | the same from each |
| Jigglypuff | forward tilt | 10, 13, 16 | 46% | 39% | 59% | 6 | all | the same from each |
| Jigglypuff | jab | 10, 13, 16 | 260+ | 260+ | 260+ | 4 | none | the same from each |
| Jigglypuff | dash attack | 10, 13, 16, 24, 30 | 29% | 24% | 38% | 5 or 7 | 24 to 26 of 26 | up to 33 more from another |
| Falco | down tilt | 10, 13, 16 | 8% | 6% | 13% | 7 | all | the same from each |
| Falco | forward tilt | 10, 13, 16, 24 | 61% | 53% | 78% | 6 | none | the same from each |
| Falco | jab | 10, 13, 16 | 125% | 110% | 156% | 4 | all | the same from each |
| Falco | dash attack | 16, 24, 30 | 27% | 23% | 36% | 5 or 6 | all | up to 46 more from another |
| Sheik | down tilt | 10, 13, 16 | 39% | 34% | 51% | 5 | all | the same from each |
| Sheik | forward tilt | 10, 13, 16 | 23% | 20% | 30% | 5 | all | the same from each |
| Sheik | jab | 10, 13, 16 | 125% | 110% | 156% | 4 | all | the same from each |
| Sheik | dash attack | 24, 30 | 19% | 15% | 26% | 6 | all | the same from each |
| Captain Falcon | down tilt | 10, 13, 16, 24 | 37% | 31% | 49% | 7 | all | the same from each |
| Captain Falcon | forward tilt | 10, 13, 16 | 38% | 33% | 50% | 6 | all | the same from each |
| Captain Falcon | jab | 10, 13, 16 | 260+ | 260+ | 260+ | 3 | all | the same from each |
| Captain Falcon | dash attack | 10, 13, 16, 24, 30 | 38% | 32% | 49% | 5 or 6 | 20 to 26 of 26 | up to 137 more from another |
| Peach | down tilt | 10, 13, 16 | not at 0% | not at 0% | not at 0% | 7 | all | the same from each |
| Peach | forward tilt | 10, 13, 16 | 16% | 12% | 23% | 6 or 7 | all | up to 8 more from another |
| Peach | jab | 10, 13, 16 | 260+ | 260+ | 260+ | 4 | all | the same from each |
| Peach | dash attack | 16, 24, 30 | not at 0% | not at 0% | not at 0% | 6 or 7 | all | up to 25 more from another |
| Ice Climbers | down tilt | 10, 13, 16 | not at 0% | not at 0% | not at 0% | 4 | all | the same from each |
| Ice Climbers | forward tilt | 10, 13, 16 | not at 0% | not at 0% | not at 0% | 5 | all | up to 36 more from another |
| Ice Climbers | jab | 10, 13, 16 | not at 0% | not at 0% | not at 0% | 3 | all | up to 187 more from another |
| Ice Climbers | dash attack | 24, 30 | not at 0% | not at 0% | not at 0% | 11 | all | the same from each |
| Pikachu | down tilt | 10, 13, 16 | 62% | 54% | 79% | 5 | all | the same from each |
| Pikachu | forward tilt | 10, 13, 16 | 56% | 49% | 72% | 5 | all | the same from each |
| Pikachu | jab | 10, 13 | 260+ | 260+ | 260+ | 3 | none | the same from each |
| Pikachu | dash attack | 10, 13, 16, 24, 30 | 40% | 35% | 52% | 5 | all | the same from each |
| Yoshi | down tilt | 10, 13, 16 | not at 0% | not at 0% | not at 0% | 6 | all | the same from each |
| Yoshi | forward tilt | 10, 13, 16 | 16% | 13% | 23% | 7 | all | the same from each |
| Yoshi | jab | 10, 13, 16 | 260+ | 260+ | 260+ | 4 | none | the same from each |
| Yoshi | dash attack | 16, 24, 30 | 44% | 38% | 57% | 6 | all | the same from each |
| Samus | down tilt | 10, 13, 16 | not at 0% | not at 0% | not at 0% | 7 | all | the same from each |
| Samus | forward tilt | 10, 13, 16, 24 | 44% | 37% | 57% | 6 | all | the same from each |
| Samus | jab | 10, 13, 16 | 151% | 134% | 189% | 4 | none | the same from each |
| Samus | dash attack | 10, 13, 16, 24, 30 | 18% | 14% | 25% | 7 | all | the same from each |
<!-- /asdi-limits -->

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
