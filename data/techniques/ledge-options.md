---
schema: melee-technique/v1
id: ledge-options
name: Ledge options
aliases: [edge options, ledge getup, ledge roll, ledge attack, ledge jump, tournament winner, ledgehop, edge hop, ledge intangibility, edgehog, ledgestall]
category: ledge
difficulty: 2
related: [ledgedash, edgeguarding, recovery, waveland, wall-jump, fast-fall]
characters: all
summary: Everything a character hanging on the ledge can do (stand, roll, attack, jump, let go into a hop, aerial, stall or ledgedash), with the intangibility and timing rules that decide which are safe.
---

# Ledge options

## What it is

A character who grabs the ledge is intangible for a short time and occupies the ledge (no
one else can grab it). From the hanging state there are four built-in getup actions and the
option to let go, which leads to everything else. Each built-in action has a fast version
below 100% damage and a slow version at 100% or more [wiki:Edge_getup] [wiki:Edge].

## Inputs

In priority order when pressed on the same frame [wiki:Edge_getup]:

| Option | Input | States [decomp] |
|-|-|-|
| Ledge attack | A, B, Z or C-stick up | `CliffAttackQuick` / `CliffAttackSlow` |
| Ledge roll | L, R or C-stick toward the stage | `CliffEscapeQuick` / `CliffEscapeSlow` |
| Ledge jump ("tournament winner") | X, Y or control stick up | `CliffJumpQuick1/2` / `CliffJumpSlow1/2` |
| Getup (climb) | control stick up/toward the stage | `CliffClimbQuick` / `CliffClimbSlow` |
| Let go | control stick down or away, or C-stick down or away | `Fall` |

Timing rule: on the last frame of `CliffCatch` the four getup actions are available but
letting go is not; letting go needs at least one frame of `CliffWait` [wiki:Ledgestall].

After letting go (the character keeps its double jump):

- **Ledgehop:** double jump immediately, then aerial, air dodge, special, or drift on
  stage [wiki:Edge_hop].
- **[Ledgedash](ledgedash.md):** double jump and air dodge onto the stage.
- **Drop, aerial, regrab** (for edgeguarding or stalling).
- **Ledgestall:** drop and regrab to refresh intangibility.
- **[Wall jump](wall-jump.md)** on stages with walls below the ledge.

## Frame data and formulas

> **Per-character numbers are in the character files.** Every character's ledge getup, roll,
> attack and jump (both below and from 100%) with intangibility and total length is in the
> `Ledge options` table of `../characters/<id>.md`, extracted from the game files, and in
> `../framedata/<id>.json` (`ledge_getup`, `ledge_roll`, `ledge_attack`, `ledge_jump_1`,
> `..._slow`). Use those where this page says a value is unknown or only sampled.

### Grab and intangibility

| Fact | Value | Source |
|-|-|-|
| `CliffCatch` length | 7 frames (Link 3) | [wiki:Ledgestall] |
| Intangibility from grabbing | 30 frames beyond `CliffCatch` (37 total; Link 33) | [wiki:Ledgestall] [wiki:Ledgedash] |
| Earliest let-go | frame 9 (Link 5) | [wiki:Ledgedash] |
| Intangibility kept after letting go | yes; it runs out on its original timer | [wiki:Edge] |
| Carry-over into getup actions | if a getup action's own intangibility ends earlier than the remaining ledge intangibility, the character stays intangible until the ledge timer ends (relevant for ledge attack and ledge jump done immediately) | [wiki:Edge] |
| Regrab lockout after letting go | 29 frames | [wiki:Ledgestall] |
| Facing | a character cannot grab a ledge behind them, with exceptions such as Captain Falcon's and Donkey Kong's up B | [wiki:Edge] |
| Holding down | prevents the automatic ledge grab | [wiki:Edge] |
| Ledge occupancy | all getup actions occupy the ledge for their whole animation, except ledge jump, which frees it when the character leaves the ledge | [wiki:Fox_(SSBM)/Edge_getups_(fast)] |
| Maximum hang time | Unknown here (the game forces the character off after a long hang) | [unverified] |

