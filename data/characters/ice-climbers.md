---
schema: melee-character/v1
id: ice-climbers
name: Ice Climbers
aliases: [ICs, Icies, Popo and Nana, Popo, Nana, Sopo]
tier: "B+ (8th of 26), 2021 tier list (13th, PG Stats; voters were told to assume wobbling is legal)"
archetype: [grappler, punish-heavy, chaingrab, technical, mixup, projectile]
related: []
summary: The Ice Climbers win by keeping both climbers together behind a wall of desynced hammers, Ice Shots and Blizzards until one grab lands, then using the second climber to turn that grab into a stock (wobble, hand-off chain grab, or pummel combo into a charged smash).
key_tech: [nana-sync-and-delay, wobbling, in-grab-combo, charged-smash-finisher, down-throw-hand-off, down-throw-chain-grab, dash-dance-blizzard-desync, roll-spotdodge-desync, reverse-ftilt-jab-desync, shieldstun-desync, belay-out-of-shield-desync, platform-drop-desync, nana-rescue-teleport, belay-and-squall-recovery]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlPp.dat
framedata: ../framedata/ice-climbers.json
code: src/melee/ft/kinds/ftPopo
specials:
  neutral_b: "Ice Shot"
  side_b: "Squall Hammer"
  up_b: "Belay"
  down_b: "Blizzard"
attributes:
  weight: 88
  gravity: 0.1
  fall_speed: 1.6
  fast_fall_speed: 2
  jump_squat: 3
  jumps: 2
  walk_speed: 0.95
  dash_speed: 1.4
  run_speed: 1.4
  traction: 0.035
  air_speed: 0.7
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [4, 16, 2]
  jab2: [5, 19, 4]
  dash_attack: [11, 38, 9]
  ftilt_high: [6, 28, 8]
  ftilt_mid_high: [6, 28, 8]
  ftilt: [6, 28, 8]
  ftilt_mid_low: [6, 28, 8]
  ftilt_low: [6, 28, 8]
  utilt: [8, 42, 7]
  dtilt: [8, 29, 5]
  fsmash: [13, 47, 14]
  usmash: [14, 44, 11]
  dsmash: [6, 36, 12]
  nair: [6, 46, 8]
  fair: [19, 55, 11]
  bair: [8, 36, 12]
  uair: [6, 30, 9]
  dair: [3, 64, 9]
  grab: [7, 31, 0]
  dash_grab: [7, 41, 0]
  pummel: [13, 26, 3]
  fthrow: [24, 50, 5]
  bthrow: [null, 40, 7]
  uthrow: [25, 60, 5]
  dthrow: [null, 50, 6]
  special_n: [15, 60, 9]
  special_air_n: [15, 60, 9]
  special_s1: [12, 90, 4]
  special_s2: [10, 70, 4]
  special_air_s1: [12, 90, 4]
  special_air_s2: [10, 70, 4]
  special_hi_start: [null, 17, 0]
  special_hi_throw: [null, 43, 0]
  special_hi_throw2: [null, 60, 0]
  special_hi_start_304: [null, 17, 0]
  special_hi_throw_305: [null, 43, 0]
  special_air_hi_start: [null, 17, 0]
  special_air_hi_throw: [null, 43, 0]
  special_air_hi_throw2: [null, 60, 0]
  special_air_hi_start_309: [null, 17, 0]
  special_air_hi_throw_310: [null, 43, 0]
  special_lw: [null, 80, 0]
  special_air_lw: [null, 80, 0]
oos:  # option: frame the hitbox is out
  dair: 6
  grab: 7
  nair: 9
  uair: 9
  bair: 11
  usmash: 15
  fair: 22
resources: 40
# generated: end
---

# Ice Climbers

<!-- GENERATED:attributes -->
## Attributes

