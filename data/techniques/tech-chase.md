---
schema: melee-technique/v1
id: tech-chase
name: Tech chase
aliases: [tech chasing, techchase, reaction tech chase, tech trap, regrab]
category: punish
difficulty: 4
related: [teching, jab-reset, chain-grab, grab-and-throw, dash-dance, di, asdi, wavedash]
characters: [sheik, captain-falcon, marth, fox, falco, ice-climbers, ganondorf, peach, dr-mario, mario, luigi]
summary: Knocking the opponent down and punishing whichever tech or getup option they choose, by reaction or by positioning to cover several options at once.
---

# Tech chase

## What it is

After a knockdown the defender has a small, known set of options: tech in place, tech roll
left, tech roll right, or miss the tech (then stand, roll, getup attack or wait). Every tech
ends with vulnerable frames (see [teching](teching.md)). A tech chase is the attacker
following the chosen option and hitting or re-grabbing during those frames. Repeating a
knockdown throw each time (for example [Sheik](../characters/sheik.md) dthrow,
[Captain Falcon](../characters/captain-falcon.md) dthrow or uthrow on fastfallers,
[Marth](../characters/marth.md) on platforms) creates a loop that can take a stock
[wiki:Tech-chase] [wiki:Tech].

Two styles:

- **Reaction:** stand where all options are reachable, watch the first frames of the tech
  animation, then move and punish.
- **Read / coverage:** commit before seeing the tech to an option that covers two or more
  choices (for example a move with a long active hitbox covering tech in place and one
  roll), or guess.

## Inputs

1. Start with a move that knocks down and leaves the attacker actionable early: typically a
   down throw or a weak launcher on a platform.
2. Position: usually stand at or just outside the spot where the opponent lands, facing
   them, often with a short [dash dance](dash-dance.md) to stay mobile.
3. Identify the option (animation or dust direction) and respond:
   - tech in place: grab or attack on the spot,
   - tech away / toward: dash and [jump-cancel](jump-cancel.md) grab, dash attack, or a
     long-range move,
   - missed tech: [jab reset](jab-reset.md) into a strong punish, or a charged smash, or
     a grab timed to the forced getup.
4. Repeat, or finish with a kill move when the percent allows.

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Tech in place | 26 frames, intangible 1-20 (Pichu/Pikachu 1-24): 6 punishable frames | [web:smashboards.com] |
| Tech roll | 40 frames, intangible 1-20: 20 punishable frames, but at a distance | [web:smashboards.com] |
| Missed tech bounce | 26 frames, no intangibility | [web:smashboards.com] |
| Neutral getup | 30 frames, intangible 1-23 for most | [web:smashboards.com] |
| Getup roll | 35 frames | [web:smashboards.com] |
| Getup attack | 49 frames | [web:smashboards.com] |
| Frame the roll direction becomes readable | 6-17 depending on character and direction (table in [teching](teching.md)) | [web:smashboards.com] |
| Standing grab | active frame 7 for most characters (Sheik 6) | [web:fightcore.gg] |

Reaction budget for the hardest case, tech in place: the grab must connect on frames 21-26
of the tech. With a frame 7 grab the grab input must happen on tech frames 15-20, so the
attacker has to recognise "in place" within roughly the first 14 frames, minus their own
reaction time. Rolls leave more time (the punish window is frames 21-40) but require
travelling the roll distance first.

Per-character facts that change the chase (all from the [teching](teching.md) table,
[web:smashboards.com]):

- Rolls with early readable movement (frame 6): Falco, Fox, Sheik backward rolls.
- Late readable movement (frame 16-17): Mewtwo both rolls, Ice Climbers backward.
- Longest rolls: Ganondorf forward (18.6), Captain Falcon forward, Luigi, Zelda (16.6).
- Shortest: Pichu (8.4), Mr. Game & Watch (9.6-9.8).

Defender counterplay that a realistic CPU should use:

- [DI](di.md) on the throw to land farther away or off the platform/stage.
- [ASDI down](asdi.md) plus tech on a weak tech-chase hit (thresholds in [asdi](asdi.md)).
- Deliberately not teching, then getup attack or roll, to break the attacker's rhythm.
- Teching toward the ledge or onto a platform edge changes the distances.

## Why it matters

