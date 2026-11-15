"""The client's screens as RmlUi markup (style.rcss has the look).

Each function returns a whole document; client.py writes it to a file and
has the game load it. What changes while a screen is up (which panel has
the focus, the line at the bottom, the character card) is changed in place
by element id.
"""
from pathlib import Path

import art
import padart

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


def over_game(board=""):
    """What goes over the game's picture in a match or a drill: the input
    display (two controllers, filled in by the game: src/host/inputs.c),
    the pause menu, the verdict banner. Each has an id so the column can be
    hidden and these moved to the middle (Client.toggle_column). (No
    loading cover: a match loads unseen, the window keeping its last
    picture: Client.load_quietly.)"""
    pads = ('<div id="gpads" class="gpads"><div id="gp0" class="gpad">%s'
            '</div><div id="gp1" class="gpad">%s</div></div>' % (
                pad_display("g0", 0), pad_display("g1", 1))
            if PAD_ART else "")
    # a mode's own score board over the game (`board`: board()); always
    # there, empty without one (the column's toggle moves it)
    pads += '<div id="gboard" class="gboard">%s</div>' % board
    return (
        pads +
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
        '</div></div><div id="pkeys" class="phint pkeys">%s<div>Tutorial'
        '</div>%s<div>Scenario</div><div>Hold: change drill</div></div>'
        '</div></div>'
        '<div id="coach" class="coach"/>'
        '<div id="replay" class="replay"/>'
        % (key("A"), key("D-SIDE"), key("B"), key("D-UP"),
           key("D-SIDE")))


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


def header(crumbs, tag=None, port=True):
    """`crumbs`: where this screen is, the last being the screen itself.
    `tag`: (text, colour, text colour[, stock icon]) for the character
    being trained, or a list of two for a match; `port`: the port and
    layout shown at the right.
    The screens above it are a small line over its name (the owner,
    2026-11-14: "The breadcrumb menu doesn't work with this much nesting":
    TRAIN / FOX / TECH SKILL / FUNDAMENTALS in the title's type did not
    fit)."""
    trail = ""
    if len(crumbs) > 1:
        trail = '<div class="trail">%s</div>' % " / ".join(
            esc(c) for c in crumbs[:-1])
    stripes = "".join('<div class="stripe" style="background-color: %s"/>'
                      % PART_COLOR[p] for p in PART_COLOR)
    who = ""
    # one tag, or the two sides of a match ([(text, colour, ink), ...])
    for i, t in enumerate([tag] if isinstance(tag, tuple) else tag or []):
        if i:
            who += '<div class="hvs">VS</div>'
        icon = t[3] if len(t) > 3 and t[3] else None
        who += ('<div class="tag%s" style="background-color: %s; color: %s">'
                '%s<div class="un">%s</div></div>' % (
                    " icon" if icon else "", t[1], t[2],
                    '<img class="tagicon" src="%s"/>' % picture(icon)
                    if icon else "", esc(t[0])))
    if port:
        who += ('<div class="port">PORT 1</div><div class="nick">----</div>'
                '<div class="layout">Default layout</div>')
    # (no ruler of ticks under it: the owner, 2026-11-14, "delete the weird
    # ruler marks near the top of every window")
    return ('<div class="header"><div class="plate"><div class="titles">'
            '%s<div class="title">%s</div></div></div>%s<div class="grow"/>'
            '<div class="who">%s</div></div>'
            % (trail, esc(crumbs[-1]), stripes, who))


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
    # container"). The post before the wall, which covers its foot: it
    # stops at the wall's edge, going in under it ("should not extend into
    # the diagonal line below it, it should stop cleanly at it", the owner,
    # 2026-11-14)
    out += ('<div class="ashade"><div class="wshadow"/><div class="postsh"/>'
            '</div><div class="post"/><div class="plip"/>'
            '<div class="wclip"><div class="wedge"/></div>'
            '<div class="wfclip"><div class="wface"/><div class="wlip"/></div>')
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


def card(c, costume=0, word=None):
    """The inside of the card about one character: the head, then its
    numbers, its course, its costumes and (Zelda and Sheik) the other.
    `word`: the button's word, if not Train (or Lab, without a course): in
    Versus, Continue (the owner, 2026-11-14)."""
    from courses import title
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
                PART_COLOR[p], esc(title(p)), counts[p])
            for p in PART_COLOR)
        about = ('<div class="about">A course of its own: %d drills.</div>'
                 '<div class="parts">%s</div>' % (sum(counts.values()),
                                                  parts))
        go = "Train"
    else:
        about = ('<div class="about">No course of its own yet: A opens the '
                 'Lab.</div>')
        go = "Lab"
    go = word or go
    return art_head(c, costume) + (
        '<div class="abody"><div class="stats">%s</div>%s%s<div class="grow"/>'
        '<div class="go"><div class="un">%s<div>%s</div></div></div></div>' % (
            stats, about, costume_row(c, costume, "X"), key("A", dark=True),
            go))


def character_select(roster, focus, title="Choose your character",
                     about="Choose who you train. A drill brings its own "
                           "opponents.", inside=None, hints=None,
                     costume=0, go=None):
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
        (inside or card(roster[focus], costume, go)) + '</div>' +
        footer(about, hints or [("A", "Choose"), ("Y", "Costume"),
                                ("B", "Back")],
               tab=roster[focus]["color"]))
    return page("Character select", body)


# ---- versus: the classic select (one grid, a card per port) --------------------

# (the owner, 2026-11-14: "more like the classic character selection where
# there is a single grid of characters and then the port cards below it!
# This should allow me to add CPUs at will")
VCOLUMNS = 9                 # the grid's places to a row, as the game's
PORT_TINT = ("#E5484D", "#3E7BFA", "#F5BE1B", "#2BB673")   # as .pvp's
PORT_INK = ("#FFFFFF", "#FFFFFF", "#12161C", "#FFFFFF")
# what a port's player is, as its chip says it
KIND_CHIP = {"you": "YOU", "human": "HMN", "cpu": "CPU", "model": "AI",
             "dummy": "DUMMY"}


def vtile(i, c, focus, marks):
    """A place in the grid: the character's panel, and a small tag for
    each port that has chosen it (`marks`: port numbers)."""
    tags = "".join('<div class="vmark" style="background-color: %s; color: '
                   '%s">P%d</div>' % (PORT_TINT[p], PORT_INK[p], p + 1)
                   for p in marks)
    return ('<div id="c%d" class="char vchar%s" style="background-color: '
            '%s">%s<div class="vmarks">%s</div></div>' % (
                i, " focus" if focus else "", c["color"], tile(c), tags))


