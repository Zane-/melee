# Melee knowledge base

Game knowledge for building training scenarios from prompts: who the characters are, what
their moves do frame by frame, which techniques matter, and what the community has written
about them. Written for AI agents first. Version: **NTSC 1.02** everywhere.

Start from the skill `.claude/skills/melee-knowledge/SKILL.md` (how to look things up) or
`.claude/skills/design-training-scenario/SKILL.md` (prompt to scenario spec).

## Layout

| Path | What | Written by |
|-|-|-|
| `characters/<id>.md` | One file per character: overview, character tech, punishes, kill options, recovery, matchups, drill seeds, exact frame data, community resources | Research (prose) + generator (marked blocks) |
| `characters/README.md` | Index table of all 26 characters | Generator |
| `techniques/<id>.md` | Universal techniques and mechanics (wavedash, shield, DI, teching, ledge options, knockback formulas...) | Research |
| `techniques/README.md` | Index of techniques | Generator |
| `courses/<id>.md`, `courses/universal.md` | Character courses: the ordered Tech / Neutral / Punish / Defense curriculum and each drill's spec and guide (`courses/README.md`) | `plan-character-course`, `design-training-scenario` skills |
| `framedata/<id>.json` | Machine-readable frame data and attributes, extracted from the game files | `tools/melee_data/extract.py` |
| `resources/README.md`, `resources/library/*.md` | The Melee Library link index, by section | Generator |
| `resources/meleelibrary.json` | Parsed snapshot of meleelibrary.com (2026-11-11) | `tools/melee_data/library.py` |

Character ids (file names, link targets, tool arguments):
`bowser captain-falcon donkey-kong dr-mario falco fox ganondorf ice-climbers jigglypuff kirby
link luigi mario marth mewtwo mr-game-and-watch ness peach pichu pikachu roy samus sheik yoshi
young-link zelda`

## Character file format

YAML front matter, then fixed headings in a fixed order. Hand-written keys come first; the
generator owns everything between `# generated: begin` and `# generated: end`.

```yaml
---
schema: melee-character/v1
id: fox                      # slug, same as the file name
name: Fox
aliases: [...]
tier: "S (1st of 26), 2021"  # most recent official NTSC tier list
archetype: [rushdown, fastfaller, technical]
related: [falco]             # other character ids
summary: one sentence on how the character wins
key_tech: [waveshine, ...]   # ids of the sections under "Character tech"
# generated: begin
dat: PlFx.dat                # fighter data file the numbers come from
framedata: ../framedata/fox.json
code: src/melee/ft/kinds/ftFox   # decomp module (action states in its forward.h)
specials: {neutral_b, side_b, up_b, down_b}   # community names
attributes: {weight, gravity, fall_speed, fast_fall_speed, jump_squat, ...}
moves:                       # key: [first hit frame, first actionable frame, max damage]
  usmash: [7, 42, 18]
oos:                         # out-of-shield option: frame its hitbox is out
  special_air_lw_start: 4
resources: 45                # number of Melee Library links
# generated: end
---
```

Body headings, in order: `Attributes` (generated), `Overview`, `Strengths and weaknesses`,
`Character tech`, `Neutral game`, `Punish game` (with `Chain grabs and tech chases`),
`Kill options`, `Recovery` (with `Edgeguarding <Name>`), `Defense and out of shield`,
`As the training dummy`, `Matchup notes`, `Drill seeds`, `Frame data` (generated),
`Resources` (generated), `Sources`.

Two list formats repeat and are meant to be parsed:

- **Character tech** entries (`### <name>`): `id`, `What`, `Inputs`, `Timing`, `Used for`,
  `Common errors`, `Drill idea`.
- **Drill seeds** (`### <name>`): `id`, `Goal`, `Player`, `CPU`, `Setup`, `CPU behaviour`,
  `Success`, `Fail`, `Variations`, `Data needed`. These are scenario ideas, not implemented
  events.

Technique files (`schema: melee-technique/v1`) have front matter `id name aliases category
difficulty related characters summary` and headings `What it is`, `Inputs`, `Frame data and
formulas`, `Why it matters`, `Common errors`, `How to detect it in a training mode`,
`Drill seeds`, `Sources`.

## Trust levels

Not everything here is equally reliable. In order:

1. **Generated blocks and `framedata/*.json`**: read from the retail fighter files by
   `extract.py`. Exact, with the gaps listed below.
