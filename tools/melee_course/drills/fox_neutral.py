"""Fox's Neutral drills: fox-whiff-punish, fox-wavedash-back-punish,
fox-anti-air.

Port of src/tmce/events/course/drills/fox_neutral.inc.h (specs:
data/courses/fox.md, Neutral), with their decks from
src/tmce/events/course/desc.c (WhiffPunish_Deck, WavedashBack_Deck,
AntiAir_Deck).

fox-whiff-punish: the CPU stands at the edge of an attack's reach and
throws it once the player has been inside that reach for its reaction
time. The player steps in, steps out so the attack misses, and hits or
grabs the CPU before it can act again. The reaction time is the
difficulty.

fox-wavedash-back-punish and fox-anti-air: the CPU stands at a scenario's
start distance and, after a wait the player cannot predict, jumps in with
an aerial. Natively, by default (option Opponent: Reactive,
melee_course/react.py), the jump-in is the same table played by the Melee
Actor: it moves back to the scenario's distance from wherever the player
went during the wait, looks ahead, and jumps once the aerial would land.
The drill's clock (attack_frame) starts at the jump either way.

fox-anti-air plays by default against Opponent: Engine
(melee_engine/jumpin.py): both fighters move; the CPU dash dances and walks
about the scenario's distance, chooses its moment, and its jump, drift and
aerial timing are found by the search engine so that the aerial lands
where the player is. It jumps only once the engine has found the player an
up tilt, up smash or back air that beats that jump-in, started no sooner
than a person's reaction time after the jump; in the air it follows the
player, and sees what the player commits to only after its own reaction
time, so an anti-air thrown early is punished. The demonstration plays the
answer the engine found.
"""
import random

from melee_actor.actor import STAGE_LIMIT
from melee_course.engine import (
    A, R, X, Drill, Entry, In, Option, Ref, ATTACK_AIR_B, ATTACK_HI3,
    ATTACK_HI4, CAPTURE_PULLED_HI, GUARD_SET_OFF, LANDING_FALL_SPECIAL)
from melee_course.react import (
    ENGINE, FIXED, Opponent, opponent_option, player_raw, put_raw, sequence,
    thinker)

# ftCo_MS_CaptureFoot (src/melee/ft/kinds/ftCommon/forward.h): the last of
# the states of a fighter being held.
CAPTURE_FOOT = 232


def cpu_grabbed(c):
    """The CPU is being held (fpr_CpuGrabbed, fox_pressure.inc.h)."""
    return CAPTURE_PULLED_HI <= c.cpu_state <= CAPTURE_FOOT


def dist(c):
    return abs(c.cpu.pos[0] - c.me.pos[0])


class WhiffScenario:
    """A scenario of a whiff-punish drill (course.h): the attack hits a
    standing player within `reach` (for the approaches: the start
    distance); `inputs` frame 0 = when the CPU commits; `hit_end`: script
    frame its last hitbox is gone after (the approaches: the landing);
    `faf`: script frame the CPU can act again; `demo_back`: script frame
    the demonstration goes back in; `demo_out`: script frame of its first
    move (approaches)."""

    def __init__(self, reach, inputs, hit_end, faf, demo_back=0, demo_out=0,
                 aerial=None):
        self.reach, self.inputs = reach, inputs
        self.hit_end, self.faf = hit_end, faf
        self.demo_back, self.demo_out = demo_back, demo_out
        self.aerial = aerial      # the engine opponent's (Opponent: Engine)


# ---- fox-whiff-punish: the attacks (desc.c) ---------------------------------
#
# Reach, hit and recovery frames measured against a standing Fox in the
# simulator sandbox and checked against data/framedata (2026-11-12):
#   Marth forward smash: hits out to 34 units, hitbox frames 10-13, acts
#     again on 48.
#   Marth dash attack (8 frames of dash, then A): from 29 out to 58,
#     hitbox 12-15 of the attack, interruptible from 40.
#   Sheik and Peach dash attack (8 frames of dash, then A): out to 46-47;
#     hitbox 6-12 (Sheik) and 6-20 (Peach) of the attack, acts again on 36.
# `reach` is a little inside the measured reach, so standing there is hit.
_wp_fsmash = [In(0, 1, 0, 0, 127, 0, 0)]
_wp_dash_attack = [In(0, 9, 127, 0, 0, 0, 0), In(8, 1, 127, 0, 0, 0, A)]

