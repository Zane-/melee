# Character courses: the training build's architecture

Decided 2026-11-12 by the owner: training is reorganised around **the character you play**.
You pick your character first, then a hub offers that character's course in four parts,
**Tech, Neutral, Punish, Defense**, plus free practice (the Lab and TM-CE's generic events).
Each drill teaches in the game itself: a guide you can summon, a demonstration, timing
feedback on every attempt, and statistics. The aim is one coherent path to getting good at a
character instead of a flat list of unrelated events.

This replaces TM-CE's organisation (event select screen → pages of events → character
select). It does not replace TM-CE's machinery: the Lab, the generic events, savestates, the
menu engine, messages, HUD drawing and the OSDs stay and are what courses are built from
(`tmce-native.md`).

**Status (2026-11-12): M1 and M2 are in; M3 (the Fox course) has started.** The engine
runs six drills with a guide overlay, a demonstration and generated frame data; the hub
opens after character select. Built: `fox-shine-oos` (Punish) and all sixteen of Fox's Tech drills. Neutral, Punish
(beyond Shine OoS) and Defense are still plans. The owner played an earlier build on
2026-11-12; the changes asked for then are in (below). The last three Tech drills (shield
drop, ledgedash, ledge stall) have not been played by a person. "Built" and "Planned" are marked per section;
update this file as milestones land.

| Piece | State | Checked how |
|-|-|-|
| Engine (`src/tmce/events/course/event.c`) | Built | 9 specs in `tests/tmtest/course/fox-shine-oos/` pass in the simulator; one confirmed in Dolphin with identical numbers |
| Drill `fox-shine-oos` | Built | same |
| Hub (`src/tmce/events/course/hub_css.c`) | Built | `tests/sim/hub_roundtrip.py` (16 checks, simulator); rendering looked at once in Dolphin (frame dump) |
| Reference scripts and demonstrations (engine plays the drill on the player's fighter) | Built | `demo_*.json`: all 9 scenarios graded a frame-4 success in the simulator; 2 confirmed in Dolphin |
| Guide overlay (D-pad up) | Built | `guide_then_demo.json` in simulator and Dolphin; rendering looked at in Dolphin (frame dump) |
| Generated frame data table (`gen/framedata.inc.h`) | Built | `tools/melee_data/gen_course_tables.py --check` |
| Boot into the course's character select | Built (`TM_AC_BOOT_EVENT_FILE "course"`) | simulator |
| Played by a person on a controller | **Not yet** | the owner has not tried it; the hub's input feel and text layout are unreviewed |

## What exists today (the base)

| Piece | Where | State |
|-|-|-|
| TM-CE core, Lab, 13 C events, 15 legacy events, OSDs | `tmce-native.md` | Ported; boot → event select → Lab booted, most of the rest not booted |
| Event mode state list (CSS → match → SSS) as overlay data | `src/melee/tm/css/tm_css.c` | Ported |
| Boot straight into an event's CSS | `src/melee/tm/addcodes/ac_boot.c` (`TM_AC_BOOT_EVENT`) | Ported |
| A drill written for this build: Shine OoS (phases, scripted CPU inputs, per-scenario stats, options menu, test bot) | `src/tmce/events/shineoos/` | Uncommitted work in progress |
| CPU character rotation (one event, many opponents, preloaded) | `src/melee/tm/rotation/` | Uncommitted work in progress |
| Automated Dolphin runs (pipe input, memory reads over GDB) | `tools/dolphin_harness.py`, `tools/test_shineoos.py` | Uncommitted work in progress |
| Game knowledge and calculators | `data/`, `tools/melee_data/query.py` | Done |

Shine OoS is the prototype of a course drill. The engine below is that event's structure
made common.

## User flow

```
boot ─► character select ─► HUB (for that character) ─► drill ─► back to the hub
                              │
                              ├─ Tech      individual techniques, executed alone
                              ├─ Neutral   openings: scenarios that end in a first hit
                              ├─ Punish    conversions: what to do once you have the hit
                              ├─ Defense   getting out: SDI, ASDI, teching, recovering
                              └─ Free      Lab, TM-CE's generic events
```

- The character select screen comes first and is where you change character. Only the
  player's character is picked there; a drill brings its own opponents.
- The hub lists only what applies to the picked character: that character's course plus
  the universal drills every character has (wavedash, L-cancel, teching...).
- Each hub row shows the drill's name, a one-line goal and its statistics (attempts,
  success rate, best streak). A course reads top to bottom as a curriculum.
