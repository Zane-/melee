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

The old drills were wiped (2026-11-14) and are rebuilt in this format one at a time with the
owner, Tech first. Done: `universal-short-hop`.

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
| `tutorial` | `what` (what the technique is), `expect` (how it is judged), `example` (inputs) and `marks` (frame captions): the drill's own page and example |
| `scenarios` | where it happens: `stage`, `player` (`{"x": ...}`), `opponent`, `camera` |
| `attempt` | `start` and `judge`: events |
| `measures` | named measures: `{"held": {"held": "jump"}, "kind": "jump_kind"}` |
| `checks` | named conditions: a measure, an expectation, and the words: `expect` (what was asked), `words` (what was measured), `headline` (the title when it fails), `fix` (what to change) |
| `verdict` | `success`: the words of a success |
| `parts` | the technique in links, in order: `name`, `teach`, `example`, `marks`, `checks` (the names that count), `streak` (in a row to pass), `success` (words, optional) |
| `mistakes` | inputs that must fail, and the check they fail on (for the proof) |
| `coach` | `rows` of the input timeline (`label`, `button`, `window`, `perfect`) and a `note` |

Numbers can be expressions of the character's numbers: `"J-1"` (J: its jump squat, from
`data/framedata`). Words can hold `{expressions}`, `{char}`, a measure (`{held}`, and
`{held_frames}` for "2 frames"), and in a check's words `{measure}` and `{frames}`.

### The words

- **Events**: `{"enters": STATE}` (jump_squat, wait, landing, air_dodge...), `"airborne"`.
- **Measures**: `"jump_kind"` (short or full: the rise speed on the first frame in the air
  against the character's two jump speeds), `{"held": BUTTON}` (frames held from the
  attempt's first frame). Buttons: A B X Y Z L R, `jump` (X or Y), `shield` (L or R).
- **Expectations**: `equals`, `at_most`, `at_least`, `within: [lo, hi]`.
- **Inputs**: `{"press": BUTTON, "frame": F, "hold": H}`, `{"stick": [x, y], ...}`,
  `{"cstick": [x, y], ...}`, `{"trigger": "L"|"R", "amount": 0..1, ...}`. Frame 1 is the
  attempt's first; stick x positive is forward.
- **Opponents**: `"none"`: no CPU in the drill (none is spawned; one a match already has
  from another drill sleeps: out of play, out of the picture).
- **Cameras**: `"normal"` (the match camera), `"stage"` (the whole stage, still),
  `{"follow": "player", "distance": D, "height": H}`: the game's own free camera (the pause
  camera's) on the player, its eye D in front and H above; Training Mode's "Zoom" is 140
  and 10. (`camera` in `src/host/camera.c`; the client puts the match camera back when the
  drill is left.)

## Tutorial and coach

They are different things.

**The tutorial shows how to do it.** It plays on a drill's first open, before any try, and
on D-pad up:

1. The drill's card: the goal, why, what it is, what to expect, and its parts, the one
   being played marked (up and down choose another).
2. The example (A on the card): played from the drill's start with the input display, at
   the game's speed to its first frame, then its frames at half speed, stopping on each
   captioned frame ("frame 1: X pressed: the jump squat begins"); the D-pad steps a frame
   either way, A plays or pauses, B goes back to the card.
3. A part passed `streak` times in a row opens the next, with its own page and example.

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
3. **Every time**: ten short hops in a row.

No CPU; the camera follows Fox, a little further out than the normal camera's close zoom
on a lone fighter.

## Next

The rest of the Tech part, one at a time with the owner: the wavedash in parts (the jump;
an air dodge into the ground from a short hop's top; the air dodge on the first airborne
frame; angle and length), L-cancel, SHFFL, dash dance, the jump-cancelled grab and up smash,
the shield drop, the ledgedash. Words added as they need them (an air dodge's frame, the
slide, the landing lag, the stick's angle).
