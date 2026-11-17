"""Fox's edgeguard in the native client (data/drills/fox-edgeguard.json),
checked without a person or a desktop: keys pressed on a virtual display.

    python -u tests/client/edgeguard.py [--shots DIR]

The drill opens from Fox's course (Punish). On first open the tutorial: its
lessons, then the first part's card. A stand-in plays:

1. part 1, the ledge taken (a jump, an air dodge down and back on the
   first frame in the air: the keyboard's diagonal): the opponent, back
   with its jump alone, falls past: a success;
2. part 2, standing still: the opponent that thinks does not stop at
   the ledge: it stands on the stage again, and only then is the try
   judged ("It got back");
3. part 2 again, at the console's pace (the opponent thinking in forked
   copies of the game, no frame waiting for it): its decisions come in
   time;
4. at that pace, down smashes at the edge whenever it comes near: hit or
   not, it goes on and the game with it (2026-11-17: a hit on it once
   took the client down), until its stock or the stage;
5. D-pad right: another opponent of the deck, swapped in.

The pause menu's CPU reaction says the drill's own 15 frames, and a change
of it is the next attempt's opponent's. Input delay 0.
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
from pausekeys import Chooser  # noqa: E402

DRILL = "fox-edgeguard"
KEYS = ("c", "x", "z", "s", "d", "h", "f", "t", "g", "k", "Down", "Left",
        "Right", "Up", "Shift_L", "Return")
SQUAT = 3                    # Fox's jump squat
GO = 24                      # the frame of a try the stand-in jumps on

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""), flush=True)


class Player:
    """The person: answers the tutorial's cards and the coach's, and plays
    `tries`, one each: "hog" (the ledge taken at once), "stand", "paced"
    (standing, the game at the console's pace), "turn" (D-pad right, then
    standing)."""

    BUDGET = 60000              # calls before the test is called stuck
    TRY_BUDGET = 2400           # frames a try may take

    def __init__(self, c, w, tries, shots=None):
        self.c, self.w, self.tries, self.shots = c, w, list(tries), shots
        self.cards, self.coaches = [], []
        self.release = []
        self.saw = {}
        self.calls = 0
        self.since, self.here = 0, None
        self.try_at = -1
        self.t = None
        self.leaving = None
        self.skipped = []
        self.starts = []              # each try's start, as drawn
        self.pilots = []              # each try's opponent, as it ended
        self.errors = []              # faults in its thinking, each try
        self.smashes = []
        self.names = []               # the scenario each try was played in
        self.reacts = []
        self.rows = None
        self.turned = None

    def tap(self, game, key, frames=2):
        game.key(key)
        self.release.append([key, frames])

    def shot(self, game, name):
        if self.shots and name not in self.saw:
            self.saw[name] = True
            game.shot(os.path.join(self.shots, name + ".png"))

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
            v = c.tutorial_now
            if not self.cards or (self.cards[-1]["title"],
                                  self.cards[-1]["sub"]) != (v["title"],
                                                             v["sub"]):
                self.cards.append(v)
                self.shot(game, "card%d" % len(self.cards))
            self.tap(game, "x")                 # A: next, or start
            return
        if frame == -4:
            v = c.coach_now
            if not self.coaches or self.coaches[-1] is not v:
                self.coaches.append(v)
                self.shot(game, "coach")
            self.tap(game, "x")                 # A: on with the drill
            return
        if frame < 0:
            if frame == -1:
                for key in KEYS:
                    game.key(key, False)
            return
        self.drill(game, frame)

    def opponent(self):
        d = self.c.session.d
        b = d.op_script.cur if d.op_script is not None else None
        return getattr(b, "pilot", None)

    def drill(self, game, frame):
        c = self.c
        done = len(c.results_now()) + len(self.skipped)
        if done >= len(self.tries):
            for key in KEYS:
                game.key(key, False)
            self.w.pace(False)
            self.leaving = self.leaving or Chooser(c, "list")
            self.leaving(game)
            return
        if self.t is None or self.try_at != done:
            for key in KEYS:
                game.key(key, False)
            self.try_at = done
            kind = self.tries[done]
            if self.rows is None:
                self.rows = [r for r in c.pause_rows("drill")
                             if r[0] == "react"]
            self.w.pace(kind in ("paced", "smash"))
            self.t = dict(kind=kind, n=0)
            self.names.append(c.session.d.scenario()["name"])
            d = c.session.d.launched or {}
            self.starts.append((d.get("name"), d.get("percent"),
                                d.get("side"), d.get("stand")))
            self.reacts.append(c.session.d.op_script.ctx.react
                               if c.session.d.op_script else None)
            print("   try %d: %s against %s (part %d)" % (
                done + 1, kind, self.names[-1],
                c.session.d.part_index + 1), file=sys.stderr, flush=True)
            return
        t = self.t
        t["n"] += 1
        if t["n"] > self.TRY_BUDGET:
            raise RuntimeError("try %d (%s) stuck after %d frames" % (
                done + 1, t["kind"], t["n"]))
        pilot = self.opponent()
        if pilot is not None:
            t["pilot"] = pilot
            t["errors"] = self.c.session.d.op_script.cur.errors
        me = game.fighter(0)
        out = "Right" if me.pos[0] > 0 else "Left"
        if os.environ.get("TRACE") and t["kind"] == "hog" and t["n"] < 45:
            print("   %2d fox state %d (%.1f, %.1f) facing %+d" % (
                t["n"], me.state, me.pos[0], me.pos[1], me.facing),
                file=sys.stderr, flush=True)
        if t["kind"] == "hog":
            # back to the ledge: a jump, and on the first frame in the air
            # an air dodge down and back
            # (once the jab of the A that started the drill is over)
            if t["n"] == GO:
                game.key("c")
            elif t["n"] == GO + SQUAT + 1:
                game.key("c", False)
                game.key("s")
                game.key("Down")
                game.key(out)
            elif t["n"] == GO + SQUAT + 4:
                for key in ("s", "Down", out):
                    game.key(key, False)
            if me.state in (252, 253) and "hung" not in t:
                t["hung"] = t["n"]
                print("   on the ledge after %d frames" % t["n"],
                      file=sys.stderr, flush=True)
        elif t["kind"] == "smash":
            # a down smash (the C-stick down) whenever it is near
            op = game.fighter(1)
            near = abs(op.pos[0] - me.pos[0]) < 28 and \
                abs(op.pos[1] - me.pos[1]) < 30
            if near and me.state in (14, 15, 16, 17, 18) and \
                    t["n"] > GO and not t.get("held"):
                game.key("k")
                t["held"] = 3
                t["smashes"] = t.get("smashes", 0) + 1
            elif t.get("held"):
                t["held"] -= 1
                if not t["held"]:
                    game.key("k", False)
        elif t["kind"] == "turn" and self.turned is None:
            if t["n"] == 6:
                self.turned = [c.session.d.scenario()["name"], None]
                self.tap(game, "h")             # D-pad right
        # ("stand", "paced": nothing)

    def verdict(self, result):
        """A try was judged."""
        t = self.t or {}
        self.pilots.append(t.get("pilot"))
        self.errors.append(t.get("errors", 0))
        self.smashes.append(t.get("smashes", 0))
        t["result"] = result


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    ap.add_argument("--seed", type=int, default=5,
                    help="the client's random numbers (the launches drawn)")
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
        c.settings["coach"] = 0
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
        check("the drill opens from Fox's course, Punish",
              part == "Punish" and
              c.drills()[c.row[c.part]]["id"] == DRILL, str(part))

        tries = ["hog", "stand", "paced", "smash", "turn"]
        p = Player(c, w, tries, args.shots)
        told = []
        show, say = c.show_result, c.banner_say

        def counted(result, results):
            told.append(dict(result))
            p.verdict(result)
            print("   result: %s (%s)" % (result["words"],
                                          result.get("scenario")),
                  file=sys.stderr, flush=True)
            if len(told) == 1:
                # on to the second part (a person passes the first three
                # times, or turns to it on the tutorial's card)
                c.session.d.set_part(1)
            if len(told) == 2:
                c.react_change(1)       # CPU reaction: one step faster
            show(result, results)

        def banner(word, text):
            if word == "Not counted":
                p.skipped.append(text)
            if p.turned is not None and p.turned[1] is None and \
                    word != "Not counted":
                p.turned[1] = text
            say(word, text)
        c.show_result, c.banner_say = counted, banner
        c.person = p
        w.key("x")
        for _ in range(120000):
            if c.screen != "drill" and p.leaving is not None:
                break
            c.frame()
        for key in KEYS:
            w.key(key, False)
        c.person, c.show_result, c.banner_say = None, show, say
        w.pace(False)
        frames(6)

        subs = [x.get("sub", "") for x in p.cards]
        check("first open: the lessons, then the first part's card",
              sum(s.startswith("LESSON") for s in subs) == 3 and
              any(s.startswith("PART 1 OF 2") for s in subs),
              "; ".join(s.replace("\n", " ") for s in subs))
        words = [r["words"] for r in told]
        check("part 1, the ledge taken: the opponent falls past, a success",
              len(told) >= 1 and told[0]["success"] and
              told[0].get("part") == "Take the ledge",
              words[0] if words else "")
        check("part 2, standing still: judged only once it stands on the "
              "stage again", len(told) >= 2 and not told[1]["success"] and
              told[1].get("part") == "Edgeguard" and
              words[1].startswith("It got back"),
              words[1] if len(words) > 1 else "")
        pl = p.pilots[1] if len(p.pilots) > 1 else None
        check("its way back was decided by the engine, to the stage",
              pl is not None and len(pl.decisions) >= 1 and
              pl.ended == "stage",
              "%s decisions, ended %s by %s" % (
                  len(pl.decisions) if pl else None,
                  pl.ended if pl else None,
                  " / ".join(pl.via) if pl else None))
        rows = p.rows or []
        check("the pause menu's CPU reaction: the drill's own 15 frames",
              [r[2] for r in rows] == ["15 frames"], str(rows))
        check("changed, the next attempt's opponent reacts in 12",
              len(p.reacts) >= 3 and p.reacts[1] == 15 and
              p.reacts[2] == 12, str(p.reacts))
        pl = p.pilots[2] if len(p.pilots) > 2 else None
        took = sorted(d.get("wall", 0.0) for d in pl.decisions) \
            if pl else []
        check("at the console's pace it thinks in forks: a route decided, "
              "in time, and it gets back",
              pl is not None and len(pl.decisions) >= 1 and
              pl.ended == "stage" and pl.late <= len(pl.decisions),
              "%d decisions, %d late, %s ms each, ended %s by %s" % (
                  len(pl.decisions) if pl else 0, pl.late if pl else 0,
                  ", ".join("%.0f" % x for x in took),
                  pl.ended if pl else None,
                  " / ".join(pl.via) if pl else None))
        pl = p.pilots[3] if len(p.pilots) > 3 else None
        check("down smashes at the edge, at the console's pace: the try "
              "goes on to its stock or the stage, nothing wrong in its "
              "thinking", len(told) >= 4 and pl is not None and
              pl.ended in ("stage", "lost") and
              not any(p.errors) and
              (told[3]["success"] or words[3].startswith("It got back")),
              "%s; %d down smashes, it took %s; ended %s; errors %s" % (
                  words[3] if len(words) > 3 else "",
                  p.smashes[3] if len(p.smashes) > 3 else 0,
                  [w for _, w in pl.log if w.startswith("hit")] if pl
                  else None, pl.ended if pl else None, p.errors))
        check("D-pad right: another opponent of the deck, and the try "
              "against it judged", p.turned is not None and
              p.turned[1] not in (None, p.turned[0]) and len(told) >= 5 and
              told[4].get("scenario") == p.turned[1],
              "%s; judged against %s" % (
                  p.turned, told[4].get("scenario") if len(told) > 4
                  else None))
        part2 = p.starts[1:]
        check("the edgeguard's tries start differently: the start, its "
              "damage, where the player stands",
              len({x[1] for x in part2}) >= 3 and
              len({x[3] for x in part2}) >= 3, str(part2))
        check("every try judged", len(told) >= len(tries) - 1,
              "%d of %d; skipped %s" % (len(told), len(tries), p.skipped))
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
