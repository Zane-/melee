---
schema: melee-technique/v1
id: sdi
name: Smash DI (SDI)
aliases: [SDI, smash directional influence, quarter-circle DI, QCDI, multiple SDI, wank DI, double stick DI, DSDI, shield SDI]
category: defense
difficulty: 4
related: [asdi, di, teching, wall-tech, hitstun-knockback, shield, jab-reset, amsah-tech]
characters: all
summary: Each new smash input on the control stick during hitlag shifts the victim 6 units in that direction, used to escape multi-hits and combos or to reach a wall or ceiling to tech.
---

# Smash DI (SDI)

## What it is

During hitlag (the freeze frames when a hit connects) the victim can move their character's
position by smashing the control stick. Every frame on which a **new** smash input in a
direction is registered moves the character a fixed distance that way. It changes position
before launch, not the launch angle; that is [DI](di.md), a separate mechanic read at the end
of hitlag [wiki:Smash_directional_influence].

## Inputs

- During the victim's hitlag, smash the control stick (from neutral to the rim) in the wanted
  direction. One input = one shift.
- **Multiple SDI:** return to neutral and smash again, or keep the stick on the rim and move
  it so a new horizontal or vertical component registers. Moving from a cardinal direction to
  an adjacent diagonal creates a new input; moving from a diagonal to the adjacent cardinal
  does not [wiki:Smash_directional_influence].
- **Quarter-circle DI:** rock the stick quickly between two neighbouring cardinals through
  the diagonal (e.g. up, up-right, right, up-right, up...) to get an input on most frames
  [wiki:Smash_directional_influence].
