---
schema: melee-character/v1
id: kirby
name: Kirby
aliases: []
tier: "F (25th of 26), 2021 tier list (13th, PG Stats)"
archetype: [floaty, lightweight, edgeguarder, mixup]
related: [jigglypuff]
summary: Kirby wins by crouching under attacks, poking with fast tilts, and turning a back air, up air, down throw tech chase or a sacrificial throw off the ledge into a stock, because he cannot approach or combo reliably.
key_tech: [crouch-and-tilt-poking, up-tilt-juggle, down-throw-tech-chase, fence-of-pain, kirbycide-throws, swallowcide, inhale-and-copy, dash-attack-cancelled-grab, multi-jump-recovery]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlKb.dat
framedata: ../framedata/kirby.json
code: src/melee/ft/kinds/ftKirby
specials:
  neutral_b: "Swallow (Inhale)"
  side_b: "Hammer"
  up_b: "Final Cutter"
  down_b: "Stone"
attributes:
  weight: 70
  gravity: 0.08
  fall_speed: 1.6
  fast_fall_speed: 2
  jump_squat: 3
  jumps: 6
  walk_speed: 0.85
  dash_speed: 1.4
  run_speed: 1.4
  traction: 0.08
  air_speed: 0.78
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [3, 16, 3]
  jab2: [3, 17, 4]
  rapid_jab_start: [null, 8, 0]
  rapid_jab_loop: [1, 20, 1]
  rapid_jab_end: [null, 10, 0]
  dash_attack: [9, 60, 8]
  ftilt_high: [5, 28, 11]
  ftilt: [5, 28, 11]
  ftilt_low: [5, 28, 11]
  utilt: [4, 24, 8]
  dtilt: [4, 30, 10]
  fsmash_high: [13, 50, 15]
  fsmash: [13, 50, 15]
  fsmash_low: [13, 50, 15]
  usmash: [13, 50, 15]
  dsmash: [7, 50, 14]
  nair: [10, 50, 10]
  fair: [10, 40, 8]
  bair: [6, 36, 14]
  uair: [11, 36, 15]
  dair: [18, 55, 3]
  grab: [7, 31, 0]
  dash_grab: [11, 41, 0]
  pummel: [10, 31, 3]
  fthrow: [null, 62, 8]
  bthrow: [null, 50, 8]
  uthrow: [null, 80, 10]
  dthrow: [10, 88, 7]
  special_n: [17, 20, 1]
  special_n_loop: [1, 18, 1]
  special_n_end: [null, 20, 0]
  special_n_loop_308: [null, 18, 0]
  special_n_drink: [null, 30, 8]
  special_n_spit: [null, 30, 10]
  special_n_320: [17, 20, 1]
  special_n_loop_321: [1, 18, 1]
  special_s: [22, 60, 23]
  special_air_s: [7, 70, 4]
  special_hi1: [null, 23, 0]
  special_hi2: [1, 35, 8]
  special_hi3: [null, 5, 0]
  special_hi4: [null, 34, 0]
  special_air_hi1: [null, 23, 0]
  special_air_hi2: [1, 35, 8]
  special_air_hi3: [null, 5, 0]
  special_air_hi4: [null, 34, 0]
  special_lw1: [null, 29, 0]
  special_lw2: [null, 31, 0]
  special_lw2_334: [null, 31, 0]
  special_air_lw1: [null, 29, 0]
  special_air_lw2: [1, 31, 18]
  special_air_lw2_337: [null, 31, 0]
oos:  # option: frame the hitbox is out
  grab: 7
  bair: 9
  nair: 13
  fair: 13
  uair: 14
  usmash: 14
  dair: 21
resources: 3
# generated: end
---

# Kirby

<!-- GENERATED:attributes -->
## Attributes

