"""A drill's jump-in, thought out by the engine (docs/ai/melee-engine.md,
"Drills on the engine"): the opponent moves about in neutral as a person
waiting to approach does, chooses its own moment, and jumps in with the
drill's aerial so that it lands where the player is, unless the player
answers it the way the drill teaches.

The drill's contract, here for anti-air (fox-anti-air):

- the scenario: the deck's aerial out of a full hop, nothing else;
- the situation: the aerial lands on the player if nothing answers it (the
  jump, the drift and the frame the aerial is pressed are found by the
  engine's timing scan, src/host/engine.c, against where the player is);
- the answer exists: before it jumps, the opponent searches the player's
  side of that same jump-in, the player starting no sooner than a person's
  reaction time after the jump: an up tilt, up smash or back air that hits
  it in the air before its aerial lands. No answer, no jump: it moves on
  and looks again;
- wrong answers lose: in the air it follows the player (drift, the
  aerial's timing), and sees what the player commits to no sooner than its
  own reaction time, so an anti-air thrown too early is whiffed and
  punished, not dodged on the frame it starts.

Its decisions are made for a frame still to come (`lead` frames ahead,
the body's pads until then as the search's pre-roll), so that they can be
thought out in a forked copy of the game while a person plays
(fork.InFork: no frame waits for them), or in the game itself (`Here`)
headless.

    opp = JumpIn(Here(n), port=1, target=0, aerial="nair",
                 body=Footsies(1, 0, band=(35, 60)))
    ...each frame, before it is stepped:
    raw = opp.pad(n.state())     # (buttons, lx, ly, cx, cy, lt, rt)
    opp.jumped                   # frame of the jump (or None)
"""
import itertools
import math
import random

from melee_engine.search import player, preroll, search
from melee_engine.opponent import NEUTRAL

NONE = (0, 0, 0, 0, 0, 0, 0)

# a decision's tag: unique across opponents (a thinker outlives them)
_tags = itertools.count(1)

# The player's states that commit them to nothing: moving about (a run's
# turn and its direct turn too). Any other is a commitment the opponent
# sees only after its reaction time.
MOVING = NEUTRAL | {19, 22}

# What the player can answer a jump-in with, as the drill counts it, and
# how they may move before it.
ANTI_AIRS = "utilt,usmash,sh_bair"
ANSWER_HOLDS = "none,walk_out,out,walk_in"   # the likeliest first


def _raw_of_pad(p):
    return (p["buttons"], p["lx"], p["ly"], p["cx"], p["cy"],
            p.get("lt", 0), p.get("rt", 0))


def press_at(line):
    """The frame of a scan line (from where it starts) its last move is
    pressed on: its first move's frames and the hold's."""
    hold = [m for m in line.moves if m.startswith("hold_")]
    k = int(hold[0].split(":")[1]) if hold else 0
    return line.first_len + k


def pick(lines, temperature, rng):
    """One of `lines` by a softmax over their scores."""
    if not lines:
        return None
    best = max(l.value for l in lines)
    w = [math.exp((l.value - best) / max(temperature, 1e-6)) for l in lines]
    return rng.choices(lines, weights=w)[0]


# ---- what is searched (run against any game: the match or its shadow) ------

def expect(pad, frames):
    """What the player is expected to do: go on with `pad` for `frames`
    frames (they have not reacted yet), then stand (the answer to a
    jump-in is not a run across the stage). As `player()`'s segments."""
    return [(frames, pad), (1, NONE)] if frames > 0 else [(1, NONE)]


def _searched(n, port, target, their, horizon, **kw):
    player(n, their)
    try:
        return search(n, port, target, horizon=horizon, budget=0, depth=1,
                      **kw)
    finally:
        player(n, None)


def jumpins(n, port, target, pre, aerial, their, first="jump_in,jump",
            holds="in,none,ff_in", drift="_in,", enough=3, ms=0):
    """The jump-ins that land: from where `pre` (PORT's raw pads) ends, a
    full hop (`first`), a drift (`holds`) and `aerial` (drifting: `drift`,
    "_in" and/or "" as a list) pressed on each frame it can be, against the
    target doing `their` (expect()), until `enough` land. Lines that hit or
    meet the shield, best first; their frames count from now."""
    if pre:
        preroll(n, pre)
    then = ",".join(aerial + d for d in drift.split(",")) if drift else \
        aerial
    kw = dict(moves=first, then=then, scan=2, hold=holds, contact=60,
              hit=20, lcancel=0, stop=1, near=45, trial=28, enough=enough)
    if ms:
        kw["ms"] = ms
    r = _searched(n, port, target, their, len(pre) + 100, **kw)
    return [l for l in r.lines if l.contact in ("hit", "shield")], r


