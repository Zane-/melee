"""universal-l-cancel, universal-shffl, universal-dash-dance,
universal-jc-grab, universal-jc-upsmash.

Port of src/tmce/events/course/drills/tech_movement.inc.h (specs:
data/courses/universal.md).

Measured with Fox in the simulator (2026-11-12):
  - Neutral air landing lasts 15 frames, 7 when L-cancelled (the table's
    `land` / `land_l`). The trigger press counts when it is 0 to 6 frames
    before the frame the landing begins; 7 before is too early.
  - Holding down while falling lands a short hop down air 5 frames
    sooner (fast fall).
  - Dash turns into run after 11 frames of holding the stick; reversing
    earlier gives one frame of Turn and a new Dash.
  - Running, jump then Z 1 or 2 frames later: jump squat into the
    standing grab (Catch). Z on the same frame as jump is the dash grab
    (CatchDash); Z 3 frames later comes out as an aerial.
"""
import struct

from melee_course.engine import (
    L, R, Z, A, X, Y, Drill, Option, Ref, Row, tapped_down, smashed_up,
    WAIT, TURN, DASH, RUN, KNEEBEND, JUMP_F, JUMP_B, LANDING, ATTACK_DASH,
    ATTACK_HI4, ATTACK_AIR_N, ATTACK_AIR_LW, LANDING_AIR_N, LANDING_AIR_LW,
    CATCH, CATCH_DASH)

AERIALS = ("nair", "fair", "bair", "uair", "dair")


def is_aerial(state):
    return ATTACK_AIR_N <= state <= ATTACK_AIR_LW


def is_aerial_landing(state):
    return LANDING_AIR_N <= state <= LANDING_AIR_LW


def was_l_cancelled(c, landing_state, frames):
    """The landing of aerial `landing_state` was L-cancelled if it lasted
    `frames`."""
    m = c.fd.move[AERIALS[landing_state - LANDING_AIR_N]]
    return frames * 2 < m.land + m.land_l


def is_fast_fall(c):
    """hd->flags.is_fastfall, which the native build does not report: a
    fast fall sets the fall speed to the fast-fall speed, which is above
    the terminal speed a plain fall stops at (every character's is), so
    falling faster than halfway between the two is a fast fall."""
    fd = c.fd
    return c.me.airborne and \
        c.me.vel[1] < -(fd.fastfall_velocity + fd.terminal_velocity) / 2


TRIGGERS = L | R | Z
# Latest and earliest frames before landing a trigger press counts.
LCANCEL_WINDOW = 6
# The landing's frame on the L-cancel timeline: room for the window and a
# press or two too early before it.
TL_LAND = 10
AIR_TIMEOUT = 150


# ---- the demonstration for L-cancel and SHFFL -------------------------------

# Built for the character and the aerial: jump, the aerial, fast fall, the
# trigger press. The landing is predicted from the hop speed, gravity and
# fast-fall speed (the game's own recursion: y += v, v -= gravity), so no
# scouting hop is needed; the simulator's traces put the landing one or two
# frames after the predicted height crosses zero, and the L-cancel window
# (7 frames) absorbs that. The aerial is timed to be a few frames past its
# first hit when the fighter lands: started at takeoff, many aerials end
# in the air or autocancel (Marth's neutral air, most slow down airs).
# Each demonstration shows the next aerial: neutral, forward, back, up,
# down.
REF_START = 10            # script frame of the jump press
REF_TAP_FROM = 4          # first airborne frame with a stick-down tap
REF_TAP_EVERY = 3
REF_PAST_HIT = 4          # aerial frames past its first hit at landing
# ...but this many frames inside the last frame that still has landing lag:
# past it the aerial autocancels (Sheik's forward air: lag on frames 5-10);
# the landing comes the frame after the height crosses zero
REF_LAG_SLACK = 3
REF_PRESS_BEFORE = 2      # trigger this long before the height is 0
REF_MAX = 40


def _f32(x):
    """A float as the C's single precision holds it."""
    return struct.unpack("f", struct.pack("f", x))[0]


