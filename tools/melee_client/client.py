"""The native client: its own main menu and character select, then the game.

    python tools/melee_client/client.py              # a window on this desktop
    python tools/melee_client/client.py --input keyboard

Opens a 1280 by 720 window. The menus are drawn by the game process over
the whole window; in a match the game keeps its four-by-three picture at
the left and a column beside it says what is going on. A GameCube
controller on an adapter drives the menus and then the fighter (read
directly, with the controller's own numbers; --devices says what the game
sees); without one, another controller or the keyboard does
(tools/melee_native/play.py has the keys).

What is here: the main menu; the character select (26 characters, their
traits from data/characters/); Versus and the Lab, against a trained
slippi-ai model, the game's CPU or nobody, on the six stages (the Lab puts
both back and sets damage from the D-pad); for a character with a course,
the hub with
its four parts and each part's drills from data/courses/, which you can
mark as done; the drills that have a scenario (data/scenarios/) running
against you with a verdict for every attempt; free play against a standing
Marth. Hold START to come back. What is not: Events, Controls, most
drills, the guide, stocks and a result in Versus, sound.

Needs tools/aurora32/build.sh (with RmlUi) and tools/native_build.py
--window. --offscreen runs it on a virtual display, which is how it is
tested (tests/client/menu.py).
"""
import argparse
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools" / "melee_native"))

sys.path.insert(0, str(ROOT / "tools"))

import characters  # noqa: E402
import courses  # noqa: E402
import online  # noqa: E402
import opponents  # noqa: E402
import fonts  # noqa: E402
import screens  # noqa: E402
import window  # noqa: E402
import native  # noqa: E402
from native import STAGES, NativeError  # noqa: E402
from melee_actor import scenario as scn  # noqa: E402
from melee_actor import tech  # noqa: E402
from melee_actor import train  # noqa: E402
from melee_course import engine as course_engine  # noqa: E402
from melee_course import registry as course_registry  # noqa: E402

A, B, X, Y, START = 0x100, 0x200, 0x400, 0x800, 0x1000
L, R = 0x40, 0x20
LEFT, RIGHT, DOWN, UP = 1, 2, 4, 8
OUT = ROOT / "build" / "ui"
COLUMNS = 7
STAGE_ORDER = ("final-destination", "battlefield", "yoshis-story",
               "dream-land", "fountain-of-dreams", "pokemon-stadium")
assert set(STAGE_ORDER) == set(STAGES)
CPU, NOBODY = "the game's own CPU", "nobody"
ONLINE = "a friend, online"
FRAMES_BEFORE_SESSION = 10   # both games, the same frames, nobody's input

# Which panel a direction leads to from each panel of the main menu.
MAIN_MOVES = {
    "train": {RIGHT: "lab"},
    "lab": {LEFT: "train", DOWN: "events"},
    "events": {LEFT: "train", UP: "lab", RIGHT: "versus"},
    "versus": {LEFT: "events", UP: "lab", DOWN: "controls"},
    "controls": {LEFT: "events", UP: "versus"},
}


class Leave(Exception):
    """Out of a drill or a match, to `to`: "back" (where it came from),
    "list", "hub", "main", "chars", "opp", or "drill" with `step` (the
    drill before or after in the course)."""

    def __init__(self, to="back", step=0):
        super().__init__(to)
        self.to, self.step = to, step


class Abandon(Exception):
    """The attempt under way stops, not counted: `what` ("scenario",
    "reset", "guide", "demo", "options", "stage"), `step`."""

    def __init__(self, what, step=0):
        super().__init__(what)
        self.what, self.step = what, step


# How long a button is held for its other meaning (frames, at 60 a second)
HOLD_COLUMN = 180      # START: hide or show the column
HOLD_DRILL = 180       # D-pad left or right: the drill before or after
HOLD_STAGE = 300       # L or R: the stage before or after (drills with stages)
DPAD = LEFT | RIGHT | DOWN | UP


