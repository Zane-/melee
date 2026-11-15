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

Added for drills to name (built 2026-11-15, 26 macros; `engine macros` lists them):

| Move | What it does | Parameters, as measured |
|-|-|-|
| `pivot_<attack>`, `pivot_<attack>_long`: `jab` `ftilt` `fsmash` `utilt` `usmash` `dtilt` `dsmash` `grab` | a dash away from the target, the stick flicked full toward it for one frame (a smash turn: the fighter faces in), the attack on the next frame with the stick under 0.8 (a tilt's angle, a C-stick smash, Z): the attack comes out of the turn, which never becomes a dash back | the dash's length: `pivot_X` the shortest a reversal turns (4 frames: a dash's first 4 ignore it, `p_ftCommonData->x44`; from standing facing the target the dash out starts with a turn of its own), `pivot_X_long` the dash's last frame before it would become a run (measured once per character by playing that frame and going back: Fox 11, Marth 15, Sheik 7, Captain Falcon 15, Peach 15, Jigglypuff 12, Mewtwo 18, Game & Watch 8, Bowser 13). Every length between: the timing scan, `scan=1 hold=out then=pivot_X` (lines `hold_out:K+pivot_X`, K the frames of dash before it). The prefix `pivot_fsmash` names both lengths. Offered standing, walking, turning or in a dash; not in a run (it turns slowly) |
| `dash_grab` | a dash toward the target, Z: a dash grab | from standing the dash's first frame, then Z; out of a dash or a run toward the target, Z at once. A longer dash: `dash_in+dash_grab`, or the scan's `hold=in` |
| `jc_grab`, `jc_usmash` | out of a dash toward the target, the jump, and on the jump squat's first frame Z or up on the C-stick: a standing grab or up smash, never airborne, sliding with the dash | as `dash_grab`: from standing a dash of one frame first; out of a dash or run at once |
| `boost_grab` | a dash attack, then Z on its next frame: a dash grab with the dash attack's speed | Z grabs on the 1st, 2nd or 3rd frame after the dash attack's A, for all six characters tested (`p_ftCommonData->x68`); the dash attack itself comes out of a dash only after its first 4 frames (A earlier is a forward smash), so from standing it dashes 4 frames first |
| `dash_dance` | a dash out and one back in, 8 frames each (the reversal a turn and a dash back), let go | movement; not out of a run |
| `crouch` | the stick held down 8 frames: a crouch | on a platform a stick smashed down drops through it (for every character: 3 frames of crouch, then through), so there the stick goes to -30 (out of the dead zone, short of a crouch) for 6 frames first: a crouch that stays on the platform |
| `platform_drop` | the stick smashed down from the middle on a platform: 3 frames of crouch, then through (Pass); the move ends on the first frame in the air, where the air's moves (aerials, `waveland_*`) follow | offered only on a platform (`mpColl_IsOnPlatform`). Pass now counts as able to act (its interrupt allows every air option) |
| `waveland_in`, `waveland_out`, `waveland` | in the air above a floor: waits for the fall, then an air dodge down and in, out (`100, -80`, as `wavedash_in`) or straight down on the last frame before the fall would land by itself (the floor below the ECB from `mpCheckFloor`, the platform dropped through not counted): it lands in its landing lag (LandingFallSpecial, 10 frames), often on the dodge's own frame | offered in the air with a floor within 40 units below. Slides on Battlefield's platform: 13.7 (Peach) to 18.4 (Marth) units in or out, 0 straight |
| regrabs | `grab`, `dash_grab`, `jc_grab`, `pivot_grab` after a throw: the ground moves are offered once the thrower can act out of its throw | a chain grab is a script loop (below) |

**The dash's length** matters (how far out the pivot goes, how far its attack reaches),
so the search varies it two ways. In the macro tree, two fixed lengths, the extremes the
game allows: the quickest pivot and the one that goes farthest out, each one playout at a
branch point as every macro is, and each the game's own measure for every character (no
table of dash lengths to keep). Between them, every length frame by frame with the timing
scan, which moves its branch point along the dash a frame at a time, about one playout a
length. A search parameter (`pivot=N`) would have needed a search per length, and one
fixed length would have left the tree a pivot that either retreats nowhere or always
retreats the most.

**Opt-in.** A search with no `moves=` or `then=` keeps the action set it had: the 26 are
offered (`moves_for`, where the fighter's state allows them) only when a prefix names
them. Ranking 22 more moves at every branch point on the ground took half again as long
(41 to 63 trials, 1,732 to 2,533 frames for Falcon next to a Fox), and a budgeted search
lost its depth: with a 4,000-frame budget the grab no longer got a deeper look for its
throws (`tests/native/engine.py`), and `behave.Punish`'s 2,500 would go on the first
ranking alone. A prefix reaches everything it matches: `dash_` now names `dash_grab`
and `dash_dance` too (as `opponent.py`'s default moves and `tests/native/shadow.py`'s
list do), `jump` names `jump_in` and `jump_out`, `waveland` the three wavelands.

**Proof.** `tests/native/engine_moves.py` (43 checks, headless, 25 s): each move played
as the search plays it and then for real, the game's own states checked, for Fox, Marth,
Sheik, Captain Falcon, Peach and Jigglypuff (the pivots also for Mewtwo, Game & Watch
and Bowser, the characters the pivot drill measured): every pivot is a dash out, the
turn, and the attack on the next frame facing the target, with no dash back or run, the
long one on the dash's last frame (held one frame more, it runs); the flick held a second
frame is a dash back; out of a dash forward the short pivot flicks after 4 frames, and a
frame earlier the flick does nothing; the dash grab is a dash grab from standing, a dash
and a run; the jump-cancelled grab and up smash a standing grab and up smash out of the
jump squat, on the ground, sliding; the boost grab a dash attack into a dash grab; the
dash dance a dash out and one back; the crouch a crouch on the stage and on a platform;
the platform drop through it; each waveland in its landing lag on the platform, sliding
in, out or not, and after a drop on the stage below. The search with them: `moves=pivot_`
against a standing Fox 10 units away finds 5 to 12 of the 16 pivots that hit (the best
played for real does the damage it was scored with), and the scan finds every dash
length from which a pivot forward smash hits (Fox 0 to 12 frames, Marth 0 to 15).
Marth on Fox at 0% (depth 4, `moves=grab`, `then=` the throws, `wait` and the four
grabs): five lines regrab as searched; replayed with Fox pressing a jump button on every
frame from the throw's release, only `grab+uthrow+grab` still regrabs before he can act
(the release on frame 18, the regrab on 49, 3 frames of his hitstun left); the forward
throw's regrabs catch him in his jump squat.

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
- 2026-11-15: layer 1 built and proved: the 26 moves above (pivots into the eight
  attacks at two dash lengths and every length by the scan, dash, jump-cancelled and
  boost grabs, dash dance, crouch, platform drop, three wavelands; regrabs after
  throws), opt-in by name; `tests/native/engine_moves.py` 43 of 43, `engine.py` 17 of
  17, `ahead.py` 12 of 12.
