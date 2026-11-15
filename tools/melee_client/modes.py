"""Versus's game modes: what a match is played for (the owner, 2026-11-14:
"We need to add support for different game modes instead of just the
unlimited score game. Let's make our first mode Tennis ... Make sure we
have a good game mode selector so we can build up more and more custom
game modes").

Every match is the game's endless time match (src/host/match.c); a mode
keeps its own score from the KOs the client sees (a fighter entering one of
the game's dead states, DEAD), shows it in the game's own HUD as stocks
(`stocks P N`: the stock row's icons, one breaking as it falls; in the
endless match they end nothing), and says when the match is won.

A mode is a class here with its place in MODES: the selector (Versus >
Local > Choose a mode) lists them in that order, so a new mode is a new
class and a line in MODES. Its settings are Options; a mode with any has
them set on the options screen after it is chosen (then the characters,
the opponent, the stage), and the client keeps them.

The format, what each part means and how to add a mode:
docs/ai/game-modes.md, the skill add-game-mode. check() holds every mode
to it:

    python tools/melee_client/modes.py          # every mode, checked
"""
import random
import re
import sys

# the game's dead states (ftCommon's Dead*: down, left, right, up, the
# star and the screen KOs): entering one is a KO
DEAD = range(0, 11)


class Option:
    """One of a mode's settings (the owner, 2026-11-14: "make sure that each
    game mode has support for settings (i.e. win by 3, etc. on tug of war)
    within the mode selection"): `key` in the mode's settings, `name` and
    `about` as the options screen shows them, the `values` it steps
    through, its `default`; `unit` (one, many) after its number."""

    def __init__(self, key, name, about, values, default, unit=("", "")):
        self.key, self.name, self.about = key, name, about
        self.values, self.default, self.unit = tuple(values), default, unit

    def words(self, value):
        """The value and its unit ("3 stocks")."""
        return "%s %s" % (value, self.unit[0] if value == 1
                          else self.unit[1])

    def step(self, value, by):
        """The value `by` places along (it stops at either end)."""
        i = self.values.index(value) if value in self.values else \
            self.values.index(self.default)
        return self.values[max(0, min(len(self.values) - 1, i + by))]


class Mode:
    """A game mode. `ident` names it in settings and tests; `name`,
    `tagline` and `rules` are what the selector shows (line() and
    rules_text(), which may say the settings); `icon` is one of the
    client's line icons (icons.py), on its panel in `colour` (`ink` the
    colour on it); `options` its settings (Option), chosen on the options
    screen after the mode, kept in `settings`."""
    ident = ""
    name = ""
    tagline = ""
    rules = ()
    icon = "play"
    colour, ink = "#3A4250", "#F3F6FA"
    options = ()

    def __init__(self, **settings):
        self.settings = {}
        for o in self.options:
            v = settings.get(o.key, o.default)
            self.settings[o.key] = v if v in o.values else o.default
        self.start()

    def line(self):
        """The line about the mode, as set."""
        return self.tagline

    def rules_text(self):
        return self.rules

    def summary(self):
        """The settings in a few words (the column: "win by 3"), or ""."""
        return ""

    def start(self):
        """A new match: the score back to nothing."""
        self.winner = None

    def ko(self, port):
        """Player `port` (0 or 1) was KO'd (a fall or a self-destruct
        alike)."""

    def stocks(self):
        """(port 0's, port 1's) stocks to show: the score in the HUD."""
        return (0, 0)

    def status(self, names):
        """The score in words, for the column ("Even"); `names`: the two
        sides' names."""
        return ""

    def scores(self):
        """Whether the mode shows a score at all (the HUD's stock row)."""
        return False


class Unlimited(Mode):
    """The match as it has been: no score, no end."""
    ident = "unlimited"
    name = "Unlimited"
    tagline = "Play as long as you like. No score, no end."
    rules = ("KOs are not counted.",
             "Leave from the pause menu when you are done.")
    icon = "infinity"


class TugOfWar(Mode):
    """A tug of war (the owner: "scoring works like tug of war. A kill pulls
    it in your favor, and you have to win by +2 ... This will train trading
    even stocks and pushing advantages"; first called Tennis, renamed "Tug
    of War"): the score is one number, port 0's lead; a KO moves it a point
    toward the side that took it; `lead` ahead wins (2 by default: a
    setting). Shown as stocks ("at the start nothing shows up, then as a
    player takes a stock, it either removes the opponent's stock or adds one
    to theirs"): the side ahead has its lead in stock icons, the other
    none."""
    ident = "tug-of-war"
    name = "Tug of War"
    tagline = "Start even. Win by a lead of stocks."
    icon = "tug"
    colour, ink = "#E2B563", "#12161C"
    options = (Option("lead", "Win by",
                      "How far ahead the rope has to be pulled to win: by "
                      "two, an even trade is never far from the end.",
                      (2, 3, 4, 5), 2, ("stock", "stocks")),)

    def line(self):
        return "Start even. Win by %s." % self.options[0].words(
            self.settings["lead"])

    def rules_text(self):
        return ("A KO pulls the rope your way: it takes away the other "
                "side's stock, or adds one to yours.",
                "Pull it %d ahead to win. Even trades bring it back to "
                "even." % self.settings["lead"],
                "Trains trading stocks evenly and pushing an advantage.")

    def summary(self):
        return "Win by %d" % self.settings["lead"]

    def start(self):
        super().start()
        self.lead = 0           # port 0's lead (negative: port 1's)

    def ko(self, port):
        if self.winner is not None:
            return
        self.lead += -1 if port == 0 else 1
        if abs(self.lead) >= self.settings["lead"]:
            self.winner = 0 if self.lead > 0 else 1

    def stocks(self):
        return (max(self.lead, 0), max(-self.lead, 0))

    def status(self, names):
        if self.winner is not None:
            return "Game: %s" % names[self.winner]
        if self.lead == 0:
            return "Even"
        return "%s +%d" % (names[0 if self.lead > 0 else 1], abs(self.lead))

    def scores(self):
        return True


