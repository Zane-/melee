"""A Versus mode's moves on the native build (src/host/moves.c): shine
only, as the client's Shine Battle plays it, headless, in seconds.

    python tests/native/moves.py [--cpu-frames N]

Fox against Fox on Jungle Japes. With "moves 0 shine", a person's every
way to an attack is tried and none may reach the game: A, Z and the
C-stick standing, in the air and in shield; B with the stick in the
middle, up and to the side; A and B on the ledge. B with the stick down is
the shine, and held it stays a shine with the stick let go. Jumping,
shielding and air dodging still work. With "recovery" the up special comes
back and the neutral one stays out; with "all" the laser is back. Then the
game's own CPU, a level 9 Fox, fights under "shine" for --cpu-frames and
never starts any other attack, while under "all" it does (so the watch can
see one).

The owner, 2026-11-14: "shine only (any non shine move disabled, only
jumping, shield, air dodge, etc., no other aerials, etc.)".
"""
import argparse
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))

import native  # noqa: E402

WAIT, KNEEBEND, GUARD_ON, GUARD_OFF = 14, 24, 178, 180
ESCAPE_AIR, CLIFF_WAIT = 236, 253
# what the rule takes away: every attack (jabs to aerials), grabs and
# throws, the getup and ledge attacks, and Fox's specials but the shine
ATTACKS = set(range(44, 70)) | set(range(212, 223)) | {187, 195, 256, 257}
LASER, ILLUSION, FIREFOX = range(341, 347), range(347, 353), range(353, 360)
SHINE = range(360, 370)
NOT_SHINE = ATTACKS | set(LASER) | set(ILLUSION) | set(FIREFOX)
GONE = set(range(0, 13))            # dead, coming back
# where each Fox stands on the stage's two sides (the river is between)
HOME = ((-90, 60), (90, 60))

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cpu-frames", type=int, default=3600)
    args = ap.parse_args()
    n = native.Native()
    try:
        run(n, args)
    finally:
        n.close()
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


def states(n, frames, port=0):
    """The states port `port` is in over the next `frames` frames."""
    seen = []
    for _ in range(frames):
        n.step()
        seen.append(n.fighter(port).state)
    return seen


def idle(n, port=0, budget=300):
    """Pads let go; port `port` back in play (after a fall: the river
    carries a fighter off), put back where it started and standing
    still."""
    n.pad(port)
    for _ in range(budget):
        n.step()
        if n.fighter(port).state not in GONE:
            break
    else:
        raise RuntimeError("port %d never came back" % port)
    n.place(port, HOME[port][0], HOME[port][1], 1 if port == 0 else -1)
    for _ in range(budget):
        n.step()
        if n.fighter(port).state == WAIT:
            return
    raise RuntimeError("port %d never stood still (state %d)" % (
        port, n.fighter(port).state))


def press(n, port=0, after=40, **pad):
    """A press held for two frames (one would not be seen), then let go:
    the states over those frames and `after` more."""
    n.pad(port, **pad)
    seen = states(n, 2, port)
    n.pad(port)
    return seen + states(n, after, port)


def airborne(n, port=0, budget=60):
    """A full hop: frames until port `port` is in the air."""
    n.pad(port, buttons=["X"])
    for _ in range(budget):
        n.step()
        if n.fighter(port).airborne:
            break
    n.pad(port)
    n.step(4)
    return n.fighter(port).airborne


