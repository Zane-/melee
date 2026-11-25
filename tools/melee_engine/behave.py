"""Behaviours: what the opponent does over time
(docs/ai/opponent-vocabulary.md, layer 3), each until a condition (its
step's `until`), a time (`for` frames) or its own end (an attack's contact
and recovery, a punish over).

A behaviour gives the opponent's pad each frame (`pad(st)`, a raw pad:
buttons, lx, ly, cx, cy, lt, rt) and says when it is over (`done`). Its
`plan(st, k)` is what it will press over the next k frames, for the
searches that ask what the player can do to it (sense.py's ranges).

Bodies (pads planned some frames ahead): `hold`, `footsies` (dash dances,
walks, stops, crouches in a band of distances: drill.Footsies), `retreat`,
`play`. Decisions the engine searches: `approach` (drill.EngineOpponent
held to a contract, `Commit` below), `move`, `punish`, `pressure`,
`chase`, `chain_grab` (`Driven`: each move chosen as the last ends). Every
decision is for a frame still to come, `lead` frames on, the pads until
then as the search's pre-roll: thought out in a forked copy of the game
while a person plays (fork.InFork), in the game itself headless (Here),
through the thinker every behaviour shares.

    ctx = Ctx(think, port=1, target=0, sense=Sense(1, 0), rng=Random(7))
    b = make(ctx, {"do": "footsies", "range": "outside"})
    raw = b.pad(n.state())     # once a frame, before the frame is played
"""
import math
import os
import random

from melee_engine import sense as S
from melee_engine.contracts import Answer, Contract, lands, searched
from melee_engine.drill import (CROUCH, NONE, SHIELD, EngineOpponent,
                                Footsies as Body, Hold as HoldBody, expect,
                                pick, press_at)
from melee_engine.search import player, preroll, search

# ---- the moves a script may name --------------------------------------------

# the engine's macros today (src/host/engine.c, "engine macros")
MACROS = tuple((
    "wait walk_in walk_out dash_in dash_out jab ftilt utilt dtilt fsmash "
    "usmash dsmash grab dash_attack shield down_b neutral_b side_b up_b "
    "wavedash_in wavedash_out hop_in hop_out hop jump_in jump jump_out "
    "sh_nair_in sh_nair sh_fair_in sh_fair sh_bair_in sh_bair sh_uair_in "
    "sh_uair sh_dair_in sh_dair fh_nair_in fh_fair_in fh_bair_in fh_uair_in "
    "fh_dair_in nair_in nair nair_out fair_in fair fair_out bair_in bair "
    "bair_out uair_in uair uair_out dair_in dair dair_out drift_in drift_out "
    "drift_none fastfall dj_in dj_out oos_grab oos_usmash oos_jump spotdodge "
    "roll_in roll_out oos_down_b oos_up_b shield_hold shield_drop fthrow "
    "bthrow uthrow dthrow tech tech_in tech_out getup getup_attack getup_in "
    "getup_out ledge_getup ledge_roll ledge_jump ledge_attack ledge_drop "
    "up_b_in up_b_out airdodge_in airdodge_out airdodge_up airdodge_down"
).split())
# the moves the scope adds (opponent-vocabulary.md, layer 1: being built
# beside this, in build/native-moves until the shared build has them); a
# script may name them now, and a search finds them once they are in. They
# are opt-in: a search offers them only where a prefix names them.
PIVOTS = ("jab", "ftilt", "fsmash", "utilt", "usmash", "dtilt", "dsmash",
          "grab")
PLANNED = tuple("pivot_%s%s" % (a, long) for a in PIVOTS
                for long in ("", "_long")) + (
    "dash_grab", "jc_grab", "jc_usmash", "boost_grab", "dash_dance",
    "crouch", "platform_drop", "waveland_in", "waveland_out", "waveland",
    "run_attack") + \
    tuple("sh_%s_out" % a for a in ("nair", "fair", "bair", "uair", "dair"))
THROWS = ("fthrow", "bthrow", "uthrow", "dthrow")


def family(names):
    """The attack a line ends with, as a person names it: the line's last
    move without its hop, drift, pivot or jump cancel ("hold_in:3+sh_nair_in"
    and "nair_out" are "nair", "pivot_fsmash_long" "fsmash", a dash or boost
    grab "grab", "dash_attack" itself)."""
    m = names.split("+")[-1] if names else ""
    for pre in ("sh_", "fh_", "pivot_", "jc_"):
        if m.startswith(pre):
            m = m[len(pre):]
    for suf in ("_in", "_out", "_long"):
        if m.endswith(suf):
            m = m[:-len(suf)]
    return "grab" if m in ("dash_grab", "boost_grab") else m


def families(prefixes):
    """The families a "moves" list names, in its order, each with the
    macros it names in it (today's and the scope's): {"nair": "sh_nair_in,
    sh_nair", "dash_attack": "dash_attack", ...}."""
    out = {}
    names = MACROS + PLANNED
    for p in prefixes.split(","):
        for m in names:
            if p and m.startswith(p):
                f = family(m)
                if m not in out.setdefault(f, []):
                    out[f].append(m)
    return {f: ",".join(ms) for f, ms in out.items()}


def unknown_moves(prefixes):
    """The prefixes of a "moves" list that name no move (today's or the
    scope's)."""
    names = MACROS + PLANNED
    return [p for p in prefixes.split(",")
            if not p or not any(m.startswith(p) for m in names)]


# ---- what the behaviours of one opponent share ------------------------------

class Ctx:
    """`think`: where decisions are made (drill.Here, fork.InFork); `sense`:
    the conditions (sense.Sense); `rng`: the script's (each behaviour draws
    its own from it, in order: the same seed, the same choices); `react`:
    the frames the opponent takes to see what the player does; `half`: the
    stage's half width; `memory`: what one behaviour learns and the next
    starts from (the player's reach)."""

    def __init__(self, think, port, target, sense, rng=None, react=S.REACT,
                 half=85.0, temperature=6.0):
        self.think, self.port, self.target = think, port, target
        self.sense = sense
        self.rng = rng or random.Random(0)
        self.react = react
        self.half = half
        self.temperature = temperature
        self.memory = {}
        self.their = NONE          # the player's raw pad this frame

    @property
    def frames(self):
        return self.sense.frames

    @property
    def cache(self):
        return self.sense.cache


def toward(st, port, target):
    me, them = st["p"][port], st["p"][target]
    return 1 if them["x"] >= me["x"] else -1


def distance(st, port, target):
    me, them = st["p"][port], st["p"][target]
    return abs(them["x"] - me["x"])


def shielding(raw):
    """A raw pad that holds a shield (R or L, or a trigger pressed)."""
    return bool(raw[0] & 0x60) or max(raw[5], raw[6]) >= 43


class Behaviour:
    name = None

    def __init__(self, ctx, spec):
        self.ctx, self.spec = ctx, spec
        self.rng = random.Random(ctx.rng.random())
        self.frame = 0
        self.done = False
        self.last = NONE
        self.log = []

    def pad(self, st):
        raw = tuple(self.step(st))
        self.last = raw
        self.frame += 1
        return raw

    def step(self, st):
        return NONE

    def plan(self, st, k):
        """What it will press over the next `k` frames (raw pads)."""
        return [self.last] * k

    def stop(self):
        """It is over (its condition, its time): what it waits for is
        dropped."""


# ---- bodies -----------------------------------------------------------------

class Hold(Behaviour):
    """Stands, shields or crouches (`pad`), or holds the control stick
    (`stick`: [toward the player, up], each -1 to 1: its DI through a
    throw or a hit, away from the player with [-1, 0]). `near`: over when
    it is within that many units of the player, by where both are now:
    its own spacing as it walks in (a step's `until` sees the player its
    reaction time late, and a walk ended by it overshoots by the frames it
    is late). `far`: over when it is at least that many units away, the
    same way: a step back, the stick away, before it comes in."""
    name = "hold"
    PADS = {"stand": NONE, "shield": SHIELD, "crouch": CROUCH}

    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        self.raw = self.PADS[spec.get("pad", "stand")]
        self.stick = spec.get("stick")
        self.near = spec.get("near")
        self.far = spec.get("far")

    def step(self, st):
        if self.near is not None or self.far is not None:
            me, them = st["p"][self.ctx.port], st["p"][self.ctx.target]
            gap = abs(them["x"] - me["x"]) if me is not None and \
                them is not None else None
            if gap is not None and (
                    self.near is not None and gap <= self.near or
                    self.far is not None and gap >= self.far):
                self.done = True
                return self.raw
        if self.stick is None:
            return self.raw
        b, _, _, cx, cy, lt, rt = self.raw
        way = toward(st, self.ctx.port, self.ctx.target) \
            if st["p"][self.ctx.port] is not None and \
            st["p"][self.ctx.target] is not None else 1
        return (b, int(round(127 * self.stick[0])) * way,
                int(round(127 * self.stick[1])), cx, cy, lt, rt)

    def plan(self, st, k):
        return [self.step(st)] * k


class Press(Behaviour):
    """Plays inputs by frame (`inputs`: [{"press": "A", "frame": N, "hold":
    H}, {"stick": [toward the player, up], ...}, {"cstick": [...], ...}],
    frame 1 this step's first): an attack played the same way every time,
    from where it stands (a drill measured against that one hit), or one
    the engine has no move for. Over after the last of them."""
    name = "press"
    BUTTONS = {"A": 0x100, "B": 0x200, "X": 0x400, "Y": 0x800, "Z": 0x10}

    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        self.inputs = spec["inputs"]
        self.end = max(i["frame"] + i.get("hold", 1) - 1
                       for i in self.inputs)

    def step(self, st):
        n = self.frame + 1
        way = toward(st, self.ctx.port, self.ctx.target) \
            if st["p"][self.ctx.port] is not None and \
            st["p"][self.ctx.target] is not None else 1
        b = lx = ly = cx = cy = 0
        for i in self.inputs:
            if not i["frame"] <= n < i["frame"] + i.get("hold", 1):
                continue
            if "press" in i:
                b |= self.BUTTONS[i["press"]]
            elif "stick" in i:
                lx = self._axis(i["stick"][0]) * way
                ly = self._axis(i["stick"][1])
            else:
                cx = self._axis(i["cstick"][0]) * way
                cy = self._axis(i["cstick"][1])
        if n >= self.end:
            self.done = True
        return (b, lx, ly, cx, cy, 0, 0)

    @staticmethod
    def _axis(part):
        """A stick value of a drill's inputs (1: all the way) as the pad's
        (80: all the way), as the course runtime plays an opponent's
        "inputs" (engine.cpu_axis): 0.63 is 50, a tilt; 80 would be a
        smash."""
        v = int(round(127 * part))
        return 0 if v == 0 else int(round(
            abs(v) * 80.0 / (127.0 if v > 0 else 128.0))) * (1 if v > 0
                                                             else -1)

    def plan(self, st, k):
        return [NONE] * k


