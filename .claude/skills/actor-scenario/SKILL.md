---
name: actor-scenario
description: Write, run and judge a scenario on the native build - a situation (fighters placed, damage), what the opponent does (a Melee Actor script of intentions, or a trained policy), a stand-in for the player, and what counts as success - and get a verdict in milliseconds, over many varied runs. Use when asked to test an interaction or a punish "by instruction" rather than by frame, to prototype a drill for AI-driven training, to check how robust a script is to spacing, or to add a step or condition to the Melee Actor.
---

# Actor scenarios on the native build

Design and status: `docs/ai/native-ai.md` (the interface, the plan) and
`docs/ai/melee-actor.md` (what a step is, why not frames). The native build is the vanilla
game: no overlay, no Lab, no course engine, no UCF. For those, use the `melee-sim` skill.

## Run

```sh
. .venv/bin/activate
python tools/native_build.py                       # once, and after changing src/host/
python tools/melee_actor/run.py tests/actor/scenarios/whiff_punish.json --steps
python tools/melee_actor/run.py FILE --runs 40 --jitter 4    # every run moved about
python tools/melee_actor/run.py FILE --json                  # everything, for a program
```

A run is a few milliseconds; starting the game is 0.4 s. Use `--runs` with `--jitter`
before believing a script: one passing run says little.

## A scenario file

```json
{
  "name": "Punish a whiffed forward smash",
  "p1": "fox", "p2": "marth", "stage": "final-destination", "seed": 1,
  "setup": [{"place": 0, "x": -30, "facing": 1},
            {"place": 1, "x": 12, "facing": -1, "percent": 30}],
  "opponent": {"port": 1, "script": [{"do": "wait", "frames": 40},
                                     {"do": "attack", "move": "fsmash"},
                                     {"do": "hold", "frames": 90, "buttons": ["R"]}]},
  "player": {"port": 0, "script": [{"do": "wait", "until": "target_swung"},
                                   {"do": "rush", "move": "grab"},
                                   {"do": "throw", "direction": "up"}]},
  "frames": 400, "after": 10,
  "success": ["target_hit", "not_hit"]
}
```

- `setup`: `place` a port's fighter at `x` (and `y`: the floor at or below it), `facing`
  1 or -1, `percent`, `"air": true` to start falling from there.
- `opponent` / `player`: a `script`, or `"policy": "marth_d18_vs_fox_v3.1"` (a slippi-ai
  model; run with `~/Games/Melee/slippi-ai/venv/bin/python`). The player is whoever is being
  trained; in a test it is a stand-in script.
- `success` is judged from the player's side after the scripts end and `after` more frames.
- Character and stage names: `tools/melee_native/native.py`.

## Vocabulary (tools/melee_actor/actor.py)

| Step | Does |
|-|-|
| `approach` `range` `tolerance` | get that close to the target, standing; stops at the stage's edge |
| `face` | turn toward the target |
| `attack` `move` | `jab ftilt utilt dtilt fsmash usmash dsmash grab neutral_b side_b up_b down_b jump`, then wait until able to act |
| `rush` `move` | run at the target and do `grab`, `dash_attack` or `usmash` (jump cancelled) out of the run, started at the distance known to connect for this character (`data/actor/reach.json`); the fast way in |
| `throw` `direction` | `up down forward back`, after a grab that connected |
| `wait` `frames` or `until` | `target_grounded`, `target_airborne`, `target_idle`, `target_attacking`, `target_swung` (its hitbox came out and went), `target_frame:N`, `in_range:N` |
| `hold` `frames` `buttons` `stick` | hold an input (shield, crouch) |
| `{"expect": ...}` inside a script | `target_hit`, `target_not_hit`, `hit`, `not_hit`, `in_range:N` |

Scripts say what is to be achieved, never which frame. If a script needs a frame number
to work, the step or condition it lacks is the thing to write: a generator method `do_x`
on `Actor` that yields one pad per frame, or a branch in `_condition`, with a scenario that
shows it. `approach` is for standing somewhere exactly and is slow (it walks the last 18
units); to hit someone in time use `rush`. There is no jump-in, aerial, dash dance,
wavedash or step that is interrupted by being attacked yet; an opponent "shields when it
can" by a `hold` with R after its attack.

A number the actor needs about a character (how far out a move connects) is measured, not
guessed: `python tools/melee_actor/calibrate.py [character]` tries every distance on the
native build (all 26 characters in under a minute) and writes `data/actor/reach.json`.

## From Python

```python
import sys; sys.path.insert(0, "tools")
from melee_actor import scenario
with scenario.Session(scenario.load("tests/actor/scenarios/whiff_punish.json")) as s:
    results = [s.run(jitter=3.0, run=i) for i in range(50)]   # same run number, same game
```

`Session` sets the match up once and restores a snapshot for every run. Always close it
(`with`): snapshots are processes (`docs/ai/native-ai.md`).

## Reporting

Say how many runs of how many passed and with what jitter, and quote the failing check of
a failed run. A scenario that only passes unjittered is not a result.
