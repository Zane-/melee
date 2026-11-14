"""Fox's shine technique drills: fox-jc-shine, fox-waveshine, fox-multishine.

Port of src/tmce/events/course/drills/fox_shine_tech.inc.h (specs:
data/courses/fox.md, Tech).

Frame facts, measured with Fox in the simulator (2026-11-12) and agreeing
with SSBWiki's Reflector page (data/characters/fox.md, "Multishine").
Frame 1 is the frame down-B is pressed and the shine comes out:
  - the earliest jump out of shine is on frame 4; a jump on frame 3 is
    ignored;
  - jump on 4, air dodge on 7 (first airborne frame after Fox's 3-frame
    jump squat): special landing from frame 7, actionable on frame 17;
  - jump on 4, shine again on 7: that shine is airborne at ground level,
    Fox is grounded again on frame 11 and can jump on 12 (a jump on 10
    or 11 is the double jump), third shine on 15: one shine per 8 frames
    after the first gap of 6.
These are Fox's numbers: Falco's jump squat is 5 and his shine differs, so
the drills are offered to Fox only until Falco's are measured.
"""
from melee_course.engine import (
    B, L, R, X, Y, Drill, Option, Ref, Row, leniency_option, KNEEBEND,
    JUMP_F, JUMP_B, JUMP_AERIAL_F, JUMP_AERIAL_B, LANDING_FALL_SPECIAL)
from melee_course.drills.tech_wavedash import (
    JUMP_TIMEOUT as WD_JUMP_TIMEOUT, DODGE_TIMEOUT as WD_DODGE_TIMEOUT,
    MIN_SLIDE as WD_MIN_SLIDE)

# Fox's shine states (ftFox/forward.h, ftFx_MS_SpecialLwStart = 0x168):
# ground start, loop, hit, end, turn; then the same five in the air.
GROUND_START = 0x168
GROUND_LAST = 0x16C
AIR_START = 0x16D
AIR_LAST = 0x171

JC_FRAME = 4             # earliest jump out of shine
WAVESHINE_LAND = 7       # special landing begins, perfect waveshine
WAVESHINE_FREE = 17      # actionable again, perfect waveshine
GAP_FIRST = 6            # shine 1 -> shine 2
GAP_NEXT = 8             # every later shine
TIMEOUT = 40             # frames after the shine before giving up


def is_shine(state):
    return GROUND_START <= state <= AIR_LAST


def is_jump(state):
    return state in (JUMP_F, JUMP_B)


def is_double_jump(state):
    return state in (JUMP_AERIAL_F, JUMP_AERIAL_B)


# ---- fox-jc-shine -----------------------------------------------------------

