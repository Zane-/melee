"""A drill's opponent played by the Melee Actor instead of a frame table.

The course drills came from C, where the opponent's attack is a table of
inputs by frame (`In`, `Ctx.script`): "jump on 0, drift from 5, nair on 20".
Pressed wherever the player has gone in the meantime, it misses a player
who stepped forward or back before it, and the drill teaches nothing. Here
the opponent is an actor script (tools/melee_actor/actor.py) whose attacks
look ahead in the game before they commit (`aerial`, `strike`), so they
land unless the player answers them the way the drill teaches.

    opp = Opponent(c, [dict(do="aerial", move="nair", hop="short")])
    ...each think():
    opp.frame(c)               # this frame's pad into the CPU's controller
    opp.committed              # attempt frame of the commitment, or None

Each converted drill has an option Opponent: Reactive (this) or Fixed
timing (the C's table, which the overlay's specs check). fox-anti-air has a
third, Engine (melee_engine/drill.py, contracts.py): the opponent moves about and plans
the jump-in itself with the search engine, and jumps only when the player
has an answer to it.
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "melee_native"))

from melee_actor.actor import Actor, STAGE_LIMIT  # noqa: E402
from native import BUTTONS  # noqa: E402

from melee_course.engine import Option  # noqa: E402

REACTIVE, FIXED, ENGINE = 0, 1, 2
NAMES = {bit: name for name, bit in BUTTONS.items()}


def sequence(inputs):
    """A C table of CPU inputs (`In`, as Ctx.script plays it) as the actor's
    frame-by-frame pads: stick values converted as cpu_axis does, X toward
    the player as "toward*k"."""
    from melee_course.engine import cpu_axis
    length = max(i.frame + (i.hold or 1) for i in inputs)
    pads = []
    for f in range(length):
        buttons, axes = 0, None
        for i in inputs:
            if i.frame <= f < i.frame + (i.hold or 1):
                buttons |= i.buttons
                axes = (i.lx, i.ly, i.cx, i.cy)   # the last one active wins
        pad = {}
        if buttons:
            pad["buttons"] = [NAMES[b] for b in NAMES if buttons & b]
        if axes is not None:
            lx, ly, cx, cy = (cpu_axis(v) / 127.0 for v in axes)
            if lx or ly:
                pad["stick"] = ("toward*%g" % lx if lx else 0.0, ly)
            if cx or cy:
                pad["cstick"] = ("toward*%g" % cx if cx else 0.0, cy)
        pads.append(pad)
    return pads


def opponent_option(engine=False):
    values = ["Reactive", "Fixed timing"]
    desc = ("Reactive: the opponent looks ahead and moves, waits and aims "
            "so its attack lands unless you answer it. Fixed timing: it "
            "presses its buttons on set frames (Training Mode's), wherever "
            "you are.")
    if engine:
        values.append("Engine")
        desc += (" Engine: it moves about, chooses its moment and plans "
                 "the jump-in by search; it jumps only when you have an "
                 "anti-air that beats it, and punishes one thrown early.")
    return Option("Opponent", values, ENGINE if engine else REACTIVE, desc)


def thinker(c):
    """Where an engine opponent thinks, kept for the session: the one it was
    given (`Session.thinker`, a test's); in the window build, where a
    person watches every frame, forked copies of the game (no frame waits
    for a decision: melee_engine/fork.py); headless, the game itself."""
    s = c.s
    t = getattr(s, "thinker", None)
    if t is None:
        if hasattr(c.n, "pace"):          # the window build
            from melee_engine.fork import InFork
            t = InFork(c.n)
        else:
            from melee_engine.drill import Here
            t = Here(c.n)
        s.thinker = t
    return t


def player_raw(c):
    """The player's pad this frame, as a raw pad."""
    s = c.s
    p = s.live_pad if s.live and s.live_pad is not None else s.player_pad
    return (p["buttons"], p["lx"], p["ly"], p["cx"], p["cy"], p.get("lt", 0),
            p.get("rt", 0))


def put_raw(c, raw):
    """A raw pad into the CPU's controller for this frame (`c._pad`)."""
    b, lx, ly, cx, cy, lt, rt = raw
    p = c._pad
    p["buttons"] |= b
    p["lx"], p["ly"], p["cx"], p["cy"] = lx, ly, cx, cy
    p["lt"], p["rt"] = max(p["lt"], lt), max(p["rt"], rt)


class Opponent:
    """An actor script as the drill's CPU, one frame per think()."""

    def __init__(self, c, script, seed=None):
        s = c.s
        stage = s.d.stage if s.d.stage in STAGE_LIMIT else \
            "final-destination"
        self.actor = Actor(c.n, port=s.cpu_port, target=s.person,
                           stage=stage,
                           rng=random.Random(
                               s.seed * 7919 + s.attempts
                               if seed is None else seed))
        if s.live:
            # A person is playing: the frame has 16.7 ms for the game, its
            # drawing and this. In the window build (unoptimised, off
            # screen, 2026-11-13) a look costs 4.5 ms for 20 frames and 8.3
            # for 70, a drawn frame about 6: one look a frame. The search
            # then goes on over the next frames.
            self.actor.look_budget = 1
        self.gen = self.actor.steps(script)
        self.result = None
        self.started = s.attempt_frame
        self.committed = None

    @property
    def running(self):
        return self.result is None

    def frame(self, c):
        """Put this frame's pad into the CPU's controller (`c._pad`).
        False once the script is over."""
        if self.result is not None:
            return False
        try:
            pad = next(self.gen)
        except StopIteration as done:
            self.result = done.value
            return False
        if self.committed is None and self.actor.committed is not None:
            self.committed = c.s.attempt_frame
        p = c._pad
        p["buttons"] |= sum(BUTTONS[b.upper()] for b in pad.get("buttons",
                                                                 ()))
        if "stick" in pad:
            p["lx"], p["ly"] = (int(round(max(-1, min(1, v)) * 127))
                                for v in pad["stick"])
        if "cstick" in pad:
            p["cx"], p["cy"] = (int(round(max(-1, min(1, v)) * 127))
                                for v in pad["cstick"])
        if pad.get("l"):
            p["lt"] = max(p["lt"], int(pad["l"] * 255))
        if pad.get("r"):
            p["rt"] = max(p["rt"], int(pad["r"] * 255))
        return True

    def step(self, do):
        """The result of the script's first step of kind `do`, if it has
        run."""
        return next((e for e in self.actor.log
                     if e["step"].get("do") == do), None)
