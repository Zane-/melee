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


# action states in which the body is moving, not committed to anything
# (ftCommon: Wait, walks, turn, dash, run, run brake, jumps, falls, squat,
# landing, shield)
NEUTRAL = set([14, 15, 16, 17, 18, 20, 21, 23, 25, 26, 27, 28, 29, 30, 31,
               32, 33, 34, 39, 40, 41, 42, 178, 179])


class Blend:
    """Moves like a person, attacks like an engine (docs/ai/melee-engine.md,
    E4). The body (human.ModelBody: a slippi-ai policy with its attacks
    taken out) moves the fighter every frame; every `every` frames the
    engine searches, against the player model's prediction of the next 17
    frames (human.ModelPlayer) when there is one, for an attack among
    `moves` that lands within its first move; when it finds one, that move
    is played (one of the best by a softmax: variance), then the body has
    the controller again. Headless: the searches run in the game itself."""

    LANDS = ("hit", "shield", "grab")

    def __init__(self, n, port, target, body, player=None, goal=None,
                 moves=None, every=4, temperature=4.0, horizon=60,
                 budget=1200, depth=2, top=6, rng=None):
        self.n, self.port, self.target = n, port, target
        self.body, self.player = body, player
        self.goal = dict(goal or dict(contact=40))
        self.moves = moves
        self.every = every
        self.temperature = float(temperature)
        self.horizon, self.budget, self.depth, self.top = horizon, budget, \
            depth, top
        self.rng = rng or random.Random(0)
        self.queue = []
        self.frame = 0
        self.commits = []           # (frame, move, contact foreseen)
        self.search_ms = 0.0
        self.searches = 0

    def pad(self, their_pad=None):
        """This frame's raw pad; call once a frame before stepping.
        `their_pad`: the target's raw pad this frame (dict buttons lx ly
        cx cy lt rt), for the player model."""
        from melee_engine.search import player as set_player
        st = self.n.state()
        body = self.body.step(st)
        predicted = []
        if self.player is not None and their_pad is not None:
            predicted = self.player.predict(st, their_pad)
        self.frame += 1
        if self.queue:
            return self.queue.pop(0)
        me = st["p"][self.port]
        if me is None or me["state"] not in NEUTRAL or \
                self.frame % self.every:
            return body
        if predicted:
            set_player(self.n, [(1, r) for r in predicted])
        weights = dict(self.goal)
        if self.moves:
            weights["moves"] = self.moves
        r = search(self.n, self.port, self.target, self.horizon,
                   self.budget, self.depth, **weights)
        self.search_ms += r.ms
        self.searches += 1
        if predicted:
            set_player(self.n, None)
        lands = [l for l in r.lines[:self.top * 2]
                 if l.contact in self.LANDS and 0 < l.contact_at <=
                 l.first_len + 2]
        if not lands:
            return body
        best = lands[0].value
        w = [math.exp((l.value - best) / max(self.temperature, 1e-6))
             for l in lands[:self.top]]
        pick = self.rng.choices(lands[:self.top], weights=w)[0]
        self.commits.append((self.frame, pick.moves[0], pick.contact))
        self.queue = list(pick.raw()[:max(1, pick.first_len)])
        return self.queue.pop(0)
