---
schema: melee-character/v1
id: mr-game-and-watch
name: Mr. Game & Watch
aliases: [G&W, GnW, Game and Watch, GW]
tier: "C- (19th of 26), 2021 tier list"
archetype: [lightweight, glass-cannon, punish-heavy, chaingrab, combo-food, mixup]
related: []
summary: Mr. Game & Watch wins by landing down tilt or a grab, chaining throws and tilts on fastfallers, and ending with his very strong neutral air, forward air or forward smash before his light weight and poor shield cost him the stock.
key_tech: [non-l-cancellable-aerials, fair-l-cancel, dtilt-combos, throw-chain-grab, throw-ambiguity, throw-to-nair-kill, judge, oil-panic-bucket, up-b-out-of-shield, light-shield]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlGw.dat
framedata: ../framedata/mr-game-and-watch.json
code: src/melee/ft/kinds/ftGameWatch
specials:
  neutral_b: "Chef"
  side_b: "Judgment (Judge)"
  up_b: "Fire"
  down_b: "Oil Panic (bucket)"
attributes:
  weight: 60
  gravity: 0.095
  fall_speed: 1.7
  fast_fall_speed: 2.3
  jump_squat: 4
  jumps: 2
  walk_speed: 1.1
  dash_speed: 1.5
  run_speed: 1.5
  traction: 0.06
  air_speed: 1
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [4, 16, 3]
  rapid_jab_start: [null, 4, 0]
  rapid_jab_loop: [7, 12, 3]
  rapid_jab_end: [null, 9, 0]
  dash_attack: [6, 38, 9]
  utilt: [9, 30, 9]
  dtilt: [6, 26, 12]
  fsmash: [13, 42, 18]
  usmash: [24, 40, 18]
  dsmash: [15, 35, 16]
  nair: [20, 45, 16]
  fair: [10, 45, 16]
  bair: [10, 40, 5]
  uair: [7, 40, 9]
  dair: [12, 50, 14]
  grab: [7, 31, 0]
  dash_grab: [11, 41, 0]
  pummel: [13, 31, 3]
  fthrow: [null, 70, 8]
  bthrow: [null, 70, 8]
  uthrow: [null, 70, 8]
  dthrow: [null, 70, 8]
  special_n: [18, 50, 5]
  special_air_n: [18, 50, 5]
  special_s: [16, 50, 2]
  special_s_298: [16, 50, 4]
  special_s_299: [16, 50, 6]
  special_s_300: [16, 50, 8]
  special_s_301: [16, 50, 3]
  special_s_302: [16, 50, 12]
  special_s_303: [16, 50, 14]
  special_s_304: [16, 50, 4]
  special_s_305: [16, 50, 32]
  special_air_s: [16, 50, 2]
  special_air_s_307: [16, 50, 4]
  special_air_s_308: [16, 50, 6]
  special_air_s_309: [16, 50, 8]
  special_air_s_310: [16, 50, 3]
  special_air_s_311: [16, 50, 12]
  special_air_s_312: [16, 50, 14]
  special_air_s_313: [16, 50, 4]
  special_air_s_314: [16, 50, 32]
  special_hi: [1, 40, 6]
  special_air_hi: [1, 40, 6]
  special_lw: [null, 50, 0]
  special_lw_catch: [null, 25, 0]
  special_lw_shoot: [2, 50, 1]
  special_air_lw: [null, 50, 0]
  special_air_lw_catch: [null, 25, 0]
  special_air_lw_shoot: [2, 50, 1]
oos:  # option: frame the hitbox is out
  special_hi: 2
  grab: 7
  uair: 11
  fair: 14
  bair: 14
  dair: 16
  nair: 24
  usmash: 25
resources: 2
# generated: end
---

# Mr. Game & Watch

<!-- GENERATED:attributes -->
## Attributes

