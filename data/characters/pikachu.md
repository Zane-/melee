---
schema: melee-character/v1
id: pikachu
name: Pikachu
aliases: [Pika]
tier: "B+ (9th of 26), 2021 list"
archetype: [rushdown, edgeguarder, lightweight, punish-heavy, mixup, chaingrab]
related: [pichu]
summary: Pikachu wins by turning stray hits into up air juggles and up smash kills on stage, and by gimping opponents off stage with up air, down air and a recovery long enough to chase anywhere.
key_tech: [uair-juggle, uair-tail-spike, quick-attack-angles, quick-attack-ledge-sweetspot, up-b-momentum-cancel, uthrow-chaingrab, uthrow-usmash, jab-reset, nair-crossup, thunder-jolt-edgeguard, thunderspike]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlPk.dat
framedata: ../framedata/pikachu.json
code: src/melee/ft/kinds/ftPikachu
specials:
  neutral_b: "Thunder Jolt"
  side_b: "Skull Bash"
  up_b: "Quick Attack"
  down_b: "Thunder"
attributes:
  weight: 80
  gravity: 0.11
  fall_speed: 1.9
  fast_fall_speed: 2.7
  jump_squat: 3
  jumps: 2
  walk_speed: 1.24
  dash_speed: 1.8
  run_speed: 1.8
  traction: 0.09
  air_speed: 0.85
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [2, 22, 2]
  dash_attack: [5, 50, 8]
  ftilt_high: [5, 30, 9]
  ftilt: [5, 30, 8]
  ftilt_low: [5, 30, 7]
  utilt: [7, 24, 7]
  dtilt: [7, 19, 7]
  fsmash: [16, 50, 21]
  usmash: [8, 41, 19]
  dsmash: [7, 51, 3]
  nair: [3, 40, 12]
  fair: [10, 40, 2]
  bair: [4, 60, 12]
  uair: [3, 28, 4]
  dair: [14, 48, 12]
  grab: [7, 31, 0]
  dash_grab: [11, 41, 0]
  pummel: [3, 25, 3]
  fthrow: [10, 44, 2]
  bthrow: [null, 50, 9]
  uthrow: [14, 44, 5]
  dthrow: [12, 48, 5]
  special_n: [null, 58, 0]
  special_air_n: [null, 58, 0]
  special_s_start: [null, 14, 0]
  special_s_hold: [null, 6, 0]
  special_s: [4, 40, 4]
  special_s_300: [null, 40, 0]
  special_s_end: [null, 45, 0]
  special_air_s_start: [null, 14, 0]
  special_air_s_hold: [null, 6, 0]
  special_s_304: [4, 40, 4]
  special_air_s_end: [null, 30, 0]
  special_hi_start: [13, 14, 3]
  special_hi_start_307: [13, 14, 2]
  special_hi_end: [null, 50, 0]
  special_air_hi_start: [13, 14, 3]
  special_air_hi_start_310: [13, 14, 2]
  special_air_hi_end: [null, 50, 0]
  special_lw_start: [null, 18, 0]
  special_lw_loop: [null, 10, 0]
  special_lw_loop_314: [1, 10, 17]
  special_lw_end: [null, 36, 0]
  special_air_lw_start: [null, 18, 0]
  special_air_lw_loop: [null, 10, 0]
  special_air_lw_loop_318: [1, 10, 17]
  special_air_lw_end: [null, 36, 0]
oos:  # option: frame the hitbox is out
  nair: 6
  uair: 6
  bair: 7
  grab: 7
  usmash: 9
  fair: 13
  special_hi_start: 14
  dair: 17
resources: 21
# generated: end
---

# Pikachu

<!-- GENERATED:attributes -->
## Attributes

