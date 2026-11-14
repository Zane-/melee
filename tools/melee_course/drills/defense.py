"""Defense drills, first file: universal-tech, fox-escape-techchase,
fox-combo-shine, universal-asdi-down, universal-di-survival.

Port of src/tmce/events/course/drills/defense.inc.h (specs:
data/courses/fox.md, Defense). Here the CPU attacks and the player is
graded on the answer.

What the C reads that the native build does not report is derived here:
`hd->flags.hitstun` is `hitstun > 0` (the host reports the frames left
while the flag is set, and the game clears the flag as they reach 0).
"""
from melee_course.engine import (
    A, B, L, R, Z, Drill, Option, Ref, WAIT, LANDING, SQUAT, SQUAT_RV,
    SQUAT_WAIT, DAMAGE_FALL, DAMAGE_FIRST, DAMAGE_LAST, GUARD_SET_OFF,
    DEAD_LAST)

# ---- action states the engine has no name for (ftCommon/forward.h) ----------

DAMAGE_FLY_HI, DAMAGE_FLY_ROLL = 87, 91
DOWN_BOUND_U, DOWN_SPOT_D = 183, 198
PASSIVE, PASSIVE_STAND_B = 199, 201
CAPTURE_PULLED_HI, CAPTURE_FOOT = 223, 232
THROWN_F, THROWN_LW_WOMEN = 239, 243
# Fox's shine, ground and air (fox_shine_tech.inc.h: FST_GROUND_START ..
# FST_AIR_LAST).
SHINE_FIRST, SHINE_LAST = 0x168, 0x171

# fox_pressure.inc.h: the two stand this far apart.
FPR_DISTANCE = 6.7
# fox_neutral.inc.h: frames before the CPU attacks, at least and spread.
AP_WAIT_MIN, AP_WAIT_SPAN = 40, 60


def _percent_option(default, desc="Your damage at the start of each "
                    "attempt.", count=151):
    return Option("Your Percent", count=count, default=default, fmt="%d%%",
                  desc=desc)


# ---- what the C drills share (df_*, nr_*, fpr_*, fst_*) ---------------------


def is_down(state):
    return DOWN_BOUND_U <= state <= DOWN_SPOT_D


def is_tech(state):
    return PASSIVE <= state <= PASSIVE_STAND_B


def is_shine(state):
    return SHINE_FIRST <= state <= SHINE_LAST


def player_dead(c):
    return c.me.state <= DEAD_LAST


def player_grabbed(c):
    """nr_PlayerGrabbed: the player is held (by the end of the last
    frame)."""
    return CAPTURE_PULLED_HI <= c.state <= CAPTURE_FOOT


def cpu_grabbed(c):
    """fpr_CpuGrabbed."""
    return CAPTURE_PULLED_HI <= c.cpu_state <= CAPTURE_FOOT


def dist(c):
    """nr_Dist."""
    return abs(c.cpu.pos[0] - c.me.pos[0])


def in_hitstun(f):
    """`fd->flags.hitstun` as the C Think reads it, part-way through the
    frame: the damage states count hitstun down in their animation
    callback (ftCo_8008F744), so the C sees the count reach 0 in the frame
    it does. Here the last frame's count is all there is, and one left
    then is none in the frame being played."""
    if DAMAGE_FIRST <= f.state <= DAMAGE_LAST:
        return f.hitstun > 1
    return f.hitstun > 0


def coming_down(c):
    """df_ComingDown, for the demonstrations' tech: sent flying for a few
    frames and on the way down. Sheik's down throw puts Fox on the ground
    23 frames after it lets go, so a press from here is inside the
    20-frame window."""
    return DAMAGE_FLY_HI <= c.state <= DAMAGE_FLY_ROLL and \
        c.state_frames >= 8 and c.me.vel[1] < 0


def place_close(c, cpu_percent, hmn_percent):
    """The two FPR_DISTANCE apart, the player at `hmn_percent` (course_Place
    and df_SetPercent)."""
    hmn_x = -c.side * (FPR_DISTANCE / 2)
    c.place(hmn_x, hmn_x + c.side * FPR_DISTANCE, False, cpu_percent,
            hmn_percent)


