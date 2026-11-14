"""The search engine's Python side (src/host/engine.c).

    from melee_engine.search import search
    res = search(n, port=1, target=0, horizon=60, budget=6000, depth=3,
                 contact=50)
    res.lines[0].names    # "dash_in+sh_nair_in"
    res.lines[0].pads     # [(frames, pad dict as Native.pad takes it)]

A line is the best the engine found starting with one first move; lines
come best first. The game is exactly as it was afterwards.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "melee_native"))

from native import BUTTONS  # noqa: E402

NAMES = {bit: name for name, bit in BUTTONS.items()}
CONTACT = {0: None, 1: "hit", 2: "shield", 3: "beaten", 4: "grab"}


class Line:
    __slots__ = ("value", "dmg", "taken", "ko", "contact", "contact_at",
                 "adv", "pos", "dist", "len", "first_len", "names",
                 "segments")

    def __init__(self, text):
        v = text.split(" ", 12)
        self.value, self.dmg, self.taken = float(v[0]), float(v[1]), \
            float(v[2])
        self.ko, self.contact, self.contact_at = int(v[3]), \
            CONTACT[int(v[4])], int(v[5])
        self.adv, self.pos, self.dist = float(v[6]), float(v[7]), float(v[8])
        self.len, self.first_len, self.names = int(v[9]), int(v[10]), v[11]
        self.segments = []
        for seg in (v[12].split(",") if len(v) > 12 and v[12] else []):
            w = seg.split()
            self.segments.append((int(w[0]), int(w[1], 16)) +
                                 tuple(int(x) for x in w[2:8]))

    @property
    def moves(self):
        return self.names.split("+")

    def pads(self):
        """[(frames, pad)] with pads as Native.pad takes them."""
        out = []
        for n, b, lx, ly, cx, cy, lt, rt in self.segments:
            pad = dict(stick=(lx / 127.0, ly / 127.0),
                       cstick=(cx / 127.0, cy / 127.0),
                       l=lt / 255.0, r=rt / 255.0)
            pad["buttons"] = [name for bit, name in NAMES.items() if b & bit]
            out.append((n, pad))
        return out

    def raw(self):
        """Per-frame raw pads: (buttons, lx, ly, cx, cy, lt, rt)."""
        out = []
        for n, *rest in self.segments:
            out += [tuple(rest)] * n
        return out

    def __repr__(self):
        return "<%s %.1f: dmg %.0f taken %.0f %s%s in %d>" % (
            self.names, self.value, self.dmg, self.taken,
            self.contact or "no contact",
            " KO" if self.ko > 0 else "", self.len)


class Result:
    def __init__(self, head, lines):
        w = head.split()
        self.ms, self.trials, self.frames = float(w[1]), int(w[2]), int(w[3])
        self.lines = lines

    @property
    def best(self):
        return self.lines[0] if self.lines else None


def search(n, port, target, horizon=60, budget=4000, depth=3, **weights):
    """Search PORT's lines against TARGET from the current frame. Keyword
    weights: dmg, taken, ko, pos, adv, contact, shield, hit, close, dist,
    held, lcancel; and moves="dash_,sh_" (the first moves allowed, by name
    prefix). See engine.c."""
    state = n.state()
    extra = " ".join(("%s=%s" if isinstance(v, str) else "%s=%g") % (k, v)
                     for k, v in weights.items())
    head = n._cmd("search %d %d %d %d %d %s" % (port, target, horizon,
                                                budget, depth, extra))
    lines = []
    while True:
        reply = n._reply()
        if reply == "end":
            break
        if reply.startswith("line "):
            lines.append(Line(reply[5:]))
    n._state = state                       # nothing changed
    return Result(head, lines)


def preroll(n, raws):
    """PORT's inputs for the next search's first frames, before it branches
    (raw pads, one a frame): the search is then for where they end."""
    words = ["1 %x %d %d %d %d %d %d" % tuple(r) for r in raws]
    n._cmd("engine preroll " + " ".join(words))


def player(n, segments=None):
    """The target's inputs for the next searches: [(frames, raw pad)] with
    raw pads (buttons, lx, ly, cx, cy, lt, rt); None: it holds its pad."""
    words = []
    for frames, raw in segments or []:
        b, lx, ly, cx, cy, lt, rt = raw
        words.append("%d %x %d %d %d %d %d %d" % (frames, b, lx, ly, cx, cy,
                                                  lt, rt))
    n._cmd("engine player " + " ".join(words))