def port_card(port, slot, focus, active, editing=None, rows=()):
    """A port's card below the grid. `slot`: {"kind", "char" (a roster
    entry or None), "costume", "level", "model_name"}; `focus`: the card
    the cursor is on; `active`: the port the grid chooses for;
    `editing`: the row in focus when its options are open (`rows`:
    [(label, value)])."""
    tint, ink = PORT_TINT[port], PORT_INK[port]
    c = slot.get("char")
    kind = slot["kind"]
    chip = KIND_CHIP.get(kind, "")
    if kind == "cpu":
        chip = "CPU %d" % slot.get("level", 9)
    face = ""
    if c is not None:
        # the series' emblem on the colour, the portrait at its own shape
        # against the card's right edge, where its cut side meets the
        # card's border (the owner, 2026-11-14: "Don't squish the model
        # and make sure they are on the right side of the selected card so
        # we don't see the harsh line of the cut off character")
        emb = art.emblem(c["series"])
        pic = _portrait(c, slot.get("costume", 0))
        if emb is not None:
            face += '<img class="vemb" src="%s" style="image-color: %s"/>' % (
                picture(emb), _tint(c, pic is None, big=True))
        if pic is not None:
            face += '<img class="vface" src="%s"/>' % picture(pic)
    name = c["name"] if c is not None else "Choose"
    who = {"you": "You", "human": "A second controller",
           "cpu": "The game's CPU", "dummy": "Stands still"}.get(
               kind, slot.get("model_name", "A trained model"))
    inner = (
        '<div class="vtop"><div class="vport" style="background-color: %s; '
        'color: %s"><div class="un">P%d</div></div><div class="vkind"><div '
        'class="un">%s</div></div></div><div class="vpic" style="'
        'background-color: %s">%s</div><div class="vname"><div class="un">'
        '%s</div><div class="vwho">%s</div></div>' % (
            tint, ink, port + 1, esc(chip), c["color"] if c else "#2B3340",
            face, esc(name), esc(who)))
    if editing is not None:
        inner += '<div class="vopts">%s</div>' % "".join(
            '<div class="vrow%s"><div class="vrl">%s</div><div class="grow"/>'
            '<div class="vrv">%s</div></div>' % (
                " focus" if i == editing else "", esc(label), esc(value))
            for i, (label, value) in enumerate(rows))
    return ('<div id="vp%d" class="vcard%s%s" style="border-color: %s">'
            '<div class="ring"/>%s</div>' % (
                port, " focus" if focus else "",
                " active" if active else "", tint, inner))


def add_card(focus, n):
    """The card after the ports: another player (a CPU at first)."""
    return ('<div id="vpadd" class="vcard vadd%s"><div class="ring"/>'
            '<div class="vplus">+</div><div class="vaddl"><div class="un">'
            'Add player</div><div class="vwho">P%d</div></div></div>' % (
                " focus" if focus else "", n + 1))


def port_cards(slots, card_at, active, editing=None, rows=(), most=4):
    """The row of port cards: each port's, then (fewer than `most`) the
    card that adds one, then empty places up to four."""
    out = [port_card(i, sl, card_at == i, active == i,
                     editing if card_at == i else None, rows)
           for i, sl in enumerate(slots)]
    if len(slots) < most:
        out.append(add_card(card_at == len(slots), len(slots)))
    while len(out) < 4:
        out.append('<div class="vcard vnone"/>')
    return "".join(out)


def versus_select(roster, focus, slots, area, card_at, active, crumbs,
                  editing=None, rows=(), most=4, ready=False,
                  locked=False):
    """Versus's character select, as the game's own: one grid of
    characters, a card per port below it. `focus`: the place in focus in
    the grid; `area`: "grid" or "cards"; `slots`: each port's (see
    port_card); `active`: the port the grid chooses for; `most`: the
    players the mode allows; `ready`: every port has a character (START
    goes on); `locked`: the mode fixes the characters (the grid shows
    them, A does not change them)."""
    marks = {}
    for p, sl in enumerate(slots):
        if sl.get("char") is not None:
            marks.setdefault(sl["char"]["id"], []).append(p)
    tiles = [vtile(i, c, area == "grid" and i == focus,
                   marks.get(c["id"], [])) for i, c in enumerate(roster)]
    rows_html = "".join('<div class="vrrow">%s</div>' % "".join(
        tiles[i:i + VCOLUMNS]) for i in range(0, len(tiles), VCOLUMNS))
    hints = [("A", "Choose" if area == "grid" else "Options"),
             ("Y", "Costume")]
    if ready:
        hints.append(("START", "Stage select"))
    hints.append(("B", "Back"))
    body = (
        header(crumbs, port=False) +
        '<div id="vgrid" class="vgrid%s">%s</div>' % (
            " locked" if locked else "", rows_html) +
        '<div id="vports" class="vports">%s</div>' % port_cards(
            slots, card_at if area == "cards" else -1, active, editing,
            rows, most) +
        footer("", hints))
    return page("Versus", body)


# ---- versus and lab: who is on the other side ---------------------------------

def opponent_card(c, who, what, count, go, costume=0):
    """The card on the opponent screen: the character in its costume, who
    plays it (`who`, with `what` that is in a few words; `count`: "2 of
    31"), changed with the D-pad left and right (the owner, 2026-11-14:
    "just using X is bad because it requires a full cycle if you overshot
    it"); its costumes (Y) and the other of a shared place (X), as on your
    own card ("for consistency"). The stage is chosen next, on a screen of
    its own."""
    return art_head(c, costume) + (
        '<div class="body low"><div class="fact"><div class="fl">Played by'
        '</div><div class="fv big2">%s</div><div class="fl">%s</div></div>'
        '<div class="pick">%s<div>Change</div><div class="grow"/>'
        '<div class="lbl">%s</div></div>%s'
        '<div class="grow"/><div class="go"><div class="un">%s<div>%s</div>'
        '</div></div></div>' % (
            esc(who), esc(what), key("D-SIDE"), esc(count),
            costume_row(c, costume, "X"), key("A", dark=True), esc(go)))


# ---- the stage select (the canvas's "A · Stage select: grid and card") -------

STAGE_COLUMNS = 3          # the six legal stages
STAGE_COLUMNS_ALL = 6      # every stage (the owner: "a toggle between all
                           # and legal")


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


def stage_card(s, go):
    """The card about the stage in focus: the stage whole, the game's name
    logo, and what A does (the owner, 2026-11-14: its line, its numbers
    and blast zones were "too verbose")."""
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
    return out + (
        '<div class="sgbody"><div class="grow"/><div class="go"><div '
        'class="un">%s<div>%s</div></div></div></div>' % (
            key("A", dark=True), esc(go)))


def stage_select(stage_list, focus, me, opp, go, every=False,
                 costumes=(0, 0)):
    """After the characters: where they play. `me`, `opp`: the two
    characters (`costumes`: theirs, for their stock icons in the
    matchup); `go`: what A does ("Fight", or "Start" in the Lab);
    `every`: all the game's stages (smaller panels, six to a row), not
    only the six legal ones (Y changes it)."""
    import art
    cols = STAGE_COLUMNS_ALL if every else STAGE_COLUMNS
    tiles = [stage_tile(i, s, i == focus) for i, s in enumerate(stage_list)]
    rows = "".join('<div class="sgrow">%s</div>' % "".join(
        tiles[i:i + cols]) for i in range(0, len(tiles), cols))
    body = (
        header(["Choose a stage", "All stages" if every else
                "Legal stages"],
               tag=[(me["name"], me["color"], me["fg"],
                     art.stock(me["id"], costumes[0])),
                    (opp["name"], opp["color"], opp["fg"],
                     art.stock(opp["id"], costumes[1]))],
               port=False) +
        '<div class="sgrid%s">' % (" all" if every else "") + rows +
        '</div>' +
        '<div id="card" class="card">' + stage_card(stage_list[focus], go) +
        '</div>' +
        # (no line at the bottom: the owner, 2026-11-14, "it's
        # unnecessary")
        footer("", [("A", go), ("X", "Random"),
             ("Y", "Legal stages" if every else "All stages"),
             ("B", "Back")]))
    return page("Stage select", body)


# ---- versus: the game modes ------------------------------------------------------

MODE_COLUMNS = 3


