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
sections). (Since then the owner plays it on their desktop, and it has sound: "Sound"
below.)

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
| Lookups by address | "Which archive is this pointer in" walked every object of every open archive, for each palette and vertex array of each frame: 27 ms a frame, 36 frames a second. The answers were first kept until any archive was opened or closed, which was still wrong (see "Stutter" below); each archive now has its own index and only what concerns a closing archive is forgotten |
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
| A GameCube controller on an adapter (`gcc1` to `gcc4`; what `auto` picks first) | Read straight from the USB device, as Dolphin does (`src/host/gcadapter.c`): the controller's own numbers, counted from where it rested when first seen, as the console does. No library: the kernel's usbfs. Needs the udev rule Dolphin asks for; while Dolphin has the adapter this cannot, and the other way round |
| Another controller, through SDL | By where the buttons are: bottom A, left B, right X, top Y; right (and left) shoulder Z; left stick the stick, right stick the C stick; triggers L and R, with the click as SDL reports it for a GameCube adapter, or the last tenth of the travel on other controllers |
| The keyboard | Arrows: the stick (left shift: a light push). I J K L: C stick. X: A. Z: B. C, V: Y, X. A, S: L, R. D: Z. Return: Start. T F G H: D-pad |

**The adapter (2026-11-13).** The owner opened the client on their desktop and "nothing
happened with my controller". SDL's own adapter driver goes through libusb, and there is
no 32-bit libusb on this machine, so SDL saw no controller at all. The game now reads the
adapter itself. Checked: `tests/native/gcadapter.py` (11 checks) decodes made-up reports
(every button, sticks and triggers from the rest position, unplug and replug, a wireless
controller) and then has the game open the owner's adapter (a Lossless adapter, 057e:0337)
and read the controller on its port 1 at rest. **Nobody has pressed a button through it
yet.** `python tools/melee_client/client.py --devices` says what the game sees.

Known limits of the SDL path (other controllers), none of them tried:

