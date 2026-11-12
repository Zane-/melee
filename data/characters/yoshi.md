---
schema: melee-character/v1
id: yoshi
name: Yoshi
aliases: [Yosh]
tier: "B+ (10th of 26), 2021 list"
archetype: [heavy, fastfaller, punish-heavy, mixup, technical, edgeguarder]
related: []
summary: Yoshi wins by absorbing or parrying the opponent's attack with double jump armour or shield startup invincibility, then converting with double-jump-cancelled aerials into a down smash, forward air meteor or up air kill.
key_tech: [double-jump-armor, double-jump-cancel, djc-counter, parry, shield-quirks, egg-lay, egg-throw, edge-canceled-eggs, dtilt-knockdown, djc-turnaround-edgehog]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlYs.dat
framedata: ../framedata/yoshi.json
code: src/melee/ft/kinds/ftYoshi
specials:
  neutral_b: "Egg Lay"
  side_b: "Egg Roll"
  up_b: "Egg Throw"
  down_b: "Yoshi Bomb"
attributes:
  weight: 108
  gravity: 0.093
  fall_speed: 1.93
  fast_fall_speed: 2.93
  jump_squat: 5
  jumps: 2
  walk_speed: 1.15
  dash_speed: 1.33
  run_speed: 1.6
  traction: 0.06
  air_speed: 1.2
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [3, 18, 3]
  jab2: [4, 21, 5]
  dash_attack: [10, 42, 9]
  ftilt_high: [6, 30, 13]
  ftilt_mid_high: [6, 30, 13]
  ftilt: [6, 30, 12]
  ftilt_mid_low: [6, 30, 12]
  ftilt_low: [6, 30, 11]
  utilt: [8, 30, 10]
  dtilt: [8, 24, 10]
  fsmash_high: [14, 44, 16]
  fsmash: [14, 44, 16]
  fsmash_low: [14, 44, 16]
  usmash: [11, 40, 14]
  dsmash: [6, 50, 14]
  nair: [3, 45, 14]
  fair: [19, 44, 17]
  bair: [10, 38, 7]
  uair: [5, 39, 13]
  dair: [18, 56, 4]
  grab: [18, 80, 0]
  dash_grab: [11, 71, 0]
  pummel: [10, 25, 3]
  fthrow: [null, 40, 6]
  bthrow: [null, 44, 6]
  uthrow: [null, 44, 5]
  dthrow: [null, 44, 4]
  special_n1: [17, 40, 1]
  special_n1_296: [null, 40, 0]
  special_n2: [null, 30, 7]
  special_air_n1: [17, 40, 1]
  special_air_n1_299: [null, 40, 0]
  special_air_n2: [null, 30, 7]
  special_s_start: [null, 20, 0]
  special_s_loop: [1, 60, 4]
  special_s_loop_303: [null, 60, 0]
  special_s_end: [null, 40, 0]
  special_air_s_start: [null, 20, 0]
  special_s_loop_306: [null, 60, 0]
  special_s_loop_307: [1, 60, 4]
  special_air_s_end: [null, 40, 0]
  special_hi: [null, 55, 0]
  special_air_hi: [null, 55, 0]
  special_lw: [27, 28, 16]
  special_lw_landing: [null, 40, 0]
  special_air_lw: [19, 20, 14]
oos:  # option: frame the hitbox is out
  nair: 8
  uair: 10
  usmash: 12
  bair: 15
  grab: 18
  dair: 23
  fair: 24
resources: 12
# generated: end
---

# Yoshi

<!-- GENERATED:attributes -->
## Attributes