def mode_tile(i, m, focus):
    """A mode's panel: its icon large on its colour, its name below."""
    return ('<div id="m%d" class="mt%s" style="background-color: %s">'
            '<div class="ring"/><div class="mtin">%s</div><div class="mtstrip">'
            '<div class="un">%s</div></div></div>' % (
                i, " focus" if focus else "", m.colour,
                icon(m.icon, "mticon" + (" dark" if m.ink != "#F3F6FA"
                                         else "")),
                esc(m.name.upper())))


def _stock(cid, costume):
    pic = art.stock(cid, costume) if cid else None
    return '<img class="mkstock" src="%s"/>' % picture(pic) if pic else ""


def tug_track(me, opp, lead):
    """Tug of War's score as a rope: their stock icon at one end, yours at
    the other, a notch for each point either way, even in the middle.
    `me`, `opp`: (character id, costume); `lead`: how far ahead wins."""
    notches = "".join('<div class="mkn%s"/>' % (" mid" if i == lead else "")
                      for i in range(2 * lead + 1))
    return (
        '<div class="mktrack"><div class="mkend">%s<div class="mklabel">'
        'They win</div></div><div class="mkrope"><div class="mkbar"/>'
        '<div class="mkticks">%s</div><div class="mkeven">Even</div></div>'
        '<div class="mkend">%s<div class="mklabel">You win</div></div></div>'
        '<div class="mksides"><div>+%d</div><div class="grow"/><div>+%d'
        '</div></div>' % (_stock(*opp), notches, _stock(*me), lead, lead))


def mode_card(m, me=None, opp=None):
    """The card about the mode in focus: its icon and name on its colour,
    the line about it as set, how it is scored, (Tug of War) the score as a
    rope. `me`, `opp`: (character id, costume) for the icons."""
    rules = "".join('<div class="mrule"><div class="mdot" style="'
                    'background-color: %s"/><div class="mrt">%s</div></div>'
                    % (m.colour, esc(r)) for r in m.rules_text())
    track = tug_track(me or ("fox", 0), opp or ("falco", 0),
                      m.settings["lead"]) if m.ident == "tug-of-war" else ""
    go = "Options" if m.options else next_step(m)
    return (
        '<div class="mchead" style="background-color: %s; color: %s">%s'
        '<div class="mcname">%s</div><div class="mctag">%s</div></div>'
        '<div class="mcbody"><div class="fl">How it is scored</div>%s%s'
        '<div class="grow"/><div class="go"><div class="un">%s<div>%s</div>'
        '</div></div></div>' % (
            m.colour, m.ink, icon(m.icon, "mcicon" + (
                " dark" if m.ink != "#F3F6FA" else "")), esc(m.name),
            esc(m.line()), rules, track, key("A", dark=True), esc(go)))


def mode_select(mode_list, focus, me=None, opp=None):
    """Versus > Local: what the match is played for (modes.py), each mode
    as set. `me`, `opp`: (character id, costume) for the score's icons
    (the last match's, or Fox's and Falco's)."""
    tiles = [mode_tile(i, m, i == focus) for i, m in enumerate(mode_list)]
    rows = "".join('<div class="mgrow">%s</div>' % "".join(
        tiles[i:i + MODE_COLUMNS])
        for i in range(0, len(tiles), MODE_COLUMNS))
    body = (
        header(["Versus", "Choose a mode"]) +
        '<div class="mgrid">' + rows + '</div>' +
        '<div id="card" class="card">' +
        mode_card(mode_list[focus], me, opp) + '</div>' +
        footer(mode_list[focus].line(),
               [("A", "Choose"), ("Z", "Rules"), ("B", "Back")]))
    return page("Choose a mode", body)


def option_rows(m, at):
    """The mode's settings as the settings screens' rows."""
    return controls_rows([(o.key, o.name, o.about.split(":")[0].split(".")[0],
                           o.words(m.settings[o.key]), m.colour)
                          for o in m.options], at)


def option_panel(m, at, me=None, opp=None):
    """The setting in focus, edited: its value big between arrows, what it
    does, (Tug of War) the rope as it would be."""
    o = m.options[at]
    v = m.settings[o.key]
    words = o.words(v)
    # a number and its unit ("3 stocks"), or a value that is a word
    # ("Off": Shine Battle's Firefox and Illusion)
    number, unit = words.split(" ", 1) if o.unit and " " in words else \
        ("", words)
    track = tug_track(me or ("fox", 0), opp or ("falco", 0), v) \
        if m.ident == "tug-of-war" and o.key == "lead" else ""
    return (
        _panel_head(o.name, m.name) +
        '<div class="dly"><div class="darr%s"><div class="un">&lt;</div>'
        '</div><div class="dnum">%s</div><div class="dside"><div '
        'class="dword">%s</div></div><div class="darr%s"><div class="un">'
        '&gt;</div></div><div class="grow"/></div>'
        '<div class="spara">%s</div><div class="otrack">%s</div>' % (
            " on" if v != o.values[0] else "", esc(number), esc(unit),
            " on" if v != o.values[-1] else "", esc(o.about), track))


def mode_options(m, at, me=None, opp=None):
    """After the mode, its settings (the owner, 2026-11-14: "It should go
    select the mode, then configure options, then start game!"): the rows
    on the left, the one in focus edited beside them; A goes on to the
    characters."""
    body = (
        header(["Versus", m.name]) +
        '<div id="slist" class="slist">%s</div>' % option_rows(m, at) +
        '<div id="spanel" class="spanel">%s</div>' % option_panel(
            m, at, me, opp) +
        footer(m.line(), [("D-SIDE", "Change"), ("A", next_step(m)),
                          ("B", "Back")]))
    return page(m.name, body)


# ---- the rules every mode is played by (Z on the mode select) ---------------

RULE_PAGES = (("items", "Item switch", "Which items appear"),
              ("stages", "Random stages", "The stages Random picks from"))
SWITCH_COLUMNS = 4


def rules_rows(r, at, stages_on, stages_all):
    """The Rules' rows: the settings, then the two switches (A opens)."""
    from modes import ITEMS, NOT_YET
    rows = [(o.key, o.name, o.about.split(":")[0].split(".")[0],
             o.words(r.settings[o.key]), r.colour) for o in r.options]
    items = [k for _, k in ITEMS]
    counts = {"items": "%d of %d" % (len([k for k in items if k not in
                                          r.items_off and k not in NOT_YET]),
                                     len(ITEMS)),
              "stages": "%d of %d" % (stages_on, stages_all)}
    rows += [(k, name, about, counts[k], r.colour)
             for k, name, about in RULE_PAGES]
    return controls_rows(rows, at)


def rules_panel(r, at, on_names):
    """The row in focus: a setting edited big between arrows, or a
    switch's items or stages that are on (`on_names`), A to change them."""
    n = len(r.options)
    if at >= n:
        k, name, about = RULE_PAGES[at - n]
        shown = ", ".join(on_names[:14]) + (
            ", and %d more" % (len(on_names) - 14)
            if len(on_names) > 14 else "")
        return (_panel_head(name, "Rules") +
                '<div class="spara">%s. On now: %s.</div>'
                '<div class="grow"/><div class="go rgo"><div class="un">%s'
                '<div>Choose</div></div></div>' % (
                    esc(about), esc(shown or "none"), key("A", dark=True)))
    o = r.options[at]
    v = r.settings[o.key]
    words = o.words(v)
    number, word = (words.split(" ", 1) if o.key == "time" and v else
                    (words, "") if o.key == "ratio" else ("", words))
    return (
        _panel_head(o.name, "Rules") +
        '<div class="dly"><div class="darr%s"><div class="un">&lt;</div>'
        '</div><div class="dnum">%s</div><div class="dside"><div '
        'class="dword">%s</div></div><div class="darr%s"><div class="un">'
        '&gt;</div></div><div class="grow"/></div>'
        '<div class="spara">%s</div>' % (
            " on" if v != o.values[0] else "", esc(number), esc(word),
            " on" if v != o.values[-1] else "", esc(o.about)))


