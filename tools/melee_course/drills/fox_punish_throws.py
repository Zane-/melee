"""Fox's Punish drills that start from a grab or end in a kill:
fox-uthrow-uair, fox-uthrow-chaingrab, fox-kill-confirm.

Port of src/tmce/events/course/drills/fox_punish_throws.inc.h (specs:
data/courses/fox.md, Punish 5, 6, 11; the chain grab changed natively, see
its section), with the Floaty, FastFaller and
KillConfirm decks of src/tmce/events/course/desc.c.

The CPU stands in grab range. Once thrown or hit it holds a DI direction
(random each time) and presses jump every other frame, so it leaves on the
first frame it can: a follow-up that is not true does not land.
"""
from melee_course.engine import (
    A, X, Z, Drill, Entry, Option, Ref, WAIT, DEAD_LAST, THROW_F, THROW_HI,
    THROW_LW, CAPTURE_PULLED_HI, ATTACK_AIR_HI, ATTACK_HI3, ATTACK_DASH)
from melee_course.drills.fox_punish import (
    FPR_DISTANCE, cpu_grabbed, is_double_jump, is_jump, is_shine)

THROWN_LW_WOMEN = 243     # ftCo_MS_ThrownlwWomen: the last of the held/thrown

# ---- decks (desc.c) ---------------------------------------------------------

FLOATY_DECK = [
    Entry("marth", None, "Marth"),
    Entry("sheik", None, "Sheik"),
    Entry("peach", None, "Peach"),
    Entry("jigglypuff", None, "Jigglypuff"),
]
# The C's Fox is in costume 1 (the player is Fox too); the native build's
# match has no costumes.
FASTFALLER_DECK = [
    Entry("falco", None, "Falco"),
    Entry("fox", None, "Fox"),
]
KILLCONFIRM_DECK = [
    Entry("marth", None, "Marth"),
    Entry("sheik", None, "Sheik"),
    Entry("jigglypuff", None, "Jigglypuff"),
]

# ---- the opponent getting away (th_*) ---------------------------------------


def is_throw(state):
    return THROW_F <= state <= THROW_LW


def cpu_dead(c):
    return c.cpu.state <= DEAD_LAST


def cpu_escaped(c):
    """The CPU got away: it double jumped, or it is back on the ground
    (standing, or lying there: a downed opponent cannot be grabbed)."""
    return is_double_jump(c.cpu_state) or not c.cpu.airborne


# How long after it could first act the CPU jumps away. Instant is what a
# perfect opponent does; measured in the simulator, up throw up air on
# Marth does not land against that at any percent from 60 to 130, which is
# the real game: it works on the opponent's reaction.
ESCAPES = (20, 12, 6, 0)


def escape_option():
    return Option("CPU Escape", ["Slow (20)", "Normal (12)", "Fast (6)",
                                 "Instant"], 1,
                  "Frames after it can first act before the CPU jumps away.")


class Escape:
    """The C's `th`: the CPU's DI and its jump away."""

    def __init__(self):
        self.di = 0       # stick X the CPU holds, -127, 0 or 127 (toward +)
        self.frame = 0    # frames since the throw or first hit
        self.odd = 0
        self.free = 0     # frames the CPU has been able to act
        self.react = 0    # frames it waits before jumping
        self.jumped = False   # it has jumped away since it was last stuck

    def pick_di(self, c):
        self.di = 0 if c.is_demo else (c.randi(3) - 1) * 127

    def cpu_escape(self, c):
        """DI, and jump once it has been able to for `react` frames."""
        cpu = c.cpu
        stuck = cpu.hitstun > 0 or \
            CAPTURE_PULLED_HI <= cpu.state <= THROWN_LW_WOMEN
        # DI only matters while it is stuck; held afterwards it would walk
        # or drift the CPU off the stage (it did, and "killed" Marth). One
        # jump away, then it stays where it lands.
        if stuck:
            c.cpu_press(lx=int(self.di * c.toward))
            self.free = 0
            self.jumped = False
            return
        self.free += 1
        if is_double_jump(cpu.state) or is_jump(cpu.state):
            self.jumped = True
        if not self.jumped and self.free > self.react:
            self.odd ^= 1
            if self.odd:
                c.cpu_press(X)

    def place(self, c, percent, escape_option):
        """th_Place: `escape_option` is the drill's option index, None for a
        true combo (the CPU acts as soon as it can)."""
        self.free = 0
        # demonstrations are shown against the Normal reaction
        if escape_option is None:
            self.react = 0
        else:
            self.react = ESCAPES[1 if c.is_demo else c.opt(escape_option)]
        hmn_x = -c.side * (FPR_DISTANCE / 2)
        c.place(hmn_x, hmn_x + c.side * FPR_DISTANCE, False, percent)
        self.frame = 0
        self.odd = 0
        self.jumped = False
        self.pick_di(c)


