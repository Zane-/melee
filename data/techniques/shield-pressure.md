---
schema: melee-technique/v1
id: shield-pressure
name: Shield pressure
aliases: [pressure, frame advantage on shield, frame traps, shield break combo, tick throw, safe on shield]
category: offense
difficulty: 4
related: [shield, out-of-shield, shffl, l-cancel, jump-cancel, grab-and-throw, powershield, shield-drop]
characters: all
summary: Hitting a shield with sequences whose gaps are too small for the defender's out-of-shield options, to force a shield poke, a shield break, a bad escape or a grab.
---

# Shield pressure

## What it is

Attacking a shielding opponent so that every gap between hits is shorter than, or equal to,
what the defender needs to act. In Melee there are always some gaps in shieldstun, so the
goal is rarely a guaranteed shield break; it is to poke the shrinking shield, or to bait and
punish a roll, spot dodge, jump or shield grab, and to mix in a grab [wiki:Shieldstun].

## Inputs

There is no single input. The common building blocks:

- **Late, L-cancelled aerial on shield** ([SHFFL](shffl.md)): hit as low as possible, then
  act immediately after landing lag.
- **Aerial into fast ground move:** jab, [Fox](../characters/fox.md)/[Falco](../characters/falco.md)
  down B (shine), dtilt, grab.
- **Shine pressure (Fox/Falco):** shine, jump out of shine, then aerial (dair/nair) or
  [wavedash](wavedash.md) (waveshine) or another shine (multishine). A double shine covers
  the grab-sized gap left after a waveshine or a jump out of shine into an aerial
  [wiki:Shieldstun].
- **Cross-up:** land behind the shield so a shield grab whiffs.
- **Spacing:** hit with the tip of a disjoint ([Marth](../characters/marth.md) fair,
  [Sheik](../characters/sheik.md) ftilt) so shield grab cannot reach.
- **Grab mixup (tick throw):** when the defender holds shield waiting for the next hit,
  grab instead.

## Frame data and formulas

Frame advantage of the attacker after a hit on shield (positive = attacker acts first):

```
advantage = shieldstun - (attacker's remaining lag after the hit connects)
```

Both sides sit through the same hitlag for a physical hit, so it cancels out
(see [hitstun-knockback](hitstun-knockback.md)).

| Quantity | Value | Source |
|-|-|-|
| Shieldstun, full shield | floor((d x 0.45 + 2) x 200/201) | [wiki:Shield] |
| Hitlag | floor(d/3 + 3) | [wiki:Hitlag] |
| Remaining lag of a grounded move | total frames (or IASA) minus the frame it connected | [fd] fields `totalFrames`, `iasa`, `hitFrames` |
| Remaining lag of an aerial | frames until landing + landing lag (`lcancelledLandingLag` with [L-cancel](l-cancel.md), else `landingLag`), or normal 4-frame landing if [auto-cancelled](auto-cancel.md) | [fd], [wiki:Landing_lag] |
| Defender's fastest answers | shield grab frame 7 for most; jump squat 3-8; table in [out-of-shield](out-of-shield.md) | [lib:Out of Shield Options Frame Data] |
| Shield health | 60, x0.7 damage taken, -0.28 per frame held | [wiki:Shield] |
| Light shield | more shieldstun for the defender (up to about d x 1.4 + 2) | [wiki:Shieldstun] |
| Attacker pushback | d x 0.07 + 0.02 (full shield) | [wiki:Shield] |

A sequence is a **frame trap** against option X if the gap (in frames where the defender is
out of shieldstun before the next hitbox) is smaller than X's startup. Example targets:
shield grab needs 7 frames (most characters), [Fox](../characters/fox.md) shine out of
shield 4, [Marth](../characters/marth.md) up B 6, [Samus](../characters/samus.md) up B 5
[lib:Out of Shield Options Frame Data].

Published frame-advantage tables assume the aerial hits on the last possible frame before
landing and is L-cancelled; hitting earlier is worse by one frame per frame of height
[wiki:Out_of_shield].

## Why it matters

Shield is the strongest low-risk defensive option, and the top tiers are defined partly by
how well they beat it: Fox and Falco with shine pressure, Marth and Sheik with spacing and
grabs, Peach with float-cancelled aerials and dsmash (which also shield pokes and punishes
shield SDI errors), Captain Falcon with cross-ups and grabs. Defenders in turn need to know
which gaps are real, so both sides of every pressure drill use the same arithmetic.

