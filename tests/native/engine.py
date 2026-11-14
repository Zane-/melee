"""The search engine on the native build (src/host/engine.c,
tools/melee_engine/search.py): lines of play tried in the real game,
scored, and undone.

    python tools/native_build.py
    python tests/native/engine.py
"""
import os
import sys
import time

sys.path.insert(0, "tools/melee_native")
sys.path.insert(0, "tools")
from native import Native, NativeError  # noqa: E402
from melee_course.engine import (  # noqa: E402
    ATTACK_AIR_B, ATTACK_HI3, ATTACK_HI4)
from melee_engine.search import player, preroll, search  # noqa: E402
from melee_engine.fork import Fork  # noqa: E402

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

        # a drill's moves only: the first (moves=) and the rest (then=)
        n.restore(snap)
        r = search(n, 1, 0, horizon=90, budget=3000, depth=3,
                   moves="dash_,walk_", then="wait,dash_", split=2)
        names = set(m for l in r.lines for m in l.moves[1:])
        check("then= keeps the moves after the first to the drill's, and "
              "split=2 reports a line per first two moves",
              names and all(m == "wait" or m.startswith("dash_")
                            for m in names) and
              len(set(tuple(l.moves[:2]) for l in r.lines)) == len(r.lines)
              and len(r.lines) > 4,
              "%d lines, after the first: %s" % (len(r.lines),
                                                  ", ".join(sorted(names))))

        # the timing scan: a full hop, a drift, the aerial on each frame
        n.restore(snap)
        n.place(1, 25, 0, -1)
        n.place(0, -22, 0, 1)
        for _ in range(3):
            n.step()
        h3 = n.state_hash()
        r = search(n, 1, 0, horizon=110, budget=0, depth=1,
                   moves="jump_in,jump", then="nair_in,nair", scan=2,
                   hold="in,none", contact=60, hit=20, lcancel=0, stop=1,
                   near=45, trial=30)
        lands = [l for l in r.lines if l.contact == "hit"]
        ks = set(l.moves[1] for l in lands)
        check("the timing scan finds full hop nairs that land, on many "
              "frames, and leaves the game as it was",
              len(lands) >= 10 and len(ks) >= 5 and
              n.state_hash() == h3,
              "%d of %d lines land, %d timings, %.0f ms" % (
                  len(lands), len(r.lines), len(ks), r.ms))
        best = lands[0] if lands else None
        # a line scored as it is (eval=1): the same contact, same frame
        if best is not None:
            preroll(n, best.raw())
            e = search(n, 1, 0, horizon=len(best.raw()) + 1, budget=0,
                       depth=1, eval=1, stop=1)
            same = e.lines and e.lines[0].contact == "hit" and \
                e.lines[0].contact_at == best.contact_at
        check("a line played back as a plan (eval=1) lands as the scan "
              "found", best is not None and same,
              repr(best) if best is not None else "no line")
        # what the answer search reports: the target in the air, and what
        # hit it (the player's port searched against the line)
        player(n, [(1, r) for r in best.raw()] if best else None)
        preroll(n, [(0, 0, 0, 0, 0, 0, 0)] * 15)
        a = search(n, 0, 1, horizon=best.contact_at + 1 if best else 60,
                   budget=0, depth=1, then="utilt,usmash,sh_bair", scan=1,
                   hold="none,walk_out,out", hit=100, lcancel=0, stop=1,
                   near=40, trial=20, enough=1)
        player(n, None)
        hits = [l for l in a.lines if l.contact == "hit"]
        check("against that line, an anti-air 15 frames on is found: the "
              "opponent hit in the air, by an up tilt, up smash or back air",
              hits and hits[0].contact_air and
              hits[0].contact_state in (ATTACK_HI3, ATTACK_HI4,
                                        ATTACK_AIR_B),
              repr(hits[0]) + " state %d" % hits[0].contact_state
              if hits else "none")

        # thinking in a forked copy, while the game goes on
        n.restore(snap)
        r0 = search(n, 1, 0, horizon=60, budget=800, depth=2, contact=30)
        f = Fork(n)
        at = f.state()["frame"]
        for _ in range(20):
            n.step()
        r1 = search(f, 1, 0, horizon=60, budget=800, depth=2, contact=30)
        refused = False
        try:
            f._cmd("step")
        except NativeError:
            refused = True
        pid = f.pid
        f.close()
        time.sleep(0.2)
        try:
            os.kill(pid, 0)
            gone = open("/proc/%d/stat" % pid).read().split()[2] == "Z"
        except OSError:
            gone = True
        check("a forked copy stands at its frame while the game plays on, "
              "finds what the game would, plays no frame, and leaves when "
              "closed",
              [(l.names, l.value) for l in r0.lines] ==
              [(l.names, l.value) for l in r1.lines] and
              f.state is not None and n.frame >= at + 20 and refused and
              gone, "forked at %d, the game at %d" % (at, n.frame))

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
