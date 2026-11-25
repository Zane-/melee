# The drill format

The owner, 2026-11-14: "In my mind a drill consists of a goal, scenarios with actor scripts
(what the CPU should do per scenario), success/failure conditions, coach configuration, and
a step that plays on first open that shows what the drill is, how it works, what to expect
... upon open we should show an example and allow the player to see frame by frame with the
input overlay. We should decompose tech into chains of actions as well ... instead of just
jumping to the entire thing (this is the 'now draw the entire owl' problem). All of this
should be well-defined in a drill so we can easily generate new drills from descriptions."
Then: a drill is JSON; "tutorial and coach are different. Tutorial should show HOW to do the
tech, coach pops up when you mess up to help show you what you did wrong and how to fix
it"; and a drill says whether a CPU is spawned and how the camera behaves ("for shorthop,
there is no CPU needed here and the camera should track the player but be zoomed out a
little bit so it doesn't feel jarring").

The old drills were wiped (2026-11-14) and are rebuilt in this format. Done (2026-11-14):
Tech skill, all three subcourses: Movement (short hop, fast fall, dash dance, wavedash,
waveland, pivot, ledgedash), Fundamentals (L-cancel, SHFFL, jump-cancel grab and up smash,
DI, SDI, ASDI, shield drop, edge cancel, slide off) and Fox's Character (waveshine, shine
grab, SHFFL shine and shine grab, jump-cancel shine, multishine, shortened Illusion, Firefox
angles, ledge stall, double laser), each passing `check.py`; the owner's QA is next.
Punish (2026-11-15): Fox's shine out of shield (`fox-shine-oos`), the first drill whose
opponent is a script of the engine's vocabulary (`opponent-vocabulary.md`): a deck of the
2021 tier list's top 11, each approaching the shield held to the shine out of shield
contract, on the front of the shield (never crossing up or overshooting), its attack drawn
from every family it has that the frame-4 shine answers (2026-11-15).
Neutral (2026-11-15): Fox's whiff punish (`fox-whiff-punish`): the same eleven, each
standing until the player comes within its reach and 8 units more (seen 15 frames late),
then one of the attacks of its own that a jump-cancelled grab punishes from where it
misses; the attempt runs from its attack's first frame (`their_attack`) to the grab, a
hit, or the opponent free again (`they_recover`: too late).
Punish (2026-11-17): Fox's edgeguard (`fox-edgeguard`): the same eleven, each knocked off
the stage by a hit drawn for the attempt (`launch`) and getting back onto it by the
engine's `recover` (`melee-engine.md`, "Recovering"): its routes played ahead in the
game, one of the best taken, another when it sees what the player commits to, its
reaction time after they do; by the ledge and up from it, after every hit, with stalls
and late timings. A try runs until its stock is gone or it stands on the stage again. The reaction time is the player's to set (CPU reaction, in the pause menu and
Settings), for this and every drill whose opponent is a script.
Defense (2026-11-24): Fox's escape from the tech chase (`fox-escape-techchase`): the
same eleven, each with the throw of its own that leaves Fox in hitstun until the floor
(the down throw of Fox, Sheik, Captain Falcon, Peach, the Ice Climbers, Pikachu and
Samus; the forward throw of Marth and Jigglypuff at 30%, Falco at 55% and Yoshi at 90%:
measured, `tests/engine/chase.py`), chasing by the engine's `chase` (`melee-engine.md`,
"Answers ready before the player chooses"): its answers to each of Fox's options worked
out before he chooses. Every try begins in the opponent's grab (the player's `held`) and
runs from the throw's first frame to the cover that lands, or `END` frames untouched.
The rest of the queue (2026-11-25, built overnight at the owner's word, each passing
`check.py` and opened in the client by `tests/client/drill_smoke.py`; none played by the
owner yet, and each course row says what its drill leaves out). Defense: escape the chain
grab (`fox-escape-chaingrab`), shine out of combos (`fox-combo-shine`), get off the ledge
(`fox-ledgedash-attack`: an opponent by the ledge that punishes what it sees). Punish: waveshine
to up smash (`fox-waveshine-usmash`: the frames with the hit's freeze), up throw up air
(`fox-uthrow-uair`) and kill confirms (`fox-kill-confirm`): the follow-ups searched in the
game for each opponent, percent and DI, the opponent jumping away the frame its hitstun
ends; chain grab fast fallers (`fox-uthrow-chaingrab`: the regrabs searched the same way);
aerial hit confirm (`fox-aerial-confirm`: it takes the hit or crouch cancels it, shown only
at the hit); shield pressure (`fox-shield-pressure`: a shield that grabs on its first free
frame); shine knockdown (`fox-shine-knockdown`: an opponent that techs in place, toward
Fox, away, or misses, the follow-up for each searched in the game). Neutral: take it on shield (`fox-shield-then-punish`: an attack or a grab), read
the stance (`fox-approach-nair-dair`), running shine (`fox-running-shine`), anti-air
(`fox-anti-air`), wavedash back punish (`fox-wavedash-back-punish`), lasers force the
approach (`fox-laser-forcing`), beat crouch cancel (`fox-vs-crouch-cancel`): every row of
the Neutral part. New for them: the events
`shield_hit`, the states `throw` and `up_throw`, `"shield": "theirs"`; the opponent's
`oos`, `jump`, `tech`, `hold` with a `stick`, `move` with `"lcancel": false`, the
condition `stunned` (`opponent-vocabulary.md`); the knockback's speed in a fighter's state
(`kvx`, `kvy`: where a hit will send it, known through its freeze);
a check that asks for something only in some scenarios compares a measure to a scenario's
number (`"at_least": "NEED"`, NEED 1 or 0), and an example input is left out of a scenario
by a frame number that never comes (999). Not built (six rows; each says in
`data/courses/fox.md` what it needs): `fox-oos-choice` (out-of-shield answers the engine
does not have as moves, and a contract that rules an answer out), `fox-shine-spike` and
`fox-edgeguard-onstage` (an example found off the stage against each recovery),
`fox-escape-pressure` (the engine's `pressure` leaves 15 to 40 frames between hits: a
scripted string needs its own measurements), `universal-wall-tech` (the player launched at
a wall), `fox-recovery-mixup` (no `edgeguard` behaviour).
From play (2026-11-25, the owner: "Every drill is supposed to feel realistic, not just
robotic spawn and do something (except things like up throw kill confirm that are a
specific action"): a drill's situation arises as it does in a match. The opponent begins
at a distance and moves, and a try begins at the event the technique answers (its attack
hitting the player, the player's shine hitting it), not with the opponent placed next to
the player doing one thing. Rebuilt so: `universal-crouch-cancel` (25 attacks of nine
opponents, another every try: the opponent keeps out of reach and attacks when the player
comes in, at once or a moment later, or comes in itself; the player's damage drawn for
each try up to that attack's measured limit for the character played,
`data/actor/crouch_cancel.json`; an opponent knocked down beside the player that gets up
with an attack; six of the attacks at a damage where crouching no longer holds),
`fox-waveshine-usmash` and `fox-shine-knockdown` (the opponent moves
about 50 units away; the try begins when the shine hits), `fox-shield-pressure`,
`fox-vs-crouch-cancel`, `fox-aerial-confirm` and `fox-approach-nair-dair` (the opponent
moves about and shields, crouches or stands when Fox comes within 40 units, and moves
again when he backs away; each example walks up to it and stops where its sequence was
measured), and, where the technique answers an attack, the opponent comes to the
player: `fox-wavedash-back-punish`, `fox-combo-shine`, `universal-asdi`, `universal-di`
and `universal-sdi` (it plays footsies past its distance for a time drawn each try, comes
to the distance its attack was measured from and attacks, then plays footsies again: how
it comes in is "Every run its own seed" below; in a demonstration it walks up, stands
exactly there and attacks. `universal-sdi`'s three down airs were measured with the
attacker placed on top of the player and pushed apart by the game, so it walks into the
player, stands while the game pushes them apart the same way, and jumps),
`fox-ledgedash-attack` (the opponent waiting by the ledge moves
about). Left as they are, and why: `fox-uthrow-uair`, `fox-uthrow-chaingrab` and
`fox-kill-confirm` (the owner's exception: "things like up throw kill confirm that are a
specific action"; the opponent stands next to Fox to be grabbed), `universal-tech`,
`fox-escape-techchase` and `fox-escape-chaingrab` (a try begins inside the opponent's
grab), `fox-edgeguard` (it begins with the opponent knocked off the stage). New for them: an opponent's
`"knockdown"`, the script step `press` (inputs by frame: the attack a drill was measured
against, played from where the opponent stands), the engine's move `run_attack` (a dash attack from standing), Yoshi's egg
seen as a shield by the engine's search (`in_shield`, `src/host/engine.c`: an opponent
asked for a move that lands on a shield never attacked a shielding Yoshi),
`tests/client/drill_smoke.py --come D` (a stand-in that walks up to the opponent before
its keys), an event's `"close": D` (a jump starts a try only next to the opponent), the
event `they_enter` and a check bound that names a measure (a try judged by what a moving
opponent did when it was hit, not by which scenario it was), and `footsies` with
`"crouch": false`. A drill that was measured with the opponent placed keeps its
measurements: in a demonstration the opponent stands still until the player comes in,
and the example stops at the measured distance (the proofs showed how narrow some are:
the down air into shine on a crouching opponent holds at 9.0 units and not at 8.95 or
9.05; a character's idle sway can put a hit a frame later, so an attacker stands a
little longer first in three scenarios). Each course row says what its drill still
leaves out.
Proved in play too (2026-11-25): `check_play.py` showed that a measured answer does not
survive an opponent that attacks from wherever the engine's `approach` lands its move (a
jab from its full reach, where Fox's shine does not reach back; a dash attack from so
near that it runs through the player), nor one begun facing away (`move` then plays it
with a pivot) or after a walk ended by a condition seen `react` frames late. So an
opponent with a measured attack keeps out of reach in footsies, turns to face the player
(`{"me": "facing"}`), walks the last steps in to the measured distance by where both
stand now (`hold` with `"near"`) and attacks out of the walk: `universal-crouch-cancel`
(1237 of 1300 runs right over all 26 characters; 75 of 75 for Fox) and `fox-combo-shine`
(33 strings of ten opponents, each at a low and a high damage of Fox's; 252 of 252).

Every run its own seed, and what that showed (2026-11-25): `check_play.py` had been
replaying one run. A demonstration takes the last try's seed, so its "several runs a
scenario" were the same run several times, and the walk-in above had been proved for one
draw of each scenario (the counts above are of those). Seeded, it was loose: `footsies`
can end with the opponent anywhere and at any speed. A dash held on at the walk's stick
is a run, whose brake slides it in under its distance; a walk begun inside the last steps
lets go slower and attacks from farther (over eight seeded tries: Sheik's jab from 1.4
units instead of 10, Marth's down tilt from 11.2 and 18.4 instead of 16; in
`fox-wavedash-back-punish` Marth's down air caught the correct wavedash 3 runs of 4). The
step-in of `universal-asdi`, `universal-di`, `universal-sdi` and
`fox-wavedash-back-punish` now: what footsies left it doing ends (`hold` standing,
`"until": {"me": {"state": "wait"}}`); a step back if it is nearer than where its last
steps begin (`hold` with `"far"`); the turn to face the player; a walk up, the last 8
units slowly (stick 0.25: whatever speed it came with is gone by their end, so it lets
go at the same speed every time); a stop of 6 to 10 frames; the attack. Where it lets go
is calibrated per scenario on the distance at the hit, not at the attack's start (an
attack out of a walk slides on). The hit then comes from within about half a unit of the
measured distance (Captain Falcon's forward smash, measured from the edge of its reach,
comes 1 unit nearer: 0.3 units farther its first frames missed and it hit late, from 1
unit instead of 6.6). Played so by all 26 characters, 3 seeded runs a scenario:
`universal-asdi` 780 of 780 in each of its two judged parts, `universal-di` 1092 of 1092
in each, `universal-sdi` 312 of 312 in each; `fox-wavedash-back-punish`, 5 runs a
scenario: 110 of 110 and 109 of 110 (82 and 79 of 88 with the earlier walk-in).
`universal-crouch-cancel` and `fox-combo-shine` keep the earlier walk-in; seeded, 4 runs a
scenario, Fox: crouch cancel 100 of 100, 24 of 24 and 94 of 100 (its getup part 20 of 28
counted: one knocked-down opponent in five only stands up, as the part says), combo shine
334 of 336 in both parts.

Counted from the hit (2026-11-25): the tutorial numbers an example's frames from the
try's start (frame 1 is the frame the attempt's `start` holds on), and marks, cues and
the coach's rows are keyed by those numbers; an input without `"from"` counts from the
demonstration's first frame. The two agree only where the try starts on the
demonstration's own first input. `universal-asdi`, `universal-di` and `universal-sdi`
start on a hit and keyed everything by the demonstration's frames (the hit on frame
`HIT`): once the opponent walked in, their captions were never shown (frame 96 of a try
judged on frame 30) and their lessons pressed long before the hit (the C-stick on frame 6
with the opponent 55 units away). They are counted from the hit now: every input
`"from": "start"`, every mark and cue from frame 1, `HIT` gone. A drill whose try starts
on what the opponent does times its inputs from an event.

Lessons proved (2026-11-25): `check.py` did not prove a lesson's example, and the client
recorded it on whichever scenario the session's deck drew: the pictures were of that
entry's opponent under the lesson's own script, numbers and captions (`universal-asdi`'s
first lesson, Sheik's down tilt, played by Falco: his freezes 7 frames, the lesson held
the C-stick for Sheik's 5 and showed a miss; all six lessons of the three drills showed a
miss). A recording is now played on the deck entry of the scenario it shows
(`JsonDrill.shown_entry`: a lesson's own, also where the part now does not have that
scenario: crouch cancel's lessons of the floor were Marth under Fox's captions; a part
card's the one whose numbers its words use). Before a part's card a deck not yet turned
draws the scenario the first try will be (`Client.first_scenario`), so the card shows
that one, as before, now with its own numbers and words. A lesson may name the checks
its example passes (`"checks"`), `check.py` proves them in the lesson's own scenario for
every character, and `tests/client/drill_smoke.py` checks that each card's pictures are
of the opponent of the scenario the card is about.

The damage drawn (2026-11-25): in the three universal drills the player's damage is
drawn for each try inside what `python tools/melee_drills/percent_range.py DRILL`
measured, per scenario and character, as the range in which the last part's example
holds. `universal-asdi`: from 0 to 3% under the most at which the example still lands at
once (Sheik's down tilt to 36% for Fox, 31% for Pichu, 48% for Bowser; Falco's down tilt
to 5%; the jabs to 100%, where the range is cut off); the same limits as
`cc_limits.py --asdi` measured apart from the drill (`data/actor/asdi_down.json`).
From that table the drill has 14 more attacks, 24 of ten opponents (all of the top 11
but the Ice Climbers, whose partner hits after the first): each lifts every character at
0% when nothing is held (Fox's and Falco's forward tilts do not: nothing to ASDI down)
and freezes every character as long.
`universal-di`: 20% either side of the damage each attack was built at, proved at both
ends. `universal-sdi`: from 0 to 21% (Pikachu's down smash against Fox) up to 60%, every
percent tried (`--step 1`): which hits of a multi-hit attack connect changes from one
damage to the next, and a binary search had put Falco's top against Jigglypuff's down air
at 45% or more where it first fails at 43%. `check.py`, every character, lessons included:
`universal-asdi` 5148 of 5148 cases, `universal-di` 2704 of 2704 (and as many
with every damage at its low end), `universal-sdi` 650 of 650,
`fox-wavedash-back-punish` 93 of 93.

## Where things are

| | |
|-|-|
| A drill | `data/drills/<id>.json`: nothing but the words below |
| The words, the checking of a file | `tools/melee_drills/format.py` |
| Its example against the opponent a person plays | `python tools/melee_drills/check_play.py <id>`: `check.py` proves an example against the demonstration's opponent, which does one thing; this plays it against the scenario's own script, several runs a scenario, each with a seed of its own, and says how often the part's checks pass. A scenario that never passes is one the drill teaches wrongly |
| The damage a part's example holds at | `python tools/melee_drills/percent_range.py <id> [--part N] [--lo A] [--hi B] [--step N]`: per scenario and character, the range around the scenario's own damage in which the example still passes the part's checks (a binary search each way; `--step 1` tries every percent, for a multi-hit attack). A drill draws a try's damage inside it: `"percent": [LO, "TOP"]`, `TOP` a number of the scenario and, per character, of its `numbers_for` |
| Playing one | `tools/melee_drills/drill.py`: `JsonDrill`, a course drill on the course runtime (`tools/melee_course/engine.py`: loads with no loading screen, attempts, resets, the demonstration, the input timeline) |
| Its proof | `python tools/melee_drills/check.py <id>` |
| In the client | `tools/melee_client/client.py`: the tutorial (`tutorial`, `tutorial_example`), the parts in the drill loop (`course_drill`), the coach (`coach`); `tests/client/short_hop.py` |

A drill file that does not hold to the format is refused with every problem named. A new
word goes into `format.py` (and this page), with a drill that uses it and its proof, never
into one drill's file.

## A drill

| Key | What |
|-|-|
| `id`, `name`, `part` | `part`: tech, neutral, punish or defense |
| `characters` | `"all"` or a list of ids |
| `goal` | one line: what the player can do at the end |
| `why` | why it matters in a match, in two or three sentences |
| `tutorial` | `lessons` (the concept, before the parts: each a `title`, a `text` and what it `show`s), `what`, `expect`, an `example` with its `marks`, and a `camera` its examples are filmed with (optional: closer than the drill's, to see the animation) |
| `scenarios` | where it happens: `stage`, `player` (`{"x": ...}`), `opponent`, `camera` |
| `attempt` | `start` and `judge`: events |
| `measures` | named measures: `{"held": {"held": "jump"}, "kind": "jump_kind"}` |
| `checks` | named conditions: a measure, an expectation, and the words: `expect` (what was asked), `words` (what was measured), `headline` (the title when it fails), `fix` (what to change) |
| `verdict` | `success`: the words of a success |
| `parts` | the technique in links, in order: `name`, `teach`, `example`, `marks` (frame captions), `cues` (frame windows with a colour), `checks` (the names that count), `streak` (in a row to pass), `success` (words, optional) |
| `mistakes` | inputs that must fail, and the check they fail on (for the proof) |
| `coach` | `rows` of the input timeline (`label`, `button`, `window`, `perfect`) and a `note` |

Numbers can be expressions of the character's numbers: `"J-1"` (J: its jump squat, from
`data/framedata`). Words can hold `{expressions}`, `{char}`, a measure (`{held}`, and
`{held_frames}` for "2 frames"), and in a check's words `{measure}` and `{frames}`.

### The words

All of them are defined in `tools/melee_drills/format.py` (checked) and played by
`tools/melee_drills/drill.py`. A word a drill needs and this list lacks is added there, with
its proof, never written into one drill's file.

- **Numbers** a drill may name (in any number or `{expression}` in words): `J` (jump squat),
  `LAND` (normal landing lag), `FA` / `SA` (the frame, counting the jump's press as 1, on
  which a full jump / a short hop reaches its top: the first frame falling), `{char}`; and
  measured in the game (`python tools/melee_drills/measure.py` → `data/drills/numbers.json`,
  for what frame data cannot give): `DASH` (a dash's frames before a held stick runs: Sheik
  7, Fox 11, Mewtwo 18), `SL` (the frame a short hop lands), `LD` (the earliest frame of a
  ledgedash's air dodge that lands on the stage: Fox 5, Peach 29), `NL` / `NFL` (the frame a
  short hop with a neutral air lands: the air on `SA`; fast-fallen, the air on `SA-4` and
  down on `SA` for 3 frames), `SHD` (how far a short hop goes with the stick held forward:
  a player placed `SHD` from an edge lands at it), `SPF` / `SPD` (the first frame of a
  forward drift with which a short hop and a neutral air on `SA` fit on a Battlefield side
  platform, 33 units at most, and how far that hop goes: 1 for most; Jigglypuff 14),
  `KF` / `KW` / `KI` / `KR` (Fox's down throw on the character, the throw's first frame
  counted as 1: the frame they touch the floor; the last frame up to which an L or R
  press is a tech, since a press in the freeze of the throw's last hit is none; the first
  frame they can act after a tech in place and after a tech's roll: `universal-tech`). Any
  number numbers.json measures may be named; a new one needs no word in format.py.
- **States** (`STATES`): the game's action states by name, a tuple being a group any of whose
  states counts: `wait turn dash run run_brake jump_squat jump double_jump (Kirby's and Jigglypuff's extra jumps included, `CHAR_STATES`) fall special_fall
  squat landing landing_special up_smash nair fair bair uair dair aerial aerial_landing
  shield grab dash_grab air_dodge platform_drop teeter roll spot_dodge damage tumble ledge
  ledge_catch ledge_hang dead` (`dead`: a stock lost, DeadDown on; Ness's up smash and Yoshi's shield are their own states,
  `CHAR_STATES`), the shield's own `shield_stun` (GuardSetOff, 181: after a hit on it,
  every input ignored) and `shield_release` (GuardOff, 180: let go, 15 frames; X or Y
  there jumps, down is a spot dodge), both in `shield` too, and
  Fox's `laser illusion illusion_dash illusion_end firefox_charge firefox firefox_any shine
  shine_ground`; `holding` (CatchPull, CatchDashPull, CatchWait: the player's grab caught)
  and `grabbed` (the player held by the opponent's grab, which deals no damage: not a
  `hit`); `throw` (the player's own throw: ThrowF, ThrowB, ThrowHi, ThrowLw) and
  `up_throw` (2026-11-25: `fox-uthrow-uair` begins its try on it);
  `thrown` (in the opponent's throw, until it lets go) and, on the floor after
  it, `tech` (`tech_in_place`, `tech_roll`: its rolls), `missed_tech` (the bounce) and
  `down` (lying there, getting up). Measured (`tests/native/engine_first_frame.py`, the drill's probes): the
  frame shield stun's animation ends is the first a new X or Y works on (Guard reads it on
  that frame), and the record of that frame is the first that has left `shield_stun`.
- **Events** (when something happens, frame by frame): `start`, `end`, `airborne`, `lands`,
  `apex` (the first frame not rising), `fast_fall`, `hit` (damage taken), `hitlag_last`
  (the last frozen frame, whose stick DI and ASDI read: `Fighter_procHitlag` runs before the
  frame's input), `hitlag_end`, `shot` (an item more than the frame before: a laser),
  `connects` (the opponent took damage: the player's attack landed), `shield_hit` (the
  player's attack landed on the opponent's shield: the shield lost more health in a frame
  than a held shield wears by itself; 2026-11-25, for `fox-shield-pressure`),
  `their_attack` (the
  opponent starts a ground attack, an aerial, a grab or a dash grab: states 44 to 69, 212
  and 214, `format.THEIR_ATTACKS`; not its specials, numbered from 341 with other states:
  Peach's forward smash is one), `they_recover` (the opponent can act again: it enters a
  state of `sense.FREE` out of one that is not), and an edgeguard's ends: `they_die` (the
  opponent's stock is lost: it enters a state of `dead`), `they_ledge` (it catches the
  ledge), `they_return` (it is back on the stage: on the ground and free to act, out of
  the air or a landing's lag); all read from the opponent's state in the frame record
  (`opp_state`, `opp_air`, live and played ahead); `{"near": D}` (the fighters come
  within D units, centre to centre along the stage: D or less, more the frame before; D
  may be an expression: `{"near": 16, "after": {"frame": "GO"}}`, the punish's grab);
  `{"is": SIMPLE, "from": S}` (a simple event with modifiers: left the ground out of a
  shine);
  `{"enters": S, "from": S2}`, `{"leaves": S, "to": S2}`, `{"pressed": B}`,
  `{"released": B}`, `{"stick": D}` / `{"cstick": D}` (D: `up down forward back neutral`,
  past the game's 0.6625, forward being where the fighter faces), `{"frame": N}` (the
  attempt's frame N), `{"they_enter": S, "from": S2}` (the opponent enters a state, as
  `enters` is the player's: `{"they_enter": "damage", "from": "squat"}`, it crouch
  cancelled); any of them with `"in_air": true` or `"on_ground": true`, or with
  `"close": D` (it counts only with the fighters within D units of each other: in a drill
  that arises from play, a jump starts a try next to the opponent and not on the way to
  it); a list is any of its events.
- **Measures**: `"jump_kind"` (short or full), `{"held": B}` (frames held from frame 1),
  `{"frames": [E1, E2]}` (from E1 to the first E2 after it; the same event twice: to its
  next time; `"last": true`: from the last E1 before E2), `{"frame_of": E}`,
  `{"happened": E}`, `{"count": E}`, `{"value": F, "at": E}` (F: `x y dx dy vx vy percent
  state facing hitlag turned`; dx, dy from frame 1, dx toward where the fighter faced),
  `{"distance": [E1, E2], "axis": "x"|"y"|"xy"}`, `{"frames_while": C, "from": E}` (C:
  `invulnerable airborne grounded hitlag` or `{"in": S}`: consecutive frames from E),
  `{"max_gap": E}` (the most frames between two of it in a row: a multishine's slowest),
  `{"moved_while": C}` (distance moved on frames that, with the one before, meet C: in
  hitlag only SDI moves a fighter),
  `{"angle": "stick"|"velocity", "at": E}` (degrees, 0 forward, 90 up; velocity: how the
  fighter moved on the next frame, knockback included; `"from_horizontal": true`: from level
  either way, -90 to 90, negative below level). A measure of something that never happened is none, and fails any
  check.
- **Buttons**: A B X Y Z L R, `jump` (X or Y), `shield` (L or R), `lcancel` (L, R or Z; a
  light trigger press counts).
- **Timing** (the player's setting, Lenient or Frame-perfect, in a drill's pause menu; the
  owner: leniency is fine "as long as there are settings to change them if the user wants
  to be held to tighter timings"): a check's `"strict": {an expectation, "expect", "fix"}`
  replaces its own when the player chose Frame-perfect, and a coach row's `strict_window`
  its window. The proof plays every part's example strictly too: examples are
  frame-perfect.
- **Expectations**: `equals` (a number, an expression like `"J"`, a word or true/false),
  `at_most`, `at_least` (a number, an expression of the scenario's numbers, or another
  measure's name: what is asked then depends on what happened, a yes counting 1 and a no
  or a never 0. `fox-aerial-confirm`: `"grab": {"measure": "grabbed", "at_least":
  "cancelled"}`, a grab is asked for only when the opponent crouch cancelled, whichever
  scenario it was),
  `within: [lo, hi]`.
- **Inputs**: `{"press": B, "frame": F, "hold": H}`, `{"stick": [x, y], ...}`,
  `{"cstick": [x, y], ...}`, `{"trigger": "L"|"R", "amount": 0..1, ...}`; entries on the
  same frame combine (down-B: a stick and a press). An input may be timed from an event,
  `"from": EVENT` (`"start"`: the attempt's start): its `frame` counts from it, 1 the frame
  the event happens on (none before it). An input without it counts from the
  demonstration's first frame, while marks, cues and the coach's rows always count from
  the try's start: where a try starts on what the opponent does, after a time of its
  own, the inputs are timed `"from": "start"` (or another event), or the captions are of
  other frames than the inputs. A demonstration finds that frame before it is
  played: each frame while the event is due the coming frame is played ahead in the game
  (`melee_actor/ahead.py`, the opponent's pad as it chose it) and undone, and where the
  event happens on it the input goes on it (the jump on the first frame after shield stun:
  Guard reads only a new press, so it cannot wait until the stun is seen to be over). The
  events of states, the ground, position, damage and hitlag can be looked for so; one the
  look misses is taken where it is seen, a frame late. A drill's inputs timed from events
  are the course runtime's marks (`Ref.mark`, `live_marks`). A character's own inputs, where the
  common ones cannot work for it, go beside them: `"example_for"` / `"inputs_for"`:
  `{"mr-game-and-watch": [...]}` (his neutral air cannot be L-cancelled). Frame 1 is the
  attempt's first; stick x
  positive is forward. A full hop's jump is held `J+2` frames (a fixed 6 is a short hop for
  Bowser). A stick of `[0, 0]` holds the stick in the middle over an earlier input's (the
  whiff punish's walk, held from before the attack, let go of once the dash back is over:
  `Ref.still`).
- **Attempt**: `start` and `judge` (events), `cancel` (events that drop it uncounted; by
  default, leaving the start's state on the ground), `limit` (frames, default 150),
  `timeout` (`judge` or `drop` at the limit), `within` (frames after the reset by which the
  start must come, or the scenario is reset uncounted, the banner saying `missed`; `cancel`
  may be `[]`, nothing drops it: an attempt begun on entering `thrown` would by default be
  dropped where the throw puts its victim on the floor as it lets go: the
  opponent's attack whiffed because the player jumped behind it; the owner: "If the hit
  doesn't connect, the scenario should be reset"). A part may change any of them
  (`attempt`). Events take `"not_to": S` beside `to` (left a state for anything but S: a
  pivot, the turn left for anything but a dash), and `"not_from": S` beside `from`
  (entered from anything but S: a SHFFL's next jump, not the jump out of the shine). In a
  drill that does not reset (`flow`) the next try starts on the frame the last was judged
  on, read against the frame before it: an event on it can start the try.
- **Reset** (after a judged try; the owner, 2026-11-15: "only reset if no damage has been
  done for 3 seconds ... test out follow ups from punishes and such much more
  naturally"). In the client, a drill with an opponent plays on after the verdict, the
  player's pad theirs and the opponent's script running (`Drill.settle`), and resets once
  neither fighter has taken damage for 3 seconds, counted from the verdict or the last
  damage (`Session.settle`, `reset_rule` in `tools/melee_course/engine.py`); a KO or a
  fighter 10 units under the stage's floor resets at once, and it waits 20 seconds at
  most. Nothing after the verdict changes it or the stats; the next try starts after the
  reset. A drill without an opponent, or one that does not reset (`flow`), is as before.
  A drill's own default: `"reset": {"after": "quiet" | "judged" | "hand", "seconds": N}`
  (`format.RESET_AFTER`). The player's choice overrides it: Reset (After damage stops,
  When judged, By hand: D-pad down or the pause menu's Restart) and Quiet time (1, 2, 3,
  4, 5 or 8 seconds), in the drill's pause menu and in Settings, Display (the same values,
  kept in the progress file; until chosen, the drill's own). Headless sessions (`live`
  false: `check.py`, the actors' runs) reset when judged, as before. Proof:
  `tests/client/whiff_punish.py` (a pummel and a throw after the punish delay the reset
  to 3 seconds after them; with no damage it comes 3 seconds after the verdict; When
  judged, at once), `tests/client/settings_menu.py`.
- **Scenarios**: `stage` (`final-destination battlefield yoshis-story dream-land
  fountain-of-dreams pokemon-stadium`; one stage for a drill, its first scenario's: the
  player's `x` may be an expression, `"84-SHD"`;
  match is loaded once; a part's `"scenario"` may be a list, which the player turns through
  with D-pad left and right or the pause menu's Scenario, kept until changed: the
  ledgedash's two ledges, `"ledge": "left"` and `"right"`; or changed by itself, the
  drill's `"switch"`: `"manual"` (the default), `"success"` (the next after a success:
  every drill of ledge work plays both sides of the stage, the owner: "so players don't
  overtrain one side! It should have options to swap ledges on success too"), `"every"`;
  a part's list may be a deck of opponents, each scenario its own (`fox-shine-oos`: eleven
  characters, each its own script), each swapped in as the list turns to it; every
  opponent of a drill's scenarios is loaded with its match (`JsonDrill.opponents`, up to
  the native build's eight fighters: the rest load a match when turned to);
  the pause menu's Swap changes it. A drill's `"shield": "infinite"` keeps the
  player's shield full every frame (a shield drill: never shrunk, poked through or broken;
  the owner, 2026-11-15); `"shield": "theirs"` keeps the opponent's full until the try
  begins (an opponent that holds its shield while it waits: held, a shield wears out in
  seven seconds; one that has been hit is left as it is, and in the try it wears and is
  hit as the game has it; 2026-11-25). A scenario facing left on a platform, the stage or in
  the air plays the examples mirrored: forward is the way it faces; `"inland": D`, with an
  opponent's `launch`: standing D units in from the ledge the opponent is knocked off, their
  back to it as TM-CE's edgeguard event leaves them, `"facing": "ledge"` to face it), `lead` (frames from the reset to
  an example's frame 1: 10, and 0
  on the ledge, whose intangibility runs from the placement: there the runtime's own 3
  neutral frames are skipped too, so frame 1 is the hang's second), `player` (`{"x"}` on the ground, `"above": Y` on
  what is below (x, Y): a platform, `"air": true` with `"y"`: falling with the double jump,
  `"ledge": "left"` hanging; `"facing"`, `"percent"`; `"held": true`: in the opponent's
  grab from the start, below), `opponent`, `camera`, `trace`,
  `numbers`. A part names its scenario by index (`"scenario"`).

  `"numbers"`: the scenario's own numbers and words, named in the drill's expressions
  and words while it is played, beside the character's (`J`, `LAND`): `{"HIT": 12, "HL":
  8, "DX": 0.7071, "DY": 0.7071, "move": "Fox's forward smash"}`. Every scenario names the
  same ones, none a character's number or a measure's. A stick's or C-stick's `[x, y]` may
  be expressions of them (`["DX", "DY"]`), so one part's example plays each attacker's own
  timing and DI; so may a check's expectation (`"within": ["LO", "HI"]`: each launch angle
  its own range), an attempt's `within` and `judge` frame, marks, cues and coach rows. The
  words `check.py` compares across scenarios (a check's `expect` and `headline`) do not
  name them; its `words` and `fix` may. `universal-di` (14 attackers, each with its hit
  frame, hitlag, survival DI and the launch angles that pass), `universal-sdi` and
  `universal-asdi` use it.

  `"trace": "di"` draws TM-CE's DI display for the player, in the game's world (and so in
  the client's pictures, the tutorial's and the coach's): its Lab's "DI Display",
  `DIDraw_Init`, `DIDraw_Update`, `DIDraw_Reset` and `DIDraw_GX` in TM-CE's `src/lab.c`,
  rewritten against the decomp in `src/host/didraw.c` (`didraw P on|off|line`,
  `Native.didraw`). On every frame of hitlag a blue line is made again: the launch
  simulated frame by frame for the stick held then (ASDI, DI as `ftCo_8008E5A4` turns it,
  gravity, the knockback's decay, the stage's floors, walls and ceilings through the
  game's own collision). When hitlag ends the line is kept as the last frozen frame made
  it, so the flight can be seen against it, until hitstun ends or the next hit; TM-CE
  remakes it from the fighter's position all through the flight. The SDI moves through
  hitlag are drawn too, in yellow and orange. Measured headless, the kept line's x is the
  flight's to the hundredth on every frame (y is drawn at the middle of the body).
  `JsonDrill.setup` turns it on or off for each scenario; the client turns it off when the
  drill is left. `universal-di` uses it.
  `"held": true` (the player's): every attempt begins in the opponent's grab. The
  opponent stands at its grab's reach (`x`) and grabs at once (its script's `chain_grab`,
  or plain `inputs`: Z a few frames after the reset, then down pressed anew a few times,
  the same grab from the same spot every time: `universal-tech`); a
  person's pad is kept from the game from the reset until the grab has them
  (`format.HELD_MOST`, 40 frames at most: a jump, a roll or a shield at the reset would
  get out of the grab's way), then handed back (`JsonDrill._withhold`, the window build's
  `script`). A demonstration's pad is the example's, which presses nothing before the
  throw. `fox-escape-techchase` uses it; in the client, `tests/client/techchase.py`: jump
  mashed from the reset, and the throw still comes.
- **Opponents**: `"none"`: no CPU in the drill (none is spawned; one a match already has
  from another drill sleeps: out of play, out of the picture). Or `{"character", "x",
  "facing": "player"|"away", "percent", "inputs", "every"}`: a CPU that plays `inputs` from
  the frame after each reset (stick x toward the player), again every `every` frames. Or a
  scripted one, `{"character", "x", "facing", "percent", "react", "script", "loop"}`: its
  `script` is behaviours (`{"do": "footsies", "range": "outside", "until": "approach"}`,
  `approach`, `punish`, `chain_grab`...) and combinators (`if`/`then`/`else`, `mix` by
  weight, `repeat` with `while` and `times`), with conditions (`approach`, `in_their_range`,
  `{"lag": 10}`...), as `docs/ai/opponent-vocabulary.md` lists them; `react` is the frames
  it takes to see what the player does (15); `loop` plays the script again when it ends.
  `JsonDrill` plays it each frame through `tools/melee_engine/script.py`, made new at each
  reset and seeded from the attempt's random numbers (so a demonstration's two passes and
  every case `check.py` plays meet the same opponent); its decisions are made in forked
  copies of the game while a person plays (the window build) and in the game itself
  headless. `format.py` checks every name against the tables (`script.py`, `behave.py`,
  `sense.py`; moves by name prefix against the engine's), and a script with `inputs` is
  refused. `check.py` takes a drill file's path too (`check.py path/to/drill.json`).

  A scripted opponent's reaction time is the player's to set: CPU reaction (30, 24, 20,
  15, 12, 9, 6 or 3 frames; fewer is harder), in the drill's pause menu and in Settings,
  Display, kept in the progress file; until chosen, each scenario's own `react`
  (`JsonDrill.react`, `Client.react_change`; the owner, 2026-11-17: "options for reaction
  time of the engine so the player can essentially choose their own difficulty"). A
  demonstration's opponent keeps the scenario's own.

  `"launch"` (an edgeguard's start, as TM-CE's edgeguard event): the opponent begins each
  attempt knocked off the stage by one of a list of hits, drawn by `"weight"` with the
  attempt's random numbers: `{"name", "knockback": N or [LO, HI], "angle": degrees above
  level, "percent": its damage, "jump": false if its double jump is gone, "inland": 8,
  "y": 6}` (where it is hit from: units in from the ledge and above the stage, each a
  number or [LO, HI]; "inland" below 0: hit when already past the ledge, an opponent
  off the stage), or `{"hang": true, "percent"}` (it starts hanging from the ledge);
  `"player": {"inland", "facing"}`: where the player stands for this hit, over the
  scenario's. The player's `"inland"` may be [LO, HI] too, their `"facing"` "stage"
  (their back to the ledge), "ledge" or "either" (drawn). `format.draw_launch` draws
  one. A start must leave the opponent a way back when it first acts a reaction after
  the launch (`python tools/melee_engine/recoveries.py --feasible 12`): one that
  leaves none is no edgeguard, and looks as if the opponent gave up. And it must not
  leave it next to the stage (the same command says how far past the ledge it is when
  it can first act; the edgeguard drill's least is 45 units, `recoveries.OUT_MIN`),
  nor on the ledge: there is nothing to guard. The game's own launch (`launch`, `src/host/setup.c`:
  the damage state the knockback gives, its speed and decay, its hitstun, the tumble),
  off the left or the right ledge as the runtime draws the side (the pause menu's CPU
  side: Random, Left, Right). `JsonDrill.launched` is what was drawn.

  A player's `"percent"` may be `[LO, HI]` (2026-11-25, for `universal-crouch-cancel`):
  the damage is drawn for each attempt with the attempt's random numbers, and a
  demonstration plays HI (what an example shows and `check.py` proves is the most damage a
  try can have). The damage a try began with is the number `PERCENT` in words and
  expressions. A scenario's `"numbers_for": {character: {NAME: number}}` gives numbers of
  its `"numbers"` another value for a character (the damage up to which that character
  can crouch through the scenario's attack: `"percent": [0, "TOP"]`).

  `"knockdown"` (a tech chase's start, 2026-11-25): the opponent begins each attempt
  knocked off its feet where it stands, `{"knockback": 90, "angle": 80, "y": 1}` (the
  game's own launch from its place, away from the player, at its `percent`; all three
  optional). What it does on the floor is its script's: the `tech` behaviour (a missed
  tech and a getup attack after a wait that changes, in `universal-crouch-cancel`). Not
  with `"launch"`.

  `"example"`: what the opponent does in a demonstration (a part's example, a mistake,
  the tutorial's and the coach's replays) in place of its `script`, `launch` and `react`:
  `{"script": [...], "launch": [...]}`. An example's inputs are frames; an opponent that
  thinks would answer them another way each time, so in an example it does the one thing
  they answer (`fox-edgeguard`: it comes to the ledge with its jump alone, `{"do":
  "recover", "to": "ledge", "tools": "jump"}`, and falls past a ledge taken). The opponent
  a person plays is proved apart from `check.py`: `tests/engine/recover.py`.

    ```json
    "opponent": {"character": "marth", "launch": [
      {"name": "normal", "knockback": [106, 120], "angle": [45, 60], "percent": [50, 80]},
      {"name": "no jump", "knockback": [90, 106], "angle": [42, 58], "jump": false}],
      "react": 15, "loop": true, "script": [{"do": "recover"}, {"do": "hold", "pad": "stand",
        "until": {"all": [{"me": "offstage"}, {"not": {"me": "on_ledge"}}]}}],
      "example": {"script": [{"do": "recover", "to": "ledge", "tools": "jump"}]}}
    ```

    ```json
    "opponent": {"character": "marth", "x": 30, "react": 15, "script": [
      {"do": "footsies", "range": [40, 55], "for": 20},
      {"mix": [{"weight": 2, "steps": [{"do": "approach", "moves": "sh_", "lands": "any"}]},
               {"weight": 1, "steps": [{"do": "approach", "moves": "dash_attack,fsmash",
                                        "lands": "any"}]}]},
      {"do": "hold", "pad": "stand"}]}
    ```
- **Lessons**: `{"title", "text", "show", "characters", "scenario", "checks"}` (played in
  their own scenario, the first by default, against that scenario's opponent, whichever
  part the player is on, and charted with the drill's own coach rows, the whole
  technique; `"checks"`: the names of the checks its example passes, all counted by one
  part: `check.py` proves them for every character, so name them for any lesson that
  shows the technique or a piece of it); `text` is a paragraph or a list, 500
  characters at most with the longest name filled in (`LESSON_MAX`: it fits beside the
  picture at 13dp or larger; under 440 reads at 15dp)
  of them; `show` is `{"example": {"inputs", "marks", "cues"}}` (played frame by frame from
  the game's own pictures, each frame captioned) or `{"still": {"inputs", "frame",
  "cue"}}` (one picture of that example, its frame `frame`, with a cue `{"words", "kind"}`);
  `characters` (optional) is a number shown for every character in a table below, the
  player's marked (`"jump_squat"`).
- **Cues**: `{"frames": [lo, hi], "words", "kind": "go" | "late" | "info"}`: a band of
  colour and words over the example's picture on those frames ("Release now: short hop" in
  green, "Held here: full hop" in red); `{f}` in the words is the frame shown.
- **Coach rows** (the drill's `coach`, or a part's own `coach`): `{"label", "button": B,
  "held"}`, `{"label", "stick": "down"|"up"|"side"|"any"}` (a tap; side: either way; any:
  whichever way, an SDI's smash out of attacks left by different ways), the same with
  `"cstick"` (not `any`), or `{"label", "state": S}`
  (entered),
  each with `perfect` and `window` frames.
- **Cameras**: `"normal"` (the match camera), `"stage"` (the whole stage, still),
  `{"follow": "player", "distance": D, "height": H}`: the game's own free camera (the pause
  camera's) on the player, its eye D in front and H above; Training Mode's "Zoom" is 140
  and 10. (`camera` in `src/host/camera.c`; the client puts the match camera back when the
  drill is left.) Followed, it is eased (the owner: "really jarring. It picks up every
  little motion ... make it smoother so it literally doesn't 100% track the character"):
  the game's free camera aims at a bone and goes half the way to it every frame, so it
  dipped with every crouch and landing; the native build hands its aim to the host, which
  follows the fighter's feet instead, holds still while the fighter is within 12 units
  across and 20 up of it, and eases a tenth (across) and a twentieth (up) of the way beyond.
  Measured through the window build (a stage point's move in the picture): a short hop
  9.8 px a frame at most and 146 px in all before, 0.35 and 2.3 after; a full hop 13.4 and
  291 before, 1.7 and 23 after; a dash is still followed, smoothly.

  A lesson played in a scenario the part now lacks (the punish's, while the player is on
  the first part) is judged as the first part that has it, its frames counted from that
  part's start; its inputs timed from an event play to their end before the try is judged
  (those before the event, a shield held until then, are its setup).

### Finding the numbers in the game

`python tools/melee_drills/probe.py <drill> [--part N] [--char C] [--inputs '[...]']` plays
inputs in the drill's scenario and prints every frame (state, air, position, speed, hitlag,
invulnerability, stick). A drill's frames come from this and the decomp, not memory: the
fast fall's rule (`ftCommon_CheckFallFast`: falling, the stick past 0.6625, and reached
there within the last 3 frames) and its top (the speed reaches 0.00 a hair above zero for
characters whose jump speed divides evenly by their gravity, so a tap is held 3 frames).

## Tutorial and coach

They are different things.

**The tutorial shows how to do it**, and teaches the concept, visually (the owner: "similar
to coach where it shows you a frame by frame playback in the tutorial itself ... more visual
rather than textual"; "more educational ... describing the concept of jump squat, how it
varies with every character and how that affects short hop timing ... a visual cue of when
they need to release the jump button"). On a drill's first open, and on D-pad up:

1. Its lessons, one card each: a few sentences beside what the lesson shows: an example
   recorded from the game's own pictures (as the coach records its target), played in the
   card with the input display, the caption of the frame shown and its cue over the
   picture, the D-pad stepping a frame (D-up plays or pauses, Y shows it full size); or one
   still picture of it; and a table of every character's number below, if it has one. A
   goes on, B back, START to the drill. No goal line and no headings over the words (the
   owner: "We don't need to say WHAT IT IS, just have the info text").
2. The part now: its example played the same way with its own captions and cues, the
   example's inputs frame by frame below, the parts as chips (L and R choose another).
3. A part passed `streak` times in a row opens the next, with its own card.

Short hop's two lessons (the owner: "a brief introduction of the jump squat and then how to
short hop"): the jump squat, purely informational (a still of the character in its squat,
what a jump squat is, how every character's differs and so the time to let go, J - 1, and
a table of every character's from 3 frames to Bowser's 8, the player's marked); how to
short hop (the squat frame by frame: green "let go now" on frames 1 to J - 1, red "still
held: full hop" on frame J, the same thin straight band in every colour).

**The coach shows what went wrong.** After misses in a row (Settings: 2 to 5, or off) its
card shows the try against the example of the part being played, from the same start (the
game's own pictures of both), the input timeline with the target window, the check that
failed as the headline ("Held through the squat") and its `fix` ("Let go of X or Y within
2 frames of pressing it ..."). The verdict after every try says the same in a line.
The full-size example of a part whose inputs are timed from its start is numbered from that
start, as the card's pictures and the coach number it (`tutorial_example_run`).

## Proof

`check.py <id>` plays, headless, for every character the drill allows: the tutorial's
example and each part's example (each must pass), and each mistake (each must fail, on the
check it names, judged as the first part that counts that check). It prints the words a
player would read once, for a person to read. `universal-short-hop`: 182 of 182 cases for
the 26 characters (jump squats of 3 to 8 frames), in 8 seconds.

A part whose scenarios are a deck of opponents (each scenario another opponent) plays its
example, its frame-perfect example and every mistake judged as it in each scenario of the
deck. `fox-shine-oos`: 45 of 45 cases, the eleven opponents' scripts each meeting the
frame-perfect example and the late jump, in 30 seconds.

A session's tries are numbered as they come, and each draws its own random numbers
(its launch, its side, its opponent's choices): `Session.run`'s `run`. The client gave
none until 2026-11-17, and every try of a session drew the same. A demonstration takes
the last try's number; `check.py`'s cases, all demonstrations, all draw number 0's.

`fox-edgeguard`: 36 of 36 cases in 50 seconds: both parts' example (the ledge taken by a
wavedash back off the edge) against each of the eleven opponents' example script, and
standing still failing on "It reached the ledge" (the first part's own `attempt`, which
ends at the ledge; the edgeguard's ends only on the stock, the stage, or Fox lost). What its opponent does against a
person (it gets back when nothing is done, changes its route when it sees a commitment,
later with a longer reaction time) is `tests/engine/recover.py`'s and
`tools/melee_engine/recoveries.py`'s to show.

`fox-escape-techchase`: 92 of 92 cases in 15 seconds: each part's example and both
mistakes (no tech; a tech, then standing still) against each of the eleven opponents'
example script (its throw, then standing: `chain_grab` with `times` 1). What its opponent
does against a person (it covers each tech at the frame its reaction allows, holds its
grab until its answers are back, reads a habit) is `tests/engine/chase.py`'s and
`tools/melee_engine/chases.py`'s to show.

`universal-tech`: 325 of 325 cases for 25 characters in 9 seconds (not the Ice
Climbers: Fox's grab takes whichever of the two is nearer). Its last part is a deck that
turns after every try (`"switch": "every"`: the tech that is called), each of whose
scenarios has its own numbers for the same example (`["SX", 0]`: the stick for the tech
called); the proof plays the scenario it names, and a demonstration shows the last try's
scenario again, not the next (`Session.run`). Its lockout is proven as a mistake: a press
too early, then one in time, and no tech. A placement now clears the game's own record of
the last L or R press as a spawn does (`still`, `src/host/setup.c`): a press late in one
attempt locked out the tech of the next, begun at once.

Any drill in the client, without a test of its own: `python tests/client/drill_smoke.py
<id>` opens it from the course, answers its tutorial, lets some tries go by and leaves.

A drill generated from a description is done when `check.py` passes and the owner has
played it.

## Example: the short hop

`data/drills/universal-short-hop.json`. Its parts:

1. **The jump squat**: press X once; before the character leaves the ground there are J
   frames of jump squat, where short or full is decided. Any jump passes it, once.
2. **Tap, do not hold**: let go within J - 1 frames. Checks: jumped with a button (not the
   stick), let go in the squat, a short hop. Three in a row.
3. **Ten in a row**: ten short hops in a row.

No CPU; the camera follows Fox, eased, further out than the normal camera's close zoom on a
lone fighter (220; the owner asked for "a little" further than the first 180). The
tutorial's examples are filmed closer (90), to see the crouch.

## Next

The owner plays and QAs the 27 Tech skill drills; then the Punish, Defense and Neutral parts
in the format. Known runtime issues found while writing them: a reset during an opponent's
sliding attack can leave it slightly off its mark (`universal-di` judges late to avoid it);
the Ice Climbers' partner was not moved by a reset (`universal-sdi` allows 4 hits for it; a reset now puts her back with the player, `partner` in `src/host/setup.c`, so that allowance may be tightened). A placed fighter also kept its ground speed and slid on from where it was put (fixed the same day; it may be the "slightly off its mark" above).
A match holds the player and seven opponents (`Session.FIGHTERS`); a drill's rotation draws
only scenarios whose opponent is loaded, and turning by hand to another loads a match. So a
drill keeps to seven opponents (`universal-di`: the top seven; `universal-asdi`: Pikachu,
Yoshi and Samus with four of them). With the Ice Climbers as the player, the native build
crashed (signal 11 in `fn_800DA054`, called through `Fighter_procAccessory`) when a reset
placed the opponent while the partner, left out of the reset, held it: the placement let go
of the grab and left her in her grab's state with nobody to hold. It had nothing to do with
the matches loaded: 96 in one game did not crash it, and that grab crashed it at once. Fixed
2026-11-15 (`release` and `partner` in `src/host/setup.c`). Seven opponents is a real limit:
the preload cache holds eight characters (`GameCache.entries[8]`, the rotation's limit in
`match.c`); a ninth asked for is not loaded.
