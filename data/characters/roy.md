---
schema: melee-character/v1
id: roy
name: Roy
aliases: ["Roy (Fire Emblem)", "the Young Lion"]
tier: "D (21st of 26), 2021 PG Stats tier list (13th official NTSC list)"
archetype: [swordie, fastfaller, combo-food, chaingrab, mixup]
related: [marth]
summary: Roy uses Marth-like ground movement, a vertical-launching down tilt and a long grab to start short combos on fastfallers, and must land a close-range (hilt) forward smash or a read to kill.
key_tech: [hilt-sweetspot, dtilt-launcher, roy-uthrow-chaingrab, double-edge-dance, counter-edgeguard, reverse-blazer, flare-blade-edgeguard, roy-recovery]
# generated: begin (tools/melee_data/render.py, do not edit)
dat: PlFe.dat
framedata: ../framedata/roy.json
code: src/melee/ft/kinds/ftEmblem
specials:
  neutral_b: "Flare Blade"
  side_b: "Double-Edge Dance"
  up_b: "Blazer"
  down_b: "Counter"
attributes:
  weight: 85
  gravity: 0.114
  fall_speed: 2.4
  fast_fall_speed: 2.9
  jump_squat: 5
  jumps: 2
  walk_speed: 1.2
  dash_speed: 1.4
  run_speed: 1.61
  traction: 0.06
  air_speed: 0.9
  landing_lag: 4
moves:  # key: [first hit frame, first actionable frame, max damage]
  jab1: [4, 26, 6]
  dash_attack: [12, 40, 12]
  utilt: [7, 40, 10]
  dtilt: [8, 20, 12]
  fsmash: [12, 54, 20]
  usmash: [15, 46, 10]
  dsmash: [6, 72, 21]
  nair: [7, 50, 8]
  fair: [5, 35, 8]
  bair: [8, 43, 9]
  uair: [5, 49, 9]
  dair: [7, 64, 9]
  grab: [7, 31, 0]
  dash_grab: [10, 41, 0]
  pummel: [7, 25, 3]
  fthrow: [null, 32, 5]
  bthrow: [null, 45, 5]
  uthrow: [null, 45, 5]
  dthrow: [null, 43, 6]
  special_n_start: [null, 12, 0]
  special_n_loop: [null, 30, 0]
  special_n_end: [5, 34, 6]
  special_n_end_298: [9, 34, 50]
  special_air_n_start: [null, 12, 0]
  special_air_n_loop: [null, 30, 0]
  special_air_n_end: [5, 34, 6]
  special_air_n_end_302: [9, 34, 50]
  special_s1: [6, 30, 5]
  special_s2_hi: [11, 40, 6]
  special_s2_lw: [13, 40, 6]
  special_s3_hi: [12, 46, 10]
  special_s3_s: [10, 46, 10]
  special_s3_lw: [15, 46, 5]
  special_s4_hi: [19, 50, 13]
  special_s4_s: [22, 50, 13]
  special_s4_lw: [12, 60, 5]
  special_air_s1: [6, 30, 5]
  special_air_s2_hi: [11, 40, 6]
  special_air_s2_lw: [13, 40, 6]
  special_air_s3_hi: [12, 46, 10]
  special_air_s3_s: [10, 46, 10]
  special_air_s3_lw: [15, 46, 5]
  special_air_s4_hi: [19, 50, 13]
  special_air_s4_s: [22, 50, 13]
  special_air_s4_lw: [12, 60, 5]
  special_hi: [9, 49, 5]
  special_air_hi: [9, 49, 5]
  special_lw: [null, 60, 0]
  special_lw_hit: [3, 36, 1]
  special_air_lw: [null, 60, 0]
  special_air_lw_hit: [3, 36, 1]
oos:  # option: frame the hitbox is out
  grab: 7
  fair: 10
  uair: 10
  special_hi: 10
  nair: 12
  dair: 12
  bair: 13
  usmash: 16
resources: 2
# generated: end
---

# Roy

<!-- GENERATED:attributes -->
## Attributes

Read from `PlFe.dat` (`ftCo_DatAttrs`). Speeds are game units per frame.

| Attribute | Value |
|-|-|
| Weight | 85 |
| Gravity | 0.114 |
| Terminal fall speed | 2.4 |
| Fast-fall speed | 2.9 |
| Jump squat (frames before airborne) | 5 |
| Full hop / short hop initial Y speed | 2.6 / 1.5 |
| Air jump Y multiplier | 0.88 |
| Jumps | 2 |
| Walk max speed | 1.2 |
| Dash initial speed / run max speed | 1.4 / 1.61 |
| Ground friction (traction) | 0.06 |
| Air max horizontal speed | 0.9 |
| Air acceleration (base + stick) | 0.02 + 0.03 |
| Air friction | 0.005 |
| Normal landing lag | 4 |
| Shield size | 11.75 |
<!-- /GENERATED:attributes -->

## Overview

Roy is a clone of [Marth](marth.md): same animations and move list, different numbers. The key
inversion is the sweetspot. Roy's strong hitboxes are at the hilt and middle of the blade and
the tip is the weak hit, so he has to fight close to get any reward, which gives up the safety
that makes Marth good [wiki:Roy_(SSBM)]. He keeps a fast dash, a usable dash dance, the sixth
longest [wavedash](../techniques/wavedash.md) and the second longest non-tether grab
[wiki:Roy_(SSBM)]. He wins neutral with dash dance grab and down tilt, punishes fastfallers
with up throw chain grabs and down tilt launches, and kills with forward smash, down smash,
side B (Double-Edge Dance) finishers or Counter. Against floaties he has almost no combos or
kill setups. He is a fastfaller himself (fall speed 2.4) but lighter than Marth (weight 85),
so he is easy to combo, and his recovery is among the worst in the game [wiki:Roy_(SSBM)].

## Strengths and weaknesses

