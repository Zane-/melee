"""Short hop in the native client, the first drill in the drill format
(data/drills/universal-short-hop.json, docs/ai/drill-format.md), checked
without a person or a desktop: keys pressed on a virtual display.

    python tests/client/short_hop.py [--shots DIR]

On first open the tutorial: the drill's card (what, why, the parts, what to
expect), its example played from the drill's start with the input display,
stopping on each captioned frame and stepped a frame at a time. Then the
parts in turn: a hop passes the first and opens the second's page; jumps
held through the squat are failures, and after two in a row the coach's
card says what was wrong and how to fix it (the tutorial shows how, the
coach what went wrong: the owner, 2026-11-14); three taps pass the second.
The part reached and the tutorial seen are kept: opened again, the drill
goes straight to its third part.
"""
import argparse
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))

import client  # noqa: E402
import screens  # noqa: E402
import courses  # noqa: E402
import window  # noqa: E402
from pausekeys import Chooser  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools"))
from melee_drills import format as fmt  # noqa: E402

WAIT = 14
KEYS = ("c", "x", "z", "h", "f", "t", "g")
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


class Hopper:
    """Holds jump (c is Y) for `hold` frames once the fighter stands."""

    def __init__(self, hold):
        self.hold, self.i, self.still = hold, None, 0

    def __call__(self, game):
        f = game.fighter(0)
        if self.i is None:
            self.still = self.still + 1 if f.state == WAIT else 0
            if self.still < 12:
                return
            self.i = 0
            game.key("c")
        elif self.i == self.hold:
            game.key("c", False)
        self.i += 1


