---
schema: melee-character/v1
id: zelda
name: Zelda
aliases: ["Princess Zelda", "Sheik's other form"]
tier: "D (24th of 26), 2021 PG Stats tier list (13th official NTSC list)"
archetype: [floaty, glass-cannon, punish-heavy, mixup, technical]
related: [sheik]
summary: Zelda waits, walls with fast transcendent moves, and ends stocks early with a sweetspot Lightning Kick (forward or back air) off a grab, down tilt, platform movement or a ledge trap.
key_tech: [lightning-kick-sweetspot, fair-aerial-interrupt, ledgehop-kick, ledge-kick, dtilt-chain, usmash-oos, nayrus-love, farores-wind-recovery, farores-ledge-stall, transform-to-sheik]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlZd.dat
framedata: ../framedata/zelda.json
code: src/melee/ft/kinds/ftZelda
specials:
  neutral_b: "Nayru's Love"
  side_b: "Din's Fire"
  up_b: "Farore's Wind"
  down_b: "Transform"
attributes:
  weight: 90
  gravity: 0.073
  fall_speed: 1.4
  fast_fall_speed: 1.85
  jump_squat: 6
  jumps: 2
  walk_speed: 0.7
  dash_speed: 1.1
  run_speed: 1.1
  traction: 0.1
  air_speed: 0.95
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [11, 27, 2]
  dash_attack: [6, 36, 13]
  ftilt_high: [12, 37, 13]
  ftilt_mid_high: [12, 37, 13]
  ftilt: [12, 37, 13]
  ftilt_mid_low: [12, 37, 13]
  ftilt_low: [12, 37, 13]
  utilt: [10, 40, 11]
  dtilt: [5, 30, 8]
  fsmash: [16, 40, 14]
  usmash: [5, 51, 5]
  dsmash: [4, 32, 11]
  nair: [6, 42, 5]
  fair: [8, 36, 20]
  bair: [5, 33, 20]
  uair: [14, 55, 13]
  dair: [14, 43, 8]
  grab: [12, 31, 0]
  dash_grab: [12, 41, 0]
  pummel: [7, 26, 3]
  fthrow: [null, 50, 12]
  bthrow: [null, 50, 11]
  uthrow: [null, 50, 11]
  dthrow: [24, 65, 2]
  special_n: [12, 60, 5]
  special_air_n: [12, 60, 5]
  special_s_start: [null, 25, 0]
  special_s_loop: [null, 15, 0]
  special_s_end: [null, 40, 0]
  special_air_s_start: [null, 25, 0]
  special_air_s_loop: [null, 15, 0]
  special_air_s_end: [null, 40, 0]
  special_hi_start: [10, 34, 4]
  special_hi: [1, 22, 4]
  special_air_hi_start: [10, 34, 4]
  special_air_hi: [1, 62, 4]
  special_lw: [null, 44, 0]
  special_lw2: [null, 26, 0]
  special_air_lw: [null, 44, 0]
  special_air_lw2: [null, 26, 0]
oos:  # option: frame the hitbox is out
  usmash: 6
  bair: 11
  special_hi_start: 11
  nair: 12
  grab: 12
  fair: 14
  uair: 20
  dair: 20
resources: 4
# generated: end
---

# Zelda

<!-- GENERATED:attributes -->
## Attributes