Tech chasing is the main punish for characters without long juggle combos against a given
opponent, and it converts a single grab into large damage or a stock.
[Sheik](../characters/sheik.md)'s dthrow tech chase on the fastfallers and
[Captain Falcon](../characters/captain-falcon.md)'s grab game are central to those
matchups; [Marth](../characters/marth.md), [Fox](../characters/fox.md) and
[Falco](../characters/falco.md) tech chase on platforms after up throws and up airs/shines.
The Library's "TechChasing" (Little England) and "Platform Follow Ups" (Zero) cover the
same ground in video form.

## Common errors

- Moving before seeing the option (guessing) and going the wrong way.
- Grabbing too early: the grab hits intangibility and whiffs; the defender then punishes
  grab lag.
- Standing too close or too far so that one roll direction is unreachable in time.
- Dash grab instead of jump-cancel grab: slower and laggier (see
  [grab-and-throw](grab-and-throw.md)).
- Missing that the opponent did not tech, and being hit by a getup attack.
- Ignoring DI: the opponent lands farther than expected or off a platform.

## How to detect it in a training mode

- Knockdown event: defender enters `Passive`, `PassiveStandF`, `PassiveStandB` or
  `DownBound*` [decomp].
- Success: the attacker's grab or hit connects before the defender's first actionable frame
  (frame 27 of `Passive`, frame 41 of a tech roll, or the end of the getup state).
- Report: which option the defender chose, the frame of the tech animation on which the
  attacker's punish connected (or the frame the grab became active versus frames 21-26),
  and "early (hit intangibility)" / "late (defender acted)".
- Loop length: number of consecutive successful chases without the defender acting.
- CPU option picker: uniform or weighted random among {in place, roll toward attacker, roll
  away, no tech then {stand, roll in, roll away, getup attack}}; plus a DI choice on the
  throw.

## Drill seeds

### Reaction tech chase on flat ground

- **id:** `tech-chase-reaction-regrab`
- **Goal:** Regrab every tech option by reaction.
- **Player:** [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md), [Marth](../characters/marth.md)
- **CPU:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Captain Falcon](../characters/captain-falcon.md)
- **Setup:** Final Destination centre; CPU at 20-40%; the drill starts with the CPU already grabbed.
- **CPU behaviour:** Random DI on the throw (none, away, behind); random tech: in place, toward, away, miss then random getup.
- **Success:** Player grabs or hits the CPU before it is actionable, three times in a row.
- **Fail:** CPU becomes actionable or hits the player.
- **Variations:** Restrict to two options first; add ASDI-down tech against weak hits; raise the percent until the throw no longer knocks down; finish with a kill move at high percent.
- **Data needed:** Throw knockback/angle and thrower lag after release, tech tables, CPU weight.

### Platform tech chase

- **id:** `tech-chase-platform-coverage`
- **Goal:** Cover all techs on a platform with one positioned move.
- **Player:** [Marth](../characters/marth.md), [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Captain Falcon](../characters/captain-falcon.md), [Sheik](../characters/sheik.md)
- **CPU:** any
- **Setup:** Battlefield or Yoshi's Story; CPU launched onto a side platform in tumble.
- **CPU behaviour:** Random tech option on the platform (rolls stop at the platform edges).
- **Success:** Player hits the CPU before it acts.
- **Fail:** CPU escapes.
- **Variations:** Top platform; no-tech and slide-off cases.
- **Data needed:** Platform widths, roll distances, player move ranges.

### Missed-tech punish

- **id:** `tech-chase-missed-tech-optimal`
- **Goal:** Recognise a missed tech and take the biggest punish.
- **Player:** any
- **CPU:** any
- **Setup:** CPU knocked down near the player.
- **CPU behaviour:** 50% tech (random direction), 50% miss then random getup after a random wait.
- **Success:** On a miss: jab reset or strong hit lands before the getup. On a tech: normal chase success.
- **Fail:** Hit by getup attack, or weak punish chosen (configurable).
- **Variations:** CPU percent near jab reset limits.
- **Data needed:** Jab reset rules ([jab-reset](jab-reset.md)).

## Sources

- SSBWiki: Tech-chasing, Tech (https://www.ssbwiki.com/Tech-chase).
- Magus420's techs/getups frame data on Smashboards (Wayback Machine copy), tagged
  `[web:smashboards.com]`.
- FightCore (https://www.fightcore.gg/) for grab frames.
- Melee Library: "ASDI Down" (DruggedFox); videos listed but not viewable: "TechChasing"
  (Little England), "Platform Follow Ups" (Zero), "Tech Traps" (Sauc3).
- `[decomp]`: state names from this repository.
