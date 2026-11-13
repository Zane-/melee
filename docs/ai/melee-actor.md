# Melee Actor: scripts carried out from the live game state

Decided 2026-11-12, after the owner's first play of the Fox course: the drills work, but a
CPU that presses buttons on fixed frames feels rigid, and every new scenario costs a round
of frame tuning. The **Melee Actor** is the layer between "what the CPU should do" and the
controller: it takes a script of intentions and decides each frame's inputs from where the
fighters actually are. The same layer lets an agent test things by instruction ("up tilt
the player") instead of by frame.

This file is the research and the design. Status: a reference implementation and a proof
exist (`tools/melee_actor/actor.py`, `tests/actor/uptilt.py`), and trained slippi-ai
policies play (`tools/melee_actor/policy.py`, `tests/actor/policy_match.py`), on the native
build and on the simulator alike. Nothing is in a game a person can play yet.

## What it is

A script is a list of steps. Steps say what is to be achieved, never which frame:

```python
[
    {"do": "approach", "range": 9, "tolerance": 4},   # get next to the target
    {"do": "wait", "until": "target_grounded"},
    {"do": "face"},
    {"do": "attack", "move": "utilt"},
    {"expect": "target_hit"},                          # the test's verdict
]
```

Each step is a small closed loop: `approach` runs while far away, walks the last stretch,
backs off if too close, stops at the stage's edge, and is done when the distance is in the
band and the fighter is standing. `attack` knows how each move is input (a tilt needs the
stick resting off-centre first, or it is a smash). `expect` turns a run into a test.

**Proof (simulator, 2026-11-12).** `python tests/sim/actor_uptilt.py`: the script above,
with Marth as the actor and Fox as the target, in four situations: Fox stands still, walks
away first, runs past the actor to the other side of the stage, keeps full hopping. The up
tilt lands in all four, on frames 126 to 187 depending on what Fox did. No frame or
position appears in the script. What went wrong on the way is the kind of knowledge the
actor now owns so that scripts do not have to: stick and A on the same frame is an up
smash; a stick at 0.55 for a few frames is a jump; chasing a target that ran off the stage
killed the actor until it was given the stage's width.

## Where it runs

| Runtime | State | For |
|-|-|-|
| Python on the native build (`tools/melee_actor/` with `tools/melee_native/native.py`), since 2026-11-13 | the same code as the next row, about 70 times faster; **where steps are developed now** (`native-ai.md`). Vanilla game only: no Lab, no drills | developing steps; agent-run tests in a fraction of a second; policies as players |
| Python on the simulator (`tools/melee_actor/`) | reference implementation: 5 steps, 3 expectations; a trained policy can be the other fighter | developing steps; agent-run tests in seconds; the player's side of a drill test |
| C in the overlay, inside the course engine | **not built** | the CPU in drills, on console and Slippi with nothing running beside the game |
| Python beside Dolphin, through libmelee | **not built** | the only place a learned policy can run live |

The drills already contain hand-written fragments of an actor, each tuned separately:
the chasing Sheik and Marth (`tc_Think`, `ec_Chase`), the pressure loop (`ep_Cpu`), the
recovering Marth (`os_CpuRecover`), the reacting whiff-punish CPU, the grab-and-throw
(`tg_Advance`). The C twin replaces those and `course_Script` with one interpreter: a
drill's CPU becomes a table of steps (the same vocabulary as the Python scripts), the
engine runs one step function per frame. Mutable actor state goes where the engine's does
(heap under `tm_state` if it is ever to run in netplay; see `CLAUDE.md`).

Keeping the two runtimes honest: the step vocabulary and parameters are the contract; a
script that passes on the simulator in Python is then run through the C interpreter in the
same simulator (the overlay is the same DOL), and the two traces are compared.

## The agent loop

```
instruction ──► script (steps + expectations) ──► run on the simulator ──► verdict + trace
     ▲                                                                         │
     └──────────────────── revise the script or the step ◄─────────────────────┘
```

- The instruction is language ("bait Marth's forward smash and grab him"); turning it
  into a script is the agent's job, with `data/` for the numbers (reach, frame data).
- A run takes seconds (`Sim.snapshot` / `restore`), so the agent can try variants and
  situations instead of reasoning about one frame-perfect line.
- **Both sides can be actors.** A drill test today scripts the player's inputs by frame
  (`tests/tmtest/course/*`: "X at 64, C-stick at 72"); most of the tuning time in the
  course went there. With an actor as the player, the test says "dash under them, jump,
  up air" and survives a change to the drill's spacing or timing.
- What a step cannot do yet is the backlog: when a script needs "wavedash back" and the
  step does not exist, that step is written once, with its own test, and every later
  script has it.

## slippi-ai (Phillip II): what it is and how it could plug in

Source read 2026-11-12: `github.com/vladfi1/slippi-ai` at its commit of 2026-10-20
(`README.md`, `ARCHITECTURE.md`, `slippi_ai/types.py`, `onnx_policies.py`, `dolphin.py`,
`eval_lib.py`, `sim_env/env.py`, `setup.cfg`), and `altf4/libmelee` (`melee/console.py`).

**Facts**

- Imitation learning on Slippi replays, then self-play reinforcement learning; MIT
  licence. Plays like a strong human, and has played top players (links in its README).
- **Trained models are published**: a Google Drive folder linked from the README, and
  ONNX exports that its Windows app downloads. `onnx_policies.py` runs an exported policy
  "with onnxruntime, without jax or tensorflow".
- **Input** per frame (`types.Game`): for each of two players: percent, facing, x, y,
  action state, invulnerable, character, jumps left, shield strength, on ground, and the
  controller; plus stage, Randall, Fountain platforms and up to 15 items. Also a player
  **name** and a **rating** the policy is conditioned on. Everything in that list is in
  our fighter structs, and its action ids are the game's own action state ids.
- **Output**: a controller (two sticks, shoulder, buttons), sampled.
- **Delay**: the policy acts on a delayed view of the game; the README gives 18 frames or
  more for the netplay bot. The delay is part of the trained policy (`policy_config`).
- **How it reaches the game**: through libmelee. libmelee starts Slippi Dolphin, reads
  the game state from Slippi's broadcast stream (UDP port 51441), sends inputs through
  Dolphin's named-pipe controllers, and by default **overwrites the user's
  `GALE01r2.ini` Gecko codes with its own**. Python 3.12 or later, `melee>=0.47.6`.
- It can also train and run on a batched decomp-based simulator (`slippi_ai/sim_env`,
  the `melee_sim` package by "Enzyme" credited in the README). That package is not in the
  repository's requirements; where it comes from was not established. It shares a name
  with our `tools/melee_sim` and is unrelated.
- Its README asks that bots not be run on Slippi's ranked or unranked ladders.

**What it is not.** It is not instructable. The policy is conditioned on a name and a
rating, not on a goal: it cannot be told "up tilt" or "only approach with aerials". It
plays a whole game its own way, 18 frames behind. So it does not replace the actor; it is
a source of realistic play around the parts the actor scripts.

**Where it can run**

| Option | What it takes | Assessment |
|-|-|-|
| A. In our simulator, headless | `onnxruntime` and a model file; a function that fills `types.Game` from simulator memory each frame and writes the decoded controller to `Sim.pad` | The cheapest real experiment. No Dolphin, no Slippi, deterministic given a seed. Unknown until tried: the exact unit conventions of a few fields (shield strength, invulnerable, items), and inference speed without a GPU |
| B. Live, beside Dolphin, through libmelee | Slippi Dolphin running our overlay build; port 2 as a pipe controller instead of a CPU; libmelee seeing our event matches as "in game" | The only way a person plays against it. Three unknowns, none checked: whether Slippi broadcasts frames during a TM-CE event match; whether libmelee's Gecko codes collide with our hooks (the same question `tools/tm_slippi_collisions.py` answers for Slippi's own); how its menu handling copes with a build that boots into our hub |
| C. Inside the game | - | Not possible: a neural policy does not fit a GameCube's 24 MB and CPU |

