"""Sound in the native build, checked against the game's own data.

    python tests/native/audio.py

The native build mixes the game's sound itself (src/host/audio.c: the AX
voices, DSP-ADPCM, the stereo mix). Run headless with the mix written to a
file (MELEE_AUDIO_RAW), this checks:

- the main menu's music (menu01.hps), as the game streams it block by
  block, is the file's samples: compared with an independent decoder of
  the format written here, after finding where the music starts (the
  game's own volume and pan scale it; the correlation shows the shape);
- a menu sound plays when the game is asked for one, and stops;
- a match makes sound (its music, and the sounds of fighters moving);
- headless without the file, the game is as it was (no sound mixed).

No sound reaches a speaker: headless has none.
"""
import math
import os
import struct
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))

from native import Native  # noqa: E402

RATE = 32000
checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


# ---- an independent decoder of a music stream (.hps) -------------------------

def decode_hps(path, seconds):
    """The first `seconds` of a .hps stream, one list of samples per
    channel. The format: a 0x80-byte header (" HALPST", rate, channels,
    then per channel 0x38 bytes: AX address settings and the ADPCM
    coefficients at +0x10), then blocks from 0x80: a 0x20-byte header
    (data size for all channels, the last nibble of a channel, the next
    block's offset, each channel's starting predictor and history) and the
    channels' data one after the other, in 8-byte DSP-ADPCM frames."""
    d = open(path, "rb").read()
    rate, chans = struct.unpack(">II", d[8:16])
    coefs = [struct.unpack(">16h", d[0x10 + 0x38 * c + 0x10:
                                     0x10 + 0x38 * c + 0x30])
             for c in range(chans)]
    out = [[] for _ in range(chans)]
    want = int(seconds * rate)
    at = 0x80
    while at != 0xFFFFFFFF and len(out[0]) < want:
        size, end, nxt = struct.unpack(">III", d[at:at + 12])
        per = size // chans
        for c in range(chans):
            _, yn1, yn2 = struct.unpack(">Hhh", d[at + 12 + 8 * c:
                                                  at + 18 + 8 * c])
            data = d[at + 0x20 + c * per: at + 0x20 + (c + 1) * per]
            nibbles = end + 1
            for f in range(0, nibbles // 16 + 1):
                frame = data[f * 8:f * 8 + 8]
                if len(frame) < 1:
                    break
                ps = frame[0]
                scale = 1 << (ps & 15)
                c1, c2 = coefs[c][2 * (ps >> 4 & 7)], coefs[c][
                    2 * (ps >> 4 & 7) + 1]
                for k in range(14):
                    nib_addr = f * 16 + 2 + k
                    if nib_addr > end:
                        break
                    byte = frame[1 + k // 2] if 1 + k // 2 < len(frame) \
                        else 0
                    nib = (byte >> 4) if k % 2 == 0 else (byte & 15)
                    if nib >= 8:
                        nib -= 16
                    v = ((nib * scale) << 11) + c1 * yn1 + c2 * yn2
                    v = (v + 1024) >> 11
                    v = max(-32768, min(32767, v))
                    yn2, yn1 = yn1, v
                    out[c].append(v)
        at = nxt
    return [ch[:want] for ch in out]


def read_raw(path):
    data = open(path, "rb").read()
    s = struct.unpack("<%dh" % (len(data) // 2), data)
    return list(s[0::2]), list(s[1::2])


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / max(1, len(xs)))


def correlation(a, b):
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    ma, mb = sum(a) / n, sum(b) / n
    sab = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return sab / (sa * sb) if sa and sb else 0.0


def first_sound(xs, level=200):
    for i, x in enumerate(xs):
        if abs(x) > level:
            return i
    return None


def main():
    tmp = tempfile.mkdtemp(prefix="melee-audio-")
    raw = os.path.join(tmp, "menu.raw")
    hps = os.path.join(ROOT, "build", "disc", "files", "audio", "menu01.hps")

    # ---- the main menu's music, against the file -------------------------
    with Native(env=dict(os.environ, MELEE_AUDIO_RAW=raw)) as n:
        n.step(30)
        before = os.path.getsize(raw)
        n.bgm(52)
        n.step(60 * 5)
        n.bgm(-1)
        n.step(150)                  # it fades out
    left, right = read_raw(raw)
    start = first_sound(left[before // 4:])
    check("the music starts", start is not None, "")
    ref = decode_hps(hps, 4.5)
    if start is not None:
        start += before // 4
        # where exactly: the best match of the reference's first 0.2 s
        # around the first sound
        probe = ref[0][2000:8400]
        best, lag = -2.0, 0
        for d in range(start - 2400, start + 2400):
            if d < 0:
                continue
            seg = left[d + 2000:d + 2000 + len(probe)]
            if len(seg) < len(probe):
                break
            r = correlation(probe[::4], seg[::4])
            if r > best:
                best, lag = r, d
        seg_l = left[lag:lag + RATE * 4]
        seg_r = right[lag:lag + RATE * 4]
        cl = correlation(ref[0][:RATE * 4], seg_l)
        cr = correlation(ref[1][:RATE * 4], seg_r)
        ratio = rms(seg_l) / max(1.0, rms(ref[0][:RATE * 4]))
        check("its first four seconds are the file's samples, block after "
              "block (both channels)", cl > 0.99 and cr > 0.99,
              "correlation left %.4f, right %.4f, level %.2f of the file's"
              % (cl, cr, ratio))
        tail = left[-RATE // 2:]
        check("and stopping the music fades it to silence", rms(tail) < 50,
              "rms %.0f two seconds later" % rms(tail))

    # ---- a menu sound ------------------------------------------------------
    raw = os.path.join(tmp, "sfx.raw")
    with Native(env=dict(os.environ, MELEE_AUDIO_RAW=raw)) as n:
        n.step(30)
        quiet = os.path.getsize(raw)
        n.sfx(2)                     # choosing something in a menu
        n.step(60)
    left, right = read_raw(raw)
    after = left[quiet // 4:]
    peak = max(abs(x) for x in after[:RATE // 2])
    check("a menu sound plays when the game is asked for one",
          peak > 2000, "peak %d in the first half second, rms %.0f" % (
              peak, rms(after[:RATE // 2])))
    check("and ends", rms(after[-RATE // 4:]) < 50,
          "rms %.0f a second later" % rms(after[-RATE // 4:]))

    # ---- a match -----------------------------------------------------------
    raw = os.path.join(tmp, "match.raw")
    with Native(env=dict(os.environ, MELEE_AUDIO_RAW=raw)) as n:
        n.start("fox", "marth", "final-destination", 1)
        n.step(120)
        for _ in range(4):
            n.pad(0, buttons=["X"])
            n.step(2)
            n.pad(0)
            n.step(40)
    left, right = read_raw(raw)
    check("a match makes sound", rms(left[-RATE * 2:]) > 500,
          "rms %.0f over its last two seconds" % rms(left[-RATE * 2:]))

    # ---- headless without the file: nothing mixed --------------------------
    with Native() as n:
        n.start("fox", "marth", "final-destination", 1)
        n.step(60)
        check("headless without a file runs as before",
              n.fighter(0).state in (14, 324) or n.fighter(0).airborne)
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