Read from `PlKb.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 70 |
| Gravity | 0.08 |
| Terminal fall speed | 1.6 |
| Fast-fall speed | 2 |
| Jump squat (frames before airborne) | 3 |
| Full hop / short hop initial Y speed | 2 / 1.5 |
| Air jump Y multiplier | 0 |
| Jumps | 6 |
| Walk max speed | 0.85 |
| Dash initial speed / run max speed | 1.4 / 1.4 |
| Ground friction (traction) | 0.08 |
| Air max horizontal speed | 0.78 |
| Air acceleration (base + stick) | 0.02 + 0.04 |
| Air friction | 0.02 |
| Normal landing lag | 4 |
| Shield size | 14.7 |
<!-- /GENERATED:attributes -->

## Overview

Kirby is a small, light, floaty character (weight 70 in NTSC, fall speed 1.6) with six jumps in total and very poor air speed (0.78, tied third-worst) [wiki:Kirby_(SSBM)]. He was ranked 25th of 26 on the 2021 tier list [wiki:List_of_SSBM_tier_lists_(NTSC)]. His real assets are a very low crouch that ducks many attacks, fast tilts (up tilt and down tilt both hit on frame 4 [fd]), an above-average grab range, a strong back air and up air, and a decent off-stage game with multiple jumps [wiki:Kirby_(SSBM)].

His problems are structural: almost no approach (slow in the air, short [wavedash](../techniques/wavedash.md), short range, no projectile, a laggy dash attack), an unreliable punish game with few guaranteed follow-ups, weak or awkward kill moves, and very low survivability: he dies early off both the top and the sides and his recovery is slow and predictable [wiki:Kirby_(SSBM)]. Kirby players therefore play defensively on the ground, wait for the opponent to come to them, and rely on reads: tech chases, edgeguards, and "Kirbycides" (carrying the opponent off stage with a throw or Inhale so both lose a stock). He is mechanically simple but has to out-think opponents to win.

## Strengths and weaknesses

- **Strengths:**
  - Low crouch and small hurtbox: ducks most jabs and many grabs/aerials; large shield relative to his body, so he is hard to shield-poke [wiki:Kirby_(SSBM)].
  - Fast tilts: utilt frame 4, dtilt frames 4-7, ftilt frames 5-8 [fd].
  - Bair: clean hit on frames 6-8 for 14%, late hit to frame 20, 7 frames of L-cancelled landing lag [fd]; his best all-round move [wiki:Kirby_(SSBM)/Back_aerial].
  - Uair: 15% on frames 11-13, the third-strongest up aerial in the game, sends horizontally [wiki:Kirby_(SSBM)/Up_aerial][fd].
  - Above-average grab range; down throw starts tech chases [wiki:Kirby_(SSBM)].
  - Off-stage presence: five midair jumps, bair chains ("fence of pain"), a multi-hit meteor dair [wiki:Kirby_(SSBM)].
  - Sacrificial KOs at any percent via throws or Inhale [wiki:Kirbycide].
- **Weaknesses:**
  - No approach: poor [SHFFL](../techniques/shffl.md) (floaty, high short hop), low air speed, short range [wiki:Kirby_(SSBM)].
  - No reliable combos; follow-ups are reads [wiki:Kirby_(SSBM)][lib:20XX+XY].
  - Kill moves are short-ranged, slow, or need a sweetspot; fsmash is weak for a forward smash [wiki:Kirby_(SSBM)].
  - Among the worst endurance in the game (with Mr. Game & Watch and Pichu); Fox kills him off the top especially early [wiki:Kirby_(SSBM)].
  - Recovery is slow and linear; up B (Final Cutter) gives almost no horizontal distance and being hit out of it removes his remaining jumps [wiki:Kirby_(SSBM)].
  - Forward and back throw can be mashed out of (in NTSC), and forward and up throw use up all his midair jumps [wiki:Kirby_(SSBM)].
  - Loses hard to disjoints ([Marth](marth.md)) and strong pressure ([Falco](falco.md)) [wiki:Kirby_(SSBM)].

## Character tech

### Crouch and tilt poking

- **id:** `crouch-and-tilt-poking`
- **What:** Kirby sits in his low crouch so attacks pass over him, and pokes with down tilt from the crouch; he also uses [crouch cancel](../techniques/crouch-cancel.md) into down smash at low percent.
- **Inputs:** Hold down; dtilt = down + A (tilt, not smash). Out of shield: wavedash out -> ftilt or dtilt [lib:20XX+XY].
- **Timing:** Dtilt hits on frames 4-7, 10%, launch angle 20 (very low), 29 frames total [fd]. Ftilt frames 5-8, 11%, interruptible from frame 28 [fd]. Dsmash clean on frames 7-9 (14%), late hit to frame 22, feet intangible on frames 7-9, interruptible from frame 50 [fd][wiki:Kirby_(SSBM)/Down_smash]. Jump squat is 3 frames [wiki:Kirby_(SSBM)].
- **Used for:** His main neutral: spacing against grounded opponents while staying under their attacks; dsmash is called a great move to pair with crouch cancelling [wiki:Kirby_(SSBM)].
- **Common errors:** Crouching against low-hitting moves and grabs that do reach him; dsmash on shield (long end lag).
- **Drill idea:** CPU throws a jab or high poke that whiffs over crouch; success if Kirby's dtilt hits within N frames.

### Up tilt juggle

- **id:** `up-tilt-juggle`
- **What:** Up tilt is a frame-4 kick behind and above Kirby with high base knockback that can be repeated and followed with aerials or Inhale [wiki:Kirby_(SSBM)].
- **Inputs:** Utilt (opponent behind or above) -> utilt again, or jump uair/bair, or neutral B (Inhale) on fastfallers.
- **Timing:** Clean hit frame 4 (8%), late frames 5-7 (6%), 23 frames total; base knockback 40, growth 114-118, angle about 90 [fd]. Utilt -> Inhale is described as important against fastfallers; Inhale's grab starts on frame 17 [wiki:Kirby_(SSBM)/Neutral_special].
- **Used for:** One of his only combo starters; damage and setting up Inhale or a kill aerial.
- **Common errors:** Using it with the opponent in front (the strong part is behind him); continuing past the percent where the opponent flies too high.
- **Drill idea:** Fox/Falco CPU placed behind Kirby at low percent with random DI; count consecutive utilts, then require an Inhale or uair before the CPU acts.

### Down throw tech chase

- **id:** `down-throw-tech-chase`
- **What:** Down throw puts the opponent on the ground in front of Kirby; he covers their tech with another grab or down smash [wiki:Kirby_(SSBM)].
- **Inputs:** Grab -> down throw -> react or read: regrab, dsmash, dtilt, or Inhale.
- **Timing:** Down throw releases on frame 57 of an 87-frame animation [wiki:Kirby_(SSBM)/Down_throw], leaving 30 frames before Kirby can move. Standing grab is active on frames 7-8, dash grab on frames 11-12 [wiki:Kirby_(SSBM)/Grab]. A neutral tech is 26 frames and tech rolls 40, both vulnerable from frame 21 [lib:20XX+XY].
- **Used for:** His most reliable follow-up from a grab. See [tech chase](../techniques/tech-chase.md).
- **Common errors:** Pure reaction is hard given the 30 frames of throw end lag; he usually has to position for two options and read.
- **Drill idea:** CPU techs at random after dthrow; success if Kirby regrabs or lands dsmash before the CPU can act.

### Fence of pain

- **id:** `fence-of-pain`
- **What:** Kirby's version of Jigglypuff's [wall of pain](jigglypuff.md): repeated back airs off stage using his midair jumps [wiki:Kirby_(SSBM)/Back_aerial].
- **Inputs:** Bair toward the ledge -> jump after the opponent -> bair -> repeat; return with remaining jumps.
- **Timing:** Bair clean frames 6-8, late 9-20, interruptible from frame 36, auto-cancels before frame 6 and after frame 27 [fd]. His air speed (0.78 [wiki:Kirby_(SSBM)]) is far below Jigglypuff's, so the chain is shorter and less reliable [wiki:Kirby_(SSBM)].
- **Used for:** Gimping characters with poor horizontal recovery such as Roy and Falco; it is near useless against Jigglypuff [wiki:Kirby_(SSBM)/Back_aerial].
- **Common errors:** Chasing too far with too few jumps; being hit out of up B on the way back (loses all jumps).
- **Drill idea:** Falco CPU launched off stage at mid percent; success if two or more bairs connect and Falco cannot reach the ledge.

### Kirbycide throws

- **id:** `kirbycide-throws`
- **What:** Forward throw, back throw and up throw all carry the opponent with Kirby. Done at the ledge they take both characters off stage and down, a sacrificial KO at any percent [wiki:Kirbycide][wiki:Kirby_(SSBM)].
- **Inputs:** Grab next to (or facing away from) the ledge -> back throw or forward throw so the slam happens past the edge; up throw only on stages/positions where the landing point is off stage.
- **Timing:** Back throw releases on frame 29 (49 total), forward throw on frame 45 (61 total), up throw on frame 51 (79 total) [wiki:Kirby_(SSBM)/Back_throw][wiki:Kirby_(SSBM)/Forward_throw][wiki:Kirby_(SSBM)/Up_throw]. Forward and back throw can be escaped by button mashing during the throw, in which case Kirby dies alone; back throw is faster, so mashing out in time is harder at higher percent. Up throw cannot be mashed out of. Forward and up throw remove all of Kirby's midair jumps. With forward/back throw Kirby wins a last-stock trade; with up throw he loses it [wiki:Kirby_(SSBM)][wiki:Kirby_(SSBM)/Up_throw].
- **Used for:** Trading stocks when ahead, or stealing a stock at low percent from a much better character. A smaller stage makes it more dangerous to stand near the edge against him [lib:20XX+XY].
- **Common errors:** Opponent mashes out (Kirby self-destructs); using it when behind on stocks.
- **Drill idea:** CPU grabbed near the ledge at a chosen percent and mash rate; success if both fall and the CPU dies first or the CPU dies and Kirby recovers.

### Swallowcide

- **id:** `swallowcide`
- **What:** Inhale an opponent, walk or jump off stage with them in Kirby's mouth, and fall. Both die unless the opponent mashes out in time [wiki:Kirbycide].
- **Inputs:** Neutral B (hold) to catch -> walk/jump off the ledge -> do nothing; or spit/swallow late.
- **Timing:** Inhale grabs from frame 17; the catching window loops from frame 20 to 59 or longer while B is held [wiki:Kirby_(SSBM)/Neutral_special]. The maximum hold time in Melee is shorter than in Smash 64 and reduced by mashing [wiki:Kirbycide] (exact value not read). Catching someone refreshes all of Kirby's midair jumps, whether they escape, are swallowed or are spat out [wiki:Kirby_(SSBM)/Neutral_special].
- **Used for:** Stock trades; ledge-hop Inhale makes opponents cautious about approaching him at the ledge [wiki:Kirby_(SSBM)/Neutral_special].
- **Common errors:** Whiffing Inhale (about 79 frames of commitment [wiki:Kirby_(SSBM)/Neutral_special]); opponent mashes out above the stage.
- **Drill idea:** CPU approaches Kirby on the ledge; player ledge-hops Inhale; success if the CPU is caught and dies.

### Inhale and copy abilities

- **id:** `inhale-and-copy`
- **What:** After Inhale, Kirby can swallow to copy the opponent's neutral B (8%) or spit them out as a star (10%, plus 8-19% if the star hits someone, depending on the spat character's weight) [wiki:Kirby_(SSBM)].
- **Inputs:** Neutral B -> down (swallow/copy) or A/B (spit).
- **Timing:** Swallow acts on frame 7 and spit on frame 6 of 29-frame animations; the star is active on frames 6-34 [wiki:Kirby_(SSBM)/Neutral_special].
- **Used for:** Falco's Blaster is the most valued copy: it causes flinch and Kirby fits two lasers into one short hop, giving him an approach tool and hit confirms. Fox's Blaster does not flinch, so keeping Inhale is preferred against Fox; against Marth plain Inhale is also preferred; star spit is good against Ice Climbers because it separates them. Copied charge moves (Samus, Donkey Kong, Sheik) lose their charge the first time Kirby is hit. Several copies enable fast ledge grabs and turnaround-B bair setups [wiki:Kirby_(SSBM)/Neutral_special].
- **Common errors:** Going for a copy when the star spit or a Kirbycide was the better choice.
- **Drill idea:** After a successful Inhale on Falco, player must copy, then land a double-laser short hop into a grab.

### Dash attack cancelled grab

- **id:** `dash-attack-cancelled-grab`
- **What:** Pressing grab during the first frames of dash attack turns it into a grab that keeps the dash attack's momentum ("boost grab"). A library video calls it Kirby's "most hidden tech" [lib:KIRBY'S MOST HIDDEN TECH].
- **Inputs:** Dash -> A, then Z within the window.
- **Timing:** Window is frames 2-4 of the dash attack [wiki:Kirby_(SSBM)/Dash_attack]. Kirby's raw dash attack is slow and punishable: clean hit frames 9-15, late hit to frame 43, interruptible from frame 60 [fd].
- **Used for:** A longer-range grab than his normal dash grab; one of his few burst options.
- **Common errors:** Late Z (full 63-frame dash attack comes out).
- **Drill idea:** CPU shields at mid range; success if the boost grab connects from a distance where dash grab would whiff.

### Multi-jump recovery

- **id:** `multi-jump-recovery`
- **What:** Five midair jumps plus aerials for drift, then up B (Final Cutter) as a last resort.
- **Inputs:** Midair jumps; bair or uair during a jump adds some horizontal distance (they have the least aerial lag for this) [wiki:Kirby_(SSBM)]; up B near the ledge.
- **Timing:** Final Cutter rises with a hitbox (8%), then plunges until it hits ground (2%), then fires a wave (6%); it cannot be cancelled and he cannot pass through platforms on the way down [wiki:Kirby_(SSBM)]. If he is knocked out of it he loses all unspent midair jumps [wiki:Kirby_(SSBM)].
- **Used for:** Getting back; also down B (Stone) to fall fast, in which form only grabs affect him [wiki:Kirby_(SSBM)].
- **Common errors:** Using up B early; predictable jump rhythm.
- **Drill idea:** Kirby off stage with N jumps against a CPU edgeguarder; success if he reaches stage or ledge unhit.

## Neutral game

- Ground-based and defensive: crouch, dtilt, ftilt, wavedash back, shield, grab. A notable Kirby player describes the ground as where he "shines most", with wavedash out of shield into ftilt/dtilt as a staple [lib:20XX+XY].
- Bair is the aerial poke: short hop or full hop backward-facing bair, auto-cancelled (after frame 27 [fd]).
- Falling uair is a strong raw hit; fair (three hits, frames 10-26 [fd]) is his approaching aerial with a landing hitbox when not L-cancelled [wiki:Kirby_(SSBM)].
- Dash attack has transcendent priority and can slide off ledges and platforms, but is very punishable [wiki:Kirby_(SSBM)].
- With Falco's laser copied he gains a real approach on flat stages [wiki:Kirby_(SSBM)/Neutral_special].
- He wants the opponent to approach into his crouch/tilts, or to be near a ledge where throws threaten a Kirbycide.

## Punish game

Kirby has strong single hits (falling uair, bair, fair, dsmash, hammer) but almost nothing sets up something guaranteed; his punishes are read-heavy and compared to a read-based Captain Falcon [lib:20XX+XY]. Realistic conversions are utilt juggles, dthrow tech chases, and edgeguards.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| Utilt | fastfallers | low (typical) | Utilt again, then Inhale or uair/bair | Utilt -> Inhale named as important vs fastfallers | [wiki:Kirby_(SSBM)/Neutral_special], [wiki:Kirby_(SSBM)] |
| Dthrow | any | any | Tech chase: regrab or dsmash | 30 frames of end lag after release | [wiki:Kirby_(SSBM)], [wiki:Kirby_(SSBM)/Down_throw] |
| Uthrow | opponents who do not DI | low | Aerial side B (Hammer) | Kirby has no jumps afterwards; DI away escapes | [wiki:Kirby_(SSBM)/Up_throw] |
| Jab reset | missed tech | any | Inhale, grab, smash | Listed as an Inhale setup | [wiki:Kirby_(SSBM)/Neutral_special] |
| Late nair | any | typical | Follow-ups, "not super reliably" | | [wiki:Kirby_(SSBM)/Neutral_aerial] |
| Copied Falco laser | any | any | Grab, jab reset, hit confirm | Two lasers per short hop | [wiki:Kirby_(SSBM)/Neutral_special] |
| Bair near ledge | Falco, Roy, short recoveries | low-mid | Fence of pain | | [wiki:Kirby_(SSBM)/Back_aerial] |

### Chain grabs and tech chases

- **Chain grabs:** none of note. Down throw can lead to another down throw only through a tech chase [wiki:Kirby_(SSBM)].
- **Tech chases:** dthrow -> read/react. Missed tech -> jab reset -> Inhale or grab. The opponent's outs are teching away from Kirby (he is slow) and, near the ledge, staying away from the edge to avoid Kirbycides.

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Uair | any | Not sourced | 15%, frames 11-13, horizontal launch; "possibly his best KO move" | [wiki:Kirby_(SSBM)], [fd] |
| Bair (clean) | any | Not sourced | 14%, frames 6-8; best off stage | [wiki:Kirby_(SSBM)/Back_aerial], [fd] |
| Usmash (foot sweetspot, clean) | any | Not sourced | 15%, frame 13 only | [wiki:Kirby_(SSBM)], [fd] |
| Side B (Hammer, grounded, head) | any | Not sourced | 23%, frames 22-28, 59 frames total; hard punish only | [fd], [wiki:Kirby_(SSBM)] |
| Dsmash | any | Not sourced | 14%, low angle (28) on the outer hit; edgeguard starter | [fd] |
| Fsmash | any | High; weak for a forward smash | 15% clean on frames 13-15 | [wiki:Kirby_(SSBM)], [fd] |
| Bthrow / fthrow Kirbycide | any | Any percent | At the ledge; escapable by mashing | [wiki:Kirbycide], [wiki:Kirby_(SSBM)] |
| Uthrow Kirbycide | any | Any percent | Certain stages/positions; not escapable; Kirby loses a last-stock trade | [wiki:Kirby_(SSBM)/Up_throw] |
| Swallowcide | any | Any percent | Escapable by mashing | [wiki:Kirbycide] |
| Dair (meteor) | off stage | Any, as a gimp | Six hits from frame 18; stops Fox's Fire Fox | [wiki:Kirby_(SSBM)], [fd] |

- No kill-percent numbers for Kirby's moves were found in the sources read; the nair clean hit is noted as failing to KO even at 200% [wiki:Kirby_(SSBM)/Neutral_aerial].
- **Edgeguards:** bair chains, dair meteor, dtilt/ftilt at the ledge (ftilt is "good for hitting an opponent offstage" [wiki:Kirby_(SSBM)]), Final Cutter's wave, and ledge-hop Inhale.

## Recovery

- **Options:** five midair jumps; bair/uair during jumps for extra horizontal drift; up B (Final Cutter) for a final vertical boost with a hitbox; down B (Stone) to change fall speed; air dodge. A successful Inhale restores all jumps [wiki:Kirby_(SSBM)/Neutral_special].
- **Mixups:** jump timing and height; recover high and Stone down; hit the edgeguarder with bair on the way in.
- **Weaknesses:** very low air speed makes his path slow and readable; Final Cutter has almost no horizontal travel, cannot be cancelled, and being hit out of it removes his jumps; his weight means any solid hit near the blast zone kills [wiki:Kirby_(SSBM)]. After a forward or up throw he has no jumps at all [wiki:Kirby_(SSBM)].

### Edgeguarding Kirby

- Go out and hit him: he cannot drift around attacks. Any strong aerial during his jump sequence usually kills because of his weight.
- At the ledge, cover Final Cutter: it rises straight up next to the ledge and plunges; hit him before the rise or take the ledge so he lands on stage in lag. Hitting him out of it strips his jumps [wiki:Kirby_(SSBM)].
- Do not stand at the very edge when he can grab you: back/forward throw there is a Kirbycide [lib:20XX+XY].
- A realistic recovering CPU should spend jumps slowly from high up, use bair when challenged, and save Final Cutter for the ledge.

## Defense and out of shield

- **Out of shield:** jump squat 3 [wiki:Kirby_(SSBM)], so bair hits 9 frames after leaving shield (frame 6 [fd]); wavedash out of shield -> ftilt/dtilt [lib:20XX+XY]; shield grab frames 7-8 [wiki:Kirby_(SSBM)/Grab]; up B out of shield (rising hitbox).
- **Crouch:** his defining defensive tool; many jabs and high moves miss entirely [wiki:Kirby_(SSBM)]. Crouch cancel -> dsmash at low percent.
- **Shield:** large relative to his body, so shield pokes are rare [wiki:Kirby_(SSBM)].
- **Combo escape:** floaty and light, so he falls out of most combos, but he also dies early; multiple jumps and Stone help him change timing.
- **What beats him:** disjointed spacing (Marth), sustained pressure and lasers (Falco), early vertical kill moves (Fox) [wiki:Kirby_(SSBM)].

## As the training dummy

- **Weight / fall speed:** weight 70 (NTSC; PAL is 74), fall speed 1.6, fast-fall 2.0, gravity 0.08 [wiki:Kirby_(SSBM)]. Light and floaty: short combos, early kills, especially vertical.
- **Small target:** crouching Kirby is under many moves; drills that depend on a jab or high hitbox connecting need to check it reaches him.
- **Chain grabs on him:** Ice Climbers' down throw hand-off works: release frame 26, regrab window frames 26-29 [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]. Other characters' chain grabs on Kirby were not found in the sources read.
- **Realistic CPU choices:** crouch in neutral, dtilt/ftilt pokes, bair when airborne; when grabbed near a ledge the opponent should expect a throw off stage; when Kirby throws with forward/back throw the victim should mash.
- **Thresholds:** none sourced.

## Matchup notes

### vs Fox

Fox kills Kirby off the top very early and can simply run away and laser. Kirby keeps Inhale rather than copying, because Fox's laser does not cause flinch [wiki:Kirby_(SSBM)/Neutral_special]. Kirby's chances come from utilt -> Inhale, dthrow tech chases, dair against Fire Fox, and Kirbycides.

### vs Falco

Falco's pressure is one of Kirby's worst problems [wiki:Kirby_(SSBM)], but copying Falco's Blaster is his best ability (flinch, two shots per short hop) and Falco's short recovery makes the fence of pain effective [wiki:Kirby_(SSBM)/Neutral_special][wiki:Kirby_(SSBM)/Back_aerial].

### vs Marth

Marth's disjointed sword shuts down Kirby's short-range approach [wiki:Kirby_(SSBM)]. Plain Inhale is preferred over the copy for damage and Kirbycide chances [wiki:Kirby_(SSBM)/Neutral_special].

### vs Ice Climbers

Star spit is useful because it leaves the climbers separated [wiki:Kirby_(SSBM)/Neutral_special]. From the Ice Climbers' side the advice is to shield-camp and roll back into Blizzard under pressure, since Kirby cannot apply much shield pressure [lib:20XX+XY].

## Drill seeds

### Crouch and down tilt whiff punish

- **id:** `kirby-crouch-dtilt-punish`
- **Goal:** Use the crouch to make an attack whiff and punish with dtilt or grab.
- **Player:** Kirby
- **CPU:** [Marth](marth.md), [Sheik](sheik.md), [Captain Falcon](captain-falcon.md), [Fox](fox.md)
- **Setup:** Flat stage, CPU at jab/grab range, Kirby at low percent.
- **CPU behaviour:** Random: jab, standing grab, a high tilt, or a low move that does hit crouch (e.g. dtilt).
- **Success:** Whiffed move is punished by dtilt (frame 4) or grab within 15 frames; low moves are shielded or crouch cancelled into dsmash.
- **Fail:** Kirby is hit while crouching and knocked down, or misses the punish window.
- **Variations:** Wavedash out of shield -> ftilt/dtilt against shield pressure.
- **Data needed:** Which CPU moves clear Kirby's crouch hurtbox (needs in-game measurement), dtilt frames 4-7, ftilt frames 5-8, dsmash frame 7 [fd].

### Up tilt juggle into Inhale

- **id:** `kirby-utilt-inhale`
- **Goal:** Juggle a fastfaller with utilt and land Inhale or a kill aerial.
- **Player:** Kirby
- **CPU:** [Fox](fox.md), [Falco](falco.md), [Captain Falcon](captain-falcon.md)
- **Setup:** CPU standing directly behind Kirby at 0-40%, flat stage.
- **CPU behaviour:** Random DI on each hit; shines/jumps/attacks when actionable.
- **Success:** At least two utilts connect, then Inhale catches the CPU (or uair/bair hits) before it acts.
- **Fail:** CPU escapes or hits Kirby.
- **Variations:** After Inhale choose copy (Falco) vs spit vs carrying off stage.
- **Data needed:** Utilt frames and knockback (base 40, growth 114-118) [fd], Inhale grab start frame 17 [wiki:Kirby_(SSBM)/Neutral_special], victim fall speeds.

### Down throw tech chase

- **id:** `kirby-dthrow-techchase`
- **Goal:** Cover tech options after down throw.
- **Player:** Kirby
- **CPU:** [Fox](fox.md), [Falco](falco.md), [Sheik](sheik.md), [Marth](marth.md)
- **Setup:** Kirby holding the CPU in a grab at centre stage, 20-80%.
- **CPU behaviour:** After the throw: tech in place, tech left, tech right, or miss the tech, at random.
- **Success:** Regrab or dsmash connects before the CPU is actionable; missed tech -> jab reset -> grab or Inhale.
- **Fail:** CPU acts first.
- **Variations:** Near the ledge so one roll is cut off and the regrab threatens a Kirbycide.
- **Data needed:** Dthrow release frame 57 of 87 [wiki:Kirby_(SSBM)/Down_throw], tech timings (26 / 40 frames, vulnerable from 21 [lib:20XX+XY]), Kirby dash speed 1.4 [wiki:Kirby_(SSBM)], grab frames.

### Fence of pain

- **id:** `kirby-fence-of-pain`
- **Goal:** Chain bairs off stage and return.
- **Player:** Kirby
- **CPU:** [Falco](falco.md), [Roy](roy.md), [Captain Falcon](captain-falcon.md)
- **Setup:** CPU launched off the side at ledge height at 40-80%; Kirby at the ledge facing inward (bair pointing out), all jumps available.
- **CPU behaviour:** DIs each hit, then recovers with its best option.
- **Success:** Two or more bairs connect and the CPU fails to reach the ledge; Kirby returns.
- **Fail:** CPU recovers, or Kirby dies (including being hit out of Final Cutter).
- **Variations:** Dair meteor on a Fire Fox start-up; uair finisher.
- **Data needed:** Bair frames 6-20, IASA 36 [fd]; Kirby air speed 0.78 and jump heights (double jump height unknown on the wiki); CPU recovery distances.

### Kirbycide at the ledge

- **id:** `kirby-ledge-kirbycide`
- **Goal:** Take a stock at low percent with a throw or Inhale off the ledge, and know when it is escapable.
- **Player:** Kirby
- **CPU:** any; [Fox](fox.md), [Marth](marth.md) as defaults
- **Setup:** CPU standing or shielding within one character width of the ledge, Kirby in grab range, both on their last stock or with Kirby ahead (variations).
- **CPU behaviour:** Mashes during the throw at a configurable rate; if released, recovers.
- **Success:** CPU loses the stock; best case Kirby wins the last-stock trade (forward/back throw) or survives.
- **Fail:** CPU mashes out and Kirby dies alone, or the throw lands on stage.
- **Variations:** Back throw (release frame 29) vs forward throw (frame 45) to show the mash window; up throw on a stage where it carries off the edge; ledge-hop Inhale -> swallowcide.
- **Data needed:** Throw release frames [wiki:Kirby_(SSBM)/Back_throw][wiki:Kirby_(SSBM)/Forward_throw][wiki:Kirby_(SSBM)/Up_throw]; throw-escape mash rules (not sourced); stage edge positions.

### Recovery against an edgeguarder

- **id:** `kirby-recovery`
- **Goal:** Return using jumps and aerials, keeping Final Cutter for the ledge.
- **Player:** Kirby
- **CPU:** [Marth](marth.md), [Fox](fox.md), [Sheik](sheik.md)
- **Setup:** Kirby off stage at a randomised height with 2-5 jumps left, at 60-100%.
- **CPU behaviour:** Comes off stage to hit him, or waits at the ledge to cover Final Cutter.
- **Success:** Kirby on stage or holding the ledge, unhit.
- **Fail:** Stock lost.
- **Variations:** No jumps left (after a forward/up throw): Final Cutter only; Stone to bait an early swing.
- **Data needed:** Jump heights per midair jump and Final Cutter travel (not sourced), CPU aerial reach, blast zones.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlKb.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/kirby.json`](../framedata/kirby.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 3-4 | 3 | Sakurai | 8 | 50 | - |  | 17 | 16 | 3 | -9 |  |
| Jab 2 | `jab2` | 3-4 | 4 | 70 | 8 | 50 | - |  | 20 | 17 | 3 | -10 | starts 1 frame late (included) |
| Rapid jab start | `rapid_jab_start` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Rapid jab loop | `rapid_jab_loop` | 1-2, 5-6, 9-10, 13-14, 17-18 | 1 | 65 | 8 | 50 | - |  | 19 | - | 2 | -16 |  |
| Rapid jab end | `rapid_jab_end` | - | - | - | - | - | - | - | 9 | - | - | - |  |
| Dash attack | `dash_attack` | 9-15 | 8 | 105 | 70 | 66 | - | fire | 63 | 60 | 5 | -45 |  |
|  |  | 16-43 | 5 | 105 | 50 | 66 | - | fire |  |  | 4 | -39 |  |
| Forward tilt (angled up) | `ftilt_high` | 5-8 | 11 | Sakurai | 8 | 100 | - |  | 32 | 28 | 6 | -16 |  |
| Forward tilt | `ftilt` | 5-8 | 11 | Sakurai | 8 | 100 | - |  | 32 | 28 | 6 | -16 |  |
| Forward tilt (angled down) | `ftilt_low` | 5-8 | 11 | Sakurai | 8 | 100 | - |  | 32 | 28 | 6 | -16 |  |
| Up tilt | `utilt` | 4 | 8 | 92 | 40 | 118/114 | - |  | 23 | - | 5 | -14 |  |
|  |  | 5-7 | 6 | 88 | 40 | 118/114 | - |  |  |  | 4 | -14 |  |
| Down tilt | `dtilt` | 4-7 | 10 | 20 | 40 | 30 | - |  | 29 | - | 6 | -19 |  |
| Forward smash (angled up) | `fsmash_high` | 13-15 | 15 | Sakurai | 24 | 96 | - |  | 49 | - | 8 | -28 | charge hold frame 5 |
|  |  | 16-21 | 13 | 75 | 18 | 96 | - |  |  |  | 7 | -26 |  |
| Forward smash | `fsmash` | 13-15 | 15 | Sakurai | 24 | 96 | - |  | 49 | - | 8 | -28 | charge hold frame 5 |
|  |  | 16-21 | 13 | 75 | 18 | 96 | - |  |  |  | 7 | -26 |  |
| Forward smash (angled down) | `fsmash_low` | 13-15 | 15 | Sakurai | 24 | 96 | - |  | 49 | - | 8 | -28 | charge hold frame 5 |
|  |  | 16-21 | 13 | 75 | 18 | 96 | - |  |  |  | 7 | -26 |  |
| Up smash | `usmash` | 13 | 15/13 | 75 | 30 | 118/110 | - | slash | 49 | - | 8 | -28 | charge hold frame 9 |
|  |  | 14-15 | 14/12 | 88 | 20 | 100 | - |  |  |  | 8 | -27 |  |
|  |  | 16-23 | 13/12 | 50 | 10 | 50 | - |  |  |  | 7 | -26 |  |
| Down smash | `dsmash` | 7-9 | 14 | 76/28 | 30/20 | 100/80 | - |  | 55 | 50 | 8 | -34 | charge hold frame 5; partly intangible 7-9 (2 bones) |
|  |  | 10-22 | 12/10 | 76/28 | 30/20 | 100/80 | - |  |  |  | 7 | -32 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 10-17 | 10 | Sakurai | 10 | 80 | - |  | 79 | 50 | 6 | 15 | 7 | <10, >37 | -1 |  |
|  |  | 18-29 | 8 | Sakurai | 10 | 80 | - |  |  |  | 5 |  |  |  | -2 |  |
|  |  | 30-34 | 6 | Sakurai | 10 | 80 | - |  |  |  | 4 |  |  |  | -3 |  |
| Forward air | `fair` | 10-11, 17-18 | 5 | 60 | 30 | 70 | - |  | 49 | 40 | 4 | 20 | 10 | <10, >37 | -6 |  |
|  |  | 25-26 | 8 | Sakurai | 30 | 130 | - |  |  |  | 5 |  |  |  | -5 |  |
| Back air | `bair` | 6-8 | 14 | Sakurai | 10 | 100 | - |  | 43 | 36 | 8 | 15 | 7 | <6, >27 | +1 |  |
|  |  | 9-20 | 10 | Sakurai | 0 | 100 | - |  |  |  | 6 |  |  |  | -1 |  |
| Up air | `uair` | 11-13 | 15 | Sakurai | 30 | 100 | - |  | 39 | 36 | 8 | 15 | 7 | <11, >16 | +1 |  |
| Down air | `dair` | 18-19, 21-22, 24-25, 27-28, 30-31, 33-34 | 3 | 270 | 30 | 100 | - |  | 59 | 55 | 3 | 20 | 10 | <18, >47 | -7 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 11-12 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 10 | 30 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 8 | 8 | 65 | 40 | 100 | - | - | 45 | 61 |  |
| Back throw | `bthrow` | 8 | 8 | 120 | 80 | 50 | - | - | 29 | 49 |  |
| Up throw | `uthrow` | 10 | 10 | 90 | 70 | 70 | - | - | 51 | 79 |  |
| Down throw | `dthrow` | 8 | 7 | 90 | 40 | 45 | - | - | 57 | 87 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Swallow (Inhale), ground | `special_n` | 17-19 | 1 | Sakurai | 0 | 100 | - | grab | 19 | - | 2 | - |  |
| Neutral B: Swallow (Inhale), ground, Loop | `special_n_loop` | 1-17 | 1 | Sakurai | 0 | 100 | - | grab | 17 | - | 2 | - |  |
| Neutral B: Swallow (Inhale), ground, End | `special_n_end` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Neutral B: Swallow (Inhale), ground, Loop | `special_n_loop_308` | - | - | - | - | - | - | - | 17 | - | - | - |  |
| Neutral B: Swallow (Inhale), ground, Drink | `special_n_drink` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Neutral B: Swallow (Inhale), ground, Spit | `special_n_spit` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Neutral B: Swallow (Inhale), ground | `special_n_320` | 17-19 | 1 | Sakurai | 0 | 100 | - | grab | 19 | - | 2 | - |  |
| Neutral B: Swallow (Inhale), ground, Loop | `special_n_loop_321` | 1-17 | 1 | Sakurai | 0 | 100 | - | grab | 17 | - | 2 | - |  |
| Side B: Hammer, ground | `special_s` | 22-28 | 16/23 | 60 | 50/65 | 50/76 | - |  | 59 | - | 12 | - |  |
| Side B: Hammer, air | `special_air_s` | 7-10, 11-14, 15-18, 19-22, 23-26 | 4 | 110 | 0 | 100 | 40 |  | 69 | - | 3 | - |  |
|  |  | 27-30, 31-34, 35-38, 39-42, 43-46 | 2 | 110 | 0 | 100 | 30 |  |  |  | 2 | - |  |
| Up B: Final Cutter, ground, 1 | `special_hi1` | - | - | - | - | - | - | - | 22 | - | - | - |  |
| Up B: Final Cutter, ground, 2 | `special_hi2` | 1 | 8 | 88/96 | 0 | 100 | 117/102 | slash | 34 | - | 5 | - |  |
|  |  | 24-33 | 2 | 275 | 0 | 100 | 100 | slash |  |  | 2 | - |  |
| Up B: Final Cutter, ground, 3 | `special_hi3` | - | - | - | - | - | - | - | 4 | - | - | - |  |
| Up B: Final Cutter, ground, 4 | `special_hi4` | - | - | - | - | - | - | - | 33 | - | - | - |  |
| Up B: Final Cutter, air, 1 | `special_air_hi1` | - | - | - | - | - | - | - | 22 | - | - | - |  |
| Up B: Final Cutter, air, 2 | `special_air_hi2` | 1 | 8 | 88/96 | 0 | 100 | 117/102 | slash | 34 | - | 5 | - |  |
|  |  | 24-33 | 2 | 275 | 0 | 100 | 100 | slash |  |  | 2 | - |  |
| Up B: Final Cutter, air, 3 | `special_air_hi3` | - | - | - | - | - | - | - | 4 | - | - | - |  |
| Up B: Final Cutter, air, 4 | `special_air_hi4` | - | - | - | - | - | - | - | 33 | - | - | - |  |
| Down B: Stone, ground, 1 | `special_lw1` | - | - | - | - | - | - | - | 28 | - | - | - |  |
| Down B: Stone, ground, 2 | `special_lw2` | - | - | - | - | - | - | - | 30 | - | - | - |  |
| Down B: Stone, ground, 2 | `special_lw2_334` | - | - | - | - | - | - | - | 30 | - | - | - |  |
| Down B: Stone, air, 1 | `special_air_lw1` | - | - | - | - | - | - | - | 28 | - | - | - |  |
| Down B: Stone, air, 2 | `special_air_lw2` | 1-30 | 18 | 70 | 65 | 55 | - |  | 30 | - | 10 | - |  |
| Down B: Stone, air, 2 | `special_air_lw2_337` | - | - | - | - | - | - | - | 30 | - | - | - |  |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-15 | - | 22 | 20 |  |
| Roll forward | `roll_forward` | intangible 4-19 | - | 31 | - |  |
| Roll backward | `roll_backward` | intangible 4-19 | - | 31 | - |  |
| Air dodge | `airdodge` | intangible 4-29 | - | 49 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-15 | 19-20, 24-25 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-18 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-20 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-27 | 20-21, 24, 26-27 (6%) | 49 | - |  |
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
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 23 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Shield grab | direct | 7 | `grab` |
| Back air | jump | 9 | `bair` |
| Neutral air | jump | 13 | `nair` |
| Forward air | jump | 13 | `fair` |
| Up air | jump | 14 | `uair` |
| Up smash | jump cancel | 14 | `usmash` |
| Down air | jump | 21 | `dair` |
| Spot dodge | direct | intangible 2-15 of 22 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 15 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Kirby indexed by [The Melee Library](https://www.meleelibrary.com/#kirby) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [KIRBY’S MOST HIDDEN TECH](https://www.youtube.com/watch?v=vv_jkRK_6Ic) | PikaChad | It's a dash-attack canceled grab. |
| [2020 Kirby Techs Guide](https://www.youtube.com/watch?v=7xuOqy88Y20&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=3&t=0s) | Third Chair | Video guide on performing useful Kirby tech in 2020. |
| [20XX Kirby Tools Part 1 and [Part 2](https://www.youtube.com/watch?v=OvCHqA7sUMY)](https://www.youtube.com/watch?v=JsC0_5BTWhw) | Chandy |  |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Kirby (SSBM): https://www.ssbwiki.com/Kirby_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Kirby_(SSBM)/Neutral_special , /Back_aerial , /Up_aerial , /Neutral_aerial , /Forward_aerial , /Down_aerial , /Dash_attack , /Down_smash , /Forward_smash , /Up_smash , /Up_tilt , /Down_tilt , /Forward_tilt , /Grab , /Forward_throw , /Back_throw , /Up_throw , /Down_throw , /Side_special
- SSBWiki, Kirbycide: https://www.ssbwiki.com/Kirbycide
- SSBWiki, List of SSBM tier lists (NTSC) and Template:MeleeTiers: https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Melee Library card "20XX+XY" (Kirby section: quotes from C.Rabbit, Triple R, Fly Amanita, CunningKitsune; tech-chase data): https://docs.google.com/document/d/1DPqPLDHfBWMluMMfd8KpDVN8s37866CTb4xQVW-_KLk/
- Nicki / Nopia, "Ice Climbers Information and Data Sheet" (hand-off window on Kirby): https://docs.google.com/document/d/1e2WfuNH1I86On59O53FubxYzA-zYMZKZVIrCPNVEqhk/
- Melee Library "Kirby" section (3 YouTube cards): titles and descriptions only.
- Frame data dump: `Kirby.json`
