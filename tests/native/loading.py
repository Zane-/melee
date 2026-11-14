"""Changing a situation the way TM-CE does, without loading: the opponent
swapped in place, the last attempt cleaned away, and a load nobody hears.

    python tools/native_build.py
    python tests/native/loading.py

- A match loads the other opponents a drill needs with it (`match ...
  CK...`, the overlay's character rotation in src/melee/tm/rotation): four
  fighters in all. `swap` makes the opponent one of them in one frame, no
  new match; its pad still drives it; a character not loaded is refused.
- `clean` (TM-CE's savestate load, src/host/setup.c): a laser in flight is
  gone but not the blaster Fox still holds (destroying that under him
  crashed the game), and a move staled by repeated hits hits as hard as at
  first again.
- `quiet`: a match loaded in a quiet stretch writes only the stretch's first
  150 ms of sound, and the music the new match started begins again from
  its start when the stretch ends (src/host/audio.c).
"""
import array
import math
import os
import sys
import tempfile

sys.path.insert(0, "tools/melee_native")
from native import Native, NativeError  # noqa: E402

checks = []
JUMPSQUAT = 24
BLASTER, LASER = 74, 54   # item kinds: Fox's blaster, its shot
TAIL_BYTES = 30 * 160 * 4  # 150 ms of 16-bit stereo at 32 kHz


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


def jab_damage(n, clean):
    """Fox's jab on Marth, from the same placement: the damage it does."""
    if clean:
        n.clean()
    n.pad(0)
    n.pad(1)
    n.place(0, -8.0, 0.0, facing=1)
    n.place(1, 8.0, 0.0, facing=-1, percent=0.0)
    n.step(2)
    n.pad(0, buttons=["A"])
    n.step(2)
    n.pad(0)
    n.step(30)
    return n.fighter(1).percent


def main():
    deck = ["sheik", "captain-falcon", "peach", "falco", "jigglypuff"]
    raw = os.path.join(tempfile.mkdtemp(prefix="melee-sound-"), "out.raw")
    env = dict(os.environ, MELEE_AUDIO_RAW=raw)
    with Native(env=env) as n:
        n.start("fox", "marth", "final-destination", seed=7, preload=deck)
        loaded = n.loaded()
        check("a match loads the deck's other opponents, four fighters in "
              "all", loaded[:2] == ["fox", "marth"] and len(loaded) == 4 and
              all(c in deck for c in loaded[2:]), ", ".join(loaded))
        matches = n.state()["match"]
        names = {v: k for k, v in __import__("native").CHARACTERS.items()}
        for c in loaded[2:] + ["marth"]:
            f0 = n.frame
            changed = n.swap(1, c)
            n.place(1, 20.0, 0.0, facing=-1)
            n.step()
            f = n.fighter(1)
            check("swap to %s: in one frame, no new match" % c,
                  changed and names.get(f.ckind) == c and
                  n.frame - f0 == 1 and n.state()["match"] == matches,
                  "%s, %d frame(s)" % (names.get(f.ckind), n.frame - f0))
            n.pad(1, buttons=["X"])
            n.step(2)
            n.pad(1)
            state = n.fighter(1).state
            n.step(60)
            check("and its pad drives it (a jump)", state == JUMPSQUAT or
                  n.fighter(1).airborne, "state %d" % state)
        try:
            n.swap(1, "pikachu")
            refused = False
        except NativeError:
            refused = True
        check("a character not loaded is refused", refused)
        check("the same match all along", n.state()["match"] == matches)

        # ---- clean ---------------------------------------------------------
        n.place(0, -40.0, 0.0, facing=1)
        n.place(1, 60.0, 0.0, facing=-1)
        n.step(2)
        n.pad(0, buttons=["B"])                  # Fox's laser
        n.step(4)
        n.pad(0)
        n.step(10)
        before = sorted(i["kind"] for i in n.state()["items"])
        n.clean()                                # Fox still holds his blaster
        n.step()
        after = sorted(i["kind"] for i in n.state()["items"])
        check("clean: the laser in flight is gone, the blaster Fox holds "
              "is not", LASER in before and BLASTER in before and
              after == [BLASTER], "%s -> %s" % (before, after))
        n.place(0, -40.0, 0.0, facing=1)
        n.step(3)
        gone = not n.state()["items"]
        n.pad(0, buttons=["B"])
        n.step(4)
        n.pad(0)
        n.step(60)
        check("and lets it go itself once he stands; he fires again",
              gone and n.fighter(0).state == 14, "items %s, state %d" % (
                  n.state()["items"], n.fighter(0).state))
        first = jab_damage(n, clean=True)
        for _ in range(3):
            staled = jab_damage(n, clean=False)
        again = jab_damage(n, clean=True)
        check("clean: a staled move hits as hard as at first again",
              first > 0 and staled < first and abs(again - first) < 1e-4,
              "%.2f%%, staled %.2f%%, after clean %.2f%%" % (
                  first, staled, again))

        # ---- quiet ---------------------------------------------------------
        n.step(30)
        before = os.path.getsize(raw)
        n.quiet(True)
        n.start("fox", "sheik", "battlefield", seed=3)
        during = os.path.getsize(raw) - before
        n.quiet(False)
        check("quiet: a match loads hearing only the first 150 ms",
              during == TAIL_BYTES, "%d bytes written, the tail is %d" % (
                  during, TAIL_BYTES))
        song = n.song()
        frames = n.frame
        n.step(120)
        after = os.path.getsize(raw) - before - during
        check("and the sound goes on in real time after it",
              abs(after - (n.frame - frames) * 32000 * 4 / 59.94) < 2000,
              "%d bytes in %d frames" % (after, n.frame - frames))
        with open(raw, "rb") as f:
            f.seek(before + during)
            pcm = array.array("h", f.read())
        loud = math.sqrt(sum(v * v for v in pcm) / max(1, len(pcm)))
        check("with the new match's music playing", song not in (
            None, "menu01.hps") and loud > 300, "%s, level %.0f" % (
                song, loud))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
