"""Defense: universal-asdi-down and universal-crouch-cancel, apart (the owner,
2026-11-13: "Let's separate ASDI and crouch cancel drills. Both of these are
very important").

In both a CPU throws out a weak move from a deck of actors, and the player
holds the ground through it and hits back before the CPU can act again.

- ASDI down: standing, the C-stick held down as the hit's freeze ends. The
  game moves the fighter 3 units toward the floor
  (ftCo_Damage_OnExitHitlag); under 80 knockback that is back on the floor
  at once, in a 4-frame landing. A C-stick held all along counts: ASDI reads
  the stick as it is, not a new press.
- Crouch cancel: crouching (Squat or SquatWait, not SquatRv) when hit. The
  knockback is two thirds and so is the defender's hitlag (the attacker
  keeps all of his), so it holds through more and gives more frames.

What each actor can be held against (the player's percent before the hit,
fresh moves, Fox; computed with the knockback formula and checked against
DruggedFox's measured table, research of 2026-11-13): above `asdi_max` a
standing ASDI down no longer lands at once (a tech or a knockdown, then a
launch), above `cc_max` a crouch cancel no longer does. The drill keeps to
the percents where it holds; "Near its limit" puts it just under the edge.

The CPU can act when its move's animation reaches the interrupt (ground
moves: the animation frame, which hitlag does not advance) or when it has
landed and stands (aerials). From then it shields, so a punish that comes
later is blocked. The player is to land the punish before.
"""
from melee_course.engine import (
    A, B, X, Drill, Entry, In, Option, Ref, WAIT, LANDING, SQUAT,
    SQUAT_WAIT, SQUAT_RV, DAMAGE_FALL, GUARD_SET_OFF)

DAMAGE_FLY_HI, DAMAGE_FLY_ROLL = 87, 91
DOWN_BOUND_U, DOWN_SPOT_D = 183, 198
PASSIVE, PASSIVE_STAND_B = 199, 201
CAPTURE_PULLED_HI, CAPTURE_FOOT = 223, 232
# The C-stick down at 0.7 of its reach (sdi_min_stick_mag), in the pad's
# units as the engine logs them (80 is all the way: STICK_SMASH is 53).
ASDI_STICK = -56
SLACK = 2                 # frames past the CPU's first free one still counted
# Landing out of the hit lasts until the hitstun is over, but can be left
# for an attack, a grab or a shine after the normal landing lag (Fox's 4:
# ftCo_Landing_IASA), which is what ASDI down is for.
LANDING_LAG = 4
AW_WAIT_MIN, AW_WAIT_SPAN = 40, 60


class Actor:
    """A move the CPU throws out: its inputs (X toward the player), the
    distance the two start at, the frame of its animation from which it can
    act (None: an aerial, free when it has landed and stands), and the
    highest percents a standing ASDI down and a crouch cancel hold at."""

    def __init__(self, inputs, distance, iasa, asdi_max, cc_max):
        self.inputs, self.distance, self.iasa = inputs, distance, iasa
        self.asdi_max, self.cc_max = asdi_max, cc_max


_marth_dtilt = [In(0, 1, 0, -80, buttons=A)]
_sheik_ftilt = [In(0, 1, 70, 0, buttons=A)]
_sheik_dtilt = [In(0, 1, 0, -80, buttons=A)]
# short hop aerials (fox_neutral.py's jump-ins, measured there)
_falcon_sh_nair = [In(0, 1, buttons=X), In(5, 30, 127),
                   In(20, 1, 127, buttons=A)]
_marth_sh_fair = [In(0, 1, buttons=X), In(5, 30, 127),
                  In(24, 1, 127, 0, 127, 0)]

