"""Answers ready before the player chooses (tools/melee_engine/chase.py,
the `chase` behaviour; src/host: the search's fresh=1, the lookahead's
hitstun), on the headless game.

    python -u tests/engine/chase.py

- thrown at the floor by Sheik, Fox has four options, each played ahead in
  the game: a tech in place, toward her, away, none; where each leaves him
  and the first frame he can act again are the game's;
- the table is made while the grab is still held, the throw played ahead
  as the opponent's next pads (the lookahead's "| pads"), and says what
  the ones made on the throw's first frame and at its release say, their
  frames that much later (the search's fresh=1: the throw the stance
  begins in is not the answer's contact);
- the opponent holds its grab until its table is back, then throws: the
  answers are there before the throw begins;
- Sheik reacting in 15 frames has a stance that covers all four surely;
  Captain Falcon, standing still, has not: the stances that move toward
  where Fox lands have;
- a throw that leaves hitstun to spare before the floor is no tech chase
  (Falco's down throw; Yoshi's): there is no table, and each of the
  drill's eleven throws is one, with all four options;
- played frame by frame against stand-ins who tech each way and jump on
  their first free frame, the chase catches all four at a reaction of 15
  with both; the first version (it stood, saw, then searched) caught
  fewer;
- a direction held through the throw changes the fall: the table is made
  again for it, and the chase still catches;
- a missed tech is chased as a second stage, its table of getups asked
  for when the bounce is seen: a roll away from it is caught;
- what the player chose before weighs the stance: against one who always
  techs in place, with a reaction too slow to cover that by reacting, the
  read of it; against one who has shown nothing, hardly ever;
- the same seed chases the same way;
- a script's `chase` step and the `chain_grab` step's `chase` are checked
  by the format.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import NONE, check, done, put  # noqa: E402

from native import Native  # noqa: E402
from melee_engine import chase as C  # noqa: E402
from melee_engine import chases as CS  # noqa: E402
from melee_engine import script as SC  # noqa: E402
from melee_engine import sense as S  # noqa: E402

STICK = {"dthrow": (0, -127), "fthrow": (127, 0), "bthrow": (-127, 0),
         "uthrow": (0, 127)}


def to_throw(n, throw="dthrow", percent=20.0, release=False, gap=12.0,
             held=False):
    """Fox (port 0) grabbed and thrown by port 1; stops on the first frame
    of the throw (`release`: on the first after it lets go; `held`: on the
    first the grab has him, nothing thrown yet). The frames the throw
    took, or None (the grab or the throw never came: 240 frames)."""
    n.clean()
    n.seed(1)
    n.place(0, 0.0, 0.0, -1, False, percent)
    n.place(1, -gap, 0.0, 1, False, 0.0)
    put(n, 0, NONE)
    put(n, 1, NONE)
    n.step(3)
    first = None
    for f in range(240):
        st = n.state()
        me, cpu = st["p"][0], st["p"][1]
        if held and me["state"] in S.CAPTURED:
            return 0
        if me["state"] in S.THROWN:
            if first is None:
                first = f
            if not release:
                return 0
        elif first is not None:
            return f - first
        if f in (2, 3):
            raw = (0x10, 0, 0, 0, 0, 0, 0)        # Z: a grab
        elif cpu["state"] == S.CATCH_WAIT:
            raw = (0,) + STICK[throw] + (0, 0, 0, 0)
        else:
            raw = NONE
        put(n, 1, raw)
        put(n, 0, NONE)
        n.step()
    return None


def kinds(row):
    return {k: c["kind"] for k, c in row["covers"].items()}


def sure_all(tab):
    return [s["name"] for s in tab["stances"]
            if all(c["kind"] == "sure" for c in s["covers"].values())]


def main():
    four = ["away", "in", "in place", "none"]
    with Native() as n:
        n.start("fox", "sheik", "final-destination", 1)
        # -- the options ------------------------------------------------------
        to_throw(n)
        before = n.state()["frame"]
        sit = C.tech_options(n, 1, 0)
        names = sorted(o["name"] for o in sit["options"]) if sit else []
        o = {x["name"]: x for x in sit["options"]} if sit else {}
        check("Sheik's down throw on Fox at 20%: a tech in place, in, away "
              "and none, each played ahead; the game left as it was",
              names == four and n.state()["frame"] == before and
              o["in place"]["free"] < o["away"]["free"] and
              o["in"]["free"] == o["away"]["free"] and
              abs(o["in place"]["x"] - sit["x"]) < 1.0 and
              abs(o["away"]["x"] - sit["x"]) > 20.0 and
              (o["in"]["x"] - sit["x"]) * (o["away"]["x"] - sit["x"]) < 0,
              "lands on frame %s at %.1f; %s" % (
                  sit and sit["land"], sit["x"] if sit else 0,
                  ", ".join("%s: free %d at %.1f" % (k, v["free"], v["x"])
                            for k, v in sorted(o.items()))))
        # -- the table: held, at the throw's first frame, at the release ------
        early = C.table(n, 1, 0, 15, every=True)
        took = to_throw(n, release=True)
        late = C.table(n, 1, 0, 15, every=True)
        to_throw(n, held=True)
        throw = C.throw_pad("dthrow", n.state()["p"][1]["facing"])
        before = n.state()["frame"]
        first = C.table(n, 1, 0, 15, every=True, throw=throw)

        def same(a, b, by):
            return a is not None and b is not None and \
                [s["name"] for s in a["stances"]] == \
                [s["name"] for s in b["stances"]] and all(
                    kinds(x) == kinds(y) and all(
                        x["covers"][k]["at"] is None or
                        x["covers"][k]["at"] - y["covers"][k]["at"] == by
                        for k in x["covers"])
                    for x, y in zip(a["stances"], b["stances"]))
        check("the table made on the throw's first frame is the one made at "
              "the release, %s frames later" % took,
              same(early, late, took) and
              early["land"] - late["land"] == took and
              early["cpu_free"] > took,
              "%d searches in %.0f ms; the opponent can act on frame %d" % (
                  early["searches"], early["wall"], early["cpu_free"])
              if early else "no table")
        at = first["throw_at"] if first else None
        check("made while the grab is held, the throw played ahead as its "
              "next pads: the same table again, its frames counted from "
              "the grab; the game left as it was",
              first is not None and at > 0 and same(first, early, at) and
              first["land"] - early["land"] == at and
              n.state()["frame"] == before and
              n.state()["p"][0]["state"] in S.CAPTURED and
              all(tuple(s["pads"][at - 1]) == throw
                  for s in first["stances"]),
              "thrown on frame %s; %d searches in %.0f ms" % (
                  at, first["searches"], first["wall"]) if first
              else "no table")
        check("Sheik, reacting in 15 frames, has a stance that covers all "
              "four surely", early is not None and bool(sure_all(early)),
              ", ".join(sure_all(early)) if early else "")
        to_throw(n)
        slow = C.table(n, 1, 0, 30, every=True)
        check("reacting in 30 she has none: something gets away",
              slow is not None and not sure_all(slow) and
              all(s["covers"]["in place"]["kind"] != "sure"
                  for s in slow["stances"] if not s["read"]),
              "; ".join("%s: %s" % (s["name"], "/".join(
                  str(kinds(s)[k])[:4] for k in four))
                  for s in (slow["stances"] if slow else [])[:4]))
        # -- what the player chose before -------------------------------------
        picks = {}
        for name, prior in (("habit", {"in place": 8}), ("none", {})):
            got = [C.choose(slow, [], prior, random.Random(seed))["name"]
                   for seed in range(40)]
            picks[name] = got.count("read in place")
        check("against a player who always techs in place she reads it "
              "(its cover begun before it is seen); against one who has "
              "shown nothing, hardly ever",
              picks["habit"] >= 30 and picks["none"] <= 8, str(picks))
        # -- the chase, frame by frame ----------------------------------------
        new = {k: CS.chase_once(n, k, "jump", react=15, seed=3)
               for k in four}
        old = {k: CS.chase_once(n, k, "jump", react=15, seed=3, ahead=False)
               for k in four}
        check("Sheik's chase at a reaction of 15 catches all four (the "
              "stand-in jumps on its first free frame); the first version, "
              "which stood, saw and then searched, fewer",
              all(r["end"] == "caught" for r in new.values()) and
              sum(r["end"] == "caught" for r in old.values()) < 4,
              "now %s; before %s" % (
                  "/".join("%s %s" % (k, new[k]["end"]) for k in four),
                  "/".join("%s %s" % (k, old[k]["end"]) for k in four)))
        words = " / ".join(w for _, w in new["away"]["log"])
        check("it holds its grab for its table, then throws: the answers "
              "are back before the throw begins",
              "thrown, its table back" in words, words[:160])
        again = CS.chase_once(n, "away", "jump", react=15, seed=3)
        check("the same seed chases the same way",
              again["stance"] == new["away"]["stance"] and
              again["frames"] == new["away"]["frames"] and
              again["how"] == new["away"]["how"],
              "%s, %s after %d frames" % (again["stance"],
                                          again["how"], again["frames"]))
        # -- a missed tech: the getups ----------------------------------------
        r = CS.chase_once(n, "none", "roll", react=24, seed=5)
        words = " / ".join(w for _, w in r["log"])
        check("a missed tech is a second stage: its getups' table asked "
              "for, and a roll away caught",
              r["end"] == "caught" and "getup:" in words and
              "roll away seen" in words, words[:150])

    with Native() as n:
        n.start("fox", "captain-falcon", "final-destination", 1)
        to_throw(n)
        tab = C.table(n, 1, 0, 15, every=True)
        stand = tab["stances"][0] if tab else None
        moving = [x for x in sure_all(tab) if x != "stand"] if tab else []
        check("Captain Falcon, standing still, does not cover all four; a "
              "stance that moves toward where Fox lands does",
              tab is not None and stand["name"] == "stand" and
              any(c["kind"] != "sure" for c in stand["covers"].values()) and
              bool(moving),
              "stand: %s; all four: %s" % (
                  "/".join(str(kinds(stand)[k]) for k in four) if stand
                  else "", ", ".join(moving)))
        new = {k: CS.chase_once(n, k, "jump", react=15, seed=3)
               for k in four}
        check("his chase at a reaction of 15 catches all four",
              all(r["end"] == "caught" for r in new.values()),
              "/".join("%s %s (%s)" % (k, new[k]["end"], new[k]["stance"])
                       for k in four))
        r = CS.chase_once(n, "in", "jump", react=15, seed=3, di=(-1, 0))
        words = " / ".join(w for _, w in r["log"])
        check("a direction held through the throw: the fall is another, "
              "the table is made again, and it still catches",
              r["end"] == "caught" and "off the path" in words, words[:150])

    # -- what is a tech chase -------------------------------------------------
    for cpu, throw in (("falco", "dthrow"), ("yoshi", "dthrow")):
        with Native() as n:
            n.start("fox", cpu, "final-destination", 1)
            ok = to_throw(n, throw) is not None
            sit = C.tech_options(n, 1, 0)
            check("%s's %s leaves Fox able to act before the floor: no "
                  "tech chase, no table" % (cpu, throw),
                  ok and sit is None and C.table(n, 1, 0, 15) is None,
                  "thrown: %s" % ok)
    bad = []
    for cpu in CS.TOP:
        throw, percent = CS.THROWS[cpu]
        with Native() as n:
            n.start("fox", cpu, "final-destination", 1)
            got = None
            for gap in (12.0, 9.0, 15.0):
                if to_throw(n, throw, float(percent), gap=gap) is not None:
                    got = C.tech_options(n, 1, 0)
                    break
            if got is None or len(got["options"]) != 4:
                bad.append("%s %s at %d%%: %s" % (
                    cpu, throw, percent,
                    got and [o["name"] for o in got["options"]]))
    check("each of the drill's eleven throws is a tech chase with all four "
          "options", not bad, "; ".join(bad))

    # -- the format -----------------------------------------------------------
    ok = SC.problems(dict(react=24, script=[
        dict(do="chain_grab", throw="dthrow", chase=True),
        dict(do="chase", throw="dthrow", ahead=True, reads=False,
             moves="grab,dash_grab"),
        dict(do="chain_grab", throw="fthrow", times=1)]))
    bad = SC.problems(dict(script=[
        dict(do="chain_grab", throw="sideways", chase="yes", times=0),
        dict(do="chase", ahead="soon", throw="down")]))
    check("a script's chase steps: their keys taken, wrong values named",
          ok == [] and len(bad) == 5, "%s; %s" % (ok, bad))
    return done()


if __name__ == "__main__":
    sys.exit(main())