WHIFF_PUNISH_DECK = [
    Entry("marth", WhiffScenario(31.0, _wp_fsmash, 13, 48, 3),
          "Marth - Forward Smash"),
    Entry("marth", WhiffScenario(50.0, _wp_dash_attack, 23, 48, 9),
          "Marth - Dash Attack"),
    Entry("sheik", WhiffScenario(42.0, _wp_dash_attack, 20, 44, 10),
          "Sheik - Dash Attack"),
    Entry("peach", WhiffScenario(42.0, _wp_dash_attack, 28, 44, 12),
          "Peach - Dash Attack"),
]

# ---- jump-in approaches (desc.c) --------------------------------------------
#
# Frame 0 is the jump input. Measured against a standing Fox in the
# simulator sandbox (2026-11-12); "lands" and "acts" are for the attack
# missing. No L-cancel: the landing lag is the window being taught.
# Short hops, for fox-wavedash-back-punish:
#   Falcon nair from 30: hits a Fox within 36 on frame 33; lands 35, acts 54.
#   Falco dair from 20: within 22, frame 18-21; lands 30, acts 48.
#   Marth fair from 26: within 31, frame 29; lands 42, acts 57.
# Full hops, for fox-anti-air:
#   Falcon nair from 47: hits on frame 51; lands 53-61.
#   Falcon dair from 45: frame 51; lands 52-59.
#   Jigglypuff fair from 60: frame 46; lands 56-62.
#   Peach fair from 50: frame 52; lands 64-71.
_ap_falcon_sh_nair = [In(0, 1, buttons=X), In(5, 30, 127),
                      In(20, 1, 127, buttons=A)]
_ap_falco_sh_dair = [In(0, 1, buttons=X), In(6, 20, 127),
                     In(14, 1, 127, 0, 0, -127)]
_ap_marth_sh_fair = [In(0, 1, buttons=X), In(5, 30, 127),
                     In(24, 1, 127, 0, 127, 0)]
_ap_falcon_fh_nair = [In(0, 8, buttons=X), In(5, 45, 127),
                      In(38, 1, 127, buttons=A)]
_ap_falcon_fh_dair = [In(0, 8, buttons=X), In(5, 45, 127),
                      In(36, 1, 127, 0, 0, -127)]
_ap_puff_fh_fair = [In(0, 8, buttons=X), In(6, 60, 127),
                    In(40, 1, 127, 0, 127, 0)]
_ap_peach_fh_fair = [In(0, 8, buttons=X), In(6, 60, 127),
                     In(34, 1, 127, 0, 127, 0)]

#                        start inputs  lands acts back out
WAVEDASH_BACK_DECK = [
    Entry("captain-falcon",
          WhiffScenario(30.0, _ap_falcon_sh_nair, 35, 54, 30, 6),
          "Falcon - Nair"),
    Entry("falco", WhiffScenario(20.0, _ap_falco_sh_dair, 30, 48, 22, 3),
          "Falco - Dair"),
    Entry("marth", WhiffScenario(26.0, _ap_marth_sh_fair, 42, 57, 34, 6),
          "Marth - Fair"),
]

ANTI_AIR_DECK = [
    Entry("captain-falcon",
          WhiffScenario(47.0, _ap_falcon_fh_nair, 61, 80, 0, 40, "nair"),
          "Falcon - Full Hop Nair"),
    Entry("captain-falcon",
          WhiffScenario(45.0, _ap_falcon_fh_dair, 59, 83, 0, 40, "dair"),
          "Falcon - Full Hop Dair"),
    Entry("jigglypuff",
          WhiffScenario(60.0, _ap_puff_fh_fair, 62, 82, 0, 35, "fair"),
          "Jigglypuff - Fair"),
    Entry("peach",
          WhiffScenario(50.0, _ap_peach_fh_fair, 71, 96, 0, 41, "fair"),
          "Peach - Fair"),
]


