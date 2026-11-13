# Agent docs index

These docs are written for AI agents (and humans) working on the training build.
Start with the root `CLAUDE.md`, then read only what the task needs.

| Doc | Read it when |
|-|-|
| [codebase-map.md](codebase-map.md) | You need to know which module or file owns something, or how names work |
| [runtime.md](runtime.md) | You need the boot → mode → scene → frame flow, GObjs, fighters, text, memory, files |
| [overlay-build.md](overlay-build.md) | You are adding code that must ship: sections, hooks, state, the layout invariant |
| [modding.md](modding.md) | You want a quick shifted dev build for an experiment |
| [training-courses.md](training-courses.md) | You are working on character courses: the hub, the drill engine, any Tech / Neutral / Punish / Defense drill |
| [simulator.md](simulator.md) | You want to run or test game behaviour without Dolphin: the headless simulator, its limits, fixing it when it stops |
| [melee-actor.md](melee-actor.md) | You want a CPU or a test that follows intentions ("approach, up tilt") instead of fixed frames: the Melee Actor, its script format, where it runs, and the slippi-ai research |
| [native-port.md](native-port.md) | You are building or running the game natively for Linux (no emulator), comparing it with the console's code, or fixing a difference between the two |
| [training-mode-port.md](training-mode-port.md) | You are porting anything from `../TrainingMode` |
| [ai-coach.md](ai-coach.md) | You are working on the Claude coach link |
| [slippi-tandem.md](slippi-tandem.md) | You are working on netplay / Slippi direct-connect training |
| [../../data/README.md](../../data/README.md) | You need game knowledge: frame data, character tech, percents, recovery, techniques (the knowledge base under `data/`) |

Skills (task recipes) are in `.claude/skills/`:

| Skill | Use |
|-|-|
| `build-melee` | Configure, build, verify the SHA, run in Dolphin |
| `find-symbol` | Go from an address, a MexTK name or a behaviour to the decomp function |
| `add-native-code` | Add a new translation unit and hook it into vanilla code |
| `port-tm-feature` | Port one Training Mode event, OSD or ASM injection to native C |
| `melee-knowledge` | Look up frame data, attributes, character and technique docs; knockback and on-shield calculators |
| `design-training-scenario` | Turn a prompt into a data-backed scenario spec (player, CPU, inputs, success conditions) |
| `plan-character-course` | Draft or extend a character's curriculum in `data/courses/` |
| `add-course-drill` | Implement one specified drill: code, guide, reference script, automated Dolphin proof |
| `melee-sim` | Run specs and explore interactions in the simulator instead of booting Dolphin |

## Keeping these docs true

- Every claim here was checked against the source at the time of writing, but function names
  change often upstream (renames are the main upstream activity). If a name in a doc no longer
  greps, look it up by address in `config/GALE01/symbols.txt` and fix the doc.
- Mark anything you did not verify as unverified. Do not turn a plan into a statement of fact.
