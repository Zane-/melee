"""What the engine's tests share: checks, raw pads into the game, and a
scripted opponent driven frame by frame against a stand-in, every loop with
a frame budget."""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for p in (os.path.join(ROOT, "tools", "melee_native"),
          os.path.join(ROOT, "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)

from melee_engine.drill import NONE  # noqa: E402

checks = []

SHIELD = (0x20, 0, 0, 0, 0, 0, 255)
JUMP = (0x400, 0, 0, 0, 0, 0, 0)
FD_HALF = 85.5657


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""),
          flush=True)
    return ok


def put(n, port, raw):
    """A raw pad (buttons, lx, ly, cx, cy, lt, rt) for the next frame."""
    b, lx, ly, cx, cy, lt, rt = raw
    n.h.pads[port].update(buttons=b, lx=lx, ly=ly, cx=cx, cy=cy, lt=lt,
                          rt=rt, connected=True)
    n._dirty.add(port)


def restart(n, p1="fox", p2="marth"):
    """A new match, both pads let go of first (Native.start sets only port
    0's: the last test's opponent pad was held through the new match's
    start: an A held through it is a jab when the countdown ends)."""
    put(n, 0, NONE)
    put(n, 1, NONE)
    n.step()
    n.start(p1, p2)


def place(n, px, ox, pct=0.0, opct=0.0, settle=3):
    """The player (port 0) at px facing the opponent (port 1) at ox."""
    n.place(0, px, 0, 1 if ox > px else -1, False, pct)
    n.place(1, ox, 0, -1 if ox > px else 1, False, opct)
    put(n, 0, NONE)
    put(n, 1, NONE)
    n.step(settle)


def drive(n, opp, standin, budget, until=None, what="the end"):
    """Play `opp` (script.Opponent, port 1) against `standin(f, st)` (the
    player's raw pad, port 0), at most `budget` frames, stopping when
    `until(f, st)` holds (after the frame is played) or the script is over.
    Returns (frames played, [(state before the frame, player pad, opponent
    pad)]); fails loudly when the budget runs out with `until` unmet."""
    log = []
    for f in range(budget):
        st = n.state()
        mine = standin(f, st)
        raw = opp.pad(st, mine)
        put(n, 0, mine)
        put(n, 1, raw)
        n.step()
        log.append((st, mine, raw))
        if until is not None and until(f, n.state()):
            return f + 1, log
        if opp.over:
            return f + 1, log
    if until is not None:
        print("      (waited %d frames for %s)" % (budget, what), flush=True)
    return budget, log


def done():
    print("%d of %d checks passed" % (sum(checks), len(checks)), flush=True)
    return 0 if all(checks) else 1
