"""The opponent's moves (docs/ai/opponent-vocabulary.md, layer 1): each
macro src/host/engine.c gained for it, played from where it applies, for
several characters, and the game's own action states checked. Then the
search with them: a pivot found that hits a standing target, and a grab,
a throw and a regrab before the thrown Fox can act.

    python tools/native_build.py
    python tests/native/engine_moves.py

Headless; every loop is bounded (a line's own frames, or a fixed count).
"""
import sys
import time

sys.path.insert(0, "tools/melee_native")
sys.path.insert(0, "tools")
from native import Native  # noqa: E402
from melee_course.engine import (  # noqa: E402
    ATTACK11, ATTACK_DASH, ATTACK_HI3, ATTACK_HI4, ATTACK_LW3, ATTACK_LW4,
    CATCH, CATCH_DASH, DASH, ESCAPE_AIR, GUARD_ON, GUARD_REFLECT,
    JUMP_AERIAL_B, JUMP_F, KNEEBEND, LANDING_FALL_SPECIAL, RUN, SQUAT,
    SQUAT_WAIT, TURN)
from melee_engine.search import search  # noqa: E402

PASS = 244                   # dropping through a platform
ATTACK_S3 = range(51, 56)    # ftilt, its five angles
ATTACK_S4 = range(58, 63)    # fsmash, its five angles
CAPTURED = range(223, 229)   # held: pulled, waiting, pummelled
THROWN = range(239, 244)     # thrown: forward, back, up, down
# a character's own action states start here (Peach's forward smash, Game
# & Watch's jab, forward smash and down tilt are their own)
OWN_STATES = 341
# what a victim mashing jump does at its first chance: a jump squat, a
# jump, a double jump, an air dodge, or a state that can act
ACTED = {KNEEBEND, JUMP_F, JUMP_F + 1, JUMP_AERIAL_B - 1, JUMP_AERIAL_B,
         ESCAPE_AIR, 14, 15, 16, 17, 18, 20, 21, 39, 40, 41}
PLATFORM_Y = 27.2            # Battlefield's side platforms
slides = {}                  # each waveland's slide, by character
CHARACTERS = ["fox", "marth", "sheik", "captain-falcon", "peach",
              "jigglypuff"]
# the pivot drill's measured characters besides: pivots only
PIVOT_ALSO = ["mewtwo", "mr-game-and-watch", "bowser"]
# the state each pivot's attack is in (PIVOT_NAME in engine.c)
PIVOTS = [("jab", (ATTACK11,)), ("ftilt", ATTACK_S3), ("fsmash", ATTACK_S4),
          ("utilt", (ATTACK_HI3,)), ("usmash", (ATTACK_HI4,)),
          ("dtilt", (ATTACK_LW3,)), ("dsmash", (ATTACK_LW4,)),
          ("grab", (CATCH,))]

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))
    sys.stdout.flush()


def setraw(n, port, raw):
    b, lx, ly, cx, cy, lt, rt = raw
    n.h.pads[port].update(buttons=b, lx=lx, ly=ly, cx=cx, cy=cy, lt=lt,
                          rt=rt, connected=True)
    n._dirty.add(port)


def play(n, port, raws, other=None, after=0):
    """Play raw pads for real (then `after` neutral frames): each frame's
    (port's fighter, the other's). `other(i)`: the other port's raw pad on
    frame i (else it holds its own)."""
    rec = []
    for i, raw in enumerate(list(raws) + [(0, 0, 0, 0, 0, 0, 0)] * after):
        setraw(n, port, raw)
        if other is not None:
            setraw(n, 1 - port, other(i))
        n.step()
        rec.append((n.fighter(port), n.fighter(1 - port)))
    n.pad(port)
    if other is not None:
        n.pad(1 - port)
    return rec


def line_of(n, port, name, horizon=120, **kw):
    """The line of macro `name` alone, as the search plays it."""
    r = search(n, port, 1 - port, horizon=horizon, budget=0, depth=1,
               moves=name, **kw)
    return next((ln for ln in r.lines if ln.names == name), None)


def states(rec):
    return [f.state for f, _ in rec]


def runs(rec):
    """The states in order, repeats merged: [(state, frames, facing)]."""
    out = []
    for f, _ in rec:
        if out and out[-1][0] == f.state:
            out[-1][1] += 1
        else:
            out.append([f.state, 1, f.facing])
    return out


def fmt(seq):
    return " ".join("%d:%d" % (s, k) for s, k, _ in seq)


# ---- pivots ---------------------------------------------------------------


