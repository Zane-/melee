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

    def back_from_css(self):
        self.s.pad(0, ["B"])     # the character select wants B held
        self.s.step(90)
        self.s.pad(0)
        self.s.step(120)

    def tap(self, wait=17, **pad):
        self.s.pad(0, **pad)
        self.s.step(3)
        self.s.pad(0)
        self.s.step(wait)


# offsets in TmCtlSettings (src/melee/tm/controls/controls.h)
PORT_PROFILE, NAME_PROFILE, PROFILES, PROFILE_SIZE = 1, 5, 125, 22
P_USED, P_MAP = 9, 10
ACT_ATTACK, ACT_SPECIAL = 1, 2
NAMEDATA = 0x198                         # NameTagData.namedata
SAVE_SLOT = 7 * 19 - 1                   # where controls.c keeps the settings


def add_name(m, slot, text):
    """Put a nickname in the game's name list, as its name entry screen
    stores it: full-width characters, two bytes each."""
    at = m.s.call("GetPersistentNameData", slot)
    raw = b"".join(bytes([0x82, ord(c) + 0x1F]) for c in text)
    m.m.write(at + NAMEDATA, raw.ljust(8, b"\0"))


def main():
    try:
        m = Menu()
        ctl = m.m.sym.addr("tm_ctl")
        layout1 = ctl + PROFILES + PROFILE_SIZE
        check("booting lands on the main menu",
              m.scene() == GS_OURS and m.mode() == GM_MENU,
              "mode %d scene %d" % (m.mode(), m.scene()))

        # --- Controls: input delay ----------------------------------------
        m.tap(stick=(0, -1))                 # Train -> Controls
        m.tap(buttons=["A"])
        check("Controls opens a page of the same scene",
              m.scene() == GS_OURS)
        m.tap(buttons=["A"])
        m.tap(buttons=["R"])
        check("A and R raise the input delay", m.delay() == 2,
              "delay %d" % m.delay())
        m.tap(buttons=["L"])
        check("L lowers it", m.delay() == 1, "delay %d" % m.delay())
        for _ in range(9):
            m.tap(buttons=["A"], wait=6)
        check("it goes up to 10", m.delay() == 10, "delay %d" % m.delay())
        m.tap(buttons=["A"])
        check("and wraps to none", m.delay() == 0, "delay %d" % m.delay())

        # --- Controls: a layout ---------------------------------------------
        m.tap(stick=(1, 0))                  # Input delay -> Edit
        m.tap(stick=(0, -1))                 # -> the A button
        check("a layout does not exist until a button in it changes",
              m.m.u8(layout1 + P_USED) == 0)
        m.tap(buttons=["A"])
        check("changing a button creates the layout",
              m.m.u8(layout1 + P_USED) == 1
              and m.m.cstr(layout1) == "Layout 1",
              "name %r" % m.m.cstr(layout1))
        check("A now does Special in it",
              m.m.u8(layout1 + P_MAP) == ACT_SPECIAL,
              "action %d" % m.m.u8(layout1 + P_MAP))
        check("the standard layout is untouched",
              m.m.u8(ctl + PROFILES + P_MAP) == ACT_ATTACK)
        m.tap(buttons=["L"])
        m.tap(buttons=["A"])
        check("L goes back, A forward again",
              m.m.u8(layout1 + P_MAP) == ACT_SPECIAL)

        m.tap(stick=(-1, 0))                 # -> the left column
        m.tap(stick=(0, -1))                 # -> Port 1
        m.tap(buttons=["A"])
        check("a port takes the new layout",
              m.m.u8(ctl + PORT_PROFILE) == 1,
              "layout %d" % m.m.u8(ctl + PORT_PROFILE))
        m.tap(buttons=["A"])
        check("and the next press is the standard one again",
              m.m.u8(ctl + PORT_PROFILE) == 0,
              "layout %d" % m.m.u8(ctl + PORT_PROFILE))

        # --- Nicknames ------------------------------------------------------
        add_name(m, 0, "ZANE")
        add_name(m, 3, "MANGO")
        for _ in range(4):
            m.tap(stick=(0, -1))             # Port 1 -> ... -> Nicknames
        m.tap(buttons=["A"])
        m.tap(stick=(0, -1))                 # the second name: slot 3
        m.tap(buttons=["A"])
        check("a nickname takes a layout",
              m.m.u8(ctl + NAME_PROFILE + 3) == 1
              and m.m.u8(ctl + NAME_PROFILE + 0) == 0,
              "slots 0..3: %s" % list(m.m.read(ctl + NAME_PROFILE, 4)))
        m.tap(stick=(0, -1))                 # -> Back
        m.tap(buttons=["A"])                 # to Controls
        m.tap(buttons=["B"])                 # to the main page

        # --- where the panels lead, and the save ----------------------------
        m.tap(buttons=["A"], wait=90)        # Train
        check("Train goes to the event mode's character select",
              m.mode() == GM_EVENT and m.scene() == GS_CSS,
              "mode %d scene %d" % (m.mode(), m.scene()))
        # Leaving the Controls page put the settings in the game's save;
        # the menu reads them from there each time it opens.
        m.m.w8(ctl, 9)
        m.m.w8(layout1 + P_MAP, 0)
        m.back_from_css()
        check("B there comes back to the main menu",
              m.scene() == GS_OURS, "mode %d scene %d" % (m.mode(),
                                                          m.scene()))
        check("the menu takes the settings from the save",
              m.delay() == 0 and m.m.u8(layout1 + P_MAP) == ACT_SPECIAL
              and m.m.u8(ctl + NAME_PROFILE + 3) == 1,
              "delay %d, A does %d, name 3 has layout %d" % (
                  m.delay(), m.m.u8(layout1 + P_MAP),
                  m.m.u8(ctl + NAME_PROFILE + 3)))

        save = m.s.call("GetPersistentNameData", SAVE_SLOT)
        check("the slot the settings are in still has no name",
              m.m.u8(save + NAMEDATA) == 0)
        m.m.w8(save + 4, 99)                 # a delay no menu can set
        m.m.w8(ctl, 4)
        m.tap(buttons=["A"], wait=90)
        m.back_from_css()
        check("a save that makes no sense is left alone", m.delay() == 4,
              "delay %d" % m.delay())

        m.m.w8(save + 4, 0)
        m.m.write(m.s.call("GetPersistentNameData", 3) + NAMEDATA, bytes(8))
        m.tap(buttons=["A"], wait=90)
        m.back_from_css()
        check("a deleted nickname loses its layout",
              m.m.u8(ctl + NAME_PROFILE + 3) == 0 and m.delay() == 0)

        m.tap(stick=(1, 0))                  # Train -> Lab
        m.tap(buttons=["A"], wait=90)
        check("Lab goes to a character select",
              m.mode() == GM_EVENT and m.scene() == GS_CSS,
              "mode %d scene %d" % (m.mode(), m.scene()))

        m2 = Menu()
        m2.tap(stick=(0, -1))                # Controls, with no nicknames
        m2.tap(buttons=["A"])
        for _ in range(5):
            m2.tap(stick=(0, -1))            # ... -> Nicknames
        m2.tap(buttons=["A"])                # only Back is there
        m2.tap(stick=(0, 1))
        m2.tap(buttons=["A"])                # Back
        m2.tap(buttons=["B"])                # to the main page
        m2.tap(stick=(1, 0))                 # Lab
        m2.tap(stick=(0, -1))                # Events
        m2.tap(buttons=["A"], wait=120)
        check("an empty Nicknames page leads back; Events opens the "
              "original menus",
              m2.mode() == GM_MENU and m2.scene() == GS_MENU,
              "mode %d scene %d" % (m2.mode(), m2.scene()))
    except GuestError as e:
        check("the game kept running", False, str(e)[:300])

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
