"""Fox's Neutral drills, second file: fox-approach-nair-dair,
fox-vs-crouch-cancel, fox-running-shine, fox-laser-forcing,
fox-shield-then-punish.

Port of src/tmce/events/course/drills/fox_neutral_reads.inc.h (specs:
data/courses/fox.md, Neutral), with CrouchCancel_Deck from
src/tmce/events/course/desc.c; fox-shield-then-punish uses
WavedashBack_Deck (fox_neutral.py).
"""
from melee_course.engine import (
    A, B, R, X, Z, Drill, Entry, In, Option, Ref, ATTACK_AIR_LW,
    CAPTURE_PULLED_HI, FOX_SHINE_FIRST, FOX_SHINE_LAST, GUARD_SET_OFF,
    LANDING_AIR_LW, WAIT)
from melee_course.drills.fox_neutral import (
    AP_WAIT_MIN, AP_WAIT_SPAN, CAPTURE_FOOT, WAVEDASH_BACK_DECK, cpu_grabbed,
    dist)


def player_grabbed(c):
    """The player is being held (nr_PlayerGrabbed)."""
    return CAPTURE_PULLED_HI <= c.state <= CAPTURE_FOOT


def is_shine(state):
    """Fox's shine states, ground and air (fst_IsShine,
    fox_shine_tech.inc.h)."""
    return FOX_SHINE_FIRST <= state <= FOX_SHINE_LAST


# ---- fox-approach-nair-dair and fox-vs-crouch-cancel ------------------------
#
# The CPU stands, crouches or shields, and changes every second or so.
# What it is doing when the player's move arrives decides the verdict:
# anything hits a standing opponent; a croucher crouch-cancels everything
# weak, so it takes down air, shine or a grab; a shield takes a grab.
# fox-vs-crouch-cancel is the same with the CPU always crouching.

ST_STAND, ST_CROUCH, ST_SHIELD, ST_COUNT = range(4)
ST_MARK_NEAR, ST_MARK_GRAB = 1, 2
ST_START = 45.0
ST_NEAR = 30.0        # the demonstration jumps from here
ST_GRAB_FROM = 22.0   # and starts its jump-cancelled grab here
ST_SWITCH_MIN = 50
ST_SWITCH_SPAN = 60
ST_OPT_STANCE = 0

CROUCH_CANCEL_DECK = [
    Entry("peach", None, "Peach - Crouching"),
    Entry("samus", None, "Samus - Crouching"),
    Entry("marth", None, "Marth - Crouching"),
]