def pivots(n, ch, snap):
    """Every pivot from standing, facing the target 60 units away: a dash
    out (facing away), the turn, the attack facing the target; no dash
    back, no run. Short: 4 frames of dash (the first a reversal turns);
    long: the dash's last frame (one frame more held is a run)."""
    bad, lens = [], {}
    for attack, want in PIVOTS:
        for longest in (0, 1):
            name = "pivot_%s%s" % (attack, "_long" if longest else "")
            n.restore(snap)
            ln = line_of(n, 0, name)
            if ln is None:
                bad.append(name + ": no line")
                continue
            raws = ln.raw()
            rec = play(n, 0, raws)
            seq = runs(rec)
            st = states(rec)
            dash = sum(1 for f, _ in rec if f.state == DASH and
                       f.facing < 0)
            # the pivot's turn: the one out of the dash away (from
            # standing facing the target, the dash out starts with a turn
            # of its own)
            turn = next((i for i in range(1, len(rec))
                         if st[i] == TURN and st[i - 1] == DASH and
                         rec[i - 1][0].facing < 0), -1)
            hit = next((i for i in range(max(turn, 0), len(st))
                        if st[i] in want or st[i] >= OWN_STATES), -1)
            ok = ((dash > 4 if longest else dash == 4) and turn > 0 and
                  hit == turn + 1 and
                  rec[hit][0].facing > 0 and RUN not in st and
                  DASH not in st[turn:] and
                  raws[turn][1] >= 100 and abs(raws[turn + 1][1]) < 64)
            if ok and longest:
                # one frame more of the dash held instead of the flick: a
                # run (the dash was at its last frame)
                n.restore(snap)
                r2 = play(n, 0, raws[:turn] + [raws[turn - 1]])
                ok = r2[-1][0].state == RUN
            lens.setdefault(longest, set()).add(dash)
            if not ok:
                bad.append("%s: %s" % (name, fmt(seq)))
    return bad, lens


def pivot_facts(n, snap, away):
    """The pivot drill's facts, on the short pivot jab: held full for a
    second frame, the flick is a dash back; and out of a dash forward
    (`away`: standing facing away from the target), it flicks on the first
    frame a reversal turns: 4 frames of dash, one fewer and the flick does
    nothing."""
    bad = []
    n.restore(snap)
    ln = line_of(n, 0, "pivot_jab")
    raws = ln.raw()
    rec = play(n, 0, raws)
    st = states(rec)
    turn = next(i for i in range(1, len(st))
                if st[i] == TURN and st[i - 1] == DASH)
    n.restore(snap)
    r2 = play(n, 0, raws[:turn + 1] + [raws[turn]])
    if r2[-1][0].state != DASH or r2[-1][0].facing < 0:
        bad.append("the flick held 2 frames: %s" % fmt(runs(r2)))
    n.restore(away)
    ln = line_of(n, 0, "pivot_jab")
    raws = ln.raw()
    rec = play(n, 0, raws)
    st = states(rec)
    turn = next((i for i in range(1, len(st))
                 if st[i] == TURN and st[i - 1] == DASH), -1)
    dash = sum(1 for s in st[:max(turn, 0)] if s == DASH)
    if turn < 0 or dash != 4 or st[0] != DASH:
        bad.append("out of a dash forward: %s" % fmt(runs(rec)))
    else:
        n.restore(away)
        r2 = play(n, 0, raws[:turn - 1] + [raws[turn]])
        if r2[-1][0].state != DASH:
            bad.append("flicked a frame earlier: %s" % fmt(runs(r2)))
    return bad


# ---- the dash moves -------------------------------------------------------


