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
| Scenarios: a situation, an opponent's script or policy, a stand-in player, what counts as success; many runs from one set-up, each moved about | `tools/melee_actor/scenario.py`, `run.py` | `tests/actor/scenarios.py`, 8 checks: one situation played three ways (below) |
| What a character's running moves reach, measured by trying | `tools/melee_actor/calibrate.py` → `data/actor/reach.json` | used by the scenarios above |
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
controller. Until it does, everything here is developed and checked with a stand-in for
the player: an actor script or a policy.

### The window: the graphics stack builds and runs 32-bit (probe, 2026-11-13)

Aurora (`build/deps/aurora`) draws GX through Dawn (WebGPU) and opens its window with
SDL3. Its prebuilt Dawn exists for 64-bit Linux only, and the game is a 32-bit process.
A time-boxed probe built all three from source as 32-bit x86:

```sh
tools/aurora32/build.sh        # -> build/aurora32/build; first time fetches Dawn and SDL3
```

| | |
|-|-|
| Builds | Aurora (unmodified), Dawn at Aurora's pinned revision, SDL 3.4.10: about 2.5 minutes at `-j 10`, 1.8 GB of build tree |
| Changes needed | One line of Dawn (`tools/aurora32/dawn-0001-vk-null-handle-32bit.patch`: on 32-bit a raw Vulkan handle is a `uint64_t` and Dawn's `VK_NULL_HANDLE` a `nullptr_t`), and `-DDAWN_USE_GLFW=OFF` (GLFW wants a 32-bit `xkbcommon`, which is not installed) |
| Runs | A 32-bit program (`build/aurora32/probe/dawn32_probe vulkan --render`) creates a WebGPU device on Vulkan with this machine's GPU through the 32-bit NVIDIA driver, with no window and no surface, draws a triangle into a texture and reads back the right pixels. Rerun by hand after the probe: same result |
| Aurora itself | Its example initialises and runs its frame loop under a virtual X server (`xvfb-run`, SDL's x11 driver). With SDL's `offscreen` or `dummy` driver it stops: Aurora only makes a surface from an X11 or Wayland window |
| Nothing had to be installed | The 32-bit Mesa, Vulkan loader and X11 that were there are enough. Would help: `lib32-libxkbcommon lib32-libdecor` (a Wayland driver in SDL3), `lib32-libxcursor lib32-libxi lib32-libxrandr` (X11 extensions SDL3 loads), `lib32-vulkan-swrast` (software Vulkan, for tests off the GPU) |

Not shown by the probe, and the work N6 now consists of:

- **Anything from the game drawn.** Aurora's GX was not exercised (the example only clears
  the screen), and nothing of this is linked into `melee_headless`. Linking means dropping
  the host layer's own GX, VI and PAD stand-ins where Aurora has the real thing, driving
  Aurora's frame from the game's, and finding out whether the game's fixed-address arena
  and a GPU driver fit in one 32-bit address space.
- **The game's draw pass.** `--draw` asserts in the first frame even into no-op graphics.
- **A frame presented.** Screenshots of the virtual X server during the example were
  black; not looked into.
- A window on the real display, sound, a controller. Nothing was run on the owner's
  screen.
- `build.sh` from an empty tree (it was run on the probe's tree).

The first target for N6 is a frame of a match drawn off screen and read back to a picture:
it needs no window, so it can be checked without anything appearing on the desktop.

Where a person can train **today** is still the overlay build on Dolphin
(`training-courses.md`).

## Plan

| Step | What | Proof |
|-|-|-|
| N1 (done) | The interface above; actor and policies on it | the three tests |
| N2 (placement done) | Setting up a situation from a command instead of from play. `Native.place(port, x, y, facing, air, percent)`: standing on whatever floor is at or below the point, or falling from it; not holding or held, no speed, a full shield (`src/host/setup.c`, the course engine's placement on the game's own functions). Stocks, items and the rest of a match's rules: not yet | `tests/native/place.py`, 11 checks |
| N3 (begun) | The actor's step library (`melee-actor.md`, A2). Done: steps are generators, so two scripts run at once; scenario files and a runner with a verdict as JSON; the conditions `target_attacking`, `target_swung`, `target_idle`, `target_frame`; `rush` (running grab, dash attack, jump-cancelled up smash, at measured distances), `throw`, `shield` (until it has blocked) and `oos` (shield grab, up smash, jump out of shield); `choose`, so an opponent varies what it does from run to run. Not done: jumps and aerials, dash dance, wavedash, a step interrupted by being attacked, branching on what happened | one scenario per step |
| N4 (begun) | A trainer process: scenarios run against a stand-in player, retried from a snapshot, scored. Done: `scenario.Session`, one situation in two versions. Not done: scenarios from `data/courses/`, a session of several, keeping score over time | two scenarios from `data/courses/` run end to end, headless |
| N5 (written, never run against the API) | Claude in the loop: turns an instruction into a scenario, runs it, reads the verdicts, revises (`ai-coach.md` for the coaching side). Never in the frame loop. `tools/melee_actor/author.py`, below | an instruction in words becomes a scenario that passes: **not shown**, no credentials on this machine |
| N6 (probe done: the graphics stack builds and runs 32-bit) | A window, sound and a controller. First: link Aurora in and draw one frame of a match off screen | a picture of a match from the native build; then a person plays one |
| N7 | The trainer with a person in it: feedback on screen | the owner trains against an actor |

N6 is the largest unknown and gates N7. N2 to N5 do not wait for it.

## The first drill-shaped thing: one situation, three ways to play it

`tests/actor/scenarios/`: Marth forward smashes from 42 units away and holds his shield
from the first frame he can. The player is a stand-in script.

| File | The player | What happens | 40 runs, each moved by up to 2 units |
|-|-|-|-|
| `whiff_punish.json` | waits until the hitbox has come out and gone (`target_swung`: 54 frames in, found from the game, not counted), runs in, grabs out of the run, throws up | holding Marth at frame 77; he could have shielded from frame 90 | 40 pass |
| `too_slow.json` | the same wait, then stops next to him and up smashes | the up smash starts at frame 105 and meets a shield: no damage | 40 "fail" as a drill should score it |
| `too_early.json` | goes when the swing starts | runs into the sword | 40 hit |

- Moved by up to 8 units, 36 of 40 punishes still pass. In the other four the two started
  within about 35 units, where the tip of the sword reaches: not a whiff any more. The
  runner found that; nobody looked it up.
- The fast way in needed a number nobody had: a running grab slides a long way before its
  grab box is out, so started too close it ends up behind the target. `calibrate.py` tries
  every starting distance for the running grab, dash attack and jump-cancelled up smash of
  every character against a standing Marth (26 characters in 44 s) and writes
  `data/actor/reach.json`. For Fox the grab connects when started 15 to 38 units out; the
  actor starts it at 26.5.
- After the smash the opponent now does one of three things, chosen per run: shields,
  jabs, or rolls away. The punish passes 60 of 60: done in time, it does not matter which.
- A trained policy can be the opponent of a scenario (`"policy": "marth_d18_vs_fox_v3.1"`,
  run with slippi-ai's Python). Tried once, to see that it runs: it does, but the policy
  has not started playing in its first frames (its inputs are 18 frames behind), so what
  that run scored means nothing. A scenario against a policy needs a warm-up first.
- What this is not yet: a drill. Nothing explains, scores over time or adapts; the player
  is a script.

A second situation was written the way `author.py` is meant to work, but by hand, from the
instruction "shield Marth's dash attack and grab him out of shield":
`data/scenarios/shield-grab-dash-attack.json`. It needed two steps the actor did not have
(`shield` until blocked, `oos`), which is the intended way for the vocabulary to grow. The
knowledge base says the dash attack is -20 on Fox's shield and a shield grab takes 7
frames; in the game the stand-in blocks, grabs and throws in 40 of 40 runs moved by up to 3
units, and without the shield the dash attack hits.

## Claude writing scenarios (`tools/melee_actor/author.py`)

```sh
.venv/bin/pip install anthropic            # once
export ANTHROPIC_API_KEY=...               # or `ant auth login`
python tools/melee_actor/author.py "Marth dash attacks from mid range. \
    I want to practise shielding it and grabbing him out of shield."
python tools/melee_actor/author.py --show-prompt
```

Claude (`claude-opus-5-5` by default, `--model` to change) is told what a scenario is, what
makes one good (works when moved about, fair, tells right from wrong, no frame numbers where
a condition would do) and the actor's vocabulary, which is generated from `actor.py` so the
prompt cannot drift from what runs. It has three tools:

| Tool | Does |
|-|-|
| `run_scenario(scenario, runs, jitter)` | runs it on the native build; answers with how many runs passed and the steps and checks of one failing and one passing run |
| `game_data(query)` | `tools/melee_data/query.py`: frame data, out-of-shield options, shield advantage, knockback |
| `save_scenario(name, scenario)` | writes `data/scenarios/<name>.json`; refuses unless that exact scenario passed 90% of a run of 10 or more |

The loop is the SDK's tool runner. A safety decline is rerun on a fallback model by the API
(`fallbacks: "default"`).

**What is checked:** the three tools, the save rule and the tool definitions the SDK builds,
without any API call (`tests/actor/author_tools.py`, 11 checks); with no credentials the
command says so and stops. **What is not:** the conversation itself. Nobody has seen
Claude write a scenario through this yet, so the prompt is a first draft.

## Not verified

- Anything here on an optimised build. `--opt 1` is faster (`native-port.md`) and was not
  rerun with the new protocol.
- Snapshots under memory pressure, or hundreds of them at once. Each keeps the pages the
  game has since changed; the table holds 256.
- That the policies play as well here as in Dolphin. They fight (in the 1,800 frame run
  Marth kept Fox in the air for long stretches); nobody compared.
- More than two fighters, CPU players, stages other than the six tournament ones.
