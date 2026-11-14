"""Fox's Punish drills after fox-shine-oos: fox-waveshine-usmash,
fox-shield-pressure, fox-oos-choice.

Port of src/tmce/events/course/drills/fox_punish.inc.h (specs:
data/courses/fox.md, Punish). fox-oos-choice reuses the Shine OoS deck
(melee_course.drills.fox_shine_oos). The small helpers the C shares between
drill files (fpr_*, fst_*, nr_*, mv_*) are here, for the three Punish
modules.
"""
from melee_course.engine import (
    A, B, X, R, Z, Drill, Option, Ref, WAIT, GUARD, GUARD_ON, GUARD_SET_OFF,
    JUMP_F, JUMP_B, JUMP_AERIAL_F, JUMP_AERIAL_B, ATTACK_AIR_N, ATTACK_AIR_LW,
    LANDING_AIR_N, LANDING_AIR_LW, ATTACK_HI4, CATCH, CATCH_PULL, CATCH_WAIT,
    CAPTURE_PULLED_HI, FOX_SHINE_FIRST, FOX_SHINE_LAST)
from melee_course.drills.fox_shine_oos import DECK as SHINE_OOS_DECK

# ---- shared with the other Punish modules (the C's fpr_, fst_, nr_, mv_) ----

CAPTURE_FOOT = 232        # ftCo_MS_CaptureFoot: the last of the held states
FPR_DISTANCE = 6.7        # the shine reaches, the grab still reaches after it


def is_shine(state):
    """fst_IsShine: Fox's or Falco's down-B, ground or air."""
    return FOX_SHINE_FIRST <= state <= FOX_SHINE_LAST


def is_jump(state):
    return state in (JUMP_F, JUMP_B)


def is_double_jump(state):
    return state in (JUMP_AERIAL_F, JUMP_AERIAL_B)


def is_aerial(state):
    return ATTACK_AIR_N <= state <= ATTACK_AIR_LW


def is_aerial_landing(state):
    return LANDING_AIR_N <= state <= LANDING_AIR_LW


def cpu_grabbed(c):
    """fpr_CpuGrabbed: the CPU is held (the end-of-frame sample)."""
    return CAPTURE_PULLED_HI <= c.cpu_state <= CAPTURE_FOOT


def player_grabbed(c):
    """nr_PlayerGrabbed."""
    return CAPTURE_PULLED_HI <= c.state <= CAPTURE_FOOT


def dist(c):
    """nr_Dist."""
    return abs(c.cpu.pos[0] - c.me.pos[0])


def place_close(c, percent=0.0):
    """fpr_Place (with the CPU's percent, as the drills that call
    course_Place with FPR_DISTANCE do)."""
    hmn_x = -c.side * (FPR_DISTANCE / 2)
    c.place(hmn_x, hmn_x + c.side * FPR_DISTANCE, False, percent)


# ---- fox-waveshine-usmash ---------------------------------------------------
#
# Marth stands next to Fox. Shine him (at low percent he slides away on his
# feet), jump out of the shine, wavedash after him and up smash. From the
# moment the shine hits, the CPU holds shield: if the up smash is a true
# follow-up it lands, if not it is blocked.

WU_OPT_PERCENT = 0
WU_MARK_HIT = 1
WU_WAIT, WU_COMBO = range(2)
WU_TIMEOUT = 70
# Found with a sweep in the simulator (2026-11-12): jump 6 or 7 frames after
# the down-B, air dodge 3 later at stick (127, -40) of 127, up smash 10 to
# 12 after that. Marth slides 44 units from the shine, so only a long
# wavedash catches him: angles of -30 and -50 both miss.
WU_REF_JUMP = 5           # frames after the hit is seen


