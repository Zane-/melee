"""Conditions: what is true on a frame, as the opponent sees it
(docs/ai/opponent-vocabulary.md, layer 2).

A condition is a word, or a dict of one key, as a drill's script writes
it ("approach", {"distance": [20, 40]}, {"not": "shielding"}). Conditions
about the player are seen `react` frames late (a person's reaction: 15 by
default), so the opponent cannot answer what it could not have seen: the
state they are read on is the one `react` frames ago, from a short history.
{"me": C} is the opponent itself, seen at once.

    sense = Sense(port=1, target=0, react=15, think=Here(n))
    ...each frame, before the opponent's pad is chosen:
    sense.update(n.state())
    sense.test("approach")                  # True / False
    sense.test({"distance": [20, 40]})

Most conditions are pure functions of states (`holds(cond, view)`), so
they are tested without a game. Two kinds need the game:

- the ranges (`in_their_range` and the others): can the player hit the
  opponent within `frames` frames (12) with any of its attacks, from
  standing or out of a dash or run toward it? Searched from the player's
  side with the engine's timing scan, as an answer is (contracts.Answer),
  the opponent doing what it plans to (its behaviour's pads), every
  `cache` frames (4), in the game or a fork of it (the thinker: `Here`
  headless, `InFork` while a person plays). `in_my_range`: the same from
  the opponent's side, the player going on as they are for a few frames
  and then stopping.
- `{"lag": N}`: the frames before the player can act again, played ahead
  in the game with the player letting go.

The results are kept by the frame they were found on, and read on the
frame the condition is read on (react frames ago for the player).
"""
import collections

from melee_engine.drill import NONE, expect
from melee_engine.search import player, preroll, search

REACT = 15        # frames: a person's reaction (the drill may set its own)
FRAMES = 12       # frames within which a range counts
CACHE = 4         # frames a range or a lag found is kept before a new one

# ---- action states (ftCommon, as the game numbers them) ---------------------

WAIT = 14
WALKS = (15, 16, 17)
TURN, TURN_RUN, DASH, RUN, RUN_DIRECT, RUN_BRAKE = 18, 19, 20, 21, 22, 23
KNEEBEND = 24
JUMPS = (25, 26, 27, 28)
FALLS = (29, 30, 31, 32, 33, 34)
FALL_SPECIAL = (35, 36, 37)
TUMBLE = 38
SQUATS = (39, 40, 41)
LANDING, LANDING_SPECIAL = 42, 43
GUARD_ON, GUARD, GUARD_OFF, GUARD_STUN, GUARD_REFLECT = 178, 179, 180, \
    181, 182
SHIELDING = (GUARD_ON, GUARD, GUARD_OFF, GUARD_STUN, GUARD_REFLECT)
DOWN = tuple(range(183, 199))         # lying down, its getups
TECHS = tuple(range(199, 205))        # Passive...: a tech
SHIELD_BREAK = tuple(range(205, 212))  # broken, dizzy
CATCHING = tuple(range(212, 223))     # grabbing, holding, throwing
CATCH_WAIT = 216
CAPTURED = tuple(range(223, 233))     # held
ROLLS = (233, 234, 235, 236)          # rolls, spot dodge, air dodge
THROWN = tuple(range(239, 244))
PASS, TEETER = 244, (245, 246)
CLIFF_CATCH, CLIFF_WAIT = 252, 253
LEDGE = (CLIFF_CATCH, CLIFF_WAIT)
LEDGE_OPTIONS = tuple(range(254, 264))  # getup, attack, roll, jump

# Moving about, free to act: anything else is a commitment (an attack,
# landing lag, shield stun, a roll or dodge, hitstun, tumble, lying down, a
# tech, a getup, grabbed or thrown, a ledge option, a special). The normal
# landing is lag (4 frames for most): a landing can be punished.
FREE = frozenset((WAIT, TURN, TURN_RUN, DASH, RUN, RUN_DIRECT, RUN_BRAKE,
                  KNEEBEND) + WALKS + JUMPS + FALLS + SQUATS +
                 (GUARD_ON, GUARD, GUARD_OFF, GUARD_REFLECT, CLIFF_WAIT,
                  CATCH_WAIT, PASS) + TEETER)


