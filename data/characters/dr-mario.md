---
schema: melee-character/v1
id: dr-mario
name: Dr. Mario
aliases: [Doc, Doctor Mario, Dr Mario]
tier: "B- (13th of 26), 2021 tier list"
archetype: [projectile, edgeguarder, chaingrab, punish-heavy, mixup]
related: [mario, luigi]
summary: Dr. Mario controls space with slow, damaging pills, converts grabs into chain grabs and juggles, and kills with forward air, forward smash, back throw and sheet or back air edgeguards, all while protecting one of the worst recoveries in the game.
key_tech: [pill-pressure, up-b-cancel, sheet-edgeguard, throw-chain-grab, throw-to-fair, bair-edgeguard, late-nair, tornado-rise, doc-ledgedash, uair-aerial-interrupt, lemon-grab]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlDr.dat
framedata: ../framedata/dr-mario.json
code: src/melee/ft/kinds/ftDrMario
specials:
  neutral_b: "Megavitamins (pills)"
  side_b: "Super Sheet (cape)"
  up_b: "Super Jump Punch"
  down_b: "Dr. Tornado"
attributes:
  weight: 100
  gravity: 0.095
  fall_speed: 1.7
  fast_fall_speed: 2.3
  jump_squat: 4
  jumps: 2
  walk_speed: 1.1
  dash_speed: 1.5
  run_speed: 1.5
  traction: 0.06
  air_speed: 0.9
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [2, 16, 4]
  jab2: [3, 19, 3]
  jab3: [5, 23, 6]
  dash_attack: [6, 38, 9]
  ftilt_high: [4, 30, 9]
  ftilt: [4, 30, 8]
  ftilt_low: [4, 30, 7]
  utilt: [4, 30, 10]
  dtilt: [5, 35, 9]
  fsmash_high: [12, 42, 20]
  fsmash: [12, 42, 19]
  fsmash_low: [12, 42, 18]
  usmash: [9, 40, 16]
  dsmash: [5, 38, 18]
  nair: [3, 46, 14]
  fair: [18, 60, 17]
  bair: [6, 29, 8]
  uair: [4, 30, 10]
  dair: [10, 38, 3]
  grab: [7, 31, 0]
  dash_grab: [11, 41, 0]
  pummel: [17, 25, 3]
  fthrow: [null, 28, 9]
  bthrow: [null, 67, 12]
  uthrow: [null, 40, 8]
  dthrow: [null, 40, 6]
  special_n: [null, 44, 0]
  special_air_n: [null, 44, 0]
  special_s: [12, 36, 12]
  special_s_air: [12, 36, 12]
  special_hi: [3, 38, 5]
  special_air_hi: [3, 38, 5]
  special_lw: [8, 80, 4]
  special_air_lw: [8, 80, 4]
oos:  # option: frame the hitbox is out
  special_hi: 4
  nair: 7
  grab: 7
  uair: 8
  bair: 10
  usmash: 10
  dair: 14
  fair: 22
resources: 17
# generated: end
---

# Dr. Mario

<!-- GENERATED:attributes -->
## Attributes

