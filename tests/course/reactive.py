"""The course drills whose opponent is the Melee Actor (option Opponent:
Reactive, tools/melee_course/react.py), against the C's frame tables
(Fixed timing).

    python tools/native_build.py
    python tests/course/reactive.py [DRILL ...]

The player moves before the attack: stays put, dashes in, dashes out or
walks away (and turns back to face the opponent), during the opponent's
wait. Then either nothing (stands, or
holds shield in shine out of shield): the attack must land, since nothing
answered it. Or the drill's own demonstration (wavedash back and punish,
anti-air up smash, shine out of shield), from the opponent's commitment:
the drill must call it a success. Fixed timing misses a player who moved,
so the first fails and the drill can be passed by stepping aside.
"""
import os
import sys
import time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from native import Native  # noqa: E402
from melee_course import engine, registry  # noqa: E402
from melee_course.react import FIXED, REACTIVE  # noqa: E402

DRILLS = ["fox-wavedash-back-punish", "fox-anti-air", "fox-shine-oos"]
MOVES = ["none", "dash_in", "dash_out", "walk_away"]
MOVE_END = 30          # attempt frames the movement may take
checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def mover(session, move, after):
    """The player's pad: `move` during the first frames of the attempt,
    then `after` (a pad)."""
    def each(game, frame):
        f = session.attempt_frame
        toward = -session.c.toward       # from the player to the opponent
        lx = 0
        if move == "dash_in" and 3 <= f < 10:
            lx = 127 * toward
        elif move == "dash_out" and 3 <= f < 10:
            lx = -127 * toward
        elif move == "walk_away" and 3 <= f < 25:
            lx = -38 * toward
        if move in ("dash_out", "walk_away") and f == MOVE_END - 4:
            lx = 30 * toward             # a tap: turn back to face them
        if f < MOVE_END and lx:
            session.set_player_pad(lx=int(lx))
        else:
            session.set_player_pad(**after)
    return each


def landed(drill_id, result):
    """The attack met the player (or the shield) in an attempt where the
    player did not answer it."""
    if drill_id == "fox-shine-oos":
        return result["report"].get("shield_hit") == 1 or \
            result["words"].startswith("Hit through")
    return result["words"].startswith("Got hit") or \
        result["words"].startswith("Shielded")


def main(only):
    t0 = time.time()
    for drill_id in only or DRILLS:
        drill = registry.get(drill_id)
        tally = {}
        for mode in (REACTIVE, FIXED):
            stand = dict(buttons=engine.R, trigger=140) \
                if drill_id == "fox-shine-oos" else {}
            hit = punished = total = 0
            misses = []
            for i, entry in enumerate(drill.deck):
                # A game per scenario: the headless game has crashed after
                # about 45 attempts in one match, with either opponent
                # (seen 2026-11-13, not the lookahead's doing).
                with Native() as game:
                    s = engine.Session(drill, game, character="fox",
                                       options={"Opponent": mode},
                                       live=False, seed=1, dpad=False)
                    # the demonstration's inputs once the movement is over
                    play_ref = s._play_reference

                    def late_ref(ref, marks, s=s, play_ref=play_ref):
                        if s.attempt_frame >= MOVE_END:
                            play_ref(ref, marks)
                    s._play_reference = late_ref
                    for move in MOVES:
                        total += 1
                        r = s.run(scenario=i, demo=False,
                                  each_frame=mover(s, move, stand))
                        hit += landed(drill_id, r)
                        r2 = s.run(scenario=i, demo=True,
                                   each_frame=mover(s, move, {}))
                        punished += r2["success"]
                        if mode == REACTIVE and not (
                                landed(drill_id, r) and r2["success"]):
                            misses.append("%s/%s: %s; %s" % (
                                entry.name, move, r["words"], r2["words"]))
            tally[mode] = (hit, punished, total, misses)
        (hit, pun, total, misses), (fhit, fpun, _, _) = \
            tally[REACTIVE], tally[FIXED]
        check("%s: unanswered, the attack lands after any movement"
              % drill_id, hit == total,
              "reactive %d of %d, fixed timing %d" % (hit, total, fhit))
        check("%s: answered as the drill teaches, it is a success"
              % drill_id, pun == total,
              "reactive %d of %d, fixed timing %d%s" % (
                  pun, total, fpun,
                  "; " + " | ".join(misses) if misses else ""))
    print("%d of %d checks passed (%.0f s)" % (sum(checks), len(checks),
                                                time.time() - t0))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
