"""The client's screens as RmlUi markup (style.rcss has the look).

Each function returns a whole document; client.py writes it to a file and
has the game load it. What changes while a screen is up (which panel has
the focus, the line at the bottom, the character card) is changed in place
by element id.
"""
from pathlib import Path

# The style sheet is named beside the document: client.py copies it there
# (RmlUi takes a path that starts with a slash for one below its own root).
STYLE = Path(__file__).with_name("style.rcss")
PART_CLASS = {"Tech": "tech", "Punish": "punish", "Defense": "defense",
              "Neutral": "neutral"}
PART_COLOR = {"Tech": "#1F49C9", "Punish": "#F0643C", "Defense": "#22B8A0",
              "Neutral": "#F5BE1B"}


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;")


def page(title, body, paper=True):
    return ('<rml><head><title>%s</title>'
            '<link type="text/rcss" href="style.rcss"/></head>'
            '<body class="%s">%s</body></rml>' % (
                esc(title), "paper" if paper else "", body))


def key(letter, dark=False, wide=False):
    return '<div class="key%s%s">%s</div>' % (
        " dark" if dark else "", " wide" if wide else "", esc(letter))


def header(crumbs, tag=None):
    """`crumbs`: where this screen is, the last being the screen itself.
    `tag`: (text, colour, text colour) for the character being trained."""
    words = []
    for c in crumbs[:-1]:
        words.append('<span class="dim">%s / </span>' % esc(c))
    words.append(esc(crumbs[-1]))
    stripes = "".join('<div class="stripe" style="background-color: %s"/>'
                      % PART_COLOR[p] for p in PART_COLOR)
    who = ""
    if tag:
        who += ('<div class="tag" style="background-color: %s; color: %s">'
                '<div class="un">%s</div></div>' % (tag[1], tag[2],
                                                    esc(tag[0])))
    who += ('<div class="port">PORT 1</div><div class="nick">----</div>'
            '<div class="layout">Default layout</div>')
    ticks = "".join('<div class="tick%s"/>' % (" ten" if i % 10 == 0 else "")
                    for i in range(60))
    return ('<div class="header"><div class="plate"><div class="title">%s'
            '</div></div>%s<div class="grow"/><div class="who">%s</div></div>'
            '<div class="ruler">%s</div>' % ("".join(words), stripes, who,
                                             ticks))


def footer(text, hints, tab="#F3F6FA"):
    """`hints`: (button, what it does) pairs."""
    # (text straight inside a flex row is not drawn: it gets an element)
    out = "".join('<div class="hint">%s<div>%s</div></div>' % (
        key(k, wide=len(k) > 1), esc(what)) for k, what in hints)
    return ('<div class="footer"><div id="tab" class="tab" '
            'style="background-color: %s"/><div id="desc" class="desc">%s'
            '</div><div class="grow"/>%s</div>' % (tab, esc(text), out))


# ---- main menu ---------------------------------------------------------------

MAIN = [
    # id, class, number, name, what it is, built in this client
    ("train", "ink", "01", "Train",
     "Pick a character and work through its course.", True),
    ("lab", "lab", "02", "Lab",
     "Free practice with any character and situation.", False),
    ("events", "events", "03", "Events",
     "Training Mode's own events, page by page.", False),
    ("versus", "slate", "04", "Versus", "A match, two to four players.",
     False),
    ("controls", "white", "05", "Controls",
     "Input delay and button layouts.", False),
]


def _tile(item, extra=""):
    ident, cls, number, name, about, built = item
    soon = "" if built else '<div class="soon">NOT YET</div>'
    return ('<div id="%s" class="tile %s"><div class="ring"/>'
            '<div class="in"><div class="row"><div class="idx">%s</div>'
            '<div class="grow"/>%s</div><div><div class="big">%s</div>'
            '<div class="sub">%s</div>%s</div></div>%s</div>' % (
                ident, cls, number, soon, esc(name), esc(about), extra[0]
                if extra else "", extra[1] if extra else ""))


def main_menu(last=None):
    """`last`: (character name, colour) of the last one trained, if any."""
    by = {item[0]: item for item in MAIN}
    mark = ""
    if last:
        mark = ('<div class="last"><div class="mark" style="background-color:'
                ' %s">LAST</div><div>%s</div></div>' % (last[1],
                                                        esc(last[0])))
    bands = '<div class="bands">%s</div>' % "".join(
        '<div class="band %s"><div class="un">%s</div></div>' % (
            PART_CLASS[p], p) for p in PART_CLASS)
    gap = '<div class="gap"/>'
    body = (
        header(["Main menu"]) +
        '<div class="mosaic">' + _tile(by["train"], (mark, bands)) + gap +
        '<div class="right">' + _tile(by["lab"]) + gap +
        '<div class="lower">' + _tile(by["events"]) + gap +
        '<div class="small">' + _tile(by["versus"]) + gap +
        _tile(by["controls"]) + '</div></div></div></div>' +
        footer(by["train"][4], [("A", "Choose")]))
    return page("Main menu", body)


