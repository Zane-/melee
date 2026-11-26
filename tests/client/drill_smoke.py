"""Any drill of the drill format in the native client, opened from Fox's
course and played without a person or a desktop: keys on a virtual
display.

    python -u tests/client/drill_smoke.py DRILL [--tries N] [--keys K,K]
        [--hold K,K] [--come D] [--paced]

The drill is found in its part of the course and opened. On first open the
tutorial: every lesson the file has, then the first part's card. Then N
tries are let go by with nothing pressed (or with `--keys` tapped now and
then: X11 key names, "x" is A, "z" B, "c" jump, "s" L/R; `--hold`: keys
held through each try, "Down" with "z" tapped is a shine; `--come D`: the
stand-in first walks toward the opponent, Shift held for the light push,
until it is within D units, and holds and taps its keys from then: a drill
whose try arises from play), until each has been judged or not counted: what a drill's own test would look at closer, here
only that it comes up, runs, judges and leaves, with no warning from the
interface and nothing left running. What each try said is printed.
"""
import argparse
import json
import os
import random
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import client  # noqa: E402
import courses  # noqa: E402
import screens  # noqa: E402
import window  # noqa: E402
from pausekeys import Chooser  # noqa: E402

KEYS = ("c", "x", "z", "s", "d", "h", "f", "t", "g", "k", "Down", "Left",
        "Right", "Up", "Shift_L", "Return")

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""), flush=True)