Read from `PlDr.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 100 |
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
| Air max horizontal speed | 0.9 |
| Air acceleration (base + stick) | 0.02 + 0.024 |
| Air friction | 0.016 |
| Normal landing lag | 4 |
| Shield size | 10.75 |
<!-- /GENERATED:attributes -->

## Overview

Dr. Mario ("Doc") is a clone of [Mario](mario.md) with the same dash and fall speed, slightly
faster air speed, and stronger versions of most attacks [wiki:Dr._Mario_(SSBM)]. In neutral he
throws pills (neutral B, Megavitamins), which do 8% each and bounce in a high, slow arc that
blocks approaches, and he moves in behind them with a long
[wavedash](../techniques/wavedash.md) and [SHFFL](../techniques/shffl.md)ed aerials. A grab
leads to a [chain grab](../techniques/chain-grab.md) on fastfallers and several mid-weights,
or to a juggle. Unlike Mario he has real kill moves: forward air ("the Fist"), a forward smash
with no weak spot, down smash, and the second strongest back throw in the game
[wiki:Dr._Mario_(SSBM)]. He also edgeguards well with side B (Super Sheet, usually just called
cape) and a low-angle back air. He dies because his recovery is short, linear and has almost no
mixups, and because his attacks have little reach, so characters with swords or strong aerial
walls ([Marth](marth.md), [Jigglypuff](jigglypuff.md)) keep him out and gimp him
[wiki:Dr._Mario_(SSBM)]. Execution is moderate; the hard parts are the up B cancel and
frame-tight chain grabs.

## Strengths and weaknesses

- **Strengths:**
  - Pills: 8% [wiki:Megavitamins], slow, bouncy, good hitstun for follow-ups.
  - Grab game: up throw and down throw chain grabs with measured windows (below); back throw
    kills.
  - Kill power from normals: fair 17% at 60° [fd], forward smash 19% with no sourspot [fd],
    down smash 18% [fd].
  - Edgeguarding: sheet reverses recoveries and has more vertical reach than Mario's cape;
    bair sends at 28° with high base knockback [fd].
  - Up B hits on frame 3 and can be cancelled on the ground into landing lag (up B cancel).
  - One of the better [ledgedashes](../techniques/ledgedash.md): up to 14 actionable
    intangible frames [lib:Doc Advanced Tech Frame Data Megathread].
- **Weaknesses:**
  - Recovery: cannot wall jump, sheet stalls for only about 4 frames, up B is short
    [wiki:Dr._Mario_(SSBM)].
  - Short reach on forward smash, up smash and grab.
  - More landing lag than Mario on every aerial (18/25/18/18/24 frames for
    nair/fair/bair/uair/dair, halved by an [L-cancel](../techniques/l-cancel.md)) [fd].
  - Struggles against disjointed hitboxes and campers [wiki:Dr._Mario_(SSBM)].

## Character tech

### Pill pressure

- **id:** `pill-pressure`
- **What:** Using aerial pills as moving cover. A pill is thrown during a jump so Doc lands
  actionable with the pill still travelling, then he acts behind it.
- **Inputs:** Short hop or full hop, neutral B, drift, land; optionally
  [waveland](../techniques/waveland.md) on landing. Repeat to keep two pills on screen (the
  wiki calls this "Pill Rush" [wiki:Dr._Mario_(SSBM)]).
- **Timing:** The pill leaves on frame 14 and the move lasts 43 frames. Doc's jumpsquat is 4
  frames and a full hop gives 52 airborne frames without fast fall, so a pill started on the
  first airborne frame leaves 9 frames spare. A pill started on airborne frame 1 still allows
  a fast fall from frame 34 on and a perfect waveland; a pill started as late as airborne
  frame 10 can still waveland on the last frame without fast falling
  [lib:Doc Advanced Tech Frame Data Megathread].
- **Used for:** Approaching, forcing shield (then grab), stopping dash dance approaches,
  covering landings, edgeguarding high recoveries.
- **Common errors:** Throwing the pill late so Doc lands in the special's animation; pilling
  at a range where the opponent can run under the arc and punish.
- **Drill idea:** Count pills thrown per 10 seconds where every landing is actionable; or
  require a grab on a CPU within N frames of the CPU shielding a pill.

### Up B cancel

- **id:** `up-b-cancel`
- **What:** A grounded up B (Super Jump Punch) can be cancelled right after its first hit, so
  Doc stays on the ground in landing lag instead of flying up into special fall
  [wiki:Super_Jump_Punch]. Only hit 1 comes out: 5% with set knockback, which knocks down
  every character at every percent [wiki:Dr._Mario_(SSBM)/Up_special].
- **Inputs:** Two methods [lib:Up-B Cancel Frame and Hitbox Data]:
  1. Up+B on frame 1; stick forward on frame 3; stick back on frame 4. Doc ends facing
     backward.
  2. Up+B on frame 1; stick anywhere but full forward on frame 2; stick back on frame 3; stick
     anywhere but back on frame 4.
- **Timing:** Hitbox and intangibility are on frame 3 only
  [wiki:Dr._Mario_(SSBM)/Up_special]. On whiff Doc is actionable on frame 34. If the hit
  connects, hitlag gives 3 extra frames to make the cancelling stick motion (it must be done
  by frame 7) and Doc is actionable on frame 37
  [lib:Up-B Cancel Frame and Hitbox Data]. From shield the fastest version is: jump input on
  frame 1, up+B on frame 2, hitbox on frame 4, actionable on frame 38 when it hits
  [lib:Up-B Cancel Frame and Hitbox Data].
- **Used for:** [Out of shield](../techniques/out-of-shield.md) punish that does not leave
  Doc helpless, combo extender, [tech chase](../techniques/tech-chase.md) hit (it always
  knocks down), and a "get off me" option. The set knockback means it never kills
  [wiki:Super_Jump_Punch].
- **Common errors:** Stick motion a frame late (full up B comes out and Doc is in special
  fall); method 1 input with the stick already forward on frame 2; tap-jumping into an aerial
  up B out of shield.
- **Drill idea:** CPU hits Doc's shield with an unsafe move; success when the up B hitbox
  connects on frame 4-6 after shield stun and Doc is grounded in landing lag afterward.

### Sheet edgeguard

- **id:** `sheet-edgeguard`
- **What:** Side B (Super Sheet) flips the opponent without knockback or interrupting their
  animation, so a recovering opponent faces away from the ledge and cannot grab it
  [wiki:Super_Sheet].
- **Inputs:** Side B toward the recovering opponent from the ledge, from a ledge hop, or
  while dropping offstage.
- **Timing:** Hitboxes on frames 12-14 in front and frames 14-15 behind Doc
  [lib:Doc Advanced Tech Frame Data Megathread]; reflector frames 6-33; 35 frames total
  [wiki:Dr._Mario_(SSBM)/Side_special]. Three hitboxes give it more vertical but less
  horizontal reach than Mario's cape [wiki:Dr._Mario_(SSBM)].
- **Used for:** Gimping [Fox](fox.md)/[Falco](falco.md) up B and side B,
  [Captain Falcon](captain-falcon.md), [Ganondorf](ganondorf.md), [Marth](marth.md),
  [Sheik](sheik.md), [Luigi](luigi.md)'s side B. Reflecting projectiles at 1.5x damage
  [wiki:Dr._Mario_(SSBM)/Side_special].
- **Common errors:** Mistimed startup (12 frames); sheeting an opponent with an active hitbox
  (Doc still gets hit [wiki:Cape]); using the sheet offstage and then lacking the distance to
  come back, since the stall lasts only frames 12-15 [wiki:Dr._Mario_(SSBM)].
- **Drill idea:** CPU Fox up Bs toward the ledge from random spots; success when the sheet
  connects and Fox dies.

### Throw chain grabs

- **id:** `throw-chain-grab`
- **What:** Up throw re-grabs fastfallers from 0%; down throw re-grabs fastfallers from mid
  percent to very high percent and several mid-weights from 0%.
- **Inputs:** Grab, throw, then: standing grab, turn-around grab, walk-turn grab, dash-pivot
  grab or dash [jump-cancel](../techniques/jump-cancel.md) grab depending on DI (directional
  influence, holding a direction to bend the launch angle).
- **Timing:** See the percent table under "Chain grabs and tech chases". Lag after release
  depends on the victim's weight: 17 frames against Fox and Falco, 23 against Captain Falcon,
  20 against Sheik, 25 against Bowser and DK
  [lib:Doc Advanced Tech Frame Data Megathread]. At the lowest working percents the full-DI
  cases are frame perfect: Falco grabbed at 27% and down thrown gives a 4-frame window for a
  standing re-grab on forward or no DI, 3 frames on slight behind DI, and a frame-perfect
  turn, dash, jump, grab on full behind DI; Fox grabbed at 49% gives 5 frames (no/slight
  forward DI), 4 (slight behind), 2 (full forward) or 1 (full behind)
  [lib:Doc Advanced Tech Frame Data Megathread].
- **Used for:** The main damage engine against Fox, Falco, Captain Falcon, Sheik, Roy, Link
  and Young Link; it ends in a kill throw, forward smash, or fair.
- **Common errors:** Grabbing forward when the opponent drifted slightly behind (walk-turn or
  dash-pivot grab covers both); down throwing fastfallers too early, when they can
  [tech](../techniques/teching.md) or DI behind and escape; ignoring port-priority and
  staleness effects.
- **Drill idea:** CPU Falco with random DI per throw; use up throw until the down throw
  window opens, then down throw; count re-grabs.

### Throw to forward air

- **id:** `throw-to-fair`
- **What:** Fair is slow (hits on frames 18-22 [fd]) but is Doc's strongest move, and both
  vertical throws set it up: up throw on fastfallers, down throw on non-fastfallers at higher
  percents [wiki:Dr._Mario_(SSBM)].
- **Inputs:** Throw, read DI, jump toward where the opponent will be, fair so the fist meets
  them near the top of their arc.
- **Timing:** Fair must be started about 18 frames before contact. The setups "are not always
  reliable" and can need a DI read [wiki:Dr._Mario_(SSBM)]. Exact percent windows: Unknown.
- **Used for:** Killing at roughly 80-100% and up [wiki:Dr._Mario_(SSBM)].
- **Common errors:** Jumping straight up when the opponent DIs away; starting fair late so it
  comes out after hitstun ends.
- **Drill idea:** CPU at 80-110% with random DI on the throw; success when fair connects
  before the CPU can act and the CPU dies.

### Back air edgeguard

- **id:** `bair-edgeguard`
- **What:** Bair's clean hit sends at 28° (a semi-spike: nearly horizontal, slightly up) with
  base knockback 43 and growth 65 [fd], which pushes recovering opponents out and low at any
  percent.
- **Inputs:** Run off or ledge-hop facing the stage, bair; often two bairs in one trip.
- **Timing:** Clean hit frames 6-8, late hit 9-16, 28 frames total, auto-cancels from frame
  19 [wiki:Dr._Mario_(SSBM)/Back_aerial]. The wiki notes Doc can bair twice offstage and
  still make it back [wiki:Dr._Mario_(SSBM)/Back_aerial].
- **Used for:** Edgeguarding characters that recover from the side or need their double jump.
  It does not kill onstage at realistic percents because of the low growth
  [wiki:Dr._Mario_(SSBM)].
- **Common errors:** Going too deep with Doc's poor recovery; hitting with the late hit (7%,
  normal angle [fd]).
- **Drill idea:** CPU recovers horizontally; success when two bairs connect and Doc regrabs
  the ledge.

### Late neutral air

- **id:** `late-nair`
- **What:** Doc's nair is a reversed "sex kick" (a lingering kick): 10% at 50° for the first
  part, then 14% at the normal angle from frame 20 of the move [fd]
  [lib:Full list of differences between Mario and Dr. Mario].
- **Inputs:** Start nair early (at the top of a short hop or while still rising) so the
  strong late part is what reaches the opponent.
- **Timing:** Active frames 3-31; strong hit from frame 20 [fd]. Landing lag 18, or 9
  L-cancelled [fd].
- **Used for:** A horizontal finisher at high percent, edgeguarding, and a long-lasting wall.
  The weak early hit is the combo and combo-breaker hit.
- **Common errors:** Hitting with the early weak hit when a kill was intended.
- **Drill idea:** CPU at kill percent near the ledge; success only if the 14% hitbox connects.

### Tornado rise

- **id:** `tornado-rise`
- **What:** Mashing B during an aerial down B (Dr. Tornado) gains height, once per airtime
  [wiki:Dr._Tornado]. The community name is PTP (perfect tornado press).
- **Inputs:** Down B, then separate B presses (one frame released between presses).
- **Timing:** Presses are read from frame 1 to frame 37; pressing on frame 38 or later does
  nothing. Six presses evenly spread over that window (first one by frame 5) are enough to
  rise from the ground to the top platform of Yoshi's Story; 18 presses (every other frame)
  is the maximum, and the difference between 12 and 18 is small. Even spacing matters more
  than count. Doc can double jump or up B on frame 80, and holding up from frame 77 buffers
  the double jump [lib:Doc Advanced Tech Frame Data Megathread].
- **Used for:** Recovery height and stalling. The tornado's last hit sends horizontally and
  can push opponents off the ledge [wiki:Dr._Mario_(SSBM)].
- **Common errors:** Mashing only at the start; forgetting it works once per airtime.
- **Drill idea:** Offstage start where jump + up B falls short; success when Doc reaches the
  ledge; report presses registered and their spacing.

### Doc ledgedash

- **id:** `doc-ledgedash`
- **What:** Drop from the ledge, double jump, air dodge onto the stage with ledge
  intangibility left over.
- **Inputs:** Drop (down or away), double jump toward the stage, diagonal air dodge.
- **Timing:** Best case 14 actionable intangible frames, with the air dodge possible on
  double-jump frame 5. Other ledge-grab situations allow the air dodge on double-jump frame
  6, 7 or 9 and give 10 to 13 frames. Which case applies depends on how Doc grabbed the ledge
  [lib:Doc Advanced Tech Frame Data Megathread].
- **Used for:** Getting off the ledge safely, punishing an opponent standing near the ledge.
- **Common errors:** Late double jump (less intangibility); air dodging too early and
  self-destructing.
- **Drill idea:** Standard ledgedash trainer: report actionable intangible frames.

### Up air aerial interrupt

- **id:** `uair-aerial-interrupt`
- **What:** Up air while rising through a platform lands Doc on the platform; with exact
  timing the first up air hitbox comes out before the cancel.
- **Inputs:** Full hop under a platform, up air, L-cancel.
- **Timing:** From a full hop under a low Battlefield platform there are 3 frames where up
  air is interrupted and only the third gives a hitbox: jump on frame 1, airborne on frame
  5, up air on frame 17, hitbox on frame 20, landing on frame 21, actionable on frame 30.
  From the ledge: drop frame 1, fast fall frame 2, double jump frame 5, up air frame 10,
  actionable frame 23 [lib:Doc Advanced Tech Frame Data Megathread].
- **Used for:** Platform tech chases and pressure; a fast route from ledge to platform.
- **Common errors:** One or two frames early gives no hitbox.
- **Drill idea:** CPU lies on a platform after a missed tech; success when the up air hits
  and Doc acts first.

### Lemon grab

- **id:** `lemon-grab`
- **What:** A dash attack toward the edge, cancelled on its first interruptible frame by
  turning, slides Doc off the stage backward so he grabs the ledge quickly
  [lib:Doc Advanced Tech Frame Data Megathread].
- **Inputs:** Dash attack so it ends at the edge; stick back on frame 37-38 of the dash
  attack; keep holding back; fast fall.
- **Timing:** Dash attack is interruptible from frame 38 [fd]. Ledge is grabbed around frame
  46 (frame 42 on Yoshi's Story because of the sloped edge)
  [lib:Doc Advanced Tech Frame Data Megathread].
- **Used for:** Dash attack hit near the ledge into an edgehog, or into a falling bair.
- **Common errors:** Stick back too early (no turn) or too late (slides off facing forward).
- **Drill idea:** Success when Doc is hanging on the ledge within 55 frames of starting the
  dash attack.

## Neutral game

- Pills first. They make the opponent shield, jump or commit; each of those is punishable
  with grab, an anti-air (up air, nair, bair) or a whiff punish.
- Wavedash and [dash dance](../techniques/dash-dance.md) to bait, then grab. The dump lists the
  standing grab box on frames 6-7 [fd]; for other characters the dump's grab frames are one
  earlier than SSBWiki's, so treat this as frame 7-8 until checked. Doc's grab reach is
  slightly worse than Mario's [wiki:Dr._Mario_(SSBM)].
- Forward tilt hits on frame 4 and has only 29 total frames [fd]: the main poke.
- Down tilt sends behind Doc at 150° [fd] and sets up edgeguards near the ledge.
- Jab 1 into down smash is a known link [wiki:Dr._Mario_(SSBM)].
- Doc wants a grab most of all. He does not want to chase a retreating aerial wall.

## Punish game

Grab is the centre: chain grab where it works, otherwise up throw or down throw into juggles
with up air (10%, 55°, no base knockback [fd]) and up tilt, ending with fair, forward smash,
up B (full version kills off the top late), or a throw offstage into an edgeguard. Up smash on
a grounded opponent spikes them into the floor so they bounce up with extra hitstun
[wiki:Dr._Mario_(SSBM)/Up_smash].

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| Up throw | Fox | 0-65% after throw | Re-grab | Jump-out impossible up to 65% with correct aim | [lib:Doc Advanced Tech Frame Data Megathread] |
| Up throw | Falco | 0-73% after throw | Re-grab | | [lib:Doc Advanced Tech Frame Data Megathread] |
| Up throw | Captain Falcon | 13-51% after throw | Re-grab | | [lib:Doc Advanced Tech Frame Data Megathread] |
| Down throw | Fox | 55-200%+ after throw | Re-grab | Any DI | [lib:Doc Advanced Tech Frame Data Megathread] |
| Down throw | Falco | 33-200%+ after throw | Re-grab | Any DI | [lib:Doc Advanced Tech Frame Data Megathread] |
| Down throw | Sheik | 0-65% after throw | Re-grab | Aim matters, you grab her leg | [lib:Doc Advanced Tech Frame Data Megathread] |
| Up throw | fastfallers | kill percent, typical 80%+ | Fair | DI read | [wiki:Dr._Mario_(SSBM)] |
| Down throw | non-fastfallers | higher percents | Fair, or short hop nair | DI read | [wiki:Dr._Mario_(SSBM)] |
| Up smash (grounded hit) | most | low-mid | Up air, up tilt, grab | Floor bounce | [wiki:Dr._Mario_(SSBM)/Up_smash] |
| Jab 1 | most | low | Down smash | | [wiki:Dr._Mario_(SSBM)] |
| Up B cancel hit | all | any | Tech chase | Always knocks down | [wiki:Dr._Mario_(SSBM)/Up_special] |
| Pill hit | most | any | Grab or aerial | Depends on distance | [wiki:Dr._Mario_(SSBM)] |

### Chain grabs and tech chases

All percents are the victim's damage **after** the throw (subtract about 6 for down throw or
8 for up throw to get the percent before it; throws stale). "Overall range" means a re-grab is
possible regardless of DI if timed and positioned correctly. Source for the whole table:
Magus420's chart quoted in [lib:Doc Advanced Tech Frame Data Megathread].

| Throw | Victim | Overall range | Notes |
|-|-|-|-|
| Up throw | Fox | 0-65 | After about 50 use walk-turn or dash-pivot grab on no DI |
| Up throw | Falco | 0-73 | After about 60 use walk-turn or dash-pivot grab on no DI |
| Up throw | Captain Falcon | 13-51 | |
| Down throw | Fox | 55-200+ | Jump-cancel grab also works from 45 on forward DI |
| Down throw | Falco | 33-200+ | Standing grab in front 6-33 if he never DIs behind |
| Down throw | Captain Falcon | 53-153 | |
| Down throw | Sheik | 0-65 | |
| Down throw | Roy | 0-50 | Grab behind you on no DI |
| Down throw | Link | 13-40 | Grab behind you on no DI |
| Down throw | Young Link | 0-39 | |
| Down throw | Pikachu, Pichu | 0-27 | Grab behind you on no DI |
| Down throw | Yoshi | 13-24 | Grab early to catch his head |
| Down throw | Bowser | 13-21 and 35-42 | |
| Down throw | Ganondorf | 13-16, 24-31, 35-36 | Small target (leg) |
| Down throw | Donkey Kong | 13-15 | |

- Practical route on Fox/Falco: up throw from 0%, switch to down throw once past the down
  throw threshold (Fox 55, Falco 33 after throw), continue to kill percent, then up throw
  fair, forward smash, or back throw.
- Escapes: before the down throw threshold, DI behind or a tech away gets out; on platform
  stages the victim can land on a platform and tech.
- Down throw on [Mr. Game & Watch](mr-game-and-watch.md) depends on port priority: with Doc
  in the lower port number the knockback is normal, otherwise it behaves like Fox's down
  throw [wiki:Dr._Mario_(SSBM)].
- Tech chase tools: up B cancel (covers tech in place and always knocks down), down smash
  (hits both sides, frames 5-6 and 14-15 [fd]), grab.

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Fair | most | 80-100%+ ("under 120%") | Usually from a throw; frame 18 startup | [wiki:Dr._Mario_(SSBM)] |
| Forward smash | most | just under 100% | Very short reach; frames 12-16 [fd] | [wiki:Dr._Mario_(SSBM)/Forward_smash] |
| Back throw | most | high percents, Unknown exact | Near the edge; second strongest back throw | [wiki:Dr._Mario_(SSBM)] |
| Down smash | most | Unknown | Frame 5; front hit 18% [fd] | [wiki:Dr._Mario_(SSBM)] |
| Late nair | most | high percents | 14% hitbox from frame 20 | [wiki:Dr._Mario_(SSBM)] [fd] |
| Up B (full, last hit) | most | high, off the top | Last hit 80°, growth 160 | [wiki:Dr._Mario_(SSBM)] |
| Sheet | linear recoveries | any | Offstage | [wiki:Super_Sheet] |
| Bair | most | any, offstage | Semi-spike, repeated hits | [wiki:Dr._Mario_(SSBM)/Back_aerial] |

- Standard edgeguard flow: hit or throw offstage, pill downward to force the double jump or
  an early up B, then choose edgehog, sheet, or ledge-hop bair.
- Down tilt near the ledge sends the opponent backward and low for an edgeguard.
- The tornado's last hit can knock an opponent off the ledge [wiki:Dr._Mario_(SSBM)].

## Recovery

- **Options:**
  - Double jump.
  - Up B: short, mostly vertical, slightly aimable; intangible on frame 3 only
    [wiki:Dr._Mario_(SSBM)/Up_special].
  - Sheet: a very small stall and rise once per airtime (stall frames 12-15)
    [wiki:Dr._Mario_(SSBM)].
  - Tornado rise: real height if mashed well, once per airtime.
  - Pills from high up to cover the descent.
  - Air dodge to the stage or ledge.
- **Mixups:** Tornado early versus late; up B to ledge versus onto stage; saving the double
  jump until after the tornado.
- **Weaknesses:** Everything is slow and short. The up B is easily edgehogged or hit from
  above; the tornado leaves him without a hitbox that protects him from below for long; no
  wall jump.

### Edgeguarding Dr. Mario

- Edgehog when he is below the ledge and has started up B: he rarely makes the stage.
- Hit him out of the tornado: it has small, briefly active hitboxes
  [wiki:Dr._Mario_(SSBM)].
- Any hit that removes the double jump at mid distance kills.
- Low-angle hits ([Sheik](sheik.md) fair/bair, [Marth](marth.md) dtilt/fsmash,
  [Fox](fox.md) shine) end stocks very early.
- A realistic CPU Doc: DI up and in, tornado mash when far, double jump late, up B to the
  ledge sweetspot.

## Defense and out of shield

- Up B cancel out of shield is the signature option: hit on frame 4 from shield, no helpless
  state [lib:Up-B Cancel Frame and Hitbox Data].
- Shield grab, nair out of shield (frame 3 hitbox after a 4-frame jumpsquat
  [lib:Doc Advanced Tech Frame Data Megathread]), wavedash out of shield.
- Nair and up B are his combo breakers.
- [Crouch cancel](../techniques/crouch-cancel.md) into down smash (frame 5) or grab at low
  percent.
- Weak to spaced sword pressure and to being carried offstage, since any offstage situation
  is dangerous for him.

## As the training dummy

- Same weight and fall speed as Mario; slightly bigger torso hurtbox
  [wiki:Dr._Mario_(SSBM)]. A mid-weight, mid-fall body.
- Peach's down throw chain grab does not work on him (he can jump out)
  [wiki:Chain_grab]; Sheik's down throw is a tech chase, not a chain grab, on him
  [wiki:Chain_grab].
- In Bowser's side B forward throw to up air combo, Doc can jump out, but a double-jump up
  air catches the jump [wiki:Bowser_(SSBM)/Up_aerial].
- Escape options a CPU should use: nair, up B, double jump, DI away.
- Best use as a dummy: edgeguard practice, since his recovery has few branches (tornado or
  not, sheet or not, up B timing).

## Matchup notes

### vs Fox and Falco

- Doc's best top-tier matchups in terms of reward: chain grabs to kill percent, sheet and bair
  edgeguards, pills that stop some approaches.
- He still loses neutral to speed and lasers, and is gimped by shine and dair.

### vs Marth

- Outranged; Marth's grab and juggle game is strong on a mid-faller and his edgeguard on Doc
  is simple. Doc needs pills to force a mistake, then a grab near the ledge.

### vs Sheik

- Down throw chain grabs Sheik from 0 to about 65% after throw
  [lib:Doc Advanced Tech Frame Data Megathread], which is Doc's main equaliser. Sheik's
  needles and edgeguards are the problem.

### vs Jigglypuff

- The wiki names Jigglypuff as a character Doc has "limited counterplay" against: her aerial
  wall outranges him and he cannot chase her [wiki:Dr._Mario_(SSBM)].

### vs Captain Falcon

- The Doc boards treat Falcon as a hard matchup [lib:Doctor Mario Info Archive and
  Discussion] (thread index only). Up throw chain grab works 13-51% and down throw 53-153%
  after throw [lib:Doc Advanced Tech Frame Data Megathread].

## Drill seeds

### Up B cancel out of shield

- **id:** `dr-mario-upb-cancel-oos`
- **Goal:** Execute the fastest cancelled up B from shield and follow up.
- **Player:** Dr. Mario
- **CPU:** Fox, Falco, Sheik, Peach
- **Setup:** Doc shielding at center stage, CPU at 30%, in aerial range.
- **CPU behaviour:** SHFFL aerial onto shield, then randomly grabs, jabs, or (Fox/Falco)
  shines late.
- **Success:** Up B hitbox connects, Doc ends in grounded landing lag (cancel succeeded), and
  a follow-up hit or grab connects on the knocked-down CPU.
- **Fail:** Full up B (Doc airborne/helpless), Doc hit, or no follow-up.
- **Variations:** Method 1 versus method 2 inputs; no-hit practice mode that only checks the
  frame 3/4 stick motion; CPU techs in place/away/in after the knockdown.
- **Data needed:** Up B cancel frame windows [lib:Up-B Cancel Frame and Hitbox Data]; hit 1
  set knockback 150 [fd]; shield stun of CPU aerials.

### Fastfaller chain grab with throw switch

- **id:** `dr-mario-chaingrab-spacies`
- **Goal:** Up throw chain from 0%, switch to down throw at the right percent, reach kill
  percent.
- **Player:** Dr. Mario
- **CPU:** Fox, Falco
- **Setup:** Final Destination, CPU grabbed at 0%.
- **CPU behaviour:** Random DI each throw; jumps/shines/techs at first opportunity.
- **Success:** CPU reaches 90% without acting.
- **Fail:** CPU escapes.
- **Variations:** Only up throw (stop at 65 Fox / 73 Falco after throw); only down throw
  starting at 55 (Fox) or 33 (Falco); DI fixed to full behind for frame-perfect practice.
- **Data needed:** Magus chain grab table above; release lag 17 frames on Fox/Falco
  [lib:Doc Advanced Tech Frame Data Megathread].

### Down throw chain grab on Sheik

- **id:** `dr-mario-dthrow-sheik`
- **Goal:** Re-grab Sheik's small leg hurtbox with correct facing.
- **Player:** Dr. Mario
- **CPU:** Sheik (also Roy, Link, Young Link, Pikachu)
- **Setup:** Final Destination, CPU grabbed at 0%.
- **CPU behaviour:** Random slight DI in front/behind; jumps out when possible.
- **Success:** Re-grabs continue until 65% after throw.
- **Fail:** Jump out or whiffed grab.
- **Variations:** Force walk-turn grab; change victim to Roy (0-50) or Link (13-40).
- **Data needed:** Magus table; Sheik release lag 20 frames
  [lib:Doc Advanced Tech Frame Data Megathread].

### Throw into the Fist

- **id:** `dr-mario-throw-fair`
- **Goal:** Read DI after up throw or down throw and land fair for the kill.
- **Player:** Dr. Mario
- **CPU:** Fox/Falco/Captain Falcon (up throw), Marth/Sheik/Peach (down throw)
- **Setup:** CPU grabbed at a percent chosen in 80-120%, mid stage.
- **CPU behaviour:** Random DI (in, away, none), air dodges or jumps when actionable.
- **Success:** Fair connects before the CPU acts; bonus if it kills.
- **Fail:** Fair whiffs or CPU acts first.
- **Variations:** Show or hide the DI direction; platform stages.
- **Data needed:** Fair hit frames 18-22 and knockback [fd]; throw knockback
  (up throw growth 80, down throw growth 40 [wiki:Dr._Mario_(SSBM)]); victim hitstun.

### Sheet the recovery

- **id:** `dr-mario-sheet-edgeguard`
- **Goal:** Sheet timing against up B recoveries.
- **Player:** Dr. Mario
- **CPU:** Fox, Falco, Captain Falcon, Marth
- **Setup:** Doc on stage near the ledge; CPU offstage below the ledge without a double jump.
- **CPU behaviour:** Recovers with up B aimed at the ledge, or (Fox/Falco) side B at ledge
  height, chosen at random.
- **Success:** CPU is reversed and dies. Against side B, success is any hit or edgehog that
  kills.
- **Fail:** CPU reaches ledge or stage; Doc is hit.
- **Variations:** Doc starts hanging on the ledge and must ledge-hop sheet.
- **Data needed:** Sheet hitboxes 12-14 front, 14-15 behind
  [lib:Doc Advanced Tech Frame Data Megathread]; CPU up B timings.

### Double back air edgeguard

- **id:** `dr-mario-bair-edgeguard`
- **Goal:** Hit two bairs offstage and return.
- **Player:** Dr. Mario
- **CPU:** Peach, Jigglypuff, Samus, Marth (horizontal recoveries)
- **Setup:** CPU launched offstage at 60%, at ledge height, with a double jump.
- **CPU behaviour:** Drifts back toward the stage using jump and recovery move.
- **Success:** Two clean bairs (8% hitbox) connect and Doc grabs the ledge.
- **Fail:** Doc dies or CPU returns.
- **Variations:** Ledge-hop bair from a ledge hang; one bair then sheet.
- **Data needed:** Bair frames 6-8 clean, 28 total, auto-cancel 19+
  [wiki:Dr._Mario_(SSBM)/Back_aerial]; Doc's jump and up B distances (attributes).

### Pill approach to grab

- **id:** `dr-mario-pill-grab`
- **Goal:** Land actionable behind a pill and convert a shielded pill into a grab.
- **Player:** Dr. Mario
- **CPU:** Marth, Sheik, Captain Falcon
- **Setup:** Opposite thirds of Final Destination.
- **CPU behaviour:** Dash dances; shields pills in range; punishes Doc if he lands in the
  pill animation near it.
- **Success:** Grab connects within 20 frames of the pill hitting shield or body.
- **Fail:** Doc is hit or grabbed; pill thrown with landing lag.
- **Variations:** Short hop versus full hop pills; CPU sometimes jumps over the pill (answer
  with up air or bair).
- **Data needed:** Pill release frame 14, move length 43, full hop 52 airborne frames
  [lib:Doc Advanced Tech Frame Data Megathread]; pill speed and arc.

### Tornado recovery

- **id:** `dr-mario-tornado-recovery`
- **Goal:** Gain height with evenly spaced B presses and recover.
- **Player:** Dr. Mario
- **CPU:** none, or an edgehogger that takes the ledge when Doc starts up B
- **Setup:** Doc offstage, below ledge height, double jump available, at a distance where
  jump + up B alone fails.
- **CPU behaviour:** Optional edgehog on up B startup.
- **Success:** Doc grabs the ledge or lands on stage.
- **Fail:** Doc dies.
- **Variations:** Require at least 6, 9 or 12 registered presses; remove the double jump.
- **Data needed:** Press window frames 1-37, actionable frame 80
  [lib:Doc Advanced Tech Frame Data Megathread].

### Ledgedash

- **id:** `dr-mario-ledgedash`
- **Goal:** Maximise actionable intangible frames from the ledge.
- **Player:** Dr. Mario
- **CPU:** any, standing near the ledge and attacking on a timer
- **Setup:** Doc hanging on the ledge.
- **CPU behaviour:** Forward smashes the ledge region at a fixed delay.
- **Success:** Doc is grounded and actionable with 8 or more intangible frames left and hits
  the CPU.
- **Fail:** Self-destruct, or hit by the CPU.
- **Variations:** Threshold 10, 12, 14 frames.
- **Data needed:** Ledgedash cases and maxima
  [lib:Doc Advanced Tech Frame Data Megathread].

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlDr.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/dr-mario.json`](../framedata/dr-mario.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 2-3 | 4 | 83/85 | 0 | 100 | 30 |  | 15 | - | 3 | -10 |  |
| Jab 2 | `jab2` | 3-4 | 3 | 83/85 | 0 | 100 | 30 |  | 18 | - | 3 | -12 | starts 1 frame late (included) |
| Jab 3 | `jab3` | 5-9 | 6 | Sakurai | 18 | 100 | - |  | 22 | - | 4 | -13 | starts 1 frame late (included) |
| Dash attack | `dash_attack` | 6-9 | 9 | 80 | 70 | 30 | - |  | 43 | 38 | 6 | -25 |  |
|  |  | 10-25 | 8/9 | 85/80 | 60/70 | 50/30 | - |  |  |  | 6 | -21 |  |
| Forward tilt (angled up) | `ftilt_high` | 4-8 | 9 | Sakurai | 11 | 100 | - |  | 29 | - | 6 | -19 |  |
| Forward tilt | `ftilt` | 4-8 | 8 | Sakurai | 10 | 100 | - |  | 29 | - | 5 | -20 |  |
| Forward tilt (angled down) | `ftilt_low` | 4-8 | 7 | Sakurai | 9 | 100 | - |  | 29 | - | 5 | -20 |  |
| Up tilt | `utilt` | 4 | 10 | Sakurai | 20 | 95 | - |  | 30 | 30 | 6 | -19 |  |
|  |  | 5-13 | 8 | 100 | 30 | 122/120/118 | - |  |  |  | 5 | -19 |  |
| Down tilt | `dtilt` | 5-8 | 9 | 150 | 20 | 82 | - |  | 34 | - | 6 | -23 |  |
| Forward smash (angled up) | `fsmash_high` | 12-16 | 20 | Sakurai | 30 | 97 | - | electric | 41 | - | 10 | -19 | charge hold frame 5 |
| Forward smash | `fsmash` | 12-16 | 19 | Sakurai | 30 | 97 | - | electric | 41 | - | 10 | -19 | charge hold frame 5 |
| Forward smash (angled down) | `fsmash_low` | 12-16 | 18 | Sakurai | 30 | 97 | - | electric | 41 | - | 10 | -19 | charge hold frame 5 |
| Up smash | `usmash` | 9-10 | 16 | 83/259 | 35 | 95 | - |  | 39 | - | 9 | -21 | charge hold frame 7; partly intangible 9-11 (1 bone) |
|  |  | 11 | 13 | 76/259 | 35 | 95 | - |  |  |  | 7 | -21 |  |
| Down smash | `dsmash` | 5-6 | 18/17 | Sakurai | 45 | 75 | - |  | 37 | - | 10 | -22 | charge hold frame 3 |
|  |  | 14-15 | 15/13 | Sakurai | 40 | 75 | - |  |  |  | 8 | -15 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 3-19 | 10 | 50 | 20 | 100 | - |  | 45 | - | 6 | 18 | 9 | <3, >35 | -3 |  |
|  |  | 20-31 | 14 | Sakurai | 20 | 100 | - |  |  |  | 8 |  |  |  | -1 |  |
| Forward air | `fair` | 18-22 | 17/16 | 60 | 50/40 | 100 | - |  | 74 | 60 | 9 | 25 | 12 | <3, >42 | -3 |  |
| Back air | `bair` | 6-8 | 8 | 28 | 43 | 65 | - |  | 28 | - | 5 | 18 | 9 | <6, >18 | -4 |  |
|  |  | 9-16 | 7 | Sakurai | 20 | 100 | - |  |  |  | 5 |  |  |  | -4 |  |
| Up air | `uair` | 4-9 | 10 | 55 | 0 | 100 | - |  | 33 | 30 | 6 | 18 | 9 | <2, >15 | -3 |  |
| Down air | `dair` | 10-11, 13-14, 16-17, 19-20, 22-23, 25-26, 28-29 | 3 | 80 | 0 | 100 | 30 |  | 38 | 38 | 3 | 24 | 12 | <6, >32 | -9 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 11-12 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 17 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 9 | 9 | 45 | 60 | 72 | - | - | 12 | 27 |  |
| Back throw | `bthrow` | 12 | 12 | 45 | 80 | 72 | - | - | 44 | 66 |  |
| Up throw | `uthrow` | 8 | 8 | 90 | 70 | 80 | - | - | 18 | 39 |  |
| Down throw | `dthrow` | 6 | 6 | 90 | 75 | 40 | - | - | 18 | 39 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Megavitamins (pills), ground | `special_n` | - | - | - | - | - | - | - | 43 | - | - | - | spawns article/projectile on 14 |
| Neutral B: Megavitamins (pills), air | `special_air_n` | - | - | - | - | - | - | - | 43 | - | - | - | spawns article/projectile on 14 |
| Side B: Super Sheet (cape), ground | `special_s` | 12-14 | 12/10 | 110 | 30 | 80 | - | cape | 35 | - | 7 | - |  |
| Side B: Super Sheet (cape), ground, Air | `special_s_air` | 12-14 | 12/10 | 110 | 30 | 80 | - | cape | 35 | - | 7 | - |  |
| Up B: Super Jump Punch, ground | `special_hi` | 3 | 5 | 70/90 | 0 | 100 | 150 | coin | 37 | - | 4 | - | intangible 3 |
|  |  | 4-7, 8-11 | 2 | 74/78 | 0 | 100 | 140/180 | coin |  |  | 2 | - |  |
|  |  | 12-15, 16-19 | 2 | 72/78 | 0 | 100 | 90/120 | coin |  |  | 2 | - |  |
|  |  | 20-21 | 3 | 80 | 40 | 160 | - | coin |  |  | 3 | - |  |
| Up B: Super Jump Punch, air | `special_air_hi` | 3 | 5 | 70/90 | 0 | 100 | 150 | coin | 37 | - | 4 | - | intangible 3 |
|  |  | 4-7, 8-11 | 2 | 74/78 | 0 | 100 | 140/180 | coin |  |  | 2 | - |  |
|  |  | 12-15, 16-19 | 2 | 72/78 | 0 | 100 | 90/120 | coin |  |  | 2 | - |  |
|  |  | 20-21 | 3 | 80 | 40 | 160 | - | coin |  |  | 3 | - |  |
| Down B: Dr. Tornado, ground | `special_lw` | 8 | 3 | 140 | 0 | 0 | 40 |  | 79 | - | 3 | - |  |
|  |  | 14, 21 | 2 | 180 | 40 | 0 | 5 |  |  |  | 2 | - |  |
|  |  | 28-29 | 3 | 100 | 40 | 0 | 5 |  |  |  | 3 | - |  |
|  |  | 38-39 | 4 | Sakurai | 75 | 120 | - |  |  |  | 3 | - |  |
| Down B: Dr. Tornado, air | `special_air_lw` | 8 | 3 | 140 | 0 | 0 | 40 |  | 79 | - | 3 | - |  |
|  |  | 14, 21 | 2 | 160 | 40 | 0 | 1 |  |  |  | 2 | - |  |
|  |  | 28-29 | 1 | 100 | 50 | 0 | 1 |  |  |  | 2 | - |  |
|  |  | 38-39 | 4 | Sakurai | 80 | 120 | - |  |  |  | 3 | - |  |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-15 | - | 22 | 20 |  |
| Roll forward | `roll_forward` | intangible 4-19 | - | 31 | - |  |
| Roll backward | `roll_backward` | intangible 4-19 | - | 31 | - |  |
| Air dodge | `airdodge` | intangible 4-29 | - | 48 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-25 | 20-21, 24-25 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-21 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-22 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-23 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-26 | 19-20, 25-26 (6%) | 49 | - |  |
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
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-36 | 40-44 (10%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-20 | 24-36 (8/6%) | 55 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-56 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-27 | - | 49 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-19 | - | 19 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 29 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-15 | - | 15 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 23 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Up B | jump cancel | 4 | `special_hi` |
| Neutral air | jump | 7 | `nair` |
| Shield grab | direct | 7 | `grab` |
| Up air | jump | 8 | `uair` |
| Back air | jump | 10 | `bair` |
| Up smash | jump cancel | 10 | `usmash` |
| Down air | jump | 14 | `dair` |
| Forward air | jump | 22 | `fair` |
| Spot dodge | direct | intangible 2-15 of 22 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 16 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Dr. Mario indexed by [The Melee Library](https://www.meleelibrary.com/#doctor-mario) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Doctor Mario Melee Techs Guide](https://www.youtube.com/watch?v=P6oz-mCtFuQ&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=17&t=0s) | Third Chair | Video guide on performing useful Doctor Mario tech in 2020. |
| [Doc Advanced Tech Frame Data Megathread](http://smashboards.com/threads/doc-advanced-tech-frame-data-megathread.378813/) | Schmooblidon | Lots of frame data on Doctor Mario (and some of the other Mario Bros). |
| [Port Priority’s Effect on Doctor Mario’s Chaingrab](http://smashboards.com/threads/how-port-priority-affects-throws.393128/#post-18676758) | Schmooblidon |  |
| [Doc General Discussion: Ask and ye shall receive ft. otg and Shroomed](http://smashboards.com/threads/doc-general-discussion-ask-and-ye-shall-receive-ft-otg-and-shroomed.172019/) | community |  |
| [Doctor Mario Hitboxes and Frame Data](http://smashboards.com/threads/doctor-mario-hitboxes-and-frame-data.309998/) | Stratocaster, Standardtoaster, and SuperDoodleMan |  |
| [Doctor Mario Info Archive and Discussion](http://smashboards.com/threads/doctor-mario-info-archive-and-discussion-miniscule-update-8d.218357/) | Desh | Collection of old information about Doctor Mario. Chaingrab info by Magus, move discussion, Doc in teams, matchups, and edgeguarding. |
| [(100% Complete) Doc. vs. the World (of Nintendo) - A Character Matchup Guide](http://smashboards.com/threads/100-complete-doc-vs-the-world-of-nintendo-a-character-matchup-guide.115319/) | SmashMac | A somewhat old thread containing matchup guides and general tips on playing Doc. |
| [Doctor Mario Matchup Guide](http://smashboards.com/threads/doctor-mario-matchup-guide.260929/) | Dogysamich |  |
| [Not to be Taken Orally: Doc Guide](http://smashboards.com/threads/not-to-be-taken-orally-doc-guide-by-cyphus-plus-tutorial-vid-by-smashmac.55939/) | Cyphus |  |
| [The Doctor’s Checkup](https://www.youtube.com/watch?v=qp_qhEx3zKE) | SmashMac | Video showing various Doctor Mario techniques. |
| [How to Up-B Cancel](https://www.youtube.com/watch?v=oWMDcnbPgy0&feature=youtu.be) | Mr. Lemon |  |
| [Up-B Cancel Frame and Hitbox Data](http://smashboards.com/threads/up-b-cancel-frame-and-hitbox-data-complete-with-gifs-and-now-oos-data.378468/) | Schmooblidon |  |
| [Uair Platform Cancel/No Impact Land + New Stuff](http://smashboards.com/threads/up-air-platform-cancel-no-impact-land-new-stuff.377831/) | Schmooblidon |  |
| [Doc Upb Cancel Edge/Teeter Cancel Tricks](https://www.reddit.com/r/SSBM/comments/4vzc7x/doc_upb_cancel_edgeteeter_cancel_tricks/) | Schmooblidon | Wacky tricks with Doc's up-b cancel. |
| [Full list of differences between Mario and Dr. Mario](https://www.reddit.com/r/SSBM/comments/6d00m3/full_list_of_differences_between_mario_and_dr/) | Palika |  |
| [Clean 2009 Dr.Mario edgeguard's ft Shroomed, Homemade Waffles, and dPsychMD](https://youtu.be/LCKMAvVld8k) | The Melee Plug |  |
| [Doctor Mario Melee Chaingrab Guide](https://www.youtube.com/watch?v=-OwJ8u_yBAY&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=18&t=0s) | Third Chair |  |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Dr. Mario (SSBM): https://www.ssbwiki.com/Dr._Mario_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Dr._Mario_(SSBM)/Up_special , /Side_special ,
  /Down_special , /Forward_smash , /Up_smash , /Back_aerial , /Forward_tilt
- SSBWiki, Megavitamins: https://www.ssbwiki.com/Megavitamins
- SSBWiki, Super Sheet: https://www.ssbwiki.com/Super_Sheet
- SSBWiki, Cape: https://www.ssbwiki.com/Cape
- SSBWiki, Super Jump Punch (Up-B cancel section): https://www.ssbwiki.com/Super_Jump_Punch
- SSBWiki, Dr. Tornado: https://www.ssbwiki.com/Dr._Tornado
- SSBWiki, Chain grab: https://www.ssbwiki.com/Chain_grab
- SSBWiki, Bowser (SSBM)/Up aerial: https://www.ssbwiki.com/Bowser_(SSBM)/Up_aerial
- SSBWiki, List of SSBM tier lists (NTSC): https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Schmooblidon, "Doc Advanced Tech Frame Data Megathread", including Magus420's chain grab
  chart (via web.archive.org):
  http://smashboards.com/threads/doc-advanced-tech-frame-data-megathread.378813/
- Schmooblidon, "Up-B Cancel Frame and Hitbox Data" (via web.archive.org):
  http://smashboards.com/threads/up-b-cancel-frame-and-hitbox-data-complete-with-gifs-and-now-oos-data.378468/
- Palika, "Full list of differences between Mario and Dr. Mario" (via web.archive.org):
  https://www.reddit.com/r/SSBM/comments/6d00m3/full_list_of_differences_between_mario_and_dr/
- Desh, "Doctor Mario Info Archive and Discussion" (index post only, via web.archive.org):
  http://smashboards.com/threads/doctor-mario-info-archive-and-discussion-miniscule-update-8d.218357/
- Frame data dump: `Dr Mario.json`
