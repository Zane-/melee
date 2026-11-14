"""Fox's offstage Punish drills: fox-shine-spike and fox-edgeguard-onstage.

Port of src/tmce/events/course/drills/punish_offstage.inc.h (specs:
data/courses/fox.md, Punish 9, 10).

Marth starts in the air off the left ledge with his double jump and
recovers by himself (`recover`): either high (jump at once, up B to land on
the stage) or low (fall, jump late, up B to the ledge). The player stands
near the ledge.
"""
from melee_course.engine import (
    B, X, Drill, Option, CLIFF_CATCH, CLIFF_WAIT, DEAD_LAST, FOX_SHINE_FIRST,
    FOX_SHINE_LAST)

OPT_CHOICE, OPT_PERCENT = range(2)
HIGH, LOW, CHOICES = range(3)
EDGEGUARD, RETURN = range(2)

CPU_OUT = 58.0      # Marth starts this far outside the ledge
CPU_UP = 6.0        # and this far above it
PLAYER_IN = 18.0    # the player this far inside it
BACK = 25           # frames Marth stands on the stage = recovered
TIMEOUT = 700
HANG = 15           # frames he hangs before getting up


def on_ledge(state):
    return state in (CLIFF_CATCH, CLIFF_WAIT)


def is_shine(state):
    return FOX_SHINE_FIRST <= state <= FOX_SHINE_LAST


def player_dead(c):
    return c.me.state <= DEAD_LAST


def cpu_dead(c):
    return c.cpu.state <= DEAD_LAST


OPTIONS = (
    Option("CPU Recovery", ["Random", "High", "Low"], 0,
           "High: jumps at once and up Bs onto the stage. "
           "Low: falls, jumps late and up Bs to the ledge."),
    Option("CPU Percent", count=201, default=80, fmt="%d%%",
           desc="The CPU's damage at the start of each attempt."),
)


class Offstage(Drill):
    """What the two drills share: the placement, Marth's recovery and the
    bookkeeping (os_Setup, os_CpuRecover, os_Advance)."""
    part = "punish"
    stage = "final-destination"
    cpu = "marth"
    characters = ("fox",)
    options = OPTIONS

    def setup(self, c):
        opt = c.opt(OPT_CHOICE)
        percent = float(c.opt(OPT_PERCENT))
        self.v = v = dict(ledge=(0.0, 0.0), choice=0, jumped=False,
                          upb=False, last_y=0.0, on_stage=0, hang=0, frame=0,
                          shined=False, left_stage=False)
        ledge = c.ledge_pos()
        if ledge is None:
            return
        v["ledge"] = ledge
        lx, ly = ledge
        # facing -1: looking out at him
        c.place_on_platform(lx + PLAYER_IN, ly + 20.0, facing=-1.0)
        c.place_in_air(c.s.cpu_port, lx - CPU_OUT, ly + CPU_UP, 1.0, percent)
        v["choice"] = opt - 1 if opt > 0 else c.randi(CHOICES)
        v["last_y"] = ly + CPU_UP

    def recover(self, c):
        """Marth's recovery. One input per decision; the stick stays toward
        the stage."""
        v, cd = self.v, c.cpu
        lx, ly = v["ledge"]
        dy = cd.pos[1] - ly
        falling = cd.pos[1] < v["last_y"]
        jump_below = 8.0 if v["choice"] == HIGH else -28.0
        upb_below = -2.0 if v["choice"] == HIGH else -18.0

        v["last_y"] = cd.pos[1]
        if not cd.airborne:
            v["on_stage"] += 1
            return
        v["on_stage"] = 0
        if on_ledge(cd.state):
            v["hang"] += 1
            if v["hang"] > HANG:
                c.cpu_press(lx=127)      # get up
            return
        v["hang"] = 0
        c.cpu_press(lx=127)
        if cd.hitstun > 0:
            v["upb"] = False             # hit out of it: he may up B again
            return
        if not v["jumped"] and dy < jump_below:
            c.cpu_press(X)
            v["jumped"] = True
        elif v["jumped"] and not v["upb"] and falling and dy < upb_below:
            c.cpu_press(B, lx=40, ly=127)
            v["upb"] = True

    def advance(self, c):
        """Shared bookkeeping. False when the attempt has been decided."""
        v, me = self.v, c.me
        lx = v["ledge"][0]
        v["frame"] += 1
        if c.phase == EDGEGUARD:
            self.recover(c)
        if me.pos[0] < lx - 12.0:
            v["left_stage"] = True
        if c.cpu_hit and is_shine(me.state) and c.cpu.pos[0] < lx:
            v["shined"] = True
        c.report("choice", v["choice"])
        c.report("shined", int(v["shined"]))
        if player_dead(c):
            c.result(False, "Got the stock, lost yours: save your jump to "
                            "get back" if c.phase == RETURN else "You fell")
            return False
        if c.hmn_hit:
            c.result(False, "Hit by the recovery")
            return False
        if c.phase == EDGEGUARD and v["on_stage"] > BACK:
            c.result(False, "He made it back: high: he lands on the stage"
                     if v["choice"] == HIGH else
                     "He made it back: low: he goes for the ledge")
            return False
        if v["frame"] > TIMEOUT:
            c.result(False, "Out of time")
            return False
        return True


