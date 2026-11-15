"""The opponent's footwork: how a body moves on the ground as a good player
does, per character (docs/ai/opponent-vocabulary.md, `footsies`).

The owner, 2026-11-15, after playing fox-shine-oos: "the sheik is just
missing dash dances and in turn around lag". The body before planned dashes
of random lengths (3 to 9 frames), walks at a stick of 70 after them and
dashes again the same way: a dash held past the character's initial dash
is a run (Sheik's is 7 frames), a stick of 70 is a dash (the game reads
x / 80: 64 smashes), any stick toward the dash in its slide makes a run
too, and a run turned around is TurnRun, let go a RunBrake (measured with
gait.py: 9 to 47% of the body's frames, for every top character).

What the game does (the decomp, ftCo_Dash.c, ftCo_Turn.c, and played for
every character, `gait.py --calibrate`):

- a dash from standing ignores the stick turned back over its first 4
  frames (`p_ftCommonData->x44`), and a reversal pressed on its 2nd or 3rd
  frame is lost (a smash counts only on the frame it crosses the dead zone
  and the next); from the 5th frame the stick turned back is a one-frame
  Turn and, still held, a dash back;
- a dash back, or a dash out of a smash turn from standing, can be turned
  again from its 2nd frame;
- held toward the dash on its frame `dash` + 1 (Sheik 7, Fox 11, Marth
  15), the dash is a run; let go of, the dash plays out its animation
  (`anim` frames, 21 to 28) sliding, and in that slide the stick toward it
  again is a run too (no foxtrot before the dash is over); turned back in
  it, a dash back; flicked back for one frame, a pivot;
- a pivot (the turn not held) plays out a Turn of `pivot` frames (11)
  facing the other way: attacks, jumps, shields, no dash;
- from a walk a smash is no dash (the stick left the dead zone long ago);
- a wavedash: the jump squat (`squat` frames), the air dodge down and in
  or out on the next, LandingFallSpecial for `wd_lag` (10), sliding `wd`.

The body plans phrases (a dash dance of 2 to 5 dashes, a walk in, a
crouch, standing, a wavedash in or out, a shield) with a small model of
those rules (`Where`): each candidate is played on the model, kept only if
it never runs, never crosses the player, stays on the stage, and scored by
where it ends (the band of distances, facing the player); one of the best
by a softmax. Dash lengths are drawn inside each character's window, a
rhythm per dance (tight, wide or mixed). The table of each character's
numbers is footwork.json, measured by `gait.py --calibrate --write`.
"""
import json
import math
import os
import random

NONE = (0, 0, 0, 0, 0, 0, 0)
SHIELD = (0x20, 0, 0, 0, 0, 0, 255)
CROUCH = (0, 0, -127, 0, 0, 0, 0)
JUMP = (0x400, 0, 0, 0, 0, 0, 0)

HERE = os.path.dirname(os.path.abspath(__file__))

# CharacterKind (the state's "ckind") by data/ character id
CKIND = {
    "captain-falcon": 0x00, "donkey-kong": 0x01, "fox": 0x02,
    "mr-game-and-watch": 0x03, "kirby": 0x04, "bowser": 0x05, "link": 0x06,
    "luigi": 0x07, "mario": 0x08, "marth": 0x09, "mewtwo": 0x0A,
    "ness": 0x0B, "peach": 0x0C, "pikachu": 0x0D, "ice-climbers": 0x0E,
    "jigglypuff": 0x0F, "samus": 0x10, "yoshi": 0x11, "zelda": 0x12,
    "sheik": 0x13, "falco": 0x14, "young-link": 0x15, "dr-mario": 0x16,
    "roy": 0x17, "pichu": 0x18, "ganondorf": 0x19,
}
CHAR_OF = {v: k for k, v in CKIND.items()}

# a character with no row (Fox's numbers, a common shape)
DEFAULT = dict(accel=0.1, anim=21, dash=11, fric=0.08, guard_off=15,
               keep=0.2, pivot=11, squat=4, squat_rv=10, vinit=1.6,
               vmax=1.8, walk=0.8, wd=20.0, wd_lag=10)

_TABLE = None


def table():
    global _TABLE
    if _TABLE is None:
        try:
            with open(os.path.join(HERE, "footwork.json")) as f:
                _TABLE = json.load(f)
        except (OSError, ValueError):
            _TABLE = {}
    return _TABLE


def numbers(char):
    return dict(DEFAULT, **table().get(char, {}))


