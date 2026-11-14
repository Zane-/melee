"""The coach in the drills judged by the frame (tools/melee_actor/tech.py),
in the native client, checked off screen.

    python tests/client/coach_tech.py [--shots DIR]

Fox's Tech part. In each of Short hop, Wavedash, L-cancel and SHFFL a
stand-in misses three times in a row the way people do (holds jump; only
jumps; never presses L; only short hops): the coach's card opens, says what
was off and how to fix it, and plays the game's own pictures of the try
next to the same try with that put right, played again from a state saved
before it, which the judge passes. In Short hop, Y replays the try to the
same verdict, B goes back to the card and A to the drill, which goes on;
on its card the D-pad steps the pictures a frame at a time (paused) and up
plays them on, and each panel's input display shows that frame's pad: the
try's jump held longer than the target's.
(The owner, 2026-11-14: "I tried short hop tech drill and intentionally
failed 5 times in a row and no coach appeared!")
"""
import argparse
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import client  # noqa: E402
import window  # noqa: E402
from pausekeys import Chooser  # noqa: E402
from tech import Aerialist, Hopper, KEYS  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    args = ap.parse_args()
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

    def go_to(ident):
        for _ in range(6):
            if c.drills()[c.row[c.part]]["id"] == ident:
                return
            at = [d["id"] for d in c.drills()].index(ident)
            tap("Down" if at > c.row[c.part] else "Up")

    def play(plan, name, replay=False):
        """Start the drill in focus; `plan` misses until the card opens.
        Returns what was seen."""
        seen = dict(step=0, tries=0, card=None, shots=0, replay=None,
                    frames=set(), stand_in=None, waited=0)

        def person(game, frame):
            if seen["step"] == 0 and seen["stand_in"] is None:
                game.key("x", False)    # the A that started the drill
            if frame == -4:             # the card
                for key in KEYS:
                    game.key(key, False)
                if seen["step"] == 0:
                    seen["card"] = dict(c.coach_now)
                    seen["step"] = 1
                seen["waited"] += 1
                if seen["step"] == 1:
                    play = c.coach_play
                    for pid in "yt":
                        if play.sent.get(pid + "iY", "").endswith("1"):
                            seen["lit_" + pid] = True
                    # pictures at a few moments of their playing
                    if args.shots and seen["waited"] in (8, 40, 90):
                        game.shot(os.path.join(args.shots, "%s-card%d.png" %
                                               (name, seen["shots"])))
                        seen["shots"] += 1
                    if replay:
                        # frame by frame: D-pad up pauses, right twice,
                        # left once, up plays on (keys: t up, h right, f
                        # left)
                        w_ = seen["waited"]
                        if w_ == 50:
                            seen["k0"] = play.k
                        for at, k in ((44, "t"), (50, "h"), (56, "h"),
                                      (62, "f"), (70, "t")):
                            if w_ == at:
                                game.key(k)
                            elif w_ == at + 1:
                                game.key(k, False)
                        if w_ == 68:
                            seen["stepped"] = (play.paused, (
                                play.k - seen["k0"]) % play.n)
                        if w_ == 76:
                            seen["played"] = not play.paused
                        if w_ == 66 and args.shots:
                            game.shot(os.path.join(args.shots,
                                                   name + "-paused.png"))
                    if seen["waited"] == 100:
                        if replay:
                            game.key("c")           # Y: replay
                            seen["step"] = 2
                        else:
                            game.key("x")           # A: on with the drill
                            seen["step"] = 4
                elif seen["step"] == 3 and seen["waited"] > 4:
                    game.key("x")
                    seen["step"] = 4
                elif seen["step"] == 2:
                    game.key("c", False)
                return
            if frame == -5:             # the replay
                game.key("c", False)
                now = c.replay_now or {}
                seen["frames"].add(now.get("frame"))
                if args.shots and now.get("frame") == 3 and \
                        not seen.get("rshot"):
                    game.shot(os.path.join(args.shots, name + "-replay.png"))
                    seen["rshot"] = True
                if c.replay_result is not None and now.get("paused"):
                    seen["replay"] = dict(c.replay_result)
                    game.key("z")                   # B: back to the card
                    seen["step"] = 3
                    seen["waited"] = 0
                return
            if seen["step"] == 3 and frame != -4:
                game.key("z", False)
            if seen["step"] >= 4:
                for key in KEYS + ("z",):
                    game.key(key, False)
                if "out" not in seen:
                    game.key("x", False)    # the A that closed the card
                seen.setdefault("out", Chooser(c, "list"))(game)
                return
            if seen["stand_in"] is None or \
                    len(c.results_now()) != seen["tries"]:
                for key in KEYS:
                    game.key(key, False)
                seen["tries"] = len(c.results_now())
                seen["stand_in"] = plan()
            seen["stand_in"](game)

        c.person = person
        c.replay_result = None
        w.key("x")
        for _ in range(9000):
            c.frame()
            if c.screen == "list" and seen["step"] >= 4:
                break
        for key in KEYS + ("x", "z", "Return"):
            w.key(key, False)
        c.person = None
        frames(6)
        seen["results"] = list(c.results or [])
        return seen

    try:
        w = window.Window(window=(1280, 720))
        w.step(30)
        c = client.Client(w, source="keyboard", save=save,
                          out=tempfile.mkdtemp(prefix="melee-ui-"))
        w.pace(False)
        frames(6)
        tap("x")
        tap("x")
        tap("x")

        cases = [
            ("universal-short-hop", "short-hop", lambda: Hopper(12),
             "Jump held", "Short hop", True),
            ("universal-wavedash", "wavedash", lambda: Hopper(1),
             "No air dodge", "Frame-perfect", False),
            ("universal-l-cancel", "l-cancel",
             lambda: Aerialist(cancel=False), "No L-cancel", "L-cancel",
             False),
            ("universal-shffl", "shffl", lambda: Hopper(1), "No aerial",
             "SHFFL", False),
        ]
        for ident, name, plan, head, put_right, replay in cases:
            go_to(ident)
            seen = play(plan, name, replay)
            card = seen["card"] or {}
            check("%s: three misses in a row open the coach" % name,
                  seen["card"] is not None and
                  seen["results"][:3] == [False] * 3,
                  str(seen["results"]))
            check("%s: the card says what was off, and how to fix it" % name,
                  head in (card.get("headline") or "") and
                  len(card.get("fix") or "") > 20,
                  "%r; %r" % (card.get("headline"), card.get("fix")))
            you = [e for p in card.get("anim") or [] if p["id"] == "y"
                   for e in p["seq"]]
            tgt = [e for p in card.get("anim") or [] if p["id"] == "t"
                   for e in p["seq"]]
            pressed = any(r["you"] for r in (card.get("timeline") or {})
                          .get("rows", []))
            check("%s: the game's pictures of the try and of it put right, "
                  "tagged where a press starts" % name,
                  bool(card.get("you_pic")) and
                  bool(card.get("target_pic")) and len(you) > 10 and
                  len(tgt) > 10 and any(e["tag"] for e in tgt) and
                  (any(e["tag"] for e in you) or not pressed),
                  "%d and %d pictures" % (len(you), len(tgt)))
            check("%s: put right, the judge passes it" % name,
                  put_right in (card.get("target_words") or ""),
                  card.get("target_words") or "none")
            if replay:
                held = [sum(1 for e in seq if e["pad"] and
                            e["pad"]["buttons"] & 0x800) for seq in (you, tgt)]
                check("%s: an input display on each panel, from that frame's "
                      "pad: Y lit in both, held longer in the try" % name,
                      seen.get("lit_y") and seen.get("lit_t") and
                      held[0] > held[1] > 0, "Y held %d and %d frames" %
                      tuple(held))
                check("%s: the D-pad steps the pictures a frame at a time, "
                      "paused, and up plays them on" % name,
                      seen.get("stepped") == (True, 1) and
                      seen.get("played") is True,
                      "%s, then playing %s" % (seen.get("stepped"),
                                               seen.get("played")))
            if replay:
                r = seen["replay"] or {}
                check("%s: Y replays the try, the same to the end, frame by "
                      "frame" % name, r.get("same") is True and
                      len(seen["frames"] - {None}) >= 5,
                      "%s; same %s; %d frames" % (
                          r.get("words"), r.get("same"),
                          len(seen["frames"] - {None})))
            check("%s: A goes back to the drill, which goes on" % name,
                  c.screen == "list" and len(seen["results"]) >= 3,
                  "%s, %d tries" % (c.screen, len(seen["results"])))
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