- Leaving a drill returns to the hub at the same row. B from the hub returns to character
  select.
- Booting goes straight to character select (as boot-to-Lab does now). The vanilla menus
  stay reachable (hold Y at boot).

### The four parts

| Part | Question it answers | A repetition | Graded on |
|-|-|-|-|
| **Tech** | Can my hands do it? | One technique, no opponent pressure (a passive dummy when the tech needs a target) | Frame accuracy of the inputs |
| **Neutral** | Can I get the first hit? | A realistic neutral situation with a CPU that commits to something; ends when the player lands the opening hit or grab, or is hit | Whether the opening was won, and how early |
| **Punish** | Can I convert it? | Starts at the hit, grab or shielded move; the CPU tries to escape (DI, SDI, tech, mash) within a tolerance the drill sets | Whether the conversion was true (no escape window), damage or kill |
| **Defense** | Can I get out? | The CPU performs the combo, pressure or edgeguard on the player | Whether the escape happened in the frames that allow it |

The parts chain: a Neutral drill ends in the situation a Punish drill starts from, and
Defense drills are Punish drills seen from the other side. A course links them explicitly
(`leads_to`), so the hub can offer "continue into the punish".

Frame tolerance is the main difficulty knob everywhere: how late the player may be (Tech),
how quickly the CPU reacts (Neutral), how many frames of slack the CPU's escape leaves
(Punish), how tight the escape window is (Defense).

## Architecture

```
data/characters, data/techniques        knowledge (exists)
        │  plan-character-course skill
        ▼
data/courses/<id>.md                    the curriculum: ordered drills per part, each a spec
        │  add-course-drill skill
        ▼
src/tmce/course/                        ENGINE: one event unit that runs any drill
src/tmce/course/drills/<area>/*.c       DRILLS: a description + a few callbacks each
src/tmce/course/gen/                    generated tables (frame data, course lists)
src/melee/tm/hub/                       HUB: menu after character select
```

### Engine (built: `src/tmce/events/course/`; the table lists what is there and what is not)

Built so far: attempt loop, re-placing reset, CPU scripts, opponent rotation, success/fail
with a verdict message and a measured-vs-target frame count, per-scenario and per-drill
statistics (attempts, successes, streaks, frame error), common options plus the drill's
own, D-pad controls, JSON test report; and from M2: reference scripts with marks,
demonstrations, the guide overlay with an input timeline, the generated frame data table.
Not built: savestate resets, weighted CPU choices beyond what a drill codes itself, the
detector library, a per-attempt timeline of what the player actually pressed, slow-motion
demonstrations, guide text generated from `data/courses/` (a drill fills it in C for now).

As built in M2:

- **Reference script** (`CourseRefInput[]`): the player inputs that solve the drill, each
  placed against a *mark* the drill announces with `course_Mark` (mark 0 = start of the
  attempt). A **demonstration** (option "Demonstration", or D-pad right in the guide) runs
  the attempt twice from the same random seed: an observing pass with only the mark-0
  inputs, which records the frame of every mark, then the full script. The inputs go to the
  player's engine pad, as the Lab's playback does. Demonstrations are not counted.
- **Guide** (D-pad up): the drill's `Guide` callback fills up to eight lines; the engine
  draws the panel, the timeline of the reference's inputs after its mark, and the controls.
  While it is open the drill waits; closing starts a fresh attempt.
