---
schema: melee-character/v1
id: young-link
name: Young Link
aliases: [YL, Yink, Kid Link, Child Link]
tier: "C- (17th of 26), 2021 tier list"
archetype: [projectile, zoner, swordie, lightweight, edgeguarder, technical]
related: [link]
summary: Young Link runs away and zones with bombs, boomerang and fire arrows, juggles with up air, and takes stocks through edgeguards and set-ups into dash attack, down smash or down air because his raw kill power is low.
key_tech: [bomb-pull-and-z-drop, death-mountain, dair-fire-meteor, fire-arrow-zoning, hookshot-recovery, boomerang-glide, falling-up-b, triple-aerials, dsmash-tech-chase, jump-cancel-grab]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlCl.dat
framedata: ../framedata/young-link.json
code: src/melee/ft/kinds/ftCLink
specials:
  neutral_b: "Fire Bow"
  side_b: "Boomerang"
  up_b: "Spin Attack"
  down_b: "Bomb"
attributes:
  weight: 85
  gravity: 0.11
  fall_speed: 2.13
  fast_fall_speed: 2.2
  jump_squat: 4
  jumps: 2
  walk_speed: 1.2
  dash_speed: 1.8
  run_speed: 1.6
  traction: 0.08
  air_speed: 1
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [6, 20, 3]
  jab2: [7, 18, 2]
  jab3: [7, 33, 5]
  rapid_jab_start: [null, 8, 0]
  rapid_jab_loop: [2, 35, 1]
  rapid_jab_end: [null, 11, 0]
  dash_attack: [7, 40, 11]
  utilt: [9, 30, 8]
  dtilt: [14, 32, 10]
  usmash: [11, 52, 9]
  dsmash: [9, 42, 13]
  nair: [4, 36, 12]
  fair: [14, 47, 12]
  bair: [6, 30, 7]
  uair: [5, 60, 15]
  dair: [13, 80, 21]
  grab: [11, 86, 0]
  dash_grab: [14, 96, 0]
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
  special_hi: [8, 80, 3]
  special_air_hi: [8, 80, 3]
  special_lw: [null, 40, 0]
  special_air_lw: [null, 40, 0]
oos:  # option: frame the hitbox is out
  nair: 8
  uair: 9
  special_hi: 9
  bair: 10
  grab: 11
  usmash: 12
  dair: 17
  fair: 18
resources: 12
# generated: end
---

# Young Link

<!-- GENERATED:attributes -->
## Attributes

