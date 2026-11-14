"""A drill's opponent on the engine (docs/ai/melee-engine.md, "Drills on
the engine"): the opponent of every course drill, held to the drill's
contract.

A contract (contracts.py) says what the drill is for:

- the scenario: which moves the opponent may use;
- the situation: what must happen if the player does nothing right (an
  attack that lands, a shield that holds, an escape that works);
- the answer: what the drill teaches; before the opponent commits, the
  player's side is searched for it, started no sooner than a person's
  reaction time: no answer, no commitment;
- wrong answers lose: the opponent follows the player, but sees what the
  player commits to only after its own reaction time.

`EngineOpponent` does the rest, the same for every drill: its body moves
(or holds a shield, a crouch, the ledge) until the contract finds a
commitment and its answer; every decision is made for a frame still to
come (`lead` frames on, the body's pads until then as the search's
pre-roll), so it can be thought out in a forked copy of the live game
(fork.InFork: no frame waits for it) or in the game itself (`Here`, when
nobody watches); one decision at a time; then it plays the line, the
contract correcting it as the player moves.

    opp = EngineOpponent(Here(n), 1, 0, JumpIn("nair"), Footsies(1, 0))
    ...each frame, before it is stepped:
    raw = opp.pad(n.state())      # (buttons, lx, ly, cx, cy, lt, rt)
    opp.committed                 # the frame it committed (or None)
"""
import itertools
import math
import random

from melee_engine.opponent import NEUTRAL

NONE = (0, 0, 0, 0, 0, 0, 0)

# a decision's tag: unique across opponents (a thinker outlives them)
_tags = itertools.count(1)

# The player's states that commit them to nothing: moving about (a run's
# turn and its direct turn too). Any other is a commitment the opponent
# sees only after its reaction time.
MOVING = NEUTRAL | {19, 22}


def raw_of_pad(p):
    return (p["buttons"], p["lx"], p["ly"], p["cx"], p["cy"],
            p.get("lt", 0), p.get("rt", 0))


def press_at(line):
    """The frame of a scan line (from where it starts) its last move is
    pressed on: its first move's frames and the hold's."""
    hold = [m for m in line.moves if m.startswith("hold_")]
    k = int(hold[0].split(":")[1]) if hold else 0
    return line.first_len + k


def pick(lines, temperature, rng):
    """One of `lines` by a softmax over their scores: never the same
    choice every time."""
    if not lines:
        return None
    best = max(l.value for l in lines)
    w = [math.exp((l.value - best) / max(temperature, 1e-6)) for l in lines]
    return rng.choices(lines, weights=w)[0]


def expect(pad, frames):
    """What the player is expected to do: go on with `pad` for `frames`
    frames (they have not reacted yet), then let go. As `player()`'s
    segments."""
    return [(frames, pad), (1, NONE)] if frames > 0 else [(1, NONE)]


# ---- where the thinking is done -------------------------------------------------

class Here:
    """Decisions thought out in the game itself, at once (headless, or
    frames nobody watches: the frame waits). Each is used on the frame it
    is for, as a fork's is."""

    lead = 0

    def __init__(self, n):
        self.n = n
        self.results = {}

    def lead_for(self, kind):
        return 0

    def submit(self, tag, fn, kind=None):
        self.results[tag] = fn(self.n)

    def result(self, tag):
        return self.results.pop(tag, None)

    def ready(self, tag):
        return tag in self.results

    def forget(self, tag):
        self.results.pop(tag, None)


# ---- bodies: what the opponent does until it commits ------------------------------

class Hold:
    """A body that holds one pad: standing (NONE), a shield, a crouch."""

    def __init__(self, raw=NONE):
        self.raw = tuple(raw)
        self.moved = 0

    def ahead(self, st, k):
        return [self.raw] * k

    def next(self, st):
        return self.raw


SHIELD = (0x20, 0, 0, 0, 0, 0, 255)       # R held, the trigger all the way
CROUCH = (0, 0, -127, 0, 0, 0, 0)


