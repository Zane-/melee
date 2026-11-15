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
  ledge_catch ledge_hang` (Ness's up smash and Yoshi's shield are their own states,
  `CHAR_STATES`), and
  Fox's `laser illusion illusion_dash illusion_end firefox_charge firefox firefox_any shine
  shine_ground`.
- **Events** (when something happens, frame by frame): `start`, `end`, `airborne`, `lands`,
  `apex` (the first frame not rising), `fast_fall`, `hit` (damage taken), `hitlag_last`
  (the last frozen frame, whose stick DI and ASDI read: `Fighter_procHitlag` runs before the
  frame's input), `hitlag_end`, `shot` (an item more than the frame before: a laser);
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
  same frame combine (down-B: a stick and a press). A character's own inputs, where the
  common ones cannot work for it, go beside them: `"example_for"` / `"inputs_for"`:
  `{"mr-game-and-watch": [...]}` (his neutral air cannot be L-cancelled). Frame 1 is the
  attempt's first; stick x
  positive is forward. A full hop's jump is held `J+2` frames (a fixed 6 is a short hop for
  Bowser).
- **Attempt**: `start` and `judge` (events), `cancel` (events that drop it uncounted; by
  default, leaving the start's state on the ground), `limit` (frames, default 150),
  `timeout` (`judge` or `drop` at the limit), `within` (frames after the reset by which the
  start must come, or the scenario is reset uncounted, the banner saying `missed`: the
  opponent's attack whiffed because the player jumped behind it; the owner: "If the hit
  doesn't connect, the scenario should be reset"). A part may change any of them
  (`attempt`). Events take `"not_to": S` beside `to` (left a state for anything but S: a
  pivot, the turn left for anything but a dash).
- **Scenarios**: `stage` (`final-destination battlefield yoshis-story dream-land
  fountain-of-dreams pokemon-stadium`; one stage for a drill, its first scenario's: the
  player's `x` may be an expression, `"84-SHD"`;
  match is loaded once; a part's `"scenario"` may be a list, which the player turns through
  with D-pad left and right or the pause menu's Scenario, kept until changed: the
  ledgedash's two ledges, `"ledge": "left"` and `"right"`), `lead` (frames from the reset to
  an example's frame 1: 10, and 0
  on the ledge, whose intangibility runs from the placement: there the runtime's own 3
  neutral frames are skipped too, so frame 1 is the hang's second), `player` (`{"x"}` on the ground, `"above": Y` on
  what is below (x, Y): a platform, `"air": true` with `"y"`: falling with the double jump,
  `"ledge": "left"` hanging; `"facing"`, `"percent"`), `opponent`, `camera`, `trace`. A
  part names its scenario by index (`"scenario"`).

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
  the frame after each reset (stick x toward the player), again every `every` frames.
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
  "held"}`, `{"label", "stick": "down"|"up"|"side"}` (a tap; side: either way), the same with
  `"cstick"`, or `{"label", "state": S}`
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

## Proof

`check.py <id>` plays, headless, for every character the drill allows: the tutorial's
example and each part's example (each must pass), and each mistake (each must fail, on the
check it names, judged as the first part that counts that check). It prints the words a
player would read once, for a person to read. `universal-short-hop`: 182 of 182 cases for
the 26 characters (jump squats of 3 to 8 frames), in 8 seconds.

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
the Ice Climbers' partner is not moved by a reset (`universal-sdi` allows 4 hits for it).
