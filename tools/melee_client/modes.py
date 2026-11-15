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
class and a line in MODES.
"""

# the game's dead states (ftCommon's Dead*: down, left, right, up, the
# star and the screen KOs): entering one is a KO
DEAD = range(0, 11)


class Mode:
    """A game mode. `ident` names it in settings and tests; `name`,
    `tagline` and `rules` are what the selector shows; `icon` is one of the
    client's line icons (icons.py), on its panel in `colour` (`ink` the
    colour on it)."""
    ident = ""
    name = ""
    tagline = ""
    rules = ()
    icon = "play"
    colour, ink = "#3A4250", "#F3F6FA"

    def __init__(self):
        self.start()

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
        """The score in words, for the column ("Deuce"); `names`: the two
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


class Tennis(Mode):
    """Tug of war (the owner: "scoring works like tug of war. A kill pulls
    it in your favor, and you have to win by +2 (so it is like starting at
    deuce in tennis). This will train trading even stocks and pushing
    advantages"): the score is one number, port 0's lead; a KO moves it a
    point toward the side that took it; two ahead wins. Shown as stocks
    ("at the start nothing shows up, then as a player takes a stock, it
    either removes the opponent's stock or adds one to theirs"): the side
    ahead has its lead in stock icons, the other none."""
    ident = "tennis"
    name = "Tennis"
    tagline = "Start at deuce. Win by two stocks."
    rules = ("A KO pulls the score your way: it takes away the other "
             "side's stock, or adds one to yours.",
             "Two ahead wins. Even trades bring it back to deuce.",
             "Trains trading stocks evenly and pushing an advantage.")
    icon = "tennis"
    colour, ink = "#C9E24A", "#12161C"
    LEAD = 2

    def start(self):
        super().start()
        self.lead = 0           # port 0's lead (negative: port 1's)

    def ko(self, port):
        if self.winner is not None:
            return
        self.lead += -1 if port == 0 else 1
        if abs(self.lead) >= self.LEAD:
            self.winner = 0 if self.lead > 0 else 1

    def stocks(self):
        return (max(self.lead, 0), max(-self.lead, 0))

    def status(self, names):
        if self.winner is not None:
            return "Game: %s" % names[self.winner]
        if self.lead == 0:
            return "Deuce"
        return "Advantage %s" % names[0 if self.lead > 0 else 1]

    def scores(self):
        return True


# the selector's list, in its order
MODES = [Unlimited, Tennis]
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