## Common errors

- Missing the [L-cancel](l-cancel.md): landing lag doubles and the defender shield grabs.
  Hitting a shield adds hitlag before landing, so the L-cancel press comes later than on a
  whiffed aerial; a light shield is bigger, so the hit connects higher and earlier.
- Hitting too high on the shield (early aerial): large gap before landing.
- Landing in front, in grab range, after an aerial that is negative on shield.
- Shine too late after landing (gap big enough for a grab) or jump out of shine too slow.
- Autopilot: repeating one sequence so the defender buffers a roll or up B in the known gap.
- Never grabbing, so the defender can hold shield safely.

## How to detect it in a training mode

- Per hit on shield, log: frame the defender leaves `GuardSetOff`, frame the attacker's
  next hitbox becomes active, and the attacker's first actionable frame. Gap = next hitbox
  frame - defender's first free frame.
- Tight pressure: every gap is below a chosen threshold (e.g. below 7 to beat shield grabs,
  below the specific character's fastest out-of-shield option to be airtight).
- Outcome states for the defender: `Damage*` from `Guard*` (poke), `ShieldBreakFly`
  (break), `CapturePulledHi/Lw` (grabbed), `Catch` then whiff (their grab missed).
- L-cancel success is observable from the landing state duration (see [l-cancel](l-cancel.md)).

## Drill seeds

### Aerial into shine/jab frame trap

- **id:** `shield-pressure-aerial-followup-gap`
- **Goal:** Leave no shield-grab gap after a SHFFL aerial.
- **Player:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md), [Marth](../characters/marth.md)
- **CPU:** [Marth](../characters/marth.md), [Sheik](../characters/sheik.md), [Peach](../characters/peach.md) (frame 7 grabs)
- **Setup:** CPU shielding at centre stage, full shield health.
- **CPU behaviour:** Shield grabs on the first possible frame after shieldstun.
- **Success:** Player's follow-up (shine, jab, second aerial) hits or is shielded before the grab connects, N times in a row.
- **Fail:** Player is grabbed.
- **Variations:** CPU uses its fastest out-of-shield option instead (up B, nair); CPU light shields; CPU rolls away.
- **Data needed:** Aerial damage, L-cancelled landing lag, CPU out-of-shield frames.

### Mixed defender

- **id:** `shield-pressure-vs-random-escape`
- **Goal:** React to and punish the defender's escape option.
- **Player:** any
- **CPU:** any
- **Setup:** CPU in shield, player in pressure range.
- **CPU behaviour:** After the first or second blocked hit, randomly: keeps shielding, shield grabs, rolls in, rolls away, spot dodges, jumps out.
- **Success:** Player hits or grabs the CPU within N frames of its escape, or pokes/grabs the held shield.
- **Fail:** Player is hit or grabbed, or the CPU escapes to neutral.
- **Variations:** Limit the CPU to two options first; add up B out of shield for characters that have it.
- **Data needed:** Roll and spot dodge durations and intangibility ([web:fightcore.gg] values in [out-of-shield](out-of-shield.md)).

### Shield poke

- **id:** `shield-pressure-poke-low-shield`
- **Goal:** Hit the exposed part of a small shield.
- **Player:** any
- **CPU:** any
- **Setup:** CPU shielding with health set to about 20 of 60.
- **CPU behaviour:** Holds shield, optionally angles it up or down at random.
- **Success:** Player's hit puts the CPU in a `Damage*` state without a shield break.
- **Fail:** Hit is blocked three times.
- **Variations:** Different remaining health; CPU angles to cover.
- **Data needed:** Shield size formula, hurtbox layout.

## Sources

- SSBWiki: Shieldstun, Shield, Hitlag, Out of shield, Landing lag
  (https://www.ssbwiki.com/Shieldstun). The wiki's "Shield pressure" title redirects to a
  general mind-games page with no Melee data.
- Melee Library: "Out of Shield Options Frame Data" (Wiseman). "Frame Advantage on Shield"
  (KirbyKaze) and "Aerial Advantage" (SuperDoodleMan spreadsheet) are the community
  references for per-move advantage; they could not be fetched in this session.
- `[fd]`: the frame data dump described in the project brief.
- `[decomp]`: state names from this repository.
