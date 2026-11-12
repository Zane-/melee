---
schema: melee-character/v1
id: jigglypuff
name: Jigglypuff
aliases: [Puff, Jiggs, Purin]
tier: "S (3rd of 26), 2021 tier list (13th, PG Stats)"
archetype: [floaty, lightweight, punish-heavy, edgeguarder, mixup]
related: [kirby, peach]
summary: Jigglypuff wins by drifting just outside the opponent's range and walling with back air, then turning any upward launch, throw or bad landing into Rest or an off-stage back air chain that the opponent cannot recover from.
key_tech: [bair-wall, wall-of-pain, up-throw-rest, up-tilt-and-up-air-rest, dair-rest-and-dair-smash, rest-punish-out-of-shield, tech-chase-rest, crouch-under-grabs-and-lasers, sing-ledge-cancel, rising-pound, ledge-refresh-planking, jump-cancel-grab-out-of-shield]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlPr.dat
framedata: ../framedata/jigglypuff.json
code: src/melee/ft/kinds/ftPurin
specials:
  neutral_b: "Rollout"
  side_b: "Pound"
  up_b: "Sing"
  down_b: "Rest"
attributes:
  weight: 60
  gravity: 0.064
  fall_speed: 1.3
  fast_fall_speed: 1.6
  jump_squat: 5
  jumps: 6
  walk_speed: 0.7
  dash_speed: 1.4
  run_speed: 1.1
  traction: 0.09
  air_speed: 1.35
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [5, 16, 3]
  jab2: [6, 17, 3]
  dash_attack: [4, 39, 12]
  ftilt_high: [6, 28, 10]
  ftilt: [6, 28, 10]
  ftilt_low: [6, 28, 10]
  utilt: [8, 24, 9]
  dtilt: [10, 30, 10]
  fsmash: [12, 45, 17]
  usmash: [7, 45, 15]
  dsmash: [9, 48, 12]
  nair: [6, 50, 12]
  fair: [7, 35, 12]
  bair: [9, 31, 12]
  uair: [9, 38, 12]
  dair: [5, 50, 2]
  grab: [7, 31, 0]
  dash_grab: [11, 41, 0]
  pummel: [11, 31, 3]
  fthrow: [10, 36, 5]
  bthrow: [null, 50, 10]
  uthrow: [null, 42, 11]
  dthrow: [10, 85, 2]
  special_n_start_r: [null, 16, 0]
  special_n_start_l: [null, 16, 0]
  special_n: [null, 60, 0]
  special_n_303: [null, 60, 0]
  special_n_304: [1, 60, 10]
  special_n_305: [null, 60, 0]
  special_n_end_r: [null, 32, 0]
  special_n_end_l: [null, 32, 0]
  special_air_n_start_r: [null, 16, 0]
  special_air_n_start_l: [null, 16, 0]
  special_n_310: [null, 60, 0]
  special_n_311: [null, 60, 0]
  special_n_312: [1, 60, 10]
  special_n_313: [null, 60, 0]
  special_air_n_end_r: [null, 32, 0]
  special_air_n_end_l: [null, 32, 0]
  special_n_316: [null, 60, 0]
  special_s: [12, 46, 13]
  special_air_s: [12, 46, 13]
  special_hi_l: [28, 180, 0]
  special_air_hi_l: [28, 180, 0]
  special_hi_r: [28, 180, 0]
  special_air_hi_r: [28, 180, 0]
  special_lw_l: [1, 250, 28]
  special_air_lw_l: [1, 250, 28]
  special_lw_r: [1, 250, 28]
  special_air_lw_r: [1, 250, 28]
oos:  # option: frame the hitbox is out
  grab: 7
  usmash: 8
  dair: 10
  nair: 11
  fair: 12
  bair: 14
  uair: 14
  special_hi_l: 29
resources: 32
# generated: end
---

# Jigglypuff

<!-- GENERATED:attributes -->
## Attributes

