---
schema: melee-course/v1
id: universal
character: all
status: draft
summary: Drills that are the same for every character; character courses place them in their own order.
includes: []
---

# Universal drills

On the native build every drill of this file that is implemented is also ported
(`tools/melee_course/drills/`) and passes the same specs (2026-11-13): "The courses on the
native build" in `docs/ai/native-ai.md`.

Draft (2026-11-12). Every drill is `planned`. A character course lists these ids as rows of
its plan tables; per-character numbers (jump squat, landing lag, traction, tech lengths) come
from the generated frame data tables for the picked character, not from this file. Seeds for
each are in the technique file's `Drill seeds` section.

A character course replaces a universal drill with its own when the technique differs
materially (Peach's float cancel, Yoshi's parry, Mr. Game & Watch's aerials that cannot be
L-cancelled, Ice Climbers' desynced wavedash).

## Tech skill

Movement and Fundamentals: the Tech skill subcourses every character shares (owner,
2026-11-14); a character's own techniques are its course's Character subcourse. Written in
the drill format (`docs/ai/drill-format.md`).

### Movement

| id | Drill | Goal | Knowledge | TM-CE event that covers part of it | Status |
|-|-|-|-|-|-|
| `universal-short-hop` | Short hop | Short hop ten times in a row | [short hop](../techniques/short-hop.md) | - | drill format: `data/drills/universal-short-hop.json` |
| `universal-fast-fall` | Fast fall | Fast fall at the top of a jump | - | - | drill format: `data/drills/universal-fast-fall.json` |
| `universal-dash-dance` | Dash dance | Dash back and forth without breaking into a run | [dash dance](../techniques/dash-dance.md), [pivot](../techniques/pivot.md) | - | drill format: `data/drills/universal-dash-dance.json` |
| `universal-wavedash` | Wavedash | Air dodge into the ground on the first frame in the air | [wavedash](../techniques/wavedash.md), [waveland](../techniques/waveland.md) | `wavedash` | drill format: `data/drills/universal-wavedash.json` |
| `universal-waveland` | Waveland | Air dodge into the stage or a platform as you land | - | - | drill format: `data/drills/universal-waveland.json` |
| `universal-pivot` | Pivot | Turn around out of a dash and stand still | - | - | drill format: `data/drills/universal-pivot.json` |
| `universal-ledgedash` | Ledgedash | Land on the stage from the ledge with invincibility left | [ledgedash](../techniques/ledgedash.md) | `ledgedash` | drill format: `data/drills/universal-ledgedash.json` |

### Fundamentals

| id | Drill | Goal | Knowledge | TM-CE event that covers part of it | Status |
|-|-|-|-|-|-|
| `universal-l-cancel` | L-cancel | Halve an aerial's landing lag | [L-cancel](../techniques/l-cancel.md) | `lcancel` | drill format: `data/drills/universal-l-cancel.json` |
| `universal-shffl` | SHFFL | Short hop, aerial, fast fall and L-cancel in one motion | [SHFFL](../techniques/shffl.md), [fast fall](../techniques/fast-fall.md) | `lcancel` | drill format: `data/drills/universal-shffl.json` |
| `universal-jc-grab` | Jump-cancel grab | A standing grab out of a dash | [jump cancel](../techniques/jump-cancel.md) | - | drill format: `data/drills/universal-jc-grab.json` |
| `universal-jc-upsmash` | Jump-cancel up smash | An up smash out of a dash | [jump cancel](../techniques/jump-cancel.md) | - | drill format: `data/drills/universal-jc-upsmash.json` |
| `universal-di` | Directional Influence (DI) | Change your launch angle with the control stick | - | - | drill format: `data/drills/universal-di.json`; rebuilt from play (2026-11-25; the owner: "Every drill is supposed to feel realistic, not just robotic spawn and do something"): the attacker begins 55 units away, plays footsies for 40, 80 or 120 frames, walks up to the distance its hit was measured from, stands for 14 frames and plays the inputs it was measured with (the new `press` step), then plays footsies again; a try begins when the hit lands. The walk's stop is calibrated for each attacker, the examples are as they were measured (the hit's frame in a demonstration is each scenario's `HIT`). `check.py` 2652 of 2652, all 26 characters (two attackers stand a little longer before they walk, where one character's idle sway changed which part of the smash hit: Fox's down smash on Falco, Sheik's up smash on Kirby); `tests/client/drill_smoke.py universal-di --tries 2 --paced` |
| `universal-sdi` | Smash DI (SDI) | Move out of a multi-hit attack during hitlag | - | - | drill format: `data/drills/universal-sdi.json`; rebuilt from play (2026-11-25; the owner: "Every drill is supposed to feel realistic, not just robotic spawn and do something"): the attacker begins 55 units away, plays footsies for 40, 80 or 120 frames, walks up and attacks with the inputs it was measured with (the `press` step), then plays footsies again; a try begins when its first hit lands. Pikachu walks up to the 10 units its down smash was measured from. The three down airs were measured with the attacker placed on top of the player and pushed apart by the game before it jumped, to a distance that is another for every character (against Fox 7.4, 7.0 and 6.8 units, against Bowser 11.0, 10.0 and 7.1): so each walks into the player (16 frames on from 12 units), stands 16 frames while the game pushes them apart the same way, and jumps. `check.py` 598 of 598, all 26 characters (walking in 18 frames instead of 16 left Kirby 0.1 units nearer Jigglypuff, and her down air hit him a third time); `tests/client/drill_smoke.py universal-sdi --tries 2 --paced` |
| `universal-asdi` | Automatic SDI (ASDI) | Shift your position at the end of hitlag | - | - | drill format: `data/drills/universal-asdi.json`; rebuilt from play (2026-11-25; the owner: "Every drill is supposed to feel realistic, not just robotic spawn and do something"): the attacker begins 55 units away, plays footsies for 40, 80 or 120 frames, walks up to the distance its hit was measured from, stands for 14 frames and plays the inputs it was measured with (the new `press` step), then plays footsies again; a try begins when the hit lands. The walk's stop is calibrated for each attacker, the examples are as they were measured (the hit's frame in a demonstration is each scenario's `HIT`). `check.py` 2184 of 2184, all 26 characters (measured while converting: Captain Falcon's idle sway puts Fox's jab a frame later on him when it comes 77 or 78 frames into a demonstration; the attacker stands 22 frames first there); `tests/client/drill_smoke.py universal-asdi --tries 2 --paced` |
| `universal-shield-drop` | Shield drop | Drop through a platform out of shield | [shield drop](../techniques/shield-drop.md) | legacy Shield Drop | drill format: `data/drills/universal-shield-drop.json` |
| `universal-edge-cancel` | Edge cancel | Slide off a platform during an aerial's landing lag | - | - | drill format: `data/drills/universal-edge-cancel.json` |
| `universal-slide-off` | Slide off | Slide off a platform during landing lag | - | - | drill format: `data/drills/universal-slide-off.json` |