def rules_page(r, at, stages_on, stages_all, on_names):
    """Versus / Rules: the game's own Rules, Item Switch and Random Stage
    Switch for every mode (the owner, 2026-11-14: "global options openable
    via Z which has basic settings like time, items, random stage
    selection filters, etc. just like the original game!")."""
    body = (
        header(["Versus", "Rules"]) +
        '<div id="slist" class="slist">%s</div>' % rules_rows(
            r, at, stages_on, stages_all) +
        '<div id="spanel" class="spanel">%s</div>' % rules_panel(
            r, at, on_names) +
        footer(r.summary(), [("D-SIDE", "Change"), ("A", "Choose"),
                             ("B", "Done")]))
    return page("Rules", body)


def thumb(path, width, height):
    """A small copy of picture `path` (None: None), made once with
    ImageMagick as the stage pictures are, kept under build/ui/art/thumb:
    a page of many pictures shown small loads small textures (the window
    build's 32-bit space is tight)."""
    import subprocess
    if path is None:
        return None
    path = Path(path)
    out = art.ART / "thumb" / ("%s-%dx%d.png" % (path.stem, width, height))
    try:
        if not out.exists() or out.stat().st_mtime < path.stat().st_mtime:
            out.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["magick", str(path), "-filter", "Lanczos",
                            "-resize", "%dx%d!" % (width, height), "-depth",
                            "8", str(out)], check=True,
                           capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out


def switch_grid(names, on, at, pics=None, square=False):
    """A switch's tiles, a row of SWITCH_COLUMNS each: its box filled when
    on, its picture (`pics`, None for none yet: a stage's preview, an
    item's icon, `square`) left of its name; `at` in focus."""
    pics = pics or [None] * len(names)
    shape = " swsq" if square else ""
    tiles = ['<div class="swt%s%s"><div class="box%s"/>%s<div class="swn">'
             '%s</div></div>' % (
                 " focus" if i == at else "", "" if on[i] else " off",
                 " on" if on[i] else "",
                 '<img class="swpic%s" src="%s"/>' % (shape, picture(p))
                 if p is not None else
                 '<div class="swpic%s none"/>' % shape, esc(name))
             for i, (name, p) in enumerate(zip(names, pics))]
    return "".join('<div class="swrow">%s</div>' % "".join(
        tiles[i:i + SWITCH_COLUMNS])
        for i in range(0, len(tiles), SWITCH_COLUMNS))


def switch_page(title, names, on, at, desc, hints, pics=None,
                square=False):
    """Versus / Rules / a switch (Item switch, Random stages): every item
    or stage with its picture, A switching the one in focus."""
    body = (
        header(["Versus", "Rules", title]) +
        '<div id="swgrid" class="swgrid">%s</div>' % switch_grid(
            names, on, at, pics, square) +
        footer(desc, hints))
    return page(title, body)


def next_step(m):
    """What A goes on to after mode `m` and its options: the characters,
    or, when the mode fixes them, who plays the opponent."""
    return "Choose opponent" if m.fighters else "Choose characters"


def results_page(m, sides, winner, rows, time, stage, online=False):
    """After a mode is won (the owner, 2026-11-14: "Let's build a more
    robust game over screen. It should have stats, etc. for both players
    ... it should be in our UI style, but it should support custom stats,
    etc. per mode!"): the winner's card on the left, the two sides' numbers
    on the right, the mode's own first (Mode.stats), then every mode's
    (modes.MatchStats). `sides`: per port {"c": the character, "costume",
    "name", "who" (You, CPU, a model's name), "you"}; `rows`: [(section,
    [(name, (port 0's, port 1's), better)])]; `time`: the match's length;
    `stage`: its name. `online`: a match with a friend (A goes on).
    `winner` None: a draw (TIME! with the falls and the damage even)."""
    draw = winner is None
    w = sides[0 if draw else winner]
    head = "" if draw else art_head(w["c"], w["costume"])
    line = m.result_line([s_["name"] for s_ in sides])
    # the score at a glance: each side's stock icon, the KOs each took
    kos = dict(rows).get("The match", [])
    kos = next((v for n, v, _ in kos if n == "KOs"), None)
    score = ""
    if kos is not None:
        pics = [art.stock(sd["c"]["id"], sd["costume"]) for sd in sides]
        score = '<div class="rxscore">%s<div class="rxkos">%s</div>%s</div>' % (
            '<img class="rxsicon" src="%s"/>' % picture(pics[0])
            if pics[0] else "",
            esc("%s – %s" % kos),
            '<img class="rxsicon" src="%s"/>' % picture(pics[1])
            if pics[1] else "")
    card = (
        '<div class="rxwin">%s<div class="rxwbody"><div class="rxwtag" style='
        '"background-color: %s; color: %s"><div class="un">%s</div>'
        '</div><div class="rxwline">%s</div>%s<div class="rxwmeta"><div '
        'class="fl">%s</div><div class="fv">%s</div><div class="fl">%s · %s'
        '</div></div></div></div>' % (
            head, m.colour, m.ink, "Draw" if draw else "Winner", esc(line),
            score, esc(m.name), esc(m.summary() or m.line()), esc(stage),
            esc(time)))

    def col(port):
        sd = sides[port]
        place = "Draw" if draw else "1st" if port == winner else "2nd"
        pic = art.stock(sd["c"]["id"], sd["costume"])
        img = '<img class="rxstock" src="%s"/>' % picture(pic) if pic else ""
        return (
            '<div class="rxcol"><div class="rxph">%s<div class="pvp p%d rxport">'
            'P%d</div><div class="grow"/><div class="rxplace%s"><div class='
            '"un">%s</div></div></div><div class="rxname">%s</div><div class='
            '"rxwho">%s</div></div>' % (
                img, port + 1, port + 1, " first" if port == winner else "",
                place, esc(sd["c"]["name"]), esc(sd["who"])))

    def number(v):
        """A value as a number to compare: 3, "42%", "1:05" (seconds)."""
        v = str(v).rstrip("%")
        if ":" in v:
            m, sec = v.split(":", 1)
            return float(m) * 60 + float(sec)
        return float(v)

    def mark(values, better, i):
        if better is None:
            return ""
        try:
            a, b = (number(v) for v in values)
        except ValueError:
            return ""
        if a == b:
            return ""
        best = (a > b) == (better == "more")
        return " best" if best == (i == 0) else ""

    table = ""
    for section, section_rows in rows:
        if not section_rows:
            continue
        table += '<div class="rxsec"><div class="rxsecn">%s</div></div>' % (
            esc(section))
        for name, values, better in section_rows:
            table += (
                '<div class="rxrow"><div class="rxlab">%s</div>%s</div>' % (
                    esc(name), "".join(
                        '<div class="rxval%s">%s</div>' % (
                            mark(values, better, i), esc(str(v)))
                        for i, v in enumerate(values))))
    body = (
        header(["Versus", m.name, "Results"]) + card +
        '<div class="rxtab"><div class="rxhead"><div class="rxlab"/>%s%s</div>'
        '%s</div>' % (col(0), col(1), table) +
        footer(line + ". " + time + ".",
               [("A", "Continue")] if online else
               [("A", "Rematch"),
                ("X", "Options" if m.fighters else "Characters"),
                ("B", "Characters" if m.stage else "Change stage")]))
    return page("Results", body)


