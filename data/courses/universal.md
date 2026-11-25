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
| `universal-di` | Directional Influence (DI) | Change your launch angle with the control stick | - | - | drill format: `data/drills/universal-di.json`; to crouch cancel's standard (2026-11-25; the owner: "bring the walk up drills to the crouch cancel's standard"): the attacker begins 55 units away, plays footsies past its distance for 30 to 150 frames, lets what it was doing end, steps back if it is too near, turns to face the player, walks up (the last 8 units slowly), stops for 6 frames and attacks with the inputs it was measured with, then plays footsies again; another scenario every try; a try begins when the hit lands. The damage is drawn for each try 20% either side of the damage each attack was built at (Fox's forward smash 90 to 130%), proved at both ends. Jigglypuff's back air is a back air again: since she walks in facing the player it had been a forward air; she turns before she jumps. Counted from the hit now: the examples, their captions and the lessons were keyed by the old demonstration's frames, so the captions never showed and the lessons pressed long before the hit; and a lesson is recorded against its own scenario's opponent (it was whichever the deck drew), its example proved by `check.py` (`"checks"`). `check.py` 2704 of 2704, all 26 characters (and as many with every damage at its low end); `check_play.py`, every character, 3 seeded runs a scenario: 1092 of 1092 in each judged part; `tests/client/drill_smoke.py universal-di --tries 2 --paced` |
| `universal-sdi` | Smash DI (SDI) | Move out of a multi-hit attack during hitlag | - | - | drill format: `data/drills/universal-sdi.json`; to crouch cancel's standard (2026-11-25; the owner: "bring the walk up drills to the crouch cancel's standard"): the attacker begins 55 units away, plays footsies past its distance for 30 to 150 frames, lets what it was doing end, steps back if it is too near, turns to face the player, walks up (the last 8 units slowly), stops for 6 frames and attacks with the inputs it was measured with, then plays footsies again; another scenario every try; a try begins when the hit lands (the three down airs: it walks into the player, 16 frames on from 12 units, and stands 16 frames while the game pushes the two apart as it did when they were measured, then jumps). The damage is drawn for each try from 0 as far as the example holds at every percent on the way (`percent_range.py --step 1`: against a multi-hit attack the outcome does not grow evenly with the damage): Pikachu's down smash to 21% for Fox, 35% for Pichu, 52% for Bowser; Jigglypuff's down air to 39% for Falco, 60% for most; Fox's and Peach's down air to 60%. Counted from the hit now: the examples, their captions and the lessons were keyed by the old demonstration's frames, so the captions never showed and the lessons pressed long before the hit; and a lesson is recorded against its own scenario's opponent (it was whichever the deck drew), its example proved by `check.py` (`"checks"`). `check.py` 650 of 650, all 26 characters; `check_play.py`, every character, 3 seeded runs a scenario: 312 of 312 in each part; `tests/client/drill_smoke.py universal-sdi --tries 2 --paced`. Still four attacks |
| `universal-asdi` | Automatic SDI (ASDI) | Shift your position at the end of hitlag | - | - | drill format: `data/drills/universal-asdi.json`; to crouch cancel's standard (2026-11-25; the owner: "bring the walk up drills to the crouch cancel's standard"): the attacker begins 55 units away, plays footsies past its distance for 30 to 150 frames, lets what it was doing end, steps back if it is too near, turns to face the player, walks up (the last 8 units slowly), stops for 6 frames and attacks with the inputs it was measured with, then plays footsies again; another scenario every try; a try begins when the hit lands. The damage is drawn for each try from 0 to 3% under the most at which the example still lands at once, measured per attack and character (`python tools/melee_drills/percent_range.py universal-asdi`; Sheik's down tilt to 36% for Fox, 31% for Pichu, 48% for Bowser; Marth's down tilt 81, 70, 100; Pikachu's 59, 51, 76; Fox's down tilt 14, 10, 20; Yoshi's forward tilt 13, 10, 20; Samus's dash attack 15, 11, 22; Falco's down tilt 5, 3, 10; the three jabs to 100%). Counted from the hit now: the examples, their captions and the lessons were keyed by the old demonstration's frames, so the captions never showed and the lessons pressed long before the hit; and a lesson is recorded against its own scenario's opponent (it was whichever the deck drew), its example proved by `check.py` (`"checks"`). `check.py` 5148 of 5148, all 26 characters; `check_play.py`, every character, 3 seeded runs a scenario: 1872 of 1872 and 1872 of 1872 in the two judged parts; `tests/client/drill_smoke.py universal-asdi --tries 2 --paced`. 24 attacks of ten opponents, all of the top 11 but the Ice Climbers (their partner hits after the first): 14 were added from `data/actor/asdi_down.json` (`cc_limits.py --asdi`: Captain Falcon's down tilt, forward tilt and dash attack; Jigglypuff's forward tilt and dash attack; Fox's, Falco's, Sheik's, Pikachu's and Yoshi's dash attack; Marth's, Sheik's, Pikachu's and Samus's forward tilt), each one that lifts every character at 0% when nothing is held and freezes every character as long (Fox's and Falco's forward tilts leave a standing character on the floor: nothing to ASDI down; Peach's forward tilt freezes 6 or 7 frames by where it hits) |
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