### Getup action timings

SSBWiki has per-character pages only for some characters; those read in this session are
below (intangible frames / total animation length). Other characters: Unknown here; the
values are character-specific animation lengths, so do not assume them.

Below 100% [wiki:Fox_(SSBM)/Edge_getups_(fast)] and the matching pages for the other
characters:

| Character | Getup | Roll | Jump (intangible / leaves ledge on / total) |
|-|-|-|-|
| Fox | 1-30 / 34 | 1-34 / 49 | 1-14 / 15 / 51 |
| Bowser | 1-30 / 34 | 1-34 / 49 | 1-3 / 4 / 37 |
| Peach | 1-30 / 32 | 1-39 / 50 | 1-10 / 11 / 38 |
| Pichu | 1-30 / 32 | 1-27 / 49 | 1-15 / 16 / 42 |
| Mr. Game & Watch | 1-30 / 34 | 1-27 / 49 | 1-12 / 13 / 37 |
| Yoshi | 1-30 / 33 | 1-23 / 49 | 1-13 / 14 / 35 |

At 100% or more [wiki:Fox_(SSBM)/Edge_getups_(slow)] and matching pages:

| Character | Getup | Roll | Jump (intangible / leaves ledge on / total) |
|-|-|-|-|
| Fox | 1-55 / 59 | 1-62 / 79 | 1-19 / 20 / 51 |
| Bowser | 1-55 / 59 | 1-59 / 79 | 1-17 / 18 / 47 |
| Peach | 1-55 / 59 | 1-64 / 79 | 1-20 / 21 / 48 |

Pattern in the sampled characters: fast getup is intangible through frame 30 and vulnerable
for the last 2-4 frames; slow getup is 59 frames with the last 4 vulnerable; fast roll is
49-50 frames with 10-26 vulnerable frames at the end; slow roll is 79 frames with 15-20
vulnerable frames at the end. Ledge attack timings were not on the pages read: Unknown.
Edge attacks have 1 bonus shield damage for most characters [wiki:Shield_damage].

A ledge-jumping character cannot act until the jump animation ends, but can fast fall from
the apex [wiki:Fox_(SSBM)/Edge_getups_(fast)] [wiki:Edge_getup].

### Option summary

| Option | Good for | Loses to | Source |
|-|-|-|-|
| Getup | fast below 100%, short vulnerable window | a hit timed to the last frames; reaction grab | [wiki:Edge_getup] |
| Roll | travels far inward; decent edgehog tool | being reacted to: long vulnerable tail, fixed distance | [wiki:Edge_getup] |
| Ledge attack | hits opponents standing at the edge | shield then punish; slow at 100%+ | [wiki:Edge_getup] |
| Ledge jump | rarely good: long, no action until it ends | almost anything on reaction | [wiki:Edge_getup] |
| Ledgehop aerial | flexible, keeps intangibility for a while | a hit after intangibility ends leaves the character offstage without a jump | [wiki:Edge_hop] |
| [Ledgedash](ledgedash.md) | fastest, intangible on stage | execution errors (SD) | [wiki:Ledgedash] |
| Stall / wait | timing mixup | anyone waiting out the intangibility | [wiki:Ledgestall] |

### Edgehogging

Because only one character can hold a ledge, grabbing it denies a recovering opponent the
ledge ("edgehog"). The grabber's intangibility protects them from the opponent's up B
hitbox. Rolling up from the ledge (long ledge occupancy plus intangibility) is a common way
to hold the ledge through the opponent's recovery [wiki:Edge-hogging] [wiki:Edge_getup].
See [edgeguarding](edgeguarding.md).

## Why it matters

Every stock involves the ledge several times. The defender's choice among these options and
the attacker's coverage of them ("ledge trapping") is a self-contained mixup, well suited
to drills: the option set is small and each has known timings. The 100% threshold changes
the picture completely: getup and roll become very slow, so above 100% players rely on
ledgehop and ledgedash.

## Common errors

- Ledge jump by accident when trying to ledgedash (jump pressed before the let-go
  registered).
