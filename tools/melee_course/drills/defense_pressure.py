"""Defense drills, third file: universal-sdi, fox-escape-pressure,
fox-recovery-mixup, universal-wall-tech.

Port of src/tmce/events/course/drills/defense_pressure.inc.h (specs:
data/courses/fox.md, Defense 4, 7, 10).

fox-recovery-mixup reads two things the native build does not report:
the frames of ledge intangibility left (`hd->hurt.intang_frames.ledge`)
and whether the player is intangible by their own move
(`hd->hurt.kind_game`). Both are derived here: see LedgeIntangibility and
own_intangible.
"""
import json
import os

from melee_course.engine import (
    ROOT, A, B, L, R, X, Z, Drill, In, Option, Ref, WAIT, GUARD, GUARD_ON,
    GUARD_REFLECT, GUARD_SET_OFF, CLIFF_CATCH, CLIFF_WAIT, PASSIVE_WALL,
    PASSIVE_WALL_JUMP)
from melee_course.drills.defense import (
    attack_wait, cpu_grabbed, dist, in_hitstun, is_shine, player_dead,
    player_grabbed)

SHIELD_BREAK_FLY, SHIELD_BREAK_FALL = 205, 206
FLY_REFLECT_WALL = 247

# ---- universal-sdi ----------------------------------------------------------
#
# Fox short hops a down air (the drill: up to seven weak hits; three land
# from this short hop) onto the standing player and shines as he lands. Each
# hit freezes both for a moment, and every fresh push of the stick during a
# freeze moves the player a little (smash DI). Enough pushes away and the
# later hits, or the shine, miss.

SX_MARK_HIT = 1
SX_WAIT, SX_DRILL, SX_SHINE = range(3)
SX_START = 12.0
SX_SHINE_REACH = 14.0     # the CPU only shines a player this close
SX_TAPS = 14

SX_DAIR = [
    In(0, 1, buttons=X),
    In(4, 8, 127),
    In(10, 1, 0, 0, 0, -127),
    In(22, 1, buttons=Z),
    In(26, 1, buttons=Z),
]


class DefSdi(Drill):
    id = "universal-sdi"
    name = "SDI out of Multi-Hits"
    goal = "Slide out of the drill before the shine"
    part = "defense"
    cpu = "fox"
    help = ("Take the first hit of the down air, then tap the",
            "stick away over and over to slide out of it.",
            "D-Pad up: guide. D-Pad down: reset.")
    live_marks = True

    def build_reference(self, c):
        """From the first hit, push the stick away from the CPU on every
        other frame, so that each push is a fresh one."""
        return [Ref(SX_MARK_HIT, 1 + 2 * i, 1, -127) for i in range(SX_TAPS)]

    def guide(self, c):
        return ["Every hit freezes you for a moment. Each time",
                "you push the stick to a new position during",
                "that freeze, you move a little: smash DI.",
                "Fox's down air hits over and over, then he",
                "shines. Take the first hit, then tap the",
                "stick away from him again and again (or roll",
                "it between away and diagonal) until you are",
                "out. Holding it still does nothing."]

    def setup(self, c):
        hmn_x = -c.side * (SX_START / 2)
        c.place(hmn_x, hmn_x + c.side * SX_START, False, 20.0, 20.0)
        self.v = dict(wait=attack_wait(c), frame=0, hits=0, start_x=hmn_x,
                      landed=False, shine_frame=0)

    def _verdict(self, c, moved):
        c.measure(self.v["hits"], 1)
        c.report("hits", self.v["hits"])
        c.report("moved", round(moved, 1))

    def think(self, c):
        v, me, cpu = self.v, c.me, c.cpu
        moved = abs(me.pos[0] - v["start_x"])
        if c.phase == SX_WAIT:
            if moved > 4.0:
                c.retry("Stand still\ntake the first hit")
            elif c.timer >= v["wait"]:
                c.set_phase(SX_DRILL)
                v["frame"] = 0
        elif c.phase == SX_DRILL:
            c.script(SX_DAIR, v["frame"])
            v["frame"] += 1
            if c.hmn_hit:
                v["hits"] += 1
                c.mark(SX_MARK_HIT)
            if me.state == GUARD_SET_OFF:
                c.result(False, "Shielded it: take the hit and SDI")
            elif v["frame"] > 12 and not cpu.airborne:
                v["landed"] = True
                if v["hits"] == 0:
                    c.retry("The down air missed\nstand still for it")
                elif c.cpu_state == WAIT:
                    # out of landing lag: shine if the player is still there
                    if dist(c) < SX_SHINE_REACH:
                        c.cpu_press(B, ly=-127)
                        c.set_phase(SX_SHINE)
                        v["shine_frame"] = 0
                    else:
                        self._verdict(c, moved)
                        c.result(True, "Out of the drill! took %d hits"
                                 % v["hits"])
            elif v["frame"] > 120:
                c.retry("Resetting")
        elif c.phase == SX_SHINE:
            v["shine_frame"] += 1
            if c.hmn_hit:
                self._verdict(c, moved)
                c.result(False, "%d hits and the shine: tap away during "
                         "the hits" % v["hits"])
            elif v["shine_frame"] > 8:
                self._verdict(c, moved)
                c.result(True, "The shine missed! took %d hits" % v["hits"])