class Client:
    def __init__(self, game, port=0, source="auto", opponent="marth",
                 stage="final-destination", save=None, out=None):
        self.w = game
        self.port = port
        self.source = source
        # where the documents are written: a test gives its own, so that it
        # and a client someone is playing do not write over each other
        self.out = Path(out) if out else OUT
        self.progress = courses.Progress(save or courses.SAVE)
        self.here = courses.scenarios()   # drill id -> scenario file
        self.course = None            # of the character being trained
        self.c = None                 # that character
        self.hub_at = "p0"            # the hub panel in focus
        self.part = 0                 # the part whose drills are listed
        self.row = [0, 0, 0, 0]       # the drill in focus, per part
        self.top = [0, 0, 0, 0]       # the first row shown, per part
        self.back = "chars"           # where free play returns to
        self.person = None            # tests: called before every frame
        self.results = None           # the attempts of the drill last left
        self.banner = 0               # frames the verdict banner stays up
        self.ended = None             # matches the game had ended itself
        self.in_guide = False         # a course drill's guide is shown
        self.last_result = None       # a course drill's last result
        self.mode = "train"           # what the character is being picked for
        self.me = None                # versus and lab: the player's character
        self.opp_at = 0               # the opponent in focus
        self.who = 0                  # which of players() plays the opponent
        self.stage_at = 0
        self.bot = None               # the trained model playing, if one is
        self.bot_said = None
        self.damage = 0               # the lab: the opponent's damage
        self.pad_now = None           # what the player holds this frame
        self.opponent, self.stage = opponent, stage
        self.roster = characters.roster()
        self.opp_at = next(i for i, c in enumerate(self.roster)
                           if c["id"] == "marth")
        self.screen = None
        self.focus = "train"          # on the main menu
        self.at = next(i for i, c in enumerate(self.roster)
                       if c["id"] == "fox")   # on the character select
        self.last = None              # the character last played
        self.buttons = 0
        self.pressed_now = self.released = 0
        self.held = {}                # direction -> frames held
        self.hold = {}                # button bit -> frames held
        self.used = set()             # bits whose hold already did something
        self.column_hidden = False    # START held: the column is put away
        self.pause_open = False       # tests: the pause menu is up
        self.pause_focus = None       # tests: the row in focus there
        self.session = None           # the drill's, while one runs
        self.status_text = None       # the drill's status line shown
        self.game_song = None         # the music a match had (sound below)
        self.rays_html = ""           # the drill's light rays shown
        self.drill_stages = None      # its stages, when it can change them
        self.has_cover = False        # the document has the loading cover
        self.start_held = 0
        self.frames = 0
        self.out.mkdir(parents=True, exist_ok=True)
        for f in fonts.fonts():
            self.w.ui("font " + str(f))
        self.w.live(port, source)
        self.w.pace(True)
        self.show_main()

    # ---- drawing ------------------------------------------------------------

    def load(self, name, rml):
        path = self.out / (name + ".rml")
        style = self.out / "style.rcss"
        text = screens.STYLE.read_text()
        if not style.exists() or style.read_text() != text:
            style.write_text(text)
        path.write_text(rml)
        self.w.ui("load " + str(path))

    def say(self, text):
        self.w.ui("text desc " + screens.esc(text))

    def loading(self, name):
        """Loading `name`: on the cover over the game when a match or a
        drill is on screen (from one drill to the next), else in the
        menu's description line."""
        if self.has_cover:
            self.cover("Loading %s" % name)
        else:
            self.say("Loading %s." % name)

    def put(self, ident, rml):
        """Replace an element's content (through a file: a list of rows is
        longer than a control line)."""
        path = self.out / ("part-%s.rml" % ident)
        path.write_text(rml)
        self.w.ui("file %s %s" % (ident, path))

    # ---- sound: the game's menu sounds and music -------------------------------

    # lbAudioAx_80024030's sounds, as the game's own menus use them
    # (mn/inlines.h: sfxBack, sfxForward, sfxMove)
    SFX_BACK, SFX_FORWARD, SFX_MOVE = 0, 1, 2

    def sfx(self, n):
        try:
            self.w.sfx(n)
        except Exception:             # a build without sound commands
            pass

    def menu_music(self):
        """The main menu's music on the menu screens (the owner: "the main
        menu music"); the match's is kept to put back."""
        try:
            now = self.w.song()
            if now != native.MENU_SONG:
                if now is not None:
                    self.game_song = now
                self.w.bgm(native.SONGS.index(native.MENU_SONG))
        except Exception:
            pass

    def match_music(self):
        """Into a match or a drill: its stage's music again, if the menus
        had replaced it (a new match starts its own)."""
        try:
            if self.w.song() == native.MENU_SONG:
                if self.game_song is not None:
                    self.w.play_song(self.game_song)
                else:
                    self.w.bgm(-1)
        except Exception:
            pass

    def menu_sounds(self, before, pressed):
        """After a menu screen's frame: forward or back when the screen
        changed on A or B, a move when the focus moved."""
        after = self.where()
        if after == before:
            return
        if after[0] != before[0]:
            if pressed & B:
                self.sfx(self.SFX_BACK)
            elif pressed & (A | START):
                self.sfx(self.SFX_FORWARD)
        else:
            self.sfx(self.SFX_MOVE)

    def where(self):
        """Where the menus are: the screen and what is in focus on it."""
        return (self.screen, self.focus, self.at, self.hub_at, self.opp_at,
                tuple(self.row), getattr(self, "part", None))

    def show_main(self):
        self.menu_music()
        self.screen = "main"
        self.w.capture(True)
        last = (self.last["name"], self.last["color"]) if self.last else None
        self.load("main", screens.main_menu(last))
        self.w.ui("class %s focus 1" % self.focus)
        self.say(self.about(self.focus))

    def show_characters(self):
        self.menu_music()
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
        self.pad_now = pad
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
        self.released = self.buttons & ~now
        self.pressed_now = pressed
        self.buttons = now
        for bit in (START, LEFT, RIGHT, L, R):
            self.hold[bit] = self.hold.get(bit, 0) + 1 if now & bit else 0
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
        if self.screen == "online_match":
            ev = self.controls(stages=False)
            if ev is not None and ev[0] == "column":
                self.toggle_column()
            elif ev is not None and ev[0] == "pause":
                ev = self.pause("online")
                if ev is not None and ev[0] == "leave":
                    self.leave_online(ev[1])
                    return
        elif self.screen in ("match", "versus"):
            ev = ("leave", "back") if self.game_quit() else \
                self.controls(stages=False)
            if ev is not None and ev[0] == "column":
                self.toggle_column()
                ev = None
            if ev is not None and ev[0] == "pause":
                ev = self.pause(self.screen)
            if ev is not None and ev[0] == "leave":
                self.leave_match(ev[1])
                return
        before = self.where()
        if self.screen not in ("match", "versus") and pressed & (A | START):
            # choosing: the sound now, before what it opens (a drill runs
            # inside the list's frame)
            self.sfx(self.SFX_FORWARD)
            pressed_sound = A | START
        else:
            pressed_sound = 0
        getattr(self, "on_" + self.screen)(pressed, moves)
        if before[0] not in ("match", "versus"):
            self.menu_sounds(before, pressed & ~pressed_sound)

    def leave_match(self, to):
        """Out of free play or Versus, chosen in the pause menu."""
        if self.screen == "versus":
            if self.bot is not None:
                self.bot.close()
                self.bot = None
            self.w.pad(1 - self.port)
        self.w.mask(0)
        self.has_cover = False
        if to == "main":
            self.show_main()
        elif self.screen == "versus":
            self.show_opponent()
        elif self.back == "hub":
            self.show_hub()
        else:
            self.show_characters()

    def controls(self, drill=False, stages=False):
        """What the buttons ask for in a match or a drill, this frame: None
        or an event. START: tap the pause menu, hold 3 s the column. In a
        drill the D-pad: up the guide, down a restart, left and right a tap
        the scenario and held 3 s the drill before or after. With stages, L
        or R held 5 s: the stage before or after. A hold that did something
        is not also a tap when let go."""
        ev = None
        holds = [(START, HOLD_COLUMN, ("column",))]
        taps = [(START, ("pause",))]
        if drill:
            holds += [(LEFT, HOLD_DRILL, ("drill", -1)),
                      (RIGHT, HOLD_DRILL, ("drill", 1))]
            taps += [(LEFT, ("scenario", -1)), (RIGHT, ("scenario", 1))]
        if stages:
            holds += [(L, HOLD_STAGE, ("stage", -1)),
                      (R, HOLD_STAGE, ("stage", 1))]
        for bit, frames, event in holds:
            if self.hold.get(bit, 0) == frames and bit not in self.used:
                self.used.add(bit)
                ev = event
        for bit, event in taps:
            if self.released & bit and bit not in self.used:
                ev = ev or event
        for bit in list(self.used):
            if self.released & bit:
                self.used.discard(bit)
        if drill:
            if self.pressed_now & UP:
                ev = ("guide",)
            elif self.pressed_now & DOWN:
                ev = ("reset",)
        return ev

    def consume(self):
        """The buttons now held did something here (closed a menu, chose
        a row): their release is not a tap, and the game does not see them
        until they are let go."""
        for bit in (START, LEFT, RIGHT, UP, DOWN, L, R):
            if self.buttons & bit:
                self.used.add(bit)
        if self.buttons & (A | B | X | Y | START | L | R | DPAD):
            self.w.capture(True)
            for _ in range(60):
                self.w.step()
                pad = self.w.pads()[self.port]
                if not pad["buttons"] & (A | B | X | Y | START | L | R | DPAD):
                    break
            self.read()
            self.w.capture(False)

    def toggle_column(self, apply_only=False):
        """Put the column away (the game's picture in the middle) or back."""
        if not apply_only:
            self.column_hidden = not self.column_hidden
        on = 1 if self.column_hidden else 0
        self.w.ui("class rail hidden %d" % on)
        for ident in ("bannerwrap", "cover", "pause", "rays"):
            self.w.ui("class %s mid %d" % (ident, on))
        self.w.ui("center %d" % on)

    def cover(self, text=None):
        """The loading cover over the game: shown with `text`, None hides
        it (nothing if the screen has none)."""
        if not self.has_cover:
            return
        if text is not None:
            self.w.ui("text covermsg " + screens.esc(text))
        self.w.ui("class cover on %d" % (1 if text is not None else 0))

    def in_match(self, name, rml, mask):
        """Load a match's or a drill's screen: the buttons the game does
        not see (`mask`: START, and the D-pad in drills), the column as
        the player left it."""
        self.load(name, rml)
        self.has_cover = True
        self.w.mask(mask)
        self.match_music()
        if self.column_hidden:
            self.toggle_column(apply_only=True)

    # ---- the pause menu ----------------------------------------------------------

    def pause_rows(self, kind):
        """(id, label, value) for the pause menu of `kind` ("drill",
        "match", "versus"); id "-" is a gap."""
        rows = [("resume", "Resume", None), ("-", "", None)]
        s = self.session
        if kind == "drill" and isinstance(s, course_engine.Session):
            for i, o in enumerate(s.d.options):
                rows.append(("opt%d" % i, o.name, o.label(s.opts[i])))
            if s.d.deck:
                names = ["Random"] + s.scenario_names()
                rows.append(("scen", "Scenario",
                             names[s.common[course_engine.OPT_SCENARIO]]))
            if s.cpu_port is not None:
                rows.append(("side", "CPU side", ("Random", "Left", "Right")[
                    s.common[course_engine.OPT_SIDE]]))
            if s.d.stages:
                rows.append(("stage", "Stage", s.d.stage.replace(
                    "-", " ").title()))
            rows.append(("-", "", None))
            rows.append(("guide", "Guide", None))
            if s.d.reference or type(s.d).build_reference is not \
                    course_engine.Drill.build_reference:
                rows.append(("demo", "Watch a demonstration", None))
        elif kind == "drill" and isinstance(s, tech.Session):
            rows.append(("tol", "Leniency", "%d frames late" % s.tolerance))
            rows.append(("-", "", None))
        if kind == "drill":
            rows.append(("reset", "Restart", None))
        rows.append(("column", "Show the column" if self.column_hidden
                     else "Hide the column", None))
        rows.append(("-", "", None))
        if kind == "drill":
            rows += [("prev", "Previous drill", None),
                     ("next", "Next drill", None),
                     ("list", "Back to the drill list", None),
                     ("hub", "Back to the course", None)]
        elif kind == "versus":
            rows.append(("opp", "Back to the opponent", None))
        elif kind == "online":
            rows.append(("back", "Leave the match", None))
        else:
            rows.append(("back", "Back", None))
        rows.append(("main", "Main menu", None))
        return rows

    def pause_change(self, ident, step):
        """Left or right on a setting. Returns whether it is one."""
        s = self.session
        if ident.startswith("opt"):
            i = int(ident[3:])
            s.opts[i] = (s.opts[i] + step) % s.d.options[i].size()
        elif ident == "scen":
            n = len(s.d.deck) + 1
            s.common[course_engine.OPT_SCENARIO] = \
                (s.common[course_engine.OPT_SCENARIO] + step) % n
        elif ident == "side":
            s.common[course_engine.OPT_SIDE] = \
                (s.common[course_engine.OPT_SIDE] + step) % 3
        elif ident == "stage":
            i = s.d.stages.index(s.d.stage)
            s.set_stage(s.d.stages[(i + step) % len(s.d.stages)])
            if self.has_cover:
                self.w.ui("text stage Stage: " + screens.esc(
                    s.d.stage.replace("-", " ").title()))
        elif ident == "tol":
            s.tolerance = max(0, min(6, s.tolerance + step))
        else:
            return False
        return True

    def pause(self, kind):
        """Our pause menu over the frozen match, until it is closed (None,
        or ("options",) when a setting changed) or something is chosen
        (an event as controls() gives)."""
        rows = self.pause_rows(kind)
        at = 0
        changed = False

        def draw():
            self.pause_focus = rows[at][0]
            self.put("prows", screens.pause_rows(rows, at))

        frozen = kind != "online"   # online the game goes on: both sides
        if frozen:
            self.w.freeze(True)
        self.pause_open = True
        self.w.ui("text ptitle Paused")
        draw()
        self.w.ui("class pause on 1")
        try:
            while True:
                if self.person is not None:
                    self.person(self.w, -3)        # tests: the player
                self.w.step()
                pressed, moves = self.read()
                if self.game_quit():
                    raise Leave()
                done = ("options",) if changed else None
                if pressed & (B | START):
                    self.sfx(self.SFX_BACK)
                    return done
                if moves & (UP | DOWN):
                    step = 1 if moves & DOWN else -1
                    at = (at + step) % len(rows)
                    while rows[at][0] == "-":
                        at = (at + step) % len(rows)
                    self.sfx(self.SFX_MOVE)
                    draw()
                if moves & (LEFT | RIGHT):
                    if self.pause_change(rows[at][0],
                                         1 if moves & RIGHT else -1):
                        self.sfx(self.SFX_MOVE)
                        changed = True
                        rows = self.pause_rows(kind)
                        draw()
                if pressed & A:
                    self.sfx(self.SFX_FORWARD)
                    ident = rows[at][0]
                    if ident == "resume":
                        return done
                    if ident == "column":
                        self.toggle_column()
                        rows = self.pause_rows(kind)
                        draw()
                        continue
                    if ident in ("guide", "demo", "reset"):
                        return (ident,)
                    if ident in ("prev", "next"):
                        return ("drill", -1 if ident == "prev" else 1)
                    if ident in ("list", "hub", "main", "opp", "back"):
                        return ("leave", ident)
        finally:
            self.w.ui("class pause on 0")
            self.pause_open = False
            self.pause_focus = None
            self.consume()                  # still frozen while let go
            if frozen:
                self.w.freeze(False)

    def playing(self):
        """A match has just been started here: from now on the game ending
        one itself means the player quit it (game_quit)."""
        self.ended = self.w.state().get("ended", 0)

    def game_quit(self):
        """Did the game end the match itself? L+R+A+Start in its pause
        does: the native game then starts the same match again (it never
        goes back to its own menus), and the client leaves it, as it does
        when START is held."""
        if self.ended is None:
            return False
        now = self.w.state().get("ended", 0)
        if now != self.ended:
            self.ended = now
            return True
        return False

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
            if self.focus == "versus":
                self.mode = "versus"
                self.show_versus_menu()
            elif self.focus in ("train", "lab"):
                self.mode = self.focus
                self.show_characters()
            else:
                self.say(self.about(self.focus))

    # ---- versus: local or online -------------------------------------------

    def show_versus_menu(self):
        """The owner: "make sure we have like submenus within Versus. It
        should go Local and Online"."""
        self.menu_music()
        self.screen = "vmenu"
        self.w.capture(True)
        self.vfocus = getattr(self, "vfocus", "vlocal")
        self.load("versus", screens.versus_menu(self.vfocus))
        self.w.ui("class %s focus 1" % self.vfocus)

    def on_vmenu(self, pressed, moves):
        to = None
        if moves & RIGHT and self.vfocus == "vlocal":
            to = "vonline"
        if moves & LEFT and self.vfocus == "vonline":
            to = "vlocal"
        if to:
            self.w.ui("class %s focus 0" % self.vfocus)
            self.vfocus = to
            self.w.ui("class %s focus 1" % to)
            self.say(next(v[4] for v in screens.VERSUS if v[0] == to))
        if pressed & B:
            self.show_main()
        elif pressed & A:
            self.versus_kind = "online" if self.vfocus == "vonline" \
                else "local"
            self.show_characters()

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
            if self.mode == "versus":
                self.show_versus_menu()
            else:
                self.show_main()
        elif pressed & A and self.mode == "versus" and \
                getattr(self, "versus_kind", "local") == "online":
            # a friend, online: they pick their own character
            self.me = self.roster[self.at]
            self.show_online()
        elif pressed & A and self.mode != "train":
            self.me = self.roster[self.at]
            self.who = None
            self.show_opponent()
        elif pressed & A:
            c = self.roster[self.at]
            if courses.load(c["id"]):
                self.show_hub()
            else:
                self.back = "chars"
                self.play(c)

    # ---- versus and the lab: who is on the other side ------------------------------

    def players(self):
        """Who can play the opponent in focus: [(name, what it is)]. In
        Versus a trained model comes first; in the Lab nobody does."""
        opp = self.roster[self.opp_at]
        trained = opponents.models(opp["id"], self.me["id"])
        rest = [(CPU, "the CPU the game came with"),
                (NOBODY, "it stands still")]
        if self.mode == "lab":
            rest.reverse()
            return rest + trained
        return trained + rest

    def opponent_card(self):
        players = self.players()
        name, what = players[self.who]
        return screens.opponent_card(
            self.roster[self.opp_at], name, what,
            STAGE_ORDER[self.stage_at].replace("-", " ").title(),
            "%d of %d" % (self.who + 1, len(players)),
            "Start" if self.mode == "lab" else "Fight")

    def show_opponent(self):
        self.menu_music()
        self.screen = "opp"
        self.w.capture(True)
        if self.who is None or self.who >= len(self.players()):
            self.who = 0
        self.load("opponent", screens.character_select(
            self.roster, self.opp_at, title="Choose your opponent",
            about="%s against whom, played by whom, and where." %
                  self.me["name"],
            inside=self.opponent_card(),
            hints=[("A", "Start" if self.mode == "lab" else "Fight"),
                   ("X", "Played by"), ("B", "Back")]))

    def on_opp(self, pressed, moves):
        at, n = self.opp_at, len(self.roster)
        if moves & LEFT and at % COLUMNS > 0:
            at -= 1
        if moves & RIGHT and at % COLUMNS < COLUMNS - 1 and at + 1 < n:
            at += 1
        if moves & UP and at >= COLUMNS:
            at -= COLUMNS
        if moves & DOWN and at + COLUMNS < n:
            at += COLUMNS
        changed = False
        if at != self.opp_at:
            self.w.ui("class c%d focus 0" % self.opp_at)
            self.opp_at, self.who = at, 0
            self.w.ui("class c%d focus 1" % at)
            self.w.ui("attr tab style background-color: %s" %
                      self.roster[at]["color"])
            changed = True
        if pressed & X:
            self.who = (self.who + 1) % len(self.players())
            changed = True
        if pressed & L:
            self.stage_at = (self.stage_at - 1) % len(STAGE_ORDER)
            changed = True
        if pressed & R:
            self.stage_at = (self.stage_at + 1) % len(STAGE_ORDER)
            changed = True
        if changed:
            self.put("card", self.opponent_card())
        if pressed & B:
            self.show_characters()
        elif pressed & A:
            self.fight()

    def fight(self):
        """A match against the opponent chosen, played as chosen."""
        opp = self.roster[self.opp_at]
        name, what = self.players()[self.who]
        stage = STAGE_ORDER[self.stage_at]
        self.say("Loading.")
        self.w.step()
        if self.bot is not None:
            self.bot.close()
            self.bot = None
        if name not in (CPU, NOBODY):
            self.bot = opponents.Bot(name, port=1 - self.port,
                                     opponent=self.port, stage=stage)
        self.bot_said = None
        self.w.pad(1 - self.port)
        self.w.pace(False)
        try:
            self.w.start(self.me["id"], opp["id"], stage,
                         seed=random.randrange(1, 1 << 30),
                         p2_human=name != CPU, settle=False)
        finally:
            self.w.pace(True)
        self.last = self.me
        self.screen = "versus"
        self.start_held = 0
        self.playing()
        self.damage = 0
        self.in_match("versus", screens.versus_rail(
            self.me, opp, name, what, stage.replace("-", " ").title(),
            self.mode == "lab"), START | (DPAD if self.mode == "lab" else 0))
        self.w.capture(False)

    # ---- a friend, online (online.py; the session: src/host/net.c) --------

    def online_rows(self):
        rows = [("copy", "Copy my code", "to send to your friend"),
                ("paste", "Paste a friend's code", "a code or ip:port")]
        for i, f in enumerate(online.friends(self.progress.data)):
            rows.append(("friend%d" % i, f["name"], "a friend"))
        return rows

    def show_online(self, status=""):
        self.menu_music()
        self.screen = "online"
        self.w.capture(True)
        self.online_at = getattr(self, "online_at", 0)
        if getattr(self, "lobby", None) is None:
            self.load("online", screens.online_page(
                "...", [], 0, "Finding your address (a STUN server)..."))
            self.w.step()
            try:
                self.lobby = online.Lobby(
                    port=self.online_port(),
                    use_stun=os.environ.get("MELEE_ONLINE_NO_STUN") is None)
            except Exception as e:
                self.lobby = None
                status = "No address: %s. Is this machine online?" % (
                    str(e)[:80],)
        rows = self.online_rows()
        self.online_at = min(self.online_at, len(rows) - 1)
        self.load("online", screens.online_page(
            self.lobby.code if self.lobby else "-", rows, self.online_at,
            status))

    def online_port(self):
        """The local UDP port: the same each time where it is free, so a
        router that keeps ports gives the same code every time."""
        return int(self.progress.data.get("online_port", 47700))

    def write_clipboard(self, text):
        """The code onto the system clipboard: SDL's (the window's), and
        xclip's where there is one (an X11 session, or Wayland's X
        clients); off screen SDL's clipboard does not keep it."""
        try:
            self.w.clipboard(text)
        except NativeError:
            pass
        if shutil.which("xclip") and not self.w.display:
            try:
                p = subprocess.Popen(
                    ["timeout", "120", "xclip", "-selection", "clipboard",
                     "-loops", "1"], stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    start_new_session=True)
                p.stdin.write(text.encode())
                p.stdin.close()
            except OSError:
                pass

    def read_clipboard(self):
        """The clipboard's text: SDL's, else xclip's."""
        try:
            text = self.w.clipboard().strip()
        except NativeError:
            text = ""
        if not text and shutil.which("xclip"):
            env = dict(os.environ)
            if self.w.display:
                env["DISPLAY"] = self.w.display
            try:
                text = subprocess.run(
                    ["xclip", "-selection", "clipboard", "-o"], env=env,
                    capture_output=True, text=True, timeout=2).stdout.strip()
            except (OSError, subprocess.TimeoutExpired):
                text = ""
        return text

    def online_say(self, text):
        self.online_status = text
        self.w.ui("text ostatus " + screens.esc(text))

    def close_lobby(self):
        if getattr(self, "lobby", None) is not None:
            self.lobby.close()
            self.lobby = None

    def on_online(self, pressed, moves):
        rows = self.online_rows()
        at = self.online_at
        if moves & UP:
            at = (at - 1) % len(rows)
        if moves & DOWN:
            at = (at + 1) % len(rows)
        if at != self.online_at:
            self.online_at = at
            self.put("orows", screens.online_rows(rows, at))
        if pressed & B:
            self.close_lobby()
            self.show_characters()
            return
        if not pressed & A or self.lobby is None:
            return
        ident = rows[self.online_at][0]
        if ident == "copy":
            self.write_clipboard(self.lobby.code)
            self.online_say("Your code is copied: paste it to your friend.")
        elif ident == "paste":
            code = self.read_clipboard()
            try:
                online.read_code(code)
            except Exception:
                self.online_say("The clipboard has no code in it.")
                return
            self.online_connect(code)
        else:
            f = online.friends(self.progress.data)[int(ident[6:])]
            self.online_connect(f["code"], f["name"])

    def online_connect(self, code, name=None):
        """Meet the friend, then the same match on both sides, then the
        session."""
        self.online_say("Looking for %s..." % (name or "your friend"))
        cancelled = []

        def tick():
            self.w.step()
            pad = self.w.pads()[self.port]["buttons"]
            if pad & B:
                cancelled.append(1)
                raise online.OnlineError("cancelled")
        try:
            met = self.lobby.meet(
                code, dict(nick=self.nickname(), char=self.me["id"],
                           color=0),
                stage=STAGE_ORDER[self.stage_at], delay=2, tick=tick)
        except online.OnlineError as e:
            self.online_say("Cancelled." if cancelled else
                            "Not found: %s. Ask for a new code, or check "
                            "the address." % str(e)[:60])
            return
        them = met["nicks"][1 - met["local"]] or name or "Friend"
        online.add_friend(self.progress.data, them, code)
        self.progress.save()
        self.close_lobby()
        self.online_match(met, them)

    def nickname(self):
        return self.progress.data.get("nickname") or "Player"

    def online_match(self, met, them):
        local, other = met["local"], 1 - met["local"]
        self.online_say("Found %s: starting the match..." % them)
        self.w.step()
        self.online_left_port = self.port
        self.w.live(self.port, "off")
        self.w.pad(0)
        self.w.pad(1)
        self.w.pace(False)
        try:
            self.w.start(met["chars"][0], met["chars"][1], met["stage"],
                         seed=met["seed"], p2_human=True, settle=False)
            self.w.step(FRAMES_BEFORE_SESSION)
        finally:
            self.w.pace(True)
        # the person plays the session's local port
        self.port = local
        self.w.live(local, self.source)
        self.w.net("start", local, met["bind"], met["peer"][0],
                   met["peer"][1], met["delay"])
        self.online = dict(them=them, met=met, frames=0, said=None)
        opp = next(c for c in self.roster
                   if c["id"] == met["chars"][other])
        self.screen = "online_match"
        self.playing()
        self.in_match("versus", screens.versus_rail(
            self.me, opp, them, "online: a friend",
            met["stage"].replace("-", " ").title(), False), START | DPAD)
        self.w.capture(False)

    def on_online_match(self, pressed, moves):
        o = self.online
        o["frames"] += 1
        if o["frames"] % 30 == 0:
            st = self.w.net("stats")
            if st["peer_left"]:
                text = "%s left the match." % o["them"]
            elif st["desync"]:
                text = "Out of step with %s at frame %d." % (
                    o["them"], st["desync_frame"])
            elif st["silent"] > 180:
                text = "Nothing heard from %s for %d s." % (
                    o["them"], st["silent"] // 60)
            else:
                text = "Rolled back %d times (deepest %d frames)." % (
                    st["rollbacks"], st["max_rollback"])
            if text != o["said"]:
                o["said"] = text
                self.bot_state(text)
            if st["peer_left"] and o.get("left_at") is None:
                o["left_at"] = o["frames"]
        if o.get("left_at") is not None and o["frames"] - o["left_at"] > 120:
            self.leave_online("online", "%s left the match." % o["them"])

    def leave_online(self, to, why="You left the match."):
        try:
            self.w.net("stop")
        except NativeError:
            pass
        self.w.live(self.port, "off")
        self.port = self.online_left_port
        self.w.live(self.port, self.source)
        self.w.mask(0)
        self.has_cover = False
        self.online = None
        if to == "main":
            self.show_main()
        else:
            self.show_online(why)

    def bot_state(self, text):
        if text != self.bot_said:
            self.bot_said = text
            self.w.ui("text botstate " + screens.esc(text))

    def on_versus(self, pressed, moves):
        other = 1 - self.port
        if self.bot is not None:
            ready = self.bot.ready()
            if ready is None:
                self.bot_state("The model is loading: it stands still until "
                               "it has.")
            elif not ready:
                self.bot_state("The model did not load (%s). Nobody is "
                               "playing." % self.bot.error[:80])
            else:
                self.bot_state("Reacts %d frames after what it sees." %
                               self.bot.delay)
                # the answer to last frame's question; then this frame's
                pad = self.bot.answer(0.002)
                if pad is not None:
                    self.w.pad(other, **pad)
                pads = [None, None]
                pads[self.port] = self.pad_now
                self.bot.ask(self.w.state()["p"], pads)
        if self.mode == "lab":
            f = self.w.fighter(other)
            if pressed & DOWN:
                self.w.place(self.port, -20, 0, 1)
                self.w.place(other, 20, 0, -1, percent=self.damage)
            elif pressed & (LEFT | RIGHT) and f.fp:
                self.damage = max(0, min(300, self.damage +
                                         (10 if pressed & RIGHT else -10)))
                self.w.place(other, f.pos[0], f.pos[1], f.facing,
                             percent=self.damage)

    # ---- the course hub -----------------------------------------------------------

    def left_off(self):
        """The drill last played, if it is one of this course's."""
        last = self.progress.data.get("last")
        if last and last.get("character") == self.c["id"]:
            return self.course["by_id"].get(last.get("drill"))
        return None

    def hub_about(self):
        if self.hub_at == "free":
            return "Free play against a standing opponent. Nothing is judged."
        part = courses.PARTS[int(self.hub_at[1])]
        return "%s: %s Every part is open from the start." % (
            part, courses.ABOUT[part][2])

    def show_hub(self):
        self.menu_music()
        self.screen = "hub"
        self.w.capture(True)
        c = self.roster[self.at]
        if self.c is not c:
            self.c, self.course = c, courses.load(c["id"])
            self.hub_at, self.part = "p0", 0
            self.row, self.top = [0, 0, 0, 0], [0, 0, 0, 0]
        self.last = c
        self.load("hub", screens.hub(c, self.course, self.here,
                                     self.progress, self.left_off()))
        self.w.ui("class %s focus 1" % self.hub_at)
        self.hub_tab()

    def hub_tab(self):
        self.say(self.hub_about())
        color = screens.PART_COLOR[courses.PARTS[int(self.hub_at[1])]] \
            if self.hub_at != "free" else "#5B3FD6"
        self.w.ui("attr tab style background-color: %s" % color)

    def on_hub(self, pressed, moves):
        at = self.hub_at
        if at == "free":
            if moves & UP:
                at = "p%d" % self.part
        else:
            i = int(at[1])
            if moves & LEFT and i > 0:
                at = "p%d" % (i - 1)
            if moves & RIGHT and i < 3:
                at = "p%d" % (i + 1)
            if moves & DOWN:
                self.part, at = i, "free"
        if at != self.hub_at:
            self.w.ui("class %s focus 0" % self.hub_at)
            self.hub_at = at
            self.w.ui("class %s focus 1" % at)
            self.hub_tab()
        left = self.left_off()
        if pressed & B:
            self.show_characters()
        elif pressed & A and self.hub_at == "free":
            self.back = "hub"
            self.play(self.c)
        elif pressed & A:
            self.part = int(self.hub_at[1])
            self.show_list()
        elif pressed & X and left:
            self.part = courses.PARTS.index(left["part"])
            self.focus_row(self.course["parts"][left["part"]].index(left))
            self.show_list()

    # ---- a part's drills ------------------------------------------------------------

    def drills(self):
        return self.course["parts"][courses.PARTS[self.part]]

    def focus_row(self, at):
        """Put the focus on a row, scrolling so it is in view."""
        top = self.top[self.part]
        if at < top:
            top = at
        if at >= top + screens.ROWS:
            top = at - screens.ROWS + 1
        self.row[self.part], self.top[self.part] = at, top

    def show_list(self):
        self.menu_music()
        self.screen = "list"
        self.w.capture(True)
        part = courses.PARTS[self.part]
        self.load("drills", screens.drill_list(
            self.c, self.course, part, self.here, self.progress,
            self.row[self.part], self.top[self.part]))

    def refresh_list(self):
        part = courses.PARTS[self.part]
        d = self.drills()[self.row[self.part]]
        self.put("rows", screens.list_rows(
            self.course, part, self.here, self.progress,
            self.row[self.part], self.top[self.part]))
        self.put("detail", screens.list_detail(self.course, d, self.here,
                                               self.progress))
        self.say(d["goal"])

    def on_list(self, pressed, moves):
        at, n = self.row[self.part], len(self.drills())
        if moves & UP and at > 0:
            at -= 1
        if moves & DOWN and at < n - 1:
            at += 1
        turn = 0
        if (pressed & L or moves & LEFT) and self.part > 0:
            turn = -1
        if (pressed & R or moves & RIGHT) and self.part < 3:
            turn = 1
        d = self.drills()[self.row[self.part]]
        if turn:
            self.part += turn
            self.show_list()
        elif at != self.row[self.part]:
            self.focus_row(at)
            self.refresh_list()
        elif pressed & Y:
            self.progress.toggle(d["id"])
            self.refresh_list()
        elif pressed & B:
            self.show_hub()
        elif pressed & A:
            if d["id"] in self.here:
                self.drill(d)
            else:
                self.say("%s is not built for the native client yet." %
                         d["name"])

    # ---- a drill ----------------------------------------------------------------------

    def drill_frame(self, game, frame):
        """Before every frame of a drill: the controls (controls()), the
        banner, and (in tests) the stand-in for the player."""
        self.read()
        if self.game_quit():
            raise Leave()
        ev = self.controls(drill=True, stages=bool(self.drill_stages))
        if ev is not None:
            self.drill_event(ev)
        if self.banner > 0:
            self.banner -= 1
            if self.banner == 0:
                self.w.ui("class banner on 0")
        self.show_status()
        self.show_rays()
        if self.person is not None:
            self.person(game, frame)

    def show_rays(self):
        """A drill's light rays (targets), where the camera shows them."""
        s = self.session
        if not isinstance(s, course_engine.Session):
            return
        points = []
        for x, y in s.d.rays(s.c):
            try:
                sx, sy = self.w.project(x, y)
            except Exception:       # no match yet
                continue
            # the game's 640x480 is 960x720 dp here
            points.append((int(sx * 1.5), int(sy * 1.5)))
        html = screens.rays(points)
        if html != self.rays_html:
            self.rays_html = html
            self.put("rays", html)

    def show_status(self):
        """The line on what the drill asks now (its scenario, the level of
        an Illusion), when it changes."""
        s = self.session
        if not isinstance(s, course_engine.Session):
            return
        text = s.d.status(s.c) or ""
        if text != self.status_text:
            self.status_text = text
            self.w.ui("text status " + screens.esc(text))

    def drill_event(self, ev):
        kind = ev[0]
        if kind == "column":
            self.toggle_column()
            return
        if kind == "pause":
            ev = self.pause("drill")
            if ev is None:
                return
            kind = ev[0]
        if kind == "drill":
            raise Leave("drill", ev[1])
        if kind == "leave":
            raise Leave(ev[1])
        course = isinstance(self.session, course_engine.Session)
        if kind == "scenario" and not (course and self.session.d.deck):
            return
        if kind in ("guide", "demo") and not course:
            return
        if kind == "stage" and not self.drill_stages:
            return
        raise Abandon(kind, ev[1] if len(ev) > 1 else 0)

    def show_result(self, result, results):
        ok = bool(result["success"])
        words = result.get("words")       # a tech drill has its own
        if not words:
            words = train.verdict(result)
            if ok:
                words = "; ".join(screens.CHECK_WORDS.get(c["expect"],
                                                          c["expect"])
                                  for c in result["checks"]) or "done"
            else:
                words = words.split(": ", 1)[-1]
        best = run = 0
        for r in results:
            run = run + 1 if r else 0
            best = max(best, run)
        shown = results[-10:]
        for ident, text in (
                ("n", len(results)),
                ("verdict", "Success" if ok else "Failure"),
                ("count", "%d OF %d" % (sum(shown), len(shown))),
                ("tries", len(results)),
                ("rate", "%d%%" % round(100.0 * sum(results) /
                                        len(results))),
                ("best", best), ("bword", "Success" if ok else "Failure"),
                # the banner has room for the first clause only
                ("bmsg", screens.esc(words.split(":")[0])),
                ("why", screens.esc(result.get("full_words", words)
                                    .replace("\n", "; "))
                 if result.get("timeline")
                 else screens.esc("%s. Frame %d, perfect %d." % (
                     result["scenario"], result["measured"],
                     result["target"]))
                 if result.get("measured") is not None
                 else screens.esc(result.get("scenario", ""))
                 if "report" in result else "")):
            self.w.ui("text %s %s" % (ident, text))
        self.put("checks", screens.check_rows(result["checks"]))
        self.put("last", screens.last_squares(results))
        self.put("tl", screens.timeline(result.get("timeline")))
        self.verdict_colour(ok)
        self.w.ui("class banner on 1")
        self.banner = 100

    def verdict_colour(self, ok):
        """Green for a success, red for a failure (None: neither), on the
        banner and the column."""
        for ident in ("chip", "banner", "verdict"):
            self.w.ui("class %s good %d" % (ident, 1 if ok is True else 0))
            self.w.ui("class %s bad %d" % (ident, 1 if ok is False else 0))

    def banner_say(self, word, text):
        self.verdict_colour(None)
        self.w.ui("text bword " + screens.esc(word))
        self.w.ui("text bmsg " + screens.esc(text.split("\n")[0]))
        self.w.ui("class banner on 1")
        self.banner = 100

    def results_now(self):
        """The verdicts of the drill being played (tests)."""
        return getattr(self, "live_results", [])

    def drill(self, d):
        """Play drills until the player leaves for a menu: from one drill
        the D-pad held, or the pause menu, can go to the one before or
        after it in the course (left at its end comes round)."""
        while d is not None:
            left = self.play_drill(d)
            d = None
            self.session = None
            self.drill_stages = None
            if left.to != "drill":
                self.w.mask(0)
                self.has_cover = False
            if left.to == "drill":
                drills = self.drills()
                at = (self.row[self.part] + left.step) % len(drills)
                self.focus_row(at)
                d = drills[at]
            elif left.to == "hub":
                self.show_hub()
            elif left.to == "main":
                self.show_main()
            else:
                self.show_list()

    def play_drill(self, d):
        """One drill until the player leaves it: returns the Leave."""
        results = []
        self.live_results = results
        try:
            if self.here[d["id"]] == courses.COURSE:
                self.course_drill(d, results)
            else:
                self.judged_drill(d, results)
        except Leave as left:
            return left
        finally:
            # kept even when the game goes away mid-drill (the window
            # closed): the tries so far count
            self.progress.record(d["id"], self.c["id"], results)
            self.results = results
        return Leave()

    def wait_released(self):
        # The A that started the drill is still down, and A in shield is
        # a grab: wait for the buttons to be let go before the first try.
        for _ in range(90):
            self.w.step()
            if not self.w.pads()[self.port]["buttons"] & (A | B | X | Y):
                break

    def course_drill(self, d, results):
        """A drill on the course engine (tools/melee_course): the overlay's
        drill, ported."""
        self.loading(d["name"])
        self.w.step()

        def on_load(fn):
            # the game sets a match up with its own presses, at full speed:
            # behind the cover
            self.cover("Loading")
            self.w.live(self.port, "off")
            self.w.pace(False)
            try:
                fn()
            finally:
                self.w.live(self.port, self.source)
                self.w.pace(True)
                self.cover(None)

        drill = course_registry.get(d["id"])
        session = course_engine.Session(
            drill, self.w, person=self.port, character=self.c["id"],
            live=True, on_load=on_load, seed=random.randrange(1, 1 << 30),
            dpad=False)
        self.session = session
        self.drill_stages = drill.stages
        self.wait_released()
        self.screen = "drill"
        self.playing()
        about = " ".join(line for line in drill.help
                         if line and not line.startswith("D-Pad")) or \
            d["goal"]
        self.in_match("drill", screens.drill_rail(
            self.c, d, self.course, about, stages=drill.stages and
            [drill.stage]), START | DPAD)
        self.w.capture(False)
        demo = False
        self.status_text = None
        self.rays_html = None
        while True:
            if demo:
                # the game plays the reference; the player is still read
                # (a D-pad press or START stops it)
                self.w.scripted(self.port, True)
                session.live = False
                self.banner_say("Watch", "the game plays it")
            try:
                result = session.run(each_frame=self.drill_frame, demo=demo)
            except Abandon as a:
                session.flowing = False
                demo = False
                if a.what == "scenario":
                    session.change_scenario(a.step)
                    self.banner_say("Next", session.scenario_names()[
                        session.scenario])
                elif a.what == "guide":
                    demo = self.course_guide(drill, session)
                elif a.what == "demo":
                    demo = True
                elif a.what == "stage":
                    i = drill.stages.index(drill.stage)
                    session.set_stage(drill.stages[(i + a.step) %
                                                   len(drill.stages)])
                    self.w.ui("text stage Stage: " + screens.esc(
                        drill.stage.replace("-", " ").title()))
                    self.banner_say("Stage", drill.stage.replace(
                        "-", " ").title())
                continue
            finally:
                self.w.scripted(self.port, False)
                session.live = True
            demo = False
            self.last_result = result
            if result.get("demo"):
                self.banner_say("Demo", result["words"])
            elif result.get("skip"):
                self.banner_say("Not counted", result["words"])
            else:
                results.append(bool(result["success"]))
                self.show_result(result, results)
            # a moment to read the verdict (the C engine's reset delay),
            # except where the drill carries on from where you stand
            for _ in range(0 if drill.flow else 45):
                self.drill_frame(self.w, -1)
                self.w.step()

    def course_guide(self, drill, session):
        """The guide, in the column, until D-pad up or B (go on) or right
        (watch a demonstration first: returns True)."""
        lines = drill.guide(session.c)
        self.verdict_colour(None)
        self.w.ui("text verdict Guide")
        # The overlay's guide breaks its lines for a narrow panel, in the
        # middle of sentences; this column wraps by itself: a line that
        # does not end a sentence goes on the one before.
        parts = []
        for line in lines:
            if parts and not parts[-1].rstrip().endswith(
                    (".", ":", "!", "?")):
                parts[-1] += " " + line.strip()
            else:
                parts.append(line.strip())
        self.w.ui("text why " + "<br/>".join(screens.esc(p) for p in parts))
        self.banner_say("Guide", "D-pad right: watch it. Up: go on")
        self.banner = 0
        has_demo = bool(drill.reference) or \
            type(drill).build_reference is not \
            course_engine.Drill.build_reference
        if self.column_hidden:
            self.toggle_column()            # the guide is in the column
        self.in_guide = True
        try:
            while True:
                if self.person is not None:
                    self.person(self.w, -2)        # tests: the player
                self.w.step()
                pressed, _ = self.read()
                if self.game_quit():
                    raise Leave()
                # (`pressed` is buttons only: the D-pad's bits, not the
                # stick)
                if pressed & (UP | B):
                    self.w.ui("class banner on 0")
                    return False
                if pressed & RIGHT and has_demo:
                    self.w.ui("class banner on 0")
                    return True
        finally:
            self.in_guide = False
            self.consume()

    def judged_drill(self, d, results):
        """A drill from a scenario file: a scenario against an opponent, or
        a tech drill judged by the frame (tools/melee_actor)."""
        sc = scn.load(str(self.here[d["id"]]))
        self.loading(d["name"])
        self.w.step()
        # the game sets the match up with its own presses, at full speed
        self.w.live(self.port, "off")
        self.w.pace(False)
        try:
            if sc.get("tech"):
                session = tech.Session(sc, self.w, self.port, self.c["id"])
            else:
                session = scn.Session(sc, game=self.w, person=self.port)
        finally:
            self.w.live(self.port, self.source)
            self.w.pace(True)
        self.session = session
        self.wait_released()
        self.screen = "drill"
        self.playing()
        self.in_match("drill", screens.drill_rail(
            self.c, d, self.course, sc.get("about", d["goal"])), START | DPAD)
        self.w.capture(False)
        first = random.randrange(1 << 20)
        while True:
            try:
                result = session.run(jitter=3.0, run=first + len(results),
                                     each_frame=self.drill_frame)
            except Abandon:
                continue
            if result.get("skip"):
                # not an attempt (an aerial with no lag to cancel):
                # say why, count nothing
                self.banner_say("Not counted",
                                result["words"].split(":")[0])
                continue
            results.append(bool(result["success"]))
            self.show_result(result, results)
            # Against an opponent the situation is put back, so the verdict
            # gets a moment first; a tech drill has nothing to put back and
            # the player sets the pace.
            for _ in range(0 if sc.get("tech") else 75):
                self.drill_frame(self.w, -1)
                self.w.step()

    # ---- free play --------------------------------------------------------------------

    def play(self, c):
        """Free play as this character."""
        self.say("Loading %s." % c["name"])
        self.w.step()
        self.w.pace(False)
        try:
            self.w.start(c["id"], self.opponent, self.stage,
                         seed=random.randrange(1, 1 << 30), settle=False)
        finally:
            self.w.pace(True)
        self.last = c
        self.screen = "match"
        self.start_held = 0
        self.playing()
        self.in_match("match", screens.match_rail(
            c, self.opponent.replace("-", " ").title(),
            self.stage.replace("-", " ").title()), START)
        self.w.capture(False)

    def on_match(self, pressed, moves):
        pass

    def run(self, frames=0):
        while not frames or self.frames < frames:
            self.frame()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--input", default="auto",
                    help="auto (a GameCube controller on the adapter, else "
                         "the first other controller, else the keyboard), "
                         "gcc1 to gcc4 (the adapter's ports), keyboard, "
                         "pad0, pad1, ...")
    ap.add_argument("--timing", action="store_true",
                    help="on leaving, say how evenly the pictures were "
                         "shown and where each frame's time went")
    ap.add_argument("--devices", action="store_true",
                    help="say which controllers the game sees, and stop "
                         "(nothing opens on the desktop)")
    ap.add_argument("--fullscreen", action="store_true",
                    help="start fullscreen (F11 switches while it runs, "
                         "and the choice is kept for next time)")
    ap.add_argument("--windowed", action="store_true",
                    help="start in a window, whatever was left last time")
    ap.add_argument("--offscreen", action="store_true",
                    help="on a virtual display (a test of this file)")
    ap.add_argument("--frames", type=int, default=0)
    ap.add_argument("--vsync", action="store_true")
    args = ap.parse_args()
    w = None
    if args.timing:
        import os
        os.environ["MELEE_TIMING"] = "1"
    if args.devices:
        with window.Window() as w:
            w.step(5)
            said = w.devices()
            for _ in range(10):
                if "looking" not in said:
                    break
                time.sleep(0.2)
                w.step(5)
                said = w.devices()
            print(said)
        return 0
    try:
        w = window.Window(real=not args.offscreen, gpu=True,
                          vsync=args.vsync, window=(1280, 720),
                          fullscreen=True if args.fullscreen else
                          False if args.windowed else None)
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
            if args.timing:
                rows = [line.strip() for line in w.log if "timing:" in line]
                late = sum(int(r.split(" of 60 late")[0].split()[-1])
                           for r in rows if " of 60 late" in r)
                inputs = [r for r in rows if "input read every" in r]
                bunched = sum(int(r.split(" closer than")[0].split()[-1])
                              for r in inputs)
                print("%d seconds measured, %d pictures shown late, %d "
                      "controller readings closer than 12 ms to the one "
                      "before" % (sum(" of 60 late" in r for r in rows),
                                  late, bunched))
                print("\n".join(rows[-6:]))
                log = ROOT / "build" / "client-timing.log"
                log.parent.mkdir(parents=True, exist_ok=True)
                log.write_text("\n".join(rows) + "\n")
                print("all of it: %s" % log)
            w.close()
        left = window.leftovers()
        if left:
            print("still running: %s" % left, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