Read from `PlCl.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 85 |
| Gravity | 0.11 |
| Terminal fall speed | 2.13 |
| Fast-fall speed | 2.2 |
| Jump squat (frames before airborne) | 4 |
| Full hop / short hop initial Y speed | 2.62 / 1.5 |
| Air jump Y multiplier | 0.88 |
| Jumps | 2 |
| Walk max speed | 1.2 |
| Dash initial speed / run max speed | 1.8 / 1.6 |
| Ground friction (traction) | 0.08 |
| Air max horizontal speed | 1 |
| Air acceleration (base + stick) | 0.02 + 0.04 |
| Air friction | 0.005 |
| Normal landing lag | 4 |
| Shield size | 11.625 |
<!-- /GENERATED:attributes -->

## Overview

Young Link is a clone of [Link](link.md) who trades power, weight and reach for speed. He
is weight 85 against Link's 104, has the same fall speed (2.13) but a much lower fast-fall
speed (2.2), a 4-frame jump squat (Link: 6), and a dash speed of 1.8 against 1.3
[wiki:Young_Link_(SSBM)]. His three projectiles are all better combo tools than Link's:
bombs hit four times instead of twice, fire arrows have far more base knockback, and the
boomerang does more damage on the way out [wiki:Young_Link_(SSBM)]. He wins neutral by
staying mobile, pulling bombs whenever it is safe, and forcing the opponent to come through
projectiles; he then juggles with up air and up tilt. His problem is finishing: most
finishers have sourspots or are multi-hits that can be escaped, so he typically needs an
edgeguard or a kill confirm [wiki:Young_Link_(SSBM)]. He is light and easy to kill, and his
recovery is slow and readable despite the hookshot and wall jump. He is known as a
counterpick against floaty characters: Armada beat Hungrybox's
[Jigglypuff](jigglypuff.md) with him repeatedly from 2011 to 2014, and he is considered
one of the best answers to [Peach](peach.md) [wiki:Young_Link_(SSBM)]. He struggles against
[Fox](fox.md), [Falco](falco.md) and [Captain Falcon](captain-falcon.md)
[wiki:Young_Link_(SSBM)]. Technical demand is high because of item (bomb) handling.

## Strengths and weaknesses

- **Strengths:**
  - Best projectile set of the two Links: bombs "don't stale, do up to 14%, are
    multi-hit" [lib:Young Link Collection]; uncharged fire arrow does 8% with base
    knockback 45 at an 80 degree angle [wiki:Young_Link_(SSBM)].
  - Good mobility: run speed 1.6, traction 0.08 for a longer wavedash than Link,
    4-frame jump squat [wiki:Young_Link_(SSBM)].
  - Fast, low-lag nair (hits frame 4, 15 frames landing lag, 7 L-cancelled [fd]) and a
    long-lasting, very disjointed up air (frames 5-49 [fd]).
  - Dash attack sends away at the Sakurai angle and kills from about 95% on some
    characters [wiki:Young_Link_(SSBM)]; dsmash sends at 30 degrees [fd], excellent near
    the ledge.
  - Dair is the strongest meteor smash in the game when the late hilt hitbox (21%)
    connects [wiki:Young_Link_(SSBM)].
  - Too light for Fox's waveshine combos: shine knocks him down instead of sliding him
    [wiki:Young_Link_(SSBM)].
  - Wall jump, hookshot and a 14-frame invincible ledgedash
    [lib:Young Link Optimization Project].
- **Weaknesses:**
  - Light (85) with normal fall speed: dies early off the top and the sides
    [wiki:Young_Link_(SSBM)].
  - Finishers are unreliable: fsmash and usmash can be DI'd out of before the last hit;
    grounded up B is a multi-hit that does not kill; dair meteor sweetspot is small
    [wiki:Young_Link_(SSBM)].
  - Grab is slow (frame 10 standing, 84 frames total; dash grab frame 13, 94 total [fd]),
    so opponents crouch cancel and shield freely [lib:Young Link Collection].
  - Shorter hookshot than Link's, so tether recovery covers less [wiki:Young_Link_(SSBM)].
  - Low fast-fall speed makes him easier to juggle and makes fast-fall mixups weak
    [wiki:Young_Link_(SSBM)] [lib:Young Link Collection].
  - Loses close quarters to the space animals and Captain Falcon [wiki:Young_Link_(SSBM)].

## Character tech

### Bomb pull and Z-drop

- **id:** `bomb-pull-and-z-drop`
- **What:** Down B pulls a bomb item. Young Link's bombs explode in four hits and, unlike
  Link's, explode the moment they touch the ground [wiki:Bomb_(Link)]. Pressing Z in the
  air drops the bomb straight down instead of throwing it.
- **Inputs:** Down B (can be done while jumping or moving in the air). Throw with A or the
  C-stick in any direction; Z in the air to drop. Grounded throws do the most damage; throw
  from a dash only after a jump cancel or pivot, from a run only after a crouch
  [lib:Young Link Collection].
- **Timing:** Bomb appears on frame 16 of a 39-frame animation
  [wiki:Young_Link_(SSBM)/Down_special]. Z-drop is described as a 2-frame commitment, and
  Z-drop out of shield puts a hitbox out on frame 5, his fastest out-of-shield option
  [lib:Young Link Collection].
- **Used for:** Everything: zoning, combo starters (bomb into uair, bomb into dair),
  escaping shield pressure, covering his own recovery, forcing Fox to stay in shine
  (reflecting locks Fox for 20 frames [lib:Young Link Collection]).
- **Common errors:** Pulling a bomb in the opponent's range; the bomb landing next to him
  and hitting him too (hold down-and-back to ASDI, automatic smash DI from the stick
  position, when grounded [lib:Young Link Collection]); letting the fuse run out in hand.
- **Drill idea:** CPU pressures Young Link's shield while he holds a bomb; success is a
  Z-drop out of shield hitting the CPU and a follow-up aerial landing.

### Death Mountain

- **id:** `death-mountain`
- **What:** A full hop dair started on the first airborne frames so that the late hilt
  hitbox (21%, a meteor) hits an opponent standing or lying on a platform above. A meteor
  against a grounded target bounces them straight up with huge knockback
  [lib:Young Link Collection].
- **Inputs:** Under a side platform: full hop, dair on airborne frames 1-3
  [lib:Young Link Collection].
- **Timing:** Dair is active frames 13-64 [fd]; the meteor hitbox is 270 degrees with base
  knockback 70 and growth 100 [fd]. Works on the platforms of Yoshi's Story, Fountain of
  Dreams and Pokemon Stadium [lib:Young Link Collection]. Listed kill percents: Fox 72% on
  Yoshi's Story and 82% on Fountain of Dreams; Marth from 59% on Yoshi's Story; Peach 52%
  on Yoshi's Story [lib:Young Link Collection].
- **Used for:** Early kills from platform tech chases, e.g. up throw onto a platform
  (Marth at 53% on Yoshi's Story), or dthrow utilt at 46% [lib:Young Link Collection].
- **Common errors:** Dair input late so the tip (non-meteor, 70 degrees) hits instead;
  wrong platform height; 50 frames of landing lag if it whiffs and is not L-cancelled [fd].
- **Drill idea:** CPU lies or techs on a Yoshi's Story side platform at 60-80%; success is
  the meteor hitbox connecting and the CPU dying off the top.

### Down air fire meteor (offstage)

- **id:** `dair-fire-meteor`
- **What:** The hilt hitbox of dair meteors airborne opponents downward with a flame
  effect. It only connects on targets beside or above the sword hilt, so it is hard to
  land and risky offstage [wiki:Young_Link_(SSBM)].
- **Inputs:** Jump up into or beside an airborne opponent and dair so the hilt, not the
  blade tip, touches them.
- **Timing:** Hitbox frames 13-64 [fd]; hilt hitbox 16% early (the wiki lists 21% for the
  late part), tip 14% early / 17% late [wiki:Young_Link_(SSBM)] [fd]. Unlike Link's, the
  move gets stronger later in the animation [wiki:Young_Link_(SSBM)]. Up throw can lead
  into the dair meteor at high percent [wiki:Young_Link_(SSBM)].
- **Used for:** Kills on opponents recovering high or jumping at him; the non-meteor tip
  hit is a strong vertical kill move on opponents below him.
- **Common errors:** Falling to his death during the 89-frame animation [fd]; using dair
  to land against a character with a disjointed up air [lib:Young Link Collection].
- **Drill idea:** CPU recovers from below and jumps toward the ledge; success is the hilt
  meteor connecting and Young Link getting back.

### Fire arrow zoning

- **id:** `fire-arrow-zoning`
- **What:** Neutral B fires a flaming arrow. Uncharged it does 8% (Link's: 5%), fully
  charged 15% (Link's: 18%), with base knockback 45 and growth 30 at 80 degrees, so even
  an uncharged arrow gives real hitstun at low percent [wiki:Young_Link_(SSBM)].
- **Inputs:** B, hold to charge, release. Can be fired while jumping, including a ledge
  hop arrow.
- **Timing:** The charge window starts at frames 13-14 and the release animation is 25
  frames [wiki:Young_Link_(SSBM)/Neutral_special]; startup is 3 frames faster than Link's
  [wiki:Young_Link_(SSBM)]. Charging adds 1% every 6-7 frames [lib:Young Link Collection].
  An arrow stuck in the ground or a shield keeps a hurtbox that blocks some projectiles
  and slows moves that hit it [lib:Young Link Collection].
- **Used for:** Forcing jumps and shields at long range, covering an approach (he can
  move alongside a slow uncharged arrow), edgeguarding at distance, slowing Fox's up B by
  making it hit the arrow [lib:Young Link Collection].
- **Common errors:** Firing at close range where any aerial beats it; over-charging and
  being approached.
- **Drill idea:** CPU approaches from far; success is an arrow hit followed by a bomb pull
  completed before the CPU can punish.

### Hookshot recovery (grapple boost, instant ledge snap)

- **id:** `hookshot-recovery`
- **What:** Air grab fires the hookshot at a wall like Link's [wiki:Wall_grapple]. Young
  Link's is shorter, so players add air dodge momentum and cancel techniques to it.
- **Inputs:** Grapple boost: air dodge up (or down), then Z or L/R + A early in the air
  dodge; the tether keeps the vertical speed. Instant ledge snap: air dodge, Z, then A
  while hooked to reel in and grab the ledge. Point-blank cancel: air dodge into the
  ledge and Z at point-blank range to grab it [lib:Young Link Collection].
- **Timing:** A grapple boost reaches slightly higher than a standing full hop; horizontal
  air dodge momentum is cut by up to 88% [lib:Young Link Collection]. One grapple per
  airborne period; a miss means special fall [wiki:Wall_grapple]. A hook placed too high
  can break the chain on stage geometry [lib:Young Link Collection].
- **Used for:** The safer of his two recovery endings; getting back faster than up B when
  facing the wrong way; stalling against edgeguards.
- **Common errors:** Holding a bomb (Z drops the bomb first); grappling when Fox or Falco
  already holds the ledge and can bair the chain position [lib:Young Link Collection].
- **Drill idea:** Young Link offstage low with no double jump; success is a ledge grab by
  hookshot while a CPU threatens the up B path.

### Boomerang glide

- **id:** `boomerang-glide`
- **What:** Young Link throws the boomerang straight down, air dodges up and forward, and
  catches the returning boomerang during the air dodge's special fall. The catch cancels
  special fall, so he can up B afterwards [wiki:Boomerang_glide].
- **Inputs:** Jump toward the stage, smash side B angled fully down, air dodge up-forward
  (about 45 degrees is easiest), hold forward, catch, then up B or wait and hookshot
  [wiki:Boomerang_glide] [lib:Young Link Collection].
- **Timing:** Extra horizontal distance is about 60% of a full-drift double jump
  [wiki:Boomerang_glide], or roughly 25 units [lib:Young Link Collection]. The boomerang
  must be thrown within the first 13 frames of the double jump to gain leniency; air dodge
  window after a perfect double jump throw is 2 to 13 frames depending on angle
  [lib:Young Link Collection]. Boomerang release is frame 27 of 45
  [wiki:Young_Link_(SSBM)/Side_special].
- **Used for:** Recoveries that would otherwise fall just short. Link cannot do it
  [wiki:Link_(SSBM)].
- **Common errors:** Opponent touches the boomerang (catch window shrinks); air dodge
  angle too flat or too steep; boomerang already out.
- **Drill idea:** Young Link launched to a distance just past double jump + up B range;
  success is reaching the ledge.

### Falling up B (ledge-cancelled Spin Attack)

- **id:** `falling-up-b`
- **What:** A grounded up B started while sliding off an edge turns into the aerial
  version as he falls, with its large hitboxes, and grabs the ledge from either facing
  [lib:Young Link Collection].
- **Inputs:** Run or waveland toward the ledge and up B on the last grounded frames, or
  dash, jump, up B during jump squat.
- **Timing:** About a 6-frame window from a run; it takes 20 frames to fall and grab a
  flat ledge this way, against 14 for a wavedash back and 7 for a fast-fallen wavedash
  back [lib:Young Link Collection].
- **Used for:** Grabbing the ledge with a hitbox out (edgehog plus hit), sometimes called
  a spin hog.
- **Common errors:** Too early gives a full grounded up B on stage (79 frames [fd]); too
  fast a run overshoots the ledge.
- **Drill idea:** CPU recovers to the ledge; success is Young Link holding the ledge
  before the CPU arrives, measured in frames from the start signal.

### Double and triple aerials

- **id:** `triple-aerials`
- **What:** Bair and nair can be interrupted early (IASA, "interruptible as soon as",
  frame 30 for bair and 36 for nair [fd]), so one full hop fits two or three aerials, e.g.
  bair, nair, uair.
- **Inputs:** Full hop, immediate bair, then nair or uair on the first actionable frame,
  optionally a third aerial or double jump.
- **Timing:** Bair hits frames 6-9 and 18-23 [fd]; nair frame 4 [fd].
- **Used for:** Escaping the corner, crossing up shields without giving a shield grab,
  pressure against tall characters such as Captain Falcon [lib:Young Link Collection].
- **Common errors:** Landing inside the opponent after the last aerial; missing the
  L-cancel.
- **Drill idea:** CPU shields in the corner-trapping position; success is three aerials on
  shield, landing behind the CPU, no shield grab taken.

### Down smash tech chase

- **id:** `dsmash-tech-chase`
- **What:** Dsmash hits in front on frames 9-11 and both sides on frames 21-23 [fd]
  [wiki:Young_Link_(SSBM)], sending at 30 degrees. Properly spaced it covers three tech
  options, four at a ledge or on a platform [lib:Young Link Collection].
- **Inputs:** After a knockdown (dthrow at low percent, fair, bomb), position so the first
  hit covers tech in place and the second covers a roll, then dsmash.
- **Timing:** Against Fox: tech in place is invincible frames 1-20 and vulnerable 21-26;
  tech roll is vulnerable frames 21-40; minimum reaction needed for a reaction grab on
  tech in place is 13 frames [lib:Young Link Collection].
- **Used for:** Converting knockdowns into a ledge-angle launch and an edgeguard. Dash
  attack (spaced) also covers three options [lib:Young Link Collection].
- **Common errors:** Hitting with the sword tip sourspot (7% / 6% [fd]); standing too
  close so tech-away is out of range.
- **Drill idea:** CPU is knocked down at mid percent and picks a random tech; success is
  dsmash or a reaction grab connecting.

### Jump-cancel grab

- **id:** `jump-cancel-grab`
- **What:** Cancelling a dash's jump squat with grab gives a standing grab while moving,
  avoiding his poor dash grab (slower, smaller hitboxes, more lag [wiki:Young_Link_(SSBM)]).
- **Inputs:** Dash, jump, grab during jump squat (see
  [jump cancel](../techniques/jump-cancel.md)).
- **Timing:** Standing grab is out frame 10 [fd] against frame 13 for dash grab [fd]. A
  jump-cancel grab gives up to 50% more range than a stationary grab
  [lib:Young Link Collection].
- **Used for:** Whiff punishes, reaction tech chases, shield punishes.
- **Common errors:** Late grab input gives a jump; grab whiff is 84 frames [fd].
- **Drill idea:** CPU whiffs a laggy move at dash distance; success is a jump-cancel grab
  within the punish window.

Also documented: Goron roll (bomb tech roll; for Young Link only from about 124% and
longest when facing backwards), bombchu, bomb rocket, bomb launching, acid drop
[wiki:Bomb_(Link)]; reverse-angle boomerang (thrown almost straight down so it arcs over
his head on return, easier for Young Link than Link) [wiki:Boomerang]; boomerang cancel
(catching the boomerang cancels landing lag, special fall and other states)
[wiki:Boomerang_cancel].

## Neutral game

- Core loop: keep moving, pull a bomb whenever the opponent cannot reach him in time,
  then threaten with it. Holding ("cooking") the bomb without throwing it makes opponents
  commit early [lib:Young Link Collection].
- Bombs and arrows are aimed where the opponent will be; they are mainly meant to block
  options, not to hit. The boomerang is usually skipped off the ground rather than thrown
  straight [lib:Young Link Collection].
- Do not give up stage for a bomb pull when the opponent is close: use full hop
  double/triple aerials, cross-up bair or dash dance grab instead
  [lib:Young Link Collection].
- Spacing tools: short hop fair (frame 14, one long swing that also hits behind him
  [fd] [wiki:Young_Link_(SSBM)]), ftilt (frame 11, much faster than Link's frame 16
  [wiki:Young_Link_(SSBM)]), nair to trade.
- Against crouch cancel: spaced fair, ftilt, bombs, arrows, dtilt, dair, cross-ups; after
  an aerial on a crouching opponent, shield and shield grab their crouch-cancel dsmash
  [lib:Young Link Collection].
- Uair beats approaches from above, including Fox's and a full-hopping Falco's dair
  [lib:Young Link Collection].
- Stages: platforms help (ban Final Destination against Peach and fear it against Sheik's
  chain grab) [lib:Young Link Collection].

## Punish game

Young Link's damage comes from juggles: uair and utilt repeated under the opponent, with
projectiles forcing a double jump. Throws give uair/utilt (uthrow: base 18, growth 230,
90 degrees, not weight dependent) or a tech chase (dthrow: base 60, growth 50)
[lib:Young Link Collection] [wiki:Young_Link_(SSBM)]. Combos should end with the opponent
offstage.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| uthrow | Fox | 19-25% (no DI) | grab/utilt/uair; Fox is not knocked down and cannot jump out, +9 to +10 | | [lib:Young Link Collection] |
| uthrow | Fox, Falco | low-mid | uair or utilt, repeat | fastest uair whiffs on Fox unless spaced; late uair better | [lib:Young Link Collection] |
| uthrow | Fox | about 80% | tech chase on Yoshi's Story top platform | | [lib:Young Link Collection] |
| dthrow | Fox | low | tech chase (grab, dsmash, dash attack) | | [lib:Young Link Collection] |
| dthrow | Fox | above 110% | dsmash | | [lib:Young Link Collection] |
| dthrow | Fox | about 150% | ftilt (kills) | | [lib:Young Link Collection] |
| utilt | Fox | 50% | combos (into uair/utilt) | | [lib:Young Link Collection] |
| weak dair | Fox | 23% (strong hit at 15%) | another dair | autocancel | [lib:Young Link Collection] |
| jab, jab | Fox | 15-43% | repeats into itself | triple jab: 17-43% | [lib:Young Link Collection] |
| jab | Marth | 16-46% | repeats into itself | | [lib:Young Link Collection] |
| dthrow, utilt | Marth | 46%, Yoshi's Story | Death Mountain | | [lib:Young Link Collection] |
| uthrow | Marth | 53%, Yoshi's Story | Death Mountain | | [lib:Young Link Collection] |
| dthrow | Marth | about 120% | dair (kills) | | [lib:Young Link Collection] |
| short hop bair | Marth | low | grab | needs poor DI | [lib:Young Link Collection] |
| bomb | Jigglypuff, Peach | any | dair or uair | "bomb dair" is the cornerstone kill | [lib:Young Link Collection] |
| uthrow | any | very high | dair meteor | up to about 200% | [wiki:Young_Link_(SSBM)] |
| shield grab | Peach dsmash, Sheik dsmash, Marth fsmash | any | throw follow-up | guaranteed on Sheik's dsmash | [lib:Young Link Collection] |

### Chain grabs and tech chases

Fthrow can chain grab heavy characters [wiki:Young_Link_(SSBM)]; no percent data found.
The main game is tech chasing after dthrow or a knockdown hit, using dsmash, spaced dash
attack, point-blank boomerang (covers two options well) or a jump-cancel grab on reaction
[lib:Young Link Collection]. Port priority matters: the lower port acts one frame earlier
out of a throw [lib:Young Link Collection].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| dash attack (11%) | "some characters" | from about 95% | hit frames 7-12; laggy on whiff | [wiki:Young_Link_(SSBM)] |
| Death Mountain (late dair on platform) | Fox | 72% Yoshi's Story, 82% Fountain of Dreams | target on platform | [lib:Young Link Collection] |
| Death Mountain | Marth / Peach | from 59% / 52%, Yoshi's Story | target on platform | [lib:Young Link Collection] |
| dthrow into dair | Marth | about 120% | | [lib:Young Link Collection] |
| dthrow into ftilt | Fox | about 150% | | [lib:Young Link Collection] |
| uair | Peach | 126% Battlefield side platform, 130% Fountain of Dreams, 144% Dream Land | no DI | [lib:Young Link Collection] |
| utilt | most | 120%+ | kills earlier than his usmash | [wiki:Young_Link_(SSBM)] |
| dsmash (13%, 30 degrees) | most | Unknown | best near the ledge | [wiki:Young_Link_(SSBM)] |
| nair (12% clean) | recovering opponents | Unknown | offstage edgeguard | [wiki:Young_Link_(SSBM)] |

- Edgeguarding plan: use non-committal projectiles from far to force the opponent low,
  then jump out with nair; cover a failed attempt with up B or air dodge into hookshot
  [lib:Young Link Collection].
- At the ledge: dsmash (charge it to react), ftilt, dash attack on anything that does
  not sweetspot; dtilt's tip is a strong meteor on ledge-hanging opponents
  [wiki:Young_Link_(SSBM)] [lib:Young Link Collection].
- Against Fox/Falco: boomerang angled down to hit side B aimed at the ledge; fire arrow
  or bomb at an up B start-up; nair when close [lib:Young Link Collection].
- "Marth killer": roll to the ledge, hold shield (Z) tilted toward the ledge, release
  when Marth up Bs [lib:Young Link Collection].

## Recovery

- **Options:**
  - Double jump (height 23.0 units [wiki:Young_Link_(SSBM)]) and good air speed (1.0).
  - Aerial up B: five hits, frames 8-50 of 79 [fd]; slightly more control than Link's
    [wiki:Young_Link_(SSBM)].
  - Hookshot wall grapple with air dodge / grapple boost [lib:Young Link Collection].
  - Wall jump (momentarily invincible, can be followed by air dodge or double jump aerial
    [lib:Young Link Collection]).
  - Bomb explosion to regain up B; double jump late to burn the fuse and DI toward the
    stage [lib:Young Link Collection]. He cannot use Link's Spin Attack bomb jump
    [wiki:Bomb_recovery].
  - Boomerang glide for a little extra distance.
- **Mixups:** Throw a boomerang or bomb at the ledge first; choose between up B to stage
  or platform, air dodge then hookshot, point-blank hookshot cancel onto the ledge, or
  falling low to sweetspot with up B. Z-drop a bomb as a decoy when the opponent comes out
  [lib:Young Link Collection].
- **Weaknesses:** Slow and predictable overall [wiki:Young_Link_(SSBM)]. Short hookshot.
  Fox and Falco holding the ledge can drop and bair the up B, shine him if he is low, or
  bair the hookshot [lib:Young Link Collection]. Being light, he is often simply hit too
  far to return.

### Edgeguarding Young Link

- Take the ledge. With the ledge held, up B has to land on stage in lag and the hookshot
  leaves him hanging on the wall.
- Fox/Falco: from the ledge, drop and bair the up B, or shine when he is low; an
  invincible ledge stall into bair covers both up B and hookshot
  [lib:Young Link Collection].
- Marth: dtilt and fsmash at the ledge reach hookshot and close up B positions, though
  the collection rates Marth's edgeguard on Young Link as hard [lib:Young Link Collection].
- Sheik: needles eat his jump or reposition him; drop-zone fair and ledge hop bair can be
  air dodged through by Young Link [lib:Young Link Collection].
- Expect a boomerang or bomb at the ledge before he commits; shield or stay on the ledge
  with invincibility.
- A realistic CPU Young Link mixes: up B sweetspot, air dodge + hookshot, and going high
  with bomb cover.

## Defense and out of shield

- Out of shield, fastest to slowest per the collection: Z-drop bomb (hitbox frame 5, only
  with a bomb in hand), nair (does not hit very low), uair (for tall opponents), bair for
  behind, grab (good range, slow) [lib:Young Link Collection]. Nair out of shield is 4
  frames of jump squat [wiki:Young_Link_(SSBM)] plus a frame 4 hitbox [fd], so frame 8.
- Up B out of shield hits frame 8 [fd] and is the fastest option that hits low, but the
  multi-hit version is escapable and unsafe; the collection calls it good only in version
  1.00 or near the ledge [lib:Young Link Collection]. This is the main defensive
  difference from Link, whose single-hit up B is a real kill move out of shield.
- Against Falco's pressure nothing is safe except possibly a Z-drop bomb; roll, spot
  dodge or wavedash out of shield [lib:Young Link Collection].
- The Deku Shield blocks weak projectiles when standing or crouching but is smaller and
  weaker than Link's shield [wiki:Young_Link_(SSBM)]. Against Falco lasers the listed
  recovery times are: powershield 1 frame, crouching Deku Shield 2, standing Deku Shield
  3, hard shield 5, getting hit 11 [lib:Young Link Collection].
- Combo escapes: nair, bair (legs tuck away on the first frames), double jump, air dodge
  into hookshot ledge cancel; Z-drop a held bomb [lib:Young Link Collection].
- Fox's shine knocks him down: tech it [lib:Young Link Collection].

## As the training dummy

- Weight 85 (17th-19th), fall speed 2.13, fast-fall 2.2 [wiki:Young_Link_(SSBM)]: a light
  character with mid fall speed. He is launched farther than Link by the same hit.
- [Sheik](sheik.md) chain grabs him with dthrow, guaranteed somewhere between about 10%
  and 50-60%; correct DI is full away below that range and behind above it
  [lib:Young Link Collection] [wiki:Chain_grab].
- [Marth](marth.md) chain grabs him at low percent and throws into fsmash near the ledge;
  the recommended DI is down and away, never in [lib:Young Link Collection].
- Fox's shine causes knockdown instead of a slide, so waveshine chains do not work, but
  shine sets up a tech chase [wiki:Young_Link_(SSBM)]. Fox up throw up air works: DI
  behind on the throw and SDI the up air [lib:Young Link Collection].
- Falco pillar: DI full left/right on the shine and diagonally on the dair, tech after
  the dair [lib:Young Link Collection].
- Bombs put Young Link himself into tumble only from about 124% [wiki:Bomb_recovery].
- Small crouch and short stature: some high moves whiff.

## Matchup notes

### vs Fox

- Hard matchup. Fox's speed and shine (which reflects every projectile) limit zoning.
  Shine on shield holds Young Link for 8 frames, and the only out-of-shield option that
  beats high nair into shine is a Z-drop bomb [lib:Young Link Collection].
- Young Link's edge: fair outspaces Fox, uair beats Fox from above, and Fox's light
  weight and fall speed make uair/utilt juggles long. A Z-dropped bomb onto shine locks
  Fox in the reflect animation [lib:Young Link Collection].
- Edgeguard matters most: boomerang/arrow from far, nair close, charged dsmash at the
  ledge [lib:Young Link Collection].

### vs Falco

- Falco wins up close and with lasers. Use platforms to leave the laser line, powershield
  when possible, and keep mid range [lib:Young Link Collection].
- Falco's dair cannot get past uair when he full hops. Edgeguarding is the same as Fox
  but easier; cover side B with utilt [lib:Young Link Collection].

### vs Sheik

- Do not get grabbed (chain grab about 10-50%+); Final Destination is the worst stage
  [lib:Young Link Collection].
- Juggle her with utilt and uair; shield grab her dsmash; edgeguard her up B by standing
  up from the ledge at the right time [lib:Young Link Collection].

### vs Marth

- Marth outranges him and his dash dance ducks under projectiles; skip the boomerang
  along the ground and whiff punish with grab. Shield grab fsmash
  [lib:Young Link Collection].
- Learn to ledgedash: Marth's dtilt makes getting off the ledge hard
  [lib:Young Link Collection].

### vs Jigglypuff

- The historical counterpick matchup (Armada over Hungrybox, 2011-2014)
  [wiki:Young_Link_(SSBM)]. Hit-and-run with bombs; "bomb dair" is the kill.
- Avoid boomerang against a Puff who is already airborne; she swings through it. A missed
  Rest gives about 4 seconds; include a bomb in the punish (uthrow puts her into a bomb
  above for 8%) [lib:Young Link Collection].

### vs Peach

- Young Link is regarded as one of the best Peach counters [wiki:Young_Link_(SSBM)]. He
  wins at range because he can pull bombs while moving; he loses close up to float-cancel
  aerials, dsmash, dash attack and grab [lib:Young Link Collection].
- Hold a bomb to freeze her; do not boomerang while she floats; nair goes through
  turnips; shield grab dsmash with the shield tilted down [lib:Young Link Collection].

### vs Captain Falcon

- Running away does not work against his speed; move toward and under him and use short
  hop uair. An offstage Falcon should always die [lib:Young Link Collection].

## Drill seeds

### Z-drop bomb out of shield versus spacie pressure

- **id:** `young-link-zdrop-oos`
- **Goal:** Escape shine pressure with the frame 5 Z-drop.
- **Player:** Young Link
- **CPU:** Fox, Falco
- **Setup:** Young Link in shield holding a bomb, centre stage. CPU at 0-60%.
- **CPU behaviour:** Short hop nair or dair on shield into shine, then repeats or grabs;
  aerial height randomised (high or low).
- **Success:** The dropped bomb hits the CPU and a follow-up aerial or grab lands.
- **Fail:** Young Link is hit or grabbed, or rolls away without a punish.
- **Variations:** No bomb in hand (must choose nair/uair/roll); Falco with lasers first.
- **Data needed:** Shield stun of Fox/Falco aerials and shine, Z-drop hitbox frame, jump
  squat 4.

### Death Mountain platform kill

- **id:** `young-link-death-mountain`
- **Goal:** Hit the late dair meteor on a platform target.
- **Player:** Young Link
- **CPU:** Fox, Marth, Peach
- **Setup:** Yoshi's Story (or Fountain of Dreams / Pokemon Stadium). CPU on a side
  platform at 60-90% in knockdown; Young Link directly below.
- **CPU behaviour:** Random tech in place, tech left/right, or missed tech.
- **Success:** The meteor hitbox connects and the CPU is KO'd off the top.
- **Fail:** Tip hit only, whiff, or no L-cancel followed by a CPU punish.
- **Variations:** Start from an up throw at the listed percents (Marth 53%); lower percent
  to find the kill threshold per stage.
- **Data needed:** Full hop trajectory, dair hit frames 13-64, platform heights, meteor
  hitbox knockback (base 70, growth 100), stage ceilings.

### Bomb into down air on floaties

- **id:** `young-link-bomb-dair`
- **Goal:** Confirm a kill from a bomb hit.
- **Player:** Young Link
- **CPU:** Jigglypuff, Peach
- **Setup:** Battlefield or Dream Land. Young Link holds a bomb; CPU airborne at mid range
  at 70-110%.
- **CPU behaviour:** Drifts in and out with aerials (Puff bair, Peach float nair/fair);
  sometimes shields on landing.
- **Success:** Bomb hits and dair (or uair) connects during the bomb's hitstun.
- **Fail:** Young Link is hit, is caught in his own explosion, or the follow-up misses.
- **Variations:** Start without a bomb so the pull must be earned; require the kill.
- **Data needed:** Bomb multi-hit damage and hitstun, dair startup 13, CPU aerial ranges.

### Edgeguarding Fox and Falco

- **id:** `young-link-edgeguard-spacies`
- **Goal:** Pick projectile, nair or ledge dsmash according to the recovery.
- **Player:** Young Link
- **CPU:** Fox, Falco
- **Setup:** CPU launched offstage at 50-90% to a random distance and height, with or
  without double jump. Young Link at centre stage.
- **CPU behaviour:** Random: side B to ledge, side B to stage, shortened side B, up B at
  varied angles, double jump then either.
- **Success:** CPU loses the stock.
- **Fail:** CPU regains the stage or ledge; Young Link is hit or dies.
- **Variations:** Start with a bomb in hand; start on the ledge; no projectiles allowed.
- **Data needed:** Fox/Falco side B and up B timings, dsmash frames 9-11/21-23, boomerang
  release frame 27, nair 4-27.

### Tech chase Fox after down throw

- **id:** `young-link-techchase-fox`
- **Goal:** Cover Fox's tech options with dsmash or reaction grab.
- **Player:** Young Link
- **CPU:** Fox (also Falco, Captain Falcon)
- **Setup:** Young Link holding Fox in grab at 10-40%, centre stage.
- **CPU behaviour:** DI random; then tech in place (sometimes with buffered shine or spot
  dodge), tech toward, tech away, or miss tech and choose a getup.
- **Success:** A hit or regrab connects before Fox is actionable.
- **Fail:** Fox escapes or hits first.
- **Variations:** Near the ledge (dsmash covers four options); on a platform; restrict to
  jump-cancel grab.
- **Data needed:** Fox tech timings (in place invincible 1-20, vulnerable 21-26; roll
  vulnerable 21-40), grab frame 10, dsmash frames.

### Recover against a ledge-holding spacie

- **id:** `young-link-recovery-mixup`
- **Goal:** Choose between up B, hookshot and wall jump.
- **Player:** Young Link
- **CPU:** Fox, Falco, Marth
- **Setup:** Young Link offstage at 60-100% at random height, sometimes with a bomb in
  hand. CPU near the ledge.
- **CPU behaviour:** Random: grab ledge and drop bair; stay on stage and dsmash/dtilt;
  jump out with an aerial.
- **Success:** Young Link reaches the ledge or stage without being hit.
- **Fail:** Hit, missed grapple, or death.
- **Variations:** No double jump; boomerang glide distance; stages with walls for wall
  jump (Yoshi's Story, Pokemon Stadium).
- **Data needed:** Hookshot range, up B travel and sweetspot, CPU ledge invincibility.

### Up air juggle

- **id:** `young-link-uair-juggle`
- **Goal:** Keep a fastfaller above him with repeated uair/utilt.
- **Player:** Young Link
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** CPU launched straight up from centre stage at 30-60%.
- **CPU behaviour:** Falls with random drift, sometimes double jumps, air dodges or
  attacks down with dair/nair.
- **Success:** Three or more consecutive uair/utilt hits, or 40% dealt before the CPU
  lands.
- **Fail:** CPU lands safely or hits Young Link.
- **Variations:** Under a platform; require ending the string with a hit that sends
  offstage.
- **Data needed:** Uair frames 5-49 and landing lag 30/15, utilt frames 9-15, CPU fall
  speeds.

### Escape Sheik's chain grab

- **id:** `young-link-vs-sheik-chaingrab-di`
- **Goal:** Learn the DI that ends Sheik's dthrow chain grab at each percent.
- **Player:** Young Link
- **CPU:** Sheik
- **Setup:** Final Destination. Sheik holds Young Link in grab at a random percent from
  0% to 70%.
- **CPU behaviour:** Dthrow, then regrab or follow up according to Young Link's DI.
- **Success:** Young Link avoids the regrab (lands and acts, or is out of range).
- **Fail:** Regrabbed or hit by the follow-up.
- **Variations:** Show or hide the percent; port priority swapped.
- **Data needed:** Sheik dthrow knockback and end lag, Young Link weight 85 and fall
  speed, the 10% to 50-60% window.

### Projectile wall and bomb pull safety

- **id:** `young-link-safe-bomb-pull`
- **Goal:** Recognise when a 39-frame bomb pull is safe.
- **Player:** Young Link
- **CPU:** Captain Falcon, Marth, Fox
- **Setup:** Final Destination, random starting distance from half to full stage.
- **CPU behaviour:** Approaches at full speed with a random delay and punishes any lag it
  reaches.
- **Success:** Bomb in hand and Young Link actionable (or shielding) before the CPU's
  attack arrives, five times in a row.
- **Fail:** Hit during the pull.
- **Variations:** Aerial pulls; add a boomerang first; platforms.
- **Data needed:** Down B 39 frames, CPU dash/run speeds, stage width.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlCl.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/young-link.json`](../framedata/young-link.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 6-8 | 3 | Sakurai | 10 | 60 | - | slash | 23 | 20 | 3 | -10 |  |
| Jab 2 | `jab2` | 7-8 | 2 | Sakurai | 10 | 60 | - | slash | 22 | 18 | 2 | -8 | starts 1 frame late (included) |
| Jab 3 | `jab3` | 7-11 | 5 | Sakurai | 10 | 100 | - | slash | 50 | 33 | 4 | -21 | starts 1 frame late (included) |
| Rapid jab start | `rapid_jab_start` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Rapid jab loop | `rapid_jab_loop` | 2-3, 9-10, 16-17, 23-24, 30-31 | 1 | 0 | 15 | 40/50/60 | - | slash | 34 | - | 2 | -30 |  |
| Rapid jab end | `rapid_jab_end` | - | - | - | - | - | - | - | 10 | - | - | - |  |
| Dash attack | `dash_attack` | 7-12 | 11/10 | Sakurai | 10 | 100 | - | slash | 53 | 40 | 6 | -26 |  |
| Up tilt | `utilt` | 9-15 | 8 | 85/70 | 20 | 128/126/124/130 | - | slash | 29 | - | 5 | -15 |  |
| Down tilt | `dtilt` | 14-16 | 10/9/7 | 280/70 | 80 | 50 | - | slash | 39 | 32 | 6 | -11 |  |
| Up smash | `usmash` | 11-14 | 3 | 98 | 40 | 100 | 23/29/31 | slash | 60 | 52 | 3 | -37 | charge hold frame 4 |
|  |  | 26-28 | 2 | 90 | 0 | 100 | 28/31/35/37 | slash |  |  | 2 | -23 |  |
|  |  | 40-42 | 7/8 | 100 | 70 | 70 | - | slash |  |  | 5 | -6 |  |
|  |  | 43-44 | 8/9 | 30 | 50 | 70 | - | slash |  |  | 6 | -2 |  |
| Down smash | `dsmash` | 9-11 | 13/7 | 30/70 | 30 | 90 | - | slash | 49 | 42 | 7 | -25 | charge hold frame 4 |
|  |  | 21-23 | 12/6 | 30 | 25 | 90/70 | - | slash |  |  | 7 | -13 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 4-5 | 12 | Sakurai | 15 | 100 | - |  | 39 | 36 | 7 | 15 | 7 | <4, >31 | +0 |  |
|  |  | 6-27 | 8 | Sakurai | 10 | 100 | - |  |  |  | 5 |  |  |  | -2 |  |
| Forward air | `fair` | 14-16 | 12/11/9 | Sakurai | 5 | 100 | - | slash | 55 | 47 | 7 | 15 | 7 | <1, >46 | +0 |  |
|  |  | 17-33 | 8/7/5 | 76 | 0 | 90 | - | slash |  |  | 5 |  |  |  | -2 |  |
| Back air | `bair` | 6-9 | 7 | Sakurai | 0 | 100 | - |  | 39 | 30 | 5 | 15 | 7 | <1, >28 | -2 |  |
|  |  | 18-23 | 7 | Sakurai | 15 | 100 | - |  |  |  | 5 |  |  |  | -2 |  |
| Up air | `uair` | 5-7 | 15 | 80 | 25 | 85 | - | slash | 69 | 60 | 8 | 30 | 15 | <5, >55 | -7 |  |
|  |  | 8-49 | 12 | 80 | 25 | 85 | - | slash |  |  | 7 |  |  |  | -8 |  |
| Down air | `dair` | 13-15 | 14/16 | 70/270 | 40/70 | 100 | - | slash/fire | 89 | 80 | 9 | 50 | 25 | <13, >64 | -16 |  |
|  |  | 16-64 | 17/21 | 70/270 | 40/70 | 100 | - | slash/fire |  |  | 11 |  |  |  | -14 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 11-18 | 85 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 14-21 | 95 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 10 | 25 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 6 | 3 | 55 | 25 | 110 | - | - | 16 | 39 |  |
| Back throw | `bthrow` | 6 | 3 | 130 | 24 | 110 | - | - | 16 | 39 |  |
| Up throw | `uthrow` | 6 | 2 | 90 | 18 | 230 | - | - | 27 | 49 |  |
| Down throw | `dthrow` | 6 | 4 | 90 | 60 | 50 | - | - | 28 | 49 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Fire Bow, ground, Start | `special_n_start` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Neutral B: Fire Bow, ground, Loop | `special_n_loop` | - | - | - | - | - | - | - | 27 | - | - | - |  |
| Neutral B: Fire Bow, ground, End | `special_n_end` | - | - | - | - | - | - | - | 24 | - | - | - |  |
| Neutral B: Fire Bow, air, Start | `special_air_n_start` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Neutral B: Fire Bow, air, Loop | `special_air_n_loop` | - | - | - | - | - | - | - | 27 | - | - | - |  |
| Neutral B: Fire Bow, air, End | `special_air_n_end` | - | - | - | - | - | - | - | 24 | - | - | - |  |
| Side B: Boomerang, ground, 1 | `special_s1` | - | - | - | - | - | - | - | 45 | - | - | - | spawns article/projectile on 5 |
| Side B: Boomerang, ground, 2 | `special_s2` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Side B: Boomerang, ground, 1 | `special_s1_304` | - | - | - | - | - | - | - | 45 | - | - | - |  |
| Side B: Boomerang, air, 1 | `special_air_s1` | - | - | - | - | - | - | - | 45 | - | - | - | spawns article/projectile on 5 |
| Side B: Boomerang, air, 2 | `special_air_s2` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Side B: Boomerang, air, 1 | `special_air_s1_307` | - | - | - | - | - | - | - | 45 | - | - | - |  |
| Up B: Spin Attack, ground | `special_hi` | 8-10, 11-13, 14-16, 17-19, 20-22, 23-25, 26-28, 29-31, 32-34, 35-37, 38-40, 41-43 | 1 | 173 | 80/60 | 40 | - | slash | 79 | - | 2 | - |  |
|  |  | 44 | 3 | 80 | 60 | 100 | - | slash |  |  | 3 | - |  |
| Up B: Spin Attack, air | `special_air_hi` | 8-13 | 3 | 88/79/70/60 | 0 | 100 | 80 | slash | 79 | - | 3 | - |  |
|  |  | 16-20 | 2 | 88/79/70/60 | 0 | 100 | 72 | slash |  |  | 2 | - |  |
|  |  | 22-27 | 2 | 88/79/70/60 | 0 | 100 | 70 | slash |  |  | 2 | - |  |
|  |  | 31-37 | 2 | 88/79/70/60 | 0 | 100 | 68 | slash |  |  | 2 | - |  |
|  |  | 46-50 | 3 | Sakurai | 40 | 180 | - | slash |  |  | 3 | - |  |
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
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
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
| Neutral air | jump | 8 | `nair` |
| Up air | jump | 9 | `uair` |
| Up B | jump cancel | 9 | `special_hi` |
| Back air | jump | 10 | `bair` |
| Shield grab | direct | 11 | `grab` |
| Up smash | jump cancel | 12 | `usmash` |
| Down air | jump | 17 | `dair` |
| Forward air | jump | 18 | `fair` |
| Spot dodge | direct | intangible 2-15 of 22 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 37 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 37 | `roll_backward` |
| Wavedash | jump | actionable on frame 16 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Young Link indexed by [The Melee Library](https://www.meleelibrary.com/#young-link) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Young Link Melee Techs Guide](https://www.youtube.com/watch?v=g2d9nLIGfXs&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=13&t=0s) | Third Chair | Video guide on performing useful Young Link tech in 2020. |
| [20XX Young Link Tools, Part 1: Bomb Pull Ledge Grabs](https://www.youtube.com/watch?v=vsT7AhfkIbo) | Chandy | Chandy shows various movement tricks to get to the ledge quickly after a bomb pull. |
| [Young Link Discussion](http://smashboards.com/threads/young-link-discussion.301062/) | community | Meant to be a social thread for Young Link mains, but still contains interesting information. Use the search function. |
| [A Young Link Killing FAQ](http://smashboards.com/threads/having-trouble-getting-that-kill-a-laijin-yl-killing-faq-who-wants-me-to-update.99549/) | Laijin | This guide is rather old but you can still find useful information. |
| [Bombs Away! ~ A Guide on Young Link's Bombs](http://smashboards.com/threads/bombs-away-a-guide-on-young-links-bombs-by-njzfinest.79517/) | NJzFinest | NJzFinest describes multiple ways to use your bombs in order to rack up percents and setup kills. |
| [Stage Ban and Counterpick Guide](http://smashboards.com/threads/updated-12-08-09-ylinks-official-stage-ban-and-counter-pick-guide.179907/) | rhan | This guide is outdated, it still includes old stage picks like Kongo Jungle 64 or Brinstar. You can still browse it to get a general idea of what Young Link mains think about stage counterpicks, but not everything will be accurate. |
| [Hookshot Frenzy: A guide on Young Link's Hookshot](http://smashboards.com/threads/video-included-hookshot-frenzy-a-guide-on-young-links-hookshot-by-smashmac-mac.87676/) | SmashMac | Technical explanation of Young Link's hookshot, as well as various ways to use it effectively. |
| [Young Link Hitboxes and Frame Data](http://smashboards.com/threads/young-link-hitboxes-and-frame-data.301753/) | Stratocaster, Standardtoaster, and SuperDoodleMan |  |
| [Young Link Optimization Project](http://smashboards.com/threads/young-link-optimization-project-current-topic-edgeguarding-spacies.425503/) | community | Chandy's massive Young Link project. Read away! |
| [The Master of The Bomb: A Compiled List of All Bomb Advanced Tech](http://smashboards.com/threads/the-master-of-the-bomb-a-compiled-list-of-all-bomb-at.410094/) | Ghetto Ninja | More bomb technology. |
| [Young Link Matchups 2015](http://smashboards.com/threads/official-young-link-match-ups-2015.379092/) | community | Community discussion regarding Young Link's various matchups. |
| [Young Link Collection](https://docs.google.com/document/d/1N0XBRQz8DmCkTIRAh8nJa2tcjP2PhMG0riRnj1e4nho/edit) | Neil Harbin | "This is a collection of all knowledge that could be be useful in competitive Young Link play." |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Young Link (SSBM): https://www.ssbwiki.com/Young_Link_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Young_Link_(SSBM)/Down_aerial ,
  /Up_special , /Dash_attack , /Neutral_special , /Down_special , /Side_special ,
  /Neutral_aerial
- SSBWiki, Link (SSBM): https://www.ssbwiki.com/Link_(SSBM)
- SSBWiki, Bomb (Link) (covers Young Link's bombs and bomb techniques):
  https://www.ssbwiki.com/Bomb_(Link)
- SSBWiki, Bomb recovery: https://www.ssbwiki.com/Bomb_recovery
- SSBWiki, Boomerang, Boomerang glide, Boomerang cancel: https://www.ssbwiki.com/Boomerang ,
  https://www.ssbwiki.com/Boomerang_glide , https://www.ssbwiki.com/Boomerang_cancel
- SSBWiki, Fire Arrow: https://www.ssbwiki.com/Fire_Bow
- SSBWiki, Wall grapple and Hookshot: https://www.ssbwiki.com/Wall_grapple ,
  https://www.ssbwiki.com/Hookshot
- SSBWiki, Chain grab: https://www.ssbwiki.com/Chain_grab
- SSBWiki, List of SSBM tier lists (NTSC): https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Melee Library card "Young Link Collection" (Neil Harbin), text export read in part
  (overview notes, throws, recovery tech, out of shield, Fox/Falco/Sheik/Marth/Falcon/
  Jigglypuff/Peach sections):
  https://docs.google.com/document/d/1N0XBRQz8DmCkTIRAh8nJa2tcjP2PhMG0riRnj1e4nho/edit
- Melee Library card "Young Link Optimization Project" (first post), via web.archive.org:
  http://smashboards.com/threads/young-link-optimization-project-current-topic-edgeguarding-spacies.425503/
- Melee Library card "A Young Link Killing FAQ" (Laijin, 2007; first post, general
  descriptions only), via web.archive.org:
  http://smashboards.com/threads/having-trouble-getting-that-kill-a-laijin-yl-killing-faq-who-wants-me-to-update.99549/
- Melee Library card "The Master of The Bomb" (first post), via web.archive.org:
  http://smashboards.com/threads/the-master-of-the-bomb-a-compiled-list-of-all-bomb-at.410094/
- Frame data dump: `fd/json/Young Link.json`
- Not read: the video cards, "Bombs Away!", "Hookshot Frenzy", "Young Link Matchups 2015",
  stage guide (downloaded but not used for claims).
