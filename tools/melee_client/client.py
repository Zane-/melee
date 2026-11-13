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
import random
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
import opponents  # noqa: E402
import fonts  # noqa: E402
import screens  # noqa: E402
import window  # noqa: E402
from native import STAGES, NativeError  # noqa: E402
from melee_actor import scenario as scn  # noqa: E402
from melee_actor import tech  # noqa: E402
from melee_actor import train  # noqa: E402

A, B, X, Y, START = 0x100, 0x200, 0x400, 0x800, 0x1000
L, R = 0x40, 0x20
LEFT, RIGHT, DOWN, UP = 1, 2, 4, 8
OUT = ROOT / "build" / "ui"
COLUMNS = 7
STAGE_ORDER = ("final-destination", "battlefield", "yoshis-story",
               "dream-land", "fountain-of-dreams", "pokemon-stadium")
assert set(STAGE_ORDER) == set(STAGES)
CPU, NOBODY = "the game's own CPU", "nobody"

# Which panel a direction leads to from each panel of the main menu.
MAIN_MOVES = {
    "train": {RIGHT: "lab"},
    "lab": {LEFT: "train", DOWN: "events"},
    "events": {LEFT: "train", UP: "lab", RIGHT: "versus"},
    "versus": {LEFT: "events", UP: "lab", DOWN: "controls"},
    "controls": {LEFT: "events", UP: "versus"},
}


class Leave(Exception):
    """The player asked to leave what is running."""


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
        self.held = {}                # direction -> frames held
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

    def put(self, ident, rml):
        """Replace an element's content (through a file: a list of rows is
        longer than a control line)."""
        path = self.out / ("part-%s.rml" % ident)
        path.write_text(rml)
        self.w.ui("file %s %s" % (ident, path))

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
            if self.focus in ("train", "versus", "lab"):
                self.mode = self.focus
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
        self.damage = 0
        self.load("versus", screens.versus_rail(
            self.me, opp, name, what, stage.replace("-", " ").title(),
            self.mode == "lab"))
        self.w.capture(False)

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
        if self.start_held >= 40:
            if self.bot is not None:
                self.bot.close()
                self.bot = None
            self.w.pad(other)
            self.show_opponent()

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
        """Before every frame of a drill: the way out, and (in tests) the
        stand-in for the player."""
        self.read()
        if self.start_held >= 40:
            raise Leave()
        if self.banner > 0:
            self.banner -= 1
            if self.banner == 0:
                self.w.ui("class banner on 0")
        if self.person is not None:
            self.person(game, frame)

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
                ("why", screens.esc(words) if "timeline" in result
                 else "")):
            self.w.ui("text %s %s" % (ident, text))
        self.put("checks", screens.check_rows(result["checks"]))
        self.put("last", screens.last_squares(results))
        self.put("tl", screens.timeline(result.get("timeline")))
        self.w.ui("class banner on 1")
        self.banner = 100

    def drill(self, d):
        """Run a drill until the player leaves it: the scenario's opponent
        against them, a verdict for each attempt."""
        sc = scn.load(str(self.here[d["id"]]))
        self.say("Loading %s." % d["name"])
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
        # The A that started the drill is still down, and A in shield is
        # a grab: wait for the buttons to be let go before the first try.
        for _ in range(90):
            self.w.step()
            if not self.w.pads()[self.port]["buttons"] & (A | B | X | Y):
                break
        self.screen = "drill"
        self.start_held = 0
        self.load("drill", screens.drill_rail(
            self.c, d, self.course, sc.get("about", d["goal"])))
        self.w.capture(False)
        results = []
        first = random.randrange(1 << 20)
        try:
            while True:
                result = session.run(jitter=3.0, run=first + len(results),
                                     each_frame=self.drill_frame)
                if result.get("skip"):
                    # not an attempt (an aerial with no lag to cancel):
                    # say why, count nothing
                    self.w.ui("text bword Not counted")
                    self.w.ui("text bmsg " + screens.esc(
                        result["words"].split(":")[0]))
                    self.w.ui("class banner on 1")
                    self.banner = 100
                    continue
                results.append(bool(result["success"]))
                self.show_result(result, results)
                # Against an opponent the situation is put back, so the
                # verdict gets a moment first; a tech drill has nothing to
                # put back and the player sets the pace.
                for _ in range(0 if sc.get("tech") else 75):
                    self.drill_frame(self.w, -1)
                    self.w.step()
        except Leave:
            pass
        self.progress.record(d["id"], self.c["id"], results)
        self.results = results
        self.show_list()

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
        self.load("match", screens.match_rail(
            c, self.opponent.replace("-", " ").title(),
            self.stage.replace("-", " ").title()))
        self.w.capture(False)

    def on_match(self, pressed, moves):
        if self.start_held >= 40:
            if self.back == "hub":
                self.show_hub()
            else:
                self.show_characters()

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
                print("%d seconds measured, %d pictures shown late"
                      % (sum(" of 60 late" in r for r in rows), late))
                print("\n".join(rows[-6:]))
            w.close()
        left = window.leftovers()
        if left:
            print("still running: %s" % left, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
