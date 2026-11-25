"""Any drill of the drill format in the native client, opened from Fox's
course and played without a person or a desktop: keys on a virtual
display.

    python -u tests/client/drill_smoke.py DRILL [--tries N] [--keys K,K]
        [--hold K,K]

The drill is found in its part of the course and opened. On first open the
tutorial: every lesson the file has, then the first part's card. Then N
tries are let go by with nothing pressed (or with `--keys` tapped now and
then: X11 key names, "x" is A, "z" B, "c" jump, "s" L/R; `--hold`: keys
held through each try, "Down" with "z" tapped is a shine), until each has been
judged or not counted: what a drill's own test would look at closer, here
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

    def __init__(self, c, w, tries, keys=(), hold=()):
        self.c, self.w, self.tries, self.keys = c, w, tries, list(keys)
        self.hold = list(hold)
        self.cards, self.coaches = [], []
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
            return
        self.n += 1
        if self.n > self.TRY_BUDGET:
            raise RuntimeError("try %d stuck after %d frames" % (
                done + 1, self.n))
        if self.n == 2:
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
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--gpu", action="store_true")
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
        w.pace(False)
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
            # (Tech skill: its categories first)
            for _ in range(4):
                if args.drill in [d["id"] for d in c.drills()]:
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

        p = Player(c, w, args.tries, [k for k in args.keys.split(",") if k],
                   [k for k in args.hold.split(",") if k])
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
