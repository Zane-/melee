---
schema: melee-technique/v1
id: recovery
name: Recovery
aliases: [recovering, sweetspot, ledge sweetspot, recovery mixup, air dodge recovery, tether recovery]
category: recovery
difficulty: 3
related: [edgeguarding, ledge-options, di, meteor-cancel, wall-jump, wall-tech, fast-fall, ledgedash]
characters: all
summary: Returning to the stage after being knocked off, using drift, the double jump, special moves, the air dodge and the ledge, while giving the edgeguarder as little as possible to hit.
---

# Recovery

## What it is

After a launch offstage the character must get back to the stage or its ledge. Resources:

| Resource | Notes | Source |
|-|-|-|
| [DI](di.md) and drift | Decide the starting position; survival DI is the first step of every recovery | [wiki:Directional_influence] |
| Double jump | One (Jigglypuff and Kirby have five midair jumps [unverified]); lost if hit after using it, so it is the most valuable resource | [unverified] |
| Up B | Main recovery move for most; ends in helpless fall (`FallSpecial`) | [wiki:Recovery] |
| Side B / other specials | Fox/Falco side B, Captain Falcon down B (restores the double jump) and side B, Peach float and parasol, Mario cape, etc. | [wiki:Recovery] |
| Air dodge | A directional boost with intangibility; causes helplessness; cannot grab the ledge until the animation ends | [wiki:Air_dodge] |
| Tether | Link, Young Link (hookshot) and Samus (grapple) can latch onto walls with their air grab | [wiki:Wavedash] (mentions wall grappling), [unverified] for details |
| [Wall jump](wall-jump.md) | Eight characters; restores no jumps but gains height | [wiki:Wall_jump] |
| The ledge | Grabbing it gives intangibility and ends the recovery | [wiki:Edge] |

## Inputs

No fixed sequence. The components:

1. DI the launching hit (up and toward the stage for horizontal hits).
2. If [meteor smashed](meteor-cancel.md), jump or up B at the right time to cancel.
3. Drift toward the stage; choose when to double jump (early = high, late = low).
4. Use the recovery special so that it ends at the ledge **sweetspot**: the character's
   ledge-grab box reaches the ledge without the body rising above stage level.
5. Do not hold down when reaching for the ledge (down prevents the grab) [wiki:Edge].
6. From the ledge, choose a [ledge option](ledge-options.md).

## Frame data and formulas

| Fact | Value | Source |
|-|-|-|
| Air dodge total animation | 49 frames (48 for Mario, Dr. Mario, Luigi, Ice Climbers, Ness; 39 for Mewtwo) | [wiki:Air_dodge] |
| Air dodge intangibility | frames 4-29 (Bowser 3-29; Peach and Zelda 4-19) | [wiki:Air_dodge] |
| Ledge grab during air dodge | not until the animation is over | [wiki:Air_dodge] |
| Ledge grab direction | must face the ledge; exceptions include Captain Falcon's and Ganondorf's up B (which can grab backward but have a small forward sweetspot) and Donkey Kong's up B | [wiki:Edge] |
| Characters that depend on air dodge for vertical recovery | Jigglypuff, Yoshi, a solo Ice Climber (their up B gives no height) | [wiki:Air_dodge] |
| Ledge intangibility on grab | 37 frames (Link 33) | [wiki:Ledgedash] |
| Regrab lockout | 29 frames after letting go | [wiki:Ledgestall] |
| Tumble | cannot air dodge while tumbling; jump, attack or tap sideways first | [wiki:Tumbling] [wiki:Air_dodge] |
| Meteor cancel | from 8 frames after hitlag ends; 40-frame lockouts for early jump / up B presses | [wiki:Meteor_cancel] |
| Fast fall speeds | per character table in [fast-fall](fast-fall.md) | [wiki:Fastfall] |

Distances and startup of each character's recovery moves are character-specific and are in
the character files ("Recovery" and "Edgeguarding <Name>" sections) and the generated frame
data, not here.

### Mixup axes

- **Height:** high (land on stage or platform), ledge height, low (from below the ledge).
- **Timing:** immediate, delayed (stall with drift, float, or a second special).
- **Target:** ledge sweetspot, on-stage landing, platform.
- **Resource order:** jump then up B, up B first keeping the jump, side B instead.
- **After being hit:** [wall tech](wall-tech.md) stage spikes, then wall jump if available.

