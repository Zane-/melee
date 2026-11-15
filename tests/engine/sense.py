"""The conditions (tools/melee_engine/sense.py): each on constructed states,
the player seen `react` frames late, the format's checking of them; then the
ranges and the lag against a live game.

    python -u tests/engine/sense.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import FD_HALF, NONE, check, done, place, put  # noqa: E402

from melee_engine import sense as S  # noqa: E402


def f(state=14, x=0.0, y=0.0, air=0, facing=1, percent=0.0, shield=60.0,
      hitlag=0):
    return dict(state=state, x=x, y=y, air=air, facing=facing,
                percent=percent, shield=shield, hitlag=hitlag, vx=0.0,
                vy=0.0)


def view(subj, prev=None, other=None, **kw):
    return S.View(subj, prev, other or f(x=40.0, facing=-1), half=FD_HALF,
                  **kw)


def pure():
    me = f(x=40.0, facing=-1)
    # distance, percent, shield
    v = view(f(x=10.0), other=me)
    check("distance: 30 apart is in [20, 40], not in [0, 20]",
          S.holds({"distance": [20, 40]}, v) and
          not S.holds({"distance": [0, 20]}, v))
    check("percent and shield_below",
          S.holds({"percent": [40, 60]}, view(f(percent=50))) and
          not S.holds({"percent": [0, 40]}, view(f(percent=50))) and
          S.holds({"shield_below": 30}, view(f(shield=20))) and
          not S.holds({"shield_below": 30}, view(f(shield=40))))
    # approach and retreat: the player on the left, the opponent at 40
    cases = [
        ("a dash toward", f(20, 0.0, facing=1), f(20, -2.0, facing=1), True),
        ("a run toward", f(21, 0.0, facing=1), f(21, -2.2, facing=1), True),
        ("a walk toward", f(15, 0.0, facing=1), f(15, -0.5, facing=1), True),
        ("a jump drifting toward", f(25, 0.0, air=1), f(25, -0.8, air=1),
         True),
        ("moving 1.5 units a frame toward in any state", f(42, 0.0),
         f(42, -1.5), True),
        ("standing", f(14, 0.0), f(14, 0.0), False),
        ("a dash away", f(20, 0.0, facing=-1), f(20, 2.0, facing=-1), False),
        ("a jump straight up", f(25, 0.0, air=1), f(25, 0.0, air=1), False),
    ]
    bad = [name for name, s, p, want in cases
           if S.holds("approach", view(s, p, me)) != want]
    check("approach: toward by dash, run, walk, a jump's drift, or more than "
          "a unit a frame; not standing, away or straight up", not bad,
          ", ".join(bad))
    away = [name for name, s, p, want in cases
            if name in ("a dash away",) and
            not S.holds("retreat", view(s, p, me))]
    check("retreat: a dash away", not away and
          not S.holds("retreat", view(f(20, 0.0, facing=1),
                                      f(20, -2.0, facing=1), me)))
    # committed and free
    committed = {"a forward smash": 60, "landing lag": 42,
                 "an aerial's landing": 70, "shield stun": 181,
                 "a roll": 233, "a spot dodge": 235, "hitstun": 75,
                 "tumble": 38, "lying down": 184, "a tech": 199,
                 "held": 224, "thrown": 241, "a ledge getup": 254,
                 "a special": 360, "helpless": 35}
    free = {"standing": 14, "a dash": 20, "a run": 21, "a walk": 15,
            "a jump": 25, "falling": 29, "a crouch": 40, "a shield": 179,
            "hanging on the ledge": 253, "a jump squat": 24}
    wrong = [k for k, s in committed.items()
             if not S.holds("committed", view(f(s)))]
    wrong += [k for k, s in free.items() if S.holds("committed", view(f(s)))]
    wrong += ["frozen in hitlag"] if not S.holds(
        "committed", view(f(14, hitlag=5))) else []
    check("committed: attacks, lag, stun, rolls, hitstun, tumble, down, "
          "techs, grabbed; not moving about or shielding", not wrong,
          ", ".join(wrong))
    check("{state: NAME}: the drill format's names (and a character's own)",
          S.holds({"state": "shield"}, view(f(181))) and
          S.holds({"state": "dash"}, view(f(20))) and
          not S.holds({"state": "dash"}, view(f(21))) and
          S.holds({"state": "shine"}, view(f(360), char="fox")) and
          S.holds({"state": "up_smash"}, view(f(342), char="ness")))
    check("shielding, airborne, grounded",
          S.holds("shielding", view(f(179))) and
          S.holds("shielding", view(f(181))) and
          not S.holds("shielding", view(f(14))) and
          S.holds("airborne", view(f(25, air=1))) and
          S.holds("grounded", view(f(14))))
    check("on_ledge, offstage, on_platform",
          S.holds("on_ledge", view(f(253, x=-85, y=-10))) and
          S.holds("offstage", view(f(29, x=-95, y=-20, air=1))) and
          S.holds("offstage", view(f(29, x=-40, y=-30, air=1))) and
          not S.holds("offstage", view(f(14, x=-80))) and
          S.holds("on_platform", view(f(14, x=0, y=27.2))) and
          not S.holds("on_platform", view(f(14))))
    check("lag: committed with at least N frames before it can act",
          S.holds({"lag": 10}, view(f(60), lag=12)) and
          not S.holds({"lag": 10}, view(f(60), lag=8)) and
          not S.holds({"lag": 10}, view(f(14), lag=12)) and
          not S.holds({"lag": 10}, view(f(60), lag=None)))
    check("ranges from what the searches found (unknown: neither in nor out)",
          S.holds("in_their_range", view(f(), ranges={"their": True})) and
          not S.holds("out_of_their_range", view(f(),
                                                 ranges={"their": True})) and
          S.holds("out_of_my_range", view(f(), ranges={"my": False})) and
          not S.holds("in_my_range", view(f())) and
          not S.holds("out_of_my_range", view(f())))
    mine = view(f(x=40, air=1, percent=80), other=f())
    v = view(f(), other=f(x=40), me_view=mine)
    check("me, not, any, all, after",
          S.holds({"me": "airborne"}, v) and
          not S.holds({"me": "grounded"}, v) and
          S.holds({"me": {"percent": [70, 90]}}, v) and
          S.holds({"not": "airborne"}, v) and
          S.holds({"any": ["airborne", "grounded"]}, v) and
          not S.holds({"all": ["airborne", "grounded"]}, v) and
          S.holds({"after": 10}, view(f(), after=10)) and
          not S.holds({"after": 10}, view(f(), after=9)))

    # seen react frames late: the player dashes in on frame 30
    sense = S.Sense(1, 0, react=15, half=FD_HALF)
    fired = None
    for t in range(80):
        x = -20.0 + max(0, t - 30) * 2.0
        p = f(20 if t >= 30 else 14, x, facing=1)
        sense.update(dict(p=[p, f(x=40.0, facing=-1)]))
        if fired is None and sense.test("approach"):
            fired = t
    check("a condition about the player is read react frames late: a dash "
          "on frame 30 is an approach on frame 45", fired == 45,
          "seen on %s" % fired)
    sense = S.Sense(1, 0, react=15, half=FD_HALF)
    seen = None
    for t in range(40):
        sense.update(dict(p=[f(), f(x=40.0, facing=-1,
                                    air=1 if t >= 10 else 0)]))
        if seen is None and sense.test({"me": "airborne"}):
            seen = t
    check("{me: C} is read at once", seen == 10, "seen on %s" % seen)

    # the format's checking
    states = ("shield", "dash")
    good = [S.problems(c, "c", states) for c in (
        "approach", {"distance": [10, 40]}, {"not": {"me": "airborne"}},
        {"any": ["committed", {"lag": 12}]}, {"state": "shield"},
        {"after": 30})]
    bad = [S.problems(c, "c", states) for c in (
        "aproach", {"distance": [40, 10]}, {"state": "nope"}, {"lag": -1},
        {"any": []}, {"me": "flying"}, {"distance": 3}, {"a": 1, "b": 2})]
    check("problems(): every word and key checked, every bad one named",
          not any(good) and all(bad),
          "; ".join(p[0] for p in bad if p))
    check("uses(): which searches a condition needs",
          S.uses({"any": ["in_their_range", {"not": {"lag": 3}}]}) ==
          {"their", "lag"} and S.uses({"me": "out_of_my_range"}) == {"my"}
          and S.uses("approach") == set())


def live():
    from native import Native
    from melee_engine.drill import Here
    with Native() as n:
        n.start("fox", "marth")
        # reach(): what the player can land within 12 frames
        place(n, -10, 10)
        near = S.reach(n, 0, 1)
        place(n, -40, 40)
        far = S.reach(n, 0, 1)
        check("reach: from 20 away Fox lands something within 12 frames, "
              "from 80 nothing", near is not None and far is None,
              "%s; %s" % (near and near.names, far and far.names))
        place(n, -20, 30)
        r20 = S.reach(n, 0, 1, their=[(0, 127 * -1, 0, 0, 0, 0, 0)] * 13)
        check("reach: Marth dashing in from 50 away walks into it",
              r20 is not None, r20 and r20.names)
        g = S.closest(n, 1, 0, [(0, -127, 0, 0, 0, 0, 0)] * 12)
        check("closest: the least distance while a plan plays (a dash in)",
              20 < g < 46, "%.1f" % g)

        # the ranges seen react frames late, the opponent's own at once
        place(n, -40, 40)
        sense = S.Sense(1, 0, react=15, think=Here(n), half=FD_HALF)
        sense.wants |= {"their", "my"}
        flips, t0 = {}, time.time()
        for t in range(60):
            if t == 20:
                place(n, -8, 8, settle=1)
            st = n.state()
            sense.update(st, NONE)
            sense.ask(None)
            for c in ("in_their_range", "in_my_range",
                      {"me": "in_their_range"}):
                k = str(c)
                if k not in flips and sense.test(c):
                    flips[k] = t
            if t == 10:
                out10 = sense.test("out_of_their_range") and \
                    sense.test("out_of_my_range")
            put(n, 0, NONE)
            put(n, 1, NONE)
            n.step()
        th = flips.get("in_their_range")
        check("80 apart: out of both ranges", out10)
        check("brought close on frame 20: in their range as seen 15 frames "
              "later (searched every 4 frames)", th is not None and
              35 <= th <= 35 + sense.cache,
              "on %s; the opponent's own view on %s; %d searches, %.1f s" % (
                  th, flips.get("{'me': 'in_their_range'}"), sense.searches,
                  time.time() - t0))
        me = flips.get("{'me': 'in_their_range'}")
        check("... and at once as the opponent's own ({me: ...})",
              me is not None and 20 <= me <= 20 + sense.cache)
        check("in my range too, seen as late",
              flips.get("in_my_range") is not None and
              35 <= flips["in_my_range"] <= 35 + sense.cache)

        # lag: Fox's forward smash, whiffed
        place(n, -40, 40)
        sense = S.Sense(1, 0, react=15, think=Here(n), half=FD_HALF)
        sense.wants.add("lag")
        lag_first = None
        on = []
        for t in range(70):
            st = n.state()
            sense.update(st, NONE)
            sense.ask(None)
            if t == 2:
                lag_first = S.lag_of(n, 0, 1)
            on.append(sense.test({"lag": 10}))
            put(n, 0, (0, 0, 0, 127, 0, 0, 0) if t == 0 else NONE)
            put(n, 1, NONE)
            n.step()
        first = on.index(True) if True in on else None
        last = len(on) - 1 - on[::-1].index(True) if True in on else None
        check("lag_of: a forward smash's frames left (39 in all)",
              lag_first is not None and 34 <= lag_first <= 39,
              "%s on its second frame" % lag_first)
        check("{lag: 10}: true once the smash is seen (react 15) and while "
              "10 frames or more are left", first is not None and
              15 <= first <= 17 and last is not None and 27 <= last <= 31,
              "frames %s to %s" % (first, last))


def main():
    t0 = time.time()
    pure()
    live()
    print("(%.0f s)" % (time.time() - t0))
    return done()


if __name__ == "__main__":
    sys.exit(main())
