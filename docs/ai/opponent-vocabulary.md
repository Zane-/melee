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

(The recovering opponent's routes are not macros: `recover.py` writes each as pads and
has the game play it ahead, `route` in `src/host/ahead.c`. Its table of what each
character recovers with is `recover.TOOLS`.)

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
| `sh_nair_out` `sh_fair_out` `sh_bair_out` `sh_uair_out` `sh_dair_out` | a short hop with the stick held away from the target from the jump on, the aerial on the first airborne frame as the other short hops': a spaced aerial, which hits the front of a shield and drifts back where a dash in and a short hop drifting in or not carry the fighter through it (Marth's nair, fair and dair crossed from every spacing) | offered on the ground; "sh_" names them too (as "dash_" names `dash_grab`). Against a shielding Fox from 15 to 35 units, `front=4` dropping none: Marth's nair, fair, dair and uair, Samus's nair, fair and uair, all five of Pikachu's, Falcon's nair, fair, dair and uair at 15. A spaced aerial is often safe from the frame-4 shine out of shield (Marth's are) |
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
so the opponent cannot answer what it could not have seen: `Sense` keeps the last
`react` + 3 frames' states and reads the player on the one `react` frames ago, the
opponent itself on this one. Most are pure functions of states (`holds(cond, view)`); the
ranges and the lag are found by the game (below), every `cache` frames (4), all in one
job: in a forked copy of the game while a person plays, in the game itself headless; what
they found is kept by the frame it was found on and read on the frame the condition is.

| Condition | True when |
|-|-|
| `{"distance": [LO, HI]}` | the fighters are that far apart (units, along the stage) |
| `"in_their_range"`, `"out_of_their_range"` | the player can (cannot) hit the opponent within `frames` (12) with any move: searched from the player's side, as an answer is (`contracts.Answer`), cached a few frames. Built: `sense.reach`, the timing scan from standing or a dash toward (every ground attack and special, the grab, a dash attack, short hops with each aerial; pressed within 38 units, every 3 frames), the opponent doing what its behaviour plans; unknown before the first search (then neither in nor out) |
| `"in_my_range"`, `"out_of_my_range"` | the same from the opponent's side |
| `"approach"` | the player closes in: dashing, running, walking or jumping toward, or the gap shrinking by more than a unit a frame (built: by the player's own movement, so the opponent's own dash in is not their approach) |
| `"retreat"` | the player moves away |
| `"committed"` | the player cannot act: an attack, landing lag, shield stun, a roll or dodge, hitstun, tumble, lying down, grabbed (built: any state but moving about, a jump squat, a crouch, a shield, the ledge's wait; or frozen in hitlag. A move's interruptible frames count as committed until it ends) |
| `"free"` | (built beside the scope) the opposite: the player can act |
| `{"state": NAME}` | the player in a state of the drill format's names (`STATES`) |
| `"shielding"`, `{"shield_below": H}` | the player shields; its health under H |
| `"airborne"`, `"grounded"` | the player in the air, on the floor |
| `"on_ledge"`, `"offstage"`, `"on_platform"` | where the player is |
| `{"percent": [LO, HI]}` | the player's damage |
| `{"lag": N}` | the player can act no sooner than N frames from now (an opening). Built: the commitment seen (`react` late) and at least N frames left now, played ahead in the game with the player letting go (`sense.lag_of`) |
| `{"me": CONDITION}` | the same, of the opponent itself, seen at once |
| `{"not": C}`, `{"any": [...]}`, `{"all": [...]}` | combinations |
| `{"after": N}` | N frames into the behaviour (in an `if` or a `while`: since the innermost repeat began, or the script) |

## 3. Behaviours (`behave.py`)

A behaviour moves the opponent frame by frame until its condition (`"until"`), its time
(`"for"` frames) or its own end (an attack's contact). Each is a body (pads planned some
frames ahead, as `Footsies` is) or a decision the engine searches in a fork, as
`EngineOpponent` does now.

| Behaviour | What it does |
|-|-|
| `footsies` `range` | dash dances turned inside each character's initial dash, pivots, let-go dashes, walks in, crouches, standing, wavedashes in and out, a shield now and then, never a run turned around (the body: `footwork.py`), keeping to a band: `"outside"` (just out of the player's range), `"edge"` (at the edge of its own), or `[LO, HI]`. Built: `"outside"` looks at each segment it plans before playing it, and every 4 frames: the player's range over 16 frames (12 and the 4 between looks) as it plans to move; one that would take it in is dropped for a retreat (the body's: a dash away and a pivot, the dash it is in turned, or a wavedash out; never closer, back to the band, facing the player again). Its band follows the reach found (up to the closest a rejected plan came, sinking slowly while none is), kept for the next behaviour (`ctx.memory`). `"edge"`: a first version, the same with its own range. The band is kept through each phrase, not only where it ends (2026-11-15, `footwork.py`): every frame of a candidate more than 3 units out of the band counts against it, one more than 4.5 inside its low end refuses it, dash legs are no longer than the band and its slack are wide, and the target it keeps to is its x eased (12% a frame: a dash dance in place is not chased leg by leg); played on, the plan is made again when the eased target is 1.5 units inside the band or 3 beyond it, or the target itself 6 inside (never in a wavedash under way). Measured with `gait.py --body footsies --standin stand,dance` (band 28 to 42) |
| `hold` `pad` | stands, shields, crouches (`"stand"`, `"shield"`, `"crouch"`) |
| `retreat` | moves out of the player's range and stays there (built: `"outside"` with 12 units more) |
| `approach` `moves` `lands` | commits to one of `moves` (by name prefix) that the engine finds lands (`"hit"`, `"shield"`, `"any"`), from wherever it is; with a contract (below) only one the player can answer. Built: `EngineOpponent` with the contract `behave.Commit`: the timing scan, the stick held K frames (still, toward, walking toward) then one of `moves`, on a shielding player as shielding on, any other as stopping; `body` (footsies closing in, or stand, shield, crouch) until then, `wait` [LO, HI] frames before it may. `front` (true by default when `lands` is "shield"; `false` for a drill that wants cross-ups): only a line whose fighter stays on the player's side it came from, from its start until its move is over (it can act again, or it hit in the air and has landed) and the frame the contract's answer out of the shield hits, whichever is later: the front of the shield, no cross-up, no attack sliding or drifting through (the engine's `front=`, `within` its frames). `pick` ("variety" by default; "best"): the attack's families (nair, fair, ftilt, fsmash, dash_attack, side_b...: `behave.family`, the last move without its hop, drift or pivot) drawn into a queue at random, by `weights` ({FAMILY: W}, 1 each by default) divided by one more than the times each was attacked with in the last 8, the last two it attacked with at its end (all of it kept from one attempt to the next by the drill; an attempt replayed with its seed starts from the same memory); each look searches the next 3 of the queue, their moves alone, and commits to the first of them, in the queue's order, one of whose two best lines (the softmax) the contract answers; while patient (90 frames) a family it attacked with twice in the last 8 waits (a dash attack, answered from anywhere, was otherwise most of them); a family that lands and is not answered is drawn later and later (halved each time, to a sixteenth) until it is answered once. "best": one of the best lines of all by the softmax over their scores, in which a forward smash's damage or a dash attack's reach wins |
| `move` `name` | plays one named move exactly (a scripted moment); facing away from the target (a footsies leg out), a ground attack with a pivot is played as `pivot_<name>` |
| `punish` | plays to win from here until the player can act again: the best combo the engine finds (built: each move two deep, for damage, a kill and hitstun left, one of the best by a softmax; `moves` limits the first) |
| `pressure` | attacks the shield with options that are safe on it, until the shield breaks or the player acts (a first version: each option's safety is the player's out-of-shield grab, up smash, shine and up-B searched as its stun ends; none safe, a dash back) |
| `chase` | waits for the player's tech, getup or ledge option (seen `react` late) and covers it (a first version: standing until it is seen, then the punish's search) |
| `chain_grab` `throw` | grab, the throw, a regrab while the engine finds one that lands before the player can act (built: `regrab` prefixes, `grab,dash_grab,pivot_grab,jc_grab` by default; a regrab connects before the player's first frame free or on the ground, played ahead with them letting go, and within 40 frames of the throw; a knockdown or a tech ends it: `chase`'s. A regrab searched against a player jumping out caught that jump, or a flight its stick's DI changed) |
| `recover` | off the stage, the way back the game says works against what the player is doing (built 2026-11-17, `recover.py`; `melee-engine.md`, "Recovering"): the routes its character has from where it is (its jumps left, its specials, their angles and timings: `recover.TOOLS`) played ahead in the game (`route`), scored (the ledge or the stage reached, a landing's lag near the player, how long it flies with nothing left to change, what the player could cover from where they are: `threats`), one of the best taken by a softmax, the kinds flown lately less often; checked again every 4 frames as it flies, decided again when it no longer ends well, and `react` frames after the player commits to something new (a jump, a drop, an attack, the ledge taken). Over on the ledge, standing on the stage, or lost (`ended`); at once if it stands on the stage already. `to` ("ledge", "stage"): it only goes there; `tools` (jump, float, up_b, side_b, down_b, airdodge): the only ones its routes use; `adapt` false: it flies the route it first chose; `predict` false: only what the player is doing counts, not what they could do; `budget`: routes a decision plays ahead (48) |
| `edgeguard` | off the stage, against a recovering player (later: not built, and a script naming it is refused) |
| `play` | moves as a person does (the slippi-ai body where a model exists, `footsies` otherwise; a first version: footsies in [25, 60], the model's body not wired in) |

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
commits (`contracts.Answer`), as fox-anti-air's jump-in does. `within`: frames from the
first frame the player can answer by which the answer hits, that frame 1: a shielding
player out of the shield the frame its stun is over (found by playing the option ahead;
`{"answer": "oos_down_b", "within": 4}`: the frame-4 shine out of shield hits), any other
no sooner than `react` frames after the commitment and before the option lands. The
answer is searched with the opponent letting go after its line, as it plays it. Up to four
of the best lines are looked at each time; the first answered is committed to, and the
player's answer is kept with it (`Approach.answer`: the frame asked at, its pads), as the
check and the demonstration play it. On a shield the line is also on its front (`front`,
the default): the opponent never past the player before its move is over and the
answer would hit, the frames after the line's end played letting go, as it plays them; a
line that would cross up or overshoot is not one of those looked at. The line is kept
while the player does what the
decision assumed (a shield held: the game it foresaw is then the game played); when they
do something else, seen after the opponent's reaction time, it reacts: a line not begun is
dropped, one begun is checked again and kept, replaced by another answered line, or given
up before its decisive press (`melee-engine.md`, "How it feels live"). That is what makes a drill
fair: the situation happens if the player does nothing, an answer exists, wrong answers
lose.

**Determinism.** A script's random choices come from the drill's seed: `check.py` replays
a drill's examples and mistakes against the same opponent, and the coach's demonstration
plays what the check found.

## Status

- 2026-11-17: `recover` built, for the edgeguard drill (`fox-edgeguard`). The owner: the
  drill "should be able to predict and adapt to the players edgeguard. For example for
  fox, if it is firefox angling, and right before the angle is locked in the player
  starts to drop and go for a bair to cover the ledge, the CPU could change angle to go
  high", with "options for reaction time of the engine so the player can essentially
  choose their own difficulty". What it is, how it was measured and what it does not do
  yet: `melee-engine.md`, "Recovering". With it: the host's `launch` (the game's own
  knockback, an edgeguard's start), `route` (a way back played ahead to where it is
  decided) and `hitboxes` (where a fighter's hitboxes would be); a forked game may fork
  (a decision plays its routes side by side in copies of its copy); the drill format's
  `launch`, `example`, `they_die`, `they_ledge`, `they_return` and the player's CPU
  reaction setting (`drill-format.md`). Proof: `tests/engine/recover.py` (15 of 15),
  `tools/melee_engine/recoveries.py` (the measurements), `fox-edgeguard`'s `check.py`
  (36 of 36), `tests/client/edgeguard.py` (12 of 12).

- 2026-11-15: an approach on the shield hits its front, and attacks with every family
  it has. The owner, playing fox-shine-oos: "the CPU often overshoots on the shield hit
  which is very very hard to punish with shine OoS, we need to make sure that the front
  of the shield is hit!", and "sheik just repeatedly fsmashes, should throw in tilts,
  fair, nair, etc. so it feels like a random attack". Measured (`feel.py`, the drill's
  part 3 against a shielding stand-in, 40 attempts a character headless and 20 live in
  the window build): no contact was from behind before either (1 of 440), but the
  opponent passed the player before the frame a frame-4 shine out of shield hits in 59 of
  440 commitments headless (31 of 218 live), and before its own landing or end in 138
  (70 live; headless Falcon 17 of 40, Pikachu 20, Peach 18): aerials drifting through,
  dash attacks sliding past. The family committed to was most often a dash attack, 20 to
  48% of the time headless (Marth live 55%), with 4 to 11 families a character. Now: the engine's `front=N`
  (`melee-engine.md`), `approach`'s `front` (the default on a shield), the short hops
  drifting out (spaced aerials), and `pick: "variety"` (the default), the deck's scripts
  one approach each naming every attack, from footsies out of reach or close in. After:
  never past the player before its landing or end and the shine's frame, headless 0 of 440,
  live 0 of 218; landed 440 of 440 and 218 of 218; the shine out of shield still answers
  every one (the frame-4 stand-in won 220 of 220 headless); 5 to 10 families a character
  (Peach 5: the frame-4 shine answers only her jab, dash attack, forward and back air on
  the front of the shield, and a down tilt now and then), the most common at most 22%
  headless but Peach's dash attack (38%), live at most 30% but Jigglypuff's (35%) and
  Peach's (42%) dash attack. The
  cost: live, the commitment comes later (median 47 to 172 frames from the approach's
  start, 37 to 64 before) while a family used twice in the last 8 waits for the others.
  Families lost to `front` (the frame-4 shine answers them only from behind or through
  the shield, from every spacing tried): Marth's nair, fair and dair; Falcon's forward
  smash, bair, uair and down-B; Peach's nair; Pikachu's side-B; Yoshi's uair and dair;
  Samus's fair and uair. `melee-engine.md`, "The front of the shield", has the numbers.

- 2026-11-15: an approach's committed attacks land on a shielding player live: 218 of 218
  across the deck (90% before), headless 220 of 220, every contact on the frame foreseen
  (`tools/melee_engine/feel.py`; the causes and the numbers in `melee-engine.md`, "How it
  feels live"): one commitment at a time, the infinite shield kept by the game in searches
  too, the body held to the pads a decision was made with, a reaction to the player
  leaving what a decision assumed, and a held dash that never runs, turns round past the
  player or reaches the ledge (the scan's `norun=1`).

- 2026-11-15: this scope written. Built before it: the layer-1 moves listed as built,
  `Footsies`, `Hold`, `EngineOpponent` and the `JumpIn` contract (`melee-engine.md`).
- 2026-11-15: layer 1 built and proved: the 26 moves above (pivots into the eight
  attacks at two dash lengths and every length by the scan, dash, jump-cancelled and
  boost grabs, dash dance, crouch, platform drop, three wavelands; regrabs after
  throws), opt-in by name; `tests/native/engine_moves.py` 43 of 43, `engine.py` 17 of
  17, `ahead.py` 12 of 12.
- 2026-11-15: the engine on the first frame the game reads an input (`engine.c`):
  a state that ends with its animation (shield stun, landing lag, a jump squat, an
  attack, a grab) ends in `Fighter_procAnim`, before `Fighter_procInput` reads the
  frame's input in the state it ended into, so the engine offers its next moves at a
  branch point whose coming frame ends it (a frame played ahead and undone: `moves_for`),
  settles a move followed by another on the frame before its fighter can act
  (`settle_xy`, `eng.exact`), counts a normal landing's lag as over at its landing lag,
  not at its animation's end (Fox's jab after a short hop: frame 4, not 30), and presses
  a short hop's aerial, a wavedash's air dodge and the shine out of shield on the first
  airborne frame, J + 1 (`squat_ends`). Before, `oos_down_b` was a frame-6 shine out of
  shield (the jump a frame late, down-B a frame late) and a contract `within` 5 committed
  to options only a frame-6 shine answered. `stun_over`'s callers hold the shield the
  frames before the first free one, not through it. An answer was searched with the
  opponent's last pad held on after its line (an Ice Climbers' aerial's drift went on in
  the search; for real they let go, landed elsewhere, and the frame-4 shine missed). Proof:
  `tests/native/engine_first_frame.py` (31 of 31: shield stun, landing lag, a jump squat,
  a whiffed grab, a forward tilt, for Fox, Marth, Peach, Falcon: the first frame a real
  input works is the first the engine offers it; the macros on J + 1; the contract within
  4 answered by its frame-4 shine, played). Not covered: the shield's drop (GuardOff), in
  which the game reads X or Y and down, is still waiting to the engine.
- 2026-11-15: layers 2 to 4 built. `tools/melee_engine/sense.py` (every condition of the
  table, and `free`), `behave.py` (`hold`, `footsies`, `retreat`, `approach`, `move`,
  `punish`, `chain_grab`; first versions of `pressure`, `chase`, `play`, footsies'
  `"edge"`; `edgeguard` and `recover` not built), `script.py` (do, if, mix, repeat, loop;
  seeded; at most 32 steps begun in a frame, and a repeat that begins nothing stops, so a
  script cannot hang a frame). A scenario's `"opponent": {"script"}` is checked by
  `format.py`, played by `JsonDrill`, proved by `check.py` (which takes a drill file's
  path). A script names moves by prefix: today's and the scope's, which a search finds
  once the engine it runs on has them. `tests/engine/sense.py` 24 of 24,
  `tests/engine/script.py` 20 of 20 (the interpreter alone, then footsies, `until`,
  approach on a shield, the shine out of shield contract played, punish, chain grab, the
  same seed, decisions in forks at 60 frames a second, an approach with pivots), the 27
  drills' `check.py` all passing. Found on the way: once port 1 had attacked for real (a
  match started with A held is a jab), the engine's searches never saw its grab again in
  that process (a real Z still grabbed). Fixed the same day: the game's interrupt flag
  (`Fighter.allow_interrupt`) is cleared only as an attack begins and read only by the
  attacks, so it stays set in every state after one, a new match's fighter too; the
  engine read it as "can act" everywhere, and a grab ended on its second frame. It now
  counts it only where the game reads it (`follow_interrupt`, `engine.c`); the chain
  grab's test plays in the shared game again, `tests/native/engine.py` checks a grab
  after a real jab.
- 2026-11-15: the body, after the owner played fox-shine-oos ("the sheik is just
  missing dash dances and in turn around lag"). The cause, measured
  (`tools/melee_engine/gait.py`): the old body held dashes 3 to 9 frames, walked at a
  stick of 70 and dashed again the same way in a dash's slide. The game reads the stick
  over 80: 64 is a dash, so its walks were dashes; held past a character's initial dash
  (Sheik 7 frames, Samus 8, Fox 11) or pressed again in its slide (50 or more), a dash
  is a run, and a run let go is RunBrake, turned TurnRun (Marth's up to 51 frames). The
  first 4 frames of a dash from standing ignore a turn, and a turn pressed on its 2nd or
  3rd frame is lost. TurnRun, RunBrake and Run were 9 to 47% of the body's frames for
  the eleven top characters; over fox-shine-oos's whole script, 156 to 468 frames in
  30 seconds. Now `tools/melee_engine/footwork.py`: phrases (a dash dance of 2 to 5
  dashes at a rhythm drawn for it, a dash let go of, a pivot, a walk in, a crouch,
  standing, a wavedash in or out, a shield) each played on a model of the game's ground
  movement (each character's initial dash, dash animation, jump squat, wavedash slide
  and lag, pivot, speeds and friction, measured by `gait.py --calibrate` into
  `footwork.json`), kept only if it never runs, turns where the game ignores it,
  crosses the player or leaves the stage, one of the best by where it ends (the band,
  facing the player) by a softmax. A turn comes from a dash's 5th frame (a dash back's
  2nd) to its last before the run. The plan's positions follow the game's each frame
  (0.1 units off a frame on average); a state the plan did not expect is planned again
  from the game. `footsies` `"outside"` retreats with the body's retreat. After
  (`gait.py`, 1,200 frames a run, stand-ins standing, shielding, moving): no TurnRun,
  RunBrake or Run in the body's frames for any of the eleven, alone or in the drill's
  script (the committed lines' own holds still run and turn: 0 to 34 frames in 30
  seconds, `Commit`'s; before, 156 to 468 in all); 3.5 to 5.2 dash backs a second
  (before 0.5 to 1.7); in its band 46 to 76% of the time against a standing or
  shielding player (before 27 to 50%); facing the player 68 to 77% of the time (before
  51 to 56%); the model a tenth of a unit off a frame; 0.03 ms a frame (at most 2).
  The slippi-ai body (`human.ModelBody`, its attacks taken out; models for all eleven
  against Fox, Falcon's and Fox's dittos): measured for Sheik, Marth, Fox, Falco and
  Jigglypuff, it jumps 20 to 73% of its frames (its aerials taken out), dash backs at
  most 1.3 a second, keeps no band (Sheik against a standing Fox stood still 79% of the
  time, 80 units away) and still runs into RunBrake now and then; not used for footsies.
  Proof: `gait.py`, `tests/engine/script.py`, `tests/engine/sense.py`, every drill's
  `check.py`.
