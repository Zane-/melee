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
        """The value and its unit ("3 stocks"); a value in words (no
        unit: "Off") as it is."""
        if not self.unit:
            return str(value)
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
    # what a mode may fix: the two characters (the player's, the
    # opponent's: the character select is skipped and the opponent screen
    # only says who plays it), the stage (the stage select is skipped)
    fighters = None
    stage = None
    # its own score display over the game (screens.BOARDS: "rope"), or
    # None: the HUD shows the score (a stock match's own stocks)
    board = None

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

    def stock_match(self):
        """The match's stocks each (a stock match: the game keeps them, the
        HUD shows them and the game ends it at the last), or 0: the endless
        time match."""
        return 0

    def end_rule(self):
        """How the game ends the match besides its stocks, decided in its
        own frame (src/host/rules.c): ("none", 0) or ("tug", lead)."""
        return ("none", 0)

    def moves(self):
        """The moves both sides may use (src/host/moves.c): "all",
        "shine" (the down special and no attack) or "recovery" (the down,
        up and side specials)."""
        return "all"

    def tick(self, fighters=()):
        """Each frame of the match, before any KO of the frame is told
        (the mode's own stats); `fighters`: the two fighters' states as
        the host gives them (a dict with "state", the motion state, and
        "percent"; None for a slot with nobody)."""

    def stats(self):
        """The mode's own rows on the results screen, above the ones every
        mode has (MatchStats): [(name, (port 0's, port 1's), better)],
        each value a number or words, `better` "more", "less" or None (which
        side's is marked)."""
        return []

    def result(self, names):
        """The line under the winner on the results screen."""
        return "%s wins" % names[self.winner] if self.winner is not None \
            else ""


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
    board = "rope"
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
        self.biggest = [0, 0]   # each side's biggest lead
        self.ahead = [0, 0]     # frames each side was ahead
        self.evened = [0, 0]    # times each side pulled it back to even

    def ko(self, port):
        if self.winner is not None:
            return
        self.lead += -1 if port == 0 else 1
        if self.lead == 0:
            self.evened[1 - port] += 1
        if self.lead > 0:
            self.biggest[0] = max(self.biggest[0], self.lead)
        if self.lead < 0:
            self.biggest[1] = max(self.biggest[1], -self.lead)
        if abs(self.lead) >= self.settings["lead"]:
            self.winner = 0 if self.lead > 0 else 1

    def tick(self, fighters=()):
        if self.winner is None and self.lead:
            self.ahead[0 if self.lead > 0 else 1] += 1

    def stats(self):
        return [("Biggest lead", tuple(self.biggest), "more"),
                ("Time ahead", tuple(clock(f) for f in self.ahead), "more"),
                ("Pulled back to even", tuple(self.evened), "more")]

    def result(self, names):
        if self.winner is None:
            return ""
        return "%s pulled it %d ahead" % (names[self.winner],
                                         self.settings["lead"])

    def stocks(self):
        return (max(self.lead, 0), max(-self.lead, 0))

    def rope(self):
        """(port 0's lead, the lead that wins): the rope board's knot."""
        return self.lead, self.settings["lead"]

    def end_rule(self):
        return ("tug", self.settings["lead"])

    def status(self, names):
        if self.winner is not None:
            return "Game: %s" % names[self.winner]
        if self.lead == 0:
            return "Even"
        return "%s +%d" % (names[0 if self.lead > 0 else 1], abs(self.lead))

    def scores(self):
        return True


# the selector's list, in its order


# Fox's down special, from the start of the shine to its end (on the ground,
# then in the air: ftFx_MS_SpecialLwStart .. ftFx_MS_SpecialAirLwTurn), and
# the two states it starts in
FOX_SHINE = range(360, 370)
FOX_SHINE_START = (360, 365)


