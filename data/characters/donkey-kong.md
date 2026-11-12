---
schema: melee-character/v1
id: donkey-kong
name: Donkey Kong
aliases: [DK, D.K.]
tier: "C- (16th of 26), 2021 tier list"
archetype: [heavy, grappler, punish-heavy, combo-food, edgeguarder, fastfaller]
related: [bowser, ganondorf]
summary: Donkey Kong walls with back air, fishes for a grab, and turns one cargo up throw into up air juggles that reach kill percent, ending with forward air, Giant Punch, up smash or an edgeguard, while trying not to be comboed and gimped himself.
key_tech: [cargo-up-throw-combo, cargo-chain-grab, cargo-carry, giant-punch-charge, reverse-charge-cancel, bair-wall, spinning-kong-out-of-shield, spinning-kong-ledge, hand-slap, dtilt-edgeguard]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlDk.dat
framedata: ../framedata/donkey-kong.json
code: src/melee/ft/kinds/ftDonkey
specials:
  neutral_b: "Giant Punch"
  side_b: "Headbutt"
  up_b: "Spinning Kong"
  down_b: "Hand Slap"
attributes:
  weight: 114
  gravity: 0.1
  fall_speed: 2.4
  fast_fall_speed: 2.96
  jump_squat: 5
  jumps: 2
  walk_speed: 1.2
  dash_speed: 1.6
  run_speed: 1.6
  traction: 0.08
  air_speed: 1
  landing_lag: 5
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [5, 25, 4]
  jab2: [5, 35, 6]
  dash_attack: [9, 55, 11]
  ftilt_high: [8, 34, 11]
  ftilt: [8, 34, 10]
  ftilt_low: [8, 34, 9]
  utilt: [6, 40, 11]
  dtilt: [6, 23, 7]
  fsmash: [22, 55, 21]
  usmash: [14, 54, 18]
  dsmash: [10, 56, 16]
  nair: [10, 39, 12]
  fair: [25, 60, 16]
  bair: [7, 32, 13]
  uair: [6, 38, 14]
  dair: [18, 55, 16]
  grab: [8, 31, 0]
  dash_grab: [10, 51, 0]
  pummel: [10, 25, 3]
  fthrow: [null, 20, 0]
  bthrow: [null, 40, 11]
  uthrow: [null, 44, 9]
  dthrow: [null, 60, 7]
  special_n_start: [null, 8, 0]
  special_n_loop: [null, 12, 0]
  special_n_cansel: [null, 8, 0]
  special_n: [17, 45, 12]
  special_n_323: [17, 45, 30]
  special_air_n_start: [null, 8, 0]
  special_air_n_loop: [null, 12, 0]
  special_air_n_cancel: [null, 8, 0]
  special_air_n: [17, 45, 12]
  special_air_n_328: [17, 45, 27]
  special_s: [20, 60, 5]
  special_air_s: [20, 60, 10]
  special_hi: [3, 85, 12]
  special_air_hi: [4, 85, 10]
  special_lw_start: [null, 14, 0]
  special_lw_loop: [5, 27, 11]
  special_lw_end: [null, 20, 0]
  special_lw_end_336: [null, 20, 0]
oos:  # option: frame the hitbox is out
  special_hi: 4
  grab: 8
  uair: 11
  bair: 12
  nair: 15
  usmash: 15
  dair: 23
  fair: 30
resources: 9
# generated: end
---

# Donkey Kong

<!-- GENERATED:attributes -->
## Attributes

