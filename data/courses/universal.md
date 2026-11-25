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
| `universal-di` | Directional Influence (DI) | Change your launch angle with the control stick | - | - | drill format: `data/drills/universal-di.json` |
| `universal-sdi` | Smash DI (SDI) | Move out of a multi-hit attack during hitlag | - | - | drill format: `data/drills/universal-sdi.json` |
| `universal-asdi` | Automatic SDI (ASDI) | Shift your position at the end of hitlag | - | - | drill format: `data/drills/universal-asdi.json` |
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
| `universal-crouch-cancel` | Crouch cancel | Crouch through weak hits and punish; know where it stops | [crouch cancel](../techniques/crouch-cancel.md) | - | drill format: `data/drills/universal-crouch-cancel.json` (2026-11-25) |
| `universal-asdi` | ASDI down | Hold the C-stick down through weak hits, land and punish; know where it stops | [ASDI](../techniques/asdi.md) | - | the Fundamentals drill, `data/drills/universal-asdi.json`, listed here too |
| `universal-di` | Survival and combo DI | DI kill moves to live and starters to escape | [DI](../techniques/di.md) | - | the Fundamentals drill, `data/drills/universal-di.json`, listed here too (survival DI only) |
| `universal-sdi` | SDI multi-hits | SDI out of multi-hit moves | [SDI](../techniques/sdi.md) | legacy SDI Training | drill format: `data/drills/universal-sdi.json` |
| `universal-wall-tech` | Wall and ledge tech | Tech the stage while recovering | [wall tech](../techniques/wall-tech.md), [Amsah tech](../techniques/amsah-tech.md) | legacy Ledgetech, Amsah Tech | planned |
| `universal-recovery` | Recover | Sweetspot and mix the recovery against coverage | [recovery](../techniques/recovery.md), [ledge options](../techniques/ledge-options.md) | `sweetspot` | planned |
| `universal-grab-mash` | Mash out of grabs | Break grabs as early as the rules allow | [grab and throw](../techniques/grab-and-throw.md) | legacy Grab Mash Out | planned |

## Neutral

Neutral drills are character-specific (ranges and options differ too much to share). The
shared part is the CPU behaviour library the engine provides: approach, whiff, shield,
crouch, jump in, with a reaction delay.
