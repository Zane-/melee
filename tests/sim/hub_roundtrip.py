#!/usr/bin/env python3
"""Simulator test of the course hub (src/tmce/events/course/hub_css.c).

    OVERLAY_OUT=build/overlay python tests/sim/hub_roundtrip.py

Needs a normal (not TM_TEST) overlay that boots into the course event (the
default) and files/TM/hubCSS.dat on build/disc (tools/tmce_disc.py).
Boots, picks Fox, presses START (the hub must open instead of the match),
moves between sections, closes with B, reopens, starts the first Punish
drill, exits the drill (the hub must reopen by itself), and starts it again.
No Dolphin involved; see docs/ai/simulator.md.
"""

import os
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "melee_sim"))
from sim import Sim  # noqa: E402

OUT = ROOT / os.environ.get("OVERLAY_OUT", "build/overlay")
EXITKIND = 0x804D6CF6       # mnCharSel_804D6CF6: 5 while a submenu is open
PLAYER_SLOTS = 0x80453080
FOX_ICON = (-20.9, 9.5)     # cursor position over Fox's icon (mncharsel.c)
CKIND_FOX = 2


def main():
    s = Sim(dol=OUT / "main.dol", overlay_map=OUT / "overlay.map")
    m = s.m
    checks = []

    def check(name, ok):
        checks.append((name, bool(ok)))
        print("%-58s %s" % (name, "ok" if ok else "FAILED"), flush=True)

    def in_match():
        return m.read(0x80479D30, 4)[3] == 1 and m.u32(PLAYER_SLOTS + 0xB0)

    def wait(cond, frames=600):
        for _ in range(frames):
            if cond():
                return True
            s.step()
        return False

    def sym(name):
        return m.sym.addr(name)

    s.boot_to_css()
    cur = m.u32(sym("mnCharSel_804A0BC0"))
    m.write(cur + 0xC, struct.pack(">ff", *FOX_ICON))
    s.step(5)
    s.press("A")
    s.press("START", wait=30)
    check("START with a character opens the hub, not the match",
          m.u8(EXITKIND) == 5 and not in_match())
    part = m.u32(sym("Course_HubPart"))
    s.press("RIGHT", wait=10)
    check("right moves to the next section",
          m.u32(sym("Course_HubPart")) == (part + 1) % 5)
    s.press("LEFT", wait=10)
    check("left moves back", m.u32(sym("Course_HubPart")) == part)
    s.press("B", wait=30)
    check("B closes the hub", m.u8(EXITKIND) == 0)
    s.press("START", wait=30)
    check("START opens it again", m.u8(EXITKIND) == 5)
    s.press("A", wait=5)
    check("A starts the drill", wait(in_match))
    s.step(120)
    check("the player is Fox", m.u32(PLAYER_SLOTS + 4) == CKIND_FOX)

    # The drill's Exit (a local of the course unit: find it in the map).
    exit_addr = None
    pat = re.compile(r"\s*[0-9a-f]{8}\s+[0-9a-f]{6}\s+([0-9a-f]{8})\s+\d+"
                     r"\s+Event_Exit\s+course")
    for line in open(OUT / "overlay.map", errors="replace"):
        mm = pat.match(line)
        if mm:
            exit_addr = int(mm[1], 16)
    s.call(exit_addr, 0)
    check("Exit returns to the character select",
          wait(lambda: m.read(0x80479D30, 4)[3] == 0 and
               m.u32(sym("mnCharSel_804A0BC0"))))
    check("the hub reopens by itself",
          wait(lambda: m.u8(EXITKIND) == 5, 120) and
          m.u32(sym("Course_HubReturn")) == 0)
    s.press("A", wait=5)
    check("A starts the drill again", wait(in_match))
    s.step(60)
    check("still as Fox", m.u32(PLAYER_SLOTS + 4) == CKIND_FOX)

    failed = [n for n, ok in checks if not ok]
    print("%d of %d checks passed" % (len(checks) - len(failed), len(checks)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
