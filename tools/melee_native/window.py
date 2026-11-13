"""The window build of the native game (build/native-window/melee_native,
`tools/native_build.py --window`), run where nothing can appear on the
desktop: on a virtual X server of its own, drawn by a software renderer
(OpenGL ES on llvmpipe) unless asked otherwise.

    from window import Window
    with Window() as w:
        w.start("fox", "marth")
        w.step(60)
        w.shot("/tmp/frame.png")          # what is on the virtual screen

    python tools/melee_native/window.py --out DIR [--match fox,marth,final-destination]
                                        [--frames 30,120,300] [--gpu]

`Window(real=True)` instead opens the window on the desktop this process
was started from (tools/melee_native/play.py does, for a person to play).

A port can be handed to a person (`live(port)`: a controller, or the
keyboard) and the game slowed to the console's speed (`pace()`); the rest
of the interface is unchanged, so a script can drive the other fighter and
read the state while they play. `key()` presses keys on the virtual display,
for tests.

`Window` is a `Native` (tools/melee_native/native.py) whose game has a
display. The X server and the game are each a process group of their own
and both are killed on close; `leftovers()` looks for any that survived, by
executable path (the game's process renames itself, so its name does not
find it) and by the mark of the driver that started them (a game someone
else has open is not a leftover).
"""
import argparse
import ctypes
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from native import (HARNESS, Native, NativeError, ROOT,  # noqa: E402
                    die_with_parent)

EXE = ROOT / "build/native-window/melee_native"


def _started_by(pid):
    """The pid of the driver that started process `pid`, or None if no
    driver did (someone ran it by hand) or it cannot be told."""
    try:
        with open("/proc/%s/environ" % pid, "rb") as f:
            for item in f.read().split(b"\0"):
                if item.startswith(HARNESS.encode() + b"="):
                    return int(item.split(b"=", 1)[1])
    except (OSError, ValueError):
        pass
    return None


def leftovers():
    """PIDs of window-build games and of virtual X servers that a driver
    started and that outlived it: started by this process, or by one that
    is gone. A game someone else has open (the owner playing the client,
    another test) is theirs: it is not listed, and so never killed by what
    acts on this list. (It once was listed, by executable path alone.)"""
    out = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            exe = os.readlink("/proc/%s/exe" % pid)
            with open("/proc/%s/cmdline" % pid, "rb") as f:
                cmd = f.read().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            continue
        if not (exe.endswith("/melee_native") or (
                exe.endswith("/Xvfb") and "melee-window" in cmd)):
            continue
        by = _started_by(pid)
        if by == os.getpid() or (
                by is not None and not os.path.exists("/proc/%d" % by)):
            out.append(int(pid))
    return out


