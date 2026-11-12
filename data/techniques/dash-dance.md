---
schema: melee-technique/v1
id: dash-dance
name: Dash dance
aliases: [dashdance, DD, dash dancing, foxtrot, dash back, smash turn]
category: movement
difficulty: 2
related: [pivot, moonwalk, wavedash, jump-cancel, tech-chase, grab-and-throw]
characters: all
summary: Reversing direction repeatedly during the initial dash animation, which keeps the character mobile and uncommitted so it can bait attacks and punish them.
---

# Dash dance

## What it is

A dash starts with an initial dash animation (`Dash`) that turns into the run (`Run`) after
a character-specific number of frames. During the initial dash, smashing the stick the other
way starts a new dash in that direction almost instantly, through a 1-frame turn. Repeating
this is a dash dance: the character flickers back and forth over a short distance and can
leave it at any moment with a dash in either direction, a jump, a grab, a shield or an
attack. Once the character is in `Run`, turning around is slow [wiki:Dash] [wiki:Dash-dancing].

## Inputs

- Smash the control stick left or right to dash. Before the initial dash ends, smash it the
  opposite way; repeat.
- Length is controlled by how long each dash lasts before reversing: 2-3 frames for a tight
  "wiggle", up to the full dash length for wide dances.
- **Foxtrot:** let the initial dash finish, return the stick to neutral, and dash again in
  the same direction (repeated initial dashes instead of a run).

## Frame data and formulas

Options during the initial dash [wiki:Dash]:

| Option | Rule |
|-|-|
| Turn and dash back | smash the stick the other way; the turn takes 1 frame, during which the character counts as standing ([pivot](pivot.md)) |
| Forward smash | A or C-stick sideways during the first 3 frames of a forward dash |
| Dash attack | A after the first 3 frames |
| Shield | L/R; during the first 2 frames of a forward dash L/R gives a roll; on frame 3 it gives shield with 1 frame of delay |
| Dash grab | Z or L/R+A |
| Jump (and [jump cancel](jump-cancel.md) options) | any time |
| Side B | any time |
| Run brake then crouch | press forward again to enter `RunBrake`; from there crouch and any move |
| [Moonwalk](moonwalk.md) | tilt the stick backward without triggering a dash back |

Options during the run [wiki:Dash]: crouch (after 1 frame of `RunBrake`), dash attack,
shield, grab, jump, specials. Turning around in the run (`TurnRun`) is slow, up to 51
frames for Marth, and only a jump can interrupt it.

### Initial dash length and speeds

"Dash frames" is the length of the initial dash, the dash-dance window [wiki:Dash].

| Character | Initial dash speed | Run speed | Dash frames |
|-|-|-|-|
| Captain Falcon | 2.0 | 2.3 | 15 |
| Fox | 1.9 | 2.2 | 11 |
| Pikachu | 1.8 | 1.8 | 13 |
| Sheik | 1.7 | 1.8 | 7 |
| Marth | 1.5 | 1.8 | 15 |
| Pichu | 1.8 | 1.72 | 13 |
| Roy | 1.4 | 1.61 | 15 |
| Young Link | 1.8 | 1.6 | 13 |
| Donkey Kong | 1.6 | 1.6 | 15 |
| Yoshi | 1.33 | 1.6 | 13 |
| Falco | 1.9 | 1.5 | 11 |
| Mario, Dr. Mario | 1.5 | 1.5 | 10 |
| Mr. Game & Watch | 1.5 | 1.5 | 8 |
| Bowser | 1.0 | 1.5 | 13 |
| Samus | 1.86 | 1.4 | 8 |
| Mewtwo | 1.4 | 1.4 | 18 |
| Kirby | 1.4 | 1.4 | 12 |
| Ice Climbers | 1.4 | 1.4 | 13 |
| Ness | 1.3 | 1.4 | 13 |
| Ganondorf | 1.3 | 1.35 | 15 |
| Luigi | 1.34 | 1.34 | 10 |
| Link | 1.3 | 1.3 | 12 |
| Peach | 1.2 | 1.3 | 15 |
| Jigglypuff | 1.4 | 1.1 | 13 |
| Zelda | 1.1 | 1.1 | 15 |