def attack_wait(c):
    return AP_WAIT_MIN if c.is_demo else AP_WAIT_MIN + c.randi(AP_WAIT_SPAN)


# ---- the throw that starts universal-tech and fox-escape-techchase ----------
#
# The CPU stands next to the player, grabs, and throws down. The player is
# to let it. `thrown` counts the frames since the throw let go.

TG_GRAB_AT = 20       # attempt frame of the CPU's grab
TG_THROW_AFTER = 10   # frames holding the player before the throw
TG_GIVE_UP = 150      # no grab by then: the player avoided it


class Throw:
    def __init__(self, c, percent, stick_y):
        place_close(c, 0.0, percent)
        self.held = 0         # frames the player has been held
        self.thrown = 0       # frames since the throw began, 0 = not yet
        self.stick_y = stick_y  # the throw: -127 down, 127 up

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
            if THROWN_F <= c.me.state <= THROWN_LW_WOMEN:
                return False  # the throw's own animation, and its damage
            # let go: by the throw's animation, which the C Think saw in
            # the frame before this one (its 1)
            self.thrown = 2
            return True
        elif c.timer == TG_GRAB_AT:
            c.cpu_press(Z)
        elif c.timer > TG_GIVE_UP:
            c.retry("Stand still\nlet it grab you")
        return False


# ---- universal-tech ---------------------------------------------------------

DT_OPT_ASK, DT_OPT_PERCENT = range(2)
DT_IN_PLACE, DT_AWAY, DT_IN, DT_COUNT = range(4)
DT_MARK_LOW = 1
DT_THROW, DT_AIR, DT_TECH = range(3)
DT_WINDOW = 20        # frames before the ground a press counts
DT_TIMEOUT = 200
DT_NAMES = ("IN PLACE", "AWAY", "IN")


class DefTech(Drill):
    id = "universal-tech"
    name = "Tech the Ground"
    goal = "Tech in place, away or in, as asked"
    part = "defense"
    cpu = "sheik"
    options = (
        Option("Tech", ["Random", "In Place", "Away", "In"], 0,
               "Which tech the drill asks for."),
        _percent_option(30),
    )
    help = ("Let it throw you, then tech the way the drill asks:",
            "L or R as you land, stick for the direction.",
            "D-Pad up: guide. D-Pad down: reset.")
    live_marks = True

    def build_reference(self, c):
        """R, with the stick held for the direction, as the player comes
        down (DT_MARK_LOW). Positive X is toward the CPU."""
        ask = self.v["ask"]
        lx = -127 if ask == DT_AWAY else 127 if ask == DT_IN else 0
        return [Ref(DT_MARK_LOW, 1, 30, lx),
                Ref(DT_MARK_LOW, 1, 1, lx, buttons=R, trigger=140)]

    def guide(self, c):
        return ["Thrown or knocked down, you choose how you",
                "land. Press L or R in the %d frames before you" % DT_WINDOW,
                "touch the ground:",
                "Stick neutral: tech in place.",
                "Stick left or right: roll that way.",
                "A press too early locks you out for 40 frames:",
                "press once, as you come down.",
                "Stand still and let the opponent grab you."]

    def setup(self, c):
        opt = c.opt(DT_OPT_ASK)
        self.v = dict(throw=Throw(c, float(c.opt(DT_OPT_PERCENT)), -127),
                      told=False, press=0, tech_x=0.0)
        if opt > 0:
            self.v["ask"] = opt - 1
        elif c.is_demo:
            self.v["ask"] = (c.demo_count + DT_COUNT - 1) % DT_COUNT
        else:
            self.v["ask"] = c.randi(DT_COUNT)

    def think(self, c):
        v = self.v
        tg = v["throw"]
        if not tg.advance(c):
            if tg.held > 0 and not v["told"]:
                v["told"] = True
                c.message("Tech %s" % DT_NAMES[v["ask"]])
            return
        if c.down & (L | R):
            v["press"] = tg.thrown
        if coming_down(c):
            c.mark(DT_MARK_LOW)
        if c.phase in (DT_THROW, DT_AIR):
            if is_tech(c.state):
                v["tech_x"] = c.me.pos[0]
                c.set_phase(DT_TECH)
            elif is_down(c.state):
                c.report("ask", v["ask"])
                if v["press"] == 0:
                    c.result(False, "No tech: press L or R as you land")
                else:
                    early = tg.thrown - v["press"]
                    c.measure(early, DT_WINDOW)
                    c.result(False, "Missed: pressed %d frames before "
                             "landing, at most %d" % (early, DT_WINDOW))
            elif tg.thrown > DT_TIMEOUT:
                c.retry("No knockdown\nresetting")
        elif c.phase == DT_TECH:
            if is_tech(c.state):
                return
            # which way it went, seen from the CPU
            moved = (c.me.pos[0] - v["tech_x"]) * c.toward
            did = DT_IN_PLACE if c.prev_state == PASSIVE \
                else DT_AWAY if moved > 0 else DT_IN
            c.report("ask", v["ask"])
            c.report("did", did)
            if did == v["ask"]:
                c.result(True, "Tech! just what was asked")
            else:
                c.message("Teched %s" % DT_NAMES[did])
                c.result(False, "A tech, but the wrong one")


