"""Shadow games: a headless copy of the live match, kept in step, to think
in (docs/ai/melee-engine.md, E2).

A headless game that runs the draw pass and is given the same commands and
the same inputs stays the same game as the window build's, frame for
frame (checked: 2,000 frames of random inputs, the fighters' and the random
seed's hash equal throughout). So the opponent can search for as long as it
likes in the copy, and the frame a person is watching never waits.

    shadow = Shadow()
    game = Mirrored(window, shadow, person=0)   # use `game` as the Native
    game.start("fox", "marth")                  # both start the match
    mind = LiveMind(shadow, port=1, target=0, goal=dict(contact=40))
    ...each frame: pad = mind.pad(); game.pad(1, ...); game.step()

`Shadow` owns its game in a thread: frames and commands are applied in the
order they came; a decision is searched when its turn comes and answered
asynchronously. `Mirrored` is the live game with every change also made in
the shadow: the commands that change the game, and each frame's inputs as
the live game used them (a person's included). Every CHECK_EVERY frames the
two hashes are compared; a desync is reported (`shadow.desync`), not hidden.
"""
import math
import os
import queue
import random
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "melee_native"))

from melee_engine.search import preroll as set_preroll, search  # noqa: E402

# Native methods that change the game: made in the shadow too.
CHANGES = {"start", "match", "place", "shield", "anchor", "clean", "swap",
           "rebirth", "ledge", "seed", "ucf", "freeze"}
CHECK_EVERY = 120


class Shadow:
    def __init__(self, exe=None, verbose=False):
        from native import Native
        kw = dict(draw=True, verbose=verbose)
        if exe is not None:
            kw["exe"] = exe
        self.n = Native(**kw)
        self.q = queue.Queue()
        self.done = threading.Condition()
        self.results = {}
        self.applied = 0          # frames applied
        self.desync = None        # the first frame the hashes differed
        self.checks = 0
        self.error = None
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    # ---- from the live side ------------------------------------------------

    def call(self, name, *a, **kw):
        self.q.put(("call", name, a, kw))

    def frame(self, pads):
        """The live game's inputs for one frame: {port: raw}, raw =
        (buttons, lx, ly, cx, cy, lt, rt)."""
        self.q.put(("frame", pads))

    def check(self, live_hash, at):
        self.q.put(("check", live_hash, at))

    def ask(self, tag, port, target, preroll, args):
        """Search for PORT from where `preroll` (its raw pads) ends, once
        every frame before has been applied; the answer goes to
        results[tag]."""
        self.q.put(("ask", tag, port, target, list(preroll), args))

    def answer(self, tag, wait=None):
        with self.done:
            if tag not in self.results and wait:
                self.done.wait_for(lambda: tag in self.results, wait)
            return self.results.pop(tag, None)

    def close(self):
        self.q.put(None)
        self.thread.join(timeout=10)
        self.n.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # ---- the shadow's thread -----------------------------------------------

    def _run(self):
        try:
            while True:
                item = self.q.get()
                if item is None:
                    return
                kind = item[0]
                if kind == "call":
                    getattr(self.n, item[1])(*item[2], **item[3])
                elif kind == "frame":
                    for port, raw in item[1].items():
                        b, lx, ly, cx, cy, lt, rt = raw
                        self.n.h.pads[port].update(
                            buttons=b, lx=lx, ly=ly, cx=cx, cy=cy, lt=lt,
                            rt=rt, connected=True)
                        self.n._dirty.add(port)
                    self.n.step()
                    self.applied += 1
                elif kind == "check":
                    self.checks += 1
                    if self.n._cmd("net hash") != item[1] and \
                            self.desync is None:
                        self.desync = item[2]
                elif kind == "ask":
                    _, tag, port, target, pre, args = item
                    if pre:
                        set_preroll(self.n, pre)
                    r = search(self.n, port, target, **args)
                    with self.done:
                        self.results[tag] = (r, self.applied)
                        self.done.notify_all()
        except Exception as e:           # reported, not swallowed
            self.error = e
            with self.done:
                self.done.notify_all()


