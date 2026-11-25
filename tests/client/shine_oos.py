"""Fox's shine out of shield in the native client (data/drills/
fox-shine-oos.json, the first drill whose opponent is a script of the
engine's vocabulary: docs/ai/opponent-vocabulary.md), checked without a
person or a desktop: keys pressed on a virtual display.

    python -u tests/client/shine_oos.py [--shots DIR] [--seed N]

The drill opens from Fox's course (Punish). On first open the tutorial: its
two lessons, the first the game's own pictures of the shine out of shield
frame by frame (X on the first frame after shield stun, down-B on frame
J + 1), then the part's card; R twice turns to the third part, against the
deck. A stand-in shields; the opponent approaches and attacks the shield;
as shield stun ends (seen a frame ahead in the game, as a person sees it
coming) the stand-in presses Y with the shield held and down-B 3 frames
later: a success, twice. Then Y 4 frames after the stun: "Late jump",
twice, and the coach's card after the second miss (Settings: 2). Then the
stand-in jumps away as the opponent commits: the attack misses the shield,
and the try is not counted (an attack too fast to leave, a jab from next
to it, lands on the shield all the same: the jump away is then tried
again, three more times at most). Input delay 0 (the stand-in's keys are
the frames it means).

Which opponent and attack a try meets is drawn from the session's random
numbers: `--seed N` sets them, and a run without it prints the seed it
drew. With TRACE set a run says which attack each try meets and, frame by
frame from the hit, both fighters' states; TRIES=oos,oos,... sets the
tries. Five draws that failed (2026-11-25), each replayed and traced: seed
8 and 650256554 (Fox's forward air hits the shield again as the late jump
is pressed), 260468154 (Fox's down air, then his up air: the shine a frame
or two late did not reach), 1008632531 (Captain Falcon's forward tilt: the
stand-in's shine, a frame late, missed the leg a frame-perfect one hits),
435630502 (a jab from next to the stand-in, too fast to jump away from).
The drill's contracts now ask for one hit and for an answer that holds at
every lateness up to 3 frames ("one_hit", "late":
docs/ai/opponent-vocabulary.md), and the jump away is tried again: the
five pass.
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

DRILL = "fox-shine-oos"
STUN, GUARD = 181, 179
KEYS = ("c", "x", "z", "s", "h", "f", "t", "g", "Down", "Left", "Return")
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""), flush=True)


def stun_ends_next(game):
    """Does the player's shield stun end on the coming frame (played
    ahead, the shield held, and undone)?"""
    from melee_actor.ahead import look
    f = game.fighter(0)
    if f.state != STUN or f.hitlag > 0:
        return False
    out = look(game, 0, 1, [(1, dict(buttons=["R"], r=1.0))], stop=0)
    return bool(out.rows) and out.rows[0].a_state != STUN


class Player:
    """The person: answers the tutorial's cards, the coach's card, and
    plays `tries` in the drill, one each: "oos" (the shine out of shield
    on the first frame it sees coming), "late" (Y 4 frames after the stun
    ends), "away" (a jump away as the opponent commits)."""

    BUDGET = 30000              # calls before the test is called stuck
    AGAIN = 3                   # more jumps away, while none got away
    TRY_BUDGET = 1500           # frames a try may take (a reset: 480)

    def __init__(self, c, tries, shots=None):
        self.c, self.tries, self.shots = c, list(tries), shots
        self.cards, self.plays, self.coaches = [], [], []
        self.release = []
        self.saw = {}
        self.calls = 0
        self.since, self.here = 0, None
        self.try_at = 0               # tries begun
        self.t = None                 # the try's own state
        self.leaving = None
        self.skipped = []             # "Not counted" banners
        self.after_success = None

    def tap(self, game, key, frames=2):
        game.key(key)
        self.release.append([key, frames])

    def shot(self, game, name):
        if self.shots and name not in self.saw:
            self.saw[name] = True
            game.shot(os.path.join(self.shots, name + ".png"))

    def __call__(self, game, frame):
        self.calls += 1
        if os.environ.get("TRACE") and self.calls % 120 == 0:
            d = getattr(self.c.session, "d", None)
            op = getattr(d, "op_script", None)
            print("   call %d frame %s doing %s" % (
                self.calls, frame, op.doing if op else None),
                file=sys.stderr, flush=True)
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
            if frame < 0:
                return
        c = self.c
        if self.leaving is not None:
            self.leaving(game)                  # (the pause menu's frames)
            return
        here = (frame, id(c.tutorial_now) if frame == -6 else
                id(c.coach_now) if frame == -4 else None)
        self.since = self.since + 1 if here == self.here else 0
        self.here = here
        if frame in (-6, -4) and self.since < 3:
            return                              # (drawn first)
        if frame == -6:
            return self.card(game)
        if frame == -4:
            v = c.coach_now
            if not self.coaches or self.coaches[-1] is not v:
                self.coaches.append(v)
                self.shot(game, "coach")
            self.tap(game, "x")                 # A: on with the drill
            return
        if frame < 0:
            return
        self.drill(game, frame)

    def card(self, game):
        c = self.c
        v = c.tutorial_now
        play = c.tutorial_play
        if not self.cards or (self.cards[-1]["title"], self.cards[-1]["sub"]) \
                != (v["title"], v["sub"]):
            self.cards.append(v)
            seq = play.panels[0]["seq"] if play.panels else []
            self.plays.append(dict(
                n=play.n, caps={e.get("label"): e.get("caption")
                                for e in seq},
                cues={e.get("label"): e.get("cue") for e in seq}))
            self.shot(game, "card%d" % len(self.cards))
        sub = v["sub"]
        if sub.startswith("LESSON"):
            self.tap(game, "x")                 # A: next
        elif sub.startswith("PART 3"):
            self.tap(game, "x")                 # A: start
        else:
            self.tap(game, "s")                 # R: the next part
        return

    def drill(self, game, frame):
        c = self.c
        res = c.results_now()
        if any(res) and self.after_success is None:
            self.after_success = 8          # the column, a moment after
        if self.after_success is not None and self.after_success > 0:
            self.after_success -= 1
            if self.after_success == 0:
                self.shot(game, "success")
        done = len(res) + len(self.skipped)
        # (the last kind, a jump away, again while its attack was too fast
        # to leave: a jab from next to the stand-in lands on the shield all
        # the same and that try is judged. Until one misses the shield.)
        more = self.tries[-1] == "away" and not self.skipped and \
            done < len(self.tries) + self.AGAIN
        if done >= len(self.tries) and not more:
            for key in KEYS:
                game.key(key, False)
            self.leaving = self.leaving or Chooser(c, "list")
            self.leaving(game)
            return
        if self.t is None or self.try_at != done:
            for key in KEYS:
                game.key(key, False)
            self.try_at = done
            kind = self.tries[min(done, len(self.tries) - 1)]
            self.t = dict(kind=kind, step="shield", n=0, all=0)
            print("   try %d: %s" % (done + 1, kind), file=sys.stderr,
                  flush=True)
            return
        t = self.t
        t["n"] += 1
        t["all"] += 1
        if t["all"] > self.TRY_BUDGET:
            raise RuntimeError("try %d (%s) stuck at %s after %d frames" % (
                done + 1, t["kind"], t["step"], t["all"]))
        f = game.fighter(0)
        kind = t["kind"]
        if os.environ.get("TRACE"):
            d = c.session.d
            b = d.op_script.cur if d.op_script is not None else None
            line = getattr(getattr(b, "opp", None), "line", None)
            if line is not None and t.get("line") is not line:
                t["line"] = line
                print("   %s commits to %s (apart %.1f)" % (
                    d.scenario()["name"], line.names,
                    abs(game.fighter(1).pos[0] - f.pos[0])),
                    file=sys.stderr, flush=True)
                ans = b.opp.answer
                if ans is not None:
                    held = next((i for i, raw in enumerate(ans[1])
                                 if raw != ans[1][0]), len(ans[1]))
                    print("      its frame %d: the answer asked on frame %d, "
                          "the shield held %d frames, free on its frame %d"
                          % (b.opp.frame, ans[0], held, ans[0] + held),
                          file=sys.stderr, flush=True)
                    from melee_actor.ahead import compress, look
                    from melee_engine.behave import raw_pad
                    o_ = b.opp
                    rest = list(o_.plan[max(0, o_.frame - o_.plan_at):])
                    plan = compress([raw_pad(r) for r in rest]) + \
                        [(40, raw_pad((0, 0, 0, 0, 0, 0, 0)))]
                    seen = look(game, 1, 0, plan, stop=0)
                    for k, row in enumerate(seen.rows):
                        if row.t_hitlag > 0 or row.t_state == STUN or \
                                k + 1 == len(seen.rows):
                            print("      ahead: its frame %d me %3d hitlag "
                                  "%.0f | it %3d apart %5.1f" % (
                                      o_.frame + k, row.t_state,
                                      row.t_hitlag, row.a_state,
                                      abs(row.a_x - row.t_x)),
                                  file=sys.stderr, flush=True)
            o = game.fighter(1)
            if f.state == STUN or t.get("traced", 0) > 0:
                if f.state == STUN and not t.get("traced"):
                    t["traced"] = 26
                t["traced"] -= 1
                print("      %s/%d me %3d hitlag %.0f | it %3d apart %5.1f | "
                      "shield %.1f | its frame %s" % (
                          t["step"], t["n"], f.state, f.hitlag, o.state,
                          abs(o.pos[0] - f.pos[0]), f.shield,
                          getattr(getattr(b, "opp", None), "frame", None)),
                      file=sys.stderr, flush=True)
        if t["step"] == "shield":
            game.key("s")                       # R held
            if kind == "away":
                d = c.session.d
                b = d.op_script.cur if d.op_script is not None else None
                if b is not None and getattr(b, "committed", None) \
                        is not None:
                    game.key("s", False)
                    game.key("Left")            # back, a full jump
                    game.key("c")
                    t.update(step="away", n=0)
                return
            if kind == "oos" and stun_ends_next(game):
                game.key("c")                   # Y, the shield held
                t.update(step="jumped", n=0)
                if os.environ.get("TRACE"):
                    print("   Y at call %d: state %d, opponent %d" % (
                        self.calls, f.state, game.fighter(1).state),
                        file=sys.stderr, flush=True)
            elif kind == "late" and f.state == GUARD and \
                    t.get("stunned"):
                t.update(step="wait", n=0)
            if f.state == STUN:
                t["stunned"] = True
        elif t["step"] == "wait":
            game.key("s")
            if t["n"] >= 3:
                game.key("c")
                t.update(step="jumped", n=0)
        elif t["step"] == "jumped":
            if t["n"] == 2:
                game.key("c", False)
            if t["n"] == 3:
                game.key("Down")                # down-B, J frames after Y
                game.key("z")
            if t["n"] == 5:
                for key in ("Down", "z", "s"):
                    game.key(key, False)
        elif t["step"] == "away":
            if t["n"] >= 10:
                game.key("c", False)
                game.key("Left", False)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    ap.add_argument("--seed", type=int,
                    help="the session's random numbers (which opponent "
                         "and attack each try draws); left out, another "
                         "every run")
    args = ap.parse_args()
    # (the session's draws decide what the stand-in meets: with some the
    # test fails, on any tree. Printed, so that a failure can be replayed)
    seed = args.seed if args.seed is not None else \
        random.randrange(1, 1 << 30)
    random.seed(seed)
    print("seed %d" % seed, flush=True)
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
        check("the drill opens from Fox's course, Punish",
              part == "Punish" and
              c.drills()[c.row[c.part]]["id"] == DRILL, str(part))

        tries = os.environ.get("TRIES", "oos,oos,late,late,away").split(",")
        p = Player(c, tries, args.shots)
        told = []
        show, say = c.show_result, c.banner_say

        def counted(result, results):
            told.append(dict(result))
            if os.environ.get("TRACE"):
                print("   result: %s" % result["words"], file=sys.stderr,
                      flush=True)
            show(result, results)

        def banner(word, text):
            if word == "Not counted":
                p.skipped.append(text)
            say(word, text)
        c.show_result, c.banner_say = counted, banner
        c.person = p
        w.key("x")
        for _ in range(60000):
            if c.screen != "drill" and p.leaving is not None:
                break
            c.frame()
        for key in KEYS:
            w.key(key, False)
        c.person, c.show_result, c.banner_say = None, show, say
        frames(6)

        subs = [x.get("sub", "") for x in p.cards]
        check("first open: two lessons, then the part's card; R turns to "
              "the third part",
              subs[:2] == ["LESSON 1 OF 2", "LESSON 2 OF 2"] and
              [x["title"] for x in p.cards[:2]] ==
              ["Out of shield", "What it punishes"] and
              any(s.startswith("PART 3 OF 3") for s in subs),
              "; ".join(s.replace("\n", " ") for s in subs))
        one = p.plays[0] if p.plays else {"caps": {}, "cues": {}}
        check("lesson 1: the game's pictures frame by frame, X on frame 1 "
              "and down-B on frame 4, each cued",
              one.get("n", 0) > 10 and
              one["caps"].get("F1", "").startswith("Frame 1: shield stun "
                                                    "over") and
              (one["cues"].get("F1") or (None, None))[1] == "go" and
              (one["cues"].get("F4") or (None, None))[1] == "go",
              "%s pictures; F1 %r; F4 %r" % (one.get("n"),
                                             one["caps"].get("F1"),
                                             one["cues"].get("F4")))
        two = p.plays[1] if len(p.plays) > 1 else {"cues": {}}
        check("lesson 2: a still of the shine hitting on frame 4",
              len(p.cards) > 1 and p.cards[1].get("still") and
              list(two["cues"].values()) == [("Frame 4: the shine hits",
                                              "go")],
              str(list(two["cues"].values())))
        three = next((pl for pl, cd in zip(p.plays, p.cards)
                      if cd.get("sub", "").startswith("PART 3")), None)
        check("the third part's card plays its example",
              three is not None and three["n"] > 10, str(three and
                                                         three["n"]))
        words = [r["words"] for r in told]
        check("shielded, the shine out of shield on the frame it is seen "
              "coming: a success, twice",
              len(told) >= 2 and all(r["success"] for r in told[:2]) and
              all(w_.startswith("Shine out of shield on frame")
                  for w_ in words[:2]) and
              all(r.get("part") == "Against an attack" for r in told[:2]),
              "; ".join(words[:2]))
        check("Y 4 frames after shield stun: a failure, saying so",
              len(told) >= 4 and not told[2]["success"] and
              not told[3]["success"] and
              all(w_.startswith("Late jump: X or Y on frame")
                  for w_ in words[2:4]),
              "; ".join(words[2:4]))
        co = p.coaches[0] if p.coaches else {}
        check("after two misses the coach's card: what was wrong and the "
              "fix", co.get("headline") == "Late jump" and
              "shield stun" in co.get("fix", "") and
              co.get("you_pic") is not None,
              "%r / %r" % (co.get("headline"), co.get("fix", "")[:60]))
        check("a jump away as the opponent commits: the attack misses the "
              "shield, the try not counted", len(p.skipped) >= 1 and
              p.skipped[0].startswith("Not counted:") and
              4 <= len(told) <= 4 + Player.AGAIN,
              "%s; %d counted, %d of them jumps away an attack was too "
              "fast for" % (p.skipped[:1], len(told), len(told) - 4))
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
