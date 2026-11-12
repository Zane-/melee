---
schema: melee-technique/v1
id: edgeguarding
name: Edgeguarding
aliases: [edge guard, edgeguard, edgehog, ledgehog, gimp, ledge trap, spike, semi-spike, wall of pain]
category: punish
difficulty: 4
related: [recovery, ledge-options, ledgedash, meteor-cancel, wall-tech, wavedash, di, hitstun-knockback]
characters: all
summary: Stopping an offstage opponent from returning, by hitting them again, taking the ledge so they cannot grab it, or covering the spot where they must land.
---

# Edgeguarding

## What it is

When a character is knocked offstage they must spend their double jump and recovery move to
return ([recovery](recovery.md)). Edgeguarding is everything the onstage player does to make
that fail. The three tools:

1. **Hit them** offstage or as they arrive: aerials, projectiles, spikes, or a move at the
   ledge.
2. **Edgehog:** hold the ledge so they cannot grab it. Only one character can hang on a
   ledge at a time [wiki:Edge-hogging].
3. **Cover the landing:** if they must land on stage (because the ledge is taken or the
   recovery goes high), punish the landing lag.

## Inputs

- **Fast edgehog:** stand near the edge facing the stage centre and
  [wavedash](wavedash.md) backward so the character slides off and grabs the ledge
  immediately; this is the most common method in competitive play [wiki:Edge-hogging].
  Alternatives: run off and [fast fall](fast-fall.md) to the ledge facing it, or drop from
  a short hop.
- **Hold the ledge through their up B:** time the grab so ledge intangibility covers the
  moment their up B hitbox passes, or use the ledge roll, which occupies the ledge for its
  whole animation while intangible ([ledge-options](ledge-options.md)).
- **Offstage hit:** run off or jump out, aerial, then double jump/up B back.
- **From the ledge:** let go, aerial, double jump back to the ledge ("ledgehop" edgeguard),
  or drop and regrab.

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Ledge intangibility | 37 frames from the grab (Link 33) | [wiki:Ledgedash] |
| Regrab lockout after letting go | 29 frames | [wiki:Ledgestall] |
| Air dodge landing lag (wavedash to ledge is a slide off the edge during it) | 10 frames | [wiki:Landing_lag] |
| Meteor smash angle range (can be [meteor cancelled](meteor-cancel.md)) | 260-280 degrees | [wiki:Spike] |
| "Spike" in Melee jargon | downward hit outside that range, e.g. 290 degrees: cannot be meteor cancelled | [wiki:Spike] |
| Stage-spike / wall bounce | bouncing off a wall removes 20% of speed; the victim can [wall tech](wall-tech.md) it | [wiki:Knockback] [wiki:Tech] |
| Fox dair angle | 290 (not meteor-cancellable); Falco dair is the classic spike | [web:fightcore.gg] (Fox dair angle), [wiki:Edge-guarding] |
| Ledge roll below 100% (sampled characters) | 49-50 frames, intangible about 1-27 to 1-39 | [wiki:Fox_(SSBM)/Edge_getups_(fast)] and sibling pages |

Characters and tools the wiki highlights for Melee [wiki:Edge-guarding]:

- [Falco](../characters/falco.md): dair spikes for the whole move; nair and bair are fast
  and long-lasting; lasers interrupt recoveries; dsmash is a fast semi-spike.
- [Fox](../characters/fox.md): down B (shine) has no startup and sends at a low angle
  (semi-spike), "shine spike"; bair.
- [Marth](../characters/marth.md): dair spike, dtilt (disjointed semi-spike), fair.
- [Jigglypuff](../characters/jigglypuff.md): chains of bair carrying the opponent offstage
  ("wall of pain"); nair and fair linger.
- [Pikachu](../characters/pikachu.md): uair weak semi-spike chains, bair, neutral B.

General knowledge (no number attached): [Sheik](../characters/sheik.md) edgeguards with
bair/fair and needles and by grabbing the ledge against up B recoveries;
[Peach](../characters/peach.md) with turnips and floating aerials;
[Captain Falcon](../characters/captain-falcon.md) with bair, uair and knee;
[Ganondorf](../characters/ganondorf.md) with uair (reverse hit) and fair.

## Why it matters

Kills from on-stage hits need high percent; a successful edgeguard kills at any percent.
Characters with short or linear recoveries (Fox, Falco, Captain Falcon, Marth, Ganondorf,
Dr. Mario, Roy) lose most stocks this way. Edgeguard drills are also the most natural
"CPU does a recovery, player must stop it" scenarios; the character files list each
character's recovery options under "Edgeguarding <Name>".

