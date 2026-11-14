"""universal-short-hop: leave the ground with a short hop.

Port of src/tmce/events/course/drills/tech_short_hop.inc.h (spec:
data/courses/universal.md).

A jump is a short hop when the jump button is no longer held on the last
frame of jump squat. The drill counts the frames the button was held and
reads the result off the first airborne frame's upward speed (short hop
and full hop speeds from the character's frame data).
"""
from melee_course.engine import (
    X, Y, Drill, Ref, Row, KNEEBEND, JUMP_F, JUMP_B)

WAIT, SQUAT = range(2)


class TechShortHop(Drill):
    id = "universal-short-hop"
    name = "Short Hop"
    goal = "Leave the ground with a short hop every time"
    part = "tech"
    cpu = None
    flow = True
    help = ("Short hop: tap X or Y and let go before you leave",
            "the ground. D-Pad up: guide. D-Pad down: reset.")
    # Jump at frame 10, held for 2 frames: short for every character (the
    # shortest jump squat is 3).
    reference = [Ref(0, 10, 2, buttons=X)]

    def guide(self, c):
        js = c.fd.jump_squat
        return ["A short hop is a jump whose button you let go",
                "before your character leaves the ground.",
                "Your jump squat is %d frames: release X or Y" % js,
                "within %d frames of pressing it." % (js - 1),
                "Tap the button. Do not hold it down."]

    def setup(self, c):
        c.place_solo(0.0)
        self.v = dict(held=0)

    def think(self, c):
        v = self.v
        if c.phase == WAIT:
            if c.state != KNEEBEND:
                return
            c.set_phase(SQUAT)
            c.tl_begin()
            v["held"] = 0
            # fall through: count this frame too
        if c.state == KNEEBEND:
            if c.held & (X | Y):
                v["held"] += 1
        elif c.state in (JUMP_F, JUMP_B):
            limit = c.fd.jump_squat - 1
            c.measure(v["held"], limit)
            c.report("held", v["held"])
            if c.me.vel[1] < (c.fd.hop_v + c.fd.jump_v) / 2:
                c.result(True, "Short hop! held %d frames" % v["held"])
            else:
                c.result(False, "Full hop: held %d, release by %d"
                         % (v["held"], limit))
        else:
            # left jump squat some other way (hit, special...)
            c.set_phase(WAIT)

    def timeline(self, c):
        js = c.fd.jump_squat
        return ([Row("Held", buttons=X | Y, held=True, perfect=(1,),
                     window=(1, js - 1)),
                 Row("Air", state=lambda st: st in (JUMP_F, JUMP_B),
                     perfect=(js + 1,))],
                "Jump squat is %d frames: let go by frame %d." % (js, js - 1))


DRILLS = [TechShortHop]
