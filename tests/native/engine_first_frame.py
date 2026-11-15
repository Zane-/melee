"""The engine offers a move on the first frame the game reads it, headless.

    python -u tests/native/engine_first_frame.py

A state that ends with its animation (shield stun, landing lag, a jump
squat, a whiffed grab, an attack) ends in Fighter_procAnim, before
Fighter_procInput reads that frame's input in the state it ended into
(src/melee/ft/fighter.c: the procs are set up anim 1, cpu 2, input 3). So
the first frame a new input works is the frame after which the fighter is
first seen able to act, not the one after it. For each situation, frame by
frame: the first frame a real input does what it should (pressed on the
coming frame, played, undone), and the first frame the engine's search
offers that move on the coming frame (a search of that move alone); they
must be the same frame. Then the macros' own timing, played for real: the
shine out of shield, a short hop's aerial and a wavedash's air dodge on
the first airborne frame (frame J + 1 of the jump); and the shine out of
shield contract with within 4: every commitment answered by the frame-4
shine it found (the jump on the first frame out of shield stun, down-B J
frames later), played.
"""
import os
import random
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tests", "engine"))
from common import NONE, SHIELD, check, done, place, put, restart  # noqa

from melee_engine import behave as B  # noqa: E402
from melee_engine.search import search  # noqa: E402

XR = (0x420, 0, 0, 0, 0, 0, 255)       # X with the shield held
X = (0x400, 0, 0, 0, 0, 0, 0)
A = (0x100, 0, 0, 0, 0, 0, 0)
Z = (0x10, 0, 0, 0, 0, 0, 0)
DTILT = (0x100, 0, -50, 0, 0, 0, 0)
KNEEBEND, NAIR, ATTACK11, CATCH = 24, 65, 44, 212
SHINES = tuple(range(360, 370))
JUMP_SQUAT = {"fox": 3, "marth": 4, "peach": 5}


def offered(n, move):
    """Does the engine's search begin `move` on the coming frame?"""
    r = search(n, 0, 1, horizon=40, budget=0, depth=1, moves=move)
    return any(line.names == move for line in r.lines)


def works(n, pad, test):
    """Pressed on the coming frame (the opponent letting go), does `pad` do
    what `test(state after)` says? Played, and undone."""
    snap = n.snapshot()
    try:
        put(n, 0, pad)
        put(n, 1, NONE)
        n.step()
        return bool(test(n.state()["p"][0]))
    finally:
        n.restore(snap)
        n.drop(snap)


def compare(n, name, hold, move, pad, test, frames=40):
    """From now, a frame at a time (port 0 holding `hold`): the first
    frame `pad` works on and the first the engine offers `move` on (1 the
    coming frame)."""
    real = eng = None
    for s in range(1, frames + 1):
        put(n, 0, hold)
        put(n, 1, NONE)
        if real is None and works(n, pad, test):
            real = s
        put(n, 0, hold)
        if eng is None and offered(n, move):
            eng = s
        if real is not None and eng is not None:
            break
        n.step()
    check("%s: the first frame %s works is the first the engine offers it"
          % (name, move), real is not None and real == eng,
          "the game: frame %s; the engine: frame %s" % (real, eng))
    return real, eng


def shield_stun(n, ch):
    """Fox shielding, `ch`'s down tilt on the shield: from the hit."""
    restart(n, "fox", ch)
    place(n, -8, 0)
    for f in range(60):
        put(n, 0, SHIELD)
        put(n, 1, DTILT if f == 10 else NONE)
        n.step()
        me = n.state()["p"][0]
        if me["state"] == 181:
            return True
    return False


def situations(n):
    for ch in ("marth", "captain-falcon"):
        ok = shield_stun(n, ch)
        if not check("%s's down tilt on Fox's shield: shield stun" % ch, ok):
            continue
        compare(n, "shield stun (%s's down tilt)" % ch, SHIELD, "oos_jump",
                XR, lambda f: f["state"] == KNEEBEND)
    for ch in ("fox", "marth", "peach"):
        # landing lag: a short hop with nothing, landed
        restart(n, ch, "marth" if ch != "marth" else "fox")
        place(n, -30, 40)
        landed = False
        for f in range(80):
            put(n, 0, X if f == 0 else NONE)
            put(n, 1, NONE)
            n.step()
            if n.state()["p"][0]["state"] == 42:
                landed = True
                break
        if check("%s: a short hop's landing lag" % ch, landed):
            compare(n, "%s's landing lag" % ch, NONE, "jab", A,
                    lambda f: f["state"] == ATTACK11)
        # the jump squat into the air: an aerial
        place(n, -30, 40)
        put(n, 0, X)
        put(n, 1, NONE)
        n.step()
        real, eng = compare(n, "%s's jump squat into the air" % ch, NONE,
                            "nair", A, lambda f: f["state"] == NAIR)
        check("%s: the first aerial is on frame J + 1 of the jump" % ch,
              real is not None and real + 1 == JUMP_SQUAT[ch] + 1,
              "frame %s of the jump" % (real + 1 if real else None))
        # a whiffed grab's end
        place(n, -30, 40)
        put(n, 0, Z)
        put(n, 1, NONE)
        n.step()
        if check("%s: a whiffed grab" % ch,
                 n.state()["p"][0]["state"] == CATCH):
            compare(n, "%s's whiffed grab" % ch, NONE, "jump", X,
                    lambda f: f["state"] == KNEEBEND, frames=60)
        # an attack's end (its interruptible frames, or its animation)
        place(n, -30, 40)
        put(n, 0, (0x100, 50, 0, 0, 0, 0, 0))     # forward tilt
        put(n, 1, NONE)
        n.step()
        compare(n, "%s's forward tilt" % ch, NONE, "jump", X,
                lambda f: f["state"] == KNEEBEND, frames=60)


