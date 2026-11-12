---
schema: melee-technique/v1
id: meteor-cancel
name: Meteor cancel
aliases: [meteor cancelling, MC, meteor smash, spike, meteor recovery]
category: recovery
difficulty: 3
related: [recovery, edgeguarding, di, hitstun-knockback, wall-tech]
characters: all
summary: After being hit downward by a meteor smash, a jump or up B input made once the cancel window opens stops the knockback immediately; spikes outside the meteor angle range cannot be cancelled.
---

# Meteor cancel

## What it is

Hitboxes whose launch angle is between 260 and 280 degrees are flagged by the game as
**meteor smashes**. A character hit by one can end the downward knockback early by using a
double jump or an up B shortly after the hit: the knockback stops, with a distinct sound and
a white flash, and the jump or up B proceeds normally. Downward hits with angles outside
that range (for example 290 degrees) are not meteors and cannot be cancelled; the Melee
community calls those **spikes** [wiki:Meteor_cancel] [wiki:Spike].

## Inputs

1. Get hit by a meteor smash.
2. Wait for the cancel window to open (see below), then press jump (X/Y or tap up) if a
   double jump remains, or up + B.
3. Do not press early: an early press starts a lockout for that input type.

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Meteor angle range | 260-280 degrees | [wiki:Spike] |
| Window opens | 8 frames after hitlag ends | [wiki:Meteor_cancel] |
| Jump lockout | any jump input starts a 40-frame period during which a double jump cannot meteor cancel; this applies even to inputs made before the hit | [wiki:Meteor_cancel] |
| Up B lockout | same, 40 frames, for up B inputs; independent of the jump lockout | [wiki:Meteor_cancel] |
| Overlap | an up B input done with tap jump is often also a jump input and starts both lockouts | [wiki:Meteor_cancel] |
| Knockback state required | none: in Melee it works whether or not the hit caused tumble | [wiki:Meteor_cancel] |
| Grounded victims | a meteor on a grounded victim bounces them up (if it tumbles); they can meteor cancel only if they then bounce off a ceiling and are travelling downward | [wiki:Meteor_cancel] [wiki:Meteor_smash] |
| Floor bounce | removes 20% of vertical speed; hitstun unchanged | [wiki:Knockback] |
| Kirby and Jigglypuff | if they have already used at least one midair jump, holding the jump button buffers a perfect meteor cancel when the window opens | [wiki:Meteor_cancel] |

Whether "8 frames after hitlag ends" means the first usable frame is the 8th or the 9th
frame of knockback is not specified by the source; test in engine. Evsen's "Mechanics of
Meteor Canceling" (Reddit, in the Melee Library) is the detailed reference and could not be
fetched.

Downward hitboxes on normal moves, from the frame data dump [fd] (specials other than
those listed are not covered by the dump):

| Type | Moves (hitbox angle) |
|-|-|
| Spike, not cancellable (outside 260-280) | Falco dair (290), Fox dair (290), Marth dair (290), one hitbox of Captain Falcon dair (290) |
| Meteor, cancellable (270) | Captain Falcon dair (main hitbox), Donkey Kong fair and dair, Ganondorf dair, Ice Climbers fair, Jigglypuff dair, Kirby dair, Luigi dair, Mewtwo dair, Mr. Game & Watch dair, Ness dair, Roy dair, Samus dair and utilt, Yoshi fair and dair, Young Link dair, Peach dtilt, Zelda dtilt, Marth side B third hit (down) |
| Meteor, cancellable (other angles in range) | Mario fair (280), Link dtilt (280), Young Link dtilt (280), Zelda dair (275) |

Dr. Mario's and Roy's usmash have a 259-degree hitbox [fd], just outside the range. Fox's
dair angle is confirmed by FightCore [web:fightcore.gg]. Many of these hitboxes are only
part of the move (sweetspots or specific frames); see the generated frame data for each
character.

## Why it matters

- It decides whether a downward hit offstage kills. Against true meteors
  ([Captain Falcon](../characters/captain-falcon.md) dair,
  [Ganondorf](../characters/ganondorf.md) dair, [Donkey Kong](../characters/donkey-kong.md)
  fair, [Mario](../characters/mario.md) fair and the others in the table) a good meteor
  cancel at low and mid percent means survival, so
  edgeguarders prefer spikes or hit again after the cancel.
- The 40-frame lockouts punish mashing: a player who mashes jump while being comboed
  offstage cannot cancel.
- A meteor-cancelling double jump is used up; the recovery afterward has only up B
  (and vice versa).

## Common errors

- Pressing during hitlag or the first frames after it, then again: the first press starts
  the lockout and the second is ignored. In game: no flash, the character keeps falling.
- Mashing jump and up B together with tap jump, locking both.
- Jumping when no double jump remains instead of using up B.
- Trying to cancel a spike (non-meteor): impossible; the right response is DI and, near the
  stage, a [wall tech](wall-tech.md).
- Cancelling with the jump and then being hit again with no jump left.

## How to detect it in a training mode

- Meteor hit: victim in a `Damage*`/`DamageFly*` state from a hitbox with angle 260-280.
- Success: victim's state changes to `JumpAerialF/B` or the up special state while hitstun
  would otherwise still be running; the game plays the meteor-cancel effect.
- Feedback: frame of the first jump / up B press relative to the end of hitlag
  ("pressed on frame N; window opens after frame 8"), and whether a lockout was active
  (a press of the same type within the previous 40 frames).
- Fail: victim crosses the bottom blast zone or stays in knockback past the window.

## Drill seeds

### Meteor cancel timing

- **id:** `meteor-cancel-timing`
- **Goal:** Cancel on the first possible frame with a single press.
- **Player:** any
- **CPU:** [Captain Falcon](../characters/captain-falcon.md), [Ganondorf](../characters/ganondorf.md), [Mario](../characters/mario.md) or any character with a 260-280 degree aerial
- **Setup:** Player airborne just offstage at low/mid percent with double jump available.
- **CPU behaviour:** Lands its meteor aerial.
- **Success:** Meteor cancel within N frames of the window opening, then return to the ledge or stage.
- **Fail:** No cancel (report early press / lockout / late), or KO.
- **Variations:** Up B only (no double jump); higher percent; second hit after the cancel.
- **Data needed:** Meteor move angle and damage (for hitlag), window rule above.

### Meteor or spike recognition

- **id:** `meteor-cancel-vs-spike-recognition`
- **Goal:** Respond correctly to cancellable and non-cancellable downward hits.
- **Player:** any
- **CPU:** mixed pool, e.g. [Falco](../characters/falco.md) dair and [Marth](../characters/marth.md) dair (spikes), [Ganondorf](../characters/ganondorf.md) dair and [Captain Falcon](../characters/captain-falcon.md) dair (meteors)
- **Setup:** Player near the ledge, airborne.
- **CPU behaviour:** Random downward aerial from the pool.
- **Success:** Meteor: cancel and recover. Spike: correct DI and wall tech if in reach, then recover if possible.
- **Fail:** KO where survival was possible.
- **Variations:** Stage walls (Battlefield, Yoshi's Story, Final Destination).
- **Data needed:** Angles of each move from the frame data dump.

## Sources

- SSBWiki: Meteor cancel, Meteor smash, Spike, Knockback
  (https://www.ssbwiki.com/Meteor_cancel).
- FightCore (https://www.fightcore.gg/characters/224/fox) for Fox's dair angle.
- Melee Library: "Mechanics of Meteor Canceling" (Evsen, Reddit) listed; not fetchable in
  this session.
- `[fd]`: project frame data dump (hitbox angles). `[decomp]`: state names from this
  repository.