# ---- fox-escape-techchase ---------------------------------------------------
#
# The same throw, but now the CPU chases: once it can see what the player
# did on the ground it waits its reaction time, runs there and grabs. What
# works is acting on the first free frame (jump, shine, spot dodge, attack)
# before the grab arrives, or a tech it cannot reach in time.

TC_OPT_REACTION, TC_OPT_PERCENT = range(2)
TC_MARK_LOW, TC_MARK_FREE = 1, 2
TC_THROW, TC_SEEN, TC_CHASE = range(3)
TC_GRAB_FROM = 14.0
TC_SAFE = 45          # frames free and untouched that count as away
TC_REACTIONS = (24, 16, 10)


class DefTechChase(Drill):
    id = "fox-escape-techchase"
    name = "Escape the Tech Chase"
    goal = "Tech and get away before the regrab"
    part = "defense"
    cpu = "sheik"
    characters = ("fox",)
    options = (
        Option("CPU Reaction", ["Slow (24)", "Normal (16)", "Fast (10)"], 0,
               "Frames the CPU takes to start after it sees your tech."),
        _percent_option(30),
    )
    help = ("Let it throw you, tech, and get away before it",
            "grabs you again.",
            "D-Pad up: guide. D-Pad down: reset.")
    # Tech away, then shine the moment the tech ends (a jump was tried:
    # Sheik's dash grab takes Fox out of his jump squat).
    reference = [
        Ref(TC_MARK_LOW, 1, 30, -127),
        Ref(TC_MARK_LOW, 1, 1, -127, buttons=R, trigger=140),
        Ref(TC_MARK_FREE, 1, 1, 0, -127, buttons=B),
    ]
    live_marks = True

    def guide(self, c):
        return ["After a throw the opponent watches where you",
                "tech and grabs you again there: a tech chase.",
                "Tech away from them to buy time, and act on",
                "your first free frame. Shine is frame 1: a",
                "jump is caught in its 3 frames on the ground.",
                "Not teching at all leaves you on the floor",
                "for them.",
                "Stand still and let the opponent grab you."]

    def setup(self, c):
        self.v = dict(throw=Throw(c, float(c.opt(TC_OPT_PERCENT)), -127),
                      seen=0, pressed=False, free=0)

    def think(self, c):
        v, me, cpu = self.v, c.me, c.cpu
        tg = v["throw"]
        react = TC_REACTIONS[1] if c.is_demo \
            else TC_REACTIONS[c.opt(TC_OPT_REACTION)]
        if not tg.advance(c):
            return
        if coming_down(c):
            c.mark(TC_MARK_LOW)
        busy = is_tech(c.state) or is_down(c.state) or in_hitstun(me) or \
            player_grabbed(c) or DAMAGE_FLY_HI <= c.state <= DAMAGE_FLY_ROLL

        if c.phase == TC_THROW:
            if tg.thrown > 3 and not me.airborne:
                c.set_phase(TC_SEEN)
                v["seen"] = 0
        elif c.phase == TC_SEEN:
            v["seen"] += 1
            if v["seen"] >= react:
                c.set_phase(TC_CHASE)
        elif c.phase == TC_CHASE:
            if not v["pressed"]:
                dx = me.pos[0] - cpu.pos[0]
                c.cpu_press(lx=127 if dx > 0 else -127)
                if abs(dx) < TC_GRAB_FROM:
                    if is_down(c.state):
                        c.cpu_press(cy=-127)   # lying there: down smash
                    else:
                        c.cpu_press(Z)
                    v["pressed"] = True

        if c.phase != TC_THROW:
            if not busy:
                c.mark(TC_MARK_FREE)
                v["free"] += 1
            if tg.thrown > 3 and (player_grabbed(c) or c.hmn_hit):
                c.result(False, "Caught after you were free: act at once"
                         if v["free"] > 0 else "Caught on the ground")
            elif c.cpu_hit:
                c.result(True, "Hit them back!")
            elif v["free"] > TC_SAFE or (v["pressed"] and v["free"] > 0 and
                                         c.cpu_state == WAIT):
                c.result(True, "Got away")
            elif tg.thrown > 400:
                c.retry("Resetting")