- **Strengths:**
  - Ground movement close to Marth's; long grab (second longest non-tether) [wiki:Roy_(SSBM)].
  - Down tilt launches at 80° with base knockback 90 and is interruptible from frame 20, a
    true combo starter that Marth's dtilt is not [fd, wiki:Roy_(SSBM)].
  - Forward smash's sweetspot covers everything but the tip and has priority, so the strong
    hit (20%, base 80, growth 65 [fd]) is easy to get at close range [wiki:Roy_(SSBM)].
  - Up throw chain grab on Fox and Falco [wiki:Chain_grab].
  - Fast SHFFL (see [shffl](../techniques/shffl.md)) because he falls fast.
  - Counter multiplies the countered hit by 1.5 instead of Marth's flat 7% [wiki:Roy_(SSBM)].
  - Slightly shorter than Marth: his standing grab reaches a crouching Jigglypuff or Kirby
    [wiki:Roy_(SSBM)].
  - NTSC Roy (weight 85) is knocked down by Fox's shine, so Fox cannot waveshine him like
    Marth [wiki:Roy_(SSBM)].
- **Weaknesses:**
  - Weak tip hitboxes with very low knockback and hitstun; spaced pokes give nothing and are
    [crouch cancelled](../techniques/crouch-cancel.md) [wiki:Roy_(SSBM)].
  - Aerials are weak (fair 8%/5%, bair and uair 9%/6% [fd]) and none "can reliably KO under
    200%" [wiki:Roy_(SSBM)]; more landing lag than Marth on nair, fair (20 frames, 10
    L-cancelled) and uair (18/9) [fd].
  - Slower or shorter-lived hitboxes than Marth on the same animations; dash attack, bair and
    jab have blind spots [wiki:Roy_(SSBM)].
  - No real punish game on floaties (Jigglypuff, Peach) [wiki:Roy_(SSBM)].
  - Fastfaller with a short up B: easy to combo, chain grab, edgeguard and gimp.
  - Jump squat is 5 frames (Marth 4) and jumps are lower [wiki:Roy_(SSBM)].

## Character tech

### Hilt sweetspot spacing

- **id:** `hilt-sweetspot`
- **What:** Roy's "reverse tipper": the strong hitboxes are near the hand and mid-blade, the
  weak one is at the tip [wiki:Tipper].
- **Inputs:** Any sword normal from close range, so the mid or hilt hitbox overlaps the target.
- **Timing:** On forward smash, mid and hilt hitboxes are all the 20% hit and out-prioritise
  the 12% tip (base knockback 30) [fd, wiki:Roy_(SSBM)]. Fsmash hits frames 12-14 and is
  interruptible from frame 54 (Marth: 10-13 and 48) [fd].
- **Used for:** Every kill and every combo starter; Roy's pokes at max range do too little.
- **Common errors:** Spacing like Marth (tip hit: weak, unsafe on hit at low percent);
  swinging late so the short active window has already ended.
- **Drill idea:** CPU stands at a random distance; success only if the 20% fsmash hitbox (or
  the 10-12% dtilt hitbox) connects.

### Down tilt launcher

- **id:** `dtilt-launcher`
- **What:** Down tilt pops the opponent straight up with high base knockback and ends quickly,
  leading to grab, aerials or fsmash.
- **Inputs:** Crouch (run cancel or wavedash), down+A, then act at IASA: dash grab, jump up
  air / fair, fsmash, or another dtilt.
- **Timing:** Hits frames 8-10, interruptible from frame 20 of 57; 12% hilt / 10% mid / 6%
  tip, 80° launch, base knockback 90 (70 on the tip), growth 40 [fd].
- **Used for:** His main neutral poke and combo starter, especially on fastfallers
  [wiki:Roy_(SSBM)]. Because base knockback is high it pops up even at 0%.
- **Common errors:** Tip hit (little hitstun); follow-up chosen for the wrong DI; using it to
  edgeguard as if it were Marth's semi-spike (it launches upward).
- **Drill idea:** CPU Fox at 0-60% takes a dtilt with random DI; success if any follow-up hit
  or grab lands before he can act.

### Up throw chain grab

- **id:** `roy-uthrow-chaingrab`
- **What:** Up throw → regrab on Fox and Falco, as with Marth. See
  [chain grab](../techniques/chain-grab.md).
- **Inputs:** Grab, up throw, follow DI (turn, dash, or pivot), JC grab.
- **Timing:** Up throw does 5% and launches at 97° (Marth: 4%, 93°) [wiki:Roy_(SSBM)].
  SSBWiki gives "0% to about 60%" for Marth and Roy on Fox and Falco [wiki:Chain_grab]. Exact
  windows by DI for Roy were not found; Marth's chart does not transfer exactly because the
  angle differs.
- **Used for:** Roy's main damage on spacies on Final Destination and Pokémon Stadium; ends in
  fsmash, dtilt or up air strings.
- **Common errors:** Same as Marth's: late regrab, wrong turn on DI behind, platforms.
- **Drill idea:** CPU Fox in grab at 0% with random DI; count regrabs to 60%.

### Double-Edge Dance

- **id:** `double-edge-dance`
- **What:** Side B: a four-swing sequence where swings 2-4 change with the stick direction.
  18 possible combinations [wiki:Dancing_Blade].
- **Inputs:** Side+B, then B (or A) with the stick up / neutral / down (down only for swings
  3 and 4). The first two swings come out however fast B is pressed; swings 3 and 4 need a
  short wait between presses or they do not come out [wiki:Double-Edge_Dance].
- **Timing:** First swing hits frames 6-8 [fd]. Third swing up is a meteor smash (280°/270°
  on the strong hitboxes) [fd]; third forward is 10% with base 50 growth 110; fourth up is
  13% at 40°; fourth forward is 13% with growth 135; fourth down is a multi-hit that
  shield-pokes [fd, wiki:Double-Edge_Dance]. Unlike Marth's it has normal (not transcendent)
  priority, so it can clank with projectiles [wiki:Roy_(SSBM)].
