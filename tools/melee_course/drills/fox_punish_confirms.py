"""Fox's Punish drills that follow a landed hit: fox-aerial-confirm and
fox-shine-knockdown.

Port of src/tmce/events/course/drills/fox_punish_confirms.inc.h (specs:
data/courses/fox.md, Punish 7, 4).
"""
from melee_course.engine import (
    A, B, R, X, Z, Drill, Option, Ref, WAIT, GUARD, GUARD_ON, GUARD_SET_OFF,
    GUARD_REFLECT)
from melee_course.drills.fox_punish import (
    FPR_DISTANCE, cpu_grabbed, dist, is_aerial, is_aerial_landing,
    is_double_jump, is_jump, is_shine, player_grabbed)
from melee_course.drills.fox_punish_throws import (
    ESCAPES, FASTFALLER_DECK, Escape, escape_option)

# fox_neutral_reads.inc.h's distances
ST_START = 45.0
ST_NEAR = 30.0            # the demonstration jumps from here

# ---- fox-aerial-confirm -----------------------------------------------------
#
# Marth stands or crouches (one or the other for the whole attempt). The
# player lands an aerial on him and has to follow it up:
#   - standing, he is in hitstun and then jumps away after his reaction
#     time (Escape.cpu_escape): the next hit or grab has to come first;
#   - crouching, he crouch cancels and shields as soon as he can, so a
#     shine or up smash is blocked and the grab is the follow-up.
# (A croucher who grabs on his first free frame was tried first: he grabs
# Fox out of his landing lag whatever Fox does, which leaves nothing to
# choose. Not landing that aerial at all is fox-approach-nair-dair.)

AC_OPT_STANCE, AC_OPT_PERCENT, AC_OPT_ESCAPE = range(3)
AC_MARK_NEAR, AC_MARK_LAND = 1, 2
AC_APPROACH, AC_FOLLOW = range(2)
AC_TIMEOUT = 90


