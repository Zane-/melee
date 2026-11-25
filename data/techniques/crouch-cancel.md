---
schema: melee-technique/v1
id: crouch-cancel
name: Crouch cancel
aliases: [CC, crouch cancelling, crouch cancel counter, CC counter]
category: defense
difficulty: 2
related: [asdi, hitstun-knockback, di, teching, shield, grab-and-throw]
characters: all
summary: Being hit while crouching multiplies knockback and hitlag by 2/3, and holding down makes the character land immediately, so weak and mid-strength hits can be absorbed and punished.
---

# Crouch cancel

## What it is

If a character is in a crouching state when hit, the knockback and the victim's hitlag are
multiplied by 0.666667 [wiki:Knockback] [wiki:Hitlag]. Because the player is holding down,
they normally also [ASDI](asdi.md) down, which puts them back on the ground on the first
frame after hitlag; landing in non-tumble hitstun puts the character in the normal landing
animation, which lasts as long as the hitstun but can be left for an attack, a grab, a shine,
a jump or a dash after the normal landing lag (4 frames for most characters:
`ftCo_Landing_IASA`; seen on the native build, 2026-11-13) [wiki:Crouch_cancel] [wiki:Hitstun].
The two effects together are what players call crouch cancelling:

- the 2/3 factor keeps the hit below the tumble threshold (80 knockback) until a much higher
  percent, and
- ASDI down removes almost all the stun as long as the hit does not tumble.

The result: the crouching player takes the damage, slides a little, and can act (usually
counterattack) long before the attacker recovers.

## Inputs

1. Be crouching (hold down on the ground; states `Squat` or `SquatWait`, **not** `SquatRv`,
   the standing up: `ftCo_Damage.c`, `ftcommon.c`) at the moment the hit connects.
2. Keep holding down until hitlag ends so ASDI down applies.
3. Act as soon as the landing can be left (after the normal landing lag): the "crouch
   cancel counter" is typically dsmash, dtilt, grab or shine.

To survive a strong horizontal hit instead, switch the stick from down to up-and-in during
hitlag ([DI](di.md)); this is tight because crouch cancel also shortens hitlag
[wiki:Crouch_cancel].

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Knockback multiplier when crouching | 0.666667 | [wiki:Knockback] |
| Hitlag multiplier (victim only; attacker keeps full hitlag) | 0.666667 | [wiki:Hitlag] |
| Stun after a crouch-cancelled non-tumble hit with ASDI down | normal landing lag, 4 frames for most characters | [wiki:Crouch_cancel] |
| Hit stops being absorbable | when KB after the 2/3 factor exceeds 80 (tumble): the victim bounces/knocks down unless they tech | [wiki:Hitstun] [wiki:Tumbling] |
| Unmodified KB at which crouch cancel fails | above 120 (80 / 0.666667), derived from the two facts above | derived |
| Throws | cannot be crouch cancelled; a grab removes the crouch | [wiki:Crouch_cancel] |

Hits that crouch cancel does **not** neutralise [wiki:Crouch_cancel]:

- Moves that do not lift the victim off the ground: 0-degree hits, Sakurai-angle hits below
  32 KB, and downward hits (meteors/spikes such as [Fox](../characters/fox.md) dair,
  [Falco](../characters/falco.md) dair). The victim stays in grounded hitstun (reduced by
  2/3 only).
- Multi-hit moves: only the first hit is crouch cancelled if the next hit arrives before the
  victim can crouch again. [Peach](../characters/peach.md) dsmash can land up to five hits
  on a player who keeps holding down.
- Grabs.

Percent thresholds: the Melee Library lists "80KB Percents for All Moves" (V_D_X) as the
table of percents at which each move breaks crouch cancel and [ASDI down](asdi.md); it
could not be fetched here. A drill generator can compute them from the knockback formula in
[hitstun-knockback](hitstun-knockback.md): find the smallest percent where
KB x 0.666667 > 80 (crouch cancel) or KB > 80 (ASDI down alone).

<!-- cc-limits: python tools/melee_drills/cc_limits.py --table -->
Measured in this build (`python tools/melee_drills/cc_limits.py`, every character in
`data/actor/crouch_cancel.json`): the most damage, before the hit, at which a crouching
character stays on its feet. One percent more and the hit tumbles it. Listed for the
distances (units between the two) the move hit all 26 crouching characters from; where a
move has a weak and a strong part the least is given, and the last column says how far
the distances differ.

