#!/usr/bin/env python3
"""Drive Dolphin for automated boot tests of the training overlay.

    from dolphin_harness import Dolphin
    with Dolphin("build/disc-test/sys/main.dol") as d:
        d.wait_for(lambda: d.read_u32(0x804A0BC0) != 0, timeout=60)
        d.press("A")

- Runs dolphin-emu with its own user directory (build/dolphin-test/), so the
  owner's config and memory card are untouched; the memory card folder is
  copied from ~/.local/share/dolphin-emu/GC/USA/Card A once.
- Controller 1 is Dolphin's pipe input (Pipes/pipe1): press(), hold(),
  release(), stick(), cstick(), trigger().
- Memory is read through Dolphin's GDB stub with a minimal remote-protocol
  client: the game is paused for each read and resumed.
- Panic dialogs are disabled so invalid reads do not block the run.

Symbol addresses: Overlay(map) reads build/overlay/overlay.map (or a test
build's), including the local statics of TM-CE units.
"""

import os
import re
import shutil
import socket
import struct
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER = ROOT / "build" / "dolphin-test"
OWNER_CARD = Path.home() / ".local/share/dolphin-emu/GC/USA/Card A"
PORT = 2346

PAD_INI = """[GCPad1]
Device = Pipe/0/pipe1
Buttons/A = `Button A`
Buttons/B = `Button B`
Buttons/X = `Button X`
Buttons/Y = `Button Y`
Buttons/Z = `Button Z`
Buttons/Start = `Button START`
Main Stick/Up = `Axis MAIN Y +`
Main Stick/Down = `Axis MAIN Y -`
Main Stick/Left = `Axis MAIN X -`
Main Stick/Right = `Axis MAIN X +`
C-Stick/Up = `Axis C Y +`
C-Stick/Down = `Axis C Y -`
C-Stick/Left = `Axis C X -`
C-Stick/Right = `Axis C X +`
Triggers/L = `Button L`
Triggers/R = `Button R`
Triggers/L-Analog = `Axis L +`
Triggers/R-Analog = `Axis R +`
D-Pad/Up = `Button D_UP`
D-Pad/Down = `Button D_DOWN`
D-Pad/Left = `Button D_LEFT`
D-Pad/Right = `Button D_RIGHT`
[GCPad2]
Device = Pipe/0/none
[GCPad3]
Device = Pipe/0/none
[GCPad4]
Device = Pipe/0/none
"""


class Overlay:
    """Symbol lookup in an overlay link map (globals and unit statics)."""

    def __init__(self, map_path=ROOT / "build/overlay/overlay.map"):
        self.syms = {}
        pat = re.compile(r"\s*[0-9a-fA-F]{8}\s+([0-9a-fA-F]{6,8})\s+([0-9a-fA-F]{8})"
                         r"\s+\d+\s+(\S+)\s+(\S+)")
        for line in Path(map_path).read_text(errors="replace").splitlines():
            m = pat.match(line)
            if m:
                size, addr, name, obj = int(m[1], 16), int(m[2], 16), m[3], m[4]
                self.syms.setdefault(name, []).append((addr, size, obj))

    def addr(self, name, obj=None):
        hits = [h for h in self.syms.get(name, []) if obj is None or obj in h[2]]
        if len(hits) != 1:
            raise KeyError(f"{name} ({obj}): {hits}")
        return hits[0][0]


class Gdb:
    """Minimal GDB remote serial protocol client for Dolphin's stub."""

    def __init__(self, port):
        for _ in range(100):
            try:
                self.s = socket.create_connection(("127.0.0.1", port), timeout=10)
                break
            except OSError:
                time.sleep(0.2)
        else:
            raise RuntimeError("Dolphin GDB stub did not open")
        self.buf = b""
        self.running = False
        self.packet("?")

    def _send(self, data):
        pkt = b"$" + data.encode() + b"#" + b"%02x" % (sum(data.encode()) & 0xFF)
        self.s.sendall(pkt)

    def _recv_packet(self):
        while True:
            i = self.buf.find(b"$")
            j = self.buf.find(b"#", i + 1) if i >= 0 else -1
            if i >= 0 and j >= 0 and len(self.buf) >= j + 3:
                data = self.buf[i + 1 : j]
                self.buf = self.buf[j + 3 :]
                self.s.sendall(b"+")
                return data.decode(errors="replace")
            chunk = self.s.recv(65536)
            if not chunk:
                raise RuntimeError("GDB stub closed the connection")
            self.buf += chunk

    def packet(self, data):
        self._send(data)
        return self._recv_packet()

    def pause(self):
        if self.running:
            self.s.sendall(b"\x03")
            self._recv_packet()
            self.running = False

    def resume(self):
        if not self.running:
            self._send("c")
            self.running = True

    def read(self, addr, n):
        was = self.running
        self.pause()
        out = b""
        while len(out) < n:
            k = min(0x400, n - len(out))
            self._send(f"m{addr + len(out):x},{k:x}")
            r = self._recv_packet()
            # After an interrupt Dolphin sends a stop reply, an empty packet
            # and a second stop reply; skip them.
            while r == "" or r[:1] in ("S", "T", "W", "O") or r == "OK":
                r = self._recv_packet()
            if r.startswith("E") or not r:
                raise RuntimeError(f"read {addr:08x}: {r}")
            out += bytes.fromhex(r)
        if was:
            self.resume()
        return out


