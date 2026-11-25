"""Answers ready before the player chooses.

The owner, 2026-11-24: "does our engine do tree searches? For example from
any given state, does it form the optimal inputs from the possible
predicted inputs? ... With this we could possibly precompute a bunch of
optimal reactions from likely inputs from a state". Until then an opponent
that covers the player's option (`chase`) stood still until it saw the
option, its reaction time late, and only then searched for an answer: the
answer came the search's time later still, from wherever it happened to
stand.

Here the tree is built before the player chooses. Thrown at the floor, the
player has a few options, all known from the moment of the throw: a tech in
place, a tech rolling either way, no tech. Each is played ahead in the
game, so where it leaves them and the first frame they can act again are
the game's, not a table's. Then, three levels:

1. how the opponent waits until it has seen which it is (a stance: stand;
   dash or walk toward where they land for some frames, then stand; or a
   read: the cover of one option begun without waiting to see);
2. the player's option, shown on the frame they land, seen `react` frames
   later;
3. the opponent's answer from that frame on, searched with the stance as
   the search's pre-roll and the option as the player's inputs (the
   engine's timing scan: a hold, then a grab or an attack). "sure": it
   connects before the player can act again, whatever they press; "late":
   it connects only if they do nothing in time.

    tab = table(n, cpu=1, player=0, react=15)   # the game untouched
    s = choose(tab, played=[], prior={}, rng=random.Random(1))
    s["pads"]                    # what to press until the option is seen
    s["covers"]["away"]["pads"]  # and from the frame it is seen on

The table is worked out in copies of the game, side by side, as early as
the situation is known: when the opponent's grab connects, its throw not
begun (`throw`: played ahead as its own next pads; it holds the grab until
the table is back, then throws, and the table's frames count from the
frame the player is thrown), or from the first frame of a throw or a fall
already under way. The flight is known before the release, for a player
who holds no direction; one who does is seen to leave the path
(`off_path`), and the table is made again. What the player then does is
answered on the frame the reaction time allows, with nothing left to
think about. Its standing row, the answers it must have, is handed over
as soon as it is searched (`early`): beside a game a person plays the
whole table takes most of a second. Measured (Captain Falcon's down throw
on Fox at 20%, reaction 15): standing still he has a sure cover for one
option of four; dashing 8 to 12 frames toward where Fox lands and then
standing, for all four.

A missed tech is a second table of the same kind (`getup_options`): lying
there the player gets up, rolls either way, attacks, or stays; each begun
on the first frame it can be, and the answers hold for a later one while
the opponent stands waiting.

What the player has done before weighs the choice of stance (`prior`:
counts of their options): against one who always techs away, the stance
that covers away; and where no stance covers an option by reacting (Sheik
at a reaction of 24 cannot reach a tech in place), a read of it, which
loses to the others: a player who mixes is not read.
"""
import collections
import math
import random
import threading
import time

from melee_actor.ahead import look
from melee_engine import sense as S
from melee_engine.contracts import searched
from melee_engine.drill import NONE
from melee_engine.search import preroll

RB = 0x20                     # R: the tech's button
AB = 0x100                    # A: the getup attack's
# what covers: grabs (standing, out of a dash, jump-cancelled), and the
# attacks of the ground
MOVES = "grab,dash_grab,jc_grab,dash_attack,ftilt,dsmash,fsmash,jab"
# before it: standing, a dash or a walk toward them (wherever they are:
# behind it too)
HOLDS = "none,in,walk_in"
DOWN_WAIT = (184, 192)        # lying there: a getup can begin
DOWN_BOUND = (183, 191)       # the bounce of a missed tech
TECH_STATES = (199, 200, 201)
# getting up from lying there: DownStand, DownAttack, DownFoward, DownBack
# (face up: 186 to 189; face down: 194 to 197)
GETUPS = (186, 187, 188, 189, 194, 195, 196, 197)
SURE, LATE = 1.0, 0.3         # what a cover is worth (LATE: if they dawdle)
# the timing scan of an answer (engine.c): every frame of the hold a
# branch, pressed only within `near` of them, stopped once `enough` lines
# connect
# connect, each move followed `trial` frames after its press (measured:
# the same tables as followed to the end, a tenth cheaper)
SEARCH = dict(scan=1, near=45, enough=3, trial=24)
# a throw's stick, x toward where the thrower faces
THROW_STICK = {"dthrow": (0, -1), "uthrow": (0, 1), "fthrow": (1, 0),
               "bthrow": (-1, 0)}
