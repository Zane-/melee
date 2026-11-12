---
schema: melee-character/v1
id: mewtwo
name: Mewtwo
aliases: [M2]
tier: "D (20th of 26), 2021 list"
archetype: [floaty, lightweight, grappler, mixup, combo-food, technical]
related: []
summary: Mewtwo wins by poking with long disjointed tail tilts, landing grabs for the strongest throws in the game, and using a long teleport recovery to stay alive and to edgeguard deep.
key_tech: [teleport-recovery, teleport-movement, double-jump-cancel, uthrow-kill, dthrow-chaingrab, dtilt-combos, shadow-ball-charge, double-jump-extension, confusion-tricks, disable]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlMt.dat
framedata: ../framedata/mewtwo.json
code: src/melee/ft/kinds/ftMewtwo
specials:
  neutral_b: "Shadow Ball"
  side_b: "Confusion"
  up_b: "Teleport"
  down_b: "Disable"
attributes:
  weight: 85
  gravity: 0.082
  fall_speed: 1.5
  fast_fall_speed: 2.3
  jump_squat: 5
  jumps: 2
  walk_speed: 1
  dash_speed: 1.4
  run_speed: 1.4
  traction: 0.04
  air_speed: 1.2
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [8, 26, 6]
  rapid_jab_start: [null, 8, 0]
  rapid_jab_loop: [7, 51, 2]
  rapid_jab_end: [null, 14, 0]
  dash_attack: [10, 38, 9]
  ftilt_high: [6, 29, 10]
  ftilt: [6, 29, 10]
  ftilt_low: [6, 29, 10]
  utilt: [6, 28, 10]
  dtilt: [5, 20, 9]
  fsmash: [18, 52, 20]
  usmash: [9, 70, 10]
  dsmash: [20, 38, 15]
  nair: [5, 42, 4]
  fair: [5, 36, 14]
  bair: [12, 32, 13]
  uair: [9, 35, 14]
  dair: [18, 47, 16]
  grab: [7, 31, 0]
  dash_grab: [9, 41, 0]
  pummel: [12, 25, 3]
  fthrow: [null, 75, 5]
  bthrow: [null, 50, 11]
  uthrow: [null, 70, 12]
  dthrow: [15, 50, 6]
  special_n_start: [null, 18, 0]
  special_n_loop: [1, 8, 2]
  special_n_loop_297: [1, 8, 2]
  special_n_cancel: [null, 8, 0]
  special_n_end: [null, 24, 0]
  special_air_n_start: [null, 18, 0]
  special_air_n_loop: [1, 8, 2]
  special_air_n_loop_302: [1, 8, 2]
  special_air_n_cancel: [null, 8, 0]
  special_air_n_end: [null, 24, 0]
  special_s: [12, 56, 10]
  special_air_s: [12, 56, 10]
  special_hi_start: [null, 8, 0]
  special_hi: [null, 30, 0]
  special_hi_lost: [null, 16, 0]
  special_air_hi_start: [null, 8, 0]
  special_air_hi: [null, 16, 0]
  special_lw: [null, 40, 0]
  special_air_lw: [null, 40, 0]
oos:  # option: frame the hitbox is out
  grab: 7
  nair: 10
  fair: 10
  usmash: 10
  uair: 14
  bair: 17
  dair: 23
resources: 2
# generated: end
---

# Mewtwo

<!-- GENERATED:attributes -->
## Attributes

