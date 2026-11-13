"""Melee Actor: carries out a script from the live game state.

A script is a list of steps ("approach to 12 units", "face the target", "up
tilt", "expect the target to be hit"). The actor decides each frame's
controller input from where the fighters actually are, so the same script
works wherever the target stands and whatever it does on the way. That is
the difference from the frame scripts of the course drills
(src/tmce/events/course): those say "press A on frame 20", this says what
is to be achieved.

This file is the reference implementation. It runs on the native build
(tools/melee_native, where it is developed: docs/ai/native-ai.md) and on the
headless simulator (tools/melee_sim); both give it the same `pad`, `step`
and `fighter`. Design and how learned policies (slippi-ai) fit in:
docs/ai/melee-actor.md.

    import sys; sys.path.insert(0, "tools/melee_native"); sys.path.insert(0, "tools")
    from native import Native
    from melee_actor.actor import Actor
    with Native() as n:
        n.start("fox", "marth")
        result = Actor(n, port=1, target=0).run([
            {"do": "approach", "range": 12},
            {"do": "face"},
            {"do": "attack", "move": "utilt"},
            {"expect": "target_hit"},
        ])

A step is a generator: it looks at the game, yields the pad for one frame,
and is resumed after that frame has run. So two actors, one per fighter, can
be advanced in turn by one loop (`run_together`), which is how a scenario
plays an opponent's script against a player's (scenario.py).
"""

# Action states the actor reasons about (src/melee/ft/kinds/ftCommon/forward.h,
# counted from 0). Only what the steps below need.
WAIT = 14
TURN = 18
DASH = 20
RUN = 21
KNEEBEND = 24
SQUAT_FIRST, SQUAT_LAST = 39, 41
LANDING = 42
ATTACK_FIRST, ATTACK_LAST = 44, 74     # jab 1 .. down air
CATCH_FIRST, CATCH_LAST = 212, 215     # grab, dash grab, and pulling in
CATCH_WAIT = 216                       # holding someone
THROW_FIRST, THROW_LAST = 219, 222     # forward, back, up, down

# One-frame inputs for moves. `toward` is replaced by the direction of the
# target (+1 / -1) when the input is built.
MOVES = {
    "jab": dict(buttons=["A"]),
    "ftilt": dict(buttons=["A"], stick=("toward*0.4", 0)),
    "utilt": dict(buttons=["A"], stick=(0, 0.4)),
    "dtilt": dict(buttons=["A"], stick=(0, -0.4)),
    "fsmash": dict(cstick=("toward", 0)),
    "usmash": dict(cstick=(0, 1)),
    "dsmash": dict(cstick=(0, -1)),
    "grab": dict(buttons=["Z"]),
    "down_b": dict(buttons=["B"], stick=(0, -1)),
    "neutral_b": dict(buttons=["B"]),
    "side_b": dict(buttons=["B"], stick=("toward", 0)),
    "up_b": dict(buttons=["B"], stick=(0, 1)),
    "jump": dict(buttons=["X"]),
}


# How a move comes out of a run, frame by frame ("toward" as above). The up
# smash is jump-cancelled: jump, and the smash on the next frame, before the
# fighter leaves the ground.
RUSH = {
    "grab": [dict(buttons=["Z"], stick=("toward", 0))],
    "dash_attack": [dict(buttons=["A"], stick=("toward", 0))],
    "usmash": [dict(buttons=["X"], stick=("toward", 0)), dict(cstick=(0, 1))],
}
# The same from a standstill, when the target is already within reach.
RUSH_STANDING = {"grab": "grab", "dash_attack": "ftilt", "usmash": "usmash"}
# How far away a running fighter gives the input, when nothing better is
# known (data/actor/reach.json, made by calibrate.py, is better).
RUSH_REACH = {"grab": 14.0, "dash_attack": 16.0, "usmash": 12.0}
THROWS = {"up": (0, 1), "down": (0, -1), "forward": ("toward", 0),
          "back": ("away", 0)}

# Tilts need the stick already resting off-centre when A is pressed: moved
# and pressed on the same frame it reads as a smash. (Found the first time
# this ran: "utilt" came out as an up smash.)
TILT_SETTLE = 4

