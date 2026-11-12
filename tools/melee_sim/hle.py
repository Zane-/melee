"""High-level replacements for the SDK functions that touch hardware.

Nothing here knows about Melee's game logic. GX, VI, audio, memory card and
the debugger are stubbed out wholesale by object file; DVD reads are served
from an extracted disc directory through a generated FST; ARAM is a host
buffer; the pad is whatever the host last set; time advances per frame.
"""

import bisect
import re
import struct
from pathlib import Path

import numpy as np

TICKS_PER_SEC = 40500000          # bus clock 162 MHz / 4
TICKS_PER_FRAME = TICKS_PER_SEC // 60
IRQ_RETURN = 0x8180FFE0           # never-executed address callbacks return to

# Whole objects replaced by "return 0". Individual functions hooked below
# take precedence because hooks are installed first.
STUB_OBJECTS = [
    "dolphin/gx/", "dolphin/vi/", "dolphin/ai/", "dolphin/dsp/",
    "dolphin/ax/", "dolphin/axfx/", "dolphin/card/", "dolphin/pad/",
    "dolphin/ar/", "dolphin/thp/", "dolphin/base/", "dolphin/db/",
    "dolphin/hio/", "dolphin/mcc/", "dolphin/amcstubs/",
    "dolphin/odenotstub/", "dolphin/dvd/dvdlow.c", "dolphin/dvd/dvd.c",
    "dolphin/dvd/dvdqueue.c", "dolphin/dvd/dvderror.c",
    "dolphin/dvd/fstload.c", "MetroTRK/",
    "dolphin/os/OSAudioSystem.c", "dolphin/os/OSCache.c",
    "dolphin/os/OSExi.c", "dolphin/os/OSSerial.c", "dolphin/os/OSRtc.c",
    "dolphin/os/OSReset.c", "dolphin/os/OSResetSW.c",
    "dolphin/os/OSReboot.c", "dolphin/os/OSUartExi.c",
    "dolphin/os/OSMemory.c", "dolphin/os/OSSync.c",
    "dolphin/os/OSInterrupt.c", "dolphin/os/OSError.c",
    "dolphin/os/OSContext.c", "dolphin/os/OSAlarm.c",   # alarms: see Hle
    "dolphin/os/OSTime.c", "dolphin/os/OSFont.c",
]


# --- FST built from an extracted disc directory ----------------------------

class Disc:
    """files/ of an extracted disc, addressable by virtual disc offset."""

    def __init__(self, root):
        self.root = Path(root)
        self.files = []            # (offset, length, path)
        self.cache = {}
        entries = [None]           # root placeholder
        names = bytearray()
        offset = 0x00100000

        def add_name(n):
            pos = len(names)
            names.extend(n.encode("latin-1") + b"\0")
            return pos

        def walk(d, parent):
            nonlocal offset
            for p in sorted(d.iterdir(), key=lambda p: p.name.lower()):
                if p.is_dir():
                    idx = len(entries)
                    entries.append(None)
                    name = add_name(p.name)
                    walk(p, idx)
                    entries[idx] = (1, name, parent, len(entries))
                else:
                    size = p.stat().st_size
                    entries.append((0, add_name(p.name), offset, size))
                    self.files.append((offset, size, p))
                    offset += (size + 0x7FFF) & ~0x7FFF
        walk(self.root, 0)
        entries[0] = (1, 0, 0, len(entries))
        out = bytearray()
        for flag, name, a, b in entries:
            out += struct.pack(">III", flag << 24 | name, a, b)
        self.fst = bytes(out + names)
        self._offs = [f[0] for f in self.files]

    def read(self, offset, length):
        i = bisect.bisect_right(self._offs, offset) - 1
        start, size, path = self.files[i]
        data = self.cache.get(path)
        if data is None:
            data = self.cache[path] = path.read_bytes()
        rel = offset - start
        chunk = data[rel:rel + length]
        return chunk + bytes(length - len(chunk)), path.name


# --- matrices ---------------------------------------------------------------

def _mtx(m, a):
    return np.frombuffer(m.read(a, 48), dtype=">f4").astype(np.float32
                                                           ).reshape(3, 4)


def _put_mtx(m, a, x):
    m.write(a, np.asarray(x, dtype=">f4").tobytes())


