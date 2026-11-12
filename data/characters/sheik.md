---
schema: melee-character/v1
id: sheik
name: Sheik
aliases: [Shiek, Seak, "Zelda's alter ego"]
tier: "A (5th of 26), 2021 PG Stats tier list (13th official NTSC list)"
archetype: [punish-heavy, tech-chase, chaingrab, edgeguarder, projectile, grappler]
related: [zelda]
summary: Sheik plays a controlled, reactive neutral around forward air, tilts, needles and grab, then turns one NTSC down throw into a chain grab, reaction tech chase or juggle that ends in a forward air edgeguard.
key_tech: [dthrow-tech-chase, dthrow-chaingrab, dthrow-di-followups, needle-cancel, boost-grab, autocancel-fair, ftilt-fair, jab-reset, shino-stall, sheik-ledgedash, vanish-recovery, transform-recovery]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlSk.dat
framedata: ../framedata/sheik.json
code: src/melee/ft/kinds/ftSeak
specials:
  neutral_b: "Needle Storm (needles)"
  side_b: "Chain"
  up_b: "Vanish"
  down_b: "Transform"
attributes:
  weight: 90
  gravity: 0.12
  fall_speed: 2.13
  fast_fall_speed: 3
  jump_squat: 3
  jumps: 2
  walk_speed: 1.2
  dash_speed: 1.7
  run_speed: 1.8
  traction: 0.08
  air_speed: 0.8
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [2, 16, 4]
  jab2: [3, 17, 3]
  rapid_jab_start: [null, 7, 0]
  rapid_jab_loop: [2, 36, 1]
  rapid_jab_end: [null, 9, 0]
  dash_attack: [6, 36, 10]
  utilt: [5, 26, 8]
  dtilt: [5, 28, 8]
  fsmash: [12, 46, 10]
  usmash: [12, 40, 17]
  dsmash: [5, 46, 13]
  nair: [3, 42, 14]
  fair: [5, 34, 13]
  bair: [4, 38, 14]
  uair: [5, 37, 12]
  dair: [15, 49, 11]
  grab: [7, 31, 0]
  dash_grab: [8, 41, 0]
  pummel: [10, 25, 3]
  fthrow: [20, 48, 2]
  bthrow: [15, 48, 2]
  uthrow: [19, 58, 2]
  dthrow: [31, 58, 3]
  special_n_start: [null, 8, 0]
  special_n_loop: [null, 18, 0]
  special_n_cansel: [null, 8, 0]
  special_n_end: [null, 40, 0]
  special_air_n_start: [null, 8, 0]
  special_air_n_loop: [null, 18, 0]
  special_air_n_cansel: [null, 8, 0]
  special_air_n_end: [null, 40, 0]
  special_s_start: [22, 25, 5]
  special_s_end: [null, 40, 0]
  special_s: [null, 30, 0]
  special_air_s_start: [22, 25, 5]
  special_air_s_end: [null, 40, 0]
  special_air_s: [null, 30, 0]
  special_hi_start: [null, 36, 0]
  special_hi: [null, 40, 0]
  special_air_hi_start: [null, 36, 0]
  special_air_hi: [null, 40, 0]
  special_lw: [null, 37, 0]
  special_lw2: [null, 26, 0]
  special_air_lw: [null, 37, 0]
  special_air_lw2: [null, 26, 0]
oos:  # option: frame the hitbox is out
  nair: 6
  bair: 7
  grab: 7
  fair: 8
  uair: 8
  usmash: 13
  dair: 18
resources: 44
# generated: end
---

# Sheik

<!-- GENERATED:attributes -->
## Attributes