# ---- fox-combo-shine --------------------------------------------------------
#
# Marth jabs the player, steps in, and follows with a forward smash that is
# not a true follow-up: there are some frames between the end of the jab's
# hitstun (and the 4 frames of landing after it) and the smash's hitbox.
# The shine (frame 1) fits in them.

CS_OPT_GAP, CS_OPT_PERCENT = range(2)
CS_MARK_FREE = 1
CS_WAIT, CS_JAB, CS_GAP = range(3)
CS_JAB_AT = 30
# Marth cannot smash sooner than about 26 frames after the jab input, which
# leaves the player some 20 free frames. Real strings are tighter, so the
# drill sets the bar itself: the shine has to come within this many frames
# of being free.
CS_GAPS = (12, 8, 4)
CS_SMASH_AT = 28      # frames from the jab input to the smash input


class DefComboShine(Drill):
    id = "fox-combo-shine"
    name = "Shine out of Combos"
    goal = "Shine in the gap between two hits"
    part = "defense"
    cpu = "marth"
    characters = ("fox",)
    options = (
        Option("Gap", ["Wide (12)", "Medium (8)", "Tight (4)"], 0,
               "How many frames after you are free the shine may come "
               "and still count."),
        _percent_option(30),
    )
    help = ("Take the jab, then shine before the forward smash",
            "arrives.",
            "D-Pad up: guide. D-Pad down: reset.")
    reference = [Ref(CS_MARK_FREE, 1, 1, 0, -127, buttons=B)]
    live_marks = True

    def guide(self, c):
        return ["Not every string is a true combo. Between two",
                "hits there is often a moment where you can",
                "act, and Fox's shine comes out on frame 1.",
                "Marth jabs, then forward smashes. Take the jab",
                "and press down+B the instant its stun ends.",
                "The verdict counts the frames you waited: the",
                "Gap option sets how many are allowed.",
                "Do not hold shield: this is about the gap."]

    def setup(self, c):
        place_close(c, 20.0, float(c.opt(CS_OPT_PERCENT)))
        self.v = dict(frame=0, was_stun=False, free=0, shine_free=0)

    def think(self, c):
        v, me = self.v, c.me
        limit = CS_GAPS[c.opt(CS_OPT_GAP)]
        gap = CS_SMASH_AT
        if c.phase == CS_WAIT:
            if c.timer >= CS_JAB_AT:
                c.set_phase(CS_JAB)
                v["frame"] = 0
            return
        if v["frame"] == 0:
            c.cpu_press(A)
        elif v["frame"] == gap:
            c.cpu_press(cx=int(127 * c.toward))
        elif 8 < v["frame"] < gap:
            # step in after the jab: it pushed the player out of reach
            c.cpu_press(lx=int(60 * c.toward))
        v["frame"] += 1
        if c.phase == CS_JAB:
            if c.hmn_hit:
                c.set_phase(CS_GAP)
            elif v["frame"] > 40:
                c.retry("The jab missed\nstand still for it")
            return
        # free: out of hitstun and past the landing that follows it
        if in_hitstun(me):
            v["was_stun"] = True
        elif c.state == WAIT or (c.state == LANDING and
                                 c.state_frames > c.fd.landing_lag) or \
                v["free"] > 0:
            v["free"] += 1
            c.mark(CS_MARK_FREE)
        if v["shine_free"] == 0 and is_shine(me.state):
            v["shine_free"] = v["free"] if v["free"] > 0 else 1
        if c.cpu_hit and is_shine(me.state):
            c.measure(v["shine_free"], 1)
            c.report("frame", v["shine_free"])
            if v["shine_free"] > limit:
                c.result(False, "Too slow: free frame %d, a real gap is "
                         "about %d" % (v["shine_free"], limit))
            else:
                c.result(True, "Shined out! on your free frame %d"
                         % v["shine_free"])
        elif c.hmn_hit and c.timer > 2:
            c.report("free", v["free"])
            c.result(False, "Hit again: you had %d frames to shine"
                     % v["free"])
        elif me.state == GUARD_SET_OFF:
            c.result(False, "Shielded it: shine in the gap instead")
        elif c.cpu_hit or cpu_grabbed(c):
            c.result(True, "Out, but not with the shine")
        elif v["frame"] > gap + 60:
            c.result(False, "The smash missed: shine him anyway")