class Footsies:
    """Moving as a person waiting to approach does: dash dances, walks,
    stops, a crouch, at random lengths, keeping to a band of distances from
    the target and on the stage, and turning back to face it. Its pads are
    planned some frames ahead (`ahead`), so a decision can be thought out
    for where they lead."""

    def __init__(self, port, target, band=(35.0, 60.0), rng=None,
                 half=70.0, crouch=True):
        self.port, self.target = port, target
        self.band = band
        self.rng = rng or random.Random(0)
        self.half = half
        self.crouch = crouch
        self.queue = []
        self.last_lx = 0
        self.moved = 0                   # frames the stick was not neutral

    def _segment(self, st):
        me, them = st["p"][self.port], st["p"][self.target]
        rng = self.rng
        dx = them["x"] - me["x"]
        toward = 1 if dx > 0 else -1
        d = abs(dx)
        lo, hi = self.band
        r = rng.random()
        if d > hi:
            way = toward if r < 0.85 else -toward
        elif d < lo:
            way = -toward if r < 0.85 else toward
        else:
            way = toward if r < 0.5 else -toward
        kind = rng.choices(("dash", "walk", "wait", "crouch"),
                           weights=(0.5, 0.2, 0.22,
                                    0.08 if self.crouch else 0))[0]
        # Not off the stage. Where it is going counts, not where it is: a
        # run let go of slides 20 units and its turn carries it on (a Fox
        # ran off Final Destination that way). From where its momentum
        # takes it, a dash covers some 30 units more, a walk 25.
        coast = me["x"] + me.get("vx", 0.0) * 12
        limit = self.half - 12.0
        reach = 30.0 if kind == "dash" else 25.0
        if abs(coast) > limit - 10.0:
            way, kind = (-1 if coast > 0 else 1), "dash"   # back in
        elif way * coast > 0 and abs(coast) + reach > limit:
            way = -way
        out = []
        if kind == "dash":
            if self.last_lx * way > 0:
                out.append(NONE)         # a dash starts from the middle
            # an initial dash at most (a dash dance), not a run
            out += [(0, 127 * way, 0, 0, 0, 0, 0)] * rng.randint(3, 9)
        elif kind == "walk":
            lx = rng.choice((40, 55, 70)) * way
            out += [(0, lx, 0, 0, 0, 0, 0)] * rng.randint(6, 16)
        elif kind == "crouch":
            out += [CROUCH] * rng.randint(4, 14)
        else:
            out += [NONE] * rng.randint(2, 18)
        facing_away = me["facing"] * toward < 0
        if way != toward and (facing_away or kind in ("dash", "walk")) and \
                rng.random() < 0.6:
            # face them again: a tap toward them
            out += [NONE, (0, 45 * toward, 0, 0, 0, 0, 0), NONE]
        self.last_lx = out[-1][1]
        return out

    def ahead(self, st, k):
        """The next `k` pads, planned now (and kept to)."""
        while len(self.queue) < k:
            self.queue += self._segment(st)
        return list(self.queue[:k])

    def next(self, st):
        if not self.queue:
            self.queue += self._segment(st)
        raw = self.queue.pop(0)
        self.moved += raw[1] != 0
        return raw


# ---- the opponent ---------------------------------------------------------------

