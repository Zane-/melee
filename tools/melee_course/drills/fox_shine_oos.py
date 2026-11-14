"""fox-shine-oos: punish a move on shield with shine out of shield.

Port of src/tmce/events/course/drills/fox_shine_oos.inc.h (spec:
data/courses/fox.md, Punish 1), with the Shine OoS event's deck
(src/tmce/events/shineoos/desc.c).

The CPU (a scenario of the deck: a character, an attack, a spacing)
attacks once the player holds shield. The player jumps out of shield and
shines on the first airborne frame; optionally follows up.
"""
from melee_course.engine import (
    A, B, X, R, Drill, Entry, In, Option, Ref, ESCAPE_AIR,
    LANDING_FALL_SPECIAL, ATTACK_HI4, GUARD, GUARD_ON, GUARD_SET_OFF,
    FOX_SHINE_FIRST, FOX_SHINE_LAST)

TOWARD, AWAY = 127, -127

# The deck: Shine OoS's scenarios (src/tmce/events/shineoos/desc.c).
_dtilt = [In(0, 1, 0, -80, 0, 0, A)]
_utilt = [In(0, 1, 0, 80, 0, 0, A)]
_fsmash = [In(0, 1, 0, 0, TOWARD, 0)]
_marth_fair = [In(0, 1, buttons=X), In(5, 30, TOWARD), In(24, 1, TOWARD, 0, TOWARD),
               In(38, 1, buttons=R)]
_falcon_nair = [In(0, 1, buttons=X), In(5, 30, TOWARD), In(20, 1, TOWARD, buttons=A),
                In(33, 1, buttons=R)]
_falco_dair = [In(0, 1, buttons=X), In(6, 20, TOWARD), In(14, 1, TOWARD, 0, 0, -127),
               In(27, 1, buttons=R)]
_puff_bair = [In(0, 1, buttons=X), In(6, 6, TOWARD), In(12, 1, 0, 0, AWAY, 0),
              In(36, 1, buttons=R)]


class Oos:
    """OosScenario: start distance, the attack, frames to wait for the
    shield hit, faces away at the start, frame advantage on Fox's shield."""

    def __init__(self, distance, inputs, attack_timeout, face_away, advantage):
        self.distance, self.inputs = distance, inputs
        self.attack_timeout, self.face_away = attack_timeout, face_away
        self.advantage = advantage


DECK = [
    Entry("marth", Oos(6.0, _dtilt, 40, 0, -6), "Marth - Down Tilt"),
    Entry("marth", Oos(4.0, _fsmash, 40, 0, -27), "Marth - Forward Smash"),
    Entry("marth", Oos(26.0, _marth_fair, 60, 0, -4), "Marth - Fair (early)"),
    Entry("sheik", Oos(6.0, _utilt, 40, 0, -15), "Sheik - Up Tilt"),
    Entry("captain-falcon", Oos(5.0, _dtilt, 40, 0, -17), "Falcon - Down Tilt"),
    Entry("captain-falcon", Oos(30.0, _falcon_nair, 60, 0, -4),
          "Falcon - Nair (early)"),
    Entry("peach", Oos(5.0, _dtilt, 40, 0, -6), "Peach - Down Tilt"),
    Entry("falco", Oos(20.0, _falco_dair, 60, 0, -4), "Falco - Dair (early)"),
    Entry("jigglypuff", Oos(22.0, _puff_bair, 60, 1, -4),
          "Jigglypuff - Bair (early)"),
]

SHINE_STARTUP = 1          # the shine's hitbox is out on its first frame
PUNISH_TIMEOUT = 60
FOLLOWUP_TIMEOUT = 90
MARK_STUN_END = 1
WAIT_SHIELD, ATTACK, PUNISH, FOLLOWUP = range(4)
OPT_SUCCESS, OPT_DELAY, OPT_PERCENT = range(3)
GOAL_SHINE, GOAL_ANY_HIT, GOAL_USMASH, GOAL_WAVESHINE_USMASH = range(4)
DELAY_RANDOM, DELAY_SHORT, DELAY_LONG = range(3)


def is_shine(f):
    return f.kind in (1, 22) and FOX_SHINE_FIRST <= f.state <= FOX_SHINE_LAST