2. **Prose numbers tagged `[fd]`**: taken from a frame data dump. If one disagrees with the
   generated table, the table wins (the public dump the researchers used runs multi-hit loops
   one time too many and reports grabs one frame early; see "Validation").
3. **`[wiki:Page]`, `[lib:Title]`, `[web:domain]`**: a source the researcher read. Percent
   ranges depend on DI, staleness and stage; treat them as starting values to tune in game.
4. **`[unverified]`**: recalled, not sourced. Check before building a drill on it.

## Frame data conventions

- Frames are **1-indexed**: "hits on frame 7" means the hitbox first exists on the 7th frame
  of the move, and an input on frame 1 makes that frame 7.
- `Active a-b`: frames a hitbox is out (inclusive). Several ranges = multi-hit.
- `Total`: length of the animation. `IASA`: first frame the move can be interrupted
  (interruptible as soon as). First actionable frame = `IASA` if present, else `Total + 1`.
- `Dmg / Angle / BKB / KBG / Set KB`: damage, launch angle in degrees (`Sakurai` = 361: about
  44 degrees on airborne targets and on strong hits, 0 on weak grounded hits), base
  knockback, knockback growth, weight-dependent set knockback (when non-zero the percent does
  not matter). Slash-separated values are different hitboxes of the same window.
- `Land lag / L-cancel`: landing lag of an aerial and the halved, rounded-down L-cancelled
  value. `Autocancel <a, >b`: landing before frame a or after frame b gives the normal
  landing lag instead.
- `Shield stun`: frames the defender is stuck in shield for that damage on a full hard
  shield. `On shield`: attacker's frame advantage (negative = defender acts first).
- **Entry delay.** Jab 2, jab 3, grab, dash grab, pummel, taunt, techs, getup-stand, shield
  release and landing are entered without stepping their script on the entry frame, so
  everything happens one frame later than the script says and the state lasts one frame
  longer. The tables already include this (`entry_delay: 1` in the JSON; "starts 1 frame late
  (included)" in notes). Evidence: `Fighter_ChangeMotionState` without `ftAnim_8006EBA4` in
  `ftCo_Catch.c`, `ftCo_Attack1.c`, `ftCo_Passive.c`, `ftCo_DownStand.c`, and frame-by-frame
  captures (grab is 30 frames long with the grab box on frame 7 for most characters).
- **Special moves** are split into the game's internal states (`special_lw_start`,
  `special_lw_loop`...). Frames count from the start of each state. Whether a given special
  has the entry delay was not determined, so treat special-move frames as +/-1 until checked
  in game. Known good: Fox and Falco shine hits on frame 1.
- **Tech and getup-stand intangibility** is listed as 2-20 (script plus entry delay) where
  community tables say 1-20. Which one holds on the entry frame is unverified.

### What the extraction does not cover

- Projectiles and other articles (lasers, needles, turnips, missiles, bombs, boomerangs,
  Fire Fox's flame is included because it is a fighter hitbox). Their hitboxes live in item
  data, not fighter scripts. Use the character prose (sourced from SSBWiki) for those.
- Behaviour implemented in code rather than script: Peach's float, Yoshi's double-jump
  armour, Jigglypuff's Rest timing beyond its script, counters, reflectors, charge levels,
  jump-cancel windows. Read the character's code (front matter `code:`, e.g.
  `src/melee/ft/kinds/ftFox`) when a drill depends on it.
- Nana (Ice Climbers partner) is not listed separately; she uses `PlNn.dat`.
- Hitbox positions and sizes are in the JSON (`offset`, `size`, `bone`) but nothing here
  computes range. Spacing has to be tuned in game.
- Kirby's copy abilities.

## Formulas

Implemented in `tools/melee_data/calc.py`; use the query tool rather than computing by hand.

- **Knockback**: `KB = ((p/10 + p*d/20) * 200/(w+100) * 1.4 + 18) * KBG/100 + BKB` with `p` =
  target percent after the hit, `d` = damage, `w` = target weight. With set knockback, `p` =
  10 and `d` = the set value. Throws use `w` = 100 for every victim. Crouch cancel multiplies
  KB by 2/3.