class EngineOpponent:
    """A drill's opponent: its `body` until the `contract` finds what to
    commit to (and the player's answer to it), then that line. `pad(st)`
    once a frame gives its pad.

    reaction: frames a person takes to answer what they saw start (the
    answer check starts the player's answer no sooner). cpu_reaction: the
    frames the opponent takes to see what the player committed to (it does
    not change its plan sooner). wait: frames before the first commitment
    may be (drawn per attempt, so it cannot be timed). track: follow the
    player during the line (off for a demonstration, which plays the answer
    that was checked).

    After the commitment: `committed` (its frame), `press` (its decisive
    input's), `line`, `answer` (frame, raw pads: the player's answer the
    check found, from that frame), `landed` (it can act again)."""

    # frames of looking without finding a commitment, after which each
    # look tries every variant (it costs more), and the body closes in on
    # the contract's distance
    PATIENCE = 90

    def __init__(self, think, port, target, contract, body=None, rng=None,
                 reaction=15, cpu_reaction=15, wait=(20, 110), track=True,
                 temperature=6.0, every=3):
        self.think = think
        self.port, self.target = port, target
        self.contract = contract
        self.body = body or Hold()
        self.rng = rng or random.Random(0)
        self.reaction, self.cpu_reaction = reaction, cpu_reaction
        self.track = track
        self.temperature = temperature
        self.every = every
        self.earliest = self.rng.randint(*wait)
        self.frame = 0
        self.mode = "neutral"     # then "committed" (the line on), "done"
        self.plan = []            # raw pads from frame `plan_at` on
        self.plan_at = None
        self.press = None
        self.committed = None
        self.landed = None
        self.answer = None
        self.line = None
        self.pending = None       # dict(tag, kind, asked, at)
        self.tag = 0
        self.player_committed = -999
        self._was_neutral = True
        self._their = None
        self.asked = self.found = self.refused = self.late = 0
        self.replans = 0
        self.outcomes = {}        # what the decisions came to, counted
        self.ms = 0.0
        self.log = []

    # (the jump-in drill's name for it)
    @property
    def jumped(self):
        return self.committed

    @property
    def patient(self):
        """Still within its patience (each look tries one variant)."""
        return self.frame - self.earliest < self.PATIENCE

    # -- asking ------------------------------------------------------------------

    def _ask(self, kind, fn, lead):
        self.tag = next(_tags)
        self.pending = dict(tag=self.tag, kind=kind, asked=self.frame,
                            at=self.frame + lead)
        self.asked += 1
        self.think.submit(self.tag, fn, kind)

    def _commit_job(self, pre, my_pad):
        c = self.contract
        rng = random.Random(self.rng.random())
        wide = not self.patient
        port, target = self.port, self.target
        temperature, reaction = self.temperature, self.reaction

        def job(n):
            return c.find(n, port, target, pre, my_pad, rng, wide=wide,
                          temperature=temperature, reaction=reaction)
        return job

    def _track_job(self, remaining, my_pad, lead):
        c = self.contract
        rng = random.Random(self.rng.random())
        port, target, temperature = self.port, self.target, self.temperature

        def job(n):
            return c.retrack(n, port, target, remaining, my_pad, lead, rng,
                             temperature=temperature)
        return job

    # -- what comes back -----------------------------------------------------------

    def _count(self, what):
        self.outcomes[what] = self.outcomes.get(what, 0) + 1

    def _collect(self):
        p = self.pending
        if p is None:
            return
        if not self.think.ready(p["tag"]):
            # Too late, it is waited out all the same (and then dropped):
            # one decision at a time, never a pile of them (forks are
            # processes; the unseen coach's run once had sixteen).
            return
        got = self.think.result(p["tag"])
        self.pending = None
        if got is None:
            self._count(p["kind"] + " failed")
            return
        self.ms += got.get("ms", 0.0)
        if self.frame > p["at"]:
            self.late += 1
            self._count(p["kind"] + " late")
            return
        if p["kind"] == "replan":
            self._count("replan " + got.get("outcome", "?"))
        if p["kind"] == "commit":
            if not got["ok"]:
                self.refused += got["why"] == "no answer"
                self.log.append((p["at"], got["why"]))
                return
            self.found += 1
            self.line = got["line"]
            self.plan = got["pads"]
            self.plan_at = p["at"]
            self.press = p["at"] + got["press"]
            self.answer = (p["asked"], got["answer"]) \
                if got.get("answer") is not None else None
            self.log.append((p["at"], got["line"].names))
        elif p["kind"] == "replan" and got.get("pads") is not None:
            # the pads until `at` stay (they were the pre-roll)
            i = p["asked"] - self.plan_at
            self.plan = self.plan[:i] + got["pads"]
            self.press = p["asked"] + got["press"]
            self.replans += 1
            self.log.append((p["at"], "replan"))

    def _their_pad(self):
        if self._their is not None:
            return tuple(self._their)
        n = getattr(self.think, "n", None)
        return raw_of_pad(n.h.pads[self.target])

    # -- each frame ----------------------------------------------------------------

    def pad(self, st, their=None):
        """This frame's pad (call once a frame, before it is played).
        `their`: the player's pad this frame (raw); by default the one the
        game was given."""
        me, them = st["p"][self.port], st["p"][self.target]
        self._their = their
        c = self.contract
        if them is not None:
            neutral = them["state"] in MOVING
            if self._was_neutral and not neutral:
                self.player_committed = self.frame
            self._was_neutral = neutral
        # what the opponent may know of the player: what they committed to
        # at least cpu_reaction frames ago
        fresh = self.frame - self.player_committed < self.cpu_reaction
        lead = self.think.lead_for(
            "commit" if self.mode == "neutral" else "replan")
        if self.pending is None and me is not None and them is not None:
            if self.mode == "neutral" and self.frame >= self.earliest and \
                    self.frame % self.every == 0 and \
                    (not fresh or c.sees_commitments) and \
                    c.ready(st, self.port, self.target):
                pre = self.body.ahead(st, lead)
                self._ask("commit", self._commit_job(pre, self._their_pad()),
                          lead)
            elif self.mode == "committed" and self.track and not fresh and \
                    c.tracks and self.press is not None and \
                    self.frame + lead < self.press and \
                    (self.frame - self.plan_at) % self.every == 0:
                i = self.frame - self.plan_at
                self._ask("replan", self._track_job(self.plan[i:],
                                                    self._their_pad(), lead),
                          lead)
        self._collect()
        if self.mode == "neutral" and self.plan_at is not None and \
                self.frame >= self.plan_at:
            self.mode = "committed"
            self.committed = self.frame
        if self.mode == "neutral":
            if self.frame - self.earliest == self.PATIENCE and \
                    c.reach is not None and hasattr(self.body, "band"):
                mid = (c.reach[0] + c.reach[1]) / 2.0
                self.body.band = (mid - 6.0, mid + 6.0)
            raw = self.body.next(st)
        elif self.mode == "committed":
            i = self.frame - self.plan_at
            raw = self.plan[i] if i < len(self.plan) else c.after
            if me is not None and self.frame > self.press + 2 and \
                    c.over(me):
                self.landed = self.frame
                self.mode = "done"
        else:
            raw = c.after
        self.frame += 1
        return raw