Read from `PlYs.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 108 |
| Gravity | 0.093 |
| Terminal fall speed | 1.93 |
| Fast-fall speed | 2.93 |
| Jump squat (frames before airborne) | 5 |
| Full hop / short hop initial Y speed | 2.5 / 1.8 |
| Air jump Y multiplier | 1.3 |
| Jumps | 2 |
| Walk max speed | 1.15 |
| Dash initial speed / run max speed | 1.33 / 1.6 |
| Ground friction (traction) | 0.06 |
| Air max horizontal speed | 1.2 |
| Air acceleration (base + stick) | 0.02 + 0.028 |
| Air friction | 0.013 |
| Normal landing lag | 4 |
| Shield size | 6 |
<!-- /GENERATED:attributes -->

## Overview

Yoshi is a heavy character who falls fast, runs fast, has the second-highest air speed
in the game and the fifth-longest [wavedash](../techniques/wavedash.md)
[wiki:Yoshi_(SSBM)]. He trades several universal options for unique ones: his double jump
has knockback armour, his shield is an egg that cannot be poked and takes no shieldstun,
and he has no jump out of shield and no recovering up B [wiki:Yoshi_(SSBM)]. Neutral
revolves around fast pokes (dtilt, ftilt, jab), up B (Egg Throw) as a lobbed projectile,
and baiting attacks into armour or a parry. His punish game is built on double jump
cancelled (DJC) aerials, which let him throw nair, uair and fair repeatedly close to the
ground; dsmash, fair (a meteor) and uair finish stocks. He dies when his double jump is
used or broken off stage, because after it he has only an air dodge, and he is easy to
combo and chain grab because he is heavy, falls fast and cannot jump out of shield
[wiki:Yoshi_(SSBM)]. He is one of the most technically demanding characters.

## Strengths and weaknesses

- **Strengths:**
  - Double jump with knockback armour for up to 70 frames [wiki:Yoshi_(SSBM)].
  - DJC aerials: nair active on frame 3, uair on frame 5, with 7 and 9 frames of
    [L-cancelled](../techniques/l-cancel.md) landing lag [fd].
  - Dsmash hits on frame 6 on a large tail hitbox and sends at angle 30 [fd]
    [wiki:Yoshi_(SSBM)].
  - Dtilt has set knockback that puts every character in tumble at 0%
    [wiki:Yoshi_(SSBM)/Down_tilt].
  - Shield cannot be shield-stabbed and takes no shieldstun; shield startup is
    invincible (parry) [wiki:Yoshi_(SSBM)] [wiki:Shield].
  - Heavy; with armour it is "somewhat common" to live past 200% [wiki:Yoshi_(SSBM)].
  - Egg Throw can be aimed over a wide arc [wiki:Egg_Throw].
- **Weaknesses:**
  - No up B recovery: after the double jump only an air dodge remains
    [wiki:Yoshi_(SSBM)].
  - Cannot jump out of shield except during the first 6 shield frames [wiki:Shield]; slow
    rolls; slow grab (standing grab active from frame 18 [wiki:Yoshi_(SSBM)/Grab]).
  - Easy to combo and chain grab; awkward large hurtbox [wiki:Yoshi_(SSBM)].
  - Using an aerial during the double jump removes its rise, so he cannot attack
    edgeguarders without giving up height [wiki:Yoshi_(SSBM)].
  - Dash grab's grab box is misaligned on the z-axis and can miss thin characters such as
    [Marth](marth.md) and [Zelda](zelda.md) at point-blank range
    [wiki:Yoshi_(SSBM)/Grab].

## Character tech

### Double jump armour

- **id:** `double-jump-armor`
- **What:** During the double jump Yoshi has knockback-based armour: hits below a
  knockback threshold deal damage and hitlag but do not interrupt the jump or move him.
- **Inputs:** Press jump in the air shortly before a hit would connect.
- **Timing:** The armour lasts for a maximum of 70 frames [wiki:Yoshi_(SSBM)]. It is
  subtractive knockback armour: the threshold is subtracted from the knockback received
  [wiki:Armor]. The threshold value was not in the sources read; it is commonly quoted as
  120 units of knockback [unverified]. Because it is knockback-based, it fails more often
  as Yoshi's percent rises and against strong moves [wiki:Double_jump_cancel_counter].
- **Used for:** Escaping combos and juggles, recovering through edgeguard hits, baiting an
  attack and making it unsafe on hit.
- **Common errors:** Jumping too late (already hit); using it at high percent against a
  move that breaks it, which usually costs the stock because the jump is gone; using it
  on stage and then having no jump when knocked off.
- **Drill idea:** CPU throws a fixed move at Yoshi in the air at a set percent; success if
  Yoshi double jumps, takes the hit without being launched and lands a counter-hit.

### Double jump cancel

- **id:** `double-jump-cancel`
- **What:** Yoshi's double jump applies its upward force gradually through the animation,
  so starting an aerial during it cancels the rise. Jump, double jump and aerial in quick
  succession puts an aerial out just above the ground and lets him land at once.
- **Inputs:** Jump, double jump as soon as he leaves the ground (not on the very first
  airborne frame), aerial, [fast fall](../techniques/fast-fall.md), L-cancel. Repeat.
- **Timing:** If the double jump and aerial are input as early as possible ("instant
  DJC"), Yoshi lands before the hitbox appears, for every aerial [wiki:Double_jump_cancel],
  so a small delay is required. Relevant startups: nair frame 3, uair frame 5, bair frame
  10, fair frame 19 [fd]. Landing lag normal/L-cancelled: nair 15/7, uair 19/9, bair
  15/7, fair 21/10, dair 26/13 [fd]. Jump squat length: 5 frames [unverified].
- **Used for:** Nair chains on floaties, uair juggles on fastfallers, finishing with fair
  or dsmash, shield pressure [wiki:Double_jump_cancel] [wiki:Yoshi_(SSBM)]. Faster than a
  [SHFFL](../techniques/shffl.md) for the same aerial.
- **Common errors:** Too fast, landing with no hitbox; too slow, rising into a full
  double jump; doing it near the edge and drifting off stage with no jump left
  [wiki:Yoshi_(SSBM)].
- **Drill idea:** Standing CPU; count DJC nairs or uairs that connect in a row with
  correct L-cancels inside a time limit.

### DJC counter

- **id:** `djc-counter`
- **What:** Absorb an attack with double jump armour, then immediately cancel the jump
  with an aerial or neutral B to hit the opponent during their recovery frames.
- **Inputs:** In the air (often from a short hop), double jump just before the opponent's
  hit lands; after hitlag, nair (or uair, or neutral B Egg Lay).
- **Timing:** Any aerial or special can be started immediately after the absorbed hit
  [wiki:Double_jump_cancel_counter]. Nair is the usual choice because it is active on
  frame 3 [fd].
- **Used for:** Beating approaching aerials and anti-airs, turning disadvantage into a
  punish, bait-and-punish in neutral [wiki:Double_jump_cancel_counter].
- **Common errors:** Opponent hits with a move strong enough to break armour; countering
  with a slow aerial; countering off stage and losing the jump.
- **Drill idea:** CPU attacks airborne Yoshi with a random aerial; success if Yoshi takes
  the hit in armour and his nair or Egg Lay connects within N frames after hitlag.

### Parry

- **id:** `parry`
- **What:** The start of Yoshi's shield animation is invincible. An attack that connects
  during it does nothing (no shield damage, shieldstun, pushback or hitlag for Yoshi),
  and Yoshi can jump out of those frames, which he cannot do from his full shield.
- **Inputs:** Digital (full click) press of L or R so that the attack connects in the
  first few frames; then jump and act (DJC aerial, jump-cancelled usmash, wavedash) or
  drop shield.
- **Timing:** Sources differ on the window. The character page says the shield button
  must be pressed "three or fewer frames before an attack hits" [wiki:Yoshi_(SSBM)]. The
  shield page says Yoshi is invincible during the first 6 shield frames, that the shield
  itself becomes active 3 frames after a digital press (immediately with an analog
  press), and that he can jump out only during the first 6 shield frames with a digital
  press [wiki:Shield]. The powershield page adds that on shield frames 1-2 Yoshi parries
  physical hits rather than powershielding them, that on frames 3-6 a close hit can be
  powershielded instead, and that a parry skips hitlag [wiki:Perfect_shield]. Magus's
  frame research thread is linked in the Melee Library [lib:Frame Data on Yoshi's Shield]
  but could not be reached, so the exact numbers should be checked in game.
- **Used for:** Punishing moves that are safe on every other shield; getting a jump out
  of shield.
- **Common errors:** Analog press (shield appears at once, no parry); pressing early so
  the hit lands on the full shield, where he cannot jump; pressing late and being hit.
- **Drill idea:** CPU performs one attack with randomised delay; success if the hit
  connects during Yoshi's invincible shield startup and Yoshi lands a punish within N
  frames.

### Shield quirks and no jump out of shield

- **id:** `shield-quirks`
- **What:** The rule set of Yoshi's egg shield, which changes every defensive situation.
- **Inputs:** Not a technique; a set of facts to play around.
- **Timing:** From the full shield Yoshi cannot jump, so no
  [out-of-shield](../techniques/out-of-shield.md) aerial, up B, usmash or wavedash
  [wiki:Shield] [wiki:Yoshi_(SSBM)]. He takes no shieldstun and can act right after
  hitlag [wiki:Shield]. He can drop shield after 7 frames instead of 8 [wiki:Shield]. He
  cannot be shield poked, but the egg darkens as it weakens and can still break
  [wiki:Shield]. Light shield makes him slide very far when hit; full shield pushback is
  small and nearly independent of damage [wiki:Shield]. His powershield can be "stored"
  and can trigger on physical hits at any time while shielding, but he cannot powershield
  cancel [wiki:Shield] [wiki:Perfect_shield].
- **Used for:** Choosing between shield drop, roll, spot dodge, shield grab, light shield
  slide, and parry.
- **Common errors:** Holding shield under pressure and getting grabbed or shield broken;
  trying to jump out of shield.
- **Drill idea:** CPU pressures the shield; success if Yoshi escapes or punishes using
  only legal options (drop, roll, spot dodge, grab, light shield slide).

### Egg Lay

- **id:** `egg-lay`
- **What:** Neutral B is a command grab, usable in the air, that swallows the opponent
  and traps them in an egg.
- **Inputs:** B with the opponent in tongue range; in the air it works the same.
- **Timing:** The grab box is out on frames 17-21 and the move lasts 39 frames on a miss
  [fd]. It does 7%; the egg lasts 200 frames, reduced by 14 frames per mash input and by
  2 frames per percent of damage dealt to the egg; damage to an egged opponent is halved
  and they take no knockback [wiki:Egg_Lay]. Yoshi has some armour from the moment the
  tongue connects until the egg is laid [wiki:Egg_Lay].
- **Used for:** Beating shields (it is a grab) when his real grab is too slow or
  awkward; after a DJC counter [wiki:Double_jump_cancel_counter]; free damage while the
  opponent is egged.
- **Common errors:** Whiffing (39 frames); expecting it to carry opponents off stage (they
  keep horizontal control and break out early [wiki:Egg_Lay]).
- **Drill idea:** CPU shields after Yoshi's aerial; success if Egg Lay connects, then
  score the damage dealt before the CPU breaks out.

### Egg Throw

- **id:** `egg-throw`
- **What:** Up B lobs an egg in an arc. Stick direction during the windup sets the angle,
  and how long B is held sets the distance. It is not a recovery move and does not leave
  Yoshi helpless.
- **Inputs:** Up + B; tilt the stick during the windup to aim; hold B for a longer
  throw.
- **Timing:** The animation is 54 frames [fd]. The egg does 10% (grounded explosion) or
  12% (aerial explosion) [wiki:Yoshi_(SSBM)].
- **Used for:** Spacing, interrupting recoveries and ledge stalls, extending combos,
  forcing approaches [wiki:Yoshi_(SSBM)].
- **Common errors:** Throwing at close range; using it in the air off stage expecting
  height.
- **Drill idea:** Moving CPU at mid to long range; score eggs that hit within a time
  limit.

### Edge-canceled eggs

- **id:** `edge-canceled-eggs`
- **What:** A ledge stall: drop from the ledge, double jump, immediately Egg Throw, and
  regrab the ledge while the egg flies. Yoshi can grab the ledge while facing either way
  during Egg Throw [wiki:Yoshi_(SSBM)].
- **Inputs:** From ledge hang: flick the stick down or away, double jump, up B at once;
  Yoshi regrabs the ledge. Reverse version: use the double jump's turnaround so the egg
  is thrown away from the stage [wiki:Egg_Throw].
- **Timing:** Exact frames Unknown. Too slow and Yoshi rises above the ledge or lands on
  stage; too fast and he falls and dies [wiki:Egg_Throw].
- **Used for:** Throwing eggs from ledge intangibility; edgeguarding with reverse eggs.
- **Common errors:** Self-destruct (the double jump is spent every repetition).
- **Drill idea:** Count consecutive ledge regrabs with an egg thrown each cycle; fail on
  landing on stage or dying.

### Down tilt knockdown

- **id:** `dtilt-knockdown`
- **What:** Dtilt has fixed (set) knockback strong enough to tumble any character at 0%,
  at a very low angle. It starts tech chases on stage and gimps at the ledge.
- **Inputs:** Down + A (tilt).
- **Timing:** Hits frames 8-10, 10%, angle 28, set knockback 100, total animation 23
  frames [fd] [wiki:Yoshi_(SSBM)/Down_tilt].
- **Used for:** Opening at 0%, [tech chasing](../techniques/tech-chase.md), low-percent
  edgeguards [wiki:Yoshi_(SSBM)/Down_tilt].
- **Common errors:** None execution-wise; the follow-up requires reacting to the tech.
- **Drill idea:** CPU at 0% is hit by dtilt and techs in a random direction or misses;
  success if Yoshi's next hit connects before the CPU is actionable.

### Double jump turnaround edgehog

- **id:** `djc-turnaround-edgehog`
- **What:** Yoshi can turn around with his double jump, so he can run off stage and
  double jump back toward the ledge to grab it facing the stage very quickly.
- **Inputs:** Run off the edge, hold toward the stage and press jump; drift into the
  ledge.
- **Timing:** Unknown in frames. Described on the wiki as a quick edgehog
  [wiki:Yoshi_(SSBM)].
- **Used for:** Edgehogging; setting up ledge egg stalls.
- **Common errors:** Jumping too late and going below the ledge with no jump left.
- **Drill idea:** CPU recovering to ledge; success if Yoshi holds the ledge within N
  frames of leaving the ground and the CPU fails to grab it.

## Neutral game

- Fast ground movement: dash, long wavedash, and a usable
  [moonwalk](../techniques/moonwalk.md) [wiki:Moonwalk].
- Pokes: jab (frame 3 [fd]), ftilt (frames 6-8, launches upward at angles 60-80 for
  combos [fd]), dtilt (frame 8, knockdown at any percent), dsmash (frame 6).
- Egg Throw from range to make the opponent move.
- Short hop or DJC nair as a fast, lingering approach; nair is active from frame 3 for
  about 30 frames [fd].
- Bait with armour: jump in, double jump through the opponent's swing, counter.
- Dash attack has an intangible head early in the move; fsmash and usmash have an
  intangible head while their hitboxes are out (frames 12-16 and 11-15)
  [wiki:Yoshi_(SSBM)] [wiki:Yoshi_(SSBM)/Forward_smash] [wiki:Yoshi_(SSBM)/Up_smash].
- Grab is risky: standing grab is active frames 18-23 (79 frames total), dash grab frames
  11-16 (70 total) and can miss thin characters [wiki:Yoshi_(SSBM)/Grab].

## Punish game

Yoshi's punishes are DJC aerial chains. On fastfallers utilt chains into itself at low
percent and uair juggles work especially well; on floaties DJC nair chains are the main
tool because utilt does not combo them [wiki:Double_jump_cancel] [wiki:Yoshi_(SSBM)].
Ftilt pops the opponent up for a fair meteor or, if they DI (directional influence,
holding a direction to bend the launch) toward the stage, a dsmash [wiki:Yoshi_(SSBM)].
Combos usually end with fair, dsmash or uair. Dair does about 51-53% if all 14 hits
connect in NTSC [wiki:Yoshi_(SSBM)], and bair about 20% [wiki:Yoshi_(SSBM)].

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| utilt | fastfallers | low | utilt again, then uair | Does not combo floaties | [wiki:Yoshi_(SSBM)] [wiki:Double_jump_cancel] |
| DJC uair | fastfallers | typical | more uairs, then fair or uair finish | | [wiki:Double_jump_cancel] |
| DJC nair | floaties | typical | nair chain, then fair | | [wiki:Double_jump_cancel] |
| ftilt (angled up) | most | typical | fair meteor | | [wiki:Yoshi_(SSBM)] |
| ftilt | most | typical | dsmash if they DI in | | [wiki:Yoshi_(SSBM)] |
| fair (on stage) | most | typical | dsmash | Meteor bounces them | [wiki:Yoshi_(SSBM)] |
| dtilt | all | from 0% | tech chase or edgeguard | Set knockback | [wiki:Yoshi_(SSBM)/Down_tilt] |
| uthrow / dthrow | most | low | DJC aerials | Both called good combo starters; the grab is the hard part | [wiki:Yoshi_(SSBM)] |
| parry or DJC counter | all | any | nair, usmash, Egg Lay | | [wiki:Double_jump_cancel_counter] |
| Egg Lay | all | any | damage on the egg, then pressure on break-out | Halved damage in egg | [wiki:Egg_Lay] |

### Chain grabs and tech chases

No chain grab of note. Tech chases come from dtilt (tumble at 0%) and from throws; jab 1
(3% [fd]) fits the Melee reset rule (at most 7% and no tumble) for punishing a missed
tech, which leaves the opponent vulnerable for 30 frames after the forced get-up
[wiki:Lock].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| dsmash (front 14%, angle 30) | all | Unknown; "considered Yoshi's best KO move" | Kills by low angle, especially near the edge | [wiki:Yoshi_(SSBM)] [fd] |
| fair (17%, meteor) | all | any off stage | Frame 19; opponents can meteor cancel after 8 frames | [fd] [wiki:Meteor_smash] |
| uair (13%, angle 90) | all | roughly 100-130% | Off the top, from juggles; number not from a source read | [fd] [unverified] |
| fsmash (16%) | all | Unknown | Head intangible frames 12-16 | [wiki:Yoshi_(SSBM)/Forward_smash] |
| usmash (14%) | all | Unknown | Head intangible frames 11-15 | [wiki:Yoshi_(SSBM)/Up_smash] |
| nair (clean 14%) | all | high | Off stage | [fd] |
| dtilt (set knockback) | poor recoveries | low (gimp) | At the ledge | [wiki:Yoshi_(SSBM)/Down_tilt] |
| down B (16% ground / 14% air) | all | Unknown | Slow (hitbox from frame 27 on the ground) | [wiki:Yoshi_(SSBM)/Down_special] |

- Setups: ftilt to fair or dsmash; DJC uair juggle to uair; parry to usmash; dtilt at the
  ledge into dsmash or fair on the recovery.
- Edgeguards: dsmash and dtilt at the ledge (both semi-spikes), fair meteor off stage,
  eggs to hit recoveries and ledge stalls, turnaround double jump edgehog. Going off
  stage is costly because the double jump is his recovery.

## Recovery

- **Options:**
  - Double jump: the longest-travelling jump in the game, with armour for up to 70 frames
    and the ability to turn around [wiki:Yoshi_(SSBM)].
  - Air dodge after the jump is spent [wiki:Yoshi_(SSBM)].
  - Egg Throw: does not noticeably help recovery in Melee [wiki:Egg_Throw]; it lets Yoshi
    grab the ledge facing either way [wiki:Yoshi_(SSBM)].
  - Down B (Yoshi Bomb) can sweetspot the ledge only when facing it [wiki:Yoshi_(SSBM)].
  - Side B (Egg Roll) leaves him helpless in the air and is useless for recovery
    [wiki:Yoshi_(SSBM)].
- **Mixups:** Timing of the double jump (early and high, or late and low to the ledge);
  holding the jump until the edgeguarder commits; air dodge to ledge or onto stage after
  the jump; down B onto the ledge from above.
- **Weaknesses:** One jump. If it is used on stage, DJC'd, or broken by a hit stronger
  than the armour, he cannot return. Any aerial during the jump stops its rise
  [wiki:Yoshi_(SSBM)]. He cannot grab the ledge in the middle of an aerial
  [wiki:Yoshi_(SSBM)].

### Edgeguarding Yoshi

- Weak and medium hits do nothing during the jump, so a normal "hit him off stage"
  edgeguard fails unless the move is very strong or Yoshi is at very high percent
  [wiki:Yoshi_(SSBM)].
- Edgehog: he is "notoriously easy to edgehog" because attacking the ledge-holder costs
  him his height [wiki:Yoshi_(SSBM)]. Hold the ledge and make him land on stage, then
  punish the landing or the air dodge.
- Hit him before he double jumps (the wiki lists interrupting the jump at its start as a
  classic gimp [wiki:Gimp]) or after the 70 frames of armour run out.
- Once the jump is gone, any hit that sends him beyond air dodge range kills.
- A realistic CPU Yoshi saves the double jump as long as possible, varies its timing, and
  air dodges to the ledge.

## Defense and out of shield

- No jump out of full shield. Options are shield drop (7 frames [wiki:Shield]), roll
  (slow and short), spot dodge (decent), shield grab (active from frame 18), light shield
  to slide away, and the parry [wiki:Yoshi_(SSBM)] [wiki:Shield].
- No shieldstun: he can start those options as soon as hitlag ends [wiki:Shield].
- Double jump armour and DJC counter are his combo breakers; nair (frame 3) is the
  fastest attack.
- [Crouch cancel](../techniques/crouch-cancel.md) works well because he is heavy; dsmash
  (frame 6) and dtilt are the punishes [unverified].
- What beats him: grabs and sustained shield pressure (he must guess with roll, spot
  dodge or drop), and multi-hit or strong moves that break armour.

## As the training dummy

- Heavyweight with fast fall speed [wiki:Yoshi_(SSBM)]: stays close after launches, so he
  is comboed and chain grabbed like a fastfaller. [Sheik](sheik.md)'s dthrow chain grab
  list includes Yoshi [wiki:Chain_grab].
- A realistic CPU Yoshi double jumps out of juggles; any combo drill against him must
  either stay below the height where he can jump safely or use hits that beat the
  armour. The armour threshold itself was not found in the sources read.
- He cannot jump out of shield, so a CPU Yoshi in shield should pick from drop, roll,
  spot dodge, grab.
- Shield cannot be poked; drills about shield stabbing do not apply.
- Off stage, the CPU's stock depends on the double jump: drills should track whether it
  has been used.

## Matchup notes

### vs Fox and Falco

Fastfallers take Yoshi's best combos: utilt chains, DJC uair juggles and fair or dsmash
finishers [wiki:Yoshi_(SSBM)]. In return shine and laser pressure exploit his lack of a
jump out of shield, and both spacies can juggle and uthrow-uair him because he falls
fast [unverified].

### vs Marth

[Marth](marth.md)'s grab leads to long juggles on a heavy fastfaller and his sword
out-ranges Yoshi's pokes; Yoshi's dash grab can miss Marth because of the z-axis bug
[wiki:Yoshi_(SSBM)/Grab]. Parry and armour punishes on Marth's laggy swings are Yoshi's
way in [unverified].

### vs Sheik

[Sheik](sheik.md) chain grabs Yoshi with dthrow [wiki:Chain_grab], and her needles and
tilts are hard to armour through profitably. Yoshi must avoid shielding near her
[unverified].

### vs Peach and Jigglypuff

Against floaties utilt does not combo, so DJC nair chains carry the punish
[wiki:Double_jump_cancel]. [Jigglypuff](jigglypuff.md)'s weak aerials are easy to armour
through, but Rest punishes a spent double jump [unverified].

## Drill seeds

### Parry punish

- **id:** `yoshi-parry-punish`
- **Goal:** Time the shield press so an attack lands on the invincible startup, then
  punish.
- **Player:** Yoshi
- **CPU:** Marth (fsmash, dtilt), Fox (nair, dash attack), Sheik (ftilt), Captain Falcon
- **Setup:** Final Destination, both grounded at the CPU's attack range, 0-60%.
- **CPU behaviour:** After a random delay performs one chosen attack.
- **Success:** The attack connects during Yoshi's shield startup invincibility (no shield
  damage taken) and Yoshi hits the CPU within 20 frames.
- **Fail:** Yoshi is hit, or the attack lands on the full egg shield.
- **Variations:** Mixed attack speeds; multi-hit moves; require a jump out of the parry
  frames into a DJC nair or usmash.
- **Data needed:** Yoshi shield startup frame data (3 vs 6 frame figures need in-game
  confirmation), CPU attack hit frames, nair frame 3, usmash frame 11.

### DJC aerial chain

- **id:** `yoshi-djc-chain`
- **Goal:** Clean DJC timing with fast fall and L-cancel.
- **Player:** Yoshi
- **CPU:** Fox, Falco (uair chains); Peach, Jigglypuff (nair chains)
- **Setup:** CPU standing at centre stage at 10-40%; Yoshi adjacent.
- **CPU behaviour:** Random DI; shields or attacks when actionable.
- **Success:** N aerial hits (start with 3) with no CPU action between them, finished by
  fair, dsmash or uair.
- **Fail:** Yoshi lands without a hitbox (DJC too fast), rises into a full double jump
  (too slow), or the CPU escapes.
- **Variations:** Start from utilt on fastfallers; start from ftilt; near the edge with a
  fail if Yoshi leaves the stage without a jump.
- **Data needed:** Aerial startups and landing lag, jump squat, double jump rise profile,
  CPU weight and fall speed.

### Armour counter

- **id:** `yoshi-djc-counter`
- **Goal:** Absorb an aerial or anti-air with double jump armour and counter.
- **Player:** Yoshi
- **CPU:** Fox, Falco, Marth, Sheik, Peach
- **Setup:** Yoshi airborne from a short hop toward the CPU, 0-50%.
- **CPU behaviour:** Attacks Yoshi with a random move from a list that does not break
  armour at that percent; occasionally grabs or waits instead.
- **Success:** Yoshi is hit during the double jump without being launched and lands
  nair, uair or Egg Lay within 15 frames after hitlag.
- **Fail:** Yoshi is launched, or burns the jump with no hit.
- **Variations:** Raise Yoshi's percent to find where each move starts breaking armour;
  include strong moves the player must avoid instead.
- **Data needed:** Armour threshold, knockback of each CPU move at each percent, 70-frame
  armour duration.

### Recovery with one jump

- **id:** `yoshi-recovery`
- **Goal:** Recover using double jump timing and air dodge against an edgeguarder.
- **Player:** Yoshi
- **CPU:** Marth, Sheik, Fox, Captain Falcon
- **Setup:** Yoshi in tumble off stage at varying distance, double jump available,
  60-140%.
- **CPU behaviour:** Randomly edgehogs, swings a strong move at the ledge, or jumps out
  with an aerial.
- **Success:** Yoshi reaches the ledge or stage and is not hit out of it for 60 frames.
- **Fail:** Stock lost.
- **Variations:** Start with the jump already used (air dodge only); higher percent so
  armour breaks.
- **Data needed:** Double jump distance and height, air dodge distance, armour threshold,
  CPU move knockback.

### Shield escape without a jump

- **id:** `yoshi-shield-escape`
- **Goal:** Learn the legal escapes from pressure on the egg shield.
- **Player:** Yoshi
- **CPU:** Fox, Falco, Sheik, Marth
- **Setup:** Yoshi in full shield at centre stage; CPU adjacent.
- **CPU behaviour:** Aerial on shield followed by a random follow-up: grab, shine or jab,
  second aerial, or wait.
- **Success:** Yoshi leaves shield without being hit or grabbed, or punishes (shield
  grab, spot dodge to dsmash, light shield slide to safety).
- **Fail:** Hit, grabbed, or shield broken.
- **Variations:** On a platform (shield drop through); near the ledge.
- **Data needed:** No shieldstun rule, shield drop 7 frames, roll and spot dodge frame
  data, CPU pressure timings.

### Down tilt tech chase

- **id:** `yoshi-dtilt-techchase`
- **Goal:** Convert the 0% knockdown.
- **Player:** Yoshi
- **CPU:** Any; most valuable against Fox, Falco, Marth, Sheik
- **Setup:** CPU at 0% standing in dtilt range at centre stage.
- **CPU behaviour:** After being hit: tech in place, tech left, tech right, or missed
  tech with a random get-up.
- **Success:** Yoshi hits the CPU (dsmash, ftilt, grab, jab reset then smash) before it
  can act.
- **Fail:** CPU acts first.
- **Variations:** Near the edge (dtilt sends off stage: edgeguard instead); higher
  percents.
- **Data needed:** Dtilt set knockback 100 at angle 28, total 23 frames, CPU tech
  distances and timings.

### Egg Lay on shield

- **id:** `yoshi-egg-lay-shield`
- **Goal:** Use the command grab against a shielding opponent.
- **Player:** Yoshi
- **CPU:** Marth, Sheik, Peach, Fox
- **Setup:** CPU shielding; Yoshi at short hop range.
- **CPU behaviour:** Holds shield, then randomly shield grabs, rolls or attacks out of
  shield after Yoshi's first aerial.
- **Success:** Egg Lay connects; bonus score for damage dealt to the egg before break-out.
- **Fail:** Yoshi whiffs and is punished.
- **Variations:** From a DJC nair on shield; aerial Egg Lay.
- **Data needed:** Egg Lay grab frames 17-21 and total 39, egg duration 200 frames and
  mash rules.

### Edge-canceled egg stall

- **id:** `yoshi-ece`
- **Goal:** Repeat the ledge egg stall without dying.
- **Player:** Yoshi
- **CPU:** None, or a CPU standing near the ledge as a target
- **Setup:** Yoshi hanging on the ledge.
- **CPU behaviour:** None, or walks toward the ledge.
- **Success:** N consecutive cycles of drop, double jump, Egg Throw, regrab.
- **Fail:** Yoshi lands on stage, rises above the ledge, or falls.
- **Variations:** Reverse version; aim eggs at a target.
- **Data needed:** Ledge regrab timing, Egg Throw animation (54 frames), double jump
  profile.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlYs.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/yoshi.json`](../framedata/yoshi.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 3-5 | 3 | Sakurai | 8 | 50 | - |  | 17 | - | 3 | -11 |  |
| Jab 2 | `jab2` | 4-6 | 5 | Sakurai | 8 | 120 | - |  | 20 | - | 4 | -12 | starts 1 frame late (included) |
| Dash attack | `dash_attack` | 10-13 | 9 | Sakurai | 15 | 100 | - |  | 43 | 42 | 6 | -25 | partly intangible 5-13 (1 bone) |
|  |  | 14-23 | 8 | Sakurai | 15 | 100 | - |  |  |  | 5 | -22 |  |
| Forward tilt (angled up) | `ftilt_high` | 6-8 | 13 | 80/70/60 | 40 | 80 | - |  | 29 | - | 7 | -16 |  |
| Forward tilt (slightly up) | `ftilt_mid_high` | 6-8 | 13 | 80/70/60 | 40 | 80 | - |  | 29 | - | 7 | -16 |  |
| Forward tilt | `ftilt` | 6-8 | 12 | 80/70/60 | 40 | 80 | - |  | 29 | - | 7 | -16 |  |
| Forward tilt (slightly down) | `ftilt_mid_low` | 6-8 | 12 | 80/70/60 | 40 | 80 | - |  | 29 | - | 7 | -16 |  |
| Forward tilt (angled down) | `ftilt_low` | 6-8 | 11 | 80/70/60 | 40 | 80 | - |  | 29 | - | 6 | -17 |  |
| Up tilt | `utilt` | 8-12 | 10 | 100 | 72 | 40 | - |  | 29 | - | 6 | -15 |  |
| Down tilt | `dtilt` | 8-10 | 10 | 28 | 0 | 100 | 100 |  | 23 | - | 6 | -9 |  |
| Forward smash (angled up) | `fsmash_high` | 14-16 | 16 | Sakurai | 32 | 94 | - |  | 47 | 44 | 9 | -20 | charge hold frame 6; partly intangible 12-16 (1 bone) |
| Forward smash | `fsmash` | 14-16 | 16 | Sakurai | 32 | 94 | - |  | 47 | 44 | 9 | -20 | charge hold frame 6; partly intangible 12-16 (1 bone) |
| Forward smash (angled down) | `fsmash_low` | 14-16 | 16 | Sakurai | 32 | 94 | - |  | 47 | 44 | 9 | -20 | charge hold frame 6; partly intangible 12-16 (1 bone) |
| Up smash | `usmash` | 11-15 | 14 | 75 | 26 | 108 | - |  | 43 | 40 | 8 | -20 | charge hold frame 6; partly intangible 11-15 (2 bones) |
| Down smash | `dsmash` | 6-8 | 14 | 30 | 50 | 75/60 | - |  | 49 | - | 8 | -35 | charge hold frame 4 |
|  |  | 21-22 | 12 | 30 | 50 | 75/80 | - |  |  |  | 7 | -21 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 3-6 | 14 | Sakurai | 15 | 100 | - |  | 47 | 45 | 8 | 15 | 7 | <3, >35 | +1 |  |
|  |  | 7-33 | 10 | Sakurai | 0 | 100 | - |  |  |  | 6 |  |  |  | -1 |  |
| Forward air | `fair` | 19-21 | 17 | 270 | 30 | 100 | - |  | 49 | 44 | 9 | 21 | 10 | <4, >35 | -1 |  |
| Back air | `bair` | 10-12 | 7 | 60 | 10 | 100 | - |  | 39 | 38 | 5 | 15 | 7 | <10, >32 | -2 |  |
|  |  | 16-18 | 6 | 60 | 10 | 100 | - |  |  |  | 4 |  |  |  | -3 |  |
|  |  | 23-25 | 5 | 60 | 10 | 100 | - |  |  |  | 4 |  |  |  | -3 |  |
|  |  | 28-30 | 4 | 60 | 40 | 100 | - |  |  |  | 3 |  |  |  | -4 |  |
| Up air | `uair` | 5-6 | 13 | 90 | 25 | 100 | - |  | 39 | 39 | 7 | 19 | 9 | <5, >32 | -2 |  |
| Down air | `dair` | 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44 | 4 | 270 | 5 | 90 | - |  | 59 | 56 | 3 | 26 | 13 | <16, >55 | -10 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 18-23 | 79 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 11-16 | 70 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 10 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 6 | 6 | 45 | 40 | 66 | - | - | 19 | 39 |  |
| Back throw | `bthrow` | 6 | 6 | 45 | 40 | 66 | - | - | 19 | 43 |  |
| Up throw | `uthrow` | 5 | 5 | 90 | 65 | 43 | - | - | 12 | 43 |  |
| Down throw | `dthrow` | 4 | 4 | 80 | 120 | 20 | - | - | 14 | 43 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Egg Lay, ground, 1 | `special_n1` | 17, 18-21 | 1 | Sakurai | 0 | 100 | - | grab | 39 | - | 2 | - |  |
| Neutral B: Egg Lay, ground, 1 | `special_n1_296` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Neutral B: Egg Lay, ground, 2 | `special_n2` | - | - | - | - | - | - | - | 29 | - | - | - | invincible 6-29 |
| Neutral B: Egg Lay, air, 1 | `special_air_n1` | 17, 18-21 | 1 | Sakurai | 0 | 100 | - | grab | 39 | - | 2 | - |  |
| Neutral B: Egg Lay, air, 1 | `special_air_n1_299` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Neutral B: Egg Lay, air, 2 | `special_air_n2` | - | - | - | - | - | - | - | 29 | - | - | - | invincible 6-29 |
| Side B: Egg Roll, ground, Start | `special_s_start` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Side B: Egg Roll, ground, Loop | `special_s_loop` | 1-59 | 4 | 80 | 43 | 70 | - |  | 59 | - | 3 | - |  |
| Side B: Egg Roll, ground, Loop | `special_s_loop_303` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Side B: Egg Roll, ground, End | `special_s_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Side B: Egg Roll, air, Start | `special_air_s_start` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Side B: Egg Roll, ground, Loop | `special_s_loop_306` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Side B: Egg Roll, ground, Loop | `special_s_loop_307` | 1-59 | 4 | 80 | 43 | 70 | - |  | 59 | - | 3 | - |  |
| Side B: Egg Roll, air, End | `special_air_s_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Up B: Egg Throw, ground | `special_hi` | - | - | - | - | - | - | - | 54 | - | - | - | spawns article/projectile on 3 |
| Up B: Egg Throw, air | `special_air_hi` | - | - | - | - | - | - | - | 54 | - | - | - | spawns article/projectile on 3 |
| Down B: Yoshi Bomb, ground | `special_lw` | 27 | 16 | 80 | 50 | 98 | - |  | 27 | - | 9 | - |  |
| Down B: Yoshi Bomb, ground, Landing | `special_lw_landing` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Down B: Yoshi Bomb, air | `special_air_lw` | 19 | 14 | 80 | 46 | 96 | - |  | 19 | - | 8 | - |  |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-15 | - | 22 | 20 |  |
| Roll forward | `roll_forward` | intangible 4-19 | - | 34 | - |  |
| Roll backward | `roll_backward` | intangible 4-19 | - | 37 | - |  |
| Air dodge | `airdodge` | intangible 4-29 | - | 49 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-20 | 13-14, 19-20 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-24 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-26 | 14-15, 25-26 (6%) | 49 | - |  |
| Getup roll forward (face down) | `getup_roll_forward_facedown` | intangible 1-14 | - | 35 | - |  |
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-29 | - | 35 | - |  |
| Tech in place | `tech_in_place` | intangible 2-20 | - | 26 | - | starts 1 frame late (included) |
| Tech roll forward | `tech_roll_forward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Tech roll backward | `tech_roll_backward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Wall tech | `wall_tech` | - | - | 26 | - | starts 1 frame late (included) |
| Wall tech jump | `wall_tech_jump` | - | - | 40 | - | starts 1 frame late (included) |
| Ceiling tech | `ceiling_tech` | intangible 2-14 | - | 26 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-55 | - | 59 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 33 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-29 | 33-37 (12%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-15 | 19-23 (6%) | 55 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-69 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-23 | - | 49 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-25 | - | 25 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 22 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-13 | - | 13 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 24 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Neutral air | jump | 8 | `nair` |
| Up air | jump | 10 | `uair` |
| Up smash | jump cancel | 12 | `usmash` |
| Back air | jump | 15 | `bair` |
| Shield grab | direct | 18 | `grab` |
| Down air | jump | 23 | `dair` |
| Forward air | jump | 24 | `fair` |
| Spot dodge | direct | intangible 2-15 of 22 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 34 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 37 | `roll_backward` |
| Wavedash | jump | actionable on frame 17 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Yoshi indexed by [The Melee Library](https://www.meleelibrary.com/#yoshi) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Yoshi Melee Techs Guide](https://www.youtube.com/watch?v=h0ZlkLRLsl0&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=18&t=0s) | Third Chair | Video guide on performing useful Yoshi tech in 2020. |
| [How To Hatch a Healthy Yoshi: A Beginner Guide](http://smashboards.com/threads/how-to-hatch-a-healthy-yoshi-a-yoshi-guide.53132/) | BringerOfDeath | An old (2005) thread. Can be used as a starting guide, but remember that some of the info here might be outdated. |
| [Project: Y.O.S.H.I.](http://smashboards.com/threads/project-y-o-s-h-i-updated-11-06-2006-reference-threads-added.73030/) | Shiri | An old Yoshi guide with information that is still relevant. There is also a breakdown of game a few essential mechanics. He calls parrying supershielding. |
| [Yoshi Hitboxes and Frame Data](http://smashboards.com/threads/yoshi-hitboxes-and-frame-data.317467/) | Stratocaster, Standardtoaster, and SuperDoodleMan | Shows gifs of all of Yoshi’s moves displaying hitboxes and hurtboxes. Also lists frame data on each move. |
| [Some Yoshi Information](http://smashboards.com/threads/some-yoshi-information.351635/) | PerhapsMan | A thread of useful Yoshi frame data and other information like combo options. |
| [Ask VMan about Yoshi Thread (A General Yoshi Discussion)](http://smashboards.com/threads/ask-vman-about-yoshi-thread-a-general-yoshi-discussion.281379/) | lots of people | A great thread to search for common questions and answers by the great Yoshi players. |
| [Frame Data on Yoshi’s Shield](http://smashboards.com/threads/frame-research-yoshis-parry.262911/#post-9415501) | Magus | Yoshi’s shield is weird and different. |
| [Yoshi Skill Videos](https://www.youtube.com/playlist?list=PLssBmYCAcRdl7KiRoVI4cz6M6FY4AQwmE) | aMSa | Playlist of videos by aMSa demonstrating various weird Yoshi things. |
| [Yoshi Trials](https://www.youtube.com/playlist?list=PLM-vPXW2t8A1rzwBW9lMJSxMHylAWRUjr) | PerhapsMan | “A series of four Street Fighter style trial videos, to be used by new Yoshi players as a learning tool. The videos focus on different elements of Yoshi tech skill.” |
| [Melee Is a 3D Game: Yoshi’s Grab](https://www.youtube.com/watch?v=eWO6iDefd-g) | Axe | Axe explains why Yoshi's grab seems to miss randomly sometimes. |
| [Yoshi ECE from Pokemon Stadium Rock Transformation Lip](http://smashboards.com/threads/brand-new-tech-yoshi-ece-from-pokemon-stadiums-lip.433723/) | community |  |
| [Physical Powershield Storing](https://smashboards.com/threads/some-yoshi-information.351635/page-9#post-21400329) | tauKhan |  |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Yoshi (SSBM): https://www.ssbwiki.com/Yoshi_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Yoshi_(SSBM)/Down_tilt , /Down_smash ,
  /Forward_smash , /Up_smash , /Forward_tilt , /Up_tilt , /Neutral_aerial ,
  /Forward_aerial , /Back_aerial , /Up_aerial , /Down_aerial , /Grab , /Down_special
- SSBWiki, Double jump cancel: https://www.ssbwiki.com/Double_jump_cancel
- SSBWiki, Double jump cancel counter: https://www.ssbwiki.com/Double_jump_cancel_counter
- SSBWiki, Double jump: https://www.ssbwiki.com/Double_jump
- SSBWiki, Armor: https://www.ssbwiki.com/Armor
- SSBWiki, Shield (Yoshi section): https://www.ssbwiki.com/Shield
- SSBWiki, Perfect shield: https://www.ssbwiki.com/Perfect_shield
- SSBWiki, Egg Lay: https://www.ssbwiki.com/Egg_Lay
- SSBWiki, Egg Throw (edge-canceled eggs): https://www.ssbwiki.com/Egg_Throw
- SSBWiki, Lock, Gimp, Moonwalk, Meteor smash, Chain grab: https://www.ssbwiki.com/Lock ,
  https://www.ssbwiki.com/Gimp , https://www.ssbwiki.com/Moonwalk ,
  https://www.ssbwiki.com/Meteor_smash , https://www.ssbwiki.com/Chain_grab
- Melee Library, Yoshi section (card titles and descriptions only; Smashboards links
  returned errors and videos cannot be watched).
- Frame data dump: `Yoshi.json`.