- **Numbers**: `course_Fighter(fd)->jump_squat`, `->move[CMOVE_USMASH].hit` ... from
  `gen/framedata.inc.h`, generated from `data/framedata/`. Regenerate with
  `python tools/melee_data/gen_course_tables.py` after `extract.py`.

Added with the first Tech drills (M3):

- **Solo drills**: `cpu_kind = -1` in the drill's info, `course_PlaceSolo` in `Setup`.
- **End-of-frame sampling**: `c->state`, `c->prev_state`, `c->state_frames`, `c->held`,
  `c->down` are the player at the end of the previous frame, taken by a proc that runs
  after the fighters'. The drill's `Think` runs part-way through the fighter's frame, so
  `hd->state_id` read there shows input- and landing-driven state changes a frame later
  than animation-driven ones; frame counts mixing the two come out one off. Count frames
  with the sampled fields.
- **Leniency option**: `COURSE_OPT_LENIENCY` in the drill's options and
  `course_Leniency(index)`; default 2 frames late still succeeds.
- **Script frames in jump squats**: a `CourseRefInput`'s last field adds that many of the
  player's jump squats to its frame, so one script fits every character. A script with no
  marks is demonstrated in one pass.
- **Options per drill**: a drill's own options reset to their defaults when another drill
  is opened; the common ones carry over.
- **HUD text limit**: TM-CE's HUD has 32 texts per frame and the game stops when a 33rd is
  drawn. The guide stays under it (it numbers only some timeline frames) and `GuideText`
  refuses past the limit.

- **Marked scripts and the landing**: a reference input may sit a negative number of
  frames before a mark (the L-cancel demonstration presses 4 frames before the landing its
  first pass found). Anything that changes when the mark happens (a fast fall) has to be
  in both passes, so it goes against mark 0.
- **One script for every character has limits.** The six `universal-` demonstrations were
  run for all 26 characters in the simulator: four pass for all, L-cancel fails for Kirby
  and Sheik, SHFFL for those and Mr. Game & Watch. Run that matrix for any new `universal-`
  drill (a spec per character with option 4 = 2).
- **The hub scrolls**: a section may hold up to 32 drills, 8 on screen.

Changed after the owner's first play session (2026-11-12):

- **Flow** (`.flow = 1` on the drill): a verdict is counted and shown and the drill starts
  again from phase 0 where the player stands; no re-placing. All solo Tech drills and
  aerial-into-shine use it. Consequences for a drill: something that is not an attempt (a
  plain jump in the wavedash drill) gives no verdict, it just returns to phase 0; and a
  condition tested in phase 0 must be true for one frame only (`c->state_frames == 1`), or
  it fires every frame.
- **Stats card**: success rate, streak and best streak, top left, while playing. Menu
  option "Stats Card", on by default.
- **Help** in the menu (not "HELP"): A closes the menu and opens the guide.
- **Built reference scripts** (`BuildReference`): the L-cancel and SHFFL demonstrations
  are built per attempt from the character's hop, gravity and fast-fall speed, so there is
  no scouting hop, and each demonstration shows the next aerial (`course_DemoCount`). In
  the simulator 171 of 175 such demonstrations over all 26 characters succeed; the four
  that do not are single aerials of Kirby, Luigi and Zelda.
- **Shielding target**: `course_CpuShield(c)` every frame; `c->cpu_state` is sampled like
  the player's.
- **Resets release grabs** (`ReleaseGrab`): a reset during a grab used to leave the two
  fighters linked (victim in the floor, next grab not taking).
- **Text**: the game's font has no semicolon; it is dropped silently. Apostrophes,
  colons, parentheses, `+ - / = %` are fine.