Read from `PlGw.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 60 |
| Gravity | 0.095 |
| Terminal fall speed | 1.7 |
| Fast-fall speed | 2.3 |
| Jump squat (frames before airborne) | 4 |
| Full hop / short hop initial Y speed | 2.3 / 1.4 |
| Air jump Y multiplier | 1 |
| Jumps | 2 |
| Walk max speed | 1.1 |
| Dash initial speed / run max speed | 1.5 / 1.5 |
| Ground friction (traction) | 0.06 |
| Air max horizontal speed | 1 |
| Air acceleration (base + stick) | 0.02 + 0.03 |
| Air friction | 0.016 |
| Normal landing lag | 4 |
| Shield size | 10.75 |
<!-- /GENERATED:attributes -->

## Overview

Mr. Game & Watch (G&W) is the second lightest character in the game (weight 60) with an
average fall speed (1.7) and a 4-frame jump squat [wiki:Mr._Game_&_Watch_(SSBM)]. He hits
very hard for his size: nair is the strongest neutral air in the game, fair and fsmash are
real kill moves, and dtilt is one of the best down tilts, both a combo starter and a kill
move [wiki:Mr._Game_&_Watch_(SSBM)] [wiki:Mr._Game_&_Watch_(SSBM)/Down_tilt]. All four
throws use the same animation, so the opponent cannot see which direction is coming, and
up throw and down throw chain grab fastfallers and set up nair kills
[wiki:Mr._Game_&_Watch_(SSBM)]. The character is held back by development oversights:
three of his five aerials (nair, bair, uair) cannot be L-cancelled, his full shield does
not cover his body, and his spot dodge has more lag than intangibility
[wiki:Mr._Game_&_Watch_(SSBM)]. He has no real zoning projectile, a slow and predictable
approach, and dies early. In practice he plays a bait-and-punish game around dtilt, fair
and grab, and tries to make each opening count.

## Strengths and weaknesses

- **Strengths:**
  - Nair: 16%, active frames 20-29, large hitbox all around him; KOs Mario at 111% from the
    centre of Final Destination [wiki:Mr._Game_&_Watch_(SSBM)/Neutral_aerial].
  - Dtilt: hits frame 6, actionable frame 26, 12% on grounded opponents, KOs middleweights
    at roughly 110% [wiki:Mr._Game_&_Watch_(SSBM)/Down_tilt].
  - Fsmash: 18% clean, lingers to frame 33, KOs lightweights from about 80%
    [wiki:Mr._Game_&_Watch_(SSBM)] [fd].
  - Grab game: identical-looking throws, chain grabs on fastfallers, throw into nair or
    Judge [wiki:Mr._Game_&_Watch_(SSBM)].
  - Disjointed, lingering hitboxes (ftilt, fsmash, fair, dair, bair)
    [wiki:Mr._Game_&_Watch_(SSBM)].
  - Up B (Fire) has a hitbox from frame 1 and great vertical distance
    [wiki:Mr._Game_&_Watch_(SSBM)/Up_special].
  - Very low crouch and small frame; opponents often lack matchup experience.
- **Weaknesses:**
  - Nair, bair and uair cannot be L-cancelled (they use a special-move landing state)
    [wiki:L-canceling] [wiki:Mr._Game_&_Watch_(SSBM)].
  - Smallest full shield in the game; easily shield-poked unless he light shields
    [wiki:Mr._Game_&_Watch_(SSBM)].
  - Spot dodge is the only one with more lag than intangibility; rolls are short and slow
    [wiki:Mr._Game_&_Watch_(SSBM)].
  - Weight 60: dies very early, and is still combo-able because of his fall speed
    [wiki:Mr._Game_&_Watch_(SSBM)].
  - Poor approach, no zoning tool, slow tilts and smashes other than dtilt
    [wiki:Mr._Game_&_Watch_(SSBM)].
  - Recovery is one predictable vertical move [wiki:Mr._Game_&_Watch_(SSBM)].

## Character tech

### Aerials that cannot be L-cancelled

- **id:** `non-l-cancellable-aerials`
- **What:** G&W's neutral, back and up aerials are coded as special moves and use a
  nonstandard landing state, so an [L-cancel](../techniques/l-cancel.md) input does
  nothing for them. Only forward air and down air can be L-cancelled [wiki:L-canceling]
  [wiki:Mr._Game_&_Watch_(SSBM)].
- **Inputs:** None; this is a restriction. Plan each aerial so it finishes in the air,
  auto-cancels, or lands where the lag is safe.
- **Timing:** Landing lag: nair 15 frames [wiki:Mr._Game_&_Watch_(SSBM)/Neutral_aerial];
  bair 18 and uair 15 in the frame data dump [fd] (a Smashboards guide lists 18 for uair
  [web:smashboards.com Flatten the Opposition]). The dump also prints halved "L-cancelled"
  values for these three (7, 9, 7); those cannot occur in game. Bair has a landing hitbox
  (3%) [wiki:Mr._Game_&_Watch_(SSBM)]. Nair on shield is about -6
  [wiki:Mr._Game_&_Watch_(SSBM)/Neutral_aerial].
- **Used for:** Knowing which aerials are safe: nair is "often used high enough to
  receive no landing lag" in kill set-ups [wiki:Mr._Game_&_Watch_(SSBM)].
- **Common errors:** Short hop nair/bair into shield at close range and being shield
  grabbed; habitually pressing L and expecting half lag.
- **Drill idea:** CPU shields; the player must hit the shield with nair and still avoid
  the shield grab (spacing/cross-up), measured by whether the grab connects.

### Forward air L-cancel

- **id:** `fair-l-cancel`
- **What:** Fair is his main approach aerial and one of the two he can L-cancel. Landing
  lag is 25 frames normally and 12 L-cancelled
  [wiki:Mr._Game_&_Watch_(SSBM)/Forward_aerial].
- **Inputs:** Short hop, fair, fast fall, L/R/Z within 7 frames before landing.
- **Timing:** Clean hit frames 10-12 (16%), late hit frames 13-32 (6%)
  [wiki:Mr._Game_&_Watch_(SSBM)/Forward_aerial] [fd]. Dair likewise: 20 frames, 10
  L-cancelled, with a landing hitbox (6%) [wiki:Mr._Game_&_Watch_(SSBM)/Down_aerial].
- **Used for:** Approaching, combo finisher (clean hit), combo starter and gimp tool (weak
  late hit) [wiki:Mr._Game_&_Watch_(SSBM)/Forward_aerial]. Weak fair into jab or grab
  [web:smashboards.com Flatten the Opposition].
- **Common errors:** Missed L-cancel leaves 25 frames of lag; hitting shield point-blank
  and being grabbed.
- **Drill idea:** CPU shields then shield grabs; success is a late, spaced fair,
  L-cancelled, followed by dtilt or grab before the CPU's grab.

### Down tilt combos

- **id:** `dtilt-combos`
- **What:** Dtilt (manhole) launches grounded opponents at 85 degrees with base knockback
  65 [fd], with very little end lag, so G&W can follow with another dtilt, a grab, fair,
  uair, nair or up B [wiki:Mr._Game_&_Watch_(SSBM)/Down_tilt].
- **Inputs:** Down + A; repeat, or jump and aerial, or grab.
- **Timing:** Hitbox frames 6-13, actionable (IASA) frame 26, animation 29
  [wiki:Mr._Game_&_Watch_(SSBM)/Down_tilt]. On Fox and Falco, dtilt into grab does not
  work at 0% (dtilt again instead) but works from around 10%
  [web:smashboards.com Flatten the Opposition]. An airborne target takes the weaker
  9% hitbox [wiki:Mr._Game_&_Watch_(SSBM)].
- **Used for:** His main combo starter at low percent, chain-grab starter on fastfallers,
  and a kill move above 100% [wiki:Mr._Game_&_Watch_(SSBM)]. Strong after a
  [crouch cancel](../techniques/crouch-cancel.md) [wiki:Mr._Game_&_Watch_(SSBM)/Down_tilt].
- **Common errors:** Second dtilt after the opponent has already teched away; using it on
  shield at close range.
- **Drill idea:** CPU Fox at 10% is hit by dtilt; success is a grab or second dtilt
  connecting before Fox can act.

### Throw chain grab on fastfallers

- **id:** `throw-chain-grab`
- **What:** Up throw chain grabs [Fox](fox.md), [Falco](falco.md) and
  [Captain Falcon](captain-falcon.md); down throw, which has 20 less base knockback than
  his other throws, chain grabs fastfallers at around 100% and above
  [wiki:Mr._Game_&_Watch_(SSBM)] [wiki:Mr._Game_&_Watch_(SSBM)/Down_throw]
  [web:smashboards.com Flatten the Opposition]. See
  [chain grab](../techniques/chain-grab.md).
- **Inputs:** Grab, uthrow (low/mid percent) or dthrow (high percent), follow the DI,
  regrab; exit into utilt, usmash, nair or Judge.
- **Timing:** Every throw is 8% and releases on frame 55 of a 69-frame animation at
  baseline weight (speed depends on the opponent's weight)
  [wiki:Mr._Game_&_Watch_(SSBM)/Up_throw] [wiki:Mr._Game_&_Watch_(SSBM)/Down_throw].
  Grab is active frames 7-8, 30 frames total [wiki:Mr._Game_&_Watch_(SSBM)/Grab] (the
  dump lists 6-7 [fd]). The up throw releases at an angle rather than straight up
  [web:smashboards.com Flatten the Opposition]. Exact percent windows: Unknown.
- **Used for:** Most of his damage on fastfallers; the "zero-to-death on Falco" route in
  the guide is four up throws, wavedash utilt, dair, fair, full hop nair, noted as very
  difficult because of DI [web:smashboards.com Flatten the Opposition].
- **Common errors:** Regrab late so a spacie shines out; misreading DI with a short grab.
- **Drill idea:** G&W holds Fox at 20% with random DI; success is three regrabs then a
  finisher.

### Throw ambiguity

- **id:** `throw-ambiguity`
- **What:** All four throws show the same juggling animation, so the opponent must guess
  the direction when choosing DI [wiki:Mr._Game_&_Watch_(SSBM)].
- **Inputs:** Grab, then any throw direction; vary it.
- **Timing:** Release frame 55 for all four [wiki:Mr._Game_&_Watch_(SSBM)/Up_throw].
- **Used for:** Punishing DI: an opponent holding the DI for up throw is sent far by a
  forward or back throw near the ledge, which starts an edgeguard
  [web:smashboards.com Flatten the Opposition]. Forward and back throw also combo into
  nair with DI mixups [wiki:Mr._Game_&_Watch_(SSBM)/Neutral_aerial].
- **Common errors:** Always using the same throw.
- **Drill idea:** As a defensive drill with G&W as the CPU: the CPU throws in a random
  direction and the player must survive using a neutral DI choice, or the reverse, with
  the player choosing the throw that beats a CPU's pre-committed DI.

### Throw into neutral air (kill set-up)

- **id:** `throw-to-nair-kill`
- **What:** Dthrow or uthrow puts the opponent just above G&W long enough for nair's
  frame 20 hitbox to connect [wiki:Mr._Game_&_Watch_(SSBM)/Neutral_aerial].
- **Inputs:** Grab, dthrow (floaties and mid-weights, high percent) or uthrow, short hop
  or full hop, nair toward the DI. Fair if they DI far away
  [web:smashboards.com Flatten the Opposition].
- **Timing:** Nair hits frames 20-29 of 44 [wiki:Mr._Game_&_Watch_(SSBM)/Neutral_aerial].
  The guide says dthrow nair should "almost always" be the finisher on Sheik, Captain
  Falcon, Ganondorf, Jigglypuff, Marth, Peach and other floaties, with a full hop needed
  on Jigglypuff at some percents [web:smashboards.com Flatten the Opposition].
- **Used for:** His most reliable kill confirm; nair can KO under 125%
  [wiki:Mr._Game_&_Watch_(SSBM)].
- **Common errors:** Jumping the wrong way; nair started too late (20-frame start-up);
  landing with the 15-frame lag next to a surviving opponent.
- **Drill idea:** G&W holds a CPU at 100-130% with random DI; success is nair connecting
  as a true combo.

### Judge (Judgment hammer)

- **id:** `judge`
- **What:** Side B swings a hammer with a random number 1-9; each number has different
  damage and knockback. A 9 does 32% with base knockback 100 and growth 80 [fd] and KOs at
  single-digit percents [wiki:Mr._Game_&_Watch_(SSBM)].
- **Inputs:** Side B, in range. Combo set-ups: dtilt into Judge, dthrow into Judge on
  floaties, uthrow into Judge on fastfallers [web:smashboards.com Flatten the Opposition]
  [wiki:Mr._Game_&_Watch_(SSBM)].
- **Timing:** Hitbox frames 16-29 of 49 (number 5 hits four times, frames 16-27)
  [wiki:Mr._Game_&_Watch_(SSBM)/Side_special]. The number is not uniformly random: it
  cannot repeat either of the previous two results, so each of the 7 allowed numbers has
  a 1/7 chance; at match start the "previous two" are set to 1 and 2, so the first use
  cannot be 1 and the first two cannot be 2 [wiki:Judge]. Results: 1 = 2% and 12% recoil
  to G&W; 2 = 4%; 3 = 6%, high shield damage, sends toward G&W; 4 = 8%; 5 = 3% x4
  electric; 6 = 12% fire semi-spike; 7 = 14%; 8 = 4% freeze; 9 = 32%
  [wiki:Mr._Game_&_Watch_(SSBM)]. The 9 has a smaller hitbox.
- **Used for:** A gamble out of a true combo, or when far ahead or behind. After a 9,
  use Judge twice more (for example during the respawn) to make 9 possible again
  [wiki:Judge].
- **Common errors:** Throwing it out raw; forgetting the 1's self-damage; not reacting to
  the number (8 freezes and allows a follow-up).
- **Drill idea:** Force the RNG to a chosen number and have the player follow up
  correctly after each result; or a set-up drill judged on Judge connecting as a combo
  regardless of number.

### Oil Panic (bucket)

- **id:** `oil-panic-bucket`
- **What:** Down B holds out a bucket that absorbs energy projectiles. After three, the
  next down B spills the oil as a strong hit [wiki:Mr._Game_&_Watch_(SSBM)].
- **Inputs:** Down B (hold) to catch; when full, down B to spill.
- **Timing:** Absorbs from frame 5; the bucket stance is a 33-frame loop that must finish
  after release, plus a 12-frame ending. Catching a projectile makes him intangible for
  the 25-frame catch animation. Spill damage is 1.5x the absorbed damage plus 5%
  (minimum 12%), with hitboxes on frames 2-37 of 49. The aerial spill's second and third
  hitboxes do only 1% because of a bug. The absorption bubble is small, so some
  projectiles hit him anyway. A partial bucket is kept after losing a stock
  [wiki:Mr._Game_&_Watch_(SSBM)/Down_special] [wiki:Mr._Game_&_Watch_(SSBM)].
- **Used for:** Matchups with energy projectiles: Fox/Falco lasers, Mario/Luigi/Dr. Mario
  fireballs and pills, Samus charge shot, Ness's PK moves, Ice Climbers' ice blocks,
  Mewtwo's shadow ball, Pikachu/Pichu thunder, Zelda's fireball. Not absorbable: Samus
  missiles, Peach's turnips, Link and Young Link projectiles, Sheik's needles, Yoshi's
  eggs [web:smashboards.com Flatten the Opposition]. Also stalls his fall briefly.
- **Common errors:** Bucketing at close range (long loop is punished); spilling into a
  shield with a very strong bucket, which triggers the "kamikaze glitch" and sends G&W
  sliding off the stage [wiki:Mr._Game_&_Watch_(SSBM)/Down_special].
- **Drill idea:** CPU Falco shoots lasers from far away and occasionally approaches;
  success is three absorbs without being hit, then landing the spill.

### Up B out of shield

- **id:** `up-b-out-of-shield`
- **What:** Up B (Fire) has a hitbox on frame 1 that lasts to frame 37, 6% at 80 degrees
  [wiki:Mr._Game_&_Watch_(SSBM)/Up_special] [fd]. From shield it is an immediate escape
  that carries him high above the opponent.
- **Inputs:** In shield, after shield stun: up + B.
- **Timing:** Hitbox frame 1; animation 39 frames, then special fall. Landing lag is 40
  frames if he lands during the move and 6 frames from special fall
  [wiki:Mr._Game_&_Watch_(SSBM)/Up_special]. Intangibility on start-up: Unknown.
- **Used for:** Getting out of shield pressure, which he otherwise cannot answer (his
  out-of-shield options are rated poor [wiki:Mr._Game_&_Watch_(SSBM)]). Also a combo
  ender on light characters near the top of the screen, after which he fast falls to
  avoid a punish [web:smashboards.com Flatten the Opposition].
- **Common errors:** The hit is weak, so the opponent recovers first and waits under him
  to punish the helpless landing; using it near the ledge and drifting offstage.
- **Drill idea:** CPU Fox/Falco pressures shield; success is up B out of shield hitting
  or escaping and G&W landing on a platform or the ground without being hit.

### Light shielding

- **id:** `light-shield`
- **What:** G&W's full (hard) shield bubble is the smallest in the game and leaves parts
  of his body uncovered even at full strength; a light shield (analog trigger partly
  pressed) is larger and covers him [wiki:Mr._Game_&_Watch_(SSBM)]. See
  [shield](../techniques/shield.md).
- **Inputs:** Press L or R partway rather than to the click.
- **Timing:** No frame data found. General rule: light shields are bigger but are pushed
  farther and suffer more shield stun [unverified].
- **Used for:** Blocking moves that would otherwise poke his head or feet; a guide lists
  "master light shielding" as a first requirement for the character
  [web:smashboards.com Flatten the Opposition].
- **Common errors:** Hard-pressing the trigger out of habit and being poked; being pushed
  off a platform or ledge by the extra shield push.
- **Drill idea:** CPU Marth uses spaced fair/dtilt on shield; success is blocking a set
  number of hits with no shield poke.

## Neutral game

- Dash dance and foxtrot rather than run; his dash-based movement is his best ground
  mobility [wiki:Mr._Game_&_Watch_(SSBM)]. Wavedash is decent (traction 0.06).
- Main pokes: dtilt (frame 6), spaced late fair, jab (frame 4, actionable frame 16 [fd])
  into dtilt or grab [web:smashboards.com Flatten the Opposition].
- Wavedash forward into dtilt, wavedash back into fsmash against an approach
  [web:smashboards.com Flatten the Opposition].
- Ftilt (frames 13-30 [fd]) and fsmash (frames 13-33 [fd]) linger and wall out
  approaches and recoveries.
- Utilt (frames 9-29 [wiki:Mr._Game_&_Watch_(SSBM)/Up_tilt]) is a long-lasting anti-air
  and juggle tool.
- Dash attack (frames 6-29 [fd]) sends the opponent behind him with low knockback; turn
  around fsmash follows [web:smashboards.com Flatten the Opposition].
- Chef (neutral B): first sausage on frame 18; up to five; low damage, erratic arcs. The
  wiki says it has some edgeguarding and anti-ledge-camping use
  [wiki:Mr._Game_&_Watch_(SSBM)].
- Avoid shielding where possible; dodge by movement and punish with dtilt or grab.

## Punish game

G&W's reward off a grab or dtilt is high, especially on fastfallers. The list below is
mostly from a Smashboards guide that reproduces Qerb's combo guide; almost no percent
windows are given, so rows are "typical" unless stated
[web:smashboards.com Flatten the Opposition].

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| uthrow | Fox, Falco, Captain Falcon | low-mid | regrab (chain grab) | | [web:smashboards.com Flatten the Opposition] [wiki:Mr._Game_&_Watch_(SSBM)] |
| uthrow | fastfallers | mid | usmash, utilt, uair | usmash is slow; spacies can shine | [web:smashboards.com Flatten the Opposition] |
| uthrow | fastfallers | high | nair or Judge | | [web:smashboards.com Flatten the Opposition] |
| dthrow | fastfallers | about 100%+ | regrab | | [wiki:Mr._Game_&_Watch_(SSBM)/Down_throw] |
| dthrow | Sheik | low-mid | regrab or tech chase grab | "your only hope vs Sheiks" | [web:smashboards.com Flatten the Opposition] |
| dthrow | most | low | dtilt | watch for tech away | [web:smashboards.com Flatten the Opposition] |
| dthrow | fastfallers | mid | fsmash or ftilt | | [web:smashboards.com Flatten the Opposition] |
| dthrow | floaties, mid-weights | high | nair (DI up), fair (DI away) | main kill confirm | [web:smashboards.com Flatten the Opposition] |
| dthrow | floaties | any | Judge | gamble | [web:smashboards.com Flatten the Opposition] |
| dtilt | Fox, Falco | 0% | dtilt | grab does not connect at 0% | [web:smashboards.com Flatten the Opposition] |
| dtilt | Fox, Falco | around 10%+ | grab, then chain grab | | [web:smashboards.com Flatten the Opposition] |
| dtilt | most | low-mid | fair, nair, uair, up B | "bread and butter" | [web:smashboards.com Flatten the Opposition] [wiki:Mr._Game_&_Watch_(SSBM)/Down_tilt] |
| dair (both hits, grounded) | most | low | dtilt, fair | about 45% total | [web:smashboards.com Flatten the Opposition] |
| utilt | fastfallers | low-mid | utilt, grab (side hit) | | [web:smashboards.com Flatten the Opposition] |
| jab | most | low | dtilt or grab | | [web:smashboards.com Flatten the Opposition] |
| late fair | most | low | jab, grab, tech chase | | [web:smashboards.com Flatten the Opposition] |
| bair | floaties | mid | double jump nair | | [web:smashboards.com Flatten the Opposition] |

### Chain grabs and tech chases

Up throw chain grabs Fox, Falco and Captain Falcon; down throw chain grabs fastfallers at
around 100% and above and can chain or tech-chase Sheik; forward and back throw can also
lead to regrabs on fastfallers depending on DI
[wiki:Mr._Game_&_Watch_(SSBM)] [web:smashboards.com Flatten the Opposition]. Percent
windows and the DI that breaks them were not found in a readable source (a Smashboards
thread "Game & Watch grab flowcharts vs spacies" exists but could not be fetched). Because
the four throws look the same, DI mixups are part of the chain. Low-percent dthrow and
weak fair lead to tech chases covered by grab or dtilt
[web:smashboards.com Flatten the Opposition].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| nair (16%) | Mario | 111% | centre of Final Destination | [wiki:Mr._Game_&_Watch_(SSBM)/Neutral_aerial] |
| nair | most | under 125% | horizontal; earlier offstage | [wiki:Mr._Game_&_Watch_(SSBM)] |
| dtilt (12%) | middleweights | roughly 110% | grounded target | [wiki:Mr._Game_&_Watch_(SSBM)/Down_tilt] |
| fsmash clean (18%) | lightweights | about 80%+ | torch hitbox, frames 13-16 | [wiki:Mr._Game_&_Watch_(SSBM)] [fd] |
| Judge 9 (32%) | everyone | single digits | 1/7 chance when allowed | [wiki:Mr._Game_&_Watch_(SSBM)] [wiki:Judge] |
| usmash (18%) | most | Unknown | hits frames 24-28, very slow | [fd] |
| dsmash hammer tips (16%) | most | Unknown | tips send up; handles are weak (10%, 20 degrees) | [wiki:Mr._Game_&_Watch_(SSBM)] [fd] |
| fair clean (16%) | most | Unknown | combo finisher, offstage | [wiki:Mr._Game_&_Watch_(SSBM)/Forward_aerial] |
| Oil Panic spill | projectile users | varies with absorbed damage | needs three absorbs | [wiki:Mr._Game_&_Watch_(SSBM)/Down_special] |
| up B (6%) | Jigglypuff and other light characters | high percent | near the top on low-ceiling stages | [web:smashboards.com Flatten the Opposition] |

- Kill set-ups: dthrow/uthrow into nair; dtilt into nair or fair; dtilt or throw into
  Judge.
- Edgeguards: nair and fair offstage (weak late fair gimps), ftilt/fsmash lingering at the
  ledge, dtilt on low recoveries, dair's first frame (frame 12) is a meteor (270 degrees)
  [fd] [wiki:Mr._Game_&_Watch_(SSBM)], Judge 6 is a semi-spike, Chef's pan can hit
  recovering opponents [web:smashboards.com Flatten the Opposition].
- A surprise forward/back throw at the ledge beats up-throw DI and starts the edgeguard.

## Recovery

- **Options:**
  - Double jump (26.7 units, close to his 29-unit full hop) [wiki:Mr._Game_&_Watch_(SSBM)].
  - Up B (Fire): excellent vertical distance, average horizontal distance, hitbox frames
    1-37, ends in special fall with good drift [wiki:Mr._Game_&_Watch_(SSBM)]
    [wiki:Mr._Game_&_Watch_(SSBM)/Up_special].
  - Air dodge.
  - Oil Panic stalls his fall for a moment [web:smashboards.com Flatten the Opposition].
- **Mixups:** Timing of the double jump; up B from low to sweetspot the ledge (reported
  hard on Battlefield and easier on Dream Land [web:smashboards.com Flatten the
  Opposition]) versus up B past the ledge onto the stage or a platform; bucket stall.
- **Weaknesses:** One move, one path: easy to read, edgehog or intercept
  [wiki:Mr._Game_&_Watch_(SSBM)]. If the ledge is taken he lands on stage helpless with 6
  frames of landing lag, or 40 if he lands during the up B itself
  [wiki:Mr._Game_&_Watch_(SSBM)/Up_special]. At weight 60 he is frequently hit too far to
  come back at all.

### Edgeguarding Mr. Game & Watch

- Grab the ledge as he starts up B from below: with the ledge occupied he must rise past
  it and fall helpless onto the stage, where any smash kills at his weight.
- If he is level with or above the stage, he will drift in during special fall; wait
  under him and punish the landing.
- Hitting him out of up B is harder because the hitbox is out from frame 1; disjointed or
  lingering moves from above or the side work best. Low-knockback pokes are enough
  because he is so light.
- Offstage chases are effective before he jumps: his double jump is his only horizontal
  tool besides drift.
- Watch for a bucket stall changing the timing.

## Defense and out of shield

- Shield: full shield does not cover him; light shield does
  [wiki:Mr._Game_&_Watch_(SSBM)]. Expect shield pokes from Marth, Sheik and Fox aerials on
  a hard shield.
- Out of shield: up B (frame 1 hitbox) is the escape; shield grab is frame 7
  [wiki:Mr._Game_&_Watch_(SSBM)/Grab]; nair is too slow (frame 20) and uair hits frame 7
  [fd] after a 4-frame jump squat; overall rated poor [wiki:Mr._Game_&_Watch_(SSBM)].
  Wavedash out of shield is the usual non-committal choice.
- Spot dodge: 32 frames total, invulnerable frames 2-12; roll: 35 frames, invulnerable
  4-19 [web:smashboards.com Flatten the Opposition]. Both are poor; avoid them under
  pressure.
- Crouch cancel into dtilt is one of his best defensive answers at low percent
  [wiki:Mr._Game_&_Watch_(SSBM)/Down_tilt], but at weight 60 crouch cancel stops working
  earlier than for other characters [unverified].
- Combo escapes: up B (frame 1), double jump, bucket momentum stop; no fast nair (frame
  20).
- What beats him: any sustained shield pressure, chain grabs, and early kill moves.

## As the training dummy

- Weight 60, second lightest (only [Pichu](pichu.md) is lighter [unverified]); fall speed
  1.7, fast-fall 2.3 [wiki:Mr._Game_&_Watch_(SSBM)]. He flies far from every hit but
  falls at a normal rate, so he is both combo-able and easy to kill.
- [Sheik](sheik.md)'s dthrow chain throws him (he is on the wiki's list) [wiki:Chain_grab].
- [Ness](ness.md)'s dthrow fire hits whiff on him [wiki:Ness_(SSBM)], and
  [Young Link](young-link.md)'s short stature is noted as helping grab him while he
  crouches [wiki:Young_Link_(SSBM)]: his crouch is very low, so some grabs and high
  moves miss.
- His hard shield can be poked at full strength, useful for shield-poke drills.
- Kill percents on him are far lower than on a middleweight; use him to practise early
  kill confirms. Throws that scale with weight are faster on him.
- Realistic CPU choices: DI kill moves up-and-in/away as appropriate, up B out of shield
  or out of combos, recover with double jump then up B to the ledge.

## Matchup notes

### vs Fox and Falco

- He is overwhelmed by shield pressure (poor shield, poor out-of-shield) and dies very
  early to up smash and up air. Lasers can be bucketed, but the bucket loop is long and
  risky [wiki:Mr._Game_&_Watch_(SSBM)/Down_special].
- His win condition is the grab or dtilt: dtilt into grab from about 10%, uthrow chain
  grab, then utilt/usmash/nair, and an edgeguard with fair/nair
  [web:smashboards.com Flatten the Opposition].

### vs Sheik

- Sheik chain grabs him [wiki:Chain_grab] and her fair kills him early. The guide's
  advice is to chain grab or tech chase her with dthrow at low percent and finish with
  dthrow nair [web:smashboards.com Flatten the Opposition].

### vs Marth

- Marth's sword pokes his shield and outranges everything but ftilt/fsmash. G&W needs
  dtilt after a crouch cancel or a whiff punish grab; dthrow nair is the finisher
  [web:smashboards.com Flatten the Opposition].

### vs Jigglypuff and Peach

- Floaties are not chain grabbed; use dthrow into nair (full hop on Jigglypuff at some
  percents) or into Judge [web:smashboards.com Flatten the Opposition]. Peach's turnips
  cannot be bucketed.

### vs projectile characters (Samus, Dr. Mario, Mario, Luigi, Ice Climbers, Ness, Mewtwo)

- The bucket changes the matchup: charge shot, pills/fireballs, ice blocks, PK moves and
  shadow ball are absorbable; missiles are not
  [web:smashboards.com Flatten the Opposition]. A full bucket is a kill threat that
  survives his own death (the stored count is kept) [wiki:Mr._Game_&_Watch_(SSBM)].

## Drill seeds

### Down tilt into grab on spacies

- **id:** `mr-game-and-watch-dtilt-grab`
- **Goal:** Convert dtilt into a grab or a second dtilt at the right percent.
- **Player:** Mr. Game & Watch
- **CPU:** Fox, Falco
- **Setup:** Final Destination, CPU standing in dtilt range at 0-30%.
- **CPU behaviour:** After being hit: random DI, then shine/jump/tech as soon as possible.
- **Success:** At 0% a second dtilt connects; from about 10% a grab connects before the
  CPU acts.
- **Fail:** CPU acts first, grab whiffs.
- **Variations:** Start from a crouch cancel of the CPU's nair; start from wavedash
  forward.
- **Data needed:** Dtilt hit 6-13 / IASA 26 and knockback (85 degrees, base 65), grab
  frame 7, Fox/Falco weight and fall speed.

### Up throw chain grab

- **id:** `mr-game-and-watch-uthrow-chaingrab`
- **Goal:** Follow DI and regrab fastfallers.
- **Player:** Mr. Game & Watch
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** G&W holding the CPU in grab, centre of Final Destination, 10-40%.
- **CPU behaviour:** Random DI left/right/none; acts on the first possible frame.
- **Success:** Three regrabs, or regrab into utilt/usmash/nair.
- **Fail:** CPU escapes.
- **Variations:** Down throw version at 100%+; log the highest percent that still works
  (not documented in the sources read).
- **Data needed:** Throw release frame 55 and animation 69 (weight scaled), throw
  knockback values, grab range, opponent fall speeds.

### Throw into neutral air kill

- **id:** `mr-game-and-watch-throw-nair`
- **Goal:** Land the nair kill confirm against all DI.
- **Player:** Mr. Game & Watch
- **CPU:** Marth, Sheik, Peach, Jigglypuff, Captain Falcon
- **Setup:** G&W holding the CPU in grab at 90-130%, centre stage.
- **CPU behaviour:** Random DI; double jumps or air dodges when actionable.
- **Success:** Nair connects before the CPU is actionable and kills or sends offstage.
- **Fail:** Nair whiffs or hits after the CPU could have escaped.
- **Variations:** Fair on DI away; full hop for Jigglypuff; choose dthrow or uthrow per
  character.
- **Data needed:** Dthrow/uthrow knockback (dthrow base is 20 lower), nair start-up 20,
  jump squat 4, CPU weights.

### Throw direction guessing game (defence)

- **id:** `mr-game-and-watch-throw-di`
- **Goal:** As the opponent, survive G&W's identical throws; as G&W, punish committed DI.
- **Player:** any character (or G&W in the reverse version)
- **CPU:** Mr. Game & Watch
- **Setup:** CPU G&W holds the player in grab near the ledge at 80-120%.
- **CPU behaviour:** Random throw direction, then the best follow-up (nair for up/down
  throws, edgeguard for forward/back).
- **Success:** Player survives the sequence and returns to stage.
- **Fail:** Player loses the stock.
- **Variations:** Reverse roles with a CPU that pre-commits DI for up throw.
- **Data needed:** Knockback and angle of each throw, release frame 55.

### Safe aerials on shield

- **id:** `mr-game-and-watch-safe-aerials`
- **Goal:** Use L-cancelled fair and spaced nair without being shield grabbed.
- **Player:** Mr. Game & Watch
- **CPU:** Marth, Sheik, Peach
- **Setup:** CPU shielding at centre stage.
- **CPU behaviour:** Shield grabs or uses its fastest out-of-shield option as soon as
  shield stun ends.
- **Success:** Aerial hits shield and G&W is not hit or grabbed afterwards (by spacing,
  crossing up, or L-cancel into dtilt/jab).
- **Fail:** G&W is grabbed or hit.
- **Variations:** Fair only (must L-cancel: 25 vs 12 frames); nair only (15 frames, no
  L-cancel, about -6); bair with landing hitbox.
- **Data needed:** Landing lag per aerial, shield stun, CPU grab frame and range.

### Up B out of shield versus pressure

- **id:** `mr-game-and-watch-up-b-oos`
- **Goal:** Escape shield pressure and land safely.
- **Player:** Mr. Game & Watch
- **CPU:** Fox, Falco, Peach
- **Setup:** Battlefield, G&W light-shielding under a platform, CPU in front.
- **CPU behaviour:** Aerial into shine or jab pressure; after the up B it waits under G&W
  to punish the landing.
- **Success:** Up B comes out between pressure hits and G&W lands on a platform or the
  ground and is actionable without being hit.
- **Fail:** Hit out of shield, shield poked, or punished on landing.
- **Variations:** Final Destination (no platform); wavedash out of shield as the
  alternative.
- **Data needed:** Up B hitbox frame 1, landing lag 6 from special fall, shield stun
  values.

### Light shield discipline

- **id:** `mr-game-and-watch-light-shield`
- **Goal:** Block without being poked.
- **Player:** Mr. Game & Watch
- **CPU:** Marth, Sheik, Fox
- **Setup:** Centre stage, CPU at poke range.
- **CPU behaviour:** Random high and low pokes (Marth fair/dtilt, Sheik fair/ftilt, Fox
  nair/dair).
- **Success:** Ten hits blocked with no damage taken.
- **Fail:** Shield poke or shield break.
- **Variations:** Shield angling required; on a platform.
- **Data needed:** G&W shield bubble sizes for hard and light shield, hurtbox positions,
  CPU hitbox heights.

### Recovery and edgeguard (both sides)

- **id:** `mr-game-and-watch-recovery`
- **Goal:** Sweetspot the ledge with up B; or, as the opponent, punish the predictable
  path.
- **Player:** Mr. Game & Watch (or the edgeguarder)
- **CPU:** Marth, Sheik, Fox (or CPU G&W)
- **Setup:** G&W offstage below the ledge at 50-80% with or without double jump.
- **CPU behaviour:** As edgeguarder: random between grabbing the ledge, waiting on stage
  to punish the landing, and jumping out. As G&W: double jump then up B aimed at the
  ledge or the stage at random.
- **Success:** G&W grabs the ledge or lands safely (edgeguard version: G&W loses the
  stock).
- **Fail:** The opposite.
- **Variations:** Battlefield (hard sweetspot) versus Dream Land (easy).
- **Data needed:** Up B height and drift, special fall landing lag 6, ledge grab boxes.

### Bucket versus lasers

- **id:** `mr-game-and-watch-bucket-lasers`
- **Goal:** Fill the bucket safely and land the spill.
- **Player:** Mr. Game & Watch
- **CPU:** Falco, Fox (also Samus, Dr. Mario)
- **Setup:** Final Destination, full-stage distance, empty bucket.
- **CPU behaviour:** Fires lasers; at random intervals approaches and punishes a bucket
  loop if in range.
- **Success:** Three projectiles absorbed with no hit taken, then the oil spill connects.
- **Fail:** Hit during the 33-frame loop, or spill whiffs/is shielded.
- **Variations:** Start with two stored; aerial bucket.
- **Data needed:** Absorb start frame 5, loop 33 frames, end lag 12, spill frames 2-37,
  multiplier 1.5x + 5.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlGw.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/mr-game-and-watch.json`](../framedata/mr-game-and-watch.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 4-6 | 3 | 83/85 | 0 | 100 | 20 |  | 17 | 16 | 3 | -8 |  |
| Rapid jab start | `rapid_jab_start` | - | - | - | - | - | - | - | 3 | - | - | - |  |
| Rapid jab loop | `rapid_jab_loop` | 7-9 | 3 | 70 | 0 | 100 | 18 |  | 11 | - | 3 | -1 |  |
| Rapid jab end | `rapid_jab_end` | - | - | - | - | - | - | - | 8 | - | - | - |  |
| Dash attack | `dash_attack` | 6-29 | 9 | 120 | 70 | 30 | - |  | 37 | - | 6 | -25 |  |
| Up tilt | `utilt` | 9-29 | 9 | 100 | 30 | 127/125/123 | - |  | 29 | - | 6 | -14 |  |
| Down tilt | `dtilt` | 6-13 | 12/9 | 85/Sakurai | 65/80 | 100/40 | - |  | 29 | 26 | 7 | -12 |  |
| Forward smash | `fsmash` | 13-16 | 18/14 | 55/Sakurai | 44 | 100 | - | fire | 44 | 42 | 10 | -18 | charge hold frame 8 |
|  |  | 17-33 | 6 | 55/Sakurai | 44 | 100 | - | fire |  |  | 4 | -20 |  |
| Up smash | `usmash` | 24-28 | 18 | 83 | 40 | 96 | - |  | 44 | 40 | 10 | -5 | charge hold frame 18; partly intangible 24-28 (1 bone) |
| Down smash | `dsmash` | 15-19 | 10/16 | 20/80 | 10/60 | 50/90 | - |  | 34 | - | 9 | -10 | charge hold frame 8 |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 20-29 | 16 | Sakurai | 20 | 100 | - |  | 44 | - | 9 | 15 | 15 | <3, >44 | -6 | cannot be L-cancelled |
| Forward air | `fair` | 10-12 | 16 | Sakurai | 30 | 80 | - |  | 44 | - | 9 | 25 | 12 | <3, >44 | -3 |  |
|  |  | 13-32 | 6 | Sakurai | 10 | 80 | - |  |  |  | 4 |  |  |  | -8 |  |
| Back air | `bair` | 10-12, 13-15, 16-18, 19-21 | 5 | 68 | 60 | 60 | - | slash | 39 | - | 4 | 18 | 18 | <10, >39 | -14 | cannot be L-cancelled |
| Up air | `uair` | 7-16 | 7 | 94 | 12 | 100 | - |  | 39 | - | 5 | 15 | 15 | <7, >39 | -10 | cannot be L-cancelled |
|  |  | 21-22 | 9 | 90 | 55 | 100 | - |  |  |  | 6 |  |  |  | -9 |  |
| Down air | `dair` | 12 | 14/13 | 270/60 | 20 | 100 | - |  | 49 | - | 8 | 20 | 10 | <6, >49 | -2 |  |
|  |  | 13-38 | 13 | 60 | 20 | 100 | - |  |  |  | 7 |  |  |  | -3 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 11-12 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 13 | 30 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 8 | 8 | 68 | 100 | 40 | - | - | 55 | 69 |  |
| Back throw | `bthrow` | 8 | 8 | 68 | 100 | 40 | - | - | 54 | 69 |  |
| Up throw | `uthrow` | 8 | 8 | 90 | 100 | 40 | - | - | 55 | 69 |  |
| Down throw | `dthrow` | 8 | 8 | 88 | 80 | 40 | - | - | 55 | 69 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Chef, ground | `special_n` | 18-21 | 5 | 10 | 60 | 30 | - | fire | 49 | - | 4 | - |  |
| Neutral B: Chef, air | `special_air_n` | 18-21 | 5 | 10 | 60 | 30 | - | fire | 49 | - | 4 | - |  |
| Side B: Judgment (Judge), ground | `special_s` | 16-29 | 2 | Sakurai | 0 | 0 | - |  | 49 | - | 2 | - | self damage 12% on frame 16 |
| Side B: Judgment (Judge), ground | `special_s_298` | 16-29 | 4 | Sakurai | 10 | 40 | - |  | 49 | - | 3 | - |  |
| Side B: Judgment (Judge), ground | `special_s_299` | 16-29 | 6 | 140 | 45 | 50 | - |  | 49 | - | 4 | - |  |
| Side B: Judgment (Judge), ground | `special_s_300` | 16-29 | 8 | 40 | 50 | 40 | - | slash | 49 | - | 5 | - |  |
| Side B: Judgment (Judge), ground | `special_s_301` | 16-18, 19-21, 22-24, 25-27 | 3 | 75 | 30 | 80 | - | electric | 49 | - | 3 | - |  |
| Side B: Judgment (Judge), ground | `special_s_302` | 16-29 | 12 | 20 | 30 | 80 | - | fire | 49 | - | 7 | - |  |
| Side B: Judgment (Judge), ground | `special_s_303` | 16-29 | 14 | Sakurai | 30 | 50 | - |  | 49 | - | 8 | - |  |
| Side B: Judgment (Judge), ground | `special_s_304` | 16-29 | 4 | 80 | 0 | 100 | 70 | ice | 49 | - | 3 | - |  |
| Side B: Judgment (Judge), ground | `special_s_305` | 16-29 | 32 | Sakurai | 100 | 80 | - |  | 49 | - | 16 | - |  |
| Side B: Judgment (Judge), air | `special_air_s` | 16-29 | 2 | Sakurai | 0 | 0 | - |  | 49 | - | 2 | - | self damage 12% on frame 16 |
| Side B: Judgment (Judge), air | `special_air_s_307` | 16-29 | 4 | Sakurai | 10 | 40 | - |  | 49 | - | 3 | - |  |
| Side B: Judgment (Judge), air | `special_air_s_308` | 16-29 | 6 | 140 | 45 | 50 | - |  | 49 | - | 4 | - |  |
| Side B: Judgment (Judge), air | `special_air_s_309` | 16-29 | 8 | 40 | 50 | 40 | - | slash | 49 | - | 5 | - |  |
| Side B: Judgment (Judge), air | `special_air_s_310` | 16-18, 19-21, 22-24, 25-27 | 3 | 75 | 30 | 80 | - | electric | 49 | - | 3 | - |  |
| Side B: Judgment (Judge), air | `special_air_s_311` | 16-29 | 12 | 20 | 30 | 80 | - | fire | 49 | - | 7 | - |  |
| Side B: Judgment (Judge), air | `special_air_s_312` | 16-29 | 14 | Sakurai | 30 | 50 | - |  | 49 | - | 8 | - |  |
| Side B: Judgment (Judge), air | `special_air_s_313` | 16-29 | 4 | 80 | 0 | 100 | 70 | ice | 49 | - | 3 | - |  |
| Side B: Judgment (Judge), air | `special_air_s_314` | 16-29 | 32 | Sakurai | 100 | 80 | - |  | 49 | - | 16 | - |  |
| Up B: Fire, ground | `special_hi` | 1-37 | 6 | 80 | 50 | 80 | - |  | 39 | - | 4 | - |  |
| Up B: Fire, air | `special_air_hi` | 1-37 | 6 | 80 | 50 | 80 | - |  | 39 | - | 4 | - |  |
| Down B: Oil Panic (bucket), ground | `special_lw` | - | - | - | - | - | - | - | 49 | - | - | - |  |
| Down B: Oil Panic (bucket), ground, Catch | `special_lw_catch` | - | - | - | - | - | - | - | 24 | - | - | - | intangible 1-24 |
| Down B: Oil Panic (bucket), ground, Shoot | `special_lw_shoot` | 2-10, 11-22, 23-37 | 1 | Sakurai | 30 | 80 | - |  | 49 | - | 2 | - |  |
| Down B: Oil Panic (bucket), air | `special_air_lw` | - | - | - | - | - | - | - | 49 | - | - | - |  |
| Down B: Oil Panic (bucket), air, Catch | `special_air_lw_catch` | - | - | - | - | - | - | - | 24 | - | - | - | intangible 1-24 |
| Down B: Oil Panic (bucket), air, Shoot | `special_air_lw_shoot` | 2-10, 11-22, 23-37 | 1 | Sakurai | 40 | 100 | - |  | 49 | - | 2 | - |  |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-12 | - | 32 | 20 |  |
| Roll forward | `roll_forward` | intangible 4-19 | - | 35 | - |  |
| Roll backward | `roll_backward` | intangible 4-19 | - | 35 | - |  |
| Air dodge | `airdodge` | intangible 4-29 | - | 49 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-34 | 20-21, 33-34 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-21 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-22 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-33 | 20-21, 32-33 (6%) | 49 | - |  |
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
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 34 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-53 | 55-59 (8/6%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-39 | 42-47 (8/6%) | 55 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-56 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-27 | - | 49 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-17 | - | 17 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 30 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-12 | - | 12 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 25 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Up B | jump cancel | 2 | `special_hi` |
| Shield grab | direct | 7 | `grab` |
| Up air | jump | 11 | `uair` |
| Forward air | jump | 14 | `fair` |
| Back air | jump | 14 | `bair` |
| Down air | jump | 16 | `dair` |
| Neutral air | jump | 24 | `nair` |
| Up smash | jump cancel | 25 | `usmash` |
| Spot dodge | direct | intangible 2-12 of 32 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 35 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 35 | `roll_backward` |
| Wavedash | jump | actionable on frame 16 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Mr. Game & Watch indexed by [The Melee Library](https://www.meleelibrary.com/#mr-game-and-watch) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Game & Watch Techs Guide](https://www.youtube.com/watch?v=VqAIBSJwGvM&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=10&t=0s) | Third Chair | Video guide on performing useful Game & Watch tech in 2020. |
| [Game & Watch Melee Chaingrab Guide](https://www.youtube.com/watch?v=zF2bjA2qJ6E&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=13&t=0s) | Third Chair |  |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Mr. Game & Watch (SSBM): https://www.ssbwiki.com/Mr._Game_%26_Watch_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Mr._Game_%26_Watch_(SSBM)/Neutral_aerial ,
  /Forward_aerial , /Down_aerial , /Down_tilt , /Up_tilt , /Grab , /Up_throw ,
  /Down_throw , /Up_special , /Side_special , /Down_special
- SSBWiki, Judge: https://www.ssbwiki.com/Judge
- SSBWiki, Oil Panic: https://www.ssbwiki.com/Oil_Panic
- SSBWiki, Chef: https://www.ssbwiki.com/Chef
- SSBWiki, L-canceling: https://www.ssbwiki.com/L-canceling
- SSBWiki, Chain grab: https://www.ssbwiki.com/Chain_grab
- SSBWiki, Ness (SSBM) and Young Link (SSBM) (cross-references):
  https://www.ssbwiki.com/Ness_(SSBM) , https://www.ssbwiki.com/Young_Link_(SSBM)
- SSBWiki, List of SSBM tier lists (NTSC): https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Smashboards, "Flatten The Opposition: A Game and Watch Guide" (move data, combo list
  credited to Qerb's combo guide, bucket list, dodge data), via web.archive.org:
  https://smashboards.com/threads/flatten-the-opposition-a-game-and-watch-guide.346291/
- Frame data dump: `fd/json/Game & Watch.json`
- Not readable: Melee Library cards "2020 Game & Watch Techs Guide" and "Game & Watch
  Melee Chaingrab Guide" (videos); Smashboards "Game & Watch grab flowcharts vs spacies"
  (no archive copy found).
