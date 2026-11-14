"""Rollback netcode between two games, checked headless over loopback.

    python tests/native/netplay.py [--frames N] [--lag L] [--loss P]
                                   [--jitter J] [--delay D] [--seed S]

Two headless games (src/host/net.c), each playing one port of the same
match with random inputs (a person's: held a few frames), connected over
UDP on this machine through a simulated network: packets held LAG of the
sender's frames, up to JITTER more, LOSS percent dropped. Checked:

- the sessions run: inputs cross, rollbacks happen when guesses were wrong
  and never go deeper than the game allows;
- no desync: the sides' hashes of the fighters and the random seed agree
  at every frame both checked (every 30);
- both end in the same game at the same frame, and a third game, offline,
  fed the inputs the sides actually played each frame with, ends in that
  same game: rollback played every frame as if the inputs had been known.

Runs with no lag and with a lossy, laggy network.
"""
import argparse
import json
import os
import random
import socket
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from native import Native  # noqa: E402
from state import inputs, view  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def set_raw(n, port, pad):
    p = n.h.pads[port]
    p.update(connected=True, **pad)
    n._dirty.add(port)


def session(args, lag, loss, jitter, label):
    seed = args.seed
    script = inputs(seed, args.frames)
    a, b = Native(), Native()
    try:
        for n in (a, b):
            n.start("fox", "marth", "final-destination", seed)
            n.step(30)
        same_start = view(a) == view(b) and \
            a.net("hash") == b.net("hash")
        pa, pb = free_port(), free_port()
        a.net("start", 0, pa, "127.0.0.1", pb, args.delay, lag, loss, jitter)
        b.net("start", 1, pb, "127.0.0.1", pa, args.delay, lag, loss, jitter)
        # each side's person: its port of the script, one input per frame
        # of real time
        for tick in range(args.frames):
            a.pad(0, **script[tick][0])
            b.pad(1, **script[tick][1])
            a.step()
            b.step()
        # hands off, until both have played the same frames and know all
        # the inputs of them
        for n, port in ((a, 0), (b, 1)):
            n.pad(port)
        for _ in range(400):
            sa, sb = a.net("stats"), b.net("stats")
            if sa["frame"] == sb["frame"] and \
                    sa["confirmed"] >= sa["frame"] - 1 and \
                    sb["confirmed"] >= sb["frame"] - 1:
                break
            if sa["frame"] > sb["frame"]:
                b.step()
            elif sb["frame"] > sa["frame"]:
                a.step()
            else:
                a.step()
                b.step()
        sa, sb = a.net("stats"), b.net("stats")
        print("     %s: %d frames; A %d rollbacks (%d frames, deepest %d), "
              "%d waits; B %d rollbacks (%d, %d), %d waits; %d+%d hash "
              "checks" % (label, sa["frame"], sa["rollbacks"], sa["rolled"],
                          sa["max_rollback"], sa["stalls"], sb["rollbacks"],
                          sb["rolled"], sb["max_rollback"], sb["stalls"],
                          sa["checks"], sb["checks"]))
        check("%s: both start from the same game" % label, same_start)
        check("%s: the sessions run and inputs cross" % label,
              sa["frame"] > args.frames // 2 and sa["received"] > 0 and
              sb["received"] > 0, "A at %d, B at %d" % (
                  sa["frame"], sb["frame"]))
        if lag or loss or jitter:
            check("%s: wrong guesses are rolled back, never deeper than 8 "
                  "frames" % label, sa["rollbacks"] + sb["rollbacks"] > 0
                  and max(sa["max_rollback"], sb["max_rollback"]) <= 8,
                  "%d and %d" % (sa["rollbacks"], sb["rollbacks"]))
        check("%s: no desync in %d checks" % (label,
                                             sa["checks"] + sb["checks"]),
              not sa["desync"] and not sb["desync"] and
              sa["checks"] + sb["checks"] > 0)
        end = sa["frame"]
        check("%s: both end in the same game at frame %d" % (label, end),
              sa["frame"] == sb["frame"] and view(a) == view(b) and
              a.net("hash") == b.net("hash"),
              "A %s / B %s" % (view(a), view(b)))
        # the inputs each frame was played with, from the side that made
        # them
        played = []
        for f in range(end):
            ia, ib = a.net("input", f), b.net("input", f)
            played.append((ia["local"], ib["local"]))
        final_a = (view(a), a.net("hash"))
        if os.environ.get("NET_DEBUG"):
            for n in (a, b):
                st = n.state()
                print("DBG", n.net("hash"), json.dumps(st["p"][:2])[:600],
                      st.get("seed"))
    finally:
        a.close()
        b.close()
    # offline: the same match, the same inputs, no network; drawn as the
    # sides draw every frame (drawing moves the random numbers through the
    # particles it starts: src/host/net.c)
    with Native(draw=True) as c:
        c.start("fox", "marth", "final-destination", seed)
        c.step(30)
        for p0, p1 in played:
            set_raw(c, 0, p0)
            set_raw(c, 1, p1)
            c.step()
        offline = (view(c), c.net("hash"))
        if os.environ.get("NET_DEBUG"):
            st = c.state()
            print("DBG offline", offline[1], json.dumps(st["p"][:2])[:600],
                  st.get("seed"))
    check("%s: an offline game fed those inputs ends in the same game"
          % label, offline == final_a, "%s / %s" % (offline[0], final_a[0]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--frames", type=int, default=600)
    ap.add_argument("--delay", type=int, default=2)
    ap.add_argument("--lag", type=int, default=4)
    ap.add_argument("--loss", type=int, default=10)
    ap.add_argument("--jitter", type=int, default=3)
    ap.add_argument("--seed", type=int, default=5)
    args = ap.parse_args()
    session(args, 0, 0, 0, "no lag")
    session(args, args.lag, args.loss, args.jitter,
            "%d frames' lag, %d%% loss, %d jitter" % (
                args.lag, args.loss, args.jitter))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
