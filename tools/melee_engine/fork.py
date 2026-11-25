"""Thinking in a forked copy of the game (src/host/engine.c, "engine
fork"): the game forks at a frame boundary, and the copy, standing at that
frame, answers searches and lookaheads on a pipe of its own while the game
goes on. A decision is thought out there, in a thread, while a person
plays the window build, and nothing of it is waited for in the frame they
are watching (docs/ai/melee-engine.md, "Thinking while a person plays").

    with Fork(n) as f:                # n: a Native (the window, headless)
        r = search(f, port=1, target=0, horizon=60, budget=800, depth=2)

    think = InFork(n)                 # for melee_engine.drill.EngineOpponent
    think.submit(tag, fn)             # fn(fork) runs in a thread
    think.ready(tag), think.result(tag)

A forked game is the window build too (the same addresses: it is a copy of
the process), but it draws nothing, plays no frame for real, and leaves when
its pipe closes. Unlike a shadow game (shadow.py) it needs nothing kept in
step: it is the game, as it is at that frame.
"""
import math
import os
import select
import shutil
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "melee_native"))

from native import Fighter, NativeError, _json  # noqa: E402


class Fork:
    """A copy of the game at the frame it was forked at. What search.py and
    contracts.py ask of a game (`_cmd`, `_reply`, `state`, `fighter`) it
    answers."""

    def __init__(self, n, timeout=10.0):
        self.timeout = timeout
        self.log = []
        self._state = None
        self._pending = b""
        self._chunks = None
        self.p = None
        if sys.platform == "win32":
            self._start_win32(n)
            return
        base = "/dev/shm" if os.path.isdir("/dev/shm") else None
        self._dir = tempfile.mkdtemp(prefix="melee-fork-", dir=base)
        inp, out = (os.path.join(self._dir, x) for x in ("in", "out"))
        os.mkfifo(inp)
        os.mkfifo(out)
        # both ends held here first (read and write), so that neither the
        # copy's opening nor ours waits for the other
        self._w = os.open(inp, os.O_RDWR)
        self._r = os.open(out, os.O_RDWR)
        try:
            reply = n._cmd("engine fork %s %s" % (inp, out))
            self.pid = int(reply.split()[1])
            first = self._reply()
            if first != "ok fork":
                raise NativeError("a forked game said " + first)
        except Exception:
            self.close()
            raise
        finally:
            shutil.rmtree(self._dir, ignore_errors=True)
        self.frame = None

    def _start_win32(self, n):
        """Windows has no fork(): the game leaves its state in a named
        section ("engine fork-state"), and the copy is this program again,
        started with `--fork-child NAME`, which loads it at its first frame
        boundary and answers "ok fork" (src/host/engine.c). Its stdin and
        stdout are the pipe, as for Native."""
        import queue
        import subprocess
        from native import die_with_parent_win32

        name = n._cmd("engine fork-state").split()[1]
        self.p = subprocess.Popen(
            [str(n.exe), "--disc", str(n.disc), "--fork-child", name],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        die_with_parent_win32(self.p.pid)
        self.pid = self.p.pid
        self._w = None
        self._r = self.p.stdout.fileno()
        self._chunks = queue.Queue()

        def read():
            while True:
                try:
                    chunk = os.read(self._r, 65536)
                except OSError:
                    chunk = b""
                self._chunks.put(chunk)
                if not chunk:
                    return

        threading.Thread(target=read, daemon=True).start()
        try:
            first = self._reply()
            if first != "ok fork":
                raise NativeError("a forked game said " + first)
        except Exception:
            self.close()
            raise
        finally:
            # loaded (or failed): the section is no longer needed
            try:
                n._cmd("engine fork-release " + name)
            except NativeError:
                pass
        self.frame = None

    def _line(self):
        while b"\n" not in self._pending:
            if self._chunks is not None:
                import queue
                try:
                    chunk = self._chunks.get(timeout=self.timeout)
                except queue.Empty:
                    raise NativeError("no reply from a forked game in %g s"
                                      % self.timeout)
                if not chunk:
                    return ""
                self._pending += chunk
                continue
            if not select.select([self._r], [], [], self.timeout)[0]:
                raise NativeError("no reply from a forked game in %g s"
                                  % self.timeout)
            chunk = os.read(self._r, 65536)
            if not chunk:
                return ""
            self._pending += chunk
        line, _, self._pending = self._pending.partition(b"\n")
        return line.decode(errors="replace") + "\n"

    def _reply(self):
        while True:
            line = self._line()
            if not line or line.startswith("@ fatal"):
                raise NativeError("a forked game stopped: " + line +
                                  "".join(self.log[-20:]))
            if line.startswith("@ "):
                return line[2:].rstrip("\n")
            self.log.append(line)

    def _cmd(self, text):
        self._state = None
        if self.p is not None:
            self.p.stdin.write((text + "\n").encode())
            self.p.stdin.flush()
        else:
            os.write(self._w, (text + "\n").encode())
        reply = self._reply()
        if reply.startswith("error"):
            raise NativeError(reply)
        return reply

    def state(self):
        if self._state is None:
            self._state = _json(self._cmd("state"))
        return self._state

    def fighter(self, i):
        return Fighter(self.state()["p"][i])

    def close(self):
        if self.p is not None:
            # its input closes: a forked game leaves (control.c)
            try:
                self.p.stdin.close()
            except OSError:
                pass
            try:
                self.p.wait(timeout=5)
            except Exception:
                self.p.kill()
            self.p = None
            return
        for fd in ("_w", "_r"):
            v = getattr(self, fd, None)
            if v is not None:
                try:
                    os.close(v)
                except OSError:
                    pass
                setattr(self, fd, None)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class InFork:
    """Decisions thought out in forked copies of the game, each in a thread
    of its own: `submit` forks at this frame (the copy then stands there)
    and returns at once. Each decision is for a frame some frames on
    (`lead_for(kind)`), which follows how long decisions of that kind take
    (at the console's 60 frames a second), so that they come back in time:
    a jump planned far ahead, a correction in the air a few frames on."""

    FRAME = 1.0 / 60
    timed = True              # its decisions are on the clock (recover.Pilot)
    # the longest lead of a kind: a correction in the air decided further
    # ahead than this comes too late to matter (the arc is over), so one
    # that takes longer is dropped, not waited for
    MOST = {"replan": 24}

    def __init__(self, n, lead=12, most=45):
        self.n = n
        self.lead = lead
        self.most = most
        self.results = {}
        self.lock = threading.Lock()
        self.took = {}            # kind: seconds each decision took
        self.leads = {}           # kind: its lead
        # The thinking is threads of this process, beside the client's
        # own (its interface, drawn in Python each frame), and all of them
        # take turns at the interpreter: a thread that has waited for the
        # game's answer waits again for its turn, up to the interpreter's
        # switch interval each time (5 ms by default). A tenth of that:
        # the turns come round at once. (It is not why a copy of the game
        # costs more beside the client than alone, as this comment said
        # until 2026-11-24: measured then, a copy's cost follows the
        # memory of the process forked, 0.3 ms headless at 81 MB, 6.7 ms
        # in the window build drawing in software at 799 MB, 3.7 ms on the
        # graphics card; the client's Python is 0.4 ms of a frame.)
        if sys.getswitchinterval() > 0.0005:
            sys.setswitchinterval(0.0005)
        self.errors = []          # decisions that raised: tracebacks
        self.said = set()         # the faults already said
        self.forgotten = set()    # decisions no longer wanted

    def realtime(self):
        """Whether the frames are a person's to watch, at the console's
        pace. Frames played unseen, as fast as they go (the coach's
        demonstration, a load), can wait: decisions are made there and
        then, in the game itself."""
        return getattr(self.n, "paced", False) and \
            not getattr(self.n, "quieted", 0)

    def lead_for(self, kind):
        if not self.realtime():
            return 0
        with self.lock:
            return self.leads.get(kind, self.lead)

    def submit(self, tag, fn, kind="any"):
        if not self.realtime():
            out = None
            try:
                out = fn(self.n)
            except Exception:
                self._fault()
            with self.lock:
                self.results[tag] = out
            return
        child = Fork(self.n)
        t = threading.Thread(target=self._run, args=(tag, fn, child, kind),
                             daemon=True)
        t.start()

    def _run(self, tag, fn, child, kind):
        t0 = time.time()
        out = None
        try:
            out = fn(child)
        except Exception:                # reported, and nothing decided
            self._fault()
        finally:
            child.close()
        took = time.time() - t0
        with self.lock:
            if tag in self.forgotten:
                self.forgotten.discard(tag)
            else:
                self.results[tag] = out
            took_kind = self.took.setdefault(kind, [])
            took_kind.append(took)
            # the second slowest of the last few: a decision that needs its
            # time (a correction searched for) is the one that must not be
            # late; one slowed by something else is not followed
            recent = sorted(took_kind[-8:])
            slow = recent[-2] if len(recent) >= 3 else recent[-1]
            most = self.MOST.get(kind, self.most)
            self.leads[kind] = max(3, min(most, int(math.ceil(
                slow / self.FRAME)) + 2))

    def _fault(self):
        """A decision that raised: kept (`errors`: its traceback), and
        said once for each kind of fault, where the client was started
        (until 2026-11-17 nothing showed them, and an opponent whose
        every decision failed stood there or fell)."""
        import sys
        import traceback
        text = traceback.format_exc()
        last = text.strip().splitlines()[-1]
        with self.lock:
            self.errors.append(text)
            new = last not in self.said
            self.said.add(last)
        if new:
            print("the opponent's thinking failed (said once):\n" + text,
                  file=sys.stderr, flush=True)

    def ready(self, tag):
        with self.lock:
            return tag in self.results

    def result(self, tag):
        with self.lock:
            return self.results.pop(tag, None)

    def forget(self, tag):
        """A decision that came too late: dropped when it comes."""
        with self.lock:
            if self.results.pop(tag, None) is None:
                self.forgotten.add(tag)