class FoxJcShine(Drill):
    id = "fox-jc-shine"
    name = "Frame-Perfect JC Shine"
    goal = "Jump out of shine on the first possible frame"
    part = "tech"
    cpu = None
    characters = ("fox",)
    flow = True
    OPT_LENIENCY = 0
    WAIT, SHINE = range(2)
    options = (leniency_option(),)
    help = ("Shine (down+B), then jump on the first frame the",
            "shine allows it: 3 frames later.",
            "D-Pad up: guide. D-Pad down: reset.")
    reference = [
        Ref(0, 10, 1, 0, -127, buttons=B),
        Ref(0, 13, 1, buttons=X),
    ]

    def guide(self, c):
        return ["Shine (down+B) can be cancelled by a jump, and",
                "everything Fox does out of shine starts there.",
                "The shine comes out on frame 1. The first frame",
                "a jump works is frame %d: %d frames after down+B."
                % (JC_FRAME, JC_FRAME - 1),
                "A jump pressed earlier is ignored, so pressing",
                "both at once does nothing."]

    def setup(self, c):
        c.place_solo(0.0)
        self.v = dict(frame=0, first_press=0)

    def think(self, c):
        v = self.v
        lenient = c.leniency(self.OPT_LENIENCY)

        if c.phase == self.WAIT:
            if c.state == GROUND_START and c.state_frames == 1:
                c.set_phase(self.SHINE)
                c.tl_begin()
                v["frame"] = 1
                v["first_press"] = 0
        elif c.phase == self.SHINE:
            v["frame"] += 1
            if v["first_press"] == 0 and c.down & (X | Y):
                v["first_press"] = v["frame"]
            if c.state == KNEEBEND:
                jumped = v["frame"]
                c.measure(jumped, JC_FRAME)
                if jumped - JC_FRAME > lenient:
                    c.result(False, "Late: jumped on frame %d\nwant frame %d"
                             % (jumped, JC_FRAME))
                elif jumped == JC_FRAME:
                    c.result(True, "Frame perfect\njump on frame %d"
                             % jumped)
                else:
                    c.result(True, "Jump on frame %d\n%d late"
                             % (jumped, jumped - JC_FRAME))
            elif not is_shine(c.state) or v["frame"] > TIMEOUT:
                if 0 < v["first_press"] < JC_FRAME:
                    c.measure(v["first_press"], JC_FRAME)
                    c.result(False, "Too early: frame %d\nwant frame %d"
                             % (v["first_press"], JC_FRAME))
                else:
                    c.set_phase(self.WAIT)  # a shine alone: ignore

    def timeline(self, c):
        lenient = c.leniency(self.OPT_LENIENCY)
        return ([Row("Shine", buttons=B, perfect=(1,), window=(1, 1)),
                 Row("Jump", buttons=X | Y, perfect=(JC_FRAME,),
                     window=(JC_FRAME, JC_FRAME + lenient)),
                 Row("Jumped", state=lambda st: st == KNEEBEND)],
                "The shine is frame 1; a jump before frame %d is ignored."
                % JC_FRAME)


# ---- fox-waveshine ----------------------------------------------------------

