"""The client's screens as RmlUi markup (style.rcss has the look).

Each function returns a whole document; client.py writes it to a file and
has the game load it. What changes while a screen is up (which panel has
the focus, the line at the bottom, the character card) is changed in place
by element id.
"""
from pathlib import Path

import art

# The style sheet is named beside the document: client.py copies it there
# (RmlUi takes a path that starts with a slash for one below its own root).
STYLE = Path(__file__).with_name("style.rcss")
# The character select's panels in a row (the arrows move by it too)
COLUMNS = 7
PART_CLASS = {"Tech": "tech", "Punish": "punish", "Defense": "defense",
              "Neutral": "neutral"}
PART_COLOR = {"Tech": "#1F49C9", "Punish": "#F0643C", "Defense": "#22B8A0",
              "Neutral": "#F5BE1B"}
# The menu panels' large faded drawings (marks.py): name -> picture, which
# panel has which, and the panels light enough to have it in faint ink
# (faint white on the rest). Without the pictures, no drawings.
MARKS = {}
MARK_OF = {"versus": "versus", "train": "train", "settings": "settings",
           "vlocal": "controller", "vonline": "globe",
           "scontrols": "controller", "sonline": "globe",
           "ssound": "speaker", "sdisplay": "monitor", "lab": "lab",
           "p0": "tech", "p1": "punish", "p2": "defense", "p3": "neutral"}
LIGHT = ("white", "punish", "defense", "neutral")


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;")


def page(title, body, paper=True):
    return ('<rml><head><title>%s</title>'
            '<link type="text/rcss" href="style.rcss"/></head>'
            '<body class="%s">%s</body></rml>' % (
                esc(title), "paper" if paper else "", body))


def over_game():
    """What goes over the game's picture in a match or a drill: the pause
    menu, the verdict banner. Each has an id so the column can be hidden
    and these moved to the middle (Client.toggle_column). (No loading
    cover: a match loads unseen, the window keeping its last picture:
    Client.load_quietly.)"""
    return (
        '<div id="rays" class="rays"/>'
        '<div id="bannerwrap" class="bannerwrap"><div id="banner" '
        'class="banner"><div id="chip" class="chip"><div id="bword" '
        'class="un">YES</div></div><div class="msg"><div id="bmsg" '
        'class="un">.</div></div></div></div>'
        '<div id="pause" class="pause"><div class="pdim"/><div '
        'class="pshade"/><div class="psheet"/><div class="pcol"><div '
        'id="ptags" class="ptags"/><div id="ptitle" class="ptitle">Paused'
        '</div><div id="ptabs" class="ptabs"/><div id="prows" class='
        '"prows"/><div id="pnav" class="pnav"/><div class="grow"/><div '
        'class="phint">%s<div>Choose</div>%s<div>Change</div>%s<div>Back'
        '</div></div></div></div>'
        '<div id="coach" class="coach"/>'
        '<div id="replay" class="replay"/>'
        % (key("A"), key("D-SIDE"), key("B")))


def rays(points):
    """Light rays coming down on the stage (a drill's targets): `points`
    are where each meets the floor in the game's picture, in dp."""
    return "".join(
        '<div class="ray" style="left: %ddp; height: %ddp;"/>'
        '<div class="rayfoot" style="left: %ddp; top: %ddp;"/>'
        % (x - 9, y, x - 22, y - 5) for x, y in points)


def online_page(code, rows, at, status, delay=2, router=None):
    """Playing a friend online: this side's code as a ticket, pasting a
    friend's, the friends met (rows: (id, label, detail); "copy", "paste",
    then the friends), `at` the one in focus; `status` in the footer. (The
    owner, 2026-11-13: no more plain menus, "i.e. the front code is a
    white box"; the canvas's "Versus: online".)"""
    return page("Online", (
        header(["Main menu", "Versus", "Online"]) +
        '<div id="orows" class="onl2">%s</div>' % online_body(
            code, rows, at, delay, router) +
        '<div class="footer"><div class="tab" style="background-color: '
        '#22B8A0"/><div id="ostatus" class="desc">%s</div><div class="grow"/>'
        '<div class="row">%s</div></div>' % (
            esc(status), hint_keys([("A", "Choose"), ("B", "Back")]))))


def online_body(code, rows, at, delay=2, router=None):
    """What online_page shows between the header and the footer; redrawn
    as the focus moves."""
    focus = rows[at][0] if rows else None
    groups = (code.split("-") if "-" in code else
              [code[i:i + 5] for i in range(0, len(code), 5)]) or [code]
    lines = [groups[:3], groups[3:]]
    code_html = "".join(
        '<div class="tline">%s</div>' % "".join(
            '<div class="tg%s">%s</div>' % (" alt" if (i + j) % 2 else "",
                                            esc(g))
            for j, g in enumerate(line))
        for i, line in enumerate(l for l in lines if l))
    perf = "".join('<div class="tperf"/>' for _ in range(9))
    ticket = (
        '<div class="ticket%s"><div class="tring"/><div class="tbody">'
        '<div class="row"><div class="tl">YOUR CODE</div><div class="grow"/>'
        '<div class="tl">A COPIES IT</div></div><div class="tcode">%s</div>'
        '<div class="tsub">Send it to your friend; paste theirs below.</div>'
        '</div><div class="tperfs">%s</div><div class="tstub"><div class="un">'
        '<div class="tadmit">ADMIT</div><div class="tadmit">ONE</div></div>'
        '</div></div>' % (" on" if focus == "copy" else "", code_html, perf))
    if router:
        rt, rw = "Router: " + router[0].lower(), router[1]
    else:
        rt, rw = ("Router: not checked",
                  "Settings, Online, Router checks it.")
    strip = (
        '<div class="ostrip"><div class="orouter"><div class="ort">%s</div>'
        '<div class="orw">%s</div></div><div class="odelay"><div '
        'class="sed">DELAY</div><div class="odv">%s</div></div></div>' % (
            esc(rt), esc(rw[:70] + ("..." if len(rw) > 70 else "")),
            "%d FRAME%s" % (delay, "" if delay == 1 else "S") if delay
            else "OFF"))
    paste = (
        '<div class="paste%s"><div class="un"><div class="pbig">Paste a '
        'friend\'s code</div><div class="psub">Or an address and port, like '
        '100.64.0.7:47700.</div></div></div>' % (
            " on" if focus == "paste" else ""))
    friends = [(i, r) for i, r in enumerate(rows)
               if r[0].startswith("friend")]
    colours = ("#5B3FD6", "#FF5C93", "#F5BE1B", "#1F49C9", "#F0643C")
    cards = "".join(
        '<div class="ofc%s"><div class="oini" style="background-color: %s">'
        '<div class="un">%s</div></div><div class="col"><div class="ofn">%s'
        '</div><div class="ofw">%s</div></div></div>' % (
            " on" if i == at else "", colours[k % len(colours)],
            esc(r[1][:2].upper()), esc(r[1]), esc(r[2]))
        for k, (i, r) in enumerate(friends[:5]))
    if not cards:
        cards = ('<div class="ofnone">Nobody yet. A friend you play is kept '
                 'here, to play again with A.</div>')
    return (
        '<div class="oleft">%s%s%s</div><div class="oright"><div class="row">'
        '<div class="ofh">Friends</div><div class="grow"/><div class="sed '
        'dk">%d MET ONLINE</div></div>%s</div>' % (
            ticket, strip, paste, len(friends), cards))


