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


# ---- the course hub -----------------------------------------------------------

def hub(c, course, here, progress, left):
    """`here`: ids of the drills that play in this client. `left`: the
    drill last played, if it is one of this course's."""
    from courses import ABOUT, PARTS
    slabs = []
    for i, part in enumerate(PARTS):
        drills = course["parts"][part]
        done = sum(progress.done(d["id"]) for d in drills)
        plays = sum(d["id"] in here for d in drills)
        nxt = next((d for d in drills if not progress.done(d["id"])), None)
        squares = "".join('<div class="sq%s"/>' % (
            " on" if progress.done(d["id"]) else "") for d in drills)
        slabs.append(
            '<div id="p%d" class="tile slab %s"><div class="ring"/>'
            '<div class="in"><div class="row"><div class="idx">0%d</div>'
            '<div class="grow"/>%s</div><div><div class="big">%s</div>'
            '<div class="q">%s</div><div class="d">%s</div></div><div>'
            '<div class="sqs">%s</div><div class="cnt2">%d of %d done · %d '
            'play here</div><div class="cnt2">Next: %s</div></div></div>'
            '</div>' % (
                i, PART_CLASS[part], i + 1,
                '<div class="first">START HERE</div>' if i == 0 else "",
                part, esc(ABOUT[part][0]), esc(ABOUT[part][1]), squares,
                done, len(drills), plays,
                esc(nxt["name"]) if nxt else "all done"))
    if left:
        tail = (
            '<div class="tile ink grow"><div class="in leftoff"><div>'
            '<div class="lbl">WHERE YOU LEFT OFF</div><div class="big">%s'
            '</div><div class="row"><div class="sq2" style="background-color:'
            ' %s"/><div>%s · drill %d of %d</div></div></div>'
            '<div class="go small"><div class="un">%s<div>Continue</div>'
            '</div></div></div></div>' % (
                esc(left["name"]), PART_COLOR[left["part"]], left["part"],
                left["number"], len(course["parts"][left["part"]]),
                key("X", dark=True)))
    else:
        tail = ('<div class="tile ink grow"><div class="in leftoff"><div>'
                '<div class="lbl">THE COURSE</div><div class="sum">%s</div>'
                '</div></div></div>' % esc(course["summary"]))
    body = (
        header(["Train", c["name"] + "'s course"],
               tag=(c["name"], c["color"], c["fg"])) +
        '<div class="hub"><div class="slabs">' +
        '<div class="gap"/>'.join(slabs) + '</div><div class="gap"/>'
        '<div class="hubrow"><div id="free" class="tile lab"><div class='
        '"ring"/><div class="in"><div class="lbl">FREE PRACTICE</div><div>'
        '<div class="big">Free play</div><div class="sub">Against a standing'
        ' opponent.</div></div></div></div><div class="gap"/>' + tail +
        '</div></div>' +
        footer("", [("A", "Open"), ("B", "Character")],
               tab=PART_COLOR["Tech"]))
    return page("Course hub", body)


# ---- a part's drills ------------------------------------------------------------

ROWS = 8


def _percent(d):
    return "%d%%" % round(100.0 * d["yes"] / d["tries"]) if d["tries"] \
        else "-"


def list_rows(course, part, here, progress, at, top):
    """The rows in view: `at` is the drill in focus, `top` the first row
    shown."""
    out = []
    for i, d in enumerate(course["parts"][part][top:top + ROWS], top):
        p = progress.drill(d["id"])
        out.append(
            '<div class="r%s"><div class="c-n"><div class="cap" style='
            '"background-color: %s"/><div class="num">%d</div></div>'
            '<div class="c-name"><div class="nm">%s</div><div class="gl">%s'
            '</div></div><div class="c-t">%s</div><div class="c-t">%s</div>'
            '<div class="c-b">%s</div><div class="c-h">%s</div><div class='
            '"c-d"><div class="box%s"/><div>%s</div></div></div>' % (
                " on" if i == at else "",
                PART_COLOR[part] if i == at else "#00000000", d["number"],
                esc(d["name"]), esc(d["goal"]),
                p["tries"] if p["tries"] else "-", _percent(p),
                p["best"] if p["tries"] else "-",
                '<div class="plays">PLAYS</div>' if d["id"] in here else "",
                " on" if p["done"] else "", "done" if p["done"] else ""))
    return "".join(out)