- **Starts other than the floor**: `course_PlaceOnLedge(c)` (the stage's left ledge, fresh
  intangibility; TM-CE's ledge search and placement, copied into `ledge.inc.h`) and
  `course_PlaceOnPlatform(c, x, above_y)` (whatever is straight below that point). A
  drill's stage is `.stage` in its info (shield drop uses Battlefield). `course_Fell(c)`
  says the player died or dropped far below the stage. These drills reset after every
  verdict, since the start position is the drill.
- **A guide can hide the timeline** (`g->hide_timeline`) when the reference is a stick
  motion rather than button presses.

Things learned the hard way: the simulator never runs drawing code (GX callbacks), so
anything drawn has to be looked at in Dolphin once (the guide crashed there on a NULL
`event_vars->HUD_DrawTextEx`, which TM-CE's table leaves unset; call `HUD_DrawTextEx`
directly); and both passes of a demonstration must start from a released pad, or the first
button is not a fresh press in one of them.

How it is laid out (differs from the first sketch below in names only):

- `course.h`: `CourseDrillInfo` (what is known before the match: id, name, goal, part,
  characters, stage, deck) and `enum CourseDrillId`.
- `desc.c` (linked globally): `Course_Drills[]`, `Course_Desc`, `Course_Select(drill)`,
  session statistics and hub state.
- `event.c`: the engine, with `CourseCtx` and `CourseDrill` (Setup/Think callbacks, options,
  help). An event unit's symbols are local, so drills are included into it:
  `drills/<name>.inc.h` (named `.h` so the build notices edits).
- Tests: `tests/tmtest/course/<drill-id>/*.json`.

Tests pick the drill with a spec's `"drill": "<id>"` (option index 0xFF, applied before the
match loads, because `Course_Select` has to run before the rotation preload reads
`Course_Desc.rotation`). Only exercised with drill 0 so far.

One TM-CE event unit, `course`, runs every drill. A drill is data plus callbacks; it owns no
match setup, menu, statistics or reset code of its own. The engine provides:

| Service | What it does | Built from |
|-|-|-|
| Attempt loop | `SETUP → READY → ACTIVE → RESULT → reset`, with a timeout | Shine OoS's phase machine |
| Reset | Savestate after setup, reload per attempt; or re-place fighters for simple drills | `event_vars->Savestate_*`, Shine OoS `ResetFighter` |
| CPU scripts | Frame-indexed input lists played into the CPU's pad, mirrored by side | Shine OoS `OosInput` / `ApplyInputs` |
| CPU choices | Weighted random picks per attempt (DI, tech, delay, which attack), seeded per attempt | new |
| Opponent rotation | A deck of scenarios with different CPU characters | `tm_rotation.h` |
| Detectors | Reusable observers: entered action state X, on frame N after event Y, hit landed, hit taken, shield hit, L-cancel result, tech result, grounded/airborne, ledge grabbed, stock lost | TM-CE `FighterData.TM` bookkeeping, OSD code |
| Grading | Success or fail plus a **timing verdict**: the frame the input came, the window, early/late by how many frames | new |
| Feedback | Result message, colour, and a per-attempt input timeline bar | `Message_Display`, `HUD_DrawActionLogBar` |
| Statistics | Per drill and per scenario: attempts, successes, current and best streak, mean frame error, last 20 results | new; Shine OoS has attempts/successes |
| Guide overlay | Summoned at will (D-pad up); pauses the drill; pages of text, an input timeline, the numbers that matter; "watch a demonstration" | `HUD_DrawRects/Text`, new |
| Demonstration | The reference input script performed in the match, optionally in slow motion with the inputs shown | CPU scripts; see below |
| Options menu | Common options (tolerance, side, percent, reset delay, CPU choice weights) plus the drill's own | TM-CE `EventMenu` |
| Controls | D-pad left/right scenario, down reset, up guide (as Shine OoS) | |

A drill definition (shape, not final names):

