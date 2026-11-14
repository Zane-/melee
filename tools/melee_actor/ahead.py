"""Lookahead: ask the game what an input plan would do, before doing it.

The native build plays the next frames with a planned pad for one port
while every other port keeps holding what it holds now (a person's live
pad too: the guess rollback netcode makes), reports what happened frame by
frame, and undoes them (src/host/ahead.c). A 30-frame look costs about 5 ms
on the unoptimised build, so the actor can look before it commits, every
frame, in a match a person is playing.

That is what makes a scripted opponent fair to train against. A drill that
says "Falcon jumps in with a nair" means a nair that would land: if the
player dashes forward or back before Falcon has committed, Falcon waits,
moves, drifts and times the button so that it still lands, and only what
the drill teaches (shield it, wavedash out, hit him first) beats it.

    look(n, port=1, target=0, plan=[(1, dict(buttons=["X"])),
                                    (13, dict(stick=(-1, 0))),
                                    (1, dict(stick=(-1, 0), buttons=["A"])),
                                    (20, dict(stick=(-1, 0)))])
    -> Outlook: .contact ("hit", "shield", "beaten" or None), .frame, and
       for a miss how it missed (.gap, .gx)

Plans are segments (frames, pad), pads as Native.pad takes them.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "melee_native"))

from native import BUTTONS  # noqa: E402

GUARD_ON, GUARD, GUARD_OFF, GUARD_STUN, GUARD_REFLECT = 178, 179, 180, 181, \
    182
GUARDING = (GUARD_ON, GUARD, GUARD_OFF, GUARD_STUN, GUARD_REFLECT)
NO_GAP = 999.0


class Row:
    """The state after one frame played ahead."""
    __slots__ = ("a_state", "a_x", "a_y", "a_air", "a_percent", "a_hitlag",
                 "a_hitbox", "a_facing", "t_state", "t_x", "t_y", "t_air",
                 "t_percent", "t_shield", "t_hitlag", "gap", "gx")

    def __init__(self, text):
        v = text.split()
        (self.a_state, self.a_air, self.a_hitbox, self.t_state,
         self.t_air) = (int(v[0]), int(v[3]), int(v[6]), int(v[8]),
                        int(v[11]))
        (self.a_x, self.a_y, self.a_percent, self.a_hitlag, self.a_facing,
         self.t_x, self.t_y, self.t_percent, self.t_shield, self.t_hitlag,
         self.gap, self.gx) = (float(v[1]), float(v[2]), float(v[4]),
                               float(v[5]), float(v[7]), float(v[9]),
                               float(v[10]), float(v[12]), float(v[13]),
                               float(v[14]), float(v[15]), float(v[16]))


class Outlook:
    """What a plan did, seen ahead.

    contact: "hit" (the target took damage), "shield" (it hit the target's
    shield), "beaten" (the actor was hit first), or None (it missed).
    frame: the frame of the plan it happened on (0 = the first).
    gap / gx: for the frame its hitbox came nearest the target: how far
    from touching (edge to edge; negative = overlapping) and where along the
    actor's facing it was relative to the target's centre (negative =
    short). gap is NO_GAP when no hitbox came out."""

    def __init__(self, rows, percent, own, ms):
        self.rows, self.ms = rows, ms
        self.contact, self.frame = None, None
        self.gap, self.gx, self.near = NO_GAP, 0.0, None
        for i, r in enumerate(rows):
            if r.a_percent > own:
                self.contact, self.frame = "beaten", i
                break
            if r.t_percent > percent:
                self.contact, self.frame = "hit", i
                break
            if r.t_hitlag > 0 and r.t_state in GUARDING:
                self.contact, self.frame = "shield", i
                break
            if r.gap < self.gap:
                self.gap, self.gx, self.near = r.gap, r.gx, i

    def connects(self, what="any"):
        """Whether the plan landed: "any" (hit or shield), "hit", "shield"."""
        if what == "any":
            return self.contact in ("hit", "shield")
        return self.contact == what

    def landed_at(self):
        """The first frame the actor was on the ground again after having
        left it, or None."""
        flew = False
        for i, r in enumerate(self.rows):
            if r.a_air:
                flew = True
            elif flew:
                return i
        return None

    def __repr__(self):
        if self.contact:
            return "<%s on %d>" % (self.contact, self.frame)
        if self.gap >= NO_GAP:
            return "<no hitbox>"
        return "<miss by %.1f, %+.1f along>" % (self.gap, self.gx)


def pad_words(buttons=(), stick=(0, 0), cstick=(0, 0), l=0, r=0):
    """A pad as Native.pad takes it, in the protocol's words."""
    mask = sum(BUTTONS[b.upper()] for b in buttons)
    lx, ly = (int(round(max(-1, min(1, v)) * 127)) for v in stick)
    cx, cy = (int(round(max(-1, min(1, v)) * 127)) for v in cstick)
    return "%x %d %d %d %d %d %d" % (mask, lx, ly, cx, cy, int(l * 255),
                                     int(r * 255))


def look(n, port, target, plan, stop=1):
    """Play `plan` ([(frames, pad), ...]) for `port` ahead, everyone else
    holding their pads, and undo it. `stop`: frames to go on after the
    first contact (0: all of the plan). The game is exactly as it was
    afterwards; the state `n` had read stays good."""
    segs = []
    for frames, pad in plan:
        if frames > 0:
            segs.append("%d %s" % (frames, pad_words(**pad)))
    me, them = n.fighter(port), n.fighter(target)
    state = n.state()
    reply = n._cmd("ahead %d %d %d %s" % (port, target, stop,
                                          " ".join(segs)))
    n._state = state                      # nothing changed
    head, _, body = reply.partition(" ")
    ms, _, body = body.partition(" ")
    rows = [Row(t) for t in body.split(";") if t.strip()]
    return Outlook(rows, them.percent, me.percent, float(ms))


def compress(pads):
    """A list of per-frame pads as segments."""
    plan = []
    for pad in pads:
        if plan and plan[-1][1] == pad:
            plan[-1] = (plan[-1][0] + 1, pad)
        else:
            plan.append((1, pad))
    return plan
