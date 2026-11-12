---
schema: melee-character/v1
id: link
name: Link
aliases: [Adult Link, Hero of Time]
tier: "C- (18th of 26), 2021 tier list"
archetype: [swordie, projectile, zoner, heavy, combo-food, edgeguarder]
related: [young-link]
summary: Link controls space with boomerang and bombs, converts a projectile hit or a long-range grab into a kill confirm (down throw into up B, bomb into down air), and finishes with a semi-spiking grounded up B at the ledge.
key_tech: [bomb-jump, z-drop-bomb-recovery, hookshot-wall-grapple, dthrow-spin-attack, spin-attack-edgeguard, up-b-out-of-shield, bomb-kill-confirm, boomerang-angling, goron-roll, acid-drop, nair-edgeguard]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlLk.dat
framedata: ../framedata/link.json
code: src/melee/ft/kinds/ftLink
specials:
  neutral_b: "Bow"
  side_b: "Boomerang"
  up_b: "Spin Attack"
  down_b: "Bomb"
attributes:
  weight: 104
  gravity: 0.11
  fall_speed: 2.13
  fast_fall_speed: 3
  jump_squat: 6
  jumps: 2
  walk_speed: 1.2
  dash_speed: 1.3
  run_speed: 1.3
  traction: 0.1
  air_speed: 1
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [6, 20, 5]
  jab2: [7, 18, 3]
  jab3: [7, 33, 6]
  rapid_jab_start: [null, 8, 0]
  rapid_jab_loop: [2, 35, 1]
  rapid_jab_end: [null, 11, 0]
  dash_attack: [7, 40, 12]
  utilt: [9, 30, 9]
  dtilt: [14, 32, 11]
  usmash: [11, 52, 10]
  dsmash: [9, 42, 17]
  nair: [4, 36, 11]
  fair: [14, 56, 13]
  bair: [6, 30, 7]
  uair: [5, 60, 16]
  dair: [13, 80, 22]
  grab: [11, 86, 0]
  dash_grab: [12, 96, 0]
  pummel: [10, 26, 3]
  fthrow: [12, 40, 3]
  bthrow: [11, 40, 3]
  uthrow: [26, 50, 2]
  dthrow: [22, 50, 4]
  special_n_start: [null, 60, 0]
  special_n_loop: [null, 28, 0]
  special_n_end: [null, 25, 0]
  special_air_n_start: [null, 60, 0]
  special_air_n_loop: [null, 28, 0]
  special_air_n_end: [null, 25, 0]
  special_s1: [null, 46, 0]
  special_s2: [null, 20, 0]
  special_s1_304: [null, 46, 0]
  special_air_s1: [null, 46, 0]
  special_air_s2: [null, 20, 0]
  special_air_s1_307: [null, 46, 0]
  special_hi: [8, 80, 15]
  special_air_hi: [8, 80, 6]
  special_lw: [null, 40, 0]
  special_air_lw: [null, 40, 0]
oos:  # option: frame the hitbox is out
  special_hi: 9
  nair: 10
  uair: 11
  grab: 11
  bair: 12
  usmash: 12
  dair: 19
  fair: 20
resources: 6
# generated: end
---

# Link

<!-- GENERATED:attributes -->
## Attributes