def percent_option():
    return Option("CPU Percent", count=151, default=20, fmt="%d%%",
                  desc="The CPU's damage at the start of each attempt.")


# ---- fox-whiff-punish -------------------------------------------------------

WP_MARK_TRIGGER, WP_MARK_ATTACK, WP_MARK_CLOSE = 1, 2, 3
WP_OPT_REACTION, WP_OPT_PERCENT = range(2)
WP_BAIT, WP_REACT, WP_ATTACK = range(3)

WP_START_GAP = 14.0   # the player starts this far outside the attack's reach
# Where the demonstration starts its jump-cancelled up smash: Fox is running
# and slides in while it comes out.
WP_CLOSE = 16.0
WP_REACTIONS = (20, 14, 9)


class FoxWhiffPunish(Drill):
    id = "fox-whiff-punish"
    name = "Whiff Punish"
    goal = "Bait an attack, make it miss, punish its recovery"
    part = "neutral"
    cpu = "marth"
    characters = ("fox",)
    deck = WHIFF_PUNISH_DECK
    live_marks = True
    options = (
        Option("CPU Reaction", ["Slow (20)", "Normal (14)", "Fast (9)"], 1,
               "Frames the CPU takes to attack once you are inside its "
               "range. Faster is harder to bait."),
        percent_option(),
    )
    help = ("Whiff punish: dash into range, dash out so the",
            "attack misses, then punish before they recover.",
            "D-Pad up: guide. D-Pad down: reset.")

    def reaction(self, c):
        """The demonstration's timings are tuned for the Normal reaction,
        so it is always shown at that."""
        if c.is_demo:
            return WP_REACTIONS[1]
        return WP_REACTIONS[c.opt(WP_OPT_REACTION)]

    def build_reference(self, c):
        """Dash in; once the CPU has noticed, dash back out (ten frames of
        stick: the dash itself carries Fox about 40 units), let go until
        the scenario's `demo_back`, dash in again and up smash when close.
        All timed against marks of the same attempt."""
        sc = c.entry.data
        out = 10
        wait = self.reaction(c) + sc.demo_back - out
        ref = [Ref(0, 5, 400, lx=127),   # toward the CPU unless told
               Ref(WP_MARK_TRIGGER, 1, out, lx=-127)]
        if wait > 0:
            # inside the dead zone: stand still
            ref.append(Ref(WP_MARK_TRIGGER, 1 + out, wait, lx=1))
        # Up smash out of a run has to be jump-cancelled.
        ref.append(Ref(WP_MARK_CLOSE, 1, 1, buttons=X))
        ref.append(Ref(WP_MARK_CLOSE, 2, 1, cy=127))
        return ref

    def setup(self, c):
        gap = c.entry.data.reach + WP_START_GAP
        hmn_x = -c.side * gap / 2
        c.place(hmn_x, hmn_x + c.side * gap, False,
                float(c.opt(WP_OPT_PERCENT)))
        self.v = dict(attack_frame=0)

    def guide(self, c):
        sc = c.entry.data if c.entry else None
        lines = ["An attack that misses leaves its user stuck.",
                 "Make the opponent swing at nothing:",
                 "1. Dash into their range. They react in %d"
                 % self.reaction(c),
                 "   frames and attack.",
                 "2. Dash back out before the attack reaches.",
                 "3. Dash in and grab or hit before they recover."]
        if sc is not None:
            lines.append("%s: hitbox gone after frame" % c.entry.name)
            lines.append("%d, acts again on frame %d." % (sc.hit_end, sc.faf))
        return lines

    def think(self, c):
        v = self.v
        sc = c.entry.data
        d = dist(c)
        hit_cpu = c.cpu_hit or cpu_grabbed(c)
        if c.phase in (WP_BAIT, WP_REACT):
            if hit_cpu:
                c.result(False, "Hit before it swung\nbait the attack first")
            elif c.phase == WP_BAIT:
                if d < sc.reach:
                    c.mark(WP_MARK_TRIGGER)
                    c.set_phase(WP_REACT)
            elif c.timer >= self.reaction(c):
                c.mark(WP_MARK_ATTACK)
                c.set_phase(WP_ATTACK)
                v["attack_frame"] = 0
        elif c.phase == WP_ATTACK:
            c.script(sc.inputs, v["attack_frame"])
            v["attack_frame"] += 1
            if v["attack_frame"] > sc.hit_end and d < WP_CLOSE:
                c.mark(WP_MARK_CLOSE)
            if c.hmn_hit:
                c.report("frame", v["attack_frame"])
                c.result(False, "Got hit: still in range\nleave sooner")
            elif c.me.state == GUARD_SET_OFF:
                c.result(False, "Shielded it\nmake it miss instead")
            elif hit_cpu:
                spare = sc.faf - v["attack_frame"]
                c.measure(v["attack_frame"], sc.hit_end + 1)
                c.report("frame", v["attack_frame"])
                c.report("spare", spare)
                c.result(True, "Whiff punish!\n%d frames to spare" % spare)
            elif v["attack_frame"] >= sc.faf:
                c.result(False, "Too slow\nit recovered on frame %d" % sc.faf)


