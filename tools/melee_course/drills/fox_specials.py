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
    B, X, Drill, Ref, WAIT, KNEEBEND, LANDING)
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


def own_items(c):
    """Items in play that belong to the player (lasers, here; and the
    blaster while it is out, as in the C). The native build's item list
    does not say whose an item is; these drills have no opponent and the
    match no items, so every item is the player's."""
    return len(c.n.state().get("items") or ())


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
        return dict(short_hop=0, frame=0, first_laser=0, lasers=0, items=0)

    def setup(self, c):
        c.place_solo(0.0)
        self.v = self._clear()

    def think(self, c):
        me = c.fd
        items = own_items(c)

        if c.phase == self.WAIT:
            if c.state == KNEEBEND:
                c.set_phase(self.SQUAT)
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
        if v["first_laser"] == 0 and \
                LASER_AIR_START <= c.state <= LASER_AIR_END:
            v["first_laser"] = v["frame"]
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


# ---- fox-illusion-shorten ---------------------------------------------------

ILL_DASH_FULL = 4       # dash frames of an Illusion not shortened
ILL_PRESS_FIRST = 19    # frames after side-B the press works from
ILL_PRESS_LAST = 22
ILL_TIMEOUT = 120


class FoxIllusionShorten(Drill):
    id = "fox-illusion-shorten"
    name = "Shortened Illusion"
    goal = "Stop Fox Illusion short with a second B press"
    part = "tech"
    cpu = None
    characters = ("fox",)
    flow = True
    WAIT, START, DASH = range(3)
    help = ("Shortened Illusion: side+B, then B again as the",
            "dash begins (19 to 22 frames later).",
            "D-Pad up: guide. D-Pad down: reset.")
    # Side-B, then B 20 frames later: the shortest Illusion.
    reference = [
        Ref(0, 10, 1, 127, 0, buttons=B),
        Ref(0, 30, 1, buttons=B),
    ]

    def guide(self, c):
        return ["Fox Illusion (side+B) always travels the same",
                "distance unless you press B again as the dash",
                "begins. Then it stops short: aim it at the",
                "ledge or the stage and be harder to predict.",
                "Press B %d to %d frames after the side+B."
                % (ILL_PRESS_FIRST, ILL_PRESS_LAST),
                "The earlier in that window, the shorter.",
                "Earlier than that, the press is ignored."]

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
                v.update(frame=1, press=0, dash=0)
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
            elif v["dash"] <= 1:
                c.result(True, "Shortest Illusion\nB %d frames after"
                         % v["press"])
            else:
                c.result(True, "Shortened: %d of 4 dash\n"
                         "frames, B %d after" % (v["dash"], v["press"]))


DRILLS = [FoxShdl, FoxIllusionShorten]