# the selector's list, in its order
MODES = [Unlimited, TugOfWar]
BY_ID = {m.ident: m for m in MODES}


class KOs:
    """KOs as the client sees them, frame by frame: a fighter entering a
    dead state from any other. `see(fighters)` with the state's two
    fighters returns the ports KO'd this frame."""

    def __init__(self):
        self.was = [None, None]

    def see(self, fighters):
        out = []
        for port in (0, 1):
            f = fighters[port] if port < len(fighters) else None
            state = f["state"] if f else None
            dead = state in DEAD
            if dead and self.was[port] is not None and \
                    self.was[port] not in DEAD:
                out.append(port)
            self.was[port] = state
        return out


# ---- the format, checked ------------------------------------------------------

HUD_MOST = 5            # the HUD's stock row shows up to 5 icons
IDENT = re.compile(r"^[a-z][a-z0-9-]*$")
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def check(cls, icons=None, tries=300, seed=1):
    """What is wrong with mode class `cls` by the format
    (docs/ai/game-modes.md), as sentences ([] if nothing): its words and
    looks, its options, and its score played through `tries` random runs
    of KOs with every setting. `icons`: the line icons there are (icons.py
    ICON), to check the mode's."""
    out = []
    for attr in ("ident", "name", "tagline", "icon"):
        if not isinstance(getattr(cls, attr, None), str) or \
                not getattr(cls, attr):
            out.append("%s has no %s" % (cls.__name__, attr))
    if cls.ident and not IDENT.match(cls.ident):
        out.append("%s's ident %r is not lower-case words joined by -"
                   % (cls.__name__, cls.ident))
    if icons is not None and cls.icon not in icons:
        out.append("%s's icon %r is not one of icons.py's" % (
            cls.__name__, cls.icon))
    for attr in ("colour", "ink"):
        if not HEX.match(getattr(cls, attr, "")):
            out.append("%s's %s is not #RRGGBB" % (cls.__name__, attr))
    keys = set()
    for o in cls.options:
        if not isinstance(o, Option):
            out.append("%s has an option that is not an Option" %
                       cls.__name__)
            continue
        if o.key in keys:
            out.append("%s has two options %r" % (cls.__name__, o.key))
        keys.add(o.key)
        if not o.values or o.default not in o.values:
            out.append("%s's option %r: its default is not one of its "
                       "values" % (cls.__name__, o.key))
        if not o.name or not o.about:
            out.append("%s's option %r has no name or no words" %
                       (cls.__name__, o.key))
    if out:
        return out
    rng = random.Random(seed)
    settings = [{}] + [{o.key: v} for o in cls.options for v in o.values]
    names = ["Fox", "Falco"]
    for kept in settings:
        m = cls(**kept)
        if set(m.settings) != keys:
            out.append("%s(%r) keeps settings %r" % (cls.__name__, kept,
                                                     m.settings))
            continue
        for _ in range(tries // len(settings) + 1):
            m.start()
            if m.winner is not None:
                out.append("%s(%r): won before a KO" % (cls.__name__,
                                                        kept))
                break
            if m.scores() and m.stocks() != (0, 0):
                out.append("%s(%r): stocks %r before a KO" % (
                    cls.__name__, kept, m.stocks()))
                break
            for _ in range(rng.randrange(1, 40)):
                before = m.winner
                m.ko(rng.randrange(2))
                a, b = m.stocks()
                if not (isinstance(a, int) and isinstance(b, int)) or \
                        a < 0 or b < 0 or a > 99 or b > 99:
                    out.append("%s(%r): stocks %r" % (cls.__name__, kept,
                                                      (a, b)))
                    break
                if m.scores() and max(a, b) > HUD_MOST and \
                        m.winner is None:
                    out.append("%s(%r): %d stocks in play, more than the "
                               "HUD's %d icons" % (cls.__name__, kept,
                                                   max(a, b), HUD_MOST))
                    break
                if m.winner not in (None, 0, 1):
                    out.append("%s(%r): winner %r" % (cls.__name__, kept,
                                                      m.winner))
                    break
                if before is not None and m.winner != before:
                    out.append("%s(%r): the winner changed after the "
                               "match was won" % (cls.__name__, kept))
                    break
                if not isinstance(m.status(names), str):
                    out.append("%s(%r): status is not words" %
                               (cls.__name__, kept))
                    break
                if m.winner is not None:
                    break
            if out:
                break
        if not isinstance(m.line(), str) or not m.line() or \
                not all(isinstance(r, str) for r in m.rules_text()):
            out.append("%s(%r): its line or rules are not words" %
                       (cls.__name__, kept))
    return out


def check_all(icons=None):
    """{ident: problems} for every mode in MODES, and the list's own
    (two modes with one ident)."""
    out = {}
    seen = set()
    for cls in MODES:
        problems = check(cls, icons)
        if cls.ident in seen:
            problems.append("two modes are %r" % cls.ident)
        seen.add(cls.ident)
        out[cls.ident or cls.__name__] = problems
    return out


if __name__ == "__main__":
    sys.path.insert(0, __import__("os").path.dirname(
        __import__("os").path.abspath(__file__)))
    import icons as _icons
    bad = 0
    for ident, problems in check_all(set(_icons.ICON)).items():
        print("%-12s %s" % (ident, "ok" if not problems else
                            "; ".join(problems)))
        bad += len(problems)
    sys.exit(1 if bad else 0)