# ---- jump-in approaches: shared ---------------------------------------------

AP_MARK_ATTACK, AP_MARK_CLOSE = 1, 2
AP_WAIT, AP_ATTACK = range(2)
AP_OPT_PERCENT, AP_OPT_OPPONENT = range(2)
AP_WAIT_MIN = 40
AP_WAIT_SPAN = 60


class _Approach(Drill):
    """The CPU stands at a scenario's start distance and, after a wait the
    player cannot predict, jumps in with an aerial (ap_* in the C)."""
    # what the engine opponent's check counts as the player's answer
    ANSWERS = (ATTACK_HI3, ATTACK_HI4, ATTACK_AIR_B)
    part = "neutral"
    cpu = "captain-falcon"
    characters = ("fox",)
    live_marks = True
    options = (percent_option(), opponent_option())
    # The reactive opponent in the air: "jump" commits to the jump-in as
    # designed (the player answers what they saw: the jump); "air" keeps
    # its drift on the player, as a person drifting onto a target does.
    track = "jump"

    def setup(self, c):
        self.opp = None
        self.eng = None
        gap = c.entry.data.reach
        hmn_x = -c.side * gap / 2
        c.place(hmn_x, hmn_x + c.side * gap, False,
                float(c.opt(AP_OPT_PERCENT)))
        # a demonstration does not keep its viewer waiting
        self.v = dict(
            wait=AP_WAIT_MIN if c.is_demo
            else AP_WAIT_MIN + c.randi(AP_WAIT_SPAN),
            attack_frame=0, wavedash=0, placed=None)

    def advance(self, c):
        """Runs the wait and the CPU's script. True while the approach is
        on (ap_Advance). The reactive opponent, after the wait, may move
        and wait some more before it jumps; the approach is on from the
        jump."""
        v = self.v
        sc = c.entry.data
        if c.opt(AP_OPT_OPPONENT) == ENGINE:
            return self.advance_engine(c)
        fixed = c.opt(AP_OPT_OPPONENT) == FIXED
        if c.s.attempt_frame == 3:
            # the spacing the jump-in was designed from, as placed
            v["placed"] = abs(c.cpu.pos[0] - c.me.pos[0])
        if c.phase == AP_WAIT:
            if c.timer < v["wait"]:
                return False
            if not fixed:
                if self.opp is None:
                    self.opp = Opponent(c, [dict(
                        do="sequence", inputs=sequence(sc.inputs),
                        distance=v["placed"] or sc.reach,
                        tolerance=0.75,
                        precision=0.2,
                        track=self.track)])
                self.opp.frame(c)
                if self.opp.committed is None:
                    return False
            c.mark(AP_MARK_ATTACK)
            c.set_phase(AP_ATTACK)
            v["attack_frame"] = 0
        elif not fixed:
            self.opp.frame(c)
        if fixed:
            c.script(sc.inputs, v["attack_frame"])
        v["attack_frame"] += 1
        return True

    def engine_opponent(self, c):
        """The engine's jump-in (melee_engine/jumpin.py): it moves about the
        scenario's distance, then jumps in with its aerial. A
        demonstration's comes sooner and does not follow the player in the
        air: the player there plays the answer that was checked."""
        from melee_engine.jumpin import Footsies, JumpIn
        sc, s = c.entry.data, c.s
        rng = random.Random(c.rng.random())
        half = STAGE_LIMIT.get(s.d.stage, 70.0)
        body = Footsies(s.cpu_port, s.person,
                        band=(sc.reach - 12.0, sc.reach + 15.0),
                        rng=random.Random(rng.random()), half=half)
        return JumpIn(thinker(c), s.cpu_port, s.person, sc.aerial, body,
                      rng=rng, track=not c.is_demo,
                      wait=(5, 15) if c.is_demo else (20, 110),
                      states=self.ANSWERS,
                      reach=(sc.reach - 20.0, sc.reach + 20.0))

    def advance_engine(self, c):
        v = self.v
        if self.eng is None:
            self.eng = self.engine_opponent(c)
        put_raw(c, self.eng.pad(c.n.state(), player_raw(c)))
        if c.phase == AP_WAIT:
            if self.eng.jumped is None:
                return False
            c.mark(AP_MARK_ATTACK)
            c.set_phase(AP_ATTACK)
            v["attack_frame"] = 0
        v["attack_frame"] += 1
        return True