def free(f):
    """Can fighter `f` (a state's fighter dict) act: moving about, not
    frozen?"""
    return f is not None and f["state"] in FREE and not f.get("hitlag")


def committed(f):
    return f is not None and not free(f)


# ---- the words --------------------------------------------------------------

# a word alone
WORDS = ("in_their_range", "out_of_their_range", "in_my_range",
         "out_of_my_range", "approach", "retreat", "committed", "free",
         "stunned", "shielding", "airborne", "grounded", "on_ledge",
         "offstage", "on_platform")
# {"key": value}
KEYS = ("distance", "state", "shield_below", "percent", "lag", "me", "not",
        "any", "all", "after")
RANGES = {"in_their_range": ("their", True),
          "out_of_their_range": ("their", False),
          "in_my_range": ("my", True), "out_of_my_range": ("my", False)}


def problems(c, where="condition", states=None):
    """What is wrong with condition `c` ([] if nothing): every word and key
    checked against the table. `states`: the state names a {"state": S}
    may use (the drill format's)."""
    out = []

    def pair(v):
        return isinstance(v, list) and len(v) == 2 and \
            all(isinstance(x, (int, float)) for x in v) and v[0] <= v[1]

    if isinstance(c, str):
        if c not in WORDS:
            out.append("%s: unknown condition %r (one of %s, or %s)" % (
                where, c, ", ".join(WORDS), ", ".join(KEYS)))
        return out
    if not isinstance(c, dict) or len(c) != 1:
        return ["%s: a word or {key: value}, one key" % where]
    k, v = next(iter(c.items()))
    w = "%s.%s" % (where, k)
    if k not in KEYS:
        out.append("%s: unknown condition %r" % (where, k))
    elif k in ("distance", "percent"):
        if not pair(v):
            out.append("%s: [LO, HI]" % w)
    elif k == "state":
        if not isinstance(v, str) or (states is not None and
                                      v not in states):
            out.append("%s: a state name" % w)
    elif k in ("shield_below", "lag", "after"):
        if not isinstance(v, (int, float)) or v < 0:
            out.append("%s: a number from 0" % w)
    elif k in ("me", "not"):
        out += problems(v, w, states)
    elif k in ("any", "all"):
        if not isinstance(v, list) or not v:
            out.append("%s: a list of conditions" % w)
        else:
            for i, x in enumerate(v):
                out += problems(x, "%s[%d]" % (w, i), states)
    return out


def uses(c):
    """The game's searches condition `c` needs: a set of "their", "my"
    (the ranges) and "lag"."""
    out = set()
    if isinstance(c, str):
        if c in RANGES:
            out.add(RANGES[c][0])
    elif isinstance(c, dict):
        for k, v in c.items():
            if k == "lag":
                out.add("lag")
            elif k in ("me", "not"):
                out |= uses(v)
            elif k in ("any", "all"):
                for x in v:
                    out |= uses(x)
    return out


# ---- pure conditions --------------------------------------------------------

class View:
    """What a condition is read on: `subj` the fighter it is about (the
    player as seen, or the opponent now), `prev` the same a frame before,
    `other` the other fighter, `half` the stage's half width (to the
    ledge), `after` frames into the step, `ranges` {"their": bool or None,
    "my": ...}, `lag` frames before `subj` can act (None: unknown),
    `char` subj's character id (the drill format's state names)."""

    def __init__(self, subj, prev=None, other=None, half=85.0, after=0,
                 ranges=None, lag=None, char=None, me_view=None):
        self.subj, self.prev, self.other = subj, prev or subj, other
        self.half, self.after = half, after
        self.ranges = ranges or {}
        self.lag = lag
        self.char = char
        self.me_view = me_view       # {"me": C} is read on this