```c
typedef struct CourseDrill {
    const char* id;            /* "fox-waveshine-usmash", same as data/courses */
    u8 part;                   /* COURSE_TECH / NEUTRAL / PUNISH / DEFENSE */
    u32 characters;            /* CSSID_* mask of player characters; 0 = universal */
    const char* name;
    const char* goal;          /* one line, shown in the hub */
    const CourseGuide* guide;  /* pages, timeline, key numbers */
    const TmRotDeck* deck;     /* scenarios: CPU character + per-scenario data */
    const CourseScript* reference; /* inputs that solve it: demo, timeline, test */
    void (*Setup)(CourseCtx*);     /* place fighters, percents, states */
    void (*Think)(CourseCtx*);     /* run detectors, drive the CPU, call course_Result */
    const EventOption* options;    /* drill-specific options */
    s16 stage;
    const char* leads_to;      /* id of the drill this situation continues into */
} CourseDrill;
```

**One reference input script per drill, three uses.** Every drill carries the inputs that
solve it. The same script (1) is played as the in-game demonstration, (2) draws the input
timeline in the guide, and (3) is run by the automated test, which must see the drill grade
it as a success. A drill whose reference fails its own grading does not ship.

**No hand-typed game numbers.** Frame data and attributes used by drills come from
`data/framedata/*.json` through a generated header (`tools/melee_data/gen_course_tables.py`,
planned), so a drill says `FD(fox, usmash).hit` and not `7`. Numbers that have to be tuned in
Dolphin (distances, script timings) are named constants with a comment saying how they were
tuned.

**Where state lives.** Courses are offline, so overlay statics are allowed, like the rest of
TM-CE. Statistics that should survive a power cycle need memory card space, which is not
designed yet (see open decisions).

### Guide overlay and demonstrations

The guide is how a player learns a drill without leaving the game:

1. **What and why**: two or three sentences from the knowledge base.
2. **Inputs**: the reference script drawn as a timeline (one row per button or stick
   direction, frames left to right, windows shaded).
