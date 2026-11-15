"""The Ice Climbers' partner on the native build: put back with the leader by
every placement, at rest, a clean slate each time (src/host/setup.c,
`partner`).

    python tools/native_build.py
    python tests/native/partner.py

A drill's reset placed only a player's first fighter, Popo. Nana stayed
where the last attempt had left her and followed her log of where Popo had
been: she walked back through the opponent and jabbed it, or took its hit
instead of him (universal-di, Jigglypuff's forward smash). Holding the
opponent when the reset placed it, she was left in her grab with nobody to
hold, and the game fell over in the grab's callback (fn_800DA054 through
Fighter_procAccessory, signal 11). Now standing, falling, on the ledge and
on the respawn platform she comes back with him, fresh: where he is, at his
damage, her log of him emptied; `sleep` takes her out of play with him.
"""
import json
import random
import sys

sys.path.insert(0, "tools/melee_native")
from native import Fighter, Native, NativeError  # noqa: E402

REBIRTH, REBIRTH_WAIT, SLEEP, WAIT, FALL = 12, 13, 11, 14, 29
CLIFF_WAIT, CATCH_WAIT, CATCH_ATTACK = 253, 216, 217
CAPTURED = range(224, 229)    # held: CapturePulledHi ... CaptureDamageHi
checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


def nana(n, port=0):
    """Player `port`'s second fighter (slots 4 to 7: control.c)."""
    return Fighter(json.loads(n._cmd("fighter %d" % (4 + port))))


def calm(n, frames, port=0):
    """Nana over `frames` frames: the states she went through and how far
    she moved."""
    states, xs = set(), []
    for _ in range(frames):
        n.step()
        f = nana(n, port)
        states.add(f.state)
        xs.append(f.pos[0])
    return states, max(xs) - min(xs)


def wander(n, seed, frames=240):
    """Random play by both, so that Nana is anywhere, doing anything."""
    rng = random.Random(seed)
    for _ in range(frames):
        for port in (0, 1):
            if rng.random() < 0.2:
                n.pad(port,
                      buttons=[b for b in "ABXZR" if rng.random() < 0.12],
                      stick=(rng.choice((-1, -0.5, 0, 0.5, 1)),
                             rng.choice((-1, 0, 0, 1))),
                      cstick=(rng.choice((-1, 0, 0, 0, 1)), 0))
        n.step()
    n.pad(0)
    n.pad(1)


def reset(n):
    """A drill's reset: the player, then the opponent in front of him."""
    n.clean()
    n.place(0, -20.0, 0.0, facing=1, percent=40.0)
    n.place(1, -8.0, 0.0, facing=-1)


def grab_by_nana(n):
    """Nana holding Fox: Popo's grab misses; Fox is put in front of her
    before hers (she plays his inputs a few frames later)."""
    for when in range(6, 16):
        n.place(0, -20.0, 0.0, facing=1)
        n.place(1, 60.0, 0.0, facing=-1)
        n.step(60)
        q = nana(n)
        for fr in range(40):
            n.pad(0, buttons=["Z"] if fr < 2 else [])
            if fr == when:
                n.place(1, q.pos[0] + 9.0, 0.0, facing=-1)
            n.step()
            if nana(n).state in (CATCH_WAIT, CATCH_ATTACK) and \
                    n.fighter(1).state in CAPTURED:
                n.pad(0)
                return True
    n.pad(0)
    return False