def dash_moves(n, ch, snap, run_snap, dash_snap):
    """dash_grab from standing, a dash and a run; jc_grab and jc_usmash a
    standing grab and up smash out of a jump squat, on the ground, sliding;
    boost_grab a dash attack into a dash grab; dash_dance out and back."""
    bad = []
    for where, s in (("standing", snap), ("dash", dash_snap),
                     ("run", run_snap)):
        n.restore(s)
        ln = line_of(n, 0, "dash_grab")
        rec = play(n, 0, ln.raw()) if ln else []
        st = states(rec)
        if CATCH_DASH not in st or rec[st.index(CATCH_DASH)][0].facing < 0:
            bad.append("dash_grab from %s: %s" % (where, fmt(runs(rec))))
        for jc, want in (("jc_grab", CATCH), ("jc_usmash", ATTACK_HI4)):
            n.restore(s)
            ln = line_of(n, 0, jc)
            rec = play(n, 0, ln.raw()) if ln else []
            st = states(rec)
            at = st.index(want) if want in st else -1
            ok = (at > 0 and st[at - 1] == KNEEBEND and
                  not any(f.airborne for f, _ in rec) and
                  rec[at][0].facing > 0 and
                  rec[min(at + 2, len(rec) - 1)][0].pos[0] >
                  rec[at][0].pos[0])
            if not ok:
                bad.append("%s from %s: %s" % (jc, where, fmt(runs(rec))))
        n.restore(s)
        ln = line_of(n, 0, "boost_grab")
        rec = play(n, 0, ln.raw()) if ln else []
        st = states(rec)
        at = st.index(CATCH_DASH) if CATCH_DASH in st else -1
        if at <= 0 or st[at - 1] != ATTACK_DASH:
            bad.append("boost_grab from %s: %s" % (where, fmt(runs(rec))))
    n.restore(snap)
    ln = line_of(n, 0, "dash_dance")
    rec = play(n, 0, ln.raw()) if ln else []
    seq = [(s, f) for s, _, f in runs(rec)]
    out = next((i for i, (s, f) in enumerate(seq) if s == DASH and f < 0),
               -1)
    back = next((i for i, (s, f) in enumerate(seq)
                 if i > out and s == DASH and f > 0), -1)
    if out < 0 or back < 0 or RUN in states(rec):
        bad.append("dash_dance: %s" % fmt(runs(rec)))
    return bad


def boost_window(n, snap):
    """Which frames after a dash attack's A a Z turns it into a dash grab
    (dash attack on the dash's 6th frame)."""
    got = []
    for j in range(1, 7):
        n.restore(snap)
        raws = [(0, 127, 0, 0, 0, 0, 0)] * 5 + [(0x100, 127, 0, 0, 0, 0, 0)]
        raws += [(0, 127, 0, 0, 0, 0, 0)] * (j - 1) + \
            [(0x10, 127, 0, 0, 0, 0, 0)]
        rec = play(n, 0, raws, after=2)
        if CATCH_DASH in states(rec):
            got.append(j)
    return got


# ---- the stick down, platforms ---------------------------------------------


def downs(n, ch):
    """crouch on the stage and on a platform (not through it);
    platform_drop through; the three wavelands onto the platform from the
    air and, after a drop, onto the stage below."""
    bad = []
    n.start(ch, "fox", stage="battlefield")
    n.place(1, 40, 0, -1)
    n.place(0, -60, 0, 1)
    n.step(3)
    ln = line_of(n, 0, "crouch")
    rec = play(n, 0, ln.raw()) if ln else []
    if not rec or rec[-1][0].state not in (SQUAT, SQUAT_WAIT):
        bad.append("crouch: %s" % fmt(runs(rec)))
    n.place(0, -39, 40, 1)
    n.step(3)
    plat = n.snapshot()
    ln = line_of(n, 0, "crouch")
    rec = play(n, 0, ln.raw()) if ln else []
    if not rec or rec[-1][0].state not in (SQUAT, SQUAT_WAIT) or \
            PASS in states(rec) or abs(rec[-1][0].pos[1] - PLATFORM_Y) > 0.1:
        bad.append("crouch on a platform: %s" % fmt(runs(rec)))
    n.restore(plat)
    ln = line_of(n, 0, "platform_drop")
    rec = play(n, 0, ln.raw(), after=4) if ln else []
    if PASS not in states(rec) or rec[-1][0].pos[1] >= PLATFORM_Y - 1:
        bad.append("platform_drop: %s" % fmt(runs(rec)))
    # a drop, then a waveland onto the stage below (the search's line)
    n.restore(plat)
    r = search(n, 0, 1, horizon=120, budget=2000, depth=2,
               moves="platform_drop", then="waveland_in")
    ln = next((x for x in r.lines if x.names == "platform_drop+waveland_in"),
              None)
    land = wavelanded(n, ln, 0.0)
    if land is None:
        bad.append("platform_drop+waveland_in: %s" % (
            ln.names if ln else "no line"))
    n.drop(plat)
    # in the air above the platform: each waveland lands on it, sliding
    # in, out or not at all
    for name, sign in (("waveland_in", 1), ("waveland_out", -1),
                       ("waveland", 0)):
        n.place(0, -39, 50, 1, air=True)
        n.step()
        x0 = n.fighter(0).pos[0]
        ln = line_of(n, 0, name)
        land = wavelanded(n, ln, PLATFORM_Y)
        ok = land is not None
        if ok:
            dx = land[-1][0].pos[0] - x0
            ok = (dx > 2) if sign > 0 else (dx < -2) if sign < 0 else \
                abs(dx) < 2
        if not ok:
            bad.append("%s: %s" % (name, fmt(runs(land)) if land else
                                   "no waveland"))
        else:
            slides.setdefault(name, []).append(round(dx, 1))
    return bad


