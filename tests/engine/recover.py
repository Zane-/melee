"""The opponent that recovers (tools/melee_engine/recover.py, the `recover`
behaviour; src/host: "launch", "route", "hitboxes"), on the headless game.

    python -u tests/engine/recover.py

- the launch is the game's own: the damage state its knockback gives, its
  hitstun, then the tumble;
- a route played ahead says where it ends and leaves the game as it was,
  and played for real it ends there, on that frame; one begun on the ledge
  ends on the stage, not on the ledge it began on;
- knocked off Final Destination by the edgeguard drill's hits, Fox, Marth,
  Sheik and Jigglypuff stand on the stage again when the player does
  nothing, by more than one kind of route, some of them by the ledge and
  up from it: it does not stop there;
- its stalls are among them: the shine (Fox), Dancing Blade (Marth), Pound
  (Jigglypuff), before the jump or the special that brings it in;
- the same seed flies the same route;
- hanging from the ledge, it gets onto the stage;
- the owner's example (2026-11-17): Fox charges Fire Fox at the ledge; 30
  frames into the charge the player jumps off the stage and back airs
  where he would arrive. Reacting in 3 frames he aims the stick onto the
  stage before the angle is read, and lands unhit; reacting in 30 he sees
  it only after the angle is read, and changes nothing before it;
- hit on its way, it goes on from where the hit left it, also when its
  decisions come back some frames after they were asked (as a fork's do:
  the client crashed on one that came back after a hit, 2026-11-17);
- `to` "ledge" with `tools` "jump" (the drill's first part): it comes to
  the ledge with its jump alone and stops there, and with the ledge held
  it falls;
- a script's `recover` step is checked by the format: its keys, their
  values.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import NONE, check, done, put, restart  # noqa: E402

from native import Native  # noqa: E402
from melee_engine import recover as RC  # noqa: E402
from melee_engine import recoveries as RV  # noqa: E402
from melee_engine import script as SC  # noqa: E402
from melee_engine.drill import Here  # noqa: E402

X = 0x400
CHARGE = (353, 354)           # Fox's Fire Fox, charging
LOCK = 43                     # the frame of it the angle is read on


class Late:
    """A thinker whose answers come `delay` frames after they were asked,
    as a fork's do while a person plays (thought out at once, in the game
    itself: `tick()` once a frame)."""

    def __init__(self, n, delay):
        self.n, self.delay = n, delay
        self.t = 0
        self.out = {}

    def tick(self):
        self.t += 1

    def lead_for(self, kind):
        return self.delay

    def submit(self, tag, fn, kind=None):
        self.out[tag] = (self.t + self.delay - 1, fn(self.n))

    def ready(self, tag):
        return tag in self.out and self.t >= self.out[tag][0]

    def result(self, tag):
        return self.out.pop(tag)[1]

    def forget(self, tag):
        self.out.pop(tag, None)


def fly(n, pilot, standin, budget=900):
    """`pilot` (port 1) flown against `standin(f, st)` (the player's raw
    pad), at most `budget` frames: the frames played."""
    for f in range(budget):
        st = n.state()
        mine = standin(f, st)
        raw = pilot.pad(st, mine)
        if pilot.done:
            return f
        put(n, 0, mine)
        put(n, 1, raw)
        n.step()
        if hasattr(pilot.think, "tick"):
            pilot.think.tick()
    return budget


def firefox(n, react, seed, think=None):
    """Fox, falling 62 units past the right ledge and 18 above it, with
    only his up special in the air; the player at the edge, their back to
    it, jumps out 30 frames into Fire Fox's charge, back airs on the 9th
    frame of the jump and falls. Returns the pilot, the frame of the jump,
    the frame the angle was read on, Fox's damage taken."""
    half = abs(n.ledge()[0])
    n.clean()
    n.seed(seed)
    n.place(0, half - 5.0, 0.0, -1, False, 0.0)
    n.place(1, half + 62.0, 18.0, -1, True, 60.0)
    put(n, 0, NONE)
    put(n, 1, NONE)
    n.step()
    pilot = RC.Pilot(think or Here(n), 1, 0, rng=random.Random(seed),
                     react=react, half=half, tools="up_b")
    seen = dict(charge=None, go=None, lock=None)

    def standin(f, st):
        me, them = st["p"][1], st["p"][0]
        if me["state"] in CHARGE and seen["charge"] is None:
            seen["charge"] = f
            seen["lock"] = f + LOCK - 1
        if seen["charge"] is not None and seen["go"] is None and \
                f - seen["charge"] >= 30:
            seen["go"] = f
        if seen["go"] is None or them["state"] in (252, 253):
            return NONE
        k = f - seen["go"]
        if k < 2:
            return (X, 127, 0, 0, 0, 0, 0)          # a short hop out
        if k < 8:
            return (0, 127, 0, 0, 0, 0, 0)
        if k == 8:                                  # a back air
            return (0, 0, -127, int(-127 * them["facing"]), 0, 0, 0)
        return (0, 0, -127, 0, 0, 0, 0)             # down, past the ledge
    start = n.state()["p"][1]["percent"]
    fly(n, pilot, standin)
    return pilot, seen["go"], seen["lock"], \
        n.state()["p"][1]["percent"] - start