class Jump(Behaviour):
    """Presses jump now, the stick held (`stick`: [toward the player, up],
    [-1, 0] by default: away): a jump from the ground, a double jump in the
    air, on this frame exactly (a body, not a search: out of hitstun the
    first frame it can). Over two frames later."""
    name = "jump"
    X = 0x400

    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        self.stick = spec.get("stick", [-1, 0])

    def step(self, st):
        way = toward(st, self.ctx.port, self.ctx.target) \
            if st["p"][self.ctx.port] is not None and \
            st["p"][self.ctx.target] is not None else 1
        if self.frame >= 2:
            self.done = True
        return (self.X if self.frame < 2 else 0,
                int(round(127 * self.stick[0])) * way,
                int(round(127 * self.stick[1])), 0, 0, 0, 0)

    def plan(self, st, k):
        return [NONE] * k


class Tech(Behaviour):
    """Knocked off its feet, it techs the floor (`option`: "in_place",
    "toward" the player, "away", or "none": it misses the tech, lies there
    `wait` frames ([LO, HI], drawn) and gets up by `getup`: "stand",
    "toward", "away" or "attack"; either may be "mix": drawn when it is
    hit). A body, not a search: L or R is pressed once, when its flight
    would meet the floor within REACH frames (its height, its fall speed
    with the knockback's, and the gravity seen between two frames; the
    main floor at height 0: not a platform), with the stick held for the
    roll; a press sooner than 20 frames before the floor is no tech, and a
    second press within 40 is none either. A hit that puts it on the floor
    as its freeze ends (Fox's shine) is teched in the freeze's last two
    frames. Over when it stands and can act again."""
    name = "tech"
    R = 0x20
    A = 0x100
    OPTIONS = ("in_place", "toward", "away", "none", "mix")
    GETUPS = ("stand", "toward", "away", "attack", "mix")
    REACH = 12          # frames ahead the floor is looked for
    # frames of the hit's freeze left when it may press: measured (Fox's
    # shine on Falco, who meets the floor on the first frame after it), a
    # press with 1 or 2 left techs, with 3 or more it does not
    EARLY = 2
    FLOOR = 0.0
    DAMAGE = (75, 91)
    LYING = (184, 192)      # DownWait, face up and face down

    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        self.option = spec.get("option", "mix")
        self.getup = spec.get("getup", "mix")
        lo, hi = spec.get("wait", [10, 40])
        self.wait = self.rng.randint(int(lo), int(hi))
        if self.option == "mix":
            self.option = self.rng.choice(self.OPTIONS[:4])
        if self.getup == "mix":
            self.getup = self.rng.choice(self.GETUPS[:4])
        self.pressed = None     # the frame L or R was pressed
        self.vy = None
        self.down_at = None
        self.up = False
        self.seen = False       # it has been in the air, hit

    def _stick(self, st, way):
        t = toward(st, self.ctx.port, self.ctx.target)
        return {"toward": 127 * t, "away": -127 * t}.get(way, 0)

    def _floor_in(self, me):
        """Frames until its flight meets the floor, within REACH (None:
        not within)."""
        vy, self.vy = self.vy, me["vy"]
        g = max((vy - me["vy"]) if vy is not None else 0.1, 0.05)
        # (kvy: the knockback's own speed, there from the hit on, through
        # its freeze: a hit that sends it up is not a floor to tech yet)
        y, v = me["y"] - self.FLOOR, me["vy"] + me.get("kvy", 0.0)
        for k in range(1, self.REACH + 1):
            v -= g
            y += v
            if y <= 0.0:
                return k
        return None

    def step(self, st):
        me = st["p"][self.ctx.port]
        if me is None:
            return NONE
        state = me["state"]
        hurt = self.DAMAGE[0] <= state <= self.DAMAGE[1] or \
            state == S.TUMBLE
        if hurt and me["air"]:
            self.seen = True
        if self.down_at is not None and state not in self.LYING:
            self.up = True          # (its getup has begun)
        if self.up or (self.seen and state in S.TECHS):
            # teching, or getting up: over when it can act
            self.up = True
            if S.free(me):
                self.done = True
            return NONE
        if state in S.DOWN:
            # on the floor: its getup, `wait` frames after it lies still
            # (DownWait: the bounce before it takes no input)
            if state not in self.LYING:
                return NONE
            if self.down_at is None:
                self.down_at = self.frame
            if self.frame - self.down_at >= self.wait:
                if self.getup == "attack":
                    return (self.A, 0, 0, 0, 0, 0, 0)
                if self.getup == "stand":
                    return (0, 0, 127, 0, 0, 0, 0)
                return (0, self._stick(st, self.getup), 0, 0, 0, 0, 0)
            return NONE
        if not (hurt and me["air"]) or (me.get("hitlag") or 0) > self.EARLY:
            self.vy = None
            if self.seen and S.free(me) and not me["air"]:
                self.done = True        # (it landed on its feet)
            return NONE
        lx = self._stick(st, self.option)
        if self.option == "none":
            return NONE
        if self.pressed is None:
            if self._floor_in(me) is None:
                return (0, lx, 0, 0, 0, 0, 0)
            self.pressed = self.frame
            return (self.R, lx, 0, 0, 0, 0, 255)
        # (the press was one frame's; the stick stays for the roll)
        return (0, lx, 0, 0, 0, 0, 0)

    def plan(self, st, k):
        return [NONE] * k


class Oos(Behaviour):
    """Holds its shield and answers every hit on it: `option` on the first
    frame its shield stun is over ("grab": a shield grab, A with the
    shield held). The frame is found by playing the stun ahead in the game
    from the hit (the shield held, the player holding what they hold): the
    press comes on it exactly, as from a player who has the timing. A hit
    on the shield before that asks again. If the answer is not back in
    time (thinking beside a live game), the press comes on the first frame
    it is seen out of the stun. Over when its answer has been played and it
    can act again, or it has been hit or grabbed out of its shield: a
    script loops it."""
    name = "oos"
    kind = "oos"
    OPTIONS = ("grab",)
    A = 0x100
    LOST = 0.5          # health a shield loses in a frame only to a hit
    MOST = 40           # frames of stun played ahead

    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        self.health = None
        self.hit_at = None      # the frame the last hit on it was seen
        self.tag = None
        self.asked = 0
        self.press_at = None    # the frame of this behaviour's to press on
        self.out = False

    def _ask(self):
        port, target, most = self.ctx.port, self.ctx.target, self.MOST

        def fn(n):
            from melee_actor.ahead import look
            out = look(n, port, target, [(most, raw_pad(SHIELD))], stop=0)
            for i, row in enumerate(out.rows):
                if row.a_state in (S.GUARD, S.GUARD_ON, S.GUARD_REFLECT) \
                        and row.a_hitlag <= 0:
                    return dict(k=i + 1, ms=out.ms)
                if row.a_state not in S.SHIELDING:
                    break
            return dict(k=None, ms=out.ms)
        self.stop()
        self.asked += 1
        self.tag = ("oos", id(self), self.asked)
        self.press_at = None
        self.ctx.think.submit(self.tag, fn, self.kind)

    def step(self, st):
        me = st["p"][self.ctx.port]
        if me is None:
            return SHIELD
        if self.out:
            if S.free(me) and me["state"] not in S.SHIELDING:
                self.done = True
            return NONE
        health, self.health = self.health, me["shield"]
        if me["state"] in S.CATCHING or me["state"] in S.CAPTURED or \
                75 <= me["state"] <= 91:
            # its grab is out, or it was grabbed or hit out of the shield
            self.stop()
            self.out = True
            return NONE
        if health is not None and health - me["shield"] > self.LOST:
            self.hit_at = self.frame
            self._ask()
        if self.hit_at is None:
            return SHIELD
        think = self.ctx.think
        if self.tag is not None and think.ready(self.tag):
            out = think.result(self.tag)
            self.tag = None
            if out is not None and out.get("k"):
                # frame k from the one asked on, 1 the next: this step's
                # pad is that frame's when self.frame == hit_at + k - 1
                self.press_at = self.hit_at + out["k"] - 1
        late = self.press_at is None and self.tag is None or \
            self.press_at is not None and self.frame > self.press_at
        if self.frame == self.press_at or (
                (late or self.tag is not None) and
                me["state"] in (S.GUARD, S.GUARD_ON, S.GUARD_REFLECT) and
                not me.get("hitlag")):
            b, lx, ly, cx, cy, lt, rt = SHIELD
            return (b | self.A, lx, ly, cx, cy, lt, rt)
        return SHIELD

    def plan(self, st, k):
        return [SHIELD] * k

    def stop(self):
        if self.tag is not None:
            self.ctx.think.forget(self.tag)
            self.tag = None


