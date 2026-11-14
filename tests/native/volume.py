"""The player's volumes on the native window build: music and sound
effects mixed apart, each with its own volume, outside the game's state.

    python tools/native_build.py --window && python tests/native/volume.py

The mix goes to a file (MELEE_AUDIO_RAW) as well as to a sound device that
does not exist (the virtual display's: nothing reaches a speaker). With
the main menu's music playing: the music at 0 is silence, at 50 about half
as loud as at 100; a menu sound with the music at 0 is heard, and with the
effects at 0 is not.
"""
import math
import os
import struct
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
import native  # noqa: E402
import window  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def rms(path, start):
    """Loudness of the mix from byte `start` on (16-bit stereo)."""
    with open(path, "rb") as f:
        f.seek(start)
        data = f.read()
    n = len(data) // 2
    if n == 0:
        return 0.0
    s = struct.unpack("<%dh" % n, data[:n * 2])
    return math.sqrt(sum(x * x for x in s) / n)


def main():
    raw = os.path.join(tempfile.mkdtemp(prefix="melee-vol-"), "mix.raw")
    with window.Window(sound_file=raw) as w:
        check("full volume unless asked", w.volume() == (100, 100),
              str(w.volume()))
        w.bgm(native.SONGS.index(native.MENU_SONG))
        w.step(120)                      # the stream's first blocks

        def listen(music, sound, frames=90, sfx=None):
            w.volume(music, sound)
            w.step(2)
            start = os.path.getsize(raw)
            if sfx is not None:
                w.sfx(sfx)
            w.step(frames)
            return rms(raw, start)

        loud = listen(100, 100)
        half = listen(50, 100)
        none = listen(0, 100)
        check("the menu's music plays at full volume", loud > 300,
              "%.0f" % loud)
        check("at 50 it is about half as loud",
              0.35 < half / max(loud, 1) < 0.65,
              "%.0f against %.0f" % (half, loud))
        check("at 0 the music is silent", none < 5, "%.0f" % none)
        beep = listen(0, 100, frames=20, sfx=1)
        check("a menu sound is heard with the music at 0", beep > 50,
              "%.0f" % beep)
        quiet = listen(0, 0, frames=20, sfx=1)
        check("and not with the effects at 0 too", quiet < 5,
              "%.0f" % quiet)
        w.volume(100, 100)
        check("the volumes are kept between 0 and 100",
              w.volume(150, -20) == (100, 0), str(w.volume()))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