def is_tap(k):
    return k >= REF_TAP_FROM and (k - REF_TAP_FROM) % REF_TAP_EVERY == 0


# neutral (A), forward, back, up, down (the C-stick)
_AERIAL_INPUT = (dict(buttons=A), dict(cx=127), dict(cx=-127),
                 dict(cy=127), dict(cy=-127))


def build_aerial_reference(c):
    me = c.fd
    which = (c.demo_count + 4) % 5         # the first one: neutral
    m = me.move[AERIALS[which]]
    # script frame of airborne frame 1
    air0 = REF_START + me.jump_squat
    v, y = _f32(me.hop_v), 0.0
    gravity = _f32(me.gravity)
    ff = _f32(me.fastfall_velocity)
    terminal = _f32(me.terminal_velocity)
    fast = False
    cross = 1
    while cross < 200:
        # the game fast-falls on a tap when the speed it started the frame
        # with is downward: v + gravity (v is after this frame's gravity)
        if not fast and _f32(v + gravity) < 0 and is_tap(cross):
            v = -ff
            fast = True
        y = _f32(y + v)
        if y < 0:
            break
        if not fast:            # a fast fall keeps its speed
            v = _f32(v - gravity)
            if v < -terminal:
                v = -terminal
        cross += 1
    at = m.hit + REF_PAST_HIT       # the aerial's frame at landing
    if m.lag_to > 0 and at > m.lag_to - REF_LAG_SLACK:
        at = m.lag_to - REF_LAG_SLACK
    if at < m.lag_from:
        at = m.lag_from
    aerial = cross - at
    # the tap on the aerial's frame is left out (down with A is a down
    # air); when that was the tap that starts the fast fall, the landing
    # came three frames late, past the lag: the aerial comes a frame
    # earlier instead (as the C now does)
    if is_tap(aerial):
        aerial -= 1
    if aerial < 1:
        aerial = 1

    ref = [Ref(0, REF_START, 1, buttons=X),
           Ref(0, air0 + aerial - 1, 1, **_AERIAL_INPUT[which])]
    k = REF_TAP_FROM
    while k <= cross and len(ref) < REF_MAX - 4:
        # no tap on the aerial's frame: down with A is a down air
        if is_tap(k) and k != aerial:
            ref.append(Ref(0, air0 + k - 1, 1, ly=-127))
        k += 1
    # Two presses five frames apart: for some characters (Mario, Luigi,
    # Peach, Zelda...) the landing comes up to six frames after the
    # prediction, past the first press's window. A press too early costs
    # nothing, and the second lands in the landing lag when the first was
    # right.
    press = air0 + cross - 1 - REF_PRESS_BEFORE
    ref.append(Ref(0, press, 1, buttons=Z))
    ref.append(Ref(0, press + 5, 1, buttons=Z))
    return ref


# ---- universal-l-cancel -----------------------------------------------------

