# Courses

A course is the ordered training path for one character: what to drill, in what order, with
what guidance. Architecture and status: `docs/ai/training-courses.md`. A course file is the
single source for a drill's goal, guide text and specification; the game's hub lists and
guide overlays are meant to be generated from it (generator planned, milestone M2).

| File | What |
|-|-|
| `<character-id>.md` | That character's course (ids as in `../characters/`) |
| `universal.md` | Drills every character has, parameterised per character |

## The four parts

| Part | Teaches | Starts from | Ends when | The CPU |
|-|-|-|-|-|
| `tech` | Executing one technique | A fixed state, no pressure | The inputs were on the right frames, or not | Absent, or a passive target |
| `neutral` | Winning the first hit | Both characters free, at a spacing | The player lands the opening (hit, grab, shield hit they can punish) or is hit | Commits to one of a few realistic options, with a reaction delay |
| `punish` | Converting an opening | The hit, grab or shielded move has just happened | The follow-up connected before the CPU could act, or the CPU escaped | Escapes as well as the drill's tolerance allows: DI, SDI, tech choice, mash, jump out |
| `defense` | Escaping and surviving | The CPU has the advantage: combo, pressure, edgeguard | The player is out (or back on stage), or was hit again | Performs the real sequence, scripted |

Order within a part goes from prerequisites to combinations. Order between parts for a new
player: `tech` basics → `punish` basics → `defense` basics → `neutral`, but every part is
open from the start.

`leads_to` chains drills across parts: a neutral drill names the punish drill that begins
where it ends; a punish drill may name the defense drill that is its mirror.

## File format

Front matter, then one `##` section per part. Each part starts with a **plan table** (every
drill of the part, in order, one row each) followed by a `###` section for each drill that
is `specified` or further: a YAML block (the spec) and a guide. A `planned` drill is only a
table row.

Plan table columns: `#` (order), `id`, `Drill`, `Goal`, `CPU`, `Requires`, `Leads to`,
`Knowledge`, `Status`. Universal drills appear as rows with the id `universal-...`.

````markdown
---
schema: melee-course/v1
id: fox
character: fox
status: draft            # draft | in-progress | playable
summary: one sentence on what completing the course gives the player
includes: [universal]    # other course files whose drills this course pulls in
---

# Fox course

## Tech

