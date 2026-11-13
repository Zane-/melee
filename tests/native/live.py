"""A person at the controls of the native window build, checked without a
person or a desktop: the game runs on a virtual display, keys are pressed
on that display, and the fighter has to do what the keys say.

    python tests/native/live.py

What this covers: a live port reading the keyboard through SDL, pacing to
the console's speed, scripted and live ports side by side, handing a port
back to a script. What it cannot cover: a real controller (there is none to
press here) and anything about how it feels.
"""
import os
import sys
import time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
import native  # noqa: E402
import window  # noqa: E402

WAIT = 14
WALK = (15, 16, 17)

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def main():
    try:
        with window.Window() as w:
            w.start("fox", "marth", "final-destination")
            w.place(0, -30, 0, facing=1)
            w.place(1, 30, 0, facing=-1)
            w.step(20)
            x0 = w.fighter(0).pos[0]

            # nothing pressed: a live port stands still
            w.live(0, "keyboard")
            w.step(30)
            f = w.fighter(0)
            check("a live port with no key held stands still",
                  f.state == WAIT and abs(f.pos[0] - x0) < 0.01,
                  "state %d, moved %.2f" % (f.state, f.pos[0] - x0))

            # the stick
            w.key("Right")
            w.step(30)
            w.key("Right", False)
            x1 = w.fighter(0).pos[0]
            check("the right arrow runs the fighter to the right",
                  x1 - x0 > 10, "moved %.1f" % (x1 - x0))
            w.step(40)
            x2 = w.fighter(0).pos[0]
            w.step(20)
            f = w.fighter(0)
            check("and it stops when the key is let go",
                  f.state == WAIT and abs(f.pos[0] - x2) < 0.01,
                  "state %d" % f.state)

            # a light push walks instead of dashing
            w.key("Shift_L")
            w.key("Left")
            w.step(30)
            f = w.fighter(0)
            slow = f.pos[0] - x2
            w.key("Left", False)
            w.key("Shift_L", False)
            w.step(40)
            check("with shift held the push is light: a walk, not a run",
                  f.state in WALK and slow < -0.5 and
                  abs(slow) < abs(x1 - x0) / 2,
                  "state %d, moved %.1f against %.1f" % (
                      f.state, slow, x1 - x0))

            # a button
            before = w.fighter(0).state
            w.key("x")
            w.step(3)
            w.key("x", False)
            w.step(2)
            f = w.fighter(0)
            check("X (the A button) starts an attack",
                  f.state != before and 44 <= f.state <= 70,
                  "state %d" % f.state)
            w.step(60)

            # a script plays the other port at the same time
            y0 = w.fighter(1).pos[1]
            w.pad(1, buttons=["X"])
            w.key("c")
            w.step(8)
            w.pad(1)
            w.key("c", False)
            w.step(4)
            a, b = w.fighter(0), w.fighter(1)
            check("the keyboard's fighter and the script's both jump",
                  a.airborne and b.airborne and b.pos[1] > y0,
                  "airborne %s %s" % (a.airborne, b.airborne))
            w.step(90)

            # the console's speed
            w.pace(True)
            w.step(5)
            t = time.time()
            w.step(120)
            took = time.time() - t
            check("120 paced frames take two seconds",
                  1.9 < took < 2.2, "%.2f s" % took)
            w.pace(False)
            t = time.time()
            w.step(120)
            fast = time.time() - t
            check("and unpaced they do not", fast < 1.5, "%.2f s" % fast)

            # handing the port back
            w.live(0, "off")
            w.key("Right")
            w.pad(0)
            w.step(30)
            w.key("Right", False)
            f = w.fighter(0)
            check("a port taken back ignores the keyboard",
                  f.state == WAIT, "state %d" % f.state)
            w.pad(0, stick=(-1, 0))
            w.step(20)
            check("and obeys the script again",
                  w.fighter(0).pos[0] < f.pos[0] - 5)

            # a controller that is not there
            w.pad(0)
            w.live(0, "pad3")
            w.step(20)
            check("a port given a controller that is not plugged in is "
                  "neutral", w.fighter(0).state in (WAIT, 18, 19, 20, 21, 22,
                                                    23, 24),
                  "state %d" % w.fighter(0).state)
            try:
                w.live(0, "mouse")
                check("an unknown source is refused", False)
            except native.NativeError:
                check("an unknown source is refused", True)
    finally:
        left = window.leftovers()
        check("nothing left running", not left, str(left))

    with native.Native() as h:
        try:
            h._cmd("live 0 auto")
            check("the headless build says it has no window", False)
        except native.NativeError as e:
            check("the headless build says it has no window",
                  "window build" in str(e))

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
