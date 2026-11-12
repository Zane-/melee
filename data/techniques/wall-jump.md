---
schema: melee-technique/v1
id: wall-jump
name: Wall jump
aliases: [walljump, wall kick, Doraki wall jump, reverse wall jump, scar jump, wall tech jump]
category: recovery
difficulty: 3
related: [wall-tech, recovery, ledge-options, edgeguarding]
characters: [falco, captain-falcon, samus, sheik, pichu, young-link, mario, fox]
summary: Eight characters can kick off a wall by flicking the stick away from it while moving into it, gaining height without using their double jump; any character can jump out of a wall tech.
---

# Wall jump

## What it is

A jump off a vertical wall. In Melee only some characters have a natural wall jump: Falco,
Captain Falcon, Samus, Sheik, Pichu, Young Link, Mario and Fox [wiki:Wall_jump]. It does not
consume the double jump and can be repeated. Separately, **every** character can jump out of
a [wall tech](wall-tech.md) ("wall tech jump"), because the game uses the same action for
both.

## Inputs

1. Be airborne and move horizontally into a wall so the character is touching it.
2. Smash the control stick away from the wall shortly after contact.

The character kicks off, facing away from the wall, with a fixed upward and outward
velocity.

Mechanics as written in this repository's decompiled wall jump routine
(`src/melee/ft/ftwalljump.c`) [decomp]:

- The character must have the wall-jump ability flag (`can_walljump`).
- The character must be hugging a wall on its left or right (collision flags), and its
  horizontal speed relative to the wall must exceed a per-character minimum approach speed
  (`wall_jump_min_approach_speed`). That starts an input timer.
- While the timer is below a global limit, a stick X value beyond a threshold in the
  direction away from the wall, reached quickly (the stick must not have lingered in the
  tilt zone), triggers the jump.
- The jump is the `PassiveWallJump` action state, the same state used for a wall tech jump.
- The game counts wall jumps used in the current airtime (`x1969_walljumpUsed`) and passes
  the count to the jump routine. Successive wall jumps giving less height is commonly
  reported [unverified]; the factor is in data files, not read here.

The numeric values of the timer limit, the stick threshold and the tilt-time limit live in
the common fighter data file and were not extracted: Unknown.

## Frame data and formulas

Wall jump height (units) [wiki:Wall_jump]:

| Character | Height |
|-|-|
| Falco | 36.33 |
| Captain Falcon | 35.42 |
| Samus | 32.364 |
| Sheik | 31.28 |
| Pichu | 29.44 |
| Young Link | 29.44 |
| Mario | 26.7 |
| Fox | 22.05 |

Other facts:

| Fact | Value | Source |
|-|-|-|
| Wall tech jump (all characters) | input an upward direction on frames 1-4 of the wall tech; the jump comes out on frame 6 | [web:smashboards.com] |
| Wall tech jump animation | 40 frames total, interruptible from frame 1 | [web:smashboards.com] |
| Ledge "Doraki" wall jump | from the ledge on Final Destination, Fox, Mario, Young Link and Pichu can drop and wall jump immediately off the stage side without using the double jump | [wiki:Edge_getup] |
| Stages with usable walls | stage geometry: Yoshi's Story and Fountain of Dreams have vertical sides, Battlefield has an angled lip under the ledge, Final Destination a long angled underside, Pokemon Stadium and Dream Land shorter sides | [unverified] general knowledge |

## Why it matters

- **Recovery:** extra height when recovering low along a wall, saving the double jump or
  up B ([Captain Falcon](../characters/captain-falcon.md), [Sheik](../characters/sheik.md),
  [Samus](../characters/samus.md), [Falco](../characters/falco.md)/[Fox](../characters/fox.md)).
- **Edgeguarding:** drop from the ledge, wall jump, and hit with an aerial while keeping the
  double jump (e.g. Captain Falcon wall jump knee, Falco wall jump dair; general knowledge).
- **Wall tech jump:** after teching a stage spike, jumping out gains height immediately.
- The Library lists "Reverse Walljumping" (Vesne), "Doraki Instant Walljump Tutorial" and
  "How to Scar Jump" as the advanced variants; none were readable here.

## Common errors

- Stick flicked before touching the wall, or too slowly (tilt, not smash): no jump, the
  character slides down.
- Not actually moving into the wall (speed below the minimum approach speed).
- Using it with a character that has no wall jump.
- Wall jumping away from the stage and being unable to return.
- After a wall tech: holding up too late (after frame 4) and getting the plain wall tech.

## How to detect it in a training mode

- Success: the fighter enters `PassiveWallJump` [decomp]. To separate a natural wall jump
  from a wall tech jump, check whether the previous state was `PassiveWall` (tech) or a
  normal airborne state.
- Input feedback: frames between first wall contact (wall-hug collision flag) and the
  stick crossing the away threshold.
- Count of wall jumps in one airtime is available on the fighter.

## Drill seeds

### Wall jump recovery

- **id:** `wall-jump-recovery-height`
- **Goal:** Use a wall jump to recover without the double jump.
- **Player:** [Captain Falcon](../characters/captain-falcon.md), [Sheik](../characters/sheik.md), [Falco](../characters/falco.md), [Fox](../characters/fox.md), [Samus](../characters/samus.md), [Mario](../characters/mario.md), [Young Link](../characters/young-link.md), [Pichu](../characters/pichu.md)
- **CPU:** none
- **Setup:** Player placed offstage below the ledge next to the stage wall on Yoshi's Story, double jump removed.
- **CPU behaviour:** None.
- **Success:** Player reaches the ledge or stage.
- **Fail:** KO.
- **Variations:** Other stages; with an edgeguarding CPU; chained wall jumps.
- **Data needed:** Wall jump height, up B height, stage wall geometry.

### Ledge drop wall jump aerial

- **id:** `wall-jump-ledge-edgeguard`
- **Goal:** From the ledge, drop, wall jump and hit a recovering opponent, keeping the double jump.
- **Player:** [Captain Falcon](../characters/captain-falcon.md), [Falco](../characters/falco.md), [Sheik](../characters/sheik.md)
- **CPU:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Marth](../characters/marth.md)
- **Setup:** Player on the ledge; CPU recovering from below.
- **CPU behaviour:** Up B toward the ledge.
- **Success:** Aerial hits; player returns to the stage with the double jump or up B.
- **Fail:** Miss or SD.
- **Variations:** Stage.
- **Data needed:** Aerial startup, CPU recovery path.

## Sources

- SSBWiki: Wall jump (Melee table), Edge getup (https://www.ssbwiki.com/Wall_jump).
- This repository: `src/melee/ft/ftwalljump.c` (decompiled wall jump routine), tagged
  `[decomp]`. It gives the logic and names, not the tuning constants.
- Magus420's techs data (Smashboards, Wayback Machine copy), tagged `[web:smashboards.com]`.
- Melee Library cards on wall jump variants: titles only.
