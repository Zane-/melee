"""How the recovering opponent does (recover.py; docs/ai/melee-engine.md,
"Recovering"): characters knocked off the stage as the edgeguard drill
knocks them (the launches below, TM-CE's hit strengths), recovering
against stand-ins for the player, headless, and what came of each.

    python tools/melee_engine/recoveries.py                    # the top 11
    python tools/melee_engine/recoveries.py --chars fox,marth --runs 6
    python tools/melee_engine/recoveries.py --standin ledge --react 15
    python tools/melee_engine/recoveries.py --chars fox --show   # each log

Stand-ins: "stand" (does nothing: every recovery should make it back),
"ledge" (takes the ledge at once and holds it), "hog" (takes it as late as
it still does), "bair" (drops from the stage and back airs the ledge as
the opponent comes), "wait" (stands at the ledge, down smashes when the
opponent is close). `--react`: the opponent's reaction time, frames.
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
from melee_engine.drill import Here  # noqa: E402
from melee_engine.script import Opponent  # noqa: E402

TOP = ("fox", "marth", "jigglypuff", "falco", "sheik", "captain-falcon",
       "peach", "ice-climbers", "pikachu", "yoshi", "samus")

# TM-CE's hit strengths (src/edgeguard.h, HitStrength_KBRange): knockback,
# its angle, the damage the opponent has
LAUNCHES = {
    "weak": dict(kb=(80, 100), angle=(45, 60), percent=(10, 40)),
    "normal": dict(kb=(106, 120), angle=(45, 60), percent=(50, 80)),
    "hard": dict(kb=(140, 170), angle=(65, 70), percent=(80, 110)),
    "shallow": dict(kb=(110, 130), angle=(20, 40), percent=(60, 80)),
}
NONE = (0, 0, 0, 0, 0, 0, 0)
A, B, X, Z, R = 0x100, 0x200, 0x400, 0x10, 0x20


def set_pad(n, port, raw):
    b, lx, ly, cx, cy, lt, rt = raw
    n.h.pads[port].update(buttons=b, lx=lx, ly=ly, cx=cx, cy=cy, lt=lt,
                          rt=rt, connected=True)
    n._dirty.add(port)


# ---- stand-ins for the player ---------------------------------------------------

class Stand:
    """Does nothing."""
    name = "stand"

    def __init__(self, side, half, rng):
        self.side, self.half, self.rng = side, half, rng
        self.t = -1

    def pad(self, st):
        self.t += 1
        return self.step(st["p"][0], st["p"][1])

    def step(self, me, them):
        return NONE


class Ledge(Stand):
    """Takes the ledge at once and holds it: a wavedash back off the edge
    (the player starts with their back to it: a jump, and an air dodge
    down and back on the first frame in the air; Fox, 20 units in, hangs
    23 frames later)."""
    name = "ledge"
    at = 2
    SQUAT = 3                 # Fox's jump squat

    def step(self, me, them):
        k = self.t - self.at
        if me["state"] in (252, 253) or k < 0:
            return NONE
        if k == 0:
            return (X, 0, 0, 0, 0, 0, 0)
        if k == self.SQUAT:
            return (R, int(0.95 * 127 * self.side), int(-0.31 * 127), 0, 0,
                    0, 255)
        return NONE


class Hog(Ledge):
    """Takes the ledge late: once the opponent, out of its hitstun, is
    within `NEAR` units of it and coming down."""
    name = "hog"
    at = None
    NEAR = 75.0

    def step(self, me, them):
        if self.at is None:
            d = ((abs(them["x"]) - self.half) ** 2 + them["y"] ** 2) ** 0.5
            if not (d < self.NEAR and them["state"] not in range(75, 92)):
                return NONE
            self.at = self.t
        return Ledge.step(self, me, them)


class Bair(Stand):
    """Drops off the stage facing in when the opponent comes within reach
    of the ledge, and back airs toward it."""
    name = "bair"

    def __init__(self, side, half, rng):
        super().__init__(side, half, rng)
        self.go = None

    def step(self, me, them):
        out = 127 * self.side
        d = abs(them["x"]) - self.half
        if self.go is None:
            if d < 45 and them["y"] < 25 and \
                    them["state"] not in range(75, 92):
                self.go = self.t
            else:
                # at the ledge, facing the stage's middle
                edge = self.side * (self.half - 4)
                if abs(me["x"] - edge) > 2.5:
                    return (0, 60 if edge > me["x"] else -60, 0, 0, 0, 0, 0)
                if me["facing"] * self.side > 0:
                    return (0, -40 * self.side, 0, 0, 0, 0, 0)
                return NONE
        k = self.t - self.go
        if not me["air"] and k < 40:
            # backwards off the edge: a short hop out
            return (X, out, 0, 0, 0, 0, 0) if k % 2 == 0 else \
                (0, out, 0, 0, 0, 0, 0)
        if me["air"] and me["state"] not in range(65, 70):
            near = abs(them["x"] - me["x"]) < 26 and \
                abs(them["y"] - me["y"]) < 22
            if near:
                # the C-stick away from where it faces: a back air
                return (0, out, 0, int(-127 * me["facing"]), 0, 0, 0)
        return (0, out if me["air"] and k < 14 else -out, 0, 0, 0, 0, 0)


class Wait(Stand):
    """Stands at the ledge and down smashes when the opponent is close."""
    name = "wait"

    def step(self, me, them):
        edge = self.side * (self.half - 6)
        if not me["air"] and abs(me["x"] - edge) > 3 and \
                me["state"] in (14, 15, 16, 17, 18, 20):
            return (0, 60 if edge > me["x"] else -60, 0, 0, 0, 0, 0)
        d = ((them["x"] - me["x"]) ** 2 + (them["y"] - me["y"]) ** 2) ** 0.5
        if d < 24 and me["state"] in (14, 15, 16, 17, 18):
            return (0, 0, 0, 0, -127, 0, 0)
        return NONE


STANDINS = {c.name: c for c in (Stand, Ledge, Hog, Bair, Wait)}


# ---- one recovery ---------------------------------------------------------------

def launch(n, rng, kind, side, half, jumps=1, port=1):
    """The opponent knocked off the stage's `side` as the drill does it: a
    launch of `kind` drawn from its ranges. Returns what was drawn."""
    L = LAUNCHES[kind]
    kb = rng.uniform(*L["kb"])
    angle = int(round(rng.uniform(*L["angle"])))
    percent = int(round(rng.uniform(*L["percent"])))
    # (the player with their back to the ledge, as TM-CE's edgeguard event
    # leaves them: after the back air that sent the opponent off)
    n.place(0, side * (half - 15.0), 0.0, -side, False, 0.0)
    n.launch(port, side * (half - 8.0), 6.0, percent, kb, angle, side, jumps)
    return dict(kb=round(kb, 1), angle=angle, percent=percent)


def recover_once(n, char, kind, side, seed, standin="stand", react=15,
                 budget=48, limit=900, jumps=1, memory=None, show=False):
    """One launch and the recovery from it. Returns dict(end, frames, kind,
    log, drawn, hit (damage it took), ms, decisions)."""
    rng = random.Random(seed)
    half = abs(n.ledge()[0])
    n.clean()
    n.seed(seed & 0xFFFFFFFF or 1)
    drawn = launch(n, rng, kind, side, half, jumps)
    n.pad(0)
    n.pad(1)
    n.step()
    spec = dict(script=[dict(do="recover", budget=budget)], react=react)
    opp = Opponent(Here(n), 1, 0, spec, seed=seed, half=half, char="fox",
                   memory=None)
    if memory is not None:
        opp.ctx.memory["recover"] = memory
    player = STANDINS[standin](side, half, random.Random(seed + 1))
    start = n.state()["p"][1]["percent"]
    end, f = None, 0
    their = NONE
    for f in range(limit):
        st = n.state()
        me = st["p"][1]
        if me is None:
            end = "gone"
            break
        their = player.pad(st)
        raw = opp.pad(st, their)
        b = opp.cur
        if b is not None and getattr(b, "ended", None):
            end = b.ended
            break
        if opp.over:
            end = getattr(b, "ended", None) or "over"
            break
        set_pad(n, 0, their)
        set_pad(n, 1, raw)
        n.step()
    pilot = opp.cur.pilot if opp.cur is not None and \
        hasattr(opp.cur, "pilot") else None
    me = n.state()["p"][1]
    out = dict(end=end or "timeout", frames=f, drawn=drawn,
               # the kinds of route it flew, in order (the air's, then the
               # ledge's if it went by it)
               kind=" / ".join(pilot.via) if pilot and pilot.via else None,
               via=list(pilot.via) if pilot else [],
               grabs=pilot.grabs if pilot else 0,
               log=list(pilot.log) if pilot else [],
               hit=(me["percent"] - start) if me else 0.0,
               ms=pilot.wall if pilot else 0.0,
               decisions=len(pilot.decisions) if pilot else 0,
               late=pilot.late if pilot else 0)
    opp.stop()
    if show:
        print("    %s %s side %+d %s -> %s in %d, %s, %.0f ms" % (
            char, kind, side, drawn, out["end"], f, out["kind"], out["ms"]))
        for fr, words in out["log"]:
            print("      %4d %s" % (fr, words))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chars", default=",".join(TOP))
    ap.add_argument("--launches", default=",".join(LAUNCHES))
    ap.add_argument("--runs", type=int, default=4,
                    help="recoveries of each launch (both sides in turn)")
    ap.add_argument("--standin", default="stand", choices=sorted(STANDINS))
    ap.add_argument("--react", type=int, default=15)
    ap.add_argument("--budget", type=int, default=48)
    ap.add_argument("--jumps", type=int, default=1,
                    help="jumps used at the launch (2: no double jump)")
    ap.add_argument("--stage", default="final-destination")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--show", action="store_true", help="each one's log")
    args = ap.parse_args()
    t0 = time.time()
    total = good = 0
    for ch in args.chars.split(","):
        with Native() as n:
            n.start("fox", ch, args.stage, args.seed)
            memory = {}
            for kind in args.launches.split(","):
                ends, kinds, ms, frames = {}, {}, 0.0, 0
                for run in range(args.runs):
                    side = 1 if run % 2 == 0 else -1
                    r = recover_once(
                        n, ch, kind, side, args.seed * 7919 + run * 104729
                        + 131 * sorted(LAUNCHES).index(kind), args.standin,
                        args.react,
                        args.budget, jumps=args.jumps, memory=memory,
                        show=args.show)
                    ends[r["end"]] = ends.get(r["end"], 0) + 1
                    if r["kind"]:
                        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
                    ms += r["ms"]
                    frames += r["frames"]
                    total += 1
                    good += r["end"] in ("ledge", "stage")
                print("%-15s %-8s %s  %s  %.0f ms, %d frames a recovery" % (
                    ch, kind, " ".join("%s %d" % kv for kv in sorted(
                        ends.items())), ", ".join(
                        "%s x%d" % kv for kv in sorted(
                            kinds.items(), key=lambda kv: -kv[1])),
                    ms / args.runs, frames / args.runs))
    print("%d of %d back (%s, react %d), %.0f s" % (
        good, total, args.standin, args.react, time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
