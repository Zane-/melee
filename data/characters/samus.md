---
schema: melee-character/v1
id: samus
name: Samus
aliases: [Samus Aran]
tier: "B+ (11th of 26), 2021 list"
archetype: [zoner, projectile, floaty, heavy, edgeguarder, technical]
related: []
summary: Samus wins by walling opponents out with missiles and long pokes, punishing approaches with crouch cancel down smash and up B out of shield, and outlasting them with a heavy body and a recovery that is very hard to edgeguard.
key_tech: [missiles, missile-cancel, super-wavedash, extended-grapple, bomb-jump, wall-grapple, up-b-out-of-shield, crouch-cancel-dsmash, dthrow-followups, bomb-shield-pressure, aerial-interrupt]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlSs.dat
framedata: ../framedata/samus.json
code: src/melee/ft/kinds/ftSamus
specials:
  neutral_b: "Charge Shot"
  side_b: "Missile"
  up_b: "Screw Attack"
  down_b: "Bomb"
attributes:
  weight: 110
  gravity: 0.066
  fall_speed: 1.4
  fast_fall_speed: 2.3
  jump_squat: 3
  jumps: 2
  walk_speed: 1
  dash_speed: 1.86
  run_speed: 1.4
  traction: 0.06
  air_speed: 0.89
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [3, 18, 3]
  jab2: [5, 31, 7]
  dash_attack: [7, 38, 13]
  ftilt_high: [6, 30, 11]
  ftilt_mid_high: [6, 30, 10]
  ftilt: [6, 30, 10]
  ftilt_mid_low: [6, 30, 10]
  ftilt_low: [6, 30, 9]
  utilt: [14, 35, 13]
  dtilt: [6, 40, 14]
  fsmash_high: [10, 44, 15]
  fsmash_mid_high: [10, 44, 14]
  fsmash: [10, 44, 14]
  fsmash_mid_low: [10, 44, 14]
  fsmash_low: [10, 44, 13]
  usmash: [12, 58, 6]
  dsmash: [6, 45, 16]
  nair: [5, 40, 14]
  fair: [6, 50, 5]
  bair: [9, 37, 14]
  uair: [5, 39, 4]
  dair: [18, 49, 16]
  grab: [18, 95, 0]
  dash_grab: [18, 75, 0]
  pummel: [10, 25, 3]
  fthrow: [null, 42, 9]
  bthrow: [null, 42, 8]
  uthrow: [13, 42, 7]
  dthrow: [null, 42, 6]
  special_lw: [null, 54, 0]
  special_air_lw: [null, 54, 0]
  special_n_start: [null, 14, 0]
  special_n_hold: [null, 10, 0]
  special_n_cancel: [null, 8, 0]
  special_n: [null, 30, 0]
  special_air_n_start: [null, 14, 0]
  special_air_n: [null, 30, 0]
  special_s: [null, 60, 0]
  special: [null, 50, 0]
  special_air_s: [null, 60, 0]
  special_air: [null, 50, 0]
  special_hi: [4, 50, 2]
  special_air_hi: [4, 48, 1]
  special_lw_309: [null, 54, 0]
  special_air_lw_310: [null, 54, 0]
oos:  # option: frame the hitbox is out
  special_hi: 5
  nair: 8
  uair: 8
  fair: 9
  bair: 12
  usmash: 13
  grab: 18
  dair: 21
resources: 21
# generated: end
---

# Samus

<!-- GENERATED:attributes -->
## Attributes

