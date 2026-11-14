"""fox-shine-grab and fox-shffl-nair-shine: Fox's two basic ways through
and onto a shield.

Port of src/tmce/events/course/drills/fox_pressure.inc.h (specs:
data/courses/fox.md, Tech 9, 10).

The CPU (Marth) stands next to the player and holds a shield that does not
shrink (c.cpu_shield()).

Measured with Fox on Marth's shield in the simulator (2026-11-12). Frame 1
is the frame of the down-B:
  - the shine's hit on shield freezes Fox for 3 frames, so the earliest
    jump out of it is frame 7, not 4; a jump on frame 6 is ignored;
  - jump on 7, Z on 8: the standing grab starts on frame 8 and takes Marth
    6 frames later. Marth's shieldstun ends on frame 9.
"""
from melee_course.engine import (
    A, B, X, Z, Drill, Ref, leniency_option, KNEEBEND, LANDING, CATCH,
    CATCH_PULL, CATCH_DASH, CATCH_WAIT, GUARD_SET_OFF, CAPTURE_PULLED_HI,
    ATTACK_AIR_N, ATTACK_AIR_LW, FOX_SHINE_FIRST, FOX_SHINE_LAST)

CAPTURE_FOOT = 232      # the last of the held states (ftCo_MS_CaptureFoot)
LANDING_AIR_N, LANDING_AIR_LW = 70, 74
SHINE_GROUND_START = FOX_SHINE_FIRST      # FST_GROUND_START
AERIALS = ("nair", "fair", "bair", "uair", "dair")

# Distance between the two at the start: the shine reaches the shield and
# the grab still reaches after the shine's pushback.
DISTANCE = 6.7
TIMEOUT = 60
AIR_TIMEOUT = 150             # MV_AIR_TIMEOUT (tech_movement.inc.h)


def is_shine(state):
    return FOX_SHINE_FIRST <= state <= FOX_SHINE_LAST


def is_aerial(state):
    return ATTACK_AIR_N <= state <= ATTACK_AIR_LW


def is_aerial_landing(state):
    return LANDING_AIR_N <= state <= LANDING_AIR_LW


def was_l_cancelled(c, landing_state, frames):
    """The landing of aerial `landing_state` was L-cancelled if it lasted
    `frames` (mv_WasLCancelled)."""
    m = c.fd.move[AERIALS[landing_state - LANDING_AIR_N]]
    return frames * 2 < m.land + m.land_l


def cpu_grabbed(c):
    return CAPTURE_PULLED_HI <= c.cpu_state <= CAPTURE_FOOT


def place(c):
    hmn_x = -c.side * (DISTANCE / 2)
    c.place(hmn_x, hmn_x + c.side * DISTANCE, False, 0.0)


# ---- fox-shine-grab ---------------------------------------------------------

SG_GRAB_FRAME = 8             # the grab's first frame when frame perfect
SG_OPT_LENIENCY = 0
SG_WAIT, SG_SHINE, SG_SQUAT, SG_GRAB = range(4)


class FoxShineGrab(Drill):
    id = "fox-shine-grab"
    name = "Shine-Grab"
    goal = "Shine a shield, jump-cancel, and grab it"
    part = "tech"
    stage = "final-destination"
    cpu = "marth"
    characters = ("fox",)
    options = (leniency_option(),)
    help = ("Shine-grab: shine the shield, jump, and press Z",
            "during jump squat.",
            "D-Pad up: guide. D-Pad down: reset.")
    reference = [
        Ref(0, 20, 1, 0, -127, buttons=B),
        Ref(0, 26, 1, buttons=X),
        Ref(0, 27, 1, buttons=Z),
    ]

    def guide(self, c):
        return ["A shield blocks the shine, but not a grab.",
                "Shine the shield, jump-cancel the shine, and",
                "grab during jump squat (a jump-cancelled grab).",
                "On shield the shine freezes you for 3 frames:",
                "the jump works from frame %d, not 4." % (SG_GRAB_FRAME - 1),
                "Perfect: down+B, jump on %d, Z on %d."
                % (SG_GRAB_FRAME - 1, SG_GRAB_FRAME)]

    def setup(self, c):
        place(c)
        self.v = dict(frame=0, on_shield=False, grab_frame=0)

    def think(self, c):
        v = self.v
        lenient = c.leniency(SG_OPT_LENIENCY)
        c.cpu_shield()
        if c.phase != SG_WAIT:
            v["frame"] += 1
            if c.cpu_state == GUARD_SET_OFF and v["frame"] <= 3:
                v["on_shield"] = True
        if c.phase == SG_WAIT:
            if c.state == SHINE_GROUND_START and c.state_frames == 1:
                c.set_phase(SG_SHINE)
                v["frame"] = 1
                v["on_shield"] = c.cpu_state == GUARD_SET_OFF
            elif c.state in (CATCH, CATCH_DASH):
                c.result(False, "Grab without the shine: shine first")
            return
        if c.phase == SG_SHINE:
            if c.state == KNEEBEND:
                c.set_phase(SG_SQUAT)
            elif not is_shine(c.state) or v["frame"] > TIMEOUT:
                c.result(False, "No jump out of shine")
            return
        if c.phase == SG_SQUAT:
            if c.state == KNEEBEND:
                return
            if c.state != CATCH:
                c.result(False, "Jumped: Z too late: Z right after the jump")
                return
            v["grab_frame"] = v["frame"]
            c.set_phase(SG_GRAB)
            # fall through
        if c.phase == SG_GRAB:
            grab = v["grab_frame"]
            if cpu_grabbed(c) or c.state in (CATCH_PULL, CATCH_WAIT):
                late = grab - SG_GRAB_FRAME
                c.measure(grab, SG_GRAB_FRAME)
                c.report("on_shield", int(v["on_shield"]))
                if not v["on_shield"]:
                    c.result(False, "The shine missed the shield")
                elif late > lenient:
                    c.result(False, "Slow: grab on frame %d, want frame %d"
                             % (grab, SG_GRAB_FRAME))
                elif late <= 0:
                    c.result(True, "Perfect shine-grab: grab on frame %d"
                             % grab)
                else:
                    c.result(True, "Shine-grab, %d late: grab on frame %d"
                             % (late, grab))
            elif c.state != CATCH:
                c.measure(grab, SG_GRAB_FRAME)
                c.result(False, "The grab missed")


