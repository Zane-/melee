---
schema: melee-character/v1
id: luigi
name: Luigi
aliases: [Weegee, Green Mario]
tier: "B- (12th of 26), 2021 tier list"
archetype: [floaty, technical, mixup, punish-heavy, tech-chase, edgeguarder]
related: [mario, dr-mario]
summary: Luigi slides across the stage on the longest wavedash in the game to land down smash, grab or forward tilt, then juggles with vertical launchers and kills with forward air, down air, up smash or a one-frame up B sweetspot.
key_tech: [wavedash-movement, wavesmash, wavedash-tech-chase, fire-jump-punch, nair-combo-breaker, green-missile-misfire, rising-cyclone, cyclone-charge, vududash, double-bair, uthrow-chain-grab]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlLg.dat
framedata: ../framedata/luigi.json
code: src/melee/ft/kinds/ftLuigi
specials:
  neutral_b: "Fireball"
  side_b: "Green Missile"
  up_b: "Super Jump Punch"
  down_b: "Luigi Cyclone"
attributes:
  weight: 100
  gravity: 0.069
  fall_speed: 1.6
  fast_fall_speed: 2
  jump_squat: 4
  jumps: 2
  walk_speed: 1.1
  dash_speed: 1.3
  run_speed: 1.34
  traction: 0.025
  air_speed: 0.68
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [2, 16, 3]
  jab2: [3, 19, 2]
  jab3: [5, 23, 5]
  dash_attack: [4, 59, 2]
  ftilt_high: [4, 32, 10]
  ftilt: [4, 32, 10]
  ftilt_low: [4, 32, 10]
  utilt: [4, 30, 9]
  dtilt: [5, 35, 9]
  fsmash_high: [12, 42, 14]
  fsmash: [12, 42, 13]
  fsmash_low: [12, 42, 12]
  usmash: [9, 40, 17]
  dsmash: [5, 38, 17]
  nair: [3, 46, 15]
  fair: [7, 33, 12]
  bair: [6, 29, 11]
  uair: [5, 30, 13]
  dair: [10, 29, 16]
  grab: [7, 31, 0]
  dash_grab: [11, 41, 0]
  pummel: [17, 25, 3]
  fthrow: [null, 28, 8]
  bthrow: [null, 67, 10]
  uthrow: [null, 40, 7]
  dthrow: [null, 40, 7]
  special_n: [null, 47, 0]
  special_air_n: [null, 47, 0]
  special_s_start: [null, 18, 0]
  special_s_hold: [null, 8, 0]
  special_s: [4, 44, 10]
  special_s_300: [4, 44, 25]
  special_s_301: [null, 44, 0]
  special_s_end: [null, 41, 0]
  special_air_s_start: [null, 18, 0]
  special_air_s_hold: [null, 8, 0]
  special_s_305: [4, 44, 10]
  special_s_306: [4, 44, 25]
  special_air_s_end: [null, 30, 0]
  special_hi: [5, 40, 25]
  special_air_hi: [5, 40, 20]
  special_lw: [6, 80, 12]
  special_air_lw: [6, 80, 12]
oos:  # option: frame the hitbox is out
  special_hi: 6
  nair: 7
  grab: 7
  uair: 9
  bair: 10
  usmash: 10
  special_air_lw: 10
  fair: 11
  dair: 14
resources: 20
# generated: end
---

# Luigi

<!-- GENERATED:attributes -->
## Attributes

