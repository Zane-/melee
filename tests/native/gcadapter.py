"""The GameCube adapter reader (src/host/gcadapter.c).

    python tests/native/gcadapter.py

Reports as the adapter sends them are handed to the decoder: which ports
have a controller, every button, the sticks and triggers measured from the
rest position the controller had when first seen, a controller unplugged
and plugged in again. Then, if an adapter is plugged into this machine and
free, the game is asked to open it and read whatever is on it: that part
can only show that it opens and reads; nobody presses anything.
"""
import sys
import time

sys.path.insert(0, "tools/melee_native")
import window  # noqa: E402
from native import NativeError  # noqa: E402

A, B, X, Y, START = 0x100, 0x200, 0x400, 0x800, 0x1000
Z, R, L = 0x10, 0x20, 0x40
LEFT, RIGHT, DOWN, UP = 1, 2, 4, 8
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def report(*ports):
    """A 37-byte report: for each port (status, buttons 1, buttons 2, stick
    x, y, C x, y, L, R), or None for an empty port."""
    out = [0x21]
    for p in list(ports) + [None] * (4 - len(ports)):
        out += list(p) if p else [0x04, 0, 0, 0x80, 0x80, 0x80, 0x80, 0, 0]
    return "".join("%02x" % b for b in out)


def decode(w, hexed):
    words = w._cmd("gcc " + hexed).split()
    out = []
    for i in range(4):
        v = words[i * 8:i * 8 + 8]
        out.append(dict(there=v[0] == "1", buttons=int(v[1], 16),
                        lx=int(v[2]), ly=int(v[3]), cx=int(v[4]),
                        cy=int(v[5]), lt=int(v[6]), rt=int(v[7])))
    return out


def main():
    rest = (0x14, 0, 0, 0x7f, 0x7f, 0x7f, 0x7f, 0x07, 0x00)
    with window.Window() as w:
        w.step(5)
        w._cmd("gcc forget")
        p = decode(w, report(rest))
        check("a controller on port 1, nothing on the others",
              [x["there"] for x in p] == [True, False, False, False])
        check("what it reads when first seen is its rest: all zero",
              all(p[0][k] == 0 for k in ("buttons", "lx", "ly", "cx", "cy",
                                         "lt", "rt")), str(p[0]))
        p = decode(w, report((0x14, 0x01 | 0x08, 0x01 | 0x02 | 0x08, 0xD0,
                              0x30, 0x10, 0xF0, 0xC8, 0x07)))[0]
        check("buttons A, Y, Start, Z and L",
              p["buttons"] == A | Y | START | Z | L, hex(p["buttons"]))
        check("sticks and triggers are counted from the rest position",
              (p["lx"], p["ly"], p["cx"], p["cy"], p["lt"], p["rt"]) ==
              (0xD0 - 0x7f, 0x30 - 0x7f, 0x10 - 0x7f, 0xF0 - 0x7f,
               0xC8 - 7, 7 - 0), str(p))
        p = decode(w, report((0x14, 0x02 | 0x04 | 0xF0, 0x04, 0x7f, 0x7f,
                              0x7f, 0x7f, 0x07, 0x00)))[0]
        check("buttons B, X, R and the four of the D-pad",
              p["buttons"] == B | X | R | LEFT | RIGHT | DOWN | UP,
              hex(p["buttons"]))
        p = decode(w, report((0x14, 0, 0, 0xFF, 0x00, 0x7f, 0x7f, 0x00,
                              0xFF)))[0]
        check("the ends of the range, and a trigger below its rest",
              (p["lx"], p["ly"], p["lt"], p["rt"]) == (127, -127, 0, 255),
              str(p))
        decode(w, report(None))
        p = decode(w, report((0x14, 0, 0, 0x90, 0x70, 0x80, 0x80, 0x20,
                              0x20)))[0]
        check("unplugged and plugged in again, it takes a new rest",
              p["there"] and (p["lx"], p["ly"], p["lt"]) == (0, 0, 0),
              str(p))
        p = decode(w, report(None, None, (0x22, 0x01, 0, 0x80, 0x80, 0x80,
                                          0x80, 0, 0)))
        check("a wireless controller on port 3",
              [x["there"] for x in p] == [False, False, True, False] and
              p[2]["buttons"] == A)
        try:
            w.live(0, "gcc5")
            check("there is no fifth port", False)
        except NativeError:
            check("there is no fifth port", True)

        # the real thing, if there is one
        w._cmd("gcc forget")
        said = w.devices()
        for _ in range(10):
            if "looking" not in said:
                break
            time.sleep(0.2)
            w.step(5)
            said = w.devices()
        print("      this machine: " + said)
        if "open" in said and "controllers on its ports" in said:
            port = int(said.split("controllers on its ports")[1].split(
                ".")[0].split()[0])
            w.live(0, "gcc%d" % port)
            w.step(10)
            p = w.pads()[0]
            check("the game opens the adapter and reads the controller on "
                  "its port %d" % port,
                  all(abs(p[k]) <= 20 for k in ("lx", "ly", "cx", "cy")),
                  "at rest unless someone is holding it: %s" % p)
        else:
            print("      (no adapter with a controller that this could "
                  "open: the live read was not tried)")
    left = window.leftovers()
    check("nothing left running", not left, str(left))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