- **Used for:** Approaching (first hit into dtilt or grab), beating crouch cancel with the
  third/fourth hits, a kill option at high percent, and gimping low Fox/Falco up B start-ups
  with the first swing [wiki:Double-Edge_Dance, wiki:Roy_(SSBM)].
- **Common errors:** Mashing B (third swing never comes out); first two hits crouch cancelled
  and punished; overuse.
- **Drill idea:** CPU crouch cancels at low percent; success if the third or fourth hit knocks
  it down. Grade the input gaps.

### Counter edgeguard

- **id:** `counter-edgeguard`
- **What:** Down B (Counter) placed where a recovery's hitbox will be; the counterattack does
  1.5× the countered move's damage, so strong recovery hitboxes kill their owner.
- **Inputs:** Stand at the ledge (or drop just offstage), press down+B so the counter window
  overlaps the incoming hitbox.
- **Timing:** Counter is active frames 8-20 of 59; on activation there are 13 freeze frames,
  then the counterattack hits on frames 3-9 with Roy intangible on frames 1-5
  [wiki:Roy_(SSBM)/Down_special]. Marth's is active 5-29 but does a flat 7%
  [wiki:Roy_(SSBM)].
- **Used for:** Linear recoveries with hitboxes (Fox/Falco up B and side B, Marth/Roy up B)
  and reads on smash attacks; it "will very likely KO most recovering opponents if landed"
  [wiki:Roy_(SSBM)].
- **Common errors:** Too early (window ends at frame 20, then 39 frames of lag); countering a
  weak hit (little reward).
- **Drill idea:** CPU Fox aims up B at the ledge; success if Counter activates and Fox is KO'd.

### Reverse Blazer

- **id:** `reverse-blazer`
- **What:** Up B (Blazer) with the stick flicked backward at start-up; the reversed first hit
  is the strong one. Its first hit has set knockback 200, which KOs very light characters off
  low ceilings.
- **Inputs:** Up+B, then hold backward at once.
- **Timing:** First hit frame 9; Roy reverses only if the stick is held backward between
  frames 10 and 11; later hits on frames 10-21; 48 frames total
  [wiki:Roy_(SSBM)/Up_special]. First hit: 5%, 84°, set knockback 200 [fd]. Landing lag 30
  frames (Marth: 34) [wiki:Roy_(SSBM)]. The move's knockback depends on the victim's weight
  and fall speed rather than percent, so it can one-hit KO Pichu, Jigglypuff and Mr. Game &
  Watch on Yoshi's Story (low ceiling), and it is punishable on hit against most characters
  [wiki:Blazer, wiki:Roy_(SSBM)].
