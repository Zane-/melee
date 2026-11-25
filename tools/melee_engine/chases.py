"""How the opponent that covers a tech does (behave.Chase, chase.py;
docs/ai/melee-engine.md, "Answers ready before the player chooses"): it
grabs, throws, and chases stand-ins for the player, headless, and what came
of each chase.

    python tools/melee_engine/chases.py                      # the table below
    python tools/melee_engine/chases.py --cpu captain-falcon --react 15,24
    python tools/melee_engine/chases.py --option mix --runs 12 --show
    python tools/melee_engine/chases.py --ahead 0          # the first version

The opponent grabs the stand-in, asks for its table as the grab connects,
throws and chases. Each character has the throw and the damage the drill
fox-escape-techchase plays (`THROWS`; `--cpu top`: all eleven).

A stand-in techs one way (in place, in: toward the opponent, away, none)
or draws one each time ("mix"), and on its first free frame does one thing
(`--then`: jump away, a spot dodge, a roll away, a shield, its down
special, nothing). "caught": grabbed or hit again after the throw;
"escaped": free and untouched for half a second.
"""
import argparse
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "melee_native"))

from native import Native  # noqa: E402
from melee_actor.ahead import look  # noqa: E402
from melee_engine import sense as S  # noqa: E402
from melee_engine.drill import Here  # noqa: E402
from melee_engine.script import Opponent  # noqa: E402

NONE = (0, 0, 0, 0, 0, 0, 0)
A, B, X, R = 0x100, 0x200, 0x400, 0x20
OPTIONS = ("in place", "in", "away", "none")
THENS = ("jump", "spotdodge", "roll", "shield", "down_b", "nothing")
SAFE = 30                     # frames free and untouched: escaped
# the throw of each of the top 11 that leaves Fox in hitstun until the
# floor (a tech chase), and the damage it is thrown at: what the drill
# fox-escape-techchase plays (data/drills)
THROWS = {
    "fox": ("dthrow", 20), "marth": ("fthrow", 30),
    "jigglypuff": ("fthrow", 30), "falco": ("fthrow", 55),
    "sheik": ("dthrow", 20), "captain-falcon": ("dthrow", 20),
    "peach": ("dthrow", 20), "ice-climbers": ("dthrow", 20),
    "pikachu": ("dthrow", 20), "yoshi": ("fthrow", 90),
    "samus": ("dthrow", 20)}
TOP = ("fox", "marth", "jigglypuff", "falco", "sheik", "captain-falcon",
       "peach", "ice-climbers", "pikachu", "yoshi", "samus")


def set_pad(n, port, raw):
    b, lx, ly, cx, cy, lt, rt = raw
    n.h.pads[port].update(buttons=b, lx=lx, ly=ly, cx=cx, cy=cy, lt=lt,
                          rt=rt, connected=True)
    n._dirty.add(port)


class Player:
    """The stand-in: stands to be grabbed; thrown, it techs `option` (R as
    it lands, the stick toward the opponent, away or neither; "none": no
    tech) and on its first free frame after that does `then`."""

    def __init__(self, n, option, then, port=0, cpu=1, di=None):
        self.n, self.option, self.then = n, option, then
        self.di = di              # the stick held while thrown (x, y)
        self.port, self.cpu = port, cpu
        self.thrown = False       # it has been thrown
        self.tech = None          # the frame R went down
        self.landed = None
        self.acted = None

    def pad(self, f, st):
        me, them = st["p"][self.port], st["p"][self.cpu]
        toward = 1 if them["x"] >= me["x"] else -1
        if me["state"] in S.THROWN:
            self.thrown = True
            if self.di:
                return (0, int(127 * self.di[0] * toward),
                        int(127 * self.di[1]), 0, 0, 0, 0)
            return NONE
        if not self.thrown:
            return NONE
        if self.landed is None and not me["air"]:
            self.landed = f
        if self.landed is None:
            if self.option == "none":
                return NONE
            if self.tech is None:
                # R within 3 frames of the floor (played ahead)
                rows = look(self.n, self.port, self.cpu, [(4, {})],
                            stop=0).rows
                if any(r.a_state in S.DOWN for r in rows):
                    self.tech = f
            if self.tech is not None:
                sx = {"in": toward, "away": -toward}.get(self.option, 0)
                return (R, 127 * sx, 0, 0, 0, 0, 0)
            return NONE
        if self.tech is not None and f <= self.tech + 5 and \
                me["state"] not in S.TECHS:
            sx = {"in": toward, "away": -toward}.get(self.option, 0)
            return (R, 127 * sx, 0, 0, 0, 0, 0)
        # on its first free frame (lying there: the first a getup can
        # begin on), one thing
        lying = me["state"] in (184, 192)
        if self.acted is None and (S.free(me) or lying):
            self.acted = f
        if self.acted is not None and f < self.acted + 3:
            if lying or me["state"] in S.DOWN:
                # (a missed tech: up, a roll away, or its getup attack)
                return {"roll": (0, -127 * toward, 0, 0, 0, 0, 0),
                        "down_b": (A, 0, 0, 0, 0, 0, 0),
                        "nothing": NONE}.get(self.then,
                                             (0, 0, 127, 0, 0, 0, 0))
            return {"jump": (X, -127 * toward, 0, 0, 0, 0, 0),
                    "spotdodge": (R, 0, -127, 0, 0, 0, 255),
                    "roll": (R, -127 * toward, 0, 0, 0, 0, 255),
                    "shield": (R, 0, 0, 0, 0, 0, 255),
                    "down_b": (B, 0, -127, 0, 0, 0, 0),
                    "nothing": NONE}[self.then]
        if self.then == "jump" and self.acted is not None:
            return (0, -127 * toward, 0, 0, 0, 0, 0)
        if self.then == "shield" and self.acted is not None and \
                f < self.acted + 40:
            return (R, 0, 0, 0, 0, 0, 255)
        return NONE