| Opponent | Move | From | Fox holds to | Pichu | Bowser | By distance |
|-|-|-|-|-|-|-|
| Fox | down tilt | 12, 18 | 50% | 43% | 64% | the same from each |
| Fox | forward smash | 12, 18, 24, 30 | 48% | 41% | 64% | up to 30 more from another |
| Fox | down smash | 12 | 84% | 73% | 108% | the same from each |
| Fox | dash attack | 18, 24, 30 | 99% | 87% | 124% | the same from each |
| Marth | down tilt | 12, 18, 24, 30 | 153% | 134% | 247% | up to 98 more from another |
| Marth | forward tilt | 12, 18, 24 | 116% | 36% | 146% | up to 83 more from another |
| Marth | jab | 18, 24 | 200% | 176% | 260+ | up to 84 more from another |
| Marth | forward smash | 12, 18, 24, 30 | 38% | 32% | 51% | up to 43 more from another |
| Marth | down smash | 12, 18, 24, 30 | 6% | 3% | 50% | up to 71 more from another |
| Marth | dash attack | 30 | 131% | 115% | 75% | the same from each |
| Jigglypuff | down tilt | 12, 18 | 249% | 219% | 260+ | the same from each |
| Jigglypuff | forward tilt | 12 | 87% | 76% | 111% | the same from each |
| Jigglypuff | jab | 12 | 260+ | 260+ | 260+ | the same from each |
| Jigglypuff | forward smash | 12, 18, 24 | 32% | 26% | 44% | the same from each |
| Jigglypuff | down smash | 12 | 88% | 76% | 112% | the same from each |
| Jigglypuff | dash attack | 12, 18, 24, 30 | 64% | 56% | 83% | up to 51 more from another |
| Falco | down tilt | 12, 18 | 35% | 29% | 46% | the same from each |
| Falco | forward smash | 18, 24, 30 | 29% | 24% | 40% | up to 26 more from another |
| Falco | down smash | 12, 18 | 70% | 60% | 91% | the same from each |
| Falco | dash attack | 18, 24, 30 | 77% | 67% | 98% | up to 60 more from another |
| Sheik | down tilt | 12, 18 | 102% | 89% | 128% | the same from each |
| Sheik | forward tilt | 18 | 79% | 69% | 99% | the same from each |
| Sheik | forward smash | 12, 18, 24, 30 | 71% | 61% | 91% | up to 197 more from another |
| Sheik | down smash | 12, 18 | 60% | 52% | 78% | up to 194 more from another |
| Sheik | dash attack | 24, 30 | 60% | 52% | 77% | the same from each |
| Captain Falcon | down tilt | 12, 18, 24 | 85% | 73% | 108% | the same from each |
| Captain Falcon | dash attack | 12, 18, 24, 30 | 84% | 73% | 107% | up to 168 more from another |
| Peach | down tilt | 12, 18 | 25% | 21% | 34% | the same from each |
| Peach | forward tilt | 12 | 55% | 58% | 71% | the same from each |
| Peach | forward smash | 12 | 88% | 77% | 63% | the same from each |
| Peach | down smash | 12 | falls at 0% | falls at 0% | 14% | the same from each |
| Peach | dash attack | 24 | 35% | 30% | 47% | the same from each |
| Ice Climbers | down tilt | 12, 18 | 119% | 104% | 61% | the same from each |
| Ice Climbers | forward tilt | 12, 18 | 29% | 68% | 40% | up to 65 more from another |
| Ice Climbers | jab | 12, 18 | 260+ | 260+ | 236% | up to 33 more from another |
| Ice Climbers | forward smash | 12, 18 | falls at 0% | 13% | falls at 0% | up to 39 more from another |
| Ice Climbers | down smash | 12 | falls at 0% | 13% | 27% | the same from each |
| Pikachu | down tilt | 12, 18 | 117% | 103% | 147% | the same from each |
| Pikachu | forward tilt | 12, 18 | 106% | 93% | 134% | the same from each |
| Pikachu | jab | 12, 18 | 260+ | 260+ | 260+ | the same from each |
| Pikachu | forward smash | 12, 18, 24 | 25% | 20% | 36% | up to 20 more from another |
| Pikachu | down smash | 12 | falls at 0% | 11% | falls at 0% | the same from each |
| Pikachu | dash attack | 12, 18, 24, 30 | 112% | 98% | 141% | the same from each |
| Yoshi | down tilt | 12, 18 | 260+ | 260+ | 260+ | the same from each |
| Yoshi | forward tilt | 12, 18 | 61% | 52% | 78% | the same from each |
| Yoshi | jab | 12, 18 | 260+ | 260+ | 260+ | the same from each |
| Yoshi | forward smash | 12, 18 | 36% | 30% | 49% | the same from each |
| Yoshi | down smash | 12, 18, 24 | 44% | 38% | 58% | up to 22 more from another |
| Yoshi | dash attack | 18, 24, 30 | 89% | 78% | 113% | the same from each |
| Samus | down tilt | 12, 18, 24 | 24% | 19% | 33% | the same from each |
| Samus | forward tilt | 12 | 85% | 74% | 108% | the same from each |
| Samus | forward smash | 12, 18 | 39% | 33% | 52% | the same from each |
| Samus | down smash | 12, 18 | falls at 0% | falls at 0% | falls at 0% | the same from each |
| Samus | dash attack | 12, 18, 24 | 49% | 42% | 64% | up to 218 more from another |
<!-- /cc-limits -->