# ---- fox-shine-spike --------------------------------------------------------


class FoxShineSpike(Offstage):
    id = "fox-shine-spike"
    name = "Shine Spike"
    goal = "Shine him off the stage and get back"
    help = ("Go out, shine him off the stage, and get back.",
            "",
            "D-Pad up: guide. D-Pad down: reset.")

    def guide(self, c):
        return ["Off the stage the shine sends them sideways",
                "and down with their jump gone: one touch ends",
                "the stock.",
                "1. Go out to them: run off, or jump out.",
                "2. Down+B when you touch them.",
                "3. Jump out of the shine and get back: keep",
                "   your double jump for that.",
                "High recovery or low: watch which he picks."]

    def think(self, c):
        v = self.v
        if not self.advance(c):
            return
        if c.phase == EDGEGUARD:
            if cpu_dead(c):
                c.set_phase(RETURN)
        elif c.phase == RETURN:
            if on_ledge(c.state) or (not c.me.airborne and
                                     c.me.pos[0] > v["ledge"][0]):
                c.report("shined", int(v["shined"]))
                if v["shined"]:
                    c.result(True, "Shine spike! and back on the stage")
                else:
                    c.result(False, "The stock, but no shine: that is the "
                                    "Edgeguard drill")


# ---- fox-edgeguard-onstage --------------------------------------------------


class FoxEdgeguard(Offstage):
    id = "fox-edgeguard-onstage"
    name = "Edgeguard from the Stage"
    goal = "Stop a recovery without leaving the stage"
    help = ("Stop his recovery without leaving the stage: hit",
            "him as he lands, or take the ledge.",
            "D-Pad up: guide. D-Pad down: reset.")

    def guide(self, c):
        return ["You do not have to leave the stage to stop a",
                "recovery. Watch which way he comes:",
                "High, landing on the stage: hit him as he",
                "  arrives (back air, up smash, down smash).",
                "Low, to the ledge: take the ledge yourself so",
                "  he cannot, or down smash as he grabs it.",
                "The stock has to go: one hit is often not",
                "enough, so be ready for the second try."]

    def think(self, c):
        v = self.v
        if not self.advance(c):
            return
        if cpu_dead(c):
            c.report("left_stage", int(v["left_stage"]))
            c.measure(v["frame"], v["frame"])
            c.result(True, "Stock taken: but you went out for it"
                     if v["left_stage"] else "Edgeguarded from the stage")


DRILLS = [FoxShineSpike, FoxEdgeguard]
