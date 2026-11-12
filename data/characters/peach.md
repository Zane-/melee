---
schema: melee-character/v1
id: peach
name: Peach
aliases: [Princess Peach, Peach Toadstool]
tier: "A (7th of 26), 2021 tier list (13th, PG Stats)"
archetype: [floaty, punish-heavy, edgeguarder, projectile, mixup, technical]
related: [jigglypuff, samus]
summary: Peach wins by floating at ground level to throw lagless aerials, punishing crouch cancels and bad approaches with down smash, and converting dash attack, throws and turnips into long juggles and off-stage edgeguards.
key_tech: [float, float-cancel, ground-float-aerials, double-jump-cancel, turnip-pull-and-throw, crouch-cancel-down-smash, dash-attack-conversions, up-throw-chain-grab, wall-bomber, parasol-fast-fall, ledge-float-return]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlPe.dat
framedata: ../framedata/peach.json
code: src/melee/ft/kinds/ftPeach
specials:
  neutral_b: "Toad"
  side_b: "Peach Bomber"
  up_b: "Peach Parasol"
  down_b: "Vegetable (turnip pull)"
attributes:
  weight: 90
  gravity: 0.08
  fall_speed: 1.5
  fast_fall_speed: 2
  jump_squat: 5
  jumps: 2
  walk_speed: 0.85
  dash_speed: 1.2
  run_speed: 1.3
  traction: 0.1
  air_speed: 1.1
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [2, 16, 3]
  jab2: [3, 17, 2]
  dash_attack: [6, 36, 12]
  utilt: [9, 37, 12]
  dtilt: [12, 26, 12]
  fsmash: [null, 48, 0]
  usmash: [13, 45, 19]
  dsmash: [5, 40, 14]
  nair: [3, 42, 14]
  fair: [16, 51, 15]
  bair: [6, 38, 14]
  uair: [7, 34, 14]
  dair: [12, 36, 3]
  grab: [7, 31, 0]
  dash_grab: [7, 41, 0]
  pummel: [14, 26, 3]
  fthrow: [14, 34, 8]
  bthrow: [20, 50, 9]
  uthrow: [20, 50, 6]
  dthrow: [34, 65, 7]
  fsmash_298: [15, 40, 17]
  fsmash_299: [15, 40, 17]
  fsmash_300: [15, 40, 12]
  special_n: [null, 30, 0]
  special_s_start: [null, 22, 0]
  special_s_end: [null, 33, 0]
  special_s_jump: [1, 30, 0]
  special_air_s_start: [null, 32, 0]
  special_air_s_end: [null, 28, 0]
  special_air_s_end_307: [null, 20, 0]
  special_hi_start: [6, 41, 5]
  special_hi_end: [null, 9, 0]
  special_air_hi_start: [6, 41, 5]
  special_air_hi_end: [null, 9, 0]
  special_lw: [null, 65, 0]
  special_lw_hit: [null, 75, 0]
  special_air_lw: [null, 65, 0]
  special_air_lw_hit: [null, 75, 0]
oos:  # option: frame the hitbox is out
  special_hi_start: 7
  grab: 7
  nair: 8
  bair: 11
  uair: 12
  usmash: 14
  dair: 17
  fair: 21
resources: 62
# generated: end
---

# Peach

<!-- GENERATED:attributes -->
## Attributes

