"""A drill in the drill format (format.py, docs/ai/drill-format.md), played
on the course runtime (tools/melee_course/engine.py): its loads with no
loading screen, its attempts, its demonstration, its timeline, and the
client's drill screen and coach all work as for any course drill.

`JsonDrill(spec)` is a course `Drill` whose behaviour is all in the spec:
where the fighters stand, when an attempt starts and is judged, what is
measured and what counts, the parts the technique is taught in, and what
the coach shows. Nothing of one drill is written here.

The parts: the drill teaches one part at a time (`part`); a part passed
`streak` times in a row opens the next. A result says which part it was,
whether it was passed, and which comes next.
"""
import math

from melee_course.engine import (Drill, Entry, Ref, Row, STICK_SMASH,
                                 SWITCH_MANUAL)

from melee_drills import format as F

WAIT, ATTEMPT = 0, 1
LIMIT = 150               # frames an attempt may last before it is dropped
REF_START = 10            # the demonstration's frame 1, after its lead


def _in(state, s, cid=None):
    """Is action state `state` the named state `s` (or one of its group),
    for character `cid` (CHAR_STATES)?"""
    want = F.CHAR_STATES.get(cid, {}).get(s, F.STATES[s])
    return state in want if isinstance(want, tuple) else state == want


def _region(x, y, d):
    """Is the stick (raw, 80 = full; x toward where the fighter faces) in
    direction `d`, past a smash (the game's 0.6625)?"""
    if d == "down":
        return y <= -STICK_SMASH
    if d == "up":
        return y >= STICK_SMASH
    if d == "forward":
        return x >= STICK_SMASH
    if d == "back":
        return x <= -STICK_SMASH
    return abs(x) < STICK_SMASH and abs(y) < STICK_SMASH


def holds(e, f, fd):
    """Does event `e` (format.py's events) happen on frame record `f`
    (Frame: its "p" the frame before it, None on the first one seen)?"""
    if isinstance(e, list):
        return any(holds(x, f, fd) for x in e)
    p = f["p"]
    if isinstance(e, str):
        if e == "start":
            return f["i"] == 0
        if e == "end":
            return f.get("last", False)
        if p is None:
            return False
        if e == "airborne":
            return f["air"] and not p["air"]
        if e == "lands":
            return not f["air"] and p["air"]
        if e == "apex":
            return f["air"] and f["vy"] <= 0.0 < p["vy"]
        if e == "fast_fall":
            # a fast fall sets the fall speed to the character's own at
            # once; an ordinary fall only reaches terminal speed, slower
            ff = -fd.fastfall_velocity * 0.98
            return f["air"] and f["vy"] <= ff < p["vy"]
        if e == "hit":
            return f["percent"] > p["percent"]
        if e == "hitlag_end":
            return f["hitlag"] <= 0.0 < p["hitlag"]
        if e == "hitlag_last":
            return 0.0 < f["hitlag"] <= 1.0
        if e == "shot":
            return f["items"] > p["items"]
        if e == "connects":
            # the opponent took damage: the player's attack landed
            return f.get("opp_percent") is not None and \
                p.get("opp_percent") is not None and \
                f["opp_percent"] > p["opp_percent"]
        if e == "shield_hit":
            # the opponent's shield took the player's attack
            now, was = f.get("opp_shield"), p.get("opp_shield")
            return now is not None and was is not None and \
                was - now > F.SHIELD_HIT
        if e in ("their_attack", "they_recover", "they_die", "they_ledge",
                 "they_return"):
            now, was = f.get("opp_state"), p.get("opp_state")
            if now is None or was is None:
                return False
            if e == "they_die":
                # the opponent's stock is lost
                dead = F.STATES["dead"]
                return now in dead and was not in dead
            if e == "they_ledge":
                # it catches the ledge
                return now == F.STATES["ledge_catch"] and \
                    was != F.STATES["ledge_catch"]
            if e == "they_return":
                # back on the stage: on the ground and free to act, out of
                # the air or a landing's lag
                from melee_engine.sense import FREE
                here = not f.get("opp_air") and now in FREE and \
                    now not in F.STATES["ledge"]
                there = not p.get("opp_air") and was in FREE and \
                    was not in F.STATES["ledge"]
                return here and not there
            if e == "their_attack":
                # the opponent starts an attack (format.THEIR_ATTACKS)
                return now in F.THEIR_ATTACKS and was not in F.THEIR_ATTACKS
            # the opponent can act again: free (sense.FREE), out of a state
            # that is not
            from melee_engine.sense import FREE
            return now in FREE and was not in FREE
        return False
    if "is" in e:
        if not holds(e["is"], f, fd):
            return False
        cid = fd.id
        if "from" in e and (p is None or not _in(p["state"], e["from"],
                                                 cid)):
            return False
        if "to" in e and not _in(f["state"], e["to"], cid):
            return False
    if e.get("in_air") and not f["air"]:
        return False
    if "close" in e:
        # only with the fighters within D units of each other
        if f.get("opp_x") is None or abs(f["x"] - f["opp_x"]) > \
                F.value(e["close"], f["nums"]):
            return False
    if "after" in e:
        # an earlier frame of the attempt had it (the frames before, back
        # to the attempt's start)
        q, seen = f["p"], False
        while q is not None and not seen:
            seen = holds(e["after"], q, fd)
            q = q["p"]
        if not seen:
            return False
    if e.get("on_ground") and f["air"]:
        return False
    if "is" in e:
        return True             # (its modifiers held, above)
    if "frame" in e:
        return f["i"] == int(F.value(e["frame"], f["nums"])) - 1
    if p is None:
        return False
    if "near" in e:
        # the fighters come within D units of each other
        if f.get("opp_x") is None or p.get("opp_x") is None:
            return False
        d = F.value(e["near"], f["nums"])
        return abs(f["x"] - f["opp_x"]) <= d < abs(p["x"] - p["opp_x"])
    cid = fd.id
    if "enters" in e:
        return _in(f["state"], e["enters"], cid) and \
            not _in(p["state"], e["enters"], cid) and \
            ("from" not in e or _in(p["state"], e["from"], cid)) and \
            ("not_from" not in e or not _in(p["state"], e["not_from"],
                                            cid))
    if "leaves" in e:
        return not _in(f["state"], e["leaves"], cid) and \
            _in(p["state"], e["leaves"], cid) and \
            ("to" not in e or _in(f["state"], e["to"], cid)) and \
            ("not_to" not in e or not _in(f["state"], e["not_to"], cid))
    if "pressed" in e:
        bits = F.BUTTONS[e["pressed"]]
        return bool(f["held"] & bits) and not p["held"] & bits
    if "released" in e:
        bits = F.BUTTONS[e["released"]]
        return not f["held"] & bits and bool(p["held"] & bits)
    for k, (x, y) in (("stick", ("lx", "ly")), ("cstick", ("cx", "cy"))):
        if k in e:
            now = _region(f[x] * f["facing"], f[y], e[k])
            was = _region(p[x] * p["facing"], p[y], e[k])
            return now and not was
    return False


