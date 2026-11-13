---
name: melee-sim
description: Run and test Melee interactions in the headless simulator (tools/melee_sim) instead of launching Dolphin - execute the real game and overlay code frame by frame from Python, drive both players' inputs, read fighter state, snapshot and restore, and run tools/tmtest.py specs in seconds. Use when testing or tuning a drill, event or CPU script, measuring an interaction (does it reach, how much stun, is the follow-up true), checking a game mechanic empirically, or whenever a task would otherwise mean booting Dolphin repeatedly.
---

# Simulate instead of launching Dolphin

What the simulator is, how far to trust it and how to fix it when it stops:
`docs/ai/simulator.md`. Spec format for event tests: `docs/ai/testing.md`.

Order of tools for any question about what the game does:

1. **Knowledge base** (`melee-knowledge` skill): frame data, formulas, calculators. Instant.
2. **Simulator** (this skill): the real engine, seconds. Spacing, pushback, hitlag, DI, CPU
   scripts, event logic, anything the calculators ignore.
3. **Dolphin** (`python tools/tmtest.py SPEC.json`): the ground truth. Run a finished drill's
   specs there before calling it verified; the simulator has known small differences.

Never loop on Dolphin to tune a value. Tune in the simulator, confirm once in Dolphin.

**Vanilla interactions run about 70 times faster on the native build**
(`tools/melee_native/native.py`, `docs/ai/native-ai.md`): no overlay, no Lab, no drills
there, but spacing, hitlag, knockback and anything between two pad-driven fighters is the
same game (`docs/ai/native-port.md`, "How close it is"). `Native` has this simulator's
`pad` / `step` / `fighter` / `snapshot` / `restore`:

```python
import sys; sys.path.insert(0, "tools/melee_native")
from native import Native
with Native() as n:                      # always close it: snapshots are processes
    n.start("fox", "marth")              # VS match, both pads ours, fighters standing
    here = n.snapshot()
    n.pad(0, stick=(1, 0)); n.step(40)
    print(n.fighter(0).summary()); n.restore(here)
```

Use the simulator when the question involves the overlay (an event, a drill, UCF, a hook).

## Setup

```sh
. .venv/bin/activate          # unicorn and numpy must be installed in it
OVERLAY_OUT=build/overlay-tmtest TM_TEST=1 python tools/overlay_build.py
```

Rebuild the test overlay after any C change. Fixtures under `build/sim/fixtures/` are keyed
by the DOL, so they refresh themselves.

## Run a test spec

```sh
python tools/melee_sim/tmtest_sim.py tests/tmtest/shineoos/*.json     # summary per spec
python tools/melee_sim/tmtest_sim.py --json SPEC.json                 # all records
```

Same specs and output as `tools/tmtest.py`. Add `"trace": 1` to a spec to log both fighters
every frame.

## Explore an interaction

```python
import sys; sys.path.insert(0, "tools/melee_sim")
from sim import Sim

s = Sim.match("lab", "fox", "marth", free=True)   # sandbox: both players from pads
s.pad(0, ["R"], r=1.0)                            # held until changed
s.pad(1, stick=(-0.6, 0)); s.step(40); s.pad(1)   # player 2 walks left
snap = s.snapshot()
s.pad(1, cstick=(-1, 0)); s.step(); s.pad(1)      # forward smash
for _ in range(30):
    s.step(); print(s.fighter(0).summary(), "|", s.fighter(1).summary())
s.restore(snap)                                   # 5 ms; try the next variant
```

- Characters by `data/characters/` id; stages `final-destination battlefield dream-land
  yoshis-story fountain-of-dreams pokemon-stadium`.
- `free=True` switches the event's own logic off. Leave it out to run the event as the game
  does (then the event controls the CPU).
- `s.fighter(i)` is a view at the time it is created; make a new one after stepping.
  Fields: `state`, `state_frame`, `pos`, `vel`, `facing`, `airborne`, `percent`, `hitlag`,
  `hitstun`, `shield`. State ids are `ftCo_MS_*` (`src/melee/ft/kinds/ftCommon/forward.h`,
  counted from 0) or the character's enum (front matter `code:` of its file in
  `data/characters/`).
- Other memory: `s.m.u32/f32/u8(addr)`, `s.m.sym.addr("symbol")`, offsets from the decomp's
  headers. Game output: `s.h.reports`. Call a game function: `s.call("name", args)`.

Patterns:

- **Measure a window.** Snapshot before the action; step and record the frame each state
  changes (`GuardSetOff` 181 = shield stun; `Wait` 14 = actionable on the ground); compare
  with the calculator's number.
- **Sweep a parameter.** Loop over distances, percents or delays, restoring the snapshot
  each time. A hundred variants take seconds.
- **Find a script's timing.** Run the CPU's inputs from a spec in the sandbox, print the
  trace, adjust the frames, restore, repeat.
- **Set a state directly** (percent, position) by writing fighter fields only when getting
  there with inputs is impractical; say so in the result, since the game did not get there
  by itself.

## Reporting

Say which backend produced each result (simulator or Dolphin). A number measured only in
the simulator goes into a spec or the knowledge base tagged `[sim 2026-..]`; after the
Dolphin run it can be `[tested ..]`. If the simulator and Dolphin disagree, report it and
treat it as a simulator bug (`docs/ai/simulator.md`, "When a run stops").