# ---- fox-shffl-nair-shine ---------------------------------------------------

NS_MARK_LAND = 1
NS_OPT_LENIENCY = 0
NS_WAIT, NS_AIR, NS_LAND, NS_AFTER = range(4)


def _ns_state():
    return dict(frame=0, on_shield=False, land_frame=0, land_state=0, lag=0,
                wait=0, stun_end=0)


class FoxNairShine(Drill):
    id = "fox-shffl-nair-shine"
    name = "Aerial into Shine"
    goal = "SHFFL neutral air on shield, shine as you land"
    part = "tech"
    stage = "final-destination"
    cpu = "marth"
    characters = ("fox",)
    flow = True
    options = (leniency_option(),)
    help = ("Aerial into shine: short hop neutral air on the",
            "shield, L-cancel, shine as you land.",
            "D-Pad up: guide. D-Pad down: reset.")
    # Short hop, neutral air at once, fast fall; trigger and shine against
    # the landing the observing pass saw.
    reference = [
        Ref(0, 20, 1, buttons=X),
        Ref(0, 23, 1, buttons=A),
        Ref(NS_MARK_LAND, -4, 1, buttons=Z),
        Ref(NS_MARK_LAND, 6, 1, 0, -127, buttons=B),
    ]

    def guide(self, c):
        m = c.fd.move["nair"]
        return ["The start of Fox's shield pressure: an aerial",
                "on the shield, then shine the moment you can.",
                "1. Short hop neutral air onto the shield.",
                "2. L-cancel: %d frames of landing, not %d."
                % (m.land_l, m.land),
                "3. Down+B on the first frame after them.",
                "The verdict shows how many frames the opponent",
                "had between shieldstun and your shine. Attack",
                "later in the hop to make that smaller."]

    def setup(self, c):
        place(c)
        self.v = _ns_state()

    def no_l_cancel(self, c):
        c.result(False, "No L-cancel: %d frames lag: L, R or Z as you land"
                 % self.v["lag"])

    def think(self, c):
        v = self.v
        lenient = c.leniency(NS_OPT_LENIENCY)
        c.cpu_shield()
        if c.phase != NS_WAIT:
            v["frame"] += 1
            if c.state == SHINE_GROUND_START:
                pass    # the shine's own hit on the shield is not the aerial's
            elif c.cpu_state == GUARD_SET_OFF:
                v["on_shield"] = True
                v["stun_end"] = 0
            elif v["on_shield"] and v["stun_end"] == 0:
                v["stun_end"] = v["frame"]
        if c.phase == NS_WAIT:
            if is_aerial(c.state):
                c.set_phase(NS_AIR)
                self.v = v = _ns_state()
                v["frame"] = 1
            elif c.state == LANDING:
                c.mark(NS_MARK_LAND)
            elif c.state == SHINE_GROUND_START and c.state_frames == 1 and \
                    c.prev_state != v["land_state"]:
                # once per shine: without a reset this is seen every frame
                c.result(False, "Shine without the aerial: jump in first")
            return
        if c.phase == NS_AIR:
            if is_aerial_landing(c.state):
                c.mark(NS_MARK_LAND)
                c.set_phase(NS_LAND)
                v["land_frame"] = v["frame"]
                v["land_state"] = c.state
                v["lag"] = 1
            elif not is_aerial(c.state):
                c.result(False, "Landed after the attack: attack later")
            elif v["frame"] > AIR_TIMEOUT:
                c.result(False, "Did not land")
            return
        if c.phase == NS_LAND:
            if c.state == v["land_state"]:
                v["lag"] += 1
                return
            c.set_phase(NS_AFTER)
            v["wait"] = 0
            # fall through
        if c.phase == NS_AFTER:
            if c.state == SHINE_GROUND_START:
                # frames the CPU was out of shieldstun before the shine;
                # 0 or less: none
                opened = v["frame"] - v["stun_end"] if v["stun_end"] > 0 \
                    else 0
                lcancel = was_l_cancelled(c, v["land_state"], v["lag"])
                c.measure(v["wait"], 0)
                c.report("on_shield", int(v["on_shield"]))
                c.report("l_cancel", int(lcancel))
                c.report("lag", v["lag"])
                c.report("open", opened)
                if not v["on_shield"]:
                    c.result(False, "The aerial missed the shield")
                elif not lcancel:
                    self.no_l_cancel(c)
                elif v["wait"] > lenient:
                    c.result(False, "Shine %d frames late: opponent had %d "
                                    "frames" % (v["wait"], opened))
                elif v["wait"] == 0:
                    c.result(True, "Perfect: shine at once: opponent had %d "
                                   "frames" % opened)
                else:
                    c.result(True, "Shine %d late: opponent had %d frames"
                             % (v["wait"], opened))
            else:
                v["wait"] += 1
                if v["wait"] > 20:
                    if not was_l_cancelled(c, v["land_state"], v["lag"]):
                        self.no_l_cancel(c)
                    else:
                        c.result(False, "No shine after landing")


DRILLS = [FoxShineGrab, FoxNairShine]
