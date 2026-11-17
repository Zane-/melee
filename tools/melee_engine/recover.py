"""Recovering: the opponent knocked off the stage finds its way back, as
well as the game allows, against what the player is doing about it
(docs/ai/melee-engine.md, "Recovering"; opponent-vocabulary.md, `recover`).

The owner, 2026-11-17: an edgeguard drill is "a big test of the engine
performance because it should be able to predict and adapt to the players
edgeguard. For example for fox, if it is firefox angling, and right before
the angle is locked in the player starts to drop and go for a bair to
cover the ledge, the CPU could change angle to go high. This should have
options for reaction time of the engine so the player can essentially
choose their own difficulty."

How it thinks. A way back (a route) is the controller, frame by frame,
from now until the fighter hangs from the ledge or stands on the stage:
drift, a jump, a special at an angle, drift again. The game itself says
what a route comes to: it is played ahead and undone ("route",
src/host/ahead.c), against the player going on with what they are doing
(their pad a few frames more, then let go: an attack begun plays out, a
ledge held stays held), and ends caught on the ledge, landed and free,
hit, or lost. Each time it decides, the opponent plays ahead the routes
its character has from where it is (`TOOLS`: the jumps it has left, its
specials, their angles and timings), scores them (the ledge or the stage
reached; a landing's lag near the player; how close the player's
hitboxes came; how long it flew with nothing left to change), and takes
one of the best by a softmax, the kinds of route it used lately drawn
less (never the same recovery twice). Where nothing reaches, the routes
that came nearest the ledge are tried again a frame or two earlier and
later.

What the player could do (`threats`). A route that ends well against a
player who does nothing more may still pass through where they can
strike. So each decision also plays the player ahead, alone, through the
attacks they have from where they are (in the air: each aerial and the
down special, now and a few frames on; on the ground: the smashes and
tilts), and keeps where their hitboxes were, frame by frame. A route that
crosses one at its frame is exposed to it; the more of them, the less
the route is worth. A player who has dropped below the ledge threatens
the ledge and no longer the stage above: the opponent goes high.

How it adapts. While it flies it checks its route again every few frames,
and decides again when the route no longer ends well or another is much
better. What the player commits to (a jump, a drop from the ledge, an
attack, the ledge taken) it sees only `react` frames after it began: the
drill's reaction time, the player's difficulty. Until then it goes on as
planned. A change of mind is only what the game still allows: Fire Fox's
angle until its charge ends, a jump not yet used, the drift.

    b = Recover(ctx, {"do": "recover"})
    raw = b.pad(n.state())        # once a frame, before the frame is played
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "melee_native"))

from native import CHARACTERS, Route  # noqa: E402

NONE = (0, 0, 0, 0, 0, 0, 0)
A, B, X, Z, R = 0x100, 0x200, 0x400, 0x10, 0x20
NAMES = {v: k for k, v in CHARACTERS.items()}

DEAD_LAST = 10                    # every death state is at or below this
REBIRTH = (11, 12, 13)
TUMBLE = 38
SPECIAL_FALL = (35, 36, 37)
DAMAGE = tuple(range(75, 92))
LEDGE = (252, 253)
LEDGE_ALL = tuple(range(252, 264))
# on the ground and free to act
STANDING = frozenset((14, 15, 16, 17, 18, 20, 21, 39, 40, 41, 178, 179))


# ---- the game, asked ------------------------------------------------------------

def _words(segs):
    return " ".join("%d %x %d %d %d %d %d %d" % ((k,) + tuple(raw))
                    for k, raw in segs if k > 0)


def route(n, port, target, plan, their=None, horizon=240, path=False):
    """`plan` ([(frames, raw pad)]) played ahead for `port` and undone,
    `target` playing `their` (None: holding its pad): a native.Route
    (`path`: with its `path`, the fighter's (x, y) after each frame). Any
    game answers it: the match, or a fork of it."""
    state = n.state()
    text = "%s %d %d %d %s" % ("routep" if path else "route", port, target,
                               horizon, _words(plan))
    if their:
        text += " | " + _words(their)
    reply = n._cmd(text)
    n._state = state                      # nothing changed
    return Route(reply)


def ledges(n):
    """The stage's ledges: ((x, y) left, (x, y) right)."""
    state = n.state()
    out = []
    for side in ("", " right"):
        x, y = n._cmd("ledge" + side).split()[:2]
        out.append((float(x), float(y)))
    n._state = state
    return tuple(out)


def segments(raws):
    """Per-frame raw pads as [(frames, raw)]."""
    out = []
    for r in raws:
        r = tuple(r)
        if out and out[-1][1] == r:
            out[-1] = (out[-1][0] + 1, r)
        else:
            out.append((1, r))
    return out


def frames(segs):
    """[(frames, raw)] as per-frame raw pads."""
    out = []
    for k, raw in segs:
        out += [tuple(raw)] * k
    return out


# ---- a route, written down ------------------------------------------------------

def stick(sx, sy, inward):
    """A stick position, `sx` toward the stage (1) or away (-1), as the
    pad's (-127..127)."""
    return (int(round(127 * max(-1.0, min(1.0, sx)) * inward)),
            int(round(127 * max(-1.0, min(1.0, sy)))))


def hold(k, sx=0.0, sy=0.0, buttons=0):
    return ("hold", int(k), buttons, sx, sy)


def press(buttons, sx=0.0, sy=0.0):
    return ("hold", 1, buttons, sx, sy)


def mash(k, button, sx=0.0, sy=0.0):
    """`button` pressed every other frame for `k` frames."""
    return ("mash", int(k), button, sx, sy)


def compile_steps(steps, inward):
    """A route's steps as [(frames, raw pad)]."""
    out = []
    for kind, k, buttons, sx, sy in steps:
        if k <= 0:
            continue
        lx, ly = stick(sx, sy, inward)
        rt = 255 if buttons & R else 0
        if kind == "mash":
            for i in range(k):
                out.append((1, (buttons if i % 2 == 0 else 0, lx, ly, 0, 0,
                                0, 0)))
        else:
            out.append((k, (buttons, lx, ly, 0, 0, 0, rt)))
    return segments(frames(out))


def angle_stick(deg):
    """The stick for a direction `deg` degrees above straight in (90: up,
    -90: down), full tilt."""
    r = math.radians(deg)
    return math.cos(r), math.sin(r)


# ---- what each character has ----------------------------------------------------

class Tool:
    """A special (or an air dodge) used on the way back. `press`: its
    input's stick (toward the stage, up). `steer`: None (the stick at one
    of `drift`, (toward the stage, up), during it), or "angle": the stick
    held at one of `angles` (degrees above straight in) or at the ledge
    (aimed from where the fighter is `lock` frames after the press) for
    `lock` + 6 frames. `button`: B, or R (an air dodge). `again`: B pressed
    again `again` frames after the first (Fox's and Falco's side special
    shortened), a variant each. `mash`: B pressed every other frame for
    that many frames (the Ice Climbers' side special rises with it).
    `helpless`: nothing can follow it (the fighter falls helpless after:
    the frames flown after it count against a route). `two`: (frames,
    angles): a second direction held from `frames` after the first is read
    (Pikachu's). `hold_for`: frames the stick is held after an unsteered
    press."""

    def __init__(self, name, press, steer=None, lock=0, angles=(),
                 drift=((1.0, 0.0),), button=B, again=(), mash=0,
                 helpless=True, hold_for=40, two=None):
        self.name, self.press, self.steer = name, press, steer
        self.lock, self.angles, self.drift = lock, tuple(angles), \
            tuple(drift)
        self.button, self.again, self.mash = button, tuple(again), mash
        self.helpless, self.hold_for, self.two = helpless, hold_for, two


SWEEP = (-60, -40, -20, 0, 20, 40, 60, 75, 90)
UP_B = (0.0, 1.0)
SIDE_B = (1.0, 0.0)
DOWN_B = (0.0, -1.0)
IN, HALF = (1.0, 0.0), (0.4, 0.0)
AIRDODGE = Tool("airdodge", (0.0, 0.0), steer="angle", lock=0,
                angles=(0, 30, 60, 90), button=R, hold_for=2)

# The specials each character recovers with (data/characters/*.md,
# "Recovery"). What a route may be is `candidates` below; what it comes to,
# the game says.
TOOLS = {
    # Fire Fox, Fire Bird: 42 frames of charge, the angle read on the 43rd
    # (data/drills/fox-firefox-angles.json); Illusion, Phantasm: B again on
    # one of its travel frames shortens it (fox-shorten.json)
    "fox": [Tool("up_b", UP_B, steer="angle", lock=43, angles=SWEEP),
            Tool("side_b", SIDE_B, again=(0, 20, 21, 22, 23))],
    "falco": [Tool("up_b", UP_B, steer="angle", lock=43, angles=SWEEP),
              Tool("side_b", SIDE_B, again=(0, 16, 17, 18, 19))],
    # Dolphin Slash; the side special's first swing once: it slows the fall
    "marth": [Tool("up_b", UP_B, drift=(IN, HALF)),
              Tool("side_b", SIDE_B, hold_for=24, helpless=False)],
    # Vanish: the direction held before she disappears
    "sheik": [Tool("up_b", UP_B, steer="angle", lock=36,
                   angles=(-45, 0, 45, 90, 20, 70))],
    # Falcon Dive; the down special in the air gives the jump back
    "captain-falcon": [Tool("up_b", UP_B, drift=(IN, HALF)),
                       Tool("down_b", DOWN_B, helpless=False)],
    # the parasol; the float is a jump held (`FLOATS`)
    "peach": [Tool("up_b", UP_B),
              Tool("side_b", SIDE_B, helpless=False)],
    # Pound, the stick up after it: it rises, and nothing is lost
    "jigglypuff": [Tool("side_b", SIDE_B, drift=((0.3, 1.0), (1.0, 0.3)),
                        helpless=False)],
    # Belay; Squall Hammer, B mashed to rise
    "ice-climbers": [Tool("up_b", UP_B), Tool("side_b", SIDE_B, mash=44)],
    # Quick Attack: a direction before the first warp, another during it
    "pikachu": [Tool("up_b", UP_B, steer="angle", lock=15,
                     angles=(0, 45, 90, -45, 20, 70),
                     two=(6, (90, 45, 0, -45)))],
    # the double jump and the air dodge are all he has
    "yoshi": [],
    # Screw Attack; a bomb stalls her fall
    "samus": [Tool("up_b", UP_B),
              Tool("down_b", DOWN_B, hold_for=30, helpless=False)],
}
# jumps in the air (1 unless named)
JUMPS = {"jigglypuff": 5, "kirby": 5}
# a character's own states are numbered from 341, its specials among them;
# Jigglypuff's and Kirby's extra jumps come first there
OWN_FIRST = {"jigglypuff": 346, "kirby": 351}
# Peach floats: the jump button held in the air, the stick toward the stage
FLOATS = ("peach",)


def tools_of(char):
    return list(TOOLS.get(char, [Tool("up_b", UP_B)])) + [AIRDODGE]


def air_jumps(char):
    """The jumps `char` has in the air."""
    return JUMPS.get(char, 1)


# ---- where the fighter is -------------------------------------------------------

class View:
    """The recovering fighter, as a decision sees it: `side` of the stage
    it is off (1 right, -1 left), `inward` the stick's x toward the stage,
    the ledge on its side, how far out and how high it is from it, the
    jumps it has left, the frames until it can act (`wait`: hitstun)."""

    def __init__(self, me, them, both, char):
        self.me, self.them, self.char = me, them, char
        left, right = both
        self.side = 1 if me["x"] >= 0 else -1
        self.inward = -self.side
        self.ledge = right if self.side > 0 else left
        self.out = (me["x"] - self.ledge[0]) * self.side    # past the ledge
        self.up = me["y"] - self.ledge[1]                   # above it
        self.jumps = max(0, air_jumps(char) + 1 - int(me["jumps"]))
        hs = int(me.get("hitstun") or 0)
        self.wait = max(0, hs - 1) if me["state"] in DAMAGE else 0
        self.state = me["state"]
        self.helpless = me["state"] in SPECIAL_FALL
        self.special = me["state"] >= OWN_FIRST.get(char, 341)


# ---- the routes a decision considers ---------------------------------------------

def _tool_steps(tool, how):
    """A tool's steps for one way of using it (`how`: angle, drift, again,
    second): its press, what is held through it."""
    out = []
    sx, sy = tool.press
    if tool.steer == "angle":
        ax, ay = angle_stick(how["angle"])
        if tool.button == R:
            # an air dodge: its direction is the stick's on its press
            out.append(press(R, ax, ay))
            out.append(hold(tool.hold_for, ax, ay))
            return out
        out.append(press(B, sx, sy))
        if tool.two and how.get("second") is not None:
            first, _ = tool.two
            out.append(hold(tool.lock + first, ax, ay))
            bx, by = angle_stick(how["second"])
            out.append(hold(tool.lock + 14, bx, by))
        else:
            out.append(hold(tool.lock + 6, ax, ay))
        return out
    dx, dy = how.get("drift", IN)
    out.append(press(B, sx, sy))
    if tool.mash:
        out.append(mash(tool.mash, B, dx, dy))
        return out
    again = how.get("again", 0)
    if again:
        out.append(hold(again - 2, dx, dy))
        out.append(press(B, dx, dy))
    out.append(hold(tool.hold_for, dx, dy))
    return out


def _hows(tool, aimed=()):
    """The ways a tool may be used."""
    if tool.steer == "angle":
        out = [dict(angle=a) for a in list(aimed) + list(tool.angles)]
        if tool.two:
            _, seconds = tool.two
            out += [dict(angle=a, second=b) for a in tool.angles[:4]
                    for b in seconds if abs(a - b) >= 40]
        return out
    return [dict(drift=d, again=g) for d in tool.drift
            for g in (tool.again or (0,))]


def _how_words(how):
    if how is None:
        return ""
    out = []
    if "angle" in how:
        out.append("at %g" % how["angle"])
    if how.get("second") is not None:
        out.append("then %g" % how["second"])
    if how.get("again"):
        out.append("B again on %d" % how["again"])
    if how.get("drift") not in (None, IN):
        out.append("stick %g, %g" % how["drift"])
    return (" " + ", ".join(out)) if out else ""


class Candidate:
    """A route to try: `build(k, g)` its steps for a wait of `k` frames
    and a gap of `g` (jump to special), `k`, `g` its own; `label` for a
    person; `kind` what it is made of ("jump", "up_b", "jump+up_b");
    `commit(k, g)`: the frame from which nothing more can be changed (None:
    it keeps its options); `jump`: it uses the double jump."""
    __slots__ = ("build", "k", "g", "label", "kind", "tool", "how", "segs",
                 "res", "score", "commit", "jump", "exposed")

    def __init__(self, build, k, g, label, kind, tool=None, how=None,
                 commit=None, jump=False):
        self.build, self.k, self.g = build, k, g
        self.label, self.kind = label, kind
        self.tool, self.how = tool, how
        self.commit, self.jump = commit, jump
        self.segs = self.res = None
        self.score = 0.0
        self.exposed = 0.0

    def steps(self, k=None, g=None):
        return self.build(self.k if k is None else k,
                          self.g if g is None else g)

    def moved(self, k, g):
        """The same route at another timing."""
        c = Candidate(self.build, k, g, self.label, self.kind, self.tool,
                      self.how, self.commit, self.jump)
        c.label = "%s (%+d, %+d)" % (self.label, k - self.k,
                                     (g or 0) - (self.g or 0))
        return c


DRIFT_END = hold(400, 1.0, 0.0)
WAITS = (0, 4, 9, 15, 22, 30, 40, 52, 66, 82)
GAPS = (0, 3, 7, 12, 18, 25, 33, 42)


def _with_tool(v, tool, how, jump):
    """A candidate's builder: a wait `k`, the jump and a gap `g` if `jump`,
    the tool used `how`, the drift to the end."""
    wait = v.wait

    def build(k, g):
        steps = [hold(wait + k, 1.0, 0.0)]
        if jump:
            steps += [press(X, 1.0, 0.0), hold(g, 1.0, 0.0)]
        if how is not None:
            steps += _tool_steps(tool, how)
            steps.append(DRIFT_END)
        return steps

    def commit(k, g):
        if not tool.helpless:
            return None
        at = wait + k + ((1 + g) if jump else 0) + 1
        if tool.steer == "angle" and tool.button == B:
            at += tool.lock
        return at
    return build, commit


TOOL_NAMES = ("jump", "float", "up_b", "side_b", "down_b", "airdodge")


def candidates(v, rng, budget=48, tools=None):
    """The routes a decision plays ahead from where the fighter is (after
    its hitstun): about `budget` of them, the ones that act at once always
    among them. A steered special's candidate has no angle yet (`how`
    None): the decision aims it from where the fighter is when the angle
    is read. `tools`: the only ones its routes may use (`TOOL_NAMES`,
    comma separated: "jump": it comes back with its jump and its drift
    alone); None: all it has."""
    out = []
    wait = v.wait
    allowed = None if tools is None else set(tools.split(","))

    def ok(name):
        return allowed is None or name in allowed
    tools = [t for t in tools_of(v.char) if ok(t.name)]

    def plain(steps_of, k, label, kind, jump=False):
        out.append(Candidate(lambda k_, g_: [hold(wait + k_, 1.0, 0.0)] +
                             steps_of(), k, None, label, kind, jump=jump))

    if v.helpless:
        # nothing left but the drift (and a fast fall)
        for d, name in ((1.0, "in"), (0.5, "half in"), (0.0, "straight"),
                        (-1.0, "out")):
            plain(lambda d=d: [hold(400, d, 0.0)], 0, "drift " + name,
                  "drift")
        plain(lambda: [hold(6, 1.0, 0.0), press(0, 0.0, -1.0), DRIFT_END],
              0, "drift in, fast fall", "drift")
        return out
    if v.special:
        # in a special: the stick's direction is all there is to change
        # (Fire Fox's angle while it charges), and B (a shortened Illusion)
        for a in SWEEP:
            ax, ay = angle_stick(a)
            plain(lambda ax=ax, ay=ay: [hold(70, ax, ay), DRIFT_END], 0,
                  "stick at %g" % a, "steer")
        plain(lambda: [hold(400, 0.0, 0.0)], 0, "stick let go", "steer")
        for k in (1, 2, 3, 4) if allowed is None else ():
            plain(lambda: [press(B, 1.0, 0.0), DRIFT_END], k,
                  "B again in %d" % k, "steer")
        return out
    # the drifts alone (a launch that leaves it above the stage)
    for d, name in ((1.0, "in"), (0.5, "half in")):
        plain(lambda d=d: [hold(400, d, 0.0)], 0, "drift " + name, "drift")
    # jumps: now or later, then the drift
    if v.jumps > 0 and ok("jump"):
        for k in WAITS[:6]:
            plain(lambda: [press(X, 1.0, 0.0), DRIFT_END], k,
                  "jump after %d" % k, "jump", jump=True)
        if v.jumps > 1:
            # every jump it has, one after the other as each tops out
            for gap in (18, 26, 34):
                def steps_of(gap=gap, jumps=v.jumps):
                    steps = []
                    for _ in range(jumps):
                        steps += [press(X, 1.0, 0.0), hold(gap, 1.0, 0.0)]
                    return steps + [DRIFT_END]
                plain(steps_of, 0, "%d jumps, %d apart" % (v.jumps, gap),
                      "jumps", jump=True)
    # a float (Peach): the jump button held, the stick toward the stage
    if v.char in FLOATS and ok("float"):
        for k in (0, 8, 18):
            plain(lambda: [press(X, 0.0, -1.0), hold(150, 1.0, 0.0, X),
                           DRIFT_END], k, "float after %d" % k, "float")
    # each special: now or later; after a jump, sooner or later
    plans = []
    for tool in tools:
        for k in WAITS:
            plans.append((tool, k, None))
        if v.jumps > 0 and ok("jump"):
            for k in WAITS[:4]:
                for g in GAPS:
                    plans.append((tool, k, g))
    rng.shuffle(plans)
    # those that act at once first: they are never left out
    plans.sort(key=lambda p: (p[1] > 0, p[2] is not None and p[2] > 0))
    for tool, k, g in plans:
        jump = g is not None
        kind = ("jump+" if jump else "") + tool.name
        label = "jump after %d, %s %d later" % (k, tool.name, g) if jump \
            else "%s after %d" % (tool.name, k)
        if tool.steer == "angle":
            build, commit = _with_tool(v, tool, None, jump)
            out.append(Candidate(build, k, g, label, kind, tool, None,
                                 commit, jump))
            continue
        for how in _hows(tool):
            build, commit = _with_tool(v, tool, how, jump)
            out.append(Candidate(build, k, g, label + _how_words(how), kind,
                                 tool, how, commit, jump))
    return out


# ---- what the player could do -----------------------------------------------------

AERIALS = (("nair", (A, 0, 0, 0, 0)), ("fair", (0, 0, 0, 1, 0)),
           ("bair", (0, 0, 0, -1, 0)), ("uair", (0, 0, 0, 0, 1)),
           ("dair", (0, 0, 0, 0, -1)), ("down_b", (B, 0, -1, 0, 0)))
GROUND = (("dsmash", (0, 0, 0, 0, -1)), ("fsmash", (0, 0, 0, 1, 0)),
          ("usmash", (0, 0, 0, 0, 1)), ("down_b", (B, 0, -1, 0, 0)))
THREAT_FRAMES = 44
REACH = 9.0               # a body's half width, about


class Team:
    """Games to play routes ahead in, side by side: `workers` forked copies
    of `n` (itself the match, or already a fork of it: fork.Fork), each
    answering in a thread of its own. `map(fn, items)`: fn(game, item) for
    each, in order. A decision plays some fifty routes of a hundred frames
    and more; one after the other they take a third of a second, too long
    for an opponent that reacts in a quarter. A game that cannot fork
    plays them one after the other in itself."""

    def __init__(self, n, workers):
        self.n = n
        self.games = []
        if workers > 1:
            from melee_engine.fork import Fork
            from native import NativeError
            try:
                for _ in range(workers):
                    self.games.append(Fork(n))
            except (NativeError, OSError, ValueError):
                self.close()

    def map(self, fn, items):
        import threading
        items = list(items)
        if len(self.games) < 2 or len(items) < 2:
            return [fn(self.n, x) for x in items]
        out = [None] * len(items)
        errors = []
        lock = threading.Lock()
        left = iter(range(len(items)))

        def run(game):
            while True:
                with lock:
                    i = next(left, None)
                if i is None:
                    return
                try:
                    out[i] = fn(game, items[i])
                except Exception as e:      # raised again below
                    errors.append(e)
                    return
        threads = [threading.Thread(target=run, args=(g,), daemon=True)
                   for g in self.games[:len(items)]]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        if errors:
            raise errors[0]
        return out

    def close(self):
        for g in self.games:
            g.close()
        self.games = []


def workers_for(n):
    """How many copies a decision plays its routes in: MELEE_RECOVER_WORKERS,
    else 6 (0 or 1: none, in the game itself)."""
    try:
        return int(os.environ.get("MELEE_RECOVER_WORKERS", "6"))
    except ValueError:
        return 6


def threats(team, target, their, k0):
    """Where the player (`target`) could strike in the next frames, from
    where they are: each attack they have now (in the air the aerials and
    the down special; on the ground the smashes and the down special)
    played ahead alone, begun now and a few frames on, and its hitboxes
    kept frame by frame. [(name, delay, {frame: [(x, y, r)]})], frames
    counted from now. `k0`: the player's pad is held this many frames first
    (as `their` has it). A lookahead each, in the team's games."""
    st = team.n.state()
    them = st["p"][target]
    if them is None:
        return [], 0.0
    s = them["state"]
    if s in LEDGE_ALL or s in DAMAGE or s <= DEAD_LAST:
        return [], 0.0
    facing = 1 if them["facing"] >= 0 else -1
    moves = AERIALS if (them["air"] or s == 24) else GROUND
    delays = (0, 5, 10, 16, 24) if them["air"] or s == 24 else (0, 8)
    held = tuple(their[0][1]) if their and their[0][0] > 1 else NONE
    asks = []
    for name, (b, lx, ly, cx, cy) in moves:
        for d in delays:
            raw = (b, 127 * lx, 127 * ly, 127 * cx * facing, 127 * cy, 0, 0)
            plan = []
            if d:
                plan.append((d, held if d <= k0 else NONE))
            plan += [(1, raw), (THREAT_FRAMES, NONE)]
            asks.append((name, d, "hitboxes %d %d %s" % (
                target, d + THREAT_FRAMES, _words(plan))))

    def ask(game, item):
        state = game.state()
        reply = game._cmd(item[2])
        game._state = state
        return reply

    out, ms = [], 0.0
    for (name, d, _), reply in zip(asks, team.map(ask, asks)):
        w = reply.split(" ", 2)
        ms += float(w[1])
        boxes = {}
        for row in (w[2].split(";") if len(w) > 2 and w[2] else ()):
            v = row.split()
            boxes[int(v[0])] = [
                (float(v[i]), float(v[i + 1]), float(v[i + 2]))
                for i in range(1, len(v) - 2, 3)]
        if boxes:
            out.append((name, d, boxes))
    return out, ms


def exposure(path, field, start=0):
    """How exposed a route is to what the player could do: the share of the
    player's attacks (`field`, from `threats`) one of whose hitboxes the
    route's body passes through at its frame. `path`: the route's (x, y)
    frame by frame, its frame 1 `start` frames from now."""
    if not field or not path:
        return 0.0, []
    hit = []
    for name, d, boxes in field:
        for f, bs in boxes.items():
            i = f - 1 - start
            if not 0 <= i < len(path):
                continue
            x, y = path[i]
            if any((x - bx) ** 2 + (y + 6.0 - by) ** 2 <=
                   (r + REACH) ** 2 for bx, by, r in bs):
                hit.append((name, d))
                break
    return len(hit) / float(len(field)), hit


# ---- what a route is worth --------------------------------------------------------

GOOD = ("ledge", "stage")


def exposed_cost(share):
    """What a route loses for the share of the player's attacks that would
    cover it (`exposure`): one in eight costs 17, a quarter 35, half 70 (a
    route kept is worth 12 more: a quarter of what they could do covering
    it, and it changes)."""
    return min(90.0, 140.0 * share)


def score(res, v, c=None, pre=0, goal=None):
    """A route's worth: the ledge or the stage reached and how safely,
    against being hit or lost. `res`: a native.Route; `c`: its candidate
    (how long it flies with nothing left to change, the jump kept);
    `goal`: "ledge" or "stage" if only that end counts."""
    lx, ly = v.ledge
    if res.end == "lost":
        # (the nearer the ledge it came, the less bad: for the refinement)
        return -300.0 + max(0.0, 40.0 - res.ledge * 0.5)
    if res.end == "hit":
        return -120.0 - res.taken + min(30.0, res.frame * 0.1)
    if res.end == "air":
        over = (lx - res.x) * v.side > 0 and res.y > ly
        return -40.0 if over else -200.0
    if goal is not None and res.end != goal:
        # it only goes there: any other end is as bad as none (it tries
        # for its goal to the last, and falls)
        return -340.0
    s = 100.0
    # the player's hitboxes came close: a route they nearly covered
    if res.gap < 12.0:
        s -= (12.0 - max(res.gap, 0.0)) * 2.0
    if c is not None:
        # flown with nothing left to change: seen coming, covered
        at = c.commit(c.k, c.g) if c.commit is not None else None
        if at is not None:
            tail = res.frame - pre - at
            s -= min(40.0, 0.35 * max(0, tail - 25))
        if not c.jump and v.jumps > 0:
            s += 4.0          # the jump kept
        s -= exposed_cost(c.exposed)
    if res.end == "ledge":
        return s + 6.0
    # on the stage: its landing's lag beside the player is a punish
    lag = max(0, (res.free or res.frame) - res.land) if res.land else 0
    d = abs(res.x - res.tx)
    close = max(0.0, min(1.0, (70.0 - d) / 45.0))
    return s - max(0, lag - 3) * 2.2 * close


def kind_of(c, res, v):
    """A route's kind, for variety: what it used and where it ended (the
    ledge, the stage from low or from high)."""
    high = res.top - v.ledge[1] > 45.0 and res.end == "stage"
    return "%s>%s%s" % (c.kind, res.end, " high" if high else "")


# ---- the decision ---------------------------------------------------------------

def expect(pad, k=3):
    """What the player is taken to do: their pad `k` frames more, then let
    go (what they began plays out: an attack, a jump's arc; a ledge held
    stays held)."""
    pad = tuple(pad)
    return [(k, pad), (1, NONE)] if k > 0 and pad != NONE else [(1, NONE)]


ANGLES = 8                # the angles a steered special is tried at


def decide(n, port, target, pre, their, rng, char=None, budget=48,
           temperature=8.0, recent=(), current=None, horizon=420,
           margin=30.0, keep=12.0, goal=None, predict=True, workers=None,
           tools=None):
    """The route to take from the frame `len(pre)` frames on (`pre`: the
    pads until then). `their`: the player's pads from now ([(frames, raw)]).
    `current`: the pads of the route now flown, from that frame on (kept
    unless another is worth `keep` more). `goal`: "ledge" or "stage": only
    routes that end there count. `tools`: the only tools its routes may
    use (`candidates`). `predict`: what the player could do counts against
    a route (`threats`). `workers`: the copies of the game
    the routes are played in, side by side (`Team`). Returns a dict: pads
    (raw pads from that frame), label, kind, end, score, ms (the frames
    played, summed), wall (how long it took), tried, good (routes that end
    well), exposed, and `routes`: every route tried (label, kind, end,
    score, frame, exposed), for a person to read."""
    st = n.state()
    me, them = st["p"][port], st["p"][target]
    if me is None or them is None:
        return None
    char = char or NAMES.get(me.get("ckind"))
    v = View(me, them, ledges(n), char)
    pre_segs = segments(pre)
    npre = len(pre)
    ms = 0.0
    import time
    t0 = time.time()
    team = Team(n, workers_for(n) if workers is None else workers)
    try:
        field = []
        if predict:
            field, tms = threats(team, target, their,
                                 their[0][0] if their else 0)
            ms += tms

        def play(game, item):
            segs, hor = item
            return route(game, port, target, pre_segs + segs, their,
                         npre + hor, path=bool(field))

        def weigh(cs):
            """Candidates played, side by side: each one's route, its
            exposure, its worth."""
            nonlocal ms
            for c in cs:
                c.segs = compile_steps(c.steps(), v.inward)
            for c, r in zip(cs, team.map(play, [(c.segs, horizon)
                                                for c in cs])):
                c.res = r
                ms += r.ms
                if field and r.end in GOOD:
                    c.exposed, _ = exposure(r.path, field)
                c.score = score(r, v, c, npre, goal)
            return cs

        # (the hitstun still left after the pre-roll: the candidates wait
        # it out)
        v.wait = max(0, v.wait - npre)
        # as many as the budget pays for: a route one, a steered special
        # its probe and its angles
        cands, spent = [], 0
        for c in candidates(v, rng, budget, tools):
            if spent >= budget:
                break
            steered = c.tool is not None and c.tool.steer == "angle" and \
                c.how is None
            spent += ANGLES + 1 if steered else 1
            cands.append(c)
        plain = [c for c in cands if c.how is not None or c.tool is None or
                 c.tool.steer != "angle"]
        steered = [c for c in cands if c not in plain]
        # where each steered special's fighter is when its angle is read
        probes = [c for c in steered if c.tool.button != R and
                  c.tool.lock > 0]
        segs = [compile_steps(c.steps() + [press(B, *c.tool.press),
                                           hold(c.tool.lock, 0.0, 1.0)],
                              v.inward) for c in probes]
        at = dict(zip(map(id, probes), team.map(play, [
            (s, sum(f for f, _ in s)) for s in segs])))
        for c in steered:
            # from there the angles: at the ledge (its catch, a little
            # under and over it), and the sweep
            r = at.get(id(c))
            aimed = []
            if r is not None:
                ms += r.ms
                if r.end in ("hit", "lost"):
                    continue
                dx = (r.x - v.ledge[0]) * v.side
                for off in (-14.0, -7.0, 0.0, 8.0, 18.0, 40.0):
                    dy = v.ledge[1] + off - r.y
                    aimed.append(round(math.degrees(math.atan2(
                        dy, max(dx, 0.0) + 1e-3)), 1))
            hows = _hows(c.tool, aimed)
            rng.shuffle(hows)
            hows.sort(key=lambda h: h["angle"] not in aimed)
            for how in hows[:ANGLES]:
                build, commit = _with_tool(v, c.tool, how, c.jump)
                plain.append(Candidate(
                    build, c.k, c.g, c.label + _how_words(how), c.kind,
                    c.tool, how, commit, c.jump))
        done = weigh(plain)
        if not any(c.res.end in GOOD and c.score > 0 for c in done):
            # nothing reaches: the routes that came nearest the ledge,
            # some frames earlier and later
            near = sorted((c for c in done
                           if c.kind not in ("drift", "steer")),
                          key=lambda c: c.res.ledge)[:4]
            more = []
            for c in near:
                moves = [(c.k + d, c.g) for d in range(-8, 9) if d]
                if c.g is not None:
                    moves += [(c.k, c.g + d) for d in range(-6, 7) if d]
                more += [c.moved(k, g) for k, g in moves
                         if k >= 0 and (g is None or g >= 0)]
            done += weigh(more)
        # the route now flown, among them
        cur = None
        if current:
            cur = Candidate(None, 0, None, "as planned",
                            current.get("kind", "?"))
            cur.segs = segments(current["pads"])
            cur.res = play(n, (cur.segs, horizon))
            ms += cur.res.ms
            if field and cur.res.end in GOOD:
                cur.exposed, _ = exposure(cur.res.path, field)
            cur.score = score(cur.res, v, None, npre, goal) - \
                exposed_cost(cur.exposed) + keep
    finally:
        team.close()
    wall = (time.time() - t0) * 1000.0
    pool = done + ([cur] if cur is not None else [])
    if not pool:
        return dict(pads=None, ms=ms, wall=wall, tried=0, good=0, routes=[])
    best = max(c.score for c in pool)
    good = [c for c in pool if c.score >= best - margin and c.score > 0]
    routes = [(c.label, c.kind, c.res.end, round(c.score, 1), c.res.frame,
               round(c.exposed, 2)) for c in pool]

    def kind(c):
        return current.get("kind", "?") if c is cur else \
            kind_of(c, c.res, v)

    if cur is not None and cur.score >= best - 1e-6:
        choice = cur            # still the best there is: no change
    elif good:
        # one of the best by a softmax, a kind flown lately less often;
        # one weight for each kind, so that a kind with many timings is
        # not drawn that much more often
        kinds = {}
        for c in good:
            w = math.exp((c.score - best) / max(temperature, 1e-6)) / \
                (1.0 + 1.5 * list(recent).count(kind(c)))
            kinds.setdefault(kind(c), []).append((c, w))
        names = sorted(kinds)
        k = rng.choices(names, weights=[max(w for _, w in kinds[x])
                                        for x in names])[0]
        cs, ws = zip(*kinds[k])
        choice = rng.choices(cs, weights=ws)[0]
    else:
        choice = max(pool, key=lambda c: c.score)
    return dict(pads=frames(choice.segs), label=choice.label,
                kind=kind(choice), end=choice.res.end,
                score=choice.score - (keep if choice is cur else 0.0),
                frame=choice.res.frame, ms=ms, wall=wall, tried=len(pool),
                good=len(good), routes=routes, kept=choice is cur,
                gap=choice.res.gap, exposed=choice.exposed,
                threats=len(field))


def check(n, port, target, pads, their, char=None, horizon=420, goal=None):
    """What the route now flown (`pads` from now) comes to: dict(end,
    score, frame, ms)."""
    st = n.state()
    me, them = st["p"][port], st["p"][target]
    if me is None or them is None or not pads:
        return None
    char = char or NAMES.get(me.get("ckind"))
    v = View(me, them, ledges(n), char)
    r = route(n, port, target, segments(pads), their, horizon)
    return dict(end=r.end, score=score(r, v, None, 0, goal), frame=r.frame,
                ms=r.ms, gap=r.gap)


# ---- the player, as the opponent sees them ----------------------------------------

def commitment(p):
    """What the player has committed to, coarsely: a change of it is what
    the opponent sees only after its reaction time (moving about on the
    ground is not one: that it follows as it happens)."""
    s = p["state"]
    if s in LEDGE:
        return ("ledge", 0)
    if s in LEDGE_ALL:
        return ("ledge", s)
    if 44 <= s <= 69 or s in (212, 214):
        return ("attack", s)
    if 70 <= s <= 74:
        return ("landing", 0)
    if s >= 341:
        return ("special", s)
    if 178 <= s <= 182:
        return ("shield", 0)
    if 233 <= s <= 236:
        return ("dodge", s)
    if s in DAMAGE or s == TUMBLE:
        return ("hit", 0)
    if s == 24 or p["air"]:
        return ("air", 2 if s in (27, 28) else 1)
    return ("ground", 0)


# ---- flying it --------------------------------------------------------------------

class Pilot:
    """The recovering fighter's controller, one pad a frame (`pad(st,
    their)`), until it is back (`done`: on the ledge, standing on the
    stage, or lost; `ended` says which).

    It decides where its decisions are made (`think`: the game itself
    headless, forked copies of it while a person plays), each for a frame
    `lead` frames on, the pads until then as the decision's pre-roll: a
    route when it has none (`decide`), the route checked again every
    `every` frames (`check`), another decided when the check says it no
    longer ends well, and when the player has committed to something new
    `react` frames ago. `goal`: "ledge" or "stage": it only goes there (an
    example's opponent, that does the one thing the example answers);
    `tools`: the only ones its routes use ("jump": its jump and drift).
    `adapt` False: it flies the route it first chose, whatever the player
    does. `predict` False: only what the player is doing counts, not what
    they could do. `log`: what it decided, [(frame, words)]; `decisions`:
    each one's record, for a test."""

    DROP = 25.0               # a route worth this much less is decided again
    RETRY = 8                 # frames between looks while nothing is good

    def __init__(self, think, port, target, rng=None, react=15, half=85.0,
                 memory=None, every=4, budget=48, temperature=8.0,
                 char=None, goal=None, adapt=True, predict=True, tools=None):
        self.think, self.port, self.target = think, port, target
        self.rng = rng or random.Random(0)
        self.react, self.half = react, half
        self.memory = memory if memory is not None else {}
        self.memory.setdefault("recent", [])
        self.every, self.budget, self.temperature = every, budget, \
            temperature
        self.char, self.goal, self.tools = char, goal, tools
        self.adapt, self.predict = adapt, predict
        self.frame = -1
        self.plan = []            # raw pads from frame `plan_at` on
        self.plan_at = 0
        self.info = None          # the decision the plan is (kind, score...)
        self.pending = None       # dict(tag, kind, asked, at, pre)
        self.need = True          # a route is wanted
        self.checked = -999
        self.retry_at = 0
        self.cls = None           # the player's commitment, as last seen
        self.unseen = None        # the frame of the oldest one not seen yet
        self.percent = None
        self.done = False
        self.ended = None
        self.tag = 0
        self.log = []
        self.decisions = []
        self.played = []
        self.late = 0
        self.ms = 0.0             # frames played ahead, in ms, summed
        self.wall = 0.0           # how long its decisions took
        self.last = NONE
        self._idle = NONE

    # -- asking ----------------------------------------------------------------

    def _their(self, their):
        return expect(their if their is not None else NONE, 3)

    def _ask(self, kind, fn, lead, pre):
        self.tag += 1
        tag = ("recover", id(self), self.tag)
        self.pending = dict(tag=tag, kind=kind, asked=self.frame,
                            at=self.frame + lead, pre=list(pre))
        self.think.submit(tag, fn, kind)

    def _rest(self, lead=0):
        """The plan's pads from `lead` frames on."""
        i = self.frame - self.plan_at + lead
        return list(self.plan[max(i, 0):])

    def _pre(self, lead):
        i = max(self.frame - self.plan_at, 0)
        out = list(self.plan[i:i + lead])
        return out + [self._idle] * (lead - len(out))

    def _decide(self, their, lead):
        port, target, char = self.port, self.target, self.char
        rng = random.Random(self.rng.random())
        pre = self._pre(lead)
        rest = self._rest(lead)
        current = dict(pads=rest, kind=self.info.get("kind", "?")) \
            if rest and self.info else None
        seg = self._their(their)
        budget, temp = self.budget, self.temperature
        recent = list(self.memory["recent"][-6:])
        goal, predict, tools = self.goal, self.predict, self.tools

        def fn(n):
            return decide(n, port, target, pre, seg, rng, char=char,
                          budget=budget, temperature=temp, recent=recent,
                          current=current, goal=goal, predict=predict,
                          tools=tools)
        self._ask("recover", fn, lead, pre)

    def _check(self, their, lead):
        port, target, char, goal = self.port, self.target, self.char, \
            self.goal
        pads = self._rest(0)
        seg = self._their(their)

        def fn(n):
            return check(n, port, target, pads, seg, char=char, goal=goal)
        self._ask("recover-check", fn, lead, [])

    # -- what comes back -------------------------------------------------------

    def _collect(self):
        p = self.pending
        if p is None or not self.think.ready(p["tag"]):
            return
        got = self.think.result(p["tag"])
        self.pending = None
        if got is None:
            self.retry_at = self.frame + self.RETRY
            return
        self.ms += got.get("ms", 0.0)
        self.wall += got.get("wall", got.get("ms", 0.0))
        if p["kind"] == "recover-check":
            good = got["end"] in GOOD
            was = self.info["score"] if self.info else 0.0
            if (not good and (self.info or {}).get("end") in GOOD) or \
                    got["score"] < was - self.DROP:
                self.need = True
                self.log.append((self.frame, "check: %s %.0f (was %.0f)" % (
                    got["end"], got["score"], was)))
            return
        if self.frame > p["at"]:
            self.late += 1
            self.need = True
            return
        # (the pads until its frame were its pre-roll: those played since
        # it was asked must be the ones it was made with)
        played = self.played[p["asked"]:self.frame]
        if list(played) != list(p["pre"][:len(played)]):
            self.need = True
            return
        if not got.get("pads"):
            self.need = True
            self.retry_at = self.frame + self.RETRY
            return
        # (MELEE_RECOVER_ROUTES: every route each decision tried, kept)
        drop = ("pads",) if os.environ.get("MELEE_RECOVER_ROUTES") else \
            ("pads", "routes")
        self.decisions.append(dict(
            {k: v for k, v in got.items() if k not in drop},
            asked=p["asked"], at=p["at"]))
        if got.get("kept"):
            self.info["score"] = got["score"]
            self.info["end"] = got["end"]
            if got["end"] in GOOD:
                self.log.append((self.frame, "kept: %s -> %s" % (
                    self.info.get("label"), got["end"])))
        else:
            self.plan = list(p["pre"]) + list(got["pads"])
            self.plan_at = p["asked"]
            self.info = dict(kind=got["kind"], score=got["score"],
                             end=got["end"], label=got["label"])
            self.log.append((self.frame, "%s -> %s %.0f (%d of %d good%s)"
                             % (got["label"], got["end"], got["score"],
                                got["good"], got["tried"],
                                ", exposed %.2f" % got["exposed"]
                                if got.get("exposed") else "")))
        self.need = got["end"] not in GOOD
        if self.need:
            self.retry_at = self.frame + self.RETRY
        self.checked = self.frame

    # -- each frame ------------------------------------------------------------

    def _state(self, me):
        """Where the recovery stands: None while it goes on."""
        s = me["state"]
        if s <= DEAD_LAST or s in REBIRTH:
            return "lost"
        if s in LEDGE:
            return "ledge"
        if not me["air"] and s in STANDING:
            return "stage"
        return None

    def pad(self, st, their=None):
        """This frame's raw pad (call once a frame, before it is played).
        `their`: the player's raw pad this frame."""
        me, them = st["p"][self.port], st["p"][self.target]
        self.frame += 1
        if me is None or them is None or self.done:
            self.played.append(NONE)
            return NONE
        inward = -1 if me["x"] >= 0 else 1
        self._idle = NONE if me["state"] in DAMAGE else \
            (0, 127 * inward, 0, 0, 0, 0, 0)
        end = self._state(me)
        if end is not None:
            self.done, self.ended = True, end
            if self.info and end != "lost":
                self.memory["recent"].append(self.info.get("kind", "?"))
                del self.memory["recent"][:-8]
            self.stop()
            self.played.append(NONE)
            return NONE
        # hit again: what was planned is over
        if self.percent is not None and me["percent"] > self.percent:
            self.plan, self.info, self.need = [], None, True
            self.retry_at = 0
            self.log.append((self.frame, "hit: %.0f%%" % me["percent"]))
        self.percent = me["percent"]
        # the player's commitment: seen `react` frames after it began
        cls = commitment(them)
        if cls != self.cls:
            if self.cls is not None and self.unseen is None and self.adapt:
                self.unseen = self.frame
            self.cls = cls
        self._collect()
        if self.pending is None:
            have = bool(self._rest(0))
            lead = self.think.lead_for("recover")
            due = self.unseen is not None and \
                self.frame >= self.unseen + self.react - lead
            blind = self.unseen is not None and not due
            if not have or (have and due) or (
                    self.need and not blind and self.adapt and
                    self.frame >= self.retry_at):
                if not blind:
                    self.unseen = None        # seen, as of this decision
                self._decide(their, lead)
                self._collect()
            elif self.adapt and not blind and \
                    self.frame - self.checked >= self.every:
                self.checked = self.frame
                self._check(their, self.think.lead_for("recover-check"))
                self._collect()
        i = self.frame - self.plan_at
        raw = self.plan[i] if 0 <= i < len(self.plan) else self._idle
        raw = tuple(raw)
        self.played.append(raw)
        self.last = raw
        return raw

    def ahead(self, k):
        """What it will press over the next `k` frames."""
        out = self._rest(0)[:k]
        return out + [self.last] * (k - len(out))

    def stop(self):
        if self.pending is not None:
            self.think.forget(self.pending["tag"])
            self.pending = None
