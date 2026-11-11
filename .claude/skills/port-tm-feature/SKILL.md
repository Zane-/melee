---
name: port-tm-feature
description: Port one Training Mode (TM-CE, ../TrainingMode) feature to native C in the Melee decomp - a C event, an OSD, a Gecko ASM injection, or a legacy ASM event. Use when asked to port, translate or reimplement anything from TrainingMode or UnclePunch Training Mode.
---

# Port a Training Mode feature

Background: `docs/ai/training-mode-port.md`. TM-CE's own docs: `../TrainingMode/CLAUDE.md`,
`DEVELOPMENT.md`, `docs/ADDING_SCENARIOS.md`. Treat TM-CE as the behavioural spec, not as code
to paste: its types, field names and memory model differ.

The build is an address-preserving overlay (`docs/ai/overlay-build.md`): hooks are hook-table
entries applied as patches, never edits to vanilla source, and mutable state lives on the heap.

## 1. Scope the feature

List every piece the feature uses:

- C: `grep -n` the feature's functions in `../TrainingMode/src`.
- ASM: `grep -rln "<FeatureName>\|TM_<Func>" ../TrainingMode/ASM`. Each `.asm` starts with
  `# To be inserted at 8XXXXXXX`.
- Assets: symbols fetched with `Archive_GetPublicAddress` and the `.dat` they come from.
- Services: savestates, menu, messages, `event_vars` fields, `FighterData.TM.*` fields.

If a service is not ported yet, port it first or stub it behind the same interface. Do not
inline a private copy.

## 2. Resolve the vanilla surface

```sh
python tools/mex_symbols.py --used ../TrainingMode/src/<file-dir> --headers   # or name by name
python tools/mex_symbols.py 0x<each injection address>
```

- For structs, match by **offset**: MexTK's `FighterData` offsets against the offset comments in
  `src/melee/ft/types.h`. Names rarely agree.
- If the decomp field is unnamed (`x2218_b3`), use it as is in mod code and add a comment with
  the MexTK name. Do not rename vanilla fields in a port change.
- Raw addresses in TM-CE source (`0x80…` literals, `R13_OFFSET`) each need a symbol
  (`find-symbol` skill). Runtime instruction patches (`*(u32*)addr = opcode`) become build-time
  hook-table entries.

## 3. Translate

| Kind | How |
|-|-|
| C event (`Event_Init` / `Event_Update` / `Event_Think` / `Event_Menu`) | One file `src/melee/tm/events/<name>.c` exporting a `const TmEventDesc`, registered in its page of `tm_event_pages` (`tm_event.c`). Model: `events/laserland.c`. Menus become `const TmOptionDesc` / `TmMenuDesc` tables (positional initialisers; C89); statics move into the event data block |
| Observing ASM injection (OSD trigger, counter) | A `call` hook on a nearby `bl` if the needed values are arguments or reachable from them (fighter GObj, globals). `inject` only as a last resort: the project goal is no assembly. Logic in a `tm/` file |
| Behaviour-changing ASM | `function` hook with an edited copy of the decomp's C, unless Slippi patches that function; then `call` |
| A cluster of injections into one screen or subsystem | Replace the subsystem's entry with one `function` hook and carry edited copies of its functions (model: `tm_ess.c`) |
| ASM that duplicates a Slippi code (unlocks, UCF, tournament defaults, neutral spawns) | Drop it. Check with `tools/tm_slippi_collisions.py` |
| ASM that only exists to reach C (function table, loader, relocation, struct size) | Delete; not needed natively |
| Legacy ASM event | Rewrite against the C event API using the ASM as the spec; port a C event of similar shape first |

Reading the injection: registers at the hook are whatever the vanilla function had live there.
Work out which C variables they are from the split asm
(`build/GALE01/asm/.../<file>.s`, `.fn <function>`) next to the decomp source.

Common substitutions are in the "Translating MexTK code" table of the port doc.

Before choosing a hook, run `python tools/tm_slippi_collisions.py --function <vanilla fn>`.

## 4. Preserve behaviour that is easy to lose

- **Frame timing.** OSDs report frame counts; a hook placed one statement early or late shifts
  results by a frame. Keep the hook at the exact mapped statement and the same proc priority
  (`callbackPriority` in the event descriptor).
- **RNG.** Do not add or remove `HSD_Randi` / `HSD_Randf` calls on gameplay paths. TM-CE keeps
  its own `event_vars->rng` for forced character RNG; keep that separate.
- **Savestate coverage.** Per-event state TM-CE keeps in the 512-byte event userdata is saved
  and restored; statics are not. Keep the same split, and keep new gameplay-affecting state in
  the saved block (this is also what rollback netplay will need).
- **Menu order and saved indices.** Appending is safe; inserting shifts saved settings and
  high-score slots.

## 5. Verify

1. Matching build SHA.
2. Overlay build links and `tools/overlay_check.py` passes.
3. In Dolphin, run the feature next to the TM-CE ISO and compare: same menu, same OSD numbers
   for the same inputs. For timing features, use frame advance in both.

Report which checks ran, what differs from TM-CE on purpose, and what is stubbed.