def run(n, args):
    n.start("fox", "fox", stage="jungle-japes", p2_human=True)
    check("Fox against Fox on Jungle Japes", n.fighter(0).fp and
          n.fighter(1).fp and n.fighter(1).ckind == n.fighter(0).ckind,
          n.fighter(0).summary())
    n.moves(0, "shine")
    n.moves(1, "shine")
    check("the host keeps each slot's rule", n._cmd("moves 0").split()[-1]
          == "shine" and n._cmd("moves 2").split()[-1] == "all")
    n.place(1, HOME[1][0], HOME[1][1], -1)
    n.place(0, HOME[0][0], HOME[0][1], 1)
    idle(n)

    def none_of(name, seen, banned=NOT_SHINE):
        bad = sorted(set(seen) & set(banned))
        check(name, not bad, "states %s" % bad if bad else "")

    none_of("A standing: no jab", press(n, buttons=["A"]))
    idle(n)
    none_of("Z standing: no grab", press(n, buttons=["Z"]))
    idle(n)
    none_of("the C-stick forward: no smash attack",
            press(n, cstick=(1, 0)))
    idle(n)
    none_of("the C-stick up: no up smash", press(n, cstick=(0, 1)))
    idle(n)
    none_of("A with the stick forward: no tilt or dash attack",
            press(n, buttons=["A"], stick=(0.6, 0)))
    idle(n)
    none_of("B in the middle: no laser", press(n, buttons=["B"]))
    idle(n)
    none_of("B up: no Firefox", press(n, buttons=["B"], stick=(0, 1)))
    idle(n)
    none_of("B to the side: no Illusion",
            press(n, buttons=["B"], stick=(1, 0)))
    idle(n)
    seen = press(n, buttons=["B"], stick=(0, -1), after=10)
    check("B down: the shine", any(s in SHINE for s in seen),
          str(sorted(set(seen))))
    idle(n)

    # the shine held: B stays down, the stick goes back to the middle
    n.pad(0, buttons=["B"], stick=(0, -1))
    n.step(2)
    n.pad(0, buttons=["B"])
    seen = states(n, 20)
    check("B held after the shine starts keeps it out (the stick let go)",
          all(s in SHINE for s in seen), str(seen))
    idle(n)

    seen = press(n, buttons=["X"], after=6)
    check("X still jumps", KNEEBEND in seen and n.fighter(0).airborne,
          str(sorted(set(seen))))
    idle(n)
    check("a full hop leaves the ground", airborne(n))
    seen = press(n, buttons=["A"], after=6)
    seen += press(n, cstick=(0, -1), after=6)
    seen += press(n, buttons=["Z"], after=6)
    none_of("in the air, A, the C-stick and Z: no aerial", seen)
    seen = press(n, buttons=["R"], stick=(1, 0), after=4)
    check("R in the air: an air dodge", ESCAPE_AIR in seen,
          str(sorted(set(seen))))
    idle(n)
    check("another hop", airborne(n))
    seen = press(n, buttons=["B"], stick=(0, -1), after=6)
    check("B down in the air: the shine there",
          any(s in SHINE for s in seen), str(sorted(set(seen))))
    idle(n)

    n.pad(0, buttons=["R"])
    seen = states(n, 10)
    check("R standing: the shield", any(GUARD_ON <= s < GUARD_OFF
                                        for s in seen), str(seen))
    n.pad(0, buttons=["R", "A"])
    seen = states(n, 2)
    n.pad(0, buttons=["R"])
    seen += states(n, 20)
    none_of("A in shield: no grab", seen)
    # out of shield, Fox's shine comes from a jump (B down in shield is a
    # spot dodge, and the jump's squat takes only up-B, a grab or an up
    # smash: ftCo_KneeBend_IASA): X, then B down as he leaves the ground
    n.pad(0, buttons=["R", "X"])
    seen = states(n, 2)
    n.pad(0)
    for _ in range(10):
        if n.fighter(0).airborne:
            break
        seen += states(n, 1)
    n.pad(0, buttons=["B"], stick=(0, -1))
    seen += states(n, 2)
    n.pad(0)
    seen += states(n, 20)
    check("a jump out of shield, then B down: the shine out of shield",
          KNEEBEND in seen and any(s in SHINE for s in seen),
          str(sorted(set(seen))))
    idle(n)

    for what, pad in (("A", dict(buttons=["A"])),
                      ("B with the stick down", dict(buttons=["B"],
                                                     stick=(0, -1))),
                      ("B", dict(buttons=["B"]))):
        n.ledge(0)
        n.step(30)
        hanging = n.fighter(0).state == CLIFF_WAIT
        seen = press(n, after=40, **pad)
        check("%s on the ledge: no ledge attack" % what, hanging and
              not set(seen) & {256, 257}, str(sorted(set(seen))))
        for _ in range(240):
            n.step()
            if n.fighter(0).state not in GONE and \
                    not n.fighter(0).airborne:
                break
        n.place(0, HOME[0][0], HOME[0][1], 1)
        idle(n)

    n.moves(0, "recovery")
    seen = press(n, buttons=["B"], stick=(0, 1), after=10)
    check("recovery: B up is Firefox again",
          any(s in FIREFOX for s in seen), str(sorted(set(seen))))
    for _ in range(300):
        n.step()
        if n.fighter(0).state == WAIT:
            break
    n.place(0, HOME[0][0], HOME[0][1], 1)
    idle(n)
    none_of("recovery: B in the middle is still no laser",
            press(n, buttons=["B"]))
    idle(n)
    n.moves(0, "all")
    seen = press(n, buttons=["B"], after=10)
    check("all: B in the middle is the laser again",
          any(s in LASER for s in seen), str(sorted(set(seen))))
    idle(n)

    # the game's CPU, a level 9 Fox, against Fox standing still
    for rule in ("shine", "all"):
        n.start("fox", "fox", stage="jungle-japes", p2_human=False)
        n.moves(0, "all")
        n.moves(1, rule)
        n.pad(0)
        seen = set()
        for _ in range(args.cpu_frames):
            n.step()
            f = n.fighter(1)
            if f.fp:
                seen.add(f.state)
        bad = sorted(seen & NOT_SHINE)
        if rule == "shine":
            check("the CPU under \"shine\" for %d frames: no other attack "
                  "or special" % args.cpu_frames, not bad,
                  "states %s" % bad if bad else
                  "%d shines" % len(seen & set(SHINE)))
        else:
            check("the CPU under \"all\" attacks (the watch sees one)",
                  bool(bad), "states %s" % bad[:12])
    n.moves(1, "all")


if __name__ == "__main__":
    main()