# The pause menu's icons (icons.py): name -> picture. Without them, rows
# have none.
ICONS = {}


def icon(name, cls="picon"):
    if name not in ICONS:
        return ""
    return '<img class="%s" src="%s"/>' % (cls, picture(ICONS[name]))


def pause_tabs(tabs, on):
    """The sheet's tabs, L and R either side (the canvas's "Paused: icons
    and the input display")."""
    if len(tabs) < 2:
        return ""
    return (key("L") + "".join(
        '<div class="ptb%s"><div class="un">%s</div></div>' % (
            " on" if t == on else "", esc(t)) for t in tabs) + key("R"))


def pause_rows(rows, at):
    """The sheet's rows: (id, label, value or None, icon); `at` the row in
    focus (None: the drills' buttons below have it). Many rows are drawn
    closer together."""
    tight = " tight" if len(rows) > 9 else ""
    out = []
    for i, (ident, label, value, ic) in enumerate(rows):
        on = i == at
        val = ""
        if value is not None:
            val = '<div class="pval">%s<div>%s</div>%s</div>' % (
                icon("left", "parr"), esc(value), icon("right", "parr"))
        out.append(
            '<div class="pr%s%s"><div class="pcap"/>%s<div class="pl">%s'
            '</div><div class="grow"/>%s</div>' % (
                " on" if on else "", tight, icon(ic), esc(label), val))
    return "".join(out)


def pause_nav(before, after, at):
    """The drills before and after, as two buttons under the rows; `at`
    0 or 1 for the one in focus, None for neither."""
    if before is None:
        return ""
    return "".join(
        '<div class="pnb%s%s"><div class="un pnu"><div class="pnl">%s</div>'
        '<div class="pnn">%s</div></div></div>' % (
            " on" if at == i else "", " right" if i else "", word,
            esc(name if len(name) <= 24 else name[:23].rstrip() + "…"))
        for i, (word, name) in enumerate((("PREVIOUS DRILL", before),
                                          ("NEXT DRILL", after))))


def hint_rows(rows):
    """(buttons, what they do) rows: the buttons drawn as the GameCube
    controller's, several to a row ("L R")."""
    return "".join(
        '<div class="hintrow"><div class="glyphs">%s</div><div>%s</div>'
        '</div>' % ("".join(key(b) for b in buttons.split()), esc(what))
        for buttons, what in rows)


def match_hints(drill=False, stages=False):
    """The sidebar's controls: in a drill three, side by side at its foot
    (the owner, 2026-11-14: "We don't need the button guides. Let's just
    pin three hints to the bottom in one row so it doesn't take up too much
    screen. Let's use Dpad up for tutorial and then keep scenario and hold:
    change drill hints, but get rid of pause and hide sidebar"); in a match
    none (START still pauses, and held hides the sidebar). `stages` is no
    longer shown (L or R held still changes the stage)."""
    if not drill:
        return ""
    return '<div class="hbar">%s</div>' % "".join(
        '<div class="hcell"><div class="glyphs">%s</div><div class="hl">%s'
        '</div></div>' % (key(b), esc(what))
        for b, what in (("D-UP", "Tutorial"), ("D-SIDE", "Scenario"),
                        ("D-SIDE", "Hold: change drill")))


# The GameCube controller's buttons, as they look on it: A green and large,
# B red, X and Y grey kidneys, Z purple, the triggers grey, START a small
# grey button, the D-pad a cross with the arm meant lit.
GLYPH = {"A": "a", "B": "b", "X": "x", "Y": "y", "Z": "z", "L": "lt",
         "R": "rt", "C": "c", "START": "st"}
DPAD = {"D-UP": ("up",), "D-DOWN": ("down",), "D-LEFT": ("left",),
        "D-RIGHT": ("right",), "D-SIDE": ("left", "right"),
        "SIDE": ("left", "right"), "D-PAD": ()}


# SmashWiki's GameCube button icons, when the client could fetch them
# (buttons.py): button name -> picture. Without them, the glyphs above.
BUTTONS = {}


def key(letter, dark=False, wide=False):
    """A button: a GameCube button as SmashWiki's icon of it (or drawn as
    one), a D-pad direction as the cross, anything else (a keyboard's key) as
    a key cap. `dark`: the button sits on a light panel (START's label is
    then dark; a key cap's edge too). `wide`: a key cap's."""
    name = letter.upper()
    if name == "SIDE":
        name = "D-SIDE"
    icon = name
    if name == "START" and not dark:
        icon = "START-LIGHT"
    if icon in BUTTONS:
        return '<img class="gcimg %s" src="%s"/>' % (
            name.lower(), picture(BUTTONS[icon]))
    if name in GLYPH:
        label = "START" if name == "START" else name
        return '<div class="gc %s"><div>%s</div></div>' % (GLYPH[name],
                                                            label)
    if name in DPAD:
        arms = "".join('<div class="arm %s"/>' % a for a in DPAD[name])
        return ('<div class="dpad"><div class="v"/><div class="h"/>%s</div>'
                % arms)
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
    # one tag, or the two sides of a match ([(text, colour, ink), ...])
    for i, t in enumerate([tag] if isinstance(tag, tuple) else tag or []):
        if i:
            who += '<div class="hvs">VS</div>'
        who += ('<div class="tag" style="background-color: %s; color: %s">'
                '<div class="un">%s</div></div>' % (t[1], t[2], esc(t[0])))
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

# (The owner, 2026-11-14: "Versus should replace the Train tile, then Train
# should replace Lab"; the Lab went into Train, in place of free play; and
# Events out, Training Mode's events to come back as drills in Train.)
MAIN = [
    # id, class, name, what it is, built in this client
    ("versus", "red", "Versus",
     "A match against a trained model, the game's CPU, or a friend.", True),
    ("train", "ink", "Train", "Your character's course, and the Lab.", True),
    ("settings", "white", "Settings",
     "Controls, input delay, sound, display and online.", True),
]


def mark(ident, cls):
    """A panel's large faded drawing, cut by the panel's edges."""
    name = MARK_OF.get(ident)
    if name not in MARKS:
        return ""
    tint = "#12161C24" if cls in LIGHT else "#FFFFFF2B"
    return ('<div class="mkclip"><img class="mk" src="%s" style="image-color:'
            ' %s"/></div>' % (picture(MARKS[name]), tint))


def _tile(item, extra=""):
    """A panel. (No number in its corner: the owner, 2026-11-13, "I don't
    like the numbered buttons, there's no point to doing that!")"""
    ident, cls, name, about, built = item
    soon = "" if built else '<div class="soon">NOT YET</div>'
    return ('<div id="%s" class="tile %s"><div class="ring"/>%s'
            '<div class="in"><div class="row">'
            '<div class="grow"/>%s</div><div><div class="big">%s</div>'
            '<div class="sub">%s</div>%s</div></div>%s</div>' % (
                ident, cls, mark(ident, cls), soon, esc(name), esc(about),
                extra[0] if extra else "", extra[1] if extra else ""))


def _last(text, colour, ink="#12161C"):
    return ('<div class="last"><div class="mark" style="background-color: '
            '%s; color: %s">LAST</div><div>%s</div></div>' % (
                colour, ink, esc(text)))


