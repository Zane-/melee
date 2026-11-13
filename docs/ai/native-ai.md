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
| Placing fighters: `Native.place()` | `src/host/setup.c` | `tests/native/place.py`: on Final Destination and on Battlefield's platforms, in the air, refused where there is no floor |
| Snapshots: `Native.snapshot()` / `restore()` / `drop()` | `control.c` (below) | `tests/native/env.py`: the same inputs from a snapshot give the same game, in any order of restores, and the same as a fresh process |
| Scenarios: a situation, an opponent's script or policy, a stand-in player, what counts as success; many runs from one set-up, each moved about | `tools/melee_actor/scenario.py`, `run.py` | `tests/actor/scenarios.py`: a whiff punish that waits for the swing to be spent (40 of 40 runs moved by up to 2 units, 0.9 s), and the same situation entered too early, which gets the player hit |
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

**Placing and repeating.** A placement makes the fighters the same whatever came before.
It does not touch what else is about: effects still playing, and so where the random
stream stands a few frames later. To repeat a situation exactly, set it up once, take a
snapshot and restore that; the test checks both halves of this.

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

What a window would take, as far as a first look goes (2026-11-13, nothing built):

- Aurora (`build/deps/aurora`, the full source) draws GX through Dawn (WebGPU) and opens
  its window with SDL3. Its prebuilt Dawn exists for 64-bit Linux only, so for this
  32-bit game Dawn has to be built from source, which is a large build nobody here has
  tried.
- This machine has 32-bit Mesa and the 32-bit Vulkan loader. `lib32-sdl3` is in the
  distribution's repositories and not installed (`sudo pacman -S lib32-sdl3`).
- The other ways round the 32-bit problem are each a project: draw in a second, 64-bit
  process that the game sends its graphics commands to, or make the game itself build
  64-bit.

Where a person can train **today** is still the overlay build on Dolphin
(`training-courses.md`).

## Plan

| Step | What | Proof |
|-|-|-|
| N1 (done) | The interface above; actor and policies on it | the three tests |
| N2 (placement done) | Setting up a situation from a command instead of from play. `Native.place(port, x, y, facing, air, percent)`: standing on whatever floor is at or below the point, or falling from it; not holding or held, no speed, a full shield (`src/host/setup.c`, the course engine's placement on the game's own functions). Stocks, items and the rest of a match's rules: not yet | `tests/native/place.py`, 11 checks |
| N3 (begun) | The actor's step library (`melee-actor.md`, A2). Done: steps are generators, so two scripts run at once; scenario files and a runner with a verdict as JSON; the conditions `target_attacking`, `target_swung`, `target_idle`, `target_frame`. Not done: every step beyond approach, face, attack, wait, hold (shield, jumps and aerials, dash dance, wavedash, reacting to being attacked, branches) | one scenario per step |
| N4 (begun) | A trainer process: scenarios run against a stand-in player, retried from a snapshot, scored. Done: `scenario.Session`, one situation in two versions. Not done: scenarios from `data/courses/`, a session of several, keeping score over time | two scenarios from `data/courses/` run end to end, headless |
| N5 | Claude in the loop: turns an instruction into a scenario or a script, reads the verdicts, revises (`ai-coach.md` for the coaching side). Never in the frame loop | an instruction in words becomes a script that passes |
| N6 | A window, sound and a controller | a person plays a match |
| N7 | The trainer with a person in it: feedback on screen | the owner trains against an actor |

N6 is the largest unknown and gates N7. N2 to N5 do not wait for it.

## What the first scenario shows, and does not

`tests/actor/scenarios/whiff_punish.json`: Marth forward smashes from 42 units away, the
stand-in Fox waits until the hitbox has come out and gone (`target_swung`: 54 frames in,
found from the game, not counted), runs in and up smashes. `too_early.json` is the same
with the wait ending when the swing starts: Fox runs into the sword.

- Moved by up to 8 units either way, 36 of 40 runs still pass. In the other four the two
  started within about 35 units, where the tip of the sword reaches: the situation was not
  a whiff any more. The runner found that; nobody looked it up.
- **It is not yet a fair punish.** The stand-in's up smash lands 70 frames after the smash
  began; Marth could act again after about 47. It lands because the opponent's script has
  nothing after the smash. `approach` walks its last 18 units, which is most of the delay.
  A drill needs an opponent that shields or moves when it can, and steps fast enough to
  beat it. That is what N3 is for.

## Not verified

- Anything here on an optimised build. `--opt 1` is faster (`native-port.md`) and was not
  rerun with the new protocol.
- Snapshots under memory pressure, or hundreds of them at once. Each keeps the pages the
  game has since changed; the table holds 256.
- That the policies play as well here as in Dolphin. They fight (in the 1,800 frame run
  Marth kept Fox in the air for long stretches); nobody compared.
- More than two fighters, CPU players, stages other than the six tournament ones.
