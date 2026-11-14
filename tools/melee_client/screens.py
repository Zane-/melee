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
        '<div id="pause" class="pause"><div class="pbox"><div class="ptitle">'
        '<div class="un"><div id="ptitle">Paused</div></div></div>'
        '<div id="prows" class="prows"/><div class="phint">%s<div>Choose'
        '</div>%s<div>Change</div>%s<div>Back</div></div></div></div>'
        % (key("A"), key("D-SIDE"), key("B")))


def rays(points):
    """Light rays coming down on the stage (a drill's targets): `points`
    are where each meets the floor in the game's picture, in dp."""
    return "".join(
        '<div class="ray" style="left: %ddp; height: %ddp;"/>'
        '<div class="rayfoot" style="left: %ddp; top: %ddp;"/>'
        % (x - 9, y, x - 22, y - 5) for x, y in points)


def online_page(code, rows, at, status):
    """Playing a friend online: this side's code, what can be done (rows:
    (id, label, detail)), and what is happening (`status`)."""
    items = "".join(
        '<div class="prow%s"><div>%s</div><div class="grow"/>'
        '<div class="pv">%s</div></div>' % (
            " on" if i == at else "", esc(label), esc(detail))
        for i, (ident, label, detail) in enumerate(rows))
    return page("Online", (
        '<div class="onl"><div class="pbox onlbox">'
        '<div class="ptitle"><div class="un">Play a friend online</div></div>'
        '<div class="onlwhat">Send your friend your code and paste theirs: '
        'both games then find each other, without a server.</div>'
        '<div class="onlcode"><div class="onll">YOUR CODE</div>'
        '<div id="code" class="onlc">%s</div></div>'
        '<div id="orows" class="prows">%s</div>'
        '<div id="ostatus" class="onls">%s</div>'
        '<div class="phint">%s<div>Choose</div>%s<div>Back</div></div>'
        '</div></div>' % (esc(code), items, esc(status), key("A", dark=True),
                          key("B"))), paper=True)


def online_rows(rows, at):
    return "".join(
        '<div class="prow%s"><div>%s</div><div class="grow"/>'
        '<div class="pv">%s</div></div>' % (
            " on" if i == at else "", esc(label), esc(detail))
        for i, (ident, label, detail) in enumerate(rows))


def pause_rows(rows, at):
    """The pause menu's rows: (id, label, value or None); `at` the row in
    focus. A row with the id "-" is a gap."""
    out = []
    for i, (ident, label, value) in enumerate(rows):
        if ident == "-":
            out.append('<div class="pgap"/>')
            continue
        out.append(
            '<div class="prow%s"><div>%s</div><div class="grow"/>%s</div>' % (
                " on" if i == at else "", esc(label),
                '<div class="pv">&lt; %s &gt;</div>' % esc(value)
                if value is not None else ""))
    return "".join(out)


def hint_rows(rows):
    """(buttons, what they do) rows: the buttons drawn as the GameCube
    controller's, several to a row ("L R")."""
    return "".join(
        '<div class="hintrow"><div class="glyphs">%s</div><div>%s</div>'
        '</div>' % ("".join(key(b) for b in buttons.split()), esc(what))
        for buttons, what in rows)


def match_hints(drill=False, stages=False):
    """The sidebar's controls, in a match or a drill."""
    rows = [("START", "Pause"), ("START", "Hold: hide sidebar")]
    if drill:
        rows = [("D-UP", "Guide"), ("D-SIDE", "Scenario"),
                ("D-SIDE", "Hold: change drill")] + rows
    if stages:
        rows.append(("L R", "Hold: change stage"))
    return '<div class="hints">%s</div>' % hint_rows(rows)


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
    # id, class, name, what it is, built in this client
    ("train", "ink", "Train",
     "Pick a character and work through its course.", True),
    ("lab", "lab", "Lab",
     "Free practice against whoever you choose: nobody, the game's CPU or "
     "a trained model.", True),
    ("events", "events", "Events",
     "Training Mode's own events, page by page.", False),
    ("versus", "slate", "Versus",
     "Local or online: a trained model, the game's CPU, or a friend.", True),
    ("settings", "white", "Settings",
     "Input delay, rumble, controls, sound, display and online.", True),
]