## Why it matters

- At low percent it beats most single-hit approaches: the attacker hits, the defender
  absorbs and punishes during the attacker's lag. Players may act earlier than they could
  after shielding the same move, and with their whole moveset [wiki:Crouch_cancel].
- Characters known for it: [Peach](../characters/peach.md) (crouch cancel dsmash),
  [Sheik](../characters/sheik.md), [Marth](../characters/marth.md) (dtilt),
  [Samus](../characters/samus.md), [Ice Climbers](../characters/ice-climbers.md),
  [Fox](../characters/fox.md)/[Falco](../characters/falco.md) (shine).
- It forces the attacker to use grabs, multi-hits, downward/horizontal hits or strong moves
  at low percent, which shapes neutral in many matchups.

## Common errors

- Crouching past the threshold percent: the hit tumbles and the victim is knocked down at
  the attacker's feet (in game: a bounce on the floor instead of a slide).
- Releasing down before hitlag ends: the 2/3 factor applies but there is no ASDI down, so
  the character is popped up in full (reduced) hitstun.
- Crouch cancelling a strong horizontal move near the ledge and holding down: DI down
  lowers the trajectory and the character dies earlier than with good DI.
- Crouching against a grab or a spike.
- Slow counter: the 4-frame landing ends but the player reacts late and the attacker shields.

## How to detect it in a training mode

- Crouch cancel applied: the victim was in `Squat`, `SquatWait` or `SquatRv` on the frame
  the hit registered [decomp]. (The game applies the 2/3 factor itself.)
- Successful absorb: victim goes from the `Damage*` state to `Landing` on the first frame
  after hitlag, instead of `DamageFly*`.
- Broken crouch cancel: victim enters `DamageFly*` then `DownBound*` (missed tech) or
  `Passive*` (tech).
- Counter success: victim's attack hits while the attacker is still in the lag of the
  original move; report frames between the end of `Landing` and the counter's first frame.

## Drill seeds

### Crouch cancel counter

- **id:** `crouch-cancel-counter-low-percent`
- **Goal:** Absorb an approach and punish it.
- **Player:** [Peach](../characters/peach.md), [Sheik](../characters/sheik.md), [Marth](../characters/marth.md), [Samus](../characters/samus.md), [Fox](../characters/fox.md)
- **CPU:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md)
- **Setup:** Final Destination, player at 0-30%, CPU at mid range.
- **CPU behaviour:** Approaches with a single-hit move (nair, dash attack, ftilt), L-cancels, then shields when actionable.
- **Success:** Player is hit while crouching, lands, and hits or grabs the CPU before it can shield.
- **Fail:** Player shields/dodges instead, is knocked down, or counters too late.
- **Variations:** Raise player percent each success until the move breaks crouch cancel; CPU sometimes grabs instead (player must not crouch into it).
- **Data needed:** CPU move knockback data and lag; player weight; landing lag.

### Know the threshold

- **id:** `crouch-cancel-threshold-recognition`
- **Goal:** Stop crouching once the move would knock down.
- **Player:** any
- **CPU:** any
- **Setup:** Player percent is shown and randomised around the computed threshold for one CPU move.
- **CPU behaviour:** Uses that move.
- **Success:** Below threshold: crouch cancel and counter. Above: shield or avoid instead.
- **Fail:** Knocked down while crouching, or shielded when crouch cancel would have worked.
- **Variations:** Different CPU moves; stale moves.
- **Data needed:** Knockback formula, threshold percent per move and character.

### Beating crouch cancel

- **id:** `crouch-cancel-beat-the-croucher`
- **Goal:** As the attacker, choose options that beat a crouching opponent.
- **Player:** any
- **CPU:** [Peach](../characters/peach.md), [Sheik](../characters/sheik.md), [Marth](../characters/marth.md)
- **Setup:** CPU at low percent, crouching at mid range.
- **CPU behaviour:** Crouch cancels any hit and counters with dsmash/dtilt/grab; shields or spot dodges at random to punish obvious grabs.
- **Success:** Player lands a grab, a move that keeps the CPU grounded in hitstun (downward or 0-degree hit), or a hit strong enough to tumble.
- **Fail:** Player's hit is crouch cancelled and punished.
- **Variations:** CPU percent sweep.
- **Data needed:** Move angles and knockback, grab ranges.

## Sources

- SSBWiki: Crouch cancel, Knockback, Hitlag, Hitstun, Tumbling
  (https://www.ssbwiki.com/Crouch_cancel).
- Melee Library: "A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling"
  (Doraki, read through the Wayback Machine) for the split between the knockback reduction
  and ASDI down; "80KB Percents for All Moves" (V_D_X) not readable.
- `[decomp]`: state names from this repository.