class _Stance(Drill):
    part = "neutral"
    cpu = "marth"
    characters = ("fox",)
    live_marks = True
    always_crouch = False

    def fixed(self, c):
        """The stance the option fixes, or -1 for changing."""
        if self.always_crouch:
            return ST_CROUCH
        return c.opt(ST_OPT_STANCE) - 1

    def pick(self, c):
        v = self.v
        if self.fixed(c) >= 0:
            v["stance"] = self.fixed(c)
        elif c.is_demo:
            # one stance per demonstration, each in turn
            v["stance"] = (c.demo_count + ST_COUNT - 1) % ST_COUNT
        else:
            v["stance"] = c.randi(ST_COUNT)
        v["next"] = ST_SWITCH_MIN + c.randi(ST_SWITCH_SPAN)

    def setup(self, c):
        self.v = dict(stance=0, next=0)
        hmn_x = -c.side * ST_START / 2
        c.place(hmn_x, hmn_x + c.side * ST_START, False, 20.0)
        self.pick(c)

    def build_reference(self, c):
        """Run in; against a shield, a jump-cancelled grab; otherwise a
        short hop from ST_NEAR with neutral air (standing) or down air
        (crouching) out as Fox leaves the ground."""
        js = c.fd.jump_squat
        stance = self.v["stance"]
        ref = [Ref(0, 5, 400, lx=127)]
        if stance == ST_SHIELD:
            ref.append(Ref(ST_MARK_GRAB, 1, 1, buttons=X))
            ref.append(Ref(ST_MARK_GRAB, 2, 1, buttons=Z))
        else:
            ref.append(Ref(ST_MARK_NEAR, 1, 1, buttons=X))
            if stance == ST_CROUCH:
                ref.append(Ref(ST_MARK_NEAR, 1 + js, 1, cy=-127))
            else:
                ref.append(Ref(ST_MARK_NEAR, 1 + js, 1, buttons=A))
        return ref

    def think(self, c):
        v = self.v
        state = c.me.state
        d = dist(c)

        # the CPU's stance
        if self.fixed(c) < 0 and not c.is_demo:
            v["next"] -= 1
            if v["next"] <= 0:
                was = v["stance"]
                self.pick(c)
                if v["stance"] == was:
                    v["stance"] = (was + 1) % ST_COUNT
        if v["stance"] == ST_CROUCH:
            c.cpu_press(ly=-127)
        elif v["stance"] == ST_SHIELD:
            c.cpu_shield()

        if d < ST_NEAR:
            c.mark(ST_MARK_NEAR)
        if d < ST_GRAB_FROM:
            c.mark(ST_MARK_GRAB)

        c.report("stance", v["stance"])
        if cpu_grabbed(c):
            c.result(True, "Grab!\nworks on every stance")
        elif c.cpu_state == GUARD_SET_OFF:
            c.result(False, "Blocked\ngrab a shielding opponent")
        elif c.cpu_hit:
            dair = state in (ATTACK_AIR_LW, LANDING_AIR_LW)
            if v["stance"] != ST_CROUCH:
                c.result(True, "Hit them standing")
            elif dair:
                c.result(True, "Down air beats the crouch")
            elif is_shine(state):
                c.result(True, "Shine beats the crouch")
            else:
                c.result(False, "Crouch cancelled\ndown air, shine or grab")
        elif c.hmn_hit or player_grabbed(c):
            c.result(False, "Got hit")


class FoxApproach(_Stance):
    id = "fox-approach-nair-dair"
    name = "Approach: Read the Stance"
    goal = "Pick the move that beats what the opponent is doing"
    options = (
        Option("CPU Stance", ["Changing", "Standing", "Crouching",
                              "Shielding"], 0,
               "What the CPU does: one thing, or changing between the "
               "three."),
    )
    help = ("Standing: neutral air. Crouching: down air, shine",
            "or grab. Shielding: grab.",
            "D-Pad up: guide. D-Pad down: reset.")

    def guide(self, c):
        return ["Look before you go in. What the opponent is",
                "doing decides what works:",
                "Standing: short hop neutral air.",
                "Crouching: they crouch cancel a neutral air and",
                "  hit back. Down air, shine or grab instead.",
                "Shielding: an aerial is blocked and you get",
                "  grabbed. Grab them.",
                "They change. Go when you know what you see."]


class FoxVsCrouchCancel(_Stance):
    id = "fox-vs-crouch-cancel"
    name = "Beat Crouch Cancel"
    goal = "Open a crouching opponent with down air, shine or grab"
    cpu = "peach"
    deck = CROUCH_CANCEL_DECK
    always_crouch = True
    help = ("They crouch cancel: open them with down air, shine",
            "or a grab, never neutral air.",
            "D-Pad up: guide. D-Pad down: reset.")

    def guide(self, c):
        return ["At low percent a crouching opponent barely",
                "moves when hit, and hits you back before you",
                "can act. That is the crouch cancel.",
                "It does not work against:",
                "Down air (it sends them down into the floor),",
                "shine (it knocks them off their feet),",
                "and grabs.",
                "Do not neutral air a croucher."]


# ---- fox-running-shine ------------------------------------------------------
#
# The CPU dash dances on the spot and now and then short hops. The player
# runs in and shines it: frame 1, so it catches a dash or the start of a
# jump that a slower move would lose to.

