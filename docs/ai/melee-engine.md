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

**E3, the engine as the opponent: begun.** `tools/melee_engine/opponent.py` (`Mind`): each
time the fighter can act it searches, picks one of the best lines by a softmax over their
scores (`temperature`), plays that line's first move, and searches again. The actor's step
`{"do": "engine", "goal": {...}, "moves": "...", "until": "contact"}` hands it the
controller. `tests/actor/engine_opponent.py`: Falcon, Falco and Marth approaching a player
who stood, shielded, dashed or walked in or out, or dash danced during the wait: **72 of 72
approaches land** (the reactive opponent missed the dash dances), and 21 of 24 situations
saw more than one opening over three runs (short hop nair, fair or dair; a wavedash in and
a full hop dair; a dash in and a dash attack). 140 ms a decision headless, unoptimised.

Not yet: the shadow games (E2), without which a live match cannot think this long; the
drills on the engine; slippi-ai as the model of the player and as the prior (E4); a
transposition table and the history heuristic.
