---
schema: melee-character/v1
id: ganondorf
name: Ganondorf
aliases: [Ganon, The Dark Lord]
tier: "C+ (14th of 26), 2021 tier list"
archetype: [heavy, punish-heavy, edgeguarder, tech-chase, chaingrab, combo-food]
related: [captain-falcon]
summary: Ganondorf walls the opponent out with back air, forward air, jab and forward tilt, then turns one hit, grab or tech-chase read into a kill with the strongest aerials in the game and a reverse up air or stomp edgeguard.
key_tech: [reverse-up-air-edgeguard, dthrow-chain-grab, dthrow-tech-chase, autocancel-bair-wall, jab-knockdown, up-angled-ftilt-anti-air, stomp-conversion, first-hit-nair-juggle, wizards-foot-jump-restore, wizards-foot-spike, ledgehop-stall-and-ledge-options, lightshield-edgehog, cc-getup-attack-punish]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlGn.dat
framedata: ../framedata/ganondorf.json
code: src/melee/ft/kinds/ftGanon
specials:
  neutral_b: "Warlock Punch"
  side_b: "Gerudo Dragon"
  up_b: "Dark Dive"
  down_b: "Wizard's Foot"
attributes:
  weight: 109
  gravity: 0.13
  fall_speed: 2
  fast_fall_speed: 2.6
  jump_squat: 6
  jumps: 2
  walk_speed: 0.73
  dash_speed: 1.3
  run_speed: 1.35
  traction: 0.07
  air_speed: 0.78
  landing_lag: 5
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [3, 19, 8]
  jab2: [null, 32, 0]
  dash_attack: [7, 38, 14]
  ftilt_high: [9, 30, 14]
  ftilt_mid_high: [9, 30, 14]
  ftilt: [9, 30, 13]
  ftilt_mid_low: [9, 30, 12]
  ftilt_low: [9, 30, 12]
  utilt: [81, 113, 27]
  dtilt: [10, 35, 12]
  fsmash_high: [20, 60, 24]
  fsmash: [20, 60, 22]
  fsmash_low: [20, 60, 20]
  usmash: [21, 40, 22]
  dsmash: [19, 47, 14]
  nair: [7, 45, 12]
  fair: [14, 35, 17]
  bair: [10, 29, 16]
  uair: [6, 30, 13]
  dair: [16, 38, 22]
  grab: [7, 31, 0]
  dash_grab: [11, 41, 0]
  pummel: [5, 25, 3]
  fthrow: [11, 40, 4]
  bthrow: [12, 50, 4]
  uthrow: [11, 44, 3]
  dthrow: [null, 40, 7]
  special_n: [70, 117, 34]
  special_air_n: [70, 117, 34]
  special_s_start: [15, 80, 0]
  special_s: [3, 25, 17]
  special_air_s_start: [18, 80, 0]
  special_air_s: [3, 45, 16]
  special_hi: [13, 65, 1]
  special_air_hi: [13, 65, 1]
  special_hi_catch: [4, 16, 1]
  special_hi_throw: [null, 60, 15]
  special_lw: [14, 40, 15]
  special_lw_end: [null, 30, 0]
  special_air_lw: [15, 30, 14]
  special_air_lw_end: [2, 45, 12]
  special_lw_end_air: [null, 30, 0]
  special_air_lw_end_air: [null, 29, 0]
  special_hi_throw_317: [null, 60, 0]
oos:  # option: frame the hitbox is out
  grab: 7
  uair: 12
  nair: 13
  special_hi: 14
  bair: 16
  fair: 20
  dair: 22
  usmash: 22
resources: 15
# generated: end
---

# Ganondorf

<!-- GENERATED:attributes -->
## Attributes

