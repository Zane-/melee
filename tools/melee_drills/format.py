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
- lessons (the tutorial's, before the parts: the concept taught): a
  title, a text (a paragraph or a list of them), and what is shown:
  {"example": {"inputs", "marks", "cues"}} (played frame by frame, each
  frame captioned) or {"still": {"inputs", "frame", "cue"}} (one picture
  of that example: its frame `frame`, a cue {"words", "kind"} on it); and
  "characters": NUMBER (every character's NUMBER in a table below, the
  player's marked: "jump_squat")
- cues (on a lesson's example or a part's): {"frames": [lo, hi], "words",
  "kind": "go" | "late" | "info"}: a colour and words on the picture for
  those frames ("let go now", "too late"); {f} in them is the frame shown
- the tutorial's camera (tutorial.camera, optional): the one its examples
  are filmed with (closer, to see the animation); the scenario's otherwise
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

# action states by name (ftCo_MS_* and Fox's ftFx_MS_*, as the game numbers
# them: src/melee/ft/kinds/ftCommon/forward.h, ftFox/forward.h); a tuple is
# a group, any of whose states counts
STATES = {
    "wait": 14, "turn": 18, "turn_run": 19, "dash": 20, "run": 21,
    "run_brake": 23, "jump_squat": 24, "jump_f": 25, "jump_b": 26,
    "jump": (25, 26), "double_jump": (27, 28),
    "fall": (29, 30, 31, 32, 33, 34), "special_fall": (35, 36, 37),
    "squat": (39, 40), "landing": 42, "landing_special": 43,
    "up_smash": 63, "nair": 65, "fair": 66, "bair": 67, "uair": 68,
    "dair": 69, "aerial": (65, 66, 67, 68, 69),
    "aerial_landing": (70, 71, 72, 73, 74),
    "shield": (178, 179, 180, 181, 182), "grab": 212, "dash_grab": 214,
    "air_dodge": 236, "platform_drop": 244, "teeter": (245, 246),
    "roll": (233, 234), "spot_dodge": 235,
    # hit: in hitstun (DamageHi1 to DamageFlyRoll); launched (DamageFly*)
    "damage": tuple(range(75, 92)), "tumble": (87, 88, 89, 90, 91),
    "ledge": (252, 253), "ledge_catch": 252, "ledge_hang": 253,
    # Fox
    "laser": (341, 342, 343, 344, 345, 346),
    "illusion": (347, 348, 349, 350, 351, 352),
    "illusion_dash": (348, 351), "illusion_end": (349, 352),
    "firefox_charge": (353, 354), "firefox": (355, 356),
    "firefox_any": (353, 354, 355, 356, 357, 358, 359),
    "shine": (360, 361, 362, 363, 364, 365, 366, 367, 368, 369),
    "shine_ground": (360, 361, 362, 363, 364),
}

# a state's numbers that differ by character (a character's own states are
# numbered from 341, each its own: Kirby's and Jigglypuff's extra jumps are
# 341 on, where Fox has his laser)
CHAR_STATES = {
    "kirby": {"double_jump": (27, 28) + tuple(range(341, 351))},
    "jigglypuff": {"double_jump": (27, 28) + tuple(range(341, 346))},
    # Ness's up smash charges in states of its own; Yoshi's shield is his
    "ness": {"up_smash": (63, 342, 343, 344)},
    "yoshi": {"shield": (178, 179, 180, 181, 182) + tuple(range(341, 346))},
}

BUTTONS = {
    "A": 0x100, "B": 0x200, "X": 0x400, "Y": 0x800, "Z": 0x10,
    "R": 0x20, "L": 0x40, "jump": 0x400 | 0x800, "shield": 0x20 | 0x40,
    # what L-cancels: L, R (a light press past the trigger threshold too)
    # or Z
    "lcancel": 0x20 | 0x40 | 0x10,
}
BUTTON_WORDS = {"jump": "X or Y", "shield": "L or R",
                "lcancel": "L, R or Z"}

# events: when something happened, frame by frame. A word, or a dict of one
# kind (with "in_air" / "on_ground": true to require either, "from" / "to"
# a state for enters / leaves), or a list of them (any)
# hitlag_last: the last frozen frame of hitlag, whose stick DI and ASDI read
# (Fighter_procHitlag runs before the frame's input); shot: an item more
# than the frame before (a projectile fired: a laser)
SIMPLE_EVENTS = ("start", "end", "airborne", "lands", "apex", "fast_fall",
                 "hit", "hitlag_last", "hitlag_end", "shot")
# "is": a simple event with modifiers ({"is": "airborne", "from": "shine"})
EVENT_KINDS = ("enters", "leaves", "pressed", "released", "stick", "cstick",
               "frame", "is")
# "after": an event that must have happened on an earlier frame of the
# attempt (left the ground after a shine, not in the first short hop)
EVENT_MODS = ("in_air", "on_ground", "from", "to", "after")
DIRECTIONS = ("up", "down", "forward", "back", "neutral")
EVENTS = SIMPLE_EVENTS + EVENT_KINDS
MEASURES = ("jump_kind", "held", "frames", "frame_of", "happened", "count",
            "value", "distance", "frames_while", "angle", "max_gap",
            "moved_while")
# what a "value" measure reads at an event: dx, dy from the attempt's first
# frame (dx toward where the player faced then)
FIELDS = ("x", "y", "dx", "dy", "vx", "vy", "percent", "state", "facing",
          "hitlag", "turned")
CONDITIONS = ("invulnerable", "airborne", "grounded", "hitlag")
EXPECTS = ("equals", "at_most", "at_least", "within")
INPUTS = ("press", "stick", "cstick", "trigger")
OPPONENTS = ("none",)       # or {"character", "x", "inputs", ...}
CUE_KINDS = ("go", "late", "info")
# a character's numbers a lesson can list for every character: its name in
# expressions, where it is in data/framedata/<id>.json
# a character's numbers a lesson can list for every character: its name in
# expressions, where it is in data/framedata/<id>.json, what it is called
CHARACTER_NUMBERS = {"jump_squat": ("J", ("attributes", "jump_startup_time"),
                                    "Jump squat")}
CAMERAS = ("normal", "stage")
# what a scenario may draw in the world for the player (src/host/didraw.c):
# "di", TM-CE's DI display, the launch predicted for the stick held
TRACES = ("di",)

TOP = {
    "id": str, "name": str, "part": str, "goal": str, "why": str,
    "tutorial": dict, "scenarios": list, "attempt": dict, "measures": dict,
    "checks": dict, "verdict": dict, "parts": list, "coach": dict,
}
OPTIONAL = {"characters": (str, list), "mistakes": list}
PLAYER_KEYS = ("x", "y", "air", "above", "ledge", "facing", "percent")
OPPONENT_KEYS = ("character", "x", "facing", "percent", "inputs", "every")
ATTEMPT_KEYS = ("start", "judge", "cancel", "limit", "timeout")


class DrillError(Exception):
    pass


# ---- the character's numbers, and expressions of them ---------------------------

def names(fd, char_name=""):
    """The numbers a drill may name, for one character (its frame data,
    melee_course.engine.FighterData): J its jump squat, LAND its normal
    landing lag, FA and SA the frames (from the jump's press, frame 1) on
    which a full jump and a short hop reach their top: the first frame
    falling (the rise lasts its speed over gravity, after the squat)."""
    import math
    out = {"J": fd.jump_squat, "LAND": fd.landing_lag,
           "FA": fd.jump_squat + math.ceil(fd.jump_v / fd.gravity) + 1,
           "SA": fd.jump_squat + math.ceil(fd.hop_v / fd.gravity) + 1,
           "char": char_name or fd.id}
    # measured in the game (measure.py): DASH (a dash's frames before a
    # held stick runs), SL (the frame a short hop lands), LD (the earliest
    # ledgedash air dodge that lands)
    out.update(measured().get(fd.id, {}))
    return out


_MEASURED = None


def pick(obj, key, cid):
    """A drill's inputs `obj[key]` (an example, a mistake's inputs) for
    character `cid`: its own from `obj[key + "_for"]` if it has some (Mr.
    Game & Watch's neutral air cannot be L-cancelled: his example uses
    another aerial)."""
    return obj.get(key + "_for", {}).get(cid, obj[key])


def measured():
    """data/drills/numbers.json: {character: {number: value}}."""
    global _MEASURED
    if _MEASURED is None:
        path = os.path.join(DIR, "numbers.json")
        _MEASURED = {}
        if os.path.exists(path):
            with open(path) as f:
                _MEASURED = json.load(f)
    return _MEASURED


_OPS = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Add, ast.Sub, ast.Mult,
        ast.FloorDiv, ast.USub, ast.UAdd, ast.Constant, ast.Name, ast.Load,
        ast.Call)
# functions an expression may call: "max(11, 29-LD)"
_FUNCS = {"max": max, "min": min}


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
        if isinstance(node, ast.Call) and not (
                isinstance(node.func, ast.Name) and node.func.id in _FUNCS
                and not node.keywords):
            raise DrillError("only max(...) and min(...) in %r" % x)
        if isinstance(node, ast.Name) and node.id in _FUNCS:
            continue
        if isinstance(node, ast.Name) and node.id not in nums:
            raise DrillError("unknown number %r in %r" % (node.id, x))
        if isinstance(node, ast.Name) and isinstance(nums[node.id], str):
            raise DrillError("not a number: %r in %r" % (node.id, x))
    names = {k: v for k, v in nums.items() if not isinstance(v, str)}
    names.update(_FUNCS)
    return eval(compile(tree, "<drill>", "eval"), {"__builtins__": {}},
                names)


def text(t, nums, **more):
    """A drill's words with their {expressions} filled in. An expression of
    a measure that never happened reads "none"."""
    have = dict(nums)
    have.update(more)

    def show(v):
        if isinstance(v, float):
            return str(int(v)) if v == int(v) else str(round(v, 2))
        return str(v)

    def fill(m):
        inner = m.group(1)
        if inner in have:
            return show(have[inner])
        try:
            return show(value(inner, have))
        except DrillError:
            if any(isinstance(have.get(n), str) for n in
                   re.findall(r"[A-Za-z_]\w*", inner)):
                return "none"
            raise
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

    test = {"J": 3, "LAND": 4, "FA": 20, "SA": 12, "DASH": 11, "SL": 26,
            "LD": 5, "NL": 22, "NFL": 18, "SHD": 12, "char": "Fox",
            "measure": "x", "frames": "2 frames", "f": 1}
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

    def state(v, where):
        need(v in STATES, where, "unknown state %r" % (v,))

    def event(e, where):
        if isinstance(e, list):
            need(len(e) > 0, where, "an empty list of events")
            for i, x in enumerate(e):
                event(x, "%s[%d]" % (where, i))
            return
        if isinstance(e, str):
            need(e in SIMPLE_EVENTS, where, "unknown event %r" % e)
            return
        if not need(isinstance(e, dict), where,
                    "an event: %s" % ", ".join(EVENTS)):
            return
        kinds = [k for k in EVENT_KINDS if k in e]
        if not need(len(kinds) == 1, where, "one of %s" %
                    ", ".join(EVENT_KINDS)):
            return
        k = kinds[0]
        v = e[k]
        if k in ("enters", "leaves"):
            state(v, where)
        elif k in ("pressed", "released"):
            need(v in BUTTONS, where, "unknown button %r" % (v,))
        elif k in ("stick", "cstick"):
            need(v in DIRECTIONS, where, "%s: one of %s" % (
                k, ", ".join(DIRECTIONS)))
        elif k == "is":
            need(v in SIMPLE_EVENTS, where, "is: one of %s" %
                 ", ".join(SIMPLE_EVENTS))
        else:
            num(v, where + ".frame")
        for m in ("from", "to"):
            if m in e:
                state(e[m], where + "." + m)
        if "after" in e:
            event(e["after"], where + ".after")
        extra = set(e) - {k} - set(EVENT_MODS)
        need(not extra, where, "unknown %s" % ", ".join(sorted(extra)))

    def inputs_for(obj, key, where):
        """`key + "_for"`: {character id: inputs}, a character's own."""
        own = obj.get(key + "_for")
        if own is None:
            return
        if need(isinstance(own, dict), where, "%s_for: {character: "
                "inputs}" % key):
            for cid, lst in own.items():
                need(os.path.exists(os.path.join(ROOT, "data", "framedata",
                                                 cid + ".json")), where,
                     "unknown character %r" % cid)
                inputs(lst, "%s.%s_for[%s]" % (where, key, cid))

    def marks(m, where):
        if need(isinstance(m, dict), where, "{frame: words} expected"):
            for f, w in m.items():
                num(f, "%s[%s]" % (where, f))
                words(w, "%s[%s]" % (where, f))

    def coach_block(co, where):
        """A coach's rows (button, stick or state; window, perfect) and
        note: the drill's, or a part's own."""
        for i, r in enumerate(co.get("rows", [])):
            w = "%s.rows[%d]" % (where, i)
            words(r.get("label"), w + ".label")
            kinds = [k for k in ("button", "stick", "cstick", "state")
                     if k in r]
            if need(len(kinds) == 1, w,
                    "one of button, stick, cstick, state"):
                k = kinds[0]
                if k == "button":
                    need(r["button"] in BUTTONS, w, "unknown button")
                elif k in ("stick", "cstick"):
                    need(r[k] in ("down", "up", "side"), w,
                         "%s: down, up or side" % k)
                else:
                    state(r["state"], w + ".state")
            for x in r.get("window", []) + r.get("strict_window", []):
                num(x, w + ".window")
            for x in r.get("perfect", []):
                num(x, w + ".perfect")
        words(co.get("note", ""), where + ".note")

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

    def cues(lst, where):
        if not need(isinstance(lst, list), where, "a list of cues"):
            return
        for i, cue in enumerate(lst):
            w = "%s[%d]" % (where, i)
            fr = cue.get("frames")
            if need(isinstance(fr, list) and len(fr) == 2, w,
                    "frames: [lo, hi]"):
                for x in fr:
                    num(x, w + ".frames")
            words(cue.get("words"), w + ".words")
            need(cue.get("kind", "info") in CUE_KINDS, w,
                 "kind: one of %s" % ", ".join(CUE_KINDS))

    def camera(cam, w):
        if isinstance(cam, dict):
            need(cam.get("follow") == "player" and
                 isinstance(cam.get("distance"), (int, float)) and
                 isinstance(cam.get("height", 10), (int, float)), w,
                 'camera: {"follow": "player", "distance": D, "height": H}')
        else:
            need(cam in CAMERAS, w, "camera: one of %s, or follow"
                 % ", ".join(CAMERAS))

    t = spec["tutorial"]
    if "camera" in t:
        camera(t["camera"], "tutorial")
    for k in ("what", "expect"):
        words(t.get(k), "tutorial.%s" % k)
    inputs(t.get("example"), "tutorial.example")
    inputs_for(t, "example", "tutorial")
    marks(t.get("marks", {}), "tutorial.marks")
    for i, le in enumerate(t.get("lessons", [])):
        w = "tutorial.lessons[%d]" % i
        words(le.get("title"), w + ".title")
        paras = le.get("text")
        for k, para in enumerate(paras if isinstance(paras, list)
                                 else [paras]):
            words(para, "%s.text[%d]" % (w, k))
        if "characters" in le:
            need(le["characters"] in CHARACTER_NUMBERS, w,
                 "characters: one of %s" % ", ".join(CHARACTER_NUMBERS))
        if "scenario" in le:
            need(isinstance(le["scenario"], int) and
                 0 <= le["scenario"] < len(spec["scenarios"]), w,
                 "scenario: an index of the drill's scenarios")
        show = le.get("show")
        if show is None:
            continue
        if not need(isinstance(show, dict) and len(show) == 1 and
                    ("example" in show or "still" in show), w,
                    'show: {"example": ...} or {"still": ...}'):
            continue
        if "example" in show:
            ex = show["example"]
            inputs(ex.get("inputs"), w + ".show.example.inputs")
            inputs_for(ex, "inputs", w + ".show.example")
            marks(ex.get("marks", {}), w + ".show.example.marks")
            cues(ex.get("cues", []), w + ".show.example.cues")
        else:
            st = show["still"]
            inputs(st.get("inputs"), w + ".show.still.inputs")
            inputs_for(st, "inputs", w + ".show.still")
            num(st.get("frame"), w + ".show.still.frame")
            if "cue" in st:
                words(st["cue"].get("words"), w + ".show.still.cue.words")
                need(st["cue"].get("kind", "info") in CUE_KINDS, w,
                     "cue kind: one of %s" % ", ".join(CUE_KINDS))

    for i, sc in enumerate(spec["scenarios"]):
        w = "scenarios[%d]" % i
        need(isinstance(sc.get("name"), str), w, "no name")
        pl = sc.get("player", {})
        if need(isinstance(pl, dict), w, "player: {...}"):
            if pl.get("ledge"):
                need(pl["ledge"] in ("left", "right", True), w,
                     "player.ledge: left or right")
            else:
                need("x" in pl, w, 'player: {"x": number}')
            for k in ("x", "y", "above", "percent"):
                if k in pl:
                    num(pl[k], "%s.player.%s" % (w, k))
            if "facing" in pl:
                need(pl["facing"] in ("left", "right"), w,
                     "player.facing: left or right")
            extra = set(pl) - set(PLAYER_KEYS)
            need(not extra, w, "player: unknown %s" % ", ".join(sorted(extra)))
        op = sc.get("opponent", "none")
        if isinstance(op, dict):
            need(isinstance(op.get("character"), str), w,
                 "opponent.character: a character id")
            need(isinstance(op.get("x"), (int, float)), w,
                 "opponent.x: a number")
            if "facing" in op:
                need(op["facing"] in ("player", "away"), w,
                     "opponent.facing: player or away")
            if "percent" in op:
                num(op["percent"], w + ".opponent.percent")
            if "inputs" in op:
                inputs(op["inputs"], w + ".opponent.inputs")
            if "every" in op:
                need(isinstance(op["every"], int) and op["every"] > 0, w,
                     "opponent.every: frames")
            extra = set(op) - set(OPPONENT_KEYS)
            need(not extra, w, "opponent: unknown %s" %
                 ", ".join(sorted(extra)))
        else:
            need(op in OPPONENTS, w, "opponent: none, or a character")
        camera(sc.get("camera", "normal"), w)
        if "lead" in sc:
            need(isinstance(sc["lead"], int) and sc["lead"] >= 0, w,
                 "lead: frames from 0")
        if "trace" in sc:
            need(sc["trace"] in TRACES, w, "trace: one of %s" %
                 ", ".join(TRACES))
        # one stage for the drill: a part's scenario is played on the
        # stage the drill's match loaded (scenarios[0]'s)
        need(sc.get("stage", "final-destination") == spec["scenarios"][0].get(
            "stage", "final-destination"), w,
             "stage: every scenario on the first one's stage")

    a = spec["attempt"]
    event(a.get("start"), "attempt.start")
    event(a.get("judge"), "attempt.judge")
    if "cancel" in a:
        event(a["cancel"], "attempt.cancel")
    if "limit" in a:
        need(isinstance(a["limit"], int) and a["limit"] > 0,
             "attempt.limit", "frames")
    if "timeout" in a:
        need(a["timeout"] in ("judge", "drop"), "attempt.timeout",
             "judge or drop")
    extra = set(a) - set(ATTEMPT_KEYS)
    need(not extra, "attempt", "unknown %s" % ", ".join(sorted(extra)))

    for name, m in spec["measures"].items():
        w = "measures[%r]" % name
        need(re.match(r"^[a-z_]+$", name) is not None, w,
             "a name of lower case letters and _")
        if m == "jump_kind":
            continue
        kinds = [k for k in MEASURES if isinstance(m, dict) and k in m]
        if not need(len(kinds) == 1, w, "unknown measure %r" % (m,)):
            continue
        k = kinds[0]
        if k == "held":
            need(m["held"] in BUTTONS, w, "unknown button %r" % m["held"])
        elif k in ("frames", "distance"):
            if need(isinstance(m[k], list) and len(m[k]) == 2, w,
                    "%s: [event, event]" % k):
                event(m[k][0], w + "[0]")
                event(m[k][1], w + "[1]")
            if k == "distance" and "axis" in m:
                need(m["axis"] in ("x", "y", "xy"), w, "axis: x, y or xy")
            if "last" in m:
                need(m["last"] is True and k == "frames", w,
                     'last: true (frames: from the last [0] before [1])')
        elif k in ("frame_of", "happened", "count", "max_gap"):
            event(m[k], w)
        elif k == "moved_while":
            need(m[k] in CONDITIONS, w, "moved_while: one of %s" %
                 ", ".join(CONDITIONS))
        elif k == "value":
            need(m["value"] in FIELDS, w, "value: one of %s" %
                 ", ".join(FIELDS))
            event(m.get("at", "end"), w + ".at")
        elif k == "frames_while":
            cond = m["frames_while"]
            if isinstance(cond, dict):
                need(set(cond) == {"in"}, w, 'frames_while: {"in": STATE}')
                state(cond.get("in"), w)
            else:
                need(cond in CONDITIONS, w, "frames_while: one of %s" %
                     ", ".join(CONDITIONS))
            event(m.get("from", "start"), w + ".from")
        elif k == "angle":
            need(m["angle"] in ("stick", "velocity"), w,
                 "angle: stick or velocity")
            if "from_horizontal" in m:
                need(m["from_horizontal"] is True, w,
                     "from_horizontal: true (either direction)")
            event(m.get("at", "end"), w + ".at")
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
        if "strict" in c:
            # the expectation when the player chose frame-perfect timing
            st = c["strict"]
            ks = [k for k in EXPECTS if isinstance(st, dict) and k in st]
            if need(len(ks) == 1, w + ".strict", "one of %s" %
                    ", ".join(EXPECTS)):
                if ks[0] == "within":
                    for x in st["within"]:
                        num(x, w + ".strict.within")
                elif ks[0] != "equals":
                    num(st[ks[0]], w + ".strict." + ks[0])
            for k in ("expect", "fix"):
                if k in st:
                    words(st[k], "%s.strict.%s" % (w, k))

    for i, p in enumerate(spec["parts"]):
        w = "parts[%d]" % i
        words(p.get("name"), w + ".name")
        words(p.get("teach"), w + ".teach")
        if "success" in p:
            words(p["success"], w + ".success")
        inputs(p.get("example"), w + ".example")
        inputs_for(p, "example", w)
        marks(p.get("marks", {}), w + ".marks")
        cues(p.get("cues", []), w + ".cues")
        for c in p.get("checks", []):
            need(c in spec["checks"], w, "no check %r" % c)
        need(isinstance(p.get("streak"), int) and p["streak"] >= 1, w,
             "streak: a whole number from 1")
        if "coach" in p:
            coach_block(p["coach"], w + ".coach")
        if "attempt" in p:
            pa = p["attempt"]
            for k in ("start", "judge", "cancel"):
                if k in pa:
                    event(pa[k], "%s.attempt.%s" % (w, k))
            extra = set(pa) - set(ATTEMPT_KEYS)
            need(not extra, w + ".attempt", "unknown %s" %
                 ", ".join(sorted(extra)))
        if "scenario" in p:
            # an index, or a list the player turns through (D-pad left and
            # right: the ledgedash from either ledge)
            sc = p["scenario"]
            lst = sc if isinstance(sc, list) else [sc]
            need(len(lst) > 0 and all(
                isinstance(i, int) and 0 <= i < len(spec["scenarios"])
                for i in lst), w,
                "scenario: an index of the drill's scenarios, or a list")

    for i, m in enumerate(spec.get("mistakes", [])):
        w = "mistakes[%d]" % i
        words(m.get("name"), w + ".name")
        inputs(m.get("inputs"), w + ".inputs")
        inputs_for(m, "inputs", w)
        need(m.get("fails") in spec["checks"], w, "fails: a check's name")

    coach_block(spec["coach"], "coach")
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


def every_character(number):
    """[(value, id, name)] of a character number (CHARACTER_NUMBERS) for
    every character in data/framedata, by value."""
    path = CHARACTER_NUMBERS[number][1]
    out = []
    d = os.path.join(ROOT, "data", "framedata")
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(d, f)) as fh:
            data = json.load(fh)
        v = data
        for k in path:
            v = v[k]
        out.append((int(v), f[:-5], data.get("name", f[:-5])))
    return sorted(out)


def ids():
    if not os.path.isdir(DIR):
        return []
    return sorted(f[:-5] for f in os.listdir(DIR) if f.endswith(".json"))