- **Double stick DI (DSDI):** SDI with the control stick plus a held C-stick direction for
  [ASDI](asdi.md) on the frame after hitlag, giving one extra half-shift in a chosen
  direction (used for wall techs and to escape upward chains) [lib:How to Double Stick DI Tech]
  (card title only; technique as described in Doraki's guide).

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Distance per SDI input | 6 units | [wiki:Smash_directional_influence] |
| Distance of ASDI | 3 units | [wiki:Smash_directional_influence] |
| Inputs possible | at most one per hitlag frame | [wiki:Smash_directional_influence] |
| Hitlag available | floor(d/3 + 3), x0.666667 if crouching, x1.5 if electric (victim), cap 20 | [wiki:Hitlag] |
| Minimum hitlag for SDI to be possible | 2 frames | [wiki:Smash_directional_influence] |
| Throws | no hitlag on release, so no SDI (hits inside a throw animation can be SDI'd; Jigglypuff fthrow is a known exception with hitlag) | [wiki:Hitlag] [lib:A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling] |
| Phantom hits | no knockback, but SDI and ASDI still apply | [lib:A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling] |
| Shield SDI | horizontal only, 0.66 of a normal input per input | [wiki:Smash_directional_influence] |

**Forbidden SDI** [wiki:Smash_directional_influence]
[lib:A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling]:

- A grounded victim hit by a move that does not launch upward (e.g. [Fox](../characters/fox.md)
  down B (shine), Fox dair) cannot SDI up off the ground.
- An airborne victim cannot SDI down into the ground. (ASDI can; see [asdi](asdi.md).)
- SDI **can** move the victim into a wall or ceiling, and a tech can come out during hitlag
  when that happens (see [wall-tech](wall-tech.md)).

The Melee Library points to Achilles' post "SDI Formula and How It Is Coded" for the exact
input conditions (stick thresholds, frame counters); it was not readable here, so the
dead-zone and "new input" thresholds are Unknown in this file.

## Why it matters

- **Escaping multi-hit moves** before the final hit: [Fox](../characters/fox.md) and
  [Jigglypuff](../characters/jigglypuff.md) dair (drill), [Peach](../characters/peach.md)
  dsmash, [Samus](../characters/samus.md) usmash, rapid jabs, [Mario](../characters/mario.md)
  /[Dr. Mario](../characters/dr-mario.md) up B and down B. Stationary multi-hits with weak
  linking hits are considered ineffective because of SDI [wiki:Smash_directional_influence].
- **Escaping set-ups:** SDI on the first hit(s) of [Fox](../characters/fox.md) uthrow uair
  (the Library lists two guides on exactly this), on [Falco](../characters/falco.md) shine
  and dair in pillars, on [Sheik](../characters/sheik.md) fair chains, on
  [jab resets](jab-reset.md).
- **Positioning for a tech:** SDI into the stage wall or under-lip to
  [wall tech](wall-tech.md) a hit near the ledge; SDI up into a ceiling.
- **Survival:** a few units toward the stage or away from a blast zone at the moment of a
  killing hit.
- More damage means more hitlag and so more SDI inputs; crouch cancelling reduces the
  window.

## Common errors

- Holding the stick instead of smashing it: only ASDI happens (3 units once).
- Inputs outside hitlag: too early (before the hit) registers nothing; too late becomes
  normal DI or drift.
- Stick returning toward centre on the last hitlag frame, which ruins the intended [DI](di.md)
  angle. SDI and DI use the same stick, so the last position must be the DI direction.
- SDI into the attacker's later hitboxes (e.g. into the centre of a multi-hit).
- Trying to SDI up while grounded against a non-lifting hit (forbidden, nothing happens).

## How to detect it in a training mode

- While the victim's hitlag counter is positive, record the control stick each frame.
  Count frames on which a new smash input registered; the fighter's position changes by
  about 6 units on those frames while both fighters are otherwise frozen (the simplest
  observable: victim position delta during hitlag).
- Total SDI displacement = position at the end of hitlag minus position at the start.
- Escape success for a multi-hit: the next hit of the move does not connect (no new hitlag
  on the victim within the move's remaining active frames).
- Wall-tech by SDI: `PassiveWall` begins during hitlag.

## Drill seeds

### SDI out of a multi-hit

- **id:** `sdi-escape-multihit`
- **Goal:** Escape a multi-hit move before the last hit.
- **Player:** any
- **CPU:** [Fox](../characters/fox.md) (dair), [Peach](../characters/peach.md) (dsmash), [Samus](../characters/samus.md) (usmash), [Mario](../characters/mario.md) (down B)
- **Setup:** Player standing, CPU adjacent.
- **CPU behaviour:** Uses the multi-hit move on the player.
- **Success:** Player takes fewer than N hits and is out of hitstun before the CPU is actionable; bonus if the player then punishes.
- **Fail:** All hits connect.
- **Variations:** Prescribed direction (up and away, behind the attacker); on shield (shield SDI away from Peach dsmash).
- **Data needed:** Hit count, damage per hit (hitlag per hit), hitbox extents.

### SDI Fox up throw up air

- **id:** `sdi-fox-uthrow-uair`
- **Goal:** SDI the first hit of uair so the second (strong) hit misses.
- **Player:** any (most relevant for floaties and mid-weights at kill percent)
- **CPU:** [Fox](../characters/fox.md)
- **Setup:** Player grabbed by Fox at 80-120% on a stage with a low ceiling (Yoshi's Story).
- **CPU behaviour:** Uthrow, jump, uair timed to the player's DI.
- **Success:** Second hit of uair does not connect, or the player survives.
- **Fail:** Player is KO'd.
- **Variations:** DI left/right on the throw first, then SDI; different percents.
- **Data needed:** Fox uthrow release frame, uair hit frames (first hit has set knockback [wiki:Knockback]), hitlag of the first hit.

### Input rate trainer

- **id:** `sdi-input-count`
- **Goal:** Increase the number of SDI inputs per hit.
- **Player:** any
- **CPU:** [Samus](../characters/samus.md) (charge shot), any strong single hit
- **Setup:** Player standing; CPU hits with a high-damage move (long hitlag).
- **CPU behaviour:** One hit at a fixed time.
- **Success:** Displacement during hitlag of at least K x 6 units in the prompted direction.
- **Fail:** Fewer inputs, or the last-frame stick position is not the prompted DI direction.
- **Variations:** Quarter-circle vs straight taps; combine with a required survival DI.
- **Data needed:** Damage of the hit (hitlag length).

## Sources

- SSBWiki: Smash directional influence, Hitlag, Knockback
  (https://www.ssbwiki.com/Smash_directional_influence).
- Melee Library: "A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling"
  (Doraki, Wayback Machine copy). Listed but not readable: "SDI Formula and How It Is Coded"
  (Achilles), "How to SDI Fox's U-throw U-air and not die" (KirbyKaze), "An Analysis Of
  Human Smash DI" (Remix, video), "How to Double Stick DI Tech" (Witchking_of_Angmar).