def main_menu(last=None, match=None, focus="versus"):
    """`last`: (character name, colour) of the last one trained, if any;
    `match`: what the last Versus match was, in words."""
    by = {item[0]: item for item in MAIN}
    bands = '<div class="bands">%s</div>' % "".join(
        '<div class="band %s"><div class="un">%s</div></div>' % (
            PART_CLASS[p], p) for p in PART_CLASS)
    sides = ('<div class="bands"><div class="band vl"><div class="un">Local'
             '</div></div><div class="band vo"><div class="un">Online</div>'
             '</div></div>')
    gap = '<div class="gap"/>'
    body = (
        header(["Main menu"]) +
        '<div class="mosaic">' +
        _tile(by["versus"], (_last(match, "#12161C", "#F3F6FA")
                             if match else "", sides)) + gap +
        '<div class="right">' +
        _tile(by["train"], (_last(*last) if last else "", bands)) + gap +
        _tile(by["settings"]) + '</div></div>' +
        footer(by[focus][3], [("A", "Choose"), ("F11", "Fullscreen")],
               tab="#D0283E" if focus == "versus" else "#F3F6FA"))
    return page("Main menu", body)


# ---- versus: local or online ------------------------------------------------------

VERSUS = [
    ("vlocal", "slate", "Local",
     "On this machine: against a trained model, the game's CPU, or "
     "nobody.", True),
    ("vonline", "ink", "Online",
     "Against a friend over the internet: swap codes, no server in "
     "between.", True),
]


def versus_menu(focus):
    body = (
        header(["Main menu", "Versus"]) +
        '<div class="mosaic vmosaic">' + _tile(VERSUS[0]) +
        '<div class="gap"/>' + _tile(VERSUS[1]) + '</div>' +
        footer(next(v[3] for v in VERSUS if v[0] == focus),
               [("A", "Choose"), ("B", "Back")]))
    return page("Versus", body)


# ---- character select -----------------------------------------------------------

def picture(path):
    """An image's source in a document: the file itself, wherever the
    document was written (RmlUi passes a file: URL on as it is)."""
    return "file://" + str(Path(path).resolve())


def _portrait(c, n=0):
    return art.portrait(c["id"], n) or (art.portrait(c["id"], 0)
                                        if n else None)


def _tint(c, alone=False, big=False):
    """The emblem behind the picture: a shade darker on a light colour,
    lighter on a dark one; plain to see where there is no picture."""
    light = c["fg"] != "#FFFFFF"
    if alone:
        a = 0x80 if light else 0x99
    else:
        a = 0x2E if light else (0x38 if big else 0x33)
    return ("#12161C%02X" if light else "#FFFFFF%02X") % a


def _name_size(name):
    longest = max(len(w) for w in name.split())
    return 64 if longest <= 4 else 52 if longest <= 6 else \
        40 if longest <= 8 else 32


def tile(c):
    """The inside of a character's panel: its emblem, its portrait (the
    default costume), its name; the part colours if it has a course."""
    face = _portrait(c)
    emb = art.emblem(c["series"])
    inner = ""
    if emb is not None:
        inner += ('<img class="wm" src="%s" style="image-color: %s"/>' % (
            picture(emb), _tint(c, face is None)))
    if face is not None:
        inner += ('<img class="face" src="%s" style="top: %.1fdp"/>' % (
            picture(face), 2 - (c["face"] + art.PAD) * 0.86))
    course = ""
    if c["course"]:
        course = '<div class="course">%s</div>' % "".join(
            '<div style="background-color: %s"/>' % PART_COLOR[p]
            for p in PART_COLOR)
    return ('<div class="ring"/><div class="pic"><div class="pin">%s</div>'
            '%s<div class="strip"><div class="un">%s</div></div></div>' % (
                inner, course, esc(c["short"])))


def art_head(c, costume=0):
    """The top of a character's card: its colour, its emblem, its portrait
    inside the card's top, behind a wall and a post, its traits and name."""
    face = _portrait(c, costume)
    emb = art.emblem(c["series"])
    out = ('<div class="aclip"><div class="acolor" style="background-color:'
           ' %s"/>' % c["color"])
    if emb is not None:
        out += '<img class="awm" src="%s" style="image-color: %s"/>' % (
            picture(emb), _tint(c, face is None, big=True))
    out += '</div>'
    if face is not None:
        out += '<img class="abig" src="%s"/>' % picture(face)
    # the portrait behind a wall (the owner's pick of the canvas's "A ·
    # Card: behind a wall", 2026-11-14, "but I also want a line in between
    # the character and the name so we can hide the cutoff right side"):
    # the wall's shadow and the post's on the character, the wall with its
    # lit top face, the post upright (the portraits' cut is upright); all
    # inside the card ("I don't want a line bleeding out of the
    # container")
    out += ('<div class="ashade"><div class="wshadow"/><div class="postsh"/>'
            '</div><div class="wclip"><div class="wedge"/></div>'
            '<div class="wfclip"><div class="wface"/><div class="wlip"/></div>'
            '<div class="post"/><div class="plip"/>')
    out += ('<div class="aname" style="color: %s"><div class="tags">%s</div>'
            '<div class="who2" style="font-size: %ddp">%s</div></div>' % (
                c["fg"], esc(" · ".join(c["tags"]).upper()),
                _name_size(c["name"]), esc(c["name"])))
    return out


def costume_row(c, costume, form_key):
    """Costume chips (Y), and the other character of a shared place
    (`form_key`) as a button."""
    chips = ""
    for n in range(c["costumes"]):
        face = art.portrait(c["id"], n)
        img = ('<img class="cimg" src="%s" style="top: %.1fdp"/>' % (
            picture(face), -1 - (c["face"] + art.PAD) * 0.4)) if face else ""
        chips += ('<div class="cchip%s" style="background-color: %s">'
                  '<div class="cpin">%s</div></div>' % (
                      " on" if n == costume else "", c["color"], img))
    form = ""
    if c.get("other") is not None and form_key:
        form = ('<div class="grow"/><div class="form"><div class="un">%s'
                '<div>%s</div></div></div>' % (key(form_key),
                                              esc(c["other"]["name"])))
    return '<div class="cos">%s%s%s</div>' % (key("Y"), chips, form)


def card(c, costume=0):
    """The inside of the card about one character: the head, then its
    numbers, its course, its costumes and (Zelda and Sheik) the other."""
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
        about = ('<div class="about">A course of its own: %d drills.</div>'
                 '<div class="parts">%s</div>' % (sum(counts.values()),
                                                  parts))
        go = "Train"
    else:
        about = ('<div class="about">No course of its own yet: A opens the '
                 'Lab.</div>')
        go = "Lab"
    return art_head(c, costume) + (
        '<div class="abody"><div class="stats">%s</div>%s%s<div class="grow"/>'
        '<div class="go"><div class="un">%s<div>%s</div></div></div></div>' % (
            stats, about, costume_row(c, costume, "X"), key("A", dark=True),
            go))


def character_select(roster, focus, title="Choose your character",
                     about="Choose who you train. A drill brings its own "
                           "opponents.", inside=None, hints=None,
                     costume=0):
    """`inside`: the card's content, if not the usual one about the
    character in focus (in `costume`)."""
    tiles = []
    for i, c in enumerate(roster):
        tiles.append('<div id="c%d" class="char%s" style="background-color: '
                     '%s">%s</div>' % (i, " focus" if i == focus else "",
                                       c["color"], tile(c)))
    # a row of its own for each COLUMNS panels: wrapped in one box, a
    # window whose scale rounded a panel up by a pixel wrapped them six to
    # a row, and the last place fell below the screen
    rows = "".join('<div class="rrow">%s</div>' % "".join(
        tiles[i:i + COLUMNS]) for i in range(0, len(tiles), COLUMNS))
    body = (
        header([title]) +
        '<div class="roster">' + rows + '</div>' +
        '<div id="card" class="card art">' +
        (inside or card(roster[focus], costume)) + '</div>' +
        footer(about, hints or [("A", "Choose"), ("Y", "Costume"),
                                ("B", "Back")],
               tab=roster[focus]["color"]))
    return page("Character select", body)


