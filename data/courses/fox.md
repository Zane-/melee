---
schema: melee-course/v1
id: fox
character: fox
status: draft
summary: From executing shine cleanly to winning the opening, converting it into a stock and getting out of the combos Fox is caught in.
includes: [universal]
---

# Fox course

Curriculum approved by the owner 2026-11-12 (with the Tech order below). Every drill is
`planned` except where the Status column says otherwise.
Format: [`README.md`](README.md). Knowledge: [`../characters/fox.md`](../characters/fox.md).

How the parts connect for Fox: **Tech** makes shine, wavedash and the aerials automatic.
**Punish** turns the three openings Fox gets most (a shielded move, a grab, a landed aerial
or shine) into up smash, up air or an edgeguard. **Defense** covers what kills Fox: chain
grabs, tech chases, crouch-cancel punishes and being edgeguarded. **Neutral** then asks the
player to earn the opening against an opponent that commits, and hands over to the punish
drill that starts from it.

`fox-shine-oos` runs on the engine; it is the Shine OoS event
(`src/tmce/events/shineoos/`) moved over, and reuses that event's scenario deck.

## Tech

Fundamentals first (including shield drop), then everything built on shine, with the ledge
and movement extras between. Jump-cancelling shine is learned inside the waveshine drill at
a loose tolerance; the frame-perfect version comes later, directly before multishine, which
is the same input repeated (owner's order, 2026-11-12).

| # | id | Drill | Goal | CPU | Requires | Leads to | Knowledge | Status |
|-|-|-|-|-|-|-|-|-|
| 1 | `universal-short-hop` | Short hop | Leave the ground with a short hop every time | none | - | `universal-shffl` | [short hop](../techniques/short-hop.md) | implemented: `drills/tech_short_hop.inc.h`; simulator and Dolphin specs pass (2026-11-12). Press length shown in the verdict |
| 2 | `universal-l-cancel` | L-cancel | Halve landing lag on every aerial, whiffed, hit or shielded | passive target | - | `universal-shffl` | [L-cancel](../techniques/l-cancel.md) | implemented: `drills/tech_movement.inc.h`; simulator and Dolphin specs pass (2026-11-12). Demonstration fails for Kirby and Sheik |
| 3 | `universal-shffl` | SHFFL | Short hop, aerial, fast fall, L-cancel as one motion, with per-component feedback | passive target | 1, 2 | `fox-shffl-nair-shine` | [SHFFL](../techniques/shffl.md), [fast fall](../techniques/fast-fall.md) | implemented: `drills/tech_movement.inc.h`; simulator and Dolphin specs pass (2026-11-12). Demonstration fails for Kirby, Sheik, Mr. Game & Watch |
| 4 | `universal-wavedash` | Wavedash | Air dodge into the ground on the first airborne frame, at a chosen length | none | - | `fox-waveshine` | [wavedash](../techniques/wavedash.md) | implemented: `drills/tech_wavedash.inc.h`; simulator and Dolphin specs pass (2026-11-12). Chosen length / angle not built |
| 5 | `universal-dash-dance` | Dash dance and pivot | Controlled dash lengths and turnarounds | none | - | neutral part | [dash dance](../techniques/dash-dance.md), [pivot](../techniques/pivot.md) | implemented: `drills/tech_movement.inc.h`; simulator and Dolphin specs pass (2026-11-12); demonstration passes for all 26 characters |
| 6 | `universal-jc-grab` | Jump-cancel grab and up smash | Standing grab and up smash out of a run | passive target | - | `fox-uthrow-uair` | [jump cancel](../techniques/jump-cancel.md) | implemented: `drills/tech_movement.inc.h`; simulator and Dolphin specs pass (2026-11-12); demonstration passes for all 26 characters |
| 7 | `universal-shield-drop` | Shield drop (Axe method) | Drop through a platform from shield: hold the stick fully left or right in shield, then roll it down to the diagonal notch; then into an aerial | none | - | defense part | [shield drop](../techniques/shield-drop.md) | implemented on Battlefield's left platform: `drills/tech_ledge.inc.h`; simulator and Dolphin specs pass (2026-11-12) |
| 8 | `fox-waveshine` | Waveshine | Shine, jump out of it, wavedash; the jump may come a few frames late at first | passive target | 4 | `fox-waveshine-usmash` | [tech](../characters/fox.md#waveshine) | implemented without a target: `drills/fox_shine_tech.inc.h`; simulator and Dolphin specs pass (2026-11-12). Passive target not built |
| 9 | `fox-shine-grab` | Shine-grab | Shine, jump-cancel, grab before the target can act | passive target, shielding | 6, 8 | `fox-shield-pressure` | [tech](../characters/fox.md#shine-grab) | implemented on a shielding Marth: `drills/fox_pressure.inc.h`; simulator and Dolphin specs pass (2026-11-12) |
| 10 | `fox-shffl-nair-shine` | Aerial into shine | SHFFL nair or dair into shine on hit and on shield | passive target, standing or shielding | 3, 8 | `fox-shield-pressure` | [tech](../characters/fox.md#drill-shine-shield-pressure) | implemented on a shielding Marth: `drills/fox_pressure.inc.h`; simulator and Dolphin specs pass (2026-11-12). Reports the gap the opponent had |
| 11 | `universal-ledgedash` | Ledgedash | Ledge drop, jump, air dodge onto the stage with intangibility left | none | 4 | `fox-ledgedash-attack` | [ledgedash](../techniques/ledgedash.md), [seed](../characters/fox.md#ledgedash-with-intangibility) | implemented on Final Destination's left ledge: `drills/tech_ledge.inc.h`; simulator and Dolphin specs pass (2026-11-12). Fox only checked |
| 12 | `fox-jc-shine` | Frame-perfect jump-cancelled shine | Jump out of shine on the first possible frame, every time | none | 8 | `fox-multishine` | [tech](../characters/fox.md#jump-cancelled-shine) | implemented: `drills/fox_shine_tech.inc.h`; simulator and Dolphin specs pass (2026-11-12) |
| 13 | `fox-multishine` | Multishine | Consecutive frame-perfect shines; count and gap shown | none, then shield | 12 | `fox-shield-pressure` | [tech](../characters/fox.md#multishine) | implemented without a shield: `drills/fox_shine_tech.inc.h`; simulator and Dolphin specs pass (2026-11-12). On-shield variant not built |
| 14 | `fox-shdl` | Short hop double laser | Two lasers in one short hop, landing actionable | none | 1 | neutral part | [tech](../characters/fox.md#short-hop-double-laser) | implemented: `drills/fox_specials.inc.h`; simulator and Dolphin specs pass (2026-11-12) |
| 15 | `fox-ledge-stall` | Firefox ledge stall | Refresh ledge intangibility with the stall | none | - | defense part | [tech](../characters/fox.md#firefox-ledge-stall) | implemented: `drills/tech_ledge.inc.h`; simulator and Dolphin specs pass (2026-11-12) |
| 16 | `fox-illusion-shorten` | Shortened Illusion | Stop Illusion at each of its lengths | none | - | `fox-recovery-mixup` | [tech](../characters/fox.md#shortened-illusion) | implemented on the ground, any shortening counts: `drills/fox_specials.inc.h`; simulator and Dolphin specs pass (2026-11-12). Recovery (offstage) variant not built |

TM-CE already has events for some of these (wavedash, L-cancel, ledgedash, legacy
Multishine, shield drop). Each is either re-expressed on the engine or kept as is behind the
same hub row; decided per drill when it is specified.

## Punish

From the three openings: a move on Fox's shield, a grab, a landed hit or shine.

| # | id | Drill | Goal | CPU | Requires | Leads to | Knowledge | Status |
|-|-|-|-|-|-|-|-|-|
| 1 | `fox-shine-oos` | Shine out of shield | Punish a shielded move with a frame 4 shine | deck: Marth, Sheik, Peach, Falcon, Falco, Jigglypuff attacks | `fox-waveshine` | `fox-waveshine-usmash` | [seed](../characters/fox.md#shine-out-of-shield-punish), [OoS](../techniques/out-of-shield.md) | implemented: `src/tmce/events/course/drills/fox_shine_oos.inc.h`; 9 specs pass in the simulator, 1 confirmed in Dolphin (2026-11-12). No full spec section or guide yet |
| 2 | `fox-oos-choice` | Pick the out-of-shield option | Choose shine, grab, nair, up smash or wavedash by spacing and advantage | deck, mixed spacings | 1 | - | [OoS](../techniques/out-of-shield.md) | implemented: `drills/fox_punish.inc.h`; the Shine OoS scenarios from 0, 4 or 8 units farther; any hit or grab before the CPU has recovered and reacted (4 frames) counts, and the verdict names the option. Simulator specs pass (2026-11-12). It does not judge whether the option was the best one |
| 3 | `fox-waveshine-usmash` | Waveshine to up smash | Shine a grounded opponent and up smash before they act | characters that slide from shine | `fox-waveshine` | - | [seed](../characters/fox.md#waveshine-to-up-smash) | implemented on Marth: `drills/fox_punish.inc.h`; he shields as soon as he can. Simulator specs pass (2026-11-12). Marth slides 44 units, so only a near-flat wavedash reaches; no other characters |
| 4 | `fox-shine-knockdown` | Shine knockdown: jab reset or tech chase | React to tech in place, tech away, tech in or no tech after shine | characters that fall from shine; random tech | 3 | - | [seed](../characters/fox.md#jab-reset-or-tech-chase-after-shine), [tech chase](../techniques/tech-chase.md) | planned |
| 5 | `fox-uthrow-uair` | Up throw up air | Land up air after up throw against DI and SDI | floaties and mid-weights; random DI, SDI at a set tolerance | `universal-jc-grab` | - | [seed](../characters/fox.md#up-throw-up-air-against-sdi) | implemented: `drills/fox_punish_throws.inc.h`; Marth, Sheik, Peach, Jigglypuff at 90%, random DI, the CPU jumps away after a reaction time (option). Simulator specs pass (2026-11-12). No SDI |
| 6 | `fox-uthrow-chaingrab` | Chain grab fastfallers | Regrab Fox and Falco out of up throw through their DI | Fox, Falco; random DI, jump or shine out when possible | `universal-jc-grab` | - | [seed](../characters/fox.md#chain-grab-fastfallers) | implemented: `drills/fox_punish_throws.inc.h`; Falco and Fox, random DI, the CPU jumps on its first free frame. Simulator specs pass (2026-11-12). No shine out |
| 7 | `fox-aerial-confirm` | Aerial hit confirm | After a landed nair or dair, pick shine, grab or up smash by percent and whether they crouch cancelled | deck; random crouch cancel / ASDI down | `fox-shffl-nair-shine` | 3, 5 | [neutral](../characters/fox.md#neutral-game), [crouch cancel](../techniques/crouch-cancel.md) | planned |
| 8 | `fox-shield-pressure` | Shield pressure | Keep the gaps too small for shield grab and the opponent's fastest out-of-shield option | shielding CPU that takes any gap it is given | `fox-shffl-nair-shine`, `fox-shine-grab` | - | [seed](../characters/fox.md#shield-pressure-against-shield-grab), [pressure](../techniques/shield-pressure.md) | implemented on Marth: `drills/fox_punish.inc.h`; he tries to grab out of shield whenever free. Simulator specs pass (2026-11-12). Only the grab, not his other out-of-shield options |
| 9 | `fox-shine-spike` | Shine spike | Take the stock offstage with shine and make it back | recovering Marth, Sheik, Falcon, Peach; random recovery choice | `fox-waveshine` | - | [seed](../characters/fox.md#shine-spike-the-recovery), [edgeguarding](../techniques/edgeguarding.md) | planned |
| 10 | `fox-edgeguard-onstage` | Edgeguard from the stage | Cover the recovery with bair, down smash or ledge grab timing | recovering spacies and Marth; random recovery choice | - | - | [edgeguarding](../techniques/edgeguarding.md), [kill options](../characters/fox.md#kill-options) | planned |
| 11 | `fox-kill-confirm` | Kill confirms | Up throw up air, dash attack or up tilt into up smash at kill percent | deck by weight class; random DI | 5 | - | [punish game](../characters/fox.md#punish-game), [kill options](../characters/fox.md#kill-options) | implemented: `drills/fox_punish_throws.inc.h`; Marth, Sheik, Jigglypuff at 110%; the opener must be a grab, shine, up tilt or dash attack, and the stock must go. Failure specs pass in the simulator (2026-11-12); a kill was seen once during development (Marth at 150%, up throw up air) but there is no spec for one and no demonstration |

## Defense

What Fox is caught in most, from the other side. The CPU performs the real sequence.

| # | id | Drill | Goal | CPU | Requires | Leads to | Knowledge | Status |
|-|-|-|-|-|-|-|-|-|
| 1 | `universal-tech` | Tech the ground | Tech in place, in and away on demand; see the lockout | hits the player into the floor | - | 5 | [teching](../techniques/teching.md) | planned |
| 2 | `universal-asdi-down` | ASDI down and crouch cancel | Hold the ground through weak hits and punish; recognise the percent where it stops | Marth, Sheik, Fox pokes at rising percent | - | - | [ASDI](../techniques/asdi.md), [crouch cancel](../techniques/crouch-cancel.md) | planned |
| 3 | `universal-di-survival` | Survival and combo DI | DI the kill move to live and the combo starter to escape | kill moves and throws by character | - | - | [DI](../techniques/di.md) | planned |
| 4 | `universal-sdi` | SDI multi-hits | SDI out of drill, up air, down smash | Fox dair and up throw up air, Peach down smash | - | - | [SDI](../techniques/sdi.md) | planned |
| 5 | `fox-escape-techchase` | Escape the tech chase | Mix tech options and act on the first free frame against Sheik and Falcon | Sheik down throw, Falcon down and up throw; reacts at a set speed | 1 | - | [dummy](../characters/fox.md#as-the-training-dummy), [Sheik](../characters/sheik.md), [Falcon](../characters/captain-falcon.md) | planned |
| 6 | `fox-escape-chaingrab` | Escape Marth's chain grab | Use the DI that ends the chain earliest, then shine or jump out | Marth up throw regrabs, pivot tipper at the end | 3 | - | [dummy](../characters/fox.md#as-the-training-dummy), [Marth](../characters/marth.md) | planned |
| 7 | `fox-escape-pressure` | Escape shield pressure | Find the gap in Falco's and Fox's pressure: shine, grab, roll or wavedash out | Falco pillar, Fox drill shine; gaps at a set tolerance | `fox-shine-oos` | - | [defense](../characters/fox.md#defense-and-out-of-shield), [Falco](../characters/falco.md) | planned |
| 8 | `fox-combo-shine` | Shine out of combos | Shine on the first actionable frame after hitstun | strings with a real gap; frame count shown | - | - | [defense](../characters/fox.md#defense-and-out-of-shield) | planned |
| 9 | `universal-wall-tech` | Wall and ledge tech | Tech the stage when hit while recovering | Marth, Sheik hits at the ledge | 1 | 10 | [wall tech](../techniques/wall-tech.md), [Amsah tech](../techniques/amsah-tech.md) | planned |
| 10 | `fox-recovery-mixup` | Recover against an edgeguard | Choose Illusion length, Firefox angle, air dodge or ledge sweetspot against a CPU covering options | Marth, Sheik, Fox edgeguarding; coverage at a set skill | `fox-illusion-shorten` | - | [seed](../characters/fox.md#recovery-mixups-against-an-edgeguarder), [recovery](../characters/fox.md#recovery) | planned |
| 11 | `fox-ledgedash-attack` | Get off the ledge | Ledgedash, ledge stall or ledge option against a CPU waiting at the ledge | opponent covering ledge options | `universal-ledgedash` | - | [ledge options](../techniques/ledge-options.md), [seed](../characters/fox.md#ledgedash-with-intangibility) | planned |

## Neutral

Each drill ends at the opening and names the punish drill that continues from it. The CPU
commits to one of a few realistic options after a reaction delay; the delay is the
difficulty.

| # | id | Drill | Goal | CPU | Requires | Leads to | Knowledge | Status |
|-|-|-|-|-|-|-|-|-|
| 1 | `fox-whiff-punish` | Whiff punish | Dash dance outside the move's range, then grab or up smash its recovery | Marth fsmash, dtilt, fair; Sheik ftilt; Peach dash attack | `universal-dash-dance`, `universal-jc-grab` | `fox-uthrow-uair`, `fox-uthrow-chaingrab` | [neutral](../characters/fox.md#neutral-game), [dash dance](../techniques/dash-dance.md) | implemented: `drills/fox_neutral.inc.h`, scenarios in `desc.c` (Marth forward smash and dash attack, Sheik and Peach dash attack); simulator and Dolphin specs pass (2026-11-12). The CPU attacks once the player has been in its reach for its reaction time. Marth down tilt and fair, Sheik ftilt not built |
| 2 | `fox-wavedash-back-punish` | Wavedash back punish | Wavedash out of an approach's range and punish its landing | Falcon nair, Falco dair, Sheik dash attack | `universal-wavedash` | `fox-kill-confirm` | [wavedash](../techniques/wavedash.md) | implemented: `drills/fox_neutral.inc.h`; the CPU jumps in after an unpredictable wait (Falcon nair, Falco dair, Marth fair; no Sheik dash attack). Simulator and Dolphin specs pass (2026-11-12) |
| 3 | `fox-shield-then-punish` | Take it on shield | Shield the approach and convert out of shield | approaches that are unsafe on shield, mixed with a grab | - | `fox-shine-oos`, `fox-oos-choice` | [OoS](../techniques/out-of-shield.md) | implemented: `drills/fox_neutral_reads.inc.h`; the wavedash-back approaches, with a run-up grab one time in three. Simulator and Dolphin specs pass (2026-11-12) |
| 4 | `fox-approach-nair-dair` | Approach: nair or dair | Nair the standing opponent, dair the one who crouches; do not approach the one who is ready to shield grab | CPU stands, crouches or shields | `universal-shffl` | `fox-aerial-confirm` | [neutral](../characters/fox.md#neutral-game) | implemented: `drills/fox_neutral_reads.inc.h`; Marth stands, crouches or shields and changes; option to fix the stance. Simulator and Dolphin specs pass (2026-11-12). The CPU does not punish a wrong choice |
| 5 | `fox-running-shine` | Running shine | Catch a dash or jump with shine | dash dancing or jumping CPU | `fox-waveshine` | `fox-waveshine-usmash`, `fox-shine-knockdown` | [neutral](../characters/fox.md#neutral-game) | implemented: `drills/fox_neutral_reads.inc.h`; Marth dash dances and sometimes short hops. Simulator and Dolphin specs pass (2026-11-12) |
| 6 | `fox-laser-forcing` | Lasers force the approach | Laser until the CPU commits, then punish the commitment | CPU that approaches after taking lasers | `fox-shdl` | 1, 2 | [neutral](../characters/fox.md#neutral-game) | implemented: `drills/fox_neutral_reads.inc.h`; Marth runs in with a dash attack after 2 to 4 lasers. Simulator and Dolphin specs pass (2026-11-12) |
| 7 | `fox-anti-air` | Anti-air | Beat a jump-in with up tilt, up smash or bair | Jigglypuff bair, Peach float nair, Falcon full-hop aerials | - | `fox-kill-confirm` | [matchups](../characters/fox.md#matchup-notes) | implemented: `drills/fox_neutral.inc.h`; Falcon full hop nair and dair, Jigglypuff fair, Peach fair (not float nair). Simulator and Dolphin specs pass (2026-11-12) |
| 8 | `fox-vs-crouch-cancel` | Beat crouch cancel | Recognise the crouch and choose dair, grab or shine instead of nair | Peach, Samus, Marth crouching at low percent | 4 | `fox-uthrow-uair` | [crouch cancel](../techniques/crouch-cancel.md), [Peach](../characters/peach.md) | implemented: `drills/fox_neutral_reads.inc.h`; Peach, Samus, Marth crouching. Simulator and Dolphin specs pass (2026-11-12). The CPU does not hit back after a crouch cancel |

## Open questions for this course

- Which drills are worth their cost. Neutral 6-8 need the most CPU behaviour and could wait
  for a second pass.
- Whether `fox-multishine` and the universal wavedash, L-cancel, ledgedash and shield drop
  rows reuse TM-CE's events or are rebuilt on the engine for uniform guides and statistics.
- Matchup depth: the decks above lean on Marth, Sheik, Falco, Falcon, Peach and Jigglypuff.