# Marks shared by the drills' demonstrations: the grab, the end of the throw
# animation, the opponent in reach, the jump nearly spent.
TH_MARK_APEX = 4
UA_REACH_X = 12.0


def mark_reach(c, mark):
    """For the demonstrations: the opponent is in reach of an up air."""
    me, cpu = c.me, c.cpu
    dx = abs(cpu.pos[0] - me.pos[0])
    dy = cpu.pos[1] - me.pos[1]
    if not me.airborne:
        return
    if dx < UA_REACH_X and dy < 30.0:
        c.mark(mark)
    elif me.vel[1] < 0.6 and me.pos[1] > 15.0:
        # the first jump is nearly spent and they are still too high
        c.mark(TH_MARK_APEX)


# ---- fox-uthrow-uair --------------------------------------------------------

UA_OPT_PERCENT, UA_OPT_ESCAPE = range(2)
UA_MARK_GRAB, UA_MARK_RELEASE, UA_MARK_REACH, UA_MARK_APEX = 1, 2, 3, 4
UA_WAIT, UA_THROW, UA_CHASE = range(3)
UA_TIMEOUT = 120
# Grab, up throw, full hop as Fox comes out of the throw and up air. The
# demonstration's CPU does not DI. Against DI the player has to dash under
# the opponent first: with Marth at 90% and full DI away, a 6-frame dash,
# jump and up air 8 frames later connects 23 frames after the throw
# animation ends, and he can first act on frame 21 (simulator sweeps,
# 2026-11-12).
UA_REF_JUMP = 1


class FoxUthrowUair(Drill):
    id = "fox-uthrow-uair"
    name = "Up Throw Up Air"
    goal = "Up air them out of up throw before they jump away"
    part = "punish"
    cpu = "marth"
    characters = ("fox",)
    deck = FLOATY_DECK
    options = (
        Option("CPU Percent", count=151, default=90, fmt="%d%%",
               desc="The CPU's damage at the start of each attempt."),
        escape_option(),
    )
    help = ("Grab, up throw, jump after them and up air before",
            "they can jump away.",
            "D-Pad up: guide. D-Pad down: reset.")
    # The up air is pressed at the UA_MARK_REACH mark (mark_reach).
    reference = [
        Ref(0, 10, 1, buttons=Z),
        Ref(UA_MARK_GRAB, 6, 2, 0, 127),
        Ref(UA_MARK_RELEASE, UA_REF_JUMP, 8, buttons=X),
        Ref(UA_MARK_APEX, 1, 2, buttons=X),          # double jump
        Ref(UA_MARK_REACH, 1, 1, cy=127),
    ]
    live_marks = True

    def guide(self, c):
        return ["Fox's up throw sends them straight up, and his",
                "up air kills off the top. Together they are",
                "his kill from a grab on floaty characters.",
                "1. Grab, then stick up.",
                "2. They drift left or right (DI): dash under",
                "   them first, then jump.",
                "3. Up air before they jump away. A perfect",
                "   opponent always can: this works on reaction."]

    def setup(self, c):
        self.th = Escape()
        self.th.place(c, float(c.opt(UA_OPT_PERCENT)), UA_OPT_ESCAPE)

    def think(self, c):
        th = self.th
        if c.cpu is None:
            return
        if cpu_grabbed(c):
            c.mark(UA_MARK_GRAB)
        if c.phase == UA_WAIT:
            if c.state == THROW_HI:
                c.set_phase(UA_THROW)
            elif is_throw(c.state):
                c.result(False, "Use the up throw")
            elif c.cpu_hit:
                c.result(False, "Start with a grab")
        elif c.phase == UA_THROW:
            th.cpu_escape(c)
            if c.state != THROW_HI:
                c.mark(UA_MARK_RELEASE)
                c.set_phase(UA_CHASE)
                th.frame = 0
        elif c.phase == UA_CHASE:
            th.frame += 1
            th.cpu_escape(c)
            mark_reach(c, UA_MARK_REACH)
            if c.cpu_hit and c.me.state == ATTACK_AIR_HI:
                c.measure(th.frame, th.frame)
                c.report("frame", th.frame)
                c.report("di", th.di)
                c.result(True, "Up throw up air!\n%d frames after the throw"
                         % th.frame)
            elif c.cpu_hit:
                c.result(False, "Hit, but not with up air")
            elif th.frame > 4 and cpu_escaped(c):
                c.report("frame", th.frame)
                c.report("di", th.di)
                c.result(False, "They got away after %d frames\njump and up "
                         "air sooner" % th.frame)
            elif th.frame > UA_TIMEOUT:
                c.result(False, "No up air")