def main():
    with Native() as n:
        n.start("fox", "marth", "final-destination", 1)
        half = abs(n.ledge()[0])

        # -- the launch -----------------------------------------------------
        n.place(0, half - 15, 0, -1, False, 0)
        n.launch(1, half - 8, 6, 60, 110, 45, 1, 1)
        n.step()
        p = n.state()["p"][1]
        check("the launch is the game's: knocked away in DamageFly, its "
              "hitstun the knockback's (110 units: 44 frames), the double "
              "jump kept", p["state"] in RC.DAMAGE and p["air"] and
              42 <= p["hitstun"] <= 44 and p["jumps"] == 1 and
              p["percent"] == 60,
              "state %d, hitstun %s, jumps %d" % (p["state"], p["hitstun"],
                                                  p["jumps"]))
        hs = int(p["hitstun"])
        n.step(hs + 1)
        p = n.state()["p"][1]
        check("then it tumbles, off the stage", p["state"] == RC.TUMBLE and
              p["x"] > half, "state %d at %.0f" % (p["state"], p["x"]))

        # -- a route --------------------------------------------------------
        n.clean()
        n.place(0, half - 15, 0, -1, False, 0)
        n.launch(1, half - 8, 6, 60, 110, 45, 1, 1)
        n.step()
        before = n.state()
        hs = int(before["p"][1]["hitstun"])
        IN = (0, -127, 0, 0, 0, 0, 0)
        plan = [(hs - 1, IN), (1, (X, -127, 0, 0, 0, 0, 0)), (20, IN),
                (1, (0x200, 0, 127, 0, 0, 0, 0)), (300, IN)]
        r = RC.route(n, 1, 0, plan, [(1, NONE)], 400, path=True)
        after = n.state()
        check("a route (a jump out of the tumble, Dolphin Slash 20 frames "
              "on) played ahead: the ledge caught; the game as it was",
              r.end == "ledge" and len(r.path) == r.frame and
              after["frame"] == before["frame"] and
              after["p"][1]["x"] == before["p"][1]["x"] and
              after["rng"] == before["rng"],
              "%r, %d places" % (r, len(r.path)))
        lost = RC.route(n, 1, 0, [(400, IN)], [(1, NONE)], 400)
        check("drifting alone, it is lost; how near the ledge it came is "
              "said", lost.end == "lost" and 5 < lost.ledge < 200,
              "%r, %.0f from the ledge" % (lost, lost.ledge))
        at = None
        for f, raw in enumerate(RC.frames(plan)):
            put(n, 1, raw)
            n.step()
            if n.state()["p"][1]["state"] in RC.LEDGE:
                at = f + 1
                break
        check("played for real it ends there, on that frame", at == r.frame,
              "%s against %d" % (at, r.frame))
        # (now it hangs, the stick let go: a route from the ledge)
        put(n, 1, NONE)
        n.step(12)
        up = RC.route(n, 1, 0, [(1, IN), (150, NONE)], [(1, NONE)], 200,
                      path=True)
        check("a route begun on the ledge (the stick toward the stage): up "
              "onto the stage and free, intangible on the way",
              up.end == "stage" and up.free > 0 and
              any(p[2] for p in up.path), "%r, free on %d" % (up, up.free))

        # -- recoveries, the player doing nothing ----------------------------
        byledge = 0
        for ch in ("fox", "marth", "sheik", "jigglypuff"):
            restart(n, "fox", ch)
            n.start("fox", ch, "final-destination", 1)
            memory, ends, kinds = {}, [], set()
            for i, kind in enumerate(("weak", "normal", "hard", "shallow",
                                      "normal", "shallow")):
                r = RV.recover_once(n, ch, kind, 1 if i % 2 == 0 else -1,
                                    1000 + 17 * i, memory=memory)
                ends.append(r["end"])
                kinds.add(r["kind"])
                byledge += r["grabs"] > 0
            check("%s stands on the stage again from six launches, either "
                  "ledge, by more than one kind of route" % ch,
                  all(e == "stage" for e in ends) and len(kinds) >= 2,
                  "%s; %s" % (" ".join(ends), ", ".join(sorted(
                      k or "?" for k in kinds))))
        check("some by the ledge, and up from it: it does not stop there",
              byledge >= 4, "%d of 24" % byledge)
        a = RV.recover_once(n, "jigglypuff", "normal", 1, 77)
        b = RV.recover_once(n, "jigglypuff", "normal", 1, 77)
        check("the same seed flies the same route",
              (a["end"], a["frames"], a["kind"]) ==
              (b["end"], b["frames"], b["kind"]),
              "%s in %d, %s; %s in %d, %s" % (
                  a["end"], a["frames"], a["kind"], b["end"], b["frames"],
                  b["kind"]))

        # -- its stalls -------------------------------------------------------
        for ch, stall, name in (("fox", "down_b", "the shine"),
                                ("marth", "side_b", "Dancing Blade"),
                                ("jigglypuff", "side_b", "Pound")):
            restart(n, "fox", ch)
            n.start("fox", ch, "final-destination", 1)
            memory, seen = {}, []
            for i in range(10):
                r = RV.recover_once(n, ch, "normal", 1 if i % 2 == 0 else -1,
                                    500 + 31 * i, memory=memory)
                seen += [k for k in r["via"]
                         if k.split(">")[0].startswith(stall + "+") or
                         ("+" + stall + "+") in k.split(">")[0] or
                         (ch == "jigglypuff" and stall in k)]
            check("%s stalls with %s before it comes in, some of ten "
                  "recoveries" % (ch, name), len(seen) >= 1,
                  "%d: %s" % (len(seen), ", ".join(sorted(set(seen)))))

        # -- from the ledge ---------------------------------------------------
        restart(n, "fox", "marth")
        n.start("fox", "marth", "final-destination", 1)
        got = []
        for px in (0.0, half - 6.0):
            n.clean()
            n.seed(5)
            n.place(0, px, 0.0, 1, False, 0.0)
            n.ledge(1, 40.0, "right")
            put(n, 0, NONE)
            put(n, 1, NONE)
            n.step()
            pilot = RC.Pilot(Here(n), 1, 0, rng=random.Random(5), half=half)
            f = fly(n, pilot, lambda f, st: NONE, 400)
            got.append((pilot.ended, f, " / ".join(pilot.via)))
        check("hanging from the ledge, it gets onto the stage: the player "
              "far away, and standing at the edge",
              all(g[0] == "stage" and g[2].startswith("ledge ")
                  for g in got), str(got))

        # -- the owner's example: Fire Fox, the angle changed ----------------
        restart(n, "fox", "fox")
        n.start("fox", "fox", "final-destination", 1)
        fast, slow = [], []
        for seed in (1, 2, 3, 4, 5, 6):
            pilot, go, lock, hit = firefox(n, 3, seed)
            first = pilot.decisions[0] if pilot.decisions else {}
            if first.get("end") != "ledge" or go is None:
                continue        # (it went for the stage from the start)
            changed = [d for d in pilot.decisions
                       if go <= d["asked"] < lock and not d.get("kept")]
            fast.append(dict(changed=changed, ended=pilot.ended, hit=hit,
                             go=go, lock=lock, seed=seed))
            pilot, go, lock, hit = firefox(n, 30, seed)
            changed = [d for d in pilot.decisions
                       if go is not None and go <= d["asked"] < lock]
            slow.append(dict(changed=changed, ended=pilot.ended, hit=hit))
        check("Fire Fox aimed at the ledge, the player standing at the "
              "edge; they jump off the stage to cover it 13 frames before "
              "the angle is read", len(fast) >= 3 and
              all(x["lock"] - x["go"] == 12 for x in fast),
              "; ".join("seed %d: jump %s, read %s" % (
                  x["seed"], x["go"], x["lock"]) for x in fast))
        went = [x for x in fast if x["changed"] and
                x["changed"][0]["end"] == "stage"]
        check("reacting in 3 frames: the stick is aimed onto the stage "
              "before the angle is read (within 5 frames of the jump), and "
              "it lands there unhit", len(went) >= 2 and
              all(x["changed"][0]["asked"] - x["go"] <= 5 and
                  x["ended"] == "stage" and x["hit"] == 0 for x in went),
              "; ".join("%s after %s, ended %s, %.0f%%" % (
                  x["changed"][0]["label"] if x["changed"] else "kept",
                  x["changed"][0]["asked"] - x["go"] if x["changed"]
                  else "-", x["ended"], x["hit"]) for x in fast))
        check("reacting in 30: nothing is decided before the angle is "
              "read", len(slow) >= 3 and
              all(not x["changed"] for x in slow),
              "; ".join("%d decisions, ended %s, %.0f%%" % (
                  len(x["changed"]), x["ended"], x["hit"]) for x in slow))

        # -- hit on its way ---------------------------------------------------
        restart(n, "fox", "marth")
        n.start("fox", "marth", "final-destination", 1)
        hits = []
        for think, name in ((None, "at once"), (Late(n, 6), "6 frames late")):
            for seed in (11, 12, 13):
                n.clean()
                n.seed(seed)
                n.place(0, 0.0, 0.0, 1, False, 0.0)
                n.launch(1, half - 8, 6, 40, 100, 50, 1, 1)
                put(n, 0, NONE)
                put(n, 1, NONE)
                n.step()
                pilot = RC.Pilot(think or Here(n), 1, 0,
                                 rng=random.Random(seed), half=half)
                again = int(n.state()["p"][1]["hitstun"]) + 14 + seed % 3

                def standin(f, st, again=again):
                    # (a hit, in place of the player's: knocked out again
                    # from where it is, 12% more, its jump as it is)
                    if f == again:
                        me = st["p"][1]
                        n.launch(1, me["x"], me["y"], me["percent"] + 12,
                                 70, 48, 1, int(me["jumps"]))
                    return NONE
                fly(n, pilot, standin)
                hits.append((name, pilot.ended, any(
                    w.startswith("hit:") for _, w in pilot.log)))
        check("hit again on its way (its answers at once, and 6 frames "
              "late as a fork's: one asked about a route the hit ended is "
              "not used), it goes on from where the hit left it",
              all(h[2] and h[1] in ("stage", "lost") for h in hits) and
              sum(h[1] == "stage" for h in hits) >= 4, str(hits))

        # -- the drill's first part: to the ledge, its jump alone -------------
        restart(n, "fox", "marth")
        n.start("fox", "marth", "final-destination", 1)
        out = {}
        for standin in ("stand", "ledge"):
            n.clean()
            n.seed(9)
            n.place(0, half - 15, 0, -1, False, 0)
            n.launch(1, half - 8, 6, 50, 88, 50, 1, 1)
            put(n, 0, NONE)
            put(n, 1, NONE)
            n.step()
            pilot = RC.Pilot(Here(n), 1, 0, rng=random.Random(9), half=half,
                             goal="ledge", tools="jump")
            player = RV.STANDINS[standin](1, half, random.Random(1))
            fly(n, pilot, lambda f, st: player.pad(st), 900)
            out[standin] = (pilot.ended, " / ".join(pilot.via))
        check('to "ledge", tools "jump": Marth comes to the ledge with his '
              "jump and stops there; with the ledge held he falls",
              out["stand"][0] == "ledge" and
              out["stand"][1] in ("jump>ledge", "drift>ledge") and
              out["ledge"][0] == "lost", str(out))

    # -- the format -----------------------------------------------------------
    ok = SC.problems(dict(script=[dict(do="recover", to="ledge",
                                       tools="jump,up_b", adapt=False,
                                       predict=False, budget=24)],
                          react=9))
    bad = SC.problems(dict(script=[dict(do="recover", to="platform",
                                        tools="wings", budget=2)]))
    check("a script's recover step: its keys taken, wrong values named",
          ok == [] and len(bad) == 3 and
          SC.problems(dict(script=[dict(do="edgeguard")])) != [],
          "%s; %s" % (ok, bad))
    return done()


if __name__ == "__main__":
    sys.exit(main())
