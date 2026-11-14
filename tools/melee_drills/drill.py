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
from melee_course.engine import Drill, Ref, Row

from melee_drills import format as F

WAIT, ATTEMPT = 0, 1
LIMIT = 150               # frames an attempt may last before it is dropped
REF_START = 10            # the demonstration's frame 1, after its lead


class JsonDrill(Drill):
    def __init__(self, spec):
        super().__init__()
        self.spec = spec
        self.id = spec["id"]
        self.name = spec["name"]
        self.goal = spec["goal"]
        self.part = spec["part"]
        sc = spec["scenarios"][0]
        self.cpu = None if sc.get("opponent", "none") == "none" else \
            sc["opponent"]
        self.stage = sc.get("stage", "final-destination")
        chars = spec.get("characters", "all")
        self.characters = None if chars == "all" else tuple(chars)
        # a tech drill alone: the player sets the pace, nothing is reset
        self.flow = self.cpu is None
        self.help = (spec["goal"], "D-Pad up: tutorial. D-Pad down: reset.")
        self.part_index = 0
        self.streak = 0
        self.v = {}

    # ---- the drill's numbers -------------------------------------------------------

    def nums(self, c):
        return F.names(c.fd, c.fd.id.replace("-", " ").title())

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
        sc = self.spec["scenarios"][0]
        c.place_solo(float(sc["player"]["x"]))
        self.camera(c.n, c.s.person)
        self.v = dict(rec=[])

    def camera(self, n, person):
        """The scenario's camera (the client puts the match camera back
        when the drill is left). A game built before the camera command
        keeps its own camera."""
        from native import NativeError
        cam = self.spec["scenarios"][0].get("camera", "normal")
        try:
            if isinstance(cam, dict):
                n.camera("follow", person, cam["distance"],
                         cam.get("height", 10))
            else:
                n.camera(cam)
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
        return inputs_to_refs(self.part_now["example"], self.nums(c))

    def timeline(self, c):
        nums = self.nums(c)
        rows = []
        for r in self.spec["coach"].get("rows", []):
            rows.append(Row(
                F.text(r["label"], nums), buttons=F.BUTTONS[r["button"]],
                held=r.get("held", True),
                perfect=tuple(int(F.value(x, nums))
                              for x in r.get("perfect", [1])),
                window=tuple(int(F.value(x, nums)) for x in r["window"])
                if "window" in r else None))
        return rows, F.text(self.spec["coach"].get("note", ""), nums)

    # ---- an attempt, frame by frame ------------------------------------------------

    def _happened(self, event, c, rec):
        if event == "airborne":
            return c.me.airborne
        state = F.STATES[event["enters"]]
        return c.state == state and c.state_frames == 1

    def think(self, c):
        a = self.spec["attempt"]
        v = self.v
        if c.phase == WAIT:
            if not self._happened(a["start"], c, None):
                return
            c.set_phase(ATTEMPT)
            c.tl_begin()
            v["rec"] = []
        rec = v["rec"]
        rec.append(dict(state=c.state, air=c.me.airborne, vy=c.me.vel[1],
                        held=c.held, down=c.down))
        if self._happened(a["judge"], c, rec):
            self._judge(c, rec)
            return
        start = a["start"]
        left = isinstance(start, dict) and "enters" in start and \
            c.state != F.STATES[start["enters"]]
        if (left and not c.me.airborne) or len(rec) > LIMIT:
            # it went another way (a hit, a jump-cancelled move): not an
            # attempt at this
            c.set_phase(WAIT)

    def _measure(self, m, c, rec):
        if m == "jump_kind":
            vy = rec[-1]["vy"]
            return "short" if vy < (c.fd.hop_v + c.fd.jump_v) / 2 else "full"
        if isinstance(m, dict) and "held" in m:
            bits = F.BUTTONS[m["held"]]
            n = 0
            for r in rec:
                if not r["held"] & bits:
                    break
                n += 1
            return n
        raise F.DrillError("unknown measure %r" % (m,))

    def _check(self, name, c, rec, nums, measured):
        ck = self.spec["checks"][name]
        got = measured[ck["measure"]]
        if "equals" in ck:
            ok = got == ck["equals"]
        elif "at_most" in ck:
            ok = got <= F.value(ck["at_most"], nums)
        elif "at_least" in ck:
            ok = got >= F.value(ck["at_least"], nums)
        else:
            lo, hi = (F.value(x, nums) for x in ck["within"])
            ok = lo <= got <= hi
        more = dict(measure=got)
        if isinstance(got, int):
            more["frames"] = F.plural(got)
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
            out[k] = v
            if isinstance(v, int):
                out[k + "_frames"] = F.plural(v)
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