class Mirrored:
    """The live game, every change to it also made in the shadow."""

    def __init__(self, live, shadow, person=None, live_ports=()):
        self.live, self.shadow = live, shadow
        self.person = person
        self.live_ports = tuple(live_ports)   # read from a controller
        self.frames = 0

    def __getattr__(self, name):
        attr = getattr(self.live, name)
        if name in CHANGES and callable(attr):
            def both(*a, **kw):
                out = attr(*a, **kw)
                self.shadow.call(name, *a, **kw)
                return out
            return both
        return attr

    def step(self, frames=1):
        out = None
        for _ in range(int(frames)):
            pads = {}
            held = self.live.h.pads
            for port in range(4):
                p = held[port]
                if p.get("connected") or port in self.live_ports:
                    pads[port] = (p["buttons"], p["lx"], p["ly"], p["cx"],
                                  p["cy"], p["lt"], p["rt"])
            if self.live_ports:
                # what a person holds, as the game is given it this frame
                given = self.live.pads(game=True)
                for port in self.live_ports:
                    g = given[port]
                    pads[port] = (g["buttons"], g["lx"], g["ly"], g["cx"],
                                  g["cy"], g["lt"], g["rt"])
            out = self.live.step()
            self.shadow.frame(pads)
            self.frames += 1
            if self.frames % CHECK_EVERY == 0:
                self.shadow.check(self.live._cmd("net hash"), self.frames)
        return out


class LiveMind:
    """The engine opponent for a live match: decisions searched in the
    shadow ahead of time, so none is waited for in the frame a person
    watches. Same choices as opponent.Mind (a softmax over the best lines'
    scores); `pad()` gives this frame's raw pad.

    Every decision is for a frame still to come: while a move plays out,
    the next is searched from where that move ends (its remaining inputs
    as the search's pre-roll). With nothing playing, the fighter holds
    still for the time a search takes (measured, plus a margin) and the
    decision is for where that wait ends. An answer that comes after its
    frame is dropped and the wait made longer."""

    def __init__(self, shadow, port, target, goal=None, moves=None,
                 temperature=4.0, horizon=60, budget=1500, depth=2, top=6,
                 rng=None, latency=8):
        self.shadow, self.port, self.target = shadow, port, target
        self.args = dict(horizon=horizon, budget=budget, depth=depth)
        self.args.update(goal or {})
        if moves:
            self.args["moves"] = moves
        self.temperature, self.top = float(temperature), top
        self.rng = rng or random.Random(0)
        self.queue = []           # raw pads still to play: a move or a wait
        self.tag = 0
        self.pending = None       # (tag, frame asked, frame it is for)
        self.frame = 0
        self.latency = float(latency)   # frames a search takes, measured
        self.decisions = []
        self.waited = 0           # frames held still waiting for a search
        self.late = 0
        self.on_time = 0

    NEUTRAL = (0, 0, 0, 0, 0, 0, 0)

    FRAME_MS = 1000.0 / 60

    def _ask(self, pre):
        self.tag += 1
        args = dict(self.args)
        # the time there is before the answer is needed: the frames until
        # its frame, less what reaching the search costs
        args["ms"] = max(10.0, (len(pre) - 2) * self.FRAME_MS * 0.75)
        self.shadow.ask(self.tag, self.port, self.target, pre, args)
        self.pending = (self.tag, self.frame, self.frame + len(pre))

    def _choose(self, r):
        lines = r.lines[:self.top]
        if not lines:
            return None
        best = lines[0].value
        w = [math.exp((l.value - best) / max(self.temperature, 1e-6))
             for l in lines]
        pick = self.rng.choices(lines, weights=w)[0]
        self.decisions.append((pick.moves[0], round(pick.value, 1)))
        return pick

    def _wait(self):
        """Hold still for a search's time and ask for where that ends."""
        n = max(3, int(math.ceil(self.latency)) + 2)
        self.queue = [self.NEUTRAL] * n
        self._ask(self.queue)

    def pad(self):
        """This frame's raw pad. Call once a frame, before the frame is
        stepped."""
        if not self.queue:
            got = None
            if self.pending is not None:
                tag, asked, at = self.pending
                got = self.shadow.answer(tag)
                if got is not None:
                    self.pending = None
                    took = self.frame - asked
                    self.latency = 0.7 * self.latency + 0.3 * took
                    if at != self.frame:
                        got = None
                elif self.frame >= at:
                    # not back in time: drop it, and wait longer next time
                    self.pending = None
                    self.late += 1
                    self.latency += 3
            if got is not None:
                line = self._choose(got[0])
                if line is not None:
                    self.on_time += 1
                    self.queue = list(line.raw()[:max(1, line.first_len)])
                    self._ask(self.queue)    # the next, for where it ends
            if not self.queue:
                self._wait()
        if self.queue and self.pending is not None and \
                self.queue[0] == self.NEUTRAL and \
                len(self.queue) == self.pending[2] - self.frame:
            self.waited += 1
        self.frame += 1
        return self.queue.pop(0)