- **Used for:** A gimmick kill on Jigglypuff on Yoshi's Story / Pokémon Stadium; an out of
  shield option with a frame-9 hitbox (frame 10 OoS with one jump squat frame, by the same
  rule as Marth's [wiki:Dolphin_Slash]); recovery.
- **Common errors:** Whiff (long fall plus 30 frames of landing lag); not reversed (weak
  hits); victim SDIs out of the multi-hit.
- **Drill idea:** CPU Jigglypuff on Yoshi's Story at 0%, shielding or landing next to Roy;
  success if reverse Blazer's first hit KOs.

### Flare Blade edgeguard

- **id:** `flare-blade-edgeguard`
- **What:** Neutral B (Flare Blade), a chargeable overhead swing: stronger than Marth's Shield
  Breaker, slow, and a one-hit KO at full charge.
- **Inputs:** Hold B at the ledge as the opponent recovers; release so the swing covers the
  ledge.
- **Timing:** Uncharged: hitbox frames 16-21, 44 frames total, 6%, base 40 growth 110. Charged:
  hitbox 5-10 frames after release. Full charge takes five seconds, does 50% (base 50 growth
  83) and costs Roy 10% recoil [wiki:Roy_(SSBM)/Neutral_special, wiki:Flare_Blade, fd].
- **Used for:** Covering slow or predictable recoveries; punishing a broken shield.
- **Common errors:** Releasing early/late; opponent recovers high over it; using it for shield
  damage (it does almost none uncharged, unlike Shield Breaker [wiki:Roy_(SSBM)]).
- **Drill idea:** CPU recovers low with a linear up B after a random delay; success if a
  partially charged Flare Blade connects.

### Recovery (side B stall into Blazer)

- **id:** `roy-recovery`
- **What:** Double jump, first swing of side B to slow the fall, then up B angled toward the
  stage.
- **Inputs:** Side+B once (no follow-up presses), drift, up+B and push the stick toward the
  stage to angle it.
- **Timing:** Blazer can be angled from straight up to 45° forward at the cost of height, and
  covers more horizontal but less vertical distance than Marth's up B
  [wiki:Blazer, wiki:Roy_(SSBM)]. Roy's fall speed (2.4; 2.9 fast-falling) makes the side B
  stall worth less than Marth's [wiki:Roy_(SSBM)].
- **Used for:** Every recovery; the multi-hit up B can hit edgeguarders who challenge it.
- **Common errors:** Up B from too low (little vertical gain); angling when height was needed.
- **Drill idea:** Roy starts offstage at the edge of his range; success if he grabs the ledge.

## Neutral game

- Dash dance and wavedash to threaten grab and dtilt, like Marth but with a smaller dash-dance
  window (run speed 1.61 vs Marth's 1.8, walk 1.2 vs 1.6) [wiki:Roy_(SSBM)].
- Down tilt is the main poke; it converts on hit.
- Side B first hit as a quick mid-range poke into dtilt or grab [wiki:Double-Edge_Dance].
- Fsmash to catch opponents who step into close range; it is slower (frame 12) and laggier
  than Marth's [fd].
- SHFFL fair/nair are fast but weak; tip hits are crouch cancelled and punished
  [wiki:Roy_(SSBM)].
- Roy must get closer than Marth for any reward, which exposes him to faster close-range moves
  (shine, jabs, grabs, Peach down smash).

## Punish game

Roy's punishes are short. On fastfallers: up throw chain grab, dtilt strings, tech chases off
forward/down throw, juggles with up air on stages with few platforms. On floaties he has
"no reliable method of achieving any combos or KO setups" [wiki:Roy_(SSBM)]. All throws do 1%
more than Marth's (5% forward/back/up, 6% down). Down throw launches at a steeper angle with
more growth than Marth's, which makes it worse for follow-ups; back throw has less growth
(45 vs 60), which makes it better for follow-ups and worse for sending offstage
[wiki:Roy_(SSBM)].

| Starter | On | Percent | Follow-up | Notes | Source |
|-|-|-|-|-|-|
| uthrow | Fox, Falco | 0 to about 60% | regrab | same idea as Marth's; Roy-specific windows not found | [wiki:Chain_grab] |
| dtilt (hilt/mid) | fastfallers | low to mid | grab, up air, fair, fsmash | 80° launch, base 90 | [fd], [wiki:Roy_(SSBM)] |
| side B 1 | most | low | dtilt, grab, or continue side B | first two hits are crouch-cancellable | [wiki:Double-Edge_Dance] |
| side B 3 up | grounded | any | side B 4 | pops them up for the fourth hit | [wiki:Double-Edge_Dance] |
| fthrow / dthrow | fastfallers | any | tech chase, edgeguard | | [wiki:Roy_(SSBM)] |
| up smash (multi-hit) | above him | any | final hit 10%, base 73 growth 90 | can be SDI'd; tip of hits 2-4 spikes | [fd], [wiki:Roy_(SSBM)] |

### Chain grabs and tech chases

- **Fox and Falco:** up throw chain grab from 0% to about 60% [wiki:Chain_grab]. Expect the
  same escape routes as Marth's (platforms, DI mixups, slight DI); see
  [Marth](marth.md#chain-grabs-and-tech-chases). The Melee Library lists a "Roy Melee Chaingrab
  Guide" video (not readable here) as the detailed reference.
- **Tech chases:** dash → JC grab covers rolls; fsmash and dtilt cover tech in place and
  missed tech. General timings in [tech chase](../techniques/tech-chase.md).
- **Floaties:** none of note.

## Kill options

| Move | On | Typical kill percent | Conditions | Source |
|-|-|-|-|-|
| fsmash (hilt/mid) | most | Unknown (third strongest fsmash at 0%, twelfth at 100%) | 20%, base 80, growth 65; frames 12-14 | [wiki:Marth_(SSBM)/Forward_smash], [fd] |
| dsmash (front, sweetspot) | most | Unknown | 21%, 75°, base 42, growth 70; frame 6 | [fd] |
| side B 4 forward | most | Unknown, high percent | 13%, growth 135 | [fd] |
| side B 4 up | most | Unknown | 13% at 40° | [fd] |
| Counter | recovering or smashing opponent | depends on the countered move | 1.5× damage | [wiki:Roy_(SSBM)] |
| Flare Blade (full charge) | any | 0% on normal-sized stages | 50%, five-second charge, 10% recoil | [wiki:Flare_Blade] |
| reverse Blazer (first hit) | Pichu, Jigglypuff, Mr. Game & Watch | 0% on Yoshi's Story | set knockback 200 | [wiki:Blazer] |
| dair (hand sweetspot) | offstage | Unknown | 270° meteor (cancellable), 9%; risky | [fd], [wiki:Roy_(SSBM)] |

- Most stocks end with a close-range fsmash that sends the opponent offstage, followed by a
  simple edgeguard: fsmash/dsmash the landing, Counter the recovery, Flare Blade, or grab the
  ledge. Roy rarely goes offstage because his fall speed and laggy aerials make it unsafe
  [wiki:Roy_(SSBM)].
- Roy's "Ken combo" (fair → dair) exists but the dair is a cancellable meteor with its
  sweetspot at his hand and often ends in a self-destruct [wiki:Ken_Combo].

## Recovery

- **Options:** double jump (lower than Marth's); side B first swing stall; up B (Blazer:
  frame 9, multi-hit with flame, angleable up to 45° forward, short vertical travel, 30 frames
  of landing lag) [wiki:Blazer, wiki:Roy_(SSBM)]; air dodge; Counter against an edgeguarder's
  hit.
- **Mixups:** angle of Blazer; reversing it; stalling with side B; recovering high with double
  jump when the opponent commits to the ledge.
- **Weaknesses:** very short vertical range and fast fall: anything that sends him low kills.
  Blazer travels slowly, so it is easy to intercept or edgehog, and its hits can be SDI'd
  [wiki:Roy_(SSBM)].

### Edgeguarding Roy

- Grab the ledge early: he usually has to up B from below and cannot reach the stage over an
  edgehog. If he lands on stage, punish 30 frames of landing lag.
- Hit him out of double jump or the side B stall; he has no fast protective aerial.
- Avoid standing unshielded at the lip in front of Blazer (multi-hit, frames 9-21
  [wiki:Roy_(SSBM)/Up_special]).
- A CPU Roy should mix Blazer angle (steep vs 45°), an early Blazer to hit a ledge-grabber,
  and a high double jump air dodge when it has the height.

## Defense and out of shield

- **Out of shield:** shield grab (long range); up B OoS (frame 9 hitbox plus one jump squat
  frame, slower and weaker than Marth's frame 5) [wiki:Roy_(SSBM)/Up_special]; short hop
  aerials after a 5-frame jump squat; wavedash OoS. Counter (active frames 8-20) as a read.
- **Crouch cancel:** usable at low percent like any fastfaller; no Roy-specific thresholds
  were found.
- **Combo escapes:** none that are fast. DI and tech are his defence; double jump early.
- **What beats him:** shield pressure, anything that exploits fastfaller physics (chain
  grabs, up throw up air, pillars), and edgeguards.

## As the training dummy

- **Class:** weight 85, fall speed 2.4 (fast fall 2.9), gravity 0.114, jump squat 5 frames
  [wiki:Roy_(SSBM)]. A light fastfaller: combos like a spacie but dies earlier off the sides
  than Captain Falcon.
- **Chain grabbed by:** Sheik's NTSC down throw (0 to as high as 90%)
  [wiki:Sheik_(SSBM)/Down_throw]; Ice Climbers (Popo alone, down throw, to about 50%); Mewtwo
  down throw sometimes [wiki:Chain_grab]. Marth/Roy up throw on Roy: plausible given his fall
  speed, not sourced [unverified].
- **Fox shine:** knocks NTSC Roy down (he must tech), unlike Marth [wiki:Roy_(SSBM)].
- **Jab reset thresholds (Sheik's jab/needles):** forced plain stand below 38% post-hit; he
  lands on his feet from a jab when holding up at 20% or more post-hit
  [web:docs.google.com Collection of Sheik Stuff].
- **Recovery behaviour:** see "Edgeguarding Roy".
- **DI:** as a fastfaller he should DI away from up throw chain grabs and tech away on
  platforms; survival DI on fsmash-type hits.

## Matchup notes

### vs Fox and Falco

- His best matchups relative to the rest of his spread: chain grab, dtilt strings, juggles on
  Final Destination / Pokémon Stadium, and Double-Edge Dance or dtilt to gimp up B start-up
  [wiki:Roy_(SSBM)]. They still out-pressure his shield, combo him as a fastfaller and
  edgeguard him easily.

### vs Marth

- Marth does everything Roy does from further away and edgeguards him for free. Roy needs to
  get inside sword range; Roy's grab and dtilt still work.

### vs Sheik

- Sheik chain grabs Roy with down throw in NTSC and edgeguards him with fair and needles
  [wiki:Sheik_(SSBM)/Down_throw]. Counted as a hard counter by the Sheik down throw page.

### vs Jigglypuff and Peach

- "Completely losing matchups": no combos or KO setups on floaties [wiki:Roy_(SSBM)]. The
  exceptions are reads: close fsmash, Counter, and reverse Blazer on Jigglypuff under a low
  ceiling. Roy can at least standing-grab a crouching Jigglypuff [wiki:Roy_(SSBM)].

## Drill seeds

### Hilt forward smash spacing

- **id:** `roy-hilt-fsmash`
- **Goal:** Land the 20% fsmash hitbox, not the 12% tip.
- **Player:** Roy
- **CPU:** Marth, Sheik, Fox
- **Setup:** Flat stage, CPU standing or dash dancing at a random distance near Roy's fsmash
  range, 60-100%.
- **CPU behaviour:** Stands, or dashes in and out once.
- **Success:** The hit that connects is 20%.
- **Fail:** Tip hit or whiff.
- **Variations:** Wavedash-in fsmash; fsmash on a tech-in-place after a throw.
- **Data needed:** fsmash hitbox sizes and positions per frame (frames 12-14) [fd]; Roy
  wavedash length.

### Down tilt conversions

- **id:** `roy-dtilt-combo`
- **Goal:** Convert a dtilt on a fastfaller into a follow-up by DI.
- **Player:** Roy
- **CPU:** Fox, Falco, Captain Falcon
- **Setup:** CPU standing in dtilt range at 0-80%.
- **CPU behaviour:** Random DI (left, right, none); jumps or attacks on its first actionable
  frame; sometimes crouch cancels (dtilt's base knockback 90 should still pop it up).
- **Success:** A grab or attack lands before the CPU acts.
- **Fail:** CPU escapes or hits Roy; tip dtilt.
- **Variations:** Require fsmash as the finisher at 80%+; require regrab → up throw chain.
- **Data needed:** dtilt IASA 20, launch 80° base 90 growth 40 [fd]; CPU weight/fall speed;
  the combo windows are not sourced and must be measured.

### Chain grab spacies

- **id:** `roy-uthrow-chaingrab-fox`
- **Goal:** Hold the up throw chain grab through DI.
- **Player:** Roy
- **CPU:** Fox, Falco
- **Setup:** Final Destination, CPU in grab at 0%.
- **CPU behaviour:** Random DI {none, away, behind, slight}; jumps or shines when able.
- **Success:** Regrabs to about 60%, then a finisher lands.
- **Fail:** CPU acts between throws.
- **Variations:** Fixed DI; start percents 20/40%.
- **Data needed:** Roy up throw launch (97°) and release frame by victim weight; windows by
  percent are not sourced for Roy.

### Double-Edge Dance input timing

- **id:** `roy-ded-timing`
- **Goal:** Get the third and fourth swings out reliably and pick the right variant.
- **Player:** Roy
- **CPU:** any mid-weight
- **Setup:** CPU standing in side B range; either crouch cancelling at low percent or
  shielding.
- **CPU behaviour:** Crouch cancel then grab if Roy stops after hit 2; or hold shield.
- **Success:** Versus crouch: hit 3 (down or forward) or hit 4 knocks the CPU down. Versus
  shield: fourth hit down pokes the shield.
- **Fail:** Sequence stops after hit 2 (inputs too fast) or Roy is grabbed.
- **Variations:** Third hit up (meteor) on a CPU hanging at the ledge.
- **Data needed:** continuation windows per swing (Marth's are listed on
  [wiki:Marth_(SSBM)/Side_special]; Roy's own were not read), hit frames per variant [fd].

### Counter the recovery

- **id:** `roy-counter-edgeguard`
- **Goal:** Time Counter against a recovery hitbox.
- **Player:** Roy
- **CPU:** Fox, Falco, Marth
- **Setup:** Roy at the ledge; CPU offstage at 50-100%.
- **CPU behaviour:** Recovers with up B or side B aimed at the ledge or at Roy, at a random
  delay.
- **Success:** Counter activates and the CPU is KO'd or sent back offstage.
- **Fail:** Counter whiffs (active only frames 8-20) or Roy is hit.
- **Variations:** CPU sometimes sweetspots the ledge without a hitbox reaching Roy (the right
  answer becomes edgehog or fsmash).
- **Data needed:** Counter window 8-20 of 59, counterattack frames 3-9; damage of each
  recovery hitbox.

### Reverse Blazer on Jigglypuff

- **id:** `roy-reverse-blazer-puff`
- **Goal:** Execute the reversed up B first hit for a ceiling KO.
- **Player:** Roy
- **CPU:** Jigglypuff (variants: Pichu, Mr. Game & Watch)
- **Setup:** Yoshi's Story, CPU at 0% directly behind and touching Roy (or landing on his
  shield for the OoS version).
- **CPU behaviour:** Stands, or does a bair on shield then lands.
- **Success:** CPU is KO'd off the top by the first hit.
- **Fail:** Not reversed, whiff, or CPU survives.
- **Variations:** Pokémon Stadium; out of shield.
- **Data needed:** reverse window (stick back on frames 10-11), first hit frame 9, set
  knockback 200 [wiki:Roy_(SSBM)/Up_special, fd]; ceiling heights.

### Recover low as a fastfaller

- **id:** `roy-recovery-angle`
- **Goal:** Choose the Blazer angle and use the side B stall to reach the ledge.
- **Player:** Roy
- **CPU:** Sheik, Marth
- **Setup:** Roy offstage in tumble at a random recoverable position.
- **CPU behaviour:** Random: edgehog, stand at the lip, or jump out with an aerial.
- **Success:** Roy is on the ledge or actionable on stage unpunished.
- **Fail:** KO or punished landing lag.
- **Variations:** No double jump.
- **Data needed:** Blazer distance at each angle; side B stall physics; Roy fall speed 2.4.

<!-- GENERATED:framedata -->
## Frame data

Extracted from the game's own files (`PlFe.dat`, NTSC 1.02) by `tools/melee_data/extract.py`; machine-readable copy in [`../framedata/roy.json`](../framedata/roy.json). Conventions are in [`../README.md`](../README.md#frame-data-conventions): frames are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` is the first frame the move can be interrupted, `Total` is the animation length (first actionable frame is IASA, or Total + 1), `Set KB` is weight-dependent set knockback, angle `Sakurai` is the special angle 361. `On shield` is the frame advantage when the first active frame hits a full hard shield (negative = the defender acts first). Projectile and article hitboxes (lasers, needles, turnips, missiles...) are not in fighter scripts and are not listed.

### Ground attacks

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Jab 1 | `jab1` | 4-7 | 5/6/3 | Sakurai | 30/5 | 60 | - | slash | 31 | 26 | 4 | -17 |  |
| Dash attack | `dash_attack` | 12-15 | 12/6 | 110/Sakurai | 70/35 | 55/60 | - | slash | 57 | 40 | 7 | -20 |  |
| Up tilt | `utilt` | 7-9 | 8/9/10/6 | 110/Sakurai | 35/20 | 120/118/116/100 | - | slash | 45 | 40 | 6 | -26 |  |
|  |  | 10-13 | 8/9/10/6 | 85/Sakurai | 35/20 | 120/118/116/100 | - | slash |  |  | 6 | -23 |  |
| Down tilt | `dtilt` | 8-10 | 10/12/6 | 80 | 90/70 | 40 | - | slash | 57 | 20 | 7 | -4 |  |
| Forward smash | `fsmash` | 12-14 | 20/12 | Sakurai | 80/30 | 65 | - | slash | 57 | 54 | 10 | -31 | charge hold frame 3 |
| Up smash | `usmash` | 15-16, 17-18, 19-20, 21-22 | 2 | 98/259 | 0 | 100 | 120 | fire | 62 | 46 | 2 | -28 | charge hold frame 8 |
|  |  | 23-24 | 10 | 90 | 73 | 90 | - | fire |  |  | 6 | -16 |  |
| Down smash | `dsmash` | 6-8 | 21/14 | 75/Sakurai | 42/15 | 70/100 | - | slash | 74 | 72 | 11 | -54 | charge hold frame 3 |
|  |  | 23-25 | 16/8 | 75/Sakurai | 42/15 | 68/100 | - | slash |  |  | 9 | -39 |  |

### Aerials

`Autocancel` `<a, >b`: landing before frame a or after frame b gives normal landing lag (4 frames) instead of the aerial's. `On shield (best)` assumes an L-cancelled landing on the frame after the hit.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | Land lag | L-cancel | Autocancel | On shield (best) | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral air | `nair` | 7-8 | 4 | 100/90 | 30 | 40 | - | slash | 57 | 50 | 3 | 20 | 10 | <7, >31 | -7 |  |
|  |  | 17-20 | 8/6 | Sakurai | 50 | 80 | - | slash |  |  | 5 |  |  |  | -5 |  |
| Forward air | `fair` | 5-7 | 8/5 | Sakurai | 30/10 | 70 | - | slash | 38 | 35 | 5 | 20 | 10 | <1, >29 | -5 |  |
| Back air | `bair` | 8-10 | 9/6 | Sakurai | 30/10 | 70 | - | slash | 45 | 43 | 6 | 24 | 12 | <1, >33 | -6 |  |
| Up air | `uair` | 5-10 | 6/9 | 80 | 10/20 | 70 | - | slash | 52 | 49 | 6 | 18 | 9 | <5, >29 | -3 |  |
| Down air | `dair` | 7-10 | 6/9 | 90/Sakurai/270 | 40 | 70 | - | slash | 68 | 64 | 6 | 32 | 16 | <7, >54 | -10 |  |

### Grabs and throws

| Move | Key | Grab box active | Total | Notes |
|-|-|-|-|-|
| Grab | `grab` | 7-8 | 30 | starts 1 frame late (included) |
| Dash grab | `dash_grab` | 10-11 | 40 | starts 1 frame late (included) |

| Move | Key | Total dmg | Throw dmg | Angle | BKB | KBG | Set KB | Effect | Release / hit | Total | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Pummel | `pummel` | 3 | - | - | - | - | - | - | 7 | 24 | starts 1 frame late (included) |
| Forward throw | `fthrow` | 5 | 5 | 45 | 70 | 45 | - | - | 14 | 31 |  |
| Back throw | `bthrow` | 5 | 5 | 117 | 70 | 45 | - | - | 7 | 44 |  |
| Up throw | `uthrow` | 5 | 5 | 97 | 60 | 130 | - | - | 12 | 44 |  |
| Down throw | `dthrow` | 6 | 6 | 120 | 65 | 60 | - | - | 14 | 42 |  |

### Special moves

One row per script (special moves are split into several states). Frames count from the start of that state; a few specials start one frame later in game than the script says, so treat +/-1 as unverified until checked in game.

| Move | Key | Active | Dmg | Angle | BKB | KBG | Set KB | Effect | Total | IASA | Shield stun | On shield | Notes |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Neutral B: Flare Blade, ground, Start | `special_n_start` | - | - | - | - | - | - | - | 11 | - | - | - |  |
| Neutral B: Flare Blade, ground, Loop | `special_n_loop` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Neutral B: Flare Blade, ground, End | `special_n_end` | 5-10 | 6 | Sakurai | 40 | 110 | - | fire | 33 | - | 4 | - |  |
| Neutral B: Flare Blade, ground, End | `special_n_end_298` | 9 | 50 | Sakurai | 50 | 83 | - | fire | 33 | - | 24 | - | self damage 10% on frame 9 |
| Neutral B: Flare Blade, air, Start | `special_air_n_start` | - | - | - | - | - | - | - | 11 | - | - | - |  |
| Neutral B: Flare Blade, air, Loop | `special_air_n_loop` | - | - | - | - | - | - | - | 29 | - | - | - |  |
| Neutral B: Flare Blade, air, End | `special_air_n_end` | 5-10 | 6 | Sakurai | 40 | 110 | - | fire | 33 | - | 4 | - |  |
| Neutral B: Flare Blade, air, End | `special_air_n_end_302` | 9 | 50 | Sakurai | 50 | 83 | - | fire | 33 | - | 24 | - | self damage 10% on frame 9 |
| Side B: Double-Edge Dance, ground, 1 | `special_s1` | 6-8 | 5/4 | 60/80/96/85 | 50/40 | 25 | - | slash | 29 | - | 4 | - |  |
| Side B: Double-Edge Dance, ground, 2Hi | `special_s2_hi` | 11-14 | 6/4 | 96 | 50 | 30 | - | slash | 39 | - | 4 | - |  |
| Side B: Double-Edge Dance, ground, 2Lw | `special_s2_lw` | 13-15 | 6/4 | 35/80/56/105 | 40/20 | 35/60 | - | slash | 39 | - | 4 | - |  |
| Side B: Double-Edge Dance, ground, 3Hi | `special_s3_hi` | 12-13 | 10/8 | 280/270 | 80/36 | 60/40 | - | slash | 45 | - | 6 | - |  |
|  |  | 14-16 | 7/5 | 60 | 60 | 60 | - | slash |  |  | 5 | - |  |
| Side B: Double-Edge Dance, ground, 3S | `special_s3_s` | 10-13 | 10/8 | Sakurai | 50 | 110 | - | slash | 45 | - | 6 | - |  |
| Side B: Double-Edge Dance, ground, 3Lw | `special_s3_lw` | 15, 17, 19 | 3 | 90/75/95 | 0/30 | 100 | 30 | fire | 45 | - | 3 | - |  |
|  |  | 21 | 5 | 64 | 70 | 100 | - | fire |  |  | 4 | - |  |
| Side B: Double-Edge Dance, ground, 4Hi | `special_s4_hi` | 19-24 | 13/10 | 40 | 22 | 130 | - | fire | 49 | - | 7 | - |  |
| Side B: Double-Edge Dance, ground, 4S | `special_s4_s` | 22-25 | 13/10 | Sakurai | 35 | 135 | - | fire | 49 | - | 7 | - |  |
| Side B: Double-Edge Dance, ground, 4Lw | `special_s4_lw` | 12-14, 18-20, 24-26, 30-32 | 3 | 80 | 2 | 40 | - | fire | 59 | - | 3 | - |  |
|  |  | 36-37 | 5 | Sakurai | 30 | 110 | - | fire |  |  | 4 | - |  |
| Side B: Double-Edge Dance, air, 1 | `special_air_s1` | 6-8 | 5/4 | 60/80/96/85 | 50/40 | 25 | - | slash | 29 | - | 4 | - |  |
| Side B: Double-Edge Dance, air, 2Hi | `special_air_s2_hi` | 11-14 | 6/4 | 96 | 50 | 30 | - | slash | 39 | - | 4 | - |  |
| Side B: Double-Edge Dance, air, 2Lw | `special_air_s2_lw` | 13-15 | 6/4 | 35/80/56/105 | 40/20 | 35/60 | - | slash | 39 | - | 4 | - |  |
| Side B: Double-Edge Dance, air, 3Hi | `special_air_s3_hi` | 12-13 | 10/8 | 60 | 60 | 60 | - | slash | 45 | - | 6 | - |  |
|  |  | 14-16 | 7/5 | 60 | 60 | 60 | - | slash |  |  | 5 | - |  |
| Side B: Double-Edge Dance, air, 3S | `special_air_s3_s` | 10-13 | 10/8 | Sakurai | 50 | 110 | - | slash | 45 | - | 6 | - |  |
| Side B: Double-Edge Dance, air, 3Lw | `special_air_s3_lw` | 15, 17, 19 | 3 | 90/75/95 | 0/30 | 100 | 30 | fire | 45 | - | 3 | - |  |
|  |  | 21 | 5 | 64 | 70 | 100 | - | fire |  |  | 4 | - |  |
| Side B: Double-Edge Dance, air, 4Hi | `special_air_s4_hi` | 19-24 | 13/10 | 40 | 22 | 130 | - | fire | 49 | - | 7 | - |  |
| Side B: Double-Edge Dance, air, 4S | `special_air_s4_s` | 22-25 | 13/10 | Sakurai | 35 | 135 | - | fire | 49 | - | 7 | - |  |
| Side B: Double-Edge Dance, air, 4Lw | `special_air_s4_lw` | 12-14, 18-20, 24-26, 30-32 | 3 | 80 | 2 | 40 | - | fire | 59 | - | 3 | - |  |
|  |  | 36-37 | 5 | Sakurai | 30 | 110 | - | fire |  |  | 4 | - |  |
| Up B: Blazer, ground | `special_hi` | 9 | 5/3 | 84/Sakurai | 0 | 100 | 200/80 | fire/slash | 48 | - | 4 | - | intangible 9 |
|  |  | 10-11, 12-13, 14-15 | 2/1 | 84/Sakurai | 0/10 | 100 | 160/0 | fire/slash |  |  | 2 | - |  |
|  |  | 16-17, 18-19, 20-21 | 1 | 84/Sakurai | 0/10 | 100 | 100/0 | fire/slash |  |  | 2 | - |  |
| Up B: Blazer, air | `special_air_hi` | 9 | 5/3 | 84/Sakurai | 0 | 100 | 200/80 | fire/slash | 48 | - | 4 | - | intangible 9 |
|  |  | 10-11, 12-13, 14-15 | 2/1 | 84/Sakurai | 0/10 | 100 | 160/0 | fire/slash |  |  | 2 | - |  |
|  |  | 16-17, 18-19, 20-21 | 1 | 84/Sakurai | 0/10 | 100 | 100/0 | fire/slash |  |  | 2 | - |  |
| Down B: Counter, ground | `special_lw` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Down B: Counter, ground, Hit | `special_lw_hit` | 3-9 | 1 | Sakurai | 30 | 90/70 | - | fire | 35 | - | 2 | - | intangible 1-5 |
| Down B: Counter, air | `special_air_lw` | - | - | - | - | - | - | - | 59 | - | - | - |  |
| Down B: Counter, air, Hit | `special_air_lw_hit` | 3-9 | 1 | Sakurai | 30 | 90/70 | - | fire | 35 | - | 2 | - | intangible 1-5 |

### Dodges and rolls

| Option | Key | Intangible / invincible | Hitbox | Total | IASA | Notes |
|-|-|-|-|-|-|-|
| Spot dodge | `spotdodge` | intangible 2-18 | - | 27 | - |  |
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
| Shield grab | direct | 7 | `grab` |
| Forward air | jump | 10 | `fair` |
| Up air | jump | 10 | `uair` |
| Up B | jump cancel | 10 | `special_hi` |
| Neutral air | jump | 12 | `nair` |
| Down air | jump | 12 | `dair` |
| Back air | jump | 13 | `bair` |
| Up smash | jump cancel | 16 | `usmash` |
| Spot dodge | direct | intangible 2-18 of 27 | `spotdodge` |
| Roll forward | direct | intangible 4-19 of 35 | `roll_forward` |
| Roll backward | direct | intangible 4-23 of 35 | `roll_backward` |
| Wavedash | jump | actionable on frame 17 | - |
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
## Resources

Community guides for Roy indexed by [The Melee Library](https://www.meleelibrary.com/#roy) (snapshot 2026-11-11). Videos cannot be read by an agent; use titles and descriptions as pointers to what the community considers important.

| Resource | Author | About |
|-|-|-|
| [2020 Roy Techs Guide](https://www.youtube.com/watch?v=qHR0OWz-uSc&list=PLQRQYzKDzrDo0LzNE4_UsAa4aOBoQG-7R&index=9&t=0s) | Third Chair | Video guide on performing useful Roy tech in 2020. |
| [Roy Melee Chaingrab Guide](https://www.youtube.com/watch?v=Nm98pKVdJgo&list=PLQRQYzKDzrDpwsHor3Ze1k31OKM08p9kl&index=4&t=0s) | Third Chair |  |
<!-- /GENERATED:resources -->

## Sources

- SSBWiki, Roy (SSBM), including "Differences from Marth":
  https://www.ssbwiki.com/Roy_(SSBM)
- SSBWiki move pages: https://www.ssbwiki.com/Roy_(SSBM)/Up_special , /Down_special ,
  /Neutral_special (timing tables); /Forward_smash and /Down_tilt had no prose
- SSBWiki technique pages: https://www.ssbwiki.com/Blazer , /Flare_Blade ,
  /Double-Edge_Dance , /Dancing_Blade , /Counter , /Tipper , /Ken_Combo , /Chain_grab ,
  /Sheik_(SSBM)/Down_throw , /Marth_(SSBM)/Forward_smash , /Dolphin_Slash ,
  /List_of_SSBM_tier_lists_(NTSC)
- "Collection of Sheik Stuff" (Magus's forced get-up thresholds):
  https://docs.google.com/document/d/1mlNwPWxO2y8u_w1t_jf_FzMx6OC8BJyFZ2fW-rOj9zk/
- Frame data dump: `Roy.json`
- Melee Library "Roy" section has two cards, both YouTube videos (2020 Roy Techs Guide, Roy
  Melee Chaingrab Guide); titles only.
