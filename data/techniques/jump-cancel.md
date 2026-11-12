---
schema: melee-technique/v1
id: jump-cancel
name: Jump cancel
aliases: [JC, jump-cancelling, JC grab, jump-cancelled grab, JC up smash, JC shine, multishine, pseudo jump cancel]
category: movement
difficulty: 2
related: [out-of-shield, grab-and-throw, short-hop, wavedash, dash-dance, shield-pressure]
characters: all
summary: Interrupting jump squat with a grab, up smash or up B so the move comes out from the ground without jumping; also, cancelling shield, shine or a run turnaround by jumping.
---

# Jump cancel

## What it is

The term covers two related things [wiki:Jump-canceling]:

1. **Cancelling the jump with a move.** During jump squat the character is still grounded,
   and three kinds of action can interrupt it: up smash, up B, and (in Melee only) grab,
   plus item throws. The jump never happens. This allows a standing grab or up smash
   directly out of a dash or run, and up B / up smash [out of shield](out-of-shield.md).
2. **Cancelling something with a jump.** Shield, Fox's and Falco's down B (shine) and the
   run turnaround can be ended by jumping. Combined with (1) this gives "shield -> jump ->
   up smash" and "shine -> jump -> grab/usmash/wavedash".

A **pseudo jump cancel** is a move that halts vertical momentum, used on the first airborne
frame so the character falls straight back to the ground, for example shine out of shield
and multishine [wiki:Jump-canceling].

## Inputs

- **JC grab:** while dashing or running, press jump then Z (or L/R + A) before jump squat
  ends. In practice the two presses are almost simultaneous, jump first.
- **JC up smash:** dash/run, jump, then up + A or C-stick up during jump squat. With tap
  jump, a hard up on the stick plus A does both.
- **Up B out of shield / shine:** jump, then up + B during jump squat.
- **Multishine (Fox/Falco):** down B, jump, down B on the first airborne frame, repeat.

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Window | the jump squat: 3 frames (Fox, Ice Climbers, Kirby, Pichu, Pikachu, Samus, Sheik), 4 (Captain Falcon, Dr. Mario, Luigi, Mario, Marth, Mr. Game & Watch, Ness, Young Link), 5 (Donkey Kong, Falco, Jigglypuff, Mewtwo, Peach, Roy, Yoshi), 6 (Ganondorf, Link, Zelda), 8 (Bowser) | [wiki:Jump] |
| Up B / up smash from shield | cannot be input on the same frame as the jump: one frame of jump squat must pass. A move that hits on frame N is frame N+1 out of shield | [wiki:Out_of_shield] |
| Moves allowed in jump squat | up smash, up B, grab, item throw; not jab or tilts | [wiki:Jump-canceling] |
| Standing grab vs dash grab | standing grab is active on frame 7 and lasts 30 frames for most characters; dash grabs of non-tether characters are active from frame 7-14 depending on character (most 10-12) and last 40 frames | [web:fightcore.gg] |
| Fox shine out of shield | frame 4 (3 jump squat + 1) | [lib:Out of Shield Options Frame Data] |
| Falco shine out of shield | frame 6 (5 jump squat + 1) | [lib:Out of Shield Options Frame Data] |
| Fox ledge jump-shine timings | see [ledgedash](ledgedash.md) | [wiki:Ledgedash] |
| Run turnaround | `TurnRun` can only be interrupted by a jump, so a JC grab/usmash is the fast way to attack backward out of a run | [wiki:Dash] |

Why JC grab is preferred: most characters' standing grabs have more range, less startup and
less lag than their dash grabs [wiki:Jump-canceling]. Per-character grab frames are in
[grab-and-throw](grab-and-throw.md). [Yoshi](../characters/yoshi.md) cannot jump out of
shield, so he has no jump-cancelled options from shield [wiki:Jump-canceling].

## Why it matters

- Running grabs: nearly all grabs out of a dash in competitive play are JC grabs.
- Running up smash: [Fox](../characters/fox.md) and others kill with usmash out of a run.
- [Out of shield](out-of-shield.md): up B and up smash from shield are jump cancels.
- Fox/Falco pressure and combos: every action after a shine goes through a jump
  (waveshine, shine-grab, shine-usmash, multishine).

## Common errors

- Grab or attack pressed after jump squat ended: the character jumps and does an aerial
  (nair from Z, or an air dodge from L/R + A).
- Grab pressed before jump, or jump not pressed: dash grab (`CatchDash`), slower and
  laggier.
- JC usmash with A pressed late or without the jump registering: a dash attack comes out
  instead.
- Multishine: second shine a frame late (rises higher, slower) or early (still in jump
  squat: an up-B or nothing).

## How to detect it in a training mode

- JC grab success: `Dash`/`Run` -> `KneeBend` (1 to jump-squat frames) -> `Catch` [decomp].
  Failure: `CatchDash` (no jump cancel) or `KneeBend` -> `JumpF/B` -> `AttackAirN`/`EscapeAir`
  (too late).
- JC up smash: `KneeBend` -> `AttackHi4`. Up B: `KneeBend` -> the character's grounded up
  special state.
- Metric: frames spent in `KneeBend` before the cancel (1 is fastest).
- Multishine: frames between consecutive shine starts; grounded vs airborne shine state.

## Drill seeds

### Jump-cancel grab out of dash

- **id:** `jump-cancel-grab-reps`
- **Goal:** Always get the standing grab out of a dash.
- **Player:** any except characters whose dash grab is preferred
- **CPU:** any, standing
- **Setup:** Mid range.
- **CPU behaviour:** Stands, or shields.
- **Success:** `Catch` (not `CatchDash`) connects.
- **Fail:** Dash grab, jump, or whiff.
- **Variations:** From run; after a dash dance; against a rolling CPU.
- **Data needed:** Grab range and frames.

### Jump-cancel up smash kill

- **id:** `jump-cancel-usmash-punish`
- **Goal:** Punish a whiff with a running up smash.
- **Player:** [Fox](../characters/fox.md), [Pikachu](../characters/pikachu.md), [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md)
- **CPU:** any
- **Setup:** CPU at kill percent performs a laggy move at mid range.
- **CPU behaviour:** Whiffs a smash attack, then shields when actionable.
- **Success:** `AttackHi4` from `KneeBend` hits before the CPU shields.
- **Fail:** Jumped, dash attack, or late.
- **Variations:** Distance; CPU DI.
- **Data needed:** Player run speed, usmash startup, CPU lag.

### Shine jump-cancel options

- **id:** `jump-cancel-shine-followups`
- **Goal:** Jump out of shine on the first possible frame into a prompted option.
- **Player:** [Fox](../characters/fox.md), [Falco](../characters/falco.md)
- **CPU:** any, shielding or standing
- **Setup:** Adjacent to the CPU.
- **CPU behaviour:** Shields and shield grabs when possible.
- **Success:** Prompted follow-up (grab, usmash, wavedash, second shine, aerial) starts within the tight window and beats the shield grab.
- **Fail:** Grabbed or wrong action.
- **Variations:** Multishine count.
- **Data needed:** Shine frame data from the character files (not in the generic dump).

## Sources

- SSBWiki: Jump-canceling, Jump, Out of shield, Dash, Ledgedash
  (https://www.ssbwiki.com/Jump-canceling).
- FightCore (https://www.fightcore.gg/) grab and dash grab frames.
- Melee Library: "Out of Shield Options Frame Data" (Wiseman).
- `[decomp]`: state names from this repository.
