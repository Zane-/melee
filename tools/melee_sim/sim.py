"""Boot Melee in the emulator and step it frame by frame.

    from sim import Sim
    s = Sim()            # build/overlay/main.dol + build/disc/files
    s.boot()
    s.step(60)
"""

import hashlib
import pickle
import struct
import sys
import time
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from unicorn import ppc_const as P  # noqa: E402
from machine import (Machine, GuestError, ROOT, STOP_ADDR,  # noqa: E402
                     RAM_BASE, RAM_SIZE, SCRATCH_BASE)
from hle import Hle  # noqa: E402


class Sim:
    def __init__(self, dol=None, disc=None, overlay_map=None, verbose=False):
        dol = Path(dol or ROOT / "build/overlay/main.dol")
        disc = Path(disc or ROOT / "build/disc")
        if overlay_map is None:
            overlay_map = dol.parent / "overlay.map"
        self.m = Machine(dol, overlay_map)
        self.h = Hle(self.m, disc / "files", verbose)
        self.disc = disc
        self.dol_hash = hashlib.sha1(dol.read_bytes()).hexdigest()
        self.frame = 0
        self._polled = False
        self._p2_human = False
        self.match_info = {}
        self._setup_lowmem()
        self._install_frame_hooks()
        self._install_match_override()
        self.h.stub_hardware()

    def _setup_lowmem(self):
        m = self.m
        boot = (self.disc / "sys/boot.bin").read_bytes()
        bi2 = (self.disc / "sys/bi2.bin").read_bytes()
        fst = self.h.disc.fst
        fst_addr = (0x81800000 - len(fst)) & ~0x1F
        bi2_addr = SCRATCH_BASE + 0x8000    # outside the arena, as in Dolphin
        self.h.scratch = SCRATCH_BASE
        arena_hi = fst_addr
        m.write(fst_addr, fst)
        m.write(bi2_addr, bi2[:0x2000])
        m.write(0x80000000, boot[:0x20])
        m.w32(0x80000020, 0x0D15EA5E)      # boot magic
        m.w32(0x80000024, 1)               # version
        m.w32(0x80000028, 0x01800000)      # physical memory size
        m.w32(0x8000002C, 0x00000003)      # console type: retail
        m.w32(0x80000030, 0)               # arena lo: use the linker's
        m.w32(0x80000034, arena_hi)        # arena hi
        m.w32(0x80000038, fst_addr)
        m.w32(0x8000003C, len(fst))
        m.w32(0x800000CC, 0)               # NTSC
        m.w32(0x800000F0, 0x01800000)      # simulated memory size
        m.w32(0x800000F4, bi2_addr)
        m.w32(0x800000F8, 162000000)       # bus clock
        m.w32(0x800000FC, 486000000)       # cpu clock

    def _install_frame_hooks(self):
        m = self.m
        poll = m.sym.addr("lb_80019894")
        renew = m.sym.addr("fn_800195FC")
        count = m.sym.addr("HSD_PadGetRawQueueCount")

        # gm_801A4D34 waits here for the pad alarm to queue a sample. One
        # call = one frame: stop for the host, then sample the pad, then
        # report the queue length.
        def poll_hook(mm):
            if self.h.pending:
                # completions that arrived while the game was not toggling
                # interrupts: deliver, then come back here
                self.h.int_enabled = True
                if getattr(self, "_poll_back", None) is None:
                    self._poll_back = mm.lr
                mm.lr = poll
                self.h.deliver(mm)
                return
            if getattr(self, "_poll_back", None) is not None:
                mm.lr = self._poll_back
                self._poll_back = None
            if not self._polled:
                self._polled = True
                self.frame += 1
                self.h.frame += 1
                self.h.advance(675000)
                mm.pc = renew
                saved = mm.lr
                self._poll_lr = saved
                mm.lr = poll
                mm.stop()
            else:
                self._polled = False
                mm.lr = self._poll_lr
                mm.pc = count
        m.hook("lb_80019894", poll_hook)

        # Every wait loop in the game spins on this idle function (disc
        # error check + memory card task). Time passes here and queued
        # completions are delivered, so waits on alarms, DVD and ARAM end
        # without counting instructions.
        idle = m.sym.addr("lb_800192A8")
        idle_body = self._relocate_entry(idle)

        def idle_hook(mm):
            self.h.advance(2000)
            if self.h.pending:
                self.h.int_enabled = True
                if self._idle_back is None:
                    self._idle_back = (mm.lr, mm.r(3))
                mm.lr = idle
                self.h.deliver(mm)
                return
            if self._idle_back is not None:
                lr, r3 = self._idle_back
                self._idle_back = None
                mm.lr = lr
                mm.set_r(3, r3)
            mm.pc = idle_body
        self._idle_back = None
        m.hook("lb_800192A8", idle_hook)
        for name in ("HSD_StartRender", "HSD_GObj_80390FC0",
                     "HSD_VICopyXFBAsync", "HSD_VIWaitXFBFlush",
                     "db_ClearFPUExceptions",
                     # graphics-only setup that needs real GX answers
                     "lbRefract_800222A4"):
            m.stub(name)

    def _relocate_entry(self, func):
        """Copy a function's first instruction to scratch memory followed by
        a branch back to its second, so a hook on the entry can still run
        the original body. The first instruction must not be PC-relative
        (prologues start with stwu or mflr)."""
        m = self.m
        self._tramp = getattr(self, "_tramp", self.h.scratch + 0x1000)
        at = self._tramp
        self._tramp += 8
        first = m.u32(func)
        assert first >> 26 not in (16, 18), "PC-relative first instruction"
        rel = (func + 4 - (at + 4)) & 0x03FFFFFC
        m.w32(at, first)
        m.w32(at + 4, 0x48000000 | rel)
        return at

    def boot(self):
        m = self.m
        m.call("__init_registers")
        m.call("__init_user")
        m.lr = STOP_ADDR
        m.pc = m.sym.addr("main")
        self.step(1)
        # After boot no more sound banks are loaded (nothing plays them, and
        # the HLE'd audio layer does not size bank memory the way the real
        # one does, so later loads would assert).
        for name in ("lbAudioAx_80027168", "lbAudioAx_8002785C"):
            m.stub(name)
        return self.frame

    def step(self, frames=1, timeout=60):
        """Advance whole frames. Raises GuestError if a frame does not end
        within `timeout` seconds of host time (a wait the HLE cannot
        satisfy)."""
        target = self.frame + frames
        while self.frame < target:
            res = self.m.run(timeout=timeout)
            if res == "done":
                raise GuestError("main returned")
            if res != "stop":
                raise GuestError(
                    "frame %d did not end within %ds (%d completions "
                    "pending, interrupts %s); at %s" % (
                        self.frame + 1, timeout, len(self.h.pending),
                        "on" if self.h.int_enabled else "off",
                        " <- ".join(self.m.backtrace())))
        return self.frame


    # --- host calls ----------------------------------------------------------
    def call(self, func, *args):
        """Call a guest function between frames; registers are preserved."""
        ctx, pc = self.m.save_context(), self.m.pc
        try:
            return self.m.call(func, *args)
        finally:
            self.m.restore_context(ctx)
            self.m.pc = pc

    # --- input ---------------------------------------------------------------
    def pad(self, port=0, buttons=(), stick=(0, 0), cstick=(0, 0), l=0, r=0):
        """Set a controller's state until changed. Buttons by name
        (A B X Y Z L R START and D-pad UP DOWN LEFT RIGHT), sticks -1..1,
        analog triggers 0..1."""
        p = self.h.pads[port]
        p["connected"] = True
        p["buttons"] = sum(BUTTONS[b.upper()] for b in buttons)
        p["lx"], p["ly"] = (int(round(max(-1, min(1, v)) * 127))
                            for v in stick)
        p["cx"], p["cy"] = (int(round(max(-1, min(1, v)) * 127))
                            for v in cstick)
        p["lt"], p["rt"] = int(l * 255), int(r * 255)

    def press(self, *buttons, port=0, frames=3, wait=20):
        self.pad(port, buttons)
        self.step(frames)
        self.pad(port)
        self.step(wait)

    # --- snapshots -----------------------------------------------------------
    def snapshot(self):
        """Everything needed to come back to this frame, as a dict."""
        m, h = self.m, self.h
        return {
            "ram": m.read(RAM_BASE, RAM_SIZE),
            "hw": m.read(0xCC000000, 0x10000),
            "lc": m.read(0xE0000000, 0x4000),
            "scratch": m.read(SCRATCH_BASE, 0x10000),
            "ctx": m.save_context(), "pc": m.pc,
            "msr": m.uc.reg_read(P.UC_PPC_REG_MSR),
            "aram": bytes(h.aram), "aram_next": h.aram_next,
            "frame": self.frame, "hframe": h.frame, "ticks": h.ticks,
            "pending": list(h.pending), "alarms": dict(h.alarms),
            "int_enabled": h.int_enabled, "irq_lr": list(h._irq_lr),
            "pads": [dict(p) for p in h.pads],
            "polled": self._polled, "poll_lr": getattr(self, "_poll_lr", 0),
            "poll_back": getattr(self, "_poll_back", None),
            "idle_back": self._idle_back, "match": dict(self.match_info),
        }

    def restore(self, snap):
        m, h = self.m, self.h
        m.write(RAM_BASE, snap["ram"])
        m.write(0xCC000000, snap["hw"])
        m.write(0xE0000000, snap["lc"])
        m.write(SCRATCH_BASE, snap["scratch"])
        # translations of code that was patched or loaded since
        m.uc.ctl_remove_cache(RAM_BASE, RAM_BASE + RAM_SIZE)
        m.restore_context(snap["ctx"])
        m.uc.reg_write(P.UC_PPC_REG_MSR, snap["msr"])
        m.pc = snap["pc"]
        h.aram[:] = snap["aram"]
        h.aram_next = snap["aram_next"]
        self.frame, h.frame, h.ticks = (snap["frame"], snap["hframe"],
                                        snap["ticks"])
        h.pending, h.alarms = list(snap["pending"]), dict(snap["alarms"])
        h.int_enabled, h._irq_lr = snap["int_enabled"], list(snap["irq_lr"])
        h.pads = [dict(p) for p in snap["pads"]]
        self._polled, self._poll_lr = snap["polled"], snap["poll_lr"]
        self._poll_back, self._idle_back = (snap["poll_back"],
                                            snap["idle_back"])
        self.match_info = dict(snap["match"])

    def save(self, path):
        snap = self.snapshot()
        snap["dol"] = self.dol_hash
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(zlib.compress(pickle.dumps(snap), 1))

    def load(self, path):
        snap = pickle.loads(zlib.decompress(Path(path).read_bytes()))
        if snap["dol"] != self.dol_hash:
            raise ValueError("%s was made with a different DOL" % path)
        self.restore(snap)

    # --- getting into a match ------------------------------------------------
    def boot_to_css(self):
        """Boot and get past the memory card prompt to the event mode's
        character select screen (the overlay boots straight into it)."""
        self.boot()
        for _ in range(40):
            self.press("A")
            if self.m.u32(self.m.sym.addr("mnCharSel_804A0BC0")):
                self.step(60)
                return
        raise GuestError("never reached the character select screen")

    @classmethod
    def match(cls, event="lab", p1="fox", p2="marth",
              stage="final-destination", seed=1, options=(), p2_human=False,
              free=False, cache=True, verbose=False):
        """A simulator standing at the first frames of a match.

        Uses the test build (build/overlay-tmtest, `TM_TEST=1`; see
        docs/ai/testing.md): its runner boots straight into `event` with
        these characters and stage, so no menu is involved. The scripted
        input of that runner is switched off; drive the pads from Python.
        `options` are (index, value) pairs for the event's main menu.
        With p2_human, player 2 reads controller port 2 (pad index 1)
        instead of being a CPU.

        free=True is the sandbox for testing raw interactions: the event's
        per-frame logic is switched off (TM-CE's events drive the CPU and
        reset positions every frame) and player 2 is human, so both
        fighters do exactly what the two pads say.

        The state at match start is cached under build/sim/fixtures/ (keyed
        by the arguments and the DOL), so later calls take a fraction of a
        second.
        """
        out = ROOT / "build" / "overlay-tmtest"
        if not (out / "main.dol").exists():
            raise FileNotFoundError(
                "no test build: run OVERLAY_OUT=build/overlay-tmtest "
                "TM_TEST=1 python tools/overlay_build.py")
        s = cls(dol=out / "main.dol", overlay_map=out / "overlay.map",
                verbose=verbose)
        p2_human = p2_human or free
        key = hashlib.sha1(repr((event, p1, p2, stage, seed, tuple(
            map(tuple, options)), p2_human, free, s.dol_hash)).encode()
        ).hexdigest()[:16]
        path = ROOT / "build/sim/fixtures" / (
            "%s_%s_%s_%s.sav" % (event, p1, p2, key))
        if cache and path.exists():
            s.load(path)
            return s
        sys.path.insert(0, str(ROOT / "tools"))
        import tmtest
        spec = {"event": event, "hmn": CHARACTERS[p1], "cpu": CHARACTERS[p2],
                "stage": STAGES[stage], "seed": seed,
                "max_frames": 0x7FFFFFFF, "options": list(options)}
        s.m.write(s.m.sym.addr("tm_test_config"), tmtest.pack_config(spec))
        s._p2_human = p2_human
        if free:
            s.m.stub("tmce_%s_Event_Think" % event)
        s.boot()
        for i in range(3000):
            # no memory card: confirm the prompt on the way
            s.pad(0, ["A"] if i % 20 < 3 else [])
            s.step()
            if any('"match":"start"' in r for r in s.h.reports):
                break
        else:
            raise GuestError("the test match never started; last output: %s"
                             % s.h.reports[-3:])
        s.pad(0)
        # hand port 1 back to the host
        s.m.stub("ScriptedPad")
        s.match_info = {"event": event, "p1": p1, "p2": p2, "stage": stage,
                        "seed": seed, "p2_human": p2_human, "free": free,
                        "start_frame": s.frame}
        if cache:
            s.save(path)
        return s

    def _install_match_override(self):
        m = self.m
        body = self._relocate_entry(m.sym.addr("fn_8016E730"))

        # fn_8016E730(StartMeleeData*) builds the match. Players are 0x24
        # bytes each from +0x60; byte 1 is the slot type (0 = human).
        def hook(mm):
            if self._p2_human:
                mm.w8(mm.r(3) + 0x60 + 0x24 + 1, 0)
            mm.pc = body
        m.hook("fn_8016E730", hook)

    # --- reading the game ----------------------------------------------------
    def fighter(self, i):
        return Fighter(self, i)


