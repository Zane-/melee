"""Tech drills: the player alone, judged on the frames of their own inputs.

A scenario (scenario.py) judges what happened between two fighters. A tech
drill has no opponent to speak of; it watches the player's pad and their
fighter's states frame by frame, finds each attempt at the technique, and
says by how many frames it was right or wrong.

    {
      "drill": "universal-short-hop",      the course drill this is
      "tech": "short_hop",                 short_hop | wavedash | l_cancel | shffl
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

- L, R (pressed at all) or Z halves an aerial's landing lag when pressed
  on the frame the fighter lands or on one of the six before it: seven
  frames; an eighth frame early, or a frame late, does nothing;
- a fast fall is the fall speed jumping to the character's fast fall speed.

Which of the two jumps came out is read from the game (the upward speed on
the first frame in the air, against the two speeds measured for this
character when the drill is set up), not from the buttons. Whether the lag
was halved is read from the game too: the frames spent in the landing
state, against that aerial's two lags in data/framedata/<character>.json.

An L-cancel attempt is any aerial (it starts when the attack does); if the
attack is over before the fighter lands there is nothing to cancel, and
the result says so and is marked "skip": it is not an attempt.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(HERE, "..", "melee_native"), os.path.join(HERE, "..")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

WAIT, SQUAT, JUMP_F, JUMP_B = 14, 24, 25, 26
LANDING, LANDING_SPECIAL, AIR_DODGE = 42, 43, 236
AERIAL = (65, 69)                 # neutral, forward, back, up, down
LAND_AIR = (70, 74)               # landing during each of them
AERIALS = ("nair", "fair", "bair", "uair", "dair")
JUMP = 0x400 | 0x800              # X or Y
SHOULDER = 0x40 | 0x20            # L or R, pressed all the way
Z = 0x10
KINDS = ("short_hop", "wavedash", "l_cancel", "shffl")
ROOT = os.path.join(HERE, "..", "..")


def _cancel_down(pad):
    """L, R or Z as an L-cancel takes them: a light press counts."""
    return bool(pad["buttons"] & (SHOULDER | Z)) or pad["lt"] >= 60 or \
        pad["rt"] >= 60


def _plural(n, word="frame"):
    return "%d %s%s" % (n, word, "" if n == 1 else "s")


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
        if self.kind not in KINDS:
            raise ValueError("no such tech drill: " + self.kind)
        with open(os.path.join(ROOT, "data", "framedata",
                               character + ".json")) as f:
            data = json.load(f)
        self.fast_fall = float(data["attributes"]["fast_fall_velocity"])
        # landing state -> (lag, lag when L-cancelled)
        self.lags = {
            LAND_AIR[0] + i: (data["moves"][name]["landing_lag"],
                              data["moves"][name]["landing_lag_lcancel"])
            for i, name in enumerate(AERIALS)}
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
        """The pad the game uses in the next frame (after the input
        delay)."""
        if self.live:
            return dict(self.n.pads(game=True)[self.person])
        return dict(self.n.h.pads[self.person])

    def _keep_on_stage(self, f):
        """Nothing: the player goes where they like, and one who falls off
        comes back as the game brings anyone back. (This once put a fighter
        standing more than 50 units out back at the start: the owner saw
        the player jump to the left of the screen after a long wavedash.)"""

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
                if self._starts(f):
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

    def _starts(self, f):
        """Is this the first frame of an attempt?"""
        if self.kind == "l_cancel":
            return f.airborne and AERIAL[0] <= f.state <= AERIAL[1]
        return f.state == SQUAT

    # ---- the judges (frame numbers here start at 1 with the attempt) ---------------

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
        if short:
            head = "Short hop"
        elif held == 0:
            head = "Full hop with the stick"
        else:
            head = "Jump held %s too long" % _plural(held - window)
        if held == 0:
            fix = ("Jump with X or Y and tap it. With the stick, let go of "
                   "up before you leave the ground.")
        else:
            fix = ("Let go of X or Y within %s of pressing it: your jump "
                   "squat is %s, and a jump still held on its last frame is "
                   "a full hop." % (_plural(window), _plural(squat)))
        return dict(
            success=short, words=words, headline=head, fix=fix,
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
        if pressed is None:
            head = "No air dodge"
            fix = ("Press L or R on frame %d, your first frame in the air, "
                   "with the stick down and to the side." % perfect)
        elif late < 0:
            head = "Air dodge %s early" % _plural(-late)
            fix = ("Wait for the air: press L or R on frame %d, not %d. In "
                   "jump squat it does nothing." % (perfect, pressed))
        elif not landed:
            head = "The air dodge missed the ground"
            fix = ("Hold the stick down and to the side as you press L or "
                   "R: the air dodge has to go into the ground.")
        elif in_time:
            head = words
            fix = "Press L or R on frame %d." % perfect
        else:
            head = "Air dodge %s late" % _plural(late)
            fix = ("Press L or R %s earlier, on frame %d: each frame later "
                   "is a frame more in the air." % (_plural(late), perfect))
        return dict(
            success=bool(in_time), words=words, headline=head, fix=fix,
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

    # ---- landing lag --------------------------------------------------------------

    def _landed(self, states):
        """The frame the fighter landed in an aerial's landing lag."""
        return next((i + 1 for i, f in enumerate(states)
                     if LAND_AIR[0] <= f.state <= LAND_AIR[1]), None)

    def _cancelled(self, states, land):
        """Was the lag halved? None while it is too soon to tell.
        Also the frames of lag so far and the lag it would be in full."""
        full, half = self.lags[states[land - 1].state]
        lag = sum(1 for f in states[land - 1:]
                  if LAND_AIR[0] <= f.state <= LAND_AIR[1])
        if LAND_AIR[0] <= states[-1].state <= LAND_AIR[1]:
            return (False if lag > half else None), lag, full
        return lag <= half, lag, full

    def _cancel_press(self, pads, before, land):
        """How many frames before landing L, R or Z was last pressed, the
        landing frame counting as 1 (0 or less: after it; None: never)."""
        presses, down = [], _cancel_down(before) if before else False
        for i, pad in enumerate(pads):
            now = _cancel_down(pad)
            if now and not down:
                presses.append(i + 1)
            down = now
        early = [p for p in presses if p <= land]
        if early:
            return land - early[-1] + 1
        return land - presses[0] + 1 if presses else None

    def _cancel_words(self, ago):
        if ago is None:
            return "No L, R or Z before landing"
        if ago <= 0:
            return "L pressed %s after landing: too late" % _plural(1 - ago)
        if ago > 7:
            return "L pressed %d frames before landing: the window is 7" % ago
        return "L pressed %s before landing" % _plural(ago)

    def _cancel_coach(self, ago):
        """The coach's headline and how to fix it, for an L-cancel."""
        if ago is None:
            return ("No L-cancel", "Press L, R or Z in the 7 frames before "
                    "you land: the frame you land counts.")
        if ago <= 0:
            return ("L %s late" % _plural(1 - ago),
                    "Press L, R or Z %s earlier: at the latest on the frame "
                    "you land." % _plural(1 - ago))
        if ago > 7:
            return ("L %s early" % _plural(ago - 7),
                    "Press L, R or Z %s later: within 7 frames of landing, "
                    "not %d." % (_plural(ago - 7), ago))
        return ("L-cancel", "Press L, R or Z within 7 frames of landing.")

    def _cancel_row(self, ago):
        """The ten frames up to the landing, as a timeline row."""
        return dict(
            frames=10, labels=[str(i) for i in range(10, 0, -1)],
            rows=[dict(label="L R Z",
                       you=[11 - ago] if ago and 1 <= ago <= 10 else [],
                       perfect=[], window=[4, 10])])

    def _judge_l_cancel(self, pads, before, states):
        f = states[-1]
        land = self._landed(states)
        if land is None:
            if f.airborne:
                return None
            return dict(skip=True, success=False, checks=[], timeline=None,
                        words="Nothing to cancel: the aerial was over "
                              "before landing")
        done, lag, full = self._cancelled(states, land)
        if done is None:
            return None
        ago = self._cancel_press(pads, before, land)
        words = self._cancel_words(ago)
        if done:
            words = "L-cancel. " + words
        tl = self._cancel_row(ago)
        tl["note"] = ("Frames before landing; 1 is the frame of landing. "
                      "Lag: %d frames, %d in full." % (lag, full))
        tl["at"] = land - 9         # the attempt frame of its first column
        tl["label_word"] = "to land"  # what its column labels count
        head, fix = self._cancel_coach(ago)
        if done:
            head = "L-cancel"
        return dict(
            success=done, words=words, timeline=tl, landed=land,
            headline=head, fix=fix,
            checks=[dict(expect="Landing lag halved", passed=done,
                         detail="%d of %d frames" % (lag, full)),
                    dict(expect="L, R or Z within 7 frames of landing",
                         passed=bool(ago and 1 <= ago <= 7), detail=words)])

    def _judge_shffl(self, pads, before, states):
        f = states[-1]
        if f.state == SQUAT:
            return None
        air = [g for g in states if g.airborne]
        if not air:
            return self._none("The jump did not come out")
        land = self._landed(states)
        if land is None and f.airborne:
            return None
        squat = self._squat_frames(states)
        short = abs(air[0].vel[1] - self.hop) < abs(air[0].vel[1] - self.full)
        held = 0
        for pad in pads:
            if not pad["buttons"] & JUMP:
                break
            held += 1
        aerial = next((i + 1 for i, g in enumerate(states)
                       if AERIAL[0] <= g.state <= AERIAL[1]), None)
        fell = next((i + 1 for i, g in enumerate(states) if g.airborne and
                     g.vel[1] <= -(self.fast_fall - 0.02)), None)
        ago = None
        if land is None:
            done = False
            lag_words = "Nothing to cancel: the aerial was over before " \
                "landing" if aerial else "No aerial"
        else:
            done, lag, full = self._cancelled(states, land)
            if done is None:
                return None
            ago = self._cancel_press(pads, before, land)
            lag_words = self._cancel_words(ago)
        if not short:
            words = "Full hop: let go of jump within %d" % (squat - 1)
            head = "Full hop"
            fix = ("Let go of X or Y within %s of pressing it: your jump "
                   "squat is %s." % (_plural(squat - 1), _plural(squat)))
        elif aerial is None:
            words = "No aerial"
            head = words
            fix = "Press A, or the C-stick, once you are in the air."
        elif fell is None:
            words = "No fast fall: tap down at the top of the hop"
            head = "No fast fall"
            fix = ("Tap the stick down once the hop starts to fall, at its "
                   "top.")
        elif not done:
            words = "No L-cancel. " + lag_words if land else lag_words
            head, fix = self._cancel_coach(ago)
        else:
            words = "SHFFL. " + lag_words
            head, fix = "SHFFL", "Keep it up."
        end = land if land else len(states)
        rows = [dict(label="Jump", you=list(range(1, min(held, end) + 1)),
                     perfect=[], window=[1, squat - 1]),
                dict(label="Attack", you=[aerial] if aerial else [],
                     perfect=[], window=None),
                dict(label="Down", you=[fell] if fell else [], perfect=[],
                     window=None),
                dict(label="L R Z",
                     you=[land - ago + 1] if land and ago and
                     1 <= land - ago + 1 <= end else [],
                     perfect=[], window=[land - 6, land] if land else None)]
        return dict(
            success=bool(short and aerial and fell and done), words=words,
            landed=land, headline=head, fix=fix,
            checks=[dict(expect="Short hop", passed=short, detail=""),
                    dict(expect="Aerial", passed=aerial is not None,
                         detail=""),
                    dict(expect="Fast fall", passed=fell is not None,
                         detail=""),
                    dict(expect="L-cancel", passed=bool(done),
                         detail=lag_words)],
            timeline=dict(frames=end, rows=rows,
                          note="Lands on frame %d." % land if land else ""))

    # ---- the coach's target: the try with what was wrong put right ---------------

    def corrected(self, result, pads):
        """For the coach: fn(t, fighter, pad) -> the pad to play instead.
        `t` is the attempt frame the pad makes (1: the first of the attempt,
        0 or less: before it), `fighter` the player's fighter before it,
        `pad` what the player pressed (None after the try: nothing). The
        player's own inputs, with what this result says was wrong put
        right: the jump let go in time, the air dodge on the first frame in
        the air, L pressed three frames before landing, a fast fall at the
        top. `pads` are the try's pads from its first attempt frame on (for
        the way the player was holding the stick)."""
        squat = self.squat
        kind = self.kind
        land = result.get("landed")
        side = next((1 if p["lx"] > 0 else -1 for p in pads
                     if p is not None and abs(p["lx"]) > 20), 0)
        st = dict(holding=True, fell=False, cancel=None, ground=None)

        def released(pad):
            return not pad["buttons"] & JUMP and pad["ly"] <= 44

        def no_cancel(pad):
            pad["buttons"] &= ~(SHOULDER | Z)
            pad["lt"] = pad["rt"] = 0

        def fix(t, f, pad):
            pad = dict(pad) if pad is not None else dict(
                buttons=0, lx=0, ly=0, cx=0, cy=0, lt=0, rt=0)
            if t < 1:
                if f is not None and not f.airborne:
                    st["ground"] = f.pos[1]
                return pad
            # the jump: let go before jump squat ends
            if kind in ("short_hop", "shffl") and st["holding"]:
                if released(pad):
                    st["holding"] = False
                elif t >= squat:
                    pad["buttons"] &= ~JUMP
                    pad["ly"] = min(pad["ly"], 0)
            if kind == "wavedash" and t <= squat + 14:
                no_cancel(pad)
                if t in (squat + 1, squat + 2):
                    pad["buttons"] |= 0x40
                    pad["lt"] = 255
                    if pad["ly"] > -40:
                        pad["lx"], pad["ly"] = 56 * side, -56 if side \
                            else -80
            if kind == "l_cancel" and land is not None and t <= land + 4:
                no_cancel(pad)
                if t in (land - 2, land - 1):
                    pad["buttons"] |= 0x40
            if kind == "shffl" and f is not None:
                if not result.get("aerial") and t == squat + 2:
                    pad["buttons"] |= 0x100           # a neutral air
                    pad["lx"] = pad["ly"] = 0
                if f.airborne:
                    no_cancel(pad)
                    if not st["fell"] and f.vel[1] <= 0:
                        pad["ly"] = -80               # the fast fall
                        st["fell"] = True
                    ground = st["ground"] if st["ground"] is not None \
                        else 0.0
                    speed = max(-f.vel[1], self.fast_fall * 0.5)
                    if st["cancel"] is None and st["fell"] and \
                            (f.pos[1] - ground) / speed <= 3.0:
                        st["cancel"] = t
                    if st["cancel"] is not None and \
                            t - st["cancel"] < 2:
                        pad["buttons"] |= 0x40
            return pad
        return fix

    def _none(self, why):
        return dict(success=False, words=why, checks=[
            dict(expect=why, passed=False, detail="")], timeline=None)


def load(path):
    import json
    with open(path) as f:
        return json.load(f)
