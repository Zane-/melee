---
schema: melee-character/v1
id: marth
name: Marth
aliases: [Mars, Marusu, "the Prince"]
tier: "S (2nd of 26), 2021 PG Stats tier list (13th official NTSC list)"
archetype: [swordie, punish-heavy, edgeguarder, chaingrab, tech-chase, mixup]
related: [roy]
summary: Marth controls the ground with dash dance, down tilt and the longest standing grab, then converts grabs and tipper hits into chain grabs, juggles and edgeguards that end stocks early.
key_tech: [tipper-spacing, dash-dance-grab, uthrow-chaingrab, pivot-tipper-fsmash, ken-combo, dtilt-poke, dolphin-slash-oos, platform-uthrow-tech-chase, side-b-recovery-stall, shield-breaker-edgeguard]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlMs.dat
framedata: ../framedata/marth.json
code: src/melee/ft/kinds/ftMars
specials:
  neutral_b: "Shield Breaker"
  side_b: "Dancing Blade"
  up_b: "Dolphin Slash"
  down_b: "Counter"
attributes:
  weight: 87
  gravity: 0.085
  fall_speed: 2.2
  fast_fall_speed: 2.5
  jump_squat: 4
  jumps: 2
  walk_speed: 1.6
  dash_speed: 1.5
  run_speed: 1.8
  traction: 0.06
  air_speed: 0.9
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [4, 26, 6]
  jab2: [5, 27, 6]
  dash_attack: [12, 40, 12]
  utilt: [6, 32, 13]
  dtilt: [7, 20, 10]
  fsmash: [10, 48, 20]
  usmash: [13, 46, 18]
  dsmash: [5, 62, 16]
  nair: [6, 50, 10]
  fair: [4, 30, 13]
  bair: [7, 35, 13]
  uair: [5, 46, 13]
  dair: [6, 60, 13]
  grab: [7, 31, 0]
  dash_grab: [10, 41, 0]
  pummel: [7, 25, 3]
  fthrow: [null, 32, 4]
  bthrow: [null, 45, 4]
  uthrow: [null, 45, 4]
  dthrow: [null, 43, 5]
  special_n_start: [null, 12, 0]
  special_n_loop: [null, 30, 0]
  special_n_end: [5, 34, 7]
  special_n_end_298: [5, 34, 28]
  special_air_n_start: [null, 12, 0]
  special_air_n_loop: [null, 30, 0]
  special_air_n_end: [5, 34, 7]
  special_air_n_end_302: [5, 34, 28]
  special_s1: [6, 30, 4]
  special_s2_hi: [11, 40, 5]
  special_s2_lw: [13, 40, 5]
  special_s3_hi: [12, 46, 6]
  special_s3_s: [10, 46, 10]
  special_s3_lw: [14, 46, 12]
  special_s4_hi: [19, 50, 10]
  special_s4_s: [22, 50, 14]
  special_s4_lw: [12, 60, 5]
  special_air_s1: [6, 30, 4]
  special_air_s2_hi: [11, 40, 5]
  special_air_s2_lw: [13, 40, 5]
  special_air_s3_hi: [12, 46, 6]
  special_air_s3_s: [10, 46, 10]
  special_air_s3_lw: [14, 46, 12]
  special_air_s4_hi: [19, 50, 10]
  special_air_s4_s: [22, 50, 14]
  special_air_s4_lw: [12, 60, 5]
  special_hi: [5, 40, 13]
  special_air_hi: [5, 40, 13]
  special_lw: [null, 60, 0]
  special_lw_hit: [3, 36, 7]
  special_air_lw: [null, 60, 0]
  special_air_lw_hit: [3, 36, 7]
oos:  # option: frame the hitbox is out
  special_hi: 6
  grab: 7
  fair: 8
  uair: 9
  nair: 10
  dair: 10
  bair: 11
  usmash: 14
resources: 60
# generated: end
---

# Marth

<!-- GENERATED:attributes -->
## Attributes

