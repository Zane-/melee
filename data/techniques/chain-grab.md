---
schema: melee-technique/v1
id: chain-grab
name: Chain grab
aliases: [chaingrab, CG, chain throw, regrab, wobbling, hand-off, pivot regrab]
category: punish
difficulty: 3
related: [grab-and-throw, tech-chase, di, jump-cancel, pivot, hitstun-knockback]
characters: [marth, sheik, ice-climbers, peach, fox, dr-mario, mario, mewtwo, donkey-kong, pikachu, ganondorf, captain-falcon]
summary: Throwing an opponent and grabbing them again before they can act, repeated for large damage; it works on specific victims in specific percent ranges and is shaped by their DI.
---

# Chain grab

## What it is

Some throws leave the victim in hitstun close enough to the thrower that another grab
connects before the victim can jump, attack or air dodge. Repeating this is a chain grab.
Whether it works depends on the throw's knockback and angle, the thrower's speed after the
throw, the victim's fall speed and gravity (throws ignore weight for knockback, see
[grab-and-throw](grab-and-throw.md)), the percent, and the victim's [DI](di.md). When the
regrab is not guaranteed but the victim must land and tech, it becomes a
[tech chase](tech-chase.md) [wiki:Chain_grab].

## Inputs

1. Grab (usually [jump-cancel](jump-cancel.md) grab).
2. Throw (most chain grabs use up throw or down throw).
3. Watch the DI, move under or toward the victim (walk, dash, or turn), and grab again on
   the first frame they are grabbable. Against DI behind, turn around or
   [pivot](pivot.md) grab.
4. At the percent where the chain ends, replace the grab with a finisher.

## Frame data and formulas

What makes a regrab guaranteed:

```
victim hitstun from the throw  >  thrower's remaining throw animation after release
                                  + time to reach the victim + grab startup (frame 7 for most)
```

- Hitstun = floor(0.4 x knockback) and the throw's knockback uses weight 100 for everyone
  [wiki:Hitstun] [wiki:Throw].
- The victim cannot SDI a throw release (no hitlag) [wiki:Hitlag]; DI is read on the frame
  before release [web:smashboards.com].
- Weight-dependent throws run slower on heavier victims, changing both sides of the
  inequality [web:smashboards.com].
- Fastfallers fall back into grab range sooner, which is why most up-throw chain grabs work
  on Fox, Falco and Captain Falcon.

### Known chain grabs

As listed by the wiki (which marks its own list as incomplete and lacking specifics)
[wiki:Chain_grab]. Percent ranges are the wiki's; they are approximate and DI dependent.

| Thrower | Throw | Victims | Range and conditions |
|-|-|-|-|
| [Sheik](../characters/sheik.md) | dthrow | Bowser, Yoshi, Donkey Kong, Pikachu, Ganondorf, Pichu, Roy, Young Link, Mr. Game & Watch, Link, Ness, Sheik | from as low as 0% to medium/high percent, up to about 90% with poor DI. NTSC only: in PAL the dthrow angle is more horizontal and regrabs work only at very low percent. On other characters it tech chases to high percent |
| [Marth](../characters/marth.md) | uthrow | Fox, Falco | 0% to about 60% |
| [Roy](../characters/roy.md) | uthrow | Fox, Falco | 0% to about 60% |
| [Marth](../characters/marth.md) | fthrow, dthrow | Jigglypuff | until about 20%, DI dependent |
| [Peach](../characters/peach.md) | uthrow | Fox, Falco, Captain Falcon | starts between 0% and 18% depending on DI and character, up to fairly high percent, usually ending in a finisher |
| [Peach](../characters/peach.md) | dthrow | most characters (not Mario, Dr. Mario, Luigi, Zelda and others who can jump out) | to high percent on heavy characters, only if they do not DI away |
| [Fox](../characters/fox.md) | uthrow | Fox, Falco | until mid percent, then usmash or uair depending on DI |
| [Mario](../characters/mario.md), [Dr. Mario](../characters/dr-mario.md) | uthrow | Fox, Falco, Captain Falcon | not specified |
| [Mario](../characters/mario.md), [Dr. Mario](../characters/dr-mario.md) | dthrow | heavyweights and fastfallers | not specified |
| [Mewtwo](../characters/mewtwo.md) | dthrow | Bowser | 0-50% |
| [Mewtwo](../characters/mewtwo.md) | dthrow | Fox, Falco, Sheik, Captain Falcon, sometimes Roy | DI dependent |
| [Donkey Kong](../characters/donkey-kong.md) | uthrow, cargo uthrow | Fox, Falco, Captain Falcon | low to mid percent |
| [Ice Climbers](../characters/ice-climbers.md) | dthrow (Popo alone) | Roy, Sheik, Ganondorf and a few others | until about 50% |
| [Ice Climbers](../characters/ice-climbers.md) | hand-offs between Popo and Nana, dthrow + Nana dair, wobbling | nearly every character | wobbling (Popo pummels while Nana attacks in rhythm) is inescapable when done correctly and is banned at most tournaments |

