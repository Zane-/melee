"""Drills' contracts with the engine (drill.py; docs/ai/melee-engine.md,
"Drills on the engine"): what the opponent searches for, what counts as
the situation the drill needs, and what the player's answer is.

A contract's searches run against any game (`n`): the match itself, or a
forked copy of it (fork.py), always from the frame the decision was asked
at, after `pre` (the opponent's pads until the frame it is for).

    JumpIn("nair")                         an aerial out of a full hop that
                                           lands; answered by an anti-air
    JumpIn("fair", hop="short", answer=…)  out of a short hop
"""
from melee_engine.search import player, preroll, search
from melee_engine.drill import NONE, expect, pick, press_at


def searched(n, port, target, their, horizon, **kw):
    """A search with the target's inputs given (`their`: player()'s
    segments), undone after."""
    player(n, their)
    try:
        return search(n, port, target, horizon=horizon, budget=0, depth=1,
                      **kw)
    finally:
        player(n, None)


def lands(n, port, target, raws, their, kinds=("hit", "shield")):
    """What PORT's plan (raw pads from now) meets, the target doing
    `their`: the contact ("hit", "shield", "grab", "beaten" or None)."""
    if not raws:
        return None
    preroll(n, raws)
    r = searched(n, port, target, their, len(raws) + 1, eval=1, stop=1)
    return r.lines[0].contact if r.lines else None


class Answer:
    """What the drill teaches the player, searched from their side: they
    hold `my_pad` for their reaction time, may then move (`holds`), and
    press one of `moves`; it counts if it hits the opponent first, taking
    nothing, in one of `states` (the drill's own judgement), and (`air`)
    with the opponent in the air, no later than the frame the opponent's
    line needs it by."""

    def __init__(self, moves, states=None, holds="none,walk_out,out,walk_in",
                 air=False, near=35, trial=16, window=26, kinds=("hit",)):
        self.moves, self.states, self.holds = moves, states, holds
        self.air, self.near, self.trial = air, near, trial
        self.window = window      # how long before `by` it may be pressed
        self.kinds = kinds

    def find(self, n, me, cpu, cpu_raws, my_pad, wait, by, enough=1):
        player(n, [(1, r) for r in cpu_raws])
        preroll(n, [my_pad] * wait)
        kw = dict(then=self.moves, scan=2, hold=self.holds, hit=100,
                  lcancel=0, stop=1, near=self.near, trial=self.trial,
                  enough=enough, **{"from": max(0, by - wait - self.window)})
        if self.states:
            kw["want"] = ",".join(str(x) for x in self.states)
        try:
            r = search(n, me, cpu, horizon=by + 1, budget=0, depth=1, **kw)
        finally:
            player(n, None)
        good = [l for l in r.lines if l.contact in self.kinds and
                l.contact_at <= by and l.taken == 0 and
                (not self.air or l.contact_air) and
                (self.states is None or l.contact_state in self.states)]
        return good, r


class Contract:
    """What every contract has. `find` and `retrack` return dicts:
    find -> ok, why, line, pads (from the frame it is for), press (frame of
    the decisive input in pads), answer (the player's pads from the frame it
    was asked at, or None), ms; retrack -> outcome, pads and press (when
    the line changes), ms."""

    reach = None              # (near, far): distances it looks from
    tracks = True             # corrects its line as the player moves
    sees_commitments = False  # looks while the player's commitment is new
    after = NONE              # its pad once the line is over

    def ready(self, st, port, target):
        me, them = st["p"][port], st["p"][target]
        if me["air"]:
            return False
        if self.reach is None:
            return True
        return self.reach[0] <= abs(me["x"] - them["x"]) <= self.reach[1]

    def over(self, me):
        from melee_engine.opponent import NEUTRAL
        return not me["air"] and me["state"] in NEUTRAL

    def retrack(self, n, port, target, remaining, my_pad, lead, rng,
                temperature=6.0):
        return dict(outcome="kept")


