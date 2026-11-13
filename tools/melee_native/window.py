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

`Window` is a `Native` (tools/melee_native/native.py) whose game has a
display. The X server and the game are each a process group of their own
and both are killed on close; `leftovers()` looks for any that survived, by
executable path (the game's process renames itself, so its name does not
find it).
"""
import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from native import Native, NativeError, ROOT  # noqa: E402

EXE = ROOT / "build/native-window/melee_native"


def leftovers():
    """PIDs of window-build games and of virtual X servers started here
    that are still alive."""
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
        if exe.endswith("/melee_native") or (
                exe.endswith("/Xvfb") and "melee-window" in cmd):
            out.append(int(pid))
    return out


class Window(Native):
    def __init__(self, gpu=False, size=(800, 600), verbose=False,
                 timeout=120, state_dir=None):
        if not EXE.exists():
            raise NativeError("no window build: run tools/aurora32/build.sh "
                              "and tools/native_build.py --window")
        # A display of our own: Xvfb picks a free number and writes it to
        # the pipe. The fake "-fp" entry only marks the process as ours.
        r, w = os.pipe()
        self.x = subprocess.Popen(
            ["Xvfb", "-displayfd", str(w), "-screen", "0",
             "%dx%dx24" % size, "-nolisten", "tcp", "-fp",
             "/melee-window/fonts,built-ins"],
            pass_fds=[w], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True)
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
                   XDG_CONFIG_HOME=str(state))
        if not gpu:
            # Software OpenGL ES (llvmpipe). The software Vulkan driver
            # (lavapipe) crashes inside its compiler in this 32-bit
            # process, a few frames in.
            env["MELEE_BACKEND"] = "gles"
            env["LIBGL_ALWAYS_SOFTWARE"] = "1"
        try:
            super().__init__(exe=EXE, verbose=verbose, timeout=timeout,
                             env=env)
        except Exception:
            self._kill_x()
            raise

    def shot(self, path):
        """Save what is on the virtual screen as a picture."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # the game's window is 640 by 480 at the corner of the screen
        r = subprocess.run(["import", "-display", self.display, "-window",
                            "root", "-crop", "640x480+0+0", "+repage",
                            str(path)], capture_output=True,
                           text=True, timeout=30)
        if r.returncode:
            raise NativeError("screenshot failed: " + r.stderr.strip()[:200])
        return path

    def _kill_x(self):
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