Read from `PlSk.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 90 |
| Gravity | 0.12 |
| Terminal fall speed | 2.13 |
| Fast-fall speed | 3 |
| Jump squat (frames before airborne) | 3 |
| Full hop / short hop initial Y speed | 2.8 / 2.14 |
| Air jump Y multiplier | 1.1 |
| Jumps | 2 |
| Walk max speed | 1.2 |
| Dash initial speed / run max speed | 1.7 / 1.8 |
| Ground friction (traction) | 0.08 |
| Air max horizontal speed | 0.8 |
| Air acceleration (base + stick) | 0.02 + 0.04 |
| Air friction | 0.04 |
| Normal landing lag | 4 |
| Shield size | 11.625 |
<!-- /GENERATED:attributes -->

## Overview

Sheik is Zelda's transformed form: a fast, fairly heavy (weight 90), fast-falling character
with quick, low-lag attacks that launch upward and chain into each other [wiki:Sheik_(SSBM)].
Her neutral is not dominant: she has a short dash dance, a high short hop and little disjoint,
so she works inside a compact "threat zone" where forward air, tilts, dash attack, boost grab
and falling needles into grab are all live [wiki:Sheik_(SSBM)]. Her punish game is among the
best in the game. In NTSC her down throw launches at 80° with low knockback
[wiki:Sheik_(SSBM)/Down_throw], which gives a chain grab on about a dozen characters, a
reaction [tech chase](../techniques/tech-chase.md) on fastfallers (Fox, Falco, Captain Falcon)
and guaranteed aerials on floaties. She kills by edgeguarding with forward air (a 25°
semi-spike [fd]), back air and needles, or with a sweetspot up smash / up air off a throw. She
dies to juggles and combos (low air speed, fast fall, no good move below her) and to a short,
exploitable recovery. She is easy to pick up, but her top-level punish (reacting to down throw
DI and tech options every time) demands very consistent reactions.

## Strengths and weaknesses

- **Strengths:**
  - NTSC down throw: chain grab, tech chase or combo on the whole cast
    [wiki:Sheik_(SSBM)/Down_throw].
  - Forward air: hits frame 5, 13%, launch angle 25°, auto-cancels from frame 11 of the
    aerial [fd]; her main finisher and edgeguard move.
  - Fast ground moves that pop up: ftilt and dtilt hit frame 5, dash attack frame 6, jab
    frame 2 [fd].
  - Needles (neutral B): fast projectile, 3% each, up to 6, no meaningful landing lag when
    thrown from the air [wiki:Needle_Storm].
  - Edgeguarding: fair, bair, needles, a fully intangible ledge stall [wiki:Ledgestall].
  - Crouch cancel game: she is heavy and has frame-5 crouching answers (tilts, down smash)
    and a strong crouch-cancel grab [web:docs.google.com Collection of Sheik Stuff].
  - Nair out of shield: hits frame 3, the fastest of her aerials [fd].
- **Weaknesses:**
  - Short dash dance ("fewest dash frames in the game") and a high short hop (poor SHFFL)
    [wiki:Sheik_(SSBM)].
  - Ground moves and most aerials are crouch cancelled at low percent, which forces her to
    rely on grab and down smash early in a stock [wiki:Sheik_(SSBM)].
  - Ground moves are unsafe on shield (ftilt about -17, utilt about -10)
    [web:docs.google.com Collection of Sheik Stuff].
  - Recovery: up B (Vanish) travels a short distance, has no hitbox on reappearance, and
    locks her horizontal drift afterwards [wiki:Sheik_(SSBM)].
  - Combo food: low air speed (0.8) with fast fall speed (2.13, 3.0 fast-falling)
    [wiki:Sheik_(SSBM)].
  - Bad matchups: Jigglypuff (Rest punishes her lag and recovery), Ice Climbers, and
    historically Fox [wiki:Sheik_(SSBM)].

## Character tech

### Down throw reaction tech chase

- **id:** `dthrow-tech-chase`
- **What:** After down throw on a fastfaller (who lands before he can act), Sheik watches the
  landing and regrabs every tech option on reaction, repeating until a launcher will combo.
- **Inputs:** Grab, down throw. Read the throw DI and move to the landing spot (walk toward DI
  away, stand still for in-front, turn for behind). Then: tech in place → standing grab; tech
  roll → [boost grab](#boost-grab) or dash JC grab; missed tech → jab (reset) or dtilt/regrab.
- **Timing:** Tech in place lasts 26 frames and tech rolls 40 frames for every character. Grab
  hits on frame 7, so the latest grab input that catches tech in place is frame 19 of the tech;
  the practical decision point is frame 18-19 [lib:Tech Chasing!]. Down throw releases on frame
  36 of a 57-frame animation regardless of victim weight [wiki:Sheik_(SSBM)/Down_throw].
- **Used for:** Fox, Falco and Captain Falcon: "you can tech chase every single option on
  reaction" [lib:Things Sheik Players Aren't Doing]. Carries them to the percent where ftilt
  or dash attack knocks down and combos.
- **Common errors:** Deciding late (tech-in-place shine from Fox/Falco hits her); guessing
  instead of reacting; mis-reading slight DI and being out of position; standing inside shine
  range (stand just outside it to widen the window
  [web:docs.google.com Collection of Sheik Stuff]).
- **Drill idea:** CPU Fox is down thrown at 0-30% with random DI and random tech; success if
  Sheik's regrab lands before the CPU's first actionable frame, N times in a row.

### Down throw chain grab

- **id:** `dthrow-chaingrab`
- **What:** Down throw into immediate regrab on characters who cannot land or act in time. See
  [chain grab](../techniques/chain-grab.md).
- **Inputs:** Grab, down throw, step/dash to follow DI, JC grab; repeat.
- **Timing:** NTSC only (80° launch; PAL changed it to 60°, which removes it)
  [wiki:Sheik_(SSBM)/Down_throw]. The player in the higher port has one more frame: against
  Peach on DI away it is a true, frame-perfect chain grab only from the higher port
  [lib:Sheik on Peach Action].
- **Used for:** Bowser, Ganondorf, Link, Mr. Game & Watch, Ness, Pichu, Pikachu, Roy, Sheik,
  Yoshi and Young Link "from 0% to as high as 90%" [wiki:Sheik_(SSBM)/Down_throw]; on other
  characters only on DI away (see below).
- **Common errors:** Regrabbing in the wrong direction after DI behind; grabbing too early
  (whiff under them) or too late (they jump); continuing past the percent where they fly too
  high instead of switching to up smash / aerial.
- **Drill idea:** CPU Link/Pikachu/Sheik in grab at 0% with random DI; count consecutive
  regrabs until the first escape.

### Down throw follow-ups by DI (non-fastfallers)

- **id:** `dthrow-di-followups`
- **What:** On mid-weights and floaties that pop up out of down throw, the follow-up is chosen
  by reacting to DI: regrab DI away, utilt or up air on no DI / DI behind.
- **Inputs:** DI away → dash regrab. Slight DI away → regrab (low percent) or dash short-hop
  up air. No DI → delayed utilt (both hits) or rising full-jump up air. DI behind → turn
  around, then utilt.
- **Timing (vs [Marth](marth.md)):** full DI away can be regrabbed until about 80%; slight DI
  away on the 45° notch can be regrabbed without dashing until 27% after the throw (about 0-16%
  before it); from about 15% switch to short-hop auto-cancelled up air on slight DIs; full-jump
  rising up air is best from about 20% after the throw [lib:Doing Bad Stuff To Marth 101].
  Utilt's second hit lands on frame 19 and utilt is interruptible from frame 26, so utilt →
  grab hits 16 frames after the second hit connects [web:docs.google.com Collection of Sheik
  Stuff].
- **Used for:** Marth, Peach, Samus, Dr. Mario, Jigglypuff, Ice Climbers. "Against non
  fastfallers you can chaingrab the DIs away, and use uptilt/turn uptilt/dash upair for the
  other DIs" [lib:Things Sheik Players Aren't Doing].
- **Common errors:** Predictable utilt timing (victim SDIs up between hits); not turning around
  on DI behind; waiting for utilt's second hit when it will miss instead of acting at IASA.
- **Drill idea:** CPU Marth in grab at 0-80% picks one of {away, slight away, none, behind};
  success if the correct follow-up connects as a true combo.

### Needle cancel (falling needles into grab)

- **id:** `needle-cancel`
- **What:** Throwing stored needles from the air late in a jump so Sheik lands with no special
  landing lag and can act while the opponent is still in hitstun or shieldstun.
- **Inputs:** Charge needles (hold B; press shield to store). Short hop or full hop, press B
  after the apex and below the peak height of her first jump, land, then grab / dash attack /
  ftilt. "Reverse needle cancel": start charging in the air and press shield or Z to stow, also
  lagless [wiki:Needle_Storm].
- **Timing:** Each needle does 3%; up to 6 are stored; grounded needles fly straight, aerial
  needles fly 45° downward [wiki:Needle_Storm]. Landing after aerial needles costs only the
  normal 4 frames of landing lag, and a needle hit leaves her even or at frame advantage
  [lib:Things Sheik Players Aren't Doing]. Being hit while charging drops the stored needles
  [wiki:Needle_Storm].
- **Used for:** Opening shields and crouch cancellers (needles → grab); controlling the ranges
  outside her fair/ftilt/grab zone; interrupting recoveries; adding percent so ftilt reaches
  its knockdown threshold on Fox (24% fresh [web:docs.google.com Collection of Sheik Stuff]).
- **Common errors:** Throwing while rising (full lag in the air, no cancel); throwing too high
  so the needles pass over a grounded target; standing needles on the ground (long end lag).
- **Drill idea:** Sheik starts with 3-6 needles; CPU shields or crouches at mid range; success
  if needles connect and a grab lands within about 10 frames of Sheik landing.

### Boost grab

- **id:** `boost-grab`
- **What:** Cancelling the first frames of dash attack into a grab, which keeps the dash
  attack's forward burst and gives a longer, faster running grab.
- **Inputs:** While running, press A (dash attack) then Z almost immediately. The cancel window
  is the first few frames of the dash attack [unverified].
- **Timing:** Exact window not sourced. Dash attack itself hits on frame 6 [fd].
- **Used for:** Catching tech rolls away in tech chases and punishing retreating movement;
  together with dash attack it is her longest grounded threat
  [lib:Things Sheik Players Aren't Doing]. Needed when the victim DIs down throw away and
  techs away with full room [web:docs.google.com Collection of Sheik Stuff].
- **Common errors:** Too slow (dash attack comes out, which is unsafe on shield and crouch
  cancel); pressing Z first (plain dash grab, shorter).
- **Drill idea:** CPU Falcon techs away at max distance after down throw DI away; success only
  if the regrab lands before the roll's actionable frame.

### Auto-cancelled forward air

- **id:** `autocancel-fair`
- **What:** A short-hop fair timed early enough that she lands after the auto-cancel point and
  has only normal landing lag; her main zoning and shield-pressure aerial. See
  [auto-cancel](../techniques/auto-cancel.md).
- **Inputs:** Short hop (usually backward or in place), fair near the top of the hop, land,
  then dash back / dash in / grab / ftilt.
- **Timing:** Fair hits frames 5-7 and auto-cancels from frame 11 of the aerial [fd]. On
  shield a full-power fair gives 7 frames of shieldstun, so both a perfect auto-cancel fair
  and a lowest-possible L-cancelled fair are about -1 [web:docs.google.com Collection of Sheik
  Stuff, lib:Sheik Shield Pressure]. Her earliest [fast fall](../techniques/fast-fall.md) is
  frame 19 of the short hop; holding down from frame 16 buffers it [lib:Sheik Shield
  Pressure].
- **Used for:** Walling approaches, then using the landing as a reaction point (dash back, see
  whether they take space, dash back in) [lib:Things Sheik Players Aren't Doing]; pressure on
  shield followed by dash away before a shield grab or dash through at point blank
  [lib:Sheik Shield Pressure].
- **Common errors:** Jumping at a range where an immediate approach hits her before the fair
  is spaced; fair too late (no auto-cancel and missed L-cancel = 16 frames of lag [fd]).
- **Drill idea:** CPU shields then shield grabs as early as possible; success if Sheik's fair
  hits shield and she is out of grab range or behind the CPU when the grab comes out.

### Forward tilt into forward air

- **id:** `ftilt-fair`
- **What:** Ftilt launches straight up with low knockback; it links into itself, up air, or a
  finishing fair.
- **Inputs:** Ftilt (walk or pivot to space it), then full hop or short hop fair as they rise;
  at lower percent ftilt → ftilt or ftilt → regrab first.
- **Timing:** Ftilt hits frames 5-10 and is interruptible from frame 27; 7%, 74° launch,
  knockback growth 100 [fd]. It only starts a combo once it knocks down: on Fox that is 24%
  when fresh (27% fully stale), and Fox can crouch cancel it without tumbling until 80%
  (83% stale) [web:docs.google.com Collection of Sheik Stuff].
- **Used for:** The standard kill/edgeguard setup on fastfallers; also used between down
  throws to reposition them for a regrab [wiki:Sheik_(SSBM)/Forward_tilt].
- **Common errors:** Ftilt below the knockdown percent (victim shines or grabs her); fair too
  late (victim DIs away and escapes); ftilt on a crouching opponent.
- **Drill idea:** CPU Fox stands at 30-80% and DIs the ftilt randomly; success if fair connects
  before he can jump or air dodge.

### Jab reset on missed tech

- **id:** `jab-reset`
- **What:** Hitting a downed opponent with jab (or needles) so they are forced to stand up in
  place, which guarantees a grab or smash. See [jab reset](../techniques/jab-reset.md).
- **Inputs:** Time jab to hit as they land from down throw without teching; then grab during
  the forced get-up. If they teched instead, react and tech chase as normal.
- **Timing:** Jab hits on frame 2 [fd]. Whether the victim is limited to a plain stand
  depends on post-hit percent: below the listed value they must stand; at or above it they can
  also roll or get-up attack. For Sheik's jab and needles: Fox 36%, Falco 37%, Captain Falcon
  42%, Marth/Peach/Sheik 39%, Jigglypuff 33% (full list in the source). Fastfallers who hold up
  land on their feet instead once they are at: Fox 71%, Falco 43%, Captain Falcon 33%, Sheik
  25%, Roy 20% (percent after the jab) [web:docs.google.com Collection of Sheik Stuff].
- **Used for:** Covering missed tech in the down throw tech chase without giving up coverage of
  the techs: a jab timed for the landing still allows a reaction regrab on every tech from
  Falcon [web:docs.google.com Collection of Sheik Stuff].
- **Common errors:** Jab too early (whiffs, they tech behind her); two jabs (launches them);
  opponent SDIs the jab upward to land standing.
- **Drill idea:** CPU Falcon down thrown at 0-25%, misses tech 50% of the time; success if jab
  hits the missed tech and the next grab connects, and techs are still regrabbed.

### Shino stall and Sami stall

- **id:** `shino-stall`
- **What:** Fully intangible ledge stalls using up B (Vanish). Shino stall regrabs the ledge
  after the explosion; Sami stall (also "Sung stall" or "no-poof stall") regrabs before the
  explosion hitbox appears [wiki:Ledgestall].
- **Inputs:** From the ledge: drop (away or down), immediately up B, hold toward/down so she
  re-grabs the ledge. For the no-poof version: drop with fast fall and input up B in a 2-frame
  window so the ledge is grabbed on frame 19 or 20 of up B [lib:Sheik Ledgedash Specifics].
- **Timing:** Vanish is intangible on frames 18-55 and its explosion hitbox is frames 36-42
  [wiki:Sheik_(SSBM)/Up_special]. The Shino stall's explosion protects the ledge but the cycle
  is slow enough that an opponent can grab the ledge mid-cycle; the Sami stall is faster and
  has no hitbox (useful when a hit would save a helpless opponent) [wiki:Ledgestall].
- **Used for:** Holding the ledge during edgeguards, waiting out an opponent, and setting up
  the best ledgedash (see next).
- **Common errors:** Up B too late (she teleports onto the stage or dies); opponent steals the
  ledge during a Shino stall.
- **Drill idea:** Count consecutive stalls with zero vulnerable frames; variant where a CPU
  tries to take the ledge at a random time.

### Ledgedash

- **id:** `sheik-ledgedash`
- **What:** Drop from ledge, jump, waveland onto the stage with ledge intangibility left
  over. See [ledgedash](../techniques/ledgedash.md).
- **Inputs:** (1) Grab the ledge from a no-poof stall. (2) Drop without fast-falling. (3) Jump
  immediately. (4) Hold toward the stage from at least the second jump frame. (5) Air dodge
  onto the stage at 45-60° from straight down [lib:Sheik Ledgedash Specifics].
- **Timing:** This method gives 11 frames of grounded actionable ledge intangibility ("galint"),
  9 if the air dodge is one frame late. 12 is possible with a harder method and 13 only on
  Battlefield. Her up air "interrupt" from the ledge gives 8 [lib:Sheik Ledgedash Specifics].
- **Used for:** Getting off the ledge with an intangible ftilt, grab, dsmash or fair.
- **Common errors:** Fast-falling the drop (she air dodges into the stage wall and dies);
  waveland angle too steep (misses the stage) or too shallow (one extra airborne frame).
- **Drill idea:** Measure intangible actionable frames on landing; success at 9 or more.

### Vanish recovery mixups

- **id:** `vanish-recovery`
- **What:** Choosing where and when up B reappears: sweetspot the ledge, land on stage, land
  on a platform, shorten it, or edge-cancel the landing (slide off a platform or stage edge to
  skip the landing lag).
- **Inputs:** Up B, then hold a direction before she disappears; a half-tilt shortens the
  travel [unverified]. Aim at the ledge from below/outside so she snaps to it.
- **Timing:** Intangible frames 18-55 of 94; landing lag 30 frames if she lands in the
  pre-free-fall part [wiki:Sheik_(SSBM)/Up_special]. Landing on stage with specific timing can
  make the explosion hit twice ("double poof") [wiki:Sheik_(SSBM)].
- **Used for:** Getting back when fair/bair/double jump alone cannot; the explosion (12%) can
  hit an edgeguarder who stands too close [wiki:Sheik_(SSBM)].
- **Common errors:** Reappearing above the ledge with no ledge grab (she is locked in drift and
  punished); aiming at an occupied ledge.
- **Drill idea:** Sheik starts offstage; CPU either holds the ledge or waits on stage; success
  if Sheik ends on the ledge or actionable on stage unpunished.

### Transform recovery

- **id:** `transform-recovery`
- **What:** Using down B offstage to become [Zelda](zelda.md), whose up B travels much further,
  then transforming back on stage.
- **Inputs:** Offstage and high enough: down B; then, as Zelda, drift toward the stage and up B
  (Farore's Wind) to the ledge or stage; down B again once safe.
- **Timing:** Sheik → Zelda: intangible frames 27-36, the swap happens on frame 37, 62 frames
  total. Zelda → Sheik: intangible 34-43, swap on frame 44, 69 total
  [wiki:Sheik_(SSBM)/Down_special, wiki:Zelda_(SSBM)/Down_special].
- **Used for:** Only when Vanish cannot reach [wiki:Sheik_(SSBM)]. Stored needles also survive
  a stock if she transforms before dying and transforms back later [wiki:Needle_Storm].
- **Common errors:** Transforming too low (62 frames of falling); being forced to fight as
  Zelda because the opponent denies the transform back.
- **Drill idea:** Start far offstage and high; success if she returns as Zelda and completes
  the transform back without being hit.

## Neutral game

- **Stance:** defensive and reactive first. Her offence is only as strong as her defence:
  establish a zone with retreating auto-cancel fair, then take space when the opponent
  respects it [lib:Things Sheik Players Aren't Doing].
- **Range ladder:** ftilt / grab / fair up close → short-hop needles outside that → dash attack
  and boost grab beyond that → platform or full-hop needles against retreat
  [lib:Things Sheik Players Aren't Doing].
- **Grab** is the goal against almost everyone: "Fair into grab. Needles into grab. Anything
  into grab" (versus Peach) [web:docs.google.com Collection of Sheik Stuff].
- **Dash attack:** frame 6, launches up and behind, starts juggles [fd, wiki:Sheik_(SSBM)].
  Unsafe on shield and on crouch cancel at low percent.
- **Bair:** frame 4, long reach; a low weak bair then dash away is very hard to punish
  directly; it beats Fox's legs on platforms [web:docs.google.com Collection of Sheik Stuff].
- **Wavedash back** creates reaction windows against close-range Fox and others; her dash
  dance is too short to play a Marth-style dash dance game
  [web:docs.google.com Collection of Sheik Stuff, wiki:Sheik_(SSBM)].
- **Low percent problem:** below the knockdown thresholds her tilts and aerials lose to crouch
  cancel. Against Fox, roughly the first 30% of his stock is hard without a grab
  [web:docs.google.com Collection of Sheik Stuff].
- **Needles on the ground:** needles stuck in the floor still have a hitbox; an attack that
  touches them takes hitlag and becomes punishable [wiki:Sheik_(SSBM)].

## Punish game

Everything routes through down throw or an upward launcher (ftilt, dash attack, utilt, dair)
into aerials, ending in fair or bair offstage. Up smash's sweetspot (17%, frame 12 only,
base 50 growth 105 [fd]) kills off a throw on the right DI. Back throw puts fastfallers
offstage for an edgeguard [wiki:Sheik_(SSBM)].

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| dthrow | Fox, Falco, Captain Falcon | 0% until launchers knock down | reaction tech chase regrab | every option coverable on reaction | [lib:Things Sheik Players Aren't Doing] |
| dthrow | Bowser, Ganondorf, Link, G&W, Ness, Pichu, Pikachu, Roy, Sheik, Yoshi, Young Link | 0 to as high as 90% | regrab (chain grab) | NTSC only | [wiki:Sheik_(SSBM)/Down_throw] |
| dthrow | Marth, DI away | to about 80% | regrab; dash attack if a platform would break it | then fair when it stops | [lib:Doing Bad Stuff To Marth 101] |
| dthrow | Marth, no DI / behind | low percent | utilt (turn first on DI behind) → utilt / regrab / fair / uair | rising full-jump uair from about 20% post-throw | [lib:Doing Bad Stuff To Marth 101] |
| grab at 65% + 2 pummels + dthrow | Marth | 78% before the up smash | sweetspot up smash (behind: in place; no DI / slight away: dash JC up smash) | kills on FD with survival DI; DI away gets regrab → dthrow → fair at the edge | [lib:Doing Bad Stuff To Marth 101] |
| dthrow | Peach, DI away | about 20-30% (estimate) | regrab | true only from the higher port; else 1 frame to escape | [lib:Sheik on Peach Action] |
| dthrow | Peach, no DI / behind | low percent | utilt (turn first on behind), then up airs | up smash never true combos on Peach | [lib:Sheik on Peach Action] |
| dthrow | Samus | any | up air, repeat | "never let her come down" | [web:docs.google.com Collection of Sheik Stuff] |
| dthrow | Dr. Mario | to about 20% then | utilt → uair; uairs after about 20%; chain grab on DI away at low percent (0-30%, source unsure) | fair to send offstage | [web:docs.google.com Collection of Sheik Stuff] |
| dthrow | floaties (Marth, Peach, Jigglypuff) | KO percent | fair or up air | the NTSC kill setup; percent not given | [wiki:Sheik_(SSBM)] |
| ftilt | Fox | from 24% (fresh) | ftilt / uair / fair | below that he does not tumble | [web:docs.google.com Collection of Sheik Stuff] |
| dash attack (clean) | Fox | from 20% (fresh) | up air, fair | CC stops working at 61% | [web:docs.google.com Collection of Sheik Stuff] |
| falling needles | any grounded | any | grab | not always a true combo | [wiki:Sheik_(SSBM)], [lib:Things Sheik Players Aren't Doing] |
| dair | most | mid percent | uair / bair / fair / sweetspot up smash | dair hits frames 15-33 | [wiki:Sheik_(SSBM)], [fd] |
| utilt | large heavies (Bowser) | low-mid | utilt chains, ftilt | | [wiki:Sheik_(SSBM)] |
| uthrow | Fox, Falco | high percent | regrab | per the character page; rarely used | [wiki:Sheik_(SSBM)] |
| bthrow | fastfallers near ledge | any | edgeguard (fair, bair, needles, ledge grab) | | [wiki:Sheik_(SSBM)] |

Knockdown (tumble) thresholds on Fox, percent before the hit, NTSC, fresh / fully stale; the
second pair is the percent at which a crouch-cancelling Fox is knocked down
[web:docs.google.com Collection of Sheik Stuff]:

| Sheik move | Knockdown fresh / stale | Knockdown through crouch cancel fresh / stale |
|-|-|-|
| Dash attack (clean) | 20% / 24% | 61% / 66% |
| Ftilt | 24% / 27% | 80% / 83% |
| Utilt hit 1 | 43% / 47% | 85% / 88% |
| Dtilt | 40% / 44% | 103% / 106% |
| Fsmash hit 2 | 16% / 21% | 76% / 80% |
| Up smash (weak) | 7% / 13% | 41% / 47% |
| Dsmash hit 1 | 19% / 25% | 61% / 67% |
| Nair (clean) | 35% / 41% | 66% / 72% |
| Fair | 39% / 45% | 72% / 78% |
| Bair (clean) | 26% / 32% | 57% / 63% |
| Uair (clean) | 21% / 26% | 51% / 56% |

### Chain grabs and tech chases

- **How NTSC down throw behaves by victim class.** The throw is 5% (hit) + 3% (throw), 80°,
  base knockback 70, growth 50, and its speed does not depend on weight
  [wiki:Sheik_(SSBM)/Down_throw]. What happens next depends on how fast the victim falls:
  - *Fastfallers (Fox, Falco, Captain Falcon):* they hit the ground before hitstun ends and
    must tech or miss. Sheik reaction tech chases. This lasts from 0% until ftilt/dash attack
    knock down (about 20-25% on Fox) and remains available later as a mixup.
  - *Chain-grab class (Bowser, Ganondorf, Link, Mr. Game & Watch, Ness, Pichu, Pikachu, Roy,
    Sheik, Yoshi, Young Link):* they stay airborne but cannot act or jump before the regrab;
    0 to as high as 90% with poor DI [wiki:Sheik_(SSBM)/Down_throw, wiki:Chain_grab].
  - *Mid-weights and floaties:* regrab only on DI away (Marth to about 80%; Peach about
    20-30%, port dependent); otherwise utilt / up air juggles, and fair or up air at kill
    percent [lib:Doing Bad Stuff To Marth 101, lib:Sheik on Peach Action]. Sourced for Marth,
    Peach, Samus and Dr. Mario; Mario, Luigi, Jigglypuff, Ice Climbers and Zelda are assumed
    to behave the same way because they are not on the chain-grab list [unverified].
- **Escapes.** Fastfallers: tech in place into shine (Fox/Falco) if Sheik is late; DI away
  plus tech away with full stage (requires boost grab); landing on a platform or going
  offstage; not teching and SDI-ing the jab upward. Falcon: from about 18-20% before the throw,
  DI the jab up and toward with C-stick up to land on his feet
  [web:docs.google.com Collection of Sheik Stuff]. Floaties: Peach can double jump out with
  correct timing, or nair out when Sheik mis-times [lib:Sheik on Peach Action]; Marth's
  slightest-away DI cannot be regrabbed (utilt instead) [lib:Doing Bad Stuff To Marth 101].
- **Sheik is hard to tech chase herself:** her tech in place and tech toward look identical
  until too late to react [wiki:Tech-chase].
- **Platform tech chase:** waveland onto the platform and regrab everything, or short hop under
  it and react (aerial on tech in place, double-jump waveland grab on a roll). At higher
  percent: down throw → full jump → auto-cancel fair on tech in place / missed tech → grab the
  tech roll [lib:Doing Bad Stuff To Marth 101].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| fair | any offstage | mid percent as an edgeguard; percent not sourced | 13%, 25° semi-spike, growth 100 | [fd], [wiki:Sheik_(SSBM)/Forward_aerial] |
| up smash (sweetspot) | Marth | 78% before the hit on Final Destination, with survival DI | frame 12 hitbox at the hands, 17% | [lib:Doing Bad Stuff To Marth 101] |
| up smash (sweetspot) | Peach | "very low" percent if she does not jump out of dthrow | not a true combo on Peach | [lib:Sheik on Peach Action] |
| up air (clean) | floaties | high percent, earlier near the top | 12%, 80°, growth 120; NTSC only (PAL weakened) | [fd], [wiki:Sheik_(SSBM)] |
| bair (clean, foot) | any | very high percent outright; earlier offstage | 14% | [wiki:Sheik_(SSBM)] |
| up B explosion | any | around 120% | 12%, hitbox frames 36-42 | [wiki:Vanish], [wiki:Sheik_(SSBM)/Up_special] |
| nair (clean) | any offstage | gimp tool rather than a raw KO move | 14% clean, lasts to frame 30 | [fd], [wiki:Sheik_(SSBM)/Neutral_aerial] |
| dthrow → fair at ledge | Marth | once DI away has carried him to the edge | guaranteed edgeguard | [lib:Doing Bad Stuff To Marth 101] |
| fair out of float/double jump | Peach | about 80%, sends offstage | "probably a guaranteed kill" | [lib:Sheik on Peach Action] |

- **Edgeguard flow:** hit them offstage with fair or back throw; then (a) needles from the
  stage or air to knock them out of double jump or a charging up B, (b) grab the ledge and
  ledge-hop bair/fair, (c) drop-zone fair/bair/nair for low recoveries, (d) hold the ledge
  with an intangible stall so they must land on stage, then punish the landing.
- **Needles in edgeguards:** high hitstun and low knockback make them ideal for stopping linear
  recoveries such as Fox's up B; they also cancel projectiles that cover recoveries (Samus)
  [wiki:Sheik_(SSBM)].
- **Fair gimps** characters with poor recoveries (Falco, Dr. Mario) at low percent
  [wiki:Sheik_(SSBM)/Forward_aerial].
- **Fair is less useful the higher the victim is:** keep them low when choosing the last hit
  of a combo [lib:Doing Bad Stuff To Marth 101].

## Recovery

- **Options:** double jump (height 38, third highest [wiki:Sheik_(SSBM)]); fair/bair/nair to
  hit edgeguarders; air dodge; up B (Vanish: intangible frames 18-55, explosion hitbox frames
  36-42, short travel, no hitbox on reappearance, 30 frames of landing lag
  [wiki:Sheik_(SSBM)/Up_special]); wall jump (short, stage dependent) [wiki:Sheik_(SSBM)];
  Transform into Zelda for a longer up B.
- **Mixups:** up B to ledge versus onto stage versus onto a platform; shortened or angled
  Vanish; edge-cancelled Vanish landings (the "Hoodie Ninja edge cancels" card); double poof;
  saving the double jump and drifting in with an aerial; reverse needle cancel to snap to the
  ledge [wiki:Needle_Storm]; upward DI then Transform so Zelda can drift back
  [wiki:Sheik_(SSBM)].
- **Weaknesses:** if the ledge is held she must land on stage in lag; after Vanish she cannot
  drift; low air speed means a hit that sends her far and low usually kills; Transform is slow.

### Edgeguarding Sheik

- **Hold the ledge.** Grab it before she vanishes. Stand up from the ledge (not roll or
  attack) right after the "poof" so the ledge stays occupied through her sweetspot window,
  then punish her landing lag on stage [lib:Marth vs. Sheik Guide].
- **Threaten the double jump.** If she can double jump and up B comfortably, go out and hit
  her as she jumps (Marth: wavedash off stage, bair, then up B back) so she has to change
  trajectory [lib:Marth vs. Sheik Guide].
- **Punish the landing.** Vanish onto stage gives 30 frames of landing lag
  [wiki:Sheik_(SSBM)/Up_special]: fsmash, Rest, grab, knee.
- **Respect the explosion** (frames 36-42, 12%) if standing at the lip, and her aerials if
  chasing her while she still has a jump.
- **Zelda:** if she transforms, edgeguard Farore's Wind instead (see [Zelda](zelda.md)) and
  deny the transform back.
- A CPU Sheik should mix: (a) double jump fair/bair at the edgeguarder, (b) low up B to ledge,
  (c) up B to stage or platform when the ledge is taken, (d) drift in high and air dodge.

## Defense and out of shield

- **Out of shield:** nair (frame 3 after a 3-frame jump squat [fd, wiki:Sheik_(SSBM)]) is the
  default; shield grab (frame 7); wavedash OoS (3 jump squat + 10 landing = 13 frames, so
  wavedash → grab takes 20 frames [web:docs.google.com Collection of Sheik Stuff]); jump away;
  [shield drop](../techniques/shield-drop.md) on platforms. Versus Fox, nair OoS beats shine
  pressure once his shine is staled even once
  [web:docs.google.com Collection of Sheik Stuff].
- **Crouch cancel / ASDI down:** very strong. She is heavy and can answer from crouch with
  frame-5 tilts and down smash or a grab; "Crouch cancel his moves! Any aerial that he doesn't
  tipper can be CCed" (versus Marth) [web:docs.google.com Collection of Sheik Stuff].
- **Down smash:** frame 5 with leg intangibility on the first active frame; a "get off me"
  move [wiki:Sheik_(SSBM)]. Punishable on shield by wavedash grab unless all three hits land
  on shield [lib:Sheik Shield Pressure].
- **Combo escapes:** nair (frame 3) or double jump; DI. She has little that protects her from
  below, so she is juggled by Marth, Falco, Jigglypuff and Fox [wiki:Sheik_(SSBM)].
- **What beats her:** grabs through her shield, pinning her on a platform (tilt shield down
  and leave quickly: wavedash OoS, shield drop, or jump
  [web:docs.google.com Collection of Sheik Stuff]), baiting the long short hop, and punishing
  jab/ftilt/utilt on shield (jab is shield-grabbable unless spaced at max range; utilt is
  shield-grabbable between hits) [lib:Sheik Shield Pressure].

## As the training dummy

- **Class:** weight 90, fall speed 2.13 (fast fall 3.0), gravity 0.12, air speed 0.8, jump
  squat 3 frames [wiki:Sheik_(SSBM)]. Heavy for her size and a semi-fastfaller.
- **Chain grabbed by:** Sheik's own down throw (0 to as high as 90%)
  [wiki:Sheik_(SSBM)/Down_throw]; Ice Climbers (Popo alone can down throw chain her to about
  50%); Mewtwo's down throw (DI dependent) [wiki:Chain_grab]; Marth forward throw → regrab at
  0%, escaped by DI down and away [lib:Marth vs. Sheik Guide].
- **Marth up throw:** utilt follows at roughly 18-25%; otherwise he baits her double jump and
  juggles with up air and fair. Her best answer is DI up and away and saving the jump
  [lib:Marth vs. Sheik Guide, lib:Marth Guide].
- **Tech chase:** tech in place and tech toward the chaser are indistinguishable until too
  late to react, so a realistic CPU Sheik should favour those two [wiki:Tech-chase].
- **Jab reset thresholds:** forced plain stand below 39% post-hit; she lands on her feet from a
  jab if she holds up at 25% or more post-hit [web:docs.google.com Collection of Sheik Stuff].
- **Crouch cancel:** a realistic CPU Sheik crouches at low percent and answers with grab,
  dtilt or dsmash.
- **Recovery behaviour:** see "Edgeguarding Sheik".
- **Common punish on her:** Fox up throw → up air; Jigglypuff Rest on her landing lag and
  recovery [wiki:Sheik_(SSBM)]; Marth grab → tech chase to the ledge.

## Matchup notes

### vs Fox

- Hard for both. Fox baits and out-manoeuvres her; she has an answer to everything and kills
  him early once she gets a grab [web:docs.google.com Collection of Sheik Stuff]. Jmook's
  consistent reaction tech chasing moved opinion toward Sheik [wiki:Sheik_(SSBM)].
- First 20-30% of Fox's stock: her hits do not knock down and trades favour Fox. Use needles
  to bring him to 24% (ftilt knockdown), fair/bair spaced against crouch cancel, and grab.
- Fox avoids grab by playing platforms; answer with bair and counter-baits rather than chasing.
- Sheik's shield and crouch are strong against Fox's pressure; nair OoS and crouch-cancel grab.

### vs Falco

- Lasers disrupt her spacing but Falco dies to one fair offstage. Reaction tech chase off down
  throw; back throw to edgeguard. Falco pillars her because she falls fast.

### vs Marth

- Sheik wants grab (down throw tree above) and to edgeguard him; Marth wants to stay grounded,
  dtilt, and dash dance grab her [lib:Marth vs. Sheik Guide].
- Move a lot so he cannot set up fair/nair spacing; dash attack goes under high nairs;
  crouch cancel non-tipper aerials; spot dodge only on reaction, since his moves are single
  short hits with lag [web:docs.google.com Collection of Sheik Stuff].
- Jab pressure does not work: he grabs it [lib:Marth vs. Sheik Guide].

### vs Jigglypuff

- Considered her worst matchup: Rest kills her at very low percent off her laggy recovery and
  whiffs [wiki:Sheik_(SSBM)]. She cannot chain grab Puff; kills come from fair/bair walls and
  up air.

### vs Peach

- Grab as much as possible; weak ground moves lose to her crouch cancel down smash and float
  nair OoS. Needles deny turnip pulls on the same plane. Shield DI away from down smash, then
  wavedash OoS grab [web:docs.google.com Collection of Sheik Stuff].
- Down throw tree: [lib:Sheik on Peach Action].

### vs Captain Falcon

- Reaction tech chase off down throw from 0%, with jab covering missed tech. Falcon's
  get-up attack can be crouch-cancel grabbed until over 100%
  [web:docs.google.com Collection of Sheik Stuff]. Her ground game beats his; he combos and
  kills her off stray hits.

### vs Ice Climbers

- A historically bad matchup while wobbling was legal [wiki:Sheik_(SSBM)]. Separate them and
  avoid being grabbed; Popo alone can still chain grab her [wiki:Chain_grab].

## Drill seeds

### Reaction tech chase on Fox

- **id:** `sheik-techchase-fox`
- **Goal:** Regrab every tech option after down throw by reaction.
- **Player:** Sheik
- **CPU:** Fox (variants: Falco, Captain Falcon)
- **Setup:** Final Destination, center. Sheik holds Fox in grab at 0-20%.
- **CPU behaviour:** Random throw DI {away, in front, behind, slight}; random tech {in place,
  toward, away, missed}. After tech in place it shines on the first actionable frame; after a
  roll it jumps away; after a missed tech it picks a random get-up.
- **Success:** Grab connects before the CPU's first actionable frame (tech in place: grab
  input no later than frame 19 of the 26-frame tech). Score a streak.
- **Fail:** CPU acts (shine connects, or it escapes), or Sheik whiffs.
- **Variations:** Show a frame counter and grade the decision frame (target 18-19); Falcon
  with jab on landing; restrict to one DI; continue until Fox reaches 24% then require
  ftilt → fair.
- **Data needed:** dthrow release frame 36 and launch (80°, base 70, growth 50), Fox
  weight/gravity/fall speed, tech-in-place 26 and tech-roll 40 frame durations and roll
  distances, Sheik grab frame 7, shine frame 1.

### Down throw DI tree on Marth

- **id:** `sheik-dthrow-marth-di`
- **Goal:** Pick the right follow-up for each DI on a non-fastfaller.
- **Player:** Sheik
- **CPU:** Marth (variants: Peach, Dr. Mario, Samus)
- **Setup:** FD, no platforms, Marth in grab at 0-60%.
- **CPU behaviour:** Random DI {full away, slight away (45° notch), none, behind}; jumps or
  fairs on its first actionable frame.
- **Success:** Regrab on away DIs (while in range), utilt both hits or up air on none/behind,
  each landing before Marth acts.
- **Fail:** Marth escapes or hits Sheik; wrong-facing utilt that drops the second hit.
- **Variations:** Kill version: grab at 65%, two pummels, down throw, sweetspot up smash on
  behind/none/slight-away DI (78% pre-hit kills on FD); platform stage where DI away lands
  him on a platform.
- **Data needed:** percent bands from [lib:Doing Bad Stuff To Marth 101]; utilt hit frames
  5-10 and 19-24, IASA 26; up smash frame 12; Marth weight 87 and fall speed 2.2.

### Chain grab count

- **id:** `sheik-dthrow-chaingrab`
- **Goal:** Hold a full down throw chain grab against DI.
- **Player:** Sheik
- **CPU:** Link, Pikachu, Sheik, Ganondorf, Roy, Yoshi, Bowser, Young Link, Ness, Mr. Game &
  Watch, Pichu
- **Setup:** FD, center, CPU in grab at 0%.
- **CPU behaviour:** Random DI each throw (away / behind / none); jumps or attacks on the
  first actionable frame.
- **Success:** Regrabs continue until a target percent (default 60%), then a finisher (up
  smash or fair) connects.
- **Fail:** CPU acts between throws.
- **Variations:** Start near the ledge (must turn the chain around); higher-port vs
  lower-port.
- **Data needed:** which characters are chain-grabbable [wiki:Sheik_(SSBM)/Down_throw]; exact
  end percents per character are not sourced and should be measured.

### Falling needles into grab

- **id:** `sheik-needle-grab`
- **Goal:** Convert aerial needles into a grab with no landing lag.
- **Player:** Sheik
- **CPU:** Fox, Peach, Marth
- **Setup:** Sheik at mid range with 6 needles stored (variant: 2-3).
- **CPU behaviour:** Randomly shields, crouches, or dash dances just outside ftilt range.
- **Success:** At least one needle hits (or hits shield) and Sheik's grab connects within
  about 10 frames of her landing.
- **Fail:** Needles thrown on the way up (full aerial lag), needles miss, or the CPU acts
  before the grab.
- **Variations:** CPU on a platform (full-hop needles); CPU approaches so Sheik must retreat
  first; reverse needle cancel to store without lag.
- **Data needed:** needle speed, angle (45° in the air) and hitstun; Sheik short hop height
  20.16 and landing lag 4 [wiki:Sheik_(SSBM)]; needle-cancel height condition
  [wiki:Needle_Storm].

### Ftilt to fair finisher

- **id:** `sheik-ftilt-fair`
- **Goal:** Confirm ftilt into fair at knockdown percent.
- **Player:** Sheik
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** CPU standing near the ledge at 30-80%, facing Sheik, Sheik in ftilt range.
- **CPU behaviour:** Randomly crouch cancels or not; DIs ftilt randomly; jumps on the first
  actionable frame.
- **Success:** Fair connects after ftilt before the CPU acts and sends it offstage.
- **Fail:** Ftilt is crouch cancelled and Sheik is hit; fair whiffs.
- **Variations:** Below 24% the correct answer is grab, not ftilt; add the edgeguard after the
  fair as a second stage.
- **Data needed:** knockdown table above; ftilt IASA 27; fair frame 5; Fox double jump and
  air dodge timing out of hitstun.

### Edgeguard Fox with needles and fair

- **id:** `sheik-edgeguard-fox`
- **Goal:** Cover a spacie recovery from stage and ledge.
- **Player:** Sheik
- **CPU:** Fox, Falco
- **Setup:** Fox offstage in tumble at 40-90% at a random height; Sheik at the ledge with 0-6
  needles.
- **CPU behaviour:** Random: side B to ledge / onto stage / shortened; up B at random angles;
  double jump air dodge; wall tech if hit into the stage.
- **Success:** Fox loses the stock; Sheik takes no hit.
- **Fail:** Fox returns to an actionable state on stage or ledge.
- **Variations:** No needles; must use ledge-hop bair; must hold the ledge with a stall and
  punish the landing.
- **Data needed:** Fox up B start-up and distance, side B distance; needle travel; fair/bair
  hitbox reach; ledge intangibility.

### Fair on shield, then leave

- **id:** `sheik-fair-shield-pressure`
- **Goal:** Hit a shield with a low fair and avoid the shield grab.
- **Player:** Sheik
- **CPU:** Marth, Fox, Peach
- **Setup:** CPU in shield, Sheik a short hop away.
- **CPU behaviour:** Shield grabs on the earliest frame after shieldstun; variants: nair OoS,
  up smash OoS (Fox), roll.
- **Success:** Fair hits the shield; Sheik is not grabbed or hit; she ends outside grab range,
  behind the CPU, or grabs the CPU's whiff.
- **Fail:** Sheik is grabbed or hit.
- **Variations:** Auto-cancel timing vs lowest L-cancel timing; point-blank (dash through)
  vs spaced (dash back).
- **Data needed:** fair shieldstun 7 frames and -1 advantage, short hop fast-fall frame 19
  [lib:Sheik Shield Pressure]; CPU grab ranges; shieldstun formula.

### Intangible ledge stall into ledgedash

- **id:** `sheik-stall-ledgedash`
- **Goal:** Stall without a vulnerable frame, then ledgedash with 9 or more intangible frames.
- **Player:** Sheik
- **CPU:** any (optional)
- **Setup:** Sheik on the ledge of Battlefield or FD.
- **CPU behaviour:** Optional: stands near the ledge and attacks at a random time, or tries to
  take the ledge.
- **Success:** K stalls with no vulnerable frame, then a ledgedash with at least 9 frames of
  grounded actionable intangibility (11 is the consistent maximum).
- **Fail:** Any vulnerable frame, a missed ledge regrab, or an SD.
- **Variations:** No-poof (Sami) stall only; act out of the ledgedash with an intangible
  ftilt/grab that must hit the CPU.
- **Data needed:** Vanish intangibility 18-55; ledge grab frames 19-20 of up B for the
  no-poof stall; ledge intangibility length [lib:Sheik Ledgedash Specifics].

### Recover against a ledge holder

- **id:** `sheik-recovery-mixup`
- **Goal:** Choose a Vanish destination the edgeguarder is not covering.
- **Player:** Sheik
- **CPU:** Marth, Fox, Sheik, Jigglypuff
- **Setup:** Sheik offstage at a random recoverable position, double jump random.
- **CPU behaviour:** Random: holds the ledge then stands up after the poof; waits on stage to
  punish a stage landing; jumps out to hit the double jump.
- **Success:** Sheik is actionable on stage/platform/ledge without being hit.
- **Fail:** KO or punished landing.
- **Variations:** Battlefield/Yoshi's (platform landings, edge cancels); allow Transform as a
  solution when placed too far for Vanish.
- **Data needed:** Vanish travel distance and landing lag 30; platform positions; Transform
  timing (swap on frame 37 of 62).

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlSk.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/sheik.json`](../framedata/sheik.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 2-3 | 4 | 70 | 0 | 100 | - | slash | 17 | 16 | 3 | -10 |  |
| Jab 2 | `jab2` | 3-5 | 3 | 70 | 0 | 100 | - | slash | 18 | 17 | 3 | -10 | starts 1 frame late (included) |
| Rapid jab start | `rapid_jab_start` | - | - | - | - | - | - | - | 6 | - | - | - |  |
| Rapid jab loop | `rapid_jab_loop` | 2-3, 8-9, 14-15, 20-21, 26-27, 32-33 | 1 | 80 | 10 | 80 | - |  | 35 | - | 2 | -31 |  |
| Rapid jab end | `rapid_jab_end` | - | - | - | - | - | - | - | 8 | - | - | - |  |
| Dash attack | `dash_attack` | 6 | 10 | 80 | 34 | 100 | - | slash | 37 | 36 | 6 | -23 |  |
|  |  | 7-12 | 7 | Sakurai | 15 | 100 | - |  |  |  | 5 | -23 |  |
| Up tilt | `utilt` | 5-10 | 8 | 80 | 10 | 120 | - |  | 33 | 26 | 5 | -15 |  |
|  |  | 19-24 | 4 | 80 | 10 | 140 | - |  |  |  | 3 | -3 |  |
| Down tilt | `dtilt` | 5-8 | 8 | 70/90 | 35 | 80 | - |  | 29 | 28 | 5 | -17 |  |
| Forward smash | `fsmash` | 12 | 5 | 78/70 | 0 | 100 | 60 |  | 50 | 46 | 4 | -29 | charge hold frame 5 |
|  |  | 27-29 | 10 | Sakurai | 50 | 70 | - |  |  |  | 6 | -12 |  |
| Up smash | `usmash` | 12 | 17 | 90 | 50 | 105 | - | slash | 47 | 40 | 9 | -18 | charge hold frame 10; partly intangible 12-16 (3 bones) |
|  |  | 14-16 | 13 | 88/78 | 38 | 100 | - | slash |  |  | 7 | -18 |  |
| Down smash | `dsmash` | 5-9 | 13 | 40 | 35 | 80 | - |  | 49 | 46 | 7 | -33 | charge hold frame 2; partly intangible 5 (4 bones) |
|  |  | 16-19, 22-24 | 10 | 50 | 35 | 80 | - |  |  |  | 6 | -23 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 3-6 | 14/10 | Sakurai | 0 | 100 | - |  | 48 | 42 | 8 | 16 | 8 | <3, >30 | +0 |  |
|  |  | 7-30 | 9 | Sakurai | 0 | 100 | - |  |  |  | 6 |  |  |  | -2 |  |
| Forward air | `fair` | 5-7 | 13 | 25 | 0 | 100 | - |  | 33 | - | 7 | 16 | 8 | <5, >10 | -1 |  |
| Back air | `bair` | 4-7 | 8/10/14 | Sakurai | 0/5/12 | 100 | - |  | 37 | - | 8 | 16 | 8 | <4, >24 | +0 |  |
|  |  | 8-19 | 6/7/9/10 | Sakurai | 0/4/8 | 100 | - |  |  |  | 6 |  |  |  | -2 |  |
| Up air | `uair` | 5-7 | 12 | 80 | 15 | 120 | - |  | 39 | 37 | 7 | 24 | 12 | <5, >29 | -5 |  |
|  |  | 8-20 | 9 | 70 | 10 | 120 | - |  |  |  | 6 |  |  |  | -6 |  |
| Down air | `dair` | 15-33 | 11 | 80 | 30 | 90 | - |  | 48 | - | 6 | 20 | 10 | <3, >48 | -4 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 8-9 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 10 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 8 | 2 | 45 | 40 | 140 | - | - | 24 | 47 |  |
| Back throw | `bthrow` | 7 | 2 | 135 | 40 | 140 | - | - | 20 | 47 |  |
| Up throw | `uthrow` | 8 | 2 | 88 | 90 | 30 | - | - | 23 | 57 |  |
| Down throw | `dthrow` | 8 | 3 | 80 | 70 | 50 | - | - | 36 | 57 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Needle Storm (needles), ground, Start | `special_n_start` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Neutral B: Needle Storm (needles), ground, Loop | `special_n_loop` | - | - | - | - | - | - | - | 17 | - | - | - |  |
| Neutral B: Needle Storm (needles), ground, Cansel | `special_n_cansel` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Neutral B: Needle Storm (needles), ground, End | `special_n_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Neutral B: Needle Storm (needles), air, Start | `special_air_n_start` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Neutral B: Needle Storm (needles), air, Loop | `special_air_n_loop` | - | - | - | - | - | - | - | 17 | - | - | - |  |
| Neutral B: Needle Storm (needles), air, Cansel | `special_air_n_cansel` | - | - | - | - | - | - | - | 7 | - | - | - |  |
| Neutral B: Needle Storm (needles), air, End | `special_air_n_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Side B: Chain, ground, Start | `special_s_start` | 22-24 | 3/5 | Sakurai/60/70/80 | 6/8/14/35 | 30 | - | slash/electric | 24 | - | 4 | - |  |
| Side B: Chain, ground, End | `special_s_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Side B: Chain, ground | `special_s` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Side B: Chain, air, Start | `special_air_s_start` | 22-24 | 3/5 | Sakurai/60/70/80 | 6/8/14/35 | 30 | - | slash/electric | 24 | - | 4 | - |  |
| Side B: Chain, air, End | `special_air_s_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Side B: Chain, air | `special_air_s` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Up B: Vanish, ground, Start | `special_hi_start` | - | - | - | - | - | - | - | 35 | - | - | - | intangible 18-35 |
| Up B: Vanish, ground | `special_hi` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Up B: Vanish, air, Start | `special_air_hi_start` | - | - | - | - | - | - | - | 35 | - | - | - | intangible 18-35 |
| Up B: Vanish, air | `special_air_hi` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Down B: Transform, ground | `special_lw` | - | - | - | - | - | - | - | 36 | - | - | - | intangible 27-36 |
| Down B: Transform, ground, 2 | `special_lw2` | - | - | - | - | - | - | - | 25 | - | - | - |  |
| Down B: Transform, air | `special_air_lw` | - | - | - | - | - | - | - | 36 | - | - | - | intangible 27-36 |
| Down B: Transform, air, 2 | `special_air_lw2` | - | - | - | - | - | - | - | 25 | - | - | - |  |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-15 | - | 22 | - |  |
| Roll forward | `roll_forward` | intangible 4-19 | - | 31 | - |  |
| Roll backward | `roll_backward` | intangible 4-19 | - | 31 | - |  |
| Air dodge | `airdodge` | intangible 4-29 | - | 49 | - |  |

### Techs and getups

Tech and getup-stand intangibility is listed as the script gives it, shifted by the entry delay (so 2-20 where community tables say 1-20).

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Missed tech bounce (face up) | `missed_tech_bounce_faceup` | - | - | 25 | - |  |
| Getup stand (face up) | `getup_stand_faceup` | intangible 2-20 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-26 | 17-19, 24-26 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 1-22 | - | 35 | - |  |
| Missed tech bounce (face down) | `missed_tech_bounce_facedown` | - | - | 25 | - |  |
| Getup stand (face down) | `getup_stand_facedown` | intangible 2-20 | - | 30 | - | starts 1 frame late (included) |
| Getup attack (face down) | `getup_attack_facedown` | intangible 1-21 | 16-17, 20-21 (6%) | 49 | - |  |
| Getup roll forward (face down) | `getup_roll_forward_facedown` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face down) | `getup_roll_backward_facedown` | intangible 1-19 | - | 35 | - |  |
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
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-53 | 57-59 (8/6%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-21 | 25-34 (8%) | 54 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-71 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-39 | - | 49 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-19 | - | 19 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 38 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-14 | - | 14 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 43 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Neutral air | jump | 6 | `nair` |
| Back air | jump | 7 | `bair` |
| Shield grab | direct | 7 | `grab` |
| Forward air | jump | 8 | `fair` |
| Up air | jump | 8 | `uair` |
| Up smash | jump cancel | 13 | `usmash` |
| Down air | jump | 18 | `dair` |
| Spot dodge | direct | intangible 2-15 of 22 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 15 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Sheik indexed by [The Melee Library](https://www.meleelibrary.com/#sheik) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [Hoodie Ninja Edge Cancels](https://www.youtube.com/watch?v=3XYLLRzu7AU) |  | Up-B edge cancels to aid with Sheik's recovery. |
| [2020 Sheik Melee Techs Guide](https://www.youtube.com/watch?v=7qLjcKpwvjA&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=25&t=0s) | Third Chair | Video guide on performing useful Sheik tech in 2020. |
| [Are You a Sheik Main?](https://www.youtube.com/watch?v=-2GI-sN1sAw) | SSBM Tutorials | They give an overview of Sheik the character to give you an idea of whether you would like to play her. |
| [1001 Mew2king Edgeguards (with Sheik)](https://www.youtube.com/watch?v=MBD8au4jQbg) | Ben Burdett | A compilation video of Mew2king edgeguarding with Sheik. I suggest putting on your favorite music or Pandora station and watching these attentively. Get a feel for how Mew2king edgeguards. You can also learn a lot using situational analysis by creating flowcharts of the options Mew2king has and the opponent has and then analyzing the options they choose to do in each situation. |
| [Sheik Q&A Thread](http://smashboards.com/threads/sheik-strategy-qna.129276/) | lots of people | Has lots of stuff in it. It has some matchup guides, character specific frame data, and the thread can probably be searched for answers to questions. |
| [Sheik Matchup Guide Compilation](https://docs.google.com/document/d/12-NQSfi_MQj6brnqEJxS2EvkuWTx6VfVbl5BpNCltfY/edit) | Mucho Man Randy Passion |  |
| [Things Sheik Players Aren’t Doing](https://portraitinsmash.blogspot.com/2015/02/things-sheik-players-arent-doing.html?m=0) | DruggedFox |  |
| [Doing Bad Stuff To Marth 101](https://portraitinsmash.blogspot.com/2015/02/doing-bad-stuff-to-marth-101.html?m=0) | DruggedFox | He means bad for Marth. It is more of a 200 level course. |
| [Sheik Hitboxes and Frame Data](http://smashboards.com/threads/sheik-hitboxes-and-frame-data.299984/) | Stratocaster, Standardtoaster, and SuperDoodleMan | Includes gifs of all of Sheik's moves showing hitboxes and hurtboxes. Also lists frame data on each move. |
| [Sheik Frame Data Visualization](http://imgur.com/a/qzyAu) | Stormchicken |  |
| [Sheik Directory](http://smashboards.com/threads/sheik-directory-guides-videos-misc.350457/) | Xeylode | “Links to useful threads.” |
| [Zero to Hero: Season 1](http://www.meleeitonme.com/zero-to-hero-episodes-1-9/) | Tafokints | A series of videos where Tafokints teaches Sheik to Atrioc. “You may know the techniques, but you may not know how to use them.” There is lots of good fundamental or generalizable information in there, too. |
| [Sheik Grab Game vs. Marth Tutorial (Basics)](https://www.youtube.com/watch?v=YFeGgV0sEIk) | SSBM Tutorials |  |
| [Sheik Grab Game and Techchasing vs. Fox/Falco/Falcon Tutorial](https://www.youtube.com/watch?v=o7l1IWUPznM) | SSBM Tutorials |  |
| [Shino Stall Tutorial](https://www.youtube.com/watch?v=K3DI4Zl6b1E) | SSBM Tutorials |  |
| [Heatmap of Sheik’s Option Out of Shield](http://imgur.com/a/WmHlt#0) | Schmooblidon | What area Sheik can cover out of shield and how fast. |
| [Sheik Melee Chaingrab Guide](https://www.youtube.com/watch?v=mjgVxUUGOyk&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=12&t=0s) | Third Chair |  |
| [Sheik Ditto Chaingrab Tutorial](https://www.youtube.com/watch?v=mgQ7AI9NsAs) | SSBM Tutorials |  |
| [Sheik Ledge Options](https://www.youtube.com/watch?v=wsvz44R4tgs) | Ippo |  |
| [Sheik Needle Canceling](https://www.youtube.com/watch?v=hFTK5t3p2x4) | Ippo |  |
| [Sheik’s Needles Damage Variation Explained](https://www.youtube.com/watch?v=8o2KmpSS7cA) | Bonfire10 |  |
| [Sheik on Peach Action](https://portraitinsmash.blogspot.com/2015/07/sheik-on-peach-action.html?m=0) | DruggedFox | DruggedFox discusses NTSC grab follow-ups on Peach. |
| [Sheik Shield Pressure](https://portraitinsmash.blogspot.com/2015/07/sheik-shield-pressure.html?m=0) | DruggedFox |  |
| [Sheik Neutral Game Tutorial (Part 1)](https://www.youtube.com/watch?v=bq3UuQONpDg) | SSBM Tutorials |  |
| [Sheik’s Invincible Ledgedash Options](https://www.youtube.com/watch?v=IGt6zN2L4ww) | Practical TAS | A video showcasing Sheik’s options she can perform intangibly from a ledgedash. |
| [Tech Chasing!](http://portraitinsmash.blogspot.ca/2015/09/tech-chasing.html) | DruggedFox | DruggedFox explains how he does his [super sick reaction tech chasing](http://www.meleeitonme.com/wp-content/uploads/DeliciousIdioticAbyssiniangroundhornbill.webm?_=2). |
| [Tech Skill Trial Video](https://www.youtube.com/watch?v=BQUYsm2mFUM) | Little England | Essential Sheik tech skill to know. |
| [Sheik Edgeguard Trick](https://www.youtube.com/watch?v=GobMNLBSMR4) | SSBM Tutorials |  |
| [Sheik Trials](https://www.youtube.com/watch?v=WBfAcfPPQyk) | Ripple |  |
| [Sheik Up-B Mechanics](http://smashboards.com/threads/sheik-up-b-mechanics.424253/) | Sycorax |  |
| [Sheik Ledgedash Specifics](http://www.meleeitonme.com/sheik-ledgedash/) | Kadano |  |
| [A Reductive Approach to Sheik with Training Exercises](http://smashboards.com/threads/a-reductive-approach-to-sheik-w-some-training-exercises.427068/) | hologram summer | A guide oriented towards mid-level players. Includes interesting training exercises to help break habits and understand Sheik's gameplan better. |
| [How to Sami Stall with Sheik](https://www.youtube.com/watch?v=01GZwcJfI_o) | SSBM Tutorials |  |
| [Theorycraft: Zelda to Sheik Safe Transformation on FD](https://www.youtube.com/watch?v=Sw-EGhhiwy8) | PewPewU |  |
| [How To Practice Sheik](https://www.youtube.com/watch?v=0alnT4DiOco) | SSBM Tutorials |  |
| [Data on Sheik's Up-B Edge Cancel](https://www.reddit.com/r/SSBM/comments/4xi7z2/daily_discussion_thread_081316/d6g3lqi) | Schmooblidon |  |
| [How to Edgeguard Sheik](https://www.youtube.com/watch?v=820utmlAqnU) | SSBM Tutorials |  |
| [Reverse + Shortened Up-b Recoveries](https://smashboards.com/threads/reverse-shortened-up-b-recoveries-video-included.273278/#post-10146397) | Axe | This technique isn't specific to Sheik, but she makes great use of it. |
| [How to Beat Sheik](https://www.youtube.com/watch?v=0ovbvriy1HY) | SSBM Tutorials |  |
| [Smart Things Said about Sheik](https://drive.google.com/drive/u/0/folders/0B6Vp_R3-rqWsTXduaUdBYk9jb2M) | Raymond Lyday | A collection of things smart people said about playing Sheik. |
| [Super Analysis with RNG\|Swedish Delight vs Armada](https://www.youtube.com/watch?v=QtuPvcpDqRM&) | SleepyK and Swedish Delight | SleepyK and Swedish Delight have an extensive top level discussion about the Sheik v. Peach matchup. |
| [Sheik Tech Chasing Trick - CDK Tips #1](https://www.youtube.com/watch?v=nyiuXyb4Dkg) | SSBM Tutorials and CDK | Use wavedash back to cover ambiguous DIs off dthrow. |
| [Sheik's Double Poof](https://www.youtube.com/watch?v=YvI-gL8U3vc) | SSBM Tutorials and Captain Faceroll | A Sheik recovery trick. |
| [The Optimal Sheik recovery?](https://www.youtube.com/watch?v=GaU36J5AYUI) | Leffen | Leffen describes an important recovery mix-up. |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Sheik (SSBM): https://www.ssbwiki.com/Sheik_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Sheik_(SSBM)/Down_throw , /Forward_aerial ,
  /Forward_tilt , /Back_aerial , /Up_smash , /Neutral_aerial , /Up_special , /Down_special
- SSBWiki technique pages: https://www.ssbwiki.com/Needle_Storm , /Vanish , /Transform ,
  /Chain_grab , /Tech-chase , /Ledgestall , /List_of_SSBM_tier_lists_(NTSC)
- DruggedFox, "Tech Chasing!": http://portraitinsmash.blogspot.ca/2015/09/tech-chasing.html
- DruggedFox, "Doing Bad Stuff To Marth 101":
  https://portraitinsmash.blogspot.com/2015/02/doing-bad-stuff-to-marth-101.html
- DruggedFox, "Things Sheik Players Aren't Doing":
  https://portraitinsmash.blogspot.com/2015/02/things-sheik-players-arent-doing.html
- DruggedFox, "Sheik on Peach Action":
  https://portraitinsmash.blogspot.com/2015/07/sheik-on-peach-action.html
- DruggedFox, "Sheik Shield Pressure" (first part read):
  https://portraitinsmash.blogspot.com/2015/07/sheik-shield-pressure.html
- Kadano, "Sheik ledgedash specifics" (via web.archive.org):
  http://www.meleeitonme.com/sheik-ledgedash/
- "Sheik Matchup Guide Compilation" (index of links):
  https://docs.google.com/document/d/12-NQSfi_MQj6brnqEJxS2EvkuWTx6VfVbl5BpNCltfY/
- "Collection of Sheik Stuff" (Tero; posts by KirbyKaze, Magus, Strong Bad, bubbaking),
  linked from the compilation:
  https://docs.google.com/document/d/1mlNwPWxO2y8u_w1t_jf_FzMx6OC8BJyFZ2fW-rOj9zk/
- Neighborhood P, "Marth vs. Sheik Guide" (via web.archive.org):
  http://www.meleeitonme.com/guest-article-marth-vs-sheik-guide/
- MookieRah's Marth Q&A Compilation Guide:
  https://docs.google.com/document/d/1Daf_Dqod1HoMj7L26ITeUM-xKUKhfxh2vJLWOl2N0C8/
- Frame data dump: `Sheik.json`
- Not reachable this session: smashboards threads (Sheik Q&A, Up-B Mechanics, hitbox thread),
  reddit comment on up-B edge cancel data. YouTube cards were used for titles only.
