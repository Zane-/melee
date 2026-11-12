---
schema: melee-technique/v1
id: amsah-tech
name: Amsah tech
aliases: [Over tech, ASDI down tech, survival tech, DI down tech, slideoff DI]
category: defense
difficulty: 4
related: [teching, asdi, di, sdi, crouch-cancel, tech-chase, hitstun-knockback]
characters: all
summary: DI down plus ASDI down on a low-angle kill move, with a tech input buffered before the hit, makes the character hit the floor at once and tech roll instead of flying off stage.
---

# Amsah tech

## What it is

A way to survive strong, low-angle hits at percents where normal survival [DI](di.md) no
longer works. The victim sends themselves into the floor on the first frame after hitlag
and techs, which cancels the knockback entirely. Named after the Dutch player Amsah; also
called an Over tech after Overtriforce [wiki:Tech].

It combines three mechanics:

1. **DI down (and sideways):** bends a low launch angle further toward the ground.
2. **[ASDI](asdi.md) down:** on the first frame after hitlag, moves the character 3 units
   down into the floor. ASDI, unlike SDI, is allowed to cause air-to-ground contact
   [wiki:Smash_directional_influence].
3. **[Tech](teching.md):** a digital L/R press made before the hit, so the tech window is
   open at the moment of floor contact.

The wiki's "ASDI down tech" is the same idea with the stick down or neutral, giving a tech
in place; it is used against moves that knock down at low percent, such as
[Fox](../characters/fox.md)'s usmash [wiki:Tech].

## Inputs

As described by the wiki [wiki:Tech]:

1. Before the hit connects, press L or R (digital). Pressing during hitlag fails except on
   its last frame (rules in [teching](teching.md)).
2. Hold the control stick down and toward or away from the attacker (diagonally down).
   Down-and-away keeps the trajectory closest to the ground and survives longest; the
   horizontal part also selects the tech roll direction.
3. Hold the C-stick down (ASDI down; the C-stick overrides the control stick for ASDI).
4. The character hits the floor on the first frame after hitlag and tech rolls
   (`PassiveStandF`/`PassiveStandB`), or techs in place if the stick was neutral or straight
   down.

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Tech window | L/R within 20 frames before floor contact; 40-frame lockout | [wiki:Tech] |
| Hitlag to wait through | floor(damage/3 + 3) frames, counted inside the 20-frame window | [wiki:Hitlag] |
| ASDI distance | 3 units, applied on the first frame after hitlag | [wiki:Smash_directional_influence] |
| DI | up to about 18 degrees of angle change | [wiki:Directional_influence] |
| Tech roll | 40 frames, intangible 1-20, vulnerable 21-40 | [web:smashboards.com] |
| Tech in place | 26 frames, intangible 1-20 (Pichu, Pikachu 1-24) | [web:smashboards.com] |
| Upper limit | works as long as DI + ASDI can bring the character into the floor on that frame: a grounded victim, a launch angle near horizontal, and a launch speed whose first-frame rise is less than what ASDI and the bent angle remove. No published percent limits were found; test per move | derived from the mechanics above |

Timing constraint: because hitlag counts against the tech window, the press must come
between 20 frames before the end of hitlag and the frame before hitlag starts. For a 20%
hit (9 frames of hitlag) that leaves about 11 frames before the hit in which to press.

Typical moves it is used against (low launch angles), from the wiki and general practice:
[Falco](../characters/falco.md) dsmash [wiki:Tech]; also [Fox](../characters/fox.md) dsmash,
[Marth](../characters/marth.md) fsmash and dtilt, [Sheik](../characters/sheik.md) dsmash and
ftilt at certain percents, [Peach](../characters/peach.md) dsmash (general knowledge, no
numbers).

## Why it matters

- It lets a character survive at percents far beyond what DI allows, because the tech
  removes the knockback instead of redirecting it [wiki:Tech].
- The price: the tech roll's ending is punishable by a prepared opponent, and DI down on a
  failed attempt (no floor contact, or missed tech) sends the character low and dead. The
  wiki describes it as a situational mixup, used especially against
  [Marth](../characters/marth.md), whose strong finishers have long ending lag and cannot
  easily punish the tech [wiki:Tech].
- The low-percent "ASDI down tech" variant defeats knockdown set-ups and tech chases
  (see the percent table in [asdi](asdi.md)).
