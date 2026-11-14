"""fox-shdl (short hop double laser) and fox-illusion-shorten.

Port of src/tmce/events/course/drills/fox_specials.inc.h (specs:
data/courses/fox.md, Tech).

Measured with Fox in the simulator (2026-11-12). Frame 1 is the frame of
the input.
  - Laser in the air: 4 frames of start, then a 10-frame loop per shot;
    B pressed during a loop queues the next one. A short hop leaves the
    ground for 19 frames.
  - Illusion on the ground: 19 frames of start, then up to 4 frames of
    dash covering 18.7 units each after a first 23. B pressed 19 to 22
    frames after the side-B ends the dash early: 23, 23, 42 or 61 units
    instead of 79. A press 18 frames after or earlier does nothing.
"""
from melee_course.engine import (
    B, X, Y, Drill, Option, Ref, Row, WAIT, KNEEBEND, JUMP_F, JUMP_B, FALL,
    LANDING, FOX_BLASTER_FIRST, FOX_BLASTER_LAST)
from melee_course.drills.tech_movement import AIR_TIMEOUT as MV_AIR_TIMEOUT

# Fox's blaster and Illusion states (ftFox/forward.h): three ground laser
# states from 0x155, three in the air, then Illusion start, dash, end.
LASER_AIR_START = 0x158
LASER_AIR_END = 0x15A
ILLUSION_START = 0x15B
ILLUSION_DASH = 0x15C
ILLUSION_END = 0x15D
ILLUSION_AIR_FIRST = 0x15E
ILLUSION_AIR_LAST = 0x160


FOX_LASER, FALCO_LASER = 54, 55     # It_Kind_Fox_Laser, It_Kind_Falco_Laser


def own_items(c):
    """The player's lasers in play (the C's fsp_OwnLasers). Only the shots:
    the blaster is an item too (kind 74), and counting it made one shot
    after the first airborne frame look like two (fixed in the C as well).
    The native build's item list does not say whose an item is; these
    drills have no opponent and the match no items, so every laser is the
    player's."""
    return sum(1 for i in c.n.state().get("items") or ()
               if i["kind"] in (FOX_LASER, FALCO_LASER))


# ---- fox-shdl ---------------------------------------------------------------

class FoxShdl(Drill):
    id = "fox-shdl"
    name = "Short Hop Double Laser"
    goal = "Two lasers out of every short hop"
    part = "tech"
    cpu = None
    characters = ("fox",)
    flow = True
    WAIT, SQUAT, AIR = range(3)
    help = ("Short hop double laser: short hop, B as you leave",
            "the ground, B again.",
            "D-Pad up: guide. D-Pad down: reset.")
    # Jump, B as Fox leaves the ground, B again during the first shot.
    reference = [
        Ref(0, 10, 1, buttons=X),
        Ref(0, 13, 1, buttons=B),
        Ref(0, 20, 1, buttons=B),
    ]

    def guide(self, c):
        js = c.fd.jump_squat
        return ["Two lasers from one short hop: Fox's way to",
                "make an opponent come to him.",
                "1. Short hop: release jump within %d frames." % (js - 1),
                "2. B as you leave the ground (%d frames later)." % js,
                "3. B again while the first laser is out.",
                "Keep the stick still: a direction with B is",
                "a different move."]

    @staticmethod
    def _clear():
        return dict(short_hop=0, frame=0, first_laser=0, lasers=0, items=0,
                    shots=[])

    def setup(self, c):
        c.place_solo(0.0)
        self.v = self._clear()

    def think(self, c):
        me = c.fd
        items = own_items(c)

        if c.phase == self.WAIT:
            if c.state == KNEEBEND:
                c.set_phase(self.SQUAT)
                c.tl_begin()
                self.v["shots"] = []
        elif c.phase == self.SQUAT:
            if c.state != KNEEBEND:
                self.v = self._clear()
                self.v["short_hop"] = int(
                    c.me.vel[1] < (me.hop_v + me.jump_v) / 2)
                self.v["items"] = items
                c.set_phase(self.AIR)
                self._air(c, items)          # fall through
        elif c.phase == self.AIR:
            self._air(c, items)
        self.v["items"] = items

    def _air(self, c, items):
        v, me = self.v, c.fd
        v["frame"] += 1
        if items > v["items"]:
            v["lasers"] += items - v["items"]
            v["shots"].append(c.tl_frame())
        if v["first_laser"] == 0 and \
                LASER_AIR_START <= c.state <= LASER_AIR_END:
            v["first_laser"] = v["frame"]
        # "It also counts stuff off the ledge too! (i.e. jump from ledge
        # single laser)" (the owner, 2026-11-13): an attempt is one short
        # hop. Anything but its rise, fall and lasers (the ledge, a double
        # jump, an aerial) is not one; the C kept counting until a landing,
        # so a laser from a ledge jump made a pair with the first.
        if not (c.state in (JUMP_F, JUMP_B, FALL, LANDING, WAIT) or
                FOX_BLASTER_FIRST <= c.state <= FOX_BLASTER_LAST):
            c.set_phase(self.WAIT)
            return
        if c.state in (LANDING, WAIT) or v["frame"] > MV_AIR_TIMEOUT:
            c.measure(v["lasers"], 2)
            c.report("lasers", v["lasers"])
            c.report("first", v["first_laser"])
            c.report("short_hop", v["short_hop"])
            if not v["short_hop"]:
                c.result(False, "Full hop\nrelease jump within %d frames"
                         % (me.jump_squat - 1))
            elif v["lasers"] >= 2:
                c.result(True, "Double laser!\n"
                         "first on airborne frame %d" % v["first_laser"])
            elif v["lasers"] == 1:
                c.result(False, "One laser: first B on\n"
                         "airborne frame %d, B again" % v["first_laser"])
            else:
                c.set_phase(self.WAIT)       # a plain jump: ignore

    def timeline(self, c):
        js = c.fd.jump_squat
        return ([Row("Jump", buttons=X | Y, held=True, perfect=(1,),
                     window=(1, js - 1)),
                 Row("B", buttons=B, perfect=(js + 1,)),
                 Row("Laser", frames=self.v.get("shots", ()))],
                "First B on frame %d, the first in the air; B again while "
                "the first laser is out." % (js + 1))