Read from `PlPp.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 88 |
| Gravity | 0.1 |
| Terminal fall speed | 1.6 |
| Fast-fall speed | 2 |
| Jump squat (frames before airborne) | 3 |
| Full hop / short hop initial Y speed | 2.6 / 1.4 |
| Air jump Y multiplier | 1 |
| Jumps | 2 |
| Walk max speed | 0.95 |
| Dash initial speed / run max speed | 1.4 / 1.4 |
| Ground friction (traction) | 0.035 |
| Air max horizontal speed | 0.7 |
| Air acceleration (base + stick) | 0.02 + 0.027 |
| Air friction | 0.02 |
| Normal landing lag | 4 |
| Shield size | 10.75 |
<!-- /GENERATED:attributes -->

## Overview

The Ice Climbers are two characters on one controller. The player controls the leader (Popo in the default costume); the partner (Nana) is a CPU that copies the player's inputs a few frames late when she is close and "synced", and otherwise runs back toward Popo on her own [wiki:Desynching]. Nana has her own damage percent and can be killed separately; with Nana gone the lone leader ("Sopo") loses most of the character's damage, grab punishes and recovery [wiki:Ice_Climbers_(SSBM)][wiki:Sopo].

They are a ground character: low traction (second lowest) gives a long [wavedash](../techniques/wavedash.md), their hammers are disjointed, and down smash, forward tilt, jab and grab come out quickly [wiki:Ice_Climbers_(SSBM)]. Their air game is poor (second-lowest air speed, floaty, laggy aerials) [wiki:Ice_Climbers_(SSBM)]. Neutral is about holding ground with hitboxes and projectiles from two bodies ("desyncs": making the two climbers do different things) and landing a grab. A grab with both climbers present is the strongest grab punish in the game: the infinite "wobble" where legal, or hand-off regrabs and pummel combos into a charged smash where it is banned [wiki:Ice_Climbers_(SSBM)/Grab].

They lose by being separated: moves such as [Fox](fox.md)'s shine and [Peach](peach.md)'s forward air knock the two apart, Nana cannot defend herself well, and Sopo is weak [wiki:Ice_Climbers_(SSBM)]. They die off the top (weight 88, fall speed 1.6) and off stage when the recovery strands Nana. They are among the most technically demanding characters [wiki:Ice_Climbers_(SSBM)].

## Strengths and weaknesses

- **Strengths:**
  - Grab punish: wobbling is an inescapable infinite on every character except other Ice Climbers [wiki:Wobbling]; without it, hand-offs, the down throw chain grab and in-grab combos (24-32% before the throw) into a charged smash still convert most grabs into heavy damage or a stock [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].
  - Two bodies: attacks hit twice (the partner's hit does 1% less from staleness [wiki:Ice_Climbers_(SSBM)]), and one climber can cover the other's lag.
  - Desyncs give simultaneous projectile + attack + movement, mostly used defensively to cover approach options [lib:20XX+XY].
  - Long wavedash, quick disjointed ground normals: dsmash hits on frames 6-11, ftilt on frames 6-9, jab on frame 4, grab on frames 7-8 [fd][wiki:Ice_Climbers_(SSBM)/Grab].
  - Ice Shot (neutral B) and Blizzard (down B) control the ground; Blizzard out-ranges most melee attacks [wiki:Ice_Climbers_(SSBM)][wiki:Blizzard].
  - Nana disrupts grabs and chain grabs on Popo by hitting the grabber [wiki:Ice_Climbers_(SSBM)].
  - Attackers who hit one climber's shield/body before the other suffer extra hitlag, which can make normally safe moves punishable [lib:20XX+XY].
- **Weaknesses:**
  - Nana: delayed inputs, cannot dash dance, does not tech, has poor DI at low CPU level, and dies easily once separated [lib:20XX+XY][lib:In Depth Analysis of Nana's CPU Behavior].
  - Sopo: no wobble, far fewer chain grabs, half the damage, and essentially only side B to recover [wiki:Ice_Climbers_(SSBM)][wiki:Sopo].
  - Poor aerial game and no good answer to opponents above them or camping platforms [wiki:Ice_Climbers_(SSBM)].
  - Second-worst traction: shield pushback is large and mistimed air dodges are punished [wiki:Ice_Climbers_(SSBM)].
  - Below-average grab range (7th worst) [wiki:Ice_Climbers_(SSBM)/Grab].
  - Laggy on shield: ftilt/dtilt about -16, dsmash -22, usmash -23, fsmash -25 when synced (worst case) [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].
  - Weak edgeguarding; recovery endangers Nana [wiki:Ice_Climbers_(SSBM)].
  - Wobbling has been banned at most events since 2019-2020 [wiki:Ice_Climbers_(SSBM)][wiki:Ice_Climbers_(SSBM)/Grab].

## Character tech

### Nana sync and input delay

- **id:** `nana-sync-and-delay`
- **What:** The rules that govern Nana. When she is near Popo and free to act she is "synced" and repeats the player's inputs 6 frames later; when separated she is AI-controlled, heads for Popo, and ignores inputs until she is back in range [wiki:Desynching][lib:20XX+XY]. Almost every Ice Climbers technique exploits the delay or a state in which one climber cannot accept an input that the other can.
- **Inputs:** None; this is the baseline behaviour.
- **Timing:** 6-frame delay on most inputs [wiki:Desynching]. Nana's CPU level rises with Popo's percent: level 0 at 0-19%, +1 per 20%, level 9 at 180%+. Observed consequences: she uses Blizzard on her own from Popo 60%, aerials from 80%, and grabs shielding opponents from 120%; higher levels DI (survival DI, perpendicular to the launch) more often and react faster [lib:In Depth Analysis of Nana's CPU Behavior]. On her own she never uses side B or up B and never chooses Ice Shot [lib:In Depth Analysis of Nana's CPU Behavior]. Nana does not tech [lib:20XX+XY]. If Nana grabs someone herself the game picks her throw: toward the ledge if she is near one, otherwise random [wiki:Ice_Climbers_(SSBM)/Grab].
- **Used for:** Predicting what Nana will do in every other technique; knowing when she is controllable.
- **Common errors:** Inputting commands while Nana is still running back (she ignores them); moving Popo away so Nana is left behind; assuming Nana will tech or DI.
- **Drill idea:** Display Nana's state (synced / returning / acting on her own) and Popo's percent band; player must re-sync within N frames after a scripted separation.

### Wobbling

- **id:** `wobbling`
- **What:** An infinite out of Popo's grab: Popo pummels while Nana hits the grabbed opponent with a tilt in an alternating rhythm. The victim stays in grab hitstun and cannot break out no matter how much they mash [wiki:Wobbling]. Works on every character except Ice Climbers [wiki:Wobbling].
- **Inputs:** Popo grabs (Nana must be next to him and free). Press A (or Z) for Popo's pummel; in the middle of the pummel animation tilt the control stick gently forward (ftilt) or down (dtilt) and press A again so that only Nana acts; keep pressing A in an even rhythm with the stick held at tilt. Finish by pressing the C-stick down right as a Nana tilt connects (Popo down smashes) [wiki:Wobbling][lib:20XX+XY].
- **Timing:** The alternating hits fall at exactly 200 beats per minute [wiki:Wobbling]. Popo's pummel hitbox is on frame 13 of a 25-frame animation [wiki:Ice_Climbers_(SSBM)/Pummel]. Tilting the stick too fast gives a throw (Popo) or a smash (Nana) [wiki:Wobbling]. Ftilt comes out 2 frames faster than dtilt and has more timing leniency; dtilt keeps Nana from walking off an edge [lib:20XX+XY]. Mash-out before the first tilt: with frame-perfect mashing an immediate pummel -> wobble is escapable until about 61%; realistic estimates are about 25% for the best mashers with warning and about 15% for most players [lib:20XX+XY]. Variants: Nana uses Blizzard ("Blizzobble"), staled fsmash/dsmash, or bair/nair/utilt combinations [wiki:Wobbling].
- **Used for:** A guaranteed stock from any synced grab where legal. Wobbling past the percent needed to kill (commonly 300%) is treated as stalling everywhere [wiki:Wobbling]. Most tournaments since 2019-2020 ban it; a common replacement rule allows 3 pummels and 3 Nana attacks per grab [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].
- **Common errors:** Smash-speed stick movement (throw or smash, opponent released); starting with a slow move when Nana is still in whiffed-grab lag (opponent mashes out); Nana out of range behind the opponent after a dash grab.
- **Drill idea:** CPU grabbed at a chosen percent and mashing at a configurable rate; count consecutive alternating pummel/tilt hits and report rhythm error per beat; fail on release.

### In-grab combo

- **id:** `in-grab-combo`
- **What:** The legal-everywhere version of the wobble: three Popo pummels interleaved with three Nana attacks, then a throw. The Nana attack is chosen for damage and position.
- **Inputs:** P = Popo pummel. Standing grab: P -> Nana ftilt -> P -> Nana Blizzard -> P -> Nana ftilt (24% before the throw). After regrabbing a Nana fthrow (hand-off): P -> Blizzard -> P -> ftilt -> P -> Blizzard (28%). At a ledge: P -> Blizzard -> P -> dtilt -> P -> dtilt (21%). Pummel + Blizzard three times ("Blizzobble") does 31% [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].
- **Timing:** Blizzard does the most damage but starts slowly and is hard to link into another Blizzard; ftilt is fast but walks Nana forward a little (she can walk off an edge); dtilt is slower and weaker but keeps her in place. After a standing grab Nana is in whiffed-grab lag, so start with ftilt, not Blizzard, or the opponent can mash out [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]. If Nana ended up behind the opponent (typical after a dash jump-cancel grab) use a "Tomber start": Nana ftilt, utilt (6 of 7 hits), or turn-around ftilt, buffered during the pummel [same source].
- **Used for:** Guaranteed damage from every synced grab before the throw follow-up.
- **Common errors:** Blizzard first from a standing grab; Nana's ftilt whiffing because she is behind the opponent; exceeding the pummel limit in a wobble-banned ruleset.
- **Drill idea:** Grab starts at random Nana positions (in front, on top, behind); player must pick the right starter and complete 3 pummels + 3 Nana hits; score total damage.

### Charged smash finisher

- **id:** `charged-smash-finisher`
- **What:** Ending a grab by having Nana charge a smash during Popo's last pummel and throw, releasing it as the opponent leaves Popo's hands.
- **Inputs:** After Popo's third pummel: start charging Nana's smash, then Popo down throws; release the smash as the throw releases. Versus fastfallers use Nana fsmash; versus everyone else who is not very light use Nana usmash. To send the opponent behind Popo instead: up throw -> Nana fsmash [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].
- **Timing:** Skipping Nana's third attack to charge kills earlier than three attacks plus an uncharged smash; the benefit grows with the opponent's weight because down throw takes longer on heavier characters (e.g. Samus dies almost 20% earlier with the charged usmash) [same source]. Up throw releases on frame 31 [wiki:Ice_Climbers_(SSBM)/Up_throw]; the input window for Nana's fsmash after up throw is usually frames 1-14 when she swings backward or Popo faces right, but as tight as frames 1-2 for a forward swing with Popo facing left against Marth or Captain Falcon [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]. Not useful against Jigglypuff, Pichu or Mr. Game & Watch [same source].
- **Used for:** Converting grabs into kills at high percent without wobbling.
- **Common errors:** Releasing the smash early (whiffs when the opponent DIs away); charging with the wrong climber.
- **Drill idea:** CPU grabbed at kill-range percent with random DI; success if the charged smash connects on the release frame and kills.

### Down throw hand-off

- **id:** `down-throw-hand-off`
- **What:** One climber down throws and the other grabs the opponent as they are released, before they can act. Repeated hand-offs form a chain grab that works on characters the solo chain grab does not. Near a ledge Nana's own throw is predictable (she throws toward the ledge [wiki:Ice_Climbers_(SSBM)/Grab]), which is what makes ledge hand-off loops reliable.
- **Inputs:** Popo grabs -> down throw; during the throw press Z (with the stick neutral, or walking Nana slightly forward) so Nana's grab is active on the release frames; then Nana throws and Popo regrabs, and so on.
- **Timing:** Down throw speed depends on the victim's weight. Release frame and regrab window (frames on which the second climber's grab must be active; opponent at about 50%; DI in / DI away), from [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]: Jigglypuff 22, 22-24 / 22-24. Fox 27, 27-30 / 27-29. Falco 29, 29-31 / 29-30. Pikachu 29, 29-33 / 29-32. Marth 32, 32-33 / 32-34. Ice Climbers 32, 32-34 / 32-34. Peach 33, 33-35 / 33-36. Sheik 33, 33-37 / 33-36. Luigi 36, 36-37 / 36-37. Captain Falcon 38, 38-40 / 38-41. Yoshi 39, 39-43 / 39-43. Samus 40, 40-41 / 40-42. Ganondorf 40, 40-42 / 40-43. Donkey Kong 42, 42-45 / 42-45. Bowser 43, 43-48 / 43-49. Windows are often 1 frame smaller at higher percent and larger at 0% [same source]. Grab is active on frames 7-8 [wiki:Ice_Climbers_(SSBM)/Grab].
- **Used for:** Chain grabbing characters who can jump out of the solo down throw chain grab (Marth, Peach, Fox, Falco...), carrying to the ledge, setting up the in-grab combo again.
- **Common errors:** Nana in front of Popo against Marth or Luigi (regrab on DI in becomes impossible); grabbing a frame late (opponent jumps or shines out); Nana walking off the edge.
- **Drill idea:** Per-character hand-off timing trainer: CPU with random DI in/away; report the frame Nana's grab became active against the valid window.

### Down throw chain grab (works with one climber)

- **id:** `down-throw-chain-grab`
- **What:** Popo's down throw drops the opponent right in front of him with low knockback; he regrabs before they can act. It needs no Nana, so it is Sopo's main punish and also a way to walk an opponent to Nana for a wobble or hand-off [wiki:Ice_Climbers_(SSBM)/Grab].
- **Inputs:** Grab -> down throw -> react to [DI](../techniques/di.md): standing regrab, walk or dash [jump-cancel](../techniques/jump-cancel.md) grab, turn-around or walk-turn grab on DI in, dash / dash JC / wavedash grab on DI away.
- **Timing:** Percent ranges over which a regrab exists for all DI, from the tables in [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)] (start of first band to end of last band; the regrab method changes inside the range and the last few percent allow a jump out): Sheik 0-142%, Pikachu 0-83%, Yoshi 0-81%, Ganondorf 0-114%, Donkey Kong 0-126%, Young Link 0-137%, Link 0-133%, Mr. Game & Watch 0-89%, Roy 0-149%, Pichu 0-104%, Ness 0-70%, Bowser 0-121%. Only if the victim DIs away (no DI or DI in lets them jump out): Marth 0-60%, Peach 0-12%, Mario/Dr. Mario 0-15%, Mewtwo 0-16%. Fox, Falco and Captain Falcon can be regrabbed over very wide ranges but reacting to their DI is not considered humanly consistent; the author reports reacting against Falco past 30% (dash forward, pivot grab on DI in) and calls Falcon arguably reactable from about 50% [same source].
- **Used for:** Damage with or without Nana; Sheik and Ganondorf are the classic victims [wiki:Ice_Climbers_(SSBM)/Grab].
- **Common errors:** Guessing DI instead of reacting; missing the jump cancel on a dash grab (40-frame dash grab instead of 30-frame standing grab [wiki:Ice_Climbers_(SSBM)/Grab]).
- **Drill idea:** Sheik CPU with random DI each throw from 0%; count regrabs until the range ends.

### Dash-dance Blizzard desync

- **id:** `dash-dance-blizzard-desync`
- **What:** A fast desync that makes Nana use Blizzard while Popo stays free. It exists because Nana cannot pivot during a dash dance and Popo cannot crouch during an initial dash [lib:20XX+XY].
- **Inputs:** Dash forward, back, forward again quickly, then press down B. Popo does nothing; Nana Blizzards [lib:20XX+XY].
- **Timing:** Speed depends on how fast the [dash dance](../techniques/dash-dance.md) is. It can be abandoned at any point before the down B by shielding, jumping or wavedashing, which re-syncs the pair [lib:20XX+XY]. Blizzard hits from frame 16 to 66 (9 hits of 2%) over a 79-frame animation [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)][fd].
- **Used for:** Getting a Blizzard wall out in neutral with Popo free to grab, smash or shoot an Ice Shot behind it.
- **Common errors:** Too slow (both Blizzard, in opposite directions); Popo crouching.
- **Drill idea:** Success if Nana is in Blizzard and Popo is actionable within N frames of the first dash; then Popo must land a grab on a CPU hit by the Blizzard.

### Roll / spot dodge / whiffed grab desync

- **id:** `roll-spotdodge-desync`
- **What:** During a roll, spot dodge or whiffed grab, holding the input for a move makes only Nana perform it afterwards [lib:20XX+XY].
- **Inputs:** Roll (or spot dodge, or grab) -> hold down + B (or another move) through the end of the animation. Nana Blizzards; Popo is free.
- **Timing:** Spot dodge is intangible on frames 2-18 of 27, roll on frames 4-19 of 31 [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]. Spot dodge -> Blizzard is a little faster than roll -> Blizzard but keeps them in place; whiffed grab is slower with no invulnerability but less obvious [lib:20XX+XY].
- **Used for:** The standard defensive desync: roll back -> Nana Blizzard relieves shield pressure and is hard to punish, including against Jigglypuff's bair [lib:20XX+XY].
- **Common errors:** Releasing the input too early (no desync); rolling into the opponent.
- **Drill idea:** CPU pressures shield; player rolls away and must have a Nana Blizzard active within N frames of the roll ending.

### Reverse ftilt / jab desync

- **id:** `reverse-ftilt-jab-desync`
- **What:** Out of a wavedash, a quick backward tilt input makes Popo ftilt while Nana only jabs; Nana's jab ends first, leaving her free while Popo is still in ftilt [lib:20XX+XY].
- **Inputs:** Wavedash -> hold the direction opposite to facing -> press A quickly. Then input Nana's next move (commonly Blizzard).
- **Timing:** Jab is interruptible from frame 16 and ftilt from frame 28 [fd], so Nana is free about 12 frames before Popo (derived from those two values).
- **Used for:** A quick Nana Blizzard after a wavedash; covering Popo's ftilt lag.
- **Common errors:** Input too slow (both ftilt).
- **Drill idea:** Detect Popo in ftilt and Nana in jab on the same frame after a wavedash, then Nana Blizzard within N frames.

### Shieldstun desync

- **id:** `shieldstun-desync`
- **What:** When an attack hits both shields on the same frame, both climbers leave shieldstun together; an input made in the last 6 frames of shieldstun is ignored by Popo but read by Nana (6 frames late, after her stun ends) [lib:20XX+XY].
- **Inputs:** Shield a strong hit -> during the final 6 frames of shieldstun input jump (then Blizzard or Ice Shot) -> Nana jumps and acts while Popo keeps shielding and can act out of shield whenever he wants.
- **Timing:** The 6-frame window moves with the attack's damage (hitlag and shieldstun both scale with damage), so it must be learned per move [lib:20XX+XY]. Recommended targets: Captain Falcon's knee and Ganondorf's fair on shield; a Blizzard can even fit between two Marth fairs with strict timing [lib:20XX+XY].
- **Used for:** Reversing pressure from high-damage, safe-on-shield aerials that they cannot punish [out of shield](../techniques/out-of-shield.md) otherwise. Described as strictly better than the belay out-of-shield desync but harder [lib:20XX+XY].
- **Common errors:** Inputting after shieldstun ends (both jump); the attack hitting the two shields on different frames.
- **Drill idea:** CPU Falcon knees the shield on a fixed timing; success if only Nana jumps and her Blizzard hits before the next knee.

### Belay out-of-shield desync

- **id:** `belay-out-of-shield-desync`
- **What:** Up B out of shield: Nana cannot join a synced up B while in shield, so Popo does a solo up B on the ground and Nana jumps, free to act in the air [lib:20XX+XY].
- **Inputs:** While both shield: up B quickly -> Nana jumps -> down B for an aerial Blizzard.
- **Timing:** Described as the fastest way to get a desynced Blizzard out of shield; Popo is stuck in the laggy solo-belay animation and usually cannot follow up [lib:20XX+XY].
- **Used for:** A defensive out-of-shield option when cornered.
- **Common errors:** Using it when the opponent can reach Popo behind Nana.
- **Drill idea:** CPU hits shield then waits at close range; success if Nana's Blizzard hits before the CPU's next attack and Popo is not hit.

### Platform drop desync

- **id:** `platform-drop-desync`
- **What:** Drop through a platform, immediately jump and waveland back onto it: Nana drops down while only Popo wavelands [lib:20XX+XY].
- **Inputs:** Platform drop -> jump at once -> air dodge onto the platform. Follow with e.g. Popo fair from the platform edge and Nana fsmash or Blizzard below [lib:20XX+XY].
- **Timing:** Not sourced.
- **Used for:** Splitting vertical coverage when under or on a platform.
- **Common errors:** Slow jump (both drop).
- **Drill idea:** Success when Popo is standing on the platform and Nana on the ground below within N frames.

### Nana rescue teleport

- **id:** `nana-rescue-teleport`
- **What:** If Nana is close enough and in a state where she could join a synced side B or up B (standing, walking, running, or airborne and not in tumble or mid-move), Popo using that move makes her appear at Popo's position [lib:20XX+XY].
- **Inputs:** Side B (fast, on-stage rescue from an incoming attack) or up B (longer range, gives Nana intangibility/invincibility, slow, leaves them apart) [lib:20XX+XY].
- **Timing:** During Belay Nana is intangible on frames 5-16 and invincible on frames 17-59 [wiki:Ice_Climbers_(SSBM)/Up_special]. Up B is mainly for a Nana who is too far to recover with her double jump but not in tumble [lib:20XX+XY].
- **Used for:** Saving Nana; general advice is to save her while she is still on stage by hitting the attacker away with fsmash, ftilt, bair or Blizzard, since off-stage rescues usually fail against good players [lib:20XX+XY].
- **Common errors:** Trying it while Nana is in tumble (does nothing); rescuing her into another hit.
- **Drill idea:** Nana launched to a random off-stage position not in tumble; success if she is back on stage alive within N frames.

### Belay and Squall recovery

- **id:** `belay-and-squall-recovery`
- **What:** Up B (Belay): Popo throws Nana upward on a rope and she pulls him up a long way; both become helpless. Side B (Squall Hammer): a spinning attack that gains height when B is mashed, more with both climbers [wiki:Belay][wiki:Squall_Hammer].
- **Inputs:** Belay: up B with Nana alive and near. Squall: side B, mash B to rise, steer left/right.
- **Timing:** Belay: Nana has a hitbox on frames 17-59 (16%), animation 89 frames, 25 frames of landing lag [wiki:Ice_Climbers_(SSBM)/Up_special][wiki:Ice_Climbers_(SSBM)]. Synced Squall: 8 hit timings between frames 10 and 52, 69 frames; solo: 11 hits, 89 frames [wiki:Ice_Climbers_(SSBM)/Side_special]. Aerial side B has 4 frames of landing lag [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]. Without Nana, Belay gains almost no height (it still grabs the ledge if close) [wiki:Belay].
- **Used for:** Recovery; see the Recovery section. Only one climber can hold the ledge at a time [wiki:Ice_Climbers_(SSBM)].
- **Common errors:** Belaying too low (Popo makes it, Nana falls to her death) [wiki:Belay]; using the double jump before a ledge grab so Nana's copied jump kills her [wiki:Sopo]; not mashing during Squall.
- **Drill idea:** Start off stage at varied positions; success only if both climbers end on stage or on the ledge alive.

## Neutral game

- **Stay grounded and together.** Wavedash in and out with shield, jab, ftilt, dsmash and grab. The classic approach is wavedash -> dsmash or wavedash -> grab; fair beats wavedash -> dsmash in the mirror [lib:20XX+XY].
- **Ftilt:** quick, good reach, low reward, good for shoving opponents into bad positions; short hoppers can jump over it unless it is angled up [lib:20XX+XY].
- **Jab:** very fast and leads to grab, ftilt or dsmash, but loses to [crouch cancel](../techniques/crouch-cancel.md) and has a small hitbox [lib:20XX+XY]. Grab can be comboed into from jab [wiki:Ice_Climbers_(SSBM)/Grab].
- **Ice Shot:** each climber fires a block that slides along the ground and drops off edges; the hammer itself hits on frames 15-20 and the move lasts 59 frames [wiki:Ice_Climbers_(SSBM)/Neutral_special]. It limits ground approaches and covers low recoveries [wiki:Ice_Climbers_(SSBM)].
- **Blizzard:** out-ranges most attacks, stuns, and is the usual desynced move. Synced on the ground the two fire in opposite directions; in the air both fire the same way [wiki:Blizzard].
- **Desync walls:** alternate Nana Blizzard with Popo Ice Shot/smash so something is always active. The cost is being rooted in place [lib:20XX+XY].
- **Down on both sticks:** crouch cancel / [ASDI down](../techniques/asdi.md) into dsmash or grab is a staple at low percent (a section heading of the compendium [lib:20XX+XY]; details not read).
- **Aerials:** bair (frames 8-11) and nair (frames 6-23) are the spacing aerials; uair juggles; fair is slow (frame 19) [fd]. Short-hop two aerials for an auto-cancel desync [wiki:Desynching].
- **What they want:** a grab. Everything else is there to make the opponent shield, whiff, or land next to them.

## Punish game

With both climbers, every grab is the punish: in-grab combo, then a hand-off, a throw into a Nana smash, or (where legal) a wobble. Without a grab, hits lead to short strings: dash attack and uair pop up, dsmash/fsmash send away for position, dair holds the opponent in place for a regrab. Sopo's punishes are the down throw chain grab and tech chases.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| Grab (synced) | all except Ice Climbers | any; mash-out possible below about 15-25% if started with an immediate pummel | Wobble -> dsmash | Where legal | [wiki:Wobbling], [lib:20XX+XY] |
| Grab (synced, standing) | any | any | P, ftilt, P, Blizzard, P, ftilt = 24%, then throw | Legal under the 3-pummel rule | [web:docs.google.com (Nicki)] |
| Grab -> dthrow | see hand-off list | about 50% reference | Other climber regrabs (hand-off) | Windows 2-7 frames by character | [web:docs.google.com (Nicki)] |
| Grab -> dthrow | Sheik 0-142%, Ganondorf 0-114%, Pikachu 0-83%, Yoshi 0-81%, others listed above | see ranges | Solo regrab on reaction to DI | Works as Sopo | [web:docs.google.com (Nicki)], [wiki:Ice_Climbers_(SSBM)/Grab] |
| Grab -> dthrow | Marth 0-60%, Peach 0-12%, Mario/Dr. Mario 0-15%, Mewtwo 0-16% | DI away only | Dash / dash JC regrab | No DI or DI in: they jump out | [web:docs.google.com (Nicki)] |
| Third pummel -> Nana charges fsmash -> dthrow | fastfallers | kill percent | Release fsmash at throw release | Kills earlier than a third Nana attack + uncharged smash | [web:docs.google.com (Nicki)] |
| Third pummel -> Nana charges usmash -> dthrow | non-fastfallers except very light | kill percent | Release usmash at throw release | Samus dies almost 20% earlier | [web:docs.google.com (Nicki)] |
| Uthrow -> Nana fsmash | any | when facing away from the near ledge | Sends behind Popo | Input windows in the tech entry | [web:docs.google.com (Nicki)] |
| Dthrow -> Nana dair -> Popo regrab | any | typical | Regrab | Dair has set knockback and keeps them in place; escapable with [SDI](../techniques/sdi.md) | [wiki:Ice_Climbers_(SSBM)/Grab], [wiki:Ice_Climbers_(SSBM)] |
| Bthrow (synced) | Marth, Ice Climbers, Sheik, Ness, Captain Falcon, Peach, Zelda, Mario/Dr. Mario, Pikachu, Samus, Link, Young Link, Ganondorf, DK, Bowser, Mewtwo | not given | Back throw hand-off | Entries marked "L" in the source (meaning not explained there) for Peach/Zelda, the Marios, Link, Young Link, Ganondorf | [web:docs.google.com (Nicki)] |
| Dthrow -> fair, then dash, crouch, dsmash on about frame 14 | fastfallers | typical | Covers no tech, tech in place and one tech roll unless they DI away | Sopo-compatible tech chase | [lib:20XX+XY] |
| Dash attack | any | low-mid | Aerials / grab | Launches at angle 80, 9% each [fd] | [wiki:Ice_Climbers_(SSBM)] |
| Nana Blizzard hit | any | any | Popo grab | Blizzard stun covers the grab | [wiki:Ice_Climbers_(SSBM)], [lib:20XX+XY] |
| Missed Rest | Jigglypuff | over about 20% | Backward usmash, or wobble; or Blizzard -> grab + pummel -> ftilt -> P -> Blizzard -> P -> ftilt (32%) | | [lib:20XX+XY], [web:docs.google.com (Nicki)] |

### Chain grabs and tech chases

- **Solo down throw chain grab:** see `down-throw-chain-grab` for ranges. The opponent's outs are DI mixups that force a different regrab method each time, and jumping out at the top of each range. Marth, Peach, the Marios and Mewtwo escape with no DI or DI in almost immediately [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].
- **Hand-offs:** see `down-throw-hand-off` for per-character windows. Away from the ledge Nana's throw choice is random, so hand-off loops are only a true infinite near the edge [wiki:Wobbling][wiki:Ice_Climbers_(SSBM)/Grab]. The "cookhold" is a named variation [wiki:Ice_Climbers_(SSBM)/Grab] (not described in the sources read).
- **Space animals and Captain Falcon:** regrabs exist over a wide range but DI cannot reliably be reacted to; alternatives are dthrow -> immediate dsmash on a DI-in read, up throw, or throwing for a tech chase [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].
- **Tech chases:** neutral tech is 26 frames and tech rolls 40 frames, both vulnerable from frame 21 [lib:20XX+XY]. Ice Climbers have to wavedash rather than dash to follow, which is the limiting factor; fastfallers will DI away and tech away until off stage [lib:20XX+XY]. On a missed tech, jab reset and regrab [lib:20XX+XY]. See [tech chase](../techniques/tech-chase.md).
- **Mirror match:** grabs cannot be converted while the other pair's free climber can hit you; back throw is the key move because its thrown-body hitbox splits the pair [lib:20XX+XY][wiki:Ice_Climbers_(SSBM)/Grab].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Wobble -> dsmash / fresh smash | all except Ice Climbers | any (rack damage first) | Synced grab, where legal | [wiki:Wobbling], [lib:20XX+XY] |
| Grab -> Nana charged fsmash / usmash + dthrow | any except very light | Not given as a number | After three pummels | [web:docs.google.com (Nicki)] |
| Fsmash (hammer head) | any | Not sourced | 14% per climber head hit (10% handle), frames 13-14 | [fd] |
| Usmash | any | Not sourced; "excellent for KOs at higher percent" | 11% per climber, growth 128, frames 14-18 | [fd], [wiki:Ice_Climbers_(SSBM)] |
| Dsmash | any | Not sourced | 12% per climber, frames 6-11, horizontal | [fd], [wiki:Ice_Climbers_(SSBM)] |
| Bair | any | "under 150%" | 12%/11%, frames 8-11 | [wiki:Ice_Climbers_(SSBM)], [fd] |
| Fair (handle sweetspot) | off stage | any, as a meteor | Angle 270 hitbox, frame 19 | [fd], [wiki:Ice_Climbers_(SSBM)] |
| Uthrow | any | Not sourced | Called one of the strongest throws | [wiki:Ice_Climbers_(SSBM)] |

- Kill percents for raw smashes were not found in the sources read; they depend on whether one or both hammers connect (the partner's hit lands on a target already damaged by the leader's).
- **Edgeguards:** Ice Shots fall off the edge and cover low recoveries [wiki:Ice_Climbers_(SSBM)]; a desynced Blizzard + Ice Shot wall at the ledge traps [Peach](peach.md) [lib:20XX+XY]; a fast-fall fair off stage can meteor a floating Peach, recovering afterwards with synced Squall [lib:20XX+XY]. Overall their edgeguarding is below average [wiki:Ice_Climbers_(SSBM)].
- **Ledge:** wavedash back to the ledge holding shield, drop, and rise with an invincible bair or dair while Nana gets up [lib:20XX+XY].
- **Freeze glitch** (Nana grab + Popo Squall during her hitlag) immobilises the opponent permanently in NTSC; it is banned and should not be used as a drill target [wiki:Freeze_glitch].

## Recovery

- **Options:**
  - Double jump (both climbers jump; Nana copies it).
  - Side B (Squall Hammer): mash B to rise; more height with both climbers; keeps them together [wiki:Squall_Hammer].
  - Up B (Belay): very large vertical gain with Nana present; both end helpless and separated; Nana is invincible while her hitbox is out [wiki:Belay][wiki:Ice_Climbers_(SSBM)/Up_special].
  - Sopo: Squall Hammer only (it still gains some height in Melee); Belay gives next to nothing [wiki:Squall_Hammer][wiki:Belay].
  - Air dodge (intangible on frames 4-29, 48 frames long [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]).
- **Mixups:** Squall high or low, repeated at varied heights to condition the edgeguarder [lib:20XX+XY]; Belay to the ledge versus onto the stage; a library video covers "belay stall / saving Nana" [lib:Ice Climbers Guide: How to belay stall/saving Nana] (not watched).
- **Weaknesses:** Only one climber fits on the ledge, so one of them often lands on stage in lag (Belay landing lag 25 frames [wiki:Ice_Climbers_(SSBM)/Up_special]). Belay from too low kills Nana [wiki:Belay]. A double jump before the ledge grab can kill Nana [wiki:Sopo]. Squall is slow and its hitboxes do not cover below. After Belay the two are apart and helpless, so each can be hit separately.

### Edgeguarding Ice Climbers

- **Both climbers, Squall:** hit them from below or from the side at the end of the spin; a hit that separates them leaves Nana to recover alone, and she only uses her double jump (she never uses side B or up B on her own [lib:In Depth Analysis of Nana's CPU Behavior]).
- **Both climbers, Belay:** Nana arrives first, invincible; do not challenge her. Take the ledge so Popo (pulled up after her) cannot grab it, or hit Popo, who is not invincible, at the top of the pull. Then punish whichever climber is in helpless landing lag. (General strategy; specific frame windows not sourced.)
- **Nana alone off stage:** any hit usually kills her; a smash knocks her far enough that she usually cannot return [lib:20XX+XY]. Wall Popo out while she falls.
- **Sopo:** cover the Squall Hammer path to the ledge; he has no other option [wiki:Ice_Climbers_(SSBM)].
- A realistic recovering CPU should prefer Squall when high and close (keeps Nana), Belay when low, and vary Squall height.

## Defense and out of shield

- **Shield grab:** grab on frames 7-8 [wiki:Ice_Climbers_(SSBM)/Grab]; short range, and low traction means they slide away when hit, so many shield grabs whiff.
- **Wavedash out of shield:** jump squat is 3 frames [wiki:Ice_Climbers_(SSBM)]; a wavedash is actionable after about 14 frames, then grab or dsmash. This punishes Peach's dsmash on shield (about -22) [lib:20XX+XY].
- **Aerials out of shield:** nair hits 9 frames after leaving shield and bair 11 (3 + frames 6 and 8 [fd]).
- **Desync options:** shieldstun desync, belay out-of-shield desync, roll back -> Blizzard (see tech entries).
- **Crouch cancel / ASDI down -> dsmash or grab** at low percent is a core defensive answer to weak aerials (heading "Down on Both Sticks" in [lib:20XX+XY]).
- **Spot dodge** intangible frames 2-18 of 27; **roll** frames 4-19 of 31 [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].
- **Acting after their own moves:** to shield as early as possible after an IASA move (e.g. jab) hold a direction to buffer a walk and then shield; holding shield alone waits for the full animation [same source].
- **Being grabbed:** if Popo is grabbed, a free Nana often hits the grabber, which protects Popo from chain grabs [wiki:Ice_Climbers_(SSBM)]. Against Jigglypuff specifically, a grabbed Popo leaves Nana passive [lib:20XX+XY].
- **What beats them:** attacks that hit Nana first or separate them (Peach fair, Fox shine [wiki:Ice_Climbers_(SSBM)]); platform camping and attacks from below (they are weak at protecting themselves from below [lib:20XX+XY]); spaced safe pressure on shield.

## As the training dummy

- **Weight / fall speed:** each climber weight 88, fall speed 1.6, fast-fall 2.0 (floaty, slightly light) [wiki:Ice_Climbers_(SSBM)]. They die off the top relatively early.
- **Two targets:** a scenario must specify both climbers' positions, percents and whether Nana is synced. Nana's percent is separate from Popo's [wiki:Nana].
- **Nana as a CPU:** CPU level = Popo's percent / 20 (rounded down, max 9) [lib:In Depth Analysis of Nana's CPU Behavior]. She survival-DIs more often at higher level, with the same strength when she does; she does not tech [lib:20XX+XY]; alone she walks/jumps back toward Popo, may attack on her own, uses Blizzard only from Popo 60%+, aerials from 80%+, grabs shields from 120%+ [lib:In Depth Analysis of Nana's CPU Behavior]. Because she does not tech, any knockdown on Nana can be followed by a guaranteed hit (the reason Peach's fair is so strong against them) [lib:20XX+XY]. A library item mentions Nana having 5 units of knockback armour [lib:Nana 5 Knockback Armor] (tweet, not read).
- **Hitting both:** hitting Popo and Nana (or their shields) on different frames gives the attacker extra hitlag; hitting both on the same frame is normal [lib:20XX+XY]. Drills on shield-pressure against them must account for this.
- **Separating them:** strong single hits on one climber; back throw (its thrown-body hitbox hits the other climber) [lib:20XX+XY]; Peach fair, Fox shine [wiki:Ice_Climbers_(SSBM)]. Then keep Popo away while killing Nana. Strategic rule of thumb from top players: target Nana when ahead (lowers variance), target Popo when behind [lib:20XX+XY].
- **Grabbing them:** grabbing Popo: Nana usually attacks the grabber, so throw immediately; back throw or a throw that hits both is preferred (Jigglypuff's fthrow hits both [lib:20XX+XY]). Grabbing Nana: Popo is free to smash [lib:20XX+XY].
- **Chain grabs on them:** Ice Climbers' own dthrow hand-off works on a lone climber (release frame 32, window 32-34) [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]. Sopo is vulnerable to chain grabs and throw setups because of low air and fall speed [wiki:Ice_Climbers_(SSBM)]; character-specific percents are not sourced here.
- **Strong DI/tech for a realistic Popo CPU:** survival DI on vertical finishers; tech toward Nana; mash only at the start of a wobble (the escape counter only needs to reach zero once; after that the victim breaks out automatically if the rhythm drops) [lib:20XX+XY].
- **Thresholds:** Ice Climbers' own fair grounds a crouch-cancelling Peach past about 20%; ftilt does so from about 90% [lib:20XX+XY]. Thresholds for moves used against them are not sourced.

## Matchup notes

### vs Peach

Their worst notable matchup; Peach is called the hardest counter to the Ice Climbers [wiki:Wobbling]. Float-cancelled fair is safe on their shield (at best about +4, usually +1 to +2), splits them, and knocks Nana down at any percent; Nana cannot tech, so one fair often means a dead Nana, while punishing the fair with Sopo yields about 30% [lib:20XX+XY]. Answers: do not jab (she crouch cancels it); use fair to beat her crouch cancel; punish dsmash on shield with wavedash -> grab; catch turnips and use them; grab her out of a ground float; punish turnip pulls with a grab [lib:20XX+XY]. Best stages listed: Pokemon Stadium, Yoshi's Story [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].

### vs Fox

Fox can kill Nana at almost any percent with little commitment and can camp platforms; the Ice Climbers need only one grab or hit. Advice is to make a compact "ground fortress" of safe moves and wait rather than approach [lib:20XX+XY]. Shine separates them [wiki:Ice_Climbers_(SSBM)]. Fox cannot be chain grabbed on reaction; use tech chases and hand-offs. Best stage Final Destination, worst Yoshi's Story [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].

### vs Falco

Lasers interrupt desyncs and pin Nana. One approach is letting Nana absorb approaching lasers while Popo dash dances and punishes on reaction; on Final Destination Sopo has guaranteed combos on Falco [lib:20XX+XY]. Falco can be chain grabbed on reaction past about 30% by dashing forward and pivot grabbing DI in [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].

### vs Marth

Marth out-ranges them and his aerials separate the pair; his grab on Popo is contested by Nana. Their solo chain grab on Marth only works on DI away up to 60%, so hand-offs matter (window 32-33 on DI in, with Nana exactly on top of Popo) [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].

### vs Sheik

Good punish matchup: Sheik is chain grabbed by down throw alone from 0% to about 142% with regrabs for every DI, and hand-offs have a generous 4-5 frame window [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]; baiting Sheik with Nana and grabbing leads to a chain grab, "usually to death" [lib:20XX+XY]. Sheik's answers are platform camping, needles and never being on the ground near them.

### vs Jigglypuff

Do not get Rested and do not run into bairs. Isolated Nana Blizzards out-range everything she has and are hard to punish; Ice Shots do little because she is airborne or nairs through them; long continuous desyncs are risky [lib:20XX+XY]. Jigglypuff aims to camp platforms, Pound shields and kill Nana. Best stage Pokemon Stadium, worst Dream Land [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].

### vs Captain Falcon

Falcon's speed and knee on shield are the problems; the shieldstun desync is the documented answer to repeated knees [lib:20XX+XY]. Yoshi's Story is suggested as a counterpick (less room for Falcon, useful platforms) [lib:20XX+XY]. He can be chain grabbed by reading or, arguably, reacting from about 50% [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)].

### vs Ice Climbers

Played like a 2-on-2: isolate and kill the other Nana without losing yours. Back throw is the main tool (splits them and protects the thrower); wobbling is impossible while the other pair is whole but works on a lone Popo, whose returning Nana just runs into the hits [lib:20XX+XY]. Keep the other pair above you; fair beats wavedash -> dsmash [lib:20XX+XY].

## Drill seeds

### Wobble rhythm

- **id:** `ice-climbers-wobble-rhythm`
- **Goal:** Start a wobble from a synced grab before the opponent mashes out and hold the 200 BPM alternation.
- **Player:** Ice Climbers
- **CPU:** any non-Ice-Climbers character; [Fox](fox.md), [Marth](marth.md), [Peach](peach.md) as defaults
- **Setup:** Final Destination, centre. Popo holding the CPU in a standing grab, Nana synced directly beside/behind Popo and out of whiffed-grab lag (variation: still in it). CPU at 0-60%.
- **CPU behaviour:** Mashes at a configurable rate (none / average / frame-perfect) from the first grab frame.
- **Success:** At least N alternating pummel/Nana-tilt hits with no release; optional finisher: Popo dsmash connects immediately after a Nana tilt.
- **Fail:** CPU breaks out, Popo throws, or Nana uses a smash.
- **Variations:** Dtilt version at a ledge; Blizzobble; "Tomber start" with Nana behind the opponent after a dash JC grab; low-percent starts to train beating the mash (about 15-25% is the human-escapable zone for pummel-first starts [lib:20XX+XY]).
- **Data needed:** Pummel frame 13 of 25 [wiki:Ice_Climbers_(SSBM)/Pummel]; ftilt frames 6-9, IASA 28; dtilt frames 8-11, IASA 29 [fd]; grab-escape timer rules; Nana 6-frame input delay.

### Three-pummel grab combo into charged smash

- **id:** `ice-climbers-grab-combo-finisher`
- **Goal:** Execute the wobble-ban-legal maximum: 3 pummels + 2-3 Nana attacks, then Nana's charged smash on the throw release.
- **Player:** Ice Climbers
- **CPU:** [Fox](fox.md), [Falco](falco.md) (fsmash finisher); [Samus](samus.md), [Marth](marth.md), [Sheik](sheik.md) (usmash finisher)
- **Setup:** Synced standing grab at centre stage. CPU at 60-110%.
- **CPU behaviour:** Mashes; DIs the down throw randomly; DIs the smash for survival.
- **Success:** Sequence P, ftilt, P, Blizzard, P completes; Nana's charged smash hits on release; CPU dies or reaches a target damage.
- **Fail:** Opponent mashes out, the smash whiffs, or more than 3 pummels are used.
- **Variations:** Up throw -> Nana backward fsmash when the near ledge is behind Popo; hand-off start (P, Blizzard, P, ftilt, P, Blizzard); ledge version with dtilts.
- **Data needed:** In-grab damage values and finisher rules [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]; dthrow release frame per character (same source); smash charge windows (fsmash frames 7-8, usmash 8-9 [wiki:Ice_Climbers_(SSBM)/Forward_smash][wiki:Ice_Climbers_(SSBM)/Up_smash]).

### Down throw hand-off timing

- **id:** `ice-climbers-dthrow-handoff`
- **Goal:** Regrab with the second climber inside the character-specific window.
- **Player:** Ice Climbers
- **CPU:** [Fox](fox.md), [Falco](falco.md), [Marth](marth.md), [Peach](peach.md), [Captain Falcon](captain-falcon.md), [Sheik](sheik.md)
- **Setup:** Flat stage, synced grab, CPU at about 50%, Nana directly on top of Popo (required for Marth/Luigi) or a step forward (helps against Falco on DI away).
- **CPU behaviour:** DI in or away at random; jumps / shines / attacks on the first actionable frame.
- **Success:** Nana's grab connects during the window (e.g. Fox frames 27-30 DI in, 27-29 DI away; Marth 32-33 / 32-34).
- **Fail:** CPU escapes; report how many frames early or late the grab was.
- **Variations:** Chain several hand-offs toward a ledge; raise percent (windows shrink by about a frame); Nana throws next (near the ledge she throws outward).
- **Data needed:** Release frames and windows table [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]; grab active frames 7-8; Nana input delay 6 frames.

### Solo down throw chain grab on Sheik

- **id:** `ice-climbers-sopo-chaingrab-sheik`
- **Goal:** React to DI after each down throw and pick the right regrab.
- **Player:** Ice Climbers (Nana dead, or alive for a wobble/hand-off conversion variant)
- **CPU:** [Sheik](sheik.md); also [Ganondorf](ganondorf.md), [Pikachu](pikachu.md), [Yoshi](yoshi.md)
- **Setup:** Final Destination. Popo holding Sheik at 0%.
- **CPU behaviour:** Random DI each throw (none, in, away); jumps out as soon as hitstun ends.
- **Success:** Consecutive regrabs carry Sheik to a target percent (e.g. 100%) or to the ledge.
- **Fail:** Sheik acts before the regrab.
- **Variations:** Other victims with their ranges (Ganondorf 0-114%, Pikachu 0-83%, Yoshi 0-81%); Marth with DI away only (0-60%); Falco from 30% using dash forward + pivot grab.
- **Data needed:** Chain grab tables [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)]; dthrow release frame 33 on Sheik; Popo dash/walk speeds (1.4 / 0.95 [wiki:Ice_Climbers_(SSBM)]), jump squat 3.

### Dash-dance Blizzard into grab

- **id:** `ice-climbers-dd-blizzard-desync`
- **Goal:** Produce a Nana-only Blizzard from a dash dance and convert a Blizzard hit into a Popo grab.
- **Player:** Ice Climbers
- **CPU:** [Marth](marth.md), [Sheik](sheik.md), [Jigglypuff](jigglypuff.md), [Peach](peach.md)
- **Setup:** Synced climbers at centre; CPU just outside Blizzard range.
- **CPU behaviour:** Approaches on the ground or with a short-hop aerial on a random delay; sometimes waits.
- **Success:** Nana enters Blizzard while Popo remains actionable; if the CPU is hit by Blizzard, Popo grabs it before it can act.
- **Fail:** Both climbers Blizzard, or Popo is hit.
- **Variations:** Roll back -> Blizzard and spot dodge -> Blizzard desyncs; Popo fires Ice Shot behind the Blizzard instead of grabbing.
- **Data needed:** Blizzard hits frames 16-66, 79 total [web:docs.google.com (Nicki, Ice Climbers Information and Data Sheet)][fd]; dash/turn rules; Blizzard hitstun (not in the dump).

### Shieldstun desync against safe aerials

- **id:** `ice-climbers-shieldstun-desync`
- **Goal:** Input Nana's jump in the last 6 frames of shieldstun so only she acts.
- **Player:** Ice Climbers
- **CPU:** [Captain Falcon](captain-falcon.md) (knee), [Ganondorf](ganondorf.md) (fair), [Marth](marth.md) (double fair)
- **Setup:** Both climbers shielding, shields the same size, CPU positioned so the aerial hits both shields on the same frame.
- **CPU behaviour:** Repeats the aerial on shield at its fastest safe rhythm.
- **Success:** Nana jumps and her Blizzard (or Ice Shot) hits the CPU before its next aerial; Popo stays in shield or punishes out of shield.
- **Fail:** Both climbers jump, neither acts, or the shields are hit on different frames.
- **Variations:** Belay out-of-shield desync as the easier alternative; different move damages to shift the window.
- **Data needed:** Shieldstun and hitlag formulas for the CPU move's damage; Nana's 6-frame delay [lib:20XX+XY]; Blizzard start-up.

### Punish Peach's down smash on shield

- **id:** `ice-climbers-punish-peach-dsmash`
- **Goal:** Shield float-cancel fair -> dsmash and punish the dsmash with wavedash out of shield -> grab.
- **Player:** Ice Climbers
- **CPU:** [Peach](peach.md)
- **Setup:** Climbers shielding at centre. Peach ground-floats in with fair.
- **CPU behaviour:** FC fair on shield, then random: dsmash (2 or 3 hits on shield), jab -> jump, re-float, roll, spot dodge.
- **Success:** On dsmash: keep shielding until the last shield hit, wavedash in, grab during dsmash's end lag (about -22; frame-tight if three hits landed on shield and Peach jabs afterwards) [lib:20XX+XY]. On ground float: immediate grab. On jab -> jump or plain jump: bair, Squall or nair.
- **Fail:** Rolling or dropping shield between fair and dsmash (the dsmash is unavoidable there) [lib:20XX+XY]; grab whiffs; Nana hit by fair.
- **Variations:** Climbers separated by the fair (then wavedash in -> dsmash instead of grab); shield DI out on the first dsmash hit to prevent the third.
- **Data needed:** Peach dsmash timing (hits 5-22, 39 total) [wiki:Peach_(SSBM)/Down_smash]; wavedash actionable frame (about 14 [lib:20XX+XY]); grab frames 7-8.

### Protect and re-sync Nana

- **id:** `ice-climbers-protect-nana`
- **Goal:** After a separation, keep the opponent off Nana and get back in sync.
- **Player:** Ice Climbers
- **CPU:** [Fox](fox.md), [Peach](peach.md), [Marth](marth.md)
- **Setup:** Nana knocked a platform-length away from Popo (on stage, variation: off stage and not in tumble), CPU between them or next to Nana. Popo at a chosen percent (sets Nana's CPU level).
- **CPU behaviour:** Targets Nana with its kill/launch move; switches to Popo if he comes within range carelessly.
- **Success:** Nana is alive and synced within N seconds; bonus if Popo hit the CPU away (fsmash, ftilt, bair or Blizzard).
- **Fail:** Nana dies, or Popo is hit/grabbed during the rescue.
- **Variations:** Side B "teleport" rescue on stage; up B rescue off stage; decide to take a Sopo combo instead when the CPU is incapacitated.
- **Data needed:** Nana AI level table [lib:In Depth Analysis of Nana's CPU Behavior]; teleport conditions [lib:20XX+XY]; Belay invincibility frames [wiki:Ice_Climbers_(SSBM)/Up_special].

### Recover with both climbers

- **id:** `ice-climbers-recovery-both-alive`
- **Goal:** Return to stage without losing Nana.
- **Player:** Ice Climbers
- **CPU:** [Marth](marth.md), [Sheik](sheik.md), [Fox](fox.md)
- **Setup:** Both climbers off stage together, synced, at a randomised height and distance; double jump available or not.
- **CPU behaviour:** Edgeguards: takes the ledge against Belay, or attacks the Squall path.
- **Success:** Both climbers alive on stage or one on the ledge and one on stage, neither hit.
- **Fail:** Either climber dies.
- **Variations:** Sopo-only Squall recovery; Nana separated and slightly behind; mix Squall heights to bait the edgeguarder.
- **Data needed:** Squall height gain per B press (not sourced), Belay distance (not sourced), Belay timings and landing lag 25 [wiki:Ice_Climbers_(SSBM)/Up_special], ledge occupancy rule.

### Mirror: back throw split and kill Nana

- **id:** `ice-climbers-ditto-bthrow-split`
- **Goal:** In the mirror match, grab Popo, back throw to split the pair, and kill Nana while walling out Popo.
- **Player:** Ice Climbers
- **CPU:** [Ice Climbers](ice-climbers.md)
- **Setup:** Both pairs synced at centre, CPU pair in grab range and shielding or whiffing a move.
- **CPU behaviour:** CPU Popo tries to return to Nana; CPU Nana runs back toward her Popo and does not tech.
- **Success:** CPU Nana loses her stock while the player's Nana survives.
- **Fail:** Player's Nana dies, or CPU pair re-syncs.
- **Variations:** Player as Sopo (1-on-2); desync a Nana Blizzard to wall Popo while the player's Popo edgeguards Nana.
- **Data needed:** Back throw thrown-body hitbox (not in the dump), dsmash/fsmash knockback on weight 88, Nana AI behaviour.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlPp.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/ice-climbers.json`](../framedata/ice-climbers.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 4-7 | 2 | 45 | 0 | 100 | - |  | 29 | 16 | 2 | -9 |  |
| Jab 2 | `jab2` | 5-7 | 4 | 45 | 0 | 100 | 30 |  | 30 | 19 | 3 | -10 | starts 1 frame late (included) |
| Dash attack | `dash_attack` | 11-12 | 9 | 80 | 90 | 40 | - |  | 41 | 38 | 6 | -20 |  |
| Forward tilt (angled up) | `ftilt_high` | 6-9 | 8 | Sakurai | 26 | 100 | - |  | 31 | 28 | 5 | -16 |  |
| Forward tilt (slightly up) | `ftilt_mid_high` | 6-9 | 8 | Sakurai | 26 | 100 | - |  | 31 | 28 | 5 | -16 |  |
| Forward tilt | `ftilt` | 6-9 | 8 | Sakurai | 26 | 100 | - |  | 31 | 28 | 5 | -16 |  |
| Forward tilt (slightly down) | `ftilt_mid_low` | 6-9 | 8 | Sakurai | 26 | 100 | - |  | 31 | 28 | 5 | -16 |  |
| Forward tilt (angled down) | `ftilt_low` | 6-9 | 8 | Sakurai | 26 | 100 | - |  | 31 | 28 | 5 | -16 |  |
| Up tilt | `utilt` | 8-9, 11-12, 14-15, 17-18, 20-21, 23-24 | 1 | 95 | 15 | 20 | - |  | 49 | 42 | 2 | -31 |  |
|  |  | 26 | 7 | 90 | 40 | 100 | - |  |  |  | 5 | -10 |  |
| Down tilt | `dtilt` | 8-11 | 5 | 70 | 30 | 100 | - |  | 34 | 29 | 4 | -16 |  |
| Forward smash | `fsmash` | 13-14 | 14/10 | Sakurai | 40 | 105 | - |  | 47 | 47 | 8 | -25 | charge hold frame 7 |
| Up smash | `usmash` | 14-18 | 11 | 83 | 50 | 128 | - |  | 49 | 44 | 6 | -23 | charge hold frame 8 |
| Down smash | `dsmash` | 6-11 | 12 | Sakurai | 50 | 110 | - |  | 39 | 36 | 7 | -22 | charge hold frame 2 |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 6-23 | 8 | Sakurai | 20 | 100 | - |  | 49 | 46 | 5 | 20 | 10 | <6, >29 | -5 |  |
| Forward air | `fair` | 19-22 | 11/10/9 | 270/70 | 40 | 100 | - |  | 59 | 55 | 6 | 20 | 10 | <3, >54 | -4 |  |
| Back air | `bair` | 8-11 | 12/11 | Sakurai | 30 | 110/100 | - |  | 39 | 36 | 7 | 20 | 10 | <8, >18 | -3 |  |
| Up air | `uair` | 6-9 | 9 | 70 | 10 | 140 | - |  | 39 | 30 | 6 | 32 | 16 | <6, >26 | -10 |  |
|  |  | 10-23 | 7 | 70 | 10 | 140 | - |  |  |  | 5 |  |  |  | -11 |  |
| Down air | `dair` | 3-52 | 9 | Sakurai | 0 | 110 | 36 |  | 65 | 64 | 6 | 25 | 12 | <3, >57 | -6 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 7-8 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 13 | 25 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 11 | 5 | 45 | 70 | 60 | - | - | 28 | 49 |  |
| Back throw | `bthrow` | 7 | 7 | 60 | 80 | 30 | - | - | 8 | 39 |  |
| Up throw | `uthrow` | 11 | 5 | 88 | 110 | 28 | - | - | 31 | 59 |  |
| Down throw | `dthrow` | 6 | 6 | 80 | 70 | 40 | - | - | 36 | 49 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Ice Shot, ground | `special_n` | 15-20 | 9 | 80 | 80 | 60 | - |  | 59 | - | 6 | - |  |
| Neutral B: Ice Shot, air | `special_air_n` | 15-20 | 9 | 80 | 80 | 60 | - |  | 59 | - | 6 | - |  |
| Side B: Squall Hammer, ground, 1 | `special_s1` | 12, 17, 23, 31, 41, 55 | 2 | 70 | 5 | 130 | - |  | 89 | - | 2 | - |  |
|  |  | 14, 20, 27, 35, 47 | 4 | 70 | 5 | 130 | - |  |  |  | 3 | - |  |
| Side B: Squall Hammer, ground, 2 | `special_s2` | 10, 18, 28, 41 | 2 | 70 | 5 | 130 | - |  | 69 | - | 2 | - |  |
|  |  | 14, 23, 34, 52 | 4 | 70 | 5 | 130 | - |  |  |  | 3 | - |  |
| Side B: Squall Hammer, air, 1 | `special_air_s1` | 12, 17, 23, 31, 41, 55 | 2 | 70 | 5 | 130 | - |  | 89 | - | 2 | - |  |
|  |  | 14, 20, 27, 35, 47 | 4 | 70 | 5 | 130 | - |  |  |  | 3 | - |  |
| Side B: Squall Hammer, air, 2 | `special_air_s2` | 10, 18, 28, 42 | 2 | 70 | 5 | 130 | - |  | 69 | - | 2 | - |  |
|  |  | 14, 23, 35, 52 | 4 | 70 | 5 | 130 | - |  |  |  | 3 | - |  |
| Up B: Belay, ground, Start | `special_hi_start` | - | - | - | - | - | - | - | 16 | - | - | - |  |
| Up B: Belay, ground, Throw | `special_hi_throw` | - | - | - | - | - | - | - | 42 | - | - | - |  |
| Up B: Belay, ground, Throw2 | `special_hi_throw2` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Up B: Belay, ground, Start | `special_hi_start_304` | - | - | - | - | - | - | - | 16 | - | - | - |  |
| Up B: Belay, ground, Throw | `special_hi_throw_305` | - | - | - | - | - | - | - | 42 | - | - | - |  |
| Up B: Belay, air, Start | `special_air_hi_start` | - | - | - | - | - | - | - | 16 | - | - | - |  |
| Up B: Belay, air, Throw | `special_air_hi_throw` | - | - | - | - | - | - | - | 42 | - | - | - |  |
| Up B: Belay, air, Throw2 | `special_air_hi_throw2` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Up B: Belay, air, Start | `special_air_hi_start_309` | - | - | - | - | - | - | - | 16 | - | - | - |  |
| Up B: Belay, air, Throw | `special_air_hi_throw_310` | - | - | - | - | - | - | - | 42 | - | - | - |  |
| Down B: Blizzard, ground | `special_lw` | - | - | - | - | - | - | - | 79 | - | - | - |  |
| Down B: Blizzard, air | `special_air_lw` | - | - | - | - | - | - | - | 79 | - | - | - |  |

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
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-20 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-26 | 6-11, 21-26 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-21 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-22 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-20 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-26 | 19-20, 25-26 (6%) | 49 | - |  |
| Getup roll forward (face down) | `getup_roll_forward_facedown` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-24 | - | 35 | - |  |
| Tech in place | `tech_in_place` | intangible 2-20 | - | 26 | - | starts 1 frame late (included) |
| Tech roll forward | `tech_roll_forward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Tech roll backward | `tech_roll_backward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Wall tech | `wall_tech` | - | - | 20 | - | starts 1 frame late (included) |
| Wall tech jump | `wall_tech_jump` | - | - | 40 | - | starts 1 frame late (included) |
| Ceiling tech | `ceiling_tech` | intangible 2-17 | - | 26 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-55 | - | 59 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 34 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-35 | 39-42 (10/8%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-23 | 27-30 (8/6%) | 54 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-56 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-27 | - | 49 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-19 | - | 19 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 28 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-15 | - | 15 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 23 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Down air | jump | 6 | `dair` |
| Shield grab | direct | 7 | `grab` |
| Neutral air | jump | 9 | `nair` |
| Up air | jump | 9 | `uair` |
| Back air | jump | 11 | `bair` |
| Up smash | jump cancel | 15 | `usmash` |
| Forward air | jump | 22 | `fair` |
| Spot dodge | direct | intangible 2-18 of 27 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 15 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Ice Climbers indexed by [The Melee Library](https://www.meleelibrary.com/#ice-climbers) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [Are You an Ice Climbers Player?](https://www.youtube.com/watch?v=wLJLSX_htYM) | SSBM Tutorials | They give an overview of Ice Climbers the character to give you an idea of whether you would like to play them. |
| [2020 Ice Climbers Melee Techs Guide](https://www.youtube.com/watch?v=aUzDwHuKoWI&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=22&t=0s) | Third Chair | Video guide on performing useful Ice Climbers tech in 2020. |
| [Ice Climbers Hitboxes and Frame Data](http://smashboards.com/threads/complete-ice-climbers-hitboxes-and-frame-data.285394/) | Stratocaster, Standardtoaster, and SuperDoodleMan |  |
| [Varokaa Heikkoa Jäätä](http://smashboards.com/threads/varokaa-heikkoa-j%C3%A4%C3%A4t%C3%A4.317195/) | Fly Amanita | An Ice Climbers guide. |
| [Ice Climbers Matchup Guide 2007](http://smashboards.com/threads/ice-climber-match-up-guide-info-on-16-character-match-ups-updated-12-19-10-w-vids.112141/) | Binx | With input from Wobbles |
| [Guide to Desyncing: Treat Your Opponents Even More Coldly](http://smashboards.com/threads/guide-to-desynching-treat-your-opponents-even-more-coldly.53912/) | Exarch | Exacron discusses the various methods of de-synching. Includes a section on the Freeze glitch. |
| [How to do the Infinite/Wobbling](http://smashboards.com/threads/how-to-do-the-infinite-wobbling.95566/) | Wobbles |  |
| [Ledge Chain-grabbing / The Handoff FAQ](http://smashboards.com/threads/ledge-chain-grabbing-the-handoff-faq.216589/) | Wobbles |  |
| [The Solution: An Ice Climbers Guide to Non-Grab Skillz](http://smashboards.com/threads/the-solution-an-ice-climbers-guide-to-non-grab-skillz-by-choknater.112413/) | Choknater | A 2007 post detailing combos and grab follow-ups (in fear that wobbling would be banned completely). |
| [Behind Wobbling: All the Stuff You Don't See](http://smashboards.com/threads/behind-wobbling-all-the-stuff-you-dont-see.340028/) | Tomer | Discusses how to do the infinite properly, how hard is wobbling, the psychology behind wobbling, stuff that leads into grabs, lagless setups, should wobbling be banned? |
| [Data Archive](http://smashboards.com/threads/lonely-peefs-data-archive-blizzard-freezing-info-added.272919/) | Peef | Peef answers questions about Nana's throw and pummel tendencies, how DI affects throw combos, which quick grab combos kill faster, and when Blizzard will freeze the opponent. |
| [Use Shield SDI To Get Synced Grabs](http://smashboards.com/threads/use-shield-sdi-to-get-synced-grabs-when-you-dont-deserve-them-vids.286056/) | Peef | Frame perfect wobble with blizzard instead of ftilt or dtilt. |
| [Blizzobbling](http://smashboards.com/threads/blizzobbling-new-ic-infinite.280371/) | Peef |  |
| [Ice Climbers’ Shield Pressure](http://smashboards.com/threads/ice-climbers-shield-pressure.280913/) | Kyu Puff | Ice Climbers can do crazy shield pressure utilizing desyncs. |
| [Nana Behavior Based on Popo’s Percent](http://smashboards.com/threads/leveling-up-nanas-reference-ai.363085/page-4#post-19379976) | Achilles |  |
| [New No Setup IC “Jump Desync”](http://smashboards.com/threads/new-no-setup-ic-jump-desync.366189) | SleepyK and Fly Amanita |  |
| [The Metronome Handoff Thread](http://smashboards.com/threads/the-metronome-handoff-thread-now-with-magus-collab-charts-aka-it-is-now-perfect.269173/) | Peef |  |
| [Nana-Rocket: How To Do It and Why It Works](http://smashboards.com/threads/nana-rocket-how-to-do-it-and-why-it-works.274911/) | Peef |  |
| [Ice Climbers’ Invincible Ledgedash Options](https://www.youtube.com/watch?v=iSCw5DH14t8) | Practical TAS | A video showcasing Ice Climbers’ options they can perform intangibly from a ledgedash. |
| [Ice Climber Tutorials](https://www.youtube.com/playlist?list=PLrTiyucJDXl4EbzoRki2zzOhkmImpATiv) | Sam Christensen | A series of videos about Ice Climbers. Includes hand-offs, wobbling, basic desyncs, advanced desyncs, shieldstun desyncs, and probably more since the writing of this. |
| [Wobbling Tutorial](https://www.youtube.com/watch?v=28C6Kn44uKs) | ChuDat |  |
| [Basic Desync Tutorial](https://www.youtube.com/watch?v=59UMYKRMhws) | SSBM Tutorials |  |
| [Top 5 Essential Ice Climber Combos](https://www.youtube.com/watch?v=7t8FKLPSrjM) | SSBM Tutorials |  |
| [Requirements of Ice Climbers Freeze Glitch](https://www.reddit.com/r/SSBM/comments/4c7y7w/requirements_of_ice_climbers_freeze_glitch/) | Evsen |  |
| [20XX+XY](https://docs.google.com/document/d/1DPqPLDHfBWMluMMfd8KpDVN8s37866CTb4xQVW-_KLk/edit#heading=h.7j26sb3g8g57) | Dennis Frogman | A massive collection of information and quotes from respectable players about Ice Climber strategies. |
| [One Inputs Two Actions: Making Synced Ice Climbers Act Independently](https://www.reddit.com/r/SSBM/comments/4ex2hd/one_input_two_actions_sometimes_you_can_make/) | Stabby McKniferson | Very precise inputs can make both Ice Climbers perform different attacks at the same time. |
| [Nana 5 Knockback Armor](https://twitter.com/kyu_puff/status/730174703776604160) | Kyu Puff |  |
| [Misconceptions about Ice Climbers](http://www.meleeitonme.com/ice-climbers-misconceptions/) | Fly Amanita |  |
| [Ice Climbers Ditto Guide](https://www.youtube.com/watch?v=8_jem_DSbJc) | Nintendude |  |
| [In Depth Analysis of Nana's CPU Behavior](https://docs.google.com/document/d/1GlMbVLgCzbP-HQa2q97eeTuRy61qxvOx-PgvuiqSVDg/edit) | BigVegetaBlunts |  |
| [Stuff You Should Know](https://www.youtube.com/watch?v=aLDvW9SwZns) | Blizzardish | Old video of useful desyncs. |
| [Blizzobble Ice Climber Infinite](https://www.youtube.com/watch?v=m-EX0JiR0fs) | Peef | An alternative to regular wobbling. |
| [Ice Climbers are Silly](https://www.youtube.com/watch?v=fV3QNpesRYo) | Sesh Evans | An old video of random little Ice Climbers tricks. |
| [Derf's Ice Climber Tutorials](https://www.youtube.com/playlist?list=PLB1V4vYNobeaL4I0LFtQfYwm53DNHOgQ7) | DerfMidWest | A playlist of not only basic Ice Climber tech tutorials but also some obscure stuff that is really interesting. |
| [Ice Climber Mechanics: "The Force"](https://www.youtube.com/watch?v=XGwUVhxoBM0) | DerfMidWest | An explanation of the "gravitational pull" of the main Ice Climber on the backup climber. |
| [How to Beat Ice Climbers](https://www.youtube.com/watch?v=mwD3bRniC5g) | SSBM Tutorials and CDK | General guide to beating ICs. |
| [7 Hours of dizzkidboogie's Ice Climbers Analysis](https://www.youtube.com/watch?v=qFzzN12WJKE) | DizzKidBoogie and Jib | A long, but immensely in-depth analysis of Ice Climbers prompted by ChuDat's set against HungryBox at Dreamhack Austin 2017. [Part 1](https://www.youtube.com/watch?v=qFzzN12WJKE) [Part 2](https://www.youtube.com/watch?v=3kNedNB-I3I) |
| [Sopo Dthrow Chaingrab on Sheik](https://www.youtube.com/watch?v=BcL5WbgT6Rg) | PracticalTAS | The details of the chaingrab. |
| [Ice Climbers Guide: How to belay stall/saving Nana](https://www.youtube.com/watch?v=RUIwf7oQrWk) | Ziggy Stardust |  |
| [Ice Climbers Melee Chaingrab Guide](https://www.youtube.com/watch?v=9NcTl2OfmdY&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=20&t=0s) | Third Chair |  |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Ice Climbers (SSBM): https://www.ssbwiki.com/Ice_Climbers_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Ice_Climbers_(SSBM)/Grab , /Pummel , /Up_throw , /Forward_throw , /Neutral_special , /Side_special , /Up_special , /Forward_smash , /Up_smash , /Down_smash , /Forward_tilt , /Down_tilt , /Up_tilt , and the aerial pages
- SSBWiki, Wobbling: https://www.ssbwiki.com/Wobbling
- SSBWiki, Desynching: https://www.ssbwiki.com/Desynching
- SSBWiki, Ice Climbers / Nana (universe page): https://www.ssbwiki.com/Nana
- SSBWiki, Sopo: https://www.ssbwiki.com/Sopo
- SSBWiki, Belay, Squall Hammer, Blizzard, Ice Shot, Freeze glitch, Chain grab: https://www.ssbwiki.com/Belay , https://www.ssbwiki.com/Squall_Hammer , https://www.ssbwiki.com/Blizzard , https://www.ssbwiki.com/Ice_Shot , https://www.ssbwiki.com/Freeze_glitch , https://www.ssbwiki.com/Chain_grab
- SSBWiki, List of SSBM tier lists (NTSC) and Template:MeleeTiers: https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Nicki / Nopia, "Ice Climbers Information and Data Sheet" (chain grab tables, hand-off windows, in-grab combos, shield safety, stage picks; linked from SSBWiki's Ice Climbers grab page): https://docs.google.com/document/d/1e2WfuNH1I86On59O53FubxYzA-zYMZKZVIrCPNVEqhk/
- Melee Library card "20XX+XY" (e. dennis frogman; read: wobbling, desyncs, tech chasing, Peach, Jigglypuff, Ice Climbers mirror and Kirby sections): https://docs.google.com/document/d/1DPqPLDHfBWMluMMfd8KpDVN8s37866CTb4xQVW-_KLk/
- Melee Library card "In Depth Analysis of Nana's CPU Behavior" (BigVegetaBlunts; draft document): https://docs.google.com/document/d/1GlMbVLgCzbP-HQa2q97eeTuRy61qxvOx-PgvuiqSVDg/
- Melee Library "Ice Climbers" section: card titles and descriptions only for Smashboards threads (403), Reddit posts (blocked), meleeitonme.com (unreachable) and YouTube videos.
- Frame data dump: `Ice Climbers - Popo.json`, `Ice Climbers - Nana.json`
