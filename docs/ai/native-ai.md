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
| Lookahead: the next frames played with a planned pad, seen, and undone in the same frame (`ahead`); actor steps whose attacks commit only when the game says they land (`sequence`, `aerial`, `strike`); three drills' opponents built on them (option Opponent) | `src/host/ahead.c`, `tools/melee_actor/ahead.py`, `tools/melee_course/react.py` | `tests/native/ahead.py` (12), `tests/actor/react.py` (7), `tests/course/reactive.py` (6); "Attacks that land" in `melee-actor.md` |
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
| The game's past pictures in the interface: RmlUi draws a copy the game made (`GXCopyTex`) where a document says `gxcopy://N`; copies to the host's ring keep one size (the coach, `src/host/frames.c`) | `tools/aurora32/aurora-0002-copy-views.patch` |
| The host loads a document and changes it by element id: `ui load|class|text|attr|hide|show|font` on the control pipe. It knows nothing about menus | `src/host/ui.cpp` |
| `pads`: what a live port's person holds. `capture`: the game gets a pad at rest meanwhile, so a press meant for a menu does not also reach the game underneath | `src/host/window.c` |
| The screens as markup, the look, the roster (names and traits from `data/characters/`, course sizes from `data/courses/`), the flow | `tools/melee_client/` (`screens.py`, `style.rcss`, `characters.py`, `client.py`) |
| The typefaces (Barlow, Barlow Condensed, IBM Plex Mono; Open Font License), fetched once into `build/ui/fonts/` | `tools/melee_client/fonts.py` |
| The game's portraits and series emblems, read off the disc into `build/ui/art/`; Sheik's drawn from her model | `tools/melee_client/art.py`, `src/host/studio.c` |
| The stage select's art: the game's name logos off the disc, each stage drawn by the native build (whole for the card, from above and to one side for its panel), its blast zones and ledge read from the running game (`studio stage`), into `build/ui/art/stage/` | `tools/melee_client/stages.py`, `src/host/studio.c` |
| The menu panels' large faded drawings, made into pictures with rsvg-convert | `tools/melee_client/marks.py` |
| Costumes: `costume P N` on the control pipe (`Native.costume`), kept for every match set up after, a drill's own too | `src/host/match.c` (`HostMatch.color`) |

The flow lives in Python, like the trainer: the client steps the game a frame at a time,
reads the pad and tells the host what to show.