# ---- versus and lab: who is on the other side ---------------------------------

def opponent_card(c, who, what, count, go):
    """The card on the opponent screen: the character, who plays it (`who`,
    with `what` that is in a few words; `count`: "2 of 31"). The stage is
    chosen next, on a screen of its own."""
    form = ""
    if c.get("other") is not None:
        form = ('<div class="pick">%s<div>Switch to %s</div></div>' % (
            key("Y"), esc(c["other"]["name"])))
    return art_head(c) + (
        '<div class="body low"><div class="fact"><div class="fl">Played by'
        '</div><div class="fv big2">%s</div><div class="fl">%s</div></div>'
        '<div class="pick">%s<div>Change</div><div class="grow"/>'
        '<div class="lbl">%s</div></div>%s'
        '<div class="grow"/><div class="go"><div class="un">%s<div>%s</div>'
        '</div></div></div>' % (
            esc(who), esc(what), key("X"), esc(count), form,
            key("A", dark=True), esc(go)))


# ---- the stage select (the canvas's "A · Stage select: grid and card") -------

STAGE_COLUMNS = 3


def stage_tile(i, s, focus):
    """A stage's panel: the native build's picture of it from above and to
    one side, or (until that is drawn) the game's name logo."""
    import stages
    pic = stages.tile(s["id"])
    if pic is not None:
        inner = '<img class="sgimg" src="%s"/>' % picture(pic)
    else:
        name = stages.logo(s["id"])
        inner = '<img class="sglogo" src="%s"/>' % picture(name) \
            if name is not None else ""
    return ('<div id="s%d" class="sg%s"><div class="ring"/><div class="sgpic">'
            '<div class="sgpin">%s</div><div class="sgstrip"><div class="un">'
            '%s</div></div></div></div>' % (
                i, " focus" if focus else "", inner,
                # (RmlUi's text-transform leaves the é of Pokémon small)
                esc(s["name"].upper())))


def _num(v):
    return "%g" % round(v, 1)


def stage_card(s, go):
    """The card about the stage in focus: the stage whole, the game's name
    logo, its width and platforms, its blast zones (as the game reads
    them, once drawn), a line about it."""
    import stages
    out = '<div class="sgclip">'
    prev = stages.preview(s["id"])
    if prev is not None:
        out += '<img class="sgprev" src="%s"/>' % picture(prev)
    out += '</div><div class="wclip"><div class="wedge"/></div>'
    name = stages.logo(s["id"])
    if name is not None:
        out += '<img class="sgname" src="%s"/>' % picture(name)
    else:
        out += '<div class="sgname2">%s</div>' % esc(s["name"])
    f = stages.facts().get(s["id"])
    stats = []
    if f:
        stats.append((_num(2 * f["ledge"]), "ledge to ledge"))
    stats.append((str(s["platforms"]) if s["platforms"] else "None",
                  "platforms"))
    stats = "".join('<div class="stat"><div class="n">%s</div><div class="l">'
                    '%s</div></div>' % (esc(n), what) for n, what in stats)
    blast = ""
    if f:
        blast = ('<div class="sgblast"><div class="fl">Blast zones</div>'
                 '<div class="sgbz">%s</div></div>' % "".join(
                     '<div class="sgb"><div class="sgbn">%s</div><div '
                     'class="sgbl">%s</div></div>' % (_num(v), side)
                     for v, side in zip(f["blast"], ("left", "right", "top",
                                                     "bottom"))))
    return out + (
        '<div class="sgbody"><div class="sgstats">%s</div>%s<div '
        'class="sgabout">%s</div><div class="grow"/><div class="go"><div '
        'class="un">%s<div>%s</div></div></div></div>' % (
            stats, blast, esc(s["about"]), key("A", dark=True), esc(go)))


def stage_select(stage_list, focus, me, opp, go):
    """After the characters: where they play. `me`, `opp`: the two
    characters; `go`: what A does ("Fight", or "Start" in the Lab)."""
    tiles = [stage_tile(i, s, i == focus) for i, s in enumerate(stage_list)]
    rows = "".join('<div class="sgrow">%s</div>' % "".join(
        tiles[i:i + STAGE_COLUMNS])
        for i in range(0, len(tiles), STAGE_COLUMNS))
    body = (
        header(["Choose a stage"], tag=[(me["name"], me["color"], me["fg"]),
                                        (opp["name"], opp["color"],
                                         opp["fg"])]) +
        '<div class="sgrid">' + rows + '</div>' +
        '<div id="card" class="card">' + stage_card(stage_list[focus], go) +
        '</div>' +
        footer("Where %s and %s play. The stage loads with the match." % (
            me["name"], opp["name"]),
            [("A", go), ("X", "Random"), ("B", "Back")]))
    return page("Stage select", body)


def versus_rail(c, opp, who, what, stage, lab):
    """The column beside a match in Versus or the Lab."""
    head = ('<div class="top" style="background-color: %s"/>'
            '<div class="slant" style="background-color: %s"/>'
            '<div class="head" style="color: %s"><div class="tags">%s</div>'
            '<div class="who2" style="font-size: %ddp">%s</div></div>' % (
                c["color"], c["color"], c["fg"], "LAB" if lab else "VERSUS",
                34 if len(c["name"]) > 9 else 48, esc(c["name"])))
    tools = ""
    if lab:
        tools = hint_rows((("D-DOWN", "Reset positions"),
                           ("D-LEFT", "Opponent damage -10"),
                           ("D-RIGHT", "Opponent damage +10")))
    body = (
        '<div class="fact"><div class="fl">Against</div><div class="fv big2">'
        '%s</div></div><div class="fact"><div class="fl">Played by</div>'
        '<div class="fv">%s</div><div class="fl">%s</div></div>'
        '<div class="fact"><div class="fl">Stage</div><div class="fv">%s'
        '</div></div><div id="botstate" class="line botstate"/>'
        '<div class="grow"/><div class="hints">%s</div>%s' % (
            esc(opp["name"]), esc(who), esc(what), esc(stage), tools,
            match_hints()))
    return page("Versus", over_game() + '<div id="rail" class="rail">%s'
                '<div class="body">%s</div></div>' % (head, body), paper=False)


# ---- the course hub -----------------------------------------------------------

# (The owner, 2026-11-14: "move Lab into Train, it should replace the free
# play button".)
LAB = ("lab", "lab", "Lab", "Any opponent, any stage. Nothing is judged.",
       True)