class FoxWaveshineUsmash(Drill):
    id = "fox-waveshine-usmash"
    name = "Waveshine to Up Smash"
    goal = "Shine, wavedash after them, up smash before they act"
    part = "punish"
    cpu = "marth"
    characters = ("fox",)
    options = (
        Option("CPU Percent", count=151, default=30, fmt="%d%%",
               desc="The CPU's damage at the start of each attempt."),
    )
    help = ("Shine, wavedash after them, up smash before they",
            "can shield.",
            "D-Pad up: guide. D-Pad down: reset.")
    reference = [
        Ref(0, 10, 1, 0, -127, buttons=B),
        Ref(WU_MARK_HIT, WU_REF_JUMP, 1, buttons=X),
        Ref(WU_MARK_HIT, WU_REF_JUMP + 3, 2, 127, -40, buttons=R,
            trigger=140),
        Ref(WU_MARK_HIT, WU_REF_JUMP + 14, 1, cy=127),
    ]
    live_marks = True

    def guide(self, c):
        return ["Shine pushes a standing opponent away with",
                "enough stun for Fox to catch up and up smash:",
                "his most reliable way to a kill move.",
                "1. Shine.",
                "2. Jump out of it and wavedash toward them,",
                "   nearly flat: they slide a long way.",
                "3. Up smash as the wavedash ends.",
                "They shield as soon as they can: blocked",
                "means the waveshine was too slow."]

    def setup(self, c):
        hmn_x = -c.side * (FPR_DISTANCE / 2)
        c.place(hmn_x, hmn_x + c.side * FPR_DISTANCE, False,
                float(c.opt(WU_OPT_PERCENT)))
        self.v = dict(frame=0)

    def think(self, c):
        v, me = self.v, c.me
        if c.phase == WU_WAIT:
            if c.cpu_hit and is_shine(me.state):
                c.mark(WU_MARK_HIT)
                c.set_phase(WU_COMBO)
                v["frame"] = 0
            elif c.cpu_hit or cpu_grabbed(c):
                c.result(False, "Start with the shine")
        elif c.phase == WU_COMBO:
            v["frame"] += 1
            c.cpu_shield()
            if c.cpu_hit and me.state == ATTACK_HI4:
                c.measure(v["frame"], v["frame"])
                c.report("frame", v["frame"])
                c.result(True, "Waveshine up smash!\n%d frames after the "
                         "shine" % v["frame"])
            elif c.cpu_state == GUARD_SET_OFF:
                c.report("frame", v["frame"])
                c.result(False, "Blocked: %d frames after\nthe shine is too "
                         "slow" % v["frame"])
            elif c.cpu_hit or cpu_grabbed(c):
                c.result(False, "Not the up smash")
            elif v["frame"] > WU_TIMEOUT:
                c.result(False, "No up smash")


# ---- fox-shield-pressure ----------------------------------------------------
#
# Marth shields, and from the first hit on tries to grab out of shield on
# every frame he is free. Each hit on the shield counts; a gap long enough
# for the grab ends the attempt. Hitting him out of the grab's startup is
# the pressure working.

PR_OPT_HITS = 0
PR_MARK_LAND = 1
PR_IDLE = 90              # frames without a hit: the pressure has stopped
PR_HITS = (3, 5, 8)