# ---- a mode's score board over the game ----------------------------------------

ROPE_STEP = 44          # dp between the rope's nodes (style.rcss .twk*)


def rope_classes(m):
    """{element id: its classes} for Tug of War's rope as the score stands:
    a node per point from port 0's goal (left) to port 1's, the knot on
    the node of the lead (the leader's stock icon there, a knot at even),
    the nodes it has been pulled across in the leader's colour."""
    lead, goal = m.rope()
    at = goal - lead                    # port 0 ahead: toward the left
    out = {}
    for i in range(2 * goal + 1):
        c = {"twat", "twk%d" % i}
        if i == 0:
            c |= {"goal", "goal0"}
        elif i == 2 * goal:
            c |= {"goal", "goal1"}
        elif i == goal:
            c.add("mid")
        if lead > 0 and at <= i < goal:
            c.add("lit0")
        if lead < 0 and goal < i <= at:
            c.add("lit1")
        out["twn%d" % i] = c
    mark = {"twat", "twm", "twk%d" % at}
    mark.add("even" if lead == 0 else "who0" if lead > 0 else "who1")
    if m.winner is not None:
        mark.add("won")
    out["twmark"] = mark
    return out


def rope_board(m, pics):
    """Tug of War's score over the game (the owner, 2026-11-14: "an actual
    tug of war display that moves the stock icon along nodes to visually
    see who is winning"): P1's stock icon at the left end, P2's at the
    right, a node per point between; the knot moves (rope_classes; the
    client changes its classes and it slides) to the leader's side, the
    leader's stock icon riding it. `pics`: each port's stock icon."""
    lead, goal = m.rope()
    st = rope_classes(m)

    def cls(ident):
        return " ".join(sorted(st[ident]))

    def end(port):
        img = '<img src="%s"/>' % picture(pics[port]) if pics[port] else ""
        return ('<div class="twend">%s<div class="pvp p%d twtag">P%d</div>'
                '</div>' % (img, port + 1, port + 1))

    nodes = "".join('<div id="twn%d" class="%s"><div class="twdot"/></div>'
                    % (i, cls("twn%d" % i)) for i in range(2 * goal + 1))
    riders = "".join('<img class="twi%d" src="%s"/>' % (p, picture(pics[p]))
                     for p in (0, 1) if pics[p])
    return ('<div class="twb">%s<div class="twtrack" style="width: %ddp;">'
            '<div class="twline"/>%s<div id="twmark" class="%s"><div '
            'class="twknot"/>%s</div></div>%s</div>' % (
                end(0), 2 * goal * ROPE_STEP, nodes, cls("twmark"), riders,
                end(1)))


# a mode's `board`: (its markup, its classes as the score stands)
BOARDS = {"rope": (rope_board, rope_classes)}


def board(m, pics):
    """Mode `m`'s score board over the game, or "" (the HUD's stocks)."""
    if m is None or m.board is None:
        return ""
    return BOARDS[m.board][0](m, pics)


def board_classes(m):
    """{element id: classes} of mode `m`'s board as its score stands."""
    if m is None or m.board is None:
        return {}
    return BOARDS[m.board][1](m)


def versus_rail(c, opp, who, what, stage, lab, mode=None, board=""):
    """The column beside a match in Versus or the Lab. `mode`: (the game
    mode's name, its score in words, its settings in words) in Versus;
    `board`: the mode's score board over the game (board()).
    """
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
        '</div></div>%s<div id="botstate" class="line botstate"/>'
        '<div class="grow"/><div class="hints">%s</div>%s' % (
            esc(opp["name"]), esc(who), esc(what), esc(stage),
            ('<div class="fact"><div class="fl">Mode</div><div class="fv">'
             '%s</div><div class="fl">%s</div><div id="vscore" class="fv '
             'vscore">%s</div></div>' % (esc(mode[0]), esc(mode[2]),
                                          esc(mode[1])) if mode else ""),
            tools,
            match_hints()))
    return page("Versus", over_game(board) + '<div id="rail" class="rail">%s'
                '<div class="body">%s</div></div>' % (head, body), paper=False)


# ---- the course hub -----------------------------------------------------------

# (The owner, 2026-11-14: "move Lab into Train, it should replace the free
# play button".)
LAB = ("lab", "lab", "Lab", "Any opponent, any stage. Nothing is judged.",
       True)


def hub(c, course, here, progress, left):
    """`here`: ids of the drills that play in this client. `left`: the
    drill last played, if it is one of this course's."""
    from courses import ABOUT, PARTS, title
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
                esc(title(part)), esc(ABOUT[part][0]), squares, done,
                len(drills),
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


def rows_for(course, part, cat=None):
    """The drill rows a part's list shows at once: one fewer when it has
    subcourses shown together, for their headings (two at most in view,
    each half a row); a category's own list has none."""
    if cat:
        return ROWS
    return ROWS - 1 if any(d.get("sub") for d in course["parts"][part]) \
        else ROWS


# a category of a part (Tech skill's subcourses), as its list says it
CATEGORY_ABOUT = {
    "Movement": "Moving on the ground, in the air and at the ledge.",
    "Fundamentals": "L-cancels, jump-cancels, DI, SDI and the shield "
                    "drop.",
    "Character": "%s's own techniques.",
}


def categories(course, part):
    """A part's categories, in order (courses.SUBCOURSES), or []."""
    from courses import SUBCOURSES
    return [s for s in SUBCOURSES.get(part, ())
            if any(d.get("sub") == s for d in course["parts"][part])]


def in_category(course, part, cat):
    """A part's drills, those of category `cat` only if it is given."""
    return [d for d in course["parts"][part]
            if not cat or d.get("sub") == cat]


def category_about(c, cat):
    words = CATEGORY_ABOUT.get(cat, "")
    return words % c["name"] if "%s" in words else words


def category_rows(c, course, part, progress, at):
    """The categories' rows: name and what it trains, drills, done."""
    out = []
    for i, cat in enumerate(categories(course, part)):
        ds = in_category(course, part, cat)
        done = sum(1 for d in ds if progress.done(d["id"]))
        out.append(
            '<div class="r rcat%s"><div class="c-n"><div class="cap" style='
            '"background-color: %s"/></div><div class="c-name"><div '
            'class="nm">%s</div><div class="gl">%s</div></div><div '
            'class="c-t">%d</div><div class="c-t">%d</div><div class="c-b"/>'
            '<div class="c-d"/></div>' % (
                " on" if i == at else "",
                PART_COLOR[part] if i == at else "#00000000", esc(cat),
                esc(category_about(c, cat)), len(ds), done))
    return "".join(out)


def category_detail(c, course, part, cat, progress, at):
    """The card beside the categories: the one in focus, its drills."""
    from courses import title
    ds = in_category(course, part, cat)
    done = sum(1 for d in ds if progress.done(d["id"]))
    fg = "#FFFFFF" if part == "Tech" else "#12161C"
    names = [d["name"] for d in ds]
    shown = ", ".join(names[:6]) + (", and %d more" % (len(names) - 6)
                                    if len(names) > 6 else "")
    facts = "".join(
        '<div class="fact"><div class="fl">%s</div><div class="fv">%s</div>'
        '</div>' % (label, esc(words))
        for label, words in (("Drills", shown),
                             ("Done", "%d of %d" % (done, len(ds)))))
    return (
        '<div class="top" style="background-color: %s"/><div class="slant" '
        'style="background-color: %s"/><div class="head" style="color: %s">'
        '<div class="tags">%s · %d OF %d</div><div class="dname" '
        'style="font-size: %ddp">%s</div></div><div class="body"><div '
        'class="goal">%s</div>%s<div class="grow"/><div class="go"><div '
        'class="un">%s<div>Open</div></div></div></div>' % (
            PART_COLOR[part], PART_COLOR[part], fg,
            esc(title(part).upper()), at + 1,
            len(categories(course, part)), 52 if len(cat) <= 12 else 38,
            esc(cat), esc(category_about(c, cat)), facts,
            key("A", dark=True)))


