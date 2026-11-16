"""How an opponent's body moves: its footsies measured, per character, on
the headless game (docs/ai/opponent-vocabulary.md, "footsies"; the engine
opponent's movement before it commits).

    python -u tools/melee_engine/gait.py [--chars sheik,marth] \
        [--body approach,footsies] [--standin stand,shield,move] \
        [--frames 1200] [--seed 1] [--json OUT] [--trace DIR]
    python -u tools/melee_engine/gait.py --calibrate [--write]

A body plays port 2 (the opponent) against a stand-in on port 1 (Fox, the
player) on Final Destination, from the drill's start (the player at -20,
the opponent at 20) for `--frames` frames. Bodies:

- approach: the body an approach moves with until it commits
  (drill.Footsies, band 12 to 30 units: what a drill's opponent does most
  of the time before it attacks);
- footsies: the script step {"do": "footsies", "range": [28, 42]}
  (fox-shine-oos's first step, held for the whole run);
- outside: {"do": "footsies", "range": "outside"} (the player's range
  searched every 4 frames: slower);
- old-approach, old-footsies, old-outside: the same with git HEAD's drill.Footsies
  and behave.py (before and after in one run);
- model: the slippi-ai body (human.ModelBody) where a model exists for the
  character against Fox (needs the policy server's Python and a GPU);
- drill, old-drill: fox-shine-oos's opponent for the character, its whole script
  looped (footsies, approaches committed to the shield and played): the
  numbers over the frames its body moves it, the lag over all.

Stand-ins: stand (lets go), shield (holds it; kept full), move (walks and
dashes in and out about its place, at random lengths).

Reported per run (frames are the body's, the share of all):

- lag: TurnRun (turnaround), RunBrake (the skid) and Run, which footsies
  never chooses: the "turn around lag" a person sees;
- dash, the dash dance's one-frame turns, pivots and slow turns (Turn
  played out), wait, walk, crouch, wavedash (jump squat into its landing),
  shield, jump, teeter, other;
- dash backs (a dash turned into one the other way inside the initial
  dash), dash dances (a dash and at least one dash back), the dash legs'
  lengths in them (mean, spread, how many different), dashes that became
  a run, reversals the game ignored (a flick in a dash's first frames);
- in band (the body's band of distances), facing the player, distance's
  mean and spread, frames teetering at the ledge.

`--calibrate`: each character's movement measured from the game (initial
dash length, the dash animation, jump squat, a wavedash's slide, a pivot's
turn, dash and walk speeds, friction) and compared with the table the
body plans with (footwork.json); `--write` writes it.
"""
import argparse
import json
import os
import random
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for _p in (os.path.join(ROOT, "tools", "melee_native"),
           os.path.join(ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

NONE = (0, 0, 0, 0, 0, 0, 0)
SHIELD = (0x20, 0, 0, 0, 0, 0, 255)
TOP = ("fox", "marth", "jigglypuff", "falco", "sheik", "captain-falcon",
       "peach", "ice-climbers", "pikachu", "yoshi", "samus")
FD_HALF = 85.5657
RANGE = (28.0, 42.0)        # the footsies body's band (--range)

# ---- what a frame's state counts as ------------------------------------------

LAG = {19: "turn_run", 23: "run_brake", 21: "run", 22: "run"}
SIMPLE = {14: "wait", 15: "walk", 16: "walk", 17: "walk", 20: "dash",
          39: "crouch", 40: "crouch", 41: "crouch", 42: "landing",
          245: "teeter", 246: "teeter"}
SHIELDS = set(range(178, 183))
YOSHI_SHIELD = set(range(341, 346))
AIR = set(range(25, 39)) | {236}
CLASSES = ("turn_run", "run_brake", "run", "dash", "dd_turn", "pivot",
           "wait", "walk", "crouch", "wavedash", "shield", "jump", "landing",
           "teeter", "other")


def classify(rows, char):
    """Each frame's class (rows: [(state, facing, ...)]). The one-frame
    turn of a dash dance (Turn between two dashes, facing flipped) apart
    from a pivot or slow turn played out; a jump squat into an air dodge
    into its landing (LandingFallSpecial) a wavedash."""
    out = [None] * len(rows)
    n = len(rows)
    for i, r in enumerate(rows):
        s = r["state"]
        if s in LAG:
            out[i] = LAG[s]
        elif s in SIMPLE:
            out[i] = SIMPLE[s]
        elif s in SHIELDS or (char == "yoshi" and s in YOSHI_SHIELD):
            out[i] = "shield"
        elif s == 18:
            nxt = rows[i + 1]["state"] if i + 1 < n else None
            out[i] = "dd_turn" if nxt == 20 else "pivot"
        elif s == 24 or s in AIR or s == 43:
            out[i] = "air"
        else:
            out[i] = "other"
    # air: a wavedash when a jump squat leads to LandingFallSpecial within a
    # few airborne frames; otherwise a jump
    i = 0
    while i < n:
        if out[i] != "air":
            i += 1
            continue
        j = i
        while j < n and out[j] == "air":
            j += 1
        states = [rows[k]["state"] for k in range(i, j)]
        airborne = sum(1 for s in states if s in AIR)
        kind = "wavedash" if 43 in states and airborne <= 4 else "jump"
        for k in range(i, j):
            out[k] = kind
        i = j
    return out


def dashes(rows):
    """The dashes: [(start, length, facing, how it ended)], how: "back" (a
    dash back), "pivot", "run", "wait", "jump", "other"."""
    out = []
    i, n = 0, len(rows)
    while i < n:
        if rows[i]["state"] != 20:
            i += 1
            continue
        j = i
        while j < n and rows[j]["state"] == 20 and \
                rows[j]["facing"] == rows[i]["facing"]:
            j += 1
        how = "end"
        if j < n:
            s = rows[j]["state"]
            if s == 18:
                how = "back" if j + 1 < n and rows[j + 1]["state"] == 20 \
                    else "pivot"
            elif s == 20:
                how = "back"            # (a turn the frame did not show)
            elif s in (21, 22):
                how = "run"
            elif s == 14:
                how = "wait"
            elif s == 24:
                how = "jump"
            elif s in SHIELDS:
                how = "shield"
            else:
                how = "other"
        out.append((i, j - i, rows[i]["facing"], how))
        i = j
    return out


def measure(rows, char, band_of=None):
    """The numbers of one run (rows: the body's frames, each a dict of
    state, facing, x, them_x, raw, band)."""
    n = len(rows)
    cls = classify(rows, char)
    counts = {c: 0 for c in CLASSES}
    for c in cls:
        counts[c] = counts.get(c, 0) + 1
    ds = dashes(rows)
    legs = []           # lengths of the legs of dash dances
    chains = 0
    k = 0
    while k < len(ds):
        if ds[k][3] != "back":
            k += 1
            continue
        chain = [ds[k]]
        while k + 1 < len(ds) and ds[k][3] == "back" and \
                ds[k + 1][0] <= ds[k][0] + ds[k][1] + 2:
            k += 1
            chain.append(ds[k])
        chains += 1
        legs += [d[1] for d in chain]
        k += 1
    backs = sum(1 for d in ds if d[3] == "back")
    ran = sum(1 for d in ds if d[3] == "run")
    # a flick the game ignored: the stick smashed against the dash's
    # direction (fresh this frame) and the next frame still that dash
    ignored = 0
    for i in range(1, n - 1):
        r, p = rows[i], rows[i - 1]
        if r["state"] != 20:
            continue
        lx, plx = r["raw"][1], p["raw"][1]
        fresh = lx * r["facing"] <= -64 and plx * r["facing"] > -64
        if fresh and rows[i + 1]["state"] == 20 and \
                rows[i + 1]["facing"] == r["facing"]:
            ignored += 1
    dist = [abs(r["them_x"] - r["x"]) for r in rows]
    inband = sum(1 for r, d in zip(rows, dist)
                 if r["band"] is not None and
                 r["band"][0] <= d <= r["band"][1])
    # within 3 units of the band, and the closest inside its low end
    near = sum(1 for r, d in zip(rows, dist)
               if r["band"] is not None and
               r["band"][0] - 3.0 <= d <= r["band"][1] + 3.0)
    under = [r["band"][0] - d for r, d in zip(rows, dist)
             if r["band"] is not None]
    facing = sum(1 for r in rows
                 if r["facing"] * (r["them_x"] - r["x"]) > 0)
    lag = counts["turn_run"] + counts["run_brake"] + counts["run"]
    out = dict(frames=n, lag=lag, lag_pct=100.0 * lag / max(n, 1),
               counts=counts, dashes=len(ds), dash_backs=backs,
               dash_dances=chains, ran=ran, ignored=ignored,
               backs_per_s=60.0 * backs / max(n, 1),
               legs_mean=statistics.mean(legs) if legs else 0.0,
               legs_sd=statistics.pstdev(legs) if len(legs) > 1 else 0.0,
               legs_distinct=len(set(legs)),
               legs_range=(min(legs), max(legs)) if legs else None,
               inband_pct=100.0 * inband / max(n, 1),
               near_pct=100.0 * near / max(n, 1),
               dist_min=min(dist) if dist else 0.0,
               under_most=max(under) if under else 0.0,
               facing_pct=100.0 * facing / max(n, 1),
               dist_mean=statistics.mean(dist) if dist else 0.0,
               dist_sd=statistics.pstdev(dist) if len(dist) > 1 else 0.0)
    return out


# ---- stand-ins ---------------------------------------------------------------

class Standin:
    """The player's pad each frame. move: walks and dashes in and out about
    where it started (within 25 units of it), at random lengths; a dash is
    let go of before it is a run. dance: a dash dance in place about where
    it started, each leg turned inside the initial dash (3 to 6 frames,
    two more toward where it started once 6 units off it): it never runs."""

    def __init__(self, kind, rng, home=-20.0):
        self.kind, self.rng, self.home = kind, rng, home
        self.queue = []

    def __call__(self, st):
        if self.kind == "stand":
            return NONE
        if self.kind == "shield":
            return SHIELD
        if self.kind == "dance" and not self.queue:
            off = st["p"][0]["x"] - self.home
            way = -getattr(self, "way", -1)
            self.way = way
            n = self.rng.randint(3, 6) if hasattr(self, "legs") else 5
            self.legs = True
            if off * way < -6:
                n += 2
            self.queue = [(0, 127 * way, 0, 0, 0, 0, 0)] * n
        if not self.queue:
            me = st["p"][0]
            off = me["x"] - self.home
            way = -1 if off > 12 else 1 if off < -12 else \
                self.rng.choice((1, -1))
            kind = self.rng.choice(("walk", "dash", "wait"))
            if kind == "walk":
                self.queue = [(0, 60 * way, 0, 0, 0, 0, 0)] * \
                    self.rng.randint(8, 24) + [NONE]
            elif kind == "dash":
                self.queue = [NONE] + [(0, 127 * way, 0, 0, 0, 0, 0)] * \
                    self.rng.randint(3, 8) + [NONE] * self.rng.randint(
                        18, 26)
            else:
                self.queue = [NONE] * self.rng.randint(10, 40)
        return self.queue.pop(0)


# ---- bodies ------------------------------------------------------------------

def _old(name):
    """git HEAD's tools/melee_engine/NAME.py as a module (the body before
    this change), its own imports the current modules'."""
    import types
    src = subprocess.run(["git", "show", "HEAD:tools/melee_engine/%s.py" %
                          name], cwd=ROOT, capture_output=True, text=True,
                         check=True).stdout
    mod = types.ModuleType("old_" + name)
    exec(compile(src, "HEAD:%s.py" % name, "exec"), mod.__dict__)
    return mod


def _old_drill():
    return _old("drill")


def _old_behave():
    """HEAD's behave.py with HEAD's drill.Footsies as its body."""
    mod = _old("behave")
    mod.Body = _old_drill().Footsies
    return mod


class DirectBody:
    """A drill.Footsies (or any body with next(st)) as a body to measure."""

    def __init__(self, body):
        self.body = body

    def pad(self, st, their):
        return self.body.next(st)

    def footwork(self):
        return self.body if hasattr(self.body, "errs") else None

    @property
    def band(self):
        return getattr(self.body, "band", None)

    def stop(self):
        pass


class ScriptBody:
    """A script's footsies step held for the whole run (`behave`: the
    behaviours' module to play it with, HEAD's for the body before)."""

    def __init__(self, n, spec, seed, char, behave=None):
        from melee_engine.drill import Here
        from melee_engine import script
        self.script, self.behave = script, behave
        self.opp = script.Opponent(Here(n), 1, 0, dict(script=[spec]),
                                   seed=seed, half=FD_HALF, char=char)

    def pad(self, st, their):
        if self.behave is None:
            return self.opp.pad(st, their)
        saved = self.script.B
        self.script.B = self.behave
        try:
            return self.opp.pad(st, their)
        finally:
            self.script.B = saved

    @property
    def band(self):
        cur = self.opp.cur
        return getattr(getattr(cur, "body", None), "band", None)

    def footwork(self):
        body = getattr(self.opp.cur, "body", None)
        return body if hasattr(body, "errs") else None

    def stop(self):
        self.opp.stop()


class ModelOpp:
    def __init__(self, char):
        from melee_engine import human
        model = human.find_model(char, "fox")
        if model is None:
            raise RuntimeError("no model for %s" % char)
        self.model = model
        self.body = human.ModelBody(model, port=1, opponent=0)
        self.band = None

    def pad(self, st, their):
        return self.body.step(st)

    def footwork(self):
        return None

    def stop(self):
        self.body.close()


class DrillBody(ScriptBody):
    """A drill scenario's whole opponent script (fox-shine-oos's for the
    character: footsies, then approaches committed to and played), looped:
    a frame is the body's while the script's footsies or an approach's body
    moves it (`body` in each row), the rest its attacks and their lag."""

    def __init__(self, n, char, seed, drill="fox-shine-oos", behave=None):
        from melee_engine.drill import Here
        from melee_engine import script
        spec = json.load(open(os.path.join(ROOT, "data", "drills",
                                           drill + ".json")))
        op = next(s["opponent"] for s in spec["scenarios"]
                  if s.get("opponent", {}).get("character") == char and
                  "script" in s["opponent"])
        self.script, self.behave = script, behave
        self.opp = script.Opponent(Here(n), 1, 0, op, seed=seed,
                                   half=FD_HALF, char=char)

    @property
    def band(self):
        body = self.footwork()
        return getattr(body, "band", None)

    @property
    def moving(self):
        cur = self.opp.cur
        if cur is None:
            return False
        o = getattr(cur, "opp", None)
        return o is None or o.mode == "neutral"

    def footwork(self):
        cur = self.opp.cur
        body = getattr(cur, "body", None) or getattr(
            getattr(cur, "opp", None), "body", None)
        return body if hasattr(body, "errs") else None


def make_body(kind, n, char, seed):
    rng = random.Random(seed)
    if kind in ("drill", "old-drill"):
        return DrillBody(n, char, seed, behave=_old_behave()
                         if kind == "old-drill" else None)
    if kind in ("approach", "old-approach"):
        if kind == "old-approach":
            F = _old_drill().Footsies
        else:
            from melee_engine.drill import Footsies as F
        return DirectBody(F(1, 0, band=(12.0, 30.0), rng=rng, half=FD_HALF))
    if kind in ("footsies", "old-footsies", "outside", "old-outside"):
        spec = {"do": "footsies",
                "range": "outside" if kind.endswith("outside") else
                list(RANGE)}
        return ScriptBody(n, spec, seed, char, behave=_old_behave()
                          if kind.startswith("old-") else None)
    if kind == "model":
        return ModelOpp(char)
    raise SystemExit("unknown body %r" % kind)


# ---- a run -------------------------------------------------------------------

def put(n, port, raw):
    b, lx, ly, cx, cy, lt, rt = raw
    n.h.pads[port].update(buttons=b, lx=lx, ly=ly, cx=cx, cy=cy, lt=lt,
                          rt=rt, connected=True)
    n._dirty.add(port)


def start(n, char, px=-20.0, ox=20.0):
    put(n, 0, NONE)
    put(n, 1, NONE)
    n.step()
    n.start("fox", char)
    n.place(0, px, 0, 1, False, 0.0)
    n.place(1, ox, 0, -1, False, 0.0)
    put(n, 0, NONE)
    put(n, 1, NONE)
    n.step(3)


def run(n, char, body_kind, standin, frames, seed, quiet=False):
    """One run: [(frame rows)] of the body's frames, and its numbers."""
    start(n, char)
    body = make_body(body_kind, n, char, seed)
    sin = Standin(standin, random.Random(seed * 7 + 3))
    rows = []
    took = []
    t0 = time.time()
    try:
        for f in range(frames):
            st = n.state()
            mine = sin(st)
            t1 = time.time()
            raw = tuple(body.pad(st, mine))
            took.append(time.time() - t1)
            put(n, 0, mine)
            put(n, 1, raw)
            if standin == "shield" and f % 30 == 0:
                n.shield(0, 60.0)
            n.step()
            after = n.state()
            me, them = after["p"][1], after["p"][0]
            if me is None or them is None:
                break
            rows.append(dict(state=me["state"], facing=me["facing"],
                             x=me["x"], them_x=them["x"], raw=raw,
                             band=body.band, them_state=them["state"],
                             air=me["air"],
                             body=getattr(body, "moving", True),
                             doing=getattr(getattr(body, "opp", None),
                                           "doing", None)))
    finally:
        body.stop()
    out = measure([r for r in rows if r["body"]], char)
    if len(rows) > out["frames"]:
        # (a drill: the attacks' frames apart; lag counted over all)
        every = measure(rows, char)
        out.update(all_frames=len(rows), all_lag=every["lag"],
                   all_counts=every["counts"])
    out["s"] = time.time() - t0
    took.sort()
    out["ms"] = dict(mean=1000.0 * sum(took) / max(len(took), 1),
                     p99=1000.0 * took[int(len(took) * 0.99)] if took else 0,
                     most=1000.0 * took[-1] if took else 0)
    fw = body.footwork()
    if fw is not None:
        errs = [abs(e) for e in fw.errs]
        out.update(resyncs=fw.resyncs, rejected=fw.rejected,
                   xerr=statistics.mean(errs) if errs else 0.0,
                   xerr_max=max(errs) if errs else 0.0,
                   kinds={k: fw.kinds.count(k) for k in set(fw.kinds)})
    return rows, out


def row_text(char, body, standin, m):
    c = m["counts"]
    n = max(m["frames"], 1)

    def pct(k):
        return 100.0 * c.get(k, 0) / n
    lr = m["legs_range"]
    return ("%-15s %-13s %-6s lag %5.1f%% (turnrun %3d brake %3d run %3d) "
            "dash %4.1f%% ddturn %3.1f%% pivot %4.1f%% wait %4.1f%% "
            "walk %4.1f%% crouch %4.1f%% wd %4.1f%% shield %4.1f%% "
            "jump %4.1f%% | backs %3d (%.1f/s) dances %3d legs %4.1f+-%3.1f "
            "%s x%d | ran %2d ignored %2d | band %4.1f%% facing %4.1f%% "
            "d %4.1f+-%4.1f teeter %d | near %4.1f%% closest %4.1f "
            "under %4.1f" % (
                char, body, standin, m["lag_pct"], c["turn_run"],
                c["run_brake"], c["run"], pct("dash"), pct("dd_turn"),
                pct("pivot"), pct("wait"), pct("walk"), pct("crouch"),
                pct("wavedash"), pct("shield"), pct("jump"),
                m["dash_backs"], m["backs_per_s"], m["dash_dances"],
                m["legs_mean"], m["legs_sd"],
                "%d-%d" % tuple(lr) if lr else "-", m["legs_distinct"],
                m["ran"], m["ignored"], m["inband_pct"], m["facing_pct"],
                m["dist_mean"], m["dist_sd"], c["teeter"], m["near_pct"],
                m["dist_min"], m["under_most"]))


# ---- calibration -------------------------------------------------------------

def calibrate(n, char):
    """`char`'s movement, measured: dash (frames of initial dash: held
    longer it runs), anim (frames a dash let go of stays a dash), squat
    (jump squat), wd (a wavedash's slide from standing), pivot (a pivot's
    turn), guard_off (the shield let go of), squat_rv, vinit, vmax, accel
    (a dash's speed), fric (its slowing when let go of), keep (the share of
    speed a dash dance's turn keeps), walk (speed at 0.47 of the stick)."""

    def S(lx, ly=0, b=0, rt=0):
        return (b, lx, ly, 0, 0, 0, rt)

    def play(pads):
        start(n, char, -40.0, 20.0)
        out = []
        for raw in pads:
            put(n, 1, raw)
            put(n, 0, NONE)
            n.step()
            p = n.state()["p"][1]
            out.append(p)
        return out

    def first(rows, pred):
        for i, r in enumerate(rows):
            if pred(r):
                return i + 1
        return None

    m = {}
    r = play([S(-127)] * 30)
    m["dash"] = first(r, lambda p: p["state"] == 21) - 1
    v = [abs(p.get("gvel", 0.0)) for p in r[:m["dash"]]]
    m["vinit"] = round(v[0], 4)
    m["vmax"] = round(v[-1], 4)
    m["accel"] = round(v[1] - v[0], 4) if len(v) > 1 else 0.0
    r = play([S(-127)] * 3 + [NONE] * 40)
    m["anim"] = first(r, lambda p: p["state"] != 20) - 1
    g = [abs(p.get("gvel", 0.0)) for p in r]
    m["fric"] = round(g[3] - g[4], 4)
    r = play([S(-127)] * 6 + [S(127)] * 3)
    m["keep"] = round(abs(r[6].get("gvel", 0.0)) /
                      max(abs(r[5].get("gvel", 1.0)), 1e-6), 4)
    r = play([S(0, 0, 0x400)] + [NONE] * 10)
    m["squat"] = first(r, lambda p: p["air"]) - 1
    J = m["squat"]
    r = play([S(0, 0, 0x400)] + [NONE] * (J - 1) +
             [S(100, -80, 0x20, 255)] + [NONE] * 24)
    m["wd"] = round(r[-1]["x"] - 20.0, 2)
    m["wd_lag"] = sum(1 for p in r if p["state"] == 43)
    r = play([S(-127)] * 5 + [S(127)] + [NONE] * 24)
    m["pivot"] = sum(1 for p in r if p["state"] == 18)
    m["pivot_dx"] = round(r[-1]["x"] - r[4]["x"], 2)
    r = play([S(0, 0, 0x20, 255)] * 8 + [NONE] * 30)
    shields = SHIELDS | (YOSHI_SHIELD if char == "yoshi" else set())
    m["guard_off"] = first(r[8:], lambda p: p["state"] not in shields) - 1
    r = play([S(0, -127)] * 10 + [NONE] * 20)
    m["squat_rv"] = sum(1 for p in r[10:] if p["state"] == 41)
    r = play([S(-60)] * 20)
    m["walk"] = round(abs(r[-1].get("gvel", 0.0)), 4)
    return m


def footwork_table():
    path = os.path.join(HERE, "footwork.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def do_calibrate(chars, write):
    from native import Native
    table = footwork_table()
    numbers = json.load(open(os.path.join(ROOT, "data", "drills",
                                          "numbers.json")))
    bad = 0
    out = dict(table)
    with Native() as n:
        for c in chars:
            m = calibrate(n, c)
            out[c] = m
            had = table.get(c)
            same = had is not None and all(
                (abs(had.get(k, 1e9) - v) < 0.02 if isinstance(v, float)
                 else had.get(k) == v) for k, v in m.items())
            dash_doc = numbers.get(c, {}).get("DASH")
            note = "" if dash_doc in (None, m["dash"]) else \
                "  (numbers.json DASH %s)" % dash_doc
            if not same:
                bad += 1
            print("%-18s %s %s%s" % (c, "same" if same else "DIFFERS",
                                     json.dumps(m, sort_keys=True), note),
                  flush=True)
    if write:
        path = os.path.join(HERE, "footwork.json")
        with open(path, "w") as f:
            json.dump(out, f, indent=1, sort_keys=True)
            f.write("\n")
        print("wrote", path)
    return bad


# ---- main --------------------------------------------------------------------

ALL = ("bowser", "captain-falcon", "donkey-kong", "dr-mario", "falco", "fox",
       "ganondorf", "ice-climbers", "jigglypuff", "kirby", "link", "luigi",
       "mario", "marth", "mewtwo", "mr-game-and-watch", "ness", "peach",
       "pichu", "pikachu", "roy", "samus", "sheik", "yoshi", "young-link",
       "zelda")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--chars", default=",".join(TOP))
    ap.add_argument("--body", default="approach,footsies")
    ap.add_argument("--standin", default="stand,shield,move")
    ap.add_argument("--frames", type=int, default=1200)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--json")
    ap.add_argument("--trace", help="a directory for each run's frames")
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--range", default="28,42",
                    help="the footsies body's band, LO,HI units")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    chars = ALL if a.chars == "all" else a.chars.split(",")
    global RANGE
    RANGE = tuple(float(v) for v in a.range.split(","))
    if a.calibrate:
        return 1 if do_calibrate(chars, a.write) and not a.write else 0
    from native import Native
    results = []
    with Native() as n:
        for c in chars:
            for b in a.body.split(","):
                for s in a.standin.split(","):
                    try:
                        rows, m = run(n, c, b, s, a.frames, a.seed)
                    except RuntimeError as e:
                        print("%-15s %-13s %-6s %s" % (c, b, s, e),
                              flush=True)
                        continue
                    print(row_text(c, b, s, m), flush=True)
                    if "all_frames" in m:
                        ac = m["all_counts"]
                        print("    all %d frames (the attacks too): lag %d "
                              "(turnrun %d brake %d run %d)" % (
                                  m["all_frames"], m["all_lag"],
                                  ac["turn_run"], ac["run_brake"],
                                  ac["run"]), flush=True)
                    if "xerr" in m:
                        print("    model: x off by %.2f (at most %.1f), "
                              "planned again %d times, %d candidates "
                              "refused; phrases %s; the body %.2f ms a "
                              "frame (99%% under %.2f, most %.1f)" % (
                                  m["xerr"], m["xerr_max"], m["resyncs"],
                                  m["rejected"], json.dumps(
                                      m["kinds"], sort_keys=True),
                                  m["ms"]["mean"], m["ms"]["p99"],
                                  m["ms"]["most"]),
                              flush=True)
                    results.append(dict(char=c, body=b, standin=s, **m))
                    if a.trace:
                        os.makedirs(a.trace, exist_ok=True)
                        with open(os.path.join(a.trace, "%s_%s_%s.json" % (
                                c, b, s)), "w") as f:
                            json.dump(rows, f)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(results, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
