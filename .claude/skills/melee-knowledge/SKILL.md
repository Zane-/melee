---
name: melee-knowledge
description: Look up competitive Melee game knowledge from the data/ knowledge base - exact frame data, character attributes, out-of-shield options, knockback and shield-advantage calculations, character tech, combos, kill percents, recovery, matchups and universal techniques. Use before designing or tuning any training scenario, drill or CPU behaviour, when a task names a character, move or technique, or when a number about the game (frames, percents, weights) is needed.
---

# Melee knowledge base lookups

Everything is under `data/` (overview, formats and trust levels: `data/README.md`). Never
answer a frame or percent question from memory when the data has it.

## What is where

| Need | Go to |
|-|-|
| A character: how they play, their tech, punishes, recovery, drill ideas | `data/characters/<id>.md` |
| Which character fits (weight, fall speed, tier, archetype) | `data/characters/README.md` |
| A universal technique or mechanic (wavedash, shield drop, DI, teching, ledge options) | `data/techniques/<id>.md`, index in `data/techniques/README.md` |
| Exact numbers for a move | `python tools/melee_data/query.py <id> <move>` or the `Frame data` section of the character file |
| Everything about a move as data (hitbox sizes, offsets, bones) | `data/framedata/<id>.json` |
| Community guides on a topic | `Resources` section of the character file, `data/resources/README.md` |
| The fighter's code and action state enums | front matter `code:` of the character file (e.g. `src/melee/ft/kinds/ftFox/forward.h`) |

Character ids: `bowser captain-falcon donkey-kong dr-mario falco fox ganondorf ice-climbers
jigglypuff kirby link luigi mario marth mewtwo mr-game-and-watch ness peach pichu pikachu roy
samus sheik yoshi young-link zelda`.

Move keys: `jab1 jab2 jab3 dash_attack ftilt utilt dtilt fsmash usmash dsmash nair fair bair
uair dair grab dash_grab pummel fthrow bthrow uthrow dthrow spotdodge roll_forward
roll_backward airdodge tech_in_place tech_roll_forward tech_roll_backward
getup_attack_faceup ledge_getup ledge_roll ledge_attack ledge_jump_1 ...` and specials by
internal state: `special_n*`, `special_s*`, `special_hi*`, `special_lw*` (ground) and
`special_air_*`. `python tools/melee_data/query.py <id>` prints every key a character has.

## Reading a character file without loading all of it

Files are 40-70 KB. Read by section:

```sh
grep -n "^## \|^### " data/characters/fox.md          # table of contents with line numbers
sed -n '/^## Drill seeds/,/^<!-- GENERATED:framedata/p' data/characters/fox.md
sed -n '/^### Aerials/,/^### Grabs/p' data/characters/fox.md
sed -n '1,/^---$/p' data/characters/fox.md | head -120  # front matter: attributes, move index, OOS
```

The front matter `moves:` map (`key: [first hit frame, first actionable frame, max damage]`)
and `oos:` map answer most quick questions.

Search across characters:

```sh
grep -rn -i "chain grab" data/characters/*.md | head
grep -ln "tech-chase" data/characters/*.md
grep -n "^- \*\*id:\*\*" data/characters/*.md data/techniques/*.md   # every tech and drill id
```

## Calculators

```sh
python tools/melee_data/query.py list                        # weight, gravity, fall speed, jump squat
python tools/melee_data/query.py oos fox                     # out-of-shield options, fastest first
python tools/melee_data/query.py shield marth fsmash fox     # advantage on shield, which OOS options punish
python tools/melee_data/query.py kb fox usmash marth 90      # knockback, hitstun, hitlag, tumble at 90%
python tools/melee_data/query.py kb marth dtilt fox 60 --cc  # same, crouch cancelled
python tools/melee_data/query.py thresholds sheik dthrow fox # percent where knockdown starts / CC stops working
python tools/melee_data/query.py fox dair --json             # raw data
```

Use `--hit N` to pick a later hit row (late hit, sourspot) of a move; `query.py <id> <move>`
lists them. Formulas are in `data/README.md` and `tools/melee_data/calc.py`.

## Rules for using the numbers

1. Frames are 1-indexed. First actionable frame = IASA if the move has one, else total + 1.
2. Generated tables and `query.py` beat prose. Prose numbers carry a source tag; `[unverified]`
   means recalled, and `[fd]` came from an older dump that has known errors on multi-hit
   moves and grabs (see `data/README.md`, "Trust levels").
3. The tools ignore range, shield pushback, staleness, DI and SDI. A computed "punishes" or
   percent threshold is a starting value: say so, and tune in Dolphin.
4. Special-move frames may be off by one (entry delay not determined per special), and
   projectile hitboxes are not extracted. For those use the character prose and the fighter's
   code.
5. Hitstun and knockback thresholds use the pre-hit percent you pass plus the move's damage.
6. If the data is missing or looks wrong, say so. Fix prose in place (keep headings and field
   lists), or fix the extractor and regenerate; do not hand-edit generated blocks.

## Keeping it current

```sh
python tools/melee_data/extract.py   # needs the extracted disc in build/disc/files
python tools/melee_data/render.py    # refresh generated blocks and indexes after any edit
```

New prose facts need a source tag. New techniques go in `data/techniques/<id>.md` with the
front matter described in `data/README.md`, then `render.py` to update the index.