class FoxShieldPressure(Drill):
    id = "fox-shield-pressure"
    name = "Shield Pressure"
    goal = "Keep hitting a shield without a gap they can grab in"
    part = "punish"
    cpu = "marth"
    characters = ("fox",)
    options = (
        Option("Hits", ["3", "5", "8"], 0,
               "How many hits on the shield in a row count as a success."),
    )
    help = ("Hit the shield again and again without leaving a",
            "gap they can grab you in.",
            "D-Pad up: guide. D-Pad down: reset.")
    # The demonstration: short hop neutral air (L-cancelled: two presses, as
    # the landing moves with the shield's hitlag), shine as the landing lag
    # ends, jump out of the shine and shine again on the first airborne
    # frame.
    reference = [
        Ref(0, 10, 1, buttons=X),
        Ref(0, 25, 1, buttons=A),             # late: hits low
        Ref(0, 30, 1, buttons=Z),
        Ref(0, 35, 1, buttons=Z),
        Ref(PR_MARK_LAND, 6, 1, 0, -127, buttons=B),
        Ref(PR_MARK_LAND, 12, 1, buttons=X),
        Ref(PR_MARK_LAND, 15, 1, 0, -127, buttons=B),
    ]
    live_marks = True

    def guide(self, c):
        return ["A shielding opponent wants one thing: a gap",
                "long enough to grab you (7 frames). Do not",
                "give it.",
                "Aerial low on the shield, L-cancel, shine at",
                "once, jump out of the shine, and again.",
                "If they try to grab and your next hit beats it,",
                "the pressure has done its job."]

    def setup(self, c):
        place_close(c)
        self.v = dict(hits=0, idle=0, in_hitlag=False, frame=0)

    def think(self, c):
        v, cpu = self.v, c.cpu
        want = PR_HITS[c.opt(PR_OPT_HITS)]
        hitlag = cpu.hitlag > 0 and cpu.state == GUARD_SET_OFF

        v["frame"] += 1
        c.cpu_shield()
        if v["hits"] > 0 and v["frame"] & 1:
            c.cpu_press(A)                    # A in shield: grab
        if is_aerial_landing(c.state):
            c.mark(PR_MARK_LAND)

        if hitlag and not v["in_hitlag"]:
            v["hits"] += 1
            v["idle"] = 0
        v["in_hitlag"] = hitlag
        if v["hits"] > 0:
            v["idle"] += 1

        if player_grabbed(c):
            c.measure(v["hits"], want)
            c.report("hits", v["hits"])
            c.result(False, "Shield grabbed after %d hits\nthe gap was too "
                     "long" % v["hits"])
        elif c.hmn_hit:
            c.result(False, "Got hit")
        elif c.cpu_hit:
            c.measure(v["hits"], want)
            c.report("hits", v["hits"])
            c.result(True, "They went for the grab\nand you hit them first")
        elif v["hits"] >= want:
            c.measure(v["hits"], want)
            c.report("hits", v["hits"])
            c.result(True, "%d hits, no gap" % v["hits"])
        elif v["idle"] > PR_IDLE:
            c.measure(v["hits"], want)
            c.report("hits", v["hits"])
            c.result(False, "Pressure stopped after %d hits" % v["hits"])


# ---- fox-oos-choice ---------------------------------------------------------
#
# The Shine OoS scenarios, but from farther away some of the time, so that
# the shine does not always reach. Any hit or grab before the CPU has
# recovered counts, and the verdict names the option and how early it was.
# Once it has recovered the CPU shields.

OC_MARK_STUN_END = 1
OC_WAIT_SHIELD, OC_ATTACK, OC_PUNISH = range(3)
OC_BUSY_MIN = 20
OC_TIMEOUT = 120
OC_CPU_REACT = 4          # frames the CPU takes to shield once it can


def oc_option(state):
    """The verdict for the option that connected."""
    if is_shine(state):
        return "Shine out of shield\nframe %d"
    if state == ATTACK_HI4:
        return "Up smash out of shield\nframe %d"
    if state == ATTACK_AIR_N:
        return "Neutral air out of shield\nframe %d"
    if state in (CATCH, CATCH_PULL, CATCH_WAIT):
        return "Grab out of shield\nframe %d"
    return "Punished out of shield\nframe %d"


