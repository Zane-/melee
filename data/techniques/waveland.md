---
schema: melee-technique/v1
id: waveland
name: Waveland
aliases: [wavelanding, platform waveland, ledge-cancel, edge cancel, no-impact landing, aerial waveland]
category: movement
difficulty: 3
related: [wavedash, ledgedash, shield-drop, fast-fall, auto-cancel, short-hop]
characters: all
summary: Air dodging into the ground or a platform from an existing jump or fall, to land with a controllable slide and only 10 frames of lag; the base of platform movement and the ledgedash.
---

# Waveland

## What it is

The same mechanic as a [wavedash](wavedash.md), started from the air instead of from the
ground: while rising through or falling onto a surface, the player air dodges into it. The
air dodge is cut short by the landing, and the character slides with the air dodge's
horizontal speed. Because the air dodge can be aimed sideways or slightly upward as well as
down, a waveland can snap a rising character onto a platform they have just passed through
[wiki:Wavedash].

Related landing tricks:

- **Edge cancel (ledge cancel):** sliding off the edge of a platform or stage during
  landing lag ends the lag immediately, because the character becomes airborne. Wavelands
  and aerial landings near an edge are aimed to slide off for this reason
  [lib:Edge Cancels Part 1] (card description only).
- **No-impact landing (NIL):** landing on a platform at the top of a jump with no landing
  animation; used in some [ledgedash](ledgedash.md) variants [wiki:Edge_getup].

## Inputs

1. Be airborne near a surface: jumping up through a platform, falling onto it, or after a
   double jump from the ledge.
2. When the character's feet are at or just above the surface, press L or R (digital) with
   the stick held in the slide direction: sideways or diagonally down for a long slide,
   straight down for none.
3. The character lands in `LandingFallSpecial` and slides.

From below a platform, the earliest moment is when the bottom of the character's
environmental collision box (ECB) is above the platform; air dodging before that goes
through or past it.

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Landing lag | 10 frames (`LandingFallSpecial`) | [wiki:Landing_lag] |
| Normal landing, for comparison | 4 frames for most characters | [wiki:Landing_lag] |
| Air dodge speed/direction | set by the stick direction at the air dodge; neutral stick = no boost | [wiki:Air_dodge] |
| Slide length | air dodge horizontal speed, then traction (doubled above max walk speed in landing states) | [wiki:Wavedash] [wiki:Traction] |
| Air dodge intangibility | starts frame 4 (frame 3 for Bowser), so a waveland that lands within 3 frames has none | [wiki:Air_dodge] |
| Air dodge that misses the surface | full animation (49 frames for most) and helpless fall | [wiki:Air_dodge] |
| Characters whose kits rely on it | Luigi after short hop aerials; Marth after short hop fair; Dr. Mario after short hop bair | [wiki:Wavedash] |

Traction and jump squat tables are in [wavedash](wavedash.md). Platform heights per stage
are stage data and not in this file.

## Why it matters

- **Platform movement:** getting onto a platform with a normal jump means rising above it
  and falling back (slow). A waveland lands as soon as the feet clear it and can slide
  across or off the platform, which is how characters chase opponents on platforms
  ([tech-chase](tech-chase.md)) and move around Battlefield, Yoshi's Story, Dream Land and
  Fountain of Dreams.
- **Slide off for an edge cancel:** waveland toward a platform edge, fall off with no lag
  and act immediately (aerial, double jump).
- **Landing mixup:** from a jump, waveland back or forward to change where the character
  lands instead of falling in a straight line.
- **[Ledgedash](ledgedash.md):** a waveland onto the stage from a ledge double jump.
- **Set-up for [shield drop](shield-drop.md):** waveland onto a platform with the stick held
  sideways, then shield and roll the stick down.

## Common errors

- **Air dodge too early** (below the platform): the character air dodges under or through
  it and falls helpless.
- **Too late:** the character has risen well above the platform; the air dodge travels
  through the air first, landing late, or misses.
- **Stick neutral or down:** lands with no slide.
- **Slides off unintentionally:** too much horizontal speed near an edge.
- **Analog press:** no air dodge at all.
- Waveland where a normal 4-frame landing would have been faster.

## How to detect it in a training mode

- Pattern: an airborne state (`JumpF/B`, `JumpAerialF/B`, `Fall*`) -> `EscapeAir` for a few
  frames -> `LandingFallSpecial` [decomp], on a platform or the main stage.
- Metrics: frames spent in `EscapeAir` before landing (1-3 is tight), slide distance,
  which surface was landed on, total frames from jump input to first actionable frame.
- Edge cancel: `LandingFallSpecial` (or `LandingAir*`) ends early into `Fall` because the
  character left the surface.
- Failure: `EscapeAir` runs to completion into `FallSpecial`.

## Drill seeds

### Platform waveland course

- **id:** `waveland-platform-circuit`
- **Goal:** Fast, accurate wavelands onto each platform.
- **Player:** any
- **CPU:** none
- **Setup:** Battlefield. Targets light up in sequence: left platform, top, right, stage.
- **CPU behaviour:** None.
- **Success:** Reach each target platform in `LandingFallSpecial` with at most 3 frames of `EscapeAir`, within a time limit.
- **Fail:** Air dodge without landing, or over time.
- **Variations:** Yoshi's Story and Fountain of Dreams heights; require sliding off the far edge (edge cancel) into an aerial.
- **Data needed:** Platform positions, character jump heights.

### Waveland tech chase on platform

- **id:** `waveland-platform-followup`
- **Goal:** Follow a launched opponent onto a platform and punish their tech.
- **Player:** [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Marth](../characters/marth.md), [Captain Falcon](../characters/captain-falcon.md), [Sheik](../characters/sheik.md)
- **CPU:** any
- **Setup:** CPU launched upward so it lands on a side platform; player below.
- **CPU behaviour:** Random tech on the platform.
- **Success:** Player wavelands onto the platform and hits or grabs the CPU before it acts.
- **Fail:** CPU acts first.
- **Variations:** Top platform; CPU misses tech and slides off.
- **Data needed:** Tech data from [teching](teching.md), platform geometry.

### Aerial then waveland

- **id:** `waveland-after-short-hop-aerial`
- **Goal:** Short hop, aerial, then waveland to reposition before landing.
- **Player:** [Luigi](../characters/luigi.md), [Marth](../characters/marth.md), [Dr. Mario](../characters/dr-mario.md), [Samus](../characters/samus.md)
- **CPU:** any, shielding
- **Setup:** CPU shielding at mid range.
- **CPU behaviour:** Shield grabs after blocking.
- **Success:** Aerial hits the shield and the player wavelands out of grab range (or behind) before the grab.
- **Fail:** Grabbed, or aerial landed with lag.
- **Variations:** Waveland forward into grab.
- **Data needed:** Aerial IASA/total frames, short hop airtime.

## Sources

- SSBWiki: Wavedash (Wavelanding section), Air dodge, Landing lag, Traction, Edge getup
  (https://www.ssbwiki.com/Wavedash#Wavelanding).
- Melee Library: "Edge Cancels Part 1" (SSBM Tutorials and CDK) and "The Mechanics Behind
  Advanced Platform Tech" (Schmooblidon) are videos; only their descriptions were used.
- `[decomp]`: state names from this repository.
