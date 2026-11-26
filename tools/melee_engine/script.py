"""An opponent's script (docs/ai/opponent-vocabulary.md, layer 4): behaviours
in order, branching, looping, mixing, as a drill's scenario writes them.

    "opponent": {
      "character": "marth", "x": 40, "react": 15,
      "script": [
        {"do": "footsies", "range": "outside", "until": "approach"},
        {"mix": [
          {"weight": 2, "steps": [{"do": "approach", "moves": "sh_",
                                   "lands": "hit"}]},
          {"weight": 1, "steps": [{"do": "retreat", "for": 40}]}]}
      ],
      "loop": true
    }

A step is a behaviour ({"do": NAME, its keys, "until": CONDITION, "for":
FRAMES}; behave.py) or a combinator:

- {"if": C, "then": [...], "else": [...]}: C read when the step starts;
- {"mix": [{"weight": W, "steps": [...]}, ...]}: one of them by weight;
- {"repeat": [...], "while": C, "times": N}: again while C holds (read
  before each time) and at most N times (either may be left out: both,
  for ever);
- "loop": true (the opponent's): the whole script again when it ends.

{"after": N} in a step's `until` counts the behaviour's frames, in an `if`
or a `while` the frames since the innermost repeat (else the script)
began.

The random choices (mix, and every behaviour's own) come from `seed`: the
same seed plays the same opponent (check.py's examples and mistakes, the
coach's demonstration). Decisions are made where `think` makes them: a
fork of the game while a person plays (fork.InFork), the game itself
headless (drill.Here); the conditions' searches too.

    opp = Opponent(think, port=1, target=0, spec=scenario["opponent"],
                   seed=7, half=85.6)
    ...each frame, before it is played:
    raw = opp.pad(n.state(), their=player_raw)
"""
import random

from melee_engine import behave as B
from melee_engine import sense as S
from melee_engine.drill import NONE

KEYS = ("character", "x", "facing", "percent", "react", "script", "loop")
STEP_KEYS = ("until", "for")
COMBINATORS = ("do", "if", "mix", "repeat")
DEPTH = 16                # combinators nested at most
PER_FRAME = 32            # steps begun in one frame at most


# ---- the format -------------------------------------------------------------

def problems(op, where="opponent", states=None):
    """What is wrong with a scripted opponent `op` (a scenario's
    "opponent": its react, script and loop; the drill format checks the
    rest), every behaviour, condition and combinator named checked against
    the tables. [] if nothing."""
    out = []
    if "react" in op and not (isinstance(op["react"], int) and
                              0 <= op["react"] <= 60):
        out.append("%s.react: frames, 0 to 60" % where)
    if "loop" in op and not isinstance(op["loop"], bool):
        out.append("%s.loop: true or false" % where)
    out += steps_problems(op.get("script"), where + ".script", states)
    return out


def steps_problems(steps, where, states=None, depth=0):
    if not isinstance(steps, list) or not steps:
        return ["%s: a list of steps" % where]
    if depth > DEPTH:
        return ["%s: nested more than %d deep" % (where, DEPTH)]
    out = []
    for i, s in enumerate(steps):
        out += step_problems(s, "%s[%d]" % (where, i), states, depth)
    return out


