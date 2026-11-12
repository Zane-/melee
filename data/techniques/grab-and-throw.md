---
schema: melee-technique/v1
id: grab-and-throw
name: Grab and throw
aliases: [grab, shield grab, dash grab, JC grab, pummel, throw, grab release, mashing out, grab break, throw DI, boost grab]
category: offense
difficulty: 1
related: [jump-cancel, chain-grab, tech-chase, di, shield, out-of-shield, shield-pressure, pivot]
characters: all
summary: Grabs beat shields and crouch cancel; this file gives grab speeds and ranges, how the held character escapes, and the throw rules (weight-dependent speed, DI timing, fixed weight in knockback) that combos and chain grabs depend on.
---

# Grab and throw

## What it is

A grab is an unblockable attack that catches a grounded or airborne opponent in front of the
character. The grabber can pummel (A) for small damage or throw in one of four directions.
The held character escapes after a time that mashing shortens. Throws are the main combo
starters for many characters and cannot be crouch cancelled, shielded or SDI'd
[wiki:Grab] [wiki:Throw].

## Inputs

- **Standing grab:** Z, or A while holding L/R. From shield, A is a shield grab
  ([out-of-shield](out-of-shield.md)).
- **Dash grab:** Z while dashing or running (`CatchDash`): slower, more lag, some extra
  range from momentum.
- **[Jump-cancel](jump-cancel.md) grab:** jump then Z during jump squat: standing grab out
  of a run.
- **Pummel:** A while holding. **Throw:** control stick or C-stick direction.
- **Held character:** mash buttons and stick to escape; hold a [DI](di.md) direction before
  the throw releases.

## Frame data and formulas

### Grab speed per character

First active frames and total animation length (whiff) [web:fightcore.gg]:

| Character | Standing grab active | Total | Dash grab active | Total |
|-|-|-|-|-|
| Sheik | 6-7 | 30 | 8-9 | 40 |
| Fox, Falco | 7-8 | 30 | 12-13 | 40 |
| Marth, Roy | 7-8 | 30 | 10-11 | 40 |
| Captain Falcon | 7-8 | 30 | 11-12 | 40 |
| Ganondorf | 7-8 | 30 | 11-13 | 40 |
| Peach, Ice Climbers | 7-8 | 30 | 7-8 | 40 |
| Mewtwo | 7-8 | 30 | 9-10 | 40 |
| Mario, Dr. Mario, Luigi, Pikachu, Pichu, Jigglypuff, Kirby, Mr. Game & Watch | 7-8 | 30 | 11-12 | 40 |
| Donkey Kong, Ness | 8-9 | 30 | 10-11 | 40 |
| Bowser | 9-10 | 40 | 10-12 | 50 |
| Zelda | 12-13 | 30 | 12-13 | 40 |
| Link | 11-17 | 85 | 12-17 | 95 |
| Young Link | 11-14 | 85 | 14-17 | 95 |
| Samus | 18-37 | 94 | 18-33 | 74 |
| Yoshi | 18-23 | 79 | 11-16 | 70 |

### Grab range

Distance from the character's origin to the tip of the farthest grab box, in units
[wiki:Grab]: Samus 43.04, Link 35.30, Young Link 25.30, Yoshi 20.56, Bowser 19.24,
Marth 18.73, Roy 17.83, Donkey Kong 17.58, Kirby 15.21, Sheik and Mewtwo 14.45,
Jigglypuff 14.19, Falco 13.36, Mr. Game & Watch 13.05, Luigi 12.99, Zelda 12.76, Fox 12.16,
Peach 11.99, Ganondorf 11.50, Ice Climbers 11.28, Captain Falcon 10.73, Pichu 10.35,
Mario and Dr. Mario 10.02, Ness 9.96, Pikachu 9.84. The wiki notes this over-rates large
bodies (Bowser, Yoshi): Marth's is the best non-tether grab relative to his size.

### Escaping a grab (mashing)

From Sycorax's write-up, quoting Schmooblidon [lib:Mechanics of Mashing Out of Grab]:

