"""fox-anti-air against Opponent: Engine (tools/melee_engine/jumpin.py):
both fighters move; the opponent chooses its moment, plans its jump-in by
search, and jumps only when the player has an anti-air.

    python tools/native_build.py
    python tests/course/anti_air_engine.py [--attempts N] [SCENARIO ...]

The player's stand-in moves about too (dashes, walks, stops, at random
lengths) until the opponent jumps, and then:

- stands: the jump-in must land (it was aimed at where they are);
- keeps moving: how often it still lands is reported (a person who keeps
  dash dancing under a jump-in is hard to hit, in a real match too);
- answers: a player who sees the jump-in perfectly but no sooner than a
  person's reaction time after the jump, and searches for an up tilt, up
  smash or back air against the opponent's line: the drill must call it a
  success, since the opponent only jumps when such an answer exists;
- swings early: an up smash as soon as they can react: the opponent sees it
  only after its own reaction time, and must punish it.

And the demonstration (the answer the opponent's check found, played)
must succeed; the jump-ins must vary (where, when, which, the frame of the
aerial) and both fighters must have moved before them.

Then the same in real time, as a person plays it: the game paced at 60
frames a second, the opponent thinking in forked copies of it
(melee_engine/fork.py), every decision made for a frame still to come.
Nothing it thinks may hold a frame up, and the jump-ins must still land
unanswered and be beaten answered (`--live N` attempts a scenario each
way; 0 skips it).
"""
import argparse
import os
import random
import sys
import time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from native import Native  # noqa: E402
from melee_course import engine, registry  # noqa: E402
from melee_course.react import ENGINE  # noqa: E402
from melee_engine.fork import InFork  # noqa: E402
from melee_engine.jumpin import (  # noqa: E402
    NONE, Footsies, answers, press_at)

DRILL = "fox-anti-air"
REACTION = 15
checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def put(session, raw):
    b, lx, ly, cx, cy, lt, rt = raw
    session.set_player_pad(b, lx, ly, cx, cy, max(lt, rt))


class StandIn:
    """The player: moves about until the opponent jumps, then `after`."""

    def __init__(self, session, after, seed):
        self.s, self.after = session, after
        self.body = Footsies(session.person, session.cpu_port,
                             band=(20.0, 75.0), rng=random.Random(seed))
        self.line = None          # (frame it starts, raw pads): an answer
        self.searches = 0
        self.at_jump = None

    def __call__(self, game, frame):
        s = self.s
        opp = getattr(s.d, "eng", None)
        st = game.state()
        if opp is None or opp.jumped is None:
            put(s, self.body.next(st))
            return
        if self.at_jump is None:
            me, cpu = st["p"][s.person], st["p"][s.cpu_port]
            self.at_jump = (round(me["x"], 1), round(cpu["x"], 1),
                            self.body.moved, opp.body.moved)
        since = opp.frame - opp.jumped
        if self.after == "keep":
            put(s, self.body.next(st))
        elif self.after == "early":
            put(s, (0, 0, 0, 0, 127, 0, 0) if since == REACTION else NONE)
        elif self.after == "answer" and since >= REACTION:
            put(s, self.answer(game, opp))
        else:
            put(s, NONE)

    def answer(self, game, opp):
        """Search, every other frame until it has pressed, for an
        anti-air against what the opponent is going to do (its plan from
        here), and play the best found."""
        f = opp.frame
        if self.line is not None:
            start, pads = self.line
            pressed = f - start > self.press
            if pressed or (f - start) % 2:
                i = f - start
                return pads[i] if i < len(pads) else NONE
        rest = opp.plan[f - opp.plan_at:] if opp.plan_at is not None else []
        good, _ = answers(game, self.s.person, self.s.cpu_port, rest, NONE, 0,
                          len(rest) + 8, holds="none,walk_in,walk_out,in,out",
                          enough=1, states=self.s.d.ANSWERS)
        self.searches += 1
        if good:
            self.line = (f, good[0].raw())
            self.press = press_at(good[0])
            return self.line[1][0]
        if self.line is not None:
            start, pads = self.line
            i = f - start
            return pads[i] if i < len(pads) else NONE
        return NONE


