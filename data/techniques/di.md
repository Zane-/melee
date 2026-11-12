---
schema: melee-technique/v1
id: di
name: Directional influence (DI)
aliases: [DI, trajectory DI, TDI, survival DI, combo DI, DI mixup, launch shuffling]
category: defense
difficulty: 3
related: [sdi, asdi, hitstun-knockback, teching, amsah-tech, chain-grab, grab-and-throw, tech-chase]
characters: all
summary: The stick position on the last frame of hitlag rotates the launch angle by up to about 18 degrees; it decides whether a hit kills and whether a combo or chain grab continues.
---

# Directional influence (DI)

## What it is

When a character is launched, the game reads the control stick once, on the last frame of
hitlag, and rotates the launch angle toward the held direction. Speed is unchanged; only the
angle changes. It is a different mechanic from [SDI](sdi.md) (position shift during hitlag)
and [ASDI](asdi.md) (one shift after hitlag), which are read at about the same time
[wiki:Directional_influence].

Two uses:

- **Survival DI:** bend the trajectory toward a top corner of the screen so the path to the
  blast zone is longer.
- **Combo DI:** bend the trajectory so the attacker's follow-up does not reach, or so a
  chain grab ends.

## Inputs

- Hold the control stick in the wanted direction before hitlag ends. Only the last hitlag
  frame counts. No smash input is needed; a partial tilt gives a partial effect
  [wiki:Directional_influence].
- For throws there is no hitlag: the stick is read on the frame immediately before the
  release frame [web:smashboards.com] (Magus420's throws/techs/getups thread, see
  Sources).

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| When the stick is read | last frame of hitlag | [wiki:Directional_influence] |
| Maximum angle change | about 18 degrees | [wiki:Directional_influence] |
| Direction that gives the maximum | perpendicular to the launch angle | [wiki:Directional_influence] |
| Direction that gives none | parallel to the launch angle (toward or away along the trajectory) | [wiki:Directional_influence] |
| Partial tilt | proportionally weaker | [wiki:Directional_influence] |
| Launch angles within 17 degrees of straight up/down/left/right | can be DI'd less, because the stick's available angles are not evenly distributed and no exact perpendicular exists | [wiki:Directional_influence] |
| Grounded victim, hit that keeps them on the ground (weak Sakurai angle, weak meteor) | DI has no effect | [wiki:Directional_influence] |
| Throw DI read | the frame before release; releases faster than about frame 10-12 are very hard to DI on reaction | [web:smashboards.com] |
| Knockback stacking | DI applies to the merged vector | [wiki:Knockback] |

The exact formula (how the perpendicular stick component maps to degrees) is documented in
Sycorax's "The Specifics of Trajectory DI" in the Melee Library; it could not be fetched, so
this file gives only the limits above.

Rules of thumb that follow from "perpendicular is strongest":

| Hit sends you | Survival DI | Combo DI (to escape follow-ups) |
|-|-|-|
| Straight up (e.g. [Fox](../characters/fox.md) usmash, uair) | hold left or right (slightly down-and-sideways is also perpendicular; the goal is a diagonal path to the top corner) | left or right, away from where the attacker can reach |
| Horizontally (e.g. [Marth](../characters/marth.md) fsmash, [Sheik](../characters/sheik.md) fair) | up and toward the stage ("up and in") | away (down and away makes follow-ups hard but kills earlier) |
| Diagonally up and away (most Sakurai-angle kill moves) | up and in, perpendicular to the path | away |
| Down throws / up throws for chain grabs | n/a | fully away or behind, or mix; see [chain-grab](chain-grab.md) |

Reference values from the wiki's general knockback table (not Melee-specific testing): from
the centre of Final Destination at the Sakurai angle, the knockback needed to KO is about
186 with no DI, 172.5 "DI'd down" and 204.75 "DI'd away" [wiki:Knockback]. The labels are
the wiki's; treat the numbers as an illustration that DI moves the kill threshold by
roughly 10% of knockback either way.

## Why it matters

- It is the largest single factor in when stocks end. The same hit can kill 20-40% apart
  depending on DI (typical; exact numbers per move belong in the character files).
- The punish game is a DI guessing game: survival DI on a weak hit gives the attacker an
  easy follow-up, combo DI on a strong horizontal hit kills very early. Attackers
  deliberately use strong horizontal moves when they expect DI away
  ([Falco](../characters/falco.md) fsmash, [Marth](../characters/marth.md) fsmash)
  [wiki:Directional_influence].
- [Chain grabs](chain-grab.md) and [tech chases](tech-chase.md) are defined by which DI
  breaks them.
- A realistic CPU dummy must DI; a drill should state the DI it assumes.

## Common errors

- No DI (stick neutral or still doing the previous movement input).
- DI "away" on a horizontal kill move: the character flies flatter and dies early.
- DI "in" on a move that sends straight up: no perpendicular component if held straight
  up; hold sideways.
- Stick snapped to the SDI direction on the last hitlag frame, replacing the intended DI.
- For throws: reacting after the release frame. Throw DI must be held before the throw's
  release.