## Common errors

- Grabbing the ledge too early: intangibility runs out before the opponent's up B arrives
  and the edgehogger is hit off the ledge.
- Grabbing too late: the opponent already has the ledge, or sweetspots first.
- Standing at the edge and missing a move with long lag, letting the opponent land.
- Hitting the opponent upward or toward the stage, giving them their recovery back
  (some up Bs can be used again after being hit).
- Going out too deep and being unable to return; or being hit by the recovery move's
  hitbox ([Marth](../characters/marth.md) up B, [Fox](../characters/fox.md) up B).
- Not covering the opponent's high option when holding the ledge (they land on stage).
- Hitting them into the stage wall where they [wall tech](wall-tech.md).

## How to detect it in a training mode

- Scenario start: CPU in tumble or free fall offstage with a defined set of resources
  (double jump yes/no, percent, position).
- Success: CPU is KO'd (crosses a blast zone) without first returning to a grounded,
  actionable state on stage or to `CliffWait`.
- Partial success: CPU lands on stage but is hit during landing lag
  (`LandingFallSpecial` or special-move landing).
- Edgehog check: player is in `CliffCatch`/`CliffWait`/`CliffEscape*`/`CliffClimb*`
  (ledge occupied) on the frame the CPU's ledge-grab box overlaps the ledge.
- Fail: CPU reaches `CliffWait` or stands on stage unpunished; or the player is KO'd.

## Drill seeds

### Edgehog a predictable up B

- **id:** `edgeguarding-wavedash-edgehog`
- **Goal:** Take the ledge in time and keep it.
- **Player:** any
- **CPU:** [Marth](../characters/marth.md), [Captain Falcon](../characters/captain-falcon.md), [Ganondorf](../characters/ganondorf.md), [Dr. Mario](../characters/dr-mario.md), [Roy](../characters/roy.md)
- **Setup:** CPU launched offstage low with no double jump; player at centre stage.
- **CPU behaviour:** Drifts in and up Bs to the ledge.
- **Success:** CPU KO'd; player not hit.
- **Fail:** CPU grabs the ledge or lands unpunished.
- **Variations:** CPU has its double jump; CPU mixes going high; player starts farther away.
- **Data needed:** CPU up B distance/timing, ledge intangibility, wavedash distance.

### Spacie recovery coverage

- **id:** `edgeguarding-vs-fox-falco`
- **Goal:** Cover side B to ledge, side B to stage, and up B at several angles.
- **Player:** [Marth](../characters/marth.md), [Sheik](../characters/sheik.md), [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Peach](../characters/peach.md), [Captain Falcon](../characters/captain-falcon.md), [Jigglypuff](../characters/jigglypuff.md)
- **CPU:** [Fox](../characters/fox.md), [Falco](../characters/falco.md)
- **Setup:** CPU offstage at ledge height or below, with or without double jump.
- **CPU behaviour:** Random: side B at ledge height, side B onto stage, up B angled to ledge, up B high, double jump then mix; optional shortened side B.
- **Success:** CPU KO'd.
- **Fail:** CPU returns.
- **Variations:** Start distance; stage (wall shape matters for wall techs); CPU techs stage spikes.
- **Data needed:** Fox/Falco side B and up B distances and startup; character file sections.

### Offstage spike with return

- **id:** `edgeguarding-offstage-dair`
- **Goal:** Land a spike or strong aerial offstage and make it back.
- **Player:** [Falco](../characters/falco.md), [Marth](../characters/marth.md), [Captain Falcon](../characters/captain-falcon.md), [Ganondorf](../characters/ganondorf.md)
- **CPU:** any
- **Setup:** CPU recovering from mid distance with double jump used.
- **CPU behaviour:** Recovers on a set path; meteor cancels meteors when possible.
- **Success:** CPU KO'd and the player returns to stage or ledge.
- **Fail:** Miss, or the player dies too.
- **Variations:** CPU percent (low percent spikes are survivable); meteor vs spike.
- **Data needed:** Move angles, player recovery distance, [meteor-cancel](meteor-cancel.md) rules.

## Sources

- SSBWiki: Edgeguarding, Edgehogging, Spike, Meteor smash, Knockback, Ledgedash, Ledgestall,
  per-character Edge getups pages (https://www.ssbwiki.com/Edge-guarding).
- FightCore (https://www.fightcore.gg/) for Fox's dair angle.
- Statements marked as general knowledge carry no numbers and come from standard community
  practice rather than a page read in this session.
