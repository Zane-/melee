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
against you with a verdict for every attempt; the stage select after the
characters, the game's own stages drawn by the native build (stages.py).
Hold START to come back. What is not: Events, Controls, most
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

import art  # noqa: E402
import buttons  # noqa: E402
import characters  # noqa: E402
import coach  # noqa: E402
import courses  # noqa: E402
import online  # noqa: E402
import opponents  # noqa: E402
import fonts  # noqa: E402
import icons  # noqa: E402
import marks  # noqa: E402
import screens  # noqa: E402
import settings  # noqa: E402
import stages  # noqa: E402
import window  # noqa: E402
import native  # noqa: E402
from native import STAGES, NativeError  # noqa: E402
from melee_actor import train  # noqa: E402
from melee_course import engine as course_engine  # noqa: E402
from melee_course import registry as course_registry  # noqa: E402

A, B, X, Y, START = 0x100, 0x200, 0x400, 0x800, 0x1000
L, R = 0x40, 0x20
LEFT, RIGHT, DOWN, UP = 1, 2, 4, 8
OUT = ROOT / "build" / "ui"
COLUMNS = screens.COLUMNS
STAGE_ORDER = tuple(s["id"] for s in stages.STAGES)
assert set(STAGE_ORDER) == set(STAGES)
CPU, NOBODY = "the game's own CPU", "nobody"
ONLINE = "a friend, online"
FRAMES_BEFORE_SESSION = 10   # both games, the same frames, nobody's input