# ---- fox-wavedash-back-punish -----------------------------------------------


class FoxWavedashBack(_Approach):
    id = "fox-wavedash-back-punish"
    name = "Wavedash Back Punish"
    goal = "Wavedash out of an approach and punish its landing"
    deck = WAVEDASH_BACK_DECK
    help = ("Wavedash back out of the jump-in, then dash in and",
            "punish the landing.",
            "D-Pad up: guide. D-Pad down: reset.")

    def build_reference(self, c):
        """Wavedash back as the CPU jumps, dash in at the scenario's
        `demo_back` and jump-cancel an up smash when close. Against Marth
        it connects on the last frame that counts (he slides behind Fox as
        he lands); a jump-cancelled grab was tried and is out of range in
        all three."""
        sc = c.entry.data
        js = c.fd.jump_squat
        return [
            Ref(AP_MARK_ATTACK, sc.demo_out, 1, buttons=X),
            Ref(AP_MARK_ATTACK, sc.demo_out + js, 2, lx=-100, ly=-75,
                buttons=R, trigger=140),
            Ref(AP_MARK_ATTACK, sc.demo_back, 200, lx=127),
            Ref(AP_MARK_CLOSE, 1, 1, buttons=X),
            Ref(AP_MARK_CLOSE, 2, 1, cy=127),
        ]

    def guide(self, c):
        sc = c.entry.data if c.entry else None
        lines = ["An opponent who jumps at you has chosen where",
                 "they land. Do not be there.",
                 "1. When they jump, wavedash back: jump, then",
                 "   air dodge down and away at once.",
                 "2. Their attack lands in front of you.",
                 "3. Dash in and punish the landing lag."]
        if sc is not None:
            lines.append("%s: lands on frame %d," % (c.entry.name,
                                                    sc.hit_end))
            lines.append("acts again on frame %d." % sc.faf)
        return lines

    def think(self, c):
        v = self.v
        sc = c.entry.data
        d = dist(c)
        hit_cpu = c.cpu_hit or cpu_grabbed(c)
        if not self.advance(c):
            if hit_cpu:
                c.result(False, "Hit before it jumped\nwait for the approach")
            return
        if c.state == LANDING_FALL_SPECIAL:
            v["wavedash"] = 1
        # For the demonstration: its up smash takes a few frames, so it
        # starts a little before the landing.
        if v["attack_frame"] > sc.hit_end - 4 and d < WP_CLOSE:
            c.mark(AP_MARK_CLOSE)
        if c.hmn_hit:
            c.report("frame", v["attack_frame"])
            c.result(False, "Got hit\nwavedash back sooner")
        elif c.me.state == GUARD_SET_OFF:
            c.result(False, "Shielded it\nmove out of the way instead")
        elif hit_cpu:
            spare = sc.faf - v["attack_frame"]
            c.report("frame", v["attack_frame"])
            c.report("spare", spare)
            c.report("wavedash", v["wavedash"])
            if not v["wavedash"]:
                c.result(False, "Hit, but no wavedash back\n"
                                "that is the Anti-Air drill")
            else:
                c.measure(v["attack_frame"], sc.hit_end + 1)
                c.result(True, "Wavedash back punish!\n%d frames to spare"
                         % spare)
        elif v["attack_frame"] >= sc.faf:
            c.result(False, "Too slow\nit recovered on frame %d" % sc.faf)


