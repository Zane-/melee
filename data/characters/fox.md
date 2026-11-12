---
schema: melee-character/v1
id: fox
name: Fox
aliases: [Fox McCloud, spacie, space animal]
tier: "S (1st of 26), 2021 tier list"
archetype: [rushdown, fastfaller, lightweight, glass-cannon, technical, edgeguarder]
related: [falco]
summary: Fox wins by out-speeding the opponent in neutral, converting any hit, shine or grab into up throw up air or up smash, and ending stocks early with frame 1 shine spikes offstage.
key_tech: [jump-cancel-shine, waveshine, shine-out-of-shield, shine-grab, multishine, drill-shine-pressure, up-throw-up-air, up-throw-chain-grab, shine-spike, short-hop-double-laser, illusion-shorten, firefox-ledge-stall, jab-reset-after-shine, waveshine-infinite]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlFx.dat
framedata: ../framedata/fox.json
code: src/melee/ft/kinds/ftFox
specials:
  neutral_b: "Blaster (laser)"
  side_b: "Fox Illusion (side B)"
  up_b: "Fire Fox"
  down_b: "Reflector (shine)"
attributes:
  weight: 75
  gravity: 0.23
  fall_speed: 2.8
  fast_fall_speed: 3.4
  jump_squat: 3
  jumps: 2
  walk_speed: 1.6
  dash_speed: 1.9
  run_speed: 2.2
  traction: 0.08
  air_speed: 0.83
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [2, 16, 4]
  jab2: [3, 19, 4]
  rapid_jab_start: [null, 7, 0]
  rapid_jab_loop: [2, 36, 1]
  rapid_jab_end: [null, 9, 0]
  dash_attack: [4, 36, 7]
  ftilt_high: [5, 27, 9]
  ftilt_mid_high: [5, 27, 9]
  ftilt: [5, 27, 9]
  ftilt_mid_low: [5, 27, 9]
  ftilt_low: [5, 27, 9]
  utilt: [5, 23, 12]
  dtilt: [7, 28, 10]
  fsmash: [12, 40, 15]
  usmash: [7, 42, 18]
  dsmash: [6, 46, 15]
  nair: [4, 42, 12]
  fair: [6, 53, 7]
  bair: [4, 38, 15]
  uair: [8, 36, 13]
  dair: [5, 50, 3]
  grab: [7, 31, 0]
  dash_grab: [12, 41, 0]
  pummel: [5, 25, 3]
  fthrow: [10, 34, 3]
  bthrow: [null, 39, 2]
  uthrow: [null, 39, 2]
  dthrow: [null, 44, 1]
  special_n_start: [null, 7, 0]
  special_n_loop: [null, 10, 0]
  special_n_end: [null, 24, 0]
  special_air_n_start: [null, 5, 0]
  special_air_n_loop: [null, 10, 0]
  special_air_n_end: [null, 22, 0]
  special_s_start: [null, 20, 0]
  special_s: [null, 4, 0]
  special_s_end: [null, 40, 0]
  special_air_s_start: [null, 20, 0]
  special_air_s: [null, 4, 0]
  special_air_s_end: [null, 40, 0]
  special_hi_hold: [20, 43, 2]
  special_hi_hold_air: [20, 43, 2]
  special_hi: [1, 30, 14]
  special_hi_landing: [null, 20, 0]
  special_hi_fall: [null, 20, 0]
  special_hi_bound: [null, 15, 0]
  special_lw_start: [1, 4, 5]
  special_lw_loop: [null, 28, 0]
  special_lw_hit: [null, 20, 0]
  special_lw_end: [null, 18, 0]
  special_air_lw_start: [1, 4, 5]
  special_air_lw_loop: [null, 28, 0]
  special_air_lw_hit: [null, 20, 0]
  special_air_lw_end: [null, 18, 0]
oos:  # option: frame the hitbox is out
  special_air_lw_start: 4
  nair: 7
  bair: 7
  grab: 7
  dair: 8
  usmash: 8
  fair: 9
  uair: 11
  special_hi_hold: 21
resources: 45
# generated: end
---

# Fox

<!-- GENERATED:attributes -->
## Attributes