# Which panel a direction leads to from each panel of the main menu:
# Versus the big one at the left, Train above Settings at the right.
MAIN_MOVES = {
    "versus": {RIGHT: "train"},
    "train": {LEFT: "versus", DOWN: "settings"},
    "settings": {LEFT: "versus", UP: "train"},
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


class Play:
    """The coach's card's pictures, played (the owner, 2026-11-14: "doesn't
    seem we have a robust animation system as well"): the try and the
    target side by side, frame for frame, from a little before the
    timeline to a moment after the end; at the game's own speed, the
    timeline's frames at half of it (a quarter, at 15 pictures a second,
    stuttered: "freezes often and is slow to loop", the owner), a short
    stop on the last, and again. Or frame by frame: `frame` steps one
    (and pauses), `toggle` pauses or plays ("The overlay should have frame
    by frame controls too so they can really see what the inputs should be
    like vs. what they are doing!"). Each panel is {"id": "y" or "t",
    "view", "ring", "seq": Client.coach_seq}; it shows the frame, a tag
    where a press starts, the pad on that frame (screens.pad_display), how
    far along, and the grid's column now."""

    SLOW, END, TAG = 2, 20, 8
    # the pad's bits, as the input display names its buttons
    BUTTONS = (("A", 0x100), ("B", 0x200), ("X", 0x400), ("Y", 0x800),
               ("Z", 0x10), ("L", 0x40), ("R", 0x20))

    def __init__(self, w, panels):
        self.w = w
        self.panels = [p for p in panels if p and p["seq"]]
        self.n = max([len(p["seq"]) for p in self.panels] or [0])
        self.sent = {}
        self.k, self.left, self.head = -1, 0, None
        self.paused = self.ended = False

    def _ui(self, key, line):
        if self.sent.get(key) != line:
            self.sent[key] = line
            self.w.ui(line)

    def _pad(self, pid, pad):
        """The input display: the buttons held, where the sticks are, how
        far the triggers are in."""
        pad = pad or {}
        held = pad.get("buttons", 0)
        for name, bit in self.BUTTONS:
            self._ui(pid + "i" + name, "class c%si%s on %d" % (
                pid, name, 1 if held & bit else 0))
        for part, x, y, middle, reach in (
                ("S", pad.get("lx", 0), pad.get("ly", 0), 10, 11),
                ("C", pad.get("cx", 0), pad.get("cy", 0), 7, 8)):
            x = max(-1.0, min(1.0, x / coach.STICK))
            y = max(-1.0, min(1.0, y / coach.STICK))
            self._ui(pid + "i" + part, "attr c%si%s style left: %ddp; top: "
                     "%ddp;" % (pid, part, round(middle + x * reach),
                                round(middle - y * reach)))
        for part, analog, bit in (("Lf", pad.get("lt", 0), 0x40),
                                  ("Rf", pad.get("rt", 0), 0x20)):
            amount = 1.0 if held & bit else min(1.0, analog / 255.0)
            self._ui(pid + "i" + part, "attr c%si%s style width: %ddp;" % (
                pid, part, round(26 * amount)))

    def show(self, k):
        """Frame `k` of each panel (its last, for one that is shorter)."""
        self.k = k
        slow = False
        for p in self.panels:
            seq, i = p["seq"], min(k, len(p["seq"]) - 1)
            e = seq[i]
            if e["pic"] is not None and e["pic"] != p.get("pic"):
                p["pic"] = e["pic"]
                self.w.frames_view(p["view"], p["ring"], e["pic"])
            pid = p["id"]
            label = e["label"]
            if self.paused:
                label = (label + " · " if label else "") + "PAUSED"
            self._ui(pid + "f", "text c%sf %s" % (pid, screens.esc(label)))
            self._ui(pid + "fo", "class c%sf on %d" % (pid, 1 if label
                                                      else 0))
            tag = next((seq[j]["tag"] for j in range(i, max(-1, i -
                                                          self.TAG), -1)
                        if seq[j]["tag"]), None)
            if tag:
                self._ui(pid + "pt", "text c%sp %s" % (pid, screens.esc(tag)))
            self._ui(pid + "p", "class c%sp on %d" % (pid, 1 if tag else 0))
            self._ui(pid + "b", "attr c%sb style width: %ddp;" % (
                pid, round(412.0 * i / max(1, len(seq) - 1))))
            self._pad(pid, e.get("pad"))
            slow = slow or e["slow"]
            if pid == "y":
                head = e["f"]
                if head != self.head:
                    if self.head is not None:
                        self.w.ui("class cgn%d now 0" % self.head)
                    if head is not None:
                        self.w.ui("class cgn%d now 1" % head)
                    self.head = head
        return slow

    def step(self):
        """One frame of the card: on to the next picture when it is time
        (not while paused)."""
        if not self.n or self.paused:
            return
        if self.left > 0:
            self.left -= 1
            return
        if self.k + 1 >= self.n:
            if self.k >= 0 and not self.ended:
                self.ended = True       # a moment on the last, then again
                self.left = self.END
                return
            k = 0
        else:
            k = self.k + 1
        self.ended = False
        self.left = (self.SLOW if self.show(k) else 1) - 1

    def frame(self, by):
        """A frame on (`by` 1) or back (-1), paused there; past either end,
        round to the other, as it plays."""
        if not self.n:
            return
        self.paused = True
        self.show((max(0, self.k) + by) % self.n)

    def toggle(self):
        """Pause, or play on from here."""
        self.paused = not self.paused
        self.left = 0
        if self.n:
            self.show(max(0, self.k))


# How long a button is held for its other meaning (frames, at 60 a second)
HOLD_COLUMN = 180      # START: hide or show the column
HOLD_DRILL = 120       # D-pad left or right: the drill before or after (2 s:
                       # the owner, 2026-11-13, "much too slow" at 3)
HOLD_STAGE = 300       # L or R: the stage before or after (drills with stages)
DPAD = LEFT | RIGHT | DOWN | UP


class Client:
    def __init__(self, game, port=0, source="auto", save=None, out=None):
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
        self.roster = characters.roster()
        self.opp_at = next(i for i, c in enumerate(self.roster)
                           if c["id"] == "marth")
        self.screen = None
        self.focus = "train"          # on the main menu
        self.last_match = None        # the last Versus match, in words
        self.lab_from = "chars"       # the Lab: "hub" or "chars"
        self.stage_job = None         # the stages being drawn
        self.at = next(i for i, c in enumerate(self.roster)
                       if c["id"] == "fox")   # on the character select
        self.last = None              # the character last played
        self.costume = {}             # character id -> the costume chosen
        self.buttons = 0
        self.pressed_now = self.released = 0
        self.held = {}                # direction -> frames held
        self.hold = {}                # button bit -> frames held
        self.used = set()             # bits whose hold already did something
        self.column_hidden = False    # START held: the column is put away
        self.column_versus = False    # a Versus match's, not the one kept
        self.pause_open = False       # tests: the pause menu is up
        self.pause_focus = None       # tests: the row in focus there
        self.session = None           # the drill's, while one runs
        self.status_text = None       # the drill's status line shown
        self.game_song = None         # the music a match had (sound below)
        self.rays_html = ""           # the drill's light rays shown
        self.drill_stages = None      # its stages, when it can change them
        self.has_cover = False        # a match's or a drill's screen is up
        self.start_held = 0
        self.frames = 0
        self.drill_now = None         # the drill being played
        self.tutorial_now = None      # tests: the tutorial's card shown
        self.example_now = None       # tests: the tutorial's example now
        self.track = None             # its try, frame by frame (coach)
        self.coach_misses = 0         # misses in a row since the coach
        self.pause_tab = None         # tests: the pause menu's tab
        self.pause_idents = []        # tests: the rows of that tab
        self.coach_open = False       # tests: the coach's card is up
        self.coach_now = None         # tests: what it said
        self.coach_play = None        # tests: its pictures, as they play
        self.replay_now = None        # tests: the replay's mode and frame
        self.replay_result = None     # tests: how the replayed try ended
        self.out.mkdir(parents=True, exist_ok=True)
        # the game's pictures, off the disc; Sheik, who has none, drawn
        # from her model in a process of its own the first time (half a
        # minute): her place shows her emblem until then
        art.ensure()
        self.art_job = art.render_sheik_later()
        # the stage select's: the game's name logos off the disc; each
        # stage drawn by the native build the first time (half a minute),
        # its name logo on its panel until then
        stages.ensure()
        self.stage_job = stages.render_later()
        # the menu panels' large faded drawings
        screens.MARKS.update(marks.ensure())
        # SmashWiki's GameCube button icons, fetched the first time
        screens.BUTTONS.update(buttons.ensure())
        # the pause menu's icons (our own drawings, made into pictures)
        screens.ICONS.update(icons.ensure())
        for f in fonts.fonts():
            self.w.ui("font " + str(f))
        self.w.live(port, source)
        # the settings (Settings in the main menu): input delay, rumble, UCF
        self.settings = settings.get(self.progress)
        settings.apply(self.w, self.settings)
        self.column_hidden = not self.settings["sidebar"]
        try:
            where = self.w.where()
            if not where.get("asked") and \
                    list(where["size"]) != list(self.settings["size"]):
                self.w.resize(*self.settings["size"])
        except Exception:
            pass
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

    def load_quietly(self, fn):
        """Load a match (fn): the game sets it up with its own presses, as
        fast as it goes, unseen and unheard (`quiet`: the window keeps its
        last picture, a menu's or a drill's, and the sound stops), and the
        new one appears on the next frame. No loading screen, as TM-CE's
        savestate loads: the owner, 2026-11-13, "no loading screens, no
        chopiness, no fast forwarding"."""
        self.w.live(self.port, "off")
        self.w.quiet(True)
        try:
            return fn()
        finally:
            self.w.quiet(False)
            self.w.live(self.port, self.source)

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
        """A menu sound, played by the game. Not while a netplay session
        runs: a sound the game starts on one side only puts the two games'
        states apart (rollback saves and restores them), and an online
        match sometimes hung leaving through its pause menu."""
        if getattr(self, "online", None) is not None:
            return
        try:
            self.w.sfx(n)
        except Exception:             # a build without sound commands
            pass

    def menu_music(self):
        """The main menu's music on the menu screens (the owner: "the main
        menu music"); the match's is kept to put back."""
        if hasattr(self, "settings"):
            self.volumes_now()              # the menus' sounds' volume
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
        if hasattr(self, "settings"):
            self.volumes_now()              # the game's sounds' volume
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
                tuple(self.row), getattr(self, "part", None),
                getattr(self, "sfocus", None), getattr(self, "ctl_at", None),
                getattr(self, "rport", None), getattr(self, "sub", None),
                getattr(self, "sub_at", None), getattr(self, "fr_at", None))

    def show_main(self):
        self.menu_music()
        self.screen = "main"
        self.w.capture(True)
        last = (self.last["name"], self.last["color"]) if self.last else None
        self.load("main", screens.main_menu(last, self.last_match,
                                            self.focus))
        self.w.ui("class %s focus 1" % self.focus)
        self.say(self.about(self.focus))

    def show_characters(self):
        self.menu_music()
        self.screen = "chars"
        self.w.capture(True)
        self.load("characters",
                  screens.character_select(self.roster, self.at,
                                           costume=self.dressed()))

    def about(self, ident):
        item = next(i for i in screens.MAIN if i[0] == ident)
        return item[3] + ("" if item[4] else
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
        if self.art_job is not None and self.art_job.poll() is not None:
            self.art_job = None
            if self.screen == "chars":
                self.show_characters()
            elif self.screen == "opp":
                self.show_opponent()
        if self.stage_job is not None and self.stage_job.poll() is not None:
            self.stage_job = None
            if self.screen == "stages":
                self.show_stages()
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
        elif self.screen == "versus":
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
        if self.screen not in ("versus", "online_match") and \
                pressed & (A | START):
            # choosing: the sound now, before what it opens (a drill runs
            # inside the list's frame)
            self.sfx(self.SFX_FORWARD)
            pressed_sound = A | START
        else:
            pressed_sound = 0
        getattr(self, "on_" + self.screen)(pressed, moves)
        if before[0] not in ("versus", "online_match"):
            self.menu_sounds(before, pressed & ~pressed_sound)

    def leave_match(self, to):
        """Out of Versus or the Lab, chosen in the pause menu."""
        if self.screen == "versus":
            if self.bot is not None:
                self.bot.close()
                self.bot = None
            self.w.pad(1 - self.port)
        self.w.mask(0)
        self.inputs_off()
        self.has_cover = False
        self.column_as_kept()
        if to == "main":
            self.show_main()
        elif to == "stages":
            self.show_stages()
        elif to == "hub":
            self.show_hub()
        else:
            self.show_opponent()

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
            if not self.column_versus:      # (Versus's own is not kept)
                self.settings["sidebar"] = not self.column_hidden
                self.progress.save()
        on = 1 if self.column_hidden else 0
        self.w.ui("class rail hidden %d" % on)
        for ident in ("bannerwrap", "pause", "rays", "coach"):
            self.w.ui("class %s mid %d" % (ident, on))
        self.w.ui("center %d" % on)

    def in_match(self, name, rml, mask):
        """Load a match's or a drill's screen: the buttons the game does
        not see (`mask`: START, and the D-pad in drills), the column as
        the player left it."""
        self.load(name, rml)
        self.has_cover = True
        self.w.mask(mask)
        self.inputs_now()
        self.match_music()
        # Versus, local or online: the sidebar put away to begin with (the
        # owner, 2026-11-14: "hide the sidebar by default in versus, it is
        # only really relevant in training mode"); START held brings it
        # back for that match. Drills and the Lab keep it as it was left.
        self.column_versus = name == "versus" and self.mode == "versus"
        if self.column_versus:
            self.column_hidden = True
        if self.column_hidden:
            self.toggle_column(apply_only=True)

    def column_as_kept(self):
        """Out of a Versus match: the sidebar as the player keeps it."""
        self.column_versus = False
        self.column_hidden = not self.settings["sidebar"]

    # ---- the pause menu ----------------------------------------------------------

    INPUT_WORDS = {"off": "Off", "you": "You", "opponent": "Opponent",
                   "both": "You and opponent"}

    def coach_words(self):
        n = self.settings.get("coach", 0)
        return "After %d misses" % n if n else "Off"

    def pause_tabs(self, kind):
        """The pause menu's tabs for a `kind` of match ("drill", "versus",
        "online")."""
        if kind == "drill":
            return ["Drill", "Course", "Settings"]
        return ["Match", "Settings"]

    def pause_rows(self, kind, tab=None):
        """(id, label, value or None, icon) for a tab of the pause menu (the
        canvas's "Paused: icons and the input display"); the first tab
        without one. A value changes with left and right."""
        tab = tab or self.pause_tabs(kind)[0]
        s = self.session
        course = kind == "drill" and isinstance(s, course_engine.Session)
        if tab == "Settings":
            rows = []
            if kind != "online":    # online, the session's delay holds
                rows.append(("delay", "Input delay", self.delay_words(),
                             "delay"))
            rows.append(("inputs", "Input display",
                         self.INPUT_WORDS[self.settings["inputs"]], "input"))
            if kind == "drill":
                rows.append(("coach", "Coach", self.coach_words(), "coach"))
            return rows
        if tab == "Course":
            return [("list", "Back to menu", None, "menu"),
                    ("hub", "Back to course", None, "course"),
                    ("main", "Main menu", None, "home")]
        rows = [("resume", "Resume", None, "play")]
        if kind == "drill":
            rows.append(("reset", "Restart", None, "restart"))
        if course:
            for i, o in enumerate(s.d.options):
                rows.append(("opt%d" % i, o.name, o.label(s.opts[i]),
                             "options"))
            if s.d.deck:
                names = ["Random"] + s.scenario_names()
                rows.append(("scen", "Scenario",
                             names[s.common[course_engine.OPT_SCENARIO]],
                             "shuffle"))
            if s.cpu_port is not None:
                rows.append(("side", "CPU side", ("Random", "Left", "Right")[
                    s.common[course_engine.OPT_SIDE]], "side"))
            if s.d.stages:
                rows.append(("stage", "Stage", s.d.stage.replace(
                    "-", " ").title(), "stage"))
        if course:
            rows.append(("coach", "Coach", self.coach_words(), "coach"))
        rows.append(("inputs", "Input display",
                     self.INPUT_WORDS[self.settings["inputs"]], "input"))
        if course:
            rows.append(("guide", "Tutorial", None, "guide"))
        rows.append(("column", "Show sidebar" if self.column_hidden
                     else "Hide sidebar", None, "sidebar"))
        if kind == "versus":
            rows.append(("opp", "Opponent select", None, "person"))
            rows.append(("stages", "Stage select", None, "stage"))
            if self.mode == "lab" and self.lab_from == "hub":
                rows.append(("hub", "Course", None, "course"))
        elif kind == "online":
            rows.append(("back", "Leave match", None, "leave"))
        elif kind != "drill":
            rows.append(("back", "Back", None, "leave"))
        if kind != "drill":
            rows.append(("main", "Main menu", None, "home"))
        return rows

    def pause_change(self, ident, step):
        """Left or right on a value: (whether it is one, whether the drill
        changed: its next attempt starts afresh)."""
        s = self.session
        if ident == "inputs":
            i = settings.INPUTS.index(self.settings["inputs"])
            self.settings["inputs"] = settings.INPUTS[
                (i + step) % len(settings.INPUTS)]
            self.progress.save()
            self.inputs_now()
            return True, False
        if ident == "coach":
            i = settings.COACH.index(self.settings["coach"])
            self.settings["coach"] = settings.COACH[
                (i + step) % len(settings.COACH)]
            self.progress.save()
            return True, False
        if ident == "delay":
            n = max(0, min(settings.DELAY_MAX, self.settings["delay"] + step))
            self.settings["delay"] = n
            self.progress.save()
            try:
                self.w.delay(n)
            except Exception:
                pass
            return True, False
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
            return False, False
        return True, True

    def pause_tags(self, kind):
        """The line over "Paused": where the player is."""
        d = getattr(self, "drill_now", None)
        if kind == "drill" and d is not None and self.course is not None:
            total = len(self.course["parts"][d["part"]])
            return "%s · %d OF %d · %s" % (d["part"].upper(), d["number"],
                                           total, d["name"].upper())
        return {"versus": "VERSUS", "online": "ONLINE"}.get(kind,
                                                             "FREE PLAY")

    def pause_neighbours(self, kind):
        """The drills before and after this one in the course (names), or
        (None, None)."""
        if kind != "drill" or self.course is None:
            return None, None
        drills = self.drills()
        if len(drills) < 2:
            return None, None
        at = self.row[self.part]
        return (drills[(at - 1) % len(drills)]["name"],
                drills[(at + 1) % len(drills)]["name"])

    def pause(self, kind):
        """Our pause menu over the frozen match, until it is closed (None,
        or ("options",) when the drill was changed) or something is chosen
        (an event as controls() gives). L and R change tab; the drills
        before and after are two buttons under the rows."""
        tabs = self.pause_tabs(kind)
        tab = tabs[0]
        rows = self.pause_rows(kind, tab)
        before, after = self.pause_neighbours(kind)
        nav = before is not None
        at = 0          # a row, or len(rows): the drills' buttons
        side = 1        # which of them: 0 before, 1 after
        changed = False

        def draw():
            on_nav = at >= len(rows)
            self.pause_focus = ("prev", "next")[side] if on_nav \
                else rows[at][0]
            self.pause_tab = tab
            self.pause_idents = [r[0] for r in rows] + (
                ["prev", "next"] if nav else [])
            self.put("ptabs", screens.pause_tabs(tabs, tab))
            self.put("prows", screens.pause_rows(rows, None if on_nav
                                                 else at))
            self.put("pnav", screens.pause_nav(before, after, side if on_nav
                                               else None))

        frozen = kind != "online"   # online the game goes on: both sides
        if frozen:
            self.w.freeze(True)
        self.pause_open = True
        self.w.ui("text ptitle Paused")
        self.w.ui("text ptags " + screens.esc(self.pause_tags(kind)))
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
                count = len(rows) + (1 if nav else 0)
                if pressed & (L | R) and len(tabs) > 1:
                    step = 1 if pressed & R else -1
                    tab = tabs[(tabs.index(tab) + step) % len(tabs)]
                    rows = self.pause_rows(kind, tab)
                    at = 0
                    self.sfx(self.SFX_MOVE)
                    draw()
                    continue
                if moves & (UP | DOWN):
                    at = (at + (1 if moves & DOWN else -1)) % count
                    self.sfx(self.SFX_MOVE)
                    draw()
                if moves & (LEFT | RIGHT):
                    step = 1 if moves & RIGHT else -1
                    if at >= len(rows):
                        side = 1 if step > 0 else 0
                        self.sfx(self.SFX_MOVE)
                        draw()
                    else:
                        known, drill = self.pause_change(rows[at][0], step)
                        if known:
                            self.sfx(self.SFX_MOVE)
                            changed = changed or drill
                            rows = self.pause_rows(kind, tab)
                            draw()
                if pressed & A:
                    self.sfx(self.SFX_FORWARD)
                    if at >= len(rows):
                        return ("drill", 1 if side else -1)
                    ident = rows[at][0]
                    if ident == "resume":
                        return done
                    if ident == "column":
                        self.toggle_column()
                        rows = self.pause_rows(kind, tab)
                        draw()
                        continue
                    if ident in ("guide", "demo", "reset"):
                        return (ident,)
                    if ident in ("list", "hub", "main", "opp", "stages",
                                 "back"):
                        return ("leave", ident)
        finally:
            self.w.ui("class pause on 0")
            self.pause_open = False
            self.pause_focus = None
            self.consume()                  # still frozen while let go
            if frozen:
                self.w.freeze(False)

    # ---- the input display ---------------------------------------------------

    def inputs_now(self, extra=0):
        """TM-CE's input display, as the settings ask, in the match on now:
        the player's controller, the opponent's, both or none (`extra`:
        ports shown besides, as the replay shows the player's)."""
        me = 1 << self.port
        them = 1 << (1 - self.port) if self.port in (0, 1) else 0
        mask = {"off": 0, "you": me, "opponent": them,
                "both": me | them}[self.settings["inputs"]] | extra
        try:
            self.w.inputs(mask)
        except Exception:           # a build without the command
            pass

    def inputs_off(self):
        try:
            self.w.inputs(0)
        except Exception:
            pass

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
                self.w.ui("attr tab style background-color: %s" % (
                    "#D0283E" if to == "versus" else "#F3F6FA"))
                break
        if pressed & A:
            if self.focus == "versus":
                self.mode = "versus"
                self.show_versus_menu()
            elif self.focus == "train":
                self.mode = "train"
                self.show_characters()
            elif self.focus == "settings":
                self.show_settings()
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
            self.say(next(v[3] for v in screens.VERSUS if v[0] == to))
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
            self.w.ui("class c%d focus 1" % at)
            self.show_card()
        if pressed & X and self.roster[self.at].get("other") is not None:
            self.switch(self.at)
            self.show_card()
        if pressed & Y:
            c = self.roster[self.at]
            self.costume[c["id"]] = (self.dressed() + 1) % c["costumes"]
            self.show_card()
        if pressed & A:
            self.dress()
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
                self.lab(c, "chars")

    def show_card(self):
        c = self.roster[self.at]
        self.put("card", screens.card(c, self.dressed()))
        self.w.ui("attr tab style background-color: %s" % c["color"])

    def switch(self, at):
        """Zelda's place: Sheik or Zelda, the one it does not hold now."""
        c = self.roster[at] = self.roster[at]["other"]
        self.w.ui("attr c%d style background-color: %s" % (at, c["color"]))
        self.put("c%d" % at, screens.tile(c))

    def dressed(self, c=None):
        """The costume chosen for `c` (the character in focus)."""
        c = c or self.roster[self.at]
        return min(self.costume.get(c["id"], 0), c["costumes"] - 1)

    def dress(self, me=None, opp=None):
        """The game puts the player (`me`: the character in focus) in the
        costume chosen for it, in every match from now on (a drill's own
        too), and the other side in its default; or, if `opp` is the same
        character, in its second."""
        me = me or self.roster[self.at]
        mine = self.dressed(me)
        self.w.costume(self.port, mine)
        other = 1 if opp is not None and opp["id"] == me["id"] and \
            mine == 0 else 0
        self.w.costume(1 - self.port, other)

    # ---- versus and the lab: who is on the other side ------------------------------

    def players(self):
        """Who can play the opponent in focus: [(key, name, what it is)],
        the key a model's file or CPU or NOBODY. In Versus the trained
        models come first, by difficulty (opponents.models); in the Lab
        nobody does."""
        opp = self.roster[self.opp_at]
        trained = opponents.models(opp["id"], self.me["id"])
        rest = [(CPU, "CPU", "The game's own AI"),
                (NOBODY, "Dummy", "Stands still")]
        if self.mode == "lab":
            rest.reverse()
            return rest + trained
        return trained + rest

    def opponent_card(self):
        players = self.players()
        _, name, what = players[self.who]
        return screens.opponent_card(
            self.roster[self.opp_at], name, what,
            "%d of %d" % (self.who + 1, len(players)), "Choose stage")

    def lab(self, c, came_from):
        """The Lab as `c` (the owner, 2026-11-14: "move Lab into Train, it
        should replace the free play button (clicking this should allow
        the user to select the character and stage)"): the opponent, then
        the stage. `came_from`: "hub" or "chars", where B goes back to."""
        self.mode = "lab"
        self.lab_from = came_from
        self.me = c
        self.who = None
        self.show_opponent()

    def show_opponent(self):
        self.menu_music()
        self.screen = "opp"
        self.w.capture(True)
        if self.who is None or self.who >= len(self.players()):
            self.who = 0
        self.load("opponent", screens.character_select(
            self.roster, self.opp_at, title="Choose your opponent",
            about="%s against whom, and played by whom." % self.me["name"],
            inside=self.opponent_card(),
            hints=[("A", "Choose stage"), ("X", "Played by"),
                   ("B", "Back")]))

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
        if pressed & Y and self.roster[self.opp_at].get("other") is not None:
            self.switch(self.opp_at)
            self.w.ui("attr tab style background-color: %s" %
                      self.roster[self.opp_at]["color"])
            self.who = 0
            changed = True
        if changed:
            self.put("card", self.opponent_card())
        if pressed & B:
            if self.mode == "lab" and self.lab_from == "hub":
                self.show_hub()
            else:
                if self.mode == "lab":
                    self.mode = "train"
                self.show_characters()
        elif pressed & A:
            self.show_stages()

    # ---- the stage select ---------------------------------------------------------

    def go_word(self):
        return "Start" if self.mode == "lab" else "Fight"

    def show_stages(self):
        """After the characters, where they play (the canvas's "A · Stage
        select: grid and card")."""
        self.menu_music()
        self.screen = "stages"
        self.w.capture(True)
        self.load("stages", screens.stage_select(
            stages.STAGES, self.stage_at, self.me,
            self.roster[self.opp_at], self.go_word()))

    def on_stages(self, pressed, moves):
        at, n, cols = self.stage_at, len(STAGE_ORDER), screens.STAGE_COLUMNS
        if moves & LEFT and at % cols > 0:
            at -= 1
        if moves & RIGHT and at % cols < cols - 1 and at + 1 < n:
            at += 1
        if moves & UP and at >= cols:
            at -= cols
        if moves & DOWN and at + cols < n:
            at += cols
        if at != self.stage_at:
            self.w.ui("class s%d focus 0" % self.stage_at)
            self.stage_at = at
            self.w.ui("class s%d focus 1" % at)
            self.put("card", screens.stage_card(stages.STAGES[at],
                                                self.go_word()))
        if pressed & B:
            self.show_opponent()
        elif pressed & X:
            # as the game's own Random: one of them, and the match starts
            self.stage_at = random.randrange(n)
            self.fight()
        elif pressed & A:
            self.fight()

    def fight(self):
        """A match against the opponent chosen, played as chosen."""
        opp = self.roster[self.opp_at]
        key, name, what = self.players()[self.who]
        stage = STAGE_ORDER[self.stage_at]
        if self.bot is not None:
            self.bot.close()
            self.bot = None
        if key not in (CPU, NOBODY):
            self.bot = opponents.Bot(key, port=1 - self.port,
                                     opponent=self.port, stage=stage)
        self.bot_said = None
        self.w.pad(1 - self.port)
        self.dress(self.me, opp)
        self.load_quietly(lambda: self.w.start(
            self.me["id"], opp["id"], stage,
            seed=random.randrange(1, 1 << 30), p2_human=key != CPU,
            settle=False))
        self.last = self.me
        if self.mode == "versus":
            self.last_match = "%s against %s · %s" % (
                self.me["name"], opp["name"], stages.BY_ID[stage]["name"])
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
        # both games set up the same match: the default costumes, as the
        # friend's game does not know the one chosen here
        self.w.costume(0, 0)
        self.w.costume(1, 0)
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
            status, self.settings["delay"], getattr(self, "router", None)))

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
            self.put("orows", screens.online_body(
                self.lobby.code if self.lobby else "-", rows, at,
                self.settings["delay"], getattr(self, "router", None)))
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
                stage=STAGE_ORDER[self.stage_at],
                delay=self.settings["delay"], tick=tick)
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
        # both sides have to play one game: UCF on, as Slippi has it,
        # whatever this player chose for practice (put back on leaving)
        try:
            self.w.ucf(True)
        except Exception:
            pass
        self.w.live(self.port, "off")
        self.w.pad(0)
        self.w.pad(1)
        # unseen and unheard, as every load (load_quietly); both sides
        # load the same way, so the two games stay the same. The quiet
        # stretch ends before the frames ahead of the session: the music
        # the match asked for starts when it ends, and started on the
        # session's first frame its stream's first read was still on its
        # way when rollback began, and a game hung later (3 runs in 4 of
        # tests/client/online.py).
        self.w.quiet(True)
        try:
            self.w.start(met["chars"][0], met["chars"][1], met["stage"],
                         seed=met["seed"], p2_human=True, settle=False)
        finally:
            self.w.quiet(False)
        self.w.step(FRAMES_BEFORE_SESSION)
        # the person plays the session's local port
        self.port = local
        self.w.live(local, self.source)
        self.w.net("start", local, met["bind"], met["peer"][0],
                   met["peer"][1], met["delay"])
        self.online = dict(them=them, met=met, frames=0, said=None)
        opp = characters.find(self.roster, met["chars"][other])[1]
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
        settings.apply(self.w, self.settings)   # UCF as the player had it
        self.w.mask(0)
        self.inputs_off()
        self.has_cover = False
        self.online = None
        self.column_as_kept()
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
                self.bot_state("Loading. The opponent stands still until "
                               "it is ready.")
            elif not ready:
                self.bot_state("Could not load (%s). The opponent stands "
                               "still." % self.bot.error[:80])
            else:
                self.bot_state("%d-frame reaction." % self.bot.delay)
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
                # put back, as a TM-CE savestate load: clean, then placed
                self.w.clean()
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
        if self.hub_at == "lab":
            return "Lab: free practice against an opponent and on a stage " \
                "you choose. Nothing is judged."
        part = courses.PARTS[int(self.hub_at[1])]
        return "%s: %s Every part is open from the start." % (
            part, courses.ABOUT[part][1])

    def show_hub(self):
        self.menu_music()
        self.screen = "hub"
        self.mode = "train"
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
            if self.hub_at != "lab" else "#5B3FD6"
        self.w.ui("attr tab style background-color: %s" % color)

    def on_hub(self, pressed, moves):
        at = self.hub_at
        if at == "lab":
            if moves & UP:
                at = "p%d" % self.part
        else:
            i = int(at[1])
            if moves & LEFT and i > 0:
                at = "p%d" % (i - 1)
            if moves & RIGHT and i < 3:
                at = "p%d" % (i + 1)
            if moves & DOWN:
                self.part, at = i, "lab"
        if at != self.hub_at:
            self.w.ui("class %s focus 0" % self.hub_at)
            self.hub_at = at
            self.w.ui("class %s focus 1" % at)
            self.hub_tab()
        left = self.left_off()
        if pressed & B:
            self.show_characters()
        elif pressed & A and self.hub_at == "lab":
            self.lab(self.c, "hub")
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
        self.record(frame)

    def record(self, frame):
        """A try frame by frame, for the coach: where the fighters are, the
        pad the game is given for the frame to come, and the number of the
        game's picture of it (kept in ring 0: pictures_rec)."""
        s = self.session
        if frame < 0:
            return
        if not isinstance(s, course_engine.Session) or s.demo_pass:
            return
        if frame == 0 or self.track is None:
            self.track = coach.Track()
        self.track.add(s.c, s.live_pad if s.live else s.player_pad, frame,
                       self.w.frame)

    # the slot that keeps the moment the coach opened
    COACH_NOW = 29

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
                self.inputs_off()
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
        self.drill_now = d
        self.coach_misses = 0
        self.track = None
        # the pictures follow both fighters; with no opponent the player
        # alone
        self.pic_follow = (1 << self.port if course_registry.get(
            d["id"]).cpu is None else 3)
        self.pictures_rec(0)
        try:
            self.course_drill(d, results)
        except Leave as left:
            return left
        finally:
            # kept even when the game goes away mid-drill (the window
            # closed): the tries so far count
            self.progress.record(d["id"], self.c["id"], results)
            self.results = results
            try:
                self.w.camera("normal")     # (a drill may have set its own)
            except Exception:       # the game is gone
                pass
            try:
                self.pictures_rec(-1)
            except Exception:       # the game is gone
                pass
        return Leave()

    def pictures_rec(self, ring):
        """The game's pictures kept in ring `ring` from now on (0: the
        live one, 1: a run played unseen; -1: none). False when this game
        cannot (built before src/host/frames.c): the coach draws paths."""
        if getattr(self, "pictures", None) is False:
            return False
        try:
            if ring == 1:
                self.w.frames_clear(1)
            self.w.frames_rec(ring, getattr(self, "pic_follow", 15))
            self.pictures = True
        except NativeError:
            self.pictures = False
        return self.pictures

    def wait_released(self):
        # The A that started the drill is still down, and A in shield is
        # a grab: wait for the buttons to be let go before the first try.
        for _ in range(90):
            self.w.step()
            if not self.w.pads()[self.port]["buttons"] & (A | B | X | Y):
                break

    def course_opponents(self):
        """The opponents of the course's drills on the course engine, the
        most used first: a drill's match loads them all (Session's `also`),
        so that the drills after it find theirs and start at once."""
        key = self.c["id"]
        if getattr(self, "_opponents_of", (None,))[0] != key:
            count = {}
            for part in self.course["parts"].values():
                for d in part:
                    if self.here.get(d["id"]) != courses.COURSE or \
                            not course_registry.has(d["id"]):
                        continue
                    drill = course_registry.get(d["id"])
                    for c in ({e.cpu for e in drill.deck} if drill.deck
                              else {drill.cpu}):
                        if c is not None:
                            count[c] = count.get(c, 0) + 1
            self._opponents_of = (key, sorted(count, key=lambda c:
                                              -count[c]))
        return list(self._opponents_of[1])

    def course_drill(self, d, results):
        """A drill on the course engine (tools/melee_course): the overlay's
        drill, ported. The match the last drill left is kept when it can
        play this one (`reuse`), and a new opponent is swapped in, so most
        drills start at once; a match that must be loaded is loaded
        quietly (on_load)."""
        drill = course_registry.get(d["id"])
        session = course_engine.Session(
            drill, self.w, person=self.port, character=self.c["id"],
            live=True, on_load=self.load_quietly,
            seed=random.randrange(1, 1 << 30), dpad=False, reuse=True,
            also=self.course_opponents())
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
        if getattr(drill, "spec", None) is not None:
            # a drill in the drill format: the part the player was on, and
            # its tutorial before the first try
            prog = self.progress.drill(d["id"])
            drill.set_part(prog.get("part", 0))
            if not prog.get("tutorial"):
                try:
                    self.tutorial(drill, session, intro=True)
                except Abandon as a:
                    demo = self.course_abandon(a, drill, session)
        while True:
            if demo:
                # the game plays the reference; the player is still read
                # (a D-pad press or START stops it)
                self.w.scripted(self.port, True)
                session.live = False
                self.banner_say("Demo", "Demonstration")
            flowed = session.flowing and drill.flow
            try:
                result = session.run(each_frame=self.drill_frame, demo=demo)
            except Abandon as a:
                demo = self.course_abandon(a, drill, session)
                continue
            finally:
                try:
                    self.w.scripted(self.port, False)
                except (NativeError, OSError):
                    pass        # the game is gone (the window closed)
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
                if result.get("part_passed"):
                    # the part done: on to the next, with its own page
                    prog = self.progress.drill(d["id"])
                    prog["part"] = drill.part_index
                    self.progress.save()
                    if result.get("next_part"):
                        self.banner_say("Part done", "Next: " +
                                        result["next_part"])
                        try:
                            self.tutorial(drill, session, intro=False)
                        except Abandon as a:
                            demo = self.course_abandon(a, drill, session)
                        self.coach_misses = 0
                        continue
                self.coach_misses = 0 if result["success"] else \
                    self.coach_misses + 1
                n = self.settings.get("coach", 0)
                if n and self.coach_misses >= n and self.track is not None:
                    self.coach_misses = 0
                    try:
                        self.coach(drill, session, result, flowed)
                    except Abandon as a:
                        demo = self.course_abandon(a, drill, session)
                        continue
            # a moment to read the verdict (the C engine's reset delay),
            # except where the drill carries on from where you stand. The
            # D-pad and the pause menu work here as in an attempt: what they
            # ask for (the guide, a restart, a changed option) once ended
            # the client, coming from outside the attempt (the owner,
            # 2026-11-13: D-pad up in the shield drop drill, "Hits" in
            # shield pressure)
            try:
                for _ in range(0 if drill.flow else 45):
                    self.drill_frame(self.w, -1)
                    self.w.step()
            except Abandon as a:
                demo = self.course_abandon(a, drill, session)

    def course_abandon(self, a, drill, session):
        """What an attempt was left for (the D-pad, the pause menu): do it.
        Returns whether a demonstration comes next."""
        session.flowing = False
        if a.what == "scenario":
            session.change_scenario(a.step)
            self.banner_say("Scenario", session.scenario_names()[
                session.scenario])
        elif a.what == "guide":
            if getattr(drill, "spec", None) is not None:
                self.tutorial(drill, session, intro=True)
                return False
            return self.course_guide(drill, session)
        elif a.what == "demo":
            return True
        elif a.what == "stage":
            i = drill.stages.index(drill.stage)
            session.set_stage(drill.stages[(i + a.step) %
                                           len(drill.stages)])
            self.w.ui("text stage Stage: " + screens.esc(
                drill.stage.replace("-", " ").title()))
            self.banner_say("Stage", drill.stage.replace("-", " ").title())
        return False

    def course_guide(self, drill, session):
        """The guide, in the column, until D-pad up or B (go on) or right
        (watch a demonstration first: returns True)."""
        lines = drill.guide(session.c)
        self.verdict_colour(None)
        self.w.ui("text verdict Tutorial")
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
        self.banner_say("Tutorial", "D-pad right: demonstration. D-pad "
                        "up: "
                        "close")
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

    # ---- the tutorial (a drill in the drill format: tools/melee_drills) --------
    #
    # The owner, 2026-11-14: "tutorial and coach are different. Tutorial
    # should show HOW to do the tech, coach pops up when you mess up to help
    # show you what you did wrong and how to fix it." The tutorial plays on a
    # drill's first open (and on D-pad up): what it is and why, the
    # technique in parts, what to expect, and an example played from the
    # drill's start with the input display, then frame by frame, each frame
    # captioned. A part passed opens the next with its own page.

    def tutorial(self, drill, session, intro=True):
        """The drill's tutorial (`intro`), or the page of the part now (a
        part just opened). Up and down choose the part on the intro."""
        from melee_drills import format as fmt
        spec = drill.spec
        nums = drill.nums(session.c)

        def T(t):
            return fmt.text(t, nums)
        while True:
            part = drill.part_now
            n = len(drill.parts)
            i = drill.part_index
            states = [(T(p["name"]), "done" if k < i else "now" if k == i
                       else "") for k, p in enumerate(drill.parts)]
            if intro:
                tut = spec["tutorial"]
                blocks = [("Goal", T(spec["goal"])), ("Why", T(spec["why"])),
                          ("What it is", T(tut["what"])),
                          ("What to expect", T(tut["expect"]))]
                example, marks = tut["example"], tut.get("marks", {})
                keys = [("A", "Show me, frame by frame"),
                        ("D-UP", "Choose the part"),
                        ("B", "Start part %d" % (i + 1))]
                sub = "%s\n%d PARTS" % (nums["char"].upper(), n)
                parts = states
            else:
                want = "; ".join(
                    T(spec["checks"][c].get("expect", c))
                    for c in part.get("checks", [])) or "Any try"
                blocks = [("Part %d of %d: %s" % (i + 1, n, T(part["name"])),
                           T(part["teach"])),
                          ("To pass it, %d in a row" % part["streak"],
                           want + ".")]
                example, marks = part["example"], part.get("marks", {})
                keys = [("A", "Show me, frame by frame"), ("B", "Start")]
                sub = "PART %d OF %d" % (i + 1, n)
                parts = None
            view = dict(title=T(spec["name"]) if intro else T(part["name"]),
                        sub=sub, blocks=blocks, parts=parts, keys=keys)
            what = self.tutorial_card(view, choose=intro)
            if what == "example":
                self.tutorial_example(drill, session, example, marks,
                                      T(spec["name"]) if intro
                                      else T(part["name"]))
                continue
            if isinstance(what, int):
                drill.set_part(drill.part_index + what)
                continue
            break
        prog = self.progress.drill(spec["id"])
        prog["tutorial"] = True
        prog["part"] = drill.part_index
        self.progress.save()

    def tutorial_card(self, view, choose=False):
        """The card until A ("example"), B ("go"), or with `choose` up or
        down (-1, 1: another part)."""
        self.tutorial_now = view            # tests: what the card says
        self.w.ui("class banner on 0")
        self.banner = 0
        self.put("coach", screens.tutorial_card(view))
        self.w.ui("class coach on 1")
        self.w.freeze(True)
        try:
            while True:
                if self.person is not None:
                    self.person(self.w, -6)        # tests: the player
                self.w.step()
                pressed, moves = self.read()
                if self.game_quit():
                    raise Leave()
                if pressed & A:
                    self.sfx(self.SFX_FORWARD)
                    return "example"
                if pressed & (B | START):
                    self.sfx(self.SFX_FORWARD)
                    return "go"
                if choose and moves & (UP | DOWN):
                    return -1 if moves & UP else 1
        finally:
            self.w.ui("class coach on 0")
            self.consume()
            self.w.freeze(False)

    def tutorial_example(self, drill, session, inputs, marks, name):
        """The example played from the drill's start, the input display
        on: at the game's speed to the example's first frame, its frames at
        half speed, stopping on each one that has a caption; the D-pad steps
        a frame either way, A plays or pauses, B goes on."""
        from melee_drills import format as fmt
        from melee_drills.drill import REF_START
        nums = drill.nums(session.c)
        at = {}
        for f, words in marks.items():
            at[int(fmt.value(f, nums))] = fmt.text(words, nums)
        pressed_on = {}
        for i in inputs:
            f = int(fmt.value(i["frame"], nums))
            pressed_on.setdefault(f, (i.get("press") or i.get("trigger") or
                                      ("Stick" if "stick" in i else "C"))
                                  .replace("jump", "X")[:5])
        last = max(list(at) + list(pressed_on) + [nums["J"] + 1])
        n = last + 6                        # a few frames after the last mark
        lead = course_engine.REF_LEAD + REF_START - 1   # frame 0 of it
        d = self.drill_now or {"part": "Tech", "number": 1, "name": name}
        total = len(self.course["parts"][d["part"]]) if self.course else 1
        self.put("replay", screens.replay_view(
            d["part"], d["number"], total, name, title="Example",
            hints=screens.EXAMPLE_HINTS, legend=False))
        shown = self.column_hidden
        if shown:
            self.column_hidden = False
            self.toggle_column(apply_only=True)
        self.inputs_now(extra=1 << self.port)
        self.w.ui("class banner on 0")
        self.banner = 0
        self.w.ui("class replay on 1")
        self.w.ui("text rmode HOW TO DO IT · HALF SPEED")
        kept = self.keep_session(session)
        seek = None
        try:
            while True:
                state = dict(paused=False, quiet=False, seen=set())
                try:
                    end = self.tutorial_example_run(
                        drill, session, inputs, nums, at, pressed_on, n,
                        lead, seek, state)
                except self.Seek as back:
                    seek = max(lead + 1, back.to)
                    continue
                finally:
                    if state["quiet"]:
                        self.w.quiet(False)
                    self.restore_session(session, kept)
                    self.w.scripted(self.port, False)
                    session.live = True
                seek = None
                if end == "back":
                    return
        finally:
            self.w.ui("class replay on 0")
            self.inputs_now()
            if shown:
                self.column_hidden = True
                self.toggle_column(apply_only=True)
            self.w.pad(self.port)
            self.example_now = None

    def tutorial_example_run(self, drill, session, inputs, nums, at,
                             pressed_on, n, lead, seek, state):
        """One pass of the example: "back" (B), or "again" (A at its end)."""
        from melee_drills.drill import inputs_to_refs
        labels = [str(i) for i in range(1, n + 1)]

        def caption(f):
            said = [at[k] for k in sorted(at) if k <= f]
            if f < 1:
                return "Standing. The example starts in %d frame%s." % (
                    1 - f, "" if 1 - f == 1 else "s")
            return said[-1] if said else ""

        def show(f, pad):
            self.example_now = dict(frame=f, of=n, paused=state["paused"],
                                    caption=caption(f))
            self.w.ui("text rf F%d" % max(f, 0))
            self.w.ui("text rof " + ("OF %d" % n if f <= n else "AFTER"))
            self.w.ui("text rpad " + screens.esc(coach.stick_words(pad)))
            self.put("rsay", '<div class="ry">%s</div>' % screens.esc(
                caption(f)))
            self.put("rscrub", screens.replay_scrub(n, f, pressed_on, set(),
                                                    labels))

        def hide(on):
            # (drawn unseen, quiet 2: a run played again undrawn is not
            # quite the same run)
            if on != state["quiet"]:
                self.w.quiet(2 if on else 0)
                state["quiet"] = on

        def keys(frame):
            if self.person is not None:
                self.person(self.w, -7)            # tests: the player
            pressed, moves = self.read()
            if self.game_quit():
                raise Leave()
            if pressed & B:
                raise Leave("example-back")
            if pressed & A:
                state["paused"] = not state["paused"]
                if self.example_now is not None:
                    self.example_now["paused"] = state["paused"]
            if moves & LEFT:
                raise self.Seek(frame - 1)
            return bool(moves & RIGHT and state["paused"])

        def wait(frames, frame):
            if frames <= 0 and not state["paused"]:
                keys(frame)
                return
            self.w.freeze(True)
            try:
                while frames > 0:
                    frames -= 1
                    self.w.step()
                    if keys(frame):
                        return
                    if state["paused"]:
                        frames = max(frames, 1)
            finally:
                self.w.freeze(False)

        def each(game, frame):
            # the picture now is the frame before this one, played
            f = frame - lead - 1
            if seek is not None and frame < seek:
                hide(True)
                return
            if state["quiet"]:
                hide(False)
                state["paused"] = True
            if f < -12:
                return
            if f in at and f not in state["seen"]:
                state["seen"].add(f)
                state["paused"] = True          # read its caption
            show(f, session.player_pad)
            wait((1 if 1 <= f <= n else 0) if not state["paused"] else 1,
                 frame)

        self.w.scripted(self.port, True)
        session.live = False
        drill.build_reference = lambda c: inputs_to_refs(inputs, nums)
        try:
            res = session.run(each_frame=each, demo=True)
            # the rest of the example after the drill's judgement (the hop
            # to its top): the frames go on, still shown and stepped, from
            # the one the judgement stopped before playing
            frame = res["frames"]
            session.set_player_pad()
            while frame - lead - 1 <= n + 30:
                each(self.w, frame)
                self.w.step()
                frame += 1
            state["paused"] = True
            self.example_now = dict(self.example_now or {}, paused=True,
                                    end=True)
            self.put("rsay", '<div class="ry">%s</div><div class="rt">%s'
                     '</div>' % (screens.esc(caption(n)), screens.esc(
                         "The end of the example. A: again. B: go on.")))
            while True:
                if self.person is not None:
                    self.person(self.w, -7)
                self.w.step()
                pressed, _ = self.read()
                if self.game_quit():
                    raise Leave()
                if pressed & B:
                    return "back"
                if pressed & A:
                    return "again"
        except Leave as left:
            if left.to == "example-back":
                return "back"
            raise
        finally:
            del drill.build_reference

    # ---- the coach ---------------------------------------------------------------

    def keep_session(self, session):
        """What a run the player does not play (the target, a replay)
        would change in a session: put back by restore_session."""
        import copy
        d = session.d
        try:
            drill = copy.deepcopy(vars(d))
        except Exception:           # something in it cannot be copied
            drill = dict(vars(d))
        return dict(drill=drill, rng=session.rng.getstate(),
                    common=dict(session.common), opts=list(session.opts),
                    keep={k: getattr(session, k, None) for k in (
                        "attempts", "last_success", "flowing", "demo_count",
                        "_forced", "live_pad", "prev_buttons",
                        "player_pad")})

    def restore_session(self, session, kept):
        vars(session.d).clear()
        vars(session.d).update(kept["drill"])
        session.rng.setstate(kept["rng"])
        session.common.clear()
        session.common.update(kept["common"])
        session.opts[:] = kept["opts"]
        for k, v in kept["keep"].items():
            setattr(session, k, v)
        session.flowing = False     # the next try starts from its place

    def has_demo(self, drill):
        return bool(drill.reference) or type(drill).build_reference is not \
            course_engine.Drill.build_reference

    def coach_target(self, drill, session, result):
        """The drill's demonstration from the try's situation, unseen and
        unheard: (its result, its track), or (None, None). Its second pass,
        the one that counts, is drawn into ring 1 of the game's pictures
        (and a moment after it ends)."""
        if not self.has_demo(drill):
            return None, None
        track = coach.Track(ring=1)
        st = dict(drawn=False)

        def each(game, frame):
            if session.demo_pass == 2 and frame >= 0:
                if not st["drawn"] and self.pictures:
                    self.w.quiet(2)         # drawn now, still unseen
                    st["drawn"] = self.pictures_rec(1)
                track.add(session.c, session.player_pad, frame,
                          self.w.frame)
        kept = self.keep_session(session)
        self.w.scripted(self.port, True)
        session.live = False
        self.w.quiet(True)
        try:
            out = session.run(each_frame=each, demo=True,
                              scenario=result["scenario_index"])
            if st["drawn"]:
                session.set_player_pad()
                self.w.step(coach.AFTER)    # how it ended
        except Exception:
            return None, None
        finally:
            self.pictures_rec(-1)
            self.w.quiet(False)
            self.w.scripted(self.port, False)
            session.live = True
            self.restore_session(session, kept)
        return out, track

    def coach_seq(self, result, track, after=0, longest=150):
        """The pictures a panel plays (Play): [{"pic": the game's picture,
        "f": the timeline's frame or None, "label", "tag": a press starting,
        "slow": in the timeline}], from a little before the timeline to
        `after` frames after the try (kept in the ring after its record
        ends: the moments the game went on)."""
        if track is None or not len(track) or not self.pictures:
            return []
        tl = result.get("timeline") or {}
        lo, hi = coach.span(result, track, longest)
        start = tl.get("start")
        n = tl.get("frames", 0)
        if start is not None and lo == max(0, start - coach.LEAD):
            # the same lead before the timeline in every panel, so that
            # the try and the target show the same frame side by side (a
            # run kept from closer to its start holds its first picture)
            lo = start - coach.LEAD
        marks = coach.marks(result)
        try:
            have = self.w.frames_range(track.ring)
        except NativeError:
            have = None
        seq, last = [], None
        for i in range(lo, hi + after + 1):
            if i < 0:
                pic = None
            elif i < len(track):
                pic = track.pictures[i]
            elif last is not None:
                pic = last + 1
            else:
                break
            if pic is not None and have is not None and \
                    not have[0] <= pic <= have[1]:
                if pic > have[1]:
                    break                   # not drawn after all
                pic = None
            if pic is not None:
                last = pic
            f = i - start + 1 if start is not None else None
            within = f is not None and 1 <= f <= n
            if f is not None and f >= 1:
                label = coach.frame_label(tl, f) or ""
            elif start is None:
                label = "F%d" % (i - lo + 1)
            else:
                label = ""
            pad = track.pads[i] if 0 <= i < len(track) else None
            seq.append(dict(pic=pic, f=f if within else None, label=label,
                            tag=marks.get(i), slow=within, pad=pad))
        # a picture missing at the start (the frame before the ring began):
        # the first there is
        first = next((e["pic"] for e in seq if e["pic"] is not None), None)
        for e in seq:
            if e["pic"] is not None:
                break
            e["pic"] = first
        return seq if first is not None else []

    def pic_panel(self, view, ring, seq, mask=15, tall=False):
        """A panel of the game's pictures (screens._picture): each already
        the part of the game's picture where the fighters were (frames.c
        follows them), shown whole at the panel's shape from its middle;
        `tall` with no timeline below it."""
        if not seq:
            return None
        return dict(view=view, tall=tall, crop=coach.crop(
            [], (coach.PATH_W, coach.TALL_H if tall else coach.PATH_H)))

    def coach_view(self, result, track, target, target_track, fix_lines=(),
                   target_words=None, mask=15):
        """What the card shows (screens.coach_card): the game's own
        pictures of the try and the target when it keeps them (Play), the
        paths otherwise."""
        lo, hi = coach.span(result, track)
        pts = coach.points(track, lo, hi)
        if target_track is not None:
            tlo, thi = coach.span(target, target_track)
            tpts = coach.points(target_track, tlo, thi)
        else:
            tpts = []
        both = pts + tpts
        mine = coach.picture(track, lo, hi, coach.marks(result), "you", both)
        theirs = coach.picture(target_track, tlo, thi, coach.marks(target),
                               "tgt", both) if target_track is not None \
            else None
        d = self.drill_now or {"name": ""}
        you_seq = self.coach_seq(result, track, coach.AFTER)
        tgt_seq = self.coach_seq(target, target_track, coach.AFTER) \
            if target_track is not None else []
        if target_words is None:
            target_words = coach.target_words(result.get("timeline"))
        # without a timeline below them the pictures take its room
        tall = not result.get("timeline")
        return dict(
            headline=coach.headline(result), drill=d["name"],
            misses=self.settings.get("coach", 3), you=mine,
            you_words=result.get("full_words", result["words"]).replace(
                "\n", "; "),
            target=theirs, target_words=target_words,
            timeline=result.get("timeline"),
            wrong=coach.first_wrong(result.get("timeline")),
            fix=coach.fix(result, fix_lines),
            you_pic=self.pic_panel(0, 0, you_seq, mask, tall),
            target_pic=self.pic_panel(1, 1, tgt_seq, mask, tall),
            anim=[dict(id="y", view=0, ring=0, seq=you_seq),
                  dict(id="t", view=1, ring=1, seq=tgt_seq)],
            replay=True)

    COACH_WAIT = 30         # frames of the verdict before the card

    def coach_wait(self):
        """A moment for the verdict (the game goes on, and its pictures
        are kept: how the try ended); then what the game is now is saved
        (COACH_NOW), to come back to when the card closes."""
        for _ in range(self.COACH_WAIT):
            self.drill_frame(self.w, -1)
            self.w.step()
        self.pictures_rec(-1)
        try:
            self.w.save(self.COACH_NOW)
            return True
        except NativeError:
            return False

    def coach_back(self, saved):
        """The game as it was when the card opened, and its pictures kept
        again."""
        if saved:
            try:
                self.w.load(self.COACH_NOW)
            except NativeError:
                pass
        self.pictures_rec(0)

    def coach(self, drill, session, result, flowed=False):
        """The coach's card, after misses in a row: what was off, the try
        against the drill's demonstration, the inputs frame by frame, how
        to change them. A or B goes on; Y replays the try (replay)."""
        track = self.track
        saved = self.coach_wait()
        try:
            target, target_track = self.coach_target(drill, session, result)
            if target is not None and target.get("ui"):
                target, target_track = None, None
            if saved:
                self.w.load(self.COACH_NOW)
            view = self.coach_view(result, track, target or {}, target_track,
                                   drill.guide(session.c))
            view["replay"] = not flowed

            def replay():
                self.replay(drill, session, result, track, target,
                            target_track)
                if saved:
                    self.w.load(self.COACH_NOW)
            self.coach_card(view, replay)
        finally:
            self.coach_back(saved)

    def coach_card(self, view, replay):
        """The card, its pictures playing, until A or B (Y: `replay`, then
        the card again)."""
        self.coach_now = view           # tests: what the card says
        self.w.ui("class banner on 0")  # the card says it
        self.banner = 0
        self.coach_open = True
        self.w.freeze(True)
        try:
            while True:
                self.put("coach", screens.coach_card(view))
                play = Play(self.w, view.get("anim") or [])
                self.coach_play = play  # tests: where it is
                play.step()             # the first pictures, before it shows
                self.w.ui("class coach on 1")
                while True:
                    if self.person is not None:
                        self.person(self.w, -4)    # tests: the player
                    self.w.step()
                    play.step()
                    pressed, moves = self.read()
                    if self.game_quit():
                        raise Leave()
                    # frame by frame (the D-pad; the stick too), or on
                    if moves & LEFT:
                        play.frame(-1)
                    elif moves & RIGHT:
                        play.frame(1)
                    if pressed & UP:
                        play.toggle()
                    if pressed & (A | B):
                        self.sfx(self.SFX_BACK if pressed & B
                                 else self.SFX_FORWARD)
                        return
                    if pressed & Y and view["replay"]:
                        self.sfx(self.SFX_FORWARD)
                        break
                self.w.ui("class coach on 0")
                self.consume()
                self.w.freeze(False)
                try:
                    replay()
                finally:
                    self.w.freeze(True)
        finally:
            self.w.ui("class coach on 0")
            self.coach_open = False
            self.consume()
            self.w.freeze(False)
            for v in (0, 1):
                try:
                    self.w.frames_view(v)
                except NativeError:
                    pass

    class Seek(Exception):
        """Back a frame in the replay: played again, unseen, to there."""

        def __init__(self, to):
            Exception.__init__(self, to)
            self.to = to

    def replay(self, drill, session, result, track, target, target_track):
        """The try played again from its start, the timeline's frames at a
        quarter of the speed, with the player's controller shown: the
        D-pad steps a frame, A plays or pauses, Y switches to the drill's
        demonstration from the same start (the target) and back, B goes
        back to the coach (the canvas's "Coach: replay of your try")."""
        d = self.drill_now or {"part": "Tech", "number": 1, "name":
                               drill.name}
        total = len(self.course["parts"][d["part"]]) if self.course else 1
        self.put("replay", screens.replay_view(d["part"], d["number"], total,
                                               d["name"]))
        shown = self.column_hidden
        if shown:                   # the replay's column is the drill's
            self.column_hidden = False
            self.toggle_column(apply_only=True)
        self.inputs_now(extra=1 << self.port)
        self.w.ui("class banner on 0")
        self.banner = 0
        self.w.ui("class replay on 1")
        mode = "you"
        seek = None
        kept = self.keep_session(session)
        try:
            while True:
                if mode == "target" and target_track is None:
                    mode = "you"
                state = dict(paused=False, quiet=False)
                try:
                    end = self.replay_run(session, mode, result, track,
                                          target, seek, state)
                except self.Seek as back:
                    seek = max(0, back.to)
                    continue
                finally:
                    if state["quiet"]:
                        self.w.quiet(False)
                    self.restore_session(session, kept)
                seek = None
                if end == "back":
                    return
                if end == "mode":
                    mode = "target" if mode == "you" else "you"
        finally:
            self.w.ui("class replay on 0")
            self.inputs_now()
            if shown:
                self.column_hidden = True
                self.toggle_column(apply_only=True)
            self.w.pad(self.port)

    def replay_run(self, session, mode, result, track, target, seek, state):
        """One pass of the replay (replay): "back", "mode" (Y) or "again"
        (A at the end)."""
        res = result if mode == "you" else target
        tl = res.get("timeline") or {}
        start = tl.get("start")
        n = tl.get("frames", 0)
        if start is None:
            lo, hi = coach.span(res, track)
            start, n = lo, hi - lo + 1
        slow_from = max(0, start - coach.LEAD)
        you = {}
        for r in tl.get("rows", []):
            for f in r["you"]:
                if f - 1 not in r["you"]:   # where a press starts
                    you.setdefault(f, r["label"][:5])
        perfect = {f for r in tl.get("rows", []) for f in r["perfect"]}
        labels = tl.get("labels") or [str(i) for i in range(1, n + 1)]
        self.w.ui("text rmode " + ("YOUR TRY" if mode == "you"
                                   else "THE TARGET") + " · 1/4 SPEED")
        lines = ('<div class="ry">%s</div><div class="rt">%s</div>' % (
            screens.esc(result.get("full_words", result["words"]).replace(
                "\n", "; ")),
            screens.esc(coach.target_words(result.get("timeline")))))
        self.put("rsay", lines)

        def show(frame, pad):
            f = frame - start + 1
            self.replay_now = dict(mode=mode, frame=f, of=n,
                                   paused=state["paused"])
            self.w.ui("text rf F%d" % f)
            self.w.ui("text rof OF %d" % n)
            self.w.ui("text rpad " + screens.esc(coach.stick_words(pad)))
            self.put("rscrub", screens.replay_scrub(n, f, you, perfect,
                                                    labels))

        def hide(on):
            # unseen but drawn (quiet 2): what the game draws takes random
            # numbers (its effects), so a run played again undrawn is not
            # quite the run it was
            if on != state["quiet"]:
                self.w.quiet(2 if on else 0)
                state["quiet"] = on

        def keys(frame):
            """The player's buttons: True for a frame on (paused)."""
            if self.person is not None:
                self.person(self.w, -5)    # tests: the player
            pressed, moves = self.read()
            if self.game_quit():
                raise Leave()
            if pressed & B:
                raise Leave("replay-back")
            if pressed & Y:
                raise Leave("replay-mode")
            if pressed & A:
                state["paused"] = not state["paused"]
            if moves & LEFT:
                raise self.Seek(frame - 1)
            return bool(moves & RIGHT and state["paused"])

        def wait(frames, frame):
            """Frames with the game still (more while paused): the
            player's buttons read. None at the game's own speed: read,
            nothing held."""
            if frames <= 0 and not state["paused"]:
                keys(frame)
                return
            self.w.freeze(True)
            try:
                while frames > 0:
                    frames -= 1
                    self.w.step()
                    if keys(frame):
                        return          # a frame on
                    if state["paused"]:
                        frames = max(frames, 1)     # until a press
            finally:
                self.w.freeze(False)

        def each(game, frame):
            if mode == "target" and session.demo_pass != 2:
                hide(True)      # its first pass only finds its marks
                return
            if mode == "you":
                pad = track.pads[frame] if frame < len(track.pads) and \
                    track.pads[frame] is not None else None
                if pad is not None:
                    session.player_pad = dict(pad)
                    session._set_pad(self.port, session.player_pad)
            pad = session.player_pad
            if seek is not None and frame < seek:
                hide(True)      # back a frame: played again, unseen
                return
            if state["quiet"]:
                hide(False)
                if seek is not None:
                    state["paused"] = True
            if frame < slow_from:
                pressed, _ = self.read()
                if pressed & B:
                    raise Leave("replay-back")
                return
            show(frame, pad)
            # the timeline's frames at half the speed, the rest at the
            # game's (a quarter, all through, was "choppy": the owner)
            slow = start <= frame < start + n
            wait((1 if slow else 0) if not state["paused"] else 1, frame)

        self.w.scripted(self.port, True)
        session.live = False
        reset = session._reset
        if mode == "you" and track.pads and track.pads[0] is not None:
            # the pad held through the placement frame, as in the try (a
            # C-stick held down from one try to the next is not a flick)
            def placed(seed, scenario=None):
                reset(seed, scenario)
                session.player_pad = dict(track.pads[0])
                session._set_pad(self.port, session.player_pad)
            session._reset = placed
        try:
            self.replay_result = session.run(
                each_frame=each, demo=mode == "target",
                scenario=result["scenario_index"])
            if self.replay_now is not None:
                self.replay_now["paused"] = True
        except Leave as left:
            if left.to == "replay-back":
                return "back"
            if left.to == "replay-mode":
                return "mode"
            raise
        finally:
            session._reset = reset
            self.w.scripted(self.port, False)
            session.live = True
        # the end: still, until the player says
        state["paused"] = True
        try:
            wait(1, start + n)
        except Leave as left:
            if left.to == "replay-back":
                return "back"
            if left.to == "replay-mode":
                return "mode"
            raise
        return "again"

    # ---- settings -----------------------------------------------------------

    SET_MOVES = {
        "scontrols": {RIGHT: "sonline"},
        "sonline": {LEFT: "scontrols", DOWN: "ssound"},
        "ssound": {LEFT: "scontrols", UP: "sonline", RIGHT: "sdisplay"},
        "sdisplay": {LEFT: "ssound", UP: "sonline"},
    }
    CTL_ROWS = ("delay", "rumble", "ucf", "layouts")

    def delay_words(self):
        d = self.settings["delay"]
        return "%d frame%s" % (d, "" if d == 1 else "s") if d else "Off"

    def rumble_words(self):
        on = self.settings["rumble"]
        if all(on):
            return "On"
        if not any(on):
            return "Off"
        return "Ports " + " ".join(str(i + 1) for i, x in enumerate(on) if x)

    def set_about(self, ident):
        item = next(i for i in screens.SETTINGS if i[0] == ident)
        return item[3] + ("" if item[4] else
                          " Not in the native client yet.")

    def show_settings(self):
        self.menu_music()
        self.screen = "settings"
        self.w.capture(True)
        self.sfocus = getattr(self, "sfocus", "scontrols")
        s = self.settings
        chips = [("INPUT DELAY", self.delay_words(), "neutral"),
                 ("RUMBLE", "On" if s["rumble"][self.port] else "Off",
                  "punish"),
                 ("UCF", "0.84" if s["ucf"] else "Off", "ink"),
                 ("BUTTONS", "The game's", "white")]
        self.load("settings", screens.settings_menu(self.sfocus, chips))
        self.w.ui("class %s focus 1" % self.sfocus)
        self.say(self.set_about(self.sfocus))

    def on_settings(self, pressed, moves):
        for d in (LEFT, RIGHT, DOWN, UP):
            to = self.SET_MOVES[self.sfocus].get(d) if moves & d else None
            if to:
                self.w.ui("class %s focus 0" % self.sfocus)
                self.sfocus = to
                self.w.ui("class %s focus 1" % to)
                self.say(self.set_about(to))
                break
        if pressed & B:
            self.show_main()
        elif pressed & A:
            if self.sfocus == "scontrols":
                self.show_controls()
            else:
                self.show_sub(self.sfocus)

    def controller_kind(self):
        """What the player's port reads, for the rumble cards: (what it
        is, whether it has a motor). The keyboard is not asked about the
        adapter, so that a test never opens one."""
        if self.source == "keyboard":
            return "KEYBOARD", False
        try:
            said = self.w.devices()
        except Exception:
            return "?", False
        others = said.split("Other controllers:")[-1].strip()
        has_other = others[:1].isdigit() and int(others.split(":")[0]) > 0
        if self.source.startswith("gcc") or (
                self.source == "auto" and "controllers on its ports" in said):
            return "GC ADAPTER", True
        if self.source.startswith("pad") or (self.source == "auto" and
                                             has_other):
            return "CONTROLLER", True
        return "KEYBOARD", False

    def controls_view(self):
        """The rows, and the panel, line and hints of the row in focus."""
        s = self.settings
        rows = [
            ("delay", "Input delay", "Frames every press is held back.",
             self.delay_words(), "#F5BE1B"),
            ("rumble", "Rumble", "Each port's motor, on or off.",
             self.rumble_words(), "#F0643C"),
            ("ucf", "UCF 0.84", "Universal Controller Fix, as on Slippi.",
             "On" if s["ucf"] else "Off", "#8A94A3"),
            ("layouts", "Button layouts", "One for each port and nickname.",
             "Not yet", "#1F49C9"),
        ]
        ident = self.CTL_ROWS[self.ctl_at]
        if ident == "delay":
            panel = screens.delay_panel(s["delay"], settings.DELAY_MAX)
            desc = ("How many frames late every press reaches the game. "
                    "Slippi plays online at 2.")
            hints = [("D-SIDE", "Frames"), ("B", "Back")]
        elif ident == "rumble":
            kind, motor = self.controller_kind()
            try:
                running = self.w.rumble()["running"]
            except Exception:
                running = [0, 0, 0, 0]
            ports = []
            for i in range(4):
                mine = i == self.port
                ports.append(dict(
                    name="Port %d" % (i + 1),
                    source=kind if mine else "NOT PLAYED HERE",
                    on=s["rumble"][i], motor=motor if mine else True,
                    running=bool(running[i]) or (
                        self.frames < getattr(self, "felt_until", 0) and
                        i == getattr(self, "felt", -1) and
                        (motor or not mine))))
            if self.rport == self.port and not motor:
                feel = "The keyboard has no motor to feel."
            else:
                feel = "Port %d rumbles for half a second." % (self.rport + 1)
            panel = screens.rumble_panel(ports, self.rport, feel)
            desc = ("Rumble as the game does it: hits taken and landed, "
                    "port by port.")
            hints = [("D-SIDE", "Port"), ("A", "On / off"), ("X", "Feel it"),
                     ("B", "Back")]
        elif ident == "ucf":
            panel = screens.toggle_panel(
                "UCF 0.84", "Every port, every match",
                "On" if s["ucf"] else "Off", s["ucf"], [
                    "The Universal Controller Fix: dash back and shield "
                    "drop work alike on every controller, as on Slippi, "
                    "where it is always on.",
                    "Online it is on whatever is chosen here: both games "
                    "have to play the same game."])
            desc = "Universal Controller Fix 0.84, as Slippi plays it."
            hints = [("D-SIDE", "On / off"), ("B", "Back")]
        else:
            panel = screens.note_panel(
                "Button layouts", "Not in the native client yet", [
                    "A layout for each port, and one a nickname brings "
                    "with it: which button jumps, which grabs, what the "
                    "D-pad does. The overlay build has them; the native "
                    "client gets them next.",
                    "Until then every port plays the game's own buttons."])
            desc = "Button layouts for each port and nickname: next."
            hints = [("B", "Back")]
        return rows, panel, desc, hints

    def draw_controls(self):
        rows, panel, desc, hints = self.controls_view()
        self.load("controls", screens.controls_page(
            rows, self.ctl_at, panel, desc, hints))

    def show_controls(self):
        self.screen = "controls"
        self.w.capture(True)
        self.ctl_at = getattr(self, "ctl_at", 0)
        self.rport = getattr(self, "rport", self.port)
        self.felt_until = 0
        self.draw_controls()

    def on_controls(self, pressed, moves):
        s = self.settings
        ident = self.CTL_ROWS[self.ctl_at]
        if pressed & B:
            self.progress.save()
            self.show_settings()
            return
        if moves & (UP | DOWN):
            self.ctl_at = (self.ctl_at + (1 if moves & DOWN else -1)) % len(
                self.CTL_ROWS)
            self.draw_controls()
            return
        step = 1 if moves & RIGHT else -1 if moves & LEFT else 0
        changed = redraw = False
        if ident == "delay" and step:
            n = max(0, min(settings.DELAY_MAX, s["delay"] + step))
            changed = n != s["delay"]
            s["delay"] = n
        elif ident == "rumble":
            if step:
                self.rport = (self.rport + step) % 4
                redraw = True
            if pressed & A:
                s["rumble"][self.rport] = not s["rumble"][self.rport]
                changed = True
            if pressed & X:
                try:
                    self.w.rumble_test(self.rport, 30)
                except Exception:
                    pass
                self.felt, self.felt_until = self.rport, self.frames + 30
                redraw = True
        elif ident == "ucf" and (step or pressed & A):
            s["ucf"] = not s["ucf"]
            changed = True
        if changed:
            settings.apply(self.w, s)
            self.progress.save()
            self.sfx(self.SFX_MOVE)
        if self.felt_until and self.frames == self.felt_until:
            redraw = True               # the pulse is over
        if changed or redraw:
            self.draw_controls()

    # Sound, Display and Online: rows on the left, the one in focus beside
    # them, as Controls
    SUB = {"ssound": ("Sound", "#F0643C", ("music", "effects", "menus")),
           "sdisplay": ("Display", "#F5BE1B",
                        ("window", "size", "sidebar", "inputs", "coach")),
           "sonline": ("Online", "#22B8A0",
                       ("nick", "port", "friends", "router"))}

    def volumes_now(self):
        """The volumes the game is given: the menus' sounds on menus, the
        game's in matches and drills."""
        s = self.settings
        try:
            self.w.volume(s["music"], s["effects"] if self.has_cover
                          else s["menus"])
        except Exception:
            pass

    def fullscreen_now(self):
        try:
            where = self.w.where()
            return bool(where.get("asked", where.get("fullscreen")))
        except Exception:
            return False

    def sub_view(self):
        s = self.settings
        name, colour, idents = self.SUB[self.sub]
        ident = idents[self.sub_at]
        if self.sub == "ssound":
            levels = [("Music", "Menus and stages", s["music"], "#F0643C"),
                      ("Effects", "Matches and drills", s["effects"],
                       "#22B8A0"),
                      ("Menus", "Moving and choosing", s["menus"],
                       "#1F49C9")]
            rows = [("music", "Music", "The game's music: menus, stages.",
                     "%d" % s["music"], "#F0643C"),
                    ("effects", "Effects", "Hits, jumps, voices in a match.",
                     "%d" % s["effects"], "#22B8A0"),
                    ("menus", "Menu sounds", "Moving and choosing here.",
                     "%d" % s["menus"], "#1F49C9")]
            try:
                song = self.w.song()
            except Exception:
                song = None
            song = ("The main menu's theme" if song == native.MENU_SONG else
                    song.rsplit(".", 1)[0] if song else "Nothing")
            panel = screens.sound_panel(levels, self.sub_at, song)
            desc = "Volumes are yours alone: the game is the same at any."
            hints = [("D-SIDE", "Volume"), ("B", "Back")]
        elif self.sub == "sdisplay":
            full = self.fullscreen_now()
            rows = [("window", "Window", "Fullscreen fills the screen.",
                     "Fullscreen" if full else "Window", "#F5BE1B"),
                    ("size", "Window size", "When it is not fullscreen.",
                     "%d x %d" % tuple(s["size"]), "#F5BE1B"),
                    ("sidebar", "Sidebar", "Beside the game in a match.",
                     "Shown" if s["sidebar"] else "Hidden", "#F5BE1B"),
                    ("inputs", "Input display", "Buttons and sticks, drawn.",
                     s["inputs"].title(), "#F5BE1B"),
                    ("coach", "Coach", "Its card, after misses in a row.",
                     "After %d misses" % s["coach"] if s["coach"] else "Off",
                     "#F5BE1B")]
            panel = screens.display_panel(s["sidebar"], full, s["size"])
            desc = ("TM-CE's input display: whose buttons and sticks are "
                    "drawn over the game in drills and matches."
                    if ident == "inputs" else
                    "The coach's card opens in a drill after this many "
                    "misses in a row." if ident == "coach" else
                    "The sidebar can also be hidden in a match: hold "
                    "START for three seconds.")
            hints = [("D-SIDE", "Change"), ("B", "Back")]
        else:
            fr = online.friends(self.progress.data)
            self.fr_at = min(getattr(self, "fr_at", 0), max(0, len(fr) - 1))
            router = getattr(self, "router", None)
            rows = [("nick", "Nickname", "What your friends see.",
                     self.nickname(), "#22B8A0"),
                    ("port", "Your code's port", "UDP, on this machine.",
                     "%d" % self.online_port(), "#22B8A0"),
                    ("friends", "Friends", "Met online, to play again.",
                     "%d" % len(fr), "#22B8A0"),
                    ("router", "Router", "Can friends reach you directly?",
                     router[0] if router else "Not checked", "#22B8A0")]
            panel = screens.online_panel(
                ident, self.nickname(), self.online_port(),
                [(f["name"], "an address" if ":" in f["code"] else "a code")
                 for f in fr], self.fr_at, router)
            desc, hints = {
                "nick": ("Copy a name, then X pastes it as your nickname.",
                         [("X", "Paste"), ("B", "Back")]),
                "port": ("The UDP port your code points at.",
                         [("D-SIDE", "Port"), ("B", "Back")]),
                "friends": ("Friends you met online.",
                            [("D-SIDE", "Friend"), ("Y", "Forget"),
                             ("B", "Back")]),
                "router": ("Asks two STUN servers how your router answers.",
                           [("A", "Check"), ("B", "Back")]),
            }[ident]
        return name, colour, rows, panel, desc, hints

    def draw_sub(self):
        name, colour, rows, panel, desc, hints = self.sub_view()
        self.load("sub", screens.settings_page(
            name, colour, rows, self.sub_at, panel, desc, hints))

    def show_sub(self, which):
        self.screen = "sub"
        self.w.capture(True)
        if getattr(self, "sub", None) != which:
            self.sub_at = 0
        self.sub = which
        self.draw_sub()

    def on_sub(self, pressed, moves):
        s = self.settings
        idents = self.SUB[self.sub][2]
        ident = idents[self.sub_at]
        if pressed & B:
            self.progress.save()
            self.show_settings()
            return
        if moves & (UP | DOWN):
            self.sub_at = (self.sub_at + (1 if moves & DOWN else -1)) % len(
                idents)
            self.draw_sub()
            return
        step = 1 if moves & RIGHT else -1 if moves & LEFT else 0
        changed = False
        if self.sub == "ssound" and step:
            n = max(0, min(100, s[ident] + 10 * step))
            changed = n != s[ident]
            s[ident] = n
            if changed:
                self.volumes_now()
        elif self.sub == "sdisplay" and (step or pressed & A):
            if ident == "window":
                try:
                    self.w.fullscreen(not self.fullscreen_now())
                except Exception:
                    pass
                changed = True
            elif ident == "size":
                sizes = [list(x) for x in settings.SIZES]
                i = sizes.index(list(s["size"]))
                s["size"] = sizes[(i + (step or 1)) % len(sizes)]
                try:
                    self.w.resize(*s["size"])
                except Exception:
                    pass
                changed = True
            elif ident == "sidebar":
                s["sidebar"] = not s["sidebar"]
                self.column_hidden = not s["sidebar"]
                changed = True
            elif ident == "inputs":
                i = settings.INPUTS.index(s["inputs"])
                s["inputs"] = settings.INPUTS[(i + (step or 1)) %
                                              len(settings.INPUTS)]
                changed = True
            else:
                i = settings.COACH.index(s["coach"])
                s["coach"] = settings.COACH[(i + (step or 1)) %
                                            len(settings.COACH)]
                changed = True
        elif self.sub == "sonline":
            if ident == "nick" and pressed & X:
                text = (self.read_clipboard() or "").strip()
                text = "".join(ch for ch in text.splitlines()[0]
                               if ch.isprintable())[:12] if text else ""
                if text:
                    self.progress.data["nickname"] = text
                    changed = True
            elif ident == "port" and step:
                self.progress.data["online_port"] = max(
                    1024, min(65535, self.online_port() + step))
                changed = True
            elif ident == "friends":
                fr = online.friends(self.progress.data)
                if step and fr:
                    self.fr_at = (self.fr_at + step) % len(fr)
                    self.draw_sub()
                if pressed & Y and fr:
                    del fr[self.fr_at]
                    self.progress.data["friends"] = fr
                    changed = True
            elif ident == "router" and pressed & A:
                if os.environ.get("MELEE_ONLINE_NO_STUN") is not None:
                    self.router = ("Not checked", "Checking is switched "
                                   "off here (MELEE_ONLINE_NO_STUN).")
                else:
                    self.router = ("Checking", "Asking the STUN servers...")
                    self.draw_sub()
                    self.w.step()
                    try:
                        self.router = online.router_check(self.online_port())
                    except Exception as e:
                        self.router = ("No answer", "%s. Is this machine "
                                       "online?" % str(e)[:80])
                self.draw_sub()
        if changed:
            self.progress.save()
            self.sfx(self.SFX_MOVE)
            self.draw_sub()

    def run(self, frames=0):
        while not frames or self.frames < frames:
            self.frame()


CRASH_LOG = ROOT / "build" / "client-crash.log"


def crash_log(game):
    """The exception being handled and the game's last lines, appended to
    build/client-crash.log."""
    import traceback
    try:
        CRASH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(CRASH_LOG, "a") as f:
            f.write("---- %s\n%s" % (time.strftime("%Y-%m-%d %H:%M:%S"),
                                    traceback.format_exc()))
            if game is not None:
                f.write("the game's last lines:\n%s\n" % "\n".join(
                    line.rstrip() for line in game.log[-20:]))
        print("what happened is in %s" % CRASH_LOG, file=sys.stderr)
    except Exception:
        pass


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
            crash_log(w)
            return 1
    except Exception:
        # what ended the client, kept: it is printed in a terminal nobody
        # may be reading (the owner reported crashes nothing had kept)
        crash_log(w)
        raise
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
