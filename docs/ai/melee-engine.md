# A chess engine for Melee: the opponent that thinks

The owner, 2026-11-13, after playing the first reactive drills: "It's slightly better, but
not super super good. I feel like we need MORE intelligence." What bothered them: "the
robotic movement, no variance, missing attacks, fixed timings, etc. This is not the way to
train and get better, we need to make essentially a chess engine but for melee." They
pointed at 4Stockfish (below) and asked for all of the directions in "The plan".

This file is the design and its status. What exists so far is marked; the rest is not
built.

## Why the reactive opponent is not enough

The reactive opponent (`melee-actor.md`, "Attacks that land") only decides *when* to start
its one designed attack. Everything else is scripted:

| Layer | Today | What a strong human has |
|-|-|-|
| Body | walks to a spot, stops, taps, attacks | dash dances, wavedashes, spacing, feints |
| Decisions | one attack per drill, fixed | options, mixups, follow-ups, adaptation |
| Model of you | "you keep holding what you hold" | expects what people do: shield, dash back, jump |
| Thinking time in a live match | one lookahead a frame, inside the frame you see | as much as it needs |

## 4Stockfish: what it is, what we take from it

`github.com/noahpodgurski/4Stockfish` (read 2026-11-13 at its commit of 2026-11-07,
`src/pc/sf_search.c` and `sf_search.h`, README, ROADMAP). A "chess engine" for Melee built on
the melee-pc port: pausing a match searches ahead by running the real game tick on
whole-state snapshots, for seconds, and lists the combos found for the first player, sorted
by damage, KO, positional advantage or length; one can replay a line. Its port code is
GPL-3.0; the game code it builds is unlicensed. **We take ideas, not code.**

What it is not: an opponent. It searches while the game is paused, for one side only; the
victim's DI, teching and actions are not in the search (its own "Current limitations").

Ideas we adopt:

| 4Stockfish | Here |
|-|-|
| Discrete input set, depending on the fighter's state: ground (walk, dash, crouch, shield, tilts, smashes, hop, grab, specials), air (five aerials, full and half drift, double jump, angled air dodge), grab (throws), shield (jump, grab, up smash, up B, down B), attack interrupt windows | the engine's action set, `src/host/engine.c` |
| Macros: dash; short or full hop with an aerial on the first airborne frame or at the apex; double jump plus aerial; wavedash left/right; laser; shine; shine, jump cancel, wavedash | macros, the same list as the actor's steps (`melee-actor.md`) |
| The stick changes at most every 6 frames while moving; L pressed every 6 frames during an aerial so any landing is L-cancelled; an attack followed through its animation; an input that leaves the same state as doing nothing is not a branch | the same pruning |
| Each frame gets a budget of simulated ticks; children are ranked by a short playout (12 frames, up to 24 more while an attack has not hit), the rest of the budget is split by rank, so the search goes deep where damage was seen | budgeted best-first search |
| Transposition table on a state hash; history heuristic (an input that extended a line from the same kind of state is tried earlier); late-move reductions (a low-ranked attack gets a short budget, and a full one only if it beats the best) | the same |
| Evaluation: damage, KO (worth 1000), position (centre stage good, past the ledge bad, hitstun still left bad), advantage (victim's hitstun left minus attacker's frames to act) | the evaluation's generic terms |
| Every kept line replayed straight from the root before it is listed | verification |
| Search ticks are silent, never end the match, start no rumble, write no replay, and a root with a disc read pending is refused | `ahead.c` already: silent, undrawn, never ends the scene |

## The design

```
 live game (window build, paced, drawn)        shadow games ×K (headless, optimised, unpaced)
 ┌──────────────────────────────┐   same inputs  ┌─────────────────────────────────────┐
 │ the match a person plays      │──────────────▶│ the same match, frame for frame      │
 │ (src/host/window.c)           │  each frame    │ search: src/host/engine.c, on the    │
 └──────────────▲───────────────┘                │ rollback records, thousands of       │
                │ the CPU's pad                   │ frames a decision, in parallel       │
 ┌──────────────┴───────────────────────────────┐└──────────────────┬──────────────────┘
 │ the opponent's mind (Python, tools/melee_engine)                 │ lines + scores
 │  goal of the drill ── evaluation                                  │
 │  slippi-ai: what a human would do (the model of you),            ◀┘
 │             what this character would do (the prior over moves)
 │  choose among the best lines with some randomness (variance)
 └───────────────────────────────────────────────────────────────────┘
```

1. **Shadow games** (thinking without stalling the frame). A headless game fed the same
   inputs stays identical to the live one: the netplay work proved two processes agree
   frame for frame when both play and draw the same frames (`netplay-p2p.md`). The live
   game's every input and every command that changes the game (placements, shields,
   anchors, swaps) go to K shadows; a hash compared now and then catches a desync. All
   search runs in the shadows, as many as there are cores.
2. **The search engine** (`search`, C, in the headless build). From the current frame:
   the opponent's candidate lines from the action set and macros, played against the
   player's predicted inputs, ranked by the evaluation, with 4Stockfish's budget split,
   transposition table, history and reductions. Branching on the rollback records (a mark
   per branch point, a rewind back to it). Also a training feature of its own: after an
   attempt, "the best punish here was dash attack, up air: 31%".