def line_states(n, raws, frames=30):
    """The searching fighter's state after each frame of `raws` played."""
    snap = n.snapshot()
    out = []
    try:
        for i in range(frames):
            put(n, 0, raws[i] if i < len(raws) else NONE)
            put(n, 1, NONE)
            n.step()
            out.append(n.state()["p"][0]["state"])
    finally:
        n.restore(snap)
        n.drop(snap)
    return out


def first_in(states, want):
    return next((i + 1 for i, s in enumerate(states) if s in want), None)


def macros(n):
    restart(n, "fox", "marth")
    place(n, -10, 30)
    for _ in range(12):
        put(n, 0, SHIELD)
        put(n, 1, NONE)
        n.step()
    put(n, 0, SHIELD)
    r = search(n, 0, 1, horizon=40, budget=0, depth=1, moves="oos_down_b")
    line = next((x for x in r.lines if x.names == "oos_down_b"), None)
    at = first_in(line_states(n, line.raw()), SHINES) if line else None
    check("oos_down_b: the shine on frame J + 1 (4) of its jump", at == 4,
          "frame %s" % at)
    for ch in ("fox", "marth"):
        restart(n, ch, "marth" if ch != "marth" else "fox")
        place(n, -10, 40)
        put(n, 0, NONE)
        n.step(3)
        j = JUMP_SQUAT[ch]
        for move, want in (("sh_nair", (NAIR,)), ("wavedash_in", (236, 43))):
            r = search(n, 0, 1, horizon=40, budget=0, depth=1, moves=move)
            line = next((x for x in r.lines if x.names == move), None)
            st = line_states(n, line.raw()) if line else []
            at = first_in(st, want)
            check("%s's %s: on the first airborne frame, J + 1 (%d)" % (
                ch, move, j + 1), at == j + 1, "frame %s: %s" % (
                    at, st[:j + 3]))


def contract(n):
    """The shine out of shield contract, within 4: what it commits to is
    answered by the frame-4 shine it found, played."""
    out, answered, committed = [], 0, 0
    for ch in ("marth", "captain-falcon"):
        restart(n, "fox", ch)
        for gap in (8, 12):
            place(n, -10, -10 + gap)
            put(n, 0, SHIELD)
            put(n, 1, NONE)
            n.step(12)
            snap = n.snapshot()
            for seed in range(2):
                n.restore(snap)
                c = B.Commit("sh_,dash_attack,ftilt,dtilt,fsmash",
                             B.LANDS["shield"], answer="oos_down_b",
                             within=4)
                got = c.find(n, 1, 0, [], SHIELD, random.Random(seed),
                             wide=True)
                if not got.get("ok"):
                    out.append("%s %d/%d: %s" % (ch, gap, seed, got["why"]))
                    continue
                committed += 1
                opp, mine = got["pads"], got["answer"]
                first = B.stun_over(n, 1, 0, opp)
                pct = n.state()["p"][1]["percent"]
                hit = jump = None
                for f in range(len(opp) + 20):
                    put(n, 1, opp[f] if f < len(opp) else NONE)
                    put(n, 0, mine[f] if f < len(mine) else NONE)
                    n.step()
                    s = n.state()
                    if jump is None and s["p"][0]["state"] == KNEEBEND:
                        jump = f + 1
                    if s["p"][1]["percent"] > pct:
                        hit = f + 1
                        break
                frame = hit - first + 1 if hit and first else None
                ok = jump == first and frame == 4
                answered += ok
                out.append("%s %d/%d %s: jump on %s (first free %s), the "
                           "shine hits on frame %s" % (
                               ch, gap, seed, got["line"].names, jump,
                               first, frame))
            n.drop(snap)
    check("contract oos_down_b within 4: every commitment answered by its "
          "frame-4 shine (the jump on the first frame out of shield stun)",
          committed > 0 and answered == committed, "; ".join(out))


def main():
    from native import Native
    with Native() as n:
        situations(n)
        macros(n)
        contract(n)
    return done()


if __name__ == "__main__":
    sys.exit(main())
