"""Tech drills: the player alone, judged on the frames of their own inputs.

A scenario (scenario.py) judges what happened between two fighters. A tech
drill has no opponent to speak of; it watches the player's pad and their
fighter's states frame by frame, finds each attempt at the technique, and
says by how many frames it was right or wrong.

    {
      "drill": "universal-short-hop",      the course drill this is
      "tech": "short_hop",                 short_hop | wavedash
      "name": "...", "about": "...",
      "p2": "marth", "stage": "final-destination",
      "start": -20,                        where the player stands
      "tolerance": 2                       frames late that still count
    }

`Session(spec, game, person, character)` has scenario.Session's shape:
`run()` returns after one attempt with {"success", "checks", "words",
"timeline", "frames"}. An attempt starts when the fighter enters jump squat
from the ground; there is nothing to wait for between attempts, so the
player sets the pace.

What the rules are was measured, not assumed (the numbers are frames, the
first being the one the jump is pressed on; J is the character's jump
squat, 3 for Fox, 4 for Marth, 8 for Bowser):

- the fighter is in jump squat on frames 1 to J and in the air on J + 1;
- the jump is a short hop when the button is held for at most J - 1 frames;
- an air dodge pressed on frame J + 1 lands at once (a frame-perfect
  wavedash); pressed during jump squat it does not come out at all, even
  if held; each frame later is a frame more in the air.

Which of the two jumps came out is read from the game (the upward speed on
the first frame in the air, against the two speeds measured for this
character when the drill is set up), not from the buttons.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(HERE, "..", "melee_native"), os.path.join(HERE, "..")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

WAIT, SQUAT, JUMP_F, JUMP_B = 14, 24, 25, 26
LANDING, LANDING_SPECIAL, AIR_DODGE = 42, 43, 236
JUMP = 0x400 | 0x800              # X or Y
SHOULDER = 0x40 | 0x20            # L or R, pressed all the way


class Session:
    """A game with one tech drill set up in it."""

    def __init__(self, spec, game, person=0, character="fox", live=True):
        self.sc = spec
        self.n = game
        self.person = person
        self.live = live              # the pad is a person's (the window)
        self.start = float(spec.get("start", -20))
        self.tolerance = int(spec.get("tolerance", 2))
        self.kind = spec["tech"]
        if self.kind not in ("short_hop", "wavedash"):
            raise ValueError("no such tech drill: " + self.kind)
        game.start(character, spec.get("p2", "marth"),
                   spec.get("stage", "final-destination"),
                   spec.get("seed", 1))
        self._home()
        self.squat, self.hop, self.full = self._measure()
        self._home()

    def close(self):
        pass

    # ---- setting up -------------------------------------------------------------

    def _home(self):
        n = self.n
        n.pad(self.person)
        n.place(self.person, self.start, 0.0, 1)
        n.place(1 - self.person, 72.0, 0.0, -1)
        n.step(4)

    def _jump(self, hold):
        """A scripted jump with the button held `hold` frames: (frames of
        jump squat, upward speed on the first frame in the air)."""
        n, p = self.n, self.person
        squat, speed = 0, None
        for frame in range(90):
            n.pad(p, buttons=["X"] if frame < hold else [])
            n.step()
            f = n.fighter(p)
            if f.state == SQUAT:
                squat += 1
            elif f.airborne and speed is None:
                speed = f.vel[1]
            elif speed is not None and not f.airborne and f.state == WAIT:
                break
        n.pad(p)
        n.step(2)
        return squat, speed

    def _measure(self):
        squat, hop = self._jump(1)
        _, full = self._jump(squat + 4)
        if squat < 1 or hop is None or full is None or full <= hop:
            raise RuntimeError("could not measure the jumps: squat %s, "
                               "speeds %s and %s" % (squat, hop, full))
        return squat, hop, full

    # ---- watching -----------------------------------------------------------------

    def _pad(self):
        """The pad the game uses in the next frame."""
        if self.live:
            return dict(self.n.pads()[self.person])
        return dict(self.n.h.pads[self.person])

    def _keep_on_stage(self, f):
        if f.pos[1] < -30 or (f.state == WAIT and abs(f.pos[0]) > 50):
            self.n.place(self.person, self.start, 0.0,
                         1 if f.facing >= 0 else -1)

    def run(self, jitter=0.0, run=0, each_frame=None):
        """Watch until one attempt has been made and judge it."""
        n, p = self.n, self.person
        pads, states = [], []
        began = None              # index of the first frame of jump squat
        frame = 0
        while True:
            if each_frame is not None:
                each_frame(n, frame if began is not None else 0)
            pad = self._pad()
            n.step()
            f = n.fighter(p)
            if began is None:
                self._keep_on_stage(f)
                if f.state == SQUAT:
                    # (the frame before, for whether a press is a new one)
                    pads = pads[-1:] + [pad]
                    states = [f]
                    began = len(pads) - 1
                    frame = 1
                else:
                    pads = [pad]
                continue
            pads.append(pad)
            states.append(f)
            frame += 1
            result = getattr(self, "_judge_" + self.kind)(
                pads[began:], pads[began - 1] if began else None, states)
            if result is not None:
                result["frames"] = len(states)
                result["name"] = self.sc.get("name", "")
                return result

    # ---- the judges (frame numbers here start at 1 with the jump) ------------------

    def _squat_frames(self, states):
        return sum(1 for f in states if f.state == SQUAT)

    def _judge_short_hop(self, pads, before, states):
        f = states[-1]
        if not f.airborne:
            if f.state == SQUAT:
                return None
            return self._none("The jump did not come out")
        squat = self._squat_frames(states)
        short = abs(f.vel[1] - self.hop) < abs(f.vel[1] - self.full)
        held = 0
        for pad in pads:
            if not pad["buttons"] & JUMP:
                break
            held += 1
        window = squat - 1
        if held == 0:
            how = "Jumped with the stick"
        elif held == len(pads):
            # (judged on the first frame in the air: how much longer the
            # button stays down is not known yet, and does not matter)
            how = "Jump still held on frame %d" % held
        else:
            how = "Jump held %d frame%s" % (held, "" if held == 1 else "s")
        words = ("Short hop. %s" % how if short else
                 "Full hop. %s: let go within %d" % (how, window))
        return dict(
            success=short, words=words,
            checks=[dict(expect="A short hop", passed=short, detail=how),
                    dict(expect="Jump let go within %d frames" % window,
                         passed=0 < held <= window, detail=how)],
            timeline=dict(
                frames=max(squat + 2, min(held, squat + 4)),
                rows=[dict(label="Jump", you=list(range(1, held + 1)),
                           perfect=[], window=[1, window])],
                note="In the air on frame %d." % (squat + 1)))

    def _judge_wavedash(self, pads, before, states):
        f = states[-1]
        squat = self._squat_frames(states)
        if f.state == SQUAT:
            return None
        perfect = squat + 1                 # the frame the air dodge is due
        # the first new press of L or R, as a frame number
        pressed = None
        last = before["buttons"] if before else 0
        for i, pad in enumerate(pads):
            if pad["buttons"] & SHOULDER and not last & SHOULDER:
                pressed = i + 1
                if pressed >= perfect:
                    break
            last = pad["buttons"]
        landed = f.state == LANDING_SPECIAL
        over = landed or (not f.airborne) or len(states) > perfect + 14
        if not over:
            return None
        late = pressed - perfect if pressed is not None else None
        in_time = landed and late is not None and \
            0 <= late <= self.tolerance
        if pressed is None:
            words = "No air dodge: press L or R as you leave the ground"
        elif late < 0:
            words = ("Air dodge %d frame%s early: it only comes out in the "
                     "air" % (-late, "" if late == -1 else "s"))
        elif not landed:
            words = ("The air dodge did not reach the ground: hold the "
                     "stick down and to the side")
        elif late == 0:
            words = "Frame-perfect"
        elif in_time:
            words = "Air dodge %d frame%s late, in the window" % (
                late, "" if late == 1 else "s")
        else:
            words = "Air dodge %d frames late: %d allowed" % (
                late, self.tolerance)
        return dict(
            success=bool(in_time), words=words,
            checks=[dict(expect="The wavedash came out", passed=landed,
                         detail=""),
                    dict(expect="Air dodge within %d frame%s of leaving "
                         "the ground" % (self.tolerance, "" if
                                         self.tolerance == 1 else "s"),
                         passed=bool(in_time), detail=words)],
            timeline=dict(
                frames=max(perfect + self.tolerance + 2,
                           min(pressed or 0, perfect + 8)),
                rows=[dict(label="Jump", you=[1], perfect=[], window=None),
                      dict(label="L or R",
                           you=[pressed] if pressed else [],
                           perfect=[perfect],
                           window=[perfect, perfect + self.tolerance])],
                note="Jump squat is frames 1 to %d." % squat))

    def _none(self, why):
        return dict(success=False, words=why, checks=[
            dict(expect=why, passed=False, detail="")], timeline=None)


def load(path):
    import json
    with open(path) as f:
        return json.load(f)
