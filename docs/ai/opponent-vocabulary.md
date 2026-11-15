# The opponent's vocabulary: moves, conditions, behaviours, scripts

The owner, 2026-11-15: "how robust is our macro system for instructing the engine/actor
system to do things? We need to scope out our set of things so we can build better
drills. For example 'dash dance out of the opponents range', 'wait for approach', 'pivot
forward smash', 'pivot grab', 'chain grab', etc.", then "Let's implement that new scope for
the engine before we get started on drills that will utilize it so we can start with a
better base".

A drill's opponent is written in four layers, each built on the one below. The engine
(`melee-engine.md`: the search on the real game, forks, contracts) is the bottom; a drill
file (`drill-format.md`) is the top. Nothing in a drill names a frame or a position the
game can work out.

| Layer | What it says | Where |
|-|-|-|
| 1. Moves | how to do one thing with the controller, frame-exact, for any character: "pivot forward smash", "dash grab" | `src/host/engine.c` macros: the search plays them, a script names them |
| 2. Conditions | what is true now, as the opponent sees it: "the player is approaching", "I am out of their range" | `tools/melee_engine/sense.py` |
| 3. Behaviours | what the opponent does over time until a condition: "dash dance out of range", "punish" | `tools/melee_engine/behave.py` |
| 4. Scripts | behaviours in order, branching, looping, mixing, held to contracts | a drill's `"opponent": {"script": [...]}`, run by `tools/melee_engine/script.py` |

## 1. Moves (engine macros)

Built (`engine.c`, about 100): wait, walk and dash in and out, every ground attack, dash
attack, shield, the four specials, wavedash in and out, hops and full hops (each aerial,
drifting in or not), the aerials in the air (drifting in, none, out), drifts, fast fall,
double jumps; out of shield grab, up smash, jump, spot dodge, rolls, shine (`oos_down_b`),
up-B, hold, drop; the four throws; techs (in place, in, out), getups, ledge options,
angled up-B, air dodges in four directions.

To add, so that drills can name them:

| Move | What it is | Notes |
|-|-|-|
| `pivot_<attack>`: `ftilt` `fsmash` `utilt` `usmash` `dtilt` `dsmash` `grab` `jab` | a dash out, a pivot (the stick flicked back through the middle and let go: the turn ends standing), then the attack facing in | the pivot as the pivot drill found it: 0.8 reached within 2 frames of crossing, under 0.8 the frame after; not in a dash's first 4 frames. Dash length a parameter of the scan (`hold`) or two fixed lengths |
| `dash_grab` | a dash in, Z | out of a dash or a run |
| `jc_grab`, `jc_usmash` | a dash in, jump, Z (or up on the C-stick) in the jump squat | a standing grab or up smash with the dash's slide |
| `boost_grab` | a dash attack, Z in its first frames | |
| `dash_dance` | in and out again, one dash each | movement; `footsies` uses it |
| `crouch` | the stick held down | crouch cancel, waiting |
| `platform_drop` | the stick down on a platform | |
| `waveland_in`, `waveland_out`, `waveland` | an air dodge down and in, out or straight onto the floor below | platforms |
| regrabs | `dash_grab`, `pivot_grab`, `jc_grab`, `grab` after a throw | a chain grab is a script loop (below) |

Each new move is offered where the fighter's state allows it (`moves_for`), named as the
others are, and proved: `tests/native/engine_moves.py` plays each from where it applies
and checks the game's states (the pivot's turn ends standing, the grab comes out of a
dash, the jump-cancelled grab is a standing grab).

## 2. Conditions (`sense.py`)