class FoxAerialConfirm(Drill):
    id = "fox-aerial-confirm"
    name = "Aerial Hit Confirm"
    goal = "Follow a landed aerial before they escape or grab"
    part = "punish"
    cpu = "marth"
    characters = ("fox",)
    options = (
        Option("CPU Stance", ["Random", "Standing", "Crouching"], 0,
               "Whether the CPU stands or crouches (and crouch cancels "
               "your aerial)."),
        Option("CPU Percent", count=151, default=20, fmt="%d%%",
               desc="The CPU's damage at the start of each attempt."),
        escape_option(),
    )
    help = ("Land an aerial, then follow it up before they jump",
            "away, or before they grab you if they crouched.",
            "D-Pad up: guide. D-Pad down: reset.")
    live_marks = True

    def build_reference(self, c):
        """Run in, short hop from ST_NEAR with neutral air (down air on a
        croucher), L-cancel (two presses, as in fox-shield-pressure), and
        shine as the landing lag ends (grab a croucher's shield)."""
        js = c.fd.jump_squat
        crouch = self.v["crouch"]
        return [
            Ref(0, 5, 400, lx=127),
            # let go of the stick from the jump on, or Fox sails past
            Ref(AC_MARK_NEAR, 1, 200, lx=1),
            Ref(AC_MARK_NEAR, 1, 1, buttons=X),
            Ref(AC_MARK_NEAR, 1 + js, 1, cy=-127) if crouch else
            Ref(AC_MARK_NEAR, 1 + js, 1, buttons=A),
            Ref(AC_MARK_NEAR, 1 + js + 16, 1, buttons=Z),
            Ref(AC_MARK_NEAR, 1 + js + 21, 1, buttons=Z),
            # AC_MARK_LAND is announced when the landing lag is over
            Ref(AC_MARK_LAND, 1, 1, buttons=Z) if crouch else
            Ref(AC_MARK_LAND, 1, 1, ly=-127, buttons=B),
        ]

    def guide(self, c):
        return ["An aerial that lands is only the start. What",
                "comes next depends on how they took it:",
                "Standing: they are stunned. Shine, grab or up",
                "  smash before they jump away.",
                "Crouching: they crouch cancel and have their",
                "  shield up at once. Grab.",
                "L-cancel the aerial, or neither works."]

    def setup(self, c):
        stance = c.opt(AC_OPT_STANCE)
        hmn_x = -c.side * ST_START / 2
        c.place(hmn_x, hmn_x + c.side * ST_START, False,
                float(c.opt(AC_OPT_PERCENT)))
        if stance != 0:
            crouch = stance == 2
        elif c.is_demo:
            crouch = (c.demo_count + 1) % 2 == 1      # standing first
        else:
            crouch = c.randi(2) == 1
        self.v = dict(crouch=crouch, frame=0, odd=0)
        th = self.th = Escape()
        th.free = 0
        th.jumped = False
        th.odd = 0
        th.di = 0
        th.react = ESCAPES[1 if c.is_demo else c.opt(AC_OPT_ESCAPE)]

    def think(self, c):
        v, th, me = self.v, self.th, c.me
        if c.cpu is None:
            return
        aerial = is_aerial(me.state) or is_aerial_landing(me.state)

        if dist(c) < ST_NEAR:
            c.mark(AC_MARK_NEAR)
        if is_aerial_landing(c.prev_state) and \
                not is_aerial_landing(c.state):
            c.mark(AC_MARK_LAND)
        c.report("crouch", int(v["crouch"]))

        if c.phase == AC_APPROACH:
            if v["crouch"]:
                c.cpu_press(ly=-127)
            if c.cpu_hit and aerial:
                c.set_phase(AC_FOLLOW)
                v["frame"] = 0
            elif c.cpu_hit or cpu_grabbed(c):
                c.result(False, "Open with an aerial")
        elif c.phase == AC_FOLLOW:
            v["frame"] += 1
            if v["crouch"]:
                c.cpu_shield()    # up as soon as the crouch cancel allows
            else:
                th.cpu_escape(c)
            if player_grabbed(c) or c.hmn_hit:
                c.result(False, "Got hit")
            elif c.cpu_state == GUARD_SET_OFF:
                c.result(False, "Blocked: they crouch cancelled\nand "
                         "shielded. Grab instead")
            elif cpu_grabbed(c) or (c.cpu_hit and not aerial):
                c.measure(v["frame"], v["frame"])
                c.report("frame", v["frame"])
                if is_shine(me.state):
                    c.result(True, "Aerial into shine\n%d frames later"
                             % v["frame"])
                elif cpu_grabbed(c):
                    c.result(True, "Aerial into grab\n%d frames later"
                             % v["frame"])
                else:
                    c.result(True, "Confirmed\n%d frames after the aerial"
                             % v["frame"])
            elif not v["crouch"] and v["frame"] > 6 and (
                    is_double_jump(c.cpu_state) or is_jump(c.cpu_state)):
                c.result(False, "They jumped away\nfollow up sooner")
            elif v["frame"] > AC_TIMEOUT:
                c.result(False, "No follow-up")


# ---- fox-shine-knockdown ----------------------------------------------------
#
# Falco or Fox stands next to the player's Fox; the shine knocks light
# characters off their feet (Captain Falcon, tried first, only slides). As
# he reaches the ground he techs in place, techs away, techs toward Fox, or
# misses the tech and then gets up, rolls or attacks. The player has to hit
# or grab him before he is on his feet and free again (he shields from then
# on). A hit while he lies there counts: that is the jab reset.

KD_TECH_PLACE, KD_TECH_AWAY, KD_TECH_IN, KD_MISS, KD_COUNT = range(5)
KD_OPT_CHOICE = 0
KD_WAIT, KD_FALL, KD_GROUND = range(3)
KD_TIMEOUT = 200
KD_GETUP_WAIT = 25        # frames lying down after a missed tech
KD_NAMES = ("tech in place", "tech away", "tech in", "missed tech")


