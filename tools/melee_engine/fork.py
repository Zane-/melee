"""Thinking in a forked copy of the game (src/host/engine.c, "engine
fork"): the game forks at a frame boundary, and the copy, standing at that
frame, answers searches and lookaheads on a pipe of its own while the game
goes on. A decision is thought out there, in a thread, while a person
plays the window build, and nothing of it is waited for in the frame they
are watching (docs/ai/melee-engine.md, "Thinking while a person plays").

    with Fork(n) as f:                # n: a Native (the window, headless)
        r = search(f, port=1, target=0, horizon=60, budget=800, depth=2)

    think = InFork(n)                 # for melee_engine.jumpin.JumpIn
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
    jumpin.py ask of a game (`_cmd`, `_reply`, `state`, `fighter`) it
    answers."""

    def __init__(self, n, timeout=10.0):
        self.timeout = timeout
        self.log = []
        self._state = None
        self._pending = b""
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

    def _line(self):
        while b"\n" not in self._pending:
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
        self.errors = []
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
            except Exception as e:
                self.errors.append(repr(e))
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
        except Exception as e:           # reported, and nothing decided
            self.errors.append(repr(e))
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