A condition is true or false on a frame, as the opponent sees it. A condition about the
player is seen `react` frames late (15 by default: a person's reaction; a drill sets it),
so the opponent cannot answer what it could not have seen.

| Condition | True when |
|-|-|
| `{"distance": [LO, HI]}` | the fighters are that far apart (units, along the stage) |
| `"in_their_range"`, `"out_of_their_range"` | the player can (cannot) hit the opponent within `frames` (12) with any move: searched from the player's side, as an answer is (`contracts.Answer`), cached a few frames |
| `"in_my_range"`, `"out_of_my_range"` | the same from the opponent's side |
| `"approach"` | the player closes in: dashing, running, walking or jumping toward, or the gap shrinking by more than a unit a frame |
| `"retreat"` | the player moves away |
| `"committed"` | the player cannot act: an attack, landing lag, shield stun, a roll or dodge, hitstun, tumble, lying down, grabbed |
| `{"state": NAME}` | the player in a state of the drill format's names (`STATES`) |
| `"shielding"`, `{"shield_below": H}` | the player shields; its health under H |
| `"airborne"`, `"grounded"` | the player in the air, on the floor |
| `"on_ledge"`, `"offstage"`, `"on_platform"` | where the player is |
| `{"percent": [LO, HI]}` | the player's damage |
| `{"lag": N}` | the player can act no sooner than N frames from now (an opening) |
| `{"me": CONDITION}` | the same, of the opponent itself, seen at once |
| `{"not": C}`, `{"any": [...]}`, `{"all": [...]}` | combinations |
| `{"after": N}` | N frames into the behaviour |

## 3. Behaviours (`behave.py`)

A behaviour moves the opponent frame by frame until its condition (`"until"`), its time
(`"for"` frames) or its own end (an attack's contact). Each is a body (pads planned some
frames ahead, as `Footsies` is) or a decision the engine searches in a fork, as
`EngineOpponent` does now.

| Behaviour | What it does |
|-|-|
| `footsies` `range` | dash dances, walks, stops and crouches, keeping to a band: `"outside"` (just out of the player's range), `"edge"` (at the edge of its own), or `[LO, HI]` |
| `hold` `pad` | stands, shields, crouches (`"stand"`, `"shield"`, `"crouch"`) |
| `retreat` | moves out of the player's range and stays there |
| `approach` `moves` `lands` | commits to one of `moves` (by name prefix) that the engine finds lands (`"hit"`, `"shield"`, `"any"`), from wherever it is; with a contract (below) only one the player can answer |
| `move` `name` | plays one named move exactly (a scripted moment) |
| `punish` | plays to win from here until the player can act again: the best combo the engine finds |
| `pressure` | attacks the shield with options that are safe on it, until the shield breaks or the player acts |
| `chase` | waits for the player's tech, getup or ledge option (seen `react` late) and covers it |
| `chain_grab` `throw` | grab, the throw, a regrab while the engine finds one that lands before the player can act |
| `edgeguard`, `recover` | off the stage (later) |
| `play` | moves as a person does (the slippi-ai body where a model exists, `footsies` otherwise) |

## 4. Scripts (in a drill)

A drill's opponent is a script: steps in order, each a behaviour or a combinator.

```json
"opponent": {
  "character": "marth",
  "react": 15,
  "script": [
    {"do": "footsies", "range": "outside", "until": "approach"},
    {"mix": [
      {"weight": 2, "steps": [{"do": "approach", "moves": "pivot_fsmash,pivot_grab", "lands": "hit"}]},
      {"weight": 1, "steps": [{"do": "retreat", "for": 40}]}
    ]}
  ],
  "loop": true
}
```

| Combinator | What it does |
|-|-|
| `{"if": C, "then": [...], "else": [...]}` | a branch, C read when the step starts |
| `{"mix": [{"weight": W, "steps": [...]}, ...]}` | one of them, by weight (a mixup: never a pattern to learn) |
| `{"repeat": [...], "while": C, "times": N}` | a loop (a chain grab while it lands; pressure while the shield holds) |
| `"loop": true` | the whole script again when it ends |

**Contracts.** A committing behaviour may carry one: `{"do": "approach", "moves": "...",
"lands": "shield", "contract": {"answer": "oos_down_b", "within": 15}}`: it commits only to
an option the player can answer with that move, searched from the player's side before it
commits (`contracts.Answer`), as fox-anti-air's jump-in does. That is what makes a drill
fair: the situation happens if the player does nothing, an answer exists, wrong answers
lose.

**Determinism.** A script's random choices come from the drill's seed: `check.py` replays
a drill's examples and mistakes against the same opponent, and the coach's demonstration
plays what the check found.

## Status

- 2026-11-15: this scope written. Built before it: the layer-1 moves listed as built,
  `Footsies`, `Hold`, `EngineOpponent` and the `JumpIn` contract (`melee-engine.md`).