class FoxShineKnockdown(Drill):
    id = "fox-shine-knockdown"
    name = "Shine Knockdown: Tech Chase"
    goal = "Cover the tech or missed tech after a shine"
    part = "punish"
    cpu = "falco"
    characters = ("fox",)
    deck = FASTFALLER_DECK
    options = (
        Option("CPU Tech", ["Random", "Tech in Place", "Tech Away",
                            "Tech In", "No Tech"], 0,
               "What the CPU does when it hits the ground."),
    )
    help = ("Shine him off his feet, watch where he techs, and",
            "hit or grab him before he is free.",
            "D-Pad up: guide. D-Pad down: reset.")

    def guide(self, c):
        return ["Shine knocks fast fallers off their feet. As",
                "they land they choose: tech in place, tech",
                "away, tech toward you, or no tech at all.",
                "Watch, then cover it: every tech has a moment",
                "at its end where they cannot act.",
                "No tech: hit them as they lie there (a weak",
                "hit stands them up helpless: the jab reset).",
                "Stay close after the shine. Do not guess early."]

    def setup(self, c):
        opt = c.opt(KD_OPT_CHOICE)
        hmn_x = -c.side * (FPR_DISTANCE / 2)
        c.place(hmn_x, hmn_x + c.side * FPR_DISTANCE, False, 30.0)
        choice = opt - 1 if opt > 0 else c.randi(KD_COUNT)
        self.v = dict(choice=choice, frame=0, pressed=False, down=0,
                      # 0 stand, 1 roll away, 2 roll in, 3 attack
                      getup=c.randi(4))

    def think(self, c):
        v = self.v
        if c.cpu is None:
            return
        hit_cpu = c.cpu_hit or cpu_grabbed(c)
        choice = v["choice"]

        if c.phase == KD_WAIT:
            if c.cpu_hit and is_shine(c.me.state):
                c.set_phase(KD_FALL)
                v["frame"] = 0
            elif hit_cpu:
                c.result(False, "Start with the shine")
        elif c.phase == KD_FALL:
            v["frame"] += 1
            # tech: one press as he comes down, with the direction held
            if choice != KD_MISS:
                if choice == KD_TECH_AWAY:
                    c.cpu_press(lx=int(-127 * c.toward))
                elif choice == KD_TECH_IN:
                    c.cpu_press(lx=int(127 * c.toward))
                # he is back on the ground 6 frames after the hit; the press
                # comes after the shine's hitlag and before that
                if not v["pressed"] and v["frame"] >= 5:
                    c.cpu_press(R)
                    v["pressed"] = True
            if hit_cpu and v["frame"] > 2:
                c.result(True, "Hit him before he landed")
            elif v["frame"] > 6 and not c.cpu.airborne:
                c.set_phase(KD_GROUND)
                v["down"] = 0
            elif v["frame"] > KD_TIMEOUT:
                c.retry("No knockdown\nresetting")
        elif c.phase == KD_GROUND:
            v["frame"] += 1
            v["down"] += 1
            if choice == KD_MISS and v["down"] > KD_GETUP_WAIT:
                # get up: stand, roll away, roll in or attack
                if v["getup"] == 0:
                    c.cpu_press(ly=127)
                elif v["getup"] == 1:
                    c.cpu_press(lx=int(-127 * c.toward))
                elif v["getup"] == 2:
                    c.cpu_press(lx=int(127 * c.toward))
                elif v["down"] & 1:
                    c.cpu_press(A)
            # a fresh press from Wait is GuardReflect: kept, or he lets go
            if c.cpu_state in (WAIT, GUARD, GUARD_ON, GUARD_REFLECT):
                c.cpu_shield()
            c.report("choice", choice)
            if c.hmn_hit:
                c.result(False, "Hit by the getup attack")
            elif hit_cpu:
                c.measure(v["frame"], v["frame"])
                c.report("frame", v["frame"])
                c.message("Covered the %s" % KD_NAMES[choice])
                c.result(True, "Tech chase!\n%d frames after the shine"
                         % v["frame"])
            elif c.cpu_state == GUARD_SET_OFF:
                c.message("It was a %s" % KD_NAMES[choice])
                c.result(False, "Blocked\nhe was up and shielding")
            elif v["frame"] > KD_TIMEOUT:
                c.message("It was a %s" % KD_NAMES[choice])
                c.result(False, "No punish")


DRILLS = [FoxShineKnockdown, FoxAerialConfirm]