class ShineBattle(Mode):
    """The owner, 2026-11-14: "Let's add a new mode called Shine battle.
    This should be fox dittos on jungle japes, 4 stocks a piece, shine only
    (any non shine move disabled, only jumping, shield, air dodge, etc., no
    other aerials, etc.)". A stock match: the side that loses its last
    stock loses. The host takes every other move away (moves.c), from a
    person, a model and the game's CPU alike; Firefox and Illusion can be
    let back in (an option, off at first: as the owner put it, the shine is
    the only move)."""
    ident = "shine-battle"
    name = "Shine Battle"
    tagline = "Fox against Fox on Jungle Japes. The shine is the only move."
    icon = "shine"
    colour, ink = "#5BC0EB", "#12161C"
    fighters = ("fox", "fox")
    stage = "jungle-japes"
    options = (
        Option("stocks", "Stocks", "How many stocks each side starts "
               "with: lose the last and the match is lost.",
               (1, 2, 3, 4, 5), 4, ("stock", "stocks")),
        Option("recovery", "Firefox and Illusion", "Whether Fox's up and "
               "side specials are allowed too, to get back to the stage: "
               "off, the shine is the only special.", ("Off", "On"), "Off",
               None),
    )

    def line(self):
        return "Fox against Fox on Jungle Japes, %s each. %s" % (
            self.options[0].words(self.settings["stocks"]),
            "Shine, Firefox and Illusion." if self.recovery() else
            "The shine is the only move.")

    def rules_text(self):
        return ("A stock match, %s each: lose the last and the match is "
                "lost." % self.options[0].words(self.settings["stocks"]),
                "The shine is the only attack: no other attack, aerial, "
                "grab%s." % ("" if self.recovery() else " or special"),
                "Jump, shield, dodge, tech and move as you like.")

    def summary(self):
        return "%s · %s" % (self.options[0].words(self.settings["stocks"]),
                            "Firefox and Illusion too" if self.recovery()
                            else "Shine only")

    def recovery(self):
        return self.settings["recovery"] == "On"

    def moves(self):
        return "recovery" if self.recovery() else "shine"

    def stock_match(self):
        return self.settings["stocks"]

    def start(self):
        super().start()
        self.left = [self.settings["stocks"]] * 2
        self.shines = [0, 0]        # shines started
        self.landed = [0, 0]        # shines that hurt the other side
        self.was = [None, None]     # last frame's state and percent

    def ko(self, port):
        if self.winner is not None:
            return
        self.left[port] = max(0, self.left[port] - 1)
        if self.left[port] == 0:
            self.winner = 1 - port

    def tick(self, fighters=()):
        now = [None, None]
        for port in (0, 1):
            f = fighters[port] if port < len(fighters) else None
            if f:
                now[port] = (f["state"], f["percent"])
        for port in (0, 1):
            if now[port] is None:
                continue
            state, percent = now[port]
            was = self.was[port]
            if state in FOX_SHINE_START and (was is None or
                                             was[0] not in FOX_SHINE_START):
                self.shines[port] += 1
            other = now[1 - port]
            if was is not None and percent > was[1] and other is not None \
                    and other[0] in FOX_SHINE:
                self.landed[1 - port] += 1
        self.was = now

    def stocks(self):
        return tuple(self.left)

    def status(self, names):
        if self.winner is not None:
            return "Game: %s" % names[self.winner]
        return "Stocks %d – %d" % tuple(self.left)

    def scores(self):
        return True

    def stats(self):
        return [("Shines", tuple(self.shines), None),
                ("Shines that hit", tuple(self.landed), "more"),
                ("Stocks left", tuple(self.left), "more")]

    def result(self, names):
        if self.winner is None:
            return ""
        n = self.left[self.winner]
        return "%s wins, %d stock%s left" % (names[self.winner], n,
                                             "" if n == 1 else "s")


MODES = [Unlimited, TugOfWar, ShineBattle]
BY_ID = {m.ident: m for m in MODES}
MOVES = ("all", "shine", "recovery")
BOARDS = (None, "rope")     # screens.BOARDS draws each
RULES = ("none", "tug")     # src/host/rules.c


