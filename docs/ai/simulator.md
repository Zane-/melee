# Simulator: running the game without Dolphin

`tools/melee_sim/` executes the real DOL (vanilla code plus our overlay) in a PowerPC CPU
emulator (Unicorn) with the GameCube's hardware replaced at the level of SDK functions.
There is no window, no audio, no rendering and no real-time pacing: a match starts in about
0.3 s, runs at 50-160 frames per second, and can be snapshotted and restored in 5 ms.

It is the fast inner loop for developing and testing drills. Dolphin stays the ground truth
(`docs/ai/testing.md`); the same test specs run in both.

```sh
. .venv/bin/activate                       # needs: pip install unicorn numpy
OVERLAY_OUT=build/overlay-tmtest TM_TEST=1 python tools/overlay_build.py   # the test build
python tools/melee_sim/tmtest_sim.py tests/tmtest/shineoos/*.json          # specs, no Dolphin
```

## What it is

| Piece | File | What it does |
|-|-|-|
| CPU and memory | `machine.py` | Unicorn PPC32 big-endian, 24 MB RAM, DOL loader, the decomp's symbols (`config/GALE01/symbols.txt`, `splits.txt`, the overlay map), function hooks, constant stubs, guest calls, backtraces |
| Hardware | `hle.py` | Whole SDK objects stubbed (GX, VI, AI, DSP, AX, CARD, PAD, AR, most of OS); DVD reads served from `build/disc/files` through a generated FST; ARAM as a host buffer; one-shot OS alarms; pad state set by the host; `OSReport` captured; DVD/ARAM/alarm completions delivered like interrupts |
| Game loop | `sim.py` | Boot, one `step()` per logic frame, pad input, snapshots, `Sim.match()` |
| Test specs | `tmtest_sim.py` | `tools/tmtest.py` with the simulator as the backend |

How a frame works: the game's own loop (`gm_801A4D34`) runs unmodified. Each iteration it
waits for a pad sample (`lb_80019894`); the simulator stops there (one frame), then lets the
game sample the pad (`PADRead` returns what Python set) and run the frame's logic
(`HSD_GObj_RunProcs`). The render half (`HSD_StartRender`, the GX link pass, the XFB copy)
is stubbed. Nothing about fighters, physics, collisions, hitboxes, items, stages, the event
code or TM-CE is reimplemented: it is the shipped code.

Details that matter when something breaks:

- **Paired singles.** Unicorn has no Gekko paired-single instructions. In vanilla code they
  occur only in about 20 SDK matrix/vector routines (`PSMTXConcat`, `PSVECAdd`...), which are
  replaced with numpy float32 implementations; and as `psq_st` / `psq_l` register saves in
  code built with the newer compiler (TM-CE units), which are turned into nops at load.
- **Interrupts.** There are none. Completion callbacks are queued and delivered when the game
  re-enables interrupts (`OSRestoreInterrupts`, `OSEnableInterrupts`), at the frame boundary,
  and from the idle function every wait loop spins on (`lb_800192A8`).
- **Time** is emulated: 675,000 ticks per frame plus a little per idle call. `OSGetTime` and
  `OSGetTick` read it. Runs are deterministic.
- **Audio.** The HSD audio layer runs during boot (its init also sets up the DVD/ARAM
  request queue); every voice is one dummy block; after boot no sound bank is loaded
  (`lbAudioAx_80027168`, `lbAudioAx_8002785C` stubbed).
- **Memory card:** none inserted. The boot prompt is confirmed with A.
- **Stubbing code after it ran** needs `ctl_remove_cache`; `Machine.stub()` does it.
- **Instruction counting** (`run(count=...)`) makes Unicorn about five times slower; stepping
  uses a host timeout instead.

## Using it

Two ways in. For tests of an event, write a spec (`docs/ai/testing.md`) and run it with
`tmtest_sim.py`. For exploring an interaction, drive it from Python:

```python
import sys; sys.path.insert(0, "tools/melee_sim")
from sim import Sim

s = Sim.match("lab", "fox", "marth", stage="final-destination", free=True)

s.pad(0, ["R"], r=1.0)                       # Fox holds shield
s.pad(1, cstick=(-1, 0)); s.step(); s.pad(1) # Marth forward smashes to the left
for _ in range(40):
    s.step()
    print(s.fighter(0).summary(), "|", s.fighter(1).summary())

snap = s.snapshot()      # try something, then come back
s.restore(snap)
```

