"""The native client: its own main menu and character select, then the game.

    python tools/melee_client/client.py              # a window on this desktop
    python tools/melee_client/client.py --input keyboard

Opens a 1280 by 720 window. The menus are drawn by the game process over
the whole window; in a match the game keeps its four-by-three picture at
the left and a column beside it says what is going on. Your controller (or
the keyboard: tools/melee_native/play.py has the keys) drives the menus
and then the fighter.

What is here: the main menu, the character select (26 characters, their
traits from data/characters/), and free play as the chosen character
against a standing Marth. Hold START to come back to the menu. What is
not: Lab, Events, Versus, Controls, courses and drills, sound.

Needs tools/aurora32/build.sh (with RmlUi) and tools/native_build.py
--window. --offscreen runs it on a virtual display, which is how it is
tested (tests/client/menu.py).
"""
import argparse
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools" / "melee_native"))

import characters  # noqa: E402
import fonts  # noqa: E402
import screens  # noqa: E402
import window  # noqa: E402
from native import CHARACTERS, NativeError  # noqa: E402

A, B, START = 0x100, 0x200, 0x1000
LEFT, RIGHT, DOWN, UP = 1, 2, 4, 8
OUT = ROOT / "build" / "ui"
COLUMNS = 7

# Which panel a direction leads to from each panel of the main menu.
MAIN_MOVES = {
    "train": {RIGHT: "lab"},
    "lab": {LEFT: "train", DOWN: "events"},
    "events": {LEFT: "train", UP: "lab", RIGHT: "versus"},
    "versus": {LEFT: "events", UP: "lab", DOWN: "controls"},
    "controls": {LEFT: "events", UP: "versus"},
}