- Holding down with the control stick for [ASDI down](asdi.md) against a strong hit, which
  is also DI down.

## How to detect it in a training mode

- Sample the control stick on the victim's last hitlag frame (for throws: the frame before
  the release frame of `ThrowF/B/Hi/Lw` [decomp]).
- Compute the angle between the stick vector and the hitbox's base launch angle (from the
  frame data dump `angle`, with 361 resolved as in [hitstun-knockback](hitstun-knockback.md)
  and mirrored by the attacker's facing). Classify: within about 30 degrees of perpendicular
  toward the wanted side = good; parallel = none; perpendicular on the wrong side = bad.
- Alternatively compare the victim's actual initial velocity angle after hitlag with the
  base angle; the difference is the DI achieved (up to about 18 degrees).
- Outcome checks: survived / KO'd; follow-up connected or not.

## Drill seeds

### Survival DI flash cards

- **id:** `di-survival-reaction`
- **Goal:** Hold the correct survival DI for different kill moves.
- **Player:** any
- **CPU:** [Fox](../characters/fox.md) (usmash), [Marth](../characters/marth.md) (fsmash tip), [Falco](../characters/falco.md) (fsmash, dair), [Sheik](../characters/sheik.md) (fair), [Jigglypuff](../characters/jigglypuff.md) (bair), [Captain Falcon](../characters/captain-falcon.md) (knee)
- **Setup:** Player at a percent where the move kills without DI but not with good DI; position chosen per move.
- **CPU behaviour:** Randomly picks a kill move from its pool and lands it.
- **Success:** Player survives; stick on the last hitlag frame within the good zone.
- **Fail:** KO, or stick outside the zone (report the angle).
- **Variations:** Preceded by a combo hit so the player must switch from combo DI to survival DI.
- **Data needed:** Move angle, knockback data, blast zone positions, victim weight/fall speed.

### DI mixup defence

- **id:** `di-mixup-read`
- **Goal:** Learn to DI by what the attacker actually does, not pre-emptively.
- **Player:** any
- **CPU:** [Falco](../characters/falco.md), [Marth](../characters/marth.md)
- **Setup:** Player in hitstun from a combo starter at 60-90%.
- **CPU behaviour:** Follows with either a vertical combo move (needs DI away) or a horizontal kill move (needs DI up/in), chosen at random.
- **Success:** Survive the kill move and escape the next hit after the combo move.
- **Fail:** Dies to the horizontal move, or is comboed after survival DI on the weak move.
- **Variations:** Ratio of options; shorter reaction windows.
- **Data needed:** Both moves' angles and knockback.

### Throw DI

- **id:** `di-throw-escape`
- **Goal:** DI a combo throw so the standard follow-up misses.
- **Player:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Captain Falcon](../characters/captain-falcon.md), others
- **CPU:** [Marth](../characters/marth.md) (uthrow), [Sheik](../characters/sheik.md) (dthrow), [Fox](../characters/fox.md) (uthrow), [Jigglypuff](../characters/jigglypuff.md) (uthrow), [Peach](../characters/peach.md)
- **Setup:** Player grabbed at a percent inside the chain-grab/combo window.
- **CPU behaviour:** Throws after a random pummel count, then attempts the follow-up for no-DI.
- **Success:** Stick on the frame before release is in the escaping zone and the follow-up misses.
- **Fail:** Regrabbed or hit.
- **Variations:** CPU reacts to the DI (harder); mix of throws so the player must identify the throw.
- **Data needed:** Throw release frames and angles, weight-dependent throw speed (see [grab-and-throw](grab-and-throw.md)).

### CPU DI configuration (for other drills)

- **id:** `di-cpu-profiles`
- **Goal:** Not a player drill: a standard set of CPU DI behaviours other drills can refer to.
- **Player:** any
- **CPU:** any
- **Setup:** n/a
- **CPU behaviour:** `none`, `in`, `away`, `survival` (perpendicular toward the top corner farther from the blast zone), `combo` (away from the attacker), `random`, `slight` (half tilt).
- **Success:** n/a
- **Fail:** n/a
- **Variations:** Add SDI and ASDI profiles from [sdi](sdi.md) and [asdi](asdi.md).
- **Data needed:** Hit angle and attacker position at the time of the hit.

## Sources

- SSBWiki: Directional influence, Knockback (https://www.ssbwiki.com/Directional_influence).
- Melee Library: "A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling"
  (Doraki, Wayback Machine copy); Magus420's "Detailed Throws, Techs and Getups Frame Data"
  thread (http://smashboards.com/threads/detailed-throws-techs-and-getups-frame-data.206469/,
  Wayback Machine copy; it is cited by SSBWiki's Knockback page rather than carded in the
  Library). Not readable: "The Specifics of Trajectory DI" (Sycorax), "How to DI" (image),
  "Understanding DI Mixups" (Radar, video), "Angles in Melee" (ajp_anton).
- `[decomp]`: state names from this repository.