# ---- fox-anti-air -----------------------------------------------------------


class FoxAntiAir(_Approach):
    id = "fox-anti-air"
    name = "Anti-Air"
    goal = "Beat a jump-in with up tilt, up smash or back air"
    deck = ANTI_AIR_DECK
    track = "air"
    options = (percent_option(), opponent_option(engine=True))
    # an engine opponent that never finds its moment: a retry
    ENGINE_LIMIT = 900
    help = ("Anti-air: beat the jump-in with up tilt, up smash",
            "or back air before it reaches you.",
            "D-Pad up: guide. D-Pad down: reset.")

    def build_reference(self, c):
        """An up smash timed to meet the jump-in. Against the engine
        opponent: the answer its check found (think())."""
        if c.opt(AP_OPT_OPPONENT) == ENGINE:
            return []
        return [Ref(AP_MARK_ATTACK, c.entry.data.demo_out, 1, cy=127)]

    def play_answer(self, c):
        """A demonstration against the engine: the player's pad is the
        answer the opponent's check found, from the frame it was found
        for."""
        ans = self.eng.answer if self.eng is not None else None
        if ans is None:
            c.s.set_player_pad()
            return
        start, pads = ans
        i = self.eng.frame - start
        b, lx, ly, cx, cy, lt, rt = pads[i] if 0 <= i < len(pads) else \
            (0, 0, 0, 0, 0, 0, 0)
        c.s.set_player_pad(b, lx, ly, cx, cy, max(lt, rt))

    def guide(self, c):
        me = c.fd
        return ["A jump commits the opponent to an arc. Meet",
                "them at the end of it with a move that hits",
                "upward before their attack reaches you.",
                "Up tilt: hits on frame %d." % me.move["utilt"].hit,
                "Up smash: frame %d.   Back air: frame %d."
                % (me.move["usmash"].hit, me.move["bair"].hit),
                "Swing as they come down, not as they jump."]

    def think(self, c):
        v = self.v
        sc = c.entry.data
        engine = c.opt(AP_OPT_OPPONENT) == ENGINE
        if engine and c.is_demo:
            self.play_answer(c)
        if not self.advance(c):
            if c.cpu_hit or cpu_grabbed(c):
                c.result(False, "Hit before it jumped\nwait for the approach")
            elif engine and c.s.attempt_frame > self.ENGINE_LIMIT:
                c.retry("No approach came\nretrying")
            return
        state = c.me.state
        if c.hmn_hit:
            c.report("frame", v["attack_frame"])
            c.result(False, "Got hit\nswing earlier")
        elif state == GUARD_SET_OFF:
            c.result(False, "Shielded it\nbeat it instead")
        elif c.cpu_hit:
            anti = state in (ATTACK_HI3, ATTACK_HI4, ATTACK_AIR_B)
            c.report("frame", v["attack_frame"])
            landed = (not c.cpu.airborne) if engine else \
                v["attack_frame"] > sc.hit_end
            if landed:
                c.result(False, "Hit after they landed\nmeet them in the air")
            elif not anti:
                c.result(False, "Hit, but not an anti-air\n"
                                "up tilt, up smash or back air")
            else:
                c.measure(v["attack_frame"], v["attack_frame"])
                c.result(True, "Anti-air!\non frame %d of the jump"
                         % v["attack_frame"])
        elif (self.eng.mode == "done" if engine else
              v["attack_frame"] >= sc.faf):
            c.result(False, "No anti-air\nthey landed and recovered")


DRILLS = [FoxWhiffPunish, FoxWavedashBack, FoxAntiAir]