**Option A, tried (2026-11-12).** The owner already had a slippi-ai checkout with its JAX
environment and 137 trained checkpoints (`~/Games/Melee/slippi-ai`, commit of 2026-09-23;
`deployed_models/`: per-matchup policies such as `fox_d18_vs_marth_v3.1`, `d18` / `d21` =
frames of delay). `tools/melee_actor/policy.py` fills `types.Game` from simulator memory,
steps the checkpoint through slippi-ai's own `build_delayed_agent`, and writes the decoded
controller to `Sim.pad`. Nothing was installed: the script runs under slippi-ai's
interpreter and adds the project's packages to the path (both are Python 3.14).

- `tests/sim/policy_match.py`: Fox and Marth, each a policy, on Final Destination. It
  worked on the first run. Over 3600 frames each took a stock; Fox used 67 different
  action states and Marth 59; there are grabs and throws, wavedashes, a ledge hang with
  Marth recovering under it. 46 frames per second with both policies on the GPU (an RTX
  3090), against about 100 for the simulator alone.
- `tests/sim/actor_vs_policy.py`: the "up tilt the target" script of the proof above
  against that Fox, five tries. **0 of 5.** Marth walks up, stops, turns and swings at a
  Fox that is no longer there, and takes up to 47% doing it. This is the point of having
  the policy: a script that passes against stand-ins says little about a real opponent.

What the bridge leaves out, so far without visible harm: projectiles and items are not
passed to the policy (it does not see lasers); jumps left assumes two for everyone but
Kirby and Jigglypuff; only Final Destination's stage number has been used; Nana is always
absent.

**Recommendation.** Build the actor first: it is what makes scenarios less rigid, it is
instructable, deterministic, and runs in the game itself. Then try option A as an
experiment, as one more step type, `{"do": "play", "policy": "...", "until": ...}`: the
policy plays neutral until a condition the script names, then scripted steps take over (or
the other way round: the actor creates the situation, the policy answers it the way a
person would). Option B comes last, and only if A shows the policy is worth having in
front of the player; it also brings a second process and a dependency on the user's
Dolphin configuration, which the overlay build has so far avoided.

