# AI on the native build

Direction set by the owner on 2026-11-13: "we want to focus on the native linux build
because we want to build in direct AI integration and the actor system to build AI-driven
training." The native build (`native-port.md`) is an ordinary Linux process: nothing in it
has a GameCube's 24 MB or its 486 MHz, which is what kept a real model out of the game
(`melee-actor.md`, "Can an instructable model run inside the game?").

This file is the plan and its status. What exists is under "What runs today"; the rest is
not built.

## The shape

```
 game: build/native/melee_headless        the deciding side: Python, 64-bit
 ┌───────────────────────────────┐  pipe  ┌──────────────────────────────────────┐
 │ the vanilla game, 32-bit      │◀──────▶│ tools/melee_native/native.py (Native) │
 │ src/host/control.c            │  one   │  ├ Melee Actor: scripts of intentions │
 │  pads in, a frame's state out │  line  │  ├ slippi-ai policies                 │
 │  snapshots (forks)            │  each  │  └ later: the trainer, Claude         │
 └───────────────────────────────┘  way   └──────────────────────────────────────┘
```

- **The game cannot be loaded into Python.** It is built 32-bit (the game's code assumes
  4-byte pointers) and Python is 64-bit. So everything that decides inputs lives in another
  process and talks over the control protocol. That costs little: a frame with its state is
  one line each way, about 110 microseconds including the Python side.
- **Nothing that decides is in the frame loop of a playable game yet**, because there is
  no playable game: the native build draws nothing (see "The gap").
- A C twin of the actor inside the game, which the overlay build would need
  (`melee-actor.md`), is **not needed here**: two full-size policies already run faster than
  real time beside the game.

## What runs today (2026-11-13)

| Piece | Where | Checked by |
|-|-|-|
| A frame per exchange: `tick` sets the pads, runs frames, returns the state (both fighters: state, frame, position, speed, facing, airborne, damage, hitlag, hitstun, shield, kind, jumps used, invulnerable, stocks; items; the random seed) | `src/host/control.c`, `Native.step` | `tests/native/env.py` |
| Placing fighters: `Native.place()` | `src/host/setup.c` | `tests/native/place.py`: on Final Destination and on Battlefield's platforms, in the air, refused where there is no floor |
| A port's second fighter (the Ice Climbers' partner): `fighter 4`..`7`, and `fp SLOT` for where a fighter's data is | `control.c` | used to find the CPU fault in `native-port.md`, kind 7 |
| Snapshots: `Native.snapshot()` / `restore()` / `drop()` | `control.c` (below) | `tests/native/env.py`: the same inputs from a snapshot give the same game, in any order of restores, and the same as a fresh process |
| Scenarios: a situation, an opponent's script or policy, a stand-in player, what counts as success; many runs from one set-up, each moved about | `tools/melee_actor/scenario.py`, `run.py` | `tests/actor/scenarios.py`, 8 checks: one situation played three ways (below) |
| What a character's running moves reach, measured by trying | `tools/melee_actor/calibrate.py` → `data/actor/reach.json` | used by the scenarios above |
| The Melee Actor, unchanged, on either the native build or the simulator | `tools/melee_actor/actor.py` | `tests/actor/uptilt.py` (4 of 4 on both) |
| slippi-ai policies as players, on either | `tools/melee_actor/policy.py` | `tests/actor/policy_match.py` |
| A window: the game drawn, at the console's speed, a port played from a controller or the keyboard (below) | `src/host/window.c`, `tools/melee_native/window.py`, `play.py` | `tests/native/live.py`, 14 checks, on a virtual display with keys pressed there. Never on a real display or with a real controller |

Measured on this machine, unoptimised build (`-O0`):

| | Native | Python simulator |
|-|-|-|
| A match up and both fighters standing, from nothing | 0.35 s | several seconds, or a cached state |
| Frames a second, a full state read back each frame | about 8,900 | 50 to 160 |
| The actor's four up tilt situations (785 frames) | 0.11 s | 7.3 s |
| Two policies playing each other, 1,800 frames | 12.4 s (146 a second; the game is 0.4 s of it) | game-bound |
| Snapshot / restore | 0.4 ms / 0.8 ms | a copy of the whole memory |

`Native` has the simulator's interface where the two overlap (`pad`, `step`, `fighter`,
`snapshot`, `restore`), which is why the actor and the policy bridge needed no changes to
their logic. `Native.start(p1, p2, stage)` boots, starts a VS match with both pads ours
and waits until both fighters stand.