# ---- fox-escape-pressure ----------------------------------------------------
#
# A CPU Fox pressures the player's shield: short hop, late neutral air,
# L-cancel, wait, shine, jump out of the shine, and again. The wait before
# each shine is the hole in it, set by an option. The player gets out by
# hitting him in that hole (shine out of shield: jump, down+B) or by
# leaving unhit.

EP_OPT_GAP = 0
EP_MARK_HOLE = 1
EP_WAIT_SHIELD, EP_PRESSURE = range(2)
EP_START = 9.0
EP_AERIAL_AT = 13         # airborne frame of the neutral air
EP_SHINE_FRAMES = 7       # frames of shine before he jumps out
EP_AWAY = 32.0            # this far from him, unhit, is out
EP_GAPS = (12, 8, 4)


class DefEscapePressure(Drill):
    id = "fox-escape-pressure"
    name = "Escape Shield Pressure"
    goal = "Find the hole in aerial-into-shine pressure"
    part = "defense"
    cpu = "fox"
    characters = ("fox",)
    options = (
        Option("Gap", ["Wide (12)", "Medium (8)", "Tight (4)"], 0,
               "Frames the CPU leaves between landing and its shine."),
    )
    help = ("Hold shield. Get out in the hole between his",
            "landing and his shine.",
            "D-Pad up: guide. D-Pad down: reset.")
    reference = [
        Ref(0, 0, 900, buttons=R, trigger=140),
        Ref(EP_MARK_HOLE, 1, 1, buttons=X),
        Ref(EP_MARK_HOLE, 4, 1, 0, -127, buttons=B),
    ]
    live_marks = True

    def guide(self, c):
        return ["Aerial, shine, aerial, shine: on your shield",
                "it looks endless, but there is a hole between",
                "his landing and his shine.",
                "Hold shield and watch him land. Then:",
                "shine out of shield (jump, down+B), or roll",
                "or wavedash away.",
                "Too early or too late and you are hit out of",
                "it. The Gap option sets the size of the hole."]

    def setup(self, c):
        hmn_x = -c.side * (EP_START / 2)
        c.place(hmn_x, hmn_x + c.side * EP_START, False, 20.0)
        self.v = dict(air=0, aerial=False, cancel=False, landed=0,
                      was_air=False, shine=0, last_y=0.0)

    def cpu_think(self, c, gap):
        """One frame of the CPU's pressure (ep_Cpu)."""
        v, cpu = self.v, c.cpu
        dx = c.me.pos[0] - cpu.pos[0]
        falling = cpu.pos[1] < v["last_y"]
        v["last_y"] = cpu.pos[1]
        if is_shine(cpu.state):
            v["shine"] += 1
            if v["shine"] == EP_SHINE_FRAMES:
                c.cpu_press(X)        # jump out: the next hop
            return
        v["shine"] = 0
        if cpu.airborne:
            # Off the ground as the jump squat's animation ends: the C
            # Think saw it in the frame before this one, and counted it.
            v["air"] += 2 if v["air"] == 0 else 1
            v["was_air"] = True
            v["landed"] = 0
            if abs(dx) > 6.0:
                c.cpu_press(lx=80 if dx > 0 else -80)  # stay on top of them
            if not v["aerial"] and v["air"] >= EP_AERIAL_AT:
                c.cpu_press(A, lx=0)
                v["aerial"] = True
            elif v["aerial"] and not v["cancel"] and falling and \
                    cpu.pos[1] < 8.0:
                c.cpu_press(Z)
                v["cancel"] = True
            return
        v["air"] = 0
        v["aerial"] = v["cancel"] = False
        if cpu.state != WAIT:
            return                    # jump squat, landing lag
        if not v["was_air"]:
            c.cpu_press(X)            # the first hop
            return
        # Standing as the landing lag's animation ends: the C Think saw it
        # in the frame before this one, and counted it; the mark goes back
        # with it (the engine plays the frame's reference again).
        c.mark(EP_MARK_HOLE, back=1)
        v["landed"] += 2 if v["landed"] == 0 else 1
        if v["landed"] > gap:
            c.cpu_press(B, ly=-127)

    def think(self, c):
        me = c.me
        gap = EP_GAPS[1] if c.is_demo else EP_GAPS[c.opt(EP_OPT_GAP)]
        shielding = GUARD_ON <= me.state <= GUARD_REFLECT
        if c.phase == EP_WAIT_SHIELD:
            if me.state == GUARD and c.timer > 20:
                c.set_phase(EP_PRESSURE)
            elif me.state not in (GUARD, GUARD_ON):
                c.timer = 0
        elif c.phase == EP_PRESSURE:
            self.cpu_think(c, gap)
            if c.hmn_hit or player_grabbed(c):
                c.result(False, "Hit out of your shield: act in the hole, "
                         "not before")
            elif me.state in (SHIELD_BREAK_FLY, SHIELD_BREAK_FALL):
                c.result(False, "Shield broken: do not wait that long")
            elif c.cpu_hit or cpu_grabbed(c):
                c.result(True, "Out: hit him in the hole")
            elif not shielding and dist(c) > EP_AWAY and not me.airborne:
                c.result(True, "Out of the pressure")
            elif c.timer > 900:
                c.result(False, "Still in shield")