def _toward(subj, other):
    """+1 if `other` is on subj's right."""
    return 1 if other["x"] >= subj["x"] else -1


def moving(view, way):
    """Is the subject closing in (`way` +1) or moving away (-1): dashing,
    running or walking that way, in the air drifting that way, or covering
    more than a unit a frame that way?"""
    s, p, o = view.subj, view.prev, view.other
    if s is None or o is None:
        return False
    toward = _toward(s, o) * way
    moved = (s["x"] - p["x"]) * toward
    if moved > 1.0:
        return True
    st = s["state"]
    if st in (DASH, RUN) + WALKS and s["facing"] * toward > 0:
        return True
    if s["air"] and moved > 0.3:
        return True
    return False


def state_is(f, name, char=None):
    """Is fighter `f` in the drill format's state `name` (STATES, and the
    character's own: CHAR_STATES)?"""
    from melee_drills import format as F
    want = F.CHAR_STATES.get(char, {}).get(name, F.STATES.get(name))
    if want is None:
        return False
    return f["state"] in want if isinstance(want, tuple) else \
        f["state"] == want


def holds(c, view):
    """Does condition `c` hold on `view`?"""
    s, o = view.subj, view.other
    if isinstance(c, str):
        if c in RANGES:
            kind, want = RANGES[c]
            got = view.ranges.get(kind)
            return got is not None and got == want
        if s is None:
            return False
        if c == "approach":
            return moving(view, 1)
        if c == "retreat":
            return moving(view, -1)
        if c == "committed":
            return committed(s)
        if c == "free":
            return free(s)
        if c == "stunned":
            # hitstun left, or frozen in a hit: it cannot act (the state
            # alone does not say: a fighter sent flying stays in its
            # flight's state some frames after its hitstun is over)
            return s.get("hitstun", 0) > 0 or bool(s.get("hitlag"))
        if c == "shielding":
            return s["state"] in SHIELDING
        if c == "airborne":
            return bool(s["air"])
        if c == "grounded":
            return not s["air"]
        if c == "on_ledge":
            return s["state"] in LEDGE
        if c == "offstage":
            return abs(s["x"]) > view.half + 1.0 or s["y"] < -8.0
        if c == "on_platform":
            return not s["air"] and s["y"] > 5.0
        raise ValueError("unknown condition %r" % c)
    (k, v), = c.items()
    if k == "not":
        return not holds(v, view)
    if k == "any":
        return any(holds(x, view) for x in v)
    if k == "all":
        return all(holds(x, view) for x in v)
    if k == "after":
        return view.after >= v
    if k == "me":
        return holds(v, view.me_view) if view.me_view is not None else False
    if s is None:
        return False
    if k == "distance":
        return o is not None and v[0] <= abs(o["x"] - s["x"]) <= v[1]
    if k == "percent":
        return v[0] <= s["percent"] <= v[1]
    if k == "shield_below":
        return s["shield"] < v
    if k == "state":
        return state_is(s, v, view.char)
    if k == "lag":
        return committed(s) and view.lag is not None and view.lag >= v
    raise ValueError("unknown condition %r" % k)


# ---- the game's part: ranges and lag ----------------------------------------

# the attacks a range is made of: every ground attack and special, the
# grab, a dash attack out of the dash or run, short hops with each aerial
ATTACKS = ("jab,ftilt,utilt,dtilt,fsmash,usmash,dsmash,grab,dash_attack,"
           "sh_,down_b,neutral_b,side_b")
KINDS = ("hit", "shield", "grab")