Not in a subcourse yet (it was planned before the owner's list of 2026-11-14):

| id | Drill | Goal | Knowledge | TM-CE event that covers part of it | Status |
|-|-|-|-|-|-|
| `universal-powershield` | Powershield | Reflect projectiles, powershield physical hits | [powershield](../techniques/powershield.md) | `powershield` | planned |

## Punish

| id | Drill | Goal | Knowledge | TM-CE event that covers part of it | Status |
|-|-|-|-|-|-|
| `universal-tech-chase` | Tech chase | React to tech in place, in, away and no tech | [tech chase](../techniques/tech-chase.md), [jab reset](../techniques/jab-reset.md) | `techchase` | planned |
| `universal-oos-punish` | Out-of-shield punish | Use the character's fastest option that fits the window | [out of shield](../techniques/out-of-shield.md) | legacy Attack on Shield | planned |
| `universal-edgeguard` | Edgeguard | Cover a recovering CPU's options | [edgeguarding](../techniques/edgeguarding.md) | `edgeguard` | planned |

## Defense

| id | Drill | Goal | Knowledge | TM-CE event that covers part of it | Status |
|-|-|-|-|-|-|
| `universal-tech` | Tech the ground | Tech in place, in and away; lockout shown | [teching](../techniques/teching.md) | - | drill format: `data/drills/universal-tech.json` (2026-11-25; not the Ice Climbers) |
| `universal-crouch-cancel` | Crouch cancel | Crouch through an attack as you come in and punish it; know where it stops | [crouch cancel](../techniques/crouch-cancel.md) | - | drill format, from play: `data/drills/universal-crouch-cancel.json` (2026-11-25; 25 attacks of nine opponents, the damage drawn up to each attack's measured limit for the character played, `data/actor/crouch_cancel.json`; details in the Defense 2 row of `fox.md`) |
| `universal-asdi` | ASDI down | Hold the C-stick down through weak hits, land and punish; know where it stops | [ASDI](../techniques/asdi.md) | - | the Fundamentals drill, `data/drills/universal-asdi.json`, listed here too; from play (2026-11-25), as its Fundamentals row says |
| `universal-di` | Survival and combo DI | DI kill moves to live and starters to escape | [DI](../techniques/di.md) | - | the Fundamentals drill, `data/drills/universal-di.json`, listed here too (survival DI only); from play (2026-11-25), as its Fundamentals row says |
| `universal-sdi` | SDI multi-hits | SDI out of multi-hit moves | [SDI](../techniques/sdi.md) | legacy SDI Training | drill format: `data/drills/universal-sdi.json`; from play (2026-11-25), as its Fundamentals row says |
| `universal-wall-tech` | Wall and ledge tech | Tech the stage while recovering | [wall tech](../techniques/wall-tech.md), [Amsah tech](../techniques/amsah-tech.md) | legacy Ledgetech, Amsah Tech | planned |
| `universal-recovery` | Recover | Sweetspot and mix the recovery against coverage | [recovery](../techniques/recovery.md), [ledge options](../techniques/ledge-options.md) | `sweetspot` | planned |
| `universal-grab-mash` | Mash out of grabs | Break grabs as early as the rules allow | [grab and throw](../techniques/grab-and-throw.md) | legacy Grab Mash Out | planned |

## Neutral

Neutral drills are character-specific (ranges and options differ too much to share). The
shared part is the CPU behaviour library the engine provides: approach, whiff, shield,
crouch, jump in, with a reaction delay.