class FoxOosChoice(Drill):
    id = "fox-oos-choice"
    name = "Out of Shield: Pick the Option"
    goal = "Punish a shielded move with whatever reaches in time"
    part = "punish"
    cpu = "marth"
    characters = ("fox",)
    deck = SHINE_OOS_DECK
    help = ("Shield the attack, then punish with whatever",
            "reaches in time: shine, up smash, nair or grab.",
            "D-Pad up: guide. D-Pad down: reset.")
    # Hold shield; jump the frame after shieldstun is seen to end and shine
    # as Fox leaves the ground: a frame later than perfect, which the CPU's
    # reaction time allows. (Placing the jump on the exact frame needs the
    # observing pass of fox-shine-oos; tried here, it went wrong against
    # the multi-hit aerials.)
    reference = [
        Ref(0, 0, 600, buttons=R, trigger=140),
        Ref(OC_MARK_STUN_END, 1, 1, buttons=X),
        Ref(OC_MARK_STUN_END, 4, 1, 0, -127, buttons=B),
    ]
    live_marks = True

    def guide(self, c):
        fd = c.fd
        return ["Out of shield, the right answer depends on how",
                "far away they end up and how long they are stuck.",
                "Shine: frame %d, but only when they are touching."
                % (fd.jump_squat + 1),
                "Up smash: frame %d, reaches further."
                % (fd.jump_squat + fd.move["usmash"].hit),
                "Neutral air: frame %d, reaches in front."
                % (fd.jump_squat + fd.move["nair"].hit),
                "Grab: frame %d, only close and in front."
                % fd.move["grab"].hit,
                "Wavedash out when nothing reaches in time."]

    def setup(self, c):
        sc = c.entry.data
        hmn_x = -c.side * 10.0
        # the demonstration shines, so it gets the shine's spacing
        extra = 0.0 if c.is_demo else 4.0 * c.randi(3)
        c.place(hmn_x, hmn_x + c.side * (sc.distance + extra), sc.face_away,
                20.0)
        self.v = dict(delay=10 + c.randi(30), attack_frame=0, stun_end=-1,
                      cpu_free=False, free_frames=0, extra=extra)

    def think(self, c):
        v, me = self.v, c.me
        sc = c.entry.data
        c.set_shield(c.s.person, 60.0)   # the player's shield does not shrink
        if c.phase >= OC_ATTACK:
            if not v["cpu_free"]:
                c.script(sc.inputs, v["attack_frame"])
            else:
                c.cpu_shield()
            v["attack_frame"] += 1
            # it shields a few frames after it can: nobody is frame perfect
            if v["attack_frame"] > OC_BUSY_MIN and c.cpu_state == WAIT:
                v["free_frames"] += 1
                if v["free_frames"] > OC_CPU_REACT:
                    v["cpu_free"] = True

        if c.phase == OC_WAIT_SHIELD:
            if me.state in (GUARD, GUARD_ON):
                if c.timer >= v["delay"]:
                    c.set_phase(OC_ATTACK)
                    v["attack_frame"] = 0
            else:
                c.timer = 0
        elif c.phase == OC_ATTACK:
            if me.state == GUARD_SET_OFF:
                c.set_phase(OC_PUNISH)
            elif c.hmn_hit:
                c.result(False, "Hit through your shield")
            elif c.timer > sc.attack_timeout + 30:
                c.retry("Attack missed\nresetting")
        elif c.phase == OC_PUNISH:
            if v["stun_end"] < 0 and me.state != GUARD_SET_OFF:
                # shieldstun ends with the animation: during the last frame
                # (see Ctx.mark), which is when the C drill sees it
                v["stun_end"] = v["attack_frame"] - 1
                c.mark(OC_MARK_STUN_END, back=1)
            if c.hmn_hit or player_grabbed(c):
                c.result(False, "Got hit")
            elif c.cpu_hit or cpu_grabbed(c):
                frame = v["attack_frame"] - v["stun_end"] \
                    if v["stun_end"] >= 0 else 0
                c.measure(frame, frame)
                c.report("frame", frame)
                c.report("extra", round(v["extra"], 1))
                c.result(True, oc_option(me.state) % frame)
            elif c.cpu_state == GUARD_SET_OFF:
                c.result(False, "Too slow: blocked\npick a faster option")
            elif c.timer > OC_TIMEOUT:
                c.result(False, "No punish")


DRILLS = [FoxOosChoice, FoxWaveshineUsmash, FoxShieldPressure]