Read from `PlMt.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 85 |
| Gravity | 0.082 |
| Terminal fall speed | 1.5 |
| Fast-fall speed | 2.3 |
| Jump squat (frames before airborne) | 5 |
| Full hop / short hop initial Y speed | 2.3 / 1.4 |
| Air jump Y multiplier | 1 |
| Jumps | 2 |
| Walk max speed | 1 |
| Dash initial speed / run max speed | 1.4 / 1.4 |
| Ground friction (traction) | 0.04 |
| Air max horizontal speed | 1.2 |
| Air acceleration (base + stick) | 0.02 + 0.03 |
| Air friction | 0.016 |
| Normal landing lag | 4 |
| Shield size | 16.25 |
<!-- /GENERATED:attributes -->

## Overview

Mewtwo is a large, light, floaty character: it weighs the same as
[Young Link](young-link.md) and falls as slowly as [Peach](peach.md), who is both
heavier and smaller [wiki:Mewtwo_(SSBM)]. It has a slow dash, very high air speed and
the third-longest [wavedash](../techniques/wavedash.md) in the game, so most of its
ground movement is wavedashing [wiki:Mewtwo_(SSBM)] [wiki:Wavedash]. Neutral is played
with disjointed tail tilts (dtilt hits on frame 5 [fd]), a charged neutral B (Shadow
Ball) and wavedash grabs. The reward for a grab is high: uthrow is the strongest throw
in the game, bthrow kills at the edge, and dthrow starts combos and some chain grabs
[wiki:Mewtwo_(SSBM)]. Up B (Teleport) plus a tall double jump give one of the longest
recoveries, but it has no hitbox. Mewtwo is easy to hit, combo, tech chase and kill, it
struggles against projectiles, and its kill moves are short-ranged or slow. It is
considered unviable at top level [wiki:Mewtwo_(SSBM)].

## Strengths and weaknesses

- **Strengths:**
  - Throws: uthrow (12%, base knockback 100, growth 70) and bthrow (11%, base 70, growth
    80) kill; dthrow combos [wiki:Mewtwo_(SSBM)/Up_throw] [wiki:Mewtwo_(SSBM)/Back_throw].
  - Dtilt: frame 5, disjointed, interruptible from frame 20, combo starter
    [wiki:Mewtwo_(SSBM)/Down_tilt] [fd].
  - Long recovery: Teleport is fully intangible while travelling, plus high double jump
    and high air speed [wiki:Mewtwo_(SSBM)].
  - Shadow Ball: fully charged it kills at around 100% and its wavy path is hard to dodge
    [wiki:Mewtwo_(SSBM)].
  - Long wavedash and the best [moonwalk](../techniques/moonwalk.md) [wiki:Moonwalk].
  - Fair is frame 5 with strong upward knockback [fd].
- **Weaknesses:**
  - Big hurtbox, light, floaty: comboed, juggled and killed early
    [wiki:Mewtwo_(SSBM)].
  - Slow tech rolls: very easy to [tech chase](../techniques/tech-chase.md)
    [wiki:Mewtwo_(SSBM)].
  - Poor [SHFFL](../techniques/shffl.md); weak against camping; side B's reflector does
    not change projectile ownership [wiki:Mewtwo_(SSBM)].
  - Teleport has no hitbox, so it is weak to edgehogging [wiki:Mewtwo_(SSBM)].
  - Dsmash hits only in front and on frame 20, the slowest down smash in the game
    [wiki:Mewtwo_(SSBM)].

## Character tech

### Teleport recovery

- **id:** `teleport-recovery`
- **What:** Up B makes Mewtwo vanish and reappear a fixed distance away in the direction
  held. It cannot be hit while travelling.
- **Inputs:** Up B, then hold the direction of travel before Mewtwo disappears.
- **Timing:** Intangible on frames 8-17 of a 32-frame move
  [wiki:Mewtwo_(SSBM)/Up_special]. It deals no damage [wiki:Teleport]. Ending in the air
  leaves Mewtwo helpless [wiki:Teleport]. Landing on the stage at the right angle cancels
  most of the ending lag [wiki:Teleport].
- **Used for:** Recovery from very far away; choosing between ledge, stage and platform.
- **Common errors:** Teleporting from too close and overshooting onto the stage in lag;
  aiming at the ledge when it is occupied; being hit during frames 1-7 before
  intangibility.
- **Drill idea:** Mewtwo off stage at random positions; success if it reaches ledge or
  stage unhit against a CPU that randomly edgehogs or waits on stage.

### Teleport movement

- **id:** `teleport-movement`
- **What:** On-stage uses of Teleport: as a dodge with less lag than a roll or spot dodge,
  as a short-hop teleport that lands with cancelled lag, as a run-off teleport to grab
  the ledge, and as an edge cancel.
- **Inputs:** Grounded: up B plus a horizontal direction. Faster version: short hop, up B
  horizontally, [fast fall](../techniques/fast-fall.md) after reappearing. Edgehog: run
  off the stage and teleport back into the ledge [wiki:Teleport].
- **Timing:** Ground-to-ground Teleport has less lag than Mewtwo's roll or spot dodge;
  the short-hop version is faster still, and only a wavedash moves Mewtwo faster
  [wiki:Teleport]. Exact frame counts for the cancelled landings: Unknown.
- **Used for:** Escaping pressure through the opponent; fast edgehogs; platform movement.
- **Common errors:** Teleporting to a predictable spot and being punished on
  reappearance; missing the ledge on the run-off version.
- **Drill idea:** CPU swings at Mewtwo at random times; success if Mewtwo teleports
  through the hit and is actionable before the CPU.

### Double jump cancel

- **id:** `double-jump-cancel`
- **What:** Mewtwo's double jump rises gradually, so an aerial started during it cancels
  the rise. Jump, double jump, aerial gives a low aerial without a SHFFL.
- **Inputs:** Jump, double jump shortly after leaving the ground, aerial (usually fair),
  [L-cancel](../techniques/l-cancel.md) on landing.
- **Timing:** Must not be frame perfect: an instant double jump cancel lands before the
  hitbox appears [wiki:Double_jump_cancel]. Fair hits frames 5-7 and has 25 frames of
  landing lag, 12 when L-cancelled; uair hits frames 9-11 (20/10); bair frames 12-15
  (28/14) [fd]. Nair and dair take too long to benefit [wiki:Double_jump_cancel]. Jump
  squat length: 5 frames [unverified].
- **Used for:** Fast fair into grab, tilt, another fair or a charged Shadow Ball
  [wiki:Mewtwo_(SSBM)]; uair juggles.
- **Common errors:** Too early (lands with no hit); too late (floats upward, slow);
  doing it off stage and losing the jump.
- **Drill idea:** Standing CPU; success if a DJC fair connects and a follow-up (grab or
  second fair) lands before the CPU acts.

### Up throw kill

- **id:** `uthrow-kill`
- **What:** Uthrow is the strongest throw in Melee and kills off the top.
- **Inputs:** Grab, uthrow. Often set up with wavedash grab or dtilt into grab.
- **Timing:** 12%, angle 90, base knockback 100, growth 70
  [wiki:Mewtwo_(SSBM)/Up_throw]. The wiki says it starts killing at around 120%, earlier
  on floaty characters, and latest on [Fox](fox.md) and [Falco](falco.md) because of
  their fall speed [wiki:Mewtwo_(SSBM)]. Standing grab is active frames 7-8, dash grab
  frames 9-10 [wiki:Mewtwo_(SSBM)/Grab].
- **Used for:** Reliable kill on floaties; against fastfallers bthrow toward the nearer
  blast zone is the better killing throw [wiki:Mewtwo_(SSBM)].
- **Common errors:** Using uthrow on a fastfaller at kill percent when bthrow would kill;
  pummelling so long the opponent breaks out.
- **Drill idea:** CPU at a percent near the kill threshold in grab; player must choose
  uthrow or bthrow correctly for the character and stage position; success if the CPU
  dies.

### Down throw chain grab

- **id:** `dthrow-chaingrab`
- **What:** Dthrow pops the opponent up at a steep angle; on heavy or fast-falling
  characters Mewtwo can regrab.
- **Inputs:** Grab, dthrow, follow the DI (directional influence, holding a direction to
  bend the launch), regrab. See [chain-grab](../techniques/chain-grab.md).
- **Timing:** Dthrow is 5% (tail hit) + 6% (throw), angle 69, base 65, growth 50; the
  opponent is released on frame 25 of a 49-frame animation
  [wiki:Mewtwo_(SSBM)/Down_throw]. On [Bowser](bowser.md) it chains from 0% to about
  50%; it also works on fastfallers ([Fox](fox.md), [Falco](falco.md),
  [Sheik](sheik.md), [Captain Falcon](captain-falcon.md), sometimes [Roy](roy.md)) but
  depends on DI [wiki:Chain_grab]. At low percent uthrow also chain grabs fastfallers and
  leads to fair then regrab on Fox and Falco [wiki:Mewtwo_(SSBM)].
- **Used for:** Damage from 0% on the listed characters; otherwise dthrow into fair or a
  tech chase.
- **Common errors:** Regrabbing in place when the opponent DI'd away; continuing past the
  percent where they can jump out.
- **Drill idea:** CPU Fox or Bowser at 0% in grab with random DI; count regrabs.

### Down tilt combos

- **id:** `dtilt-combos`
- **What:** Dtilt is a fast, low, disjointed tail sweep that launches upward and ends
  quickly, leading into more hits.
- **Inputs:** Down + A (tilt), often out of a wavedash; then dtilt again, fair, or grab.
- **Timing:** Hits frames 5-7, interruptible from frame 20, angle 80, 9% near the body
  down to 5% at the tip [fd] [wiki:Mewtwo_(SSBM)/Down_tilt]. Spaced at the tip it cannot
  be punished out of shield [wiki:Mewtwo_(SSBM)/Down_tilt]. Follow-ups listed by the
  wiki: itself at lower percents, fair for a juggle, grab into uthrow, dthrow or bthrow
  [wiki:Mewtwo_(SSBM)/Down_tilt].
- **Used for:** Mewtwo's main combo starter and safest poke.
- **Common errors:** Hitting with the weak tip at low percent and getting
  [crouch cancelled](../techniques/crouch-cancel.md).
- **Drill idea:** CPU walks into range; success if dtilt connects and a second hit or grab
  lands before the CPU can act.

### Shadow Ball charge

- **id:** `shadow-ball-charge`
- **What:** Neutral B charges a projectile that can be stored with L/R and released
  later. It can be charged in the air, and the charge is not lost when Mewtwo is hit
  during Teleport [wiki:Shadow_Ball].
- **Inputs:** Hold B to charge; L or R to store; B again to fire.
- **Timing:** Damage 3-25% by charge [wiki:Mewtwo_(SSBM)]. The charging ball has a small
  2% hitbox [fd] [wiki:Mewtwo_(SSBM)]. Firing a full charge in the air pushes Mewtwo
  backward a long way [wiki:Mewtwo_(SSBM)]. A full charge kills at roughly 100% and
  takes about half a shield [wiki:Mewtwo_(SSBM)] [wiki:Shadow_Ball].
- **Used for:** Kill move, combo ender after aerials, tech chase option that covers
  several choices at once, recovery mixup (recoil back toward the stage when facing
  away) [wiki:Mewtwo_(SSBM)].
- **Common errors:** Charging within the opponent's reach; firing it facing the stage
  while recovering, which pushes Mewtwo away from the stage.
- **Drill idea:** CPU knocked down at about 100%; success if a full Shadow Ball hits
  whichever tech option it picks.

### Double jump extension

- **id:** `double-jump-extension`
- **What:** A well-timed aerial during the rise of the double jump lengthens it, adding
  recovery distance. Bair is normally used because it ends soonest.
- **Inputs:** Double jump, then bair at the right moment during the ascent.
- **Timing:** Exact frame Unknown. Described on the wiki [wiki:Mewtwo_(SSBM)]. Bair lasts
  31 frames [fd].
- **Used for:** Extra recovery distance before Teleport.
- **Common errors:** Aerial too early, which cancels the jump's rise instead (that is the
  double jump cancel).
- **Drill idea:** Off stage at a distance only reachable with the extension plus
  Teleport; success on reaching the ledge.

### Confusion tricks

- **id:** `confusion-tricks`
- **What:** Side B (Confusion) is a command grab that spins the opponent and drops them
  in tumble facing away, and also a reflector. It has two niche uses: stalling or
  reversing Mewtwo's air momentum, and dragging an opponent through a thin stage edge.
- **Inputs:** Side B. In the air against Mewtwo's momentum it acts like a small extra
  jump [wiki:Mewtwo_(SSBM)].
- **Timing:** Grab frames 12-15, reflects frames 12-38, 55 frames total, 10%
  [wiki:Mewtwo_(SSBM)/Side_special] [wiki:Mewtwo_(SSBM)]. On hit, every character can
  bair Mewtwo before it recovers [wiki:Mewtwo_(SSBM)]. Used on an airborne opponent it
  restores their double jump [wiki:Confusion]. Near the thin side of Battlefield, the
  held opponent can be pulled under the stage [wiki:Confusion].
- **Used for:** Recovery stall; a gimmick gimp on Battlefield.
- **Common errors:** Using it as an attack on stage (negative on hit).
- **Drill idea:** Recovery drill that requires one Confusion stall before Teleport to
  avoid a timed edgeguard.

### Disable

- **id:** `disable`
- **What:** Down B fires a short beam that stuns a grounded opponent who is facing
  Mewtwo. Stun lasts longer at higher percent. If the target is already stunned or in
  tumble it is launched instead.
- **Inputs:** Down B at close range, opponent facing Mewtwo.
- **Timing:** Hitbox frames 15-21, 41 frames total, 1% [wiki:Mewtwo_(SSBM)/Down_special]
  [wiki:Mewtwo_(SSBM)]. In the air it slows Mewtwo's descent [wiki:Mewtwo_(SSBM)].
- **Used for:** Hard read at high percent into a charged smash or Shadow Ball; recovery
  stall.
- **Common errors:** Opponent facing away (no effect); using it at low percent where the
  stun is too short.
- **Drill idea:** CPU at high percent facing Mewtwo after a get-up; success if Disable
  connects and a kill move lands during the stun.

## Neutral game

- Move by wavedash; Mewtwo wavedashes long distances faster than it can dash
  [wiki:Wavedash].
- Dtilt and ftilt (frames 6-8, disjointed [fd]) at tail-tip range; utilt (frame 6) as an
  anti-air and juggle starter.
- Wavedash or dash grab when the opponent shields the tilts. Grab range is average
  [wiki:Mewtwo_(SSBM)].
- DJC fair as the fast aerial; full-hop nair (multi-hit, active frames 5-38 [fd]) to
  cover space and as a punish.
- Charge Shadow Ball when the opponent is far away; a stored full charge changes how they
  can approach.
- Jab hits on frame 8 [fd] and can reset a missed tech (the wiki shows dthrow, jab reset,
  dsmash on Fox [wiki:Lock]).
- Teleport and the invisible air dodge make Mewtwo's landings and retreats harder to
  follow [wiki:Mewtwo_(SSBM)].

## Punish game

Most damage comes from grabs and from dtilt or utilt into fair. Fair (14%, angle 84)
launches upward for juggles with uair (tail tip 14%) and more fairs [fd]. Bair chains
into itself off stage as a "wall of pain" [wiki:Mewtwo_(SSBM)]. Fthrow (throw plus five
small Shadow Balls) is only for damage and stage control and can be SDI'd
[wiki:Mewtwo_(SSBM)].

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| dthrow | Bowser | 0-50% | regrab | Chain grab | [wiki:Chain_grab] |
| dthrow | Fox, Falco, Sheik, Captain Falcon, sometimes Roy | low, DI dependent | regrab | | [wiki:Chain_grab] |
| uthrow | Fox, Falco | low | regrab, or fair then regrab | | [wiki:Mewtwo_(SSBM)] |
| dthrow | most | typical | fair, or tech chase | | [wiki:Mewtwo_(SSBM)] |
| dtilt | most | low | dtilt | | [wiki:Mewtwo_(SSBM)/Down_tilt] |
| dtilt | most | typical | fair or grab | | [wiki:Mewtwo_(SSBM)/Down_tilt] |
| DJC fair | most | typical | grab, tilt, fair, Shadow Ball | Character dependent | [wiki:Mewtwo_(SSBM)] |
| utilt | most | typical | uair, fair | Juggle | [wiki:Mewtwo_(SSBM)] |
| missed tech after dthrow | Fox (example) | Unknown | jab reset, then dsmash | | [wiki:Lock] |

### Chain grabs and tech chases

See the table: dthrow on [Bowser](bowser.md) 0-50%, dthrow and low-percent uthrow on
fastfallers, all DI dependent [wiki:Chain_grab] [wiki:Mewtwo_(SSBM)]. The Melee Library
has a video guide [lib:Mewtwo Melee Chaingrab Guide] that could not be watched, so exact
windows per character are Unknown. Dthrow also sets up tech chases, where a charged
Shadow Ball covers several options [wiki:Mewtwo_(SSBM)].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| uthrow | floaties and mid weights | from about 100-120% | Latest on Fox and Falco | [wiki:Mewtwo_(SSBM)] |
| bthrow | all, best on fastfallers | around 100% on some characters | Near the edge, facing away from it | [wiki:Mewtwo_(SSBM)] |
| Shadow Ball (full, 25%) | all | around 100% | | [wiki:Mewtwo_(SSBM)] |
| fair (14%) | all | around 120% | Off the top | [wiki:Mewtwo_(SSBM)] |
| usmash (last hit, 10%) | all | around 120% | Hard to land; early hits can be SDI'd | [wiki:Mewtwo_(SSBM)] |
| dsmash (15%) | all | Unknown | Frame 20, front only, interruptible from frame 38 | [wiki:Mewtwo_(SSBM)/Down_smash] |
| fsmash (blast 20%) | all | Unknown; "rather low knockback" | Tip only; arms do 12% | [wiki:Mewtwo_(SSBM)] |
| dair (14-16%, meteor) | all | off stage | Frame 18; weak meteor | [wiki:Mewtwo_(SSBM)] [fd] |
| bair | all | off stage | Repeated bairs | [wiki:Mewtwo_(SSBM)] |

- Setups: dtilt to grab to uthrow or bthrow; dthrow, jab reset, dsmash; DJC fair to
  Shadow Ball.
- Edgeguards: bair and nair off stage (Mewtwo can go very deep and still return), dair
  meteor, dsmash at the ledge, run-off Teleport edgehog, Confusion under Battlefield.

## Recovery

- **Options:** Tall floaty double jump (can be lengthened with a timed bair); Teleport
  (intangible frames 8-17, long fixed distance, any direction); high air speed and slow
  fall; nair slows the fall slightly; airborne full Shadow Ball recoil; Confusion against
  momentum; Disable stall; invisible air dodge [wiki:Mewtwo_(SSBM)]
  [wiki:Mewtwo_(SSBM)/Up_special].
- **Mixups:** Teleport to ledge, to stage, or to a platform; teleport from far (straight
  in) or from below; delay with Confusion or Disable; drift in high with the double jump
  and keep Teleport in reserve.
- **Weaknesses:** No hitbox, so an occupied ledge forces Mewtwo onto the stage where the
  reappearance is punishable; 7 vulnerable frames before intangibility; large light
  body, so any solid hit before the teleport sends it far.

### Edgeguarding Mewtwo

- Edgehog during the teleport: the wiki names edgehogging as the main weakness
  [wiki:Mewtwo_(SSBM)]. Then punish the landing on stage.
- Hit it during the double jump or drift, before up B; it is light and floaty, so strong
  aerials kill early.
- Do not chase the teleport itself (intangible frames 8-17); cover the two or three end
  points instead.
- A realistic CPU Mewtwo varies teleport end points (ledge, on stage past the
  edgeguarder, platform) and sometimes stalls first.

## Defense and out of shield

- Out of shield: nair is called a great out-of-shield option by the wiki
  [wiki:Mewtwo_(SSBM)] (first hit frame 5 after the jump squat [fd]); shield grab (grab
  active frames 7-8 [wiki:Mewtwo_(SSBM)/Grab]); wavedash out of shield into dtilt;
  Teleport away.
- Its shield is poked easily because the body is large; spot dodge is poor; rolls are
  long [wiki:Mewtwo_(SSBM)].
- Crouch cancel is weak because Mewtwo is light.
- Combo escapes: double jump and drift, invisible air dodge, Teleport. No fast
  combo-breaking attack besides nair (frame 5) and fair (frame 5).

## As the training dummy

- Light (same weight as Young Link), floaty (same fall speed as Peach), very large
  hurtbox [wiki:Mewtwo_(SSBM)]. Combos and juggles on Mewtwo are long; vertical kills
  come early.
- Tech rolls travel far but are slow: an ideal dummy for learning to react to tech
  options [wiki:Mewtwo_(SSBM)].
- Not on the wiki's list of characters [Sheik](sheik.md) chain grabs with dthrow
  [wiki:Chain_grab]; expect tech chases.
- Good CPU choices: DI away and double jump out of juggles; tech away (long distance);
  recover with mixed teleport end points.
- Numeric thresholds: Unknown from sources read.

## Matchup notes

### vs Jigglypuff

Named by the wiki as Mewtwo's biggest struggle among commonly played characters
[wiki:Mewtwo_(SSBM)].

### vs Fox and Falco

Mewtwo gets real reward here: uthrow and dthrow chain grabs, fair to regrab, and bthrow
kills [wiki:Mewtwo_(SSBM)] [wiki:Chain_grab]. But lasers are hard to avoid with a large
floaty body and the reflector does not turn them against their owner, and both kill
Mewtwo early off the top [wiki:Mewtwo_(SSBM)].

### vs Sheik and Captain Falcon

Both are on the dthrow chain grab list [wiki:Chain_grab]. Both tech chase Mewtwo easily
because of its slow tech rolls [wiki:Mewtwo_(SSBM)].

### vs Marth

Tail tilts compete with [Marth](marth.md)'s sword at range, but Marth's grab and
juggles are severe on a big floaty target [unverified].

## Drill seeds

### Teleport recovery mixup

- **id:** `mewtwo-teleport-recovery`
- **Goal:** Choose the teleport end point the edgeguarder is not covering.
- **Player:** Mewtwo
- **CPU:** Marth, Sheik, Fox, Captain Falcon
- **Setup:** Mewtwo in tumble off stage at varying distance and height, double jump
  available or not, 50-110%.
- **CPU behaviour:** Randomly grabs the ledge, waits on stage near the edge with a smash,
  or jumps out with an aerial.
- **Success:** Mewtwo reaches ledge, stage or platform and is not hit for 60 frames.
- **Fail:** Hit or stock lost.
- **Variations:** No double jump; require a Confusion or Disable stall first; require the
  bair double jump extension.
- **Data needed:** Teleport distance and intangibility (frames 8-17 of 32), landing lag
  by landing type, double jump height.

### Throw choice at kill percent

- **id:** `mewtwo-kill-throw`
- **Goal:** Pick uthrow or bthrow correctly and land the grab.
- **Player:** Mewtwo
- **CPU:** Peach, Jigglypuff, Marth, Sheik (uthrow); Fox, Falco, Captain Falcon (bthrow)
- **Setup:** CPU at 100-130% standing or shielding at a random stage position.
- **CPU behaviour:** Shields, pokes or dash dances; uses survival DI when thrown.
- **Success:** CPU dies from the throw.
- **Fail:** Wrong throw and the CPU survives; grab whiffs.
- **Variations:** Start from dtilt on shield; start from wavedash distance.
- **Data needed:** Throw knockback values (uthrow 12%/90/100/70, bthrow 11%/135/70/80),
  blast zones, CPU weight and fall speed.

### Chain grab on Fox and Bowser

- **id:** `mewtwo-dthrow-chaingrab`
- **Goal:** Follow DI and regrab after dthrow or uthrow.
- **Player:** Mewtwo
- **CPU:** Bowser, Fox, Falco, Captain Falcon, Sheik
- **Setup:** CPU at 0% in grab at centre stage.
- **CPU behaviour:** Random DI each throw; jumps or attacks as soon as possible.
- **Success:** N regrabs (start with 3), then a finisher (fair, uthrow).
- **Fail:** CPU acts before the regrab.
- **Variations:** Uthrow, fair, regrab loop on Fox and Falco; higher starting percent.
- **Data needed:** Dthrow release frame 25 of 49 and knockback, grab frames, CPU fall
  speed.

### DJC fair conversion

- **id:** `mewtwo-djc-fair`
- **Goal:** Land a double-jump-cancelled fair and follow up.
- **Player:** Mewtwo
- **CPU:** Fox, Falco, Marth, Sheik
- **Setup:** CPU standing at 20-60%; Mewtwo at wavedash distance.
- **CPU behaviour:** Random DI; acts as soon as hitstun ends.
- **Success:** Fair connects within a few frames of the minimum DJC height and a second
  hit or grab lands before the CPU acts.
- **Fail:** Mewtwo lands before the hitbox, or the CPU escapes.
- **Variations:** Start from dtilt; end with a stored Shadow Ball.
- **Data needed:** Fair frames 5-7, landing lag 25/12, double jump rise profile.

### Shadow Ball tech chase

- **id:** `mewtwo-shadow-ball-techchase`
- **Goal:** Use a full Shadow Ball or dsmash to punish a tech.
- **Player:** Mewtwo
- **CPU:** Fox, Falco, Captain Falcon, Sheik
- **Setup:** Mewtwo holds a full charge; CPU at 90-110% is knocked down by dthrow.
- **CPU behaviour:** Tech in place, away, toward, or no tech.
- **Success:** CPU is hit by Shadow Ball, or by jab reset into dsmash on a missed tech,
  and dies.
- **Fail:** CPU gets away.
- **Variations:** Platform knockdowns; lower percents with fair as the punish.
- **Data needed:** Shadow Ball release timing and speed, CPU tech data, jab frame 8,
  dsmash frame 20.

### Tail spacing on shield

- **id:** `mewtwo-dtilt-spacing`
- **Goal:** Hit shields with the tip of dtilt and stay unpunished.
- **Player:** Mewtwo
- **CPU:** Marth, Sheik, Fox, Peach
- **Setup:** CPU shielding at centre stage; Mewtwo at wavedash distance.
- **CPU behaviour:** After shieldstun uses its fastest out-of-shield punish.
- **Success:** Dtilt hits shield and the CPU's punish whiffs; bonus for a grab afterward.
- **Fail:** Mewtwo is hit or grabbed.
- **Variations:** CPU sometimes does not shield (confirm into fair or grab).
- **Data needed:** Dtilt range, interruptible from frame 20, shieldstun for 5-9%, CPU
  out-of-shield data.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlMt.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/mewtwo.json`](../framedata/mewtwo.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 8 | 6 | 83 | 0 | 100 | 20 | darkness | 29 | 26 | 4 | -13 |  |
| Rapid jab start | `rapid_jab_start` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Rapid jab loop | `rapid_jab_loop` | 7, 14, 21, 28, 35, 42, 49 | 2 | 70 | 0 | 70 | - | darkness | 50 | - | 2 | -41 |  |
| Rapid jab end | `rapid_jab_end` | - | - | - | - | - | - | - | 13 | - | - | - |  |
| Dash attack | `dash_attack` | 10-14 | 9 | 80/110 | 80 | 60 | - | darkness | 49 | 38 | 6 | -21 |  |
|  |  | 15-29 | 6 | 80/110 | 40 | 60 | - | darkness |  |  | 4 | -18 |  |
| Forward tilt (angled up) | `ftilt_high` | 6-8 | 10/8/5 | Sakurai | 20/10/0 | 100 | - | slash | 31 | 29 | 6 | -16 |  |
| Forward tilt | `ftilt` | 6-8 | 10/8/5 | Sakurai | 20/10/0 | 100 | - | slash | 31 | 29 | 6 | -16 |  |
| Forward tilt (angled down) | `ftilt_low` | 6-8 | 10/8/5 | Sakurai | 20/10/0 | 100 | - | slash | 31 | 29 | 6 | -16 |  |
| Up tilt | `utilt` | 6 | 10/8/6/5 | 110/Sakurai | 0/70 | 115/114/80 | - |  | 31 | 28 | 6 | -15 |  |
|  |  | 7-11 | 10/8/6/5 | 78 | 60/50/40 | 114 | - |  |  |  | 6 | -14 |  |
| Down tilt | `dtilt` | 5-7 | 9/8/5 | 80 | 40 | 80 | - |  | 29 | 20 | 6 | -8 |  |
| Forward smash | `fsmash` | 18-19 | 12/20 | Sakurai | 30/21 | 80/75 | - | darkness | 59 | 52 | 10 | -23 | charge hold frame 14 |
| Up smash | `usmash` | 9-10, 13-14, 17-18, 21-22, 25-26, 29-30 | 1 | 95/170 | 0 | 100 | 40/18/8 | darkness | 79 | 70 | 2 | -58 | charge hold frame 1 |
|  |  | 33-34 | 10 | 90/80 | 40 | 118 | - | darkness |  |  | 6 | -30 |  |
| Down smash | `dsmash` | 20-21 | 15 | Sakurai | 20 | 103 | - | darkness | 59 | 38 | 8 | -9 | charge hold frame 17 |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 5-6, 9-10, 13-14, 17-18, 21-22, 25-26, 29-30, 33-34 | 2/1 | 160/110 | 20 | 100 | 20/40 | electric | 54 | 42 | 2 | 26 | 13 | <5, >38 | -11 |  |
|  |  | 37-38 | 4 | Sakurai | 70 | 80 | - | electric |  |  | 3 |  |  |  | -10 |  |
| Forward air | `fair` | 5-7 | 14 | 84 | 40 | 100 | - | darkness | 39 | 36 | 8 | 25 | 12 | <1, >34 | -4 |  |
| Back air | `bair` | 12-15 | 9/11/13 | Sakurai | 0 | 100 | - |  | 31 | - | 7 | 28 | 14 | <3, >29 | -7 |  |
| Up air | `uair` | 9-11 | 10/12/14 | 55 | 0 | 100 | - |  | 37 | 35 | 8 | 20 | 10 | <4, >32 | -2 |  |
| Down air | `dair` | 18-21 | 14/15/16 | 270 | 10 | 100 | - |  | 57 | 47 | 9 | 28 | 14 | <6, >44 | -5 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 9-10 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 12 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 5 | 5 | 78 | 0 | 100 | 38 | - | 18 | 74 |  |
| Back throw | `bthrow` | 11 | 11 | 45 | 70 | 80 | - | - | 27 | 49 |  |
| Up throw | `uthrow` | 12 | 12 | 90 | 100 | 70 | - | - | 42 | 69 |  |
| Down throw | `dthrow` | 11 | 6 | 69 | 65 | 50 | - | - | 25 | 49 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Shadow Ball, ground, Start | `special_n_start` | - | - | - | - | - | - | - | 17 | - | - | - |  |
| Neutral B: Shadow Ball, ground, Loop | `special_n_loop` | 1-3, 6-7 | 2 | 80 | 20 | 100 | - | electric | 7 | - | 2 | - |  |
| Neutral B: Shadow Ball, ground, Loop | `special_n_loop_297` | 1-3, 6-7 | 2 | 80 | 20 | 100 | - | electric | 7 | - | 2 | - |  |
| Neutral B: Shadow Ball, ground, Cancel | `special_n_cancel` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Neutral B: Shadow Ball, ground, End | `special_n_end` | - | - | - | - | - | - | - | 23 | - | - | - |  |
| Neutral B: Shadow Ball, air, Start | `special_air_n_start` | - | - | - | - | - | - | - | 17 | - | - | - |  |
| Neutral B: Shadow Ball, air, Loop | `special_air_n_loop` | 1-3, 6-7 | 2 | 80 | 20 | 100 | - | electric | 7 | - | 2 | - |  |
| Neutral B: Shadow Ball, air, Loop | `special_air_n_loop_302` | 1-3, 6-7 | 2 | 80 | 20 | 100 | - | electric | 7 | - | 2 | - |  |
| Neutral B: Shadow Ball, air, Cancel | `special_air_n_cancel` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Neutral B: Shadow Ball, air, End | `special_air_n_end` | - | - | - | - | - | - | - | 23 | - | - | - |  |
| Side B: Confusion, ground | `special_s` | 12-15 | 0 | 40 | 0 | 100 | - | grab | 55 | - | - | - |  |
| Side B: Confusion, air | `special_air_s` | 12-15 | 0 | 40 | 0 | 100 | - | grab | 55 | - | - | - |  |
| Up B: Teleport, ground, Start | `special_hi_start` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Up B: Teleport, ground | `special_hi` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Up B: Teleport, ground, Lost | `special_hi_lost` | - | - | - | - | - | - | - | 15 | - | - | - |  |
| Up B: Teleport, air, Start | `special_air_hi_start` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Up B: Teleport, air | `special_air_hi` | - | - | - | - | - | - | - | 15 | - | - | - |  |
| Down B: Disable, ground | `special_lw` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Down B: Disable, air | `special_air_lw` | - | - | - | - | - | - | - | 39 | - | - | - |  |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-21 | - | 37 | 29 |  |
| Roll forward | `roll_forward` | intangible 4-21 | - | 37 | - |  |
| Roll backward | `roll_backward` | intangible 4-19 | - | 37 | - |  |
| Air dodge | `airdodge` | intangible 4-29 | - | 39 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-31 | 18-31 (6/5%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-21 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-22 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-35 | 20-35 (7/5%) | 49 | - |  |
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
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 33 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-46 | 50-52 (10%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-22 | 26-30 (8/6%) | 55 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-74 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-27 | - | 49 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-21 | - | 21 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 46 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-15 | - | 15 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 37 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Shield grab | direct | 7 | `grab` |
| Neutral air | jump | 10 | `nair` |
| Forward air | jump | 10 | `fair` |
| Up smash | jump cancel | 10 | `usmash` |
| Up air | jump | 14 | `uair` |
| Back air | jump | 17 | `bair` |
| Down air | jump | 23 | `dair` |
| Spot dodge | direct | intangible 2-21 of 37 | `spotdodge` |
| Roll forward | direct | intangible 4-21 of 37 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 37 | `roll_backward` |
| Wavedash | jump | actionable on frame 17 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Mewtwo indexed by [The Melee Library](https://www.meleelibrary.com/#mewtwo) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Mewtwo Techs Guide](https://www.youtube.com/watch?v=XrRwivjkaRY&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=8&t=0s) | Third Chair | Video guide on performing useful Mewtwo tech in 2020. |
| [Mewtwo Melee Chaingrab Guide](https://www.youtube.com/watch?v=vDjmN5vOcMs&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=8&t=0s) | Third Chair |  |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Mewtwo (SSBM): https://www.ssbwiki.com/Mewtwo_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Mewtwo_(SSBM)/Up_special , /Up_throw ,
  /Back_throw , /Down_throw , /Forward_throw , /Grab , /Down_tilt , /Up_tilt ,
  /Forward_tilt , /Down_smash , /Forward_aerial , /Back_aerial , /Up_aerial ,
  /Down_aerial , /Neutral_aerial , /Neutral_special , /Side_special , /Down_special
- SSBWiki, Teleport: https://www.ssbwiki.com/Teleport
- SSBWiki, Double jump cancel: https://www.ssbwiki.com/Double_jump_cancel
- SSBWiki, Shadow Ball: https://www.ssbwiki.com/Shadow_Ball
- SSBWiki, Confusion: https://www.ssbwiki.com/Confusion
- SSBWiki, Disable: https://www.ssbwiki.com/Disable
- SSBWiki, Chain grab, Lock, Wavedash, Moonwalk: https://www.ssbwiki.com/Chain_grab ,
  https://www.ssbwiki.com/Lock , https://www.ssbwiki.com/Wavedash ,
  https://www.ssbwiki.com/Moonwalk
- Melee Library, Mewtwo section (two video cards; titles only).
- Frame data dump: `Mewtwo.json`.