class TechLCancel(Drill):
    id = "universal-l-cancel"
    name = "L-Cancel"
    goal = "Halve the landing lag of an aerial attack"
    part = "tech"
    cpu = None
    flow = True
    WAIT, AIR, LAND = range(3)
    help = ("L-cancel: jump, attack in the air, and press L, R",
            "or Z just before you land.",
            "D-Pad up: guide. D-Pad down: reset.")

    def build_reference(self, c):
        return build_aerial_reference(c)

    def guide(self, c):
        m = c.fd.move["dair"]
        return ["Landing during an aerial attack costs landing",
                "lag. Pressing L, R or Z just before you touch",
                "the ground halves it.",
                "Your down air: %d frames, %d with the cancel."
                % (m.land, m.land_l),
                "The press counts in the last 7 frames of the",
                "fall. Jump, attack late, press as you land."]

    def setup(self, c):
        c.place_solo(0.0)
        # air_frame, land_frame, land_state, lag keep their values across
        # attempts in the C (statics); each is set before it is read.
        self.v.setdefault("air_frame", 0)
        self.v.setdefault("land_frame", 0)
        self.v.setdefault("land_state", 0)
        self.v.setdefault("lag", 0)
        self.v["press_frame"] = -1

    def think(self, c):
        v = self.v
        if c.phase == self.WAIT:
            if is_aerial(c.state):
                c.set_phase(self.AIR)
                v["air_frame"] = 0
                v["press_frame"] = -1
        elif c.phase == self.AIR:
            v["air_frame"] += 1
            if c.down & TRIGGERS:
                v["press_frame"] = v["air_frame"]
            if is_aerial_landing(c.state):
                c.set_phase(self.LAND)
                c.tl_begin(back=TL_LAND - 1)
                v["land_frame"] = v["air_frame"]
                v["land_state"] = c.state
                v["lag"] = 1
            elif not is_aerial(c.state):
                if c.state == LANDING:
                    c.result(False, "No landing lag to cancel\n"
                             "attack later in the jump")
                else:
                    c.set_phase(self.WAIT)  # the aerial ended in the air
            elif v["air_frame"] > AIR_TIMEOUT:
                c.set_phase(self.WAIT)
        elif c.phase == self.LAND:
            if c.state == v["land_state"]:
                v["lag"] += 1
                if v["press_frame"] < 0 and c.down & TRIGGERS:
                    v["press_frame"] = v["land_frame"] + v["lag"] - 1
                return
            before = v["land_frame"] - v["press_frame"]
            c.report("lag", v["lag"])
            if v["press_frame"] >= 0:
                c.report("before", before)
            if was_l_cancelled(c, v["land_state"], v["lag"]):
                if v["press_frame"] >= 0:
                    c.result(True, "L-cancel! %d frames lag\n"
                             "pressed %d before landing"
                             % (v["lag"], before))
                else:
                    c.result(True, "L-cancel! %d frames lag" % v["lag"])
            elif v["press_frame"] < 0:
                c.result(False, "No press: %d frames lag\n"
                         "L, R or Z as you land" % v["lag"])
            elif before > LCANCEL_WINDOW:
                c.result(False, "Too early: %d frames before\n"
                         "landing, at most %d" % (before, LCANCEL_WINDOW))
            else:
                c.result(False, "Too late: %d frames after\nlanding"
                         % -before)

    def timeline(self, c):
        return ([Row("Press", buttons=TRIGGERS, trigger=True,
                     window=(TL_LAND - LCANCEL_WINDOW, TL_LAND)),
                 Row("Land", state=is_aerial_landing, perfect=(TL_LAND,))],
                "You land on frame %d: L, R or Z on frames %d to %d."
                % (TL_LAND, TL_LAND - LCANCEL_WINDOW, TL_LAND))


# ---- universal-shffl --------------------------------------------------------