# What each character's players do more or less of (a weight's factor):
# Peach and Jigglypuff wavedash short and seldom, Sheik and Samus crouch,
# Yoshi cannot jump out of his shield (and his is another state), the
# spacies and Marth dash dance and wavedash the most.
STYLE = {
    "jigglypuff": dict(wavedash=0.25, walk=1.4, stand=1.2),
    "peach": dict(wavedash=0.4, walk=1.6, crouch=1.3),
    "sheik": dict(crouch=1.6, wavedash=1.2),
    "samus": dict(crouch=1.4, wavedash=1.3, dance=0.8),
    "yoshi": dict(shield=0.0, wavedash=0.8),
    "fox": dict(dance=1.2, wavedash=1.3, walk=0.6),
    "falco": dict(dance=1.1, wavedash=1.3, walk=0.7),
    "marth": dict(dance=1.3, wavedash=1.1),
    "captain-falcon": dict(dance=1.3, walk=0.6),
    "ice-climbers": dict(wavedash=1.2),
    "pikachu": dict(dance=1.1),
}

# action states (ftCommon)
WAIT, WALKS, TURN, TURN_RUN, DASH, RUN, RUN_BRAKE = 14, (15, 16, 17), 18, \
    19, 20, (21, 22), 23
KNEEBEND, SQUAT, SQUAT_WAIT, SQUAT_RV = 24, 39, 40, 41
LANDING, LANDING_SPECIAL = 42, 43
GUARDS = (178, 179, 182)
GUARD_OFF = 180

# The stick in raw pad units: the game reads x / 80, clamped to 1
# (played: from standing 23 stands, 24 walks, 63 walks, 64 dashes; in a
# dash's slide 48 walks after it, 50 runs; 55 down stands, 60 crouches)
DEAD = 23           # the dead zone (0.2875)
SMASH = 64          # a smash: past 0.8
RUNS = 50           # held toward a dash past its window: a run (0.62)
DOWN = -60          # a crouch
WALKS_LX = (30, 40, 50, 60)     # walking speeds (under a smash)


def sign(v):
    return 1 if v > 0 else -1 if v < 0 else 0


def jumps(raw):
    return bool(raw[0] & 0xC00)


def guards(raw):
    return bool(raw[0] & 0x60) or max(raw[5], raw[6]) >= 43


# ---- the model --------------------------------------------------------------

