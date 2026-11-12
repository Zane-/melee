---
schema: melee-technique/v1
id: wall-tech
name: Wall tech
aliases: [walltech, ledge tech, edge tech, stage tech, ceiling tech, wall tech jump, tech the stage spike]
category: recovery
difficulty: 4
related: [teching, sdi, asdi, wall-jump, recovery, edgeguarding, meteor-cancel, di]
characters: all
summary: Teching against a wall or ceiling while in hitstun absorbs the launch and gives brief intangibility; near the ledge, combining a tech input before the hit with SDI toward the stage survives hits that would otherwise kill.
---

# Wall tech

## What it is

A [tech](teching.md) performed against a wall (`PassiveWall`) or ceiling (`PassiveCeil`)
instead of the floor. The character must be in hitstun and tumbling when they touch the
surface; drifting into a wall after hitstun does not allow it. A successful wall tech removes
the character's momentum, gives a few frames of intangibility, and can be turned into a jump
by holding up (`PassiveWallJump`). Without the tech the character bounces off the surface
(a "stage spike" when it sends them down and away) [wiki:Tech].

A **ledge tech** is a wall tech done at the stage's edge: the character is hit while on or
next to the ledge, moves into the stage's side with [SDI](sdi.md) or [ASDI](asdi.md), and
techs there instead of flying off [lib:A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling].

## Inputs

Reliable ledge-tech method from Doraki's guide
[lib:A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling]:

1. Press L or R (digital) **before** the hit connects. A press during hitlag generally
   fails (see the tech rules in [teching](teching.md)).
2. During hitlag, smash the control stick toward the wall (SDI). When the SDI moves the
   character into the wall, the tech triggers at that moment, provided the L/R press was
   within the tech window (the guide suggests the SDI about 15-20 frames after the press at
   most; the window is 20 frames).
3. Hold the C-stick toward the wall as well for ASDI in case the SDI was missed.
4. For a wall tech jump, hold up on the control stick (or jump) during the first frames of
   the tech.

At mid percent, ASDI toward the stage alone can be enough to touch the wall; at higher
percent SDI is needed because the launch is too fast. More damage also means more hitlag,
which uses up more of the 20-frame window if the press came early
[lib:A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling].

When a tech happens during hitlag via SDI, the character resumes moving only when hitlag
ends and still has the tech's intangibility then
[lib:A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling].

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Tech window / lockout | 20 frames / 40 frames, same rules as ground techs | [wiki:Tech] |
| SDI into walls and ceilings | allowed, and a tech can come out during hitlag | [wiki:Tech] |
| ASDI into a wall, ceiling or floor on the first frame after hitlag | allowed, even if the launch points away | [wiki:Tech] |
| Same-frame press | L/R on the frame of contact still techs | [wiki:Tech] |
| Wall tech total animation | 31 frames (Ice Climbers 25, Donkey Kong 30) | [web:smashboards.com] |
| Wall tech interruptible (IASA) | frame 6 | [web:smashboards.com] |
| Wall tech intangibility | frames 1-14 (Ganondorf 1-19, cut to 14 if he acts or wall-tech-jumps) | [web:smashboards.com] |
| Wall tech jump | hold an upward direction on frames 1-4; the jump starts on frame 6; 40-frame animation interruptible from frame 1 | [web:smashboards.com] |
| Ceiling tech total | 26 frames (Donkey Kong, Jigglypuff, Kirby 25) | [web:smashboards.com] |
| Ceiling tech intangibility | 1-18 Bowser; 1-17 Dr. Mario, Mr. Game & Watch, Ice Climbers, Jigglypuff, Kirby, Luigi, Mario, Mewtwo, Ness, Sheik; 1-15 Donkey Kong; 1-14 Falco, Fox, Yoshi; 1-13 Link, Marth, Pichu, Pikachu, Roy, Young Link; 1-12 Samus; 1-11 Captain Falcon, Ganondorf; none for Peach and Zelda | [web:smashboards.com] |
| Missed wall/ceiling bounce | intangible frames 1-15 | [web:smashboards.com] |
| Speed lost when bouncing without a tech | 20% of total speed | [wiki:Knockback] |
| SDI / ASDI distance | 6 / 3 units | [wiki:Smash_directional_influence] |

"Random Wall Tech Assist" (Schmooblidon) in the Library describes ECB distortion on hit that
sometimes makes wall techs happen without SDI; not readable here.

## Why it matters

- **Surviving edgeguards:** a character hanging on or returning to the ledge who is hit by
  a strong move (classic: [Marth](../characters/marth.md) fsmash or dtilt,
  [Fox](../characters/fox.md) shine, [Falco](../characters/falco.md) dair,
  [Sheik](../characters/sheik.md) fair) can tech the stage and stay alive at any percent,
  because the tech cancels all knockback.