# ---- fox-uthrow-chaingrab ---------------------------------------------------
#
# The chain goes on until the player drops it (the owner, 2026-11-13: "Chain
# grab training should go until the player drops their combo (don't reset on
# one throw, let them cook! we should even let them tech chase, if they miss
# the follow up though reset)"). Any throw, regrab or hit keeps it going. The
# CPU DIs while it is stuck, techs (in place, away, in) or misses the tech
# when it comes down in tumble, gets up, rolls or attacks from the floor, and
# jumps away as soon as it is free: a regrab that is not true does not land.
# Free for CG_AWAY frames, a double jump, or the player hit by its getup
# attack ends the chain; the attempt says how long it was.

CG_OPT_PERCENT, CG_OPT_COUNT = range(2)
CG_MARK_GRAB, CG_MARK_RELEASE = 1, 2
CG_WAIT, CG_HELD, CG_THROW, CG_CHASE = range(4)
CG_COUNTS = (1, 2, 3, 5)
CG_REF_GRAB = 5           # from a sweep in the simulator
CG_AWAY = 10              # frames free: it has jumped and is away
CG_TIMEOUT = 400          # frames in one chase with nothing happening
CG_GETUP_WAIT = 20        # frames lying down after a missed tech
CG_TECH_HEIGHT = 12.0     # the tech is pressed when this close to the floor
CG_TECHS = ("tech in place", "tech away", "tech in", "missed tech")
CG_PLACE, CG_AWAY_TECH, CG_IN, CG_MISS = range(4)
DOWN_BOUND_U, DOWN_SPOT_D = 183, 198
DOWN_WAITS = (184, 192)   # DownWaitU, DownWaitD
PASSIVE, PASSIVE_STAND_B = 199, 201
DAMAGE_FALL = 38
DAMAGE_FLY_HI, DAMAGE_FLY_ROLL = 87, 91
R = 0x20


def _downed(state):
    return DOWN_BOUND_U <= state <= DOWN_SPOT_D or \
        PASSIVE <= state <= PASSIVE_STAND_B