Read from `PlGn.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 109 |
| Gravity | 0.13 |
| Terminal fall speed | 2 |
| Fast-fall speed | 2.6 |
| Jump squat (frames before airborne) | 6 |
| Full hop / short hop initial Y speed | 2.6 / 2 |
| Air jump Y multiplier | 0.95 |
| Jumps | 2 |
| Walk max speed | 0.73 |
| Dash initial speed / run max speed | 1.3 / 1.35 |
| Ground friction (traction) | 0.07 |
| Air max horizontal speed | 0.78 |
| Air acceleration (base + stick) | 0.02 + 0.04 |
| Air friction | 0.02 |
| Normal landing lag | 5 |
| Shield size | 15 |
<!-- /GENERATED:attributes -->

## Overview

Ganondorf is a slower, larger, stronger clone of [Captain Falcon](captain-falcon.md):
weight 109 (4th heaviest), fall speed 2.0, fast-fall speed 2.6, dash speed 1.3, air speed
0.78 (3rd slowest) and a 6-frame jump squat (the grounded frames before a jump leaves the
floor) [wiki:Ganondorf_(SSBM)]. He ranks 14th on the 2021 tier list, the lowest he has
placed [wiki:Ganondorf_(SSBM)]. He has no projectile and no safe way to approach, so his
neutral is bait and punish: he holds space with bair, fair, jab and ftilt and waits for
the opponent to run into one of them [wiki:Ganondorf_(SSBM)]. Every hit hurts: bair does
16%, fair 17%, dair (the stomp) 22%, and most of them kill or send the opponent offstage
at mid percent [fd]. His edgeguarding is his best trait; the late hit of a reversed up
air sends at a 0-30 degree angle with long hitstun and beats most ledge sweetspots
[wiki:Ganondorf_(SSBM)] [lib:Ganon Edgeguarding 101]. His grab leads to down throw chain
grabs and tech chases on fastfallers [lib:The Ganon Chaingrabbing Guide]. He loses to
camping and fast, careful pressure, is easy to combo and chain grab, and is one of the
easiest characters to edgeguard and edgehog [wiki:Ganondorf_(SSBM)]. He benefits more
than anyone from [L-cancelling](../techniques/l-cancel.md), since his aerials have 25-35
frames of landing lag without it [fd].

## Strengths and weaknesses

- **Strengths:**
  - Raw power: fair KOs Mario at 106% and bair at 109% from the centre of Final
    Destination; fair kills Fox/Falco below 80% near the edge of most legal stages
    [wiki:Ganondorf_(SSBM)] [wiki:Ganondorf_(SSBM)/Forward_aerial].
  - Dair: 22% meteor, hitbox covers his whole body, strongest aerial in the game; kills
    grounded opponents under about 100% [wiki:Ganondorf_(SSBM)/Down_aerial].
  - Bair autocancels in a short hop and has no weak late hit; very hard to whiff punish
    [wiki:Ganondorf_(SSBM)/Back_aerial].
  - Jab hits on frame 3 for 7-8% and knocks fastfallers down from about 38-45%
    [fd] [lib:Techchasing into 2015: Metagame and Theory].
  - Edgeguarding: reverse up air, bair, fair, dair, down-angled ftilt, and an aerial
    down B that is a true spike [wiki:Ganondorf_(SSBM)] [lib:Ganon Edgeguarding 101].
  - Down throw chain grabs a large part of the cast [lib:The Ganon Chaingrabbing Guide].
  - Heavy with moderate fall speed: lives long.
- **Weaknesses:**
  - Slow: 6th slowest dash, 3rd slowest air speed, short dash dance, short slow
    wavedash [wiki:Ganondorf_(SSBM)].
  - No projectile; cannot force approaches; struggles against camping
    [wiki:Ganondorf_(SSBM)].
  - Combo food and chain grab victim ([Sheik](sheik.md) down throw, Ice Climbers,
    [Marth](marth.md), the space animals) [wiki:Chain_grab] [wiki:Ganondorf_(SSBM)].
  - Recovery: low double jump, slow drift, up B cannot affect an opponent on the ledge
    [wiki:Ganondorf_(SSBM)] [wiki:Dark_Dive].
  - Slow startup on most moves (fair frame 14, dair frame 16, smashes frame 19-21) [fd].
  - Worst-tier ledgedash: 4 actionable intangible frames [wiki:Ledgedash].
  - Dtilt and other grounded pokes are very vulnerable to crouch cancel (holding down to
    reduce knockback) [wiki:Ganondorf_(SSBM)].

## Character tech

### Reverse up air edgeguard (Tipman spike)

- **id:** `reverse-up-air-edgeguard`
- **What:** Up air performed with his back to the ledge so that the last frames of the
  kick, when the foot points down and behind him, hit a recovering opponent at the ledge.
  The late hit is a low-damage semi-spike (a hit that sends at a very low horizontal
  angle) [wiki:Ganondorf_(SSBM)/Up_aerial].
- **Inputs:** stand near the ledge facing the stage, short hop, up air timed so its final
  active frames reach just below ledge level; L-cancel; then grab the ledge or follow up.
- **Timing:** Up air: clean frames 6-10 (13%), mid 11-13 (12%, angle 30), late 14-16
  (8%, angle 0, base knockback 20, growth 70); landing lag 25, or 12 L-cancelled [fd]
  [wiki:Ganondorf_(SSBM)/Up_aerial]. Frame 16, the last active frame at the toe, reaches
  lowest and does not trade with Fire Fox / Fire Bird [lib:Ganon Edgeguarding 101].
- **Used for:** Beating ledge sweetspots without leaving the stage. Works on Ganondorf,
  Captain Falcon, Fox, Falco, Marth, Sheik and others; after it lands, grabbing the ledge
  usually finishes the stock [lib:Ganon Edgeguarding 101]. It is hard to tech
  [lib:Ganon Edgeguarding 101].
- **Common errors:** Facing the wrong way (the front of the move sends up and out);
  hitting with the thigh instead of the toe; mistiming against Peach's up B, where only
  frame 16 or waiting for the apex works [lib:Ganon Edgeguarding 101]; Marth up B'ing
  right beside the ledge and drifting onto it [lib:Ganon Edgeguarding 101].
- **Drill idea:** CPU recovers to the ledge with a sweetspot; success if the late up air
  hit connects and the CPU fails to reach the ledge afterwards.

### Down throw chain grab

- **id:** `dthrow-chain-grab`
- **What:** Down throw into regrab, repeated. One of the most extensive
  [chain grabs](../techniques/chain-grab.md) in the game by number of characters
  [lib:The Ganon Chaingrabbing Guide].
- **Inputs:** grab, down throw, then standing grab, jump-cancel (JC) grab, dash grab or
  pivot JC grab depending on where the opponent's DI (directional influence, holding a
  direction to bend the launch angle) sends them.
- **Timing:** Ranges in pre-throw percent, assuming the throw does 5%
  [lib:The Ganon Chaingrabbing Guide]: Bowser 0-72, Yoshi 0-36, Donkey Kong 21-69,
  Ganondorf 0-67, Falco 12 to death, Fox 34 to death, Ness 0-18, Sheik 0-90, Link 0-74,
  Young Link 0-72, Pichu 0-54, Pikachu 0-37, Mr. Game & Watch 0-28, Marth 0-15, Roy
  0-91. The end of each range is where DI slightly away sends them straight up and they
  can jump out. Standing grab is active on frames 7-8, dash grab 11-13
  [wiki:Ganondorf_(SSBM)/Grab]; the fastest moving JC grab (1 dash frame, jump, grab)
  has its grab box out in 9 frames, 3 faster than the fastest dash grab; a grab behind
  him costs 1 more frame [lib:The Ganon Chaingrabbing Guide]. Against DI behind he needs
  a pivot dash JC grab from 65% on Falco and 70% on Fox
  [lib:Techchasing into 2015: Metagame and Theory].
- **Used for:** Zero-to-death on Falco and Fox in theory; large damage on Sheik (chain
  grab to 85-90%, then down throw into bair or fair) [lib:Ganon Edgeguarding 101]; ended
  with fair/bair by DI, or fsmash on Sheik from centre stage on Final Destination
  [wiki:Ganondorf_(SSBM)].
- **Common errors:** Dash grab where a JC grab was needed; grabbing too high (the grab
  boxes dip where they overlap); missing the turn for DI behind. The Fox chain grab is
  rated the hardest in the game and Falco's is very hard below 50%
  [lib:The Ganon Chaingrabbing Guide] [lib:Techchasing into 2015: Metagame and Theory].
- **Drill idea:** CPU from the list at the bottom of its range with random DI per throw;
  count regrabs to the end of the range and require an aerial finisher.

### Down throw tech chase

- **id:** `dthrow-tech-chase`
- **What:** Using down throw (and sometimes up throw) to force Fox, Falco and Captain
  Falcon to land next to him and tech, then covering at least one option with a move
  that kills or regrabs [lib:Techchasing into 2015: Metagame and Theory]. See
  [tech chase](../techniques/tech-chase.md).
- **Inputs:** grab, down throw, then by read or reaction: tech in place -> down smash,
  grab, jab; tech away -> dash SHFFL fair; tech toward -> bair or turnaround option;
  missed tech -> jab then dair, or dair.
- **Timing:** Down throw releases on frame 20 of 39 against a baseline weight and sends
  at angle 100 with low growth, so the opponent always lands close
  [wiki:Ganondorf_(SSBM)/Down_throw] [lib:Techchasing into 2015: Metagame and Theory].
  A fresh jab knocks down Fox at 38%, Falco at 39% and Captain Falcon at 45%: at 35-40%
  a late jab after down throw hits them after they have already pressed the tech
  button, forcing a missed tech and a free dair
  [lib:Techchasing into 2015: Metagame and Theory]. The wiki describes down throw, jab,
  dair on space animals at around 50% [wiki:Ganondorf_(SSBM)].
- **Used for:** His main kill route on fastfallers. Up throw is the mixup: with a
  platform in front of him, DI away from up throw lands them on it for a free platform
  tech chase (up air covers it on reaction) [lib:Techchasing into 2015: Metagame and
  Theory].
- **Common errors:** Covering no option at all (the guide's first rule is always cover
  at least one); down smash first hit DI'd out of [lib:On Ganon vs. Falcon]; choosing a
  laggy move that covers only one option at low percent.
- **Drill idea:** Ganondorf holding CPU Fox/Falco/Falcon in grab at 30-90%; CPU DIs and
  techs at random; success on any hit or regrab before the CPU acts; kill-percent mode
  requires fair, bair or dair.

### Autocancel bair wall

- **id:** `autocancel-bair-wall`
- **What:** Repeated short hop bairs that land without landing lag, forming a wall the
  opponent must get around [wiki:Ganondorf_(SSBM)/Back_aerial]. See
  [auto-cancel](../techniques/auto-cancel.md).
- **Inputs:** facing away from the opponent, short hop, bair at or before the top of the
  hop (or at the start of a fast fall), land, repeat or mix with jab/ftilt.
- **Timing:** Bair hitbox frames 10-15, 16%, same power throughout; autocancels from
  frame 19 of the move [fd] [wiki:Ganondorf_(SSBM)/Back_aerial]. A rising bair is high
  enough that every character except Mewtwo can crouch under it and many can dash under
  it; delaying it and fast falling fixes that at the cost of landing lag (25 frames, 12
  L-cancelled) [wiki:Ganondorf_(SSBM)/Back_aerial] [fd].
- **Used for:** Neutral control, anti-approach, shield pokes on characters whose shields
  leave the head exposed (Marth, Falco) [wiki:Ganondorf_(SSBM)/Back_aerial]. When he
  expects a shield he should SHFFL it instead: properly spaced it cannot be shield
  grabbed [wiki:Ganondorf_(SSBM)/Back_aerial].
- **Common errors:** Opponent dashes under the rising bair and punishes; facing the
  wrong way; fair instead of bair (fair does not autocancel in a short hop
  [wiki:Ganondorf_(SSBM)/Forward_aerial]).
- **Drill idea:** CPU approaches with random dash-in grab, short hop aerial or run-under;
  success if bair or the follow-up jab hits first, N times.

### Jab knockdown

- **id:** `jab-knockdown`
- **What:** His frame 3 jab is strong enough to knock opponents down at realistic
  percents, turning a fast defensive poke into a tech chase
  [wiki:Ganondorf_(SSBM)/Neutral_attack].
- **Inputs:** A (often after running and crouching, after a wavedash, after a tech roll,
  or right after a blocked aerial).
- **Timing:** Hitbox frames 3-5, 7-8%, base knockback 30, interruptible on frame 19
  [fd] [wiki:Ganondorf_(SSBM)/Neutral_attack]. Electric effect (longer hitlag).
  Knockdown thresholds, fresh: Fox 38%, Falco 39%, Captain Falcon 45%
  [lib:Techchasing into 2015: Metagame and Theory].
- **Used for:** Stopping run-ins and grabs, covering the gap after a spaced fair or bair
  on shield, wake-up option, tech-chase starter; after a jab that hits a space animal
  out of side B he gets a free dair or fair [lib:Ganon Edgeguarding 101].
- **Common errors:** Trading (which makes the opponent's tech unpunishable)
  [lib:Techchasing into 2015: Metagame and Theory]; short characters ducking under it
  [wiki:Ganondorf_(SSBM)].
- **Drill idea:** CPU Fox dashes in for a grab or nair at random timing; success if the
  jab hits clean and the resulting tech is punished.

### Up-angled ftilt anti-air

- **id:** `up-angled-ftilt-anti-air`
- **What:** Ftilt angled up as his fastest reliable answer to short hop approaches
  [wiki:Ganondorf_(SSBM)].
- **Inputs:** stick diagonally up-forward (tilt, not smash) + A.
- **Timing:** Hitbox frames 9-11 for all angles, total 29 frames; up angle does 12-14%,
  side 11-13%, down 10-12% [fd]. Spaced on shield with the foot it is about -13, which a
  space animal cannot punish with a waveshine [wiki:Ganondorf_(SSBM)/Forward_tilt].
- **Used for:** Beating Captain Falcon's short hop nair and knee and other jump-ins
  [lib:On Ganon vs. Falcon]; the down angle hits ledge sweetspots, especially Fox/Falco
  side B [wiki:Ganondorf_(SSBM)].
- **Common errors:** Only 3 active frames, so mistiming whiffs; fsmash by accident.
- **Drill idea:** CPU Captain Falcon approaches with short hop nair or knee at varied
  timing; success if up-angled ftilt hits or trades favourably.

### Stomp conversions

- **id:** `stomp-conversion`
- **What:** Dair on a grounded opponent pops them up at low percent for another aerial,
  and kills off the top at high percent; in the air it is a meteor
  [wiki:Ganondorf_(SSBM)/Down_aerial].
- **Inputs:** short hop or full hop dair, fast fall, L-cancel, then jab, grab, first-hit
  nair, fair, bair or another dair.
- **Timing:** Hitbox frames 16-20, 22%, angle 270; autocancels from frame 36; landing lag
  35 frames or 17 L-cancelled [fd] [wiki:Ganondorf_(SSBM)/Down_aerial]. A full hop dair
  that intercepts an approach forces a tech when they hit the ground; a dair out of
  shield hits early, so the fast fall must be delayed
  [lib:Techchasing into 2015: Metagame and Theory].
- **Used for:** Punishing missed techs and predictable approaches; dair then fair sends
  offstage; at lower percent dair then first-hit nair onto a platform creates another
  tech chase [lib:Techchasing into 2015: Metagame and Theory].
- **Common errors:** Missed L-cancel (35 frames); opponent meteor cancels or techs when
  used at the ledge [lib:Ganon Edgeguarding 101].
- **Drill idea:** CPU misses a tech at 40-100%; success if dair hits and one more aerial
  connects in the same combo (or the CPU dies).

### First-hit nair juggle

- **id:** `first-hit-nair-juggle`
- **What:** Landing only the first kick of nair, which has lower knockback and a 55-65
  degree angle, to keep the opponent close for another hit
  [wiki:Ganondorf_(SSBM)/Neutral_aerial].
- **Inputs:** jump, nair so the first kick hits, land with L-cancel before the second
  kick (or let the opponent's DI carry them away from it), repeat or finish with
  fair/bair.
- **Timing:** Hit 1 frames 7-8 (12%), hit 2 frames 20-21 (12%); landing lag 25 or 12
  L-cancelled [fd]. The first hit rarely links into the second and never past about 25%
  [wiki:Ganondorf_(SSBM)].
- **Used for:** Mid-percent combo extension after dair, down smash or dtilt, one to four
  repetitions, then fair or bair [wiki:Ganondorf_(SSBM)/Neutral_aerial]; creating
  platform tech chases [lib:Techchasing into 2015: Metagame and Theory].
- **Common errors:** Second kick hits and launches too far; only 2 active frames per
  kick.
- **Drill idea:** CPU launched by dair at 40-70% with random DI; success if two or more
  first-hit nairs connect followed by fair or bair.

### Wizard's Foot jump restore

- **id:** `wizards-foot-jump-restore`
- **What:** Using aerial down B (Wizard's Foot) after the double jump: if the move ends
  in the air he gets the double jump back [wiki:Wizard's_Foot].
- **Inputs:** double jump, down B while high, wait for the move to end, double jump
  again, up B.
- **Timing:** Aerial Wizard's Foot: hitbox frames 15-30, about 58 frames total, travels
  steeply down; landing during it costs 57 frames of landing lag [wiki:Wizard's_Foot].
  More usable than Falcon Kick because Ganondorf falls slower [wiki:Wizard's_Foot].
- **Used for:** Extending recovery when launched high.
- **Common errors:** Using it close to the stage: the opponent gets a free fair, bair or
  dair if they hit him before it ends [lib:Ganon Edgeguarding 101]; starting too low.
- **Drill idea:** Ganondorf launched high and far without a double jump; success if he
  reaches the ledge.

### Wizard's Foot spike

- **id:** `wizards-foot-spike`
- **What:** The aerial down B kick is a true spike (cannot be meteor cancelled), usable
  offstage as a high-risk edgeguard [wiki:Ganondorf_(SSBM)] [lib:Ganon Edgeguarding 101].
- **Inputs:** full jump off stage toward the opponent, down B at about three quarters of
  jump height or higher, then double jump and up B back.
- **Timing:** 14%, angle 290 [fd]; hitbox frames 15-30 [wiki:Wizard's_Foot]. From ground
  level he must full jump and reach about 3/4 of the jump's height before down B to make
  it back to the ledge, and must double jump or be at the peak to make it back onto the
  stage; never from a short hop [lib:Ganon Edgeguarding 101].
- **Used for:** Ganondorf dittos and Captain Falcon; DK and Bowser [wiki:Ganondorf_(SSBM)]
  [lib:Ganon Edgeguarding 101].
- **Common errors:** Missing (he is then edgeguarded himself); spiking someone into the
  stage wall, where it can be teched [lib:Ganon Edgeguarding 101].
- **Drill idea:** CPU Ganondorf/Falcon recovers from the side; success if the spike
  connects and the player returns to the ledge.

### Ledgehop stall and ledge options

- **id:** `ledgehop-stall-and-ledge-options`
- **What:** Ganondorf's ledgedash is poor, so he uses other intangible ledge options:
  the ledgehop stall, ledge-drop up air, no-impact-land ledge jump and reverse ledgedash.
- **Inputs:** Stall: drop with fast fall, double jump, regrab [wiki:Ledgestall].
  Invincible up air: double jump regrab the ledge, drop with away (no fast fall), up air
  immediately [lib:Ganon Edgeguarding 101]. Reverse ledgedash ("haxdash"): drop, jump
  toward the stage, airdodge back out to slide off and regrab or double jump back in
  [lib:Ganondorf Guide of Advanced Techniques].
- **Timing:** Ledge grab gives 29 usable intangible frames after the earliest drop on
  frame 9 [wiki:Ledgestall]. Normal ledgedash: 4 actionable intangible frames; jumping
  straight onto the stage with a no-impact land: 9; grabbing the ledge at the apex of up
  B first raises that to 18 [wiki:Ledgedash]. The ledge-drop up air can have every
  hitbox frame covered by ledge intangibility [lib:Ganon Edgeguarding 101].
- **Used for:** Edgehogging through recoveries, intangible up air against Marth's up B,
  getting back on stage against ledge pressure.
- **Common errors:** Fast falling too long; airdodging off stage in the reverse
  ledgedash [lib:Ganondorf Guide of Advanced Techniques].
- **Drill idea:** Count intangible frames remaining when the up air hitbox starts, or on
  first grounded actionable frame.

### Lightshield edgehog

- **id:** `lightshield-edgehog`
- **What:** Standing at the edge in a light shield while holding away, so that a
  recovery move hitting the shield pushes him off the stage onto the ledge, taking it
  from the recovering opponent. Nicknamed the "Marth killer" [lib:Ganon Edgeguarding 101].
- **Inputs:** roll to the edge while holding Z (light shield) and the stick away from
  the stage.
- **Timing:** Used when Marth must up B to survive; the shield ASDI (automatic small
  shift in the held direction when hit) outward drops him to the ledge. If Marth lands on
  stage instead, his landing lag is long enough to ledgehop and grab him; from the grab,
  down throw into fair or bair works at mid percent up to about 130%
  [lib:Ganon Edgeguarding 101].
- **Used for:** [Marth](marth.md) recoveries from below.
- **Common errors:** Doing it too early: Marth jumps and fairs or nairs instead
  [lib:Ganon Edgeguarding 101].
- **Drill idea:** CPU Marth recovers low with up B (variation: with a jump left);
  success if Ganondorf ends on the ledge and Marth dies, or Marth is grabbed on landing.

### Crouch cancel getup attack punish

- **id:** `cc-getup-attack-punish`
- **What:** Crouching on reaction to a getup attack so it barely moves him, then
  punishing with dtilt (or grab at low percent) [lib:Ganondorf Knockdown Data].
- **Inputs:** stand over a missed tech, crouch when the getup attack starts, after it
  hits press dtilt, then fair or up air.
- **Timing:** Dtilt hits on frames 10-12 [fd]. The thread notes a percent range in which
  only certain moves (notably dtilt) reach Fox before he can act; exact numbers: Unknown
  (the first post was not retrievable).
- **Used for:** Turning the opponent's getup attack into a kill confirm; see
  [crouch cancel](../techniques/crouch-cancel.md).
- **Common errors:** Crouching late; ASDI toward the attacker lifts him off the ground
  [lib:Ganondorf Knockdown Data].
- **Drill idea:** CPU misses a tech and then randomly getup attacks, rolls or stands;
  success if a getup attack is crouch cancelled and dtilt connects.

## Neutral game

- **Hold space, do not chase.** Fast characters must come to him; he punishes the
  approach [wiki:Ganondorf_(SSBM)].
- **Bair** (short hop autocancel) and **fair** (falling, spaced) are the wall. Both are
  hard to punish on shield when spaced because of their damage and pushback; a jab
  afterwards stuffs most punish attempts [wiki:Ganondorf_(SSBM)/Forward_aerial].
- **Jab** (frame 3) and **ftilt** (frame 9) are the grounded answers. Ftilt and dash
  attack are slightly more disjointed at the tip than jab
  [lib:Techchasing into 2015: Metagame and Theory].
- **Up-angled ftilt** for jump-ins; **retreating up air** also catches Falcon's nair
  approach [lib:On Ganon vs. Falcon].
- **Stay grounded against Falcon;** aerial approaches get him combo'd
  [lib:On Ganon vs. Falcon].
- **Grabs** come from wavedash back into dash JC grab, empty hop ("tomahawk") grabs,
  crouch cancel or ASDI down into grab, jab into grab, side B into grab, and
  ledgedash grabs [lib:Techchasing into 2015: Metagame and Theory].
- **Movement:** perfect wavelands on platforms, moonwalk, pivots; his roll is unusually
  fast and long [wiki:Ganondorf_(SSBM)] [lib:Ganondorf Guide of Advanced Techniques].
- **Against projectiles:** [powershield](../techniques/powershield.md); the "Z
  powershield" (Z and L/R on the same frame, A held to stop the grab) enlarges the
  reflecting area [lib:Ganondorf Guide of Advanced Techniques].
- **Up smash** (hits frames 21-23 and 26-29; the move page gives -3 on shield for the
  second hit, the character page -7) is a
  committal anti-air and ledge call-out [wiki:Ganondorf_(SSBM)/Up_smash].
- **Side B** (Gerudo Dragon) covers tech options and can hit slightly behind him, but is
  very unsafe on whiff [wiki:Ganondorf_(SSBM)].

## Punish game

Ganondorf needs few hits. Against fastfallers: grab, down throw, then chain grab or
tech chase into dair/fair/bair. Against mid-weights: down throw into bair or fair by DI,
or chain grab first. Launchers (dair, down smash, dtilt) lead to first-hit nair juggles
and a fair or bair finish, then an edgeguard.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| Down throw | Falco | 12% to death (pre-throw) | Regrab | Very hard below 50%; pivot dash JC grab for DI behind from 65% | [lib:The Ganon Chaingrabbing Guide] [lib:Techchasing into 2015: Metagame and Theory] |
| Down throw | Fox | 34% to death (pre-throw) | Regrab | Hardest chain grab in the game; pivot dash JC grab for DI behind from 70% | [lib:The Ganon Chaingrabbing Guide] |
| Down throw | Sheik | 0-90% | Regrab; end at 85-90% with bair or fair | 80-90% is tricky | [lib:The Ganon Chaingrabbing Guide] [lib:Ganon Edgeguarding 101] |
| Down throw | Roy 0-91, Link 0-74, Young Link 0-72, Bowser 0-72, DK 21-69, Ganondorf 0-67, Pichu 0-54, Pikachu 0-37, Yoshi 0-36, G&W 0-28, Ness 0-18, Marth 0-15 | as listed | Regrab | Pre-throw percent; escape by DI slightly away then jump | [lib:The Ganon Chaingrabbing Guide] |
| Down throw | Fox, Falco | 35-40% | Late jab (forces missed tech), then dair | | [lib:Techchasing into 2015: Metagame and Theory] |
| Down throw | Non-space-animals | until it kills | Bair on DI behind; fair on DI in front | Turn around for bair on DI forward from 125% | [wiki:Ganondorf_(SSBM)/Back_aerial] |
| Down throw | Marth (after a ledgehop grab) | mid to about 130% | Fair or bair | | [lib:Ganon Edgeguarding 101] |
| Down throw / up throw | Captain Falcon | any | Regrab unless he DIs full away (down throw) or behind (up throw); otherwise tech chase | | [lib:Techchasing into 2015: Metagame and Theory] |
| Up throw | Fastfallers under a platform | mid+ | Platform tech chase with up air | DI away is only safe for them with no platform | [lib:Techchasing into 2015: Metagame and Theory] |
| Dair (grounded) | Most | low-mid | Jab, first-hit nair, fair, bair, dair | Then tech chase or edgeguard | [lib:Techchasing into 2015: Metagame and Theory] |
| Down smash | Fastfallers | kill percent | Aerial (fair, bair or dair) | Second hit sends up; first hit can be DI'd out | [wiki:Ganondorf_(SSBM)] [lib:On Ganon vs. Falcon] |
| Dtilt | Most | mid | Most aerials | Loses to crouch cancel | [wiki:Ganondorf_(SSBM)] |
| First-hit nair | Most | mid | Nair again (1-4 times), then fair/bair | | [wiki:Ganondorf_(SSBM)/Neutral_aerial] |
| Jab | Fox / Falco / Falcon | from 38% / 39% / 45% | Tech chase | Fresh jab knockdown thresholds | [lib:Techchasing into 2015: Metagame and Theory] |
| Crouch cancelled getup attack | Fox and others | varies | Dtilt, then fair or up air | | [lib:Ganondorf Knockdown Data] |

### Chain grabs and tech chases

- **Chain grab list and ranges:** see the technique entry. Captain Falcon is not truly
  chain grabbable: the chain grab guide says he escapes down throw at any percent by DI'ing behind
  and up throw by DI'ing away; the later tech-chase guide says Ganondorf can regrab
  him unless he DIs down throw full away or up throw behind
  [lib:The Ganon Chaingrabbing Guide] [lib:Techchasing into 2015: Metagame and Theory].
  The two sources disagree on which DI escapes which throw.
- **Since the guide was written,** Yoshi and Pikachu players have developed better
  counterplay to his chain grabs [wiki:Ganondorf_(SSBM)].
- **Chain grab or tech chase?** Decide by how reliable the regrab is: a missed regrab
  loses both the kill and the damage [lib:Techchasing into 2015: Metagame and Theory].
- **Knockdown thresholds (fresh) for starting tech chases:**

  | Move | Fox | Falco | Captain Falcon |
  |-|-|-|-|
  | Jab | 38% | 39% | 45% |
  | Ftilt | 22% | 23% | 28% |
  | Dtilt | 17% | 18% | 22% |
  | Dash attack | 12% | 12% | 18% |

  [lib:Techchasing into 2015: Metagame and Theory]
- **Coverage:** tech in place -> down smash (damage and a free aerial) or grab; tech
  away -> dash SHFFL fair; rolls toward the ledge -> run and fair to start the edgeguard
  [lib:On Ganon vs. Falcon]. Side B and grounded down B cover rolls on a read
  [lib:On Ganon vs. Falcon]. On platforms, up air on reaction "always works"
  [lib:Techchasing into 2015: Metagame and Theory]; fair also reaches platform tech
  options from below [wiki:Ganondorf_(SSBM)/Forward_aerial].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Fair | Mario | 106% | Centre of Final Destination | [wiki:Ganondorf_(SSBM)] |
| Fair | Fox, Falco | below 80% | Near the edge of most legal stages | [wiki:Ganondorf_(SSBM)/Forward_aerial] |
| Bair | Mario | 109% | Centre of Final Destination; stronger than fair above about 106-125% (the wiki gives both figures) | [wiki:Ganondorf_(SSBM)] [wiki:Ganondorf_(SSBM)/Back_aerial] |
| Dair | Grounded opponents | under about 100% | Off the top after the ground bounce | [wiki:Ganondorf_(SSBM)/Down_aerial] |
| Dair | Offstage opponents | any | Meteor; can be meteor cancelled | [wiki:Ganondorf_(SSBM)/Down_aerial] |
| Up smash (foot, second hit) | Fastfallers | below 100% | Hits frame 21+ | [wiki:Ganondorf_(SSBM)] |
| Nair second kick | Most | under 130% | | [wiki:Ganondorf_(SSBM)] |
| Grounded down B | Mario | about 115% centre FD, about 75% at the ledge | Very unsafe on whiff or shield | [wiki:Wizard's_Foot] |
| Side B (grounded) | Most | from about 127% | | [wiki:Ganondorf_(SSBM)] |
| Up B | Most | about 150% | Centre of Final Destination | [wiki:Dark_Dive] |
| Reverse up air (late) | Anyone recovering | any (gimp) | At the ledge; follow with edgehog | [lib:Ganon Edgeguarding 101] |
| Aerial down B | Offstage opponents | any | True spike; high risk | [lib:Ganon Edgeguarding 101] |
| Up tilt | Any | as low as 30% | Hits on frame 81; shield break or ledge trap only | [wiki:Ganondorf_(SSBM)] [fd] |
| Neutral B (Warlock Punch) | Any | very low | Hits on frame 70; not practical | [wiki:Ganondorf_(SSBM)] [fd] |

- **Kill setups:** down throw into bair/fair; chain grab into fair/bair/fsmash; tech
  chase into dair or fair; down smash into aerial on fastfallers; dair into fair; jab
  knockdown into tech chase.
- **Edgeguards** (he rarely needs to leave the stage) [lib:Ganon Edgeguarding 101]:
  - Reverse up air for anyone sweetspotting; then grab the ledge.
  - Bair, fully spaced, for an up B that overshoots; wait until they are just above
    stage level so they cannot tech the wall.
  - Down-angled ftilt for side B and ledge sweetspots when there is no time to turn
    around.
  - Jab or ftilt against a space animal's side B onto the stage; then dair/fair, or
    edgehog.
  - Fast-fall fair or drop-zone up air when they up B too close.
  - Dair at the ledge as a last resort (meteor cancel and wall tech are possible).
  - Hit Fox/Falco out of the up B charge whenever reachable.

## Recovery

- **Options:**
  - Double jump (low) and slow drift [wiki:Ganondorf_(SSBM)].
  - Up B (Dark Dive): rises diagonally; grab box from frame 13 (lasting to about frame
    33-39 depending on source); a successful grab does 17% in total and lets him up B
    again; grabs the ledge even facing away; unlike Falcon's it has electric hitboxes
    that can hit bystanders [wiki:Dark_Dive] [wiki:Ganondorf_(SSBM)/Up_special] [fd].
  - Aerial down B: restores the double jump if it ends in the air [wiki:Wizard's_Foot].
  - Aerial side B: horizontal distance, then helpless [wiki:Ganondorf_(SSBM)].
  - Airdodge; attacking the edgeguarder with fair/up air on the way back.
- **Mixups:** up B early versus late; aiming to grab the edgeguarder; down B then double
  jump; using the down B spike on an opponent who comes out to edgeguard
  [lib:On Ganon vs. Falcon]; wall tech into immediate fair when grabbed by an opposing
  Dark Dive / Falcon Dive below the stage [lib:Ganon Edgeguarding 101].
- **Weaknesses:** Slow and linear; the double jump gives little height; up B cannot grab
  or affect an opponent hanging on the ledge, so edgehogging is very effective
  [wiki:Dark_Dive] [wiki:Ganondorf_(SSBM)].

### Edgeguarding Ganondorf

- **Edgehog:** when he is below the ledge and must up B, hold the ledge (refresh
  intangibility if needed). He cannot hit a ledge-hanging opponent [wiki:Dark_Dive].
- **Hit the up B from the stage:** a spaced bair-type move as he rises just above ground
  level; do not stand where the grab box reaches [lib:Ganon Edgeguarding 101].
- **Punish down B:** if he uses Wizard's Foot to regain his jump near the stage, jump out
  and hit him before it ends; he then has no jump [lib:Ganon Edgeguarding 101].
- **Take his double jump:** Falco's ledge lasers force him to recover repeatedly
  [wiki:Blaster_(Falco)]; Falco's and Fox's fsmash cover his drift to ledge or stage
  [wiki:Falco_(SSBM)/Forward_smash].
- **Go out:** his slow air speed makes him easy to reach; a Fox shine or any semi-spike
  ends the stock.
- **If grabbed by Dark Dive below the stage:** tech the wall on the release hit and
  counter-attack ("tech check") [wiki:Dark_Dive].
- **CPU-as-Ganondorf recovery policy:** far and high: drift, optionally down B then
  double jump; near: double jump late, up B to ledge; if the ledge is taken, up B onto
  the stage or try to grab the edgeguarder.

## Defense and out of shield

- **Out of shield:** shield grab (frame 7 [wiki:Ganondorf_(SSBM)/Grab]); up air (6 jump
  squat frames plus frame 6 hitbox = frame 12 [wiki:Ganondorf_(SSBM)] [fd]); bair (frame
  16 by the same sum); wavedash or dash out of shield into jab/ftilt; roll (his roll is
  among the fastest and longest) [wiki:Ganondorf_(SSBM)]; shield drop up air on
  platforms covers almost the whole platform [lib:Ganondorf Guide of Advanced
  Techniques].
- **Crouch cancel and ASDI down:** very strong because of his weight; run-crouch or ASDI
  down into jab or grab is a core counter to approaches
  [wiki:Ganondorf_(SSBM)/Neutral_attack]. During ftilt he can buffer ASDI down plus a
  tech away at once (C-stick down, control stick down-away)
  [wiki:Ganondorf_(SSBM)/Forward_tilt].
- **Combo escapes:** none fast. Jab (frame 3) after a tech roll or in a gap; DI away from
  Falcon's up air chains at low percent rather than up [lib:On Ganon vs. Falcon]; SDI to
  shift position [lib:Techchasing into 2015: Metagame and Theory].
- **What beats him:** camping, projectiles, grabs into chain grabs, and shield pressure
  that stays outside jab range.

## As the training dummy

- **Class:** heavy (weight 109), medium-fast faller (fall 2.0, fast fall 2.6)
  [wiki:Ganondorf_(SSBM)]. Tall, wide hurtbox. Does not fall from Fox's shine (weight
  above 87) [wiki:Waveshine].
- **Chain grabbed by:** [Sheik](sheik.md) down throw (NTSC), 0% to medium/high percent,
  up to about 90% on poor DI; Ice Climbers (Popo alone with down throw to about 50%)
  [wiki:Chain_grab]; [Captain Falcon](captain-falcon.md) down throw
  [wiki:Captain_Falcon_(SSBM)]; Ganondorf down throw 0-67%
  [lib:The Ganon Chaingrabbing Guide]; Mario/Dr. Mario down throw (heavyweights) and
  Peach down throw unless he DIs away [wiki:Chain_grab].
- **Combo'd by:** Fox waveshines and Falco pillars (he slides rather than falls); Fox's
  fair works well on him [lib:Chaingrab Info] (thread comment).
- **Strong DI for a realistic CPU:** against down throw chain grabs, slightly away so he
  rises straight up and can jump at the end of the range
  [lib:The Ganon Chaingrabbing Guide]; against horizontal kill moves, up and in
  [unverified].
- **Recovery behaviour:** see "Edgeguarding Ganondorf". A realistic CPU avoids down B
  near the stage and aims up B at the ledge only when it is free.
- **Crouch cancel:** a realistic Ganondorf CPU holds down against weak aerials at low
  and mid percent and answers with jab or grab. Heavy characters crouch cancel Fox's
  nair until above 80% (the wiki's examples are Donkey Kong and Captain Falcon;
  Ganondorf is heavier than Falcon) [wiki:Fox_(SSBM)/Neutral_aerial].

## Matchup notes

### vs Fox

- Fox camps with lasers and out-moves him; Ganondorf must powershield or accept damage
  and wait for an approach [wiki:Ganondorf_(SSBM)].
- One grab can be a stock: down throw chain grab from 34%, or jab/tech-chase setups at
  35-40% [lib:The Ganon Chaingrabbing Guide]
  [lib:Techchasing into 2015: Metagame and Theory].
- "Any time you knock Fox or Falco offstage they should be dead": reverse up air, bair,
  down-angled ftilt; hit the up B before it launches [lib:Ganon Edgeguarding 101].
  Reverse up air may not kill Fox outright but sets up the next hit.

### vs Falco

- Lasers control him; Z-powershield and patience are the answers
  [lib:Ganondorf Guide of Advanced Techniques].
- Chain grab from 12% (pre-throw) to death, very hard below 50%
  [lib:The Ganon Chaingrabbing Guide]. Bair shield-pokes Falco's head
  [wiki:Ganondorf_(SSBM)/Back_aerial].
- After a reverse up air on a sweetspotting Falco, an immediate drop-zone dair secures
  the kill [lib:Ganon Edgeguarding 101].

### vs Captain Falcon

- Stay grounded; up-angled ftilt beats short hop nair and knee; keep a jab ready for
  grab, gentleman and side B [lib:On Ganon vs. Falcon].
- Tech chasing from down throw is "the only way Ganon stands a chance"; tech in place ->
  down smash; near the ledge -> fair [lib:On Ganon vs. Falcon].
- Edgeguarding Falcon is easy: reverse up air, bair, drop-zone up air; do not commit
  early when he drifts between ledge and stage [lib:Ganon Edgeguarding 101].
- When combo'd at low percent, DI away from up air chains [lib:On Ganon vs. Falcon].

### vs Sheik

- Sheik chain grabs him in NTSC and edgeguards him easily [wiki:Chain_grab]. He chain
  grabs her back from 0-90% and can finish with fsmash from centre stage on Final
  Destination [lib:The Ganon Chaingrabbing Guide] [wiki:Ganondorf_(SSBM)].
- Edgeguard her by taking the ledge, standing up through the up B hitbox with
  intangibility, pausing a few frames and grabbing [lib:Ganon Edgeguarding 101].

### vs Marth

- Marth out-ranges him on the ground; Ganondorf's bair pokes the top of Marth's shield
  [wiki:Ganondorf_(SSBM)/Back_aerial], and Marth can duck under down smash
  [wiki:Ganondorf_(SSBM)].
- Edgeguards: reverse up air beats the sweetspot when timed; lightshield edgehog when
  Marth must up B; invincible ledge-drop up air beats the up B itself
  [lib:Ganon Edgeguarding 101].

### vs Peach

- Reverse up air must be timed at the apex of her up B or with frame 16 only; non-lethal
  bairs give her many recovery options [lib:Ganon Edgeguarding 101].

### vs Ganondorf (ditto)

- Fight facing backwards with spaced bairs, which beat the fair approach; chain grab
  0-67%; Wizard's Foot spike and reverse up air offstage
  [lib:On Ganon vs. Falcon] [lib:The Ganon Chaingrabbing Guide]
  [lib:Ganon Edgeguarding 101].

## Drill seeds

### Reverse up air at the ledge

- **id:** `ganondorf-reverse-uair`
- **Goal:** Hit a ledge sweetspot with the late up air hit and secure the stock.
- **Player:** Ganondorf
- **CPU:** [Fox](fox.md), [Falco](falco.md), [Marth](marth.md),
  [Captain Falcon](captain-falcon.md), [Ganondorf](ganondorf.md), [Sheik](sheik.md)
- **Setup:** CPU offstage near ledge height or below at 40-90%; Ganondorf on stage one
  step from the ledge, facing centre stage.
- **CPU behaviour:** Recovers to the ledge with a sweetspot (side B at ledge height for
  space animals, up B from below for the others) at random timing; sometimes aims at the
  stage instead.
- **Success:** The up air's late hit (8% hit) connects and the CPU does not reach the
  ledge or stage afterwards (edgehog allowed).
- **Fail:** CPU grabs the ledge or lands; Ganondorf is hit.
- **Variations:** Peach (frame 16 only); CPU that goes high (correct answer becomes
  bair or ftilt); require an edgehog after the hit.
- **Data needed:** Up air hitbox positions per frame (frame 16 toe), CPU recovery
  timings and ledge-grab boxes, short hop height, L-cancel lag 12.

### Down throw chain grab

- **id:** `ganondorf-dthrow-chaingrab`
- **Goal:** Regrab through the whole listed range against changing DI.
- **Player:** Ganondorf
- **CPU:** [Sheik](sheik.md) (easiest), [Falco](falco.md), [Fox](fox.md),
  [Link](link.md), [Roy](roy.md)
- **Setup:** Final Destination centre; Ganondorf holding the CPU in grab at the bottom of
  the range (Sheik 0%, Falco 12%, Fox 34%).
- **CPU behaviour:** Random DI on each throw (in front, behind, slightly away); jumps at
  the first actionable frame.
- **Success:** N consecutive regrabs, or reaching a target percent, then a fair or bair
  finisher that connects.
- **Fail:** CPU lands and acts or jumps out.
- **Variations:** Fixed DI to learn standing / JC / dash / pivot grabs; DI behind above
  65% (Falco) and 70% (Fox), which needs pivot dash JC grabs.
- **Data needed:** Down throw knockback (angle 100, base 75, growth 36
  [wiki:Ganondorf_(SSBM)/Down_throw]), victim weight and fall speed, the three grab
  ranges and their frames.

### Tech chase fastfallers from down throw

- **id:** `ganondorf-tech-chase`
- **Goal:** Always cover at least one tech option with a rewarding move.
- **Player:** Ganondorf
- **CPU:** [Fox](fox.md), [Falco](falco.md), [Captain Falcon](captain-falcon.md)
- **Setup:** Ganondorf holding the CPU in grab at 20-100%, centre or near a ledge;
  Battlefield for the platform variant.
- **CPU behaviour:** Random DI; techs in place / toward / away or misses; shines or
  spot dodges after tech in place (space animals).
- **Success:** A hit or grab connects before the CPU acts; at kill percent the hit must
  be fair, bair, dair or down smash.
- **Fail:** CPU escapes or hits Ganondorf.
- **Variations:** 35-40% jab-forced missed tech into dair; up throw onto a platform and
  up air on reaction.
- **Data needed:** Tech roll distances and timings for the CPU, jab knockdown thresholds
  (table above), Ganondorf dash speed and move startups.

### Bair wall against approaches

- **id:** `ganondorf-bair-wall`
- **Goal:** Space autocancelled bairs and jabs so that no approach gets through.
- **Player:** Ganondorf
- **CPU:** [Fox](fox.md), [Captain Falcon](captain-falcon.md), [Marth](marth.md),
  [Sheik](sheik.md)
- **Setup:** Final Destination; Ganondorf facing away from the CPU at mid range.
- **CPU behaviour:** Random approach: dash-in grab, short hop aerial, run under and
  attack, or wait and whiff punish a bair.
- **Success:** Ganondorf lands a hit before being hit or grabbed, N times in a row.
- **Fail:** Grabbed or hit.
- **Variations:** CPU shields (player should SHFFL a spaced bair and jab, or grab).
- **Data needed:** Bair frames 10-15 and autocancel frame 19, short hop air time, CPU
  crouch/dash hurtbox heights.

### Edgeguard the space animals from the stage

- **id:** `ganondorf-edgeguard-spacies`
- **Goal:** Choose the right on-stage edgeguard for each recovery.
- **Player:** Ganondorf
- **CPU:** [Fox](fox.md), [Falco](falco.md)
- **Setup:** CPU offstage at 30-80%, random height, with or without a double jump.
- **CPU behaviour:** Random: side B to the ledge, side B onto the stage, up B to the
  ledge from below, up B over Ganondorf, wall tech into up B.
- **Success:** CPU is hit and loses the stock, or is hit back offstage.
- **Fail:** CPU returns unhit or hits Ganondorf.
- **Variations:** Require the specific answer per option (reverse up air / down-angled
  ftilt / jab / bair) [lib:Ganon Edgeguarding 101].
- **Data needed:** Side B travel frames (Fox 21, Falco 17), up B charge and travel
  frames, Ganondorf move startups.

### Recover against an edgehog

- **id:** `ganondorf-recovery`
- **Goal:** Get back with a slow recovery against ledge coverage.
- **Player:** Ganondorf
- **CPU:** [Fox](fox.md), [Marth](marth.md), [Sheik](sheik.md),
  [Captain Falcon](captain-falcon.md)
- **Setup:** Ganondorf offstage at 50-100%, with and without a double jump, at three
  heights.
- **CPU behaviour:** Randomly holds the ledge, hits from the stage, or jumps out with an
  aerial.
- **Success:** Ganondorf reaches ledge or stage and is actionable.
- **Fail:** Hit or falls.
- **Variations:** Launched high (down B jump restore needed); CPU that punishes down B
  near the stage.
- **Data needed:** Up B path and grab frames, down B distance and duration, double jump
  height.

### Stomp punish and conversion

- **id:** `ganondorf-stomp`
- **Goal:** Land dair on a missed tech or predictable action and convert.
- **Player:** Ganondorf
- **CPU:** [Fox](fox.md), [Falco](falco.md), [Marth](marth.md), [Sheik](sheik.md)
- **Setup:** CPU knocked down next to Ganondorf at 30-110%.
- **CPU behaviour:** Misses the tech and waits a random time, or techs in place.
- **Success:** Dair connects and either a second aerial hits in the same combo or the
  CPU is KO'd.
- **Fail:** Dair whiffs or the L-cancel is missed and the CPU punishes.
- **Variations:** Dair out of shield; full hop dair against an approaching CPU.
- **Data needed:** Dair frames 16-20, landing lag 17, hitstun at each percent.

### Lightshield edgehog on Marth

- **id:** `ganondorf-marth-killer`
- **Goal:** Take the ledge from a recovering Marth using his own up B.
- **Player:** Ganondorf
- **CPU:** [Marth](marth.md)
- **Setup:** Marth below the ledge without a double jump (variation: with one);
  Ganondorf on stage near the ledge.
- **CPU behaviour:** Up B to the ledge; with a jump, sometimes jumps and fairs instead.
- **Success:** Ganondorf ends on the ledge and Marth dies, or Marth lands on stage and is
  grabbed and punished.
- **Fail:** Marth grabs the ledge, or Ganondorf is hit by fair.
- **Variations:** Invincible ledge-drop up air instead.
- **Data needed:** Marth up B hit frames, light shield size and ASDI behaviour, ledge
  intangibility.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlGn.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/ganondorf.json`](../framedata/ganondorf.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 3-5 | 7/8 | Sakurai | 30 | 100 | - | electric | 21 | 19 | 5 | -10 |  |
| Jab 2 | `jab2` | - | - | - | - | - | - | - | 31 | - | - | - | starts 1 frame late (included) |
| Dash attack | `dash_attack` | 7-9 | 14 | 115 | 40 | 80 | - |  | 39 | 38 | 8 | -22 |  |
|  |  | 10-16 | 10 | 110 | 25 | 60 | - |  |  |  | 6 | -21 |  |
| Forward tilt (angled up) | `ftilt_high` | 9-11 | 14/13/12 | Sakurai | 20 | 100 | - |  | 29 | - | 8 | -12 |  |
| Forward tilt (slightly up) | `ftilt_mid_high` | 9-11 | 14/13/12 | Sakurai | 20 | 100 | - |  | 29 | - | 8 | -12 |  |
| Forward tilt | `ftilt` | 9-11 | 13/12/11 | Sakurai | 20 | 100 | - |  | 29 | - | 7 | -13 |  |
| Forward tilt (slightly down) | `ftilt_mid_low` | 9-11 | 12/11/10 | Sakurai | 20 | 100 | - |  | 29 | - | 7 | -13 |  |
| Forward tilt (angled down) | `ftilt_low` | 9-11 | 12/11/10 | Sakurai | 20 | 100 | - |  | 29 | - | 7 | -13 |  |
| Up tilt | `utilt` | 81-83 | 27 | Sakurai | 110 | 80 | - | fire | 114 | 113 | 14 | -17 |  |
| Down tilt | `dtilt` | 10-12 | 12 | 80/70/60 | 30 | 100 | - |  | 35 | 35 | 7 | -17 |  |
| Forward smash (angled up) | `fsmash_high` | 20-24 | 24 | 80 | 40 | 85 | - | darkness | 66 | 60 | 12 | -27 | charge hold frame 10 |
| Forward smash | `fsmash` | 20-24 | 22 | 70 | 40 | 83 | - | darkness | 66 | 60 | 11 | -28 | charge hold frame 10 |
| Forward smash (angled down) | `fsmash_low` | 20-24 | 20 | 60 | 40 | 80 | - | darkness | 66 | 60 | 10 | -29 | charge hold frame 10 |
| Up smash | `usmash` | 21-23 | 22 | 90/80/Sakurai | 50 | 80 | - |  | 54 | 40 | 11 | -7 | charge hold frame 8 |
|  |  | 26-29 | 19 | 90/80/Sakurai | 40 | 80 | - |  |  |  | 10 | -3 |  |
| Down smash | `dsmash` | 19-22 | 8 | 160 | 0 | 100 | 90/130 |  | 49 | 47 | 5 | -22 | charge hold frame 14 |
|  |  | 29-32 | 14/12 | 120 | 60 | 110 | - |  |  |  | 8 | -9 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (5 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 7-8 | 12 | 55/60/65 | 30 | 100 | - |  | 44 | - | 7 | 25 | 12 | <4, >25 | -5 |  |
|  |  | 20-21 | 12 | Sakurai | 50 | 100 | - |  |  |  | 7 |  |  |  | -5 |  |
| Forward air | `fair` | 14-19 | 17 | Sakurai | 60 | 80 | - |  | 44 | 35 | 9 | 25 | 12 | <7, >33 | -3 |  |
| Back air | `bair` | 10-15 | 16 | Sakurai | 30/10 | 100 | - |  | 35 | 29 | 9 | 25 | 12 | <7, >18 | -3 |  |
| Up air | `uair` | 6-10 | 13/12 | Sakurai | 35 | 100 | - |  | 33 | 30 | 7 | 25 | 12 | <1, >21 | -5 |  |
|  |  | 11-13 | 12/10 | 30 | 30 | 80 | - |  |  |  | 7 |  |  |  | -5 |  |
|  |  | 14-16 | 8/6 | 0 | 20 | 70 | - |  |  |  | 5 |  |  |  | -7 |  |
| Down air | `dair` | 16-20 | 22 | 270 | 50 | 100 | - | electric | 44 | 38 | 11 | 35 | 17 | <4, >35 | -6 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 11-13 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 5 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 9 | 4 | 45 | 45 | 105 | - | - | 18 | 39 |  |
| Back throw | `bthrow` | 9 | 4 | 135 | 30 | 130 | - | - | 20 | 49 |  |
| Up throw | `uthrow` | 7 | 3 | 90 | 70 | 105 | - | - | 15 | 43 |  |
| Down throw | `dthrow` | 7 | 7 | 100 | 75 | 36 | - | - | 20 | 39 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Warlock Punch, ground | `special_n` | 70-72 | 30/32/34 | Sakurai | 30 | 100 | - | darkness | 119 | 117 | 17 | - |  |
| Neutral B: Warlock Punch, air | `special_air_n` | 70-72 | 30/32/34 | Sakurai | 40 | 100 | - | darkness | 119 | 117 | 17 | - |  |
| Side B: Gerudo Dragon, ground, Start | `special_s_start` | 15-79 | 0 | Sakurai | 0 | 0 | - | inert | 79 | - | - | - |  |
| Side B: Gerudo Dragon, ground | `special_s` | 3-7 | 17 | 105 | 60 | 69 | - | darkness | 24 | - | 9 | - |  |
| Side B: Gerudo Dragon, air, Start | `special_air_s_start` | 18-79 | 0 | Sakurai | 0 | 0 | - | inert | 79 | - | - | - |  |
| Side B: Gerudo Dragon, air | `special_air_s` | 3-7 | 16 | 70 | 50 | 65 | - | darkness | 44 | - | 9 | - |  |
| Up B: Dark Dive, ground | `special_hi` | 13, 14-33 | 1 | Sakurai | 0 | 100 | - | grab | 64 | - | 2 | - |  |
| Up B: Dark Dive, air | `special_air_hi` | 13, 14-33 | 1 | Sakurai | 0 | 100 | - | grab | 64 | - | 2 | - |  |
| Up B: Dark Dive, ground, Catch | `special_hi_catch` | 4, 8, 12 | 1 | Sakurai | 60 | 100 | - | electric | 15 | - | 2 | - |  |
| Up B: Dark Dive, ground, Throw | `special_hi_throw` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Down B: Wizard's Foot, ground | `special_lw` | 14-34 | 15 | Sakurai | 60 | 85 | - | darkness | 39 | - | 8 | - |  |
| Down B: Wizard's Foot, ground, End | `special_lw_end` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Down B: Wizard's Foot, air | `special_air_lw` | 15-29 | 14 | 290 | 50 | 80 | - | darkness | 29 | - | 8 | - |  |
| Down B: Wizard's Foot, air, End | `special_air_lw_end` | 2-3 | 12 | 80 | 60 | 20 | - |  | 44 | - | 7 | - |  |
| Down B: Wizard's Foot, ground, EndAir | `special_lw_end_air` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Down B: Wizard's Foot, air, EndAir | `special_air_lw_end_air` | - | - | - | - | - | - | - | 28 | - | - | - |  |
| Up B: Dark Dive, ground, Throw | `special_hi_throw_317` | - | - | - | - | - | - | - | 59 | - | - | - |  |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-20 | - | 32 | 29 |  |
| Roll forward | `roll_forward` | intangible 4-19 | - | 31 | - |  |
| Roll backward | `roll_backward` | intangible 4-19 | - | 31 | - |  |
| Air dodge | `airdodge` | intangible 4-29 | - | 49 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-29 | 19-20, 28-29 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-23 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-19 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-27 | 20-21, 26-27 (6%) | 49 | - |  |
| Getup roll forward (face down) | `getup_roll_forward_facedown` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-25 | - | 35 | - |  |
| Tech in place | `tech_in_place` | intangible 2-20 | - | 26 | - | starts 1 frame late (included) |
| Tech roll forward | `tech_roll_forward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Tech roll backward | `tech_roll_backward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Wall tech | `wall_tech` | intangible 2-14 | - | 26 | - | starts 1 frame late (included) |
| Wall tech jump | `wall_tech_jump` | - | - | 40 | - | starts 1 frame late (included) |
| Ceiling tech | `ceiling_tech` | intangible 2-11 | - | 26 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-49 | - | 58 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-22 | - | 33 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-33 | 37-40 (8%) | 68 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-20 | 24-29 (10%) | 54 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-54 | - | 78 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-24 | - | 48 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-18 | - | 18 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 35 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-11 | - | 11 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 32 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Shield grab | direct | 7 | `grab` |
| Up air | jump | 12 | `uair` |
| Neutral air | jump | 13 | `nair` |
| Up B | jump cancel | 14 | `special_hi` |
| Back air | jump | 16 | `bair` |
| Forward air | jump | 20 | `fair` |
| Down air | jump | 22 | `dair` |
| Up smash | jump cancel | 22 | `usmash` |
| Spot dodge | direct | intangible 2-20 of 32 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 18 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Ganondorf indexed by [The Melee Library](https://www.meleelibrary.com/#ganondorf) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [Ganondorf Is the Best Character in Melee](https://www.youtube.com/watch?v=kZNJhUld7Ek) |  | A VERY serious video describing why Ganondorf is actually the best character in Melee. |
| [2020 Ganondorf Melee Techs Guide](https://www.youtube.com/watch?v=KcW3xHgyjDk&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=15&t=0s) | Third Chair | Video guide on performing useful Ganondorf tech in 2020. |
| Ganondorf Guide of Advanced Techniques | Bizzaro Flame | [Introduction](https://web.archive.org/web/20151231022537/http://showdown.gg/bizzarro-flames-introduction-to-ganondorf-advanced-techniques-guide/) [Part I](https://web.archive.org/web/20160101125420/http://showdown.gg/bizarro-flames-ganondorf-guide-of-advanced-techniques-part-i/) [Part II](https://web.archive.org/web/20160101170210/http://showdown.gg/bizzarro-flames-ganondorf-guide-of-advanced-techniques-part-ii/) [Part III](https://web.archive.org/web/20160101170226/http://showdown.gg/bizzarro-flames-ganondorf-guide-of-advanced-techniques-part-iii/) |
| [How to Wreck *****es with Ganon: A Q&A Thread](http://smashboards.com/threads/how-to-wreck-es-with-ganon-linguini-q-a-thread.215432/) | Linguini | A Q&A thread. Search it and become enlightened. |
| [Techchasing into 2015: Metagame and Theory](http://smashboards.com/threads/techchasing-into-2015-metagame-and-theory.369684/) | Ace | A detailed guide on techchasing as Ganondorf. Includes percents and follow-ups. |
| [Ganon Edgeguarding 101](http://smashboards.com/threads/ganon-edgeguarding-101-open-discussion-whos-next.266671/) | Ace | Ace discusses edgeguarding. Includes sections for a lot of characters. |
| [The Ganon Chaingrabbing Guide](http://smashboards.com/threads/the-ganon-chaingrabbing-guide-update-12-31-06-falco-cg-vids-added.85582/) | Magus |  |
| [Ganon vs.](http://smashboards.com/threads/ganon-vs.242794/) | PaperstSoupCo | Some old advice on matchups. |
| [Ganondorf Knockdown Data](http://smashboards.com/threads/ganondorfs-knockdown-data.360530/) | Locke Robster | What percents Ganondorf’s moves will knock down Fox, Falco, and Captain Falcon |
| [Ganondorf Hitboxes and Frame Data](http://smashboards.com/threads/ganondorf-hitboxes-and-frame-data.303443/page-2#post-16796157) | Stratocaster, Standardtoaster, and SuperDoodleMan |  |
| [On Ganon vs. Falcon](http://smashboards.com/threads/ganon-vs.242794/page-6#post-8170196) | Ace |  |
| [Ledgeguarding with Ganondorf’s Uair](http://smashboards.com/threads/how-to-wreck-es-with-ganon-linguini-q-a-thread.215432/page-482#post-19030142) | Locke Robster |  |
| [Ganondorf's Intangible Ledgedash Options](https://www.youtube.com/watch?v=CCwvV2NBBGc) | Practical TAS |  |
| [Dark Dive 1.00 Glitch](https://www.youtube.com/watch?v=IwYQs-mRS6E) | Simna ibn Sind | A glitch with Ganondorf's Up-B in the 1.00 version of the game. |
| [Ganondorf Chaingrab Guide](https://www.youtube.com/watch?v=1V1zS0WluBk&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=21&t=0s) | Third Chair |  |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Ganondorf (SSBM): https://www.ssbwiki.com/Ganondorf_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Ganondorf_(SSBM)/Up_aerial , /Down_aerial ,
  /Forward_aerial , /Back_aerial , /Neutral_aerial , /Forward_tilt , /Neutral_attack ,
  /Down_throw , /Up_throw , /Grab , /Side_special , /Up_special , /Up_smash ,
  /Down_smash
- SSBWiki technique pages: https://www.ssbwiki.com/Wizard's_Foot ,
  https://www.ssbwiki.com/Dark_Dive , https://www.ssbwiki.com/Chain_grab ,
  https://www.ssbwiki.com/Ledgestall , https://www.ssbwiki.com/Ledgedash ,
  https://www.ssbwiki.com/Moonwalk , https://www.ssbwiki.com/Waveshine ,
  https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Melee Library, "The Ganon Chaingrabbing Guide" (Magus), via web.archive.org:
  http://smashboards.com/threads/the-ganon-chaingrabbing-guide-update-12-31-06-falco-cg-vids-added.85582/
- Melee Library, "Techchasing into 2015: Metagame and Theory" (Ace), via web.archive.org:
  http://smashboards.com/threads/techchasing-into-2015-metagame-and-theory.369684/
- Melee Library, "Ganon Edgeguarding 101" (Ace), via web.archive.org:
  http://smashboards.com/threads/ganon-edgeguarding-101-open-discussion-whos-next.266671/
- Melee Library, "On Ganon vs. Falcon" / "Ganon vs." thread page 6, via web.archive.org:
  http://smashboards.com/threads/ganon-vs.242794/page-6
- Melee Library, "Ganondorf Knockdown Data" (Locke Robster), via web.archive.org (only
  later replies were retrievable, not the data table):
  http://smashboards.com/threads/ganondorfs-knockdown-data.360530/
- Melee Library, "Ganondorf Guide of Advanced Techniques" (Bizzarro Flame), parts I-III:
  https://web.archive.org/web/20160101125420/http://showdown.gg/bizarro-flames-ganondorf-guide-of-advanced-techniques-part-i/
- Melee Library (Fox section), "Chaingrab Info" thread (KirbyKaze), via web.archive.org
- Frame data dump: `Ganondorf.json`