class Footsies(Behaviour):
    """Dash dances, walks, stops and crouches in a band of distances from
    the player (drill.Footsies): `range` [LO, HI] in units; "outside", just
    out of the player's range; "edge", at the edge of its own.

    "outside": every `cache` frames the player's side is searched (sense's
    "guard": can they hit me within `frames` + `cache` frames, as I plan to
    move?), and a plan that would take it into their range is dropped for
    a dash back before it is played. The band follows the reach found: it
    rises to a distance found in range and sinks slowly while nothing is,
    so the opponent hovers at the edge of the player's range ("their
    reach", kept for the next behaviour). "edge": the same with its own
    range (sense's "my"): in range at a distance, the reach is at least
    that; out of it, less."""
    name = "footsies"
    MARGIN = 3.0          # units outside the reach found
    WIDTH = 8.0
    SINK = 0.25           # units the reach sinks each look that finds none
    LEAST = 8.0

    def __init__(self, ctx, spec, margin=None, width=None):
        super().__init__(ctx, spec)
        r = spec.get("range", "outside")
        self.mode = r if isinstance(r, str) else "band"
        self.margin = self.MARGIN if margin is None else margin
        self.width = self.WIDTH if width is None else width
        band = tuple(r) if self.mode == "band" else (30.0, 45.0)
        self.body = Body(ctx.port, ctx.target, band=band, rng=self.rng,
                         half=ctx.half, crouch=spec.get("crouch", True))
        self.body.keep = self.mode == "band"
        if self.mode == "outside":
            ctx.sense.wants.add("guard")
        elif self.mode == "edge":
            ctx.sense.wants.add("my")
        self.looked = None
        self.backs = 0            # plans dropped for a dash back
        self.unchecked = False    # a segment planned and not looked at
        self._band()

    def _band(self):
        m = self.ctx.memory
        if self.mode == "outside":
            r = m.setdefault("their_reach", 30.0)
            self.body.band = (r + self.margin, r + self.margin + self.width)
        elif self.mode == "edge":
            r = m.setdefault("my_reach", 25.0)
            self.body.band = (max(2.0, r - 4.0), r + 3.0)

    def _back(self, st):
        """Away from the player now, facing them again at its end: the
        body's retreat (a wavedash out, a dash away and a pivot, the dash
        it is in turned away; standing still with the ledge behind),
        queued in place of its plan."""
        return self.body.retreat(st)

    def _outside(self, st):
        sense = self.ctx.sense
        m = self.ctx.memory
        if self.unchecked and (sense.latest("guard") is None or
                               sense.latest("guard")[0] < sense.frame):
            # a segment planned since the last look: looked at before it
            # is played
            sense.ask(self.plan(st, self.ctx.frames + self.ctx.cache),
                      force=True)
        self.unchecked = False
        for _ in range(3):
            got = sense.detail.get("guard")
            if got is None or got[0] == self.looked:
                return
            self.looked = got[0]
            gap = got[1].get("gap")
            if gap is None:
                gap = distance(st, self.ctx.port, self.ctx.target)
            if not got[1]["v"]:
                # out of their range all the way: the reach is less than
                # the closest the plan comes; and sinks a little (it looks
                # closer in, next time)
                m["their_reach"] = max(self.LEAST, min(
                    m["their_reach"] - self.SINK, gap - 0.5))
                self._band()
                return
            # in their range, as planned (at least where the plan comes
            # closest): a dash back instead, looked at at once
            m["their_reach"] = max(m["their_reach"], gap)
            self._band()
            self._back(st)
            self.backs += 1
            sense.ask(self.plan(st, self.ctx.frames + self.ctx.cache),
                      force=True)

    def _edge(self, st):
        got = self.ctx.sense.latest("my")
        if got is None or got == self.looked:
            return
        self.looked = got
        d = distance(st, self.ctx.port, self.ctx.target)
        m = self.ctx.memory
        if got[1]:
            m["my_reach"] = max(m["my_reach"], d)
        else:
            m["my_reach"] = max(self.LEAST, min(m["my_reach"], d - 0.5))
        self._band()

    def step(self, st):
        self._segment(st)
        if self.mode == "outside":
            self._outside(st)
        elif self.mode == "edge":
            self._edge(st)
        return self.body.next(st)

    def _segment(self, st):
        """A phrase planned when the last runs out (the body plans each
        from where its model has the fighter at the queue's end, so two
        dashes the same way no longer run it off the stage)."""
        if not self.body.queue:
            self.body.extend(st)
            self.unchecked = True

    def plan(self, st, k):
        n = len(self.body.queue)
        out = self.body.ahead(st, k)
        if len(self.body.queue) > n:
            self.unchecked = True     # a phrase planned: looked at first
        return out


class Retreat(Footsies):
    """Out of the player's range and staying there: "outside", further."""
    name = "retreat"

    def __init__(self, ctx, spec):
        super().__init__(ctx, dict(spec, range="outside"), margin=12.0,
                         width=18.0)


class Play(Footsies):
    """Moving as a person does. First version: footsies in a wide band (the
    slippi-ai body, human.ModelBody, is not wired into scripts yet)."""
    name = "play"

    def __init__(self, ctx, spec):
        super().__init__(ctx, dict(spec, range=[25.0, 60.0]))


# ---- committing: an approach held to a contract -----------------------------

LANDS = {"hit": ("hit", "grab"), "shield": ("shield",),
         "any": ("hit", "shield", "grab")}


def raw_pad(raw):
    """A raw pad as Native.pad's arguments (for a lookahead's plan)."""
    from melee_engine.opponent import raw_to_pad
    return raw_to_pad(raw)


def stun_over(n, port, target, raws, most=40, clear=0, single=False):
    """Where `port` plays `raws` against a shielding `target` (holding its
    pad), the first frame (counted from now, 1 the first) the target can
    act out of the shield after the first hit on it; None if none hits
    it. On that frame shield stun's animation ends into the shield and the
    frame's input is read there (Fighter_procAnim runs before
    Fighter_procInput): an answer holds the shield the frames before it
    and is pressed on it. `clear`: None too if the shield, still held, is
    hit again in the `clear` frames from that one (a multi-hit attack's
    next hit: an answer pressed late would meet it in the shield).
    `single`: None too if the shield is hit a second time before its stun
    is over (an attack that keeps it in stun hit after hit: by the stun's
    end it has pushed the two apart, and what was promised of the first
    hit no longer holds)."""
    from melee_actor.ahead import compress, look
    plan = compress([raw_pad(r) for r in raws]) + [(most, raw_pad(NONE))]
    out = look(n, port, target, plan, stop=0)
    hit = None
    for i, row in enumerate(out.rows):
        if hit is None:
            if row.t_hitlag > 0 and row.t_state in S.SHIELDING:
                hit = i
            continue
        if single and row.t_state in S.SHIELDING and \
                row.t_hitlag > out.rows[i - 1].t_hitlag:
            return None
        if row.t_state in (S.GUARD, S.GUARD_ON) and row.t_hitlag <= 0:
            if any(r.t_hitlag > 0 and r.t_state in S.SHIELDING
                   for r in out.rows[i + 1:i + clear]):
                return None
            return i + 1
        if row.t_state not in S.SHIELDING:
            return None
    return None