def category_list(c, course, part, progress, at):
    """A part with categories (Tech skill: Movement, Fundamentals,
    Character) opens on them; A opens one's drills (the owner,
    2026-11-14: "in tech skill I want the first view to be categories
    then selecting that puts you into the list view for all the drills in
    that category")."""
    from courses import PARTS, title
    cats = categories(course, part)
    tabs = "".join(
        '<div class="ptab %s%s"><div class="un">%s · %d</div></div>' % (
            PART_CLASS[p], " on" if p == part else "", title(p),
            len(course["parts"][p])) for p in PARTS)
    body = (
        header(["Train", c["name"], title(part)],
               tag=(c["name"], c["color"], c["fg"])) +
        '<div class="tabs">' + key("L", dark=True, wide=True) + tabs +
        key("R", dark=True, wide=True) + '</div>'
        '<div class="listhead"><div class="c-n"><div class="cap"/></div>'
        '<div class="c-name">CATEGORY</div><div class="c-t">DRILLS</div>'
        '<div class="c-t">DONE</div><div class="c-b"/><div class="c-d"/>'
        '</div>'
        '<div id="rows" class="rows">' +
        category_rows(c, course, part, progress, at) + '</div>'
        '<div id="detail" class="card detail">' +
        category_detail(c, course, part, cats[at], progress, at) + '</div>' +
        footer(category_about(c, cats[at]), [("A", "Open"), ("B", "Back")],
               tab=PART_COLOR[part]))
    return page("Drills", body)


def place_of(course, d):
    """Where a drill is, as its card says it: ("MOVEMENT", its number, how
    many) in a subcourse, else (the part's name, ...)."""
    from courses import title
    if d.get("sub"):
        same = [x for x in course["parts"][d["part"]]
                if x.get("sub") == d["sub"]]
        return d["sub"].upper(), d["number"], len(same)
    return title(d["part"]).upper(), d["number"], len(course["parts"][
        d["part"]])


def _percent(d):
    return "%d%%" % round(100.0 * d["yes"] / d["tries"]) if d["tries"] \
        else "-"


def list_rows(course, part, here, progress, at, top, cat=None):
    """The rows in view: `at` is the drill in focus, `top` the first row
    shown (of category `cat`'s drills, when given)."""
    out = []
    sub = None
    for i, d in enumerate(in_category(course, part, cat)[top:top + rows_for(
            course, part, cat)], top):
        if d.get("sub") and d["sub"] != sub and not cat:
            # the subcourse's heading: over its first row in view
            sub = d["sub"]
            out.append('<div class="rsub"><div>%s</div></div>' % esc(sub))
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
    place, number, total = place_of(course, d)
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
        % (PART_COLOR[part], PART_COLOR[part], fg, esc(place),
           number, total, size, esc(d["name"]), esc(d["goal"]),
           "".join(facts), " on" if done else "", " on" if done else "",
           "Done. Press again to undo" if done else "Mark as done",
           key("Y", dark=done), "" if plays else " off",
           key("A", dark=True), "Start" if plays else "Not in this client "
           "yet"))


def drill_list(c, course, part, here, progress, at, top, cat=None):
    from courses import PARTS, title
    drills = in_category(course, part, cat)
    tabs = "".join(
        '<div class="ptab %s%s"><div class="un">%s · %d</div></div>' % (
            PART_CLASS[p], " on" if p == part else "", title(p),
            len(course["parts"][p])) for p in PARTS)
    body = (
        header(["Train", c["name"], title(part)] + ([cat] if cat else []),
               tag=(c["name"], c["color"], c["fg"])) +
        '<div class="tabs">' + key("L", dark=True, wide=True) + tabs +
        key("R", dark=True, wide=True) + '</div>'
        '<div class="listhead"><div class="c-n"><div class="cap"/><div>#'
        '</div></div><div class="c-name">DRILL</div><div class="c-t">TRIES'
        '</div><div class="c-t">SUCCESS</div><div class="c-b">BEST</div>'
        '<div class="c-d"><div>DONE</div></div>'
        '</div>'
        '<div id="rows" class="rows">' +
        list_rows(course, part, here, progress, at, top, cat) + '</div>'
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
    """A tech drill's attempt frame by frame: for each input a row of the
    frames it was pressed on, and under it the frames allowed and the
    frame-perfect ones."""
    if not tl:
        return ""
    n = tl["frames"]
    labels = tl.get("labels") or [
        # a long attempt has no room for every number
        str(i) if n <= 12 or i % 5 == 0 else "" for i in range(1, n + 1)]
    head = "".join('<div class="tlc tln">%s</div>' % label
                   for label in labels)
    rows = ['<div class="tlrow">%s</div>' % head]
    for row in tl["rows"]:
        # its name on a line of its own (beside the frames, "Stick to the
        # side" ran over them: the owner, 2026-11-14, "glitched
        # formatting"), then one row: yours outlined over the window
        rows.append('<div class="tllab">%s</div>' % esc(row["label"]))
        rows.append('<div class="tlrow">%s</div>' % input_cells(
            row, n, "both", "tlc"))
    legend = ('<div class="tlleg"><div class="tlc you"/><div>you</div>'
              '<div class="tlc perf"/><div>frame-perfect</div>'
              '<div class="tlc win"/><div>window</div></div>')
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
    label, number, total = place_of(course, d)
    fg = "#FFFFFF" if part == "Tech" else "#12161C"
    size = 40 if len(d["name"]) <= 12 else 32 if len(d["name"]) <= 20 else 24
    head = ('<div class="top" style="background-color: %s"/><div class='
            '"slant" style="background-color: %s"/><div class="head" style='
            '"color: %s"><div class="tags">%s · %d OF %d</div><div class='
            '"dname" style="font-size: %ddp">%s</div></div>' % (
                PART_COLOR[part], PART_COLOR[part], fg, esc(label),
                number, total, size, esc(d["name"])))
    # the numbers first, always in view; the try below them takes what is
    # left, cut at its foot if it must be (the owner, 2026-11-14: a long
    # try "completely hides the attempts counter"); the button hints are
    # in the pause menu ("tuck them in the pause menu")
    body = (
        '<div class="line">%s</div>'
        '<div id="status" class="line now"/>'
        '<div class="stats two"><div class="stat"><div id="tries" class="n">'
        '0</div><div class="l">tries</div></div><div class="stat"><div '
        'id="rate" class="n">-</div><div class="l">success</div></div><div '
        'class="stat"><div id="best" class="n">0</div><div class="l">best '
        'run</div></div></div>'
        '<div class="row lastrow"><div class="lbl">LAST 10</div>'
        '<div class="grow"/><div id="count" class="lbl">0 OF 0</div></div>'
        '<div id="last" class="sqs3">%s</div>%s'
        '<div class="try"><div class="row"><div class="lbl">THIS TRY</div>'
        '<div class="grow"/><div id="n" class="lbl">0</div></div>'
        '<div id="verdict" class="verdict">Go</div>'
        '<div id="why" class="why"/><div id="checks"/><div id="tl"/></div>'
        % (esc(about), last_squares([]),
           '<div id="stage" class="line stageline">Stage: %s</div>' % esc(
               stages[0].replace("-", " ").title()) if stages else ""))
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
                    "The port your code points at. If your router keeps "
                    "this port, your code stays the same. Change it only "
                    "if another program uses %d." % port))
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