3. **slippi-ai as the model of you.** Its policies imitate human play, so sampled from the
   player's side they are a model of what a person does next. With 18 frames of delay their
   next 18 frames depend only on what has already happened: K sampled futures of the
   player's inputs are exact samples of the model over that window. The engine scores
   each opponent line against each future (expected value, and the worst case for "will it
   land").
4. **slippi-ai as the opponent's prior.** The opponent character's policy proposes moves;
   the engine adds them to the candidates and prefers lines a human would play. In
   neutral, with no drill goal in reach, the opponent mostly plays the policy: it moves
   like a person. When the drill's goal is in reach, the search takes over and commits.
   Matchup models exist against Fox for Marth, Sheik, Peach, Puff, Falco, Samus, Yoshi,
   Pikachu and DK (`~/Games/Melee/slippi-ai/deployed_models`); Falcon has none against Fox.
5. **Variance.** The opponent chooses among the lines within a margin of the best with
   probabilities by score (a softmax with a temperature per difficulty), not always the
   best: mixups, and no pattern to memorise.
6. **Goals per drill.** A drill states what the opponent is for ("land a jump-in on the
   shield", "pressure the shield", "recover to the ledge", "punish a missed tech"); the
   evaluation adds that term to the generic ones. Every drill's opponent becomes the
   engine with a goal; the frame tables go.
7. **Training it (reinforcement learning).** slippi-ai's policies fine-tuned on each
   drill's goal in the native build (thousands of frames a second a process, many
   processes, the owner's RTX 3090), with slippi-ai's own penalty for drifting from the
   human-imitation teacher (`slippi_ai/rl/learner.py`) so it stays human. The result needs
   no search at play time.
8. **Adaptation and coaching.** Every attempt logged (positions, inputs, outcome); the
   scenario mix and difficulty steer to the player's weak spots; later the model of you
   tuned on your own play; Claude as the coach between attempts (`ai-coach.md`).

## The plan

| Step | What | Proof |
|-|-|-|
| E1 | Search engine core in C: action set, macros, budgeted search, evaluation, transposition table, verification; the player as given input sequences | finds the known combos (Fox up throw up air at its percents), a landing jump-in from any spacing, matches a brute force on small cases |
| E2 | Shadow games: the live game mirrored into K headless ones, hash-checked | a 10-minute session of a person's inputs, no desync |
| E3 | The engine as a drill's opponent: decisions every few frames, variance, goals; the three reactive drills on it | the reactive drills' tests, plus: no two attempts alike, nothing a moved player can dodge without the counterplay |
| E4 | slippi-ai: the model of you (sampled futures) and the opponent's prior; neutral played by the policy, the search committing | moves like a person (measured against replays: action-state statistics), lands what it commits to |
| E5 | Every drill's opponent on the engine | each drill's tests |
| E6 | Reinforcement learning on drill goals, KL to the imitation teacher | trained opponents beat the search-only one on the goal and stay human-like |
| E7 | Adaptation, the replay and attempt analysis ("best punish here"), Claude as coach | the owner's sessions |

## Status

**E1, the search engine: built (2026-11-13).** `search PORT TARGET HORIZON BUDGET DEPTH
[KEY=VALUE ...]` (`src/host/engine.c`; Python `tools/melee_engine/search.py`). 72 macros:
on the ground wait, walk and dash in and out, jab, the tilts and smashes, grab, dash attack
(out of a run), shield, the four specials, wavedash in and out, a plain hop in and out,
short hops with each aerial (drifting in or not) and full hops with each aerial at the top;
in the air each aerial drifting in, not or out, drifts, fast fall, double jump; in shield
grab, up smash, jump, spot dodge, rolls, hold, drop; holding the opponent the four throws.
L is pulsed during aerials (any landing L-cancelled; `lcancel=0` to turn off). A line
reports its first move's length, so a player of it knows where to decide again; `moves=`
limits the first moves by name prefix (a drill's scenario). The search is a coroutine; its
frames run as a lookahead's do (undrawn, unheard, never ending the scene).

`tests/native/engine.py` (11 checks): the game untouched afterwards; deterministic; a best
line played for real does exactly the damage it was scored with (Falcon, 30 units from a
standing Fox: short hop nair, forward smash, 27%); with a shielding player's inputs given,
the attacks meet the shield; grab then throws are searched (a late move with a reduced
budget, as 4Stockfish's); about 14,000 simulated frames a second on the unoptimised build.

Found on the way: a pure halving budget never reached a grab ranked sixth (it scores
nothing until its throw); every one of the best twelve now gets a reduced share first, and
holding the target scores (`held`, 20 by default).

Where a move ends (the fighter can act again) is read from the game, including its
interrupt flag, `Fighter.allow_interrupt`. The game's attacks clear it as they begin, their
scripts set it at the frame they may be cancelled, and only they read it; no other state
and no new match clears it. So after a fighter's first attack it stays set. Read in every
state, it ended a grab line on its second frame for the rest of the process (2026-11-15).
The engine counts it only in the states that read it, or once it has been seen cleared
since the state began (`follow_interrupt`, `engine.c`). A state that ends with its
animation ends in `Fighter_procAnim`, before `Fighter_procInput` reads the frame's input
in the state it ended into: the first frame a fighter can act on is the frame after which
it is first seen able to. So a branch point whose coming frame ends the state offers the
next state's moves (`moves_for`, the frame played ahead and undone), and a move followed
by another settles on the frame before (`settle_xy` with `eng.exact`: the frame undone,
from the last mark, the path played again); a normal landing's lag ends at its landing lag
(`ftCo_Landing_IASA`), not at its animation's end (2026-11-15,
`tests/native/engine_first_frame.py`).

**E3, the engine as the opponent: begun.** `tools/melee_engine/opponent.py` (`Mind`): each
time the fighter can act it searches, picks one of the best lines by a softmax over their
scores (`temperature`), plays that line's first move, and searches again. The actor's step
`{"do": "engine", "goal": {...}, "moves": "...", "until": "contact"}` hands it the
controller. `tests/actor/engine_opponent.py`: Falcon, Falco and Marth approaching a player
who stood, shielded, dashed or walked in or out, or dash danced during the wait: **72 of 72
approaches land** (the reactive opponent missed the dash dances), and 21 of 24 situations
saw more than one opening over three runs (short hop nair, fair or dair; a wavedash in and
a full hop dair; a dash in and a dash attack). 140 ms a decision headless, unoptimised.

**E2, shadow games: built (2026-11-13).** `tools/melee_engine/shadow.py`. `Shadow`: a
headless game that runs the draw pass, in a thread of its own, applying the live game's
frames and commands in order and answering searches asynchronously. `Mirrored`: the live
game (the window build) with every change also made in the shadow (the commands that
change the game, and each frame's inputs as the game was given them, a person's included);
the fighters' and random seed's hash compared every 120 frames. `LiveMind`: the engine
opponent for a live match. Every decision is for a frame still to come: while a move plays
out, the next is searched from where it ends (its remaining inputs as the search's
`preroll`); with nothing playing, the fighter holds still for the time a search takes
(measured) and the decision is for where that ends; each search is given the time there is
(`ms=`), and stops with the best found when it runs out.

`tests/native/shadow.py` (5 checks, the window build on a virtual display): 1,200 frames of
random inputs, the shadow the same game throughout; then the engine opponent live at 60
frames a second, deciding in the shadow, lands hits against standing, dash dancing,
walking-away and dashing-in stand-ins, 0 of 65 decisions late, and the two still in step.

Found on the way: a search switched the draw pass off before taking its root mark, so going
back to the root brought "off" back, and the shadow drew no more after its first search;
with no draw pass its effects drew random numbers differently, and 70 frames later a hit
did 1% more. Found by dumping a searching and a non-searching shadow and diffing them, then
`save 0`, a search, `hash 0` in one process: the first byte that differed was `host.draw`.
`tests/native/engine.py` now checks every byte after searches in a game that draws. Also:
rollback tracks the game heap 16 MB past its peak, so that what frames gone back over
allocated past it is undone too.

What it does not do yet: it still holds still a lot (searches on the unoptimised build take
about ten frames of real time, and "wait" often scores best); the drills do not use it; and
it plays against a player assumed to hold their input.

**E4, slippi-ai in the engine: first version (2026-11-13).** `tools/melee_engine/human.py`.
The policy server (`tools/melee_actor/policy_server.py`) now answers `peek: N` with the N
frames the model has already decided (with 18 frames of delay the next 17 are fixed; read
from its delayed agent's queue in play order, not `peek_n`, which gives the newest), and
takes `own: true` (its own port's real pad: a person's). `ModelPlayer`: a model of the
person, told what they really pressed, predicting their next 17 frames, which the search
plays against (`engine player`). `ModelBody`: the opponent character's model with its
attacks taken out (A, B, Z, the C-stick): it moves, dash dances, jumps, wavedashes and
shields like a person. `opponent.Blend`: the body moves the fighter every frame; every 4
frames the engine searches against the model of the player for an attack that lands within
its first move, and plays one of the best (a softmax) when there is one.

`tests/actor/blend.py`, Marth against a Fox model for 900 frames, three ways (one run each;
two runs so far):

| Marth | Dealt | Taken | Dash, run, turn frames | Jump frames |
|-|-|-|-|-|
| the Marth model alone | 67%, 20% | 28%, 77% | 85, 57 | 66, 70 |
| the engine alone (assumes Fox holds still) | 52%, 82% | 83%, 66% | 0, 0 | 2, 4 |
| the blend | 81%, 84% | 25%, 15% | 71, 145 | 58, 51 |

The blend moves like the model, hits like the engine, and takes the least: its commitments
varied (dash attack, forward smash, short hop nair and bair, an out-of-shield grab, up tilt,
Dolphin slash, Shield Breaker, a grab). Several model processes share the GPU
(`XLA_PYTHON_CLIENT_PREALLOCATE=false`; a third did not fit otherwise).

Not yet: the blend live (its searches in the shadow: `LiveMind` does it for the engine
alone); the drills on it; an optimised shadow build; a transposition table and the history
heuristic; several sampled futures of the player (determinized search across shadows);
reinforcement learning (E6); adaptation (E7).

## Drills on the engine

The owner, 2026-11-14: "will this even be good for training mode scripts? How will it find
things that fulfill the function of the drill?" An engine that only plays to win would
grab, wait, or never approach. A drill's opponent is the engine held to a **contract**:

| Part | What it is | Anti-air (built) |
|-|-|-|
| The scenario | the moves allowed | the deck's aerial out of a full hop, nothing else |
| The situation | what must happen if the player does nothing | the aerial lands where the player is |
| The answer exists | searched from the player's side before the opponent commits | an up tilt, up smash or back air that hits it in the air before it lands, started no sooner than a person's reaction time (15 frames) after the jump |
| Wrong answers lose | the opponent follows the player, but sees a commitment only after its own reaction time | in the air it corrects drift and the aerial's frame; an anti-air thrown early is whiffed and punished |
| Variance | never the same twice | its own moment, place, jump, drift and aerial frame, chosen among the best by a softmax |

Then play to win (sparring, the Lab) is the same engine without the contract.

**The first drill on it: fox-anti-air, Opponent: Engine (2026-11-14), the default
there.** The owner asked for a dynamic drill, "where both players have to move".
`tools/melee_engine/jumpin.py`:

- `Footsies`: the opponent's movement before it approaches: dash dances, walks, stops, a
  crouch, at random lengths, keeping to a band of distances about the scenario's and on
  the stage, turning back to face the player (since 2026-11-15 `footwork.py`: each dash
  turned inside the character's initial dash, pivots, wavedashes, never a run turned
  around; `opponent-vocabulary.md`, Status). Its pads are planned some frames ahead, so a
  decision can be made for where they lead. (The slippi-ai body, `human.ModelBody`, can
  take its place; Falcon has no model against Fox.)
- `JumpIn`: from a random moment on (20 to 110 frames), every 3 frames within reach of
  the scenario's distance, it asks: if I jumped *now* (or `lead` frames on), which jump-ins
  land, against a player who stops? One of the best is chosen; then the answer check;
  then it jumps, or moves on and looks again. After 90 frames without one it looks at
  every jump and drift each time and closes in on the scenario's distance. In the air,
  every 3 frames: does the plan still land, the player going on as they are for a few
  frames and then standing (`eval=1`)? If not, the drift and the aerial's frame are
  searched again from there. A player's commitment (anything but moving about) is not
  seen until 15 frames after it.
- The drill (`tools/melee_course/drills/fox_neutral.py`): the clock starts at the jump;
  hit while the opponent is in the air with up tilt, up smash or back air is the success;
  the demonstration plays the very answer the check found.

What the engine gained for it (`src/host/engine.c`):

| | |
|-|-|
| `jump_in`, `jump`, `jump_out` | full hops with no aerial yet: the air's moves follow |
| `then=PREFIX,...` | the moves after the first, so a line is made of the drill's moves only |
| `split=N` | the best line for each of the first N moves, not just the first (up to 64) |
| The timing scan, `scan=STEP` | lines [FIRST] + a hold (`hold=`: the stick in, none, out, walking in or out, `ff_` with a fast fall) for K frames + LAST, every K tried. The branch point moves forward along the hold one frame at a time, its rollback records merged into one (`host_rb_merge`), so every timing costs about one playout. The macro tree, stepping 6 frames at a time, found landing full hops for Falcon's nair only with a fast fall, and none for his dair or Peach's fair; the scan finds dozens. `stop=1` ends a line at its first contact, `trial=N` follows LAST N frames, `near=D` presses only within D units, `from=K` only after K frames, `enough=N` stops after N lines connect, counting only contacts in PORT's states `want=S,...` (what the drill counts), `norun=1` ends a hold on the ground where it would run, pass the target or reach the ledge, `front=N` keeps only a line whose PORT stays on its side of the target from the line's start until its move is over (it can act, or it hit in the air and has landed) and the frame an answer pressed on the target's first frame out of shield stun hits (N frames: a frame-4 shine out of shield is `front=4`), whichever is later, the frames past the line's end played letting go (each line's SIDE and CROSS; "@ ok"'s last number the lines dropped) |
| `eval=1` | the pre-roll scored as one line ("plan"): a lookahead that honours `engine player` |
| Each line's AIR and STATE | the target in the air at the first contact, and what PORT was doing (an up smash, not a dash attack) |

`tests/course/anti_air_engine.py`, the four scenarios, the player's stand-in moving about
too until the jump (12 attempts each way, headless):

| The player, after the jump | Result |
|-|-|
| stops | the jump-in lands 11 of 11 (one attempt saw no approach and was not counted) |
| answers: sees the jump-in perfectly, but no sooner than 15 frames after it, and searches for an anti-air | success 12 of 12 |
| up smashes as soon as they can react | punished 12 of 12 |
| keeps dash dancing | lands about half the time (3 to 7 of 12 between versions): a dash dancer under a full hop is hard to hit in a match too; the drill calls it "No anti-air" |
| the demonstration | 8 of 8 |

48 attempts: 48 different jump-ins (frame, where, which line), 37 different lines; both
fighters moved before every one. Found on the way: aimed at a player "holding their pad",
a dash held was a run across the stage, and it jumped from 116 units at a Fox who then
stopped; the bodies dashed off the stage near the ledge (a dash and its slide carry 40
units); Falcon's dair, which lands only at a narrow spacing, waited up to 7 seconds until
half drift and the widened look were added.

## Thinking while a person plays: forks

The shadow games (E2) stay in step only if every command that changes the game is made in
both, from the match's start; the client keeps matches across drills, swaps opponents,
loads quietly, draws its own pictures. A game state cannot be copied from the window build
to a headless one either: they are different programs, and the state holds code addresses.
So the opponent thinks in **forks of the window game itself**: `engine fork IN OUT`
(`src/host/engine.c`) forks the process at the frame boundary; the copy stands at that
frame and answers searches, lookaheads and the state on its own pipes; it plays no frame
for real (`step`, `tick`, `quit` refused or ending it), skips the scene loop's render calls
(`gmscene.c` is built with them renamed: a window's graphics are its parent's), and leaves
when its pipe closes. It is exact: it is the game, at that frame.

`tools/melee_engine/fork.py`: `Fork(n)` (a game `search()` can be given), and `InFork`,
the opponent's thinker in a live match: each decision forks at its frame and runs in a
thread, for a frame some frames on; how far on (`lead_for(kind)`) follows how long that kind
of decision takes, the second slowest of the last 8 (a decision to jump: about 70 ms
headless; a correction in the air: a few ms when the plan still lands, capped at 24 frames
when it must be searched again). `melee_course/react.thinker` uses it whenever the game is
the window build, so the client needs no change.

Measured: a fork of the window build (950 MB resident, software rendering) takes 7 ms of
the frame, headless 1 ms; with one every 4 frames the paced window kept 16.7 ms frames (99th
percentile 17.6 ms). A fork finds exactly what the game would. In real time (headless,
paced at 60 frames a second): 6 of 7 jump-ins landed unanswered and 6 of 7 were beaten
answered, no frame waited. With the machine loaded by three other window tests (load 25
on 28 cores), decisions took up to 1.3 s: 4 of 8 landed, 6 of 8 were beaten. The drill in
the window build off screen (software rendering, loaded): 2 of 4 landed, 4 of 4 beaten.
The window build's forks search about 1.8 times slower than headless; on the owner's
desktop the GPU draws and the cores are free, which none of these runs had.

**How it feels live: `tools/melee_engine/feel.py` (2026-11-15).** The owner, playing
fox-shine-oos in the client: "the sheik is just missing ... and missing still". `feel.py`
plays a drill's scenarios as the client does (the course runtime, the drill's script,
decisions in forks of the window build at 60 frames a second; or headless, decided in the
game itself; `--load K` beside K busy cores) against stand-ins (the shield held, digitally,
by an analog press, or noisily as a controller holds it; a person waiting in shield who
walks a little now and then; one who lets go as the opponent commits; the frame-4 shine
out of shield), and records every commitment: the frame its decision was asked on and was
for, the frame it began, the line, the contact it foresaw and when, what really happened
and when, whether the player's pad left what the decision assumed, and (`--trace`) the
first frame the live game differs from the one the fork foresaw. The causes, each fixed:

| Cause | Evidence | Fix |
|-|-|-|
| A second decision, asked while the first one's line waited for its frame, came back after the line had begun and replaced it: `plan[i]` with `i` negative played the end of the new plan | live, 8 of 14 Sheik commitments replaced part-way, every miss among them; headless (decided at once) never | one commitment: once a decision has found a line, no other is asked, and a commitment that comes back while one is in play is dropped (`EngineOpponent`) |
| The drill's infinite shield was set by the driver between frames: live the shield was full, in a search it shrank as it was held | headless, 22 of 220 contacts 1 or 2 frames before the frame foreseen; against the frame-4 shine out of shield, 4 of 220 tries out of reach (Marth's nair, Samus's aerials: a first hit met the live shield up to 5 frames early) | the game keeps it (`shield P H 1`, `src/host/setup.c`): set again at every frame boundary, the frames searches, lookaheads and forks play included; the drill keeps it from its setup, the client lets it go when the drill is left |
| A committed line's held stick ran past the initial dash and, the fighter past the player, turned round in the run (the stick is toward the target each frame); once Falco ran to the ledge and turned (found by the movement helper) | headless, 86 of 220 lines ran, 507 TurnRun frames in them | the timing scan's `norun=1` (`engine.c`): a hold on the ground ends where its fighter would run, has passed the target or is 10 units from the ledge; `Commit` asks for it: 5 TurnRun frames left in 219 lines, every one landing |
| A body that plans again on its own (the new footwork's resync, an `ahead` padded with neutral pads) would have a line begin from where its decision never saw it | (a guard: with the old body the pads were always kept) | the pads the body plays while a decision is out, or its line waits, are compared with the pre-roll; one it does not keep to drops the decision |

Not causes: the draw pass (the window build's live frames draw and draw random numbers,
search frames do not; headless with the draw pass on gave the very same 220 results),
frame pacing (a frame over 18.5 ms in 1 of 1,000 unloaded), late decisions (a decision back
after its frame is dropped and asked again: lost time, never a miss), the player's shield
input (digital, analog, a noisy controller: every contact on its frame). A person's real
change of input is the one remaining cause of a miss, and the opponent now reacts to it: a
decision keeps the pad it assumed (`Contract.assumes`: Commit's, a shield held), and the
player leaving it is seen after the opponent's reaction time, as their commitments are:
a line not begun is dropped; one begun is checked again in a fork, kept if it still lands,
replaced by another answered one, or given up before its decisive press (`react`, the
`bait` stand-in: Fox gave up 14 lines against a player who let go as it committed).

Landed on a shielding player (the drill's part 3, every character of its deck, 20 attempts
each unless noted):

| | Fox | Marth | Puff | Falco | Sheik | Falcon | Peach | ICs | Pika | Yoshi | Samus | All |
|-|-|-|-|-|-|-|-|-|-|-|-|-|
| live, before | 91% | 78% | 95% | 79% | 95% | 91% | 100% | 95% | 95% | 82% | 91% | 212 of 236, 90% |
| live, one decision and the kept shield | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 218 of 218 |
| live, all of it (15 attempts) | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 154 of 154, one line cut short by the drill's reset |
| live under load, before | 72% | 94% | 78% | 81% | 100% | 69% | 94% | 83% | 81% | 76% | 88% | 148 of 179, 83% |
| live under load, after (before `norun`) | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 158 of 158 |
| headless, before and after | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 220 of 220 |

Under load: 20 busy cores, before and after played side by side, a load average of 26 to
42 on 28 cores; 15 attempts each; the window game below 60 frames a second (most frames
over 18.5 ms). Every line began on the frame it was decided for, before and after; what
went wrong before was the line itself. Decisions take 80 to 140 ms (the 90th percentile
180 to 320 ms) in the unloaded window build's forks; 15 to 20% of them come back after
their frame and are asked again (lost time: the body moves on, never a miss).

The frame-4 shine out of shield answered every attack headless after (220 of 220, every
contact on its frame; 216 of 220 before the kept shield). Against the shuffling stand-in,
live, 168 of 179 landed: 10 misses a change of the player's pad 1 to 18 frames before the
contact (the attack already pressed), one line cut short by the drill's reset; headless
251 of 258, the same kinds. A line cut short is one that had not landed when the drill's
part 3 reset (`within`: 300 frames from the reset); the slowest approaches commit some
220 frames into it (typically 40), before and after.

**The front of the shield (2026-11-15).** The owner, after the fixes above: "the CPU
often overshoots on the shield hit which is very very hard to punish with shine OoS".
`feel.py` now records where each commitment met the shield: the side it started on, the
gap at the contact along it, and the first frame the opponent was past the player up to
the frame a frame-4 shine out of shield hits (the first frame out of shield stun + 3), up
to its own landing or end and that frame, and up to its line's end; and the family of its
attack. Before, contacts were from the front (1 of 440 from behind), but the attacker
passed through; and a dash attack, which reaches and is answered from anywhere, was most
of what it committed to (the drill's part 3 against a shielding stand-in, 40 attempts a
character headless, 20 live in the window build on a virtual display; "after" is the
front of the shield, the drift-out short hops, the variety pick and the deck's new
scripts together):

| | Fox | Marth | Puff | Falco | Sheik | Falcon | Peach | ICs | Pika | Yoshi | Samus | All |
|-|-|-|-|-|-|-|-|-|-|-|-|-|
| past the player by the frame a frame-4 shine hits, before, headless; live | 2; 1 | 0; 2 | 4; 5 | 0; 0 | 2; 1 | 12; 5 | 3; 4 | 10; 5 | 11; 3 | 10; 4 | 5; 1 | 59 of 440; 31 of 218 |
| past the player by its landing or end, before, headless; live | 11; 5 | 10; 3 | 15; 10 | 6; 3 | 5; 5 | 17; 9 | 18; 8 | 12; 7 | 20; 6 | 15; 9 | 9; 5 | 138 of 440; 70 of 218 |
| after, headless; live | 0; 0 | 0; 0 | 0; 0 | 0; 0 | 0; 0 | 0; 0 | 0; 0 | 0; 0 | 0; 0 | 0; 0 | 0; 0 | 0 of 440; 0 of 218 |
| landed, after, headless; live | 40/40; 20/20 | 40/40; 20/20 | 40/40; 20/20 | 40/40; 20/20 | 40/40; 20/20 | 40/40; 20/20 | 40/40; 19/19 | 40/40; 20/20 | 40/40; 20/20 | 40/40; 20/20 | 40/40; 19/19 | 440 of 440; 218 of 218 |
| families, before → after, headless | 9 → 10 | 8 → 9 | 7 → 9 | 8 → 10 | 8 → 8 | 8 → 9 | 4 → 5 | 9 → 6 | 11 → 8 | 8 → 9 | 8 → 6 |  |
| the most common, before → after, headless | dash attack 30% → uair 18% | dash attack 45% → dash attack 18% | dash attack 30% → dash attack 20% | fsmash 20% → bair 18% | dash attack 30% → nair 20% | dash attack 28% → fair 20% | dash attack 38% → dash attack 38% | dash attack 20% → fair 20% | dash attack 22% → nair 22% | dash attack 28% → fair 18% | dash attack 48% → dash attack 22% |  |
| families, before → after, live | 7 → 9 | 8 → 6 | 8 → 6 | 6 → 10 | 6 → 6 | 6 → 8 | 4 → 5 | 8 → 6 | 9 → 10 | 6 → 6 | 6 → 6 |  |
| the most common, before → after, live | dash attack 30% → nair 20% | dash attack 55% → dash attack 30% | dash attack 30% → dash attack 35% | fsmash 35% → dair 20% | dash attack 32% → dair 20% | dash attack 35% → dair 25% | dash attack 42% → dash attack 42% | nair 35% → fair 25% | dsmash 25% → dair 20% | dash attack 30% → dash attack 30% | dash attack 35% → fsmash 26% |  |
| distinct lines, before → after, headless (40 attempts) | 32 → 37 | 26 → 34 | 29 → 34 | 34 → 38 | 32 → 34 | 30 → 33 | 23 → 24 | 29 → 35 | 32 → 39 | 31 → 35 | 26 → 33 |  |
| frames to the commitment (median), before → after, live | 49 → 47 | 38 → 152 | 50 → 86 | 48 → 48 | 37 → 74 | 49 → 85 | 40 → 172 | 38 → 51 | 54 → 61 | 42 → 147 | 64 → 111 |  |

Families that land on the front of the shield and are answered by the frame-4 shine,
from a shielding Fox 8 to 38 units away (each family's lines searched alone, with and
without `front=4`): every one of Fox's, Jigglypuff's, Falco's, Sheik's and the Ice
Climbers' that the shine answers at all survives it, some at fewer spacings; lost to it
(answered only through the shield or from behind): Marth's nair, fair and dair (spaced,
drifting out, they are safe from the shine), Falcon's forward smash, bair, uair and
down-B, Peach's nair, Pikachu's side-B, Yoshi's uair and dair, Samus's fair and uair.
Not answered by a frame-4 shine from any of those spacings, front or not (the attacker
acts first, or a second hit meets the shield in the answer's frames): most up and down
smashes, Fox's up and down tilts, Peach's tilts, forward smash, uair and dair, Samus's
nair, bair and dair; from a moving start a few come out all the same (Fox's up and down
tilts, Peach's down tilt).

The cause: nothing in a line said where its fighter goes after the contact. A short hop
drifting in, or one out of a dash with no drift, carries an aerial through the shield (a
dash attack slides past); the frame-4 shine, a sphere, still hits it, so the contract
answered it. The timing scan's `front=N` (`engine.c`, `front_ok`): a line counts only if
PORT never passes the target from the line's start until its move is over and the
answer's frame, the frames after the line's end played letting go as the opponent plays
them; `Commit` asks for it with `within`'s frames, and checks it again when the player
moves (`contracts.lands(front=)`). The short hops drifting out (`sh_X_out`) add the
spaced aerial. The deck picks for variety (`opponent-vocabulary.md`, `approach`): the
families drawn into a queue, three searched a look, one used twice in the last 8 waiting
while the opponent is patient. On a shield the contract also wants one hit in the
answer's frames (`behave.stun_over(clear=)`: Yoshi's two-hit back air told a jump three
frames late that the shield was hit again, where check.py's mistake is judged late). And a
lookahead takes 48 pads, not 16 (`ahead.c`): live, a body's dash dances in the pre-roll
and a line's L-cancel pulses made more, and the decision failed ("16 pads at most": 106
of 750 decisions before, 587 of 1,476 with the variety pick, each one waited for again).
The cost: live, the commitment comes later for some (Marth's median 38 to 152 frames,
Peach's 40 to 172, Yoshi's 42 to 147): a family used twice waits for the others, each
look a decision in a fork; `Commit.CAP` (2 of the last 8), `PER_LOOK` (3) and the
patience (`EngineOpponent.PATIENCE`, 90 frames) set it. Tried first and dropped: one
family a look (even headless; live, Peach waited 180 frames and 7 of 20 attempts saw no
attack), every move a look with the family drawn among those found (the scan stops at
`enough` with what it finds first: Sheik's tilts never, Peach's dash attack 80%), three a
look with no cap (Jigglypuff's dash attack 70% live).

## Recovering: the opponent off the stage (2026-11-17)

The owner, asking for an edgeguard drill (`data/drills/fox-edgeguard.json`): "a big test
of the engine performance because it should be able to predict and adapt to the players
edgeguard. For example for fox, if it is firefox angling, and right before the angle is
locked in the player starts to drop and go for a bair to cover the ledge, the CPU could
change angle to go high. This should have options for reaction time of the engine so the
player can essentially choose their own difficulty. The goal of this is to get the player
amazing at edgeguarding by building a CPU that recovers very optimally to force the
player to adapt and learn more consistent options".

A recovery is not an attack that lands, so it is not the macro search's: it is the
behaviour `recover` (`tools/melee_engine/recover.py`; `opponent-vocabulary.md`), on three
host commands.

| Command | What |
|-|-|
| `launch P X Y PERCENT KB ANGLE DIR [JUMPS]` (`setup.c`) | a fighter knocked away by the game's own launch (`ftCo_8008DCE0`, as a throw's release calls it): the damage state its knockback gives, its speed and decay, its hitstun, the tumble. TM-CE's edgeguard event writes those itself (`Reset_CPU`, `src/edgeguard.c`); its hit strengths are the drill's. With the state reading H frames of hitstun, a jump pressed H - 1 frames later is the first that works (measured: a frame sooner is ignored) |
| `route PORT TARGET HORIZON pads [| pads]` (`ahead.c`) | a way back played ahead and undone: PORT's pads, TARGET's (what the player is expected to do), until PORT has caught the ledge, has landed and can act, is hit or grabbed, or is lost (dead, or under the lower blast line). The reply says which and when, where, the landing's frame and the first free one, how close the target's hitboxes came, how near the ledge it came (for routes that fall short), and with `routep` the path frame by frame. 22,000 frames a second headless: a 140-frame recovery in 6 ms |
| `hitboxes PORT FRAMES pads` (`ahead.c`) | where a fighter's hitboxes would be, frame by frame, if it pressed that |

**A decision** (`recover.decide`, about 50 routes): from where the fighter is, after its
hitstun, the routes its character has: the drift; its jumps, now or later; each special
(`recover.TOOLS`: Fire Fox, Fire Bird and Vanish at an angle, Illusion and Phantasm full
or shortened, Dolphin Slash, Dancing Blade's stall, Falcon Dive and the kick that gives
the jump back, the parasol and the float, Pound, Belay and Squall Hammer mashed, Quick
Attack's two directions, a bomb, Screw Attack) now or later, after a jump or without, and
an air dodge. A steered special's angles are aimed from where the fighter is when the
angle is read (one route played to there first): at the ledge, a little under and over
it, and a sweep. Each is played ahead against the player going on with what they are
doing (their pad three frames more, then let go: an attack begun plays out, a ledge held
stays held). The score: the ledge or the stage reached; a landing's lag next to the
player; the player's hitboxes close by; the frames flown with nothing left to change (an
air dodge 60 frames from the ledge is seen coming); the jump kept; and what the player
could do. One of the best by a softmax, the kinds of route flown lately (kept from one
attempt to the next) drawn less. Where nothing reaches, the four routes that came nearest
the ledge are played again at every timing 8 frames either side.

**What the player could do** (`recover.threats`, `exposure`). A route that ends well
against a player who does nothing more may pass through where they can strike. Each
decision plays the player ahead alone through the attacks they have from where they are
(in the air: the five aerials and the down special, pressed now and 5, 10, 16 and 24
frames on; on the ground: the smashes and the down special) and keeps their hitboxes
frame by frame. The share of them a route's body crosses at its frame costs it: an
eighth 17 points, a quarter 35 (a route kept is worth 12). So a player who has jumped
off the stage threatens the ledge and not the stage above them, and the opponent goes
high; one standing at the edge threatens what comes up beside it.

**Reacting** (`recover.Pilot`). The route is checked again every 4 frames (one route
played: 5 ms) and decided again when it no longer ends well or is worth 25 less. What
the player commits to (`recover.commitment`: the ground left, a double jump, an attack,
a special, the shield, a dodge, the ledge taken or left) starts a clock: until `react`
frames have passed the opponent decides nothing, and then decides with what it sees.
Moving about on the ground is not a commitment: that it follows as it happens. What it
can still change is what the game allows: in a special only the stick (Fire Fox's angle
until its 43rd frame) and B. `react` is the scenario's (15), or the player's: CPU
reaction, 30 to 3 frames, in the pause menu and Settings.

**Side by side** (`recover.Team`). Fifty routes one after the other take a third of a
second, too long for an opponent that reacts in a quarter. A decision forks the game it
is made in six times (`engine fork`: a forked game may now fork too, so the game a person
watches still pays for one fork) and plays its routes in those copies, each answering in
a thread. Headless a recovery's thinking, checks and all, takes 150 to 250 ms (350 to
400 before); live, in forks of the window build on a virtual display, a first decision
took 207 to 226 ms (`tests/client/edgeguard.py`), inside the launch's hitstun (32 to 68
frames).

`tests/engine/recover.py` (15 of 15, headless): the launch's state, hitstun and tumble;
a route played ahead says where it ends, leaves the game as it was, and played for real
ends there on that frame; Fox, Marth, Sheik and Jigglypuff back from six launches each
by more than one kind of route; the same seed, the same route; the first part's opponent
(`to` "ledge", `tools` "jump") falls past a ledge held; and the owner's example, four
seeds: Fox, 62 units out and 18 up, charges Fire Fox at the ledge; 30 frames into the
charge (13 before the angle is read) the player jumps off the stage and back airs where
he would arrive.

| Reaction | What Fox does | Result |
|-|-|-|
| 3 frames | 4 frames after the jump the stick is aimed onto the stage (20 or 60 degrees up) | lands on the stage unhit, 4 of 4 |
| 30 frames | nothing before the angle is read | flies at the ledge: hit by the back air 3 of 4 |

`tools/melee_engine/recoveries.py` (the drill's launches, TM-CE's weak, normal, hard and
shallow, either ledge, headless):

| The player | Back |
|-|-|
| does nothing, the eleven characters, 16 recoveries each | 175 of 176 (Falco, shallow and far, once fell short) |
| takes the ledge late (a wavedash back as the opponent comes within 75 units), six characters (Fox, Marth, Sheik, Falco, Captain Falcon, Pikachu), normal and shallow launches, 48 recoveries: reaction 30, 15, 3 | 23, 27, 31 |
| jumps off and back airs the ledge: 30, 15, 3 | 38, 39, 40 |
| stands at the edge and down smashes: 30, 15, 3 | 34, 33, 35 |
| takes the ledge at once and holds it: 30, 15, 3 | 44, 45, 45 |

(The stand-ins are crude: they do not aim. A ledge taken early is no edgeguard against a
special with a hitbox: once the 30 frames of intangibility are over, Fire Fox, Dolphin
Slash, Vanish, Quick Attack and Screw Attack hit Fox off the ledge and take it, which the
opponent finds by playing it. The drill's first part has the opponent come back with its
jump alone for that reason.)

Not yet: a model of the player beyond "goes on, then lets go" and the attacks they have
without moving (a grounded player's run to the ledge, a jump and an aerial, a ledge
dropped and regrabbed); stalling until the player leaves the ledge; DI of the launch and
teching the stage; the wall jump and Samus's grapple; ledge options once it hangs (the
drill judges there); an edgeguarding stand-in that aims, to measure it against. The
routes' table is hand-written per character (`recover.TOOLS`); what a route comes to is
the game's.

Not yet: the other drills on the engine (E5: wavedash back, shine out of shield, then the
rest, each with its contract); the slippi-ai body and model of the player in the drills;
several futures of the player (a jump-in that lands whether they stop or go on); faster
searches (an optimised build, fewer rollback pages scanned); TT and history; E6, E7.
