"""Train against a scenario yourself: the opponent does what the scenario
says, you play, and each attempt gets a verdict.

    python tools/melee_actor/train.py data/scenarios/shield-grab-dash-attack.json
    python tools/melee_actor/train.py FILE --reps 20 --jitter 6 --input keyboard

Opens the native build's window on this desktop (tools/melee_native/play.py
has the controls and what is needed). The situation is put back after each
attempt; the verdict is printed here, not on the game's screen, yet. Close
the window or press Ctrl-C to stop.

--offscreen runs it on a virtual display with nobody at the controls (every
attempt then fails or passes as the scenario does with a player who stands
still); tests/actor/train.py plays it there with key presses.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "melee_native"))
sys.path.insert(0, os.path.join(HERE, ".."))

import window  # noqa: E402
from native import NativeError  # noqa: E402
from melee_actor import scenario as scn  # noqa: E402


def verdict(result):
    """One line for the person who just tried."""
    if result["success"]:
        return "success"
    missed = [c for c in result["checks"] if not c["passed"]]
    words = {"target_hit": "you did not hit them",
             "not_hit": "you were hit",
             "target_not_hit": "they were hit",
             "hit": "you were not hit"}
    return "failure: " + "; ".join(
        words.get(c["expect"], c["expect"] + " did not hold")
        for c in missed)


def train(game, sc, port=0, reps=10, jitter=0.0, source="auto", pause=45,
          each_frame=None, say=print):
    """Run the scenario `reps` times with a person on `port`. Returns the
    results."""
    session = scn.Session(sc, game=game, person=port)
    game.live(port, source)
    game.pace(True)
    say(sc.get("name", "A scenario"))
    if sc.get("about"):
        say(sc["about"])
    results = []
    for i in range(reps):
        result = session.run(jitter=jitter, run=i, each_frame=each_frame)
        results.append(result)
        say("%2d  %s" % (i + 1, verdict(result)))
        game.step(pause)
    done = sum(r["success"] for r in results)
    say("%d of %d" % (done, len(results)))
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("scenario")
    ap.add_argument("--reps", type=int, default=10)
    ap.add_argument("--jitter", type=float, default=0.0,
                    help="move the placements sideways by up to this much "
                         "from one attempt to the next")
    ap.add_argument("--input", default="auto",
                    help="auto, keyboard, pad0, pad1, ...")
    ap.add_argument("--offscreen", action="store_true")
    args = ap.parse_args()
    sc = scn.load(args.scenario)
    port = sc.get("player", {}).get("port", 0)
    w = None
    try:
        w = window.Window(real=not args.offscreen)
        train(w, sc, port=port, reps=args.reps, jitter=args.jitter,
              source=args.input)
    except KeyboardInterrupt:
        pass
    except NativeError as e:
        if "the window was closed" not in "".join(w.log[-5:] if w else []):
            print(str(e)[-1500:], file=sys.stderr)
            return 1
    finally:
        if w is not None:
            w.close()
        left = window.leftovers()
        if left:
            print("still running: %s" % left, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