NEAR, FAR = 12.0, 24.0        # units to where they land: which stances
AFTER = 70                    # frames after the option is seen an answer has
LATE_ROOM = 14                # ... and past the frame they are free, at most
SPARE = 10                    # frames before the option is seen a table that
#                               is on the clock is back by
MOST = 140                    # frames looked ahead (a throw, and the fall)
OFF = 1.5                     # units off the path looked ahead: not that fall
# frames before the floor the hitstun may end by and it still be a tech
# chase (a jump or an air dodge begun there is no way out in the time)
LOOSE = 0
# frames a stance moves toward where they land before it stands
DASHES = (8, 12, 4, 16)
WALKS = (16, 8, 24)


def _plan(segs, most):
    """`player()`'s segments as a lookahead's plan, the last held on."""
    out = []
    for k, raw in segs:
        out.append((k, dict(buttons=(["R"] if raw[0] & RB else []) +
                            (["A"] if raw[0] & AB else []),
                            stick=(raw[1] / 127.0, raw[2] / 127.0))))
    out[-1] = (most, out[-1][1])
    return out


def throw_pad(throw, facing):
    """The pad of a throw (`THROW_STICK`) for a fighter facing `facing`."""
    x, y = THROW_STICK[throw]
    return (0, int(127 * x * (1 if facing >= 0 else -1)), int(127 * y), 0,
            0, 0, 0)