For the "realistic neutral" complaint specifically, SmashBot (`altf4/SmashBot`, same
libmelee) is the other reference: a hand-written hierarchy of strategies, tactics and
chains (`Chains/`: wavedash, shffl, edgedash, tech, sdi, grabandthrow...). It is the same
idea as actor steps, one level up, and its chain list is a good checklist for ours.

## Can an instructable model run inside the game?

Asked by the owner 2026-11-12. Short answer: not a model like Phillip, but a small learned
"director" over actor steps can, and that is where the intelligence should go.

**Measured** (two of the owner's checkpoints, loaded with slippi-ai's own code):

| Checkpoint | Network | Parameters | As 32-bit floats |
|-|-|-|-|
| `fox_d18_vs_marth_v3.1` | 3 layers, hidden 512, LSTM | 10.5 million | 42 MB |
| `fox_d21_ditto_v6.1` | 3 layers, hidden 1024, LSTM | 44.7 million | 179 MB |

A GameCube has 24 MB of main memory in all, and the game uses most of it. One step of the
smaller network is on the order of 10 to 20 million multiply-adds, sixty times a second,
on a 486 MHz CPU that is already running Melee. Neither fits, by two to three orders of
magnitude. Slippi Dolphin emulates that CPU at its real speed, so playing on an emulator
does not change this. And these policies are not instructable in the first place.

**What does fit.** An estimate, not a measurement: if a millisecond per frame can be spared
and the CPU manages some tens of millions of multiply-adds per second in practice, the
budget is roughly 50 to 100 thousand parameters evaluated every frame, a few hundred
thousand if a decision is only needed every several frames. That is too small to drive a
controller frame by frame at a high level, which is what Phillip's ten million are for.
It is plenty for choosing between a few dozen competent behaviours.

**So the split is:**

- **Execution is the Melee Actor's steps, in C.** Exact, free, already native in spirit
  (the drills contain hand-written ones). A step is "wavedash back", "shine out of
  shield", "up tilt when in range", not a stick position.
- **Decisions are a small network over those steps.** Input: the same few dozen numbers
  slippi-ai reads, plus a goal. Output: which step next, with its parameters. Tens of
  thousands of parameters.
- **Instruction is the goal input,** a structured code ("prefer grabs", "recover low",
  "punish whiffs with up smash", "play at 12 frames of reaction"), not language. Language
  is turned into goals and scripts before the match, by a person in a menu or by Claude
  through the coach link (`ai-coach.md`); nothing in the game parses text.

**Where the intelligence would come from.** Three sources this project now has: Slippi
replays relabelled in step vocabulary, where what the player did next becomes the goal
that clip teaches (hindsight labelling); the slippi-ai policies in the simulator, as
teachers to imitate at step level and as opponents to train against; and the simulator
itself for reinforcement learning toward an instructed goal, where a decision every 10 to
20 frames makes its speed (about 100 frames a second per process) tolerable.

**Risks, in the order they should be retired.** (1) The real per-frame budget on the
emulated CPU is unknown: measure it with a matrix-multiply benchmark in the overlay under
Dolphin before choosing a size. (2) Whether a step-level student of a few tens of
thousands of parameters plays convincingly is unproven; the cheap test is to train one to
predict Phillip's next step from simulator games and see how often it agrees. (3) The
step library has to be good first: a director can only be as good as its steps, and the
naive ones just went 0 for 5.

## Roadmap

| Step | What | Proof |
|-|-|-|
| A1 (done) | Reference actor on the simulator: approach, face, attack, wait, hold; expectations | `tests/sim/actor_uptilt.py`, 4 of 4 |
| A2 | Step library: dash dance, wavedash, short hop aerial with L-cancel, shield and out-of-shield, grab and throw, tech and DI answers, "react when" (a condition that interrupts the current step), branches | one simulator test per step |
| A3 | Script files and a runner (`tests/actor/*.json`, both sides scripted, expectations), a CLI, and a skill for writing them | a drill's player-side tests rewritten as actor scripts |
| A4 | The C interpreter in the course engine; convert the first drills (whiff punish, tech chase, edgeguard) | same scripts, same simulator, Python and C traces agree; Dolphin once |
| A5 (bridge done) | slippi-ai in the simulator (option A): the bridge exists; a `play` step in scripts does not | `tests/sim/policy_match.py` (two policies play a minute); `tests/sim/actor_vs_policy.py` (the naive up tilt script: 0 of 5) |
| A6 | Live bridge (option B) | a person plays a round against it in our build |

## Not verified

- slippi-ai live in Dolphin (option B): only the simulator bridge has been run.
- That the policies play as well in our simulator as in Dolphin. They fight and take
  stocks; nobody has compared the two, and the bridge omits projectiles.
- That Slippi Dolphin broadcasts frame data during our event matches (option B).
- That libmelee's Gecko codes are compatible with the overlay's hooks.
- The actor on any stage but Final Destination, with any actor but Marth, and against a
  target that fights back. `STAGE_LIMIT` values other than Final Destination's are
  estimates.
