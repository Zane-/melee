"""Setting up a situation on the native build: fighters put where a scenario
needs them (src/host/setup.c).

    python tools/native_build.py
    python tests/native/place.py
"""
import random
import sys

sys.path.insert(0, "tools/melee_native")
from native import Native, NativeError  # noqa: E402

WAIT, FALL = 14, 29
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


def play(n, seed, frames):
    rng = random.Random(seed)
    out = []
    for _ in range(frames):
        for port in (0, 1):
            if rng.random() < 0.2:
                n.pad(port,
                      buttons=[b for b in "ABXZR" if rng.random() < 0.12],
                      stick=(rng.choice((-1, -0.5, 0, 0.5, 1)),
                             rng.choice((-1, 0, 0, 1))),
                      cstick=(rng.choice((-1, 0, 0, 0, 1)), 0))
        n.step()
        s = n.state()
        out.append((s["rng"], s["p"], s["items"]))
    return out


def setup(n):
    """The situation under test: both on the floor, close, Marth hurt."""
    n.pad(0)
    n.pad(1)
    n.place(0, -12.0, 0.0, facing=1)
    n.place(1, 12.0, 0.0, facing=-1, percent=40.0)
    n.seed(7)
    n.step()


def main():
    with Native() as n:
        n.start("fox", "marth")
        setup(n)
        a, b = n.fighter(0), n.fighter(1)
        # (Final Destination's floor is at 0.0001, not 0)
        check("both stand where they were put, facing each other",
              a.pos[0] == -12.0 and b.pos[0] == 12.0 and
              abs(a.pos[1]) < 0.001 and abs(b.pos[1]) < 0.001 and
              a.facing == 1 and b.facing == -1 and a.state == WAIT and
              b.state == WAIT and not a.airborne and not b.airborne,
              "%s | %s" % (a.summary(), b.summary()))
        check("with the damage asked for", a.percent == 0 and b.percent == 40)

        n.pad(0, buttons=["A"])
        n.step(3)
        n.pad(0)
        check("a placed fighter acts at once", n.fighter(0).state == 44,
              "state %d" % n.fighter(0).state)
        n.step(60)

        # The same situation after two different pasts: the fighters are
        # the same. What else is about (effects still playing, where the
        # random stream stands after them) is not touched by a placement, so
        # to repeat a situation exactly it is kept as a snapshot.
        setup(n)
        fighters = n.state()["p"]
        here = n.snapshot()
        first = play(n, 3, 400)
        play(n, 99, 500)                 # anything: hits, falls
        setup(n)
        check("the same placement after another past gives the same "
              "fighters", n.state()["p"] == fighters)
        n.restore(here)
        again = play(n, 3, 400)
        same = next((i for i in range(400) if first[i] != again[i]), None)
        check("a set-up situation kept as a snapshot plays the same again",
              same is None, "" if same is None else
              "differs at frame %d of 400" % same)

        n.pad(0)
        n.pad(1)
        n.place(0, 0.0, 30.0, air=True, percent=80.0)
        n.step()
        f = n.fighter(0)
        check("put in the air: falling from there", f.airborne and
              f.state == FALL and 25 < f.pos[1] <= 30 and f.percent == 80,
              f.summary())
        for _ in range(120):
            n.step()
            if not n.fighter(0).airborne:
                break
        check("and it lands", not n.fighter(0).airborne and
              abs(n.fighter(0).pos[1]) < 0.001, n.fighter(0).summary())

        try:
            n.place(0, 400.0, 0.0)
            refused = False
        except NativeError:
            refused = True
        check("nowhere to stand is refused", refused)

    runs = []
    for _ in (0, 1):
        with Native() as n:
            n.start("fox", "marth")
            setup(n)
            runs.append(play(n, 3, 400))
    check("set up in two fresh processes, it is the same game",
          runs[0] == runs[1])

    with Native() as n:
        n.start("fox", "marth", stage="battlefield")
        n.place(0, -38.0, 40.0)
        n.place(1, 0.0, 70.0)
        n.step()
        a, b = n.fighter(0), n.fighter(1)
        check("on Battlefield: the floor below the point is a platform",
              abs(a.pos[1] - 27.2) < 0.01 and abs(b.pos[1] - 54.4) < 0.01 and
              not a.airborne and not b.airborne,
              "%s | %s" % (a.summary(), b.summary()))
        n.step(30)
        check("and they stay on it", abs(n.fighter(0).pos[1] - 27.2) < 0.01
              and abs(n.fighter(1).pos[1] - 54.4) < 0.01)

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
