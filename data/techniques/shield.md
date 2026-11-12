---
schema: melee-technique/v1
id: shield
name: Shield
aliases: [shielding, guard, light shield, shieldstun, shield pushback, shield poke, shield break, shield DI]
category: defense
difficulty: 1
related: [powershield, out-of-shield, shield-drop, shield-pressure, grab-and-throw, crouch-cancel, sdi]
characters: all
summary: Holding L/R on the ground raises a bubble that blocks hits at the cost of shield health, shieldstun and pushback; the exact stun and health formulas decide what is punishable.
---

# Shield

## What it is

A grounded defensive state. The shield comes out on the first frame the input is read and
blocks any hitbox that touches the bubble instead of the body. It loses health while held and
when hit, shrinks as it loses health, and breaks at zero. It does not block grabs.
In Melee the shield is analog: a partial trigger press gives a **light shield** (bigger,
drains slower, but more shieldstun and pushback) [wiki:Shield].

## Inputs

- Hold L or R (digital click = full "hard" shield). Partial press = light shield. Holding Z
  after a grab or after another action's lag gives a near-lightest shield (analog level
  s = 0.35) [wiki:Shield].
- Tilt the control stick slightly to shift the bubble (shield angling). A fast tilt left or
  right rolls, down spot dodges, up jumps (tap jump) [wiki:Shield].
- Release to drop shield: 15 frames of `GuardOff` (16 for [Yoshi](../characters/yoshi.md))
  [wiki:Out_of_shield].
- The shield must stay up at least 8 frames before it can be dropped [wiki:Shield].
- C-stick held during shieldstun buffers a jump (up), roll (left/right) or spot dodge (down)
  on the first frame after shieldstun [wiki:Shieldstun].

## Frame data and formulas

### Shield health

| Property | Value (full hard shield) | Source |
|-|-|-|
| Maximum health | 60 | [wiki:Shield] |
| Damage multiplier (damage taken by the shield) | 0.7 x attack damage, so about 85.71 effective HP | [wiki:Shield] |
| Depletion while held | 0.28 per frame (16.8 per second); a full shield lasts about 3.58 s | [wiki:Shield] |
| Regeneration while down | 0.07 per frame (4.2 per second); near-empty to full takes about 14.22 s | [wiki:Shield] |
| Health after a shield break | 30 | [wiki:Shield] |
| Size multiplier | (HP x 0.5 / 60) x 0.85 + 0.15 | [wiki:Shield] |

Some hitboxes add **bonus shield damage** on top (fixed, not affected by staling or charge).
Examples: [Marth](../characters/marth.md) neutral B (Shield Breaker) 30/38 uncharged and 60
fully charged, [Jigglypuff](../characters/jigglypuff.md) side B (Pound) 20,
[Donkey Kong](../characters/donkey-kong.md) side B 30, [Peach](../characters/peach.md)
usmash 4, [Sheik](../characters/sheik.md) usmash first hit 4, [Samus](../characters/samus.md)
bombs 6, most dash attacks, edge attacks and floor attacks 1 [wiki:Shield_damage].

### Shieldstun

```
shieldstun = floor( (d * (a + 0.3) * 1.5 + 2) * 200/201 )
a = 0.65 * (1 - (s - 0.3)/0.7)
```
d = attack damage rounded down, s = analog shield level (n/140, n from 43 to 140; full press
s = 1, so a = 0) [wiki:Shieldstun].

- Full shield simplifies to floor((d x 0.45 + 2) x 200/201) [wiki:Shield].
- Lightest shield is about d x 1.4 + 2 [wiki:Shieldstun].
- Example from the wiki: a 13% hit gives 7 frames on a full shield and 20 on the lightest
  [wiki:Shieldstun]. Other full-shield values computed from the formula: 4% gives 3,
  9% gives 6, 12% gives 7, 15% gives 8, 17% gives 9, 20% gives 10.
- The defender also sits through **hitlag** first: floor(d/3 + 3) frames, same as the
  attacker for melee hits (see [hitstun-knockback](hitstun-knockback.md)).
- During shieldstun the defender cannot jump, grab, roll or spot dodge [wiki:Shieldstun].
- [Yoshi](../characters/yoshi.md) takes no shieldstun except during the first 4 frames of
  shield startup (then 5 minus the shield frame number), and cannot jump out of shield
  outside the first 6 frames of a digital press [wiki:Shieldstun] [wiki:Shield].

### Pushback

| Who | Formula (full shield) | Source |
|-|-|-|
| Defender | (d x 0.09 + 0.4) x 0.6, capped at 2; factor is 1 instead of 0.6 for a [powershield](powershield.md) | [wiki:Shield] |
| Attacker | d x 0.07 + 0.02, no cap | [wiki:Shield] |

Pushback is an initial slide speed; how far the character slides then depends on traction
(table in [wavedash](wavedash.md)).

### Light shield (analog) effects

All use s = n/140 as above [wiki:Shield].

| Attribute | Formula | Lightest shield result |
|-|-|-|
| Damage multiplier | 0.7 + 0.2 x (1 - (s-0.3)/0.7) | 0.898 |
| Depletion per frame | (1.9 x (s-0.3)/0.7 + 0.1) x 0.14 | 0.0167 (about 1 per second) |
| Shieldstun | see above | (d x 1.415 + 2) x 200/201 |
| Defender pushback | (d x (0.195 x (1-(s-0.3)/0.7) + 0.09) + 0.4) x shield factor | (d x 0.283 + 0.4) x factor |
| Attacker pushback | d x ((s-0.3) x 0.1) + 0.02 | d x 0.000714 + 0.02 |

