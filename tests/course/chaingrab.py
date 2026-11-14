"""Fox's chain grab goes on until the player drops it, on the native build
(headless).

    python tests/course/chaingrab.py

A scripted player who grabs, up throws and regrabs as the CPU comes back
down to the floor (the CPU's DI held at none) chains Falco several times at
low percent, and the attempt ends only when the chain is dropped, saying how
long it was. Thrown and not regrabbed, Falco comes down in tumble: he techs
or lies there (the attempt goes on: a tech chase), and the chain ends when
he gets away.
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from native import Native  # noqa: E402
from melee_course import engine, registry  # noqa: E402
from melee_course.engine import (  # noqa: E402
    Z, CATCH_PULL, CATCH_DASH_PULL, CATCH_WAIT, THROW_F, THROW_LW)

HOLDING = (CATCH_PULL, CATCH_DASH_PULL, CATCH_WAIT)   # an up throw from here
THROWS = range(THROW_F, THROW_LW + 1)

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def cook(game, percent, scenario=1, regrab=True):
    """One attempt with a player who grabs, up throws and regrabs as the CPU
    comes back down to the floor (the CPU does not DI: the spacing is not
    what is tested); the result and the CPU states seen."""
    d = registry.get("fox-uthrow-chaingrab")
    setup = d.setup

    def no_di(c):
        setup(c)
        d.th.pick_di = lambda c: None    # DI 0: the spacing is not tested
        d.th.di = 0
    d.setup = no_di
    s = engine.Session(d, game, live=False, seed=3,
                       options={0: percent, 1: 2},
                       common={engine.OPT_SCENARIO: scenario})
    seen = set()
    last = dict(state=None, released=None)

    def each(g, frame):
        c = s.c
        seen.add(c.cpu_state)
        if last["state"] in THROWS and c.state not in THROWS:
            last["released"] = frame
        last["state"] = c.state
        holding = c.state in HOLDING
        # the regrab as he comes down (the grab takes about 7 frames to come
        # out: he lands in them), once per throw
        low = c.cpu.pos[1] < 14 and c.cpu.vel[1] <= 0 and \
            abs(c.cpu.pos[0] - c.me.pos[0]) < 12
        grab = frame < 3 or (regrab and last["released"] is not None and
                             low and not last.get("tried"))
        if grab and frame >= 3:
            last["tried"] = True
        if c.state in THROWS:
            last["tried"] = False
        # a throw takes a fresh press of the stick: up every other frame
        up = holding and frame % 2 == 0
        s.set_player_pad(buttons=Z if grab else 0, ly=127 if up else 0)
    return s.run(each_frame=each), seen


def main():
    with Native() as game:
        r, seen = cook(game, 0)
        regrabs = r.get("report", {}).get("regrabs", 0)
        words = r.get("full_words", "").replace("\n", " / ")
        check("at 0% Falco is chained more than once, and the attempt "
              "ends when it is dropped", regrabs >= 2 and
              "Dropped" in words, words)
        r, seen = cook(game, 0, regrab=False)
        downed = sorted(st for st in seen if 183 <= st <= 201)
        words = r.get("full_words", "").replace("\n", " / ")
        check("thrown and not regrabbed, he comes down in tumble and techs "
              "or lies there, and the chain ends only when he is away",
              bool(downed) and "Dropped" in words and
              ("jumped" in words or "free" in words),
              "%s; down/tech states: %s" % (words, downed))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
