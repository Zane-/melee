"""Control profiles and input delay (src/melee/tm/controls/), in the simulator.

Fox stands in the Lab's sandbox. Each check sets the module's settings in
memory, presses a button and watches which state Fox enters and when.

    python tests/sim/controls.py
"""
import sys

sys.path.insert(0, "tools/melee_sim")
from sim import Sim  # noqa: E402

WAIT = 14
JUMP_SQUAT = 24
# offsets in TmCtlSettings (src/melee/tm/controls/controls.h)
DELAY, PORT_PROFILE, PROFILES, PROFILE_SIZE = 0, 1, 125, 22
P_USED, P_MAP, P_TAP_JUMP = 9, 10, 21
IN_X, IN_Y, IN_L = 2, 3, 5
ACT_SPECIAL, ACT_JUMP, ACT_SHIELD = 2, 3, 4

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


def frames_until(s, state, limit=40):
    """Frames until player 1 is in `state`, counting the frame that gets
    there; None if it does not within `limit`."""
    for n in range(1, limit + 1):
        s.step()
        if s.fighter(0).state == state:
            return n
    return None


def settle(s):
    s.pad(0)
    for _ in range(14):     # anything still in the delay line plays out
        s.step()
    for _ in range(120):
        s.step()
        if s.fighter(0).state == WAIT:
            return
    raise SystemExit("Fox never came back to standing")


def main():
    s = Sim.match("lab", "fox", "marth", stage="final-destination", free=True)
    ctl = s.m.sym.addr("tm_ctl")
    for _ in range(120):
        s.step()
    settle(s)

    # --- input delay --------------------------------------------------------
    # Timed with a jump: its first state (jump squat) follows the press by a
    # fixed number of frames whatever came before, unlike a jab, which the
    # game chains into the next one.
    s.pad(0, ["X"])
    base = frames_until(s, JUMP_SQUAT)
    settle(s)
    check("a jump starts with no delay set", base is not None,
          "%s frames after the press" % base)
    for delay in (2, 5, 0, 10):
        s.m.w8(ctl + DELAY, delay)
        for _ in range(12):       # let the delay line fill with idle frames
            s.step()
        s.pad(0, ["X"])
        n = frames_until(s, JUMP_SQUAT)
        settle(s)
        check("delay %d holds the jump back %d frames" % (delay, delay),
              n == base + delay, "%s frames" % n)
    s.m.w8(ctl + DELAY, 0)
    for _ in range(12):
        s.step()

    # --- a profile ----------------------------------------------------------
    prof = ctl + PROFILES + 1 * PROFILE_SIZE
    s.m.w8(prof + P_USED, 1)
    for i, act in enumerate((1, 2, 3, 3, 5, 4, 4, 6, 0, 0, 0)):
        s.m.w8(prof + P_MAP + i, act)
    s.m.w8(prof + P_TAP_JUMP, 1)
    s.m.w8(prof + P_MAP + IN_Y, ACT_SPECIAL)      # Y is special
    s.m.w8(prof + P_MAP + IN_L, ACT_JUMP)         # L jumps

    s.pad(0, ["Y"])
    n = frames_until(s, JUMP_SQUAT, 8)
    settle(s)
    check("standard layout: Y jumps", n is not None)

    s.m.w8(ctl + PORT_PROFILE + 0, 1)
    s.pad(0, ["Y"])
    states = set()
    for _ in range(8):
        s.step()
        states.add(s.fighter(0).state)
    settle(s)
    check("profile: Y no longer jumps", JUMP_SQUAT not in states)
    check("profile: Y is special (Fox's blaster)",
          any(st >= 341 for st in states), "states %s" % sorted(states))

    s.pad(0, ["L"], l=1.0)
    n = frames_until(s, JUMP_SQUAT, 8)
    settle(s)
    check("profile: L jumps and does not shield", n is not None)

    s.pad(0, ["R"], r=1.0)
    states = set()
    for _ in range(10):
        s.step()
        states.add(s.fighter(0).state)
    settle(s)
    check("profile: R still shields", any(178 <= st <= 182 for st in states),
          "states %s" % sorted(states))

    s.m.w8(ctl + PORT_PROFILE + 0, 0)
    s.pad(0, ["Y"])
    n = frames_until(s, JUMP_SQUAT, 8)
    check("back on the standard profile: Y jumps", n is not None)

    # --- Slippi online ------------------------------------------------------
    # Slippi runs online matches in game mode 8 and supplies the pads itself;
    # there nothing may be remapped or held back. The mode number is the
    # first byte of the game's state machine.
    settle(s)
    mode_at = s.m.sym.addr("state_machine")
    mode = s.m.u8(mode_at)
    s.m.w8(ctl + PORT_PROFILE + 0, 1)             # Y is special in profile 1
    s.m.w8(ctl + DELAY, 6)
    s.m.w8(mode_at, 8)
    for _ in range(12):
        s.step()
    s.pad(0, ["Y"])
    n = frames_until(s, JUMP_SQUAT, 8)
    check("in Slippi's online game mode the pad is left alone: Y jumps, "
          "with no delay", n == base, "%s frames (no delay: %s)" % (n, base))
    s.m.w8(mode_at, mode)
    s.m.w8(ctl + PORT_PROFILE + 0, 0)
    s.m.w8(ctl + DELAY, 0)

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