def step_problems(s, w, states=None, depth=0):
    if not isinstance(s, dict):
        return ["%s: a step: {\"do\": ...} or a combinator" % w]
    kinds = [k for k in COMBINATORS if k in s]
    if len(kinds) != 1:
        return ["%s: one of %s" % (w, ", ".join(COMBINATORS))]
    k = kinds[0]
    out = []

    def cond(c, where):
        out.extend(S.problems(c, where, states))

    if k == "do":
        name = s["do"]
        if name in B.NOT_BUILT:
            return ["%s: %s is not built yet" % (w, name)]
        if name not in B.BEHAVIOURS:
            return ["%s: unknown behaviour %r (one of %s)" % (
                w, name, ", ".join(sorted(B.BEHAVIOURS)))]
        params = B.PARAMS[name]
        for key in B.REQUIRED.get(name, ()):
            if key not in s:
                out.append("%s: %s needs %r" % (w, name, key))
        for key, v in s.items():
            if key in ("do",) + STEP_KEYS:
                continue
            if key not in params:
                out.append("%s: %s has no %r (it has %s)" % (
                    w, name, key, ", ".join(params) or "nothing more"))
            elif not params[key][0](v):
                out.append("%s.%s: %s" % (w, key, params[key][1]))
        if "for" in s and not (isinstance(s["for"], int) and s["for"] > 0):
            out.append("%s.for: frames" % w)
        if "until" in s:
            cond(s["until"], w + ".until")
    elif k == "if":
        extra = set(s) - {"if", "then", "else"}
        if extra:
            out.append("%s: unknown %s" % (w, ", ".join(sorted(extra))))
        cond(s["if"], w + ".if")
        out += steps_problems(s.get("then"), w + ".then", states, depth + 1)
        if "else" in s:
            out += steps_problems(s["else"], w + ".else", states, depth + 1)
    elif k == "mix":
        extra = set(s) - {"mix"}
        if extra:
            out.append("%s: unknown %s" % (w, ", ".join(sorted(extra))))
        mix = s["mix"]
        if not isinstance(mix, list) or not mix:
            return out + ["%s.mix: a list of {\"weight\", \"steps\"}" % w]
        for i, m in enumerate(mix):
            mw = "%s.mix[%d]" % (w, i)
            if not isinstance(m, dict) or set(m) - {"weight", "steps"}:
                out.append("%s: {\"weight\": W, \"steps\": [...]}" % mw)
                continue
            if not (isinstance(m.get("weight", 1), (int, float)) and
                    m.get("weight", 1) > 0):
                out.append("%s.weight: a number above 0" % mw)
            out += steps_problems(m.get("steps"), mw + ".steps", states,
                                  depth + 1)
    else:
        extra = set(s) - {"repeat", "while", "times"}
        if extra:
            out.append("%s: unknown %s" % (w, ", ".join(sorted(extra))))
        if "while" in s:
            cond(s["while"], w + ".while")
        if "times" in s and not (isinstance(s["times"], int) and
                                 s["times"] > 0):
            out.append("%s.times: a count from 1" % w)
        out += steps_problems(s.get("repeat"), w + ".repeat", states,
                              depth + 1)
    return out


def conditions(steps):
    """Every condition a script reads."""
    out = []
    for s in steps or ():
        if not isinstance(s, dict):
            continue
        for k in ("until", "if", "while"):
            if k in s:
                out.append(s[k])
        for k in ("then", "else", "repeat"):
            out += conditions(s.get(k))
        for m in s.get("mix", ()) if isinstance(s.get("mix"), list) else ():
            out += conditions(m.get("steps"))
    return out


# ---- playing it -------------------------------------------------------------