- On being grabbed the victim gets a counter that depends on their damage. It decreases by
  1 every frame and by a further 6 for each counted input. At 0 the victim breaks free.
- Counted inputs: presses of A, B, X, Y, L, R, Z, and control stick "smash" inputs.
  Not counted: C-stick, D-pad, Start.
- Two buttons pressed on the same frame count once. L and R count as the same button
  (holding L and mashing R gives one input); any amount of trigger press counts as held.
  Z counts as A + trigger on one frame.
- Stick: each input must be a new smash input that crosses the x or y axis; rocking between
  two neighbouring directions in one quadrant only counts once each. Rotating or swinging
  across the centre gives repeated inputs.
- The formula for the initial counter value was not in the sources read: Unknown.

Grab release: [Bowser](../characters/bowser.md)'s release animation as the grabber, and
[Donkey Kong](../characters/donkey-kong.md)'s as the one released, are 10 frames shorter
than normal, giving them guaranteed follow-ups in theory [wiki:Grab_release].

### Throw rules

| Fact | Value | Source |
|-|-|-|
| Thrower invincibility | frames 1-8 of every throw | [wiki:Throw] [web:smashboards.com] |
| Weight in throw knockback | always 100: every character is launched the same at the same percent; fall speed and gravity then differ | [wiki:Throw] |
| Weight-dependent throw speed | many throws animate faster on light victims and slower on heavy ones: multiply the listed release and total frames by the victim's multiplier and round up | [web:smashboards.com] |
| Hitlag on release | none, so no SDI on the throw itself; hits inside the animation have hitlag and can be SDI'd | [wiki:Hitlag] [wiki:Throw] |
| DI read | the frame immediately before release | [web:smashboards.com] |
| Crouch cancel | does not apply to throws | [wiki:Crouch_cancel] |
| Escapable throws | Donkey Kong's cargo fthrow; Kirby's fthrow and bthrow can be mashed out of | [wiki:Throw] |
| Thrown character as hitbox | a thrown character damages bystanders they collide with | [wiki:Knockback] |

Throw speed multipliers by victim (NTSC) [web:smashboards.com]:

| Multiplier | Victim |
|-|-|
| 1.17 | Bowser |
| 1.14 | Donkey Kong |
| 1.10 | Samus |
| 1.09 | Ganondorf |
| 1.08 | Yoshi |
| 1.04 | Captain Falcon, Link |
| 1.00 | Dr. Mario, Luigi, Mario |
| 0.94 | Ness |
| 0.90 | Peach, Sheik, Zelda |
| 0.88 | Ice Climbers |
| 0.87 | Marth |
| 0.85 | Mewtwo, Roy, Young Link |
| 0.80 | Falco, Pikachu |
| 0.75 | Fox |
| 0.70 | Kirby |
| 0.60 | Jigglypuff, Mr. Game & Watch |
| 0.55 | Pichu |