Table rows with merged cells on the wiki were expanded here; Peach's initial dash speed
(1.2) and Kirby's and Ice Climbers' shared values are read from those merged rows.

**Dash back problem:** a turn from standing normally takes the `Turn` state first; to get an
immediate dash backward the stick must travel from neutral to the smash threshold within
one polling frame, which depends on controller and timing (Kadano's article "The Problem of
Back Dashes and Smash Turns" in the Library; not re-read here) [lib:Controller Mechanics: The Problem of Back Dashes and Smash Turns].

## Why it matters

- Neutral game: staying just outside the opponent's range and moving in and out makes them
  attack empty space; the dash back avoids the attack and the dash in punishes its lag
  [wiki:Dash-dancing].
- Leads straight into every approach: [SHFFL](shffl.md), jump-cancel grab, wavedash.
- [Tech chase](tech-chase.md) positioning: from a dash dance the player can reach either
  roll direction.
- Strongest for characters with long, fast initial dashes: Fox, Marth, Captain Falcon
  [wiki:Dash-dancing]. [Sheik](../characters/sheik.md) has the shortest (7 frames), which
  makes her dash dance small but gives her a quick crouch out of run [wiki:Dash-dancing].

## Common errors

- Holding a direction too long: the character enters `Run`, and the reversal becomes the
  slow `TurnRun` skid.
- Stick not smashed hard enough: `Turn` then walk instead of dash (the "slow turn").
- Dash dancing in range of the opponent's attack: movement without spacing.
- Predictable rhythm; always dashing in after exactly two dashes.
- Inputting shield in the first 2 frames of a dash and rolling instead.

## How to detect it in a training mode

- Sequence of `Dash` -> `Turn` (1 frame) -> `Dash` with alternating facing [decomp]. A
  failed dance shows `Run`, `RunBrake`, `TurnRun`, or `Turn` followed by `WalkSlow/Middle/Fast`.
- Metrics: frames per dash, distance covered, whether `Run` was entered.
- Whiff-punish drills: CPU attack misses (no hit registered) and the player's hit or grab
  lands during the CPU's remaining lag.

## Drill seeds

### Dash dance control

- **id:** `dash-dance-lengths`
- **Goal:** Dash dance at chosen widths without entering run.
- **Player:** any
- **CPU:** none
- **Setup:** Final Destination with two markers.
- **CPU behaviour:** None.
- **Success:** N reversals between the markers with no `Run` or `TurnRun` state.
- **Fail:** Entered run or left the zone.
- **Variations:** Tight (2-4 frame dashes) vs full length; end with a prompted action (grab, short hop aerial, wavedash back).
- **Data needed:** Dash frames per character.

### Dash dance whiff punish

- **id:** `dash-dance-grab-punish`
- **Goal:** Bait an attack with a dash back and punish with a dash in.
- **Player:** [Marth](../characters/marth.md), [Fox](../characters/fox.md), [Captain Falcon](../characters/captain-falcon.md), [Sheik](../characters/sheik.md)
- **CPU:** any
- **Setup:** Mid range; CPU facing the player.
- **CPU behaviour:** Attacks (dash attack, SHFFL aerial, ftilt, grab) when the player enters a trigger distance, aimed at the player's position at that moment.
- **Success:** CPU's move whiffs and the player grabs or hits during its lag.
- **Fail:** Player hit or no punish.
- **Variations:** CPU sometimes waits (player must not over-commit); CPU overshoots.
- **Data needed:** CPU move ranges and lag, player dash speeds, grab range.

## Sources

- SSBWiki: Dash (Melee sections and ranking table), Dashdance
  (https://www.ssbwiki.com/Dash). The wiki cites a community spreadsheet for dash frames.
- Melee Library: "Controller Mechanics: The Problem of Back Dashes and Smash Turns" (Kadano)
  and "Dash Dancing" (Zero, video) by description; "Ultimate Ground Movement Analysis"
  (Schmooblidon) not fetchable.
- `[decomp]`: state names from this repository.