class Commit(Contract):
    """An approach's contract: one of `moves` (engine macros by name
    prefix) pressed after the stick is held K frames (still, toward,
    walking toward), the timing scan finding where it lands (`kinds`) on
    the player: a shielding player as shielding on, any other as stopping
    (aimed at where they are: one who goes on is followed). With `answer`
    (move prefixes) only an option the player can answer, within `within`
    frames of the contact, is committed to: searched from their side
    (contracts.Answer) before it commits, a shielding player out of the
    shield as soon as its stun is over, any other no sooner than their
    reaction time after the commitment. `front`: only a line that stays on
    the side of the player it came from (the engine's front=: through its
    move's end and the frame the answer would hit, `within`'s frames out of
    the shield; never a cross-up or an attack that overshoots through the
    shield).

    `pick`: "variety" draws the families into a queue (by `weights` and
    what each came to, the last `AVOID` in `recent`, the families attacked
    with, at its end: the script's memory, kept from one attempt to the
    next), each look searching the next `PER_LOOK` of them, their moves
    alone; in the queue's order, two lines of each by the softmax, the
    first answered taken; not patient (`wide`), every move, the families
    that land in a drawn order. "best": one of the best lines of every
    move by the softmax over their scores."""

    sees_commitments = False
    AVOID = 2             # the last families attacked with: drawn last
    PER_LOOK = 3          # families a look searches
    SHARE = 8             # the attacks a family's share is counted over
    CAP = 2               # times in them after which it waits, if patient

    def __init__(self, moves, kinds=LANDS["any"], answer=None, within=15,
                 near=50, trial=30, front=False, pick="best", recent=None,
                 weights=None, tried=None, one_hit=None, late=None):
        # (the answer out of the shield must also hit pressed `late`
        # frames after the first it can be: as late as a drill lets it)
        self.late = late or 0
        # (only an attack that hits a shield once: none again before its
        # stun is over, nor in `one_hit` frames from the first the player
        # can act on)
        self.one_hit = one_hit
        self.moves = moves
        self.kinds = kinds
        self.front = within if front else 0
        self.pick = pick
        self.groups = families(moves)
        self.recent = recent if recent is not None else []
        self.weights = dict(weights or {})
        # each family's [answered, looks it landed unanswered], kept as
        # `recent` is: a family never answered is drawn less and less
        self.tried = tried if tried is not None else {}
        self.queue = []           # the families the next looks search
        self.answer = None
        if answer:
            self.answer = Answer(answer, holds="none,walk_out,out,walk_in",
                                 near=45, trial=20, window=400)
        self.within = within
        self.near, self.trial = near, trial
        # a line found answerable stays that line while the player does
        # what it assumed (the game it foresaw is then the game played);
        # when they do something else, it reacts (EngineOpponent: a line
        # checked again, kept, replaced by another answered one, or given
        # up before its press)
        self.tracks = answer is None
        self.reacts = answer is not None

    def _their(self, my_pad, frames):
        if shielding(my_pad):
            return [(240, tuple(my_pad))]
        return expect(my_pad, min(frames, 3))

    def assumes(self, my_pad, k, ahead):
        """What `_their` assumed (`ahead`: the frames the decision was
        asked ahead, its pre-roll): a shield held; else the pad for a few
        frames, then let go."""
        if shielding(my_pad) or k < min(ahead, 3):
            return tuple(my_pad)
        return NONE

    def _avoid(self):
        """The families drawn last: the last one or two attacked with
        (fewer when the list has few)."""
        k = min(self.AVOID, len(self.groups) - 1)
        return set(self.recent[-k:]) if k > 0 else set()

    def _weight(self, f):
        """A family's draw weight: the step's (1 by default), divided by
        one more than the times it was attacked with in the last 8 (a dash
        attack, which lands from anywhere, would come out most: it is
        searched later), and halved for each look it landed and was not
        answered (to a sixteenth) until it has been answered once (an up
        tilt the frame-4 shine never answers is seldom searched first
        again; Peach's forward air, answered from 12 to 20 units,
        stays)."""
        answered, unanswered = self.tried.get(f, (0, 0))
        w = float(self.weights.get(f, 1.0)) / (
            1 + self.recent[-self.SHARE:].count(f))
        return w if answered > 0 else w * 0.5 ** min(unanswered, 4)

    def _note(self, f, answered):
        t = self.tried.setdefault(f, [0, 0])
        t[0 if answered else 1] += 1

    def _order(self, choices, rng):
        """`choices` in the order they are tried: drawn one by one by
        weight, the last attacked with after all the others."""
        avoid = self._avoid()
        out = []
        for part in ([f for f in choices if f not in avoid],
                     [f for f in choices if f in avoid]):
            while part:
                f = rng.choices(part, weights=[self._weight(x)
                                               for x in part])[0]
                out.append(f)
                part.remove(f)
        return out

    def _capped(self, f):
        """Attacked with CAP times in the last SHARE: while patient, not
        searched (a dash attack, which lands and is answered from
        anywhere, would otherwise be most of them)."""
        return self.recent[-self.SHARE:].count(f) >= self.CAP

    def _next(self, rng, wide=False):
        """The families this look searches: the next `PER_LOOK` of the
        queue, drawn again (`_order`) when it runs short; patient, without
        the capped ones (unless every one is)."""
        live = [f for f in self.groups if self.weights.get(f, 1.0) > 0]
        if not wide:
            live = [f for f in live if not self._capped(f)] or live
            self.queue = [f for f in self.queue if f in live]
        if len(self.queue) < self.PER_LOOK or \
                (wide and any(f not in self.queue for f in live)):
            self.queue += [f for f in self._order(live, rng)
                           if f not in self.queue]
        out, self.queue = self.queue[:self.PER_LOOK], \
            self.queue[self.PER_LOOK:]
        return out

    def search(self, n, port, target, pre, their, holds, enough=6,
               then=None):
        if pre:
            preroll(n, pre)
        # (norun: a held dash stays a dash, never a run turned round past
        # the player or to the ledge: engine.c)
        # (front: only a line on the front of the shield, engine.c)
        kw = dict(front=self.front) if self.front else {}
        r = searched(n, port, target, their, len(pre) + 50,
                     then=then or self.moves,
                     scan=2, hold=holds, contact=40, trial=self.trial,
                     near=self.near, enough=enough, norun=1, **kw)
        return [l for l in r.lines if l.contact in self.kinds and
                l.taken == 0], r

    TRIES = 4             # lines whose answer is looked for, each look

    def find(self, n, port, target, pre, my_pad, rng, wide=False,
             temperature=6.0, reaction=15):
        if self.pick == "variety" and len(self.groups) > 1:
            return self._find_variety(n, port, target, pre, my_pad, rng,
                                      wide, temperature, reaction)
        # (standing still and pressing later lands only close in: from
        # further it is a scan of every frame for nothing)
        close = distance(n.state(), port, target) <= 30
        if wide:
            holds = "none,in,walk_in" if close else "in,walk_in"
        else:
            holds = rng.choice(("in", "none", "walk_in", "in,none")
                               if close else ("in", "walk_in", "in,walk_in"))
        their = self._their(my_pad, len(pre))
        found, r = self.search(n, port, target, pre, their, holds)
        if not found:
            return dict(ok=False, why="lands nowhere", ms=r.ms)
        if self.answer is None:
            line = pick(found[:12], temperature, rng)
            return dict(ok=True, line=line, pads=line.raw(),
                        press=press_at(line), ms=r.ms, answer=None)
        # with an answer: the lines in a softmax's order (drawn without
        # putting back), the first few whose answer is looked for, the
        # first answered taken
        ms = r.ms
        left = list(found[:12])
        for _ in range(min(self.TRIES, len(left))):
            line = pick(left, temperature, rng)
            left.remove(line)
            got, ams = self._answered(n, port, target, pre, my_pad, line,
                                      reaction)
            ms += ams
            if got is not None:
                return dict(ok=True, line=line, pads=line.raw(),
                            press=press_at(line), ms=ms, answer=got[0],
                            answer_line=got[1])
        return dict(ok=False, why="no answer", ms=ms, line=line)

    def _find_variety(self, n, port, target, pre, my_pad, rng, wide,
                      temperature, reaction):
        """find, the families first: the next `PER_LOOK` of the queue
        searched, their moves alone, in the queue's order (patient, the
        capped left out); in each, two of its lines by the softmax, the
        first the contract answers taken (TRIES + 2 looked at in all). The
        holds as find's: one kind a look drawn, every kind once not patient
        (a look searching three families with every hold took 750 ms in a
        fork of the game). (Every move a look, the families drawn among
        those found, was quick, but the scan finds lines in its own order
        and stops at `enough`: a dash attack from far is found first,
        Sheik's tilts, a walk in away, never.)"""
        close = distance(n.state(), port, target) <= 30
        if wide:
            holds = "none,in,walk_in" if close else "in,walk_in"
        else:
            holds = rng.choice(("in", "none", "walk_in", "in,none")
                               if close else ("in", "walk_in", "in,walk_in"))
        their = self._their(my_pad, len(pre))
        fams = self._next(rng, wide)
        found, r = self.search(n, port, target, pre, their, holds,
                               then=",".join(self.groups[f] for f in fams))
        ms = r.ms
        by = {}
        for l in found:
            by.setdefault(family(l.names), []).append(l)
        order = [f for f in fams if by.get(f)]
        if not order:
            return dict(ok=False, why="lands nowhere", ms=ms)
        tries, line = 0, None
        for f in order:
            left = list(by[f][:12])
            for _ in range(min(2, len(left))):
                if tries >= self.TRIES + 2:
                    break
                line = pick(left, temperature, rng)
                left.remove(line)
                tries += 1
                if self.answer is None:
                    got = (None, None)
                else:
                    got, ams = self._answered(n, port, target, pre, my_pad,
                                              line, reaction)
                    ms += ams
                    if got is None:
                        self._note(f, False)
                        continue
                self._note(f, True)
                out = dict(ok=True, line=line, pads=line.raw(),
                           press=press_at(line), ms=ms, answer=got[0],
                           family=f)
                if got[1] is not None:
                    out["answer_line"] = got[1]
                return out
        return dict(ok=False, why="no answer", ms=ms, line=line)

    def _answered(self, n, port, target, pre, my_pad, line, reaction):
        """The player's answer to `line` ((raw pads from the frame asked
        at, its line), ms), or (None, ms)."""
        raws = list(pre) + line.raw()
        if shielding(my_pad):
            # out of the shield the moment its stun is over: the shield
            # held the frames before the first it can act on, the answer
            # pressed on it, hitting by frame `within` counting it as 1 (a
            # frame-4 shine out of shield is within 4); the shield not hit
            # again in those frames (a late answer is then judged late, not
            # hit again: the drill's "one hit")
            self.answer.holds = "none"
            first = stun_over(n, port, target, raws,
                              clear=max(self.within, self.one_hit or 0),
                              single=bool(self.one_hit))
            if first is None:
                return None, 0.0
            wait = first - 1
            by = wait + self.within
        else:
            # no sooner than their reaction time, and before it lands
            self.answer.holds = "none,walk_out,out,walk_in"
            wait = len(pre) + reaction
            by = min(line.contact_at, wait + self.within)
            if by <= wait:
                return None, 0.0
        good, a = self.answer.find(n, target, port,
                                   raws + [self.after] * 90, tuple(my_pad),
                                   wait, by)
        if not good:
            return None, a.ms
        ms = a.ms
        if self.late and shielding(my_pad):
            # the same answer, the shield held 1 to `late` frames more
            # (each of them: an attacker's limb comes and goes): a line
            # only a frame-perfect answer reaches is not promised (Fox's up
            # air on a shield: the frame-4 shine hits, two frames later it
            # does not)
            for more in range(1, self.late + 1):
                again, b = self.answer.find(
                    n, target, port, raws + [self.after] * 90,
                    tuple(my_pad), wait + more, by + more)
                ms += b.ms
                if not again:
                    return None, ms
        return ([tuple(my_pad)] * wait + good[0].raw(), good[0]), ms

    owner = None          # the EngineOpponent playing it

    def over(self, me):
        """The line played to its end (a tilt's button comes 3 frames after
        its stick: over before that, it was never pressed), and the opponent
        free again."""
        o = self.owner
        if o is not None and o.plan_at is not None and \
                o.frame - o.plan_at < len(o.plan) - 1:
            return False
        if o is not None and self.late and o.answer is not None:
            # until the answer it promised, pressed as late as allowed,
            # would have landed, it stays as that was checked: not off
            # into its next step
            asked, pads = o.answer
            held = next((i for i, raw in enumerate(pads) if raw != pads[0]),
                        len(pads))
            if o.frame <= asked + held + self.within + self.late:
                return False
        return Contract.over(self, me)

    def retrack(self, n, port, target, remaining, my_pad, lead, rng,
                temperature=6.0, reaction=15):
        their = self._their(my_pad, lead + 6)
        if lands(n, port, target, remaining, their,
                 front=self.front) in self.kinds:
            return dict(outcome="lands")
        pre = remaining[:lead]
        # (picking for variety: the attack it was making, if it still
        # lands; else any)
        o = self.owner
        fam = family(o.line.names) if self.pick == "variety" and \
            o is not None and o.line is not None else None
        then = self.groups.get(fam) if fam else None
        found, r = self.search(n, port, target, pre, their,
                               "none,in,walk_in,out", enough=3, then=then)
        ms = r.ms
        if then is not None and not found:
            found, r = self.search(n, port, target, pre, their,
                                   "none,in,walk_in,out", enough=3)
            ms += r.ms
        if self.answer is not None:
            # only a line the player can answer (as when it committed)
            left, line = list(found[:12]), None
            for _ in range(min(self.TRIES, len(left))):
                c = pick(left, temperature, rng)
                left.remove(c)
                got, ams = self._answered(n, port, target, pre, my_pad, c,
                                          reaction)
                ms += ams
                if got is not None:
                    line = c
                    break
            found = [line] if line is not None else []
        if not found:
            return dict(outcome="nothing better", ms=ms)
        line = pick(found[:12], temperature, rng)
        return dict(outcome="new", pads=list(pre) + line.raw(),
                    press=len(pre) + press_at(line), ms=ms)


