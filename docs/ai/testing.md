# Testing training events (agent-first)

`tools/tmtest.py` runs a deterministic, scripted test of an event in Dolphin and returns JSON.
No menus, no wall-clock timing, no window interaction: a run takes 2-6 seconds.

```sh
python tools/tmtest.py tests/tmtest/shineoos/*.json          # build the test DOL, run all
python tools/tmtest.py --no-build --json SPEC.json             # machine-readable
```

## How it works

| Piece | Where |
|-|-|
| Test build (`TM_TEST=1`): the runner compiled in, plus `config/GALE01/tm_hooks/test.txt` | `tools/overlay_build.py` (`build/overlay-tmtest/`); a normal build has none of it |
| Config the run reads: event, characters, stage, seed, option overrides, input script, frame budget | `tm_test_config` (`src/melee/tm/test/tmtest.h`), patched into the DOL by `tools/tmtest.py` |
| Boot straight into the event's match: no CSS or SSS; the characters go into the preload cache the CSS would fill; the event's own CPU and stage are used unless the spec names others (FD if the event lets you pick) | `tm_test_OnEventModeLoad`, `tm_test_OnMatchEnter` (`src/melee/tm/test/tmtest.c`) |
| Input: port 1's raw pad reading is replaced each logic frame before the game pops it (`gm_801A4D34+0xB4`), so menus, fighters and TM-CE all see real controller input | `tm_test_PadRenew` |
| Output: `OSReport` lines `TMTEST {json}`: `boot`, `match`, trace frames (`f`, per fighter `ck st x y pct`), the event's own `result` lines, `done` | Dolphin's log (`build/tmtest/user/Logs/dolphin.log`) |
| Dolphin: isolated user dir (`build/tmtest/user`, memory card copied from the owner's), Null video, no audio, unlimited speed, panic dialogs off, inside `xvfb-run` (no window; a visible window steals the owner's desktop focus, so without xvfb-run the runner refuses unless `--window`) | `tools/tmtest.py run()` |

The same test build runs in `tools/melee_sim` (another session's Unicorn-based simulator, which
hooks `OSReport`); keep tests independent of Dolphin specifics.

## Writing a spec

```json
{
  "event": "shineoos", "hmn": "fox", "cpu": "marth", "seed": 1, "max_frames": 240,
  "trace": 0,
  "options": [[0, 1], [3, 1], [4, 1]],
  "inputs": [
    {"at": 0, "hold": 240, "buttons": ["R"], "r": 255},
    {"on_exit": {"port": 0, "state": "GuardSetOff"}, "delay": 0, "buttons": ["X"], "exact": true},
    {"on_exit": {"port": 0, "state": "GuardSetOff"}, "delay": 3, "buttons": ["B"],
     "stick": [0, -127], "exact": true}
  ],
  "expect": {"event_result": "success", "oos_frame": 4}
}
```

- `drill` (with `"event": "course"`): the course drill to run, by its id in
  `data/courses/` (`"fox-shine-oos"`). Applied before the match loads.
- `options`: `[index, value]` into the event's main menu (`Event_Menu`), applied before the
  match. Use them to pin the scenario, side and delays so a run is reproducible.
- `inputs` (port 1): `at` = match frame; `on_enter` / `on_exit` = a fighter (`port` = slot, 0 is
  the player) entering or leaving an action state, plus `delay`. State triggers fire on the frame
  **after** the change is visible (a one-frame reaction). `"exact": true` places the input on the
  frame of the change itself: the runner does a traced dry run first (runs are deterministic) and
  rewrites it to `at`. Only the first occurrence is used.
- `"occurrence": N` in an exact trigger picks the Nth time the state is entered or left (a
  jump out of shield and a later jump out of the shine are both KneeBend).
- Which frame "exact" means: the frame during which the change happened. An input on that frame
  works when the change comes from the animation (shieldstun ending: jump out of shield on it),
  but not when it comes from physics later in the frame (landing): use `delay: 1` there. Likewise
  an input on the frame a jump squat starts plus 3 is still in jump squat; the first frame Fox
  can act in the air is +4. Check with `--states` rather than guessing.
