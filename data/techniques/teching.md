---
schema: melee-technique/v1
id: teching
name: Teching
aliases: [tech, ukemi, tech in place, tech roll, tech away, tech in, missed tech, getup, getup attack, tech lockout]
category: defense
difficulty: 2
related: [tech-chase, wall-tech, amsah-tech, asdi, jab-reset, hitstun-knockback, di]
characters: all
summary: Pressing L/R within 20 frames before hitting the floor while tumbling makes the character recover instantly in place or with a roll; missing it leaves them lying on the ground with slower, punishable getup options.
---

# Teching

## What it is

A character launched into tumble (knockback above 80, see
[hitstun-knockback](hitstun-knockback.md)) who touches the floor is knocked down. A digital
L or R press shortly before impact makes them **tech**: a quick recovery with
intangibility, in place or rolling left or right. Without it they bounce (**missed tech**)
and lie on the floor, where they must choose a getup option. The same input against a wall
or ceiling is a [wall tech](wall-tech.md). Internally these are the `Passive*` states
[wiki:Tech].

## Inputs

- **Tech in place:** press L or R (digital click; analog-only presses do not tech) at most
  20 frames before touching the ground, stick neutral.
- **Tech roll:** same, with the control stick held left or right at impact.
- **After a missed tech** (lying on the floor): nothing = stay down (limited time), up or
  tap = stand, left/right = roll, A or B = getup attack.
- **Tech lockout:** each press starts a 40-frame period in which another press cannot tech.
  Press once.

## Frame data and formulas

> Per-character tech, tech roll, missed-tech getup and getup attack lengths and intangibility
> are also in the `Techs and getups` table of each `../characters/<id>.md` (extracted from
> the game files; see `../README.md` on the one-frame entry delay).

### Tech window and lockout

| Fact | Value | Source |
|-|-|-|
| Window | a digital L/R press opens a 20-frame tech window | [wiki:Tech] |
| Lockout | a second press within 40 frames of the previous one closes the window; after a press there is a 40-frame lockout | [wiki:Tech] |
| Analog (light) press | does not open a window and does not cause lockout; this is why light-press or Z [L-cancels](l-cancel.md) are safer | [wiki:Tech] [wiki:L-canceling] |
| Press during hitlag | treated as pressed on every remaining hitlag frame: the window is 1 frame unless the press was on the last hitlag frame (then 20), and the 40-frame lockout starts when hitlag ends. In practice: press before the hit or after hitlag, not during it | [wiki:Tech] |
| Same-frame press | pressing on the frame of contact still techs | [wiki:Tech] |
| ASDI into the floor | on the first frame after hitlag, ASDI down can cause floor contact and a tech even when the launch angle points away from the floor | [wiki:Tech] |
| SDI into the floor | not allowed (SDI can reach walls/ceilings only) | [wiki:Tech] |

Consequence: a player hit shortly after shielding, air dodging, or L-cancelling with a hard
press may be unable to tech (they are inside their own lockout) [wiki:Tech].

### Tech animations (all characters unless noted)

Data from Magus420's "Techs & Getups Frame Data" [web:smashboards.com].

| Action | Total frames | Intangible | Notes |
|-|-|-|-|
| Tech in place (`Passive`) | 26 | 1-20 (Pichu, Pikachu: 1-24) | vulnerable for the last 6 frames (2 for Pichu/Pikachu) [wiki:Tech] |
| Tech roll forward/backward (`PassiveStandF/B`) | 40 | 1-20 | 20 vulnerable frames at the end |
| Missed tech bounce (`DownBoundU/D`) | 26 | none | can be hit; see [jab-reset](jab-reset.md) |
| Neutral getup (`DownStandU/D`) | 30 | 1-23 (Marth, Roy 1-22; Ice Climbers, Peach, Sheik, Zelda 1-20; Donkey Kong 1-24 from back) | |
| Getup attack (`DownAttackU/D`) | 49 (Pichu, Pikachu 50 from stomach) | varies | hits both sides, timing per character |
| Getup roll (`DownFowardU/D`, `DownBackU/D`) | 35 | varies per character and direction | |