class TechShffl(Drill):
    id = "universal-shffl"
    name = "SHFFL"
    goal = "Short hop, aerial, fast fall, L-cancel in one motion"
    part = "tech"
    cpu = None
    flow = True
    WAIT, SQUAT, AIR, LAND = range(4)
    help = ("SHFFL: short hop, aerial attack, tap down to fast",
            "fall, L-cancel the landing.",
            "D-Pad up: guide. D-Pad down: reset.")

    def build_reference(self, c):
        return build_aerial_reference(c)

    def guide(self, c):
        return ["Short Hop, Fast Fall, L-cancel: the fastest way",
                "to put an aerial attack on the ground.",
                "1. Short hop: release jump within %d frames."
                % (c.fd.jump_squat - 1),
                "2. Attack in the air.",
                "3. Fast fall: tap down once you start falling.",
                "4. L-cancel: L, R or Z in the last 7 frames.",
                "The verdict names the first part you missed."]

    @staticmethod
    def _clear():
        return dict(short_hop=0, aerial=0, fast_fall=0, frame=0,
                    press_frame=-1, land_frame=0, land_state=0, lag=0)

    def setup(self, c):
        c.place_solo(0.0)
        self.v = self._clear()

    def think(self, c):
        me = c.fd
        if c.phase == self.WAIT:
            if c.state == KNEEBEND:
                c.set_phase(self.SQUAT)
                c.tl_begin()
            return

        if c.phase == self.SQUAT:
            if c.state == KNEEBEND:
                return
            self.v = self._clear()
            self.v["short_hop"] = int(c.me.vel[1] < (me.hop_v + me.jump_v) / 2)
            c.set_phase(self.AIR)
            # fall through

        v = self.v
        if c.phase == self.AIR:
            v["frame"] += 1
            if c.down & TRIGGERS:
                v["press_frame"] = v["frame"]
            if is_fast_fall(c):
                v["fast_fall"] = 1
            if is_aerial(c.state):
                v["aerial"] = 1
            elif is_aerial_landing(c.state):
                c.set_phase(self.LAND)
                v["land_frame"] = v["frame"]
                v["land_state"] = c.state
                v["lag"] = 1
            elif c.state in (LANDING, WAIT):
                if v["aerial"]:
                    c.result(False, "No landing lag to cancel\n"
                             "attack later in the jump")
                else:
                    c.set_phase(self.WAIT)  # a plain jump: ignore
            elif v["frame"] > AIR_TIMEOUT:
                c.set_phase(self.WAIT)
            return

        if c.phase == self.LAND:
            if c.state == v["land_state"]:
                v["lag"] += 1
                return
            lcancel = int(was_l_cancelled(c, v["land_state"], v["lag"]))
            # frames from leaving the ground to acting again
            total = v["land_frame"] + v["lag"]
            c.measure(v["short_hop"] + v["fast_fall"] + lcancel, 3)
            c.report("short_hop", v["short_hop"])
            c.report("fast_fall", v["fast_fall"])
            c.report("l_cancel", lcancel)
            c.report("total", total)
            if not v["short_hop"]:
                c.result(False, "Full hop\nrelease jump within %d frames"
                         % (me.jump_squat - 1))
            elif not v["fast_fall"]:
                c.result(False, "No fast fall\ntap down as you fall")
            elif not lcancel:
                if v["press_frame"] < 0:
                    c.result(False, "No L-cancel\nL, R or Z as you land")
                else:
                    c.result(False, "L-cancel missed: pressed\n"
                             "%d frames before landing"
                             % (v["land_frame"] - v["press_frame"]))
            else:
                c.result(True, "SHFFL!\nacting again after %d frames"
                         % total)

    def timeline(self, c):
        js = c.fd.jump_squat
        land = js + self.v["land_frame"] if self.v.get("land_frame") else 0
        return ([Row("Jump", buttons=X | Y, held=True, perfect=(1,),
                     window=(1, js - 1)),
                 Row("Aerial", state=is_aerial),
                 Row("Fall", test=tapped_down),
                 Row("Press", buttons=TRIGGERS, trigger=True,
                     window=(land - LCANCEL_WINDOW, land) if land else None),
                 Row("Land", state=is_aerial_landing)],
                "Jump: frames held. Fall: taps down. Press: the 7 frames "
                "to the landing.")


# ---- universal-dash-dance ---------------------------------------------------

# Owner, 2026-11-13: "Dash dance and pivot should just be Dash dance. Also we
# shouldn't count for 6, let's just record the count of direction switches
# and show the user their longest dash dance hold! We should also build in
# targets (i.e. little light rays that come down on the stage) for the user
# to target so they can build in moving towards a target while dash
# dancing!" A dance is two dashes or more; it ends when the player stops or
# does something else (a success: so many switches) or runs (a failure:
# the turn came too late). Native only: the overlay's C drill still counts
# to a number of dashes.

def plural(n, word):
    return "%d %s" % (n, word if n == 1 else word + (
        "es" if word.endswith("ch") else "s"))


