---
schema: melee-character/v1
id: falco
name: Falco
aliases: [Falco Lombardi, spacie, space animal, bird]
tier: "S (4th of 26), 2021 tier list"
archetype: [rushdown, projectile, fastfaller, glass-cannon, punish-heavy, technical]
related: [fox]
summary: Falco locks the opponent down with hitstun lasers, opens them with a laser-covered aerial or shine, and converts into long shine-and-down-air "pillar" combos that end in a spike, forward smash or edgeguard.
key_tech: [short-hop-laser, laser-approach, pillar-combo, shine-out-of-shield, shield-pillar-pressure, multishine, waveshine, dair-edgeguard, laser-reset, phantasm-shorten, firebird-ledge-stall, optimal-fastfall-aerial, ledgehop-double-laser, dthrow-on-fox]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlFc.dat
framedata: ../framedata/falco.json
code: src/melee/ft/kinds/ftFalco
specials:
  neutral_b: "Blaster (laser)"
  side_b: "Falco Phantasm (side B)"
  up_b: "Fire Bird"
  down_b: "Reflector (shine)"
attributes:
  weight: 80
  gravity: 0.17
  fall_speed: 3.1
  fast_fall_speed: 3.5
  jump_squat: 5
  jumps: 2
  walk_speed: 1.4
  dash_speed: 1.9
  run_speed: 1.5
  traction: 0.08
  air_speed: 0.83
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [2, 16, 4]
  jab2: [3, 19, 4]
  rapid_jab_start: [null, 7, 0]
  rapid_jab_loop: [2, 36, 1]
  rapid_jab_end: [null, 9, 0]
  dash_attack: [4, 36, 9]
  ftilt_high: [5, 27, 9]
  ftilt_mid_high: [5, 27, 9]
  ftilt: [5, 27, 9]
  ftilt_mid_low: [5, 27, 9]
  ftilt_low: [5, 27, 9]
  utilt: [5, 23, 9]
  dtilt: [7, 28, 13]
  fsmash: [12, 40, 17]
  usmash: [7, 44, 14]
  dsmash: [6, 46, 16]
  nair: [4, 42, 12]
  fair: [6, 53, 9]
  bair: [4, 38, 15]
  uair: [8, 36, 10]
  dair: [5, 50, 12]
  grab: [7, 31, 0]
  dash_grab: [12, 41, 0]
  pummel: [5, 25, 3]
  fthrow: [10, 34, 3]
  bthrow: [null, 39, 2]
  uthrow: [null, 39, 2]
  dthrow: [null, 44, 1]
  special_n_start: [null, 7, 0]
  special_n_loop: [null, 24, 0]
  special_n_end: [null, 27, 0]
  special_air_n_start: [null, 5, 0]
  special_air_n_loop: [null, 16, 0]
  special_air_n_end: [null, 22, 0]
  special_s_start: [null, 16, 0]
  special_s: [null, 4, 0]
  special_s_end: [null, 40, 0]
  special_air_s_start: [null, 16, 0]
  special_air_s: [null, 4, 0]
  special_air_s_end: [null, 40, 0]
  special_hi_hold: [null, 43, 0]
  special_hi_hold_air: [null, 43, 0]
  special_hi: [1, 30, 16]
  special_hi_landing: [null, 20, 0]
  special_hi_fall: [null, 20, 0]
  special_hi_bound: [null, 15, 0]
  special_lw_start: [1, 4, 8]
  special_lw_loop: [null, 28, 0]
  special_lw_hit: [null, 20, 0]
  special_lw_end: [null, 18, 0]
  special_air_lw_start: [1, 4, 8]
  special_air_lw_loop: [null, 28, 0]
  special_air_lw_hit: [null, 20, 0]
  special_air_lw_end: [null, 18, 0]
oos:  # option: frame the hitbox is out
  special_air_lw_start: 6
  grab: 7
  usmash: 8
  nair: 9
  bair: 9
  dair: 10
  fair: 11
  uair: 13
resources: 42
# generated: end
---

# Falco

<!-- GENERATED:attributes -->
## Attributes