class Client:
    def __init__(self, game, port=0, source="auto", opponent="marth",
                 stage="final-destination"):
        self.w = game
        self.port = port
        self.opponent, self.stage = opponent, stage
        self.roster = characters.roster()
        self.screen = None
        self.focus = "train"          # on the main menu
        self.at = next(i for i, c in enumerate(self.roster)
                       if c["id"] == "fox")   # on the character select
        self.last = None              # the character last played
        self.buttons = 0
        self.held = {}                # direction -> frames held
        self.start_held = 0
        self.frames = 0
        OUT.mkdir(parents=True, exist_ok=True)
        for f in fonts.fonts():
            self.w.ui("font " + str(f))
        self.w.live(port, source)
        self.w.pace(True)
        self.show_main()

    # ---- drawing ------------------------------------------------------------

    def load(self, name, rml):
        path = OUT / (name + ".rml")
        style = OUT / "style.rcss"
        text = screens.STYLE.read_text()
        if not style.exists() or style.read_text() != text:
            style.write_text(text)
        path.write_text(rml)
        self.w.ui("load " + str(path))

    def say(self, text):
        self.w.ui("text desc " + screens.esc(text))

    def show_main(self):
        self.screen = "main"
        self.w.capture(True)
        last = (self.last["name"], self.last["color"]) if self.last else None
        self.load("main", screens.main_menu(last))
        self.w.ui("class %s focus 1" % self.focus)
        self.say(self.about(self.focus))

    def show_characters(self):
        self.screen = "chars"
        self.w.capture(True)
        self.load("characters",
                  screens.character_select(self.roster, self.at))

    def about(self, ident):
        item = next(i for i in screens.MAIN if i[0] == ident)
        return item[4] + ("" if item[5] else
                          " Not in the native client yet.")

    # ---- input ----------------------------------------------------------------

    def read(self):
        """(buttons pressed this frame, directions pressed or repeating)."""
        pad = self.w.pads()[self.port]
        now = pad["buttons"]
        dirs = now & 0xF
        if pad["lx"] < -60:
            dirs |= LEFT
        if pad["lx"] > 60:
            dirs |= RIGHT
        if pad["ly"] < -60:
            dirs |= DOWN
        if pad["ly"] > 60:
            dirs |= UP
        pressed = now & ~self.buttons
        self.buttons = now
        moves = 0
        for d in (LEFT, RIGHT, DOWN, UP):
            if dirs & d:
                n = self.held.get(d, 0)
                if n == 0 or (n >= 16 and (n - 16) % 5 == 0):
                    moves |= d
                self.held[d] = n + 1
            else:
                self.held[d] = 0
        self.start_held = self.start_held + 1 if now & START else 0
        return pressed, moves

    # ---- one frame -------------------------------------------------------------

    def frame(self):
        self.w.step()
        self.frames += 1
        pressed, moves = self.read()
        getattr(self, "on_" + self.screen)(pressed, moves)

    def on_main(self, pressed, moves):
        for d in (LEFT, RIGHT, DOWN, UP):
            to = MAIN_MOVES[self.focus].get(d) if moves & d else None
            if to:
                self.w.ui("class %s focus 0" % self.focus)
                self.focus = to
                self.w.ui("class %s focus 1" % to)
                self.say(self.about(to))
                break
        if pressed & A:
            if self.focus == "train":
                self.show_characters()
            else:
                self.say(self.about(self.focus))

    def on_chars(self, pressed, moves):
        at, n = self.at, len(self.roster)
        if moves & LEFT and at % COLUMNS > 0:
            at -= 1
        if moves & RIGHT and at % COLUMNS < COLUMNS - 1 and at + 1 < n:
            at += 1
        if moves & UP and at >= COLUMNS:
            at -= COLUMNS
        if moves & DOWN:
            at = min(at + COLUMNS, n - 1) if at + COLUMNS < n or \
                at // COLUMNS < (n - 1) // COLUMNS else at
        if at != self.at:
            self.w.ui("class c%d focus 0" % self.at)
            self.at = at
            c = self.roster[at]
            self.w.ui("class c%d focus 1" % at)
            self.w.ui("text card " + screens.card(c))
            self.w.ui("attr tab style background-color: %s" % c["color"])
        if pressed & B:
            self.show_main()
        elif pressed & A:
            self.play(self.roster[self.at])

    def play(self, c):
        """Free play as this character."""
        self.say("Loading %s." % c["name"])
        self.w.match(c["id"], self.opponent, self.stage,
                     seed=random.randrange(1, 1 << 30))
        for _ in range(900):
            self.w.step()
            if self.w.fighter(0).fp and self.w.fighter(1).fp and \
                    self.w.fighter(0).ckind == CHARACTERS[c["id"]]:
                break
        else:
            raise NativeError("the match never started")
        self.last = c
        self.screen = "match"
        self.start_held = 0
        self.load("match", screens.match_rail(
            c, self.opponent.replace("-", " ").title(),
            self.stage.replace("-", " ").title()))
        self.w.capture(False)

    def on_match(self, pressed, moves):
        if self.start_held >= 40:
            self.show_characters()

    def run(self, frames=0):
        while not frames or self.frames < frames:
            self.frame()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--input", default="auto",
                    help="auto (the first controller, else the keyboard), "
                         "keyboard, pad0, pad1, ...")
    ap.add_argument("--offscreen", action="store_true",
                    help="on a virtual display (a test of this file)")
    ap.add_argument("--frames", type=int, default=0)
    ap.add_argument("--vsync", action="store_true")
    args = ap.parse_args()
    w = None
    try:
        w = window.Window(real=not args.offscreen, gpu=True,
                          vsync=args.vsync, window=(1280, 720))
        w.step(30)
        began = time.time()
        client = Client(w, source=args.input)
        client.run(args.frames)
        print("%d frames in %.1f s" % (client.frames, time.time() - began))
    except KeyboardInterrupt:
        pass
    except NativeError as e:
        if "the window was closed" not in "".join(w.log[-5:] if w else []):
            print(str(e)[-1500:], file=sys.stderr)
            return 1
    finally:
        if w is not None:
            w.close()
        left = window.leftovers()
        if left:
            print("still running: %s" % left, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