class Approach(Behaviour):
    """Commits to one of `moves` that the engine finds lands (`lands`: hit,
    shield, any) from wherever it is, its body (`body`: footsies closing in,
    or stand, shield, crouch) moving until then; with a `contract` {"answer":
    MOVE_PREFIXES, "within": N}, only to one the player can answer. `pick` (by
    default "variety"): the attack's family drawn among those that land,
    the last one or two it attacked with last (`weights`: {FAMILY: W}, 1
    each by default); "best": one of the best lines of all. Over when
    the line has played and the opponent can act again. `front` (by
    default when it lands on the shield): only lines on the front of it,
    the opponent never past the player before its move is over and their
    answer would hit.
    drill.EngineOpponent
    does the work: `committed`, `answer` ((frame asked, the player's raw
    pads from it): the answer the check found), `line`."""
    name = "approach"

    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        con = spec.get("contract") or {}
        lands_on = spec.get("lands", "any")
        # the families attacked with, the script's (and, through the
        # drill, the attempts before)
        self.recent = ctx.memory.setdefault("families", [])
        tried = ctx.memory.setdefault("tried", {})
        self.contract = Commit(spec["moves"], LANDS[lands_on],
                               answer=con.get("answer"),
                               within=con.get("within", 15),
                               front=spec.get("front", lands_on == "shield"),
                               pick=spec.get("pick", "variety"),
                               recent=self.recent,
                               weights=spec.get("weights"), tried=tried,
                               one_hit=con.get("one_hit"),
                               late=con.get("late"))
        self.noted = None         # the commitment its family was kept for
        body = spec.get("body", "footsies")
        if body == "footsies":
            body = Body(ctx.port, ctx.target, band=(12.0, 30.0),
                        rng=random.Random(self.rng.random()), half=ctx.half)
        else:
            body = HoldBody(Hold.PADS[body])
        wait = spec.get("wait", [0, 0])
        self.opp = EngineOpponent(
            ctx.think, ctx.port, ctx.target, self.contract, body=body,
            rng=random.Random(self.rng.random()), reaction=ctx.react,
            cpu_reaction=ctx.react, wait=(int(wait[0]), int(wait[1])),
            temperature=ctx.temperature, every=3)
        self.contract.owner = self.opp

    @property
    def committed(self):
        return self.opp.committed

    @property
    def answer(self):
        return self.opp.answer

    def step(self, st):
        raw = self.opp.pad(st, their=self.ctx.their)
        o = self.opp
        if o.committed is not None and o.committed != self.noted and \
                o.line is not None:
            self.noted = o.committed
            self.recent.append(family(o.line.names))
        if self.opp.mode == "done":
            self.done = True
        return raw

    def plan(self, st, k):
        o = self.opp
        if o.mode == "committed":
            i = o.frame - o.plan_at
            out = list(o.plan[i:i + k])
            return out + [NONE] * (k - len(out))
        return o.body.ahead(st, k)

    def stop(self):
        if self.opp.pending is not None:
            self.ctx.think.forget(self.opp.pending["tag"])


# ---- moves chosen one at a time by the engine -------------------------------

class Driven(Behaviour):
    """Each move chosen by a search as the last ends: the search is for the
    frame the queued pads run out (`lead` frames on at most, the frames a
    decision takes: InFork's measure; 0 headless), the pads until then as
    its pre-roll. Subclasses give `job(st, pre)`: a function of the game
    (or a fork of it) returning {"pads": [...]} (None: nothing found)."""
    kind = "drive"
    idle = NONE
    RETRY = 3                 # frames held before looking again

    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        self.queue = []
        self.pending = None
        self.tag = 0
        self.finished = False     # nothing more to ask for
        self.decisions = []
        self.late = 0
        self.ms = 0.0

    def job(self, st, pre):
        return None

    def got(self, out):
        pass

    def _collect(self):
        if self.pending is None:
            return
        tag, asked, at = self.pending
        think = self.ctx.think
        if not think.ready(tag):
            return
        out = think.result(tag)
        self.pending = None
        if out is None:
            return
        self.ms += out.get("ms", 0.0)
        if self.frame > at:
            self.late += 1
            return
        pads = list(out.get("pads") or [])
        if not pads and not self.finished:
            pads = [self.idle] * self.RETRY
        self.queue = self.queue[:at - self.frame] + pads
        self.decisions.append((at, out.get("line")))
        self.got(out)

    def drive(self, st):
        think = self.ctx.think
        self._collect()
        if self.pending is None and not self.finished:
            lead = think.lead_for(self.kind)
            if len(self.queue) <= lead:
                pre = (self.queue + [self.idle] * lead)[:lead]
                fn = self.job(st, pre)
                if fn is not None:
                    self.tag += 1
                    tag = ("drive", id(self), self.tag)
                    self.pending = (tag, self.frame, self.frame + lead)
                    think.submit(tag, fn, self.kind)
                    self._collect()
        return self.queue.pop(0) if self.queue else self.idle

    def step(self, st):
        return self.drive(st)

    def plan(self, st, k):
        out = list(self.queue[:k])
        return out + [self.idle] * (k - len(out))

    def stop(self):
        if self.pending is not None:
            self.ctx.think.forget(self.pending[0])
            self.pending = None


class Move(Driven):
    """One named move (`name`, an engine macro), played exactly, to where
    the opponent can act again. Over when it has played (at once, if the
    fighter's state does not allow it). An aerial is L-cancelled unless
    `lcancel` is false: then it lands with its whole landing lag, as from
    an opponent who misses the L-cancel (an approach that can be punished
    on landing)."""
    name = "move"

    def job(self, st, pre):
        self.finished = True
        port, target, name = self.ctx.port, self.ctx.target, \
            self.spec["name"]
        # (`lcancel`: false, an aerial lands with its whole landing lag)
        lcancel = 1 if self.spec.get("lcancel", True) else 0
        me, them = st["p"][port], st["p"][target]
        if me is not None and them is not None and \
                me["facing"] * (them["x"] - me["x"]) < 0 and \
                name in PIVOTS and not me.get("air"):
            # facing away (footsies' leg out): the attack out of a pivot
            name = "pivot_" + name

        def fn(n):
            if pre:
                preroll(n, pre)
            r = search(n, port, target, horizon=len(pre) + 90, budget=0,
                       depth=1, moves=name, lcancel=lcancel)
            exact = [l for l in r.lines if l.names == name or
                     l.names.startswith(name + "_")] or r.lines[:1]
            return dict(pads=exact[0].raw() if exact else None, ms=r.ms,
                        line=exact[0].names if exact else None)
        return fn

    def step(self, st):
        me, them = st["p"][self.ctx.port], st["p"][self.ctx.target]
        if not self.finished and self.pending is None and \
                not self.queue and self.frame < 40 and me is not None and \
                them is not None and me["state"] == 20 and \
                me["facing"] * (them["x"] - me["x"]) > 0:
            return NONE           # a dash toward: let go of first
        raw = self.drive(st)
        if self.finished and self.pending is None and not self.queue:
            self.done = True
        return raw


class Punish(Driven):
    """Plays to win from here until the player can act again: each move the
    best (by a softmax: not always the same) the engine finds two moves
    deep for damage, a kill, hitstun left (`moves`: the first moves
    allowed, by name prefix). The player is taken to let go (they are in
    lag or hitstun)."""
    name = "punish"
    kind = "punish"
    WEIGHTS = dict(dmg=1.0, hit=20.0, adv=1.0, ko=1000.0, taken=1.5)
    BUDGET, DEPTH, HORIZON = 2500, 2, 60

    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        self.moves = spec.get("moves")
        self.start = None
        self.hit = False

    def job(self, st, pre):
        port, target = self.ctx.port, self.ctx.target
        rng = random.Random(self.rng.random())
        temp = 4.0
        kw = dict(self.WEIGHTS)
        if self.moves:
            kw["moves"] = self.moves
        budget, depth, horizon = self.BUDGET, self.DEPTH, self.HORIZON

        def fn(n):
            if pre:
                preroll(n, pre)
            player(n, [(1, NONE)])
            try:
                r = search(n, port, target, horizon=len(pre) + horizon,
                           budget=budget, depth=depth, **kw)
            finally:
                player(n, None)
            lines = r.lines[:6]
            if not lines:
                return dict(pads=None, ms=r.ms)
            line = pick(lines, temp, rng)
            return dict(pads=line.raw()[:max(1, line.first_len)], ms=r.ms,
                        line=line.names, contact=line.contact)
        return fn

    def watch(self, st):
        them = st["p"][self.ctx.target]
        if self.start is None:
            self.start = them["percent"]
        if them["percent"] > self.start or them["state"] in S.CAPTURED:
            self.hit = True
        return them

    def step(self, st):
        them = self.watch(st)
        if S.free(them):
            # they can act again: the punish is over (one that never
            # started too: nothing to punish)
            self.done = True
            return NONE
        return self.drive(st)