class FoxWaveshine(Drill):
    id = "fox-waveshine"
    name = "Waveshine"
    goal = "Shine, jump, wavedash with no wasted frames"
    part = "tech"
    cpu = None
    characters = ("fox",)
    flow = True
    OPT_LENIENCY = 0
    WAIT, SHINE, SQUAT, AIR, LAND = range(5)
    # "Waveshine training needs more tolerance for slowness. Let's do up
    # to 5 frames late!" (the owner, 2026-11-13): frames late, 0 to 5.
    options = (Option("Leniency", ["Frame Perfect", "1 Frame", "2 Frames",
                                   "3 Frames", "4 Frames", "5 Frames"], 5,
                      "How many frames late the landing still counts."),)
    help = ("Waveshine: down+B, jump 3 frames later, air dodge",
            "into the ground 3 frames after that.",
            "D-Pad up: guide. D-Pad down: reset.")
    reference = [
        Ref(0, 10, 1, 0, -127, buttons=B),
        Ref(0, 13, 1, buttons=X),
        Ref(0, 16, 2, 90, -90, buttons=R, trigger=140),
    ]

    def guide(self, c):
        return ["Shine, jump out of it, wavedash: Fox slides",
                "after the opponent the shine pushed away.",
                "1. Down+B                      (frame 1)",
                "2. Jump                        (frame %d)" % JC_FRAME,
                "3. R + stick down and sideways (frame %d)"
                % WAVESHINE_LAND,
                "Perfect: you can act again on frame %d."
                % WAVESHINE_FREE]

    def setup(self, c):
        c.place_solo(0.0)
        self.v = dict(frame=0, land_frame=0, start_x=0.0)

    def lenient(self, c):
        return c.opt(self.OPT_LENIENCY)       # the value is the frames

    def timeline(self, c):
        late = self.lenient(c)
        return ([Row("Shine", buttons=B, perfect=(1,), window=(1, 1)),
                 Row("Jump", buttons=X | Y, perfect=(JC_FRAME,),
                     window=(JC_FRAME, JC_FRAME + late)),
                 Row("Dodge", buttons=L | R, trigger=True,
                     perfect=(WAVESHINE_LAND,),
                     window=(WAVESHINE_LAND, WAVESHINE_LAND + late)),
                 Row("Slide", state=lambda st: st == LANDING_FALL_SPECIAL,
                     perfect=(WAVESHINE_LAND,))],
                "Slide: the landing; frame-perfect is free on frame %d."
                % WAVESHINE_FREE)

    def think(self, c):
        v = self.v
        lenient = self.lenient(c)

        if c.phase != self.WAIT:
            v["frame"] += 1

        if c.phase == self.WAIT:
            if c.state == GROUND_START and c.state_frames == 1:
                c.set_phase(self.SHINE)
                c.tl_begin()
                v["frame"] = 1
                v["start_x"] = c.me.pos[0]
            return

        if c.phase == self.SHINE:
            if c.state == KNEEBEND:
                c.set_phase(self.SQUAT)
            elif not is_shine(c.state) or v["frame"] > TIMEOUT:
                c.result(False, "No jump out of shine")
            return

        if c.phase == self.SQUAT:
            if c.state == KNEEBEND:
                return
            c.set_phase(self.AIR)
            # fall through

        if c.phase == self.AIR:
            if c.state == LANDING_FALL_SPECIAL:
                v["land_frame"] = v["frame"]
                c.set_phase(self.LAND)
            elif is_shine(c.state):
                c.result(False, "Shined again\nair dodge, do not shine")
            elif c.timer > WD_JUMP_TIMEOUT + WD_DODGE_TIMEOUT:
                c.result(False, "No wavedash\nair dodge leaving the ground")
            return

        if c.phase == self.LAND:
            if c.state == LANDING_FALL_SPECIAL:
                return
            slide = abs(c.me.pos[0] - v["start_x"])
            late = v["land_frame"] - WAVESHINE_LAND
            c.measure(v["land_frame"], WAVESHINE_LAND)
            c.report("free", v["frame"])
            c.report("slide", round(slide, 1))
            if slide < WD_MIN_SLIDE:
                c.result(False, "No slide\nangle the stick sideways")
            elif late > lenient:
                c.result(False, "Slow: landed %d late\non frame %d, up "
                         "to %d late counts" % (late, v["land_frame"],
                                                lenient))
            elif late == 0:
                c.result(True, "Perfect waveshine\nfree on frame %d"
                         % v["frame"])
            else:
                c.result(True, "Waveshine, %d late\nfree on frame %d"
                         % (late, v["frame"]))


# ---- fox-multishine ---------------------------------------------------------

COUNTS = (2, 3, 5, 8)


