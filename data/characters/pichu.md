---
schema: melee-character/v1
id: pichu
name: Pichu
aliases: []
tier: "D (22nd of 26), 2021 list"
archetype: [rushdown, lightweight, glass-cannon, combo-food, chaingrab]
related: [pikachu]
summary: Pichu wins by never getting hit, stringing neutral airs and up airs together, chain grabbing fastfallers with up throw, and finishing with up smash or an edgeguard.
key_tech: [self-damage-management, nair-strings, uthrow-chaingrab, agility-recovery, agility-landing, dsmash-edgeguard, fsmash-ledge-trap]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlPc.dat
framedata: ../framedata/pichu.json
code: src/melee/ft/kinds/ftPichu
specials:
  neutral_b: "Thunder Jolt"
  side_b: "Skull Bash"
  up_b: "Agility"
  down_b: "Thunder"
attributes:
  weight: 55
  gravity: 0.11
  fall_speed: 1.9
  fast_fall_speed: 2.5
  jump_squat: 3
  jumps: 2
  walk_speed: 1.24
  dash_speed: 1.8
  run_speed: 1.72
  traction: 0.1
  air_speed: 0.85
  landing_lag: 2
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [2, 22, 2]
  dash_attack: [5, 50, 8]
  ftilt_high: [5, 30, 9]
  ftilt: [5, 30, 8]
  ftilt_low: [5, 30, 7]
  utilt: [7, 24, 6]
  dtilt: [7, 19, 7]
  fsmash: [16, 50, 6]
  usmash: [9, 41, 16]
  dsmash: [7, 51, 13]
  nair: [3, 40, 12]
  fair: [10, 40, 2]
  bair: [4, 60, 9]
  uair: [4, 28, 4]
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
  special_s_end: [null, 30, 0]
  special_air_s_start: [null, 14, 0]
  special_air_s_hold: [null, 6, 0]
  special_s_304: [4, 40, 4]
  special_air_s_end: [null, 30, 0]
  special_hi_start: [null, 14, 0]
  special_hi_start_307: [null, 14, 0]
  special_hi_end: [null, 50, 0]
  special_air_hi_start: [null, 14, 0]
  special_air_hi_start_310: [null, 14, 0]
  special_air_hi_end: [null, 50, 0]
  special_lw_start: [null, 18, 0]
  special_lw_loop: [null, 10, 0]
  special_lw_loop_314: [1, 10, 13]
  special_lw_end: [null, 36, 0]
  special_air_lw_start: [null, 18, 0]
  special_air_lw_loop: [null, 10, 0]
  special_air_lw_loop_318: [1, 10, 13]
  special_air_lw_end: [null, 36, 0]
oos:  # option: frame the hitbox is out
  nair: 6
  bair: 7
  uair: 7
  grab: 7
  usmash: 10
  fair: 13
  dair: 17
resources: 3
# generated: end
---

# Pichu

<!-- GENERATED:attributes -->
## Attributes