DD_IDLE = 2               # frames of standing a dash may run out into
TARGET_REACH = 7.0        # how near the middle of a ray counts as reaching it
TARGET_NEAR, TARGET_FAR = 20.0, 50.0   # a new ray, from where the player is
TARGET_MARGIN = 60        # of the picture's 640: a ray this far inside
TARGET_EDGE = 70.0        # rays stay this far inside the stage's middle


class TechDashDance(Drill):
    id = "universal-dash-dance"
    name = "Dash Dance"
    goal = "Dash back and forth without running"
    part = "tech"
    cpu = None
    flow = True
    OPT_TARGETS = 0
    WAIT, DANCE = range(2)
    options = (Option("Targets", ["On", "Off"], 0,
                      "Light rays on the stage to dance toward: reach one "
                      "and the next comes down."),)
    help = ("Dash dance: dash left and right, turning before",
            "the dash becomes a run. Dance to the light rays.",
            "D-Pad up: guide. D-Pad down: reset.")
    # Seven frames each way, twenty times: short enough for every
    # character's dash.
    reference = [r for n in range(10) for r in (
        Ref(0, 10 + 14 * n, 7, 127, 0), Ref(0, 17 + 14 * n, 7, -127, 0))]

    def guide(self, c):
        return ["Dash one way, then the other before the dash",
                "becomes a run. You stay mobile and can leave in",
                "either direction at any moment.",
                "Flick the stick fully left and right. Hold a",
                "direction too long and you run, and turning",
                "around out of a run is slow.",
                "A light ray on the stage: dance your way to it.",
                "Each turn counts; your longest dance is kept."]

    def init(self):
        self.best = 0             # the most switches in one dance
        self.target = None        # the ray's x, while targets are on
        self.reached = 0          # rays reached, all dances

    def targets_on(self, c):
        return c.opt(self.OPT_TARGETS) == 0 and not c.is_demo

    def status(self, c):
        best = "longest dance: %d switches" % self.best if self.best else \
            "no dance yet"
        if self.targets_on(c):
            return "Rays reached: %d. %s" % (self.reached, best[0].upper()
                                             + best[1:])
        return best[0].upper() + best[1:]

    def rays(self, c):
        """Where light rays come down on the stage now: [(x, y)]."""
        if not self.targets_on(c) or self.target is None:
            return []
        return [(self.target, 0.0)]

    def new_target(self, c):
        """A ray TARGET_NEAR to TARGET_FAR from the player, on the stage
        and in the picture: the camera is not always centred on a lone
        fighter (a ray 37 units away was once off the screen)."""
        x = c.me.pos[0]
        best = None
        for _ in range(12):
            d = TARGET_NEAR + c.randi(int(TARGET_FAR - TARGET_NEAR) + 1)
            t = x + (d if c.randi(2) else -d)
            if not -TARGET_EDGE <= t <= TARGET_EDGE:
                continue
            best = t
            if self.in_view(c, t):
                break
        if best is None:
            best = max(-TARGET_EDGE, min(TARGET_EDGE, -x))
        self.target = best

    @staticmethod
    def in_view(c, x):
        """Is stage point (x, 0) well inside the picture?"""
        try:
            sx, _ = c.n.project(x, 0.0)
        except Exception:         # a game without the command
            return True
        return TARGET_MARGIN <= sx <= 640 - TARGET_MARGIN

    def setup(self, c):
        c.place_solo(0.0)
        self.v = dict(dashes=0, length=0, longest=0, idle=0, reached=0)

    def end(self, c, ran):
        v = self.v
        switches = v["dashes"] - 1
        record = switches > self.best
        self.best = max(self.best, switches)
        c.measure(switches, self.best)
        c.report("dashes", v["dashes"])
        c.report("switches", switches)
        c.report("longest", v["longest"])
        c.report("best", self.best)
        rays = ", %s" % plural(v["reached"], "ray") \
            if self.targets_on(c) else ""
        if ran:
            c.result(False, "Ran after %s%s\nturn sooner"
                     % (plural(switches, "switch"), rays))
        else:
            c.result(True, "%s%s\n%s" % (
                plural(switches, "switch"), rays,
                "a new best" if record and switches > 1
                else "best %d" % self.best))

    def think(self, c):
        v = self.v
        if self.targets_on(c):
            if self.target is None:
                self.new_target(c)
            elif c.state in (DASH, TURN) and \
                    abs(c.me.pos[0] - self.target) <= TARGET_REACH:
                self.reached += 1
                v["reached"] += 1
                self.new_target(c)
        if c.phase == self.WAIT:
            if c.state == DASH:
                c.set_phase(self.DANCE)
                v.update(dashes=1, length=1, longest=1, idle=0, reached=0)
        elif c.phase == self.DANCE:
            if c.state == DASH:
                if c.state_frames == 1:
                    v["dashes"] += 1
                    v["length"] = 0
                v["length"] += 1
                v["idle"] = 0
                if v["length"] > v["longest"]:
                    v["longest"] = v["length"]
            elif c.state == TURN:
                pass                # the frame between two dashes
            elif c.state == RUN:
                if v["dashes"] < 2:
                    c.set_phase(self.WAIT)  # just running
                else:
                    self.end(c, ran=True)
            elif c.state == WAIT and self._idle(v) <= DD_IDLE:
                pass                # a dash that ran out: allowed for a moment
            elif v["dashes"] >= 2:
                self.end(c, ran=False)
            else:
                c.set_phase(self.WAIT)  # one dash is not a dance

    @staticmethod
    def _idle(v):
        v["idle"] += 1              # ++dd.idle
        return v["idle"]