| Screen | What it does | From |
|-|-|-|
| Main menu | Versus (the big panel), Train, Settings, each with its faded drawing | `screens.main_menu` |
| Character select | 25 places, each with the game's own portrait over its series emblem (Zelda and Sheik share one: Sheik first, X on the card turns it into Zelda and back); the card shows the portrait standing out over its top, three style words, weight, fall speed, jump squat, and the costumes (Y), the one chosen worn in every match after | `data/characters/<id>.md`; the art: `tools/melee_client/art.py` |
| Course hub (a character with a course: Fox) | The four parts, how many drills each has, how many are marked done and how many play in this client; the Lab; where you left off (X continues) | `data/courses/<id>.md` through `courses.py` |
| A part's drills | Every drill of the part in the course's order, with its goal, opponent, what it builds on and leads to; tries, success and best run; **Y marks it done** (the owner's rule for now: the player decides) | the part's plan table |
| A drill | The scenario's opponent against the player, attempt after attempt: a small banner at the top of the game with the verdict ("Success" or "Failure": the owner's word, 2026-11-13), and in the column this try's checks, the last ten, tries, success and best run. Hold START to leave | `data/scenarios/*.json` through `melee_actor.scenario.Session(person=...)` |
| Versus | Your character, then the opponent: which character, who plays it (X turns through a trained slippi-ai model for the pairing, other models, the game's CPU, nobody), then the stage select. A match with the sidebar put away (START held shows it) | `tools/melee_client/opponents.py`, `melee_actor/policy_server.py` |
| Stage select | The six stages as panels with the native build's pictures of them, three to a row; the card shows the stage whole, the game's name logo, its width, platforms and blast zones; X picks one at random and starts | `screens.stage_select`, `tools/melee_client/stages.py` |
| The Lab (in Train: the course hub, or A on a character with no course) | The same choice with nobody playing the opponent unless asked, then the stage; D-pad down puts both back, left and right set the opponent's damage | the same |

**Versus first, the Lab in Train, a stage select (2026-11-14).** The owner: "Let's move
Lab into Train, it should replace the free play button (clicking this should allow the
user to select the character and stage". "Versus should replace the Train tile, then Train
should replace Lab", Events out of the menu (Training Mode's events are to come back as
drills in Train, in this interface), a stage select after the characters "similar to
character select that uses the real stage icons with a preview", and "ensure all menu
items have a faded icon like in the mockups". The canvas's row "Versus first, the Lab in
Train, and a stage select"; the owner chose layout A, and asked for "higher resolution
images for the stage selection badges ... native angled screenshots": the disc's icons are
58 by 50 pixels, so each panel is the stage drawn by the native build from above and to one
side, empty (the fighter put to sleep: no fighter, no damage display), with the studio
camera, at twice the size shown. The game's own name logos stay (off the disc). The
pictures are drawn the first time the client starts, beside it, in about 30 seconds (the
name logo stands on each panel until then); `python tools/melee_client/stages.py --render`
draws them again. The main menu opens with Train in focus (the client is for training;
Versus is the big panel). Free play is gone: the Lab took its place. **Versus hides the
sidebar** ("it is only really relevant in training mode"): a Versus match, local or online,
starts with it put away; START held shows it for that match without changing what the
player keeps; drills and the Lab keep it as it was. `tests/client/stage_select.py` (16
checks); `menu.py`, `versus.py`, `course.py`, `sound.py`, `portraits.py`, `fullscreen.py`,
`settings_menu.py` and `online.py` follow the new layout.

**The character card: behind a wall (2026-11-14).** The game's portraits end flat at the
bottom and the right of their frame, and the card's ink edge cut across each one. The
owner chose the canvas's "A · Card: behind a wall" ("but I also want a line in between the
character and the name so we can hide the cutoff right side"): the ink below is a wall in
front of the character with a lit top face, and an upright post stands between the
portrait and the name, from the card's top down to the wall; each casts a soft shadow on
the character. The post is upright, not slanted like the panels, because the cut it hides
is upright: at 12 degrees a thin post drifts 40 dp over the card's height. All of it inside
the card ("scale down the character and the wall so it fits within the card, I don't want a
line bleeding out of the container"): the portrait, smaller, has its frame's top and left
edges on the card's (13 of the 25 portraits are cut at the top too, and there the cut is
the card's edge), its bottom behind the wall. `screens.art_head` (the character select's
card and the opponent screen's).

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
placeholders), panel icons, sound.

**Character art (2026-11-13).** The owner asked for the character artworks "instead of
just a chemical element" (the two-letter panels), in a style that "uses the original art
but builds on it", and picked direction A of three mockups (the design canvas, row
"Character select with the game's art"): each panel the character's colour with its
series emblem and the game's own select-screen portrait, the card's portrait standing out
over its top edge. The art is Nintendo's, so it is never in the repository: `art.py` reads
it off the disc (`MnSlChr.usd`: 118 portraits, every costume, and 13 emblems; where they
are is in its docstring) into `build/ui/art/` when the client starts, and the documents
name the files by `file://` paths.

Sheik has no portrait on the disc: the game shows her in Zelda's place. The owner: "Render
Sheik (this should be default, there should be a button on the character card to switch
to zelda". `art.py` draws her, once per costume (half a minute, in a process of its own
that the client starts the first time; her place shows her emblem until then): a match
with her alone, frozen, everything but the fighters left undrawn, the developers' free
camera close (`studio` on the control pipe, `src/host/studio.c`), a picture on black and
one on white. The difference between the two is how much background shows through each
pixel, so her outline keeps its soft edges; she is cropped and given the shadow the game's
own portraits have (measured on them: 10 pixels left, 9 down, black at about 45%). Her
standing pose, seen three-quarters as Zelda's portrait is: her taunt turns her back to the
camera, her needle charge and her attacks crop badly. `tests/client/portraits.py` (14
checks): the pictures in the documents, 25 places, Y the costume, X Sheik into Zelda and
back on her panel and card, a match as Zelda in the costume chosen (the fighter reports
its costume), Y on the opponent screen. Online matches keep both players in their default
costumes: the friend's game does not know the one chosen here.

