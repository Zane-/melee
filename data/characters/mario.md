---
schema: melee-character/v1
id: mario
name: Mario
aliases: [Mario Mario, the plumber]
tier: "C+ (15th of 26), 2021 tier list"
archetype: [mixup, edgeguarder, projectile, chaingrab, punish-heavy]
related: [dr-mario, luigi]
summary: Mario wins with fast low-knockback aerials and throws that string into long combos, then takes the stock with a cape, back air or back throw edgeguard because he has few raw kill moves.
key_tech: [cape-edgeguard, cape-stall, up-b-wall-jump, up-b-out-of-shield, throw-chain-grab, dair-landing-hit, uair-aerial-interrupt, fireball-waveland, tornado-rise]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlMr.dat
framedata: ../framedata/mario.json
code: src/melee/ft/kinds/ftMario
specials:
  neutral_b: "Fireball"
  side_b: "Cape"
  up_b: "Super Jump Punch"
  down_b: "Mario Tornado"
attributes:
  weight: 100
  gravity: 0.095
  fall_speed: 1.7
  fast_fall_speed: 2.3
  jump_squat: 4
  jumps: 2
  walk_speed: 1.1
  dash_speed: 1.5
  run_speed: 1.5
  traction: 0.06
  air_speed: 0.86
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [2, 16, 3]
  jab2: [3, 19, 2]
  jab3: [5, 23, 5]
  dash_attack: [6, 38, 9]
  ftilt_high: [5, 33, 10]
  ftilt: [5, 33, 9]
  ftilt_low: [5, 33, 8]
  utilt: [4, 30, 8]
  dtilt: [5, 35, 9]
  fsmash_high: [12, 42, 19]
  fsmash: [12, 42, 18]
  fsmash_low: [12, 42, 17]
  usmash: [9, 40, 15]
  dsmash: [5, 38, 16]
  nair: [3, 46, 12]
  fair: [18, 60, 15]
  bair: [6, 29, 11]
  uair: [4, 30, 11]
  dair: [10, 38, 2]
  grab: [7, 31, 0]
  dash_grab: [11, 41, 0]
  pummel: [17, 25, 3]
  fthrow: [null, 28, 9]
  bthrow: [null, 67, 12]
  uthrow: [null, 40, 8]
  dthrow: [null, 40, 6]
  special_n: [null, 44, 0]
  special_air_n: [null, 44, 0]
  special_s: [12, 36, 10]
  special_s_air: [12, 36, 9]
  special_hi: [3, 38, 5]
  special_air_hi: [3, 38, 5]
  special_lw: [8, 80, 5]
  special_air_lw: [8, 80, 3]
oos:  # option: frame the hitbox is out
  special_hi: 4
  nair: 7
  grab: 7
  uair: 8
  bair: 10
  usmash: 10
  dair: 14
  fair: 22
resources: 11
# generated: end
---

# Mario

<!-- GENERATED:attributes -->
## Attributes