- SDL rescales a controller's sticks before the game sees them.
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
python tools/melee_client/client.py --fullscreen                   # or F11 while it runs
```

The native build's own interface, in the look of the design canvas (the owner's decisions
on it are in the project memory `ui-mockups-canvas`): a main menu, a character select and
the column beside a match. 16:9, with the game's picture kept four by three at the left.
**It has only been run on a virtual display.** (The owner has since opened it on their
own screen.)

**Fullscreen (2026-11-13).** The owner: "Let's also add support for fullscreen.
Fullscreen should center the window when fullscreening on screens that do not have the
same aspect ratio (for example I have an ultrawide monitor)". F11 switches, `--fullscreen`
and `--windowed` choose at start, and the choice is kept for the next start (a file
`fullscreen` beside Aurora's shader cache; `MELEE_FULLSCREEN=0|1` overrides it). It is
SDL's desktop fullscreen: the screen's mode is not changed. Whatever the window's shape,
the interface and the game's picture keep to a 16:9 frame (the shape the window was made
with), as large as fits and centred, black round it: `aurora_set_ui_frame` in
`tools/aurora32/aurora-0001-ui-full-window.patch`. The driver's `window` command (and
`Window.where()`, `fullscreen()`, `resize()`) say where that frame is.
`tests/client/fullscreen.py` (18 checks) gives the window an ultrawide shape (1720 by 720)
and a tall one (1280 by 900) on a virtual display and compares pictures: black bars, the
same menu between them, a match with the game at the frame's left. **The switch to
fullscreen itself is not tested**: a window manager does it and a virtual display has
none; the test checks that it is asked for, by F11 and by command, and remembered.

**The verdict banner** sits at the top of the game's picture, about a third the size it
was ("much too large", the owner, 2026-11-13).

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
| A drill | The scenario's opponent against the player, attempt after attempt: a small banner at the top of the game with the verdict ("Success" or "Failure": the owner's word, 2026-11-13), and in the column this try's checks, the last ten, tries, success and best run. Hold START to leave | `data/scenarios/*.json` through `melee_actor.scenario.Session(person=...)` |
| Free play | The chosen character against a standing Marth; nothing is judged | `Native.start` |
| Versus | Your character, then the opponent: which character, who plays it (X turns through a trained slippi-ai model for the pairing, other models, the game's CPU, nobody) and the stage (L and R). A match with the column saying who is on the other side | `tools/melee_client/opponents.py`, `melee_actor/policy_server.py` |
| The Lab | The same choice with nobody playing the opponent unless asked; D-pad down puts both back, left and right set the opponent's damage | the same |

**A trained model on the other side (2026-11-13).** slippi-ai's models
(`~/Games/Melee/slippi-ai/deployed_models/`, 137 of them) play natively: no Dolphin, no
Slippi. The model runs in a process of its own in slippi-ai's Python
(`melee_actor/policy_server.py`; its packages do not load in the project's), and the
client talks to it in lines of JSON. **The game never waits for it**: the client asks
about the frame just played and uses the answer a frame later, and the model is told so
(`console_delay=1`: it reacts one frame sooner to make up). Measured: the frame loop
spends 0.2 ms a frame on it; a model loads in about five seconds, beside the match (the
opponent stands still until then). `opponents.models(bot, player)` picks: a model trained
for the pairing first (`falco_d21_vs_fox_v6.1` for Falco against Fox), then the
character's other models, then the ones named for a rank, which are not tied to a
character. `tests/client/versus.py` (16 checks): the Falco model against a Fox nobody
moves answers 420 of 421 frames, is in 21 different states and crosses the stage; the Lab's
tools.

Not there, of Versus and the Lab: stocks, a timer that ends the match, a result (the
match is the debug mode's endless one); more than two players; the Lab's other tools
(saving and loading a position, recording, the CPU's settings: everything Training Mode's
Lab has). Not known: how well the models play here against a person (they see no
projectiles and no partner Ice Climber: `policy.py` does not pass them on); whether the
rank models play characters they have no model of. slippi-ai's own rule stands: these are
for offline play, not for the Slippi ladders.

**Which drills play.** A drill plays in this client when a file in `data/scenarios/`
names it (`"drill": "<course drill id>"`). There are two kinds of file:

| Kind | What judges | Plays (of Fox's 46) |
|-|-|-|
| A scenario (`opponent`, `success`) | What happened between the two fighters: hit or not hit (`melee_actor/scenario.py`) | Neutral: Take it on shield, Whiff punish |
| A tech drill (`"tech": "short_hop"`, `"l_cancel"`, `"shffl"` or `"wavedash"`) | The player's own pad and their fighter's states, frame by frame (`melee_actor/tech.py`) | Tech: Short hop, L-cancel, SHFFL, Wavedash (the first four of the part) |

The other 40 are listed with everything the course file says about them and "Not in this
client yet" where Start would be. No Punish or Defense drill plays.

**The tech judge.** It finds each attempt (the fighter entering jump squat), so the
player sets the pace and nothing is put back between tries. Its rules were measured on the
game, not assumed: jump squat is frames 1 to J (3 for Fox, 4 for Marth, 8 for Bowser); a
short hop needs the button held at most J - 1 frames; an air dodge pressed on frame J + 1
lands at once, pressed in jump squat it never comes out, and each frame later is one more
in the air; L, R (pressed at all) or Z halves an aerial's landing lag when pressed on the
frame of landing or one of the six before it, and an eighth frame early or a frame late
does nothing; a fast fall is the fall speed jumping to the character's fast fall speed.
Whether the lag was halved is read from the game (the frames spent in the landing state
against that aerial's two lags in `data/framedata/`). An L-cancel attempt is any aerial;
one that is over before landing has nothing to cancel and is shown as "not counted". A
SHFFL is judged on its four parts and names the first one missing. Which jump came out is
read from the game (the upward speed on the first
airborne frame, against the two speeds measured for the character when the drill is set
up), so a jump with the stick is judged too. The verdict names the frames ("Full hop.
Jump still held on frame 4: let go within 2", "Air dodge 3 frames late: 2 allowed", "No
air dodge", "The air dodge did not reach the ground") and the column draws the attempt
frame by frame: what was pressed when, where it was due, what is allowed. The two files
are character-free; the client plays them as whoever is being trained.

What the player has done is kept in `save/client.json` (ignored by git): per drill the
done mark, tries, successes and best run, and the last drill played.

`tests/actor/tech.py` (51 checks, headless) scripts the inputs to the frame for Fox, Marth
and Bowser: the verdict turns exactly where the jump squat and the seven frames say.
`tests/client/tech.py` (12 checks) plays the four drills in the client with stand-ins that
press keys.

Tests, with key presses on the virtual display: `tests/client/menu.py` (15 checks: the
menu, the roster, free play and back) and `tests/client/course.py` (16 checks: hub, list,
a drill that is not built, the shield grab played three times by a stand-in who shields,
grabs and hits twice and stands still once, the numbers and the done mark kept on disk,
where you left off, free play from the hub). `--shots DIR` saves a picture of each
screen.

Not there: Lab, Events, Versus and Controls (their panels say "not yet"), the guide and
the demonstration, the other twelve Tech drills, a target for the aerial drills (they are
done on the spot; "hit or shielded" is not there), nicknames and layouts (the header shows
placeholders), character art (two letters and a colour of the client's choosing stand
in), panel icons, sound.

**Smooth edges.** The slanted panels were stair-stepped on the owner's screen ("the
aliasing on diagonal graphics is quite bad"). Aurora's RmlUi renderer has 4x
multisampling behind a compile-time switch that is off; the patch turns it on. The game's
own picture is not anti-aliased (`AuroraConfig.msaa` would do it; not asked for).

**Stutter (2026-11-13).** The owner, on their own screen: "The game plays fine, but the
graphics are completely choppy." Measured (`MELEE_TIMING=1`, or `client.py --timing`):
the driver in Python is not it (the game waits 0.1 to 0.4 ms a frame for it). With the
fighters acting, the slowest frame of every second took 27 ms on the game's side: a
fighter's animation archive is closed and opened at every change of animation, and each
time everything the window build remembered about archives by address was thrown away
and asked again, by a walk over every object of every open archive. An idle match never
showed it, and idle matches were all that had been timed. Now each archive has an index
from converted object to file offset (`find_native`, `archive.c`) and what is remembered
is only dropped for the archive that closes. An active match: 150 late pictures in 1,140
before, 5 after; the slowest frame 1 ms. Pictures are also held to an even schedule
(`present_wait`: shown 6 ms after their frame began, `MELEE_PRESENT_MS`), instead of
whenever each happened to be done. On the virtual display there is little headroom at
1280 by 720 (it copies every picture on the CPU: 93 frames a second flat out, 238 at
640 by 480), so the last few late pictures there say nothing about a real screen.
**Whether it is smooth on the owner's screen is theirs to say.**

**The focus ring** was a square round every panel but the first: a ring shown later
(`display`) was drawn without the slant of the panels it sits in. It is always there now
and only its colour changes; `tests/client/menu.py` looks at a picture for it.

**Tests and a client someone is playing** share nothing now: an off-screen run has its
own shader cache (`MELEE_STATE_DIR`) and its own folder for documents. Before, a test run
while the owner had the client open failed on a locked cache.

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

### The courses on the native build (2026-11-13)

The owner: "Let's work on porting over all the training courses over into native now."
The overlay's course drills (Fox's 46, with the universal ones) run on an engine in C
written against Training Mode's framework (`src/tmce/events/course/`). That framework
(its headers, menus, on-screen text, event loading) is not part of the native build, and
its drawn interface would fight the client's. So the engine was ported instead, to Python
on the native driver, and the drills one by one, callback for callback:

| Piece | Where |
|-|-|
| The engine: attempts, placements (floor, solo, ledge, air, platform), CPU scripts, phases, marks, verdicts with a measured frame, retries, flow drills, decks (a shuffled bag), two-pass demonstrations, the D-pad, per-character numbers | `tools/melee_course/engine.py` |
| The drills, one module per C file, `DRILLS = [...]` | `tools/melee_course/drills/` |
| Which drills exist | `tools/melee_course/registry.py` |
| The overlay's own specs (230, `tests/tmtest/course/`), run against the port: same options, inputs, expectations | `python tests/course/specs.py [DRILL ...]` |
| The client playing one, guide and demonstration included | `tests/client/course_engine.py` |

**Status: all 46 drills of Fox's course (the universal ones included) are ported, and all
229 of their specs that apply pass** (`python tests/course/specs.py`, 2026-11-13; the one
other spec drives Training Mode's pause menu). Every frame count the specs check comes
out as in C. The client plays all of them (`tests/client/course.py`: every drill of the
course plays here).

Host additions for it: the stage's left ledge and a fighter hanging on it (`ledge`), shield
health (`shield`), one-fighter matches (`start(p1, None)`).

What the port works out instead of reading, because the native fighter report does not
have it (each checked against the specs and the game's own flag): ledge intangibility
frames left and the move's own intangibility (`tech_ledge.py`, `defense.py`: counted as
the game counts them), the fast-fall flag (`tech_movement.py`: from the falling speed),
who owns an item (`fox_specials.py`: there is only the player's). Reporting `fp->x1990`,
`fp->x1988`, the hitstun and fast-fall flags and items' owners in `host_fighter_json`
would let those go.

Random choices: the C drills draw from the game's random stream (HSD_Randi), the port from
Python's, so the same seed makes the same choices in another order. Two specs depend on one
particular draw (the CPU's DI); `tests/course/specs.py` pins it to what the C drew
(`DRAWS`).

Found in the C drills while porting, and fixed in both (the owner: "yes please, go ahead
and fix!", 2026-11-13; overlay specs checked in the simulator, the port's natively):

- `fox-shdl` counted Fox's blaster (an item from the moment the laser state starts) as a
  laser, so one shot after the first airborne frame passed as two. It counts laser items
  now. The spec that passed because of it (`first_on_six`) is replaced by two measured
  ones: the first B on airborne frame 3 still leaves time for a second laser, on frame 4 it
  does not.
- The `fox-shine-knockdown` opponent let go of its shield: a fresh press from Wait is
  GuardReflect (182), which its test left out, so it cycled Wait, GuardReflect, GuardOff.
- The L-cancel and SHFFL demonstrations: the landing prediction checked the fast fall
  against the speed after the frame's gravity (the game uses the speed the frame started
  with) and kept adding gravity during a fast fall (the game holds it constant); and the
  aerial was aimed at its first hit plus four frames whatever its lag window. Now the
  prediction follows the game, the aim stays three frames inside the last frame with
  landing lag (`lag_from`/`lag_to` in the generated tables, from the frame data's
  autocancel window), and an aerial that would fall on a fast-fall tap comes a frame
  earlier. Natively every character's five demonstrations succeed in both drills except
  Mr. Game & Watch's neutral, back and up air, which cannot be L-cancelled (the drill waits
  for a landing lag that never comes; a course for him replaces the drill).
- Two verdict strings held a raw line break inside the literal; they are `\n` now. One spec,
`fox-anti-air/hit_first`, fails natively for another reason than the one it is named for:
at its frames Fox runs through Falcon before the dash attack starts.

Two things the C does that do not carry over as written:

- **The CPU's stick.** The C scripts write the CPU's stick (`fp->cpu.lstick`), which the
  game reads as v / 127; the native opponent is a pad, read as min(raw, 80) / 80. A
  script's 80 is a tilt for the CPU and a smash on a pad (and UCF snaps it to 1.0). The
  engine converts (`cpu_axis`); reference inputs are converted as the C's `SetPlayerPad`
  does. Found when Peach's down tilt came out as a down smash and pushed Fox away.
- **When a change is seen.** A C drill's Think runs part-way through a frame and sees a
  change the animation makes (shieldstun ending, a jump squat ending) in the frame it
  happens; the native state is read between frames, a frame later. A drill records such a
  moment one frame back (`Ctx.mark(..., back=1)`). Found as "frame 3" for a frame-4 shine.

The client (`client.py`, `course_drill`) plays a ported drill when a course lists it. The
four tech drills judged by the frame (`data/scenarios/tech-*.json`, with their input
timeline) keep that judge. In a drill the D-pad is the drill's, as in the overlay: up shows
the guide in the column (right there plays a demonstration, up goes on), left and right
change the opponent's scenario, down resets. A drill's options (CPU damage, leniency, what
counts as a success) are in the client's pause menu (START), below.

Found on the way, fixed: every character's sounds were loaded twice (a disc read completes
inside the request here, before the sound manager had stored the load's id, so its
completion callback started the same load again), and after a few different opponents the
sound bank overflowed and an assertion stopped the game. A native patch stores the id
first (`lbaudio_ax.c` in `PATCHES`). Nineteen opponents and five stages in one game since.

### In a drill or a match: the controls (2026-11-13)

From the owner's play session: "Success should be green, failure red ... (Both on the top
overlay and the right overlay)", "The right overlay should be dismissable. Let's use start
for 3 seconds to toggle it. Let's also build a custom pause menu", "Pause should always be
drill settings", "hold D pad left for 3 second or D pad right for 3 seconds to cycle
between [drills]", "changing the stage via holding L or R for 5 seconds", and the
fast-forwarding and teleporting they saw.

| Control | What it does |
|-|-|
| START tap | The client's pause menu over the frozen match (`freeze`: the game's developers' pause, which stops gameplay and goes on drawing). In a drill: the drill's own settings (its options from the C, the scenario, the CPU's side, the stage where it has several), the guide, a demonstration, restart, hide the column, the drill before or after, the drill list, the course, the main menu. In free play and Versus: resume, the column, back, main menu. A setting changed is in force from the next try |
| START held 3 s | The column away, the game's picture in the middle of the window (`center` in the interface: `aurora_set_game_centered` in the Aurora patch); again to bring it back |
| D-pad up / down | The guide / a restart (drills) |
| D-pad left or right | A tap: the scenario before or after; held 3 s: the drill before or after in the course |
| L or R held 5 s | The stage before or after, in a drill that has several stages (`Drill.stages`) |

START and the D-pad never reach the game in a drill (`mask`; in free play and Versus
START only), so the game's own pause and taunts do not happen. A button that did
something in a menu is not a tap when let go, and the game does not see it until it is
(`Client.consume`): the A that chose "Resume" once came out as a jab. During a
demonstration the game takes the script's pad and the player is still read (`script`), so
a D-pad press or START stops it. Verdicts are green or red (the palette's Defense and
Punish colours) on the banner and in the column. (A match loaded inside a drill was
once behind a "Loading" cover; there is no cover now: "Loading like TM-CE" below.)

The jumps the owner saw: the course engine reloaded the match before every try of a drill
without an opponent, and the tech judge moved a player standing more than 50 units out
back to the start; both are gone (commit 73c814112).

`tests/client/controls.py` (8): the column away and back (pictures: black at both sides),
a setting changed in the pause menu and in force on the next try, a failure in red on the
banner (a picture), D-pad right held 3 s to the next drill. The other client tests leave
through the pause menu now (`tests/client/pausekeys.py`).

### Drills the owner changed, and timelines (2026-11-13)

From the owner's play session, done natively first (the overlay's C drills keep their old
behaviour; `tests/course/specs.py` plays these the C's way where an option can,
`NATIVE_AS_C`, and marks the three dash dance specs whose behaviour changed, `SUPERSEDED`):

| Drill | Change |
|-|-|
| Short hop double laser | An attempt is one short hop: grabbing the ledge, a double jump or an aerial drops it ("It also counts stuff off the ledge too!": a laser from a ledge jump made a pair with the hop's) |
| Dash dance (was "Dash dance and pivot") | No count to reach: the dance's direction switches are counted, it ends as a success when the player stops or acts, a failure when they run; the longest dance is kept. Light rays come down on the stage (option Targets): reach one and the next comes down where the camera shows it |
| Jump-cancel grab (was "... and up smash") | An up smash is not counted. **Jump-cancel up smash** is a new drill below it (`universal-jc-upsmash`, native only) |
| Shield drop | A deck of nine starts: the left, top or right platform, standing on it, dropping onto it, or jumping up to it from the floor; Battlefield, Yoshi's Story, Dream Land, Fountain of Dreams (L or R held 5 s, or the pause menu) |
| Waveshine | Up to 5 frames late counts (its own Leniency option, 0 to 5, default 5) |
| Aerial into shine | The shielding opponent is held in place (option Opponent): the host clears its sideways speeds, shield pushback among them, at every frame boundary (`anchor`) |
| Ledgedash | Starts on the ledge, falling to it (the default), on the stage by it, or on a respawn platform (host `rebirth`, as TM-CE's ledgedash event), or any of them; a regrab is a refresh, not a failure |
| Shortened Illusion | Levels 1 to 4, the frame of the window the second B is on (1 the shortest, 4 the longest), in turn or one of them |

`tests/course/native_changes.py` (62 checks) plays each change; `tests/client/drills.py`
(9) checks the ray on screen, a stage change with R held and a timeline in the client.

**Timelines are standard** ("Frame perfect jump-cancelled shine should have frame timings
visualized as well. We should make that standard"). A drill's `timeline(c)` gives rows
(`engine.Row`: a button pressed or held, an analog trigger, a state entered, a stick tap,
or frames the drill counted) with the frame-perfect frames and the window that counts; the
engine logs every frame's inputs and states and builds the result's `timeline`, which the
column draws under the verdict as the tech judge's. Frame 1 is the drill's own (the shine,
the jump, the drop); a long attempt shows its last 30 frames. Drills with one: short hop,
L-cancel, SHFFL, wavedash, JC grab, JC up smash, shield drop, waveshine, shine-grab,
aerial into shine, ledgedash, JC shine, multishine, SHDL, Illusion, shine out of shield.
A line under the drill's description says what is asked now (`Drill.status`: the deck's
scenario, the Illusion level, the rays reached).

Found on the way: a live pad, as `pads` reports it between frames, is the one sampled for
the coming frame, so the engine saw a press a frame before the state it starts (on a
timeline, Jump on 5 and the jump squat on 6). The engine now takes the previous reading
(`Session.live_pad`); scripted pads were right already.

Host additions: `project X Y` (a stage point in the picture, through the match camera, as
the name tags do), `rebirth P X Y`, `anchor P 1|0`.

### Closing the window (2026-11-13)

The owner: "the game still seems to freeze on closing as well" (a desktop dialog,
"melee_native is not responding"). Closing the window reached `exit(0)` from the frame
loop, and the teardown it runs (Dawn's and SDL's) never returned. The window build now ends
the process with `_exit` once its output is flushed, on a close, on `quit` and when the
driver goes away (`host_quit`); the system frees the window and the GPU's memory. A
drill's tries are saved even when the game goes away in the middle of it.
`tests/client/close.py` closes the window as a desktop does (`Window.close_window`, a
WM_DELETE_WINDOW message): the game is gone 0.03 s later and the tries are in the save.

### L+R+A+Start, and matches the game ends itself (2026-11-13)

The owner: "pressing start + LRAB crashes the game, it shows the no memory card screen,
then it crashes!" L+R+A+Start in the game's pause ends the match (no contest), and the
game then asks which mode comes next. The host passed it the game's own boot choice: the
memory card check, then menus the native build does not provide for. Also, the fighter
report went on describing the fighters of the ended match from freed memory, which the
client reads every frame.

Now (`src/host/match.c`): once a driver has asked for a match, the game never goes back to
its own scenes; a match it ends itself is followed at once by the same match again, and
counted (`state`'s "ended"). The fighter report, `fp` and placement check that a fighter
still exists (`host_live_fighter`). The client leaves a match or a drill when the game
ended it, as it does when START is held (`Client.game_quit`). `tests/client/versus.py`
does it with the keyboard: pause, hold L+R+A, press Start; the client is back on the
opponent screen and the game in a fresh match.

Found on the way, not fixed: a stock match (`match ... stocks`, new) does not end when a
fighter loses its last stock. The fighter stays dead and nothing follows; probably the
end-of-game sequence waits for something the native build does not have (sound).

### Sound (2026-11-13)

The owner: "audio doesn't work at all. Let's add the native sound effects to our menu
navigation + button clicks as well as the main menu music and ensure in-game audio works
as well!"

The game's sound code is decompiled and runs as it is: Melee's lbAudio, sysdolphin's
AXDriver (sound scripts) and synth (voices, sound banks, music streams). Under it the
console has Nintendo's AX library and the DSP, which every 5 ms reads 64 voice parameter
blocks, decodes DSP-ADPCM from audio RAM, resamples to 32 kHz and mixes. That layer was a
stub (one shared dummy voice); it is C now, in the host: `src/host/audio.c`.

| Piece | What it does |
|-|-|
| Voices | 64, given out by priority (a higher one drops the lowest, whose callback the synth gets), freed, and set the way the game sets them: addresses, ADPCM coefficients and loop context, resampling ratio, volume and its ramp, left/right mix |
| Mixer | Every 5 ms of game time (3.34 per frame at 59.94): the game's AX callback (its sound scripts), then each playing voice decoded (ADPCM, PCM16, PCM8), resampled linearly, looped or stopped at its end address, mixed to stereo |
| Output | The window build: SDL's default device, 32 kHz stereo, started once 64 ms is queued, new sound dropped when 200 ms is waiting. `MELEE_AUDIO=0` turns it off; `MELEE_AUDIO_RAW=FILE` writes the mix to a file instead (tests, any build) |
| Not done | The aux buses (reverb, chorus, delay: AXFX is a no-op), surround, ITD |

Two things the data needed:

- **Words.** The disc layer gives sound files to the game in 32-bit words of host order
  (`dvd.c`), so a pair of 16-bit fields in them (an address's high and low half, two
  ADPCM coefficients) is one word with the first field in its top half. The game reads
  some of these pairs as one word itself (a voice's current address, the ratio it
  writes). The AX calls read structures that come from files by the word, and keep the
  ones the game builds (volume, mix) as fields.
- **Music streams** (`.hps`) were not converted at all: the stream player reads the file's
  0x80-byte header and each block's 0x20-byte header as words and sends the sample data
  to audio RAM. `dvd.c` now walks a stream's block chain once and swaps exactly those
  headers.

Headless, sound stays off unless a file is asked for: every voice is the old dummy block,
which nothing writes to, so the game takes the same paths as before (`compare.py
--tolerance 1e-4` identical; nothing in the sound code draws random numbers).

`tests/native/audio.py` (7): the main menu's music, as the game streams it block by block,
correlates 1.0000 on both channels with an independent decoder of the file (written in the
test) over four seconds, at 0.70 of the file's level (the game's volume); stopping it fades
to silence; a menu sound plays and ends; a match makes sound.

The client (`client.py`, "sound"): the main menu's music (`menu01.hps`, song 52) on every
menu screen; the game's own menu sounds as its menus use them (`mn/inlines.h`: back 0,
forward 1, move 2): forward on A, back on B, a move when the focus moves (none when it
cannot), the same in the pause menu. A match keeps its stage's music (the game picks it,
sometimes at random, so the client does not); the host remembers which song the game last
started (`bgm` with no number, `host_pstream_start`), and going back into play from the
menus on the same match puts it back. Off screen the harness uses SDL's dummy audio driver:
no test reaches the speakers. `tests/client/sound.py` (12).

Host commands: `sfx N` (menu sound), `sound ID [VOL [PAN]]`, `bgm N` / `bgm -1` / `bgm`.

### How it feels: UCF, and when the controller is read (2026-11-13)

The owner, after playing: "I also feel like the gameplay feels slightly off; I am not sure
if we implemented UCF dash fixes correctly, dashback seems a little stuck, I am getting
stuck in my movement sometimes so I wonder if a frame is being eaten somewhere." Three
causes found:

1. **No UCF.** The native build played the vanilla game's stick handling. A dash back from
   standing whose flick the game reads half done spent four extra frames turning. UCF is
   now in the native build, on by default, identical frame by frame to Slippi's own code
   over six long seeds: "In the native build" in `ucf.md`.
2. **Hurrying after a late frame.** The pacer made up lost time by running the next frames
   back to back (up to 100 ms of it). Each frame reads the controller once, so those
   frames read it a millisecond apart, and to the game a flick across them is a slow one:
   the dash back that comes out as a turn. Now a frame more than 2 ms late starts the
   schedule again (`pace_wait`): the readings are never closer than about 14.7 ms. Off
   screen, with two deliberate stalls of 45 ms: one long gap each, nothing bunched.
3. **Reading after the window's events.** The controller was read after the window's
   events were handled, which takes a variable time; on the virtual display the readings
   were 2.6 to 28 ms apart in ordinary seconds. The adapter's reading is now taken as the
   frame starts (`host_gcc_take`): 16.6 to 16.8 ms apart. (The keyboard and SDL's
   controllers still need the events and are read after them.)

The pipeline itself drops nothing: each frame boundary takes one reading and the game
runs one frame on it (`lb_80019894` in `main.c`; the retrace count is the frame count, not
the clock).

Not known: how it is on the owner's screen. `python tools/melee_client/client.py --timing`
prints, on leaving, pictures shown late and controller readings closer than 12 ms, and
writes every second's numbers to `build/client-timing.log`: the spacing of the readings,
the adapter's reports, failed reads and reopenings, how old its newest report was when
read, and frames where the auto port found no adapter controller.

### Loading like TM-CE: no loading screens, no fast-forward (2026-11-13)

The owner: "Loading state shows a Loading screen and plays fastforwarded audio ... This is
the behavior I want, clean state loading, no audio played during that transition so it is
a quick, seamless experience! ... no loading screens, no chopiness, no fast forwarding",
with a screen recording of TM-CE's Edgeguard Training in Dolphin. In it an attempt ends
and the next begins between two frames: the old scene (timer 00:08) on one, the restored
one (00:00) on the next, no fade, no screen in between. TM-CE never reloads the match: its
savestate load (`savestate_v1.c`, `Savestate_Load_v1`) puts each fighter's data back in one
frame, then stops that fighter's sounds and the crowd's, removes every particle, the camera
shakes and the fighter's items, snaps the camera, and plays no sound of its own when the
event asks for a silent load (`Savestate_Silent`).

What the client did instead: a course drill whose next scenario had another opponent
(Marth, then Sheik, then Falcon in the shine out of shield deck) loaded a whole new match,
about 400 frames run as fast as the window could draw them (2.5 to 6 s with software
rendering) behind a "Loading" cover, and those frames' sound went to the speakers until
200 ms was queued, then was dropped: sped-up, chopped sound, and the music 200 ms late
from then on. Every move to another drill and every free play or Versus start loaded the
same way.

| Now | How |
|-|-|
| A new opponent in one frame | A match loads the deck's other opponents with it (`match ... CK...`): the overlay's character rotation, `src/melee/tm/rotation/rotation.c`, compiled into the native build, up to four fighters and its animation budget. `swap P CK` makes player P one of them (`tm_rot_SetFighter`, which keeps the slot a human slot so the drill still drives its pad). The course engine draws scenarios from the opponents loaded, as the overlay does (`Session.usable`, the bag); only a scenario chosen by hand whose opponent is not loaded loads a match |
| The next drill with no load | `Session(reuse=True)` (the client): a match the last drill left is kept when it is the same character and stage and has all of this drill's opponents loaded. Nearly every Fox drill is on Final Destination |
| A clean slate each attempt | `clean` (`host_clean`, `src/host/setup.c`), before the drill places the fighters: TM-CE's list, plus the stale-move queue (`plStale_ResetStaleMoveTableForPlayer`; TM-CE puts back the one saved at the match's start), so the tenth jab hits as hard as the first. Items are removed only when no fighter still points at them: removing Fox's blaster while he held it crashed the game in the blaster's code, and his own code lets go of it once he stands. Scenario drills played by a person clean too (`tools/melee_actor/scenario.py`) |
| A load nobody sees or hears | `quiet 1` ... `quiet 0` (`Client.load_quietly`): no draw pass (a tenth of the time: 0.4 to 0.6 s for a match with software rendering, against 2.5 to 6), no pacing, and the window keeps its last picture (`aurora_set_present_hold`, added to the Aurora patch). The first frame drawn afterwards is whole and shown at once. Sound: the stretch's first 150 ms goes through as ordinary real-time sound (the menu's click that started it, the end of what was playing), then nothing; afterwards the sound effects it started are keyed off and music it asked for starts from its beginning (`host_pstream_start` waits for the end of the stretch; starting the music again instead stopped a stream whose first read was still coming, and the stream's code fell over). The device then waits for its 64 ms lead again |

The "Loading" cover is gone from the client. Free play, Versus and scenario drills load
quietly too; the menu stays on screen meanwhile (a menu covers the game's picture anyway).
Not changed: the online match start (`online_match`), which still loads unpaced.

Two traps found on the way: a frame held from the screen asked for no surface texture,
and Aurora took the "Error" status that left for a failed surface and dropped it every
frame, until Dawn lost the device (the patch now skips that while holding). And the
harness's screenshots lag the screen by a frame, which first looked like a stale first
frame after a quiet load.

Tests: `tests/native/loading.py` (15, headless: four fighters loaded, a swap in one frame
with no new match and the pad driving the new opponent, a character not loaded refused, a
laser in flight cleaned but not the blaster Fox holds, a staled jab back to full damage, a
quiet load writing exactly the 150 ms tail and the new music playing after it);
`tests/client/loading.py` (10, off screen: the picture held through a quiet load with no
black frame, a sixth of the time of a drawn one; seven whiff punish attempts against Marth
and another opponent on one match; the next drill keeps the match). The course specs:
227 of 227, as before.

Not known: how long a quiet load takes on the owner's GPU (no drawing happens in it, so
it should be about the same as here), and whether holding the picture for half a second
is noticed when a load does happen (a stage change, a scenario chosen by hand, a solo drill
after one with an opponent).

## The target (owner, 2026-11-13)

"Our target to hit is 100% of everything implemented in native w/ native support for
slippi-ai in versus mode and lab!"

Where that stands, honestly:

| Part of "everything" | Native today | Missing |
|-|-|-|
| The game itself | Runs, draws, takes a GameCube controller, plays its sound and music; identical to the console's code on the compared matches | Reverb and the other sound effects buses. Known differences (`native-port.md`) |
| Menus | Main menu, character select, opponent and stage choice | Nicknames, the vanilla menus' other modes |
| Courses | Fox's hub and lists; 6 of his 46 drills play; the done mark | 40 Fox drills, the guide and demonstration, every other character's course |
| Versus | A match against a trained model, the CPU or nobody, six stages | Stocks, timer, result; 3 and 4 players; items |
| The Lab | Opponent choice, put back, damage | The rest of Training Mode's Lab: save states, recording, CPU behaviours, the info displays |
| Events | Nothing | All of Training Mode's events |
| Controls | The adapter is read directly; UCF 0.84 (Slippi's, frame for frame) | Layouts, nicknames' profiles, input delay: all exist only in the overlay build (`src/melee/tm/`) |
| slippi-ai | In Versus and the Lab, in real time | Projectiles and the partner Ice Climber in what the model sees; choosing a strength |
| Tandem play | Nothing | `netplay-p2p.md` is a study |

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
