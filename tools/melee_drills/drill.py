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
    cid = fd.id
    if "enters" in e:
        return _in(f["state"], e["enters"], cid) and \
            not _in(p["state"], e["enters"], cid) and \
            ("from" not in e or _in(p["state"], e["from"], cid))
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
        self.part_index = 0
        self.streak = 0
        self.v = {}

    # ---- the drill's numbers -------------------------------------------------------

    def nums(self, c):
        return F.names(c.fd, c.fd.id.replace("-", " ").title())

    lesson_scenario = None  # a lesson's own, while the client records it
    scenario_at = None      # the one of a part's list played now
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
        return [Entry(self.cpu, i, self.spec["scenarios"][i]["name"])
                for i in idx]

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
        op = sc.get("opponent", "none")
        if isinstance(op, dict):
            x = float(op["x"])
            toward = -1 if x > px else 1
            c.place_cpu(x, -toward if op.get("facing") == "away" else
                        toward, float(F.value(op.get("percent", 0), nums)))
            self.op_refs = inputs_to_refs(op.get("inputs", []), nums, 1) \
                if op.get("inputs") else []
            self.op_toward = toward
        else:
            self.op_refs = []
        self.camera(c.n, c.s.person)
        self.trace(c.n, c.s.person)
        self.v = dict(rec=[], last=None)

    filming = False     # the client recording the tutorial's examples
    strict = False      # frame-perfect timing (Settings): checks' "strict"

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
                    p=self.v.get("last"), i=-1, nums=self.v.get("nums"))

    def _opponent(self, c):
        """The opponent's inputs this frame (its "inputs", frame 1 the
        first after the reset, again every "every" frames); stick x
        toward the player."""
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

    def attempt(self):
        """The part's attempt: the drill's, with what the part changes."""
        a = dict(self.spec["attempt"])
        a.update(self.part_now.get("attempt", {}))
        return a

    def _lesson_inputs_left(self, c):
        """While the client records a lesson (its own scenario and inputs,
        build_reference): whether the lesson's inputs have frames still to
        play."""
        build = vars(self).get("build_reference")
        if self.lesson_scenario is None or build is None:
            return False
        js = c.fd.jump_squat
        end = max((self.ref_lead + r.frame + r.js * js + (r.hold or 1)
                   for r in build(c) if r.mark == 0), default=0)
        return c.s.attempt_frame < end

    def think(self, c):
        a = self.attempt()
        v = self.v
        v["nums"] = v.get("nums") or self.nums(c)
        self._opponent(c)
        f = self._frame(c)
        if c.phase == WAIT and f["p"] is not None:
            f["p"]["p"] = None      # (no chain of every frame since)
        v["last"] = f
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
        part = self.part_now
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


def inputs_to_refs(inputs, nums, start=REF_START):
    """A drill's inputs (frame 1 = the attempt's first) as the course
    runtime's reference (Ref), after a lead of `start` frames."""
    out = []
    for i in inputs:
        f = int(F.value(i["frame"], nums))
        hold = int(F.value(i.get("hold", 1), nums))
        kw = {}
        if "press" in i:
            kw["buttons"] = F.BUTTONS[i["press"]] & ~0x800 \
                if i["press"] == "jump" else F.BUTTONS[i["press"]]
        elif "stick" in i:
            kw["lx"], kw["ly"] = (int(round(a * 127)) for a in i["stick"])
        elif "cstick" in i:
            kw["cx"], kw["cy"] = (int(round(a * 127)) for a in i["cstick"])
        else:
            kw["buttons"] = F.BUTTONS[i["trigger"]]
            kw["trigger"] = int(i.get("amount", 1.0) * 255)
        out.append(Ref(0, start + f - 1, hold, **kw))
    return out


def get(drill_id):
    return JsonDrill(F.load(drill_id))
