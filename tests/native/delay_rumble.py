"""Input delay and rumble on the native build.

    python tools/native_build.py && python tools/native_build.py --window
    python tests/native/delay_rumble.py

Input delay, as Slippi plays online: a live port's press reaches the game
N frames after it is read; `pads` (what the person holds) is not held
back, `pads game` (what the game is given) is, and the fighter acts that
much later. Rumble: the game's own motor command when a person's fighter
is hit (PADControlMotor), a port's rumble switched off, and a test pulse.

The live port here is the keyboard of a virtual display: no real
controller is opened, so nothing on the desk rumbles (a GameCube adapter
plugged into this machine is left alone: the adapter's motors must read
"never told" at the end).
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
import native  # noqa: E402
import window  # noqa: E402

WAIT = 14
A_BIT = 0x100

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def motors(n):
    """The game's motor command for each port (1 running)."""
    return [int(x) for x in n._cmd("rumble").split("|")[0].split()[-4:]]


def hit_rumbles(n):
    """Marth jabs Fox from up close: does the game run port 1's motor, and
    stop it again?"""
    n.place(0, 0, 0, facing=1)
    n.place(1, 12, 0, facing=-1)
    n.step(10)
    before = motors(n)
    n.pad(1, buttons=["A"])
    seen = []
    for _ in range(40):
        n.step()
        seen.append(motors(n))
        n.pad(1)
    n.step(120)
    return before, seen, motors(n), n.fighter(0).percent


def press_to(w, delay):
    """With `delay`, press A and count frames: until the person's pad has
    it, until the game's has it, and until the fighter leaves its wait."""
    w.delay(delay)
    w.key("x", False)
    w.step(20)
    seen = given = acted = None
    w.key("x")
    for i in range(1, 30):
        w.step()
        if seen is None and w.pads()[0]["buttons"] & A_BIT:
            seen = i
        if given is None and w.pads(game=True)[0]["buttons"] & A_BIT:
            given = i
        if acted is None and w.fighter(0).state != WAIT:
            acted = i
    w.key("x", False)
    w.step(60)
    return seen, given, acted


def main():
    with native.Native() as n:
        n.start("fox", "marth", "final-destination")
        before, seen, after, pct = hit_rumbles(n)
        on = [m[0] for m in seen]
        check("the game runs a person's motor when their fighter is hit",
              before[0] == 0 and 1 in on and pct > 0,
              "motor %s, %.0f%%" % ("".join(map(str, on)), pct))
        check("and stops it again", after[0] == 0, "motor %s" % after)
        # (Marth's motor runs too: his jab's own script has a rumble
        # command, ftaction.c, as on the console.)
        check("the ports with nobody on them stay still",
              all(m[2] == 0 and m[3] == 0 for m in seen),
              "port 2: %s" % "".join(str(m[1]) for m in seen))

    with window.Window() as w:
        w.start("fox", "marth", "final-destination")
        w.place(0, -30, 0, facing=1)
        w.place(1, 30, 0, facing=-1)
        w.step(20)
        w.live(0, "keyboard")
        w.step(5)

        check("no delay unless asked", w.delay() == 0)
        s0, g0, a0 = press_to(w, 0)
        check("delay 0: the game is given a press the frame it is read",
              s0 is not None and g0 == s0, "read %s, given %s" % (s0, g0))
        s2, g2, a2 = press_to(w, 2)
        check("delay 2: the game is given it two frames later",
              s2 is not None and g2 == s2 + 2,
              "read %s, given %s" % (s2, g2))
        check("and the fighter acts two frames later",
              None not in (a0, a2) and (a2 - s2) - (a0 - s0) == 2,
              "%s frames, against %s" % (
                  None if a2 is None else a2 - s2,
                  None if a0 is None else a0 - s0))
        s5, g5, _ = press_to(w, 5)
        check("delay 5: five frames", s5 is not None and g5 == s5 + 5,
              "read %s, given %s" % (s5, g5))
        check("a delay past 15 frames is 15", w.delay(40) == 15)

        w.delay(2)
        w.capture(True)
        w.key("x")
        w.step(6)
        held, given = w.pads()[0]["buttons"], w.pads(game=True)[0]["buttons"]
        w.key("x", False)
        w.capture(False)
        w.step(10)
        check("a menu's capture still keeps the press from the game",
              held & A_BIT and not given & A_BIT,
              "held %x, given %x" % (held, given))

        r = w.rumble()
        check("rumble is allowed on every port unless switched off",
              r["allowed"] == [1, 1, 1, 1], str(r))
        w.rumble(0, False)
        check("a port's rumble switches off",
              w.rumble()["allowed"][0] == 0)
        w.rumble(0, True)
        w.delay(0)
        before, seen, after, pct = hit_rumbles(w)
        check("in the window build too the game runs the motor on a hit",
              any(m[0] for m in seen), "%.0f%%" % pct)
        w.rumble_test(0, 30)
        w.step(2)
        r = w.rumble()
        check("the keyboard has no motor: nothing runs, even for a test",
              r["running"][0] == 0, str(r))
        check("the GameCube adapter was never told anything",
              r["adapter"] == [-1, -1, -1, -1], str(r))

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
