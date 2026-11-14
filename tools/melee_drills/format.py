"""The drill format (docs/ai/drill-format.md): a drill is a JSON file,
data/drills/<id>.json, made only of the words defined here. `load(id)`
reads one and checks it; a drill that does not hold to the format is
refused with every problem named.

Numbers in a drill may be written as expressions of the character's own
numbers (`names()`): "J-1" is one frame before the end of the jump squat,
whatever the character. Text may hold {expressions} the same way, and
{char}, {measure}.

The words:

- events (an attempt's start and judgement): {"enters": STATE}, "airborne"
- measures, named once in "measures" and used by name in checks and
  words ({held}, and {held_frames} for "2 frames"): "jump_kind" ("short" or
  "full", read from the rise speed on the first frame in the air),
  {"held": BUTTON} (frames the button was held from the attempt's first
  frame)
- expectations: "equals", "at_most", "at_least", "within" [lo, hi]
- inputs: {"press": BUTTON, "frame": F, "hold": H}, {"stick": [x, y], ...},
  {"cstick": [x, y], ...}, {"trigger": "L"|"R", "amount": 0..1, ...};
  stick x positive is forward (toward the opponent, if there is one); -1..1
- opponents: "none" (no CPU in the drill: none is spawned, and one a
  match already has is asleep: out of play, out of the picture)
- cameras: "normal" (the match camera), "stage" (the whole stage, still),
  {"follow": "player", "distance": D, "height": H} (the game's free camera
  on the player: D in front, H above; Training Mode's "Zoom" is 140 and
  10)

A new word is added here (and to the doc), with a drill that uses it and
its proof (check.py), never written into one drill's file.
"""
import ast
import json
import os
import re

ROOT = os.path.normpath(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "..", ".."))
DIR = os.path.join(ROOT, "data", "drills")

PARTS = ("tech", "neutral", "punish", "defense")

# action states by name (ftCo_MS_*, as the game numbers them)
STATES = {
    "wait": 14, "jump_squat": 24, "jump_f": 25, "jump_b": 26,
    "landing": 42, "landing_special": 43, "air_dodge": 236,
}

BUTTONS = {
    "A": 0x100, "B": 0x200, "X": 0x400, "Y": 0x800, "Z": 0x10,
    "R": 0x20, "L": 0x40, "jump": 0x400 | 0x800, "shield": 0x20 | 0x40,
}
BUTTON_WORDS = {"jump": "X or Y", "shield": "L or R"}

EVENTS = ("enters", "airborne")
MEASURES = ("jump_kind", "held")
EXPECTS = ("equals", "at_most", "at_least", "within")
INPUTS = ("press", "stick", "cstick", "trigger")
OPPONENTS = ("none",)
CAMERAS = ("normal", "stage")

TOP = {
    "id": str, "name": str, "part": str, "goal": str, "why": str,
    "tutorial": dict, "scenarios": list, "attempt": dict, "measures": dict,
    "checks": dict, "verdict": dict, "parts": list, "coach": dict,
}
OPTIONAL = {"characters": (str, list), "mistakes": list}


class DrillError(Exception):
    pass


# ---- the character's numbers, and expressions of them ---------------------------

def names(fd, char_name=""):
    """The numbers a drill may name, for one character (its frame data,
    melee_course.engine.FighterData)."""
    return {"J": fd.jump_squat, "char": char_name or fd.id}


_OPS = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Add, ast.Sub, ast.Mult,
        ast.FloorDiv, ast.USub, ast.UAdd, ast.Constant, ast.Name, ast.Load)


def value(x, nums):
    """A number of a drill: an int, or an expression of `nums` ("J-1")."""
    if isinstance(x, bool):
        raise DrillError("not a number: %r" % (x,))
    if isinstance(x, (int, float)):
        return x
    if not isinstance(x, str):
        raise DrillError("not a number: %r" % (x,))
    try:
        tree = ast.parse(x.strip(), mode="eval")
    except SyntaxError:
        raise DrillError("not an expression: %r" % x)
    for node in ast.walk(tree):
        if not isinstance(node, _OPS):
            raise DrillError("not allowed in %r: %s" % (x, type(node).__name__))
        if isinstance(node, ast.Name) and node.id not in nums:
            raise DrillError("unknown number %r in %r" % (node.id, x))
    return eval(compile(tree, "<drill>", "eval"), {"__builtins__": {}},
                {k: v for k, v in nums.items() if not isinstance(v, str)})


