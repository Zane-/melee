---
name: add-game-mode
description: Add or change a Versus game mode in the native client (what a match is played for - its scoring from KOs, its settings, how its score shows in the HUD's stock icons, when it is won, its stats on the results screen, and what it fixes - the characters, the stage, the moves allowed) in the standard mode format of tools/melee_client/modes.py, with its icon, its check and its test. Use when asked for a new Versus mode or rule set (first to N, stock trades, handicaps, score variants, a character or move restricted mode like Shine Battle), to add a setting or a stat to a mode, or to change how a mode scores.
---

# Add a game mode

The format and what the client does with a mode: `docs/ai/game-modes.md` (read it first).
The modes: `tools/melee_client/modes.py` (`Mode`, `Option`, `MODES`). A mode is one class
and a line in `MODES`; the selector, the options screen, the column, the HUD and the result
come from it with no other change to the client.

## 1. Pin the rules down in words first

Before code, write down (and confirm with the owner when anything is unclear):

- what one KO does to the score, for the side that took it and the side that lost it
  (a self-destruct gives the point to the other side: the client cannot tell them apart);
- when the match is won, and by whom;
- how its score shows: a board over the game (`screens.BOARDS`: the rope, or a new one)
  or, for a stock match, the game's own HUD;
- how the game ends it: a stock match at its last stock, or a rule decided in the game's
  own frame from its counters (`src/host/rules.c`: `tug`; a new end is a new rule there,
  in C). The client never writes a score into the game: that is what keeps every mode
  playable online (`docs/ai/game-modes.md`, "Online");
- what the player can set before the match (each setting's values and default);
- whether it fixes the characters, the stage, or the moves both sides may use (`all`,
  `shine`, `recovery`; a rule the host lacks is C in `src/host/moves.c`, see the doc);
- what the results screen shows of it (its own stats rows, its result line).

## 2. The class

In `modes.py`, after the last mode:

```python
class FirstTo(Mode):
    """... the owner's words for it, quoted, with the date ..."""
    ident = "first-to"                 # never changed once players have it
    name = "First To"
    tagline = "The first to take N stocks wins."
    rules = ("...", "...")             # or rules_text() saying the settings
    icon = "flag"                      # one of icons.py's ICON
    colour, ink = "#4A90D9", "#F3F6FA"
    options = (Option("goal", "First to", "How many stocks win: ...",
                      (3, 4, 5), 3, ("stock", "stocks")),)

    def line(self):                    # the tagline as set (optional)
        return "First to %d stocks." % self.settings["goal"]

    def summary(self):
        return "First to %d" % self.settings["goal"]

    def start(self):
        super().start()                # winner = None
        self.taken = [0, 0]

    def ko(self, port):                # port was KO'd
        if self.winner is not None:
            return
        self.taken[1 - port] += 1
        if self.taken[1 - port] >= self.settings["goal"]:
            self.winner = 1 - port

    def end_rule(self):                # the game ends it (src/host/rules.c:
        return ("first", self.settings["goal"])  # a "first" rule to add)

    board = "score"                    # its board (screens.BOARDS: to add)

    def stocks(self):                  # the stocks each side has, if any
        return tuple(self.taken)

    def status(self, names):
        ...                            # the score in words

    def scores(self):
        return True

    def stats(self):                   # its rows on the results screen
        return [("Stocks taken", tuple(self.taken), "more")]

    def result(self, names):           # the line under the winner
        return "%s took %d first" % (names[self.winner],
                                     self.settings["goal"])
```

A mode played with set characters, on a set stage, with only some moves (Shine Battle):

```python
    fighters = ("fox", "fox")          # yours, theirs: no character select
    stage = "jungle-japes"             # one of native.STAGES: no stage select

    def moves(self):                   # "all", "shine" or "recovery"
        return "shine"

    def tick(self, fighters):          # each frame: states for its stats
        ...
```

A stage outside the select's six also goes in `stages.OTHER` (its name) and, if the
native build lacks it, `native.STAGES` (its id). A stock match is `stock_match()`
returning the stocks each: the game keeps them, shows them and ends the match.

A new end rule is C in `src/host/rules.c` (read only the game's counters, e.g.
`Player_GetFalls`; return `OUTCOME_ELIMINATION` when won), its word in the host's `rules`
command and `modes.RULES`. A new board is a pair in `screens.BOARDS`: its markup and its
classes as the score stands (`rope_board`, `rope_classes`; the client changes only the
classes, so a `transition` in `style.rcss` animates them).

Then add it to `MODES` where it belongs in the selector's order.

Rules the check holds a mode to (`modes.check`): `ident` lower-case words joined by `-`;
`name`, `tagline`, `icon` set; `colour` and `ink` `#RRGGBB`; each option's default among
its values; no win after `start()`, and stocks within the HUD's 5 (a stock match shows its
stocks from the start; a score from nothing shows `(0, 0)`); stocks whole numbers, at most 5
a side while the match is on; `winner` only 0 or 1, never changed once set; `status`, the
rules and the result line words; `stats()` rows `(name, (one, other), better)`; fixed
characters and stage the native build's; `moves()` one of `modes.MOVES`.

## 3. Its icon

A line drawing on a 24 by 24 grid in `tools/melee_client/icons.py`'s `ICON` (`(path,
filled)`: stroked lines, the client tints them), and its name in `LARGE` (mode icons are
shown at 112 dp, so they are made at 256 pixels). `python tools/melee_client/icons.py`
makes it; look at it on the selector before going on.

## 4. Check, then play it

```sh
python tools/melee_client/modes.py              # every mode: "ok"
python tests/client/modes_format.py             # the same, as a test (a second)
python tests/native/moves.py                    # a mode that restricts moves
```

Then extend `tests/client/versus_modes.py` (a virtual display; run it in the background,
`python -u`, a timeout of about twice its usual time: see CLAUDE.md): choose the mode on
the selector, set its options, play a match against a fighter nobody plays, make KOs with
its `ko(port)` helper (a fighter dropped below the blast zone), and check `c.game_mode`'s
score, its board's classes or a stock match's stocks (`w.state()["p"][i]["stocks"]`), the
game ending the match, the results screen (`results.rml`) and the rematch; for a mode that fixes things, that the selects are
skipped and the moves rule is in force (`w._cmd("moves 0")`). Take pictures (`--shots
DIR`, under `build/shots/`, never committed) of the selector, the options, the HUD and the
results, and look at them.

## 5. Docs

Add the mode to "The modes" in `docs/ai/game-modes.md`, with the owner's words for it. A
mode that needs anything new of the game (not a score in stocks: a timer, items, a
different end) changes the host too: say what in that doc and in `docs/ai/native-ai.md`'s
"Versus's game modes", and rebuild the window build (`python tools/native_build.py
--window`; another session may be using it: tell it first).

## Limits now

- Online, both sides must choose the same mode and settings (they are told when not).
  Test a mode online too: `tests/client/online_modes.py`, KOs made by inputs (a fighter
  walking off), never by commands into one game.
- The game's CPU does not know a moves rule: it keeps choosing attacks that never come
  out. A restricted mode is played against a person or a model.
- A KO is the game's count of falls, not who caused it: a self-destruct counts as the
  other side's KO.
- In the endless match the game's own "SCORE +1"/"−1" pop-ups still show on each KO.
