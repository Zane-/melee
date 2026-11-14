"""The coach: what a player who keeps missing a drill is told (the owner,
2026-11-13: "If they are struggling to get it, a helpful overlay should pop
up that tells them what they are doing wrong with visual explanations of
what they are doing, the inputs they are pressing, what it should look
like, and how they need to modify their inputs"; the canvas's "Coach: what
went wrong", approved).

What it works from, all of it the game's own:
- the try: its result (the drill's verdict, its timeline of the player's
  inputs against the frame-perfect ones) and, frame by frame, where the
  fighters were, the pad the game was given and the game's own picture
  (Client.drill_frame records them; the pictures are kept by the game,
  src/host/frames.c, the owner, 2026-11-14: "Need to ensure this is generic
  and works across the board");
- the target: the drill's demonstration, played unseen from the same
  situation (the same scenario, the same draws), or for a drill judged by
  the frame (tools/melee_actor/tech.py) the try itself with what was wrong
  put right, from a state saved before it; recorded the same way.

Nothing here talks to the game: Client gathers, these functions say.
"""

# How the paths are drawn (dp): a panel's drawing area (the pictures too;
# TALL_H without a timeline below them)
PATH_W, PATH_H = 412, 236
TALL_H = 340
PAD = 26             # room round the path, for the tags
MAX_SCALE = 9.0      # dp per game unit: a small movement is not blown up
LEAD = 8             # frames shown before the timeline's first
AFTER = 24           # frames shown after the try's last (how it ended)
STICK = 80.0         # the pad's units at full tilt
GAME_W, GAME_H = 640.0, 480.0   # the game's picture, in its own units


class Track:
    """What one run of an attempt did, frame by frame (the attempt's own
    frame numbers, from 0): `me` and `cpu` (x, y, airborne, state) or None,
    `pads` the pad the game was given for the next frame, `pictures` the
    number of the game's picture of it (Native.frames_view) or None.
    `ring`: the ring of pictures it is in (0 the live one, 1 a run played
    unseen)."""

    def __init__(self, ring=0):
        self.me, self.cpu, self.pads, self.pictures = [], [], [], []
        self.ring = ring
        self.attempt = None     # (tech) the entry of the attempt's frame 1

    def add(self, c, pad=None, frame=None, picture=None):
        """Frame by frame, from the drill's context (`c.me`, `c.cpu`); at
        the attempt's `frame` (frames skipped are None)."""
        while frame is not None and len(self.me) < frame:
            self.me.append(None)
            self.cpu.append(None)
            self.pads.append(None)
            self.pictures.append(None)
        if frame is not None and len(self.me) > frame:
            del self.me[frame:], self.cpu[frame:], self.pads[frame:]
            del self.pictures[frame:]
        self.add_fighters(c.me, c.cpu, pad, picture)

    def add_fighters(self, me, cpu, pad=None, picture=None):
        self.me.append((me.pos[0], me.pos[1], me.airborne, me.state)
                       if me else None)
        self.cpu.append((cpu.pos[0], cpu.pos[1], cpu.airborne, cpu.state)
                        if cpu else None)
        self.pads.append(dict(pad) if pad is not None else None)
        self.pictures.append(picture)

    def drop(self, n):
        """The first `n` frames forgotten (a rolling record)."""
        del self.me[:n], self.cpu[:n], self.pads[:n], self.pictures[:n]
        if self.attempt is not None:
            self.attempt -= n

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


def frame_label(timeline, f):
    """A frame of the timeline as the pictures say it: "F9", or with the
    timeline's own labels "3 TO LAND" (an L-cancel's count to landing);
    None outside a labelled timeline."""
    labels = timeline.get("labels")
    if not labels:
        return "F%d" % frame_no(timeline, f)
    if 1 <= f <= len(labels):
        return ("%s %s" % (labels[f - 1], timeline.get("label_word", "")))\
            .strip().upper()
    return None


def headline(result):
    """The card's title: what was off, in a few words."""
    if result.get("headline"):
        return result["headline"]
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
    """How to change the inputs: the judge's own when it says (a drill
    judged by the frame), from the timeline when there is one, the drill's
    own words otherwise."""
    if result.get("fix"):
        return result["fix"]
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


def span(result, track, longest=90):
    """The attempt frames the pictures show: from a little before the
    timeline's first to its last (or the try's last `longest`, without
    one)."""
    tl = result.get("timeline")
    if tl and "start" in tl:
        lo = max(0, tl["start"] - LEAD)
        hi = min(len(track) - 1, tl["start"] + tl["frames"] - 1)
        if hi > lo:
            return lo, hi
    return max(0, len(track) - longest), len(track) - 1


def crop(boxes, box=(PATH_W, PATH_H), margin=36.0, least=200.0):
    """The part of the game's picture a panel shows: every box (where the
    fighters were, x0 y0 x1 y1 in the game's 640x480) with a margin, at
    the panel's shape, no closer than `least` wide, inside the picture.
    (left, top, width, height) in the game's units; the whole picture's
    middle band without boxes."""
    aspect = float(box[0]) / box[1]
    boxes = [b for b in boxes if b is not None]
    if not boxes:
        w = GAME_W
        return 0.0, (GAME_H - w / aspect) / 2, w, w / aspect
    x0 = min(b[0] for b in boxes) - margin
    x1 = max(b[2] for b in boxes) + margin
    y0 = min(b[1] for b in boxes) - margin
    y1 = max(b[3] for b in boxes) + margin * 0.6
    w = max(x1 - x0, (y1 - y0) * aspect, least)
    w = min(w, GAME_W, GAME_H * aspect)
    h = w / aspect
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    left = min(max(cx - w / 2, 0.0), GAME_W - w)
    top = min(max(cy - h / 2, 0.0), GAME_H - h)
    return left, top, w, h


def press_starts(row, first=1):
    """The frames a row's presses start on (not a hold going on)."""
    return [f for f in row["you"] if f - 1 not in row["you"] and
            not (f == 1 and first > 1)]


def marks(result):
    """{attempt frame: tag} for the first press of each of the timeline's
    rows ("F9 · DODGE": the frame as the drill counts it)."""
    tl = result.get("timeline")
    out = {}
    if not tl or "start" not in tl:
        return out
    for r in tl["rows"]:
        # where a press starts: not a held one going on from before
        for f in press_starts(r, tl.get("first", 1))[:1]:
            out.setdefault(tl["start"] + f - 1, "%s · %s" % (
                frame_label(tl, f), r["label"].upper()))
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
