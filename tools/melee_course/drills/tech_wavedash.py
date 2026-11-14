"""universal-wavedash: air dodge into the ground out of a jump.

Port of src/tmce/events/course/drills/tech_wavedash.inc.h (spec:
data/courses/universal.md).

Perfect is an air dodge on the first airborne frame: the fighter never
shows a jump state and goes from jump squat straight to the special
landing (10 frames). Measured in the simulator with Fox (2026-11-12):
dodge one frame late = 1 frame of jump, then the air dodge, then the
landing; a dodge during jump squat does nothing and the jump comes out.
"""
from melee_course.engine import (
    R, X, Drill, Ref, leniency_option, KNEEBEND, JUMP_F, JUMP_B, ESCAPE_AIR,
    LANDING_FALL_SPECIAL)

# Special landing after an air dodge: the wavedash's lag.
LANDING_FRAMES = 10
# Frames of jump without an air dodge before "no air dodge".
JUMP_TIMEOUT = 12
# Frames in the air dodge without landing before "too high".
DODGE_TIMEOUT = 8
# Ground covered below which it was a dodge straight down, not a dash.
MIN_SLIDE = 4.0

OPT_LENIENCY = 0
WAIT, SQUAT, JUMP, DODGE, LAND = range(5)


class TechWavedash(Drill):
    id = "universal-wavedash"
    name = "Wavedash"
    goal = "Air dodge into the ground on your first airborne frame"
    part = "tech"
    cpu = None
    flow = True
    options = (leniency_option(),)
    help = ("Wavedash: jump, then air dodge diagonally into the",
            "ground as you leave it.",
            "D-Pad up: guide. D-Pad down: reset.")
    # Jump, then R with the stick down and forward on the first airborne
    # frame: one jump squat later.
    reference = [
        Ref(0, 10, 1, buttons=X),
        Ref(0, 10, 2, 90, -90, buttons=R, trigger=140, js=1),
    ]

    def guide(self, c):
        return ["Jump, then air dodge diagonally into the ground",
                "the moment you leave it. You slide, and can act",
                "after %d frames of landing." % LANDING_FRAMES,
                "1. Press X or Y.",
                "2. %d frames later: R (or L) with the stick"
                % c.fd.jump_squat,
                "   down and to the side.",
                "Too early and you only jump. Too late and you",
                "dodge in the air."]

    def setup(self, c):
        c.place_solo(0.0)
        self.v = dict(jump_frames=0, start_x=0.0)

    def think(self, c):
        v = self.v
        lenient = c.leniency(OPT_LENIENCY)

        if c.phase == WAIT:
            if c.state == KNEEBEND:
                c.set_phase(SQUAT)
                v["jump_frames"] = 0
                v["start_x"] = c.me.pos[0]
            return

        if c.phase == SQUAT:
            if c.state == KNEEBEND:
                return
            c.set_phase(JUMP)
            # fall through: classify the state that followed jump squat

        if c.phase == JUMP:
            if c.state == LANDING_FALL_SPECIAL:
                c.set_phase(LAND)
            elif c.state == ESCAPE_AIR:
                c.set_phase(DODGE)
            elif c.state in (JUMP_F, JUMP_B):
                v["jump_frames"] += 1
                if v["jump_frames"] > JUMP_TIMEOUT:
                    c.set_phase(WAIT)       # a plain jump: not an attempt
            else:
                c.set_phase(WAIT)   # an aerial, a special...: ignore
            return

        if c.phase == DODGE:
            if c.state == LANDING_FALL_SPECIAL:
                c.set_phase(LAND)
            elif c.state != ESCAPE_AIR or c.timer > DODGE_TIMEOUT:
                c.measure(v["jump_frames"] + 1, 1)
                c.result(False, "Air dodged too high\n%d frames late"
                         % v["jump_frames"])
            return

        if c.phase == LAND:
            if c.state == LANDING_FALL_SPECIAL:
                return
            # The air dodge came on airborne frame jump_frames + 1.
            frame = v["jump_frames"] + 1
            slide = abs(c.me.pos[0] - v["start_x"])
            c.measure(frame, 1)
            c.report("slide", round(slide, 1))
            if slide < MIN_SLIDE:
                c.result(False, "No slide\nangle the stick sideways")
            elif frame - 1 > lenient:
                c.result(False, "Late: airborne frame %d\nwant frame 1"
                         % frame)
            elif frame == 1:
                c.result(True, "Perfect wavedash\nslid %d units"
                         % int(slide))
            else:
                c.result(True, "Wavedash, %d late\nslid %d units"
                         % (frame - 1, int(slide)))


DRILLS = [TechWavedash]
