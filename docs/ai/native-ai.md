# AI on the native build

Direction set by the owner on 2026-11-13: "we want to focus on the native linux build
because we want to build in direct AI integration and the actor system to build AI-driven
training." The native build (`native-port.md`) is an ordinary Linux process: nothing in it
has a GameCube's 24 MB or its 486 MHz, which is what kept a real model out of the game
(`melee-actor.md`, "Can an instructable model run inside the game?").

This file is the plan and its status. What exists is under "What runs today"; the rest is
not built.

## The shape

```
 game: build/native/melee_headless        the deciding side: Python, 64-bit
 ┌───────────────────────────────┐  pipe  ┌──────────────────────────────────────┐
 │ the vanilla game, 32-bit      │◀──────▶│ tools/melee_native/native.py (Native) │
 │ src/host/control.c            │  one   │  ├ Melee Actor: scripts of intentions │
 │  pads in, a frame's state out │  line  │  ├ slippi-ai policies                 │
 │  snapshots (forks)            │  each  │  └ later: the trainer, Claude         │
 └───────────────────────────────┘  way   └──────────────────────────────────────┘
```

- **The game cannot be loaded into Python.** It is built 32-bit (the game's code assumes
  4-byte pointers) and Python is 64-bit. So everything that decides inputs lives in another
  process and talks over the control protocol. That costs little: a frame with its state is
  one line each way, about 110 microseconds including the Python side.
- **Nothing that decides is in the frame loop of a playable game yet**, because there is
  no playable game: the native build draws nothing (see "The gap").
- A C twin of the actor inside the game, which the overlay build would need
  (`melee-actor.md`), is **not needed here**: two full-size policies already run faster than
  real time beside the game.

## What runs today (2026-11-13)

| Piece | Where | Checked by |
|-|-|-|
| A frame per exchange: `tick` sets the pads, runs frames, returns the state (both fighters: state, frame, position, speed, facing, airborne, damage, hitlag, hitstun, shield, kind, jumps used, invulnerable, stocks; items; the random seed) | `src/host/control.c`, `Native.step` | `tests/native/env.py` |
| Snapshots: `Native.snapshot()` / `restore()` / `drop()` | `control.c` (below) | `tests/native/env.py`: the same inputs from a snapshot give the same game, in any order of restores, and the same as a fresh process |
| The Melee Actor, unchanged, on either the native build or the simulator | `tools/melee_actor/actor.py` | `tests/actor/uptilt.py` (4 of 4 on both) |
| slippi-ai policies as players, on either | `tools/melee_actor/policy.py` | `tests/actor/policy_match.py` |

Measured on this machine, unoptimised build (`-O0`):

| | Native | Python simulator |
|-|-|-|
| A match up and both fighters standing, from nothing | 0.35 s | several seconds, or a cached state |
| Frames a second, a full state read back each frame | about 8,900 | 50 to 160 |
| The actor's four up tilt situations (785 frames) | 0.11 s | 7.3 s |
| Two policies playing each other, 1,800 frames | 12.4 s (146 a second; the game is 0.4 s of it) | game-bound |
| Snapshot / restore | 0.4 ms / 0.8 ms | a copy of the whole memory |

`Native` has the simulator's interface where the two overlap (`pad`, `step`, `fighter`,
`snapshot`, `restore`), which is why the actor and the policy bridge needed no changes to
their logic. `Native.start(p1, p2, stage)` boots, starts a VS match with both pads ours
and waits until both fighters stand.

**What the native build is not, still:** the vanilla game only. No overlay, no TM-CE, no
course engine, no UCF (`ucf.md`), no drills. Where the simulator's Lab and the native VS
match were given the same script, three of four runs ended within a frame of each other
and with the same positions; one differed in where the target ended up. Not looked into.

## Snapshots are forks

`snap` forks the game. The child goes to sleep holding everything as it was: the arena,
the statics, the host layer's own heap (converted archives), audio RAM. It shares memory
with the running game until either writes to a page. `restore` wakes the sleeper, which
forks a copy of itself to take over stdin and stdout, and the process that asked exits; the
sleeper stays, so a snapshot can be restored any number of times.

- No game code had to change, and nothing can be missed: it is the whole address space.
  (`netplay-p2p.md` lists the in-process alternative, which needs the host's allocations
  moved into one region first. Rollback netcode will want that one; experiments do not.)
- Which process is "the game" changes at every restore. The table of sleepers is in memory
  shared by all of them. `Native` starts the game in its own process group and kills the
  group on `close()`; sleepers also leave by themselves when stdin closes. A leaked
  emulator took this machine down once (2026-11-11), so the test checks that nothing is
  left running.
- Commands are read with `read()`, not stdio, and one at a time: a process started from a
  snapshot must not find bytes in a buffer that another process already acted on.
- With sleepers holding stdout open, a crashed game no longer shows as end of input. A
  fatal error prints `@ fatal`; `Native` also gives up after `timeout` seconds of silence.

## The gap: nobody can play it

AI-driven training has a person in it. The native build has no graphics, no sound and no
controller: `--draw` asserts in the first frame, and Aurora, the library upstream uses for
graphics, has never been built for 32-bit Linux here (`native-port.md`). Until that
exists, everything below is developed and checked with a stand-in for the player: an actor
script or a policy.

Where a person can train **today** is still the overlay build on Dolphin
(`training-courses.md`).

## Plan

| Step | What | Proof |
|-|-|-|
| N1 (done) | The interface above; actor and policies on it | the three tests |
| N2 | Setting up a situation: place a fighter (position, facing, damage, on the ground or in the air), choose stocks and items off, from a command instead of from play | a situation set up twice is the same game twice; against the simulator's Lab placement |
| N3 | The actor's step library (`melee-actor.md`, A2) and "react when", developed here at 8,900 frames a second; script files and a runner with a verdict as JSON (A3) | one test per step; a drill's player-side test rewritten as a script |
| N4 | A trainer process: a scenario (setup, the opponent's script or policy, what counts as success), run against a stand-in player, retried from a snapshot, scored | two scenarios from `data/courses/` run end to end, headless |
| N5 | Claude in the loop: turns an instruction into a scenario or a script, reads the verdicts, revises (`ai-coach.md` for the coaching side). Never in the frame loop | an instruction in words becomes a script that passes |
| N6 | A window, sound and a controller | a person plays a match |
| N7 | The trainer with a person in it: feedback on screen | the owner trains against an actor |

N6 is the largest unknown and gates N7. N2 to N5 do not wait for it.

## Not verified

- Anything here on an optimised build. `--opt 1` is faster (`native-port.md`) and was not
  rerun with the new protocol.
- Snapshots under memory pressure, or hundreds of them at once. Each keeps the pages the
  game has since changed; the table holds 256.
- That the policies play as well here as in Dolphin. They fight (in the 1,800 frame run
  Marth kept Fox in the air for long stretches); nobody compared.
- More than two fighters, CPU players, stages other than the six tournament ones.
