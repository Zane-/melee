---
schema: melee-character/v1
id: bowser
name: Bowser
aliases: [King Koopa, Koopa, Boozer]
tier: "F (26th of 26), 2021 tier list"
archetype: [heavy, grappler, combo-food, punish-heavy, edgeguarder, mixup]
related: [donkey-kong, ganondorf]
summary: Bowser survives to high percent, answers pressure with an intangible up B out of shield, and takes stocks with single strong hits, the Koopa Klaw command grab, and ledge play built on up B edgehogs and his ledge attack.
key_tech: [fortress-out-of-shield, fortress-hog, fortress-parry, fortress-landing, koopa-klaw, klaw-throw-up-air, grab-release-regrab, ledge-attack, jab-up-tilt, bomb-ledge-snap]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlKp.dat
framedata: ../framedata/bowser.json
code: src/melee/ft/kinds/ftKoopa
specials:
  neutral_b: "Fire Breath"
  side_b: "Koopa Klaw"
  up_b: "Whirling Fortress"
  down_b: "Bowser Bomb"
attributes:
  weight: 117
  gravity: 0.13
  fall_speed: 1.9
  fast_fall_speed: 2.4
  jump_squat: 8
  jumps: 2
  walk_speed: 0.65
  dash_speed: 1
  run_speed: 1.5
  traction: 0.06
  air_speed: 0.8
  landing_lag: 6
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [7, 21, 5]
  jab2: [9, 27, 6]
  dash_attack: [10, 56, 11]
  ftilt_high: [12, 37, 15]
  ftilt: [12, 37, 14]
  ftilt_low: [12, 37, 13]
  utilt: [7, 50, 13]
  dtilt: [14, 55, 13]
  fsmash: [29, 66, 24]
  usmash: [16, 53, 20]
  dsmash: [14, 68, 10]
  nair: [8, 48, 13]
  fair: [8, 42, 14]
  bair: [9, 50, 13]
  uair: [22, 45, 17]
  dair: [14, 78, 3]
  grab: [9, 41, 0]
  dash_grab: [10, 51, 0]
  pummel: [10, 25, 3]
  fthrow: [null, 60, 10]
  bthrow: [null, 40, 10]
  uthrow: [20, 70, 2]
  dthrow: [47, 85, 0]
  special_n_start: [null, 22, 0]
  special_n: [null, 20, 0]
  special_n_end: [null, 30, 0]
  special_air_n_start: [null, 22, 0]
  special_air_n: [null, 20, 0]
  special_air_n_end: [null, 30, 0]
  special_s_start: [16, 60, 12]
  special_s_hit: [18, 30, 4]
  special_s_hit_303: [18, 30, 4]
  special_s_end_f: [17, 40, 11]
  special_s_end_b: [null, 40, 11]
  special_air_s_start: [16, 60, 12]
  special_air_s_hit: [18, 30, 4]
  special_air_s_hit_308: [18, 30, 4]
  special_air_s_end_f: [17, 40, 11]
  special_air_s_end_b: [null, 40, 10]
  special_hi: [5, 80, 13]
  special_air_hi: [5, 80, 10]
  special_lw: [null, 40, 0]
  special_air_lw: [null, 32, 0]
  special_lw_landing: [1, 60, 8]
oos:  # option: frame the hitbox is out
  special_hi: 6
  grab: 9
  nair: 16
  fair: 16
  bair: 17
  usmash: 17
  dair: 22
  uair: 30
resources: 6
# generated: end
---

# Bowser

<!-- GENERATED:attributes -->
## Attributes