- Rolling or standing up at 100%+ out of habit: 59-79 frames, easily punished.
- Ledgehop aerial started after intangibility ran out, trading or losing.
- Waiting on the ledge until intangibility ends, then being hit while hanging.
- Regrabbing too early (inside the 29-frame lockout) and falling past the ledge.
- Holding down while recovering and failing to grab the ledge.

## How to detect it in a training mode

- Ledge grab: `CliffCatch` then `CliffWait`. Percent at that moment selects Quick (<100) or
  Slow (>=100) variants.
- Option chosen = first state after `CliffWait`/`CliffCatch` (table above). Let-go leads to
  `Fall`; then `JumpAerialF/B` (ledgehop), `EscapeAir` (ledgedash or air dodge),
  `AttackAir*`, or `CliffCatch` again (stall).
- Intangibility remaining is a timer on the fighter; a drill can compare the frame the
  player becomes hittable with the frame the CPU's hitbox arrives.
- Success for a "get off the ledge" drill: player reaches a grounded actionable state on
  stage and is not hit for N frames.

## Drill seeds

### Ledge trap (attacker side)

- **id:** `ledge-options-cover-getup`
- **Goal:** React to and punish each ledge option.
- **Player:** any; classic for [Marth](../characters/marth.md), [Sheik](../characters/sheik.md), [Peach](../characters/peach.md), [Fox](../characters/fox.md)
- **CPU:** any
- **Setup:** CPU hanging on the ledge with fresh intangibility; player standing at a set distance.
- **CPU behaviour:** After a random wait, picks getup, roll, ledge attack, ledge jump, ledgehop aerial or ledgedash.
- **Success:** Player hits or grabs the CPU within its vulnerable frames and is not hit.
- **Fail:** CPU reaches centre stage or hits the player.
- **Variations:** CPU percent below/above 100; restrict the CPU to two options; add stall.
- **Data needed:** The timing tables above for the CPU character (Unknown for characters not listed), player move ranges.

### Get off the ledge (defender side)

- **id:** `ledge-options-escape-trap`
- **Goal:** Pick an option that beats the opponent's coverage.
- **Player:** any
- **CPU:** [Marth](../characters/marth.md), [Sheik](../characters/sheik.md), [Peach](../characters/peach.md)
- **Setup:** Player on the ledge; CPU positioned to trap.
- **CPU behaviour:** Shows one of several coverages (shield near ledge, charged smash at roll distance, jump for ledgehop) chosen at random before the player must act.
- **Success:** Player on stage, not hit, within N frames.
- **Fail:** Hit, or still on the ledge when intangibility is long gone.
- **Variations:** Above 100%.
- **Data needed:** Ledge option timings, CPU move data.

### Edgehog timing

- **id:** `ledge-options-edgehog-roll`
- **Goal:** Hold the ledge through an opponent's up B.
- **Player:** any
- **CPU:** [Marth](../characters/marth.md), [Captain Falcon](../characters/captain-falcon.md), [Sheik](../characters/sheik.md), [Fox](../characters/fox.md)
- **Setup:** CPU offstage below the ledge with up B available; player on stage near the ledge.
- **CPU behaviour:** Up B aimed at the ledge with random timing.
- **Success:** CPU fails to grab the ledge and is KO'd; player not hit.
- **Fail:** CPU grabs the ledge or lands on stage safely, or the player is hit off the ledge.
- **Variations:** Player must [wavedash](wavedash.md) back to grab the ledge; CPU sometimes recovers high (player must roll/stand and punish the landing).
- **Data needed:** CPU up B distance and timing, ledge intangibility.

## Sources

- SSBWiki: Edge, Edge getup (Edge recovery), Edge hopping, Edge-hogging, Ledgestall,
  Ledgedash, Shield damage, and the per-character pages `<Character>_(SSBM)/Edge_getups_(fast)`
  and `(slow)` for Fox, Bowser, Peach, Pichu, Mr. Game & Watch and Yoshi
  (https://www.ssbwiki.com/Fox_(SSBM)/Edge_getups_(fast)). Pages for the other characters
  did not exist when checked.
- `[decomp]`: state names from this repository.
