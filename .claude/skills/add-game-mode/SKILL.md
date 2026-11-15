---
name: add-game-mode
description: Add or change a Versus game mode in the native client (what a match is played for - its scoring from KOs, its settings, how its score shows in the HUD's stock icons, when it is won) in the standard mode format of tools/melee_client/modes.py, with its icon, its check and its test. Use when asked for a new Versus mode or rule set (first to N, stock trades, handicaps, score variants), to add a setting to a mode, or to change how a mode scores.
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
- what the HUD's stock icons show at the start and after each KO (each side up to 5
  icons; nothing at the start reads as "nothing yet");
- what the player can set before the match (each setting's values and default).

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

    def stocks(self):                  # the HUD: up to 5 icons each
        return tuple(self.taken)

    def status(self, names):
        ...                            # the score in words

    def scores(self):
        return True
```

Then add it to `MODES` where it belongs in the selector's order.

Rules the check holds a mode to (`modes.check`): `ident` lower-case words joined by `-`;
`name`, `tagline`, `icon` set; `colour` and `ink` `#RRGGBB`; each option's default among
its values; no win and `stocks() == (0, 0)` after `start()` for a mode that scores; stocks
whole numbers, at most 5 a side while the match is on; `winner` only 0 or 1, never changed
once set; `status` and the rules words.

## 3. Its icon

A line drawing on a 24 by 24 grid in `tools/melee_client/icons.py`'s `ICON` (`(path,
filled)`: stroked lines, the client tints them), and its name in `LARGE` (mode icons are
shown at 112 dp, so they are made at 256 pixels). `python tools/melee_client/icons.py`
makes it; look at it on the selector before going on.

## 4. Check, then play it

```sh
python tools/melee_client/modes.py              # every mode: "ok"
python tests/client/modes_format.py             # the same, as a test (a second)
```

Then extend `tests/client/versus_modes.py` (a virtual display; run it in the background,
`python -u`, a timeout of about twice its usual time: see CLAUDE.md): choose the mode on
the selector, set its options, play a match against a fighter nobody plays, make KOs with
its `ko(port)` helper (a fighter dropped below the blast zone), and check `c.game_mode`'s
score, the HUD's stocks (`w.state()["p"][i]["stocks"]`), the end and the rematch. Take
pictures (`--shots DIR`, under `build/shots/`, never committed) of the selector, the
options and the HUD, and look at them.

## 5. Docs

Add the mode to "The modes" in `docs/ai/game-modes.md`, with the owner's words for it. A
mode that needs anything new of the game (not a score in stocks: a timer, items, a
different end) changes the host too: say what in that doc and in `docs/ai/native-ai.md`'s
"Versus's game modes", and rebuild the window build (`python tools/native_build.py
--window`; another session may be using it: tell it first).

## Limits now

- Online Versus has no modes (both sides would have to agree and score alike).
- A KO is seen, not who caused it: a self-destruct counts as the other side's KO.
- Every match is the endless time match: a mode's score is the client's, shown in the
  stock row; the game's own "+1"/"−1" pop-ups still show on each KO.