Two things RmlUi needed: `clip: always` on a box that clips its positioned children (it
clips only what it counts as overflowing, which leaves them out: the portraits spilled out
of their panels), and a 2-pixel transparent border round every portrait (the renderer
wraps a picture's edges round, which drew a line of the cut at the bottom of the body over
the top of the head).

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
| START tap | The client's pause menu over the frozen match (`freeze`: the game's developers' pause, which stops gameplay and goes on drawing): a sheet with tabs, L and R between them (below, "The coach"). In a drill, Drill: resume, restart, the drill's own settings (its options from the C, the scenario, the CPU's side, the stage where it has several), the coach, the input display, the guide, hide the column; Course: the drill list, the course, the main menu; Settings: input delay, input display, coach; and the drills before and after as two buttons. In free play and Versus, Match: resume, the input display, the column, back or opponent select, main menu; Settings. A drill setting changed is in force from the next try |
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

### The coach, the input display, the pause sheet (2026-11-14)

The owner, 2026-11-13: "If they are struggling to get it, a helpful overlay should pop up
that tells them what they are doing wrong with visual explanations of what they are doing,
the inputs they are pressing, what it should look like, and how they need to modify their
inputs ... (this should replace the Help essentially that has the CPU do it)", "a gamecube
controller overlay that shows inputs ... TM-CE has this already so let's reuse it", and a
cleaner pause menu "with icons". Built from the canvas's approved boards (PauseIcons,
CoachCard, CoachReplay; memory `ui-mockups-canvas`).

**Input display** (`src/host/inputs.c`, control `inputs MASK`, `Native.inputs`): TM-CE's
`Inputs_Init`/`Inputs_Think` (lab.c) in C against the decomp, with TM-CE's own controller
model from `lab.dat` (put on the disc as `files/TM/lab.dat` by `tools/tmce_disc.py`; not in
the repository). A controller per shown port at the top right of the picture; sticks and
triggers move, buttons turn white, from the fighter's input record (after the input delay;
a CPU's too). Two departures: it draws on GX link 11, the HUD's, because no camera of the
native match draws TM-CE's link 12; and the display keeps everything in its own GObj's user
data and is looked for among the match's GObjs each frame, so a state loaded from before it
existed (every reset of a drill) makes it again instead of leaving a dangling pointer. The
setting is `settings["inputs"]` (off, you, opponent, both), in Settings > Display and the
pause menu; the client sends the mask when a match or drill screen loads and 0 on leaving.

**Pause sheet** (`screens.pause_tabs`/`pause_rows`/`pause_nav`, `Client.pause`): as the
canvas, with our own line icons (`tools/melee_client/icons.py`, drawn on a 24 grid and
made into PNGs with rsvg-convert, tinted per row). A on a value does nothing; left and
right change it ("A Choose, D-pad Change"). Demonstration left the pause menu (it is not
on the approved board): the guide's D-pad right still plays it, and the coach's replay
shows it.

**Coach** (`tools/melee_client/coach.py`, `Client.coach`, `Client.coach_tech`,
`screens.coach_card`): after N misses in a row in any drill that plays in the client, the
course engine's and the four judged by the frame (`settings["coach"]`: off or 2 to 5,
default 3; Settings > Display and the pause menu), a card over the frozen game:
- the headline: the judge's own when it gives one (a tech drill: "Jump held 2 frames too
  long", "Air dodge 3 frames late", "L 2 frames early"), else the first timeline row off
  its window ("Dodge 5 frames late", "No jump in time"), else the drill's verdict;