class FoxShineOos(Drill):
    id = "fox-shine-oos"
    name = "Shine Out of Shield"
    goal = "Punish a shielded move with a frame 4 shine."
    part = "punish"
    characters = ("fox", "falco")
    deck = DECK
    options = (
        Option("Success", ["Shine Hits", "Shine + Any Hit",
                           "Shine + Up Smash", "Waveshine Up Smash"], 0,
               "What counts as a success: the shine hitting, or the shine "
               "and a follow-up."),
        Option("Attack Delay", ["Random", "Short", "Long"], 0,
               "How long the CPU waits after you shield."),
        Option("CPU Percent", count=151, default=20, fmt="%d%%",
               desc="The CPU's damage at the start of each attempt."),
    )
    help = ("Hold shield. When the attack hits your shield, jump out",
            "of shield and shine on the first frame of the jump.",
            "D-Pad left/right: change scenario. D-Pad down: reset.")
    # Hold shield; jump on the frame shieldstun is seen to end; down-B 3
    # frames later (Fox's jump squat), his first airborne frame.
    reference = [
        Ref(0, 0, 600, buttons=R, trigger=140),
        Ref(MARK_STUN_END, 0, 1, buttons=X),
        Ref(MARK_STUN_END, 3, 1, 0, -127, buttons=B),
    ]

    def perfect(self, c):
        return c.fd.jump_squat + SHINE_STARTUP

    def guide(self, c):
        sc = c.entry.data if c.entry else None
        lines = ["Punish a move that hit your shield before the",
                 "opponent can act again.",
                 "1. Hold shield and take the hit.",
                 "2. Jump the moment shieldstun ends.",
                 "3. Down+B on your first airborne frame (%d after the "
                 "jump)." % c.fd.jump_squat,
                 "Perfect: shine on out-of-shield frame %d."
                 % self.perfect(c)]
        if sc is not None:
            lines.append("%s leaves you %d frames to start."
                         % (c.entry.name, -sc.advantage))
        return lines

    def setup(self, c):
        sc = c.entry.data
        hmn_x = -c.side * 10.0
        cpu_x = hmn_x + c.side * sc.distance
        c.place(hmn_x, cpu_x, sc.face_away, float(c.opt(OPT_PERCENT)))
        delay = c.opt(OPT_DELAY)
        self.v = dict(
            delay=10 if delay == DELAY_SHORT else 40 if delay == DELAY_LONG
            else 8 + c.randi(40),
            attack_frame=0, stun_end=-1, shine_frame=-1, wavedash=False,
            distance=0.0)

    def oos_frame(self):
        return self.v["shine_frame"] - self.v["stun_end"]

    def finish(self, c, success, words):
        v = self.v
        oos = self.oos_frame() if v["shine_frame"] >= 0 and \
            v["stun_end"] >= 0 else -1
        if oos >= 0:
            c.measure(oos, self.perfect(c))
        c.report("shield_hit", int(c.phase >= PUNISH))
        c.report("stun_end", v["stun_end"])
        c.report("shine", v["shine_frame"])
        c.report("oos_frame", oos)
        c.report("distance", round(v["distance"], 1))
        c.result(success, words)

    def think(self, c):
        v, me, cpu = self.v, c.me, c.cpu
        sc = c.entry.data
        c.set_shield(c.s.person, 60.0)
        if c.phase >= ATTACK:
            c.script(sc.inputs, v["attack_frame"])
            v["attack_frame"] += 1
        if c.phase == WAIT_SHIELD:
            if me.state in (GUARD, GUARD_ON):
                if c.timer >= v["delay"]:
                    c.set_phase(ATTACK)
                    v["attack_frame"] = 0
            else:
                c.timer = 0
        elif c.phase == ATTACK:
            if me.state == GUARD_SET_OFF:
                c.set_phase(PUNISH)
            elif c.hmn_hit:
                self.finish(c, False, "Hit through your shield")
            elif c.timer > sc.attack_timeout:
                c.retry("Attack missed\nresetting")
        elif c.phase == PUNISH:
            if v["stun_end"] < 0 and me.state != GUARD_SET_OFF:
                # shieldstun ends with the animation: during the last
                # frame (see Ctx.mark), which is when the C drill sees it
                v["stun_end"] = v["attack_frame"] - 1
                v["distance"] = abs(cpu.pos[0] - me.pos[0])
                c.mark(MARK_STUN_END, back=1)
            if v["shine_frame"] < 0 and is_shine(me):
                v["shine_frame"] = v["attack_frame"]
            if c.hmn_hit:
                self.finish(c, False, "Got hit")
            elif c.cpu_hit and is_shine(me):
                if c.opt(OPT_SUCCESS) == GOAL_SHINE:
                    self.finish(c, True, "Shine OoS! frame %d"
                                % self.oos_frame())
                else:
                    c.set_phase(FOLLOWUP)
                    c.message("Shine on frame %d, follow up!"
                              % self.oos_frame())
            elif c.cpu_hit:
                self.finish(c, False, "Hit, but not with the shine")
            elif c.timer > PUNISH_TIMEOUT:
                if v["shine_frame"] >= 0:
                    self.finish(c, False, "Shine missed: frame %d"
                                % self.oos_frame())
                else:
                    self.finish(c, False, "No shine")
        elif c.phase == FOLLOWUP:
            goal = c.opt(OPT_SUCCESS)
            if me.state in (ESCAPE_AIR, LANDING_FALL_SPECIAL):
                v["wavedash"] = True
            if c.hmn_hit:
                self.finish(c, False, "Got hit")
            elif c.cpu_hit and not is_shine(me):
                usmash = me.state == ATTACK_HI4
                if goal == GOAL_ANY_HIT or (goal == GOAL_USMASH and usmash) \
                        or (goal == GOAL_WAVESHINE_USMASH and usmash and
                            v["wavedash"]):
                    self.finish(c, True, "Punished!")
                elif goal == GOAL_WAVESHINE_USMASH and usmash:
                    self.finish(c, False, "Up smash, but no waveshine")
                else:
                    self.finish(c, False, "Wrong follow-up")
            elif c.timer > FOLLOWUP_TIMEOUT:
                self.finish(c, False, "No follow-up")


DRILLS = [FoxShineOos]
