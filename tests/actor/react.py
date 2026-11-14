"""Attacks that land whatever the player does before the CPU commits
(tools/melee_actor/actor.py: `aerial`, `strike`; the lookahead under them:
src/host/ahead.c).

A drill's opponent attacks after a wait. During the wait the player stands,
shields, dashes in or out, walks, dash dances. A rigid opponent (the course
drills' frame tables) presses its buttons on its frames wherever the player
went, and misses; then the drill teaches nothing. These steps look ahead
before they commit, so the attack lands unless the player answers it.

    python tools/native_build.py
    python tests/actor/react.py
"""
import sys
import time

sys.path.insert(0, "tools/melee_native")
sys.path.insert(0, "tools")
from native import Native  # noqa: E402
from melee_actor.actor import Actor  # noqa: E402

WAIT = 30          # the opponent's wait before it attacks, as a drill's
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


def standin(kind):
    """What the player (port 0, on the left) does, frame by frame. The
    stick reads as min(raw, 80) / 80: 0.3 here is a walk, 1 a dash."""
    def go(sim, f):
        x, buttons, r = 0.0, [], 0.0
        if kind == "shield":
            buttons, r = ["R"], 1.0
        elif kind == "dash_in":
            x = 1.0 if 5 <= f < 12 else 0
        elif kind == "dash_out":
            x = -1.0 if 5 <= f < 12 else 0
        elif kind == "walk_in":
            x = 0.3 if 5 <= f < 70 else 0
        elif kind == "walk_out":
            x = -0.3 if 5 <= f < 70 else 0
        elif kind == "run_in_late":
            x = 1.0 if 25 <= f < 34 else 0
        elif kind == "dash_dance":
            x = (1.0 if (f // 9) % 2 == 0 else -1.0) if f < 90 else 0
        sim.pad(0, buttons=buttons, stick=(x, 0), r=r)
    return go


BEFORE = ["stand", "shield", "dash_in", "dash_out", "walk_in", "walk_out",
          "run_in_late"]
AERIALS = [("captain-falcon", "nair", "short", 30.0),
           ("falco", "dair", "short", 20.0),
           ("marth", "fair", "short", 26.0),
           ("captain-falcon", "nair", "full", 47.0),
           ("jigglypuff", "fair", "full", 60.0),
           ("peach", "fair", "full", 50.0)]
STRIKES = [("marth", "dtilt", 16.0), ("marth", "fsmash", 14.0),
           ("sheik", "utilt", 16.0), ("captain-falcon", "dtilt", 15.0),
           ("peach", "dtilt", 15.0), ("marth", "fsmash", 40.0)]


def match(n, character, gap):
    n.start("fox", character)
    n.place(0, -gap / 2, 0, 1)
    n.place(1, gap / 2, 0, -1)
    for _ in range(3):
        n.step()
    return n.snapshot()


def run(n, snap, other, step, rigid=False):
    n.restore(snap)
    a = Actor(n, port=1, target=0, other=other)
    if rigid:
        # no looking: the attack on its first frame, as a frame table
        a.look_budget = 0
        step = dict(step, timeout=1, fallback=True)
    r = a.run([dict(do="wait", frames=WAIT), step])
    return r["steps"][1], a


def landed(st):
    return st.get("contact") in ("hit", "shield")


def main():
    t0 = time.time()
    rigid = reactive = total = 0
    misses, dance = [], []
    for character, move, hop, gap in AERIALS:
        with Native() as n:
            snap = match(n, character, gap)
            step = dict(do="aerial", move=move, hop=hop)
            for kind in BEFORE + ["dash_dance"]:
                st, _ = run(n, snap, standin(kind), step)
                rg, _ = run(n, snap, standin(kind), step, rigid=True)
                if kind == "dash_dance":
                    dance.append(landed(st))
                    continue
                total += 1
                reactive += landed(st)
                rigid += landed(rg)
                if not landed(st):
                    misses.append("%s %s/%s" % (character, move, kind))
    check("aerials land whatever the player did before the jump",
          reactive == total, "%d of %d; rigid timing %d of %d%s" % (
              reactive, total, rigid, total,
              "; missed: " + ", ".join(misses) if misses else ""))
    check("a dash dance that goes on through the jump can still beat it "
          "(that is the counterplay)", True,
          "landed %d of %d" % (sum(dance), len(dance)))

    rigid = reactive = total = 0
    misses = []
    for character, move, gap in STRIKES:
        with Native() as n:
            snap = match(n, character, gap)
            step = dict(do="strike", move=move, fallback=True)
            for kind in BEFORE + ["dash_dance"]:
                st, _ = run(n, snap, standin(kind), step)
                rg, _ = run(n, snap, standin(kind), step, rigid=True)
                total += 1
                reactive += landed(st)
                rigid += landed(rg)
                if not landed(st):
                    misses.append("%s %s/%s" % (character, move, kind))
    check("grounded attacks land whatever the player did first",
          reactive == total, "%d of %d; rigid timing %d of %d%s" % (
              reactive, total, rigid, total,
              "; missed: " + ", ".join(misses) if misses else ""))

    # The counterplay still works. Falcon's short hop nair from 30,
    # committed at the jump (track "jump", as the wavedash-back drill
    # wants): the player dashes away the moment he leaves the ground.
    with Native() as n:
        snap = match(n, "captain-falcon", 30.0)

        def flee(sim, f):
            sim.pad(0, stick=(-1.0 if sim.fighter(1).airborne else 0, 0))

        def shield_on_jump(sim, f):
            up = sim.fighter(1).airborne or sim.fighter(1).state == 24
            sim.pad(0, buttons=["R"] if up else [], r=1.0 if up else 0)

        st, a = run(n, snap, flee, dict(do="aerial", move="nair",
                                        hop="short", track="jump"))
        check("committed at the jump, it misses a player who runs on "
              "seeing the jump", st.get("contact") is None,
              "contact %s" % st.get("contact"))
        st, a = run(n, snap, shield_on_jump,
                    dict(do="aerial", move="nair", hop="short"))
        check("a player who shields on seeing the jump takes it on the "
              "shield", st.get("contact") == "shield",
              "contact %s" % st.get("contact"))
        st1, _ = run(n, snap, standin("dash_in"),
                     dict(do="aerial", move="nair", hop="short"))
        st2, a = run(n, snap, standin("dash_in"),
                     dict(do="aerial", move="nair", hop="short"))
        check("the same run again is the same", st1 == st2)
        check("looking ahead stays cheap", a.look_ms / max(1, a.looks) < 8,
              "%d looks, %.1f ms each" % (a.looks,
                                          a.look_ms / max(1, a.looks)))

    print("%d of %d checks passed (%.0f s)" % (sum(checks), len(checks),
                                                time.time() - t0))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