class Player:
    """Answers the tutorial's cards and the coach's, and lets `tries`
    tries go by (tapping `keys` in turn every 20 frames, if any)."""

    BUDGET = 90000              # calls before the test is called stuck
    TRY_BUDGET = 2400           # frames a try may take

    def __init__(self, c, w, tries, keys=(), hold=(), come=0.0, shots=None,
                 frames=()):
        self.c, self.w, self.tries, self.keys = c, w, tries, list(keys)
        # pictures of the tutorial's cards: a directory, and the frames of
        # each example to stop on ("F1": frame 1)
        self.shots, self.frames = shots, ["F%d" % f for f in frames]
        self.want, self.steps, self.due = [], 0, None
        self.hold = list(hold)
        self.come, self.walking, self.there = come, None, False
        self.cards, self.coaches = [], []
        # the opponent each card's pictures were of, and the opponent of
        # the scenario the drill was on while the card was shown
        self.shown = []
        self.release = []
        self.calls = 0
        self.since, self.here = 0, None
        self.try_at = -1
        self.n = 0
        self.leaving = None
        self.skipped = []
        self.started = False

    def tap(self, game, key, frames=2):
        game.key(key)
        self.release.append([key, frames])

    def __call__(self, game, frame):
        self.calls += 1
        if self.calls > self.BUDGET:
            raise RuntimeError("stuck after %d frames (frame %s, try %d)" % (
                self.calls, frame, self.try_at))
        if not self.started:
            self.started = True
            game.key("x", False)                # the A that started it
            return
        if self.release:
            for r in self.release:
                r[1] -= 1
                if r[1] <= 0:
                    game.key(r[0], False)
            self.release = [r for r in self.release if r[1] > 0]
        c = self.c
        if self.leaving is not None:
            self.leaving(game)
            return
        here = (frame, id(c.tutorial_now) if frame == -6 else
                id(c.coach_now) if frame == -4 else None)
        self.since = self.since + 1 if here == self.here else 0
        self.here = here
        if frame in (-6, -4) and self.since < 3:
            return
        if frame == -6:
            v = c.tutorial_now
            if not self.cards or (self.cards[-1]["title"],
                                  self.cards[-1]["sub"]) != (v["title"],
                                                             v["sub"]):
                self.cards.append(v)
                # (what the session loaded for the card's recording)
                op = c.session.d.scenario().get("opponent", "none") \
                    if c.session else None
                self.shown.append((
                    c.session.cpu_char if c.session else None,
                    op["character"] if isinstance(op, dict) else None))
                self.want = list(self.frames) if self.shots and \
                    v.get("pic") else []
                self.steps = 0
            if self.want:
                # its example stepped a frame at a time (the D-pad, which
                # pauses it), a picture on each frame asked for
                play = c.tutorial_play
                seq = play.panels[0]["seq"] if play.panels else []
                at = seq[play.k]["label"] if 0 <= play.k < len(seq) else ""
                if self.due is not None:
                    # (the frame stepped to is on the screen a call later)
                    game.shot(os.path.join(self.shots, "card%d-%s.png" % (
                        len(self.cards), self.due)))
                    self.want.remove(self.due)
                    self.due = None
                elif play.paused and at in self.want:
                    self.due = at
                    return
                self.steps += 1
                if self.want and self.steps < 480:
                    if self.steps % 4 == 1:
                        self.tap(game, "h")     # D-pad right: a frame on
                    return
                self.want = []
            self.tap(game, "x")                 # A: next, or start
            return
        if frame == -4:
            v = c.coach_now
            if not self.coaches or self.coaches[-1] is not v:
                self.coaches.append(v)
            self.tap(game, "x")                 # A: on with the drill
            return
        if frame < 0:
            if frame == -1:
                for key in KEYS:
                    game.key(key, False)
            return
        done = len(c.results_now()) + len(self.skipped)
        if done >= self.tries:
            for key in KEYS:
                game.key(key, False)
            self.leaving = self.leaving or Chooser(c, "list")
            self.leaving(game)
            return
        if self.try_at != done:
            self.try_at, self.n = done, 0
            self.there = False
            return
        self.n += 1
        if self.n > self.TRY_BUDGET:
            raise RuntimeError("try %d stuck after %d frames" % (
                done + 1, self.n))
        if self.come and not self.there:
            # walk up to the opponent first, wherever it has moved to
            me, op = game.fighter(0), game.fighter(1)
            gap = op.pos[0] - me.pos[0]
            if abs(gap) > self.come:
                side = "Right" if gap > 0 else "Left"
                if side != self.walking:
                    for key in self.hold + [self.walking]:
                        if key is not None:
                            game.key(key, False)
                    game.key("Shift_L")
                    game.key(side)
                    self.walking = side
                return
            if self.walking is not None:
                game.key(self.walking, False)
                game.key("Shift_L", False)
                self.walking = None
            self.there = True
            for key in self.hold:
                game.key(key)
            return
        if self.n == 2 and not self.come:
            for key in self.hold:
                game.key(key)
        if self.keys and self.n % 20 == 10:
            self.tap(game, self.keys[(self.n // 20) % len(self.keys)], 3)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("drill")
    ap.add_argument("--tries", type=int, default=3)
    ap.add_argument("--keys", default="",
                    help="keys tapped in turn during a try, comma separated")
    ap.add_argument("--hold", default="",
                    help="keys held through each try, comma separated")
    ap.add_argument("--come", type=float, default=0.0,
                    help="walk to within this many units of the opponent "
                         "before the keys of --hold and --keys, each try")
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--shots", help="a directory for pictures of the "
                                    "tutorial's cards (not the repository)")
    ap.add_argument("--frames", default="1,2",
                    help="with --shots: the frames of each card's example "
                         "to take a picture of")
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--paced", action="store_true",
                    help="at the console's speed, as a person plays it: an "
                         "opponent's thinking is then done in copies of "
                         "the game, beside it")
    args = ap.parse_args()
    random.seed(args.seed)
    spec = json.load(open(os.path.join(ROOT, "data", "drills",
                                       args.drill + ".json")))
    lessons = len(spec["tutorial"].get("lessons", []))
    save = os.path.join(tempfile.mkdtemp(prefix="melee-client-"),
                        "client.json")
    w = c = None

    def frames(n):
        for _ in range(n):
            c.frame()

    def tap(key, after=6):
        w.key(key)
        frames(2)
        w.key(key, False)
        frames(after)

    try:
        w = window.Window(window=(1280, 720), gpu=args.gpu)
        w.step(30)
        c = client.Client(w, source="keyboard", save=save,
                          out=tempfile.mkdtemp(prefix="melee-ui-"))
        c.settings["coach"] = 0
        c.settings["delay"] = 0
        w.delay(0)
        w.pace(args.paced)
        frames(6)
        tap("x")
        tap("x")
        frames(6)
        for _ in range(4):
            if c.screen == "hub" and args.drill in [
                    d["id"] for d in c.course["parts"][
                        courses.PARTS[int(c.hub_at[1:])]]]:
                break
            tap("Right")
        part = courses.PARTS[int(c.hub_at[1:])] if c.screen == "hub" \
            else None
        tap("x")
        if c.screen == "cats":
            # (Tech skill: its categories first; the one the drill is in)
            for _ in range(len(c.cats())):
                if args.drill in [d["id"] for d in screens.in_category(
                        c.course, part, c.cats()[c.cat_at])]:
                    break
                tap("Down")
            tap("x")
        for _ in range(40):
            if c.drills()[c.row[c.part]]["id"] == args.drill:
                break
            tap("Down")
        check("%s opens from Fox's course, %s" % (args.drill, part),
              c.drills()[c.row[c.part]]["id"] == args.drill,
              str(c.screen))

        if args.shots:
            os.makedirs(args.shots, exist_ok=True)
        p = Player(c, w, args.tries, [k for k in args.keys.split(",") if k],
                   [k for k in args.hold.split(",") if k], args.come,
                   args.shots, [int(f) for f in args.frames.split(",") if f])
        told = []
        show, say = c.show_result, c.banner_say

        def counted(result, results):
            told.append(dict(result))
            print("   try %d: %s (%s)" % (len(told), result["words"],
                                          result.get("scenario")),
                  file=sys.stderr, flush=True)
            show(result, results)

        def banner(word, text):
            if word == "Not counted":
                p.skipped.append(text)
                print("   not counted: %s" % text, file=sys.stderr,
                      flush=True)
            say(word, text)
        c.show_result, c.banner_say = counted, banner
        c.person = p
        w.key("x")
        for _ in range(150000):
            if c.screen != "drill" and p.leaving is not None:
                break
            c.frame()
        for key in KEYS:
            w.key(key, False)
        c.person, c.show_result, c.banner_say = None, show, say
        frames(6)

        subs = [x.get("sub", "") for x in p.cards]
        check("first open: its %d lessons, then the first part's card" %
              lessons,
              sum(s.startswith("LESSON") for s in subs) == lessons and
              any(s.startswith("PART 1 OF") for s in subs),
              "; ".join(s.replace("\n", " ") for s in subs))
        # a card's pictures are of the scenario its words are about: a
        # lesson's own, a part card's the one the drill is on (the
        # session's deck used to draw the opponent: "Sheik's down tilt"
        # played by Falco)
        got = [pair for pair, v in zip(p.shown, p.cards)
               if v.get("pic") or v.get("timeline")]
        check("each card's pictures are of its own scenario's opponent",
              all(a == b for a, b in got),
              "; ".join("%s%s" % (a, "" if a == b else ", wanted %s" % b)
                        for a, b in got) if got else "no pictures")
        check("%d tries, each judged or not counted" % args.tries,
              len(told) + len(p.skipped) >= args.tries,
              "%d judged, %d not counted" % (len(told), len(p.skipped)))
        think = getattr(c.session, "thinker", None) if c.session else None
        errors = list(getattr(think, "errors", []) or [])
        check("nothing wrong in an opponent's thinking", not errors,
              errors[0].strip().splitlines()[-1] if errors else "")
        check("back on the drill list", c.screen == "list", str(c.screen))
        bad = [line.strip()[:160] for line in w.log
               if "aurora" in line and ("warn" in line or "error" in line)]
        check("the interface raised no warnings", not bad,
              "; ".join(bad[:3]))
    finally:
        if w is not None:
            w.close()
        left = window.leftovers()
        check("nothing left running", not left, str(left))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
