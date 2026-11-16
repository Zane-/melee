---
schema: melee-course/v1
id: fox
character: fox
status: draft
summary: From executing shine cleanly to winning the opening, converting it into a stock and getting out of the combos Fox is caught in.
includes: [universal]
---

# Fox course

On the native build every drill of this file that is implemented is also ported
(`tools/melee_course/drills/`) and passes the same specs (2026-11-13): "The courses on the
native build" in `docs/ai/native-ai.md`.

Curriculum approved by the owner 2026-11-12 (with the Tech order below). Every drill is
`planned` except where the Status column says otherwise.
Format: [`README.md`](README.md). Knowledge: [`../characters/fox.md`](../characters/fox.md).

How the parts connect for Fox: **Tech** makes shine, wavedash and the aerials automatic.
**Punish** turns the three openings Fox gets most (a shielded move, a grab, a landed aerial
or shine) into up smash, up air or an edgeguard. **Defense** covers what kills Fox: chain
grabs, tech chases, crouch-cancel punishes and being edgeguarded. **Neutral** then asks the
player to earn the opening against an opponent that commits, and hands over to the punish
drill that starts from it.

`fox-shine-oos` is in the drill format (`data/drills/fox-shine-oos.json`, 2026-11-15): its
deck the 2021 tier list's top 11, each opponent a script of the engine's vocabulary that
approaches the shield and commits only to what a frame-4 shine out of shield answers. The
Shine OoS event (`src/tmce/events/shineoos/`) is the overlay's.

## Tech skill