def text(t, nums, **more):
    """A drill's words with their {expressions} filled in."""
    have = dict(nums)
    have.update(more)

    def fill(m):
        inner = m.group(1)
        if inner in have and isinstance(have[inner], str):
            return have[inner]
        if inner in have:
            v = have[inner]
            return str(int(v)) if isinstance(v, float) and v == int(v) \
                else str(v)
        return str(value(inner, have))
    return re.sub(r"\{([^{}]+)\}", fill, t)


def plural(n, word="frame"):
    return "%d %s%s" % (n, word, "" if n == 1 else "s")


# ---- checking a drill against the format -------------------------------------------

def _problems(spec):
    out = []

    def need(cond, where, what):
        if not cond:
            out.append("%s: %s" % (where, what))
        return cond

    test = {"J": 3, "char": "Fox", "measure": "x", "frames": "2 frames"}
    for m in spec.get("measures", {}) if isinstance(spec.get("measures"),
                                                     dict) else ():
        test[m] = 2
        test[m + "_frames"] = "2 frames"

    def num(x, where):
        try:
            value(x, test)
        except DrillError as e:
            out.append("%s: %s" % (where, e))

    def words(t, where):
        if need(isinstance(t, str), where, "words expected"):
            try:
                text(t, test)
            except DrillError as e:
                out.append("%s: %s" % (where, e))

    def inputs(lst, where):
        if not need(isinstance(lst, list) and lst, where,
                    "a list of inputs expected"):
            return
        for i, inp in enumerate(lst):
            w = "%s[%d]" % (where, i)
            kinds = [k for k in INPUTS if k in inp]
            if not need(len(kinds) == 1, w, "one of %s" % ", ".join(INPUTS)):
                continue
            k = kinds[0]
            if k == "press":
                need(inp["press"] in BUTTONS, w, "unknown button %r"
                     % inp["press"])
            elif k in ("stick", "cstick"):
                v = inp[k]
                need(isinstance(v, list) and len(v) == 2 and
                     all(isinstance(a, (int, float)) and -1 <= a <= 1
                         for a in v), w, "[x, y] from -1 to 1")
            else:
                need(inp["trigger"] in ("L", "R"), w, "trigger L or R")
            need("frame" in inp, w, "no frame")
            if "frame" in inp:
                num(inp["frame"], w + ".frame")
            if "hold" in inp:
                num(inp["hold"], w + ".hold")
            extra = set(inp) - {k, "frame", "hold", "amount"}
            need(not extra, w, "unknown %s" % ", ".join(sorted(extra)))

    def event(e, where):
        if e == "airborne":
            return
        if need(isinstance(e, dict) and len(e) == 1, where,
                "an event: %s" % ", ".join(EVENTS)):
            k, v = next(iter(e.items()))
            if need(k == "enters", where, "unknown event %r" % k):
                need(v in STATES, where, "unknown state %r" % v)

    def marks(m, where):
        if need(isinstance(m, dict), where, "{frame: words} expected"):
            for f, w in m.items():
                num(f, "%s[%s]" % (where, f))
                words(w, "%s[%s]" % (where, f))

    for k, typ in TOP.items():
        need(k in spec, "drill", "no %r" % k) and \
            need(isinstance(spec[k], typ), k, "%s expected" % typ.__name__)
    for k in spec:
        need(k in TOP or k in OPTIONAL, "drill", "unknown key %r" % k)
    if out:
        return out
    need(re.match(r"^[a-z0-9-]+$", spec["id"]) is not None, "id",
         "lower case, digits and dashes")
    need(spec["part"] in PARTS, "part", "one of %s" % ", ".join(PARTS))
    for k in ("goal", "why"):
        words(spec[k], k)

    t = spec["tutorial"]
    for k in ("what", "expect"):
        words(t.get(k), "tutorial.%s" % k)
    inputs(t.get("example"), "tutorial.example")
    marks(t.get("marks", {}), "tutorial.marks")

    for i, sc in enumerate(spec["scenarios"]):
        w = "scenarios[%d]" % i
        need(isinstance(sc.get("name"), str), w, "no name")
        need(sc.get("opponent") in OPPONENTS, w, "opponent: one of %s"
             % ", ".join(OPPONENTS))
        need(isinstance(sc.get("player", {}).get("x"), (int, float)), w,
             "player: {\"x\": number}")
        cam = sc.get("camera", "normal")
        if isinstance(cam, dict):
            need(cam.get("follow") == "player" and
                 isinstance(cam.get("distance"), (int, float)) and
                 isinstance(cam.get("height", 10), (int, float)), w,
                 'camera: {"follow": "player", "distance": D, "height": H}')
        else:
            need(cam in CAMERAS, w, "camera: one of %s, or follow"
                 % ", ".join(CAMERAS))

    a = spec["attempt"]
    event(a.get("start"), "attempt.start")
    event(a.get("judge"), "attempt.judge")

    for name, m in spec["measures"].items():
        w = "measures[%r]" % name
        need(re.match(r"^[a-z_]+$", name) is not None, w,
             "a name of lower case letters and _")
        if m == "jump_kind":
            pass
        elif isinstance(m, dict) and set(m) == {"held"}:
            need(m["held"] in BUTTONS, w, "unknown button %r" % m["held"])
        else:
            out.append("%s: unknown measure %r" % (w, m))
    words(spec["verdict"].get("success"), "verdict.success")

    for name, c in spec["checks"].items():
        w = "checks[%r]" % name
        need(c.get("measure") in spec["measures"], w,
             "measure: one of the drill's measures")
        exp = [k for k in EXPECTS if k in c]
        if need(len(exp) == 1, w, "one of %s" % ", ".join(EXPECTS)):
            k = exp[0]
            if k == "within":
                need(isinstance(c[k], list) and len(c[k]) == 2, w,
                     "within: [lo, hi]")
                for x in c[k] if isinstance(c[k], list) else ():
                    num(x, w + ".within")
            elif k != "equals":
                num(c[k], "%s.%s" % (w, k))
        words(c.get("words"), w + ".words")
        words(c.get("fix"), w + ".fix")
        words(c.get("expect", "x"), w + ".expect")

    for i, p in enumerate(spec["parts"]):
        w = "parts[%d]" % i
        words(p.get("name"), w + ".name")
        words(p.get("teach"), w + ".teach")
        if "success" in p:
            words(p["success"], w + ".success")
        inputs(p.get("example"), w + ".example")
        marks(p.get("marks", {}), w + ".marks")
        for c in p.get("checks", []):
            need(c in spec["checks"], w, "no check %r" % c)
        need(isinstance(p.get("streak"), int) and p["streak"] >= 1, w,
             "streak: a whole number from 1")

    for i, m in enumerate(spec.get("mistakes", [])):
        w = "mistakes[%d]" % i
        words(m.get("name"), w + ".name")
        inputs(m.get("inputs"), w + ".inputs")
        need(m.get("fails") in spec["checks"], w, "fails: a check's name")

    co = spec["coach"]
    for i, r in enumerate(co.get("rows", [])):
        w = "coach.rows[%d]" % i
        words(r.get("label"), w + ".label")
        need(r.get("button") in BUTTONS, w, "unknown button")
        if "window" in r:
            for x in r["window"]:
                num(x, w + ".window")
        if "perfect" in r:
            for x in r["perfect"]:
                num(x, w + ".perfect")
    words(co.get("note", ""), "coach.note")
    return out


def load(drill_id=None, path=None):
    """The drill `drill_id` (or the file `path`), checked."""
    path = path or os.path.join(DIR, drill_id + ".json")
    with open(path) as f:
        try:
            spec = json.load(f)
        except ValueError as e:
            raise DrillError("%s: not JSON: %s" % (path, e))
    problems = _problems(spec)
    if problems:
        raise DrillError("%s does not hold to the drill format:\n  %s"
                         % (path, "\n  ".join(problems)))
    return spec


def ids():
    if not os.path.isdir(DIR):
        return []
    return sorted(f[:-5] for f in os.listdir(DIR) if f.endswith(".json"))