class FoxUthrowChaingrab(Drill):
    id = "fox-uthrow-chaingrab"
    name = "Chain Grab Fastfallers"
    goal = "Regrab Fox and Falco until you drop it"
    part = "punish"
    cpu = "falco"
    characters = ("fox",)
    deck = FASTFALLER_DECK
    options = (
        Option("CPU Percent", count=151, default=20, fmt="%d%%",
               desc="The CPU's damage at the start of each attempt."),
        Option("Count From", ["1", "2", "3", "5"], 0,
               "Regrabs that make a chain a success. It goes on until "
               "you drop it either way."),
    )
    help = ("Grab, up throw, and grab them again as they land;",
            "keep going. Tech chase them when they hit the floor.",
            "D-Pad up: guide. D-Pad down: reset.")
    # Grab, up throw, grab again.
    reference = [
        Ref(0, 10, 1, buttons=Z),
        Ref(CG_MARK_GRAB, 6, 2, 0, 127),
        Ref(CG_MARK_RELEASE, CG_REF_GRAB, 1, buttons=Z),
    ]
    live_marks = True

    def guide(self, c):
        return ["Fox and Falco fall so fast that an up throw",
                "puts them back on the ground before they can",
                "act. Grab them again as they land, and again.",
                "1. Grab, then stick up.",
                "2. Watch which way they drift (DI) and move",
                "   under them. Turn round if they go behind.",
                "3. Grab just before they would be free.",
                "As their percent climbs they land in tumble:",
                "watch the tech (in place, away, in, or none)",
                "and grab them as they get up. The chain goes on",
                "until they get away."]

    def setup(self, c):
        self.th = Escape()
        self.th.place(c, float(c.opt(CG_OPT_PERCENT)), None)
        self.v = dict(regrabs=0, hits=0, free=0, frame=0, pressed=False,
                      down=0, tech=c.randi(4), getup=c.randi(4), techs=[])

    def end(self, c, why):
        v = self.v
        want = CG_COUNTS[c.opt(CG_OPT_COUNT)]
        regrabs = v["regrabs"]
        c.measure(regrabs, want)
        c.report("regrabs", regrabs)
        c.report("hits", v["hits"])
        c.report("di", self.th.di)
        chain = "%d regrab%s" % (regrabs, "" if regrabs == 1 else "s")
        if v["hits"]:
            chain += ", %d hit%s" % (v["hits"], "" if v["hits"] == 1 else "s")
        if v["techs"]:
            c.message("Tech chased: " + ", ".join(v["techs"]))
        if regrabs >= want:
            c.result(True, "Chain grab! %s\n%s" % (chain, why))
        else:
            c.result(False, "%s\n%s" % (chain.capitalize(), why))

    def _cpu(self, c):
        """The CPU getting away: DI while stuck, the tech as it comes down
        in tumble, a getup from the floor, a jump as soon as it is free."""
        th, v, cpu = self.th, self.v, c.cpu
        st = c.cpu_state
        if cpu.airborne and (st == DAMAGE_FALL or
                             DAMAGE_FLY_HI <= st <= DAMAGE_FLY_ROLL):
            # a tumble: the tech, once, near the floor and falling
            if v["tech"] != CG_MISS:
                if v["tech"] == CG_AWAY_TECH:
                    c.cpu_press(lx=int(-127 * c.toward))
                elif v["tech"] == CG_IN:
                    c.cpu_press(lx=int(127 * c.toward))
                if not v["pressed"] and cpu.vel[1] < 0 and \
                        cpu.pos[1] < CG_TECH_HEIGHT:
                    c.cpu_press(R)
                    v["pressed"] = True
        if _downed(st):
            v["free"] = 0
            if st in DOWN_WAITS:
                v["down"] += 1
                if v["down"] > CG_GETUP_WAIT:
                    # stand, roll away, roll in, or the getup attack
                    if v["getup"] == 0:
                        c.cpu_press(ly=127)
                    elif v["getup"] == 1:
                        c.cpu_press(lx=int(-127 * c.toward))
                    elif v["getup"] == 2:
                        c.cpu_press(lx=int(127 * c.toward))
                    elif v["down"] & 1:
                        c.cpu_press(A)
            return
        stuck = cpu.hitstun > 0 or \
            CAPTURE_PULLED_HI <= st <= THROWN_LW_WOMEN
        th.cpu_escape(c)          # DI while stuck; the jump once free
        v["free"] = 0 if stuck else v["free"] + 1

    def think(self, c):
        th, v = self.th, self.v
        if c.cpu is None:
            return
        if c.phase == CG_WAIT:
            if cpu_grabbed(c):
                c.mark(CG_MARK_GRAB)
                c.set_phase(CG_HELD)
            elif c.cpu_hit:
                c.result(False, "Start with a grab")
        elif c.phase == CG_HELD:
            if is_throw(c.state):
                c.set_phase(CG_THROW)
                th.pick_di(c)
                v["pressed"] = False
                v["down"] = 0
                v["tech"] = c.randi(4)
                v["getup"] = c.randi(4)
            elif not cpu_grabbed(c) and c.timer > 3:
                self.end(c, "Dropped: they broke out of the grab")
        elif c.phase == CG_THROW:
            th.cpu_escape(c)
            if not is_throw(c.state):
                c.mark(CG_MARK_RELEASE)
                c.set_phase(CG_CHASE)
                th.frame = 0
                v["free"] = 0
        elif c.phase == CG_CHASE:
            th.frame += 1
            self._cpu(c)
            st = c.cpu_state
            if PASSIVE <= st <= PASSIVE_STAND_B and v["pressed"] and \
                    CG_TECHS[v["tech"]] not in v["techs"][-1:]:
                v["techs"].append(CG_TECHS[v["tech"]])
            elif DOWN_BOUND_U <= st <= DOWN_SPOT_D and v["tech"] == CG_MISS \
                    and "missed tech" not in v["techs"][-1:]:
                v["techs"].append("missed tech")
            if cpu_grabbed(c):
                v["regrabs"] += 1
                c.set_phase(CG_HELD)
            elif c.cpu_hit:
                v["hits"] += 1
                v["free"] = 0
                th.frame = 0
            elif c.hmn_hit:
                self.end(c, "Dropped: hit by their getup attack")
            elif is_double_jump(st):
                self.end(c, "Dropped: they jumped away")
            elif v["free"] >= CG_AWAY:
                self.end(c, "Dropped: they were free")
            elif th.frame > CG_TIMEOUT:
                self.end(c, "Dropped")


