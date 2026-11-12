"""PowerPC machine for running Melee's code without Dolphin.

A Unicorn big-endian PPC32 CPU with the GameCube's 24 MB of RAM, a DOL
loaded into it, the decomp's symbol table, and function-level hooks: any
function can be replaced by a Python callable or by a "return constant" stub.
Hardware is never emulated; the SDK functions that touch it are hooked
(see hle.py).
"""

import bisect
import re
import struct
from pathlib import Path

from unicorn import (UC_ARCH_PPC, UC_HOOK_CODE, UC_HOOK_MEM_UNMAPPED,
                     UC_MODE_BIG_ENDIAN, UC_MODE_PPC32, Uc, UcError)
from unicorn import ppc_const as P

ROOT = Path(__file__).resolve().parent.parent.parent

RAM_BASE = 0x80000000
RAM_SIZE = 0x01800000
SCRATCH_BASE = 0x81800000
STOP_ADDR = 0x8180FFF0   # host calls return here; never executed

GPR = [getattr(P, "UC_PPC_REG_%d" % i) for i in range(32)]
FPR = [getattr(P, "UC_PPC_REG_FPR%d" % i) for i in range(32)]


class GuestError(Exception):
    pass


class Symbols:
    """Address <-> name from config/GALE01/symbols.txt plus an overlay map."""

    def __init__(self):
        self.by_name = {}
        self.funcs = []      # (addr, size, name), sorted
        self.objects = []    # (start, end, object path) for .text/.init
        pat = re.compile(r"(\S+) = \.(\w+):0x([0-9A-Fa-f]+);(.*)")
        for line in (ROOT / "config/GALE01/symbols.txt").read_text(
                ).splitlines():
            m = pat.match(line)
            if not m:
                continue
            name, sect, addr, rest = m[1], m[2], int(m[3], 16), m[4]
            self.by_name.setdefault(name, addr)
            if "type:function" in rest:
                sz = re.search(r"size:0x([0-9A-Fa-f]+)", rest)
                self.funcs.append((addr, int(sz[1], 16) if sz else 4, name))
        self._load_splits()
        self.funcs.sort()
        self._keys = [f[0] for f in self.funcs]

    def _load_splits(self):
        obj = None
        for line in (ROOT / "config/GALE01/splits.txt").read_text(
                ).splitlines():
            m = re.match(r"(\S+):\s*(?:comment.*)?$", line)
            if m and not line.startswith(("\t", " ")):
                obj = m[1]
                continue
            m = re.match(r"\s+\.(text|init)\s+start:0x([0-9A-Fa-f]+)"
                         r"\s+end:0x([0-9A-Fa-f]+)", line)
            if m and obj:
                self.objects.append((int(m[2], 16), int(m[3], 16), obj))
        self.objects.sort()

    def load_overlay_map(self, path):
        pat = re.compile(r"\s*[0-9a-fA-F]{8}\s+([0-9a-fA-F]{6,8})\s+"
                         r"([0-9a-fA-F]{8})\s+\d+\s+(\S+)\s+(\S+)")
        for line in Path(path).read_text(errors="replace").splitlines():
            m = pat.match(line)
            if not m:
                continue
            size, addr, name = int(m[1], 16), int(m[2], 16), m[3]
            if addr < 0x804F0000 or name.startswith("."):
                continue
            self.by_name.setdefault(name, addr)
            self.funcs.append((addr, size or 4, name))
        self.funcs.sort()
        self._keys = [f[0] for f in self.funcs]

    def addr(self, name):
        return self.by_name[name]

    def name(self, addr):
        i = bisect.bisect_right(self._keys, addr) - 1
        if i < 0:
            return "%08X" % addr
        a, size, name = self.funcs[i]
        if addr >= a + max(size, 4) + 0x4000:
            return "%08X" % addr
        return name if addr == a else "%s+0x%X" % (name, addr - a)

    def functions_in(self, prefix):
        """Names of all functions whose object path starts with prefix."""
        out = []
        for start, end, obj in self.objects:
            if obj.startswith(prefix):
                lo = bisect.bisect_left(self._keys, start)
                hi = bisect.bisect_left(self._keys, end)
                out += [self.funcs[i][2] for i in range(lo, hi)]
        return out