def wavelanded(n, ln, floor):
    """Play a line that ends in a waveland: in the air from its first
    airborne frame until its air dodge (R), then only the dodge until its
    landing lag on `floor`. The
    record, or None. (A dodge pressed on the last frame before landing
    lands on its own frame: no EscapeAir frame in between.)"""
    if ln is None:
        return None
    raws = ln.raw()
    rec = play(n, 0, raws)
    st = states(rec)
    dodge = next((i for i, r in enumerate(raws) if r[0] & 0x20), -1)
    land = next((i for i in range(max(dodge, 0), len(st))
                 if st[i] == LANDING_FALL_SPECIAL), -1)
    air = next((i for i, (f, _) in enumerate(rec) if f.airborne), -1)
    if dodge < 1 or land < dodge or air < 0 or air >= dodge or \
            not all(f.airborne for f, _ in rec[air:dodge]) or \
            any(s != ESCAPE_AIR for s in st[dodge:land]) or \
            abs(rec[land][0].pos[1] - floor) > 0.1:
        return None
    return rec


# ---- the search with them ------------------------------------------------------


def pivot_search(n, ch, gap):
    """moves=pivot_ against a standing target `gap` away: a pivot line that
    hits, which played for real does what it was scored with; and the
    timing scan (hold=out then=pivot_fsmash) finds dash lengths that hit."""
    n.place(0, -gap / 2.0, 0, 1)
    n.place(1, gap / 2.0, 0, -1)
    n.step(3)
    s = n.snapshot()
    r = search(n, 0, 1, horizon=90, budget=0, depth=1, moves="pivot_",
               hit=50)
    hits = [ln for ln in r.lines if ln.contact == "hit"]
    best = hits[0] if hits else None
    same = False
    if best is not None:
        pct = n.fighter(1).percent
        rec = play(n, 0, best.raw())
        same = abs((rec[-1][1].percent - pct) - best.dmg) < 0.01
    n.restore(s)
    sc = search(n, 0, 1, horizon=90, budget=0, depth=1, scan=1, hold="out",
                then="pivot_fsmash", hit=50, stop=1)
    ks = sorted(set(int(ln.moves[0].split(":")[1]) for ln in sc.lines
                    if ln.contact == "hit" and
                    ln.moves[-1] == "pivot_fsmash"))
    n.drop(s)
    return hits, best, same, ks


def chain_grab(n, thrower, victim, pct, x=0.0):
    """grab, a throw, a regrab: the lines the search finds (depth 4: the
    regrab the third move, or the fourth after a wait), each played for
    real twice: as searched (the victim holding still), and with the victim
    pressing a jump button anew on every frame from the throw's release
    (X and Y in turn: a jump on its first frame able to act). A chain grab:
    regrabbed on the same frame both times, and never in a jump squat, a
    jump, a shield, an air dodge or a state that can act before it."""
    n.start(thrower, victim)
    n.place(0, x - 6, 0, 1, percent=0)
    n.place(1, x + 6, 0, -1, percent=pct)
    n.step(3)
    s = n.snapshot()
    regrabs = "grab,dash_grab,jc_grab,pivot_grab"
    r = search(n, 0, 1, horizon=200, budget=60000, depth=4, moves="grab",
               then="fthrow,bthrow,uthrow,dthrow,wait," + regrabs, split=4)
    found = []
    for ln in r.lines:
        m = ln.moves
        if len(m) < 3 or not m[1].endswith("throw") or \
                m[-1] not in regrabs.split(",") or \
                any(w != "wait" for w in m[2:-1]):
            continue
        n.restore(s)
        rec = play(n, 0, ln.raw(), after=12)
        vs = [v.state for _, v in rec]
        rel = next((i for i in range(1, len(vs)) if vs[i - 1] in THROWN and
                    vs[i] not in THROWN), -1)
        caught = next((i for i in range(max(rel, 0), len(vs))
                       if vs[i] in CAPTURED), -1)
        if rel < 0 or caught < 0:
            continue
        n.restore(s)
        rec = play(n, 0, ln.raw(), after=12, other=lambda i: (
            (0x400 if i % 2 else 0x800) if i >= rel else 0,
            0, 0, 0, 0, 0, 0))
        vs = [v.state for _, v in rec]
        caught2 = next((i for i in range(rel, len(vs)) if vs[i] in CAPTURED),
                       -1)
        acted = sorted(set(v for v in vs[rel:caught2 if caught2 > 0 else None]
                           if v in ACTED or GUARD_ON <= v <= GUARD_REFLECT))
        left = rec[caught2 - 1][1].hitstun if caught2 > 0 else -1
        found.append((ln, rel, caught, caught2, acted, left))
    n.drop(s)
    return r, found