class Window(Native):
    def __init__(self, gpu=False, size=(800, 600), verbose=False,
                 timeout=120, state_dir=None, real=False, vsync=False,
                 window=(640, 480)):
        if not EXE.exists():
            raise NativeError("no window build: run tools/aurora32/build.sh "
                              "and tools/native_build.py --window")
        self.x = None
        self.display = None
        self._xlib = None
        self.window = tuple(window)   # the game's window, in pixels
        size = (max(size[0], window[0] + 40), max(size[1], window[1] + 40))
        if real:
            # the desktop this was started from, and its GPU
            env = dict(os.environ)
        else:
            env = self._virtual_display(size, state_dir)
            if not gpu:
                # Software OpenGL ES (llvmpipe). The software Vulkan driver
                # (lavapipe) crashes inside its compiler in this 32-bit
                # process, a few frames in.
                env["MELEE_BACKEND"] = "gles"
                env["LIBGL_ALWAYS_SOFTWARE"] = "1"
        if vsync:
            env["MELEE_VSYNC"] = "1"
        env["MELEE_WINDOW_SIZE"] = "%dx%d" % self.window
        try:
            super().__init__(exe=EXE, verbose=verbose, timeout=timeout,
                             env=env)
        except Exception:
            self._kill_x()
            raise

    def _virtual_display(self, size, state_dir):
        # A display of our own: Xvfb picks a free number and writes it to
        # the pipe. The fake "-fp" entry only marks the process as ours.
        r, w = os.pipe()
        self.x = subprocess.Popen(
            ["Xvfb", "-displayfd", str(w), "-screen", "0",
             "%dx%dx24" % size, "-nolisten", "tcp", "-fp",
             "/melee-window/fonts,built-ins"],
            pass_fds=[w], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True,
            env=dict(os.environ, **{HARNESS: str(os.getpid())}),
            preexec_fn=die_with_parent)
        os.close(w)
        number = b""
        deadline = time.time() + 10
        while not number.endswith(b"\n") and time.time() < deadline:
            chunk = os.read(r, 16)
            if not chunk:
                break
            number += chunk
        os.close(r)
        if not number.strip():
            self._kill_x()
            raise NativeError("the virtual X server did not start")
        self.display = ":" + number.decode().strip()

        state = Path(state_dir or os.environ.get("CLAUDE_JOB_DIR", "/tmp")) \
            / "tmp" / "melee-window-xdg"
        state.mkdir(parents=True, exist_ok=True)
        env = {k: v for k, v in os.environ.items()
               if k not in ("WAYLAND_DISPLAY", "XAUTHORITY")}
        env.update(DISPLAY=self.display, SDL_VIDEODRIVER="x11",
                   XDG_DATA_HOME=str(state), XDG_CACHE_HOME=str(state),
                   XDG_CONFIG_HOME=str(state),
                   # its own shader cache: the one beside the executable
                   # belongs to whoever is playing
                   MELEE_STATE_DIR=str(state / "aurora"))
        return env

    # ---- a person at the controls -------------------------------------------

    def devices(self):
        """What there is to play with, in a line: the GameCube adapter's
        state and the controllers SDL knows. Starts looking for the
        adapter."""
        return self._cmd("devices")

    def live(self, port=0, source="auto"):
        """Hand a port to a person: "auto" (a GameCube controller on the
        adapter if there is one, else the first controller SDL knows, else
        the keyboard), "keyboard", "gcc" / "gccN" (the adapter's port N,
        from 1), "pad" / "padN" (the Nth controller SDL lists), or "off" to
        take it back for pad()."""
        self._cmd("live %d %s" % (port, source))

    def pace(self, on=True):
        """Run at the console's speed (59.94 frames a second) instead of
        as fast as the machine goes."""
        self._cmd("pace %d" % (1 if on else 0))

    # ---- the client's interface (src/host/ui.cpp) ---------------------------

    def ui(self, command):
        """One command to the interface: "load PATH", "class ID NAME 1",
        "text ID RML", "hide", "show", "font PATH", "attr ID NAME VALUE"."""
        self._cmd("ui " + command)

    def capture(self, on=True):
        """Keep the live ports' presses from the game (a menu is up)."""
        self._cmd("capture %d" % (1 if on else 0))

    def pads(self):
        """What the people at the live ports are holding, whether or not
        the game sees it: four dicts of buttons (a bit mask), lx, ly, cx,
        cy (-127..127), lt, rt (0..255)."""
        words = self._cmd("pads").split()
        out = []
        for i in range(4):
            w = words[i * 7:i * 7 + 7]
            out.append(dict(buttons=int(w[0], 16), lx=int(w[1]),
                            ly=int(w[2]), cx=int(w[3]), cy=int(w[4]),
                            lt=int(w[5]), rt=int(w[6])))
        return out

    def key(self, name, down=True):
        """Press or release a key on the virtual display, by its X name
        ("Right", "x", "Return", "Shift_L"). For tests."""
        if self.display is None:
            raise NativeError("key() is for the virtual display only")
        if self._xlib is None:
            x = ctypes.CDLL("libX11.so.6")
            t = ctypes.CDLL("libXtst.so.6")
            x.XOpenDisplay.restype = ctypes.c_void_p
            x.XOpenDisplay.argtypes = [ctypes.c_char_p]
            x.XStringToKeysym.restype = ctypes.c_ulong
            x.XStringToKeysym.argtypes = [ctypes.c_char_p]
            x.XKeysymToKeycode.restype = ctypes.c_ubyte
            x.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
            x.XFlush.argtypes = [ctypes.c_void_p]
            x.XCloseDisplay.argtypes = [ctypes.c_void_p]
            t.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint,
                                            ctypes.c_int, ctypes.c_ulong]
            t.XTestFakeMotionEvent.argtypes = [
                ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                ctypes.c_ulong]
            dpy = x.XOpenDisplay(self.display.encode())
            if not dpy:
                raise NativeError("cannot open the virtual display")
            # with no window manager, keys go to the window under the
            # pointer: put it on the game's
            t.XTestFakeMotionEvent(dpy, 0, 320, 240, 0)
            self._xlib = (x, t, dpy)
        x, t, dpy = self._xlib
        code = x.XKeysymToKeycode(dpy, x.XStringToKeysym(name.encode()))
        if not code:
            raise NativeError("no such key: " + name)
        t.XTestFakeKeyEvent(dpy, code, 1 if down else 0, 0)
        x.XFlush(dpy)

    def shot(self, path):
        """Save what is on the virtual screen as a picture."""
        if self.display is None:
            raise NativeError("shot() is for the virtual display only")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # the game's window is at the corner of the screen
        r = subprocess.run(["import", "-display", self.display, "-window",
                            "root", "-crop", "%dx%d+0+0" % self.window,
                            "+repage",
                            str(path)], capture_output=True,
                           text=True, timeout=30)
        if r.returncode:
            raise NativeError("screenshot failed: " + r.stderr.strip()[:200])
        return path

    def _kill_x(self):
        if self._xlib is not None:
            self._xlib[0].XCloseDisplay(self._xlib[2])
            self._xlib = None
        if self.x is None:
            return
        try:
            os.killpg(self.x.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            self.x.wait(timeout=5)
        except Exception:
            pass

    def close(self):
        try:
            super().close()
        finally:
            self._kill_x()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, help="directory for pictures")
    ap.add_argument("--match", default="fox,marth,final-destination")
    ap.add_argument("--frames", default="30,120,300",
                    help="frames after the match is up to take pictures at")
    ap.add_argument("--boot", action="store_true",
                    help="no match: pictures of the first screens")
    ap.add_argument("--gpu", action="store_true",
                    help="draw with the machine's GPU instead of software")
    ap.add_argument("-v", action="store_true")
    args = ap.parse_args()
    if not shutil.which("Xvfb") or not shutil.which("import"):
        sys.exit("needs Xvfb and ImageMagick's import")
    marks = sorted(int(x) for x in args.frames.split(","))
    try:
        with Window(gpu=args.gpu, verbose=args.v) as w:
            try:
                if not args.boot:
                    p1, p2, stage = args.match.split(",")
                    w.start(p1, p2, stage, settle=False)
                at = 0
                for mark in marks:
                    w.step(mark - at)
                    at = mark
                    print("frame +%d: %s" % (mark, w.shot(
                        Path(args.out) / ("frame_%04d.png" % mark))))
            except NativeError as e:
                print("stopped: %s" % str(e)[:3000])
                print("".join(w.log[-25:]))
                return 1
    finally:
        left = leftovers()
        if left:
            print("LEFT RUNNING:", left)
            for pid in left:
                os.kill(pid, signal.SIGKILL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