# ---- fox-recovery-mixup -----------------------------------------------------
#
# The player starts in the air off the left ledge with a double jump. Marth
# waits by the ledge. He forward smashes a player who comes in at stage
# height, after his reaction time, and a player on the ledge as the ledge
# intangibility runs out (as in fox-ledgedash-attack). Standing on the
# stage unhit is the goal.

RM_OPT_REACTION = 0
RM_PLAYER_OUT = 46.0
RM_PLAYER_UP = 8.0
RM_CPU_IN = 14.0
RM_SWING_X = 34.0         # he swings at a player this close, at his height
RM_SAFE = 30
# defense_escapes.inc.h (fox-ledgedash-attack)
LA_SMASH_LEAD = 8         # he starts this long before the player can be hit
LA_REACTIONS = (20, 14, 9)


def on_ledge(state):
    """lg_OnLedge."""
    return state in (CLIFF_CATCH, CLIFF_WAIT)


class LedgeIntangibility:
    """The frames of ledge intangibility left (lg_Intangible:
    `hd->hurt.intang_frames.ledge`, fp->x1990), which the native build does
    not report, kept from what it does.

    The game gives p_ftCommonData->x49C frames of it on entering CliffWait
    (ftCo_8009A804) and counts it down once a frame in Fighter_procAnim,
    on the ledge or off it. Measured on the native build (Fox, the spec
    hang_too_long): `invulnerable` is seen for state_frames 1 .. 30 of
    CliffWait and not on 31, so x49C is 30 and at the end of the frame
    Python last saw, LEDGE_INTANG - state_frames + 1 are left. The C Think
    runs part-way through the next frame, after that frame's decrement:
    it reads one less (frames())."""
    LEDGE_INTANG = 30

    def __init__(self):
        self.left = 0

    def update(self, c):
        if c.state == CLIFF_WAIT and c.state_frames == 1:
            self.left = self.LEDGE_INTANG
        elif self.left > 0:
            self.left -= 1
        if not c.me.invulnerable:
            self.left = 0

    def frames(self):
        """What `hd->hurt.intang_frames.ledge` reads in the C Think."""
        return max(self.left - 1, 0)


# The states whose own subaction makes the fighter intangible (fp->x1988,
# `hd->hurt.kind_game`), by the frame data's subaction names.
_OWN_INTANG_STATES = {
    "EscapeF": 233, "EscapeB": 234, "EscapeN": 235, "EscapeAir": 236,
    "CliffClimbSlow": 254, "CliffClimbQuick": 255, "CliffAttackSlow": 256,
    "CliffAttackQuick": 257, "CliffEscapeSlow": 258,
    "CliffEscapeQuick": 259, "CliffJumpSlow1": 260, "CliffJumpQuick1": 262,
}
_own_intang = {}


