---
schema: melee-technique/v1
id: pivot
name: Pivot
aliases: [pivoting, empty pivot, pivot grab, pivot smash, pivot fsmash, pivot tipper, smash turn]
category: movement
difficulty: 4
related: [dash-dance, moonwalk, jump-cancel, grab-and-throw, wavedash]
characters: all
summary: Using the single standing frame of a dash turnaround to stop or to start any grounded move facing the other way, with the dash's momentum.
---

# Pivot

## What it is

When a dashing character reverses direction during the initial dash, there is exactly one
frame of the `Turn` state between the two dashes. On that frame the character counts as
standing and can start any ground attack except neutral B. If the stick is back at neutral
after that frame, the character simply stands still, facing the new direction. Using that
frame is a pivot [wiki:Dash] [wiki:Pivot].

- **Empty pivot:** stop on the turn frame (stick to neutral). A way to halt a dash
  instantly and stand.
- **Pivot attack:** input fsmash, ftilt, jab, dtilt, grab, etc. on the turn frame. The
  attack comes out facing the new direction while the character keeps some slide.

## Inputs

1. Dash one way.
2. Smash the stick the opposite way (the turn frame occurs).
3. Either return the stick to neutral immediately (within the same frame window) for an
   empty pivot, or press the attack on the turn frame: C-stick for a smash, A or Z for
   jab/grab, etc.

The window is 1 frame in Melee (it was longer in Smash 64) [wiki:Pivot]. Common hand
methods (flick and let the stick return, or tap opposite and input C-stick together) are
covered in Gravy's video "Different Ways to Pivot" in the Library; not viewable here.

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Pivot window | 1 frame (the `Turn` frame inside a dash dance) | [wiki:Pivot] [wiki:Dash] |
| Available on that frame | all grounded attacks except neutral B; standing still if the stick is neutral afterwards | [wiki:Dash] |
| Must be in the initial dash | yes; in the run the turnaround is the long `TurnRun` animation (up to 51 frames, Marth), which only a jump interrupts | [wiki:Dash] |
| Initial dash length (time available) | 7-18 frames by character, table in [dash-dance](dash-dance.md) | [wiki:Dash] |
| Compared with alternatives | pivot grab and pivot fsmash are typically faster than doing the same move out of a raw dash or a wavedash | [wiki:Pivot] |

For comparison, the other ways to do a standing move while moving: [wavedash](wavedash.md)
(jump squat + 10 frames before acting), run then crouch (`RunBrake` then `Squat`), or
[jump-cancel](jump-cancel.md) (grab and usmash only).

## Why it matters

- **Spacing kills:** [Marth](../characters/marth.md) pivot fsmash to land the tip after a
  throw or on a falling opponent; [Fox](../characters/fox.md)/[Falco](../characters/falco.md)
  pivot usmash/fsmash; [Jigglypuff](../characters/jigglypuff.md),
  [Peach](../characters/peach.md) and others pivot grab.
- **Dash back, then attack forward:** dash away from an approach, pivot, and hit toward the
  opponent with a standing move (for example a pivot ftilt or grab), without wavedash lag.
- **Stopping precisely:** empty pivot to stand at an exact distance, then act.
- **Facing:** turning around quickly to use a back-facing move (bair set-ups) or a
  forward-facing one after running past.

## Common errors

- Attack input a frame late: a dash attack or dash grab in the new direction comes out
  instead.
- Attack input early: the move comes out in the original direction (or as a dash attack).
- Stick held too long in the new direction for an empty pivot: the character dashes back
  instead of stopping.
- C-stick sideways smash during the first 3 frames of the new dash also gives an fsmash
  (the dash's own fsmash window [wiki:Dash]), which hides timing errors for fsmash but not
  for grab, jab or tilts.

## How to detect it in a training mode

- Empty pivot: `Dash` -> `Turn` (1 frame) -> `Wait` with facing reversed [decomp].
- Pivot attack: `Dash` -> `Turn` (1 frame) -> attack state (`AttackS4*`, `Catch`,
  `Attack11`, `AttackS3*`, `AttackLw3`...) with facing reversed, not `AttackDash` or
  `CatchDash`.
- Failure: `Dash` in the new direction followed by `AttackDash`/`CatchDash`, or the attack
  starting from the original facing.
- Spacing drills additionally check which hitbox connected (e.g. Marth's tip).

## Drill seeds

### Empty pivot stop

- **id:** `pivot-empty-reps`
- **Goal:** Stop on the turn frame.
- **Player:** any
- **CPU:** none
- **Setup:** Flat stage.
- **CPU behaviour:** None.
- **Success:** `Dash` -> `Turn` -> `Wait`, facing reversed, 10 times.
- **Fail:** Second dash, or slow turn.
- **Variations:** Stop on a marker; pivot then immediate jab.
- **Data needed:** None beyond states.

### Pivot grab on approach

- **id:** `pivot-grab-vs-approach`
- **Goal:** Dash away from an approach and pivot grab it.
- **Player:** [Marth](../characters/marth.md), [Jigglypuff](../characters/jigglypuff.md), [Peach](../characters/peach.md), [Sheik](../characters/sheik.md), [Fox](../characters/fox.md)
- **CPU:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Captain Falcon](../characters/captain-falcon.md)
- **Setup:** Mid range.
- **CPU behaviour:** Approaches with a SHFFL aerial or dash attack aimed at the player's start position.
- **Success:** CPU whiffs and is grabbed by a standing grab (`Catch`), not a dash grab.
- **Fail:** Dash grab, hit, or miss.
- **Variations:** Pivot ftilt/fsmash instead.
- **Data needed:** Grab ranges and frames ([grab-and-throw](grab-and-throw.md)), CPU approach ranges.

### Pivot tipper

- **id:** `pivot-fsmash-tipper`
- **Goal:** Kill with a tipped pivot fsmash after a throw.
- **Player:** [Marth](../characters/marth.md)
- **CPU:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md)
- **Setup:** CPU grabbed at kill percent near centre stage.
- **CPU behaviour:** Random DI on the throw; no jump until hitstun ends.
- **Success:** Fsmash connects with the tip hitbox and the CPU is KO'd.
- **Fail:** Non-tip hit, miss, or dash attack.
- **Variations:** fthrow vs uthrow set-ups; platforms.
- **Data needed:** Throw trajectories, fsmash hitbox data, kill percents from the character files.

## Sources

- SSBWiki: Pivot, Dash (https://www.ssbwiki.com/Pivot).
- Melee Library: "Different Ways to Pivot" (Gravy, video) and "Techniques to Aid
  Smashturns" (Gravy, Reddit) by title/description only.
- `[decomp]`: state names from this repository. Character examples are general knowledge
  without numbers.