# ---- universal-jc-grab ------------------------------------------------------

class TechJcGrab(Drill):
    id = "universal-jc-grab"
    name = "Jump-Cancelled Grab"
    goal = "Standing grab out of a run"
    part = "tech"
    cpu = None
    flow = True
    WAIT, MOVING, SQUAT = range(3)
    help = ("JC grab: while running, jump and press Z during",
            "jump squat for a standing grab.",
            "D-Pad up: guide. D-Pad down: reset.")
    # Dash for 14 frames, jump, Z on the next frame.
    reference = [
        Ref(0, 10, 16, 127, 0),
        Ref(0, 24, 1, buttons=X),
        Ref(0, 25, 1, buttons=Z),
    ]

    def guide(self, c):
        me = c.fd
        return ["Grabbing while you run gives the slow dash grab.",
                "Jump first and grab during jump squat: the jump",
                "is cancelled and you get your standing grab.",
                "Standing grab: %d frames. Dash grab: %d."
                % (me.move["grab"].total, me.move["dash_grab"].total),
                "1. Dash or run.   2. Jump (X or Y).",
                "3. Z within %d frames after the jump."
                % (me.jump_squat - 1),
                "Both at once is still the dash grab."]

    def setup(self, c):
        c.place_solo(-30.0)
        self.v = dict(squat_frames=0)

    def think(self, c):
        v = self.v
        if c.phase == self.WAIT:
            if c.state in (DASH, RUN):
                c.set_phase(self.MOVING)
        elif c.phase == self.MOVING:
            if c.state == KNEEBEND:
                c.set_phase(self.SQUAT)
                c.tl_begin()
                v["squat_frames"] = 1
            elif c.state == CATCH_DASH:
                c.tl_begin()
                c.result(False, "Dash grab\njump first, then Z")
            elif c.state not in (DASH, RUN, TURN, CATCH_DASH):
                c.set_phase(self.WAIT)  # did something else
            elif c.state == WAIT:
                c.set_phase(self.WAIT)
        elif c.phase == self.SQUAT:
            if c.state == KNEEBEND:
                v["squat_frames"] += 1
            elif c.state == CATCH:
                # Z came this many frames after the jump
                c.measure(v["squat_frames"], 1)
                c.result(True, "JC grab!\nZ %d after the jump"
                         % v["squat_frames"])
            elif c.state == ATTACK_HI4:
                # "JC grab and up smash should just be JC grab. If I
                # upsmash it says failure" (the owner, 2026-11-13): the up
                # smash has its own drill, next in the course
                c.retry("Up smash: not counted\nthe JC up smash drill "
                        "is next")
            else:
                c.result(False, "Jumped: Z too late\nwithin %d frames"
                         % (c.fd.jump_squat - 1))

    def timeline(self, c):
        js = c.fd.jump_squat
        return ([Row("Jump", buttons=X | Y, perfect=(1,), window=(1, 1)),
                 Row("Grab", buttons=Z, perfect=(2,), window=(2, js))],
                "Jump squat is %d frames: Z on frames 2 to %d. Z with the "
                "jump is the dash grab." % (js, js))