def live(drill, args, misses):
    """The drill at the console's pace, the opponent thinking in forks."""
    tally = {"stand": [0, 0], "answer": [0, 0]}
    behind, decided, errors = 0, [], []
    for i, entry in enumerate(drill.deck):
        if args.only and not any(o.lower() in entry.name.lower()
                                 for o in args.only):
            continue
        with Native() as game:
            s = engine.Session(drill, game, character="fox",
                               options={"Opponent": ENGINE}, live=False,
                               seed=17, dpad=False)
            s.thinker = InFork(game)
            game.paced = True        # paced here, by the stand-in's clock
            run = 0
            for after in ("stand", "answer"):
                for a in range(args.live):
                    run += 1
                    who = StandIn(s, after, seed=run * 23 + i)
                    clock = [time.time()]
                    late = [0]

                    def paced(g, f, who=who):
                        who(g, f)
                        clock[0] += 1 / 60.0
                        wait = clock[0] - time.time()
                        if wait > 0:
                            time.sleep(wait)
                        elif wait < -1 / 60.0:
                            late[0] += 1
                            clock[0] = time.time()
                    r = s.run(scenario=i, demo=False, each_frame=paced,
                              run=run)
                    if r["skip"]:
                        misses.append("live %s/%s: %s" % (entry.name, after,
                                                          r["words"]))
                        continue
                    ok = r["words"].startswith("Got hit") \
                        if after == "stand" else r["success"]
                    tally[after][0] += ok
                    tally[after][1] += 1
                    if after == "stand":
                        behind += late[0]     # (the answerer searches)
                    if not ok:
                        misses.append("live %s/%s: %s %s" % (
                            entry.name, after, r["words"], s.d.eng.outcomes))
            decided += s.thinker.took.get("commit", [])
            errors += s.thinker.errors
        print("     live: %s done" % entry.name)
    for k, what in (("stand", "unanswered, the jump-in lands"),
                    ("answer", "answered, the anti-air wins")):
        got, of = tally[k]
        check("in real time, thinking in forks: %s" % what,
              of and got >= of * 0.75, "%d of %d" % (got, of))
    d = sorted(decided)
    check("in real time, no frame waited for a decision, and none failed",
          behind == 0 and not errors,
          "%d frames behind; decisions to jump: median %.0f ms, longest "
          "%.0f ms%s" % (behind, d[len(d) // 2] * 1000 if d else 0,
                         d[-1] * 1000 if d else 0,
                         "; " + errors[0] if errors else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempts", type=int, default=4)
    ap.add_argument("--live", type=int, default=2)
    ap.add_argument("only", nargs="*")
    args = ap.parse_args()
    t0 = time.time()
    drill = registry.get(DRILL)
    tally = {k: [0, 0] for k in ("stand", "keep", "answer", "early", "demo")}
    misses, jumps, moved = [], [], []
    for i, entry in enumerate(drill.deck):
        if args.only and not any(o.lower() in entry.name.lower()
                                 for o in args.only):
            continue
        with Native() as game:
            s = engine.Session(drill, game, character="fox",
                               options={"Opponent": ENGINE}, live=False,
                               seed=7, dpad=False)
            run = 0
            for after in ("stand", "keep", "answer", "early"):
                for a in range(args.attempts):
                    run += 1
                    who = StandIn(s, after, seed=run * 31 + i)
                    r = s.run(scenario=i, demo=False, each_frame=who,
                              run=run)
                    if r["skip"]:
                        misses.append("%s/%s: %s" % (entry.name, after,
                                                     r["words"]))
                        continue
                    opp = s.d.eng
                    words = r["words"]
                    if after in ("stand", "keep", "early"):
                        ok = words.startswith("Got hit")
                    else:
                        ok = r["success"]
                    tally[after][0] += ok
                    tally[after][1] += 1
                    if opp.line is not None:
                        jumps.append((entry.name, opp.jumped,
                                      who.at_jump[:2] if who.at_jump
                                      else None, opp.line.names))
                    if who.at_jump:
                        moved.append(who.at_jump[2:])
                    if not ok and after != "keep":
                        misses.append("%s/%s: %s (%s, %d refused)" % (
                            entry.name, after, words,
                            opp.line.names if opp.line else "-",
                            opp.refused))
            # the demonstration
            for a in range(2):
                run += 1
                r = s.run(scenario=i, demo=True, run=run)
                tally["demo"][0] += r["success"]
                tally["demo"][1] += 1
                if not r["success"]:
                    misses.append("%s/demo: %s" % (entry.name, r["words"]))
        print("     %s done (%.0f s)" % (entry.name, time.time() - t0))

    def rate(k):
        got, of = tally[k]
        return got, of, "%d of %d" % (got, of)

    got, of, txt = rate("stand")
    check("unanswered (the player stops when it jumps), the jump-in lands",
          of and got >= of * 0.95, txt)
    got, of, txt = rate("answer")
    check("answered with an anti-air, no sooner than %d frames after the "
          "jump, it is a success" % REACTION, of and got >= of * 0.9, txt)
    got, of, txt = rate("early")
    check("an up smash thrown as soon as they can react is punished",
          of and got >= of * 0.8, txt)
    got, of, txt = rate("demo")
    check("the demonstration (the answer the opponent's check found) "
          "succeeds", of and got == of, txt)
    print("     keeps moving: the jump-in still lands %d of %d"
          % tuple(tally["keep"]))
    distinct = len(set((j[1], j[2], j[3]) for j in jumps))
    lines = len(set(j[3] for j in jumps))
    check("the jump-ins vary: when, from where, which jump, drift and "
          "aerial frame", distinct >= len(jumps) * 0.8 and
          lines >= len(jumps) * 0.5,
          "%d attempts, %d different, %d different lines" % (
              len(jumps), distinct, lines))
    check("both fighters moved before it jumped",
          moved and all(m[0] > 0 and m[1] > 0 for m in moved),
          "%d of %d" % (sum(m[0] > 0 and m[1] > 0 for m in moved),
                        len(moved)))
    if args.live:
        live(drill, args, misses)
    for m in misses:
        print("     ", m)
    print("%d of %d checks passed (%.0f s)" % (sum(checks), len(checks),
                                                time.time() - t0))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