class JumpIn(Contract):
    """An aerial out of a hop (`hop`: "full" or "short"), the hop, its drift
    and the aerial's frame found by the timing scan so that it lands where
    the player is (a player who stops: one who goes on is followed in the
    air). Answered (`answer`) or not; `kinds`: what counts as landing
    ("hit", "shield")."""

    def __init__(self, aerial, hop="full", answer=None, reach=None,
                 kinds=("hit", "shield"), track_hold=6):
        self.aerial = aerial
        self.hop = hop
        self.answer = answer
        self.reach = reach
        self.kinds = kinds
        self.track_hold = track_hold

    def _firsts(self):
        return ("jump_in", "jump") if self.hop == "full" else \
            ("hop_in", "hop")

    def search(self, n, port, target, pre, their, first, holds, drift,
               enough=3):
        if pre:
            preroll(n, pre)
        a = self.aerial
        then = ",".join(a + d for d in drift.split(",")) if drift else a
        r = searched(n, port, target, their, len(pre) + 100, moves=first,
                     then=then, scan=2, hold=holds, contact=60, hit=20,
                     lcancel=0, stop=1, near=45, trial=28, enough=enough)
        return [l for l in r.lines if l.contact in self.kinds], r

    def find(self, n, port, target, pre, my_pad, rng, wide=False,
             temperature=6.0, reaction=15):
        firsts = self._firsts()
        if not wide:
            # one hop and one drift each time it looks: they vary from one
            # look to the next, and a look costs a third (walk_in: half the
            # stick, half the drift: the distances between none and all)
            first = rng.choice((firsts[0], firsts[0], firsts[1]))
            holds = rng.choice(("in", "walk_in", "none", "ff_in"))
            drift = rng.choice(("_in", "_in", ""))
        else:
            first, holds, drift = (",".join(firsts),
                                   "in,walk_in,none,ff_in", "_in,")
        # Aimed at a player who stops now (as one waiting for it does; one
        # who goes on is followed in the air). Decided ahead (a fork's
        # time), where they will be is not known: about where they are.
        their = expect(my_pad, min(len(pre), 3))
        found, r = self.search(n, port, target, pre, their, first, holds,
                               drift)
        if not found:
            return dict(ok=False, why="lands nowhere", ms=r.ms)
        line = pick(found[:12], temperature, rng)
        out = dict(ok=True, line=line, pads=line.raw(), press=press_at(line),
                   ms=r.ms, answer=None)
        if self.answer is not None:
            # the answer: from where they are, no sooner than their reaction
            # time after the jump; with nothing decided ahead, going on as
            # they are until then (the latest a person starts it)
            wait = len(pre) + reaction
            pad = my_pad if not pre else NONE
            good, a = self.answer.find(n, target, port, list(pre) + line.raw(),
                                       pad, wait, line.contact_at)
            out["ms"] += a.ms
            if not good:
                return dict(ok=False, why="no answer", ms=out["ms"],
                            line=line)
            out["answer"] = [pad] * wait + good[0].raw()
            out["answer_line"] = good[0]
        return out

    def retrack(self, n, port, target, remaining, my_pad, lead, rng,
                temperature=6.0):
        # in the air: they go on as they are a little, then stand
        their = expect(my_pad, lead + self.track_hold)
        if lands(n, port, target, remaining, their) in self.kinds:
            return dict(outcome="lands")
        pre = remaining[:lead]
        if pre:
            preroll(n, pre)
        a = self.aerial
        r = searched(n, port, target, their, len(pre) + 80,
                     then="%s_in,%s" % (a, a), scan=2,
                     hold="in,walk_in,none,out,ff_in", contact=60, hit=20,
                     lcancel=0, stop=1, near=45, trial=28, enough=3)
        found = [l for l in r.lines if l.contact in self.kinds]
        if not found:
            return dict(outcome="nothing better", ms=r.ms)
        line = pick(found[:12], temperature, rng)
        return dict(outcome="new", pads=list(pre) + line.raw(),
                    press=lead + press_at(line), ms=r.ms)


# ---- what the course's drills answer with -----------------------------------------

def anti_air(states):
    """Fox's anti-airs (fox-anti-air): up tilt, up smash, a short hop back
    air, hitting the opponent in the air."""
    return Answer("utilt,usmash,sh_bair", states=states, air=True)