**What the native build is not, still:** the vanilla game only. No overlay, no TM-CE, no
course engine, no UCF (`ucf.md`), no drills. Where the simulator's Lab and the native VS
match were given the same script, three of four runs ended within a frame of each other
and with the same positions; one differed in where the target ended up. Not looked into.

**Placing and repeating.** A placement makes the fighters the same whatever came before.
It does not touch what else is about: effects still playing, and so where the random
stream stands a few frames later. To repeat a situation exactly, set it up once, take a
snapshot and restore that; the test checks both halves of this.

## Snapshots are forks

`snap` forks the game. The child goes to sleep holding everything as it was: the arena,
the statics, the host layer's own heap (converted archives), audio RAM. It shares memory
with the running game until either writes to a page. `restore` wakes the sleeper, which
forks a copy of itself to take over stdin and stdout, and the process that asked exits; the
sleeper stays, so a snapshot can be restored any number of times.

- No game code had to change, and nothing can be missed: it is the whole address space.
  (`netplay-p2p.md` lists the in-process alternative, which needs the host's allocations
  moved into one region first. Rollback netcode will want that one; experiments do not.)
- Which process is "the game" changes at every restore. The table of sleepers is in memory
  shared by all of them. `Native` starts the game in its own process group and kills the
  group on `close()`; sleepers also leave by themselves when stdin closes. A leaked
  emulator took this machine down once (2026-11-11), so the test checks that nothing is
  left running.
- Commands are read with `read()`, not stdio, and one at a time: a process started from a
  snapshot must not find bytes in a buffer that another process already acted on.
- With sleepers holding stdout open, a crashed game no longer shows as end of input. A
  fatal error prints `@ fatal`; `Native` also gives up after `timeout` seconds of silence.

## The gap: nobody has played it

AI-driven training has a person in it. Until 2026-11-13 the native build had no graphics
and no controller, and everything here was developed with a stand-in for the player: an
actor script or a policy. It now draws and reads a person's input (the next three
sections), but no person has played it: it has only been run on a virtual display. It has
no sound.

### The window: the graphics stack builds and runs 32-bit (probe, 2026-11-13)

Aurora (`build/deps/aurora`) draws GX through Dawn (WebGPU) and opens its window with
SDL3. Its prebuilt Dawn exists for 64-bit Linux only, and the game is a 32-bit process.
A time-boxed probe built all three from source as 32-bit x86:

```sh
tools/aurora32/build.sh        # -> build/aurora32/build; first time fetches Dawn and SDL3
```

