"""How an engine opponent feels live: a drill's scenario played as the
client plays it (the course runtime, the drill's script, its decisions in
forked copies of the game at 60 frames a second), against stand-ins for
the player, every commitment the opponent makes measured
(docs/ai/melee-engine.md, "Thinking while a person plays: forks").

    python -u tools/melee_engine/feel.py [--mode window|paced|headless]
        [--drill fox-shine-oos] [--chars sheik,marth] [--standin shield]
        [--attempts 20] [--load 0] [--trace] [--json OUT]

Modes: `window` (the window build on a virtual display, paced by the game
as the client paces it, decisions in forks of it: what a person playing
the client gets), `paced` (the headless build paced to 60 frames a second
here, decisions in forks: the live way of thinking without the window's
drawing), `headless` (decisions made in the game itself, the frame waiting
for them: the engine's own accuracy).

Stand-ins (`--standin`, comma separated, each a run of its own):

- shield: holds the shield, digitally (R and the trigger all the way);
- analog: holds the shield with the trigger part way (a light press);
- jitter: R held, as a person's controller holds it: the trigger's
  analog value and the stick wander a little every frame (150 to 255, the
  stick within 3 of the middle);
- stand: stands (a drill that wants the shield then never commits:
  `--lands any` measures an approach that lands on anything);
- shuffle: as a person waiting in shield: the shield for a while, let go,
  a small walk (toward or away), the shield again, at random lengths;
- bait: holds the shield; the frame after the opponent commits, lets go
  and walks away for 40 frames, then shields again (a line whose press
  comes later than the opponent's reaction time after can be given up);
- oos: holds the shield and answers each hit with the frame-4 shine out of
  shield (Y on the first frame out of shield stun, seen coming a frame
  ahead as tests/client/shine_oos.py does, down-B 3 frames later): the
  contract's guarantee, measured (each attempt's verdict).

For every commitment: the frame its decision was asked on and the frame
it was for, the frame the line really started on, the line, the contact
it predicted and when, and what really happened (on the shield, a hit,
beaten, a miss), and for a miss whether the player's input changed after
the decision (a real change) or not (a wrong prediction); and how the
line moved (frames running or turning round in a run, past the player); where it met
the shield (`_geometry`: the move's family, the side the line started on, the
gap at the contact along it, negative from behind, the opponent past the player
at any frame up to the frame a frame-4 shine out of shield hits or up to the
line's end, a contact on the player's back). `--trace`: each
decision's predicted frames too (played ahead in the fork after it chose),
compared with the live ones: the first frame they differ and in which
fighter.

`--draw` (headless and paced): the frames played for real run the draw
pass, as the window build's do (searches never do).

"reacted D+A": plans dropped before they began, lines given up part way,
after the player left what the decision assumed; "body broke": decisions
the body did not keep the pads of.

`--load K`: K busy processes for the run (one core each), as tests running
in parallel load the machine.

Every loop has a frame budget: an attempt at most the session's own
limit, a run at most --attempts attempts per character.
"""
import argparse
import json
import os
import random
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for _p in (os.path.join(ROOT, "tools", "melee_native"),
           os.path.join(ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from melee_engine import behave as B  # noqa: E402
from melee_engine import drill as D  # noqa: E402

GUARDING = (178, 179, 180, 181, 182)
SHIELD_RAW = (0x20, 0, 0, 0, 0, 0, 255)
ANALOG_RAW = (0, 0, 0, 0, 0, 0, 120)
NONE = D.NONE

# ---- instrumentation (wrappers: nothing of the engine's code changes) -------

LOG = []          # every EngineOpponent made, with what it saw and did


def _instrument(trace=False):
    """Wrap EngineOpponent and Commit so that every decision and every frame
    of every opponent is recorded."""
    E = D.EngineOpponent
    if getattr(E, "_feel", False):
        return
    E._feel = True
    init, pad, ask, collect = E.__init__, E.pad, E._ask, E._collect

    def _init(self, *a, **kw):
        init(self, *a, **kw)
        self.feel = dict(frames=[], asks=[], got=[], swaps=[])
        LOG.append(self)

    def _pad(self, st, their=None):
        k = self.frame
        mode0, plan_at0 = self.mode, self.plan_at
        raw = pad(self, st, their)
        me, them = st["p"][self.port], st["p"][self.target]
        self.feel["frames"].append(dict(
            k=k, gf=st.get("frame"), t=time.time(), raw=tuple(raw),
            their=tuple(their) if their is not None else None,
            mode=self.mode, plan_at=self.plan_at,
            me=_brief(me), them=_brief(them)))
        if mode0 == "committed" and self.plan_at != plan_at0 and \
                self.plan_at is not None:
            self.feel["swaps"].append((k, plan_at0, self.plan_at))
        return raw

    def _ask(self, kind, fn, lead, **kw):
        ask(self, kind, fn, lead, **kw)
        self.feel["asks"].append(dict(tag=self.tag, kind=kind,
                                      k=self.frame, lead=lead,
                                      at=self.frame + lead, t=time.time()))

    def _collect(self):
        p = self.pending
        if p is not None and self.think.ready(p["tag"]):
            got = self.think.results.get(p["tag"]) \
                if hasattr(self.think, "results") else None
            rec = dict(tag=p["tag"], kind=p["kind"], k=self.frame,
                       asked=p["asked"], at=p["at"],
                       late=self.frame > p["at"], mode=self.mode)
            if got is not None:
                rec.update(ok=got.get("ok"), why=got.get("why"),
                           ms=got.get("ms"))
                line = got.get("line")
                if line is not None:
                    rec.update(line=line.names, contact=line.contact,
                               contact_at=line.contact_at,
                               first_len=line.first_len,
                               press=got.get("press"))
                if got.get("trace") is not None:
                    rec["trace"] = got["trace"]
                rec["took"] = got.get("feel_took")
            self.feel["got"].append(rec)
        collect(self)

    E.__init__, E.pad, E._ask, E._collect = _init, _pad, _ask, _collect

    C = B.Commit
    find = C.find

    def _find(self, n, port, target, pre, my_pad, rng, **kw):
        t0 = time.time()
        out = find(self, n, port, target, pre, my_pad, rng, **kw)
        if trace and out.get("ok"):
            out["trace"] = _predict(n, port, target,
                                    list(pre) + out["pads"])
        out["feel_took"] = time.time() - t0
        return out

    C.find = _find


def _brief(p):
    if p is None:
        return None
    return dict(state=p["state"], x=round(p["x"], 3), y=round(p["y"], 3),
                air=p["air"], percent=p["percent"], hitlag=p["hitlag"],
                shield=round(p.get("shield", 0.0), 2), facing=p["facing"])


def _predict(n, port, target, raws):
    """The frames `raws` (PORT's pads from now) lead to, the target holding
    its pad: [(a_state, a_x, a_y, t_state, t_x, t_hitlag, t_percent)]."""
    from melee_actor.ahead import compress, look
    # (a lookahead takes 48 segments at most: the frames they cover)
    plan = compress([B.raw_pad(r) for r in raws] + [B.raw_pad(NONE)] * 20)
    out = look(n, port, target, plan[:48], stop=0)
    return [(r.a_state, round(r.a_x, 3), round(r.a_y, 3), r.t_state,
             round(r.t_x, 3), r.t_hitlag, r.t_percent) for r in out.rows]


# ---- stand-ins --------------------------------------------------------------

class Standin:
    """The player's pad each frame, from the game's state."""

    def __init__(self, kind, rng):
        self.kind, self.rng = kind, rng
        self.left = rng.randint(25, 90)
        self.raw = SHIELD_RAW
        self.walks = 0
        self.oos = None           # frames since Y (the shine out of shield)

    OOS = [(0x20 | 0x800, 0, 0, 0, 0, 0, 255),        # Y, the shield held
           (0x20 | 0x800, 0, 0, 0, 0, 0, 255),
           SHIELD_RAW,                                 # (jump squat)
           (0x20 | 0x200, 0, -127, 0, 0, 0, 255),      # down-B: frame 4
           (0x20 | 0x200, 0, -127, 0, 0, 0, 255)]

    def __call__(self, st, me, opp, n=None):
        k = self.kind
        if k == "shield":
            return SHIELD_RAW
        if k == "bait":
            if self.left > 0:
                self.left -= 1
                return self.raw
            o = LOG[-1] if LOG else None
            if o is not None and o.mode == "committed" and \
                    o.committed is not None and id(o) != getattr(
                        self, "baited", None):
                self.baited = id(o)
                d = opp["x"] - me["x"] if opp else 1.0
                way = -1 if d > 0 else 1
                if abs(me["x"]) > 50 and way * me["x"] > 0:
                    way = -way
                self.raw = (0, 60 * way, 0, 0, 0, 0, 0)
                self.left = 40
                return self.raw
            return SHIELD_RAW
        if k == "oos":
            if self.oos is not None:
                self.oos += 1
                if self.oos < len(self.OOS):
                    return self.OOS[self.oos]
                self.oos = None
            if me["state"] == 181 and me["hitlag"] <= 0 and n is not None:
                from melee_actor.ahead import look
                out = look(n, 0, 1, [(1, dict(buttons=["R"], r=1.0))],
                           stop=0)
                if out.rows and out.rows[0].a_state != 181:
                    self.oos = 0
                    return self.OOS[0]
            return SHIELD_RAW
        if k == "analog":
            return ANALOG_RAW
        if k == "jitter":
            r = self.rng
            return (0x20, r.randint(-3, 3), r.randint(-3, 3), 0, 0, 0,
                    r.randint(150, 255))
        if k == "stand":
            return NONE
        # shuffle: the shield for a while, a small walk, the shield again
        if self.left <= 0:
            if self.raw[0] & 0x20 or self.raw[6]:
                d = opp["x"] - me["x"] if opp else 1.0
                toward = 1 if d > 0 else -1
                way = -toward if abs(d) < 18 else (
                    toward if abs(d) > 40 else self.rng.choice((1, -1)))
                if abs(me["x"]) > 55 and way * me["x"] > 0:
                    way = -way
                self.raw = (0, self.rng.choice((40, 55, 70)) * way, 0, 0, 0,
                            0, 0)
                self.left = self.rng.randint(5, 16)
                self.walks += 1
            else:
                self.raw = SHIELD_RAW
                self.left = self.rng.randint(25, 90)
        self.left -= 1
        return self.raw


# ---- what each commitment came to -------------------------------------------

def outcomes(opp, port_me=0):
    """Each commitment of one EngineOpponent: its decision, what it
    predicted, and what really happened. The frames' records `k` are the
    opponent's own frame counts; the state recorded at k is the game
    before frame k is played (after frame k - 1)."""
    f = opp.feel
    frames = {r["k"]: r for r in f["frames"]}
    out = []
    used = [g for g in f["got"] if g.get("ok") and not g["late"] and
            g["kind"] == "commit"]
    if opp.committed is None:
        return out, used
    # the decision that was played: the last collected before it committed
    # whose `at` is the frame it committed on (several may have come back)
    took = [g for g in used if g["k"] <= opp.committed]
    g = took[-1] if took else None
    rec = dict(committed=opp.committed, line=opp.line.names if opp.line
               else None, decisions=len(used), swaps=list(f["swaps"]))
    if g is not None:
        rec.update(asked=g["asked"], at=g["at"], start_off=opp.committed -
                   g["at"], predicted=g.get("contact"),
                   predicted_at=g["asked"] + g.get("contact_at", 0),
                   collected=g["k"], took=g.get("took"))
    # what really happened: from the commitment, the first contact
    c0 = frames.get(opp.committed)
    real, real_at = None, None
    if c0 is not None and c0["them"] is not None:
        pct_t, pct_a = c0["them"]["percent"], c0["me"]["percent"]
        last = max(frames)
        for k in range(opp.committed + 1, last + 1):
            r = frames.get(k)
            if r is None or r["them"] is None or r["me"] is None:
                continue
            t, a = r["them"], r["me"]
            if t["percent"] > pct_t:
                real, real_at = "hit", k
            elif t["hitlag"] > 0 and t["state"] in GUARDING:
                real, real_at = "shield", k
            elif t["state"] in range(223, 233):
                real, real_at = "grab", k
            elif a["percent"] > pct_a:
                real, real_at = "beaten", k
            if real:
                break
        rec["end"] = last
        rec["cut"] = real is None and opp.mode != "done"
    rec.update(real=real, real_at=real_at)
    # how the line moved: frames running (TurnRun, Run, RunDirect,
    # RunBrake) and turning round in a run, and whether it passed the player
    ran = turned = 0
    crossed = False
    side = None
    for k in range(opp.committed, max(frames) + 1):
        r = frames.get(k)
        if r is None or r["mode"] != "committed" or r["me"] is None or \
                r["them"] is None:
            break
        st = r["me"]["state"]
        ran += st in (19, 21, 22, 23)
        turned += st == 19
        if not r["me"]["air"]:
            way = r["them"]["x"] >= r["me"]["x"]
            if side is None:
                side = way
            elif way != side:
                crossed = True
    rec.update(ran=ran, turned=turned, crossed=crossed)
    rec["family"] = B.family(rec["line"])
    rec.update(_geometry(frames, opp.committed, real, real_at))
    # the player's input from the decision to the predicted contact: as
    # assumed (held) or changed
    if g is not None:
        a0 = frames.get(g["asked"])
        held = a0["their"] if a0 else None
        upto = rec.get("predicted_at") or opp.committed
        changed = None
        for k in range(g["asked"], upto + 1):
            r = frames.get(k)
            if r is not None and held is not None and r["their"] != held:
                changed = k
                break
        rec["their_changed"] = changed
        if g.get("trace"):
            rec["diverged"] = _diverged(g["trace"], frames, g["asked"])
    out.append(rec)
    return out, used


def _geometry(frames, committed, real, real_at, within=4):
    """Where a commitment met the player, from the frames' records (record
    k: the game after frame k - 1): `side` the way the player was from the
    opponent at the commitment; `gap` the distance at the contact along it
    (negative: the opponent past the player, a hit from behind); `answer_k`
    the record after the frame a frame-`within` answer out of shield hits
    (the first frame out of shield stun, the frame after which the player
    is first seen in the shield again with no hitlag, counted as 1; a
    contact not on the shield: the contact's); `done_k` the record its
    move was over by (it hit in the air and has landed, or it is on the
    ground in a free state: opponent.NEUTRAL); `crossed_answer`,
    `crossed_window` and `crossed_end` the first record (from the
    commitment) the opponent was past the player, to answer_k, to the
    later of answer_k and done_k (what the engine's front= checks) and to
    the line's end (its last committed frame), in the air or not (None:
    never); `back` the contact on the player's back (they faced away from
    the opponent)."""
    from melee_engine.opponent import NEUTRAL
    c0 = frames.get(committed)
    if c0 is None or c0["me"] is None or c0["them"] is None:
        return {}
    side = 1 if c0["them"]["x"] >= c0["me"]["x"] else -1
    out = dict(side=side)
    last = max(frames)
    end_k = committed
    while end_k + 1 <= last and frames.get(end_k + 1) is not None and \
            frames[end_k + 1]["mode"] == "committed":
        end_k += 1
    end_k += 1
    answer_k = done_k = None
    if real_at is not None:
        r = frames.get(real_at)
        if r is not None and r["me"] is not None and r["them"] is not None:
            out["gap"] = round((r["them"]["x"] - r["me"]["x"]) * side, 2)
            out["above"] = round(r["me"]["y"] - r["them"]["y"], 2)
            out["back"] = r["them"]["facing"] == side
        answer_k = real_at
        if real == "shield":
            for k in range(real_at + 1, min(last, real_at + 80) + 1):
                q = frames.get(k)
                if q is not None and q["them"] is not None and \
                        q["them"]["state"] in (178, 179) and \
                        q["them"]["hitlag"] <= 0:
                    answer_k = k + within - 1
                    break
        r = frames.get(real_at)
        flew = r is not None and r["me"] is not None and r["me"]["air"]
        for k in range(real_at + 1, min(last, real_at + 80) + 1):
            q = frames.get(k)
            if q is not None and q["me"] is not None and \
                    not q["me"]["air"] and (flew or
                                            q["me"]["state"] in NEUTRAL):
                done_k = k
                break
    out["answer_k"], out["done_k"] = answer_k, done_k

    def first_past(upto):
        for k in range(committed + 1, min(upto, last) + 1):
            q = frames.get(k)
            if q is None or q["me"] is None or q["them"] is None:
                continue
            if (q["them"]["x"] - q["me"]["x"]) * side < 0:
                return k - committed
        return None
    out["crossed_answer"] = first_past(answer_k) \
        if answer_k is not None else None
    out["crossed_window"] = first_past(max(answer_k or 0, done_k or end_k))
    out["crossed_end"] = first_past(max(end_k, answer_k or 0))
    return out


def _diverged(trace, frames, asked):
    """The first predicted frame the live game differs from, and how."""
    for i, row in enumerate(trace):
        r = frames.get(asked + 1 + i)
        if r is None or r["me"] is None or r["them"] is None:
            return None
        a_state, a_x, a_y, t_state, t_x, t_hitlag, t_pct = row
        me, them = r["me"], r["them"]
        bad = []
        if me["state"] != a_state:
            bad.append("opp state %d, predicted %d" % (me["state"], a_state))
        if abs(me["x"] - a_x) > 0.01 or abs(me["y"] - a_y) > 0.01:
            bad.append("opp at %.2f,%.2f, predicted %.2f,%.2f" % (
                me["x"], me["y"], a_x, a_y))
        if them["state"] != t_state:
            bad.append("player state %d, predicted %d" % (them["state"],
                                                          t_state))
        if abs(them["x"] - t_x) > 0.01:
            bad.append("player at %.2f, predicted %.2f" % (them["x"], t_x))
        if bad:
            return dict(frame=i + 1, k=asked + 1 + i, what=bad)
    return dict(frame=None)


# ---- a run ------------------------------------------------------------------

def make_game(mode, draw=False):
    if mode == "window":
        from window import Window
        w = Window(window=(640, 480))
        w.step(30)
        w.pace(True)
        return w
    from native import Native
    # (draw: the draw pass on in the frames played for real, as the window
    # build's are; searches and lookaheads never run it)
    return Native(draw=draw)


class Pacer:
    """60 frames a second, for the headless build (`paced`): the frame
    waits for its sixtieth, and one that starts late does not hurry the
    next (as the window build's pace)."""

    def __init__(self):
        self.next = None
        self.slow = 0

    def __call__(self):
        now = time.time()
        if self.next is None or now - self.next > 0.002:
            if self.next is not None:
                self.slow += 1
            self.next = now
        elif now < self.next:
            time.sleep(self.next - now)
        self.next += 1.0 / 60


def run_char(game, mode, spec, ch, scen, standin, attempts, seed, lands,
             verbose):
    from melee_course import engine
    from melee_drills.drill import JsonDrill
    if lands:
        spec = _lands(spec, lands)
    drill = JsonDrill(spec)
    part = next(i for i, p in enumerate(spec["parts"])
                if isinstance(p.get("scenario"), list))
    drill.set_part(part)
    deck = drill._part_scenarios()
    k = deck.index(scen)

    def load(fn):
        if hasattr(game, "pace"):
            game.quiet(True)
            try:
                return fn()
            finally:
                game.quiet(False)
        return fn()
    s = engine.Session(drill, game, character="fox", live=False, seed=seed,
                       dpad=False, on_load=load)
    if mode == "paced":
        from melee_engine.fork import InFork
        game.paced = True
        s.thinker = InFork(game)
    elif mode == "headless":
        from melee_engine.drill import Here
        s.thinker = Here(game)
    rng = random.Random(seed)
    who = Standin(standin, rng)
    pacer = Pacer() if mode == "paced" else None
    steps = []
    last = [None]
    del LOG[:]

    def each(n, frame):
        st = n.state()
        me, opp = st["p"][0], st["p"][1]
        raw = who(st, me, opp, n) if me is not None else NONE
        s.set_player_pad(raw[0], raw[1], raw[2], raw[3], raw[4], raw[6])
        now = time.time()
        if last[0] is not None:
            steps.append(now - last[0])
        last[0] = now
        if pacer is not None:
            pacer()
    results = []
    t0 = time.time()
    for a in range(attempts):
        r = s.run(each_frame=each, scenario=k, run=a)
        results.append((bool(r["success"]), r["words"]))
        if verbose:
            print("      %s attempt %d: %s (%d frames)" % (
                ch, a + 1, r["words"], r["frames"]), flush=True)
    took = time.time() - t0
    think = s.thinker if getattr(s, "thinker", None) is not None else None
    commits, decisions = [], []
    for opp in LOG:
        got, used = outcomes(opp)
        commits += got
        decisions.append(dict(
            dropped=getattr(opp, "dropped", 0),
            aborts=getattr(opp, "aborts", 0),
            broken=getattr(opp, "broken", 0),
            asked=opp.asked, late=opp.late, found=opp.found,
            refused=opp.refused, outcomes=dict(opp.outcomes),
            lates=[(g["asked"], g["at"], g["k"]) for g in opp.feel["got"]
                   if g["late"]],
            leads=[x["lead"] for x in opp.feel["asks"]]))
    if mode == "paced":
        game.paced = False
    return dict(char=ch, standin=standin, mode=mode, results=results,
                commits=commits, decisions=decisions, took=took,
                frames=len(steps), slow=sum(1 for x in steps if x > 0.0185),
                step_ms=_pct([x * 1000 for x in steps]),
                errors=list(getattr(think, "errors", []) or []),
                leads=dict(getattr(think, "leads", {}) or {}),
                took_s={k: _pct([x for x in v]) for k, v in
                        (getattr(think, "took", {}) or {}).items()})


def _pct(xs):
    if not xs:
        return None
    xs = sorted(xs)
    return dict(n=len(xs), p50=round(xs[len(xs) // 2], 4),
                p90=round(xs[int(len(xs) * 0.9)], 4),
                p99=round(xs[min(len(xs) - 1, int(len(xs) * 0.99))], 4),
                max=round(xs[-1], 4))


def _lands(spec, lands):
    spec = json.loads(json.dumps(spec))

    def walk(steps):
        for st in steps or ():
            if st.get("do") == "approach":
                st["lands"] = lands
            for k in ("then", "else", "repeat"):
                walk(st.get(k))
            for m in st.get("mix", ()) if isinstance(st.get("mix"),
                                                      list) else ():
                walk(m.get("steps"))
    for sc in spec["scenarios"]:
        op = sc.get("opponent")
        if isinstance(op, dict):
            walk(op.get("script"))
    return spec


def summary(r):
    cs = r["commits"]
    n = len(cs)
    landed = sum(1 for c in cs if c["real"] in ("shield", "hit", "grab"))
    wrong = [c for c in cs if c["real"] not in ("shield", "hit", "grab")
             and not c.get("cut") and c.get("their_changed") is None]
    changed = [c for c in cs if c["real"] not in ("shield", "hit", "grab")
               and c.get("their_changed") is not None]
    cut = [c for c in cs if c.get("cut")]
    offs = [c["start_off"] for c in cs if "start_off" in c]
    late = sum(d["late"] for d in r["decisions"])
    asked = sum(d["asked"] for d in r["decisions"])
    swaps = sum(1 for c in cs if c["swaps"])
    early = [c for c in cs if c["real"] in ("shield", "hit") and
             c.get("predicted_at") is not None and
             c["real_at"] != c["predicted_at"]]
    met = [c for c in cs if c["real"] in ("shield", "hit", "grab")]
    gaps = sorted(c["gap"] for c in met if c.get("gap") is not None)
    fams = {}
    for c in cs:
        fams[c.get("family")] = fams.get(c.get("family"), 0) + 1
    tries = [w for ok, w in r["results"] if not w.startswith("Not counted")
             and not w.startswith("Nothing happened")]
    won = sum(1 for ok, w in r["results"] if ok)
    return dict(n=n, landed=landed, rate=landed / n if n else None,
                tries=len(tries), won=won,
                running=sum(1 for c in cs if c.get("ran")),
                turned=sum(c.get("turned", 0) for c in cs),
                crossed=sum(1 for c in cs if c.get("crossed")),
                dropped=sum(d.get("dropped", 0) for d in r["decisions"]),
                aborts=sum(d.get("aborts", 0) for d in r["decisions"]),
                broken=sum(d.get("broken", 0) for d in r["decisions"]) +
                sum(d["outcomes"].get("commit body moved otherwise", 0)
                    for d in r["decisions"]),
                wrong=len(wrong), changed=len(changed), cut=len(cut),
                late=late, asked=asked, swaps=swaps,
                behind=sum(1 for c in met if (c.get("gap") or 0) < 0),
                past_answer=sum(1 for c in met
                                if c.get("crossed_answer") is not None),
                past_window=sum(1 for c in met
                                if c.get("crossed_window") is not None),
                past_end=sum(1 for c in met
                             if c.get("crossed_end") is not None),
                back=sum(1 for c in met if c.get("back")),
                gap=(gaps[0], gaps[len(gaps) // 2], gaps[-1]) if gaps
                else None,
                families=dict(sorted(fams.items(), key=lambda kv: -kv[1])),
                lines=len(set(c.get("line") for c in cs)),
                off=(min(offs), max(offs)) if offs else None,
                contact_off=sorted(set(c["real_at"] - c["predicted_at"]
                                       for c in early)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mode", default="window",
                    choices=("window", "paced", "headless"))
    ap.add_argument("--drill", default="fox-shine-oos")
    ap.add_argument("--chars", help="the deck's opponents by scenario name "
                    "or character id, comma separated (default: all)")
    ap.add_argument("--standin", default="shield",
                    help="shield, analog, stand, shuffle (comma separated)")
    ap.add_argument("--attempts", type=int, default=20,
                    help="attempts per character")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--lands", help="every approach's lands: hit, shield, any")
    ap.add_argument("--load", type=int, default=0,
                    help="busy processes beside the run")
    ap.add_argument("--draw", action="store_true",
                    help="headless: the draw pass on (as the window build)")
    ap.add_argument("--trace", action="store_true",
                    help="each decision's predicted frames, compared")
    ap.add_argument("--json", help="write every result here")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    from melee_drills import format as F
    _instrument(trace=args.trace)
    spec = F.load(args.drill)
    part = next(p for p in spec["parts"]
                if isinstance(p.get("scenario"), list))
    deck = part["scenario"]
    names = {}
    for i in deck:
        sc = spec["scenarios"][i]
        names[i] = (sc["name"], sc["opponent"]["character"])
    want = args.chars.split(",") if args.chars else None
    scen = [i for i in deck if want is None or names[i][0] in want or
            names[i][1] in want]
    busy = []
    if args.load:
        for _ in range(args.load):
            busy.append(subprocess.Popen(
                [sys.executable, "-c", "while True: pass"],
                start_new_session=True))
    out = []
    try:
        game = make_game(args.mode, args.draw)
        try:
            for standin in args.standin.split(","):
                for i in scen:
                    name, ch = names[i]
                    t0 = time.time()
                    r = run_char(game, args.mode, spec, name, i, standin,
                                 args.attempts, args.seed + i,
                                 args.lands, args.verbose)
                    r["load"] = args.load
                    out.append(r)
                    sm = summary(r)
                    if standin == "oos":
                        print("%-15s oos      %-8s the shine out of shield "
                              "won %d of %d tries" % (
                                  name, args.mode, sm["won"], sm["tries"]),
                              flush=True)
                    print("%-15s %-8s %-8s landed %3s of %3s%s  wrong %d "
                          "changed %d cut %d  late %d of %d asked  start "
                          "off %s  swaps %d  contact off %s  frames >18.5 "
                          "ms %d of %d  reacted %d+%d  body broke %d  "
                          "lines that ran %d, TurnRun frames %d, passed "
                          "the player %d  (%.0f s)" % (
                              name, standin, args.mode, sm["landed"],
                              sm["n"], " (%.0f%%)" % (100 * sm["rate"])
                              if sm["rate"] is not None else "",
                              sm["wrong"], sm["changed"], sm["cut"],
                              sm["late"], sm["asked"], sm["off"],
                              sm["swaps"], sm["contact_off"], r["slow"],
                              r["frames"], sm["dropped"], sm["aborts"],
                              sm["broken"], sm["running"], sm["turned"],
                              sm["crossed"], time.time() - t0), flush=True)
                    print("      front: from behind %d, past the player by "
                          "the answer %d, by its landing or end and the "
                          "answer %d, by the line's end %d, on the "
                          "player's back %d, gap at contact (min, median, "
                          "max) %s; families %s; distinct lines %d" % (
                              sm["behind"], sm["past_answer"],
                              sm["past_window"], sm["past_end"],
                              sm["back"], sm["gap"],
                              sm["families"], sm["lines"]), flush=True)
                    for c in r["commits"]:
                        if c["real"] not in ("shield", "hit", "grab") or \
                                args.verbose:
                            print("      %s" % _fmt(c), flush=True)
                    if r["errors"]:
                        print("      errors: %s" % r["errors"][:3],
                              flush=True)
        finally:
            game.close()
    finally:
        for p in busy:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except OSError:
                pass
    if args.json:
        with open(args.json, "w") as f:
            json.dump(out, f, indent=1, default=str)
    tot = [summary(r) for r in out]
    n = sum(t["n"] for t in tot)
    landed = sum(t["landed"] for t in tot)
    print("all: landed %d of %d (%.1f%%), wrong predictions %d, the player "
          "changed %d, cut %d, late decisions %d of %d" % (
              landed, n, 100.0 * landed / n if n else 0,
              sum(t["wrong"] for t in tot), sum(t["changed"] for t in tot),
              sum(t["cut"] for t in tot), sum(t["late"] for t in tot),
              sum(t["asked"] for t in tot)), flush=True)
    return 0


def _fmt(c):
    s = "%s: asked %s for %s, started %s (off %s), predicted %s at %s, " \
        "real %s at %s" % (c.get("line"), c.get("asked"), c.get("at"),
                           c["committed"], c.get("start_off"),
                           c.get("predicted"), c.get("predicted_at"),
                           c["real"], c["real_at"])
    if c.get("their_changed") is not None:
        s += ", the player's pad changed at %s" % c["their_changed"]
    if c.get("swaps"):
        s += ", plan replaced while committed %s" % c["swaps"]
    if c.get("cut"):
        s += ", cut short (ended at %s)" % c.get("end")
    if c.get("diverged") is not None and c["diverged"].get("frame"):
        s += ", diverged at +%d: %s" % (c["diverged"]["frame"],
                                       "; ".join(c["diverged"]["what"]))
    if c.get("decisions", 1) > 1:
        s += ", %d decisions used" % c["decisions"]
    return s


if __name__ == "__main__":
    sys.exit(main())
