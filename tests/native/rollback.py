"""Rollback's frame records: going back any number of frames, checked
headless against full snapshots.

    python tests/native/rollback.py [--frames N] [--seed S]

src/host/rollback.c keeps, for each of the last frames, the pages it wrote
and what they held before. Here a match is played by random inputs (both
ports), a record made at every frame boundary and a full snapshot
(state.c) at some of them. Checked: going back 1 to 20 frames gives exactly
the state saved at that boundary; playing on from there with the same
inputs gives the same game and the same state as the first time, and the
records made the second time can be gone back through again; and how much
a frame writes and what the records cost.

Which pages a frame wrote comes from the watched regions alone where the
kernel has it (userfaultfd's asynchronous write protection and the
pagemap's scan: "ranged"), else from the whole process's soft-dirty marks
(MELEE_RB=softdirty asks for those). And a forked copy of a game keeps its
parent's mirror where that is the memory: a copy of a copy plays the same
frames ahead as its parent, twice over, and is left as it was; a copy made
after frames were played for real, the mirror behind, makes its own.
(MELEE_RB_VERIFY=1: every mirror kept is compared with the memory.)
"""
import argparse
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from native import Native  # noqa: E402
from state import inputs, view  # noqa: E402
from melee_actor.ahead import look  # noqa: E402
from melee_engine.fork import Fork  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def step(n, frame):
    for p in range(2):
        n.pad(p, **frame[p])
    n.step()
    n.rb("mark")
    return view(n)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--frames", type=int, default=400)
    ap.add_argument("--seed", type=int, default=3)
    args = ap.parse_args()
    script = inputs(args.seed, args.frames)
    with Native() as n:
        n.start("fox", "marth", "final-destination", args.seed)
        n.step(30)
        why = None
        try:
            n.rb("start")
        except Exception as e:
            why = str(e)
        check("the kernel says which pages were written", why is None,
              why or "")
        if why is not None:
            return 1
        how = n._cmd("rb how").split()[-1]
        want = "soft-dirty" if os.environ.get("MELEE_RB") == "softdirty" \
            else how
        check("by the watched regions alone, or by soft-dirty marks",
              how in ("ranged", "soft-dirty") and how == want, how)
        views = []
        saved = {}             # boundary index -> snapshot slot
        for i, frame in enumerate(script):
            views.append(step(n, frame))
            if i % 37 == 20:
                slot = len(saved) % 32
                n.save(slot)
                saved[i + 1] = slot   # the boundary after frame i
        end = len(script)
        n.save(31)
        stats = n.rb("stats")
        print("     a frame writes %.0f pages on average (%.1f MB), %d at "
              "most; marking takes %.3f ms on average, %.3f at most" % (
                  stats["pages"] / stats["marks"],
                  stats["pages"] / stats["marks"] * 4096 / 1e6,
                  stats["max_pages"], stats["mark_ms"] / stats["marks"],
                  stats["max_mark_ms"]))

        # back to the last few saved boundaries, one at a time
        here = end
        for boundary in sorted(saved, reverse=True):
            back = here - boundary
            if back > 20 or back < 1:
                continue
            n.rb("back", back)
            diff = n.state_diff(saved[boundary])
            check("%d frames back is the state saved there" % back,
                  diff is None, "first difference %s" % (diff,))
            here = boundary
        # play on from there with the same inputs, recording again
        replay = [step(n, script[i]) for i in range(here, end)]
        check("playing on from there is the same game",
              replay == views[here:end], "%d frames" % (end - here))
        check("and ends in the same state", n.state_diff(31) is None,
              str(n.state_diff(31)))
        # the new records go back too: to the earliest saved boundary
        # within reach
        reach = [b for b in saved if 0 < end - b <= 20]
        if reach:
            b = min(reach)
            n.rb("back", end - b)
            check("the records made the second time go back too "
                  "(%d frames)" % (end - b), n.state_diff(saved[b]) is None,
                  str(n.state_diff(saved[b])))
        # many short rollbacks, as netplay makes them: back 1 to 7, play
        # those frames again, every frame for a while
        n.load(31)
        n.rb("stop")
        n.rb("start")
        more = inputs(args.seed + 1, 200)
        straight = []
        for frame in more:
            straight.append(step(n, frame))
        n.save(30)
        n.load(31)
        n.rb("stop")
        n.rb("start")
        rolled = []
        for i, frame in enumerate(more):
            rolled.append(step(n, frame))
            back = min(1 + i % 7, i + 1)
            n.rb("back", back)
            for j in range(i + 1 - back, i + 1):
                rolled[j] = step(n, more[j])
        check("rolling back 1 to 7 frames after every frame and playing "
              "them again ends where playing straight does",
              rolled == straight and n.state_diff(30) is None,
              "first difference %s" % (n.state_diff(30),))
        stats = n.rb("stats")
        print("     %d rollbacks, %.3f ms each on average" % (
            stats["rewinds"], stats["rewind_ms"] / max(1, stats["rewinds"])))

        # -- copies and their mirrors -------------------------------------
        plan = [(30, dict(buttons=["A"], stick=(1.0, 0.0))),
                (30, dict(buttons=[], stick=(-1.0, 0.0)))]

        def ahead(g):
            return [(r.a_state, round(r.a_x, 3), round(r.a_y, 3),
                     r.t_state, round(r.t_x, 3))
                    for r in look(g, 0, 1, plan, stop=0).rows]

        def played(g):
            """A lookahead twice, the game's state around them."""
            before = g.state()
            one = ahead(g)
            two = ahead(g)
            return one, two, before == g.state()
        first = Fork(n)
        first._cmd("rb start")
        a1, a2, same_a = played(first)
        second = Fork(first)          # (keeps the first's mirror)
        b1, b2, same_b = played(second)
        check("a copy of a copy plays the same frames ahead as its parent, "
              "twice over, and is left as it was",
              len(a1) == 60 and a1 == a2 == b1 == b2 and same_a and same_b,
              "%d frames; left as they were: %s, %s" % (
                  len(a1), same_a, same_b))
        second.close()
        first.close()
        # frames played for real with rollback on and no marks: the mirror
        # is behind, and a copy made now must not keep it
        for frame in more[:5]:
            for p in range(2):
                n.pad(p, **frame[p])
            n.step()
        for p in range(2):
            n.pad(p)
        third = Fork(n)
        c1, c2, same_c = played(third)
        fourth = Fork(third)
        d1, d2, same_d = played(fourth)
        check("a copy made after frames were played for real makes its own "
              "mirror: its lookaheads leave it as it was, and its copy's "
              "too", len(c1) == 60 and c1 == c2 == d1 == d2 and same_c and
              same_d, "left as they were: %s, %s" % (same_c, same_d))
        fourth.close()
        third.close()
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