Three subcourses (owner, 2026-11-14): Movement (movement every character uses), Fundamentals
(techniques every character uses), Character (Fox's own). Each `###` subcourse has its own
plan table, numbered from 1. Drills are written in the drill format (`data/drills/`,
`docs/ai/drill-format.md`).

### Movement

| # | id | Drill | Goal | CPU | Requires | Leads to | Knowledge | Status |
|-|-|-|-|-|-|-|-|-|
| 1 | `universal-short-hop` | Short hop | Short hop ten times in a row | none | - | - | implemented: `drills/tech_short_hop.inc.h`; simulator and Dolphin specs pass (2026-11-12). Press length shown in the verdict | drill format: `data/drills/universal-short-hop.json` |
| 2 | `universal-fast-fall` | Fast fall | Fast fall at the top of a jump | none | - | - | - | drill format: `data/drills/universal-fast-fall.json` |
| 3 | `universal-dash-dance` | Dash dance | Dash back and forth without breaking into a run | none | - | - | implemented: `drills/tech_movement.inc.h`; simulator and Dolphin specs pass (2026-11-12); demonstration passes for all 26 characters. Native (2026-11-13): switches counted, longest dance kept, light-ray targets; the C still counts to a number of dashes | drill format: `data/drills/universal-dash-dance.json` |
| 4 | `universal-wavedash` | Wavedash | Air dodge into the ground on the first frame in the air | none | - | - | implemented: `drills/tech_wavedash.inc.h`; simulator and Dolphin specs pass (2026-11-12). Chosen length / angle not built | drill format: `data/drills/universal-wavedash.json` |
| 5 | `universal-waveland` | Waveland | Air dodge into the stage or a platform as you land | none | - | - | - | drill format: `data/drills/universal-waveland.json` |
| 6 | `universal-pivot` | Pivot | Turn around out of a dash and stand still | none | - | - | - | drill format: `data/drills/universal-pivot.json` |
| 7 | `universal-ledgedash` | Ledgedash | Land on the stage from the ledge with invincibility left | none | - | - | implemented on Final Destination's left ledge: `drills/tech_ledge.inc.h`; simulator and Dolphin specs pass (2026-11-12). Fox only checked. Native (2026-11-13): starts on the ledge, falling, on the stage or on a respawn platform; a regrab is a refresh, not a failure | drill format: `data/drills/universal-ledgedash.json` |

### Fundamentals

| # | id | Drill | Goal | CPU | Requires | Leads to | Knowledge | Status |
|-|-|-|-|-|-|-|-|-|
| 1 | `universal-l-cancel` | L-cancel | Halve an aerial's landing lag | none | - | - | implemented: `drills/tech_movement.inc.h`; simulator and Dolphin specs pass (2026-11-12). Demonstrations succeed for every character but Mr. Game & Watch's three aerials that cannot be L-cancelled (simulator and native, 2026-11-13) | drill format: `data/drills/universal-l-cancel.json` |
| 2 | `universal-shffl` | SHFFL | Short hop, aerial, fast fall and L-cancel in one motion | none | - | - | implemented: `drills/tech_movement.inc.h`; simulator and Dolphin specs pass (2026-11-12). Demonstrations succeed for every character but Mr. Game & Watch's three aerials that cannot be L-cancelled (simulator and native, 2026-11-13) | drill format: `data/drills/universal-shffl.json` |
| 3 | `universal-jc-grab` | Jump-cancel grab | A standing grab out of a dash | none | - | - | implemented: `drills/tech_movement.inc.h`; simulator and Dolphin specs pass (2026-11-12); demonstration passes for all 26 characters. Native (2026-11-13): an up smash is not counted (its own drill below) | drill format: `data/drills/universal-jc-grab.json` |
| 4 | `universal-jc-upsmash` | Jump-cancel up smash | An up smash out of a dash | none | - | - | native only (2026-11-13, the owner: "JC up smash should be its own drill below JC grab"): `tools/melee_course/drills/tech_movement.py`; no C drill in the overlay | drill format: `data/drills/universal-jc-upsmash.json` |
| 5 | `universal-di` | Directional Influence (DI) | Change your launch angle with the control stick | hits you | - | - | - | drill format: `data/drills/universal-di.json` |
| 6 | `universal-sdi` | Smash DI (SDI) | Move out of a multi-hit attack during hitlag | hits you | - | - | - | drill format: `data/drills/universal-sdi.json` |
| 7 | `universal-asdi` | Automatic SDI (ASDI) | Shift your position at the end of hitlag | hits you | - | - | - | drill format: `data/drills/universal-asdi.json` |
| 8 | `universal-shield-drop` | Shield drop | Drop through a platform out of shield | none | - | - | implemented on Battlefield's left platform: `drills/tech_ledge.inc.h`; simulator and Dolphin specs pass (2026-11-12). Native (2026-11-13): left, top and right platforms, standing, dropping onto it or jumping up to it, on four stages (L/R held 5 s) | drill format: `data/drills/universal-shield-drop.json` |
| 9 | `universal-edge-cancel` | Edge cancel | Slide off the edge during an aerial's landing lag | none | - | - | - | drill format: `data/drills/universal-edge-cancel.json` |
| 10 | `universal-slide-off` | Slide off | Slide off a platform during landing lag | none | - | - | - | drill format: `data/drills/universal-slide-off.json` |

### Character

| # | id | Drill | Goal | CPU | Requires | Leads to | Knowledge | Status |
|-|-|-|-|-|-|-|-|-|
| 1 | `fox-waveshine` | Waveshine | Shine, jump out of it, and wavedash | none | - | - | implemented without a target: `drills/fox_shine_tech.inc.h`; simulator and Dolphin specs pass (2026-11-12). Passive target not built. Native (2026-11-13): up to 5 frames late counts by default | drill format: `data/drills/fox-waveshine.json` |
| 2 | `fox-shine-grab` | Shine grab | Shine, jump out of it, and grab before leaving the ground | none | - | - | implemented on a shielding Marth: `drills/fox_pressure.inc.h`; simulator and Dolphin specs pass (2026-11-12) | drill format: `data/drills/fox-shine-grab.json` |
| 3 | `fox-shffl-shine` | SHFFL shine | SHFFL an aerial, then shine as you land | none | - | - | - | drill format: `data/drills/fox-shffl-shine.json` |
| 4 | `fox-shffl-shine-grab` | SHFFL shine grab | SHFFL an aerial, shine as you land, then grab | none | - | - | - | drill format: `data/drills/fox-shffl-shine-grab.json` |
| 5 | `fox-jc-shine` | Jump-cancel shine | Jump out of a dash and shine as you leave the ground | none | - | - | implemented: `drills/fox_shine_tech.inc.h`; simulator and Dolphin specs pass (2026-11-12) | drill format: `data/drills/fox-jc-shine.json` |
| 6 | `fox-multishine` | Multishine | Jump out of each shine and shine again as you leave the ground | none | - | - | implemented without a shield: `drills/fox_shine_tech.inc.h`; simulator and Dolphin specs pass (2026-11-12). On-shield variant not built | drill format: `data/drills/fox-multishine.json` |
| 7 | `fox-shorten` | Shortened Illusion | Stop Illusion at the length you choose | none | - | - | - | drill format: `data/drills/fox-shorten.json` |
| 8 | `fox-firefox-angles` | Firefox angles | Recover with Firefox at the angle each position needs | none | - | - | - | drill format: `data/drills/fox-firefox-angles.json` |
| 9 | `fox-ledge-stall` | Firefox ledge stall | Drop from the ledge and grab it again with Firefox | none | - | - | implemented: `drills/tech_ledge.inc.h`; simulator and Dolphin specs pass (2026-11-12) | drill format: `data/drills/fox-ledge-stall.json` |
| 10 | `fox-double-laser` | Double laser | Two lasers in one short hop | none | - | - | - | drill format: `data/drills/fox-double-laser.json` |

TM-CE already has events for some of these (wavedash, L-cancel, ledgedash, legacy
Multishine, shield drop).

## Punish

From the three openings: a move on Fox's shield, a grab, a landed hit or shine.

| # | id | Drill | Goal | CPU | Requires | Leads to | Knowledge | Status |
|-|-|-|-|-|-|-|-|-|
| 1 | `fox-shine-oos` | Shine out of shield | Punish a shielded move with a frame 4 shine | deck: the 2021 top 11 (Fox, Marth, Jigglypuff, Falco, Sheik, Captain Falcon, Peach, Ice Climbers, Pikachu, Yoshi, Samus), each an engine script: footsies, then an approach on the shield (aerials, tilts, smashes, dash attacks, some specials) held to the contract `{"answer": "oos_down_b", "within": 4}` | `fox-waveshine` | `fox-waveshine-usmash` | [seed](../characters/fox.md#shine-out-of-shield-punish), [OoS](../techniques/out-of-shield.md) | drill format: `data/drills/fox-shine-oos.json` (2026-11-15): jump out of shield, the shine out of shield, then against the deck; `check.py` 45 of 45 (every opponent); the frame-perfect example against 16 approaches of each opponent, 176 of 176; `tests/client/shine_oos.py`. A match holds eight fighters: the rotation draws Fox to the Ice Climbers, Pikachu, Yoshi and Samus come with D-pad left and right (a match loaded). The overlay's C drill: `src/tmce/events/course/drills/fox_shine_oos.inc.h` |
| 2 | `fox-oos-choice` | Pick the out-of-shield option | Choose shine, grab, nair, up smash or wavedash by spacing and advantage | deck, mixed spacings | 1 | - | [OoS](../techniques/out-of-shield.md) | implemented: `drills/fox_punish.inc.h`; the Shine OoS scenarios from 0, 4 or 8 units farther; any hit or grab before the CPU has recovered and reacted (4 frames) counts, and the verdict names the option. Simulator specs pass (2026-11-12). It does not judge whether the option was the best one |
| 3 | `fox-waveshine-usmash` | Waveshine to up smash | Shine a grounded opponent and up smash before they act | characters that slide from shine | `fox-waveshine` | - | [seed](../characters/fox.md#waveshine-to-up-smash) | implemented on Marth: `drills/fox_punish.inc.h`; he shields as soon as he can. Simulator specs pass (2026-11-12). Marth slides 44 units, so only a near-flat wavedash reaches; no other characters |
| 4 | `fox-shine-knockdown` | Shine knockdown: jab reset or tech chase | React to tech in place, tech away, tech in or no tech after shine | characters that fall from shine; random tech | 3 | - | [seed](../characters/fox.md#jab-reset-or-tech-chase-after-shine), [tech chase](../techniques/tech-chase.md) | implemented on Falco and Fox: `drills/fox_punish_confirms.inc.h`; the CPU techs in place, away or in, or misses and then gets up, rolls or attacks (option to fix the choice); he shields once he is up. Simulator and Dolphin specs pass (2026-11-12). No demonstration |
| 5 | `fox-uthrow-uair` | Up throw up air | Land up air after up throw against DI and SDI | floaties and mid-weights; random DI, SDI at a set tolerance | `universal-jc-grab` | - | [seed](../characters/fox.md#up-throw-up-air-against-sdi) | implemented: `drills/fox_punish_throws.inc.h`; Marth, Sheik, Peach, Jigglypuff at 90%, random DI, the CPU jumps away after a reaction time (option). Simulator specs pass (2026-11-12). No SDI |
| 6 | `fox-uthrow-chaingrab` | Chain grab fastfallers | Regrab Fox and Falco out of up throw until you drop it; tech chase them when they hit the floor | Fox, Falco; random DI, a tech (in place, away, in) or none when they land in tumble, a getup option from the floor, jump away on their first free frame | `universal-jc-grab` | - | [seed](../characters/fox.md#chain-grab-fastfallers) | implemented: `drills/fox_punish_throws.inc.h`; Falco and Fox, random DI, the CPU jumps on its first free frame. Simulator specs pass (2026-11-12). Natively (2026-11-13, the owner: "let them cook"): `tools/melee_course/drills/fox_punish_throws.py` goes on until the chain is dropped, any throw, regrab or hit keeps it, the CPU techs or misses and gets up, and the attempt says how long the chain was; `tests/course/chaingrab.py` (a 10-regrab chain at 0%, a missed tech chased). No shine out |
| 7 | `fox-aerial-confirm` | Aerial hit confirm | After a landed nair or dair, pick shine, grab or up smash by percent and whether they crouch cancelled | deck; random crouch cancel / ASDI down | `fox-shffl-nair-shine` | 3, 5 | [neutral](../characters/fox.md#neutral-game), [crouch cancel](../techniques/crouch-cancel.md) | implemented on Marth: `drills/fox_punish_confirms.inc.h`; standing he jumps away after his reaction time, crouching he crouch cancels and shields, so the grab is the follow-up. Simulator and Dolphin specs pass (2026-11-12). Not by percent; no ASDI down |
| 8 | `fox-shield-pressure` | Shield pressure | Keep the gaps too small for shield grab and the opponent's fastest out-of-shield option | shielding CPU that takes any gap it is given | `fox-shffl-nair-shine`, `fox-shine-grab` | - | [seed](../characters/fox.md#shield-pressure-against-shield-grab), [pressure](../techniques/shield-pressure.md) | implemented on Marth: `drills/fox_punish.inc.h`; he tries to grab out of shield whenever free. Simulator specs pass (2026-11-12). Only the grab, not his other out-of-shield options |
| 9 | `fox-shine-spike` | Shine spike | Take the stock offstage with shine and make it back | recovering Marth, Sheik, Falcon, Peach; random recovery choice | `fox-waveshine` | - | [seed](../characters/fox.md#shine-spike-the-recovery), [edgeguarding](../techniques/edgeguarding.md) | implemented: `drills/punish_offstage.inc.h`; Marth starts in the air off the ledge and recovers high (up B onto the stage) or low (to the ledge); the stock must go to a shine off the stage and the player must get back. Simulator and Dolphin specs pass (2026-11-12). Marth only; no demonstration |
| 10 | `fox-edgeguard-onstage` | Edgeguard from the stage | Cover the recovery with bair, down smash or ledge grab timing | recovering spacies and Marth; random recovery choice | - | - | [edgeguarding](../techniques/edgeguarding.md), [kill options](../characters/fox.md#kill-options) | implemented: `drills/punish_offstage.inc.h`; the same recovering Marth; the stock must go, and the verdict notes if the player left the stage for it. Simulator and Dolphin specs pass (2026-11-12). No spec for a kill made from the stage; no demonstration |
| 11 | `fox-kill-confirm` | Kill confirms | Up throw up air, dash attack or up tilt into up smash at kill percent | deck by weight class; random DI | 5 | - | [punish game](../characters/fox.md#punish-game), [kill options](../characters/fox.md#kill-options) | implemented: `drills/fox_punish_throws.inc.h`; Marth, Sheik, Jigglypuff at 110%; the opener must be a grab, shine, up tilt or dash attack, and the stock must go. Failure specs pass in the simulator (2026-11-12); a kill was seen once during development (Marth at 150%, up throw up air) but there is no spec for one and no demonstration |

## Defense

What Fox is caught in most, from the other side. The CPU performs the real sequence.

| # | id | Drill | Goal | CPU | Requires | Leads to | Knowledge | Status |
|-|-|-|-|-|-|-|-|-|
| 1 | `universal-tech` | Tech the ground | Tech in place, in and away on demand; see the lockout | hits the player into the floor | - | 6 | [teching](../techniques/teching.md) | implemented: `drills/defense.inc.h`; Sheik grabs and down throws, the drill asks for a tech in place, away or in. Simulator and Dolphin specs pass (2026-11-12). The lockout is described, not shown |
| 2 | `universal-crouch-cancel` | Crouch cancel | Crouch through weak hits and punish before they can act; recognise the percent where it stops | Marth down tilt and fair, Sheik forward and down tilt, Falcon nair, each at percents it holds to | - | 3 | [crouch cancel](../techniques/crouch-cancel.md) | implemented natively (2026-11-13, split from the C drill `universal-asdi-down` at the owner's request): `tools/melee_course/drills/defense_asdi.py`; the drill picks the player's percent where the crouch holds against the move (or just under its limit), the CPU shields once it can act. Limits measured on the native build: `tests/course/asdi.py` |
| 3 | `universal-asdi-down` | ASDI down | Hold the C-stick down through weak hits, land at once and punish | Marth down tilt and fair, Sheik forward and down tilt, each at percents it holds to | 2 | - | [ASDI](../techniques/asdi.md) | implemented natively (2026-11-13): `tools/melee_course/drills/defense_asdi.py`; standing, the C-stick down as the freeze ends (pressed during it or held from before: a fresh press while standing is a down smash); the landing can be left for a shine or grab after 4 frames. Falcon's nair launches a standing Fox at any percent, so it is crouch cancel only. The overlay's C drill is still the one of 2026-11-12 |
| 4 | `universal-di-survival` | Survival and combo DI | DI the kill move to live and the combo starter to escape | kill moves and throws by character | - | - | [DI](../techniques/di.md) | implemented: `drills/defense.inc.h`; Fox up smash at 90%, where no DI dies and sideways DI lives (80% lives without, 100% dies with). Simulator and Dolphin specs pass (2026-11-12). Survival DI only, one move |
| 5 | `universal-sdi` | SDI multi-hits | SDI out of drill, up air, down smash | Fox dair and up throw up air, Peach down smash | - | - | [SDI](../techniques/sdi.md) | implemented: `drills/defense_pressure.inc.h`; Fox short hop down air then shine; getting out before the shine connects is the success. Simulator and Dolphin specs pass (2026-11-12). One multi-hit; no up air or down smash |
| 6 | `fox-escape-techchase` | Escape the tech chase | Mix tech options and act on the first free frame against Sheik and Falcon | Sheik down throw, Falcon down and up throw; reacts at a set speed | 1 | - | [dummy](../characters/fox.md#as-the-training-dummy), [Sheik](../characters/sheik.md), [Falcon](../characters/captain-falcon.md) | implemented: `drills/defense.inc.h`; Sheik down throw, then she reacts to the tech (option) and grabs, or down smashes a missed tech. Simulator and Dolphin specs pass (2026-11-12). No Falcon |
| 7 | `fox-escape-chaingrab` | Escape Marth's chain grab | Use the DI that ends the chain earliest, then shine or jump out | Marth up throw regrabs, pivot tipper at the end | 4 | - | [dummy](../characters/fox.md#as-the-training-dummy), [Marth](../characters/marth.md) | implemented: `drills/defense_escapes.inc.h`; Marth up throws and regrabs (he turns round or runs in, he cannot reposition in the 15 frames he has); with no DI at 0% he regrabs three times, with DI he misses and smashes a player who lies there. Simulator and Dolphin specs pass (2026-11-12). No pivot tipper finish |
| 8 | `fox-escape-pressure` | Escape shield pressure | Find the gap in Falco's and Fox's pressure: shine, grab, roll or wavedash out | Falco pillar, Fox drill shine; gaps at a set tolerance | `fox-shine-oos` | - | [defense](../characters/fox.md#defense-and-out-of-shield), [Falco](../characters/falco.md) | implemented: `drills/defense_pressure.inc.h`; a CPU Fox loops short hop late neutral air, L-cancel, shine, jump; the wait before each shine is the hole (option). Simulator and Dolphin specs pass (2026-11-12). No Falco pillar |
| 9 | `fox-combo-shine` | Shine out of combos | Shine on the first actionable frame after hitstun | strings with a real gap; frame count shown | - | - | [defense](../characters/fox.md#defense-and-out-of-shield) | implemented: `drills/defense.inc.h`; Marth jab then forward smash; the shine must come within 12, 8 or 4 frames of being free (option). Simulator and Dolphin specs pass (2026-11-12). One string |
| 10 | `universal-wall-tech` | Wall and ledge tech | Tech the stage when hit while recovering | Marth, Sheik hits at the ledge | 1 | 11 | [wall tech](../techniques/wall-tech.md), [Amsah tech](../techniques/amsah-tech.md) | implemented: `drills/defense_pressure.inc.h`; the player starts below the ledge and Marth forward airs him into the stage's side. Simulator and Dolphin specs pass (2026-11-12). One hit, Final Destination; no wall jump, no Amsah tech |
| 11 | `fox-recovery-mixup` | Recover against an edgeguard | Choose Illusion length, Firefox angle, air dodge or ledge sweetspot against a CPU covering options | Marth, Sheik, Fox edgeguarding; coverage at a set skill | `fox-illusion-shorten` | - | [seed](../characters/fox.md#recovery-mixups-against-an-edgeguarder), [recovery](../characters/fox.md#recovery) | implemented: `drills/defense_pressure.inc.h`; the player starts off the ledge, Marth swings at a high approach after his reaction time and at a ledge hang as the intangibility ends. Simulator and Dolphin specs pass (2026-11-12). One CPU answer per approach; Marth only; no demonstration |
| 12 | `fox-ledgedash-attack` | Get off the ledge | Ledgedash, ledge stall or ledge option against a CPU waiting at the ledge | opponent covering ledge options | `universal-ledgedash` | - | [ledge options](../techniques/ledge-options.md), [seed](../characters/fox.md#ledgedash-with-intangibility) | implemented: `drills/defense_escapes.inc.h`; Marth waits 22 units inside the ledge and forward smashes as the player's intangibility runs out. Simulator and Dolphin specs pass (2026-11-12). One CPU answer; no ledge stall branch |

## Neutral

Each drill ends at the opening and names the punish drill that continues from it. The CPU
commits to one of a few realistic options after a reaction delay; the delay is the
difficulty.

| # | id | Drill | Goal | CPU | Requires | Leads to | Knowledge | Status |
|-|-|-|-|-|-|-|-|-|
| 1 | `fox-whiff-punish` | Whiff punish | Dash dance outside the move's range, then grab or up smash its recovery | Marth fsmash, dtilt, fair; Sheik ftilt; Peach dash attack | `universal-dash-dance`, `universal-jc-grab` | `fox-uthrow-uair`, `fox-uthrow-chaingrab` | [neutral](../characters/fox.md#neutral-game), [dash dance](../techniques/dash-dance.md) | built in the drill format (2026-11-15): `data/drills/fox-whiff-punish.json`, two parts (make it miss; punish the whiff with a jump-cancelled grab), a deck of the top 11 playing footsies just outside their reach (reach + 6 to + 18 units), swinging when the player comes within reach + 8 (seen 15 frames late; a dash toward let go of first), one of its attacks at random: Fox usmash, grab; Marth fsmash, usmash, utilt; Sheik dsmash, usmash, dash grab; Falcon fsmash, usmash, utilt, dash grab; Peach dsmash, usmash, ftilt, utilt, dash grab; Pikachu fsmash, dsmash, usmash, dash grab; Yoshi fsmash, dsmash, usmash, ftilt, utilt. Standing until then (fewer than 2 attacks punishable out of footsies, or Falco's not provably able to catch a player walking in): Jigglypuff fsmash, dsmash, usmash, dash grab; Falco dsmash, usmash, dtilt, dash grab; Ice Climbers fsmash, usmash, utilt; Samus fsmash, dsmash, usmash. Each attack punished in `check.py` from where it misses; left out: tilts and smashes a grab cannot reach in time, Marth's dash grab (escaping it and punishing it need retreats a frame apart), Peach's forward smash (states of her own, not seen as an attack) and dash attacks (the opponent attacks from standing). `tests/client/whiff_punish.py` |
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