# The limits are measured on the native build, the drill's own demonstration
# (the hold, then a shine on the first frame it is taken) at each 10%, then
# put a little inside where it last worked (tests/course/asdi.py checks them;
# research of 2026-11-13 for why). None: the hold does not work against it at
# all (Falcon's nair launches a standing Fox at any percent). 150: it holds
# at every percent tried. Where a hold still works but the punish no longer
# reaches (Marth's fair past 50% crouching), the limit is the punish's.
#                                   inputs        dist iasa asdi   cc
ACTORS = [
    Entry("marth", Actor(_marth_dtilt, 6.7, 20, 150, 150),
          "Marth - Down Tilt"),
    Entry("sheik", Actor(_sheik_ftilt, 8.0, 27, 22, 74),
          "Sheik - Forward Tilt"),
    Entry("sheik", Actor(_sheik_dtilt, 9.0, 28, 33, 100),
          "Sheik - Down Tilt"),
    Entry("marth", Actor(_marth_sh_fair, 22.0, None, 32, 52),
          "Marth - Fair"),
    Entry("captain-falcon", Actor(_falcon_sh_nair, 30.0, None, None, 22),
          "Falcon - Nair"),
]
ASDI_DECK = [e for e in ACTORS if e.data.asdi_max is not None]
CC_DECK = [e for e in ACTORS if e.data.cc_max is not None]

OPT_PERCENT = 0
PERCENT_ANY, PERCENT_EDGE = range(2)
MARK_HIT, MARK_FREE = 1, 2
WAITING, ATTACK, PUNISH = range(3)


def _percent_option():
    return Option("Percent", ["Anywhere it holds", "Near its limit"], 0,
                  "Your damage at each attempt: anywhere the hold works "
                  "against this move, or just under where it stops.")


def _launched(c):
    me = c.me
    return (DOWN_BOUND_U <= c.state <= DOWN_SPOT_D or
            PASSIVE <= c.state <= PASSIVE_STAND_B or
            c.state == DAMAGE_FALL or
            DAMAGE_FLY_HI <= me.state <= DAMAGE_FLY_ROLL)


def _cpu_grabbed(c):
    return CAPTURE_PULLED_HI <= c.cpu_state <= CAPTURE_FOOT


class _HoldAndPunish(Drill):
    """What the two drills share; `crouch` says which hold is asked for."""
    part = "defense"
    cpu = "marth"
    live_marks = True
    crouch = False

    def limit(self, actor):
        return actor.cc_max if self.crouch else actor.asdi_max

    def setup(self, c):
        actor = c.entry.data
        top = self.limit(actor)
        if c.opt(OPT_PERCENT) == PERCENT_EDGE:
            percent = max(0, top - 6) + c.randi(7)
        else:
            percent = c.randi(top + 1)
        hmn_x = -c.side * actor.distance / 2
        c.place(hmn_x, hmn_x + c.side * actor.distance, False, 20.0,
                float(percent))
        self.v = dict(wait=AW_WAIT_MIN if c.is_demo else
                      AW_WAIT_MIN + c.randi(AW_WAIT_SPAN),
                      frame=0, percent=percent, crouched=False,
                      asdi=False, free=None, held_cy=0, out=False)

    def _cpu_free(self, c):
        """Can the CPU act (and so shield) this frame?"""
        actor = c.entry.data
        if actor.iasa is not None:
            return c.cpu_state == WAIT or (
                self.v["frame"] > 1 and c.cpu.state_frame >= actor.iasa)
        return c.cpu_state in (WAIT, SQUAT_WAIT) and self.v["frame"] > 8

    def think(self, c):
        v, actor = self.v, c.entry.data
        if c.phase == WAITING:
            if c.cpu_hit or _cpu_grabbed(c):
                c.result(False, "Hit before it attacked: take the hit first")
            elif c.timer >= v["wait"]:
                c.set_phase(ATTACK)
                v["frame"] = 0
            return
        c.script(actor.inputs, v["frame"])
        v["frame"] += 1
        if v["free"] is None and c.phase == PUNISH and self._cpu_free(c):
            v["free"] = v["frame"]
        if v["free"] is not None:
            c.cpu_shield()
        if c.phase == ATTACK:
            if c.me.hitlag > 0 or c.hmn_hit:
                v["crouched"] = c.prev_state in (SQUAT, SQUAT_WAIT) or \
                    c.state in (SQUAT, SQUAT_WAIT)
                c.mark(MARK_HIT)
                c.set_phase(PUNISH)
            elif c.me.state == GUARD_SET_OFF:
                c.result(False, "Shielded it: take the hit and hold")
            elif v["frame"] > 90:
                c.retry("The move missed\nstay where you are")
            return
        # PUNISH: the hold, judged as the hit's freeze ends; then the punish
        # (whose own hit freezes the player too: that is not this freeze)
        if not v["out"]:
            if c.me.hitlag > 0:
                v["held_cy"] = c.s.tl_log[-1]["cy"] if c.s.tl_log else 0
                return
            v["out"] = True
            v["asdi"] = v["held_cy"] <= ASDI_STICK
        if c.state in (WAIT, SQUAT_WAIT) or (
                c.state == LANDING and c.me.state_frame >= LANDING_LAG):
            c.mark(MARK_FREE)           # the first frame a shine is taken
        c.report("crouched", int(v["crouched"]))
        if _launched(c):
            c.result(False, self.launched_words(v))
        elif c.cpu_hit or _cpu_grabbed(c):
            late = v["free"] is not None and \
                v["frame"] > v["free"] + SLACK
            c.measure(v["frame"], v["free"] or v["frame"])
            if late:
                c.result(False, "Late: he could act %d frames before"
                         % (v["frame"] - v["free"]))
            else:
                ok, words = self.held_words(v)
                c.result(ok, words)
        elif c.cpu_state == GUARD_SET_OFF:
            c.result(False, "Too slow: he shielded")
        elif v["frame"] > 150:
            c.result(False, "No punish: hit back as soon as you land")

    def launched_words(self, v):
        raise NotImplementedError

    def held_words(self, v):
        raise NotImplementedError