def own_intangible_frames(cid):
    """{state: [(first, last), ...]}: the frames of each state above in
    which the character is intangible by the move itself
    (data/framedata)."""
    if cid not in _own_intang:
        with open(os.path.join(ROOT, "data", "framedata",
                               cid + ".json")) as f:
            moves = json.load(f)["moves"]
        _own_intang[cid] = {
            _OWN_INTANG_STATES[m["subaction"]]: [tuple(r) for r in
                                                 m["intangible"]]
            for m in moves.values()
            if m.get("subaction") in _OWN_INTANG_STATES and
            m.get("intangible")}
    return _own_intang[cid]


def own_intangible(c, ledge):
    """`hd->hurt.kind_game != 0`: intangible by its own move, not by the
    ledge. The native build reports one flag for both (`invulnerable`),
    so while ledge intangibility runs the move's own is read off the frame
    data: the frame the C Think sees is the state's next one."""
    if not c.me.invulnerable:
        return False
    if ledge.frames() <= 0:
        return True
    frame = c.state_frames + 1
    return any(a <= frame <= b for a, b in
               own_intangible_frames(c.s.char).get(c.state, ()))


class DefRecovery(Drill):
    id = "fox-recovery-mixup"
    name = "Recover against an Edgeguard"
    goal = "Get back to the stage past a waiting Marth"
    part = "defense"
    cpu = "marth"
    characters = ("fox",)
    options = (
        Option("CPU Reaction", ["Slow (20)", "Normal (14)", "Fast (9)"], 1,
               "Frames the CPU takes to swing once you are in reach."),
    )
    help = ("Get back to the stage past Marth, who swings at",
            "what he sees coming.",
            "D-Pad up: guide. D-Pad down: reset.")

    def guide(self, c):
        return ["Getting back is a guessing game you can tilt.",
                "Marth swings at what he sees coming.",
                "Illusion (side+B) straight at the stage: fast,",
                "  and the one he expects. Shorten it (B again)",
                "  to stop at the ledge.",
                "Fire Fox (up+B) from below to the ledge.",
                "From the ledge, the ledgedash.",
                "Mix them, and keep your double jump in hand."]

    def setup(self, c):
        self.v = dict(ledge=(0.0, 0.0), seen=0, safe=0, frame=0, swung=0,
                      intang=LedgeIntangibility())
        ledge = c.ledge_pos()
        if ledge is None:
            return
        self.v["ledge"] = ledge
        c.side, c.toward = 1.0, -1.0
        c.place_in_air(c.s.person, ledge[0] - RM_PLAYER_OUT,
                       ledge[1] + RM_PLAYER_UP, 1.0, 40.0)
        c.place_cpu(ledge[0] + RM_CPU_IN, -1.0, 20.0)

    def think(self, c):
        v, me, cpu = self.v, c.me, c.cpu
        intang = v["intang"]
        intang.update(c)
        react = LA_REACTIONS[c.opt(RM_OPT_REACTION)]
        dx = abs(me.pos[0] - cpu.pos[0])
        dy = me.pos[1] - cpu.pos[1]
        hanging = on_ledge(c.state)
        in_reach = not hanging and dx < RM_SWING_X and -6.0 < dy < 22.0
        v["frame"] += 1
        # Marth
        if v["swung"] > 0:
            v["swung"] += 1
            if v["swung"] > 50:
                v["swung"] = 0
        elif hanging:
            v["seen"] = 0
            # once the player has hung for a moment: the intangibility
            # counter is not set yet while the ledge is being caught
            if c.state == CLIFF_WAIT and c.state_frames > 4 and \
                    intang.frames() <= LA_SMASH_LEAD:
                c.cpu_press(cx=-127 if me.pos[0] < cpu.pos[0] else 127)
                v["swung"] = 1
        elif in_reach:
            v["seen"] += 1
            if v["seen"] >= react and not own_intangible(c, intang):
                c.cpu_press(cx=-127 if me.pos[0] < cpu.pos[0] else 127)
                v["swung"] = 1
                v["seen"] = 0
        else:
            v["seen"] = 0

        if not me.airborne and me.pos[0] > v["ledge"][0] and \
                not in_hitstun(me):
            v["safe"] += 1
        else:
            v["safe"] = 0
        if player_dead(c):
            c.result(False, "Did not make it back")
        elif c.hmn_hit or player_grabbed(c):
            c.result(False, "Hit on the way in: he saw that one coming")
        elif c.cpu_hit or cpu_grabbed(c):
            c.result(True, "Back, and hit him!")
        elif v["safe"] > RM_SAFE:
            c.measure(v["frame"], v["frame"])
            c.result(True, "Back on the stage: after %d frames" % v["frame"])
        elif v["frame"] > 900:
            c.result(False, "Out of time")