Example from the source: Bowser fthrow releases on frame 35 with first actionable frame 60;
on Fox that becomes release 27 (26.25 rounded up) and actionable 45. Which throws are
weight-dependent is listed per throw in the source (e.g. Jigglypuff uthrow yes, dthrow no;
Sheik's four throws no; Mewtwo uthrow and fthrow yes) [web:smashboards.com]; per-character
lists belong in the character files.

## Why it matters

- The grab is the answer to shield and to [crouch cancel](crouch-cancel.md); without it
  defence would be free.
- Throws start [chain grabs](chain-grab.md), [tech chases](tech-chase.md) and kill
  set-ups ([Marth](../characters/marth.md) uthrow/fthrow, [Sheik](../characters/sheik.md)
  dthrow, [Fox](../characters/fox.md) uthrow uair, [Jigglypuff](../characters/jigglypuff.md)
  uthrow Rest, [Captain Falcon](../characters/captain-falcon.md) dthrow/uthrow,
  [Ice Climbers](../characters/ice-climbers.md) hand-offs).
- A whiffed grab is very punishable (30 frames total, far more for tethers).
- The victim's only defences are mashing early, DI on the throw, and SDI on throw hits.

## Common errors

- Dash grab where a jump-cancel grab was intended (slower, 40-frame whiff).
- Grabbing an opponent who is intangible (tech, ledge, spot dodge) or just out of range.
- Too many pummels at low percent: the opponent mashes out.
- Throwing immediately every time: at very fast releases the opponent cannot react with
  DI, but the thrower also cannot react to their held DI; throwing late lets them mash out.
- As the victim: mashing the control stick and then having it in a random position when
  the throw releases (bad DI).

## How to detect it in a training mode

- Grabber states: `Catch`/`CatchDash` (attempt), `CatchPull`, `CatchWait` (holding),
  `CatchAttack` (pummel), `ThrowF/B/Hi/Lw`, `CatchCut` (released) [decomp].
- Victim states: `CapturePulledHi/Lw`, `CaptureWaitHi/Lw`, `CaptureDamageHi/Lw`,
  `ThrownF/B/Hi/Lw`, `CaptureCut`/`CaptureJump` (escaped) [decomp].
- Mash feedback: count qualifying inputs per frame while in `CaptureWait*` and show inputs
  per second and frames until escape.
- Throw DI: stick on the frame before the release frame (see [di](di.md)).

## Drill seeds

### Mash out

- **id:** `grab-and-throw-mash-escape`
- **Goal:** Escape grabs quickly and end with the stick in a chosen DI position.
- **Player:** any
- **CPU:** any
- **Setup:** Player grabbed at a chosen percent.
- **CPU behaviour:** Pummels, then throws after a random delay.
- **Success:** Player escapes before the throw, or if thrown, holds the prompted DI on the release frame.
- **Fail:** Thrown with wrong DI.
- **Variations:** Percent; CPU throws quickly.
- **Data needed:** Mash rules above; initial counter (measure in engine).

### Grab the shield

- **id:** `grab-and-throw-punish-shield`
- **Goal:** Recognise a held shield and grab it.
- **Player:** any
- **CPU:** any
- **Setup:** CPU at mid range.
- **CPU behaviour:** Randomly holds shield, or attacks when the player comes into range.
- **Success:** Grab on shield, or avoid/punish the attack.
- **Fail:** Hit, or attacked a shield and got shield-grabbed.
- **Variations:** CPU spot dodges sometimes.
- **Data needed:** Grab ranges and frames.

### Throw follow-up versus DI

- **id:** `grab-and-throw-followup-di-read`
- **Goal:** Follow the opponent's DI after a combo throw.
- **Player:** [Marth](../characters/marth.md), [Sheik](../characters/sheik.md), [Fox](../characters/fox.md), [Captain Falcon](../characters/captain-falcon.md), [Jigglypuff](../characters/jigglypuff.md), [Peach](../characters/peach.md)
- **CPU:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Captain Falcon](../characters/captain-falcon.md), [Marth](../characters/marth.md), [Sheik](../characters/sheik.md)
- **Setup:** CPU grabbed at a percent inside the combo window.
- **CPU behaviour:** Random DI (left, right, none), then jumps or attacks as soon as hitstun ends.
- **Success:** Follow-up hit or regrab connects during hitstun.
- **Fail:** CPU acts first.
- **Variations:** Percent sweep; platforms.
- **Data needed:** Throw data (release frame, angle, knockback), weight multiplier, CPU fall speed.

## Sources

- SSBWiki: Grab, Throw, Grab release, Hitlag, Knockback, Crouch cancel
  (https://www.ssbwiki.com/Grab).
- FightCore (https://www.fightcore.gg/) character pages for grab frames.
- Magus420, "Detailed Throws, Techs and Getups Frame Data" (Smashboards, Wayback Machine
  copy), tagged `[web:smashboards.com]`.
- Melee Library: "Mechanics of Mashing Out of Grab" (Sycorax, Wayback Machine copy).
  Not readable: "How Port Priority Affects Throws" (Stratocaster), "Boost Grab Stats"
  (Schmooblidon), "Buffering Dthrow" (video).
- `[decomp]`: state names from this repository.
