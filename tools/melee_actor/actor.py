"""Melee Actor: carries out a script from the live game state.

A script is a list of steps ("approach to 12 units", "face the target", "up
tilt", "expect the target to be hit"). The actor decides each frame's
controller input from where the fighters actually are, so the same script
works wherever the target stands and whatever it does on the way. That is
the difference from the frame scripts of the course drills
(src/tmce/events/course): those say "press A on frame 20", this says what
is to be achieved.

This file is the reference implementation, running on the headless
simulator (tools/melee_sim). Design, the in-game twin and how learned
policies (slippi-ai) fit in: docs/ai/melee-actor.md.

    import sys; sys.path.insert(0, "tools/melee_sim"); sys.path.insert(0, "tools")
    from sim import Sim
    from melee_actor.actor import Actor
    s = Sim.match("lab", "fox", "marth", free=True)
    result = Actor(s, port=1, target=0).run([
        {"do": "approach", "range": 12},
        {"do": "face"},
        {"do": "attack", "move": "utilt"},
        {"expect": "target_hit"},
    ])
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

    def tick(self, **pad):
        """Hold `pad` for one frame (nothing = neutral) and advance."""
        if self.other is not None:
            self.other(self.sim, self.frame)
        self.sim.pad(self.port, **pad)
        self.sim.step()
        self.frame += 1

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
                self.tick()
                return dict(distance=round(abs(self.dx()), 1))
            going_off = abs(me.pos[0] + self.toward() * 4) > self.limit
            if me.airborne or (going_off and dist > range):
                self.tick()                                  # wait at the edge
            elif dist > range + 18:
                self.tick(stick=(self.toward(), 0))          # run
            elif dist > range:
                self.tick(stick=(self.toward() * 0.45, 0))   # walk the rest
            elif dist < range - tolerance:
                self.tick(stick=(-self.toward() * 0.45, 0))  # too close
            else:
                self.tick()                                  # slide to a stop
        raise StepFailed("never got within %.0f of the target" % range)

    def do_face(self, timeout=60, **_):
        """Turn to face the target."""
        for _ in _frames(timeout):
            me = self.me()
            if me.facing == self.toward() and self.grounded_idle(me):
                return {}
            self.tick(stick=(self.toward() * 0.3, 0))
            self.tick()
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
                self.tick(stick=pad["stick"])
        self.tick(**pad)
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
            self.tick()
        return dict(states=states,
                    damage=round(self.them().percent - before, 1))

    def do_wait(self, frames=None, until=None, timeout=600, **_):
        """Wait a number of frames, or until a condition holds:
        "target_grounded", "target_airborne", "in_range:<units>"."""
        if frames is not None:
            for _ in _frames(frames):
                self.tick()
            return {}
        for _ in _frames(timeout):
            if self._condition(until):
                return {}
            self.tick()
        raise StepFailed("waited %d frames for %s" % (timeout, until))

    def do_hold(self, frames, buttons=(), stick=(0, 0), **_):
        """Hold an input for a number of frames (shield, crouch...)."""
        for _ in _frames(frames):
            kw = dict(buttons=list(buttons), stick=tuple(stick))
            if "R" in buttons:
                kw["r"] = 1.0
            self.tick(**kw)
        return {}

    def _condition(self, text):
        them = self.them()
        if text == "target_grounded":
            return not them.airborne
        if text == "target_airborne":
            return them.airborne
        if text and text.startswith("in_range:"):
            return abs(self.dx()) <= float(text.split(":")[1])
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
        if what.startswith("in_range:"):
            d = abs(self.dx())
            return d <= float(what.split(":")[1]), "distance %.1f" % d
        raise StepFailed("unknown expectation %r" % what)

    # ---- running a script ---------------------------------------------------

    def run(self, script):
        """Execute `script`. Returns {"success", "frames", "steps": [...]}."""
        since = dict(percent=self.them().percent)
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
                    entry.update(handler(**args))
            except StepFailed as e:
                entry.update(failed=str(e))
                ok = False
                self.log.append(entry)
                break
            self.log.append(entry)
        self.sim.pad(self.port)
        return dict(success=ok, frames=self.frame, steps=self.log)


def _frames(n):
    return range(int(n))