class DefAsdiDownStand(_HoldAndPunish):
    id = "universal-asdi-down"
    name = "ASDI Down"
    goal = "Hold the C-stick down through a weak hit and punish"
    deck = ASDI_DECK
    options = (_percent_option(),)
    help = ("Stand, hold the C-stick down as it hits, land",
            "at once and hit back.",
            "D-Pad up: guide. D-Pad down: reset.")
    # The C-stick goes down during the hit's freeze: pressed while
    # standing it would be a down smash.
    reference = [
        Ref(MARK_HIT, 0, 120, cy=-127),
        Ref(MARK_FREE, 1, 1, 0, -127, 0, -127, buttons=B),   # the shine
    ]

    def guide(self, c):
        return ["Have the C-stick down when a weak hit's freeze",
                "ends: you move 3 units toward the floor and land",
                "at once, while they are still in their move.",
                "Press it during the freeze, or keep it held from",
                "before (through the reset): a fresh press while",
                "standing is a down smash. Stand: crouching is",
                "the crouch cancel drill.",
                "Then hit back first: shine, grab, down smash.",
                "Each move holds up to some percent; Near its",
                "limit puts you just under it."]

    def launched_words(self, v):
        if not v["asdi"]:
            return "Launched: hold the C-stick down as it hits"
        return "Launched at %d%%: past what holds" % v["percent"]

    def held_words(self, v):
        if v["crouched"]:
            return (False, "Crouched: that is a crouch cancel. Stand and "
                    "hold the C-stick down")
        if not v["asdi"]:
            return (True, "Punished, but the C-stick was not down")
        return (True, "ASDI down punish! at %d%%" % v["percent"])


class DefCrouchCancel(_HoldAndPunish):
    id = "universal-crouch-cancel"
    name = "Crouch Cancel"
    goal = "Crouch through a weak hit and punish"
    crouch = True
    deck = CC_DECK
    options = (_percent_option(),)
    help = ("Crouch, take the hit, and hit back before they",
            "can shield.",
            "D-Pad up: guide. D-Pad down: reset.")
    reference = [
        Ref(0, 5, 400, 0, -127),
        Ref(MARK_FREE, 1, 1, 0, -127, buttons=B),
    ]

    def guide(self, c):
        return ["Crouching when a hit lands takes a third off",
                "its knockback and off your freeze (not theirs):",
                "you stay on the floor through more, with more",
                "time to answer.",
                "Crouch before it hits (not as you stand up),",
                "then hit back first: shine, grab, down smash.",
                "Each move holds up to some percent; Near its",
                "limit puts you just under it."]

    def launched_words(self, v):
        if not v["crouched"]:
            return "Launched: crouch before it hits"
        return "Launched at %d%%: past what holds" % v["percent"]

    def held_words(self, v):
        if not v["crouched"]:
            return (False, "Standing when it hit: crouch first")
        return (True, "Crouch cancel punish! at %d%%" % v["percent"])


DRILLS = [DefAsdiDownStand, DefCrouchCancel]