Read from `PlFx.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 75 |
| Gravity | 0.23 |
| Terminal fall speed | 2.8 |
| Fast-fall speed | 3.4 |
| Jump squat (frames before airborne) | 3 |
| Full hop / short hop initial Y speed | 3.68 / 2.1 |
| Air jump Y multiplier | 1.2 |
| Jumps | 2 |
| Walk max speed | 1.6 |
| Dash initial speed / run max speed | 1.9 / 2.2 |
| Ground friction (traction) | 0.08 |
| Air max horizontal speed | 0.83 |
| Air acceleration (base + stick) | 0.02 + 0.06 |
| Air friction | 0.02 |
| Normal landing lag | 4 |
| Shield size | 14.375 |
<!-- /GENERATED:attributes -->

## Overview

Fox is a very fast, light fastfaller (a character with high fall speed): weight 75, fall
speed 2.8 (third fastest), fast-fall speed 3.4, run speed 2.2 (second fastest) and a 3-frame
jump squat (the grounded frames before a jump leaves the floor) [wiki:Fox_(SSBM)]. He ranks
1st on the 2021 NTSC tier list [wiki:Fox_(SSBM)]. He wins neutral with movement and with
fast, safe aerials (nair, bair, dair) out of a low short hop, backed by a laser that deals
damage without hitstun and so forces the opponent to come to him [wiki:Fox_(SSBM)]. His
defining move is down B (the Reflector, called "shine"): its hitbox is out on frame 1, Fox
is intangible on that frame, and it can be cancelled by a jump from frame 4
[wiki:Fox_(SSBM)/Down_special]. Everything else in his kit chains through it. He punishes
with short, reliable conversions rather than long combos: up throw into up air, shine into
up smash, and shine spikes offstage [wiki:Fox_(SSBM)]. He dies to being combo'd and chain
grabbed (light plus fast falling means long hitstun and short flight) and to edgeguards on
his linear recovery moves [wiki:Fox_(SSBM)]. He is one of the most execution-heavy
characters: most of his best options have 1-3 frame windows.

## Strengths and weaknesses

- **Strengths:**
  - Frame 1 shine that is jump-cancellable from frame 4: combo starter, combo breaker,
    out-of-shield option, shield pressure tool and gimp in one move
    [wiki:Fox_(SSBM)/Down_special].
  - Up smash hits on frame 7 for 18% with very high knockback (base 30, growth 112) [fd];
    it kills most characters at roughly 75-90% [wiki:Fox_(SSBM)/Up_smash] and many things
    combo into it.
  - Up throw into up air works on most of the cast and kills floaties (slow-falling
    characters) from as low as about 65% on low ceilings [wiki:Fox_(SSBM)/Up_throw].
  - Second fastest run, fast dash dance, 3-frame jump squat, long quick wavedash
    [wiki:Fox_(SSBM)].
  - Laser racks up damage safely and forces approaches [wiki:Fox_(SSBM)].
  - Very hard to kill off the top because of his fall speed [wiki:Fox_(SSBM)].
  - Best ledgedash in the game: 15 actionable intangible frames from a perfect ledgedash,
    tied with Pichu [wiki:Ledgedash].
- **Weaknesses:**
  - Combo food: nearly every character can juggle, combo or chain grab him;
    [Marth](marth.md) and [Peach](peach.md) are singled out for chain grabs on Final
    Destination [wiki:Fox_(SSBM)].
  - Light (weight 75), so he dies early off the sides [wiki:Fox_(SSBM)].
  - Recovery is long but linear; both up B and side B are interceptable, and one hit
    offstage usually ends the stock [wiki:Fox_(SSBM)].
  - Nair, dash attack and jab lose to crouch cancel (holding down to reduce knockback) at
    low and mid percent [wiki:Fox_(SSBM)/Neutral_aerial] [wiki:Fox_(SSBM)/Dash_attack].
  - Shine has one active frame and short range; it must be spaced correctly
    [wiki:Fox_(SSBM)/Down_special].
  - Grab range is only average [wiki:Fox_(SSBM)].
  - Execution errors (missed L-cancel, double jump out of shine, airdodge off the ledge)
    are punished by death.

## Character tech

### Jump-cancelled shine

- **id:** `jump-cancel-shine`
- **What:** Cancelling the Reflector with a jump so that Fox can act almost immediately
  after shining. It is the base of every other shine technique.
- **Inputs:** down B, then jump (X/Y or up on the stick) on or after frame 4 of the shine.
  From the jump squat Fox can leave the ground, grab, up smash, up B or airdodge.
- **Timing:** Hitbox and full-body intangibility on frame 1 only; frames 2-3 are lag;
  jump-cancellable from frame 4 for as long as B is held (frames 4-21 if tapped). An
  uncancelled tapped shine lasts 39 frames. Turning around inside the shine blocks the
  jump cancel for 3 frames [wiki:Fox_(SSBM)/Down_special]. The hitbox does 5%, angle 0,
  set knockback 80 [fd].
- **Used for:** Making shine safe on hit, on shield and on whiff; starting waveshines,
  shine-grabs, shine-up smash, shine-bair, shine-nair.
- **Common errors:** Jumping before frame 4 (nothing happens, Fox sits in shine); holding
  jump too long and full hopping; pressing jump while turning around.
- **Drill idea:** Stationary CPU; player shines and must be airborne or in another action
  by a target frame (for example jump squat begins on frame 4-6 of the shine).

### Waveshine

- **id:** `waveshine`
- **What:** A [wavedash](../techniques/wavedash.md) performed directly out of a
  jump-cancelled shine, so Fox slides toward (or away from) the opponent while they are
  still in shine hitstun [wiki:Waveshine].
- **Inputs:** down B, jump (X/Y recommended), then airdodge diagonally into the ground on
  the first airborne frame.
- **Timing:** With frame-perfect inputs: shine on frame 1, jump on frame 4, Fox's 3-frame
  jump squat, airdodge on frame 7 [wiki:Reflector_(Fox)] [wiki:Fox_(SSBM)]. Wavedash
  landing lag is 10 frames [unverified]. Whether a follow-up connects depends on how far
  the opponent slides: [Peach](peach.md) barely moves, [Luigi](luigi.md) and
  [Ice Climbers](ice-climbers.md) slide too far for normal follow-ups [wiki:Waveshine]
  [lib:Guide to Ace Arwing Pilot Fox McCloud]. Characters lighter than weight 87 fall down
  when shined on the ground instead of sliding: Falco, Fox, Jigglypuff, Kirby, Mewtwo,
  Mr. Game & Watch, Pichu, Pikachu, Roy, Young Link [wiki:Waveshine]. A near-horizontal
  airdodge angle ("89er") gives the longest slide and is needed to reach
  [Marth](marth.md) and [Sheik](sheik.md) reliably [wiki:Waveshine].
- **Used for:** Shine into up smash (kill), grab (then up throw up air), dtilt, down smash
  near the ledge, or another shine [wiki:Waveshine]
  [lib:Guide to Ace Arwing Pilot Fox McCloud]. Also a retreat: shine on shield, wavedash
  back.
- **Common errors:** Airdodging too late (Fox rises and air dodges in the air); stick too
  horizontal (airdodge sideways in the air); shining after a nair that popped the
  opponent into the air, which pushes them back into the ground and cuts the stun short so
  they can punish [lib:Guide to Ace Arwing Pilot Fox McCloud]; opponent SDI (smash
  directional influence, tapping the stick during hitlag to shift position) away.
- **Drill idea:** CPU Peach/Marth/Sheik/Falcon stands in shield-less idle; player must
  shine then land up smash or grab before the CPU can shield (CPU buffers shield out of
  hitstun).

### Shine out of shield

- **id:** `shine-out-of-shield`
- **What:** Jumping out of shield and shining before leaving the ground area, used to
  punish attacks that hit the shield. See
  [out of shield](../techniques/out-of-shield.md).
- **Inputs:** While in shield (after shield stun ends): jump, then down B on the first
  airborne frame, then jump-cancel the shine (usually into a wavedash down or away, or a
  double jump).
- **Timing:** Hits on frame 4 after shield stun at the earliest (3 jump squat frames plus
  the frame 1 shine) [lib:Falco optimal fastfall timing]. Shining later than the first
  airborne frame makes Fox rise and leaves him in the air needing a double jump or
  waveland.
- **Used for:** Punishing unsafe aerials, tilts and smashes on shield; breaking
  [shield pressure](../techniques/shield-pressure.md); it is listed with Samus up B and
  Bowser up B as an option that relieves pillar pressure [wiki:Pillaring].
- **Common errors:** Opponent spaced outside the small shine hitbox (whiff, then Fox is
  airborne next to them) [lib:Guide to Ace Arwing Pilot Fox McCloud]; shining late and
  double jumping away; acting during shield stun so the jump never comes out.
- **Drill idea:** CPU hits Fox's shield with a chosen move at a chosen spacing; success if
  the shine connects within N frames of shield stun ending and the player follows with a
  hit or grab.

### Shine-grab

- **id:** `shine-grab`
- **What:** Jump-cancelling a shine directly into a grab. The jump squat is cancelled by
  the grab input, so Fox never leaves the ground [wiki:Reflector_(Fox)].
- **Inputs:** down B, jump, Z during the jump squat. See
  [jump cancel](../techniques/jump-cancel.md).
- **Timing:** Jump on frame 4 or later of the shine, Z within Fox's 3 jump squat frames
  [wiki:Fox_(SSBM)/Down_special] [wiki:Fox_(SSBM)]. Standing grab is active on frames 7-8
  of the grab [wiki:Fox_(SSBM)/Grab].
- **Used for:** Beating opponents who hold shield through aerial-shine pressure; the shine
  catches anything other than shield, the grab beats shield. Loses to a roll or spot
  dodge started before the grab [wiki:Reflector_(Fox)].
- **Common errors:** Z too late (Fox jumps and air-attacks with Z); Z too early (grab
  never comes out because the jump has not started).
- **Drill idea:** CPU holds shield and randomly rolls or keeps shielding after an aerial;
  success if a grab lands on the held shield within N frames of the shine.

### Multishine

- **id:** `multishine`
- **What:** Repeated grounded shines, each jump-cancelled and re-shined on the first
  airborne frame so that Fox lands immediately and can jump again
  [wiki:Reflector_(Fox)].
- **Inputs:** down B, jump, down B on the first airborne frame, jump once grounded,
  repeat.
- **Timing:** Frame-perfect cycle for Fox: shine on frame 1, jump on 4, second shine on 7,
  grounded again on 11, earliest next jump 12, third shine on 15; one shine every 8 frames
  [wiki:Reflector_(Fox)]. If the second shine is later than the first airborne frame Fox
  rises too high and the chain ends. Jumping while still airborne (frame 10) spends the
  double jump. On hit or shield each shine adds 4 frames of hitlag for Fox
  [lib:Multishine: An Extensive Guide].
- **Used for:** Shield pressure with gaps too small to react to; double shine into grab or
  into wavedash. Rarely more than two in a row in tournament because errors are punished
  [wiki:Reflector_(Fox)].
- **Common errors:** Double jumping out of the second shine; late B so Fox short hops with
  the shine out; drifting out of range as the shield is pushed back.
- **Drill idea:** Count consecutive grounded shines on a shielding CPU with at most N
  frames between shine hitboxes; fail on double jump or on leaving the ground for more
  than the landing frames.

### Drill-shine shield pressure

- **id:** `drill-shine-pressure`
- **What:** [SHFFL](../techniques/shffl.md) (short hop, fast fall, L-cancel) aerial into
  shine, jump-cancelled into another aerial, waveshine, grab or retreat. Called
  pillaring when looped [wiki:Pillaring].
- **Inputs:** short hop, dair or nair, fast fall, L-cancel, down B, then jump into the
  next option.
- **Timing:** Nair is 0 on shield at best and bair -2 at best
  [wiki:Fox_(SSBM)/Neutral_aerial] [wiki:Fox_(SSBM)/Back_aerial]; L-cancelled landing lag
  is 7 (nair), 9 (dair) and 10 (bair) frames [fd]. Dair's advantage on shield varies with
  staleness and timing, so a fresh, well-timed drill cannot be shield grabbed while a
  stale or mistimed one can [wiki:Fox_(SSBM)/Down_aerial]. On hit, a perfectly timed
  SHFFL drill (dair input on the second airborne frame) true-combos into up smash, grab
  or dtilt [wiki:Fox_(SSBM)/Down_aerial].
- **Used for:** Opening shields, beating crouch cancel and ASDI down (dair is not
  crouch-cancellable the way nair is) [wiki:Fox_(SSBM)/Down_aerial].
- **Common errors:** Missed L-cancel (18 frames of lag after dair [fd]); aerial too high
  on the shield so the gap before shine allows a shield grab; opponent SDIs out of the
  drill.
- **Drill idea:** CPU shields and attempts a grab at the first frame it is free; success
  if the player's shine hits the grab attempt or the shield before the grab connects, N
  repetitions in a row.

### Up throw up air

- **id:** `up-throw-up-air`
- **What:** Fox's main grab conversion and kill confirm: up throw, then jump (usually
  double jump) into up air [wiki:Fox_(SSBM)/Up_throw].
- **Inputs:** grab, up on the stick, then full jump, double jump, up air, following the
  opponent's DI (directional influence, holding a direction to bend the launch angle).
- **Timing:** Up throw releases on frame 8 against a baseline-weight character and the
  whole animation is 38 frames; the speed scales with the opponent's weight
  [wiki:Fox_(SSBM)/Up_throw]. Up air hits twice: tail on frames 8-9 (5%, set knockback)
  and kick on frames 11-14 (13%, base 40, growth 116) [fd]. The tail gives only 4 frames
  of hitlag in which to SDI [wiki:Fox_(SSBM)/Up_aerial].
- **Used for:** Kills on floaties and mid-weights from roughly 65% upward on low ceilings
  (Yoshi's Story, Pokemon Stadium) [wiki:Fox_(SSBM)/Up_throw]; damage and juggles at
  lower percent.
- **Common errors:** Opponent SDIs the tail hit and falls out before the kick, then
  punishes Fox [wiki:Fox_(SSBM)/Up_aerial]. Fix: hit with the kick only. This is done by
  up-airing immediately out of the double jump (Fox rises between the two hits), double
  jumping lower than usual so only the top of the kick reaches, and fading back; the
  kick alone does 5% less, so the kill percent is about 5% higher
  [lib:Single Hit Up Air].
- **Drill idea:** Player starts holding the CPU in grab at a set percent; CPU picks random
  DI (in, away, none) and SDIs the first hit up/away; success if the kick connects (or the
  CPU dies).

### Up throw chain grab on fastfallers

- **id:** `up-throw-chain-grab`
- **What:** Repeated up throw into regrab on Fox and Falco, ended with up tilt, up smash
  or up air. See [chain grab](../techniques/chain-grab.md).
- **Inputs:** up throw, follow DI with a dash, jump-cancel grab (or pivot grab when they
  land behind), repeat.
- **Timing:** Tool-assisted limits before staling: against Fox 0-66% regardless of DI if
  the thrown Fox has the lower port number and 0-54% if it has the higher port; against
  Falco 0-81% (lower port) or 0-66% (higher port). If the victim DIs fully left or right
  it works until 86% (Fox) and 103% (Falco). Many percents need pivot or dash-dance
  jump-cancel grabs with 1-2 frames of leniency [wiki:Fox_(SSBM)/Up_throw]. Practical
  player numbers: Fox 0-50%, Falco 0-55% with no or slight DI, about 80% if they keep
  DI'ing away; finish with up tilt at about 50%, and delay the up tilt after about 55%
  [lib:Chaingrab Info].
- **Used for:** Guaranteed damage in the Fox ditto and against [Falco](falco.md) on Final
  Destination, or wherever no platform interrupts [lib:Guide to Ace Arwing Pilot Fox
  McCloud].
- **Common errors:** Dash grab instead of jump-cancel grab (too slow); not turning for DI
  behind; continuing past the escape percent, where no DI lets the victim jump or shine
  out [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Drill idea:** CPU Fox/Falco at 0% on Final Destination with random DI per throw;
  count regrabs until a target percent, then require a finisher (up tilt or up smash).

### Shine spike

- **id:** `shine-spike`
- **What:** Hitting an offstage opponent with the shine. Its 0-degree angle and set
  knockback push them away from the stage at any percent, and it cannot be meteor
  cancelled [wiki:Shine_spike] [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Inputs:** Run or jump offstage, down B when touching the opponent, jump out of the
  shine (turn around in shine first if needed), return with double jump, side B or up B,
  or grab the ledge.
- **Timing:** One active frame, so timing and spacing must be exact
  [wiki:Fox_(SSBM)/Down_special]. Works even at 0% [wiki:Shine_spike]. Hitting with the
  lower outside part of the hexagon gives the best trajectory; the hitbox reaches
  slightly further behind Fox [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Used for:** Killing characters with poor horizontal or vertical recovery at any
  percent. Much weaker against Jigglypuff, Kirby, Yoshi, Mewtwo and sometimes
  Pikachu/Pichu [lib:Guide to Ace Arwing Pilot Fox McCloud]. The "Armada shine" is the
  variant that hits Fox/Falco during up B between its hitbox frames [wiki:Shine_spike].
- **Common errors:** Shining into the stage: characters that tumble from shine (lighter
  than Marth) can wall tech it [lib:Guide to Ace Arwing Pilot Fox McCloud]; using the
  double jump on the way out and having no way back.
- **Drill idea:** CPU recovers from a set offstage position with a randomised option;
  success if a shine connects offstage and Fox returns to the stage or ledge alive.

### Short hop double laser

- **id:** `short-hop-double-laser`
- **What:** Firing two lasers in one short hop to add damage from range without
  committing. See [short hop](../techniques/short-hop.md).
- **Inputs:** short hop, B twice, land. Stick left/right after the first B to drift
  (moving the stick prevents a fast fall) [wiki:Short_hop_laser].
- **Timing:** Fox's short hop is very low, so both shots need tight inputs; he can fit at
  most two [wiki:Short_hop_laser]. Aerial blaster: first shot on frame 10, repeat window
  frames 4-14; grounded: first shot on frame 12 with more end lag
  [wiki:Fox_(SSBM)/Neutral_special]. Each laser does 3% fresh and no hitstun
  [wiki:Fox_(SSBM)/Neutral_special]; on shield it causes a few frames of shield stun
  [wiki:Fox_(SSBM)/Neutral_special].
- **Used for:** Forcing an opponent who is ahead, or who out-ranges Fox, to approach;
  free damage on a shield-broken or sleeping opponent [wiki:Fox_(SSBM)/Neutral_special].
- **Common errors:** Full hop; only one laser; landing during the blaster animation and
  getting the grounded end lag.
- **Drill idea:** Count lasers that hit a distant CPU in N seconds; fail on any full hop
  or on landing lag from the grounded blaster ending.

### Shortened Illusion

- **id:** `illusion-shorten`
- **What:** Pressing B again during side B (Fox Illusion) to stop the dash early, giving
  five shorter distances [wiki:Fox_(SSBM)/Side_special].
- **Inputs:** side B, then B on one of the 5 frames in which Fox travels (or just before).
- **Timing:** Fox starts moving on frame 21; the hitbox is frames 22-25; he can grab a
  ledge from frame 29; the whole move is 63 frames [wiki:Fox_(SSBM)/Side_special]
  [lib:Guide to Ace Arwing Pilot Fox McCloud]. One shortened length per travel frame
  [wiki:Fox_Illusion].
- **Used for:** Landing short of an edgeguard that was timed for the full-length dash;
  sweetspotting the ledge from a distance that would otherwise carry him onto the stage
  [wiki:Fox_Illusion] [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Common errors:** Shortening too much and falling short of the ledge in helpless fall;
  pressing B too late (full length).
- **Drill idea:** Fox starts offstage at a set distance; a marker shows the required
  landing spot (ledge, or a point on stage); success if he lands or grabs within
  tolerance.

### Firefox ledge stall

- **id:** `firefox-ledge-stall`
- **What:** Dropping from the ledge and immediately using up B so that Fox regrabs the
  ledge and refreshes ledge intangibility [wiki:Ledgestall].
- **Inputs:** From ledge hang: stick down or away to drop, then up B (optionally double
  jump or shine first), regrab.
- **Timing:** A ledge grab gives 7 frames of catch animation plus 30 more frames of
  intangibility; the earliest drop is frame 9, leaving 29 intangible frames, and the
  ledge cannot be regrabbed for 29 frames after letting go. A fully intangible stall
  needs the frame-perfect drop, but Fox has a 14-frame window after dropping to input up B
  and still be fully intangible [wiki:Ledgestall]. Double jumping and delaying up B by at
  least 9 frames after the drop suppresses the charge hitboxes [wiki:Ledgestall].
- **Used for:** Holding the ledge against a recovering opponent, waiting out an
  opponent's ledge trap, setting up drop-down shine spikes with intangibility
  [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Common errors:** Fast falling too far before up B and dying; up B aimed into the
  stage; late drop leaving vulnerable frames.
- **Drill idea:** Count consecutive stalls with zero vulnerable frames (or at most N);
  variation with a CPU attacking the ledge on a timer.

### Jab reset after shine

- **id:** `jab-reset-after-shine`
- **What:** Against characters that fall over when shined, a jab on the downed opponent
  forces them to stand up, giving a free grab or smash. See
  [jab reset](../techniques/jab-reset.md). Using an attack to force the stand-up after a
  waveshine is called Thunder's combo [wiki:Waveshine].
- **Inputs:** shine, (wavedash to them), jab once the opponent has missed the tech and is
  lying down, then grab or up smash. Dtilt is a common alternative
  [wiki:Fox_(SSBM)/Down_tilt].
- **Timing:** Jab hits on frames 2-3 [fd]. Per the Fox guide, a jabbed prone Fox stands up
  below 82-84% and a prone Falco below 52-55%; above that they pop into the air instead
  and can act [lib:Guide to Ace Arwing Pilot Fox McCloud]. The victim can SDI the jab up
  to escape; a second jab covers that [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Used for:** Turning a grounded shine on Fox, Falco, Pikachu, Jigglypuff and other
  light characters into a grab.
- **Common errors:** Opponent techs the shine (no reset possible, becomes a
  [tech chase](../techniques/tech-chase.md)); jabbing above the pop-up percent.
- **Drill idea:** CPU Fox/Falco at set percent is shined on the ground and randomly
  techs or misses; player must react: jab reset into grab on a missed tech, chase on a
  tech.

### Waveshine infinite

- **id:** `waveshine-infinite`
- **What:** Repeated waveshines (or drill-shines) on a character who does not fall from
  shine, most reliably against a wall [wiki:Waveshine].
- **Inputs:** Against a wall: shine, wavedash straight down, shine, repeat; finish with a
  jump-cancelled up smash [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Timing:** Each link is a full waveshine; the victim must weigh 87 or more
  [wiki:Waveshine]. Wall-less versions exist but are broken by SDI and are considered
  impractical; among legal stages only Pokemon Stadium's transformations provide walls
  [wiki:Waveshine] [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Used for:** Large guaranteed damage on Pokemon Stadium transformations.
- **Common errors:** Drifting out of shine range (the victim's hitstun animation pushes
  Fox back); victim SDIs out; victim wall techs the up smash finisher
  [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Drill idea:** CPU Peach or Captain Falcon against a wall with SDI on/off; count
  consecutive shines, then require an up smash finish.

## Neutral game

- Goal: get a clean aerial, grab or shine on the opponent, or make them whiff and punish
  with dash attack, grab or up smash.
- **Movement:** [dash dance](../techniques/dash-dance.md) and wavedash back to bait, then
  run in. Run speed 2.2 and a 3-frame jump squat let Fox threaten from far away
  [wiki:Fox_(SSBM)].
- **Nair:** frames 4-31, 12% clean then 9% [fd]. The standard approach and anti-approach
  aerial. Loses to crouch cancel: light characters can crouch cancel it until the low
  60s%, heavy ones until above 80%; ASDI down alone works to about half those percents
  [wiki:Fox_(SSBM)/Neutral_aerial].
- **Dair (drill):** frames 5-24 in seven hits [wiki:Fox_(SSBM)/Down_aerial]; beats crouch
  cancel and ASDI down, catches dashes toward Fox, leads to shine/up smash/grab.
- **Bair:** frames 4-19, 15% clean [fd]; longer reach than nair, used for spacing and to
  beat out-of-shield options [wiki:Fox_(SSBM)/Back_aerial].
- **Dash attack:** hits on frame 4; a whiff punish and, on an airborne or high-percent
  opponent, a confirm into up smash or up air; unsafe on crouch cancel
  [wiki:Fox_(SSBM)/Dash_attack].
- **Grab:** running jump-cancel grab; leads to up throw conversions.
- **Laser:** 3% per shot with no hitstun [wiki:Fox_(SSBM)/Neutral_special]; used when the
  opponent will not approach.
- **Full hop:** full-hop nair/bair/dair control the space above platforms and are hard to
  anti-air [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Running shine:** catches jumps and dashes; leads to waveshine follow-ups or, on
  lightweights, a knockdown.

## Punish game

Fox's punishes are short and end either in a vertical kill (up smash, up air) or in an
edgeguard (bair, down smash, shine offstage). Against characters that slide from shine he
waveshines into grab or up smash; against fastfallers he chain grabs and tech chases;
against floaties he looks for up throw up air and up tilt strings.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| Up throw | Fox | 0-54% any DI (0-66% if victim has lower port) | Regrab | Before staling; pivot/JC grabs needed | [wiki:Fox_(SSBM)/Up_throw] |
| Up throw | Falco | 0-66% any DI (0-81% if victim has lower port) | Regrab | Same conditions | [wiki:Fox_(SSBM)/Up_throw] |
| Up throw | Fox / Falco | about 50% / 55% (end of practical chain grab) | Up tilt, up tilt, first-hit up air, more | Player rule of thumb | [lib:Chaingrab Info] |
| Up throw | Fastfallers | around 20-40%, no DI | Up tilt into grab, aerial or tech chase | | [wiki:Fox_(SSBM)/Up_throw] |
| Up throw | Fastfallers | around 40%+ | Nair (knocks down), then tech chase | For DI in or away | [wiki:Fox_(SSBM)/Up_throw] |
| Up throw | Fastfallers | 68%+ | Fair knocks down, tech chase or up smash | Combos to up smash on DI in at higher percent | [wiki:Fox_(SSBM)/Up_throw] |
| Up throw | Fox (ditto) | up to 102% (victim higher port) or 109% (lower port), no DI | Dash, pivot, charged up smash | Kills on any stage if no platform interferes | [wiki:Fox_(SSBM)/Up_throw] |
| Up throw | Floaties and mid-weights | from about 65% (kill range, low ceiling) | Up air | SDI on the tail hit escapes; kick-only up air avoids it | [wiki:Fox_(SSBM)/Up_throw] [lib:Single Hit Up Air] |
| Waveshine | Characters weight 87+ with normal traction | any | Up smash, grab, dtilt, down smash | Not Luigi/Ice Climbers (slide too far) | [wiki:Waveshine] |
| Grounded shine | Characters lighter than 87 | below pop-up percent | Jab reset into grab | Only on missed tech | [lib:Guide to Ace Arwing Pilot Fox McCloud] |
| SHFFL dair | Most | low-mid | Shine, up smash, grab or dtilt | True combo only if drill is timed perfectly and fresh | [wiki:Fox_(SSBM)/Down_aerial] |
| Dash attack | Fastfallers | kill percent | Up smash | Not on DI away (tech chase instead) | [wiki:Fox_(SSBM)/Dash_attack] |
| Dash attack | Dr. Mario, Peach, Luigi, mid-fallers | kill percent | Up air | | [wiki:Fox_(SSBM)/Dash_attack] |
| Back throw | Fox, Falco | typical | Tech chase; up smash on wrong DI | Fast throw, hard to DI on reaction | [wiki:Fox_(SSBM)/Back_throw] |
| Up tilt | Most | low | Up tilt, up air, up smash | Low base knockback (18), hits frame 5 | [wiki:Fox_(SSBM)/Up_tilt] |
| Shine | Sheik, others | mid | Waveshine down smash | Sets up an edgeguard when too low to kill | [lib:Guide to Ace Arwing Pilot Fox McCloud] |

### Chain grabs and tech chases

- **Up throw chain grab** on Fox and Falco: see the technique entry above. It needs a
  stage area without platforms. The victim's best DI is none or slight (allows a jump or
  shine out at about 50-55%); full DI to a side extends it to about 80%
  [lib:Chaingrab Info] [lib:Guide to Ace Arwing Pilot Fox McCloud].
- Fox cannot chain grab reliably at higher percent, but up throw still leads to aerials
  depending on DI [wiki:Fox_(SSBM)].
- **Platform tech chase:** up throw onto a platform, then up air. At lower percents Fox
  cannot cover everything on reaction; he either reads tech in place / missed tech or
  waits and reacts to a tech roll [wiki:Tech-chase].
- **Down throw:** a meteor that can be teched. Reaction tech chase works on very light
  characters (Jigglypuff, Mr. Game & Watch); used on characters that up throw up air does
  not work on, such as Samus [wiki:Fox_(SSBM)/Down_throw].
- **Knockdown tech chases** from nair (about 40%+), dash attack (about 50%+) and fair
  (68%+) on fastfallers [wiki:Fox_(SSBM)/Up_throw].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Up smash (clean) | Most characters | roughly 75-90% | Grounded, facing the opponent | [wiki:Fox_(SSBM)/Up_smash] |
| Up throw, up air | Floaties / low fall speed | from about 65% | Low ceilings (Yoshi's Story, Pokemon Stadium); later on high ceilings | [wiki:Fox_(SSBM)/Up_throw] |
| Up throw, up smash | Fastfallers | just above 100% | | [wiki:Fox_(SSBM)/Up_throw] |
| Kick-only up air | Marth, Sheik | low kill range about 90% | About 5% later than the two-hit version | [lib:Single Hit Up Air] |
| Fsmash | Most | around 120% | Late hit is weaker | [wiki:Fox_(SSBM)] |
| Up tilt | Light floaties | around 120% | Grounded foot hitbox | [wiki:Fox_(SSBM)] |
| Shine spike | Anyone with a limited recovery | any, including 0% | Offstage, sends away from the stage | [wiki:Shine_spike] |
| Bair (clean) | Any | Unknown (edgeguard move) | Offstage or at the ledge | [wiki:Fox_(SSBM)/Back_aerial] |
| Down smash | Any | Unknown (edgeguard move) | Low angle (25 degrees [fd]) at the ledge; techable on the stage wall | [wiki:Fox_(SSBM)/Down_smash] |

- **Kill setups:** waveshine up smash; SHFFL dair or nair into up smash; dash attack into
  up smash on fastfallers; jab into up smash [wiki:Fox_(SSBM)]; up throw up air; back
  throw into up smash on bad DI [wiki:Fox_(SSBM)/Back_throw].
- **Edgeguards:** shine spike (run off or drop from ledge with intangibility), bair
  offstage, down smash and down-angled ftilt at the ledge
  [wiki:Fox_(SSBM)/Forward_tilt], fsmash against [Captain Falcon](captain-falcon.md) to
  cover both ledge and stage [wiki:Fox_(SSBM)/Forward_smash], grabbing the ledge
  (edgehog) with a ledge stall. Fthrow and bthrow put opponents offstage quickly;
  fthrow has the same speed against every weight, which makes it strong against heavy
  characters such as Captain Falcon [wiki:Fox_(SSBM)/Forward_throw].
- Against [Sheik](sheik.md): hold the ledge and time a roll or stand-up through her up B
  hitbox so she must land on stage [lib:Guide to Ace Arwing Pilot Fox McCloud].

## Recovery

- **Options:**
  - Double jump: very high (about 40 units versus a 31-unit first jump)
    [wiki:Fox_(SSBM)].
  - Up B (Fire Fox): charges with a multi-hit flame on even frames 20-32 (2% each), then
    travels with a 14% hitbox on frames 43-72; total 92 frames; angle chosen with the
    stick at release [wiki:Fox_(SSBM)/Up_special]. Longest recovery of the space
    animals; landing on stage gives very little lag [wiki:Fire_Fox].
  - Side B (Fox Illusion): fast horizontal dash, moves on frame 21, covers about half of
    Final Destination, can be shortened to five lengths
    [wiki:Fox_(SSBM)/Side_special] [wiki:Fox_Illusion].
  - Shine stall: shining in the air stops his momentum and slows his fall, changing
    timing without using a jump [wiki:Reflector_(Fox)].
  - Wall jump on stages with walls [wiki:Fox_(SSBM)].
  - Airdodge onto the stage or a platform [unverified].
- **Mixups:** Up B angle (to ledge, onto stage, to a platform, high over the opponent);
  side B at ledge height versus above the stage, full versus shortened; delaying with
  shine or double jump; sweetspotting the ledge so the hurtbox is never above the stage
  (see [recovery](../techniques/recovery.md)). The up B angle also changes his collision
  shape, which can make wall techs easier [lib:ECB manipulation via Firefox angles allows
  for easier techs] (title only, not read).
- **Weaknesses:** Both specials are linear and slow to start (up B does not move until
  frame 43 [wiki:Fox_(SSBM)/Up_special]); once hit out of either he usually cannot
  recover again [wiki:Fox_(SSBM)]. Side B ends in helpless fall. Low air speed means his
  drift alone covers little distance [wiki:Fox_(SSBM)].

### Edgeguarding Fox

- **Decision tree for the CPU-as-Fox:** above ledge height and far: side B (full or
  shortened) or drift then up B. Below ledge height: must up B. Close to the ledge with a
  jump: double jump to ledge, double jump side B, or double jump airdodge.
- **Side B:** hit it with a move placed on the travel line just as it arrives. Marth's
  jab and other disjointed moves, Falco's dair, and Mario's and Dr. Mario's cape all
  intercept it [wiki:Fox_(SSBM)]. Low moves at the ledge (Fox dtilt
  [wiki:Fox_(SSBM)/Down_tilt], Falcon dtilt [wiki:Captain_Falcon_(SSBM)], Ganondorf
  down-angled ftilt [wiki:Ganondorf_(SSBM)]) catch the sweetspot attempt. The sound cue
  ("ping") at startup can be used to time a hit [lib:Guide to Ace Arwing Pilot Fox
  McCloud]. A shortened side B beats options timed for full length.
- **Up B:** the 42 startup frames let the edgeguarder reach him. Options: shine spike
  between the charge hits (Armada shine) [wiki:Shine_spike]; a spike or strong aerial
  into the charge; grab the ledge during the charge so he must land on stage, then punish
  the landing; or wait on stage and hit the travel path. The charge hits for 2% and can
  knock an edgeguarder away [wiki:Fox_(SSBM)/Up_special].
- **Forcing low:** [Falco](falco.md) lasers fired offstage clip his double jump and force
  him to recover from below [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Walls:** if hit into the stage Fox can wall tech (see
  [wall tech](../techniques/wall-tech.md)); edgeguarders should hit him away from the
  wall or follow with a delayed bair to catch the side B after the tech
  [lib:Guide to Ace Arwing Pilot Fox McCloud].

## Defense and out of shield

- **Out of shield:** shine (frame 4) [lib:Falco optimal fastfall timing]; shield grab
  (grab active on frame 7 [wiki:Fox_(SSBM)/Grab]); nair or bair (frame 7); up smash
  (frame 8) [lib:A Dissection of Falco's Options on Shield]; wavedash out; roll.
- **Crouch cancel / ASDI down:** useful at low percent to shine or grab through weak hits;
  as a light character Fox stops being able to hold the ground earlier than heavy
  characters. Do not crouch cancel moves that send down or have high base knockback.
- **Combo escapes:** frame 1 shine (intangible on that frame) as soon as hitstun ends;
  double jump; DI and SDI. Against chain grabs, no or slight DI lets him shine or jump
  out earliest [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Teching:** tech away or in place to avoid tech chases; missing a tech at the edge of
  a platform can slide him off, which makes him actionable immediately
  [wiki:Fox_(SSBM)/Down_special].
- **What beats Fox on shield:** grabs (he is chain grabbed by much of the cast), Falco's
  pillar pressure, and well-spaced disjoints that the short shine cannot reach. Some of
  Fox's hurtboxes extend slightly outside a full shield and can be poked
  [lib:Guaranteed Shield Poke on Full Shield Fox] (title and description only).

## As the training dummy

- **Class:** light (weight 75), fastfaller (fall 2.8, fast fall 3.4)
  [wiki:Fox_(SSBM)]. Long hitstun, low vertical travel, early horizontal deaths.
- **Shine reaction:** falls over when shined on the ground and can tech it
  [wiki:Waveshine].
- **Chain grabbed by:** [Marth](marth.md) up throw from 0 to about 60%
  [wiki:Chain_grab]; [Fox](fox.md) up throw (ranges above); [Peach](peach.md) up throw,
  starting at 0-18% depending on DI; [Sheik](sheik.md) down throw tech chase; Mario and
  Dr. Mario up throw; Donkey Kong up throw and cargo up throw; Mewtwo down throw
  [wiki:Chain_grab]; [Ganondorf](ganondorf.md) down throw from 34% (pre-throw) upward,
  rated the hardest chain grab in the game [lib:The Ganon Chaingrabbing Guide];
  [Falco](falco.md) down throw pseudo chain grab from 0 to 40% in NTSC
  [wiki:Falco_(SSBM)/Down_throw]; Pikachu up throw [unverified].
- **Tech chased by:** [Captain Falcon](captain-falcon.md) (down throw at low percent, up
  throw after about 50%; Fox can jump out of up throw at about 85% realistically)
  [lib:Techchasing Like a Man: Complete Breakdown]; Sheik; Fox; Marth.
- **Strong DI for a realistic CPU:** against Marth's up throw chain grab, no DI (shine
  out possible from about 20%) rather than side DI (extends it to about 80%)
  [lib:Guide to Ace Arwing Pilot Fox McCloud]; against Fox's up throw, no or slight DI
  [lib:Chaingrab Info]; against Falco's down throw, DI down and shine
  [wiki:Falco_(SSBM)/Down_throw]; against horizontal kill moves, up and in (survival DI)
  [unverified]; against up smash and up air, to the side [unverified].
- **Strong tech choices:** mix tech in place, tech away, tech in and no tech; shine or
  spot dodge immediately after tech in place.
- **Known thresholds (attacker's fresh move):** Ganondorf jab knocks Fox down at 38%,
  ftilt at 22%, dtilt at 17%, dash attack at 12%
  [lib:Techchasing into 2015: Metagame and Theory]. Fox's own nair knocks Fox/Falco down
  at about 40%, dash attack at about 50%, fair at 68% [wiki:Fox_(SSBM)/Up_throw]. A jab
  on prone Fox pops him up instead of standing him from 82-84%
  [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Recovery behaviour for edgeguard drills:** see "Edgeguarding Fox".

## Matchup notes

### vs Marth

- Marth out-ranges Fox and converts a grab into the up throw chain grab, tipper fsmash or
  an edgeguard; Fox must not run into dash-cancelled dtilt or jump-cancel grab range
  [lib:Guide to Ace Arwing Pilot Fox McCloud].
- Fox's best conversions are up throw up air (kick-only against SDI, low kill range about
  90% [lib:Single Hit Up Air]) and nair strings into up smash.
- Marth does not fall from shine in NTSC, so waveshines work but need a long wavedash
  [wiki:Waveshine].
- Marth's edgeguards on side B and up B are among Fox's most common ways to lose a stock
  early [lib:Guide to Ace Arwing Pilot Fox McCloud].

### vs Falco

- Falco's lasers (which do cause hitstun) limit Fox's movement; his shine combos and dair
  edgeguards kill Fox early. Fox answers with knockdowns, the up throw chain grab,
  edgeguards and shine spikes; Falco loses stocks at very low percent offstage
  [lib:Guide to Ace Arwing Pilot Fox McCloud].
- Falco's side B starts moving on frame 17 versus Fox's frame 21
  [lib:Guide to Ace Arwing Pilot Fox McCloud].
- Final Destination favours whichever player lands the grab or shine combo; Fox players
  often ban it [lib:Guide to Ace Arwing Pilot Fox McCloud].

### vs Sheik

- Sheik tech chases Fox from down throw and kills with fair; Fox cannot combo up throw at
  0% into up air or up smash on her [lib:Guide to Ace Arwing Pilot Fox McCloud].
- Waveshine down smash sets up edgeguards at percents too low for a vertical kill
  [lib:Guide to Ace Arwing Pilot Fox McCloud].
- Edgeguard her by holding the ledge through the up B hitbox
  [lib:Guide to Ace Arwing Pilot Fox McCloud].

### vs Jigglypuff

- Up throw up air and up smash are the kill tools; fair is more useful than usual because
  floaties do not fall out of it [wiki:Fox_(SSBM)/Forward_aerial]
  [wiki:Fox_(SSBM)/Up_aerial].
- Puff falls from shine, crouch cancels nair until the low 60s% and punishes with Rest
  [wiki:Fox_(SSBM)/Neutral_aerial] [wiki:Waveshine]. Shine spikes are weak against her
  recovery [lib:Guide to Ace Arwing Pilot Fox McCloud].

### vs Peach

- Peach barely slides from shine, so waveshine into grab or up smash is consistent
  [wiki:Waveshine] [lib:Guide to Ace Arwing Pilot Fox McCloud].
- She chain grabs Fox with up throw and punishes nair with crouch cancel
  [wiki:Chain_grab].

### vs Captain Falcon

- Falcon tech chases Fox from throws and kills with knee. Fox gimps Falcon easily:
  fthrow near the ledge creates a 50:50, and fsmash covers both ledge and stage
  [wiki:Fox_(SSBM)/Forward_throw] [wiki:Fox_(SSBM)/Forward_smash].

### vs Fox (ditto)

- Decided by grabs: up throw chain grab, up tilt strings, up smash; grounded shine gives
  a knockdown and a jab reset rather than a combo
  [lib:Guide to Ace Arwing Pilot Fox McCloud].
- Offstage, a single shine ends the stock; shortened side B is the main counter
  [lib:Guide to Ace Arwing Pilot Fox McCloud].

## Drill seeds

### Shine out of shield punish

- **id:** `fox-shine-oos`
- **Goal:** Punish a move on shield with a frame 4 shine and convert.
- **Player:** Fox
- **CPU:** [Marth](marth.md) (fsmash, fair, dtilt), [Falco](falco.md) (dair, nair),
  [Sheik](sheik.md) (ftilt, dash attack), [Captain Falcon](captain-falcon.md) (nair,
  knee)
- **Setup:** Final Destination, centre. Fox shielding, CPU 15-25 units away facing him.
  Both at a chosen percent.
- **CPU behaviour:** Performs the selected attack into Fox's shield with randomised
  spacing (close/tipper) and, for aerials, randomised timing (early/late).
- **Success:** Shine hitbox connects within N frames of Fox's shield stun ending (N = 4
  for frame-perfect, larger for practice) and a follow-up (up smash, grab or aerial) hits
  before the CPU can act.
- **Fail:** Fox is hit or grabbed, shine whiffs, or Fox double jumps away without hitting.
- **Variations:** Add a CPU follow-up (Marth second fsmash, Falco shine after dair) that
  punishes slow reactions; spacings that are out of shine range, where the correct answer
  is wavedash out of shield or nair instead.
- **Data needed:** CPU move frame data and shield stun, shine hitbox size, Fox jump squat
  (3), opponent weight (slide versus fall from shine).

### Waveshine to up smash

- **id:** `fox-waveshine-usmash`
- **Goal:** Convert a grounded shine into up smash or grab on characters that slide.
- **Player:** Fox
- **CPU:** [Peach](peach.md), [Marth](marth.md), [Sheik](sheik.md),
  [Captain Falcon](captain-falcon.md), [Ganondorf](ganondorf.md)
- **Setup:** Flat stage, CPU standing next to Fox at kill percent for up smash
  (roughly 75-90% [wiki:Fox_(SSBM)/Up_smash]).
- **CPU behaviour:** Stands or shields-then-drops; after being shined, holds a random DI
  or SDIs away, and buffers shield or a jump at the first actionable frame.
- **Success:** Up smash (or grab) connects before the CPU's first actionable frame.
- **Fail:** CPU shields, jumps or hits Fox first; Fox airdodges in the air.
- **Variations:** SDI away on/off; start from a SHFFL dair instead of a raw shine;
  backwards waveshine; opponents with longer slides.
- **Data needed:** Shine set knockback and resulting hitstun per weight, each character's
  traction, Fox wavedash length, up smash startup (frame 7).

### Up throw up air against SDI

- **id:** `fox-uthrow-uair`
- **Goal:** Land the kill from grab against every DI, including SDI on the first hit.
- **Player:** Fox
- **CPU:** [Marth](marth.md), [Sheik](sheik.md), [Peach](peach.md),
  [Jigglypuff](jigglypuff.md)
- **Setup:** Fox holding the CPU in grab at centre stage; CPU at 80-110%; Yoshi's Story or
  Battlefield.
- **CPU behaviour:** Random throw DI (none, in, away, behind); on being hit by the up air
  tail, SDIs up or away during the 4 frames of hitlag and then attacks or jumps.
- **Success:** The up air kick connects (CPU is launched by the 13% hit) or CPU is KO'd.
- **Fail:** Only the tail hits, the up air whiffs, or the CPU acts first.
- **Variations:** Platform directly above (requires waiting or covering a tech on the
  platform); lower percents where the goal is a juggle instead of a kill.
- **Data needed:** Up throw knockback and release frame by weight, up air hit frames,
  opponent fall speed and weight, ceiling height.

### Chain grab fastfallers

- **id:** `fox-uthrow-chaingrab`
- **Goal:** Regrab Fox or Falco out of up throw until the escape percent, then finish.
- **Player:** Fox
- **CPU:** [Fox](fox.md), [Falco](falco.md)
- **Setup:** Final Destination, centre; CPU at 0% held in grab.
- **CPU behaviour:** Random DI each throw (none, slight, full left, full right); at
  escape percents with no DI, jumps or shines on the first actionable frame.
- **Success:** Reach a target percent (for example 50% on Fox, 55% on Falco
  [lib:Chaingrab Info]) without dropping the chain, then land up tilt or up smash.
- **Fail:** CPU lands, jumps out or shines Fox.
- **Variations:** Fixed DI to learn each regrab type (standing, JC, pivot); port order
  swapped (changes the limits [wiki:Fox_(SSBM)/Up_throw]).
- **Data needed:** Up throw knockback, victim weight/fall speed, port priority, Fox grab
  ranges and jump-cancel grab timing.

### Shine spike the recovery

- **id:** `fox-shine-spike`
- **Goal:** Go offstage, land the one-frame shine and get back.
- **Player:** Fox
- **CPU:** [Falco](falco.md), [Fox](fox.md), [Captain Falcon](captain-falcon.md),
  [Marth](marth.md), [Sheik](sheik.md)
- **Setup:** CPU launched offstage at low percent with its double jump (variation:
  without); Fox on stage near the ledge.
- **CPU behaviour:** Recovers with a random option: double jump to ledge, side B
  (full/short) or up B at random angle for the space animals; up B for the others.
- **Success:** Shine connects offstage and Fox ends on stage or on the ledge; bonus if the
  CPU is KO'd.
- **Fail:** Fox dies, or the CPU reaches the ledge or stage untouched.
- **Variations:** Start from the ledge (drop-down shine with intangibility); require a
  ledge grab after the shine (shine turnaround edgehog); Armada shine only (hit during
  up B charge).
- **Data needed:** CPU recovery move timings (side B travel frame, up B charge frames),
  ledge intangibility timing, stage geometry (to avoid shining into the wall).

### Recovery mixups against an edgeguarder

- **id:** `fox-recovery-mixup`
- **Goal:** Return to stage against an opponent covering one option at a time.
- **Player:** Fox
- **CPU:** [Marth](marth.md), [Sheik](sheik.md), [Falco](falco.md)
- **Setup:** Fox offstage at a set position (high/level/low, with or without double
  jump) at 50-80%; CPU at the ledge.
- **CPU behaviour:** Picks one coverage at random: hold ledge, ledge-height attack timed
  for full-length side B, on-stage attack covering a high up B, or run-off aerial.
- **Success:** Fox grabs the ledge or lands and reaches an actionable state unhit.
- **Fail:** Fox is hit, or falls without grabbing the ledge.
- **Variations:** Force side B only and require a specific shortened length; walls for
  wall jump and wall tech.
- **Data needed:** Side B distances per shortened length, up B distance, ledge grab
  boxes, CPU move timings.

### Ledgedash with intangibility

- **id:** `fox-ledgedash`
- **Goal:** Get from ledge to stage with as many actionable intangible frames as possible
  (maximum 15 [wiki:Ledgedash]). See [ledgedash](../techniques/ledgedash.md).
- **Player:** Fox
- **CPU:** Any; [Marth](marth.md) and [Sheik](sheik.md) for realistic ledge traps
- **Setup:** Fox hanging on the ledge with fresh intangibility; CPU standing near the
  ledge.
- **CPU behaviour:** Attacks the ledge area on a timer or on Fox's first movement.
- **Success:** Fox is grounded and actionable with at least N intangible frames left and
  hits the CPU with an intangible move (up smash, grab, shine).
- **Fail:** Self-destruct, airdodge on stage without sliding, a normal ledge jump, or
  being hit.
- **Variations:** Yoshi's Story slanted edge; requirement of a specific follow-up.
- **Data needed:** Ledge intangibility (37 frames from grab, earliest drop frame 9
  [wiki:Ledgedash]), Fox double jump physics, stage ledge geometry.

### Shield pressure against shield grab

- **id:** `fox-shield-pressure`
- **Goal:** Hit a shield with an aerial and shine before the defender's grab or
  out-of-shield option comes out; then choose grab or retreat.
- **Player:** Fox
- **CPU:** [Marth](marth.md), [Sheik](sheik.md), [Peach](peach.md), [Fox](fox.md)
- **Setup:** CPU shielding at centre stage, Fox at dash-dance distance.
- **CPU behaviour:** After the aerial hits shield, does one of: shield grab on the first
  possible frame, hold shield, roll away, or its fastest out-of-shield attack (frame 4
  shine for Fox, frame 6 nair for Sheik [lib:A Dissection of Falco's Options on Shield]).
- **Success:** CPU's grab/attack is beaten by the shine, a held shield is shine-grabbed,
  or a roll is chased and punished.
- **Fail:** Fox is grabbed or hit.
- **Variations:** Nair versus dair; require late aerials; double shine.
- **Data needed:** Aerial shield stun and landing lag, CPU out-of-shield frame data, grab
  ranges.

### Jab reset or tech chase after shine

- **id:** `fox-shine-knockdown`
- **Goal:** React to tech versus missed tech after a grounded shine on a light character.
- **Player:** Fox
- **CPU:** [Fox](fox.md), [Falco](falco.md), [Pikachu](pikachu.md),
  [Jigglypuff](jigglypuff.md)
- **Setup:** CPU standing next to Fox at 0-50%; player lands a running shine.
- **CPU behaviour:** Randomly techs in place, techs toward, techs away or misses the tech;
  after a missed tech it randomly stays down, rolls or uses a getup attack.
- **Success:** Grab or up smash connects (via jab reset on a missed tech, or by following
  the tech).
- **Fail:** CPU returns to neutral or hits Fox.
- **Variations:** Percent above the pop-up threshold, where jab no longer resets; SDI up
  on the jab.
- **Data needed:** Tech and getup animation lengths and distances for each CPU character,
  jab knockback thresholds.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlFx.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/fox.json`](../framedata/fox.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 2-3 | 4 | 70 | 0 | 100 | - |  | 17 | 16 | 3 | -10 |  |
| Jab 2 | `jab2` | 3-4 | 4 | 70 | 0 | 100 | - |  | 20 | 19 | 3 | -12 | starts 1 frame late (included) |
| Rapid jab start | `rapid_jab_start` | - | - | - | - | - | - | - | 6 | - | - | - |  |
| Rapid jab loop | `rapid_jab_loop` | 2-3, 9-10, 16-17, 23-24, 30-31 | 1 | 78 | 10 | 80 | - |  | 35 | - | 2 | -31 |  |
| Rapid jab end | `rapid_jab_end` | - | - | - | - | - | - | - | 8 | - | - | - |  |
| Dash attack | `dash_attack` | 4-7 | 7 | 72 | 35 | 90 | - |  | 39 | 36 | 5 | -26 |  |
|  |  | 8-17 | 5 | 72 | 20 | 90 | - |  |  |  | 4 | -23 |  |
| Forward tilt (angled up) | `ftilt_high` | 5-8 | 9 | Sakurai | 0 | 100 | - |  | 26 | - | 6 | -15 |  |
| Forward tilt (slightly up) | `ftilt_mid_high` | 5-8 | 9 | Sakurai | 0 | 100 | - |  | 26 | - | 6 | -15 |  |
| Forward tilt | `ftilt` | 5-8 | 9 | Sakurai | 0 | 100 | - |  | 26 | - | 6 | -15 |  |
| Forward tilt (slightly down) | `ftilt_mid_low` | 5-8 | 9 | Sakurai | 0 | 100 | - |  | 26 | - | 6 | -15 |  |
| Forward tilt (angled down) | `ftilt_low` | 5-8 | 9 | Sakurai | 0 | 100 | - |  | 26 | - | 6 | -15 |  |
| Up tilt | `utilt` | 5-11 | 12/9 | 110/84/80 | 18 | 140 | - |  | 23 | 23 | 7 | -10 |  |
| Down tilt | `dtilt` | 7-9 | 10 | 70/80/90 | 25 | 125 | - |  | 29 | 28 | 6 | -14 |  |
| Forward smash | `fsmash` | 12-16 | 15 | Sakurai | 10 | 105 | - |  | 39 | - | 8 | -19 | charge hold frame 7 |
|  |  | 17-22 | 12 | Sakurai | 2 | 100 | - |  |  |  | 7 | -15 |  |
| Up smash | `usmash` | 7-9 | 18 | 80 | 30 | 112 | - |  | 41 | - | 10 | -24 | charge hold frame 2; partly intangible 1-9 (1 bone) |
|  |  | 10-17 | 13 | Sakurai | 10 | 100 | - |  |  |  | 7 | -24 |  |
| Down smash | `dsmash` | 6-10 | 15/12 | 25/Sakurai | 20 | 65 | - |  | 49 | 46 | 8 | -31 | charge hold frame 2; partly intangible 6 (4 bones) |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 4-7 | 12 | Sakurai | 10 | 100 | - |  | 49 | 42 | 7 | 15 | 7 | <4, >36 | +0 |  |
|  |  | 8-31 | 9 | Sakurai | 0 | 100 | - |  |  |  | 6 |  |  |  | -1 |  |
| Forward air | `fair` | 6-8 | 7 | Sakurai | 10 | 100 | - |  | 59 | 53 | 5 | 22 | 11 | <6, >48 | -6 |  |
|  |  | 16-18 | 5 | Sakurai | 10 | 100 | - |  |  |  | 4 |  |  |  | -7 |  |
|  |  | 24-26 | 6 | Sakurai | 10 | 100 | - |  |  |  | 4 |  |  |  | -7 |  |
|  |  | 33-35 | 4 | Sakurai | 10 | 100 | - |  |  |  | 3 |  |  |  | -8 |  |
|  |  | 43-45 | 3 | Sakurai | 50 | 100 | - |  |  |  | 3 |  |  |  | -8 |  |
| Back air | `bair` | 4-7 | 15/9 | Sakurai | 0 | 100 | - |  | 39 | 38 | 8 | 20 | 10 | <4, >22 | -2 |  |
|  |  | 8-19 | 9 | Sakurai | 0 | 100 | - |  |  |  | 6 |  |  |  | -4 |  |
| Up air | `uair` | 8-9 | 5 | 92 | 0 | 120 | 30 |  | 39 | 36 | 4 | 18 | 9 | <8, >25 | -5 |  |
|  |  | 11-14 | 13 | 85 | 40 | 116 | - |  |  |  | 7 |  |  |  | -2 |  |
| Down air | `dair` | 5-6, 8-9, 11-12, 14-15, 17-18, 20-21, 23-24 | 3/2 | 290 | 0 | 100 | 30 |  | 49 | - | 3 | 18 | 9 | <5, >30 | -6 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 12-13 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 5 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 7 | 3 | 45 | 35 | 130 | - | - | 11 | 33 |  |
| Back throw | `bthrow` | 2 | 2 | 56 | 80 | 85 | - | - | 9 | 38 | spawns article/projectile on 15, 18, 21 |
| Up throw | `uthrow` | 2 | 2 | 90 | 75 | 110 | - | - | 8 | 38 | spawns article/projectile on 18, 20, 24 |
| Down throw | `dthrow` | 1 | 1 | 270 | 150 | 40 | - | - | 33 | 43 | spawns article/projectile on 23, 25, 28, 31 |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Blaster (laser), ground, Start | `special_n_start` | - | - | - | - | - | - | - | 6 | - | - | - |  |
| Neutral B: Blaster (laser), ground, Loop | `special_n_loop` | - | - | - | - | - | - | - | 9 | - | - | - |  |
| Neutral B: Blaster (laser), ground, End | `special_n_end` | - | - | - | - | - | - | - | 23 | - | - | - |  |
| Neutral B: Blaster (laser), air, Start | `special_air_n_start` | - | - | - | - | - | - | - | 4 | - | - | - |  |
| Neutral B: Blaster (laser), air, Loop | `special_air_n_loop` | - | - | - | - | - | - | - | 9 | - | - | - |  |
| Neutral B: Blaster (laser), air, End | `special_air_n_end` | - | - | - | - | - | - | - | 21 | - | - | - |  |
| Side B: Fox Illusion (side B), ground, Start | `special_s_start` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Side B: Fox Illusion (side B), ground | `special_s` | - | - | - | - | - | - | - | 3 | - | - | - |  |
| Side B: Fox Illusion (side B), ground, End | `special_s_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Side B: Fox Illusion (side B), air, Start | `special_air_s_start` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Side B: Fox Illusion (side B), air | `special_air_s` | - | - | - | - | - | - | - | 3 | - | - | - |  |
| Side B: Fox Illusion (side B), air, End | `special_air_s_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Up B: Fire Fox, ground, Hold | `special_hi_hold` | 20, 22, 24, 26, 28, 30, 32 | 2 | 70 | 40 | 40 | - | fire | 42 | - | 2 | - |  |
| Up B: Fire Fox, ground, HoldAir | `special_hi_hold_air` | 20, 22, 24, 26, 28, 30, 32 | 2 | 70 | 40 | 40 | - | fire | 42 | - | 2 | - |  |
| Up B: Fire Fox, ground | `special_hi` | 1-29 | 14 | 80 | 60 | 60 | - | fire | 29 | - | 8 | - |  |
| Up B: Fire Fox, ground, Landing | `special_hi_landing` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Up B: Fire Fox, ground, Fall | `special_hi_fall` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Up B: Fire Fox, ground, Bound | `special_hi_bound` | - | - | - | - | - | - | - | 14 | - | - | - |  |
| Down B: Reflector (shine), ground, Start | `special_lw_start` | 1 | 5 | 0 | 0 | 100 | 80 | electric | 3 | - | 4 | - | intangible 1 |
| Down B: Reflector (shine), ground, Loop | `special_lw_loop` | - | - | - | - | - | - | - | 27 | - | - | - |  |
| Down B: Reflector (shine), ground, Hit | `special_lw_hit` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Down B: Reflector (shine), ground, End | `special_lw_end` | - | - | - | - | - | - | - | 17 | - | - | - |  |
| Down B: Reflector (shine), air, Start | `special_air_lw_start` | 1 | 5 | 0 | 0 | 100 | 80 | electric | 3 | - | 4 | - | intangible 1 |
| Down B: Reflector (shine), air, Loop | `special_air_lw_loop` | - | - | - | - | - | - | - | 27 | - | - | - |  |
| Down B: Reflector (shine), air, Hit | `special_air_lw_hit` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Down B: Reflector (shine), air, End | `special_air_lw_end` | - | - | - | - | - | - | - | 17 | - | - | - |  |

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
| Getup attack (face up) | `getup_attack_faceup` | intangible 1-26 | 17-19, 24-26 (6%) | 49 | - |  |
| Getup roll forward (face up) | `getup_roll_forward_faceup` | intangible 1-19 | - | 35 | - |  |
| Getup roll backward (face up) | `getup_roll_backward_faceup` | intangible 12-29 | - | 35 | - |  |
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
| Ceiling tech | `ceiling_tech` | intangible 2-14 | - | 26 | - | starts 1 frame late (included) |

### Ledge options

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Ledge grab | `ledge_catch` | intangible 1-7 | - | 7 | - |  |
| Ledge getup (>=100%) | `ledge_getup_slow` | intangible 1-55 | - | 59 | - |  |
| Ledge getup (<100%) | `ledge_getup` | intangible 1-30 | - | 34 | - |  |
| Ledge attack (>=100%) | `ledge_attack_slow` | intangible 1-53 | 57-59 (8/6%) | 69 | - |  |
| Ledge attack (<100%) | `ledge_attack` | intangible 1-21 | 25-34 (8/6%) | 54 | - |  |
| Ledge roll (>=100%) | `ledge_roll_slow` | intangible 1-62 | - | 79 | - |  |
| Ledge roll (<100%) | `ledge_roll` | intangible 1-34 | - | 49 | - |  |
| Ledge jump part 1 (>=100%) | `ledge_jump_slow_1` | intangible 1-19 | - | 19 | - |  |
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 32 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-14 | - | 14 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 37 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Down B (aerial) | jump | 4 | `special_air_lw_start` |
| Neutral air | jump | 7 | `nair` |
| Back air | jump | 7 | `bair` |
| Shield grab | direct | 7 | `grab` |
| Down air | jump | 8 | `dair` |
| Up smash | jump cancel | 8 | `usmash` |
| Forward air | jump | 9 | `fair` |
| Up air | jump | 11 | `uair` |
| Up B | jump cancel | 21 | `special_hi_hold` |
| Spot dodge | direct | intangible 2-15 of 22 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 15 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Fox indexed by [The Melee Library](https://www.meleelibrary.com/#fox) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Fox Melee Techs Guide](https://www.youtube.com/watch?v=MP7iGIjtShs&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=28&t=0s) | Third Chair | Video guide on performing useful Fox tech in 2020. |
| [Guide to Ace Arwing Pilot Fox McCloud](http://smashboards.com/guides/guide-to-ace-arwing-pilot-fox-mccloud-updated-for-2015.100/) | Cunning Kitsune | An extremely in-depth guide to everything Fox. |
| [Fox Hitboxes and Frame Data](http://smashboards.com/threads/complete-fox-hitboxes-and-frame-data.285177/) | Stratocaster, Standardtoaster, and SuperDoodleMan |  |
| [Fox Frame Data Visualization](http://imgur.com/a/g9niE) | Stormchicken |  |
| [Fox Trials](https://www.youtube.com/watch?v=t3rVxV3c2lg) | Ripple | A video demonstrating and explaining essential Fox tech. |
| [Is Samus the Secret to 20XX?](https://www.youtube.com/watch?v=la9-P29TdR8) | Reslived | An analysis of the Fox vs Samus matchup. It touches on a lot of different fundamental ideas about spacing and option coverage that most players/characters could learn to apply to their game. |
| [Fox Melee Chaingrab Guide](https://www.youtube.com/watch?v=rEbkN50SZOc&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=7&t=0s) | Third Chair | [Changes](http://www.ssbwiki.com/Fox_(SSBM)/Up_throw) due to port priority. |
| [Chaingrab Info](http://smashboards.com/threads/attn-fox-players.292187/#post-11682326) | KirbyKaze | [Changes](http://www.ssbwiki.com/Fox_(SSBM)/Up_throw) due to port priority. |
| [Lucky’s Favorite Fox Techniques](https://www.youtube.com/playlist?list=PLoU3TQBakHOqdcN4HWVDpVuYcO58Xf617) | SSBM Tutorials and Lucky | A playlist of videos showing Lucky’s favorite Fox techniques. |
| [How To Do Obscure Things with Fox](http://smashboards.com/threads/fluxs-how-to-do-obscure-things-w-fox-series-video-how-to-series.215002/) | Fluxwolf | Some Fox minutiae. |
| [Fox Edgehog Comparison](https://www.youtube.com/watch?v=62IDrqxCAPc) | mugg1991 | Compares the fastest ways for Fox to grab the ledge from far away. |
| [Waveshining](https://www.youtube.com/watch?v=_9FpTbwxuU0) | Ippo | Ippo goes over waveshine execution and what it can lead into. |
| [Punish Game on Spacies Tutorial (Basics)](https://www.youtube.com/watch?v=aeCH3GTPHeU) | SSBM Tutorials |  |
| Neutral Game Tutorial | SSBM Tutorials | [Part 1: Offense](https://www.youtube.com/watch?v=7euwVDL_In4) [Part 2: Defense](https://www.youtube.com/watch?v=S5WLjB8qOTE) |
| [How to Perform ALL of Fox’s Different Illusion Lengths](https://www.youtube.com/watch?v=EE_3XIc5d0k) | MikeHaze | Fox can shorten his side-b at different lengths. This is how you do them. |
| [Fox’s Invincible Ledgedash Options](https://www.youtube.com/watch?v=O0JQeVcpd_g) | Practical TAS | A video showcasing Fox’s options he can perform intangibly from a ledgedash. |
| [Fox's Invincible Ledge Options](https://www.youtube.com/watch?v=aCy8u-tALoU&) | SSBM Tutorials | An additional ledge option for Fox on Yoshi's story and Battlefield: no impact land with a laser. |
| [Compiled List of All Fox Tech](http://smashboards.com/threads/compiled-list-of-all-fox-tech-work-in-progress.415406/) | BRUJO | A work-in-progress post listing important tech skill to learn as Fox. Most of the items have links explaining the tech. For the rest, you can probably find in the Melee Library. |
| [First 5 Frames of Fox’s Tech Animations](http://imgur.com/a/v1Umh) | ??? | Useful for learning to tech chase. |
| [Solo Training Routine](https://www.reddit.com/r/SSBM/comments/3u4b69/cohenskis_solo_fox_training_routine/) | Cohenski | List of techskill to practice and learn as Fox. |
| [Fox vs Pikachu Match Analysis](https://www.youtube.com/watch?v=K7O4qBs9c78) | SFAT | SFAT discusses his approach to the Fox vs Pikachu matchup, one he is known for doing quite well in. |
| [Firefox Ledgestall Inputs gif](http://gfycat.com/InsignificantBriskBarracuda) | ??? |  |
| [Shinehog](https://www.youtube.com/watch?v=ZhqZQSgu0J0) | Garbanzo | Shine, jump, edge cancel advanced tech. |
| [How to Shorthop Double Laser](https://www.youtube.com/watch?v=YNLlAGhulRA) | SSBM Tutorials |  |
| [How to Practice Fox](https://www.youtube.com/watch?v=kXpQ9-TRop4) | SSBM Tutorials |  |
| [The Musician's Way to Successfully Land the Armada Shine](https://www.reddit.com/r/SSBM/comments/4bdzm8/the_musicians_way_to_successfully_land_the_armada/) | NanchoMan | NanchoMan describes a musical method based on rhythm pulses to land the Armada shine. |
| [Using Visual Cues to Help Land the Armada Shine](https://pbs.twimg.com/media/CeFp6wjUEAEgLJg.jpg:large) | Tai |  |
| [Multishine Guide](https://www.youtube.com/watch?v=5UUHAPWu2B8) | Lucky |  |
| [How to Laser Effectively](https://www.youtube.com/watch?v=mNC5ITn7MbA) | Remix | In this video, Remix looks at the multiple ways you can use Fox's blaster and their most effective uses. |
| [How to Perfect Ledgedash as Fox Part 1, [Part 2](https://www.youtube.com/watch?v=UZ579vLt6nY)](https://www.youtube.com/watch?v=w-Ysh9FWImc) | Remix |  |
| [Guaranteed Shield Poke on Full Shield Fox](https://www.youtube.com/watch?v=lzG5psgkrtg) | SleepyK | Some of Fox's hurtboxes extend slightly outside of his shield. You can use that to punish him while he's in full shield like SleepyK does with Falco's shine in this video. |
| [Escaping Sheik Techchases as Spacies](https://www.reddit.com/r/SSBM/comments/4yzyro/escaping_sheik_techchases_as_spacies/) | groating |  |
| [Fox 22 Frame Ledge Semi-Actionable Intangibility Frames on Yoshi Story](https://www.reddit.com/r/SSBM/comments/54ix9m/new_fox_22_frame_ledge_semiactionable/) | FaxxSSBM |  |
| [Short and Efficient Fox Practice Routine](https://www.youtube.com/watch?v=6UTIiuGAgWQ) | Remix | This Fox practice routine will ensure your techskill is crisp and efficient. |
| [Fox vs. Captain Falcon Matchup Guide](https://www.youtube.com/watch?v=r3T1Cck6vhg) | SSBM Tutorials |  |
| [Shine Shenanigans - Invisible Shine, Pseudo Shine, Shine Mine](https://www.youtube.com/watch?v=bttwseiNFpI) | Jib | Mostly silly shine tech. |
| [How To Waveshine Infinite As Fox](https://www.youtube.com/watch?v=2kQxkXiQg-k) | Remix |  |
| [Has the Fox - Jigglypuff matchup been solved??? SFat vs Hungrybox Analysis.](https://www.youtube.com/watch?v=XszU6TMxkIc) | Leffen |  |
| [Single Hit Up Air](https://stratsfoxstrats.blogspot.com/2016/11/single-hit-up-air.html) | Stratocaster | Stratocaster explains ways to hit with only the second hit of Fox's uair. |
| [Q&A - Rambling about Retreating Nair vs Marth](https://www.youtube.com/watch?v=4472IY3d3-M) | Leffen |  |
| [How to Beat Fox](https://www.youtube.com/watch?v=5ayp3eFIT28) | SSBM Tutorials |  |
| [Laser Land](https://www.youtube.com/watch?v=NNmaaFCFtLo) | KJH | Use the ECB distortions of neutral B to quickly board platforms. |
| [ECB manipulation via Firefox angles allows for easier techs](https://www.reddit.com/r/SSBM/comments/6kgtmc/ecb_manipulation_via_firefox_angles_allows_for/) | Gravy | The angle you approach the ledge with Firefox can make wall teching easier. |
| [The Fox Privilege Series: The Jigglypoke](https://www.youtube.com/watch?v=LhKR96Wgo2s) | KJH | A specific shield poke on Jigglypuff with Fox's uair. |
| [Fox VS Samus Matchup Guide](https://youtu.be/NMRvAAm2xlc) | Pipsqueak | Pipsqueak breaks down the Fox vs Samus matchup. |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Fox (SSBM): https://www.ssbwiki.com/Fox_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Fox_(SSBM)/Down_special , /Up_throw ,
  /Up_aerial , /Up_smash , /Side_special , /Up_special , /Neutral_special ,
  /Neutral_aerial , /Back_aerial , /Down_aerial , /Forward_aerial , /Dash_attack ,
  /Down_tilt , /Up_tilt , /Forward_tilt , /Forward_smash , /Down_smash , /Grab ,
  /Forward_throw , /Back_throw , /Down_throw
- SSBWiki technique pages: https://www.ssbwiki.com/Reflector_(Fox) ,
  https://www.ssbwiki.com/Waveshine , https://www.ssbwiki.com/Pillaring ,
  https://www.ssbwiki.com/Shine_spike , https://www.ssbwiki.com/Short_hop_laser ,
  https://www.ssbwiki.com/Fox_Illusion , https://www.ssbwiki.com/Fire_Fox ,
  https://www.ssbwiki.com/Ledgestall , https://www.ssbwiki.com/Ledgedash ,
  https://www.ssbwiki.com/Chain_grab , https://www.ssbwiki.com/Tech-chase ,
  https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- Melee Library, "Guide to Ace Arwing Pilot Fox McCloud" (Cunning Kitsune), via
  web.archive.org:
  http://smashboards.com/guides/guide-to-ace-arwing-pilot-fox-mccloud-updated-for-2015.100/
- Melee Library, "Chaingrab Info" (KirbyKaze), via web.archive.org:
  http://smashboards.com/threads/attn-fox-players.292187/
- Melee Library, "Single Hit Up Air" (Stratocaster):
  https://stratsfoxstrats.blogspot.com/2016/11/single-hit-up-air.html
- Melee Library (Falco section), "Falco optimal fastfall timing" (Druggedfox):
  https://portraitinsmash.blogspot.com/2015/12/falco-optimal-fastfall-timing.html
- Melee Library (Falco section), "A Dissection of Falco's Options on Shield" (Robotic
  Phish), via web.archive.org: http://peekand.co/editorials/dissection-falcos-options-shield/
- Melee Library (Falco section), "Multishine: An Extensive Guide" (Stratocaster), via
  web.archive.org:
  http://smashboards.com/threads/multishine-an-extensive-guide-updated-8-13-10.214549/
- Melee Library (Ganondorf section), "The Ganon Chaingrabbing Guide" (Magus) and
  "Techchasing into 2015: Metagame and Theory" (Ace), via web.archive.org
- Melee Library (Captain Falcon section), "Techchasing Like a Man: Complete Breakdown"
  (Gravy), via web.archive.org
- Frame data dump: `Fox.json`