class JsonDrill(Drill):
    def __init__(self, spec):
        super().__init__()
        self.spec = spec
        self.id = spec["id"]
        self.name = spec["name"]
        self.goal = spec["goal"]
        self.part = spec["part"]
        sc = spec["scenarios"][0]
        op = sc.get("opponent", "none")
        # the opponent's character (loaded with the match), or None
        self.cpu = op["character"] if isinstance(op, dict) else None
        self.stage = sc.get("stage", "final-destination")
        chars = spec.get("characters", "all")
        self.characters = None if chars == "all" else tuple(chars)
        # a tech drill alone on the ground: the player sets the pace,
        # nothing is reset. One that starts on the ledge, in the air or on
        # a platform resets after each attempt: it cannot be walked back to
        self.flow = self.cpu is None and all(
            set(s.get("player", {})) <= {"x", "facing", "percent"}
            for s in spec["scenarios"])
        self.help = (spec["goal"], "D-Pad up: tutorial. D-Pad down: reset.")
        # its own default reset after a judged try (Session.reset_rule)
        self.reset = spec.get("reset")
        self.part_index = 0
        self.streak = 0
        self.v = {}
        self.op_refs = []
        self.op_script = None   # a scripted opponent (melee_engine/script.py)
        # what each opponent's approaches learnt (its last attacks'
        # families, what each family came to), from one attempt to the next
        # (its approach draws another: behave.Commit, "variety")
        self.op_memory = {}

    # ---- the drill's numbers -------------------------------------------------------

    def nums(self, c):
        """The character's numbers, and the scenario's own (its
        "numbers": the hit's frame, its hitlag, the DI that survives
        it)."""
        out = F.names(c.fd, c.fd.id.replace("-", " ").title())
        out.update(self.scenario().get("numbers", {}))
        return out

    lesson_scenario = None  # a lesson's own, while the client records it
    scenario_at = None      # the one of a part's list played now
    # inputs timed from an event ("from", inputs_to_refs) are marks of the
    # course runtime, set on the frame the event comes, in the same pass
    live_marks = True
    anchors = ()            # a demonstration's events its inputs are timed from
    @property
    def switch(self):
        """How a part's scenarios change by themselves (the engine's
        OPT_SWITCH): the drill's `switch`, "manual" (kept until the player
        turns it, D-pad left or right) by default, "success" (the other
        side after a success: ledge work) or "every"."""
        from melee_course.engine import SWITCH_EVERY, SWITCH_ON_SUCCESS
        return {"success": SWITCH_ON_SUCCESS, "every": SWITCH_EVERY}.get(
            self.spec.get("switch"), SWITCH_MANUAL)

    def _part_scenarios(self):
        """The part's scenarios: [index] (its "scenario"), or the list the
        player turns through with the D-pad's left and right."""
        sc = self.part_now.get("scenario", 0)
        return list(sc) if isinstance(sc, list) else [sc]

    @property
    def deck(self):
        """A part with several scenarios (the ledgedash from either ledge)
        as the runtime's deck: D-pad left and right, and the pause menu's
        Scenario, change it."""
        idx = self._part_scenarios()
        if len(idx) < 2:
            return None
        return [Entry(self.op_char(i), i, self.spec["scenarios"][i]["name"])
                for i in idx]

    def op_char(self, i):
        """Scenario `i`'s opponent (a deck of opponents: each scenario its
        own, swapped in as the runtime turns to it), or the drill's."""
        op = self.spec["scenarios"][i].get("opponent", "none")
        return op["character"] if isinstance(op, dict) else self.cpu

    @property
    def scripted(self):
        """Whether an opponent of the drill thinks (a script:
        melee_engine/script.py): then its reaction time is the player's to
        set (`react`)."""
        return any(isinstance(sc.get("opponent"), dict) and
                   "script" in sc["opponent"]
                   for sc in self.spec["scenarios"])

    @property
    def opponents(self):
        """Every opponent of the drill's scenarios, in order: loaded with
        its match (Session._opponents), so that a later part's deck is
        there from the first load."""
        out = []
        for sc in self.spec["scenarios"]:
            op = sc.get("opponent", "none")
            if isinstance(op, dict) and op["character"] not in out:
                out.append(op["character"])
        return out

    def scenario(self):
        """The scenario the part now is taught in (its "scenario", the one
        of its list the player has chosen, else the first), or the
        lesson's being recorded."""
        if self.lesson_scenario is not None:
            return self.spec["scenarios"][self.lesson_scenario]
        idx = self._part_scenarios()
        at = self.scenario_at if self.scenario_at in idx else idx[0]
        return self.spec["scenarios"][at]

    @property
    def ref_start(self):
        """Frames after the reset (and the runtime's lead, ref_lead) before
        an example's frame 1: the scenario's "lead", else none on the
        ledge (the hang's intangibility runs from the placement: a player
        can let go on its second frame) and REF_START elsewhere."""
        sc = self.scenario()
        if "lead" in sc:
            return sc["lead"]
        return 0 if sc.get("player", {}).get("ledge") else REF_START

    @property
    def ref_lead(self):
        """The runtime's neutral frames before an example (engine.REF_LEAD):
        none on the ledge."""
        from melee_course.engine import REF_LEAD
        return 0 if self.scenario().get("player", {}).get("ledge") else \
            REF_LEAD

    @property
    def parts(self):
        return self.spec["parts"]

    @property
    def part_now(self):
        return self.parts[self.part_index]

    def set_part(self, i):
        """Teach part `i` from now on (the client: the player chose it)."""
        self.part_index = max(0, min(len(self.parts) - 1, i))
        self.streak = 0

    # ---- the course runtime's hooks ------------------------------------------------

    def setup(self, c):
        if c.entry is not None:         # (the deck's: a part's list)
            self.scenario_at = c.entry.data
        sc = self.scenario()
        nums = self.nums(c)
        pl = sc["player"]
        pct = float(F.value(pl.get("percent", 0), nums))
        px = float(F.value(pl.get("x", 0), nums))
        facing = -1 if pl.get("facing") == "left" else 1
        op = sc.get("opponent", "none")
        # in a demonstration, what the opponent does in an example
        # (format.EXAMPLE_KEYS: its own script, launch, reaction)
        if isinstance(op, dict) and c.is_demo and "example" in op:
            op = dict(op, **op["example"])
        launch = op.get("launch") if isinstance(op, dict) else None
        if launch:
            # knocked off the side the runtime drew (the pause menu's CPU
            # side): the player `inland` from that ledge, their back to it
            side = 1 if c.side >= 0 else -1
            ledge = c.ledge_pos()
            half = abs(ledge[0]) if ledge else 85.0
            # the hit drawn for this attempt, and where the player stands
            # for it (the attempt's random numbers: the same seed, the same
            # start)
            drawn = self.launched = dict(
                F.draw_launch(c.rng, launch, pl), side=side)
            px = side * (half - drawn["stand"])
            facing = side if drawn["facing"] == "ledge" else -side
        if pl.get("ledge"):
            c.place_on_ledge(pct, "right" if pl["ledge"] == "right" else
                             "left")
        elif "above" in pl:
            c.place_on_platform(px, float(F.value(pl["above"], nums)),
                                facing, pct)
        elif pl.get("air"):
            c.side, c.toward = 1.0, -1.0
            c.place_in_air(c.s.person, px,
                           float(F.value(pl.get("y", 30), nums)), facing,
                           pct)
        else:
            c.side, c.toward = 1.0, -1.0
            c.n.place(c.s.person, px, 0.0, facing, False, pct)
        if not pl.get("ledge"):
            # an example's stick forward is the way the scenario faces: a
            # scenario on the other side of the stage, facing left, plays
            # the same example mirrored (the ledge's placement knows its
            # side already)
            c.toward = -1.0 if facing > 0 else 1.0
        if launch:
            self._launch(c, drawn, side, half)
            self.op_refs = []
            self.op_toward = -side
            self._script(c, op if "script" in op else None)
        elif isinstance(op, dict):
            x = float(op["x"])
            toward = -1 if x > px else 1
            c.place_cpu(x, -toward if op.get("facing") == "away" else
                        toward, float(F.value(op.get("percent", 0), nums)))
            if "knockdown" in op and c.s.cpu_port is not None:
                # knocked off its feet where it stands, away from the
                # player (format.KNOCKDOWN_KEYS): the game's own launch
                kd = op["knockdown"]
                c.n.launch(c.s.cpu_port, x, float(kd.get("y", 1)),
                           float(F.value(op.get("percent", 0), nums)),
                           float(kd.get("knockback", 90)),
                           int(kd.get("angle", 80)), -toward, 1)
            self.op_refs = inputs_to_refs(op.get("inputs", []), nums, 1) \
                if op.get("inputs") else []
            self.op_toward = toward
            self._script(c, op if "script" in op else None)
        else:
            self.op_refs = []
            self._script(c, None)
        self.camera(c.n, c.s.person)
        self.trace(c.n, c.s.person)
        self._withhold(c, bool(pl.get("held")))
        if self.spec.get("shield") == "infinite":
            # kept by the game at every frame boundary: what the opponent's
            # searches foresee is the shield the player has (the client
            # lets it go when the drill is left)
            from native import NativeError
            try:
                c.n.shield(c.s.person, 60.0, keep=True)
            except NativeError:
                pass
        self.v = dict(rec=[], last=None)
        # a demonstration's inputs timed from an event: the events (mark k
        # the k-th), looked for frame by frame (_look_ahead)
        self.anchors = list(getattr(self.build_reference(c), "anchors",
                                    ())) if c.is_demo else []
        self.predicted = {}

    def _launch(self, c, drawn, side, half):
        """The opponent knocked off the stage's `side` by the hit drawn
        for the attempt (format.draw_launch): the game's own launch from
        where it was hit; or, a hit that says so, hanging from the
        ledge."""
        from melee_engine.recover import air_jumps
        if c.s.cpu_port is None:
            return
        if drawn["hang"]:
            c.n.ledge(c.s.cpu_port, drawn["percent"],
                      "right" if side > 0 else "left")
            return
        jumps = 1 if drawn["jump"] else air_jumps(c.s.cpu_char) + 1
        c.n.launch(c.s.cpu_port, side * (half - drawn["inland"]),
                   drawn["y"], drawn["percent"], drawn["knockback"],
                   drawn["angle"], side, jumps)

    launched = None     # the opponent's launch this attempt (_launch)
    filming = False     # the client recording the tutorial's examples
    strict = False      # frame-perfect timing (Settings): checks' "strict"
    # the opponent's reaction time, frames (the player's choice in the
    # pause menu and Settings; None: each scenario's own "react")
    react = None

    def camera(self, n, person):
        """The scenario's camera, or while the tutorial's examples are
        recorded (`filming`) the tutorial's (the client puts the match
        camera back when the drill is left). A game built before the camera
        command keeps its own camera."""
        from native import NativeError
        cam = self.scenario().get("camera", "normal")
        if self.filming:            # the tutorial's examples: its own
            cam = self.spec["tutorial"].get("camera", cam)
        try:
            if isinstance(cam, dict):
                n.camera("follow", person, cam["distance"],
                         cam.get("height", 10))
            else:
                n.camera(cam)
        except NativeError:
            pass

    def trace(self, n, person):
        """The scenario's trace for the player ("di": TM-CE's DI display,
        src/host/didraw.c), or none (the client turns it off when the drill
        is left). A game built before the didraw command draws nothing."""
        from native import NativeError
        try:
            n.didraw(person, self.scenario().get("trace") == "di")
        except NativeError:
            pass

    def status(self, c):
        return "Part %d of %d: %s" % (self.part_index + 1, len(self.parts),
                                      self.part_now["name"])

    def guide(self, c):
        nums = self.nums(c)
        t = self.spec["tutorial"]
        return [F.text(t["what"], nums),
                F.text(self.part_now["teach"], nums)]

    def build_reference(self, c):
        return inputs_to_refs(F.pick(self.part_now, "example", c.fd.id),
                              self.nums(c), self.ref_start)

    def timeline(self, c):
        nums = self.nums(c)
        rows = []
        # a lesson shows the whole technique: the drill's own rows (the
        # owner, 2026-11-14: the L-cancel lesson's chart lacked the L, R or
        # Z press, which part 1's rows leave out); a part, its own
        coach = self.spec["coach"] if self.lesson_scenario is not None \
            else self.part_now.get("coach", self.spec["coach"])
        for r in coach.get("rows", []):
            kw = {}
            if "button" in r:
                kw = dict(buttons=F.BUTTONS[r["button"]],
                          held=r.get("held", True))
            elif "cstick" in r:
                d = r["cstick"]
                kw = dict(test=lambda e, d=d: (
                    e["cy"] <= -STICK_SMASH < e["pcy"]) if d == "down" else
                    (e["cy"] >= STICK_SMASH > e["pcy"]) if d == "up" else
                    abs(e["cx"]) >= STICK_SMASH)
            elif "stick" in r:
                d = r["stick"]
                kw = dict(test=lambda e, d=d: (
                    e["ly"] <= -STICK_SMASH < e["ply"]) if d == "down" else
                    (e["ly"] >= STICK_SMASH > e["ply"]) if d == "up" else
                    # any: past a smash whichever way, newly (an SDI's)
                    (max(abs(e["lx"]), abs(e["ly"])) >= STICK_SMASH >
                     max(abs(e.get("plx", 0)), abs(e["ply"])))
                    if d == "any" else
                    # side: either way, past a smash, newly
                    abs(e["lx"]) >= STICK_SMASH > abs(e.get("plx", 0)))
            else:
                st = r["state"]
                cid = c.fd.id
                kw = dict(state=lambda s, st=st: _in(s, st, cid),
                          entered=not r.get("held", False))
            rows.append(Row(
                F.text(r["label"], nums),
                perfect=tuple(int(F.value(x, nums))
                              for x in r.get("perfect", [1])),
                window=tuple(int(F.value(x, nums)) for x in r[
                    "strict_window" if self.strict and "strict_window" in r
                    else "window"])
                if "window" in r else None, **kw))
        return rows, F.text(coach.get("note", ""), nums)

    # ---- an attempt, frame by frame ------------------------------------------------

    withheld = False

    def _withhold(self, c, on):
        """A scenario whose player begins in the opponent's grab
        ("held"): a person's pad is kept from the game from the reset
        (`on`) until the grab has them, format.HELD_MOST frames at most,
        so that every try begins held (a jump or a roll at the reset
        would get out of the grab's way). Nothing to do for a
        demonstration or headless: their pad is the example's."""
        n = c.n
        if not hasattr(n, "scripted") or not getattr(c.s, "live", False):
            self.withheld = False
            return
        if c.is_demo:
            self.withheld = False     # (the client's own: left as it is)
            return
        if on:
            # (said again each reset: the client's own demonstrations
            # hand the port back when they end)
            n.scripted(c.s.person, True)
            n.pad(c.s.person)
        elif self.withheld:
            n.scripted(c.s.person, False)
        self.withheld = on

    def _held_yet(self, c):
        """Hand the pad back once the grab has the player (or it never
        came)."""
        if self.withheld and (
                c.me.state in F.STATES["grabbed"] + F.STATES["thrown"] or
                c.timer > F.HELD_MOST):
            self._withhold(c, False)

    def _frame(self, c):
        """This frame as the events and measures read it."""
        me = c.me
        log = c.s.tl_log[-1] if c.s.tl_log else {}
        held = c.held
        if log.get("trig"):
            held |= F.BUTTONS["L"]  # (a light press: as L, for L-cancels)
        return dict(state=me.state, air=me.airborne, x=me.pos[0],
                    y=me.pos[1], vx=me.vel[0], vy=me.vel[1],
                    facing=1 if me.facing >= 0 else -1,
                    percent=me.percent, hitlag=me.hitlag,
                    invulnerable=me.invulnerable, held=held,
                    items=len(c.n.state().get("items") or []),
                    lx=log.get("lx", 0), ly=log.get("ly", 0),
                    cx=log.get("cx", 0), cy=log.get("cy", 0),
                    p=self.v.get("last"), i=-1, nums=self.v.get("nums"),
                    gf=c.n.state().get("frame"),
                    opp_percent=c.cpu.percent if c.cpu is not None
                    else None,
                    opp_state=c.cpu.state if c.cpu is not None else None,
                    opp_x=c.cpu.pos[0] if c.cpu is not None else None,
                    opp_air=c.cpu.airborne if c.cpu is not None else None,
                    opp_shield=c.cpu.shield if c.cpu is not None else None)

    def _script(self, c, op):
        """The scenario's scripted opponent (`op`: its "script", "react",
        "loop"; None: none), made new at each reset: its random choices
        drawn from the attempt's numbers (a demonstration's two passes and
        check.py's every case play the same opponent), its decisions made
        where the session's thinker makes them (forked copies of the window
        build while a person plays, the game itself headless)."""
        old = self.op_script
        if self.op_script is not None:
            self.op_script.stop()
            self.op_script = None
        if op is None:
            return
        from melee_course.react import thinker
        from melee_engine.script import Opponent
        ledge = c.ledge_pos()
        seed = c.rng.getrandbits(32)
        if old is not None and old.seed != seed:
            # what it attacked with, for the next attempt (one with the same
            # seed, a demonstration's second pass, replays the first: the
            # same memory, the same choices)
            m = old.ctx.memory
            self.op_memory[old.spec.get("character")] = dict(
                m, families=m.get("families", [])[-8:],
                tried=m.get("tried", {}))
        self.op_script = Opponent(
            thinker(c), c.s.cpu_port, c.s.person, op, seed=seed,
            half=abs(ledge[0]) if ledge and abs(ledge[0]) > 1 else 85.0,
            char=c.fd.id, memory=self.op_memory.get(op.get("character")),
            # (a demonstration's opponent keeps its own: the example was
            # written against it)
            react=None if c.is_demo else self.react)

    def settle(self, c):
        """After a judged try, until the reset (Session.settle): the
        scripted opponent plays on (a combo on the player plays out), the
        shield kept full in a shield drill."""
        if self.spec.get("shield") == "infinite":
            c.n.shield(c.s.person, 60.0)
        self._withhold(c, False)
        if self.op_script is not None:
            self._opponent(c)

    def _opponent(self, c):
        """The opponent's inputs this frame: its script's pad, or its
        "inputs" (frame 1 the first after the reset, again every "every"
        frames; stick x toward the player)."""
        if self.spec.get("shield") == "theirs" and c.phase != ATTEMPT and \
                c.cpu is not None and c.cpu.shield >= F.SHIELD_WORN:
            # (a shield held while it waits for the try does not wear; one
            # that has been hit is left as it is: the hit begins the try)
            c.n.shield(c.s.cpu_port, 60.0)
        if self.op_script is not None:
            from melee_course.react import player_raw, put_raw
            put_raw(c, self.op_script.pad(c.n.state(), player_raw(c)))
            return
        if not self.op_refs:
            return
        op = self.scenario()["opponent"]
        t = c.timer
        if op.get("every"):
            t = (t - 1) % op["every"] + 1
        for r in self.op_refs:
            # (a Ref's sticks are a script's -127..127, as cpu_press takes
            # them; frame 1 the first after the reset: the example's frame
            # f is the opponent's f + ref_lead + ref_start, 13 by default)
            if r.frame <= t < r.frame + (r.hold or 1):
                c.cpu_press(r.buttons,
                            int(r.lx * self.op_toward) if r.lx else None,
                            int(r.ly) if r.ly else None,
                            int(r.cx * self.op_toward) if r.cx else None,
                            int(r.cy) if r.cy else None,
                            r.trigger or None)

    def judged_part(self):
        """The part an attempt is judged as: the part now; while the client
        records a lesson played in a scenario the part now does not have,
        the first part that has it (a lesson of the punish, recorded while
        the player is on the first part, is judged as the punish: its
        frames counted from the punish's start)."""
        ls = self.lesson_scenario
        if ls is not None and ls not in self._part_scenarios():
            for p in self.parts:
                sc = p.get("scenario", 0)
                if ls in (sc if isinstance(sc, list) else [sc]):
                    return p
        return self.part_now

    def attempt(self):
        """The part's attempt: the drill's, with what the part changes."""
        a = dict(self.spec["attempt"])
        a.update(self.judged_part().get("attempt", {}))
        return a

    def _anchor_holds(self, e, rec, c, a):
        """Does the event an input is timed from happen on frame record
        `rec` ("start": the attempt's start, while it waits for it)?"""
        if e == "start":
            return c.phase == WAIT and holds(a["start"], rec, c.fd)
        return holds(e, rec, c.fd)

    def _predict(self, c, f):
        """The coming frame's record, before it is played: played ahead in
        the game with the pads it will have (the player's as the
        demonstration sets them, the opponent's as it chose them this
        frame) and undone (melee_actor/ahead.py). State, air, position,
        damage, hitlag and the pad are the coming frame's; speed,
        invulnerability and items the last one's. None if the game cannot
        look ahead."""
        from melee_actor.ahead import look
        from melee_course.react import player_raw
        from melee_engine.opponent import raw_to_pad
        from native import NativeError
        s = c.s
        if s.cpu_port is not None:
            s._set_pad(s.cpu_port, c._pad)    # (as it will be given)
        pad = s.player_pad
        try:
            out = look(c.n, s.person, s.cpu_port if s.cpu_port is not None
                       else 1 - s.person,
                       [(1, raw_to_pad(player_raw(c)))], stop=0)
        except NativeError:
            return None
        if not out.rows:
            return None
        r = out.rows[0]
        held = pad["buttons"]
        if max(pad.get("lt", 0), pad.get("rt", 0)) >= 43:
            held |= F.BUTTONS["L"]
        rec = dict(f, state=r.a_state, air=bool(r.a_air), x=r.a_x, y=r.a_y,
                   facing=1 if r.a_facing >= 0 else -1, percent=r.a_percent,
                   hitlag=r.a_hitlag, held=held, lx=pad.get("lx", 0),
                   ly=pad.get("ly", 0), cx=pad.get("cx", 0),
                   cy=pad.get("cy", 0), p=f,
                   i=len(self.v.get("rec") or ()) + 1
                   if c.phase == ATTEMPT else 0, gf=None,
                   opp_percent=r.t_percent if s.cpu_port is not None
                   else None,
                   opp_state=r.t_state if s.cpu_port is not None else None,
                   opp_x=r.t_x if s.cpu_port is not None else None,
                   opp_air=bool(r.t_air) if s.cpu_port is not None
                   else None,
                   opp_shield=r.t_shield if s.cpu_port is not None
                   else None)
        return rec

    def _look_ahead(self, c, f, a):
        """A demonstration's inputs timed from an event ("from"): its
        frame found before it is played, so that an input on the event's
        own frame goes on it (the jump on the first frame out of shield
        stun: the game reads only a new press there). Each frame while an
        event is due, the coming frame is played ahead; where the event
        happens on it, its mark is that frame and the demonstration's pad
        for it is made again (Session.replay). An event the look missed is
        marked on the frame it was seen (its inputs from then on a frame
        late); one looked for that did not come is looked for again."""
        s = c.s
        for k, at in list(self.predicted.items()):
            if at == s.attempt_frame - 1 and s.marks[k] == at and \
                    not self._anchor_holds(self.anchors[k - 1], f, c, a):
                s.marks[k] = -1         # it did not come: again
            del self.predicted[k]
        due = [k for k in range(1, len(self.anchors) + 1) if s.marks[k] < 0]
        for k in list(due):
            if self._anchor_holds(self.anchors[k - 1], f, c, a):
                c.mark(k, back=1)       # (seen only now)
                due.remove(k)
        if not due:
            return
        pred = self._predict(c, f)
        if pred is None:
            return
        for k in due:
            if self._anchor_holds(self.anchors[k - 1], pred, c, a):
                c.mark(k)
                s.replay = True         # (this frame's pad, made again)
                self.predicted[k] = s.attempt_frame

    def _lesson_inputs_left(self, c):
        """While the client records a lesson (its own scenario and inputs,
        build_reference): whether the lesson's inputs have frames still to
        play."""
        build = vars(self).get("build_reference")
        if self.lesson_scenario is None or build is None:
            return False
        js = c.fd.jump_squat
        refs = build(c)
        timed = [r for r in refs if r.mark > 0]
        if timed:
            # inputs timed from an event are the technique (those before
            # it, a shield held until then, are the setup): played to
            # their end, from where their event came
            marks = c.s.marks
            end = max((marks[r.mark] + r.frame + (r.hold or 1)
                       for r in timed if marks[r.mark] >= 0), default=0)
        else:
            end = max((self.ref_lead + r.frame + r.js * js + (r.hold or 1)
                       for r in refs if r.mark == 0), default=0)
        return c.s.attempt_frame < end

    def think(self, c):
        a = self.attempt()
        v = self.v
        v["nums"] = v.get("nums") or self.nums(c)
        self._held_yet(c)
        if self.spec.get("shield") == "infinite":
            # the shield kept full: a hit's stun and push come from its
            # damage, not the shield's health, so nothing else changes (the
            # game keeps it too, from setup; this for a game built before)
            c.n.shield(c.s.person, 60.0)
        self._opponent(c)
        last = v.get("last")
        if last is not None and last.get("gf") is not None and \
                last["gf"] == c.n.state().get("frame"):
            # the same frame again: a drill that does not reset (flow)
            # starts the next try on the frame the last was judged on, read
            # against the frame before it, so what happened on it (a jump
            # squat entered) can start the try (a SHFFL right after a "No
            # shine" was not judged)
            f = last
        else:
            f = self._frame(c)
        if c.phase == WAIT and f["p"] is not None:
            f["p"]["p"] = None      # (no chain of every frame since)
        v["last"] = f
        if self.anchors:
            self._look_ahead(c, f, a)
        if c.phase == WAIT:
            f["i"] = 0
            v.pop("judge_due", None)
            if "within" in a and c.timer > int(F.value(a["within"],
                                                       v["nums"])):
                # it did not start in time (the opponent's attack missed:
                # the player jumped behind it): reset, not counted (the
                # owner, 2026-11-14: "If the hit doesn't connect, the
                # scenario should be reset")
                c.s.end(None, F.text(a.get("missed", "Not counted: again"),
                                     v["nums"]))
                return
            if not holds(a["start"], f, c.fd):
                return
            c.set_phase(ATTEMPT)
            c.tl_begin()
            v["rec"] = []
        rec = v["rec"]
        f["i"] = len(rec)
        rec.append(f)
        if holds(a["judge"], f, c.fd) or v.get("judge_due"):
            if self._lesson_inputs_left(c):
                # a lesson shows the whole technique, whatever part the
                # player is on: its inputs play to their end before the
                # try is judged (the shine grab's lesson, on the part
                # "Jump out of the shine", was judged at the jump and its
                # Z never came: the owner, 2026-11-14, "doesn't actually
                # show any grabbing")
                v["judge_due"] = True
                return
            v.pop("judge_due", None)
            self._judge(c, rec)
            return
        cancel = a.get("cancel")
        if cancel is None:
            # by default: an attempt that began on entering a state and
            # left it on the ground went another way (a hit, a jump-
            # cancelled move)
            start = a["start"]
            cancel = {"leaves": start["enters"], "on_ground": True} \
                if isinstance(start, dict) and "enters" in start else []
        if cancel and holds(cancel, f, c.fd):
            c.set_phase(WAIT)
        elif len(rec) > a.get("limit", LIMIT):
            if a.get("timeout") == "judge":
                self._judge(c, rec)
            else:
                c.set_phase(WAIT)

    @staticmethod
    def _index(e, rec, fd, after=0):
        """The first frame of `rec` from `after` on that event `e` holds
        on, or None."""
        for k in range(after, len(rec)):
            if holds(e, rec[k], fd):
                return k
        return None

    @staticmethod
    def _cond(cond, f, fd=None):
        """Does frame `f` meet condition `cond` (format.CONDITIONS, or
        {"in": STATE})?"""
        if isinstance(cond, dict):
            return _in(f["state"], cond["in"], fd.id if fd else None)
        if cond == "invulnerable":
            return f["invulnerable"]
        if cond == "airborne":
            return f["air"]
        if cond == "grounded":
            return not f["air"]
        return f["hitlag"] > 0

    def _measure(self, m, c, rec):
        fd = c.fd
        rec[-1]["last"] = True
        if m == "jump_kind":
            # the rise on the first frame in the air: a short hop's speed
            # or a full jump's
            k = self._index("airborne", rec, fd)
            vy = rec[k if k is not None else -1]["vy"]
            return "short" if vy < (c.fd.hop_v + c.fd.jump_v) / 2 else "full"
        if "held" in m:
            bits = F.BUTTONS[m["held"]]
            n = 0
            for r in rec:
                if not r["held"] & bits:
                    break
                n += 1
            return n
        if "frames" in m:
            first, second = m["frames"]
            if m.get("last"):
                # from the last [0] up to the first [1]: the L press that
                # counted, not an earlier one
                b = self._index(second, rec, fd)
                if b is None:
                    return None
                a = next((k for k in range(b, -1, -1)
                          if holds(first, rec[k], fd)), None)
                return None if a is None else b - a
            a = self._index(first, rec, fd)
            # the same event twice: its next time (a shine to the next)
            b = None if a is None else self._index(
                second, rec, fd, a + 1 if first == second else a)
            return None if b is None else b - a
        if "frame_of" in m:
            k = self._index(m["frame_of"], rec, fd)
            return None if k is None else k + 1
        if "happened" in m:
            return self._index(m["happened"], rec, fd) is not None
        if "count" in m:
            return sum(1 for f in rec if holds(m["count"], f, fd))
        if "max_gap" in m:
            # the most frames between two of it in a row (a multishine's
            # slowest shine to the next)
            at = [k for k, f in enumerate(rec) if holds(m["max_gap"], f, fd)]
            return max(b - a for a, b in zip(at, at[1:])) \
                if len(at) >= 2 else None
        if "moved_while" in m:
            # how far the fighter moved on frames that, with the frame
            # before, are all C: in hitlag only SDI moves a fighter
            total = 0.0
            for a, b in zip(rec, rec[1:]):
                if self._cond(m["moved_while"], a) and \
                        self._cond(m["moved_while"], b):
                    total += math.hypot(b["x"] - a["x"], b["y"] - a["y"])
            return round(total, 2)
        if "value" in m:
            k = self._index(m.get("at", "end"), rec, fd)
            if k is None:
                return None
            f, first = rec[k], rec[0]
            if m["value"] == "turned":
                return f["facing"] != first["facing"]
            if m["value"] == "dx":
                return round((f["x"] - first["x"]) * first["facing"], 2)
            if m["value"] == "dy":
                return round(f["y"] - first["y"], 2)
            v = f[m["value"]]
            return round(v, 2) if isinstance(v, float) else v
        if "distance" in m:
            a = self._index(m["distance"][0], rec, fd)
            b = None if a is None else self._index(m["distance"][1], rec, fd,
                                                   a)
            if b is None:
                return None
            dx = rec[b]["x"] - rec[a]["x"]
            dy = rec[b]["y"] - rec[a]["y"]
            axis = m.get("axis", "x")
            return round(abs(dx) if axis == "x" else abs(dy) if axis == "y"
                         else math.hypot(dx, dy), 2)
        if "frames_while" in m:
            k = self._index(m.get("from", "start"), rec, fd)
            if k is None:
                return None
            n = 0
            for f in rec[k:]:
                if not self._cond(m["frames_while"], f, fd):
                    break
                n += 1
            return n
        if "angle" in m:
            k = self._index(m.get("at", "end"), rec, fd)
            if k is None:
                return None
            f = rec[k]
            if m["angle"] == "stick":
                x, y = f["lx"] * f["facing"], f["ly"]
                if m.get("from_horizontal"):
                    x = abs(x)      # either way: the angle from level
                if abs(x) < 8 and abs(y) < 8:
                    return None
            else:
                # how it moved on the next frame (knockback included)
                if k + 1 >= len(rec):
                    return None
                x = (rec[k + 1]["x"] - f["x"]) * f["facing"]
                y = rec[k + 1]["y"] - f["y"]
                if m.get("from_horizontal"):
                    x = abs(x)
            return round(math.degrees(math.atan2(y, x)))
        raise F.DrillError("unknown measure %r" % (m,))

    def _check(self, name, c, rec, nums, measured):
        ck = self.spec["checks"][name]
        if self.strict and "strict" in ck:
            # the player chose frame-perfect timing: the strict expectation
            # (and its own expect and fix words, if it has them)
            ck = {k: v for k, v in ck.items() if k not in F.EXPECTS}
            ck.update(self.spec["checks"][name]["strict"])
        got = measured[ck["measure"]]
        if got is None:
            ok = False      # it never happened: nothing to compare
        elif "equals" in ck:
            want = ck["equals"]
            if isinstance(want, str) and not isinstance(got, str):
                want = F.value(want, nums)      # an expression: "J"
            ok = got == want
        elif "at_most" in ck:
            ok = got <= F.value(ck["at_most"], nums)
        elif "at_least" in ck:
            ok = got >= F.value(ck["at_least"], nums)
        else:
            lo, hi = (F.value(x, nums) for x in ck["within"])
            ok = lo <= got <= hi
        more = dict(measure="none" if got is None else
                    "yes" if got is True else "no" if got is False else got)
        if isinstance(got, int) and not isinstance(got, bool):
            more["frames"] = F.plural(got)
        else:
            more["frames"] = more["measure"]
        more.update(self._named(measured))
        return dict(name=name, passed=bool(ok), measured=got,
                    expect=F.text(ck.get("expect", name), nums, **more),
                    detail=F.text(ck["words"], nums, **more),
                    fix=F.text(ck["fix"], nums, **more),
                    headline=F.text(ck.get("headline", name.capitalize()),
                                    nums, **more))

    @staticmethod
    def _named(measured):
        """The measures as words may name them: {held}, {held_frames}."""
        out = {}
        for k, v in measured.items():
            out[k] = "none" if v is None else "yes" if v is True else \
                "no" if v is False else v
            out[k + "_frames"] = F.plural(v) if isinstance(v, int) and \
                not isinstance(v, bool) else out[k]
        return out

    def _judge(self, c, rec):
        nums = self.nums(c)
        part = self.judged_part()
        measured = {k: self._measure(m, c, rec)
                    for k, m in self.spec["measures"].items()}
        # every check is measured (the coach shows them all); the part's
        # own decide
        done = [self._check(n, c, rec, nums, measured)
                for n in self.spec["checks"]]
        counted = [d for d in done if d["name"] in part.get("checks", [])]
        success = all(d["passed"] for d in counted)
        failed = next((d for d in counted if not d["passed"]), None)
        for d in done:
            c.report(d["name"], d["measured"])
        if failed is None:
            words = F.text(part.get("success",
                                     self.spec["verdict"]["success"]),
                           nums, **self._named(measured))
            head = words.split(".")[0].split("!")[0]
            fix = None
        else:
            head = failed["headline"]
            words = "%s: %s" % (failed["headline"], failed["detail"])
            fix = failed["fix"]
        passed_part, next_part = False, None
        if not c.is_demo:
            self.streak = self.streak + 1 if success else 0
            if self.streak >= part["streak"]:
                passed_part = True
                if self.part_index + 1 < len(self.parts):
                    self.part_index += 1
                    next_part = self.part_now["name"]
                self.streak = 0
        c.result(success, words, headline=head, fix=fix,
                 checks=[dict(expect=d["expect"], passed=d["passed"],
                              detail=d["detail"], counted=d in counted)
                         for d in done],
                 part=part["name"], part_number=self.parts.index(part) + 1,
                 parts=len(self.parts), streak=self.streak,
                 part_passed=passed_part, next_part=next_part)