Read from `PlLk.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 104 |
| Gravity | 0.11 |
| Terminal fall speed | 2.13 |
| Fast-fall speed | 3 |
| Jump squat (frames before airborne) | 6 |
| Full hop / short hop initial Y speed | 2.5 / 1.5 |
| Air jump Y multiplier | 0.88 |
| Jumps | 2 |
| Walk max speed | 1.2 |
| Dash initial speed / run max speed | 1.3 / 1.3 |
| Ground friction (traction) | 0.1 |
| Air max horizontal speed | 1 |
| Air acceleration (base + stick) | 0.02 + 0.04 |
| Air friction | 0.005 |
| Normal landing lag | 4 |
| Shield size | 11.625 |
<!-- /GENERATED:attributes -->

## Overview

Link is a heavy, fairly fast-falling swordsman with three projectiles (bow, boomerang, bombs)
and the second longest grab in the game [wiki:Link_(SSBM)]. He is weight 104 with fall speed
2.13 and a 6-frame jump squat (the grounded frames before a jump leaves the floor)
[wiki:Link_(SSBM)], so his aerials start late and he is easy to combo. He wins neutral from
mid range: a boomerang or bomb forces the opponent to block, jump or get hit, and Link
follows the projectile with an aerial, a grab or a kill move. His punish game is built on
throws with low knockback (down throw, up throw) and on up tilt, which lead to up air, down
air or the grounded up B (Spin Attack). In NTSC the late hit of grounded Spin Attack is a
semi-spike (a hit that sends at a very low horizontal angle), which makes it one of the best
ledge-covering moves in the game [wiki:Link_(SSBM)]. He loses when faster characters get past
the projectiles: his out-of-shield options are slow, his grab cannot catch airborne
opponents at range, and Fox, Falco and Sheik all have easy, long combos on him
[wiki:Link_(SSBM)]. Execution difficulty is moderate for the basics and high for the bomb
recovery and bomb movement techniques.

## Strengths and weaknesses

- **Strengths:**
  - Disjointed sword with one large hitbox per swing; no tipper/sourspot management
    [wiki:Link_(SSBM)].
  - Boomerang and bombs start combos, extend them and cover his own approach; the Hylian
    Shield passively blocks projectiles while he stands or crouches [wiki:Link_(SSBM)].
  - Reliable kill confirms: dthrow into grounded up B, bomb into dair/fair/fsmash, up throw
    into dair on fastfallers [wiki:Link_(SSBM)] [lib:Grab Punishes with Link].
  - Nair hitbox stays out for the whole animation (frames 4-39) because of a scripting
    error, so it is an excellent edgeguard move [wiki:Link_(SSBM)/Neutral_aerial].
  - Heavy and fast falling, so he survives vertical kill moves for a long time
    [wiki:Link_(SSBM)].
  - Recovery has many layers: double jump, aerial up B, hookshot wall grapple, bomb jump.
- **Weaknesses:**
  - Slow ground game: dash speed 1.3, poor dash dance, short wavedash [wiki:Link_(SSBM)].
  - 6-frame jump squat delays every aerial and every out-of-shield aerial
    [wiki:Link_(SSBM)].
  - Poor out of shield; struggles against Fox and Falco shield pressure [wiki:Link_(SSBM)].
  - Combo food: called arguably the easiest character for Fox to waveshine and for Falco
    to shine into dair, and one of the easiest for Sheik to chain grab [wiki:Link_(SSBM)].
  - Grab and dtilt are laggy (standing grab lasts 84 frames, dash grab 94 [fd]); a whiff
    is a full punish.
  - Fast aerials (nair, bair) lose to crouch cancel, and dash attack is weak against
    opponents holding down [wiki:Link_(SSBM)].
  - Aerial up B recovery is predictable [wiki:Link_(SSBM)].

## Character tech

### Bomb jump (Spin Attack bomb recovery)

- **id:** `bomb-jump`
- **What:** Link throws a bomb upward while recovering, then hits it with his aerial up B.
  The explosion damages Link, which takes him out of special fall (the helpless state after
  up B) and lets him up B or hookshot again [wiki:Bomb_recovery].
- **Inputs:** Offstage with a bomb in hand: throw the bomb straight up, drift under it,
  aerial up B so the sword hits the bomb, then up B again (or grab-air the wall).
- **Timing:** Down B takes 39 frames and the bomb appears on frame 16
  [wiki:Link_(SSBM)/Down_special], so the bomb must usually be pulled before or right
  after being hit offstage. The aerial up B must be unstaled: if a grounded Spin Attack hit
  an opponent earlier in the stock, the staled aerial version does too little damage to
  detonate the bomb [wiki:Bomb_recovery] [wiki:Bomb_(Link)].
- **Used for:** Getting back from distances where one up B is not enough. Only Link can do
  this version; Young Link cannot [wiki:Bomb_recovery].
- **Common errors:** Bomb thrown too far ahead so the up B misses it; up B staled so the
  bomb does not explode; bomb explodes in hand before the throw (fuse ran out).
- **Drill idea:** Start Link offstage at a fixed distance beyond single up B range with a
  bomb in hand; success is grabbing the ledge or landing on stage.

### Z-drop bomb recovery

- **id:** `z-drop-bomb-recovery`
- **What:** Link drops a bomb with Z in the air and attacks it (or lets it explode on him).
  The blast gives a burst toward the stage and refreshes up B [wiki:Bomb_recovery].
- **Inputs:** Airborne with a bomb: press Z to drop it, wait a moment, hit it with an
  aerial (bair and nair are the usual choices) while holding DI (directional influence,
  holding a direction to bend the launch angle) toward the stage. A third variant: pull a
  bomb right after hitstun ends and up B so the bomb explodes in hand at the end of the
  up B [wiki:Bomb_recovery].
- **Timing:** Bombs start launching Link into tumble at about 34% [wiki:Bomb_recovery];
  below that the explosion barely moves him. From tumble next to a wall he can also wall
  tech and wall-jump-tech for more height [wiki:Bomb_recovery].
- **Used for:** Extra horizontal distance, and a second up B when the Spin Attack method is
  not available.
- **Common errors:** Wrong DI sends Link away from the stage; attacking too early so the
  aerial misses the falling bomb.
- **Drill idea:** Link offstage at 40%+ with a bomb; success is reaching the ledge after
  one bomb explosion plus one up B.

### Hookshot wall grapple

- **id:** `hookshot-wall-grapple`
- **What:** Link's air grab (Z in the air, or shield + A) fires the hookshot, which latches
  onto any wall surface, not only the ledge. Link can hang, reel up with A, and still has
  his double jump and up B afterwards [wiki:Wall_grapple].
- **Inputs:** Face the wall, press Z (or L/R + A) at grapple range. Using L/R + A after an
  upward air dodge carries the air dodge's momentum into the grapple [wiki:Wall_grapple].
  Press A to climb, or jump / up B off the chain.
- **Timing:** One wall grapple per airborne period; a second attempt gives nair or an air
  dodge. Too close or too far and the hookshot misses and Link goes helpless. Hanging too
  long drops Link in tumble and removes his double jump [wiki:Wall_grapple].
- **Used for:** Recovering below the ledge where grounded attacks cannot reach, stalling to
  wait out ledge invincibility, mixing the timing of the final ledge grab
  [wiki:Link_(SSBM)].
- **Common errors:** Facing away from the stage (the hookshot only fires forward);
  grappling while the opponent holds the ledge and then having no safe way up.
- **Drill idea:** Link below ledge height facing the stage wall; success is latching, then
  reaching the ledge or stage while a CPU swings at the normal up B path.

### Down throw into Spin Attack

- **id:** `dthrow-spin-attack`
- **What:** Dthrow pops the opponent up a short, fixed-feeling distance (90 degrees, base
  knockback 60, growth 50 [wiki:Link_(SSBM)/Down_throw]) and Link acts in time to hit
  them with grounded up B before they land or jump.
- **Inputs:** Grab, dthrow, then up B on the first actionable frame. If the opponent DIs
  behind Link, turn around first, because the up B reaches the back later
  [lib:Grab Punishes with Link].
- **Timing:** Grounded up B hits on frame 8 [fd]. The clean hit does 15% at the Sakurai
  angle (361) with base 32, growth 95 [fd]. Works on Fox/Falco from about 126% and on
  Sheik at about 70-100% (author's estimates, pre-throw percent)
  [lib:Grab Punishes with Link].
- **Used for:** Link's most reliable kill confirm on fastfallers and mid-weights
  [wiki:Link_(SSBM)].
- **Common errors:** Not turning around on DI behind; using it too early so the opponent
  lands and shields; staling up B (which also breaks the bomb jump).
- **Drill idea:** CPU Fox at 130% grabbed at centre stage with random DI (in, away, none);
  success is the clean up B connecting within the true-combo window.

### Spin Attack edgeguard

- **id:** `spin-attack-edgeguard`
- **What:** The late hit of grounded up B does 5% at angle 0 with base knockback 60 [fd],
  a flat semi-spike. On a recovering opponent near the ledge it sends them out and down
  with no height. NTSC only; PAL changed the angle to 361 [wiki:Link_(SSBM)/Up_special].
- **Inputs:** Stand near the ledge, up B so the late portion overlaps the opponent's
  arrival.
- **Timing:** Hitbox starts frame 8; the late hit runs until frame 41 of a 79-frame
  animation [wiki:Link_(SSBM)/Up_special] [fd]. The move has transcendent priority (it
  does not clank) [wiki:Link_(SSBM)].
- **Used for:** Covering recoveries that must pass the ledge at stage height: Fox/Falco
  side B and up B, Marth and Sheik up B, Captain Falcon up B.
- **Common errors:** Starting too late (38 frames of lag after the last hitbox frame);
  hitting with the clean hit instead, which sends at a normal angle.
- **Drill idea:** CPU Fox recovers with side B or up B aimed at the ledge or stage;
  success is a late-hit up B connecting and the CPU not making it back.

### Up B out of shield

- **id:** `up-b-out-of-shield`
- **What:** Up B can be input directly from shield (it cancels the jump), so Link gets a
  frame 8 hit [fd] that covers both sides without his 6-frame jump squat.
- **Inputs:** While in shield after shield stun ends: up + B.
- **Timing:** Hits frame 8 [fd]. For comparison, nair out of shield needs 6 frames of jump
  squat [wiki:Link_(SSBM)] plus nair's frame 4 hitbox [fd], so it hits on frame 10 at the
  earliest; up smash out of shield hits frame 11 [fd] and only covers above
  [wiki:Link_(SSBM)]. The wiki rates Link's up B out of shield as slow next to
  [Bowser](bowser.md)'s and [Samus](samus.md)'s [wiki:Link_(SSBM)].
- **Used for:** Punishing unsafe aerials and smash attacks on shield, and as a kill move at
  high percent.
- **Common errors:** Using it against well-spaced or fast pressure (Fox/Falco shine), where
  it is beaten or blocked and Link is stuck in the rest of a 79-frame move.
- **Drill idea:** CPU Marth fsmashes Link's shield at varied spacing; success is up B out
  of shield hitting before the CPU can shield.

### Bomb kill confirm

- **id:** `bomb-kill-confirm`
- **What:** A thrown bomb pops the opponent up with flame hitstun (explosion: 70 degrees,
  base 60 [wiki:Link_(SSBM)/Down_special]), long enough to land dair, fair, uair, fsmash
  or up B [wiki:Link_(SSBM)].
- **Inputs:** Pull a bomb (down B), approach or wait, throw with A or the C-stick, then
  jump and aerial, or dash and grounded up B.
- **Timing:** Bomb pull is 39 frames, bomb in hand from frame 16
  [wiki:Link_(SSBM)/Down_special]. Dair hits frame 13 and stays out until frame 64 [fd].
- **Used for:** Killing floaties ([Peach](peach.md), [Jigglypuff](jigglypuff.md)) that
  dthrow up B does not kill; "bomb into dair/uair are easy finishers" on Peach
  [lib:Link vs Peach].
- **Common errors:** Throwing from too close and being caught in the blast; pulling a bomb
  without boomerang cover and getting hit during the 39-frame pull.
- **Drill idea:** Link holds a bomb, CPU Peach floats at mid range at 90%; success is bomb
  hit followed by dair within the hitstun window.

### Boomerang angling

- **id:** `boomerang-angling`
- **What:** Side B throws a boomerang that can be aimed up or down with the stick and
  thrown farther with a smash input; it hits on the way out and on the way back
  [wiki:Boomerang].
- **Inputs:** Side B; hold up/down during the throw to angle; tap the stick for the long
  throw. Catching it on return plays a catch animation unless Link is busy.
- **Timing:** The boomerang leaves the hand on frame 27 of a 45-frame animation; a normal
  throw is out for frames 27-167, a smash throw 27-197
  [wiki:Link_(SSBM)/Side_special]. Hitbox data on that page: 8% clean, 6% after the first
  few frames, 3% returning (the character page's summary table lists larger numbers).
  Only one boomerang can be out; a second side B is an empty animation [wiki:Boomerang].
- **Used for:** Covering bomb pulls, cutting off Peach's float and jumps
  [lib:Link vs Peach], interrupting recoveries (it destroys [Ness](ness.md)'s PK Thunder
  without damage [wiki:Ness_(SSBM)]), and returning hits that set up kill moves.
- **Common errors:** Throwing at close range (27 frames of startup); being hit by the
  catch animation timing; forgetting the boomerang is still out and getting the empty
  throw.
- **Drill idea:** CPU approaches from full-screen with a jump or dash at random; success
  is the boomerang hitting and Link landing a follow-up before the CPU acts.

### Goron roll

- **id:** `goron-roll`
- **What:** Link throws a bomb at his own feet and techs the knockback, giving a tech roll
  on demand that is quicker than a normal roll [wiki:Bomb_(Link)].
- **Inputs:** Standing with a bomb: C-stick down (throw down) and at the same time press
  L/R with the control stick left or right to tech roll [wiki:Bomb_(Link)].
- **Timing:** Only possible once the bomb sends Link into tumble, at about 34%+ for Link
  [wiki:Bomb_(Link)]. Link's longest roll is the forward-facing one.
- **Used for:** Movement mixup, escaping pressure, closing distance with tech
  invincibility. The wiki calls it situational with few follow-ups [wiki:Link_(SSBM)].
- **Common errors:** Below the tumble threshold Link just takes damage in place; missed
  tech leaves him lying down next to the opponent.
- **Drill idea:** Link at 40% with a bomb, CPU swings on a timer; success is a tech roll
  through or away from the attack with no hit taken other than the bomb.

### Acid drop (fusedash)

- **id:** `acid-drop`
- **What:** A Z-dropped bomb combined with a [wavedash](../techniques/wavedash.md) or
  [waveland](../techniques/waveland.md) so the bomb's contact hitbox hits the opponent
  while Link slides; it can be looped and works as a pseudo waveshine and an out-of-shield
  option [wiki:Bomb_(Link)].
- **Inputs:** With a bomb: jump, Z-drop, air dodge diagonally into the ground.
- **Timing:** Unknown (no frame data found). Z-drop is a very short commitment compared to
  a throw.
- **Used for:** Getting a hitbox out while moving; escaping shield pressure with a bomb in
  hand.
- **Common errors:** Air dodging before the drop (Z with shield held becomes an air dodge
  or air grab instead of a drop).
- **Drill idea:** Link in shield with a bomb, CPU Fox does aerial into shine on shield;
  success is the dropped bomb hitting the CPU.

### Lingering nair edgeguard

- **id:** `nair-edgeguard`
- **What:** Link's nair is active from frame 4 to the end of the animation (frame 39)
  because the late hitbox is never cleared [wiki:Link_(SSBM)/Neutral_aerial]. Link jumps
  off stage and holds it in the opponent's path.
- **Inputs:** Run off or jump off, nair early, drift into the recovery line, double jump
  and up B or hookshot back.
- **Timing:** Clean hit frames 4-5 (11% foot), late hit 7% for the rest; lands with 15
  frames of lag, 7 with an [L-cancel](../techniques/l-cancel.md) [fd]
  [wiki:Link_(SSBM)/Neutral_aerial].
- **Used for:** Edgeguarding characters whose recovery has no strong hitbox in front, and
  as an escape/landing option because it comes out fast.
- **Common errors:** Going too deep to return; getting crouch cancelled when using the weak
  hit on stage [wiki:Link_(SSBM)].
- **Drill idea:** CPU Sheik or Marth recovers from mid height; success is nair connecting
  offstage and Link returning to stage.

Other documented but niche bomb tech: bombchu (hitting a planted bomb with a hit under 6%
makes it slide), bomb rocket, bomb launching [wiki:Bomb_(Link)]. The chain dance, ghost
arrow and boomerang superjump glitches do not work in version 1.02 [wiki:Chain_dance].

## Neutral game

- Stay at boomerang range. The usual pattern is boomerang first, then pull a bomb behind
  it, then throw the bomb or approach with it in hand [lib:Link vs Peach].
- Sword pokes: spaced fair (first hit 13%, frame 14 [fd]; done as low as possible in a
  short hop it is roughly even on shield [wiki:Link_(SSBM)]), ftilt (frame 16, 13-15%
  [fd]), dtilt (frame 14 [fd]), jab.
- Up tilt (frames 9-15, 9% [fd]) is the anti-air and main combo starter
  [wiki:Link_(SSBM)].
- Dash attack (frame 7 [fd]) pops grounded opponents up at mid percent and can chain into
  another dash attack or up tilt, but loses to opponents holding down [wiki:Link_(SSBM)].
- Grab is long but slow and cannot grab airborne opponents with the far hitbox
  [wiki:Link_(SSBM)]; use it as a whiff punish or shield grab, not a raw approach.
- Arrows are slow and low reward; mainly for edgeguarding and forcing a jump
  [wiki:Link_(SSBM)].
- Link wants: the opponent above him or offstage, platforms to throw opponents onto, and
  Final Destination against characters who cannot get around projectiles
  [wiki:Link_(SSBM)].

## Punish game

Link's throws are the core. Up throw (90 degrees, base 24, growth 230; throw releases on
frame 27 of 49 [wiki:Link_(SSBM)/Up_throw]) and down throw (base 60, growth 50
[wiki:Link_(SSBM)/Down_throw]) both leave the opponent close. Which one to use depends on
percent and fall speed. The percent windows below are one experienced player's estimates
("rough numbers ... off the top of my head"), measured before the throw
[lib:Grab Punishes with Link]; treat them as typical, not frame-tested.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| dthrow | Fox, Falco | 0-16% | tech chase | uthrow does not knock down this low | [lib:Grab Punishes with Link] |
| uthrow | Fox, Falco | 17-35% | dsmash (utilt if no DI) | hold up-forward and walk in | [lib:Grab Punishes with Link] |
| uthrow | Fox, Falco | 36-50% | dash attack or nair (utilt if no DI) | | [lib:Grab Punishes with Link] |
| uthrow | Fox, Falco | 51-95% | running uair | short hop low in range, full hop high | [lib:Grab Punishes with Link] |
| uthrow | Fox, Falco | 96-105% | running full hop dair | kills on Final Destination / Pokemon Stadium | [lib:Grab Punishes with Link] |
| uthrow | Fox, Falco | 106-125% | double jump fair (uair if no DI) | sets up edgeguard | [lib:Grab Punishes with Link] |
| dthrow | Fox, Falco | 126%+ | up B | turn around if DI behind | [lib:Grab Punishes with Link] |
| throws as above | Captain Falcon | add about 10% to each window | same | uthrow dair may not connect | [lib:Grab Punishes with Link] |
| bair | Captain Falcon | up to roughly 40-50% | grab | not if he crouch cancels | [lib:Grab Punishes with Link] |
| dthrow | Peach | 0-50% | utilt, then uair or fair | DI-dependent | [lib:Grab Punishes with Link] |
| dthrow | Peach | 41-95% | uair | | [lib:Grab Punishes with Link] |
| dthrow | Peach, Marth | 96-105% | dair | often a kill | [lib:Grab Punishes with Link] |
| dthrow | Peach, Marth | 106%+ | uair (kills around 130-135%) or nair | | [lib:Grab Punishes with Link] |
| dthrow | Marth | 0-50% | utilt, or turn-around dsmash on DI behind | | [lib:Grab Punishes with Link] |
| dthrow | Marth | 51-95% | uair, or fair/nair toward the ledge | | [lib:Grab Punishes with Link] |
| uthrow | Sheik | 30-70% | uair | not always a true combo | [lib:Grab Punishes with Link] |
| dthrow | Sheik | 70-100% | up B | may be escapable with upward DI | [lib:Grab Punishes with Link] |
| utilt | most | mid percent | uair, dair | main non-grab starter | [wiki:Link_(SSBM)] |
| bomb or boomerang hit | most | high percent | dair, fair, fsmash, up B | | [wiki:Link_(SSBM)] |
| late nair | most | high percent | up B | | [wiki:Link_(SSBM)/Neutral_aerial] |

### Chain grabs and tech chases

No true chain grab of note in general. Against [Captain Falcon](captain-falcon.md) at low
percent his tech is slow enough that Link can regrab off dthrow the way Sheik does, but a
miss is very punishable [lib:Grab Punishes with Link]. Link's real strength is the
[tech chase](../techniques/tech-chase.md): dsmash hits front (frames 9-11) then back
(frames 21-23) [fd] and so covers several tech options at once [wiki:Link_(SSBM)];
grounded up B and dair are the kill options on a read. Throwing fastfallers onto a platform
(uthrow at 17-35% knocks spacies down onto one [lib:Grab Punishes with Link]) forces a
tech on a small surface.

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| dair (clean, 22%) | most of the cast | about 80-100% | grounded or low target; from uthrow/dthrow/utilt/bomb | [wiki:Link_(SSBM)/Down_aerial] |
| uair (clean, 16%) | most | about 120%; about 130-135% from dthrow on Peach/Marth | vertical | [wiki:Link_(SSBM)] [lib:Grab Punishes with Link] |
| dthrow into up B | Fox, Falco | 126%+ | typical DI | [lib:Grab Punishes with Link] |
| grounded up B late hit | recovering opponents | any percent offstage | NTSC semi-spike at the ledge | [wiki:Link_(SSBM)/Up_special] |
| fair first hit (13%) | most | Unknown | used after uthrow on fastfallers at 106-125% | [lib:Grab Punishes with Link] |
| fsmash second hit (18-20%) | most | Unknown | second hit rarely links above about 30% | [wiki:Link_(SSBM)] |

- Edgeguards: lingering nair offstage, late-hit up B at the ledge, bombs and boomerang
  thrown at the recovery path so Link keeps the stage, arrows at long range.
- Dtilt's inner hitbox (angle 280 [fd]) meteor smashes an opponent hanging on or reaching
  for the ledge; situational [wiki:Link_(SSBM)].
- Bomb into dair or uair is the standard finisher on floaties [lib:Link vs Peach].

## Recovery

- **Options:**
  - Double jump (height 20.9 units [wiki:Link_(SSBM)]).
  - Aerial up B: five hits, frames 8-50 of 79 [fd]; rises and covers above Link; can grab
    the ledge backwards during the animation [wiki:Link_(SSBM)].
  - Hookshot [wall grapple](#hookshot-wall-grapple): attaches to any wall; double jump and
    up B remain available afterwards [wiki:Wall_grapple].
  - Air dodge into hookshot for extra distance [wiki:Hookshot].
  - Bomb jump / Z-drop bomb for a second up B [wiki:Bomb_recovery].
- **Mixups:** High with drift and double jump; straight to the ledge with up B; low to the
  wall with hookshot and then choose when to climb; bomb or boomerang thrown at the ledge
  first to push the edgeguarder away [lib:Link vs Peach] [wiki:Link_(SSBM)].
- **Weaknesses:** Up B path is slow and predictable [wiki:Link_(SSBM)]. A missed hookshot
  leaves Link helpless [wiki:Wall_grapple]. If the ledge is held (edgehog) while Link hangs
  from the chain he has few safe ways up. Being heavy and fast falling, he does not get
  much horizontal drift from low percent hits.

### Edgeguarding Link

- Hold the ledge with invincibility while he up Bs to it: aerial up B gains little height
  and he lands in lag on stage.
- When he hangs on the hookshot, wait: the chain drops him if he hangs too long and takes
  his double jump if unused [wiki:Wall_grapple]. Then cover the up B.
- Hit him out of the bomb pull (39 frames [wiki:Link_(SSBM)/Down_special]) before the
  bomb jump starts, or bait the bomb jump and hit the second up B.
- Characters with strong offstage aerials (Marth fair/dair, Sheik fair/bair, Fox
  bair/shine) go out and hit him before the up B; its multi-hit sword covers above and
  beside him more than below.
- Do not stand at the ledge in range of a returning boomerang or a thrown bomb.

## Defense and out of shield

- Out of shield: up B hits frame 8 [fd] and covers both sides; up smash hits frame 11 [fd]
  but only above and can be SDI'd (smash directional influence) out of
  [wiki:Link_(SSBM)]; nair needs the 6-frame jump squat first; shield grab is frame 10
  [fd] with long range but whiffs on airborne opponents at the tip [wiki:Link_(SSBM)].
  The wiki summary: among the worst tools in the game against shield pressure, especially
  from Fox and Falco [wiki:Link_(SSBM)].
- [Crouch cancel](../techniques/crouch-cancel.md): useful at low percent because Link is
  heavy; one Link player recommends crouch cancel into jab against spacie aerials when
  their dair will not reach, and SDI sideways when it will [lib:Optimizing Link].
- [Shield drop](../techniques/shield-drop.md) uair from a platform is rated very highly
  by the same player [lib:Optimizing Link].
- Combo escapes: nair (frame 4 [fd]) is his only fast move in the air, so opponents
  expect it [wiki:Link_(SSBM)]. Otherwise DI, SDI and teching.
- With a bomb in hand: acid drop or a thrown bomb out of shield.

## As the training dummy

- Weight 104 (6th-7th heaviest), fall speed 2.13, fast-fall speed 3.0
  [wiki:Link_(SSBM)]: a heavy semi-fastfaller. Combos built for Captain Falcon or the
  space animals mostly work on him with adjusted percents.
- Chain grabbed by [Sheik](sheik.md)'s down throw (the wiki lists Link among the
  characters she chain throws from low percent to mid or high percent depending on DI)
  [wiki:Chain_grab].
- [Fox](fox.md)'s waveshine works because Link is heavy enough to stay grounded when
  shined, and the wiki calls him arguably the easiest character to waveshine;
  [Falco](falco.md)'s shine into dair pillar is similarly easy [wiki:Link_(SSBM)].
- Tall hurtbox with a slow jump: up airs and shield pokes from above connect easily.
- Realistic CPU defence: DI away from combo throws, tech away or in place at random, use
  nair as the "get off me" option, and recover with a mix of up B to ledge and hookshot.
- Bombs put Link himself in tumble from about 34% [wiki:Bomb_recovery], relevant if the
  CPU is scripted to hold bombs.

## Matchup notes

### vs Fox

- One of Link's hardest matchups. Fox's speed gets past projectiles and his reflector
  (shine) returns them; waveshine combos are especially easy on Link, and Link's shield
  options do not answer Fox's pressure [wiki:Link_(SSBM)].
- Link's reward is real though: uthrow follow-ups at every percent and dthrow up B from
  about 126% [lib:Grab Punishes with Link]; late-hit up B at the ledge kills Fox's
  recovery outright.

### vs Falco

- Lasers interrupt bomb pulls, and Link's out-of-shield options are weak against Falco's
  pressure; shine into dair is easy on him [wiki:Link_(SSBM)]. Link's passive Hylian
  Shield can block projectiles while he is not acting [wiki:Link_(SSBM)].
- Falco's short recovery dies to nair, bombs and the semi-spike. Same grab windows as Fox
  [lib:Grab Punishes with Link].

### vs Sheik

- Sheik chain grabs Link [wiki:Chain_grab] and edgeguards his up B with ease.
- Link's punishes: dthrow tech chase at 0-29%, uthrow uair at 30-70%, dthrow up B at
  70-100% [lib:Grab Punishes with Link].

### vs Marth

- The matchup where Link has his best modern results: Aklo uses Link as a counterpick,
  usually for Marth, and beat Zain with him twice in 2024 [wiki:Link_(SSBM)].
- Marth has no projectile and must walk through boomerang and bombs; on Final Destination
  Link's projectile game and kill confirms are strongest [wiki:Link_(SSBM)].
- Against Marth, do not jump after throws unless the follow-up is a true combo; use
  dthrow into utilt or turn-around dsmash at 0-50% [lib:Grab Punishes with Link].

### vs Peach

- Playable but Peach-favoured according to players on both sides [lib:Link vs Peach].
  Link stays just outside her dash attack range, throws boomerangs to cut off float, and
  pulls bombs behind them. Bomb into dair/uair finishes; Link can shield grab her down
  smash [lib:Link vs Peach].
- [Young Link](young-link.md) is the better pick for this matchup [lib:Link vs Peach].

### vs Jigglypuff and other floaties

- Link's combos on floaties are short; he relies on bombs into kill moves and uair.
  Young Link does better against floaty characters, Link better against the rest
  [wiki:Young_Link_(SSBM)].

## Drill seeds

### Down throw to Spin Attack on spacies

- **id:** `link-dthrow-up-b-spacies`
- **Goal:** Land the dthrow up B kill confirm against every DI.
- **Player:** Link
- **CPU:** Fox, Falco (Captain Falcon with about +10%)
- **Setup:** Final Destination, centre stage. Link starts holding the CPU in a grab. CPU at
  a random percent from 126% to 150%.
- **CPU behaviour:** Random DI on the throw: none, toward Link's front, behind Link, away.
  After hitstun it jumps away or shines if able.
- **Success:** Clean grounded up B (15% hit) connects before the CPU is actionable.
- **Fail:** CPU acts first, or the up B whiffs or only the 5% late hit lands.
- **Variations:** Lower the percent to find the bottom of the window; start near the ledge
  so the up B kills; require a pummel first.
- **Data needed:** Dthrow knockback and Link's throw end lag, up B hit frame 8, opponent
  weight/fall speed, hitstun formula.

### Up throw percent ladder on Fox

- **id:** `link-uthrow-ladder-fox`
- **Goal:** Pick the right up throw follow-up for the percent.
- **Player:** Link
- **CPU:** Fox, Falco
- **Setup:** Final Destination, Link holding the CPU in grab. Percent chosen at random
  from the bands 17-35, 36-50, 51-95, 96-105, 106-125.
- **CPU behaviour:** DI none or slight left/right; double jumps away as soon as hitstun
  ends.
- **Success:** The band's follow-up connects as a combo: dsmash/utilt, dash attack or
  nair, uair, full hop dair, double jump fair/uair respectively.
- **Fail:** CPU escapes, or a hit lands after the CPU was actionable.
- **Variations:** Battlefield/Yoshi's Story with a platform above (17-35% becomes a
  platform tech chase); show the percent or hide it.
- **Data needed:** Uthrow knockback (base 24, growth 230), release frame 27, Link's jump
  squat 6, aerial startup frames, Fox fall speed.

### Ledge semi-spike

- **id:** `link-spin-attack-ledge`
- **Goal:** Time the late hit of grounded up B on a recovery.
- **Player:** Link
- **CPU:** Fox, Falco, Marth, Sheik, Captain Falcon
- **Setup:** CPU offstage at 40-80% with its double jump used, at a random position
  (level with the stage, below, far). Link stands a short step from the ledge.
- **CPU behaviour:** Recovers with a random option: side B to ledge, side B onto stage,
  up B to ledge, up B high.
- **Success:** CPU is hit by the 5% angle-0 hit and loses the stock, or is forced below
  the stage and dies.
- **Fail:** CPU grabs the ledge or lands; Link is hit.
- **Variations:** Give the CPU its double jump; add platforms; require Link to first throw
  a boomerang.
- **Data needed:** Up B clean/late frame split and total 79 frames, Fox/Falco side B and
  up B travel timing, ledge sweetspot geometry.

### Bomb jump recovery

- **id:** `link-bomb-jump`
- **Goal:** Recover from beyond single up B range.
- **Player:** Link
- **CPU:** none (or a passive edgeguarder)
- **Setup:** Link launched offstage (scripted knockback) with a bomb already in hand, no
  double jump, at a distance just past up B range. Up B unstaled.
- **CPU behaviour:** None in the base version.
- **Success:** Link grabs the ledge or lands on stage.
- **Fail:** Link dies, or the bomb is not detonated by the first up B.
- **Variations:** No bomb in hand (must pull in the air); with double jump; Z-drop + bair
  variant at 40%+; CPU holds the ledge so Link must land on stage.
- **Data needed:** Bomb fuse length, bomb pull timing (16/39), aerial up B travel, tumble
  threshold about 34%.

### Hookshot recovery under pressure

- **id:** `link-hookshot-recovery`
- **Goal:** Use the wall grapple and choose a safe way up.
- **Player:** Link
- **CPU:** Marth, Sheik, Fox
- **Setup:** Battlefield or Yoshi's Story. Link offstage below ledge height facing the
  stage, with double jump.
- **CPU behaviour:** Random: stands at the ledge and dtilts/dsmashes the up B path; grabs
  the ledge and rolls up; drops off with a bair.
- **Success:** Link returns to the ledge or stage without being hit.
- **Fail:** Link is hit, misses the grapple (helpless), or hangs until the chain releases.
- **Variations:** No double jump; Final Destination (overhang); require air dodge into
  grapple.
- **Data needed:** Hookshot range and active frames, hang time limit, ledge invincibility
  of the CPU.

### Up B out of shield punish

- **id:** `link-up-b-oos`
- **Goal:** Learn which moves on shield can be punished with frame 8 up B.
- **Player:** Link
- **CPU:** Marth, Sheik, Peach, Captain Falcon
- **Setup:** Link in shield at centre stage; CPU at kill percent (120%).
- **CPU behaviour:** Random unsafe option on shield: Marth fsmash, Sheik dash attack,
  Peach dsmash, Falcon late nair; sometimes a safe spaced move as a decoy.
- **Success:** Up B hits before the CPU shields or moves, with no hit taken.
- **Fail:** Up B is shielded or whiffs; Link is hit.
- **Variations:** Compare with shield grab (frame 10) and nair out of shield; add a bomb
  in hand.
- **Data needed:** Shield stun and attacker end lag for each CPU move, up B frame 8.

### Projectile wall into confirm

- **id:** `link-boomerang-bomb-confirm`
- **Goal:** Chain boomerang cover, bomb pull, bomb hit, kill move.
- **Player:** Link
- **CPU:** Peach, Jigglypuff, Marth
- **Setup:** Final Destination, characters about two-thirds of the stage apart, CPU at
  80-110%.
- **CPU behaviour:** Approaches at random through the air (float/jumps) or on the ground
  (dash, wavedash), shields projectiles sometimes.
- **Success:** A bomb or boomerang hit is followed by dair, uair, fair or up B within the
  hitstun window.
- **Fail:** Link is hit during a bomb pull or boomerang throw.
- **Variations:** CPU percent; add platforms; CPU reflects (Fox).
- **Data needed:** Boomerang startup 27 frames, bomb pull 39 frames, bomb hitstun, dair
  startup 13.

### Tech chase with down smash

- **id:** `link-dsmash-tech-chase`
- **Goal:** Cover multiple tech options after a low-percent down throw.
- **Player:** Link
- **CPU:** Fox, Falco, Captain Falcon, Sheik
- **Setup:** Link holding CPU in grab at 0-16% (0-29% for Sheik), centre stage.
- **CPU behaviour:** After the dthrow, random: tech in place, tech toward, tech away,
  missed tech then getup attack/roll/stand.
- **Success:** A hit or regrab lands before the CPU can act out of the tech.
- **Fail:** CPU escapes or hits Link.
- **Variations:** On a platform; restrict Link to dsmash only (positioning drill) or to
  reaction grabs.
- **Data needed:** Dsmash hit frames 9-11 and 21-23, tech and tech-roll timings and
  distances for each CPU, Link's dash speed.

### Offstage nair edgeguard

- **id:** `link-nair-offstage`
- **Goal:** Use the full-duration nair offstage and get back.
- **Player:** Link
- **CPU:** Sheik, Marth, Captain Falcon, Peach
- **Setup:** CPU launched offstage at 60-100% at mid height with double jump. Link at the
  ledge.
- **CPU behaviour:** Recovers with jump then up B, mixing high and low.
- **Success:** Nair connects offstage and the CPU fails to return; Link returns.
- **Fail:** Link dies or the CPU reaches the ledge.
- **Variations:** Require hookshot return; add boomerang first.
- **Data needed:** Nair active frames 4-39, Link air speed 1.0, CPU recovery paths.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlLk.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/link.json`](../framedata/link.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 6-8 | 5 | Sakurai | 10 | 60 | - | slash | 24 | 20 | 4 | -9 |  |
| Jab 2 | `jab2` | 7-8 | 3 | Sakurai | 10 | 60 | - | slash | 22 | 18 | 3 | -7 | starts 1 frame late (included) |
| Jab 3 | `jab3` | 7-11 | 6 | Sakurai | 10 | 100 | - | slash | 50 | 33 | 4 | -21 | starts 1 frame late (included) |
| Rapid jab start | `rapid_jab_start` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Rapid jab loop | `rapid_jab_loop` | 2-3, 9-10, 16-17, 23-24, 30-31 | 1 | 0 | 15 | 40/50/60 | - | slash | 34 | - | 2 | -30 |  |
| Rapid jab end | `rapid_jab_end` | - | - | - | - | - | - | - | 10 | - | - | - |  |
| Dash attack | `dash_attack` | 7-12 | 12/11/9 | 80/70/60/90 | 10 | 100 | - | slash | 53 | 40 | 7 | -25 |  |
| Up tilt | `utilt` | 9-15 | 9 | 95/85 | 30 | 122/130/124/123 | - | slash | 29 | - | 6 | -14 |  |
| Down tilt | `dtilt` | 14-16 | 11 | 80/280 | 80 | 50 | - | slash | 39 | 32 | 6 | -11 |  |
| Up smash | `usmash` | 11-15 | 4 | 98 | 40 | 100 | 26/30/33 | slash | 60 | 52 | 3 | -37 | charge hold frame 4 |
|  |  | 26-28 | 2 | 90 | 0 | 100 | 30/33/37/40 | slash |  |  | 2 | -23 |  |
|  |  | 41-43 | 10/9 | 80/90 | 90 | 80 | - | slash |  |  | 6 | -4 |  |
| Down smash | `dsmash` | 9-11 | 13/16/17 | 75 | 26 | 90 | - | slash | 49 | 42 | 9 | -23 | charge hold frame 4 |
|  |  | 21-23 | 11/16/17 | 75 | 20 | 90 | - | slash |  |  | 9 | -11 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 4-5 | 9/11/8 | Sakurai | 15 | 100 | - |  | 39 | 36 | 6 | 15 | 7 | <4, >31 | -1 |  |
|  |  | 6-39 | 7 | Sakurai | 10 | 100 | - |  |  |  | 5 |  |  |  | -2 |  |
| Forward air | `fair` | 14-16 | 13 | Sakurai | 5 | 100 | - | slash | 55 | - | 7 | 15 | 7 | <1, >50 | +0 |  |
|  |  | 30-33 | 8 | Sakurai | 0 | 90 | - | slash |  |  | 5 |  |  |  | -2 |  |
| Back air | `bair` | 6-9 | 7 | Sakurai | 0 | 100 | - |  | 39 | 30 | 5 | 15 | 7 | <1, >28 | -2 |  |
|  |  | 18-23 | 7 | Sakurai | 15 | 100 | - |  |  |  | 5 |  |  |  | -2 |  |
| Up air | `uair` | 5-7 | 16 | 80 | 25 | 85 | - | slash | 69 | 60 | 9 | 30 | 15 | <5, >55 | -6 |  |
|  |  | 8-49 | 12 | 80 | 25 | 85 | - | slash |  |  | 7 |  |  |  | -8 |  |
| Down air | `dair` | 13-15 | 22/20 | 65 | 50/40 | 80 | - | slash | 89 | 80 | 11 | 50 | 25 | <13, >64 | -14 |  |
|  |  | 16-64 | 19 | 65 | 50/40 | 80 | - | slash |  |  | 10 |  |  |  | -15 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 11-18 | 85 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 12-18 | 95 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 10 | 25 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 6 | 3 | 55 | 25 | 110 | - | - | 16 | 39 |  |
| Back throw | `bthrow` | 6 | 3 | 130 | 24 | 110 | - | - | 16 | 39 |  |
| Up throw | `uthrow` | 6 | 2 | 90 | 24 | 230 | - | - | 27 | 49 |  |
| Down throw | `dthrow` | 6 | 4 | 90 | 60 | 50 | - | - | 28 | 49 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Bow, ground, Start | `special_n_start` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Neutral B: Bow, ground, Loop | `special_n_loop` | - | - | - | - | - | - | - | 27 | - | - | - |  |
| Neutral B: Bow, ground, End | `special_n_end` | - | - | - | - | - | - | - | 24 | - | - | - |  |
| Neutral B: Bow, air, Start | `special_air_n_start` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Neutral B: Bow, air, Loop | `special_air_n_loop` | - | - | - | - | - | - | - | 27 | - | - | - |  |
| Neutral B: Bow, air, End | `special_air_n_end` | - | - | - | - | - | - | - | 24 | - | - | - |  |
| Side B: Boomerang, ground, 1 | `special_s1` | - | - | - | - | - | - | - | 45 | - | - | - | spawns article/projectile on 5 |
| Side B: Boomerang, ground, 2 | `special_s2` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Side B: Boomerang, ground, 1 | `special_s1_304` | - | - | - | - | - | - | - | 45 | - | - | - |  |
| Side B: Boomerang, air, 1 | `special_air_s1` | - | - | - | - | - | - | - | 45 | - | - | - | spawns article/projectile on 5 |
| Side B: Boomerang, air, 2 | `special_air_s2` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Side B: Boomerang, air, 1 | `special_air_s1_307` | - | - | - | - | - | - | - | 45 | - | - | - |  |
| Up B: Spin Attack, ground | `special_hi` | 8-13 | 15 | Sakurai | 32 | 95 | - | slash | 79 | - | 8 | - |  |
|  |  | 14-41 | 5/15 | 0/Sakurai | 60/32 | 100/95 | - | slash |  |  | 8 | - |  |
| Up B: Spin Attack, air | `special_air_hi` | 8-13 | 4/6 | 90/86/80/75 | 0 | 100 | 72/68 | slash | 79 | - | 4 | - |  |
|  |  | 16-20 | 2 | 90/86/80/75 | 0 | 100 | 64/60 | slash |  |  | 2 | - |  |
|  |  | 22-27 | 2 | 90/86/80/75 | 0 | 100 | 58/55 | slash |  |  | 2 | - |  |
|  |  | 31-37 | 2 | 90/86/80/75 | 0 | 100 | 46/43 | slash |  |  | 2 | - |  |
|  |  | 46-50 | 4/6 | Sakurai | 40 | 160 | - | slash |  |  | 4 | - |  |
| Down B: Bomb, ground | `special_lw` | - | - | - | - | - | - | - | 39 | - | - | - | spawns article/projectile on 16 |
| Down B: Bomb, air | `special_air_lw` | - | - | - | - | - | - | - | 39 | - | - | - | spawns article/projectile on 16 |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-15 | - | 22 | 20 |  |
| Roll forward | `roll_forward` | intangible 4-19 | - | 37 | - |  |
| Roll backward | `roll_backward` | intangible 4-19 | - | 37 | - |  |
| Air dodge | `airdodge` | intangible 4-29 | - | 49 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-29 | 19-20, 28-29 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-24 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-31 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-26 | 15-16, 24-26 (6%) | 49 | - |  |
| Getup roll forward (face down) | `getup_roll_forward_facedown` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-25 | - | 35 | - |  |
| Tech in place | `tech_in_place` | intangible 2-20 | - | 26 | - | starts 1 frame late (included) |
| Tech roll forward | `tech_roll_forward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Tech roll backward | `tech_roll_backward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Wall tech | `wall_tech` | - | - | 26 | - | starts 1 frame late (included) |
| Wall tech jump | `wall_tech_jump` | - | - | 40 | - | starts 1 frame late (included) |
| Ceiling tech | `ceiling_tech` | intangible 2-13 | - | 26 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-3 | - | 3 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-55 | - | 59 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 32 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-46 | 50-55 (8%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-23 | 27-29 (8%) | 55 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-56 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-38 | - | 48 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-21 | - | 21 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 36 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-15 | - | 15 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 27 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Up B | jump cancel | 9 | `special_hi` |
| Neutral air | jump | 10 | `nair` |
| Up air | jump | 11 | `uair` |
| Shield grab | direct | 11 | `grab` |
| Back air | jump | 12 | `bair` |
| Up smash | jump cancel | 12 | `usmash` |
| Down air | jump | 19 | `dair` |
| Forward air | jump | 20 | `fair` |
| Spot dodge | direct | intangible 2-15 of 22 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 37 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 37 | `roll_backward` |
| Wavedash | jump | actionable on frame 18 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Link indexed by [The Melee Library](https://www.meleelibrary.com/#link) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Link Melee Techs Guide](https://www.youtube.com/watch?v=uaV7Snt0C5A&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=11&t=0s) | Third Chair | Video guide on performing useful Link tech in 2020. |
| [Link Guide](http://www.mediafire.com/download/8ddhfpu0n1457d3/LinkGuide.htm) | Skler |  |
| [Linkology](https://www.youtube.com/watch?v=kjrYLXC2p8s) | Germ |  |
| [Optimizing Link](http://smashboards.com/threads/optimizing-link.396662/) | community | Community discussion, involving Saus, on how to make Link as good as he can be. |
| [Link vs Peach](http://smashboards.com/threads/link-as-a-cp-to-peach.417424/#post-20301735) | Saus | Saus discusses Link's general gameplan against Peach. |
| [Grab Punishes with Link](http://smashboards.com/threads/grab-punishes-with-link.387797/) | Saus and community | An extensive discusses of Link's grab follow-ups on multiple characters. |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Link (SSBM): https://www.ssbwiki.com/Link_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Link_(SSBM)/Up_special , /Down_throw ,
  /Up_throw , /Neutral_aerial , /Down_aerial , /Down_special , /Side_special ,
  /Neutral_special
- SSBWiki, Bomb recovery: https://www.ssbwiki.com/Bomb_recovery
- SSBWiki, Bomb (Link) (includes Goron roll, acid drop, bombchu):
  https://www.ssbwiki.com/Bomb_(Link)
- SSBWiki, Wall grapple: https://www.ssbwiki.com/Wall_grapple
- SSBWiki, Hookshot: https://www.ssbwiki.com/Hookshot
- SSBWiki, Boomerang: https://www.ssbwiki.com/Boomerang
- SSBWiki, Hero's Bow: https://www.ssbwiki.com/Hero%27s_Bow
- SSBWiki, Chain dance (ghost arrow, boomerang superjump): https://www.ssbwiki.com/Chain_dance
- SSBWiki, Chain grab: https://www.ssbwiki.com/Chain_grab
- SSBWiki, Young Link (SSBM) (differences list): https://www.ssbwiki.com/Young_Link_(SSBM)
- SSBWiki, List of SSBM tier lists (NTSC): https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Melee Library card "Grab Punishes with Link" (Saus and community), read via
  web.archive.org: http://smashboards.com/threads/grab-punishes-with-link.387797/
- Melee Library card "Link vs Peach" (Saus), read via web.archive.org:
  http://smashboards.com/threads/link-as-a-cp-to-peach.417424/
- Melee Library card "Optimizing Link", read via web.archive.org:
  http://smashboards.com/threads/optimizing-link.396662/
- Frame data dump: `fd/json/Link.json`
- Not readable (titles only): "2020 Link Melee Techs Guide" (video), "Linkology" (video),
  "Link Guide" by Skler (file download).