| # | id | Drill | Goal | CPU | Requires | Leads to | Knowledge | Status |
|-|-|-|-|-|-|-|-|-|
| 12 | `fox-jc-shine` | Frame-perfect jump-cancelled shine | Jump out of shine on the first possible frame, every time | none | 8 | `fox-multishine` | [tech](../characters/fox.md#jump-cancelled-shine) | specified |

### Jump-cancelled shine

```yaml
id: fox-jc-shine               # <character>-<kebab>, unique across all courses
part: tech
status: planned                # planned | specified | implemented | verified
order: 12
goal: Jump out of shine on the first possible frame, every time.
requires: [fox-waveshine]      # drill ids that should be comfortable first
leads_to: fox-multishine
knowledge: [../characters/fox.md#jump-cancelled-shine]   # where the facts are
cpu: none                      # none | passive:<id> | [<id>, ...] for a deck
stage: final-destination
```

**Guide**

- **What:** ...
- **Why:** ...
- **Inputs:** ...
- **Timing:** ...
- **Errors:** verdict → what happened → fix
````

### Status values

| Status | Meaning | Required content |
|-|-|-|
| `planned` | Belongs in the course; a row in the plan table | id, order, goal, knowledge |
| `specified` | Fully designed; ready to implement | everything in "Full spec" below, every number with evidence |
| `implemented` | Code exists and builds | plus `code:` path |
| `verified` | Reference script passes and the off-by-one script fails in an automated Dolphin run | plus `verified:` date and what was run |

Never mark a drill beyond what was actually done. `verified` means the automated run, not
"it looked right".

### Full spec (status `specified` and later)

The scenario fields are those of the `design-training-scenario` skill; the course adds the
teaching fields. All of these go in the drill's YAML block:

```yaml
id: fox-shine-oos
part: punish
status: specified
order: 3
goal: Punish a move on shield with shine out of shield before the opponent can act.
requires: [fox-waveshine]
leads_to: fox-waveshine-usmash
knowledge: [../characters/fox.md#shine-out-of-shield, ../techniques/out-of-shield.md]
player: {character: fox, also: [falco]}      # other characters the same drill serves
stage: final-destination
deck:                                        # one entry per scenario; CPU character each
  - name: Marth - forward smash
    cpu: marth
    start: {distance: tune, cpu_percent: 20, player_state: shield}
    cpu_script:                              # frame 0 = CPU starts acting; X toward the player
      - {frame: 0, hold: 1, cstick: [127, 0]}
    window: {from: shield stun ends, frames: 23}   # derived, see evidence
cpu_choices:                                 # randomised per attempt, weights
  - {name: delay, values: [8, 20, 40], weights: [1, 1, 1]}
trigger: player holds shield
success: shine hits the CPU before the CPU is actionable
fail: [player hit or grabbed, CPU actionable first, timeout 60 frames after the shield hit]
grading:                                     # what the timing verdict measures
  measure: frames from first actionable frame out of shield to shine start
  perfect: 1                                 # jump on the first frame, shine on frame 4
  tolerance: {default: 3, options: [0, 1, 3, 6, any]}
  verdicts:
    - {when: shine after the window, say: "Late by {n} frames"}
    - {when: no shine, say: "No shine: jump, then down-B on the first airborne frame"}
    - {when: shine missed, say: "Out of range: this spacing needs wavedash or nair instead"}
reference:                                   # inputs that solve it (player side)
  - {at: shield stun ends, frame: 1, buttons: [X]}
  - {frame: 4, stick: [0, -127], buttons: [B]}
stats: [success_rate, best_streak, mean_frame_error]   # shown in hub and result
variations:
  - {name: follow-up, values: [shine only, shine + any hit, waveshine up smash]}
detect:
  player_states: [ftFx_MS_SpecialLwStart..ftFx_MS_SpecialAirLwTurn]
evidence:
  - "query.py shield marth fsmash fox -> -27 (first active frame)"
  - "query.py oos fox -> Down B (aerial) frame 4"
tune:
  - CPU start distance per scenario
```

Rules:

- Every number is in `evidence` (a `query.py` line or a knowledge-base section with a source
  tag) or in `tune`. `[unverified]` facts from the knowledge base go in `tune`.
- `grading` is required: a drill must be able to tell the player how far off they were, not
  only that they failed. If nothing about timing can be measured, say what is measured
  instead (position, choice, reaction time).
- `reference` is required from `specified` on. It is the demonstration, the guide's input
  timeline and the automated proof that the drill is winnable.
- For `neutral`, `punish` and `defense`, `cpu_choices` must contain the options a real
  opponent mixes between, taken from the CPU character's file. One fixed CPU action is only
  acceptable as the first, introductory tolerance level.
- The guide is written for the player, in the second person, short. Each bullet at most two
  lines on screen (about 40 characters per line in the overlay; the generator will wrap).
  Numbers in the guide repeat numbers in the spec; they are not new facts.
- Frames are 1-indexed for move data and counted from a named event (`at:`) in scripts.

## Universal drills

`universal.md` holds drills that are the same for everyone (wavedash, L-cancel, SHFFL, tech,
ledgedash, shield drop, SDI, ASDI down, DI...). A character course lists them as plan-table
rows in the position where they belong in that character's path. Per-character numbers
(jump squat, landing lag, traction) are not parameters to write down: the engine reads them
from the generated frame data tables for whoever the player picked.

A character-specific version replaces the universal one when the technique is materially
different for that character (Peach float cancel instead of L-cancel timing, Yoshi parry
instead of powershield).

## Writing a course

Use the `plan-character-course` skill. In short: take the character's `Character tech`,
`Punish game`, `Recovery`, `As the training dummy` and `Drill seeds` sections and the
technique files' seeds, sort them into the four parts, order them by prerequisite, chain
them with `leads_to`, and mark everything `planned`. Specify and implement drills one at a
time from the top of each part (`design-training-scenario`, then `add-course-drill`).
