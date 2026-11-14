"""The coach: what a player who keeps missing a drill is told (the owner,
2026-11-13: "If they are struggling to get it, a helpful overlay should pop
up that tells them what they are doing wrong with visual explanations of
what they are doing, the inputs they are pressing, what it should look
like, and how they need to modify their inputs"; the canvas's "Coach: what
went wrong", approved).

What it works from, all of it the game's own:
- the try: its result (the drill's verdict, its timeline of the player's
  inputs against the frame-perfect ones) and, frame by frame, where the
  fighters were and the pad the game was given (Client.drill_frame
  records them);
- the target: the drill's demonstration, played unseen from the same
  situation (the same scenario, the same draws), recorded the same way.

Nothing here talks to the game: Client gathers, these functions say.
"""

# How the paths are drawn (dp): a panel's drawing area
PATH_W, PATH_H = 412, 236
PAD = 26             # room round the path, for the tags
MAX_SCALE = 9.0      # dp per game unit: a small movement is not blown up
LEAD = 8             # frames shown before the timeline's first
STICK = 80.0         # the pad's units at full tilt


class Track:
    """What one run of an attempt did, frame by frame (the attempt's own
    frame numbers, from 0): `me` and `cpu` (x, y, airborne, state) or None,
    `pads` the pad the game was given for the next frame."""

    def __init__(self):
        self.me, self.cpu, self.pads = [], [], []

    def add(self, c, pad=None, frame=None):
        """Frame by frame, from the drill's context (`c.me`, `c.cpu`); at
        the attempt's `frame` (frames skipped are None)."""
        while frame is not None and len(self.me) < frame:
            self.me.append(None)
            self.cpu.append(None)
            self.pads.append(None)
        if frame is not None and len(self.me) > frame:
            del self.me[frame:], self.cpu[frame:], self.pads[frame:]
        self.me.append((c.me.pos[0], c.me.pos[1], c.me.airborne,
                        c.me.state) if c.me else None)
        self.cpu.append((c.cpu.pos[0], c.cpu.pos[1], c.cpu.airborne,
                         c.cpu.state) if c.cpu else None)
        self.pads.append(dict(pad) if pad is not None else None)

    def __len__(self):
        return len(self.me)


def plural(n, word):
    return "%d %s%s" % (n, word, "" if n == 1 else "s")


def misses(row):
    """Each row's first press against its first frame-perfect one: (label,
    yours or None, perfect, window or None)."""
    out = []
    for r in row:
        if not r.get("perfect"):
            continue
        out.append((r["label"], r["you"][0] if r["you"] else None,
                    r["perfect"][0], r.get("window")))
    return out


def first_wrong(timeline):
    """The first row the player was off on: (label, yours or None, perfect,
    window), or None (every row on its frame, or no timeline)."""
    if not timeline:
        return None
    for label, you, perfect, window in misses(timeline["rows"]):
        if you is None:
            return (label, None, perfect, window)
        if window and window[0] <= you <= window[1]:
            continue
        if you != perfect:
            return (label, you, perfect, window)
    return None


def frame_no(timeline, f):
    """A frame of the timeline shown (from 1) as the drill counts it."""
    return f + timeline.get("first", 1) - 1


def headline(result):
    """The card's title: what was off, in a few words."""
    tl = result.get("timeline")
    wrong = first_wrong(tl)
    if wrong is not None:
        label, you, perfect, _ = wrong
        if you is None:
            return "No %s in time" % label.lower()
        k = you - perfect
        return "%s %s %s" % (label, plural(abs(k), "frame"),
                             "late" if k > 0 else "early")
    return result.get("words") or "Missed"


def fix(result, guide_lines=()):
    """How to change the inputs: from the timeline when there is one, the
    drill's own words otherwise."""
    tl = result.get("timeline")
    wrong = first_wrong(tl)
    note = (tl or {}).get("note", "")
    if wrong is not None:
        label, you, perfect, window = wrong
        due = frame_no(tl, perfect)
        if you is None:
            text = "Press %s on frame %d." % (label, due)
        else:
            k = you - perfect
            text = "Press %s %s %s: on frame %d, not %d." % (
                label, plural(abs(k), "frame"),
                "earlier" if k > 0 else "later", due, frame_no(tl, you))
        if window and window[1] > window[0]:
            text += " Frames %d to %d count." % (frame_no(tl, window[0]),
                                                  frame_no(tl, window[1]))
        return (text + " " + note).strip()
    if note:
        return note
    return sentences(" ".join(guide_lines), 2)


def sentences(text, n):
    """The first `n` sentences of `text`."""
    out, rest = [], " ".join(text.split())
    while rest and len(out) < n:
        cut = min((i for i in (rest.find(". "), rest.find("! "),
                               rest.find("? ")) if i >= 0),
                  default=len(rest) - 1)
        out.append(rest[:cut + 1])
        rest = rest[cut + 2:]
    return " ".join(out)