class Opponent:
    """A script played, one pad a frame. `trace`: what it did, [(frame,
    words)]; `choices`: each mix's choice in order (its index); `cur`: the
    behaviour on now; `over`: the script has ended (no loop)."""

    def __init__(self, think, port, target, spec, seed=0, half=85.0,
                 char=None, react=None, temperature=6.0, memory=None):
        self.spec = spec
        self.seed, self.char = seed, char
        self.steps = spec["script"]
        self.loop = bool(spec.get("loop", False))
        react = spec.get("react", S.REACT) if react is None else react
        self.rng = random.Random(seed)
        self.sense = S.Sense(port, target, react=react, think=think,
                             half=half, char=char)
        for c in conditions(self.steps):
            self.sense.wants |= S.uses(c)
        self.ctx = B.Ctx(think, port, target, self.sense, rng=self.rng,
                         react=react, half=half, temperature=temperature)
        # what its approaches learnt (behave.Approach: the families it
        # attacked with, what each came to), from the attempts before
        # (`memory`, the drill's)
        memory = memory or {}
        self.ctx.memory["families"] = list(memory.get("families", []))
        self.ctx.memory["tried"] = {f: list(v) for f, v in
                                    memory.get("tried", {}).items()}
        # and what its other behaviours keep (recover: the kinds of route
        # it flew, what they came to)
        import copy
        for k, v in memory.items():
            if k not in ("families", "tried"):
                self.ctx.memory[k] = copy.deepcopy(v)
        self.frame = -1
        self.cur = None           # the behaviour on now
        self.cur_spec = None
        self.blocks = []          # frames the repeats on now began on
        self.begun = 0            # behaviours begun
        self.over = False
        self.passes = 0
        self.trace = []
        self.choices = []
        self.gen = self._run()

    # -- the steps, in order --------------------------------------------------

    def _after(self):
        return self.frame - (self.blocks[-1] if self.blocks else 0)

    def _test(self, c):
        return self.sense.test(c, after=self._after())

    def _block(self, steps):
        for s in steps:
            if "do" in s:
                yield s
            elif "if" in s:
                ok = self._test(s["if"])
                self.trace.append((self.frame, "if %s" % ok))
                yield from self._block(s["then"] if ok else
                                       s.get("else", []))
            elif "mix" in s:
                mix = s["mix"]
                i = self.rng.choices(range(len(mix)), weights=[
                    float(m.get("weight", 1)) for m in mix])[0]
                self.choices.append(i)
                self.trace.append((self.frame, "mix %d" % i))
                yield from self._block(mix[i]["steps"])
            elif "repeat" in s:
                times, cond = s.get("times"), s.get("while")
                self.blocks.append(self.frame)
                try:
                    i = 0
                    while (times is None or i < times) and \
                            (cond is None or self._test(cond)):
                        before = self.begun
                        yield from self._block(s["repeat"])
                        i += 1
                        if self.begun == before:
                            break         # nothing in it: not for ever
                    self.trace.append((self.frame, "repeat %d" % i))
                finally:
                    self.blocks.pop()

    def _run(self):
        while True:
            before = self.begun
            yield from self._block(self.steps)
            if not self.loop or self.begun == before:
                return
            self.passes += 1

    def _ended(self, b, s):
        if b.done:
            return "done"
        why = None
        if "for" in s and b.frame >= s["for"]:
            why = "for"
        elif "until" in s and self.sense.test(s["until"], after=b.frame):
            why = "until"
        # a behaviour may play out what it is in the middle of first
        # (footsies with "finish": its phrase): asked to end once, it ends
        # when it can, whatever the condition says by then
        why = why or b.ending
        if why is not None and not b.may_end():
            b.ending = why
            return None
        return why

    def _next(self):
        try:
            s = next(self.gen)
        except StopIteration:
            self.over = True
            return None, None
        self.begun += 1
        self.trace.append((self.frame, "do " + s["do"]))
        return B.make(self.ctx, s), s

    # -- each frame -----------------------------------------------------------

    def pad(self, st, their=None):
        """This frame's raw pad (call once a frame, before it is played).
        `their`: the player's raw pad this frame."""
        self.sense.update(st, their)
        self.ctx.their = tuple(their) if their is not None else NONE
        self.frame = self.sense.frame
        for _ in range(PER_FRAME):
            if self.over:
                return NONE
            b = self.cur
            if b is not None:
                why = self._ended(b, self.cur_spec)
                if why is None:
                    break
                b.stop()
                self.trace.append((self.frame, "end %s: %s after %d" % (
                    self.cur_spec["do"], why, b.frame)))
            self.cur, self.cur_spec = self._next()
        else:
            return NONE           # steps that take no frame: one a frame
        if self.cur is None:
            return NONE
        k = self.sense.frames + self.sense.cache + 1
        self.sense.ask(self.cur.plan(st, k))
        return self.cur.pad(st)

    def stop(self):
        if self.cur is not None:
            self.cur.stop()
        self.sense.forget()

    @property
    def doing(self):
        return self.cur_spec["do"] if self.cur_spec else None
