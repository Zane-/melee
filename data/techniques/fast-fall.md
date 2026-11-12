---
schema: melee-technique/v1
id: fast-fall
name: Fast fall
aliases: [FF, fastfall, fast falling]
category: movement
difficulty: 1
related: [shffl, short-hop, l-cancel, ledgedash, recovery, auto-cancel]
characters: all
summary: Tapping down while falling sets the character's downward speed to its faster fast-fall speed until landing, shortening every jump and aerial.
---

# Fast fall

## What it is

Each character has a normal maximum falling speed and a higher fast-fall speed. Tapping down
on the control stick while the character is moving downward immediately sets vertical speed
to the fast-fall speed; gravity is ignored from then on. It lasts until the character lands,
is hit, or jumps. It cannot be started while tumbling [wiki:Fastfall].

## Inputs

- Tap (smash) the control stick down while the character is falling, that is after the
  apex of the jump.
- Tapping down while hanging on the ledge lets go and starts a fast fall at once (a slow
  tilt down or away only lets go) [wiki:Fastfall].
- A fast fall cannot begin while the character is still rising. The earliest frame is the
  first frame with downward velocity.

## Frame data and formulas

Falling speeds in units per frame [wiki:Fastfall]:

| Character | Normal fall | Fast fall | Increase |
|-|-|-|-|
| Falco | 3.1 | 3.5 | 12.9% |
| Captain Falcon | 2.9 | 3.5 | 20.7% |
| Fox | 2.8 | 3.4 | 21.4% |
| Link | 2.13 | 3.0 | 40.8% |
| Sheik | 2.13 | 3.0 | 40.8% |
| Donkey Kong | 2.4 | 2.96 | 23.3% |
| Yoshi | 1.93 | 2.93 | 51.8% |
| Roy | 2.4 | 2.9 | 20.8% |
| Pikachu | 1.9 | 2.7 | 42.1% |
| Ganondorf | 2.0 | 2.6 | 30.0% |
| Marth | 2.2 | 2.5 | 13.6% |
| Pichu | 1.9 | 2.5 | 31.6% |
| Bowser | 1.9 | 2.4 | 26.3% |
| Mario, Dr. Mario, Mr. Game & Watch | 1.7 | 2.3 | 35.3% |
| Mewtwo | 1.5 | 2.3 | 53.3% |
| Samus | 1.4 | 2.3 | 64.3% |
| Young Link | 2.13 | 2.2 | 3.3% |
| Ness | 1.83 | 2.2 | 20.2% |
| Luigi, Kirby, Ice Climbers | 1.6 | 2.0 | 25.0% |
| Peach | 1.5 | 2.0 | 33.3% |
| Zelda | 1.4 | 1.85 | 32.1% |
| Jigglypuff | 1.3 | 1.6 | 23.1% |

Other facts:

| Fact | Value | Source |
|-|-|-|
| Effect on speed | instantly set to fast-fall speed, no acceleration | [wiki:Fastfall] |
| Ends | on landing, on being hit, or on jumping | [wiki:Fastfall] |
| While tumbling | the general description says not possible; the wiki's Tumbling page says tumbling characters can fast fall in Melee. The two pages disagree; treat as unverified | [wiki:Fastfall] [wiki:Tumbling] |
| Landing lag | unchanged by fast falling: one normal landing animation, 4 frames for most | [wiki:Landing_lag] |
| Knockback | while in knockback, a character's own fall speed still applies (not fast fall) | [wiki:Knockback] |

"Fastfallers" as a character class means characters with high normal fall speed and
gravity (Fox, Falco, Captain Falcon), not characters who are fast falling.

## Why it matters

- Shortens the vulnerable time in the air; part of [SHFFL](shffl.md).
- Changes aerial timing: a fast-fallen aerial hits lower and lands sooner, so mixing
  fast-fall timings changes when and where the hit arrives.
- Reaching the ledge or the ground before an opponent's hitbox
  ([edgeguarding](edgeguarding.md), [ledgedash](ledgedash.md) set-ups, haxdash).
- Timing an aerial to land in its [auto-cancel](auto-cancel.md) window, or deliberately not
  fast falling so the aerial finishes before landing.

## Common errors

- Tapping down before the apex: nothing happens, and the player believes they fast fell.
- Holding down from earlier (stick already down at the apex): no new tap, no fast fall.
- Fast falling into the ledge while still holding down: the ledge is not grabbed
  ([recovery](recovery.md)).
- Fast falling a multi-hit or slow aerial so it lands before the strong hit comes out.
- C-stick down for the aerial does not fast fall; only the control stick does.
- Fast falling offstage with a character that cannot recover from that depth.

## How to detect it in a training mode

- The fighter has a fast-fall flag; observable equivalent: vertical velocity equals minus
  the character's fast-fall speed while airborne and not in hitstun.
- Timing metric: frames between the apex (first frame with downward velocity) and the
  fast-fall start. 0-1 = immediate.
- For SHFFL drills: whether the fast fall started before the aerial's hit and how many
  frames the whole jump lasted.

## Drill seeds

### Fast fall at the apex

- **id:** `fast-fall-apex-timing`
- **Goal:** Start the fast fall on the first falling frame.
- **Player:** any
- **CPU:** none
- **Setup:** Flat stage, repeated short hops and full hops.
- **CPU behaviour:** None.
- **Success:** Fast fall begins within 2 frames of the apex, 10 times in a row.
- **Fail:** No fast fall, or later.
- **Variations:** With an aerial; from a double jump; onto platforms.
- **Data needed:** Jump airtime to locate the apex (or read velocity).

### Fast fall timing mixups

- **id:** `fast-fall-delay-mix`
- **Goal:** Hit a shield early or late on command by changing the fast-fall timing.
- **Player:** [Marth](../characters/marth.md), [Falco](../characters/falco.md), [Fox](../characters/fox.md), [Captain Falcon](../characters/captain-falcon.md)
- **CPU:** any, shielding
- **Setup:** CPU in shield; drill prompts "early" or "late".
- **CPU behaviour:** Releases shield and attacks at a fixed time that only the prompted timing beats.
- **Success:** Aerial lands at the prompted timing and wins the exchange.
- **Fail:** Wrong timing or hit.
- **Variations:** No prompt; CPU picks randomly.
- **Data needed:** Aerial hit frames, short hop airtime.

## Sources

- SSBWiki: Fast fall, Tumbling, Landing lag, Knockback (https://www.ssbwiki.com/Fast_fall).
- Melee Library: "Analysis of Aerial Drift and Fastfall Timings with Mango's Marth"
  (SSBM Tutorials, video; description only).