Read from `PlZd.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 90 |
| Gravity | 0.073 |
| Terminal fall speed | 1.4 |
| Fast-fall speed | 1.85 |
| Jump squat (frames before airborne) | 6 |
| Full hop / short hop initial Y speed | 2.1 / 1.6 |
| Air jump Y multiplier | 0.86 |
| Jumps | 2 |
| Walk max speed | 0.7 |
| Dash initial speed / run max speed | 1.1 / 1.1 |
| Ground friction (traction) | 0.1 |
| Air max horizontal speed | 0.95 |
| Air acceleration (base + stick) | 0.01 + 0.038 |
| Air friction | 0.005 |
| Normal landing lag | 4 |
| Shield size | 11.875 |
<!-- /GENERATED:attributes -->

## Overview

Zelda is the slow, floaty half of the Zelda/[Sheik](sheik.md) pair; down B swaps between them
in the middle of a match. She has the slowest dash in the game, a very short
[wavedash](../techniques/wavedash.md), a high short hop and no useful projectile, so she cannot
approach [wiki:Zelda_(SSBM)]. What she has is power and speed at close range: forward air and
back air ("Lightning Kicks") do 20% and can KO "as low as 50%" when the small sweetspot at the
foot connects, back air hits on frame 5, down smash on frame 4 and up smash on frame 5
[wiki:Zelda_(SSBM), fd]. She wins by defending a small area, punishing an approach with a
grab, down tilt, dash attack or a kick, and then killing very early. She loses neutral to
almost every relevant character, is tall, light-feeling and floaty (easy to juggle and to KO
off the top), and her up B recovery is long but slow and exact. In practice most Zelda seen in
tournament is a Sheik who transformed offstage to recover [wiki:Zelda_(SSBM)]. Modern Zelda
play leans on platform movement tech (aerial interrupts, ledge kicks) to make up for her
ground speed [lib:The Profane Tome].

## Strengths and weaknesses

- **Strengths:**
  - Lightning Kick sweetspot: 20%, base knockback 30, growth 96 on both fair and bair [fd];
    among the strongest aerials in the game.
  - Fast close-range moves: dsmash frame 4 (interruptible from frame 32), up smash frame 5,
    bair frame 5, dtilt frame 5 [fd].
  - Many moves have transcendent priority (they do not clank), including jab, tilts, smashes,
    nair, fair, bair and up air [wiki:Zelda_(SSBM)].
  - Up tilt: 11%, active frames 10-24, base 65 growth 105 [fd]; a long-lasting anti-air and a
    reliable KO move.
  - Strong throws: forward 12%, back 11%, up 11% [wiki:Zelda_(SSBM)]; up throw sets up kicks.
  - Long recovery (Farore's Wind) and Nayru's Love (neutral B), which is invincible early and
    reflects projectiles [wiki:Zelda_(SSBM)].
  - Weight 90, the same as Sheik and Peach [wiki:Zelda_(SSBM)].
- **Weaknesses:**
  - Worst ground mobility: initial dash 1.1 (slowest), walk 0.7, traction 0.1, jump squat 6
    frames [wiki:Zelda_(SSBM)].
  - Slow grab: the grab box is out on frames 11-12 [fd].
  - Kick sourspots have priority and do only 10% with no base knockback [fd,
    wiki:Lightning_Kick]; a mis-spaced kick is punished.
  - Multi-hit smashes (fsmash, up smash) and nair can be escaped with SDI (smash directional
    influence, tapping the stick during hitlag to shift position) [wiki:Zelda_(SSBM)].
  - Din's Fire (side B) is slow, telegraphed and leaves her helpless in the air
    [wiki:Din's_Fire].
  - Tall and floaty (fall speed 1.4): juggled and KO'd off the top [wiki:Zelda_(SSBM)].

## Character tech

### Lightning Kick sweetspot

- **id:** `lightning-kick-sweetspot`
- **What:** Landing the small 20% hitbox at the tip of the foot on forward air or back air,
  instead of the 10% leg hitbox.
- **Inputs:** Jump, then fair or bair spaced so only the toe overlaps the target on the first
  active frames. Bair is usually preferred.
- **Timing:** Bair: hitbox frames 5-8, interruptible from frame 33, auto-cancels from frame
  26. Fair: hitbox frames 8-11, interruptible from frame 36, auto-cancels from frame 25. Both:
  landing lag 18, or 9 [L-cancelled](../techniques/l-cancel.md) [fd]. Bair is fast enough to
  be used twice in one short hop [wiki:Zelda_(SSBM)]. The sourspot out-prioritises the
  sweetspot, which is why the spacing is strict [wiki:Lightning_Kick].
- **Used for:** Killing. A sweetspot can KO as low as 50% [wiki:Zelda_(SSBM)].
- **Common errors:** Too close (10% sourspot, almost no knockback, Zelda is punished); too far
  (whiff, 18/9 frames of landing lag).
- **Drill idea:** CPU stands, or floats at kick height, at a random distance; success only if
  the hit is the 20% hitbox.

### Fair aerial interrupt (platform landing)

- **id:** `fair-aerial-interrupt`
- **What:** The kick animation sharply raises then lowers Zelda's environmental collision box
  (ECB), so a kick started just below a platform makes her land on it early with the
  auto-cancel landing (4 frames). It is her fastest way onto a side platform.
- **Inputs:** Full jump, double jump, then fair, timed so the ECB shift puts her feet on the
  platform. On Battlefield the fastest versions are: double jump on frame 5 after jump squat
  and fair on frame 4 after the double jump, or frame 4 and frame 5 respectively
  [lib:The Profane Tome].
- **Timing:** On Battlefield she is actionable on a side platform on frame 28 counting the
  first jump squat frame as 1, versus frame 32 for a no-impact landing and frame 33 for the up
  air version. A slower, lenient version is actionable between frames 33 and 39
  [lib:The Profane Tome].
- **Used for:** Platform movement; up throw onto a side platform → fair interrupt →
  [tech chase](../techniques/tech-chase.md) grab; buffering a
  [shield drop](../techniques/shield-drop.md); also a ledge option with 7 frames of actionable
  intangibility on flat-walled stages (SSBWiki says 9), 10 on Yoshi's Story and 13 on
  Battlefield [lib:The Profane Tome, wiki:Zelda_(SSBM)/Forward_aerial].
- **Common errors:** Too early (she rises through the platform mid-kick, not actionable); too
  late (normal landing with lag).
- **Drill idea:** From standing under a Battlefield side platform, measure the first
  actionable frame on the platform; success at frame 33 or earlier.

### Invincible ledge-hop kick

- **id:** `ledgehop-kick`
- **What:** Drop from the ledge, double jump immediately and kick onto the stage while still
  intangible from the ledge.
- **Inputs:** Release the ledge, double jump on the next frame, fair or bair toward the stage;
  add a few fast-fall frames before the jump to kick lower and poke shields
  [lib:The Profane Tome].
- **Timing:** There is "a wide window" in which the kick is fully intangible; thrown early
  enough it also auto-cancels on landing [lib:The Profane Tome]. Frame counts not given.
- **Used for:** Getting off the ledge with her best kill move; punishing opponents who stand
  near the edge.
- **Common errors:** Late jump (intangibility runs out); sourspot.
- **Drill idea:** CPU stands at a random distance from the ledge, shielding or not; success if
  the sweetspot lands while Zelda is intangible.

### Ledge kick (edge-cancelled kick)

- **id:** `ledge-kick`
- **What:** A kick placed so Zelda lands on the lip of the stage and slides off, cancelling
  the landing: a strong hitbox exactly where a recovering opponent wants to be, after which
  she is immediately actionable or grabs the ledge.
- **Inputs:** From on stage, jump/drift so the kick ends at the stage corner; do nothing
  afterwards to grab the ledge, or double jump and kick again. "Ribbon kick": buffer up during
  the kick and up B into the ledge so the Farore's Wind start-up hitbox also covers it
  [lib:The Profane Tome].
- **Timing:** Not given in frames. Risk: if the opponent takes the ledge first, the up B
  version can kill Zelda [lib:The Profane Tome].
- **Used for:** Edgeguarding: "often nets a full stock" at low commitment
  [lib:The Profane Tome].
- **Common errors:** Overshooting the edge (she is now offstage too); kicking early.
- **Drill idea:** CPU recovers to the ledge at a random time; success if the kick sweetspots
  or Zelda holds the ledge when the CPU arrives.

### Down tilt chain

- **id:** `dtilt-chain`
- **What:** Down tilt's leg hitbox meteor-smashes a grounded opponent into the floor, leaving
  them standing in hitstun so dtilt repeats or links into down smash.
- **Inputs:** Down+A repeatedly at close range; finish with down smash, grab or a kick.
- **Timing:** Hits frames 5-7, interruptible from frame 30; 8% leg / 7% foot, leg launch angle
  270° [fd]. It combos into itself "until around 95%" and into down smash
  [wiki:Zelda_(SSBM)]. Airborne opponents hit by the foot are launched upward instead
  [wiki:Zelda_(SSBM)].
- **Used for:** Close-range damage and setting up a finisher.
- **Common errors:** Foot hit on an airborne target (pops up, chain ends); opponent
  [ASDI](../techniques/asdi.md)s or SDIs away between hits.
- **Drill idea:** CPU stands at 0-90% and holds a random SDI direction; count consecutive
  dtilts before it escapes, then require a finisher.

### Up smash out of shield

- **id:** `usmash-oos`
- **What:** Jump-cancelled up smash from shield, the fastest up smash in the game.
- **Inputs:** In shield, press up on the C-stick with jump (or up + A during jump squat).
- **Timing:** First hit frame 5 [fd], so frame 6 out of shield with one jump squat frame (the
  same rule as other jump-cancelled options [wiki:Dolphin_Slash]). Twelve hits; the last does
  5% with knockback growth 210 [fd]. Very short horizontal range; the opponent can SDI out,
  which often leads to a grab instead [wiki:Zelda_(SSBM)].
- **Used for:** Punishing aerials that land on or cross up her shield at close range.
- **Common errors:** Opponent is beside rather than above/touching her (whiff); SDI escape.
- **Drill idea:** CPU Fox does a late nair on shield and lands next to Zelda; success if up
  smash's final hit connects.

### Nayru's Love

- **id:** `nayrus-love`
- **What:** Neutral B: a spinning crystal with hitboxes on both sides that reflects
  projectiles, briefly stalls her fall, and is invincible early.
- **Inputs:** B (on the ground, in the air, or out of shield via jump cancel).
- **Timing:** Invincible from frame 4 [wiki:Zelda_(SSBM)]. Hitboxes every 3 frames from frame
  12 to frame 30, 59 frames total [fd]. High end lag, and no protection above her
  [wiki:Zelda_(SSBM)]. "Subwarp": used just above the ground (or out of shield one frame
  late), her collision box rises and the hitboxes sink lower than normal, which shield-pokes
  [lib:The Profane Tome].
- **Used for:** Reflecting Falco lasers, Samus missiles and turnips; a "get off me" option
  against fast approaches.
- **Common errors:** Whiff (very long lag); opponent shields and punishes; attacked from
  above.
- **Drill idea:** CPU Falco fires lasers then approaches; success if a laser is reflected or
  the approach is hit, without Zelda being punished.

### Farore's Wind recovery

- **id:** `farores-wind-recovery`
- **What:** Up B: Zelda vanishes and reappears a long distance away in a chosen direction.
- **Inputs:** Up+B, then hold the travel direction before she disappears. No input = straight
  up.
- **Timing:** Start-up hitbox frames 10-11 (4%, set knockback 120 [fd]); intangible frames
  33-53; 114 frames total; 30 frames of landing lag before free fall
  [wiki:Zelda_(SSBM)/Up_special]. There is no hitbox on reappearance in Melee
  [wiki:Farore's_Wind]. If she reappears in the air she cannot move for a while; landing on
  the ground or going helpless has less lag [wiki:Zelda_(SSBM)].
- **Used for:** Recovery from very far; aim to reappear exactly at the ledge (sweetspot) or to
  ride the stage wall up to it. Also a rare movement option and can be ledge-cancelled
  [wiki:Zelda_(SSBM)].
- **Common errors:** Wrong angle or distance: reappearing above the stage in lag, below the
  ledge, or into an occupied ledge (self-destruct).
- **Drill idea:** Zelda starts at random offstage positions; success if the teleport ends in a
  ledge grab.

### Ledge stalls and haxdash

- **id:** `farores-ledge-stall`
- **What:** Ways to stay on or return to the ledge while intangible: up B stall, double-jump
  fast-fall stall, and an intangible haxdash. See
  [ledge options](../techniques/ledge-options.md).
- **Inputs:** (a) Double-jump fast-fall: release the ledge, jump on the next frame, fast fall
  on frame 25 of the double jump. (b) Fast-fall double jump: fast fall from the ledge for 4
  frames, then double jump. (c) Haxdash: release, jump toward the stage, air dodge down and
  away on frames 15-20, fast fall; earlier and more vertical is better. (d) "Ribbondash": up B
  as soon as she is actionable in the haxdash [lib:The Profane Tome].
- **Timing:** As above. A haxdash that misses the angle and goes straight down still leaves up
  to 3 intangible actionable frames on stage [lib:The Profane Tome]. Zelda is one of the
  characters with an up B ledge stall [wiki:Ledgestall].
- **Used for:** Holding the ledge during edgeguards and threatening ledge-hop kicks.
- **Common errors:** Mistimed fast fall (no regrab, death).
- **Drill idea:** Count stall cycles with no vulnerable frame.

### Transform to Sheik

- **id:** `transform-to-sheik`
- **What:** Down B swaps to [Sheik](sheik.md). Percent and stock carry over.
- **Inputs:** Down+B on the ground or in the air.
- **Timing:** Zelda → Sheik: intangible frames 34-43, swap on frame 44, 69 frames total. Sheik
  → Zelda: intangible 27-36, swap on frame 37, 62 total
  [wiki:Zelda_(SSBM)/Down_special, wiki:Sheik_(SSBM)/Down_special]. The swap needs no loading
  in Melee [wiki:Transform].
- **Used for:** Returning to Sheik after a Zelda recovery; switching to Zelda at high opponent
  percent to fish for a kick or for a matchup (Zelda has been used as a niche counterpick,
  e.g. against Ice Climbers [wiki:Zelda_(SSBM)]).
- **Common errors:** Transforming in range of the opponent: frames 44-69 after the swap are
  vulnerable (intangible only on frames 34-43).
- **Drill idea:** CPU approaches from a random distance; success if the transform completes
  and the new character is actionable before being hit.

## Neutral game

- **Plan:** defend a small space and punish. "Players must bait out options and wait for an
  opponent to make a mistake" [wiki:Zelda_(SSBM)].
- **Bair/fair walls:** retreating or in-place kicks at the height the opponent wants to jump
  through. Bair starts on frame 5.
- **Dash attack:** frame 6, 13% on the clean body hit, launches straight up; her main grounded
  combo starter [fd, wiki:Zelda_(SSBM)].
- **Forward smash:** disjointed and with low end lag; can be thrown out to catch a fast
  approach; its last hit is larger than the earlier ones [wiki:Zelda_(SSBM)].
- **Down smash:** frame 4, both sides, 30° launch [fd]; the "get off me" move; her leg is
  intangible during the kicks [wiki:Zelda_(SSBM)].
- **Up tilt** as anti-air (frames 10-24) [fd].
- **Grab** when the opponent shields a kick threat; it is slow (frame 11), so it is a punish
  or read, not a neutral poke.
- **Platforms:** being on a platform is where her kicks and movement are strongest; use fair
  aerial interrupt and wavelands to get there [lib:The Profane Tome].
- **Din's Fire:** only for edgeguarding or at very long range [wiki:Din's_Fire].

## Punish game

Zelda's punishes are short and aim at a kick. Down throw (four 2% hits then a 2% throw) sends
the opponent behind her with weak knockback and leads to dash attack, a kick or ftilt; up
throw leads to a kick on some characters and chain grabs fastfallers at low percent; ftilt's
hand hitbox sends behind her for follow-ups; nair, if it lands without the last hit, pops the
opponent up with set knockback into a kick [wiki:Zelda_(SSBM)].

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| uthrow | "certain matchups" | around 80% | bair or fair (kill confirm) | character list not given | [wiki:Zelda_(SSBM)] |
| uthrow | fastfallers | low percent | regrab (chain throw); platform tech chase | windows not sourced | [wiki:Zelda_(SSBM)] |
| dthrow | most | low-mid | dash attack, Lightning Kick, ftilt | also sets up stage spikes and edgeguards | [wiki:Zelda_(SSBM)] |
| dtilt | grounded | to about 95% | dtilt again; dsmash | leg hitbox | [wiki:Zelda_(SSBM)] |
| utilt | most | low percent | utilt; up air when it stops chaining | | [wiki:Zelda_(SSBM)] |
| up smash | above her | low percent | up smash again | | [wiki:Zelda_(SSBM)] |
| dash attack (clean) | most | low-mid | up tilt, up air, kick | 13%, 90°, base 70 | [fd], [wiki:Zelda_(SSBM)] |
| nair without last hit | certain matchups | any | bair / fair | | [wiki:Zelda_(SSBM)] |
| up B start-up hit ("ribbon") | at ledge | any | kick on bad DI | | [lib:The Profane Tome] |

### Chain grabs and tech chases

- Up throw can chain throw fastfallers at low percent and sets up platform tech chases
  [wiki:Zelda_(SSBM)]; fair aerial interrupt makes up throw → side platform → tech chase grab
  possible [lib:The Profane Tome]. No percent windows were found in text sources (the Melee
  Library's "Zelda Melee Chaingrab Guide" is a video).
- Otherwise none of note: her slow dash and frame-11 grab make ground tech chases depend on
  reads (down smash covers both sides near her; a kick covers one roll).

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| bair / fair sweetspot | most | from about 50% | toe hitbox only; earlier near the ledge | [wiki:Zelda_(SSBM)] |
| uthrow → bair/fair | certain characters | around 80% | | [wiki:Zelda_(SSBM)] |
| up tilt | most | Unknown; called "surprisingly powerful" and a reliable KO move | 11%, 70°, base 65, growth 105 | [fd], [wiki:Zelda_(SSBM)] |
| up air | most | Unknown; sixth strongest up air | 13%, 90°, growth 120; hitbox frames 14-16, above her only | [fd], [wiki:Zelda_(SSBM)] |
| fsmash (last hit) | most | Unknown | 14%, base 50, growth 98; earlier hits can be SDI'd | [fd] |
| up smash (last hit) | above her | Unknown | 5%, growth 210 | [fd] |
| dsmash | at ledge | Unknown; weak for a smash | 11% at 30° (semi-spike) | [fd], [wiki:Zelda_(SSBM)] |
| fthrow / bthrow | most | very high percent, near the edge | 12% / 11% | [wiki:Zelda_(SSBM)] |

- **Edgeguarding:** ledge kick and ledge-hop kick (above); down smash at the ledge (30°); dtilt
  leg meteor on opponents at the lip; Din's Fire offstage, whose knockback direction depends
  on which side of the target it hits, so it can push them away or pull them toward a kick
  [wiki:Din's_Fire]; holding the ledge with stalls.
- **Up air** can hit opponents standing on the stage or a platform from below while she
  recovers [wiki:Zelda_(SSBM)].

## Recovery

- **Options:** double jump (low: 21.4 units [wiki:Zelda_(SSBM)]); slow fall and good air speed
  (0.95) for drifting; air dodge (fast initial speed, gives distance like a second jump
  [wiki:Zelda_(SSBM)]); Nayru's Love to stall; Farore's Wind (longest teleport, intangible
  frames 33-53, no reappearance hitbox, 30 frames of landing lag
  [wiki:Zelda_(SSBM)/Up_special]).
- **Mixups:** teleport to the ledge versus onto the stage versus a platform; angle (eight
  directions and in-betweens); riding the stage wall upward to the ledge; teleport early from
  far away versus drifting close first; up air on the way in.
- **Weaknesses:** the teleport's destination is committed before she disappears; if she
  reappears in the air she is locked for a while; landing on stage is punishable; a held
  ledge can kill her outright.

### Edgeguarding Zelda

- **Hold the ledge** through her reappearance. She has no hitbox when she reappears, so an
  edgehog with ledge intangibility is safe; she then lands on stage in lag (30 frames) or
  falls.
- **Hit the start-up:** Farore's Wind takes over 30 frames before she is intangible (frame
  33) and its only hitbox is on frames 10-11; reach her before she vanishes.
- **Punish the stage landing** with a smash, grab or Rest.
- **Juggle instead of edgeguarding** when she is above the stage: she is floaty with no fast
  downward option.
- A CPU Zelda should mix: (a) teleport to ledge, (b) teleport onto stage past the edgeguarder,
  (c) drift in with double jump and air dodge when close, (d) teleport to a platform.

## Defense and out of shield

- **Out of shield:** up smash (frame 5 + 1), Nayru's Love (invincible from frame 4), down
  smash after dropping shield (frame 4), bair after a 6-frame jump squat, shield grab (slow,
  frame 11) [fd, wiki:Zelda_(SSBM)]. Her short wavedash makes wavedash OoS poor for escaping.
- **Crouch cancel:** she is weight 90, so crouch cancel into down smash (frame 4) or dtilt
  (frame 5) is a real answer to weak hits at low percent.
- **Combo escapes:** floaty physics get her out of fastfaller-style combos, but she is juggled
  from below; nair (frame 6) and Nayru's Love are the "get off me" options; air dodge.
- **What beats her:** camping (she cannot approach), projectiles she must spend 59 frames
  reflecting, shield pressure that stays beside rather than above her, and juggling.

## As the training dummy

- **Class:** weight 90, fall speed 1.4 (fast fall 1.85), gravity 0.066, air speed 0.95, jump
  squat 6 frames [wiki:Zelda_(SSBM)]. A tall floaty.
- **Combos on her:** not chain-grabbable by the usual fastfaller chain grabs. Versus Peach's
  down throw she is listed among characters who can jump out [wiki:Chain_grab]. Sheik's down
  throw gives up tilt / up air / fair rather than a regrab (floaty class; see
  [Sheik](sheik.md#chain-grabs-and-tech-chases)).
- **Kill profile:** dies early off the top (tall, floaty) [wiki:Zelda_(SSBM)]; survives
  horizontally better thanks to weight and a long recovery.
- **Jab reset:** forced plain stand below 39% post-hit for Sheik's jab/needles
  [web:docs.google.com Collection of Sheik Stuff].
- **Realistic CPU choices:** DI away and jump out of juggles; down smash or Nayru's Love when
  pressured at close range; teleport recovery mixups as listed above.
- **Marth:** a floaty for Marth's purposes: up throw juggles, side B → up tilt and pivot
  tipper setups apply as for other floaties (no Zelda-specific data found).

## Matchup notes

### vs Fox and Falco

- She cannot catch them and they can camp her; Nayru's Love reflects lasers but has long lag.
  Her answers are close-range speed (dsmash frame 4, up smash OoS frame 6, bair frame 5) and
  early kills: one sweetspot kick near the ledge at around 50% can take the stock
  [wiki:Zelda_(SSBM)]. Up throw chain throws them at low percent.

### vs Marth

- Marth out-ranges her and juggles her; she must get inside sword range or catch a landing
  with a kick. No sourced specifics.

### vs Sheik

- Sheik out-speeds her everywhere; the Zelda player usually just transforms. Zelda's main use
  here is the recovery.

### vs Ice Climbers

- Cited as a niche counterpick matchup for Zelda (Jmook) [wiki:Zelda_(SSBM)]: her kicks and
  down smash separate and kill the climbers early.

### vs Peach and Jigglypuff

- Slow matchups where both sides wait. Kicks out-prioritise little but kill floaties early off
  the side; up tilt and up air kill off the top. No sourced specifics.

## Drill seeds

### Sweetspot kick spacing

- **id:** `zelda-kick-sweetspot`
- **Goal:** Hit the 20% hitbox of bair and fair on demand.
- **Player:** Zelda
- **CPU:** Fox, Marth, Peach, Captain Falcon (different heights and widths)
- **Setup:** Flat stage. CPU at 50-80% standing at a random horizontal distance; variant with
  the CPU in a short hop.
- **CPU behaviour:** Stands, or jumps in place at a random time.
- **Success:** The connecting hit is 20%; bonus for a KO.
- **Fail:** 10% sourspot or whiff.
- **Variations:** Rising vs falling kick; auto-cancelled kick (bair lands on or after frame
  26, fair on or after frame 25 of the aerial); two bairs in one short hop.
- **Data needed:** kick hitbox positions/sizes per frame (bair frames 5-8, fair 8-11), CPU
  hurtbox sizes, Zelda short hop height 18.337 and jump squat 6 [wiki:Zelda_(SSBM)].

### Up throw to kick

- **id:** `zelda-uthrow-kick`
- **Goal:** Confirm a kick from up throw at kill percent.
- **Player:** Zelda
- **CPU:** Fox, Falco, Captain Falcon, Sheik, Marth
- **Setup:** CPU in Zelda's grab at 70-90% near center.
- **CPU behaviour:** Random DI on the throw; jumps or air dodges on its first actionable
  frame.
- **Success:** Sweetspot bair/fair connects before the CPU acts.
- **Fail:** Sourspot, whiff, or CPU escapes.
- **Variations:** Low percent fastfaller version: up throw → regrab; platform version: up
  throw to side platform → fair aerial interrupt → grab the tech.
- **Data needed:** up throw launch data and release frame (not in the sources read; must be
  taken from game data), CPU weight/fall speed, kick start-up. Which characters this is true
  on around 80% must be measured.

### Down tilt chain into finisher

- **id:** `zelda-dtilt-chain`
- **Goal:** Chain dtilts and end with dsmash, grab or a kick.
- **Player:** Zelda
- **CPU:** Marth, Sheik, Fox, Peach
- **Setup:** CPU standing next to Zelda at 0-60%.
- **CPU behaviour:** Holds a random ASDI/SDI direction; shields or jumps as soon as it can.
- **Success:** At least three dtilts connect in a row and the finisher lands.
- **Fail:** CPU acts between hits.
- **Variations:** Start from a crouch-cancelled hit; finish with a ledge dsmash.
- **Data needed:** dtilt hit frames 5-7, IASA 30, leg angle 270° [fd]; ground-meteor hitstun
  behaviour; "until around 95%" [wiki:Zelda_(SSBM)].

### Fair aerial interrupt to platform

- **id:** `zelda-fair-ai-platform`
- **Goal:** Reach a side platform actionable as fast as possible.
- **Player:** Zelda
- **CPU:** none (or a CPU lying on the platform after an up throw)
- **Setup:** Battlefield, Zelda standing under a side platform.
- **CPU behaviour:** If present: techs in place / left / right / misses at random.
- **Success:** Zelda is actionable on the platform by frame 33 (frame 28 is perfect), counting
  the first jump squat frame as 1; with a CPU, she grabs the tech.
- **Fail:** She passes through the platform still kicking, or lands with full lag.
- **Variations:** Yoshi's Story and Dream Land platform heights; chain into a shield drop.
- **Data needed:** platform heights; Zelda jump/double-jump arcs; fair ECB shift frames (only
  the Battlefield input timings are sourced [lib:The Profane Tome]).

### Ledge trap with kicks

- **id:** `zelda-ledge-kick-edgeguard`
- **Goal:** Cover a recovery with a ledge kick or an intangible ledge-hop kick.
- **Player:** Zelda
- **CPU:** Marth, Sheik, Captain Falcon, Fox
- **Setup:** CPU offstage at 40-80% with double jump; Zelda on stage near the ledge (variant:
  already hanging on the ledge).
- **CPU behaviour:** Random: recover to ledge, recover onto stage, recover high.
- **Success:** Sweetspot kick lands, or Zelda holds the ledge as the CPU's up B ends and the
  CPU dies.
- **Fail:** CPU reaches an actionable state on stage or ledge; Zelda self-destructs.
- **Variations:** Require the intangible ledge-hop version; dsmash-only version from stage.
- **Data needed:** ledge intangibility length; CPU recovery distances; kick auto-cancel
  frames.

### Up smash out of shield

- **id:** `zelda-usmash-oos`
- **Goal:** Punish close shield pressure with the frame-6 OoS up smash.
- **Player:** Zelda
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** Zelda shielding; CPU does an aerial on shield.
- **CPU behaviour:** Late or early aerial at random; lands in front, on top, or behind; then
  shines, jabs or grabs.
- **Success:** Up smash's final hit connects.
- **Fail:** Zelda is hit or grabbed, or up smash whiffs / is SDI'd out of.
- **Variations:** Allow Nayru's Love OoS or dsmash as alternates when the CPU lands beside her.
- **Data needed:** up smash hit frames and horizontal reach; shieldstun formula; CPU landing
  lag.

### Farore's Wind to ledge

- **id:** `zelda-recovery-teleport`
- **Goal:** Pick the angle and distance that ends on the ledge.
- **Player:** Zelda (or Sheik who must transform first)
- **CPU:** Marth, Fox (optional edgeguarder)
- **Setup:** Zelda offstage at a random position within teleport range, double jump random.
- **CPU behaviour:** None; or holds the ledge on reaction to the start-up; or waits on stage.
- **Success:** Ledge grab, or actionable on stage/platform without being hit.
- **Fail:** KO, or punished during 30 frames of landing lag.
- **Variations:** Start as Sheik far offstage: transform (swap on frame 37 of 62), then
  recover as Zelda, then transform back safely.
- **Data needed:** Farore's Wind travel distance per direction (not sourced), intangibility
  33-53, ledge sweetspot rules.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlZd.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/zelda.json`](../framedata/zelda.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 11, 13, 15 | 2 | Sakurai | 10 | 100 | - | electric | 29 | 27 | 2 | -13 |  |
| Dash attack | `dash_attack` | 6-8 | 13/9 | 90/Sakurai | 70/50 | 70 | - | electric | 37 | 36 | 7 | -22 |  |
|  |  | 9-13 | 8/7 | 90/Sakurai | 20 | 70 | - | electric |  |  | 5 | -21 |  |
| Forward tilt (angled up) | `ftilt_high` | 12-14 | 13/12/11 | 110/Sakurai | 50 | 88 | - | slash | 37 | 37 | 7 | -17 |  |
| Forward tilt (slightly up) | `ftilt_mid_high` | 12-14 | 13/12/11 | 110/Sakurai | 50 | 88 | - | slash | 37 | 37 | 7 | -17 |  |
| Forward tilt | `ftilt` | 12-14 | 13/12/11 | 110/Sakurai | 50 | 88 | - | slash | 37 | 37 | 7 | -17 |  |
| Forward tilt (slightly down) | `ftilt_mid_low` | 12-14 | 13/12/11 | 110/Sakurai | 50 | 88 | - | slash | 37 | 37 | 7 | -17 |  |
| Forward tilt (angled down) | `ftilt_low` | 12-14 | 13/12/11 | 110/Sakurai | 50 | 88 | - | slash | 37 | 37 | 7 | -17 |  |
| Up tilt | `utilt` | 10-24 | 11 | 70 | 65 | 105 | - | electric | 43 | 40 | 6 | -23 |  |
| Down tilt | `dtilt` | 5-7 | 7/8 | 270/80 | 20 | 80 | - |  | 31 | 30 | 5 | -19 |  |
| Forward smash | `fsmash` | 16, 18, 20, 22 | 1 | 160/60/45/30 | 0 | 100 | 40/12/11/13 |  | 39 | - | 2 | -21 | charge hold frame 11 |
|  |  | 24 | 14 | Sakurai | 50 | 98 | - | electric |  |  | 8 | -7 |  |
| Up smash | `usmash` | 5, 7, 9, 11, 13, 15 | 1 | 90/170 | 0 | 100 | 16/20/45 | electric | 56 | 51 | 2 | -43 | charge hold frame 4 |
|  |  | 24, 26, 28, 30, 32 | 1 | 90/110 | 0 | 100 | 16/20/45 | electric |  |  | 2 | -24 |  |
|  |  | 34 | 5 | 90 | 20 | 210 | - | electric |  |  | 4 | -12 |  |
| Down smash | `dsmash` | 4-7 | 11 | 30 | 20 | 90 | - |  | 39 | 32 | 6 | -21 | charge hold frame 2; partly intangible 4-16 (2 bones) |
|  |  | 13-16 | 11 | 30 | 20 | 80 | - |  |  |  | 6 | -12 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 6-7, 10-11, 14-15, 18-19, 22-23 | 2/3 | 130/90 | 0 | 100/90 | 70/120/50 |  | 49 | 42 | 3 | 18 | 9 | <6, >37 | -6 |  |
|  |  | 26-27 | 5 | Sakurai | 40 | 130/120 | - |  |  |  | 4 |  |  |  | -5 |  |
| Forward air | `fair` | 8-11 | 10/20 | Sakurai | 0/30 | 80/96 | - | electric | 39 | 36 | 10 | 18 | 9 | <8, >24 | +1 |  |
| Back air | `bair` | 5-8 | 10/20 | Sakurai | 0/30 | 80/96 | - | electric | 35 | 33 | 10 | 18 | 9 | <5, >25 | +1 |  |
| Up air | `uair` | 14-16 | 13 | 90 | 0 | 120 | - | fire | 54 | - | 7 | 25 | 12 | <14, >44 | -5 |  |
| Down air | `dair` | 14-17 | 8/7 | 275 | 5/0 | 100/80 | - |  | 43 | 43 | 5 | 24 | 12 | <1, >39 | -7 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 12-13 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 12-13 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 7 | 25 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 12 | 12 | 45 | 70 | 50 | - | - | 32 | 49 |  |
| Back throw | `bthrow` | 11 | 11 | 45 | 80 | 60 | - | - | 25 | 49 |  |
| Up throw | `uthrow` | 11 | 11 | 90 | 80 | 50 | - | - | 29 | 49 |  |
| Down throw | `dthrow` | 10 | 2 | 120 | 80 | 42 | - | electric | 50 | 64 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Nayru's Love, ground | `special_n` | 12, 15, 18, 21, 24 | 1/2 | 10 | 12 | 40 | - | slash | 59 | - | 2 | - | intangible 4-11 |
|  |  | 27 | 5/4 | Sakurai | 50/40 | 100 | - | slash |  |  | 4 | - |  |
| Neutral B: Nayru's Love, air | `special_air_n` | 12, 15, 18, 21, 24 | 1/2 | 10 | 12 | 40 | - | slash | 59 | - | 2 | - | intangible 4-11 |
|  |  | 27 | 5/4 | Sakurai | 50/40 | 100 | - | slash |  |  | 4 | - |  |
| Side B: Din's Fire, ground, Start | `special_s_start` | - | - | - | - | - | - | - | 24 | - | - | - |  |
| Side B: Din's Fire, ground, Loop | `special_s_loop` | - | - | - | - | - | - | - | 14 | - | - | - |  |
| Side B: Din's Fire, ground, End | `special_s_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Side B: Din's Fire, air, Start | `special_air_s_start` | - | - | - | - | - | - | - | 24 | - | - | - |  |
| Side B: Din's Fire, air, Loop | `special_air_s_loop` | - | - | - | - | - | - | - | 14 | - | - | - |  |
| Side B: Din's Fire, air, End | `special_air_s_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Up B: Farore's Wind, ground, Start | `special_hi_start` | 10-11 | 4 | 80 | 0 | 100 | 120 | slash | 33 | - | 3 | - | intangible 33 |
| Up B: Farore's Wind, ground | `special_hi` | 1-2 | 4 | Sakurai | 0 | 100 | 120 | fire | 21 | - | 3 | - |  |
| Up B: Farore's Wind, air, Start | `special_air_hi_start` | 10-11 | 4 | 80 | 0 | 100 | 120 | slash | 33 | - | 3 | - | intangible 33 |
| Up B: Farore's Wind, air | `special_air_hi` | 1-2 | 4 | Sakurai | 0 | 100 | 120 | fire | 61 | - | 3 | - |  |
| Down B: Transform, ground | `special_lw` | - | - | - | - | - | - | - | 43 | - | - | - | intangible 34-43 |
| Down B: Transform, ground, 2 | `special_lw2` | - | - | - | - | - | - | - | 25 | - | - | - |  |
| Down B: Transform, air | `special_air_lw` | - | - | - | - | - | - | - | 43 | - | - | - | intangible 34-43 |
| Down B: Transform, air, 2 | `special_air_lw2` | - | - | - | - | - | - | - | 25 | - | - | - |  |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 3-20 | - | 32 | 29 |  |
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
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-30 | 34-39 (10/8%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-23 | 27-30 (6%) | 53 | - |  |
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
| Up smash | jump cancel | 6 | `usmash` |
| Back air | jump | 11 | `bair` |
| Up B | jump cancel | 11 | `special_hi_start` |
| Neutral air | jump | 12 | `nair` |
| Shield grab | direct | 12 | `grab` |
| Forward air | jump | 14 | `fair` |
| Up air | jump | 20 | `uair` |
| Down air | jump | 20 | `dair` |
| Spot dodge | direct | intangible 3-20 of 32 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 18 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Zelda indexed by [The Melee Library](https://www.meleelibrary.com/#zelda) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Zelda Techs Guide](https://www.youtube.com/watch?v=vmreAHYq5xU&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=7&t=0s) | Third Chair | Video guide on performing useful Zelda tech in 2020. |
| [Zelda Melee Chaingrab Guide](https://www.youtube.com/watch?v=GuGtSZYGkBk&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=6&t=0s) | Third Chair | With an [update](https://www.youtube.com/watch?v=bOKbZUkdtzo&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=15&t=0s). |
| [Zelda Tech 101](https://www.youtube.com/watch?v=ApqM9Y5snhw) | Chandy | Chandy shows various Zelda tech. |
| [The Profane Tome](http://profaneto.me/) | Profane | An expansive technical guide on a bunch of advanced Zelda tech |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Zelda (SSBM): https://www.ssbwiki.com/Zelda_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Zelda_(SSBM)/Forward_aerial , /Back_aerial ,
  /Up_special , /Down_special ; https://www.ssbwiki.com/Sheik_(SSBM)/Down_special
- SSBWiki technique pages: https://www.ssbwiki.com/Lightning_Kick , /Farore's_Wind ,
  /Din's_Fire , /Nayru's_Love , /Transform , /Ledgestall , /Chain_grab ,
  /List_of_SSBM_tier_lists_(NTSC) , /Dolphin_Slash (jump-cancel OoS rule)
- Profane, "The Profane Tome" (front page posts: Fair AI, Haxdash/Ribbondash, Ledgekick and
  Ribbonkick, Invuln Ledgehop Kicks, Airdodge Interrupts, Nayru's Love Subwarp):
  http://profaneto.me/
- "Collection of Sheik Stuff" (Magus's forced get-up thresholds):
  https://docs.google.com/document/d/1mlNwPWxO2y8u_w1t_jf_FzMx6OC8BJyFZ2fW-rOj9zk/
- Frame data dump: `Zelda.json`
- The other three Melee Library cards for Zelda are YouTube videos (2020 Zelda Techs Guide,
  Zelda Melee Chaingrab Guide, Zelda Tech 101); titles only.