def target_words(timeline):
    """Under the target's picture: each input on its frame."""
    if not timeline:
        return "The drill's demonstration, from the same start."
    parts = ["%s on frame %d" % (label, frame_no(timeline, perfect))
             for label, _, perfect, _ in misses(timeline["rows"])]
    if not parts:
        return "The drill's demonstration, from the same start."
    text = ", ".join(parts)
    return text[0].upper() + text[1:] + "."


def span(result, track):
    """The attempt frames the pictures show: from a little before the
    timeline's first to its last (or the whole try, without one)."""
    tl = result.get("timeline")
    if tl and "start" in tl:
        lo = max(0, tl["start"] - LEAD)
        hi = min(len(track) - 1, tl["start"] + tl["frames"] - 1)
        if hi > lo:
            return lo, hi
    return max(0, len(track) - 90), len(track) - 1


def marks(result):
    """{attempt frame: tag} for the first press of each of the timeline's
    rows ("F9 · DODGE": the frame as the drill counts it)."""
    tl = result.get("timeline")
    out = {}
    if not tl or "start" not in tl:
        return out
    for r in tl["rows"]:
        # where a press starts: not a held one going on from before
        starts = [f for f in r["you"] if f - 1 not in r["you"] and
                  not (f == 1 and tl.get("first", 1) > 1)]
        for f in starts[:1]:
            out.setdefault(tl["start"] + f - 1, "F%d · %s" % (
                frame_no(tl, f), r["label"].upper()))
    return out


def frame(scale_from, box=(PATH_W, PATH_H)):
    """Where the paths' points go in a box: one scale for x and y (game
    units are square), fitted to every point of `scale_from` (both paths,
    so the two pictures compare), the floor kept low. Returns fn(x, y) ->
    (left, top) in dp, and the floor's top or None."""
    xs = [p[0] for p in scale_from]
    ys = [p[1] for p in scale_from]
    if not xs:
        return (lambda x, y: (box[0] / 2, box[1] / 2)), None
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h = box[0] - 2 * PAD, box[1] - 2 * PAD - 12
    s = min(MAX_SCALE, w / max(x1 - x0, 1e-3), h / max(y1 - y0, 1e-3))
    cx = (x0 + x1) / 2
    floor = min((p[1] for p in scale_from if not p[2]), default=None)

    def at(x, y):
        return (box[0] / 2 + (x - cx) * s,
                box[1] - PAD - 12 - (y - y0) * s)
    return at, (at(cx, floor)[1] if floor is not None else None)


def picture(track, lo, hi, presses, colour, scale_from, box=(PATH_W,
                                                               PATH_H)):
    """A path's dots and tags: [(left, top, kind, text)] with kind "me",
    "cpu", "mark", "tag"; and the floor's top."""
    at, floor = frame(scale_from, box)
    out = []
    for k in range(lo, hi + 1):
        o = track.cpu[k] if k < len(track.cpu) else None
        if o is not None:
            x, y = at(o[0], o[1])
            out.append((x, y, "cpu", ""))
    for k in range(lo, hi + 1):
        p = track.me[k] if k < len(track.me) else None
        if p is None:
            continue
        x, y = at(p[0], p[1])
        if k in presses:
            out.append((x, y, "mark", ""))
            out.append((x, y, "tag", presses[k]))
        else:
            out.append((x, y, "me" if p[2] else "ground", ""))
    return out, floor


def points(track, lo, hi):
    return [p for p in track.me[lo:hi + 1] if p is not None]


def stick_words(pad):
    """A pad as the replay's line says it: the buttons held, the stick."""
    if not pad:
        return ""
    names = [n for n, bit in (("A", 0x100), ("B", 0x200), ("X", 0x400),
                              ("Y", 0x800), ("Z", 0x10), ("L", 0x40),
                              ("R", 0x20)) if pad.get("buttons", 0) & bit]
    if pad.get("lt", 0) > 40 and "L" not in names:
        names.append("L")
    if pad.get("rt", 0) > 40 and "R" not in names:
        names.append("R")
    lx, ly = pad.get("lx", 0) / STICK, pad.get("ly", 0) / STICK
    cx, cy = pad.get("cx", 0) / STICK, pad.get("cy", 0) / STICK
    parts = names
    if abs(lx) > 0.2 or abs(ly) > 0.2:
        parts.append("Stick %+.2f %+.2f" % (max(-1, min(1, lx)),
                                           max(-1, min(1, ly))))
    if abs(cx) > 0.2 or abs(cy) > 0.2:
        parts.append("C %+.2f %+.2f" % (max(-1, min(1, cx)),
                                       max(-1, min(1, cy))))
    return " · ".join(parts) or "Nothing held"