Read from `PlSs.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 110 |
| Gravity | 0.066 |
| Terminal fall speed | 1.4 |
| Fast-fall speed | 2.3 |
| Jump squat (frames before airborne) | 3 |
| Full hop / short hop initial Y speed | 2.1 / 1.7 |
| Air jump Y multiplier | 0.9 |
| Jumps | 2 |
| Walk max speed | 1 |
| Dash initial speed / run max speed | 1.86 / 1.4 |
| Ground friction (traction) | 0.06 |
| Air max horizontal speed | 0.89 |
| Air acceleration (base + stick) | 0.02 + 0.0125 |
| Air friction | 0.01 |
| Normal landing lag | 4 |
| Shield size | 16.25 |
<!-- /GENERATED:attributes -->

## Overview

Samus is a tall, heavy character who falls very slowly: only [Bowser](bowser.md) and
[Donkey Kong](donkey-kong.md) weigh more, and her fall speed is the second slowest in the
game, tied with [Zelda](zelda.md) [wiki:Samus_(SSBM)]. She plays a defensive, spacing
game. Side B (Missile) and neutral B (Charge Shot) control the ground, long tilts and a
frame-10 fsmash stop dashes, and anything that touches her at low or mid percent can be
[crouch cancelled](../techniques/crouch-cancel.md) into dsmash or dtilt. Her punish game
is weaker than the top tiers' because her floatiness and high short hop make it hard to
follow fastfallers, and her grab, though the longest in the game, is slow and very
punishable on whiff [wiki:Samus_(SSBM)]. She survives horizontal hits to very high
percent and recovers with bombs, a wall grapple, wall jumps and up B (Screw Attack). She
loses stocks off the top (slow fall) and to long juggles. Execution of her basics is
moderate; her advanced techniques (super wavedash, extended grapple) are hard.

## Strengths and weaknesses

- **Strengths:**
  - Two projectiles: slow homing missiles, fast Super Missiles, and a storable Charge Shot
    that kills [wiki:Samus_(SSBM)].
  - One of the best crouch cancels in the game, with dsmash (frame 6) and dtilt (frame 6)
    as punishes [wiki:Samus_(SSBM)] [fd].
  - Up B out of shield: intangible from frame 1, hits on frame 4
    [wiki:Samus_(SSBM)/Up_special].
  - Recovery with more options than any other character [wiki:Samus_(SSBM)].
  - Very high horizontal survivability.
  - Long reach: ftilt, fsmash, nair and bair with long legs, longest grab
    [wiki:Samus_(SSBM)].
  - Strong edgeguarding with nair, bair, dair and dsmash [wiki:Samus_(SSBM)].
- **Weaknesses:**
  - Poor [SHFFL](../techniques/shffl.md): highest short hop in the game (22.75 units
    [wiki:Jump]) and slow fall speed, so aerial approaches are reactable
    [wiki:Samus_(SSBM)].
  - Grab is active from frame 18 and lasts 94 frames in total when standing
    [wiki:Samus_(SSBM)/Grab].
  - Dies early off the top for her weight; easy to juggle [wiki:Samus_(SSBM)].
  - Shield leaves her legs exposed; slow roll [wiki:Samus_(SSBM)].
  - Struggles to combo fastfallers [wiki:Samus_(SSBM)].

## Character tech

### Missiles

- **id:** `missiles`
- **What:** Side B fires a homing missile when the stick is tilted and a Super Missile
  when it is smashed. Homing missiles are slow, track a little and do 5%; Super Missiles
  fly straight and fast and do more damage with real knockback.
- **Inputs:** Tilt side + B for homing; smash side + B for Super. In the air the same
  inputs apply. Common pattern: full hop or double jump, fire, drift back, land, fire
  again.
- **Timing:** Grounded: missile appears on frame 22 for both types; the animation is 59
  frames for homing and 49 for Super. In the air the homing missile appears on frame 24
  and the Super Missile on frame 15 [wiki:Samus_(SSBM)/Side_special]. Super Missile
  damage is listed as 12% on the character page and 10% on the Missile page
  [wiki:Samus_(SSBM)] [wiki:Missile]; treat the exact value as unconfirmed. A missile is
  destroyed by any hit of 4% or more [wiki:Missile]. A powershield in its first 2 frames
  reflects projectiles [wiki:Perfect_shield].
- **Used for:** Forcing approaches, covering her own approach (walk behind a homing
  missile), edgeguarding, and killing with Super Missiles at high percent
  [wiki:Missile].
- **Common errors:** Firing at close range (49-59 frames of commitment); predictable
  rhythm that gets powershielded or jumped over.
- **Drill idea:** CPU approaches from full stage; player must land M missiles and never
  be hit during a missile animation.

### Missile cancel

- **id:** `missile-cancel`
- **What:** Firing a missile in the air shortly before landing so that landing cuts off
  the rest of the firing animation, letting Samus shoot and act much sooner than on the
  ground.
- **Inputs:** Short hop (or fall), side B late enough that the missile comes out before
  landing, land. Repeat.
- **Timing:** The missile must have left the cannon before Samus lands: aerial Super
  Missile frame 15, aerial homing missile frame 24 [wiki:Samus_(SSBM)/Side_special].
  Landing lag after the cancel: Unknown (commonly described as the normal 4-frame landing
  [unverified]). The wiki mentions "missile cancelling" as the way Samus creates an
  "obstacle course" of missiles [wiki:Missile].
- **Used for:** Higher missile rate; mixing homing and Super Missiles at different
  heights (ESAM's "Battlefield Missiles" video is linked in the Melee Library
  [lib:ESAM's Battlefield Missiles]; not watchable).
- **Common errors:** Landing before the missile spawns (no missile, wasted jump); firing
  too early and floating in the full animation.
- **Drill idea:** Count missiles fired per 10 seconds from short hops; target is a rate
  that grounded firing cannot reach.

### Super wavedash

- **id:** `super-wavedash`
- **What:** A frame-perfect exploit of down B (Bomb, which puts Samus in Morph Ball) that
  sends her sliding roughly the length of Final Destination [wiki:Super_wavedash].
- **Inputs:** Down B on the ground. As Samus lands from the bomb's small hop, press the
  control stick fully in the direction opposite to travel for exactly one frame, then
  fully in the travel direction on the next frame, then release the stick to keep the
  full distance.
- **Timing:** From a standing bomb: opposite direction on frame 41, desired direction on
  frame 42. From a crouching bomb the animation skips its first 2 frames, so the inputs
  are frames 39 and 40 [wiki:Super_wavedash]. It is the last frame of a wider "daughter
  dash" window (left on one frame, right on the next while the Morph Ball touches the
  ground); earlier frames in the window give a shorter boost [wiki:Super_wavedash].
  Jumping, spot dodging, Charge Shot and smash attacks can be done out of the slide
  without stopping it; other moves stop it [wiki:Super_wavedash].
- **Used for:** Surprise approach into fsmash or dsmash, crossing the stage, escaping the
  corner. Variants: "boost ball" (keeping the speed in the air off a platform) and a
  TAS-only "super duper wavedash" [wiki:Super_wavedash].
- **Common errors:** Stick reversal one frame early or late (short slide or none);
  holding the stick afterwards (shorter distance); sliding off the stage.
- **Drill idea:** Player lays a bomb at a marker; success if Samus's horizontal speed on
  frame 43 exceeds a threshold, with a readout of which frame the reversal landed on.

### Extended grapple

- **id:** `extended-grapple`
- **What:** An NTSC-only input code that makes the Grapple Beam grab about 3 times longer
  for the rest of the stock [wiki:Extended_Grapple].
- **Inputs:** Press Z to grab, then D-pad Up, D-pad Down, D-pad Up, then Z or A. With the
  extender active, press L as the beam comes out to make it home in, and press A or Z
  when the tip is over the opponent to complete the grab [wiki:Extended_Grapple].
- **Timing:** The code must be entered during frames 8-39 of the grab animation, before
  the beam is visible. Only the tip of the extended beam grabs and it cannot grab
  airborne opponents. The effect lasts until Samus loses a stock
  [wiki:Extended_Grapple].
- **Used for:** Long-range grabs into dthrow follow-ups, and platform tech chases
  (buffering dthrow with the C-stick after an extender grab on a platform [lib:NEW
  EXTENDER TECH?!]).
- **Common errors:** Finishing the code after frame 39; forgetting the confirm press so
  the beam passes through the opponent; whiffing, which leaves Samus in a very long
  animation.
- **Drill idea:** Stationary CPU at 2-3 normal grab lengths; success if the grab connects.
  A first stage only checks that the code was entered inside frames 8-39.

### Bomb jump

- **id:** `bomb-jump`
- **What:** Using down B repeatedly in the air. Each bomb slows her fall, and a second
  bomb placed on the first pops Samus upward, so she can travel almost unlimited
  horizontal distance without spending her double jump [wiki:Bomb_(Samus)]
  [wiki:Bomb_recovery].
- **Inputs:** In the air: down B, drift, down B again as the first bomb explodes under
  her, repeat while holding toward the stage.
- **Timing:** The bomb exists from frame 10 and explodes at frames 83-99 if untouched;
  the Morph Ball animation is 53 frames and has partial intangibility on frames 10-42
  [wiki:Samus_(SSBM)/Down_special]. Bombs do 4% [wiki:Samus_(SSBM)].
- **Used for:** Recovery from far away, stalling to change the timing of a recovery,
  baiting an edgeguarder off stage.
- **Common errors:** Losing height by bombing too slowly; being hit out of the Morph Ball
  between intangible windows; drifting into the edgeguarder.
- **Drill idea:** Samus starts far off stage below ledge height with no double jump;
  success if she reaches the ledge using bombs, grapple and up B.

### Wall grapple

- **id:** `wall-grapple`
- **What:** The aerial Grapple Beam (zair) attaches to any wall, not just the ledge, and
  Samus can then climb up.
- **Inputs:** Facing the wall, press Z in the air (or L/R + A, which also allows an
  upward air dodge first). Press A to reel in and rise.
- **Timing:** Zair's hitbox is active frames 10-28 and does 4%
  [wiki:Samus_(SSBM)/Grab_aerial] [wiki:Samus_(SSBM)]. Only one wall grapple is allowed
  until Samus touches the ground. Too close or too far and it misses, leaving her
  helpless. Hanging too long drops her in tumble and removes her double jump if unused
  [wiki:Wall_grapple].
- **Used for:** Recovering low under the stage out of reach; a second chance after an
  accidental air dodge.
- **Common errors:** Grappling while facing away; missing the range and falling helpless.
- **Drill idea:** Samus below the ledge at varying distance from the wall; success if the
  grapple attaches and she reaches the ledge or stage.

### Up B out of shield

- **id:** `up-b-out-of-shield`
- **What:** Screw Attack straight from shield. It is intangible on its first frames and
  hits very early, so it beats most shield pressure that is not perfectly spaced.
- **Inputs:** While in shield after shieldstun: press up on the stick and B together (the
  up input starts a jump, B cancels the jump squat into up B). See
  [out-of-shield](../techniques/out-of-shield.md).
- **Timing:** Grounded Screw Attack: intangible frames 1-5, first hit frames 4-5, last
  hit frames 28-29; landing lag afterwards 24 frames [wiki:Samus_(SSBM)/Up_special]. The
  first grounded hit does 2% with base knockback 130 [fd]. Opponents can
  [SDI](../techniques/sdi.md) out of the multi-hit and punish her fall
  [wiki:Samus_(SSBM)].
- **Used for:** Punishing unsafe aerials and close grabs attempts on her shield; a combo
  breaker in the air (aerial version is intangible frames 1-3
  [wiki:Samus_(SSBM)/Up_special]).
- **Common errors:** Using it against a spaced move and whiffing (she is helpless and
  falls slowly); losing a stored Charge Shot if hit during the move [wiki:Samus_(SSBM)].
- **Drill idea:** CPU pressures shield with an aerial then a follow-up; success if up B
  hits the CPU before the follow-up lands.

### Crouch cancel down smash

- **id:** `crouch-cancel-dsmash`
- **What:** Hold down to reduce the knockback of an incoming hit, stay grounded, and
  answer immediately with dsmash (or dtilt).
- **Inputs:** Hold down before the hit; after hitlag, C-stick down (dsmash) or tilt down
  + A (dtilt).
- **Timing:** Dsmash front hit frames 6-8 (16%, angle 120, base knockback 110, growth
  50), back hit frames 14-16 (15%), interruptible from frame 45 [fd]
  [wiki:Samus_(SSBM)/Down_smash]. Because the angle is 120, an opponent in front is
  launched behind Samus at a low trajectory, often off stage if she has her back to the
  edge [wiki:Samus_(SSBM)/Down_smash]. Dtilt hits frames 6-8 for 14% (angle 100, base 80,
  growth 60) [fd]. The percent at which specific moves stop being crouch cancellable:
  Unknown from sources read.
- **Used for:** Beating nair, dash attack and weak aerial approaches from
  [Fox](fox.md), [Sheik](sheik.md), [Captain Falcon](captain-falcon.md) and others.
- **Common errors:** Crouch cancelling a grab or a move that meteors or launches
  regardless; crouching at too high a percent and being knocked down.
- **Drill idea:** CPU approaches with a crouch-cancellable aerial at random timing;
  success if Samus takes the hit crouching and dsmash connects within N frames.

### Down throw follow-ups

- **id:** `dthrow-followups`
- **What:** Dthrow has very low knockback scaling, so the opponent stays close at any
  percent and Samus gets a follow-up or a tech chase.
- **Inputs:** Grab, dthrow, then utilt, dash attack, Charge Shot, or a jab reset if they
  miss the tech.
- **Timing:** Dthrow is 6%, angle 80, base knockback 80, growth 20
  [wiki:Samus_(SSBM)/Down_throw]. The wiki lists jab reset, utilt, dash attack and Charge
  Shot as follow-ups "at virtually any percentage"; Charge Shot does not work on
  [Young Link](young-link.md) [wiki:Samus_(SSBM)].
- **Used for:** Low-percent combos and high-percent kill setups (dthrow to Charge Shot).
- **Common errors:** Missing the grab (94-frame animation); choosing a follow-up that the
  opponent's DI (directional influence) avoids.
- **Drill idea:** CPU in grab at a set percent with random DI and tech; success if a
  listed follow-up connects.

### Bomb shield pressure

- **id:** `bomb-shield-pressure`
- **What:** Dropping bombs onto a shield: the bomb explodes on contact and bounces Samus
  up, from where she can bomb again, air dodge down ("wavebomb"), or attack.
- **Inputs:** Short hop or run up, down B touching the shield; then another down B, an
  aerial, or an air dodge toward the ground.
- **Timing:** If Samus uses Bomb while touching an opponent, the bomb hits them or their
  shield and she is popped up [wiki:Bomb_(Samus)]. Frame advantage: Unknown. The Melee
  Library links Goomy's write-up arguing multi-bomb pressure is very strong [lib:Bomb
  Shield Pressure] and a video [lib:Bomb Pressure and Bomb Combos]; neither could be
  read.
- **Used for:** One of her few ways to pressure a shield without a risky grab.
- **Common errors:** Being hit out of Morph Ball by up B or usmash out of shield.
- **Drill idea:** CPU shields then picks an out-of-shield option after the first bomb;
  success if Samus lands 2 bombs on shield and is not hit.

### Aerial interrupt

- **id:** `aerial-interrupt`
- **What:** Starting an aerial (usually uair) just before reaching the ground or a
  platform so that Samus lands earlier than her normal jump arc would allow, with almost
  no lag.
- **Inputs:** Jump from the ledge or under a side platform, uair at the right height.
- **Timing:** Uair auto-cancels on frames 1-4 [wiki:Samus_(SSBM)/Up_aerial], which is the
  window used. The wiki says this gives grounded, actionable intangibility from the
  ledge, and the Melee Library notes an aerial interrupt from the ledge gives her more
  intangibility than a [ledgedash](../techniques/ledgedash.md) [lib:Samus's Invincible
  Ledgedash Options].
- **Used for:** Getting from ledge to stage safely; fast platform movement.
- **Common errors:** Uair too late (lands in 15 frames of lag, or 7 if L-cancelled [fd]);
  too early (the full aerial comes out).
- **Drill idea:** From the ledge: success if Samus is grounded and actionable on stage
  with intangibility frames remaining.

## Neutral game

- Missiles first. Homing missiles are slow enough to walk behind; Super Missiles punish
  jumps and landings.
- Ftilt hits frames 6-8 and is the standard poke; it is -16 on shield but usually safe at
  max range [wiki:Samus_(SSBM)/Forward_tilt] [fd]. Fsmash hits frames 10-13 [fd].
- Dtilt and dsmash as crouch cancel punishes; dash attack (clean hit frames 7-9, 13%
  [fd]) as a burst option that also combos at low percent [wiki:Samus_(SSBM)].
- [Wavedash](../techniques/wavedash.md) back into ftilt, fsmash or dsmash; her wavedash
  is long [wiki:Samus_(SSBM)].
- Nair (clean frames 5-8, 14%) is the air-to-air and out-of-shield aerial; dair (frames
  18-22, 16%, meteor) is a slow but rewarding opener that is at best +2 on shield
  [wiki:Samus_(SSBM)/Down_aerial].
- Grab only as a hard read or with the extender; the standing grab has 94 total frames
  [wiki:Samus_(SSBM)/Grab]. The dash grab is active from the same frame and is 20 frames
  shorter overall [wiki:Samus_(SSBM)].
- Charge Shot: charge when the opponent is far away, store it with L/R, and use it as a
  threat or a punish [wiki:Samus_(SSBM)].

## Punish game

Samus's combos are short. Typical flow: a launcher (utilt on a grounded opponent, dair,
dthrow, dash attack) into one or two hits (nair, bair, fsmash, dsmash, Charge Shot), then
an edgeguard. Utilt (frames 14-17) is a meteor on grounded opponents (angle 270), which
bounces them up for a follow-up, and sends aerial opponents horizontally
[wiki:Samus_(SSBM)/Up_tilt] [fd]. On fastfallers dsmash at low percent leads to aerials
[wiki:Samus_(SSBM)/Down_smash].

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| dthrow | all (not Young Link for Charge Shot) | any | utilt, dash attack, Charge Shot, jab reset | Low knockback growth (20) | [wiki:Samus_(SSBM)] |
| utilt (grounded target) | all | low to moderate, typical | smash attacks or nair; bair at moderate percent | Meteor bounce | [wiki:Samus_(SSBM)/Up_tilt] [wiki:Samus_(SSBM)] |
| dair (meteor) | all | low for dsmash; typical otherwise | dsmash, utilt, Charge Shot | Slow start (frame 18) | [wiki:Samus_(SSBM)/Down_aerial] [wiki:Samus_(SSBM)/Down_smash] |
| dsmash | fastfallers | low | aerials | | [wiki:Samus_(SSBM)/Down_smash] |
| crouch cancel | approaching opponent | low to mid | dsmash or dtilt | Sends behind Samus | [wiki:Samus_(SSBM)/Down_smash] |
| uair | most | typical | missile | Multi-hit, opponents often fall out | [wiki:Samus_(SSBM)] |
| dash attack (late hit, 9%) | most | low | aerial or tilt | | [wiki:Samus_(SSBM)] |
| fair | most | high | individual hits launch; fsmash | 5% per hit | [wiki:Samus_(SSBM)/Forward_aerial] [wiki:Samus_(SSBM)/Forward_smash] |
| ftilt | most | high | tech chase | | [wiki:Samus_(SSBM)/Forward_tilt] |

### Chain grabs and tech chases

No chain grab of note. Dthrow creates a [tech chase](../techniques/tech-chase.md) with or
without the extended grapple [wiki:Samus_(SSBM)]; utilt reaches through low side
platforms (Fountain of Dreams, Yoshi's Story) for platform tech chases
[wiki:Samus_(SSBM)/Up_tilt]. Jab 1 (frame 3, 3% [fd]) can reset a missed tech: a
reset needs a hit of at most 7% that does not cause tumble, and leaves the opponent
vulnerable for 30 frames after the forced get-up [wiki:Lock].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Charge Shot (full, 25%) | all | roughly 80-110% | Often from dthrow or a read; number not from a source read | [wiki:Samus_(SSBM)] [unverified] |
| fsmash (13-15% by angle) | all | Unknown; "one of her most reliable KO options" | Angle up for most damage | [wiki:Samus_(SSBM)/Forward_smash] |
| dtilt (14%) | all | under 150% | Launches up (angle 100) | [wiki:Samus_(SSBM)] |
| dash attack (clean, 13%) | all | under 150% | | [wiki:Samus_(SSBM)] |
| nair (clean, 14%) | all | under 150%; earlier off stage | High growth, low base knockback | [wiki:Samus_(SSBM)/Neutral_aerial] |
| bair (foot, 14%) | all | Unknown; third strongest bair in the game | Edgeguard | [wiki:Samus_(SSBM)] |
| dair (16%, meteor) | all | off stage: any; grounded bounce KO around 115% | | [wiki:Samus_(SSBM)] |
| dsmash | all | weak at high percent with good DI; kills by sending off stage at low angle | Low growth (50) | [wiki:Samus_(SSBM)/Down_smash] |
| Super Missile | all | high | | [wiki:Missile] |
| utilt (aerial target) | all | Unknown | Low horizontal angle, edgeguard | [wiki:Samus_(SSBM)/Up_tilt] |

- Setups: dthrow to Charge Shot; dair or utilt to fsmash or Charge Shot; crouch cancel
  dsmash with her back to the edge, then edgeguard.
- Edgeguards: nair and bair off stage (her recovery lets her go far out), dair meteor
  (opponents can [meteor cancel](../techniques/meteor-cancel.md) after 8 frames
  [wiki:Meteor_smash]), down-angled ftilt and dtilt at the ledge, bombs (weak semi-spike
  with useful hitstun [wiki:Samus_(SSBM)]), missiles against high recoveries, and
  edgehogging.

## Recovery

- **Options:**
  - Bomb jump: near-unlimited horizontal distance, partial intangibility in Morph Ball
    (frames 10-42 of each bomb) [wiki:Samus_(SSBM)/Down_special] [wiki:Bomb_(Samus)].
  - Double jump (kept while bomb jumping).
  - Wall grapple: attaches to any wall once per airtime [wiki:Wall_grapple].
  - Up B: aerial version intangible frames 1-3, multi-hit, modest height
    [wiki:Samus_(SSBM)/Up_special].
  - [Wall jump](../techniques/wall-jump.md) on stages with walls below the ledge
    (Fountain of Dreams, Dream Land are the wiki's examples [wiki:Samus_(SSBM)]); her
    wall jump height is 32.364 units, third highest [wiki:Wall_jump].
  - Air dodge to ledge; slow fall speed and average air speed.
- **Mixups:** Stall with bombs to desynchronise the edgeguarder; go low and grapple the
  wall; go high and drift with missiles or nair; up B from below sweetspotting the ledge;
  bomb then immediate double jump to change height.
- **Weaknesses:** Slow and floaty, so strong aerials reach her; up B's multi-hit can be
  SDI'd through; grapple fails outright at the wrong range; a hit during Screw Attack
  loses the stored Charge Shot [wiki:Samus_(SSBM)].

### Edgeguarding Samus

The wiki calls this "a long and arduous task" [wiki:Bomb_recovery]. Practical points for
a drill where Samus is the CPU:

- She cannot be gimped by one weak hit; the edgeguarder has to keep hitting her outward
  or meteor her.
- Characters with good off-stage aerials go out and hit her during bomb stalls (outside
  frames 10-42 of each bomb) or before the grapple.
- Holding the ledge forces her to up B onto the stage (24 frames of landing lag
  [wiki:Samus_(SSBM)/Up_special]) or grapple the wall and climb.
- Vertical kills are more realistic than horizontal ones: juggle her and kill off the
  top.
- A realistic CPU Samus mixes: bomb stall then ledge, low wall grapple, high return with
  nair, and immediate up B.

## Defense and out of shield

- Up B out of shield is the main option (intangible frames 1-5, hit on frame 4
  [wiki:Samus_(SSBM)/Up_special]).
- Nair out of shield (active on frame 5 after the jump squat [fd]) and wavedash out of
  shield into ftilt or dsmash; her roll is slow and she relies on wavedash to escape
  [wiki:Wavedash].
- Shield grab is poor: the grab is active from frame 18.
- Crouch cancel and [ASDI](../techniques/asdi.md) down are central; see the tech above.
- Combo breakers: nair (frame 5) and aerial up B (intangible 1-3) [wiki:Samus_(SSBM)].
- Her shield does not cover her legs: low hits poke it [wiki:Samus_(SSBM)].
- On the ledge she is strong: Phanna's "Samus's Best Defensive Position: On the Edge" is
  linked in the Melee Library [lib:Samus's Best Defensive Position: On the Edge] (not
  reachable).

## As the training dummy

- Third heaviest character and second slowest faller [wiki:Samus_(SSBM)]: a floaty
  heavyweight. She does not get chain grabbed by the standard fastfaller chain grabs, and
  [Sheik](sheik.md)'s dthrow list on the wiki does not include her [wiki:Chain_grab];
  expect tech chases and juggles instead.
- She survives horizontal kill moves to very high percent; drills that need a kill should
  use vertical finishers or edgeguards.
- A realistic CPU Samus crouch cancels at low and mid percent and answers with dsmash,
  and uses up B out of shield against pressure.
- Good CPU escape choices: nair or up B as soon as hitstun ends; DI away from vertical
  launchers.
- Exact crouch cancel and knockdown thresholds: Unknown from sources read.

## Matchup notes

### vs Fox and Falco

Samus wants them to approach into crouch cancel dsmash or up B out of shield, and
edgeguards both well. They in turn kill her off the top (usmash, uair) because she falls
slowly, and [Falco](falco.md)'s lasers out-shoot missiles. She has trouble comboing them
[wiki:Samus_(SSBM)].

### vs Sheik

[Sheik](sheik.md) cannot chain grab her and Sheik's fair does not kill her early
horizontally; Samus crouch cancels Sheik's pokes. Sheik's edgeguard is still dangerous if
Samus recovers predictably [unverified].

### vs Marth

[Marth](marth.md) out-ranges her pokes with a disjoint and can juggle her; Samus relies
on missiles and on edgeguarding Marth's linear recovery [unverified].

### vs Peach and Jigglypuff

Slow, floaty matchups. [Peach](peach.md)'s dsmash and turnips contest Samus's ground
game; [Jigglypuff](jigglypuff.md) out-drifts her in the air and Samus's whiffed grab or
up B invites a Rest punish [unverified].

### vs Captain Falcon

Often cited as one of Samus's better matchups against a high tier: crouch cancel beats
his nair and stomp approaches at low percent and his recovery is easy to edgeguard
[unverified].

## Drill seeds

### Crouch cancel down smash

- **id:** `samus-cc-dsmash`
- **Goal:** Take a weak approach while crouching and punish with dsmash.
- **Player:** Samus
- **CPU:** Fox, Captain Falcon, Sheik, Marth
- **Setup:** Final Destination, Samus at centre or with her back to the edge at 0-60%;
  CPU at mid range.
- **CPU behaviour:** Approaches with a SHFFL nair, dash attack or tilt at random timing;
  sometimes grabs instead (crouch cancel loses to grab).
- **Success:** Samus is hit while crouching, stays grounded and lands dsmash within 15
  frames of hitlag ending; or she avoids the grab.
- **Fail:** Samus is knocked down, grabbed, or misses the punish.
- **Variations:** Raise Samus's percent until crouch cancel fails; replace dsmash with
  dtilt; require an edgeguard afterwards.
- **Data needed:** Dsmash frame 6, dtilt frame 6, knockback of the CPU's move against
  Samus's weight, crouch cancel knockback reduction.

### Up B out of shield

- **id:** `samus-upb-oos`
- **Goal:** Punish shield pressure with Screw Attack.
- **Player:** Samus
- **CPU:** Fox, Falco, Marth, Sheik, Captain Falcon
- **Setup:** Samus shielding at centre stage; CPU within aerial range.
- **CPU behaviour:** Hits shield with an aerial, then randomly: shine or jab, grab,
  spaced retreat, or a delayed second aerial.
- **Success:** Up B's first hit connects before the CPU's follow-up; on a spaced retreat,
  success is not using up B.
- **Fail:** Samus is hit or grabbed, or whiffs up B.
- **Variations:** Powershield option; nair out of shield as an alternative answer.
- **Data needed:** Screw Attack intangibility 1-5 and hit frame 4, shieldstun per move,
  CPU follow-up timings.

### Super wavedash timing

- **id:** `samus-super-wavedash`
- **Goal:** Hit the 1-frame stick reversal.
- **Player:** Samus
- **CPU:** None, or a stationary target at the far side of the stage
- **Setup:** Final Destination, Samus at one edge facing inward.
- **CPU behaviour:** None.
- **Success:** Opposite direction on frame 41 and travel direction on frame 42 of a
  standing bomb (39 and 40 from a crouch); Samus's slide covers at least a set distance.
- **Fail:** Normal bomb landing; display how many frames early or late the reversal was.
- **Variations:** From crouch; follow with fsmash on a target; do it toward the ledge and
  stop before falling off.
- **Data needed:** Bomb animation frame counter, stick X per frame, Samus ground speed.

### Missile wall

- **id:** `samus-missile-wall`
- **Goal:** Keep an approaching opponent out with mixed homing and Super Missiles and
  missile cancels.
- **Player:** Samus
- **CPU:** Marth, Sheik, Captain Falcon, Peach
- **Setup:** Battlefield or Final Destination, characters at opposite ends, 0%.
- **CPU behaviour:** Approaches by dash, jump, shield and (rarely) powershield; attacks
  if it reaches Samus.
- **Success:** Deal a target amount of missile damage before the CPU lands a hit.
- **Fail:** CPU hits Samus.
- **Variations:** Require a ftilt or dsmash when the CPU gets close; CPU Falco with
  lasers.
- **Data needed:** Missile spawn frames (22 ground; 24 and 15 air), animation lengths 59
  and 49, missile speed.

### Bomb jump recovery

- **id:** `samus-bomb-recovery`
- **Goal:** Return from far off stage using bombs, grapple and up B without being hit.
- **Player:** Samus
- **CPU:** Marth, Sheik, Fox, Jigglypuff
- **Setup:** Samus in tumble far off stage, at or below ledge height, with or without
  double jump, 60-120%.
- **CPU behaviour:** Randomly edgehogs, jumps out with an aerial, or waits on stage.
- **Success:** Samus grabs the ledge or lands and is not hit for 60 frames.
- **Fail:** Hit, or falls below recovery range.
- **Variations:** No double jump; require a wall grapple; stage with or without a wall
  under the ledge.
- **Data needed:** Bomb timings (10-82, explosion 83-99, intangible 10-42), grapple
  range, up B height.

### Down throw to Charge Shot

- **id:** `samus-dthrow-charge-shot`
- **Goal:** Convert a grab into a kill.
- **Player:** Samus
- **CPU:** Fox, Falco, Marth, Sheik
- **Setup:** Samus holds a full Charge Shot and has the CPU grabbed at 80-110% near
  centre stage.
- **CPU behaviour:** Random DI on the throw; attempts to act as early as possible.
- **Success:** Charge Shot connects before the CPU can shield, jump or act.
- **Fail:** Shot misses or is shielded.
- **Variations:** Replace with utilt or dash attack at low percent; start from a standing
  grab attempt on a CPU that spot dodges sometimes.
- **Data needed:** Dthrow knockback (base 80, growth 20, angle 80), Charge Shot release
  timing, CPU weight and fall speed.

### Extended grapple setup

- **id:** `samus-extended-grapple`
- **Goal:** Enter the extender code and land a long grab.
- **Player:** Samus
- **CPU:** Any standing character
- **Setup:** CPU stands about two normal grab lengths away.
- **CPU behaviour:** Stands; later walks back and forth or shields.
- **Success:** Code completed inside frames 8-39 of a grab; then a grab connects at
  extended range.
- **Fail:** Code late or wrong; grab passes through without the confirm press.
- **Variations:** CPU on a platform, then buffer dthrow.
- **Data needed:** Grab animation frame counter, D-pad input log, extended beam range.

### Edgeguard with nair and dair

- **id:** `samus-edgeguard`
- **Goal:** Go off stage, hit a recovering opponent and return.
- **Player:** Samus
- **CPU:** Fox, Falco, Marth, Captain Falcon, Sheik
- **Setup:** CPU launched off stage at 50-100% (for example from a simulated crouch
  cancel dsmash); Samus on stage near the edge.
- **CPU behaviour:** Recovers with a random mix of its options.
- **Success:** CPU loses the stock; Samus returns.
- **Fail:** CPU returns to stage or ledge.
- **Variations:** Meteor-only (dair) mode; ledge-only mode (down-angled ftilt, dtilt).
- **Data needed:** Nair, bair and dair windows, CPU recovery data, meteor cancel window
  of 8 frames.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlSs.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/samus.json`](../framedata/samus.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 3-4 | 3 | Sakurai | 0 | 100 | - |  | 17 | - | 3 | -11 |  |
| Jab 2 | `jab2` | 5-7 | 7 | Sakurai | 15 | 100 | - |  | 30 | - | 5 | -20 | starts 1 frame late (included) |
| Dash attack | `dash_attack` | 7-9 | 13 | 60 | 22 | 105 | - |  | 37 | - | 7 | -23 |  |
|  |  | 10-16 | 9 | 60 | 22 | 105 | - |  |  |  | 6 | -21 |  |
| Forward tilt (angled up) | `ftilt_high` | 6-8 | 11 | Sakurai | 10 | 100 | - |  | 31 | 30 | 6 | -17 |  |
| Forward tilt (slightly up) | `ftilt_mid_high` | 6-8 | 10 | Sakurai | 10 | 100 | - |  | 31 | 30 | 6 | -17 |  |
| Forward tilt | `ftilt` | 6-8 | 10 | Sakurai | 10 | 100 | - |  | 31 | 30 | 6 | -17 |  |
| Forward tilt (slightly down) | `ftilt_mid_low` | 6-8 | 10 | Sakurai | 10 | 100 | - |  | 31 | 30 | 6 | -17 |  |
| Forward tilt (angled down) | `ftilt_low` | 6-8 | 9 | Sakurai | 10 | 100 | - |  | 31 | 30 | 6 | -17 |  |
| Up tilt | `utilt` | 14-17 | 13/12 | 270/Sakurai | 40 | 100 | - |  | 39 | 35 | 7 | -13 |  |
| Down tilt | `dtilt` | 6-8 | 14 | 100 | 80 | 60 | - | fire | 39 | - | 8 | -25 |  |
| Forward smash (angled up) | `fsmash_high` | 10-13 | 15 | Sakurai | 30 | 104 | - |  | 43 | - | 8 | -25 | charge hold frame 4 |
| Forward smash (slightly up) | `fsmash_mid_high` | 10-13 | 14 | Sakurai | 30 | 104 | - |  | 43 | - | 8 | -25 | charge hold frame 4 |
| Forward smash | `fsmash` | 10-13 | 14 | Sakurai | 30 | 104 | - |  | 43 | - | 8 | -25 | charge hold frame 4 |
| Forward smash (slightly down) | `fsmash_mid_low` | 10-13 | 14 | Sakurai | 30 | 104 | - |  | 43 | - | 8 | -25 | charge hold frame 4 |
| Forward smash (angled down) | `fsmash_low` | 10-13 | 13 | Sakurai | 30 | 104 | - |  | 43 | - | 7 | -26 | charge hold frame 4 |
| Up smash | `usmash` | 12-14 | 4 | 130 | 50 | 50 | - | fire | 59 | 58 | 3 | -42 | charge hold frame 8 |
|  |  | 16-18 | 4 | 120 | 35 | 50 | - | fire |  |  | 3 | -38 |  |
|  |  | 20-22 | 4 | 90 | 25 | 50 | - | fire |  |  | 3 | -34 |  |
|  |  | 24-26 | 5 | 85 | 30 | 50 | - | fire |  |  | 4 | -29 |  |
|  |  | 28-29 | 6 | 80 | 50 | 120 | - | fire |  |  | 4 | -25 |  |
| Down smash | `dsmash` | 6-8 | 16 | 120 | 110 | 50 | - |  | 48 | 45 | 9 | -29 | charge hold frame 3 |
|  |  | 14-16 | 15 | 120 | 90 | 40 | - |  |  |  | 8 | -22 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 5-8 | 14 | Sakurai | 10 | 100 | - |  | 49 | 40 | 8 | 15 | 7 | <5, >34 | +1 |  |
|  |  | 9-29 | 10 | Sakurai | 10 | 100 | - |  |  |  | 6 |  |  |  | -1 |  |
| Forward air | `fair` | 6-7, 13-14, 20-21, 27-28 | 5 | 85 | 20 | 100 | - | fire | 55 | 50 | 4 | 15 | 7 | <1, >46 | -3 |  |
|  |  | 32-33 | 5 | Sakurai | 20 | 100 | - | fire |  |  | 4 |  |  |  | -3 |  |
| Back air | `bair` | 9-12 | 10/14 | Sakurai | 30/42 | 100 | - |  | 39 | 37 | 8 | 15 | 7 | <9, >30 | +1 |  |
| Up air | `uair` | 5-6 | 3 | 90/Sakurai | 0 | 100/130 | 30/0 |  | 39 | 39 | 3 | 15 | 7 | <5, >33 | -4 |  |
|  |  | 8-9, 11-12, 14-15, 17-18 | 1 | 80 | 0 | 100/130 | 30/0 |  |  |  | 2 |  |  |  | -5 |  |
|  |  | 20-21 | 4 | Sakurai | 40 | 120 | - |  |  |  | 3 |  |  |  | -4 |  |
| Down air | `dair` | 18-22 | 16 | 270 | 30 | 100 | - |  | 54 | 49 | 9 | 15 | 7 | <3, >33 | +2 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 18-41 | 94 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 18-33 | 74 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 10 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 9 | 9 | 42 | 50 | 45 | - | - | 15 | 41 |  |
| Back throw | `bthrow` | 8 | 8 | 140 | 50 | 42 | - | - | 11 | 41 |  |
| Up throw | `uthrow` | 7 | 7 | 90 | 100 | 45 | - | - | 31 | 41 |  |
| Down throw | `dthrow` | 6 | 6 | 80 | 80 | 20 | - | - | 21 | 41 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Down B: Bomb, ground | `special_lw` | - | - | - | - | - | - | - | 53 | - | - | - |  |
| Down B: Bomb, air | `special_air_lw` | - | - | - | - | - | - | - | 53 | - | - | - |  |
| Neutral B: Charge Shot, ground, Start | `special_n_start` | - | - | - | - | - | - | - | 13 | - | - | - |  |
| Neutral B: Charge Shot, ground, Hold | `special_n_hold` | - | - | - | - | - | - | - | 9 | - | - | - |  |
| Neutral B: Charge Shot, ground, Cancel | `special_n_cancel` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Neutral B: Charge Shot, ground | `special_n` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Neutral B: Charge Shot, air, Start | `special_air_n_start` | - | - | - | - | - | - | - | 13 | - | - | - |  |
| Neutral B: Charge Shot, air | `special_air_n` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Side B: Missile, ground | `special_s` | - | - | - | - | - | - | - | 59 | - | - | - | spawns article/projectile on 22 |
| Special | `special` | - | - | - | - | - | - | - | 49 | - | - | - | spawns article/projectile on 22 |
| Side B: Missile, air | `special_air_s` | - | - | - | - | - | - | - | 59 | - | - | - | spawns article/projectile on 24 |
| SpecialAir | `special_air` | - | - | - | - | - | - | - | 49 | - | - | - | spawns article/projectile on 15 |
| Up B: Screw Attack, ground | `special_hi` | 4-5 | 2 | 100 | 130/100 | 100 | - |  | 49 | - | 2 | - | intangible 1-5 |
|  |  | 6-7, 8-9, 10-11 | 1 | 105/100 | 110/70 | 100 | - |  |  |  | 2 | - |  |
|  |  | 12-13, 14-15, 16-17, 18-19, 20-21, 22-23, 24-25, 26-27 | 1 | 110/200 | 70/40 | 100 | - |  |  |  | 2 | - |  |
|  |  | 28-29 | 1 | 70 | 0 | 100 | 80 | electric |  |  | 2 | - |  |
| Up B: Screw Attack, air | `special_air_hi` | 4-5, 6-7, 8-9 | 1 | 140/110 | 25/100 | 0 | - |  | 47 | - | 2 | - | intangible 1-3 |
|  |  | 10-11, 12-13, 14-15, 16-17, 18-19, 20-21, 22-23, 24-25 | 1 | 140/110 | 25/80 | 0 | - |  |  |  | 2 | - |  |
|  |  | 26-27 | 1 | 70 | 0 | 100 | 80 | electric |  |  | 2 | - |  |
| Down B: Bomb, ground | `special_lw_309` | - | - | - | - | - | - | - | 53 | - | - | - | spawns article/projectile on 10 |
| Down B: Bomb, air | `special_air_lw_310` | - | - | - | - | - | - | - | 53 | - | - | - | spawns article/projectile on 10 |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-15 | - | 22 | 20 |  |
| Roll forward | `roll_forward` | intangible 4-23 | - | 44 | - |  |
| Roll backward | `roll_backward` | intangible 4-23 | - | 44 | - |  |
| Air dodge | `airdodge` | intangible 4-29 | - | 49 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-29 | 19-20, 28-29 (8/6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-14 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-20 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-27 | 19-20, 25-27 (6%) | 49 | - |  |
| Getup roll forward (face down) | `getup_roll_forward_facedown` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-22 | - | 35 | - |  |
| Tech in place | `tech_in_place` | intangible 2-20 | - | 26 | - | starts 1 frame late (included) |
| Tech roll forward | `tech_roll_forward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Tech roll backward | `tech_roll_backward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Wall tech | `wall_tech` | - | - | 26 | - | starts 1 frame late (included) |
| Wall tech jump | `wall_tech_jump` | - | - | 40 | - | starts 1 frame late (included) |
| Ceiling tech | `ceiling_tech` | intangible 2-12 | - | 26 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-55 | - | 58 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 32 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-34 | 38-40 (10%) | 68 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-20 | 24-27 (10%) | 54 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-67 | - | 78 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-36 | - | 48 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-19 | - | 19 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 35 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-11 | - | 11 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 32 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Up B | jump cancel | 5 | `special_hi` |
| Neutral air | jump | 8 | `nair` |
| Up air | jump | 8 | `uair` |
| Forward air | jump | 9 | `fair` |
| Back air | jump | 12 | `bair` |
| Up smash | jump cancel | 13 | `usmash` |
| Shield grab | direct | 18 | `grab` |
| Down air | jump | 21 | `dair` |
| Spot dodge | direct | intangible 2-15 of 22 | `spotdodge` |
| Roll forward | direct | intangible 4-23 of 44 | `roll_forward` |
| Roll backward | direct | intangible 4-23 of 44 | `roll_backward` |
| Wavedash | jump | actionable on frame 15 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Samus indexed by [The Melee Library](https://www.meleelibrary.com/#samus) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [Are You a Samus Player?](https://www.youtube.com/watch?v=G-qmHasiFlw) | SSBM Tutorials | They give an overview of Samus the character to give you an idea of whether you would like to play her. |
| [2020 Samus Melee Techs Guide](https://www.youtube.com/watch?v=ne3gSitLsOY&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=19&t=0s) | Third Chair | Video guide on performing useful Samus tech in 2020. |
| [Mission Briefing](https://www.youtube.com/watch?v=00HEzWiSmpM) | Aftermath | Old school Samus tutorial video. With an [accompanying thread](http://smashboards.com/threads/aftermaths-guide-to-samus.38411/). |
| [Superwavedash Discussion](http://smashboards.com/threads/official-super-wavedash-discussion-please-read-and-post-here.55424/) | Aftermath and community |  |
| [Intro To Samus + Character Matchups](http://smashboards.com/threads/intro-to-samus-character-match-ups.185258/) | AIDS | A 2008 guide to Samus with interesting discussions in the posts too. |
| [Samus Hitboxes and Frame Data](http://smashboards.com/threads/samus-hitboxes-and-frame-data.320253/) | Stratocaster, Standardtoaster, and SuperDoodleMan |  |
| [The Samus Index Thread](http://smashboards.com/threads/the-samus-index-thread-updated-3-9-13.333011/) | iRobinhoood and community | A large collection of various posts about matchups. |
| [EXTENNNDUURRRRRR](http://smashboards.com/threads/extennnduurrrrrr-samus-gen-disc.243160/) | community | General Samus discussion. |
| [Samus Neutral Game Tutorial](https://www.youtube.com/watch?v=is0DOA5lYuw) | SSBM Tutorials and Hugs |  |
| [Samus Extended Grapple Instructions and Applications](https://www.youtube.com/watch?v=WKbFwgUMrxY) | Rykard |  |
| [Mechanics Behind Daughter Dash, SuperWavedash, and Boost Ball](https://www.youtube.com/watch?v=8GZelT0GuPs) | Goomy | Samus can do some wonky physics stuff with her down special. |
| [Bomb Pressure and Bomb Combos](https://youtu.be/F8HqMTduEBA) | Goomy | Samus can do some strong shield pressure with her down b. |
| [Samus’s Invincible Ledgedash Options](https://www.youtube.com/watch?v=HHOAoAmZWA4) | Practical TAS | A video showcasing Samus’s options she can perform intangibly from a ledgedash. It does not show her options after an aerial interrupt from the ledge which grants more intangibility for her than ledgedash. |
| [ESAM’s Battlefield Missiles](https://www.youtube.com/watch?v=KKDP5wdEuYI) | ESAM |  |
| [How to Super Wavedash and Use Extended Grapple](https://www.youtube.com/watch?v=U_tjfr_kaHs) | Smash Bros. Legacy |  |
| [Samus’s Best Defensive Position: On the Edge](http://smashboards.com/threads/samus-best-defensive-position-on-the-edge.108203/) | Phanna | An old outline by Phanna describing Samus’s ledge game. |
| [Samus Index Thread](http://smashboards.com/threads/the-samus-index-thread-updated-3-9-13.333011/) | community | Index thread of discussions on Samus. Lots of old information but some may still be applicable. |
| [NEW EXTENDER TECH?!](https://www.youtube.com/watch?v=0XsAWjyYJ6Y) | CoriGames | Buffer dthrow with cstick to covert off of extender grabs on platforms. |
| [Samus Advanced Techniques](https://www.youtube.com/watch?v=J1d0Ue4a0IQ) | SSBM Tutorials |  |
| [Bomb Shield Pressure](https://www.reddit.com/r/SSBM/comments/4u0m4r/samus_multibomb_shield_pressure_is_arguably/) | Goomy |  |
| [Official Samus Missile Guide (2007)](https://smashboards.com/threads/official-samus-missile-guide.105908/) | Wii4Mii 99 | An old guide with fundamentals of missile usage. |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Samus (SSBM): https://www.ssbwiki.com/Samus_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Samus_(SSBM)/Up_special ,
  /Down_special , /Side_special , /Neutral_special , /Grab , /Grab_aerial , /Down_throw ,
  /Up_throw , /Down_smash , /Forward_smash , /Up_smash , /Down_tilt , /Forward_tilt ,
  /Up_tilt , /Dash_attack , /Neutral_aerial , /Forward_aerial , /Back_aerial ,
  /Up_aerial , /Down_aerial
- SSBWiki, Super wavedash: https://www.ssbwiki.com/Super_wavedash
- SSBWiki, Extended Grapple: https://www.ssbwiki.com/Extended_Grapple
- SSBWiki, Bomb recovery: https://www.ssbwiki.com/Bomb_recovery
- SSBWiki, Bomb (Samus): https://www.ssbwiki.com/Bomb_(Samus)
- SSBWiki, Missile: https://www.ssbwiki.com/Missile
- SSBWiki, Grapple Beam: https://www.ssbwiki.com/Grapple_Beam
- SSBWiki, Wall grapple: https://www.ssbwiki.com/Wall_grapple
- SSBWiki, Charge Shot: https://www.ssbwiki.com/Charge_Shot
- SSBWiki, Perfect shield: https://www.ssbwiki.com/Perfect_shield
- SSBWiki, Meteor smash: https://www.ssbwiki.com/Meteor_smash
- SSBWiki, Lock: https://www.ssbwiki.com/Lock
- SSBWiki, Wall jump: https://www.ssbwiki.com/Wall_jump
- SSBWiki, Jump, Wavedash, Chain grab: https://www.ssbwiki.com/Jump ,
  https://www.ssbwiki.com/Wavedash , https://www.ssbwiki.com/Chain_grab
- Melee Library, Samus section (card titles and descriptions only; Smashboards and Reddit
  links returned errors and videos cannot be watched).
- Frame data dump: `Samus.json`.