class Where:
    """Where the body's pads leave the fighter, as the game would: its mode
    (wait, walk, dash, ddturn: the one-frame turn of a dash dance, turn: a
    pivot played out, squat, squatrv, kneebend, landsp, guard, guardoff,
    run: never planned, busy: anything else), facing, x, ground speed,
    frames in the mode (`age`), whether a dash turns from its 2nd frame
    (`back`) or its 5th, and the stick's last x (a smash counts on the
    frame it leaves the dead zone and the next)."""

    __slots__ = ("c", "mode", "facing", "x", "v", "age", "back", "held",
                 "lx", "out", "left", "bad", "state")

    def __init__(self, c, mode="wait", facing=1, x=0.0, v=0.0):
        self.c = c
        self.mode, self.facing, self.x, self.v = mode, facing, x, v
        self.age = 1
        self.back = False
        self.held = False           # a dash's stick still held toward it
        self.lx = 0
        self.out = 9                # frames since the stick left the dead
        #                             zone on its side
        self.left = 0
        self.bad = None             # what went wrong (a run), if anything
        self.state = None           # the game's state, when read from it

    def copy(self):
        w = Where.__new__(Where)
        for k in Where.__slots__:
            setattr(w, k, getattr(self, k))
        return w

    # what the game's state would be (a coarse class, compared with the
    # real one to see the plan still holds)
    def cls(self):
        m = self.mode
        if m in ("wait", "walk", "squatrv"):
            return "stand"
        if m == "ddturn":
            return "turn"
        return m

    @property
    def standing(self):
        return self.mode in ("wait", "walk", "squatrv")

    def can_reverse(self):
        """The stick turned back on the coming frame turns the dash."""
        return self.mode == "dash" and (self.back or self.age >= 4)

    def over(self):
        """The mode is over with the coming frame (its input is read in
        the next state: Fighter_procAnim runs before Fighter_procInput)."""
        c, m = self.c, self.mode
        return (m == "dash" and self.age >= c["anim"]) or \
            (m == "turn" and self.age >= self.left) or \
            (m == "landsp" and self.age >= c["wd_lag"]) or \
            (m == "guardoff" and self.age >= c["guard_off"]) or \
            (m == "squatrv" and self.age >= c["squat_rv"])

    def now(self):
        """The mode the coming frame's input is read in."""
        if self.over():
            self.mode, self.age = "wait", 0
        return self

    def _slow(self):
        f = self.c["fric"]
        self.v = 0.0 if abs(self.v) <= f else self.v - sign(self.v) * f

    def _dash_start(self, way, back):
        self.mode, self.facing, self.age, self.back = "dash", way, 1, back
        self.held = True
        vi = self.c["vinit"]
        old = self.v
        self.v = (self.v + way * vi) if self.v * way < 0 else way * vi
        # (a dash's first frame moves at the speed it had: the new one
        # from its second)
        self.x += old - self.v

    def step(self, raw):
        """The frame played with `raw`."""
        c = self.c
        lx, ly = raw[1], raw[2]
        # the smash timer: a stick past 0.8 is a smash on the frame it left
        # the dead zone (or crossed to this side) and the next
        if abs(lx) < DEAD or sign(lx) != sign(self.lx) or abs(self.lx) < DEAD:
            out = 0 if abs(lx) >= DEAD else 9
        else:
            out = self.out + 1
        smash = abs(lx) >= SMASH and out <= 1
        self.lx, self.out = lx, out
        m = self.now().mode
        way = sign(lx)
        if m in ("wait", "walk", "squatrv"):
            if jumps(raw):
                self.mode, self.age = "kneebend", 1
                self._slow()
            elif guards(raw):
                self.mode, self.age = "guard", 1
                self._slow()
            elif smash and m == "squatrv":
                self.mode, self.age = "walk", 1    # a frame of walk first
                self._slow()
            elif smash:
                if way == self.facing:
                    self._dash_start(way, False)
                else:
                    # a smash turn: a frame of Turn, the dash out of it
                    self.mode, self.age = "ddturn", 1
                    self.v *= c["keep"]
            elif ly <= DOWN:
                self.mode, self.age = "squat", 1
                self._slow()
            elif abs(lx) >= DEAD and m != "walk" and way != self.facing:
                # a slow turn (never planned)
                self.mode, self.age, self.left = "turn", 1, c["pivot"]
                self.facing = way
                self.bad = self.bad or "slow turn"
            elif abs(lx) >= DEAD:
                if m != "walk":
                    self.mode, self.age = "walk", 0
                self.age += 1
                target = c["walk"] * min(1.0, abs(lx) / 60.0) * self.facing
                self.v += max(-0.07, min(0.07, target - self.v))
            else:
                if m == "walk":
                    self.mode, self.age = "wait", 0
                self.age += 1
                self._slow()
        elif m == "dash":
            nxt = self.age + 1
            back = lx * self.facing <= -SMASH
            if jumps(raw):
                self.mode, self.age = "kneebend", 1
            elif guards(raw):
                if self.back or nxt > 2:
                    self.mode, self.age = "guard", 1
                    self._slow()
                else:
                    self.mode, self.bad = "busy", "roll"
            elif back and smash and (self.back or nxt >= 5):
                self.mode, self.age = "ddturn", 1
                self.v *= c["keep"]
            elif back:
                # turned back too soon (a dash's first 4 frames), or held
                # back past its smash: the game does nothing with it
                self.bad = self.bad or "ignored"
                self.age = nxt
                self.held = False
                self._slow()
            elif nxt >= c["dash"] + 1 and lx * self.facing >= RUNS:
                self.mode, self.age, self.bad = "run", 1, "run"
            else:
                self.age = nxt
                if lx * self.facing >= RUNS:
                    if not self.held:
                        self.bad = self.bad or "run"   # (toward in a slide)
                    a, vmax = c["accel"], c["vmax"]
                    s = abs(self.v) + a
                    s = min(s, vmax) if a >= 0 else max(s, vmax)
                    self.v = s * self.facing
                else:
                    self.held = False
                    self._slow()
        elif m == "ddturn":
            new = -self.facing
            if lx * new >= SMASH:
                self._dash_start(new, True)
            elif jumps(raw):
                self.facing = new
                self.mode, self.age = "kneebend", 1
            else:
                self.facing = new
                self.mode, self.age, self.left = "turn", 2, c["pivot"]
                self._slow()
        elif m == "turn":
            if jumps(raw):
                self.mode, self.age = "kneebend", 1
            elif guards(raw):
                self.mode, self.age = "guard", 1
            else:
                self.age += 1
            self._slow()
        elif m == "kneebend":
            if self.age >= c["squat"]:
                if guards(raw) and raw[2] < -30:
                    # the air dodge on the first airborne frame: landed
                    self.mode, self.age = "landsp", 1
                    w = sign(raw[1])
                    v0 = math.sqrt(2.0 * c["fric"] * c["wd"])
                    self.v = self.v * 0.5 + w * v0
                else:
                    self.mode, self.age, self.bad = "busy", 1, "jump"
            else:
                self.age += 1
                self._slow()
        elif m == "landsp":
            self.age += 1
            self._slow()
        elif m == "squat":
            if ly <= DOWN:
                self.age += 1
            else:
                self.mode, self.age = "squatrv", 1
            self._slow()
        elif m == "guard":
            if guards(raw):
                self.age += 1
            else:
                self.mode, self.age = "guardoff", 1
            self._slow()
        elif m == "guardoff":
            self.age += 1
            self._slow()
        else:                       # run, busy: not modelled
            self.age += 1
            self._slow()
        self.x += self.v
        return self


def play(w, pads):
    """`w` after `pads` (a copy), and the farthest |x| and the closest
    approach to `them` it passes (filled in by the caller's check)."""
    w = w.copy()
    xs = []
    for raw in pads:
        w.step(raw)
        xs.append(w.x)
    return w, xs


