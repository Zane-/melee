"""The damage a fighter takes off the screen is not a hit (the window
build: the headless one has no camera, and nothing is off its screen).

    python tools/native_build.py --window
    python -u tests/native/offscreen.py

A fighter that stays in the magnifier (off the screen) takes 1% for each
second there (fighter.c: Fighter's own count, `dmg.x1910`), with no hitlag
and no change of state. A route played ahead (`route`, src/host/ahead.c)
ended "hit" at any damage, and the recovering opponent's pilot
(tools/melee_engine/recover.py) dropped its route at any: knocked far out
or high, every way back of an opponent in the magnifier counted as a hit,
none was good, and it drifted to its death without a press (the owner,
2026-11-17: "many of the drills the CPU will just SD"). Checked here:

1. off the screen and high, Jigglypuff takes 1% with no hitlag, in the
   state it was in;
2. a route flown through that second ends on the stage, its damage taken
   0, not "hit";
3. the pilot goes on with its route over that 1% (nothing dropped), and
   stands on the stage again;
4. a route of 100 pads is played (48 was the most: a longer one, the Ice
   Climbers' side special mashed after a pre-roll, lost the whole
   decision).
"""
import os
import random
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import window  # noqa: E402
from melee_engine import recover as RC  # noqa: E402
from melee_engine.drill import Here  # noqa: E402

NONE = RC.NONE
IN = (0, -127, 0, 0, 0, 0, 0)        # the stick toward the stage
BUDGET = 400                          # frames a loop here may take

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""), flush=True)


def put(n, port, raw):
    b, lx, ly, cx, cy, lt, rt = raw
    n.h.pads[port].update(buttons=b, lx=lx, ly=ly, cx=cx, cy=cy, lt=lt,
                          rt=rt, connected=True)
    n._dirty.add(port)


def main():
    w = None
    try:
        w = window.Window(window=(1280, 720))
        w.step(30)
        w.start("fox", "jigglypuff", "final-destination", 1)
        half = abs(w.ledge()[0])

        def begin():
            """Jigglypuff far out and high, off the screen. (Placed again
            each time: a snapshot restored in the window build has no
            display, and its next frame is never drawn.)"""
            w.clean()
            w.seed(3)
            w.place(0, 0.0, 0.0, 1, False, 0.0)
            w.place(1, half + 150.0, 165.0, -1, True, 40.0)
            put(w, 0, NONE)
            put(w, 1, NONE)
            w.step()
        begin()
        # (Jigglypuff's jumps keep her up there: one every 30 frames)
        tick, was = None, w.state()["p"][1]
        for f in range(BUDGET):
            put(w, 1, (0x400 if f % 30 == 0 else 0, 0, 0, 0, 0, 0, 0))
            w.step()
            me = w.state()["p"][1]
            if me["percent"] > was["percent"]:
                tick = (f, me["percent"] - was["percent"], me["hitlag"],
                        me["state"], was["state"])
                break
            was = me
        check("off the screen and high: 1% taken with no hitlag, in the "
              "state it was in", tick is not None and
              abs(tick[1] - 1.0) < 1e-6 and tick[2] <= 0 and
              (tick[3] == tick[4] or tick[3] not in RC.DAMAGE),
              "frame, damage, hitlag, state, the state before: %s" % (tick,))
        begin()
        plan = [(f, (0x400, 0, 0, 0, 0, 0, 0) if i % 2 == 0 else NONE)
                for i, f in enumerate([1, 29] * 3)] + [(400, IN)]
        r = RC.route(w, 1, 0, plan, [(1, NONE)], 420)
        check("a route flown through that second ends on the stage, its "
              "damage 0, not hit", r.end in ("stage", "ledge") and
              r.taken == 0 and tick is not None and r.frame > tick[0],
              "ended %s on frame %d, taken %.1f" % (r.end, r.frame, r.taken))
        # (50 frames off the screen first: the damage comes 10 frames into
        # the pilot's flight)
        begin()
        for f in range(50):
            put(w, 1, (0x400 if f % 30 == 0 else 0, 0, 0, 0, 0, 0, 0))
            w.step()
        pilot = RC.Pilot(Here(w), 1, 0, rng=random.Random(2), half=half)
        hits, f = [], 0
        for f in range(BUDGET * 2):
            st = w.state()
            raw = pilot.pad(st, NONE)
            if pilot.done:
                break
            put(w, 0, NONE)
            put(w, 1, raw)
            w.step()
        hits = [x for x in pilot.log if x[1].startswith("hit")]
        took = w.state()["p"][1]["percent"] - 40.0
        check("the pilot flies on over the magnifier's damage: no route "
              "dropped as hit, and it stands on the stage again",
              pilot.ended == "stage" and not hits and took >= 1,
              "ended %s after %d frames, %.0f%% taken off the screen, log "
              "%s" % (pilot.ended, f, took, [x[1][:40] for x in pilot.log]))
        begin()
        long = [(1, (0x200 if i % 2 == 0 else 0, -127, 0, 0, 0, 0, 0))
                for i in range(100)] + [(300, IN)]
        try:
            r = RC.route(w, 1, 0, long, [(1, NONE)], 420)
            said = "ended %s on frame %d" % (r.end, r.frame)
        except Exception as e:
            r, said = None, repr(e)[:120]
        check("a route of 101 pads is played", r is not None, said)
    finally:
        if w is not None:
            w.close()
        left = window.leftovers()
        check("nothing left running", not left, str(left))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
