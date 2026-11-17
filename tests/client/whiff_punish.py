"""Fox's whiff punish in the native client (data/drills/fox-whiff-punish.json)
and the reset after a judged try, checked without a person or a desktop:
keys pressed on a virtual display.

    python -u tests/client/whiff_punish.py [--shots DIR]

The drill opens from Fox's course (Neutral). On first open the tutorial: its
lesson, then the parts' cards; R turns to the second part (the punish). A
stand-in plays as the example does: it walks in (the keyboard's light push);
with the attack's first frame (the walk was within the opponent's trigger
distance, which it sees 15 frames late) it dashes back, and on the
scenario's frame GO of the attack dashes in again and jump-cancels a grab
once within 22 units. Every try is its own exchange (the session numbers
its tries, and each draws its own opponent's choices). Tries:

1. the punish: a success; after the verdict it pummels and throws, and the
   reset waits until 3 seconds after that damage (Reset: After damage
   stops, the default);
2. the dash in only once the opponent can act again: "Too late"; with no
   damage after it, the reset comes 3 seconds after the verdict;
3. a dash in, let go, standing next to the opponent: caught, a failure
   saying so, and the coach's card after this second miss (Settings: 2);
4. the punish (a dash attack, which lands at any spacing) with Reset on
   When judged: the reset at once (the client's 45 frames to read the
   verdict).

The pause menu's Reset and Quiet time say what Settings says. Input delay
0 (the stand-in's keys are the frames it means).
"""
import argparse
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
from melee_drills import format as F  # noqa: E402
from melee_engine.sense import FREE  # noqa: E402
from pausekeys import Chooser  # noqa: E402

DRILL = "fox-whiff-punish"
KEYS = ("c", "x", "z", "s", "d", "h", "f", "t", "g", "Down", "Left",
        "Right", "Shift_L", "Return")
DASH = 20
QUIET = 180                  # 3 seconds
SEEN = 16                    # frames: its 15 of reaction, and its start seen
GRAB_FROM = 22               # units: the jump of the stand-in's grab
HIT_FROM = 26                # units: its dash attack


def near(c):
    """The scenario's trigger distance: its script's first step's."""
    until = c.session.d.scenario()["opponent"]["script"][0]["until"]
    return next(x["distance"][1] for x in until["all"]
                if isinstance(x, dict) and "distance" in x)
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""), flush=True)