def chase_once(n, option, then, react=15, seed=1, percent=20.0, gap=12.0,
               throw="dthrow", ahead=True, reads=True, memory=None,
               limit=420, show=False, di=None):
    """One grab, throw and chase. Returns dict(end: "caught", "escaped" or
    "no throw", how (a grab or a hit), frames, stance, option (as the
    table named it), cover, back (frames the table took), log, memory)."""
    half = abs(n.ledge()[0])
    n.clean()
    n.seed(seed & 0xFFFFFFFF or 1)
    n.place(0, 0.0, 0.0, -1, False, percent)
    n.place(1, -gap, 0.0, 1, False, 0.0)
    n.pad(0)
    n.pad(1)
    n.step(3)
    spec = dict(react=react, script=[
        {"do": "chain_grab", "throw": throw, "chase": True},
        {"do": "chase", "throw": throw, "ahead": bool(ahead),
         "reads": bool(reads)}])
    opp = Opponent(Here(n), 1, 0, spec, seed=seed, half=half, memory=memory)
    player = Player(n, option, then, di=di)
    released = None
    base = None                   # their damage when the throw let go
    free_for = 0
    end, how, f, chase = None, None, 0, None
    for f in range(limit):
        st = n.state()
        me = st["p"][0]
        mine = player.pad(f, st)
        raw = opp.pad(st, mine)
        if opp.doing == "chase" and chase is None:
            chase = opp.cur
        if player.thrown and released is None and \
                me["state"] not in S.THROWN:
            released, base = f, me["percent"]
        if released is not None and f > released:
            if me["state"] in S.CAPTURED:
                end, how = "caught", "grab"
            elif me["percent"] > base:
                end, how = "caught", "hit"
            elif S.free(me) and player.landed is not None:
                free_for += 1
                if free_for >= SAFE:
                    end = "escaped"
            else:
                free_for = 0
        if end is not None or opp.over and released is None:
            break
        set_pad(n, 0, mine)
        set_pad(n, 1, raw)
        n.step()
    opp.stop()
    out = dict(end=end or ("no throw" if released is None else "escaped"),
               how=how, frames=f - (released or 0),
               stance=chase.stance["name"] if chase and chase.stance
               else None,
               option=chase.option if chase else None,
               cover=chase.cover if chase else None,
               back=chase.back if chase else None,
               log=list(chase.log) if chase else [],
               memory=opp.ctx.memory)
    if show:
        print("    %s then %s (react %d): %s%s after %d frames; waited: %s; "
              "cover: %s" % (option, then, react, out["end"],
                             " by a " + how if how else "", out["frames"],
                             out["stance"], out["cover"]))
        for fr, words in out["log"]:
            print("      %4d %s" % (fr, words))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpu", default="sheik,captain-falcon",
                    help="characters, or top: the drill's eleven")
    ap.add_argument("--player", default="fox")
    ap.add_argument("--react", default="15,20,24,30")
    ap.add_argument("--option", default=",".join(OPTIONS),
                    help="in place, in, away, none, or mix")
    ap.add_argument("--then", default="jump,nothing")
    ap.add_argument("--percent", type=float, default=None,
                    help="the player's damage (by default the drill's "
                    "for the character)")
    ap.add_argument("--throw", default=None,
                    help="dthrow, fthrow, bthrow, uthrow (by default the "
                    "drill's for the character)")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--ahead", type=int, default=1,
                    help="0: the first version (stands, searches when it "
                    "has seen the option)")
    ap.add_argument("--reads", type=int, default=1)
    ap.add_argument("--forget", action="store_true",
                    help="each chase with nothing remembered of the "
                    "player's choices")
    ap.add_argument("--di", default="",
                    help="the stick held while thrown: in, away, down "
                    "(toward or away from the opponent)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    cpus = TOP if args.cpu == "top" else args.cpu.split(",")
    for cpu in cpus:
        throw = args.throw or THROWS.get(cpu, ("dthrow", 20))[0]
        percent = args.percent if args.percent is not None else \
            float(THROWS.get(cpu, ("dthrow", 20))[1])
        with Native() as n:
            n.start(args.player, cpu, "final-destination", args.seed)
            for react in [int(x) for x in args.react.split(",")]:
                for option in args.option.split(","):
                    for then in args.then.split(","):
                        rng = random.Random(args.seed * 31 + react)
                        memory, caught, ways = {}, 0, {}
                        for run in range(args.runs):
                            o = rng.choice(OPTIONS) if option == "mix" \
                                else option
                            r = chase_once(
                                n, o, then, react, args.seed * 7919 + run,
                                percent, throw=throw,
                                ahead=args.ahead, reads=args.reads,
                                memory=None if args.forget else memory,
                                show=args.show,
                                di={"in": (1, 0), "away": (-1, 0),
                                    "down": (0, -1)}.get(args.di))
                            memory = {"chase": r["memory"].get("chase", {})}
                            caught += r["end"] == "caught"
                            key = "%s/%s" % (r["stance"], r["cover"])
                            ways[key] = ways.get(key, 0) + 1
                        print("%-15s %s react %2d  %-9s then %-9s caught "
                              "%d of %d  (%s)" % (
                                  cpu, throw, react, option, then, caught,
                                  args.runs, ", ".join(
                                      "%s x%d" % kv
                                      for kv in sorted(ways.items()))),
                              flush=True)
    print("%.0f s" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