def reach(n, port, target, frames=FRAMES, their=None, pre=None,
          attacks=ATTACKS, near=38, step=3):
    """Can `port` land an attack on `target` within `frames` frames, from
    standing or out of a dash or run toward it (the timing scan: the stick
    held K frames, then the attack)? `their`: the target's raw pads, frame
    by frame from now (None: it holds what it holds); `pre`: port's own
    pads first (it goes on doing what it does). The first line that
    connects, or None. Presses only within `near` units (no attack reaches
    further), every `step` frames of the hold."""
    if pre:
        preroll(n, pre)
    lead = len(pre or ())
    if their is not None:
        player(n, [(1, r) for r in their])
    try:
        r = search(n, port, target, horizon=lead + frames + 1, budget=0,
                   depth=1, then=attacks, scan=step, hold="none,in",
                   stop=1, trial=frames, enough=1, hit=100, lcancel=0,
                   near=near)
    finally:
        if their is not None:
            player(n, None)
    for line in r.lines:
        if line.contact in KINDS and line.contact_at <= lead + frames and \
                line.taken == 0:
            return line
    return None


def closest(n, port, target, raws):
    """The fighters' least distance (along the stage) while `port` plays
    `raws`, the target holding its pad: played ahead and undone."""
    from melee_actor.ahead import compress, look
    from melee_engine.opponent import raw_to_pad
    me, them = n.state()["p"][port], n.state()["p"][target]
    gap = abs(me["x"] - them["x"])
    if not raws:
        return gap
    out = look(n, port, target, compress([raw_to_pad(r) for r in raws]),
               stop=0)
    for row in out.rows:
        gap = min(gap, abs(row.a_x - row.t_x))
    return gap


def lag_of(n, port, target, most=90):
    """Frames before `port` can act again (free), letting go of its pad:
    played ahead and undone. `most` if it cannot within that."""
    from melee_actor.ahead import look
    f = n.state()["p"][port]
    if free(f):
        return 0
    out = look(n, port, target, [(most, {})], stop=0)
    for i, row in enumerate(out.rows):
        if row.a_state in FREE and row.a_hitlag <= 0:
            return i + 1
    return most