class Chase(Punish):
    """Covers the player's tech, getup, missed tech or ledge option, seen
    `react` frames late, until they can act again or are caught.

    Thrown or knocked at the floor, the player's options are known before
    they choose (a tech in place, a roll either way, none), so the answers
    are worked out before they do (chase.py: the owner, 2026-11-24,
    "precompute a bunch of optimal reactions from likely inputs from a
    state"). Begun with the player in its grab (`chain_grab` with `chase`
    leaves them there), it makes the throw itself (`throw`): the table is
    asked for as the grab connects, in copies of the game, the throw
    played ahead; it holds the grab until the table is back (`HOLD` frames
    at most: a held player mashes out) and then throws, its answers ready
    before the throw begins. Then one of the table's stances is taken (how
    to wait: where to stand, or a read where reacting cannot cover an
    option), weighed by what this player has chosen before; and when the
    option is seen, its answer is played from that frame on: the reaction
    is the reaction time, with no search after it. A missed tech is a
    second stage of the same kind (the getups). `ahead` false, an option
    the table has not got, or a table that is not back in time: the first
    version, which stands until the option is seen and then searches
    (`Punish`). `reads` false: no stance commits before the option is
    seen. Over when they are held again (the next step's), or free."""
    name = "chase"
    kind = "chase"
    OPTIONS = S.TECHS + S.DOWN + S.LEDGE_OPTIONS + (S.CLIFF_CATCH,)
    ROOM = 1.2                # seconds a table may take while a person plays
    #                           (and no longer than the throw leaves it:
    #                           chase.table's clock)
    LATEST = 150              # frames a table is waited for
    GIVE_UP = 40              # frames past the reaction with nothing seen
    PATIENCE = (10, 34)       # frames it waits for a getup before it hits
    AGAIN = 2                 # tables made again in one chase, at most
    HOLD = 18                 # frames it holds its grab for its table
    # copies of the game a table is searched in: headless, and beside a
    # game a person plays (measured 2026-11-24 in the window build drawn
    # by the graphics card, the copies at low priority: the whole table
    # in 0.10 s with 12 copies and 0.11 to 0.14 with 6, none of the
    # game's frames late in nine tables with 12): half the machine's
    # processors, 12 at most
    COPIES = max(2, min(16, (os.cpu_count() or 4) - 2))
    LIVE = max(2, min(12, (os.cpu_count() or 4) // 2))

    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        self.started = None
        self.ahead = spec.get("ahead", True)
        self.reads = spec.get("reads", True)
        self.throw = spec.get("throw", "dthrow")
        self.mode = "look"        # look, table, throw, live
        # a stage: the table asked for at one moment and what came of it
        # (the tech; then, after a missed one, the getup)
        self.stage = None
        self.coming = None        # the next stage, asked for ahead
        self.stages = []          # every stage, for a test and a tool
        self.tags = 0
        self.again = 0            # tables made again (they left the path)
        self.throw_raw = None

    # (what a tool and a test read: of the stage that answered, else of
    # the one it is in)
    def _told(self):
        told = [g for g in self.stages if g["option"] is not None and
                g["cover"] is not None]
        return told[-1] if told else self.stage or (
            self.stages[-1] if self.stages else None)

    @property
    def tab(self):
        g = self._told()
        return g["tab"] if g else None

    @property
    def stance(self):
        g = self._told()
        return g["stance"] if g else None

    @property
    def option(self):
        g = self._told()
        return g["option"] if g else None

    @property
    def cover(self):
        g = self._told()
        return g["cover"] if g else None

    @property
    def back(self):
        g = self.stages[0] if self.stages else None
        return g["back"] if g else None

    # -- the tables -----------------------------------------------------------

    def _ask(self, prefix=(), start=None, cut=False, throw=None):
        """A stage: its table asked for now. `prefix`: the pads already
        decided for the next frames (the stance it is in; `cut`: only
        until the table is expected back); `start`: the first frame a
        stance may differ from standing on; `throw`: its own throw's pad,
        the player in its grab (the table is then of the throw it has not
        begun: its frames count from the throw, whenever it comes)."""
        from melee_engine import chase as CH
        think = self.ctx.think
        port, target, react = self.ctx.port, self.ctx.target, self.ctx.react
        moves = self.moves or CH.MOVES
        reads = self.reads
        prefix = [tuple(x) for x in prefix]
        live = bool(think.lead_for(self.kind))
        # while a person plays the table comes back some frames later: its
        # stances begin on the frame it is expected by (as long as the
        # last ones took, kept by the thinker), and it has that long;
        # with its own throw still to come, less the frames the grab is
        # held for it
        took = getattr(think, "chase_frames", 16.0)
        begin = max(start or 1, int(math.ceil(took)) + 2 - (
            self.HOLD if throw is not None else 0) if live else 1)
        deadline = self.ROOM if live else None
        if cut:
            prefix = prefix[:begin - 1]
        early = {}                # its standing row, as soon as it is done
        workers = self.LIVE if live else self.COPIES
        # (what this player chose before: which reads are worth searching)
        prior = dict(self.ctx.memory.get("chase", {}).get("tech", {}))

        def fn(n):
            return CH.table(n, port, target, react, moves=moves,
                            reads=reads, start=begin, deadline=deadline,
                            prefix=prefix, clock=live, throw=throw,
                            early=early, workers=workers, prior=prior)
        self.tags += 1
        stage = dict(tag=("chase", id(self), self.tags), asked=self.frame,
                     tab=None, back=None, stance=None, option=None,
                     shown=None, answer=None, cover=None, seen_at=None,
                     played=[], prefix=prefix, throw=throw, thrown_at=None,
                     held=0, early=early, whole=False, first=None,
                     patience=self.rng.randint(*self.PATIENCE))
        think.submit(stage["tag"], fn, self.kind)
        self.stages.append(stage)
        return stage

    def _k(self, g):
        """The stage's frame now as its table counts them, or None (its
        own throw not begun, or begun with the table not back: not known
        yet)."""
        if g["throw"] is None:
            return self.frame - g["asked"]
        if g["thrown_at"] is None or g["tab"] is None:
            return None
        return g["tab"]["throw_at"] + self.frame - g["thrown_at"]

    def _table_back(self, g, tab=None):
        """The stage's table, back: kept, and a stance chosen (`tab`: its
        standing row alone, come first: the whole table replaces it when
        it comes, unless an answer is already being played). False: there
        is none (nothing to chase, or it failed)."""
        from melee_engine import chase as CH
        think = self.ctx.think
        whole = tab is None
        if whole:
            tab = think.result(g["tag"])
            g["whole"] = True
            if tab is None or not tab["stances"]:
                return g["tab"] is not None
            g["back"] = self.frame - g["asked"]
            if think.lead_for(self.kind):
                was = getattr(think, "chase_frames", 16.0)
                think.chase_frames = max(4.0, 0.5 * was + 0.5 * g["back"])
            if g["answer"] is not None:
                return True       # (too late to change how it waits)
        if g["first"] is None:
            g["first"] = self.frame - g["asked"]
        g["tab"] = tab
        prior = self.ctx.memory.get("chase", {}).get(tab["kind"], {})
        played = g["played"]
        if g["throw"] is not None:
            # (of the table's frames: the throw, then standing since)
            k = self._k(g)
            at = tab["throw_at"]
            played = [] if k is None else \
                list(tab["lead"]) + [NONE] * (k - at)
        stance = CH.choose(tab, played, dict(prior), self.rng)
        if stance is None:
            return g["stance"] is not None
        g["stance"] = stance
        self.log.append((self.frame, "%s: waits %s (worth %.2f; %d "
                         "searches, %.0f ms%s)" % (
                             tab["kind"], g["stance"]["name"],
                             g["stance"]["worth"], tab["searches"],
                             tab["wall"],
                             ", its standing row" if not whole else
                             ", not all" if tab["partial"] else "")))
        return True

    def _note(self, g, them):
        """What the player chose, for the next time (the opponent's
        memory: the stance is weighed by it)."""
        if g["tab"] is None or g["shown"] is not None:
            return None
        from melee_engine import chase as CH
        o = CH.option_of(g["tab"], them["state"])
        if o is None:
            return None
        g["shown"] = self.frame
        seen = self.ctx.memory.setdefault("chase", {}).setdefault(
            g["tab"]["kind"], {})
        seen[o["name"]] = seen.get(o["name"], 0) + 1
        return o

    def _table(self, st):
        """This frame's pad from the stage's table, or None: the first
        version takes over."""
        from melee_engine import chase as CH
        think = self.ctx.think
        them = st["p"][self.ctx.target]
        g = self.stage
        if not g["whole"] and think.ready(g["tag"]):
            if not self._table_back(g):
                return None
        elif g["tab"] is None and g["early"].get("tab") is not None:
            self._table_back(g, g["early"]["tab"])
        if g["throw"] is not None and g["thrown_at"] is None:
            # its own grab: held until the table is back, then the throw
            if them["state"] in S.THROWN:
                g["thrown_at"] = self.frame
                if g["whole"] and g["back"] is not None:
                    self.log.append((self.frame, "thrown, its table back "
                                     "%d frames before" % (
                                         self.frame - g["asked"] -
                                         g["back"])))
            elif them["state"] not in S.CAPTURED:
                return None           # they got out of the grab
            else:
                g["held"] += 1
                me = st["p"][self.ctx.port]
                # (pressed once the grab has settled: a stick held from
                # before that is no throw)
                if (g["whole"] or g["held"] > self.HOLD) and \
                        me["state"] == S.CATCH_WAIT:
                    return g["throw"]
                return NONE
        k = self._k(g)
        if k is None:
            # thrown, the table not back yet: it stands
            if self.frame - g["asked"] > self.LATEST:
                return None
            return NONE
        if g["tab"] is None:
            if k > self.LATEST:
                return None           # it never came: the first version
            # not back yet: what was decided before, then it stands
            raw = g["prefix"][k] if k < len(g["prefix"]) else NONE
        else:
            tab, see = g["tab"], g["tab"]["see"]
            if g["shown"] is None and g["answer"] is None and \
                    self.again < self.AGAIN and CH.off_path(tab, k, them):
                # they held a direction through the throw: another fall
                # than the one its answers are for
                self.again += 1
                self.log.append((self.frame, "off the path: the table "
                                 "again"))
                self.stage = self._ask(prefix=g["stance"]["pads"][k:],
                                       cut=True)
                return self._table(st)
            shown = self._note(g, them)
            if shown is not None and shown["name"] == "none" and \
                    self.coming is None:
                c = g["stance"]["covers"].get("none")
                if not c or c["kind"] != "sure":
                    # a missed tech it has no sure hit for: the getup is
                    # the next thing to cover, thought about from now (it
                    # acts on it only once it has seen the missed tech)
                    self.coming = self._ask(
                        prefix=g["stance"]["pads"][k:see],
                        start=see - k + 1)
            if g["answer"] is None and k >= see:
                _, seen, _ = self.ctx.sense.seen()
                o = CH.option_of(tab, seen["state"]) if seen else None
                if o is None and tab["kind"] == "getup" and seen and \
                        seen["state"] in CH.DOWN_WAIT and \
                        k >= see + g["patience"]:
                    o = next(x for x in tab["options"]
                             if x["name"] == "stay")
                if o is not None:
                    c = g["stance"]["covers"].get(o["name"])
                    g["option"] = o["name"]
                    if o["name"] == "none" and self.coming is not None:
                        # (seen now: on to the getup, already asked for)
                        self.log.append((self.frame, "none seen: the getup"))
                        self.stage, self.coming = self.coming, None
                        return self._table(st)
                    if not c or not c.get("pads"):
                        self.log.append((self.frame, "%s seen: no answer "
                                         "ready" % o["name"]))
                        return None
                    g["answer"], g["cover"] = list(c["pads"]), c["kind"]
                    g["seen_at"] = k
                    self.log.append((self.frame, "%s seen: %s (%s, on "
                                     "frame %s)" % (o["name"], c["line"],
                                                    c["kind"], c["at"])))
                elif k >= see + self.GIVE_UP + g["patience"]:
                    return None       # they did something else
            if g["answer"] is not None:
                i = k - g["seen_at"]
                if i >= len(g["answer"]):
                    return None       # played out: on from here by search
                raw = g["answer"][i]
            else:
                pads = g["stance"]["pads"]
                raw = pads[k] if k < len(pads) else NONE
        raw = tuple(raw)
        for x in self.stages:
            if x["tab"] is None or x is g:
                x["played"].append(raw)
        return raw

    # -- each frame -----------------------------------------------------------

    def step(self, st):
        from melee_engine import chase as CH
        them = self.watch(st)
        g = self.stage
        ours = self.mode == "throw" or (
            g is not None and g["throw"] is not None and
            g["thrown_at"] is None)
        if them["state"] in S.CAPTURED and self.mode != "look" and not ours:
            self.done = True          # held again: the next step's
            return NONE
        if self.mode == "look":
            held = them["state"] in S.CAPTURED
            down = them["state"] in S.THROWN or (
                them.get("air") and not S.free(them))
            if held:
                me = st["p"][self.ctx.port]
                self.throw_raw = CH.throw_pad(self.throw,
                                              me.get("facing", 1))
            if self.ahead and (held or down):
                self.stage = self._ask(throw=self.throw_raw if held
                                       else None)
                self.mode = "table"
            else:
                self.mode = "throw" if held else "live"
        if self.mode == "throw":
            # (the first version: the throw at once)
            if them["state"] in S.CAPTURED:
                me = st["p"][self.ctx.port]
                return self.throw_raw if me["state"] == S.CATCH_WAIT \
                    else NONE
            self.mode = "live"
        if self.mode == "table":
            g = self.stage
            k = self._k(g)
            busy = g["answer"] is not None and k is not None and \
                k - g["seen_at"] < len(g["answer"])
            if k is not None and S.free(them) and g["tab"] is not None and \
                    not busy and k > g["tab"]["land"]:
                self.done = True      # they got away
                return NONE
            raw = self._table(st)
            if raw is not None:
                return raw
            self.mode = "live"
            self.started = self.frame \
                if any(x["option"] for x in self.stages) else None
        if self.started is None:
            _, seen, _ = self.ctx.sense.seen()
            if seen is None or seen["state"] not in self.OPTIONS:
                if S.free(them) and self.frame > 0 and self.stages:
                    self.done = True
                return NONE
            self.started = self.frame
        return super().step(st)

    def stop(self):
        for g in self.stages:
            if not g["whole"]:
                self.ctx.think.forget(g["tag"])
        super().stop()


class Pressure(Driven):
    """Attacks the shield with options safe on it, until the shield breaks
    or the player acts (leaves the shield). Each option: the timing scan
    for `moves` landing on the shield (the player holding it), then its
    safety: the player's out-of-shield options (`oos`) searched from the
    shield as soon as its stun is over; an option they can answer before
    the opponent can act again is not taken. None safe: a dash back.
    First version: the options' order and their safety only; no shield
    pokes, no mixups of timing beyond the scan's."""
    name = "pressure"
    kind = "pressure"
    MOVES = "sh_,jab,ftilt,dtilt,utilt,dash_attack,side_b,down_b,neutral_b"
    OOS = "oos_grab,oos_usmash,oos_down_b,oos_up_b"

    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        self.moves = spec.get("moves", self.MOVES)
        self.backs = 0
        self.safe = 0

    def job(self, st, pre):
        port, target = self.ctx.port, self.ctx.target
        rng = random.Random(self.rng.random())
        moves, oos = self.moves, self.OOS
        away = -toward(st, port, target)

        def fn(n):
            if pre:
                preroll(n, pre)
            r = searched(n, port, target, [(240, SHIELD)], len(pre) + 50,
                         then=moves, scan=3, hold="none,in,walk_in",
                         trial=30, shield=40, taken=3, near=45, enough=8)
            ms = r.ms
            cands = [l for l in r.lines if l.contact == "shield" and
                     l.taken == 0][:6]
            safe = []
            for line in cands:
                raws = list(pre) + line.raw()
                first = stun_over(n, port, target, raws)
                if first is None:
                    continue
                # (the shield held up to the first frame out of it, the
                # option pressed on it)
                a = Answer(oos, holds="none", near=45, trial=20, window=400)
                good, ar = a.find(n, target, port, raws, SHIELD, first - 1,
                                  len(raws) + 2)
                ms += ar.ms
                if not good:
                    safe.append(line)
                if len(safe) >= 3:
                    break
            if not safe:
                back = [NONE] + [(0, 127 * away, 0, 0, 0, 0, 0)] * 8
                return dict(pads=back, ms=ms, line="back")
            line = pick(safe, 4.0, rng)
            return dict(pads=line.raw(), ms=ms, line=line.names)
        return fn

    def got(self, out):
        if out.get("line") == "back":
            self.backs += 1
        elif out.get("line"):
            self.safe += 1

    def step(self, st):
        them = st["p"][self.ctx.target]
        if them["state"] in S.SHIELD_BREAK or (
                self.frame > 0 and them["state"] not in S.SHIELDING):
            self.done = True
            return NONE
        return self.drive(st)


def escape_at(n, port, target, most=60):
    """The first frame (1 the next) `port`, letting go, could act: free, or
    on the ground teching (a missed tech's first frame down); `most` if not
    within that. Played ahead and undone."""
    from melee_actor.ahead import look
    out = look(n, port, target, [(most, {})], stop=0)
    for i, row in enumerate(out.rows):
        if row.a_hitlag <= 0 and (row.a_state in S.FREE or
                                  row.a_state in S.DOWN + S.TECHS):
            return i + 1
    return most


class ChainGrab(Driven):
    """Grab, `throw`, then a regrab (`regrab`: move prefixes; by default a
    grab, standing or out of a dash or run toward, which is a dash grab,
    and the scope's dash_grab, pivot_grab, jc_grab once they are in) while
    the engine finds one that lands before the player could act (their
    first frame free or on the ground, played ahead: `escape_at`; a
    regrab found against a player jumping out caught that jump, or a
    flight its stick's DI had changed). Over when none does, at a
    knockdown, or after `MOST` throws."""
    name = "chain_grab"
    kind = "chain"
    MOST = 8
    SOON = 40             # frames after the throw a regrab must land by
    # the regrabs: a standing grab (out of a dash or run toward it: a dash
    # grab), and the scope's moves once the engine has them (opt-in: named)
    REGRABS = "grab,dash_grab,pivot_grab,jc_grab"
    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        self.throw = spec.get("throw", "dthrow")
        self.regrab = spec.get("regrab", self.REGRABS)
        # over when the grab has them: the next step, `chase`, makes the
        # throw (it asks for its answers as the grab connects, and holds
        # the grab until it has them)
        self.chase = spec.get("chase", False)
        # throws at most (`times`: 1, a throw and no regrab: what a
        # drill's example opponent does)
        self.most = spec.get("times", self.MOST)
        self.grabs = self.throws = 0
        self._held = self._threw = False
        self._thrown = False

    def _count(self, st):
        me, them = st["p"][self.ctx.port], st["p"][self.ctx.target]
        held = them["state"] in S.CAPTURED
        if held and not self._held:
            self.grabs += 1
        self._held = held
        threw = me["state"] in (219, 220, 221, 222)
        if threw and not self._threw:
            self.throws += 1
        self._threw = threw
        thrown = them["state"] in S.THROWN
        if self.chase and (held or thrown):
            self.released = True      # held: the throw is the chase's
        self._thrown = thrown

    def job(self, st, pre):
        port, target = self.ctx.port, self.ctx.target
        me = st["p"][port]
        if me["state"] == S.CATCH_WAIT:
            throw = self.throw

            def fn(n):
                if pre:
                    preroll(n, pre)
                r = search(n, port, target, horizon=len(pre) + 90, budget=0,
                           depth=1, moves=throw)
                line = next((l for l in r.lines if l.names == throw), None)
                return dict(pads=line.raw() if line else None, ms=r.ms,
                            line=throw)
            return fn
        if me["state"] in S.CATCHING:
            return None           # the grab or the throw still going on
        them = st["p"][target]
        if self.throws >= self.most or (self.grabs > 0 and them["state"] in
                                        S.DOWN + S.TECHS):
            # (on the ground, a tech or a missed one: a tech chase, not a
            # chain grab: `chase`)
            self.finished = True
            return None
        first = self.grabs == 0
        regrab = "grab" if first else self.regrab
        rng = random.Random(self.rng.random())
        soon = self.SOON

        def fn(n):
            # a regrab must connect before the player could do anything:
            # their first frame free, or their landing (a tech would start
            # a tech chase), played ahead with them letting go
            by = None if first else len(pre) + escape_at(n, target, port,
                                                         soon)
            if pre:
                preroll(n, pre)
            r = searched(n, port, target, expect(NONE, 0),
                         len(pre) + (70 if first else soon), then=regrab,
                         scan=1, hold="none,in,walk_in,out,walk_out",
                         stop=1, near=45, enough=4, hit=0, held=50)
            good = [l for l in r.lines if l.contact == "grab" and
                    (by is None or l.contact_at <= by)]
            if not good:
                return dict(pads=None, ms=r.ms, end=True, by=by)
            line = pick(good[:6], 2.0, rng)
            return dict(pads=line.raw(), ms=r.ms, line=line.names, by=by)
        return fn

    def got(self, out):
        if out.get("end") and self.grabs > 0:
            self.finished = True

    released = False

    def step(self, st):
        self._count(st)
        if self.released:
            self.stop()
            self.done = True
            return NONE
        raw = self.drive(st)
        if self.finished and self.pending is None and not self.queue:
            self.done = True
        return raw


# ---- off the stage ----------------------------------------------------------

class Recover(Behaviour):
    """Back onto the stage by any means, against what the player is doing:
    off the stage the routes its character has (jumps, specials at their
    angles and timings, a stall first) played ahead, one of the best
    taken, checked again as it flies and changed when the player commits
    to covering it, seen `react` frames late; on the ledge a getup, a
    roll, an attack, a jump, or a drop and back on; knocked down, a getup;
    hit, again from where it is (recover.py). Over when it stands on the
    stage, free to act, or is lost (`ended`); at once if it stands there
    already. `budget`: routes a decision plays ahead. `to` "ledge": it
    only goes there and is over once it hangs (an example's opponent, which
    does the one thing the example answers). `tools`: the only ones its
    routes use, comma separated (jump, float, up_b, side_b, down_b,
    airdodge; "jump": it comes back with its jump and its drift alone, no
    special that would hit a player on the ledge). `adapt` false: it flies the
    route it first chose, whatever the player does. `predict` false: only
    what the player is doing counts against a route, not what they could
    do from where they are."""
    name = "recover"

    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        from melee_engine.recover import Pilot
        self.pilot = Pilot(
            ctx.think, ctx.port, ctx.target,
            rng=random.Random(self.rng.random()), react=ctx.react,
            half=ctx.half, memory=ctx.memory.setdefault("recover", {}),
            budget=int(spec.get("budget", 64)),
            temperature=ctx.temperature + 2.0, goal=spec.get("to"),
            tools=spec.get("tools"),
            adapt=spec.get("adapt", True), predict=spec.get("predict", True))
        self.errors = 0

    @property
    def ended(self):
        return self.pilot.ended

    def step(self, st):
        try:
            raw = self.pilot.pad(st, self.ctx.their)
        except Exception:
            # A fault in its thinking never takes the game a person is
            # playing down with it (2026-11-17: a stale answer once did):
            # it is said, the route it was on is dropped, and it decides
            # again from where it is. (A headless run raises: a test sees
            # it.)
            import sys
            import traceback
            self.errors += 1
            if not hasattr(self.ctx.think, "realtime") or self.errors > 20:
                raise
            traceback.print_exc(file=sys.stderr)
            p = self.pilot
            p.stop()
            p.plan, p.info, p.need = [], None, True
            if len(p.played) <= p.frame:
                p.played.append(NONE)
            raw = NONE
        self.done = self.pilot.done
        self.log = self.pilot.log
        return raw

    def plan(self, st, k):
        return self.pilot.ahead(k)

    def stop(self):
        self.pilot.stop()


# ---- the table --------------------------------------------------------------

BEHAVIOURS = {
    "hold": Hold, "jump": Jump, "press": Press, "oos": Oos, "tech": Tech,
    "footsies": Footsies,
    "retreat": Retreat,
    "approach": Approach, "move": Move, "punish": Punish,
    "pressure": Pressure, "chase": Chase, "chain_grab": ChainGrab,
    "play": Play, "recover": Recover,
}
# in the scope, not built yet: a script naming them is refused
NOT_BUILT = ("edgeguard",)


def _pair(v):
    return isinstance(v, list) and len(v) == 2 and \
        all(isinstance(x, (int, float)) for x in v) and 0 <= v[0] <= v[1]


def _moves(v):
    return isinstance(v, str) and v != "" and not unknown_moves(v)


def _presses(v):
    """`press`'s inputs: each one of a button, the stick or the C-stick,
    on a frame from 1, held a frame or more."""
    def axis(a):
        return isinstance(a, list) and len(a) == 2 and all(
            isinstance(x, (int, float)) and -1 <= x <= 1 for x in a)
    return isinstance(v, list) and len(v) > 0 and all(
        isinstance(i, dict) and
        sum(k in i for k in ("press", "stick", "cstick")) == 1 and
        set(i) <= {"press", "stick", "cstick", "frame", "hold"} and
        i.get("press", "A") in Press.BUTTONS and
        axis(i.get("stick", [0, 0])) and axis(i.get("cstick", [0, 0])) and
        isinstance(i.get("frame"), int) and i["frame"] >= 1 and
        isinstance(i.get("hold", 1), int) and i.get("hold", 1) >= 1
        for i in v)


# each behaviour's own keys: a check of the value, and what it says
PARAMS = {
    "press": {"inputs": (_presses, "inputs by frame: press A B X Y or Z, "
                                   "stick or cstick [toward the player, "
                                   "up], frame from 1, hold")},
    "hold": {"pad": (lambda v: v in Hold.PADS, "stand, shield or crouch"),
             "near": (lambda v: isinstance(v, (int, float)) and
                      not isinstance(v, bool) and v >= 0, "units"),
             "far": (lambda v: isinstance(v, (int, float)) and
                     not isinstance(v, bool) and v >= 0, "units"),
             "stick": (lambda v: isinstance(v, list) and len(v) == 2 and
                       all(isinstance(x, (int, float)) and -1 <= x <= 1
                           for x in v),
                       "[toward the player, up], each -1 to 1")},
    "jump": {"stick": (lambda v: isinstance(v, list) and len(v) == 2 and
                       all(isinstance(x, (int, float)) and -1 <= x <= 1
                           for x in v),
                       "[toward the player, up], each -1 to 1")},
    "oos": {"option": (lambda v: v in Oos.OPTIONS, ", ".join(Oos.OPTIONS))},
    "tech": {"option": (lambda v: v in Tech.OPTIONS,
                        ", ".join(Tech.OPTIONS)),
             "getup": (lambda v: v in Tech.GETUPS, ", ".join(Tech.GETUPS)),
             "wait": (_pair, "[LO, HI] frames")},
    "footsies": {"range": (lambda v: v in ("outside", "edge") or _pair(v),
                           'outside, edge or [LO, HI]'),
                 "crouch": (lambda v: isinstance(v, bool), "true or false")},
    "retreat": {},
    "approach": {
        "moves": (_moves, "engine moves by name prefix, comma separated"),
        "lands": (lambda v: v in LANDS, "hit, shield or any"),
        "front": (lambda v: isinstance(v, bool), "true or false"),
        "pick": (lambda v: v in ("variety", "best"), "variety or best"),
        "weights": (lambda v: isinstance(v, dict) and all(
            isinstance(k, str) and isinstance(w, (int, float)) and w >= 0
            for k, w in v.items()), "{FAMILY: WEIGHT}, e.g. "
            '{"fsmash": 0.5}'),
        "contract": (lambda v: isinstance(v, dict) and
                     set(v) <= {"answer", "within", "one_hit", "late"} and
                     _moves(v.get("answer", "")) and
                     isinstance(v.get("within", 15), int) and
                     isinstance(v.get("one_hit", 1), int) and
                     isinstance(v.get("late", 0), int),
                     '{"answer": MOVE_PREFIXES, "within": FRAMES, '
                     '"one_hit": FRAMES, "late": FRAMES}'),
        "body": (lambda v: v in ("footsies",) + tuple(Hold.PADS),
                 "footsies, stand, shield or crouch"),
        "wait": (_pair, "[LO, HI] frames"),
    },
    "move": {"name": (lambda v: isinstance(v, str) and v in MACROS + PLANNED,
                      "an engine move's name"),
             "lcancel": (lambda v: isinstance(v, bool), "true or false")},
    "punish": {"moves": (_moves, "engine moves by name prefix")},
    "pressure": {"moves": (_moves, "engine moves by name prefix")},
    "chase": {"moves": (_moves, "engine moves by name prefix"),
              "throw": (lambda v: v in THROWS, ", ".join(THROWS)),
              "ahead": (lambda v: isinstance(v, bool), "true or false"),
              "reads": (lambda v: isinstance(v, bool), "true or false")},
    "chain_grab": {"throw": (lambda v: v in THROWS, ", ".join(THROWS)),
                   "regrab": (_moves, "engine moves by name prefix"),
                   "chase": (lambda v: isinstance(v, bool),
                             "true or false"),
                   "times": (lambda v: isinstance(v, int) and
                             not isinstance(v, bool) and 1 <= v <= 8,
                             "1 to 8")},
    "play": {},
    "recover": {"budget": (lambda v: isinstance(v, int) and 8 <= v <= 200,
                           "routes a decision plays ahead, 8 to 200"),
                "to": (lambda v: v in ("ledge", "stage"), "ledge or stage"),
                "tools": (lambda v: isinstance(v, str) and v != "" and all(
                    t in ("jump", "float", "up_b", "side_b", "down_b",
                          "airdodge") for t in v.split(",")),
                    "jump, float, up_b, side_b, down_b, airdodge, comma "
                    "separated"),
                "adapt": (lambda v: isinstance(v, bool), "true or false"),
                "predict": (lambda v: isinstance(v, bool), "true or false")},
}
REQUIRED = {"approach": ("moves",), "move": ("name",),
            "press": ("inputs",)}


def make(ctx, spec):
    """The behaviour of a script's {"do": NAME, ...} step."""
    return BEHAVIOURS[spec["do"]](ctx, spec)