PLAYER_SLOTS = 0x80453080
BUTTONS = {"LEFT": 0x0001, "RIGHT": 0x0002, "DOWN": 0x0004, "UP": 0x0008,
           "Z": 0x0010, "R": 0x0020, "L": 0x0040, "A": 0x0100, "B": 0x0200,
           "X": 0x0400, "Y": 0x0800, "START": 0x1000}
# CharacterKind (src/melee/ft/forward.h), by data/ character id
CHARACTERS = {
    "captain-falcon": 0x00, "donkey-kong": 0x01, "fox": 0x02,
    "mr-game-and-watch": 0x03, "kirby": 0x04, "bowser": 0x05, "link": 0x06,
    "luigi": 0x07, "mario": 0x08, "marth": 0x09, "mewtwo": 0x0A,
    "ness": 0x0B, "peach": 0x0C, "pikachu": 0x0D, "ice-climbers": 0x0E,
    "jigglypuff": 0x0F, "samus": 0x10, "yoshi": 0x11, "zelda": 0x12,
    "sheik": 0x13, "falco": 0x14, "young-link": 0x15, "dr-mario": 0x16,
    "roy": 0x17, "pichu": 0x18, "ganondorf": 0x19,
}
STAGES = {"fountain-of-dreams": 0x02, "pokemon-stadium": 0x03,
          "yoshis-story": 0x08, "dream-land": 0x1C, "battlefield": 0x1F,
          "final-destination": 0x20}


