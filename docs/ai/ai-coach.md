# AI coach design

Status: design proposal. Nothing is implemented. Items marked *unverified* come from memory of
how Dolphin works and must be checked against Dolphin's source before building on them.

## Goal

Claude acts as a coach inside the training build. It can:

- see what the player did (per-drill results, not raw video),
- say something useful on screen at the right moment,
- drive the training mode: pick a drill, set options, place fighters, load a state.

## Constraints

- A GameCube frame is 16.7 ms. A model reply takes seconds. **Claude is never in the frame
  loop.** The game emits events and applies commands asynchronously; it must run identically
  with no coach connected.
- The game has no network stack worth using. All model calls happen in a **companion process**
  on the host PC. The game only needs a byte pipe to it.
- Anything the coach changes during a netplay session must go through the same synced path as
  a player's menu input, or it will desync (see `slippi-tandem.md`).

## Architecture

```
 game (native C, src/melee/ai/)            host PC
 ┌────────────────────────────┐   bytes   ┌───────────────────────────┐   HTTPS
 │ telemetry → ring buffer ───┼──────────▶│ companion                 │──────────▶ Claude API
 │ command queue ◀────────────┼───────────│  session store, tool loop │◀──────────
 │ coach panel (text)         │   EXI     │  optional voice / overlay │
 └────────────────────────────┘           └───────────────────────────┘
```

### Game side (`src/melee/ai/`)

| Piece | Job |
|-|-|
| `ai_link.c` | Framed, non-blocking transport over EXI. Never waits on the host; drops telemetry when the buffer is full |
| `ai_telemetry.c` | Turns game events into compact records. Called from training-mode code and a few hook-table entries |
| `ai_command.c` | Validates and applies commands at a safe point in the frame (start of `EventUpdate`) |
| `ai_panel.c` | A text panel GObj for coach messages; reuses the TM message / tip system once ported |

Telemetry should be **semantic, low-rate records**, because that is what a language model
reasons about well:

- drill start / end with settings,
- per-attempt results the drills already compute (L-cancel timing in frames, wavedash angle and
  frame, ledgedash GALINT, tech direction, SDI inputs, punish damage, reaction frames),
- conversions: opening → punish → outcome, with percent and positions,
- optional sampled state (position, action state, percent) at a few Hz for context.

Commands are a small closed set:

- `show_message(text, duration, slot)`
- `select_drill(id)`, `set_option(menu_path, value)`
- `set_fighter_state(slot, percent, position, facing)`
- `save_state()`, `load_state()`
- `set_cpu_behaviour(...)` (maps to the Lab's CPU options)

The companion exposes these to Claude as tools. The game treats every command as untrusted:
range-check everything, ignore unknown IDs.

### Transport options

| Option | How | Pros | Cons |
|-|-|-|-|
| USB Gecko over EXI | Dolphin emulates a USB Gecko as a local TCP socket (*unverified*: slot B, port 55020, byte-wise commands) | Works with stock Dolphin; also works on a real console with real hardware; trivial protocol | Slot B is where Slippi Dolphin puts its own EXI device (*unverified*), so it may conflict with Slippi |
| Slippi's EXI device | Use the frame data Slippi already streams to the host; send commands back another way | No new game-side telemetry for basic data; replays for free | One-way; custom commands need a Dolphin fork |
| Dolphin memory access from the host | Companion reads / writes emulated RAM at symbol addresses from `main.elf.MAP` | No game-side transport code | Emulator-only; racy; addresses change every build (regenerate from the map) |
| Broadband adapter + in-game TCP/IP | Real sockets from the game | Direct | Large amount of code; pointless when a host companion exists |

Recommendation: build `ai_link.c` behind a tiny interface (`ai_Link_Send`, `ai_Link_Poll`) and
implement USB Gecko first. Revisit once the Slippi research settles which EXI slots are free in
Slippi Dolphin. The SDK's EXI API is in `libs/dolphin/include/dolphin/exi.h`.

### Companion

- Any language; TypeScript or Python with the Anthropic SDK. Load the `claude-api` skill before
  writing it.
- Holds the conversation, the player's history across sessions, and the tool definitions.
- Batches telemetry: one model call per drill block or on a trigger (e.g. three failures of the
  same kind), not per event.
- Decides when to speak. Default to short, specific, infrequent messages; a coach that talks
  every rep is noise.
- Keeps working when the game disconnects and reconnects (scene changes, resets).

## Milestones

1. Link proof: game sends a counter, companion prints it, companion sends text, game shows it
   with DevText.
2. Telemetry from one ported drill (e.g. L-cancel), a session summary from Claude after the drill.
3. Commands: Claude selects a drill and sets options.
4. Live coaching rules (when to interject), player history, drill plans.
5. Netplay-safe command path for tandem sessions.

## Interaction with Slippi

- The coach link is local-only. In a netplay session it may read state and draw text, but any
  command that changes the simulation must be injected as synced input or be disabled.
- Slippi already streams per-frame game data from the game to Dolphin over EXI (replay
  commands 0x35–0x41). If the build runs under Slippi Dolphin, that stream is a ready telemetry
  source for the companion; only the game-bound direction needs a new channel.

## Open questions

- Which EXI channel / device is free under Slippi Dolphin, and does stock Dolphin's USB Gecko
  emulation behave as described above?
- On-screen text budget: SIS text supports limited glyphs and line length; long coach messages
  need wrapping and paging.
- Should coach output also go to a host-side overlay or voice, so in-game text stays minimal?
- Console play (real hardware) is possible in principle with a USB Gecko; is it a goal?