# ---- the real fighter, as the model sees it ---------------------------------

class Seen:
    """The real fighter's history, frame by frame: how long it has been in
    its state, whether its dash came out of a turn, the pads it was given
    (for a smash's timing)."""

    def __init__(self):
        self.state = None
        self.facing = None
        self.age = 0
        self.back = False
        self.lx = 0
        self.out = 9
        self._st = None

    def update(self, st, me):
        if st is self._st:
            return                  # (this frame's already)
        self._st = st
        s, f = me["state"], me["facing"]
        if s == self.state and (s != DASH or f == self.facing):
            self.age += 1
        else:
            if s == DASH:
                self.back = self.state == TURN or (
                    self.state == DASH and f != self.facing)
            self.age = 1
        self.state, self.facing = s, f

    def sent(self, raw):
        lx = raw[1]
        if abs(lx) < DEAD or sign(lx) != sign(self.lx) or abs(self.lx) < DEAD:
            self.out = 0 if abs(lx) >= DEAD else 9
        else:
            self.out += 1
        self.lx = lx


def where_of(me, seen, c):
    """The model's Where for the real fighter `me` now."""
    s = me["state"]
    w = Where(c, facing=me["facing"], x=me["x"],
              v=me.get("gvel", me.get("vx", 0.0)))
    w.lx, w.out = seen.lx, seen.out
    w.age = max(1, seen.age)
    w.state = s
    k = cls_of(me, c)
    if k == "stand":
        w.mode = "walk" if s in WALKS else "squatrv" if s == SQUAT_RV \
            else "wait"
    elif k == "dash":
        w.mode, w.back = "dash", seen.back
        w.held = seen.lx * me["facing"] >= RUNS
    elif k == "turn":
        if seen.age <= 1 and abs(seen.lx) >= SMASH and \
                sign(seen.lx) != me["facing"]:
            w.mode = "ddturn"
        else:
            w.mode, w.left = "turn", c["pivot"]
    elif k in ("squat", "kneebend", "landsp", "guard", "guardoff", "run"):
        w.mode = k
    else:
        w.mode = "busy"
    return w


def cls_of(me, c=None):
    """The real state's class, as Where.cls() names them."""
    s = me["state"]
    if me.get("air"):
        return "busy"
    if s == WAIT or s in WALKS or s == SQUAT_RV:
        return "stand"
    if s == DASH:
        return "dash"
    if s == TURN:
        return "turn"
    if s in (SQUAT, SQUAT_WAIT):
        return "squat"
    if s == KNEEBEND:
        return "kneebend"
    if s == LANDING_SPECIAL:
        return "landsp"
    yoshi = c is not None and c.get("yoshi")
    if s in GUARDS or (yoshi and 341 <= s <= 344):
        return "guard"
    if s == GUARD_OFF or (yoshi and s == 345):
        return "guardoff"
    if s in RUN:
        return "run"
    return "busy"


# the model's class for a frame, against the real one: these may end
# sooner than the model has them, the pads after them still right
LOOSE = {("turn", "stand"), ("landsp", "stand"), ("guardoff", "stand"),
         ("squat", "stand"), ("guard", "guardoff")}


# ---- the body ---------------------------------------------------------------

