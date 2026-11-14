"""Finding a friend online: the lobby, checked on this machine.

    python tests/client/online_lobby.py [--stun]

tools/melee_client/online.py: codes carry the public and the LAN address
and read back; two lobbies on this machine find each other from each
other's codes (LAN addresses here: no STUN), agree who plays port 1 and
port 2, and on the same stage, seed, delay and characters; a plain
"ip:port" works as a code. With --stun, one binding request to a public STUN
server (it learns this machine's public address, as any STUN use does) and
the mapped address it gives back.
"""
import argparse
import os
import sys
import threading

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))

import online  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def meet_both(a, b, code_a, code_b):
    got = {}

    def run(name, lobby, friend, me):
        try:
            got[name] = lobby.meet(friend, me, stage="battlefield", delay=3,
                                   timeout=10)
        except Exception as e:
            got[name] = e
    ta = threading.Thread(target=run, args=("a", a, code_b, dict(
        nick="Zed", char="fox", color=1)))
    tb = threading.Thread(target=run, args=("b", b, code_a, dict(
        nick="Amy", char="marth", color=2)))
    ta.start()
    tb.start()
    ta.join()
    tb.join()
    return got["a"], got["b"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stun", action="store_true")
    args = ap.parse_args()

    code = online.make_code(("203.0.113.7", 50123), ("192.168.1.20", 50123))
    check("a code reads back to its two addresses",
          online.read_code(code) == [("203.0.113.7", 50123),
                                     ("192.168.1.20", 50123)], code)
    check("a plain ip:port is read as one",
          online.read_code("10.0.0.5:7777") == [("10.0.0.5", 7777)])

    a = online.Lobby(use_stun=False)
    b = online.Lobby(use_stun=False)
    # on one machine the public address is the LAN one
    ra, rb = meet_both(a, b, a.code, b.code)
    a.close()
    b.close()
    ok = isinstance(ra, dict) and isinstance(rb, dict)
    check("two lobbies meet from each other's codes", ok,
          "" if ok else "%s / %s" % (ra, rb))
    if ok:
        check("one plays port 1, the other port 2",
              {ra["local"], rb["local"]} == {0, 1})
        check("they agree on stage, seed, delay, characters and colours",
              all(ra[k] == rb[k] for k in ("stage", "seed", "delay",
                                           "chars", "colors")) and
              ra["stage"] == "battlefield" and ra["delay"] == 3,
              "%s / %s" % ({k: ra[k] for k in ("stage", "seed", "chars")},
                           {k: rb[k] for k in ("stage", "seed", "chars")}))
        mine = ra["chars"][ra["local"]]
        check("each side's own character is its port's",
              mine == "fox" and rb["chars"][rb["local"]] == "marth",
              str(ra["chars"]))
        check("each knows the other's address and its own port to bind",
              ra["peer"][1] == b.port and rb["peer"][1] == a.port and
              ra["bind"] == a.port)

    a = online.Lobby(use_stun=False)
    b = online.Lobby(use_stun=False)
    ra, rb = meet_both(a, b, "127.0.0.1:%d" % a.port,
                       "127.0.0.1:%d" % b.port)
    a.close()
    b.close()
    check("plain ip:port codes meet too", isinstance(ra, dict) and
          isinstance(rb, dict) and ra["seed"] == rb["seed"])

    if args.stun:
        lobby = None
        try:
            lobby = online.Lobby(use_stun=True)
            check("a STUN server gives this machine's public address",
                  lobby.public[1] > 0 and lobby.public[0] != "0.0.0.0",
                  "port %d mapped to port %d" % (lobby.port,
                                                 lobby.public[1]))
        except online.OnlineError as e:
            check("a STUN server gives this machine's public address",
                  False, str(e))
        finally:
            if lobby is not None:
                lobby.close()
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
