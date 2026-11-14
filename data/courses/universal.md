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

## Tech

| id | Drill | Goal | Knowledge | TM-CE event that covers part of it | Status |
|-|-|-|-|-|-|
| `universal-short-hop` | Short hop | Short hop every time; press length shown | [short hop](../techniques/short-hop.md) | - | implemented: `drills/tech_short_hop.inc.h`; simulator and Dolphin specs pass (2026-11-12). Press length shown in the verdict |
| `universal-l-cancel` | L-cancel | L-cancel whiffed, hit and shielded aerials | [L-cancel](../techniques/l-cancel.md) | `lcancel` | implemented: `drills/tech_movement.inc.h`; simulator and Dolphin specs pass (2026-11-12). Demonstrations succeed for every character but Mr. Game & Watch's three aerials that cannot be L-cancelled (simulator and native, 2026-11-13) |
| `universal-shffl` | SHFFL | All four components with per-component feedback | [SHFFL](../techniques/shffl.md), [fast fall](../techniques/fast-fall.md) | `lcancel` | implemented: `drills/tech_movement.inc.h`; simulator and Dolphin specs pass (2026-11-12). Demonstrations succeed for every character but Mr. Game & Watch's three aerials that cannot be L-cancelled (simulator and native, 2026-11-13) |
| `universal-wavedash` | Wavedash | Air dodge on the first airborne frame at a chosen angle | [wavedash](../techniques/wavedash.md), [waveland](../techniques/waveland.md) | `wavedash` | implemented: `drills/tech_wavedash.inc.h`; simulator and Dolphin specs pass (2026-11-12). Chosen length / angle not built |
| `universal-dash-dance` | Dash dance and pivot | Controlled dash lengths and turnarounds | [dash dance](../techniques/dash-dance.md), [pivot](../techniques/pivot.md) | - | implemented: `drills/tech_movement.inc.h`; simulator and Dolphin specs pass (2026-11-12); demonstration passes for all 26 characters |
| `universal-jc-grab` | Jump-cancel grab and up smash | Standing grab and up smash out of a run | [jump cancel](../techniques/jump-cancel.md) | - | implemented: `drills/tech_movement.inc.h`; simulator and Dolphin specs pass (2026-11-12); demonstration passes for all 26 characters |
| `universal-ledgedash` | Ledgedash | Onto the stage with intangibility left | [ledgedash](../techniques/ledgedash.md) | `ledgedash` | implemented on Final Destination's left ledge: `drills/tech_ledge.inc.h`; simulator and Dolphin specs pass (2026-11-12). Fox only checked |
| `universal-shield-drop` | Shield drop (Axe method) | Hold the stick fully left or right in shield, roll down to the diagonal notch, drop into an aerial | [shield drop](../techniques/shield-drop.md) | legacy Shield Drop | implemented on Battlefield's left platform: `drills/tech_ledge.inc.h`; simulator and Dolphin specs pass (2026-11-12) |
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
| `universal-tech` | Tech the ground | Tech in place, in and away; lockout shown | [teching](../techniques/teching.md) | - | planned |
| `universal-asdi-down` | ASDI down and crouch cancel | Hold the ground and punish; know where it stops | [ASDI](../techniques/asdi.md), [crouch cancel](../techniques/crouch-cancel.md) | - | planned |
| `universal-di-survival` | Survival and combo DI | DI kill moves to live and starters to escape | [DI](../techniques/di.md) | - | planned |
| `universal-sdi` | SDI multi-hits | SDI out of multi-hit moves | [SDI](../techniques/sdi.md) | legacy SDI Training | planned |
| `universal-wall-tech` | Wall and ledge tech | Tech the stage while recovering | [wall tech](../techniques/wall-tech.md), [Amsah tech](../techniques/amsah-tech.md) | legacy Ledgetech, Amsah Tech | planned |
| `universal-recovery` | Recover | Sweetspot and mix the recovery against coverage | [recovery](../techniques/recovery.md), [ledge options](../techniques/ledge-options.md) | `sweetspot` | planned |
| `universal-grab-mash` | Mash out of grabs | Break grabs as early as the rules allow | [grab and throw](../techniques/grab-and-throw.md) | legacy Grab Mash Out | planned |

## Neutral

Neutral drills are character-specific (ranges and options differ too much to share). The
shared part is the CPU behaviour library the engine provides: approach, whiff, shield,
crouch, jump in, with a reaction delay.