def _looks(n, games, asks):
    """Lookaheads side by side: [(port, target, plan, the target's pads or
    None)] -> their rows, each in a copy of its own (`games`) where there
    are that many, else one after the other in `n`."""
    if len(games) < len(asks):
        return [look(n, p, t, plan, stop=0, their=their).rows
                for p, t, plan, their in asks]
    out = [None] * len(asks)
    errors = []

    def one(i):
        try:
            p, t, plan, their = asks[i]
            out[i] = look(games[i], p, t, plan, stop=0, their=their).rows
        except Exception as e:
            errors.append(e)
    threads = [threading.Thread(target=one, args=(i,), daemon=True)
               for i in range(len(asks))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if errors:
        raise errors[0]
    return out


def _free_at(rows, since):
    return next((i + 1 for i, r in enumerate(rows)
                 if i >= since and r.a_state in S.FREE), len(rows))


def tech_options(n, cpu, player, most=MOST, games=(), throw=None):
    """The player's options as they come down onto the floor in tumble
    (thrown, from the first frame of the throw; held, with `throw`, the
    opponent's pad for the throw it is about to make: played ahead as its
    next pads; or hit), or None (they are not coming down, or can act
    before they land): dict(kind, land, x, cpu_free, side, path, options,
    throw_at: the frame they are thrown on, 0 if they were already; lead:
    the opponent's pads until then, the throw pressed once its grab has
    settled). Frames count from now: 1 is the next
    frame played. `land`: the frame they touch the floor; `x`: where;
    `cpu_free`: the first frame the opponent can act (its throw over);
    `side`: the way from the opponent to where they land (1 right);
    `path`: where they are after each frame until they land ([(x, y)]: a
    player who holds a direction through the throw leaves it). Each
    option: name ("in place", "in", "away", "none"; a roll toward the
    opponent's side is "in"), `their` (the player's pads from now: R and
    the stick as they land), `state` (their action state on the landing
    frame: how it is told apart), `free` (the first frame they can act
    again; a missed tech: the first they can begin a getup), `x` (where
    they are then). Played ahead and undone; `games`: copies of the game
    to look in, side by side."""
    st = n.state()
    me, them = st["p"][cpu], st["p"][player]
    if me is None or them is None:
        return None
    games = list(games)
    their, throw_at, mine_plan, lead = None, 0, [(most, {})], []
    if throw is not None and them["state"] in S.CAPTURED:
        # held: the throw first, pressed on the first frame the grab
        # allows it (the pull over: CatchWait; a stick held from before
        # is no throw) until they are thrown, then let go of
        if not games:
            return None           # (looked for in copies only: `table`)
        pull = _looks(n, games, [(cpu, player, [(most, {})], None)])[0]
        wait = 0 if me["state"] == S.CATCH_WAIT else next(
            (i + 1 for i, r in enumerate(pull)
             if r.a_state == S.CATCH_WAIT), None)
        if wait is None:
            return None
        press = ([(wait, NONE)] if wait else []) + [(most, throw)]
        first = _looks(n, games, [(player, cpu, [(most, {})], press)])[0]
        throw_at = next((i + 1 for i, r in enumerate(first)
                         if r.a_state in S.THROWN), None)
        if throw_at is None or throw_at <= wait:
            return None
        lead = [NONE] * wait + [tuple(throw)] * (throw_at - wait)
        their = ([(wait, NONE)] if wait else []) + \
            [(throw_at - wait, throw), (1, NONE)]
        stick = dict(buttons=[], stick=(throw[1] / 127.0, throw[2] / 127.0))
        mine_plan = ([(wait, {})] if wait else []) + \
            [(throw_at - wait, stick), (most, {})]
    elif them["state"] not in S.THROWN and (not them["air"] or
                                            S.free(them)):
        return None
    rows, mine = _looks(n, games, [(player, cpu, [(most, {})], their),
                                   (cpu, player, mine_plan, None)])
    land = None
    for i, r in enumerate(rows):
        if r.a_state in DOWN_BOUND:
            land = i + 1
            break
        if r.a_state in S.FREE and r.a_hitlag <= 0:
            return None           # free in the air first: not a tech chase
    if land is None:
        return None
    # the hitstun must last to the floor: tumbling without it they can
    # jump, attack or air dodge on the way down, and nothing is forced
    stun = 0
    for i, r in enumerate(rows[:land]):
        if r.a_state in S.THROWN + S.CAPTURED or r.a_hitstun > 0 or \
                r.a_hitlag > 0:
            stun = i + 1
    if stun < land - 1 - LOOSE:
        return None
    lx = rows[land - 1].a_x
    # (holding them it "can act": the first frame after its throw)
    cpu_free = next((i + 1 for i, r in enumerate(mine)
                     if i >= throw_at and r.a_state in S.FREE and
                     r.a_state != S.CATCH_WAIT), len(mine))
    cx = mine[min(cpu_free, len(mine)) - 1].a_x
    side = 1 if lx >= cx else -1
    kinds = (0, -127, 127)
    segs = [[(max(1, land - 3), NONE), (4, (RB, sx, 0, 0, 0, 0, 0)),
             (1, NONE)] for sx in kinds]
    got = _looks(n, games, [(player, cpu, _plan(s, most), their)
                            for s in segs])
    options = []
    for sx, seg, r in zip(kinds, segs, got):
        if len(r) < land or r[land - 1].a_state not in TECH_STATES:
            continue              # (no tech came of it: left out)
        state = r[land - 1].a_state
        free = _free_at(r, land - 1)
        end = r[free - 1].a_x
        name = "in place" if sx == 0 else \
            "in" if (end - lx) * (cx - lx) > 0 else "away"
        if any(o["state"] == state for o in options):
            continue
        options.append(dict(name=name, their=seg, state=state, free=free,
                            x=end))
    free = next((i + 1 for i, r in enumerate(rows)
                 if i >= land - 1 and r.a_state in DOWN_WAIT), len(rows))
    options.append(dict(name="none", their=[(1, NONE)],
                        state=rows[land - 1].a_state, free=free,
                        x=rows[free - 1].a_x))
    names = [o["name"] for o in options]
    for o in options:
        # (both rolls to one side of it: told apart by their own side)
        if names.count(o["name"]) > 1:
            o["name"] = "%s (%s)" % (o["name"],
                                     "left" if o["x"] < lx else "right")
    return dict(kind="tech", land=land, x=lx, cpu_free=cpu_free, side=side,
                gap=abs(lx - cx), throw_at=throw_at, lead=lead,
                path=[(r.a_x, r.a_y) for r in rows[:land]], options=options)


def getup_options(n, cpu, player, most=MOST, games=()):
    """The player's options lying on the floor after a missed tech (or in
    its bounce, about to lie there), as `tech_options` gives a tech's:
    "getup" (up), "roll in", "roll away", "getup attack", each begun on the
    first frame it can be (`land`: the frame the earliest shows; the
    player may begin later: while the opponent stands waiting the answers
    hold, counted from the frame the getup is seen), and "stay": nothing
    pressed (no state tells it: the chase's patience does). None if they
    are not lying there."""
    st = n.state()
    me, them = st["p"][cpu], st["p"][player]
    if me is None or them is None or \
            them["state"] not in DOWN_BOUND + DOWN_WAIT:
        return None
    rows, mine = _looks(n, list(games), [(player, cpu, [(most, {})], None),
                                         (cpu, player, [(most, {})], None)])
    if them["state"] in DOWN_WAIT:
        wait = 0
    else:
        wait = next((i + 1 for i, r in enumerate(rows)
                     if r.a_state in DOWN_WAIT), None)
        if wait is None:
            return None
    lx = rows[max(wait, 1) - 1].a_x
    cpu_free = next((i + 1 for i, r in enumerate(mine)
                     if r.a_state in S.FREE), 1)
    cx = mine[min(cpu_free, len(mine)) - 1].a_x
    side = 1 if lx >= cx else -1
    kinds = (("getup", (0, 0, 127, 0, 0, 0, 0)),
             ("roll", (0, -127, 0, 0, 0, 0, 0)),
             ("roll", (0, 127, 0, 0, 0, 0, 0)),
             ("getup attack", (AB, 0, 0, 0, 0, 0, 0)))
    segs = [([(wait, NONE)] if wait else []) + [(3, raw), (1, NONE)]
            for _, raw in kinds]
    got = _looks(n, list(games), [(player, cpu, _plan(s, most), None)
                                  for s in segs])
    options = []
    for (name, _), seg, r in zip(kinds, segs, got):
        show = next((i + 1 for i, x in enumerate(r)
                     if x.a_state in GETUPS), None)
        if show is None:
            continue
        state = r[show - 1].a_state
        free = _free_at(r, show - 1)
        end = r[free - 1].a_x
        if name == "roll":
            name = "roll in" if (end - lx) * (cx - lx) > 0 else "roll away"
        if any(o["state"] == state for o in options):
            continue
        options.append(dict(name=name, their=seg, state=state, free=free,
                            x=end, show=show))
    if not options:
        return None
    land = min(o["show"] for o in options)
    options.append(dict(name="stay", their=[(1, NONE)], state=None,
                        free=most + 200, x=lx, show=None))
    return dict(kind="getup", land=land, x=lx, cpu_free=cpu_free, side=side,
                gap=abs(lx - cx), throw_at=0, lead=[], path=[],
                options=options)


def stances(start, see, side, prefix=(), gap=None):
    """The ways to wait until the option is seen, [(name, pads)], each
    `see` frames long: standing; a dash or a walk toward where they land
    for some frames from frame `start` (the first it can act on, or the
    first the table can be there by), then standing; a dash away for a
    few. `prefix`: the pads already decided for the first frames (a stance
    it is in from the stage before, the throw it is about to make): every
    stance begins with them. `gap`: how far it is from where they land:
    near, the walks, a short dash and the dash away; far, the dashes
    (None: all of them)."""
    prefix = [tuple(p) for p in prefix][:see]
    start = max(start, len(prefix) + 1)
    head = prefix + [NONE] * (start - 1 - len(prefix))
    out = [("stand", (head + [NONE] * see)[:see])]
    room = see - (start - 1)
    dashes, walks, back = DASHES, WALKS, True
    if gap is not None and gap < NEAR:
        dashes, walks = (4,), (8, 16)
    elif gap is not None and gap < FAR:
        dashes, walks = (4, 8), (8, 16)
    elif gap is not None:
        dashes, walks, back = (8, 12, 4, 16), (16,), False
    for kind, amount, counts in (("dash", 127, dashes), ("walk", 60, walks)):
        for k in counts:
            if k > room:
                continue
            pads = head + [(0, amount * side, 0, 0, 0, 0, 0)] * k
            out.append(("%s in %d" % (kind, k),
                        (pads + [NONE] * see)[:see]))
    if back and room >= 8:
        pads = head + [(0, -127 * side, 0, 0, 0, 0, 0)] * 8
        out.append(("dash out 8", (pads + [NONE] * see)[:see]))
    return out


def cover(game, cpu, player, pads, option, moves=MOVES, holds=HOLDS,
          after=AFTER):
    """The opponent's answer to `option` having played `pads` first (its
    stance until it has seen the option: as many frames as that takes):
    the engine's timing scan from there (a hold, then one of `moves`), the
    player doing the option and then nothing. dict(kind: "sure" (it
    connects before they can act again), "late" (after: only if they do
    nothing in time) or None, at (the frame it connects, from the start),
    contact ("grab" or "hit"), line, pads (from the frame after `pads`),
    value, ms)."""
    if pads:
        preroll(game, pads)
    # (no further than a little past the frame they are free: a cover
    # later than that is no cover, and the frames cost)
    horizon = max(len(pads) + 12, min(len(pads) + after,
                                      option["free"] + LATE_ROOM))
    # (fresh: the throw the stance begins in is no contact of the answer's)
    r = searched(game, cpu, player, option["their"], horizon,
                 then=moves, hold=holds, stop=1, hit=10, held=50, fresh=1,
                 **SEARCH)
    good = [l for l in r.lines if l.contact in ("grab", "hit") and
            l.taken == 0]
    sure = [l for l in good if l.contact_at < option["free"]]
    best = (sure or good or [None])[0]
    if best is None:
        return dict(kind=None, ms=r.ms, at=None, pads=None, line=None,
                    contact=None, value=0.0)
    return dict(kind="sure" if sure else "late", at=best.contact_at,
                contact=best.contact, line=best.names, pads=best.raw(),
                value=best.value, ms=r.ms)


def worth(c):
    """What a cover is worth to a stance: `SURE`, `LATE` or nothing."""
    return SURE if c and c["kind"] == "sure" else \
        LATE if c and c["kind"] == "late" else 0.0


def lead_pads(prefix, start):
    """The pads before frame `start`: what was already decided, then
    standing."""
    prefix = [tuple(p) for p in prefix][:start - 1]
    return prefix + [NONE] * (start - 1 - len(prefix))


def table(n, cpu, player, react, moves=MOVES, holds=HOLDS, workers=16,
          deadline=None, reads=True, start=None, every=False, prefix=(),
          clock=False, throw=None, wide=False, early=None):
    """The stances and, for each, the answer to each of the player's
    options (the module's text), or None where there is nothing to chase.
    dict(kind, land, x, cpu_free, side, path, see (the frames until an
    option is seen: land + react), start, options, stances: [dict(name,
    pads, covers: {option name: cover}, read: the option it reads, if it
    is one)], ms (searching, summed), wall, searches, partial, stopped,
    times).

    The searches are one list in the order they matter, worked through
    side by side in `workers` copies of the game: the standing row
    (always: it is what the first version had, without its wait), each
    option's cover begun at once (a read's line), the other stances; for
    an option standing does not cover surely by reacting, its read as a
    stance of its own (`reads`), as soon as its line is known. It stops
    when a stance covers every option surely (`every`: it does not;
    "stopped"), or after `deadline` seconds: the stances not finished are
    left out ("partial"). `clock`: while a person plays, its time is what
    the throw leaves it: until a little before the option is seen (`see`
    frames at 60 a second, less `SPARE`), `deadline` at most. `throw`:
    the pad of the throw the opponent is about to make, the player held
    (`throw_pad`): the table is then made before the throw begins, its
    frames counted from now with the throw made at once (`throw_at`: the
    frame they are thrown on; the opponent may throw later: the table
    holds, counted from the frame they are thrown). `wide`: every stance,
    however far it has to go (else those that fit the distance). `early`:
    a dict that is given the table of the standing row alone ("tab") as
    soon as that row is done: the answers it must have, there while the
    rest is still searched (a table made beside a game a person plays
    comes when it comes). `start`: the first frame a stance may differ
    from standing on (the frame the table is expected back by, while a
    person plays; never before the opponent can act). `prefix`: the pads
    already decided for the next frames. The game is untouched."""
    from melee_engine.recover import copies
    t0 = time.time()
    until = None if deadline is None else t0 + max(0.0, deadline)
    games = copies(n, workers) if workers >= 2 else []
    times = dict(copies=(time.time() - t0) * 1000.0)
    try:
        sit = tech_options(n, cpu, player, games=games, throw=throw) or \
            getup_options(n, cpu, player, games=games)
        times["options"] = (time.time() - t0) * 1000.0
        if sit is None:
            return None
        see = sit["land"] + react
        options = sit["options"]
        if clock:
            room = t0 + max(0.1, (see - SPARE) / 60.0)
            until = room if until is None else min(until, room)
        if sit["throw_at"]:
            # (its own throw first: every stance begins with it)
            prefix = list(sit["lead"])
        start = max(sit["cpu_free"], start or 1, len(prefix) + 1)
        todo = stances(start, see, sit["side"], prefix,
                       None if wide else sit["gap"])
        # (lying there: a read of a getup they have not begun is a guess
        # at its frame too: none)
        reads = reads and sit["kind"] == "tech"
        k = len(options)
        queue = collections.deque()
        for j, o in enumerate(options):
            queue.append((("s", 0, j), todo[0][1], o))
        if reads:
            for j, o in enumerate(options):
                queue.append((("line", j), lead_pads(prefix, start), o))
        for i in range(1, len(todo)):
            for j, o in enumerate(options):
                queue.append((("s", i, j), todo[i][1], o))
        found = {}
        lock = threading.Condition()
        box = dict(running=0, stop=False, late=False, errors=[], ms=0.0,
                   count=0)

        def row(i):
            return [found.get(("s", i, j)) for j in range(k)]

        def read_pads(j):
            c = found[("line", j)]
            return (lead_pads(prefix, start) + list(c["pads"]) +
                    [NONE] * see)[:see]

        def first_row():
            """(Under the lock.) The standing row alone, as a table."""
            r = row(0)
            if early is None or "tab" in early or \
                    any(c is None for c in r):
                return
            early["tab"] = dict(
                sit, see=see, react=react, start=start, ms=box["ms"],
                wall=(time.time() - t0) * 1000.0, searches=box["count"],
                partial=True, stopped=False, times=dict(times),
                stances=[dict(name=todo[0][0], pads=todo[0][1], read=None,
                              covers={o["name"]: c
                                      for o, c in zip(options, r)})])

        def got(key):
            """(Under the lock.) What a result leads to: a read's rows,
            or the end."""
            if key[0] == "s" and key[1] == 0:
                first_row()
            if key[0] == "line" or (key[0] == "s" and key[1] == 0):
                j = key[-1]
                line, stand = found.get(("line", j)), found.get(("s", 0, j))
                if reads and line and stand and line["kind"] == "sure" \
                        and stand["kind"] != "sure" and \
                        ("read", j, j) not in found:
                    found[("read", j, j)] = line
                    for x in range(k - 1, -1, -1):
                        if x != j:
                            queue.appendleft((("read", j, x), read_pads(j),
                                              options[x]))
            if key[0] == "s" and not every:
                r = row(key[1])
                if all(c is not None and c["kind"] == "sure" for c in r):
                    box["stop"] = True      # it covers them all

        def work(game):
            while True:
                with lock:
                    while not queue and box["running"] and not box["stop"]:
                        lock.wait(0.05)
                    if box["stop"] or not queue:
                        lock.notify_all()
                        return
                    key, pads, o = queue.popleft()
                    forced = key[0] == "s" and key[1] == 0
                    if not forced and until is not None and \
                            time.time() >= until:
                        box["late"] = True
                        continue          # out of time: left out
                    box["running"] += 1
                c = None
                try:
                    c = cover(game, cpu, player, pads, o, moves, holds)
                except Exception as e:
                    box["errors"].append(e)
                with lock:
                    box["running"] -= 1
                    if c is not None:
                        found[key] = c
                        box["ms"] += c["ms"]
                        box["count"] += 1
                        got(key)
                    lock.notify_all()
        if len(games) >= 2:
            threads = [threading.Thread(target=work, args=(g,), daemon=True)
                       for g in games]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        else:
            work(games[0] if games else n)
        if box["errors"] and not box["count"]:
            raise box["errors"][0]
        times["searches"] = (time.time() - t0) * 1000.0
        out = []
        for i, (name, pads) in enumerate(todo):
            r = row(i)
            if any(c is None for c in r):
                continue
            out.append(dict(name=name, pads=pads, read=None,
                            covers={o["name"]: c
                                    for o, c in zip(options, r)}))
        lead = len(lead_pads(prefix, start))
        for j, o in enumerate(options):
            if ("read", j, j) not in found:
                continue
            r = [found.get(("read", j, x)) for x in range(k)]
            if any(c is None for c in r):
                continue
            covers = {x["name"]: c for x, c in zip(options, r)}
            covers[o["name"]] = dict(r[j],
                                     pads=list(r[j]["pads"][see - lead:]))
            out.append(dict(name="read " + o["name"], pads=read_pads(j),
                            read=o["name"], covers=covers))
    finally:
        for g in games:
            g.close()
    return dict(sit, see=see, react=react, start=start, stances=out,
                ms=box["ms"], wall=(time.time() - t0) * 1000.0,
                searches=box["count"], partial=box["late"],
                stopped=box["stop"], times=times)


def expected(stance, options, prior):
    """What a stance is worth against a player who chooses as `prior`
    counts say ({option name: times}; one more for each, so that nothing
    is ever ruled out)."""
    total = sum(prior.get(o["name"], 0) + 1.0 for o in options)
    return sum((prior.get(o["name"], 0) + 1.0) / total *
               worth(stance["covers"].get(o["name"])) for o in options)


def choose(tab, played=(), prior=None, rng=None, temperature=0.06):
    """One of the table's stances whose first pads are the ones already
    played (`played`: raw pads since the table was asked for), by a softmax
    over what each is worth against this player (`expected`): the best
    most often, never one only. None if none fits."""
    prior = prior or {}
    rng = rng or random.Random(0)
    played = [tuple(p) for p in played]
    fit = [s for s in tab["stances"]
           if [tuple(p) for p in s["pads"][:len(played)]] ==
           played[:len(s["pads"])]]
    if not fit:
        return None
    vals = [expected(s, tab["options"], prior) for s in fit]
    best = max(vals)
    w = [math.exp((v - best) / max(temperature, 1e-6)) for v in vals]
    s = rng.choices(fit, weights=w)[0]
    return dict(s, worth=vals[fit.index(s)], best=best)


def option_of(tab, state):
    """The table's option the player's action state `state` is, or None."""
    for o in tab["options"]:
        if o["state"] is not None and (
                o["state"] == state or (o["name"] == "none" and
                                        state in DOWN_BOUND + DOWN_WAIT)):
            return o
    return None


def off_path(tab, k, them):
    """Whether the player, `k` frames after the table was asked for, is
    off the fall it was made for (they held a direction through the
    throw: its answers are another fall's)."""
    path = tab.get("path") or []
    if not 1 <= k <= len(path) - 1:
        return False
    x, y = path[k - 1]
    return abs(them["x"] - x) > OFF or abs(them["y"] - y) > OFF


def describe(tab):
    """The table as lines for a person: each stance, and for each option
    its cover and the frame it connects on."""
    opts = tab["options"]
    out = ["%s: shows on frame %d at x %.1f; the opponent can act on frame "
           "%d; an option is seen on frame %d (reaction %d); %d searches, "
           "%.0f ms%s" % (tab["kind"], tab["land"], tab["x"],
                          tab["cpu_free"], tab["see"], tab["react"],
                          tab["searches"], tab["wall"],
                          ", not all of them" if tab["partial"] else ""),
           "%-16s %s" % ("", "  ".join("%-24s" % ("%s (free %d)" % (
               o["name"], o["free"])) for o in opts))]
    for s in tab["stances"]:
        cells = []
        for o in opts:
            c = s["covers"].get(o["name"])
            cells.append("%-24s" % (
                "%s %s %s" % (c["kind"].upper() if c["kind"] == "sure"
                              else c["kind"], (c["line"] or "").replace(
                                  "hold_", "")[:13], c["at"])
                if c and c["kind"] else "nothing"))
        out.append("%-16s %s" % (s["name"], "  ".join(cells)))
    return out