- the try against the target, played side by side in the game's own pictures (below):
  from 8 frames before the timeline to a moment after the try ended, at the game's speed
  and the timeline's frames at half of it, a short stop on the last frame and again (at
  first the timeline went at a quarter, each picture held four frames, with a longer
  stop: "freezes often and is slow to loop", the owner, 2026-11-14). Each panel shows the
  frame ("F4"), a tag where a press starts ("F1 · JUMP"), how far along it is, and an
  **input display** of the pad on that frame (`screens.pad_display`: the triggers with
  Z, the control stick and the C-stick in their gates, B A X Y; SmashWiki's button icons,
  lit while held), the try's pad beside the target's ("ensure that coach overlay has
  input displays on both what you did wrong and what it should look like"); the grid's
  column for the frame is marked as it plays. **Frame by frame**: the D-pad (or the
  stick) left and right step both panels a frame back or on and pause there, up plays on
  ("frame by frame controls too so they can really see what the inputs should be like vs.
  what they are doing!"). Each panel is cropped to where the fighters were all through
  it (the player alone in a tech drill). The target of a course-engine drill is its
  demonstration played unseen (`quiet`) from the same situation: the same scenario, the
  same draws (`Session.run` with the try's `scenario_index`; run 0 draws the same
  numbers), and the session put back afterwards (`keep_session`/`restore_session`: the
  drill's own fields, the session's counters and random state). The target of a tech drill
  is **the try itself with what was wrong put right** (`tech.Session.corrected`: the
  player's own inputs, the jump let go before jump squat ends, the air dodge on the first
  frame in the air with the stick down and to the side, L three frames before landing, a
  neutral air, a fast fall at the top and L as it comes down), played from a state saved
  before the try and judged again: the card says what the judge made of it ("The same
  try, put right: Short hop");
- the inputs frame by frame (the result's timeline: yours filled, frame-perfect outlined,
  the allowed window shaded) with a bracket "5 FRAMES LATE";
- "How to fix it": the judge's own when it gives one (a tech drill), else the frame to
  press on and by how much, then the drill's timeline note (or its guide's first
  sentences without a timeline).
A or B go on; Y replays the try. When the card closes the game is put back as it was
when it opened (state slot 29, `COACH_NOW`): a tech drill goes on from where the player
stood.

**The game's own pictures** (`src/host/frames.c`; the owner, 2026-11-14: "doesn't seem we
have a robust animation system as well, chain grab doesn't have any visuals. Need to ensure
this is generic and works across the board"). While a drill plays, each frame the game
draws is copied out of its frame buffer at 480 by 360 (`GXCopyTex` at the frame boundary,
before Aurora ends the frame) into a ring of the last 300: Aurora keeps a copy as a GPU
texture under the address it was copied "to", and those addresses are a static array of
`frames.c` that nothing writes. A second patch to Aurora
(`tools/aurora32/aurora-0002-copy-views.patch`) lets RmlUi draw such a copy wherever a
document says `<img src="gxcopy://N">` (`aurora_rmlui_copy_view`: which copy view N shows,
looked up when drawn, so nothing is cached or uploaded), and keeps copies to the ring at
that size whatever the window's (`aurora_set_copy_exact`): 0.7 MB each, 370 MB for both
rings full. A copy is made in `GX_TF_RGB565`, which Aurora converts with the alpha set to
1, so the picture is opaque under RmlUi's blending. Ring 0 is the live game; ring 1 a run
played unseen, which `quiet 2` draws without showing (the window keeps its last picture,
no sound, no pacing) where `quiet 1` does not draw at all. Each picture keeps where the
fighters were on screen (their feet and 20 units above, per port), for the crop. A
picture's number is the frame number a driver is told after stepping it, so what the
driver read of the game then is what the picture shows. Control: `frames rec|clear|range|
view|box` (`Native.frames_*`). The rings are not part of the game's state: a state load
leaves them alone. A game built before `frames.c` makes the card fall back to drawn paths
(the player's position frame by frame).

**Tech drills: saved states.** A drill judged by the frame (`tech.py`) has no reset: the
player sets the pace. While the player is between attempts the client saves the game's
state every 12 frames into slots 30 and 31 in turn (3 to 6 ms each, 69 MB; only with the
coach on), and records the try frame by frame as the course engine's drills are
(`Client.record_tech`: the last 240 frames, rolling). The target and the replay start from
the latest of those saved at least 8 frames before the attempt began (else the earliest
from before it), with the recorded pads (after the input delay) given to a scripted port.
`tests/client/coach_tech.py` checks the replay reaches the try's last frame with the
fighter in the same place and state.

**The replay's crash (fixed 2026-11-14).** The owner's first replay in a tech drill
aborted the game inside Aurora (`push_uniform` on the GX worker thread). `host`, which
holds whether the draw pass runs, is among the statics a state saves; the replay loaded
its saved state inside a `quiet 1` stretch, which had turned drawing off, and the load
turned it back on. The game then drew frame after frame with no frame of Aurora's begun:
Aurora keeps such commands queued until the next frame, which took them all at once,
past its 24 MB of uniforms a frame. `host_state_load` now keeps `host.draw`; the window
build's draw pass is skipped whenever no Aurora frame is open (`host_window_drawable`,
`cuts.c`); and a replay's unseen frames are drawn (`quiet 2`), because what the game
draws takes random numbers (its effects) and a run played again undrawn is not quite the
run it was. Reproduced with a save, `quiet 1`, a load and 60 frames (the game aborted),
and gone after the fix (240 frames).

**Replay** (`Client.replay`, `screens.replay_view`): the try played again from its reset
with the pads the game was given in it (recorded each frame in `Client.record`: the
engine's `live_pad`, which is after the input delay; the port `scripted`, so the
controller is read but not played), the pad held through the placement frame put back too
(a C-stick held from the last try is not a fresh flick). The timeline's frames (and 8
before) at a quarter speed, the player's controller shown, a frame strip along the bottom;
D-pad right a frame on, left a frame back (played again unseen to there), A play/pause, Y
the target instead (the demonstration from the same start) and back, B to the card.
`tests/client/coach.py` checks that the replay ends as the try did.

Departures from the boards: "what it should look like" is played beside the try, not
onion-skinned over it (the frames are the game's own pictures, so a still of overlaid
frames would be overlaid backgrounds too); the replay's target is played in place of the
try (Y), not a translucent ghost over it (one fighter, one game). Not done: a replay of a
course-engine flow drill's try that carried on from the last one (it did not start from a
reset; Y is not offered; the tech drills' saved states would do it); the coach for a drill
played from a scenario file against an opponent (`scn.Session`; none of the course's drills
is played that way now).

`tests/client/coach.py` (10): the sheet's tabs, Input display set and kept, the game made
the controller, three misses open the card, its paths, the replay to the same verdict,
back to the drill and the list. Pictures with `--shots DIR`.

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
| Chain grab fastfallers | Goes on until the player drops it ("let them cook! we should even let them tech chase, if they miss the follow up though reset"): any throw, regrab or hit keeps the chain; the CPU DIs, techs in place, away or in (or misses) when it lands in tumble, gets up, rolls or attacks from the floor, and jumps away as soon as it is free; free for 10 frames, a double jump or a getup attack that hits ends it, and the result says how long it was (option Count From: the regrabs that make it a success). `tests/course/chaingrab.py` (2) |
| ASDI down and crouch cancel (was one drill, "ASDI down and crouch cancel"; second note session) | Two drills ("Both of these are very important"), `tools/melee_course/drills/defense_asdi.py`. Each a deck of moves: Marth down tilt and fair, Sheik forward and down tilt, and for crouch cancel Falcon's nair (it launches a standing Fox at any percent). The player's percent is picked where the hold works against the move (or just under its limit: option Percent). The CPU shields once it can act (ground moves: its animation's interrupt frame; aerials: landed and standing); the punish must land before. ASDI down: standing, the C-stick down as the freeze ends; crouching there is a crouch cancel and does not count. The limits are measured on the native build and checked at the limit and 8% past it: `tests/course/asdi.py` (16). The landing after an ASDI-down hit lasts as long as the hitstun but can be left after 4 frames (`ftCo_Landing_IASA`), which is what a punish uses |

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

Also from the second notes: a drill's reset sent the player's own port a neutral pad,
which beat the controller for a frame, so a C-stick held through the reset (to keep ASDI
down) was read as a fresh flick and Fox down smashed on every attempt's first frame. In
live play the reset leaves the player's pad alone (`Session._reset`). And the D-pad or a
changed pause option between two attempts (the frames left to read the verdict) ended the
client; they are handled as in an attempt now (`Client.course_abandon`,
`tests/client/between.py`).

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
| A new opponent in one frame | A match loads the other opponents with it (`match ... CK...`): the overlay's character rotation, `src/melee/tm/rotation/rotation.c`, compiled into the native build. `swap P CK` makes player P one of them (`tm_rot_SetFighter`, which keeps the slot a human one so the drill still drives its pad). The course engine draws scenarios from the opponents loaded, as the overlay does (`Session.usable`, the bag) |
| Every deck whole | The overlay is held to four fighters by the console's memory: the animations that do not fit the preload heap load into the game's audio RAM heap as each fighter is made, and that ran out ("memp_kouho" in `lbmemory.c`). The native host has 64 MB of audio RAM (`HOST_ARAM_SIZE`), the game's 16 MB clamp is patched out for the native build only (`PATCHES` in `tools/native_build.py`, `lbmemory.c`), and the rotation's limits are raised there (`tm_rot_SetLimits(8, ...)` in `match.c`): eight fighters, the preload cache's entries. Fox with the shine out of shield deck's six, and eight of the heaviest (Bowser, Donkey Kong, Ganondorf, the Ice Climbers, Zelda and Sheik, Mewtwo, with Fox and Marth), load and swap back and forth. The overlay keeps the console's limits |
| The next drill with no load | `Session(reuse=True, also=...)` (the client): a match also loads the rest of the course's opponents (`Client.course_opponents`, the most used first; Fox's course has seven, so a match holds all eight fighters), and the next drill keeps it when it is the same character and stage and has all of that drill's opponents. A drill without an opponent keeps it too, its opponent asleep (`sleep P`, `host_sleep`: the game's sleep state, as between a lost stock and the respawn, so not drawn, not hit, not followed by the camera; its damage display removed, `ifStatus_802F6788`); placing the opponent again wakes it (`wake` in `host_place`, `host_ledge`, `host_rebirth`: `Fighter_EnterRebirth` and the damage display back). In Fox's course only the shield drop (Battlefield) and the drills played from scenario files load a match after the first |
| A clean slate each attempt | `clean` (`host_clean`, `src/host/setup.c`), before the drill places the fighters: the fighters' sounds and the crowd's stopped, particles ended (through the game's own delete: their life set to one frame), the fighters' free items destroyed, colour overlays off, and the stale-move queue emptied (`plStale_ResetStaleMoveTableForPlayer`; TM-CE puts back the one saved at the match's start), so the tenth jab hits as hard as the first. Items are destroyed only when no fighter still points at them: destroying Fox's blaster while he held it crashed the game in the blaster's code, and his own code lets go of it once he stands. TM-CE's camera shakes are left alone (below). Scenario drills played by a person clean too (`tools/melee_actor/scenario.py`) |
| A load nobody sees or hears | `quiet 1` ... `quiet 0` (`Client.load_quietly`): no draw pass, no pacing, no Aurora frames at all, and the window keeps its last picture (`aurora_set_present_hold`, added to the Aurora patch): 0.28 s for a match with software rendering, against 2.5 to 6 drawn. The first frame drawn afterwards is whole and shown at once. Sound: the stretch's first 150 ms goes through as ordinary real-time sound (the menu's click that started it, the end of what was playing), then nothing; afterwards the sound effects it started are keyed off and music it asked for starts from its beginning (`host_pstream_start` waits for the end of the stretch; starting the music again instead stopped a stream whose first read was still coming, and the stream's code fell over). The device then waits for its 64 ms lead again |

The "Loading" cover is gone from the client. Free play, Versus, scenario drills and the
online match start load quietly too (online, both sides load the same way, so the two
games stay the same); the menu stays on screen meanwhile. Online, the quiet stretch ends
before the 10 frames both games play ahead of the session, not on its first frame: the
music the match asked for starts as the stretch ends, and with its stream's first read
still on its way when rollback began, Alpha's game hung in `tests/client/online.py`'s
leave step in 3 runs of 4 (another session's bisection). Ended earlier: 9 runs of 11
passed whole; one hung in the leave step and one did not reach "Leave match" in its 200
frames. The rest was the menu sounds: the client played them through the game during a
session (every A or START in an online match), on one side only; it no longer does
(1acbda006, which also gave the test's leave step more frames), and 5 runs of 5 passed.

Traps found on the way:

- TM-CE removes "camera shake" objects as class 3 on link 18. The stage's objects are
  class 3 too (`HSD_GOBJ_CLASS_STAGE`), and the camera keeps a pointer to its looping
  shake (`Camera_RequestQuake`'s `quake_gobj`): freeing them crashed the game in the sixth
  shine out of shield attempt (another session's long run found it, at the 45th). A
  one-shot shake ends by itself after 22 frames, before a verdict's pause is over.
- A frame held from the screen asked for no surface texture, and Aurora took the "Error"
  status that left for a failed surface and dropped it every frame, until Dawn lost the
  device (the patch skips that while holding).
- A match asked for in the frames right after another settled is not started at all;
  `start()`'s 30 frames before asking are needed between matches too.
- The game's "no Ready, no GO" switches (the rules' `x1_2`, `x1_3`, which TM-CE's events
  and All-Star mode set) change nothing in the debug VS mode the host uses: it has no
  countdown to skip.
- The harness's screenshots lag the screen by a frame, and the last picture before a quiet
  stretch can reach the virtual display a frame late.

Tests: `tests/native/loading.py` (24, headless: the six-opponent deck loaded whole, a swap
in one frame with no new match and the pad driving the new opponent, a character not
loaded refused, sleep and wake, a laser in flight cleaned but not the blaster Fox holds,
a staled jab back to full damage, eight shine out of shield attempts in one match each
cleaned, eight of the heaviest fighters, a quiet load writing exactly the 150 ms tail and
the new music playing after it); `tests/client/loading.py` (11, off screen: the picture
held through a quiet load with no black frame, a tenth of the time of a drawn one; the
first drill from the menu loading the course's opponents, all of shine out of shield's six
there and seven attempts against them on one match; a drill without an opponent keeping
the match with Marth asleep; the next drill against Marth keeping it with Marth back).
The course specs: 227 of 227. The overlay's shine out of shield specs (28, which use the
rotation) pass in the simulator.

Not known: how long the first load from the menu takes on the owner's GPU (1.5 s here,
counted from A to the first attempt, with eight fighters loaded and software rendering),
and whether the half-second hold at a stage change is noticed.

### Settings: input delay, rumble, volumes (2026-11-13)

The owner: "do we have the frame delay from slippi built in yet? We need that so practice
is consistent. Normally it defaults to 2 frames of input delay. We need to build out a
Settings menu in the main menu ... (move Controls into a submenu in settings)", then, on
the mockups (the canvas's Settings row): "Frame delay should just be a suboption in
Controls I feel, make Controls the headliner ... Make sure that we have rumble support in
controls as well", and no numbers on the panels.

The main menu's fifth panel is Settings: Controls big, Online, Sound and Display beside
it. Each opens a list of rows with the row in focus edited in a dark panel. Kept in the
progress file under `settings` (`tools/melee_client/settings.py`) and given to the game
process when the client starts and whenever one changes.

| Row | What it does |
|-|-|
| Controls: Input delay | 0 to 9 frames, 2 unless changed (Slippi's online default). A live port's press reaches the game that many frames after it is read (`delay N`, `host_window_delay` in `window.c`: a queue per port in `read_live`). What the person holds (`pads`) is not held back, so the client's menus answer at once; what the game is given (`pads game`) is, and the course engine, the tech judge and the escape drills read that one, so a press lines up with what it did. A netplay session delays the local pad itself (`net.c`), so the queue adds nothing there; online the session's delay is the one the player chose here |
| Controls: Rumble | The game's own rumble (`PADControlMotor`, a generated stub until now, records each port's motor in `hw.c`), passed to the controller the port reads: a GameCube controller on the adapter (its `0x11` command, sent by the reader thread, `gcadapter.c`) or another controller (`SDL_RumbleGamepad`, renewed with a 500 ms duration so a game that dies does not leave it running). On or off per port (`rumble P 1|0`), stopped while a menu is up, "Feel it" (X: `rumble P test 30`). Matches enable rumble for people's ports, as `gm_LoadRumbleEnabled` does; whether it reaches a controller is the host's, outside the game's state, so both sides of a netplay session keep one game. The adapter's motors are stopped when it is opened and when the game quits or its window closes. Nintendo's adapter powers motors through its second (grey) plug |
| Controls: UCF | On or off for practice; online always on (both games must be the same) |
| Controls: Button layouts | Said to be next: they exist only in the overlay build |
| Sound | Music, effects (matches and drills) and menu sounds, 0 to 100 in tens. Mixed apart outside the game (`volume MUSIC SOUND`, `host_window_gain`): a voice is music when its samples came from a `.hps` file (`host_aram_file`, `audio.c`'s `is_music`). The client gives the effects' volume in matches and the menus' on menus |
| Display | Fullscreen or a window, the window's size (1280x720 to 2560x1440), the sidebar shown or hidden (also START held in a match; kept) |
| Online | The nickname (X pastes it), the code's UDP port, the friends met (Y forgets one), and the router: two STUN servers asked from one socket, "Open" when both saw the same public port (`online.router_check`; only when A is pressed) |

The online screen (Versus, Online) is redrawn as the canvas's "Versus: online" (the
owner: "I don't want any more plain looking menus or overlays (i.e. the front code is a
white box)"): the code as a ticket in groups of alternating colours, the router's last
check and the delay under it, a "Paste a friend's code" button, and the friends as
cards. It behaves as before (up and down, A, B).

Enabling rumble found a bug: LbRb.dat's rumble scripts (`op:3`, `frame:13` in a u16) were
read in x86 bit order, and the game looped forever on the first hit. `RumbleCommand` and
`HSD_Rumble` are `PPC_LAYOUT` now, as the other script types.

Tests: `tests/native/delay_rumble.py` (15: a press given 2 and 5 frames later and the
fighter acting that much later, a menu's capture, the game's motor on a hit and off
again, a port switched off, the keyboard's lack of a motor, and no adapter ever told
anything: the tests read the virtual display's keyboard only); `tests/native/volume.py`
(7: the menu's music at 100, 50, 0, a menu sound with the music at 0 and with the effects
at 0); `tests/client/settings_menu.py` (42, off screen: every row of the four screens, the
game process given each change, all of it kept and given again by a new client, no STUN
server asked). Not known: how the rumble feels on the owner's controller (nothing here
was felt), and whether the owner's adapter powers its motors.

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
| Controls | The adapter is read directly; UCF 0.84 (Slippi's, frame for frame); input delay (2 frames unless changed) and rumble, in Settings | Layouts and nicknames' profiles: they exist only in the overlay build (`src/melee/tm/`) |
| slippi-ai | In Versus and the Lab, in real time | Projectiles and the partner Ice Climber in what the model sees; choosing a strength |
| Tandem play | Nothing | `netplay-p2p.md` is a study |

## Plan

| Step | What | Proof |
|-|-|-|
| N1 (done) | The interface above; actor and policies on it | the three tests |
| N2 (placement done) | Setting up a situation from a command instead of from play. `Native.place(port, x, y, facing, air, percent)`: standing on whatever floor is at or below the point, or falling from it; not holding or held, no speed, a full shield (`src/host/setup.c`, the course engine's placement on the game's own functions). Stocks, items and the rest of a match's rules: not yet | `tests/native/place.py`, 11 checks |
| N3 (begun) | The actor's step library (`melee-actor.md`, A2). Done: steps are generators, so two scripts run at once; scenario files and a runner with a verdict as JSON; the conditions `target_attacking`, `target_swung`, `target_idle`, `target_frame`; `rush` (running grab, dash attack, jump-cancelled up smash, at measured distances), `throw`, `shield` (until it has blocked) and `oos` (shield grab, up smash, jump out of shield); `choose`, so an opponent varies what it does from run to run; attacks that look ahead before they commit, so they land whatever the player did first (`sequence`, `aerial`, `strike`; the drills fox-wavedash-back-punish, fox-anti-air and fox-shine-oos react). Not done: dash dance, wavedash, a step interrupted by being attacked, branching on what happened; the other drills' opponents | one scenario per step |
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