# ---- universal-asdi-down ----------------------------------------------------
#
# Marth down tilts the player from close range. Crouching (or just holding
# down as it hits) at low percent keeps the player on the ground with little
# stun, in time to hit Marth before his down tilt can be interrupted (frame
# 20). The CPU does not use that interrupt, so the drill fails a hit that
# comes more than AD_SLACK frames after it.

AD_OPT_PERCENT = 0
AD_MARK_FREE = 1
AD_WAIT, AD_ATTACK, AD_PUNISH = range(3)
AD_IASA = 20
AD_SLACK = 4          # frames past that still counted


class DefAsdiDown(Drill):
    id = "universal-asdi-down"
    name = "Crouch Cancel and Punish"
    goal = "Hold the ground through a weak hit and hit back"
    part = "defense"
    cpu = "marth"
    options = (
        _percent_option(20, "Your damage at the start of each attempt. "
                        "Raise it to find where the crouch stops working."),
    )
    help = ("Crouch, take the down tilt, and hit back before",
            "he can shield.",
            "D-Pad up: guide. D-Pad down: reset.")
    reference = [
        Ref(0, 5, 300, 0, -127),
        Ref(AD_MARK_FREE, 1, 1, 0, -127, buttons=B),
    ]
    live_marks = True

    def guide(self, c):
        return ["Holding down when a weak hit lands keeps you",
                "on the ground with almost no stun: you act",
                "while they are still finishing their move.",
                "Crouch, take the down tilt, and hit back at",
                "once (shine, grab, down smash).",
                "Stronger hits and higher percent knock you",
                "over anyway: try Your Percent in the menu."]

    def setup(self, c):
        place_close(c, 20.0, float(c.opt(AD_OPT_PERCENT)))
        self.v = dict(wait=attack_wait(c), frame=0, crouched=0, free=0)

    def think(self, c):
        v, me = self.v, c.me
        if c.phase == AD_WAIT:
            if c.cpu_hit or cpu_grabbed(c):
                c.result(False, "Hit before it attacked: take the hit first")
            elif c.timer >= v["wait"]:
                c.set_phase(AD_ATTACK)
                v["frame"] = 0
            return
        if v["frame"] == 0:
            c.cpu_press(A, ly=-80)
        elif v["frame"] >= AD_IASA:
            c.cpu_shield()
        v["frame"] += 1
        if c.phase == AD_ATTACK:
            if c.hmn_hit:
                v["crouched"] = int(SQUAT <= c.state <= SQUAT_RV or
                                    SQUAT <= c.prev_state <= SQUAT_RV)
                c.set_phase(AD_PUNISH)
            elif me.state == GUARD_SET_OFF:
                c.result(False, "Shielded it: crouch and take it")
            elif v["frame"] > 50:
                c.retry("The down tilt missed\nstay close")
            return
        if c.state in (SQUAT_WAIT, SQUAT, WAIT):
            v["free"] += 1
            c.mark(AD_MARK_FREE)
        c.report("crouched", v["crouched"])
        if is_down(c.state) or c.state == DAMAGE_FALL or \
                DAMAGE_FLY_HI <= me.state <= DAMAGE_FLY_ROLL:
            c.result(False, "Knocked over: too much percent for this")
        elif c.cpu_hit or cpu_grabbed(c):
            c.measure(v["frame"], AD_IASA)
            c.report("frame", v["frame"])
            if v["frame"] > AD_IASA + AD_SLACK:
                # the CPU does not use its early interrupt, a player would
                c.result(False, "Hit on frame %d of his move: he can act "
                         "from frame %d" % (v["frame"], AD_IASA))
            elif v["crouched"]:
                c.result(True, "Crouch cancel punish! on frame %d of his "
                         "move" % v["frame"])
            else:
                c.result(True, "Punished: on frame %d" % v["frame"])
        elif c.cpu_state == GUARD_SET_OFF:
            c.result(False, "Too slow: blocked" if v["crouched"]
                     else "Too slow: blocked, hold down as it hits")
        elif v["frame"] > 90:
            c.result(False, "No punish")