3. **Numbers**: the frames that define success ("shine on the first airborne frame: frame 4
   after shield stun"), generated from the frame data.
4. **Common errors**: what each failure verdict means and how to fix it.
5. **Watch**: plays the reference script in the match, at full speed or slowed, with the
   input display on, then hands control back.

Text is authored in the course file (`data/courses/<id>.md`) and compiled into the drill's
`CourseGuide`; it is not written twice.

How the demonstration is performed is the least proven part. Planned order of preference:
(a) the engine drives the player's own fighter from the script for the length of the demo
(TM-CE's Lab does this for input playback; how much of that can be reused outside the Lab is
unverified); (b) fall back to a second copy of the player's character as a CPU, driven by
the proven CPU script path. Milestone M2 settles this.

### Hub (built: `src/tmce/events/course/hub_css.c`)

As built: a css unit (`hubCSS`, art borrowed from `labCSS.dat`) loaded for the course event.
Its proc runs after the scene's and turns the scene's "start the match" state into the open
hub; sections with left/right (or L/R), drills with up/down, A starts, B goes back to
picking a character. It remembers the character, because this character select does not
restore the pick when the scene comes back, and starts the match itself with that character
(scene data and preload request). Every way out of a drill (its Exit, L+R+A+START, the
match ending) returns to the character select and the hub reopens on the same row; the
event mode's state callbacks ask `tmce_CourseRoute` (desc.c) where TM-CE would go to the
main menu. Free Practice has two rows: the Lab, which opens the Lab's own character select
(CPU pick, stage select, recordings; B there or the Lab match ending comes back to the hub),
and "Training Mode events" (the main menu's event list). Sections without drills say so.

Not done: drill rows show session statistics only; nothing is saved.

The original plan, for reference:

The event mode's state list is already ours (`tm_css_EventStates`), so the flow change is
local to it. Plan: the hub is a menu drawn in the character select scene once the character
is confirmed (TM-CE's `lab_css.c` already builds menus in that scene), rather than a new
scene. Choosing a drill sets the event (the `course` unit) and the drill id, preloads what
the drill needs and moves to the match state; choosing the Lab or a generic event sets that
event and continues as TM-CE does today (stage select when the event has no fixed stage).
Returning from a match re-enters character select with the hub open on the same row.

Unverified: opening an overlay menu from the vanilla CSS confirm, skipping the CPU puck for
course drills, and reopening the hub on return. The alternative, a dedicated game-mode state
with its own scene, costs more code but has no CSS interactions. M1 decides.

TM-CE's event select screen stops being the entry point. Its code stays until the hub's
"Free" section can launch every event it could.

### Course content (`data/courses/`)

A course is a markdown file per character: front matter, then the four parts as ordered
lists of drill specs. Universal drills live in `data/courses/universal.md` and are included
by reference with per-character parameters (Fox's wavedash numbers differ from Luigi's but
the drill is the same). Format and rules: `data/courses/README.md`. The build generates the
hub's lists and the guide text from these files, so the curriculum the player sees and the
document an agent edits are the same thing.

## Milestones

Each ends with something booted in Dolphin and an automated run.

| | Deliverable | Proves |
|-|-|-|
| **M0** | Shine OoS and rotation committed as they are; harness documented | The base the engine is extracted from |
| **M1** (done 2026-11-12, not yet played by the owner) | Engine skeleton with attempt loop, reset, CPU scripts, grading, statistics, messages; Shine OoS re-expressed as a drill on it; hub with the four parts and Free, entered after character select | The flow and the drill shape |
| **M2** (done 2026-11-12, not yet played by the owner) | Guide overlay with timeline and numbers; demonstration playback; reference-script test runner for all drills | Teaching in game; the three-uses rule |
| **M3** | Fox course: Tech complete, then Punish, Defense, Neutral (curriculum in `data/courses/fox.md`) | The recipe, end to end |
| **M4** | Universal drills parameterised for every character; second character course (Falco or Marth) written only with the skills | That the recipe transfers |
| later | Persistent statistics; course progress view; coach integration (`ai-coach.md` can read the same statistics) | |

Order inside M3: Tech first (no CPU behaviour to tune), then Punish (builds on Shine OoS),
then Defense (needs CPU combo scripts), then Neutral (needs the most CPU behaviour).

## Rules

- A drill is added through `data/courses/` first, then code. No drill exists only in C.
- Every drill has: a goal, a guide, a reference script, a timing verdict on failure, and
  statistics. A drill that can only say "fail" is not finished.
- Every drill is proven winnable by its reference script in an automated run, and proven to
  fail on a deliberately wrong script (one frame outside the window).
- CPU behaviour is what that character really does (sourced in `data/characters/`), with the
  realistic options randomised. A CPU that always does the same thing is a Tech drill, not a
  Neutral, Punish or Defense drill.
- Numbers come from generated tables or are named, commented tuning constants.
- The overlay rules of `CLAUDE.md` apply unchanged: no edits to vanilla functions, hooks
  through the hook tables, C only, `overlay_check.py` passes.
- Courses are offline. Nothing here runs under rollback; tandem drills (`slippi-tandem.md`)
  are a separate design.

## Open decisions (owner)

1. **Persistent statistics.** Session-only until designed. Options: unused save data fields
   as TM-CE does for settings (small), or a separate memory card file (room for history).
2. **What "complete" means for a drill** (unlocking, medals, a target success rate), or
   whether the hub only shows numbers.
3. **Hub look.** Plan is TM-CE's menu style with no new art. Custom art is a later choice.
4. **Fate of TM-CE's character-specific events** (ledgedash, eggs, the legacy Multishine...).
   Plan: each is either re-expressed as a course drill or stays under Free; none is deleted
   until its replacement exists.

## Skills

| Skill | Use |
|-|-|
| `plan-character-course` | Write or extend `data/courses/<id>.md` from the knowledge base |
| `design-training-scenario` | One drill spec from a prompt, in the course format |
| `add-course-drill` | Implement one specified drill on the engine, guide and test included |
| `melee-knowledge` | Every lookup those three need |