- **Hitstun** = `floor(0.4 * KB)` frames. **Tumble** (and knockdown on landing) at `KB >= 80`.
- **Launch speed** = `0.03 * KB` units per frame, decaying 0.051 per frame.
- **Hitlag** = `floor(d/3 + 3)` frames (electric x1.5, capped at 20).
- **Shield stun** = `floor((1.5 * d * (0.3 + 0.65 * L) + 2) * 200/201)` with `L` = 0 for a
  full hard shield and 1 for the lightest shield. Read from `ftCo_80092ED8` /
  `ftCo_80092F2C` in `src/melee/ft/kinds/ftCommon/ftCo_Guard.c` and the constants in
  `PlCo.dat` (1.5, 2.0, 0.05, 0.7; the 200/201 factor is the 20-frame `GuardSetOff`
  animation played at rate 20.1 / stun). For a hard shield this is the community's
  `floor((d + 4.45) / 2.235)`.
- **Out of shield** (frame the hitbox is out, counting the first frame of acting as frame
  1): aerial = jump squat + aerial startup; up smash or up B = 1 + startup (jump-cancelled);
  shield grab = grab startup; wavedash = actionable on jump squat + 12.
- Knockback, hitstun and hitlag formulas are the standard community ones (SSBWiki
  "Knockback", "Hitstun", "Hitlag"); they were not re-derived from the decomp here. See
  `techniques/hitstun-knockback.md`.

Other constants read from `PlCo.dat` through the decomp: ledge-hang intangibility 30 frames
(`ftCo_CliffWait.c`, `x49C`), slow ledge options from 100% (`x488`).

## Querying

```sh
python tools/melee_data/query.py list                       # all characters, key attributes
python tools/melee_data/query.py fox                        # attributes and move keys
python tools/melee_data/query.py fox usmash                 # one move, every hit
python tools/melee_data/query.py oos fox                    # out-of-shield options by speed
python tools/melee_data/query.py shield marth fsmash fox    # on-shield advantage + punishes
python tools/melee_data/query.py kb fox usmash marth 90     # knockback, hitstun at 90%
python tools/melee_data/query.py thresholds marth dtilt fox # knockdown / crouch-cancel percents
```

For prose, grep: `grep -n "^### " data/characters/fox.md` lists every tech, matchup and drill
seed; `grep -rn "chain grab" data/characters/` finds who chain grabs whom.

## Regenerating

```sh
python tools/melee_data/extract.py     # Pl*.dat (build/disc/files) -> data/framedata/*.json
python tools/melee_data/library.py     # meleelibrary.com -> data/resources/meleelibrary.json
python tools/melee_data/render.py      # fill generated blocks, indexes, resources/library/
```

`render.py` only rewrites the generated front matter keys and the three
`<!-- GENERATED:name -->` blocks; prose is untouched. Edit prose by hand (keep the headings
and the field lists), then re-run `render.py` to refresh the indexes.

## Validation

- **Against a public dump** (pfirsich's meleeFrameDataExtractor JSON, 576 common moves across
  26 characters): totals, IASA, first hit frame, landing lag and autocancel agree except
  where that dump is wrong: it runs script loops once too often (extra hit on Fox's down
  air, Peach's down smash...), drops a hit window that lasts until the animation ends (Link
  neutral air's late hit), and swaps the subroutine/goto opcodes. The loop count and opcodes
  here follow `src/melee/lb/lbcommand.c`.
- **Against frame-by-frame hitbox captures** (the 969 animations this folder originally
  held, one image per game frame): 453 of 566 comparable moves had exactly the extracted
  length; the rest were grabs, jab 2/3 and taunts (one frame longer, which is how the entry
  delay was found), Mr. Game & Watch (captures two frames long) and a few captures that
  were trimmed or held more than one move. Fox's down air capture shows 7 hits on frames
  5-24, matching the extraction and not the public dump.

## Provenance

- Frame data and attributes: the user's NTSC 1.02 disc, via `tools/melee_data/extract.py`.
- Resource index: [The Melee Library](https://www.meleelibrary.com/) by Daniel Baggerman,
  one page, 871 of its 881 link cards parsed 2026-11-11 (ten are lost to malformed markup). Only titles, authors, URLs and the library's
  own short descriptions are stored.
- Prose: summarised from SSBWiki and reachable library links by research agents on
  2026-11-11, each file listing its sources. smashboards.com blocks automated fetches and
  videos cannot be read, so many library links informed topic selection only.
- The raw hitbox animations (6.7 GB of APNG/GIF/MP4 per move, from a frame data
  visualisation site) were used for validation and then removed.
