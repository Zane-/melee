# Tandem training over Slippi direct connect

Status: research from reading source on 2026-11-11 (`project-slippi/slippi-ssbm-asm`,
`Ishiiruka` branch `slippi`, `project-slippi/dolphin`, `slippi-rust-extensions`,
`slippi-launcher`, `akaneia/m-ex`, `akaneia/akaneia-build`). **Nothing was run.** Items under
"Not verified" are open.

## Verdict

Two humans training together over Slippi direct connect is feasible, with one hard condition:

> **Stock Slippi Dolphin only works with a DOL whose vanilla 1.02 addresses are unchanged.**

A freely shifted DOL (the default way this repo adds code) cannot use stock Slippi. That would
need a Dolphin fork plus a port of Slippi's game-side code.

## Why addresses must not move

Slippi's netplay is not in the game; Dolphin injects it at boot.

- For any disc with ID `GALE01`, Slippi Dolphin writes a bootloader into the game, which pulls
  the full Gecko codeset over EXI and applies it. 310 injections are listed for netplay, 276
  required.
- Those codes use vanilla addresses throughout: 541 distinct absolute `0x80…` literals in the
  Online, Common and Recording folders (injection sites, called functions, static data, r13
  offsets).
- **Rollback savestates are taken by Dolphin, over hardcoded memory ranges**
  (`SlippiSavestate.cpp::initBackupLocs`):
  - `0x80005520–0x80005940`
  - `0x803B7240–0x804DEC00` (vanilla data and BSS)
  - `0x8065C000–0x8071B000`
  - the main heap, bounds read from `0x804D76B8` / `0x804D76BC`
  - minus about 30 excluded ranges (sound, XFB)
- So a shifted DOL breaks the injections, and worse, rollback would silently snapshot the
  wrong memory.

How rollback works, for reference:

| Piece | Where (vanilla address) |
|-|-|
| Send local pad, receive remote / predicted pads | after `PAD_Read` in `HSD_PadRenewRawStatus` (0x80376A28) |
| Re-run the engine loop on rollback | 0x801A5014, 0x801A4DE4, 0x801A4DB4 (inside the frame loop, `gm_801A4D34`) |
| Init online play, RNG sync | 0x8016E748 (inside `fn_8016E730`, match start) |
| Max rollback | 7 frames |
| Desync check | per-frame checksum of each fighter's action state, position, percent, spawn count |

The desync checksum covers fighters only. Diverging mode state is detected only once it changes
a fighter.

## What Slippi allows

| Mode | ISO hash check | Character / stage validation |
|-|-|-|
| Ranked, unranked | Blocks a list of known-desync modded ISOs | Vanilla legal sets only |
| Teams | none seen | Extended characters on m-ex builds only |
| **Direct** | **none** | **none**; pause allowed |

- Game type is detected from the disc: `GALE01` → normal Melee (codes injected); a disc
  containing `MxDt.dat` → m-ex; `GTME01` (UnclePunch / TM-CE) → training mode type, **no online
  codes at all**. This is why TM-CE cannot go online today.
- No prior two-human rollback training mode was found.

## How Akaneia does it

- m-ex builds keep the vanilla DOL layout and inject code, so Slippi's codes still apply.
- Slippi and m-ex cooperate explicitly: reserved heaps (Slippi 5, m-ex 6), overridable
  "compatibility hook" functions at fixed low addresses, and m-ex copying Slippi's scenes into
  its expanded scene table.
- Volleyball is a **stage** (`GrMVb.dat`, extended stage ID). Inference: both players pick it on
  Slippi's own stage select in direct mode, so the choice syncs through Slippi's normal
  selection path (a u16 stage ID, unvalidated in direct). No custom sync channel was found.
- Akaneia's release notes show repeated rollback desync fixes; determinism work is ongoing cost.

## Consequence for this project: two possible architectures

| | A. Address-preserving overlay | B. Freely shifted native build |
|-|-|-|
| Vanilla code | Byte-identical layout; hooks are post-link branch patches or whole-function replacements | Edited in place with guarded calls (what `modding.md` describes) |
| New code | Extra section above the vanilla image; arena raised | Linked anywhere |
| Mutable state | Heap (HSD allocation) or existing vanilla BSS only | Anywhere |
| Slippi | Stock Slippi Dolphin: direct connect, rollback, replays for free | Needs a forked Dolphin and a C port of ~9–15k lines of Slippi ASM (GPL-3.0), tracking an active upstream. Precedent: Lylat |
| Ease of changing vanilla behaviour | Harder: patch or replace functions; must avoid Slippi's injection sites | Easy |
| Who can play | Anyone with Slippi and the ISO | Only users of the custom Dolphin |

**Decision (2026-11-11): A.** The design, its experiments and the tools are in
`overlay-build.md`.

## Rules for netplay-safe training features

- Simulation may depend only on **synced inputs** and **state inside the saved regions**.
  Not on: local menus or OSD settings, unsynced controller ports, the wall clock, the camera,
  the AI coach link.
- Mode configuration syncs by one of: the stage ID (a custom "Edgeguard" stage, like
  volleyball), an in-match menu driven by synced inputs, or character / colour choice.
- Display-only features (OSDs, input display, coach text) are safe if they never write
  simulation state.
- Rollback re-runs up to 7 frames: creating and destroying objects must be safe to repeat.
- Do not add or remove RNG calls on one client only.

### Reset-to-position under rollback

Do not use a TM-style local savestate load or an emulator savestate. Make reset an ordinary
simulation event:

- On frame N, if the synced input of a permitted player has the reset button newly pressed,
  re-initialise fighters (position, percent, action state, velocity, collision), items, stage
  state and mode counters from the synced config.
- Being a pure function of synced inputs and saved state, it re-simulates correctly.
- Reset **everything**; stale or uninitialised fields are the classic desync source.
- "Save the current situation, restore later" works only if the snapshot lives in the heap.
  That grows the heap Dolphin copies every frame, so keep it small.

## First use case: edgeguard training

- A custom stage or stage variant selected on Slippi's stage select in direct mode.
- Roles (recoverer / edgeguarder) from port or character-select choice; swap on a synced input.
- Synced reset: recoverer placed offstage at a configured position and percent, edgeguarder on
  stage; variants as stage variants or a synced in-match menu.
- Slippi's desync recovery restarts with last agreed stocks and percent; check how that
  interacts with a mode that resets percent itself.

## Testing

- Two local Slippi Dolphin instances over direct connect.
- Slippi's "DESYNC DETECTED" checksum, plus our own hash of mode state in debug builds, since
  Slippi's covers fighters only.

## Replays and licences

- Under A, `.slp` recording works unchanged. Replays play back correctly only on the same
  build; third-party stat parsers will see an unknown stage and teleports.
- `slippi-ssbm-asm` is GPL-3.0; Ishiiruka and `slippi-rust-extensions` GPL-2.0. A C port of the
  ASM (architecture B) is a derivative work. Architecture A redistributes none of it.
- MexTK is MIT. m-ex, Akaneia, TM-CE and UnclePunch Training Mode show no licence on GitHub;
  ask the authors before distributing ported code.

## Not verified

- Exactly how Akaneia selects volleyball online (inferred from its stage data).
- Slippi's official policy wording on modded ISOs in direct mode, and how the launcher treats
  unknown ISO hashes.
- Whether an extra DOL section and raised arena disturb Slippi's bootloader heap.
- Slippi playback behaviour with reset events.
- Whether Slippi's servers reject anything about an unknown build in direct mode (no client-side
  check was seen).
- Prior art that exists only on Discord.
