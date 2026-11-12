---
name: design-training-scenario
description: Turn a prompt like "shine out of shield against Marth's forward smash" or "Sheik tech-chase practice on Falco at 40%" into a concrete, data-backed training scenario spec - player, CPU, stage, positions, percents, CPU inputs frame by frame, success and fail conditions - using the data/ knowledge base. Use when asked to create, design, propose or tune a training drill, event or scenario, before writing any event code.
---

# Design a training scenario from a prompt

Output of this skill: a **scenario spec** (format below) whose every number is looked up or
computed, plus a list of what still has to be tuned in Dolphin. Implementing the spec as an
event is a separate step: follow the `add-training-event` skill if it exists, otherwise use
`src/tmce/events/shineoos/` (deck of CPU input scripts, `OosScenario`, `TmRotDeck` in
`src/melee/tm/rotation/tm_rotation.h`) as the worked example and `port-tm-feature` for TM-CE
services (savestates, menus, messages).

Lookups go through the `melee-knowledge` skill. Do not take frame numbers or percents from
memory.

## 1. Parse the prompt into the five questions

| Question | Where the answer comes from |
|-|-|
| What skill is being trained, and what does one repetition look like? | The prompt; `Character tech` and `Drill seeds` in `data/characters/<player>.md`; `Drill seeds` and `How to detect it in a training mode` in `data/techniques/<id>.md` |
| Who is the player, who is the CPU? | The prompt. If the CPU is unspecified, pick opponents where the situation is real: `Matchup notes`, `As the training dummy`, and `data/characters/README.md` (weight, fall speed, tier) |
| What is the CPU doing? | An attack to punish, a recovery to edgeguard, a tech/DI choice to react to, a shield to pressure. Take realistic options from the CPU character's `Neutral game`, `Recovery`, `As the training dummy` |
| What state does a repetition start from? | Positions, facing, percent, who is in which action state on frame 0 |
| What is success, observably? | Action states, hits, frame counts. Never "the player played well" |

Check for an existing seed first: `grep -n "^- \*\*id:\*\*" data/characters/<id>.md
data/techniques/*.md`. A matching seed gives the structure; still verify its numbers.

If the prompt leaves a real choice open that changes the design (which character the player
is, punish vs. escape), ask once. Otherwise pick the common case and state the assumption.

## 2. Get the numbers

Run these, and paste the relevant lines into the spec's `evidence`:

```sh
python tools/melee_data/query.py <cpu> <move>              # startup, active frames, total, IASA
python tools/melee_data/query.py shield <cpu> <move> <player>   # advantage on shield + which OOS options punish
python tools/melee_data/query.py oos <player>              # the player's out-of-shield options
python tools/melee_data/query.py kb <attacker> <move> <defender> <percent> [--cc]
python tools/melee_data/query.py thresholds <attacker> <move> <defender>   # knockdown / crouch-cancel percents
python tools/melee_data/query.py jump <cpu>                # jump squat and hop timing for aerial scripts
```

Typical derivations:

- **Punish-on-shield drills.** Window = `-advantage` frames. The scenario is only meaningful
  if at least one of the player's OOS options fits; list which ones do and which do not.
  For aerials on shield the advantage depends on when the CPU lands: the tool gives the best
  case (hit on the last airborne frame, L-cancelled). A realistic CPU hits earlier, which
  makes it more punishable; choose and state the timing.
- **Tech-chase and knockdown drills.** Use `thresholds` for the percent where the starter
  knocks down (and where crouch cancel stops preventing it). Tech options and their
  intangibility and length are in the defender's `Techs and getups` table: tech in place 26
  frames, tech rolls 40, with intangibility ending on frame 20; missed-tech getup options are
  listed there too. The reaction window is what remains after intangibility ends.
- **Combo and chain-grab drills.** Hitstun from `kb`; the follow-up is true only if its
  startup (plus travel) fits inside hitstun minus the attacker's remaining lag. DI changes
  everything: specify the CPU's DI as a randomised option and take the percent window from
  the sourced table in the character file, not from one calculation.
- **Edgeguard drills.** CPU recovery options from its `Recovery` section; ledge option
  lengths and intangibility from `Ledge options`; ledge-hang intangibility is 30 frames.
- **Execution drills** (wavedash, shield drop, ledgedash, L-cancel): the timing windows are
  in `data/techniques/<id>.md`; the per-character numbers (jump squat, landing lag, traction)
  are in the character front matter.
- **CPU aerial approach scripts.** Build the input timeline from jump squat (`jump`), the
  aerial's startup and the fast-fall and L-cancel timing: jump on frame 0, aerial input so
  the hitbox is out when it reaches the target, fast fall after the apex, L-cancel within 7
  frames before landing. The estimate is +/-2 frames; mark the timeline `tune: true`.