Read from `PlMr.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 100 |
| Gravity | 0.095 |
| Terminal fall speed | 1.7 |
| Fast-fall speed | 2.3 |
| Jump squat (frames before airborne) | 4 |
| Full hop / short hop initial Y speed | 2.3 / 1.4 |
| Air jump Y multiplier | 1 |
| Jumps | 2 |
| Walk max speed | 1.1 |
| Dash initial speed / run max speed | 1.5 / 1.5 |
| Ground friction (traction) | 0.06 |
| Air max horizontal speed | 0.86 |
| Air acceleration (base + stick) | 0.02 + 0.025 |
| Air friction | 0.016 |
| Normal landing lag | 4 |
| Shield size | 10.75 |
<!-- /GENERATED:attributes -->

## Overview

Mario is the all-rounder: middle of the cast in weight, fall speed, air speed and dash speed
[wiki:Mario_(SSBM)]. He has no standout strength in neutral. He approaches with fireballs
(neutral B), a long floaty [wavedash](../techniques/wavedash.md) and
[SHFFL](../techniques/shffl.md)ed aerials, and he converts hits into juggles with up tilt, up
air and up throw. His problem is ending stocks: most of his moves are weak combo tools, his
forward smash only kills from the fire sweetspot at the end of the arm, and his back throw
needs position near the edge [wiki:Mario_(SSBM)]. Most Mario kills are edgeguards, built on
the cape (side B), which turns a recovering opponent around so that they cannot grab the ledge.
He dies to being outranged by swords and to edgeguards on his short, predictable up B. Mario is
not hard to pick up, but his best recovery technique (up B wall jump) is one of the hardest
inputs in the game [wiki:Mario_(SSBM)]. He is generally considered slightly worse than his
clone [Dr. Mario](dr-mario.md), who trades combo ease for kill power [wiki:Mario_(SSBM)].

## Strengths and weaknesses

- **Strengths:**
  - Fast, low-lag aerials: nair hits on frame 3, up air on frame 4, bair on frame 6 [fd];
    L-cancelled landing lag is 7-8 frames for nair, bair and up air [fd].
  - Up tilt (frame 4, launches at 96°) and up air (55°, no base knockback) juggle well [fd].
  - Throws that combo: up throw [chain grabs](../techniques/chain-grab.md) fastfallers, down
    throw chain grabs heavies, Pikachu and Pichu [wiki:Mario_(SSBM)].
  - Cape: reverses any opponent it touches, reflects projectiles, and stalls Mario in the air.
  - Up B hits on frame 3 and is intangible on frames 3-6 [wiki:Mario_(SSBM)/Up_special]: a
    very fast [out of shield](../techniques/out-of-shield.md) option.
  - Can wall jump, including out of his up B.
- **Weaknesses:**
  - Few kill moves. Up smash, down smash and aerials are weak; forward smash needs the tip.
  - Short reach on normals and a poor grab range [wiki:Mario_(SSBM)].
  - Recovery is short and linear; one edgehog or a hit during up B usually ends it.
  - Fireballs are weak (6% [wiki:Mario_(SSBM)]) and do not force approaches the way Dr.
    Mario's pills do.

## Character tech

### Cape edgeguard

- **id:** `cape-edgeguard`
- **What:** Side B (Cape) deals damage but no knockback and flips the target to face the other
  way without interrupting their animation [wiki:Cape]. A recovering opponent who is flipped
  travels or faces the wrong way and cannot grab the ledge, because in Melee a character must
  face the ledge to grab it during most up specials.
- **Inputs:** Stand at the ledge (or jump/drop just offstage), side B toward the opponent so
  the cape overlaps them as they travel toward the ledge.
- **Timing:** Cape hitbox is active on frames 12-14 and the whole move lasts 35 frames
  [wiki:Mario_(SSBM)/Side_special]. The reflector is active frames 6-33
  [wiki:Mario_(SSBM)/Side_special]. Mario's cape has no hitbox behind him; Dr. Mario's sheet
  does on frames 14-15 [lib:Doc Advanced Tech Frame Data Megathread].
- **Used for:** Gimping linear recoveries. The wiki singles out [Fox](fox.md)'s up B (Fire Fox)
  and [Luigi](luigi.md)'s side B (Green Missile) [wiki:Mario_(SSBM)]. Also works on
  [Captain Falcon](captain-falcon.md), [Ganondorf](ganondorf.md), [Marth](marth.md),
  [Sheik](sheik.md) and other Marios. Also reflects projectiles at 1.5x damage
  [wiki:Mario_(SSBM)/Side_special].
- **Common errors:** Caping too early (12 frames of startup means the opponent arrives after
  the 3 active frames); caping an opponent whose attack hitbox is out (the cape does not stop
  the attack, so Mario still gets hit [wiki:Cape]); caping a recovery that is already past the
  point where it snaps to the ledge.
- **Drill idea:** CPU Fox recovers with up B from random angles below/level with the ledge;
  success when Fox is hit by the cape and dies without grabbing the ledge or landing.

### Cape stall

- **id:** `cape-stall`
- **What:** The first aerial cape after leaving the ground halts Mario's fall and gives a
  small rise, which adds recovery distance and changes his timing.
- **Inputs:** Side B in the air, once per airtime.
- **Timing:** The stall covers roughly frames 12-34 of the cape; Dr. Mario's lasts only frames
  12-15 [wiki:Dr._Mario_(SSBM)]. The rising cape is only restored by a normal landing, a
  special-fall landing (air dodge, wavedash, up B) or landing during a cape; landing during
  an aerial or fireball, or a normal ledge get-up, does not restore it
  [lib:Doc Advanced Tech Frame Data Megathread].
- **Used for:** Extending recovery, delaying to bait an edgeguard, turning around in the air.
- **Common errors:** Using a second cape and expecting a second stall; starting the cape so low
  that the up B afterward cannot reach.
- **Drill idea:** Start Mario offstage at a distance where jump + up B alone falls short;
  success when he grabs the ledge using jump, cape, then up B.

### Up B wall jump

- **id:** `up-b-wall-jump`
- **What:** Mario's up B (Super Jump Punch) is the only up special in Melee that can be
  cancelled by a [wall jump](../techniques/wall-jump.md), after which he can up B again
  [wiki:Mario_(SSBM)/Up_special].
- **Inputs:** Hug a wall, up B, then tap the control stick away from the wall near the apex.
- **Timing:** With the up B started against the wall: wall jump window is frames 23-29 with no
  angle (earliest jump frame 25), 22-29 for a diagonal angle (earliest 24), 21-29 for the most
  horizontal angle (earliest 23), and 25-29 for the fully extended angle (earliest 27). Inputs
  inside the window but before the earliest frame are buffered
  [wiki:Mario_(SSBM)/Up_special]. If the up B is not started against the wall the window is
  smaller or absent [wiki:Mario_(SSBM)/Up_special].
- **Used for:** Recovering from far below the ledge on stages with a wall under the ledge (the
  wiki names Yoshi's Story) [wiki:Super_Jump_Punch]. It does not work on every wall
  [wiki:Super_Jump_Punch].
- **Common errors:** Tapping away too late (Mario enters special fall and dies); starting the
  up B a little off the wall.
- **Drill idea:** Place Mario below the ledge against the stage wall with no double jump;
  success when a wall jump occurs during up B and he reaches the ledge.

### Up B out of shield

- **id:** `up-b-out-of-shield`
- **What:** Jump-cancelled up B from shield as a fast punish for attacks on shield.
- **Inputs:** While shielding, press up (tap jump) and B on the next frame.
- **Timing:** Up B hits on frame 3 and Mario is intangible frames 3-6
  [wiki:Mario_(SSBM)/Up_special]. In Melee an up special cannot start on the first jumpsquat
  frame [wiki:Super_Jump_Punch], so the earliest hit from shield is frame 4 (the same
  arithmetic is shown frame by frame for Dr. Mario in
  [lib:Up-B Cancel Frame and Hitbox Data]). Total damage about 12-14% if all hits connect
  [wiki:Super_Jump_Punch].
- **Used for:** Punishing unsafe aerials and grabs on shield, escaping
  [shield pressure](../techniques/shield-pressure.md).
- **Common errors:** Late input (jump comes out, aerial up B has the same startup but Mario
  leaves the ground first); using it against spaced attacks, after which Mario lands in
  special fall and is punished.
- **Drill idea:** CPU does an unsafe aerial on Mario's shield; success when up B hit 1 connects
  within 6 frames of shield stun ending.

### Throw chain grabs

- **id:** `throw-chain-grab`
- **What:** Up throw re-grabs on [Fox](fox.md), [Falco](falco.md) and
  [Captain Falcon](captain-falcon.md); down throw re-grabs on heavy characters and on
  [Pikachu](pikachu.md) and [Pichu](pichu.md) "up to high percents"; at high percents down
  throw also re-grabs fastfallers [wiki:Mario_(SSBM)].
- **Inputs:** Grab, throw, follow the opponent's DI (directional influence, holding a
  direction to bend the launch angle) with a walk, dash, pivot or
  [jump-cancelled](../techniques/jump-cancel.md) grab, repeat.
- **Timing:** Up throw releases on frame 18 of a 39-frame animation against a baseline-weight
  opponent; throw speed depends on the victim's weight [wiki:Mario_(SSBM)/Up_throw]. Mario's
  throws have lower knockback growth than Dr. Mario's (up throw 72 vs 80, down throw 30 vs 40
  [wiki:Dr._Mario_(SSBM)]), so the opponent stays close for longer; exact Mario percent
  windows: Unknown. Dr. Mario's measured windows are in [dr-mario.md](dr-mario.md) and are a
  conservative guide.
- **Used for:** Damage from 0% on fastfallers, then a finisher (up tilt, up air strings,
  forward smash, or a throw offstage).
- **Common errors:** Grabbing facing the wrong way when the opponent DIs behind; re-grabbing
  too early (grab whiffs under the falling opponent).
- **Drill idea:** CPU Fox at 0% with randomised DI on each throw; count consecutive up throw
  re-grabs with no jump-out.

### Down air landing hit

- **id:** `dair-landing-hit`
- **What:** Mario's dair (drill kick) has a weak landing hitbox that Dr. Mario's lacks. It
  pops the opponent up slightly next to Mario, who is actionable quickly after an
  [L-cancel](../techniques/l-cancel.md).
- **Inputs:** Short hop, dair, land on or next to the opponent, L-cancel.
- **Timing:** Drill hits on frames 10-29 in 2-frame pulses; landing hitbox is active on
  landing frames 1-2 (frame 1 only when L-cancelled); landing lag 23 frames, 11 L-cancelled
  [wiki:Mario_(SSBM)/Down_aerial]. The landing hit has set knockback
  [lib:Full list of differences between Mario and Dr. Mario].
- **Used for:** Starting a grab, up tilt or up smash combo from a safe-ish aerial.
- **Common errors:** Missing the L-cancel (23 frames of lag loses the follow-up).
- **Drill idea:** Stationary CPU; success when the landing hit connects and a grab or up tilt
  connects before the CPU can act.

### Up air aerial interrupt

- **id:** `uair-aerial-interrupt`
- **What:** Using up air while rising through a platform makes Mario land on the platform
  with the aerial cancelled, optionally after the first hitbox frame has come out
  [lib:Doc Advanced Tech Frame Data Megathread].
- **Inputs:** Full hop under a platform, up air at the frame where his body crosses it,
  L-cancel.
- **Timing:** Documented frame by frame for Dr. Mario (up air on airborne frame 13 from a full
  hop under a low Battlefield platform); Mario's version works the same way but must be input
  2 frames earlier [lib:Doc Advanced Tech Frame Data Megathread]. Mario can also
  platform-cancel nair, which Dr. Mario cannot [lib:Doc Advanced Tech Frame Data Megathread].
- **Used for:** Fast platform landings that hit an opponent standing or teching on the
  platform; platform [tech chases](../techniques/tech-chase.md).
- **Common errors:** One frame early gives the interrupt with no hitbox; late gives a normal
  rising up air.
- **Drill idea:** CPU shields on a Battlefield side platform; success when Mario lands on the
  platform within N frames of jumping and the up air hitbox touched the CPU.

### Fireball waveland

- **id:** `fireball-waveland`
- **What:** Throw a fireball during a full hop and still land with a
  [waveland](../techniques/waveland.md) or an aerial, so Mario moves in behind his projectile.
- **Inputs:** Full hop, neutral B early, air dodge diagonally into the ground on landing.
- **Timing:** Documented for Dr. Mario's pill and stated to work identically for Mario: the
  projectile leaves on frame 14 of a 43-frame move; a full hop gives 52 airborne frames, so
  there are about 9 spare frames [lib:Doc Advanced Tech Frame Data Megathread].
- **Used for:** Approaching behind a fireball, covering a landing.
- **Common errors:** Throwing the fireball too late in the jump and landing in the special's
  animation.
- **Drill idea:** Success when a fireball is released and Mario is grounded and actionable
  within a set frame budget after jumping.

### Tornado rise

- **id:** `tornado-rise`
- **What:** Mashing B during an aerial down B (Mario Tornado) makes Mario rise; it works once
  per airtime [wiki:Mario_(SSBM)].
- **Inputs:** Down B in the air, then press B repeatedly; each press needs at least one
  released frame before the next.
- **Timing:** Documented for Dr. Mario and stated to be identical for Mario: presses count
  from frame 1 up to frame 38; 6 evenly spread presses already give useful height and 18 is
  the maximum; Mario can act again on frame 80
  [lib:Doc Advanced Tech Frame Data Megathread].
- **Used for:** Extra recovery height and stalling.
- **Common errors:** Bunching the presses at the start (even spacing matters more than count).
- **Drill idea:** Count B presses registered in frames 1-38 and report height gained.

## Neutral game

- Fireballs to make the opponent shield or jump, then move in behind them with a wavedash or
  a short hop aerial. Fireballs travel faster and flatter than Dr. Mario's pills and are
  better for covering Mario's own high recovery [wiki:Dr._Mario_(SSBM)].
- [Dash dance](../techniques/dash-dance.md) and wavedash to bait a whiff, then grab or SHFFL
  nair/bair. The dump lists the standing grab box on frames 6-7 [fd]; for other characters
  the dump's grab frames are one earlier than SSBWiki's, so treat this as frame 7-8 until
  checked.
- Forward tilt (frame 5 [fd]) and the tip of forward smash as mid-range pokes. The forward
  smash fire sweetspot has transcendent priority (it does not clank)
  [wiki:Mario_(SSBM)/Forward_smash].
- Up tilt as an anti-air and combo starter.
- Mario wants a grab or a launcher; he does not want to trade pokes with swords.

## Punish game

Mario's punishes are strings of weak hits. Launch with up throw, up tilt or down throw, juggle
with up tilt and up air while following DI, and end either with a hit that sends the opponent
offstage (bair, forward smash, back throw) or with a re-grab.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| Up throw | Fox, Falco, Captain Falcon | low to mid, exact range Unknown | Re-grab, repeat | Chain grab; follow DI | [wiki:Mario_(SSBM)] |
| Up throw | most | low | Up tilt | Wiki: "good for leading into an up tilt" | [wiki:Mario_(SSBM)] |
| Down throw | Pikachu, Pichu, heavy characters | low to mid ("up to high percents" on Pikachu/Pichu) | Re-grab | | [wiki:Mario_(SSBM)] |
| Down throw | fastfallers | high | Re-grab | | [wiki:Mario_(SSBM)] |
| Up tilt | most | low | Up tilt, up air | Juggle | [wiki:Mario_(SSBM)] |
| Fair (meteor) onstage | grounded opponent | mid | Forward smash or up smash | Fair bounces them up | [wiki:Mario_(SSBM)] |
| Dair landing hit | most | typical low-mid | Grab, up tilt, up smash | Needs L-cancel | [lib:Mario Dair Tutorial] (title only) |
| Lemon grab bair | Falco | 40-60%, no DI (measured for Dr. Mario) | Dash attack, turn, fall, bair | "Janky gimp" | [lib:Doc Advanced Tech Frame Data Megathread] |

### Chain grabs and tech chases

- Up throw on Fox, Falco and Captain Falcon; down throw on heavies, Pikachu and Pichu
  [wiki:Mario_(SSBM)]. Exact Mario windows were not found. Dr. Mario's measured windows
  (see [dr-mario.md](dr-mario.md)) should be a lower bound because Mario's throws send less
  far at the same percent.
- The opponent escapes by DI behind Mario combined with a late re-grab (jump out), or by
  reaching a platform and [teching](../techniques/teching.md).
- Down throw at low percent on characters that land before Mario can re-grab becomes a tech
  chase: cover tech in place with grab or down smash, tech away with dash attack or
  wavedash forward smash.

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Forward smash (fire sweetspot) | most | about 70% when fully charged and angled up; uncharged Unknown | Must hit with the flame, not the arm | [wiki:Mario_(SSBM)/Forward_smash] |
| Back throw | most | under 150% | Near the edge | [wiki:Mario_(SSBM)] |
| Cape | linear recoveries | any | Offstage, opponent must be mid-recovery | [wiki:Mario_(SSBM)] |
| Fair (meteor) | most | any, offstage | Hits frames 18-22, 280° [fd]; can be [meteor cancelled](../techniques/meteor-cancel.md) | [wiki:Mario_(SSBM)/Forward_aerial] |
| Up tilt | most | very high | | [wiki:Mario_(SSBM)] |
| Bair | most | Unknown | Offstage edgeguard hit | [wiki:Mario_(SSBM)] |

- Edgeguard tools in order of use: grab the ledge (edgehog), cape, ledge-hop bair, fireballs
  thrown down at the recovery, up air against opponents level or above
  [wiki:Mario_(SSBM)].
- Forward and back throw at the edge at any percent to start an edgeguard.
- Fair offstage is risky: 74 frames long with IASA (first actionable frame) at 60 [fd].

## Recovery

- **Options:**
  - Double jump.
  - Cape: one stall and small rise per airtime; also turns Mario around.
  - Up B: mostly vertical, can be angled forward for distance at the cost of height; hits
    frames 3 onward and can clip edgeguarders [wiki:Mario_(SSBM)/Up_special].
  - Wall jump, and up B wall jump into a second up B.
  - Tornado mash: a small rise once per airtime.
  - Fireballs from high up to stuff an edgeguarder [wiki:Mario_(SSBM)].
- **Mixups:** High with fireballs versus low with a sweetspotted up B; cape to delay; air
  dodge onto the stage; up B angled to land on stage versus to the ledge.
- **Weaknesses:** Short total distance, one predictable final move, and the up B has no
  protection after the first few frames. An edgehog timed to the up B, or any hit after the
  double jump is gone, usually kills.

### Edgeguarding Mario

- Take the ledge when he commits to up B from below: he cannot reach the stage from most
  positions.
- Hit him out of his double jump: without it, cape + up B covers little distance.
- Characters with a move that reaches below the ledge (Marth dtilt, Sheik fair/bair, Fox
  shine, Falco dair) can hit the up B on its way up. Be aware the first up B frames have a
  hitbox and frames 3-6 are intangible [wiki:Mario_(SSBM)/Up_special].
- A CPU Mario should vary: cape stall then up B, immediate up B, and occasional air dodge.

## Defense and out of shield

- Best out of shield: up B (hits frame 4 from shield, see above), then shield grab, nair out
  of shield, and wavedash out of shield to reposition.
- Nair (frame 3 [fd]) is his combo breaker in the air.
- [Crouch cancel](../techniques/crouch-cancel.md) into down smash (frame 5 [fd]) or grab at low
  percent.
- He struggles against well-spaced sword pressure (cannot reach the opponent with a shield
  grab) and against Fox/Falco shine pressure only in the usual way; up B out of shield is his
  answer to imperfect pressure.

## As the training dummy

- Mid weight, mid fall speed: the reference "average" body. Combos designed for mid-fallers
  ([Sheik](sheik.md), [Marth](marth.md), Dr. Mario) apply.
- Not a fastfaller: Fox/Falco/Marth up throw chain grabs that need fastfall speed do not last
  on him. [Peach](peach.md)'s down throw chain grab does not work on Mario because he can
  jump out [wiki:Chain_grab].
- Sheik's down throw is a tech chase on him rather than a chain grab [wiki:Chain_grab].
- Realistic escape options a CPU should use: nair out of hitstun, up B as a panic option when
  grounded, double jump away, DI away from juggles.
- Recovery behaviour for edgeguard drills: see "Edgeguarding Mario".

## Matchup notes

### vs Fox and Falco

- Mario's reward on a grab is high: up throw chain grab, then cape or bair edgeguards. The
  cape reverses Fire Fox and Fire Bird, and reflects lasers.
- He loses neutral to their speed and lasers and dies off the top early to up smash and up air.

### vs Marth

- Outranged on the ground and in the air; Marth's down tilt and forward smash cover Mario's
  recovery. Mario needs to get inside and grab; cape works on Marth's up B.

### vs Sheik

- Sheik out-frames him up close and edgeguards him easily. Cape turns her up B around if she
  recovers in range.

### vs Dr. Mario

- Near mirror. Doc kills earlier (forward smash, fair, back throw); Mario combos longer and
  recovers further [wiki:Dr._Mario_(SSBM)].

## Drill seeds

### Cape the Fire Fox

- **id:** `mario-cape-firefox`
- **Goal:** Time the cape's 3 active frames against a moving recovery.
- **Player:** Mario
- **CPU:** Fox (also Falco, Captain Falcon, Luigi side B)
- **Setup:** Final Destination. Mario stands at the left ledge facing out. Fox starts offstage
  left, below ledge height, no double jump, at 60%.
- **CPU behaviour:** Charges up B and aims at the ledge or just above the stage, angle
  randomised among: sweetspot ledge, onto stage, high.
- **Success:** Fox takes cape damage during up B travel and loses the stock without grabbing
  the ledge.
- **Fail:** Fox grabs the ledge or lands on stage; Mario is hit.
- **Variations:** Mario starts center stage and must run to the ledge; Fox uses side B
  (Illusion) some of the time, which needs a different answer (hit or edgehog).
- **Data needed:** Cape hitbox frames 12-14 and total 35 [wiki:Mario_(SSBM)/Side_special];
  Fox up B startup and travel timing.

### Up throw chain grab on a fastfaller

- **id:** `mario-uthrow-chaingrab`
- **Goal:** Follow DI and re-grab without letting the opponent jump out.
- **Player:** Mario
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** Final Destination, center, CPU starts grabbed at 0%.
- **CPU behaviour:** Random DI on each throw (none, slight forward, slight behind, full
  forward, full behind); jumps or shines at the first actionable frame.
- **Success:** N consecutive re-grabs (start with 3, raise to 6).
- **Fail:** CPU acts between grabs, or a grab whiffs.
- **Variations:** Start percent; allow platforms (Battlefield) so the CPU can tech on them.
- **Data needed:** Up throw release frame 18 / 39 total by weight
  [wiki:Mario_(SSBM)/Up_throw], Mario grab startup [fd], victim fall speed and hitstun.

### Up B out of shield punish

- **id:** `mario-upb-oos`
- **Goal:** Punish an aerial on shield with jump-cancelled up B.
- **Player:** Mario
- **CPU:** Fox, Falco, Sheik, Marth
- **Setup:** Mario shielding center stage; CPU approaches with a SHFFL aerial that lands in
  front of or on Mario.
- **CPU behaviour:** Randomly either lands close and grabs/jabs (punishable) or spaces the
  aerial out of range (should not be up B'd).
- **Success:** Up B hit 1 connects within 6 frames of shield stun ending on the close case; no
  up B attempted on the spaced case.
- **Fail:** Mario is grabbed or hit, or whiffs up B.
- **Variations:** Add shine after the aerial for Fox/Falco so only the gap before the shine is
  punishable.
- **Data needed:** Up B hit frame 3 and intangibility 3-6 [wiki:Mario_(SSBM)/Up_special];
  shield stun of the CPU's aerial.

### Up B wall jump recovery

- **id:** `mario-upb-walljump`
- **Goal:** Hit the wall jump window out of up B.
- **Player:** Mario
- **CPU:** none (or an edgehogging CPU for pressure)
- **Setup:** Yoshi's Story. Mario placed against the stage wall well below the ledge, double
  jump already used.
- **CPU behaviour:** None.
- **Success:** Wall jump registers during up B frames 23-29 (no-angle case) and Mario grabs
  the ledge after a second up B.
- **Fail:** Mario enters special fall.
- **Variations:** Require the horizontal angle (window 21-29) or the extended angle (25-29);
  start slightly off the wall.
- **Data needed:** Wall jump windows [wiki:Mario_(SSBM)/Up_special].

### Juggle to edgeguard

- **id:** `mario-utilt-juggle`
- **Goal:** Convert a launcher into repeated up tilts/up airs and finish with a hit that puts
  the opponent offstage.
- **Player:** Mario
- **CPU:** Captain Falcon, Sheik, Marth
- **Setup:** CPU starts in hitstun above Mario from an up throw at 20%.
- **CPU behaviour:** Random DI; jumps or attacks when actionable.
- **Success:** At least 4 hits without the CPU acting, last hit sends the CPU past the ledge.
- **Fail:** CPU lands or acts before hit 4.
- **Variations:** Start percent 0-60%; platform stages.
- **Data needed:** Up tilt and up air hitbox data [fd]; victim weight/fall speed.

### Tip forward smash spacing

- **id:** `mario-fsmash-sweetspot`
- **Goal:** Land the fire sweetspot, not the arm.
- **Player:** Mario
- **CPU:** any mid-weight
- **Setup:** CPU at 90%, standing or shielding then dropping shield, distance randomised.
- **CPU behaviour:** Stands, or walks slowly in/out.
- **Success:** Forward smash connects with the sweetspot hitbox (18% unangled [fd]) after a
  wavedash that sets the spacing.
- **Fail:** Arm hitbox (10-11% [fd]) connects, or a whiff.
- **Variations:** Require up-angled (19%) or down-angled (17%) versions [fd].
- **Data needed:** Forward smash hitbox ids and frames 12-16 [fd].

### Fireball approach

- **id:** `mario-fireball-waveland`
- **Goal:** Full hop fireball, waveland, and act behind the fireball.
- **Player:** Mario
- **CPU:** Marth, Sheik (shielding/dash dancing)
- **Setup:** Opposite sides of Final Destination.
- **CPU behaviour:** Shields fireballs and tries to grab Mario if he lands in lag.
- **Success:** Fireball released, Mario lands with a waveland, and a grab or hit connects
  while the CPU is in shield stun or hitstun from the fireball.
- **Fail:** Mario lands in fireball animation or gets grabbed.
- **Variations:** Short hop fireballs; retreating versions.
- **Data needed:** Fireball release frame 14 and move length 43
  [lib:Doc Advanced Tech Frame Data Megathread] [fd].

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlMr.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/mario.json`](../framedata/mario.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 2-3 | 3 | 83/85 | 0 | 100 | 20 |  | 15 | - | 3 | -10 |  |
| Jab 2 | `jab2` | 3-4 | 2 | 83/85 | 0 | 100 | 20 |  | 18 | - | 2 | -13 | starts 1 frame late (included) |
| Jab 3 | `jab3` | 5-9 | 5 | Sakurai | 10 | 100 | - |  | 22 | - | 4 | -13 | starts 1 frame late (included) |
| Dash attack | `dash_attack` | 6-9 | 9 | 110 | 70 | 50 | - |  | 48 | 38 | 6 | -25 |  |
|  |  | 10-25 | 7 | 120 | 45 | 30 | - |  |  |  | 5 | -22 |  |
| Forward tilt (angled up) | `ftilt_high` | 5-7 | 10 | Sakurai | 6 | 100 | - |  | 32 | - | 6 | -21 |  |
| Forward tilt | `ftilt` | 5-7 | 9 | Sakurai | 6 | 100 | - |  | 32 | - | 6 | -21 |  |
| Forward tilt (angled down) | `ftilt_low` | 5-7 | 8 | Sakurai | 6 | 100 | 1 |  | 32 | - | 5 | -22 |  |
| Up tilt | `utilt` | 4-12 | 8 | 96 | 26 | 125/122/120 | - |  | 30 | 30 | 5 | -20 |  |
| Down tilt | `dtilt` | 5-8 | 8/9 | 80 | 10 | 80 | - |  | 34 | - | 6 | -23 |  |
| Forward smash (angled up) | `fsmash_high` | 12-16 | 19/15 | Sakurai | 25 | 95/96 | - | fire | 41 | - | 10 | -19 | charge hold frame 5 |
| Forward smash | `fsmash` | 12-16 | 18/11/10 | Sakurai | 25 | 95/96 | - | fire | 41 | - | 10 | -19 | charge hold frame 5 |
| Forward smash (angled down) | `fsmash_low` | 12-16 | 17/13 | Sakurai | 25 | 95/96 | - | fire | 41 | - | 9 | -20 | charge hold frame 5 |
| Up smash | `usmash` | 9-11 | 15 | 83 | 32 | 97 | - |  | 39 | - | 8 | -22 | charge hold frame 7; partly intangible 9-11 (1 bone) |
| Down smash | `dsmash` | 5-6 | 16 | Sakurai | 40 | 75 | - |  | 37 | - | 9 | -23 | charge hold frame 3 |
|  |  | 14 | 10/12 | Sakurai | 35 | 75 | - |  |  |  | 7 | -16 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 3-6 | 12 | Sakurai | 20 | 100 | - |  | 45 | - | 7 | 16 | 8 | <3, >35 | -1 |  |
|  |  | 7-32 | 8 | Sakurai | 15 | 100 | - |  |  |  | 5 |  |  |  | -3 |  |
| Forward air | `fair` | 18-22 | 15 | 280 | 30 | 70 | - |  | 74 | 60 | 8 | 21 | 10 | <3, >42 | -2 |  |
| Back air | `bair` | 6-8 | 11 | Sakurai | 10 | 100 | - |  | 28 | - | 6 | 15 | 7 | <6, >18 | -1 |  |
|  |  | 9-17 | 9 | Sakurai | 7 | 100 | - |  |  |  | 6 |  |  |  | -1 |  |
| Up air | `uair` | 4-9 | 11 | 55 | 0 | 100 | - |  | 33 | 30 | 6 | 15 | 7 | <2, >15 | -1 |  |
| Down air | `dair` | 10-11, 13-14, 16-17, 19-20, 22-23, 25-26, 28-29 | 2 | 94 | 0 | 100 | 30 |  | 38 | 38 | 2 | 23 | 11 | <6, >32 | -9 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 11-12 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 17 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 9 | 9 | 45 | 60 | 65 | - | - | 12 | 27 |  |
| Back throw | `bthrow` | 12 | 12 | 45 | 80 | 65 | - | - | 44 | 66 |  |
| Up throw | `uthrow` | 8 | 8 | 90 | 70 | 72 | - | - | 18 | 39 |  |
| Down throw | `dthrow` | 6 | 6 | 90 | 75 | 30 | - | - | 18 | 39 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Fireball, ground | `special_n` | - | - | - | - | - | - | - | 43 | - | - | - | spawns article/projectile on 14 |
| Neutral B: Fireball, air | `special_air_n` | - | - | - | - | - | - | - | 43 | - | - | - | spawns article/projectile on 14 |
| Side B: Cape, ground | `special_s` | 12-14 | 10/8 | 110 | 30 | 80 | - | cape | 35 | - | 6 | - |  |
| Side B: Cape, ground, Air | `special_s_air` | 12-14 | 9/7 | 110 | 30 | 80 | - | cape | 35 | - | 6 | - |  |
| Up B: Super Jump Punch, ground | `special_hi` | 3-6 | 5 | 70/90 | 0 | 100 | 130 | coin | 37 | - | 4 | - | intangible 3-6 |
|  |  | 7-8, 9-10, 11-12, 13-14 | 1 | 74/78 | 0 | 100 | 110/150 | coin |  |  | 2 | - |  |
|  |  | 15-16, 17-18, 19-20, 21-22 | 1 | 72/78 | 0 | 100 | 90/120 | coin |  |  | 2 | - |  |
|  |  | 23-24 | 3 | 50 | 40 | 140 | - | coin |  |  | 3 | - |  |
| Up B: Super Jump Punch, air | `special_air_hi` | 3-6 | 5 | 70/90 | 0 | 100 | 130 | coin | 37 | - | 4 | - | intangible 3-6 |
|  |  | 7-8, 9-10, 11-12, 13-14 | 1 | 74/78 | 0 | 100 | 110/150 | coin |  |  | 2 | - |  |
|  |  | 15-16, 17-18, 19-20, 21-22 | 1 | 72/78 | 0 | 100 | 90/120 | coin |  |  | 2 | - |  |
|  |  | 23-24 | 3 | 50 | 40 | 140 | - | coin |  |  | 3 | - |  |
| Down B: Mario Tornado, ground | `special_lw` | 8-9 | 2 | 140 | 0 | 0 | 40 |  | 79 | - | 2 | - |  |
|  |  | 12-13, 15-16, 18-19, 21-22, 24-25 | 1 | 180 | 40 | 0 | 1 |  |  |  | 2 | - |  |
|  |  | 27-28 | 1 | 100 | 40 | 0 | 1 |  |  |  | 2 | - |  |
|  |  | 38-39 | 5 | 80 | 60 | 115 | - |  |  |  | 4 | - |  |
| Down B: Mario Tornado, air | `special_air_lw` | 8-9 | 2 | 140 | 0 | 0 | 40 |  | 79 | - | 2 | - |  |
|  |  | 12-13, 15-16, 18-19, 21-22, 24-25 | 1 | 160/270 | 40/10/60 | 0 | 1 |  |  |  | 2 | - |  |
|  |  | 27-28 | 1 | 100 | 50 | 0 | 1 |  |  |  | 2 | - |  |
|  |  | 38-39 | 3 | 80 | 70 | 120 | - |  |  |  | 3 | - |  |

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
| Up B | jump cancel | 4 | `special_hi` |
| Neutral air | jump | 7 | `nair` |
| Shield grab | direct | 7 | `grab` |
| Up air | jump | 8 | `uair` |
| Back air | jump | 10 | `bair` |
| Up smash | jump cancel | 10 | `usmash` |
| Down air | jump | 14 | `dair` |
| Forward air | jump | 22 | `fair` |
| Spot dodge | direct | intangible 2-15 of 22 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 16 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Mario indexed by [The Melee Library](https://www.meleelibrary.com/#mario) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Mario Melee Techs Guide](https://www.youtube.com/watch?v=NF6ctTSbXJg&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=14&t=0s) | Third Chair | Video guide on performing useful Mario tech in 2020. |
| [Mario Edgeguard Options](http://imgur.com/a/P6CNM#0) | Schmooblidon | Pictures of the coverage of Mario’s edgeguard options. |
| [Matchup Discussion Thread](http://smashboards.com/threads/the-mario-match-up-discussion-thread-now-on-falcon.286647/) | community |  |
| [Mario Hitboxes and Frame Data](http://smashboards.com/threads/mario-hitboxes-and-frame-data.312343/) | Stratocaster, Standardtoaster, and SuperDoodleMan |  |
| [Ambitious as a Plumber: A Mario FAQ](http://smashboards.com/threads/ambitions-as-a-plumber-a-mario-faq.96853/) | community | A Q&A. Use the search function. |
| [Mario FAQ: Guide to Italian Plumbing](http://smashboards.com/threads/maelstrom218s-mario-faq-guide-to-italian-plumbing-vn-1-0.56009/) | Maelstrom218 | A general guide on Mario. |
| [We Livin’ Doe! Mario Resurrection Thread](http://smashboards.com/threads/we-livin-doe-a-mario-resurrection-thread-ft-a-rookie.341083/) | A Rookie | A Rookie answers various questions. |
| [Mario Dair Tutorial](https://www.youtube.com/watch?v=iq7nDkzn5eU) | A Rookie | He found some applications for the landing hitbox of Mario’s dair. |
| [Mario Walljump Frame Data](http://smashboards.com/threads/marios-up-b-walljump-frame-data.389719/#post-18541850) | Schmooblidon |  |
| [The Mechanics of Walljump Up-B](http://smashboards.com/threads/the-mechanics-of-up-b-walljump.425622/) | Schmooblidon |  |
| [Mario Melee Chaingrab Guide](https://www.youtube.com/watch?v=CNRVGt_0V5I&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=19&t=0s) | Third Chair |  |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Mario (SSBM): https://www.ssbwiki.com/Mario_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Mario_(SSBM)/Up_special ,
  /Side_special , /Down_special , /Up_throw , /Down_throw , /Back_throw , /Down_aerial ,
  /Forward_aerial , /Forward_smash , /Forward_tilt
- SSBWiki, Cape: https://www.ssbwiki.com/Cape
- SSBWiki, Super Jump Punch: https://www.ssbwiki.com/Super_Jump_Punch
- SSBWiki, Mario Tornado: https://www.ssbwiki.com/Mario_Tornado
- SSBWiki, Fireball: https://www.ssbwiki.com/Fireball
- SSBWiki, Dr. Mario (SSBM), "Differences from Mario": https://www.ssbwiki.com/Dr._Mario_(SSBM)
- SSBWiki, Chain grab: https://www.ssbwiki.com/Chain_grab
- SSBWiki, List of SSBM tier lists (NTSC): https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Schmooblidon, "Doc Advanced Tech Frame Data Megathread" (via web.archive.org; includes Mario
  compatibility notes and up B wall jump data):
  http://smashboards.com/threads/doc-advanced-tech-frame-data-megathread.378813/
- Schmooblidon, "Up-B Cancel Frame and Hitbox Data" (via web.archive.org):
  http://smashboards.com/threads/up-b-cancel-frame-and-hitbox-data-complete-with-gifs-and-now-oos-data.378468/
- Palika, "Full list of differences between Mario and Dr. Mario" (via web.archive.org):
  https://www.reddit.com/r/SSBM/comments/6d00m3/full_list_of_differences_between_mario_and_dr/
- maelstrom218, "Mario FAQ: Guide to Italian Plumbing" (first post only, via web.archive.org):
  http://smashboards.com/threads/maelstrom218s-mario-faq-guide-to-italian-plumbing-vn-1-0.56009/
- Frame data dump: `Mario.json`
