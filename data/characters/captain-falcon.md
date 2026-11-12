---
schema: melee-character/v1
id: captain-falcon
name: Captain Falcon
aliases: [Falcon, C. Falcon, Cpt. Falcon, Douglas Jay Falcon]
tier: "A (6th of 26), 2021 tier list"
archetype: [rushdown, fastfaller, heavy, punish-heavy, tech-chase, combo-food]
related: [ganondorf]
summary: Captain Falcon uses the fastest ground speed in the game to bait and whiff punish, then converts a grab, stomp or neutral air into tech chases and aerial strings that end in the knee.
key_tech: [reaction-tech-chase, throw-regrab-fastfallers, stomp-knee, weak-knee-conversion, gentleman, raptor-boost-tech-chase, moonwalk-edgeguard, up-air-out-of-shield, falcon-kick-jump-restore, ledgehop-stall, falcon-dive-reverse, sacred-combo]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlCa.dat
framedata: ../framedata/captain-falcon.json
code: src/melee/ft/kinds/ftCaptain
specials:
  neutral_b: "Falcon Punch"
  side_b: "Raptor Boost"
  up_b: "Falcon Dive"
  down_b: "Falcon Kick"
attributes:
  weight: 104
  gravity: 0.13
  fall_speed: 2.9
  fast_fall_speed: 3.5
  jump_squat: 4
  jumps: 2
  walk_speed: 0.85
  dash_speed: 2
  run_speed: 2.3
  traction: 0.08
  air_speed: 1.12
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [3, 16, 2]
  jab2: [5, 19, 3]
  jab3: [6, 23, 8]
  rapid_jab_start: [null, 6, 0]
  rapid_jab_loop: [4, 40, 1]
  rapid_jab_end: [null, 9, 0]
  dash_attack: [7, 38, 10]
  ftilt_high: [9, 30, 12]
  ftilt_mid_high: [9, 30, 12]
  ftilt: [9, 30, 11]
  ftilt_mid_low: [9, 30, 11]
  ftilt_low: [9, 30, 11]
  utilt: [17, 38, 13]
  dtilt: [10, 35, 12]
  fsmash_high: [18, 60, 21]
  fsmash: [18, 60, 20]
  fsmash_low: [18, 60, 19]
  usmash: [21, 40, 14]
  dsmash: [19, 45, 18]
  nair: [7, 45, 7]
  fair: [14, 36, 18]
  bair: [10, 29, 14]
  uair: [6, 30, 13]
  dair: [16, 38, 16]
  grab: [7, 31, 0]
  dash_grab: [11, 41, 0]
  pummel: [5, 25, 3]
  fthrow: [11, 40, 4]
  bthrow: [12, 50, 4]
  uthrow: [11, 44, 3]
  dthrow: [null, 40, 7]
  special_n: [52, 65, 27]
  special_air_n: [52, 100, 27]
  special_s_start: [15, 80, 0]
  special_s: [3, 25, 7]
  special_air_s_start: [18, 80, 0]
  special_air_s: [3, 45, 7]
  special_hi: [13, 65, 1]
  special_air_hi: [13, 65, 1]
  special_hi_catch: [3, 16, 5]
  special_hi_throw: [null, 60, 12]
  special_lw: [14, 40, 15]
  special_lw_end: [null, 30, 0]
  special_air_lw: [15, 30, 15]
  special_air_lw_end: [2, 45, 9]
  special_lw_end_air: [null, 30, 0]
  special_air_lw_end_air: [null, 29, 0]
  special_hi_throw_317: [null, 60, 0]
oos:  # option: frame the hitbox is out
  grab: 7
  uair: 10
  nair: 11
  bair: 14
  special_hi: 14
  fair: 18
  dair: 20
  usmash: 22
resources: 40
# generated: end
---

# Captain Falcon

<!-- GENERATED:attributes -->
## Attributes