def _vec(m, a):
    return np.frombuffer(m.read(a, 12), dtype=">f4").astype(np.float32)


def _put_vec(m, a, v):
    m.write(a, np.asarray(v, dtype=">f4").tobytes())


def _full(x):
    return np.vstack([x, np.array([0, 0, 0, 1], dtype=np.float32)])


def _ret_f(m, v):
    m.set_f(1, float(np.float32(v)))


def install_math(m):
    f32 = np.float32

    def identity(m):
        _put_mtx(m, m.r(3), np.eye(3, 4, dtype=f32))

    def copy(m):
        m.write(m.r(4), m.read(m.r(3), 48))

    def concat(m):
        a, b = _full(_mtx(m, m.r(3))), _full(_mtx(m, m.r(4)))
        _put_mtx(m, m.r(5), (a @ b)[:3])

    def transpose(m):
        s = _mtx(m, m.r(3))
        o = np.zeros((3, 4), dtype=f32)
        o[:, :3] = s[:, :3].T
        _put_mtx(m, m.r(4), o)

    def inverse(m):
        s = _mtx(m, m.r(3)).astype(np.float64)
        det = np.linalg.det(s[:, :3])
        if det == 0:
            return 0
        inv = np.linalg.inv(s[:, :3])
        o = np.zeros((3, 4))
        o[:, :3] = inv
        o[:, 3] = -inv @ s[:, 3]
        _put_mtx(m, m.r(4), o)
        return 1

    def rot_trig(m):
        axis = chr(m.r(4) & 0xFF).lower()
        s, c = f32(m.f(1)), f32(m.f(2))
        o = np.eye(3, 4, dtype=f32)
        if axis == "x":
            o[1, 1], o[1, 2], o[2, 1], o[2, 2] = c, -s, s, c
        elif axis == "y":
            o[0, 0], o[0, 2], o[2, 0], o[2, 2] = c, s, -s, c
        else:
            o[0, 0], o[0, 1], o[1, 0], o[1, 1] = c, -s, s, c
        _put_mtx(m, m.r(3), o)

    def rot_axis_rad(m):
        v = _vec(m, m.r(4)).astype(np.float64)
        n = np.linalg.norm(v)
        x, y, z = v / n if n else v
        a = m.f(1)
        s, c = np.sin(a), np.cos(a)
        t = 1 - c
        o = np.zeros((3, 4))
        o[0, :3] = [t * x * x + c, t * x * y - s * z, t * x * z + s * y]
        o[1, :3] = [t * x * y + s * z, t * y * y + c, t * y * z - s * x]
        o[2, :3] = [t * x * z - s * y, t * y * z + s * x, t * z * z + c]
        _put_mtx(m, m.r(3), o)

    def trans(m):
        o = np.eye(3, 4, dtype=f32)
        o[:, 3] = [m.f(1), m.f(2), m.f(3)]
        _put_mtx(m, m.r(3), o)

    def scale(m):
        o = np.zeros((3, 4), dtype=f32)
        o[0, 0], o[1, 1], o[2, 2] = m.f(1), m.f(2), m.f(3)
        _put_mtx(m, m.r(3), o)

    def quat(m):
        x, y, z, w = np.frombuffer(m.read(m.r(4), 16), dtype=">f4"
                                   ).astype(np.float64)
        n = x * x + y * y + z * z + w * w
        s = 2.0 / n if n else 0.0
        o = np.zeros((3, 4))
        o[0, :3] = [1 - s * (y * y + z * z), s * (x * y - w * z),
                    s * (x * z + w * y)]
        o[1, :3] = [s * (x * y + w * z), 1 - s * (x * x + z * z),
                    s * (y * z - w * x)]
        o[2, :3] = [s * (x * z - w * y), s * (y * z + w * x),
                    1 - s * (x * x + y * y)]
        _put_mtx(m, m.r(3), o)

    def mult_vec(m):
        a, v = _mtx(m, m.r(3)), _vec(m, m.r(4))
        _put_vec(m, m.r(5), a[:, :3] @ v + a[:, 3])

    def mult_vec_sr(m):
        a, v = _mtx(m, m.r(3)), _vec(m, m.r(4))
        _put_vec(m, m.r(5), a[:, :3] @ v)

    def vadd(m):
        _put_vec(m, m.r(5), _vec(m, m.r(3)) + _vec(m, m.r(4)))

    def vsub(m):
        _put_vec(m, m.r(5), _vec(m, m.r(3)) - _vec(m, m.r(4)))

    def vscale(m):
        _put_vec(m, m.r(4), _vec(m, m.r(3)) * f32(m.f(1)))

    def vnorm(m):
        v = _vec(m, m.r(3))
        n = np.sqrt(np.dot(v, v), dtype=f32)
        _put_vec(m, m.r(4), v / n if n else v)

    def vmag(m):
        v = _vec(m, m.r(3))
        _ret_f(m, np.sqrt(np.dot(v, v), dtype=f32))

    def vdot(m):
        _ret_f(m, np.dot(_vec(m, m.r(3)), _vec(m, m.r(4))))

    def vcross(m):
        _put_vec(m, m.r(5), np.cross(_vec(m, m.r(3)), _vec(m, m.r(4))))

    for name, fn in {
        "PSMTXIdentity": identity, "PSMTXCopy": copy, "PSMTXConcat": concat,
        "PSMTXTranspose": transpose, "PSMTXInverse": inverse,
        "PSMTXRotTrig": rot_trig, "PSMTXRotAxisRad": rot_axis_rad,
        "PSMTXTrans": trans, "PSMTXScale": scale, "PSMTXQuat": quat,
        "PSMTXMultVec": mult_vec, "PSMTXMultVecSR": mult_vec_sr,
        "PSVECAdd": vadd, "PSVECSubtract": vsub, "PSVECScale": vscale,
        "PSVECNormalize": vnorm, "PSVECMag": vmag,
        "PSVECDotProduct": vdot, "PSVECCrossProduct": vcross,
    }.items():
        m.hook(name, fn)