| | |
|-|-|
| Builds | Aurora (unmodified), Dawn at Aurora's pinned revision, SDL 3.4.10: about 2.5 minutes at `-j 10`, 1.8 GB of build tree |
| Changes needed | One line of Dawn (`tools/aurora32/dawn-0001-vk-null-handle-32bit.patch`: on 32-bit a raw Vulkan handle is a `uint64_t` and Dawn's `VK_NULL_HANDLE` a `nullptr_t`), and `-DDAWN_USE_GLFW=OFF` (GLFW wants a 32-bit `xkbcommon`, which is not installed) |
| Runs | A 32-bit program (`build/aurora32/probe/dawn32_probe vulkan --render`) creates a WebGPU device on Vulkan with this machine's GPU through the 32-bit NVIDIA driver, with no window and no surface, draws a triangle into a texture and reads back the right pixels. Rerun by hand after the probe: same result |
| Aurora itself | Its example initialises and runs its frame loop under a virtual X server (`xvfb-run`, SDL's x11 driver). With SDL's `offscreen` or `dummy` driver it stops: Aurora only makes a surface from an X11 or Wayland window |
| Nothing had to be installed | The 32-bit Mesa, Vulkan loader and X11 that were there are enough. Would help: `lib32-libxkbcommon lib32-libdecor` (a Wayland driver in SDL3), `lib32-libxcursor lib32-libxi lib32-libxrandr` (X11 extensions SDL3 loads), `lib32-vulkan-swrast` (software Vulkan, for tests off the GPU) |

### The game draws (2026-11-13)

```sh
tools/aurora32/build.sh                      # once: Aurora, Dawn, SDL3 as 32-bit
python tools/native_build.py --window        # build/native-window/melee_native
python tools/melee_native/window.py --out DIR [--match fox,marth,final-destination] [--frames 30,150,330]
```

`melee_native` is the headless game with Aurora under its graphics calls
(`src/host/window.c`). `tools/melee_native/window.py` runs it where nothing can appear on
the desktop: on a virtual X server of its own, drawn by a software renderer, and saves
what is on that screen. A picture of a match (Fox and Marth on Final Destination, frame
330) shows the stage, both fighters, the background, the damage display and each
player's stock icon. Set beside a frame of the same stage and characters from Dolphin it
shows nothing wrong, but the two were taken from different camera positions and compared
by eye, not pixel by pixel.

It runs faster than the game needs: a frame of that match takes about 6 ms with the
software renderer and 4 ms on this machine's GPU (240 a second), where the game wants one
every 16.7 ms. `MELEE_TIMING=1` logs where a frame's time goes every 60 frames;
`MELEE_DEBUGGER=1` lets a debugger that is not the game's parent attach (the kernel's
default forbids it), which is how the slow part below was found.

Pictures of the game are not kept in this repository (it is public, and they show the
game's art): they go under `build/shots/`, which git ignores. One was committed by mistake
in e61f7e715 and removed in the next commit; it is still in that commit's history.

What it took, beyond linking Aurora in:

| | |
|-|-|
| A frame | One Aurora frame is opened at each of the game's frame boundaries and closed at the next (`host_window_frame`) |
| Writes straight to the console's command pipe | The particle and a few other files write vertex data with `GXWGFifo.f32 = x;`, an assignment to a hardware address, which Aurora never sees: its command stream lost its place. `native_build.py` compiles a copy of those files in which each such write is `GXParam1f32(x)` (`FIFO_FILES`) |
| Vertex arrays | The console's `GXSetArray` has no length; Aurora copies the whole array into the frame. A model's vertex data is a blob of an archive, so its length is bounded the way the readers bound any array of unknown length: up to the next thing the archive points at (`host_dat_blob_size`). A looser bound overflowed Aurora's 8 MB of frame storage |
| Fighter materials | `ftmaterial.c` reads two templates through a struct laid over three adjacent globals; natively they are not adjacent (one more of `native-port.md`'s "memory layout" kind). Patched at build time |
| Palettes | A palette is a typed array in the archives, so the readers hand the game entries in host byte order; Aurora decodes them as the console stores them. It is given the file's own bytes instead (`host_GXInitTlutObj`). Until then every indexed texture had wrong colours |
| Lookups by address | "Which archive is this pointer in" walked every object of every open archive, for each palette and vertex array of each frame: 27 ms a frame, 36 frames a second. The answers are now kept until an archive is opened or closed (`memo_slot` in `window.c`) |
| Stock icons | Both players' icons were Captain Falcon's. `gm_80168B34` never assigns `base` for the first twenty characters; the console's code happens to keep the character's number in that register (confirmed in the retail code), and natively it was whatever the stack held. Patched at build time. It led to a search for others of its kind (`native-port.md`, kind 7) |
| Running it safely | The game's process renames itself ("Main thread"), so `pgrep melee_native` does not find it, and `timeout` around `xvfb-run` leaves it running. `window.py` puts the X server and the game each in a process group, kills both on close and looks for survivors by executable path |

Known, not fixed:

- **Variables the game's code reads without assigning**: four places found and patched,
  two of which changed play (a hit CPU's decision, so the Ice Climbers' partner; Samus's
  grapple beam). `native-port.md`, kind 7, and `tests/native/uninit.py`. What that test
  did not exercise is unknown.
- **The software Vulkan driver (lavapipe) crashes** inside its compiler a few frames in,
  in this 32-bit process. Tests use software OpenGL ES (llvmpipe) instead
  (`MELEE_BACKEND=gles`). `--gpu` leaves the choice to Dawn and has run a match on the
  virtual display; which driver it chose there was not recorded.
- **Every texture is new to Aurora each time it is drawn** (the game fills in a fresh
  texture object per draw, and Aurora numbers them). Aurora finds the picture again by
  its content, so it is correct, but what this costs over a long session is unmeasured.
- **Snapshots do not work in the window build** (a fork of a process with a GPU context
  and threads): not guarded, do not use them there.
- No sound, and nothing has been run on the real display.

### A person at the controls (2026-11-13, off screen only)

```sh
python tools/melee_native/play.py                         # Fox against a standing Marth
python tools/melee_native/play.py falco sheik --stage battlefield --cpu
python tools/melee_native/play.py --input keyboard        # or pad0, pad1; --input2 for port 2
```

`play.py` opens the window on the desktop it is started from, hands port 1 to a person
and runs at the console's speed. **It has never been run that way**: agents here do not
put windows on the owner's desktop. `--offscreen` runs the same loop on a virtual
display, which is what was tested.

How it works: a port can be *live* (`live P SOURCE` on the control pipe,
`Window.live()`). At each frame boundary a live port's pad is read from a controller or
the keyboard through SDL into the same `host.pads[]` a script writes, so the game, the
state on the pipe and the other port's script are as before: an actor or a policy can
play port 2 and read every frame while a person plays port 1. That is the shape N7
needs. `pace` (`Window.pace()`) holds the game to 59.94 frames a second.

| Input | Mapping |
|-|-|
| A controller, through SDL | By where the buttons are: bottom A, left B, right X, top Y; right (and left) shoulder Z; left stick the stick, right stick the C stick; triggers L and R, with the click as SDL reports it for a GameCube adapter, or the last tenth of the travel on other controllers |
| The keyboard | Arrows: the stick (left shift: a light push). I J K L: C stick. X: A. Z: B. C, V: Y, X. A, S: L, R. D: Z. Return: Start. T F G H: D-pad |

Known limits of the controller path, none of them tried:

- **Not a controller's own numbers.** SDL rescales a GameCube controller's sticks before
  the game sees them (88 steps from the centre become a full push). For exact inputs
  (what UCF and control profiles are about) the adapter has to be read directly, as
  Dolphin does. Not done.
- The adapter must be openable by SDL (the permissions Dolphin needs).
- Aurora's own controller layer (bindings, rumble) is not used: it would replace the
  host's `PADRead`, which scripted runs depend on.
- No vsync by default (`--vsync`); the picture is shown as soon as it is drawn.

Two faults in the driver came out of this and are fixed for every user of `Native`:

- **A reply could be missed and the driver wait for ever.** It read lines through
  Python's text layer but looked for waiting data below it; when the game printed several
  lines at once (always with `-v`) the reply sat in between. It reads the pipe itself now,
  and a silent game is an error after `timeout` seconds.
- **A driver killed from outside left the game and the virtual display running** (twice,
  for two minutes, under `timeout`). Both are now killed by the kernel when the driver
  dies, however it dies (`die_with_parent`); checked by killing a driver with SIGKILL.

Looked at, one frame each, software renderer (pictures under `build/shots/`): Dream Land,
Battlefield, Pokémon Stadium, Yoshi's Story, Fountain of Dreams and Final Destination,
with twelve characters between them. All ran 400 frames and are recognisably right.
Seen and not looked into: Fountain of Dreams' reflecting floor is drawn in coarse blocks;
Pokémon Stadium's screen shows "kj" under "Combatants".

### Training against a scenario yourself (2026-11-13, off screen only)

```sh
python tools/melee_actor/train.py data/scenarios/shield-grab-dash-attack.json [--reps 20] [--jitter 6]
```

The first loop with a person in it: the scenario's opponent script plays port 2, the
person plays port 1, each attempt gets a verdict ("success", or "failure: you did not hit
them; you were hit") and the situation is put back. The same scenario files, the same judge
(`success`), the same opponent steps as the scripted runs: `Session(scenario,
game=window, person=port)` leaves the player's stand-in script out.

What differs from a scripted run, and why:

- **No snapshots** (the window build has none): the situation is put back by placement
  alone. Effects still in the air and the random stream carry over from one attempt to
  the next, so attempts are not exact repeats.
- **An attempt lasts as long as the opponent's script** (then `after` frames), since
  nothing says when a person is done.
- **The verdict is printed in the terminal**, not on the game's screen. Aurora carries
  ImGui, which could draw it over the game; not done.

`tests/actor/train.py` (7 checks) is three people made of key presses on the virtual
display: one stands still (hit: failure), one shields and does nothing (not hit, no
punish: failure), one shields, grabs when the hit has landed and hits (success). **No person has used
it.**

### The client: its own menus (2026-11-13, off screen only)

```sh
tools/aurora32/build.sh && python tools/native_build.py --window   # once: RmlUi is now part of it
python tools/melee_client/client.py [--input keyboard]             # a 1280 by 720 window
```

The native build's own interface, in the look of the design canvas (the owner's decisions
on it are in the project memory `ui-mockups-canvas`): a main menu, a character select and
the column beside a match. 16:9, with the game's picture kept four by three at the left.
**It has only been run on a virtual display.**

| Piece | Where |
|-|-|
| RmlUi (an HTML-and-CSS-like UI library that Aurora carries as an option), built 32-bit | `tools/aurora32/build.sh` |
| Aurora drew that layer only over the game's picture, and centred the picture. A patch makes it cover the window with the picture at the left (`aurora_set_ui_full_window`) | `tools/aurora32/aurora-0001-ui-full-window.patch` |
| The host loads a document and changes it by element id: `ui load|class|text|attr|hide|show|font` on the control pipe. It knows nothing about menus | `src/host/ui.cpp` |
| `pads`: what a live port's person holds. `capture`: the game gets a pad at rest meanwhile, so a press meant for a menu does not also reach the game underneath | `src/host/window.c` |
| The screens as markup, the look, the roster (names and traits from `data/characters/`, course sizes from `data/courses/`), the flow | `tools/melee_client/` (`screens.py`, `style.rcss`, `characters.py`, `client.py`) |
| The typefaces (Barlow, Barlow Condensed, IBM Plex Mono; Open Font License), fetched once into `build/ui/fonts/` | `tools/melee_client/fonts.py` |

The flow lives in Python, like the trainer: the client steps the game a frame at a time,
reads the pad and tells the host what to show.

| Screen | What it does | From |
|-|-|-|
| Main menu | Five panels; Train goes on, the other four say "not yet" | `screens.main_menu` |
| Character select | 26 characters; the card shows three style words, weight, fall speed, jump squat | `data/characters/<id>.md` |
| Course hub (a character with a course: Fox) | The four parts, how many drills each has, how many are marked done and how many play in this client; free play; where you left off (X continues) | `data/courses/<id>.md` through `courses.py` |
| A part's drills | Every drill of the part in the course's order, with its goal, opponent, what it builds on and leads to; tries, success and best run; **Y marks it done** (the owner's rule for now: the player decides) | the part's plan table |
| A drill | The scenario's opponent against the player, attempt after attempt: a banner over the game with the verdict ("Success" or "Failure": the owner's word, 2026-11-13), and in the column this try's checks, the last ten, tries, success and best run. Hold START to leave | `data/scenarios/*.json` through `melee_actor.scenario.Session(person=...)` |
| Free play | The chosen character against a standing Marth; nothing is judged | `Native.start` |

**Which drills play.** A drill plays in this client when a file in `data/scenarios/`
names it (`"drill": "<course drill id>"`). There are two kinds of file:

| Kind | What judges | Plays (of Fox's 46) |
|-|-|-|
| A scenario (`opponent`, `success`) | What happened between the two fighters: hit or not hit (`melee_actor/scenario.py`) | Neutral: Take it on shield, Whiff punish |
| A tech drill (`"tech": "short_hop"` or `"wavedash"`) | The player's own pad and their fighter's states, frame by frame (`melee_actor/tech.py`) | Tech: Short hop, Wavedash |

The other 42 are listed with everything the course file says about them and "Not in this
client yet" where Start would be. No Punish or Defense drill plays.

**The tech judge.** It finds each attempt (the fighter entering jump squat), so the
player sets the pace and nothing is put back between tries. Its rules were measured on the
game, not assumed: jump squat is frames 1 to J (3 for Fox, 4 for Marth, 8 for Bowser); a
short hop needs the button held at most J - 1 frames; an air dodge pressed on frame J + 1
lands at once, pressed in jump squat it never comes out, and each frame later is one more
in the air. Which jump came out is read from the game (the upward speed on the first
airborne frame, against the two speeds measured for the character when the drill is set
up), so a jump with the stick is judged too. The verdict names the frames ("Full hop.
Jump still held on frame 4: let go within 2", "Air dodge 3 frames late: 2 allowed", "No
air dodge", "The air dodge did not reach the ground") and the column draws the attempt
frame by frame: what was pressed when, where it was due, what is allowed. The two files
are character-free; the client plays them as whoever is being trained.

What the player has done is kept in `save/client.json` (ignored by git): per drill the
done mark, tries, successes and best run, and the last drill played.

`tests/actor/tech.py` (21 checks, headless) scripts the inputs to the frame for Fox, Marth
and Bowser: the verdict turns exactly where the jump squat says. `tests/client/tech.py`
(8 checks) plays both drills in the client with stand-ins that press keys.

Tests, with key presses on the virtual display: `tests/client/menu.py` (15 checks: the
menu, the roster, free play and back) and `tests/client/course.py` (16 checks: hub, list,
a drill that is not built, the shield grab played three times by a stand-in who shields,
grabs and hits twice and stands still once, the numbers and the done mark kept on disk,
where you left off, free play from the hub). `--shots DIR` saves a picture of each
screen.

Not there: Lab, Events, Versus and Controls (their panels say "not yet"), the guide and
the demonstration, the other fourteen Tech drills (L-cancel and SHFFL are the next two
the judge could take), nicknames and layouts (the header shows
placeholders), character art (two letters and a colour of the client's choosing stand
in), panel icons, sound.

What RmlUi is not, learned on the way: no CSS grid and no `clip-path` (layouts are flex
rows and columns; a slanted edge is a skewed element); no outline (a focus ring is an
element of its own); no built-in styles at all (`div` has to be told it is a block); text
straight inside a flex row is not drawn (it gets an element); an inherited italic applies
to a face that has none (set `font-style: normal` with the mono face); a style sheet
named by a path starting with a slash is looked for below RmlUi's own root (the client
copies it beside the document).

Known: the match left behind when coming back to the menu keeps running unseen (and will
end on its timer); starting the next one from wherever the game then is has only been
tried from inside a match.
A drill is started with A, and A held on into the drill would be a grab out of shield:
the first try waits (up to a second and a half) for the buttons to be let go.

Where a person can train **today** is still the overlay build on Dolphin
(`training-courses.md`).

## Plan

| Step | What | Proof |
|-|-|-|
| N1 (done) | The interface above; actor and policies on it | the three tests |
| N2 (placement done) | Setting up a situation from a command instead of from play. `Native.place(port, x, y, facing, air, percent)`: standing on whatever floor is at or below the point, or falling from it; not holding or held, no speed, a full shield (`src/host/setup.c`, the course engine's placement on the game's own functions). Stocks, items and the rest of a match's rules: not yet | `tests/native/place.py`, 11 checks |
| N3 (begun) | The actor's step library (`melee-actor.md`, A2). Done: steps are generators, so two scripts run at once; scenario files and a runner with a verdict as JSON; the conditions `target_attacking`, `target_swung`, `target_idle`, `target_frame`; `rush` (running grab, dash attack, jump-cancelled up smash, at measured distances), `throw`, `shield` (until it has blocked) and `oos` (shield grab, up smash, jump out of shield); `choose`, so an opponent varies what it does from run to run. Not done: jumps and aerials, dash dance, wavedash, a step interrupted by being attacked, branching on what happened | one scenario per step |
| N4 (begun) | A trainer process: scenarios run against a stand-in player, retried from a snapshot, scored. Done: `scenario.Session`, one situation in two versions. Not done: scenarios from `data/courses/`, a session of several, keeping score over time | two scenarios from `data/courses/` run end to end, headless |
| N5 (written, never run against the API) | Claude in the loop: turns an instruction into a scenario, runs it, reads the verdicts, revises (`ai-coach.md` for the coaching side). Never in the frame loop. `tools/melee_actor/author.py`, below | an instruction in words becomes a scenario that passes: **not shown**, no credentials on this machine |
| N6 (draws, paced, a port played from the keyboard; all off screen) | A window, sound and a controller. Done: Aurora linked in, six stages drawn, the console's speed, live ports, `play.py`. Next: **the owner runs `play.py`** (first time on a real display and with a real controller), then sound, then the adapter read directly | a person plays a match |
| N7 (begun, off screen: `train.py`) | The trainer with a person in it. Done: a scenario's opponent against a live port, a verdict per attempt in the terminal. Next: the verdict and the guide on the game's screen, statistics over a session, choosing what to practise next | the owner trains against an actor |
| N8 (off screen: `client.py`) | The client: the interface of the design canvas, natively. Done: main menu, character select, course hub, drill list with the done mark, drills against an opponent and tech drills with their verdicts, free play. Next: more drills (L-cancel, SHFFL; then Punish and Defense scenarios), the guide, Controls | the owner picks a character and trains a drill without a terminal |

N6 gated N7 and is now far enough for it. What all of it waits for is the owner running
`client.py`, `play.py` or `train.py`: nothing here has been on a real display or had a
real controller.

## The first drill-shaped thing: one situation, three ways to play it

`tests/actor/scenarios/`: Marth forward smashes from 42 units away and holds his shield
from the first frame he can. The player is a stand-in script.

| File | The player | What happens | 40 runs, each moved by up to 2 units |
|-|-|-|-|
| `whiff_punish.json` | waits until the hitbox has come out and gone (`target_swung`: 54 frames in, found from the game, not counted), runs in, grabs out of the run, throws up | holding Marth at frame 77; he could have shielded from frame 90 | 40 pass |
| `too_slow.json` | the same wait, then stops next to him and up smashes | the up smash starts at frame 105 and meets a shield: no damage | 40 "fail" as a drill should score it |
| `too_early.json` | goes when the swing starts | runs into the sword | 40 hit |

- Moved by up to 8 units, 36 of 40 punishes still pass. In the other four the two started
  within about 35 units, where the tip of the sword reaches: not a whiff any more. The
  runner found that; nobody looked it up.
- The fast way in needed a number nobody had: a running grab slides a long way before its
  grab box is out, so started too close it ends up behind the target. `calibrate.py` tries
  every starting distance for the running grab, dash attack and jump-cancelled up smash of
  every character against a standing Marth (26 characters in 44 s) and writes
  `data/actor/reach.json`. For Fox the grab connects when started 15 to 38 units out; the
  actor starts it at 26.5.
- After the smash the opponent now does one of three things, chosen per run: shields,
  jabs, or rolls away. The punish passes 60 of 60: done in time, it does not matter which.
- A trained policy can be the opponent of a scenario (`"policy": "marth_d18_vs_fox_v3.1"`,
  run with slippi-ai's Python). Tried once, to see that it runs: it does, but the policy
  has not started playing in its first frames (its inputs are 18 frames behind), so what
  that run scored means nothing. A scenario against a policy needs a warm-up first.
- What this is not yet: a drill. Nothing explains, scores over time or adapts; the player
  is a script.

A second situation was written the way `author.py` is meant to work, but by hand, from the
instruction "shield Marth's dash attack and grab him out of shield":
`data/scenarios/shield-grab-dash-attack.json`. It needed two steps the actor did not have
(`shield` until blocked, `oos`), which is the intended way for the vocabulary to grow. The
knowledge base says the dash attack is -20 on Fox's shield and a shield grab takes 7
frames; in the game the stand-in blocks, grabs and throws in 40 of 40 runs moved by up to 3
units, and without the shield the dash attack hits.

## Claude writing scenarios (`tools/melee_actor/author.py`)

```sh
.venv/bin/pip install anthropic            # once
export ANTHROPIC_API_KEY=...               # or `ant auth login`
python tools/melee_actor/author.py "Marth dash attacks from mid range. \
    I want to practise shielding it and grabbing him out of shield."
python tools/melee_actor/author.py --show-prompt
```

Claude (`claude-opus-5-5` by default, `--model` to change) is told what a scenario is, what
makes one good (works when moved about, fair, tells right from wrong, no frame numbers where
a condition would do) and the actor's vocabulary, which is generated from `actor.py` so the
prompt cannot drift from what runs. It has three tools:

| Tool | Does |
|-|-|
| `run_scenario(scenario, runs, jitter)` | runs it on the native build; answers with how many runs passed and the steps and checks of one failing and one passing run |
| `game_data(query)` | `tools/melee_data/query.py`: frame data, out-of-shield options, shield advantage, knockback |
| `save_scenario(name, scenario)` | writes `data/scenarios/<name>.json`; refuses unless that exact scenario passed 90% of a run of 10 or more |

The loop is the SDK's tool runner. A safety decline is rerun on a fallback model by the API
(`fallbacks: "default"`).

**What is checked:** the three tools, the save rule and the tool definitions the SDK builds,
without any API call (`tests/actor/author_tools.py`, 11 checks); with no credentials the
command says so and stops. **What is not:** the conversation itself. Nobody has seen
Claude write a scenario through this yet, so the prompt is a first draft.

## Not verified

- Anything here on an optimised build. `--opt 1` is faster (`native-port.md`) and was not
  rerun with the new protocol.
- Snapshots under memory pressure, or hundreds of them at once. Each keeps the pages the
  game has since changed; the table holds 256.
- That the policies play as well here as in Dolphin. They fight (in the 1,800 frame run
  Marth kept Fox in the air for long stretches); nobody compared.
- More than two fighters, CPU players, stages other than the six tournament ones.
