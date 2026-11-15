"""Keys for Versus's classic select (client.show_vselect: one grid of the
characters, a card per port below it) in the client tests. Each function
takes the client `c` and the test's `tap(key, after=n)`; every loop has a
budget and says what it waited for."""
import screens


def to_char(c, tap, cid, budget=30):
    """The grid's cursor onto character `cid` (a place's other form, as
    Sheik, is reached through its place and X)."""
    ids = [x["id"] for x in c.roster]
    other = None
    if cid not in ids:
        other = cid
        cid = next(x["id"] for x in c.roster
                   if (x.get("other") or {}).get("id") == other)
    want, cols = ids.index(cid), screens.VCOLUMNS
    for _ in range(budget):
        if c.varea != "grid":
            tap("Up", after=3)
            continue
        at = c.vat
        if at == want:
            if other is not None and c.roster[at]["id"] != other:
                tap("v", after=3)               # X: the other form
            return
        if at // cols != want // cols:
            tap("Down" if want // cols > at // cols else "Up", after=2)
        else:
            tap("Right" if want > at else "Left", after=2)
    raise RuntimeError("the grid's cursor never reached %s" % cid)


def to_card(c, tap, i, budget=20):
    """The cursor onto port `i`'s card (len(slots): the add card)."""
    for _ in range(budget):
        if c.varea == "grid":
            tap("Down", after=3)
            continue
        if c.vcard == i:
            return
        tap("Right" if c.vcard < i else "Left", after=3)
    raise RuntimeError("the cursor never reached card %d" % i)


def open_row(c, tap, port, key, budget=12):
    """Port `port`'s card open, its row `key` in focus."""
    to_card(c, tap, port)
    if c.vedit is None:
        tap("x", after=4)
    keys = [k for k, _, _ in c.vrows(port)]
    for _ in range(budget):
        if c.vedit is not None and keys[c.vedit] == key:
            return
        tap("Down" if c.vedit < keys.index(key) else "Up", after=3)
    raise RuntimeError("card %d's row %s never in focus" % (port, key))


def pick(c, tap, port, cid):
    """Character `cid` for port `port`."""
    if c.vactive != port or c.varea != "grid":
        if port == 0:
            to_card(c, tap, 0)
            tap("x", after=4)                   # your card: the grid
        else:
            open_row(c, tap, port, "char")
            tap("x", after=4)                   # Character: the grid
    to_char(c, tap, cid)
    tap("x", after=6)


def set_kind(c, tap, port, kind, budget=8):
    """Who plays port `port`: "cpu", "model", "dummy", "human"."""
    open_row(c, tap, port, "kind")
    for _ in range(budget):
        if c.vslots[port]["kind"] == kind:
            break
        tap("Right", after=3)
    else:
        raise RuntimeError("card %d never became %s" % (port, kind))
    tap("z", after=4)                           # closed


def set_level(c, tap, port, level):
    open_row(c, tap, port, "level")
    for _ in range(10):
        now = c.vslots[port].get("level", 9)
        if now == level:
            break
        tap("Right" if level > now else "Left", after=3)
    tap("z", after=4)


def remove(c, tap, port):
    """Port `port` out of the match (Player: Remove, then A)."""
    open_row(c, tap, port, "kind")
    for _ in range(8):
        if c.vslots[port]["kind"] == "remove":
            break
        tap("Right", after=3)
    tap("x", after=4)


def add(c, tap):
    """A player more (a level 9 CPU); its character is chosen next."""
    to_card(c, tap, len(c.vslots))
    tap("x", after=6)


def setup(c, tap, me, opp, kind="dummy", level=9):
    """You as `me` against `opp` played by `kind`, two players."""
    for _ in range(4):
        if len(c.vslots) <= 2:
            break
        remove(c, tap, len(c.vslots) - 1)
    pick(c, tap, 0, me)
    if c.vslots[1]["kind"] != kind:
        set_kind(c, tap, 1, kind)
    if not (c.mode_class() and c.mode_class().fighters):
        pick(c, tap, 1, opp)
    if kind == "cpu" and c.vslots[1].get("level", 9) != level:
        set_level(c, tap, 1, level)