class Player:
    """The person: answers the tutorial's card and example, the coach's
    card, and hops as `hops` says (hold frames, one attempt each)."""

    def __init__(self, c, hops, shots=None):
        self.c, self.hops, self.shots = c, list(hops), shots
        self.cards, self.examples, self.coaches = [], [], []
        self.release = []
        self.stand_in = None
        self.done = 0
        self.saw = {}
        self.ex_steps = 0
        self.leaving = None
        self.want_example = False
        self.plays = []
        self.card_steps = 0
        self.k1 = None
        self.stepped = None
        self.full_done = False
        self.l3 = set()

    # calls (frames) a test may take before it is called stuck: a loop that
    # waits for a screen or a key that never comes fails, saying where
    BUDGET = 20000

    def tap(self, game, key):
        """A key pressed for two frames (one pressed and let go within a
        single frame is not seen)."""
        game.key(key)
        self.release.append([key, 2])

    def shot(self, game, name):
        if self.shots and name not in self.saw:
            self.saw[name] = True
            game.shot(os.path.join(self.shots, name + ".png"))

    def __call__(self, game, frame):
        self.calls = getattr(self, "calls", 0) + 1
        if self.calls > self.BUDGET:
            raise RuntimeError("stuck after %d frames, last at %r" % (
                self.calls, getattr(self, "_last", None)))
        self._last = (frame, (self.c.example_now or {}).get("frame")
                      if frame == -7 else None)
        if os.environ.get("TRACE"):
            what = (frame if frame < -1 else "play", (self.c.tutorial_now or
                    {}).get("title") if frame == -6 else (self.c.example_now
                    or {}).get("frame") if frame == -7 else None)
            if what != getattr(self, "_traced", None):
                self._traced = what
                print("   trace", what, len(self.c.results_now()),
                      file=sys.stderr, flush=True)
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
            return
        c = self.c
        ex = c.example_now or {}
        here = (frame, id(c.tutorial_now) if frame == -6 else
                id(c.coach_now) if frame == -4 else
                (ex.get("frame"), ex.get("paused"), ex.get("end"))
                if frame == -7 else None)
        self.since = self.since + 1 if here == getattr(self, "here", None) \
            else 0
        self.here = here
        if frame in (-6, -4, -7) and self.since < 3:
            return                              # (drawn first)
        if len(c.results_now()) >= len(self.hops) and \
                frame not in (-6, -4, -7):
            # all hops made: out through the pause menu
            for key in KEYS:
                game.key(key, False)
            self.leaving = self.leaving or Chooser(c, "list")
            self.leaving(game)
            return
        if frame == -6:                         # the tutorial's card
            v = c.tutorial_now
            play = c.tutorial_play
            # (the same card again, after its full-size example, is not a
            # new one)
            if not self.cards or (self.cards[-1]["title"], self.cards[-1]
                                  ["sub"]) != (v["title"], v["sub"]):
                self.cards.append(v)
                seq = play.panels[0]["seq"] if play.panels else []
                self.plays.append(dict(
                    n=play.n,
                    caps={e.get("label"): e.get("caption") for e in seq},
                    cues={e.get("label"): e.get("cue") for e in seq}))
                self.shot(game, "card%d" % len(self.cards))
                self.card_steps = 0
            sub = v["sub"]
            if sub.startswith("LESSON 1 "):
                # step its example: the first press pauses it a frame on
                self.card_steps += 1
                if self.card_steps == 2:
                    self.k1 = play.k
                if self.card_steps <= 3:
                    self.tap(game, "h")
                else:
                    self.stepped = (self.k1, play.k, play.paused)
                    self.shot(game, "lesson-stepped")
                    self.tap(game, "x")         # A: next
                return
            if sub.startswith("LESSON 3 "):
                # frame by frame (round again if it played past them) onto
                # frame 4, a picture of frames 1 to 3
                seq = play.panels[0]["seq"] if play.panels else []
                at = seq[play.k]["label"] if 0 <= play.k < len(seq) else ""
                if play.paused and at in ("F1", "F2", "F3"):
                    self.shot(game, "lesson3-" + at)
                    self.l3.add(at)
                self.card_steps += 1
                if (len(self.l3) < 3 or at != "F4") and \
                        self.card_steps < 100:
                    self.tap(game, "h")
                else:
                    self.tap(game, "x")         # A: on to part 1
                return
            if sub.startswith("LESSON"):
                self.tap(game, "x")             # A: next
                return
            if not self.full_done:
                self.full_done = True
                self.tap(game, "c")             # Y: the example, full size
            else:
                self.tap(game, "z")             # B: start
            return
        if frame == -7:                         # the example
            e = c.example_now or {}
            self.examples.append(dict(e))
            if e.get("end"):
                self.shot(game, "example-end")
                self.tap(game, "z")             # B: go on
            elif e.get("paused"):
                if e.get("frame") == 1:
                    self.shot(game, "example-f1")
                if self.ex_steps < 2 and e.get("frame", 0) >= 1:
                    self.ex_steps += 1
                    self.tap(game, "h")         # a frame on
                else:
                    self.tap(game, "x")         # play on
            return
        if frame == -4:                         # the coach's card
            v = c.coach_now
            if not self.coaches or self.coaches[-1] is not v:
                self.coaches.append(v)
                self.shot(game, "coach")
            self.tap(game, "x")
            return
        if frame < -1:
            return
        n = len(c.results_now())
        if n >= len(self.hops):
            for key in KEYS:
                game.key(key, False)
            self.leaving = self.leaving or Chooser(c, "list")
            self.leaving(game)
            return
        if self.stand_in is None or self.done != n:
            game.key("c", False)
            self.done = n
            self.stand_in = Hopper(self.hops[n])
        self.stand_in(game)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    args = ap.parse_args()
    if args.shots:
        os.makedirs(args.shots, exist_ok=True)
    save = os.path.join(tempfile.mkdtemp(prefix="melee-client-"),
                        "client.json")
    w = None

    def frames(n):
        for _ in range(n):
            c.frame()

    def tap(key, after=6):
        w.key(key)
        frames(2)
        w.key(key, False)
        frames(after)

    def play(person):
        """Start the drill in focus with `person` playing it, until they
        leave it."""
        told = []
        show = c.show_result

        def counted(result, results):
            told.append(result)
            show(result, results)
        c.show_result = counted
        c.person = person
        c.results = None
        w.key("x")
        for _ in range(20):
            c.frame()
            if c.results is not None:
                break
        for key in KEYS:
            w.key(key, False)
        c.person, c.show_result = None, show
        w.pace(False)
        frames(6)
        return told

    try:
        w = window.Window(window=(1280, 720))
        w.step(30)
        c = client.Client(w, source="keyboard", save=save,
                          out=tempfile.mkdtemp(prefix="melee-ui-"))
        c.settings["coach"] = 2
        w.pace(False)
        frames(6)
        tap("x")
        tap("x")
        tap("x")
        first = c.drills()[c.row[c.part]]
        check("Tech opens on Short hop, and it plays here",
              c.screen == "list" and courses.PARTS[c.part] == "Tech" and
              first["id"] == "universal-short-hop" and
              c.here.get(first["id"]) == courses.COURSE)

        # part 1: one hop; part 2: two held through the squat (the coach),
        # then three taps
        p = Player(c, [1, 6, 6, 1, 1, 1], args.shots)
        told = play(p)
        subs = [x.get("sub", "") for x in p.cards]
        check("first open: the tutorial's three lessons, then part 1's card",
              subs[:4] == ["LESSON 1 OF 3", "LESSON 2 OF 3", "LESSON 3 OF 3",
                           "PART 1 OF 3\nTHE JUMP SQUAT"] and
              [x["title"] for x in p.cards[:3]] ==
              ["The jump squat", "Every character's is different",
               "When to let go"], "; ".join(subs[:4]))
        one = p.plays[0] if p.plays else {}
        check("lesson 1 plays the jump squat, the game's own pictures, each "
              "frame captioned and its frame of the squat counted",
              p.cards[0].get("pic") is not None and one.get("n", 0) > 20 and
              one["caps"].get("F1", "").startswith("Frame 1: jump pressed")
              and one["cues"].get("F2") == ("Jump squat: frame 2 of 3",
                                            "info") and
              one["cues"].get("F4") == ("In the air", "info"),
              "%d pictures; F2 %r" % (one.get("n", 0),
                                      one.get("cues", {}).get("F2")))
        st = p.stepped or (None, None, False)
        check("the D-pad steps it a frame at a time, paused",
              st[2] and st[0] is not None and st[1] == (st[0] + 2) %
              max(1, one.get("n", 1)), str(st))
        table = p.cards[1].get("table", "") if len(p.cards) > 1 else ""
        everyone = fmt.every_character("jump_squat")
        check("lesson 2: every character's jump squat, Fox's marked",
              all(screens.esc(name) in table for _, _, name in everyone) and
              table.count('class="trow') == len(set(v for v, _, _ in
                                                    everyone)) and
              '<span class="tme">Fox</span>' in table,
              "%d characters, %d lengths" % (len(everyone),
                                             table.count('class="trow')))
        three = p.plays[2] if len(p.plays) > 2 else {"cues": {}}
        cu = three["cues"]
        check("lesson 3: when to let go, frame by frame: green on frames 1 "
              "and 2, red on 3, then the air",
              cu.get("F1", (None, None))[1] == "go" and
              cu.get("F2", (None, None))[1] == "go" and
              cu.get("F3") == ("Still held: full hop", "late") and
              cu.get("F4", (None, None))[1] == "info",
              "; ".join("%s %s" % (k, cu.get(k)) for k in ("F1", "F2", "F3",
                                                           "F4")))
        caps = {e["frame"]: e["caption"] for e in p.examples
                if e.get("frame") is not None}
        check("Y shows it full size: stopping on the captioned frames, "
              "stepped a frame at a time, to its end",
              caps.get(1, "").startswith("X pressed") and
              caps.get(3, "").startswith("The squat's last frame") and
              caps.get(4, "").startswith("In the air") and
              any(e.get("end") for e in p.examples) and p.ex_steps == 2,
              "; ".join("%d: %s" % (k, caps[k][:30]) for k in sorted(caps)
                        if k in (1, 2, 3, 4)))
        words = [r["words"] for r in told]
        parts = [r.get("part") for r in told]
        check("a hop passes the first part, and the second's card opens, "
              "playing its example",
              told and told[0]["success"] and told[0].get("part_passed")
              and len(p.cards) >= 2 and
              len(p.cards) >= 5 and
              "TAP, DO NOT HOLD" in p.cards[4].get("sub", "") and
              p.plays[4]["n"] > 20 and
              p.plays[4]["cues"].get("F3", (None, None))[1] == "late",
              "%s; then the card %r" % (words[:1], p.cards[4].get("sub")
                                        if len(p.cards) > 4 else None))
        check("jumps held through the squat fail, saying so",
              len(told) >= 3 and not told[1]["success"] and
              not told[2]["success"] and
              all(w.startswith("Held through the squat") for w in words[1:3]),
              "; ".join(words[1:3]))
        co = p.coaches[0] if p.coaches else {}
        check("after two misses the coach: what was wrong (the try against "
              "the example, the game's pictures of both) and how to fix it",
              co.get("headline") == "Held through the squat" and
              "within 2 frames" in co.get("fix", "") and
              co.get("you_pic") is not None and
              co.get("target_pic") is not None,
              "%r / %r; try pictured %s" % (
                  co.get("headline"), co.get("fix", "")[:60],
                  co.get("you_pic") is not None))
        check("three taps pass the second part, and the third opens",
              len(told) == 6 and all(r["success"] for r in told[3:]) and
              told[5].get("part_passed") and
              told[5].get("next_part") == "Every time" and
              parts[3:] == ["Tap, do not hold"] * 3,
              "; ".join(words[3:]))
        saved = courses.Progress(save).drill("universal-short-hop")
        check("the tutorial seen and the part reached are kept",
              saved.get("tutorial") and saved.get("part") == 2 and
              saved["tries"] == 6, str(saved))

        # opened again: no tutorial, the third part
        p2 = Player(c, [1, 1], args.shots and None)
        told2 = play(p2)
        check("opened again: no tutorial, straight to the third part",
              not p2.cards and len(told2) == 2 and
              all(r.get("part") == "Every time" for r in told2),
              "%d cards; %s" % (len(p2.cards),
                                [r.get("part") for r in told2]))
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