Read from `PlCa.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 104 |
| Gravity | 0.13 |
| Terminal fall speed | 2.9 |
| Fast-fall speed | 3.5 |
| Jump squat (frames before airborne) | 4 |
| Full hop / short hop initial Y speed | 3.1 / 1.9 |
| Air jump Y multiplier | 0.9 |
| Jumps | 2 |
| Walk max speed | 0.85 |
| Dash initial speed / run max speed | 2 / 2.3 |
| Ground friction (traction) | 0.08 |
| Air max horizontal speed | 1.12 |
| Air acceleration (base + stick) | 0.02 + 0.04 |
| Air friction | 0.01 |
| Normal landing lag | 4 |
| Shield size | 15 |
<!-- /GENERATED:attributes -->

## Overview

Captain Falcon is a heavy fastfaller (a character with high fall speed) with the fastest
run in the game: weight 104, run speed 2.3, fall speed 2.9 (second fastest), fast-fall
speed 3.5, 4-frame jump squat (the grounded frames before a jump leaves the floor)
[wiki:Captain_Falcon_(SSBM)]. He ranks 6th on the 2021 tier list
[wiki:Captain_Falcon_(SSBM)]. He has no projectile. He wins neutral with movement: the
longest [dash dance](../techniques/dash-dance.md) in the game baits attacks, and he
punishes with grab, nair, up air or dair (the stomp) [wiki:Captain_Falcon_(SSBM)]
[lib:Extensive Captain Falcon Guide 2016]. His punishes are among the most damaging: up
throw and down throw lead to [tech chases](../techniques/tech-chase.md) on fastfallers and
to aerial strings on everyone, and nearly all of them end in the clean fair (the Knee
Smash, "knee"), 18% at a 32-degree angle, which kills from about 60% offstage
[wiki:Captain_Falcon_(SSBM)/Forward_aerial] [fd]. He dies to edgeguards (his up B cannot
hurt or grab anyone holding the ledge) and to chain grabs and juggles, since he is a large,
fast-falling target [wiki:Captain_Falcon_(SSBM)]. He is unforgiving to play: weak matchup
knowledge or fundamentals are punished heavily [lib:Extensive Captain Falcon Guide 2016].

## Strengths and weaknesses

- **Strengths:**
  - Fastest dash and run, long dash dance, high air speed
    [wiki:Captain_Falcon_(SSBM)].
  - Knee: one of the strongest and most comboed-into kill moves; +2 on shield when the
    clean hit is L-cancelled [lib:Extensive Captain Falcon Guide 2016]
    [wiki:Knee_Smash].
  - Stomp (dair): 16% meteor with high hitstun, not crouch-cancellable in practice, leads
    to knee [wiki:Captain_Falcon_(SSBM)/Down_aerial]
    [lib:Extensive Captain Falcon Guide 2016].
  - Throw game: down throw is useful against every character at some percent; up throw
    regrabs fastfallers [wiki:Captain_Falcon_(SSBM)/Down_throw]
    [lib:Uthrow Followups on Falco].
  - Up air: fastest aerial (frame 6), 15/7 frames of landing lag, combos into itself and
    knee [fd] [wiki:Captain_Falcon_(SSBM)/Up_aerial].
  - Heavy and fast falling: survives vertical kill moves very long
    [wiki:Captain_Falcon_(SSBM)].
  - Far-reaching offstage edgeguards thanks to air speed; good moonwalk
    [wiki:Moonwalk].
- **Weaknesses:**
  - Recovery: up B (Falcon Dive) is slow, has no hitbox other than a grab, cannot grab
    opponents on the ledge; side B does not grab ledges and leaves him helpless
    [wiki:Captain_Falcon_(SSBM)/Up_special] [wiki:Raptor_Boost].
  - Combo food: chain grabbed by [Peach](peach.md), [Pikachu](pikachu.md) and others;
    juggled by up tilts and up airs [wiki:Captain_Falcon_(SSBM)].
  - No projectile; many attacks start slowly (knee frame 14, stomp frame 16, grab range
    sixth shortest) [fd] [wiki:Captain_Falcon_(SSBM)].
  - Nair's first hit trades badly and can be crouch cancelled (holding down to reduce
    knockback) or DI'd so the second hit misses [lib:Extensive Captain Falcon Guide 2016].
  - Poor out-of-shield game compared with the space animals and Sheik.

## Character tech

### Reaction tech chase

- **id:** `reaction-tech-chase`
- **What:** After a throw or knockdown, standing at the right distance and reacting to
  the opponent's tech choice (in place, toward, away, missed) with grab, knee, stomp or
  jab instead of guessing [lib:Techchasing Like a Man: Complete Breakdown].
- **Inputs:** throw, wavedash or dash-wavedash to a spot just outside the opponent's
  shine range but inside standing-grab range, watch the tech animation, then: tech in
  place -> standing grab (Z only); tech away -> dash, instant jump, knee or stomp; tech
  behind -> jump, pull-back stomp; missed tech -> jab reset or grab.
- **Timing:** Counted from the first frame of a space animal's tech
  [lib:Techchasing Like a Man: Complete Breakdown]: the options become visually distinct
  from about frame 2-3 (tech in place looks like a split; rolls have the legs together,
  and tech away lacks the blue flash); frame 17 is the last frame to jab a missed tech;
  frame 18 is the last frame to grab a tech in place; frame 19 is the last frame to
  start dash forward, instant jump, instant stomp against tech away; frame 20 the last
  to jump for a pull-back stomp on the roll behind; frame 21 the last for dash, instant
  knee on tech away. The author budgets about 15 frames for human reaction. The clean
  knee is only active for 3 frames (14-16) [fd].
- **Used for:** Falcon's main punish on [Fox](fox.md), [Falco](falco.md) and
  [Sheik](sheik.md); every correct read is another throw or a kill.
- **Common errors:** Standing too close (shined on tech in place) or too far (cannot
  reach tech away); jump-cancel grabbing when a plain Z would be on time; committing
  before seeing the tech.
- **Drill idea:** Falcon holds CPU Fox/Falco in grab at set percent; CPU DIs and techs
  at random; success when any hit or grab lands before the CPU is actionable.

### Throw regrabs on fastfallers

- **id:** `throw-regrab-fastfallers`
- **What:** Up throw (and at low percent down throw) leaves Fox, Falco and Falcon falling
  straight back toward him, so he can regrab or hit them before or as they land. A
  pseudo [chain grab](../techniques/chain-grab.md) [wiki:Tech-chase].
- **Inputs:** grab, up throw, then standing regrab, turn regrab, or turn dash
  jump-cancel regrab depending on DI; short hop up air, short hop knee or fsmash at
  higher percent.
- **Timing:** Measured against Falco, percent before the throw
  [lib:Uthrow Followups on Falco]: regrab works with no DI at 40-126%, with DI slightly
  behind at 32-123%, with DI straight behind at 40-139% (turnaround regrab, then turn
  dash JC regrab from 70%). Short hop up air is added from about 51% and short hop knee
  and fsmash from 86% for no DI. Against DI straight away almost nothing is guaranteed:
  a run JC regrab only at 130-135% and knee from about 130%; Falco techs or jumps out.
  Falco can jump out of up throw at about 90% (70% if frame-perfect) and Fox at about
  85% (65%) [lib:Techchasing Like a Man: Complete Breakdown]. Down throw is the better
  tech-chase throw (more frames to react) until about 50%, up throw after that
  [lib:Techchasing Like a Man: Complete Breakdown].
- **Used for:** Guaranteed damage whenever the opponent misses the DI; from 40% with
  missed DI the follow-ups are essentially guaranteed [lib:Uthrow Followups on Falco].
- **Common errors:** Not turning around for DI behind; dash grab (too slow) instead of
  JC grab; attempting a regrab on DI away instead of tech chasing.
- **Drill idea:** CPU Falco/Fox at a random percent 30-130% with random DI; player must
  pick the correct guaranteed follow-up from the table or switch to a tech chase on DI
  away.

### Stomp to knee

- **id:** `stomp-knee`
- **What:** Dair on a grounded or low opponent pops them up with enough hitstun for a
  jump into clean fair. The standard kill confirm
  [wiki:Captain_Falcon_(SSBM)/Down_aerial].
- **Inputs:** short hop (or falling) dair, fast fall, L-cancel, jump, fair so that frames
  14-16 of the knee overlap the opponent.
- **Timing:** Dair hitbox frames 16-20, 16%, landing lag 24 frames or 12 with
  [L-cancel](../techniques/l-cancel.md); knee clean hit frames 14-16, late hit 17-30 [fd].
  Tech-chase discussion treats stomp into knee as a kill on space animals once they are
  at a high enough percent [lib:Techchasing Like a Man: Complete Breakdown]; exact
  percent: Unknown.
- **Used for:** Kills from stray hits, tech-chase reads, platform tech chases (double
  jump dair) and punishes on shields that drop.
- **Common errors:** Missed L-cancel (24 frames [fd]); knee too early or late (soft knee
  6% instead of 18%); opponent DIs the stomp or techs the ground bounce.
- **Drill idea:** CPU stands or shields-then-drops at 60-100%; player must hit dair and
  then a clean knee as a true combo.

### Weak knee and up air conversions

- **id:** `weak-knee-conversion`
- **What:** Using low-knockback aerial hits (late "soft" knee, up air, first hit of nair)
  to carry the opponent and set up the clean knee [wiki:Knee_Smash].
- **Inputs:** hit with the late part of fair or with up air, land with L-cancel (or stay
  airborne and double jump), then up air again or clean knee.
- **Timing:** Late knee is frames 17-30, 6%, base knockback 35 with growth 80 in NTSC;
  PAL halves the damage and removes the soft knee to hard knee link
  [fd] [wiki:Knee_Smash]. Up air is frames 6-13 with 7 frames of L-cancelled landing lag
  [fd]. Nair hits on frames 7-12 and 20-29; the first hit has set knockback (40) that
  normally leads into the second [fd].
- **Used for:** Combos on the whole cast; "weak knee into hard knee" and "weak knee into
  up air" are named as the most common [wiki:Knee_Smash]. Offstage, a weak knee often
  leads to a free up air or strong knee [lib:Extensive Captain Falcon Guide 2016].
- **Common errors:** Floaty opponents SDI (tap the stick during hitlag) the first nair
  hit up so the second misses and they counter-attack
  [lib:Extensive Captain Falcon Guide 2016]; going for knee when DI away puts the
  opponent out of reach.
- **Drill idea:** CPU Marth/Sheik at 40-80% launched by down throw with random DI;
  success if an up air or weak knee is followed by a clean knee in one combo.

### Gentleman

- **id:** `gentleman`
- **What:** The three-hit jab (punch, punch, knee) ended without going into the rapid-jab
  finisher. The third hit knocks away with little lag [wiki:Gentleman].
- **Inputs (NTSC):** Any method that "drops" one button toggle: (a) press A, A, then hold
  the third press through hitlag; (b) release the first A during the hitlag of jab 1
  (hold the first press about 3-6 frames); (c) let each jab animation finish, or walk out
  of one, before the next press; (d) use Z for the third hit; (e) hold down after the
  first jab [wiki:Gentleman] [lib:Frame Data: The Way Gentleman Works]
  [lib:Extensive Captain Falcon Guide 2016].
- **Timing:** The rapid jabs start when the game counts 4 press/release toggles of A
  during the first hits; toggles made during hitlag or during idle time after a hit do
  not count, and the first press does not count. PAL raises the count to 7, which makes
  the gentleman automatic [wiki:Gentleman]. Jab 1 hits on frames 3-5, jab 2 on frames
  4-6 of its own animation, the knee on frames 5-8 of its animation for 8% [fd]. Methods
  (a), (b), (d) and (e) need the jabs to hit; on whiff only waiting for the animation to
  end is safe [wiki:Gentleman].
- **Used for:** A fast close-range option after aerials on shield; knocks down at higher
  percent for a tech chase or edgeguard; weak at low percent because it can be crouch
  cancelled [lib:Extensive Captain Falcon Guide 2016]. Delaying between hits or
  substituting a grab after jab 1 or 2 is a mixup
  [lib:Extensive Captain Falcon Guide 2016].
- **Common errors:** Mashing A (rapid jabs come out, very punishable); jab whiff with a
  hitlag-dependent method.
- **Drill idea:** CPU stands or shields; success if the third hit comes out and no rapid
  jab action state is entered, N times in a row; variation where jabs whiff.

### Raptor Boost tech chase

- **id:** `raptor-boost-tech-chase`
- **What:** Using side B (Raptor Boost) to cover tech options: its dash travels far and
  the uppercut launches straight up for an aerial follow-up [wiki:Raptor_Boost].
- **Inputs:** side B toward the expected landing spot; on hit, jump into up air or knee.
- **Timing:** Grounded search hitbox from frame 15; the dash can connect until about
  frame 33; on contact the uppercut hits on frames 3-7 of its own animation for 7% at 90
  degrees [wiki:Captain_Falcon_(SSBM)/Side_special] [fd]. On whiff he falls over with
  about 3/4 of a second of lag [wiki:Captain_Falcon_(SSBM)/Side_special]. During
  startup he steps back, which can make an attack or grab whiff
  [wiki:Captain_Falcon_(SSBM)/Side_special].
- **Used for:** Covering tech in place and one roll at once; from an edge, side B toward
  centre covers nearly every option, and if the opponent techs the other way the move
  still ends in the uppercut animation, keeping him safe
  [lib:Extensive Captain Falcon Guide 2016]. After low-mid percent it is sometimes the
  best tech-chase punish because it cannot be crouch cancelled there
  [lib:Extensive Captain Falcon Guide 2016]. Good against Sheik, whose tech in place and
  tech toward look alike [wiki:Tech-chase]. In NTSC the search hitbox also disables
  projectiles it touches [wiki:Raptor_Boost].
- **Common errors:** Whiff (full punish); using it offstage (helpless, no ledge grab).
- **Drill idea:** CPU Sheik/Fox knocked down near an edge with random tech; success if
  Raptor Boost connects and an aerial follows.

### Moonwalk edgeguard

- **id:** `moonwalk-edgeguard`
- **What:** [Moonwalking](../techniques/moonwalk.md) backward off the stage so Falcon
  slides out facing the stage with his double jump intact, then hitting with bair, up
  air or knee [wiki:Moonwalk].
- **Inputs:** dash forward (away from the ledge), then roll the stick through the lower
  back diagonal for at least 2 frames and hold straight back; slide off the edge; aerial;
  double jump back.
- **Timing:** Tilting back too fast gives a dash back instead; the stick must be lightly
  back for 2 or more frames before fully back. Prior velocity in the moonwalk direction
  (walk, wavedash, an earlier moonwalk) lengthens it. Falcon has the longest moonwalk
  [wiki:Moonwalk].
- **Used for:** Reaching far offstage for an edgeguard while keeping the double jump for
  the return [wiki:Moonwalk].
- **Common errors:** Dash back instead of moonwalk; sliding off without an aerial;
  self-destruct.
- **Drill idea:** Falcon starts near the ledge facing centre; CPU recovers from far;
  success if Falcon leaves the stage in a moonwalk state, hits an aerial and returns.

### Up air out of shield

- **id:** `up-air-out-of-shield`
- **What:** Instant short hop up air as the main [out of shield](../techniques/out-of-shield.md)
  and close-range option [lib:Extensive Captain Falcon Guide 2016].
- **Inputs:** from shield: jump, up air immediately, L-cancel.
- **Timing:** Up air hitbox from frame 6 [fd] after a 4-frame jump squat
  [wiki:Captain_Falcon_(SSBM)], so it hits on frame 10 after shield stun. Its hitbox
  starts high and can miss short or ducking characters
  [lib:Extensive Captain Falcon Guide 2016].
- **Used for:** Punishing moves on shield from tall characters (for example Sheik's
  ftilt) and winning close SHFFL exchanges where nair's first hit would trade
  [lib:Extensive Captain Falcon Guide 2016].
- **Common errors:** Whiff over a low hurtbox; missed L-cancel (15 frames [fd]).
- **Drill idea:** CPU Sheik/Marth hits Falcon's shield with a tilt; success if up air
  hits within N frames of shield stun ending.

### Falcon Kick jump restore

- **id:** `falcon-kick-jump-restore`
- **What:** An aerial down B (Falcon Kick) that ends in the air gives back the double
  jump [wiki:Captain_Falcon_(SSBM)/Down_special].
- **Inputs:** after using the double jump, down B in the air high enough that it ends
  before landing, then double jump again and up B.
- **Timing:** Aerial Falcon Kick: hitbox frames 15-29, animation about 58-59 frames,
  travels diagonally down a long way [wiki:Captain_Falcon_(SSBM)/Down_special].
- **Used for:** Extending horizontal recovery when launched high; it forces a low
  recovery afterwards [wiki:Captain_Falcon_(SSBM)].
- **Common errors:** Using it too low (dies before the move ends); landing on stage in
  the lag; doing it where an edgeguarder can hit him out of it
  [lib:On Ganon vs. Falcon].
- **Drill idea:** Falcon launched high and far with no double jump; success if he
  reaches the ledge.

### Ledgehop stall

- **id:** `ledgehop-stall`
- **What:** Dropping from the ledge, fast falling and double jumping back to regrab
  within the regrab lockout, keeping continuous ledge intangibility
  [wiki:Ledgestall].
- **Inputs:** from ledge: stick down (fast fall), jump, drift back to the ledge. Variant:
  jump immediately after dropping, fast fall after the jump's peak (harder).
- **Timing:** Earliest ledge drop is frame 9 of the grab with 29 intangible frames left;
  the ledge cannot be regrabbed for 29 frames, and Falcon's fast fall and low double
  jump fit the cycle inside that time [wiki:Ledgestall].
- **Used for:** Edgehogging through a recovery; waiting on the ledge safely.
- **Common errors:** Holding down too long (no regrab); jumping onto the stage.
- **Drill idea:** Count consecutive regrabs with no vulnerable frame.

### Reverse and drifted Falcon Dive

- **id:** `falcon-dive-reverse`
- **What:** Turning up B around during startup and steering it, so Falcon can recover
  facing away, grab the ledge backwards or grab an edgeguarder
  [wiki:Captain_Falcon_(SSBM)/Up_special].
- **Inputs:** up B, then hold the opposite direction before the move activates; hold a
  direction during the rise to drift.
- **Timing:** The reverse input is accepted until about frame 13; the grab box appears
  on frame 13 (with a large disjointed box against grounded opponents on that frame) and
  lasts through frame 33-39 depending on source; total 64 frames
  [wiki:Captain_Falcon_(SSBM)/Up_special] [fd]. Falcon can also drift during the
  startup [lib:You Can Move during the Startup of Captain Falcon's Up-B] (card title
  only).
- **Used for:** Recovery mixups; grabbing the ledge while facing away (for example from
  under Battlefield); a surprise hit on shielding opponents on platforms
  [lib:Extensive Captain Falcon Guide 2016]. A successful grab lets him up B again
  [wiki:Captain_Falcon_(SSBM)].
- **Common errors:** Grabbing an opponent at low percent near the stage: his lag exceeds
  their hitstun [wiki:Captain_Falcon_(SSBM)/Up_special]; the release hit can be teched
  on the stage wall [wiki:Falcon_Dive].
- **Drill idea:** Recover from below with a CPU on the ledge or on stage; success on
  ledge grab or safe landing.

### Sacred combo

- **id:** `sacred-combo`
- **What:** Clean knee followed by an aerial neutral B (Falcon Punch) before hitstun
  ends [wiki:Captain_Falcon_(SSBM)].
- **Inputs:** knee, double jump, neutral B in the air.
- **Timing:** Falcon Punch hits on frames 52-56 [fd]; possible "occasionally" when a
  clean knee lands at about 60% [wiki:Knee_Smash]. Depends on the opponent's DI.
- **Used for:** Style; not a practical conversion.
- **Common errors:** Jumping too far and self-destructing [wiki:Captain_Falcon_(SSBM)].
- **Drill idea:** CPU with no DI at 60%; success if both hits register in one combo.

## Neutral game

- **Movement is the main tool.** Dash dance at the edge of the opponent's range, run
  away from a committed aerial and come back with grab, nair or up air
  [lib:Extensive Captain Falcon Guide 2016].
- **Nair** (frames 7-12 and 20-29 [fd]): long, disjointed, best at mid range, with
  mixups (one hit or two, fast fall or not, cross-up or fade back). Bad at close range
  because the first hit trades poorly [lib:Extensive Captain Falcon Guide 2016].
- **Instant up air** at close range and out of shield
  [lib:Extensive Captain Falcon Guide 2016].
- **Stomp** on shield or on a dash-dancing opponent: it cannot be crouch cancelled and
  countered, deals heavy shield damage and stun, and can be done late in a short hop;
  facing away uses the larger rear hitbox [lib:Extensive Captain Falcon Guide 2016]
  [wiki:Captain_Falcon_(SSBM)/Down_aerial].
- **Knee** on shield is +2 when clean and removes nearly a quarter of a shield
  [lib:Extensive Captain Falcon Guide 2016] [wiki:Knee_Smash].
- **Retreating bair** (frames 10-17 [fd]) against opponents who chase him.
- **Grab:** standing grab active frames 7-8, dash grab frames 11-12
  [wiki:Captain_Falcon_(SSBM)/Grab]; jump-cancel grab out of a run for range.
- **Jab / gentleman** after aerials on shield, with delays and grab mixups
  [lib:Extensive Captain Falcon Guide 2016].
- **Dtilt** (frame 10) after crouch cancelling a move, popping the opponent up at higher
  percent [lib:Extensive Captain Falcon Guide 2016].
- **Raptor Boost** occasionally, to catch shield drops, jumps out of shield and wavedash
  back, and to pass through projectiles (NTSC) [lib:Extensive Captain Falcon Guide 2016]
  [wiki:Raptor_Boost].

## Punish game

Falcon turns one opening into a stock more often than most characters. On fastfallers
the loop is throw, tech chase, throw, then stomp or knee. On mid-weights and floaties it
is down throw or up throw into up air and nair strings, finishing with knee toward the
nearest blastzone. Offstage he continues with knee, bair, up air and dair.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| Up throw | Falco | 40-126% (no DI), 32-123% (DI slightly behind), 40-139% (DI behind) | Regrab | Pre-throw percent; turn or turn-dash JC grab for DI behind | [lib:Uthrow Followups on Falco] |
| Up throw | Falco | from about 51% (no DI / slightly behind) | Short hop up air | | [lib:Uthrow Followups on Falco] |
| Up throw | Falco | 86-126% (no DI) | Short hop knee or fsmash | Knee stays guaranteed to 150% for no DI | [lib:Uthrow Followups on Falco] |
| Up throw | Falco, Fox | any, DI straight away | Tech chase | Knee only connects from about 130% | [lib:Uthrow Followups on Falco] |
| Down throw | Fox, Falco | 0% to about 50% | Reaction tech chase | More reaction frames than up throw below 50% | [lib:Techchasing Like a Man: Complete Breakdown] |
| Down throw | Mid-weights, floaties | varies | Nair, up air or knee | "Direct combos" by percent and DI | [wiki:Captain_Falcon_(SSBM)/Down_throw] |
| Down throw | Ganondorf and other floatier characters | low-mid | Regrab (chain grab) | Wiki names Ganondorf as an example | [wiki:Captain_Falcon_(SSBM)] |
| Stomp (grounded target) | Most | mid-high | Knee | Kill confirm | [wiki:Captain_Falcon_(SSBM)/Down_aerial] |
| Stomp | Most | low | Stomp again, nair, up air | | [wiki:Captain_Falcon_(SSBM)/Down_aerial] |
| Nair | Most | low-mid | Grab, up air, nair, knee | Two-hit starter | [wiki:Captain_Falcon_(SSBM)] |
| Up air | Most | low-mid | Up air, knee | | [wiki:Captain_Falcon_(SSBM)/Up_aerial] |
| Weak knee | All | varies | Clean knee or up air | NTSC only for the knee link | [wiki:Knee_Smash] |
| Raptor Boost | Most | low-mid | Up air or knee | Launches straight up | [wiki:Raptor_Boost] |
| Dtilt | Fox, Falco | medium | Regrab; or nair, knee, up air | | [wiki:Captain_Falcon_(SSBM)] |
| Up smash | Many | varies | Knee or up air | First hit can be ASDI'd down to avoid the second | [wiki:Captain_Falcon_(SSBM)/Up_smash] |
| Gentleman | Most | higher percent | Tech chase or edgeguard | Knocks down | [lib:Extensive Captain Falcon Guide 2016] |

### Chain grabs and tech chases

- **Fastfallers (Fox, Falco, Falcon):** up throw regrabs and tech chases as described
  under "Throw regrabs on fastfallers". The victim's correct DI on up throw is straight
  away, followed by a tech or jump [lib:Uthrow Followups on Falco].
- **Throw choice by percent (damage after the throw):** on Falco, down throw gives a
  tech-chase situation at any percent, fthrow from 38%, bthrow from 49%, and up throw
  from 0% until he can jump out at about 90%; Fox is the same with up throw to about 85%
  [lib:Techchasing Like a Man: Complete Breakdown] (data posted by a thread
  contributor, not the author).
- **Sheik:** tech chase from down throw; her tech in place and tech toward are hard to
  tell apart, so use a read or a move that covers both, such as Raptor Boost
  [wiki:Tech-chase].
- **Mechanical coverage:** time a landing knee, bair or up air on the first vulnerable
  frame of tech in place, then dash JC grab the rolls; knee's L-cancelled lag is 9
  frames, stomp's 12 [lib:Techchasing Like a Man: Complete Breakdown] [fd].
- **Missed tech:** jab reset (see [jab reset](../techniques/jab-reset.md)); a jab that
  hits early in the missed-tech window still leaves time to cover the forced getup
  [lib:Techchasing Like a Man: Complete Breakdown].
- **Platforms:** an empty hop under the platform then up air on tech in place, or
  fast fall and grab a roll; double jump dair for a harder punish
  [lib:Techchasing Like a Man: Complete Breakdown].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Knee (clean fair) | Most | under 100% on most stages; from about 60% offstage | 32-degree angle; frames 14-16 only | [wiki:Knee_Smash] [wiki:Captain_Falcon_(SSBM)/Forward_aerial] |
| Fsmash | Most | about 100% uncharged; as early as 80% from centre on a hard read | Hits frame 18, very punishable | [wiki:Captain_Falcon_(SSBM)] [wiki:Captain_Falcon_(SSBM)/Forward_smash] |
| Stomp (dair) | Offstage opponents | low percent | Meteor; torso hitbox is a true spike | [wiki:Captain_Falcon_(SSBM)/Down_aerial] |
| Bair (clean) | Most | high percent | 14%, frames 10-13 [fd]; mostly an edgeguard move | [wiki:Captain_Falcon_(SSBM)/Back_aerial] |
| Up air | Offstage opponents | any (gimp) | Late hit sends at 0-30 degrees | [wiki:Captain_Falcon_(SSBM)/Up_aerial] |
| Down smash | Most | Unknown | Front hit 18%, hits frame 19 [fd] | [wiki:Captain_Falcon_(SSBM)] |
| Falcon Punch | Any | Unknown (27%) | Frame 52; hard reads only | [wiki:Captain_Falcon_(SSBM)/Neutral_special] |

- **Kill setups:** stomp to knee; up air to knee; weak knee to knee; throw to knee at
  high percent (on Falco from 86% with no DI [lib:Uthrow Followups on Falco]);
  Raptor Boost to knee [wiki:Raptor_Boost]; dtilt to knee after a crouch cancel
  [lib:Extensive Captain Falcon Guide 2016]; gentleman knockdown into a tech-chase knee.
- **Edgeguards:** run-off or moonwalk knee and bair; weak knee to push the opponent
  further out, then up air or knee [lib:Extensive Captain Falcon Guide 2016]; reverse up
  air's late hit as a gimp [wiki:Captain_Falcon_(SSBM)/Up_aerial]; stomp below the
  ledge; dtilt at the ledge against Fox/Falco side B [wiki:Captain_Falcon_(SSBM)]; up
  tilt, whose heel reaches below the ledge [wiki:Captain_Falcon_(SSBM)]; edgehog with a
  ledgehop stall. Fthrow and bthrow near the ledge set these up
  [wiki:Captain_Falcon_(SSBM)].

## Recovery

- **Options:**
  - Double jump and air drift (high air speed) [wiki:Captain_Falcon_(SSBM)].
  - Up B (Falcon Dive): rises diagonally, steerable, reversible until about frame 13;
    only a grab box (frames 13 onward), no damaging hitbox; grabs the ledge even when
    facing away; total 64 frames [wiki:Captain_Falcon_(SSBM)/Up_special].
  - Down B in the air (Falcon Kick): restores the double jump if it ends in the air;
    travels far down [wiki:Captain_Falcon_(SSBM)/Down_special].
  - Side B in the air: more horizontal distance than an airdodge, but no ledge grab,
    always helpless afterwards, and it stops dead if it touches anyone
    [wiki:Captain_Falcon_(SSBM)/Side_special].
  - Airdodge to the stage or a platform; wall jump [wiki:Captain_Falcon_(SSBM)].
- **Mixups:** drift toward the stage and choose late between landing on stage, a
  platform or the ledge; save the double jump; up B early and high versus late and to
  the ledge; reverse up B; go low, then double jump and up B.
- **Weaknesses:** Up B is slow and predictable, loses to any hitbox and to an opponent
  holding the ledge (he must then land on stage with lag). Fast fall speed shortens
  every option. Falcon Kick puts him very low [wiki:Captain_Falcon_(SSBM)].

### Edgeguarding Captain Falcon

- **Typical situation:** Falcon above ledge height drifting in with or without a double
  jump. He must pick ledge or stage. A long-lasting hitbox that covers both wins:
  Fox's fsmash and Falco's fsmash are named for exactly this
  [wiki:Fox_(SSBM)/Forward_smash] [wiki:Falco_(SSBM)/Forward_smash].
- **Hold the ledge** when he is below it: up B cannot grab or hit a ledge-hanging
  opponent [wiki:Captain_Falcon_(SSBM)/Up_special]; he lands on stage in lag or falls.
  Refresh intangibility with a ledge stall.
- **Hit the up B:** it has no hitbox, so bairs, spikes and semi-spikes all beat it.
  Ganondorf's reverse up air beats his ledge grab attempt "in almost any situation"
  [lib:On Ganon vs. Falcon].
- **Remove the double jump first:** Falco's lasers from the ledge repeatedly knock him
  out of his jump and force another recovery attempt [wiki:Blaster_(Falco)]; Fox's
  fthrow near the ledge creates a 50:50 because it is equally fast on heavy characters
  [wiki:Fox_(SSBM)/Forward_throw].
- **Punish the Falcon Kick:** if he uses down B to regain his jump, hit him before it
  ends [lib:On Ganon vs. Falcon].
- **Watch for the up B grab:** an edgeguarder who is grabbed below stage level gets stage
  spiked unless they wall tech the release hit [wiki:Dark_Dive] (described for the
  clone move) [wiki:Falcon_Dive].
- **CPU-as-Falcon recovery policy:** high: drift, airdodge or land on a platform; ledge
  height with jump: double jump to ledge or aerial onto stage; below: up B (sometimes
  reversed) aimed at the ledge; high and far without a jump: Falcon Kick, then double
  jump and up B.

## Defense and out of shield

- **Out of shield:** instant up air (frame 10 after shield stun) [fd]
  [lib:Extensive Captain Falcon Guide 2016]; shield grab (frame 7
  [wiki:Captain_Falcon_(SSBM)/Grab]); nair (frame 11 [fd]); up B, whose frame-13 grab box
  has unusual horizontal reach on grounded opponents
  [wiki:Captain_Falcon_(SSBM)/Up_special]; wavedash out; roll.
- **Crouch cancel:** his weight makes it strong; he can crouch cancel Fox's nair until
  above 80% [wiki:Fox_(SSBM)/Neutral_aerial] and answer with dtilt, grab or jab
  [lib:Extensive Captain Falcon Guide 2016].
- **Combo escapes:** no fast escape move. He relies on DI, SDI, double jump and teching.
  Against other Falcons and Ganondorf at low percent, DI away from the up air strings
  rather than up [lib:On Ganon vs. Falcon] (written for Ganondorf, same combo).
- **Getting off the ledge:** ledgedash gives 10 actionable intangible frames at best; a
  no-impact-land ledge jump gives 12, and a bair aerial interrupt 15 [wiki:Ledgedash].
- **What beats him:** shield pressure from Fox/Falco (his out-of-shield options start
  at frame 7-10), projectiles (he must jump or shield them), and grabs that lead to chain
  grabs.

## As the training dummy

- **Class:** heavy (weight 104), fastfaller (fall 2.9, fast fall 3.5)
  [wiki:Captain_Falcon_(SSBM)]. Large hurtbox. Does not fall over from Fox's shine
  (weight above 87) so he can be waveshined [wiki:Waveshine].
- **Chain grabbed by:** [Peach](peach.md) up throw (from 0-18% depending on DI);
  Mario and Dr. Mario up throw; Donkey Kong up throw and cargo up throw; Mewtwo down
  throw [wiki:Chain_grab]; [Pikachu](pikachu.md) up throw
  [wiki:Captain_Falcon_(SSBM)]. [Ganondorf](ganondorf.md) can regrab him from down throw
  unless he DIs fully away, and from up throw unless he DIs behind
  [lib:Techchasing into 2015: Metagame and Theory]; the older chain grab guide instead
  says DI behind escapes down throw and DI away escapes up throw
  [lib:The Ganon Chaingrabbing Guide].
- **Tech chased by:** [Sheik](sheik.md), [Captain Falcon](captain-falcon.md),
  [Marth](marth.md), [Ganondorf](ganondorf.md).
- **Combo'd by:** Fox waveshine into up smash or grab; Falco pillars; Sheik and Marth
  juggles. Fox's fair drops him below about 80% (he falls out), giving Fox a tech chase
  [wiki:Fox_(SSBM)/Forward_aerial].
- **Knockdown thresholds (Ganondorf's fresh moves):** jab 45%, ftilt 28%, dtilt 22%,
  dash attack 18% [lib:Techchasing into 2015: Metagame and Theory].
- **Strong DI for a realistic CPU:** against Ganondorf's down throw, full away; against
  his up throw, behind [lib:Techchasing into 2015: Metagame and Theory] (sources
  disagree, see above); against knee, up and toward
  the stage (survival DI) [unverified]; against Falcon up air strings at low percent,
  away [lib:On Ganon vs. Falcon].
- **Recovery behaviour:** see "Edgeguarding Captain Falcon". A realistic CPU saves the
  double jump and varies between ledge and stage.

## Matchup notes

### vs Fox

- Volatile: Falcon kills Fox off one grab via tech chases, stomp and knee; Fox combos
  and gimps Falcon easily (waveshine, up throw up air, fthrow at the ledge, fsmash on his
  recovery) [wiki:Fox_(SSBM)/Forward_smash] [wiki:Fox_(SSBM)/Forward_throw].
- At low percent Fox crouch cancels the first hit of nair and the gentleman; stomp and
  grab are the safer openers there [lib:Extensive Captain Falcon Guide 2016].
- Dtilt at the ledge intercepts Fox's side B [wiki:Captain_Falcon_(SSBM)].

### vs Falco

- Take guaranteed damage from up throw: with missed DI the follow-ups are guaranteed from
  40% [lib:Uthrow Followups on Falco]. Falco's lasers stop Falcon's dash dance and gimp
  his recovery [wiki:Blaster_(Falco)].
- A soft knee can gimp Falco's recovery [wiki:Captain_Falcon_(SSBM)/Forward_aerial].

### vs Marth

- Raptor Boost and cross-up knees catch Marth trying to jump or wavedash out of shield;
  his bair out of shield is slow [lib:Extensive Captain Falcon Guide 2016].
- Marth out-spaces Falcon's aerials and edgeguards him easily; Falcon needs whiff
  punishes and grabs. Repeated aerial up airs on Marth ("air wobbling") are a known
  kill setup [wiki:Captain_Falcon_(SSBM)/Up_aerial].

### vs Sheik

- Sheik chain-tech-chases Falcon and edgeguards him; Falcon tech chases Sheik back and
  kills with knee. Up air out of shield hits her after a blocked ftilt
  [lib:Extensive Captain Falcon Guide 2016].

### vs Jigglypuff and Peach

- Floaties SDI the first nair hit up to escape the second and counter-attack; use up air
  and well-spaced knees instead [lib:Extensive Captain Falcon Guide 2016].
- Peach chain grabs him with up throw [wiki:Chain_grab].
- The S2J guide warns that Samus, Ice Climbers and Luigi, matchups Falcon "is supposed
  to" win, beat a Falcon who lacks matchup knowledge
  [lib:Extensive Captain Falcon Guide 2016].

### vs Ganondorf

- Falcon out-moves Ganondorf; Ganondorf answers short hop approaches with up-angled
  ftilt and wins by tech chasing from down throw. Falcon's recovery is easy for Ganondorf
  to edgeguard with reverse up air [lib:On Ganon vs. Falcon].

## Drill seeds

### Tech chase space animals on reaction

- **id:** `captain-falcon-tech-chase`
- **Goal:** Cover every tech option after a throw by reaction.
- **Player:** Captain Falcon
- **CPU:** [Fox](fox.md), [Falco](falco.md); later [Sheik](sheik.md)
- **Setup:** Final Destination centre; Falcon holding the CPU in grab; CPU at 0-60%.
- **CPU behaviour:** Random DI on the throw; on landing randomly techs in place, toward,
  away, or misses; after tech in place shines or spot dodges on the first free frame;
  after a missed tech randomly stays, rolls or getup attacks.
- **Success:** Grab or hit lands before the CPU's first actionable frame; chain N
  successes for a stock.
- **Fail:** CPU acts first or escapes.
- **Variations:** Down throw only (below 50%) versus up throw only (above 50%)
  [lib:Techchasing Like a Man: Complete Breakdown]; "call it out" mode where the player
  only presses a direction matching the tech; kill percent mode requiring stomp or knee.
- **Data needed:** Tech animation frames and distances for each CPU character, throw
  knockback, Falcon grab range, knee/stomp startup, reaction-window table above.

### Up throw follow-ups by DI

- **id:** `captain-falcon-uthrow-falco`
- **Goal:** Pick the guaranteed follow-up for each DI and percent.
- **Player:** Captain Falcon
- **CPU:** [Falco](falco.md) (data exists); [Fox](fox.md)
- **Setup:** Falcon holding Falco in grab; percent chosen from 30-140%.
- **CPU behaviour:** DI none, slightly behind, straight behind or straight away at
  random; jumps or techs at the first chance.
- **Success:** Regrab, up air, knee or fsmash connects as a true follow-up; on DI away a
  correct tech chase.
- **Fail:** CPU jumps out or lands and acts.
- **Variations:** Percent bands from the Kadano table (32-39, 40-50, 51-69, 70-85,
  86-126, 127+) [lib:Uthrow Followups on Falco].
- **Data needed:** Falcon up throw knockback (throw: angle 85, base 70, growth 105
  [wiki:Captain_Falcon_(SSBM)/Up_throw]), Falco weight and gravity, grab ranges.

### Stomp to knee confirm

- **id:** `captain-falcon-stomp-knee`
- **Goal:** Land the kill confirm with correct L-cancel and knee timing.
- **Player:** Captain Falcon
- **CPU:** [Fox](fox.md), [Marth](marth.md), [Sheik](sheik.md), [Peach](peach.md)
- **Setup:** CPU grounded at 60-110%, near centre or near a ledge.
- **CPU behaviour:** Stands, dash dances or shields then drops; random DI on the stomp;
  techs if it lands.
- **Success:** Stomp hits, then the clean knee (18% hit) connects in the same combo.
- **Fail:** Soft knee, whiff, or the CPU acts between hits.
- **Variations:** Stomp on shield then react (jab, grab) when it is blocked; stomp on a
  platform tech.
- **Data needed:** Stomp hitstun by percent and weight, L-cancelled landing lag (12),
  knee frames 14-16, Falcon jump squat (4).

### Gentleman consistency

- **id:** `captain-falcon-gentleman`
- **Goal:** End the jab string on the third hit every time, on hit, shield and whiff.
- **Player:** Captain Falcon
- **CPU:** Any
- **Setup:** CPU adjacent; three modes: standing (hit), shielding, out of range (whiff).
- **CPU behaviour:** Static; optional crouch cancel at low percent to show when the move
  is unsafe.
- **Success:** Jab 3 comes out and the rapid-jab state is never entered, N times in a
  row.
- **Fail:** Rapid jabs start, or the string stops before the third hit.
- **Variations:** Delay between jabs; grab after jab 2 instead.
- **Data needed:** Jab continuation windows and the toggle rule [wiki:Gentleman], jab
  hitlag.

### Edgeguard with knee and bair

- **id:** `captain-falcon-edgeguard`
- **Goal:** Go offstage, hit the recovering opponent and get back.
- **Player:** Captain Falcon
- **CPU:** [Fox](fox.md), [Falco](falco.md), [Marth](marth.md), [Sheik](sheik.md),
  [Captain Falcon](captain-falcon.md)
- **Setup:** CPU launched offstage at 50-90% with random height; Falcon at the ledge.
- **CPU behaviour:** Recovers with a random option and timing.
- **Success:** An aerial connects offstage and Falcon returns; KO preferred.
- **Fail:** CPU reaches ledge or stage; Falcon dies.
- **Variations:** Moonwalk entry required; ledgehop stall edgehog only; dtilt at ledge
  against side B.
- **Data needed:** CPU recovery timings, Falcon air speed and double jump height, ledge
  intangibility.

### Recover against ledge coverage

- **id:** `captain-falcon-recovery`
- **Goal:** Choose between stage, platform and ledge late enough to beat the edgeguard.
- **Player:** Captain Falcon
- **CPU:** [Fox](fox.md) (fsmash, shine), [Falco](falco.md) (laser, fsmash, dair),
  [Marth](marth.md), [Ganondorf](ganondorf.md) (reverse up air)
- **Setup:** Falcon offstage above ledge height at 60-100% with a double jump (variation:
  without).
- **CPU behaviour:** Randomly holds ledge, covers the stage landing, or goes out to hit
  him.
- **Success:** Falcon is on stage and actionable, or on the ledge, unhit.
- **Fail:** Hit or falls.
- **Variations:** Start high and far with no jump (Falcon Kick restore needed); start
  under the stage (reverse up B).
- **Data needed:** Up B path and grab box frames, Falcon Kick distance, airdodge
  distance.

### Punish out of shield

- **id:** `captain-falcon-oos`
- **Goal:** Use up air, grab or up B out of shield correctly.
- **Player:** Captain Falcon
- **CPU:** [Sheik](sheik.md) (ftilt), [Marth](marth.md) (fsmash, dtilt),
  [Fox](fox.md) (unsafe aerial without shine)
- **Setup:** Falcon shielding; CPU attacks the shield.
- **CPU behaviour:** Attacks with chosen move and spacing, then shields or attacks again.
- **Success:** Up air (or grab) hits within N frames after shield stun; follow-up
  connects.
- **Fail:** Whiff, blocked or hit.
- **Variations:** Short CPU characters where up air misses and grab or nair is correct.
- **Data needed:** CPU move advantage on shield, up air hitbox height, CPU hurtbox
  height.

### Combo floaties with up air and nair

- **id:** `captain-falcon-floaty-combo`
- **Goal:** Convert a down throw or up throw into an aerial string ending in knee.
- **Player:** Captain Falcon
- **CPU:** [Marth](marth.md), [Sheik](sheik.md), [Peach](peach.md),
  [Jigglypuff](jigglypuff.md)
- **Setup:** Falcon holding the CPU in grab at 20-80%.
- **CPU behaviour:** Random DI on every hit; SDI up on the first nair hit; double jumps
  or attacks when free.
- **Success:** At least N aerial hits in one combo and a clean knee or an offstage
  finish.
- **Fail:** CPU escapes or hits back.
- **Variations:** Platform stages (tech chase on platform with up air).
- **Data needed:** Throw knockback, opponent weights and fall speeds, hitstun formula.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlCa.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/captain-falcon.json`](../framedata/captain-falcon.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 3-5 | 2 | 80 | 0 | 100 | 20 |  | 21 | 16 | 2 | -10 |  |
| Jab 2 | `jab2` | 5-7 | 3 | 80 | 0 | 100 | 20 |  | 20 | 19 | 3 | -10 | starts 1 frame late (included) |
| Jab 3 | `jab3` | 6-9 | 8 | Sakurai | 20 | 100 | - |  | 32 | 23 | 5 | -11 | starts 1 frame late (included) |
|  |  | 10-12 | 6 | Sakurai | 0 | 100 | - |  |  |  | 4 | -8 |  |
| Rapid jab start | `rapid_jab_start` | - | - | - | - | - | - | - | 5 | - | - | - |  |
| Rapid jab loop | `rapid_jab_loop` | 4-5, 12-13, 20-21, 28-29, 35-36 | 1 | Sakurai | 0 | 70 | - |  | 39 | - | 2 | -33 |  |
| Rapid jab end | `rapid_jab_end` | - | - | - | - | - | - | - | 8 | - | - | - |  |
| Dash attack | `dash_attack` | 7-9 | 10 | Sakurai | 22 | 90 | - |  | 39 | 38 | 6 | -24 |  |
|  |  | 10-16 | 7 | Sakurai | 10 | 50 | - |  |  |  | 5 | -22 |  |
| Forward tilt (angled up) | `ftilt_high` | 9-11 | 12/11 | Sakurai | 10 | 100 | - |  | 29 | - | 7 | -13 |  |
| Forward tilt (slightly up) | `ftilt_mid_high` | 9-11 | 12/11 | Sakurai | 10 | 100 | - |  | 29 | - | 7 | -13 |  |
| Forward tilt | `ftilt` | 9-11 | 11 | Sakurai | 10 | 100 | - |  | 29 | - | 6 | -14 |  |
| Forward tilt (slightly down) | `ftilt_mid_low` | 9-11 | 10/11 | Sakurai | 0/10 | 100 | - |  | 29 | - | 6 | -14 |  |
| Forward tilt (angled down) | `ftilt_low` | 9-11 | 10/11 | Sakurai | 0/10 | 100 | - |  | 29 | - | 6 | -14 |  |
| Up tilt | `utilt` | 17-21 | 13 | Sakurai | 50 | 80 | - |  | 39 | 38 | 7 | -13 |  |
| Down tilt | `dtilt` | 10-15 | 12 | 80/70/60 | 25 | 75 | - |  | 35 | 35 | 7 | -17 |  |
| Forward smash (angled up) | `fsmash_high` | 18-21 | 21 | Sakurai | 24 | 100 | - | fire | 64 | 60 | 11 | -30 | charge hold frame 10 |
| Forward smash | `fsmash` | 18-21 | 20 | Sakurai | 24 | 100 | - | fire | 64 | 60 | 10 | -31 | charge hold frame 10 |
| Forward smash (angled down) | `fsmash_low` | 18-21 | 19 | Sakurai | 24 | 100 | - | fire | 64 | 60 | 10 | -31 | charge hold frame 10 |
| Up smash | `usmash` | 21-22 | 8/14 | 90/100/80 | 0/30 | 100/105 | 80/100/0 |  | 54 | 40 | 8 | -10 | charge hold frame 8 |
|  |  | 27-28 | 13/12 | 90/80 | 30 | 128/126/110 | - |  |  |  | 7 | -5 |  |
| Down smash | `dsmash` | 19-22 | 18 | Sakurai | 30 | 100 | - |  | 49 | 45 | 10 | -15 | charge hold frame 14 |
|  |  | 29-32 | 16 | Sakurai | 20 | 100 | - |  |  |  | 9 | -6 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 7-12 | 6/5 | 82/78/74 | 0 | 100 | 40 |  | 44 | - | 4 | 15 | 7 | <4, >33 | -3 |  |
|  |  | 20-29 | 7 | Sakurai | 40 | 100 | - |  |  |  | 5 |  |  |  | -2 |  |
| Forward air | `fair` | 14-16 | 18 | 32 | 24 | 100 | - | electric | 39 | 36 | 10 | 19 | 9 | <7, >34 | +1 |  |
|  |  | 17-30 | 6 | Sakurai | 35 | 80 | - |  |  |  | 4 |  |  |  | -5 |  |
| Back air | `bair` | 10-13 | 14 | Sakurai | 20/0 | 100 | - |  | 35 | 29 | 8 | 18 | 9 | <7, >20 | -1 |  |
|  |  | 14-17 | 8 | Sakurai | 20/0 | 100 | - |  |  |  | 5 |  |  |  | -4 |  |
| Up air | `uair` | 6-10 | 13/12 | Sakurai | 10 | 100 | - |  | 33 | 30 | 7 | 15 | 7 | <1, >21 | +0 |  |
|  |  | 11-13 | 12/10 | 30 | 8 | 80 | - |  |  |  | 7 |  |  |  | +0 |  |
| Down air | `dair` | 16-20 | 16 | 270/290 | 40 | 100 | - |  | 44 | 38 | 9 | 24 | 12 | <4, >35 | -3 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 11-12 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 5 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 9 | 4 | 45 | 45 | 105 | - | - | 18 | 39 |  |
| Back throw | `bthrow` | 9 | 4 | 135 | 30 | 130 | - | - | 20 | 49 |  |
| Up throw | `uthrow` | 7 | 3 | 85 | 70 | 105 | - | - | 15 | 43 |  |
| Down throw | `dthrow` | 7 | 7 | 65 | 75 | 34 | - | - | 20 | 39 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Falcon Punch, ground | `special_n` | 52-56 | 27/25/23 | Sakurai | 30 | 102 | - | fire | 99 | 65 | 14 | - |  |
| Neutral B: Falcon Punch, air | `special_air_n` | 52-56 | 27/25/23 | Sakurai | 40 | 102 | - | fire | 99 | - | 14 | - |  |
| Side B: Raptor Boost, ground, Start | `special_s_start` | 15-79 | 0 | Sakurai | 0 | 0 | - | inert | 79 | - | - | - |  |
| Side B: Raptor Boost, ground | `special_s` | 3-7 | 7 | 90 | 78 | 80 | - | fire | 24 | - | 5 | - |  |
| Side B: Raptor Boost, air, Start | `special_air_s_start` | 18-79 | 0 | Sakurai | 0 | 0 | - | inert | 79 | - | - | - |  |
| Side B: Raptor Boost, air | `special_air_s` | 3-7 | 7 | 270 | 60 | 70 | - | fire | 44 | - | 5 | - |  |
| Up B: Falcon Dive, ground | `special_hi` | 13, 14-33 | 1 | Sakurai | 0 | 100 | - | grab | 64 | - | 2 | - |  |
| Up B: Falcon Dive, air | `special_air_hi` | 13, 14-33 | 1 | Sakurai | 0 | 100 | - | grab | 64 | - | 2 | - |  |
| Up B: Falcon Dive, ground, Catch | `special_hi_catch` | 3-4 | 5 | Sakurai | 0 | 0 | - | fire | 15 | - | 4 | - |  |
| Up B: Falcon Dive, ground, Throw | `special_hi_throw` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Down B: Falcon Kick, ground | `special_lw` | 14-16 | 15 | Sakurai | 50 | 70 | - | fire | 39 | - | 8 | - |  |
|  |  | 17-24 | 12/15 | 80/Sakurai | 50 | 60/70 | - | fire |  |  | 8 | - |  |
|  |  | 25-32 | 9/15 | 90/Sakurai | 50 | 50/70 | - | fire |  |  | 8 | - |  |
| Down B: Falcon Kick, ground, End | `special_lw_end` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Down B: Falcon Kick, air | `special_air_lw` | 15-17 | 15 | Sakurai | 40 | 70 | - | fire | 29 | - | 8 | - |  |
|  |  | 18-25 | 13 | Sakurai | 40 | 65 | - | fire |  |  | 7 | - |  |
|  |  | 26-29 | 11 | Sakurai | 40 | 60 | - | fire |  |  | 6 | - |  |
| Down B: Falcon Kick, air, End | `special_air_lw_end` | 2-3 | 9 | 80 | 80 | 20 | - |  | 44 | - | 6 | - |  |
| Down B: Falcon Kick, ground, EndAir | `special_lw_end_air` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Down B: Falcon Kick, air, EndAir | `special_air_lw_end_air` | - | - | - | - | - | - | - | 28 | - | - | - |  |
| Up B: Falcon Dive, ground, Throw | `special_hi_throw_317` | - | - | - | - | - | - | - | 59 | - | - | - |  |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 3-20 | - | 32 | 29 |  |
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
| Wall tech | `wall_tech` | - | - | 26 | - | starts 1 frame late (included) |
| Wall tech jump | `wall_tech_jump` | - | - | 40 | - | starts 1 frame late (included) |
| Ceiling tech | `ceiling_tech` | intangible 2-11 | - | 26 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-49 | - | 58 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-22 | - | 32 | - |  |
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
| Up air | jump | 10 | `uair` |
| Neutral air | jump | 11 | `nair` |
| Back air | jump | 14 | `bair` |
| Up B | jump cancel | 14 | `special_hi` |
| Forward air | jump | 18 | `fair` |
| Down air | jump | 20 | `dair` |
| Up smash | jump cancel | 22 | `usmash` |
| Spot dodge | direct | intangible 3-20 of 32 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 16 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Captain Falcon indexed by [The Melee Library](https://www.meleelibrary.com/#captain-falcon) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [Are You a Captain Falcon Player?](https://www.youtube.com/watch?v=nEtiGSeShK4) | SSBM Tutorials | They give an overview of Captain Falcon the character to give you an idea of whether you would like to play him. |
| [2020 Captain Falcon Melee Techs Guide](https://www.youtube.com/watch?v=dxAEj3lU7Co&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=21&t=0s) | Third Chair | Video guide on performing useful Captain Falcon tech in 2020. |
| [Captain Falcon Hitboxes and Frame Data](http://smashboards.com/threads/captain-falcon-hitboxes-and-frame-data.284165/) | Stratocaster, Standardtoaster, and SuperDoodleMan |  |
| [Everything You Needed To Know About Captain Falcon Before 2011](http://smashboards.com/threads/the-falcon-index-thread-new-post-of-the-week-by-magus.307911/) | 0Room | This is actually a (somewhat) old collection of different posts by various Falcon mains on multiple match-ups. |
| [Extensive Captain Falcon Guide 2016](http://www.meleeitonme.com/s2js-captain-falcon-guide/) | S2J |  |
| [This Is How To Move and Do Other Things Good Too](http://smashboards.com/threads/this-is-how-to-move-good-and-do-other-things-good-too.389487/) | Gravy | Gravy explains in technical details Falcon's movement options. |
| [Techchasing Like a Man: Complete Breakdown](http://smashboards.com/threads/tech-chasing-like-a-man-complete-breakdown.382475/) | Gravy | Gravy discusses four different types of techchasing with Falcon. |
| [Uthrow Followups on Falco](http://smashboards.com/threads/captain-falcons-uthrow-followups-on-falco.364342/) | Kadano |  |
| [Ask Mango Falcon Questions](http://smashboards.com/threads/ask-mango-falcon-questions-d-and-other-things.214662/) | community | Lots of questions and answers about Falcon. May give you a place to start. Use the search function. |
| [Captain Falcon FAQ and Training Guide](http://smashboards.com/threads/resumed-captain-falcon-faq-and-training-guide.227344/#post-7019543) | Scar | Has info on stage picks, matchups, training regimen, and FAQs. |
| [20GX Match Critiques](https://www.youtube.com/playlist?list=PLVPruFoQFB14l-MZyzvBZxDnU-pCVJ2mi) | 20GX Crew and friends | Playlist. Learn what the Florida Falcons think about how other people play Captain Falcon. |
| [Beginner Fundamental Discussion](https://www.youtube.com/watch?v=qAUVzXOct4o) | 20GX Crew | The 20GX crew discusses basic movement options, frame advantage and invincibility options. |
| [Improving Falcon’s Wavelands for Beginners](https://www.youtube.com/watch?v=HwVwbBEHCGg) | 20GX Crew |  |
| [Different Ways To Pivot](https://www.youtube.com/watch?v=MtRPjZ37cO0) | 20GX Crew |  |
| [Dissecting the Mechanics of Jump](https://www.youtube.com/watch?v=tY3XugmyMow) | 20GX Crew |  |
| [Sheik Data](https://drive.google.com/file/d/0B6WQf0mbyOU4TEtad2haUVcwdDQ/view) | 20GX Crew | Percents to help followups on Sheik. |
| [Soapsudropping](http://www.reddit.com/r/SSBM/comments/36xaw0/soapsudrop_the_fastest_way_for_falcon_to_grab/) | Soapsuds | The fastest way for Captain Falcon to grab the ledge in many situations. |
| [Protato Accidentally Finds Stuff: The Thread](http://smashboards.com/threads/protato-accidentally-finds-stuff-the-thread.392989/) | Protato | Some Captain Falcon minutiae. Dash attack wall jump, pivot wall jump, sticky walking, quick ways to get to ledge, SH nair data, crouching in run boost run, dsmash on platforms, run b cancel and vududashing, rising falcon punches, and Mango's stomp spacing. |
| [Falcon Walljump Tips and Tricks](https://www.youtube.com/watch?v=ELcWOXRACNk) | Vlogarithm |  |
| [Optimization Fundamentals](https://www.youtube.com/watch?v=93xR0lnMink) | 20GX Crew | Movement is Captain Falcon’s best and most fundamental tool. Optimizing your control of it is important. |
| [Frame Data: The Way Gentleman Works](http://smashboards.com/threads/frame-data-the-way-gentleman-works.394171/) | SoapSuds |  |
| [The Gentleman - Technical Data](https://smashboards.com/threads/frame-data-the-way-gentleman-works.394171/#post-21554393) | Achilles | Achilles explains how the Gentleman technique is programmed into the game to help players perform the technique. |
| [How to Train Your Falcon](https://www.youtube.com/watch?v=JbgR29W_X_o) | F. Zero | A video that covers training your Captain Falcon's combo game, defensive game, and control by yourself. |
| [Captain Falcon Tutorial](https://www.youtube.com/watch?v=DPDJUpzul-U) | Wizzrobe | Wizzrobe discusses shield pressure, ledge options, approach options, combos on Marth, combos on Sheik, tech chasing, the Fox match up, stages Captain Falcon likes especially versus Jigglypuff, punishing Jigglypuff, the Falco match up, and random Q&A. |
| [Air Wobbling Marth](https://www.youtube.com/watch?v=4kQabPgE50Y) | Vlogarithm | A video going over aerial follow-ups on Marth. |
| [Project Falcon: Why Gravy Is Right](http://smashboards.com/threads/project-falcon.412971/) | Furta and community | A thread similar to Kadano’s thread but for Falcon. |
| [Captain Falcon Drills](https://www.youtube.com/watch?v=sZQhGlHQ9uY) | SSBM Tutorials |  |
| [Captain Falcon Edgeguard Compilation](https://www.youtube.com/watch?v=6rBBiaEiLMc) | Yellow Money Falcon | A tutorial/compilation exemplifying great Falcon edgeguarding tactics. |
| [Raptor Boost Disables Projectiles](https://www.reddit.com/r/SSBM/comments/3q9zv6/raptor_boost_dodge/) | Schmooblidon | A NTSC-specific technique regarding raptor boost. |
| [Captain Falcon Neutral Game Tutorial](https://www.youtube.com/watch?v=kozPeTCcw5s) | SSBM Tutorials |  |
| [Dash Attack to Wall Jump](https://www.youtube.com/watch?v=n7gLqWAA6kg) | PewPewU |  |
| [You Can Move during the Startup of Captain Falcon's Up-B](https://www.reddit.com/r/smashbros/comments/4ecx2h/til_you_can_move_during_the_startup_of_falcons_upb/) | lucatron |  |
| [Captain Falcon Trials - For Newer and Expert Falcons](http://smashboards.com/threads/captain-falcon-trials-for-newer-and-expert-falcons.344677/) | TheSpyMachine | Trials are technical challenges meant to improve your techskill. |
| [Handcams for Haxdash and [Moonwalk](https://www.youtube.com/watch?v=vdqX3l8sesA)](https://www.youtube.com/watch?v=lxg05IN9ncw) | Vlogarithm |  |
| [How to Moonwalk](https://www.youtube.com/watch?v=64be4Hqeshw) | Jynx |  |
| [Captain Falcon Practice Tutorials for All Levels](https://www.youtube.com/playlist?list=PL7Pex5PDRPKRN8kluqZOGRg_EQj5c7dmg) | NMW | A playlist of videos showing how to practice Captain Falcon. |
| [How to Combo Fastfallers with Captain Falcon](https://www.youtube.com/watch?v=cipX05p1He4) | SSBM Tutorials |  |
| [Falcon platform techchase concept](https://www.youtube.com/watch?v=avx6m1cUGS4) | Adam Farmer | Tech chasing with double jump dair. |
| [Captain Falcon Melee Chaingrab Guide](https://www.youtube.com/watch?v=ZIsBkXhm7Js&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=2&t=0s) | Third Chair |  |
| [Captain Falcon Melee Discord Channel](https://discord.gg/AZtHzRj) | Setchi, Rachman | An exceptional discord channel with extra special resources. The admins have put a lot of effort into a bot that you can type commands to with questions and receive answers with accompanying gifs. |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Captain Falcon (SSBM): https://www.ssbwiki.com/Captain_Falcon_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Captain_Falcon_(SSBM)/Forward_aerial ,
  /Down_aerial , /Up_aerial , /Neutral_aerial , /Back_aerial , /Neutral_attack ,
  /Up_throw , /Down_throw , /Forward_throw , /Back_throw , /Grab , /Side_special ,
  /Up_special , /Down_special , /Neutral_special , /Up_smash , /Forward_smash
- SSBWiki technique pages: https://www.ssbwiki.com/Knee_Smash ,
  https://www.ssbwiki.com/Gentleman , https://www.ssbwiki.com/Moonwalk ,
  https://www.ssbwiki.com/Raptor_Boost , https://www.ssbwiki.com/Falcon_Dive ,
  https://www.ssbwiki.com/Falcon_Kick , https://www.ssbwiki.com/Tech-chase ,
  https://www.ssbwiki.com/Chain_grab , https://www.ssbwiki.com/Ledgestall ,
  https://www.ssbwiki.com/Ledgedash , https://www.ssbwiki.com/Waveshine ,
  https://www.ssbwiki.com/Blaster_(Falco)
- Melee Library, "Extensive Captain Falcon Guide 2016" (S2J), via web.archive.org:
  http://www.meleeitonme.com/s2js-captain-falcon-guide/
- Melee Library, "Techchasing Like a Man: Complete Breakdown" (Gravy and thread
  contributors), via web.archive.org:
  http://smashboards.com/threads/tech-chasing-like-a-man-complete-breakdown.382475/
- Melee Library, "Uthrow Followups on Falco" (Kadano), via web.archive.org:
  http://smashboards.com/threads/captain-falcons-uthrow-followups-on-falco.364342/
- Melee Library, "Frame Data: The Way Gentleman Works" (SoapSuds), via web.archive.org:
  http://smashboards.com/threads/frame-data-the-way-gentleman-works.394171/
- Melee Library (Ganondorf section), "On Ganon vs. Falcon" / "Ganon vs." thread page 6,
  "Techchasing into 2015: Metagame and Theory" (Ace), "The Ganon Chaingrabbing Guide"
  (Magus), via web.archive.org
- Frame data dump: `Captain Falcon.json`