Other chain grabs the community recognises but the wiki list omits (no numbers, general
knowledge): [Pikachu](../characters/pikachu.md) uthrow on fastfallers,
[Captain Falcon](../characters/captain-falcon.md) and [Ganondorf](../characters/ganondorf.md)
throws into regrab on fastfallers at low percent. See the character files for sourced
ranges.

### How the victim breaks it

- **DI** the throw: full away or full behind to maximise the distance the thrower must
  cover; slight DI to make the thrower misjudge; mixing so the thrower must react
  [wiki:Directional_influence].
- **Act on the first free frame:** jump, shine (Fox/Falco), fast aerial, or up B as soon as
  hitstun ends; if the regrab is late it loses.
- **Land on a platform** and tech.
- **SDI** any hits that are part of the throw animation (e.g. Fox uthrow lasers)
  [web:smashboards.com].
- Mash out during pummels ([grab-and-throw](grab-and-throw.md)).

## Why it matters

A single grab becomes 40-60% or a stock. Marth's uthrow chain on Fox and Falco and Sheik's
dthrow chain (NTSC) define those matchups at low percent, and the Ice Climbers' whole game
plan is built on grab conversions. For a training mode, chain grabs are ideal drills: a
repeatable loop with a clear success condition and a small set of CPU DI choices.

## Common errors

- Regrab too early (victim still thrown/ungrabbable or above the grab box) or too late
  (victim jumps or shines out).
- Dash grab instead of standing/JC grab: more startup, misses the window.
- Not turning around for DI behind.
- Continuing past the percent where the throw sends too far; missing the switch to a
  finisher (for Marth on spacies: uthrow to utilt/uair/fsmash).
- Walking off or being carried to the edge or under a platform and losing the chain.

## How to detect it in a training mode

- Loop detection: victim goes `ThrownHi`/`ThrownLw` -> `DamageFly*`/`Damage*` ->
  `CapturePulled*` without ever being actionable in between (hitstun counter still positive
  when the grab connects) [decomp].
- "Guaranteed" check: frames between the victim's hitstun end and the regrab connecting;
  negative = true regrab, positive = the victim could have acted.
- Count regrabs and damage dealt; classify the failure as early whiff (`Catch` with no
  capture before hitstun ended) or late (victim state became `JumpAerial*`, an attack, or
  another action).
- CPU DI profile per throw: none, full away, full behind, slight away, slight behind,
  random.

## Drill seeds

### Marth up throw chain on spacies

- **id:** `chain-grab-marth-uthrow-spacies`
- **Goal:** Chain uthrow from 0% and finish.
- **Player:** [Marth](../characters/marth.md)
- **CPU:** [Fox](../characters/fox.md), [Falco](../characters/falco.md)
- **Setup:** Final Destination, CPU grabbed at 0%.
- **CPU behaviour:** Random DI per throw; jumps or shines on the first actionable frame.
- **Success:** At least N consecutive regrabs, then a finisher that connects, with the CPU never actionable.
- **Fail:** CPU escapes.
- **Variations:** DI restricted to one type; start at other percents; platform stages.
- **Data needed:** Marth uthrow release/actionable frames, Fox/Falco fall speeds, range above (0 to about 60%).

### Sheik down throw chain (NTSC)

- **id:** `chain-grab-sheik-dthrow`
- **Goal:** Regrab or tech chase off dthrow.
- **Player:** [Sheik](../characters/sheik.md)
- **CPU:** [Sheik](../characters/sheik.md), [Ganondorf](../characters/ganondorf.md), [Link](../characters/link.md), [Roy](../characters/roy.md), [Pikachu](../characters/pikachu.md), [Young Link](../characters/young-link.md) (chain); [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Captain Falcon](../characters/captain-falcon.md) (tech chase)
- **Setup:** CPU grabbed at 0-30%.
- **CPU behaviour:** Random DI; techs randomly when the throw knocks down.
- **Success:** Consecutive regrabs to a target percent.
- **Fail:** CPU escapes.
- **Variations:** Percent; finisher required.
- **Data needed:** Sheik dthrow data (release 39, actionable 61 [web:smashboards.com]), victim fall speeds.

### Escape the chain grab

- **id:** `chain-grab-escape-di-mix`
- **Goal:** As the victim, break a chain grab with DI mixups and a frame-perfect escape.
- **Player:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Captain Falcon](../characters/captain-falcon.md)
- **CPU:** [Marth](../characters/marth.md), [Peach](../characters/peach.md), [Sheik](../characters/sheik.md)
- **Setup:** Player grabbed at low percent.
- **CPU behaviour:** Chain grabs with human-like reaction (covers the DI it saw N frames ago; configurable error).
- **Success:** Player escapes within K throws.
- **Fail:** Taken to the finisher.
- **Variations:** CPU reaction quality.
- **Data needed:** Throw data, DI limits.

## Sources

- SSBWiki: Chain grab, Throw, Hitstun, Hitlag, Directional influence
  (https://www.ssbwiki.com/Chain_grab).
- Magus420's throw data (Smashboards, Wayback Machine copy), tagged `[web:smashboards.com]`.
- `[decomp]`: state names from this repository. Character-specific ranges beyond the wiki
  list are deliberately left to the character files.