class Fighter:
    """Read-only view of a player's fighter (offsets: src/melee/ft/types.h)."""

    def __init__(self, sim, index):
        self.sim, self.index = sim, index
        m = sim.m
        self.gobj = m.u32(PLAYER_SLOTS + index * 0xE90 + 0xB0)
        self.fp = m.u32(self.gobj + 0x2C) if self.gobj else 0

    def _u32(self, off):
        return self.sim.m.u32(self.fp + off)

    def _f32(self, off):
        return self.sim.m.f32(self.fp + off)

    @property
    def kind(self):
        return self._u32(0x04)

    @property
    def state(self):
        """Motion state id (ftCo_MS_* / the character's own enum)."""
        return self._u32(0x10)

    @property
    def state_frame(self):
        return self._f32(0x894)

    @property
    def facing(self):
        return self._f32(0x2C)

    @property
    def pos(self):
        return (self._f32(0xB0), self._f32(0xB4))

    @property
    def vel(self):
        return (self._f32(0x80), self._f32(0x84))

    @property
    def airborne(self):
        return bool(self._u32(0xE0))

    @property
    def percent(self):
        return self._f32(0x1830)

    @property
    def hitlag(self):
        return self._f32(0x195C)

    @property
    def hitstun(self):
        """Frames of hitstun left (0 when not in hitstun)."""
        return self._f32(0x2340) if (self.sim.m.u8(self.fp + 0x221C) & 2) \
            else 0.0

    @property
    def shield(self):
        return self._f32(0x1998)

    @property
    def jumps_used(self):
        return self.sim.m.u8(self.fp + 0x1968)

    @property
    def invulnerable(self):
        return self._u32(0x1988) != 0 or self._u32(0x198C) != 0

    def summary(self):
        x, y = self.pos
        return "P%d state %3d f%-4g pos (%7.2f, %6.2f) %s %5.1f%%" % (
            self.index + 1, self.state, self.state_frame, x, y,
            "air" if self.airborne else "gnd", self.percent)


if __name__ == "__main__":
    s = Sim(verbose=True)
    t = time.time()
    try:
        s.boot()
        n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
        for i in range(n):
            s.step()
        print("frames", s.frame, "in %.1fs" % (time.time() - t))
    except (GuestError, RuntimeError) as e:
        print("STOPPED after %.1fs, frame %d:" % (time.time() - t, s.frame))
        print(e)
        print("last reads:", s.h.reads[-5:])