class Refs(list):
    """A reference, and the events its inputs are timed from (`anchors`:
    mark k is the k-th)."""

    def __init__(self):
        super().__init__()
        self.anchors = []


def inputs_to_refs(inputs, nums, start=REF_START):
    """A drill's inputs (frame 1 = the attempt's first) as the course
    runtime's reference (Ref), after a lead of `start` frames. An input
    timed "from" an event is a mark's (frame 1 the event's own frame)."""
    out = Refs()
    for i in inputs:
        f = int(F.value(i["frame"], nums))
        hold = int(F.value(i.get("hold", 1), nums))
        kw = {}
        if "press" in i:
            kw["buttons"] = F.BUTTONS[i["press"]] & ~0x800 \
                if i["press"] == "jump" else F.BUTTONS[i["press"]]
        elif "stick" in i:
            kw["lx"], kw["ly"] = (int(round(F.value(a, nums) * 127))
                                  for a in i["stick"])
            # [0, 0]: the stick in the middle, over an earlier input's
            kw["still"] = kw["lx"] == 0 and kw["ly"] == 0
        elif "cstick" in i:
            kw["cx"], kw["cy"] = (int(round(F.value(a, nums) * 127))
                                  for a in i["cstick"])
        else:
            kw["buttons"] = F.BUTTONS[i["trigger"]]
            kw["trigger"] = int(i.get("amount", 1.0) * 255)
        if "from" in i:
            if i["from"] not in out.anchors:
                out.anchors.append(i["from"])
            out.append(Ref(1 + out.anchors.index(i["from"]), f - 1, hold,
                           **kw))
        else:
            out.append(Ref(0, start + f - 1, hold, **kw))
    return out


def get(drill_id):
    return JsonDrill(F.load(drill_id))