Read from `PlKp.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 117 |
| Gravity | 0.13 |
| Terminal fall speed | 1.9 |
| Fast-fall speed | 2.4 |
| Jump squat (frames before airborne) | 8 |
| Full hop / short hop initial Y speed | 2.8 / 1.6 |
| Air jump Y multiplier | 1 |
| Jumps | 2 |
| Walk max speed | 0.65 |
| Dash initial speed / run max speed | 1 / 1.5 |
| Ground friction (traction) | 0.06 |
| Air max horizontal speed | 0.8 |
| Air acceleration (base + stick) | 0.02 + 0.03 |
| Air friction | 0.01 |
| Normal landing lag | 6 |
| Shield size | 31.25 |
<!-- /GENERATED:attributes -->

## Overview

Bowser is the heaviest character in the game and the classic punching bag: last on the tier
list [wiki:Bowser_(SSBM)]. He hits harder than anyone, but nearly everything he has is slow.
His jumpsquat (the grounded frames before a jump leaves the ground) is 8 frames, the longest
in the game, which makes every aerial, [wavedash](../techniques/wavedash.md) and jump out of
shield late and readable [wiki:Bowser_(SSBM)]. He has no useful projectile and a huge body, so
he is camped, comboed, juggled and [chain grabbed](../techniques/chain-grab.md) by most of the
cast [wiki:Bowser_(SSBM)]. What he does have: grounded up B (Whirling Fortress), which is
intangible from frame 1 and hits on frame 5 [wiki:Bowser_(SSBM)/Up_special], making it one of
the best [out of shield](../techniques/out-of-shield.md) moves in the game; side B (Koopa
Klaw), a command grab that also works in the air and beats shields; forward air, a fast and
long-reaching aerial by his standards; and the best under-100% ledge attack in the game
[wiki:Bowser_(SSBM)]. He wins neutral rarely and mostly by making the opponent's pressure
unsafe. He punishes with one to three hard hits, not long combos. He dies to being comboed up
to kill percent and to edgeguards: his up B travels sideways but barely rises, so spikes and
an occupied ledge end his stocks [wiki:Bowser_(SSBM)]. He is not technically demanding in the
usual sense, but his best play depends on precise up B ledge and platform movement and on
hard reads.

## Strengths and weaknesses

- **Strengths:**
  - Whirling Fortress on the ground: intangible frames 1-4, 13% clean hit on frames 5-6
    [wiki:Bowser_(SSBM)/Up_special]; fast lateral movement; edgehog tool.
  - Koopa Klaw: command grab plus a slash hitbox, usable in the air.
  - Raw power: forward smash 24%, up air 17%, up tilt 13% with knockback growth 120, forward
    tilt 12-15% [fd]. Down tilt can do 22% over two hits [wiki:Bowser_(SSBM)].
  - Heaviest character: lives very long, and [crouch cancel](../techniques/crouch-cancel.md)
    works to high percent [lib:Melee 225: Advanced Bowser Tech].
  - Grab release leaves him 10 frames ahead, which no other normal grab does
    [wiki:Bowser_(SSBM)/Grab].
  - Under-100% ledge attack with the largest reach in the game
    [lib:Melee 225: Advanced Bowser Tech].
- **Weaknesses:**
  - 8-frame jumpsquat; forward air effectively comes out on frame 16 from the ground
    [wiki:Bowser_(SSBM)/Forward_aerial].
  - Slow normals: jab frame 7, forward tilt frame 12, forward smash frame 29 [fd]; standing
    grab frame 9 [wiki:Bowser_(SSBM)/Grab].
  - Aerial landing lag of 30 frames (35 bair, 40 dair) uncancelled; 15/17/20 with an
    [L-cancel](../techniques/l-cancel.md) [fd].
  - Enormous hurtbox, fast fall speed: comboed and chain grabbed by most characters.
  - Recovery gains very little height [wiki:Bowser_(SSBM)].
  - Neutral B (Fire Breath) is slow, short and punishable on hit [wiki:Fire_Breath]. The
    "flame cancel" that fixes its startup exists only in NTSC 1.00/1.01, not in 1.02
    [wiki:Bowser_(SSBM)/Neutral_special].
  - His shield does not cover him well and is easily shield-stabbed; his roll is the
    shortest in the game [wiki:Bowser_(SSBM)] [lib:Melee 225: Advanced Bowser Tech].

## Character tech

### Fortress out of shield

- **id:** `fortress-out-of-shield`
- **What:** Jump-cancelled grounded up B from shield. Bowser is intangible until the hitbox
  appears, so it beats or trades with almost any follow-up pressure.
- **Inputs:** While shielding, press up (tap jump) and then B during the jumpsquat. Hold a
  direction to slide.
- **Timing:** Grounded up B: intangible frames 1-4, clean hit frames 5-6 (13%, 80°), weaker
  hits until frame 46, 79 frames total; head and limbs stay intangible until frame 49
  [wiki:Bowser_(SSBM)/Up_special]. In Melee the up B cannot start on the first jumpsquat
  frame [wiki:Whirling_Fortress], so from shield the earliest hit is frame 6 with
  intangibility from frame 2. The 8-frame jumpsquat gives a very wide window to input B and
  still get the grounded version [lib:Melee 225: Advanced Bowser Tech]. If the hit is
  shielded Bowser is open to a full punish, including grab [wiki:Whirling_Fortress].
- **Used for:** Punishing aerials and grabs on shield, escaping
  [shield pressure](../techniques/shield-pressure.md), replacing his roll. It kills
  floaties: [Jigglypuff](jigglypuff.md) at about 80% (about 105% on Dream Land)
  [wiki:Bowser_(SSBM)/Up_special]. Slide to a ledge afterward to cancel the end lag (see
  fortress hog).
- **Common errors:** Pressing B after leaving the ground (aerial version: no intangibility,
  10% hit, then special fall [wiki:Bowser_(SSBM)/Up_special]); using it against a spaced
  move and getting it shielded; using it when too close, which can cause a second weak hit
  that cancels the launch (17% total but no kill) [wiki:Bowser_(SSBM)/Up_special].
- **Drill idea:** CPU pressures Bowser's shield with an aerial then a grab or jab; success
  when the 13% hit connects within 8 frames of shield stun ending.

### Fortress hog

- **id:** `fortress-hog`
- **What:** A grounded up B slid off the edge of the stage snaps to the ledge, facing either
  way: a very fast edgehog (grabbing the ledge so the opponent cannot)
  [wiki:Whirling_Fortress].
- **Inputs:** Near the edge, up B and hold the stick up-and-away from the stage (diagonal).
  Alternative: roll or walk to the very edge (teeter), up B, move off and down
  [wiki:Whirling_Fortress]. Easier facing the stage than facing away; slow down with a
  diagonal stick when close to the ledge [lib:Melee 225: Advanced Bowser Tech].
- **Timing:** There is a window of about 49 frames in which sliding off still grabs the
  ledge [lib:Melee 225: Advanced Bowser Tech]. On Yoshi's Story the sloped edges make it
  work with no adjustment, even from near center stage facing away
  [lib:Melee 225: Advanced Bowser Tech].
- **Used for:** Edgeguarding (take the ledge, then ledge attack or ledge-hop bair), and
  cancelling the end lag of up B out of shield.
- **Common errors:** Sliding off too fast or with the wrong stick angle (Bowser falls past
  the ledge in the spin and dies); starting too far away.
- **Drill idea:** Bowser at varying distances from the edge, facing either way; success
  when he is hanging on the ledge within N frames of the up B input.

### Fortress parry

- **id:** `fortress-parry`
- **What:** Using the intangible startup and strong first hit of grounded up B on reaction
  or read to beat or clank with an incoming attack, without shielding first
  [lib:Melee 225: Advanced Bowser Tech].
- **Inputs:** Up B from any grounded actionable state (stand, crouch, dash turn).
- **Timing:** Frames 1-4 intangible, hitbox frame 5 [wiki:Bowser_(SSBM)/Up_special]. The
  13% first hit clanks with grounded attacks of up to 22% (examples given: Marth's tipper
  forward smash, Fox's up smash, Peach's down smash), and it also clanks with weak hits of
  4% or more rather than beating them [lib:Melee 225: Advanced Bowser Tech]. Because the
  first hitbox frame is also the first vulnerable frame, it often trades; trading with a
  weak projectile (Falco laser, Sheik needle) leaves the opponent launched and Bowser
  barely stunned, which starts a combo [wiki:Bowser_(SSBM)/Up_special].
- **Used for:** Surviving kill moves at high percent, stuffing approaches, starting
  offence from a trade. Follow a clank with a second up B, forward tilt or up tilt.
- **Common errors:** Mistiming so the opponent hits after frame 4 but before the hitbox
  reaches them; expecting a clean win against multi-hit or disjointed moves.
- **Drill idea:** CPU Marth forward smashes at random delay; success when Bowser takes no
  damage and Marth is hit or the moves clank.

### Fortress landing and aerial fortress interrupt

- **id:** `fortress-landing`
- **What:** Two ways to land an aerial up B on a platform or the stage without the usual
  special-fall landing: (1) aerial fortress interrupt (AFI): the up B's rise ends exactly
  at platform height and Bowser lands silently and can act at once; (2) fortress landing:
  he snaps to the ground during the spin and slides along it
  [lib:Melee 225: Advanced Bowser Tech].
- **Inputs:** Aerial up B from below a platform or from a ledge drop at a height where the
  arc tops out at the surface.
- **Timing:** Height dependent, no fixed frame window in the source. The snap points
  correspond to downward extensions of his collision box on frames 3, 6, 13, 17, 25 and 33
  of the move [lib:Melee 225: Advanced Bowser Tech]. Landing after special fall costs 10
  frames; landing before it costs 1 [wiki:Bowser_(SSBM)/Up_special]. Edge-cancelling only
  works after the up B animation has finished; touching an edge earlier slides him off
  helpless [lib:Melee 225: Advanced Bowser Tech].
- **Used for:** Platform movement, getting off the ledge with a hitbox, retreating to a
  side platform and edge-cancelling the lag.
- **Common errors:** Too high (special fall and landing lag); sliding off the far side.
- **Drill idea:** From ledge hang, success when Bowser is grounded on stage and actionable
  within N frames of the up B with no landing-lag animation.

### Koopa Klaw

- **id:** `koopa-klaw`
- **What:** Side B. Close targets are grabbed (a command grab: it ignores shield); targets
  slightly farther are hit by a slash (12% or 10%) that launches upward
  [wiki:Koopa_Klaw]. Works on the ground and in the air.
- **Inputs:** Side B. On grab: B to bite, forward or back on the stick to throw.
- **Timing:** Slash and grab are active around frames 16-18; 59 frames on whiff
  [wiki:Bowser_(SSBM)/Side_special] [fd]. Forward throw: hits on 18-19, releases on 23,
  40 frames, 15%. Back throw: releases on 16, 40 frames, 11%
  [wiki:Bowser_(SSBM)/Side_special] [wiki:Bowser_(SSBM)]. The hold lasts up to 250 frames
  regardless of percent, and each mash input shortens it by 12 frames [wiki:Koopa_Klaw].
  The opponent cannot air-release out of it [lib:Melee 225: Advanced Bowser Tech].
- **Used for:** Beating shields, especially on platforms and after conditioning with
  [SHFFL](../techniques/shffl.md)ed aerials (an aerial Klaw replaces the expected aerial,
  like a tomahawk grab that never lands first); it grabs lower than expected in the air and
  can pick up opponents lying on the ground [lib:Melee 225: Advanced Bowser Tech]. Back
  throw is a kill throw, about 1.3x his normal back throw
  [lib:Melee 225: Advanced Bowser Tech]. Grabbing a recovering opponent in the air and back
  throwing them into the stage is a stage spike; biting all the way down is a suicide KO,
  where who dies first depends on the victim (victim first: Bowser, DK, Captain Falcon,
  Ganondorf, Fox, Samus, Roy; Bowser first: most others; sudden death: Peach, Zelda,
  Mewtwo) [lib:Melee 225: Advanced Bowser Tech].
- **Common errors:** Too far (slash instead of grab) or whiff (59 frames of lag); using it
  at the edge facing out and falling to his death.
- **Drill idea:** CPU shields on a platform or after Bowser's aerials; success when the
  grab (not the slash) connects and a throw follow-up lands.

### Klaw throw to up air

- **id:** `klaw-throw-up-air`
- **What:** Koopa Klaw forward throw pops the opponent up in front of Bowser; up air (his
  strongest aerial) or another aerial follows.
- **Inputs:** Side B grab, forward throw, jump, up air; L-cancel on landing.
- **Timing:** Both Klaw throws let Bowser act on frame 41 [wiki:Koopa_Klaw]. Up air hits on
  frames 22-25 and needs the 8-frame jumpsquat first [wiki:Bowser_(SSBM)/Up_aerial]. It
  works at "any reasonable percentage" but only on some characters: yes on Bowser, Captain
  Falcon, DK, Falco, Fox, Ganondorf, Link, Marth, Pichu, Pikachu, Roy, Sheik, Yoshi, Young
  Link; no on Jigglypuff, Luigi, Samus, Zelda; on Dr. Mario, Mario, Ice Climbers, Kirby,
  Mewtwo, Mr. Game & Watch, Ness and Peach they can jump out, but a double-jump up air
  catches the jump [wiki:Bowser_(SSBM)/Up_aerial]. On Fox and Falco, DI (directional
  influence) backward can be followed with a second Klaw instead
  [lib:Melee 225: Advanced Bowser Tech].
- **Used for:** His most consistent combo and kill confirm; three or four up airs on
  fastfallers with platforms [wiki:Bowser_(SSBM)/Up_aerial].
- **Common errors:** Missing the L-cancel (30 frames of lag); delaying the jump.
- **Drill idea:** CPU held in Klaw at a chosen percent with random DI; success when up air
  connects before the CPU acts.

### Grab release regrab

- **id:** `grab-release-regrab`
- **What:** When an opponent breaks out of Bowser's normal grab on the ground, Bowser is
  actionable 10 frames before they are, which is just enough to grab again and keep
  pummelling [wiki:Bowser_(SSBM)/Grab].
- **Inputs:** Grab, pummel until the release, dash grab immediately.
- **Timing:** +10 on release; dash grab is active on frames 10-12, so the re-grab is
  frame-tight [wiki:Bowser_(SSBM)/Grab] [lib:Melee 225: Advanced Bowser Tech]. The opponent
  avoids it by holding up to force an air release [wiki:Bowser_(SSBM)/Grab]. Forward tilt
  (frame 12) is an alternative after a ground release, for example near the ledge at 60%+
  [lib:Melee 225: Advanced Bowser Tech]. Against a wall it repeats regardless of release
  type [lib:Melee 225: Advanced Bowser Tech].
- **Used for:** Extra damage on opponents who do not know to air release.
- **Common errors:** One frame late (opponent shields or jumps).
- **Drill idea:** CPU mashes out with ground release; count consecutive re-grabs.

### Ledge attack

- **id:** `ledge-attack`
- **What:** Bowser's ledge attack below 100% is a fast spin onto the stage with the largest
  reach of any ledge attack; at 100% or more it is replaced by a slow, weak one
  [wiki:Bowser_(SSBM)] [lib:Melee 225: Advanced Bowser Tech].
- **Inputs:** A or Z while hanging on the ledge with under 100% damage.
- **Timing:** 8% [wiki:Bowser_(SSBM)]. Frame data: Unknown. It is long-lasting enough to
  be used in place of a ledge roll to keep the ledge occupied
  [lib:Melee 225: Advanced Bowser Tech].
- **Used for:** Hitting opponents near the ledge, knocking recovering opponents back out,
  and beating Fox/Falco recoveries after a fortress hog
  [lib:Melee 225: Advanced Bowser Tech]. Mix with ledge-hop bair.
- **Common errors:** Using it at 100%+ (slow version); repeating it into a shield.
- **Drill idea:** Track Bowser's percent; fortress hog then ledge attack must hit a CPU
  recovering onto the stage.

### Jab to up tilt

- **id:** `jab-up-tilt`
- **What:** Jab 1 has set knockback, so it leaves the opponent in place at any percent and
  links to up tilt or jab 2 unless they SDI (smash DI, tapping a direction during hitlag)
  [lib:Melee 225: Advanced Bowser Tech].
- **Inputs:** A, then up tilt.
- **Timing:** Jab 1 hits on frames 7-9 and is interruptible from frame 21; up tilt hits on
  frames 7-10 and is interruptible from frame 50 [fd] [wiki:Bowser_(SSBM)/Up_tilt].
- **Used for:** A close-range kill confirm: up tilt kills floaties at mid to high percent
  [lib:Melee 225: Advanced Bowser Tech]. Up tilt also links into itself from about 35%,
  into up smash, up air, grab, or up B [wiki:Bowser_(SSBM)/Up_tilt].
- **Common errors:** Whiffing up tilt (small hitbox, misses short or crouching characters
  [wiki:Bowser_(SSBM)/Up_tilt]) and eating a punish during its long recovery.
- **Drill idea:** CPU at 80-110% in jab range; success when jab 1 then up tilt both
  connect.

### Bowser Bomb ledge snap

- **id:** `bomb-ledge-snap`
- **What:** Down B in the air is a stall-then-fall; if Bowser falls past a ledge he is
  facing or next to, he grabs it and skips the long landing lag [wiki:Bowser_Bomb].
- **Inputs:** Aerial down B positioned above the ledge; do not hold down (holding down
  prevents the ledge grab) [lib:Melee 225: Advanced Bowser Tech].
- **Timing:** 21% on the drop, 8% for the landing shockwave [wiki:Bowser_(SSBM)]. He keeps
  drifting during the stall, so horizontal speed before the input must be accounted for
  [wiki:Bowser_Bomb].
- **Used for:** Getting down from high up quickly; a risky edgeguard on opponents at the
  ledge.
- **Common errors:** Drifting past the ledge and dying; landing on stage (about a second
  of lag).
- **Drill idea:** Bowser starts high above the ledge; success when he is hanging on it
  after the drop.

## Neutral game

- Bowser does not approach well. He holds space with forward air (frames 8-11, auto-cancels
  from frame 31 [wiki:Bowser_(SSBM)/Forward_aerial]) and forward tilt (frames 12-16,
  disjointed, interruptible from frame 37 [wiki:Bowser_(SSBM)/Forward_tilt]), and waits for
  the opponent to commit.
- He uses shield and crouch as bait: up B out of shield, crouch cancel into forward tilt,
  up tilt or grab.
- Platforms are essential: they block projectiles, set up Klaws on shielding opponents, and
  allow fortress movement and edge cancels. Bowser players are advised never to pick Final
  Destination, least of all against projectile characters
  [lib:Melee 225: Advanced Bowser Tech].
- Dash grab has much more reach than standing or jump-cancel grab but a long whiff
  animation (50 frames) [wiki:Bowser_(SSBM)/Grab].
- [Waveland](../techniques/waveland.md) back into forward tilt and turnaround shield stops
  are listed as core movement [lib:Melee 225: Advanced Bowser Tech].
- Avoid in neutral: forward smash (frame 29), dair, roll, spot dodge, raw dash attack
  [lib:Melee 225: Advanced Bowser Tech].

## Punish game

Bowser's combos are two or three hits and often depend on poor DI [wiki:Bowser_(SSBM)]. The
reliable structure is: Klaw or grab, one launcher, one or two strong aerials, then a tech chase
or edgeguard.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| Koopa Klaw forward throw | Fox, Falco, Captain Falcon, Marth, Sheik, Ganondorf, DK, Bowser, Link, Young Link, Roy, Pikachu, Pichu, Yoshi | any reasonable percent | Up air | Platforms extend to 3-4 up airs on fastfallers | [wiki:Bowser_(SSBM)/Up_aerial] |
| Koopa Klaw forward throw | Mario, Dr. Mario, Peach, Ice Climbers, Ness, Mewtwo, Kirby, Mr. Game & Watch | any | Double-jump up air | Catches their jump out | [wiki:Bowser_(SSBM)/Up_aerial] |
| Koopa Klaw forward throw | Fox, Falco | low | Second Koopa Klaw, or fair/nair/bair | On DI behind | [lib:Melee 225: Advanced Bowser Tech] |
| Forward air (no tumble) | most | low | Grab | Needs L-cancel | [wiki:Bowser_(SSBM)/Forward_aerial] |
| Up throw | fastfallers | any (set knockback) | Forward tilt, fair, re-grab | They can jump or shine out depending on DI | [wiki:Bowser_(SSBM)/Forward_tilt] [lib:Melee 225: Advanced Bowser Tech] |
| Up tilt | most | from about 35% | Up tilt, up smash, up air, grab | | [wiki:Bowser_(SSBM)/Up_tilt] |
| Jab 1 | most | any | Up tilt or jab 2 | Set knockback | [lib:Melee 225: Advanced Bowser Tech] |
| Down smash | fastfallers | low-mid | Down smash, up smash | | [wiki:Bowser_(SSBM)] |
| Dash attack | Fox, Falco | low-mid | Up tilt | Inconsistent | [lib:Melee 225: Advanced Bowser Tech] |
| Up B trade with a weak hit | most | any | Any aerial or tilt | "Shell shock" | [wiki:Bowser_(SSBM)/Up_special] |
| Grab release (ground) | all | any | Dash re-grab, or forward tilt | Opponent can air release | [wiki:Bowser_(SSBM)/Grab] |

### Chain grabs and tech chases

- Up throw has set knockback, so in principle it re-grabs fastfallers at any percent, but
  with DI they get a window to jump, shine or attack; treat it as a mixup with tech chases
  and grab releases, not a true chain grab [lib:Melee 225: Advanced Bowser Tech]. Up throw
  releases on frame 52 of 69 [wiki:Bowser_(SSBM)/Up_throw]. On platform stages it puts the
  opponent on a platform for a [tech chase](../techniques/tech-chase.md)
  [wiki:Bowser_(SSBM)].
- Down throw sets up a tech chase. Its 12% comes from a one-frame hitbox on frame 47; in
  NTSC it does no damage to Jigglypuff and Mr. Game & Watch because the weight-scaled
  animation skips that frame [wiki:Bowser_(SSBM)/Down_throw].
- Tech chase coverage: dash grab for reach, Klaw (also picks up missed techs), forward air,
  up air on platform techs [lib:Melee 225: Advanced Bowser Tech].
- Grab release re-grab: see tech entry.

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Grounded up B (clean hit) | Jigglypuff | about 80% (about 105% on Dream Land) | Out of shield or parry | [wiki:Bowser_(SSBM)/Up_special] |
| Up air | most | about 100%+, earlier on light characters | Usually from Klaw forward throw; frames 22-25 | [wiki:Bowser_(SSBM)] |
| Up tilt | floaties | mid to high | Frame 7; from jab 1 | [lib:Melee 225: Advanced Bowser Tech] |
| Forward smash | most | 18-38% when fully charged; uncharged Unknown | Frame 29; hard read, shield break, missed Rest | [wiki:Bowser_(SSBM)] |
| Koopa Klaw back throw | most | Unknown; early near the edge and on small stages | Command grab | [lib:Melee 225: Advanced Bowser Tech] |
| Koopa Klaw slash | most | high | Spacing must be outside grab range | [wiki:Koopa_Klaw] |
| Forward air | most | Unknown | Near the edge or offstage; low angle | [wiki:Bowser_(SSBM)/Forward_aerial] |
| Bair (clean) | most | Unknown | 13% at 24° [fd]; edgeguard semi-spike | [wiki:Bowser_(SSBM)] |
| Up smash | most | Unknown | Frames 16-21, intangible on 16-17; reads on platform drops | [wiki:Bowser_(SSBM)/Up_smash] |
| Forward throw | most | high | At the edge | [wiki:Bowser_(SSBM)] |
| Aerial Klaw back throw into the stage | recovering opponents | any | Stage spike; techable | [lib:Melee 225: Advanced Bowser Tech] |

- Edgeguard flow: fortress hog to take the ledge, then under-100% ledge attack or ledge-hop
  bair; down-angled forward tilt hits below the stage lip and is called his primary
  edgeguard move [lib:Melee 225: Advanced Bowser Tech]; forward air trades well with Fox's
  and Falco's up B [wiki:Bowser_(SSBM)/Forward_aerial].
- Fire Breath only for damage on very linear recoveries [wiki:Bowser_(SSBM)].

## Recovery

- **Options:**
  - Aerial up B: good horizontal distance, very little height; no intangibility on the body
    in the air, head and limbs intangible during the spin; hits up to 11 times
    [wiki:Bowser_(SSBM)/Up_special].
  - Double jump (slow, poor air speed).
  - Bowser Bomb from high above the ledge to snap to it.
  - Koopa Klaw in the air to grab an edgeguarder (and die with them or stage spike them).
  - Air dodge.
- **Mixups:** High recovery onto a platform with an edge cancel or fortress landing; early
  versus late up B; Bowser Bomb to ledge. There are few.
- **Weaknesses:** He must be above ledge height before the up B. Meteors and spikes
  ([Falco](falco.md), [Marth](marth.md)) gimp him at any percent, and holding the ledge
  beats most low recoveries [wiki:Bowser_(SSBM)]. Koopa Klaw at the edge kills him
  [lib:Melee 225: Advanced Bowser Tech].

### Edgeguarding Bowser

- Take the ledge when he is level with or below it; he cannot rise over an edgehog.
- Spike or semi-spike him during the up B from above; his body is hittable in the air
  version.
- Do not jump into the spin from the side at low percent: aerial up B does up to 32% if
  every hit connects [wiki:Whirling_Fortress].
- If he comes high, wait under him: his landing options are slow (special-fall landing lag,
  Bowser Bomb lag) unless he reaches a platform edge.
- CPU Bowser script: DI up, double jump early to stay high, up B toward the ledge or a
  platform, occasional Bowser Bomb to ledge.

## Defense and out of shield

- Up B out of shield is the centre of his defence (frame 6 hit from shield, intangible from
  frame 2). It is unsafe when shielded, so opponents bait it by spacing.
- Other options: up tilt out of shield when the fortress is stale or would not kill
  [wiki:Bowser_(SSBM)/Up_tilt]; forward air out of shield against badly spaced moves
  despite the jumpsquat [wiki:Bowser_(SSBM)/Forward_aerial]; shield grab (frame 9, slow).
- Crouch cancel into forward tilt, up tilt or grab works to high percent because of his
  weight [wiki:Bowser_(SSBM)/Forward_tilt] [lib:Melee 225: Advanced Bowser Tech].
- Aerial up B is his only fast combo breaker, and it has no intangibility.
- He cannot escape projectile camping, and his shield is easy to poke.

## As the training dummy

- Heaviest character, large hurtbox, above-average fall speed (12th-14th fastest
  [lib:Melee 225: Advanced Bowser Tech]). He is the standard test body for long combos and
  for "what kills a heavy" measurements. Other files use him for that: DK's clean fair kills
  him at 128% from center stage [wiki:Donkey_Kong_(SSBM)/Forward_aerial].
- Chain grabs on him: [Sheik](sheik.md)'s down throw from 0% to medium or high percents in
  NTSC; [Mewtwo](mewtwo.md)'s down throw from 0-50%; [Peach](peach.md)'s down throw to high
  percents if he does not DI away [wiki:Chain_grab]; [Dr. Mario](dr-mario.md)'s down throw
  in two windows, 13-21% and 35-42% after throw
  [lib:Doc Advanced Tech Frame Data Megathread]. Weight-scaled throws are at their slowest
  on him.
- Strong CPU choices: crouch cancel at low and mid percent; up B out of shield; DI away
  from chain grabs; aerial up B when juggled; tech away on platforms.
- Because Bowser's jumpsquat is 8 frames, a CPU Bowser that tries to jump out of pressure
  is hit before leaving the ground; drills for the opponent's pressure should have him use
  up B out of shield as the realistic threat.
- His under-100% and 100%+ ledge attacks differ completely; a ledge-trap drill against him
  must set his percent on the intended side of 100%.

## Matchup notes

### vs Fox and Falco

- They camp him with lasers, combo him freely, and Falco's dair gimps his recovery
  [wiki:Bowser_(SSBM)]. Bowser's chances come from up B out of shield against their
  pressure, Klaw forward throw into up air strings, and edgeguards: fortress hog, ledge
  attack, and fair trades against their up B [wiki:Bowser_(SSBM)/Forward_aerial]
  [lib:Melee 225: Advanced Bowser Tech].

### vs Marth

- Marth outranges him, juggles him, and spikes his recovery [wiki:Bowser_(SSBM)]. A
  well-timed fortress clanks with tipper forward smash
  [lib:Melee 225: Advanced Bowser Tech]; Klaw forward throw to up air works on Marth
  [wiki:Bowser_(SSBM)/Up_aerial].

### vs Sheik

- Down throw chain grab in NTSC [wiki:Chain_grab], needles (which a fortress can trade
  with favourably [wiki:Bowser_(SSBM)/Up_special]) and easy edgeguards.

### vs Jigglypuff

- His best-known kill number: grounded up B kills her at about 80%
  [wiki:Bowser_(SSBM)/Up_special]. Up tilt can be ducked under by her
  [wiki:Bowser_(SSBM)/Up_tilt]; down throw does no damage to her
  [wiki:Bowser_(SSBM)/Down_throw]; Klaw forward throw to up air does not work
  [wiki:Bowser_(SSBM)/Up_aerial].

### vs projectile characters (Samus, Young Link, Link)

- The guide singles out Samus on Final Destination as the scenario to avoid
  [lib:Melee 225: Advanced Bowser Tech]. He needs platforms to get in.

## Drill seeds

### Fortress out of shield

- **id:** `bowser-fortress-oos`
- **Goal:** Get the grounded, intangible up B from shield in every pressure gap.
- **Player:** Bowser
- **CPU:** Fox, Falco, Sheik, Marth, Captain Falcon
- **Setup:** Bowser shielding at center stage, 0-80%.
- **CPU behaviour:** Aerial on shield, then at random: grab, jab, shine (Fox/Falco), second
  aerial, or retreat out of range.
- **Success:** The 13% clean hit connects; or, on the retreat case, Bowser does not up B.
- **Fail:** Aerial up B comes out (B pressed after the 8-frame jumpsquat), Bowser is hit or
  grabbed, or the up B is shielded.
- **Variations:** Require sliding to the ledge after the hit (fortress hog) to cancel lag;
  Jigglypuff at 80% as a kill drill.
- **Data needed:** Up B frames [wiki:Bowser_(SSBM)/Up_special]; jumpsquat 8 frames
  [wiki:Bowser_(SSBM)]; CPU shield stun and move lag.

### Fortress hog

- **id:** `bowser-fortress-hog`
- **Goal:** Edgehog from the stage with up B, both facings.
- **Player:** Bowser
- **CPU:** Fox, Falco, Marth (recovering low)
- **Setup:** Bowser at a random distance from the left ledge on Battlefield, random facing;
  CPU offstage below the ledge.
- **CPU behaviour:** Up B to the ledge sweetspot.
- **Success:** Bowser is hanging on the ledge before the CPU arrives and the CPU dies or is
  then hit by the ledge attack.
- **Fail:** Bowser falls past the ledge, or the CPU grabs it first.
- **Variations:** Yoshi's Story (easier); follow-up with ledge attack required; Bowser at
  100%+ (ledge attack is the bad one, so ledge-hop bair instead).
- **Data needed:** Ledge grab window of about 49 frames
  [lib:Melee 225: Advanced Bowser Tech]; stage edge geometry; grounded up B slide speed.

### Koopa Klaw versus shield

- **id:** `bowser-klaw-shield`
- **Goal:** Space the grab part of Klaw and choose it when the opponent shields.
- **Player:** Bowser
- **CPU:** Marth, Sheik, Peach
- **Setup:** CPU standing on a Battlefield side platform or on the ground; Bowser
  approaching with short hop aerials.
- **CPU behaviour:** Shields when Bowser jumps at it (probability rises after each shielded
  aerial); otherwise anti-airs.
- **Success:** Klaw grab (not slash) connects on a shielding CPU, then a throw.
- **Fail:** Slash hits shield, Klaw whiffs, or Bowser is hit.
- **Variations:** Aerial Klaw from a platform drop; grounded Klaw on a CPU lying down
  after a missed tech.
- **Data needed:** Klaw grab box versus slash box positions and frames 16-18
  [wiki:Bowser_(SSBM)/Side_special] [fd].

### Klaw forward throw to up air

- **id:** `bowser-klaw-uair`
- **Goal:** Convert his main grab into his strongest aerial.
- **Player:** Bowser
- **CPU:** Fox, Falco, Captain Falcon, Marth, Sheik (true); Peach, Dr. Mario (double-jump
  version)
- **Setup:** CPU held in Koopa Klaw at 40-110%; platform stage or Final Destination.
- **CPU behaviour:** Random DI; mashes; jumps out when possible.
- **Success:** Up air connects before the CPU acts; L-cancel is hit on landing; bonus for a
  second up air off a platform or a kill.
- **Fail:** Up air whiffs or CPU escapes; missed L-cancel.
- **Variations:** DI behind on Fox/Falco where the answer is a second Klaw; back throw at
  the edge for the kill instead.
- **Data needed:** Klaw throw actionable frame 41 [wiki:Koopa_Klaw]; up air 22-25 and
  jumpsquat 8; the per-character table in [wiki:Bowser_(SSBM)/Up_aerial].

### Grab release regrab

- **id:** `bowser-grab-release`
- **Goal:** Hit the frame-tight dash grab after a ground release.
- **Player:** Bowser
- **CPU:** any
- **Setup:** CPU grabbed at 60%; flat stage.
- **CPU behaviour:** Mashes out; ground release by default.
- **Success:** Dash grab reconnects; count repetitions.
- **Fail:** CPU acts first.
- **Variations:** CPU holds up for an air release some of the time (the correct answer is
  then an anti-air, not a grab); forward tilt follow-up near the ledge.
- **Data needed:** +10 on release [wiki:Bowser_(SSBM)/Grab]; dash grab frames 10-12.

### Fortress parry

- **id:** `bowser-fortress-parry`
- **Goal:** Time frames 1-4 of up B against a kill move.
- **Player:** Bowser
- **CPU:** Marth (forward smash), Fox (up smash), Peach (down smash)
- **Setup:** Bowser at 120%, standing in the CPU's range.
- **CPU behaviour:** Uses its kill move after a random delay, sometimes from a dash.
- **Success:** Bowser takes no knockback and the CPU is hit or the moves clank, followed by
  a Bowser hit.
- **Fail:** Bowser is launched.
- **Variations:** Falco laser or Sheik needle into approach (practise the trade follow-up).
- **Data needed:** Up B intangibility 1-4 and hit frame 5; CPU move startup; clank rule
  with the 13% hitbox [lib:Melee 225: Advanced Bowser Tech].

### Ledge attack edgeguard

- **id:** `bowser-ledge-attack`
- **Goal:** Use the under-100% ledge attack on recoveries and know when it is unavailable.
- **Player:** Bowser
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** Bowser hanging on the ledge, percent randomly 60% or 110%; CPU recovering
  toward the stage above the ledge (side B or high up B).
- **CPU behaviour:** Lands on stage near the ledge or tries to pass over Bowser.
- **Success:** Under 100%: ledge attack hits the CPU. At 110%: the player uses ledge-hop
  bair or fair instead and hits.
- **Fail:** CPU lands safely; slow ledge attack used at 110%.
- **Variations:** Start on stage and require a fortress hog first.
- **Data needed:** Ledge attack frame data and reach for both versions (not in the dump);
  Bowser's percent.

### Forward air spacing and auto-cancel

- **id:** `bowser-fair-spacing`
- **Goal:** Make his main aerial safe.
- **Player:** Bowser
- **CPU:** Marth, Sheik, Fox
- **Setup:** Mid range on a platform stage.
- **CPU behaviour:** Dash dances; shield grabs unspaced fairs; punishes missed L-cancels.
- **Success:** Fair hits or touches shield at max range, landing is L-cancelled or
  auto-cancelled (frame 31+), and Bowser is not punished; bonus for fair into grab at low
  percent.
- **Fail:** Shield grabbed or whiff punished.
- **Variations:** Platform-drop fair that auto-cancels; retreating fair.
- **Data needed:** Fair frames 8-11, auto-cancel 1-7 and 31+, lag 30/15
  [wiki:Bowser_(SSBM)/Forward_aerial]; jumpsquat 8.

### Recovery under pressure

- **id:** `bowser-recovery`
- **Goal:** Stay above ledge height and pick ledge, platform or stage.
- **Player:** Bowser
- **CPU:** Marth, Falco, Sheik
- **Setup:** Bowser launched offstage at 60-120%, above ledge height, with double jump.
- **CPU behaviour:** Randomly holds the ledge, jumps out to spike, or waits on stage.
- **Success:** Bowser grabs the ledge or lands and becomes actionable without being hit.
- **Fail:** Bowser dies or is hit during landing lag.
- **Variations:** Bowser Bomb to ledge from high; fortress landing on a side platform with
  an edge cancel.
- **Data needed:** Aerial up B distance and 49-frame length, landing lag 10 after special
  fall [wiki:Bowser_(SSBM)/Up_special]; Bowser Bomb ledge snap rules.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlKp.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/bowser.json`](../framedata/bowser.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 7-9 | 5 | 83 | 0 | 100 | 20 | slash | 24 | 21 | 4 | -9 |  |
| Jab 2 | `jab2` | 9-11 | 6 | Sakurai | 30 | 110 | - | slash | 30 | 27 | 4 | -13 | starts 1 frame late (included) |
| Dash attack | `dash_attack` | 10-13 | 11 | 80 | 120 | 30 | - |  | 59 | 56 | 6 | -39 |  |
|  |  | 14-17 | 8/11 | 80 | 80/120 | 30 | - |  |  |  | 6 | -35 |  |
| Forward tilt (angled up) | `ftilt_high` | 12-16 | 15/13 | Sakurai | 29 | 100 | - |  | 47 | 37 | 8 | -16 |  |
| Forward tilt | `ftilt` | 12-16 | 14/12/13 | Sakurai | 25 | 100 | - |  | 47 | 37 | 8 | -16 |  |
| Forward tilt (angled down) | `ftilt_low` | 12-16 | 13/11 | Sakurai | 31/32 | 100 | - |  | 47 | 37 | 7 | -17 |  |
| Up tilt | `utilt` | 7-10 | 13 | 100 | 40 | 120 | - | slash | 54 | 50 | 7 | -35 |  |
| Down tilt | `dtilt` | 14-18 | 13 | Sakurai | 15 | 100 | - | slash | 59 | 55 | 7 | -33 |  |
|  |  | 27-31 | 10 | Sakurai | 12 | 100 | - | slash |  |  | 6 | -21 |  |
| Forward smash | `fsmash` | 29-33 | 24 | Sakurai/60 | 30 | 100 | - |  | 69 | 66 | 12 | -24 | charge hold frame 10 |
| Up smash | `usmash` | 16-21 | 20/17 | 90 | 40 | 86 | - | slash | 59 | 53 | 10 | -26 | charge hold frame 10; intangible 16-17 |
|  |  | 30 | 12 | 74 | 60 | 100 | - |  |  |  | 7 | -15 |  |
| Down smash | `dsmash` | 14-15, 17-18, 20-21, 23-24, 26-27, 29-30 | 2 | 150/190 | 40 | 50 | - | slash | 69 | 68 | 2 | -51 | charge hold frame 8; partly intangible 14-48 (12 bones) |
|  |  | 32 | 10 | 90 | 40 | 140 | - | slash |  |  | 6 | -29 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (6 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 8-23 | 13 | Sakurai | 20 | 80 | - |  | 49 | 48 | 7 | 30 | 15 | <8, >39 | -8 |  |
| Forward air | `fair` | 8-11 | 14/12/11 | Sakurai | 50 | 80 | - |  | 45 | 42 | 8 | 30 | 15 | <9, >30 | -7 |  |
| Back air | `bair` | 9-10 | 13 | 24 | 25 | 80 | - | slash | 49 | - | 7 | 35 | 17 | <9, >44 | -10 |  |
|  |  | 11-17 | 9 | Sakurai | 25 | 80 | - | slash |  |  | 6 |  |  |  | -11 |  |
| Up air | `uair` | 22-25 | 17 | 85 | 50 | 100 | - |  | 47 | 45 | 9 | 30 | 15 | <10, >39 | -6 |  |
| Down air | `dair` | 14-15, 17-18, 20-21, 23-24, 26-27, 29-30, 32-33, 35-36, 38-39 | 3 | 80 | 0 | 100 | 10 | slash | 79 | 78 | 3 | 40 | 20 | <14, >69 | -17 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 9-10 | 40 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 10-12 | 50 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 10 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 10 | 10 | 45 | 60 | 50 | - | - | 35 | 59 |  |
| Back throw | `bthrow` | 10 | 10 | 45 | 60 | 50 | - | - | 18 | 39 |  |
| Up throw | `uthrow` | 10 | 2 | 70 | 0 | 100 | 120 | - | 52 | 69 |  |
| Down throw | `dthrow` | 12 | 0 | 50 | 75 | 30 | - | - | 56 | 84 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Fire Breath, ground, Start | `special_n_start` | - | - | - | - | - | - | - | 21 | - | - | - |  |
| Neutral B: Fire Breath, ground | `special_n` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Neutral B: Fire Breath, ground, End | `special_n_end` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Neutral B: Fire Breath, air, Start | `special_air_n_start` | - | - | - | - | - | - | - | 21 | - | - | - |  |
| Neutral B: Fire Breath, air | `special_air_n` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Neutral B: Fire Breath, air, End | `special_air_n_end` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Side B: Koopa Klaw, ground, Start | `special_s_start` | 16-18 | 8/12/10 | 0/80 | 0/80 | 100/90 | - | grab/slash | 59 | - | 7 | - |  |
| Side B: Koopa Klaw, ground, Hit | `special_s_hit` | 18-19 | 4 | 80 | 0 | 0 | - | slash | 29 | - | 3 | - |  |
| Side B: Koopa Klaw, ground, Hit | `special_s_hit_303` | 18-19 | 4 | 80 | 0 | 0 | - | slash | 29 | - | 3 | - |  |
| Side B: Koopa Klaw, ground, EndF | `special_s_end_f` | 17-18 | 4 | 80 | 140 | 15 | - | slash | 39 | - | 3 | - |  |
| Side B: Koopa Klaw, ground, EndB | `special_s_end_b` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Side B: Koopa Klaw, air, Start | `special_air_s_start` | 16-18 | 8/12/10 | 0/80 | 0/80 | 100/90 | - | grab/slash | 59 | - | 7 | - |  |
| Side B: Koopa Klaw, air, Hit | `special_air_s_hit` | 18-19 | 4 | 80 | 0 | 0 | - | slash | 29 | - | 3 | - |  |
| Side B: Koopa Klaw, air, Hit | `special_air_s_hit_308` | 18-19 | 4 | 80 | 0 | 0 | - | slash | 29 | - | 3 | - |  |
| Side B: Koopa Klaw, air, EndF | `special_air_s_end_f` | 17-18 | 4 | 80 | 140 | 15 | - | slash | 39 | - | 3 | - |  |
| Side B: Koopa Klaw, air, EndB | `special_air_s_end_b` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Up B: Whirling Fortress, ground | `special_hi` | 5-6 | 13 | 80 | 90 | 80 | - |  | 79 | - | 7 | - | intangible 1-4 |
|  |  | 7-10, 11-14, 15-18, 19-22, 23-26 | 5 | 90 | 80 | 50 | - | slash |  |  | 4 | - |  |
|  |  | 27-30, 31-34, 35-38, 39-42, 43-46 | 3 | 70 | 50 | 50 | - | slash |  |  | 3 | - |  |
| Up B: Whirling Fortress, air | `special_air_hi` | 5-6 | 10 | 80 | 80 | 60 | - |  | 79 | - | 6 | - |  |
|  |  | 7-10, 11-14, 15-18, 19-22, 23-26 | 3 | 84 | 50 | 20 | - | slash |  |  | 3 | - |  |
|  |  | 27-30, 31-34, 35-38, 39-42, 43-46 | 2 | 84 | 50 | 20 | - | slash |  |  | 2 | - |  |
| Down B: Bowser Bomb, ground | `special_lw` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Down B: Bowser Bomb, air | `special_air_lw` | - | - | - | - | - | - | - | 31 | - | - | - |  |
| Down B: Bowser Bomb, ground, Landing | `special_lw_landing` | 1-2 | 8 | 76 | 60 | 72 | - |  | 59 | - | 5 | - |  |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 4-24 | - | 42 | 37 |  |
| Roll forward | `roll_forward` | intangible 4-19 | - | 39 | - |  |
| Roll backward | `roll_backward` | intangible 4-19 | - | 39 | - |  |
| Air dodge | `airdodge` | intangible 3-29 | - | 49 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-26 | 18-19, 25-26 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-27 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-27 | 10-11, 26-27 (6%) | 49 | - |  |
| Getup roll forward (face down) | `getup_roll_forward_facedown` | intangible 1-27 | - | 35 | - |  |
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-19 | - | 35 | - |  |
| Tech in place | `tech_in_place` | intangible 2-20 | - | 26 | - | starts 1 frame late (included) |
| Tech roll forward | `tech_roll_forward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Tech roll backward | `tech_roll_backward` | intangible 2-20 | - | 40 | - | starts 1 frame late (included) |
| Wall tech | `wall_tech` | - | - | 26 | - | starts 1 frame late (included) |
| Wall tech jump | `wall_tech_jump` | - | - | 40 | - | starts 1 frame late (included) |
| Ceiling tech | `ceiling_tech` | intangible 2-18 | - | 26 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-55 | - | 59 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 32 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-40 | 44-48 (10%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-34 | 7-34 (8%) | 54 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-59 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-33 | - | 49 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-17 | - | 17 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 30 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-3 | - | 3 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 34 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Up B | jump cancel | 6 | `special_hi` |
| Shield grab | direct | 9 | `grab` |
| Neutral air | jump | 16 | `nair` |
| Forward air | jump | 16 | `fair` |
| Back air | jump | 17 | `bair` |
| Up smash | jump cancel | 17 | `usmash` |
| Down air | jump | 22 | `dair` |
| Up air | jump | 30 | `uair` |
| Spot dodge | direct | intangible 4-24 of 42 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 39 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 39 | `roll_backward` |
| Wavedash | jump | actionable on frame 20 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Bowser indexed by [The Melee Library](https://www.meleelibrary.com/#bowser) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Bowser Techs Guide](https://www.youtube.com/watch?v=QHyqB6kTgso&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=4&t=0s) | Third Chair | Video guide on performing useful Bowser tech in 2020. |
| [Basic Bowser Tech](https://www.youtube.com/watch?v=MTbdXRcOAX4) | Chandy | This video explains basic Bowser techniques such as his Up-B OOS. The introduction also has and interesting discussion on Bowser's weaknesses. |
| [Fortress Landing](https://www.youtube.com/watch?v=0zNljm78Ec0) | Pangwell |  |
| [Fortresshog Tutorial](https://www.youtube.com/watch?v=-YXbjkkjj-g) | Synnett |  |
| [Aerial Fortress Interrupt](https://www.youtube.com/watch?v=2FPgMKssIkQ) | Synnett |  |
| [Melee 225: Advanced Bowser Tech [Competing in a 20XX World]](https://smashboards.com/threads/melee-225-advanced-bowser-tech-competing-in-a-20xx-world.430465/) | Pangwell | The post is a joke but there is a link to a Google Doc in the post that is the actual guide. |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Bowser (SSBM): https://www.ssbwiki.com/Bowser_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Bowser_(SSBM)/Up_special , /Side_special ,
  /Neutral_special , /Down_special , /Grab , /Up_throw , /Down_throw , /Forward_aerial ,
  /Up_aerial , /Forward_tilt , /Up_tilt , /Up_smash , /Down_smash
- SSBWiki, Whirling Fortress (including Fortress hogging): https://www.ssbwiki.com/Whirling_Fortress
- SSBWiki, Koopa Klaw: https://www.ssbwiki.com/Koopa_Klaw
- SSBWiki, Fire Breath (including Flame cancel): https://www.ssbwiki.com/Fire_Breath
- SSBWiki, Bowser Bomb: https://www.ssbwiki.com/Bowser_Bomb
- SSBWiki, Chain grab: https://www.ssbwiki.com/Chain_grab
- SSBWiki, Wavedash: https://www.ssbwiki.com/Wavedash
- SSBWiki, List of SSBM tier lists (NTSC): https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Pangwell, "Melee 225: Advanced Bowser Tech/Miscellaneous Guide" (Google Doc linked from
  the Smashboards thread):
  https://docs.google.com/document/d/1ZasAxA5AkM0uLQgMlVlDBc9RNiKDnjkLQ4QzGEFHa3M/edit
  (thread: https://smashboards.com/threads/melee-225-advanced-bowser-tech-competing-in-a-20xx-world.430465/)
- Schmooblidon, "Doc Advanced Tech Frame Data Megathread" (Magus chain grab chart, Bowser
  row): http://smashboards.com/threads/doc-advanced-tech-frame-data-megathread.378813/
- Frame data dump: `Bowser.json`