# ---- character select -----------------------------------------------------------

def card(c):
    """The inside of the panel about one character."""
    size = 40 if len(c["name"]) > 9 else 64
    head = ('<div class="top" style="background-color: %s"/>'
            '<div class="slant" style="background-color: %s"/>'
            '<div class="head" style="color: %s"><div class="tags">%s</div>'
            '<div class="who2" style="font-size: %ddp">%s</div></div>' % (
                c["color"], c["color"], c["fg"],
                esc(" · ".join(c["tags"]).upper()), size, esc(c["name"])))
    stats = "".join(
        '<div class="stat"><div class="n">%s</div><div class="l">%s</div>'
        '</div>' % (esc(n), what) for n, what in (
            (c["weight"], "weight"), (c["fall"], "fall speed"),
            (c["squat"], "frames of jump squat")))
    if c["course"]:
        summary, counts = c["course"]
        parts = "".join(
            '<div class="part"><div class="sq" style="background-color: %s"/>'
            '<div>%s</div><div class="cnt">%d</div></div>' % (
                PART_COLOR[p], p, counts[p])
            for p in PART_COLOR)
        about = ('<div class="about">A course of its own, %d drills. '
                 'Drills are not in this client yet: this starts free play.'
                 '</div><div class="parts">%s</div>' % (
                     sum(counts.values()), parts))
    else:
        about = ('<div class="about">No course of its own yet. Drills are '
                 'not in this client yet either: this starts free play.'
                 '</div>')
    go = ('<div class="grow"/><div class="go"><div class="un">%s'
          '<div>Play</div></div></div>' % key("A", dark=True))
    return head + ('<div class="body"><div class="stats">%s</div>%s%s</div>'
                   % (stats, about, go))


def character_select(roster, focus):
    tiles = []
    for i, c in enumerate(roster):
        course = ""
        if c["course"]:
            course = '<div class="course">%s</div>' % "".join(
                '<div style="background-color: %s"/>' % PART_COLOR[p]
                for p in PART_COLOR)
        tiles.append(
            '<div id="c%d" class="char%s" style="background-color: %s; '
            'color: %s"><div class="ring"/><div class="in"><div class="mono2">'
            '%s</div><div class="name">%s</div></div>%s</div>' % (
                i, " focus" if i == focus else "", c["color"], c["fg"],
                esc(c["mono"]), esc(c["short"]), course))
    body = (
        header(["Choose your character"]) +
        '<div class="roster">' + "".join(tiles) + '</div>' +
        '<div id="card" class="card">' + card(roster[focus]) + '</div>' +
        footer("Choose who you train. A drill brings its own opponents.",
               [("A", "Choose"), ("B", "Back")], tab=roster[focus]["color"]))
    return page("Character select", body)


# ---- in a match ----------------------------------------------------------------

def match_rail(c, opponent, stage):
    """The column beside the game's picture. The rest of the window is left
    clear: the game shows through at the left."""
    head = ('<div class="top" style="background-color: %s"/>'
            '<div class="slant" style="background-color: %s"/>'
            '<div class="head" style="color: %s"><div class="tags">FREE PLAY'
            '</div><div class="who2" style="font-size: %ddp">%s</div></div>'
            % (c["color"], c["color"], c["fg"],
               34 if len(c["name"]) > 9 else 48, esc(c["name"])))
    stats = "".join(
        '<div class="stat"><div class="n">%s</div><div class="l">%s</div>'
        '</div>' % (esc(n), what) for n, what in (
            (c["weight"], "weight"), (c["fall"], "fall speed"),
            (c["squat"], "jump squat")))
    body = (
        '<div class="line">Against a standing %s on %s. No drill is '
        'running: nothing is judged.</div>'
        '<div class="about"/><div class="stats">%s</div>'
        '<div class="grow"/><div class="hints"><div class="hintrow">%s'
        '<div>Pause</div></div><div class="hintrow">%s<div>Back to the menu'
        '</div></div></div>' % (
            esc(opponent), esc(stage), stats, key("START", wide=True),
            key("HOLD START", wide=True)))
    return page("Free play", '<div class="rail">%s<div class="body">%s</div>'
                '</div>' % (head, body), paper=False)