Read from `PlPe.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 90 |
| Gravity | 0.08 |
| Terminal fall speed | 1.5 |
| Fast-fall speed | 2 |
| Jump squat (frames before airborne) | 5 |
| Full hop / short hop initial Y speed | 2.2 / 1.6 |
| Air jump Y multiplier | 0.7 |
| Jumps | 2 |
| Walk max speed | 0.85 |
| Dash initial speed / run max speed | 1.2 / 1.3 |
| Ground friction (traction) | 0.1 |
| Air max horizontal speed | 1.1 |
| Air acceleration (base + stick) | 0.01 + 0.06 |
| Air friction | 0.005 |
| Normal landing lag | 4 |
| Shield size | 11.875 |
<!-- /GENERATED:attributes -->

## Overview

Peach is a slow, floaty, below-average-weight character (weight 90, fall speed 1.5 [wiki:Peach_(SSBM)]) whose game is built on one unique ability: holding jump makes her hover ("float") at a fixed height for up to 2.5 seconds [wiki:Float]. Any aerial started during a float lands with the normal 4-frame landing instead of its landing lag ("float cancel") [wiki:Float], so Peach can hover a few pixels above the ground and throw aerials that are effectively lagless. On the ground she is slow (second-slowest dash in the game, shortest wavedash [wiki:Peach_(SSBM)]) and relies on three things: down smash, dash attack and her grab.

In neutral she walls with float-cancelled fair and nair, throws turnips (down B) to force reactions, and punishes approaches with crouch cancel into down smash. Her punish game is juggle- and edgeguard-based: dash attack, down throw, up throw and dair pop the opponent up, float aerials and uair keep them there, and fair, nair, bair or a turnip finish off stage. She dies mostly off the top (floaty and fairly light) and to being out-ranged or out-run; her recovery is very long but slow and predictable. Execution is moderate: float cancelling is easier than [L-cancelling](../techniques/l-cancel.md), but precise float heights, turnip handling and edgeguard routes take time.

## Strengths and weaknesses

- **Strengths:**
  - Float-cancelled aerials: every aerial can be made to land in 4 frames [wiki:Float], which makes fair and nair safe on shield and hard to shield grab.
  - Nair hits on frame 3 [fd] and is one of the fastest [out of shield](../techniques/out-of-shield.md) options in the game after her 5-frame jump squat [wiki:Peach_(SSBM)].
  - Down smash: five hits, 14%/12% each, angle 140 (low, backwards relative to the hitbox side) [fd][wiki:Peach_(SSBM)/Down_smash]. It punishes [crouch cancel](../techniques/crouch-cancel.md) harder than any other move in the game because a crouching opponent is not knocked out of the later hits.
  - Turnips: a reusable item projectile for neutral, combos and edgeguards, with a small chance of a huge-damage pull.
  - Strong throws: fthrow is the strongest forward throw in the game; uthrow and dthrow start chain grabs and juggles [wiki:Peach_(SSBM)].
  - Recovery distance: float + double jump + side B + up B with a slow-falling parasol.
  - Off-stage edgeguarding: she can float off stage and hit with bair/fair/nair, then still make it back.
- **Weaknesses:**
  - Slow ground movement and the shortest wavedash; she cannot chase or run away well [wiki:Peach_(SSBM)].
  - Dies early off the top to vertical finishers (floaty, weight 90) [wiki:Peach_(SSBM)].
  - Tilts are slow; ground approach is essentially dash attack or nothing [wiki:Peach_(SSBM)].
  - Recovery is slow and linear once the float is used; the parasol leaves her open from below and from the side.
  - Turnip pull is a 29-frame commitment and the turnip is lost if she is hit during it [wiki:Peach_(SSBM)/Down_special].
  - Loses badly to [Jigglypuff](jigglypuff.md), who out-ranges her in the air and is hard for her to kill [wiki:Peach_(SSBM)].

## Character tech

### Float

- **id:** `float`
- **What:** Holding the jump button (or up on the stick) while airborne makes Peach hover at her current height. She can drift horizontally and attack while hovering.
- **Inputs:** Jump, then keep jump held when she reaches the desired height. To float at a chosen height on demand ("auto-float"): while airborne and holding jump, press down on the control stick; she starts floating at that height [wiki:Float]. From the ground, hold down, then press and hold jump to float just above the ground ("ground float").
- **Timing:** Float lasts up to 2.5 seconds per airtime [wiki:Float] (a player guide rounds it to "about 3 seconds" [lib:The Melee Puff Bible]). One float per airtime; it is restored only by landing, not by grabbing the ledge or being hit [wiki:Float]. Pressing down+jump while falling must be simultaneous, or she spends her double jump instead [wiki:Float].
- **Used for:** Lagless aerials (see float cancel), spacing fair at any height, holding a turnip and still using aerials, off-stage edgeguards, stalling recovery timing, escaping juggles.
- **Common errors:** Releasing jump early (she drops and the aerial lands with full lag); double jumping instead of floating when falling (double-jump ring and sound appear) [wiki:Float]; floating too high so aerials whiff over crouching opponents.
- **Drill idea:** Target heights marked on screen; player must enter float within N frames of leaving the ground and hold it at ground-float, short-hop and full-hop heights.

### Float cancel

- **id:** `float-cancel`
- **What:** If Peach starts an aerial while floating, then lands at any point during that aerial (still floating or not), she gets the normal 4-frame landing as if the move had [auto-cancelled](../techniques/auto-cancel.md) [wiki:Float]. No L-cancel input is needed.
- **Inputs:** Float (usually ground float) -> aerial -> release jump (or press down) so she drops to the ground before the aerial ends.
- **Timing:** Landing is 4 frames [wiki:Float][wiki:Peach_(SSBM)] instead of the aerial's normal landing lag, e.g. fair 25 frames (12 L-cancelled) and nair 17 (8 L-cancelled) [fd]. The aerial must have been started during the float; an aerial started before the float does not get the benefit.
- **Used for:** Everything. Float-cancel (FC) fair is her main spacing and shield-pressure move; FC nair is the fast close-range option; FC dair is a combo starter and shield pressure; FC bair and uair extend combos. One community estimate puts FC fair at about +4 on shield at best (hit as late as possible), more often +1 to +2 in practice [lib:20XX+XY].
- **Common errors:** Releasing float before pressing attack (aerial is not float-cancelled, full landing lag); attacking too high so the hitbox whiffs and she lands in front of the opponent with nothing out; dropping late so the opponent can act before she lands.
- **Drill idea:** CPU shields; player does ground float -> fair/nair -> land; measure frames from hit to Peach being actionable and whether the following grab/jab/dsmash beats the CPU's fastest out-of-shield option.

### Ground-float aerial strings

- **id:** `ground-float-aerials`
- **What:** Chaining aerials out of repeated ground floats: float, aerial, land (4 frames), act. The standard pressure strings end in jab, grab, down smash, another float, or a retreat.
- **Inputs:** Hold down + press and hold jump (ground float) -> aerial -> release jump to land -> next action. Common strings: FC fair -> jab/grab/dsmash; FC nair -> dsmash; FC dair (hits on frames 12-13, 18-19, 24-25, 30-31 [wiki:Peach_(SSBM)/Down_aerial]) -> nair ("float dair into +3 nair" is a library card title [lib:Float Dair into +3 Nair]).
- **Timing:** Jump squat is 5 frames [wiki:Peach_(SSBM)]; nair hitbox is out on frame 3 of the aerial, fair on frame 16 [fd]. A library source notes FC fair followed by dsmash is safe on Ice Climbers' shield, with no escape by buffered roll [lib:20XX+XY].
- **Used for:** Shield pressure, catching dash-dancers with the long fair, conditioning the opponent to hold shield (then grab) or to act (then dsmash).
- **Common errors:** Predictable timing (opponents jump over or grab the landing); always following with dsmash (dsmash is very unsafe if fully shielded: about -22 on Ice Climbers' shield [lib:20XX+XY]).
- **Drill idea:** CPU shields then picks one of {hold shield, grab out of shield, roll, jump out}; player must choose the string ender that beats it.

### Double jump cancel (DJC)

- **id:** `double-jump-cancel`
- **What:** Peach has a delayed double jump (it sinks before it rises). Starting an aerial immediately after the double jump cancels the upward momentum, so she attacks low and lands quickly [wiki:Double_jump_cancel].
- **Inputs:** Jump -> double jump -> aerial immediately. Related: "double jump land" (double jump just before touching a platform/ground so she lands without rising).
- **Timing:** The aerial must come out during the first frames of the double jump, before upward speed applies. A related movement trick, the "Prince pivot" (double-jump-land out of a run to act quickly), takes at minimum 7 frames according to its library card [lib:Prince Pivots].
- **Used for:** Low aerials without spending the float (which is then still available for recovery or a follow-up), auto-cancelled fair for movement, edgeguarding from the ledge.
- **Common errors:** Late aerial input (she rises to full double jump height); using it off stage and having no double jump left to recover.
- **Drill idea:** Player must land a DJC nair/fair on a standing CPU and be grounded within N frames of leaving the ground, with float still unused.

### Turnip pull and throw

- **id:** `turnip-pull-and-throw`
- **What:** Down B on the ground pulls a turnip (an item). Peach then throws it, drops it (Z), or carries it while floating and attacking.
- **Inputs:** Down B (grounded only; it cannot be started in the air [wiki:Vegetable]). Throw with A/Z + direction (tilt or smash); Z in the air with no direction drops it ("z-drop"). While holding a turnip she cannot use grounded A attacks and can only use aerials out of float [lib:The Melee Puff Bible][wiki:Float].
- **Timing:** Pull animation is 29 frames; the turnip exists from frame 14; if Peach is hit at any point in those 29 frames the turnip disappears [wiki:Peach_(SSBM)/Down_special]. Turnip face odds: about 60% smiley, 6.8% wink, 1.7% dot-eyes, 1.7% stitch-face, 1/128 for a non-turnip item (Mr. Saturn, Bob-omb, Beam Sword) [wiki:Peach_(SSBM)/Down_special]. Base damage 2% (normal faces), 6% wink, 12% dot-eyes, 30% stitch; thrown damage = base - 0.4 + 3 x item speed; a z-dropped or knocked-loose turnip does 5-7%; Bob-omb always 25% [wiki:Peach_(SSBM)/Down_special]. A turnip lasts about 3.5 seconds in the air and bounces off shields and clashing attacks, so she can re-catch it [wiki:Vegetable].
- **Used for:** Forcing the opponent to act (shield, jump, catch), covering her own approach (throw, then float in behind it), combo extension (z-drop into aerial), edgeguarding (a turnip knocks Fox/Falco out of up B start-up; the interaction is covered in a library thread [lib:Royal Academy Finishing School: Frame Data Application Thread], not read). Stitch-face and Bob-omb pulls kill early, so opponents must pressure her rather than let her pull freely [wiki:Peach_(SSBM)/Down_special].
- **Common errors:** Pulling inside the opponent's threat range (hit during the 29 frames, turnip lost); throwing at a range where the opponent catches it and now has a projectile; forgetting that holding a turnip disables grounded attacks.
- **Drill idea:** CPU approaches from a randomised distance; player must decide pull / no pull; success if the pull completes (frame 29) unhit and the throw hits or is shielded.

### Crouch cancel into down smash

- **id:** `crouch-cancel-down-smash`
- **What:** Peach crouches through a weak hit ([crouch cancel](../techniques/crouch-cancel.md) / [ASDI down](../techniques/asdi.md)) and immediately down smashes. Separately, her own dsmash destroys opponents who crouch cancel it, because they stay inside the remaining hits.
- **Inputs:** Hold down before the hit connects -> C-stick down (or down + A) as soon as hitlag ends.
- **Timing:** Dsmash hits on frames 5-6, 9-10, 13-14, 17-18, 21-22; legs are intangible on frames 3-24; total 39 frames [wiki:Peach_(SSBM)/Down_smash]. Each hit is 14% (outer) or 12% (inner) [fd]. Against a crouch-cancelling opponent at low percent multiple hits connect; the theoretical maximum is about 65% [wiki:Peach_(SSBM)/Down_smash]. It can kill fastfallers near the edge from as low as about 20% when several hits connect [wiki:Peach_(SSBM)/Down_smash].
- **Used for:** Punishing unsafe aerials and tilts on her at low percent, punishing opponents who try to crouch cancel her, shield poking (the low hitboxes hit feet).
- **Common errors:** Dsmashing a full shield at close range (unsafe; Ice Climbers can wavedash out of shield and grab [lib:20XX+XY]); trying to CC at high percent, where the hit knocks her down instead.
- **Drill idea:** CPU Fox/Sheik/Marth does a low aerial or tilt at Peach at 0-30%; success if Peach's dsmash hitbox connects within N frames of being hit and deals at least two hits.

### Dash attack conversions

- **id:** `dash-attack-conversions`
- **What:** Dash attack ("the push") is fast, lingers, and launches upward; it is her main burst option and [tech chase](../techniques/tech-chase.md) tool [wiki:Peach_(SSBM)/Dash_attack].
- **Inputs:** Run -> A. Follow with float/jump aerials, utilt, uthrow chain grab, or up B.
- **Timing:** Clean hit frames 6-8 (12%, angle 80), late hit frames 9-20 (8%/7%); IASA 36 [fd][wiki:Peach_(SSBM)/Dash_attack].
- **Used for:** Punishing landings and rolls, covering tech options on the main stage (the long late hit covers a wide timing window), starting juggles on fastfallers, setting up the uthrow chain grab [wiki:Peach_(SSBM)].
- **Common errors:** Using it on shield at close range (she ends in front of the opponent in lag; Jigglypuff can shield or crouch under it and Rest [lib:The Melee Puff Bible]); hitting with the late hit at high percent where it does not launch enough to follow up.
- **Drill idea:** CPU techs in a random direction after a knockdown; player must hit with dash attack and land one follow-up aerial before the CPU can act.

### Up throw chain grab

- **id:** `up-throw-chain-grab`
- **What:** Uthrow launches almost straight up (angle 88 [wiki:Peach_(SSBM)/Up_throw]) with little knockback, so Peach can regrab characters that fall back quickly.
- **Inputs:** Grab -> up throw -> step under the opponent following their [DI](../techniques/di.md) -> grab again (jump-cancel grab or standing grab). End with usmash, a float aerial or fair when the regrab stops working.
- **Timing:** Uthrow releases on frame 25 of a 49-frame animation [wiki:Peach_(SSBM)/Up_throw], leaving 24 frames before Peach can move; standing grab is active on frames 7-8 [wiki:Peach_(SSBM)/Grab]. The percent window is not well sourced here: SSBWiki's move list says floaty and mid-fall-speed characters can be regrabbed from 0% and that fastfallers "must be around 40%" [wiki:Peach_(SSBM)]; community practice is a chain grab on Fox, Falco and Captain Falcon at low to mid percent on Final Destination [unverified]. Treat exact ranges as unknown until tested.
- **Used for:** Damage on fastfallers on stages without platforms, leading into usmash or an aerial finisher.
- **Common errors:** Not adjusting to DI behind (opponent lands behind her); grabbing too late so the opponent double jumps or shines out.
- **Drill idea:** Fox CPU on Final Destination with random DI (none / left / right) on each throw; count consecutive regrabs.

### Wall bomber

- **id:** `wall-bomber`
- **What:** Side B (Peach Bomber) against a wall makes Peach rebound upward slightly, which can be repeated to climb a wall while recovering [wiki:Peach_Bomber].
- **Inputs:** Side B toward a vertical stage wall; on rebound, side B again.
- **Timing:** Aerial side B searches for a target on frames 32-41 of a 56-frame animation (grounded: frames 22-31 of 46) [wiki:Peach_(SSBM)/Side_special]. Landing after a miss has 33 frames of lag [wiki:Peach_(SSBM)/Side_special].
- **Used for:** Extra recovery height on stages with walls (e.g. Yoshi's Story) [wiki:Peach_Bomber]. Repeating it to stall is banned in tournaments [wiki:Peach_Bomber]. On hit the bomber does 16% (18% if input as a smash) [wiki:Peach_(SSBM)/Side_special] and heavy shield damage (19.88 of a 60-point shield for the smash version per the library card [lib:Peach Bomber Shield Breaker]).
- **Common errors:** Using it with no wall in range (very long lag, easy edgeguard); bombing into an opponent's shield on stage.
- **Drill idea:** Start Peach below the ledge next to a wall with no jump or float; success if she reaches the ledge using bombers then up B.

### Parasol fast fall

- **id:** `parasol-fast-fall`
- **What:** After up B opens the parasol, pressing down closes it and she falls normally (and can fast fall); pressing up re-opens it [wiki:Peach_Parasol].
- **Inputs:** Up B -> (parasol opens automatically after the rise) -> down to close -> up to re-open.
- **Timing:** Rising hit 1 on frames 6-9, then multi-hits to frame 29; rise animation 40 frames; she can grab the ledge only when facing it, from frame 34 of the rise [wiki:Peach_(SSBM)/Up_special]. Landing lag is 30 frames with the parasol open and 4 frames with it closed [wiki:Peach_(SSBM)/Up_special]. The parasol can stay open for 944 frames in total [wiki:Peach_(SSBM)/Up_special].
- **Used for:** Mixing descent speed during recovery, landing with 4 frames of lag instead of 30, dropping below the ledge to grab it.
- **Common errors:** Landing with the parasol open (30 frames of lag); facing away from the ledge during the rise (no ledge grab).
- **Drill idea:** Peach starts high off stage with only up B; CPU waits at the ledge; success if Peach lands on stage with the closed-parasol landing or grabs the ledge without being hit.

### Ledge float return

- **id:** `ledge-float-return`
- **What:** Getting from the ledge onto the stage using double jump and float instead of the standard [ledge options](../techniques/ledge-options.md). Peach has no fully invincible way back on stage [lib:20XX+XY].
- **Inputs:** One documented sequence: drop from ledge -> double jump -> float for 1 frame -> land; done perfectly there is a single punishable frame before she can shield [lib:20XX+XY]. Simpler alternative: drop -> air dodge up and inward at 45 degrees [lib:20XX+XY]. Follow-ups after landing: roll, jab (frame 2 [fd]), FC fair that slips back to the ledge, nair.
- **Timing:** See above; other exact frame counts are in library sources not read (e.g. [lib:Peach's Shitty Edge Options Optimized]).
- **Used for:** Returning to stage against opponents who wait outside ledge-attack range.
- **Common errors:** Floating too long above the ledge (free hit); using the double jump and then being hit off stage with only float/up B left.
- **Drill idea:** CPU stands at a random distance from the ledge and attacks on a randomised timer; success if Peach reaches a grounded, actionable state without being hit.

## Neutral game

- **FC fair** is the main tool: long reach, 15%, high base knockback (enough to tumble heavy characters at 0% [wiki:Peach_(SSBM)/Forward_aerial]), no weak late hit. It beats crouch cancel. Its weakness is start-up (frame 16 [fd]); opponents dash in and out of its range or jump over it.
- **FC nair** (frame 3, 14% clean [fd]) covers close range and trades well. It is the answer when the opponent is already inside fair range.
- **Turnips** make the opponent move first. Throw then follow; or hold one while floating and threaten both the throw and an aerial.
- **Dash attack** is the only fast ground approach; use it on landings, whiffs and rolls rather than raw.
- **Crouch / CC dsmash** at low percent deters weak pokes. Jab (frame 2 [fd]) interrupts slow pressure and leads to grab or dsmash.
- **Shield and nair out of shield** against rushdown; Peach players also [powershield](../techniques/powershield.md) Falco's lasers [lib:Hollabarracuda Girl: A Peach Tutorial].
- Peach wants the opponent in the corner or above her. She does not want to chase: her dash is the second slowest in the game [wiki:Peach_(SSBM)].
- Typical float heights: ground float for pressure and combos; short-hop height to hit standing opponents and stay above low pokes; full-jump height to punish approaches from above [wiki:Float].

## Punish game

Peach's combos are juggles. A launcher (dash attack, dthrow, uthrow, dair, dtilt, usmash sourspot) puts the opponent above her; she follows with float or jump aerials (uair to keep them up, nair/bair/fair to send them off stage), then edgeguards. Against fastfallers, grabs lead to the uthrow chain grab and dsmash near the edge kills very early. Against floaties, combos are short and she relies on single strong hits, dsmash, and edgeguards.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| Dash attack (clean) | fastfallers | low to mid (typical) | uair / nair / utilt / regrab; up B for style | Launch angle 80; also sets up uthrow chain grab | [wiki:Peach_(SSBM)], [wiki:Peach_(SSBM)/Dash_attack] |
| Uthrow | fastfallers | see chain grab section | regrab, then usmash or aerial | Needs a flat stage | [wiki:Peach_(SSBM)] |
| Dthrow | floaties, heavies; fastfallers at high percent | typical | regrab, ftilt, or aerial depending on weight, fall speed and DI | Dthrow angle 108, release frame 43 of 64 | [wiki:Peach_(SSBM)], [wiki:Peach_(SSBM)/Down_throw] |
| FC dair | any (grounded) | low to mid (typical) | nair / fair / bair chosen by DI | Dair hits pop the opponent slightly up (angle 90) | [wiki:Peach_(SSBM)], [fd] |
| FC fair | any | spacing dependent | dash attack | Only if spaced so she lands close | [wiki:Peach_(SSBM)] |
| Dtilt | any (grounded) | typical | float aerial strings | Grounded hit sends up (angle 80 hitbox); arm hitbox meteors airborne targets | [wiki:Peach_(SSBM)], [fd] |
| Usmash (weak side/hand hit) | fastfallers | high | aerial | Sourspot only | [wiki:Peach_(SSBM)] |
| CC -> dsmash | opponents who hit her with weak moves, or who crouch | 0-30% is where multi-hit is most likely [unverified] | edgeguard | Up to ~65% if all five hits connect on a CCing target | [wiki:Peach_(SSBM)/Down_smash] |
| Jab 1 | any | low | grab / dsmash | Jab 1 is described as a combo starter; missed-tech jab resets are documented in a library thread (not read) | [wiki:Peach_(SSBM)], [lib:Jab Reset Data] |
| Turnip hit / z-drop | any | any | aerial, re-catch turnip | Turnips bounce off the target and can be re-caught | [wiki:Vegetable] |
| Ftilt | heavies without a double jump | low | repeated ftilt juggles | KOs above about 120% | [wiki:Peach_(SSBM)] |

### Chain grabs and tech chases

- **Uthrow chain grab (fastfallers).** Works on flat ground against characters who fall fast enough to come back into grab range. The sourced percent information is weak (see the technique entry): SSBWiki states fastfallers need to be "around 40%" and that mid-weight/floaty characters can be regrabbed at 0% [wiki:Peach_(SSBM)]; the usual community description is Fox/Falco/Captain Falcon at low-mid percent on Final Destination [unverified]. Escapes: DI behind/away to make her turn or move, double jump or shine once hitstun ends, landing on a platform and teching.
- **Dthrow chain grab.** SSBWiki lists dthrow regrabs on floaty characters, heavyweights, and fastfallers at high percent [wiki:Peach_(SSBM)]. No percent table was found.
- **Tech chase.** Dash attack is her standard main-stage tech-chase option because its hitbox lasts from frame 6 to frame 20 [fd] and covers a wide area [wiki:Peach_(SSBM)/Dash_attack]. On platforms she tech-chases from below with uair out of a full hop or low float [wiki:Peach_(SSBM)/Up_aerial]. Reaction tech chasing is covered in a library thread that could not be fetched [lib:Royal Academy Finishing School: Frame Data Application Thread].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Fair | any | Not sourced; strong at mid percent, off stage much earlier | 15%, base knockback 60, growth 70; best when it sends off stage | [fd], [wiki:Peach_(SSBM)/Forward_aerial] |
| Nair (clean) | any | Out-kills fair from about 100% on an 80-weight opponent | 14%, growth 100; low launch angle | [wiki:Peach_(SSBM)/Forward_aerial], [fd] |
| Bair (clean) | any | Not sourced | Reliable off-stage KO move, frames 6-9 clean | [wiki:Peach_(SSBM)/Back_aerial] |
| Uair | light/floaty (Jigglypuff) | above about 110% | Foot hitbox 14%, growth 120 | [wiki:Peach_(SSBM)], [fd] |
| Dsmash | fastfallers | from about 20% near the edge if several hits land; otherwise high percent single hit | Low angle (140) makes recovery hard | [wiki:Peach_(SSBM)/Down_smash] |
| Usmash (arm sweetspot) | any | about 73% fully charged; hand hit about 110-120% | Sweetspot is at her shoulder/arm, 19% | [wiki:Peach_(SSBM)] |
| Fthrow | Mario (reference) | 134% from the centre of Final Destination | Strongest fthrow in the game | [wiki:Peach_(SSBM)/Forward_throw] |
| Bthrow | any | above about 170% near the edge | Mostly used to start edgeguards instead | [wiki:Peach_(SSBM)] |
| Fsmash (frying pan) | any | about 120% | Random weapon; pan sends upward | [wiki:Peach_(SSBM)] |
| Fsmash (golf club tip) | any | about 130% fully charged | Sourspot does not kill until over 200% | [wiki:Peach_(SSBM)] |
| Ftilt | any | above about 120% | Sends straight up | [wiki:Peach_(SSBM)] |
| Dtilt meteor | grounded or off-stage | "under 150%" on grounded targets (as stated by the wiki) | Forearm hitbox, angle 270 | [wiki:Peach_(SSBM)], [fd] |
| Stitch-face turnip | any | very early | 1.7% pull chance, base 30% | [wiki:Peach_(SSBM)/Down_special] |
| Bob-omb | any | very early | 0.26% pull chance, 25% | [wiki:Peach_(SSBM)/Down_special] |

- **Edgeguards are her main kill source.** Float off stage and hit with bair/nair/fair; her float and double jump get her back. Float bair is the standard off-stage hit [wiki:Peach_(SSBM)/Back_aerial]; nair's low angle catches DI [wiki:Peach_(SSBM)/Neutral_aerial]; fair at low percent gimps because it tumbles at 0% [wiki:Peach_(SSBM)/Forward_aerial].
- **Turnips off stage.** A thrown turnip interrupts recoveries and forces a second up B from lower. Throwing backward gives a longer throw [lib:Extended Turnip Throw].
- **Dtilt at the ledge** meteors recovering opponents (forearm hitbox only) [wiki:Peach_(SSBM)].
- **Fsmash weapon cycling.** The weapon is random but never the same twice in a row; players swing in dead time until the pan appears so the next one is the longer club or racket [lib:20XX+XY].
- **Turnip "knitting".** During the opponent's respawn she pulls and discards turnips looking for a good one; a wink is good enough to stop [lib:20XX+XY].

## Recovery

- **Options:**
  - Float: up to 2.5 seconds of level flight [wiki:Float], with any aerial available for protection.
  - Double jump: a long, delayed double jump; can be double-jump-cancelled with an aerial.
  - Side B (Peach Bomber): small horizontal travel; rebounds upward off walls [wiki:Peach_Bomber]; hits for 16%/18% if it connects.
  - Up B (Peach Parasol): rising multi-hit, then a slow parasol descent with a disjointed hitbox above her; can close/re-open the parasol [wiki:Peach_Parasol].
  - Neutral B (Toad) adds a little stalling distance but is slow (64 frames) [wiki:Peach_(SSBM)].
  - Air dodge and a held turnip (throw it at the edgeguarder).
- **Mixups:** Order of float / double jump / up B; float high and wait, or drop low and double jump; fast fall with the parasol closed, re-open to stall; grab the ledge from below during up B (only when facing it, from frame 34 [wiki:Peach_(SSBM)/Up_special]); aerials during float (nair frame 3, uair frame 7, bair frame 6 [fd]) to hit edgeguarders.
- **Weaknesses:** Slow. Once float and double jump are gone she has only a predictable up B with 30 frames of landing lag if she lands with the parasol open [wiki:Peach_(SSBM)/Up_special]. The parasol protects from above, not from below or the side. Float holds her at one height, which makes her position predictable for 2.5 seconds. Being hit does not restore float [wiki:Float].

### Edgeguarding Peach

- **While she floats:** do not challenge the fair from the front at her height. Position below and in front of her, out of the roughly 45-degree zone below-forward that falling fair covers, and wait out the float (count it), then hit her as she falls [lib:The Melee Puff Bible]. Poke her feet from below (her float aerials do not cover directly beneath except dair).
- **If she drops with an aerial instead of floating:** whiff punish the landing; do not trade [lib:The Melee Puff Bible].
- **If she air dodges:** treat the landing as a fixed-lag punish [lib:The Melee Puff Bible].
- **From below the stage:** challenge the double jump with a spaced hit. If she uses up B, wait until the peak of the rise and hit her from the side or below as the parasol opens; if she reaches the ledge, cover her ledge options, which are poor [lib:The Melee Puff Bible][lib:20XX+XY].
- **At the ledge:** Peach has no invincible way back onto the stage [lib:20XX+XY]. Ice Climbers can wall the ledge with a desynced Blizzard + Ice Shot at a safe distance [lib:20XX+XY]. Going off stage with a meteor works because her vertical recovery is weak once the double jump is gone [lib:20XX+XY].
- A realistic recovering-Peach CPU should: float first when high, save the double jump, throw nair/bair at a close edgeguarder, and vary between landing on stage with a closed parasol and grabbing the ledge.

## Defense and out of shield

- **Nair out of shield:** jump squat 5 [wiki:Peach_(SSBM)] + nair frame 3 [fd] = hitbox on frame 8 after leaving shield. Hits both sides. Her best answer to pressure that leaves a gap.
- **Bair out of shield:** frame 6 aerial [fd], used when the opponent is behind her [wiki:Peach_(SSBM)/Back_aerial].
- **Shield grab:** grab active on frames 7-8 [wiki:Peach_(SSBM)/Grab]. (The frame data dump lists 6-7; see the generated table.)
- **Turnip out of shield:** an item can be thrown directly out of shield, or z-dropped out of a jump [wiki:Vegetable].
- **Up B out of shield:** hits from frame 6 [wiki:Peach_(SSBM)/Up_special]; very punishable on whiff.
- **Crouch cancel / ASDI down:** central to her defense at low percent; CC -> dsmash punishes most single weak hits. Opponents answer with grabs, strong hits, or moves that knock down despite CC (e.g. Ice Climbers' fair grounds a CCing Peach past about 20% with both climbers; their ftilt at about 90%+ [lib:20XX+XY]).
- **Combo escapes:** float out of hitstun to change her fall timing; nair (frame 3) to break weak strings; double jump. Float after tumble needs the tumble cleared first [lib:Untumbling into Float] (video, not watched).
- **Captain Falcon's dthrow -> knee** can be escaped with an air dodge; this is credited to Bladewise [wiki:Peach_(SSBM)] and shown in a library video [lib:How to Escape Dthrow Knee].
- **What beats her shield:** grabs (her roll and spot dodge are not special), and Jigglypuff's Pound. Peach is hard to shield-poke only while the shield is fresh.
- **Dsmash survival:** opponents caught in dsmash should not crouch; [SDI](../techniques/sdi.md) out and away is the documented defense [lib:Surviving Peach's Dsmash] (video, not watched).

## As the training dummy

- **Weight / fall speed:** weight 90 (below average), fall speed 1.5, fast-fall 2.0 (floaty) [wiki:Peach_(SSBM)]. She is hard to combo vertically for long and dies early off the top.
- **Chain grabs on her:** Ice Climbers' dthrow chain grab on Peach only works at 0-12% and only if she DIs away (dash jump-cancel grab); with no DI or DI in she jumps out [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]. Ice Climbers' dthrow hand-off on Peach: she is released on frame 33; the regrab window is frames 33-35 (DI in) or 33-36 (DI away) [same source]. Marth, Sheik and others get throw follow-ups rather than long chain grabs [unverified].
- **Strong DI choices for a realistic CPU:** survival DI on vertical finishers (she dies off the top first); DI away/out on throws from Ice Climbers except when it enables the dash regrab at 0-12%; against Jigglypuff's utilt/uair, DI out to avoid Rest ("no DI" is what gets Rested at low percent [lib:The Melee Puff Bible]).
- **Rest setups on Peach** (from the Jigglypuff side): utilt at 0% -> Rest; at 12% no DI -> full hop double jump Rest; low uair 12-50% no DI -> full hop Rest [lib:The Melee Puff Bible]. Jigglypuff's dair -> usmash is a true combo on Peach from 67% and dair -> fsmash from 108% [lib:The Melee Puff Bible].
- **Kill percents on Peach** (Jigglypuff usmash, centre stage, good DI): Yoshi's Story 104%, Pokemon Stadium 108%, Final Destination 111%, Battlefield 114%, Fountain of Dreams 115%, Dream Land 128% [lib:The Melee Puff Bible].
- **CPU behaviours worth scripting:** crouch cancel -> dsmash at low percent when hit by a weak move; nair out of shield after a shielded aerial; float at fair range and fair on approach; after a whiffed fair, pick between jab, dsmash, roll, spot dodge, or re-float (the options a top Peach is reported to use [lib:20XX+XY]).
- **Thresholds:** crouch cancel stops protecting her once a move knocks her down despite the reduction; move-specific percents were not found except the Ice Climbers values above.

## Matchup notes

### vs Jigglypuff

Regarded as Peach's worst matchup and the hardest counter among top-tier matchups [wiki:Peach_(SSBM)]. Jigglypuff out-drifts her, her bair wall beats Peach's approach, and Peach struggles to kill a character this floaty; uair is one of her few reliable kill moves (above about 110%) [wiki:Peach_(SSBM)/Up_aerial]. Turnip pulls matter mainly because of the stitch-face threat, which forces Jigglypuff to approach [wiki:Peach_(SSBM)/Down_special]. Jigglypuff punishes dash attack on shield or crouch with Rest and avoids the fair zone while Peach floats [lib:The Melee Puff Bible].

### vs Fox

Slight disadvantage in NTSC [wiki:Peach_(SSBM)]. Fox out-runs her, kills her off the top early, and can camp platforms. Peach's rewards are large: CC dsmash at low percent, the uthrow chain grab on flat stages, dsmash kills near the edge, and strong edgeguards (turnips and float aerials against Fire Fox / Illusion). Nair out of shield and CC answer sloppy pressure.

### vs Falco

The one top-tier matchup where SSBWiki does not list her as disadvantaged [wiki:Peach_(SSBM)]. Lasers stop float approaches, so Peach powershields or ducks them and punishes Falco's approaches with nair out of shield and CC dsmash [lib:Hollabarracuda Girl: A Peach Tutorial]. Falco's recovery is short, so any off-stage hit or turnip tends to kill.

### vs Marth

Slight disadvantage [wiki:Peach_(SSBM)]. Marth's sword out-ranges fair and his dash dance avoids it; his grab and tipper punish her float landings. Peach wins exchanges by CCing non-tipper hits at low percent and by edgeguarding his linear recovery with float bair/nair and turnips. A dedicated guide exists [lib:Guide to Peach vs Marth] (not reachable this session).

### vs Sheik

Slight disadvantage [wiki:Peach_(SSBM)]. Sheik's needles and tilts control her float; Sheik's throws lead to follow-ups and fair kills her off the side. Peach's CC dsmash punishes Sheik's tilts and dash attack at low percent, and she edgeguards Sheik's up B well. Guide: [lib:Guide to Peach vs Sheik] (not reachable this session).

### vs Captain Falcon

Falcon out-runs her and kills with knee, but he is combo food for uthrow/dash attack juggles and easy to edgeguard. Learn the air dodge escape from dthrow -> knee [wiki:Peach_(SSBM)]. Guide: [lib:Guide to Peach vs Falcon] (not reachable this session).

### vs Ice Climbers

Considered Peach's best top/high-tier matchup; she is called the hardest counter to the Ice Climbers [wiki:Wobbling]. FC fair is the whole matchup: it is safe on their shield, separates the climbers, and knocks Nana down at any percent; Nana does not tech, so she can be hit again and killed [lib:20XX+XY]. Turnips thrown between separated climbers slow Popo's return [lib:20XX+XY]. Peach must avoid being grabbed after a whiffed fair or a shielded dsmash.

## Drill seeds

### Float-cancel fair on shield into mixup

- **id:** `peach-fc-fair-shield-mixup`
- **Goal:** Space float-cancelled fair on a shield and pick the follow-up that beats the defender's response.
- **Player:** Peach
- **CPU:** [Marth](marth.md), [Sheik](sheik.md), [Fox](fox.md), [Ice Climbers](ice-climbers.md)
- **Setup:** Final Destination, centre. CPU standing, shielding, facing Peach at about fair range. Both at 0-40%.
- **CPU behaviour:** Holds shield until hit, then one of (random): shield grab on the first actionable frame; roll in/away; jump out of shield with an aerial; keep holding shield for 30+ frames; wavedash back.
- **Success:** Fair hits the shield while Peach is in float and she lands with the 4-frame landing; her next action beats the CPU option (grab vs hold shield, jab/dsmash vs grab attempt, dash attack vs roll, shield/nair vs jump aerial) without her being hit or grabbed.
- **Fail:** Peach is grabbed or hit within 40 frames of landing, or the fair lands with full landing lag (not float-cancelled).
- **Variations:** FC nair instead of fair at closer range; FC dair -> nair; CPU percent high enough that fair knocks down on hit; CPU sometimes drops shield early so the fair hits.
- **Data needed:** Fair hit frames 16-20, landing lag 25/12 vs 4 [fd][wiki:Float]; shieldstun for a 15% hit; CPU grab start-up; Peach jab frame 2, grab frames 7-8, dsmash frame 5.

### Crouch cancel into down smash

- **id:** `peach-cc-dsmash-punish`
- **Goal:** Hold down through a weak hit and down smash on the first possible frame.
- **Player:** Peach
- **CPU:** [Fox](fox.md), [Sheik](sheik.md), [Falco](falco.md), [Marth](marth.md)
- **Setup:** Final Destination, centre, Peach standing at 0%. CPU at 0-30%, one dash length away.
- **CPU behaviour:** Approaches with a randomised weak move: Fox/Falco SHFFL nair or dair (optionally followed by shine), Sheik ftilt or dash attack, Marth non-tipper fair or dtilt. On some repetitions the CPU grabs instead (CC loses to grab), so the player must not crouch blindly.
- **Success:** Peach is hit while crouching, does not get knocked down, and at least two dsmash hits connect within 30 frames of the CPU's hit.
- **Fail:** Peach is grabbed while crouching, is knocked down, or the dsmash whiffs/is shielded.
- **Variations:** Raise Peach's percent until CC fails (finds the threshold per move); CPU crouch cancels Peach's dsmash to show the multi-hit damage; CPU spaces the move so dsmash whiffs.
- **Data needed:** Dsmash hit frames 5-6/9-10/13-14/17-18/21-22, 39 total [wiki:Peach_(SSBM)/Down_smash]; knockback of each CPU move vs Peach weight 90 to compute knockdown thresholds; hitlag.

### Nair out of shield against space-animal pressure

- **id:** `peach-nair-oos`
- **Goal:** Punish gaps in shield pressure with jump -> nair.
- **Player:** Peach
- **CPU:** [Fox](fox.md), [Falco](falco.md)
- **Setup:** Peach shielding at centre stage. CPU starts a short hop toward her.
- **CPU behaviour:** Aerial (nair or dair) on shield, then random: shine -> jump away; shine -> grab; delayed second aerial; late aerial with no shine; stand and shield.
- **Success:** Peach's nair (hitbox on frame 8 after leaving shield: 5 jump squat + frame 3 [wiki:Peach_(SSBM)][fd]) hits the CPU before the CPU's next hitbox touches her.
- **Fail:** Peach is hit out of jump squat, shield is grabbed, or nair whiffs.
- **Variations:** Require the correct choice between nair OoS, shield grab and holding shield depending on the CPU option; add turnip-in-hand (throw OoS).
- **Data needed:** Shieldstun and landing lag of the CPU aerials, shine frame data (not in the dump), Peach jump squat 5, nair frame 3.

### Up throw chain grab on fastfallers

- **id:** `peach-uthrow-chaingrab`
- **Goal:** Regrab after up throw while reading DI; finish when the regrab stops working.
- **Player:** Peach
- **CPU:** [Fox](fox.md), [Falco](falco.md), [Captain Falcon](captain-falcon.md)
- **Setup:** Final Destination, centre. Peach starts with the CPU already grabbed. CPU at a chosen start percent.
- **CPU behaviour:** Random DI on each throw (none, slight/full behind, slight/full in front). Double jumps or shines (space animals) on the first actionable frame after hitstun.
- **Success:** N consecutive regrabs before the CPU acts, then a finisher (usmash, fair, or dsmash) connects.
- **Fail:** CPU escapes (acts before the regrab) or lands and shields/rolls.
- **Variations:** Sweep the start percent to map the working window (the sourced percent data is contradictory; see the technique entry); add platforms so the CPU can land and tech.
- **Data needed:** Uthrow release frame 25 of 49, throw knockback (angle 88, base 70, growth 56) [wiki:Peach_(SSBM)/Up_throw], victim weight/gravity/fall speed, hitstun formula, Peach grab frames 7-8 and jump squat 5.

### Dash attack tech chase and follow-up

- **id:** `peach-dash-attack-techchase`
- **Goal:** Cover a tech option with dash attack and convert the launch into at least one aerial.
- **Player:** Peach
- **CPU:** [Fox](fox.md), [Falco](falco.md), [Captain Falcon](captain-falcon.md), [Sheik](sheik.md)
- **Setup:** Flat stage. CPU is launched into a knockdown in front of Peach (e.g. after a dthrow or a fair knockdown) at 20-80%.
- **CPU behaviour:** Random: tech in place, tech roll left, tech roll right, missed tech (then getup attack, roll, or stand).
- **Success:** Dash attack hits (frames 6-20 active [fd]) and a follow-up aerial hits before the CPU can act.
- **Fail:** CPU acts or shields before being hit; Peach is hit by getup attack.
- **Variations:** Platform version with full-hop uair from below; require jab reset on missed tech at low percent.
- **Data needed:** Tech timings (in-place and roll durations and vulnerability), dash attack frames, Peach run speed 1.3 [wiki:Peach_(SSBM)], launch knockback of clean vs late hit.

### Safe turnip pull and turnip approach

- **id:** `peach-turnip-pull-safety`
- **Goal:** Judge when a 29-frame turnip pull is safe, then use the turnip to cover an approach.
- **Player:** Peach
- **CPU:** [Fox](fox.md), [Marth](marth.md), [Captain Falcon](captain-falcon.md), [Jigglypuff](jigglypuff.md)
- **Setup:** Peach near a ledge or centre; CPU at a randomised distance (inside or outside its burst range).
- **CPU behaviour:** Either waits/dash-dances at range or runs in with its fastest burst option on a randomised delay.
- **Success:** If the player pulls, the pull completes (frame 29) without Peach being hit; then the thrown turnip hits or is shielded and Peach lands an FC aerial or grab behind it. If the CPU is in range, the correct answer is not pulling (shield/CC instead).
- **Fail:** Peach is hit during the pull (turnip lost) or the CPU catches the turnip.
- **Variations:** Respawn "knitting" window: CPU is invincible-respawning with a countdown; player pulls and discards until a wink or better; score by turnip quality and position when invincibility ends.
- **Data needed:** Pull timing (turnip at frame 14, 29 total) [wiki:Peach_(SSBM)/Down_special], CPU burst ranges (dash speeds, attack reach), turnip odds table, item throw speeds.

### Float edgeguard off stage

- **id:** `peach-float-edgeguard`
- **Goal:** Leave the stage, hit a recovering opponent with a float aerial, and return.
- **Player:** Peach
- **CPU:** [Marth](marth.md), [Sheik](sheik.md), [Fox](fox.md), [Falco](falco.md), [Captain Falcon](captain-falcon.md)
- **Setup:** CPU launched off stage at 50-100% with its double jump (or without, as a variation). Peach on stage near the ledge.
- **CPU behaviour:** Recovers with a randomised route: high, at ledge height, low; mixes double jump timing and up B / side B.
- **Success:** CPU loses the stock, or is hit off stage and Peach returns to stage/ledge.
- **Fail:** CPU reaches the stage or ledge unhit, or Peach fails to return.
- **Variations:** Peach holds a turnip at the start; edgeguard from the ledge with DJC bair; dtilt meteor at the ledge.
- **Data needed:** CPU recovery move distances and frame data, Peach float duration 2.5 s [wiki:Float], air speed 1.1 [wiki:Peach_(SSBM)], bair frames 6-9 / nair frames 3-6 [fd], blast zone positions.

### Recovering against an edgeguarder

- **id:** `peach-recovery-mixup`
- **Goal:** Return to stage from far off stage using float, double jump, and parasol mixups.
- **Player:** Peach
- **CPU:** [Marth](marth.md), [Fox](fox.md), [Jigglypuff](jigglypuff.md), [Sheik](sheik.md)
- **Setup:** Peach launched off stage at a randomised height and distance, with float and double jump available (variation: one or both spent).
- **CPU behaviour:** Edgeguards realistically: waits below-front of a floating Peach and hits her when the float ends; challenges the double jump from below; hits the up B at its peak; grabs the ledge to deny it.
- **Success:** Peach is grounded on stage and actionable, or holding the ledge, without losing the stock.
- **Fail:** Stock lost, or Peach lands with the 30-frame open-parasol landing and is punished.
- **Variations:** Stage with walls for wall bomber; start with a turnip in hand.
- **Data needed:** Float duration, parasol landing lag 30/4 and ledge-grab rule (front only, from frame 34) [wiki:Peach_(SSBM)/Up_special], double jump height (unknown on the wiki), CPU edgeguard hitbox timings.

### Punishing a missed Rest

- **id:** `peach-rest-punish`
- **Goal:** Take the maximum punish on a sleeping Jigglypuff.
- **Player:** Peach
- **CPU:** [Jigglypuff](jigglypuff.md)
- **Setup:** Jigglypuff has just whiffed Rest next to Peach at a randomised stage position and percent.
- **CPU behaviour:** Asleep for the remainder of Rest's 249-frame animation [wiki:Jigglypuff_(SSBM)/Down_special], then acts.
- **Success:** Jigglypuff is KO'd, or takes at least a target damage amount, before she wakes.
- **Fail:** Jigglypuff wakes and escapes, or the punish does less than the target.
- **Variations:** Score different punishes (charged usmash arm sweetspot, pull turnips first then smash, fsmash weapon fishing); a library video covers Peach's options [lib:Punishing a Missed Rest] (not watched).
- **Data needed:** Rest total frames 249; usmash charge window (frames 10-11) and sweetspot hitbox [wiki:Peach_(SSBM)/Up_smash]; turnip pull 29 frames; Jigglypuff weight 60 [wiki:Jigglypuff_(SSBM)].

### Escaping down throw to knee

- **id:** `peach-dthrow-knee-escape`
- **Goal:** As Peach, avoid Captain Falcon's dthrow -> fair (knee) with DI and an air dodge.
- **Player:** Peach
- **CPU:** [Captain Falcon](captain-falcon.md)
- **Setup:** Falcon has Peach grabbed at 60-110% on a flat stage.
- **CPU behaviour:** Down throw, then jumps and knees toward Peach's position on reaction to DI.
- **Success:** Peach is not hit by the knee and lands or reaches a neutral position.
- **Fail:** Knee connects.
- **Variations:** Falcon mixes in uair or a delayed knee to punish the air dodge.
- **Data needed:** Falcon dthrow knockback and Peach's hitstun at each percent, air dodge intangibility frames, knee hit frames; the exact timing is explained in a library thread/video not read this session [lib:How to Escape Dthrow Knee].

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlPe.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/peach.json`](../framedata/peach.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 2-3 | 3 | 74/78 | 0 | 100 | 20 |  | 19 | 16 | 3 | -10 |  |
| Jab 2 | `jab2` | 3-4 | 2 | Sakurai | 30 | 100 | - |  | 20 | 17 | 2 | -11 | starts 1 frame late (included) |
| Dash attack | `dash_attack` | 6-8 | 12/9 | 80/Sakurai | 70/50 | 70 | - |  | 37 | 36 | 7 | -22 |  |
|  |  | 9-20 | 8/7 | 80/Sakurai | 20 | 70 | - |  |  |  | 5 | -21 |  |
| Up tilt | `utilt` | 9-13 | 12 | 80 | 48 | 72 | - |  | 39 | 37 | 7 | -20 | partly intangible 9-12 (1 bone) |
| Down tilt | `dtilt` | 12-13 | 12 | 270/80 | 60/15 | 100 | - |  | 27 | 26 | 7 | -6 |  |
| Forward smash | `fsmash` | - | - | - | - | - | - | - | 47 | - | - | - |  |
| Up smash | `usmash` | 13-22 | 15/19/8 | 90/75 | 40/30 | 100 | - |  | 44 | - | 10 | -21 | charge hold frame 10; partly intangible 13-22 (3 bones) |
| Down smash | `dsmash` | 5-6, 9-10, 13-14, 17-18, 21-22 | 14/12 | 140 | 40/35 | 80 | - |  | 39 | - | 8 | -26 | charge hold frame 3; partly intangible 3-24 (4 bones) |
| Forward smash (variant AttackS4) | `fsmash_298` | 15-18 | 13/17 | 45/Sakurai | 50/70 | 50 | - |  | 47 | 40 | 9 | -15 | charge hold frame 8 |
| Forward smash (variant AttackS4) | `fsmash_299` | 15-18 | 17/15 | 80/Sakurai | 50 | 60 | - |  | 47 | 40 | 9 | -15 | charge hold frame 8 |
| Forward smash (variant AttackS4) | `fsmash_300` | 15-18 | 12 | 29 | 75/65 | 35 | - |  | 47 | 40 | 7 | -17 | charge hold frame 8 |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 3-6 | 14 | Sakurai | 20 | 100 | - |  | 49 | 42 | 8 | 17 | 8 | <3, >35 | +0 |  |
|  |  | 7-23 | 10/9 | Sakurai | 0 | 100 | - |  |  |  | 6 |  |  |  | -2 |  |
| Forward air | `fair` | 16-20 | 15 | Sakurai | 60 | 70 | - |  | 54 | 51 | 8 | 25 | 12 | <16, >38 | -4 |  |
| Back air | `bair` | 6-9 | 14 | Sakurai | 0 | 100 | - |  | 44 | 38 | 8 | 15 | 7 | <6, >22 | +1 |  |
|  |  | 10-22 | 10 | Sakurai | 10 | 90 | - |  |  |  | 6 |  |  |  | -1 |  |
| Up air | `uair` | 7-11 | 14/12/11 | 80/Sakurai | 0 | 120 | - |  | 35 | 34 | 8 | 15 | 7 | <7, >21 | +1 |  |
| Down air | `dair` | 12-13, 18-19, 24-25, 30-31 | 3 | 90 | 16/12 | 50 | - |  | 39 | 36 | 3 | 15 | 7 | <12, >35 | -4 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 7-8 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 14 | 25 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 10 | 8 | 45 | 10 | 160 | - | - | 15 | 33 |  |
| Back throw | `bthrow` | 11 | 9 | 135 | 80 | 40 | - | - | 21 | 49 |  |
| Up throw | `uthrow` | 8 | 6 | 88 | 70 | 56 | - | - | 25 | 49 |  |
| Down throw | `dthrow` | 7 | 7 | 108 | 60 | 30 | - | - | 43 | 64 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Toad, ground | `special_n` | - | - | - | - | - | - | - | 29 | - | - | - | spawns article/projectile on 1 |
| Side B: Peach Bomber, ground, Start | `special_s_start` | - | - | - | - | - | - | - | 21 | - | - | - |  |
| Side B: Peach Bomber, ground, End | `special_s_end` | - | - | - | - | - | - | - | 32 | - | - | - |  |
| Side B: Peach Bomber, ground, Jump | `special_s_jump` | 1-9 | 0 | 0 | 0 | 0 | - | inert | 29 | - | - | - |  |
| Side B: Peach Bomber, air, Start | `special_air_s_start` | - | - | - | - | - | - | - | 31 | - | - | - |  |
| Side B: Peach Bomber, air, End | `special_air_s_end` | - | - | - | - | - | - | - | 27 | - | - | - |  |
| Side B: Peach Bomber, air, End | `special_air_s_end_307` | - | - | - | - | - | - | - | 27 | 20 | - | - |  |
| Up B: Peach Parasol, ground, Start | `special_hi_start` | 6-9 | 5 | 70 | 0 | 100 | 150 |  | 40 | - | 4 | - | intangible 3 |
|  |  | 10-11, 12-13, 14-15, 16-17, 18-19 | 1 | 74/78 | 0 | 100 | 120/90 |  |  |  | 2 | - |  |
|  |  | 20-21, 22-23, 24-25, 26-27, 28-29 | 1 | 72/78 | 0 | 100 | 60/90 |  |  |  | 2 | - |  |
| Up B: Peach Parasol, ground, End | `special_hi_end` | - | - | - | - | - | - | - | 8 | - | - | - |  |
| Up B: Peach Parasol, air, Start | `special_air_hi_start` | 6-9 | 5 | 70 | 0 | 100 | 150 |  | 40 | - | 4 | - | intangible 3 |
|  |  | 10-11, 12-13, 14-15, 16-17, 18-19 | 1 | 74/78 | 0 | 100 | 120/90 |  |  |  | 2 | - |  |
|  |  | 20-21, 22-23, 24-25, 26-27, 28-29 | 1 | 72/78 | 0 | 100 | 60/90 |  |  |  | 2 | - |  |
| Up B: Peach Parasol, air, End | `special_air_hi_end` | - | - | - | - | - | - | - | 8 | - | - | - |  |
| Down B: Vegetable (turnip pull), ground | `special_lw` | - | - | - | - | - | - | - | 64 | - | - | - |  |
| Down B: Vegetable (turnip pull), ground, Hit | `special_lw_hit` | - | - | - | - | - | - | - | 74 | - | - | - | intangible 10-13 |
| Down B: Vegetable (turnip pull), air | `special_air_lw` | - | - | - | - | - | - | - | 64 | - | - | - |  |
| Down B: Vegetable (turnip pull), air, Hit | `special_air_lw_hit` | - | - | - | - | - | - | - | 74 | - | - | - | intangible 10-13 |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-18 | - | 27 | 25 |  |
| Roll forward | `roll_forward` | intangible 4-19 | - | 31 | - |  |
| Roll backward | `roll_backward` | intangible 4-19 | - | 31 | - |  |
| Air dodge | `airdodge` | intangible 4-19 | - | 49 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-20 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-27 | 17-19, 25-27 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-19 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-20 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-26 | 17-18, 25-26 (6/8%) | 49 | - |  |
| Getup roll forward (face down) | `getup_roll_forward_facedown` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-19 | - | 35 | - |  |
| Tech in place | `tech_in_place` | intangible 2-20 | - | 26 | - | starts 1 frame late (included) |
| Tech roll forward | `tech_roll_forward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Tech roll backward | `tech_roll_backward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Wall tech | `wall_tech` | - | - | 26 | - | starts 1 frame late (included) |
| Wall tech jump | `wall_tech_jump` | - | - | 40 | - | starts 1 frame late (included) |
| Ceiling tech | `ceiling_tech` | - | - | 26 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-55 | - | 59 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 32 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-40 | 44-47 (10/8%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-6 | 10-14 (6%) | 54 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-64 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-39 | - | 50 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-20 | - | 20 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 28 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-10 | - | 10 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 28 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Up B | jump cancel | 7 | `special_hi_start` |
| Shield grab | direct | 7 | `grab` |
| Neutral air | jump | 8 | `nair` |
| Back air | jump | 11 | `bair` |
| Up air | jump | 12 | `uair` |
| Up smash | jump cancel | 14 | `usmash` |
| Down air | jump | 17 | `dair` |
| Forward air | jump | 21 | `fair` |
| Spot dodge | direct | intangible 2-18 of 27 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 17 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Peach indexed by [The Melee Library](https://www.meleelibrary.com/#peach) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [Are You a Peach Player?](https://www.youtube.com/watch?v=2zUiyEvVSGw) | SSBM Tutorials | They give an overview of Peach the character to give you an idea of whether you would like to play her. |
| [2020 Peach Melee Techs Guide](https://www.youtube.com/watch?v=qQg_2Vp8mEk&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=23&t=0s) | Third Chair | Video guide on performing useful Peach tech in 2020. |
| [Advanced Peach Tutorial](https://www.youtube.com/watch?v=zvNgmahChOM) | MacD | MacD introduces you to the essentials of Peach. |
| [Peach Neutral Game Tutorial (Basics)](https://www.youtube.com/watch?v=8C01hqm6bdQ) | SSBM Tutorials |  |
| [How to Practice Peach](https://www.youtube.com/watch?v=4z3zzQpT2tE) | SSBM Tutorials and ConnorDaKid | A beginner’s guide to practicing Peach. |
| [Newbie Peach Training Guide](http://smashboards.com/threads/newbie-peach-training-guide.41170/) | Fieari | A wonderful starting place for anyone learning Peach. |
| [Extensive Turnip Guide](http://smashboards.com/threads/quetzalcoatls-extensive-turnip-guide.79319/) | Quetzalcoatl |  |
| [Turnip Guide revision #1 - Turnip Damage and Knockback](http://smashboards.com/threads/quetzs-turnip-guide-revision-1-turnip-damage-and-knockback.400824/) | Quetzalcoatl | Quetzalcoatl adds some more info about how turnips work. |
| [Float FAQ](http://smashboards.com/threads/float-faq-critique-and-suggestions.32406/) | SuperDoodleMan | Lots of information about floating and how to use it. |
| [Guide to Peach vs Sheik](http://www.meleeitonme.com/armadas-guide-to-peach-vs-sheik/) | Armada |  |
| [Guide to Peach vs Marth](http://www.meleeitonme.com/armadas-guide-to-peach-vs-marth/) | Armada |  |
| [Guide to Peach vs Falcon](http://www.meleeitonme.com/peach-vs-falcon-guide/) | ConnorTheKid |  |
| [VaNz Stuff about Peach](http://smashboards.com/threads/vanz-stuff-about-peach-tactical-discussion.242179/) | VaNz | VaNz discusses Peach’s matchups, giving some dos and don’ts. It is an outdated source, but much of the information and tactics are still good. If not, they provide a good starting point to begin approaching the matchups. Search the thread too for additional information. |
| [Peach Hitboxes and Frame Data](http://smashboards.com/threads/peach-hitboxes-and-frame-data-thread-remastered.425917/) | Stratocaster, Standardtoaster, and SuperDoodleMan | Shows gifs of all of Peach’s moves displaying hitboxes and hurtboxes. Also lists frame data on each move including frame advantage on shield. |
| [Peach Data and Notes](http://smashboards.com/threads/peach-data-and-notes.309178/) | Veril | Data on various aspects of Peach. Turnip, throws, moves, chaingrabs. |
| [Rock, Paper, Scissors, Theory, Peach](http://smashboards.com/threads/rock-paper-scissors-theory-peach.395652/) | Sycorax | An analysis of Peach’s mixup game on shield. |
| [Bob-omb Minutiae](http://smashboards.com/threads/bob-omb-minutiae.388104/) | CAUP | Fun tricks when you pull a Bob-omb. |
| [Autocancel DJC Fair into Tomahawk](http://smashboards.com/threads/auto-cancel-djc-fair-into-tomahawk.401948/) | Quetzalcoatl | Neat movement trick. |
| [Invincible Head Bounce Ledgestall](http://www.reddit.com/r/SSBM/comments/347d7b/new_tech_peach_invincible_head_bounce_ledge_stall/) | Schmooblidon | Peach has an intangible ledgestall on battlefield. |
| [Why Peach Beats Ice Climbers](http://www.reddit.com/r/SSBM/comments/35x2f1/discussion_about_ice_climbers/cr8nsln) | _Panda |  |
| [Peach Stage Discussion](http://smashboards.com/threads/official-2015-peach-stage-discussion.393381/) | community |  |
| [Prince Pivots](https://www.youtube.com/watch?v=GjX8_hsuXtc) | SSBM Tutorials and The Prince | Peach can use her double jump land to act quickly out of a run. Minimally 7 frames. |
| [How To Practice Tech Skill with Peach](https://www.youtube.com/watch?v=yK9x5H1vaoI) | ConnorTheKid |  |
| [Peach’s Shitty Edge Options Optimized](https://www.reddit.com/r/SSBM/comments/3bpf3k/peachs_shitty_edge_options_optimized/) | RadioGiraffe |  |
| [Postmodern RNG Tactics: Panning & Knitting Theory](http://smashboards.com/threads/postmodern-rng-tactics-panning-knitting-theory.414626/) | Vestboy_Myst | How to squeeze the most out of the RNG aspects of Peach. |
| [Hollabarracuda Girl: A Peach Tutorial](https://www.youtube.com/watch?v=4COWe9ILFog) | DoH | DoH explains his tactic for fighting Falco: [powershield everything](https://youtu.be/FTIlCychHVw?t=533)! |
| [Armada’s 2015 Peach Edgeguards](https://www.youtube.com/watch?v=q86I4s7pkWg) | ARGO | Put on some music and study how Armada edgeguards multiple characters. |
| [Armada's 2016 Peach Edgeguards](https://www.youtube.com/watch?v=FmiN0f7wOQ8) | ARGO | Similar to Armada's 2015 Peach Edgeguards video. Put on some music and study up. |
| [Float Dair into +3 Nair](https://www.youtube.com/watch?v=_gBeJJHViXs) | Wisp | A strong option that Peach can use on shield. Especially useful against Ice Climbers. |
| [How to use Float Cancel Fair in the Neutral Game](https://www.youtube.com/watch?v=3l82bEGzdDk) | Wisp | Wisp explains how Peach's fair fits into her general gameplan. |
| [How to win 50/50s](https://www.youtube.com/watch?v=mLPMiX_q778) | Wisp | Wisp discusses Peach's 50/50s and how to win mixups. While being Peach-centric, the video is useful to any character since the topic at hand is universal. |
| [Subfloat](https://www.youtube.com/watch?v=oySLq4y-c8M) | Quetzalcoatl | Quetz recently discovered a new method of floating called “subfloat”. This video describes how to do it and why it can be useful to implement it in your game. |
| [Double Jump Land Frame Data](http://smashboards.com/threads/dj-land-onto-platform-stage-specifics.385827/) | DarkRijin |  |
| Ice Climbers Match Up Flowchart by Armada | Armada | Series of posts about how to beat ICs with Peach: [1](http://smashboards.com/threads/vanz-stuff-about-peach-tactical-discussion.242179/page-285#post-14725426), [2](http://smashboards.com/threads/vanz-stuff-about-peach-tactical-discussion.242179/page-331#post-15513660), [3](http://smashboards.com/threads/vanz-stuff-about-peach-tactical-discussion.242179/page-331#post-15514369) |
| [Some weird, marginally useful Peach tech](https://www.reddit.com/r/SSBM/comments/3eetvn/new_peach_tech_lustdash/) | lemonlust |  |
| [Turnip Damage and Trajectory Data](http://smashboards.com/threads/official-ask-anyone-frame-things-thread.313889/page-30#post-20925654) | Magus | The table shows, for each throw, the initial X and Y velocity vectors, the magnitude of those vectors added [speed (speed/0.6)], and launch angle. |
| [Untumbling into Float](https://www.youtube.com/watch?v=DVeDtdJ9TfE) | Quetzalcoatl | [A comment](http://smashboards.com/threads/untumbling-vid.409452/#post-20910043) correcting some information in this video. |
| [Royal Academy Finishing School: Frame Data Application Thread](http://smashboards.com/threads/royal-academy-finishing-school-peach-frame-data-application-thread.431376/) | Sycorax | Contains info on the chaingrab on fastfallers, escaping dthrow knee, when nair causes more knockback than fair, turnip interaction with Fox/Falco's up-b, Peach's shield pressure, reaction tech chasing off uthrow, how staleness affects the end of Peach's chaingrabs, escaping Marth's fthrow regrab, uair aerial interrupt combo, sweetspot up-b, dthrow and uthrow followups, dash attack, dash jump nair to end chaingrabs, air to ground turnip throw mechanics, Samus jab shield pressure, glide tossing, move staling, parasol fall rates, up-B out of shield, parasol flick combo, how to escape Fox's uthrow uair, and more. |
| [Peach Melee Chaingrab Guide](https://www.youtube.com/watch?v=Daf2KRmfoeQ&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=11&t=0s) | Third Chair |  |
| [Wall Bomber Jump](https://www.youtube.com/watch?v=VfNigYNB5Ps) | PewPewU |  |
| [New Ledge Tech for Peach](https://www.youtube.com/watch?v=YW9oOOhOmuo) | Leffen |  |
| [Double Jump Land and AC Fair to Navigate Stages](https://www.youtube.com/watch?v=8PbS0bfdCRI) | Quetzalcoatl | And some [additional info](http://smashboards.com/threads/discovery-float-canceling-can-be-transferred-to-a-non-float-aerial-iasafc-linked-fc.424491/). |
| [Linked Float Canceling](https://www.youtube.com/watch?v=jsfZiX88g98) | Quetzalcoatl |  |
| [Punishing a Missed Rest](https://www.youtube.com/watch?v=ZcFIGijHCVA) | Pilot |  |
| [A Creating Turnip Walls to Pull More Turnips Relatively Safely](https://gfycat.com/TanWeepyAdamsstaghornedbeetle) | Toshi Milardo |  |
| [Surviving Peach’s Dsmash](https://www.youtube.com/watch?v=dqHxiegypyU) | PewPewU |  |
| [Jab Reset Data](http://smashboards.com/threads/peach-tap-jab-reset-data.437705/) | Vestboy_Myst | Percent data on causing jab resets with jab, dair, and z-dropped turnips. |
| [Peach Bomber Shield Breaker](https://www.youtube.com/watch?v=_SN-8e8jjqg) | Quetzalcoatl | Peach bomber does a lot of shield damage. For comparison, Marth's shield breaker uncharged does 31.78 shield health damage. Peach smash bomber does 19.88. Max shield health is 60. So this should break shields when the opponent has about 1/3 of their shield left. Stitch face does about 21.5. Mr. Saturn does about 32. |
| [How to Escape Dthrow Knee](https://www.youtube.com/watch?v=I4ZqQCY6vT4&feature=youtu.be) | Bladewise | A video showing what Sycorax [explains in his thread](http://smashboards.com/threads/royal-academy-finishing-school-peach-frame-data-application-thread.431376/#post-20902575). |
| [Extended Turnip Throw](https://www.youtube.com/watch?v=nfcHOLHmRlY) | Quetzalcoatl | Throw turnips farther by throwing them backward. |
| [Reverse Tilt Bomber Combos](https://www.youtube.com/watch?v=8BBlLUFpkGs) | Quetzalcoatl | Wacky tilt bomber combos. |
| [Peach Bomber Oddity](https://www.reddit.com/r/smashbros/comments/29od01/peach_bomber_oddity/) | DJLO | Peach's bomber has strange properties that allow it to clang with moves in the air. |
| [Armada's Peach Combos](http://smashboards.com/threads/armadas-peach-combos.428069/) | Sycorax | A directory of Armada Peach combos on fastfallers. |
| [Float No Impact Land](https://www.youtube.com/watch?v=uWO2tlMSbRg) | Quetzalcoatl | Similar to double jump no impact land. |
| [Closed Parasol V Cancel](https://www.youtube.com/watch?v=DZ8si2Jjne8) | Quetzalcoatl |  |
| [Buffered Float](https://www.youtube.com/watch?v=7Jiu1PE2xZI) | Quetzalcoatl | Press and hold X/Y early to float instantly after leaving platform. |
| [Armada's Shield Pressure at TBH6](https://smashboards.com/threads/armadas-shield-pressure-at-tbh6.442873/) | Sycorax | A thread exploring how Armada's shield pressure could be optimized. |
| [Wobble Disruption Using Frozen Turnip Glitch](https://smashboards.com/threads/wobble-disruption-using-frozen-turnip-glitch.443634/#post-21557872) | CAUP | A niche trick to prevent wobbling. |
| [Frozen Turnip Glitch Finally Solved!](https://www.reddit.com/r/SSBM/comments/3v20an/frozen_turnip_glitch_finally_solved_with_bonus/) | Evsen | This explains the mechanics behind the frozen turnip glitch. |
| [Wallbombing Guide](https://www.youtube.com/watch?v=beK7myWnvSU) | Quetzalcoatl | How to use Peach's side-b against a wall to help recover. |
| [Armada's 5 Tips for Peach Players](https://www.youtube.com/watch?v=mKLGhUAO-V8) | Armada | Armada advises Peach players to use wavedashing, not be lazy with movement, use shield more/better, mix up and guess better, and be willing to go off-stage for edgeguarding. |
| [Invincible Peach Ledge Options](https://twitter.com/RococoSSBM/status/878078984805920768) | RococoSSBM | This thread demonstrates two ways Peach is able to get a hitbox out while intangible from grabbing the ledge. The first is by using Up-b to the ledge for ECB manipulation, then dropping an air dodging on stage, and landing as the ECB updates. This yields at least 5 frames of grounded actionable ledge intangibility (enough for a dsmash). The second is glide tossing a turnip on to the stage. |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Peach (SSBM): https://www.ssbwiki.com/Peach_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Peach_(SSBM)/Down_smash , /Forward_aerial , /Neutral_aerial , /Back_aerial , /Up_aerial , /Down_aerial , /Dash_attack , /Up_throw , /Down_throw , /Forward_throw , /Back_throw , /Grab , /Up_tilt , /Down_tilt , /Forward_tilt , /Up_smash , /Forward_smash , /Neutral_special , /Side_special , /Up_special , /Down_special
- SSBWiki, Float (includes float cancel): https://www.ssbwiki.com/Float
- SSBWiki, Vegetable: https://www.ssbwiki.com/Vegetable
- SSBWiki, Peach Bomber: https://www.ssbwiki.com/Peach_Bomber
- SSBWiki, Peach Parasol: https://www.ssbwiki.com/Peach_Parasol
- SSBWiki, Double jump cancel: https://www.ssbwiki.com/Double_jump_cancel
- SSBWiki, Wobbling (Peach as Ice Climbers counter): https://www.ssbwiki.com/Wobbling
- SSBWiki, List of SSBM tier lists (NTSC) and Template:MeleeTiers: https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Melee Library card "20XX+XY" (Ice Climbers compendium; Peach matchup section with quotes from Armada, Tomber, Wobbles, Fly Amanita, Leffen, PracticalTAS and others): https://docs.google.com/document/d/1DPqPLDHfBWMluMMfd8KpDVN8s37866CTb4xQVW-_KLk/
- Melee Library card "The Melee Puff Bible" (Puff vs Peach section): https://docs.google.com/document/d/1VN4LFZCqnq_0t-X9FkcTXD5GD4XjIW1vg7oT4jpVMhY/
- Nicki / Nopia, "Ice Climbers Information and Data Sheet" (chain grab and hand-off data on Peach; linked from SSBWiki's Ice Climbers grab page): https://docs.google.com/document/d/1e2WfuNH1I86On59O53FubxYzA-zYMZKZVIrCPNVEqhk/
- Melee Library "Peach" section: card titles and descriptions only for the Smashboards threads, Reddit posts, meleeitonme.com guides and YouTube videos (Smashboards returned 403, the Wayback Machine returned 429, Reddit returned a block page).
- Frame data dump: `Peach.json`