def list_detail(course, d, here, progress):
    from courses import refer
    part = d["part"]
    total = len(course["parts"][part])
    size = 52 if len(d["name"]) <= 12 else 38 if len(d["name"]) <= 20 else 28
    fg = "#FFFFFF" if part == "Tech" else "#12161C"
    facts = []
    for label, words in (("Opponent", [d["cpu"]] if d["cpu"] not in
                          ("", "-") else []),
                         ("Builds on", refer(course, d, d["requires"])),
                         ("Leads to", refer(course, d, d["leads"]))):
        if words:
            facts.append('<div class="fact"><div class="fl">%s</div>'
                         '<div class="fv">%s</div></div>' % (
                             label, esc(", ".join(words))))
    done = progress.done(d["id"])
    plays = d["id"] in here
    return (
        '<div class="top" style="background-color: %s"/><div class="slant" '
        'style="background-color: %s"/><div class="head" style="color: %s">'
        '<div class="tags">%s · DRILL %d OF %d</div><div class="dname" '
        'style="font-size: %ddp">%s</div></div><div class="body"><div '
        'class="goal">%s</div>%s<div class="grow"/><div class="donebtn%s">'
        '<div class="box%s"/><div>%s</div><div class="grow"/>%s</div>'
        '<div class="go%s"><div class="un">%s<div>%s</div></div></div></div>'
        % (PART_COLOR[part], PART_COLOR[part], fg, part.upper(),
           d["number"], total, size, esc(d["name"]), esc(d["goal"]),
           "".join(facts), " on" if done else "", " on" if done else "",
           "Done. Press again to undo" if done else "Mark as done",
           key("Y", dark=done), "" if plays else " off",
           key("A", dark=True), "Start" if plays else "Not in this client "
           "yet"))


def drill_list(c, course, part, here, progress, at, top):
    from courses import PARTS
    drills = course["parts"][part]
    tabs = "".join(
        '<div class="ptab %s%s"><div class="un">%s · %d</div></div>' % (
            PART_CLASS[p], " on" if p == part else "", p,
            len(course["parts"][p])) for p in PARTS)
    body = (
        header(["Train", c["name"], part],
               tag=(c["name"], c["color"], c["fg"])) +
        '<div class="tabs">' + key("L", dark=True, wide=True) + tabs +
        key("R", dark=True, wide=True) + '</div>'
        '<div class="listhead"><div class="c-n"><div class="cap"/><div>#'
        '</div></div><div class="c-name">DRILL</div><div class="c-t">TRIES'
        '</div><div class="c-t">SUCCESS</div><div class="c-b">BEST</div>'
        '<div class="c-h">HERE</div><div class="c-d"><div>DONE</div></div>'
        '</div>'
        '<div id="rows" class="rows">' +
        list_rows(course, part, here, progress, at, top) + '</div>'
        '<div id="detail" class="card detail">' +
        list_detail(course, drills[at], here, progress) + '</div>' +
        footer(drills[at]["goal"], [("A", "Start"), ("Y", "Done"),
                                    ("B", "Back")], tab=PART_COLOR[part]))
    return page("Drills", body)


# ---- a drill running --------------------------------------------------------------

CHECK_WORDS = {"target_hit": "You hit them", "not_hit": "You were not hit",
               "target_not_hit": "They were not hit", "hit": "You were hit"}


def check_rows(checks):
    return "".join(
        '<div class="chk"><div class="box%s"/><div>%s</div><div class="grow"/>'
        '<div class="yn">%s</div></div>' % (
            " on" if ch["passed"] else "",
            esc(CHECK_WORDS.get(ch["expect"], ch["expect"])),
            "YES" if ch["passed"] else "NO") for ch in checks)


def last_squares(results):
    """The last ten attempts, oldest first."""
    shown = results[-10:]
    return "".join('<div class="sq3%s"/>' % (" on" if ok else "")
                   for ok in shown) + "".join(
        '<div class="sq3 none"/>' for _ in range(10 - len(shown)))


def drill_rail(c, d, course, about):
    part = d["part"]
    total = len(course["parts"][part])
    fg = "#FFFFFF" if part == "Tech" else "#12161C"
    size = 40 if len(d["name"]) <= 12 else 32 if len(d["name"]) <= 20 else 24
    head = ('<div class="top" style="background-color: %s"/><div class='
            '"slant" style="background-color: %s"/><div class="head" style='
            '"color: %s"><div class="tags">%s · %d OF %d</div><div class='
            '"dname" style="font-size: %ddp">%s</div></div>' % (
                PART_COLOR[part], PART_COLOR[part], fg, part.upper(),
                d["number"], total, size, esc(d["name"])))
    body = (
        '<div class="line">%s</div>'
        '<div class="try"><div class="row"><div class="lbl">THIS TRY</div>'
        '<div class="grow"/><div id="n" class="lbl">0</div></div>'
        '<div id="verdict" class="verdict">Go</div>'
        '<div id="checks"/></div>'
        '<div class="row lastrow"><div class="lbl">LAST 10</div>'
        '<div class="grow"/><div id="count" class="lbl">0 OF 0</div></div>'
        '<div id="last" class="sqs3">%s</div>'
        '<div class="stats two"><div class="stat"><div id="tries" class="n">'
        '0</div><div class="l">tries</div></div><div class="stat"><div '
        'id="rate" class="n">-</div><div class="l">yes</div></div><div '
        'class="stat"><div id="best" class="n">0</div><div class="l">best '
        'run</div></div></div>'
        '<div class="grow"/><div class="hints"><div class="hintrow">%s'
        '<div>Back to the list</div></div></div>' % (
            esc(about), last_squares([]), key("HOLD START", wide=True)))
    banner = ('<div class="bannerwrap"><div id="banner" class="banner">'
              '<div class="chip"><div id="bword" class="un">YES</div></div>'
              '<div class="msg"><div id="bmsg" class="un">.</div></div></div>'
              '</div>')
    return page("Drill", banner + '<div class="rail">%s<div class="body">%s'
                '</div></div>' % (head, body), paper=False)