# ---- fox-illusion-shorten ---------------------------------------------------

ILL_DASH_FULL = 4       # dash frames of an Illusion not shortened
ILL_PRESS_FIRST = 19    # frames after side-B the press works from
ILL_PRESS_LAST = 22
ILL_TIMEOUT = 120
# "For shortened illusion we should do 1, 2, 3, 4, 1 is shortest, 2 is
# frame 2 mid shorten, 3 is frame 3 mid shorten, and 4 is longest!" (the
# owner, 2026-11-13): level k is a press on the k-th frame of the window,
# ILL_PRESS_FIRST - 1 + k frames after the side-B.
ILL_LEVELS = 4
LEVEL_CYCLE, LEVEL_ANY = 0, 5


def press_level(press):
    """The level of a press `press` frames after the side-B (0: outside
    the window)."""
    if ILL_PRESS_FIRST <= press <= ILL_PRESS_LAST:
        return press - ILL_PRESS_FIRST + 1
    return 0


class FoxIllusionShorten(Drill):
    id = "fox-illusion-shorten"
    name = "Shortened Illusion"
    goal = "Stop Fox Illusion short with a second B press"
    part = "tech"
    cpu = None
    characters = ("fox",)
    flow = True
    WAIT, START, DASH = range(3)
    OPT_LEVEL = 0
    options = (Option("Level", ["1 to 4 in turn", "1 (shortest)", "2", "3",
                                "4 (longest)", "Any"], 0,
                      "Which shortened Illusion counts: the frame of the "
                      "window the second B is on."),)
    help = ("Shortened Illusion: side+B, then B again as the",
            "dash begins (19 to 22 frames later).",
            "D-Pad up: guide. D-Pad down: reset.")
    def build_reference(self, c):
        # Side-B, then B on the level's frame (any level: 20 frames later,
        # as the C's reference)
        want = self.level(c) or 2
        return [Ref(0, 10, 1, 127, 0, buttons=B),
                Ref(0, 10 + ILL_PRESS_FIRST - 1 + want, 1, buttons=B)]

    def guide(self, c):
        return ["Fox Illusion (side+B) always travels the same",
                "distance unless you press B again as the dash",
                "begins. Then it stops short: aim it at the",
                "ledge or the stage and be harder to predict.",
                "Press B %d to %d frames after the side+B."
                % (ILL_PRESS_FIRST, ILL_PRESS_LAST),
                "Level 1 is the window's first frame (shortest),",
                "level 4 its last. Earlier, the press is ignored."]

    def init(self):
        self.target = 1             # in turn: the level asked for next

    def level(self, c):
        """The level asked for (0: any)."""
        opt = c.opt(self.OPT_LEVEL)
        if opt == LEVEL_ANY:
            return 0
        return self.target if opt == LEVEL_CYCLE else opt

    def status(self, c):
        want = self.level(c)
        if not want:
            return "Any level: B %d to %d frames after side+B" % (
                ILL_PRESS_FIRST, ILL_PRESS_LAST)
        return "Level %d: B %d frames after side+B" % (
            want, ILL_PRESS_FIRST - 1 + want)

    def timeline(self, c):
        want = self.v.get("want", 0)
        perfect = (ILL_PRESS_FIRST + want,) if want else ()
        return ([Row("Side+B", state=lambda st: st == ILLUSION_START,
                     perfect=(1,)),
                 Row("B", buttons=B, perfect=perfect, start=2,
                     window=(ILL_PRESS_FIRST + 1, ILL_PRESS_LAST + 1)),
                 Row("Dash", state=lambda st: st == ILLUSION_DASH,
                     entered=False)],
                "Side+B is frame 1: B on frames %d to %d is levels 1 to 4."
                % (ILL_PRESS_FIRST + 1, ILL_PRESS_LAST + 1))

    def setup(self, c):
        c.place_solo(0.0)
        self.v = dict(frame=0, press=0, dash=0)

    def think(self, c):
        v = self.v
        if c.phase != self.WAIT:
            v["frame"] += 1
            if v["press"] == 0 and c.down & B:
                v["press"] = v["frame"] - 1

        if c.phase == self.WAIT:
            if c.state == ILLUSION_START and c.state_frames == 1:
                c.set_phase(self.START)
                c.tl_begin()
                v.update(frame=1, press=0, dash=0, want=self.level(c))
            elif c.state == ILLUSION_AIR_FIRST and c.state_frames == 1:
                c.result(False, "Use it on the ground here")
            return

        if c.phase == self.START:
            if c.state == ILLUSION_START:
                if v["frame"] > ILL_TIMEOUT:
                    c.result(False, "Illusion did not finish")
                return
            c.set_phase(self.DASH)
            # fall through

        if c.phase == self.DASH:
            if c.state == ILLUSION_DASH:
                v["dash"] += 1
                return
            if v["press"] != 0:
                # how far from the earliest press that works
                c.measure(v["press"], ILL_PRESS_FIRST)
            c.report("dash", v["dash"])
            c.report("press", v["press"])
            if c.state != ILLUSION_END:
                c.result(False, "Illusion interrupted")
            elif v["dash"] >= ILL_DASH_FULL:
                if v["press"] == 0:
                    c.result(False, "Full length: no B press\n"
                             "B %d to %d frames after"
                             % (ILL_PRESS_FIRST, ILL_PRESS_LAST))
                elif v["press"] < ILL_PRESS_FIRST:
                    c.result(False, "Too early: B %d frames after\n"
                             "want %d or later"
                             % (v["press"], ILL_PRESS_FIRST))
                else:
                    c.result(False, "Too late: B %d frames after\n"
                             "want %d or sooner"
                             % (v["press"], ILL_PRESS_LAST))
            else:
                self.judge_level(c, press_level(v["press"]))

    def judge_level(self, c, got):
        """A shortened Illusion of level `got` (1 to 4; 0 if the press was
        not in the window, which the game should not shorten for)."""
        want = self.v["want"]
        dash = self.v["dash"]
        c.report("level", got)
        if want == 0 or got == want:
            if c.opt(self.OPT_LEVEL) == LEVEL_CYCLE:
                self.target = self.target % ILL_LEVELS + 1
            c.result(True, "Level %d Illusion\nB %d frames after, %d of "
                     "4 dash frames" % (got, self.v["press"], dash))
        elif got < want:
            c.result(False, "Level %d: B %d early\nwant level %d"
                     % (got, want - got, want))
        else:
            c.result(False, "Level %d: B %d late\nwant level %d"
                     % (got, got - want, want))


DRILLS = [FoxShdl, FoxIllusionShorten]