Read from `PlDk.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 114 |
| Gravity | 0.1 |
| Terminal fall speed | 2.4 |
| Fast-fall speed | 2.96 |
| Jump squat (frames before airborne) | 5 |
| Full hop / short hop initial Y speed | 2.7 / 1.6 |
| Air jump Y multiplier | 0.91 |
| Jumps | 2 |
| Walk max speed | 1.2 |
| Dash initial speed / run max speed | 1.6 / 1.6 |
| Ground friction (traction) | 0.08 |
| Air max horizontal speed | 1 |
| Air acceleration (base + stick) | 0.02 + 0.02 |
| Air friction | 0.02 |
| Normal landing lag | 5 |
| Shield size | 17.5 |
<!-- /GENERATED:attributes -->

## Overview

Donkey Kong (DK) is a super heavyweight who is fast for his size: fast walk, above-average
run, high air speed and a long [dash dance](../techniques/dash-dance.md)
[wiki:Donkey_Kong_(SSBM)]. He also falls fast (fourth-highest falling speed in the game
[wiki:Donkey_Kong_(SSBM)/Up_special]) but with only average gravity
[wiki:Donkey_Kong_(SSBM)]. He has no projectile and his forward-facing approach is poor, so
his neutral is played backward: turn around and space back air, which is fast, slightly
disjointed and safe on shield, then grab when the opponent starts shielding or dash dancing
around it [wiki:Donkey_Kong_(SSBM)/Back_aerial]. The grab is where he wins. His forward throw
is the "cargo" hold: he carries the opponent, can walk and jump, and has four extra throws.
Cargo up throw into up air is his bread and butter and leads to zero-to-death combos on
fastfallers and long juggles on most of the cast [wiki:Donkey_Kong_(SSBM)/Forward_throw]. He
kills with forward air, a charged neutral B (Giant Punch), up smash, the first hit of grounded
up B (Spinning Kong), and edgeguards. His weaknesses mirror his strengths: he is big, heavy and
fast-falling, so he is combo food and gets [chain grabbed](../techniques/chain-grab.md); his
shield covers him badly; and his recovery goes far sideways but gains almost no height, so
spikes and low hits kill him early [wiki:Donkey_Kong_(SSBM)]. Long regarded as low tier, he
rose in the 2020s through players such as Junebug [wiki:Donkey_Kong_(SSBM)].

## Strengths and weaknesses

- **Strengths:**
  - Punish game from grab: cargo up throw combos, chain grabs on fastfallers, cargo carry
    to the edge or offstage.
  - Back air: hits frames 7-8 (13%) and 9-15 (9%), auto-cancels on frames 1-6 and from 20,
    7 frames of [L-cancelled](../techniques/l-cancel.md) lag
    [wiki:Donkey_Kong_(SSBM)/Back_aerial].
  - Up air: frames 6-8, 14%, straight up, auto-cancels from frame 13
    [wiki:Donkey_Kong_(SSBM)/Up_aerial].
  - Grounded up B: hits and is intangible on frame 3 [wiki:Donkey_Kong_(SSBM)/Up_special];
    top-class [out of shield](../techniques/out-of-shield.md) option.
  - Many kill moves and strong edgeguarding (bair, down tilt, aerial up B, ledge attack).
  - Very heavy: survives vertical kill moves to high percent.
- **Weaknesses:**
  - Combo food: huge hurtbox (including his tie), high fall speed, heavy
    [wiki:Donkey_Kong_(SSBM)].
  - Recovery has almost no vertical gain; meteors and semi-spikes kill him at low percent.
  - No projectile; weak forward-facing approach; below-average grab range
    [wiki:Donkey_Kong_(SSBM)].
  - Shield leaves parts of him exposed (shield stabs) and he is weak to
    [shield pressure](../techniques/shield-pressure.md)
    [lib:Guide to Donkey Kong].
  - Slow smashes: forward smash frame 22, up smash frame 14 [fd].

## Character tech

### Cargo up throw combo

- **id:** `cargo-up-throw-combo`
- **What:** Grab, forward throw (enters the cargo hold), then up throw from the hold. The
  opponent goes straight up with low knockback and DK recovers fast, so up air connects and
  can be repeated.
- **Inputs:** Z (grab), forward on the stick, then up + A or Z while carrying. Optionally
  walk, turn or jump first. Follow with short hop or full hop up air.
- **Timing:** Cargo up throw releases on frame 14 of a 29-frame animation (other cargo
  throws: release frame 15 of 39) and does 7% [wiki:Donkey_Kong_(SSBM)/Forward_throw]
  [lib:Guide to Donkey Kong]. Up air hits on frame 6 and auto-cancels from frame 13, so a
  short hop fast-fall up air needs no L-cancel [lib:Guide to Donkey Kong]. DK's facing
  during the hold changes where a given DI (directional influence, holding a direction to
  bend the launch angle) sends the opponent relative to him; turning toward their DI before
  throwing keeps them closer [lib:Guide to Donkey Kong]. Jumping before the throw releases
  them higher, which buys time against fastfallers at low percent and reach against
  everyone at high percent [lib:Guide to Donkey Kong].
- **Used for:** Every DK punish. Routes by opponent class are in the Punish game table.
- **Common errors:** Throwing while the opponent is about to mash out (both take 10%
  [lib:Guide to Donkey Kong]); wrong facing; jumping the throw against mid-fallers (lets
  them escape the up air [lib:Guide to Donkey Kong]); late up air.
- **Drill idea:** CPU grabbed at a chosen percent with random DI; success when up air (or the
  routed finisher) hits before the CPU can act.

### Cargo chain grab

- **id:** `cargo-chain-grab`
- **What:** Against [Fox](fox.md), [Falco](falco.md) and
  [Captain Falcon](captain-falcon.md), cargo up throw (or regular up throw) can be followed
  directly by another grab, or by up air then a re-grab [wiki:Chain_grab].
- **Inputs:** Cargo up throw, dash [jump-cancel](../techniques/jump-cancel.md) grab under the
  falling opponent; or cargo up throw, short hop fast-fall up air, dash jump-cancel grab.
- **Timing:** Direct re-grabs work from 0% until about the mid 20s per one guide
  [lib:Guide to Donkey Kong] or about 30-40% per an older one [lib:DK Throw Mini-FAQ 2005].
  From 0%, up throw, up air, re-grab works twice on Fox/Falco. Captain Falcon can jump out
  after the second up air re-grab attempt, so use another up air there to catch the jump
  [lib:Guide to Donkey Kong]. The window after up air is short and DI makes it harder; a
  short-hopped cargo throw gives more time [lib:Guide to Donkey Kong].
- **Used for:** Building damage from 0% to the percent where up air strings start.
- **Common errors:** Using dash grab (slow, 40+ frame animation) instead of jump-cancel grab
  [lib:Guide to Donkey Kong]; grabbing before the opponent has fallen into range.
- **Drill idea:** CPU Fox at 0%, random DI; success when DK reaches 40% dealt with no CPU
  action.

### Cargo carry

- **id:** `cargo-carry`
- **What:** Moving with the opponent on his back to choose where the throw happens: under
  no platform for juggles, at the edge for an edgeguard, or offstage for a stage spike or a
  sacrificial KO [wiki:Donkey_Kong_(SSBM)].
- **Inputs:** Forward throw, then walk or jump; throw with a direction + A/Z.
- **Timing:** The opponent escapes by mashing; if they break out, both take 10%
  [lib:Guide to Donkey Kong] (the wiki lists the 10% for DK
  [wiki:Donkey_Kong_(SSBM)]). An opponent released from cargo does not get their double jump
  back if they had used it ("jumpkeeping"), unlike a normal grab release
  [wiki:Donkey_Kong_(SSBM)/Forward_throw]. Rule of thumb for pummels before throwing: about
  one per 25% of the opponent's damage [lib:DK Throw Mini-FAQ 2005].
- **Used for:** Cargo back throw offstage (it sends farther than cargo forward
  [lib:DK Throw Mini-FAQ 2005]); cargo down throw under the stage or for a low-angle send
  [wiki:Donkey_Kong_(SSBM)/Forward_throw]; around 70% on fastfallers, jump offstage, cargo
  down throw, double jump fair for a meteor [lib:DK Throw Mini-FAQ 2005].
- **Common errors:** Carrying a low-percent opponent offstage (they mash out and recover
  while DK cannot).
- **Drill idea:** CPU mashes at a realistic rate; success when DK carries to the ledge,
  throws offstage and takes the stock without losing his own.

### Giant Punch charge

- **id:** `giant-punch-charge`
- **What:** Neutral B winds up a punch through 10 arm swings; the charge can be stored by
  shielding or rolling out of the wind-up and released later with one press
  [wiki:Giant_Punch].
- **Inputs:** B to start swinging; L/R (or roll) to store; B again to punch. Also works in
  the air, where shield input cancels the wind-up.
- **Timing:** Each swing adds 2% [wiki:Donkey_Kong_(SSBM)]. Uncharged: hitbox on frame 24,
  51 frames total. Fully charged: hitbox on frame 17 (the frame data dump lists 18), brief
  intangibility on frames 17-18, 44 frames total
  [wiki:Donkey_Kong_(SSBM)/Neutral_special] [fd]. Full charge does up to 30% grounded and
  27% in the air [fd]. A punch one stage below full has noticeably more knockback than a
  full one, and a punch released straight from charging is stronger than a stored one
  [wiki:Giant_Punch]. The stored charge is lost if DK takes knockback while charging or is
  hit during up B [wiki:Giant_Punch]. Using it in the air leaves DK helpless
  [wiki:Giant_Punch].
- **Used for:** Combo finisher after up air strings or cargo up throw; whiff punish with a
  B-reversed punch that outranges bair [wiki:Donkey_Kong_(SSBM)/Back_aerial]; punishing
  rolls and landings.
- **Common errors:** Charging in range and being hit (charge lost); releasing in the air
  offstage (helpless); forgetting the charge was lost to a hit during up B.
- **Drill idea:** HUD shows stored stage; drill requires storing 9 or 10 swings in gaps
  after knockdowns, then landing it as a finisher.

### Reverse charge cancel

- **id:** `reverse-charge-cancel`
- **What:** A turnaround neutral B cancelled immediately with shield. It flips DK's facing
  (in the air too), so he can face backward for bair out of a forward jump
  [wiki:Giant_Punch].
- **Inputs:** Tap the stick backward, return to neutral, B, then L/R on the first wind-up;
  in the air follow with bair.
- **Timing:** The wind-up start animation is 7 frames and the cancel animation is 7 frames
  [fd]. With good timing a reverse charge cancel and a bair fit in one short hop
  [wiki:Donkey_Kong_(SSBM)/Back_aerial].
- **Used for:** Getting his best aerial out while moving forward; ledge options; mixups
  between bair and a turnaround grab; it also adds one swing to the stored punch each time.
- **Common errors:** Inputting a B-reverse instead of a turnaround B (the wind-ups cannot be
  B-reversed [wiki:Giant_Punch]); cancelling late and landing in the wind-up.
- **Drill idea:** From a forward short hop, success when DK's facing flips and a bair hitbox
  comes out before landing.

### Back air wall

- **id:** `bair-wall`
- **What:** Repeated spaced bairs as DK's main neutral tool and edgeguard, the way
  [Jigglypuff](jigglypuff.md) uses hers [wiki:Donkey_Kong_(SSBM)/Back_aerial].
- **Inputs:** Face away (pivot, turnaround shield stop, or reverse charge cancel), short
  hop, bair, fast fall, L-cancel; or rising bair that auto-cancels.
- **Timing:** Hit frames 7-15, interruptible from frame 32, auto-cancel from frame 20,
  landing lag 15 or 7 with L-cancel [fd] [wiki:Donkey_Kong_(SSBM)/Back_aerial]. A
  [SHFFL](../techniques/shffl.md)ed bair is about even (+/-0) on shield
  [wiki:Donkey_Kong_(SSBM)/Back_aerial]. Landing with the L-cancel rather than
  auto-cancelling lowers the hitbox so opponents cannot duck under it
  [lib:Guide to Donkey Kong].
- **Used for:** Approaching, walling, shield pressure into up B (a frame trap that beats
  most out-of-shield options, including Fox's shine
  [wiki:Donkey_Kong_(SSBM)/Back_aerial]), bair or tomahawk grab mixups, and offstage strings
  of two or three bairs ended by aerial up B [wiki:Donkey_Kong_(SSBM)/Back_aerial].
- **Common errors:** Facing forward (fair and nair are much worse); hitting shield deep and
  not following with up B or a buffered roll.
- **Drill idea:** CPU dash dances near bair range; success when a bair connects or hits
  shield at max spacing and DK is not punished.

### Spinning Kong out of shield

- **id:** `spinning-kong-out-of-shield`
- **What:** Jump-cancelled grounded up B from shield. Its first hit comes out on frame 3
  with intangibility and strong knockback.
- **Inputs:** While shielding, up (jump) then B on the next frame, before leaving the
  ground. Hold left or right to slide, ideally to a ledge.
- **Timing:** Grounded: intangible frames 3-5, hit 1 on frames 3-5 (12%, base knockback 60),
  weak spin hits from frame 19, 84 frames total [wiki:Donkey_Kong_(SSBM)/Up_special] [fd].
  Out of shield the hit lands on frame 4 at the earliest, since an up B cannot start on the
  first jumpsquat frame [wiki:Super_Jump_Punch]. The strong hit sits high on DK's upper
  body: it misses very short characters (Jigglypuff, Pichu) and short characters standing
  behind him; a short hop into immediate aerial up B has a different sweetspot that reaches
  them [lib:Guide to Donkey Kong]. The aerial version is intangible on frames 2-5 and hits
  on frame 3 [wiki:Donkey_Kong_(SSBM)/Up_special].
- **Used for:** Punishing shield pressure and aerials that land on him (for example Fox's
  full hop dair), after his own bair on shield, and as a kill move (it can be confirmed from
  combos and [tech chases](../techniques/tech-chase.md))
  [wiki:Donkey_Kong_(SSBM)/Up_special]. Sliding off the stage into a ledge grab removes the
  end lag.
- **Common errors:** Whiffing the strong hit on a short or spaced opponent, leaving DK in a
  long spin; jumping first (aerial version, weaker hit and helpless after).
- **Drill idea:** CPU Fox does nair or dair into shine on DK's shield; success when up B
  hit 1 connects in the gap.

### Spinning Kong at the ledge

- **id:** `spinning-kong-ledge`
- **What:** Three uses of up B around the ledge: sliding a grounded up B off the stage to
  grab the ledge from either direction (an edgehog similar to Bowser's fortress hog), an
  option select against Fox/Falco recoveries, and aerial up B as DK's ledge get-up.
- **Inputs:** (a) Grounded up B near the edge, hold toward the edge. (b) Up B as the
  opponent passes above the stage edge. (c) From ledge hang: drop, immediately up B, drift
  onto the stage.
- **Timing:** Aerial up B has arm intangibility on frames 11-42 while the hits are active
  [wiki:Donkey_Kong_(SSBM)/Up_special]. DK's [ledgedash](../techniques/ledgedash.md) gives
  only 7 frames of leftover intangibility even when frame perfect and kills him when
  mistimed, so up B from the ledge is the practical option
  [wiki:Donkey_Kong_(SSBM)/Up_special].
- **Used for:** (b) hits a Fox/Falco side B onto the stage and takes the ledge if they fall
  and up B instead [wiki:Donkey_Kong_(SSBM)/Up_special].
- **Common errors:** Sliding off facing so that the ledge is not grabbed in time; using the
  ledge up B into a waiting shield.
- **Drill idea:** CPU Fox recovers with side B or up B at random; one DK input sequence must
  beat both.

### Hand Slap

- **id:** `hand-slap`
- **What:** Down B slaps the ground: a wide, low quake hitbox that only hits grounded
  opponents, with set knockback that pops them up.
- **Inputs:** Down B; hold or repeat B to loop.
- **Timing:** Hits on frames 19-20 and 30-31, 60 frames total for the minimum two slaps; in
  a loop the hits come every 11 frames [wiki:Donkey_Kong_(SSBM)/Down_special]
  [lib:Guide to Donkey Kong]. 11% per hit [wiki:Donkey_Kong_(SSBM)].
- **Used for:** Covering every tech option at once in a tech chase; beating
  [crouch cancel](../techniques/crouch-cancel.md) (it tumbles crouching opponents of Peach's
  weight or lighter); shield damage; stopping grounded approaches from
  [Luigi](luigi.md) and [Ice Climbers](ice-climbers.md), and separating Nana
  [wiki:Donkey_Kong_(SSBM)/Down_special]. A hit can combo into grab.
- **Common errors:** Using it against airborne or aerial-approaching opponents (cannot hit
  them); starting it in range of a fast punish.
- **Drill idea:** CPU techs randomly after a knockdown; success when Hand Slap hits any tech
  option and a grab follows.

### Down tilt edgeguard

- **id:** `dtilt-edgeguard`
- **What:** Down tilt reaches below the stage lip and hits opponents trying to sweetspot
  the ledge.
- **Inputs:** Crouch at the ledge, down + A, repeat.
- **Timing:** Hits frames 6-9, only 22 frames total, 7%, 40° launch
  [wiki:Donkey_Kong_(SSBM)/Down_tilt] [fd].
- **Used for:** Repeatable edgeguard: it "always" hits Fox/Falco side B and Captain
  Falcon/Ganondorf up B at the ledge [lib:Guide to Donkey Kong]; after it hits, charge a
  forward smash for the next up B attempt [lib:Guide to Donkey Kong].
- **Common errors:** Standing too far back; mistiming against a recovery with a hitbox.
- **Drill idea:** CPU Captain Falcon up Bs to the ledge; success when down tilt hits him out
  of it twice in a row or forward smash kills the second attempt.

## Neutral game

- Face backward and wall with bair; dash dance to bait and grab (jump-cancel grab, not dash
  grab [lib:Guide to Donkey Kong]).
- Forward tilt (frames 8-11, 10% [fd]) is the best grounded poke; down tilt is the fast, low
  one (frame 6, safe because he is low to the ground and can
  [ASDI](../techniques/asdi.md) down hits at low percent)
  [wiki:Donkey_Kong_(SSBM)/Down_tilt].
- Up air as an air-to-air against short hops (for example Sheik and Ganondorf)
  [wiki:Donkey_Kong_(SSBM)/Up_aerial].
- Crouch cancel into grab or down smash (frame 10 [fd]); one guide's example is crouch
  cancelling Fox's nair and down smashing as Fox lands behind [lib:Guide to Donkey Kong].
- Charge Giant Punch whenever there is time.
- Light shield and platforms help against pressure; DK players are advised to avoid Final
  Destination against projectile characters and prefer Pokemon Stadium or Dream Land
  [lib:Guide to Donkey Kong].
- Avoid: dash attack (rated one of the worst moves in the game
  [wiki:Donkey_Kong_(SSBM)/Dash_attack]) and raw forward smash.

## Punish game

Everything routes through cargo up throw. The follow-up depends on the opponent's fall speed
and percent. "Jump the throw" means jumping during the cargo hold and throwing at the top.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| Cargo up throw | Fox, Falco, Captain Falcon | 0 to mid 20s (older source: 30-40) | Dash jump-cancel re-grab, repeat | Chain grab | [lib:Guide to Donkey Kong] [lib:DK Throw Mini-FAQ 2005] |
| Cargo up throw | Fox, Falco | from 0 | Short hop fast-fall up air, re-grab, repeat twice, then aerial string | Short hop the throw at low percent | [lib:Guide to Donkey Kong] |
| Cargo up throw | Captain Falcon | from 0 | Up air, re-grab, cargo up throw, up air, up air, string | He can jump out of the second re-grab | [lib:Guide to Donkey Kong] |
| Cargo up throw | fastfallers | about 100-120 | Up smash (follow DI), grounded up B hit 1, or short hop fair | Up smash stops working past about 120 | [lib:Guide to Donkey Kong] |
| Up throw | Fox, Falco | kill percent | Up smash if no DI; up B if DI away | Kill confirm | [wiki:Donkey_Kong_(SSBM)/Up_smash] |
| Cargo up throw (full hop the throw) | fastfallers | 120+ | Double jump fair or Giant Punch | Tight; react to DI | [lib:Guide to Donkey Kong] |
| Cargo up throw | Sheik, Ganondorf, Link, Roy, Bowser, DK | low-mid | Short hop up air, full hop up air, up air, then fair or Giant Punch | Do not jump the throw | [lib:Guide to Donkey Kong] |
| Cargo up throw (full hop the throw) | mid-fallers | 80+ | Double jump fair or Giant Punch | | [lib:Guide to Donkey Kong] |
| Cargo up throw (full hop the throw) | mid-fallers | about 100 | Double jump up air | Kills off the top | [lib:Guide to Donkey Kong] |
| Cargo up throw | Marth, Peach | up to about 80-90 | Fair from the ground | Sends offstage | [lib:Guide to Donkey Kong] |
| Cargo up throw | Marth, Peach, Young Link | low | Full hop up air, then up air or aerial up B | | [lib:Guide to Donkey Kong] |
| Cargo up throw | Jigglypuff, Samus, Luigi | any, works to about 120 | One up air | Pummel first; turn toward their DI | [lib:Guide to Donkey Kong] |
| Cargo up throw | floaties | from 0 | Up air, double jump aerial up B | About 43% total | [lib:Guide to Donkey Kong] |
| Cargo up throw | Jigglypuff | mid | Up air | Kill confirm | [wiki:Donkey_Kong_(SSBM)/Forward_throw] |
| Dair (meteor, grounded target) | fastfallers | mid-high | Charged up smash, bair, fair | Often on a platform | [lib:Guide to Donkey Kong] |
| Late bair | mid-fallers | mid | Bair or up air | | [lib:Guide to Donkey Kong] |
| Hand Slap | grounded, any | any | Grab | | [wiki:Donkey_Kong_(SSBM)/Down_special] |
| Grab on a platform | Fox, Falco, Captain Falcon | about 50-65 | Cargo up throw, forward smash | | [lib:Guide to Donkey Kong] |

### Chain grabs and tech chases

- Up throw and cargo up throw chain grab Fox, Falco and Captain Falcon at low to mid
  percents [wiki:Chain_grab]; details in the tech entry. Escapes: DI away plus double jump
  once the window is not frame-tight; Falcon after the second up air re-grab; landing on a
  platform and [teching](../techniques/teching.md).
- Down throw (release on frame 40 of 59 against a baseline weight
  [wiki:Donkey_Kong_(SSBM)/Down_throw]) puts non-fastfallers on the ground in front of DK
  for a tech chase at low percent: follow tech away with jump-cancel grab, cover tech in
  with turn-around grab, down smash or bair, or use Hand Slap for everything. Near a wall
  it is nearly a free Hand Slap [lib:DK Throw Mini-FAQ 2005].
- Side B (Headbutt) buries a grounded opponent; they mash out and are stuck in a pop-out
  animation that can be punished like a roll [lib:Guide to Donkey Kong]. It is slow
  (frames 20-21 [fd]) and rarely used.

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Fair (clean hit, frames 25-26) | Bowser | 128% from center stage | Usually after cargo up throw or up air; late hit is a meteor | [wiki:Donkey_Kong_(SSBM)/Forward_aerial] |
| Forward smash (elbow sweetspot) | Fox | 100% uncharged from center Battlefield | Frame 22; needs a hard read, jab reset or shield break | [wiki:Donkey_Kong_(SSBM)/Forward_smash] |
| Giant Punch (9-10 swings) | most | Unknown; DK's strongest hit, up to 30% | Stored charge; frame 17 | [wiki:Giant_Punch] [fd] |
| Up smash | fastfallers | about 90-120% from cargo up throw | Only hits above him; frames 14-16 | [lib:Guide to Donkey Kong] |
| Grounded up B hit 1 | most | Unknown | Frame 3; out of shield or after throw on DI away | [wiki:Donkey_Kong_(SSBM)/Up_special] |
| Up air | mid-fallers, floaties | about 100% when thrown from a full hop | Kills about 30% later than Fox's up air | [lib:Guide to Donkey Kong] |
| Bair | most | 100%+ offstage | Edgeguard | [wiki:Donkey_Kong_(SSBM)/Back_aerial] |
| Down smash | light characters | high | Frame 10, vertical | [lib:Guide to Donkey Kong] |
| Back throw | light characters | high | Edge of stage | [lib:DK Throw Mini-FAQ 2005] |
| Dair / late fair / aerial side B (meteors) | any | any, offstage | Can be [meteor cancelled](../techniques/meteor-cancel.md) | [wiki:Donkey_Kong_(SSBM)] |

- When a combo ender does not kill it usually puts the opponent offstage, where DK uses
  down tilt at the ledge, ledge-drop double jump bair and regrab, aerial up B's first hit,
  or simply the ledge [wiki:Donkey_Kong_(SSBM)/Forward_aerial].
- Fair offstage is risky: half a second of end lag and DK cannot regain height
  [wiki:Donkey_Kong_(SSBM)/Forward_aerial].
- Cargo carry offstage for a stage spike or a traded stock at high percent.
- Against a missed Rest, shield break or jab reset, forward smash instead of Giant Punch
  keeps the charge [wiki:Donkey_Kong_(SSBM)/Forward_smash].

## Recovery

- **Options:**
  - Aerial up B: long horizontal travel, almost no height; body intangible frames 2-5, arms
    intangible frames 11-42, hits throughout [wiki:Donkey_Kong_(SSBM)/Up_special].
  - Double jump (must be saved for height).
  - Aerial side B and Giant Punch wind-up as small stalls [lib:Guide to Donkey Kong].
  - No wall jump, nothing that slows his fall [wiki:Donkey_Kong_(SSBM)].
- **Mixups:** Recover high over the edgeguarder (his weight lets him do this repeatedly);
  hover at arm's length from the ledge so the intangible arms clear ledge-covering moves
  and he still grabs it automatically [lib:Guide to Donkey Kong]; land on a platform; early
  versus late up B.
- **Weaknesses:** Once below the ledge he cannot come back up. Any meteor, spike or
  semi-spike kills at low percent; disjointed attacks beat the up B from below; a hit
  during up B also deletes his Giant Punch charge [wiki:Giant_Punch].

### Edgeguarding Donkey Kong

- Force him low: take his double jump with a hit, then let him fall, or edgehog when he is
  level with the ledge.
- Hit from above or below the spinning arms. Luigi's dair from directly above is one
  documented answer [lib:Smash God's Epic 2000th Post Luigi Guide 2009]; Falco's and
  Marth's spikes are the classic ones.
- Do not challenge the arms from the side during frames 11-42.
- A CPU DK should DI up and toward the stage, up B early enough to stay above ledge height,
  drift to the ledge at arm's length, and sometimes go high onto a platform.

## Defense and out of shield

- Up B out of shield is the main answer (hit on frame 4 from shield, intangible).
- Bair out of shield when the opponent has crossed up or is spaced where up B would whiff;
  up air out of a [shield drop](../techniques/shield-drop.md)
  [wiki:Donkey_Kong_(SSBM)/Back_aerial].
- Shield grab is only for unspaced attacks; grab range is below average.
- Crouch cancel into grab or down smash at low percent.
- Aerial up B (intangible from frame 2) is his combo breaker and can carry him to a top
  platform to escape juggles [wiki:Donkey_Kong_(SSBM)/Up_special]. His normal aerials cover
  his limbs, not his body, so they are poor escapes.
- He loses to sustained shield pressure and to projectile camping
  [lib:Guide to Donkey Kong]; his shield leaves parts of his body open to shield stabs
  [wiki:Donkey_Kong_(SSBM)].

## As the training dummy

- Super heavyweight, fastfaller-class fall speed, very large body with a tie hurtbox
  [wiki:Donkey_Kong_(SSBM)]. Vertical combos work on him for a long time and he survives
  the top blast line to high percent, so opponents usually kill him sideways or by gimp.
- Chain grabs on him: [Sheik](sheik.md)'s down throw from 0% to medium or high percents in
  NTSC [wiki:Chain_grab]. [Dr. Mario](dr-mario.md)'s down throw only in a tiny window
  (13-15% after throw) [lib:Doc Advanced Tech Frame Data Megathread].
  [Bowser](bowser.md)'s side B forward throw into up air works on him
  [wiki:Bowser_(SSBM)/Up_aerial]. Other characters' up throw chains on DK: likely (Marth,
  Fox up throw up air) but not sourced here [unverified].
- Strong CPU choices: aerial up B at the first actionable frame when being juggled; DI away
  from up throws; crouch cancel and ASDI down at low percent (he is heavy, so this works to
  a higher percent than for most characters; thresholds Unknown); up B out of shield when
  pressured.
- For edgeguard drills, his recovery is one-dimensional: horizontal up B at or above ledge
  height. Spike practice is the natural use.
- Throws on him run slower because throw speed scales with weight; weight-dependent release
  timings in other characters' files matter here.

## Matchup notes

### vs Fox

- DK's reward is a zero-to-death from any grab; up B out of shield and crouch cancel down
  smash punish Fox's aerial approaches [lib:Guide to Donkey Kong]. Fox's reward is also
  huge: up throw up air, shine combos, and shine spikes on a recovery with no height.
- Stage choice matters; DK prefers platforms to escape lasers [lib:Guide to Donkey Kong].

### vs Falco

- Called the worst matchup by the 2014 guide ("Peach, Sheik and FALCO are hell")
  [lib:Guide to Donkey Kong]: lasers stop his approach, pillar combos work for a long time
  on his body, and dair kills his recovery. DK still kills Falco from one grab.

### vs Sheik

- Hard: down throw chain grab on DK [wiki:Chain_grab], needles, and easy edgeguards. DK
  gets up air strings from cargo up throw and up air as a kill move on her
  [wiki:Donkey_Kong_(SSBM)/Up_aerial].

### vs Marth

- Rated one of the two easiest top tiers for DK by the 2014 guide
  [lib:Guide to Donkey Kong]: DK's bair and forward tilt contest Marth's range, and cargo
  up throw leads to fair until about 80-90%. Marth's dair and down tilt punish DK's
  recovery.

### vs Jigglypuff

- The other "easiest" top tier per the same guide. Cargo up throw up air is a kill confirm
  at mid percent [wiki:Donkey_Kong_(SSBM)/Forward_throw]; a missed Rest is a free charged
  smash or Giant Punch. Grounded up B out of shield misses her because she is short
  [lib:Guide to Donkey Kong].

### vs Peach

- Listed as one of DK's three hardest matchups by the 2014 guide, without detail
  [lib:Guide to Donkey Kong]. Expect turnips against a character with no projectile and
  pressure on a shield that covers him badly. Cargo up throw fair works until about 80-90%
  [lib:Guide to Donkey Kong].

### vs Luigi and Ice Climbers

- Hand Slap is unusually good against their wavedash approaches
  [wiki:Donkey_Kong_(SSBM)/Down_special].

## Drill seeds

### Cargo up throw to up air to re-grab

- **id:** `donkey-kong-cargo-uair-regrab`
- **Goal:** The 0% fastfaller opener.
- **Player:** Donkey Kong
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** Final Destination, center. CPU grabbed at 0%.
- **CPU behaviour:** Random DI on the throw and on the up air; jumps, shines or attacks on
  the first actionable frame.
- **Success:** Cargo up throw, up air, re-grab, cargo up throw, up air all connect with no
  CPU action (versus Captain Falcon: the second up air is followed by a third up air instead
  of a grab).
- **Fail:** CPU acts, or DK misses a grab.
- **Variations:** Require a short-hopped throw; pure chain grab (no up air) to the mid 20s;
  Battlefield with platform techs.
- **Data needed:** Cargo up throw release frame 14 of 29 and 7% [wiki:Donkey_Kong_(SSBM)/Forward_throw];
  up air frames 6-8, auto-cancel from 13; DK grab startup; fastfaller fall speeds and
  weights.

### Up air juggle to finisher

- **id:** `donkey-kong-uair-juggle`
- **Goal:** Keep a mid-faller in up air strings and end with fair or Giant Punch.
- **Player:** Donkey Kong
- **CPU:** Sheik, Ganondorf, Link, Roy, Marth
- **Setup:** CPU grabbed at 20-40%; DK has a stored 9-swing Giant Punch.
- **CPU behaviour:** Random DI; double jumps or air dodges when possible.
- **Success:** At least three up airs connect and the last hit is fair (clean hit) or Giant
  Punch.
- **Fail:** CPU lands or acts before the finisher.
- **Variations:** No stored punch (fair only); floaty CPU where only one up air then aerial
  up B works.
- **Data needed:** Up air knockback (14%, 90°, base 32, growth 90 [fd]); fair clean hit
  frames 25-26; Giant Punch full-charge timing.

### Kill confirm from cargo at high percent

- **id:** `donkey-kong-cargo-kill`
- **Goal:** Pick the right finisher from DI and percent.
- **Player:** Donkey Kong
- **CPU:** Fox, Falco (100-130%); Sheik, Marth (80-110%); Jigglypuff (50-80%)
- **Setup:** CPU grabbed mid stage at a percent in the listed band.
- **CPU behaviour:** Random DI (none, in, away); mashes out of cargo at a realistic rate.
- **Success:** The follow-up connects before the CPU acts and kills: up smash on no DI, up B
  hit 1 or short hop fair on DI away for fastfallers; full-hop throw into double jump
  fair/up air for mid-fallers; up air for Jigglypuff.
- **Fail:** CPU survives or escapes; cargo break-out (10% to DK).
- **Variations:** Hide the DI indicator; add platforms.
- **Data needed:** Up smash frames 14-16 and hitbox height; up B hit 1; fair; victim
  weights and blast-zone heights.

### Up B out of shield

- **id:** `donkey-kong-upb-oos`
- **Goal:** Punish pressure with the frame 3 hit.
- **Player:** Donkey Kong
- **CPU:** Fox, Falco, Sheik, Marth
- **Setup:** DK shielding center stage at 0-60%.
- **CPU behaviour:** Aerial on shield followed at random by shine, jab, grab or a second
  aerial; sometimes crosses up; sometimes spaces out of range.
- **Success:** Up B hit 1 connects in the first available gap; on cross-up or spaced cases
  the player chooses bair out of shield or holds shield instead.
- **Fail:** DK is hit or grabbed, or whiffs up B.
- **Variations:** Short CPU (Jigglypuff, Pikachu) where the answer is short hop aerial up B;
  slide to ledge after the hit to cancel lag.
- **Data needed:** Grounded up B frames 3-5 and intangibility
  [wiki:Donkey_Kong_(SSBM)/Up_special]; hitbox height versus CPU hurtboxes; shield stun of
  CPU moves.

### Back air spacing on shield

- **id:** `donkey-kong-bair-spacing`
- **Goal:** Safe bair pressure and the bair/grab mixup.
- **Player:** Donkey Kong
- **CPU:** Marth, Sheik, Fox
- **Setup:** DK and CPU mid-range on Final Destination, DK facing away.
- **CPU behaviour:** Shields when DK jumps toward it; shield grabs if DK lands close with
  lag; otherwise dash dances and punishes whiffs.
- **Success:** Bair hits shield at tip range with an L-cancel and DK is not grabbed, three
  times in a row; or a tomahawk turnaround grab lands when the CPU pre-shields.
- **Fail:** DK is shield grabbed or whiff punished.
- **Variations:** Enter via reverse charge cancel from a forward-facing run; follow a deep
  bair with up B.
- **Data needed:** Bair hit frames, 7-frame L-cancel lag [fd]; shield stun for 13% and 9%
  hits; CPU grab startup.

### Giant Punch whiff punish

- **id:** `donkey-kong-giant-punch-punish`
- **Goal:** Use a stored punch as a long-range punish.
- **Player:** Donkey Kong
- **CPU:** Marth, Captain Falcon, Sheik
- **Setup:** DK starts with a 9-swing stored punch; CPU at 70-100%.
- **CPU behaviour:** Dash dances just outside bair range and occasionally whiffs a laggy
  move or rolls in/away.
- **Success:** Giant Punch hits during the CPU's lag or at the end of its roll.
- **Fail:** Punch whiffs or is shielded; DK is hit while holding the charge.
- **Variations:** Start with no charge and require charging during safe moments (HUD shows
  stage); require a turnaround punch.
- **Data needed:** Full-charge hit frame 17-18 and range
  [wiki:Donkey_Kong_(SSBM)/Neutral_special] [fd]; charge stage in memory; CPU roll and move
  durations.

### Ledge down tilt edgeguard

- **id:** `donkey-kong-dtilt-edgeguard`
- **Goal:** Repeated low hits on sweetspot recoveries.
- **Player:** Donkey Kong
- **CPU:** Captain Falcon, Ganondorf, Fox, Falco, Marth
- **Setup:** CPU offstage below the ledge at 60%; DK standing at the ledge.
- **CPU behaviour:** Recovers to the ledge sweetspot with up B or (Fox/Falco) side B; after
  being hit, tries again.
- **Success:** CPU is hit by down tilt at least once and loses the stock (by a second down
  tilt, a charged forward smash, bair or the ledge).
- **Fail:** CPU grabs the ledge or lands.
- **Variations:** Spinning Kong option select version against Fox/Falco; ledge-drop double
  jump bair version.
- **Data needed:** Down tilt frames 6-9, 22 total, reach below the lip
  [wiki:Donkey_Kong_(SSBM)/Down_tilt]; CPU recovery timings.

### Recover without dying to a spike

- **id:** `donkey-kong-recovery`
- **Goal:** Manage height and use arm intangibility.
- **Player:** Donkey Kong
- **CPU:** Marth (down tilt, dair), Falco (dair), Sheik (bair)
- **Setup:** DK launched offstage at 40-80% at or above ledge height with his double jump.
- **CPU behaviour:** Covers the ledge with one option at random: stand and down tilt/smash
  the ledge, jump out with a spike, or hold the ledge.
- **Success:** DK grabs the ledge or lands and is actionable.
- **Fail:** DK dies or is hit back offstage.
- **Variations:** No double jump; stored Giant Punch at stake (fail if hit during up B).
- **Data needed:** Aerial up B travel distance and arm intangibility 11-42
  [wiki:Donkey_Kong_(SSBM)/Up_special]; ledge grab box.

### Hand Slap tech chase

- **id:** `donkey-kong-hand-slap-techchase`
- **Goal:** Cover all techs with one move and convert to grab.
- **Player:** Donkey Kong
- **CPU:** Sheik, Marth, Peach
- **Setup:** CPU knocked down in front of DK after a down throw at 20-50%.
- **CPU behaviour:** Random tech in place, toward, away, or missed tech.
- **Success:** Hand Slap hits and a grab connects before the CPU lands and acts.
- **Fail:** Slap whiffs (wrong timing or spacing) or no follow-up.
- **Variations:** Reaction version with jump-cancel grab instead; wall nearby.
- **Data needed:** Hand Slap hit frames 19-20 and 30-31, horizontal range
  [wiki:Donkey_Kong_(SSBM)/Down_special]; CPU tech distances and durations.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlDk.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/donkey-kong.json`](../framedata/donkey-kong.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 5-7 | 4 | Sakurai | 0 | 100 | - |  | 24 | - | 3 | -16 |  |
| Jab 2 | `jab2` | 5-11 | 6 | Sakurai | 0 | 100 | - |  | 34 | - | 4 | -25 | starts 1 frame late (included) |
| Dash attack | `dash_attack` | 9-12 | 11 | 100 | 115 | 15 | - |  | 54 | - | 6 | -39 |  |
|  |  | 13-20 | 9 | 100 | 0 | 100 | 120 |  |  |  | 6 | -35 |  |
| Forward tilt (angled up) | `ftilt_high` | 8-11 | 11 | Sakurai | 10 | 100 | - |  | 33 | - | 6 | -19 |  |
| Forward tilt | `ftilt` | 8-11 | 10 | Sakurai | 10 | 100 | - |  | 33 | - | 6 | -19 |  |
| Forward tilt (angled down) | `ftilt_low` | 8-11 | 9 | Sakurai | 10 | 100 | - |  | 33 | - | 6 | -19 |  |
| Up tilt | `utilt` | 6-11 | 9/10/11 | 100 | 40 | 105/110/115 | - |  | 39 | - | 6 | -27 |  |
| Down tilt | `dtilt` | 6-9 | 7 | 40 | 10 | 80 | - |  | 22 | - | 5 | -11 |  |
| Forward smash | `fsmash` | 22-23 | 20/21/19/18 | Sakurai | 22/18 | 94/100 | - |  | 54 | - | 11 | -21 | charge hold frame 15 |
| Up smash | `usmash` | 14-16 | 18 | 90 | 40 | 93 | - |  | 53 | - | 10 | -29 | charge hold frame 7; partly intangible 12-16 (3 bones) |
| Down smash | `dsmash` | 10-13 | 16/14 | 115/98 | 35 | 100 | - |  | 55 | - | 9 | -36 | charge hold frame 3 |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (5 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 10-13 | 12 | Sakurai | 0 | 100 | - |  | 43 | 39 | 7 | 20 | 10 | <10, >38 | -3 |  |
|  |  | 14-26 | 10 | Sakurai | 0 | 100 | - |  |  |  | 6 |  |  |  | -4 |  |
| Forward air | `fair` | 25-26 | 16 | Sakurai | 20 | 100 | - |  | 59 | - | 9 | 30 | 15 | <1, >59 | -6 |  |
|  |  | 27-29 | 16 | 270 | 50 | 80 | - |  |  |  | 9 |  |  |  | -6 |  |
| Back air | `bair` | 7-8 | 13 | Sakurai | 10 | 100 | - |  | 39 | 32 | 7 | 15 | 7 | <7, >19 | +0 |  |
|  |  | 9-15 | 9 | Sakurai | 0 | 100 | - |  |  |  | 6 |  |  |  | -1 |  |
| Up air | `uair` | 6-8 | 14 | 90 | 32 | 90 | - |  | 44 | 38 | 8 | 25 | 12 | <6, >12 | -4 |  |
| Down air | `dair` | 18-23 | 16/13 | 270 | 38/20 | 90 | - |  | 54 | - | 9 | 31 | 15 | <3, >49 | -6 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 8-9 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 10-11 | 50 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 10 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | - | - | - | - | - | - | - | - | 19 |  |
| Back throw | `bthrow` | 11 | 11 | 45 | 60 | 65 | - | - | 13 | 39 |  |
| Up throw | `uthrow` | 9 | 9 | 90 | 70 | 50 | - | - | 13 | 43 |  |
| Down throw | `dthrow` | 7 | 7 | Sakurai | 60 | 45 | - | - | 40 | 59 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Giant Punch, ground, Start | `special_n_start` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Neutral B: Giant Punch, ground, Loop | `special_n_loop` | - | - | - | - | - | - | - | 11 | - | - | - |  |
| Neutral B: Giant Punch, ground, Cansel | `special_n_cansel` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Neutral B: Giant Punch, ground | `special_n` | 17 | 12 | 80 | 15 | 100 | - |  | 44 | - | 7 | - |  |
|  |  | 18-21 | 10 | Sakurai | 15 | 100 | - |  |  |  | 6 | - |  |
| Neutral B: Giant Punch, ground | `special_n_323` | 17 | 18 | 80 | 40 | 90 | - |  | 44 | - | 10 | - | intangible 17-18 |
|  |  | 18-21 | 30 | Sakurai | 10 | 90 | - |  |  |  | 15 | - |  |
| Neutral B: Giant Punch, air, Start | `special_air_n_start` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Neutral B: Giant Punch, air, Loop | `special_air_n_loop` | - | - | - | - | - | - | - | 11 | - | - | - |  |
| Neutral B: Giant Punch, air, Cancel | `special_air_n_cancel` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Neutral B: Giant Punch, air | `special_air_n` | 17 | 12 | 80 | 15 | 100 | - |  | 44 | - | 7 | - |  |
|  |  | 18-21 | 10 | Sakurai | 15 | 100 | - |  |  |  | 6 | - |  |
| Neutral B: Giant Punch, air | `special_air_n_328` | 17 | 16 | 80 | 40 | 90 | - |  | 44 | - | 9 | - | intangible 17-18 |
|  |  | 18-21 | 27 | Sakurai | 10 | 90 | - |  |  |  | 14 | - |  |
| Side B: Headbutt, ground | `special_s` | 20-21 | 5 | 270 | 0 | 100 | 100 | bury | 59 | - | 4 | - |  |
| Side B: Headbutt, air | `special_air_s` | 20-21 | 10 | 270 | 0 | 100 | 100 |  | 59 | - | 6 | - |  |
| Up B: Spinning Kong, ground | `special_hi` | 3-5 | 12 | Sakurai | 60 | 100 | - |  | 84 | - | 7 | - | intangible 3-5 |
|  |  | 19-26, 27-34 | 8 | Sakurai | 50 | 70 | - |  |  |  | 5 | - |  |
|  |  | 35-42, 43-50, 51-58 | 3 | Sakurai | 10 | 90 | - |  |  |  | 3 | - |  |
| Up B: Spinning Kong, air | `special_air_hi` | 4-5 | 10 | Sakurai | 40 | 80 | - |  | 84 | - | 6 | - | intangible 4-5; partly intangible 11-42 (2 bones) |
|  |  | 11-18, 19-26, 27-34, 35-42 | 5/4 | Sakurai | 20 | 70 | - |  |  |  | 4 | - |  |
|  |  | 43-50, 51-58, 59-66 | 2 | Sakurai | 0 | 100 | - |  |  |  | 2 | - |  |
| Down B: Hand Slap, ground, Start | `special_lw_start` | - | - | - | - | - | - | - | 13 | - | - | - |  |
| Down B: Hand Slap, ground, Loop | `special_lw_loop` | 5-6 | 11 | 84 | 20 | 100 | 110 |  | 26 | - | 6 | - |  |
|  |  | 16-17 | 11 | 84 | 30 | 100 | 110 |  |  |  | 6 | - |  |
| Down B: Hand Slap, ground, End | `special_lw_end` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Down B: Hand Slap, ground, End | `special_lw_end_336` | - | - | - | - | - | - | - | 19 | - | - | - |  |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-23 | - | 37 | 33 |  |
| Roll forward | `roll_forward` | intangible 4-19 | - | 31 | - |  |
| Roll backward | `roll_backward` | intangible 4-19 | - | 31 | - |  |
| Air dodge | `airdodge` | intangible 4-29 | - | 49 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-24 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-19 | 6-7, 18-19 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-24 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-25 | 19-20, 24-25 (6%) | 49 | - |  |
| Getup roll forward (face down) | `getup_roll_forward_facedown` | intangible 1-14 | - | 35 | - |  |
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-24 | - | 35 | - |  |
| Tech in place | `tech_in_place` | intangible 2-20 | - | 26 | - | starts 1 frame late (included) |
| Tech roll forward | `tech_roll_forward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Tech roll backward | `tech_roll_backward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Wall tech | `wall_tech` | - | - | 25 | - | starts 1 frame late (included) |
| Wall tech jump | `wall_tech_jump` | - | - | 40 | - | starts 1 frame late (included) |
| Ceiling tech | `ceiling_tech` | intangible 2-15 | - | 25 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-55 | - | 59 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 34 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-33 | 37-49 (10%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-5 | 9-16 (8%) | 54 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-61 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-34 | - | 49 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-22 | - | 22 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 15 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-11 | - | 11 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 16 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Up B | jump cancel | 4 | `special_hi` |
| Shield grab | direct | 8 | `grab` |
| Up air | jump | 11 | `uair` |
| Back air | jump | 12 | `bair` |
| Neutral air | jump | 15 | `nair` |
| Up smash | jump cancel | 15 | `usmash` |
| Down air | jump | 23 | `dair` |
| Forward air | jump | 30 | `fair` |
| Spot dodge | direct | intangible 2-23 of 37 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 17 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Donkey Kong indexed by [The Melee Library](https://www.meleelibrary.com/#donkey-kong) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Donkey Kong Melee Techs Guide](https://www.youtube.com/watch?v=AkrRPV8Uv1k&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=12&t=0s) | Third Chair | Video guide on performing useful Donkey Kong tech in 2020. |
| [DK Melee Chaingrab Guide](https://www.youtube.com/watch?v=ZZzyEpEOsBI&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=5&t=0s) | Third Chair |  |
| [Jumpkeeping? a New DK Tech!?](https://smashboards.com/threads/jumpkeeping-a-new-dk-tech.481975/) | Soniclamp |  |
| [DK Video Archive](https://www.youtube.com/playlist?list=PLi3ZQqPymrsCYxaFn161340zHz_8-DsGd) | wutadisaster | Collection of nearly every DK video. |
| [Donkey Kong Hitboxes and Frame Data](https://smashboards.com/threads/donkey-kong-hitboxes-and-frame-data.298620/) | Stratocaster, Standardtoaster, and SuperDoodleMan |  |
| [DK Throw Mini-FAQ 2005](https://smashboards.com/threads/dk-throw-mini-faq.59133/) | Brahma | An old guide talking about the uses of DK's throws. |
| [Guide to Donkey Kong](https://smashboards.com/threads/guide-to-donkey-kong-2014-update-in-progress.294993/) | NJzFinest | A very simple introductory guide to DK. It covers the uses of his moves and also cargo uthrow combos. |
| [DK Questions and Answers Thread](https://smashboards.com/threads/the-official-ask-your-questions-thread.185701/) | community |  |
| [DK's Match-Up Chart thread](https://smashboards.com/threads/dks-match-up-chart-thread.286771/) | community | DK matchups discussion. |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Donkey Kong (SSBM): https://www.ssbwiki.com/Donkey_Kong_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Donkey_Kong_(SSBM)/Forward_throw ,
  /Up_special , /Neutral_special , /Down_special , /Side_special , /Back_aerial ,
  /Up_aerial , /Forward_aerial , /Neutral_aerial , /Forward_smash , /Up_smash , /Down_tilt ,
  /Forward_tilt , /Dash_attack , /Up_throw , /Down_throw
- SSBWiki, Giant Punch: https://www.ssbwiki.com/Giant_Punch
- SSBWiki, Spinning Kong: https://www.ssbwiki.com/Spinning_Kong
- SSBWiki, Chain grab: https://www.ssbwiki.com/Chain_grab
- SSBWiki, Forward throw (cargo section): https://www.ssbwiki.com/Forward_throw
- SSBWiki, Bowser (SSBM)/Up aerial: https://www.ssbwiki.com/Bowser_(SSBM)/Up_aerial
- SSBWiki, List of SSBM tier lists (NTSC): https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- NJzFinest and others, "Guide to Donkey Kong" (first posts, via web.archive.org):
  https://smashboards.com/threads/guide-to-donkey-kong-2014-update-in-progress.294993/
- Brahma, "DK Throw Mini-FAQ" (2005, via web.archive.org):
  https://smashboards.com/threads/dk-throw-mini-faq.59133/
- Schmooblidon, "Doc Advanced Tech Frame Data Megathread" (Magus chain grab chart, DK row):
  http://smashboards.com/threads/doc-advanced-tech-frame-data-megathread.378813/
- SmashGod, Luigi guide (edgeguarding DK's up B):
  http://smashboards.com/threads/smash-gods-epic-2000th-post-luigi-guide-updated-jan-16-13-with-more-to-come.228500/
- Frame data dump: `Donkey Kong.json`