# --- printf -----------------------------------------------------------------

def format_guest(m, fmt_addr, first_gpr):
    fmt = m.cstr(fmt_addr, 1024)
    gi, fi = first_gpr, 1

    sp = m.r(1)

    def nxt_int():
        # r3..r10, then the caller's parameter area at 8(r1)
        nonlocal gi
        v = m.r(gi) if gi <= 10 else m.u32(sp + 8 + 4 * (gi - 11))
        gi += 1
        return v

    def nxt_float():
        nonlocal fi
        v = m.f(fi) if fi <= 8 else 0.0
        fi += 1
        return v

    def rep(mo):
        flags, conv = mo.group(1), mo.group(2)
        try:
            if conv == "%":
                return "%"
            if conv == "s":
                a = nxt_int()
                return ("%" + flags + "s") % (
                    m.cstr(a) if 0x80000000 <= a < 0x81800000 else "")
            if conv in "di":
                v = nxt_int()
                return ("%" + flags + "d") % (v - (1 << 32) if v >> 31 else v)
            if conv in "uxXc":
                v = nxt_int()
                return ("%" + flags + conv) % (chr(v & 0xFF) if conv == "c"
                                               else v)
            if conv == "p":
                return "%08x" % nxt_int()
            if conv in "fFeEgG":
                return ("%" + flags + conv) % nxt_float()
        except (ValueError, TypeError):
            pass
        return mo.group(0)
    return re.sub(r"%([-+ #0-9.]*)(?:l|ll|h)?([%sdiuxXcpfFeEgG])", rep, fmt)


# --- everything else --------------------------------------------------------