# ---- universal-di-survival --------------------------------------------------
#
# Fox up smashes the player at a percent where it kills off the top without
# DI and does not with it. The stick has to be held sideways on the frame
# the hit's freeze ends.

DS_DEFAULT_PERCENT = 90   # found with a sweep in the simulator
DS_OPT_PERCENT = 0
DS_MARK_ATTACK = 1
DS_WAIT, DS_ATTACK, DS_FLY = range(3)
DS_SURVIVE = 150      # frames alive after the hit that count as lived


class DefDiSurvival(Drill):
    id = "universal-di-survival"
    name = "Survival DI"
    goal = "DI the kill move and live"
    part = "defense"
    cpu = "fox"
    options = (_percent_option(DS_DEFAULT_PERCENT, count=201),)
    help = ("Hold left or right as the up smash hits, and",
            "survive it.",
            "D-Pad up: guide. D-Pad down: reset.")
    # Hold the stick away from the CPU from just before the hit.
    reference = [Ref(DS_MARK_ATTACK, 5, 40, -127)]
    live_marks = True

    def guide(self, c):
        return ["The stick, held as a hit's freeze ends, bends",
                "the path you are sent on (DI). You cannot slow",
                "down, only turn.",
                "Fox's up smash sends you straight up to the",
                "top. Hold left or right as it hits: the path",
                "leans toward the corner, which is further.",
                "Up or down does nothing here: DI works across",
                "the direction you are sent, not along it."]

    def setup(self, c):
        place_close(c, 20.0, float(c.opt(DS_OPT_PERCENT)))
        self.v = dict(wait=attack_wait(c), frame=0, fly=0)

    def think(self, c):
        v, me = self.v, c.me
        if c.phase == DS_WAIT:
            if c.timer >= v["wait"]:
                c.mark(DS_MARK_ATTACK)
                c.set_phase(DS_ATTACK)
                v["frame"] = 0
        elif c.phase == DS_ATTACK:
            if v["frame"] == 0:
                c.cpu_press(cy=127)
            v["frame"] += 1
            if c.hmn_hit:
                c.set_phase(DS_FLY)
                v["fly"] = 0
            elif me.state == GUARD_SET_OFF:
                c.result(False, "Shielded it: take the hit and DI")
            elif v["frame"] > 50:
                c.retry("The up smash missed\nstay close")
        elif c.phase == DS_FLY:
            v["fly"] += 1
            if player_dead(c):
                c.measure(v["fly"], DS_SURVIVE)
                c.result(False, "Star KO after %d frames: hold left or "
                         "right as it hits" % v["fly"])
            elif v["fly"] > DS_SURVIVE or (v["fly"] > 30 and
                                           not in_hitstun(me) and
                                           me.vel[1] <= 0):
                c.measure(v["fly"], v["fly"])
                c.result(True, "Survived! the DI bent the path")


DRILLS = [DefTech, DefAsdiDown, DefDiSurvival, DefTechChase, DefComboShine]