class Footsies:
    """Moving as a good player waiting to approach does: dash dances whose
    turns come inside the initial dash, at a rhythm and length that vary,
    pivots and let-go dashes that stop without a skid, walks in, crouches,
    standing, wavedashes in and out, now and then a shield; keeping to a
    band of distances from the target and on the stage, ending its phrases
    facing the target. Its pads are planned some frames ahead (`ahead`),
    so a decision can be thought out for where they lead, and kept to while
    the fighter does what they were planned to do (`next` compares the
    game's state with the plan's each frame, and plans again from where the
    fighter really is when they differ).

    band: (LO, HI) units from the target; half: the stage's half width;
    crouch: crouches among the phrases; char: the character (by default
    read from the state)."""

    TRIES = 9           # candidate phrases drawn each time one is planned
    LEDGE = 12.0        # units from the stage's end it keeps out of
    CLOSE = 7.0         # units from the target it never comes inside

    def __init__(self, port, target, band=(35.0, 60.0), rng=None,
                 half=70.0, crouch=True, char=None):
        self.port, self.target = port, target
        self.band = band
        self.rng = rng or random.Random(0)
        self.half = half
        self.crouch = crouch
        self.char = char
        self.c = None
        self.queue = []          # raw pads planned
        self.expect = []         # the model's class after each of them
        self.end = None          # Where the queue leaves the fighter
        self.want = None         # the class the last pad was to lead to,
        #                          and where
        self.seen = Seen()
        self.moved = 0           # frames the stick was not neutral
        self.last_lx = 0
        self.kinds = []          # the phrases planned, in order
        self.resyncs = 0
        self.rejected = 0
        self.errs = []           # the model's x against the game's, a frame
        self.them_v = 0.0        # the target's speed when last planned

    # -- the character -----------------------------------------------------

    def _char(self, me):
        if self.c is None:
            if self.char is None:
                self.char = CHAR_OF.get(me.get("ckind"))
            self.c = numbers(self.char)
            self.c["yoshi"] = self.char == "yoshi"
        return self.c

    # -- planning ------------------------------------------------------------

    def _real(self, st):
        me = st["p"][self.port]
        self._char(me)
        self.seen.update(st, me)
        return where_of(me, self.seen, self.c)

    def _append(self, w, pads, kind):
        for raw in pads:
            w.step(raw)
            self.queue.append(tuple(raw))
            self.expect.append((w.cls(), w.x))
        self.end = w
        self.kinds.append(kind)

    # modes the model cannot see the end of: nothing is planned after them
    # until the game shows where they ended
    BLIND = ("busy", "run")

    def extend(self, st):
        """Plan one more phrase after the queue. The pads added (none
        while the queue ends where the model cannot follow)."""
        if self.queue and self.end is not None:
            if self.end.mode in self.BLIND:
                return 0
            w = self.end.copy()
        else:
            w = self._real(st)
        them = st["p"][self.target]
        self.them_v = 0.0 if them.get("air") else \
            (them.get("gvel", them.get("vx", 0.0)) or 0.0)
        pads, kind = self._phrase(w, them["x"])
        self._append(w, pads, kind)
        return len(pads)

    def ahead(self, st, k):
        """The next `k` pads, planned now (and kept to)."""
        for _ in range(64):
            if len(self.queue) >= k or not self.extend(st):
                break
        return list(self.queue[:k]) + [NONE] * (k - len(self.queue))

    def _segment(self, st):
        """(The old interface: the next phrase's pads, queued.)"""
        before = len(self.queue)
        self.extend(st)
        return list(self.queue[before:])

    def replace(self, pads_of, st, kind):
        """Drop what is planned and play `pads_of(where)` from now, planned
        from where the fighter really is."""
        w = self._real(st)
        pads = pads_of(w)
        self.queue, self.expect, self.end = [], [], None
        self._append(w, pads, kind)

    def forget(self):
        """Drop what is planned (a line given up part way leaves the fighter
        where the plan never had it): the next pad is planned from where the
        fighter really is."""
        self.queue, self.expect, self.end, self.want = [], [], None, None

    def next(self, st):
        me = st["p"][self.port]
        if me is not None:
            self._char(me)
            self.seen.update(st, me)
            real = cls_of(me, self.c)
            want = self.want[0] if self.want is not None else None
            if self.want is not None:
                # where the model has it against the game: the plan's
                # positions moved by the difference (the model's error a
                # frame, not added up over phrases planned ahead)
                err = me["x"] - self.want[1]
                self.errs.append(err)
                if err:
                    self.expect = [(k, x + err) for k, x in self.expect]
                    if self.end is not None:
                        self.end.x += err
            if want is not None and self.queue and real != want and \
                    want not in ("busy", "run") and \
                    (want, real) not in LOOSE:
                # the fighter is not where the plan has it (hit, pushed, a
                # state the model has wrong): planned again from here
                self.queue, self.expect, self.end = [], [], None
                self.resyncs += 1
        if not self.queue:
            self.extend(st)
        raw = self.queue.pop(0) if self.queue else NONE
        self.want = self.expect.pop(0) if self.expect else None
        if not self.queue:
            self.end = None
        self.seen.sent(raw)
        self.moved += raw[1] != 0
        self.last_lx = raw[1]
        return raw

    def retreat(self, st):
        """Away from the target now, ending facing it (`outside`'s answer
        to a plan that would take it into the target's range): the best
        retreat on the model, or standing still with the ledge behind. In a
        jump squat, the wavedash out; in a landing, a shield let go of or
        anything the model cannot steer, the plan as it is."""
        them_x = st["p"][self.target]["x"]
        now = self._real(st).now()
        if now.mode in ("landsp", "guardoff", "guard", "busy", "run"):
            return list(self.queue)
        if now.mode == "kneebend":
            self.replace(lambda w: self._land(
                w, -self._toward(w, them_x)), st, "retreat")
            return list(self.queue)

        def pads_of(w):
            w = w.copy().now()
            cands = []
            for _ in range(self.TRIES + 4):
                pads = self._away(w, them_x)
                if not pads:
                    continue
                score = self._score(w, pads, them_x, "retreat", away=True)
                if score is not None:
                    cands.append((score, pads))
            if not cands:
                return [NONE] * 6
            best = max(sc for sc, _ in cands)
            return self.rng.choice([p for sc, p in cands if sc == best])
        self.replace(pads_of, st, "retreat")
        return list(self.queue)

    # -- phrases ---------------------------------------------------------------

    def _phrase(self, w, them_x):
        """One phrase from `w`: one of TRIES candidates, by a softmax over
        their scores ((pads, kind))."""
        rng = self.rng
        w.now()
        if w.mode in ("busy", "kneebend", "landsp", "guardoff", "run"):
            return self._settle(w, them_x), "settle"
        if w.mode == "guard":
            return [NONE], "unshield"
        cands = []
        kinds = self._kinds(w, them_x)
        for _ in range(self.TRIES):
            kind = rng.choices([k for k, _ in kinds],
                               weights=[p for _, p in kinds])[0]
            pads = getattr(self, "_" + kind)(w, them_x)
            if not pads:
                continue
            score = self._score(w, pads, them_x, kind)
            if score is None:
                self.rejected += 1
                continue
            cands.append((score, kind, pads))
        if not cands:
            return self._safe(w, them_x), "safe"
        best = max(sc for sc, _, _ in cands)
        weights = [math.exp((sc - best) / 0.6) for sc, _, _ in cands]
        _, kind, pads = rng.choices(cands, weights=weights)[0]
        return pads, kind

    def _kinds(self, w, them_x):
        """The kinds of phrase that can start from `w`, and their weights."""
        st = STYLE.get(self.char, {})
        d = abs(them_x - w.x)
        lo, hi = self.band
        close = d < lo + 4.0

        def wt(k, p):
            return (k, p * st.get(k, 1.0))
        if w.mode in ("wait", "walk"):
            ks = [wt("dance", 0.45), wt("stand", 0.08), wt("walk", 0.10),
                  wt("wavedash", 0.08), wt("dash", 0.10),
                  wt("shield", 0.025 if close else 0.006)]
            if self.crouch:
                ks.append(wt("crouch", 0.05))
        elif w.mode == "dash":
            ks = [wt("dance", 0.55), wt("let_go", 0.15), wt("pivot", 0.15),
                  wt("wavedash", 0.12)]
        elif w.mode in ("turn", "ddturn"):
            ks = [wt("stand", 0.7), wt("wavedash", 0.15),
                  wt("shield", 0.02 if close else 0.004)]
        elif w.mode == "squat":
            ks = [wt("stand", 0.3), wt("crouch", 0.4)]
        else:                    # squatrv
            ks = [wt("stand", 0.8), wt("wavedash", 0.2)]
        return [(k, p) for k, p in ks if p > 0]

    @staticmethod
    def _toward(w, them_x):
        return 1 if them_x >= w.x else -1

    def _want(self, w, them_x):
        """+1 to close in, -1 to back off, 0 to stay (the band)."""
        d = abs(them_x - w.x)
        lo, hi = self.band
        return 1 if d > hi else -1 if d < lo else 0

    def _lens(self, w, way, n, them_x):
        """A dash dance's leg lengths (the frames the stick is held each
        way, a dash back's turn counted), its first leg `way`: inside each
        dash's window, a rhythm drawn for the dance (tight, wide, mixed),
        the legs the band wants longer, the others shorter."""
        c, rng = self.c, self.rng
        D = c["dash"]
        style = rng.choice(("tight", "wide", "mixed", "mixed"))
        want = self._want(w, them_x)
        toward = self._toward(w, them_x)
        out = []
        cur = way
        for i in range(n):
            if i == 0 and w.mode in ("wait", "walk") and way == w.facing:
                lo, hi = 4, D            # from standing: turns on its 5th
            else:
                lo, hi = 2, D + 1        # a dash back, or out of a smash
                #                          turn: from its 2nd
            hi = min(hi, lo + 10)
            if style == "tight":
                k = rng.randint(lo, min(hi, lo + 2))
            elif style == "wide":
                k = rng.randint(max(lo, hi - 3), hi)
            else:
                k = rng.randint(lo, hi)
            if want and cur == want * toward:
                k = min(hi, k + rng.randint(0, 3))
            elif want:
                k = max(lo, k - rng.randint(0, 3))
            out.append(k)
            cur = -cur
        return out

    def _pre(self, w):
        """Pads before a dash dance can start from `w`: a walk let go of, a
        dash held (or let slide) to the frame it may be turned."""
        if w.mode == "walk" or (w.mode == "wait" and abs(w.lx) >= DEAD):
            return [NONE]
        if w.mode == "dash" and not w.can_reverse():
            hold = (0, 127 * w.facing, 0, 0, 0, 0, 0) if w.held else NONE
            return [hold] * (4 - w.age)
        return []

    def _dance(self, w, them_x):
        """A dash dance: 2 to 5 dashes, each turned inside its window, then
        let go of (a dash toward), a pivot (after one away) or a wavedash
        out of the last."""
        rng = self.rng
        toward = self._toward(w, them_x)
        if w.mode == "dash":
            first = -w.facing           # the turn of the dash it is in
        elif w.mode in ("wait", "walk"):
            want = self._want(w, them_x)
            first = (toward if want > 0 else -toward if want < 0 else
                     rng.choice((toward, -toward)))
        else:
            return None
        pre = self._pre(w)
        n = rng.choices((2, 3, 4, 5), weights=(3, 4, 3, 2))[0]
        lens = self._lens(w, first, n, them_x)
        pads = list(pre)
        cur = first
        for k in lens:
            pads += [(0, 127 * cur, 0, 0, 0, 0, 0)] * k
            cur = -cur
        last = -cur
        end = rng.random()
        if end < 0.25:
            return pads                         # on into the next phrase,
            #                                     the dash still held
        if last == toward:
            if end < 0.8:
                pads.append(NONE)               # let go: its slide, facing in
            else:
                pads += self._wd_pads(-toward)  # out of it, facing in
        else:
            if end < 0.65:
                pads += [(0, 127 * toward, 0, 0, 0, 0, 0), NONE]   # pivot
            elif end < 0.85:
                pads += [(0, 127 * toward, 0, 0, 0, 0, 0)] * rng.randint(
                    2, 4) + [NONE]              # a last dash in, let go
            else:
                pads.append(NONE)
        return pads

    def _dash(self, w, them_x):
        """One dash, let go of inside its window (its slide is the stop),
        or turned into a pivot after one away."""
        if w.mode not in ("wait", "walk"):
            return None
        rng = self.rng
        toward = self._toward(w, them_x)
        want = self._want(w, them_x)
        way = toward if want > 0 or (want == 0 and rng.random() < 0.5) \
            else -toward
        D = self.c["dash"]
        pre = self._pre(w)
        k = rng.randint(4, D) if way == w.facing else rng.randint(2, D + 1)
        pads = pre + [(0, 127 * way, 0, 0, 0, 0, 0)] * k
        if way != toward:
            pads += [(0, 127 * toward, 0, 0, 0, 0, 0), NONE]       # pivot
        else:
            pads.append(NONE)
        return pads

    def _let_go(self, w, them_x):
        if w.mode != "dash":
            return None
        return [NONE] * self.rng.randint(1, 5)

    def _pivot(self, w, them_x):
        """A flick back in a dash away: it stands, facing the target."""
        if w.mode != "dash":
            return None
        toward = self._toward(w, them_x)
        if w.facing == toward:
            return None
        pre = self._pre(w)
        if pre and pre[0] != NONE:
            pre = [NONE] * len(pre)
        return pre + [(0, 127 * toward, 0, 0, 0, 0, 0), NONE]

    def _walk(self, w, them_x):
        """A walk in (facing the target), let go of."""
        if w.mode not in ("wait", "walk"):
            return None
        toward = self._toward(w, them_x)
        if w.facing != toward or self._want(w, them_x) < 0:
            return None
        lx = self.rng.choice(WALKS_LX) * toward
        return [(0, lx, 0, 0, 0, 0, 0)] * self.rng.randint(6, 22) + [NONE]

    def _crouch(self, w, them_x):
        if w.mode not in ("wait", "walk", "squat"):
            return None
        return [CROUCH] * self.rng.randint(5, 16) + [NONE]

    def _stand(self, w, them_x):
        if w.mode in ("turn", "ddturn"):
            left = max(1, self.c["pivot"] - w.age)
            return [NONE] * (left + self.rng.randint(0, 4))
        if w.mode == "squat":
            return [NONE]
        if w.mode == "squatrv":
            return [NONE] * max(1, self.c["squat_rv"] - w.age + 1)
        return [NONE] * self.rng.randint(3, 12)

    def _wd_pads(self, way):
        c = self.c
        return [JUMP] + [NONE] * (c["squat"] - 1) + \
            [(0x20, 100 * way, -80, 0, 0, 0, 255)] + \
            [NONE] * (c["wd_lag"] - 1)

    def _wavedash(self, w, them_x):
        """A wavedash in or out, facing as it was."""
        if w.mode not in ("wait", "walk", "dash", "turn", "squatrv"):
            return None
        toward = self._toward(w, them_x)
        want = self._want(w, them_x)
        way = toward if want > 0 else -toward if want < 0 else \
            self.rng.choice((toward, -toward))
        return self._wd_pads(way)

    def _shield(self, w, them_x):
        if w.mode not in ("wait", "walk", "turn"):
            return None
        return [SHIELD] * self.rng.randint(5, 12) + [NONE]

    def _away(self, w, them_x):
        """A retreat from `w`: a wavedash out (facing as it was), a dash
        away and a pivot back, or the dash it is in turned away."""
        rng = self.rng
        toward = self._toward(w, them_x)
        D = self.c["dash"]
        if w.mode in ("busy", "landsp", "guardoff", "run", "guard",
                      "squat"):
            return [NONE] * 4
        if w.mode == "kneebend":
            return self._land(w, -toward)
        if w.mode in ("turn", "ddturn", "squatrv") or rng.random() < 0.25:
            return self._wd_pads(-toward)
        pre = self._pre(w)
        if w.mode == "dash" and w.facing == -toward:
            k = rng.randint(0, max(0, min(4, D - w.age))) if w.held else 0
            pads = pre + [(0, -127 * toward, 0, 0, 0, 0, 0)] * k
        else:
            k = rng.randint(2, min(D + 1, 9))
            if w.mode in ("wait", "walk") and w.facing == -toward:
                k = rng.randint(4, min(D, 9))
            pads = pre + [(0, -127 * toward, 0, 0, 0, 0, 0)] * k
        if rng.random() < 0.3:
            # a dash back in, short, let go of (the dance goes on)
            return pads + [(0, 127 * toward, 0, 0, 0, 0, 0)] * rng.randint(
                2, 3) + [NONE]
        return pads + [(0, 127 * toward, 0, 0, 0, 0, 0), NONE]   # pivot

    def _land(self, w, way):
        """In a jump squat: the air dodge `way` on its first airborne
        frame (a wavedash), its landing waited out."""
        c = self.c
        return [NONE] * max(0, c["squat"] - w.age) + \
            [(0x20, 100 * way, -80, 0, 0, 0, 255)] + [NONE] * (c["wd_lag"] - 1)

    def _settle(self, w, them_x=None):
        """Busy (a landing, a jump squat, a shield let go of): waited out
        (a jump squat as a wavedash); out of a run, a crouch (one frame of
        RunBrake, then a squat) rather than a turn; hanging on the ledge,
        the stick toward the stage (a getup); in the air off the stage,
        drifting back."""
        c = self.c
        if w.mode == "kneebend":
            way = -sign(w.x) or 1
            if them_x is not None:
                way = -self._toward(w, them_x) if \
                    abs(them_x - w.x) < self.band[0] else \
                    self._toward(w, them_x)
            return self._land(w, way)
        if w.mode == "run":
            return [CROUCH] * 6 + [NONE]
        if w.mode == "landsp":
            return [NONE] * max(1, c["wd_lag"] - w.age)
        if w.mode == "guardoff":
            return [NONE] * max(1, c["guard_off"] - w.age)
        home = -sign(w.x) or 1
        if w.state in (252, 253):                    # CliffCatch, CliffWait
            return [(0, 127 * home, 0, 0, 0, 0, 0), NONE]
        if w.mode == "busy" and abs(w.x) > self.half - 4.0:
            return [(0, 127 * home, 0, 0, 0, 0, 0)]  # drift back
        return [NONE]

    def _safe(self, w, them_x):
        """Nothing passed: toward the stage's middle, or stand."""
        if w.mode in ("wait", "walk") and \
                abs(w.x) > self.half - self.LEDGE - 6:
            way = -sign(w.x)
            return [NONE] + [(0, 127 * way, 0, 0, 0, 0, 0)] * 4 + [NONE]
        return [NONE] * 3

    def _score(self, w, pads, them_x, kind, away=False):
        """A candidate's worth (None: never): played on the model and on
        through its slide; kept on the stage, out of the target, and never
        running or turning back where the game ignores it; ending in the
        band (`away`: as far as it gets), facing the target."""
        end, xs = play(w, pads)
        if end.bad is not None:
            return None
        coast = end.copy()
        for _ in range(30):
            # on through its slide (a dash let go of, a wavedash's)
            if coast.mode in ("busy", "run") or abs(coast.v) < 0.05:
                break
            coast.step(NONE)
            xs.append(coast.x)
        side = sign(them_x - w.x) or 1
        limit = self.half - self.LEDGE
        d0 = abs(them_x - w.x)
        close = min(self.CLOSE, d0 - 2.0)
        # the target goes on as it moves, slowing (a guess: it will not
        # keep on for long)
        v = max(-1.5, min(1.5, self.them_v)) * 0.7

        def tx(i):
            return them_x + v * min(i, 15)
        for i, x in enumerate(xs):
            if abs(x) > limit and abs(x) > abs(w.x):
                return None
            if (tx(i) - x) * side < close:
                return None
        lo, hi = self.band
        d = abs(tx(len(xs)) - coast.x)
        if away:
            # a retreat never comes closer than it is, and backs off to the
            # band (just out of the reach found), not as far as it can
            if any((them_x - x) * side < d0 - 1.0 for x in xs) or d <= d0:
                return None
        miss = max(0.0, lo - d, d - hi)
        score = -miss / 4.0
        if lo <= d <= hi:
            score -= abs(d - (lo + hi) / 2.0) / max(hi - lo, 1.0) * 0.5
        if end.facing * sign(them_x - end.x) > 0:
            score += 0.8
        if len(self.kinds) and self.kinds[-1] == kind:
            score -= 0.5
        if kind in ("stand", "crouch") and len(self.kinds) and \
                self.kinds[-1] in ("stand", "crouch", "shield"):
            score -= 0.6              # (still for long: not in neutral)
        return score
