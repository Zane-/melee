---
schema: melee-character/v1
id: ness
name: Ness
aliases: [PK Kid]
tier: "D (23rd of 26), 2021 tier list"
archetype: [floaty, combo-food, punish-heavy, mixup, technical]
related: [peach, yoshi, mewtwo]
summary: Ness wins by landing double-jump-cancelled aerials or a grab, comboing with forward air and up air, and killing with back throw, back air, up air or an edgeguard; he loses most stocks to his PK Thunder recovery.
key_tech: [double-jump-cancel, djc-fast-fall-l-cancel, psi-dash, back-throw-kill, uthrow-chain-grab, pk-thunder-2-recovery, pk-thunder-edgeguard, magnet-stall, pk-fire-confirm, yo-yo-glitch]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlNs.dat
framedata: ../framedata/ness.json
code: src/melee/ft/kinds/ftNess
specials:
  neutral_b: "PK Flash"
  side_b: "PK Fire"
  up_b: "PK Thunder"
  down_b: "PSI Magnet"
attributes:
  weight: 94
  gravity: 0.09
  fall_speed: 1.83
  fast_fall_speed: 2.2
  jump_squat: 4
  jumps: 2
  walk_speed: 0.84
  dash_speed: 1.3
  run_speed: 1.4
  traction: 0.06
  air_speed: 0.93
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [3, 20, 3]
  jab2: [4, 21, 2]
  jab3: [7, 31, 4]
  dash_attack: [8, 40, 5]
  ftilt_high: [7, 35, 12]
  ftilt_mid_high: [7, 35, 12]
  ftilt: [7, 35, 11]
  ftilt_mid_low: [7, 35, 11]
  ftilt_low: [7, 35, 10]
  utilt: [5, 32, 7]
  dtilt: [3, 14, 3]
  fsmash: [16, 50, 24]
  usmash: [12, 49, 9]
  dsmash: [12, 59, 11]
  nair: [5, 36, 11]
  fair: [8, 40, 5]
  bair: [10, 36, 16]
  uair: [8, 42, 13]
  dair: [20, 60, 12]
  grab: [8, 31, 0]
  dash_grab: [10, 41, 0]
  pummel: [16, 25, 3]
  fthrow: [null, 53, 11]
  bthrow: [null, 53, 11]
  uthrow: [null, 56, 10]
  dthrow: [10, 50, 4]
  special_n_start: [null, 16, 0]
  special_n_hold: [null, 7, 0]
  special_n_hold_301: [null, 7, 0]
  special_n_end: [null, 40, 0]
  special_air_n_start: [null, 16, 0]
  special_air_n_hold: [null, 7, 0]
  special_air_n_hold_305: [null, 7, 0]
  special_air_n_end: [null, 40, 0]
  special_s: [null, 70, 0]
  special_air_s: [null, 70, 0]
  special_hi_start: [null, 20, 0]
  special_hi_hold: [null, 10, 0]
  special_hi_end: [null, 30, 0]
  special_hi: [1, 70, 25]
  special_air_hi_start: [null, 20, 0]
  special_air_hi_hold: [null, 10, 0]
  special_air_hi_end: [null, 30, 0]
  special_hi_316: [1, 70, 25]
  special_lw_start: [null, 10, 0]
  special_lw_hold: [null, 20, 0]
  special_lw_hit: [null, 20, 0]
  special_lw_end: [null, 20, 0]
  special_air_lw_start: [null, 10, 0]
  special_air_lw_hold: [null, 20, 0]
  special_air_lw_hit: [null, 20, 0]
  special_air_lw_end: [null, 20, 0]
oos:  # option: frame the hitbox is out
  grab: 8
  nair: 9
  fair: 12
  uair: 12
  usmash: 13
  bair: 14
  dair: 24
resources: 6
# generated: end
---

# Ness

<!-- GENERATED:attributes -->
## Attributes

