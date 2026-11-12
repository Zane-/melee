---
schema: melee-technique/v1
id: powershield
name: Powershield
aliases: [power shield, perfect shield, PS, powershield cancel, projectile reflect]
category: defense
difficulty: 5
related: [shield, out-of-shield, shield-pressure, crouch-cancel]
characters: all
summary: Blocking a hit in the first frames of a hard shield takes no shield damage, lets you attack straight out of shield against physical hits, and reflects projectiles.
---

# Powershield

## What it is

If an attack touches the shield during the first few frames after a full (digital) shield
press, the game registers a powershield: a flash and a distinct sound, no shield damage, and
a special follow-up property that depends on what was blocked [wiki:Perfect_shield].

- **Physical attack:** hitlag and shieldstun are the same as a normal shield, but the
  defender can cancel the shield-drop animation into any ground action ("powershield
  cancel"), a 1-frame delay instead of the usual 15 [wiki:Perfect_shield].
- **Projectile:** the projectile is reflected at half its damage, the defender takes no
  shieldstun, and there is no powershield cancel [wiki:Perfect_shield].

## Inputs

1. Press L or R fully (digital click) so that the incoming hitbox touches the shield within
   the window below.
2. Physical hit: after shieldstun, release shield and input the punish; the attack comes
   out during the shield drop.
3. Projectile: nothing more; act immediately.

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Window against physical attacks | first 4 frames of the shield | [wiki:Perfect_shield] |
| Window against projectiles (reflect) | first 2 frames of the shield | [wiki:Perfect_shield] |
| Shield damage taken | 0 | [wiki:Perfect_shield] |
| Shieldstun, physical | same as a normal full shield (see [shield](shield.md)) | [wiki:Perfect_shield] |
| Shieldstun, projectile | none | [wiki:Perfect_shield] |
| Defender pushback factor | 1 instead of 0.6, so more pushback than a normal shield: (d x 0.09 + 0.4) x 1, cap 2 | [wiki:Shield] |
| Powershield cancel delay | 1 frame instead of the 15-frame shield drop | [wiki:Perfect_shield] |
| Reflected projectile damage | half | [wiki:Perfect_shield] |

Worked example from the wiki: [Falco](../characters/falco.md)'s jab hits on frame 2. From a
normal shield it is a frame 17 option (15 drop + 2); from a powershield it is a frame 3
option [wiki:Perfect_shield].

Character exceptions:

- [Yoshi](../characters/yoshi.md): different rules. His shield startup "parries" physical
  hits in the first frames instead; he can powershield physical hits at any time while
  shielding because the powershield bubble stays active, but he cannot powershield cancel
  [wiki:Perfect_shield] [wiki:Shield].
- A Melee Library note (Mahie's card, annotated by the curator) says crouching first makes
  powershielding easier only for [Marth](../characters/marth.md),
  [Roy](../characters/roy.md) and [Samus](../characters/samus.md) because of how their
  shields are programmed [lib:Crouch to Make Powershielding Easier]. The linked post itself
  was not readable.

## Why it matters

- The main answer to [Falco](../characters/falco.md) lasers and other projectile walls
  ([Sheik](../characters/sheik.md) needles, [Samus](../characters/samus.md) missiles,
  [Young Link](../characters/young-link.md) projectiles): a powershield reflects the laser
  and leaves the defender free to move at once.
- Against physical hits it converts moves that are safe on a normal shield into punishable
  ones, because any grounded attack is available with 1 frame of delay.
- Costs: more pushback (can push the defender out of punish range, worse for low-traction
  characters); too early gives a normal shield, too late gets hit [wiki:Perfect_shield].

## Common errors

- Pressing too early: normal shield, full shieldstun, laser pressure continues.
- Pressing too late: hit (against lasers: laser hitstun, usually followed by an aerial).
- Light press (analog only): never powershields; the window requires the hard shield.
- Powershielding a physical hit and then acting as if it were a normal shield (jumping or
  grabbing only), wasting the cancel.
- Against lasers at close range: reflecting but still being hit by Falco's following aerial
  because the player stopped to watch.

## How to detect it in a training mode

- Projectile powershield: the defender enters the `GuardReflect` state; in this
  repository's `ftCo_Guard.c` that state is entered from the shield's reflect callback
  [decomp]. Physical powershield: the state after the hit was not traced; do not assume
  `GuardReflect`. Observable conditions instead: the hit touched the shield within the
  first 4 frames of `GuardOn`/`Guard` after a digital press, and shield health did not
  drop.
- Timing feedback: count frames from the first frame of `GuardOn` to the frame the hitbox
  touched. 1-2 = projectile powershield, 1-4 = physical powershield, more = late shield
  ("N frames early"); hit before the press = "N frames late".
- Powershield cancel success: an attack state begins while the defender would otherwise
  still be in `GuardOff`.
- Projectile reflect: the projectile's owner changes to the defender and it travels back.

## Drill seeds

### Laser powershield

- **id:** `powershield-falco-laser`
- **Goal:** Reflect short hop lasers on reaction/rhythm.
- **Player:** any
- **CPU:** [Falco](../characters/falco.md) (also [Fox](../characters/fox.md) for no-stun lasers)
- **Setup:** Final Destination, CPU at one side, player at mid range.
- **CPU behaviour:** Short hop laser at randomised intervals and heights (high, low).
- **Success:** Player enters `GuardReflect` and the laser is reflected.
- **Fail:** Laser hits the player, or a normal shield is hit (report frames early/late).
- **Variations:** Approaching lasers; laser then aerial (player must punish after reflecting); different distances.
- **Data needed:** Laser travel speed, Falco short hop laser timing.

### Powershield punish

- **id:** `powershield-cancel-punish`
- **Goal:** Use powershield cancel to punish a move that is safe on normal shield.
- **Player:** any
- **CPU:** [Marth](../characters/marth.md), [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md)
- **Setup:** CPU at fixed spacing performs one telegraphed move (e.g. spaced ftilt).
- **CPU behaviour:** Attack, then shield as soon as actionable.
- **Success:** Player powershields and lands a grounded attack before the CPU can shield.
- **Fail:** Normal shield, got hit, or punish too slow.
- **Variations:** Random delay before the CPU attack; pool of moves.
- **Data needed:** CPU move frame data, shieldstun formula, player's fastest ground moves.

### Needle and missile reflect

- **id:** `powershield-projectile-mix`
- **Goal:** Generalise projectile powershield timing.
- **Player:** any
- **CPU:** [Sheik](../characters/sheik.md), [Samus](../characters/samus.md), [Young Link](../characters/young-link.md), [Mario](../characters/mario.md)
- **Setup:** CPU at long range.
- **CPU behaviour:** Fires its projectile at random intervals.
- **Success:** The projectile is reflected (`GuardReflect`).
- **Fail:** Hit or normal shield.
- **Variations:** Player must dash forward between projectiles.
- **Data needed:** Projectile speeds.

## Sources

- SSBWiki: Perfect shield (Powershield), Shield, Out of shield
  (https://www.ssbwiki.com/Perfect_shield).
- Melee Library: "Crouch to Make Powershielding Easier" (card description only);
  "Powershielding" (Kadano, Ask Anyone Frame Things thread, page 17) and "Heart Shield
  (Powershield Storing)" (Schmooblidon) could not be fetched.
- `[decomp]`: state names from this repository.
