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
    "crouch", "platform_drop", "waveland_in", "waveland_out", "waveland") + \
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
    """Stands, shields or crouches (`pad`)."""
    name = "hold"
    PADS = {"stand": NONE, "shield": SHIELD, "crouch": CROUCH}

    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        self.raw = self.PADS[spec.get("pad", "stand")]

    def step(self, st):
        return self.raw

    def plan(self, st, k):
        return [self.raw] * k


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
                         half=ctx.half)
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


def stun_over(n, port, target, raws, most=40, clear=0):
    """Where `port` plays `raws` against a shielding `target` (holding its
    pad), the first frame (counted from now, 1 the first) the target can
    act out of the shield after the first hit on it; None if none hits
    it. On that frame shield stun's animation ends into the shield and the
    frame's input is read there (Fighter_procAnim runs before
    Fighter_procInput): an answer holds the shield the frames before it
    and is pressed on it. `clear`: None too if the shield, still held, is
    hit again in the `clear` frames from that one (a multi-hit attack's
    next hit: an answer pressed late would meet it in the shield)."""
    from melee_actor.ahead import compress, look
    plan = compress([raw_pad(r) for r in raws]) + [(most, raw_pad(NONE))]
    out = look(n, port, target, plan, stop=0)
    hit = None
    for i, row in enumerate(out.rows):
        if hit is None:
            if row.t_hitlag > 0 and row.t_state in S.SHIELDING:
                hit = i
            continue
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
                 weights=None, tried=None):
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
            first = stun_over(n, port, target, raws, clear=self.within)
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
        return ([tuple(my_pad)] * wait + good[0].raw(), good[0]), a.ms

    owner = None          # the EngineOpponent playing it

    def over(self, me):
        """The line played to its end (a tilt's button comes 3 frames after
        its stick: over before that, it was never pressed), and the opponent
        free again."""
        o = self.owner
        if o is not None and o.plan_at is not None and \
                o.frame - o.plan_at < len(o.plan) - 1:
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
                               weights=spec.get("weights"), tried=tried)
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
    fighter's state does not allow it)."""
    name = "move"

    def job(self, st, pre):
        self.finished = True
        port, target, name = self.ctx.port, self.ctx.target, \
            self.spec["name"]
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
                       depth=1, moves=name, lcancel=1)
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
    """Waits (standing) for the player's tech, getup, missed tech or ledge
    option, seen `react` frames late, then punishes it, until they can act
    again. First version: covering is the punish's search from where the
    option is seen, the player going on with it."""
    name = "chase"
    OPTIONS = S.TECHS + S.DOWN + S.LEDGE_OPTIONS + (S.CLIFF_CATCH,)

    def __init__(self, ctx, spec):
        super().__init__(ctx, spec)
        self.started = None

    def step(self, st):
        if self.started is None:
            _, seen, _ = self.ctx.sense.seen()
            if seen is None or seen["state"] not in self.OPTIONS:
                return NONE
            self.started = self.frame
        return super().step(st)


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
        self.grabs = self.throws = 0
        self._held = self._threw = False

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
        if self.throws >= self.MOST or (self.grabs > 0 and them["state"] in
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

    def step(self, st):
        self._count(st)
        raw = self.drive(st)
        if self.finished and self.pending is None and not self.queue:
            self.done = True
        return raw


# ---- the table --------------------------------------------------------------

BEHAVIOURS = {
    "hold": Hold, "footsies": Footsies, "retreat": Retreat,
    "approach": Approach, "move": Move, "punish": Punish,
    "pressure": Pressure, "chase": Chase, "chain_grab": ChainGrab,
    "play": Play,
}
# in the scope, not built yet: a script naming them is refused
NOT_BUILT = ("edgeguard", "recover")


def _pair(v):
    return isinstance(v, list) and len(v) == 2 and \
        all(isinstance(x, (int, float)) for x in v) and 0 <= v[0] <= v[1]


def _moves(v):
    return isinstance(v, str) and v != "" and not unknown_moves(v)


# each behaviour's own keys: a check of the value, and what it says
PARAMS = {
    "hold": {"pad": (lambda v: v in Hold.PADS, "stand, shield or crouch")},
    "footsies": {"range": (lambda v: v in ("outside", "edge") or _pair(v),
                           'outside, edge or [LO, HI]')},
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
                     set(v) <= {"answer", "within"} and _moves(
                         v.get("answer", "")) and
                     isinstance(v.get("within", 15), int),
                     '{"answer": MOVE_PREFIXES, "within": FRAMES}'),
        "body": (lambda v: v in ("footsies",) + tuple(Hold.PADS),
                 "footsies, stand, shield or crouch"),
        "wait": (_pair, "[LO, HI] frames"),
    },
    "move": {"name": (lambda v: isinstance(v, str) and v in MACROS + PLANNED,
                      "an engine move's name")},
    "punish": {"moves": (_moves, "engine moves by name prefix")},
    "pressure": {"moves": (_moves, "engine moves by name prefix")},
    "chase": {"moves": (_moves, "engine moves by name prefix")},
    "chain_grab": {"throw": (lambda v: v in THROWS, ", ".join(THROWS)),
                   "regrab": (_moves, "engine moves by name prefix")},
    "play": {},
}
REQUIRED = {"approach": ("moves",), "move": ("name",)}


def make(ctx, spec):
    """The behaviour of a script's {"do": NAME, ...} step."""
    return BEHAVIOURS[spec["do"]](ctx, spec)
