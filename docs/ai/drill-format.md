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
the stage by a hit drawn for the attempt (`launch`) and recovering by the engine's
`recover` (`melee-engine.md`, "Recovering"): its routes played ahead in the game, one of
the best taken, another when it sees what the player commits to, its reaction time after
they do. The reaction time is the player's to set (CPU reaction, in the pause menu and
Settings), for this and every drill whose opponent is a script.

## Where things are

| | |
|-|-|
| A drill | `data/drills/<id>.json`: nothing but the words below |
| The words, the checking of a file | `tools/melee_drills/format.py` |
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
  platform, 33 units at most, and how far that hop goes: 1 for most; Jigglypuff 14). Any
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
  `hit`). Measured (`tests/native/engine_first_frame.py`, the drill's probes): the
  frame shield stun's animation ends is the first a new X or Y works on (Guard reads it on
  that frame), and the record of that frame is the first that has left `shield_stun`.
- **Events** (when something happens, frame by frame): `start`, `end`, `airborne`, `lands`,
  `apex` (the first frame not rising), `fast_fall`, `hit` (damage taken), `hitlag_last`
  (the last frozen frame, whose stick DI and ASDI read: `Fighter_procHitlag` runs before the
  frame's input), `hitlag_end`, `shot` (an item more than the frame before: a laser),
  `connects` (the opponent took damage: the player's attack landed), `their_attack` (the
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
  attempt's frame N); any of them with `"in_air": true` or `"on_ground": true`; a list is
  any of its events.
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
  `at_most`, `at_least`,
  `within: [lo, hi]`.
- **Inputs**: `{"press": B, "frame": F, "hold": H}`, `{"stick": [x, y], ...}`,
  `{"cstick": [x, y], ...}`, `{"trigger": "L"|"R", "amount": 0..1, ...}`; entries on the
  same frame combine (down-B: a stick and a press). An input may be timed from an event,
  `"from": EVENT` (`"start"`: the attempt's start): its `frame` counts from it, 1 the frame
  the event happens on (none before it). A demonstration finds that frame before it is
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
  start must come, or the scenario is reset uncounted, the banner saying `missed`: the
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
  the owner, 2026-11-15). A scenario facing left on a platform, the stage or in
  the air plays the examples mirrored: forward is the way it faces; `"inland": D`, with an
  opponent's `launch`: standing D units in from the ledge the opponent is knocked off, their
  back to it as TM-CE's edgeguard event leaves them, `"facing": "ledge"` to face it), `lead` (frames from the reset to
  an example's frame 1: 10, and 0
  on the ledge, whose intangibility runs from the placement: there the runtime's own 3
  neutral frames are skipped too, so frame 1 is the hang's second), `player` (`{"x"}` on the ground, `"above": Y` on
  what is below (x, Y): a platform, `"air": true` with `"y"`: falling with the double jump,
  `"ledge": "left"` hanging; `"facing"`, `"percent"`), `opponent`, `camera`, `trace`,
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
  "y": 6}` (where it is hit from). The game's own launch (`launch`, `src/host/setup.c`:
  the damage state the knockback gives, its speed and decay, its hitstun, the tumble),
  off the left or the right ledge as the runtime draws the side (the pause menu's CPU
  side: Random, Left, Right). `JsonDrill.launched` is what was drawn.

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
- **Lessons**: `{"title", "text", "show", "characters", "scenario"}` (played in their own
  scenario, the first by default, whichever part the player is on, and charted with the
  drill's own coach rows, the whole technique); `text` is a paragraph or a list, 500
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

`fox-edgeguard`: 36 of 36 cases in 40 seconds: both parts' example (the ledge taken by a
wavedash back off the edge) against each of the eleven opponents' example script, and
standing still failing on "It reached the ledge". What its opponent does against a
person (it gets back when nothing is done, changes its route when it sees a commitment,
later with a longer reaction time) is `tests/engine/recover.py`'s and
`tools/melee_engine/recoveries.py`'s to show.

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