def in_air(n, port, target, pre, aerial, their,
           holds="in,walk_in,none,out,ff_in", enough=3, ms=0):
    """From the air (after `pre`): a drift and the aerial's frame, the
    lines that land (the first `enough`)."""
    if pre:
        preroll(n, pre)
    kw = dict(then="%s_in,%s" % (aerial, aerial), scan=2, hold=holds,
              contact=60, hit=20, lcancel=0, stop=1, near=45, trial=28,
              enough=enough)
    if ms:
        kw["ms"] = ms
    r = _searched(n, port, target, their, len(pre) + 80, **kw)
    return [l for l in r.lines if l.contact in ("hit", "shield")], r


def lands(n, port, target, raws, their):
    """Whether PORT's plan (raw pads from now) lands, the target doing
    `their`: the contact ("hit", "shield", "beaten" or None)."""
    if not raws:
        return None
    preroll(n, raws)
    r = _searched(n, port, target, their, len(raws) + 1, eval=1, stop=1)
    return r.lines[0].contact if r.lines else None


def answers(n, me, cpu, cpu_raws, my_pad, wait, lands_at, answers=ANTI_AIRS,
            holds=ANSWER_HOLDS, enough=1, states=None, ms=0):
    """The player's answers to the opponent playing `cpu_raws` (raw pads
    from now): the player holds `my_pad` for `wait` frames (their reaction
    time), then may move (`holds`) and presses one of `answers`; an answer
    hits the opponent in the air no later than `lands_at` (the frame its
    attack would land, from now), takes nothing, and (`states`) hits with
    one of those action states: what the drill counts. `enough`: stop
    after that many."""
    player(n, [(1, r) for r in cpu_raws])
    preroll(n, [my_pad] * wait)
    # an answer is pressed in the last frames before the attack lands (an
    # up smash's hitbox is out 7 frames after it, a back air's 4 after a
    # short hop's squat): the hold before that is played, not tried
    kw = dict(then=answers, scan=2, hold=holds, hit=100, lcancel=0, stop=1,
              near=35, trial=16, enough=enough,
              **{"from": max(0, lands_at - wait - 26)})
    if states:
        kw["want"] = ",".join(str(x) for x in states)
    if ms:
        kw["ms"] = ms
    try:
        r = search(n, me, cpu, horizon=lands_at + 1, budget=0, depth=1, **kw)
    finally:
        player(n, None)
    good = [l for l in r.lines if l.contact == "hit" and l.contact_air and
            l.contact_at <= lands_at and l.taken == 0 and
            (states is None or l.contact_state in states)]
    return good, r


# ---- where the thinking is done ---------------------------------------------

class Here:
    """Decisions thought out in the game itself, at once (headless: the
    frame waits). The answer is used on the frame it is for, as a shadow's
    is."""

    lead = 0

    def lead_for(self, kind):
        return 0

    def __init__(self, n):
        self.n = n
        self.results = {}

    def submit(self, tag, fn, kind=None):
        self.results[tag] = fn(self.n)

    def result(self, tag):
        return self.results.pop(tag, None)

    def ready(self, tag):
        return tag in self.results

    def forget(self, tag):
        self.results.pop(tag, None)


# ---- the body: moving about before the approach ------------------------------

class Footsies:
    """Moving as a person waiting to approach does: dash dances, walks,
    stops, a crouch, at random lengths, keeping to a band of distances from
    the target and on the stage, and turning back to face it. Its pads are
    planned some frames ahead (`ahead`), so a decision can be thought out
    for where they lead."""

    def __init__(self, port, target, band=(35.0, 60.0), rng=None,
                 half=70.0):
        self.port, self.target = port, target
        self.band = band
        self.rng = rng or random.Random(0)
        self.half = half
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
                           weights=(0.5, 0.2, 0.22, 0.08))[0]
        # not off the stage: a dash and its slide carry a fighter some 40
        # units, a walk some 20
        reach = 40.0 if kind == "dash" else 20.0
        if way * me["x"] > 0 and abs(me["x"]) + reach > self.half:
            way = -way
        out = []
        if kind == "dash":
            if self.last_lx * way > 0:
                out.append(NONE)         # a dash starts from the middle
            out += [(0, 127 * way, 0, 0, 0, 0, 0)] * rng.randint(3, 13)
        elif kind == "walk":
            lx = rng.choice((40, 55, 70)) * way
            out += [(0, lx, 0, 0, 0, 0, 0)] * rng.randint(6, 24)
        elif kind == "crouch":
            out += [(0, 0, -127, 0, 0, 0, 0)] * rng.randint(4, 14)
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