Read from `PlPc.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 55 |
| Gravity | 0.11 |
| Terminal fall speed | 1.9 |
| Fast-fall speed | 2.5 |
| Jump squat (frames before airborne) | 3 |
| Full hop / short hop initial Y speed | 2.6 / 1.7 |
| Air jump Y multiplier | 1 |
| Jumps | 2 |
| Walk max speed | 1.24 |
| Dash initial speed / run max speed | 1.8 / 1.72 |
| Ground friction (traction) | 0.1 |
| Air max horizontal speed | 0.85 |
| Air acceleration (base + stick) | 0.02 + 0.03 |
| Air friction | 0.01 |
| Normal landing lag | 2 |
| Shield size | 24.3 |
<!-- /GENERATED:attributes -->

## Overview

Pichu is a clone of [Pikachu](pikachu.md) that is smaller, lighter (the lightest
character in the game [wiki:Pichu_(SSBM)]) and damages itself with most electric moves.
It moves well: fast dash, low landing lag, a good
[ledgedash](../techniques/ledgedash.md) and a small body make it hard to hit
[wiki:Pichu_(SSBM)]. Its game plan is built on nair, which is active on frame 3 and has
only 6 frames of [L-cancelled](../techniques/l-cancel.md) landing lag [fd], plus uair
juggles, uthrow chain grabs on fastfallers and usmash as the kill move. Its range is very
poor, its grab is the third shortest in the game, and nair-heavy neutral is predictable
and loses to [crouch cancel](../techniques/crouch-cancel.md) [wiki:Pichu_(SSBM)]. Pichu
dies extremely early and is comboed easily, so it must win many more neutral exchanges
than its opponent. It is rarely played seriously.

## Strengths and weaknesses

- **Strengths:**
  - Nair: frame 3, 12% clean, landing lag 12 frames or 6 with L-cancel [fd]; combos into
    itself at almost any percent [wiki:Pichu_(SSBM)].
  - Strong, fast smashes for their speed: usmash (frame 9, 16%) and the last hit of
    fsmash kill from about 70%; dsmash semi-spikes (angle 160) and is intangible on
    frames 7-10 [wiki:Pichu_(SSBM)] [wiki:Pichu_(SSBM)/Down_smash] [fd].
  - Uthrow chain grabs fastfallers; dthrow sets up jab resets and tech chases
    [wiki:Pichu_(SSBM)].
  - Long, flexible recovery with up B (Agility) and side B (Skull Bash)
    [wiki:Pichu_(SSBM)].
  - Large shield relative to its body, so it is hard to shield poke [wiki:Pichu_(SSBM)].
  - Tech in place has 2 vulnerable frames instead of the usual 6 [wiki:Tech].
- **Weaknesses:**
  - Lightest character; average fall speed; high hitstun; easily comboed and killed
    [wiki:Pichu_(SSBM)].
  - Recoil damage on electric moves, including the recovery [wiki:Recoil_damage].
  - Very short range and third-shortest grab [wiki:Pichu_(SSBM)].
  - Short tech rolls and get-ups, slow short ledge roll: easy to tech chase
    [wiki:Pichu_(SSBM)].
  - Uair has no semi-spike part, unlike Pikachu's [wiki:Pichu_(SSBM)/Up_aerial].

## Character tech

### Self-damage management

- **id:** `self-damage-management`
- **What:** Most electric moves add damage to Pichu itself. The player chooses
  non-electric moves where possible and accepts recoil only when the move is worth it.
- **Inputs:** None specific. Know the list.
- **Timing:** Recoil per use in Melee [wiki:Recoil_damage] [wiki:Pichu_(SSBM)]:
  neutral B (Thunder Jolt) 1%; side B (Skull Bash) 1%; up B (Agility) 1% for the first
  warp and 3% more for the second; down B (Thunder) 3% only if the bolt reaches Pichu;
  fsmash 2%; fair up to 4% (1% per hit); dair 1%, 2% if it lands during the move; pummel
  1%; fthrow 1%. Recoil ignores staleness and intangibility and causes no knockback
  [wiki:Recoil_damage]. Moves with no recoil include jab, tilts, dash attack, usmash,
  dsmash, nair, bair, uair, bthrow, uthrow and dthrow [wiki:Pichu_(SSBM)].
- **Used for:** Staying alive: a full two-warp recovery costs 4% each time.
- **Common errors:** Pummelling for no reason; spamming Thunder Jolt; using fair as a
  combo move (4% to self for about 7% dealt).
- **Drill idea:** Run any combo or edgeguard drill with a counter of self-inflicted
  damage and a cap the player must stay under.

### Neutral air strings

- **id:** `nair-strings`
- **What:** [SHFFL](../techniques/shffl.md) nair into another nair, uair, grab or usmash.
- **Inputs:** Short hop, nair, [fast fall](../techniques/fast-fall.md), L-cancel, then
  jump again or act on the ground.
- **Timing:** Nair is active frames 3-28: 12% (base knockback 18, growth 100) on frames
  3-10 and 9% (base 0) after; landing lag 12, or 6 when L-cancelled; auto-cancels from
  frame 35 [fd] [wiki:Pichu_(SSBM)/Neutral_aerial]. Pichu's L-cancelled nair has one
  frame less landing lag than Pikachu's [wiki:Pichu_(SSBM)/Neutral_aerial].
- **Used for:** Approach, combo filler, off-stage wall of hits, and at certain percents a
  jab reset setup [wiki:Pichu_(SSBM)/Neutral_aerial].
- **Common errors:** Hitting a crouching opponent at low percent and being punished;
  missing the L-cancel; staling nair so much it stops killing.
- **Drill idea:** CPU at a set percent with random DI; count consecutive nairs/uairs that
  connect before the CPU lands or acts.

### Up throw chain grab

- **id:** `uthrow-chaingrab`
- **What:** Uthrow and regrab on fastfallers, ending with usmash.
- **Inputs:** Grab, uthrow, follow the DI (directional influence), regrab; at kill
  percent uthrow then usmash. See [chain-grab](../techniques/chain-grab.md).
- **Timing:** Uthrow is 5% + 5%, angle 90, base knockback 90, growth 45, release on
  frame 20 of 43, identical to Pikachu's [wiki:Pichu_(SSBM)/Up_throw]. Usmash hits frames
  9-11 for 16% at angle 95 (base 50/40, growth 105) [fd]. The wiki says usmash can be
  guaranteed from uthrow on fastfallers at high percent [wiki:Pichu_(SSBM)]. Percent
  window: Unknown from sources read.
- **Used for:** Pichu's most reliable damage and kill on [Fox](fox.md),
  [Falco](falco.md) and [Captain Falcon](captain-falcon.md).
- **Common errors:** Whiffing the short grab after sideways DI; pummelling (1% recoil
  each).
- **Drill idea:** CPU Fox at 0% in grab with random DI; count regrabs; finish with usmash.

### Agility recovery

- **id:** `agility-recovery`
- **What:** Up B (Agility) is two warps like Pikachu's Quick Attack but with no hitbox,
  slower travel, self-damage, and looser rules on the second direction.
- **Inputs:** Up B with a direction held; hold a second direction during the first warp.
- **Timing:** One warp is 68 frames total, two warps 81; the first warp begins after 12
  frames [wiki:Pichu_(SSBM)/Up_special]. Agility "can be used in almost the same
  direction both times" [wiki:Pichu_(SSBM)], unlike Pikachu's 38-degree rule. Costs 1%
  then 3% [wiki:Agility]. The Melee Library card for the momentum-cancel video says both
  Pikachu's and Pichu's up B cancel all knockback momentum on the 14th frame
  [lib:Pikachu/Pichu Up-Special Momentum Cancel].
- **Used for:** Recovery; surviving strong hits by cancelling momentum.
- **Common errors:** Using both warps when one reaches (3% wasted); having no hitbox
  means an opponent on the ledge is never threatened.
- **Drill idea:** Pichu off stage with a ledge-guarding CPU; success on a safe return
  using at most one warp when one is enough.

### Agility landing

- **id:** `agility-landing`
- **What:** Landing from Agility after free fall has begun has almost no lag, so Pichu
  can warp onto the stage or a platform and act immediately.
- **Inputs:** Short hop or jump, up B aimed so the last warp ends just above the ground
  and Pichu enters free fall before touching down; then attack.
- **Timing:** Landing lag is 1 frame after free fall begins and 12 frames before it
  [wiki:Pichu_(SSBM)/Up_special]. (The general Agility page says 14 frames for the failed
  case [wiki:Agility]; the move page's 12 is used here.)
- **Used for:** Movement mixups and fast platform positioning, at 1-4% self damage per
  use.
- **Common errors:** Landing during the warp (12 frames of lag); over-using it and
  racking up recoil.
- **Drill idea:** Target marker on a platform; success if Pichu lands on it from up B and
  performs an attack within N frames of landing.

### Down smash edgeguard

- **id:** `dsmash-edgeguard`
- **What:** Dsmash at the ledge hits on both sides at a low backward angle and is
  intangible while the hitbox starts, beating recovery hitboxes.
- **Inputs:** Stand at the edge, dsmash as the opponent reaches the ledge.
- **Timing:** Hitboxes frames 7-13, 13%, angle 160, base 30, growth 70; intangible frames
  7-10; interruptible from frame 51 [wiki:Pichu_(SSBM)/Down_smash] [fd]. Not electric, so
  no recoil [wiki:Pichu_(SSBM)].
- **Used for:** Gimping recoveries that pass the ledge with a hitbox (Fox and Falco up B,
  Marth up B).
- **Common errors:** Too early: 40 frames of end lag at the ledge.
- **Drill idea:** CPU recovers with up B to the ledge; success if dsmash connects during
  frames 7-10 without Pichu being hit and the CPU dies.

### Forward smash ledge trap

- **id:** `fsmash-ledge-trap`
- **What:** Fsmash is a multi-hit electric jolt whose last hit has very high knockback;
  held low at the ledge it catches fastfallers who fail to sweetspot.
- **Inputs:** Fsmash facing the ledge, timed so the final hit meets the opponent.
- **Timing:** Hits 1-5 on frames 16-30 (2% each), final hit frames 31-33 (6%, base
  knockback 90, growth 140) [wiki:Pichu_(SSBM)/Forward_smash] [fd]. 2% recoil
  [wiki:Recoil_damage]. Opponents can use DI/SDI to leave before the last hit, which
  limits it mostly to edgeguards and jab-reset punishes [wiki:Pichu_(SSBM)/Forward_smash].
- **Used for:** Kills at the ledge on [Fox](fox.md), [Falco](falco.md) and
  [Captain Falcon](captain-falcon.md); punish after a jab reset.
- **Common errors:** Using it in neutral: no protection above or behind.
- **Drill idea:** CPU Falco recovers with side B or up B without a perfect sweetspot;
  success if the final hit connects.

## Neutral game

- Dash dance and wavedash just outside the opponent's range (Pichu's wavedash is short
  [wiki:Pichu_(SSBM)]), then SHFFL nair on a whiff or a commitment.
- Thunder Jolt covers approaches but costs 1% each [wiki:Recoil_damage].
- Dtilt out-ranges ftilt and is the safest poke; ftilt lingers (frames 5-14 [fd]) with no
  recoil [wiki:Pichu_(SSBM)].
- Grab when the opponent shields the nair approach; the grab range is short, so it must
  be point blank.
- Do not trade: Pichu loses almost every trade because of its weight.

## Punish game

Nair and uair strings do most of the damage. Uair is frames 4-9, always angle 80 with
base knockback 100, 4% [fd], so it juggles but does little damage (as low as 2% when
stale [wiki:Pichu_(SSBM)]). Uthrow chain grabs fastfallers; dthrow gives a jab reset or
tech chase on some characters. Kills come from usmash, fsmash at the ledge, nair off
stage and dsmash gimps.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| uthrow | fastfallers | low to mid, typical | regrab | Follow DI | [wiki:Pichu_(SSBM)/Up_throw] |
| uthrow | fastfallers | high | usmash | Kill confirm | [wiki:Pichu_(SSBM)] |
| nair | most | almost any | nair, uair, grab | Loses to crouch cancel at low percent | [wiki:Pichu_(SSBM)] |
| uair | non-floaties | up to high | nair or bair | Sets up an edgeguard at high percent | [wiki:Pichu_(SSBM)/Up_aerial] |
| dthrow | some characters | typical | jab reset or tech chase | Dthrow is 5%+5%, angle 80, base 60, growth 38 | [wiki:Pichu_(SSBM)] [wiki:Pichu_(SSBM)/Down_throw] |
| utilt | most | low | aerial | Slow (frame 7) and short | [wiki:Pichu_(SSBM)] [fd] |
| jab reset | all | Unknown | fsmash or usmash | | [wiki:Pichu_(SSBM)/Forward_smash] |

### Chain grabs and tech chases

Uthrow chain grab on [Fox](fox.md), [Falco](falco.md) and
[Captain Falcon](captain-falcon.md) [wiki:Pichu_(SSBM)/Up_throw]; percent limits Unknown
from sources read (the Melee Library links a video guide [lib:Pichu Melee Chaingrab
Guide] that could not be watched). Uthrow onto a platform and dthrow both create
[tech chase](../techniques/tech-chase.md) situations [wiki:Pichu_(SSBM)].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| usmash (16%) | all | from about 70% | Wiki figure, no DI stated | [wiki:Pichu_(SSBM)] |
| fsmash final hit | all | from about 70% | Near the edge; escapable with DI/SDI | [wiki:Pichu_(SSBM)] |
| dsmash (13%, angle 160) | poor recoveries | any (gimp) | At the ledge | [wiki:Pichu_(SSBM)/Down_smash] |
| nair | all | high | Off stage | [wiki:Pichu_(SSBM)] |
| Skull Bash (fully charged, 39%) | all | very low | Needs up to 181 frames of charge; rarely lands | [wiki:Pichu_(SSBM)] [wiki:Pichu_(SSBM)/Side_special] |
| Thunder (bolt) | some | Unknown | Thunderspike after uair or usmash | [wiki:Pichu_(SSBM)/Up_aerial] |

- Edgeguards: nair off stage repeatedly (Pichu can go deep), dsmash and fsmash at the
  ledge, Thunder Jolt down the wall [wiki:Pichu_(SSBM)].

## Recovery

- **Options:** Agility (two warps, no hitbox, 1% + 3% recoil); Skull Bash (5-39%, 1%
  recoil, charges longer and travels farther than Pikachu's; fully charged it nearly
  crosses Final Destination [wiki:Skull_Bash]); double jump;
  [wall jump](../techniques/wall-jump.md), which Pikachu lacks in Melee
  [wiki:Wall_jump].
- **Mixups:** Warp directions and lengths; second warp nearly parallel to the first;
  landing on stage after free fall begins costs 1 frame of lag
  [wiki:Pichu_(SSBM)/Up_special].
- **Weaknesses:** No hitbox at all on Agility, slower than Quick Attack [wiki:Agility];
  every recovery costs percent; Pichu is light, so any hit off stage sends it far.

### Edgeguarding Pichu

Hold the ledge: Agility cannot hit an edgehogger. If Pichu lands on stage before free
fall it has 12 frames of lag. Any lingering aerial placed on Agility's path wins
outright. Pichu dies so early that simply hitting it off stage twice is usually enough.

## Defense and out of shield

- Out of shield: usmash out of shield is called good by the wiki [wiki:Pichu_(SSBM)];
  nair out of shield is frame 3 after the jump squat [fd].
- Crouch cancel is weak for Pichu because it is the lightest character.
- Escapes: nair, double jump, up B. Tech in place has only 2 vulnerable frames
  [wiki:Tech], but tech rolls are short [wiki:Pichu_(SSBM)].

## As the training dummy

- Lightest character in the game with average fall speed [wiki:Pichu_(SSBM)]; dies
  earliest to almost everything.
- Chain grabbed by [Sheik](sheik.md)'s dthrow [wiki:Chain_grab]; the wiki says
  [Ganondorf](ganondorf.md) has a chain throw on Pichu that can be an infinite or
  zero-to-death [wiki:Pichu_(SSBM)].
- Tech in place is the strong tech option (2 vulnerable frames); tech rolls are short and
  easy to cover.
- Small: some high attacks miss a standing or crouching Pichu [unverified].

## Matchup notes

### vs Fox, Falco, Captain Falcon

These are Pichu's best chances because of the uthrow chain grab and ledge traps, but the
wiki notes Pichu struggles with single moves such as [Fox](fox.md)'s nair
[wiki:Pichu_(SSBM)].

### vs Marth

Much of [Marth](marth.md)'s moveset out-ranges everything Pichu has [wiki:Pichu_(SSBM)].

### vs Sheik and Ganondorf

Both have chain throws on Pichu [wiki:Chain_grab] [wiki:Pichu_(SSBM)].

## Drill seeds

### Nair string

- **id:** `pichu-nair-string`
- **Goal:** Chain SHFFL nairs and uairs with correct L-cancels.
- **Player:** Pichu
- **CPU:** Fox, Falco, Marth, Sheik
- **Setup:** Final Destination, CPU standing at 20-60%, Pichu at dash range.
- **CPU behaviour:** Random DI; attacks or shields as soon as it is actionable.
- **Success:** N hits (start with 3) connect without the CPU acting between them.
- **Fail:** CPU acts or shields; a missed L-cancel (12 frames of landing lag) is flagged.
- **Variations:** CPU crouch cancels at low percent to teach when nair is unsafe.
- **Data needed:** Nair windows, landing lag 12/6, CPU weight and fall speed.

### Up throw chain grab

- **id:** `pichu-uthrow-chaingrab`
- **Goal:** Regrab fastfallers and finish with usmash.
- **Player:** Pichu
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** CPU at 0% already grabbed at centre stage.
- **CPU behaviour:** Random DI; jumps or shines when actionable.
- **Success:** N regrabs then usmash connects.
- **Fail:** Whiffed grab or CPU escapes; any pummel is flagged (1% recoil).
- **Variations:** Start percent; platform stages.
- **Data needed:** Uthrow release 20 / total 43, usmash frame 9, grab range.

### Recoil budget recovery

- **id:** `pichu-recovery-recoil`
- **Goal:** Recover safely using the least recoil.
- **Player:** Pichu
- **CPU:** Marth, Sheik
- **Setup:** Pichu off stage at varied distance with double jump available, 40-80%.
- **CPU behaviour:** Randomly edgehogs or waits on stage with a smash.
- **Success:** Pichu returns unhit; score is lower for each percent of self damage.
- **Fail:** Hit, self-destruct, or 4% taken when a single warp would have reached.
- **Variations:** No double jump; require Skull Bash.
- **Data needed:** Agility distances, recoil values, landing lag 12 vs 1.

### Ledge down smash

- **id:** `pichu-dsmash-edgeguard`
- **Goal:** Time dsmash's intangible frames against an up B at the ledge.
- **Player:** Pichu
- **CPU:** Fox, Falco, Marth
- **Setup:** Pichu at the edge; CPU recovering from below at 30-80%.
- **CPU behaviour:** Up B aimed at the ledge with varied timing.
- **Success:** Dsmash hits and the CPU fails to return; Pichu takes no damage.
- **Fail:** Pichu is hit or dsmash whiffs.
- **Variations:** Replace with fsmash final hit; CPU sweetspots some of the time.
- **Data needed:** Dsmash hit 7-13 and intangibility 7-10, CPU up B hitbox timing.

### Survive as Pichu

- **id:** `pichu-survival-di`
- **Goal:** Practise DI and momentum-cancel up B to live as the lightest character.
- **Player:** Pichu
- **CPU:** Marth, Fox, Sheik
- **Setup:** Pichu at 50-80% near centre; CPU performs a set kill move.
- **CPU behaviour:** One of several kill moves at random.
- **Success:** Pichu survives and recovers.
- **Fail:** Stock lost.
- **Variations:** Percent ramps up after each success.
- **Data needed:** Knockback of the chosen moves on Pichu's weight, up B frame-14
  momentum cancel.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlPc.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/pichu.json`](../framedata/pichu.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 2-3 | 2 | 0 | 7 | 50 | - |  | 21 | - | 2 | -17 |  |
| Dash attack | `dash_attack` | 5-16 | 8 | Sakurai | 40 | 70 | - |  | 49 | - | 5 | -39 |  |
| Forward tilt (angled up) | `ftilt_high` | 5-14 | 9 | Sakurai | 10 | 100 | - |  | 29 | - | 6 | -18 |  |
| Forward tilt | `ftilt` | 5-14 | 8 | Sakurai | 10 | 100 | - |  | 29 | - | 5 | -19 |  |
| Forward tilt (angled down) | `ftilt_low` | 5-14 | 7 | Sakurai | 10 | 100 | - |  | 29 | - | 5 | -19 |  |
| Up tilt | `utilt` | 7-14 | 6 | 95 | 20/25 | 120 | - |  | 23 | - | 4 | -12 |  |
| Down tilt | `dtilt` | 7-9 | 7 | 35 | 12 | 100 | - |  | 21 | 19 | 5 | -6 |  |
| Forward smash | `fsmash` | 16-18, 19-21, 22-24, 25-27, 28-30 | 2 | 0/20/180 | 10 | 50 | - | electric | 49 | - | 2 | -31 | charge hold frame 14; self damage 2% on frame 16 |
|  |  | 31-33 | 6 | Sakurai | 90 | 140 | - | electric |  |  | 4 | -14 |  |
| Up smash | `usmash` | 9-11 | 16 | 95 | 50/40 | 105 | - |  | 43 | 41 | 9 | -22 | charge hold frame 8 |
| Down smash | `dsmash` | 7-13 | 13 | 160 | 30 | 70 | - |  | 54 | 51 | 7 | -36 | charge hold frame 5; intangible 7-10 |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (2 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 3-10 | 12 | Sakurai | 18 | 100 | - |  | 39 | - | 7 | 12 | 6 | <3, >34 | +1 |  |
|  |  | 11-28 | 9 | Sakurai | 0 | 100 | - |  |  |  | 6 |  |  |  | +0 |  |
| Forward air | `fair` | 10-12, 14-16, 18-20, 22-24 | 2 | Sakurai | 0 | 100 | 30 | electric | 39 | - | 2 | 15 | 7 | <10, >33 | -5 | self damage 1% on frame 10, 1% on frame 14, 1% on frame 18, 1% on frame 22 |
| Back air | `bair` | 4-7, 8-37 | 9 | Sakurai | 20 | 100 | - |  | 59 | - | 6 | 18 | 9 | <4, >49 | -3 |  |
| Up air | `uair` | 4-5, 6-7, 8-9 | 4 | 80 | 100 | 60 | - |  | 27 | - | 3 | 18 | 9 | <4, >17 | -6 |  |
| Down air | `dair` | 14-26 | 12 | Sakurai | 20 | 100 | - | electric | 57 | 48 | 7 | 26 | 13 | <1, >38 | -6 | self damage 1% on frame 14 |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 11-12 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 3 | 24 | starts 1 frame late (included); self damage 1% on frame 3 |
| Forward throw | `fthrow` | 10 | 2 | 45 | 45 | 110 | - | electric | 29 | 43 | self damage 1% on frame 10 |
| Back throw | `bthrow` | 9 | 9 | 135 | 75 | 50 | - | electric | 30 | 49 |  |
| Up throw | `uthrow` | 10 | 5 | 90 | 90 | 45 | - | electric | 20 | 43 |  |
| Down throw | `dthrow` | 10 | 5 | 80 | 60 | 38 | - | electric | 20 | 47 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Thunder Jolt, ground | `special_n` | - | - | - | - | - | - | - | 57 | - | - | - | self damage 1% on frame 18 |
| Neutral B: Thunder Jolt, air | `special_air_n` | - | - | - | - | - | - | - | 57 | - | - | - | self damage 1% on frame 18 |
| Side B: Skull Bash, ground, Start | `special_s_start` | - | - | - | - | - | - | - | 13 | - | - | - |  |
| Side B: Skull Bash, ground, Hold | `special_s_hold` | - | - | - | - | - | - | - | 5 | - | - | - |  |
| Side B: Skull Bash, ground | `special_s` | 4-39 | 4 | Sakurai | 15 | 90 | - | electric | 39 | - | 3 | - | self damage 1% on frame 4 |
| Side B: Skull Bash, ground | `special_s_300` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Side B: Skull Bash, ground, End | `special_s_end` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Side B: Skull Bash, air, Start | `special_air_s_start` | - | - | - | - | - | - | - | 13 | - | - | - |  |
| Side B: Skull Bash, air, Hold | `special_air_s_hold` | - | - | - | - | - | - | - | 5 | - | - | - |  |
| Side B: Skull Bash, ground | `special_s_304` | 4-39 | 4 | Sakurai | 15 | 90 | - | electric | 39 | - | 3 | - | self damage 1% on frame 4 |
| Side B: Skull Bash, air, End | `special_air_s_end` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Up B: Agility, ground, Start | `special_hi_start` | - | - | - | - | - | - | - | 13 | - | - | - | self damage 1% on frame 1 |
| Up B: Agility, ground, Start | `special_hi_start_307` | - | - | - | - | - | - | - | 13 | - | - | - | self damage 3% on frame 13 |
| Up B: Agility, ground, End | `special_hi_end` | - | - | - | - | - | - | - | 49 | - | - | - |  |
| Up B: Agility, air, Start | `special_air_hi_start` | - | - | - | - | - | - | - | 13 | - | - | - | self damage 1% on frame 1 |
| Up B: Agility, air, Start | `special_air_hi_start_310` | - | - | - | - | - | - | - | 13 | - | - | - | self damage 3% on frame 13 |
| Up B: Agility, air, End | `special_air_hi_end` | - | - | - | - | - | - | - | 49 | - | - | - |  |
| Down B: Thunder, ground, Start | `special_lw_start` | - | - | - | - | - | - | - | 17 | - | - | - |  |
| Down B: Thunder, ground, Loop | `special_lw_loop` | - | - | - | - | - | - | - | 9 | - | - | - | spawns article/projectile on 3 |
| Down B: Thunder, ground, Loop | `special_lw_loop_314` | 1-9 | 13 | Sakurai | 90 | 60 | - | electric | 9 | - | 7 | - | self damage 3% on frame 1 |
| Down B: Thunder, ground, End | `special_lw_end` | - | - | - | - | - | - | - | 35 | - | - | - |  |
| Down B: Thunder, air, Start | `special_air_lw_start` | - | - | - | - | - | - | - | 17 | - | - | - |  |
| Down B: Thunder, air, Loop | `special_air_lw_loop` | - | - | - | - | - | - | - | 9 | - | - | - | spawns article/projectile on 3 |
| Down B: Thunder, air, Loop | `special_air_lw_loop_318` | 1-9 | 13 | Sakurai | 90 | 60 | - | electric | 9 | - | 7 | - | self damage 3% on frame 1 |
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
| Back air | jump | 7 | `bair` |
| Up air | jump | 7 | `uair` |
| Shield grab | direct | 7 | `grab` |
| Up smash | jump cancel | 10 | `usmash` |
| Forward air | jump | 13 | `fair` |
| Down air | jump | 17 | `dair` |
| Spot dodge | direct | intangible 2-15 of 22 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 15 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Pichu indexed by [The Melee Library](https://www.meleelibrary.com/#pichu) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Pichu Techs Guide](https://www.youtube.com/watch?v=ltTFNDCuGhQ&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=5&t=0s) | Third Chair | Video guide on performing useful Pichu tech in 2020. |
| [Pichu Melee Chaingrab Guide](https://www.youtube.com/watch?v=5COBdQEhQxk&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=3&t=0s) | Third Chair |  |
| [How to Embarrass with Pichu - A Pichu Guide](https://www.youtube.com/watch?v=Q3yexswM15Q) | Mew2King | M2K goes over various aspects of Pichu so you can win some embarrassing money matches. |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Pichu (SSBM): https://www.ssbwiki.com/Pichu_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Pichu_(SSBM)/Neutral_aerial ,
  /Up_aerial , /Up_smash , /Down_smash , /Forward_smash , /Up_throw , /Down_throw ,
  /Up_special , /Side_special
- SSBWiki, Agility: https://www.ssbwiki.com/Agility
- SSBWiki, Skull Bash: https://www.ssbwiki.com/Skull_Bash
- SSBWiki, Recoil damage: https://www.ssbwiki.com/Recoil_damage
- SSBWiki, Tech: https://www.ssbwiki.com/Tech
- SSBWiki, Wall jump: https://www.ssbwiki.com/Wall_jump
- SSBWiki, Chain grab: https://www.ssbwiki.com/Chain_grab
- Melee Library, Pichu and Pikachu sections (card titles and descriptions only; all
  Pichu cards are videos).
- Frame data dump: `Pichu.json`.