### Shield SDI and shield ASDI

During hitlag on shield the defender can SDI horizontally only; each input moves 0.66 of a
normal SDI input. Shield ASDI is half of that and is applied on the first frame of shieldstun
[wiki:Smash_directional_influence]. Used to slide out of multi-hit moves such as
[Peach](../characters/peach.md) dsmash, or to slide off a platform edge.

### Shield break and shield poke

- At 0 health the shield breaks: the character is popped up, lands knocked down, then is
  stunned (`Furafura`). Stun is longer at low percent and can be shortened by mashing
  [wiki:Shield]. [Jigglypuff](../characters/jigglypuff.md) is launched with 300 vertical
  knockback and dies unless there is a ceiling [wiki:Shield].
- A shrunken shield leaves hurtboxes outside the bubble. A hit that touches body before
  bubble is a **shield poke** and hits normally [wiki:Shield].
- A shielding character pushed off an edge by pushback slides off and tumbles
  [wiki:Tumbling].

## Why it matters

Shield is the default answer to an attack, and almost every punish starts from it. Whether a
move is "safe on shield" is arithmetic: attacker's remaining lag after hitlag versus
shieldstun plus the defender's fastest [out-of-shield](out-of-shield.md) option. Melee has
little shieldstun, so many grounded moves are punishable and attackers rely on
[L-cancelled](l-cancel.md) aerials and [shield pressure](shield-pressure.md).

## Common errors

- Holding shield too long: it shrinks and gets poked (feet and head first).
- Light shielding by accident (soft trigger press): more stun and pushback, punish is lost.
- Rolling or spot dodging out of habit after blocking, which a waiting attacker punishes.
- Trying to act during shieldstun; in Melee the input is lost (no buffer except C-stick).
- Shielding near a ledge facing the stage: pushback slides the defender off.

## How to detect it in a training mode

- States: `GuardOn` (startup), `Guard` (hold), `GuardSetOff` (shieldstun), `GuardOff`
  (dropping), `GuardReflect` (projectile reflect, see [powershield](powershield.md))
  [decomp].
- Shield health and analog level are fighter fields (`shield_health`, `lightshield_amount`
  in this repo [decomp]). Full shield = 60.
- "Blocked": defender enters `GuardSetOff`. "Poked": defender enters a `Damage*` state from
  a `Guard*` state. "Broken": `ShieldBreakFly`.
- Frame advantage for a drill = (frame the defender leaves `GuardSetOff`) minus (first
  actionable frame of the attacker).

## Drill seeds

### Hold shield without being poked

- **id:** `shield-angle-vs-poke`
- **Goal:** Learn to angle the shield to cover the exposed part.
- **Player:** any
- **CPU:** [Marth](../characters/marth.md), [Fox](../characters/fox.md), [Sheik](../characters/sheik.md)
- **Setup:** Player in shield with health set to about half; CPU in range.
- **CPU behaviour:** Randomly attacks high (e.g. descending aerial) or low (dtilt).
- **Success:** Player stays in `Guard`/`GuardSetOff` for N attacks.
- **Fail:** Player enters a `Damage*` state.
- **Variations:** Lower starting shield health; light shield allowed or not.
- **Data needed:** Shield size formula, CPU hitbox positions.

### Punish or hold: frame advantage quiz

- **id:** `shield-safe-or-unsafe`
- **Goal:** Learn which of an opponent's moves are punishable after shielding.
- **Player:** any
- **CPU:** any
- **Setup:** Player shielding; CPU performs one move from a pool on the shield.
- **CPU behaviour:** After the move, shields as soon as actionable.
- **Success:** If the move was unsafe (shieldstun + player's fastest option less than CPU lag), the player's hit or grab connects before the CPU shields. If it was safe, the player does not get hit by the CPU's follow-up.
- **Fail:** Missed a guaranteed punish, or attacked after a safe move and got hit.
- **Variations:** CPU spaces the move at max range; CPU hits late on shield.
- **Data needed:** Damage of each CPU move (for hitlag and shieldstun), CPU lag, player's out-of-shield frames.

### Light shield slide-off

- **id:** `shield-light-shield-edge`
- **Goal:** Learn when light shield pushback helps (sliding to ledge) or hurts.
- **Player:** any
- **CPU:** [Marth](../characters/marth.md)
- **Setup:** Player near the ledge, back to it; CPU does fsmash on shield.
- **CPU behaviour:** Fsmash at fixed timing.
- **Success:** Player light shields, slides off and grabs ledge (`CliffCatch`).
- **Fail:** Player is hit, or stays on stage in shieldstun.
- **Variations:** Platform edge instead of ledge.
- **Data needed:** Light shield pushback formula, traction.

## Sources

- SSBWiki: Shield, Shieldstun, Shield damage, Out of shield, Smash directional influence,
  Tumbling (https://www.ssbwiki.com/Shield and sibling pages).
- `[decomp]`: state and field names from this repository (`src/melee/ft/forward.h`,
  `src/melee/ft/types.h`).
- Melee Library cards on this topic not readable here (video or 403): "All About Shields"
  (CDK), "Frame Advantage on Shield" (KirbyKaze), "Light Shield L Cancel" (MikeHaze).
