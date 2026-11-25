"""Escape the tech chase in the native client
(data/drills/fox-escape-techchase.json), checked without a person or a
desktop: keys pressed on a virtual display.

    python -u tests/client/techchase.py [--shots DIR]

The drill opens from Fox's course (Defense). On first open the tutorial:
its lessons, then the first part's card. A stand-in plays:

1. part 1, mashing jump from the reset, then L or R as Fox comes down: the
   pad is kept from the game until the grab has him (every try begins
   held), and the tech is a success;
2. part 2, at the console's pace (the opponent thinking in forked copies
   of the game): a tech away and a jump on the first free frame. It asks
   for its table of answers as its grab connects and holds the grab for
   it: its answers are there before the tech can be seen (the standing
   row first; with --gpu, the whole table 10 frames or more before
   that), with nothing wrong in its thinking; caught or not is the game's
   to say;
3. at that pace, no tech and nothing after it: a missed tech;
4. at that pace, a tech in place and nothing after it: the cover lands
   (unless it had read another option: a read loses to the others);
5. D-pad right: another opponent of the deck, swapped in.

The pause menu's CPU reaction says the drill's own 24 frames. Input delay
0.
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

DRILL = "fox-escape-techchase"
KEYS = ("c", "x", "z", "s", "d", "h", "f", "t", "g", "k", "Down", "Left",
        "Right", "Up", "Shift_L", "Return")
THROWN = (239, 240, 241, 242, 243)
TECH = (199, 200, 201)
PACED = ("away", "none", "inplace")

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""), flush=True)


class Player:
    """The person: answers the tutorial's cards and the coach's, and plays
    `tries`, one each: "mash" (jump mashed from the reset, then a tech in
    place), "away" (a tech away, a jump on the first free frame), "none"
    (nothing), "inplace" (a tech in place, nothing after), "turn" (D-pad
    right, then a tech away)."""

    BUDGET = 60000              # calls before the test is called stuck
    TRY_BUDGET = 1800           # frames a try may take

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
        self.names = []               # the scenario each try was played in
        self.reacts = []
        self.chases = []              # each try's tables, as they came
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

    def tables(self):
        """The opponent's chase now: its stages' tables as they came."""
        d = self.c.session.d
        b = d.op_script.cur if d.op_script is not None else None
        out = []
        for g in getattr(b, "stages", None) or []:
            tab = g["tab"]
            # (its frames as the game's: a throw it held its grab for
            # begins later than its table has it)
            shift = 0
            if tab and g["throw"] is not None and \
                    g["thrown_at"] is not None:
                shift = g["thrown_at"] - g["asked"] - tab["throw_at"]
            out.append(dict(
                back=g["back"], first=g["first"],
                kind=tab and tab["kind"], held=g["held"],
                thrown=g["thrown_at"] is not None and
                g["thrown_at"] - g["asked"],
                free=tab and tab["cpu_free"] + shift,
                see=tab and tab["see"] + shift,
                partial=tab and tab["partial"],
                searches=tab and tab["searches"],
                wall=tab and tab["wall"],
                stance=g["stance"] and g["stance"]["name"],
                option=g["option"], cover=g["cover"]))
        return out

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
            self.w.pace(kind in PACED)
            self.t = dict(kind=kind, n=0, thrown=None, was=None)
            sc = c.session.d.scenario()
            self.names.append(sc["name"])
            self.t["floor"] = int(sc["numbers"]["FLOOR"])
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
        got = self.tables()
        if got:
            t["tables"] = got
        me, op = game.fighter(0), game.fighter(1)
        kind = t["kind"]
        if kind == "mash" and t["thrown"] is None and t["n"] <= 14:
            # jump mashed from the reset: kept from the game until held
            game.key("c", t["n"] % 4 < 2)
            t["mashed"] = t.get("mashed", 0) + (t["n"] % 4 == 0)
        elif kind == "mash" and t["n"] == 15:
            game.key("c", False)
        if kind == "turn" and self.turned is None and t["n"] == 6:
            self.turned = [c.session.d.scenario()["name"], None]
            self.tap(game, "h")                 # D-pad right
            return
        if me.state in THROWN and t["thrown"] is None:
            t["thrown"] = t["n"]
            game.key("c", False)
        if t["thrown"] is not None and kind != "none":
            a = t["n"] - t["thrown"] + 1        # the attempt's frame
            away = "Right" if me.pos[0] > op.pos[0] else "Left"
            roll = kind in ("away", "turn")
            if a == t["floor"] - 5:
                game.key("s")                   # R: the tech
                if roll:
                    t["way"] = away
                    game.key(away)
            elif a == t["floor"] + 3:
                game.key("s", False)
                if roll:
                    game.key(t["way"], False)
            if roll and t["was"] in TECH and me.state not in TECH and \
                    "out" not in t:
                # the first free frame: a jump away
                t["out"] = t["n"]
                game.key("c")
                game.key(away)
                t["way"] = away
            elif "out" in t and t["n"] == t["out"] + 10:
                game.key("c", False)
                game.key(t["way"], False)
        t["was"] = me.state

    def verdict(self, result):
        """A try was judged."""
        t = self.t or {}
        self.chases.append(t.get("tables") or self.tables())
        t["result"] = result


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    ap.add_argument("--seed", type=int, default=5,
                    help="the client's random numbers")
    ap.add_argument("--gpu", action="store_true",
                    help="drawn by the graphics card (off screen), not in "
                    "software: the timings a person's game has")
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
            if c.screen == "hub" and DRILL in [
                    d["id"] for d in c.course["parts"][
                        courses.PARTS[int(c.hub_at[1:])]]]:
                break
            tap("Right")
        part = courses.PARTS[int(c.hub_at[1:])] if c.screen == "hub" \
            else None
        tap("x")
        for _ in range(30):
            if c.drills()[c.row[c.part]]["id"] == DRILL:
                break
            tap("Down")
        check("the drill opens from Fox's course, Defense",
              part == "Defense" and
              c.drills()[c.row[c.part]]["id"] == DRILL, str(part))

        tries = ["mash", "away", "none", "inplace", "turn"]
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
              any(s.startswith("PART 1 OF 3") for s in subs),
              "; ".join(s.replace("\n", " ") for s in subs))
        words = [r["words"] for r in told]
        check("part 1, jump mashed from the reset: the pad is kept from "
              "the game until the grab has Fox, and the tech is a success",
              len(told) >= 1 and told[0]["success"] and
              told[0].get("part") == "Tech" and not p.skipped,
              "%s; skipped %s" % (words[0] if words else "", p.skipped))
        rows = p.rows or []
        check("the pause menu's CPU reaction: the drill's own 24 frames",
              [r[2] for r in rows] == ["24 frames"], str(rows))
        paced = [(tries[i], p.chases[i]) for i in range(
            min(len(tries), len(p.chases))) if tries[i] in PACED]
        first = [(k, ch[0]) for k, ch in paced if ch]
        check("at the console's pace it thinks in forks: each throw's "
              "answers are there before the tech can be seen (the standing "
              "row first, the whole table when it comes)",
              len(first) == len(PACED) and all(
                  g["first"] is not None and g["first"] < g["see"]
                  for _, g in first),
              "; ".join("%s: answers after %s frames, the whole table "
                        "after %s (the grab held %s, thrown on %s, it can "
                        "act on %s, sees the tech on %s; %s searches in "
                        "%.0f ms%s)" % (
                            k, g["first"], g["back"], g["held"],
                            g["thrown"], g["free"], g["see"],
                            g["searches"], g["wall"] or 0,
                            ", not all" if g["partial"] else "")
                        for k, g in first))
        if args.gpu:
            # (drawn by the graphics card, as a person's game is: the
            # whole table in time to choose how to wait)
            check("drawn by the graphics card, the whole table is back "
                  "in time to choose how to wait: 10 frames or more before "
                  "the tech is seen",
                  len(first) == len(PACED) and all(
                      g["back"] is not None and g["back"] + 10 <= g["see"]
                      for _, g in first), "")
        think = getattr(c.session, "thinker", None)
        errors = list(getattr(think, "errors", []) or [])
        check("nothing wrong in its thinking", not errors,
              errors[0].strip().splitlines()[-1] if errors else "")
        check("part 2, a tech away and a jump at once: judged, escaped or "
              "caught", len(told) >= 2 and
              told[1].get("part") == "Choose where" and
              (told[1]["success"] or words[1].startswith("Caught")),
              words[1] if len(words) > 1 else "")
        check("no tech and nothing after it: a missed tech",
              len(told) >= 3 and not told[2]["success"] and
              words[2].startswith("Missed tech"),
              words[2] if len(words) > 2 else "")
        # (a read of another option, begun before the tech is seen,
        # loses to this one: the mixup the drill is about)
        read = [g["stance"] for g in (p.chases[3] if len(p.chases) > 3
                                      else []) if g["stance"] and
                g["stance"].startswith("read ") and
                g["stance"] != "read in place"]
        check("a tech in place and nothing after it: the cover lands, "
              "unless it had read another option",
              len(told) >= 4 and (
                  (not told[3]["success"] and
                   words[3].startswith("Caught")) or bool(read)),
              "%s; %s" % (words[3] if len(words) > 3 else "",
                          [(g["stance"], g["option"], g["cover"])
                           for g in (p.chases[3] if len(p.chases) > 3
                                     else [])]))
        check("D-pad right: another opponent of the deck, and the try "
              "against it judged", p.turned is not None and
              p.turned[1] not in (None, p.turned[0]) and len(told) >= 5 and
              told[4].get("scenario") == p.turned[1],
              "%s; judged against %s" % (
                  p.turned, told[4].get("scenario") if len(told) > 4
                  else None))
        check("every try judged", len(told) >= len(tries),
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