## Why it matters

A stock ends at the edge more often than at high percent. A character's recovery range sets
how far it can chase offstage, and its predictability sets how early it dies. For a training
mode, recovery matters in two roles: the player practising sweetspots and mixups under
pressure, and the CPU performing realistic recoveries so the player can practise
[edgeguarding](edgeguarding.md).

## Common errors

- Double jumping immediately and predictably, then being hit and left with only up B.
- Up B started too high: the body rises above the ledge and is hit before grabbing.
- Up B started too low or too far: falls short (SD).
- Holding down (fast fall) into the ledge and not grabbing it.
- Recovering to the ledge every time against a prepared edgehog, or to the stage every
  time against a waiting smash.
- Air dodging toward the stage and landing with lag in front of the opponent, or air
  dodging offstage into helplessness.
- Missing the [meteor cancel](meteor-cancel.md) by mashing (lockout).
- Bad DI on the hit that started it (see [di](di.md)).

## How to detect it in a training mode

- Success: player reaches `CliffCatch`, or a grounded actionable state on stage, without
  taking a hit; optionally "sweetspot" = `CliffCatch` reached while the character's top
  never rose above stage level during the up B.
- Failure: KO, or hit during the recovery or its landing lag (`LandingFallSpecial`).
- Useful logged values: position when the double jump was used, position and frame of the
  up B start, whether the ledge was grabbed on the first possible frame, stick Y on the
  frames near the ledge (holding down?).
- CPU recovery scripts need per-character logic; a simple model is "drift toward the ledge;
  if below height H, double jump; if within up B range R, up B aimed at the ledge", with
  randomised H and aim, plus character specials.

## Drill seeds

### Sweetspot the ledge

- **id:** `recovery-sweetspot-upb`
- **Goal:** Reach the ledge with up B without exposing the body above the stage.
- **Player:** [Marth](../characters/marth.md), [Fox](../characters/fox.md), [Falco](../characters/falco.md), [Sheik](../characters/sheik.md), [Captain Falcon](../characters/captain-falcon.md), [Dr. Mario](../characters/dr-mario.md), [Mario](../characters/mario.md), any
- **CPU:** [Marth](../characters/marth.md) or [Sheik](../characters/sheik.md) as edgeguarder
- **Setup:** Player placed offstage at a random position within up B range, no double jump.
- **CPU behaviour:** Stands at the edge and uses a ledge-covering move (dtilt, fsmash, ftilt) on a timer.
- **Success:** `CliffCatch` without being hit.
- **Fail:** Hit, landed on stage in lag and hit, or SD.
- **Variations:** With double jump; CPU edgehogs instead (player must go to stage); different stages (wall shapes).
- **Data needed:** Up B travel, ledge-grab box, stage ledge coordinates.

### Recovery mixup versus a reacting opponent

- **id:** `recovery-mixup-vs-coverage`
- **Goal:** Choose high, ledge or low according to what the edgeguarder commits to.
- **Player:** any
- **CPU:** any
- **Setup:** Player offstage with all resources at mid percent.
- **CPU behaviour:** Randomly: grabs the ledge early, waits at the edge to hit, or jumps out to intercept.
- **Success:** Player back on stage or ledge unharmed.
- **Fail:** Hit or KO.
- **Variations:** Remove the double jump; add a second hit at the start that must be DI'd.
- **Data needed:** Both characters' move data.

### Survive, then recover

- **id:** `recovery-di-then-return`
- **Goal:** Chain survival DI, optional meteor cancel/wall tech, and the recovery.
- **Player:** any
- **CPU:** [Marth](../characters/marth.md), [Fox](../characters/fox.md), [Falco](../characters/falco.md)
- **Setup:** Player near the edge at kill percent.
- **CPU behaviour:** Lands a kill move, then edgeguards with a simple script.
- **Success:** Player returns.
- **Fail:** KO.
- **Variations:** Percent; kill move pool.
- **Data needed:** Knockback data, blast zones.

## Sources

- SSBWiki: Recovery (Melee list), Air dodge (Melee section and table), Edge, Tumbling,
  Meteor cancel, Ledgedash, Ledgestall, Wall jump, Fast fall, Directional influence
  (https://www.ssbwiki.com/Recovery).
- Items tagged `[unverified]` are widely known facts not re-read in this session.