Read from `PlNs.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 94 |
| Gravity | 0.09 |
| Terminal fall speed | 1.83 |
| Fast-fall speed | 2.2 |
| Jump squat (frames before airborne) | 4 |
| Full hop / short hop initial Y speed | 2.5 / 1.5 |
| Air jump Y multiplier | 0.85 |
| Jumps | 2 |
| Walk max speed | 0.84 |
| Dash initial speed / run max speed | 1.3 / 1.4 |
| Ground friction (traction) | 0.06 |
| Air max horizontal speed | 0.93 |
| Air acceleration (base + stick) | 0.02 + 0.04 |
| Air friction | 0.03 |
| Normal landing lag | 4 |
| Shield size | 13.75 |
<!-- /GENERATED:attributes -->

## Overview

Ness is a mid-weight (94), below-average fall speed (1.83) character with short reach, a
4-frame jump squat and a delayed, "swooping" double jump [wiki:Ness_(SSBM)]. That double
jump is the centre of his game: starting an aerial during it cancels the upward movement,
so he can attack from just above the ground much faster than with a normal short hop. This
is the double jump cancel (DJC) [wiki:Double_jump_cancel]. In neutral he spaces forward air
(a disjointed multi-hit), uses dash attack as his one ranged ground poke, and looks for a
grab even though his grab range is the second shortest in the game [wiki:Ness_(SSBM)].
Off a hit or throw he strings fair, uair and nair together with DJC. He kills with back
throw (the second strongest throw in the game), sweetspot bair, uair, a tipper fsmash, or
by edgeguarding with fair, dair (a meteor) and PK Thunder [wiki:Ness_(SSBM)]. His recovery
is called arguably the worst in the game: PK Thunder must be steered into Ness himself
while he is helpless to act, and the opponent can simply touch the projectile to end it
[wiki:Ness_(SSBM)]. He has losing matchups across the cast and almost no top-level
representation [wiki:Ness_(SSBM)].

## Strengths and weaknesses

- **Strengths:**
  - DJC aerials: fast, low attacks with good hitstun; fair, nair and uair chain into each
    other [wiki:Ness_(SSBM)] [wiki:Double_jump_cancel].
  - All four throws are useful: fthrow has very high base knockback (edgeguard starter),
    bthrow kills reliably from about 130%, uthrow chain grabs fastfallers at low percent,
    dthrow starts combos [wiki:Ness_(SSBM)].
  - Strong single hits in the air: bair 16% clean, uair 13%, nair 11% [fd].
  - Dair has very high base knockback (90 [fd]) as a meteor: strong at 0% offstage.
  - Low traction (0.06) gives a quick, above-average wavedash [wiki:Ness_(SSBM)].
  - One of the few characters who can auto-cancel every aerial in a short hop (the wiki
    lists Ness, Luigi, Samus, Peach and Zelda) [wiki:L-canceling].
- **Weaknesses:**
  - Recovery: slow to start, linear, easily intercepted; an aerial used offstage spends
    the double jump [wiki:Ness_(SSBM)].
  - Range: tilts, grab and most aerials are short; dash grab is very laggy
    [wiki:Ness_(SSBM)].
  - Weak smashes: usmash and dsmash cannot kill below roughly 180-200%; fsmash needs the
    bat tip [wiki:Ness_(SSBM)].
  - Poor normal SHFFL (high short hop of 13.26 units, low fall speed) [wiki:Ness_(SSBM)].
  - Specials are situational: PK Fire is easy to SDI out of, PK Flash is slow, PSI Magnet
    only matters against energy projectiles [wiki:Ness_(SSBM)].
  - Loses to disjointed spacing, most of all [Marth](marth.md) [wiki:Ness_(SSBM)].

## Character tech

### Double jump cancel (DJC)

- **id:** `double-jump-cancel`
- **What:** Ness's double jump applies its upward force gradually. Starting an aerial
  attack during the double jump removes the remaining upward force, so Ness attacks while
  falling from very low height [wiki:Double_jump_cancel].
- **Inputs:** Jump, then double jump shortly after leaving the ground, then the aerial
  immediately. A common grip: X/Y for the first jump, tap jump or the other jump button
  for the second, C-stick for the aerial.
- **Timing:** Jump squat is 4 frames [wiki:Ness_(SSBM)]. The double jump must not be
  frame-perfect after leaving the ground: an instant double jump cancel lands before any
  aerial's hitbox comes out [wiki:Double_jump_cancel]. Hit frames: nair 5, fair 8, uair 8,
  bair 10, dair 20 [fd].
- **Used for:** Almost every aerial Ness does on stage: approaching fair, combo uair and
  nair, shield-poking bair, landing aerials on platforms.
- **Common errors:** Double jumping too early (lands with no hitbox); too late (rises to
  full double jump height); doing it offstage and losing the double jump needed to
  recover.
- **Drill idea:** Stationary CPU; success is a DJC aerial hitting within a set number of
  frames of leaving the ground and Ness landing actionable.

### DJC fast fall L-cancel

- **id:** `djc-fast-fall-l-cancel`
- **What:** After the DJC aerial starts, Ness can fast fall almost immediately and
  L-cancel the landing, which is faster than a SHFFL (short hop fast fall L-cancel)
  [wiki:Double_jump_cancel].
- **Inputs:** Jump, double jump, aerial, tap down, press L/R/Z within 7 frames before
  landing (see [L-cancel](../techniques/l-cancel.md)).
- **Timing:** Landing lag normal / L-cancelled: nair 22 / 11, fair 18 / 9, bair 18 / 9,
  uair 18 / 9, dair 28 / 14 [fd]. Alternatively land in an auto-cancel window for 4
  frames of landing: fair auto-cancels before frame 8 and from frame 30; uair before 8
  and from 27; bair before 10 and from 25; dair before 20 and from 29
  [wiki:Ness_(SSBM)/Forward_aerial] [wiki:Ness_(SSBM)/Up_aerial]
  [wiki:Ness_(SSBM)/Back_aerial] [wiki:Ness_(SSBM)/Down_aerial].
- **Used for:** Shield pressure, combo links such as fair into grab, repeated uairs.
- **Common errors:** Missing the L-cancel on nair (22 frames); fast falling before the
  multi-hit fair finishes so the launching last hit does not come out.
- **Drill idea:** CPU shields; success is DJC fair on shield followed by a grab or second
  aerial before the CPU's shield grab comes out.

### Psi dash (DJC dair auto-cancel movement)

- **id:** `psi-dash`
- **What:** Dair has no hitbox and auto-cancels for its first 19 frames
  [wiki:Ness_(SSBM)/Down_aerial]. Jump, double jump and dair with a fast fall produces a
  short, quick hop with no attack and almost no landing lag, usable as movement and out of
  shield [lib:Offensive and defensive applications of foot+dj cancelling aka Psi dashing].
- **Inputs:** Diagonal tap jump (or X/Y), second jump with the other hand as early as
  possible after jump squat, C-stick down, fast fall. From shield the tap jump angle is
  narrower because diagonals roll.
- **Timing:** The thread's author estimates about 10 frames in total for a perfect one
  and states he had not verified it; treat as [unverified]. Dair's hitbox does not appear
  until frame 20 [fd], so landing before then gives the normal 4-frame landing.
- **Used for:** Micro-spacing, getting onto platforms without air dodge lag, a fast
  out-of-shield movement option.
- **Common errors:** Missing the second jump (full hop dair); missing the C-stick (plain
  double jump); hitting B on the way to the C-stick (accidental PK Fire/Thunder); not
  fast falling so dair's hitbox comes out and he lands with 28 frames of lag. Any failure
  also burns the double jump.
- **Drill idea:** CPU swings at Ness's shield at intervals; success is a psi dash out of
  shield that avoids the next hit and a punish landing afterwards.

### Back throw kill

- **id:** `back-throw-kill`
- **What:** Bthrow does 11% with extremely low base knockback and very high growth, so it
  is weak early and a kill throw late; it is the second strongest throw in Melee and
  kills reliably from 130% [wiki:Ness_(SSBM)].
- **Inputs:** Grab (frame 7 [fd]), optionally pummel, hold back.
- **Timing:** The throw releases on frame 27 of a 52-frame animation at baseline weight
  (throw speed depends on the opponent's weight) [wiki:Ness_(SSBM)/Back_throw].
- **Used for:** Closing stocks when Ness's smashes cannot. Near the ledge at lower
  percent it sets up bair, dair or PK Fire offstage [web:smashboards.com Ness guide].
- **Common errors:** Whiffing the short grab (standing grab total 29 frames, dash grab 39
  [fd]); throwing toward the far blast zone; opponent DIs up-and-in to survive.
- **Drill idea:** CPU at 120-150% shields near the ledge; success is grab, turn the right
  way, bthrow, KO.

### Up throw chain grab on fastfallers

- **id:** `uthrow-chain-grab`
- **What:** Uthrow (10%) can be regrabbed on [Fox](fox.md), [Falco](falco.md) and
  [Captain Falcon](captain-falcon.md) at low percent [wiki:Ness_(SSBM)].
- **Inputs:** Grab, uthrow, step under the falling opponent, grab again; switch to utilt
  or DJC uair when they start flying too high.
- **Timing:** Uthrow releases on frame 36 of 55 at baseline weight
  [wiki:Ness_(SSBM)/Up_throw]. Exact percent windows: Unknown (the wiki says only "low
  percentages").
- **Used for:** Early damage on the characters Ness otherwise struggles to hit; uthrow
  also sets up platform tech chases and PK Thunder juggles [wiki:Ness_(SSBM)].
- **Common errors:** Regrab too late (opponent lands and shines or jumps); short grab
  range missing a DI'd opponent.
- **Drill idea:** CPU Fox at 0% with random DI; success is three consecutive regrabs or
  a regrab into utilt/uair.

### PK Thunder 2 recovery

- **id:** `pk-thunder-2-recovery`
- **What:** Up B creates a steerable lightning ball. Steering it into Ness launches him in
  the direction opposite the side that was hit; this is PK Thunder 2 (PKT2), his only
  real distance recovery and a 25% hit [wiki:PK_Thunder].
- **Inputs:** Up B, then rotate the control stick to loop the ball around and into Ness
  from the side opposite the desired travel direction (hit from below-left to fly
  up-right).
- **Timing:** PKT2's hitbox is 25% for frames 1-12 and 20% for frames 13-43 of a 69-frame
  animation [fd]. Ness is intangible for the first half of the move [wiki:Ness_(SSBM)]. He
  cannot move or act while steering the ball [wiki:PK_Thunder]. It ends in special fall if
  it finishes in the air, and has heavy lag if he lands on stage [wiki:Ness_(SSBM)].
- **Used for:** Recovery; also a risky kill move (KOs around 75-90%
  [wiki:PK_Thunder] [wiki:Ness_(SSBM)]).
- **Common errors:** Wrong angle (flies under the stage lip, especially on Battlefield
  [wiki:Ness_(SSBM)]); ball hits a wall or the opponent and disappears; overshooting onto
  the stage and being punished.
- **Drill idea:** Ness starts offstage at a random position with no double jump; success
  is grabbing the ledge with PKT2. Add a CPU that tries to touch the ball.

### PK Thunder edgeguard and juggle

- **id:** `pk-thunder-edgeguard`
- **What:** The ball's head does 8% and knocks the target in the direction of contact; the
  tail does 1% and stuns [wiki:PK_Thunder] [wiki:Ness_(SSBM)]. Steered offstage it hits
  recovering opponents; low and far from the stage the hitstun alone can prevent a return
  [web:smashboards.com Ness guide].
- **Inputs:** Up B from on stage, steer the head into the opponent from the stage side or
  from above.
- **Timing:** The head disappears when it hits an opponent [wiki:Ness_(SSBM)]; a
  shield can be passed through because the hitbox only re-hits every 48 frames
  [wiki:PK_Thunder]. Ness is stuck in place while steering.
- **Used for:** Gimping fastfallers' up B and side B, catching up B start-up with the
  tail, harassing after an uthrow [wiki:Ness_(SSBM)].
- **Common errors:** Using it at close range and being hit during the steering; hitting
  the opponent toward the stage.
- **Drill idea:** CPU Fox/Falco recovers from below; success is the head hitting them
  away or down so they fail to return.

### Magnet stall

- **id:** `magnet-stall`
- **What:** Down B (PSI Magnet) in the air halts Ness's fall for a moment, like a
  reflector stall, changing his landing or recovery timing [wiki:Ness_(SSBM)]
  [wiki:PSI_Magnet].
- **Inputs:** Down B in the air; hold to keep it out.
- **Timing:** Absorption is active from frame 10 with a minimum of 30 frames held, then
  ending lag; minimum animation 59 frames [wiki:Ness_(SSBM)/Down_special]. Heals 2.0x the
  absorbed projectile's damage [wiki:Ness_(SSBM)/Down_special].
- **Used for:** Mixing up descent from high up [web:smashboards.com Ness guide];
  absorbing Falco/Fox lasers, Samus charge shot, Mewtwo shadow ball and similar energy
  projectiles.
- **Common errors:** Using it low to the stage where the long animation is punished; it
  does nothing against physical projectiles (needles, turnips, bombs).
- **Drill idea:** CPU Falco fires lasers from across the stage; success is absorbing a
  set number without being hit by the follow-up approach.

### PK Fire confirm

- **id:** `pk-fire-confirm`
- **What:** Side B fires a bolt (2%) that bursts into a multi-hit fire pillar (3% then
  2% per hit) on contact, holding the opponent briefly [wiki:Ness_(SSBM)].
- **Inputs:** Side B on the ground (travels forward) or in the air (travels diagonally
  down; can be edge-cancelled). Follow with grab, fair or a throw toward the ledge.
- **Timing:** Animation 69 frames [fd]. Short reach for a projectile and easy to SDI out
  of [wiki:Ness_(SSBM)]. Near the ledge: PK Fire, fthrow, then dair is a documented gimp
  sequence, though DI on the fthrow avoids the dair [wiki:PK_Fire].
- **Used for:** Punishing landings at mid range, stopping approaches, gimping fastfallers.
- **Common errors:** Using it at point-blank or on shield (very punishable); the opponent
  SDIs out before the follow-up.
- **Drill idea:** CPU lands at mid range with random SDI; success is PK Fire into a grab
  before the CPU escapes.

### Yo-yo glitch

- **id:** `yo-yo-glitch`
- **What:** A bug in up smash leaves the yo-yo's hitbox active where it was after the move
  ends. Ness's next non-projectile attack (or grab) then also hits anything between Ness
  and that spot, and some attacks can be "worn" as a body hitbox (jackets)
  [wiki:Yo-yo_glitch]. Works in all versions.
- **Inputs:** Hit an opponent or damageable object with up smash's outreaching or spinning
  yo-yo, keep charging, and release in the window below. Then use any attack or grab
  ("deadline"), or PKT2 into the floor/ledge for the Thunder Jacket.
- **Timing:** If the outreaching hit connects, charge 6-11 more frames after the hit; with
  an unstaled up smash that means releasing A between the 24th and 29th frame of the
  move including hitlag. If the spinning hit connects, charge 7-12 frames
  [wiki:Yo-yo_glitch]. Each opponent can be hit only once by the stored hitbox, and Ness's
  next set of hitboxes cannot hit that opponent [wiki:Yo-yo_glitch].
- **Used for:** A one-time long-range hit or grab; mostly a novelty in tournament play.
- **Common errors:** Releasing outside the window (normal up smash); using a projectile
  special does not consume it but getting KO'd clears it.
- **Drill idea:** A target (or CPU) at yo-yo range; success is the game state showing the
  lingering hitbox, verified by a grab connecting from across the stage.

## Neutral game

- Fair is the main poke: disjointed sparks, first hit frame 8, last hit launches
  (growth 135) [fd]. Auto-cancel it from a short hop, then immediately DJC another
  [web:smashboards.com Ness guide].
- Dash attack: three hits on frames 8, 15 and 22 [fd], good disjointed range and his only
  reliable ground approach; laggy on shield [wiki:Ness_(SSBM)].
- Wavedash and dash dance to bait, then grab. Grab is frame 7 [fd] but very short.
- PK Fire at mid range to stop approaches or catch landings.
- Utilt (frame 5, 7% [fd]) as an anti-air and juggle starter; Ness's head is intangible
  early in the move [wiki:Ness_(SSBM)].
- Dtilt is 13 frames total with a frame 3 hitbox [fd]; it can be mashed to repeat and
  locks some characters against walls [wiki:Ness_(SSBM)].
- Ness depends on stage control and tends to roll in when cornered, which is punishable
  when expected [wiki:Ness_(SSBM)].
- What he wants: the opponent above him or between him and the ledge; platforms for DJC
  movement.

## Punish game

Ness's combos are aerial chains kept low with DJC. Fair and nair start, uair juggles,
bair/uair/bthrow finish. Fastfallers and Marth take the longest strings; he struggles to
combo Peach, Samus, the Ice Climbers and Jigglypuff [web:smashboards.com Ness guide].
Few percent windows are documented; rows without percents are typical.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| uthrow | Fox, Falco, Captain Falcon | low (window Unknown) | regrab | chain grab | [wiki:Ness_(SSBM)] |
| uthrow | fastfallers | low-mid | utilt, DJC uair; platform tech chase | | [wiki:Ness_(SSBM)] |
| dthrow | most | low-mid | DJC fair or uair | fire hits whiff on Mr. Game & Watch | [wiki:Ness_(SSBM)] |
| dthrow | most | high | uair (kills) | | [wiki:Ness_(SSBM)] |
| dash attack | all but Jigglypuff | mid | uair | | [web:smashboards.com Ness guide] |
| dash attack | fastfallers, Marth | mid | fair, fair | | [web:smashboards.com Ness guide] |
| fair | most | low | grab, dthrow, fair | | [web:smashboards.com Ness guide] |
| dair | fastfallers | low-mid | utilt, then any aerial | hard to land against good DI | [web:smashboards.com Ness guide] |
| utilt | fastfallers | low | utilt, DJC uair | | [wiki:Ness_(SSBM)] |
| usmash swing | most | mid-high | aerial | almost no knockback, odd combo starter | [wiki:Ness_(SSBM)] |
| PK Fire | most | any | grab or fair | SDI escapes | [wiki:Ness_(SSBM)] |

### Chain grabs and tech chases

Uthrow chain grabs Fox, Falco and Captain Falcon at low percent [wiki:Ness_(SSBM)];
percent limits and the DI that breaks it were not found. Tech chase options from a
knockdown: on tech toward Ness, DJC nair or dair (into utilt on fastfallers); on tech
away, dash attack, DJC fair, or dair on a hard read; on tech in place, dash attack, nair
or grab [web:smashboards.com Ness guide].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| bthrow (11%) | most | 130%+ | "reliably"; earlier near the ledge | [wiki:Ness_(SSBM)] |
| PK Thunder 2 (25%) | most | about 75-90% | very risky, long start-up | [wiki:PK_Thunder] [wiki:Ness_(SSBM)] |
| fair last hit | offstage opponents | under about 130% | offstage | [wiki:Ness_(SSBM)] |
| uair (13%) | Peach | from about 110% | Final Destination, Battlefield, Yoshi's Story | [web:smashboards.com Ness guide] |
| bair clean (16%) | most | Unknown | sweetspot frames 10-11 only | [fd] |
| fsmash bat tip (24%) | most | Unknown | tip only; weak otherwise; frame 16 | [wiki:Ness_(SSBM)] [fd] |
| dair (12%, meteor) | offstage opponents | any (very high base knockback) | cannot kill grounded opponents even at 200%; meteor cancellable | [wiki:Ness_(SSBM)] |
| PK Flash (11-36%) | offstage, predictable recoveries | Unknown | very slow; edgeguard only | [wiki:Ness_(SSBM)] |

- Edgeguards: fthrow or bthrow at the ledge, then fair/bair/dair offstage; PK Thunder
  steered into the recovery; charged up smash yo-yo hanging over the ledge
  [wiki:Ness_(SSBM)].
- Up smash and down smash do not kill below about 180-200% and are not finishers
  [wiki:Ness_(SSBM)].
- Fsmash's close hitbox reflects projectiles for 2 frames; not practical
  [wiki:Ness_(SSBM)].

## Recovery

- **Options:**
  - Double jump: one of the highest, with a curved path; Ness can drift a long way during
    it [wiki:Ness_(SSBM)].
  - Air dodge to the ledge or stage.
  - PK Thunder 2: long distance, intangible for the first half, 25% hitbox
    [wiki:Ness_(SSBM)].
  - PSI Magnet to stall the fall when high [web:smashboards.com Ness guide].
- **Mixups:** Recover high with double jump and drift so PK Thunder is not needed; vary
  where the ball loops (above, below, behind); aim PKT2 at the ledge, onto the stage or
  onto a platform; bounce PKT2 off a wall to change direction or shorten it
  [wiki:PK_Thunder].
- **Weaknesses:** Any aerial during the double jump cancels it [wiki:Ness_(SSBM)]. While
  steering, Ness cannot defend. The ball vanishes if it touches an opponent, the stage or
  a destroying projectile, leaving Ness helpless. PKT2 is linear, can slide under stage
  lips, and has long landing lag [wiki:Ness_(SSBM)].

### Edgeguarding Ness

- **Touch the ball.** A character with a good recovery ([Jigglypuff](jigglypuff.md),
  [Samus](samus.md)) jumps into the PK Thunder head, takes 8% and minor knockback, and
  Ness falls helpless [wiki:Ness_(SSBM)].
- **Destroy or absorb the ball.** [Link](link.md)'s boomerang and the
  [Ice Climbers](ice-climbers.md)' Ice Shot remove it without the user taking damage
  [wiki:Ness_(SSBM)]; [Mr. Game & Watch](mr-game-and-watch.md) can bucket it
  [web:smashboards.com Flatten the Opposition].
- **Hit Ness before the loop completes.** PK Thunder has long start-up; any offstage
  aerial works while he steers.
- **Intercept PKT2.** It travels in a straight line: [Mario](mario.md)'s cape or Link's
  Spin Attack meet it as he arrives [wiki:Ness_(SSBM)]; the second half of the move is
  not intangible.
- **Punish the landing.** If PKT2 ends on stage, Ness is in heavy lag; charge a smash
  [wiki:Ness_(SSBM)].
- **Bait the double jump.** Threatening him offstage makes him use an aerial, which
  cancels the double jump.
- A realistic CPU Ness should recover high when it can and vary the PK Thunder loop
  direction.

## Defense and out of shield

- Out of shield: nair is the usual option (4-frame jump squat [wiki:Ness_(SSBM)] plus a
  frame 5 hitbox [fd], so frame 9), with roll and wavedash out of shield as escapes; fair,
  bair, dair, DJC uair and grab are too slow or too short against good pressure
  [web:smashboards.com Ness guide]. Shield grab is frame 7 [fd] but short.
- Psi dash out of shield is a movement escape rather than a hit.
- [Crouch cancel](../techniques/crouch-cancel.md) into dtilt (frame 3 [fd]) or grab works
  at low percent given his weight of 94.
- Combo escapes: nair (frame 5), double jump (he keeps drift control, but losing it
  offstage is fatal), air dodge. Landing options: DJC aerial, dair auto-cancel, air dodge
  [web:smashboards.com Ness guide].
- What beats him: disjointed spacing (Marth), fast shield pressure (Fox, Falco), and any
  hit that sends him offstage without a jump.

## As the training dummy

- Weight 94, fall speed 1.83, fast-fall 2.2 [wiki:Ness_(SSBM)]: a mid-weight on the
  floaty side. Short, with a small hurtbox.
- [Sheik](sheik.md)'s dthrow chain throws him (he is on the wiki's list of characters she
  chain throws from low to mid/high percent) [wiki:Chain_grab].
- A CPU Ness recovering should behave like the real thing: double jump first, then PK
  Thunder looped into himself; this is the standard target for "hit the PK Thunder" and
  "intercept PKT2" drills.
- His double jump is cancellable by his own aerials; a CPU that attacks offstage will
  self-destruct in a realistic way.
- PSI Magnet heals 2.0x absorbed energy projectiles [wiki:Ness_(SSBM)/Down_special]: a
  CPU Ness can be set to absorb lasers for projectile-discipline drills.
- Strong DI choices: away and up against kill throws; SDI is less relevant because few
  characters use long multi-hits on him.

## Matchup notes

### vs Marth

- The matchup the wiki singles out as worst: Marth's sword outranges every Ness aerial,
  so DJC approaches are swatted, and Marth's fair/dtilt/dair cover the PK Thunder recovery
  [wiki:Ness_(SSBM)].
- Ness's wins come from whiff-punish grabs and long fair strings (Marth is one of the
  characters fair-fair works on [web:smashboards.com Ness guide]).

### vs Fox and Falco

- Their speed and shine pressure beat his slow out-of-shield options
  [web:smashboards.com Ness guide]. Falco's lasers can be absorbed with PSI Magnet, but
  the animation is long [wiki:PSI_Magnet].
- Ness's reward is high when he connects: uthrow chain grab at low percent
  [wiki:Ness_(SSBM)], utilt and uair juggles, and gimps with dair, PK Thunder or PK Fire
  [web:smashboards.com Ness guide] [wiki:Ness_(SSBM)].

### vs Sheik

- Sheik chain grabs him [wiki:Chain_grab] and needles interrupt PK Thunder steering.
  Ness needs the first hit and a bthrow at kill percent.

### vs Jigglypuff, Peach, Samus

- Floaties he cannot combo [web:smashboards.com Ness guide] and who edgeguard him by
  touching the ball [wiki:Ness_(SSBM)]. Uair kills Peach from about 110% on small stages
  [web:smashboards.com Ness guide]. Hungrybox tried Ness against Armada's Young Link at
  Apex 2013 and lost both games [wiki:Young_Link_(SSBM)].

### vs Mr. Game & Watch

- G&W's bucket absorbs PK Fire, PK Thunder and PK Flash
  [web:smashboards.com Flatten the Opposition], and Ness's dthrow fire hits whiff on him
  [wiki:Ness_(SSBM)].

## Drill seeds

### DJC forward air pressure

- **id:** `ness-djc-fair-pressure`
- **Goal:** Consistent low DJC fair with fast fall and L-cancel, into a second action.
- **Player:** Ness
- **CPU:** Marth, Sheik, Fox (any shielding CPU)
- **Setup:** Final Destination, CPU shielding at fair range, 0%.
- **CPU behaviour:** Holds shield, then shield grabs or rolls at a random time after the
  first aerial.
- **Success:** DJC fair hits shield, Ness lands (L-cancel or auto-cancel) and a second
  DJC aerial or grab comes out before the CPU's shield grab.
- **Fail:** Ness is grabbed, the aerial has no hitbox before landing (instant DJC), or
  Ness rises to full double jump height.
- **Variations:** CPU not shielding (must combo fair into grab or fair); cross-up bair
  shield poke; on a platform.
- **Data needed:** Jump squat 4, fair hit frames and landing lag 18/9, auto-cancel
  windows, double jump physics, CPU shield grab frame.

### Up throw chain grab on spacies

- **id:** `ness-uthrow-chaingrab`
- **Goal:** Regrab Fox/Falco/Falcon after up throw at low percent.
- **Player:** Ness
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** Ness holding the CPU in grab at 0%, centre stage, Final Destination.
- **CPU behaviour:** Random DI (none, left, right); on landing or when actionable it
  shines / jumps / attacks.
- **Success:** At least three regrabs, or a regrab followed by utilt or DJC uair.
- **Fail:** CPU acts before the regrab; grab whiffs.
- **Variations:** Find the highest percent it still works at (the window is not
  documented; the drill can log it); end with a platform tech chase.
- **Data needed:** Uthrow knockback and release frame (36 of 55 at baseline), Ness grab
  frame 7 and range, opponent fall speeds and weights.

### Back throw kill at the ledge

- **id:** `ness-bthrow-kill`
- **Goal:** Land the short grab and throw the correct way at kill percent.
- **Player:** Ness
- **CPU:** Marth, Sheik, Peach, Fox
- **Setup:** CPU at 120-160% within a few steps of a ledge, facing random direction.
- **CPU behaviour:** Shields, spot dodges or pokes at random; DIs the throw up-and-in.
- **Success:** Bthrow sends the CPU off the nearer blast zone for a KO.
- **Fail:** Grab whiff punished, wrong throw direction, CPU survives.
- **Variations:** Centre stage (find the kill percent per character and stage); require a
  wavedash or dash-dance grab.
- **Data needed:** Bthrow knockback values, CPU weights, stage blast zones, grab range.

### PK Thunder 2 to the ledge

- **id:** `ness-pkt2-recovery`
- **Goal:** Aim PKT2 from any offstage position.
- **Player:** Ness
- **CPU:** none, then Marth / Sheik / Jigglypuff as edgeguarder
- **Setup:** Ness offstage at a random position (below, level, above; near or far), no
  double jump, 60%.
- **CPU behaviour:** Base: none. Advanced: jumps out to touch the ball, or waits to hit
  the PKT2 path, or charges a smash at the landing spot.
- **Success:** Ness grabs the ledge or lands and shields before being hit.
- **Fail:** Death, helpless fall, or hit on landing.
- **Variations:** Battlefield (lip catches low angles); with double jump available; wall
  bounce required.
- **Data needed:** PK Thunder ball speed and turn rate, PKT2 travel distance, intangible
  frames, 69-frame animation, ledge geometry.

### Edgeguard Ness (player is the opponent)

- **id:** `ness-edgeguard-the-thunder`
- **Goal:** Learn the three answers to PK Thunder: touch the ball, hit Ness, intercept
  PKT2.
- **Player:** any character (Marth, Fox, Sheik, Jigglypuff, Link most instructive)
- **CPU:** Ness
- **Setup:** CPU Ness launched offstage at 50-100% with or without double jump.
- **CPU behaviour:** Double jump toward the stage if available, then PK Thunder looped
  from a random side into himself, aimed at the ledge or the stage.
- **Success:** Ness loses the stock without the player being hit by PKT2.
- **Fail:** Ness returns, or the player is hit by the 25% PKT2.
- **Variations:** Restrict the player to one method; Ness recovers high.
- **Data needed:** PK Thunder head damage 8%, disappearance on contact, PKT2 hitbox
  frames 1-12 / 13-43.

### Offstage down air and forward air gimps

- **id:** `ness-offstage-gimp`
- **Goal:** Hit recovering fastfallers with fair or the dair meteor and still get back.
- **Player:** Ness
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** CPU thrown off the ledge by fthrow at 30-70%; Ness on stage at the ledge
  with double jump.
- **CPU behaviour:** Random recovery: jump then up B, side B, immediate up B.
- **Success:** CPU KO'd and Ness returns to the stage.
- **Fail:** Ness dies (double jump spent, no PKT2 room) or the CPU returns.
- **Variations:** PK Thunder only from stage; PK Fire offstage.
- **Data needed:** Dair frames 20-28 and meteor knockback (base 90, growth 70), fair
  frames, Ness double jump cancel behaviour offstage.

### Psi dash out of shield

- **id:** `ness-psi-dash-oos`
- **Goal:** Execute jump, double jump, dair auto-cancel as an escape.
- **Player:** Ness
- **CPU:** Fox, Falco, Marth
- **Setup:** Ness in shield, CPU in front at 0%.
- **CPU behaviour:** Hits the shield with an aerial, then follows with shine/grab/jab
  after a short random gap.
- **Success:** Ness leaves shield with a psi dash, lands with no dair hitbox out and is
  not hit; bonus for a punish.
- **Fail:** Hit, dair hitbox comes out (frame 20+), or full hop / plain double jump.
- **Variations:** Onto a platform; direction left/right/neutral.
- **Data needed:** Dair auto-cancel window 1-19, jump squat 4, double jump cancel
  physics, shield stun of the CPU's move.

### Tech chase fastfallers after down throw

- **id:** `ness-techchase`
- **Goal:** Cover tech options with dash attack, DJC aerials and grab.
- **Player:** Ness
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** CPU knocked down at Ness's feet at 20-60% (from uthrow onto a platform or a
  low dair).
- **CPU behaviour:** Random: tech in place, tech toward, tech away, missed tech with
  getup option.
- **Success:** A hit or grab lands before the CPU is actionable.
- **Fail:** CPU escapes or hits Ness.
- **Variations:** On Battlefield/Yoshi's Story platforms; restrict to regrab.
- **Data needed:** CPU tech timings and distances, dash attack frames 8/15/22, Ness dash
  speed 1.3.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlNs.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/ness.json`](../framedata/ness.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 3-4 | 3 | Sakurai | 8 | 50 | - |  | 19 | - | 3 | -13 |  |
| Jab 2 | `jab2` | 4-5 | 2 | 70 | 8 | 50 | - |  | 20 | - | 2 | -14 | starts 1 frame late (included) |
| Jab 3 | `jab3` | 7-8, 9-10 | 4 | Sakurai | 16 | 100 | - |  | 30 | - | 3 | -20 | starts 1 frame late (included) |
| Dash attack | `dash_attack` | 8 | 5 | 0/100/Sakurai | 60/18 | 70/100 | 60/0 | electric | 41 | 40 | 4 | -27 |  |
|  |  | 15 | 4 | 20 | 0 | 70 | 60 | electric |  |  | 3 | -21 |  |
|  |  | 22 | 4 | 100 | 70 | 100 | - | electric |  |  | 3 | -14 |  |
| Forward tilt (angled up) | `ftilt_high` | 7-11 | 12 | Sakurai | 12 | 100 | - |  | 34 | - | 7 | -20 |  |
| Forward tilt (slightly up) | `ftilt_mid_high` | 7-11 | 12 | Sakurai | 12 | 100 | - |  | 34 | - | 7 | -20 |  |
| Forward tilt | `ftilt` | 7-11 | 11 | Sakurai | 12 | 100 | - |  | 34 | - | 6 | -21 |  |
| Forward tilt (slightly down) | `ftilt_mid_low` | 7-11 | 11 | Sakurai | 12 | 100 | - |  | 34 | - | 6 | -21 |  |
| Forward tilt (angled down) | `ftilt_low` | 7-11 | 10 | Sakurai | 12 | 100 | - |  | 34 | - | 6 | -21 |  |
| Up tilt | `utilt` | 5-9 | 7 | 96 | 42 | 126 | - |  | 39 | 32 | 5 | -21 | partly intangible 5-6 (1 bone) |
| Down tilt | `dtilt` | 3-5 | 3 | 0 | 4 | 50 | - |  | 13 | - | 3 | -7 |  |
| Forward smash | `fsmash` | 16-17 | 18/20/22/24 | Sakurai | 50 | 62 | - |  | 49 | - | 12 | -21 | charge hold frame 10 |
| Up smash | `usmash` | 12-14 | 9 | 70 | 80 | 80 | - |  | 49 | 49 | 6 | -30 |  |
|  |  | 15-31 | 6 | 80 | 60 | 45 | - |  |  |  | 4 | -29 |  |
| Down smash | `dsmash` | 12 | 11 | 70 | 70 | 80 | - |  | 61 | 59 | 6 | -40 |  |
|  |  | 13-31 | 7 | 70 | 70 | 60 | - |  |  |  | 5 | -40 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 5-12 | 11 | Sakurai | 15 | 100 | - |  | 39 | 36 | 6 | 22 | 11 | <5, >26 | -5 |  |
|  |  | 13-23 | 8 | Sakurai | 0 | 100 | - |  |  |  | 5 |  |  |  | -6 |  |
| Forward air | `fair` | 8-10, 11-13, 14-16, 17-19 | 3/2 | Sakurai | 16 | 100 | - | electric | 41 | 40 | 3 | 18 | 9 | <8, >29 | -6 |  |
|  |  | 20-21 | 5 | Sakurai | 24 | 135 | - | electric |  |  | 4 |  |  |  | -5 |  |
| Back air | `bair` | 10-11 | 16 | Sakurai | 16 | 100 | - | electric | 39 | 36 | 9 | 18 | 9 | <10, >24 | +0 |  |
|  |  | 12-19 | 10 | Sakurai | 0 | 100 | - |  |  |  | 6 |  |  |  | -3 |  |
| Up air | `uair` | 8-11 | 13 | 85 | 13 | 109 | - |  | 45 | 42 | 7 | 18 | 9 | <8, >26 | -2 |  |
| Down air | `dair` | 20-28 | 12 | 270 | 90 | 70 | - |  | 59 | - | 7 | 28 | 14 | <20, >28 | -7 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 8-9 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 10-11 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 16 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 11 | 11 | 45 | 120 | 10 | - | - | 27 | 52 |  |
| Back throw | `bthrow` | 11 | 11 | 135 | 15 | 130 | - | - | 27 | 52 |  |
| Up throw | `uthrow` | 10 | 10 | 90 | 105 | 40 | - | - | 36 | 55 |  |
| Down throw | `dthrow` | 9 | 4 | 70 | 90 | 30 | - | fire | 30 | 49 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: PK Flash, ground, Start | `special_n_start` | - | - | - | - | - | - | - | 15 | - | - | - |  |
| Neutral B: PK Flash, ground, Hold | `special_n_hold` | - | - | - | - | - | - | - | 6 | - | - | - |  |
| Neutral B: PK Flash, ground, Hold | `special_n_hold_301` | - | - | - | - | - | - | - | 6 | - | - | - |  |
| Neutral B: PK Flash, ground, End | `special_n_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Neutral B: PK Flash, air, Start | `special_air_n_start` | - | - | - | - | - | - | - | 15 | - | - | - |  |
| Neutral B: PK Flash, air, Hold | `special_air_n_hold` | - | - | - | - | - | - | - | 6 | - | - | - |  |
| Neutral B: PK Flash, air, Hold | `special_air_n_hold_305` | - | - | - | - | - | - | - | 6 | - | - | - |  |
| Neutral B: PK Flash, air, End | `special_air_n_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Side B: PK Fire, ground | `special_s` | - | - | - | - | - | - | - | 69 | - | - | - | spawns article/projectile on 20 |
| Side B: PK Fire, air | `special_air_s` | - | - | - | - | - | - | - | 69 | - | - | - | spawns article/projectile on 20 |
| Up B: PK Thunder, ground, Start | `special_hi_start` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Up B: PK Thunder, ground, Hold | `special_hi_hold` | - | - | - | - | - | - | - | 9 | - | - | - |  |
| Up B: PK Thunder, ground, End | `special_hi_end` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Up B: PK Thunder, ground | `special_hi` | 1-10 | 25 | Sakurai | 60 | 70 | - | electric | 69 | - | 13 | - | intangible 1-10 |
|  |  | 11-37 | 20 | Sakurai | 45 | 65 | - | electric |  |  | 10 | - |  |
| Up B: PK Thunder, air, Start | `special_air_hi_start` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Up B: PK Thunder, air, Hold | `special_air_hi_hold` | - | - | - | - | - | - | - | 9 | - | - | - |  |
| Up B: PK Thunder, air, End | `special_air_hi_end` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Up B: PK Thunder, ground | `special_hi_316` | 1-10 | 25 | Sakurai | 60 | 70 | - | electric | 69 | - | 13 | - | intangible 1-10 |
|  |  | 11-37 | 20 | Sakurai | 45 | 65 | - | electric |  |  | 10 | - |  |
| Down B: PSI Magnet, ground, Start | `special_lw_start` | - | - | - | - | - | - | - | 9 | - | - | - |  |
| Down B: PSI Magnet, ground, Hold | `special_lw_hold` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Down B: PSI Magnet, ground, Hit | `special_lw_hit` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Down B: PSI Magnet, ground, End | `special_lw_end` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Down B: PSI Magnet, air, Start | `special_air_lw_start` | - | - | - | - | - | - | - | 9 | - | - | - |  |
| Down B: PSI Magnet, air, Hold | `special_air_lw_hold` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Down B: PSI Magnet, air, Hit | `special_air_lw_hit` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Down B: PSI Magnet, air, End | `special_air_lw_end` | - | - | - | - | - | - | - | 19 | - | - | - |  |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-18 | - | 27 | 25 |  |
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
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-19 | - | 35 | - |  |
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
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-36 | 39-41 (10%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-20 | 24-36 (8/6%) | 55 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-56 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-27 | - | 49 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-18 | - | 18 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 29 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-14 | - | 14 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 23 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Shield grab | direct | 8 | `grab` |
| Neutral air | jump | 9 | `nair` |
| Forward air | jump | 12 | `fair` |
| Up air | jump | 12 | `uair` |
| Up smash | jump cancel | 13 | `usmash` |
| Back air | jump | 14 | `bair` |
| Down air | jump | 24 | `dair` |
| Spot dodge | direct | intangible 2-18 of 27 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 16 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Ness indexed by [The Melee Library](https://www.meleelibrary.com/#ness) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Ness Techs Guide](https://www.youtube.com/watch?v=oFnSUL2ZI-U&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=6&t=0s) | Third Chair | Video guide on performing useful Ness tech in 2020. |
| [Ness Melee Chaingrab Guide](https://www.youtube.com/watch?v=FtDKPPCAjYg&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=10&t=0s) | Third Chair |  |
| [Offensive and defensive applications of foot+dj cancelling aka Psi dashing](https://smashboards.com/threads/offensive-and-defensive-applications-of-foot-dj-cancelling-aka-psi-dashing.382932/) | Ganreizu |  |
| [Yo-Yo Glitch and Jackets](http://supersmashbros.wikia.com/wiki/Yoyo_glitch) | community | An explanation of what the yo-yo glitch does and the jackets you can attach to Ness using the glitch. |
| [The Yo-yo Glitch: Cracked](https://smashboards.com/threads/the-yo-yo-glitch-cracked-update-faq-now-in-first-post.48717/) | Reik and Dan Smith | A explanation of how to activate the yo-yo glitch. Find frame data in the Ness hitboxes and frame data thread. |
| [New methods to get Ness' Throw Jacket + new variation of it](https://www.reddit.com/r/SSBM/comments/5iby88/new_methods_to_get_ness_throw_jacket_new/) | audiodrummerguy |  |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Ness (SSBM): https://www.ssbwiki.com/Ness_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Ness_(SSBM)/Back_throw , /Forward_throw ,
  /Up_throw , /Down_throw , /Down_aerial , /Forward_aerial , /Up_aerial , /Back_aerial ,
  /Neutral_aerial , /Down_special
- SSBWiki, Double jump cancel: https://www.ssbwiki.com/Double_jump_cancel
- SSBWiki, PK Thunder (includes PK Thunder 2): https://www.ssbwiki.com/PK_Thunder
- SSBWiki, PK Fire: https://www.ssbwiki.com/PK_Fire
- SSBWiki, PSI Magnet: https://www.ssbwiki.com/PSI_Magnet
- SSBWiki, PK Flash: https://www.ssbwiki.com/PK_Flash
- SSBWiki, Yo-yo glitch (includes Thunder Jacket and other jackets):
  https://www.ssbwiki.com/Yo-yo_glitch
- SSBWiki, L-canceling: https://www.ssbwiki.com/L-canceling
- SSBWiki, Chain grab: https://www.ssbwiki.com/Chain_grab
- SSBWiki, List of SSBM tier lists (NTSC): https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Melee Library card "Offensive and defensive applications of foot+dj cancelling aka Psi
  dashing" (Ganreizu), via web.archive.org:
  https://smashboards.com/threads/offensive-and-defensive-applications-of-foot-dj-cancelling-aka-psi-dashing.382932/
- Smashboards user guide "Ness" (short, user-written, low rating), via web.archive.org:
  https://smashboards.com/guides/ness.1057/
- Smashboards "Flatten The Opposition: A Game and Watch Guide" (bucket absorb list), via
  web.archive.org:
  https://smashboards.com/threads/flatten-the-opposition-a-game-and-watch-guide.346291/
- Frame data dump: `fd/json/Ness.json`
- Not readable: the two Third Chair video cards; "The Yo-yo Glitch: Cracked" thread (not
  fetched; the wiki page cites it); the reddit Throw Jacket post (blocked).
