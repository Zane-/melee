"""Defense drills, second file: fox-ledgedash-attack (getting off the ledge)
and fox-escape-chaingrab.

Port of src/tmce/events/course/drills/defense_escapes.inc.h (specs:
data/courses/fox.md, Defense 11, 6). The grab-and-throw opening of
fox-escape-chaingrab is defense.inc.h's (tg_Setup, tg_Advance), copied
here as `ThrowOpening`.

fox-escape-chaingrab's first version, a Marth that walked to stand under
the falling player, never landed a regrab: the player came down inside his
grab's reach, and he is only free about 15 frames before the landing.
"""
from melee_course.engine import (
    B, R, X, Z, Drill, Option, Ref, CLIFF_CATCH, CLIFF_WAIT, WAIT,
    CAPTURE_PULLED_HI, DAMAGE_FALL, DAMAGE_FIRST, DAMAGE_LAST, PASSIVE,
    PASSIVE_STAND_B, THROWN_F)
from melee_course.drills.tech_ledge import (
    LedgeIntang, LD_REF_DROP, LD_REF_JUMP, LD_REF_DODGE)

CAPTURE_FOOT = 232             # the last of the held states
THROWN_LW_WOMEN = 243          # the last of the thrown states
DOWN_BOUND_U, DOWN_SPOT_D = 183, 198


def on_ledge(state):
    return state in (CLIFF_CATCH, CLIFF_WAIT)


def player_grabbed(c):
    """nr_PlayerGrabbed (fox_neutral_reads.inc.h)."""
    return CAPTURE_PULLED_HI <= c.state <= CAPTURE_FOOT


def cpu_grabbed(c):
    """fpr_CpuGrabbed (fox_pressure.inc.h)."""
    return CAPTURE_PULLED_HI <= c.cpu_state <= CAPTURE_FOOT


def is_thrown(state):
    return THROWN_F <= state <= THROWN_LW_WOMEN


def is_down(state):
    return DOWN_BOUND_U <= state <= DOWN_SPOT_D


def is_tech(state):
    return PASSIVE <= state <= PASSIVE_STAND_B


def player_stick(c):
    """The player's main stick, raw (the C reads hd->input.lstick)."""
    s = c.s
    pad = s.n.pads(game=True)[s.person] if s.live else s.player_pad
    return pad["lx"], pad["ly"]


# ---- fox-ledgedash-attack ---------------------------------------------------
#
# The player hangs on the ledge; Marth waits just inside it, facing out.
# When the player leaves the ledge, by any option, Marth waits his reaction
# time and forward smashes at the ledge. Getting onto the stage unhit, or
# hitting him, is the goal: a ledgedash is still intangible when the smash
# arrives, a slow getup is not, a roll ends up behind him.

LA_OPT_REACTION = 0
LA_MARK_FREE = 1
LA_HANG, LA_REACT, LA_SMASH = range(3)

LA_CPU_FROM_LEDGE = 22.0
LA_SAFE = 40              # frames standing on the stage unhit
LA_SMASH_LEAD = 8         # he starts this long before the player can be hit
LA_REACTIONS = (20, 14, 9)


class DefLedgeAttack(Drill):
    id = "fox-ledgedash-attack"
    name = "Get off the Ledge"
    goal = "Onto the stage past an opponent waiting at the ledge"
    part = "defense"
    stage = "final-destination"
    cpu = "marth"
    characters = ("fox",)
    options = (
        Option("CPU Reaction", ["Slow (20)", "Normal (14)", "Fast (9)"], 1,
               "Frames the CPU takes to swing once you leave the ledge."),
    )
    help = ("Get from the ledge onto the stage past Marth, who",
            "swings when he sees you move.",
            "D-Pad up: guide. D-Pad down: reset.")
    # The demonstration: the ledgedash of universal-ledgedash, then shine
    # as the landing ends.
    reference = [
        Ref(0, LD_REF_DROP, 1, -127, 0),
        Ref(0, LD_REF_DROP + LD_REF_JUMP, 1, 127, 0, buttons=X),
        Ref(0, LD_REF_DROP + LD_REF_DODGE, 2, 110, -65, buttons=R,
            trigger=140),
        Ref(LA_MARK_FREE, 1, 1, 0, -127, buttons=B),
    ]
    live_marks = True

    def guide(self, c):
        return ["On the ledge with someone waiting, every way",
                "up has a moment they can hit.",
                "Getup, getup attack, roll, jump: slow, and",
                "they see it coming.",
                "Ledgedash: you are on the stage, still",
                "intangible, before they can react. Then act:",
                "shine or grab them.",
                "Marth swings as your intangibility runs out."]

    def setup(self, c):
        c.place_on_ledge()
        self.lint = LedgeIntang()
        self.lint.place()
        # where the placement put the player (hd->phys.pos.X)
        ledge_x = c.n.state()["p"][c.s.person]["x"]
        # Marth inside the ledge, facing it
        c.place_cpu(ledge_x + LA_CPU_FROM_LEDGE, -1.0, 20.0)
        self.v = dict(frame=0, safe=0, smashed=False)

    def think(self, c):
        v, me, cd = self.v, c.me, c.cpu
        self.lint.frame(c)
        react = LA_REACTIONS[1] if c.is_demo \
            else LA_REACTIONS[c.opt(LA_OPT_REACTION)]
        if c.phase == LA_HANG:
            if on_ledge(c.state) or c.state < 0:
                return
            c.set_phase(LA_REACT)
            v["frame"] = 0
            # fall through
        v["frame"] += 1
        if c.phase == LA_REACT and v["frame"] >= react:
            c.set_phase(LA_SMASH)
        if c.phase == LA_SMASH and not v["smashed"] and \
                self.lint.left <= LA_SMASH_LEAD and self.lint.kind_game == 0:
            # toward wherever the player is now, timed for the end of the
            # ledge intangibility (swinging on reaction alone missed a
            # plain getup, which is intangible longer)
            c.cpu_press(cx=-127 if me.pos[0] < cd.pos[0] else 127)
            v["smashed"] = True
        if c.state == WAIT and not me.airborne:
            c.mark(LA_MARK_FREE)
            v["safe"] += 1
        if c.hmn_hit or player_grabbed(c):
            c.report("frame", v["frame"])
            c.result(False, "Hit on the way up: %d frames off the ledge"
                     % v["frame"])
        elif c.cpu_hit or cpu_grabbed(c):
            c.measure(v["frame"], v["frame"])
            c.report("frame", v["frame"])
            c.report("galint", self.lint.left)
            c.result(True, "Off the ledge and hit him: %d frames after "
                           "letting go" % v["frame"])
        elif v["safe"] > LA_SAFE:
            c.result(True, "On the stage, unhit")
        elif on_ledge(c.state) and v["frame"] > 10:
            c.result(False, "Back on the ledge")
        elif c.fell() or v["frame"] > 400:
            c.result(False, "Fell")