# The input display: a GameCube controller, the owner's picture of one made
# into layers (padart.py: "make it look exactly like this, just slightly
# transparent with the interactive button highlights on press", the owner,
# 2026-11-14). Its layers all cover the same box, so each lies on the
# others exactly; PAD_ART has them (the client fills it; without them, no
# controller here, and the match shows TM-CE's). style.rcss (.pv) gives
# the box's size wherever it is.
PAD_W, PAD_H = float(padart.SHELL_W), float(padart.SHELL_H)
PAD_ART = {}
# the port's label ("P1"): its middle and foot, its width, as shares of
# the box (between the logo and START/PAUSE)
PAD_LABEL = padart.LABEL + (0.075,)
# the port whose controller a card's display is, unless told (the client
# sets it: the player's)
PAD_PORT = 0
# the buttons lit while held, as the pad's bits
PAD_BITS = (("A", 0x100), ("B", 0x200), ("X", 0x400), ("Y", 0x800),
            ("Z", 0x10), ("ST", 0x1000), ("DU", 0x8), ("DD", 0x4),
            ("DL", 0x1), ("DR", 0x2))
# how far a stick's cap goes at full tilt and a trigger goes in, in
# hundredths of the box across and down (left and top are shares of its
# width and of its height). The game's own display (ui.cpp) does the same.
PAD_TRAVEL = {s: (t / padart.SHELL_W * 100, t / padart.SHELL_H * 100)
              for s, t in padart.TRAVEL.items()}
PAD_PRESS = padart.PRESS / padart.SHELL_H * 100


def _pad_layer(name, ident=None, cls="pvl"):
    """One of the controller's layers (a bare element of that id without
    its picture: the display's updates still find it)."""
    at = ' id="%s"' % ident if ident else ""
    if name in PAD_ART:
        return '<img%s class="%s" src="%s"/>' % (at, cls,
                                                  picture(PAD_ART[name]))
    return '<div%s class="%s"/>' % (at, cls)


def pad_display(k, port=None):
    """An input display (the coach's pictures, the tutorial's example, the
    game's own over a match): a GameCube controller, slightly see-through,
    whose buttons light up while held, whose sticks' caps move and whose
    triggers light as far as they are pressed, its port on it ("P1": "a
    small label ... so it is clear"; `port` from 0, PAD_PORT if None). Its
    parts' ids are `c` + `k` + "i" + the part (A B X Y Z, ST for START,
    DU DD DL DR the D-pad, S and C the sticks' caps, L and R the triggers
    and Ll and Rl their lights, P the label); pad_lines says what they
    show."""
    def at(part):
        return "c%si%s" % (k, part)
    n = (PAD_PORT if port is None else port) + 1
    out = ['<div id="c%si" class="pv">' % k, _pad_layer("BASE", None,
                                                       "pvl pvbase")]
    for t in ("L", "R"):
        out.append('<div id="%s" class="pvm">%s</div>' % (
            at(t), _pad_layer(t + "-LIT", at(t + "l"), "pvl pvlit")))
    for part in padart.LIT:
        out.append(_pad_layer(part, at(part), "pvl pvk"))
    for cap in ("S", "C"):
        out.append('<div id="%s" class="pvm">%s</div>' % (
            at(cap), _pad_layer(cap, None, "pvl pvcap")))
    x, foot, w = PAD_LABEL
    out.append('<div id="%s" class="pvp p%d" style="left: %.2f%%; bottom: '
               '%.2f%%; width: %.2f%%;">P%d</div>' % (
                   at("P"), n, (x - w / 2) * 100, (1 - foot) * 100,
                   w * 100, n))
    out.append("</div>")
    return "".join(out)


def pad_lines(k, held, stick, cstick, ltrig, rtrig):
    """What the input display `k` shows for a pad, as the interface's
    commands: [(part, line)]. `held`: the pad's bits; `stick`, `cstick`:
    (x, y) from -1 to 1; `ltrig`, `rtrig`: how far in, 0 to 1 (a click all
    the way counts as 1)."""
    out = []
    for part, bit in PAD_BITS:
        out.append((part, "class c%si%s on %d" % (k, part,
                                                  1 if held & bit else 0)))
    for part, (x, y) in (("S", stick), ("C", cstick)):
        x = max(-1.0, min(1.0, x))
        y = max(-1.0, min(1.0, y))
        tx, ty = PAD_TRAVEL[part]
        out.append((part, "attr c%si%s style left: %.2f%%; top: %.2f%%;" % (
            k, part, x * tx + 0.0, -y * ty + 0.0)))
    for part, t in (("L", ltrig), ("R", rtrig)):
        t = max(0.0, min(1.0, t))
        out.append((part, "attr c%si%s style top: %.2f%%;" % (
            k, part, t * PAD_PRESS)))
        out.append((part + "l", "attr c%si%sl style opacity: %.2f;" % (
            k, part, t)))
    return out


def _picture(pic, kind, width=412.0):
    """A panel of the game's own pictures (Native.frames_view): `pic` is
    {"view": the interface's view, "crop": (left, top, width, height) of
    the game's 640x480 shown}. The client plays them (Client.Play): the
    frame, a tag at each press, how far along. `kind`: "you", "tgt", or
    "ex" (the tutorial's example, `width` wide)."""
    left, top, w, h = pic["crop"]
    s = width / w
    k = {"you": "y", "tgt": "t", "ex": "e"}[kind]
    cls = "cpic" + (" tall" if pic.get("tall") else "") + \
        (" tpic" if kind == "ex" else "")
    # the tutorial's cue over its example: "let go now", "too late"
    cue = '<div id="c%sq" class="tcue"/>' % k if kind == "ex" else ""
    return (
        '<div class="%s"><img class="cpimg" src="gxcopy://%d" style="left: '
        '%.1fdp; top: %.1fdp; width: %.1fdp; height: %.1fdp;"/>'
        '<div id="c%sf" class="cfr"/><div id="c%sp" class="cptag %s"/>%s%s'
        '<div class="cbar"><div id="c%sb" class="cbarf %s"/></div></div>' % (
            cls, pic["view"], -left * s, -top * s, 640.0 * s, 480.0 * s, k,
            k, kind, cue, pad_display(k), k, kind))


def input_cells(row, n, which, cls):
    """One row of an input timeline's cells, frames 1 to n, each of class
    `cls`: `which` "both" (the frames it was pressed or held, an outline,
    over the frame-perfect ones, solid, and the window, light), "you" (the
    presses only) or "should" (the fills only). The owner, 2026-11-14:
    "we don't want pressed and allowed rows as that is confusing. Let's
    just do a black outline for pressed, solid green for frame perfect,
    light green for window" (a press used to hide what was allowed under
    it: two rows, then)."""
    cells = []
    for i in range(1, n + 1):
        c = cls
        if which in ("should", "both"):
            if i in row["perfect"]:
                c += " perf"
            elif row["window"] and row["window"][0] <= i <= row["window"][1]:
                c += " win"
        if which in ("you", "both") and i in row["you"]:
            c += " you"
        cells.append('<div class="%s"/>' % c)
    return "".join(cells)