# ---- universal-wall-tech ----------------------------------------------------
#
# The player starts in the air just outside and below the left ledge, as at
# the end of a low recovery. Marth, further out, forward airs toward the
# stage: the hit sends the player into the stage's side. L or R in the 20
# frames before touching the wall techs it.

WT_HANG, WT_HIT = range(2)
WT_MARK_HIT = 1
WT_PLAYER_OUT = 7.0
WT_PLAYER_DOWN = 30.0
WT_CPU_OUT = 24.0
WT_CPU_DOWN = 28.0
WT_SWING_AT = 2


class DefWallTech(Drill):
    id = "universal-wall-tech"
    name = "Wall Tech"
    goal = "Tech the side of the stage when hit off the ledge"
    part = "defense"
    cpu = "marth"
    help = ("Marth hits you into the side of the stage. Tech",
            "it: L or R as you touch the wall.",
            "D-Pad up: guide. D-Pad down: reset.")
    # Measured in the simulator (2026-11-12): the forward air hits on frame
    # 7 and Fox reaches the wall 20 frames later. A press 4 frames after
    # the hit techs; one frame after it, still in the hit's freeze, does
    # nothing.
    reference = [Ref(WT_MARK_HIT, 4, 1, buttons=R, trigger=140)]
    live_marks = True

    def guide(self, c):
        return ["Hit against the side of the stage you bounce",
                "off it, unless you tech: L or R in the 20",
                "frames before you touch the wall. You stop",
                "dead, and can jump straight back.",
                "You start below the ledge and Marth hits you",
                "into the stage. Press just after the hit's",
                "freeze: a press during it does not count."]

    def setup(self, c):
        self.v = dict(ledge=(0.0, 0.0), hit_frame=0, press=0)
        ledge = c.ledge_pos()
        if ledge is None:
            return
        self.v["ledge"] = ledge
        c.side, c.toward = 1.0, -1.0
        # facing away from the stage, or the player just grabs the ledge
        c.place_in_air(c.s.person, ledge[0] - WT_PLAYER_OUT,
                       ledge[1] - WT_PLAYER_DOWN, -1.0, 60.0)
        c.place_in_air(c.s.cpu_port, ledge[0] - WT_CPU_OUT,
                       ledge[1] - WT_CPU_DOWN, 1.0, 20.0)

    def think(self, c):
        v = self.v
        if c.phase == WT_HANG:
            if c.timer == WT_SWING_AT:
                c.cpu_press(cx=127)   # forward air, toward the stage
            if c.hmn_hit:
                c.mark(WT_MARK_HIT)
                c.set_phase(WT_HIT)
                v["hit_frame"] = 0
            elif c.timer > 60:
                c.retry("The hit missed\nresetting")
        elif c.phase == WT_HIT:
            v["hit_frame"] += 1
            if c.down & (L | R):
                v["press"] = v["hit_frame"]
            c.report("state", c.state)
            if c.state in (PASSIVE_WALL, PASSIVE_WALL_JUMP):
                c.measure(v["hit_frame"], v["hit_frame"])
                c.result(True, "Wall tech! %d frames after the hit"
                         % v["hit_frame"])
            elif c.state == FLY_REFLECT_WALL:
                c.report("press", v["press"])
                c.result(False, "Bounced: pressed %d frames after the hit, "
                         "in its freeze" % v["press"] if v["press"] else
                         "Bounced off the wall: L or R after you are hit")
            elif player_dead(c) or v["hit_frame"] > 150:
                c.result(False, "Never reached the wall: hold the stick "
                         "toward it")


DRILLS = [DefSdi, DefEscapePressure, DefWallTech, DefRecovery]