# ---- the throw that opens fox-escape-chaingrab (defense.inc.h) --------------
#
# The CPU stands next to the player, grabs, and throws. The player is to
# let it. `thrown` counts the frames since the throw let go.

TG_DISTANCE = 6.7      # FPR_DISTANCE (fox_pressure.inc.h)
TG_GRAB_AT = 20        # attempt frame of the CPU's grab
TG_THROW_AFTER = 10    # frames holding the player before the throw
TG_GIVE_UP = 150       # no grab by then: the player avoided it


class ThrowOpening:
    """tg_Setup / tg_Advance."""

    def setup(self, c, percent, stick_y):
        hmn_x = -c.side * (TG_DISTANCE / 2)
        c.place(hmn_x, hmn_x + c.side * TG_DISTANCE, False, 0.0,
                hmn_percent=percent)
        self.held = 0
        self.thrown = 0
        self.stick_y = stick_y

    def advance(self, c):
        """Runs the grab and throw. True from the frame the throw starts."""
        if self.thrown > 0:
            self.thrown += 1
            return True
        if player_grabbed(c):
            self.held += 1
            if self.held >= TG_THROW_AFTER:
                c.cpu_press(ly=self.stick_y)
        elif self.held > 0:
            if is_thrown(c.me.state):
                return False     # the throw's own animation, and its damage
            self.thrown = 1      # let go
            return True
        elif c.timer == TG_GRAB_AT:
            c.cpu_press(Z)
        elif c.timer > TG_GIVE_UP:
            c.retry("Stand still\nlet it grab you")
        return False


# ---- fox-escape-chaingrab ---------------------------------------------------
#
# Marth grabs the player, up throws, and grabs again as the player comes
# down, for as long as it works. The player holds a DI direction through
# each throw and, if hitstun ends before the grab arrives, jumps or shines
# away.
#
# Marth is only free about 15 frames before the player lands, so he does
# not reposition: he turns round if the player is coming down behind him,
# runs in if they are out of reach, and presses grab EC_GRAB_LEAD frames
# before they reach the ground.

EC_OPT_PERCENT = 0
EC_MARK_FREE, EC_MARK_LOW = 1, 2
EC_FIRST, EC_AIR, EC_HELD = range(3)

EC_MAX_REGRABS = 3
EC_SAFE = 30          # frames free and ungrabbed that count as out
EC_REACH = 14.0       # his grab reaches a player this far in front
EC_GRAB_LEAD = 8.0    # frames before the ground he presses grab