# ---- universal-jc-upsmash ---------------------------------------------------

class TechJcUpsmash(Drill):
    """Up smash out of a run: a run cannot be cancelled into a smash, but
    jump squat can. Jump, then up smash (C-stick up, or A with the stick
    up) during jump squat. Asked for by the owner (2026-11-13) as its own
    drill below the JC grab; native only (no C drill in the overlay)."""
    id = "universal-jc-upsmash"
    name = "Jump-Cancelled Up Smash"
    goal = "Up smash out of a run"
    part = "tech"
    cpu = None
    flow = True
    WAIT, MOVING, SQUAT = range(3)
    help = ("JC up smash: while running, jump and up smash",
            "during jump squat (C-stick up).",
            "D-Pad up: guide. D-Pad down: reset.")
    # Dash for 14 frames, jump, the C-stick up on the next frame.
    reference = [
        Ref(0, 10, 16, 127, 0),
        Ref(0, 24, 1, buttons=X),
        Ref(0, 25, 2, cy=127),
    ]

    def guide(self, c):
        js = c.fd.jump_squat
        return ["A run cannot turn into an up smash; a jump can.",
                "Jump, then up smash before you leave the ground:",
                "the jump is cancelled into the smash.",
                "1. Dash or run.   2. Jump (X or Y).",
                "3. C-stick up (or A with the stick up) within",
                "   %d frames after the jump." % (js - 1),
                "Jump squat is %d frames; later is an up air." % js]

    def setup(self, c):
        c.place_solo(-30.0)
        self.v = dict(squat_frames=0)

    def think(self, c):
        v = self.v
        if c.phase == self.WAIT:
            if c.state in (DASH, RUN):
                c.set_phase(self.MOVING)
        elif c.phase == self.MOVING:
            if c.state == KNEEBEND:
                c.set_phase(self.SQUAT)
                c.tl_begin()
                v["squat_frames"] = 1
            elif c.state == ATTACK_DASH:
                c.tl_begin()
                c.result(False, "Dash attack\njump first, then up smash")
            elif c.state == ATTACK_HI4:
                c.retry("Up smash out of the dash\nnow from a run: jump "
                        "first")
            elif c.state not in (DASH, RUN, TURN):
                c.set_phase(self.WAIT)
        elif c.phase == self.SQUAT:
            if c.state == KNEEBEND:
                v["squat_frames"] += 1
            elif c.state == ATTACK_HI4:
                c.measure(v["squat_frames"], 1)
                c.result(True, "JC up smash!\nsmash %d after the jump"
                         % v["squat_frames"])
            elif c.state in (CATCH,):
                c.retry("A grab: not counted\nthis drill is the up smash")
            elif is_aerial(c.state) or c.state in (JUMP_F, JUMP_B):
                c.result(False, "Jumped: up smash too late\nwithin %d "
                         "frames" % (c.fd.jump_squat - 1))
            else:
                c.set_phase(self.WAIT)

    def timeline(self, c):
        js = c.fd.jump_squat
        return ([Row("Jump", buttons=X | Y, perfect=(1,), window=(1, 1)),
                 Row("Smash", test=smashed_up, perfect=(2,),
                     window=(2, js))],
                "Jump squat is %d frames: up smash on frames 2 to %d."
                % (js, js))


DRILLS = [TechLCancel, TechShffl, TechDashDance, TechJcGrab,
          TechJcUpsmash]
