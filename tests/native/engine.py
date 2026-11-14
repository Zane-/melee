"""The search engine on the native build (src/host/engine.c,
tools/melee_engine/search.py): lines of play tried in the real game,
scored, and undone.

    python tools/native_build.py
    python tests/native/engine.py
"""
import sys
import time

sys.path.insert(0, "tools/melee_native")
sys.path.insert(0, "tools")
from native import Native, NativeError  # noqa: E402
from melee_engine.search import player, search  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


def play_line(n, port, line):
    """Play a found line for real, frame by frame."""
    for b, lx, ly, cx, cy, lt, rt in line.raw():
        n.h.pads[port].update(buttons=b, lx=lx, ly=ly, cx=cx, cy=cy, lt=lt,
                              rt=rt, connected=True)
        n._dirty.add(port)
        n.step()
    n.pad(port)


def main():
    t0 = time.time()
    with Native() as n:
        n.start("fox", "captain-falcon")
        n.place(0, -15, 0, 1)
        n.place(1, 15, 0, -1)
        for _ in range(5):
            n.step()
        snap = n.snapshot()
        h0, f0 = n.state_hash(), n.frame

        r = search(n, 1, 0, horizon=90, budget=3000, depth=2, contact=30)
        check("a search leaves the whole game as it was",
              n.state_hash() == h0 and n.state()["frame"] == f0,
              "%d trials, %d frames in %.0f ms" % (r.trials, r.frames, r.ms))
        check("against a Fox standing 30 away, the best lines hit him",
              r.best.contact == "hit" and r.best.dmg > 0,
              "; ".join(map(repr, r.lines[:3])))
        check("lines are deeper than one move when the budget allows",
              any("+" in l.names for l in r.lines[:3]), r.best.names)
        r2 = search(n, 1, 0, horizon=90, budget=3000, depth=2, contact=30)
        check("the same search again finds the same",
              [(l.names, l.value) for l in r.lines] ==
              [(l.names, l.value) for l in r2.lines])

        # the best line played for real does what the search said
        pct = n.fighter(0).percent
        play_line(n, 1, r.best)
        got = n.fighter(0).percent - pct
        check("the best line played for real does the damage it was scored "
              "with", abs(got - r.best.dmg) < 0.01,
              "%s: %.0f%% for real, %.0f%% searched" % (r.best.names, got,
                                                         r.best.dmg))
        n.restore(snap)

        # the target's inputs: Fox shields from the start
        player(n, [(200, (0x20, 0, 0, 0, 0, 0, 255))])
        r = search(n, 1, 0, horizon=60, budget=0, depth=1, shield=30)
        player(n, None)
        check("with the player's inputs given (a shield), the attacks "
              "meet the shield", r.best.contact == "shield",
              "; ".join(map(repr, r.lines[:3])))
        n.restore(snap)

        # holding the opponent: throws are the moves
        n.place(1, -5, 0, -1)
        for _ in range(3):
            n.step()
        r = search(n, 1, 0, horizon=60, budget=0, depth=1)
        grab = next((l for l in r.lines if l.names == "grab"), None)
        check("a grab next to him is among the lines, and connects",
              grab is not None and grab.contact == "grab",
              repr(grab))
        r = search(n, 1, 0, horizon=120, budget=4000, depth=2)
        thrown = [l for l in r.lines if l.names.startswith("grab+")]
        check("after the grab, the throws are searched",
              any(m.split("+")[1].endswith("throw") for m in
                  (l.names for l in thrown)),
              ", ".join(l.names for l in thrown[:4]))
        n.restore(snap)

        # bad input is refused and changes nothing
        h1 = n.state_hash()
        refused = 0
        for cmd in ("search", "search 9 0 60 0 1", "engine nonsense"):
            try:
                n._cmd(cmd)
            except NativeError:
                refused += 1
        check("malformed searches are refused, nothing moves",
              refused == 3 and n.state_hash() == h1)

        # in a process restored from a snapshot
        n.restore(snap)
        h2 = n.state_hash()
        r = search(n, 1, 0, horizon=60, budget=500, depth=2)
        f = n.frame
        n.step()
        check("in a restored process it undoes everything too, and play "
              "goes on", n.state_hash() != h2 and n.frame == f + 1,
              "%d trials" % r.trials)

        # what it costs
        n.restore(snap)
        r = search(n, 1, 0, horizon=90, budget=12000, depth=3)
        check("throughput: thousands of simulated frames a second",
              r.frames / (r.ms / 1000.0) > 3000,
              "%.0f frames/s (%d frames, %d trials, %.0f ms)" % (
                  r.frames / (r.ms / 1000.0), r.frames, r.trials, r.ms))

    # A game that draws (a shadow game does): nothing of the search may be
    # left behind, the draw flag included (it once was: the shadow then
    # drew no more and fell out of step).
    with Native(draw=True) as n:
        n.start("fox", "captain-falcon")
        n.place(0, -15, 0, 1)
        n.place(1, 15, 0, -1)
        for _ in range(5):
            n.step()
        same = 0
        for _ in range(5):
            n._cmd("save 0")
            search(n, 1, 0, horizon=60, budget=800, depth=2, contact=30)
            same += n._cmd("hash 0") == "ok same"
            n.step()
        check("in a game that draws, every byte of its state is as before "
              "each search", same == 5, "%d of 5 the same" % same)

    print("%d of %d checks passed (%.0f s)" % (sum(checks), len(checks),
                                                time.time() - t0))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