class DefChaingrab(Drill):
    id = "fox-escape-chaingrab"
    name = "Escape Marth's Chain Grab"
    goal = "DI the up throws and get out of the chain"
    part = "defense"
    stage = "final-destination"
    cpu = "marth"
    characters = ("fox",)
    options = (
        Option("Your Percent", count=151, default=10, fmt="%d%%",
               desc="Your damage at the start of each attempt. The chain "
                    "is tightest at low percent."),
    )
    help = ("Marth chain grabs you. DI each throw and jump or",
            "shine out the moment you can.",
            "D-Pad up: guide. D-Pad down: reset.")
    # The demonstration: hold the stick away from Marth from the grab on,
    # and tech away as Fox comes down (at low percent the stun outlasts the
    # fall, so jumping out is not possible: a jump at the end of the stun
    # was tried and Fox was already on the floor).
    reference = [
        Ref(0, TG_GRAB_AT + 8, 600, -127, 0),
        Ref(EC_MARK_LOW, 1, 1, -127, 0, buttons=R, trigger=140),
    ]
    live_marks = True

    def guide(self, c):
        return ["Marth's up throw drops a fast faller back into",
                "his hands, again and again, until percent or",
                "your DI ends it.",
                "Hold the stick left or right through every",
                "throw: he has to move to catch you.",
                "Then tech the landing (L or R as you come",
                "down), or jump out if the stun ends in the air.",
                "Stand still and let him grab you first."]

    def setup(self, c):
        self.tg = ThrowOpening()
        self.tg.setup(c, float(c.opt(EC_OPT_PERCENT)), 127)
        self.v = dict(regrabs=0, free=0, pressed=False, smashed=False,
                      down=0, acted=False, last_y=0.0)

    def end(self, c, success, words):
        v = self.v
        c.measure(v["regrabs"], 0)
        c.report("regrabs", v["regrabs"])
        c.result(success, words % v["regrabs"])

    @staticmethod
    def air(c):
        """EC_AIR begins: the throw let go. The C sees that through
        hd->state_id in the frame Marth's throw animation releases, this
        a frame later (Ctx.mark): the phase began a frame back, and its
        timer (the `> 6` gates) is a frame on."""
        c.set_phase(EC_AIR)
        c.timer = 1

    def chase(self, c):
        """Marth between throws: get the player in front of him, then
        grab."""
        v, me, cd = self.v, c.me, c.cpu
        dx = me.pos[0] - cd.pos[0]
        fall = v["last_y"] - me.pos[1]
        # how far in front of Marth the player is (negative: behind him)
        front = dx * cd.facing
        if v["pressed"]:
            return
        if front > EC_REACH:
            c.cpu_press(lx=127 if dx > 0 else -127)      # run to them
        elif front < -2.0:
            c.cpu_press(lx=50 if dx > 0 else -50)        # turn round
        elif fall > 0 and me.pos[1] < fall * EC_GRAB_LEAD:
            c.cpu_press(Z)
            v["pressed"] = True

    def think(self, c):
        v, me, cd = self.v, c.me, c.cpu
        dx = me.pos[0] - cd.pos[0]
        hitstun = me.hitstun > 0

        if not self.tg.advance(c):
            v["last_y"] = me.pos[1]
            return          # the first grab and throw
        if c.phase == EC_FIRST:
            self.air(c)
            v["free"] = 0
            v["pressed"] = False

        if c.phase == EC_AIR:
            if is_down(c.state):
                # missed the tech and lies there: Marth stops (a smash does
                # not come out of a walk at once) and forward smashes
                v["down"] += 1
                if v["down"] > 8 and not v["smashed"]:
                    c.cpu_press(cx=127 if dx > 0 else -127)
                    v["smashed"] = True
            else:
                self.chase(c)
            # free: out of hitstun and doing something of the player's own
            lx, ly = player_stick(c)
            if c.held != 0 or lx != 0 or ly != 0:
                v["acted"] = True    # doing nothing is not an escape
            if v["acted"] and not hitstun and c.timer > 6 and \
                    not is_down(c.state) and not is_tech(c.state) and \
                    c.state != DAMAGE_FALL and \
                    not DAMAGE_FIRST <= c.state <= DAMAGE_LAST:
                v["free"] += 1
            if not hitstun and c.timer > 6:
                c.mark(EC_MARK_FREE)
            fall = v["last_y"] - me.pos[1]
            if fall > 0 and me.pos[1] < fall * 10.0 and c.timer > 6:
                c.mark(EC_MARK_LOW)          # about to land: tech now
            if player_grabbed(c):
                v["regrabs"] += 1
                if v["regrabs"] >= EC_MAX_REGRABS:
                    self.end(c, False, "Chain grabbed %d times: DI away and "
                                       "jump out")
                else:
                    c.set_phase(EC_HELD)
            elif c.hmn_hit and c.timer > 6:
                self.end(c, False, "Hit out of the chain: after %d regrabs")
            elif c.cpu_hit:
                self.end(c, True, "Out, and hit him! after %d regrabs")
            elif v["free"] > EC_SAFE:
                self.end(c, True, "Out of the chain grab: after %d regrabs")
            elif c.timer > 400:
                c.retry("Resetting")
        elif c.phase == EC_HELD:
            # held again: throw up after a moment, as the opening does
            if player_grabbed(c):
                if c.timer >= TG_THROW_AFTER:
                    c.cpu_press(ly=127)
            elif not is_thrown(me.state):
                self.air(c)
                v["free"] = 0
                v["pressed"] = False
                v["down"] = 0
        v["last_y"] = me.pos[1]


DRILLS = [DefLedgeAttack, DefChaingrab]