def gdb_write(gdb, addr, data):
    """Write guest memory through the GDB stub (game paused meanwhile)."""
    was = gdb.running
    gdb.pause()
    gdb._send("M%x,%x:%s" % (addr, len(data), data.hex()))
    r = gdb._recv_packet()
    while r != "OK" and (r == "" or r[:1] in ("S", "T", "W", "O")):
        r = gdb._recv_packet()
    if r != "OK":
        raise RuntimeError(f"write {addr:08x}: {r}")
    if was:
        gdb.resume()


class Dolphin:
    def __init__(self, dol, speed=1.0, port=PORT, dump_frames=False):
        self.dol = Path(dol)
        self.speed = speed
        self.port = port
        # dump_frames: record video to build/dolphin-test/Dump/Frames/ so a
        # run can be looked at afterwards (see frame() below).
        self.dump_frames = dump_frames

    def __enter__(self):
        (USER / "Config").mkdir(parents=True, exist_ok=True)
        (USER / "Pipes").mkdir(exist_ok=True)
        card = USER / "GC" / "USA" / "Card A"
        if not card.exists() and OWNER_CARD.exists():
            shutil.copytree(OWNER_CARD, card)
        (USER / "Config" / "GCPadNew.ini").write_text(PAD_INI)
        # The game's OSReport output (panics, asserts, TM-CE logs) goes to
        # build/dolphin-test/Logs/dolphin.log.
        (USER / "Config" / "Logger.ini").write_text(
            "[Logs]\nOSREPORT = True\nOSREPORT_HLE = True\nMI = True\n"
            "[Options]\nWriteToFile = True\nWriteToConsole = False\n"
            "Verbosity = 4\n")
        log = USER / "Logs" / "dolphin.log"
        if log.exists():
            log.unlink()
        pipe = USER / "Pipes" / "pipe1"
        if not pipe.exists():
            os.mkfifo(pipe)
        cmd = ["dolphin-emu", "-u", str(USER), "-b",
               "-C", f"Dolphin.General.GDBPort={self.port}",
               "-C", "Dolphin.Interface.UsePanicHandlers=False",
               "-C", "Dolphin.Interface.ConfirmStop=False",
               "-C", "Dolphin.Display.Fullscreen=False",
               "-C", f"Dolphin.Core.EmulationSpeed={self.speed}",
               "-C", "Dolphin.Core.SIDevice0=6",
               "-e", str(self.dol)]
        if self.dump_frames:
            shutil.rmtree(USER / "Dump" / "Frames", ignore_errors=True)
            cmd[-2:-2] = ["-C", "Dolphin.Movie.DumpFrames=True",
                          "-C", "Dolphin.Movie.DumpFramesSilent=True"]
        self.log = open(USER / "dolphin.log", "w")
        self.proc = subprocess.Popen(cmd, stdout=self.log, stderr=subprocess.STDOUT)
        self.gdb = Gdb(self.port)
        # Dolphin opens the pipe once emulation starts.
        self.gdb.resume()
        deadline = time.time() + 30
        while True:
            try:
                self.pipe = os.open(pipe, os.O_WRONLY | os.O_NONBLOCK)
                break
            except OSError:
                if time.time() > deadline:
                    raise RuntimeError("Dolphin never opened the input pipe")
                time.sleep(0.1)
        self.neutral()
        return self

    def __exit__(self, *exc):
        try:
            os.close(self.pipe)
        except Exception:
            pass
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self.log.close()

    # --- input -----------------------------------------------------------
    def send(self, *lines):
        os.write(self.pipe, ("".join(l + "\n" for l in lines)).encode())

    def neutral(self):
        self.send("SET MAIN 0.5 0.5", "SET C 0.5 0.5", "SET L 0", "SET R 0")

    def hold(self, button):
        self.send(f"PRESS {button}")

    def release(self, button):
        self.send(f"RELEASE {button}")

    def press(self, button, secs=0.1):
        self.hold(button)
        time.sleep(secs)
        self.release(button)
        time.sleep(secs)

    def stick(self, x, y):
        """x, y in -1..1."""
        self.send(f"SET MAIN {0.5 + x / 2:.3f} {0.5 + y / 2:.3f}")

    def cstick(self, x, y):
        self.send(f"SET C {0.5 + x / 2:.3f} {0.5 + y / 2:.3f}")

    # --- memory ----------------------------------------------------------
    def read(self, addr, n):
        # The stub sometimes answers E00 for a valid address; retry.
        for attempt in range(5):
            try:
                return self.gdb.read(addr, n)
            except RuntimeError:
                if attempt == 4 or not self.alive():
                    raise
                self.gdb.resume()
                time.sleep(0.2)

    def write(self, addr, data):
        gdb_write(self.gdb, addr, bytes(data))

    def read_u32(self, addr):
        return struct.unpack(">I", self.read(addr, 4))[0]

    def read_s32(self, addr):
        return struct.unpack(">i", self.read(addr, 4))[0]

    def read_f32(self, addr):
        return struct.unpack(">f", self.read(addr, 4))[0]

    def read_u8(self, addr):
        return self.read(addr, 1)[0]

    def alive(self):
        return self.proc.poll() is None

    def wait_for(self, cond, timeout=30, interval=0.1):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not self.alive():
                raise RuntimeError("Dolphin exited")
            try:
                if cond():
                    return True
            except RuntimeError:
                pass
            time.sleep(interval)
        return False
