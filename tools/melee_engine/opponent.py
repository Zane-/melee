"""The opponent that thinks (docs/ai/melee-engine.md, E3).

Each time the fighter can act, the engine searches its lines of play from
the current frame (src/host/engine.c), and one of the best is chosen at
random, weighted by score: a softmax over the lines' values with a
temperature (low: nearly always the best; high: more varied). Only the
chosen line's first move is played; then it searches again, from where
that move left it. So it moves, varies and adapts as the player does, and
what it commits to is what the game said would work.

    mind = Mind(n, port=1, target=0, goal=dict(contact=40),
                moves="sh_,fh_,dash_,walk_,wait,wavedash_", temperature=4)
    for raw in mind.pads():     # one raw pad a frame, forever
        ...

`goal`: the score's weights (engine.c: dmg taken ko pos adv contact shield
hit held close dist lcancel). `moves`: the first moves allowed, by name
prefix ("sh_" all short hops), so a drill keeps its scenario: a Marth that
approaches with aerials, not one that grabs.
"""
import math
import random

from melee_engine.search import search


class Mind:
    def __init__(self, n, port, target, goal=None, moves=None,
                 temperature=4.0, horizon=60, budget=2500, depth=2, top=6,
                 rng=None):
        self.n, self.port, self.target = n, port, target
        self.goal = dict(goal or {})
        self.moves = moves
        self.temperature = float(temperature)
        self.horizon, self.budget, self.depth = horizon, budget, depth
        self.top = top
        self.rng = rng or random.Random(0)
        self.decisions = []          # (first move, value, line) chosen
        self.search_ms = 0.0

    def decide(self):
        """Search from here and choose a line; returns it (None if the
        search found nothing)."""
        weights = dict(self.goal)
        if self.moves:
            weights["moves"] = self.moves
        r = search(self.n, self.port, self.target, self.horizon,
                   self.budget, self.depth, **weights)
        self.search_ms += r.ms
        lines = r.lines[:self.top]
        if not lines:
            return None
        if self.temperature <= 0:
            pick = lines[0]
        else:
            best = lines[0].value
            w = [math.exp((l.value - best) / self.temperature) for l in lines]
            pick = self.rng.choices(lines, weights=w)[0]
        self.decisions.append((pick.moves[0], round(pick.value, 1), pick))
        return pick

    def pads(self):
        """Raw pads (buttons, lx, ly, cx, cy, lt, rt), one a frame: the
        chosen line's first move, then a new decision."""
        while True:
            line = self.decide()
            if line is None:
                yield (0, 0, 0, 0, 0, 0, 0)
                continue
            for raw in line.raw()[:max(1, line.first_len)]:
                yield raw


def raw_to_pad(raw):
    """A raw pad as the actor's pads are (Native.pad's arguments)."""
    from melee_engine.search import NAMES
    b, lx, ly, cx, cy, lt, rt = raw
    pad = dict(stick=(lx / 127.0, ly / 127.0), cstick=(cx / 127.0,
                                                       cy / 127.0))
    names = [name for bit, name in NAMES.items() if b & bit]
    if names:
        pad["buttons"] = names
    if lt:
        pad["l"] = lt / 255.0
    if rt:
        pad["r"] = rt / 255.0
    return pad