def clock(frames):
    """Frames as m:ss."""
    s = int(frames // 60)
    return "%d:%02d" % (s // 60, s % 60)


class MatchStats:
    """What every mode's results screen shows of a match, read frame by
    frame from the two fighters (`see(fighters, kos)` with the state's
    fighters and the ports KO'd this frame): KOs taken, damage dealt and
    taken (a fighter's percent going up while it is in play), the highest
    damage each reached, the average percent each took a stock at, the
    match's length."""

    def __init__(self):
        self.frames = 0
        self.taken = [0, 0]         # stocks each side took
        self.dealt = [0.0, 0.0]
        self.hurt = [0.0, 0.0]
        self.highest = [0.0, 0.0]
        self.at_ko = [[], []]       # the other side's percent at each KO
        self.percent = [0.0, 0.0]   # last frame's, in play

    def see(self, fighters, kos):
        self.frames += 1
        for port in (0, 1):
            f = fighters[port] if port < len(fighters) else None
            if not f or f["state"] in DEAD or f["state"] in (11, 12, 13):
                continue
            p = f["percent"]
            if p > self.percent[port]:
                self.hurt[port] += p - self.percent[port]
                self.dealt[1 - port] += p - self.percent[port]
            self.percent[port] = p
            self.highest[port] = max(self.highest[port], p)
        for port in kos:
            self.taken[1 - port] += 1
            self.at_ko[1 - port].append(self.percent[port])
            self.percent[port] = 0.0

    def rows(self):
        """[(name, (port 0's, port 1's), better)] as Mode.stats."""
        def average(v):
            return "%d%%" % round(sum(v) / len(v)) if v else "-"
        return [
            ("KOs", tuple(self.taken), "more"),
            ("Damage dealt", tuple("%d%%" % round(v) for v in self.dealt),
             "more"),
            ("Damage taken", tuple("%d%%" % round(v) for v in self.hurt),
             "less"),
            ("Highest damage", tuple("%d%%" % round(v)
                                     for v in self.highest), None),
            ("Average KO", tuple(average(v) for v in self.at_ko), "less"),
        ]


class Falls:
    """KOs from the game's own count of each player's falls (a
    self-destruct counts too): `see(fighters)` with the state's two
    fighters returns the ports that fell since the last look. Online, give
    `frame` (the session frame the state is of) and `confirmed` (the last
    frame both sides' inputs are known for, `net stats`): a fall then
    counts only once its frame is confirmed, and one a rollback takes back
    is never counted."""

    def __init__(self):
        self.counted = [None, None]
        self.waiting = [[], []]     # frames each uncounted fall was seen on

    def see(self, fighters, frame=None, confirmed=None):
        out = []
        for port in (0, 1):
            f = fighters[port] if port < len(fighters) else None
            if not f:
                continue
            n = f.get("falls", 0)
            if self.counted[port] is None:
                self.counted[port] = n
                continue
            w = self.waiting[port]
            have = self.counted[port] + len(w)
            if n < have:            # a rollback took one back
                del w[max(0, n - self.counted[port]):]
            for _ in range(n - have):
                w.append(frame)
            while w and (confirmed is None or (w[0] is not None and
                                               confirmed >= w[0])):
                w.pop(0)
                self.counted[port] += 1
                out.append(port)
        return out


# ---- the format, checked ------------------------------------------------------

HUD_MOST = 5            # the HUD's stock row shows up to 5 icons
IDENT = re.compile(r"^[a-z][a-z0-9-]*$")
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def check(cls, icons=None, tries=300, seed=1, characters=None,
          stage_ids=None):
    """What is wrong with mode class `cls` by the format
    (docs/ai/game-modes.md), as sentences ([] if nothing): its words and
    looks, its options, what it fixes, and its score played through `tries`
    random runs of KOs with every setting. `icons`: the line icons there
    are (icons.py ICON), to check the mode's; `characters` and
    `stage_ids`: the ones the native build knows (native.py CHARACTERS,
    STAGES), to check a mode's fixed fighters and stage."""
    out = []
    if cls.fighters is not None and not (
            isinstance(cls.fighters, tuple) and len(cls.fighters) == 2 and
            all(isinstance(c, str) for c in cls.fighters)):
        out.append("%s's fighters are not (yours, theirs)" % cls.__name__)
    elif cls.fighters is not None and characters is not None and \
            not set(cls.fighters) <= set(characters):
        out.append("%s's fighters %r are not characters the native build "
                   "knows" % (cls.__name__, cls.fighters))
    if cls.stage is not None and stage_ids is not None and \
            cls.stage not in stage_ids:
        out.append("%s's stage %r is not one the native build knows" % (
            cls.__name__, cls.stage))
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
            if m.scores() and m.board is None and not m.stock_match():
                out.append("%s(%r): keeps a score, but neither a board nor "
                           "a stock match shows it" % (cls.__name__, kept))
                break
            if m.scores() and not m.stock_match() and \
                    m.end_rule()[0] == "none":
                out.append("%s(%r): keeps a score, but the game never ends "
                           "the match (a stock match or a rule)" % (
                               cls.__name__, kept))
                break
            if m.end_rule()[0] not in RULES:
                out.append("%s(%r): end rule %r, not one of %s" % (
                    cls.__name__, kept, m.end_rule(), RULES))
                break
            if m.board not in BOARDS:
                out.append("%s: board %r, not one of %s" % (
                    cls.__name__, m.board, BOARDS))
                break
            if m.moves() not in MOVES:
                out.append("%s(%r): moves %r, not one of %s" % (
                    cls.__name__, kept, m.moves(), ", ".join(MOVES)))
                break
            a, b = m.stocks()
            if not (isinstance(a, int) and isinstance(b, int)) or \
                    min(a, b) < 0 or (m.scores() and max(a, b) > HUD_MOST):
                out.append("%s(%r): stocks %r at the start" % (
                    cls.__name__, kept, (a, b)))
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
                for _ in range(rng.randrange(0, 90)):
                    m.tick([dict(state=rng.choice((14, 44, 360, 361, 365)),
                                 percent=rng.choice((0.0, 10.0, 25.0)))
                            if rng.random() > 0.1 else None
                            for _ in range(2)])
                bad = _bad_rows(m.stats())
                if bad:
                    out.append("%s(%r): stats %s" % (cls.__name__, kept,
                                                     bad))
                    break
                if m.winner is not None and (
                        not isinstance(m.result(names), str) or
                        not m.result(names)):
                    out.append("%s(%r): won, but no result line" %
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


def _bad_rows(rows):
    """What is wrong with a mode's stats rows, or ""."""
    if not isinstance(rows, list):
        return "are not a list"
    for r in rows:
        if not (isinstance(r, tuple) and len(r) == 3 and
                isinstance(r[0], str) and isinstance(r[1], tuple) and
                len(r[1]) == 2 and r[2] in ("more", "less", None)):
            return "row %r is not (name, (one, other), better)" % (r,)
    return ""


def check_all(icons=None, characters=None, stage_ids=None):
    """{ident: problems} for every mode in MODES, and the list's own
    (two modes with one ident). The arguments as check's."""
    out = {}
    seen = set()
    for cls in MODES:
        problems = check(cls, icons, characters=characters,
                         stage_ids=stage_ids)
        if cls.ident in seen:
            problems.append("two modes are %r" % cls.ident)
        seen.add(cls.ident)
        out[cls.ident or cls.__name__] = problems
    return out


if __name__ == "__main__":
    sys.path.insert(0, __import__("os").path.dirname(
        __import__("os").path.abspath(__file__)))
    import icons as _icons
    sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(
        __import__("os").path.abspath(__file__)), "..", "melee_native"))
    import native as _native
    bad = 0
    for ident, problems in check_all(set(_icons.ICON), _native.CHARACTERS,
                                     _native.STAGES).items():
        print("%-12s %s" % (ident, "ok" if not problems else
                            "; ".join(problems)))
        bad += len(problems)
    sys.exit(1 if bad else 0)