def _tile(item, extra=""):
    """A panel. (No number in its corner: the owner, 2026-11-13, "I don't
    like the numbered buttons, there's no point to doing that!")"""
    ident, cls, name, about, built = item
    soon = "" if built else '<div class="soon">NOT YET</div>'
    return ('<div id="%s" class="tile %s"><div class="ring"/>'
            '<div class="in"><div class="row">'
            '<div class="grow"/>%s</div><div><div class="big">%s</div>'
            '<div class="sub">%s</div>%s</div></div>%s</div>' % (
                ident, cls, soon, esc(name), esc(about), extra[0]
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
        _tile(by["settings"]) + '</div></div></div></div>' +
        footer(by["train"][3], [("A", "Choose"), ("F11", "Fullscreen")]))
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
    standing out over the card's top edge, its traits and name."""
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
    out += '<div class="wclip"><div class="wedge"/></div>'
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
        about = ('<div class="about">No course of its own yet: A starts '
                 'free play.</div>')
        go = "Play"
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
    body = (
        header([title]) +
        '<div class="roster">' + "".join(tiles) + '</div>' +
        '<div id="card" class="card art">' +
        (inside or card(roster[focus], costume)) + '</div>' +
        footer(about, hints or [("A", "Choose"), ("Y", "Costume"),
                                ("B", "Back")],
               tab=roster[focus]["color"]))
    return page("Character select", body)


# ---- versus and lab: who is on the other side ---------------------------------

def opponent_card(c, who, what, stage, count, go):
    """The card on the opponent screen: the character, who plays it (`who`,
    with `what` that is in a few words; `count`: "2 of 31"), the stage."""
    form = ""
    if c.get("other") is not None:
        form = ('<div class="pick">%s<div>Switch to %s</div></div>' % (
            key("Y"), esc(c["other"]["name"])))
    return art_head(c) + (
        '<div class="body low"><div class="fact"><div class="fl">Played by'
        '</div><div class="fv big2">%s</div><div class="fl">%s</div></div>'
        '<div class="pick">%s<div>Change</div><div class="grow"/>'
        '<div class="lbl">%s</div></div>%s'
        '<div class="fact"><div class="fl">Stage</div><div class="fv big2">'
        '%s</div></div><div class="pick">%s%s<div>Change stage</div></div>'
        '<div class="grow"/><div class="go"><div class="un">%s<div>%s</div>'
        '</div></div></div>' % (
            esc(who), esc(what), key("X"), esc(count), form, esc(stage),
            key("L", wide=True), key("R", wide=True), key("A", dark=True),
            esc(go)))


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
        '<div class="line">Against a standing %s on %s.</div>'
        '<div class="about"/><div class="stats">%s</div>'
        '<div class="grow"/>%s' % (
            esc(opponent), esc(stage), stats, match_hints()))
    return page("Free play", over_game() + '<div id="rail" class="rail">%s'
                '<div class="body">%s</div></div>' % (head, body),
                paper=False)


# ---- the course hub -----------------------------------------------------------

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
            '<div id="p%d" class="tile slab %s"><div class="ring"/>'
            '<div class="in"><div class="row">'
            '<div class="grow"/>%s</div><div><div class="big">%s</div>'
            '<div class="d">%s</div></div><div>'
            '<div class="sqs">%s</div><div class="cnt2">%d of %d complete'
            '</div><div class="cnt2">Next: %s</div></div></div>'
            '</div>' % (
                i, PART_CLASS[part],
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
        '<div class="hubrow"><div id="free" class="tile lab"><div class='
        '"ring"/><div class="in"><div class="lbl">FREE PRACTICE</div><div>'
        '<div class="big">Free play</div><div class="sub">Against a standing'
        ' opponent.</div></div></div></div><div class="gap"/>' + tail +
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
