"""Recovering: the opponent knocked off the stage gets back onto it, by any
means its character has, against what the player is doing about it
(docs/ai/melee-engine.md, "Recovering"; opponent-vocabulary.md, `recover`).

The owner, 2026-11-17: an edgeguard drill is "a big test of the engine
performance because it should be able to predict and adapt to the players
edgeguard. For example for fox, if it is firefox angling, and right before
the angle is locked in the player starts to drop and go for a bair to
cover the ledge, the CPU could change angle to go high. This should have
options for reaction time of the engine so the player can essentially
choose their own difficulty." And after playing the first version, which
stopped at the ledge: "the CPU should still attempt to recover after a
ledge grab or aerial that knocks them down. They should try to make it
back to the stage by any means necessary, this needs to be a cat and mouse
drill where the player has to adapt to a CPU whos instructions are to get
back to the stage (with mixups and options like shine stalling, pound,
late up B, side b stalling for marth, etc). We want realism here and a
reactive CPU".

Its one instruction: stand on the stage again, free to act. Until then it
never stops: off the stage it flies a way back; on the ledge it gets up,
rolls, attacks, jumps, or drops and comes back on (a jump, an air dodge
onto the stage, its special, the ledge again); knocked down on the stage
it gets up or rolls; hit, it starts again from where the hit left it.

How it thinks. A route is the controller, frame by frame, from now until
the fighter hangs from the ledge or stands on the stage. The game itself
says what a route comes to: it is played ahead and undone ("route",
src/host/ahead.c), against the player going on with what they are doing
(their pad a few frames more, then let go: an attack begun plays out, a
ledge held stays held), and ends on the ledge, on the stage and free, hit,
or lost. Each time it decides, the opponent plays ahead the routes its
character has from where it is (`TOOLS`: its jumps, its specials at their
angles and timings, sooner or later; a stall first, the shine, Dancing
Blade, Pound, a bomb, the float, and then the rest), scores them (the
stage, the ledge; a landing's lag within the player's reach; how close
their hitboxes came; how long it flew with nothing left to change; the
ledge taken again and again), and takes one of the best by a softmax, the
kinds of route it used lately drawn less: never the same recovery twice.
Where nothing reaches, the routes that came nearest the ledge are played
again at every timing a few frames either side.

What the player could do (`threats`). A route that ends well against a
player who does nothing more may still pass through where they can
strike. So each decision also plays the player ahead, alone, through the
attacks they have from where they are (in the air: each aerial and the
down special, now and some frames on; on the ground: the smashes and the
down special), and keeps where their hitboxes were, frame by frame. A
route whose body is there at that frame, and can be hit, is exposed to
it; the more of them, the less the route is worth. A player who has
dropped below the ledge threatens the ledge and no longer the stage above:
the opponent goes high. One who jumped out early threatens now and not in
a second: it stalls, and comes later.

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
import time

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
DOWN = tuple(range(183, 199))     # lying down, its getups
LEDGE = (252, 253)                # CliffCatch, CliffWait
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
    (`path`: with its `path`, the fighter's (x, y, intangible) after each
    frame). Any game answers it: the match, or a fork of it."""
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
    shortened), a variant each. `held`: B kept held that many frames (the
    shine, held), a variant each. `mash`: B pressed every other frame for
    that many frames (the Ice Climbers' side special rises with it).
    `helpless`: nothing can follow it (the fighter falls helpless after:
    the frames flown after it count against a route). `stall`: it holds
    the fighter up or back and something follows it (the shine, Dancing
    Blade's first swing, Pound, a bomb): a route may begin with one.
    `jump_after`: the double jump is back after it (Captain Falcon's down
    special). `two`: (frames, angles): a second direction held from
    `frames` after the first is read (Pikachu's). `hold_for`: frames the
    stick is held after an unsteered press. `fade`: frames the stick may be
    held away from the stage first, a variant each (a special that drifts:
    Falcon Dive pulled back before it comes in, to arrive later)."""

    def __init__(self, name, press, steer=None, lock=0, angles=(),
                 drift=((1.0, 0.0),), button=B, again=(), held=(), mash=0,
                 helpless=True, stall=False, jump_after=False, hold_for=40,
                 two=None, fade=()):
        self.name, self.press, self.steer = name, press, steer
        self.lock, self.angles, self.drift = lock, tuple(angles), \
            tuple(drift)
        self.button, self.again, self.mash = button, tuple(again), mash
        self.held = tuple(held)
        self.helpless, self.stall = helpless and not stall, stall
        self.jump_after, self.hold_for, self.two = jump_after, hold_for, two
        self.fade = tuple(fade)


SWEEP = (-60, -40, -20, 0, 20, 40, 60, 75, 90)
UP_B = (0.0, 1.0)
SIDE_B = (1.0, 0.0)
DOWN_B = (0.0, -1.0)
IN, HALF, STILL = (1.0, 0.0), (0.4, 0.0), (0.0, 0.0)
AIRDODGE = Tool("airdodge", (0.0, 0.0), steer="angle", lock=0,
                angles=(0, 30, 60, 90, -30), button=R, hold_for=2)
# the shine in the air: it stops the fall for as long as B is held, and a
# jump comes out of it
SHINE = dict(drift=(STILL, IN), held=(0, 10, 22), stall=True, hold_for=4)

# The specials each character recovers with (data/characters/*.md,
# "Recovery"). What a route may be is `candidates` below; what it comes to,
# the game says.
TOOLS = {
    # Fire Fox, Fire Bird: 42 frames of charge, the angle read on the 43rd
    # (data/drills/fox-firefox-angles.json); Illusion, Phantasm: B again on
    # one of its travel frames shortens it (fox-shorten.json); the shine
    # stalls
    "fox": [Tool("up_b", UP_B, steer="angle", lock=43, angles=SWEEP),
            Tool("side_b", SIDE_B, again=(0, 20, 21, 22, 23)),
            Tool("down_b", DOWN_B, **SHINE)],
    "falco": [Tool("up_b", UP_B, steer="angle", lock=43, angles=SWEEP),
              Tool("side_b", SIDE_B, again=(0, 16, 17, 18, 19)),
              Tool("down_b", DOWN_B, **SHINE)],
    # Dolphin Slash; the side special's first swing: it slows the fall
    "marth": [Tool("up_b", UP_B, drift=(IN, HALF), fade=(8,)),
              Tool("side_b", SIDE_B, hold_for=24, stall=True)],
    # Vanish: the direction held before she disappears
    "sheik": [Tool("up_b", UP_B, steer="angle", lock=36,
                   angles=(-45, 0, 45, 90, 20, 70))],
    # Falcon Dive; the down special in the air gives the jump back
    "captain-falcon": [Tool("up_b", UP_B, drift=(IN, HALF),
                            fade=(10, 20, 30)),
                       Tool("down_b", DOWN_B, stall=True, jump_after=True,
                            hold_for=50)],
    # the parasol; Peach Bomber; the float is a jump held (`FLOATS`)
    "peach": [Tool("up_b", UP_B, fade=(12, 24, 40)),
              Tool("side_b", SIDE_B, stall=True, hold_for=50)],
    # Pound, the stick up after it: it rises, and nothing is lost
    "jigglypuff": [Tool("side_b", SIDE_B, drift=((0.3, 1.0), (1.0, 0.3)),
                        stall=True, hold_for=44)],
    # Belay; Squall Hammer, B mashed to rise
    "ice-climbers": [Tool("up_b", UP_B, fade=(10,)),
                     Tool("side_b", SIDE_B, mash=44)],
    # Quick Attack: a direction before the first warp, another during it
    "pikachu": [Tool("up_b", UP_B, steer="angle", lock=15,
                     angles=(0, 45, 90, -45, 20, 70),
                     two=(6, (90, 45, 0, -45)))],
    # the double jump and the air dodge are all he has
    "yoshi": [],
    # Screw Attack; a bomb stalls her fall
    "samus": [Tool("up_b", UP_B, fade=(8, 16)),
              Tool("down_b", DOWN_B, hold_for=50, stall=True)],
}
# jumps in the air (1 unless named)
JUMPS = {"jigglypuff": 5, "kirby": 5}
# a character's own states are numbered from 341, its specials among them;
# Jigglypuff's and Kirby's extra jumps come first there
OWN_FIRST = {"jigglypuff": 346, "kirby": 351}
# Peach floats: the jump button held in the air, the stick toward the stage
FLOATS = ("peach",)
FLOATING = 341            # ftPe_MS_Float
TOOL_NAMES = ("jump", "float", "up_b", "side_b", "down_b", "airdodge")


def tools_of(char):
    return list(TOOLS.get(char, [Tool("up_b", UP_B)])) + [AIRDODGE]


def air_jumps(char):
    """The jumps `char` has in the air."""
    return JUMPS.get(char, 1)


# ---- where the fighter is -------------------------------------------------------

def phase_of(me, char=None):
    """Where a recovery stands: "lost" (the stock gone), "stage" (standing
    on it, free: over), "ledge" (hanging), "down" (lying on the stage),
    "ground" (on it and not free yet: a landing's lag, a getup under way),
    "air"."""
    s = me["state"]
    if s <= DEAD_LAST or s in REBIRTH:
        return "lost"
    if s in LEDGE:
        return "ledge"
    if not me["air"]:
        if s in STANDING:
            return "stage"
        return "down" if s in DOWN else "ground"
    return "air"


class View:
    """The recovering fighter, as a decision sees it: `side` of the stage
    it is off (1 right, -1 left), `inward` the stick's x toward the stage,
    the ledge on its side, how far out and how high it is from it, the
    jumps it has left, the frames until it can act (`wait`: hitstun), its
    `phase`, the times it has caught the ledge on this recovery
    (`grabs`)."""

    def __init__(self, me, them, both, char, grabs=0):
        self.me, self.them, self.char = me, them, char
        left, right = both
        self.side = 1 if me["x"] >= 0 else -1
        self.inward = -self.side
        self.ledge = right if self.side > 0 else left
        self.half = abs(self.ledge[0])
        self.out = (me["x"] - self.ledge[0]) * self.side    # past the ledge
        self.up = me["y"] - self.ledge[1]                   # above it
        self.jumps = max(0, air_jumps(char) + 1 - int(me["jumps"]))
        hs = int(me.get("hitstun") or 0)
        self.wait = max(0, hs - 1) if me["state"] in DAMAGE else 0
        self.state = me["state"]
        self.phase = phase_of(me, char)
        self.helpless = me["state"] in SPECIAL_FALL
        self.special = me["air"] and \
            me["state"] >= OWN_FIRST.get(char, 341)
        self.tumbling = me["state"] in DAMAGE or me["state"] == TUMBLE
        self.grabs = grabs
        # the player and the ledge on its side: they hang from it (it is
        # theirs: caught only by hitting them off it); or they stand within
        # reach of it, free: they can take it, `hog_time` frames after they
        # see where it is going (their reaction, 15, and a wavedash back
        # off the edge, 23 from as far as 25 units in, more from further)
        near = them["x"] * self.side > 0
        inland = self.half - abs(them["x"])
        self.their_ledge = near and them["state"] in LEDGE_ALL
        self.hog_ready = near and not them["air"] and \
            them["state"] in STANDING and -2.0 <= inland <= 60.0
        self.hog_time = 38.0 + max(0.0, inland - 25.0) * 0.5


# ---- the routes a decision considers ---------------------------------------------

def _tool_steps(tool, how):
    """A tool's steps for one way of using it (`how`: angle, drift, again,
    held, second): its press, what is held through it."""
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
    if how.get("held"):
        out.append(hold(how["held"], dx, dy, B))
    again = how.get("again", 0)
    if again:
        out.append(hold(again - 2, dx, dy))
        out.append(press(B, dx, dy))
    back = how.get("back", 0)
    if back:
        # pulled back first: it comes in later, and from further out
        out.append(hold(back, -1.0, dy))
    out.append(hold(tool.hold_for - back, dx, dy))
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
    out = [dict(drift=d, again=g, held=h) for d in tool.drift
           for g in (tool.again or (0,)) for h in (tool.held or (0,))]
    return out + [dict(drift=tool.drift[0], back=b) for b in tool.fade]


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
    if how.get("held"):
        out.append("held %d" % how["held"])
    if how.get("back"):
        out.append("pulled back %d" % how["back"])
    if how.get("drift") not in (None, IN):
        out.append("stick %g, %g" % how["drift"])
    return (" " + ", ".join(out)) if out else ""


class Candidate:
    """A route to try: `build(k, g)` its steps for a wait of `k` frames
    and a gap of `g` (before its last tool), `k`, `g` its own; `label` for
    a person; `kind` what it is made of ("jump", "up_b", "jump+up_b",
    "down_b+up_b", "ledge getup"); `commit(k, g)`: the frame from which
    nothing more can be changed (None: it keeps its options); `jump`: it
    uses the double jump; `tool`, `how`: a steered special still to be
    aimed (`how` None); `way`: how it is flown, when not straight in
    ("fade": it hangs back or comes and pulls away; "late": back before it
    comes in at the end; "fast": a fast fall; "weave"): a kind of its own
    for variety; `end`: its last steps (`end_steps`)."""
    __slots__ = ("build", "k", "g", "label", "kind", "tool", "how", "segs",
                 "res", "score", "commit", "jump", "exposed", "lead", "way",
                 "end", "now")

    def __init__(self, build, k, g, label, kind, tool=None, how=None,
                 commit=None, jump=False, lead=None, way="", end=None,
                 now=False):
        self.now = now            # among the first played, whatever it is
        self.build, self.k, self.g = build, k, g
        self.label, self.kind = label, kind
        self.tool, self.how = tool, how
        self.commit, self.jump = commit, jump
        self.way, self.end = way, end
        self.lead = lead          # steps before the steered tool's press
        self.segs = self.res = None
        self.score = 0.0
        self.exposed = 0.0

    def steps(self, k=None, g=None):
        return self.build(self.k if k is None else k,
                          self.g if g is None else g)

    def moved(self, k, g):
        """The same route at another timing."""
        c = Candidate(self.build, k, g, self.label, self.kind, self.tool,
                      self.how, self.commit, self.jump, self.lead, self.way,
                      self.end)
        c.label = "%s (%+d, %+d)" % (self.label, k - self.k,
                                     (g or 0) - (self.g or 0))
        return c


DRIFT_END = hold(400, 1.0, 0.0)


# How a route is flown between its presses. A person does not hold the
# stick at the stage from the hit to the landing (the owner, 2026-11-17:
# "Peaches will bait attacks and then drift back to dodge, Captain Falcon
# will drift back in up B to mix up timings ... Humans are naturally
# tricky"): they hang back, come at the player and pull away, fall fast or
# slow. So a wait and a route's end are flown one of several ways, drawn for
# each route, and what comes of it the game says.
WAYS = ("in", "out", "fade", "still")
ENDS = (("back", 8), ("back", 16), ("back", 26), ("ff", 6), ("ff", 16),
        ("ff", 30), ("weave", 12), ("weave", 24))
WAY_TAG = {"out": "fade", "fade": "fade", "back": "late", "ff": "fast",
           "weave": "weave"}


def way_steps(k, way="in"):
    """`k` frames of drift: "in" (the stick toward the stage), "out" (away:
    it hangs back), "fade" (in, and away for the second half: it comes at
    them and pulls back), "still" (the stick let go)."""
    if k <= 0:
        return []
    if way == "out":
        return [hold(k, -1.0, 0.0)]
    if way == "still":
        return [hold(k, 0.0, 0.0)]
    if way == "fade" and k >= 6:
        return [hold(k - k // 2, 1.0, 0.0), hold(k // 2, -1.0, 0.0)]
    return [hold(k, 1.0, 0.0)]


def end_steps(end=None):
    """A route's last steps, to wherever it comes down: the drift toward
    the stage (None); ("back", d): away from it for `d` frames first (it
    arrives later, and from further out); ("ff", d): toward it, and a fast
    fall after `d` frames (it arrives sooner); ("weave", d): toward it for
    `d`, away for half of that, and in."""
    if end is None:
        return [DRIFT_END]
    kind, d = end
    if kind == "back":
        return [hold(d, -1.0, 0.0), DRIFT_END]
    if kind == "ff":
        return [hold(d, 1.0, 0.0), press(0, 0.0, -1.0), DRIFT_END]
    return [hold(d, 1.0, 0.0), hold(max(4, d // 2), -1.0, 0.0), DRIFT_END]


def way_words(way="in", gway="in", end=None):
    out = []
    if way == "out":
        out.append("hanging back")
    elif way == "fade":
        out.append("in and back out")
    elif way == "still":
        out.append("the stick let go")
    if gway == "out":
        out.append("back after the jump")
    elif gway == "fade":
        out.append("in and back after the jump")
    if end is not None:
        out.append({"back": "then back %d first",
                    "ff": "then a fast fall after %d",
                    "weave": "then in %d, back, in"}[end[0]] % end[1])
    return (", " + ", ".join(out)) if out else ""


def way_tag(way="in", gway="in", end=None):
    """A flown route's tag, for variety (kind_of): what marks it most."""
    if end is not None:
        return WAY_TAG[end[0]]
    return WAY_TAG.get(way) or WAY_TAG.get(gway) or ""


SHAPED = 8                # the shaped drifts, jumps and floats of a decision
STALLS = 6                # the stalls always among its routes
STALL_WEIGHT = 2.5        # a route that begins with one: drawn that much more
WAITS = (0, 4, 9, 15, 22, 30, 40, 52, 66, 82)
GAPS = (0, 3, 7, 12, 18, 25, 33, 42)
STALL_GAPS = (2, 8, 16, 26)


def _route_of(first, tool, how, jump, stall=None, stall_how=None,
              stall_jump=False, way="in", gway="in", end=None):
    """A candidate's builder: `first` (the steps before it: hitstun waited
    out, a ledge let go of), a wait `k` flown `way`; a stall and what is
    held through it, if any; the jump if `jump`, and a gap `g` flown
    `gway`; the tool used `how` (None: left to the decision, a steered
    special's angle); its `end` (`end_steps`: the drift to where it comes
    down)."""
    def before(k, g):
        steps = list(first) + way_steps(k, way)
        if stall is not None:
            steps += _tool_steps(stall, stall_how)
            if stall_jump:
                steps += [press(X, 1.0, 0.0)]
            steps += way_steps(g, gway)
        elif jump:
            steps += [press(X, 1.0, 0.0)] + way_steps(g, gway)
        return steps

    def build(k, g):
        steps = before(k, g)
        if tool is not None and how is not None:
            steps += _tool_steps(tool, how)
        if tool is None or how is not None:
            steps += end_steps(end)
        return steps

    def commit(k, g):
        if tool is None or not tool.helpless:
            return None
        at = sum(s[1] for s in before(k, g)) + 1
        if tool.steer == "angle" and tool.button == B:
            at += tool.lock
        return at
    return build, commit


def air_candidates(v, rng, tools=None, first=(), tag=""):
    """The routes from the air (after its hitstun): the drift; its jumps,
    now or later; each special now or later, after a jump or without; a
    stall, then a jump, a special or the drift. The ones that act at once
    come first: they are never left out. A steered special's candidate has
    no angle yet (`how` None): the decision aims it from where the fighter
    is when the angle is read. `tools`: the only ones its routes may use
    (`TOOL_NAMES`, comma separated); None: all it has. `first`: steps
    before every route (a ledge let go of), `tag` before every kind."""
    out = []
    first = list(first) + ([hold(v.wait, 1.0, 0.0)] if v.wait else [])
    allowed = None if tools is None else set(tools.split(","))

    def ok(name):
        return allowed is None or name in allowed
    have = [t for t in tools_of(v.char) if ok(t.name)]

    def plain(steps_of, k, label, kind, jump=False, way="", now=False):
        out.append(Candidate(
            lambda k_, g_: first + [hold(k_, 1.0, 0.0)] + steps_of(), k,
            None, label, tag + kind, jump=jump, way=way, now=now))

    if v.helpless:
        # nothing left but the drift (and a fast fall)
        for d, name in ((1.0, "in"), (0.5, "half in"), (0.0, "straight"),
                        (-1.0, "out")):
            plain(lambda d=d: [hold(400, d, 0.0)], 0, "drift " + name,
                  "drift")
        plain(lambda: [hold(6, 1.0, 0.0), press(0, 0.0, -1.0), DRIFT_END],
              0, "drift in, fast fall", "drift")
        return out
    if v.special and v.char in FLOATS and v.state == FLOATING:
        # floating: the jump button still held, and the stick. On toward
        # the stage; back first, and then in (what she drew out swings at
        # nothing, and she comes in after it); or let go, now or later
        for b in (0, 10, 20, 32):
            plain(lambda b=b: [hold(b, -1.0, 0.0, X),
                               hold(150, 1.0, 0.0, X), DRIFT_END], 0,
                  "floats on" + (", back %d first" % b if b else ""),
                  "float", way="fade" if b else "", now=True)
        for d in (0, 12, 30):
            plain(lambda d=d: [hold(d, 1.0, 0.0, X), DRIFT_END], 0,
                  "float let go" + (" after %d" % d if d else ""), "float",
                  way="fast")
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
        if v.jumps > 0 and ok("jump"):
            # (out of the shine, a jump)
            for k in (1, 6, 14):
                plain(lambda: [press(X, 1.0, 0.0), DRIFT_END], k,
                      "jump in %d" % k, "steer", jump=True)
        return out
    # the drifts alone (a launch that leaves it above the stage, or high
    # beside it)
    for d, name in ((1.0, "in"), (0.5, "half in")):
        plain(lambda d=d: [hold(400, d, 0.0)], 0, "drift " + name, "drift")
    # ... and flown some other way (WAYS, ENDS): `shaped`, of which a few
    # are drawn for each decision. Pulling back is always among them, and
    # among the first played unless it is far under the ledge: what dodges
    # an attack it sees coming
    # (an opponent held to some of its tools is an example's, or a first
    # part's: it comes straight in, the one thing its lesson answers)
    shaped = []
    if allowed is None:
        for d in (10, 22):
            plain(lambda d=d: end_steps(("back", d)), 0,
                  "drift, back %d first" % d, "drift", way="late",
                  now=v.up > -10)
    for end in ENDS:
        shaped.append((lambda end=end: end_steps(end), 0,
                       "drift" + way_words(end=end), "drift", False,
                       way_tag(end=end)))
    if v.tumbling and v.out < 0 and v.up < 60 and v.me.get("vy", 0) <= 0:
        # over the stage and coming down in its tumble: a tech as it lands
        # (in place, in, out), pressed within 20 frames of the floor
        for k in (0, 8, 16, 26):
            for sx, name in ((0.0, "in place"), (1.0, "in"), (-1.0, "out")):
                plain(lambda sx=sx: [press(R, sx, 0.0), hold(12, sx, 0.0),
                                     hold(60, 0.0, 0.0)], k,
                      "tech %s after %d" % (name, k), "tech")
    # jumps: now or later, then the drift
    if v.jumps > 0 and ok("jump"):
        for k in WAITS[:6]:
            plain(lambda: [press(X, 1.0, 0.0), DRIFT_END], k,
                  "jump after %d" % k, "jump", jump=True)
            for end in ENDS:
                shaped.append((
                    lambda end=end: [press(X, 1.0, 0.0)] + end_steps(end),
                    k, "jump after %d%s" % (k, way_words(end=end)), "jump",
                    True, way_tag(end=end)))
        for k in WAITS[2:6]:
            for way in ("out", "fade"):
                shaped.append((
                    lambda k=k, way=way: way_steps(k, way) +
                    [press(X, 1.0, 0.0), DRIFT_END], 0,
                    "jump after %d%s" % (k, way_words(way)), "jump", True,
                    way_tag(way)))
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
            # a float that comes at them and pulls back, or is let go early
            for d, b in ((20, 14), (40, 18), (64, 24)):
                shaped.append((
                    lambda d=d, b=b: [
                        press(X, 0.0, -1.0), hold(d, 1.0, 0.0, X),
                        hold(b, -1.0, 0.0, X),
                        hold(150 - d - b, 1.0, 0.0, X), DRIFT_END], k,
                    "float after %d: in %d, back %d, in" % (k, d, b),
                    "float", False, "fade"))
            for d in (25, 50, 80):
                shaped.append((
                    lambda d=d: [press(X, 0.0, -1.0), hold(d, 1.0, 0.0, X),
                                 DRIFT_END], k,
                    "float after %d, let go after %d" % (k, d), "float",
                    False, "fast"))
    rng.shuffle(shaped)
    for item in shaped[:SHAPED] if allowed is None else ():
        plain(*item)
    # each special: now or later; after a jump, sooner or later; after a
    # stall
    plans = []
    stalls = [t for t in have if t.stall]
    for tool in have:
        for k in WAITS:
            plans.append((tool, k, None, None))
        if v.jumps > 0 and ok("jump"):
            for k in WAITS[:4]:
                for g in GAPS:
                    plans.append((tool, k, g, None))
        for s in stalls:
            if s is tool:
                continue
            for k in WAITS[:5]:
                for g in STALL_GAPS:
                    plans.append((tool, k, g, s))
    for s in stalls:
        # a stall, then the jump (its own: the shine's, Falcon's back) or
        # the drift
        for k in WAITS[:5]:
            for g in STALL_GAPS:
                plans.append((None, k, g, s))
    # Those that act at once are always there (each special now, and a
    # jump and the special: what is needed when there is no time); the
    # rest are drawn evenly from all of it, later timings and stalls with
    # the others, as far as the decision's budget goes. (In their order by
    # time the ones that act at once took the whole budget, and nothing
    # was ever flown late.) An air dodge leaves it helpless: drawn a third
    # as often, and at once only where there is nothing else.
    only = len(have) == 1
    now = [p for p in plans if p[3] is None and p[1] == 0 and
           p[2] in (None, 0) and not p[0].stall and
           (p[0] is not AIRDODGE or only)]
    rest = [p for p in plans if p not in now and
            (p[0] is not AIRDODGE or only or rng.random() < 0.35)]
    rng.shuffle(rest)
    # (a stall is a mixup it should always have to hand: three of them
    # before the rest)
    some = [p for p in rest if p[3] is not None][:STALLS]
    rest = some + [p for p in rest if p not in some]

    def drawn(k, g):
        """How a drawn route is flown: straight in, mostly; one in three
        some other way (its wait, the gap after its jump, its end)."""
        way = gway = "in"
        end = None
        if allowed is not None:
            return way, gway, end
        if k >= 9 and rng.random() < 0.25:
            way = rng.choice(WAYS[1:])
        if g is not None and g >= 7 and rng.random() < 0.2:
            gway = rng.choice(("out", "fade"))
        if rng.random() < 0.25:
            end = rng.choice(ENDS)
        return way, gway, end

    for i, (tool, k, g, stall) in enumerate(now + rest):
        way, gway, end = ("in", "in", None) if i < len(now) else drawn(k, g)
        words, wtag = way_words(way, gway, end), way_tag(way, gway, end)
        if stall is not None:
            shows = _hows(stall)
            show = shows[rng.randrange(len(shows))]
            # (out of a stall the jump: its own, or the one it gives back)
            sj = (v.jumps > 0 or stall.jump_after) and ok("jump") and \
                (tool is None or rng.random() < 0.4)
            if tool is None and not sj:
                continue
            kind = stall.name + ("+jump" if sj else "") + \
                ("+" + tool.name if tool is not None else "")
            label = "%s%s after %d%s, %s %d later" % (
                stall.name, _how_words(show), k, ", a jump" if sj else "",
                tool.name if tool is not None else "the drift", g)
            hows = [None] if tool is None or tool.steer == "angle" \
                else _hows(tool)
            for how in hows:
                build, commit = _route_of(first, tool, how, sj, stall, show,
                                          sj, way, gway, end)
                out.append(Candidate(
                    build, k, g, label + _how_words(how) + words,
                    tag + kind, tool, how, commit, sj, way=wtag, end=end))
            continue
        jump = g is not None
        kind = ("jump+" if jump else "") + tool.name
        label = "jump after %d, %s %d later" % (k, tool.name, g) if jump \
            else "%s after %d" % (tool.name, k)
        if tool.steer == "angle":
            build, commit = _route_of(first, tool, None, jump, way=way,
                                      gway=gway, end=end)
            out.append(Candidate(build, k, g, label + words, tag + kind,
                                 tool, None, commit, jump, way=wtag,
                                 end=end))
            continue
        # (at once: every way of using it; drawn: one of them)
        hows = _hows(tool)
        for how in hows if k == 0 else [hows[rng.randrange(len(hows))]]:
            build, commit = _route_of(first, tool, how, jump, way=way,
                                      gway=gway, end=end)
            out.append(Candidate(
                build, k, g, label + _how_words(how) + words, tag + kind,
                tool, how, commit, jump,
                way=wtag or ("late" if how.get("back") else ""), end=end))
    # those that act at once lead (the drift, the jump, each special, a
    # jump and the special, straight in): a decision that must answer in
    # little time plays what it gets to, in this order
    out.sort(key=lambda c: not at_once(c))
    return out


LEDGE_WAITS = (0, 5, 11, 18, 27, 38)


def ledge_candidates(v, rng, tools=None):
    """The routes from the ledge, each after a wait: up onto the stage
    (the stick toward it), a roll (the shield), an attack (A), a jump; or
    let go (the stick down) and then what the air has: a jump back on, an
    air dodge onto the stage, a special, the ledge again."""
    out = []

    def direct(steps_of, k, label, kind):
        out.append(Candidate(lambda k_, g_: [hold(k_, 0.0, 0.0)] +
                             steps_of(), k, None, label, "ledge " + kind))
    for k in LEDGE_WAITS:
        direct(lambda: [press(0, 1.0, 0.0), hold(150, 0.0, 0.0)], k,
               "up onto the stage after %d" % k, "getup")
        direct(lambda: [press(R, 0.0, 0.0), hold(150, 0.0, 0.0)], k,
               "ledge roll after %d" % k, "roll")
        direct(lambda: [press(A, 0.0, 0.0), hold(150, 0.0, 0.0)], k,
               "ledge attack after %d" % k, "attack")
        direct(lambda: [press(X, 0.0, 0.0), hold(200, 1.0, 0.0)], k,
               "ledge jump after %d" % k, "jump")
    # let go, and back: as from the air just under the ledge, the jump
    # restored. An air dodge onto the stage right after the jump is the
    # ledgedash
    w = View(dict(v.me, state=29, air=1, jumps=1, hitstun=0), v.them,
             ((-v.half, v.ledge[1]), (v.half, v.ledge[1])), v.char, v.grabs)
    w.side, w.inward, w.ledge = v.side, v.inward, v.ledge
    for k in LEDGE_WAITS[:4]:
        first = [hold(k, 0.0, 0.0), press(0, 0.0, -1.0)]
        for g in (1, 2, 3, 5):
            for a in (-30, -12, 0):
                ax, ay = angle_stick(a)
                out.append(Candidate(
                    lambda k_, g_, first=first, ax=ax, ay=ay: first + [
                        hold(k_, 0.0, 0.0), press(X, 1.0, 0.0),
                        hold(g_, 1.0, 0.0), press(R, ax, ay),
                        hold(2, ax, ay), hold(120, 0.0, 0.0)],
                    0, g, "let go after %d, a jump, an air dodge at %g %d "
                    "later" % (k, a, g), "ledge drop+jump+airdodge",
                    jump=True))
        if k in LEDGE_WAITS[:2]:
            more = air_candidates(w, rng, tools, first=first,
                                  tag="ledge drop+")
            # (few of them: the ones that act soon)
            out += [c for c in more if c.k <= 9 and (c.g is None or
                                                     c.g <= 12)][:14]
    return out


def down_candidates(v, rng):
    """Lying on the stage: up, an attack, a roll in or out, each after a
    wait."""
    out = []
    for k in (0, 4, 10, 18, 30):
        for steps, name in (([press(0, 0.0, 1.0)], "up"),
                            ([press(A, 0.0, 0.0)], "attack"),
                            ([press(0, 1.0, 0.0)], "roll in"),
                            ([press(0, -1.0, 0.0)], "roll out")):
            out.append(Candidate(
                lambda k_, g_, steps=steps: [hold(k_, 0.0, 0.0)] + steps +
                [hold(120, 0.0, 0.0)], k, None,
                "getup %s after %d" % (name, k), "getup " + name))
    return out


def candidates(v, rng, tools=None):
    """The routes a decision plays ahead from where the fighter is."""
    if v.phase == "ledge":
        return ledge_candidates(v, rng, tools)
    if v.phase == "down":
        return down_candidates(v, rng)
    return air_candidates(v, rng, tools)


# ---- side by side -----------------------------------------------------------------

def copies(n, count):
    """`count` copies of the game `n` (fork.Fork), made by doubling: each
    copy made makes copies in its turn, side by side. (One after the
    other, seven of them were half the time a decision had while a person
    plays: a copy takes 3 ms to make alone and 15 beside a busy client.)
    Fewer than asked, or none, where the game will not fork."""
    import threading
    from melee_engine.fork import Fork
    from native import NativeError
    games = []
    try:
        # its rollback started first: each copy then keeps the mirror of
        # the game's memory it is forked with, where it made its own (70
        # MB copied page by page, 33 ms a copy: src/host/rollback.c)
        if count > 0:
            n._cmd("rb start")
    except NativeError:
        pass
    while len(games) < count:
        parents = ([n] + games)[:count - len(games)]
        new = [None] * len(parents)

        def make(i, parent):
            try:
                new[i] = Fork(parent)
            except (NativeError, OSError, ValueError):
                pass
        threads = [threading.Thread(target=make, args=(i, parent),
                                    daemon=True)
                   for i, parent in enumerate(parents)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        games += [g for g in new if g is not None]
        if any(g is None for g in new):
            break
    return games


class Team:
    """Games to play routes ahead in, side by side: `workers` forked copies
    of `n` (itself the match, or already a fork of it: fork.Fork), each
    answering in a thread of its own. `map(fn, items)`: fn(game, item) for
    each, in order. A decision plays some sixty routes of a hundred frames
    and more; one after the other they take a third of a second, too long
    for an opponent that reacts in a quarter. A game that cannot fork
    plays them one after the other in itself."""

    def __init__(self, n, workers, games=None):
        self.n = n
        self.faults = 0           # routes that raised (map)
        # (`games`: copies already made, the caller's: `copies`)
        self.games = list(games) if games is not None else \
            copies(n, workers) if workers > 1 else []
        if games is None and len(self.games) < 2:
            self.close()

    def map(self, fn, items, until=None):
        """fn(game, item) for each, in order, side by side. `until`: a
        time (time.time()) after which no more are begun: theirs are None
        (a decision that must answer by then: `decide`'s deadline). One
        that raises is None too and counted (`faults`: a route the game
        would not play is one route less, not the decision lost); if all
        of them raise, the first is raised."""
        import threading
        items = list(items)
        out = [None] * len(items)
        errors = []
        if len(self.games) < 2 or len(items) < 2:
            # (in a copy of its own if it has one: the game itself may be
            # another thread's at this moment)
            game = self.games[0] if self.games else self.n
            for i, x in enumerate(items):
                if until is not None and i and time.time() >= until:
                    break
                try:
                    out[i] = fn(game, x)
                except Exception as e:
                    errors.append(e)
        else:
            lock = threading.Lock()
            left = iter(range(len(items)))

            def run(game):
                while True:
                    if until is not None and time.time() >= until:
                        return
                    with lock:
                        i = next(left, None)
                    if i is None:
                        return
                    try:
                        out[i] = fn(game, items[i])
                    except Exception as e:
                        errors.append(e)
            threads = [threading.Thread(target=run, args=(g,), daemon=True)
                       for g in self.games[:len(items)]]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        self.faults += len(errors)
        if errors and all(x is None for x in out):
            raise errors[0]
        return out

    def close(self):
        for g in self.games:
            g.close()
        self.games = []


def workers_for(n):
    """How many copies a decision plays its routes in: MELEE_RECOVER_WORKERS,
    else 8 (0 or 1: none, in the game itself)."""
    try:
        return int(os.environ.get("MELEE_RECOVER_WORKERS", "8"))
    except ValueError:
        return 8


# ---- what the player could do -----------------------------------------------------

AERIALS = (("nair", (A, 0, 0, 0, 0)), ("fair", (0, 0, 0, 1, 0)),
           ("bair", (0, 0, 0, -1, 0)), ("uair", (0, 0, 0, 0, 1)),
           ("dair", (0, 0, 0, 0, -1)), ("down_b", (B, 0, -1, 0, 0)))
GROUND = (("dsmash", (0, 0, 0, 0, -1)), ("fsmash", (0, 0, 0, 1, 0)),
          ("usmash", (0, 0, 0, 0, 1)), ("down_b", (B, 0, -1, 0, 0)))
THREAT_FRAMES = 44
REACH = 9.0               # a body's half width, about


def threats(team, target, their, k0, st=None, until=None):
    """Where the player (`target`) could strike in the next frames, from
    where they are: each attack they have now (in the air the aerials and
    the down special; on the ground the smashes and the down special)
    played ahead alone, begun now and a few frames on, and its hitboxes
    kept frame by frame. [(name, delay, {frame: [(x, y, r)]})], frames
    counted from now. `k0`: the player's pad is held this many frames first
    (as `their` has it). A lookahead each, in the team's games. `st`: the
    game's state, where the caller has it (the game itself is not asked:
    a decision plays its routes in it meanwhile)."""
    if st is None:
        st = team.n.state()
    them = st["p"][target]
    if them is None:
        return [], 0.0
    s = them["state"]
    if s in LEDGE_ALL or s in DAMAGE or s <= DEAD_LAST:
        return [], 0.0
    facing = 1 if them["facing"] >= 0 else -1
    flying = bool(them["air"]) or s == 24
    moves = AERIALS if flying else GROUND
    # (on the ground they can wait and strike whenever it arrives: each
    # attack once, and where it reaches guarded from then on, `guard`)
    delays = (0, 5, 10, 16, 24) if flying else (0,)
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
    # (`until`: no attack is begun after it: those played by then count)
    for (name, d, _), reply in zip(asks, team.map(ask, asks, until)):
        if reply is None:
            continue
        w = reply.split(" ", 2)
        ms += float(w[1])
        boxes = {}
        for row in (w[2].split(";") if len(w) > 2 and w[2] else ()):
            v = row.split()
            boxes[int(v[0])] = [
                (float(v[i]), float(v[i + 1]), float(v[i + 2]))
                for i in range(1, len(v) - 2, 3)]
        if boxes:
            out.append((name, d, boxes, None if flying else guard(boxes)))
    return out, ms


def guard(boxes):
    """Where an attack reaches, whenever it is thrown: its hitboxes of
    every frame as a few circles ((x, y, r), one for each 3 units), the
    box around them, and its first frame out. A player standing there
    covers it for as long as they stand."""
    cells = {}
    for bs in boxes.values():
        for x, y, r in bs:
            key = (round(x / 3.0), round(y / 3.0))
            if key not in cells or cells[key][2] < r:
                cells[key] = (x, y, r)
    circles = list(cells.values())
    pad = REACH + max(c[2] for c in circles)
    box = (min(c[0] for c in circles) - pad, max(c[0] for c in circles) + pad,
           min(c[1] for c in circles) - pad, max(c[1] for c in circles) + pad)
    return circles, box, min(boxes)


def exposure(path, field, start=0):
    """How exposed a route is to what the player could do: the share of the
    player's attacks (`field`, from `threats`) one of whose hitboxes the
    route's body is in at its frame, where it can be hit (not intangible).
    `path`: the route's (x, y, intangible) frame by frame from now; its
    first `start` frames are not counted (hitstun, the pre-roll: no route
    can do otherwise there)."""
    if not field or not path:
        return 0.0, []
    hit = []
    for name, d, boxes, zone in field:
        if zone is not None:
            # a player on the ground: where the attack reaches, at any
            # frame from its first one out
            circles, (x0, x1, y0, y1), first = zone
            for i in range(max(start, first - 1), len(path)):
                x, y = path[i][0], path[i][1] + 6.0
                if x < x0 or x > x1 or y < y0 or y > y1 or \
                        (len(path[i]) > 2 and path[i][2]):
                    continue
                if any((x - bx) ** 2 + (y - by) ** 2 <= (r + REACH) ** 2
                       for bx, by, r in circles):
                    hit.append((name, d))
                    break
            continue
        for f, bs in boxes.items():
            i = f - 1
            # (not while it cannot act: every route flies those frames)
            if not start <= i < len(path):
                continue
            x, y = path[i][0], path[i][1]
            if len(path[i]) > 2 and path[i][2]:
                continue
            if any((x - bx) ** 2 + (y + 6.0 - by) ** 2 <=
                   (r + REACH) ** 2 for bx, by, r in bs):
                hit.append((name, d))
                break
    return len(hit) / float(len(field)), hit


# ---- what a route is worth --------------------------------------------------------

GOOD = ("ledge", "stage")
STAGE, HANG = 100.0, 80.0     # standing on the stage; hanging from the ledge
AGAIN = 30.0                  # less for each time the ledge was caught before
THEIRS = 40.0                 # less for a ledge the player hangs from
HOG = 30.0                    # less for a ledge they have time to take
FAILED = 25.0                 # less for each time such a route failed lately


def route_key(kind):
    """What a route came down to, for what is remembered of it: its last
    tool and its end ("jump+side_b>ledge" and "side_b>ledge" are both
    "side_b>ledge"; "ledge drop+jump+airdodge>stage" is "ledge
    airdodge>stage")."""
    base, _, end = (kind or "?").partition(">")
    end = end.split(" ")[0]
    ledge = base.startswith("ledge ")
    last = base.split("+")[-1]
    if ledge and "+" in base:
        last = "ledge " + last
    return "%s>%s" % (last, end)


def exposed_cost(share):
    """What a route loses for the share of the player's attacks that would
    cover it (`exposure`): one in eight costs 17, a quarter 35, half 70 (a
    route kept is worth 12 more: a quarter of what they could do covering
    it, and it changes)."""
    return min(90.0, 140.0 * share)


def score(res, v, c=None, pre=0, goal=None):
    """A route's worth. The stage, standing and free, is what it is for;
    the ledge is on the way there (less each time it is caught again: it
    does not hang there for ever); hit is bad, lost worst. `res`: a
    native.Route; `c`: its candidate (how long it flies with nothing left
    to change, the jump kept, how exposed); `goal`: "ledge" or "stage" if
    only that end counts."""
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
    s = STAGE if res.end == "stage" else \
        max(20.0, HANG - AGAIN * v.grabs)
    # the player's hitboxes came close: a route they nearly covered
    if res.gap < 12.0:
        s -= (12.0 - max(res.gap, 0.0)) * 2.0
    if c is not None:
        # flown with nothing left to change: seen coming, covered
        at = c.commit(c.k, c.g) if c.commit is not None else None
        if at is not None:
            tail = res.frame - pre - at
            s -= min(40.0, 0.35 * max(0, tail - 25))
        if not c.jump and v.jumps > 0 and v.phase == "air":
            s += 4.0          # the jump kept
        s -= exposed_cost(c.exposed)
    if res.end == "ledge":
        if v.their_ledge:
            # the ledge is the player's: it was caught by hitting them off
            # it, and they have every ledge option before that
            s -= THEIRS
        elif v.hog_ready and c is not None and c.commit is not None and \
                c.tool is not None:
            # they stand where they can take it: a special to the ledge
            # that they can see start, and still be on the ledge before it
            # arrives, is theirs to take (Fire Fox's charge; not a quick
            # Illusion)
            at = c.commit(c.k, c.g)
            if at is not None:
                seen = at - (c.tool.lock if c.tool.steer == "angle" and
                             c.tool.button == B else 0)
                if res.frame - pre - seen >= v.hog_time:
                    s -= HOG
        return s
    # on the stage: its lag within the player's reach is a punish (they
    # run about 1.6 units a frame, and reach 15)
    lag = max(0, (res.free or res.frame) - res.land) if res.land else 0
    reach = 15.0 + 1.6 * max(0, lag - 3)
    d = abs(res.x - res.tx) + abs(res.ty - v.ledge[1]) * 0.5
    close = max(0.0, min(1.0, (reach - d) / 20.0 + 0.5)) if lag > 3 else 0.0
    return s - 70.0 * close


def family(kind):
    """A route's kind without the way it is flown ("jump>stage high fade":
    "jump>stage high")."""
    head, _, tail = kind.rpartition(" ")
    return head if head and tail in WAY_TAG.values() else kind


def kind_of(c, res, v):
    """A route's kind, for variety: what it used and where it ended (the
    ledge, the stage from low or from high)."""
    high = res.top - v.ledge[1] > 45.0 and res.end == "stage"
    way = getattr(c, "way", "")
    return "%s>%s%s%s" % (c.kind, res.end, " high" if high else "",
                          " " + way if way else "")


# ---- the decision ---------------------------------------------------------------

def expect(pad, k=3):
    """What the player is taken to do: their pad `k` frames more, then let
    go (what they began plays out: an attack, a jump's arc; a ledge held
    stays held)."""
    pad = tuple(pad)
    return [(k, pad), (1, NONE)] if k > 0 and pad != NONE else [(1, NONE)]


ANGLES = 6                # the angles a steered special is tried at


IDLE_KINDS = ("drift", "steer", "tech")
HIGH = 25.0               # above the ledge by this much it has time


def at_once(c):
    """Whether a candidate acts at once, straight in."""
    # (not a stall on its own: the shine and then the drift is no way back)
    return c.now or (c.k == 0 and c.g in (None, 0) and not c.way and
                     not c.kind.endswith("tech") and
                     not (c.tool is not None and c.tool.stall))


def tries(c):
    """Whether a candidate does something for its recovery (a jump, a
    special, a float, a getup), not only drifts."""
    return c.kind.split(" ")[-1].split("+")[-1] not in IDLE_KINDS


def decide(n, port, target, pre, their, rng, char=None, budget=64,
           temperature=8.0, recent=(), current=None, horizon=420,
           margin=30.0, keep=12.0, goal=None, predict=True, workers=None,
           tools=None, grabs=0, outcomes=(), deadline=None):
    """The route to take from the frame `len(pre)` frames on (`pre`: the
    pads until then). `their`: the player's pads from now ([(frames, raw)]).
    `current`: the pads of the route now flown, from that frame on (kept
    unless another is worth `keep` more; "waiting": it is one that waits
    for a ledge the player holds). `goal`: "ledge" or "stage": only
    routes that end there count. `tools`: the only tools its routes may
    use (`air_candidates`). `predict`: what the player could do counts
    against a route (`threats`). `workers`: the copies of the game the
    routes are played in, side by side (`Team`). `grabs`: the times it has
    caught the ledge on this recovery. `outcomes`: what its last routes
    came to ([(route_key, "ok" | "hit" | "lost")], kept from one attempt to
    the next): a kind of route that got it hit or killed lately is worth
    less, so what the player has found an answer to is flown less.

    `deadline`: seconds it may take (while a person plays: the frames
    until its frame, less what the answer's way back takes). The routes
    that act at once are played first, then the rest as far as the time
    goes, and it answers with the best of those played ("partial": some
    were not): late is worse than rough. None: all of them (headless).

    Where no route ends well it still goes for it: the best of those that
    do something (a jump, a special), never only a drift when there is one
    (until 2026-11-17 a drift that fell past nearest the ledge was "the
    best", and it fell without pressing a button).

    Returns a dict: pads (raw pads from that frame), label, kind, end,
    score, phase, ms (the frames played, summed), wall (how long it took),
    tried, good (routes that end well), exposed, partial, faults (routes
    the game would not play), and `routes`: every route tried (label,
    kind, end, score, frame, exposed), for a person to read."""
    import threading
    t0 = time.time()
    until = None if deadline is None else t0 + max(0.0, deadline)

    def over():
        return until is not None and time.time() >= until
    st = n.state()
    me, them = st["p"][port], st["p"][target]
    if me is None or them is None:
        return None
    char = char or NAMES.get(me.get("ckind"))
    v = View(me, them, ledges(n), char, grabs)
    pre_segs = segments(pre)
    npre = len(pre)
    ms = 0.0
    done, cur = [], None
    partial = False
    # (a copy for every 8 routes: a small decision, one made again with a
    # route in hand, does not pay for copies it has no routes for; a fork
    # of the window build takes 3 ms)
    count = min(workers_for(n), max(2, budget // 8)) \
        if workers is None else workers
    if until is not None:
        # (on the clock: each copy costs 3 ms, and several times that
        # beside a client that is busy)
        count = min(count, 5)
    # what the player could do, played beside the routes in copies of its
    # own (a quarter of a decision's time, one after the other)
    ts = them["state"]
    may = predict and not (ts in LEDGE_ALL or ts in DAMAGE or
                           ts <= DEAD_LAST)
    # (the routes' copies and the player's attacks', made together)
    beside = (2 if until is not None or not them["air"] else 3) \
        if may and count >= 2 else 0
    made = copies(n, count + beside) if count >= 2 else []
    if len(made) < count + beside:
        beside = 0                # (it will not fork that many: one team)
    team = Team(n, count, made[:len(made) - beside])
    side = Team(n, beside, made[len(made) - beside:]) if beside else None
    times = dict(copies=(time.time() - t0) * 1000.0)
    box = {}
    waiter = None
    k0 = their[0][0] if their else 0
    try:
        field = []
        if may and side is not None and len(side.games) >= 2:
            def think():
                try:
                    box["field"] = threats(side, target, their, k0, st,
                                           until)
                except Exception as e:      # raised below, in its turn
                    box["error"] = e
            waiter = threading.Thread(target=think, daemon=True)
            waiter.start()
        elif may:
            field, tms = threats(team, target, their, k0, st)
            ms += tms

        def play(game, item):
            segs, hor = item
            return route(game, port, target, pre_segs + segs, their,
                         npre + hor, path=may)

        def played(cs, stop=None):
            """Candidates played, side by side (those not begun by `stop`
            left out): each one's route."""
            nonlocal ms, partial
            for c in cs:
                c.segs = compile_steps(c.steps(), v.inward)
            out = []
            for c, r in zip(cs, team.map(play, [(c.segs, horizon)
                                                for c in cs], stop)):
                if r is None:
                    partial = True
                    continue
                c.res = r
                ms += r.ms
                out.append(c)
            return out

        def weigh(cs):
            """Each one's exposure and its worth."""
            for c in cs:
                if field and c.res.end in GOOD:
                    c.exposed, _ = exposure(c.res.path, field,
                                            npre + v.wait)
                c.score = score(c.res, v, c, npre, goal)
            return cs

        # (the hitstun still left after the pre-roll: the candidates wait
        # it out)
        v.wait = max(0, v.wait - npre)
        # as many as the budget pays for: a route one, a steered special
        # its probe and its angles
        cands, spent = [], 0
        for c in candidates(v, rng, tools):
            if spent >= budget:
                break
            aim = c.tool is not None and c.tool.steer == "angle" and \
                c.how is None
            spent += ANGLES + 1 if aim else 1
            cands.append(c)
        def steered(c):
            return c.tool is not None and c.tool.steer == "angle" and \
                c.how is None

        def aimed_at(c, r):
            """A steered special's candidates, one for each angle: at the
            ledge (its catch, a little under and over it) from where its
            probe `r` left the fighter when the angle is read, and the
            sweep."""
            nonlocal ms
            aimed = []
            if r is not None:
                ms += r.ms
                if r.end in ("hit", "lost"):
                    return []
                dx = (r.x - v.ledge[0]) * v.side
                for off in (-10.0, 0.0, 10.0, 28.0):
                    dy = v.ledge[1] + off - r.y
                    aimed.append(round(math.degrees(math.atan2(
                        dy, max(dx, 0.0) + 1e-3)), 1))
            hows = _hows(c.tool, aimed)
            rng.shuffle(hows)
            hows.sort(key=lambda h: h["angle"] not in aimed)
            out = []
            for how in hows[:ANGLES]:
                def build(k, g, lead=c, how=how):
                    return lead.build(k, g) + _tool_steps(lead.tool, how) + \
                        end_steps(lead.end)
                out.append(Candidate(
                    build, c.k, c.g, c.label + _how_words(how), c.kind,
                    c.tool, how, c.commit, c.jump, way=c.way, end=c.end))
            return out

        if until is not None:
            # on the clock not all of them are played: the ones that act
            # at once and the others in turn (two of the first to one of
            # the others when it is low and must act; one to two when it
            # is high and has time: from up there what acts at once is
            # seldom the way)
            now = [c for c in cands if at_once(c)]
            rest = [c for c in cands if not at_once(c)]
            if current:
                # (with a route in hand it is an answer to what the player
                # did: the pull back and the float kept lead, what dodges)
                now.sort(key=lambda c: not c.now)
            a, b = (1, 2) if v.phase == "air" and v.up > HIGH else (2, 1)
            if current:
                a, b = 2, 1
            cands = []
            while now or rest:
                cands += now[:a] + rest[:b]
                now, rest = now[a:], rest[b:]
        # A few candidates at a time on the clock (all at once without
        # one): where each steered special's fighter is when its angle is
        # read (a probe each, side by side), then their routes. (All the
        # probes first took a quarter of the time a decision had, and Fox
        # and Falco from high had four routes played.)
        size = len(cands) if until is None else max(4, len(team.games))
        for i in range(0, max(len(cands), 1), max(size, 1)):
            chunk = cands[i:i + size]
            if i and over():
                partial = True
                break
            probes = [c for c in chunk if steered(c) and
                      c.tool.button != R and c.tool.lock > 0]
            segs = [compile_steps(c.steps() + [press(B, *c.tool.press),
                                               hold(c.tool.lock, 0.0, 1.0)],
                                  v.inward) for c in probes]
            at = dict(zip(map(id, probes), team.map(play, [
                (s, sum(f for f, _ in s)) for s in segs],
                until if i else None)))
            ordered = []
            for c in chunk:
                ordered += aimed_at(c, at.get(id(c))) if steered(c) else [c]
            if not i:
                times["first"] = (time.time() - t0) * 1000.0
                # (the first of them whatever the time, one in each copy:
                # an answer with nothing in it is no answer)
                force = max(1, len(team.games))
                done += played(ordered[:force]) + \
                    played(ordered[force:], until)
            else:
                done += played(ordered, until)
        times["routes"] = (time.time() - t0) * 1000.0
        if waiter is not None:
            waiter.join()
            if "error" in box:
                raise box["error"]
            field, tms = box["field"]
            ms += tms
        times["threats"] = (time.time() - t0) * 1000.0
        weigh(done)
        if v.phase == "air" and not over() and \
                not any(c.res.end in GOOD and c.score > 0 for c in done):
            # nothing reaches: the routes that came nearest the ledge,
            # some frames earlier and later
            near = sorted((c for c in done if tries(c)),
                          key=lambda c: c.res.ledge)[:4]
            more = []
            for c in near:
                moves = [(c.k + d, c.g) for d in range(-8, 9) if d]
                if c.g is not None:
                    moves += [(c.k, c.g + d) for d in range(-6, 7) if d]
                more += [c.moved(k, g) for k, g in moves
                         if k >= 0 and (g is None or g >= 0)]
            # (nearest first: what the time allows)
            more.sort(key=lambda c: abs(c.k - near[0].k))
            done += weigh(played(more, until))
        # what failed lately is worth less
        fails = {}
        for key, what in list(outcomes)[-8:]:
            if what != "ok":
                fails[key] = fails.get(key, 0) + 1
        if fails:
            for c in done:
                if c.res.end in GOOD:
                    c.score -= FAILED * min(3, fails.get(route_key(
                        kind_of(c, c.res, v)), 0))
        # the route now flown, among them
        if current:
            cur = Candidate(None, 0, None, "as planned",
                            current.get("kind", "?"))
            cur.segs = segments(current["pads"])
            cur.res = play(n, (cur.segs, horizon))
            ms += cur.res.ms
            if field and cur.res.end in GOOD:
                cur.exposed, _ = exposure(cur.res.path, field,
                                          npre + v.wait)
            cur.score = score(cur.res, v, None, npre, goal) - \
                exposed_cost(cur.exposed) + keep
        waiting = None
        if v.their_ledge and v.phase == "air" and goal is None and \
                not any(c.res.end in GOOD and c.score > 0 for c in done):
            # the player hangs from the ledge and nothing else reaches:
            # they cannot hang there for ever. The routes that would reach
            # if they let go, and one of the later of those: it waits, and
            # decides again on the way. One it is already waiting on is
            # kept while it would still reach (until 2026-11-17 each
            # decision put it off again for a later one, until none
            # reached, and it fell without a try)
            free = [(1, (0, 0, -127, 0, 0, 0, 0)), (1, NONE)]

            def play_free(game, item):
                segs, hor = item
                return route(game, port, target, pre_segs + segs, free,
                             npre + hor)
            if cur is not None and current.get("waiting") and \
                    play_free(n, (cur.segs, horizon)).end in GOOD:
                waiting = cur
            elif not over():
                cs = [c for c in done if c.segs is not None and
                      tries(c)][:40]
                late = [c for c, r in zip(cs, team.map(play_free, [
                    (c.segs, horizon) for c in cs], until))
                    if r is not None and r.end in GOOD]
                if late:
                    late.sort(key=lambda c: c.k + (c.g or 0))
                    waiting = rng.choice(late[len(late) // 2:])
    finally:
        team.close()
        if side is not None:
            if waiter is not None:
                waiter.join()
            side.close()
    faults = team.faults + (side.faults if side is not None else 0)
    wall = (time.time() - t0) * 1000.0
    pool = done + ([cur] if cur is not None else [])
    if not pool:
        return dict(pads=None, ms=ms, wall=wall, tried=0, good=0, routes=[],
                    phase=v.phase, partial=partial, faults=faults,
                    times=times)
    best = max(c.score for c in pool)
    good = [c for c in pool if c.score >= best - margin and c.score > 0]
    routes = [(c.label, c.kind, c.res.end, round(c.score, 1), c.res.frame,
               round(c.exposed, 2)) for c in pool]

    def kind(c):
        return current.get("kind", "?") if c is cur else \
            kind_of(c, c.res, v)

    waits = False
    if good and cur is not None and cur.score >= best - 1e-6:
        choice = cur            # still the best there is: no change
    elif good:
        # one of the best by a softmax, a kind flown lately less often;
        # one weight for each kind, so that a kind with many timings is
        # not drawn that much more often
        # (a route flown some other way than straight in is of its kind's
        # family: it is drawn within it, not as a kind more, or the kinds
        # with many ways, the jump and the drift, would crowd out the rest)
        # (and a route that begins with a stall weighs more: among so
        # many ways straight in it was hardly ever flown, and it is what
        # makes it come later than the player expects)
        stallers = {t.name for t in tools_of(char) if t.stall}
        kinds = {}
        for c in good:
            w = math.exp((c.score - best) / max(temperature, 1e-6)) / \
                (1.0 + 1.5 * list(recent).count(kind(c)))
            if c is not cur and "+" in c.kind and \
                    c.kind.split("+")[0] in stallers:
                w *= STALL_WEIGHT
            kinds.setdefault(family(kind(c)), []).append((c, w))
        names = sorted(kinds)
        k = rng.choices(names, weights=[max(w for _, w in kinds[x])
                                        for x in names])[0]
        cs, ws = zip(*kinds[k])
        choice = rng.choices(cs, weights=ws)[0]
    elif waiting is not None:
        choice = waiting
        waits = True
        if choice is not cur:
            choice.label = "waits for the ledge: " + choice.label
    elif partial and goal is None and v.phase == "air" and v.up > HIGH \
            and not v.helpless and not v.special and \
            any(c.label == "drift in" for c in done):
        # nothing ends well among the few it had time for, and from up
        # here there is time: it drifts on, its jump and its specials
        # kept, and decides again at once
        choice = cur if cur is not None else \
            next(c for c in done if c.label == "drift in")
    else:
        # nothing ends well: it goes for it all the same (the route it is
        # on, if that still has something to press; else the best of those
        # that do something)
        # (one held to a goal only falls: it tries for that to the last)
        doing = [c for c in done if tries(c)] if goal is None else []
        if goal is None and cur is not None and \
                any(raw[0] for _, raw in cur.segs):
            doing.append(cur)
        choice = max(doing or pool, key=lambda c: c.score)
    return dict(pads=frames(choice.segs), label=choice.label,
                kind=kind(choice), end=choice.res.end,
                score=choice.score - (keep if choice is cur else 0.0),
                frame=choice.res.frame, ms=ms, wall=wall, tried=len(pool),
                good=len(good), routes=routes, kept=choice is cur,
                gap=choice.res.gap, exposed=choice.exposed,
                threats=len(field), phase=v.phase, partial=partial,
                faults=faults, waiting=waits, times=times)


def check(n, port, target, pads, their, char=None, horizon=420, goal=None,
          grabs=0):
    """What the route now flown (`pads` from now) comes to: dict(end,
    score, frame, ms)."""
    st = n.state()
    me, them = st["p"][port], st["p"][target]
    if me is None or them is None or not pads:
        return None
    char = char or NAMES.get(me.get("ckind"))
    v = View(me, them, ledges(n), char, grabs)
    # (a player on the ground guards where they stand: four lookaheads;
    # one in the air is the decisions' to weigh, when it sees them commit)
    field = []
    if not (them["air"] or them["state"] == 24):
        field, _ = threats(Team(n, 0), target, their,
                           their[0][0] if their else 0)
    r = route(n, port, target, segments(pads), their, horizon,
              path=bool(field))
    s = score(r, v, None, 0, goal)
    if field and r.end in GOOD:
        s -= exposed_cost(exposure(r.path, field, v.wait)[0])
    return dict(end=r.end, score=s, frame=r.frame, ms=r.ms, gap=r.gap)


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
    their)`), until it stands on the stage again, free to act, or has lost
    its stock (`done`; `ended`: "stage" or "lost"). Off the stage, on the
    ledge, knocked down, hit again: it goes on from wherever it is.

    It decides where its decisions are made (`think`: the game itself
    headless, forked copies of it while a person plays), each for a frame
    `lead` frames on, the pads until then as the decision's pre-roll: a
    route when it has none (`decide`: from the air, from the ledge, from
    the floor), the route checked again every `every` frames (`check`),
    another decided when the check says it no longer ends well, and when
    the player has committed to something new `react` frames ago. A hit,
    the ledge caught and a knockdown end the route it was on.

    `goal`: "ledge": it only goes there, and is over once it hangs (an
    example's opponent, that does the one thing the example answers);
    `tools`: the only ones its routes use ("jump": its jump and drift).
    `adapt` False: it flies the route it first chose, whatever the player
    does. `predict` False: only what the player is doing counts, not what
    they could do. `log`: what it decided, [(frame, words)]; `decisions`:
    each one's record, for a test; `via`: the kinds of route it flew, in
    order; `grabs`: the times it caught the ledge."""

    DROP = 25.0               # a route worth this much less is decided again
    RETRY = 8                 # frames between looks while nothing is good
    # While a person plays, a decision is made for a frame LEAD frames on
    # and must answer by then: `decide` is given that long less SLACK (the
    # copy made, the answer's way back) and answers with what it has. In
    # hitstun there is longer: until it can act, up to LEAD_MOST. (Until
    # 2026-11-17 the lead followed how long decisions took, a third to
    # half a second in the client, more when nothing reached: a fighter
    # hit off the stage with little hitstun fell that long before its
    # first press, and from low it was lost.) A person reacts in about
    # this long.
    LEAD = 14
    LEAD_MOST = 40
    QUICK = 8                 # the shortest: an answer to what the player did
    SLACK = 3
    FRAME = 1.0 / 60
    MORE = 2                  # decisions made again after a partial one
    # An answer that still comes back after its frame (a machine slower
    # than the allowance took it for) is not thrown away: its route is
    # flown from the frame it came, that much later, and checked on the
    # way. (Until 2026-11-17 it was thrown away and asked again, each time
    # as late: from high or far out, where routes are long to play ahead,
    # none ever came in time, and it fell without a press.) And the
    # allowance follows the machine: what a decision is given to think in
    # is its lead less a slack that grows when answers come late or just
    # in time and shrinks when they come early (kept by the thinker, for
    # the session); when the slack is all of it, the lead grows.
    LATE_MOST = 24            # frames late an answer may be, and flown
    THINK = 7                 # frames of thinking a decision needs at least
    LEAD_LONG = 24            # the longest lead out of hitstun

    def __init__(self, think, port, target, rng=None, react=15, half=85.0,
                 memory=None, every=4, budget=64, temperature=8.0,
                 char=None, goal=None, adapt=True, predict=True, tools=None):
        self.think, self.port, self.target = think, port, target
        self.rng = rng or random.Random(0)
        self.react, self.half = react, half
        self.memory = memory if memory is not None else {}
        self.memory.setdefault("recent", [])
        # what its routes came to, the last ten (decide's `outcomes`)
        self.memory.setdefault("outcomes", [])
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
        self.state = None         # its action state the frame before
        self.grabs = 0
        self.via = []
        self.done = False
        self.ended = None
        self.tag = 0
        self.log = []
        self.decisions = []
        self.played = []
        self.late = 0
        self.promise = []         # the pads played until a decision's frame
        self.promise_at = 0
        self.more = 0             # decisions still to make again (partial)
        self.partials = 0
        self.shifted = 0          # answers flown late
        self.dropped = []         # answers not used: (asked, at, frame, why)
        self.faults = 0           # routes the game would not play
        self.first = None         # the frame of its first press
        self.ms = 0.0             # frames played ahead, in ms, summed
        self.wall = 0.0           # how long its decisions took
        self.last = NONE
        self._idle = NONE

    # -- asking ----------------------------------------------------------------

    def _their(self, their):
        return expect(their if their is not None else NONE, 3)

    def _ask(self, kind, fn, lead, pre, allowed=None):
        self.tag += 1
        tag = ("recover", id(self), self.tag)
        self.pending = dict(tag=tag, kind=kind, asked=self.frame,
                            at=self.frame + lead, pre=list(pre),
                            plan=self.plan_at if self.plan else None,
                            allowed=allowed)
        if kind != "recover-check":
            # the pads until its frame are the ones it was made with:
            # played as promised, whatever happens meanwhile
            self.promise, self.promise_at = list(pre), self.frame
        self.think.submit(tag, fn, kind)

    def _lead(self, kind, me):
        """(the frames ahead a decision of `kind` is made for, the seconds
        it may take): (0, None) where nothing waits for it (headless)."""
        if not self.think.lead_for(kind):
            return 0, None
        wait = int(me.get("hitstun") or 0) if me["state"] in DAMAGE else 0
        # (a thinker that is not on the clock, a test's, is given no
        # deadline: what it decides does not depend on the machine)
        if not getattr(self.think, "timed", False):
            return max(self.LEAD, min(wait, self.LEAD_MOST)), None
        slack = getattr(self.think, "recover_slack", float(self.SLACK))
        need = getattr(self.think, "recover_think", float(self.THINK))
        base = min(self.LEAD_LONG,
                   max(self.LEAD, int(math.ceil(slack + need))))
        lead = max(base, min(wait, self.LEAD_MOST))
        return lead, self._allowed(lead)

    def _allowed(self, lead):
        """The seconds a decision made for `lead` frames on may take."""
        slack = getattr(self.think, "recover_slack", float(self.SLACK))
        return max(1.0, lead - slack) * self.FRAME

    def _paced(self, p, got):
        """An answer is back: how long after its deadline it came (the
        routes under way when the time was up, the answer's way back) is
        the slack the next ones are given, measured (kept by the thinker,
        for the session)."""
        think = self.think
        if not getattr(think, "timed", False) or p.get("allowed") is None:
            return
        first = (got.get("times") or {}).get("first")
        if first is not None and p["kind"] == "recover":
            # what it needs before its first route (the copies, the first
            # probes), and four frames of routes
            need = first / 1000.0 / self.FRAME + 4.0
            was = getattr(think, "recover_think", float(self.THINK))
            think.recover_think = max(float(self.THINK),
                                      0.5 * was + 0.5 * need)
        if not got.get("partial"):
            return
        post = (self.frame - p["asked"]) - p["allowed"] / self.FRAME
        slack = getattr(think, "recover_slack", float(self.SLACK))
        slack = 0.6 * slack + 0.4 * (post + 1.0) if post + 1.0 < slack \
            else post + 1.0
        think.recover_slack = min(max(float(self.SLACK), slack),
                                  self.LEAD_MOST - self.THINK)

    def _rest(self, lead=0):
        """The plan's pads from `lead` frames on."""
        i = self.frame - self.plan_at + lead
        return list(self.plan[max(i, 0):])

    def _pre(self, lead, me=None):
        """The pads of the next `lead` frames: the plan's, and after it
        the stick toward the stage once its hitstun is over."""
        i = max(self.frame - self.plan_at, 0)
        out = list(self.plan[i:i + lead])
        if len(out) < lead:
            inward = -1 if (me or {}).get("x", 0.0) >= 0 else 1
            drift = (0, 127 * inward, 0, 0, 0, 0, 0)
            stun = 0
            if me is not None and me["state"] in DAMAGE:
                stun = int(me.get("hitstun") or 0)
            for j in range(len(out), lead):
                out.append(NONE if j < stun or me is None or
                           not me["air"] else drift)
        return out

    def _decide(self, their, lead, me=None, deadline=None):
        port, target, char = self.port, self.target, self.char
        rng = random.Random(self.rng.random())
        pre = self._pre(lead, me)
        rest = self._rest(lead)
        current = dict(pads=rest, kind=self.info.get("kind", "?"),
                       waiting=self.info.get("waiting")) \
            if rest and self.info else None
        seg = self._their(their)
        # (with a route to compare against, fewer: it must come back in
        # time to matter)
        budget = self.budget if current is None else \
            max(20, self.budget * 2 // 5)
        temp = self.temperature
        recent = list(self.memory["recent"][-6:])
        outcomes = list(self.memory["outcomes"][-8:])
        goal, predict, tools = self.goal, self.predict, self.tools
        grabs = self.grabs

        def fn(n):
            return decide(n, port, target, pre, seg, rng, char=char,
                          budget=budget, temperature=temp, recent=recent,
                          current=current, goal=goal, predict=predict,
                          tools=tools, grabs=grabs, outcomes=outcomes,
                          deadline=deadline)
        self._ask("recover" if current is None else "recover-again", fn,
                  lead, pre, deadline)

    def _check(self, their, lead):
        port, target, char, goal = self.port, self.target, self.char, \
            self.goal
        pads = self._rest(0)
        seg = self._their(their)
        grabs = self.grabs

        def fn(n):
            return check(n, port, target, pads, seg, char=char, goal=goal,
                         grabs=grabs)
        self._ask("recover-check", fn, lead, [])

    def _came_to(self, what):
        """What the route it was on came to ("ok", "hit", "lost"), kept
        for the decisions after it (this attempt's and the next ones')."""
        kind = (self.info or {}).get("kind")
        if kind:
            self.memory["outcomes"].append((route_key(kind), what))
            del self.memory["outcomes"][:-10]

    def _drop(self, why=None):
        """The route it was on is over (a hit, the ledge caught, knocked
        down): what was being decided for it is dropped with it."""
        if self.info and why and why.startswith("hit"):
            self._came_to("hit")
        elif self.info:
            self._flown()
        self.plan, self.info, self.need = [], None, True
        self.promise, self.more = [], 0
        self.retry_at = 0
        self.stop()
        if why:
            self.log.append((self.frame, why))

    def _flown(self):
        """The route it was on has been flown: its kind, for variety."""
        kind = (self.info or {}).get("kind")
        if kind and (not self.via or self.via[-1] != kind):
            self.via.append(kind)
            self.memory["recent"].append(kind)
            del self.memory["recent"][:-8]

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
        # (asked about a route that is no longer the one flown: a hit or
        # the ledge ended it since. Nothing of it is used)
        stale = p["plan"] != (self.plan_at if self.plan else None)
        if p["kind"] == "recover-check":
            if stale or self.info is None:
                return
            good = got["end"] in GOOD
            was = self.info["score"]
            if (not good and self.info.get("end") in GOOD) or \
                    got["score"] < was - self.DROP:
                self.need = True
                self.log.append((self.frame, "check: %s %.0f (was %.0f)" % (
                    got["end"], got["score"], was)))
            return
        # (the pads until its frame were its pre-roll, and after it the
        # route's own: those played since it was asked must be the ones it
        # was made with. An answer back a few frames after its frame is
        # still good if what was played meanwhile is what its route begins
        # with: a route that waits, as most do)
        behind = self.frame - p["at"]
        self._paced(p, got)
        made = list(p["pre"]) + list(got.get("pads") or [])
        played = self.played[p["asked"]:self.frame]
        if behind > 0:
            self.late += 1
        since = []
        if stale or behind > self.LATE_MOST:
            self.dropped.append((p["asked"], p["at"], self.frame,
                                 "stale" if stale else "late"))
            self.need = True
            return
        if list(played) != made[:len(played)]:
            # back after its frame, and what was played since is not how
            # its route begins: the route from now, that much later
            since = list(self.played[p["at"]:self.frame])
            self.shifted += 1
            self.checked = -999               # (looked at again at once)
        self.faults += got.get("faults", 0)
        if not got.get("pads"):
            self.need = True
            self.retry_at = self.frame + self.RETRY
            return
        if got.get("partial"):
            # not everything was played in the time it had: once more,
            # with this route in hand, while there is time to change it
            self.partials += 1
            if p["kind"] == "recover":
                self.more = self.MORE
        elif p["kind"] == "recover-again":
            self.more = 0
        # (MELEE_RECOVER_ROUTES: every route each decision tried, kept)
        drop = ("pads",) if os.environ.get("MELEE_RECOVER_ROUTES") else \
            ("pads", "routes")
        self.decisions.append(dict(
            {k: v for k, v in got.items() if k not in drop},
            asked=p["asked"], at=p["at"]))
        if got.get("kept") and self.info is not None:
            self.info["score"] = got["score"]
            self.info["end"] = got["end"]
            if got["end"] in GOOD:
                self.log.append((self.frame, "kept: %s -> %s" % (
                    self.info.get("label"), got["end"])))
        elif not got.get("kept"):
            self.plan = list(p["pre"]) + since + list(got["pads"])
            self.plan_at = p["asked"]
            self.info = dict(kind=got["kind"], score=got["score"],
                             end=got["end"], label=got["label"],
                             waiting=bool(got.get("waiting")))
            self.log.append((self.frame, "%s -> %s %.0f (%d of %d good%s)"
                             % (got["label"], got["end"], got["score"],
                                got["good"], got["tried"],
                                ", exposed %.2f" % got["exposed"]
                                if got.get("exposed") else "")))
        else:
            self.need = True
            return
        self.need = got["end"] not in GOOD
        if self.need:
            # (a rough answer: again at once, there was more to play)
            self.retry_at = self.frame + \
                (0 if got.get("partial") else self.RETRY)
        self.checked = self.frame

    # -- each frame ------------------------------------------------------------

    def pad(self, st, their=None):
        """This frame's raw pad (call once a frame, before it is played).
        `their`: the player's raw pad this frame."""
        me, them = st["p"][self.port], st["p"][self.target]
        self.frame += 1
        if me is None or them is None or self.done:
            self.played.append(NONE)
            return NONE
        phase = phase_of(me, self.char)
        inward = -1 if me["x"] >= 0 else 1
        self._idle = (0, 127 * inward, 0, 0, 0, 0, 0) \
            if phase == "air" and me["state"] not in DAMAGE else NONE
        if phase in ("lost", "stage") or \
                (phase == "ledge" and self.goal == "ledge"):
            self.done, self.ended = True, phase
            self._came_to("lost" if phase == "lost" else "ok")
            self._flown()
            self.stop()
            self.played.append(NONE)
            return NONE
        # what ends the route it was on: a hit, the ledge caught, knocked
        # down on the stage
        s, was = me["state"], self.state
        self.state = s
        # (a hit: its damage with hitlag, or a damage state begun. The 1%
        # for each second off the screen is neither: until 2026-11-17 it
        # ended the route each time, and what was being decided with it)
        if self.percent is not None and me["percent"] > self.percent and \
                ((me.get("hitlag") or 0) > 0 or
                 (s in DAMAGE and was not in DAMAGE)):
            self._drop("hit: %.0f%%" % me["percent"])
        elif s == LEDGE[0] and was != LEDGE[0]:
            self.grabs += 1
            self._drop("the ledge")
        elif s in DOWN and was is not None and was not in DOWN:
            self._drop("knocked down")
        self.percent = me["percent"]
        # the player's commitment: seen `react` frames after it began
        cls = commitment(them)
        if cls != self.cls:
            if self.cls is not None and self.unseen is None and self.adapt:
                self.unseen = self.frame
            self.cls = cls
        self._collect()
        if self.pending is None and phase != "ground":
            have = bool(self._rest(0))
            lead, deadline = self._lead("recover-again" if have else
                                        "recover", me)
            # (what the player commits to is answered `react` frames after
            # it began: a decision for then, begun as early as it can be,
            # and shorter than the others when the reaction is)
            quick = max(self.QUICK, min(lead, self.react)) if lead else 0
            due = self.unseen is not None and \
                self.frame >= self.unseen + self.react - quick
            blind = self.unseen is not None and not due
            if due and have and lead:
                lead = quick
                if deadline is not None:
                    deadline = self._allowed(quick)
            again = have and self.more > 0 and self.adapt and not blind
            if not have or (have and due) or again or (
                    self.need and not blind and self.adapt and
                    self.frame >= self.retry_at):
                if not blind:
                    self.unseen = None        # seen, as of this decision
                if again:
                    self.more -= 1
                self._decide(their, lead, me, deadline)
                self._collect()
            elif self.adapt and not blind and \
                    self.frame - self.checked >= self.every:
                self.checked = self.frame
                self._check(their, self.think.lead_for("recover-check"))
                self._collect()
        i = self.frame - self.plan_at
        j = self.frame - self.promise_at
        raw = self.plan[i] if 0 <= i < len(self.plan) else \
            self.promise[j] if 0 <= j < len(self.promise) else self._idle
        raw = tuple(raw)
        if raw[0] and self.first is None:
            self.first = self.frame
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
