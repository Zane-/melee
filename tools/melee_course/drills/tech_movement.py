"""universal-l-cancel, universal-shffl, universal-dash-dance,
universal-jc-grab.

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
    L, R, Z, A, X, Drill, Option, Ref, WAIT, TURN, DASH, RUN, KNEEBEND,
    LANDING, ATTACK_AIR_N, ATTACK_AIR_LW, LANDING_AIR_N, LANDING_AIR_LW,
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
        if not fast and v < 0 and is_tap(cross):
            v = -ff
            fast = True
        y = _f32(y + v)
        if y < 0:
            break
        v = _f32(v - gravity)
        if v < -terminal and not fast:
            v = -terminal
        cross += 1
    aerial = cross - (m.hit + REF_PAST_HIT)
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


# ---- universal-dash-dance ---------------------------------------------------

DD_COUNTS = (4, 6, 10, 20)


class TechDashDance(Drill):
    id = "universal-dash-dance"
    name = "Dash Dance"
    goal = "Dash back and forth without ever running"
    part = "tech"
    cpu = None
    flow = True
    OPT_COUNT = 0
    WAIT, DANCE = range(2)
    options = (Option("Dashes", ["4", "6", "10", "20"], 1,
                      "How many dashes in a row count as a success."),)
    help = ("Dash dance: dash left and right, turning before",
            "the dash becomes a run.",
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
                "The verdict shows your longest dash in frames."]

    def setup(self, c):
        c.place_solo(0.0)
        self.v = dict(dashes=0, length=0, longest=0, idle=0)

    def fail(self, c, fmt):
        want = DD_COUNTS[c.opt(self.OPT_COUNT)]
        c.measure(self.v["dashes"], want)
        c.report("dashes", self.v["dashes"])
        c.result(False, fmt % (self.v["dashes"], want))

    def think(self, c):
        v = self.v
        want = DD_COUNTS[c.opt(self.OPT_COUNT)]
        if c.phase == self.WAIT:
            if c.state == DASH:
                c.set_phase(self.DANCE)
                v.update(dashes=1, length=1, longest=1, idle=0)
        elif c.phase == self.DANCE:
            if c.state == DASH:
                if c.state_frames == 1:
                    v["dashes"] += 1
                    v["length"] = 0
                    if v["dashes"] >= want:
                        c.measure(v["dashes"], want)
                        c.report("dashes", v["dashes"])
                        c.report("longest", v["longest"])
                        c.result(True, "%d dashes\nlongest %d frames"
                                 % (v["dashes"], v["longest"]))
                        return
                v["length"] += 1
                v["idle"] = 0
                if v["length"] > v["longest"]:
                    v["longest"] = v["length"]
            elif c.state == TURN:
                pass                # the frame between two dashes
            elif c.state == RUN and v["dashes"] < 2:
                c.set_phase(self.WAIT)  # just running
            elif c.state == RUN:
                self.fail(c, "Ran after %d of %d dashes\nturn sooner")
            elif c.state == WAIT and self._idle(v) <= 2:
                pass                # a dash that ran out: allowed for a moment
            elif v["dashes"] >= 2:
                self.fail(c, "Stopped after %d of %d dashes")
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
                v["squat_frames"] = 1
            elif c.state == CATCH_DASH:
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
            else:
                c.result(False, "Jumped: Z too late\nwithin %d frames"
                         % (c.fd.jump_squat - 1))


DRILLS = [TechLCancel, TechShffl, TechDashDance, TechJcGrab]