def hub(c, course, here, progress, left):
    """`here`: ids of the drills that play in this client. `left`: the
    drill last played, if it is one of this course's."""
    from courses import ABOUT, PARTS
    slabs = []
    for i, part in enumerate(PARTS):
        drills = course["parts"][part]
        done = sum(progress.done(d["id"]) for d in drills)
        nxt = next((d for d in drills if not progress.done(d["id"])), None)
        squares = "".join('<div class="sq%s"/>' % (
            " on" if progress.done(d["id"]) else "") for d in drills)
        slabs.append(
            '<div id="p%d" class="tile slab %s"><div class="ring"/>%s'
            '<div class="in"><div class="row">'
            '<div class="grow"/>%s</div><div><div class="big">%s</div>'
            '<div class="d">%s</div></div><div>'
            '<div class="sqs">%s</div><div class="cnt2">%d of %d complete'
            '</div><div class="cnt2">Next: %s</div></div></div>'
            '</div>' % (
                i, PART_CLASS[part], mark("p%d" % i, PART_CLASS[part]),
                '<div class="first">START HERE</div>' if i == 0 else "",
                part, esc(ABOUT[part][0]), squares, done, len(drills),
                esc(nxt["name"]) if nxt else "complete"))
    if left:
        tail = (
            '<div class="tile ink grow"><div class="in leftoff"><div>'
            '<div class="lbl">LAST PLAYED</div><div class="big">%s'
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
        header(["Train", c["name"]],
               tag=(c["name"], c["color"], c["fg"])) +
        '<div class="hub"><div class="slabs">' +
        '<div class="gap"/>'.join(slabs) + '</div><div class="gap"/>'
        '<div class="hubrow">' + _tile(LAB) + '<div class="gap"/>' + tail +
        '</div></div>' +
        footer("", [("A", "Open"), ("B", "Back")],
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
            '<div class="c-b">%s</div><div class='
            '"c-d"><div class="box%s"/><div>%s</div></div></div>' % (
                " on" if i == at else "",
                PART_COLOR[part] if i == at else "#00000000", d["number"],
                esc(d["name"]), esc(d["goal"]),
                p["tries"] if p["tries"] else "-", _percent(p),
                p["best"] if p["tries"] else "-",
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
        '<div class="c-d"><div>DONE</div></div>'
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


def timeline(tl):
    """A tech drill's attempt frame by frame: a row for each input, the
    frames it was pressed on, where it was due and what is allowed."""
    if not tl:
        return ""
    n = tl["frames"]
    labels = tl.get("labels") or [
        # a long attempt has no room for every number
        str(i) if n <= 12 or i % 5 == 0 else "" for i in range(1, n + 1)]
    head = "".join('<div class="tlc tln">%s</div>' % label
                   for label in labels)
    rows = ['<div class="tlrow"><div class="tll"/>%s</div>' % head]
    for row in tl["rows"]:
        cells = []
        for i in range(1, n + 1):
            cls = "tlc"
            if row["window"] and row["window"][0] <= i <= row["window"][1]:
                cls += " win"
            if i in row["perfect"]:
                cls += " perf"
            if i in row["you"]:
                cls += " you"
            cells.append('<div class="%s"/>' % cls)
        rows.append('<div class="tlrow"><div class="tll">%s</div>%s</div>'
                    % (esc(row["label"]), "".join(cells)))
    legend = ('<div class="tlleg"><div class="tlc you"/><div>you</div>'
              '<div class="tlc perf"/><div>frame-perfect</div>'
              '<div class="tlc win"/><div>allowed</div></div>')
    return "".join(rows) + legend + '<div class="tlnote">%s</div>' % esc(
        tl.get("note", ""))


def last_squares(results):
    """The last ten attempts, oldest first."""
    shown = results[-10:]
    return "".join('<div class="sq3%s"/>' % (" on" if ok else "")
                   for ok in shown) + "".join(
        '<div class="sq3 none"/>' for _ in range(10 - len(shown)))


def drill_rail(c, d, course, about, stages=None):
    """The column beside a drill. `stages`: the drill's stages when it can
    change them (with the one it is on first)."""
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
        '<div id="status" class="line now"/>'
        '<div class="try"><div class="row"><div class="lbl">THIS TRY</div>'
        '<div class="grow"/><div id="n" class="lbl">0</div></div>'
        '<div id="verdict" class="verdict">Go</div>'
        '<div id="why" class="why"/><div id="checks"/><div id="tl"/></div>'
        '<div class="row lastrow"><div class="lbl">LAST 10</div>'
        '<div class="grow"/><div id="count" class="lbl">0 OF 0</div></div>'
        '<div id="last" class="sqs3">%s</div>'
        '<div class="stats two"><div class="stat"><div id="tries" class="n">'
        '0</div><div class="l">tries</div></div><div class="stat"><div '
        'id="rate" class="n">-</div><div class="l">success</div></div><div '
        'class="stat"><div id="best" class="n">0</div><div class="l">best '
        'run</div></div></div>'
        '<div class="grow"/>%s%s' % (
            esc(about), last_squares([]),
            '<div id="stage" class="line stageline">Stage: %s</div>' % esc(
                stages[0].replace("-", " ").title()) if stages else "",
            match_hints(drill=True, stages=bool(stages))))
    return page("Drill", over_game() + '<div id="rail" class="rail">%s'
                '<div class="body">%s</div></div>' % (head, body),
                paper=False)


# ---- settings ---------------------------------------------------------------
#
# The design: the canvas's "Settings" row (Settings, Controls, Controls:
# input delay, Controls: rumble). The owner, 2026-11-13: "Frame delay
# should just be a suboption in Controls I feel, make Controls the
# headliner", and "make sure that we have rumble support in controls".

SETTINGS = [
    # id, class, name, what it is, built in this client
    ("scontrols", "tech", "Controls",
     "Input delay, rumble and UCF. Button layouts for each port and "
     "nickname come next.", True),
    ("sonline", "defense", "Online",
     "Your nickname, your code's port, friends, your router.", True),
    ("ssound", "punish", "Sound", "Music, effects and menu sounds.", True),
    ("sdisplay", "neutral", "Display",
     "Fullscreen, the sidebar, the window's size.", True),
]
PORT_COLOR = ("#F0643C", "#1F49C9", "#F5BE1B", "#22B8A0")


def settings_menu(focus, chips):
    """The Settings panels, Controls the big one. `chips`: (label, value,
    class) for the strip along the bottom of Controls."""
    by = {item[0]: item for item in SETTINGS}
    strip = '<div class="bands chips">%s</div>' % "".join(
        '<div class="band %s"><div class="un"><div class="clbl">%s</div>'
        '<div class="cval">%s</div></div></div>' % (cls, esc(label),
                                                    esc(value))
        for label, value, cls in chips)
    gap = '<div class="gap"/>'
    body = (
        header(["Main menu", "Settings"]) +
        '<div class="mosaic">' + _tile(by["scontrols"], ("", strip)) + gap +
        '<div class="right">' + _tile(by["sonline"]) + gap +
        '<div class="lower">' + _tile(by["ssound"]) + gap +
        _tile(by["sdisplay"]) + '</div></div></div>' +
        footer(by[focus][3], [("A", "Choose"), ("B", "Back")],
               tab="#1F49C9"))
    return page("Settings", body)


def hint_keys(hints):
    return "".join('<div class="hint">%s<div>%s</div></div>' % (
        key(k, wide=len(k) > 1), esc(what)) for k, what in hints)


def controls_rows(rows, at):
    """rows: (id, name, what it is, value, colour of its mark)."""
    return "".join(
        '<div class="srow%s"><div class="cap" style="background-color: %s"/>'
        '<div class="c-name"><div class="nm">%s</div><div class="gl">%s'
        '</div></div><div class="sv">%s</div></div>' % (
            " on" if i == at else "", colour, esc(name), esc(about),
            esc(value))
        for i, (ident, name, about, value, colour) in enumerate(rows))


def settings_page(name, colour, rows, at, panel, desc, hints):
    """Settings / `name`: the rows on the left, the one in focus edited in
    the dark panel beside them; `colour` the section's."""
    body = (
        header(["Main menu", "Settings", name]) +
        '<div id="slist" class="slist">%s</div>' % controls_rows(rows, at) +
        '<div id="spanel" class="spanel">%s</div>' % panel +
        '<div class="footer"><div class="tab" style="background-color: '
        '%s"/><div id="desc" class="desc">%s</div><div class="grow"/>'
        '<div id="fh" class="row">%s</div></div>' % (
            colour, esc(desc), hint_keys(hints)))
    return page(name, body)


def controls_page(rows, at, panel, desc, hints):
    return settings_page("Controls", "#1F49C9", rows, at, panel, desc, hints)


def _panel_head(title, right):
    return ('<div class="shd"><div><div class="sed">EDITING</div>'
            '<div class="stl">%s</div></div><div class="grow"/>'
            '<div class="sright">%s</div></div>' % (esc(title), esc(right)))


LANE_CELLS = 13


def delay_panel(frames, most):
    """Input delay: the number of frames, big, and what the game sees of a
    jab pressed on frame 0."""
    ms = frames * 1000.0 * 1001 / 60000
    chip = ("SLIPPI'S DEFAULT" if frames == 2 else
            "NO DELAY" if frames == 0 else
            "%d MORE THAN SLIPPI'S" % (frames - 2) if frames > 2 else
            "1 LESS THAN SLIPPI'S")
    sub = ("The console as it is." if frames == 0 else
           "Off is the console as it is.")

    def lane(name, cls_text):
        return ('<div class="lane"><div class="ll">%s</div>%s</div>' % (
            esc(name), "".join(
                '<div class="lc %s"><div class="un">%s</div></div>' % (c, t)
                for c, t in cls_text)))

    ruler = ('<div class="lane nums"><div class="ll lbl">FRAME</div>%s</div>'
             % "".join('<div class="lc n"><div class="un">%d</div></div>' % i
                       for i in range(LANE_CELLS)))
    press = [("press", "A") if i == 0 else ("", "")
             for i in range(LANE_CELLS)]
    held = [("held", "") if i < frames else ("", "")
            for i in range(LANE_CELLS)]
    jab = []
    for i in range(LANE_CELLS):
        k = i - frames
        jab.append(("move", "START") if k == 0 else ("hit", "HIT") if k == 1
                   else ("move", "") if k in (2, 3) else ("", ""))
    note = ("A jab pressed on frame 0 starts on frame %d, here and online "
            "alike." % frames if frames else
            "A jab pressed on frame 0 starts on frame 0, as on the console.")
    return (
        _panel_head("Input delay", "Every port, in matches and drills") +
        '<div class="dly"><div class="darr%s"><div class="un">&lt;</div>'
        '</div><div class="dnum">%d</div><div class="dside"><div '
        'class="dword">%s</div><div class="dms">%s</div></div><div '
        'class="darr%s"><div class="un">&gt;</div></div><div class="grow"/>'
        '<div class="dnote"><div class="dchip">%s</div><div class="dsub">%s'
        '</div></div></div>' % (
            " on" if frames > 0 else "", frames,
            "Frame" if frames == 1 else "Frames",
            "%.1f MS LATER" % ms if frames else "NOTHING HELD BACK",
            " on" if frames < most else "", chip, sub) +
        '<div class="lanes">%s%s%s%s</div><div class="lnote">%s</div>' % (
            ruler, lane("You press A", press), lane("Held back", held),
            lane("Fox's jab", jab), esc(note)))


def rumble_panel(ports, at, feel):
    """Rumble: a card for each port (name, source, on, has a motor,
    running), `at` the card in focus; `feel`: what "Feel it" says."""
    cards = []
    for i, p in enumerate(ports):
        state = ("RUMBLING" if p["running"] else
                 "NO MOTOR" if not p["motor"] else
                 "ON" if p["on"] else "OFF")
        cards.append(
            '<div class="pcard%s%s%s"><div class="pband" style="background-'
            'color: %s"><div class="pname">%s</div><div class="grow"/><div '
            'class="psrc">%s</div></div><div class="pbody"><div class="sw%s">'
            '<div class="knob"%s><div class="un">%s</div></div></div><div '
            'class="grow"/><div class="pst%s">%s</div></div></div>' % (
                " l" if i % 2 == 0 else "",
                " on" if i == at else "", "" if p["motor"] else " nomotor",
                PORT_COLOR[i], esc(p["name"]), esc(p["source"]),
                " on" if p["on"] else "",
                ' style="background-color: %s"' % PORT_COLOR[i]
                if p["on"] else "", "ON" if p["on"] else "OFF",
                " go" if p["running"] else "", state))
    return (
        _panel_head("Rumble", "The game's own rumble, port by port") +
        '<div class="pcards"><div class="prow2">%s</div>'
        '<div class="prow2">%s</div></div><div class="grow"/>'
        '<div class="feel"><div class="feelbtn"><div class="un">%s'
        '<div>Feel it</div></div></div><div class="feeltxt"><div>%s</div>'
        '<div class="dim2">Nintendo\'s adapter powers motors through its '
        'grey plug.</div></div></div>' % (
            "".join(cards[:2]), "".join(cards[2:]), key("X", dark=True),
            esc(feel)))


def toggle_panel(title, right, big, on, lines):
    """A setting that is on or off: its state, big, what it does."""
    return (
        _panel_head(title, right) +
        '<div class="sbig%s">%s</div>%s<div class="picks">'
        '<div class="pk%s"><div class="un">On</div></div>'
        '<div class="pk%s"><div class="un">Off</div></div></div>' % (
            "" if on else " off", esc(big),
            "".join('<div class="spara">%s</div>' % esc(l) for l in lines),
            " on" if on else "", "" if on else " on"))


def note_panel(title, right, lines):
    return (_panel_head(title, right) + "".join(
        '<div class="spara">%s</div>' % esc(l) for l in lines))


def sound_panel(levels, at, song):
    """Sound: a meter for each volume (name, what it is, 0 to 100,
    colour), `at` the one in focus; `song` the music playing now."""
    meters = []
    for i, (name, about, value, colour) in enumerate(levels):
        lit = (value + 5) // 10
        blocks = "".join(
            '<div class="blk" style="background-color: %s"/>' % (
                colour if 9 - b < lit else "#2B3340") for b in range(10))
        meters.append(
            '<div class="meter%s"><div class="mv"><div class="mn">%d</div>'
            '<div class="mp">%%</div></div><div class="mbar"><div '
            'class="un">%s</div></div><div class="mlabel" style="background-'
            'color: %s"><div class="un"><div class="ml1">%s</div><div '
            'class="ml2">%s</div></div></div></div>' % (
                " on" if i == at else "", value, blocks, colour, esc(name),
                esc(about)))
    return (
        _panel_head("Sound", "Yours: the game is the same at any volume") +
        '<div class="meters">%s<div class="playing"><div class="sed">NOW '
        'PLAYING</div><div class="song">%s</div><div class="spara2">The '
        'menus play the main menu\'s theme; a match and a drill their '
        'stage\'s.</div></div></div>' % ("".join(meters), esc(song)))


def display_panel(sidebar, fullscreen, size):
    """Display: where the game and the sidebar go on the screen."""
    game = ('<div class="dgame"><div class="dlbl">THE GAME · 4:3</div>'
            '<div class="dstage"/></div>')
    side = ('<div class="dside2"><div class="dsb1"/><div class="dsb2"/>'
            '<div class="dsb2 short"/><div class="dsb3"/><div class="grow"/>'
            '<div class="dlbl">SIDEBAR</div></div>') if sidebar else ""
    return (
        _panel_head("Display", "Fullscreen: F11 anywhere too") +
        '<div class="dscreen"><div class="dwin%s">%s%s</div></div>'
        '<div class="spara">%s</div>' % (
            "" if sidebar else " mid", game, side, esc(
                "The game keeps its own 4:3 at any size, %s. %s" % (
                    "the sidebar beside it" if sidebar else
                    "in the middle of the window",
                    "Fullscreen fills the screen, bars at its sides." if
                    fullscreen else "In a window: %d by %d." % tuple(size)))))


def online_panel(ident, nick, port, friends, at, router):
    """Online: the row in focus. `friends`: (name, what) pairs, `at` the
    one in focus; `router`: what the last check found, or None."""
    if ident == "nick":
        return (_panel_head("Nickname", "What your friends see") +
                '<div class="sbig nick">%s</div>' % esc(nick) +
                '<div class="spara">%s</div>' % esc(
                    "Copy a name (up to 12 letters), then X pastes it "
                    "here. It goes to a friend with your code when you "
                    "meet."))
    if ident == "port":
        return (_panel_head("Your code's port", "UDP, on this machine") +
                '<div class="sbig">%d</div>' % port +
                '<div class="spara">%s</div>' % esc(
                    "The port your code points at. A router that keeps it "
                    "gives the same code every time. Change it only if "
                    "another program uses %d." % port))
    if ident == "friends":
        cards = "".join(
            '<div class="fcard%s"><div class="fini"><div class="un">%s</div>'
            '</div><div class="fname">%s</div><div class="grow"/><div '
            'class="fwhat">%s</div></div>' % (
                " on" if i == at else "", esc(name[:2].upper()), esc(name),
                esc(what)) for i, (name, what) in enumerate(friends[:5]))
        return (_panel_head("Friends", "%d met online" % len(friends)) +
                (cards or '<div class="spara">%s</div>' % esc(
                    "Nobody yet: a friend you play online is kept here, "
                    "to play again from Versus, Online.")))
    found = router or ("Not checked", "Asks two STUN servers what this "
                       "machine's address and port look like from outside.")
    return (_panel_head("Router", "Can friends reach you directly?") +
            '<div class="sbig%s">%s</div><div class="spara">%s</div>' % (
                "" if router and router[0] == "Open" else " off",
                esc(found[0]), esc(found[1])))


# ---- the coach ----------------------------------------------------------------
#
# The canvas's "Coach: what went wrong" and "Coach: replay of your try"
# (approved by the owner, 2026-11-13). What they say comes from coach.py.

def _path(dots, floor, kind):
    """A path drawn in its box: the floor, a dot a frame, the presses
    marked and tagged."""
    out = []
    if floor is not None:
        out.append('<div class="cfloor" style="top: %ddp;"/>' % floor)
    for x, y, what, text in dots:
        if what == "tag":
            out.append('<div class="ctag %s" style="left: %ddp; top: %ddp;">'
                       '%s</div>' % (kind, max(4, min(x + 9, 300)),
                                     max(4, min(y - 26, 210)), esc(text)))
        else:
            size = 12 if what == "mark" else 7
            out.append('<div class="cdot %s %s" style="left: %ddp; top: '
                       '%ddp;"/>' % (kind, what, x - size // 2,
                                     y - size // 2))
    return "".join(out)


def pad_display(k):
    """An input display over a panel of the coach's pictures (the owner,
    2026-11-14: "ensure that coach overlay has input displays on both what
    you did wrong and what it should look like"): the triggers with Z
    between them, the control stick and the C-stick in their gates, B A X Y;
    a button lit while held. Client.Play moves it frame by frame (`c` +
    `k` + "i" + the part's name)."""
    def b(name):
        return '<div id="c%si%s" class="pvk">%s</div>' % (k, name, key(name))
    return (
        '<div id="c%si" class="pv"><div class="pvrow">%s<div class="pvt">'
        '<div id="c%siLf" class="pvf"/></div>%s<div class="pvt"><div id='
        '"c%siRf" class="pvf"/></div>%s</div><div class="pvrow"><div class='
        '"pvg"><div id="c%siS" class="pvd"/></div><div class="pvg c"><div '
        'id="c%siC" class="pvd"/></div>%s%s%s%s</div></div>' % (
            k, b("L"), k, b("Z"), k, b("R"), k, k, b("B"), b("A"), b("X"),
            b("Y")))


def _picture(pic, kind):
    """A panel of the game's own pictures (Native.frames_view): `pic` is
    {"view": the interface's view, "crop": (left, top, width, height) of
    the game's 640x480 shown}. The client plays them (Client.coach_play):
    the frame, a tag at each press, how far along."""
    left, top, w, h = pic["crop"]
    s = 412.0 / w
    k = "y" if kind == "you" else "t"
    return (
        '<div class="cpic%s"><img class="cpimg" src="gxcopy://%d" style="left: '
        '%.1fdp; top: %.1fdp; width: %.1fdp; height: %.1fdp;"/>'
        '<div id="c%sf" class="cfr"/><div id="c%sp" class="cptag %s"/>%s'
        '<div class="cbar"><div id="c%sb" class="cbarf %s"/></div></div>' % (
            " tall" if pic.get("tall") else "", pic["view"], -left * s,
            -top * s, 640.0 * s, 480.0 * s, k, k, kind, pad_display(k), k,
            kind))


def coach_grid(tl, wrong):
    """The try's inputs frame by frame against the frame-perfect ones, and
    a bracket from where one was due to where it came (`wrong`: coach.
    first_wrong). The columns' heads are `cgn1`... (the pictures' frame,
    marked as they play)."""
    if not tl:
        return ""
    n = tl["frames"]
    labels = tl.get("labels") or [str(i) for i in range(1, n + 1)]
    head = "".join('<div id="cgn%d" class="cgc cgn">%s</div>' % (i + 1,
                                                              esc(l))
                   for i, l in enumerate(labels))
    rows = ['<div class="cgr"><div class="cgl"/>%s</div>' % head]
    for row in tl["rows"]:
        cells = []
        for i in range(1, n + 1):
            cls = "cgc"
            if row["window"] and row["window"][0] <= i <= row["window"][1]:
                cls += " win"
            if i in row["perfect"]:
                cls += " perf"
            if i in row["you"]:
                cls += " you"
            cells.append('<div class="%s"/>' % cls)
        rows.append('<div class="cgr"><div class="cgl">%s</div>%s</div>'
                    % (esc(row["label"]), "".join(cells)))
    bracket = ""
    if wrong is not None and wrong[1] is not None:
        cell = 690.0 / n
        a, b = sorted((wrong[1], wrong[2]))
        k = abs(wrong[1] - wrong[2])
        bracket = (
            '<div class="cbr"><div class="cbrl" style="left: %ddp; width: '
            '%ddp;"/><div class="cbrt" style="left: %ddp;">%s %s</div></div>'
            % ((a - 0.5) * cell, (b - a) * cell, (a - 0.5) * cell +
               (b - a) * cell / 2 - 60, "%d FRAME%s" % (k, "" if k == 1
                                                        else "S"),
               "LATE" if wrong[1] > wrong[2] else "EARLY"))
    legend = ('<div class="cleg"><div class="cgc you"/><div>you</div>'
              '<div class="cgc perf"/><div>frame-perfect</div>'
              '<div class="cgc win"/><div>allowed</div></div>')
    # four rows or more: closer together (the card's height is fixed)
    return ('<div class="csec">YOUR INPUTS, FRAME BY FRAME</div>'
            '<div class="cgrid%s">%s</div>%s%s' % (
                " tight" if len(tl["rows"]) >= 4 else "", "".join(rows),
                bracket, legend))


def coach_card(v):
    """The coach's card over the game's picture. `v`: headline, drill,
    misses, you (dots, floor) or you_pic (_picture), you_words, target
    (dots, floor), target_pic or neither, target_words, timeline, wrong,
    fix, replay (Y works)."""
    if v.get("you_pic") is not None:
        mine = _picture(v["you_pic"], "you")
    else:
        mine = '<div class="cpath">%s</div>' % _path(
            v["you"][0], v["you"][1], "you")
    you = ('<div class="cpanel"><div class="csec you">YOUR TRY</div>%s<div '
           'class="ccap">%s</div></div>' % (mine, esc(v["you_words"])))
    theirs = None
    if v.get("target_pic") is not None:
        theirs = _picture(v["target_pic"], "tgt")
    elif v.get("target") is not None:
        theirs = '<div class="cpath">%s</div>' % _path(
            v["target"][0], v["target"][1], "tgt")
    if theirs is not None:
        target = ('<div class="cpanel"><div class="csec tgt">WHAT IT SHOULD '
                  'LOOK LIKE</div>%s<div class="ccap">%s</div></div>' % (
                      theirs, esc(v["target_words"])))
    else:
        target = ('<div class="cpanel"><div class="csec tgt">WHAT IT SHOULD '
                  'LOOK LIKE</div><div class="cpath cnone">This drill has '
                  'no demonstration to compare with.</div><div class="ccap">'
                  '%s</div></div>' % esc(v["target_words"]))
    size = 34 if len(v["headline"]) <= 30 else 28 if \
        len(v["headline"]) <= 40 else 22
    keys = [("A", "Try again")]
    if v.get("replay"):
        keys.append(("Y", "Replay"))
    keys.append(("B", "Close"))
    if v.get("anim"):
        keys += [("D-SIDE", "Frame by frame"), ("D-UP", "Play, pause")]
    return (
        '<div class="cdim"/><div class="ccard">'
        '<div class="chead"><div class="cstrip"/><div class="cbadge"><div '
        'class="un">Coach</div></div><div class="ctitle" style="font-size: '
        '%ddp;">%s</div><div class="grow"/><div class="cwhat">%s<br/>%s '
        'MISSES IN A ROW</div></div>'
        '<div class="cpanels">%s%s</div>'
        '<div class="cmid">%s</div>'
        '<div class="cfix"><div class="cfixh">How to fix it</div><div '
        'class="cfixt">%s</div></div>'
        '<div class="grow"/><div class="cfoot">%s</div></div>' % (
            size, esc(v["headline"]), esc(v["drill"].upper()), v["misses"],
            you, target, coach_grid(v.get("timeline"), v.get("wrong")),
            esc(v["fix"]), "".join(
                '<div class="ckey">%s<div>%s</div></div>' % (key(b, dark=True),
                                                             esc(w))
                for b, w in keys)))


REPLAY_HINTS = [("D-SIDE", "Frame by frame"), ("A", "Play, pause"),
                ("Y", "Your try, the target"), ("B", "Back to the coach")]
EXAMPLE_HINTS = [("D-SIDE", "Frame by frame"), ("A", "Play, pause"),
                 ("B", "Go on")]


def replay_view(part, number, total, name, title="Replay", hints=None,
                legend=True):
    """The replay of a try (or a drill's example, played for the tutorial:
    `title`, `hints`): the game's picture left clear, a line at the top,
    the frames along the bottom, and a column of its own over the drill's
    (filled in by Client.replay, Client.tutorial_example)."""
    fg = "#FFFFFF" if part == "Tech" else "#12161C"
    leg = ('<div class="rleg"><div class="rsw now"/><div>this frame</div>'
           '<div class="rsw you"/><div>a press</div><div class="rsw tgt"/>'
           '<div>frame-perfect</div></div>') if legend else \
        ('<div class="rleg"><div class="rsw now"/><div>this frame</div>'
         '<div class="rsw you"/><div>a press</div></div>')
    return (
        '<div class="rtop"><div class="rtitle">%s</div><div id="rmode" '
        'class="rmode"/></div>'
        '<div class="rbottom"><div id="rscrub" class="rscrub"/>%s</div>'
        '<div class="rcol"><div class="rhead" style="background-color: %s; '
        'color: %s;"><div class="tags">%s · %d OF %d · %s</div><div '
        'class="dname">%s</div></div><div class="rbody"><div class="row '
        'rfr"><div id="rf" class="rfn">F1</div><div id="rof" class="rof">'
        'OF 1</div></div><div id="rpad" class="rpad"/><div id="rsay" '
        'class="rsay"/><div class="grow"/><div class="hints">%s</div></div>'
        '</div>' % (
            esc(title), leg, PART_COLOR[part], fg, part.upper(), number,
            total, esc(title.upper()), esc(name),
            hint_rows(hints or REPLAY_HINTS)))


def tutorial_card(v):
    """The tutorial: how to do it (not the coach, which comes after misses
    and is about the try). Over the game's picture, in the coach card's
    frame with a teal head. `v`: title, sub (the line at the right), blocks
    [(heading, text)], parts [(name, state: "done" | "now" | "")] or None,
    keys [(button, words)]."""
    blocks = "".join(
        '<div class="tblock"><div class="th">%s</div><div class="tt">%s'
        '</div></div>' % (esc(h), esc(t)) for h, t in v["blocks"] if t)
    parts = ""
    if v.get("parts"):
        rows = []
        for i, (name, state) in enumerate(v["parts"]):
            rows.append('<div class="tpart %s"><div class="tpn">%d</div><div '
                        'class="tpw">%s</div><div class="tps">%s</div></div>'
                        % (state, i + 1, esc(name),
                           {"done": "Done", "now": "Now"}.get(state, "")))
        parts = ('<div class="tblock"><div class="th">How: one part at a '
                 'time</div><div class="tparts">%s</div></div>' % "".join(rows))
    size = 34 if len(v["title"]) <= 30 else 28
    return (
        '<div class="cdim"/><div class="ccard tcard">'
        '<div class="chead"><div class="cstrip tut"/><div class="cbadge tut">'
        '<div class="un">Tutorial</div></div><div class="ctitle" style='
        '"font-size: %ddp;">%s</div><div class="grow"/><div class="cwhat">'
        '%s</div></div>'
        '<div class="tutbody">%s%s</div>'
        '<div class="grow"/><div class="cfoot">%s</div></div>' % (
            size, esc(v["title"]), esc(v.get("sub", "")).replace("\n",
                                                                "<br/>"),
            blocks, parts, "".join(
                '<div class="ckey">%s<div>%s</div></div>' % (key(b, dark=True),
                                                             esc(w))
                for b, w in v["keys"])))


def replay_scrub(n, now, you, perfect, labels):
    """The frames along the bottom: `now` the one shown (from 1), `you`
    {frame: what was pressed}, `perfect` the frame-perfect ones."""
    out = []
    for i in range(1, n + 1):
        cls = "rs"
        text = labels[i - 1] if i - 1 < len(labels) else ""
        if i in you:
            cls += " you"
            text = you[i]
        if i in perfect:
            cls += " tgt"
        if i == now:
            cls += " now"
        out.append('<div class="%s">%s</div>' % (cls, esc(text)))
    return "".join(out)
