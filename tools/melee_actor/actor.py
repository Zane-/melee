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
WALKS = (15, 16, 17)             # slow, middle, fast
TURN = 18
DASH = 20
RUN = 21
KNEEBEND = 24
SQUAT_FIRST, SQUAT_LAST = 39, 41
LANDING = 42
ATTACK_FIRST, ATTACK_LAST = 44, 74     # jab 1 .. down air
CATCH_FIRST, CATCH_LAST = 212, 215     # grab, dash grab, and pulling in
GUARD_ON, GUARD, GUARD_OFF, GUARD_STUN, GUARD_REFLECT = 178, 179, 180, 181, 182
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
# Out of shield, frame by frame. The shield button stays held where the
# move needs it (a shield grab is A with the shield up); the up smash is
# jump-cancelled, as out of a run.
OOS = {
    "grab": [dict(buttons=["R", "A"], r=1.0)],
    "usmash": [dict(buttons=["X"]), dict(cstick=(0, 1))],
    "jump": [dict(buttons=["X"])],
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


JUMP_F, JUMP_B = 25, 26
AIR_ATTACK_FIRST, AIR_ATTACK_LAST = 65, 69     # nair .. dair
AIR_LANDING_FIRST, AIR_LANDING_LAST = 70, 74   # their landing lag

# Aerials, by what is pressed. "front" and "back" are the actor's facing
# (an aerial does not turn it round). A nair is A with the stick at rest
# for that frame: A with the stick held is a directional aerial.
AERIALS = {
    "nair": dict(buttons=["A"], rest=True),
    "fair": dict(cstick="front"),
    "bair": dict(cstick="back"),
    "uair": dict(cstick=(0, 1)),
    "dair": dict(cstick=(0, -1)),
}
# Frames X is held: a short hop lets go inside the jump squat, a full hop
# holds through the longest one (Bowser's 8).
HOPS = {"short": 1, "full": 9}
# Grounded moves `strike` knows, frame by frame ("toward" as in MOVES). A
# tilt rests the stick first: moved and pressed together it is a smash.
STRIKES = {
    "jab": [dict(buttons=["A"])],
    "ftilt": [dict(stick=("toward*0.4", 0))] * TILT_SETTLE +
             [dict(buttons=["A"], stick=("toward*0.4", 0))],
    "utilt": [dict(stick=(0, 0.4))] * TILT_SETTLE +
             [dict(buttons=["A"], stick=(0, 0.4))],
    "dtilt": [dict(stick=(0, -0.4))] * TILT_SETTLE +
             [dict(buttons=["A"], stick=(0, -0.4))],
    "fsmash": [dict(cstick=("toward", 0))],
    "usmash": [dict(cstick=(0, 1))],
    "dsmash": [dict(cstick=(0, -1))],
    "grab": [dict(buttons=["Z"])],
}
# Frames a lookahead goes on after the input, at most: long enough for any
# common attack's hitboxes to have come and gone.
STRIKE_LOOK = 30
# Frames an aerial approach dashes away for when the target is too close
# for any jump-in to land, before it looks again.
RETREAT = 10
# Lookaheads a step may make in one frame. Each costs about 5 ms on the
# unoptimised build; a live game has about 16 for everything.
LOOK_BUDGET = 3


class StepFailed(Exception):
    pass


_reach = None
# (character, aerial, hop) -> when it leaves the ground, lands, and has
# the aerial's hitbox out (Actor._hop_profile)
_PROFILES = {}


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
                 stage="final-destination", rng=None):
        """sim: a Native or a Sim in a match. port / target: fighter
        indices. other: optional function(sim, frame) called each frame to
        drive the target's pad (a test's stand-in for the player). rng: a
        random.Random for `choose` steps (seeded by whoever runs the
        script, so a run can be repeated)."""
        import random
        self.rng = rng or random.Random(0)
        self.limit = STAGE_LIMIT[stage]
        self.sim = sim
        self.port = port
        self.target = target
        self.other = other
        self.frame = 0
        self.log = []
        # lookaheads (ahead.py): how many, their time, at most per frame
        self.looks = 0
        self.look_ms = 0.0
        self.look_budget = LOOK_BUDGET
        self._budget_at, self._budget_used = -1, 0
        # the frame an attack step committed (its first input given), for
        # whoever times things from the attack (a drill's clock)
        self.committed = None

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
        out = yield from self._recover(before, timeout)
        out["started_at"] = round(at, 1)
        return out

    def _recover(self, before, timeout):
        """After an input: let it play out. Ends when the actor can act
        again or is holding the target; returns what it went through."""
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
        return dict(states=states, grabbed=grabbed,
                    damage=round(self.them().percent - before, 1))

    def do_shield(self, until="blocked", frames=None, timeout=300, **_):
        """Hold the shield up: for a number of `frames`, or `until`
        "blocked" (it has taken a hit and the stun from it is over: the
        first frame something can be done out of shield), or until any
        condition `wait` knows. The shield stays up when the step ends, so
        the next step can act out of it."""
        shield = dict(buttons=["R"], r=1.0)
        if frames is not None:
            for _ in _frames(frames):
                yield dict(shield)
            return {}
        stunned = False
        for n in _frames(timeout):
            me = self.me()
            if until == "blocked":
                if me.state == GUARD_STUN:
                    stunned = True
                elif stunned and me.state in (GUARD, GUARD_ON):
                    return dict(blocked=True, held=n,
                                shield=round(me.shield, 1))
                elif me.hitstun > 0 or me.percent > 0 and me.hitlag > 0 \
                        and me.state not in (GUARD_STUN, GUARD,
                                             GUARD_ON, GUARD_REFLECT):
                    raise StepFailed("was hit instead of blocking")
            elif self._condition(until):
                return dict(held=n)
            yield dict(shield)
        raise StepFailed("held the shield %d frames and nothing %s"
                         % (timeout, "hit it" if until == "blocked"
                            else "happened"))

    def do_oos(self, move, timeout=120, **_):
        """Act out of shield: "grab" (a shield grab), "usmash" (jump
        cancelled) or "jump". Use right after `shield`."""
        if move not in OOS:
            raise StepFailed("no way out of shield with %r" % move)
        if self.me().state not in (GUARD_ON, GUARD, GUARD_STUN,
                                   GUARD_REFLECT):
            raise StepFailed("not in shield")
        before = self.them().percent
        for pad in OOS[move]:
            yield self._resolve(pad)
        return (yield from self._recover(before, timeout))

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

    # ---- attacks that connect: the game is asked first (ahead.py) ---------------
    #
    # An attack in a drill is there to be answered: shielded, dodged, beaten
    # to the punch. If it can miss by itself, because the player walked a
    # step, the drill teaches nothing. So these steps commit only to inputs
    # the game, played ahead with the player holding what they hold now,
    # says will land; until then they move, wait or re-aim. What the
    # player does after the commitment is theirs to do.

    def _look(self, pads, stop=1):
        """Play per-frame `pads` (resolved) ahead; an Outlook."""
        if not hasattr(self.sim, "_cmd"):
            raise StepFailed("looking ahead needs the native build")
        try:
            from melee_actor.ahead import compress, look
        except ImportError:
            from ahead import compress, look
        if self._budget_at != self.frame:
            self._budget_at, self._budget_used = self.frame, 0
        self._budget_used += 1
        self.looks += 1
        out = look(self.sim, self.port, self.target, compress(pads), stop)
        self.look_ms += out.ms
        return out

    def _can_look(self):
        return self._budget_at != self.frame or \
            self._budget_used < self.look_budget

    def _along(self, out, toward):
        """How far past the target (+) or short of it (-) the nearest
        hitbox of a missed look came, measured toward the target."""
        facing = out.rows[out.near].a_facing if out.near is not None else 1
        return out.gx * facing * toward

    def _aerial_pads(self, move, hop, s, p, length, toward, facing,
                     lcancel=None):
        """A jump-in, frame by frame: X on frame 0 (held for the hop), the
        stick at `s` toward the target all along, the aerial on frame `p`,
        and R on frame `lcancel` (before the landing: an L-cancel)."""
        spec = AERIALS[move]
        pads = []
        for i in range(length):
            pad = dict(stick=(s * toward, 0.0))
            buttons = ["X"] if i < HOPS[hop] else []
            if i == p:
                buttons += spec.get("buttons", [])
                if spec.get("rest"):
                    pad["stick"] = (0.0, 0.0)
                cs = spec.get("cstick")
                if cs == "front":
                    pad["cstick"] = (facing, 0.0)
                elif cs == "back":
                    pad["cstick"] = (-facing, 0.0)
                elif cs is not None:
                    pad["cstick"] = cs
            if i == lcancel:
                buttons.append("R")
                pad["r"] = 1.0
            if buttons:
                pad["buttons"] = buttons
            pads.append(pad)
        return pads

    def _hop_profile(self, move, hop):
        """When this fighter leaves the ground and lands with this hop,
        and how many frames after the button `move` has a hitbox out: looked
        at once (straight up, so nothing is hit), then remembered."""
        key = (self.me().ckind, move, hop)
        if key in _PROFILES:
            return _PROFILES[key]
        toward, facing = self.toward(), self.me().facing
        prof = None
        for p in (9, 4):
            out = self._look(self._aerial_pads(move, hop, 0.0, p, 90, toward,
                                               facing), stop=0)
            rows = out.rows
            air = next((i for i, r in enumerate(rows) if r.a_air), None)
            if air is None:
                break
            land = next((i for i in range(air, len(rows))
                         if not rows[i].a_air), len(rows))
            hit = [i for i in range(p, land) if rows[i].a_hitbox]
            if hit:
                prof = dict(air=air, land=land, first=hit[0] - p,
                            last=hit[-1] - p)
                break
        if prof is None:
            raise StepFailed("%s from a %s hop never had a hitbox out"
                             % (move, hop))
        _PROFILES[key] = prof
        return prof

    def _plan_aerial(self, move, hop, connect, prof, lcancel=False):
        """Look for a jump-in that lands if begun now: a generator that
        yields when this frame's looks are spent (it goes on next frame,
        from the situation then) and returns (plan, out) when one lands
        (plan: the _jump_in parameters; the look that found it is of the
        frame it returns on), else (None, why): "far" or "close"."""
        toward, facing = self.toward(), self.me().facing
        late = prof["land"] - 2 - prof["first"]
        times = [p for p in (late, late - 3, late - 6) if p >= prof["air"]]
        if not times:
            times = [prof["air"]]
        length = prof["land"] + 2

        def attempt(s, p):
            plan = dict(move=move, hop=hop, s=s, p=p, length=length,
                        toward=self.toward(), facing=self.me().facing,
                        lcancel=prof["land"] - 3 if lcancel else None)
            return plan, self._look(self._jump_in(plan))

        why = "close"
        for p in times:
            # Where the hitbox comes, along the line to the target, is
            # about linear in the drift: full in, none, then in between
            # (or away, then in between) by where the two straddle zero.
            tried = []
            for s in (1.0, 0.0, None, -1.0, None):
                if s is None:
                    pts = sorted(tried)
                    s = next((s0 + (s1 - s0) * -a0 / (a1 - a0)
                              for (s0, a0), (s1, a1) in zip(pts, pts[1:])
                              if a0 <= 0 <= a1 and a1 != a0), None)
                    if s is None or any(abs(s - q) < 0.02 for q, _ in pts):
                        continue
                elif tried and s == -1.0 and min(a for _, a in tried) <= 0:
                    continue          # straddled already: no need to back off
                while not self._can_look():
                    yield
                plan, out = attempt(s, p)
                if out.connects(connect):
                    return plan, out
                if out.gap >= 900 or out.contact is not None:
                    break             # no hitbox came, or they hit first
                along = self._along(out, toward)
                tried.append((s, along))
                if s == 1.0 and along < 0:
                    # short even drifting in all the way: too far now (an
                    # earlier swing reaches less far still)
                    return None, "far"
        return None, why

    def do_aerial(self, move="nair", hop="short", connect="any",
                  track="air", timeout=600, fallback=True, lcancel=False,
                  **_):
        """Jump in with `move` ("nair", "fair", "bair", "uair", "dair")
        from a "short" or "full" hop, so that it lands: hits the target or
        its shield (`connect`: "any", "hit", "shield"). On the ground, each
        frame the jump is looked at before it is made; while it would miss,
        the actor closes in (too far) or holds (too close). `track`: "air"
        keeps re-aiming the drift in the air until the hitbox is out and
        gone; "jump" commits to the plan at the jump, so a player who
        moves after seeing the jump makes it miss (that is the counterplay
        a wavedash-back drill teaches). `fallback`: after `timeout` frames
        with nothing found, jump in anyway rather than fail. `lcancel`: R
        three frames before the landing."""
        if move not in AERIALS or hop not in HOPS:
            raise StepFailed("no aerial %r from a %r hop" % (move, hop))
        need = -1.0 if move == "bair" else 1.0
        plan = out = search = None
        waited = 0
        prof = None
        moving = {}
        retreat = 0
        for waited in _frames(timeout):
            me = self.me()
            want = need * self.toward()
            idle = self.grounded_idle(me) or me.state in (DASH, RUN) + WALKS
            if me.airborne or not idle:
                yield {}
                continue
            if retreat > 0:
                # too close for any jump-in: dash off a little, come again
                retreat -= 1
                search = None
                away = -self.toward()
                if abs(me.pos[0] + away * 6) > self.limit:
                    retreat = 0
                yield dict(stick=(away, 0)) if retreat > 0 else {}
                continue
            if me.facing != want:
                if me.state in (DASH, RUN):
                    yield dict(stick=(want, 0))     # dash back the other way
                else:
                    yield dict(stick=(want * 0.3, 0))      # turn round
                continue
            if prof is None:
                prof = self._hop_profile(move, hop)
            if search is None:
                search = self._plan_aerial(move, hop, connect, prof,
                                           lcancel)
            try:
                next(search)
                yield moving                     # still looking
                continue
            except StopIteration as done:
                search = None
                plan, why = done.value
            if plan is not None:
                out = why
                break
            going_off = abs(me.pos[0] + self.toward() * 4) > self.limit
            if why == "far" and not going_off and \
                    (move != "bair" or abs(self.dx()) > 45):
                # close in at a dash: from a walk the stick goes back to
                # the middle for a frame first, or it only walks faster
                moving = {} if me.state in WALKS and abs(self.dx()) > 30 \
                    else dict(stick=(self.toward(), 0))
            elif why == "close" and move != "bair":
                retreat = RETREAT
                moving = {}
            else:
                moving = {}
            yield moving
        if plan is None:
            if not fallback:
                raise StepFailed("never found a %s that lands" % move)
            prof = prof or self._hop_profile(move, hop)
            plan = dict(move=move, hop=hop, s=1.0,
                        p=max(prof["air"], prof["land"] - 2 - prof["first"]),
                        length=prof["land"] + 2, toward=self.toward(),
                        facing=self.me().facing,
                        lcancel=prof["land"] - 3 if lcancel else None)
        result = dict(waited=waited, foreseen=out.contact if out else None,
                      drift_planned=round(plan["s"], 2))
        before = dict(percent=self.them().percent, own=self.me().percent)
        contact = None
        self.committed = self.frame
        for i in range(plan["length"]):
            if track == "air" and i > 0 and contact is None and \
                    self._can_look() and self.me().airborne:
                plan = self._reaim(plan, i, connect)
            yield self._jump_in(plan)[i]
            contact = contact or self._contact(before)
        for _ in _frames(60):                  # the landing, its lag
            contact = contact or self._contact(before)
            if self.grounded_idle(self.me()):
                break
            yield {}
        result.update(contact=contact, drift=round(plan["s"], 2),
                      pressed=plan["p"])
        return result

    def _jump_in(self, plan):
        return self._aerial_pads(plan["move"], plan["hop"], plan["s"],
                                 plan["p"], plan["length"], plan["toward"],
                                 plan["facing"], plan.get("lcancel"))

    def _reaim(self, plan, i, connect):
        """In the air, `i` frames into a jump-in: the plan with its drift
        changed if the target has moved so that it would now miss. The
        press stays on its frame."""
        out = self._look(self._jump_in(plan)[i:])
        if out.connects(connect) or out.contact == "beaten" or \
                out.gap >= 900:
            return plan
        toward = plan["toward"]
        along = self._along(out, toward)
        s = plan["s"]
        s2 = 1.0 if along < 0 else -1.0
        if s2 == s or not self._can_look():
            return plan
        alt = dict(plan, s=s2)
        o2 = self._look(self._jump_in(alt)[i:])
        if o2.connects(connect) or o2.gap >= 900:
            return alt if o2.connects(connect) else plan
        a2 = self._along(o2, toward)
        best, err = (alt, abs(a2)) if abs(a2) < abs(along) else \
            (plan, abs(along))
        if a2 * along < 0 and self._can_look():
            mid = dict(plan, s=s + (s2 - s) * along / (along - a2))
            o3 = self._look(self._jump_in(mid)[i:])
            if o3.connects(connect):
                return mid
            if o3.gap < 900 and abs(self._along(o3, toward)) < err:
                best = mid
        return best

    # ---- a designed sequence, started where it lands ---------------------------

    @staticmethod
    def _drift(inputs, s):
        """`inputs` with the main stick's sideways part scaled by `s` (the
        drift of a jump-in; 1 = as designed)."""
        if s == 1.0:
            return inputs
        out = []
        for pad in inputs:
            stick = pad.get("stick")
            if stick is None or not stick[0]:
                out.append(pad)
                continue
            x = stick[0]
            if isinstance(x, str):
                k = float(x.split("*")[1]) if "*" in x else 1.0
                x = ("toward*%g" if x.startswith("toward") else "away*%g") \
                    % (k * s)
            else:
                x = x * s
            out.append(dict(pad, stick=(x, stick[1])))
        return out

    def _resolve_all(self, inputs):
        out = []
        for pad in inputs:
            pad = dict(pad)
            for key in ("stick", "cstick"):
                if key in pad:
                    pad[key] = tuple(
                        v if not isinstance(v, str) else
                        (-1.0 if v.startswith("away") else 1.0) *
                        self.toward() * (float(v.split("*")[1])
                                         if "*" in v else 1.0)
                        for v in pad[key])
            out.append(pad)
        return out

    def do_sequence(self, inputs, distance=None, tolerance=3.0,
                    face="toward", connect="any", track="jump", look=30,
                    drifts=(1.0, 0.6, 0.3), still=True, precision=None,
                    timeout=600, fallback=True, **_):
        """A designed attack, frame by frame (`inputs`: pads as `pad`
        takes them, a stick's x "toward*k" or "away*k" of the target),
        started only where it lands. The actor gets to `distance` from the
        target (centre to centre, within `tolerance`; None: from anywhere),
        facing it (`face` "toward", "away" or None), and looks ahead with
        the sequence played through and `look` frames more: it commits
        when the attack lands (`connect`), the sideways stick scaled by
        `drifts` in turn if as designed it would not; otherwise it waits
        for the player and moves with them. A drill's attack keeps its
        timing, its landing and what it leaves open: only where it starts
        follows the player. `track` "air": in the air the drift is scaled
        to stay on target, as in `aerial`. `still`: start only from a
        standstill, as the sequence was designed (sliding out of a walk, a
        jump carries the slide and reaches further than designed).
        `precision`: once stopped too far by more than this, step in by
        one-frame taps whose stopping point the game is asked for first."""
        def band():
            return distance is None or \
                abs(abs(self.dx()) - distance) <= tolerance
        go = out = None
        waited = 0
        taps = 0
        closing = []          # the distance while walking in
        blocked = False       # walking in no longer gets it closer
        for waited in _frames(timeout):
            me = self.me()
            dist = abs(self.dx())
            idle = self.grounded_idle(me) or me.state in WALKS + (DASH, RUN)
            if me.airborne or not idle:
                yield {}
                continue
            going_off = abs(me.pos[0] + self.toward() * 4) > self.limit
            backing_off = abs(me.pos[0] - self.toward() * 4) > self.limit
            if distance is not None and me.state in WALKS + (DASH, RUN) \
                    and abs(dist - distance) < 30 and self._can_look():
                # Where it would stop, let go of now (a walk or a run
                # slides): let go once that is no longer too far (a run
                # covers the band in less than a frame).
                rows = self._look([{}] * 20, stop=0).rows
                if rows and abs(rows[-1].t_x - rows[-1].a_x) <= \
                        distance + tolerance:
                    yield {}
                    continue
            if distance is not None and dist > distance:
                closing.append(dist)
                if len(closing) >= 4 and closing[-4] - dist < 0.2:
                    blocked = True       # bodies touching: as close as it gets
            else:
                closing = []
            if not band() and not blocked and \
                    not (dist > distance and going_off) and \
                    not (dist < distance and backing_off):
                if dist > distance + 18:
                    yield ({} if me.state in WALKS else
                           dict(stick=(self.toward(), 0)))      # run
                elif dist > distance + 6:
                    yield dict(stick=(self.toward() * 0.45, 0))   # walk in
                elif dist > distance:
                    yield dict(stick=(self.toward() * 0.3, 0))    # slowly
                else:
                    yield dict(stick=(-self.toward() * 0.45, 0))  # back off
                continue
            if me.state in (DASH, RUN) + WALKS or \
                    (still and abs(me.vel[0]) > 0.02):
                yield {}                       # stop where it is
                continue
            want = self.toward() * (-1.0 if face == "away" else 1.0)
            if face is not None and me.facing != want:
                yield dict(stick=(want * 0.3, 0))
                continue
            if precision is not None and distance is not None and \
                    not blocked and dist - distance > precision and \
                    taps < 8 and self._can_look():
                # a fraction too far: the tap whose stop is nearest
                best, err = None, dist - distance
                for k in (0.2, 0.25, 0.3, 0.35):
                    if not self._can_look():
                        break
                    rows = self._look([dict(stick=(self.toward() * k, 0))] +
                                      [{}] * 15, stop=0).rows
                    e = abs(abs(rows[-1].t_x - rows[-1].a_x) - distance)
                    if e < err:
                        best, err = k, e
                if best is not None:
                    taps += 1
                    yield dict(stick=(self.toward() * best, 0))
                    continue
            for s in drifts:
                if not self._can_look():
                    break
                pads = self._resolve_all(self._drift(inputs, s))
                out = self._look(pads + [{}] * look)
                if out.connects(connect):
                    go = s
                    break
            if go is not None:
                break
            yield {}
        if go is None:
            if not fallback:
                raise StepFailed("the sequence never would have landed")
            go = 1.0
        before = dict(percent=self.them().percent, own=self.me().percent)
        contact = None
        s = go
        self.committed = self.frame
        toward = self.toward()
        rest = None
        for i in range(len(inputs)):
            if track == "air" and i > 0 and contact is None and \
                    self.me().airborne and self._can_look():
                s = self._reaim_sequence(inputs, i, s, toward, connect, look)
            pads = self._drift(inputs, s)
            # the direction as it was at the commitment: a jump-in does not
            # turn round when it passes over the target
            pad = dict(pads[i])
            for key in ("stick", "cstick"):
                if key in pad:
                    pad[key] = tuple(
                        v if not isinstance(v, str) else
                        (-1.0 if v.startswith("away") else 1.0) * toward *
                        (float(v.split("*")[1]) if "*" in v else 1.0)
                        for v in pad[key])
            yield pad
            contact = contact or self._contact(before)
        for _ in _frames(90):          # the attack's end, a landing's lag
            contact = contact or self._contact(before)
            if self.grounded_idle(self.me()):
                break
            yield {}
        return dict(waited=waited, contact=contact, drift=round(s, 2),
                    foreseen=out.contact if out is not None else None,
                    distance=round(abs(self.dx()), 1))

    def _reaim_sequence(self, inputs, i, s, toward, connect, look):
        """In the air, `i` frames into a sequence: the drift scale that
        keeps it landing, or `s` if it still does or nothing does better."""
        def rest(scale):
            pads = []
            for pad in self._drift(inputs, scale)[i:]:
                pad = dict(pad)
                for key in ("stick", "cstick"):
                    if key in pad:
                        pad[key] = tuple(
                            v if not isinstance(v, str) else
                            (-1.0 if v.startswith("away") else 1.0) *
                            toward * (float(v.split("*")[1])
                                      if "*" in v else 1.0)
                            for v in pad[key])
                pads.append(pad)
            return pads + [{}] * look
        out = self._look(rest(s))
        if out.connects(connect) or out.gap >= 900 or out.contact:
            return s
        along = self._along(out, toward)
        for s2 in ((1.0 if along < 0 else 0.0), (s + 1.0) / 2
                   if along < 0 else s / 2):
            if s2 == s or not self._can_look():
                continue
            if self._look(rest(s2)).connects(connect):
                return s2
        return s

    def _contact(self, before):
        """What has happened since `before`: "hit", "shield", "beaten"."""
        me, them = self.me(), self.them()
        if me.percent > before["own"]:
            return "beaten"
        if them.percent > before["percent"]:
            return "hit"
        if them.hitlag > 0 and them.state in (GUARD_ON, GUARD, GUARD_OFF,
                                              GUARD_STUN, GUARD_REFLECT):
            return "shield"
        return None

    def do_strike(self, move, connect="any", timeout=600, fallback=False,
                  **_):
        """A grounded attack ("jab", "ftilt", "utilt", "dtilt", "fsmash",
        "usmash", "dsmash", "grab") that lands: each frame the actor
        could start it, the game is asked whether it would hit the target
        or its shield; until it would, the actor walks in (runs from far)
        or waits. `fallback`: after `timeout`, swing anyway."""
        if move not in STRIKES:
            raise StepFailed("no strike %r" % move)
        before = None
        go = None
        waited = 0
        for waited in _frames(timeout):
            me = self.me()
            dist = abs(self.dx())
            if me.airborne or not (self.grounded_idle(me) or
                                   me.state in (DASH, RUN) + WALKS):
                yield {}
                continue
            going_off = abs(me.pos[0] + self.toward() * 4) > self.limit
            if me.state in (DASH, RUN):
                # out of a run, A is a dash attack: run or stop first
                if dist > 40 and not going_off:
                    yield dict(stick=(self.toward(), 0))
                else:
                    yield {}
                continue
            if me.facing != self.toward():
                yield dict(stick=(self.toward() * 0.3, 0))
                continue
            if not self._can_look():
                yield {}
                continue
            pads = [self._resolve(p) for p in STRIKES[move]]
            out = self._look(pads + [{}] * STRIKE_LOOK)
            if out.connects(connect):
                go = (pads, out)
                break
            along = self._along(out, self.toward()) if out.gap < 900 \
                else None
            if along is not None and along < 0 and not going_off:
                if dist > 40:
                    yield dict(stick=(self.toward(), 0))       # run in
                else:
                    yield dict(stick=(self.toward() * 0.45, 0))  # walk in
            else:
                yield {}
        if go is None:
            if not fallback:
                raise StepFailed("never close enough for a %s that lands"
                                 % move)
            go = ([self._resolve(p) for p in STRIKES[move]], None)
        pads, out = go
        before = dict(percent=self.them().percent, own=self.me().percent)
        contact = None
        self.committed = self.frame
        for pad in pads:
            yield pad
            contact = contact or self._contact(before)
        states = []
        for _ in _frames(120):
            contact = contact or self._contact(before)
            me = self.me()
            if me.state not in states:
                states.append(me.state)
            if len(states) > 1 and self.grounded_idle(me):
                break
            yield {}
        return dict(waited=waited, contact=contact,
                    foreseen=out.contact if out else None,
                    distance=round(abs(self.dx()), 1))

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
        """Hold an input for a number of frames (shield, crouch...). A
        stick axis may be "toward" or "away" (from the target): R with the
        stick away is a roll back."""
        for _ in _frames(frames):
            kw = self._resolve(dict(buttons=list(buttons),
                                    stick=tuple(stick)))
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
        {"success", "frames", "steps": [...]} when the script is over.

        Besides steps and expectations a script may hold
        {"choose": [script, script, ...], "weights": [...]}: one of the
        branches, picked by the actor's random source, is run in its place.
        That is how an opponent varies what it does from run to run."""
        since = dict(percent=self.them().percent, own=self.me().percent)
        ok = yield from self._script(script, since)
        return dict(success=ok, frames=self.frame, steps=self.log)

    def _script(self, script, since):
        ok = True
        for step in script:
            # logged when it starts, so a step that is cut short (the run
            # ended, the fighter was grabbed) still shows when it began
            entry = dict(step=step, at=self.frame)
            self.log.append(entry)
            try:
                if "choose" in step:
                    branches = step["choose"]
                    pick = self.rng.choices(
                        range(len(branches)),
                        weights=step.get("weights"))[0]
                    entry.update(step=dict(choose=len(branches)), chose=pick)
                    if not (yield from self._script(branches[pick], since)):
                        return False
                elif "expect" in step:
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
                return False
        return ok

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
