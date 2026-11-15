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
stage > the match > **the results**. B steps back the same way. A mode that fixes the
characters skips the character select (the opponent screen then only says who plays the
other side), and one that fixes the stage skips the stage select. **Online** goes the same
way to the online screen (Versus > Online > the mode > its options > the character, unless
fixed); see "Online" below.

**The results** (`screens.results_page`, the owner: "a more robust game over screen. It
should have stats, etc. for both players ... in our UI style, but it should support custom
stats, etc. per mode!"): when the game has ended the match (its own GAME!, below), the
winner's card (its
art, the mode's `result()` line, the KOs as each side's stock icon either side of the
score, the mode, its settings, the stage, the match's length) beside a table of the two
sides: P1 and P2, 1st and 2nd, the character and who played it, then the mode's own rows
(`stats()`) and every mode's (`modes.MatchStats`: KOs, damage dealt and taken, the highest
damage, the average damage at which each took a stock). In each row the better side's
number is marked. A plays again, X goes to the characters (the mode's options when it
fixes them), B to the stages (the opponent when it fixes the stage); online, A goes back to
the online screen.

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
| `stocks()` | `(port 0's, port 1's)` stocks: a stock match's left, for its stats and results |
| `stock_match()` | the match's stocks each (a stock match: the game keeps them, its HUD shows them, it ends the match at the last), or 0: the endless time match |
| `end_rule()` | how the game ends an endless match besides stocks, decided in its own frame (`src/host/rules.c`): `("none", 0)` or `("tug", lead)` |
| `board` | `None`, or the score board drawn over the game (`screens.BOARDS`: `"rope"`, Tug of War's; the client changes its elements' classes as the score changes, and RmlUi slides what moves) |
| `status(names)` | the score in words for the column (`"Even"`, `"Fox +1"`), `names` the two sides' |
| `scores()` | whether the mode keeps a score at all (False: no board, no KOs counted, no end) |
| `fighters` | `None`, or the two characters it is played with, `(yours, theirs)` by the native build's ids (`("fox", "fox")`): the character select is skipped |
| `stage` | `None`, or the stage it is played on (`"jungle-japes"`, one of `native.STAGES`; a stage not among the six on the select also goes in `stages.OTHER` for its name): the stage select is skipped |
| `moves()` | the moves both sides may use: `"all"`, `"shine"` (the down special and no attack) or `"recovery"` (the down, up and side specials); see "Moves" below |
| `tick(fighters)` | each frame, before that frame's KOs are told: the two fighters' states (`"state"`, the motion state, `"percent"`), for the mode's own stats |
| `stats()` | the mode's rows on the results screen, `[(name, (port 0's, port 1's), better)]`: each value a number or words (`"0:12"`, `"40%"`), `better` `"more"`, `"less"` or `None` (which side's is marked) |
| `result(names)` | the line under the winner (`"Fox pulled it 3 ahead"`) |

**An option** is `Option(key, name, about, values, default, unit)`: `key` in the mode's
`settings`, `name` and `about` as the options screen shows them (`about`'s first clause is
the row's gloss), the `values` left and right step through (they stop at either end), the
`default`, and `unit` = (one, many) after the number ("3 stocks"), or `None` for values that are words
(`("Off", "On")`). The mode reads its settings from `self.settings[key]`; a kept value no
longer among `values` falls back to the default.

## What the client does with it

`Client.fight` (and `online_match`) makes the mode as set, puts its rules into the game
before the match (`mode_rules`: `moves P RULE`, `rules ...`) and starts a stock match of
`stock_match()` stocks or the endless time match. Each frame (`mode_frame`), `modes.Falls`
reads each player's falls (the game's own count, a self-destruct too; `state()`'s "falls")
and calls `ko(port)` for each new one, then `tick`, the stats, the column's `status()` and
the board.

**The game ends the match itself**, as the console's does (the owner, 2026-11-14: "use the
stock game's GAME! screen which freezes the game the moment it ends so we have more of a
natural, familiar transition"): a stock match at its last stock, an endless match by the
mode's `end_rule()` (`src/host/rules.c`, asked by `gm_GetMatchOutcome` each frame through
a patch: the lead reached ends it as a last stock does, `OUTCOME_ELIMINATION`). The game
stops, GAME! and the announcer play, and the scene ends; the host starts the same match
again (`state()`'s "ended"), and the client puts the results over it (held still and
quiet locally; online it runs on). An end the mode had no winner for is a quit
(L+R+A+Start): the client leaves the match as before. The score is never written into the
game by the client, so nothing it does mid-match can put two online games apart.