Read from `PlPk.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 80 |
| Gravity | 0.11 |
| Terminal fall speed | 1.9 |
| Fast-fall speed | 2.7 |
| Jump squat (frames before airborne) | 3 |
| Full hop / short hop initial Y speed | 2.6 / 1.7 |
| Air jump Y multiplier | 1 |
| Jumps | 2 |
| Walk max speed | 1.24 |
| Dash initial speed / run max speed | 1.8 / 1.8 |
| Ground friction (traction) | 0.09 |
| Air max horizontal speed | 0.85 |
| Air acceleration (base + stick) | 0.02 + 0.03 |
| Air friction | 0.01 |
| Normal landing lag | 4 |
| Shield size | 12 |
<!-- /GENERATED:attributes -->

## Overview

Pikachu is a small, fast, light character with very short range. The wiki describes it as
the third fastest dasher, with medium fall speed, high traction (so a short
[wavedash](../techniques/wavedash.md)) and below-average air speed
[wiki:Pikachu_(SSBM)]. Neutral is the hard part: almost every useful move needs Pikachu to
be touching the opponent, the grab is the shortest in the game, and there is little safe
shield pressure, so Pikachu gets in with neutral B (Thunder Jolt), short hop nair
cross-ups and dash-dance baits [wiki:Pikachu_(SSBM)]. Once a hit lands the punish is
strong: uair juggles, uthrow chain grabs on fastfallers, and the strongest usmash in the
game as a finisher [wiki:Pikachu_(SSBM)/Up_smash]. Off stage Pikachu is one of the best
edgeguarders, because up B (Quick Attack) and side B (Skull Bash) bring it back from very
deep. Pikachu dies early to vertical kill moves and combos (weight 80, fall speed 1.9
[wiki:Pikachu_(SSBM)]) and loses neutral to disjointed hitboxes, especially
[Marth](marth.md). The character is considered hard to play well.

## Strengths and weaknesses

- **Strengths:**
  - Usmash is the strongest up smash in the game at realistic kill percents and hits on
    frame 8 [fd] [wiki:Pikachu_(SSBM)/Up_smash].
  - Uair is active on frame 3 [fd], juggles at any percent, and its middle frames send at
    angle 0 (a semi-spike, a launch that travels flat and low) [fd].
  - Recovery is long, fast and multi-directional; most characters must guess rather than
    react to edgeguard it [wiki:Pikachu_(SSBM)].
  - Small hurtbox; hard to shield poke; tech in place leaves only 2 vulnerable frames
    where every other character except [Pichu](pichu.md) has 6 [wiki:Tech].
  - Jab is fast (frame 2 [fd]) and weak, giving reliable
    [jab resets](../techniques/jab-reset.md) [wiki:Pikachu_(SSBM)].
  - Thunder Jolt hugs the ground, ledges and walls and interrupts some recoveries
    [wiki:Pikachu_(SSBM)].
- **Weaknesses:**
  - Very short range on almost everything; shortest grab in the game
    [wiki:Pikachu_(SSBM)].
  - Poor approach: short wavedash, no safe move out of a dash, high-ish short hop for its
    size, aerials other than uair cannot auto-cancel in a short hop [wiki:Pikachu_(SSBM)].
  - Weak [shield pressure](../techniques/shield-pressure.md) [wiki:Pikachu_(SSBM)].
  - Light and easy to combo and chain grab; [Sheik](sheik.md) chain grabs it
    [wiki:Pikachu_(SSBM)].
  - Loses hard to disjoints ([Marth](marth.md)) [wiki:Pikachu_(SSBM)].

## Character tech

### Up air juggle

- **id:** `uair-juggle`
- **What:** Repeated uairs under an airborne opponent. The early hit sends almost straight
  up with high base and low scaling knockback, so it keeps the opponent just above
  Pikachu at a wide range of percents.
- **Inputs:** Jump (or full hop / double jump as height requires), uair so the first two
  active frames connect, land or double jump, repeat. Finish with usmash, nair, another
  uair's semi-spike part off stage, or down B (Thunder).
- **Timing:** Uair is active frames 3-8 in three parts: frames 3-4 send at angle 80 (base
  knockback 100, growth 60), frames 5-6 at angle 0 (base 60), frames 7-8 at angle 130
  (base 80); all deal 4% [fd] [wiki:Pikachu_(SSBM)/Up_aerial]. It can be interrupted from
  frame 28, auto-cancels on landing from frame 18, and otherwise has 26 frames of landing
  lag (13 with an [L-cancel](../techniques/l-cancel.md)) [wiki:Pikachu_(SSBM)/Up_aerial].
  It is the only Pikachu aerial that auto-cancels inside a short hop [wiki:Pikachu_(SSBM)].
- **Used for:** Damage on floaties (the wiki singles out [Jigglypuff](jigglypuff.md),
  who has few options below herself [wiki:Pikachu_(SSBM)/Up_aerial]) and on fastfallers
  after uthrow; setting up usmash or Thunder.
- **Common errors:** Hitting with frames 5-6 on stage by accident, which sends the
  opponent sideways out of the juggle; landing during the move without an L-cancel
  (26 frames of lag); chasing so high that the opponent falls past Pikachu.
- **Drill idea:** CPU launched upward above Pikachu at a set percent; count consecutive
  uairs that connect before the CPU lands or leaves hitstun.

### Up air tail spike

- **id:** `uair-tail-spike`
- **What:** Hitting with the middle (angle 0) or late (angle 130, behind Pikachu) part of
  uair to send a recovering opponent flat away from the stage or back under it, at any
  percent.
- **Inputs:** Off stage, jump toward the opponent and press uair so that the tail meets
  them on active frames 5-8 rather than 3-4. Facing matters: the tail sweeps from in front
  of Pikachu, over its head, to behind it.
- **Timing:** Mid part is frames 5-6 (angle 0, base 60, growth 60); late part is frames
  7-8 (angle 130, base 80) [fd]. Only 2 frames each, so spacing decides which part hits.
  The Melee Library links a video ("Explaining Pika Up Air") on these hitboxes
  [lib:Explaining Pika Up Air]; its content was not readable in this session.
- **Used for:** Gimping (killing at low percent by denying the recovery) characters with
  short or linear recoveries; the wiki says it edgeguards reliably even at low percents
  [wiki:Pikachu_(SSBM)/Up_aerial].
- **Common errors:** Hitting with frames 3-4, which pops the opponent upward and gives
  them their recovery back; hitting with the late part while facing the wrong way and
  sending them toward the stage.
- **Drill idea:** CPU recovers from off stage at low percent; success only if the CPU is
  hit by uair's angle-0 or angle-130 part and fails to return.

### Quick Attack angles

- **id:** `quick-attack-angles`
- **What:** Up B (Quick Attack) is one or two straight-line warps whose directions and
  lengths are chosen with the control stick. Controlling both gives Pikachu many recovery
  paths.
- **Inputs:** Up B, hold a direction before the first warp starts; during the first warp
  hold a second direction for the optional second warp. Tilting the stick less far gives
  a shorter warp. With no stick input the first warp goes up and Pikachu keeps its facing
  [wiki:Pikachu_(SSBM)].
- **Timing:** First warp's hitbox is frames 13-18, second is frames 27-31; the move is 68
  frames with one warp and 81 with two [wiki:Pikachu_(SSBM)/Up_special]. The second
  direction must differ from the first by at least 38 degrees, although a specific stick
  coordinate lets both warps go upward [wiki:Pikachu_(SSBM)]
  [lib:Quick Attack Upwards Twice]. There is no intangibility on startup
  [wiki:Quick_Attack]. Landing lag is 24 frames if Pikachu lands before entering free
  fall and 4 frames if it lands after [wiki:Pikachu_(SSBM)/Up_special].
- **Used for:** Recovery mixups (high to platform, straight to ledge, low then up, short
  warps to change timing, reversed and shortened warps [lib:Reverse + Shortened Up-b
  Recoveries]); occasionally movement on stage.
- **Common errors:** Second direction within 38 degrees of the first, so the second warp
  does not happen and Pikachu falls helpless; ending a warp on stage before free fall
  (24 frames of lag, easily punished); aiming slightly above the ledge and landing on
  stage in lag.
- **Drill idea:** Start Pikachu off stage at random positions with no double jump; success
  if it grabs the ledge or lands on a platform without being hit by a CPU waiting at the
  ledge.

### Quick Attack to ledge from stage

- **id:** `quick-attack-ledge-sweetspot`
- **What:** Using up B from on stage to warp to the ledge and grab it immediately, to
  edgehog (occupy the ledge so the opponent cannot grab it) faster than running off.
- **Inputs:** Near the edge, up B aimed down and away so the warp ends at the ledge
  facing the stage; many players use two warps (away, then back to the ledge).
- **Timing:** Unknown in frames. The wiki notes that a mistake leaves Pikachu helpless
  below the stage [wiki:Pikachu_(SSBM)]. Covered in the Melee Library by Axe's "Pikachu
  Tips and Tricks" and PikaChad's "Pikachu Up-B ledgehog tips/etc." [lib:Pikachu Tips and
  Tricks] (videos; titles and descriptions only).
- **Used for:** Edgehogging recoveries that must grab the ledge; refreshing ledge
  intangibility.
- **Common errors:** Self-destruct by missing the ledge; warping past it.
- **Drill idea:** Pikachu at a set distance from the edge, CPU recovering toward the
  ledge; success if Pikachu is hanging on the ledge within N frames of up B and the CPU
  fails to grab it.

### Up B momentum cancel

- **id:** `up-b-momentum-cancel`
- **What:** Quick Attack removes all knockback velocity partway through its startup, so
  using it as early as possible after a strong hit lets Pikachu survive hits that would
  otherwise carry it to the blast zone.
- **Inputs:** Up B on the first frame out of hitstun, then angle the warps back to the
  stage.
- **Timing:** Knockback momentum is cancelled on the 14th frame of up B
  [lib:Pikachu/Pichu Up-Special Momentum Cancel]. The wiki confirms Quick Attack is one of
  very few moves that stops knockback speed [wiki:Quick_Attack].
- **Used for:** Surviving horizontal kill moves at high percent.
- **Common errors:** Double jumping first (wastes the jump and delays the cancel);
  inputting up B while still in hitstun so nothing comes out.
- **Drill idea:** CPU hits Pikachu with a set horizontal kill move at a percent that kills
  without the cancel; success if Pikachu survives and returns to stage.

### Up throw chain grab

- **id:** `uthrow-chaingrab`
- **What:** Uthrow followed by a regrab before the opponent can act, repeated. Works on
  fastfallers (Fox, Falco, Captain Falcon).
- **Inputs:** Grab, uthrow, move under where the opponent's DI (directional influence,
  holding a direction to bend the launch angle) sends them, grab again (jump-cancelled
  grab if running). See [chain-grab](../techniques/chain-grab.md).
- **Timing:** Uthrow releases on frame 20 of a 43-frame animation; the throw is 5% + 5%,
  angle 90, base knockback 90, growth 45 [wiki:Pikachu_(SSBM)/Up_throw]. Standing grab is
  active frames 7-8 and dash grab frames 11-12 [wiki:Pikachu_(SSBM)/Grab] (the frame data
  dump lists them one frame earlier [fd]). Pikachu must reposition for the opponent's DI
  each time [wiki:Pikachu_(SSBM)/Up_throw]. Exact percent window: Unknown from sources
  read; commonly quoted as low to mid percents on Fox and Falco [unverified].
- **Used for:** Guaranteed damage on fastfallers from 0, ending in usmash or uair.
- **Common errors:** Grab whiffs because the grab box is tiny and the opponent DI'd to the
  side; regrabbing too late so the opponent jumps or shines out.
- **Drill idea:** CPU Fox at 0% grabbed at centre stage with random DI (none, left,
  right); count consecutive regrabs; fail when the CPU acts or lands.

### Up throw to up smash

- **id:** `uthrow-usmash`
- **What:** At kill percent on a fastfaller, uthrow directly into usmash.
- **Inputs:** Grab, uthrow, small step or turn to get under the DI, usmash (C-stick up).
- **Timing:** Usmash hits on frame 8; the clean hit (frames 8-10) does 19% close to
  Pikachu and 17% at the tail tip, angle 85, base 40, growth 110 (100 at the tip); frames
  11-13 do 13%; frames 14-17 do 7% at angle 40 with almost no knockback and are punishable
  even on hit [fd] [wiki:Pikachu_(SSBM)]. The wiki describes usmash as a follow-up to
  uthrow or dthrow depending on the opponent's fall speed and that uthrow sets up usmash
  at KO percentages [wiki:Pikachu_(SSBM)/Up_smash] [wiki:Pikachu_(SSBM)].
- **Used for:** Converting a grab into a stock.
- **Common errors:** Hitting with the late hit (weak, sends sideways); usmashing facing
  the wrong way so the tail's strong hit misses.
- **Drill idea:** CPU Fox at a kill percent in grab; success if usmash's clean hit connects
  and the CPU dies off the top.

### Jab reset

- **id:** `jab-reset`
- **What:** Jab an opponent who missed a tech and is lying on the ground to force the slow
  stand-up animation, then punish with a charged smash or grab.
- **Inputs:** Walk or dash to the downed opponent, jab once, then usmash or fsmash.
- **Timing:** Jab hits frames 2-3 for 2% at angle 0 with base knockback 7 and can be
  repeated quickly [fd] [wiki:Pikachu_(SSBM)]. In Melee a hit resets a downed opponent
  only if it does at most 7% and less than 80 units of knockback (no tumble); after the
  forced get-up the opponent is vulnerable for a further 30 frames, and a second reset
  must land within 12 frames of the first [wiki:Lock].
- **Used for:** Kill confirms after dthrow, late nair, Thunder Jolt or any missed tech.
- **Common errors:** Jabbing twice (second jab hits the standing opponent out of the
  reset); too slow, so the opponent rolls or stands.
- **Drill idea:** CPU lies in missed-tech state at mid percent; success if one jab
  connects and a smash attack hits during the forced get-up.

### Neutral air cross-up

- **id:** `nair-crossup`
- **What:** Short hop nair that drifts through or over the opponent's shield so Pikachu
  lands behind it, where shield grabs miss.
- **Inputs:** Dash, short hop, nair early, drift past the opponent,
  [fast fall](../techniques/fast-fall.md), L-cancel, then jab, grab, usmash or dsmash.
- **Timing:** Nair is active frames 3-28 (12% for frames 3-10, 9% after), with 15 frames
  of landing lag, 7 when L-cancelled [fd] [wiki:Pikachu_(SSBM)/Neutral_aerial]. Advantage
  on shield: Unknown from sources read.
- **Used for:** Pikachu's main way to open shields, since its grab is short and its
  pressure is weak [wiki:Pikachu_(SSBM)].
- **Common errors:** Landing in front of the shield and being shield grabbed; missing the
  L-cancel.
- **Drill idea:** CPU holds shield and shield grabs or does its fastest
  [out-of-shield](../techniques/out-of-shield.md) option after shieldstun; success if
  Pikachu's nair hits shield, Pikachu lands behind and is not hit.

### Thunder Jolt edgeguard

- **id:** `thunder-jolt-edgeguard`
- **What:** Neutral B travels along the ground, wraps around the ledge and down the stage
  wall, hitting opponents who recover low or hang on the ledge.
- **Inputs:** Neutral B on stage facing the edge, or in the air aimed so the ball lands
  near the edge.
- **Timing:** The projectile appears on frame 18 and lasts 100 frames; the user's
  animation is 57 frames [wiki:Pikachu_(SSBM)/Neutral_special]. Grounded jolt does 7%,
  the aerial ball 10% [wiki:Pikachu_(SSBM)].
- **Used for:** Forcing a recovering opponent to go high or take a hit that sets up an
  uair, dair or edgehog; covering approaches in neutral.
- **Common errors:** Throwing it at close range (57 frames is a long commitment).
- **Drill idea:** CPU recovers low to the ledge; success if a jolt hits the CPU below
  stage level and Pikachu follows with an aerial or edgehog that kills.

### Thunderspike

- **id:** `thunderspike`
- **What:** Launch the opponent upward (usually with usmash), then use down B (Thunder) so
  the descending bolt hits them near the top blast zone for an early kill.
- **Inputs:** Usmash, then immediately down B under the opponent.
- **Timing:** Thunder's bolt comes from a cloud at a fixed height above Pikachu, and the
  bolt does 10% [wiki:Thunder_(Pokémon)] [wiki:Pikachu_(SSBM)]. The wiki rates it weaker
  than in Smash 64 but still effective on floaty characters [wiki:Thunderspiking]. If the
  bolt reaches Pikachu it creates a shockwave: 17%, base knockback 100, growth 60 [fd].
- **Used for:** Finishing floaties who survive usmash; the shockwave is a strong but
  risky horizontal kill move.
- **Common errors:** Opponent DIs out from under the bolt; Thunder in the air without the
  bolt reaching Pikachu has very long end lag [wiki:Pikachu_(SSBM)].
- **Drill idea:** CPU floaty at mid percent standing over Pikachu's usmash; success if
  usmash then Thunder's bolt connects and the CPU dies off the top.

## Neutral game

- Goal: get close without running into a disjointed hitbox, then land nair, a grab,
  dtilt or usmash.
- Thunder Jolt from mid range covers the ground and makes the opponent jump or shield;
  Pikachu follows behind it.
- Short hop nair is the main approach and cross-up tool. Uair is the only aerial that
  auto-cancels in a short hop [wiki:Pikachu_(SSBM)].
- [Dash dance](../techniques/dash-dance.md) (dash speed is third best in the game
  [wiki:Pikachu_(SSBM)]) to bait a whiff, then punish with grab, usmash or nair.
- Ftilt is active frames 5-14 [fd] and is used to stop short-hop approaches and as an
  edgeguard poke [wiki:Pikachu_(SSBM)]. Dtilt (frames 7-9, interruptible from frame 19
  [fd]) is the safest grounded poke.
- Dsmash (first hit frame 7 [fd]) out of a [crouch cancel](../techniques/crouch-cancel.md)
  punishes weak approaches at low percent [wiki:Pikachu_(SSBM)].
- Avoid dash attack and grounded Skull Bash: both are laggy and easy to shield grab
  [wiki:Pikachu_(SSBM)].

## Punish game

Pikachu's punishes are short strings into a finisher rather than long true combos. On
fastfallers, a grab leads to uthrow chain grabs, uair juggles and usmash. On floaties,
uair juggles lead to more uairs, usmash or Thunder. Anything that knocks down leads to a
tech chase or a jab reset into usmash. Near the edge, bthrow or a semi-spike uair starts
an edgeguard.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| uthrow | fastfallers | low to mid, typical | regrab, repeat | Reposition for DI each time | [wiki:Pikachu_(SSBM)/Up_throw] |
| uthrow | fastfallers | KO percents | usmash | Clean hit only | [wiki:Pikachu_(SSBM)] |
| uthrow | fastfallers | above chain grab range, typical | uair juggle | Then usmash or nair | [wiki:Pikachu_(SSBM)] |
| dthrow | lightweights such as Jigglypuff | low | usmash | DI'd more easily than uthrow | [wiki:Pikachu_(SSBM)] |
| uair (frames 3-4) | floaties | any, typical | uair, usmash, Thunder | Juggle | [wiki:Pikachu_(SSBM)/Up_aerial] |
| usmash | fastfallers | low | usmash again, uair | "Juggles fastfallers at lower percentages" | [wiki:Pikachu_(SSBM)/Up_smash] |
| dsmash (final hit, angle 70) | most | low | aerial | Opponents can SDI out of the early hits | [wiki:Pikachu_(SSBM)] |
| Thunder Jolt | most | any | dash grab, nair, usmash | Low knockback with useful hitstun | [wiki:Pikachu_(SSBM)] |
| missed tech | all | any percent where jab stays under 80 knockback | jab reset then usmash / fsmash | 30 vulnerable frames after the forced get-up | [wiki:Lock] |
| bthrow near edge | all | any | edgeguard with uair, dair, Thunder Jolt | Pikachu rolls backward before releasing | [wiki:Pikachu_(SSBM)/Back_throw] |

### Chain grabs and tech chases

- **Uthrow chain grab on fastfallers** ([Fox](fox.md), [Falco](falco.md),
  [Captain Falcon](captain-falcon.md)): works from low percent; Pikachu must follow the
  DI [wiki:Pikachu_(SSBM)/Up_throw]. Exact end percent is Unknown from the sources read;
  the Melee Library has a video guide [lib:Pikachu Melee Chaingrab Guide] that could not
  be watched. DI to either side at higher percent and shine or jump once hitstun ends are
  the escapes [unverified].
- **Usmash tech chase:** the wiki describes usmash as "a powerful tech chasing tool at all
  percentages", leading to more usmashes on fastfallers at low percent and kills later
  [wiki:Pikachu_(SSBM)]. See [tech-chase](../techniques/tech-chase.md).
- **Jab resets** after dthrow or any knockdown [wiki:Pikachu_(SSBM)].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| usmash (clean, frames 8-10) | fastfallers and mid weights | roughly 90-110% | No DI data read; lower on low ceilings (Yoshi's Story) | [unverified] |
| usmash (clean) | floaties and lightweights | roughly 70-90% uncharged; fully charged kills light characters on low ceilings from about 35-55% | Charged figure is from the wiki | [wiki:Pikachu_(SSBM)] [unverified] |
| fsmash (early hit, frames 16-18, 21%) | all | roughly 90-120% near the edge | Disjointed; slow start | [fd] [unverified] |
| Thunder shockwave (17%) | all | Unknown | Bolt must reach Pikachu; rarely lands raw | [fd] |
| Thunder bolt (thunderspike) | floaties | Unknown; earlier than usmash alone | After usmash near the top | [wiki:Thunderspiking] |
| uair semi-spike | poor recoveries | any (gimp) | Off stage | [wiki:Pikachu_(SSBM)/Up_aerial] |
| dair (12%) | all | Unknown | Off stage, decent horizontal knockback | [wiki:Pikachu_(SSBM)] |
| nair (clean 12%) | all | high percent only | Off stage | [fd] |
| Skull Bash (charged, up to 29%) | all | Unknown | Rarely lands | [wiki:Pikachu_(SSBM)] |

- Dsmash does not kill "well past 150%" [wiki:Pikachu_(SSBM)/Down_smash].
- Kill setups: uthrow to usmash on fastfallers; jab reset to usmash; uair juggle to
  usmash; usmash to Thunder on floaties.
- Edgeguards: bthrow puts the opponent off stage at any percent; then uair (angle-0 or
  angle-130 part), dair, ftilt/dtilt at the ledge, fsmash (disjointed), Thunder Jolt
  down the wall, or edgehog via Quick Attack [wiki:Pikachu_(SSBM)]. Pikachu can go very
  deep and still return. A Reddit GIF guide to Pikachu gimps is linked in the Melee
  Library [lib:Pseudo-Guide to Pikachu Gimps/edgeguards in Gif Format] but was not
  reachable.

## Recovery

- **Options:**
  - Up B (Quick Attack): two fast straight warps in chosen directions; weak hitboxes (3%
    then 2%); no intangibility [wiki:Pikachu_(SSBM)/Up_special] [wiki:Quick_Attack].
    Cancels knockback momentum on frame 14 [lib:Pikachu/Pichu Up-Special Momentum Cancel].
  - Side B (Skull Bash): horizontal distance that grows with charge; 4% uncharged up to
    29%; maximum charge 91 frames from a tilt input, and a smash input starts with 20
    frames of charge [wiki:Pikachu_(SSBM)/Side_special]. Leaves Pikachu helpless
    [unverified]; landing lag 45 frames [wiki:Pikachu_(SSBM)/Side_special].
  - Double jump (height 29.44 units [wiki:Pikachu_(SSBM)]).
  - No [wall jump](../techniques/wall-jump.md): Pikachu is not on the wiki's Melee
    wall-jump list (it gained one in Brawl; [Pichu](pichu.md) has one) [wiki:Wall_jump].
- **Mixups:** first warp up then second to ledge or platform; first warp horizontal then
  down to the ledge; a single warp; shortened warps by partial stick tilt; double-up warp
  [lib:Quick Attack Upwards Twice]; Skull Bash first to get distance, then double jump and
  up B; landing on stage after free fall begins costs only 4 frames of lag
  [wiki:Pikachu_(SSBM)/Up_special].
- **Weaknesses:** no intangibility and brief pauses at the start, between warps and at the
  end [wiki:Quick_Attack]; ending a warp on stage before free fall costs 24 frames; the
  ledge snap is not generous, so recovering from above is weaker than in Smash 64
  [wiki:Quick_Attack]; a second direction within 38 degrees fails.

### Edgeguarding Pikachu

The wiki states that most characters cannot cover all of Pikachu's recovery paths by
reaction and must read [wiki:Pikachu_(SSBM)]. Practical coverage:

- Hit Pikachu before or during up B startup (it has no intangibility) with a lingering
  aerial; frames 1-12 of up B are stationary startup [wiki:Pikachu_(SSBM)/Up_special].
- Hold the ledge to force Pikachu onto the stage, then punish the landing: 24 frames of
  lag if it lands before free fall, 4 if after.
- Cover the gap between the two warps (about frames 19-26, when there is no hitbox and
  Pikachu is not yet moving again [wiki:Pikachu_(SSBM)/Up_special]).
- Skull Bash is slow and linear: intercept it or edgehog.
- A realistic CPU Pikachu should randomise between: straight to ledge, high to platform,
  short warp then ledge, and Skull Bash plus up B from far away.

## Defense and out of shield

- Out of shield: usmash out of shield (jump-cancelled; hits frame 8 after the jump squat
  is cancelled [fd]) is the main punish and a kill move; nair out of shield (jump squat 3
  [wiki:Pikachu_(SSBM)], nair active on frame 3 [fd]) is the fastest aerial; shield grab
  is weak because the grab is the shortest in the game. Quick Attack is not an
  invincible out-of-shield option in Melee [wiki:Quick_Attack].
- [Crouch cancel](../techniques/crouch-cancel.md) into dsmash or dtilt works at low
  percent; Pikachu is light (weight 80), so it stops working earlier than for heavy
  characters.
- Combo escapes: nair (frame 3), double jump, up B (also cancels momentum). Tech in place
  is unusually safe (2 vulnerable frames [wiki:Tech]).
- Shield is rarely poked because Pikachu is small [wiki:Pikachu_(SSBM)].

## As the training dummy

- Weight 80 (20th-21st of 26), fall speed 1.9 (medium), fast-fall speed 2.7, gravity
  0.11, jump squat 3 frames [wiki:Pikachu_(SSBM)]. Light, mid fall speed: launched far
  and comboed.
- Chain grabbed by [Sheik](sheik.md) with dthrow, from 0% to about 40% in NTSC with
  perfect regrabs and DI [wiki:Pikachu_(SSBM)]. Vulnerable to
  [Captain Falcon](captain-falcon.md)'s dthrow follow-ups [wiki:Pikachu_(SSBM)].
- Good CPU choices: tech in place often (2 vulnerable frames instead of 6 [wiki:Tech]);
  DI away from combo starters; survival DI plus immediate up B on horizontal kill moves
  (momentum cancel on frame 14).
- Short tether range needed: Pikachu is small and crouches low; some high moves miss
  [unverified].
- Thresholds (crouch cancel limits, knockdown percents): Unknown from sources read.

## Matchup notes

### vs Marth

The wiki names [Marth](marth.md) as the clearest problem matchup because of disjointed
range [wiki:Pikachu_(SSBM)]. Pikachu has to get inside the sword with Thunder Jolt cover
and cross-ups; Marth's recovery is linear and is a good target for uair semi-spikes and
dair.

### vs Sheik

The wiki calls [Sheik](sheik.md) Pikachu's hardest top-tier matchup: dthrow chain grab
from 0% to about 40% in NTSC [wiki:Pikachu_(SSBM)], and her tilts outrange Pikachu. Pikachu
needs to avoid grabs and edgeguard Sheik's up B.

### vs Fox and Falco

Fastfallers are where the punish game is strongest: uthrow chain grab, uair juggles,
usmash kills, and both have recoveries that uair, dair and Thunder Jolt gimp. Axe's
matchup guides for Fox and Falco are linked in the Melee Library [lib:Pikachu Matchup
Guides] but were not reachable. Falco's lasers make approaching harder.

### vs Jigglypuff

Uair juggles are the key tool because [Jigglypuff](jigglypuff.md) is floaty and has
little to attack below herself; dthrow to usmash can kill her early
[wiki:Pikachu_(SSBM)/Up_aerial] [wiki:Pikachu_(SSBM)].

### vs Captain Falcon

Falcon's dthrow follow-ups are dangerous for Pikachu [wiki:Pikachu_(SSBM)]. In return
Falcon is chain grabbed and his recovery is easy to gimp with uair.

## Drill seeds

### Up air juggle count

- **id:** `pikachu-uair-juggle`
- **Goal:** Keep an opponent in the air with repeated clean uairs and end with usmash.
- **Player:** Pikachu
- **CPU:** Jigglypuff, Peach, Fox, Falco
- **Setup:** Final Destination. CPU starts airborne a short hop above Pikachu at centre
  stage, in hitstun from a simulated uthrow, at a chosen percent.
- **CPU behaviour:** Random DI (left, right, none); when out of hitstun it double jumps
  away or attacks downward.
- **Success:** At least N uairs (start with 3) connect with the frame 3-4 part, followed
  by a usmash clean hit, before the CPU touches the ground.
- **Fail:** CPU lands, acts, or is hit by the angle-0 part and leaves range.
- **Variations:** Percent 0-80%; fastfaller vs floaty; require finishing with Thunder on
  floaties.
- **Data needed:** Uair hit windows and angles per part, landing lag 26/13, usmash frame
  8, CPU fall speed and weight.

### Tail spike edgeguard

- **id:** `pikachu-uair-gimp`
- **Goal:** Hit a recovering opponent with the semi-spike part of uair.
- **Player:** Pikachu
- **CPU:** Marth, Captain Falcon, Fox, Falco, Sheik
- **Setup:** Battlefield or Yoshi's Story. CPU starts off stage at ledge height or below
  with its double jump used, at 20-60%. Pikachu stands at the edge.
- **CPU behaviour:** Recovers with up B or side B, randomising timing and height.
- **Success:** CPU is hit by uair frames 5-8 (angle 0 or 130) and loses its stock; Pikachu
  returns to the stage.
- **Fail:** CPU grabs ledge or lands; Pikachu hits with frames 3-4; Pikachu dies.
- **Variations:** Start from a bthrow at the edge; add dair and Thunder Jolt as allowed
  finishers; lower percent.
- **Data needed:** Uair part timings and angles, CPU recovery move frame data, Quick
  Attack distances.

### Up throw chain grab on Fox

- **id:** `pikachu-uthrow-chaingrab`
- **Goal:** Regrab after uthrow against every DI and end with usmash.
- **Player:** Pikachu
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** Final Destination centre, CPU at 0%, Pikachu already holding the grab.
- **CPU behaviour:** Random DI on each throw (left, right, none, slight); once out of
  hitstun, jumps or shines.
- **Success:** N consecutive regrabs (start with 3) and a finishing usmash or uair that
  connects.
- **Fail:** CPU acts before the regrab or the grab whiffs.
- **Variations:** Start percent 0-50%; near edge; require uthrow-usmash at a kill percent.
- **Data needed:** Uthrow release frame 20 and total 43, knockback values, grab frames,
  CPU weight and fall speed.

### Jab reset to up smash

- **id:** `pikachu-jab-reset-usmash`
- **Goal:** React to a missed tech with a single jab and a kill move.
- **Player:** Pikachu
- **CPU:** Any; most useful against Fox, Falco, Sheik, Marth
- **Setup:** CPU at 80-110% knocked down in front of Pikachu at a short dash distance.
- **CPU behaviour:** Randomly techs in place, techs away, techs toward, or misses the
  tech and lies for a random time before a get-up option.
- **Success:** On a missed tech: exactly one jab connects on the lying CPU and a smash
  attack hits during the reset. On a tech: Pikachu punishes with usmash or grab.
- **Fail:** CPU gets up unpunished; two jabs; Pikachu is hit.
- **Variations:** Start from Pikachu's dthrow; platform knockdowns.
- **Data needed:** Jab frame 2 and total 21, usmash frame 8, CPU tech and get-up
  timings.

### Recovery mixups against a ledge guard

- **id:** `pikachu-recovery-mixup`
- **Goal:** Recover with Quick Attack without being hit, using different paths.
- **Player:** Pikachu
- **CPU:** Marth, Sheik, Fox, Peach
- **Setup:** Pikachu starts in tumble off stage at varying distance and height with or
  without its double jump, at 60-120%.
- **CPU behaviour:** Randomly holds ledge, waits at the edge with a tilt or smash, or
  jumps out with an aerial.
- **Success:** Pikachu reaches the ledge or the stage and is not hit for the next 60
  frames.
- **Fail:** Pikachu is hit, self-destructs, or lands with 24 frames of lag and is
  punished.
- **Variations:** Force no double jump; require a two-warp path; require a shortened
  warp.
- **Data needed:** Quick Attack warp distances per stick magnitude, 38-degree rule,
  landing lag 24 vs 4.

### Momentum cancel survival

- **id:** `pikachu-up-b-momentum-cancel`
- **Goal:** Use up B on the first actionable frame after a kill move to survive.
- **Player:** Pikachu
- **CPU:** Marth (fsmash), Fox (bair), Sheik (fair)
- **Setup:** Pikachu near the edge at a percent where the CPU's move kills with good DI
  but no momentum cancel.
- **CPU behaviour:** Hits Pikachu with the chosen move.
- **Success:** Pikachu survives and returns to the stage.
- **Fail:** Pikachu crosses the blast zone.
- **Variations:** Different moves and percents; with and without double jump.
- **Data needed:** Hitstun length for the launch, cancel on frame 14 of up B, blast zone
  positions.

### Neutral air cross-up on shield

- **id:** `pikachu-nair-crossup`
- **Goal:** Hit a shield with nair, land behind it and stay safe.
- **Player:** Pikachu
- **CPU:** Marth, Sheik, Fox, Peach
- **Setup:** CPU shielding at centre stage; Pikachu at dash distance.
- **CPU behaviour:** After shieldstun randomly shield grabs, does its fastest
  out-of-shield attack, or rolls.
- **Success:** Nair hits shield, Pikachu lands behind the CPU with an L-cancel and is not
  hit; bonus for landing a follow-up grab or usmash.
- **Fail:** Pikachu is grabbed or hit.
- **Variations:** CPU reacts with up B out of shield (Samus, Marth); CPU drops shield
  and dash dances.
- **Data needed:** Nair hit windows and landing lag 15/7, shieldstun for 12% and 9%, CPU
  out-of-shield frame data.

### Quick Attack edgehog

- **id:** `pikachu-quick-attack-edgehog`
- **Goal:** Take the ledge from on stage with up B fast enough to deny a recovery.
- **Player:** Pikachu
- **CPU:** Fox, Falco, Marth, Captain Falcon
- **Setup:** Pikachu at a fixed distance from the edge facing it; CPU launched off stage
  and recovering to the ledge.
- **CPU behaviour:** Recovers aiming at the ledge.
- **Success:** Pikachu is hanging on the ledge when the CPU arrives and the CPU dies.
- **Fail:** Pikachu self-destructs, lands on stage, or the CPU grabs the ledge.
- **Variations:** Different start distances; require a ledge roll or get-up to cover a
  CPU that lands on stage.
- **Data needed:** Quick Attack warp length and timing, ledge grab boxes, CPU recovery
  timing.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlPk.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/pikachu.json`](../framedata/pikachu.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 2-3 | 2 | 0 | 7 | 50 | - |  | 21 | - | 2 | -17 |  |
| Dash attack | `dash_attack` | 5-16 | 8 | Sakurai | 40 | 70 | - |  | 49 | - | 5 | -39 |  |
| Forward tilt (angled up) | `ftilt_high` | 5-14 | 9 | Sakurai | 10 | 100 | - |  | 29 | - | 6 | -18 |  |
| Forward tilt | `ftilt` | 5-14 | 8 | Sakurai | 10 | 100 | - |  | 29 | - | 5 | -19 |  |
| Forward tilt (angled down) | `ftilt_low` | 5-14 | 7 | Sakurai | 10 | 100 | - |  | 29 | - | 5 | -19 |  |
| Up tilt | `utilt` | 7-14 | 7/6 | 96/88 | 40/45 | 124 | - |  | 23 | - | 5 | -11 |  |
| Down tilt | `dtilt` | 7-9 | 7 | 35 | 12 | 100 | - |  | 21 | 19 | 5 | -6 |  |
| Forward smash | `fsmash` | 16-18 | 21 | Sakurai | 25 | 92 | - | electric | 49 | - | 11 | -22 | charge hold frame 14 |
|  |  | 19-21 | 19 | Sakurai | 25 | 95/90 | - | electric |  |  | 10 | -20 |  |
|  |  | 22-23 | 18 | Sakurai | 22 | 95/90/85 | - | electric |  |  | 10 | -17 |  |
| Up smash | `usmash` | 8-10 | 19/18/17 | 85 | 40 | 110/100 | - |  | 43 | 41 | 10 | -22 | charge hold frame 5 |
|  |  | 11-13 | 13 | 90 | 30 | 110 | - |  |  |  | 7 | -22 |  |
|  |  | 14-17 | 7 | 40 | 5 | 48 | - |  |  |  | 5 | -21 |  |
| Down smash | `dsmash` | 7-8, 10-11, 13-14, 16-17, 19-20, 22-23 | 2 | 170/90 | 70/30 | 30 | - | electric | 54 | 51 | 2 | -41 | charge hold frame 5 |
|  |  | 25 | 3 | 70 | 70 | 170 | - | electric |  |  | 3 | -22 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 3-10 | 12 | Sakurai | 18 | 100 | - |  | 39 | - | 7 | 15 | 7 | <3, >34 | +0 |  |
|  |  | 11-28 | 9 | Sakurai | 0 | 100 | - |  |  |  | 6 |  |  |  | -1 |  |
| Forward air | `fair` | 10-12, 14-16, 18-20, 22-24 | 2 | Sakurai | 0 | 100 | 30 | electric | 39 | - | 2 | 20 | 10 | <10, >33 | -8 |  |
| Back air | `bair` | 4-7 | 12 | Sakurai | 20 | 100 | - |  | 59 | - | 7 | 30 | 15 | <4, >49 | -8 |  |
|  |  | 8-37 | 9 | Sakurai | 20 | 100 | - |  |  |  | 6 |  |  |  | -9 |  |
| Up air | `uair` | 3-4 | 4 | 80 | 100 | 60 | - |  | 27 | - | 3 | 26 | 13 | <3, >17 | -10 |  |
|  |  | 5-6 | 4 | 0 | 60 | 60 | - |  |  |  | 3 |  |  |  | -10 |  |
|  |  | 7-8 | 4 | 130 | 80 | 60 | - |  |  |  | 3 |  |  |  | -10 |  |
| Down air | `dair` | 14-26 | 12 | Sakurai | 20 | 100 | - | electric | 57 | 48 | 7 | 40 | 20 | <1, >38 | -13 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 11-12 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 3 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 10 | 2 | 45 | 45 | 110 | - | electric | 29 | 43 |  |
| Back throw | `bthrow` | 9 | 9 | 135 | 75 | 50 | - | electric | 30 | 49 |  |
| Up throw | `uthrow` | 10 | 5 | 90 | 90 | 45 | - | electric | 20 | 43 |  |
| Down throw | `dthrow` | 10 | 5 | 80 | 60 | 38 | - | electric | 20 | 47 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Thunder Jolt, ground | `special_n` | - | - | - | - | - | - | - | 57 | - | - | - |  |
| Neutral B: Thunder Jolt, air | `special_air_n` | - | - | - | - | - | - | - | 57 | - | - | - |  |
| Side B: Skull Bash, ground, Start | `special_s_start` | - | - | - | - | - | - | - | 13 | - | - | - |  |
| Side B: Skull Bash, ground, Hold | `special_s_hold` | - | - | - | - | - | - | - | 5 | - | - | - |  |
| Side B: Skull Bash, ground | `special_s` | 4-29 | 4 | Sakurai | 15 | 90 | - | electric | 39 | - | 3 | - |  |
| Side B: Skull Bash, ground | `special_s_300` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Side B: Skull Bash, ground, End | `special_s_end` | - | - | - | - | - | - | - | 44 | - | - | - |  |
| Side B: Skull Bash, air, Start | `special_air_s_start` | - | - | - | - | - | - | - | 13 | - | - | - |  |
| Side B: Skull Bash, air, Hold | `special_air_s_hold` | - | - | - | - | - | - | - | 5 | - | - | - |  |
| Side B: Skull Bash, ground | `special_s_304` | 4-29 | 4 | Sakurai | 15 | 90 | - | electric | 39 | - | 3 | - |  |
| Side B: Skull Bash, air, End | `special_air_s_end` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Up B: Quick Attack, ground, Start | `special_hi_start` | 13 | 3 | 0 | 5 | 40 | - | electric | 13 | - | 3 | - |  |
| Up B: Quick Attack, ground, Start | `special_hi_start_307` | 13 | 2 | 0 | 5 | 40 | - | electric | 13 | - | 2 | - |  |
| Up B: Quick Attack, ground, End | `special_hi_end` | - | - | - | - | - | - | - | 49 | - | - | - |  |
| Up B: Quick Attack, air, Start | `special_air_hi_start` | 13 | 3 | 0 | 5 | 40 | - | electric | 13 | - | 3 | - |  |
| Up B: Quick Attack, air, Start | `special_air_hi_start_310` | 13 | 2 | 0 | 5 | 40 | - | electric | 13 | - | 2 | - |  |
| Up B: Quick Attack, air, End | `special_air_hi_end` | - | - | - | - | - | - | - | 49 | - | - | - |  |
| Down B: Thunder, ground, Start | `special_lw_start` | - | - | - | - | - | - | - | 17 | - | - | - |  |
| Down B: Thunder, ground, Loop | `special_lw_loop` | - | - | - | - | - | - | - | 9 | - | - | - | spawns article/projectile on 3 |
| Down B: Thunder, ground, Loop | `special_lw_loop_314` | 1-9 | 17 | Sakurai | 100 | 60 | - | electric | 9 | - | 9 | - |  |
| Down B: Thunder, ground, End | `special_lw_end` | - | - | - | - | - | - | - | 35 | - | - | - |  |
| Down B: Thunder, air, Start | `special_air_lw_start` | - | - | - | - | - | - | - | 17 | - | - | - |  |
| Down B: Thunder, air, Loop | `special_air_lw_loop` | - | - | - | - | - | - | - | 9 | - | - | - | spawns article/projectile on 3 |
| Down B: Thunder, air, Loop | `special_air_lw_loop_318` | 1-9 | 17 | Sakurai | 100 | 60 | - | electric | 9 | - | 9 | - |  |
| Down B: Thunder, air, End | `special_air_lw_end` | - | - | - | - | - | - | - | 35 | - | - | - |  |

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
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-19 | 13-14, 18-19 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-14 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-19 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-24 | 17-18, 23-24 (6%) | 50 | - |  |
| Getup roll forward (face down) | `getup_roll_forward_facedown` | intangible 1-19 | - | 36 | - |  |
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-19 | - | 35 | - |  |
| Tech in place | `tech_in_place` | intangible 2-24 | - | 26 | - | starts 1 frame late (included) |
| Tech roll forward | `tech_roll_forward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Tech roll backward | `tech_roll_backward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Wall tech | `wall_tech` | - | - | 26 | - | starts 1 frame late (included) |
| Wall tech jump | `wall_tech_jump` | - | - | 40 | - | starts 1 frame late (included) |
| Ceiling tech | `ceiling_tech` | intangible 2-13 | - | 26 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-55 | - | 59 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 32 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-50 | 54-59 (6%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-18 | 22-24 (8%) | 53 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-70 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-24 | - | 49 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-26 | - | 26 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 27 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-15 | - | 15 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 27 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Neutral air | jump | 6 | `nair` |
| Up air | jump | 6 | `uair` |
| Back air | jump | 7 | `bair` |
| Shield grab | direct | 7 | `grab` |
| Up smash | jump cancel | 9 | `usmash` |
| Forward air | jump | 13 | `fair` |
| Up B | jump cancel | 14 | `special_hi_start` |
| Down air | jump | 17 | `dair` |
| Spot dodge | direct | intangible 2-15 of 22 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 15 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Pikachu indexed by [The Melee Library](https://www.meleelibrary.com/#pikachu) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [Are You a Pikachu Player?](https://youtu.be/xWJzd8Zx7OA?t=30) | SSBM Tutorials | They give an overview of Pikachu the character to give you an idea of whether you would like to play him. |
| [2020 Pikachu Melee Techs Guide](https://www.youtube.com/watch?v=ZNru1MFwwpY&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=20&t=0s) | Third Chair | Video guide on performing useful Pikachu tech in 2020. |
| [Pikachu Guide 2011](http://smashboards.com/threads/pikachu-guide-2011.312544/) | N64 |  |
| [Ask about Pikachu! Hosted by Axe and N64! feat. dkuo!](http://smashboards.com/threads/ask-about-pikachu-hosted-by-axe-and-n64-feat-dkuo.240209/) | community | A discussion thread. Search and learn. |
| [Pikachu Info Dump](http://smashboards.com/threads/pikachu-information-dump.311185/) | Soju | Collection of informative things said by top level Pikachu players. |
| [Pika’s Matchups](http://smashboards.com/threads/pikas-matchups.68694/) | N64 | N64 writes about his thoughts on matchups. Lots of old info with a few updates for modern meta. |
| [Pikachu Hitboxes and Frame Data](http://smashboards.com/threads/pikachu-hitboxes-and-frame-data.320088/) | Stratocaster, Standardtoaster, and SuperDoodleMan |  |
| [Explaining Pika Up Air](https://www.youtube.com/watch?v=vEGJKphlc3U) | PikaChad | Pikachu’s uair has lots of weird hitboxes. This is how they work. |
| [Slightly Better Edge Invincibility Refresh](http://smashboards.com/threads/slightly-better-edge-invincibility-refresh.402755/) | Mittenz |  |
| [Pikachu Up-B ledgehog tips/etc.](https://www.youtube.com/watch?v=L9YOGo6E5C4) | PikaChad |  |
| [Pikachu Tutorial](http://www.twitch.tv/pikachad/c/4081228) | N64 and PikaChad |  |
| [Pseudo-Guide to Pikachu Gimps/edgeguards in Gif Format](https://www.reddit.com/r/SSBM/comments/3abbkj/pseudoguide_to_pikachu_gimpsedgeguards_in_gif/) | Mylox |  |
| [Pikachu Aerial Interrupt on Battlefield](http://smashboards.com/threads/pikachu-aerial-interrupt-on-battlefield-fastest-way-possible-to-get-to-side-platforms.424316/) | community |  |
| [Pikachu’s Intangible Ledgedash Options](https://www.youtube.com/watch?v=dErTf-38oYY) | Practical TAS |  |
| [Thunder Jolt Glitch Setup](https://www.youtube.com/watch?v=W6Axu_tocoY&feature=youtu.be) | Zappdos |  |
| [Pikachu Matchup Guides](http://smashboards.com/threads/axes-pikachu-matchup-guides-starting-with-fox.431741/) | Axe | Up to date match up information by the best Pikachu player in the world. At the time of posting this, only Fox and Falco are completed. |
| [Quick Attack Upwards Twice](https://smashboards.com/threads/new-technique-quick-attack-upwards-twice.273075/) | Axe |  |
| [Reverse + Shortened Up-b Recoveries](https://smashboards.com/threads/reverse-shortened-up-b-recoveries-video-included.273278/#post-10146397) | Axe |  |
| [Pikachu/Pichu Up-Special Momentum Cancel](https://www.youtube.com/watch?v=ohSzm1S7fsM) | BandDGames | Pikachu's and Pichu's up-b cancels all knockback momentum on the 14th frame. |
| [Pikachu Tips and Tricks](https://www.youtube.com/watch?v=qKeNxleydC0) | Axe | Axe discusses quick attack sweetspots to the ledge from the stage, moonwalking, and aerial interrupts. |
| [Pikachu Melee Chaingrab Guide](https://www.youtube.com/watch?v=A8efmqQrInw&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=9&t=0s) | Third Chair |  |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Pikachu (SSBM): https://www.ssbwiki.com/Pikachu_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Pikachu_(SSBM)/Up_aerial ,
  /Up_smash , /Up_special , /Up_throw , /Down_throw , /Back_throw , /Grab ,
  /Neutral_aerial , /Neutral_special , /Side_special , /Down_smash , /Forward_smash
- SSBWiki, Quick Attack: https://www.ssbwiki.com/Quick_Attack
- SSBWiki, Skull Bash: https://www.ssbwiki.com/Skull_Bash
- SSBWiki, Thunder (Pokémon): https://www.ssbwiki.com/Thunder_(Pokémon)
- SSBWiki, Thunder Jolt: https://www.ssbwiki.com/Thunder_Jolt
- SSBWiki, Thunderspiking: https://www.ssbwiki.com/Thunderspiking
- SSBWiki, Tech: https://www.ssbwiki.com/Tech
- SSBWiki, Wall jump: https://www.ssbwiki.com/Wall_jump
- SSBWiki, Lock (jab reset): https://www.ssbwiki.com/Lock
- SSBWiki, Chain grab: https://www.ssbwiki.com/Chain_grab
- SSBWiki, List of SSBM tier lists (NTSC): https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Melee Library, Pikachu section (card titles and descriptions only; the Smashboards and
  Reddit links returned errors and the videos cannot be watched).
- Frame data dump: `Pikachu.json`.
