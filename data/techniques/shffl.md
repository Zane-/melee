---
schema: melee-technique/v1
id: shffl
name: SHFFL
aliases: [short hop fast fall L-cancel, shuffle, SHFFL aerial]
category: offense
difficulty: 3
related: [short-hop, fast-fall, l-cancel, auto-cancel, shield-pressure, jump-cancel]
characters: all
summary: Short hop, aerial, fast fall and L-cancel done as one sequence, the fastest low-lag way to use an aerial from the ground for most characters.
---

# SHFFL

## What it is

A combination of three techniques around an aerial attack: [short hop](short-hop.md) (stay
low), [fast fall](fast-fall.md) (get down sooner) and [L-cancel](l-cancel.md) (halve the
landing lag). The result is an aerial that threatens grounded opponents and leaves the
attacker actionable soon after landing, so aerials can be combined with ground moves
[wiki:SHFFL].

## Inputs

In order [wiki:SHFFL]:

1. Jump (X/Y), released during jump squat for a short hop.
2. Aerial: A with a direction, or the C-stick. Timing depends on the move's startup and
   whether it should hit rising or falling.
3. Tap down on the control stick at or after the apex to fast fall.
4. Press L, R or Z within 7 frames before landing.

Steps 2 and 3 swap for slow aerials (fast fall first would land before the hitbox) and for
"late" aerials. If the aerial hits a character or shield, hitlag pushes the landing later,
so step 4 comes later than on a whiff [wiki:SHFFL].

## Frame data and formulas

| Component | Rule | Source |
|-|-|-|
| Short hop window | release jump within (jump squat - 1) frames | [wiki:Short_hop] |
| Jump squat | 3-8 frames, table in [short-hop](short-hop.md) | [wiki:Jump] |
| Fast fall | earliest on the first falling frame | [wiki:Fastfall] |
| L-cancel | within 7 frames before landing; during hitlag counts if landing is within 6 frames after hitlag | [wiki:L-canceling] |
| Hitlag on hit or shield | floor(damage/3 + 3) | [wiki:Hitlag] |
| Lag after landing | `lcancelledLandingLag` of the aerial | [fd] |
| When not to L-cancel | aerials that [auto-cancel](auto-cancel.md) in a short hop land with the normal 4 frames | [wiki:Auto-canceling] |

Total commitment of a SHFFL = jump squat + airtime of the fast-fallen short hop +
L-cancelled landing lag. Airtime per character is not in the sources read (measure in
engine). Whether a given aerial's hitbox comes out before landing in a fast-fallen short hop
depends on its first hit frame from the frame data dump and that airtime.

Frame advantage on shield of a SHFFL aerial that hits on the last airborne frame:

```
advantage = shieldstun - L-cancelled landing lag     (shieldstun in shield.md)
```

Each frame earlier that the aerial connects costs one frame [wiki:Out_of_shield].

## Why it matters

It is the default way to attack with aerials: approach, combo extension, and
[shield pressure](shield-pressure.md). The wiki notes it is a mistake to treat repeated
SHFFLs as more important than fundamentals and spacing, and that timing on a real target
differs from timing in the air because of hitlag [wiki:SHFFL].

## Common errors

- Full hop instead of short hop.
- Aerial too late: lands before the hitbox is out (often with full landing lag and no hit).
- Fast fall before the apex (no effect) or forgotten: floaty, slow aerial.
- L-cancel timed for a whiff when the move hit (too early), or the reverse.
- Hitting the top of a shield (aerial too early): large disadvantage even with L-cancel.
- No plan after landing: the SHFFL is only safe if followed by spacing, a fast move, or
  a shield.

## How to detect it in a training mode

Check each component independently and report which failed:

- Short hop: initial jump velocity after `KneeBend` (see [short-hop](short-hop.md)).
- Aerial: `AttackAir*` started N frames after leaving the ground; hitbox active before
  landing; connected or not.
- Fast fall: fast-fall flag set / vertical speed equals fast-fall speed; frames after apex.
- L-cancel: `LandingAir*` duration equals the halved value.
- Overall metric: frames from jump press to first actionable frame after landing, compared
  with the best possible for that character and aerial.

## Drill seeds

### SHFFL component report

- **id:** `shffl-component-feedback`
- **Goal:** Clean SHFFLs with per-component feedback.
- **Player:** any
- **CPU:** any, standing or shielding
- **Setup:** CPU at short range.
- **CPU behaviour:** Stands (hit timing) or shields (shield timing), alternating at random.
- **Success:** Short hop + aerial connects + fast fall + L-cancel all true.
- **Fail:** Any component false; show which.
- **Variations:** Each aerial; approaching vs in place vs retreating; whiff case.
- **Data needed:** Aerial frame data, landing lag, jump squat.

### SHFFL approach into combo

- **id:** `shffl-approach-followup`
- **Goal:** Convert a SHFFL hit into the next move without a gap.
- **Player:** [Fox](../characters/fox.md) (nair to shine/grab), [Falco](../characters/falco.md) (dair to shine), [Captain Falcon](../characters/captain-falcon.md) (nair to grab), [Sheik](../characters/sheik.md) (fair/nair), [Marth](../characters/marth.md) (fair)
- **CPU:** any
- **Setup:** CPU standing at mid range, low percent.
- **CPU behaviour:** After hitstun, shields or jumps away.
- **Success:** Second move hits while the CPU is still in hitstun.
- **Fail:** CPU escapes.
- **Variations:** CPU crouch cancels at low percent (see [crouch-cancel](crouch-cancel.md)); CPU DI.
- **Data needed:** Aerial knockback and hitstun, L-cancelled lag, follow-up startup.

### Late versus early aerial

- **id:** `shffl-late-aerial-on-shield`
- **Goal:** Hit the shield as late (low) as possible.
- **Player:** any
- **CPU:** any, shielding
- **Setup:** CPU in full shield.
- **CPU behaviour:** Shield grab on the first possible frame.
- **Success:** Aerial connects within the last 2 airborne frames, L-cancel succeeds, and the player's next action beats the grab.
- **Fail:** Grabbed.
- **Variations:** Cross-up; light shield.
- **Data needed:** Shieldstun formula, landing lag, CPU grab frame.

## Sources

- SSBWiki: Short hop fast fall L-cancel (SHFFL), Short hop, Fast fall, L-canceling,
  Auto-canceling, Hitlag, Out of shield (https://www.ssbwiki.com/SHFFL).
- `[fd]`: project frame data dump. State names from this repository's decomp.