# ---- the opponent -------------------------------------------------------------

class JumpIn:
    """The drill's opponent: moves (`body`), then jumps in with `aerial` once
    the engine has found a jump-in that lands and that the player can
    answer. `pad(st)` once a frame gives its pad.

    reaction: frames a person takes to answer a jump they saw start (the
    answer check starts the player's answer no sooner). cpu_reaction: the
    frames the opponent takes to see what the player committed to (it does
    not change its plan sooner). wait: frames of neutral before the first
    jump may be (drawn per attempt, so it cannot be timed). track: follow
    the player in the air (off for a demonstration, which plays the answer
    that was checked).

    After the jump: `jumped` (its frame), `press` (the aerial's), `answer`
    (frame, raw pads: the player's answer the check found, from that
    frame), `landed` (it can act again)."""

    # in the air, the player is expected to go on as they are for this many
    # frames, then stand
    track_hold = 6

    def __init__(self, think, port, target, aerial, body, rng=None,
                 reaction=15, cpu_reaction=15, wait=(20, 110), track=True,
                 temperature=6.0, every=3, states=None, reach=None):
        self.think = think
        self.port, self.target = port, target
        self.aerial = aerial
        self.body = body
        self.rng = rng or random.Random(0)
        self.reaction, self.cpu_reaction = reaction, cpu_reaction
        self.track = track
        self.temperature = temperature
        self.every = every
        self.states = states      # what the drill counts as the answer
        self.reach = reach        # (near, far): distances it jumps in from
        self.earliest = self.rng.randint(*wait)
        self.frame = 0
        self.mode = "neutral"     # then "approach" (the jump on), "done"
        self.plan = []            # raw pads from frame `plan_at` on
        self.plan_at = None
        self.press = None
        self.jumped = None
        self.landed = None
        self.answer = None
        self.line = None          # the jump-in chosen
        self.pending = None       # dict(tag, kind, asked, at)
        self.tag = 0
        self.player_committed = -999
        self._was_neutral = True
        self.asked = self.found = self.refused = self.late = 0
        self.replans = 0
        self.outcomes = {}        # what the decisions came to, counted
        self.ms = 0.0
        self.log = []

    # -- what is asked ---------------------------------------------------------

    def _ask(self, kind, fn, lead):
        self.tag = next(_tags)
        self.pending = dict(tag=self.tag, kind=kind, asked=self.frame,
                            at=self.frame + lead)
        self.asked += 1
        self.think.submit(self.tag, fn, kind)

    # frames of looking without finding a jump-in, after which each look
    # tries every jump and drift (it costs more), and the body closes in on
    # the distance the drill's jump-in is from
    PATIENCE = 90

    def _commit_job(self, pre, my_pad):
        port, target, aerial = self.port, self.target, self.aerial
        rng = random.Random(self.rng.random())
        if self.frame - self.earliest < self.PATIENCE:
            # one jump and one drift each time it looks: they vary from one
            # look to the next, and a look costs a third
            first = rng.choice(("jump_in", "jump_in", "jump"))
            # (walk_in: half the stick, half the drift: the distances
            # between none and all of it)
            holds = rng.choice(("in", "walk_in", "none", "ff_in"))
            drift = rng.choice(("_in", "_in", ""))
        else:
            first, holds, drift = ("jump_in,jump", "in,walk_in,none,ff_in",
                                   "_in,")
        temperature, wait = self.temperature, len(pre) + self.reaction
        # Aimed at a player who stops now (as one waiting to anti-air does;
        # one who goes on is followed in the air). Decided ahead (a fork's
        # time), where they will be is not known: about where they are.
        their = expect(my_pad, min(len(pre), 3))
        # the answer: from where they are, no sooner than their reaction
        # time after the jump; with nothing decided ahead, going on as they
        # are until then (the latest a person starts it)
        answer_pad = my_pad if not pre else NONE
        states = self.states

        def job(n):
            found, r = jumpins(n, port, target, pre, aerial, their,
                               first=first, holds=holds, drift=drift)
            if not found:
                return dict(ok=False, why="lands nowhere", ms=r.ms)
            # one of the best timings: never the same jump-in twice
            line = pick(found[:12], temperature, rng)
            good, a = answers(n, target, port, list(pre) + line.raw(),
                              answer_pad, wait, line.contact_at,
                              states=states)
            if not good:
                return dict(ok=False, why="no answer", ms=r.ms + a.ms,
                            line=line)
            return dict(ok=True, line=line, ms=r.ms + a.ms,
                        answer=[answer_pad] * wait + good[0].raw(),
                        answer_line=good[0])
        return job

    def _replan_job(self, remaining, my_pad, lead):
        port, target, aerial = self.port, self.target, self.aerial
        rng = random.Random(self.rng.random())
        temperature = self.temperature
        # in the air: they go on as they are a little, then stand
        their = expect(my_pad, lead + self.track_hold)

        def job(n):
            if lands(n, port, target, remaining, their) in ("hit", "shield"):
                return dict(keep=True)
            pre = remaining[:lead]
            found, r = in_air(n, port, target, pre, aerial, their)
            if not found:
                return dict(keep=True, ms=r.ms)
            line = pick(found[:12], temperature, rng)
            return dict(keep=False, pads=list(pre) + line.raw(),
                        press=lead + press_at(line), ms=r.ms)
        return job

    # -- what comes back -------------------------------------------------------

    def _count(self, what):
        self.outcomes[what] = self.outcomes.get(what, 0) + 1

    def _collect(self):
        p = self.pending
        if p is None:
            return
        if not self.think.ready(p["tag"]):
            if self.frame > p["at"]:
                self.pending = None       # too late: dropped
                self.think.forget(p["tag"])
                self.late += 1
                self._count(p["kind"] + " late")
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
            self._count("replan " + ("lands" if got["keep"] and "ms" not in
                                     got else "nothing better" if
                                     got["keep"] else "new"))
        if p["kind"] == "commit":
            if not got["ok"]:
                self.refused += got["why"] == "no answer"
                self.log.append((p["at"], got["why"]))
                return
            self.found += 1
            self.line = got["line"]
            self.plan = got["line"].raw()
            self.plan_at = p["at"]
            self.press = p["at"] + press_at(got["line"])
            self.answer = (p["asked"], got["answer"])
            self.log.append((p["at"], got["line"].names))
        elif p["kind"] == "replan" and not got["keep"]:
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
        if n is None:
            n = self.think.shadow.n
        return _raw_of_pad(n.h.pads[self.target])

    _their = None

    # -- each frame ------------------------------------------------------------

    def pad(self, st, their=None):
        """This frame's pad (call once a frame, before it is played).
        `their`: the player's pad this frame (raw); by default the one the
        game was given."""
        me, them = st["p"][self.port], st["p"][self.target]
        self._their = their
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
        if self.pending is None and me is not None and them is not None \
                and not fresh:
            d = abs(me["x"] - them["x"])
            if self.mode == "neutral" and self.frame >= self.earliest and \
                    self.frame % self.every == 0 and not me["air"] and \
                    (self.reach is None or
                     self.reach[0] <= d <= self.reach[1]):
                pre = self.body.ahead(st, lead)
                self._ask("commit", self._commit_job(pre, self._their_pad()),
                          lead)
            elif self.mode == "approach" and self.track and \
                    self.press is not None and \
                    self.frame + lead < self.press and \
                    (self.frame - self.plan_at) % self.every == 0:
                i = self.frame - self.plan_at
                self._ask("replan", self._replan_job(self.plan[i:],
                                                     self._their_pad(), lead),
                          lead)
        self._collect()
        if self.mode == "neutral" and self.plan_at is not None and \
                self.frame >= self.plan_at:
            self.mode = "approach"
            self.jumped = self.frame
        if self.mode == "neutral":
            if self.frame - self.earliest == self.PATIENCE and \
                    self.reach is not None and \
                    hasattr(self.body, "band"):
                mid = (self.reach[0] + self.reach[1]) / 2.0
                self.body.band = (mid - 6.0, mid + 6.0)
            raw = self.body.next(st)
        elif self.mode == "approach":
            i = self.frame - self.plan_at
            raw = self.plan[i] if i < len(self.plan) else NONE
            if me is not None and self.frame > self.press + 2 and \
                    not me["air"] and me["state"] in NEUTRAL:
                self.landed = self.frame
                self.mode = "done"
        else:
            raw = NONE
        self.frame += 1
        return raw
