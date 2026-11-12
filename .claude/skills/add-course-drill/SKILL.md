---
name: add-course-drill
description: Implement one course drill end to end - from its spec in data/courses/<id>.md to C on the course engine, with its in-game guide, timing feedback, statistics, reference input script and an automated Dolphin run that proves it. Use when asked to implement, build, port or fix a training drill or course event, or to move an existing TM-CE event onto the course engine.
---

# Add a course drill

Architecture and milestones: `docs/ai/training-courses.md`. Spec format and status ladder:
`data/courses/README.md`. TM-CE services and build: `docs/ai/tmce-native.md`. Overlay rules:
`CLAUDE.md` (no edits to vanilla functions, hooks through the hook tables, C only).

**Engine status (update this line when it changes): not built.** As of 2026-11-12 the course
engine (`src/tmce/course/`) and the hub are planned (milestone M1). Until M1 lands, the
worked example of a drill is the standalone event `src/tmce/events/shineoos/` (`event.c`,
`desc.c`, `shineoos.h`) with `src/melee/tm/rotation/` and `tools/test_shineoos.py`. If you
are asked for a drill before the engine exists, say so and either build the engine piece the
drill needs first (preferred: extract it from Shine OoS) or build the drill as a standalone
event in the same shape, so it can move onto the engine unchanged in behaviour.

## 0. Preconditions

- The drill has a section in `data/courses/<id>.md` with `status: specified`: full spec,
  `grading`, `reference`, guide, every number in `evidence` or `tune`. If it is only
  `planned`, specify it first with `design-training-scenario`.
- The matching build passes and `python tools/overlay_build.py` builds (`build-melee` skill).

## 1. Re-check the spec against the data

Run the spec's `evidence` commands again (`python tools/melee_data/query.py ...`). If a
number changed or was wrong, fix the spec before writing code. Read the `knowledge` links.

## 2. Write the drill

A drill is a description plus callbacks; everything common belongs to the engine. Per drill:

| Part | Content | From the spec |
|-|-|-|
| Description | id, part, player characters, name, goal, stage, `leads_to` | header fields |
| Deck | scenarios: CPU character, start positions and percents, CPU input script | `deck`, `cpu_script` |
| CPU choices | weighted random options per attempt | `cpu_choices` |
| Setup | place fighters and states for one attempt | `start`, `trigger` |
| Think | per frame: drive the CPU, run detectors, decide success or fail with a timing verdict | `success`, `fail`, `grading`, `detect` |
| Reference | the player inputs that solve it | `reference` |
| Guide | pages, timeline, key numbers | the guide bullets (generated when the generator exists; until then transcribed, with a comment naming the course file as the source) |
| Options | tolerance and drill-specific options | `grading.tolerance`, `variations` |

Rules while writing:

- **Numbers.** Frame data and attributes come from the generated tables
  (`tools/melee_data/gen_course_tables.py`, planned) or, until it exists, from named
  constants each with a comment giving the `query.py` line that produced it. Tuned values
  (distances, script frames) are named constants with a comment saying how they were tuned.
  No bare literals for game facts.
- **Action states** by enum name: MexTK names on the TM-CE side; when only the decomp has
  the name, define it next to its use with the decomp name in a comment (as `SHINE_FIRST`
  in Shine OoS does) and check the value with `find-symbol`.
- **Timing verdicts.** Record the frame of each graded input relative to the event the spec
  names (`at:`). On failure report the measured value and the window ("shine on frame 6,
  needed 4: 2 late"), never a bare "fail".
- **Detectors.** Use the engine's; add a new one to the engine when a second drill would
  need it. TM-CE already tracks much per fighter in `FighterData.TM` and the OSD code
  (`src/melee/tm/osd*/`): look there before writing a detector.
- **CPU.** Scripted inputs through the engine's script player (stick X positive = toward the
  player). Randomised choices through `cpu_choices`. Set the CPU's AI off while scripted, as
  Shine OoS does.
- **Reset.** Savestate after setup when the drill mutates anything beyond fighters'
  positions; re-place fighters otherwise.
- **State.** Courses are offline: overlay statics are fine. Nothing here runs under rollback.
- **Style.** The repo's (`CLAUDE.md` rule 4) for native code; TM-CE's own style inside
  TM-CE-side files, as the existing events do.

Files (planned layout): `src/tmce/course/drills/<area>/<drill>.c`, registered in the
engine's drill list; standalone events before M1: `src/tmce/events/<name>/` plus a line in
`src/tmce/units.txt` and an entry in `src/tmce/custom_pages.c`.

## 3. Build

```sh
. .venv/bin/activate
ninja                              # matching build: must still report the SHA-1 match
python tools/overlay_build.py      # overlay; runs tools/overlay_check.py
```

A drill never touches vanilla source. If you think it needs a new hook, that is engine work:
`add-native-code` skill, and re-run the matching build.

## 4. Prove it: simulator first, then Dolphin

Write the runs below as `tools/tmtest.py` specs under `tests/tmtest/<event>/`
(`docs/ai/testing.md`). Develop and tune them in the simulator
(`python tools/melee_sim/tmtest_sim.py`, `melee-sim` skill: seconds per run, no window), and
measure `tune` values there instead of guessing. When they pass, run the same specs once in
Dolphin (`python tools/tmtest.py`); only that run makes a drill `verified`.


Every drill gets these runs (model: `tests/tmtest/shineoos/`):

1. **Reference passes.** With the reference script as the player's inputs, every scenario
   of the deck is graded a success over repeated attempts. Report per scenario.
2. **Off-by-one fails.** The same script with the graded input one frame outside the window
   is graded a failure with the right verdict text.
3. **CPU behaves.** For each scenario and each `cpu_choices` value: the CPU's action really
   happens (the attack reaches the shield, the recovery reaches the ledge, the tech comes
   out). Scenarios where it does not are fixed or removed, not left in.
4. **By hand**, when the owner or a display is available: the guide opens and reads
   correctly, the demonstration plays, statistics count.

Tune the spec's `tune` list here; write the tuned values and how they were found back into
the spec.

## 5. Update status and docs

- In the course file: `status: implemented` with `code:`; `verified` only after step 4's
  runs 1-3 passed, with `verified: <date>` and the command that was run.
- If the drill replaced a TM-CE event behind the hub, note it in the course file's part
  introduction and in `docs/ai/training-courses.md`.
- Anything learned about the game that the knowledge base did not have goes into
  `data/characters/` or `data/techniques/` with a source tag (`[tested 2026-..]` for values
  measured in Dolphin), then `python tools/melee_data/render.py`.

## Report

State exactly which of these ran: matching SHA check, overlay layout check, reference-pass
run, off-by-one run, CPU-behaviour run, manual check. A drill is not "done" on a build
alone.