class Hle:
    def __init__(self, m, disc_root, verbose=False):
        self.m = m
        self.disc = Disc(disc_root)
        self.verbose = verbose
        self.frame = 0
        self.ticks = 0
        self.aram = bytearray(0x1000000)
        self.aram_next = 0x4000
        self.pads = [dict(buttons=0, lx=0, ly=0, cx=0, cy=0, lt=0, rt=0,
                          connected=(i == 0)) for i in range(4)]
        self.retrace_post = 0
        self.scratch = 0           # set by Sim: zeroed guest memory for dummies
        self.reports = []
        self.reads = []
        # Emulated interrupt state. Hardware completions (DVD, ARAM) are
        # queued and delivered like interrupts: when the game re-enables
        # interrupts, or at the frame boundary.
        self.int_enabled = False
        self.pending = []          # (function, args)
        self.alarms = {}           # OSAlarm* -> (due tick, handler)
        self._irq_lr = []
        self.install()

    def report(self, text):
        self.reports.append(text)
        if self.verbose:
            print("[game] " + text.rstrip("\n"))

    def install(self):
        m = self.m
        install_math(m)

        # time
        def get_time(m):
            self.ticks += 64
            m.set_r(4, self.ticks & 0xFFFFFFFF)
            return self.ticks >> 32
        m.hook("OSGetTime", get_time)
        m.hook("__OSGetSystemTime", get_time)

        def get_tick(m):
            self.ticks += 64
            return self.ticks & 0xFFFFFFFF
        m.hook("OSGetTick", get_tick)

        # text output
        m.hook("OSReport", lambda m: self.report(format_guest(m, m.r(3), 4)))

        def panic(m):
            self.report("OSPanic %s:%d %s" % (
                m.cstr(m.r(3)), m.r(4), format_guest(m, m.r(5), 6)))
            raise RuntimeError("OSPanic: " + self.reports[-1])
        m.hook("OSPanic", panic)

        def hsd_assert(m):
            raise RuntimeError("assert %s:%d %s\n  backtrace: %s" % (
                m.cstr(m.r(3)), m.r(4), m.cstr(m.r(5)),
                " <- ".join(m.backtrace())))
        m.hook("__assert", hsd_assert)

        # interrupts
        def disable(m):
            old, self.int_enabled = self.int_enabled, False
            return int(old)

        def enable(m):
            old, self.int_enabled = self.int_enabled, True
            self.deliver(m)
            return int(old)

        def restore(m):
            old, self.int_enabled = self.int_enabled, bool(m.r(3))
            m.set_r(3, int(old))
            if self.int_enabled:
                self.deliver(m)
            return None
        m.hook("OSDisableInterrupts", disable)
        m.hook("OSEnableInterrupts", enable)
        m.hook("OSRestoreInterrupts", restore)
        m.hook(IRQ_RETURN, self._irq_return)

        # one-shot alarms (periodic ones are only the pad sampler, which
        # the frame hook drives itself)
        def set_alarm(m):
            alarm, ticks, handler = m.r(3), m.r(5) << 32 | m.r(6), m.r(7)
            self.alarms[alarm] = (self.ticks + ticks, handler)
            return 0

        def cancel_alarm(m):
            self.alarms.pop(m.r(3), None)
            return 0
        m.hook("OSSetAlarm", set_alarm)
        m.hook("OSCancelAlarm", cancel_alarm)

        # DVD
        m.hook("DVDInit", lambda m: m.tail_call(m.sym.addr("__DVDFSInit")))
        m.hook("DVDReadAsyncPrio", self.dvd_read_async)
        m.hook("DVDClose", lambda m: 1)

        # ARAM
        m.hook("ARInit", lambda m: 0x4000)
        m.hook("ARGetSize", lambda m: len(self.aram))
        m.hook("ARAlloc", self.ar_alloc)
        m.hook("ARStartDMA", self.ar_dma)
        m.hook("ARQPostRequest", self.arq_post)

        # video
        def set_post(m):
            old, self.retrace_post = self.retrace_post, m.r(3)
            return old
        m.hook("VISetPostRetraceCallback", set_post)
        m.hook("VIGetRetraceCount", lambda m: self.frame)
        m.hook("VIGetNextField", lambda m: self.frame & 1)

        def wait_retrace(m):
            self.frame += 1
            self.ticks += TICKS_PER_FRAME
            return 0
        m.hook("VIWaitForRetrace", wait_retrace)

        # pad
        m.hook("PADRead", self.pad_read)
        m.hook("PADInit", lambda m: 1)
        m.hook("PADReset", lambda m: 1)
        m.hook("PADRecalibrate", lambda m: 1)

        # GX: nothing is drawn, but sizes feed allocations
        m.hook("GXGetTexBufferSize",
               lambda m: (max(m.r(3), 4) * max(m.r(4), 4) * 4 + 31) & ~31)

        # audio: every voice is one scratch block nobody listens to
        m.hook("AXAcquireVoice", lambda m: self.scratch)

        # memory card: none inserted
        m.hook("CARDProbeEx", lambda m: -3)   # CARD_RESULT_NOCARD

    def advance(self, ticks):
        """Move emulated time forward and queue alarms that came due."""
        self.ticks += ticks
        for alarm, (due, handler) in sorted(self.alarms.items(),
                                            key=lambda kv: kv[1][0]):
            if due <= self.ticks:
                del self.alarms[alarm]
                self.post(handler, alarm, 0)

    def post(self, func, *args):
        """Queue a completion callback (delivered as an interrupt)."""
        self.pending.append((func, args))

    def deliver(self, m):
        """Run the next queued callback, if any, from inside a hook: the
        callback returns to IRQ_RETURN, which delivers the rest and then
        returns to the hooked function's caller."""
        if not self.pending:
            return False
        func, args = self.pending.pop(0)
        self._irq_lr.append((m.lr, m.r(3), None))
        self.int_enabled = False
        m.lr = IRQ_RETURN
        m.tail_call(func, *args)
        return True

    def inject(self, m):
        """Deliver the next queued callback at an arbitrary point (between
        run slices), preserving every register like a real interrupt. For
        busy-wait loops that never toggle interrupts."""
        if not self.pending or not self.int_enabled:
            return False
        func, args = self.pending.pop(0)
        ctx = m.save_context()
        self._irq_lr.append((m.pc, 0, ctx))
        self.int_enabled = False
        m.lr = IRQ_RETURN
        for i, a in enumerate(args):
            m.set_r(3 + i, a)
        m.pc = func
        return True

    def _irq_return(self, m):
        lr, r3, ctx = self._irq_lr.pop()
        self.int_enabled = True
        if ctx is not None:
            m.restore_context(ctx)
            m.pc = lr
            return None
        m.lr = lr
        m.set_r(3, r3)
        if not self.deliver(m):
            m.pc = lr
        return None

    def stub_hardware(self):
        n = 0
        for obj in STUB_OBJECTS:
            n += self.m.stub_object(obj)
        return n

    # DVDReadAsyncPrio(fileInfo, addr, length, offset, callback, prio)
    def dvd_read_async(self, m):
        fi, addr, length, offset, cb = (m.r(i) for i in range(3, 8))
        start = m.u32(fi + 0x30)
        data, name = self.disc.read(start + offset, length)
        m.write(addr, data)
        self.reads.append((name, offset, length))
        m.w32(fi + 0x0C, 0)          # command block state: END
        m.w32(fi + 0x20, length)     # transferred size
        if cb:
            self.post(cb, length, fi)
        return 1

    def ar_alloc(self, m):
        addr = self.aram_next
        self.aram_next += (m.r(3) + 31) & ~31
        return addr

    # ARStartDMA(type, mainmem, aram, length): type 0 = RAM -> ARAM
    def ar_dma(self, m):
        kind, ram, aram, length = (m.r(i) for i in range(3, 7))
        self._aram_copy(kind, ram, aram, length)
        return 0

    def _aram_copy(self, kind, ram, aram, length):
        if kind == 0:
            self.aram[aram:aram + length] = self.m.read(ram, length)
        else:
            self.m.write(ram, bytes(self.aram[aram:aram + length]))

    # ARQPostRequest(task, owner, type, prio, source, dest, length, callback)
    def arq_post(self, m):
        task, owner, kind, prio, src, dst, length, cb = (
            m.r(i) for i in range(3, 11))
        # the request struct is the caller's; fill it as the SDK does
        m.write(task, struct.pack(">8I", 0, owner, kind, prio, src, dst,
                                  length, cb))
        if kind == 0:
            self._aram_copy(0, src, dst, length)
        else:
            self._aram_copy(1, dst, src, length)
        if cb:
            self.post(cb, task)
        return 0

    # PADRead(PADStatus status[4]); 12 bytes each
    def pad_read(self, m):
        base = m.r(3)
        mask = 0
        for i, p in enumerate(self.pads):
            if p["connected"]:
                raw = struct.pack(">HbbbbBBBBbx", p["buttons"], p["lx"],
                                  p["ly"], p["cx"], p["cy"], p["lt"],
                                  p["rt"], 0, 0, 0)
                mask |= 0x80000000 >> i
            else:
                raw = struct.pack(">HbbbbBBBBbx", 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                  -1)
            m.write(base + i * 12, raw)
        return mask