RS_MARK_CLOSE = 1
RS_START = 50.0
RS_CLOSE = 13.0       # the demonstration shines from here
RS_DASH = 9           # frames the CPU dashes each way


class FoxRunningShine(Drill):
    id = "fox-running-shine"
    name = "Running Shine"
    goal = "Catch a dash dance or a jump with shine"
    part = "neutral"
    cpu = "marth"
    characters = ("fox",)
    live_marks = True
    help = ("Running shine: run at the dash dancing opponent",
            "and shine when you touch them.",
            "D-Pad up: guide. D-Pad down: reset.")
    reference = [
        Ref(0, 5, 400, 127),
        Ref(RS_MARK_CLOSE, 1, 1, 0, -127, buttons=B),
    ]

    def setup(self, c):
        hmn_x = -c.side * RS_START / 2
        c.place(hmn_x, hmn_x + c.side * RS_START, False, 20.0)
        self.v = dict(frame=0, hop=0)

    def guide(self, c):
        return ["Shine comes out on frame 1. Run at an opponent",
                "who is dash dancing or about to jump and shine:",
                "nothing they start now is faster.",
                "Run in, then down+B when you are touching them.",
                "The shine is small. Too early and it misses.",
                "Then jump out of it: waveshine, or up smash."]

    def think(self, c):
        v = self.v
        # the CPU: dash away, dash back, sometimes a short hop in between
        v["frame"] += 1
        if v["hop"] > 0:
            v["hop"] -= 1
        elif v["frame"] % (RS_DASH * 2) == 0 and not c.is_demo and \
                c.randi(4) == 0:
            c.cpu_press(X)
            v["hop"] = 30
        else:
            away = (v["frame"] // RS_DASH) % 2
            c.cpu_press(lx=int((-127 if away else 127) * c.toward))

        if dist(c) < RS_CLOSE:
            c.mark(RS_MARK_CLOSE)
        if c.cpu_hit:
            if is_shine(c.me.state):
                c.result(True, "Running shine!")
            else:
                c.result(False, "Hit, but not with the shine")
        elif cpu_grabbed(c):
            c.result(False, "A grab, not the shine")
        elif is_shine(c.state) and c.state_frames == 12:
            c.result(False, "The shine missed\nget closer first")


# ---- fox-laser-forcing ------------------------------------------------------
#
# The CPU (Marth) waits far away. Lasers do not flinch, but nobody lets them
# add up: after a few it runs in with a dash attack (the whiff punish
# drill's: reach 50, hitbox gone after script frame 23, acts again on 48).
# The player answers that approach: any hit or grab that is not a laser,
# before being hit.

LF_MARK_ATTACK, LF_MARK_STUN_END = 1, 2
LF_LASER, LF_RUN, LF_ATTACK = range(3)
LF_START = 90.0
LF_REACH = 50.0
LF_FAF = 48
LF_LASER_DAMAGE = 3.5  # a hit of at most this is a laser

_lf_dash_attack = [In(0, 9, 127), In(8, 1, 127, buttons=A)]


class FoxLaserForcing(Drill):
    id = "fox-laser-forcing"
    name = "Lasers Force the Approach"
    goal = "Laser until they come, then punish the approach"
    part = "neutral"
    cpu = "marth"
    characters = ("fox",)
    live_marks = True
    help = ("Laser from far away. When the opponent runs in,",
            "stop shooting and punish the approach.",
            "D-Pad up: guide. D-Pad down: reset.")
    # One short hop double laser, shield the dash attack, up smash out of
    # shield (jump-cancelled) when shieldstun ends.
    reference = [
        Ref(0, 5, 1, buttons=X),
        Ref(0, 8, 1, buttons=B),
        Ref(0, 15, 1, buttons=B),
        Ref(LF_MARK_ATTACK, 1, 60, buttons=R, trigger=140),
        Ref(LF_MARK_STUN_END, 1, 1, buttons=X),
        Ref(LF_MARK_STUN_END, 2, 1, cy=127),
    ]

    def setup(self, c):
        hmn_x = -c.side * LF_START / 2
        c.place(hmn_x, hmn_x + c.side * LF_START, False, 0.0)
        self.v = dict(lasers=0, need=2 if c.is_demo else 2 + c.randi(3),
                      percent=0.0, attack_frame=0, shielded=0)

    def guide(self, c):
        return ["Lasers do little damage and no hitstun, but an",
                "opponent cannot stand in them for ever. They",
                "have to come to you, and you know it.",
                "1. Short hop lasers from far away.",
                "2. After a few they run in and attack.",
                "3. Be ready: shield it and punish, or make it",
                "   miss and punish. Do not be mid-laser."]

    def think(self, c):
        v = self.v
        gained = c.cpu.percent - v["percent"]
        laser = c.cpu_hit and gained <= LF_LASER_DAMAGE
        real_hit = (c.cpu_hit and not laser) or cpu_grabbed(c)

        v["percent"] = c.cpu.percent
        if laser:
            v["lasers"] += 1

        if c.phase == LF_LASER:
            if real_hit:
                c.result(False, "Hit before it came\nlaser from far away")
            elif v["lasers"] >= v["need"]:
                c.set_phase(LF_RUN)
            return

        if c.phase == LF_RUN:
            c.cpu_press(lx=int(127 * c.toward))
            if dist(c) < LF_REACH:
                c.mark(LF_MARK_ATTACK)
                c.set_phase(LF_ATTACK)
                v["attack_frame"] = 0
            # the hit checks apply while it runs in too
        if c.phase == LF_ATTACK:
            c.script(_lf_dash_attack, v["attack_frame"])
            v["attack_frame"] += 1
        if c.me.state == GUARD_SET_OFF:
            v["shielded"] = 1
        elif v["shielded"]:
            # shieldstun ends with the animation: during the last frame
            c.mark(LF_MARK_STUN_END, back=1)
        if c.hmn_hit:
            c.report("lasers", v["lasers"])
            c.result(False, "Got hit\nstop shooting when it comes")
        elif real_hit:
            c.measure(v["lasers"], v["need"])
            c.report("lasers", v["lasers"])
            c.report("shielded", v["shielded"])
            c.result(True, "Forced it and punished\nafter %d lasers"
                     % v["lasers"])
        elif c.phase == LF_ATTACK and v["attack_frame"] >= LF_FAF:
            c.report("lasers", v["lasers"])
            c.result(False, "No punish\nit attacked and recovered")


# ---- fox-shield-then-punish -------------------------------------------------
#
# The CPU comes in with one of the jump-in aerials of the wavedash back
# drill (WavedashBack_Deck), or, about one time in three, runs up and
# grabs. The aerial is to be shielded and punished out of shield; the grab
# cannot be shielded, so the player has to see which it is.

SP_MARK_ATTACK, SP_MARK_STUN_END, SP_MARK_CLOSE = 1, 2, 3
SP_WAIT, SP_ATTACK = range(2)
SP_GRAB_START = 40.0  # start distance when the CPU will grab
SP_GRAB_FROM = 14.0   # it presses Z this close
SP_SHINE_FROM = 15.0  # the demonstration shines it from here
SP_BUSY_MIN = 20      # frames before the CPU can count as done


class FoxShieldThenPunish(Drill):
    id = "fox-shield-then-punish"
    name = "Shield, Then Punish"
    goal = "Shield the jump-in and punish; do not shield the grab"
    part = "neutral"
    cpu = "captain-falcon"
    characters = ("fox",)
    deck = WAVEDASH_BACK_DECK
    live_marks = True
    help = ("A jump-in: shield it and shine out of shield.",
            "A run-up grab: dodge it, then punish.",
            "D-Pad up: guide. D-Pad down: reset.")

    def build_reference(self, c):
        """Aerial: hold shield, then jump and shine as shieldstun ends.
        Grab: shine it as it arrives (a spot dodge was tried: the dash grab
        carries the CPU through Fox and out of reach)."""
        js = c.fd.jump_squat
        if self.v["grab"]:
            # hit it first: the shine is out on frame 1
            return [Ref(SP_MARK_CLOSE, 1, 1, ly=-127, buttons=B)]
        return [
            Ref(SP_MARK_ATTACK, 1, 90, buttons=R, trigger=140),
            Ref(SP_MARK_STUN_END, 1, 1, buttons=X),
            Ref(SP_MARK_STUN_END, 1 + js, 1, ly=-127, buttons=B),
        ]

    def setup(self, c):
        # demonstrations alternate: aerial first
        grab = (c.demo_count + 1) % 2 if c.is_demo else \
            int(c.randi(3) == 0)
        gap = SP_GRAB_START if grab else c.entry.data.reach
        hmn_x = -c.side * gap / 2
        c.place(hmn_x, hmn_x + c.side * gap, False, 20.0)
        self.v = dict(
            grab=grab,
            wait=AP_WAIT_MIN if c.is_demo
            else AP_WAIT_MIN + c.randi(AP_WAIT_SPAN),
            attack_frame=0, pressed=0, shielded=0)

    def guide(self, c):
        return ["Shielding an approach and hitting back out of",
                "shield is safe, so opponents mix in grabs.",
                "They jump: shield, then shine out of shield",
                "  (jump, down+B as you leave the ground).",
                "They run at you on the ground: that is the",
                "  grab. Hit them first (shine is frame 1), or",
                "  jump or dodge it and punish the miss."]

    def think(self, c):
        v = self.v
        sc = c.entry.data
        hit_cpu = c.cpu_hit or cpu_grabbed(c)
        # The CPU is done when it stands again: on shield its landing
        # comes later than the scenario's `faf`, which is for a miss.
        done = v["attack_frame"] > SP_BUSY_MIN and c.cpu_state == WAIT \
            and (not v["grab"] or v["pressed"])

        if c.phase == SP_WAIT:
            if hit_cpu:
                c.result(False, "Hit before it came\nwait for the approach")
            elif c.timer >= v["wait"]:
                c.mark(SP_MARK_ATTACK)
                c.set_phase(SP_ATTACK)
            return

        # the CPU
        if not v["grab"]:
            c.script(sc.inputs, v["attack_frame"])
        elif not v["pressed"]:
            c.cpu_press(lx=int(127 * c.toward))
            if dist(c) < SP_GRAB_FROM:
                c.cpu_press(Z)
                v["pressed"] = 1
        v["attack_frame"] += 1

        # marks for the demonstration
        if v["grab"] and dist(c) < SP_SHINE_FROM:
            c.mark(SP_MARK_CLOSE)
        if c.me.state == GUARD_SET_OFF:
            v["shielded"] = 1
        elif v["shielded"]:
            # shieldstun ends with the animation: during the last frame
            c.mark(SP_MARK_STUN_END, back=1)

        c.report("grab", v["grab"])
        if player_grabbed(c):
            c.result(False, "Grabbed\nit ran in: do not shield that")
        elif c.hmn_hit:
            c.result(False, "Got hit\nit jumped: shield that")
        elif hit_cpu:
            c.measure(v["attack_frame"], v["attack_frame"])
            c.report("shielded", v["shielded"])
            if v["grab"]:
                c.result(True, "Saw the grab\nand punished it")
            elif v["shielded"]:
                c.result(True, "Shielded and punished")
            else:
                c.result(True, "Punished without the shield")
        elif done:
            c.result(False, "No punish\nthe grab missed, hit back"
                     if v["grab"] else "No punish\nhit back out of shield")


DRILLS = [FoxApproach, FoxVsCrouchCancel, FoxRunningShine, FoxLaserForcing,
          FoxShieldThenPunish]