class Player:
    """The person: answers the tutorial's cards and the coach's, and plays
    `tries`, one each: "punish", "stand", "late", "judged" (the punish with
    Reset on When judged). Between a verdict and the next try's first frame
    (frame -1) it counts the frames and the damage, and after the first
    punish pummels and throws."""

    BUDGET = 30000              # calls before the test is called stuck
    TRY_BUDGET = 1500           # frames a try may take

    def __init__(self, c, tries, shots=None):
        self.c, self.tries, self.shots = c, list(tries), shots
        self.cards, self.coaches = [], []
        self.release = []
        self.saw = {}
        self.calls = 0
        self.since, self.here = 0, None
        self.try_at = 0
        self.t = None
        self.leaving = None
        self.skipped = []
        self.told = 0                 # verdicts seen
        self.gaps = []                # per verdict: (frames to reset,
        self.gap = None               # the last damage's frame), as counted
        self.pause_rows = None

    def tap(self, game, key, frames=2):
        game.key(key)
        self.release.append([key, frames])

    def shot(self, game, name):
        if self.shots and name not in self.saw:
            self.saw[name] = True
            game.shot(os.path.join(self.shots, name + ".png"))

    def verdict(self):
        """A try was judged (Client.show_result): the count to its reset
        starts."""
        self.told += 1
        if self.gap is not None:
            self.gaps.append(tuple(self.gap[:2]))
        self.gap = [0, 0, None, self.tries[self.told - 1] if
                    self.told <= len(self.tries) else None]

    def __call__(self, game, frame):
        self.calls += 1
        if self.calls > self.BUDGET:
            raise RuntimeError("stuck after %d frames (frame %s, try %d)" % (
                self.calls, frame, self.try_at))
        if not getattr(self, "started", False):
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
            return self.card(game)
        if frame == -4:
            v = c.coach_now
            if not self.coaches or self.coaches[-1] is not v:
                self.coaches.append(v)
                self.shot(game, "coach")
            self.tap(game, "x")                 # A: on with the drill
            return
        if frame == -1:
            return self.between(game)
        if frame < 0:
            return
        if frame == 0 and self.gap is not None:
            self.gaps.append(tuple(self.gap[:2]))
            self.gap = None
        self.drill(game, frame)

    def card(self, game):
        v = self.c.tutorial_now
        if not self.cards or (self.cards[-1]["title"], self.cards[-1]["sub"]) \
                != (v["title"], v["sub"]):
            self.cards.append(v)
            self.shot(game, "card%d" % len(self.cards))
        sub = v["sub"]
        if sub.startswith("LESSON") or sub.startswith("PART 2"):
            self.tap(game, "x")                 # A: next, or start
        else:
            self.tap(game, "s")                 # R: the next part

    def between(self, game):
        """A frame after a verdict, before the reset: counted; after the
        first punish, a pummel and a throw."""
        g = self.gap
        if g is None:
            return
        g[0] += 1
        both = (game.fighter(0).percent, game.fighter(1).percent)
        if g[2] is not None and (both[0] > g[2][0] or both[1] > g[2][1]):
            g[1] = g[0]
        g[2] = both
        if g[0] == 2:
            for key in KEYS:
                game.key(key, False)        # the try's keys let go
        if g[3] == "punish" and self.told == 1:
            if g[0] in (4, 14):
                self.tap(game, "x")             # A: a pummel
            if g[0] == 26:
                self.tap(game, "Down", 3)       # a down throw

    def drill(self, game, frame):
        c = self.c
        done = len(c.results_now()) + len(self.skipped)
        if done >= len(self.tries):
            for key in KEYS:
                game.key(key, False)
            self.leaving = self.leaving or Chooser(c, "list")
            self.leaving(game)
            return
        if self.t is None or self.try_at != done:
            for key in KEYS:
                game.key(key, False)
            self.try_at = done
            kind = self.tries[done]
            if kind == "judged":
                c.settings["reset"] = "judged"
                c.reset_now()
            if self.pause_rows is None:
                self.pause_rows = [r for r in c.pause_rows("drill")
                                   if r[0] in ("rmode", "rquiet")]
            self.t = dict(kind=kind, step="walk", n=0, all=0)
            print("   try %d: %s" % (done + 1, kind), file=sys.stderr,
                  flush=True)
            return
        t = self.t
        t["n"] += 1
        t["all"] += 1
        if t["all"] > self.TRY_BUDGET:
            raise RuntimeError("try %d (%s) stuck at %s after %d frames" % (
                done + 1, t["kind"], t["step"], t["all"]))
        me, op = game.fighter(0), game.fighter(1)
        toward = "Right" if op.pos[0] > me.pos[0] else "Left"
        away = "Left" if toward == "Right" else "Right"
        gap = abs(op.pos[0] - me.pos[0])
        go = int(c.session.d.scenario().get("numbers", {}).get("GO", 9))
        if t["step"] == "walk":
            if t["n"] < 30:
                return                          # (the opponent's footsies)
            if t["kind"] == "stand":
                # a dash in, let go: it carries Fox up to the opponent,
                # where it stands (the drill's mistake)
                game.key(toward)
                t.update(step="stand", n=0, toward=toward)
                return
            hist = t.setdefault("gaps", [])
            hist.append(gap)
            # the opponent attacks when it sees the walk within its
            # trigger distance, 15 frames late: the dash back goes with
            # its attack's first frame, as the example's (frame 1)
            if t["kind"] != "stand" and (
                    op.state in F.THEIR_ATTACKS or
                    (len(hist) > SEEN and hist[-SEEN - 1] <= near(c))):
                game.key("Shift_L", False)
                game.key(toward, False)
                game.key(away)                  # a dash back
                t.update(step="back", n=1, away=away, toward=toward,
                         att=0 if op.state in F.THEIR_ATTACKS else None)
                return
            game.key("Shift_L")                 # a walk in
            game.key(toward)
        elif t["step"] == "stand":
            if t["n"] >= 6:
                game.key(t["toward"], False)
        elif t["step"] == "back":
            if t["n"] > 6:
                game.key(t["away"], False)
            if t["att"] is None and op.state in F.THEIR_ATTACKS:
                t["att"] = 0
                if os.environ.get("TRACE"):
                    print("   attack %d at gap %.1f, GO %d, %d frames "
                          "after the dash back" % (op.state, gap, go,
                                                   t["n"]),
                          file=sys.stderr, flush=True)
            if t["att"] is None:
                if t["n"] > 60:
                    raise RuntimeError("no attack after the dash back")
                return
            t["att"] += 1                       # its frame, as seen
            if t["kind"] == "late" and op.state in FREE:
                game.key(t["toward"])           # a dash in, too late
                t.update(step="in", n=0)
            elif t["kind"] != "late" and t["att"] + 1 >= go:
                game.key(t["toward"])           # a dash in
                t.update(step="in", n=0)
        elif t["step"] == "in":
            if t["kind"] == "judged":
                # a dash attack: out for 14 frames as Fox slides through,
                # it lands whatever the spacing. (Every try is its own
                # exchange now, not the first one again; the grab from a
                # fixed distance goes past a Marth leaning into a forward
                # smash from 5 units as from 1)
                if gap <= HIT_FROM and "jumped" not in t:
                    game.key("x")               # A, running
                    t["jumped"] = t["n"]
                elif "jumped" in t and t["n"] == t["jumped"] + 2:
                    game.key("x", False)
            elif gap <= GRAB_FROM and "jumped" not in t:
                game.key("c")                   # Y: the jump
                t["jumped"] = t["n"]
                if os.environ.get("TRACE"):
                    print("   jump at in+%d, gap %.1f, opponent %d" % (
                        t["n"], gap, op.state), file=sys.stderr, flush=True)
            elif "jumped" in t and t["n"] == t["jumped"] + 1:
                game.key("d")                   # Z: the grab in the squat
            elif "jumped" in t and t["n"] == t["jumped"] + 3:
                game.key("c", False)
                game.key("d", False)
            if os.environ.get("TRACE") and "jumped" in t and \
                    t["n"] <= t["jumped"] + 30:
                a, b = game.state()["p"][:2]
                print("      in+%d: Fox %d, opponent %d, gap %.1f; %s" % (
                    t["n"], me.state, op.state, gap, "; ".join(
                        " ".join("%s %s" % (k, p.get(k)) for k in (
                            "x", "y", "facing", "invuln", "air"))
                        for p in (a, b))), file=sys.stderr, flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    ap.add_argument("--seed", type=int, default=5,
                    help="the client's random numbers (the opponents drawn)")
    args = ap.parse_args()
    random.seed(args.seed)
    if args.shots:
        os.makedirs(args.shots, exist_ok=True)
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
        w = window.Window(window=(1280, 720))
        w.step(30)
        c = client.Client(w, source="keyboard", save=save,
                          out=tempfile.mkdtemp(prefix="melee-ui-"))
        c.settings["coach"] = 2
        c.settings["delay"] = 0
        w.delay(0)
        w.pace(False)
        frames(6)
        tap("x")
        tap("x")
        frames(6)
        for _ in range(4):
            if c.screen == "hub" and DRILL in [
                    d["id"] for d in c.course["parts"][
                        courses.PARTS[int(c.hub_at[1:])]]]:
                break
            tap("Right")
        part = courses.PARTS[int(c.hub_at[1:])] if c.screen == "hub" \
            else None
        tap("x")
        for _ in range(20):
            if c.drills()[c.row[c.part]]["id"] == DRILL:
                break
            tap("Down")
        check("the drill opens from Fox's course, Neutral",
              part == "Neutral" and
              c.drills()[c.row[c.part]]["id"] == DRILL, str(part))

        tries = ["punish", "late", "stand", "judged"]
        p = Player(c, tries, args.shots)
        told = []
        show, say = c.show_result, c.banner_say

        def counted(result, results):
            told.append(dict(result))
            p.verdict()
            print("   result: %s (%s, %s)" % (
                result["words"], result.get("scenario"),
                "plays on" if result.get("settles") else "resets"),
                file=sys.stderr, flush=True)
            show(result, results)

        def banner(word, text):
            if word == "Not counted":
                p.skipped.append(text)
            say(word, text)
        c.show_result, c.banner_say = counted, banner
        c.person = p
        w.key("x")
        for _ in range(80000):
            if c.screen != "drill" and p.leaving is not None:
                break
            c.frame()
        for key in KEYS:
            w.key(key, False)
        c.person, c.show_result, c.banner_say = None, show, say
        frames(6)

        subs = [x.get("sub", "") for x in p.cards]
        check("first open: the lesson, then the parts' cards; R turns to "
              "the punish", any(s.startswith("LESSON") for s in subs) and
              any(s.startswith("PART 2 OF 2") for s in subs),
              "; ".join(s.replace("\n", " ") for s in subs))
        words = [r["words"] for r in told]
        gaps = p.gaps
        print("   between verdict and reset (frames, last damage): %s" %
              gaps, file=sys.stderr, flush=True)
        check("the punish: dash back as it swings, dash in and grab: a "
              "success", len(told) >= 1 and told[0]["success"] and
              told[0].get("part") == "Punish the whiff",
              words[0] if words else "")
        g = gaps[0] if gaps else (0, 0)
        check("after it a pummel and a throw: the reset waits 3 seconds "
              "from that damage", g[1] > 0 and
              QUIET - 2 <= g[0] - g[1] <= QUIET + 6, str(g))
        check("the dash in once it can act again: judged late",
              len(told) >= 2 and not told[1]["success"] and
              words[1].startswith("Too late:"), words[1] if len(words) > 1
              else "")
        g = gaps[1] if len(gaps) > 1 else (0, 0)
        check("no damage after the verdict: the reset 3 seconds later",
              g[1] == 0 and QUIET - 2 <= g[0] <= QUIET + 6, str(g))
        check("dashing in and standing next to it: caught, a failure saying "
              "so", len(told) >= 3 and not told[2]["success"] and
              words[2].startswith("Caught:"), words[2] if len(words) > 2
              else "")
        co = p.coaches[0] if p.coaches else {}
        check("after two misses the coach's card: what was wrong and the "
              "fix", co.get("headline") == "Caught" and
              bool(co.get("fix")) and co.get("you_pic") is not None,
              "%r / %r" % (co.get("headline"), co.get("fix", "")[:60]))
        g = gaps[3] if len(gaps) > 3 else (999, 0)
        check("Reset on When judged: the punish's reset at once",
              len(told) >= 4 and told[3]["success"] and g[0] <= 50,
              "%s; %s" % (words[3] if len(words) > 3 else "", g))
        rows = p.pause_rows or []
        check("the pause menu's Reset and Quiet time say what Settings "
              "says", [r[2] for r in rows] == ["After damage stops",
                                               "3 seconds"],
              str(rows))
        check("every try counted", not p.skipped, str(p.skipped))
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