**A board** is the mode's own score over the game, top centre. Tug of War's rope (the owner:
"an actual tug of war display that moves the stock icon along nodes to visually see who is
winning"): P1's stock icon at the left end, P2's at the right, a node a point between; the
knot sits on the lead's node, the leader's stock icon riding it (a knot at even), the
nodes it was pulled across in the leader's colour. A stock match's score is the game's own
HUD. The endless match's own "SCORE +1/−1" pop-ups still show.

## Online

Both sides choose a mode and its settings; the lobby's hello carries them
(`online.Lobby.meet`, `me["mode"]`), and two that differ do not meet: each is told what the
other chose (`online.ModeMismatch`). The side that proposes the match sends the mode with
the rest (a fixed stage replaces its stage; in a mirror the second costume is the next).
Both put the same rules into their games before the session starts (`moves`, `rules`, a
stock match's stocks): rules that do not change during the match, so the session's two
games stay one. KOs count only once both sides' inputs up to them are known (`Falls` with
`net stats`' `confirmed`), so the board never shows a KO a rollback takes back; the end is
the game's own, on the same frame in both games. `tests/client/online_modes.py`: two
clients choose different modes (refused, each told), then Tug of War, and play it to the
end with KOs made by inputs (Marth walking off), the results on both, no desync.

## Moves

A mode's `moves()` goes to the host before the match loads (`moves P RULE`,
`Native.moves`) and back to `"all"` when the match is left. `src/host/moves.c` applies it
in `Fighter_procInput`, right after the fighter's buttons are read (a patch in
`tools/native_build.py`), so it holds for a person, a slippi-ai model and the game's own
CPU alike: A and Z never reach the game; the C-stick is still except in hitlag (its ASDI),
again after UCF has read the pad; B reaches the game only as a new press with the stick
past the line the game's down special takes (and, for `"recovery"`, past the up or side
special's), never on the ledge or lying down (there it is the ledge or getup attack); held,
it stays (the reflector held). Jumps, shield, rolls, dodges, air dodges, techs and
movement are untouched. `python tests/native/moves.py` tries every way to an attack
standing, in the air, in shield and on the ledge, and a level 9 CPU for a minute. The
game's CPU does not know the rule: it keeps choosing attacks that never come out, and it
rarely shines, so a shine-only mode is played against a person or a model.

## Checked

`python tools/melee_client/modes.py` holds every mode in `MODES` to this format
(`modes.check`): its words, ident, icon and colours; its options (a default among its
values, keys unique); and its score, played through hundreds of random runs of KOs with
every setting: stocks whole numbers, no more than the HUD's 5 icons while the match is on,
`winner` only 0 or 1 and never changed once set, `status` words, `stats()` rows in their
shape, a `result()` line once won; at the start no win and stocks within the HUD; a fixed
character or stage one the native build knows (`native.CHARACTERS`, `native.STAGES`);
`moves()`, `end_rule()` and `board` among the host's and the screens' (`modes.MOVES`,
`RULES`, `BOARDS`). A mode that keeps a score must show it (a board, or a stock match's
HUD) and must be ended by the game (a stock match, or a rule): the client never writes a
score into the game, which is what lets every mode play online.
`tests/client/modes_format.py` runs it with no game (a second); the client test
`tests/client/versus_modes.py` plays the selector, the options, a Tug of War match to the
results and a Shine Battle on a virtual display; `tests/client/online_modes.py` the modes
online; `tests/native/moves.py` the moves.

## The modes

- **Unlimited**: the match as it was. No score, no end.
- **Tug of War** (first called Tennis): one number, the player's lead; a KO pulls it a
  point toward the side that took it; `lead` ahead wins (2 to 5, 2 at first; the game ends
  it, `end_rule()` `("tug", lead)`). Its board is the rope. Its stats: the biggest lead, the
  time ahead, the times each pulled it back to even.
- **Shine Battle** (the owner, 2026-11-14: "fox dittos on jungle japes, 4 stocks a piece,
  shine only (any non shine move disabled, only jumping, shield, air dodge, etc., no other
  aerials, etc.)"): Fox against Fox on Jungle Japes, the game's own stock match (1 to 5
  stocks, 4 at first), `moves()` `"shine"`; the option Firefox and Illusion (off at first) lets the up
  and side specials back for recovering (`"recovery"`). Its stats: shines started, shines
  that hurt the other side (its damage rising while the other is in the shine), stocks
  left.