- `Sim.match(event, p1, p2, stage, seed, options, p2_human, free)`: the test build boots
  straight into the event's match with these characters (ids as in `data/characters/`),
  cached under `build/sim/fixtures/`. `free=True` is the sandbox: the event's per-frame
  logic is off and player 2 reads pad index 1, so both fighters do exactly what the pads
  say. Without it the event runs as in the game (the Lab forces player 2 to be a CPU every
  frame, for instance).
- `s.pad(port, buttons, stick, cstick, l, r)` holds until changed. `s.step(n)`.
- `s.fighter(i)` is a view at the time it is created: `state` (motion state id, `ftCo_MS_*`
  in `src/melee/ft/kinds/ftCommon/forward.h` or the character's enum), `state_frame`, `pos`,
  `vel`, `facing`, `airborne`, `percent`, `hitlag`, `hitstun`, `shield`. Anything else:
  `s.m.u32(addr)`, `s.m.f32(addr)` with offsets from `src/melee/ft/types.h` and addresses
  from `s.m.sym.addr("name")`.
- `s.call("function", args...)` calls a game function between frames.
- `s.h.reports`: everything the game printed with `OSReport`.
- `s.m.trace("function")` logs calls (name, arguments, caller) into `s.m.log`.

Getting a number out of the simulator (when a hitbox reaches, how long shield stun lasts at
a spacing, whether a follow-up is true) is usually ten lines and a few seconds. Do that
instead of guessing a `tune` value in a drill spec; then confirm the finished drill in
Dolphin.

## How far to trust it

Checked 2026-11-12:

- **Against Dolphin, same specs** (`tests/tmtest/`): 9 of 11 give identical result records,
  including a 19-attempt soak run with random scenarios and mid-match character swaps. Same
  shield-stun end frame, same shine frame, same distances to one decimal. Of the other two,
  one is identical up to a record Dolphin logs after `done`; the other (`peach_down_tilt`)
  stops in the simulator at preload with `memp_kouho`: the rotation preload chose Marth,
  Peach, Sheik (which brings Zelda) and Jigglypuff next to Fox, whose animation files
  (10.2 MB) exceed the 9 MB ARAM heap. That looks like a bug in the rotation preload that
  Dolphin's run did not hit; not yet explained why the two pick differently.
- **Against the frame data** (`data/framedata/`): Fox's short hop rises 2.1 then loses 0.23
  per frame; jump squat is 3 frames; shine freezes his fall; Marth's forward smash connects
  on frame 10.
- **Coverage:** all 26 characters ran 600 frames of random two-player input (hits, grabs,
  projectiles, deaths) in the sandbox without a fault. Boot, the character and stage select
  screens, the Lab and the Shine OoS event run. Other events, other stages than Final
  Destination and Dream Land, and other scenes (results, classic mode...) have not been run
  and may hit a hardware wait nobody has handled yet.

Known differences from the console:

- Matrix and vector helpers are computed in float32 with numpy, not with the console's
  exact instruction sequence, so bone and hitbox positions can differ in the last bits. No
  result differed in the comparison above, but a hit that connects by a hair could.
- The boot-time RNG seed (`OSGetTick`) differs from Dolphin's, so anything random before a
  test sets its seed can differ.
- No rendering: anything that reads back from the framebuffer or depends on draw timing is
  absent. Effects and cameras still run their logic.
- No audio: nothing that waits for a sound to finish will ever finish.

When the two disagree, Dolphin is right and the difference is a simulator bug to fix here.

## When a run stops

`GuestError` carries the reason and a symbolised backtrace.

| Message | Meaning | Usual fix |
|-|-|-|
| `unmapped read/write of 000000xx` | A stub returned 0 where the game expected a pointer | Hook that SDK function in `hle.py` with a plausible result (as `AXAcquireVoice`, `GXGetTexBufferSize`), or stub the graphics-only caller in `sim.py` |
| `frame N did not end within 60s` | A wait loop on something the HLE never completes | Read the loop in the decomp; deliver what it waits for (alarm, callback, status value) |
| `assert file.c:line` | The game's own assert | Usually a stubbed function's return value; the backtrace names the path |
| `Unhandled CPU exception` | An instruction Unicorn lacks | Print the opcode at the PC; paired singles outside the handled cases need a hook or a nop |

Keep fixes at the SDK boundary. Do not patch game logic to make the simulator pass: then it
no longer tests the game.