class FoxMultishine(Drill):
    id = "fox-multishine"
    name = "Multishine"
    goal = "Consecutive shines without leaving the ground"
    part = "tech"
    cpu = None
    characters = ("fox",)
    flow = True
    OPT_LENIENCY, OPT_COUNT = range(2)
    WAIT, CHAIN = range(2)
    options = (
        leniency_option(),
        Option("Shines", ["2", "3", "5", "8"], 1,
               "How many shines in a row count as a success."),
    )
    help = ("Multishine: shine, jump, shine as you leave the",
            "ground, wait to land, jump, shine...",
            "D-Pad up: guide. D-Pad down: reset.")
    # Eight shines: after the first, jump 5 frames after each shine (once
    # Fox is grounded again) and shine 3 frames after each jump.
    reference = [
        Ref(0, 10, 1, 0, -127, buttons=B), Ref(0, 13, 1, buttons=X),
        Ref(0, 16, 1, 0, -127, buttons=B), Ref(0, 21, 1, buttons=X),
        Ref(0, 24, 1, 0, -127, buttons=B), Ref(0, 29, 1, buttons=X),
        Ref(0, 32, 1, 0, -127, buttons=B), Ref(0, 37, 1, buttons=X),
        Ref(0, 40, 1, 0, -127, buttons=B), Ref(0, 45, 1, buttons=X),
        Ref(0, 48, 1, 0, -127, buttons=B), Ref(0, 53, 1, buttons=X),
        Ref(0, 56, 1, 0, -127, buttons=B), Ref(0, 61, 1, buttons=X),
        Ref(0, 64, 1, 0, -127, buttons=B),
    ]

    def guide(self, c):
        return ["Shine, jump, and shine again before Fox leaves",
                "the ground: he lands at once and can repeat.",
                "Shine 1: frame 1.   Jump: frame %d." % JC_FRAME,
                "Shine 2: frame %d (first airborne frame)."
                % (1 + GAP_FIRST),
                "Then wait for the landing: jump %d frames after" % 5,
                "each shine, shine 3 frames after each jump.",
                "A jump too soon is the double jump: Fox rises.",
                "Perfect: a shine every %d frames." % GAP_NEXT]

    def setup(self, c):
        c.place_solo(0.0)
        self.v = dict(shines=0, since=0, worst=0, air_time=0)

    def want(self, c):
        return COUNTS[c.opt(self.OPT_COUNT)]

    def end(self, c, fmt):
        v = self.v
        want = self.want(c)
        c.measure(v["shines"], want)
        c.report("shines", v["shines"])
        c.report("worst_late", v["worst"])
        c.result(False, fmt % (v["shines"], want))

    def think(self, c):
        v = self.v
        lenient = c.leniency(self.OPT_LENIENCY)
        want = self.want(c)
        new_shine = c.state in (GROUND_START, AIR_START) and \
            c.state_frames == 1

        if c.phase == self.WAIT:
            if c.state == GROUND_START and c.state_frames == 1:
                c.set_phase(self.CHAIN)
                c.tl_begin()
                v.update(shines=1, since=1, worst=0, air_time=0)
        elif c.phase == self.CHAIN:
            v["since"] += 1
            if new_shine:
                # `since` counted the frames from the last shine to this one
                gap = v["since"] - 1
                late = gap - (GAP_FIRST if v["shines"] == 1 else GAP_NEXT)
                if late > v["worst"]:
                    v["worst"] = late
                v["shines"] += 1
                v["since"] = 1
                v["air_time"] = 0
                if late > lenient:
                    self.end(c, "Shine %d of %d was slow")
                    return
                if v["shines"] >= want:
                    c.measure(v["shines"], want)
                    c.report("shines", v["shines"])
                    c.report("worst_late", v["worst"])
                    if v["worst"] <= 0:
                        c.result(True, "%d shines\nframe perfect"
                                 % v["shines"])
                    else:
                        c.result(True, "%d shines\nworst %d late"
                                 % (v["shines"], v["worst"]))
            elif is_double_jump(c.state):
                self.end(c, "Double jump at %d of %d\njump after landing")
            elif is_jump(c.state):
                # Each frame of jump is a frame the shine is late.
                v["air_time"] += 1
                if v["air_time"] > lenient:
                    self.end(c, "Left the ground at %d of %d\nshine sooner")
            elif c.state == KNEEBEND or is_shine(c.state):
                if v["since"] > TIMEOUT:
                    self.end(c, "Stopped at %d of %d")
            else:
                self.end(c, "Chain ended at %d of %d")

    def timeline(self, c):
        # the perfect chain: shines on 1, 7, 15, 23...; the first jump 3
        # after the first shine, the others 5 after a shine (once Fox has
        # landed), 3 before the next; as far as this chain got
        n = min(self.want(c), self.v.get("shines", 1) + 1)
        shines = [1] + [1 + GAP_FIRST + GAP_NEXT * k for k in range(n - 1)]
        jumps = [JC_FRAME] + [f + 5 for f in shines[1:n - 1]]
        return ([Row("Shine", state=lambda st: st in (GROUND_START,
                                                      AIR_START),
                     perfect=shines),
                 Row("Jump", buttons=X | Y, perfect=jumps)],
                "A shine every %d frames after the first gap of %d."
                % (GAP_NEXT, GAP_FIRST))


DRILLS = [FoxJcShine, FoxWaveshine, FoxMultishine]
