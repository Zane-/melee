---
name: plan-character-course
description: Write or extend a character's training course (data/courses/<id>.md) - the ordered curriculum of Tech, Neutral, Punish and Defense drills for one character, drawn from the data/ knowledge base. Use when asked to plan, draft, outline, reorder or extend a character course or curriculum, or to decide which drills a character needs, before specifying or implementing individual drills.
---

# Plan a character course

Architecture: `docs/ai/training-courses.md`. File format, the four parts and the status
ladder: `data/courses/README.md`. Worked example: `data/courses/fox.md`. Lookups:
`melee-knowledge` skill.

A course plan is a set of plan tables, one per part, every drill `planned`. Specifying a
drill (`design-training-scenario`) and implementing it (`add-course-drill`) come after, one
drill at a time. Do not write specs or code while planning.

## 1. Collect candidates

From `data/characters/<id>.md`:

| Section | Gives |
|-|-|
| `Character tech` (and front matter `key_tech`) | Tech drills, one per entry worth drilling |
| `Punish game` table, `Chain grabs and tech chases`, `Kill options` | Punish drills: one per conversion a player must know |
| `Neutral game`, `Matchup notes` | Neutral drills: the character's real openings and what they lose to |
| `Defense and out of shield`, `As the training dummy`, `Recovery`, `Edgeguarding <Name>` | Defense drills: what this character gets caught in and how it gets out |
| `Drill seeds` | Ready-made ideas; reuse their ids as the base of drill ids |

From `data/techniques/`: the universal drills (`data/courses/universal.md`) and each
technique's `Drill seeds`. From the opponents' files: `As the training dummy` (how they
escape this character's punishes) and their punish tables (what they do to this character).

```sh
grep -n "^### \|^- \*\*id:\*\*" data/characters/<id>.md
grep -rn "(<id>.md)" data/characters/*.md | grep -i "chain grab\|tech chase\|edgeguard" | head -40
```

## 2. Sort into the four parts

Use the definitions in `data/courses/README.md`. The test for each drill:

- **Tech**: can it be practised with no opponent decision at all? Then it is Tech.
- **Punish**: does the repetition start with the player already having the advantage?
- **Defense**: does it start with the CPU having the advantage?
- **Neutral**: does it start with nobody having it? It must name the punish drill it ends in.

One idea often yields two or three drills: waveshine (Tech), waveshine to up smash (Punish),
running shine (Neutral). Keep them separate and chain them with `Requires` / `Leads to`.

## 3. Order and chain

- Within a part: prerequisites first, combinations later. Universal fundamentals precede
  character tech that uses them.
- Every Neutral drill has a `Leads to` in Punish. Punish drills whose mirror exists in
  another character's Defense part are worth noting in that course, not here.
- Aim for a course a player can finish: roughly 10-16 Tech, 8-12 Punish, 8-12 Defense, 6-10
  Neutral. Cut drills that teach the same decision twice.

## 4. Choose opponents

Each non-Tech drill names its CPU characters. Pick where the situation is real and common:
the top and high tiers first (`data/characters/README.md`), the matchup the technique is
famous in, and at least one opponent of each relevant class (fastfaller, floaty, heavy) when
the answer changes with class. The rotation system preloads a limited number of characters
per session (`TM_ROT_MAX_CHARS` in `src/melee/tm/rotation/tm_rotation.h`), so a deck should
not need more than that at once.

## 5. Write the file

- Front matter and plan tables exactly as in `data/courses/README.md`; `status: draft`.
- Every row links the knowledge-base section it comes from. A row with nothing to link to is
  a sign the knowledge base lacks the facts: add them there first (with source tags) or drop
  the drill.
- Note where a TM-CE event already covers the drill (`docs/ai/tmce-native.md` lists them).
- End with open questions for the owner: cuts, order, matchup depth.

## 6. Check

```sh
python3 - <<'PY'
import re,os,glob
for p in glob.glob('data/courses/*.md'):
    s=open(p).read()
    for m in re.finditer(r'\]\(([^)#\s]+)(#[^)]*)?\)', s):
        t=os.path.normpath(os.path.join(os.path.dirname(p), m.group(1)))
        if not m.group(1).startswith('http') and not os.path.exists(t): print(p, 'broken', m.group(1))
    ids=re.findall(r'^\| *\d* *\|? *`([a-z0-9-]+)`', s, re.M)
    dup={i for i in ids if ids.count(i)>1 and not i.startswith('universal-')}
    if dup: print(p, 'duplicate ids', dup)
PY
```

Also check by eye: every `Requires` and `Leads to` names an id that exists in this course or
in `universal.md`; ids are `<character>-<kebab>` and unique across courses.

Report the plan as a proposal: part sizes, the drills you cut and why, and the open
questions. The owner decides the curriculum.