- On platforms, the related "slide-off DI" uses ASDI down to land and slide off the edge to
  escape combos [wiki:Smash_directional_influence].

## Common errors

- L/R pressed during hitlag or not at all: the character hits the floor and bounces
  (missed tech) at the attacker's feet, or flies off low.
- L/R pressed too early (hitlag pushes contact beyond 20 frames) or twice (lockout).
- No C-stick down and control stick not low enough: no floor contact; the character is
  launched with DI down, the worst trajectory.
- Attempting it against a move that sends too vertically (never touches the floor) or when
  airborne above the floor by more than the ASDI distance.
- Always rolling the same way, so the attacker waits and punishes the tech roll.
- Using it at low percent against a move that could simply be [crouch cancelled](crouch-cancel.md)
  or ASDI'd without a tech.

## How to detect it in a training mode

- Pattern: victim grounded when hit -> hitlag -> on the first frame after hitlag the state
  is `PassiveStandF`, `PassiveStandB` or `Passive` [decomp], without an intermediate
  `DamageFly*` flight.
- Inputs to log: frame of the L/R press relative to the first hitlag frame; control stick
  and C-stick positions on the last hitlag frame.
- Failure classes: `DownBound*` on the first post-hitlag frame (floor reached, no tech);
  `DamageFly*` continuing (no floor contact); KO.
- Punish-side drill: attacker hits the victim during frames 21-40 of the tech roll.

## Drill seeds

### Amsah tech a kill move

- **id:** `amsah-tech-survive-dsmash`
- **Goal:** Survive a low-angle finisher at kill percent with an Amsah tech.
- **Player:** any
- **CPU:** [Falco](../characters/falco.md) (dsmash), [Fox](../characters/fox.md) (dsmash), [Marth](../characters/marth.md) (fsmash), [Sheik](../characters/sheik.md) (dsmash)
- **Setup:** Player standing near the edge at 100-150%; CPU adjacent.
- **CPU behaviour:** Uses the move after a visible wind-up with a small random delay.
- **Success:** Player enters a `Passive*` state on the first frame after hitlag and is not hit again for 60 frames.
- **Fail:** KO, missed tech, or punished after the tech.
- **Variations:** CPU waits and punishes the tech roll (player must vary direction); percent sweep to find where it stops working.
- **Data needed:** Move angle, damage and knockback; tech window rules.

### ASDI down tech at low percent

- **id:** `amsah-tech-asdi-down-tech-usmash`
- **Goal:** Tech in place on a low-percent knockdown move instead of being comboed.
- **Player:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Captain Falcon](../characters/captain-falcon.md), [Marth](../characters/marth.md)
- **CPU:** [Fox](../characters/fox.md) (usmash), [Sheik](../characters/sheik.md) (usmash, dash attack)
- **Setup:** Player grounded at a percent just above the knockdown threshold for the move.
- **CPU behaviour:** Lands the move, then attempts the standard follow-up.
- **Success:** `Passive` on the first post-hitlag frame and the follow-up misses.
- **Fail:** Launched and hit by the follow-up.
- **Variations:** Thresholds from [asdi](asdi.md); require a counterattack after the tech.
- **Data needed:** Knockdown thresholds, follow-up timing.

### Punish the Amsah tech

- **id:** `amsah-tech-punish-roll`
- **Goal:** As the attacker, cover the tech roll after a finisher is Amsah teched.
- **Player:** [Marth](../characters/marth.md), [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Sheik](../characters/sheik.md)
- **CPU:** any
- **Setup:** CPU at high percent in front of the player.
- **CPU behaviour:** Amsah techs the player's finisher with a random roll direction.
- **Success:** Player hits the CPU before it is actionable.
- **Fail:** CPU escapes.
- **Variations:** Use a faster, lower-lag finisher so the punish is possible.
- **Data needed:** Player move lag, tech roll distances ([teching](teching.md)).

## Sources

- SSBWiki: Tech (Amsah tech and ASDI down tech paragraphs; "Amsah tech" redirects there),
  Smash directional influence, Directional influence, Hitlag
  (https://www.ssbwiki.com/Tech#Rolling_tech).
- Magus420's techs data (Smashboards, Wayback Machine copy), tagged `[web:smashboards.com]`.
- Melee Library: Kadano's video "Teching and Advanced DI" covers the Amsah tech; not
  viewable. Doraki's DI guide for the ASDI-into-floor tech mechanism.
- `[decomp]`: state names from this repository.