- **Stage spikes:** when hit into the stage's side or underside, teching prevents the
  downward bounce. A wall tech jump regains height immediately.
- **Punishing the edgeguarder:** the tech is actionable from frame 6 with intangibility to
  frame 14, enough for some characters to counterattack (e.g. Fox/Falco shine).
- Walls under the ledge differ by stage (Yoshi's Story and Fountain of Dreams vertical
  sides; Battlefield's lip; Final Destination's slanted underside), which changes how much
  SDI is needed.

## Common errors

- Pressing L/R on reaction during hitlag: fails. In game: the character bounces off the
  wall or flies away.
- Pressing far too early (more than 20 frames before contact) or pressing twice (lockout).
- SDI in the wrong direction, or holding the stick (ASDI only) when a smash input was
  needed.
- Being in tech lockout from an earlier air dodge or L-cancel press.
- Teching but then doing nothing and being hit after the intangibility ends, or wall
  jumping away from the stage.
- Up B input immediately after the tech into the edgeguarder's next hit.

## How to detect it in a training mode

- Success: victim enters `PassiveWall` (or `PassiveCeil`, or `PassiveWallJump` for the jump
  variant) [decomp]. Failure: `FlyReflectWall` / `FlyReflectCeil` (bounce) or the victim
  leaves without touching the wall.
- Feedback values: frames between the L/R press and wall contact; whether the press was
  before hitlag, on the last hitlag frame, or inside hitlag; SDI displacement toward the
  wall during hitlag; C-stick direction on the last hitlag frame.
- Outcome: survived and returned to ledge/stage within N frames.

## Drill seeds

### Ledge tech a telegraphed hit

- **id:** `wall-tech-ledge-vs-marth`
- **Goal:** Tech the stage when hit at the ledge.
- **Player:** any; most practised with [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md)
- **CPU:** [Marth](../characters/marth.md) (fsmash, dtilt), [Fox](../characters/fox.md) (shine, bair), [Sheik](../characters/sheik.md) (fair, ftilt)
- **Setup:** Player recovering to the ledge with up B (or hanging after intangibility ends); CPU at the edge.
- **CPU behaviour:** Hits the player as they reach the ledge, with a short random delay.
- **Success:** `PassiveWall` or `PassiveWallJump`, then the player returns to the ledge or stage.
- **Fail:** Bounce or KO; report press timing and SDI.
- **Variations:** Percent 50-150 (more hitlag and speed); stages; the hitbox freeze-repeat style of 20XX (the Library's "20XX Hitbox Freeze Repeater" video describes practising ledge techs this way).
- **Data needed:** CPU move damage (hitlag), stage wall geometry, tech rules.

### Stage spike tech

- **id:** `wall-tech-stage-spike`
- **Goal:** Tech when hit into the underside or side of the stage.
- **Player:** any
- **CPU:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Captain Falcon](../characters/captain-falcon.md), [Jigglypuff](../characters/jigglypuff.md)
- **Setup:** Player offstage below the ledge close to the wall; CPU drops down.
- **CPU behaviour:** Bair or similar toward the stage.
- **Success:** Wall tech (optionally wall tech jump) and recovery.
- **Fail:** Bounce and KO.
- **Variations:** With/without double jump afterwards.
- **Data needed:** As above.

### Tech then punish

- **id:** `wall-tech-counterattack`
- **Goal:** Use the frame 6 interrupt to hit the edgeguarder.
- **Player:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Sheik](../characters/sheik.md)
- **CPU:** [Marth](../characters/marth.md)
- **Setup:** As the first drill.
- **CPU behaviour:** Fsmash at the ledge, then lag.
- **Success:** Wall tech, then the player's attack hits the CPU within its lag.
- **Fail:** No tech or no hit.
- **Variations:** CPU uses a faster move (dtilt) with less lag.
- **Data needed:** Wall tech frames above, CPU lag.

## Sources

- SSBWiki: Tech (wall, ceiling, Melee rules), Knockback, Smash directional influence
  (https://www.ssbwiki.com/Tech).
- Melee Library: "A Guide to DI, Smash DI, C-stick DI, Teching, and Crouch Cancelling"
  (Doraki, Wayback Machine copy). Titles only: "Wall Tech Tutorial" (SSBM Tutorials), "How
  To Ledge Tech and What To Do Afterwards" (Remix), "Random Wall Tech Assist"
  (Schmooblidon), "20XX Hitbox Freeze Repeater Instructional Video" (Achilles), "Spot Dodge
  After DSDI Tech" (Sycorax).
- Magus420's techs data (Smashboards, Wayback Machine copy), tagged `[web:smashboards.com]`.
- `[decomp]`: state names from this repository.
