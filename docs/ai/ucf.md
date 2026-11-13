# UCF 0.84 in C

Asked for by the owner on 2026-11-12: "Frame delay and other features from Slippi including
UCF so we get a consistent practice experience." Built 2026-11-13: `src/melee/tm/ucf/`,
`config/GALE01/tm_hooks/ucf.txt`, `tests/sim/ucf.py`.

UCF (Universal Controller Fix) is eight small changes to how the game reads the control
stick, so that controllers whose sticks report slightly different numbers all get the same
dash back, shield drop, SDI, tumble wiggle and cardinal directions. Tournaments and Slippi run
it as assembly injected into eight vanilla functions.

## Why it is not simply patched in

Slippi Dolphin injects its own copy of UCF ("Required: General Codes") at those eight
addresses whenever the game boots, and this build may not patch an address Slippi patches
(`CLAUDE.md`). So before this, the build had UCF on Slippi Dolphin and none anywhere else
(plain Dolphin, a console, the native build).

Now the same rules are in C and are reached without touching those addresses:

- **Through the calls and table slots that lead to the eight functions.** A `call` hook on
  each `bl` to a function, or a `pointer` hook on its slot in `ftData_MotionStateList`, runs a
  C version of that function. The vanilla functions are neither edited nor replaced.
- **It steps aside.** `tm_ucf_Active()` reads the instruction at each of the eight sites. If
  any is not the vanilla one, somebody else's UCF is there (Slippi's): every hook then calls
  the vanilla function, which runs with that code in it. The game is never fixed twice, and
  on Slippi Dolphin the build behaves exactly as stock Slippi does, which netplay needs.

## The rules, and how each is reached

Read from the code Slippi ships (`GALE01r2.ini`, compiled C; disassembled with
`build/binutils/powerpc-eabi-objdump -D -b binary -m powerpc:750 -EB`).

| Rule | Slippi's site | What it does | Reached by |
|-|-|-|-|
| Pad buffer, 1.0 cardinals | `Fighter_procInput+0x750` | Keeps the last four raw stick samples per port. A raw stick 80 or more along one axis and at most 6 off it reads exactly 1.0 / 0 (not while Zelda aims Farore's Wind). Counts the frames the stick sits at the rim below y = -0.609 after a fast move down (more than 44 in two frames) | Two `call` hooks in `Fighter_procInput`: +0xC4 hands over the fighter, +0x738 is the call just before the site (only two timer stores lie between, which UCF does not use) |
| Dash back | `ftCo_Turn_IASA+0x4C` | On frame 2 of a turn, a stick past 0.8 that moved more than 75 in two frames finishes the turn at once, so the dash starts. The Ice Climbers' partner gets the same direction | `pointer` hook on Turn's input callback: a copy of the function with the rule in place |
| Dash back out of crouch | `ftCo_SquatRv_CheckInput+0x14` | A stick that has just left the centre sideways and is at the rim uses 0.59 instead of 0.625 as the line for standing up | `call` hook on its one call: a copy |
| Shield drop | `ftCo_80099894+0x10` | On a platform, with the stick at the rim, above -0.8, held sideways for 4 frames and no C-stick dodge: the spot dodge that was about to start does not, and the checks after it run (the drop among them) | `call` hooks on every call of the two functions that decide on a spot dodge: they return false first when the rule holds |
| Shield drop, held | `ftCo_8009A080+0x38` | The drop through a platform also happens when the rim counter above is over 1 | `call` hooks on every call: a copy with the wider test |
| SDI | `ftCo_Damage_OnEveryHitlag+0x5C` | Also when the stick's timer has run out but the raw stick moved more than 62 in two frames from inside the SDI circle | From the wrapper of the call before `fp->hitlag_cb(gobj)` (osdtech's): the callback is run with the timer at 0 for those frames, and the timer put back if the callback refused for another reason |
| Shield SDI | `ftCo_80093240+0x54` | The same on one axis. (The "was inside" test is signed: a push to the left always passes it. That is how UCF is, and it is kept) | Same |
| Tumble | `ftCo_DamageFall_IASA+0xCC` | The wiggle counts on the frame the stick crosses 0.8, or on the next if it was still inside the frame before and moved more than 75 in two frames | `call` hooks on its three calls and a `pointer` hook on DamageFall's input callback: a copy |

Three of the C versions are copies of functions in which the mod already has `call` hooks
(the OSDs). A copy calls those wrappers by name (`tm_osdtech_DashEnter`, `tm_osdact_DF*`)
where the vanilla body has the hooked calls. A new hook inside `ftCo_Turn_IASA`,
`ftCo_DamageFall_IASA`, `ftCo_8009A080` or `ftCo_SquatRv_CheckInput` must be mirrored in
`ucf.c`. `ftCo_Guard_IASA` and `ftCo_GuardOff_IASA` are already replaced by osdact, whose
copies call `tm_ucf_8009980C` / `tm_ucf_8009A080` directly.

Not ported: the "UCF 0.84" text Slippi's copy draws on the character select screen. The
Controls page of the main menu says whose UCF is running instead.

State: the stick history and the fighter handed between the two `Fighter_procInput` hooks
are statics. They are not rolled back; that is fine because this code is off whenever
Slippi (and so its netplay) is present. For netcode of our own on the native build they
have to move into the saved state.

## How it is checked

`tests/sim/ucf.py` plays the same inputs three times from one saved match start, in the
simulator:

- **ours**: the overlay as built;
- **slippi**: Slippi's eight codes injected at their addresses the way a Gecko handler does
  it (read from the Slippi Launcher install on this machine; the test stops if there is
  none), which makes the C step aside by itself;
- **vanilla**: the C switched off (`tm_ucf_off`), nothing injected.

"ours" must equal "slippi" on every frame: state, state frame, position, velocity, facing,
damage, hitlag and hitstun of both fighters. "vanilla" must differ somewhere, and code hooks
inside the injected code count how often each rule actually fired: a rule that never fired
is a failure, because then the inputs proved nothing about it.

The inputs are one segment per rule (flicks through a halfway point while standing;
crouching and out to the rim; shielding on a platform with rolls and flicks to the notches;
being hit bare, in shield, and one frame after a tap jump; a segment of random stick and
buttons), with every random number drawn from the seed. Player 2 walks up and smashes. A
fighter that leaves the stage is put back by writing its position, the same in each run.

Two rules hardly ever come up in play and needed a recipe:

- **SDI by flick** needs the stick's timer spent by something else on the frame before the
  hit. The test tap-jumps (y = 54, under the SDI circle) on the frame before player 2's
  smash lands, then pushes to 100.
- **Shield SDI by flick** comes up on the second frame of a full push to the left during
  shield hitlag (the signed test above).

Result on 2026-11-13 (`--seeds 5 --frames 2700`, about 7 minutes): identical to Slippi's
code on every frame of all five runs; the vanilla game parted from it in every run (first at
frames 52 to 1053). Times each rule fired in Slippi's code: cardinals 894 (x) and 1,708 (y),
rim counter 1,413, dash back 16, crouch line 15, SDI by flick 4, shield SDI by flick 2,
wiggle on the second frame 2 (both by flick), spot dodge held back 3, drop from a held
position 4. The counts for the rare rules are small: they show the rule's own path agrees,
not every corner of it.

**The drill specs.** All 230 specs under `tests/tmtest/course/` were run in the simulator
with UCF on (2026-11-13): 229 gave the result they gave without it. The one that changed is
`universal-shield-drop/spot_dodge.json`: its stick position (90, -89) was a spot dodge in the
vanilla game and is a shield drop with UCF, which is the point of UCF. The spec now pushes
the stick past the notch (90, -127). Before, the specs ran without UCF while the owner plays
with Slippi's; they now run with the rules the game is played with.
`TM_UCF_OFF=1 python tools/melee_sim/tmtest_sim.py SPEC` runs a spec without UCF.

## In the native build (2026-11-13)

The owner, playing the native client: "dashback seems a little stuck, I am getting stuck
in my movement sometimes". The native build had no UCF at all: it compiled the vanilla
game and nothing of `src/melee/tm/`. It now compiles `ucf.c` too and reaches it at the same
places as the overlay's hooks, in the copies of vanilla files it builds
(`tools/native_build.py`):

- files that call one of the replaced functions without defining it are compiled with it
  renamed (`-DftCo_80099794=tm_ucf_80099794` and so on; `VANILLA`). Every call of those
  functions in the decomp is one the hook table hooks, so a rename reaches exactly those
  sites; the Turn and DamageFall entries of `ftData_MotionStateList` the same way
  (`ftmotionstates.c`);
- `fighter.c` is patched (`PATCHES`) at the two calls in `Fighter_procInput` (the first
  `ftCo_IsCpuControlled`, +0xC4, and the one `lb_8000D148`, +0x738: both checked against
  the console's code) and before the hitlag callback in `Fighter_procUpdate`;
- `src/host/ucf.c` stands in for the overlay's display wrappers that the C calls
  (`tm_osdtech_DashEnter` is `ftCo_Dash_Enter` here) and has its own copy of
  `ftCo_SquatRv_Enter`, which is `static` in the decomp (the overlay reaches it by its
  console address; without the copy the native link stubbed it, silently);
- `tm_ucf_Active()` does not read the eight sites under `TARGET_PC`: they are this
  machine's code and nothing injects into them.

On from the start, as on Slippi. The driver's `ucf 0|1` (`Native.ucf()`) switches it;
`tools/melee_native/compare.py` switches it off, because the console code it compares
with is vanilla.

`tests/native/ucf.py` checks it against Slippi's own code: the console's code in the
simulator with Slippi's eight codes injected, the native build with UCF, the native build
without, the same controller input to all three every frame (tests/sim/ucf.py's input,
without its writes into memory: the fighters walk where each part happens). Six seeds of
2,700 frames: identical on every frame (states, facing, hitlag and hitstun exact;
positions, speeds and animation frames to rounding, as `compare.py`), and every rule
fired in Slippi's code at least once (SDI 4 times, shield SDI 3, the rest more). The
vanilla build parts from them in each seed.

What a player feels (the same test, first): Fox standing, facing right, the stick flicked
left with one frame part way (-40). With UCF the dash starts after one frame of Turn;
without it, after five. Four frames stuck turning, on every dash back whose flick the game
happens to read half done.

## Not done

- In Dolphin the overlay with these hooks boots, the Controls page reports "built in"
  (so all eight sites read as vanilla there) and two drill specs run; no UCF rule was
  exercised by hand or by script in Dolphin. Not tried on Slippi Dolphin (where it should
  report "Slippi's") or on a console.
- Characters other than Fox (player 1) and Marth (player 2), and stages other than
  Battlefield, are not in the comparison. The rules are in common fighter code, but Yoshi's
  shield and Samus's down special have their own call sites, which only the hook table and
  the layout check cover.
- The native build has no UCF: it has no hooks yet (`native-port.md`).