## 3. Write the spec

One YAML block. Keep every field; write `unknown` or `tune` instead of guessing.

```yaml
scenario:
  id: fox-shine-oos-marth-fsmash          # <player>-<skill>-<cpu>-<situation>, kebab-case
  title: Shine out of shield vs Marth forward smash
  goal: Punish a shielded forward smash with shine out of shield before Marth can act.
  seed: fox-shine-oos                      # drill seed id it came from, or none
  player: {character: fox, allowed: [fox, falco]}
  cpu: {character: marth, costume: 0}
  stage: final-destination                 # flat and hazard-free unless the drill needs platforms/ledge
  start:
    player: {state: shield, x: 0, facing: toward-cpu, percent: 0}
    cpu: {state: standing, distance: tune, facing: toward-player, percent: 0}
    trigger: player holds shield           # what starts a repetition
  cpu_script:                              # frame 0 = the frame the CPU starts acting
    - {frame: 0, hold: 1, stick: [0, 0], cstick: [127, 0], buttons: []}   # stick X is toward the player
  cpu_randomise:                           # options the CPU picks between, with weights
    - {name: delay, values: [0, 10, 25], weights: [1, 1, 1]}
  timeline:                                # what should happen, in frames, from the data
    - {frame: 10, event: "fsmash hitbox out (active 10-13)"}
    - {frame: 10, event: "shield hit: shield stun 10"}
    - {note: "Marth actionable on frame 48: advantage -27"}
    - {note: "shine OOS is out 4 frames after acting: lands if started within 23 frames of stun ending"}
  success:
    - player enters SpecialAirLwStart (shine) and it hits the CPU before the CPU is actionable
  fail:
    - player is hit, grabbed, or the CPU becomes actionable first
    - timeout: 60 frames after the shield hit
  variations:
    - {name: follow-up, values: [shine only, shine + any hit, waveshine up smash]}
    - {name: tipper vs. close spacing, effect: "changes shield pushback and whether shine reaches"}
  detect:                                  # how the event code observes it
    player_states: [ftFx_MS_SpecialLwStart..ftFx_MS_SpecialAirLwTurn]   # from the fighter's forward.h
    cpu_hit_by: player
  evidence:                                # tool output and file sections the numbers came from
    - "query.py shield marth fsmash fox -> -27 (first active frame)"
    - "query.py oos fox -> Down B (aerial) frame 4"
  tune:                                    # must be checked in Dolphin
    - cpu start distance so the fsmash connects with the shield
    - whether shine reaches after shield pushback at tipper range
  confidence: {frames: extracted, spacing: untested, percents: n/a}
```

Rules for the spec:

- Frames are 1-indexed for move data and 0-indexed for `cpu_script` (frame 0 is the first
  input frame); say which wherever both appear.
- `cpu_script` uses the input model of the existing events: per entry a start frame, a hold
  length, main stick and C-stick as signed bytes (X positive = toward the player), and
  buttons. CPU reactions that are not fixed inputs (DI, tech choice, recovery choice) go in
  `cpu_randomise` with weights.
- Action state names in `detect` come from the decomp (`src/melee/ft/kinds/ftCommon/forward.h`
  for common states such as `ftCo_MS_GuardSetOff`, `ftCo_MS_Passive`, `ftCo_MS_DownWaitU`;
  the character's own `forward.h`, path in the character file's front matter `code:`, for
  specials). Use the `find-symbol` skill if a name does not grep.
- Several CPU characters or attacks for one skill are one event with a deck of scenarios
  (one spec, `cpu` and `cpu_script` repeated per entry), not several events.
- Everything the tools cannot know goes in `tune`: distances, shield pushback, whether a
  hitbox reaches, exact aerial timing, staleness, DI ranges. Hitbox sizes and offsets are in
  `data/framedata/<id>.json` if a first estimate of range is needed.

## 4. Sanity checks before handing off

- The repetition is possible: the window exists (`-advantage` >= the fastest relevant option,
  hitstun >= follow-up startup, the percent is inside the sourced range).
- The CPU behaviour is something that character really does (it appears in their file), and
  the randomisation covers the options a real opponent mixes between.
- Success and fail are mutually exclusive and both observable; there is a timeout.
- Every number has an `evidence` line or is in `tune`. Numbers tagged `[unverified]` in the
  prose, special-move frames (+/-1) and jump timings are in `tune`.
- The drill resets fast (savestate or re-place) and has an obvious difficulty knob.

## 5. Report

Give the user the spec, the assumptions made, and the `tune` list. If the knowledge base was
missing something the scenario needed, say what, and add it to the character or technique
file (with a source tag) so the next scenario has it.