Read from `PlMs.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 87 |
| Gravity | 0.085 |
| Terminal fall speed | 2.2 |
| Fast-fall speed | 2.5 |
| Jump squat (frames before airborne) | 4 |
| Full hop / short hop initial Y speed | 2.4 / 1.5 |
| Air jump Y multiplier | 0.88 |
| Jumps | 2 |
| Walk max speed | 1.6 |
| Dash initial speed / run max speed | 1.5 / 1.8 |
| Ground friction (traction) | 0.06 |
| Air max horizontal speed | 0.9 |
| Air acceleration (base + stick) | 0.02 + 0.03 |
| Air friction | 0.005 |
| Normal landing lag | 4 |
| Shield size | 11.75 |
<!-- /GENERATED:attributes -->

## Overview

Marth is a sword character whose attacks are disjointed (the sword has a hitbox but no hurtbox)
and whose strongest hitbox on most moves is the tip of the blade, the "tipper". He has a fast
dash, a long [dash dance](../techniques/dash-dance.md), the fourth longest
[wavedash](../techniques/wavedash.md) in the game and the longest non-tether grab
[wiki:Marth_(SSBM)]. He wins neutral by moving just outside the opponent's range, poking with
down tilt, and grabbing whatever the opponent commits. He punishes with throws: up throw chain
grabs on fastfallers (Fox, Falco), up throw juggles on everyone else, and forward/down throw
into [tech chases](../techniques/tech-chase.md) and edgeguards. He kills with tipper forward
smash, the down air spike (a true spike in NTSC, not meteor-cancellable) and edgeguards, but
his safe moves do not kill, so a Marth that misses his setups ends up at high percent with no
reliable finisher ("Marthritis") [wiki:Marth_(SSBM)]. Defensively he is weak: his
[out of shield](../techniques/out-of-shield.md) options are slow or very risky, his recovery is
short and linear, and Fox can waveshine him because NTSC Marth (weight 87) is not knocked down
by shine [wiki:Marth_(SSBM)]. Entry-level execution is low, but optimal punishes (pivot
tippers, DI-reactive chain grabs) are among the hardest in the game.

## Strengths and weaknesses

- **Strengths:**
  - Range and disjoint on every normal; tipper hitboxes reward exact spacing.
  - Longest standing grab of the non-tether grabs; dash dance grab is the core neutral threat
    [wiki:Marth_(SSBM)/Grab].
  - Down tilt: hits frame 7, interruptible from frame 20 of 49 [fd], long, low and hard to
    punish when spaced.
  - Up throw chain grab on Fox and Falco that leads to a kill or edgeguard from 0% on Final
    Destination [lib:Marth Chaingrab Charts].
  - Down air is a spike (290° launch angle on the tip, cannot be meteor cancelled in NTSC)
    [wiki:Marth_(SSBM)/Down_aerial].
  - Edgeguarding: forward smash, down tilt, back air, forward air walls, Shield Breaker,
    counter, ledge-hop down air.
- **Weaknesses:**
  - Poor finishers at high percent; tipper smashes and up B are committal and hard to land in
    neutral [wiki:Marth_(SSBM)].
  - Sweetspots have the *lowest* hitbox priority on most moves: if a non-tip hitbox also
    overlaps the target on that frame, the weak hit wins (down air and up B are the
    exceptions) [wiki:Marth_(SSBM), wiki:Marth_(SSBM)/Down_aerial, wiki:Dolphin_Slash].
  - Weak out of shield: moves swing in short arcs with high end lag.
  - Short, predictable recovery; up B is easily edgehogged and loses to the "Marth killer"
    light shield at the ledge [wiki:Dolphin_Slash].
  - Standing grab whiffs on some crouching characters, most notoriously Jigglypuff
    [wiki:Marth_(SSBM)/Grab].
  - Combo food for Fox (waveshine, up throw up air), Falco (pillars), Sheik (down throw) and
    Captain Falcon.

## Character tech

### Tipper spacing

- **id:** `tipper-spacing`
- **What:** Hitting with the hitbox at the tip of the sword, which does more damage and
  knockback than the rest of the blade. Example: forward smash is 20% with base knockback 80
  at the tip versus 14% with base knockback 60 elsewhere, both with knockback growth 70 [fd].
- **Inputs:** Any sword normal, spaced so only the outermost hitbox overlaps the opponent's
  hurtbox on the first active frame that connects.
- **Timing:** The tip hitbox has the lowest priority on most moves, so being one step too
  close gives the weak hit [wiki:Marth_(SSBM)]. Forward smash is active frames 10-13,
  interruptible from frame 48 [fd]. Up smash's "tipper" (18%) sits at the middle of the blade,
  not the end [wiki:Marth_(SSBM)].
- **Used for:** Kills (tipper fsmash kills "reliably under 100%" and sometimes under 75%
  [wiki:Marth_(SSBM)/Forward_smash]); combo starters at range (tipper fair launches at 67°
  instead of the Sakurai angle [fd]); safety on shield.
- **Common errors:** Standing too close (non-tip hit, opponent survives and may punish the
  end lag); whiffing because the target moved back; hitting a crouching target with the blade.
- **Drill idea:** CPU stands still at a random distance inside Marth's fsmash range; success
  only if the hit that connects is the 20% hitbox.

### Dash dance grab

- **id:** `dash-dance-grab`
- **What:** Weaving in and out of the opponent's range with dash dance, then punishing a
  whiffed attack, shield or landing with a [jump-cancelled](../techniques/jump-cancel.md)
  standing grab.
- **Inputs:** Dash away / dash toward repeatedly; when the opponent commits, dash in, press
  jump and Z (or shield+A) so the jump squat is cancelled into a standing grab.
- **Timing:** Standing grab is active frames 7-8, 30 frames total; dash grab is active frames
  10-11, 40 frames total, and reaches less far forward [wiki:Marth_(SSBM)/Grab]. (The frame
  data dump lists 6-7 and 9-10 [fd]; the two sources differ by one frame.) JC grab is therefore
  both faster and longer than dash grab.
- **Used for:** Marth's main neutral win condition in almost every matchup; "the neutral game
  for Marth centers completely around downtilt and grab" versus Sheik [lib:Marth vs. Sheik
  Guide].
- **Common errors:** Getting a dash grab (missed jump cancel); dash dancing with no room behind
  (keep at least one wavedash length from the ledge [lib:Marth Guide]); grabbing a crouching
  Jigglypuff and whiffing.
- **Drill idea:** CPU approaches with a randomly timed committal attack (Fox running nair, Sheik
  dash attack, Falcon nair) or stays back; success if Marth takes no hit and lands a standing
  grab within N frames of the CPU's attack ending.

### Up throw chain grab on fastfallers

- **id:** `uthrow-chaingrab`
- **What:** Up throw, then regrab Fox or Falco before they can act, repeated until the percent
  is high enough for an up air or up tilt into tipper fsmash. See
  [chain grab](../techniques/chain-grab.md).
- **Inputs:** Grab, up throw, read the DI (directional influence: the victim holds a direction
  to bend the launch angle), then: no movement + regrab; turn + regrab; dash + JC grab; or
  pivot + regrab, depending on where they fall.
- **Timing:** Up throw launches at 93° with base knockback 60 and growth 130; release is on
  frame 12 of 44 for a baseline-weight victim (earlier for lighter victims)
  [wiki:Marth_(SSBM)/Up_throw]. The player in the higher controller port gets one extra frame
  of leniency because the victim's throw hitstun starts a frame later
  [lib:Marth Chaingrab Charts].
- **Used for:** 0-to-death or 0-to-edgeguard on Fox and Falco on Final Destination; shorter
  versions under platforms. Percent windows are in "Chain grabs and tech chases" below.
- **Common errors:** Regrabbing too late (victim jumps or shines out); using up tilt at mid
  percent (victim escapes by DI behind Marth [lib:Marth Chaingrab Charts]); missing the pivot
  on no-DI and grabbing air.
- **Drill idea:** CPU Fox/Falco starts grabbed at a chosen percent and picks DI at random from
  {none, full left, full right, slight toward}; success if Marth regrabs (or lands the chart's
  listed follow-up) before the CPU's first actionable frame.

### Pivot tipper forward smash

- **id:** `pivot-tipper-fsmash`
- **What:** A [pivot](../techniques/pivot.md) (cancelling a dash's turnaround into standing)
  straight into forward smash, used to put Marth at exact tipper distance facing the right way
  after a throw or up air.
- **Inputs:** Dash past or away from the falling opponent, flick the stick the other way and
  input fsmash (C-stick) on the turn frame.
- **Timing:** The pivot window in Melee is 1 frame, but the stick does not need to return to
  neutral if the pivot is immediately cancelled into fsmash [wiki:Pivot]. Fsmash hits frames
  10-13 [fd].
- **Used for:** Killing floaties off throws (forward throw into pivot fsmash on Jigglypuff
  [wiki:Pivot]; PewPewU and Zain made this the standard Jigglypuff kill
  [wiki:Marth_(SSBM)]); finishing the spacie chain grab when they DI to the side (pivot fsmash
  on full DI at 80-85% on Fox [lib:Marth Chaingrab Charts]). Working percent on Jigglypuff:
  roughly 50-70% from forward throw [unverified].
- **Common errors:** Dash instead of pivot (Marth runs past); fsmash faces the wrong way;
  correct direction but non-tip hit.
- **Drill idea:** CPU Jigglypuff starts grabbed at 55-70% with random DI on forward throw;
  success if the tipper fsmash connects before she can jump or air dodge.

### Ken combo

- **id:** `ken-combo`
- **What:** Forward air into a double-jump down air spike, usually near or past the ledge.
  Named after Ken [wiki:Ken_Combo].
- **Inputs:** Jump, fair (tip), double jump, dair. A "jumpless" version skips the double jump;
  a "reverse" version uses fair's rear hitbox; up B (reversed) can replace dair
  [wiki:Ken_Combo, wiki:Dolphin_Slash].
- **Timing:** Fair hits frames 4-7 and is interruptible from frame 30; dair hits frames 6-9
  [fd]. Against fastfallers the tipper fair must hit from below so they pop up and fall into
  the dair; against floaties the fair must hit from above so they are not sent out of reach.
  There is a percent window: too low and fair gives too little knockback, too high and the
  Sakurai-angle hitboxes start launching at 45° and send them away [wiki:Ken_Combo].
- **Used for:** Ending stocks at mid percent; the tipper dair "can KO reliably even as low as
  40%" offstage [wiki:Marth_(SSBM)]. On Fox, a dair that sends him offstage works from about
  23-115% on side DI after up throw [lib:Marth Chaingrab Charts].
- **Common errors:** Opponent DIs the fair away and escapes (every fair in a combo is a DI
  mixup [lib:Marth Chaingrab Charts]); dair hits with the non-tip hitbox (sends up at 80°
  [fd]); Marth dairs too low offstage and cannot recover (dair has 59 total frames [fd]).
- **Drill idea:** CPU starts in hitstun above the ledge at 40-80%, DI toward or neutral;
  success if dair's 13% hitbox lands and the CPU is KO'd off the bottom.

### Down tilt poke

- **id:** `dtilt-poke`
- **What:** Down tilt used as a low-commitment poke from a run cancel (crouch out of run) or
  wavedash, then acting again immediately.
- **Inputs:** Run, hold down to crouch, down+A; or wavedash, down+A. Follow with dash back,
  another dtilt, or dash grab.
- **Timing:** Hits frames 7-9, interruptible from frame 20 of 49 [fd]. It cannot be interrupted
  with shield, so Marth cannot block immediately after it
  [wiki:Marth_(SSBM)/Down_tilt]. Launch angle 30° (a semi-spike) with low growth (40) [fd].
- **Used for:** Stopping grounded approaches and dash dances; edgeguarding (pokes below the
  ledge and sends at a low angle); setting up grabs below roughly 100% [wiki:Marth_(SSBM)].
  "Marth's best poke is by far dtilt" [lib:Marth Guide].
- **Common errors:** Using it against an opponent who is jumping (it only covers the ground);
  being [crouch cancelled](../techniques/crouch-cancel.md) at low percent and grabbed;
  repeating the same dtilt timing.
- **Drill idea:** CPU dash dances at the edge of dtilt range and randomly dashes in; success if
  the dtilt tip hits and Marth is actionable (IASA) before the CPU can retaliate.

### Dolphin Slash out of shield

- **id:** `dolphin-slash-oos`
- **What:** Up B (Dolphin Slash) jump-cancelled out of shield as Marth's fastest punish.
- **Inputs:** While in shield (after shieldstun ends), press up+B; the jump squat is cancelled
  into up B. Optionally hold backward to reverse it.
- **Timing:** Up B hits on frame 5 and Marth is intangible on that frame only; out of shield it
  hits on frame 6 because of one frame of jump squat, one frame faster than shield grab
  [wiki:Dolphin_Slash]. Clean hit is frame 5 only (13% tip, base knockback 80; 10% inner);
  frames 6-11 are a weak late hit (6-7%) [fd]. Marth reverses only if the stick is held
  backward between frames 5 and 6 [wiki:Marth_(SSBM)/Up_special]. Landing lag is 34 frames
  [wiki:Dolphin_Slash].
- **Used for:** Punishing pressure with small gaps (works on spacie nairs "really, really
  well" [lib:Marth Guide]); reversing shield pressure at kill percent; a replacement for grab
  on whiff punishes at high percent.
- **Common errors:** Whiff or late hit, then a full punish during the fall and 34 frames of
  landing lag; facing the ledge and falling to death without the reverse.
- **Drill idea:** CPU Fox does a late nair on Marth's shield then shines; success if Marth's
  up B clean hit lands in the gap; fail if Marth is hit or lands the weak hit.

### Platform up throw tech chase

- **id:** `platform-uthrow-tech-chase`
- **What:** Up throwing a fastfaller so they land on a platform, then covering every tech
  option from below.
- **Inputs:** Under a platform: up throw, then short hop up air if in range, or double jump
  back air, or wait below and react with up tilt / fsmash / regrab.
- **Timing:** Tech in place lasts 26 frames and tech rolls 40 frames for every character
  [lib:Tech Chasing!]. At low percent on platform stages, up throw then short-hop up air when
  in range, otherwise double-jump bair covers all platform options [lib:Marth Guide]. Until
  around 60%, the victim can use slide-off DI to escape Marth's up air / fair platform hits
  [wiki:Tech-chase].
- **Used for:** Converting grabs on Yoshi's Story, Battlefield, Pokémon Stadium where the chain
  grab is interrupted by platforms.
- **Common errors:** Swinging before the tech choice is visible; hitting with a non-tip up air
  so they slide off; missing a tech-in-place shine from Fox/Falco.
- **Drill idea:** CPU Fox thrown onto a Battlefield side platform at 20-50% with random tech
  (in place, left, right, miss); success if Marth hits or regrabs before the CPU acts.

### Side B recovery stall

- **id:** `side-b-recovery-stall`
- **What:** Using the first hit of side B (Dancing Blade) in the air to slow Marth's fall and
  gain horizontal distance before up B.
- **Inputs:** Offstage, press side+B once (do not continue the sequence), drift toward the
  stage, then double jump and/or up B.
- **Timing:** The first swing "has pseudo-jump properties" and lowers falling speed even on
  repeat uses [wiki:Marth_(SSBM)/Side_special]; hitbox frames 6-8, 29 frames total [fd].
- **Used for:** Extending a recovery that would fall short; changing recovery timing so the
  edgeguarder mistimes.
- **Common errors:** Pressing B twice (second swing, more lag); using it too low and having no
  height left for up B.
- **Drill idea:** Marth starts offstage at a distance that plain double jump + up B cannot
  cover; success if he grabs the ledge.

### Shield Breaker edgeguard

- **id:** `shield-breaker-edgeguard`
- **What:** Neutral B (Shield Breaker), an overhead arc with a large hitbox, used at the ledge
  or in the air to cover recoveries.
- **Inputs:** Hold B to charge, release to swing; uncharged tap swings quickly.
- **Timing:** Uncharged damage 7%, full charge 28% [fd]; a full charge breaks any shield unless
  it is [powershielded](../techniques/powershield.md) [wiki:Shield_Breaker].
- **Used for:** Covering Jigglypuff and Peach drifting near the ledge (it either hits or forces
  them to weave uncomfortably far [lib:Marth Guide]); extending aerial combos past normal
  aerial reach; platform tech chases [wiki:Shield_Breaker].
- **Common errors:** Charging too long and being hit; using it where fsmash or dtilt would be
  safer.
- **Drill idea:** CPU Jigglypuff drifts back toward the ledge at fair-spacing distance; success
  if Shield Breaker hits before she lands or grabs the ledge.

## Neutral game

- **Goal:** Stay grounded, hold center, keep the opponent at the tip of dtilt/grab range, and
  punish their commitment with a grab. Marth "should commit as little as possible from
  neutral" and use movement, not swings, to create openings [lib:Marth Guide].
- **Dash dance:** Start from just outside the opponent's largest attack range and weave in and
  out; dash in = pressure, dash back = bait [lib:Marth Guide].
- **Wavedash back:** Gives up little stage and still threatens grab, tilts and fsmash in front
  [lib:Marth Guide].
- **Down tilt:** Primary poke (see tech above).
- **Forward air:** Fastest aerial (frame 4) with 7 frames of L-cancelled landing lag [fd]. Best
  used late and retreating/defensively; it swings top-down, so Marth's lower front is exposed
  until the blade comes down [lib:Sharpening Your Sword: Tai's Marth Guide].
- **Neutral air:** Two hits (frames 6-7 and 15-21 [fd]), auto-cancels from frame 25
  [wiki:Marth_(SSBM)/Neutral_aerial]. Good as a fade-back wall against tall characters and for
  swatting Peach's turnips [lib:Marth Guide]; a poor approach against Fox, Falco and Sheik.
- **Jab:** Low-commitment spacing tool, especially out of wavedash [wiki:Marth_(SSBM)].
- **Forward smash in neutral:** Only safe when the opponent is airborne, being tech chased, or
  shielding on a platform [lib:Marth vs. Sheik Guide].
- **Dash attack:** High risk; mostly a hard punish on a retreating or landing opponent.

## Punish game

Almost every large punish starts from a grab. Up throw is the default against fastfallers and
most mid-weights; forward throw and down throw set up tech chases and put the opponent offstage;
back throw is a positional or DI-trap throw. Throw speed depends on the victim's weight: heavier
victims make Marth's throw animation slower, which wastes throw hitstun, so follow-ups are
tighter on heavy characters [lib:Sharpening Your Sword: Tai's Marth Guide]. Prefer guaranteed
follow-ups (regrab, up air, fsmash) over DI mixups (up tilt, fair) when one exists
[lib:Marth Chaingrab Charts].

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| uthrow | Fox | 0-17% pre-throw | regrab (any DI) | Final Destination, tested from port 1 | [lib:Marth Chaingrab Charts] |
| uthrow | Fox | 18-46% | pivot regrab (no DI), dash regrab (full DI), pivot regrab (slight toward DI) | chain grab on no DI ends at 46% for the lower port | [lib:Marth Chaingrab Charts] |
| uthrow | Fox | 47-64% | rising tipper uair → regrab or fsmash | pivot uair → regrab on no DI is very hard at 47-55% | [lib:Marth Chaingrab Charts] |
| uthrow | Fox | 65-79% | falling soft (non-tip) uair → regrab, or rising tipper uair → fsmash | | [lib:Marth Chaingrab Charts] |
| uthrow | Fox | 80-85% | fsmash; pivot fsmash on full DI | | [lib:Marth Chaingrab Charts] |
| uthrow | Fox | 95-120% | nair (no DI), fair (full DI), nair or tipper bair (slight toward) | at 121-140% only nair (no DI) and tipper bair (slight toward) remain | [lib:Marth Chaingrab Charts] |
| uthrow | Falco | 0-24% | regrab; at 0-6% DI toward escapes into a tech chase | must dash grab side DI from 14% | [lib:Marth Chaingrab Charts] |
| uthrow | Falco | 25-55% | pivot regrab (no DI) / dash regrab (full DI) | windows run about 5-6% higher than Fox up to 80% | [lib:Marth Chaingrab Charts] |
| uthrow | Falco | 90-105% | falling soft uair → fsmash; fsmash direct up to about 103% on no DI | pivot/wavedash fsmash on side DI up to about 110% | [lib:Marth Chaingrab Charts] |
| fthrow | Captain Falcon | 8-26% | reaction tech chase | uthrow options here all have an escape DI | [lib:Marth Chaingrab Charts] |
| uthrow | Captain Falcon | 27-35% | regrab (no DI), utilt (away DI), turn utilt (toward DI) | Falcon combos are mostly DI mixups | [lib:Marth Chaingrab Charts] |
| uthrow | Captain Falcon | 54-76% | on DI toward or away: mixup of fair (beats DI toward / survival DI) vs fsmash or pivot fsmash (beats DI away) | toward DI at 54-63% still allows fair or regrab | [lib:Marth Chaingrab Charts] |
| fthrow at 0% | Sheik | 0% | regrab → pummel once → uthrow → utilt | Sheik escapes fthrow by DI down and away; uthrow → utilt works until about 25% | [lib:Marth vs. Sheik Guide] |
| uthrow | Sheik | about 18-21% | utilt | "a gamble"; otherwise short hop and react: uair if she falls, double-jump uair if she jumps | [lib:Marth Guide] |
| fthrow / dthrow | Sheik | any | tech chase: dtilt or fsmash a missed tech, dash dance regrab a tech | carries her to the ledge | [lib:Marth vs. Sheik Guide] |
| fthrow | Jigglypuff | roughly 50-70% | pivot tipper fsmash | DI dependent; percent range not sourced | [wiki:Pivot], range [unverified] |
| fthrow / dthrow | Jigglypuff | 0 to about 20% | regrab | depends on DI | [wiki:Chain_grab] |
| side B first hit | floaties (Peach, Jigglypuff, Samus) | KO percent | utilt (tipper kills from about 130%) | utilt is Marth's main KO move on floaties | [wiki:Marth_(SSBM)/Up_tilt, wiki:Marth_(SSBM)] |
| dtilt | most | below about 100% | dash grab | not guaranteed; depends on reaction | [wiki:Marth_(SSBM)] |
| fair (tip) | most | mid percent, near ledge | double jump dair (Ken combo) | DI away on the fair escapes | [wiki:Ken_Combo] |
| missed Rest | Jigglypuff | low percent | dair, then throw combo | about 40% total | [lib:Sharpening Your Sword: Tai's Marth Guide] |

### Chain grabs and tech chases

- **Fox and Falco (up throw).** Works from 0%. On Final Destination Marth should chain grab
  Fox to around 60%, using utilt/uair into another grab only when the DI makes a direct regrab
  impossible in roughly the 33-60% range [lib:Sharpening Your Sword: Tai's Marth Guide]. Exact
  windows from the Signia chart (percent before the throw, port 1, FD): Fox regrab 0-17% any
  DI; 18-46% regrab with a pivot (no DI) or dash (full DI); direct chain grab ends at 46% on
  no DI, 52% on DI away, 61% on DI toward. Falco's windows are about 5-6% higher, and Falco
  can escape at 0-6% by DI toward (Marth then tech chases) [lib:Marth Chaingrab Charts].
  SSBWiki summarises it as "0% to about 60%" [wiki:Chain_grab].
- **What breaks it:** platforms (the victim lands and techs); alternating DI each throw to make
  Marth mis-position; slight DI variants that sit between "turn" and "dash" regrabs; SDI on
  utilt/uair; and DI toward center stage on every grab so the final fsmash sends across the
  whole stage ("cross-stage fsmash") [lib:Marth Chaingrab Charts].
- **Captain Falcon.** No true chain grab. 0-7%: no throw gives a strong follow-up (fthrow does
  not knock down). 8-26%: forward throw reaction tech chase. From 27%: up throw into
  regrab/utilt/fair/fsmash mixups by DI [lib:Marth Chaingrab Charts]. Up throw combos under
  about 45% are unreliable, so platform and ground tech chases matter
  [lib:Sharpening Your Sword: Tai's Marth Guide].
- **Sheik.** Forward throw → regrab at 0%, then tech chase with fthrow/dthrow toward the ledge
  [lib:Marth vs. Sheik Guide]. Sheik's tech in place and tech toward look the same for too long
  to react to, so chasing her needs a read or a move that covers both [wiki:Tech-chase].
- **Reaction tech chase basics:** react by about frame 18-19 of the tech; tech in place is 26
  frames, rolls 40; Marth covers rolls with dash → JC grab [lib:Tech Chasing!]. Fsmash and
  dair are the read options. Against tech-in-place shine from spacies: grab earlier, cover it
  with nair, or run up and shield grab [lib:Marth Guide].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| fsmash (tipper) | most | under 100%; under 75% "in certain situations" | near ledge, bad DI lowers it; 20%, base 80, growth 70 | [wiki:Marth_(SSBM)/Forward_smash], [fd] |
| fsmash (non-tip) | most | struggles to KO from center under 150% | 14%, base 60 | [wiki:Marth_(SSBM)/Forward_smash] |
| dair (tip, spike) | any offstage | from about 40% | must hit the 13% tip hitbox; opponent offstage | [wiki:Marth_(SSBM)] |
| utilt (tipper) | floaties | 130%+ | clean hit, 13%, launches at 85° | [wiki:Marth_(SSBM)] |
| up B (clean tip) | Mario | about 80% at the edge of FD, 130-140% from center, no DI | frame 5 only | [wiki:Dolphin_Slash] |
| dsmash (tipper) | most | high percent, off the top | 16%, launches at 70°, growth 100 | [fd], [wiki:Marth_(SSBM)] |
| side B 3rd hit forward | most | around 120% | | [wiki:Marth_(SSBM)] |
| side B 4th hit forward | most | under 100% | hard to land all four | [wiki:Marth_(SSBM)] |
| uthrow | most | "extremely high percents" | third strongest up throw per the character page | [wiki:Marth_(SSBM)] |

- **Edgeguards are the main kill method.** Dtilt at the ledge (semi-spike), jab to stop linear
  recoveries (first jab) and shortened Fox/Falco side B (second jab), fsmash on a recovery that
  lands on stage, back air offstage, counter against recoveries with hitboxes, ledge-hop dair
  [wiki:Marth_(SSBM), wiki:Marth_(SSBM)/Down_aerial].
- **Fox/Falco up B:** the charge-up is long enough to hit with up B, fair, or dair; the first
  hit of side B gimps low up B start-ups [wiki:Marth_(SSBM), wiki:Marth_(SSBM)/Up_special].
  Grabbing the ledge and choosing between ledge-hop aerial, get-up and roll covers the angles.
- **Ledge get-up attack edgehog:** timed well, Marth's fast ledge attack can push a recovering
  Fox off the lip while he is helpless [wiki:Marth_(SSBM)].
- **Throw near the ledge:** forward throw / down throw at the edge puts fastfallers offstage
  below the ledge for dtilt or dair. Against good players forward throw off the edge is "a
  coin-toss", because they can DI into the ledge, double jump air dodge in, or stall
  [lib:Marth Guide].
- **Sheik:** force her to up B onto the stage and tipper her landing; stand up from the ledge
  (not roll or attack) right after her vanish to deny the sweetspot
  [lib:Marth vs. Sheik Guide].

## Recovery

- **Options:** double jump; side B first swing (stalls fall, adds horizontal distance); up B
  (fast, frame 5 hitbox, intangible on frame 5 only, good vertical and poor horizontal
  distance, can be angled slightly and reversed) [wiki:Dolphin_Slash]; air dodge to ledge;
  counter (down B) against an edgeguarder's hitbox; fair/bair to hit an edgeguarder who comes
  out.
- **Mixups:** recover high with double jump and aerial versus low with up B; delay with side B;
  sweetspot the ledge with up B so the hitbox ends just as he grabs (up B can grab the ledge
  from frame 23 [wiki:Dolphin_Slash]); up B through the stage lip to hit someone standing at
  the edge; reverse up B from under the stage.
- **Weaknesses:** little horizontal travel, so a Marth hit far offstage low is usually dead; up
  B is edgehogged easily (a ledge roll beats it consistently) [wiki:Dolphin_Slash]; 34 frames
  of landing lag if forced onstage; side B stalls are slow and hittable.

### Edgeguarding Marth

- **Edgehog:** grab the ledge as he up Bs. If he is forced to land onstage he has 34 frames of
  landing lag [wiki:Dolphin_Slash]: roll or get-up from the ledge and punish with a smash.
- **Marth killer:** stand at the ledge and hold a light shield angled away from the stage; the
  late hit of up B hits the shield and the push slides the defender onto the ledge, which
  edgehogs him [wiki:Dolphin_Slash]. As Marth, the answers are to sweetspot (so no hitbox
  reaches the shield) or to stall and change timing.
- **Hit the double jump:** Marth must usually jump before up B; hitting him out of the jump
  (Sheik fair/bair, Fox bair/shine, Falco dair, Peach nair/dsmash at the ledge, Jigglypuff
  bair) leaves only a short up B.
- **Intercept side B:** the stall has no protection below or behind; go out and hit it.
- **Respect the up B hitbox:** standing unshielded at the lip loses to up B through the stage.
- A CPU Marth should mix: (a) double jump high then fair/air dodge, (b) fall low and up B
  sweetspot, (c) side B once then up B, (d) up B early to hit an opponent on the ledge.

## Defense and out of shield

- **Out of shield:** up B (frame 6 OoS, hugely punishable on whiff) [wiki:Dolphin_Slash];
  shield grab (grab frame 7, long range) [wiki:Marth_(SSBM)/Grab]; wavedash out of shield
  (4-frame jump squat [wiki:Marth_(SSBM)] plus 10 frames of landing lag
  [web:docs.google.com Collection of Sheik Stuff]); short hop fair/nair/dair OoS (dair covers
  cross-ups [wiki:Marth_(SSBM)/Down_aerial]). The standing advice is "get out of shield as
  fast as possible" [lib:Marth Guide].
- **What beats his shield:** well-spaced or crossed-up pressure with gaps under 6 frames (Fox
  and Falco shine pressure), late aerials into grab, and anything that pins him on a platform.
- **Crouch cancel / [ASDI](../techniques/asdi.md) down:** useful at low percent against Sheik
  ("CC a lot" [lib:Marth Guide]), Fox nair and Peach; CC into dtilt or grab is the standard
  counter-hit.
- **Combo escapes:** no fast "get off me" move. Options are DI, SDI, double jump, fair (often
  comes out before Falco can follow a laser hit in the air [lib:Marth Guide]), air dodge, and
  counter (active from frame 5 [wiki:Roy_(SSBM)]) as a read.
- **Versus lasers:** crouch or dash-away powershield; low lasers have a 1-frame powershield
  window for Marth [lib:Marth Guide].
- **On the ledge:** haxdash/ledgedash give partial intangibility [wiki:Ledge_stall]; his
  100%+ ledge attack is slow and one of the most punishable [wiki:Marth_(SSBM)].

## As the training dummy

- **Class:** weight 87, fall speed 2.2 (fast fall 2.5), gravity 0.085, jump squat 4 frames
  [wiki:Marth_(SSBM)]. Mid-weight, medium-fast faller, tall.
- **Fox:** NTSC Marth is not knocked down by shine, so Fox can waveshine into grab, up smash or
  more shines [wiki:Marth_(SSBM)]. Fox up throw → up air is escaped by DI behind Fox then
  smash DI the first hit of up air the opposite way [lib:Marth Guide].
- **Sheik down throw (NTSC):** full DI away is regrabbable until about 80%; slight DI away at
  the 45° notch is regrabbable without a dash until 27% after the throw; no DI / DI behind
  gives utilt at low percent then full-jump rising uair from about 20% after the throw; at 78%
  before the hit a tipper up smash kills on FD even with survival DI. The DIs a realistic CPU
  Marth should choose from are: away, slight away, none, behind
  [lib:Doing Bad Stuff To Marth 101].
- **Jab reset / forced get-up:** after Sheik's jab or needles on a downed Marth, he must do a
  normal stand below 39% post-hit; at or above that he may also roll or get-up attack
  [web:docs.google.com Collection of Sheik Stuff].
- **Recovery behaviour:** see "Edgeguarding Marth". A realistic CPU sweetspots up B and
  sometimes side B stalls.
- **Tech choices:** tech away from Marth-ditto and Sheik grabs toward center; tech in place is
  strong only if the chaser is out of position, since Marth has no fast get-up option.

## Matchup notes

### vs Fox

- Marth wants a grab: on FD it is a chain grab into kill or edgeguard; on platform stages it is
  up throw platform tech chases. Bait Fox's nair with dash dance and pivot grab the landing; if
  the nair would overshoot, rising bair or a retreating fsmash [lib:Marth Guide].
- Dtilt works as a mixup that takes the ground back when Fox dash dances; it loses to jumps
  [lib:Marth Guide].
- Fox wins by shield pressure (Marth's OoS is slow), waveshine conversions, up throw up air,
  and running away/laser when ahead. Edgeguard Fox with dtilt, jab, fsmash, dair and ledge
  options; he dies early offstage.

### vs Falco

- Lasers control Marth's ground game. Stay grounded, powershield by crouching or dashing away,
  and punish "bad lasers" fired too close; dash attack when Falco starts a laser; shield grab
  after a ledge-hop double laser [lib:Marth Guide].
- Falco's retreating movement is poor against Marth; pin him at the ledge. Throwing Falco
  offstage is favourable: waiting for double-jump dair or air dodge is safe and he has few
  options from the ledge [lib:Marth Guide].
- Chain grab works like Fox's but about 5-6% later, and Falco can be pivot fsmashed and up B'd
  at higher percents [lib:Marth Chaingrab Charts].

### vs Sheik

- Historically Marth's hard matchup because of NTSC down throw and Sheik's edgeguards. The
  plan: stay on the ground, dtilt and dash dance grab; avoid approaching fair, dash attack and
  nair; never get grabbed [lib:Marth vs. Sheik Guide].
- Marth's grab range shuts down Sheik's jab pressure; fsmash cannot be crouch cancelled even at
  0% [lib:Marth vs. Sheik Guide].
- Wavedash out of shield when she short hops; she lacks the air mobility to follow
  [lib:Marth vs. Sheik Guide].
- Sheik can crouch cancel any Marth aerial that is not a tipper, then dtilt or dash attack
  [web:docs.google.com Collection of Sheik Stuff]; space aerials at the tip or stay grounded. Grab the ledge when she is offstage; dtilt a lot
  [lib:Marth Guide].

### vs Jigglypuff

- Crouching Puff ducks standing grab [wiki:Marth_(SSBM)/Grab]. Kill with throw → pivot tipper
  fsmash [wiki:Marth_(SSBM)]. Stay under her, count jumps, keep moving; poke the ledge with
  dtilt; ftilt is often safer than fsmash; Shield Breaker catches her spacing outside fair
  range [lib:Marth Guide].
- Rest punishes Marth's laggy whiffs and up B.

### vs Peach

- Dash dance just outside her dash attack range; run-up grab or dtilt when she pulls a turnip.
  Nair through thrown turnips. Do not swing while moving into a grounded Peach who can down
  smash [lib:Marth Guide]. Her float-cancelled aerials have only 4 frames of landing lag, so
  cover what she does next rather than punishing the landing
  [lib:Sharpening Your Sword: Tai's Marth Guide].

### vs Captain Falcon

- Both combo each other hard. Falcon up throw combos are unreliable under about 45%, so tech
  chases carry the low-percent punish [lib:Sharpening Your Sword: Tai's Marth Guide]. Falcon's
  recovery is very exposed to fsmash, dtilt and up B.

## Drill seeds

### Chain grab Fox by DI

- **id:** `marth-uthrow-chaingrab-fox`
- **Goal:** Learn the regrab type for each DI and percent band.
- **Player:** Marth
- **CPU:** Fox (variant: Falco)
- **Setup:** Final Destination, center stage. Marth holds Fox in grab at a chosen percent
  (default 0%). Marth is in the higher port if available.
- **CPU behaviour:** On each throw the CPU picks DI at random from {none, full away, full
  behind, slight toward}; it jumps or shines on its first actionable frame.
- **Success:** N consecutive regrabs (default: carry Fox from 0% to 46%+), each landing before
  Fox acts.
- **Fail:** Fox touches the ground actionable, jumps away, or hits Marth.
- **Variations:** Start at 18% (pivot regrabs), 47% (uair → regrab), 65% (soft uair → regrab),
  80% (fsmash / pivot fsmash finisher must be a tipper); Falco with windows about 5-6% later;
  fixed DI to isolate one branch.
- **Data needed:** Marth uthrow release frame per victim weight and launch (93°, base 60,
  growth 130), Fox/Falco weight, gravity, fall speed, hitstun formula, Marth grab frame 7 and
  JC grab timing, the percent table in [lib:Marth Chaingrab Charts].

### Up throw to tipper finisher

- **id:** `marth-uthrow-finisher`
- **Goal:** End the chain grab correctly: up air into tipper fsmash, or direct fsmash, by DI.
- **Player:** Marth
- **CPU:** Fox, Falco
- **Setup:** FD, Fox in grab at 60-85% (random), random distance from the ledge.
- **CPU behaviour:** Random DI on the throw; survival DI (up and toward the stage) on the
  finisher; tech randomly if it lands.
- **Success:** A 20% tipper fsmash connects, or Fox is KO'd, before Fox acts.
- **Fail:** Non-tip fsmash, whiff, or Fox escapes.
- **Variations:** Require pivot fsmash on full DI at 80-85%; allow dair when it would send Fox
  offstage (works about 23-115% on side DI [lib:Marth Chaingrab Charts]).
- **Data needed:** fsmash hit frames 10-13 and hitbox positions; uair hit frames 5-8 and
  landing lag 15/7 [fd]; Fox fall speed.

### Pivot tipper on Jigglypuff

- **id:** `marth-pivot-tipper-puff`
- **Goal:** Kill a floaty from a throw with a pivot tipper fsmash.
- **Player:** Marth
- **CPU:** Jigglypuff (variants: Peach, Samus)
- **Setup:** Any stage, Marth holding Jigglypuff in grab at 50-70% near center.
- **CPU behaviour:** Random DI on forward throw (away, toward, down-away); jumps or air dodges
  on the first actionable frame.
- **Success:** The 20% fsmash hitbox lands; bonus if it KOs.
- **Fail:** Non-tip hit, whiff, or Puff acts first.
- **Variations:** Up throw instead of forward throw; lower percent with down throw; stage
  position near the ledge so the tipper kills earlier.
- **Data needed:** fthrow launch (50°, base 70, growth 45) and release frame 14 of 31 baseline
  [wiki:Marth_(SSBM)/Forward_throw]; Jigglypuff weight and air mobility; exact percent window
  is not sourced and must be measured.

### Dash dance whiff punish

- **id:** `marth-dd-grab-whiff-punish`
- **Goal:** Stay out of range, then JC grab the opponent's commitment.
- **Player:** Marth
- **CPU:** Fox, Sheik, Captain Falcon, Peach
- **Setup:** FD, both at 0%, about one Marth dash-dance length apart, Marth with room behind.
- **CPU behaviour:** After a random delay the CPU does one approach: Fox running short-hop
  nair or drill; Sheik dash attack or boost grab; Falcon running nair or dash grab; Peach dash
  attack. Sometimes it fakes (dash in, dash back).
- **Success:** Marth takes no damage and lands a standing grab within about 20 frames of the
  CPU's move ending or landing.
- **Fail:** Marth is hit or grabbed, shields the attack (no punish), or gets a dash grab.
- **Variations:** Require a follow-up throw combo; shrink the stage room behind Marth; add
  Falco lasers before the approach.
- **Data needed:** CPU approach move ranges and landing lag; Marth dash/run speed and
  initial-dash length; grab frames.

### Ken combo at the ledge

- **id:** `marth-ken-combo-ledge`
- **Goal:** Convert a tipper fair into a dair spike.
- **Player:** Marth
- **CPU:** Fox, Falco, Sheik, Captain Falcon, Marth
- **Setup:** Yoshi's Story or Battlefield, CPU standing near the ledge at 40-70%, Marth a short
  hop away facing it.
- **CPU behaviour:** Stands or shields briefly, then is hit; DI on the fair is random between
  toward/neutral (combo works) and away (combo should be abandoned for an edgeguard).
- **Success:** Dair's 13% hitbox hits and the CPU is KO'd; or, on DI away, Marth grabs the
  ledge / lands a follow-up edgeguard hit instead of whiffing dair.
- **Fail:** Dair whiffs, non-tip dair, or Marth self-destructs.
- **Variations:** Replace dair with reverse up B; start from a forward throw instead of a raw
  fair; fastfaller vs floaty spacing (fair from below vs from above).
- **Data needed:** fair hit frames 4-7 / IASA 30, dair hit frames 6-9, tip angle 290°, Marth
  double jump height 25.188 [wiki:Marth_(SSBM)], Sakurai-angle threshold.

### Edgeguard Fox's up B

- **id:** `marth-edgeguard-fox`
- **Goal:** Cover Fox's recovery options from the ledge and from the stage.
- **Player:** Marth
- **CPU:** Fox (variant: Falco)
- **Setup:** FD or Battlefield. Fox starts offstage in tumble at 30-80%, at a random
  height/distance, with his double jump available at random. Marth stands near the ledge.
- **CPU behaviour:** Random choice: side B to ledge, side B onto stage, shortened side B, up B
  at a random angle (to ledge, high onto stage, into the wall for a wall tech), double jump
  air dodge onto stage.
- **Success:** Fox loses the stock without Marth taking a hit.
- **Fail:** Fox lands on stage or the ledge and becomes actionable, or hits Marth.
- **Variations:** Force stage-only answers (dtilt, jab, fsmash, counter) or ledge-only
  answers; give Fox random [amsah tech](../techniques/amsah-tech.md) / wall tech on hit.
- **Data needed:** Fox side B and up B distances and start-up; Marth dtilt/jab/fsmash reach
  below the ledge; ledge intangibility frames.

### Up B out of shield versus spacie pressure

- **id:** `marth-upb-oos`
- **Goal:** Find the gap in aerial → shine pressure and punish with a clean up B.
- **Player:** Marth
- **CPU:** Fox, Falco
- **Setup:** Marth shielding center stage at any percent; CPU at 60-100% (kill range).
- **CPU behaviour:** Short hop nair or dair on shield at a random height (late = small gap,
  early = large gap), then shine, then repeats or grabs.
- **Success:** Marth's frame-5 clean hit (10% or 13%) connects.
- **Fail:** Marth is hit, grabbed, or lands only the late 6-7% hit.
- **Variations:** Allow shield grab and wavedash OoS as alternative successes; CPU sometimes
  crosses up (requires reverse up B, stick back on frames 5-6).
- **Data needed:** shield stun per damage (floor((damage + 4.45) / 2.235)
  [web:docs.google.com Collection of Sheik Stuff]), Fox/Falco aerial landing lag and shine
  frame, Marth jump squat.

### Tech chase Sheik to the ledge

- **id:** `marth-tech-chase-sheik`
- **Goal:** Keep control after forward/down throw and finish at the ledge.
- **Player:** Marth
- **CPU:** Sheik (variants: Captain Falcon, Marth)
- **Setup:** FD, Sheik in grab at 20-60%, random stage position.
- **CPU behaviour:** Random DI on the throw; random tech (in place, toward, away, missed); on a
  missed tech random get-up (stand, roll, attack). After teching she spot dodges or jabs.
- **Success:** Regrab, dtilt/fsmash on a missed tech, or tipper fsmash on a read; repeat until
  Sheik is offstage.
- **Fail:** Sheik becomes actionable and escapes or hits Marth.
- **Variations:** Platform version after back throw at mid percent; Falcon at 8-26% with
  forward throw (the chart's tech chase band).
- **Data needed:** tech durations (in place 26, roll 40 frames [lib:Tech Chasing!]), Sheik
  tech roll distances, Marth fthrow/dthrow release frames for weight 90.

### Recover against an edgehog

- **id:** `marth-recovery-sweetspot`
- **Goal:** Mix recovery timing and sweetspot the ledge.
- **Player:** Marth
- **CPU:** Sheik, Fox, Marth
- **Setup:** Marth offstage in tumble at a random position that is recoverable, double jump
  available.
- **CPU behaviour:** Randomly: grabs the ledge and rolls on reaction to up B; stands at the lip
  with the "Marth killer" light shield; comes offstage with a bair/fair at the double jump.
- **Success:** Marth reaches the ledge or stage and is actionable without being hit.
- **Fail:** Marth is KO'd or hit during landing lag.
- **Variations:** No double jump; start below ledge height (reverse up B from under the
  stage).
- **Data needed:** up B travel distances and ledge-grab frame 23 [wiki:Dolphin_Slash]; side B
  stall physics; ledge occupancy rules.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlMs.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/marth.json`](../framedata/marth.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 4-7 | 4/6 | Sakurai | 20/30 | 50/60 | - | slash | 27 | 26 | 4 | -17 |  |
| Jab 2 | `jab2` | 5-9 | 4/6 | Sakurai | 20/30 | 50/60 | - | slash | 28 | 27 | 4 | -17 | starts 1 frame late (included) |
| Dash attack | `dash_attack` | 12-15 | 11/9/12 | 110/Sakurai | 70/35 | 55/60 | - | slash | 49 | 40 | 7 | -20 |  |
| Up tilt | `utilt` | 6-8 | 9/8/12 | 110/Sakurai | 40/50 | 120/118/116/100 | - | slash | 39 | 32 | 7 | -18 |  |
|  |  | 9-12 | 10/9/13 | 85/Sakurai | 40/30/50 | 120/118/116/100 | - | slash |  |  | 7 | -15 |  |
| Down tilt | `dtilt` | 7-9 | 9/8/10 | 30 | 40/25/20/50 | 40 | - | slash | 49 | 20 | 6 | -6 |  |
| Forward smash | `fsmash` | 10-13 | 14/20 | Sakurai | 60/80 | 70 | - | slash | 49 | 48 | 10 | -27 | charge hold frame 3 |
| Up smash | `usmash` | 13-16 | 8/15/18 | 70/90 | 0/30/60 | 100/80 | 100/0 | slash | 54 | 46 | 10 | -22 | charge hold frame 7 |
| Down smash | `dsmash` | 5-7 | 11/16 | 75/Sakurai/70 | 70/20/16 | 72/100 | - | slash | 64 | 62 | 9 | -47 | charge hold frame 3 |
|  |  | 20-22 | 11/16 | 75/Sakurai | 70/30/15 | 72/100 | - | slash |  |  | 9 | -32 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 6-7 | 4 | 100/90 | 30 | 40 | - | slash | 49 | - | 3 | 15 | 7 | <6, >24 | -4 |  |
|  |  | 15-21 | 10 | Sakurai | 50 | 80 | - | slash |  |  | 6 |  |  |  | -1 |  |
| Forward air | `fair` | 4-7 | 10/9/13 | Sakurai/67 | 30/20/42 | 70 | - | slash | 33 | 30 | 7 | 15 | 7 | <1, >26 | +0 |  |
| Back air | `bair` | 7-11 | 10/9/13 | Sakurai | 30/25/10 | 70 | - | slash | 39 | 35 | 7 | 24 | 12 | <1, >31 | -5 |  |
| Up air | `uair` | 5-8 | 13/10/9 | 90/80 | 40/30/20/18 | 70 | - | slash | 45 | - | 7 | 15 | 7 | <5, >26 | +0 |  |
| Down air | `dair` | 6-9 | 13/10/9 | 290/80/Sakurai | 40/30/20 | 70 | - | slash | 59 | - | 7 | 32 | 16 | <6, >47 | -9 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 10-11 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 7 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 4 | 4 | 50 | 70 | 45 | - | - | 14 | 31 |  |
| Back throw | `bthrow` | 4 | 4 | 117 | 70 | 60 | - | - | 7 | 44 |  |
| Up throw | `uthrow` | 4 | 4 | 93 | 60 | 130 | - | - | 12 | 44 |  |
| Down throw | `dthrow` | 5 | 5 | 135 | 65 | 50 | - | - | 14 | 42 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Shield Breaker, ground, Start | `special_n_start` | - | - | - | - | - | - | - | 11 | - | - | - |  |
| Neutral B: Shield Breaker, ground, Loop | `special_n_loop` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Neutral B: Shield Breaker, ground, End | `special_n_end` | 5-10 | 7 | Sakurai | 30/34/40 | 100 | - | slash | 33 | - | 5 | - |  |
| Neutral B: Shield Breaker, ground, End | `special_n_end_298` | 5-10 | 28 | Sakurai | 30/34/40 | 100 | - | slash | 33 | - | 14 | - |  |
| Neutral B: Shield Breaker, air, Start | `special_air_n_start` | - | - | - | - | - | - | - | 11 | - | - | - |  |
| Neutral B: Shield Breaker, air, Loop | `special_air_n_loop` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Neutral B: Shield Breaker, air, End | `special_air_n_end` | 5-10 | 7 | Sakurai | 30/34/40 | 100 | - | slash | 33 | - | 5 | - |  |
| Neutral B: Shield Breaker, air, End | `special_air_n_end_302` | 5-10 | 28 | Sakurai | 30/34/40 | 100 | - | slash | 33 | - | 14 | - |  |
| Side B: Dancing Blade, ground, 1 | `special_s1` | 6-8 | 4 | 85/96/80/76 | 55 | 25 | - | slash | 29 | - | 3 | - |  |
| Side B: Dancing Blade, ground, 2Hi | `special_s2_hi` | 11-14 | 5 | 90/85/79 | 30/60/70/85 | 40 | - | slash | 39 | - | 4 | - |  |
| Side B: Dancing Blade, ground, 2Lw | `special_s2_lw` | 13-15 | 5 | 105/80/70/50 | 16 | 100 | - | slash | 39 | - | 4 | - |  |
| Side B: Dancing Blade, ground, 3Hi | `special_s3_hi` | 12-16 | 6 | 80 | 60 | 60 | - | slash | 45 | - | 4 | - |  |
| Side B: Dancing Blade, ground, 3S | `special_s3_s` | 10-13 | 10 | Sakurai | 0 | 160 | - | slash | 45 | - | 6 | - |  |
| Side B: Dancing Blade, ground, 3Lw | `special_s3_lw` | 14-17 | 12 | 270 | 50 | 100 | - | slash | 45 | - | 7 | - |  |
| Side B: Dancing Blade, ground, 4Hi | `special_s4_hi` | 19-24 | 10 | 80 | 40 | 130 | - | slash | 49 | - | 6 | - |  |
| Side B: Dancing Blade, ground, 4S | `special_s4_s` | 22-25 | 14 | Sakurai | 15 | 120 | - | slash | 49 | - | 8 | - |  |
| Side B: Dancing Blade, ground, 4Lw | `special_s4_lw` | 12-14, 18-20, 24-26, 30-32 | 3 | 80 | 2 | 40 | - | slash | 59 | - | 3 | - |  |
|  |  | 36-37 | 5 | Sakurai | 20 | 130 | - | slash |  |  | 4 | - |  |
| Side B: Dancing Blade, air, 1 | `special_air_s1` | 6-8 | 4 | 85/96/80/76 | 55 | 25 | - | slash | 29 | - | 3 | - |  |
| Side B: Dancing Blade, air, 2Hi | `special_air_s2_hi` | 11-14 | 5 | 90/85/79 | 30/60/70/85 | 40 | - | slash | 39 | - | 4 | - |  |
| Side B: Dancing Blade, air, 2Lw | `special_air_s2_lw` | 13-15 | 5 | 105/80/70/50 | 16 | 100 | - | slash | 39 | - | 4 | - |  |
| Side B: Dancing Blade, air, 3Hi | `special_air_s3_hi` | 12-16 | 6 | 80 | 60 | 60 | - | slash | 45 | - | 4 | - |  |
| Side B: Dancing Blade, air, 3S | `special_air_s3_s` | 10-13 | 10 | Sakurai | 0 | 160 | - | slash | 45 | - | 6 | - |  |
| Side B: Dancing Blade, air, 3Lw | `special_air_s3_lw` | 14-17 | 12 | 270 | 50 | 100 | - | slash | 45 | - | 7 | - |  |
| Side B: Dancing Blade, air, 4Hi | `special_air_s4_hi` | 19-24 | 10 | 80 | 40 | 130 | - | slash | 49 | - | 6 | - |  |
| Side B: Dancing Blade, air, 4S | `special_air_s4_s` | 22-25 | 14 | Sakurai | 15 | 120 | - | slash | 49 | - | 8 | - |  |
| Side B: Dancing Blade, air, 4Lw | `special_air_s4_lw` | 12-14, 18-20, 24-26, 30-32 | 3 | 80 | 2 | 40 | - | slash | 59 | - | 3 | - |  |
|  |  | 36-37 | 5 | Sakurai | 20 | 130 | - | slash |  |  | 4 | - |  |
| Up B: Dolphin Slash, ground | `special_hi` | 5 | 13/10 | Sakurai/74 | 80/60 | 70 | - | slash | 39 | - | 7 | - | intangible 5 |
|  |  | 6-10 | 7/6 | Sakurai/74 | 20 | 90 | - | slash |  |  | 5 | - |  |
| Up B: Dolphin Slash, air | `special_air_hi` | 5 | 13/10 | Sakurai/74 | 80/60 | 70 | - | slash | 39 | - | 7 | - | intangible 5 |
|  |  | 6-10 | 7/6 | Sakurai/74 | 20 | 90 | - | slash |  |  | 5 | - |  |
| Down B: Counter, ground | `special_lw` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Down B: Counter, ground, Hit | `special_lw_hit` | 3-9 | 7 | Sakurai | 90 | 35 | - | slash | 35 | - | 5 | - | intangible 1-5 |
| Down B: Counter, air | `special_air_lw` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Down B: Counter, air, Hit | `special_air_lw_hit` | 3-9 | 7 | Sakurai | 90 | 35 | - | slash | 35 | - | 5 | - | intangible 1-5 |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-18 | - | 27 | 25 |  |
| Roll forward | `roll_forward` | intangible 4-19 | - | 35 | - |  |
| Roll backward | `roll_backward` | intangible 4-23 | - | 35 | - |  |
| Air dodge | `airdodge` | intangible 4-29 | - | 49 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-22 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-31 | 20-23, 30-31 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 6-19 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-19 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-22 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-28 | 22-23, 27-28 (6%) | 49 | - |  |
| Getup roll forward (face down) | `getup_roll_forward_facedown` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-19 | - | 35 | - |  |
| Tech in place | `tech_in_place` | intangible 2-20 | - | 26 | - | starts 1 frame late (included) |
| Tech roll forward | `tech_roll_forward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Tech roll backward | `tech_roll_backward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Wall tech | `wall_tech` | - | - | 26 | - | starts 1 frame late (included) |
| Wall tech jump | `wall_tech_jump` | - | - | 40 | - | starts 1 frame late (included) |
| Ceiling tech | `ceiling_tech` | intangible 2-13 | - | 26 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-55 | - | 58 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 32 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-34 | 38-41 (8/6%) | 68 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-20 | 24-27 (8/6%) | 54 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-56 | - | 78 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-38 | - | 48 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-18 | - | 18 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 39 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-11 | - | 11 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 39 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Up B | jump cancel | 6 | `special_hi` |
| Shield grab | direct | 7 | `grab` |
| Forward air | jump | 8 | `fair` |
| Up air | jump | 9 | `uair` |
| Neutral air | jump | 10 | `nair` |
| Down air | jump | 10 | `dair` |
| Back air | jump | 11 | `bair` |
| Up smash | jump cancel | 14 | `usmash` |
| Spot dodge | direct | intangible 2-18 of 27 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 35 | `roll_forward` |
| Roll backward | direct | intangible 4-23 of 35 | `roll_backward` |
| Wavedash | jump | actionable on frame 16 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Marth indexed by [The Melee Library](https://www.meleelibrary.com/#marth) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [Marth: Prince of Altea](http://melee.guru/characters/marth.html) | STT_PureDrop | A website pefectly designed to be your guide to learning everything about Marth. |
| [2020 Marth Melee Techs Guide](https://www.youtube.com/watch?v=vtwLwYbP_mg&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=26&t=0s) | Third Chair | Video guide on performing useful Marth tech in 2020. |
| [Are You a Marth Player?](https://www.youtube.com/watch?v=IiVzSzuuv88) | SSBM Tutorials | They give an overview of Marth the character to give you an idea of whether you would like to play him. |
| [Marth Guide](https://docs.google.com/document/d/1Daf_Dqod1HoMj7L26ITeUM-xKUKhfxh2vJLWOl2N0C8/edit?pli=1) | Mookie Rah | A compilation of smart things said by good Marth players. Includes general Marth tips and theory, as well as matchup notes. Most info is pre-2014. |
| [Matchup Guides](http://smashboards.com/threads/compilation-of-matchup-guides.341532/) | Beat | These guides are pretty simple. In his words, “They're mainly aimed at players who struggle with a matchup and need a good starting point.” This also includes a very detailed flowchart to chaingrab Fox to death on FD (this was probably written for PAL Fox, but most of it still applies). |
| [Detailed Chaingrab Information](http://smashboards.com/threads/detailled-chaingrab-information.323364/) | lots of people | Compilation of information from various Marth players. None of it is tested so some info may be inaccurate. It is a place to start. I have found Beat’s chaingrab flowchart above to be pretty effective even in NTSC. |
| [Sharpening Your Sword: Tai’s Marth Guide](http://www.meleeitonme.com/sharpening-your-sword-tais-marth-guide/) | Tai | A guide on how to play Marth. This guide is unique from the rest in its emphasis on explaining the fundamentals. Even players who do not play Marth could learn a lot from this guide. Tai also discusses each of Marth’s moves and how they are useful, or not. At the end, he gives a few matchup tips. |
| [Marth vs. Sheik Guide](http://www.meleeitonme.com/guest-article-marth-vs-sheik-guide/) | Neighborhood P | Neighborhood P discusses the Marth vs. Sheik matchup. |
| [Perfect Marth Class—Advanced Frame Data Application](http://smashboards.com/threads/kadanos-perfect-marth-class-advanced-frame-data-application.337035/) | Kadano | Kadano applies intensive frame data analysis to optimize Marth play. Most of the information is indexed in the main post, but the second post, below the indexing, also includes more information that is not indexed. |
| [Marth Hitboxes and Frame Data](http://smashboards.com/threads/complete-marth-hitboxes-and-frame-data.285324/) | Stratocaster, Standardtoaster, and SuperDoodleMan | Includes gifs of all of Marth’s moves showing hitboxes and hurtboxes. Also lists frame data on each move. |
| [Marth Frame Data Visualization](http://i.imgur.com/KYtUPyO.png) | RZR |  |
| [List of Important Marth Tech to Practice](http://smashboards.com/threads/technical-things.283211/#post-10954335) | The Crimson Blur | Crimson Blur lists 21 things Marth players should practice. |
| [Marth Trials](https://www.youtube.com/watch?v=_IACW5mltqY) | Ripple | A video demonstrating and explaining essential Marth tech. |
| [PewPewUniversity](https://www.youtube.com/playlist?list=PL0vnsPOq4FD37x4d_yhRfS9yrziqCWGQ4) | PewPewU | A series of videos demonstrating various techniques and their applications. |
| [Pivoting Tutorial](https://www.youtube.com/watch?v=JyYC19ciM20) | Arc | A video explaining how to pivot with Marth and some applications. |
| [Marth Tutorial](https://www.youtube.com/watch?v=PFCQIAnYUMM) | Ken | Ken talks about how to play Marth. |
| [Super Easy Marth Tech Skill Fundamentals Tutorial](https://www.youtube.com/watch?v=cmcfXVQvE9E) | Ken | Ken talks some more about how to play Marth. |
| [Marth Tutorial](https://www.youtube.com/watch?v=AexiFPr6x84) | Overswarm | A very old video about how to play Marth. |
| [739 Mew2king Edgeguards with Marth](https://www.youtube.com/watch?v=s63pPeyWasw) | Ben Burdett | A compilation video of Mew2king edgeguarding with Marth. I suggest putting on your favorite music or Pandora station and watching these attentively. Get a feel for how Mew2king edgeguards. You can also learn a lot using situational analysis by creating flowcharts of the options Mew2king has and the opponent has and then analyzing the options they choose to do in each situation. |
| [Marth Neutral Game Tutorial](https://www.youtube.com/watch?v=vkI8krzFrro) | SSBM Tutorials |  |
| [Marth Edgeguarding Fox Tutorial Part 1 [Part 2](https://www.youtube.com/watch?v=z4CBle2C3Qs)](https://www.youtube.com/watch?v=8LoaduZZTA8) | SSBM Tutorials |  |
| [Marth Movement & Tips](https://www.youtube.com/watch?v=O-dqZ93qG44) | The Moon | The Moon talks about movement with Marth and general tips. |
| [Marth’s Haxdash, Easiest Execution](http://gfycat.com/GrippingEverlastingArthropods) | Kadano | Gfycat of invincible haxdash with Marth. Use the frame advance options to see inputs and breakdown. Kadano also includes a breakdown in his Perfect Marth Class thread. |
| [Dreamland Glitch](http://smashboards.com/threads/marth-trips-over-himself-on-dreamland-64.97797/page-2#post-2183026) | Magus | Some of Marth’s moves sometimes [do not come out](https://www.youtube.com/watch?v=zBpHylGW00s) on Dreamland. It’s dumb. |
| [Boost Grab, Jump Cancelled Grab, and Dash Grab Comparison](http://i.imgur.com/xMh4jQE.png) | Kadano |  |
| [SSBM Training Tips](https://www.youtube.com/playlist?list=PL3Z01NXawoQceMjbPnuegbh4C_ECzAKOZ) | Ippo | Playlist of videos created by Ippo about things you can practice on your own. Mostly Marth, but there are some other characters in there, too. |
| [Smash Practice with PPMD, Zhu, and Cactuar Parts 1, [2](https://www.youtube.com/watch?v=z9ybib14CkU&feature=youtu.be), [3](https://www.youtube.com/watch?v=8ZGdcLXj4mY&feature=youtu.be), [4](https://www.youtube.com/watch?v=qXXy7XenFAU&feature=youtu.be), [5](https://www.youtube.com/watch?v=EYeVL78xLCA&feature=youtu.be), and [6](https://www.youtube.com/watch?v=oXfu2wSLDvM&feature=youtu.be)](https://www.youtube.com/watch?v=UyY4VzQxG78) |  |  |
| [How I Train by Myself](https://www.youtube.com/watch?v=LRnhBYquweA) | PewPewU |  |
| [Marth’s Angled Up-B](http://smashboards.com/threads/marths-angled-up-b.413141/) | Sycorax | Sycorax explains how you can angle Marth's Up-B vertically. |
| [Mew2king Shares a Marth Secret](https://www.youtube.com/watch?v=ClUYBhuHoqQ) | Mew2king | A useful tool against Fox's Up-B recovery on stage. |
| [Edgeguarding Fox with Marth](https://www.reddit.com/r/SSBM/comments/3grvlv/edgeguarding_fox_as_marth/) | Poi830 | A simple flowchart that covers most of Fox’s recovery options in most situations. |
| [Marth’s Invincible Ledgedash Options](https://www.youtube.com/watch?v=SPV1ocOcZYA) | Practical TAS | A video showcasing Marth’s options he can perform intangibly from a ledgedash. |
| [DownSmash vs Sheik Tutorial](https://www.youtube.com/watch?v=WVNWvZDZOPk) | SSBM Tutorials | A little bit of jank for techchasing Sheik. |
| [Marth Discussion Thread](http://smashboards.com/threads/official-ask-dr-ppmd-about-cactuars-stuff-thread.118998/page-380#post-18278271) | community | A huge long thread of people talking about Marth. Use the search function to find what you want. Most of the good stuff has been compiled in Mookie Rah’s google doc. |
| [Chaingrab on Spacies Tutorial](https://www.youtube.com/watch?v=HSEcRDiOSqk) | SSBM Tutorials | A simple flowchart to chaingrabbing Fox and Falco. This flowchart is not perfect but should get you most of the way against most spacie players. |
| [Marth’s On-stage Edgeguard Options and How Low They Go](http://imgur.com/a/bl0hW) | ??? |  |
| [Zero to Hero Season 2](https://www.youtube.com/playlist?list=PLGC_XHknYHa6yMba4RqgVZvSDsvK6eH5n) | Tafokints | Tafokints teaches Marth to Van. |
| [Some discussion about dtilt](https://www.reddit.com/r/SSBM/comments/3w1say/daily_discussion_thread_120915/cxsogto?sort=confidence) | 24095827059827502984 |  |
| [Double Stick DI’ing out of Marth’s Platform Combos](http://smashboards.com/threads/double-stick-di-out-of-marths-platform-combos.403279/) | tauKhan |  |
| [How to Practice Marth](https://www.youtube.com/watch?v=NB29clCzTcM) | SSBM Tutorials |  |
| [Marth Shielddrop Options](https://www.youtube.com/watch?v=4Jiyl-_Ky_8) | PewPewU |  |
| [Marth Moonwalk](https://www.youtube.com/watch?v=kRN-DA3Wn78) | PewPewU |  |
| [Using Crouch Cancel to Tech Chase with Marth](http://smashboards.com/threads/guide-marth-cc-to-techchase-missed-tech.435135) | xXadevs2000Xx |  |
| [How to Edgeguard Marth: Part 1, [Part 2](https://www.youtube.com/watch?v=ZwfOAlS3Au0)](https://www.youtube.com/watch?v=vDSYxMRuqOQ) | SSBM Tutorials |  |
| [Wavedash turnaround D tilt Art Class](https://www.youtube.com/watch?v=0OqI1qEPhoU) | PewPewU |  |
| [Leffen vs PPMD @ Apex '15 Analysis](https://www.youtube.com/watch?v=4gVzWoYPQ_w) | ZoSo |  |
| [Marth Side-B Recovery Mechanics](http://smashboards.com/threads/marth-side-b-recovery-mechanics.437735/) | Sycorax |  |
| [Useful No Impact Lands as Marth](https://www.youtube.com/watch?v=TTfZrZ2GZq8) | Zaheer's Air Scooter |  |
| [How to Edgeguard Pikachu](https://smashboards.com/threads/how-to-edgeguard-pikachu.440636/) | Sycorax |  |
| [Step Pivot Forward Smash - Applications for Marth](https://www.youtube.com/watch?v=-Ic2HC37wdY) | RCJ Smash | You can cancel the first 3 frames of dash into a fsmash and this video explains uses for that. |
| [Marth Tutorials](https://www.youtube.com/playlist?list=PLOzYxSEpTNXqVkzJNiEBExSjb24goBlMq) | Zephirex | A playlist of videos showing movement options, attack options, ledge options, how to Ken combo, how to chaingrab, and how to use third hit down side-b meteor. |
| [ASDI Down Marth Killer](https://www.reddit.com/r/SSBM/comments/5vejw1/asdi_down_marth_killer/) | Quetzalcoatl |  |
| Marth Chaingrab Charts | Signia | A set of flowcharts outlining a robust set of options after uthrowing fastfallers. [Fox](https://marthnerd.blogspot.com/2017/03/marths-uthrow-combos-on-fox-and-falco.html) [Falco](https://marthnerd.blogspot.com/2017/03/marth-uthrow-combo-table-and-flowchart.html) [Captain Falcon](https://marthnerd.blogspot.com/2017/03/marth-uthrow-combo-table-for-falcon.html) |
| [Marth Melee Chaingrab Guide](https://www.youtube.com/watch?v=4yKPucXDopc&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=17&t=0s) | Third Chair | Another Marth chaingrab guide. Marth has one of the most complicated chaingrab flowcharts and this video doest a mostly good job of covering it all. Always know that because of several Melee mechanics, it is hard to be 100% accurate about this topic. |
| [How to Beat Marth](https://www.youtube.com/watch?v=Z-Btw2WMleg) | SSBM Tutorials |  |
| [Marth vs. Jigglypuff tips and tricks](https://www.youtube.com/watch?v=HYCoA6cgwTw) | Arc | Tricks to use in the matchup. Most importantly, conditioning drift in order to land safe grabs. The throw combos are better explained in Kadano's thread. The bthrow combos are not real. |
| [The 'TRUE' Sweetspot](https://www.youtube.com/watch?v=6C-rfAOJPjU) | PewPewU | Combining horizontal and vertical sweetspot. |
| [The Basics of Marth's Dancing Blade](https://www.youtube.com/watch?v=mFYJM6eQjQw) | SSBM Tutorials and Ken |  |
| [General Marth Guide](https://www.youtube.com/watch?v=bIm6oEMR5Ik) | PPMD | Marth master, PPMD, gives a guide on how to play Marth. He covers Marth's moveset's special properties such as tipper hitboxes, arcing attacks, lingering attackes, and disjoint. He uses these properties to construct a strategy for Marth to be played as a zoning character and goes into depth on what that means exactly. |
| [New Marth Ledge Tech: DJB (Double Jump Bonk) up to GALINT 18](https://www.reddit.com/r/SSBM/comments/b8mprp/new_marth_ledge_tech_djb_double_jump_bonk_up_to/) | Schmooblidon | An advanced technique to get more ledge intangibility as Marth. |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Marth (SSBM): https://www.ssbwiki.com/Marth_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Marth_(SSBM)/Up_throw ,
  /Forward_throw , /Forward_smash , /Forward_aerial , /Down_aerial , /Down_tilt , /Up_tilt ,
  /Neutral_aerial , /Grab , /Up_special , /Side_special
- SSBWiki technique pages: https://www.ssbwiki.com/Ken_Combo , /Tipper , /Chain_grab ,
  /Tech-chase , /Pivot , /Dolphin_Slash , /Dancing_Blade , /Shield_Breaker , /Counter ,
  /Ledgestall , /List_of_SSBM_tier_lists_(NTSC) , /Roy_(SSBM) (Marth comparison values)
- Signia, "Marth's uthrow combos on Fox and Falco" (Melee Library card "Marth Chaingrab
  Charts"): https://marthnerd.blogspot.com/2017/03/marths-uthrow-combos-on-fox-and-falco.html
- Signia, Falco table: https://marthnerd.blogspot.com/2017/03/marth-uthrow-combo-table-and-flowchart.html
- Signia, Captain Falcon table: https://marthnerd.blogspot.com/2017/03/marth-uthrow-combo-table-for-falcon.html
- MookieRah's Marth Q&A Compilation Guide (card "Marth Guide"):
  https://docs.google.com/document/d/1Daf_Dqod1HoMj7L26ITeUM-xKUKhfxh2vJLWOl2N0C8/
- Tai, "Sharpening Your Sword: Tai's Marth Guide" (via web.archive.org):
  http://www.meleeitonme.com/sharpening-your-sword-tais-marth-guide/
- Neighborhood P, "Marth vs. Sheik Guide" (via web.archive.org):
  http://www.meleeitonme.com/guest-article-marth-vs-sheik-guide/
- DruggedFox, "Tech Chasing!": http://portraitinsmash.blogspot.ca/2015/09/tech-chasing.html
- DruggedFox, "Doing Bad Stuff To Marth 101":
  https://portraitinsmash.blogspot.com/2015/02/doing-bad-stuff-to-marth-101.html
- "Collection of Sheik Stuff" (Tero, KirbyKaze, Magus and others):
  https://docs.google.com/document/d/1mlNwPWxO2y8u_w1t_jf_FzMx6OC8BJyFZ2fW-rOj9zk/
- Frame data dump: `Marth.json`
- Not reachable this session (403 or login wall): smashboards threads (Kadano's Perfect Marth
  Class, Detailed Chaingrab Information), reddit threads (Edgeguarding Fox as Marth, ASDI Down
  Marth Killer, DJB ledge tech). YouTube cards were used for titles only.
