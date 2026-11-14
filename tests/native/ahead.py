"""Lookahead on the native build (src/host/ahead.c, tools/melee_actor/ahead.py):
frames played ahead with a planned pad, seen, and undone.

    python tools/native_build.py
    python tests/native/ahead.py
"""
import sys
import time

sys.path.insert(0, "tools/melee_native")
sys.path.insert(0, "tools")
from native import Native, NativeError  # noqa: E402
from melee_actor.ahead import look  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


def row_of(st, a=1, t=0):
    """What a lookahead row holds, from a frame's state."""
    pa, pt = st["p"][a], st["p"][t]
    return (pa["state"], round(pa["x"], 3), round(pa["y"], 3), pa["air"],
            round(pa["percent"], 2), pt["state"], round(pt["x"], 3),
            round(pt["y"], 3), round(pt["percent"], 2))


def main():
    with Native() as n:
        n.start("fox", "marth")
        n.place(0, -10, 0, 1)
        n.place(1, 15, 0, -1)
        for _ in range(5):
            n.step()

        # Marth forward smashes Fox, ahead.
        frame, h0 = n.frame, n.state_hash()
        smash = [(1, dict(cstick=(-1, 0))), (40, {})]
        out = look(n, 1, 0, smash, stop=0)
        check("a lookahead leaves the whole game state as it was",
              n.state_hash() == h0 and n.state()["frame"] == frame,
              "frame %d, %.1f ms for %d frames" % (frame, out.ms,
                                                    len(out.rows)))
        check("it sees the forward smash land", out.contact == "hit",
              repr(out))

        # The same inputs for real: the same frames.
        snap = n.snapshot()
        real = []
        n.pad(1, cstick=(-1, 0))
        n.step()
        real.append(row_of(n.state()))
        n.pad(1)
        for _ in range(40):
            n.step()
            real.append(row_of(n.state()))
        seen = [(r.a_state, round(r.a_x, 3), round(r.a_y, 3), r.a_air,
                 round(r.a_percent, 2), r.t_state, round(r.t_x, 3),
                 round(r.t_y, 3), round(r.t_percent, 2)) for r in out.rows]
        check("what it saw is what then happens, frame for frame",
              seen == real,
              "first difference at frame %s" % next(
                  (i for i, (a, b) in enumerate(zip(seen, real)) if a != b),
                  None))
        n.restore(snap)

        # Everyone else holds their pad: Fox holding shield is seen
        # shielding, and the smash meets the shield.
        n.pad(0, buttons=["R"], r=1.0)
        n.step()
        n.step()
        out = look(n, 1, 0, smash)
        check("the other port keeps holding its pad (a shield, here)",
              out.contact == "shield", repr(out))
        n.pad(0)
        for _ in range(20):
            n.step()

        # stop=1: it ends a frame after the contact.
        out = look(n, 1, 0, smash, stop=1)
        check("stop: it ends the frame after the contact",
              out.contact == "hit" and len(out.rows) == out.frame + 2,
              "contact on %s, %d frames played" % (out.frame,
                                                    len(out.rows)))

        # Nothing out: no hitbox, no contact, no gap.
        out = look(n, 1, 0, [(20, {})])
        check("standing still: no contact and no hitbox",
              out.contact is None and out.gap >= 900, repr(out))

        # Misses say by how much and which way.
        n.place(1, 60, 0, -1)
        n.step()
        out = look(n, 1, 0, smash)
        check("a forward smash from too far misses short",
              out.contact is None and 0 < out.gap < 900 and out.gx < 0,
              repr(out))

        # Errors leave the game where it was.
        h1 = n.state_hash()
        bad = []
        for cmd in ("ahead", "ahead 1 0 0", "ahead 7 0 0 5 0 0 0 0 0 0 0",
                    "ahead 1 0 0 0 0 0 0 0 0 0 0"):
            try:
                n._cmd(cmd)
                bad.append(cmd)
            except NativeError:
                pass
        check("malformed lookaheads are refused, and nothing moves",
              not bad and n.state_hash() == h1, ", ".join(bad))

        # Several in one frame, then play goes on as ever.
        f = n.frame
        for _ in range(5):
            look(n, 1, 0, [(30, dict(stick=(-1, 0)))])
        n.step()
        check("after five lookaheads in a frame, the next tick is the next "
              "frame", n.frame == f + 1, "%d -> %d" % (f, n.frame))

        # In a process restored from a snapshot (rollback's marks are the
        # other process's there).
        snap2 = n.snapshot()
        for _ in range(3):
            n.step()
        n.restore(snap2)
        h2 = n.state_hash()
        out = look(n, 1, 0, smash)
        check("in a process restored from a snapshot it still undoes "
              "everything", n.state_hash() == h2, repr(out))

        # A frame played ahead that would end the scene (here the pause
        # menu's L+R+A+Start): the lookahead stops there, nothing is ended.
        n.pad(0, buttons=["START"])
        n.step()
        n.pad(0)
        for _ in range(10):
            n.step()
        h3 = n.state_hash()
        ended = n.state()["ended"]
        out = look(n, 0, 1, [(1, dict(buttons=["L", "R", "A"])),
                             (30, dict(buttons=["L", "R", "A", "START"],
                                       l=1.0, r=1.0))], stop=0)
        same = n.state_hash() == h3
        n.pad(0, buttons=["START"])
        n.step()
        n.pad(0)
        for _ in range(30):
            n.step()
        check("a lookahead that would end the match stops short and ends "
              "nothing", same and len(out.rows) < 31 and
              n.state()["ended"] == ended and n.fighter(1).fp,
              "%d of 31 frames played, match ended %s -> %s" % (
                  len(out.rows), ended, n.state()["ended"]))

        # What it costs.
        t = time.perf_counter()
        for _ in range(20):
            look(n, 1, 0, [(30, {})], stop=0)
        each = (time.perf_counter() - t) * 1000 / 20
        check("a 30-frame lookahead costs a few milliseconds", each < 10,
              "%.1f ms" % each)

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
