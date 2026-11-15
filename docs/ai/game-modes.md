# Versus game modes: the format

What a Versus match is played for. The owner, 2026-11-14: "We need to add support for
different game modes instead of just the unlimited score game ... Make sure we have a good
game mode selector so we can build up more and more custom game modes", then "make sure
that each game mode has support for settings (i.e. win by 3, etc. on tug of war) within the
mode selection. It should go select the mode, then configure options, then start game!",
and "make sure we have a standard format for defining game modes and we have skills for
creating them so we can extend this!". To add one, use the skill `add-game-mode`.

## The flow

Versus > Local > **Choose a mode** (`screens.mode_select`: a panel per mode, its icon on
its colour; a card saying how it is scored) > **its options**, if it has any
(`screens.mode_options`: a row per setting, the one in focus edited big beside them, left
and right to change; the client keeps them) > the character select > the opponent > the
stage > the match. B steps back the same way. Online Versus has no modes yet (both sides
would have to agree on one and score it alike).

## A mode is a class

In `tools/melee_client/modes.py`, a subclass of `Mode` with its place in `MODES` (the
selector lists them in that order). Nothing else in the client changes for a new mode:
the selector, the options screen, the column, the HUD and the result are drawn from it.

| Part | What it is |
|-|-|
| `ident` | lower-case words joined by `-` (`"tug-of-war"`): its name in the kept settings and in tests; never changed once players have it |
| `name` | as the player reads it (`"Tug of War"`) |
| `tagline` | one line about it; `line()` may say it as set ("Start even. Win by 3 stocks.") |
| `rules`, `rules_text()` | how it is scored, a sentence each (the card's list); `rules_text()` may say the settings |
| `icon` | one of the client's line icons (`tools/melee_client/icons.py`, `ICON`; a mode's goes in `LARGE` too, made at 256 pixels) |
| `colour`, `ink` | its panel's colour and the colour on it (`#RRGGBB`) |
| `options` | its settings, `Option`s (below); none: the options screen is skipped |
| `summary()` | its settings in a few words for the column (`"Win by 3"`), or `""` |
| `start()` | a new match: the score back to nothing, `winner = None` |
| `ko(port)` | port 0 or 1 was KO'd (a self-destruct too): change the score; set `winner` (0 or 1) when the match is won; nothing once it is won |
| `stocks()` | `(port 0's, port 1's)` stocks to show: the score in the HUD (up to 5 icons each) |
| `status(names)` | the score in words for the column (`"Even"`, `"Fox +1"`), `names` the two sides' |
| `scores()` | whether the mode keeps a score at all (False: no HUD row, no KOs counted, no end) |

**An option** is `Option(key, name, about, values, default, unit)`: `key` in the mode's
`settings`, `name` and `about` as the options screen shows them (`about`'s first clause is
the row's gloss), the `values` left and right step through (they stop at either end), the
`default`, and `unit` = (one, many) after the number ("3 stocks"). The mode reads its
settings from `self.settings[key]`; a kept value no longer among `values` falls back to
the default.

## What the client does with it

`Client.fight` makes the mode as the player set it (`make_mode`). Each frame of the match,
`modes.KOs` sees a KO as a fighter entering one of the game's dead states (`DEAD`) and
calls `ko(port)`; after any KO the client sets the HUD's stocks from `stocks()` (`stocks P
N`, `Native.stocks`) and the column's line from `status()`. When `winner` is set, the
winning stock shows for `Client.GAME_SHOWN` frames, then the game stops (`freeze`) with the
result on the banner: A plays again (`start()` on a new match), B goes back to the stages.

**The score is the game's own stock row.** Every match is the game's endless time match:
stocks end nothing in it, so a mode keeps its score in them. That match's HUD shows one
icon whatever the count; the host makes a player's icons again as a stock match's (which
follow the count each frame, one breaking with the game's own effect as it falls) the
first time a mode asks in a match and on each respawn (`stock_rows`, `src/host/control.c`).
So a mode that shows nothing at the start returns `(0, 0)`. The HUD shows up to 5 icons;
more is drawn as a number. The endless match's own "+1"/"−1" pop-ups still show on each
KO.

## Checked

`python tools/melee_client/modes.py` holds every mode in `MODES` to this format
(`modes.check`): its words, ident, icon and colours; its options (a default among its
values, keys unique); and its score, played through hundreds of random runs of KOs with
every setting: stocks whole numbers, no more than the HUD's 5 icons while the match is on,
`winner` only 0 or 1 and never changed once set, no win and nothing shown before a KO,
`status` words. `tests/client/modes_format.py` runs it with no game (a second); the client
test `tests/client/versus_modes.py` plays the selector, the options and a match on a
virtual display.

## The modes

- **Unlimited**: the match as it was. No score, no end.
- **Tug of War** (first called Tennis): one number, the player's lead; a KO pulls it a
  point toward the side that took it; `lead` ahead wins (2 to 5, 2 at first). The side
  ahead has its lead in stock icons, the other none; even, nothing.