Read from `PlLg.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 100 |
| Gravity | 0.069 |
| Terminal fall speed | 1.6 |
| Fast-fall speed | 2 |
| Jump squat (frames before airborne) | 4 |
| Full hop / short hop initial Y speed | 2.4 / 1.4 |
| Air jump Y multiplier | 0.9 |
| Jumps | 2 |
| Walk max speed | 1.1 |
| Dash initial speed / run max speed | 1.3 / 1.34 |
| Ground friction (traction) | 0.025 |
| Air max horizontal speed | 0.68 |
| Air acceleration (base + stick) | 0.015 + 0.025 |
| Air friction | 0.01 |
| Normal landing lag | 4 |
| Shield size | 10.75 |
<!-- /GENERATED:attributes -->

## Overview

Luigi is a semi-clone of [Mario](mario.md) with extreme physics: the lowest traction, the
lowest air speed, one of the slowest dashes, a very high jump and a slow fall
[wiki:Luigi_(SSBM)]. The low traction gives him the longest
[wavedash](../techniques/wavedash.md) in the game, close to half the length of Final
Destination per wavedash [wiki:Luigi_(SSBM)], and nearly all of his ground movement is
wavedashing rather than running. He wins neutral by sliding in and out of range and attacking
during the slide, most often with down smash, which hits on frame 5 and launches straight up
[wiki:Luigi_(SSBM)/Down_smash]. His punish game is juggling: down smash, up tilt, nair and
up throw all send vertically and chain into each other, and he finishes with fair, dair, up
smash, or the up B sweetspot (Fire Jump Punch, often called shoryuken), a single-frame hitbox
that does 25% [wiki:Luigi_(SSBM)/Up_special]. He dies off the top early because he is floaty,
gets juggled because he cannot fall or drift out, and has a long but slow and linear recovery
that is easy to intercept [wiki:Luigi_(SSBM)]. He is technically demanding: a Luigi player
must control wavedash length precisely [wiki:Luigi_(SSBM)].

## Strengths and weaknesses

- **Strengths:**
  - Wavedash distance and speed; attacks, grabs and shield are all available during the slide.
  - Down smash: frame 5, both sides, 17%, 90° launch [fd].
  - Nair: frame 3, 15% clean, launches at 90°, 7 frames of landing lag when
    [L-cancelled](../techniques/l-cancel.md) [fd]. Best combo breaker among floaties.
  - Strong aerial finishers: fair 12% with base knockback 43, dair 16% [fd].
  - Fire Jump Punch: 25% grounded, kills very early [wiki:Luigi_(SSBM)/Up_special].
  - Destroys [Fox](fox.md)'s and [Falco](falco.md)'s recoveries with fair, bair and fireballs
    [lib:Smash God's Epic 2000th Post Luigi Guide 2009].
- **Weaknesses:**
  - Worst air speed in the game; aerial approaches are slow and committal
    [wiki:Luigi_(SSBM)].
  - Short [dash dance](../techniques/dash-dance.md), slow dash, short reach.
  - Low traction pushes him far away when his shield is hit, which removes many
    [out of shield](../techniques/out-of-shield.md) punishes [wiki:Luigi_(SSBM)].
  - Floaty: juggled easily, dies early off the top.
  - Recovery: up B has no horizontal movement, side B has about half a second of end lag
    [wiki:Luigi_(SSBM)/Side_special], down B needs very fast mashing.
  - Weak projectile (fireball: slow, 6%, lasts 50 frames [wiki:Fireball]).

## Character tech

### Wavedash movement

- **id:** `wavedash-movement`
- **What:** Luigi's standard way to move: jump and immediately air dodge diagonally into the
  ground, sliding a long distance while free to act.
- **Inputs:** Jump (X/Y), then L/R with the stick diagonally down-left or down-right on the
  first airborne frame. A shallower stick angle gives a longer slide.
- **Timing:** A full wavedash costs 14 frames before Luigi can act (jumpsquat plus 10 frames
  of landing lag) [lib:20GX: On Luigi]; the jumpsquat is 4 frames [unverified]. He keeps
  sliding after he becomes actionable. Luigi is ranked first of the cast for wavedash length
  [wiki:Wavedash].
- **Used for:** Approaching, retreating, spacing forward tilt and down smash, wavedash out of
  shield, moving between platforms with [wavelands](../techniques/waveland.md). The wiki
  notes he covers ground faster by wavedashing than by dashing [wiki:Wavedash].
- **Common errors:** Air dodging late (visible hop, shorter slide); wrong angle (too steep
  gives a short slide, too flat gives an air dodge that does not land); sliding off the edge
  unintentionally.
- **Drill idea:** Target zones on the floor at different distances; success when Luigi stops
  inside the zone, with the required slide length selected at random.

### Wavesmash

- **id:** `wavesmash`
- **What:** A smash attack (or tilt, jab, grab) input during the wavedash slide, so the
  attack travels with Luigi.
- **Inputs:** Wavedash toward the opponent, then C-stick down (down smash), forward tilt, or
  Z on the first actionable frame.
- **Timing:** Earliest down smash hit is 14 + 5 = frame 19 from the jump input
  [lib:20GX: On Luigi]. Down smash front hit frames 5-6, back hit 14-15, 37 frames total
  [wiki:Luigi_(SSBM)/Down_smash]. On shield it is at worst -23 when only the first hit
  connects, but Luigi's slide and the shield pushback usually carry him out of punish range
  [wiki:Luigi_(SSBM)/Down_smash]. Charging a forward smash mid-slide stops the slide
  instantly [wiki:Luigi_(SSBM)].
- **Used for:** His main approach. On hit, down smash pops the opponent up for a juggle. An
  opponent who [crouch cancels](../techniques/crouch-cancel.md) it is usually hit by both
  hits (up to 34%) [wiki:Luigi_(SSBM)/Down_smash].
- **Common errors:** Attacking before landing lag ends (nothing comes out); sliding past the
  opponent so the weaker timing hits; down smash from too far.
- **Drill idea:** CPU stands or dash dances at mid range; success when a wavedash down smash
  hits within N frames of the jump input.

### Wavedash tech chase

- **id:** `wavedash-tech-chase`
- **What:** A reaction [tech chase](../techniques/tech-chase.md) built on jumping during the
  opponent's tech animation, then choosing between a jump-cancelled grab (tech in place) and
  a wavedash left or right into down smash or up tilt (tech rolls)
  [lib:20GX: On Luigi].
- **Inputs:** Stand next to the knocked-down opponent. When the tech starts, input jump; if
  it is tech in place, press Z during jumpsquat ([jump-cancel](../techniques/jump-cancel.md)
  grab); otherwise air dodge toward the roll direction and down smash (front hit covers
  roll away) or up tilt on landing.
- **Timing:** Using the source's frame counts (tech in place lasts 26 frames, tech rolls 40):
  jump on tech frame 15, decide by frame 19, airborne on frame 20, grab comes out on frame 26
  if chosen, wavedash lag ends around frame 30, tech roll ends at frame 40. The latest jump
  that still punishes a roll with down smash is frame 21, because 21 + 14 (wavedash) + 5
  (down smash) = 40 [lib:20GX: On Luigi]. Down smash and up tilt launch vertically, which
  is the hardest launch to resist with [ASDI](../techniques/asdi.md) down
  [lib:20GX: On Luigi].
- **Used for:** Punishing every tech option of fastfallers after down throw, a knockdown hit,
  or a missed tech.
- **Common errors:** Jumping too early (full hop instead of a decision); picking the wrong
  side; using down smash at a percent where it does not knock down a crouching opponent.
- **Drill idea:** CPU techs in place, toward or away at random; success when Luigi hits or
  grabs within 4 frames of the CPU becoming vulnerable.

### Fire Jump Punch

- **id:** `fire-jump-punch`
- **What:** The up B (Super Jump Punch) sweetspot: a tiny hitbox at Luigi's jaw on one frame.
  It does 25% grounded (20% aerial) with strong vertical knockback. Every later frame is a 1%
  sourspot with almost no hitstun [wiki:Luigi_(SSBM)/Up_special].
- **Inputs:** Stand touching the opponent, up B. Usually done from a wavedash, a jab, or a
  jab reset.
- **Timing:** Sweetspot on frame 5 only; sourspot frames 6-23; Luigi is intangible frames
  5-8; 39 frames of animation then special fall [wiki:Luigi_(SSBM)/Up_special]. Landing on a
  platform after it shortens the end lag [wiki:Luigi_(SSBM)/Up_special].
- **Used for:** Killing. It kills Fox on Dream Land at 92% even with perfect survival DI
  (directional influence), and [Jigglypuff](jigglypuff.md) under 40% on most stages
  [wiki:Luigi_(SSBM)/Up_special]. Setups listed by the wiki: wavedash in during a tech
  chase, juggle finisher, after a [jab reset](../techniques/jab-reset.md) or shield break, a
  missed Rest, and the landing lag of [Marth](marth.md), [Sheik](sheik.md),
  [Captain Falcon](captain-falcon.md) or [Ganondorf](ganondorf.md) up B forced onto the stage
  by an edgehog. Also out of shield against an opponent directly on top of him. A late nair
  into up B at around 40% is a known link on many characters [wiki:Super_Jump_Punch].
- **Common errors:** Standing slightly too far (sourspot: 1% and Luigi is helpless above the
  opponent); wrong facing.
- **Drill idea:** CPU Sheik lands on stage in up B landing lag at 60%; success only if the
  25% hitbox connects.

### Nair combo breaker

- **id:** `nair-combo-breaker`
- **What:** Nair comes out on frame 3, covers Luigi's body, and launches straight up, so a
  nair thrown in a gap of the opponent's combo both ends the combo and starts Luigi's
  [wiki:Luigi_(SSBM)/Neutral_aerial].
- **Inputs:** A (or C-stick) with no direction as soon as hitstun ends.
- **Timing:** Clean hit frames 3-6 (15%), late hit 7-31 (8%), auto-cancel on frames 1-2 and
  from 36; landing lag 15, or 7 L-cancelled [wiki:Luigi_(SSBM)/Neutral_aerial].
- **Used for:** Escaping juggles and shield pressure follow-ups; starting juggles (clean hit
  at low percent, late hit at mid percent); shield pressure after a fair or dair in the same
  jump.
- **Common errors:** Mashing it against a true combo (no effect) or against a disjointed
  follow-up that outranges it.
- **Drill idea:** CPU performs a string with a gap of a few frames; success when Luigi's nair
  hits in the gap.

### Green Missile and misfire

- **id:** `green-missile-misfire`
- **What:** Side B launches Luigi sideways; it is his main horizontal recovery. Each use has
  a 1 in 8 chance to misfire, which travels much farther and does 25%
  [wiki:Luigi_(SSBM)/Side_special].
- **Inputs:** Side B, hold to charge, release. Tapping the stick (smash input) makes an
  uncharged missile travel farther than a held input [wiki:Green_Missile].
- **Timing:** Full charge takes about three seconds [wiki:Green_Missile]. End lag in the air
  is about half a second; landing on stage during it leaves Luigi helpless for a 41-frame
  landing animation [wiki:Luigi_(SSBM)/Side_special]. Landing on the very edge of a platform
  edge-cancels the lag [wiki:Luigi_(SSBM)/Side_special]. A misfire flies farther than the
  length of Final Destination [wiki:Green_Missile] and kills Fox at 71% from the middle of
  Battlefield [wiki:Luigi_(SSBM)/Side_special].
- **Used for:** Recovery: one charged missile at ledge height, or several uncharged missiles
  from high up (each one is another misfire roll)
  [lib:Smash God's Epic 2000th Post Luigi Guide 2009].
- **Common errors:** Using it low (the end lag drops him below the ledge); landing on stage
  in lag; misfiring off the far side of the stage.
- **Drill idea:** Recovery drill with a forced-misfire toggle so the player practises both
  outcomes.

### Rising cyclone

- **id:** `rising-cyclone`
- **What:** Mashing B during an aerial down B (Luigi Cyclone) makes Luigi rise, if the
  cyclone is "charged" (see next entry).
- **Inputs:** Down B in the air, hold left/right to drift, press B repeatedly with at least
  one released frame between presses.
- **Timing:** Presses on frames 1-5 do nothing; the mash window is frames 6-43. Five presses
  starting on frame 6 return Luigi to his starting height, 6 is the minimum to gain height,
  and 19 (every other frame from frame 6) is the maximum. Not mashing for about 7 frames at
  the start or 11 near the end loses the rise. Mash fastest at the start to cancel the
  initial downward movement. Luigi can act on frame 80 (double jump can be buffered from
  frame 77) [lib:Rising Cyclone (PTP) Frame Data Guide]. The wiki gives the height tiers as:
  under 5 presses lose height, 5-7 hold height, 8-10 give about half of maximum, 12-13 about
  two thirds, 14-18 near maximum [wiki:Luigi_Cyclone].
- **Used for:** Vertical and horizontal recovery; it does not cause special fall, so side B
  or up B can follow [wiki:Luigi_Cyclone].
- **Common errors:** Starting to mash before frame 6 and tiring early; mashing with an
  uncharged cyclone.
- **Drill idea:** Report presses registered in frames 6-43 and net height; pass at 8 or more.

### Cyclone charge

- **id:** `cyclone-charge`
- **What:** The cyclone can only rise if its hidden state is "charged". Touching the ground
  at any point during a cyclone sets it charged; being airborne on frame 44 of a cyclone sets
  it uncharged [lib:Rising Cyclone (PTP) Frame Data Guide].
- **Inputs:** Use down B on the ground once (for example right after taking a stock).
- **Timing:** The cyclone lasts 79 frames. Being interrupted on frames 1-43 of an aerial
  cyclone keeps the charge; interrupted on frame 44 or later loses it. Rising does not
  itself consume the charge; frame 44 does
  [lib:Rising Cyclone (PTP) Frame Data Guide]. At match start the state is uninitialised
  and depends on stage, opponent character and port [wiki:Luigi_Cyclone].
- **Used for:** Making sure the recovery tool is available. A training mode should expose or
  force this flag.
- **Common errors:** Assuming it is charged after respawn; charging on a platform and
  getting hit.
- **Drill idea:** HUD indicator for the flag; drill fails if the player goes offstage
  uncharged.

### Vududash

- **id:** `vududash`
- **What:** Normally a wavedash that slides off an edge loses its momentum. Starting a
  fireball during the slide preserves it, so Luigi flies off the platform or stage with his
  wavedash speed [wiki:Wavedash].
- **Inputs:** Wavedash toward an edge, neutral B just before reaching it.
- **Timing:** Fireball animation is 46 frames [fd]; Luigi must leave the edge during it.
  Exact window: Unknown.
- **Used for:** Fast movement off platforms, getting offstage facing backward for a bair
  edgeguard, leaving a fireball as an obstacle
  [lib:Smash God's Epic 2000th Post Luigi Guide 2009].
- **Common errors:** Fireball too late (Luigi grabs the ledge or stops at the edge).
- **Drill idea:** Success when Luigi leaves the stage with horizontal speed above a
  threshold while in the fireball animation.

### Double back air

- **id:** `double-bair`
- **What:** Two bairs in one short hop, or bair, waveland, bair, as a moving wall
  [lib:Smash God's Epic 2000th Post Luigi Guide 2009].
- **Inputs:** Short hop backward-facing, bair immediately, bair again, L-cancel.
- **Timing:** Bair hits frames 6-17, 28 frames total, auto-cancels from frame 19, landing lag
  15 or 7 L-cancelled [fd]. Luigi's high, slow short hop is what leaves room for two.
- **Used for:** Zoning (the wiki highlights it against floaties such as Jigglypuff
  [wiki:Luigi_(SSBM)]), shield pressure, pushing opponents offstage, ledge-drop edgeguards.
- **Common errors:** Second bair too late to auto-cancel or L-cancel.
- **Drill idea:** Success when two bair hitboxes come out in one short hop and Luigi lands
  with 7 or fewer frames of lag.

### Up throw chain grab

- **id:** `uthrow-chain-grab`
- **What:** Up throw re-grabs fastfallers at low percent
  ([chain grab](../techniques/chain-grab.md)); the wavedash lets Luigi follow DI
  [wiki:Luigi_(SSBM)].
- **Inputs:** Grab, up throw, wavedash or walk under the opponent, grab again.
- **Timing:** One guide puts the range at "up to like 40ish%" on Fox and Falco, from memory
  [lib:Smash God's Epic 2000th Post Luigi Guide 2009]. Exact windows: Unknown.
- **Used for:** Early damage on Fox, Falco and Captain Falcon before switching to up throw
  down smash or up throw up tilt juggles.
- **Common errors:** Over-sliding past the opponent.
- **Drill idea:** CPU Fox at 0% with random DI; count re-grabs.

## Neutral game

- Move by wavedash; stay just outside the opponent's range, then slide in with down smash,
  forward tilt (frame 4, 10% [fd]) or grab, or slide in with shield up to absorb a hit.
- Forward tilt and shield are named as the two most important ground tools
  [lib:Smash God's Epic 2000th Post Luigi Guide 2009].
- Jab (frame 2 [fd]) to interrupt, then wavedash behind and pivot grab.
- Short hop fair or dair on shield, drift back or follow with nair in the same jump to beat
  shield grabs [lib:Smash God's Epic 2000th Post Luigi Guide 2009].
- Against projectiles: shield, or grounded down B, which clanks with a projectile and ends
  immediately so Luigi can act [lib:Smash God's Epic 2000th Post Luigi Guide 2009].
- Crouch cancel into down smash is his standard answer to weak approaching aerials
  [wiki:Luigi_(SSBM)/Down_smash].
- Dash attack is close to useless: unsafe on hit, no launching hit
  [wiki:Luigi_(SSBM)/Dash_attack]. Do not build drills that reward it.

## Punish game

Luigi's launchers send straight up (down smash, nair, cyclone at 90°; up tilt at 100° [fd]), so
punishes are vertical juggles under the opponent. Against fastfallers these repeat many times
(down smash into down smash, nair into nair); against floaties one launcher leads to one or two
aerials. Finish with fair or dair near the edge, up smash off the top, or Fire Jump Punch.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| Up throw | Fox, Falco, Captain Falcon | low, up to about 40% | Re-grab | Chain grab | [lib:Smash God's Epic 2000th Post Luigi Guide 2009] |
| Up throw | Fox, Falco | low | Turn-around down smash | Starts juggle | [lib:Smash God's Epic 2000th Post Luigi Guide 2009] |
| Up throw | fastfallers | higher | Fair | Kill | [lib:Smash God's Epic 2000th Post Luigi Guide 2009] |
| Up throw | Sheik | 0% | Up smash | She can escape only by jumping immediately | [lib:Smash God's Epic 2000th Post Luigi Guide 2009] |
| Down throw | non-fastfallers | low | Forward tilt (angle up as percent rises) | Opponent pops up behind Luigi | [lib:Smash God's Epic 2000th Post Luigi Guide 2009] |
| Down throw | floaties | roughly 70-80% | Turn, clean nair | | [lib:Smash God's Epic 2000th Post Luigi Guide 2009] |
| Down throw | most | high | Turn-around fair, or bair | Kill near edge | [lib:Smash God's Epic 2000th Post Luigi Guide 2009] |
| Down smash | fastfallers | low | Down smash again, up tilt, nair | Repeats | [wiki:Luigi_(SSBM)] |
| Late nair | most | mid | Fair or dair | "Weak nair, chop" | [lib:Smash God's Epic 2000th Post Luigi Guide 2009] |
| Late nair or jab | most | around 40% | Fire Jump Punch | Must be touching | [wiki:Super_Jump_Punch] |
| Down throw, down smash, nair, jab, up B | Fox, Falco | 0% | 52% total | Example string | [lib:Smash God's Epic 2000th Post Luigi Guide 2009] |
| Grounded cyclone hit 1 | Fox, Falco | low-mid | Cyclone hit 2, then aerial | | [wiki:Luigi_(SSBM)/Down_special] |

### Chain grabs and tech chases

- Up throw chain grab on fastfallers at low percent (see tech entry). Exact windows unknown.
- Down throw bounces the opponent at a low angle behind Luigi and sets up tech chases
  [wiki:Luigi_(SSBM)]; use the wavedash tech chase above.
- Tech chase punishes by priority: Fire Jump Punch if he can be touching the opponent on
  their first vulnerable frame, otherwise down smash (roll away, tech in place) or up tilt
  (roll behind), or a jump-cancel grab on tech in place [lib:20GX: On Luigi].
- On platforms, a tech roll away can be covered with an immediate dair or forward smash
  instead of a wavedash [lib:20GX: On Luigi].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Fire Jump Punch (grounded up B frame 5) | Fox | 92% guaranteed on Dream Land (earlier elsewhere) | Must be touching; unstaled | [wiki:Luigi_(SSBM)/Up_special] |
| Fire Jump Punch | Jigglypuff | under 40% on most stages | Not Dream Land | [wiki:Luigi_(SSBM)/Up_special] |
| Forward smash | most | under 130% | Frames 12-13, knockback growth 135 [fd] | [wiki:Luigi_(SSBM)] |
| Fair / dair (non-meteor hit) | most | roughly 70%+ | Near or past the edge | [lib:Smash God's Epic 2000th Post Luigi Guide 2009] |
| Up smash | floaties, anyone off the top | Unknown | Frames 9-11, head intangible | [wiki:Luigi_(SSBM)] |
| Down smash | Fox | not until 135% on Battlefield | Weak killer | [wiki:Luigi_(SSBM)/Down_smash] |
| Clean nair | floaties | high | Near the top blast line | [wiki:Luigi_(SSBM)] |
| Misfire | Fox | 71% from mid Battlefield | 1 in 8 chance | [wiki:Luigi_(SSBM)/Side_special] |
| Full-charge Green Missile | most | under 150% | Three second charge | [wiki:Green_Missile] |
| Back throw | most | very high | At the edge | [lib:Smash God's Epic 2000th Post Luigi Guide 2009] |
| Dair hip hitbox (meteor) | most | any, offstage | Small hitbox near the hips, 270° [fd] | [wiki:Luigi_(SSBM)] |

- Edgeguards: wavedash to the ledge and drop with bair (covers horizontal and low
  recoveries); run or wavedash off with fair against Fox/Falco up B; dair on recoveries
  coming from below such as DK's; fireball to knock Fox/Falco out of up B startup
  [lib:Smash God's Epic 2000th Post Luigi Guide 2009].
- Down-angled forward tilt and down tilt hit opponents hanging on or sweetspotting the ledge
  [wiki:Luigi_(SSBM)].
- Forward throw at the edge at low percent, then follow with fair or dair before the up B
  [lib:Smash God's Epic 2000th Post Luigi Guide 2009].

## Recovery

- **Options:**
  - Green Missile: horizontal distance, no special fall, repeatable while high; 1 in 8
    misfire.
  - Rising cyclone: height and drift when charged and mashed.
  - Up B: straight up only, intangible frames 5-8; must be directly under the ledge
    [wiki:Luigi_(SSBM)/Up_special].
  - Double jump (high) and air dodge to the ledge; the wiki rates these above up B when they
    reach [wiki:Luigi_(SSBM)/Up_special].
  - Fireball to interrupt an edgeguarder (reflectors punish it) [wiki:Luigi_(SSBM)].
- **Mixups:** Charge length of the missile; several short missiles versus one long; cyclone
  before or after the missile; keep the double jump until last
  [lib:Smash God's Epic 2000th Post Luigi Guide 2009]; missile to a platform edge for an
  edge cancel; DI high to get more time.
- **Weaknesses:** Slow and telegraphed. The missile's end lag makes him drop; taking a hit
  during the missile shortens its distance; the up B can be edgehogged on reaction and the
  sourspot does not protect him [wiki:Luigi_(SSBM)/Up_special]. Up B is also one of the
  worst moves to [meteor cancel](../techniques/meteor-cancel.md) with [wiki:Luigi_(SSBM)].

### Edgeguarding Luigi

- Intercept the missile: stand or jump in its path with a lasting hitbox, or just take the
  hit (5-26% [wiki:Luigi_(SSBM)/Side_special]) to stop him short, then edgehog.
- When he is under the ledge and uses up B, grab the ledge; he has no horizontal movement
  and falls. [Marth](marth.md)'s down tilt also beats it [wiki:Luigi_(SSBM)/Up_special].
- Respect the misfire: do not stand in the missile's line at kill percent without a hitbox
  out or a shield.
- A scripted CPU Luigi is required for edgeguard drills: the vanilla CPU only repeats
  uncharged Green Missiles and never switches to up B once below the stage
  [wiki:Green_Missile].
- Good CPU script: DI up, cyclone (if charged) with random mash quality, missile with random
  charge to ledge height, double jump, up B under the ledge.

## Defense and out of shield

- Out of shield: wavedash out of shield (reposition or wavedash back into forward tilt/down
  smash), nair, shield grab when the opponent is still close, cyclone, and Fire Jump Punch
  when the opponent is directly on top of him (his fastest option, intangible on the frame it
  hits) [wiki:Luigi_(SSBM)/Up_special] [wiki:Luigi_Cyclone].
- Shield pushback is large because of his traction, so many punishes whiff
  [wiki:Luigi_(SSBM)].
- Crouch cancel into down smash at low percent.
- In the air: nair immediately; aerial down B halts upward momentum and drops him straight
  down, a known way to get out from above [DK](donkey-kong.md)'s or Marth's up air strings
  [wiki:Luigi_(SSBM)/Down_special]; up air to challenge things above him.
- Spot dodge then wavedash away [lib:Smash God's Epic 2000th Post Luigi Guide 2009].

## As the training dummy

- Floaty and average weight (weight 100, the baseline for weight-dependent throws
  [wiki:Bowser_(SSBM)/Down_throw]). Vertical kill moves kill him early; horizontal combos on
  him are short.
- Not chain-grabbable by the usual fastfaller chain grabs. [Peach](peach.md)'s down throw
  chain grab does not work (he jumps out) [wiki:Chain_grab]. [Bowser](bowser.md)'s side B
  throw to up air does not work on him at all [wiki:Bowser_(SSBM)/Up_aerial]. DK gets about
  one up air from cargo up throw [lib:Guide to Donkey Kong].
- CPU escape behaviour that matters: nair on the first actionable frame (frame 3 hitbox);
  aerial down B to fall out of juggles; DI away from vertical finishers.
- Ground interactions: he slides far on shield hits and when crouch cancelling, so
  follow-ups that assume the dummy stays in place will whiff.
- DK's down B (Hand Slap) is called out as especially good against Luigi because he
  approaches on the ground [wiki:Donkey_Kong_(SSBM)/Down_special].

## Matchup notes

### vs Marth

- Widely considered a bad matchup: Marth starts and keeps juggles on Luigi easily and
  outranges his aerials [wiki:Luigi_(SSBM)]. Luigi relies on wavedash shield, ground pokes
  and punishing Marth's up B landing lag with Fire Jump Punch.

### vs Fox and Falco

- Luigi's reward is very high: down smash and nair juggles from 0%, up throw chain grab,
  and edgeguards with fair, bair and fireball
  [lib:Smash God's Epic 2000th Post Luigi Guide 2009].
- Their reward is also high: up throw up air and up smash kill a floaty early, and lasers
  force Luigi to approach.

### vs Sheik

- Up throw up smash at 0%; down throw forward tilt and down smash for damage
  [lib:Smash God's Epic 2000th Post Luigi Guide 2009]. Her up B (Vanish) landing lag is the
  textbook Fire Jump Punch punish [wiki:Luigi_(SSBM)/Up_special].

### vs Jigglypuff

- Bair is his zoning tool [wiki:Luigi_(SSBM)]; Fire Jump Punch kills under 40% and punishes
  a missed Rest [wiki:Luigi_(SSBM)/Up_special].

### vs Captain Falcon

- Falcon is named as a character that shuts down Luigi's aerial game
  [lib:Smash God's Epic 2000th Post Luigi Guide 2009]; Luigi fights from the ground and
  punishes with throw into down smash.

### vs Donkey Kong and Ice Climbers-style ground threats

- DK's Hand Slap covers wavedash approaches [wiki:Donkey_Kong_(SSBM)/Down_special]; approach
  with shield or from the air there.

## Drill seeds

### Wavedash down smash approach

- **id:** `luigi-wavedash-dsmash`
- **Goal:** Close distance and hit with the first hit of down smash on the earliest frames.
- **Player:** Luigi
- **CPU:** Fox, Falco, Sheik, Marth
- **Setup:** Final Destination, CPU at 0-30%, standing at a random distance between half and
  one full wavedash away.
- **CPU behaviour:** Stands, dash dances, or throws out a slow poke at random delay.
- **Success:** Down smash front hit connects within 24 frames of the jump input (14 for the
  wavedash, 5 for the smash, 5 slack).
- **Fail:** Whiff, shielded with a punish, or Luigi hit.
- **Variations:** CPU shields (then the correct answer is grab); CPU crouch cancels (check
  both hits connect); retreating wavedash forward tilt instead.
- **Data needed:** Wavedash timing 14 frames [lib:20GX: On Luigi]; down smash frames
  [wiki:Luigi_(SSBM)/Down_smash]; Luigi traction (attributes).

### Reaction tech chase

- **id:** `luigi-tech-chase`
- **Goal:** Cover tech in place, tech toward and tech away from one position.
- **Player:** Luigi
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** CPU knocked down next to Luigi at 40% (for example after a down throw); flat
  stage.
- **CPU behaviour:** Random among tech in place, tech left, tech right, missed tech then
  get-up attack/roll/stand.
- **Success:** Luigi's grab, down smash or up tilt connects no later than 4 frames after the
  CPU's invulnerability ends.
- **Fail:** CPU acts first.
- **Variations:** Require the Gravy method (jump during the tech, then jump-cancel grab or
  wavedash); restrict punish to Fire Jump Punch for bonus; platform version where roll away
  is covered by dair.
- **Data needed:** Tech in place 26 frames and tech roll 40 frames as given in
  [lib:20GX: On Luigi] (verify per character); invulnerability frames of each tech; down
  smash/up tilt knockdown thresholds versus ASDI down.

### Shoryuken punish

- **id:** `luigi-fire-jump-punch`
- **Goal:** Position for the one-frame sweetspot.
- **Player:** Luigi
- **CPU:** Sheik, Marth, Captain Falcon, Ganondorf
- **Setup:** CPU recovering with up B; Luigi holds the ledge so the CPU must land on stage in
  landing lag. CPU at 50-80%.
- **CPU behaviour:** Up B onto the stage at a random landing spot within range.
- **Success:** Up B sweetspot (25% hitbox) connects.
- **Fail:** Sourspot (1%) connects or the CPU shields in time.
- **Variations:** Jab reset setup (CPU lying down after a missed tech: jab, then up B);
  Jigglypuff asleep after a missed Rest; wavedash-in from a distance.
- **Data needed:** Sweetspot frame 5 and its hitbox size [wiki:Luigi_(SSBM)/Up_special];
  landing lag of each CPU up B.

### Nair out of a combo

- **id:** `luigi-nair-escape`
- **Goal:** Recognise and hit the gap in a string.
- **Player:** Luigi
- **CPU:** Marth (up tilt/up air juggles), Fox (up throw up air), Sheik
- **Setup:** Luigi launched above the CPU at 30-60%.
- **CPU behaviour:** Follows with an aerial; the timing is randomly a true combo or 3-8
  frames late.
- **Success:** On late timings, Luigi's nair hits the CPU first. On true timings, Luigi
  survives by DI and does not get hit by a third move.
- **Fail:** Luigi is hit during a gap he could have used.
- **Variations:** Replace nair with aerial down B to drop out; add the option to double
  jump away.
- **Data needed:** Nair frame 3 [fd]; hitstun of the CPU's moves on Luigi (weight 100, low
  gravity).

### Juggle a fastfaller

- **id:** `luigi-vertical-juggle`
- **Goal:** Chain vertical launchers without dropping the opponent.
- **Player:** Luigi
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** CPU grabbed at 0% on Final Destination.
- **CPU behaviour:** Random DI; shines/jumps/techs when actionable.
- **Success:** 50% or more dealt before the CPU acts; bonus for ending with fair offstage or
  Fire Jump Punch.
- **Fail:** CPU escapes before 50%.
- **Variations:** Start from a down smash hit instead of a grab; Battlefield with platform
  techs.
- **Data needed:** Up throw (7%), down smash, up tilt, nair hitbox data [fd]
  [wiki:Luigi_(SSBM)]; victim fall speed and weight.

### Full recovery sequence

- **id:** `luigi-recovery`
- **Goal:** Combine missile, cyclone, double jump and up B, and avoid landing in missile lag.
- **Player:** Luigi
- **CPU:** Marth or Sheik as edgeguarder (or none)
- **Setup:** Luigi launched offstage at 60% from a random point: high and far, level and
  far, or low and close. Cyclone flag charged or uncharged at random and shown on the HUD.
- **CPU behaviour:** Grabs the ledge when Luigi starts up B; otherwise swings at the missile
  path.
- **Success:** Luigi grabs the ledge or lands actionable.
- **Fail:** Luigi dies or lands on stage in missile lag and is hit.
- **Variations:** Force misfire on a given missile; require a rising cyclone of 8 or more
  presses; no double jump.
- **Data needed:** Missile timings [wiki:Luigi_(SSBM)/Side_special]; cyclone press window
  6-43 [lib:Rising Cyclone (PTP) Frame Data Guide]; the cyclone charge flag in memory.

### Rising cyclone mash trainer

- **id:** `luigi-rising-cyclone`
- **Goal:** Build the mash rhythm and learn the frame 6 start.
- **Player:** Luigi
- **CPU:** none
- **Setup:** Luigi airborne above a pit, cyclone charged, repeated automatically.
- **CPU behaviour:** None.
- **Success:** Net height gain (6 or more presses registered between frames 6 and 43).
- **Fail:** Height loss.
- **Variations:** Thresholds at 8, 12, 14 presses; with horizontal drift toward a ledge.
- **Data needed:** [lib:Rising Cyclone (PTP) Frame Data Guide] press rules.

### Edgeguard Fox and Falco

- **id:** `luigi-edgeguard-spacies`
- **Goal:** Choose fair, bair, or fireball against up B and side B recoveries.
- **Player:** Luigi
- **CPU:** Fox, Falco
- **Setup:** CPU offstage at 50% with no double jump; Luigi at center stage.
- **CPU behaviour:** Random: up B from below, up B level with the stage, side B to ledge,
  side B onto stage.
- **Success:** CPU loses the stock.
- **Fail:** CPU returns to the stage or ledge.
- **Variations:** Luigi starts on the ledge (ledge-drop bair); require a Vududash to get
  offstage.
- **Data needed:** Fair frames 7-10 and bair frames 6-17 [fd]; Fox/Falco up B startup and
  side B timings.

### Wavedash out of shield

- **id:** `luigi-wavedash-oos`
- **Goal:** Turn shield pushback into a punish instead of losing the punish.
- **Player:** Luigi
- **CPU:** Marth, Sheik, Peach
- **Setup:** Luigi shielding; CPU hits the shield with a spaced, laggy move (for example
  Marth forward smash).
- **CPU behaviour:** Attack at random spacing; shields afterward if Luigi is slow.
- **Success:** Luigi wavedashes out of shield toward the CPU and lands down smash, grab or
  forward tilt during the CPU's lag.
- **Fail:** Shield grab whiff, or late punish that is shielded.
- **Variations:** Close spacing where Fire Jump Punch out of shield is correct.
- **Data needed:** Shield stun and pushback versus Luigi's traction; CPU move end lag.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlLg.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/luigi.json`](../framedata/luigi.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 2-3 | 3 | 83/85 | 0 | 100 | 20 |  | 15 | - | 3 | -10 |  |
| Jab 2 | `jab2` | 3-4 | 2 | 83/85 | 0 | 100 | 20 |  | 18 | - | 2 | -13 | starts 1 frame late (included) |
| Jab 3 | `jab3` | 5-6 | 5 | Sakurai | 10 | 100 | - |  | 30 | 23 | 4 | -13 | starts 1 frame late (included) |
| Dash attack | `dash_attack` | 4, 10, 16, 22, 29, 37 | 2 | Sakurai | 2 | 100 | - |  | 63 | 59 | 2 | -52 |  |
| Forward tilt (angled up) | `ftilt_high` | 4-8 | 10 | Sakurai | 2 | 100 | - |  | 32 | 32 | 6 | -21 |  |
| Forward tilt | `ftilt` | 4-8 | 10 | Sakurai | 2 | 100 | - |  | 32 | 32 | 6 | -21 |  |
| Forward tilt (angled down) | `ftilt_low` | 4-8 | 10 | Sakurai | 2 | 100 | 1 |  | 32 | 32 | 6 | -21 |  |
| Up tilt | `utilt` | 4-12 | 9 | 100 | 30 | 127/125/123 | - |  | 29 | - | 6 | -19 |  |
| Down tilt | `dtilt` | 5-8 | 9 | 80 | 10 | 80 | - |  | 34 | - | 6 | -23 |  |
| Forward smash (angled up) | `fsmash_high` | 12-13 | 14 | 65 | 20 | 135 | - | slash | 41 | - | 8 | -21 | charge hold frame 5 |
| Forward smash | `fsmash` | 12-13 | 13 | 55 | 20 | 135 | - | slash | 41 | - | 7 | -22 | charge hold frame 5 |
| Forward smash (angled down) | `fsmash_low` | 12-13 | 12 | 45 | 20 | 135 | - | slash | 41 | - | 7 | -22 | charge hold frame 5 |
| Up smash | `usmash` | 9-11 | 17 | 110 | 35 | 98 | - |  | 39 | - | 9 | -21 | charge hold frame 7; partly intangible 9-11 (1 bone) |
| Down smash | `dsmash` | 5-6, 14-15 | 17 | 90 | 40 | 80 | - |  | 37 | - | 9 | -23 | charge hold frame 3 |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 3-6 | 15 | 90 | 20 | 100 | - |  | 45 | - | 8 | 15 | 7 | <3, >35 | +1 |  |
|  |  | 7-31 | 8 | 90 | 20 | 100 | - |  |  |  | 5 |  |  |  | -2 |  |
| Forward air | `fair` | 7-10 | 12 | Sakurai | 43 | 100 | - |  | 34 | 33 | 7 | 25 | 12 | <2, >19 | -5 |  |
| Back air | `bair` | 6-17 | 11 | Sakurai | 12 | 100 | - |  | 28 | - | 6 | 15 | 7 | <6, >18 | -1 |  |
| Up air | `uair` | 5-7 | 13 | 55 | 0 | 100 | - |  | 33 | 30 | 7 | 15 | 7 | <2, >15 | +0 |  |
| Down air | `dair` | 10-14 | 16 | Sakurai/270 | 20 | 100 | - |  | 32 | 29 | 9 | 18 | 9 | <6, >23 | +0 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 11-12 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 17 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 8 | 8 | 45 | 60 | 65 | - | - | 12 | 27 |  |
| Back throw | `bthrow` | 10 | 10 | 45 | 80 | 65 | - | - | 44 | 66 |  |
| Up throw | `uthrow` | 7 | 7 | 100 | 70 | 72 | - | - | 18 | 39 |  |
| Down throw | `dthrow` | 7 | 7 | 110 | 75 | 30 | - | - | 18 | 39 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Fireball, ground | `special_n` | - | - | - | - | - | - | - | 46 | - | - | - | spawns article/projectile on 17 |
| Neutral B: Fireball, air | `special_air_n` | - | - | - | - | - | - | - | 46 | - | - | - | spawns article/projectile on 17 |
| Side B: Green Missile, ground, Start | `special_s_start` | - | - | - | - | - | - | - | 17 | - | - | - |  |
| Side B: Green Missile, ground, Hold | `special_s_hold` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Side B: Green Missile, ground | `special_s` | 4-43 | 10 | Sakurai | 20 | 80 | - | fire | 43 | - | 6 | - |  |
| Side B: Green Missile, ground | `special_s_300` | 4-43 | 25 | Sakurai | 20 | 100 | - | fire | 43 | - | 13 | - |  |
| Side B: Green Missile, ground | `special_s_301` | - | - | - | - | - | - | - | 43 | - | - | - |  |
| Side B: Green Missile, ground, End | `special_s_end` | - | - | - | - | - | - | - | 40 | - | - | - |  |
| Side B: Green Missile, air, Start | `special_air_s_start` | - | - | - | - | - | - | - | 17 | - | - | - |  |
| Side B: Green Missile, air, Hold | `special_air_s_hold` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Side B: Green Missile, ground | `special_s_305` | 4-43 | 10 | Sakurai | 20 | 80 | - | fire | 43 | - | 6 | - |  |
| Side B: Green Missile, ground | `special_s_306` | 4-43 | 25 | Sakurai | 20 | 100 | - | fire | 43 | - | 13 | - |  |
| Side B: Green Missile, air, End | `special_air_s_end` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Up B: Super Jump Punch, ground | `special_hi` | 5 | 25 | 90 | 70 | 73 | - | fire | 39 | - | 13 | - | intangible 5-8 |
|  |  | 6-23 | 1 | 80 | 1 | 1 | - | coin |  |  | 2 | - |  |
| Up B: Super Jump Punch, air | `special_air_hi` | 5 | 20 | 90 | 58 | 72 | - | fire | 39 | - | 10 | - | intangible 5-8 |
|  |  | 6-23 | 1 | 80 | 1 | 1 | - | coin |  |  | 2 | - |  |
| Down B: Luigi Cyclone, ground | `special_lw` | 6-29 | 8 | 90 | 50 | 80 | - |  | 79 | - | 5 | - |  |
|  |  | 43 | 12 | 90 | 50 | 80 | - |  |  |  | 7 | - |  |
| Down B: Luigi Cyclone, air | `special_air_lw` | 6-29 | 9 | 90 | 50 | 80 | - |  | 79 | - | 6 | - |  |
|  |  | 43 | 12 | 90 | 50 | 80 | - |  |  |  | 7 | - |  |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-15 | - | 22 | 20 |  |
| Roll forward | `roll_forward` | intangible 4-19 | - | 31 | - |  |
| Roll backward | `roll_backward` | intangible 4-19 | - | 31 | - |  |
| Air dodge | `airdodge` | intangible 4-29 | - | 48 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-25 | 20-21, 24-25 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-21 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-22 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-26 | 19-20, 25-26 (6%) | 49 | - |  |
| Getup roll forward (face down) | `getup_roll_forward_facedown` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-24 | - | 35 | - |  |
| Tech in place | `tech_in_place` | intangible 2-20 | - | 26 | - | starts 1 frame late (included) |
| Tech roll forward | `tech_roll_forward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Tech roll backward | `tech_roll_backward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Wall tech | `wall_tech` | - | - | 26 | - | starts 1 frame late (included) |
| Wall tech jump | `wall_tech_jump` | - | - | 40 | - | starts 1 frame late (included) |
| Ceiling tech | `ceiling_tech` | intangible 2-17 | - | 26 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-55 | - | 59 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 34 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-36 | 40-44 (10%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-20 | 24-36 (8/6%) | 55 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-56 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-27 | - | 49 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-19 | - | 19 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 29 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-15 | - | 15 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 23 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Up B | jump cancel | 6 | `special_hi` |
| Neutral air | jump | 7 | `nair` |
| Shield grab | direct | 7 | `grab` |
| Up air | jump | 9 | `uair` |
| Back air | jump | 10 | `bair` |
| Up smash | jump cancel | 10 | `usmash` |
| Down B (aerial) | jump | 10 | `special_air_lw` |
| Forward air | jump | 11 | `fair` |
| Down air | jump | 14 | `dair` |
| Spot dodge | direct | intangible 2-15 of 22 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 16 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Luigi indexed by [The Melee Library](https://www.meleelibrary.com/#luigi) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [Are You A Luigi Player?](https://www.youtube.com/watch?v=hXzI1QMr-UU) | SSBM Tutorials | They give an overview of Luigi the character to give you an idea of whether you would like to play him. |
| [2020 Luigi Melee Techs Guide](https://www.youtube.com/watch?v=K0E0QdueNcA&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=16&t=0s) | Third Chair | Video guide on performing useful Luigi tech in 2020. |
| [20GX: On Luigi](http://www.reddit.com/r/SSBM/comments/334b0r/20gx_on_luigi/) | Gravy | Gravy weighs in on 20XX techchasing with Luigi. [Here](http://smashboards.com/threads/20gx-on-luigi-techchase.399700/) is a Smashboards thread with the same content, but with discussion by real Luigi players. |
| [Advance, Attack, Avoid (Through the lens of Luigi)](http://smashboards.com/threads/advance-attack-avoid-through-the-lens-of-luigi.389684/) | BluEG | An analysis of gameplay in neutral based on Rock, Paper, Scissors. |
| [Luigi Hitboxes and Frame Data](http://smashboards.com/threads/luigi-hitboxes-and-frame-data.306546/) | Stratocaster, Standardtoaster, and SuperDoodleMan |  |
| [The Official Luigi Matchup Database!](http://smashboards.com/threads/the-official-luigi-matchup-database-currently-discussing-various.283735/) | SmashGod | A collection of matchup guides and discussions about matchups. 2010-2014 |
| [Smash God's Epic 2000th Post Luigi Guide 2009](http://smashboards.com/threads/smash-gods-epic-2000th-post-luigi-guide-updated-jan-16-13-with-more-to-come.228500/) | SmashGod | An introduction to Luigi for beginners. |
| [The Official Tornado (B-Down), Down-Air and Taunt Thread](http://smashboards.com/threads/the-official-tornado-b-down-down-air-and-taunt-thread.64648/) | Duke | People keep asking questions about these moves and misfire, so they made a thread with clarifying information. |
| [ROFL Tells You How to Beat Marth](http://smashboards.com/threads/rofl-tells-you-how-to-beat-marth.91241/) | ROFL |  |
| [Luigi FAQ](http://smashboards.com/threads/tobias-xelkythes-luigi-faq.75787/) | Tobias | A really old (2006), but in depth, guide about Luigi. Good for beginners. |
| [Rising Cyclone (PTP) Frame Data Guide](http://smashboards.com/threads/rising-cyclone-ptp-frame-data-guide.384946/) | Schmooblidon | How best to mash to get the most distance from the tornado. |
| [No Impact Land with Luigi](http://smashboards.com/threads/new-tech.308463/) | by Weslo | Good discussion in the comments too. |
| [Everywhere at Once](http://freepdfhosting.com/33299f9128.pdf) | BluEG | Utilizing Luigi’s unique movement. |
| [Luigi Neutral Game Tutorial](https://www.youtube.com/watch?v=1db7pFfSGKM) | SSBM Tutorials and Ka-Master |  |
| [Luigi Trials](https://www.youtube.com/watch?v=Rzh-wwsoI6A) | Hulk A | A series of challenges for Luigi inspired by Street Fighter's trials system. |
| [Down B Starting Charged](http://smashboards.com/threads/luigis-down-b-starting-charged.292168/#post-12768689) | community | Luigi starts with his down-b charged on certain stages against certain characters. |
| [How to Edgeguard Luigi](https://www.youtube.com/watch?v=VOfE_R6qNys) | Remix |  |
| [Momentum Canceling](http://smashboards.com/guides/momentum-canceling.907/) | F-ric | Control your momentum out of wavedashes better using dashes and pivots. |
| [Luigi 100% Invincible Ledge Stalling](https://www.youtube.com/watch?v=Mf184bmDY7w) | Luigi TAS | A video showing Luigi's ability to haxdash invincibly. |
| [Luigi Melee Chaingrab Guide](https://www.youtube.com/watch?v=72I3ZHLh6Lg&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=14&t=0s) | Third Chair |  |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Luigi (SSBM): https://www.ssbwiki.com/Luigi_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Luigi_(SSBM)/Up_special , /Side_special ,
  /Down_special , /Down_smash , /Neutral_aerial , /Forward_smash , /Dash_attack ,
  /Down_aerial
- SSBWiki, Green Missile: https://www.ssbwiki.com/Green_Missile
- SSBWiki, Luigi Cyclone: https://www.ssbwiki.com/Luigi_Cyclone
- SSBWiki, Super Jump Punch: https://www.ssbwiki.com/Super_Jump_Punch
- SSBWiki, Fireball: https://www.ssbwiki.com/Fireball
- SSBWiki, Wavedash (including Vududash): https://www.ssbwiki.com/Wavedash
- SSBWiki, Chain grab: https://www.ssbwiki.com/Chain_grab
- SSBWiki, Donkey Kong (SSBM)/Down special: https://www.ssbwiki.com/Donkey_Kong_(SSBM)/Down_special
- SSBWiki, Bowser (SSBM)/Up aerial and /Down throw
- SSBWiki, List of SSBM tier lists (NTSC): https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Gravy, "20GX: On Luigi" (via web.archive.org):
  http://www.reddit.com/r/SSBM/comments/334b0r/20gx_on_luigi/
- SmashGod, "Smash God's Epic 2000th Post Luigi Guide" (via web.archive.org):
  http://smashboards.com/threads/smash-gods-epic-2000th-post-luigi-guide-updated-jan-16-13-with-more-to-come.228500/
- Schmooblidon, "Rising Cyclone (PTP) Frame Data Guide" (via web.archive.org):
  http://smashboards.com/threads/rising-cyclone-ptp-frame-data-guide.384946/
- NJzFinest, "Guide to Donkey Kong" (for DK versus floaties, via web.archive.org):
  https://smashboards.com/threads/guide-to-donkey-kong-2014-update-in-progress.294993/
- Frame data dump: `Luigi.json`