def coach_grid(tl, wrong, title="YOUR INPUTS, FRAME BY FRAME", you="you"):
    """The try's inputs frame by frame, a row each: the frames `you`
    pressed it on outlined, over the frame-perfect ones (solid) and the
    window (light); and a bracket from where one was due to where it came
    (`wrong`: coach.first_wrong). The columns' heads are `cgn1`... (the
    pictures' frame, marked as they play)."""
    if not tl:
        return ""
    n = tl["frames"]
    labels = tl.get("labels") or [str(i) for i in range(1, n + 1)]
    head = "".join('<div id="cgn%d" class="cgc cgn">%s</div>' % (i + 1,
                                                              esc(l))
                   for i, l in enumerate(labels))
    rows = ['<div class="cgr"><div class="cgl"/>%s</div>' % head]
    for row in tl["rows"]:
        rows.append(
            '<div class="cgr"><div class="cgl"><div class="cgb">%s</div>'
            '</div>%s</div>' % (esc(row["label"]),
                                input_cells(row, n, "both", "cgc")))
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
    legend = ('<div class="cleg"><div class="cgc you"/><div>%s</div>'
              '<div class="cgc perf"/><div>frame-perfect</div>'
              '<div class="cgc win"/><div>window</div></div>' % esc(you))
    # the legend beside the title; four inputs or more: closer together
    # (the card's height is fixed)
    return ('<div class="cgh"><div class="csec">%s</div><div class="grow"/>'
            '%s</div><div class="cgrid%s">%s</div>%s' % (
                esc(title), legend, " tight" if len(tl["rows"]) >= 4 else "",
                "".join(rows), bracket))


def frame_strip(tl, kind):
    """The frame boxes under a replay of the coach's card, in the same
    columns under both (the owner: "line up these frame boxes under each
    replay too ... so we can directly compare the frame sequences"):
    `kind` "you" (the frames you pressed each input on) or "tgt" (the
    frames allowed, and the frame-perfect ones). The heads are c{y,t}n1...
    (the frame shown, marked as the replay plays)."""
    if not tl:
        return ""
    n = tl["frames"]
    k = "y" if kind == "you" else "t"
    labels = tl.get("labels") or [
        str(i) if n <= 12 or i % 5 == 0 else "" for i in range(1, n + 1)]
    head = "".join('<div id="c%sn%d" class="cfc cfn">%s</div>' % (
        k, i + 1, esc(l)) for i, l in enumerate(labels))
    rows = ['<div class="cfsr"><div class="cfsl"/>%s</div>' % head]
    for row in tl["rows"]:
        rows.append('<div class="cfsr"><div class="cfsl">%s</div>%s</div>' % (
            esc(row["label"]), input_cells(
                row, n, "you" if kind == "you" else "should", "cfc")))
    return '<div class="cfs">%s</div>' % "".join(rows)


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
    tl = v.get("timeline")
    you = ('<div class="cpanel"><div class="csec you">YOUR TRY</div>%s%s<div '
           'class="ccap">%s</div></div>' % (mine, frame_strip(tl, "you"),
                                            esc(v["you_words"])))
    theirs = None
    if v.get("target_pic") is not None:
        theirs = _picture(v["target_pic"], "tgt")
    elif v.get("target") is not None:
        theirs = '<div class="cpath">%s</div>' % _path(
            v["target"][0], v["target"][1], "tgt")
    if theirs is not None:
        target = ('<div class="cpanel"><div class="csec tgt">WHAT IT SHOULD '
                  'LOOK LIKE</div>%s%s<div class="ccap">%s</div></div>' % (
                      theirs, frame_strip(tl, "tgt"),
                      esc(v["target_words"])))
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
                legend=True, label=None):
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
            esc(title), leg, PART_COLOR[part], fg,
            esc(label or part.upper()), number,
            total, esc(title.upper()), esc(name),
            hint_rows(hints or REPLAY_HINTS)))


def character_table(rows, me, what="Jump squat"):
    """Every character's number in a row of columns, one per value, the
    player's character marked (a lesson's table: the jump squat): `rows`
    [(value, id, name)]."""
    groups = {}
    for v, cid, name in rows:
        groups.setdefault(v, []).append((cid, name))
    out = []
    for v in sorted(groups):
        mine = any(cid == me for cid, _ in groups[v])
        names = ", ".join(
            ('<span class="tme">%s</span>' if cid == me else "%s")
            % esc(name) for cid, name in groups[v])
        out.append('<div class="tcol%s"><div class="tval">%d</div><div '
                   'class="tnames">%s</div></div>' % (" mine" if mine else "",
                                                      v, names))
    return ('<div class="th">%s, in frames, by character</div><div '
            'class="ttable">%s</div>' % (esc(what), "".join(out)))


def tutorial_card(v):
    """The tutorial: how to do it, shown (not the coach, which comes after
    misses and is about the try). The coach card's frame with a teal head.
    A lesson (the concept: what a jump squat is and how it differs from
    one character to the next; how to short hop) or a part of the
    technique: on the left the game's own pictures of its example, played
    large with the input display and a band on each frame ("Let go now"),
    frame by frame (Client.Play, panel "e"), or one still picture of it;
    on the right its words and, for a moving example, the caption of the
    frame shown; below, the example's inputs frame by frame or a table of
    every character; the parts as chips. `v`: title, sub, pic (_picture's)
    or None, still, text [paragraphs], timeline, table (character_table's),
    parts [(name, state)], keys [(button, words)]."""
    if v.get("pic") is not None:
        visual = _picture(v["pic"], "ex", 520.0)
    else:
        visual = ('<div class="cpath cnone tpic">The example could not be '
                  'recorded in this game.</div>')
    text = v.get("text", [])
    paras = text if isinstance(text, list) else [text]
    side = '<div class="twords">%s</div>' % "".join(
        '<div class="ttext">%s</div>' % esc(t) for t in paras)
    # the words fit beside the picture (300 high): smaller as they grow
    # (the owner, 2026-11-14: a long lesson pushed the card's head off its
    # place and clipped "LESSON 1 OF 1")
    n = sum(len(t) for t in paras) + (60 if v.get("pic") is not None and
                                      not v.get("still") else 0)
    fit = "t16" if n <= 360 else "t15" if n <= 440 else "t14" if \
        n <= 520 else "t13" if n <= 620 else "t12"
    if v.get("pic") is not None and not v.get("still"):
        side += ('<div class="th">This frame</div><div id="cecap" '
                 'class="tcap"/>')
    below = ""
    if v.get("timeline") and not v.get("still"):
        below = coach_grid(v["timeline"], None,
                           title="THE INPUTS, FRAME BY FRAME", you="pressed")
    if v.get("table"):
        below += v["table"]
    chips = "".join(
        '<div class="tchip %s"><div class="tpn">%d</div><div class="tpw">%s'
        '</div></div>' % (state, i + 1, esc(name))
        for i, (name, state) in enumerate(v.get("parts") or []))
    size = 34 if len(v["title"]) <= 26 else 28
    return (
        '<div class="cdim"/><div class="ccard tcard">'
        '<div class="chead"><div class="cstrip tut"/><div class="cbadge tut">'
        '<div class="un">Tutorial</div></div><div class="ctitle" style='
        '"font-size: %ddp;">%s</div><div class="grow"/><div class="cwhat">'
        '%s</div></div>'
        '<div class="tmain">%s<div class="tside %s">%s</div></div>'
        '<div class="cmid">%s</div>'
        '<div class="tchips">%s</div>'
        '<div class="grow"/><div class="cfoot">%s</div></div>' % (
            size, esc(v["title"]), esc(v.get("sub", "")).replace("\n",
                                                                "<br/>"),
            visual, fit, side, below, chips, "".join(
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