def main():
    with Native() as n:
        n.start("ice-climbers", "fox", "final-destination")
        # Nana somewhere else, doing something else
        n.pad(0, stick=(1, 0))
        n.step(40)
        n.pad(0, buttons=["A"])
        n.step(2)
        n.pad(0)
        n.step(3)
        before = nana(n)
        reset(n)
        n.step()
        p, f = n.fighter(0), nana(n)
        check("placing Popo puts Nana where he stands, on the floor",
              abs(f.pos[0] - p.pos[0]) < 0.01 and abs(f.pos[1]) < 0.01 and
              not f.airborne and f.state == WAIT and f.facing == p.facing,
              "she was at %.1f in state %d; Popo %s | Nana %s" % (
                  before.pos[0], before.state, p.summary(), f.summary()))
        check("at his damage, a full shield, no hitstun or hitlag",
              f.percent == 40 and f.shield == 60 and f.hitstun == 0 and
              f.hitlag == 0, f.summary())
        states, moved = calm(n, 90)
        check("and she stays there, standing, in front of the opponent",
              states == {WAIT} and moved < 0.01,
              "states %s, moved %.2f" % (sorted(states), moved))

        seed = n.state()["rng"]
        reset(n)
        check("the placement draws no random number (her CPU's reset "
              "does, and the seed is put back)", n.state()["rng"] == seed)

        # the same placement after two different pasts: the same two
        wander(n, 3)
        reset(n)
        first = [n.fighter(0).d, nana(n).d]
        wander(n, 99, 400)
        reset(n)
        again = [n.fighter(0).d, nana(n).d]
        check("after another past the same placement gives the same Popo "
              "and Nana", first == again,
              "" if first == again else "%s | %s" % (first[1], again[1]))

        # The C-stick down (universal-asdi's examples): in her log from the
        # last attempt (the respawn's reset of the log leaves the C-stick),
        # and held through the reset (by a person: a live pad is left as it
        # is). Either was a down smash of hers into the opponent.
        for held in (False, True):
            n.place(1, 60.0, 0.0, facing=-1)
            n.step(60)
            n.pad(0, cstick=(0, -1))
            n.step(40)
            if not held:
                n.pad(0)
                n.step(2)
            reset(n)
            states, _ = calm(n, 30)
            mine = n.fighter(0).state
            n.pad(0)
            check("the C-stick down %s: she does not smash" % (
                "held through the reset" if held else
                "in the last attempt"), states == {WAIT} and mine == WAIT,
                "her states %s, his %d" % (sorted(states), mine))
            n.step(30)

        n.place(0, 20.0, 0.0, facing=-1, percent=0.0)
        n.step()
        f = nana(n)
        check("facing the other way: she does too", f.facing == -1 and
              abs(f.pos[0] - 20.0) < 0.01 and f.state == WAIT, f.summary())

        n.place(0, 0.0, 30.0, air=True, percent=10.0)
        n.step()
        p, f = n.fighter(0), nana(n)
        check("put in the air: she falls with him", f.airborne and
              f.state == FALL and abs(f.pos[0] - p.pos[0]) < 0.01 and
              abs(f.pos[1] - p.pos[1]) < 0.01 and f.jumps_used == 1 and
              f.percent == 10, f.summary())
        for _ in range(120):
            n.step()
            if not nana(n).airborne:
                break
        n.step(30)
        check("and lands", not nana(n).airborne and
              abs(nana(n).pos[1]) < 0.01, nana(n).summary())

        for side in ("left", "right"):
            lx = n.ledge(side=side)[0]
            n.ledge(0, 20.0, side)
            n.step()
            p, f = n.fighter(0), nana(n)
            ok = p.state == CLIFF_WAIT and f.state == WAIT and \
                not f.airborne and abs(f.pos[0] - lx) < 0.01 and \
                abs(f.pos[1]) < 0.01
            states, moved = calm(n, 120)
            check("Popo on the %s ledge: Nana stands at its end, and stays"
                  % side, ok and states == {WAIT} and moved < 0.01,
                  "%s | %s, then %s, moved %.2f" % (
                      p.summary(), f.summary(), sorted(states), moved))

        n.rebirth(0, -30.0, 40.0)
        n.step()
        p, f = n.fighter(0), nana(n)
        ok = f.state == REBIRTH_WAIT and abs(f.pos[0] + 30.0) < 0.01 and \
            abs(f.pos[1] - 40.0) < 0.01
        states, moved = calm(n, 120)
        check("on the respawn platform: she waits on it with him",
              ok and states == {REBIRTH_WAIT} and moved < 0.01,
              "%s, then %s" % (f.summary(), sorted(states)))
        n.pad(0, stick=(0, -1))
        n.step(3)
        n.pad(0)
        n.step(2)
        check("and leaves it when he does", n.fighter(0).state == FALL and
              nana(n).state == FALL, "%s | %s" % (
                  n.fighter(0).summary(), nana(n).summary()))
        n.step(60)

        n.sleep(0)
        n.step()
        check("asleep, as between a stock and the respawn: both",
              n.fighter(0).state == SLEEP and nana(n).state == SLEEP)
        n.place(0, -20.0, 0.0, facing=1)
        n.step()
        check("placed: both back", n.fighter(0).state == WAIT and
              nana(n).state == WAIT and abs(nana(n).pos[0] + 20.0) < 0.01,
              nana(n).summary())

        held = grab_by_nana(n)
        check("(Nana holding Fox, set up)", held)
        try:
            reset(n)
            n.step(30)
            alive, why = True, ""
        except NativeError as e:
            alive, why = False, str(e).splitlines()[1:3]
        check("a reset while she holds the opponent: the game goes on, "
              "and both are free", alive and nana(n).state == WAIT and
              n.fighter(1).state == WAIT, str(why) if not alive else
              "%s | %s" % (nana(n).summary(), n.fighter(1).summary()))

    with Native() as n:
        n.start("fox", "ice-climbers", "final-destination")
        n.place(1, 30.0, 0.0, facing=-1, percent=25.0)
        n.step()
        f = nana(n, 1)
        check("the opponent as the Ice Climbers: its Nana is placed too",
              f.state == WAIT and abs(f.pos[0] - 30.0) < 0.01 and
              f.facing == -1 and f.percent == 25, f.summary())

    with Native() as n:
        n.start("zelda", "fox", "final-destination")
        other = nana(n).d
        n.place(0, -20.0, 0.0, facing=1)
        n.step()
        check("Zelda's other form, her second fighter, is left alone",
              n.fighter(0).state == WAIT and nana(n).d is not None and
              nana(n).state == other["state"] if other else
              n.fighter(0).state == WAIT,
              "before %s, after %s" % (other and other["state"],
                                       nana(n).d and nana(n).state))

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