### Tech roll distance and readability per character

"Move at" is Magus420's estimate of the frame on which the roll direction becomes visible;
distance is in his "ft" units (relative scale only). Forward/backward are relative to the
character's facing [web:smashboards.com].

| Character | Roll forward: move at / distance | Roll backward: move at / distance |
|-|-|-|
| Bowser | 14 / 13.8 | 8 / 13.6 |
| Captain Falcon | 11 / 16.6 | 8 / 13.6 |
| Donkey Kong | 9 / 14.8 | 10 / 14.8 |
| Dr. Mario | 9 / 14.6 | 10 / 14.6 |
| Falco | 9 / 14.4 | 6 / 14.4 |
| Fox | 9 / 12.6 | 6 / 12.6 |
| Ganondorf | 11 / 18.6 | 8 / 15.2 |
| Ice Climbers | 9 / 15.2 | 16 / 15.2 |
| Jigglypuff | 11 / 11.8 | 10 / 14.8 |
| Kirby | 10 / 12.4 | 10 / 14.4 |
| Link | 11 / 16.2 | 9 / 16.2 |
| Luigi | 9 / 16.6 | 10 / 16.6 |
| Mario | 9 / 14.6 | 10 / 14.6 |
| Marth | 9 / 15.2 | 8 / 15.2 |
| Mewtwo | 17 / 13.6 | 17 / 13.4 |
| Mr. Game & Watch | 7 / 9.8 | 7 / 9.6 |
| Ness | 9 / 13.2 | 9 / 13.2 |
| Peach | 8 / 15.4 | 9 / 15.6 |
| Pichu | 12 / 8.4 | 10 / 8.4 |
| Pikachu | 10 / 12 | 9 / 13.2 |
| Roy | 9 / 14.2 | 8 / 14.4 |
| Samus | 10 / 11.8 | 9 / 11.8 |
| Sheik | 10 / 16.2 | 6 / 16.2 |
| Yoshi | 10 / 14.6 | 12 / 14.4 |
| Young Link | 11 / 12.8 | 9 / 12.8 |
| Zelda | 8 / 16.6 | 9 / 16.6 |

Notes from the same source: a tech roll into an edge stops at the edge; for Mewtwo and
Pikachu (forward roll) acting as the roll ends at an edge makes them slip off
[web:smashboards.com] [wiki:Tech].

### Missed tech specifics

- Lying on the floor (`DownWaitU` face up / `DownWaitD` face down) the character can be hit
  by anything; weak hits cause a [jab reset](jab-reset.md).
- A lying character holding down can [ASDI down](asdi.md) and tech a weak follow-up hit if
  not in lockout [lib:ASDI Down].
- Getup attack hit frames differ per character (e.g. Fox/Falco from back: front hit 17-19,
  rear hit 24-26; Marth and Roy from back: rear hit first, 20-23; Sheik from back: front hit
  first, 17-19)
  [web:smashboards.com].

## Why it matters

A missed tech is the worst outcome of most hits: the attacker gets a jab reset or a free
charged smash. Teching limits the damage but each tech option can be covered by a prepared
opponent ([tech-chase](tech-chase.md)), so defenders must mix tech in place, tech away, tech
in and (rarely, deliberately) no tech. For a training mode, the tech tables define the CPU's
realistic options after any knockdown and the windows the player has to punish them.

## Common errors

- Pressing twice (panic mashing): the second press cancels the window. In game: the
  character bounces even though the player "pressed in time".
- Pressing during hitlag of a hit that sends straight into the floor.
- Pressing too early (more than 20 frames before impact), common when launched from height.
- Being locked out by an earlier hard press: L-cancel, shield, air dodge or wavedash input
  less than 40 frames before.