Read from `PlPr.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 60 |
| Gravity | 0.064 |
| Terminal fall speed | 1.3 |
| Fast-fall speed | 1.6 |
| Jump squat (frames before airborne) | 5 |
| Full hop / short hop initial Y speed | 1.6 / 1.05 |
| Air jump Y multiplier | 0 |
| Jumps | 6 |
| Walk max speed | 0.7 |
| Dash initial speed / run max speed | 1.4 / 1.1 |
| Ground friction (traction) | 0.09 |
| Air max horizontal speed | 1.35 |
| Air acceleration (base + stick) | 0.19 + 0.09 |
| Air friction | 0.05 |
| Normal landing lag | 4 |
| Shield size | 13.125 |
<!-- /GENERATED:attributes -->

## Overview

Jigglypuff is the game's extreme floaty: second-lightest weight (60), slowest fall speed (1.3), slowest run (tied with Zelda), but the fastest air speed (1.35) and highest air acceleration, with five midair jumps [wiki:Jigglypuff_(SSBM)]. She plays almost entirely in the air, weaving in and out of range and hitting with back air (bair), which has a large disjointed hitbox [wiki:Jigglypuff_(SSBM)/Back_aerial]. She has no projectile and a weak ground game, so her neutral is patient: space bairs, let the opponent over-commit, punish.

Her punish game is among the strongest in the game. Down B (Rest) hits on frame 1 for 28% with enormous knockback and kills at very low percent [wiki:Jigglypuff_(SSBM)/Down_special][fd]; up throw, up tilt, up air, down air, tech chases and many out-of-shield situations lead into it. Off stage, repeated bairs (the "wall of pain") carry opponents past the point of recovery [wiki:Wall_of_Pain]. She is hard to combo and hard to edgeguard, so despite her weight she often lives long; she dies to stray strong vertical hits, to a few specific setups (Fox's up throw -> up air), and instantly if her shield breaks [wiki:Jigglypuff_(SSBM)]. Mechanically she is one of the easier top tiers; the difficulty is spacing, patience, and precise Rest setups.

## Strengths and weaknesses

- **Strengths:**
  - Best air mobility in the game: air speed 1.35, air acceleration 0.28, five midair jumps [wiki:Jigglypuff_(SSBM)].
  - Bair: 12%, hitbox on frames 9-12, IASA 31, auto-cancels after frame 24 [fd]; long disjoint, usable rising, falling, retreating or in chains.
  - Rest: frame 1, 28%, base knockback 78, growth 120 [fd][wiki:Jigglypuff_(SSBM)/Down_special]; a kill from almost any confirmed hit.
  - Edgeguarding: can follow opponents far off stage and return [wiki:Jigglypuff_(SSBM)].
  - Recovery: effectively cannot be gimped at low percent; jumps + side B (Pound) cover huge horizontal distance [wiki:Pound].
  - Hard to combo, chain grab or zero-to-death because of weight and floatiness [wiki:Jigglypuff_(SSBM)].
  - Low crouch ducks many grabs, lasers and attacks [wiki:Jigglypuff_(SSBM)][lib:The Melee Puff Bible].
- **Weaknesses:**
  - Dies early to strong vertical hits (weight 60) [wiki:Jigglypuff_(SSBM)].
  - Shield break is an instant KO on tournament stages (300 units of vertical knockback) [wiki:Jigglypuff_(SSBM)].
  - Slowest run, very short [wavedash](../techniques/wavedash.md), no projectile [wiki:Jigglypuff_(SSBM)].
  - Weak aerial hits (late nair/fair) are [crouch cancelled](../techniques/crouch-cancel.md) up to mid percent [wiki:Jigglypuff_(SSBM)].
  - Slow to re-attack after landing: from the ground her fastest aerial hitbox is 11 frames away (5 jump squat + nair frame 6), and an L-cancelled aerial plus the next aerial is about 21 frames [lib:20XX+XY][fd].
  - A missed Rest leaves her helpless for the rest of a 249-frame animation [wiki:Jigglypuff_(SSBM)/Down_special].
  - Zoned by projectile characters such as [Falco](falco.md) and [Young Link](young-link.md) [wiki:Jigglypuff_(SSBM)].

## Character tech

### Bair wall

- **id:** `bair-wall`
- **What:** Spacing back airs so that the tip of the hitbox is between Jigglypuff and the opponent, then drifting back out of range. A player guide lists ten distinct uses: retreating auto-cancel bair, advancing auto-cancel bair, neutral rising full-hop bair, retreating rising full-hop bair, falling low bair, falling high fade-back bair, falling high cross-up bair, in-place double-jump bair, fade-back double-jump bair, low double-jump bair [lib:The Melee Puff Bible].
- **Inputs:** Face away from the opponent (or turn in the air by jumping the other way). Short hop or full hop -> bair -> drift with the control stick. [L-cancel](../techniques/l-cancel.md) when landing during the move, or time it to [auto-cancel](../techniques/auto-cancel.md).
- **Timing:** Hitbox frames 9-12; IASA 31; auto-cancel before frame 9 and after frame 24; landing lag 20, 10 L-cancelled [fd]. After a short-hop bair that hits she can be acting as early as 18 frames after the hit, or go straight into a double-jump bair [lib:The Melee Puff Bible]. Bair -> bair has about a 27-frame gap between hitboxes [lib:20XX+XY].
- **Used for:** Stopping approaches, taking space safely, starting off-stage chains. A low, spaced, L-cancelled bair is almost never directly punishable except out of crouch cancel; at about 40% it forces a knockdown/tech on Fox and Marth [lib:The Melee Puff Bible].
- **Common errors:** Drifting forward during the rise of the jump (runs into disjoints, especially Marth's) [lib:The Melee Puff Bible]; bairing too high so it whiffs over crouchers and lands with more lag; advancing bairs into a crouch-cancelling or shielding opponent.
- **Drill idea:** CPU dash-dances and randomly approaches; player must hit with the outer part of bair and be outside the CPU's grab/dash-attack range on landing.

### Wall of pain

- **id:** `wall-of-pain`
- **What:** A chain of bairs that pushes an opponent off stage and further out with each hit, using her air speed and jumps to keep up [wiki:Wall_of_Pain].
- **Inputs:** Bair toward the ledge -> drift and jump after the opponent -> bair -> repeat until out of jumps or the opponent is too far to recover; return with remaining jumps and Pound.
- **Timing:** Each bair must land before hitstun ends; in Melee the opponent cannot air dodge out without becoming helpless off stage [wiki:Wall_of_Pain]. Usable from about 45-50% on Marth and from 50%+ on Sheik and Captain Falcon after a launcher [lib:The Melee Puff Bible].
- **Used for:** Killing at low-mid percent off stage, especially characters with short recoveries such as Falco and Roy [wiki:Wall_of_Pain].
- **Common errors:** Using jumps too early and having to return; hitting with bair facing the wrong way (sends toward stage); following too low and getting hit by an up B.
- **Drill idea:** CPU launched toward the ledge at 40-60%; count bairs landed in sequence; success if CPU cannot reach the ledge and Jigglypuff returns.

### Up throw Rest

- **id:** `up-throw-rest`
- **What:** Up throw, then jump into the falling opponent and Rest. Works on fastfallers because they do not travel far from the throw [wiki:Space_animal_slayer]. Also called the "space animal slayer".
- **Inputs:** Grab -> up throw -> jump (double jump if needed) so Jigglypuff's centre overlaps the opponent -> down B. At mid percent insert an up air first [wiki:Space_animal_slayer].
- **Timing:** Rest hits only on frame 1, with a hitbox about the size of her eye at her centre [wiki:Jigglypuff_(SSBM)/Down_special] (the frame data dump lists the hitbox on frame 2 [fd]; see the generated table). Jigglypuff is actionable on frame 32 after up-throwing Fox and frame 34 after Falco (throw speed depends on weight) [lib:The Melee Puff Bible]. Flowchart vs Fox on a flat stage [lib:The Melee Puff Bible]:
  - 0-15%: no DI or DI forward -> short hop uair -> grab / utilt / Rest; DI behind -> short hop bair (not guaranteed against full DI).
  - 15-30%: no DI -> double-jump Rest; DI forward -> short hop uair -> grab/Rest; DI behind -> full hop bair.
  - 30-70%: no DI -> double-jump Rest; full DI forward -> full hop auto-cancel nair -> grab/Rest; DI behind -> full hop bair.
  - 70%+: throw off stage instead, or uthrow -> full hop double jump aerial.
  - Falco is the same with thresholds at 20% and 30%, and the 0-20% uair needs a 2-frame dash first [lib:The Melee Puff Bible].
- **Used for:** Killing Fox, Falco and Captain Falcon from a grab at low percent; occasionally Roy [wiki:Space_animal_slayer].
- **Common errors:** Resting when the opponent used horizontal [DI](../techniques/di.md) (whiff, then a full punish); not accounting for platforms. With no DI Fox lands on the top platform after uthrow from 14% on Yoshi's Story, 17% on Fountain of Dreams, 62% on Dream Land, 76% on Battlefield; Falco from 0%, 0%, 43%, 60% [lib:The Melee Puff Bible].
- **Drill idea:** Fox/Falco CPU with random DI on the throw; player must choose Rest only when it is real and pick the listed alternative otherwise.

### Up tilt and up air into Rest

- **id:** `up-tilt-and-up-air-rest`
- **What:** Up tilt and up air both launch nearly straight up with high hitstun; at the right percent Jigglypuff jumps and Rests before the opponent can act.
- **Inputs:** Utilt (hits behind and above her; clean on frames 8-9 [fd]) or a low/rising uair (frames 9-12 [fd]) -> short hop / full hop / full hop + double jump -> down B when overlapping.
- **Timing:** Utilt has high base knockback (40, growth 120 [fd]); it tumbles Fox from 9% and knocks fastfallers down between 15% and 50%; against non-fastfallers it combos into Rest at nearly all percents except under 5% or very high [wiki:Jigglypuff_(SSBM)/Up_tilt]. Sourced setups [lib:The Melee Puff Bible]:
  - Spacies: rising uair at 12% -> Rest; at 30% Rest or falling uair (Falco from 35%); at 50% double-jump Rest. Low uair 0-60% no DI -> grab or Rest. Utilt 10-65% no DI -> Rest or grab.
  - Marth: utilt at 0% -> short hop Rest; 12% no/forward DI -> short hop Rest, DI behind -> short hop bair auto-cancel -> Rest; 30% -> full hop (double jump) Rest. Low uair at 0% -> utilt -> Rest; 12-40% -> full hop Rest; 40-50% -> full hop double jump Rest.
  - Sheik: low uair 0-30% -> react to DI with Rest/utilt/grab; rising uair at 20% -> double jump Rest or bair.
  - Peach: utilt at 0% -> Rest; at 12% no DI -> full hop double jump Rest; low uair 12-50% no DI -> full hop Rest.
  - Captain Falcon: utilt or low uair at 0% no DI -> Rest; DI out -> grab.
- **Used for:** Converting stray hits into kills against the whole cast, not only fastfallers.
- **Common errors:** Resting against DI away; jumping too late (opponent double jumps or air dodges); utilt used facing the opponent from too far (the strong part is behind/above her).
- **Drill idea:** CPU at a set percent with random DI; player lands utilt/uair and must Rest only when the opponent stays above her.

### Down air into Rest or smash

- **id:** `dair-rest-and-dair-smash`
- **What:** Down air (drill) is a multi-hit that holds the opponent in place. Late in the percent range it combos into grab, up smash, forward smash, or Rest.
- **Inputs:** Low dair (L-cancelled, or auto-cancelled from a full hop) -> Rest immediately if the opponent leans into her; otherwise usmash / fsmash / grab.
- **Timing:** Dair hits every 3 frames from frame 5; landing lag 30, 15 L-cancelled [fd]. Dair starts giving frame advantage at about 45%; grab starts to combo at about 70% [lib:The Melee Puff Bible]. "Spikestun": past about 45%, if the last hit strikes the opponent's lowest hurtbox they lean forward into her and dair -> Rest is a true combo without moving [lib:The Melee Puff Bible]. Dair -> usmash is a true combo from 63% on Marth, 67% on Sheik and Peach, 56% on Jigglypuff; dair -> fsmash from 100% on Fox, 103% on Falco, 107% on Marth, 108% on Sheik and Peach, 92% on Jigglypuff (all assuming perfect execution) [lib:The Melee Puff Bible].
- **Used for:** Kill confirms at percents where grab no longer leads to anything and aerials do not kill outright; shield pokes on platforms and on depleted shields [lib:The Melee Puff Bible].
- **Common errors:** Missing the L-cancel (30 frames of lag [fd]); using it at low percent where the opponent acts first; trading with an anti-air.
- **Drill idea:** CPU standing at 60-110%; player must land dair and connect the smash within the combo window; report whether the follow-up was a true combo.

### Rest punish out of shield or crouch

- **id:** `rest-punish-out-of-shield`
- **What:** Using Rest as a frame-1 punish after shielding or crouching under an attack that ends close to her.
- **Inputs:** Shield (or crouch) the attack -> jump or wavedash to overlap the opponent -> down B. From a platform: [shield drop](../techniques/shield-drop.md) -> Rest/uair.
- **Timing:** Jump squat is 5 frames [wiki:Jigglypuff_(SSBM)], so jump -> Rest hits 6 frames after leaving shield at the earliest. Documented cases: Sheik's dsmash can be Rested out of shield or out of crouch cancel with a wavedash or short hop, if its last hit whiffs [lib:The Melee Puff Bible] (also a library video [lib:Sheik Down Smash to Rest out of Shield]); Peach's dash attack if shielded or crouched under [lib:The Melee Puff Bible]; Marth's dair out of shield if she anticipated and shielded it [lib:The Melee Puff Bible]; Marth's utilt from a platform via shield drop [lib:Shielddrop Rest Punish Marth Utilt]; Falco's dair when she is airborne under tumble percent and ASDIs/SDIs it down to the ground [lib:The Melee Puff Bible]; rising badly spaced aerials on her platform shield -> grab or Rest [lib:The Melee Puff Bible].
- **Used for:** Turning the opponent's unsafe pressure into a stock.
- **Common errors:** Resting when not overlapping (the hitbox is tiny); Resting moves that are actually safe; getting hit out of jump squat.
- **Drill idea:** CPU performs one of the listed moves on Jigglypuff's shield with varied spacing; success if Rest connects, fail if Rest whiffs or she is hit first.

### Tech-chase Rest

- **id:** `tech-chase-rest`
- **What:** After a knockdown, hover over the tech-in-place spot with an empty short hop and react: Rest a tech in place, chase rolls with an aerial into grab, jab-reset a missed tech. One guide calls this the "WreckChase" [lib:The Melee Puff Bible].
- **Inputs:** Low bair or short-hop bair that knocks down (about 40-50% on Fox) -> short hop over the opponent -> react. On a side platform after uthrow from 15%+: full hop to the tech-in-place spot, slight fast fall at the apex, react [lib:The Melee Puff Bible].
- **Timing:** A neutral tech is 26 frames and tech rolls are 40 frames, both vulnerable from frame 21 [lib:20XX+XY]. Resting the missed-tech bounce is listed as too inconsistent; use jab reset instead [lib:The Melee Puff Bible].
- **Used for:** Kills on fastfallers at the percents where bair/utilt knock down. See [tech chase](../techniques/tech-chase.md).
- **Common errors:** Committing to Rest before seeing the tech; being hit by a getup attack while hovering too low.
- **Drill idea:** CPU knocked down with random tech choice; success = Rest on tech in place, aerial or grab on rolls, jab reset on missed tech.

### Crouch under grabs and lasers

- **id:** `crouch-under-grabs-and-lasers`
- **What:** Jigglypuff's crouch is low enough to duck some standing/dash grabs, low lasers and several aerials, which lets her punish instead of shielding.
- **Inputs:** Hold down; act out of crouch with utilt, grab, wavedash, jump or Rest. After a low aerial on shield, buffer a crouch to avoid the shield grab [lib:The Melee Puff Bible].
- **Timing:** Marth cannot dash grab her initial crouch, but can after she has crouched about half a second; Sheik cannot grab her crouch at all [lib:The Melee Puff Bible]. Her initial crouch and jump squat duck Falco's lowest laser; a prolonged crouch is inconsistent [lib:The Melee Puff Bible]. Crouch-powershielding low lasers has about an 8-frame window; Falco's laser comes out on frame 10 [lib:The Melee Puff Bible]. Captain Falcon's short-hop nair essentially cannot hit a crouching Jigglypuff [lib:The Melee Puff Bible]. Crouch cancel stops working against Sheik's dsmash at 55% [lib:The Melee Puff Bible].
- **Used for:** Beating grab-based punish games (Marth, Sheik), getting through lasers, baiting moves to Rest.
- **Common errors:** Sitting in crouch against Marth (he waits and dash grabs or dtilts) [lib:The Melee Puff Bible]; crouching at percents where the move knocks her down.
- **Drill idea:** CPU Marth/Sheik attempts grab or a tilt at random; success if the grab whiffs over crouch and Jigglypuff punishes within N frames.

### Sing ledge cancel

- **id:** `sing-ledge-cancel`
- **What:** Up B (Sing) used while falling next to the ledge is cancelled by the ledge grab, removing its end lag. Grounded opponents in range fall asleep [wiki:Jigglypuff_(SSBM)/Up_special].
- **Inputs:** Drop or run off next to the ledge -> up B while moving downward -> she grabs the ledge. Running off and immediately singing to grab the ledge is called a "2Drop". Variant: fsmash, slide off the edge, then Sing [wiki:Jigglypuff_(SSBM)/Up_special].
- **Timing:** Sing's hitboxes are active on frames 28-35, 69-76 and 113-125 of a 179-frame animation; it only affects grounded opponents and is deactivated by hitting a shield [wiki:Jigglypuff_(SSBM)/Up_special]. Sleep lasts longer at higher percent and can be mashed out of [wiki:Sing]. At the ledge the sleep can be re-applied repeatedly; the wiki suggests at most 9 repetitions (to fully un-stale other moves) before the finisher [wiki:Jigglypuff_(SSBM)/Up_special].
- **Used for:** Fast ledge grab for edgehogging (it grabs facing either way); putting an opponent who lands at the ledge to sleep, then ledgedash into charged fsmash or Rest [wiki:Jigglypuff_(SSBM)/Forward_smash][lib:The Melee Puff Bible].
- **Common errors:** Singing while rising (no ledge grab, 179 frames of lag, usually a self-destruct off stage) [wiki:Jigglypuff_(SSBM)/Up_special]; singing at an airborne or shielding opponent.
- **Drill idea:** CPU Marth up-Bs onto the stage edge; player drops from ledge, Sings to regrab, then must land fsmash or Rest before the CPU wakes.

### Rising Pound

- **id:** `rising-pound`
- **What:** Side B (Pound) moves her forward; pressing up right after it starts makes her gain a little height. It does not cause helplessness, so it can be repeated between jumps for very long horizontal recovery [wiki:Pound].
- **Inputs:** Side B -> hold up on the control stick. (Down instead gives a "falling Pound".)
- **Timing:** Pound hitbox frames 12-27, total 45 frames, 13% [fd][wiki:Pound]. Each Pound ends slightly lower than it started, so it is not infinite [wiki:Pound].
- **Used for:** Recovery distance, crossing under stages, extra shield damage (a guide counts one Pound as two normal hits of shield depletion [lib:The Melee Puff Bible]), and as a poke that launches upward when it hits close [wiki:Pound].
- **Common errors:** Pounding into an edgeguarder's hitbox; forgetting to press up and losing height.
- **Drill idea:** Jigglypuff starts far off stage below ledge height with one jump; success if she reaches the ledge using jump + rising Pounds.

### Ledge refresh (planking)

- **id:** `ledge-refresh-planking`
- **What:** Repeatedly dropping from the ledge and regrabbing it (with a jump, aerial or Sing) to keep ledge intangibility and threaten invincible aerials.
- **Inputs:** Let go of ledge -> double jump -> aerial (bair/fair) or Sing -> regrab.
- **Timing:** A character cannot regrab the ledge before frame 29 after letting go, which guarantees at least 8 frames of vulnerability per cycle; an empty refresh is vulnerable on roughly frames 30-38 after the commitment; doing nothing on the ledge leaves her vulnerable from frame 38 after the grab; her under-100% getup attack is active on frames 20-24, invincible 1-30, vulnerable 31-56 [lib:How to Combat Puff Planking]. Three timings to attack her: just before she grabs the ledge, about 30 frames after she commits from the ledge, and 38 frames after a ledge grab if she does nothing [lib:How to Combat Puff Planking].
- **Used for:** Stalling, regaining invincibility, hitting opponents who come near the ledge. The same source calls it a gimmick that depends on the opponent not knowing these timings. See [ledge options](../techniques/ledge-options.md).
- **Common errors:** Predictable rhythm; any angled projectile beats it on its own [lib:How to Combat Puff Planking].
- **Drill idea:** (Jigglypuff as CPU) CPU cycles random refresh options; player must hit one of the three vulnerable timings.

### Jump-cancel grab out of shield

- **id:** `jump-cancel-grab-out-of-shield`
- **What:** Against Falco's aerial -> shine pressure, Jigglypuff jumps out of shield and cancels the jump squat with grab ([jump cancel](../techniques/jump-cancel.md)), which avoids the shine and grabs him [lib:The Melee Puff Bible].
- **Inputs:** While shielding: jump, then Z during jump squat (or up + Z).
- **Timing:** Standing grab is active on frames 7-8 [wiki:Jigglypuff_(SSBM)/Grab]. Works reliably against Falco; against Fox it needs more distance because Fox's shine is wider [lib:The Melee Puff Bible]. Jump-cancel usmash (frame 7 [fd]) is an alternative but loses to double shine [lib:The Melee Puff Bible].
- **Used for:** Escaping and punishing shield pressure, leading to up throw.
- **Common errors:** Plain shield grab (gets shined); pressing Z late (she jumps).
- **Drill idea:** Falco CPU does aerial -> shine on shield with varied spacing; success if the grab connects.

## Neutral game

- **Core plan:** hover at the edge of the opponent's threat range, put bair in front of their approach, drift back if nothing happens, take space when they retreat. Bair is "not very good in itself"; its value comes from combining it with drift [lib:The Melee Puff Bible].
- **Full-hop "C" nair:** drift in during the rise, back before landing; nair is active on frames 6-28 and auto-cancels after frame 28 [fd], so a full-hop nair lands lag-free. It pokes heads and shields and stuffs jumps. Delay the nair until the apex so the hitbox lasts until landing [lib:The Melee Puff Bible].
- **Short-hop nair** covers horizontal space against heavy dash dancing; only follow up directly if it hits low on the body [lib:The Melee Puff Bible].
- **Side platform "reset":** jumping to a side platform (about full-hop height) lets her threaten the same space as a full hop while choosing when to come down; the inner edge of the platform is the best spot [lib:The Melee Puff Bible].
- **Full hop then fast-fall fade-back:** if the opponent is not already within about one Battlefield platform length when she full hops, they cannot punish a fade-back landing on reaction [lib:The Melee Puff Bible].
- **Low pokes at close dash dancers:** deep low uair, bair or Pound. Low uair starts kill combos; Pound out-ranges and leads to uair or stage control [lib:The Melee Puff Bible].
- **Shield poking:** shields last about 3.6 seconds from full; each hit shortens that and Pound counts double; utilt pokes feet, cross-up uair pokes heads, dair pokes depleted shields and platforms from below [lib:The Melee Puff Bible].
- **Crouch and wavedash back** on the ground instead of shielding when possible; her shield is a liability because of the shield-break KO.
- **What she does not do:** run at people, or drift forward on the way up into a sword.

## Punish game

Any hit that sends the opponent upward near her is a Rest threat, and any hit that sends them sideways near the ledge is a wall-of-pain threat. At low percent she uses utilt, uair and up throw to set up Rest; at mid percent uair/fair strings and tech chases; at high percent dair into a smash, or throws off stage into edgeguards. Late (weak) fair combos well from mid percent into falling uair or Rest on bad DI [lib:The Melee Puff Bible].

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| Uthrow | Fox | 0-15% | SH uair -> grab/utilt/Rest (no DI / DI forward); SH bair (DI behind) | Flat stage; platform snap percents in the tech entry | [lib:The Melee Puff Bible] |
| Uthrow | Fox | 15-70% | Double-jump Rest (no DI); FH bair (DI behind); SH uair or FH auto-cancel nair -> grab/Rest (DI forward) | Falco same with 20/30% thresholds | [lib:The Melee Puff Bible] |
| Uthrow | Captain Falcon | 0% | FH instant uair -> Rest (very tight) or -> falling uair | Only with no/slight DI; full DI either side gives nothing direct | [lib:The Melee Puff Bible] |
| Uthrow | Captain Falcon | 12% / 36% / 60% | FH uair -> falling uair / -> double-jump uair or wall of pain / FH double-jump uair chains | No/slight DI | [lib:The Melee Puff Bible] |
| Utilt | Fox, Falco | 10-65% | Rest or grab (no DI); grab / dash attack / tech-chase (DI away) | 0-10%: grab (second utilt on Falco) | [lib:The Melee Puff Bible] |
| Utilt | Marth | 0-30%+ | SH Rest; 30%: FH (double jump) Rest; 50%: FH double-jump aerial into wall of pain | DI behind at 12%: SH bair auto-cancel -> Rest | [lib:The Melee Puff Bible] |
| Utilt | Peach | 0% / 12% | Rest / FH double-jump Rest (no DI) | DI out at 12%: FH bair -> falling bair | [lib:The Melee Puff Bible] |
| Low uair | Fox, Falco | 0-60% | Grab or Rest (no DI); grab (DI away) | 65%+: FH soft fair -> falling uair | [lib:The Melee Puff Bible] |
| Rising uair | Fox, Falco | 12% / 30% / 50% | Rest / Rest or falling uair / double-jump Rest or uair | Falco's second step starts at 35% | [lib:The Melee Puff Bible] |
| Low uair | Marth | 0% / 12-40% / 40-50% | utilt -> Rest / FH Rest / FH double-jump Rest | 50-65%: wall of pain | [lib:The Melee Puff Bible] |
| Low uair | Sheik | 0-30% | Rest / utilt / grab by DI | 30-50%: SH uair; 50%+: wall of pain | [lib:The Melee Puff Bible] |
| Utilt or uair | Fox, Falco | 30-50% (utilt), 24-50% (uair) | Dsmash | Semi-spike edgeguard starter; no easy Amsah tech | [lib:The Melee Puff Bible] |
| Dthrow | Fox | on stage | Fsmash or (utilt ->) Rest on DI in / no DI; wavedash forward tech chase on DI out | Fox can land on a platform from 60%, Falco from 0% | [lib:The Melee Puff Bible] |
| Dthrow | Sheik | any | Rest on DI in; platform tech-chase Rest on DI out | Uthrow gives nothing guaranteed on Sheik | [lib:The Melee Puff Bible] |
| Dair | Marth / Sheik, Peach / Jigglypuff | 63%+ / 67%+ / 56%+ | Usmash | Perfect execution; back of head hits first | [lib:The Melee Puff Bible] |
| Dair | Fox / Falco / Marth / Sheik, Peach / Jigglypuff | 100% / 103% / 107% / 108% / 92%+ | Fsmash | Perfect execution | [lib:The Melee Puff Bible] |
| Low bair | Fox, Marth | about 40-50% | Tech chase (Rest on tech in place) | Bair forces knockdown from about 40% | [lib:The Melee Puff Bible] |
| Bair near ledge | any, esp. Falco, Roy | low-mid | Wall of pain | Off-stage chain | [wiki:Wall_of_Pain] |
| Sing at ledge | grounded opponent | higher percent sleeps longer | Charged fsmash or Rest | Ledge-cancelled Sing only | [wiki:Jigglypuff_(SSBM)/Up_special] |

### Chain grabs and tech chases

- **Chain grabs:** none of note. The closest is uthrow -> regrab on Fox at 0%, documented in a library video [lib:Up-throw Regrab vs Fox] (not watched), and uthrow -> uair -> grab at 0-15% [lib:The Melee Puff Bible].
- **Tech chases:** central at 15-50% on fastfallers, where utilt and bair knock down [wiki:Jigglypuff_(SSBM)/Up_tilt][lib:The Melee Puff Bible]. Hover over the tech-in-place spot and react: tech in place -> Rest; tech roll -> aerial then grab; missed tech -> jab reset (fast-fall jab or dair) or stand outside getup-attack range. On platforms after uthrow: at 0-15% it is a 50/50 between waveland grab (covers rolls) and full-hop reaction Rest (covers in place); from 15% a full hop to the in-place spot covers by reaction, with bair as the fallback for tech away [lib:The Melee Puff Bible]. Dthrow DI out: wavedash forward and react with dash attack or grab; tech roll away is not covered unless the ledge cuts it off [lib:The Melee Puff Bible].
- **What breaks them:** DI away on throws and launchers; teching on platforms; tech away toward open stage.

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Rest | any | KOs reliably from about 25%; under 15% on most characters from centre stage on legal stages; can KO at 0% in specific positions | 28%, frame 1, tiny hitbox at her centre; opponent should DI sideways | [wiki:Jigglypuff_(SSBM)/Down_special], [wiki:Rest], [fd] |
| Dair -> fsmash | Fox | 90% (Yoshi's Story, Fountain of Dreams), 105% (Battlefield), 110% (Final Destination, Pokemon Stadium), 115% (Dream Land) | From centre stage; true combo from 100% | [lib:The Melee Puff Bible] |
| Dair -> fsmash | Falco | 90% YS, 95% FoD, 100% BF, 105% FD/PS, 110% DL | From centre, grabbing ledge afterward | [lib:The Melee Puff Bible] |
| Dair -> usmash | Marth | 114% YS, 118% PS, 120% FD, 124% BF, 125% FoD, 139% DL | Centre stage, great DI; fsmash instead: 95-120% by stage | [lib:The Melee Puff Bible] |
| Dair -> usmash | Sheik | 117% YS, 121% PS, 124% FD, 128% BF/FoD, 142% DL | Centre stage, great DI | [lib:The Melee Puff Bible] |
| Dair -> usmash | Peach | 104% YS, 108% PS, 111% FD, 114% BF, 115% FoD, 128% DL | Centre stage, great DI | [lib:The Melee Puff Bible] |
| Dair -> usmash | Jigglypuff | 82% YS, 86% PS, 88% FD, 91% BF/FoD, 103% DL | Centre stage, great DI | [lib:The Melee Puff Bible] |
| Fsmash (clean) | any | Not sourced beyond the rows above | 17%, growth 118, clean on frames 12-15 | [fd], [wiki:Jigglypuff_(SSBM)/Forward_smash] |
| Bair / fair off stage | any | Low-mid percent via wall of pain | Depends on the opponent's recovery | [wiki:Wall_of_Pain] |
| Uair | floaties, midweights | Not sourced | 12%, straight up | [wiki:Jigglypuff_(SSBM)/Up_aerial], [fd] |
| Rollout (uncharged, inner hitbox) | any | Unknown | A small inner hitbox on uncharged Rollout has high knockback per the card description; thread not readable | [lib:Instant Rollout Kill Tech] |

- **Rest positioning:** the opponent's best DI on Rest is sideways (a side-blast-zone death or survival lets them come back before she wakes; a star KO off the top takes long enough for her to wake up) [wiki:Space_animal_slayer][wiki:Jigglypuff_(SSBM)/Down_special].
- **Edgeguards (general):** empty short hop near the ledge and react rather than committing early [lib:The Melee Puff Bible]. If the opponent must recover low, grab the ledge just before they can and use ledge intangibility to hit them, or drop -> double-jump fair -> regrab ("fair reset") [lib:The Melee Puff Bible].
- **vs Fox/Falco off stage:** watch for the first frame of Fire Fox / Illusion start-up; stay positioned to hit an early side B; if he must up B from below, grab the ledge and bair or roll as appropriate; if he double jumps toward the ledge, put a dair or fair in front of it [lib:The Melee Puff Bible].
- **vs Marth off stage:** grab the ledge as he falls below it; if he up-Bs onto the stage, drop -> double-jump Rest, or Sing to sleep him then ledgedash fsmash [lib:The Melee Puff Bible].
- **Bthrow / fthrow off stage:** start edgeguards; bthrow -> jump bair is not a true combo on Marth [lib:The Melee Puff Bible].
- **Juggling:** stay below the falling opponent and let them commit first rather than burning jumps on guesses [lib:The Melee Puff Bible].

## Recovery

- **Options:**
  - Five midair jumps [wiki:Jigglypuff_(SSBM)]; every jump gains height.
  - Side B (Pound) with up held (rising Pound): large horizontal distance, no helplessness [wiki:Pound].
  - Aerials during jumps protect her and adjust drift; a library thread is about aerials improving aerial control during recovery [lib:Using Aerials Helps Jigglypuff's Aerial Control] (not read).
  - Air dodge as a last burst (leaves her helpless).
  - Up B (Sing) gives no height at all; its only recovery use is enlarging her ledge-grab range and grabbing the ledge facing either way [wiki:Sing][wiki:Jigglypuff_(SSBM)/Up_special]. Neutral B (Rollout) in the air ends in helplessness [wiki:Rollout].
- **Mixups:** recover high (around top-platform height keeps the most options [lib:The Melee Puff Bible]); recover low to the ledge; fast fall, edge-cancel aerials or air dodge to slip past an opponent waiting below; hit the edgeguarder with bair/fair on the way in.
- **Weaknesses:** every hit matters at high percent because of her weight; a strong hit off stage after her jumps are spent leaves only Pounds; a predictable falling nair to protect her landing can be traded with deliberately [lib:The Melee Puff Bible]. A Rest or Sing used off stage is a self-destruct [wiki:Jigglypuff_(SSBM)/Down_special].

### Edgeguarding Jigglypuff

- Realistic goal: force her high or low and keep stage, not kill her outright. Against a high recovery, stay underneath, do not chase with reads unless it would kill, and punish over-committed fast falls; use a platform as a ceiling to uair her through [lib:The Melee Puff Bible].
- Against a low recovery: grab the ledge first and hit her with ledge intangibility [lib:The Melee Puff Bible].
- Against ledge stalling: use the three vulnerable timings listed under "Ledge refresh" and angled projectiles [lib:How to Combat Puff Planking].
- Ice Climbers have almost nothing but Ice Shots to catch her jumps, then an invincible rising dair/bair from the ledge [lib:20XX+XY].
- She is killed at the ledge by strong hits at percent, not by gimps: plan for an on-stage kill move when she lands or grabs the ledge.

## Defense and out of shield

- **Out-of-shield speeds:** jump squat 5 [wiki:Jigglypuff_(SSBM)]; so dair is out 10 frames after leaving shield, nair 11, fair 12 (aerial start-ups 5, 6, 7 [fd]; the same totals are quoted in [lib:20XX+XY]); bair and uair 14 (frame 9 [fd]). Jump -> Rest hits on the first airborne frame. Shield grab frames 7-8; jump-cancel usmash frame 7 [fd].
- **Avoid shielding for long:** shield break kills her [wiki:Jigglypuff_(SSBM)]. Prefer crouch, wavedash back, or a full hop away. A lightly-held ("slight") shield adds pushback with little extra shieldstun and can push her out of shine range [lib:The Melee Puff Bible].
- **Versus space-animal shield pressure:** jump-cancel grab out of shield (Falco), powershield or shield DI to avoid the shine, or accept the shine, which usually only resets neutral [lib:The Melee Puff Bible].
- **Crouch cancel:** useful at low percent, especially against Sheik (until dsmash breaks it at 55%) and Marth's non-spaced tilts [lib:The Melee Puff Bible].
- **SDI/ASDI:** at low percent in the air, an aerial out of hitstun; near the ground, SDI down then shield or grab; when jabbed before an up smash, SDI away then double jump or air dodge [lib:The Melee Puff Bible]. Below tumble percent she can SDI an aerial away to dodge the shine follow-up and grab the whiff [lib:The Melee Puff Bible]. See [SDI](../techniques/sdi.md) and [ASDI](../techniques/asdi.md).
- **Combo escapes:** she falls out of most combos on her own; double jump or bair out of hitstun.
- **After a missed Rest:** survival DI plus double-stick SDI on the punish; a library video shows this [lib:Jigglypuff Missed Rest Dual Stick Tech Survival DI] (not watched).

## As the training dummy

- **Weight / fall speed:** weight 60 (second lightest), fall speed 1.3 (slowest), fast-fall 1.6, gravity 0.064 (lowest) [wiki:Jigglypuff_(SSBM)]. She flies far from every hit; combos on her are one or two hits. Kill percents on her are low.
- **Chain grabs / tech chases on her:** effectively none. Ice Climbers' dthrow hand-off still works: she is released on frame 22 and the regrab window is frames 22-24 [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].
- **Fox up throw -> up air:** the standard kill on her. Fresh two-hit uair after uthrow kills her (bad throw DI, good survival DI) from these pre-throw percents: Yoshi's Story 39%, Pokemon Stadium 42%, Final Destination 44%, Battlefield 49%, Fountain of Dreams 49%, Dream Land 61%; a single-hit uair about 5% later [lib:The Melee Puff Bible]. Strong choices for a realistic CPU: DI the throw behind Fox (takes the least laser damage), then repeated SDI away from Fox's side on the uair; a perfectly centred two-hit uair needs 2 SDI inputs in 3 frames to escape, an off-centre one only 1 [lib:The Melee Puff Bible].
- **Falco up throw:** SDI the lasers upward [lib:The Melee Puff Bible].
- **Marth grab:** DI down and away; expect a fthrow/dthrow 50/50; the goal is avoiding the tipper, not avoiding regrabs [lib:The Melee Puff Bible].
- **Crouch behaviour:** a realistic CPU crouches briefly under grabs and low lasers (see the crouch tech entry) and punishes with utilt/grab/Rest.
- **Rest punish (she is asleep):** Rest lasts 249 frames with intangibility on frames 1-26 [wiki:Jigglypuff_(SSBM)/Down_special]; the punisher has time for a fully charged smash or a setup. Ice Climbers use a backward-facing usmash, or a grab combo (Blizzard -> grab + pummel -> ftilt -> pummel -> Blizzard -> pummel -> ftilt = 32% before the finisher) [lib:20XX+XY][web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]. Other characters' optimal punishes are not sourced here.
- **Shield:** breaking it kills her; Pound-like shield damage moves and multi-hits are stronger against her than against other characters.
- **Thresholds:** her own bair forces tech on Fox/Marth from about 40%; Sheik's dsmash beats her crouch cancel from 55% [lib:The Melee Puff Bible].

## Matchup notes

### vs Fox

Fox kills her with up throw -> up air (percent table above) and out-runs her; she kills him with up throw -> Rest, utilt/uair -> Rest and edgeguards. Her tools: side-platform resets, full-hop fast-fall fade-backs, the retreating short-hop nair bait, and low spaced bair / empty-hop pressure on a cornered or shielding Fox [lib:The Melee Puff Bible]. A library video analyses whether the matchup is "solved" [lib:Has the Fox - Jigglypuff matchup been solved???] (not watched).

### vs Falco

Lasers are the problem: do not jump from the ground without frame advantage; crouch-powershield low lasers, wavedash or dash under them, and SDI a laser into the ground when airborne (4 frames of landing instead of stun; laser stun is 12 frames) [lib:The Melee Puff Bible]. Jump-cancel grab out of shield largely neutralises his shield pressure. Combos on Falco are those on Fox with slightly shifted percents, and his recovery makes every off-stage hit lethal [lib:The Melee Puff Bible].

### vs Marth

Marth's grab and sword punish forward drift, so she rises neutrally and only drifts forward on the way down [lib:The Melee Puff Bible]. His shield is weak against her: after a low aerial she buffers crouch and cannot be shield grabbed, and utilt/uair poke it. Off stage Marth is "probably dead" with good execution [lib:The Melee Puff Bible]. Her risks are grab -> tipper and being pushed under a side platform.

### vs Sheik

Shallow auto-cancelled bairs beat Sheik's pokes through disjoint; Sheik answers with falling aerials, needles, dtilt under her descent and platform play [lib:The Melee Puff Bible]. Sheik cannot grab a crouching Jigglypuff, and dsmash can be Rested out of shield or crouch. Up throw gives nothing guaranteed; dthrow -> Rest on DI in [lib:The Melee Puff Bible].

### vs Peach

Heavily in Jigglypuff's favour; SSBWiki calls it Peach's hardest counter matchup [wiki:Peach_(SSBM)]. Corner Peach, stay out of the roughly 45-degree zone under-forward of a floating Peach (float-cancel fair), wait out the float, and Rest dash attacks out of shield or crouch. A stitch-face turnip is the main danger (about a 1/58 pull) [lib:The Melee Puff Bible].

### vs Captain Falcon

Falcon's speed means she cannot adjust on reaction; she pushes forward on the ground to limit his dash back, beats approaches with shallow short-hop bair, and crosses him up with uair from close range. His short-hop nair cannot hit her crouch. Up throw only leads to something with no/slight DI [lib:The Melee Puff Bible].

### vs Ice Climbers

Avoid being grabbed; attack Nana. Grabbing Popo leaves Nana passive, so uthrow Popo then bair-chain or Rest Nana; fthrow hits both if unsure which one was grabbed [lib:20XX+XY]. Pound catches their wavedashes and damages shields. Nana's Blizzard out-ranges bair and is the Climbers' main answer [lib:20XX+XY].

### vs Jigglypuff

When close, stay lower than the other Jigglypuff and punish whiffed rising aerials; when ahead, zone with in-place or retreating bairs; do not approach with bair. Dair is the key move (out of shield, out of the corner), leading to grab or usmash from 60% [lib:The Melee Puff Bible].

## Drill seeds

### Up throw Rest decision on fastfallers

- **id:** `jigglypuff-uthrow-rest`
- **Goal:** Read DI after up throw and choose Rest, uair -> Rest, bair, or nothing.
- **Player:** Jigglypuff
- **CPU:** [Fox](fox.md), [Falco](falco.md), [Captain Falcon](captain-falcon.md)
- **Setup:** Final Destination, centre. Jigglypuff starts holding the CPU in a grab. CPU percent chosen from 0-70%.
- **CPU behaviour:** DI on the throw chosen at random from: none, forward, behind, full away. Acts (double jump / shine / air dodge) on its first actionable frame.
- **Success:** With no DI, Rest connects (frame-1 hit while overlapping) before the CPU acts. With DI, the flowchart follow-up for that percent band lands (e.g. short-hop uair at 0-15% DI forward, full-hop bair on DI behind at 15%+).
- **Fail:** Rest whiffs, or the CPU acts before being hit.
- **Variations:** Platform stages (the CPU lands on the top platform at the snap percents and must be tech-chased); Falco thresholds (20/30%); require the uair -> Rest route at 30-50%.
- **Data needed:** Puff actionable frame after uthrow (32 Fox, 34 Falco [lib:The Melee Puff Bible]), uthrow knockback (not in the dump), victim hitstun and trajectories by DI, Rest hitbox size and frame, jump heights (full hop 20.8 [wiki:Jigglypuff_(SSBM)]), platform heights.

### Up tilt into Rest

- **id:** `jigglypuff-utilt-rest`
- **Goal:** Land utilt and convert to Rest on non-fastfallers at low percent.
- **Player:** Jigglypuff
- **CPU:** [Marth](marth.md), [Peach](peach.md), [Sheik](sheik.md), [Captain Falcon](captain-falcon.md)
- **Setup:** Flat stage. CPU standing just behind/over Jigglypuff's back at 0-30% (utilt hits behind and above).
- **CPU behaviour:** Stands or shields briefly, then drops shield. After being hit: random DI (none, forward, behind); double jumps or attacks when able.
- **Success:** Utilt hits and Rest connects with the correct jump (short hop at 0-12% on Marth; full hop or full hop + double jump at 12-30% on Marth/Peach).
- **Fail:** Rest whiffs or CPU escapes; for DI behind/out, success is instead the listed alternative (short-hop bair auto-cancel -> Rest on Marth at 12%).
- **Variations:** Start from a low uair instead; start from a shield-poke utilt on the CPU's back foot.
- **Data needed:** Utilt hit frames 8-14, knockback (base 40, growth 120) [fd], total 23 frames, victim weights, Rest overlap requirement.

### Wall of pain edgeguard

- **id:** `jigglypuff-wall-of-pain`
- **Goal:** Chain bairs off stage until the opponent cannot recover, then return.
- **Player:** Jigglypuff
- **CPU:** [Falco](falco.md), [Marth](marth.md), [Captain Falcon](captain-falcon.md), [Sheik](sheik.md), [Roy](roy.md)
- **Setup:** CPU launched from near the ledge, travelling outward at ledge height, at 40-70%. Jigglypuff on stage facing away from the ledge-side opponent (so bair points outward), all jumps available.
- **CPU behaviour:** DIs each bair randomly (up-and-in vs down-and-away), then recovers with its best option when out of hitstun.
- **Success:** At least three bairs connect, the CPU loses the stock, and Jigglypuff lands on stage or grabs the ledge.
- **Fail:** CPU reaches the ledge/stage, or Jigglypuff self-destructs.
- **Variations:** Start from a bthrow at the ledge; fair instead of bair when facing outward; CPU with/without double jump.
- **Data needed:** Bair frames 9-12, IASA 31, 12% (base 10, growth 100) [fd]; Puff air speed 1.35 and jump heights; CPU recovery distances; blast zones.

### Rest out of shield and crouch punishes

- **id:** `jigglypuff-rest-oos`
- **Goal:** Recognise the specific unsafe moves that can be Rested and execute jump/wavedash -> Rest.
- **Player:** Jigglypuff
- **CPU:** [Sheik](sheik.md), [Peach](peach.md), [Marth](marth.md), [Falco](falco.md)
- **Setup:** Jigglypuff shielding or crouching at centre stage (or on a side platform for the Marth utilt version, with Marth below).
- **CPU behaviour:** One of: Sheik dsmash at close range (sometimes spaced so the last hit whiffs, sometimes not); Peach dash attack; Marth dair on shield; Marth utilt through a platform; Falco dair on an airborne Jigglypuff below tumble percent. Mixed with safe moves (spaced tilts) that must not be Rested.
- **Success:** Rest connects on the punishable move; for safe moves, success is not Resting.
- **Fail:** Rest whiffs, or Jigglypuff is hit before Rest.
- **Variations:** Shield-drop Rest from platforms; out of crouch cancel instead of shield at low percent.
- **Data needed:** End lag of each CPU move, shieldstun, Puff jump squat 5 and wavedash length, Rest hitbox size; Sheik dsmash CC threshold 55% [lib:The Melee Puff Bible].

### Tech-chase Rest (WreckChase)

- **id:** `jigglypuff-techchase-rest`
- **Goal:** React to tech options from an empty short hop.
- **Player:** Jigglypuff
- **CPU:** [Fox](fox.md), [Falco](falco.md), [Captain Falcon](captain-falcon.md)
- **Setup:** CPU at 40-50% is hit by a low bair and lands in knockdown in front of Jigglypuff on a flat stage.
- **CPU behaviour:** Random: tech in place, tech toward, tech away, missed tech then (getup attack / roll / stand).
- **Success:** Tech in place -> Rest connects; tech roll -> aerial hits and a grab follows; missed tech -> jab reset then grab/Rest.
- **Fail:** CPU returns to neutral unhit, or Rest whiffs.
- **Variations:** Platform version after uthrow (full hop to the in-place spot); ledge behind the CPU so tech away is cut off.
- **Data needed:** Tech in place 26 frames and rolls 40 frames, vulnerable from frame 21 [lib:20XX+XY]; roll distances per character; Puff short hop height 9.146 [wiki:Jigglypuff_(SSBM)].

### Dair kill confirm

- **id:** `jigglypuff-dair-smash-confirm`
- **Goal:** Land a low dair and link usmash or fsmash at kill percent.
- **Player:** Jigglypuff
- **CPU:** [Marth](marth.md), [Sheik](sheik.md), [Peach](peach.md), [Fox](fox.md), [Jigglypuff](jigglypuff.md)
- **Setup:** CPU standing or shielding with a weakened shield, at or above the combo threshold (e.g. Marth 63%+ for usmash, Fox 100%+ for fsmash).
- **CPU behaviour:** After the dair's last hit: shields, jumps, or attacks on the first actionable frame.
- **Success:** The smash connects before the CPU acts (true combo) and kills at the listed stage percent.
- **Fail:** Missed L-cancel (30-frame landing), smash shielded or whiffed.
- **Variations:** "Spikestun" Rest when the last hit strikes the feet past about 45%; auto-cancel dair from a full hop; teeter-cancel version at a platform edge.
- **Data needed:** Dair hit timing and landing lag 30/15, usmash frame 7, fsmash frame 12 [fd]; thresholds and kill percents from [lib:The Melee Puff Bible]; stage blast zones.

### Crouch under grab

- **id:** `jigglypuff-crouch-vs-grab`
- **Goal:** Use crouch to make grabs whiff and punish, without crouching into a tilt at kill percent.
- **Player:** Jigglypuff
- **CPU:** [Marth](marth.md), [Sheik](sheik.md)
- **Setup:** Ground level, CPU at dash-grab range, Jigglypuff at 0-40%.
- **CPU behaviour:** Random: immediate dash grab; wait about half a second then dash grab (Marth only: this one connects on a held crouch); dtilt/ftilt; short-hop aerial.
- **Success:** Immediate grab whiffs and Jigglypuff punishes (grab, utilt, or Rest) within 20 frames; against the delayed grab she has already wavedashed back or jumped; tilts are crouch cancelled and punished.
- **Fail:** Grabbed, or knocked down.
- **Variations:** Falco laser version: crouch-powershield low lasers (about 8-frame window) or wavedash under them, then grab.
- **Data needed:** Grab box heights vs Puff crouch hurtbox (not in the dump; needs in-game measurement), Marth/Sheik grab frames, Puff utilt/grab frames.

### Sing at the ledge into a kill

- **id:** `jigglypuff-ledge-sing`
- **Goal:** Ledge-cancel Sing on an opponent landing at the edge, then finish.
- **Player:** Jigglypuff
- **CPU:** [Marth](marth.md), [Fox](fox.md), [Falco](falco.md)
- **Setup:** Jigglypuff holding the ledge. CPU recovers and lands on stage next to the ledge (e.g. Marth up B onto stage).
- **CPU behaviour:** Lands in its up B landing lag; mashes out of sleep at a configurable rate.
- **Success:** Jigglypuff drops, Sings while falling (hitbox frames 28-35), regrabs the ledge, CPU is asleep; then ledgedash or getup into charged fsmash or Rest that connects before the CPU wakes.
- **Fail:** Sing done while rising (no ledge cancel), CPU not asleep, or CPU wakes first.
- **Variations:** 2Drop from the stage for a fast edgehog instead; repeat Sing before finishing.
- **Data needed:** Sing hit frames [wiki:Jigglypuff_(SSBM)/Up_special]; sleep duration formula (unknown; flagged as missing on the wiki); ledge grab rules; fsmash charge frames 4-5 and hit frame 12.

### Surviving Fox's up throw up air

- **id:** `jigglypuff-survive-uthrow-uair`
- **Goal:** As Jigglypuff, DI the throw and SDI the up air to survive.
- **Player:** Jigglypuff
- **CPU:** [Fox](fox.md)
- **Setup:** Fox has Jigglypuff grabbed at a percent near the kill threshold for the stage (e.g. 44% on Final Destination).
- **CPU behaviour:** Up throw, then jumps and up airs, aiming the second hit at her centre.
- **Success:** Jigglypuff survives (SDI out of the second hit or lives through it).
- **Fail:** Stock lost.
- **Variations:** Stage list with the corresponding thresholds (39% Yoshi's Story ... 61% Dream Land); single-hit uair version (about 5% later).
- **Data needed:** Threshold table [lib:The Melee Puff Bible]; Fox uthrow/uair hitboxes and hitlag; SDI distance per input; ceiling heights.

### Rising Pound recovery

- **id:** `jigglypuff-rising-pound-recovery`
- **Goal:** Recover from far off stage using jumps and rising Pounds while avoiding an edgeguarder.
- **Player:** Jigglypuff
- **CPU:** [Marth](marth.md), [Fox](fox.md), [Captain Falcon](captain-falcon.md)
- **Setup:** Jigglypuff far off stage at a randomised height with 1-3 jumps left, at 80-120%.
- **CPU behaviour:** Waits near the ledge and attacks her arrival point; sometimes grabs the ledge.
- **Success:** She lands on stage or grabs the ledge without being hit.
- **Fail:** Stock lost or hit during the return.
- **Variations:** Recover high to top-platform height; go under the stage to the opposite ledge.
- **Data needed:** Pound movement (45 frames, displacement with up held; not in the dump), jump heights per midair jump (unknown), CPU hitbox reach at the ledge.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlPr.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/jigglypuff.json`](../framedata/jigglypuff.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 5-6 | 3 | Sakurai | 8 | 50 | - |  | 17 | 16 | 3 | -7 |  |
| Jab 2 | `jab2` | 6-7 | 3 | Sakurai | 16 | 50 | - |  | 20 | 17 | 3 | -7 | starts 1 frame late (included) |
| Dash attack | `dash_attack` | 4-8 | 12 | Sakurai | 16 | 100 | - |  | 39 | 39 | 7 | -27 |  |
|  |  | 9-14 | 8 | Sakurai | 8 | 100 | - |  |  |  | 5 | -24 |  |
| Forward tilt (angled up) | `ftilt_high` | 6-9 | 10 | Sakurai | 8 | 100 | - |  | 27 | - | 6 | -15 |  |
| Forward tilt | `ftilt` | 6-9 | 10 | Sakurai | 8 | 100 | - |  | 27 | - | 6 | -15 |  |
| Forward tilt (angled down) | `ftilt_low` | 6-9 | 10 | Sakurai | 8 | 100 | - |  | 27 | - | 6 | -15 |  |
| Up tilt | `utilt` | 8-9 | 9 | 96 | 40 | 120 | - |  | 23 | - | 6 | -9 |  |
|  |  | 10-14 | 8 | 88 | 40 | 120 | - |  |  |  | 5 | -8 |  |
| Down tilt | `dtilt` | 10-12 | 10 | 20 | 40 | 30 | - |  | 39 | 30 | 6 | -13 |  |
| Forward smash | `fsmash` | 12-15 | 17 | Sakurai | 10 | 118 | - |  | 44 | - | 9 | -23 | charge hold frame 4 |
|  |  | 16-20 | 13 | Sakurai | 6 | 105 | - |  |  |  | 7 | -21 |  |
| Up smash | `usmash` | 7-10 | 14/15 | 90 | 20 | 110 | - |  | 54 | 45 | 8 | -29 | charge hold frame 5 |
| Down smash | `dsmash` | 9-10 | 12 | 0 | 34 | 66 | - |  | 54 | 48 | 7 | -31 | charge hold frame 5; partly intangible 9-10 (2 bones) |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 6-7 | 12 | Sakurai | 10 | 70 | - |  | 49 | - | 7 | 20 | 10 | <6, >28 | -3 |  |
|  |  | 8-28 | 9 | Sakurai | 10 | 80 | - |  |  |  | 6 |  |  |  | -4 |  |
| Forward air | `fair` | 7-8 | 12/10 | Sakurai | 10 | 100 | - |  | 39 | 35 | 7 | 20 | 10 | <7, >33 | -3 |  |
|  |  | 9-22 | 7 | Sakurai | 10 | 80 | - |  |  |  | 5 |  |  |  | -5 |  |
| Back air | `bair` | 9-12 | 12 | Sakurai | 10 | 100 | - |  | 39 | 31 | 7 | 20 | 10 | <9, >24 | -3 |  |
| Up air | `uair` | 9-12 | 12 | 90 | 30 | 100 | - |  | 39 | 38 | 7 | 20 | 10 | <9, >36 | -3 |  |
| Down air | `dair` | 5-6, 8-9, 11-12, 14-15, 17-18, 20-21, 23-24, 26-27 | 2 | 270/30 | 20/10 | 100 | - |  | 49 | - | 2 | 30 | 15 | <5, >38 | -13 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 11-12 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 11 | 30 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 12 | 5 | 55 | 100 | 30 | - | - | 10 | 35 |  |
| Back throw | `bthrow` | 10 | 10 | 135 | 90 | 25 | - | - | 25 | 49 |  |
| Up throw | `uthrow` | 11 | 11 | 90 | 130 | 25 | - | - | 8 | 41 |  |
| Down throw | `dthrow` | 9 | 2 | 80 | 100 | 45 | - | - | 63 | 84 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Rollout, ground, StartR | `special_n_start_r` | - | - | - | - | - | - | - | 15 | - | - | - |  |
| Neutral B: Rollout, ground, StartL | `special_n_start_l` | - | - | - | - | - | - | - | 15 | - | - | - |  |
| Neutral B: Rollout, ground | `special_n` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Neutral B: Rollout, ground | `special_n_303` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Neutral B: Rollout, ground | `special_n_304` | 1-59 | 10 | 20 | 30 | 120 | - |  | 59 | - | 6 | - |  |
| Neutral B: Rollout, ground | `special_n_305` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Neutral B: Rollout, ground, EndR | `special_n_end_r` | - | - | - | - | - | - | - | 31 | - | - | - |  |
| Neutral B: Rollout, ground, EndL | `special_n_end_l` | - | - | - | - | - | - | - | 31 | - | - | - |  |
| Neutral B: Rollout, air, StartR | `special_air_n_start_r` | - | - | - | - | - | - | - | 15 | - | - | - |  |
| Neutral B: Rollout, air, StartL | `special_air_n_start_l` | - | - | - | - | - | - | - | 15 | - | - | - |  |
| Neutral B: Rollout, ground | `special_n_310` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Neutral B: Rollout, ground | `special_n_311` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Neutral B: Rollout, ground | `special_n_312` | 1-59 | 10 | 90 | 30 | 102 | - |  | 59 | - | 6 | - |  |
| Neutral B: Rollout, ground | `special_n_313` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Neutral B: Rollout, air, EndR | `special_air_n_end_r` | - | - | - | - | - | - | - | 31 | - | - | - |  |
| Neutral B: Rollout, air, EndL | `special_air_n_end_l` | - | - | - | - | - | - | - | 31 | - | - | - |  |
| Neutral B: Rollout, ground | `special_n_316` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Side B: Pound, ground | `special_s` | 12-27 | 13 | 90/120 | 52 | 75 | - |  | 45 | - | 7 | - |  |
| Side B: Pound, air | `special_air_s` | 12-27 | 13 | 90/120 | 52 | 75 | - |  | 45 | - | 7 | - |  |
| Up B: Sing, ground, L | `special_hi_l` | 28-125 | 0 | Sakurai | 0 | 100 | - | sleep | 179 | - | - | - |  |
| Up B: Sing, air, L | `special_air_hi_l` | 28-125 | 0 | Sakurai | 0 | 100 | - | sleep | 179 | - | - | - |  |
| Up B: Sing, ground, R | `special_hi_r` | 28-125 | 0 | Sakurai | 0 | 100 | - | sleep | 179 | - | - | - |  |
| Up B: Sing, air, R | `special_air_hi_r` | 28-125 | 0 | Sakurai | 0 | 100 | - | sleep | 179 | - | - | - |  |
| Down B: Rest, ground, L | `special_lw_l` | 1 | 28 | Sakurai | 78 | 120 | - | fire | 249 | - | 14 | - | intangible 1-26 |
| Down B: Rest, air, L | `special_air_lw_l` | 1 | 28 | Sakurai | 78 | 120 | - | fire | 249 | - | 14 | - | intangible 1-26 |
| Down B: Rest, ground, R | `special_lw_r` | 1 | 28 | Sakurai | 78 | 120 | - | fire | 249 | - | 14 | - | intangible 1-26 |
| Down B: Rest, air, R | `special_air_lw_r` | 1 | 28 | Sakurai | 78 | 120 | - | fire | 249 | - | 14 | - | intangible 1-26 |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-15 | - | 27 | 25 |  |
| Roll forward | `roll_forward` | intangible 2-18 | - | 34 | - |  |
| Roll backward | `roll_backward` | intangible 4-19 | - | 34 | - |  |
| Air dodge | `airdodge` | intangible 4-29 | - | 49 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-15 | 19-20, 24-25 (8/6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-18 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-20 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-26 | 20-21, 24-26 (8/6%) | 49 | - |  |
| Getup roll forward (face down) | `getup_roll_forward_facedown` | intangible 1-23 | - | 35 | - |  |
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-28 | - | 35 | - |  |
| Tech in place | `tech_in_place` | intangible 2-20 | - | 26 | - | starts 1 frame late (included) |
| Tech roll forward | `tech_roll_forward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Tech roll backward | `tech_roll_backward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Wall tech | `wall_tech` | - | - | 26 | - | starts 1 frame late (included) |
| Wall tech jump | `wall_tech_jump` | - | - | 40 | - | starts 1 frame late (included) |
| Ceiling tech | `ceiling_tech` | intangible 2-17 | - | 25 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-55 | - | 59 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 33 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-39 | 43-59 (6%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-15 | 19-23 (6%) | 55 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-53 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-28 | - | 49 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-17 | - | 17 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 30 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-14 | - | 14 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 24 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Shield grab | direct | 7 | `grab` |
| Up smash | jump cancel | 8 | `usmash` |
| Down air | jump | 10 | `dair` |
| Neutral air | jump | 11 | `nair` |
| Forward air | jump | 12 | `fair` |
| Back air | jump | 14 | `bair` |
| Up air | jump | 14 | `uair` |
| Up B | jump cancel | 29 | `special_hi_l` |
| Spot dodge | direct | intangible 2-15 of 27 | `spotdodge` |
| Roll forward | direct | intangible 2-18 of 34 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 34 | `roll_backward` |
| Wavedash | jump | actionable on frame 17 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Jigglypuff indexed by [The Melee Library](https://www.meleelibrary.com/#jigglypuff) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [Alex’s Puff Stuff](https://alexspuffstuff.blogspot.com/) | alexspuffstuff | A blog where Alex shares ideas and knowledge about Jigglypuff. |
| [The Melee Puff Bible](https://docs.google.com/document/d/1VN4LFZCqnq_0t-X9FkcTXD5GD4XjIW1vg7oT4jpVMhY/edit) | alexspuffstuff | Everything about Jigglypuff, in depth. |
| [2020 Jigglypuff Melee Techs Guide](https://www.youtube.com/watch?v=mr2RJ2CHjVw&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=24&t=0s) | Third Chair | Video guide on performing useful Jigglypuff tech in 2020. |
| [Is Aggressive Puff Play Practical](http://smashboards.com/threads/is-aggressive-puff-play-practical.398342/) | lots of people | Thread on SmashBoards discussing aggressive play with Jigglypuff. |
| [Jigglypuff Hitboxes and Frame Data](http://smashboards.com/threads/jigglypuff-hitbox-and-frame-data-nsf56k.303202/) | Stratocaster, Standardtoaster, and SuperDoodleMan |  |
| [Rest Setup Tutorial](https://www.youtube.com/watch?v=GbD_Q_RDxTE) | SSBM Tutorials |  |
| [Shielddrop Rest Punish Marth Utilt](https://www.youtube.com/watch?v=HghTnO5VXts) | Jigglypuff Tutorials | A very important if somewhat underused tech to punish Marth's up-tilt spam. |
| [Double Stick Techs - Magus is 'Sexy' =D](https://www.youtube.com/watch?v=Ei-iOIN32i4) | Magus | Video of various kill moves being [DSDI’d](http://smashboards.com/threads/we-3-magus420-plus-ds-tech-guide-12-17-pivot-guide-update.210133/page-2#post-6093911) as Jigglypuff to survive. The percents in the video are the limiting cases. Some of these moves are stale when used on Jigglypuff so the percentages may be slightly higher than with a fully un-stale move. |
| [Jigglypuff Missed Rest Dual Stick Tech Survival DI](https://www.youtube.com/watch?v=vZXdE0r2m4I) | Jigglypuff Tutorials |  |
| [Down-air to Rest True Combo](https://www.youtube.com/watch?v=57ynH7mqqF4) | Jigglypuff Tutorials |  |
| [Using Aerials Helps Jigglypuff’s Aerial Control](http://smashboards.com/threads/improved-recovery-f-air.118470/#post-2987122) | Magus and <π |  |
| [Puff Uptilt Shieldpoke Stuff + Research](https://www.youtube.com/watch?v=NkYEn7bPy4g) | SleepyK |  |
| [Every Hungrybox Rest](https://www.youtube.com/watch?v=wHn3FL9Drps) | notbob | A compilation video of every one of Hungrybox’s rests. Study for rest setups. |
| [Every Hungrybox Rest, Vol. 2](https://www.youtube.com/watch?v=Ilb4kFpA6g8) | notbob |  |
| [Every HungryBox Rest, Vol. 3](https://www.youtube.com/watch?v=XCeRm3OSyrE) | motbob |  |
| [Jigglypuff’s Invincible Ledgedash Options](https://www.youtube.com/watch?v=9Flj_QcVeQM) | Practical TAS | A video showcasing Jigglypuff’s options she can perform intangibly from a ledgedash. |
| [Sheik Down Smash to Rest out of Shield](https://www.youtube.com/watch?v=SuE-cIkr800) | Jigglypuff Tutorials |  |
| [Hungrybox shares some thoughts on the Puff vs Marth matchup](https://www.youtube.com/watch?v=h7IkCDl9Fqg) | Hungrybox and JigglyPuff Tutorials |  |
| [Up-throw Regrab vs Fox](https://www.youtube.com/watch?v=v2CtLe7Od9M) | Jigglypuff Tutorials | Combo options versus Fox at 0%. |
| [How To Use Jigglypuff’s Neutral Aerial](https://www.youtube.com/watch?v=9cDknSIc0Os) | SSBM Tutorials |  |
| [Oddities of Jigglypuff's Fthrow](https://www.reddit.com/r/smashbros/comments/4gex6m/can_we_talk_about_this_weird_di_summit_gf_spoilers/) | Schmooblidon | A technical deconstruction of Puff's Fthrow. |
| [Analyzing HungryBox's Grab Punish Game](https://bignokh.com/2016/07/08/analyzing-hungryboxs-punish-game/) | Anokh Palakurthi |  |
| [Jigglypuff 101 2006](http://smashboards.com/threads/jigglypuff-101-by-rpk-aka-pink-3.69949/) | RPK aka Pink=3 | A beginner level Jigglypuff guide. |
| [Mah0ne's Stuff about Puff](http://smashboards.com/threads/mah0nes-stuff-about-puff.298777/) | Mah0ne | Your generic stickied character guide. Try searching the thread, too. |
| [Mango’s Stuff about Puff](http://smashboards.com/threads/stuff-about-puff.177816/) | Mango | Old thread about how to play Jigglypuff. Some info might still be relevant. |
| [DendyPretendy's Jigglypuff Secret](https://www.youtube.com/watch?v=phhJHO0gRdI) | SSBM Tutorials | Grabbing the ledge in tricky ways using Puff's up-b. |
| [Technical Machine No. 44](https://www.youtube.com/watch?v=jGT-qx7vfqw) | Zappdos | Unconventional rest setups. |
| [Has the Fox - Jigglypuff matchup been solved??? SFat vs Hungrybox Analysis.](https://www.youtube.com/watch?v=XszU6TMxkIc) | Leffen |  |
| [How To Practice Jigglypuff](https://www.youtube.com/watch?v=ycpehXvkgsU) | SSBM Tutorials | They cover how to practice using aerials with various jumps, spacing, timing, and drift, practicing combos, and using the ledge. |
| [Instant Rollout Kill Tech](https://www.reddit.com/r/SSBM/comments/5iv8it/new_instant_rollout_kill_tech/) | Sanspeau and Schmooblidon | A small hidden hitbox inside Jigglypuff when she does rollout without charging has high knockback. |
| [How to Combat Puff Planking](https://alexspuffstuff.blogspot.com/2017/06/how-to-combat-puff-planking-and-save.html) | alexpuffstuff | Alexpuffstuff lists Puff's ledge options and steps through their vulnerabilities and weaknesses. |
| [10 Different Bairs](https://alexspuffstuff.blogspot.com/2017/06/10-different-bairs.html?m=1) | alexpuffstuff | 10 different ways to use Jigglypuff's bair. |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Jigglypuff (SSBM): https://www.ssbwiki.com/Jigglypuff_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Jigglypuff_(SSBM)/Down_special , /Up_special , /Back_aerial , /Up_aerial , /Up_tilt , /Up_smash , /Forward_smash , /Forward_aerial , /Neutral_aerial , /Down_aerial , /Grab , /Down_throw , /Forward_throw
- SSBWiki, Rest: https://www.ssbwiki.com/Rest
- SSBWiki, Sing: https://www.ssbwiki.com/Sing
- SSBWiki, Pound: https://www.ssbwiki.com/Pound
- SSBWiki, Rollout: https://www.ssbwiki.com/Rollout
- SSBWiki, Wall of pain: https://www.ssbwiki.com/Wall_of_Pain
- SSBWiki, Up throw Rest (Space animal slayer): https://www.ssbwiki.com/Space_animal_slayer
- SSBWiki, Peach (SSBM) (matchup statement): https://www.ssbwiki.com/Peach_(SSBM)
- SSBWiki, List of SSBM tier lists (NTSC) and Template:MeleeTiers: https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Melee Library card "The Melee Puff Bible" (alexspuffstuff), read in full: https://docs.google.com/document/d/1VN4LFZCqnq_0t-X9FkcTXD5GD4XjIW1vg7oT4jpVMhY/
- Melee Library card "How to Combat Puff Planking": https://alexspuffstuff.blogspot.com/2017/06/how-to-combat-puff-planking-and-save.html
- Melee Library card "20XX+XY" (Ice Climbers compendium; Jigglypuff matchup section, tech-chase data): https://docs.google.com/document/d/1DPqPLDHfBWMluMMfd8KpDVN8s37866CTb4xQVW-_KLk/
- Nicki / Nopia, "Ice Climbers Information and Data Sheet": https://docs.google.com/document/d/1e2WfuNH1I86On59O53FubxYzA-zYMZKZVIrCPNVEqhk/
- Melee Library "Jigglypuff" section: card titles and descriptions only for YouTube videos, Smashboards threads (403) and Reddit posts (blocked).
- Frame data dump: `Jigglypuff.json`
