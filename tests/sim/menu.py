"""The main menu (src/melee/tm/menu/), in the simulator: where each panel
leads and what the Controls page changes. Nothing is drawn here; for
pictures run tests/tmtest/menu/boot.json with tools/tmtest.py --shots.

    OVERLAY_OUT=build/overlay-tmtest TM_TEST=1 python tools/overlay_build.py
    python tests/sim/menu.py
"""
import sys

sys.path.insert(0, "tools/melee_sim")
from sim import Sim                      # noqa: E402
from machine import GuestError, ROOT     # noqa: E402

OUT = ROOT / "build/overlay-tmtest"
GS_MENU, GS_CSS, GS_OURS = 1, 8, 10      # GameSceneKind
GM_MENU, GM_EVENT = 1, 43                # GameModeKind

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


class Menu:
    def __init__(self):
        self.s = Sim(dol=OUT / "main.dol", overlay_map=OUT / "overlay.map")
        self.m = self.s.m
        self.s.boot()
        for _ in range(40):
            if self.scene() == GS_OURS:
                break
            self.s.press("A")        # the memory card prompt
        self.s.step(40)

    def scene(self):
        p = self.m.u32(self.m.sym.addr("gm_804D6720"))
        return self.m.u8(p) if p else -1

    def mode(self):
        return self.m.u8(self.m.sym.addr("state_machine"))

    def delay(self):
        return self.m.u8(self.m.sym.addr("tm_ctl"))

    def tap(self, wait=17, **pad):
        self.s.pad(0, **pad)
        self.s.step(3)
        self.s.pad(0)
        self.s.step(wait)


def main():
    try:
        m = Menu()
        check("booting lands on the main menu",
              m.scene() == GS_OURS and m.mode() == GM_MENU,
              "mode %d scene %d" % (m.mode(), m.scene()))

        m.tap(stick=(0, -1))                 # Train -> Controls
        m.tap(buttons=["A"])
        check("Controls opens a page of the same scene",
              m.scene() == GS_OURS)
        m.tap(stick=(1, 0))
        m.tap(stick=(1, 0))
        check("right raises the input delay", m.delay() == 2,
              "delay %d" % m.delay())
        m.tap(stick=(-1, 0))
        check("left lowers it", m.delay() == 1, "delay %d" % m.delay())
        for _ in range(14):
            m.tap(stick=(1, 0), wait=6)
        check("it stops at the maximum", m.delay() == 10,
              "delay %d" % m.delay())
        for _ in range(14):
            m.tap(stick=(-1, 0), wait=6)
        check("and at zero", m.delay() == 0, "delay %d" % m.delay())

        m.tap(buttons=["B"])                 # back to the main page
        m.tap(buttons=["A"], wait=90)        # Train
        check("Train goes to the event mode's character select",
              m.mode() == GM_EVENT and m.scene() == GS_CSS,
              "mode %d scene %d" % (m.mode(), m.scene()))
        m.s.pad(0, ["B"])                    # the character select wants
        m.s.step(90)                         # B held to leave
        m.s.pad(0)
        m.s.step(120)
        check("B there comes back to the main menu",
              m.scene() == GS_OURS, "mode %d scene %d" % (m.mode(),
                                                          m.scene()))

        m.tap(stick=(1, 0))                  # Train -> Lab
        m.tap(buttons=["A"], wait=90)
        check("Lab goes to a character select",
              m.mode() == GM_EVENT and m.scene() == GS_CSS,
              "mode %d scene %d" % (m.mode(), m.scene()))

        m2 = Menu()
        m2.tap(stick=(1, 0))                 # Lab
        m2.tap(stick=(0, -1))                # Events
        m2.tap(buttons=["A"], wait=120)
        check("Events opens the original menus",
              m2.mode() == GM_MENU and m2.scene() == GS_MENU,
              "mode %d scene %d" % (m2.mode(), m2.scene()))
    except GuestError as e:
        check("the game kept running", False, str(e)[:300])

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
