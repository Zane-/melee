"""The tech drill judges (tools/melee_actor/tech.py), on the headless build,
with the player's inputs scripted to the frame.

    python tests/actor/tech.py

Short hop: the jump button held 1, 2, ... frames; the verdict has to turn
from success to failure exactly where the character's jump squat says, and
name the frames held. Wavedash: the air dodge pressed a frame early, on the
frame, one, two and three frames late, not at all, and straight up; only
the ones within the tolerance succeed, and each failure says why. L-cancel:
L pressed nine frames before landing down to a frame after it, a light R,
Z. SHFFL: the whole motion, then with each of its four parts left out. For
Fox (3 frames of jump squat), Marth (4) and Bowser (8).
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
    # Back to the middle: the judge no longer moves the player (commit
    # 73c814112), and four wavedashes to the right left Marth teetering
    # at the ledge, never standing still, so the next script never began.
    session.n.place(session.person, 0.0, 0.0, 1)
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
            # the top of a short hop, as a frame of the script
            s.kind = "short_hop"
            top = None
            hop = Scripted({0: dict(buttons=["X"]), 1: dict()})
            for _ in range(160):
                hop(n, 0)
                n.step()
                g = n.fighter(0)
                if hop.i is not None and g.airborne and g.vel[1] <= 0 and \
                        top is None:
                    top = hop.i - 1
                if top is not None and not g.airborne:
                    break
            n.pad(0)
            n.step(30)

            # ---- L-cancel: an aerial at the top of a short hop -----------------
            s.kind = "l_cancel"
            jump = {0: dict(buttons=["X"]), 1: dict(),
                    top: dict(buttons=["A"]), top + 1: dict()}
            r = attempt(s, jump)
            # the script's frame of landing (the attempt starts with the
            # aerial, at the script's frame `top`)
            land = top + r["landed"] - 1
            check("%s: an aerial with nothing pressed lands with its full "
                  "lag" % who, not r["success"] and "No L" in r["words"],
                  r["words"])

            def press(ago, pad=None):
                at = land - ago + 1
                script = dict(jump)
                script[at] = pad or dict(buttons=["L"], l=1.0)
                script[at + 1] = dict()
                return attempt(s, script)

            got = [press(ago)["success"] for ago in (9, 8, 7, 4, 1, 0)]
            check("%s: L on any of the 7 frames up to landing halves it; "
                  "an 8th early or a frame late does not" % who,
                  got == [False, False, True, True, True, False],
                  "".join("s" if g else "F" for g in got))
            r8, r0 = press(8), press(0)
            check("%s: and says how early or late" % who,
                  "8 frames before" in r8["words"] and
                  "after landing" in r0["words"],
                  "%s; %s" % (r8["words"], r0["words"]))
            check("%s: a light press of R and Z do it too" % who,
                  press(3, dict(r=0.5))["success"] and
                  press(3, dict(buttons=["Z"]))["success"])
            # a back air at the start of a full hop is over long before the
            # fighter comes down
            r = attempt(s, {0: dict(buttons=["X"]), squat + 2: dict(),
                            squat + 3: dict(cstick=(-1, 0)),
                            squat + 5: dict()})
            check("%s: an aerial that is over before landing is no attempt"
                  % who, bool(r.get("skip")) and
                  "Nothing to cancel" in r["words"], r["words"])

            # ---- SHFFL -----------------------------------------------------------
            s.kind = "shffl"
            # (the aerial a little before the top, so that it is still out
            # at the landing for a slow faller too)
            air = top - 2
            base = {0: dict(buttons=["X"]), 1: dict(),
                    air: dict(buttons=["A"]), air + 1: dict(),
                    top + 1: dict(stick=(0, -1)), top + 3: dict()}
            r = attempt(s, base)
            land = r["landed"] - 1          # as a frame of the script
            check("%s: the whole motion without the L-cancel fails on "
                  "that alone" % who,
                  [c["passed"] for c in r["checks"]] ==
                  [True, True, True, False], r["words"])
            full = dict(base)
            full[land - 2] = dict(buttons=["L"], l=1.0)
            full[land - 1] = dict()
            r = attempt(s, full)
            check("%s: short hop, aerial, fast fall, L-cancel is a SHFFL"
                  % who, r["success"] and r["words"].startswith("SHFFL"),
                  r["words"])
            held = dict(full)
            held[1] = dict(buttons=["X"])
            held[squat + 2] = dict()
            r = attempt(s, held)
            check("%s: with the jump held it is a full hop" % who,
                  not r["success"] and "Full hop" in r["words"], r["words"])
            none = dict(full)
            del none[air]
            r = attempt(s, none)
            check("%s: with no attack it says no aerial" % who,
                  not r["success"] and "No aerial" in r["words"],
                  r["words"])
            slow = dict(full)
            del slow[top + 1]
            r = attempt(s, slow)
            check("%s: with no fast fall it says so" % who,
                  not r["success"] and "No fast fall" in r["words"],
                  r["words"])
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
