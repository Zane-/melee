---
name: add-course-drill
description: Implement one course drill end to end - from its spec in data/courses/<id>.md to C on the course engine, with its in-game guide, timing feedback, statistics, reference input script and an automated Dolphin run that proves it. Use when asked to implement, build, port or fix a training drill or course event, or to move an existing TM-CE event onto the course engine.
---

# Add a course drill

Architecture and milestones: `docs/ai/training-courses.md`. Spec format and status ladder:
`data/courses/README.md`. TM-CE services and build: `docs/ai/tmce-native.md`. Overlay rules:
`CLAUDE.md` (no edits to vanilla functions, hooks through the hook tables, C only).

**Engine status (update this when it changes): M2, 2026-11-12.** The engine runs drills
with a guide overlay, demonstrations and generated frame data, and the hub lists them
(`docs/ai/training-courses.md` says exactly what is built). One drill exists and is the
model: `src/tmce/events/course/drills/fox_shine_oos.inc.h`. Not built yet, so a drill cannot
use them: savestate resets, the detector library, guide text generated from the course file.

Adding a drill touches four places:

1. `course.h`: a new `DRILL_...` in `enum CourseDrillId`.
2. `desc.c`: its `CourseDrillInfo` in `Course_Drills[]` (id as in `data/courses/`, name,
   goal, part, player characters as a `CSSID_*` mask, stage, first CPU, deck).
3. `drills/<name>.inc.h`: options, state, `Setup`, `Think`, the reference script
   (`CourseRefInput[]` against marks the Think announces with `course_Mark`), the `Guide`
   callback, and the `CourseDrill`; included from `event.c` and added to its `drills[]`
   table. Prefix every identifier (all drills share one translation unit).
4. `tests/tmtest/course/<drill-id>/*.json`: per scenario, a spec with scripted inputs and a
   `demo_` spec with none and option 4 (Demonstration) = 2, expecting a success with
   `"demo": 2` and `measured` equal to `target`. The `demo_` spec is the proof that the
   reference solves the drill.

Finding a reference's offsets: start from the spec's frames, run the `demo_` spec in the
simulator, read the verdict, adjust, repeat (a build and a run take about 20 seconds). An
input one frame early often comes out as a different action, not nothing.

Numbers in `Think` and `Guide` come from `course_Fighter(c->hd)` / `course_Fighter(c->cd)`
(jump squat, weight, per-move `hit`, `faf`, `total`, landing lag, intangibility); add a
move to `MOVES` in `tools/melee_data/gen_course_tables.py` if it is missing and rerun it.

A spec selects the drill with `"event": "course", "drill": "<drill-id>"`.

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

Engine services a drill calls (`event.c`): `course_Place`, `course_Script`, `course_Phase`,
`course_Message`, `course_Measure`, `course_Report` / `course_ReportF`, `course_Result`,
`course_Retry`; its options are `Options_Main[OPT_COMMON_COUNT + i]`. The hub needs nothing
per drill: it lists `Course_Drills[]`. After changing the hub or the flow, run
`python tests/sim/hub_roundtrip.py`.

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

**Anything drawn needs Dolphin.** The simulator skips all drawing code, so a new guide,
HUD element or menu can crash or look wrong there without any spec noticing. Look at it
once: a frame dump from one contained run (`tools/dolphin_harness.py` with
`dump_frames=True` under `xvfb-run`, own process group, check `pgrep -c dolphin-emu` is 0
afterwards; `docs/ai/testing.md`, "Process hygiene").

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