# ---- fox-kill-confirm -------------------------------------------------------

KC_OPT_PERCENT, KC_OPT_ESCAPE = range(2)
KC_MARK_GRAB, KC_MARK_RELEASE = 1, 2
KC_WAIT, KC_COMBO = range(2)
KC_TIMEOUT = 300


class FoxKillConfirm(Drill):
    id = "fox-kill-confirm"
    name = "Kill Confirms"
    goal = "Turn an opening into the stock at kill percent"
    part = "punish"
    cpu = "marth"
    characters = ("fox",)
    deck = KILLCONFIRM_DECK
    options = (
        Option("CPU Percent", count=201, default=110, fmt="%d%%",
               desc="The CPU's damage at the start of each attempt."),
        escape_option(),
    )
    help = ("They are at kill percent: turn the opening into",
            "the stock.",
            "D-Pad up: guide. D-Pad down: reset.")
    # No demonstration: the up throw up air one was tried and only killed
    # Marth at 150%; which route kills depends on the character and the
    # percent, which is the drill.

    def guide(self, c):
        return ["At kill percent every opening should end the",
                "stock. Fox's routes to his kill moves:",
                "Grab, up throw, up air (floaty characters).",
                "Shine, wavedash, up smash.",
                "Up tilt or dash attack, then up smash.",
                "They DI, and jump away a moment after they",
                "can (CPU Escape in the menu)."]

    def setup(self, c):
        self.th = Escape()
        self.th.place(c, float(c.opt(KC_OPT_PERCENT)), KC_OPT_ESCAPE)
        self.v = dict(hits=0, thrown=False)

    def think(self, c):
        th, v = self.th, self.v
        if c.cpu is None:
            return
        if cpu_grabbed(c):
            c.mark(KC_MARK_GRAB)
        if c.phase == KC_WAIT:
            st = c.me.state
            if cpu_grabbed(c) or (c.cpu_hit and (
                    is_shine(st) or st in (ATTACK_HI3, ATTACK_DASH))):
                c.set_phase(KC_COMBO)
                th.frame = 0
                v["hits"] = 0
                v["thrown"] = False
            elif c.cpu_hit:
                # a kill move on a standing dummy is not a confirm
                c.result(False, "Open with a grab, shine,\nup tilt or dash "
                         "attack")
        elif c.phase == KC_COMBO:
            th.frame += 1
            th.cpu_escape(c)
            if c.state == THROW_HI:
                th.frame = 0      # the clock starts when the throw lets go
                v["thrown"] = True
            elif v["thrown"]:
                c.mark(KC_MARK_RELEASE)
            mark_reach(c, UA_MARK_REACH)
            if c.cpu_hit and not is_throw(c.state):
                v["hits"] += 1
            if cpu_dead(c):
                c.measure(th.frame, th.frame)
                c.report("frame", th.frame)
                c.report("hits", v["hits"])
                c.result(True, "Stock taken!\n%d frames after the opening"
                         % th.frame)
            elif th.frame > 30 and c.cpu_state == WAIT and \
                    not cpu_grabbed(c):
                c.report("hits", v["hits"])
                c.result(False, "They survived\nand are back on the ground")
            elif th.frame > KC_TIMEOUT:
                c.result(False, "No kill")


DRILLS = [FoxUthrowUair, FoxUthrowChaingrab, FoxKillConfirm]