Read from `PlFc.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 80 |
| Gravity | 0.17 |
| Terminal fall speed | 3.1 |
| Fast-fall speed | 3.5 |
| Jump squat (frames before airborne) | 5 |
| Full hop / short hop initial Y speed | 4.1 / 1.9 |
| Air jump Y multiplier | 0.94 |
| Jumps | 2 |
| Walk max speed | 1.4 |
| Dash initial speed / run max speed | 1.9 / 1.5 |
| Ground friction (traction) | 0.08 |
| Air max horizontal speed | 0.83 |
| Air acceleration (base + stick) | 0.02 + 0.05 |
| Air friction | 0.02 |
| Normal landing lag | 4 |
| Shield size | 12.5 |
<!-- /GENERATED:attributes -->

## Overview

Falco is Fox's clone: slower on the ground, heavier, and built around combos rather than
quick kills [wiki:Falco_(SSBM)]. He weighs 80, has the fastest fall speed in the game
(3.1, fast fall 3.5), a 5-frame jump squat (the grounded frames before a jump leaves the
floor), run speed 1.5 and by far the highest jump [wiki:Falco_(SSBM)]. He ranks 4th on the
2021 tier list [wiki:Falco_(SSBM)]. He wins neutral with neutral B (Blaster, "laser"),
which unlike Fox's causes hitstun: short hop lasers stop movement and let him follow with
dair, nair, grab or shine [wiki:Falco_(SSBM)/Neutral_special]. His down B (Reflector,
"shine") hits on frame 1, is jump-cancellable from frame 4 and launches straight up (angle
84, base knockback 110) at any percent, so it leads into dair, which spikes the opponent
back down into another shine; this loop is called pillaring
[wiki:Falco_(SSBM)/Down_special] [fd]. He kills with dair offstage, fsmash, bair and dtilt.
He dies early: he is light, the easiest character to chain grab and combo because of his
fall speed, and his recovery is among the worst in the game [wiki:Falco_(SSBM)].
Execution demands are high (fast-fall and L-cancel timing on every aerial, laser height
control).

## Strengths and weaknesses

- **Strengths:**
  - Laser with hitstun and effectively unlimited range on legal stages; controls
    neutral, interrupts approaches and recoveries [wiki:Falco_(SSBM)].
  - Shine launches every character into tumble at 0%, even when crouch cancelled (holding
    down to reduce knockback) [wiki:Falco_(SSBM)/Down_special].
  - Dair: hitbox frames 5-24, 12% clean, spikes for the whole duration in NTSC, cannot be
    escaped by SDI because it is a single hit [wiki:Falco_(SSBM)] [fd].
  - Strong finishers: fsmash (17%, kills around 90-110%
    [wiki:Falco_(SSBM)/Forward_smash]), dtilt (13%, kills some characters from 90%
    [wiki:Falco_(SSBM)/Down_tilt]), bair, down smash semi-spike.
  - Heavier than Fox with a faster fall, giving the 3rd best vertical survival
    [wiki:Falco_(SSBM)].
  - Good ledgedash: 14 actionable intangible frames at best [wiki:Ledgedash].
  - Longer grab range than Fox [wiki:Falco_(SSBM)].
- **Weaknesses:**
  - Recovery: up B (Fire Bird) travels about half as far as Fox's and has no hitbox while
    charging; side B (Phantasm) is shorter than Fox's [wiki:Falco_(SSBM)].
  - Fastest faller: chain grabbed and combo'd by much of the cast
    ([Marth](marth.md), [Peach](peach.md), [Fox](fox.md), [Sheik](sheik.md))
    [wiki:Falco_(SSBM)] [wiki:Chain_grab].
  - Slow run (1.5) and short wavedash; relies on lasers to move safely
    [wiki:Falco_(SSBM)].
  - Throws are DI-dependent, so grab is not a guaranteed kill or combo starter
    [lib:A Dissection of Falco's Options on Shield].
  - 5-frame jump squat makes shine out of shield and multishine slower than Fox's
    [wiki:Falco_(SSBM)].
  - Shine hitbox has less range than Fox's [wiki:Falco_(SSBM)].
  - Committing to a laser costs 20+ frames in which he cannot react
    [lib:Squid Inklings].

## Character tech

### Short hop laser

- **id:** `short-hop-laser`
- **What:** Firing one laser during a short hop and fast falling so that the landing
  cancels the blaster's end lag. See [short hop](../techniques/short-hop.md) and
  [fast fall](../techniques/fast-fall.md).
- **Inputs:** short hop, B, tap down to fast fall after the shot, land. Timing of B
  within the hop sets the laser's height.
- **Timing:** In the air the first shot comes out on frame 13 of the blaster and it can
  repeat every 16 frames; on the ground the first shot is frame 23
  [wiki:Falco_(SSBM)/Neutral_special] [wiki:Falco_(SSBM)]. Falco can fast fall a short
  hop from frame 13 of the hop [lib:Falco optimal fastfall timing]. Each laser does 3%
  with small set knockback [wiki:Falco_(SSBM)/Neutral_special]; on shield it causes only
  3 frames of shield stun [lib:A Dissection of Falco's Options on Shield].
- **Used for:** Stopping dash dances and approaches, forcing shield or jump, covering his
  own approach, adding damage. Low lasers hit crouchers and grounded opponents; high
  lasers catch jumps.
- **Common errors:** Full hop; firing too late so the laser is not out before landing;
  no fast fall (slow, floaty hop); always the same height and rhythm, which opponents
  powershield or jump over [lib:Squid Inklings].
- **Drill idea:** Target line on the CPU at a set height; count consecutive short hop
  lasers that hit within the height band with a fast fall and no grounded blaster lag.

### Laser approach

- **id:** `laser-approach`
- **What:** Using the hitstun of a low, late laser to cover the dash in and the next
  attack.
- **Inputs:** approaching short hop laser (drift forward), fast fall, land, then dash
  into grab / shine / SHFFL dair or nair, or laser again.
- **Timing:** The follow-up must arrive inside the laser's hitstun or shield stun, so the
  laser has to be the "latest, lowest possible" one; on a shield even shine cannot catch
  a buffered spot dodge after a laser [lib:A Dissection of Falco's Options on Shield].
  After a laser both players decide at once; Falco should vary the next action
  [lib:Squid Inklings].
- **Used for:** Opening opponents who try to move or attack; conditioning them to shield,
  which sets up aerial pressure or grab.
- **Common errors:** Laser too high (opponent ducks or dashes under and punishes; a
  ducked ledgehop laser cost a stock in a cited set [lib:Guide to Ace Arwing Pilot Fox
  McCloud]); predictable laser count; lasering at a range where the opponent can simply
  take the laser and hit him.
- **Drill idea:** CPU dash dances at mid range and reacts to a laser hit by shielding,
  jumping or attacking at random; success if Falco's follow-up hits or grabs within N
  frames of the laser connecting.

### Pillar combo

- **id:** `pillar-combo`
- **What:** The shine/dair loop: shine launches up, a rising or falling dair spikes the
  opponent back to the ground, shine again [wiki:Falco_(SSBM)/Down_aerial].
- **Inputs:** down B, jump (jump-cancel), dair, fast fall, L-cancel, down B, repeat.
  Substitute up tilt, nair, bair or a waveshine when the opponent's DI or percent moves
  them out of dair range.
- **Timing:** Shine: hitbox frame 1, jump-cancellable from frame 4, 8% [fd]
  [wiki:Falco_(SSBM)/Down_special]. Jump squat 5 frames [wiki:Falco_(SSBM)]. Dair hitbox
  frames 5-24; landing lag 18 frames, 9 when L-cancelled [fd]. At low percent a dair that
  spikes an airborne opponent into the ground only gives them normal landing lag (4
  frames for most characters), so the shine after it must be immediate
  [wiki:Falco_(SSBM)/Down_aerial].
- **Used for:** His main punish on every character; can lead to kills from very low
  percent when it ends in a dair offstage or fsmash [wiki:Falco_(SSBM)/Down_aerial].
- **Common errors:** Missed L-cancel; dair too early so Falco lands long after the
  opponent; jumping the wrong way after shine when the opponent DIs behind; opponent
  SDIs (taps the stick during hitlag) the shine or dair to shift out of range; staled
  shine on a prone opponent can cause "spooky stun" where they float and act early
  [wiki:Falco_(SSBM)/Down_special].
- **Drill idea:** CPU at 0-40% with random DI/SDI per hit; count shine and dair hits in
  one true combo; target N hits or a finisher (fsmash or offstage dair).

### Shine out of shield

- **id:** `shine-out-of-shield`
- **What:** Jump out of shield, shine on the first airborne frame. See
  [out of shield](../techniques/out-of-shield.md).
- **Inputs:** from shield: jump, down B as soon as Falco is airborne, then jump or
  wavedash out of the shine.
- **Timing:** Hits on frame 6 after shield stun (5 jump squat frames plus frame 1 shine)
  [lib:A Dissection of Falco's Options on Shield]. For comparison Fox's hits on frame 4
  and most grabs on frame 7 [lib:Falco optimal fastfall timing]
  [lib:A Dissection of Falco's Options on Shield].
- **Used for:** Punishing unsafe pressure and starting a full pillar combo from defence;
  countering a low-percent dair in the Falco ditto by jumping into it
  [lib:A Dissection of Falco's Options on Shield].
- **Common errors:** Opponent out of the small shine range; late shine (Falco rises and
  must use his double jump); attacker's own shine or jab arrives first.
- **Drill idea:** CPU pressures Falco's shield with a move that is -6 or worse; success
  if shine connects within N frames of shield stun ending and at least a dair follows.

### Shield pillar pressure

- **id:** `shield-pillar-pressure`
- **What:** Aerial on shield, shine, jump-cancel into the next aerial (or waveshine,
  grab, double shine). Pillaring in the shield-pressure sense [wiki:Pillaring].
- **Inputs:** SHFFL nair or dair on shield, down B, then one of: jump dair/nair,
  wavedash behind or back, jump-cancel grab, second shine.
- **Timing:** Nair is 0 on shield at best [wiki:Falco_(SSBM)/Neutral_aerial]; its
  advantage depends on when in the short hop it is input and when Falco fast falls (see
  optimal fast fall below). At -4 he has one frame of leniency to shine before a
  frame-perfect Falco shine out of shield; rolls are intangible from frame 4, so a late
  shine lets the defender roll away [lib:Falco optimal fastfall timing]. Dair has extra
  landing lag and is narrower; a missed L-cancel after dair leaves 18 frames
  [lib:A Dissection of Falco's Options on Shield] [fd].
- **Used for:** Wearing down shields for a shield poke, catching out-of-shield attempts,
  forcing rolls that he can chase. Because his throws are DI-dependent, the grab is a
  conditional mixup rather than the goal [lib:A Dissection of Falco's Options on Shield].
- **Common errors:** Aerial too high on the shield (shield grabbed); rhythm with a gap
  larger than the defender's fastest option; ignoring roll; nair into a crouch
  cancelling opponent (punishable up to about 60% by some top tiers
  [lib:A Dissection of Falco's Options on Shield]).
- **Drill idea:** CPU in shield chooses at random between shield grab, roll, spot dodge
  and its fastest out-of-shield move at its first free frame; success if every CPU
  attempt is beaten for N cycles.

### Multishine

- **id:** `multishine`
- **What:** Consecutive grounded shines by re-shining on the first airborne frame of the
  jump out of the previous shine [wiki:Reflector_(Fox)].
- **Inputs:** down B, jump, down B exactly when airborne, jump after landing, repeat.
  The B press comes 5 frames after the jump press [lib:Multishine: An Extensive Guide].
- **Timing:** Frame-perfect cycle for Falco: shine on 1, jump on 4, second shine on 9,
  airborne but jump-cancellable on 12-13 (jumping here burns the double jump), grounded
  on 14, earliest jump 15, third shine on 20; one shine every 11 frames, versus 8 for Fox.
  The jump window is 2 frames wider than Fox's [wiki:Reflector_(Fox)]. Each shine that
  hits adds 4 frames of hitlag, which delays the jump press but not the jump-to-B rhythm
  [lib:Multishine: An Extensive Guide].
- **Used for:** Shield pressure; double shine into grab or wavedash.
- **Common errors:** Double jump out of the second shine; B late (shine comes out in a
  rising short hop).
- **Drill idea:** Count grounded shines on a shielding CPU with at most 11-13 frames
  between hitboxes; fail on double jump.

### Waveshine

- **id:** `waveshine`
- **What:** [Wavedash](../techniques/wavedash.md) out of shine. For Falco it is a
  positioning tool: his shine sends up, so he does not get Fox's grounded follow-ups or
  the infinite [wiki:Waveshine].
- **Inputs:** down B, jump, airdodge diagonally into the ground on the first airborne
  frame.
- **Timing:** Earliest airdodge is frame 9 of the sequence (shine 1, jump 4, 5-frame jump
  squat) [wiki:Reflector_(Fox)].
- **Used for:** Following a launched opponent horizontally when they DI away, so the next
  jump reaches them; crossing behind a shield to avoid a shield grab; retreating to
  laser [wiki:Waveshine].
- **Common errors:** Airdodge too late (airborne dodge, long lag); sliding out of range
  because Falco's wavedash is short.
- **Drill idea:** CPU DIs the shine away; success if Falco waveshines toward them and
  lands the next aerial as a true combo.

### Dair edgeguard

- **id:** `dair-edgeguard`
- **What:** Spiking a recovering opponent with dair, usually by running or jumping off
  stage and returning with the double jump. See
  [edgeguarding](../techniques/edgeguarding.md).
- **Inputs:** run off or short hop off the ledge, dair timed over the opponent, double
  jump back (side B or up B if needed).
- **Timing:** Hitbox frames 5-24, 12% for frames 5-14 and 9% after; both hits spike
  (angle 290) in NTSC [fd] [wiki:Falco_(SSBM)/Down_aerial]. The long duration lets one
  dair cover several recovery timings.
- **Used for:** Early kills on anyone below the ledge; especially strong against
  [Fox](fox.md) and Falco, whose up B has a long charge [lib:Guide to Ace Arwing Pilot Fox
  McCloud].
- **Common errors:** Opponent [meteor cancels](../techniques/meteor-cancel.md) (it is a
  meteor in game terms [unverified]); going too deep to return; getting hit by an
  up B hitbox.
- **Drill idea:** CPU recovers low with a random timing; success if dair connects
  offstage and Falco returns; bonus on KO.

### Laser reset

- **id:** `laser-reset`
- **What:** Hitting an opponent who is lying on the ground after a missed tech with a
  laser; like a [jab reset](../techniques/jab-reset.md) it forces the stand-up animation
  [wiki:Falco_(SSBM)/Neutral_special].
- **Inputs:** low short hop laser onto the prone opponent, land, fsmash (or dair/grab).
- **Timing:** The laser must hit while the opponent is in the lying state and low enough
  to reach a prone body. Fsmash hits on frame 12 [fd] and must connect before the forced
  stand-up ends.
- **Used for:** Guaranteed fsmash after a missed tech; described as the most useful
  follow-up to the reset [wiki:Falco_(SSBM)/Forward_smash].
- **Common errors:** Laser too high; opponent techs (no reset possible).
- **Drill idea:** CPU misses the tech after a dair at mid percent; success if a laser
  resets and fsmash connects.

### Shortened Phantasm

- **id:** `phantasm-shorten`
- **What:** Pressing B during side B (Falco Phantasm) to stop early; four shortened
  lengths [wiki:Falco_(SSBM)/Side_special].
- **Inputs:** side B, then B on one of the 4 travel frames (the high-pitched sound marks
  the timing [wiki:Falco_Phantasm]).
- **Timing:** Falco starts moving on frame 17 and the hitbox is frames 18-21 (Fox: 21 and
  22-25) [lib:Guide to Ace Arwing Pilot Fox McCloud]
  [wiki:Falco_(SSBM)/Side_special]; ledge grab possible from frame 25; total 59 frames
  [wiki:Falco_(SSBM)/Side_special]. The aerial hit is a weak meteor (angle 270) [fd]
  [wiki:Falco_(SSBM)].
- **Used for:** Recovery mixup against moves timed for the full length (for example Marth
  jab, Falco down smash) [wiki:Falco_(SSBM)/Side_special]
  [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Common errors:** Too short and falls below the ledge with no jump; predictable side B
  every time [lib:7 Mistakes All Falcos Make] (card description only).
- **Drill idea:** Start offstage at a set distance; success if Falco grabs the ledge or
  lands at the marked point using the required shortened length.

### Firebird ledge stall

- **id:** `firebird-ledge-stall`
- **What:** Drop from ledge, double jump, up B back into the ledge to refresh ledge
  intangibility [wiki:Ledgestall].
- **Inputs:** from ledge: stick away/down to drop, double jump, up B aimed at the ledge.
- **Timing:** Earliest ledge drop is frame 9 of the grab, leaving 29 intangible frames;
  the ledge cannot be regrabbed for 29 frames. Falco must double jump for his stall (Fox
  need not). He has a 14-frame window after dropping to input up B and still be fully
  intangible [wiki:Ledgestall].
- **Used for:** Edgehogging through a recovery, waiting on ledge, mixing up the timing of
  getting up [lib:Squid Inklings].
- **Common errors:** No double jump (Fire Bird too low, dies); late drop (vulnerable
  frames).
- **Drill idea:** Count consecutive stalls with zero vulnerable frames.

### Optimal fast fall on aerials

- **id:** `optimal-fastfall-aerial`
- **What:** Fast falling before the aerial's hitbox connects (during its startup) instead
  of after hitlag, so the aerial lands lower and later and gives better frame advantage
  [lib:Falco optimal fastfall timing].
- **Inputs:** short hop, nair on frame 10-15 of the hop, hold down so the fast fall
  starts on frame 13 of the hop (a 3-frame buffer exists when down is held early),
  L-cancel.
- **Timing:** Nair input on short hop frame 10 gives -3 on shield with the early fast
  fall versus -4 with a fast fall after hitlag; frame 11: -2 versus -4; frame 12: -1
  versus -3; frame 15: 0. With the after-hitlag method 0 is only reached by inputting
  nair on frame 20 [lib:Falco optimal fastfall timing].
- **Used for:** Making approaching nairs tie or beat shine out of shield and deny rolls
  [lib:Falco optimal fastfall timing].
- **Common errors:** Pressing down during hitlag (ignored, no fast fall); fast falling so
  early the aerial has no hitbox before landing.
- **Drill idea:** CPU shields then shines out of shield frame-perfectly; success if
  Falco's shine after nair hits first or trades.

### Ledgehop double laser

- **id:** `ledgehop-double-laser`
- **What:** Dropping from the ledge, double jumping and firing two lasers while rising
  onto the stage.
- **Inputs:** drop from ledge, double jump toward stage, B, B, land. Exact frame windows:
  Unknown (video-only sources).
- **Timing:** Uses ledge intangibility for the start of the jump; the lasers must be low
  enough to hit a standing opponent. Opponents who expect it duck under high lasers and
  punish [lib:Guide to Ace Arwing Pilot Fox McCloud]; overusing it is a listed common
  mistake [lib:7 Mistakes All Falcos Make] (card description only).
- **Used for:** Getting off the ledge while forcing the opponent to shield or get hit.
- **Common errors:** Lasers too high; landing with blaster lag; predictable timing.
- **Drill idea:** CPU stands near the ledge and randomly shields, crouches or attacks the
  ledge; success if both lasers come out and Falco lands unhit.

### Down throw on Fox (NTSC)

- **id:** `dthrow-on-fox`
- **What:** Against Fox in NTSC the last laser of Falco's down throw overrides the throw's
  knockback, so Fox cannot tech it and Falco gets true follow-ups or a pseudo chain grab
  [wiki:Falco_(SSBM)/Down_throw].
- **Inputs:** grab, down throw, then regrab, shine or dtilt.
- **Timing:** Works from 0% to about 40%; Fox escapes by DI'ing down and shining as early
  as possible. Does not work in PAL (Fox weighs 73 there)
  [wiki:Falco_(SSBM)/Down_throw].
- **Used for:** Low-percent damage on Fox from grab.
- **Common errors:** Slow regrab (Fox shines first).
- **Drill idea:** CPU Fox at 0-40% DIs down and shines at first chance on a random
  subset of throws; count regrabs or shine follow-ups.

## Neutral game

- **Lasers first.** Short hop lasers from mid and long range force the opponent to
  shield, jump or powershield (see [powershield](../techniques/powershield.md)). Falco
  reads their response and punishes it [lib:Squid Inklings].
- **Laser, then dash dance.** A reactive style: after a laser, retreat, hold ground or
  move in based on what the opponent does (for example bait Sheik's nair out of shield
  and punish it) [lib:Squid Inklings]. Dash dancing keeps more options available than
  another laser does [lib:Squid Inklings].
- **Aerial approach behind a laser:** dair beats crouch cancel and ASDI down; nair is
  safer on shield and pops airborne opponents up but loses to crouch cancel
  [lib:A Dissection of Falco's Options on Shield].
- **Dair** as an opener at low percent combos into shine or dtilt
  [wiki:Falco_(SSBM)/Down_aerial]. Against a crouching Fox at 0%, an early-hitting
  SHFFL dair is -12 on hit; it must hit late in the jump
  [wiki:Falco_(SSBM)/Down_aerial].
- **Bair** (15% clean, autocancels in a short hop [wiki:Falco_(SSBM)]) and **up tilt**
  (frames 5-11, large hitbox behind him [wiki:Falco_(SSBM)/Up_tilt]) are his anti-air
  and spacing moves.
- **Shine** approaches are used in some matchups (notably Ice Climbers) at the cost of
  the double jump when done in the air [lib:A Dissection of Falco's Options on Shield].
- **Platforms:** high jump and fast fall let him drop through platforms with lasers and
  aerials [lib:Squid Inklings].
- He wants centre stage at all times: losing the stage means recovering, which is his
  worst situation [wiki:Falco_(SSBM)].

## Punish game

Falco's punishes are long. Almost every opener (laser into shine, dair, nair, up tilt,
grab) leads to shine, and shine leads to dair, up tilt, bair or nair depending on DI. He
ends with fsmash on stage, dair or bair offstage, or a knockdown that he covers with a
laser reset or tech chase.

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| Shine | All | any (launches at 0%) | Jump dair, then shine again | Core pillar loop; follow DI with waveshine | [wiki:Falco_(SSBM)/Down_special] |
| Shine | All | mid | Jump-cancelled bair or nair | Sends offstage for an edgeguard | [wiki:Falco_(SSBM)/Back_aerial] |
| Dair (grounded opponent) | All | low | Shine or dtilt | Direct combo at low percent | [wiki:Falco_(SSBM)/Down_aerial] |
| Dair (grounded opponent) | All | mid-high | Fsmash | Fsmash covers tech and getup options | [wiki:Falco_(SSBM)/Forward_smash] |
| Late nair | Most | low-mid | Shine, grab, nair or dair | | [wiki:Falco_(SSBM)/Neutral_aerial] |
| Late (weak) bair | Crouch cancelling opponents | low | Shine | Sakurai angle keeps them grounded | [wiki:Falco_(SSBM)/Back_aerial] |
| Up tilt | Fastfallers, heavies | low-mid | Up tilt, shine, bair, dair, sometimes fsmash | Base knockback 30, growth 120 | [wiki:Falco_(SSBM)/Up_tilt] [fd] |
| Laser | Any (standing) | any | Grab, shine or fsmash | Only if the laser is low and late | [wiki:Falco_(SSBM)/Neutral_special] |
| Laser (prone opponent) | Any after a missed tech | any | Fsmash | Laser reset | [wiki:Falco_(SSBM)/Neutral_special] |
| Down throw | Fox (NTSC) | 0-40% | Regrab, shine, dtilt | Fox escapes with DI down and shine | [wiki:Falco_(SSBM)/Down_throw] |
| Down throw | Others | any | Tech chase (throw is techable) | Combos into dtilt or shine on a missed tech | [wiki:Falco_(SSBM)] |
| Up throw | Varies | DI-dependent | Up air, shine | The throw's lasers can be SDI'd | [wiki:Falco_(SSBM)] |
| Up tilt / up air / aerial shine | Floaties | mid-high | Up B (Fire Bird) | Situational top-blastzone kill | [wiki:Falco_(SSBM)/Up_special] |
| Down smash sourspot | Any | any | Up smash | Hit near his body sends straight up weakly | [wiki:Falco_(SSBM)/Down_smash] |

### Chain grabs and tech chases

- No reliable chain grab [wiki:Falco_(SSBM)]. The exceptions are the down throw
  pseudo chain grab on NTSC Fox (0-40%) [wiki:Falco_(SSBM)/Down_throw] and fthrow on some
  floaty characters [wiki:Falco_(SSBM)].
- **Tech chases** come from dair knockdowns and down throw. Covering options: fsmash
  (long active window, frames 12-21 [fd]) covers tech in place and getup; dair or
  another shine covers tech toward him; a laser covers tech away or resets a missed tech
  [wiki:Falco_(SSBM)/Forward_smash] [wiki:Falco_(SSBM)/Neutral_special].
- **Platforms:** up air's tall second hit lets him cover a fastfaller teching on a
  platform above while staying below it [wiki:Falco_(SSBM)/Up_aerial].
- Fthrow at high percent is a tech-chase starter and resets his laser game; unlike Fox's
  it is weight-dependent, so some of Fox's low-percent gimp setups do not transfer
  [wiki:Falco_(SSBM)/Forward_throw].

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| Fsmash | Most | around 90-110% | Clean hit; deadlier at the ledge | [wiki:Falco_(SSBM)/Forward_smash] |
| Dair (spike) | Anyone offstage or below the ledge | from very low percent (combos can kill by about 30%) | Opponent must be offstage; meteor cancel possible | [wiki:Falco_(SSBM)/Down_aerial] |
| Dtilt | Some characters (light floaties) | from about 90% fresh | Short range, sends up | [wiki:Falco_(SSBM)/Down_tilt] |
| Bair (clean) | Most | Unknown ("realistic percents" on small stages) | Side or top blastzone | [wiki:Falco_(SSBM)/Back_aerial] |
| Down smash | Most | Unknown (edgeguard) | 16%, 25-degree semi-spike at the ledge | [wiki:Falco_(SSBM)/Down_smash] [fd] |
| Up air | Floaties | Unknown | Low ceilings (Yoshi's Story, Pokemon Stadium); second hit has a weak sourspot | [wiki:Falco_(SSBM)/Up_aerial] |
| Up B (Fire Bird) | Floaties | mid-high | After up tilt / up air / aerial shine; DI-dependent | [wiki:Falco_(SSBM)/Up_special] |
| Shine | Floaties | Unknown | Top blastzone on low ceilings (the wiki calls up air an alternative to shine for this) | [wiki:Falco_(SSBM)/Up_aerial] |

- **Kill setups:** pillar into fsmash; dair knockdown into fsmash; laser reset into
  fsmash; shine into bair toward the blastzone; shine into dair at the ledge.
- **Edgeguards:** dair and bair offstage; down smash, fsmash and dtilt at the ledge;
  nair's long duration hits both immediate and delayed recoveries
  [wiki:Falco_(SSBM)/Neutral_aerial]. Lasers fired from the ledge repeatedly knock
  [Captain Falcon](captain-falcon.md) and [Ganondorf](ganondorf.md) out of their jumps
  and force them to recover again and again [wiki:Blaster_(Falco)]; fsmash covers their
  choice between ledge and stage [wiki:Falco_(SSBM)/Forward_smash]. Lasers also clip a
  space animal's double jump and force a low up B [lib:Guide to Ace Arwing Pilot Fox
  McCloud].

## Recovery

- **Options:**
  - Double jump (Falco's jumps are the highest in the game [wiki:Falco_(SSBM)]).
  - Side B (Phantasm): fast horizontal dash, moves on frame 17, four shortened lengths,
    shorter than Fox's; his main recovery [wiki:Falco_(SSBM)/Side_special].
  - Up B (Fire Bird): no hitbox during the charge, 16% travel hitbox on frames 43-64,
    total 84 frames, about half the distance of Fox's
    [wiki:Falco_(SSBM)/Up_special] [wiki:Falco_(SSBM)].
  - Shine stall to change fall timing [wiki:Reflector_(Fox)]; wall jump (much higher
    than Fox's) [wiki:Falco_(SSBM)].
- **Mixups:** side B to ledge versus onto stage, shortened versus full; up B angle
  (the short distance makes the ledge easy to sweetspot and leaves little time to react
  to the chosen angle when he is close) [wiki:Falco_(SSBM)/Up_special]; double jump
  timing; fast options out of a wall tech [wiki:Falco_(SSBM)].
- **Weaknesses:** Cannot recover from far or low. Up B is vulnerable for all 42 startup
  frames with nothing to protect him. Side B is linear and loses to any hitbox on its
  line. Low air speed [wiki:Falco_(SSBM)].

### Edgeguarding Falco

- **Push him below the ledge** so that side B is no longer possible; he then has to
  double jump or up B [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Up B:** hit him during the charge with anything; spikes and meteors (Marth dair,
  Falco dair) are fatal; Marth's Counter, Link's up B and Mario's cape beat the travel
  [wiki:Falco_(SSBM)]. Or hold the ledge: the short distance often leaves him unable to
  reach the stage.
- **Side B:** place a hitbox at ledge height at the arrival time. Down smash and up tilt
  at the ledge, rising nair/bair, a late-hitting soft knee
  [wiki:Captain_Falcon_(SSBM)/Forward_aerial], Marth's jab [wiki:Falco_(SSBM)/Side_special]
  and low tilts all work. It arrives 4 frames sooner than Fox's
  [lib:Guide to Ace Arwing Pilot Fox McCloud]; the startup sound is the cue. Beware the
  weak meteor on its aerial hit [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Shine spike** from [Fox](fox.md) kills at any percent; a nair that grazes him sets it
  up [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **CPU-as-Falco recovery policy:** above ledge and within range: side B (full or
  shortened, to ledge or stage). Below ledge: double jump then side B if height allows,
  otherwise up B with a varied angle. Very far: dead.

## Defense and out of shield

- **Out of shield:** shine (frame 6), shield grab (frame 7), up smash (frame 8)
  [lib:A Dissection of Falco's Options on Shield]; nair/bair (5 jump squat frames then
  frame 4 hitbox [wiki:Falco_(SSBM)] [fd]); wavedash out; roll (his rolls travel further
  than Fox's [wiki:Falco_(SSBM)]). Shield drop aerials on platforms (see
  [shield drop](../techniques/shield-drop.md)).
- **Crouch cancel / ASDI down into shine:** at low percent he can hold down through weak
  aerials and shine. Against Sheik's autocancelled fair, ASDI down into shine works
  until about 20%; after that he slides too far unless he fully crouch cancels, where
  dtilt or grab may be the better answer [lib:Squid Inklings].
- **Combo escapes:** frame 1 shine (intangible on frame 1) as soon as hitstun ends; it
  also works out of a tech in place and beats grabs [wiki:Falco_(SSBM)/Down_special].
  Double jump (very high). DI and SDI.
- **Shield weakness:** his head is not fully covered by his shield, which makes him easy
  to shield poke from above (for example Ganondorf bair)
  [wiki:Ganondorf_(SSBM)/Back_aerial]. Rolls should not be dismissed: they are
  bufferable and intangible early [lib:Squid Inklings].
- **Powershield** rather than shine to reflect projectiles on the ground: shine cannot
  be jump-cancelled while reflecting [wiki:Falco_(SSBM)/Down_special].

## As the training dummy

- **Class:** light-middle (weight 80), fastest faller (3.1 / 3.5)
  [wiki:Falco_(SSBM)]. Falls over from Fox's shine (weight below 87) [wiki:Waveshine].
- **Chain grabbed by:** [Marth](marth.md) up throw, 0 to about 60% [wiki:Chain_grab];
  [Fox](fox.md) up throw, 0-66% regardless of DI (0-81% if Falco has the lower port), up
  to 103% if he DIs fully sideways [wiki:Fox_(SSBM)/Up_throw], or in practice 0-55%
  and about 80% with DI away [lib:Chaingrab Info]; [Peach](peach.md) up throw; Mario and
  Dr. Mario up throw; Donkey Kong up throw and cargo up throw; Mewtwo down throw
  [wiki:Chain_grab]; [Ganondorf](ganondorf.md) down throw from 12% (pre-throw) to death
  [lib:The Ganon Chaingrabbing Guide].
- **Tech chased / regrabbed by:** [Captain Falcon](captain-falcon.md): up throw regrabs
  work from 40% to 126% with no DI, 32-123% with DI slightly behind, 40-139% with DI
  straight behind; DI straight away avoids regrabs except around 130-135% and avoids the
  knee until about 130% [lib:Uthrow Followups on Falco]. Falcon's down throw is the better
  tech-chase throw until about 50%, up throw after; Falco can jump out of up throw from
  about 90% (70% frame-perfect) [lib:Techchasing Like a Man: Complete Breakdown].
  [Sheik](sheik.md) down throw tech chases him [wiki:Chain_grab].
- **Strong DI for a realistic CPU:** Falcon's up throw: straight away, then tech or jump
  [lib:Uthrow Followups on Falco]. Fox's and Marth's up throw: none or slight (full
  side DI extends the chain) [lib:Chaingrab Info]. Ganondorf's down throw: slightly away
  so he goes straight up and can jump out at the end of the range
  [lib:The Ganon Chaingrabbing Guide].
- **Knockdown thresholds (fresh moves):** Ganondorf jab 39%, ftilt 23%, dtilt 18%, dash
  attack 12% [lib:Techchasing into 2015: Metagame and Theory]. Fox's nair knocks down at
  about 40%, dash attack about 50%, fair 68% [wiki:Fox_(SSBM)/Up_throw].
- **Jab reset:** a jabbed prone Falco stands up below 52-55% and pops up above it
  according to the Fox guide [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Getup attack:** Fox can crouch cancel it until about 90% and punish with fsmash
  [lib:Guide to Ace Arwing Pilot Fox McCloud].
- **Tech choices:** mix all four; tech in place into shine beats slow coverage; he can
  SDI Fox's shine up to make the tech easier [lib:Guide to Ace Arwing Pilot Fox McCloud].

## Matchup notes

### vs Fox

- Falco limits Fox with lasers and converts openings into shine combos and dair/down
  smash/bair edgeguards; Fox is faster, chain grabs him and gimps him at low percent
  [lib:Guide to Ace Arwing Pilot Fox McCloud].
- Fox falls from shine, so Falco's shine on a grounded Fox still launches (Falco's shine
  tumbles everyone [wiki:Falco_(SSBM)/Down_special]), and down throw gives the NTSC
  pseudo chain grab [wiki:Falco_(SSBM)/Down_throw].
- Fox's shine out of shield (frame 4) is 2 frames faster than Falco's; aerials on Fox's
  shield need the best possible frame advantage [lib:Falco optimal fastfall timing].

### vs Marth

- Marth chain grabs Falco with up throw to about 60% and edgeguards both recovery moves
  with jab, Counter and dair [wiki:Chain_grab] [wiki:Falco_(SSBM)].
- Falco's lasers stop Marth's dash dance; pillars work at any percent. Marth's shield
  does not cover his head fully, so high aerials poke
  [wiki:Ganondorf_(SSBM)/Back_aerial].

### vs Sheik

- Lasers force Sheik to shield; bait her nair out of shield (frame 6) and punish
  [lib:Squid Inklings] [lib:A Dissection of Falco's Options on Shield].
- Sheik's down throw tech chase and fair/needle edgeguards are the danger. ASDI down
  into shine against her fair works to about 20% [lib:Squid Inklings].

### vs Jigglypuff

- Up air and shine are the vertical kill tools on low ceilings
  [wiki:Falco_(SSBM)/Up_aerial]; dtilt kills light floaties from about 90%
  [wiki:Falco_(SSBM)/Down_tilt].
- Puff's rise on the 2021 tier list is given as one reason Falco dropped two places
  [wiki:List_of_SSBM_tier_lists_(NTSC)].

### vs Peach

- Peach chain grabs him with up throw and can throw a Stitch Face turnip; shine in the
  air reflects it [wiki:Falco_(SSBM)/Down_special] [wiki:Chain_grab]. A long pillar on
  Peach (16 hits, 123%) is cited as the showcase of the combo [wiki:Pillaring].

### vs Captain Falcon

- Falcon tech chases and regrabs him from up throw across a huge percent range
  [lib:Uthrow Followups on Falco]. Falco gimps Falcon with repeated ledge lasers and
  fsmash [wiki:Blaster_(Falco)] [wiki:Falco_(SSBM)/Forward_smash].

### vs Falco (ditto)

- Jumping out of shield into a low-percent dair to land a counter shine is a key
  defensive trick [lib:A Dissection of Falco's Options on Shield]. Whoever shines first
  gets a pillar; dair edgeguards end stocks early.

## Drill seeds

### Shine out of shield into pillar

- **id:** `falco-shine-oos`
- **Goal:** Punish shield pressure with a frame 6 shine and start a combo.
- **Player:** Falco
- **CPU:** [Marth](marth.md) (fsmash, fair), [Fox](fox.md) (nair, drill),
  [Sheik](sheik.md) (ftilt, fair), [Falco](falco.md) (dair)
- **Setup:** Final Destination centre; Falco in shield; CPU in attack range; both at a
  chosen percent.
- **CPU behaviour:** Hits the shield with the chosen move at random spacing/timing, then
  performs its usual follow-up (jab, shine, second swing) at the first free frame.
- **Success:** Shine connects within N frames of shield stun ending (6 is perfect) and a
  dair or other aerial hits as a true combo.
- **Fail:** Falco is hit or grabbed, shine whiffs, or he double jumps away.
- **Variations:** Moves that are safe against frame 6 (correct answer: hold shield or
  roll); low-percent Falco ditto dair where jumping into it is the answer.
- **Data needed:** CPU move shield stun/advantage, Falco jump squat (5), shine hitbox
  size.

### Pillar combo with DI

- **id:** `falco-pillar`
- **Goal:** Keep a shine/dair combo going against changing DI and finish it.
- **Player:** Falco
- **CPU:** [Fox](fox.md), [Captain Falcon](captain-falcon.md), [Marth](marth.md),
  [Sheik](sheik.md), [Peach](peach.md)
- **Setup:** CPU standing next to Falco at 0-30%, flat stage or Battlefield.
- **CPU behaviour:** Random DI on every shine (in, away, behind, none); optional SDI;
  techs randomly when knocked down; jumps/attacks at the first actionable frame.
- **Success:** At least N consecutive hits registered as one combo and a finisher (fsmash
  or a hit that sends the CPU offstage).
- **Fail:** CPU becomes actionable and escapes or hits Falco.
- **Variations:** Fixed DI to learn each branch (DI away needs waveshine or full hop dair;
  DI in needs up tilt or turnaround); platform stages.
- **Data needed:** Shine knockback (angle 84, base 110, growth 50 [fd]) per weight and
  fall speed, dair landing lag, hitstun formula.

### Laser pressure into opener

- **id:** `falco-laser-approach`
- **Goal:** Use laser hitstun to land a grab, shine or aerial.
- **Player:** Falco
- **CPU:** [Marth](marth.md), [Sheik](sheik.md), [Fox](fox.md),
  [Captain Falcon](captain-falcon.md)
- **Setup:** Final Destination, characters about half a stage apart.
- **CPU behaviour:** Dash dances; on each laser randomly takes it and attacks, shields,
  jumps over, or powershields (low probability).
- **Success:** A non-laser hit or grab connects within N frames of a laser hit or
  shielded laser.
- **Fail:** Falco is hit, or fires more than M lasers without converting.
- **Variations:** Required laser height (low only); CPU that punishes any repeated
  laser count.
- **Data needed:** Laser speed, hitstun and shield stun, aerial blaster frame data
  (first shot frame 13), Falco short hop duration.

### Shield pressure against out-of-shield options

- **id:** `falco-shield-pressure`
- **Goal:** Hit a shield with nair or dair and shine before the defender can act.
- **Player:** Falco
- **CPU:** [Fox](fox.md) (shine out of shield frame 4), [Sheik](sheik.md) (nair frame
  6), [Marth](marth.md) (up B frame 6, grab frame 7), [Falco](falco.md)
  [lib:A Dissection of Falco's Options on Shield]
- **Setup:** CPU shielding at centre stage; Falco one short hop away.
- **CPU behaviour:** At its first free frame after shield stun chooses at random: fastest
  out-of-shield attack, shield grab, roll, or hold shield.
- **Success:** Falco's shine hits the CPU or its shield before the CPU's option becomes
  active, for N cycles; rolls are followed and punished.
- **Fail:** Falco is hit or grabbed.
- **Variations:** Require the early fast-fall timing (nair input on short hop frames
  10-15); dair only; shine-grab and waveshine-behind mixups.
- **Data needed:** Table of nair frame advantage by input frame
  [lib:Falco optimal fastfall timing], CPU out-of-shield frame data.

### Dair edgeguard

- **id:** `falco-dair-edgeguard`
- **Goal:** Spike a recovering opponent and return to the stage.
- **Player:** Falco
- **CPU:** [Fox](fox.md), [Falco](falco.md), [Marth](marth.md),
  [Captain Falcon](captain-falcon.md), [Sheik](sheik.md)
- **Setup:** CPU launched offstage at 30-60% with or without a double jump; Falco at the
  ledge.
- **CPU behaviour:** Recovers with a random legal option and timing (side B, up B angle,
  double jump to ledge); meteor cancels at a configurable rate.
- **Success:** Dair (or bair) connects offstage and Falco returns; KO preferred.
- **Fail:** CPU grabs the ledge or lands; Falco dies.
- **Variations:** Stay on stage and use down smash/fsmash instead; ledge laser first to
  remove the double jump.
- **Data needed:** Dair hitbox frames 5-24, CPU recovery timings, Falco double jump
  height.

### Recover against an edgeguarder

- **id:** `falco-recovery`
- **Goal:** Choose and execute the right recovery from each offstage position.
- **Player:** Falco
- **CPU:** [Marth](marth.md), [Fox](fox.md), [Sheik](sheik.md)
- **Setup:** Falco offstage at ledge height or slightly below, 40-80%, with double jump.
- **CPU behaviour:** Randomly holds the ledge, swings at ledge height timed for a
  full-length side B, or jumps out for an aerial.
- **Success:** Falco grabs the ledge or lands and is actionable.
- **Fail:** Hit or falls.
- **Variations:** Require a specific shortened Phantasm; no double jump; start below the
  ledge (up B only).
- **Data needed:** Phantasm distances per shortened length, Fire Bird distance, ledge
  grab timing (side B can grab from frame 25).

### Laser reset into forward smash

- **id:** `falco-laser-reset`
- **Goal:** React to a missed tech with a low laser and fsmash.
- **Player:** Falco
- **CPU:** Any; [Sheik](sheik.md), [Marth](marth.md), [Fox](fox.md)
- **Setup:** CPU at 60-100% is hit by a dair on the ground a short distance from Falco.
- **CPU behaviour:** Randomly techs (in place/in/away) or misses the tech; after a
  missed tech waits a random time before getting up.
- **Success:** On a missed tech: laser hits the prone CPU and fsmash connects. On a tech:
  any punish connects.
- **Fail:** CPU gets up freely.
- **Variations:** Platform knockdowns; higher percents where the kill is required.
- **Data needed:** Prone hurtbox height per character, missed-tech and getup timings,
  laser height from a short hop.

### Ledgedash

- **id:** `falco-ledgedash`
- **Goal:** Ledgedash with at least 10 actionable intangible frames. See
  [ledgedash](../techniques/ledgedash.md).
- **Player:** Falco
- **CPU:** Any standing near the ledge.
- **Setup:** Falco on the ledge after a sweetspot side B, a Fire Bird ledge stall or a
  down-angled sweetspot up B (the recommended ledge-grab states; grabbing from an up B
  from below changes his collision shape and makes normal timings self-destruct)
  [lib:Falco Ledgedash Timing and Intangibility].
- **CPU behaviour:** Attacks the ledge on a timer.
- **Success:** Falco is grounded and actionable with 10 or more intangible frames left
  (the guide's target; maximum 14 [wiki:Ledgedash]) and lands an intangible grab, dtilt,
  shine or up smash.
- **Fail:** Self-destruct, airborne airdodge, or hit.
- **Variations:** Drop without fast fall (slow arcing stick motion) versus with fast
  fall [lib:Falco Ledgedash Timing and Intangibility].
- **Data needed:** Ledge intangibility timing, Falco double jump physics, stage edge
  geometry.

### Escape chain grabs and tech chases

- **id:** `falco-cg-escape`
- **Goal:** Learn the DI and tech choices that end each opponent's grab punish.
- **Player:** Falco
- **CPU:** [Marth](marth.md) (up throw), [Fox](fox.md) (up throw),
  [Captain Falcon](captain-falcon.md) (up/down throw), [Sheik](sheik.md) (down throw)
- **Setup:** Falco held in grab at a chosen percent, Final Destination.
- **CPU behaviour:** Throws and attempts the standard regrab or follow-up.
- **Success:** Falco lands, jumps out or shines before being regrabbed or hit.
- **Fail:** Regrabbed or hit.
- **Variations:** Percent sweeps to find each escape window.
- **Data needed:** Throw knockback, attacker regrab timings, Falco weight and fall speed.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlFc.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/falco.json`](../framedata/falco.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 2-3 | 4 | 70 | 0 | 100 | - |  | 17 | 16 | 3 | -10 |  |
| Jab 2 | `jab2` | 3-4 | 4 | 50 | 0 | 100 | - |  | 20 | 19 | 3 | -12 | starts 1 frame late (included) |
| Rapid jab start | `rapid_jab_start` | - | - | - | - | - | - | - | 6 | - | - | - |  |
| Rapid jab loop | `rapid_jab_loop` | 2-3, 9-10, 16-17, 23-24, 30-31 | 1 | 80 | 10 | 80 | - |  | 35 | - | 2 | -31 |  |
| Rapid jab end | `rapid_jab_end` | - | - | - | - | - | - | - | 8 | - | - | - |  |
| Dash attack | `dash_attack` | 4-7 | 9 | 72 | 35 | 90 | - |  | 39 | 36 | 6 | -25 |  |
|  |  | 8-17 | 6 | 72 | 20 | 90 | - |  |  |  | 4 | -23 |  |
| Forward tilt (angled up) | `ftilt_high` | 5-9 | 9 | Sakurai | 0 | 100 | - |  | 26 | - | 6 | -15 |  |
| Forward tilt (slightly up) | `ftilt_mid_high` | 5-9 | 9 | Sakurai | 0 | 100 | - |  | 26 | - | 6 | -15 |  |
| Forward tilt | `ftilt` | 5-9 | 9 | Sakurai | 0 | 100 | - |  | 26 | - | 6 | -15 |  |
| Forward tilt (slightly down) | `ftilt_mid_low` | 5-9 | 9 | Sakurai | 0 | 100 | - |  | 26 | - | 6 | -15 |  |
| Forward tilt (angled down) | `ftilt_low` | 5-9 | 9 | Sakurai | 0 | 100 | - |  | 26 | - | 6 | -15 |  |
| Up tilt | `utilt` | 5-11 | 9 | 97/90 | 30 | 120 | - |  | 23 | 23 | 6 | -11 |  |
| Down tilt | `dtilt` | 7-9 | 13 | 75 | 25 | 125 | - | slash | 29 | 28 | 7 | -13 |  |
| Forward smash | `fsmash` | 12-16 | 17 | Sakurai/110 | 40 | 90 | - |  | 39 | - | 9 | -18 | charge hold frame 7 |
|  |  | 17-21 | 14 | Sakurai | 10 | 105 | - |  |  |  | 8 | -14 |  |
| Up smash | `usmash` | 7-10 | 14 | 95 | 25 | 100 | - |  | 43 | - | 8 | -28 | charge hold frame 2; partly intangible 1-10 (1 bone) |
|  |  | 11-15 | 12 | Sakurai | 10 | 100 | - |  |  |  | 7 | -25 |  |
| Down smash | `dsmash` | 6-10 | 16/13 | 25/80 | 20 | 70 | - |  | 49 | 46 | 9 | -30 | charge hold frame 2; partly intangible 1-6 (4 bones) |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 4-7 | 12 | Sakurai | 10 | 100 | - |  | 49 | 42 | 7 | 15 | 7 | <4, >36 | +0 |  |
|  |  | 8-31 | 9 | Sakurai | 0 | 100 | - |  |  |  | 6 |  |  |  | -1 |  |
| Forward air | `fair` | 6-8 | 9 | Sakurai | 10 | 100 | - |  | 59 | 53 | 6 | 22 | 11 | <6, >48 | -5 |  |
|  |  | 16-18 | 8 | Sakurai | 10 | 100 | - |  |  |  | 5 |  |  |  | -6 |  |
|  |  | 24-26 | 7 | Sakurai | 10 | 100 | - |  |  |  | 5 |  |  |  | -6 |  |
|  |  | 33-35 | 5 | Sakurai | 10 | 100 | - |  |  |  | 4 |  |  |  | -7 |  |
|  |  | 43-45 | 3 | Sakurai | 50 | 100 | - |  |  |  | 3 |  |  |  | -8 |  |
| Back air | `bair` | 4-7 | 15/9 | Sakurai | 0 | 100 | - |  | 39 | 38 | 8 | 20 | 10 | <4, >22 | -2 |  |
|  |  | 8-19 | 9 | Sakurai | 0 | 100 | - |  |  |  | 6 |  |  |  | -4 |  |
| Up air | `uair` | 8-9 | 6 | 90 | 40/30 | 20 | - | slash | 39 | 36 | 4 | 18 | 9 | <8, >25 | -5 |  |
|  |  | 11-14 | 10 | 70/90 | 22/30 | 120/20 | - | slash |  |  | 6 |  |  |  | -3 |  |
| Down air | `dair` | 5-14 | 12 | 290 | 10 | 100 | - |  | 49 | - | 7 | 18 | 9 | <5, >29 | -2 |  |
|  |  | 15-24 | 9 | 290 | 20 | 100 | - |  |  |  | 6 |  |  |  | -3 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 12-13 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 5 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 7 | 3 | 45 | 35 | 135 | - | - | 11 | 33 |  |
| Back throw | `bthrow` | 2 | 2 | 56 | 80 | 85 | - | - | 9 | 38 | spawns article/projectile on 15, 18, 21 |
| Up throw | `uthrow` | 2 | 2 | 90 | 75 | 110 | - | - | 7 | 38 | spawns article/projectile on 18, 20, 24 |
| Down throw | `dthrow` | 1 | 1 | 270 | 150 | 40 | - | - | 33 | 43 | spawns article/projectile on 23, 25, 28, 31 |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Blaster (laser), ground, Start | `special_n_start` | - | - | - | - | - | - | - | 6 | - | - | - |  |
| Neutral B: Blaster (laser), ground, Loop | `special_n_loop` | - | - | - | - | - | - | - | 23 | - | - | - |  |
| Neutral B: Blaster (laser), ground, End | `special_n_end` | - | - | - | - | - | - | - | 26 | - | - | - |  |
| Neutral B: Blaster (laser), air, Start | `special_air_n_start` | - | - | - | - | - | - | - | 4 | - | - | - |  |
| Neutral B: Blaster (laser), air, Loop | `special_air_n_loop` | - | - | - | - | - | - | - | 15 | - | - | - |  |
| Neutral B: Blaster (laser), air, End | `special_air_n_end` | - | - | - | - | - | - | - | 21 | - | - | - |  |
| Side B: Falco Phantasm (side B), ground, Start | `special_s_start` | - | - | - | - | - | - | - | 15 | - | - | - |  |
| Side B: Falco Phantasm (side B), ground | `special_s` | - | - | - | - | - | - | - | 3 | - | - | - |  |
| Side B: Falco Phantasm (side B), ground, End | `special_s_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Side B: Falco Phantasm (side B), air, Start | `special_air_s_start` | - | - | - | - | - | - | - | 15 | - | - | - |  |
| Side B: Falco Phantasm (side B), air | `special_air_s` | - | - | - | - | - | - | - | 3 | - | - | - |  |
| Side B: Falco Phantasm (side B), air, End | `special_air_s_end` | - | - | - | - | - | - | - | 39 | - | - | - |  |
| Up B: Fire Bird, ground, Hold | `special_hi_hold` | - | - | - | - | - | - | - | 42 | - | - | - |  |
| Up B: Fire Bird, ground, HoldAir | `special_hi_hold_air` | - | - | - | - | - | - | - | 42 | - | - | - |  |
| Up B: Fire Bird, ground | `special_hi` | 1-29 | 16 | 80 | 80 | 60 | - | fire | 29 | - | 9 | - |  |
| Up B: Fire Bird, ground, Landing | `special_hi_landing` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Up B: Fire Bird, ground, Fall | `special_hi_fall` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Up B: Fire Bird, ground, Bound | `special_hi_bound` | - | - | - | - | - | - | - | 14 | - | - | - |  |
| Down B: Reflector (shine), ground, Start | `special_lw_start` | 1 | 8 | 84 | 110 | 50 | - | electric | 3 | - | 5 | - | intangible 1 |
| Down B: Reflector (shine), ground, Loop | `special_lw_loop` | - | - | - | - | - | - | - | 27 | - | - | - |  |
| Down B: Reflector (shine), ground, Hit | `special_lw_hit` | - | - | - | - | - | - | - | 19 | - | - | - |  |
| Down B: Reflector (shine), ground, End | `special_lw_end` | - | - | - | - | - | - | - | 17 | - | - | - |  |
| Down B: Reflector (shine), air, Start | `special_air_lw_start` | 1 | 8 | 84 | 110 | 50 | - | electric | 3 | - | 5 | - | intangible 1 |
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
| Ledge jump part 2 (>=100%) | `ledge_jump_slow_2` | - | - | 38 | - |  |
| Ledge jump part 1 (<100%) | `ledge_jump_1` | intangible 1-14 | - | 14 | - |  |
| Ledge jump part 2 (<100%) | `ledge_jump_2` | - | - | 43 | - |  |

### Out of shield options (computed)

Frame the hitbox first comes out, counting the first frame the player acts out of shield as frame 1. Aerials: jump squat + aerial startup. Up smash and up B: jump-cancelled, 1 + startup. Shield release (15 frames of `GuardOff`) is not needed for any of these.

| Option | Via | Hitbox out on frame | Key |
|-|-|-|-|
| Down B (aerial) | jump | 6 | `special_air_lw_start` |
| Shield grab | direct | 7 | `grab` |
| Up smash | jump cancel | 8 | `usmash` |
| Neutral air | jump | 9 | `nair` |
| Back air | jump | 9 | `bair` |
| Down air | jump | 10 | `dair` |
| Forward air | jump | 11 | `fair` |
| Up air | jump | 13 | `uair` |
| Spot dodge | direct | intangible 2-15 of 22 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 31 | `roll_forward` |
| Roll backward | direct | intangible 4-19 of 31 | `roll_backward` |
| Wavedash | jump | actionable on frame 17 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Falco indexed by [The Melee Library](https://www.meleelibrary.com/#falco) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [Falco](https://www.youtube.com/watch?v=122r0CWkWWU) |  |  |
| [2020 Falco Melee Techs Guide](https://www.youtube.com/watch?v=WtIYAdjUdx4&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=27&t=0s) | Third Chair | Video guide on performing useful Falco tech in 2020. |
| [Are You a Falco Player?](https://www.youtube.com/watch?v=wpxR9WSUvwg&index=39&list=WL) | SSBM Tutorials | They give an overview of Falco the character to give you an idea of whether you would like to play him. |
| [Falco Trials](https://www.youtube.com/watch?v=Tb_B_2TEHBA&feature=youtu.be) | Ripple | Essential Falco tech inspired by the trials system in Street Fighter. |
| [Falco Hitboxes and Frame Data](http://smashboards.com/threads/falco-hitboxes-and-frame-data.300397/) | Stratocaster, Standardtoaster, and SuperDoodleMan |  |
| [Falco Frame Data Visualization](http://imgur.com/a/NuX4r) | Stormchicken |  |
| Short and Efficient Falco Practice Routine | Remix | This Falco practice routine will ensure your techskill is crisp and efficient. |
| Falco Shield Pressure Tutorials | SSBM Tutorials | [Beginner Part 1](https://www.youtube.com/watch?v=GRkQwrpBQZw) [Beginner Part 2](https://www.youtube.com/watch?v=zE92BbjEnSQ) [Intermediate](https://www.youtube.com/watch?v=WwZiy6OTAsA) |
| [Falco Multishine Tutorial](https://www.youtube.com/watch?v=mM_SnqTWHsI) | SSBM Tutorials and Squid |  |
| [A Slightly More Optimal Way to Drop Through Platforms](https://www.reddit.com/r/SSBM/comments/4j7tqr/i_found_a_slightly_more_optimal_way_to_drop/) | jkenney1 | Small guide on a faster way to drop through platforms after lasering. Also includes a good explanation of Shai and Isai drops. |
| [Multishine: An Extensive Guide](http://smashboards.com/threads/multishine-an-extensive-guide-updated-8-13-10.214549/) | Stratocaster | An old guide on multishines. The image links are broken. |
| Falco Neutral Game Tutorials | SSBM Tutorials | [Part 1: Lasers](https://www.youtube.com/watch?v=RkUfAtXnNAU) [Part 2: Grounded Approaches](https://www.youtube.com/watch?v=Rqw5wRh2E88) [Part 3: Anti-air](https://www.youtube.com/watch?v=yLa6jCtQrVQ) |
| [Hao To Fazfall Thru Platz Fasta Like Shia/Chawps](http://smashboards.com/threads/hao-to-fazfall-thru-platz-fasta-like-shia-chawps.273161/) | Mogwai |  |
| [Falco Tutorials](https://www.youtube.com/playlist?list=PL8IfDsQrNL3WRhFucPp9AVdYM1nM8vhBu) | The Melee.pe TV | A playlist of a few videos demonstrating Falco techniques including laser, mobililty, combo, and recovery tricks. |
| [Falco Discussion Thread](http://smashboards.com/threads/falco-discussion-thread.256826/) | community | Lots of great discussion with input by PPMD himself! |
| [Falco’s Invincible Ledgedash Options](https://www.youtube.com/watch?v=_yXUJ-q2P9c) | Practical TAS | A video showcasing options Falco can perform intangibly from a ledgedash. |
| [Ledge Hop Double Laser Tutorial](https://www.youtube.com/watch?v=FF_YhidQ_NE&list=WL&index=21) | SSBM Tutorials |  |
| [Falco Trick Throws Tutorial](https://www.youtube.com/watch?v=QWHjjztkAQ0&index=30&list=WL) | SSBM Tutorials |  |
| [Squid Inklings](https://docs.google.com/document/d/1wDdb-kNgCaZ-zTBFL33rrs3bcPjRWpEnXHegYCIaO5o/edit) | Squid | A document outlining Squid’s thought processes in solving problems as Falco. |
| [Top 6 Ways to Get Off the Ledge with Falco](https://www.youtube.com/watch?v=bPnrEd1z2XQ) | SSBM Tutorials |  |
| [Lowest Possible Laser Theorycraft and Explanation](https://www.youtube.com/watch?v=cVyA3-V8RMM) | SleepyK | Shooting low lasers off the stage to edgeguard spacies’ side-b. |
| [How to Practice Falco](https://www.youtube.com/watch?v=15myVh03yos&) | SSBM Tutorials |  |
| [Falco DI Mixups and Jump Cancel Shine Usage](https://www.youtube.com/watch?v=eLh7N3X0wn4) | Lint |  |
| [Multishine Pseudo Option Select](https://www.reddit.com/r/SSBM/comments/4de38s/new_falco_multishine_pseudoos/) | Choclate Lava | A single set of inputs that will yield a double shine grab or a Westballz shine depending on how fast you execute. |
| [How to SDI Falco Combos](https://www.youtube.com/watch?v=AwuWG9taMvA&feature=youtu.be) | Trahh |  |
| [Escaping Sheik Techchases as Spacies](https://www.reddit.com/r/SSBM/comments/4yzyro/escaping_sheik_techchases_as_spacies/) | groating |  |
| [Mango Character Discussion: Falco in 2016](https://www.youtube.com/watch?v=uRa7249dBWk) | Mang0 | Mango describes how lasers exert pressure on your opponent and the kinds of mixups they create. |
| [Falco vs. Marth Matchup Guide](https://www.youtube.com/watch?v=VqEgr8NyeSU) | SSBM Tutorials |  |
| [Falco Ledgedash Timing and Intangibility](https://smashboards.com/threads/falco-ledgedash-timing-and-intangibility.442300) | Sycorax | How much intangibility you can expect from Falco's ledgedash given certain jump and airdodge timings and ledgegrab setups. |
| A Dissection of Falco's Options on Shield | Robotic Phish | [Part 1: The Approach](https://web.archive.org/web/20170606062410/http://peekand.co/editorials/dissection-falcos-options-shield/) [Part 2: After Shine](https://www.youtube.com/watch?v=IzvPVkb5_08) |
| [Falco Multi-Shine Pseudo Option Select](https://www.reddit.com/r/SSBM/comments/4de38s/new_falco_multishine_pseudoos/) | TheChocolateLava | A way to perform multishine pressure so that "if the shine is grounded, you get a shinegrab. If it's aerial, you wavedash down, and can resume pressure." |
| [7 Mistakes All Falcos Make](https://www.youtube.com/watch?v=VId80hN2dG8) | SSBM Tutorials | They are: not getting much off throws, using side-b to recover too predictably, double laser from the ledge too predictably, spamming spotdodge, shooting the same number of lasers before approaching, not dash dancing, and using dair too much. |
| [Anti Falco Laser Technique](https://www.youtube.com/watch?v=VD4nDvvdCWc) | SSBM Tutorials | It is "take the laser, then do an action". |
| [How to Reverse Double Laser from Ledge](https://www.youtube.com/watch?v=P9A1NorZbt4) | Zenith |  |
| [Falco optimal fastfall timing](https://portraitinsmash.blogspot.com/2015/12/falco-optimal-fastfall-timing.html?m=0) | DruggedFox | Druggedfox discusses fastfall timings to achieve the best possible frame advantage on aerials. |
| [Possible Methods for Countering Ledge Stalling as Falco](https://www.reddit.com/r/smashbros/comments/6go9rz/saints_gaming_live_super_smash_bros_melee_winners/dirsxrr/) | PPMD |  |
| [Mogwai’s Falco Thread 2008](http://smashboards.com/threads/mogwais-falco-thread-mogwai-plays-league-of-legends-and-doesnt-write-stuff.203781/) | Mogwai and community | Some old Falco discussion. |
| [Falco Matchup Thread 2011](http://smashboards.com/threads/falco-matchup-thread-updated-with-2011-pp-fox-stuff.260699/) | community |  |
| [Character Matchup Guide 2007](http://smashboards.com/threads/character-match-ups-guide-will-be-updated-soon.95998/) | GamerGuitarist7 | Old matchup info. Still some useful stuff. |
| [The Marvelous Guide on Falco Lombardi 2005](http://smashboards.com/threads/the-marvellous-guide-on-falco-lombardi-by-bornfidelity-com-v4-2.54145/) | BadInfluence | It is old, but maybe you will find some nuggets. |
| [Melee Falco Tutorial 2009](https://www.youtube.com/watch?v=T_CrTWvKpRQ) | Overswarm | Old school tutorial video. |
| [Falco Practice Guide](https://www.youtube.com/watch?v=UjmWGvnrHWA) | PPMD | PPMD covers great skills to practice with Falco. |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Falco (SSBM): https://www.ssbwiki.com/Falco_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Falco_(SSBM)/Down_special , /Down_aerial ,
  /Neutral_special , /Side_special , /Up_special , /Up_throw , /Down_throw ,
  /Forward_throw , /Back_throw , /Neutral_aerial , /Back_aerial , /Up_aerial ,
  /Forward_smash , /Down_smash , /Down_tilt , /Up_tilt , /Grab
- SSBWiki technique pages: https://www.ssbwiki.com/Reflector_(Fox) (multishine frame
  table for both characters), https://www.ssbwiki.com/Waveshine ,
  https://www.ssbwiki.com/Pillaring , https://www.ssbwiki.com/Blaster_(Falco) ,
  https://www.ssbwiki.com/Falco_Phantasm , https://www.ssbwiki.com/Short_hop_laser ,
  https://www.ssbwiki.com/Ledgestall , https://www.ssbwiki.com/Ledgedash ,
  https://www.ssbwiki.com/Chain_grab ,
  https://www.ssbwiki.com/List_of_SSBM_tier_lists_(NTSC)
- SSBWiki pages for other characters used for cross-references:
  https://www.ssbwiki.com/Fox_(SSBM)/Up_throw ,
  https://www.ssbwiki.com/Ganondorf_(SSBM)/Back_aerial ,
  https://www.ssbwiki.com/Captain_Falcon_(SSBM)/Forward_aerial
- Melee Library, "Falco optimal fastfall timing" (Druggedfox):
  https://portraitinsmash.blogspot.com/2015/12/falco-optimal-fastfall-timing.html
- Melee Library, "A Dissection of Falco's Options on Shield", part 1 (Robotic Phish):
  https://web.archive.org/web/20170606062410/http://peekand.co/editorials/dissection-falcos-options-shield/
- Melee Library, "Squid Inklings" (Squid):
  https://docs.google.com/document/d/1wDdb-kNgCaZ-zTBFL33rrs3bcPjRWpEnXHegYCIaO5o/edit
- Melee Library, "Falco Ledgedash Timing and Intangibility" (Sycorax), via
  web.archive.org:
  https://smashboards.com/threads/falco-ledgedash-timing-and-intangibility.442300
- Melee Library, "Multishine: An Extensive Guide" (Stratocaster), via web.archive.org:
  http://smashboards.com/threads/multishine-an-extensive-guide-updated-8-13-10.214549/
- Melee Library (Fox section), "Guide to Ace Arwing Pilot Fox McCloud" (Cunning Kitsune)
  and "Chaingrab Info" (KirbyKaze), via web.archive.org
- Melee Library (Captain Falcon section), "Uthrow Followups on Falco" (Kadano) and
  "Techchasing Like a Man: Complete Breakdown" (Gravy), via web.archive.org
- Melee Library (Ganondorf section), "The Ganon Chaingrabbing Guide" (Magus) and
  "Techchasing into 2015: Metagame and Theory" (Ace), via web.archive.org
- Frame data dump: `Falco.json`