def main():
    t0 = time.time()
    with Native() as n:
        for ch in CHARACTERS + PIVOT_ALSO:
            n.start(ch, "fox")
            n.place(1, 40, 0, -1)
            n.place(0, -20, 0, 1)
            n.step(3)
            snap = n.snapshot()
            bad, lens = pivots(n, ch, snap)
            check("%s: the 16 pivots: a dash out, the turn, the attack the "
                  "frame after it facing the target, no dash back or run; "
                  "the long dash the last before a run" % ch, not bad,
                  "; ".join(bad) if bad else
                  "dash frames before the turn: short %s, long %s" % (
                      sorted(lens.get(0, ())), sorted(lens.get(1, ()))))
            n.place(0, -20, 0, -1)
            n.step(3)
            away = n.snapshot()
            bad = pivot_facts(n, snap, away)
            n.drop(away)
            check("%s: the flick held a second frame is a dash back; out of "
                  "a dash forward the short pivot flicks after 4 frames, "
                  "and a frame earlier the flick does nothing" % ch, not bad,
                  "; ".join(bad))
            if ch in PIVOT_ALSO:
                n.drop(snap)
                continue
            n.restore(snap)
            play(n, 0, [(0, 127, 0, 0, 0, 0, 0)] * 8)
            dash_snap = n.snapshot()
            n.restore(snap)
            play(n, 0, [(0, 127, 0, 0, 0, 0, 0)] * 24)
            run_snap = n.snapshot()
            ok_run = n.fighter(0).state == RUN
            bad = dash_moves(n, ch, snap, run_snap, dash_snap)
            check("%s: dash_grab a dash grab, jc_grab and jc_usmash a "
                  "standing grab and up smash out of the jump squat, "
                  "sliding, boost_grab a dash attack into a dash grab, from "
                  "standing, a dash and a run; dash_dance out and back" % ch,
                  not bad and ok_run, "; ".join(bad))
            win = boost_window(n, snap)
            check("%s: the boost grab's Z grabs on frames %s after the dash "
                  "attack's A (the macro presses it on the 1st)" % (
                      ch, ",".join(map(str, win))), 1 in win)
            for s in (snap, dash_snap, run_snap):
                n.drop(s)
            bad = downs(n, ch)
            check("%s: crouch on the stage and on a platform (not through "
                  "it), platform_drop through it, the wavelands land in "
                  "their landing lag on the platform (in, out, straight) "
                  "and on the stage after a drop" % ch, not bad,
                  "; ".join(bad))

        for ch in CHARACTERS:
            n.start(ch, "fox")
            hits, best, same, ks = pivot_search(n, ch, 10)
            check("%s: a search with moves=pivot_ against a standing Fox 10 "
                  "away finds pivots that hit, the best played for real as "
                  "scored; the scan (hold=out then=pivot_fsmash) finds the "
                  "dash lengths a pivot fsmash hits from" % ch,
                  hits and same and ks,
                  "%d of 16 hit (%s), best %r; hold_out:K for K in %s" % (
                      len(hits), ",".join(h.names[6:] for h in hits), best,
                      ks))

        r, found = chain_grab(n, "marth", "fox", 0)
        good = [f for f in found if f[3] == f[2] and not f[4]]
        check("Marth on Fox at 0%: the search (depth 4, then= the throws, "
              "wait and the four ground grabs) finds grab, a throw, a "
              "regrab; with Fox jumping from the release on, the regrab "
              "still comes before he can act",
              good, "%d lines regrab as searched, %d also against the "
              "jumps; %d ms" % (len(found), len(good), r.ms))
        for ln, rel, caught, caught2, acted, left in found:
            print("      %-26s released %d, regrabbed %d; jumping: %s" % (
                ln.names, rel, caught,
                "regrabbed %d, %d frames of hitstun left" % (caught2, left)
                if caught2 == caught and not acted else
                "acted first (states %s)" % ",".join(map(str, acted))))

    print("      waveland slides on the platform (units, by character): "
          + "; ".join("%s %s" % (k, v) for k, v in sorted(slides.items())))
    print("%d of %d checks passed (%.0f s)" % (sum(checks), len(checks),
                                                time.time() - t0))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
