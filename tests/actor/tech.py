"""The tech drill judges (tools/melee_actor/tech.py), on the headless build,
with the player's inputs scripted to the frame.

    python tests/actor/tech.py

Short hop: the jump button held 1, 2, ... frames; the verdict has to turn
from success to failure exactly where the character's jump squat says, and
name the frames held. Wavedash: the air dodge pressed a frame early, on the
frame, one, two and three frames late, not at all, and straight up; only
the ones within the tolerance succeed, and each failure says why. For Fox
(3 frames of jump squat), Marth (4) and Bowser (8).
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from native import Native  # noqa: E402
from melee_actor import tech  # noqa: E402

SQUAT = {"fox": 3, "marth": 4, "bowser": 8}
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


class Scripted:
    """A player whose pad is a script: {frame: pad}, frame 0 being the one
    the script starts on, once the fighter has stood still for a moment."""

    def __init__(self, script):
        self.script, self.i, self.still = script, None, 0

    def __call__(self, n, frame):
        f = n.fighter(0)
        if self.i is None:
            self.still = self.still + 1 if f.state == tech.WAIT else 0
            if self.still < 8:
                n.pad(0)
                return
            self.i = 0
        if self.i in self.script:
            n.pad(0, **self.script[self.i])
        self.i += 1


def attempt(session, script):
    result = session.run(each_frame=Scripted(script))
    session.n.pad(0)
    session.n.step(30)
    return result


def main():
    for who, squat in SQUAT.items():
        with Native() as n:
            s = tech.Session(dict(tech="short_hop"), n, 0, who, live=False)
            check("%s: jump squat measured as %d frames" % (who, squat),
                  s.squat == squat and s.full > s.hop,
                  "%d; speeds %.2f and %.2f" % (s.squat, s.hop, s.full))
            got = []
            for held in range(1, squat + 3):
                r = attempt(s, {0: dict(buttons=["X"]), held: dict()})
                got.append(r["success"])
                said = "held %d frame" % held if held <= squat else \
                    "still held on frame %d" % (squat + 1)
                if said not in r["words"]:
                    check("%s: names the frames held" % who, False,
                          "%d: %s" % (held, r["words"]))
            want = [held <= squat - 1 for held in range(1, squat + 3)]
            check("%s: a short hop up to %d frames held, a full hop after"
                  % (who, squat - 1), got == want,
                  "".join("s" if g else "F" for g in got))
            r = attempt(s, {0: dict(stick=(0, 1)), 2: dict()})
            check("%s: a jump with the stick is judged by what came out"
                  % who, "stick" in r["words"], r["words"])

            s.kind = "wavedash"
            diag = dict(buttons=["R"], stick=(0.7, -0.7), r=1.0)
            cases = [(-1, False, "early"), (0, True, "Frame-perfect"),
                     (1, True, "1 frame late"), (2, True, "2 frames late"),
                     (3, False, "3 frames late")]
            ok, said = True, []
            for late, good, word in cases:
                at = squat + late
                r = attempt(s, {0: dict(buttons=["X"]), 1: dict(), at: diag,
                                at + 2: dict()})
                said.append("%+d %s" % (late, "s" if r["success"] else "F"))
                if r["success"] != good or word not in r["words"]:
                    ok = False
                    said[-1] += " (%s)" % r["words"]
            check("%s: the air dodge a frame early, on time, 1, 2 and 3 "
                  "frames late" % who, ok, ", ".join(said))
            r = attempt(s, {0: dict(buttons=["X"]), 1: dict()})
            check("%s: no air dodge is said to be none" % who,
                  not r["success"] and "No air dodge" in r["words"],
                  r["words"])
            r = attempt(s, {0: dict(buttons=["X"]), 1: dict(),
                            squat: dict(buttons=["R"], stick=(0, 1), r=1.0),
                            squat + 2: dict()})
            check("%s: an air dodge upward did not reach the ground" % who,
                  not r["success"] and "did not reach" in r["words"],
                  r["words"])
            tl = attempt(s, {0: dict(buttons=["X"]), 1: dict(),
                             squat + 1: diag, squat + 3: dict()})["timeline"]
            check("%s: the timeline has the press and where it was due"
                  % who, tl["rows"][1]["you"] == [squat + 2] and
                  tl["rows"][1]["perfect"] == [squat + 1],
                  str(tl["rows"][1]))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