- Always teching the same direction; teching toward the ledge into a waiting opponent;
  tech roll off a platform edge is not possible, so the roll stops and is easy to cover.

## How to detect it in a training mode

- Knockdown incoming: victim in `DamageFly*` / `DamageFall` moving toward the floor.
- Outcome on floor contact: `Passive` (in place), `PassiveStandF`, `PassiveStandB` (rolls,
  relative to facing), or `DownBoundU`/`DownBoundD` (missed) [decomp].
- Input feedback: frames between the last digital L/R press and contact (success needs
  1-20, with no other digital press in the 40 frames before that press). Report "pressed N
  frames early", "double press", or "pressed in hitlag".
- Getup option after a miss: `DownStand*`, `DownAttack*`, `DownFoward*`, `DownBack*`
  (the decomp spells it `DownFoward`), or still `DownWait*`.
- Vulnerability window for the attacker side: frames 21-26 of `Passive`, frames 21-40 of
  the rolls.

## Drill seeds

### Tech every knockdown

- **id:** `teching-basic-ground-tech`
- **Goal:** Tech consistently with a single press and chosen direction.
- **Player:** any
- **CPU:** [Marth](../characters/marth.md), [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md)
- **Setup:** Player at 40-80%, CPU adjacent on flat stage.
- **CPU behaviour:** Hits with a knockdown move (Sheik dthrow or dash attack, Marth fthrow at mid percent, Falcon dthrow); the drill shows a direction prompt during hitstun.
- **Success:** Player techs in the prompted direction.
- **Fail:** Missed tech, wrong direction, or double press.
- **Variations:** Hit comes right after the player had to L-cancel (lockout awareness); platform knockdowns; no prompt, but the CPU covers one option at random.
- **Data needed:** Knockback of the CPU move at the percent (must exceed 80).

### Getup option mixing

- **id:** `teching-missed-tech-getup`
- **Goal:** Choose a safe getup after a missed tech.
- **Player:** any
- **CPU:** any
- **Setup:** Player starts in `DownWait*`; CPU nearby.
- **CPU behaviour:** Covers one of: stand, roll in, roll away, getup attack (by shielding then punishing), chosen at random, or attempts a jab reset.
- **Success:** Player is not hit for 60 frames after getting up.
- **Fail:** Hit, grabbed or jab reset.
- **Variations:** Near the ledge; on a platform.
- **Data needed:** Getup durations and intangibility from the tables above.

### Tech under lockout pressure

- **id:** `teching-no-lockout-lcancel`
- **Goal:** L-cancel with a light press or Z so a tech is still available.
- **Player:** any
- **CPU:** any with a fast knockdown counter-hit
- **Setup:** Player does a falling aerial on the CPU's shield; CPU counter-hits with a tumble-knockback move right after.
- **CPU behaviour:** Out-of-shield knockdown move timed after the player's landing.
- **Success:** Player L-cancels and techs the following hit.
- **Fail:** Missed tech because of lockout.
- **Variations:** Player must use Z or a light press.
- **Data needed:** Tech lockout rules.

## Sources

- SSBWiki: Tech, L-canceling (https://www.ssbwiki.com/Tech).
- Magus420, "Detailed Throws, Techs and Getups Frame Data", Smashboards
  (http://smashboards.com/threads/detailed-throws-techs-and-getups-frame-data.206469/,
  second post, read through the Wayback Machine); tagged `[web:smashboards.com]`.
- Melee Library: "ASDI Down" (DruggedFox); "A Guide to DI, Smash DI, C-stick DI, Teching, and
  Crouch Cancelling" (Doraki) for the tech window and lockout explanation. "Diagrams of L/R
  Tech Input Down Time" (Kadano, image) and "Teching and Advanced DI" (Kadano, video) not
  readable.
- `[decomp]`: state names from this repository.