class Machine:
    def __init__(self, dol_path, overlay_map=None):
        self.sym = Symbols()
        if overlay_map and Path(overlay_map).exists():
            self.sym.load_overlay_map(overlay_map)
        self.uc = Uc(UC_ARCH_PPC, UC_MODE_PPC32 | UC_MODE_BIG_ENDIAN)
        self.uc.mem_map(RAM_BASE, RAM_SIZE)
        # Hardware registers and the locked cache are plain memory: writes
        # go nowhere, reads give zero. Code that needs real answers from
        # hardware is hooked at function level instead.
        self.uc.mem_map(0xCC000000, 0x10000)
        self.uc.mem_map(0xE0000000, 0x4000)
        # Host scratch (trampolines, dummy structs) just above RAM, so it
        # costs the game no arena.
        self.uc.mem_map(SCRATCH_BASE, 0x10000)
        self.hooks = {}
        self.entry = self._load_dol(Path(dol_path).read_bytes())
        self.uc.hook_add(UC_HOOK_MEM_UNMAPPED, self._on_unmapped)
        # MSR: FP available, supervisor
        self.uc.reg_write(P.UC_PPC_REG_MSR, 0x2000)
        self.stopped = None
        self.log = []

    # --- loading -----------------------------------------------------------
    def _load_dol(self, dol):
        offs = struct.unpack(">18I", dol[0x00:0x48])
        addrs = struct.unpack(">18I", dol[0x48:0x90])
        sizes = struct.unpack(">18I", dol[0x90:0xD8])
        self.ps_nops = 0
        for i, (o, a, s) in enumerate(zip(offs, addrs, sizes)):
            if not s:
                continue
            data = dol[o:o + s]
            if i < 7:
                data = self._nop_paired_single_saves(data)
            self.uc.mem_write(a, data)
        return struct.unpack(">I", dol[0xE0:0xE4])[0]

    def _nop_paired_single_saves(self, text):
        """Unicorn has no Gekko paired singles. Newer MWCC (used for the
        TM-CE units) saves and restores both halves of callee-saved float
        registers with psq_st / psq_l next to the usual stfd / lfd; the
        second half is never used by scalar code, so those become nops.
        Functions that really compute with paired singles are SDK matrix
        routines, replaced in hle.py."""
        import numpy as np
        w = np.frombuffer(text[:len(text) & ~3], dtype=">u4").copy()
        op = w >> 26
        mask = (op == 56) | (op == 57) | (op == 60) | (op == 61)
        self.ps_nops += int(mask.sum())
        w[mask] = 0x60000000
        return w.tobytes() + text[len(text) & ~3:]

    # --- memory ------------------------------------------------------------
    def read(self, addr, n):
        return bytes(self.uc.mem_read(addr, n))

    def write(self, addr, data):
        self.uc.mem_write(addr, bytes(data))

    def u8(self, a):
        return self.read(a, 1)[0]

    def u16(self, a):
        return struct.unpack(">H", self.read(a, 2))[0]

    def u32(self, a):
        return struct.unpack(">I", self.read(a, 4))[0]

    def s32(self, a):
        return struct.unpack(">i", self.read(a, 4))[0]

    def f32(self, a):
        return struct.unpack(">f", self.read(a, 4))[0]

    def w8(self, a, v):
        self.write(a, bytes([v & 0xFF]))

    def w16(self, a, v):
        self.write(a, struct.pack(">H", v & 0xFFFF))

    def w32(self, a, v):
        self.write(a, struct.pack(">I", v & 0xFFFFFFFF))

    def wf32(self, a, v):
        self.write(a, struct.pack(">f", v))

    def cstr(self, a, limit=512):
        out = bytearray()
        while len(out) < limit:
            chunk = self.read(a + len(out), 32)
            i = chunk.find(b"\0")
            if i >= 0:
                out += chunk[:i]
                break
            out += chunk
        return out.decode("latin-1")

    # --- registers ---------------------------------------------------------
    def r(self, i):
        return self.uc.reg_read(GPR[i])

    def set_r(self, i, v):
        self.uc.reg_write(GPR[i], v & 0xFFFFFFFF)

    def f(self, i):
        """Float register as a Python float (Unicorn holds raw IEEE bits)."""
        return struct.unpack("<d", struct.pack(
            "<Q", self.uc.reg_read(FPR[i])))[0]

    def set_f(self, i, v):
        self.uc.reg_write(FPR[i], struct.unpack(
            "<Q", struct.pack("<d", float(v)))[0])

    @property
    def pc(self):
        return self.uc.reg_read(P.UC_PPC_REG_PC)

    @pc.setter
    def pc(self, v):
        self.uc.reg_write(P.UC_PPC_REG_PC, v)

    @property
    def lr(self):
        return self.uc.reg_read(P.UC_PPC_REG_LR)

    @lr.setter
    def lr(self, v):
        self.uc.reg_write(P.UC_PPC_REG_LR, v)

    _CTX = (GPR + FPR + [P.UC_PPC_REG_LR, P.UC_PPC_REG_CTR, P.UC_PPC_REG_XER,
                         P.UC_PPC_REG_CR, P.UC_PPC_REG_FPSCR])

    def save_context(self):
        return [self.uc.reg_read(r) for r in self._CTX]

    def restore_context(self, ctx):
        for r, v in zip(self._CTX, ctx):
            self.uc.reg_write(r, v)

    # --- hooks -------------------------------------------------------------
    def stub(self, name, value=0):
        """Make a function return a constant (`li r3, value; blr`)."""
        addr = self.sym.addr(name) if isinstance(name, str) else name
        if -0x8000 <= value < 0x8000:
            code = struct.pack(">II", 0x38600000 | (value & 0xFFFF),
                               0x4E800020)
        else:
            code = struct.pack(">III", 0x3C600000 | (value >> 16 & 0xFFFF),
                               0x60630000 | (value & 0xFFFF), 0x4E800020)
        self.write(addr, code)
        # drop any translation of the old code
        self.uc.ctl_remove_cache(addr, addr + len(code))

    def stub_object(self, prefix, value=0, keep=()):
        n = 0
        for name in self.sym.functions_in(prefix):
            if name not in keep and name not in self.hooks:
                self.stub(name, value)
                n += 1
        return n

    def hook(self, name, fn):
        """Replace a function with fn(machine); fn returns the value for r3
        (or None to leave registers as it set them). Unless fn changes the
        PC itself (tail call), execution continues at the caller."""
        addr = self.sym.addr(name) if isinstance(name, str) else name
        self.hooks[name] = fn

        def cb(uc, address, size, user):
            self.pc = address
            ret = fn(self)
            if ret is not None:
                self.set_r(3, int(ret))
            if self.pc == address:
                self.pc = self.lr
        self.uc.hook_add(UC_HOOK_CODE, cb, begin=addr, end=addr)
        self.uc.ctl_remove_cache(addr, addr + 4)

    def trace(self, name, nargs=4):
        """Log every call of a function (for debugging) into self.log."""
        addr = self.sym.addr(name)

        def cb(uc, address, size, user):
            self.log.append("%s(%s) from %s" % (
                name, ", ".join("%X" % self.r(3 + i) for i in range(nargs)),
                self.sym.name(self.lr)))
        self.uc.hook_add(UC_HOOK_CODE, cb, begin=addr, end=addr)
        # code translated before the hook existed would not call it
        self.uc.ctl_remove_cache(addr, addr + 4)

    def tail_call(self, func, *args):
        """From inside a hook: run a guest function next, returning to the
        hooked function's caller."""
        for i, a in enumerate(args):
            self.set_r(3 + i, a)
        self.pc = func

    # --- running -----------------------------------------------------------
    def _on_unmapped(self, uc, access, address, size, value, user):
        self.stopped = "unmapped %s of %08X (size %d) at %s, lr %s" % (
            "write" if access in (20, 23) else "read", address, size,
            self.sym.name(self.pc), self.sym.name(self.lr))
        return False

    def backtrace(self, depth=12):
        out = [self.sym.name(self.pc), "lr " + self.sym.name(self.lr)]
        sp = self.r(1)
        for _ in range(depth):
            if not (RAM_BASE <= sp < RAM_BASE + RAM_SIZE - 8):
                break
            nxt = self.u32(sp)
            if not (RAM_BASE <= nxt < RAM_BASE + RAM_SIZE - 8):
                break
            out.append(self.sym.name(self.u32(nxt + 4)))
            sp = nxt
        return out

    def run(self, start=None, until=STOP_ADDR, count=0, timeout=0):
        """Run until `until`, a stop() from a hook, `count` instructions or
        `timeout` seconds. Returns "done", "stop", or "count" (limit hit).
        An instruction count makes Unicorn instrument every instruction
        (about 5x slower): use it for debugging, not for stepping."""
        self.stopped = None
        begin = self.pc if start is None else start
        try:
            self.uc.emu_start(begin, until, timeout=int(timeout * 1e6),
                              count=count)
        except UcError as e:
            raise GuestError("%s\n  %s\n  backtrace: %s" % (
                e, self.stopped or "", " <- ".join(self.backtrace())))
        if self.stopped == "stop":
            return "stop"
        return "done" if self.pc == until else "count"

    def stop(self):
        self.stopped = "stop"
        self.uc.emu_stop()

    def call(self, func, *args, count=0):
        """Call a guest function from the host and return r3."""
        addr = self.sym.addr(func) if isinstance(func, str) else func
        for i, a in enumerate(args):
            self.set_r(3 + i, a)
        self.lr = STOP_ADDR
        res = self.run(addr, STOP_ADDR, count)
        if res != "done":
            raise GuestError("call %s: %s at %s" % (
                func, res, " <- ".join(self.backtrace())))
        return self.r(3)