- A button held by an earlier input (R for the shield) cannot be pressed again: airdodge with L.
- Names for `hmn`/`cpu`/`stage`/`state` are the tables at the top of `tools/tmtest.py`; numbers
  work too. State names follow `ftCo_MS_*` in `src/melee/ft/kinds/ftCommon/forward.h`.
- `trace: N` logs both fighters every N frames: the way to see what actually happened.
- `expect` checks fields of the **first** `result` record the event logs.

## Events report results

An event under test logs one line per attempt, in test builds only:

```c
#ifdef TM_TEST
OSReport("TMTEST {\"result\":\"%s\", ...}\n", ...);
#endif
```

Keep every value JSON-safe (no newlines; see `Reason()` in `src/tmce/events/shineoos/event.c`).
Report measured numbers (frames, distances), not only pass/fail, so a failing test explains itself.

## Workflow for tuning a drill

1. Run the spec with `--states` (traces every frame, prints each fighter's state changes with
   positions) and read what actually happened.
2. Change the scenario data, rerun (`--no-build` only when the C did not change).
3. Keep one spec per scenario under `tests/tmtest/<event>/` with `expect`, plus a soak spec
   (long random run) for crashes. Run the folder before committing.

## Process hygiene (read before changing how Dolphin is launched)

Dolphin runs at unlimited speed and never exits by itself, and under `xvfb-run` it is a
grandchild of the runner. On 2026-11-11 the runner terminated only `xvfb-run`: every run left
a Dolphin spinning, 94 accumulated in 22 minutes, load average passed 100 and the owner's
desktop session went down. Rules since then, enforced in `tools/tmtest.py`:

- Each run is its own process group (`start_new_session=True`) and is stopped with
  `os.killpg`, then checked: no `dolphin-emu` using `build/tmtest/user` may survive.
- A run refuses to start if such a process already exists.
- Never start runs in parallel or in a loop without checking `pgrep -c dolphin-emu` is 0
  between them. Prefer the simulator (`tools/melee_sim`), which is one Python process that
  exits when done.

## Findings so far

- Fighter files must be loaded before the match creates fighters: the CSS commits its picks every
  frame; a test build commits in the match state's `on_enter` and waits (`lbDvd_80017700`).
  Committing in the mode's `on_load` does not work: `preloadState` (`lbDvdPreload_3`) releases
  the heaps after it.
- At most 4 different fighters can be preloaded; a 5th overflows the preload heap
  (`memp_kouho`, `lbmemory.c`). Character rotation counts what is already cached and fills
  up to 4 (`TM_ROT_MAX_FIGHTERS`).
- Fox's shine out of shield: jump on the frame shieldstun ends, down-B on the first airborne frame
  (3 later); the shine is out on frame 4. Down-B during jump squat does nothing.

## Menus: boot scripts and pictures

A spec with `"boot": true` and no event does not start a match. Its inputs count frames
from boot and drive whatever screen is up, and each frame listed under `"shots"` is kept
as a picture when `--shots DIR` is given:

```sh
python tools/tmtest.py tests/tmtest/menu/boot.json --shots /tmp/shots   # about 30 s
```

```json
{ "boot": true, "max_frames": 700, "shots": [330, 440, 640],
  "inputs": [ {"at": 385, "buttons": ["A"], "hold": 2} ] }
```

With `--shots` Dolphin runs with a renderer (OpenGL under the virtual X server;
`TMTEST_VIDEO` chooses another) at real-time speed and dumps every frame; the runner copies
the newest file about 0.4 s after the game logs the shot, so a picture shows the screen
some 20 frames after its number. Leave the screen still for half a second around a shot.
Without `--shots` the same spec runs with no renderer in a few seconds, which is enough to
see whether a path through the menus crashes.

The copy of the disc these runs use (`build/tmtest/disc`) is made once; files added to
`build/disc` later are linked in at each run. Before that was so, a new event's art file
was missing there and its screen crashed in Dolphin only.