class Sense:
    """The opponent's view of the game, frame by frame: a short history of
    states (the player seen `react` frames late), and what the game's
    searches found (ranges, lag) by the frame they were found on.

    `think`: where the searches run (melee_engine.drill.Here, fork.InFork);
    None: no game (the ranges and lag unknown: tests of pure conditions).
    `half`: the stage's half width, to the ledge. `char`: the player's
    character id (state names that differ by character)."""

    def __init__(self, port, target, react=REACT, frames=FRAMES, cache=CACHE,
                 think=None, half=85.0, char=None):
        self.port, self.target = port, target
        self.react, self.frames, self.cache = react, frames, cache
        self.think = think
        self.half = half
        self.char = char
        self.frame = -1
        self.hist = collections.deque(maxlen=react + 3)
        # what the searches found, [(frame, value)]: "their" and "my", the
        # ranges; "guard", the player's range over `frames` + `cache`
        # frames, as the opponent plans to move (a body keeping out of it:
        # checked every `cache` frames, so with that much to spare); "lag"
        self.found = {"their": [], "my": [], "guard": [], "lag": []}
        self.detail = {}          # kind: (frame, the last search's dict)
        self.wants = set()
        self.pending = {}         # the job out: {"tag", "frame"}
        self.tag = 0
        self.ms = 0.0
        self.searches = 0
        self.their_pad = NONE

    # -- each frame -----------------------------------------------------------

    def update(self, st, their=None):
        """The frame's state (as it stands before this frame's inputs), once
        a frame; `their`: the player's raw pad this frame."""
        self.frame += 1
        p = st["p"]
        self.hist.append((self.frame, p[self.port], p[self.target]))
        if their is not None:
            self.their_pad = tuple(their)
        self._collect()

    def ask(self, plan=None, force=False):
        """Search what is wanted and due (each `cache` frames; `force`: now),
        all of it in one job (one fork while a person plays): `plan`, the
        opponent's raw pads from now (what it will do), for the player's
        range. Headless, found at once. One job at a time: a forced look
        while one is out waits for it."""
        if self.think is None or not self.wants or self.pending:
            return
        due = []
        for kind in sorted(self.wants):
            if not force and self.found[kind] and \
                    self.frame - self.found[kind][-1][0] < self.cache:
                continue
            if kind == "lag":
                _, _, them = self.hist[-1]
                if free(them):
                    self.found["lag"].append((self.frame, 0))
                    continue
            due.append(kind)
        if due:
            self._submit(due, list(plan or ()))
            self._collect()

    def _submit(self, kinds, plan):
        port, target, frames, cache = self.port, self.target, self.frames, \
            self.cache
        their = self.their_pad

        def one(n, kind):
            if kind in ("their", "guard"):
                # the player's side: can they hit me, as I plan to move?
                k = frames + (cache if kind == "guard" else 0)
                out = dict(gap=closest(n, port, target, plan[:k + 1])
                           if kind == "guard" and plan else None)
                line = reach(n, target, port, k,
                             their=plan[:k + 1] if plan else None)
                out.update(v=line is not None,
                           line=line.names if line else None)
                return out
            if kind == "my":
                line = reach(n, port, target, frames,
                             their=[r for k, r in expect(their, 3)
                                    for _ in range(k)])
                return dict(v=line is not None,
                            line=line.names if line else None)
            return dict(v=lag_of(n, target, port))

        def job(n):
            return {kind: one(n, kind) for kind in kinds}
        self.tag += 1
        tag = ("sense", id(self), self.tag)
        self.pending = dict(tag=tag, frame=self.frame)
        self.searches += 1
        self.think.submit(tag, job, "sense")

    def _collect(self):
        p = self.pending
        if not p or not self.think.ready(p["tag"]):
            return
        got = self.think.result(p["tag"])
        self.pending = {}
        for kind, out in (got or {}).items():
            self.found[kind].append((p["frame"], out["v"]))
            self.detail[kind] = (p["frame"], out)
            del self.found[kind][:-64]

    def forget(self):
        if self.pending:
            self.think.forget(self.pending["tag"])
        self.pending = {}

    # -- reading --------------------------------------------------------------

    def at(self, kind, frame):
        """What a search found for `frame`: the last found on or before it
        (the first found, before any was), or None."""
        got = self.found[kind]
        if not got:
            return None
        best = got[0][1]
        for f, v in got:
            if f > frame:
                break
            best = v
        return best

    def latest(self, kind):
        """The last found, and its frame: (frame, value), or None."""
        got = self.found[kind]
        return got[-1] if got else None

    def lag_at(self, frame):
        """Frames before the player can act, from `frame` on."""
        got = [(f, v) for f, v in self.found["lag"] if f <= frame]
        if not got:
            return None
        f, v = got[-1]
        return max(0, v - (frame - f))

    def seen(self):
        """(frame, the player as seen, the player a frame before that)."""
        h = self.hist
        i = max(0, len(h) - 1 - self.react)
        frame, _, them = h[i]
        _, _, before = h[max(0, i - 1)]
        return frame, them, before

    def views(self, after=0):
        """The views conditions are read on: the player as seen, and the
        opponent itself now ({"me": C})."""
        frame, them, before = self.seen()
        now, me, _ = self.hist[-1]
        _, me_before, _ = self.hist[max(0, len(self.hist) - 2)]
        ranges_now = {k: self.at(k, now) for k in ("their", "my")}
        mine = View(me, me_before, self.hist[-1][2], self.half, after,
                    ranges_now, None, None)
        theirs = View(them, before, me, self.half, after,
                      {k: self.at(k, frame) for k in ("their", "my")},
                      self.lag_at(now) if committed(them) else None,
                      self.char, mine)
        mine.me_view = mine
        return theirs

    def test(self, cond, after=0):
        """Does `cond` hold now, as the opponent sees it? (`after`: frames
        into the step.)"""
        if not self.hist:
            return False
        return holds(cond, self.views(after))