# How far from the centre the actor will walk or run, by stage. Past this it
# stops rather than follow a target off the edge (it did, and died).
STAGE_LIMIT = {"final-destination": 78.0, "battlefield": 61.0,
               "dream-land": 70.0, "yoshis-story": 50.0,
               "fountain-of-dreams": 56.0, "pokemon-stadium": 80.0}


class StepFailed(Exception):
    pass


_reach = None


def reach_table():
    """{character kind: {move: units}} from data/actor/reach.json, if it
    has been made."""
    global _reach
    if _reach is None:
        import json
        import os
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                            "..", "data", "actor", "reach.json")
        try:
            with open(path) as f:
                _reach = {int(k): v for k, v in json.load(f)["reach"].items()}
        except (OSError, ValueError, KeyError):
            _reach = {}
    return _reach


class Actor:
    """One fighter, driven by a script, aware of one target fighter."""

    def __init__(self, sim, port, target, other=None,
                 stage="final-destination"):
        """sim: a melee_sim Sim in a match. port / target: fighter indices.
        other: optional function(sim, frame) called each frame to drive the
        target's pad (a test's stand-in for the player)."""
        self.limit = STAGE_LIMIT[stage]
        self.sim = sim
        self.port = port
        self.target = target
        self.other = other
        self.frame = 0
        self.log = []

    # ---- what the actor sees ------------------------------------------------

    def me(self):
        return self.sim.fighter(self.port)

    def them(self):
        return self.sim.fighter(self.target)

    def dx(self):
        return self.them().pos[0] - self.me().pos[0]

    def toward(self):
        return 1.0 if self.dx() >= 0 else -1.0

    def grounded_idle(self, f):
        return (not f.airborne) and f.state in (WAIT, LANDING, TURN) + tuple(
            range(SQUAT_FIRST, SQUAT_LAST + 1))

    # ---- one frame ----------------------------------------------------------

    @staticmethod
    def pad(**pad):
        """What a step yields: the pad to hold for one frame (nothing =
        neutral)."""
        return pad

    def _resolve(self, pad):
        """A pad from the tables above, with "toward" and "away" turned
        into the direction of the target."""
        t = self.toward()

        def axis(v):
            if not isinstance(v, str):
                return v
            if v == "away":
                return -t
            return t * float(v.split("*")[1]) if "*" in v else t
        return {k: (tuple(axis(v) for v in val) if k in ("stick", "cstick")
                    else val) for k, val in pad.items()}

    def reach(self, move):
        """How far from the target this fighter, running, starts `move`."""
        me = self.me()
        table = reach_table().get(getattr(me, "ckind", -1), {})
        return float(table.get(move, RUSH_REACH[move]))

    def _input(self, move):
        t = self.toward()
        out = {}
        for key, value in MOVES[move].items():
            if key in ("stick", "cstick"):
                out[key] = tuple(
                    (t * float(v.split("*")[1]) if "*" in v else t)
                    if isinstance(v, str) else v for v in value)
            else:
                out[key] = value
        return out

    # ---- steps --------------------------------------------------------------

    def do_approach(self, range=12.0, tolerance=3.0, timeout=600, **_):
        """Get within `range` of the target (centre to centre), not closer
        than range - tolerance, standing."""
        for _ in _frames(timeout):
            me, dist = self.me(), abs(self.dx())
            if dist <= range and dist >= range - tolerance and \
                    self.grounded_idle(me):
                yield {}
                return dict(distance=round(abs(self.dx()), 1))
            going_off = abs(me.pos[0] + self.toward() * 4) > self.limit
            if me.airborne or (going_off and dist > range):
                yield {}                                  # wait at the edge
            elif dist > range + 18:
                yield dict(stick=(self.toward(), 0))          # run
            elif dist > range:
                yield dict(stick=(self.toward() * 0.45, 0))   # walk the rest
            elif dist < range - tolerance:
                yield dict(stick=(-self.toward() * 0.45, 0))  # too close
            else:
                yield {}                                  # slide to a stop
        raise StepFailed("never got within %.0f of the target" % range)

    def do_face(self, timeout=60, **_):
        """Turn to face the target."""
        for _ in _frames(timeout):
            me = self.me()
            if me.facing == self.toward() and self.grounded_idle(me):
                return {}
            yield dict(stick=(self.toward() * 0.3, 0))
            yield {}
        raise StepFailed("could not turn to face the target")

    def do_attack(self, move, timeout=120, **_):
        """Do `move` once and wait until the actor can act again."""
        if move not in MOVES:
            raise StepFailed("unknown move %r" % move)
        before = self.them().percent
        start_state = self.me().state
        pad = self._input(move)
        if move.endswith("tilt"):
            for _ in _frames(TILT_SETTLE):
                yield dict(stick=pad["stick"])
        yield dict(pad)
        states = []
        for _ in _frames(timeout):
            me = self.me()
            if me.state not in states:
                states.append(me.state)
            if len(states) > 0 and self.grounded_idle(me) and \
                    me.state != start_state or \
                    (states and me.state == WAIT and self.frame > 2 and
                     len(states) > 1):
                break
            yield {}
        return dict(states=states,
                    damage=round(self.them().percent - before, 1))

    def do_rush(self, move, reach=None, timeout=300, **_):
        """Run at the target and do `move` out of the run, without stopping
        first: "grab" (a running grab), "dash_attack", "usmash" (jump
        cancelled). The input is given `reach` units away (by default what
        is known for this character). Done when the actor can act again, or
        is holding the target."""
        if move not in RUSH:
            raise StepFailed("no way to rush with %r" % move)
        reach = float(reach) if reach is not None else self.reach(move)
        before = self.them().percent
        at = None
        for _ in _frames(timeout):
            me, dist = self.me(), abs(self.dx())
            running = me.state in (DASH, RUN)
            if dist <= reach and (running or self.grounded_idle(me)):
                at = dist
                break
            going_off = abs(me.pos[0] + self.toward() * 4) > self.limit
            if me.airborne or going_off:
                yield {}
            else:
                yield dict(stick=(self.toward(), 0))
        if at is None:
            raise StepFailed("never got within %.0f of the target" % reach)
        if self.me().state in (DASH, RUN):
            for pad in RUSH[move]:
                yield self._resolve(pad)
        else:                              # it was already next to us
            yield self._input(RUSH_STANDING[move])
        states, grabbed = [], False
        for _ in _frames(timeout):
            me = self.me()
            if me.state not in states:
                states.append(me.state)
            if me.state == CATCH_WAIT:
                grabbed = True
                break
            if len(states) > 1 and self.grounded_idle(me):
                break
            yield {}
        return dict(states=states, started_at=round(at, 1), grabbed=grabbed,
                    damage=round(self.them().percent - before, 1))

    def do_throw(self, direction="up", timeout=120, **_):
        """Throw the fighter being held."""
        if direction not in THROWS:
            raise StepFailed("unknown throw %r" % direction)
        before = self.them().percent
        thrown = False
        for _ in _frames(timeout):
            me = self.me()
            if THROW_FIRST <= me.state <= THROW_LAST:
                thrown = True
                yield {}
            elif thrown and self.grounded_idle(me):
                return dict(damage=round(self.them().percent - before, 1))
            elif me.state == CATCH_WAIT:
                yield self._resolve(dict(stick=THROWS[direction]))
            elif CATCH_FIRST <= me.state <= CATCH_LAST:
                yield {}                   # still pulling them in
            else:
                break
        raise StepFailed("holding nobody" if not thrown else
                         "the throw never ended")

    def do_wait(self, frames=None, until=None, timeout=600, **_):
        """Wait a number of frames, or until a condition holds:
        "target_grounded", "target_airborne", "target_idle",
        "target_attacking", "target_swung" (its hitbox came out and went),
        "target_frame:<n>", "in_range:<units>"."""
        if frames is not None:
            for _ in _frames(frames):
                yield {}
            return {}
        if until == "target_swung":
            # the target's hitbox has been out and is gone again: the swing
            # is spent, what is left of the move is its ending
            out = False
            for n in _frames(timeout):
                now = self.them().hitbox
                if out and not now:
                    return dict(waited=n)
                out = out or now
                yield {}
            raise StepFailed("waited %d frames for a swing" % timeout)
        for _ in _frames(timeout):
            if self._condition(until):
                return {}
            yield {}
        raise StepFailed("waited %d frames for %s" % (timeout, until))

    def do_hold(self, frames, buttons=(), stick=(0, 0), **_):
        """Hold an input for a number of frames (shield, crouch...)."""
        for _ in _frames(frames):
            kw = dict(buttons=list(buttons), stick=tuple(stick))
            if "R" in buttons:
                kw["r"] = 1.0
            yield kw
        return {}

    def _condition(self, text):
        them = self.them()
        if text == "target_grounded":
            return not them.airborne
        if text == "target_airborne":
            return them.airborne
        if text and text.startswith("in_range:"):
            return abs(self.dx()) <= float(text.split(":")[1])
        if text == "target_attacking":
            return ATTACK_FIRST <= them.state <= ATTACK_LAST or \
                CATCH_FIRST <= them.state <= CATCH_LAST or them.state >= 341
        if text == "target_idle":
            return self.grounded_idle(them)
        if text and text.startswith("target_frame:"):
            # the target's animation has reached this frame
            return them.state_frame >= float(text.split(":")[1])
        raise StepFailed("unknown condition %r" % text)

    # ---- expectations -------------------------------------------------------

    def _expect(self, what, since):
        them = self.them()
        if what == "target_hit":
            return them.percent > since["percent"], \
                "target at %.0f%% (was %.0f%%)" % (them.percent,
                                                   since["percent"])
        if what == "target_not_hit":
            return them.percent == since["percent"], \
                "target at %.0f%%" % them.percent
        if what == "not_hit":
            me = self.me()
            return me.percent == since["own"], \
                "at %.0f%% (was %.0f%%)" % (me.percent, since["own"])
        if what == "hit":
            me = self.me()
            return me.percent > since["own"], \
                "at %.0f%% (was %.0f%%)" % (me.percent, since["own"])
        if what.startswith("in_range:"):
            d = abs(self.dx())
            return d <= float(what.split(":")[1]), "distance %.1f" % d
        raise StepFailed("unknown expectation %r" % what)

    # ---- running a script ---------------------------------------------------

    def steps(self, script):
        """A generator over `script`: yields each frame's pad, and returns
        {"success", "frames", "steps": [...]} when the script is over."""
        since = dict(percent=self.them().percent, own=self.me().percent)
        ok = True
        for step in script:
            entry = dict(step=step, at=self.frame)
            try:
                if "expect" in step:
                    passed, detail = self._expect(step["expect"], since)
                    entry.update(passed=passed, detail=detail)
                    ok = ok and passed
                else:
                    handler = getattr(self, "do_" + step["do"], None)
                    if handler is None:
                        raise StepFailed("unknown step %r" % step["do"])
                    args = {k: v for k, v in step.items() if k != "do"}
                    gen = handler(**args)
                    try:
                        pad = next(gen)
                        while True:
                            yield pad
                            self.frame += 1
                            pad = next(gen)
                    except StopIteration as done:
                        entry.update(done.value or {})
            except StepFailed as e:
                entry.update(failed=str(e))
                ok = False
                self.log.append(entry)
                break
            self.log.append(entry)
        return dict(success=ok, frames=self.frame, steps=self.log)

    def run(self, script):
        """Execute `script` alone (anything else moving is driven by
        `other`). Returns what steps() returns."""
        gen = self.steps(script)
        try:
            while True:
                pad = next(gen)
                if self.other is not None:
                    self.other(self.sim, self.frame)
                self.sim.pad(self.port, **pad)
                self.sim.step()
        except StopIteration as done:
            self.sim.pad(self.port)
            return done.value


def run_together(sim, pairs, frames=1200, after=0):
    """Run several actors' scripts at once: `pairs` is [(actor, script)].
    Each frame every unfinished script gives its fighter's pad, then the
    game runs one frame. Stops when all are done (plus `after` frames, for
    what the last input still causes) or after `frames`. Returns their
    results in order; a script still running at the end gets
    success=False and "unfinished"."""
    gens = [actor.steps(script) for actor, script in pairs]
    results = [None] * len(pairs)
    for _ in range(int(frames)):
        for i, (actor, _script) in enumerate(pairs):
            if results[i] is None:
                try:
                    sim.pad(actor.port, **next(gens[i]))
                except StopIteration as done:
                    results[i] = done.value
                    sim.pad(actor.port)
        if all(r is not None for r in results):
            break
        sim.step()
    for _ in range(int(after)):
        sim.step()
    for i, (actor, _script) in enumerate(pairs):
        if results[i] is None:
            sim.pad(actor.port)
            results[i] = dict(success=False, frames=actor.frame,
                              steps=actor.log, unfinished=True)
    return results


def _frames(n):
    return range(int(n))
