"""Behaviours and scripts (tools/melee_engine/behave.py, script.py) on the
headless game: an opponent written as a drill's "opponent": {"script"}.

    python -u tests/engine/script.py

The interpreter on its own (no game): a mix follows its weights over many
seeds and the same seed makes the same choices; a repeat loops while its
condition holds and stops; times; if/else; loop. Then, Fox the player
(port 0, a stand-in) against the opponent (port 1):

- footsies "outside" stays out of a standing player's range (searched
  again afterwards, frame by frame, with what the opponent really did) while
  it moves, and near its edge;
- `until: "approach"` fires when the stand-in dashes in, `react` frames
  after, not sooner;
- approach with lands "shield" meets a shielding player's shield;
- a contract, answer oos_down_b: it commits only to what a frame-4 shine out
  of shield answers, proved by playing the answer it found;
- punish lands damage on a player in landing lag;
- chain_grab regrabs (Marth's up throw on Fox at 0%);
- the same seed plays the same opponent, engine decisions and all;
- as while a person plays (60 frames a second, paced): decisions and
  the ranges thought out in forks of the game (fork.InFork);
- (when the engine has the scope's pivots: MELEE_HEADLESS=
  build/native-moves/melee_headless) an approach with pivot_ moves.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (FD_HALF, JUMP, NONE, SHIELD, check, done, drive,  # noqa
                    place, put, restart)

from melee_engine import sense as S  # noqa: E402
from melee_engine.script import Opponent  # noqa: E402

DASH_IN = (0, 127, 0, 0, 0, 0, 0)       # the player on the left
DAIR = (0, 0, 0, 0, -127, 0, 0)


def standing(state=14, x=-20.0):
    return dict(state=state, x=x, y=0.0, air=0, facing=1, percent=0.0,
                shield=60.0, hitlag=0, vx=0.0, vy=0.0)


def offline(script, frames, player=None, seed=0, react=15, loop=False):
    """A script played on constructed states (no game): the player's state
    on frame t is `player(t)`."""
    opp = Opponent(None, 1, 0, dict(script=script, react=react, loop=loop),
                   seed=seed, half=FD_HALF)
    for t in range(frames):
        p = player(t) if player else standing()
        opp.pad(dict(p=[p, dict(standing(x=30.0), facing=-1)]))
        if opp.over:
            break
    return opp


def interpreter():
    hold1 = {"do": "hold", "pad": "stand", "for": 1}
    mix = [{"mix": [{"weight": 3, "steps": [hold1]},
                    {"weight": 1, "steps": [hold1]}]}]
    firsts = [offline(mix, 2, seed=s).choices[0] for s in range(400)]
    share = firsts.count(0) / float(len(firsts))
    check("mix by weight over 400 seeds: 3 to 1 is about 75%",
          0.69 <= share <= 0.81, "%.1f%%" % (share * 100))
    a = offline(mix, 2000, seed=11, loop=True)
    b = offline(mix, 2000, seed=11, loop=True)
    c = offline(mix, 2000, seed=12, loop=True)
    share = a.choices.count(0) / float(len(a.choices))
    check("a looping mix: about 75% over a thousand choices, the same seed "
          "the same choices, another seed others",
          a.choices == b.choices and a.choices != c.choices and
          0.72 <= share <= 0.78,
          "%d choices, %.1f%%" % (len(a.choices), share * 100))

    hold7 = {"do": "hold", "pad": "stand", "for": 7}
    opp = offline([{"repeat": [hold7], "while": {"not": {"after": 30}}},
                   {"do": "hold", "pad": "shield"}], 60)
    began = [f for f, w in opp.trace if w == "do hold"]
    check("repeat while {not: {after: 30}}: five times (frames 0 to 28), "
          "then on", began == [0, 7, 14, 21, 28, 35] and
          opp.doing == "hold" and opp.cur.raw == SHIELD, str(began))
    opp = offline([{"repeat": [{"do": "hold", "pad": "stand", "for": 3}],
                    "times": 4}, {"do": "hold", "pad": "crouch",
                                  "for": 2}], 40)
    check("repeat times 4, then the next step, then the script is over",
          [f for f, w in opp.trace if w == "do hold"] == [0, 3, 6, 9, 12] and
          opp.over, str(opp.trace[-3:]))

    # repeat while the player shields (seen 15 frames late): the player
    # shields on frames 0 to 39
    def shields(t):
        return standing(179 if t < 40 else 14)
    opp = offline([{"repeat": [{"do": "hold", "pad": "stand", "for": 5}],
                    "while": "shielding"}, {"do": "hold", "pad": "crouch"}],
                  90, player=shields)
    began = [f for f, w in opp.trace if w == "do hold"]
    check("repeat while shielding: loops while the shield is seen (to frame "
          "39, seen 15 later) and stops at the first look after",
          began[:-1] == list(range(0, 55, 5)) and began[-1] == 55,
          "%d times, then on at %d" % (len(began) - 1, began[-1]))
    opp = offline([{"if": "shielding", "then": [hold1],
                    "else": [{"do": "hold", "pad": "crouch", "for": 1}]}],
                  3, player=shields)
    opp2 = offline([{"if": {"not": "shielding"}, "then": [hold1],
                     "else": [{"do": "hold", "pad": "crouch", "for": 1}]}],
                   3, player=shields)
    check("if / then / else, read when the step starts",
          opp.trace[0][1] == "if True" and opp2.trace[0][1] == "if False")
    opp = offline([{"repeat": [{"do": "hold", "pad": "stand",
                                "until": "grounded"}]}], 30)
    check("steps that take no frame cannot hang a frame (until true at once, "
          "for ever)", opp.frame == 29)
    opp = offline([hold7], 50, loop=True)
    check("loop: the script again when it ends",
          [f for f, w in opp.trace if w == "do hold"][:4] == [0, 7, 14, 21])


def footsies(n):
    from melee_engine.drill import Here
    place(n, -20, 35)
    snap = n.snapshot()
    try:
        opp = Opponent(Here(n), 1, 0, dict(script=[
            {"do": "footsies", "range": "outside"}]), seed=5, half=FD_HALF)
        t0 = time.time()
        frames, log = drive(n, opp, lambda f, st: NONE, 300)
        ms = (time.time() - t0) * 1000.0 / frames
        b = opp.cur
        # afterwards, frame by frame: could the standing player hit the
        # opponent within 12 frames, given what it really did next?
        n.restore(snap)
        inside, same = [], True
        for f, (st, mine, raw) in enumerate(log):
            now = n.state()
            same &= abs(now["p"][1]["x"] - st["p"][1]["x"]) < 1e-3
            if f % 2 == 0 and f + 13 < len(log):
                line = S.reach(n, 0, 1, 12,
                               their=[r for _, _, r in log[f:f + 13]])
                if line is not None:
                    inside.append((f, line.names))
            put(n, 0, mine)
            put(n, 1, raw)
            n.step()
        # the player's reach against a standing opponent: in 12 frames (the
        # range), and in 16 (what the body keeps out of: 4 frames to spare,
        # one look every 4 frames)
        reach = {}
        for k in (12, 16):
            for gap in range(20, 90, 2):
                place(n, -gap / 2.0, gap / 2.0)
                if S.reach(n, 0, 1, k, their=[NONE] * (k + 1)) is None:
                    reach[k] = gap
                    break
    finally:
        n.drop(snap)
    xs = [st["p"][1]["x"] for st, _, _ in log]
    gaps = [abs(st["p"][1]["x"] - st["p"][0]["x"]) for st, _, _ in log]
    moved = sum(abs(a - b) for a, b in zip(xs, xs[1:]))
    moving = sum(st["p"][1]["state"] in (15, 16, 17, 18, 20, 21, 23, 39, 40)
                 for st, _, _ in log)
    check("footsies outside: the replay is the same game", same)
    check("footsies outside: out of the standing player's range on every "
          "frame looked at (every other one of %d)" % frames, not inside,
          "in range at %s" % inside[:5])
    check("footsies outside: moving all along", moved > 150 and
          moving > frames // 2,
          "%.0f units covered, %d of %d frames moving (dash, walk, turn, "
          "crouch); %d dashes back; %.1f ms a frame" % (
              moved, moving, frames, b.backs, ms))
    mean = sum(gaps) / len(gaps)
    r12, r16 = reach.get(12), reach.get(16)
    check("footsies outside: near the edge, not running away (its closest "
          "within 20 units of the player's 16-frame reach, on average within "
          "40: its forward dashes must stay out too)",
          r12 is not None and r16 is not None and min(gaps) >= r12 and
          min(gaps) <= r16 + 20 and mean <= r16 + 40,
          "a standing opponent is out of reach from %s (12 frames), %s (16); "
          "distances %.0f to %.0f, %.0f on average; reach learnt %.1f" % (
              r12, r16, min(gaps), max(gaps), mean,
              opp.ctx.memory["their_reach"]))


def until_approach(n):
    from melee_engine.drill import Here
    place(n, -40, 30)
    dashed = []

    def standin(f, st):
        if st["p"][0]["state"] == 20 and not dashed:
            dashed.append(f)
        return DASH_IN if 60 <= f < 70 else NONE
    opp = Opponent(Here(n), 1, 0, dict(react=15, script=[
        {"do": "footsies", "range": "outside", "until": "approach"},
        {"do": "hold", "pad": "shield"}]), seed=2, half=FD_HALF)
    drive(n, opp, standin, 120, until=lambda f, st: opp.doing == "hold",
          what="the approach to be seen")
    ended = next((f for f, w in opp.trace if w.startswith("end footsies")),
                 None)
    check("until approach: fires when the player dashes in, react (15) "
          "frames after it is seen, no sooner",
          dashed and ended is not None and ended - dashed[0] == 15,
          "dash seen in the state on frame %s, the footsies ended on %s" % (
              dashed[0] if dashed else None, ended))


def shield_hit(st):
    p = st["p"][0]
    return p["hitlag"] > 0 and p["state"] in S.SHIELDING


def approach_shield(n):
    from melee_engine.drill import Here
    out = []
    ok = True
    for ch in ("marth", "captain-falcon", "falco"):
        restart(n, "fox", ch)
        for seed in (1, 2):
            place(n, -20, 25)
            put(n, 0, SHIELD)
            n.step(10)
            opp = Opponent(Here(n), 1, 0, dict(script=[
                {"do": "approach", "moves": "sh_,fh_,dash_attack,ftilt,dtilt,"
                 "fsmash,side_b", "lands": "shield"}]), seed=seed,
                half=FD_HALF)
            frames, log = drive(n, opp, lambda f, st: SHIELD, 240,
                                until=lambda f, st: shield_hit(st),
                                what="a hit on the shield")
            hit = shield_hit(n.state())
            pct = n.state()["p"][0]["percent"]
            ok &= hit and pct == 0
            line = opp.cur.opp.line if opp.cur else None
            out.append("%s %s%s" % (ch, line.names if line else "nothing",
                                    "" if hit else " MISSED"))
    check("approach lands shield: the line meets a shielding player's shield "
          "(three characters, two seeds)", ok, "; ".join(out))


def contract(n):
    from melee_engine.drill import Here
    answered = committed = 0
    out = []
    for ch in ("marth", "captain-falcon"):
        restart(n, "fox", ch)
        for seed in range(3):
            place(n, -20, 25)
            put(n, 0, SHIELD)
            n.step(10)
            opp = Opponent(Here(n), 1, 0, dict(react=15, script=[
                {"do": "approach",
                 "moves": "sh_,fh_,dash_attack,ftilt,dtilt,fsmash,side_b",
                 "lands": "shield",
                 "contract": {"answer": "oos_down_b", "within": 15}}]),
                seed=seed, half=FD_HALF)
            b = []
            pct0 = n.state()["p"][1]["percent"]

            def standin(f, st):
                # shielding, then the answer the contract found, from the
                # frame it was asked at
                a = b[0].answer if b and b[0].answer else None
                if a is None:
                    return SHIELD
                asked, pads = a
                i = b[0].opp.frame - asked
                return pads[i] if 0 <= i < len(pads) else NONE

            def until(f, st):
                if not b and opp.cur is not None:
                    b.append(opp.cur)
                return st["p"][1]["percent"] > pct0 or \
                    st["p"][0]["percent"] > 0
            drive(n, opp, standin, 300, until=until,
                  what="the answer to land")
            st = n.state()
            got = b and b[0].committed is not None
            committed += bool(got)
            shone = st["p"][1]["percent"] > pct0 and st["p"][0]["percent"] == 0
            answered += bool(got and shone)
            line = b[0].opp.line if b else None
            out.append("%s/%d %s%s" % (ch, seed, line.names if line else "-",
                                       "" if shone else " NOT ANSWERED"))
    check("contract oos_down_b: it commits (6 of 6), and each commitment is "
          "answered by the frame-4 shine out of shield it found, played",
          committed == 6 and answered == 6, "; ".join(out))


def punish(n):
    from melee_engine.drill import Here
    restart(n, "fox", "marth")
    dealt = []
    for seed in (0, 1):
        place(n, -15, 12)
        opp = Opponent(Here(n), 1, 0, dict(react=15, script=[
            {"do": "hold", "pad": "stand", "until": {"lag": 10}},
            {"do": "punish"}]), seed=seed, half=FD_HALF)
        lagged = []

        def standin(f, st):
            if st["p"][0]["state"] in (70, 71, 72, 73, 74) and not lagged:
                lagged.append(f)
            # a short hop down air, not L-cancelled
            return JUMP if f == 0 else DAIR if f == 6 else NONE
        hit_at = []

        def until(f, st):
            # 60 frames after the first damage (a stand-in that never DIs or
            # techs is juggled a long time: the punish lasts while it cannot
            # act)
            if st["p"][0]["percent"] > 0 and not hit_at:
                hit_at.append(f)
            return opp.over or (hit_at and f - hit_at[0] >= 60)
        drive(n, opp, standin, 240, until=until, what="the punish to land")
        began = next((f for f, w in opp.trace if w == "do punish"), None)
        dealt.append((n.state()["p"][0]["percent"], began,
                      lagged[0] if lagged else None))
    check("punish: lands damage on a player in landing lag (a short hop down "
          "air, not L-cancelled), started from what it saw",
          all(d > 0 and b is not None for d, b, _ in dealt),
          "; ".join("%.0f%%, the punish from frame %s (landing lag from "
                    "%s)" % d for d in dealt))


def chain_grab(n):
    """In the game the other tests played in: once Marth had attacked for
    real, the engine read the interrupt flag his attack left (the game
    clears it only as an attack begins) as "can act" in his grab, and every
    grab line ended on its second frame (engine.c, follow_interrupt; found
    2026-11-15, when this test played in a game of its own)."""
    from melee_engine.drill import Here
    restart(n, "fox", "marth")
    place(n, 0, 12)
    opp = Opponent(Here(n), 1, 0, dict(script=[
        {"do": "chain_grab", "throw": "uthrow"}]), seed=0, half=FD_HALF)
    beh = []

    def until(f, st):
        if not beh and opp.cur is not None:
            beh.append(opp.cur)
        return opp.over
    drive(n, opp, lambda f, st: NONE, 600, until=until,
          what="the chain to end")
    st = n.state()
    b = beh[0] if beh else None
    grabs = b.grabs if b else 0
    lines = [w for _, w in b.decisions if w] if b else []
    check("chain_grab: Marth's up throw on Fox at 0%, regrabbed (grab "
          "standing or out of a dash, and the scope's regrabs where the "
          "engine has them)", grabs >= 2,
          "%d grabs, %d throws, Fox at %.0f%%: %s" % (
              grabs, b.throws if b else 0, st["p"][0]["percent"],
              ", ".join(lines[:9])))


def same_seed(n):
    from melee_engine.drill import Here
    restart(n, "fox", "marth")
    place(n, -20, 30)
    snap = n.snapshot()
    runs = []
    try:
        for _ in range(2):
            n.restore(snap)
            opp = Opponent(Here(n), 1, 0, dict(react=15, script=[
                {"do": "footsies", "range": "outside", "for": 30},
                {"mix": [{"weight": 1, "steps": [
                    {"do": "approach", "moves": "sh_,dash_attack",
                     "lands": "any"}]},
                         {"weight": 1, "steps": [{"do": "retreat",
                                                  "for": 20}]}]}],
                loop=True), seed=9, half=FD_HALF)
            frames, log = drive(n, opp, lambda f, st: NONE, 200)
            runs.append(([r for _, _, r in log], list(opp.choices)))
    finally:
        n.drop(snap)
    check("the same seed plays the same opponent (footsies, a mix, engine "
          "decisions; 200 frames twice)", runs[0] == runs[1],
          "choices %s" % runs[0][1])


def forks(n):
    """As while a person plays: the frames at the console's 60 a second,
    every decision (the approach's, the ranges' searches) thought out in a
    forked copy of the game (fork.InFork), none waited for."""
    from melee_engine.fork import InFork
    restart(n, "fox", "marth")
    n.paced = True            # (as the window build: InFork forks)
    out = []
    try:
        think = InFork(n)
        place(n, -20, 25)
        put(n, 0, SHIELD)
        n.step(10)
        opp = Opponent(think, 1, 0, dict(react=15, script=[
            {"do": "footsies", "range": "outside", "for": 60},
            {"do": "approach", "moves": "sh_,dash_attack,ftilt",
             "lands": "shield"}]), seed=3, half=FD_HALF)
        frame, slow, t0 = 1.0 / 60, 0, time.time()
        due, b = t0, None
        for f in range(400):
            st = n.state()
            raw = opp.pad(st, SHIELD)
            put(n, 0, SHIELD)
            put(n, 1, raw)
            n.step()
            if opp.doing == "approach":
                b = opp.cur
            if shield_hit(n.state()):
                break
            due += frame
            wait = due - time.time()
            if wait > 0:
                time.sleep(wait)
            else:
                slow += 1
        hit = shield_hit(n.state())
        a = b.opp if b is not None else None
        out = dict(frames=f + 1, hit=hit, slow=slow, trace=opp.trace,
                   looks=opp.sense.searches, errors=think.errors,
                   late=a.late if a else None,
                   line=a.line.names if a and a.line else None,
                   leads=dict(think.leads))
    finally:
        n.paced = False
    check("in forks, at 60 frames a second: footsies then an approach onto "
          "the shield, nothing waited for in the frame", out.get("hit") and
          not out.get("errors"),
          "%s in %d frames (%d over their 16.7 ms); %d looks of the ranges; "
          "the thinker's leads %s; decisions late %s; %s" % (
              out.get("line"), out.get("frames", 0), out.get("slow", 0),
              out.get("looks", 0), out.get("leads"), out.get("late"),
              out.get("trace")))


def pivots(n):
    from melee_engine.drill import Here
    names = n._cmd("engine macros").split()
    if "pivot_fsmash" not in names:
        print("skip  approach with pivot_ moves (not in this build; enable "
              "with MELEE_HEADLESS=build/native-moves/melee_headless)",
              flush=True)
        return
    restart(n, "fox", "marth")
    place(n, -20, 25)
    opp = Opponent(Here(n), 1, 0, dict(script=[
        {"do": "approach", "moves": "pivot_", "lands": "hit"}]), seed=1,
        half=FD_HALF)
    drive(n, opp, lambda f, st: NONE, 240,
          until=lambda f, st: st["p"][0]["percent"] > 0,
          what="a pivot attack to hit")
    line = opp.cur.opp.line if opp.cur else None
    check("approach with pivot_ moves: a pivot attack that hits",
          line is not None and "pivot_" in line.names and
          n.state()["p"][0]["percent"] > 0, line and line.names)


def main():
    from native import Native
    t0 = time.time()
    interpreter()
    with Native() as n:
        restart(n, "fox", "marth")
        for test in (footsies, until_approach, approach_shield, contract,
                     punish, chain_grab, same_seed, forks, pivots):
            t = time.time()
            test(n)
            print("      (%s: %.0f s)" % (test.__name__, time.time() - t),
                  flush=True)
    print("(%.0f s)" % (time.time() - t0))
    return done()


if __name__ == "__main__":
    sys.exit(main())
