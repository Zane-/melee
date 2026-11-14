"""Course drills on the native build: the overlay's course engine, in Python.

The overlay build runs the character courses on an engine in C
(src/tmce/events/course/event.c, docs/ai/training-courses.md): an attempt
loop, placements, scripted CPU inputs, phases, a verdict with a measured
frame count, demonstrations played from a reference script. Each drill there
is a pair of callbacks, Setup and Think, against a small context. This is
the same engine for the native build (docs/ai/native-ai.md), driving the
game through tools/melee_native, so the drills can be ported callback for
callback (tools/melee_course/drills/). The C stays the reference: where this
file and event.c differ, event.c is right unless a comment here says why.

    from melee_course import engine, registry
    with Native() as n:
        s = engine.Session(registry.get("fox-shine-oos"), n, live=False)
        result = s.run()          # one attempt: {"success", "words", ...}

What a drill sees each frame (`Ctx`, the C engine's CourseCtx):

- `me`, `cpu`: the two fighters as they ended the last frame (native.Fighter
  views; `cpu` is None in a drill without an opponent). The C drills read
  `hd->state_id` part-way through the frame and `c->state` at its end; here
  there is only the end of the last frame, so a frame count that mixes the
  two can come out one off. The specs (tests/course/specs.py) say so.
- `state`, `prev_state`, `state_frames` (1 = entered in the last frame),
  `held`, `down` (the player's buttons in the last frame, PAD_* bits),
  `cpu_state`; `hmn_hit`, `cpu_hit` (damage went up in the last frame).
- `phase` (0 after every reset), `timer` (frames in the phase, 1 on its
  first think), `scenario`, `entry` (the deck's, or None), `side` (+1: the
  CPU starts on the player's right), `toward` (+1/-1: the player's
  direction seen from the CPU), `rng` (this attempt's; a demonstration's two
  passes draw the same numbers).

and what it can do: place the fighters, press the CPU's buttons for this
frame (`script`, `cpu_press`, `cpu_shield`), mark moments for the reference
script, and end the attempt (`result`, `retry`).
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for _p in (os.path.join(ROOT, "tools", "melee_native"),
           os.path.join(ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from native import Fighter  # noqa: E402

# ---- the controller's bits (dolphin/pad.h) -----------------------------------

DLEFT, DRIGHT, DDOWN, DUP = 0x1, 0x2, 0x4, 0x8
Z, R, L = 0x10, 0x20, 0x40
A, B, X, Y, START = 0x100, 0x200, 0x400, 0x800, 0x1000

# ---- action states (ftCo_MS_*, as the game numbers them) ---------------------

DEAD_LAST = 10            # every death state is at or below this
WAIT, WALK_SLOW, TURN, DASH, RUN, RUN_BRAKE = 14, 15, 18, 20, 21, 23
KNEEBEND, JUMP_F, JUMP_B, JUMP_AERIAL_F, JUMP_AERIAL_B = 24, 25, 26, 27, 28
FALL, FALL_AERIAL, FALL_SPECIAL, DAMAGE_FALL = 29, 32, 35, 38
SQUAT, SQUAT_WAIT, SQUAT_RV = 39, 40, 41
LANDING, LANDING_FALL_SPECIAL = 42, 43
ATTACK11, ATTACK_DASH = 44, 50
ATTACK_S3, ATTACK_HI3, ATTACK_LW3 = 51, 56, 57
ATTACK_S4, ATTACK_HI4, ATTACK_LW4 = 58, 63, 64
ATTACK_AIR_N, ATTACK_AIR_F, ATTACK_AIR_B = 65, 66, 67
ATTACK_AIR_HI, ATTACK_AIR_LW = 68, 69
LANDING_AIR_N, LANDING_AIR_LW = 70, 74
DAMAGE_FIRST, DAMAGE_LAST = 75, 91
GUARD_ON, GUARD, GUARD_OFF, GUARD_SET_OFF, GUARD_REFLECT = 178, 179, 180, 181, 182
DOWN_BOUND_U, DOWN_WAIT_U = 183, 184
DOWN_BOUND_D, DOWN_WAIT_D = 191, 192
PASSIVE, PASSIVE_STAND_F, PASSIVE_STAND_B = 199, 200, 201
PASSIVE_WALL, PASSIVE_WALL_JUMP, PASSIVE_CEIL = 202, 203, 204
ESCAPE_F, ESCAPE_B, ESCAPE, ESCAPE_AIR = 233, 234, 235, 236
CATCH, CATCH_PULL, CATCH_DASH, CATCH_DASH_PULL, CATCH_WAIT = 212, 213, 214, 215, 216
CATCH_ATTACK, CATCH_CUT = 217, 218
THROW_F, THROW_B, THROW_HI, THROW_LW = 219, 220, 221, 222
CAPTURE_PULLED_HI, CAPTURE_WAIT_HI = 223, 224
CAPTURE_PULLED_LW, CAPTURE_WAIT_LW = 226, 227
CAPTURE_CUT, CAPTURE_JUMP = 229, 230
THROWN_F, THROWN_B, THROWN_HI, THROWN_LW = 239, 240, 241, 242
CLIFF_CATCH, CLIFF_WAIT = 252, 253
REBIRTH, REBIRTH_WAIT = 12, 13

# Fox and Falco's specials (ftFox/forward.h, from 0x155).
FOX_BLASTER_FIRST, FOX_BLASTER_LAST = 0x155, 0x15A
FOX_ILLUSION_FIRST, FOX_ILLUSION_LAST = 0x15B, 0x160
FOX_FIREFOX_FIRST, FOX_FIREFOX_LAST = 0x161, 0x167
FOX_SHINE_FIRST, FOX_SHINE_LAST = 0x168, 0x171

# ---- inputs -------------------------------------------------------------------


class In:
    """One scripted pad state for the CPU (the C engine's CourseInput):
    held `hold` frames (0 = 1) from `frame` of the script. Stick and C-stick
    X are relative to the player: positive is toward them."""
    __slots__ = ("frame", "hold", "lx", "ly", "cx", "cy", "buttons")

    def __init__(self, frame, hold=1, lx=0, ly=0, cx=0, cy=0, buttons=0):
        self.frame, self.hold = frame, hold
        self.lx, self.ly, self.cx, self.cy = lx, ly, cx, cy
        self.buttons = buttons


class Ref:
    """One input of a reference script, the player's side (CourseRefInput):
    `frame` frames after mark `mark` (0 = the start of the attempt, after a
    lead of REF_LEAD neutral frames), plus `js` of the player's jump squats.
    Stick X positive is toward the opponent (or forward, without one)."""
    __slots__ = ("mark", "frame", "hold", "lx", "ly", "cx", "cy", "buttons",
                 "trigger", "js")

    def __init__(self, mark, frame, hold=1, lx=0, ly=0, cx=0, cy=0,
                 buttons=0, trigger=0, js=0):
        self.mark, self.frame, self.hold = mark, frame, hold
        self.lx, self.ly, self.cx, self.cy = lx, ly, cx, cy
        self.buttons, self.trigger, self.js = buttons, trigger, js


REF_LEAD = 3
MAX_MARKS = 8


def cpu_axis(v):
    """A CPU's stick value as the raw pad value that reads the same.

    The game reads a CPU's stick (`fp->cpu.lstick`, what the C drills
    script) as v / 127, v / 128 below zero (convertStickAxis, ftCo_0A01.c),
    and a person's raw pad as min(raw, 80) / 80 (HSD_PadClamp, scale_stick
    80, gmmain.c). Here the opponent is a pad, so a script's 80 (a tilt,
    0.63) has to become 50, not 80: a raw 80 is a full press, a smash, and
    UCF snaps it to exactly 1.0."""
    v = int(v)
    if v == 0:
        return 0
    return int(round(v * 80.0 / (127.0 if v > 0 else 128.0)))


def ref_axis(v):
    """A reference script's stick value as the raw pad value: what the C
    engine writes for the player (SetPlayerPad: `lx * 80 / 127`)."""
    return int(v * 80 / 127)

# ---- options --------------------------------------------------------------------


class Option:
    """A drill's option: `values` (labels) or `count` integers, the index of
    the default."""

    def __init__(self, name, values=None, default=0, desc="", count=None,
                 fmt="%d"):
        self.name, self.values, self.default = name, values, default
        self.desc, self.count, self.fmt = desc, count, fmt

    def size(self):
        return len(self.values) if self.values is not None else self.count

    def label(self, value):
        if self.values is not None:
            return self.values[value]
        return self.fmt % value


LENIENCY_FRAMES = (0, 1, 2, 4)


def leniency_option():
    return Option("Leniency", ["Frame Perfect", "1 Frame", "2 Frames",
                               "4 Frames"], 2,
                  "How many frames late still counts as a success.")


# Common options: the C engine's, by the same indexes (the specs set them so).
OPT_SCENARIO, OPT_SWITCH, OPT_SIDE, OPT_RESET_DELAY, OPT_DEMO = range(5)
OPT_COMMON_COUNT = 5
SWITCH_EVERY, SWITCH_ON_SUCCESS, SWITCH_MANUAL = range(3)
SIDE_RANDOM, SIDE_LEFT, SIDE_RIGHT = range(3)
DEMO_OFF, DEMO_ONCE, DEMO_ALWAYS = range(3)

# ---- a deck of opponents ------------------------------------------------------------


class Entry:
    """A scenario of a drill's deck: the CPU character (an id of
    tools/melee_native's CHARACTERS) and the drill's data for it."""

    def __init__(self, cpu, data=None, name=""):
        self.cpu, self.data, self.name = cpu, data, name


class Drill:
    """A drill: what the C engine has in CourseDrillInfo (desc.c) and
    CourseDrill (drills/*.inc.h). Subclasses override `setup` and `think`
    (and `guide`, `build_reference` when they have them)."""
    id = ""
    name = ""
    goal = ""
    part = "tech"                 # tech | neutral | punish | defense
    stage = "final-destination"
    cpu = "marth"                 # the opponent without a deck; None: none
    characters = None             # player characters it is for; None: any
    deck = None                   # [Entry, ...] or None
    options = ()                  # [Option, ...]
    help = ()                     # up to three lines
    reference = None              # [Ref, ...]
    flow = False                  # a verdict does not reset the situation
    live_marks = False            # the reference uses this attempt's marks

    def __init__(self):
        self.v = {}               # the drill's own state (the C drills' statics)

    def init(self):
        """Once, when the drill is opened."""

    def setup(self, c):
        """Place the fighters for an attempt."""

    def think(self, c):
        """Once a frame of the attempt."""

    def build_reference(self, c):
        return self.reference

    def guide(self, c):
        """Lines of the guide (the C engine shows up to eight)."""
        return [line for line in self.help if line]


# ---- per-character numbers ----------------------------------------------------------

_MOVES = {
    "jab1": "jab1", "dash_attack": "dash_attack", "ftilt": "ftilt",
    "utilt": "utilt", "dtilt": "dtilt", "fsmash": "fsmash",
    "usmash": "usmash", "dsmash": "dsmash", "nair": "nair", "fair": "fair",
    "bair": "bair", "uair": "uair", "dair": "dair", "grab": "grab",
    "dash_grab": "dash_grab", "spotdodge": "spotdodge",
    "roll_forward": "roll_forward", "roll_backward": "roll_backward",
    "airdodge": "airdodge", "tech_in_place": "tech_in_place",
    "tech_roll_forward": "tech_roll_forward",
    "tech_roll_backward": "tech_roll_backward",
    "ledge_getup": "ledge_getup", "ledge_roll": "ledge_roll",
}


class MoveData:
    """A move's frames (gen/framedata.inc.h's CourseMoveData)."""

    def __init__(self, m):
        from melee_data import calc
        m = m or {}
        self.hit = m.get("first_hit_frame") or 0
        self.faf = calc.faf(m) if m else 0
        self.total = m.get("total_frames", 0)
        self.land = m.get("landing_lag", 0) or 0
        self.land_l = m.get("landing_lag_lcancel", 0) or 0
        dmg = [b["damage"] for h in m.get("hits", []) for b in h["hitboxes"]]
        self.damage = min(max(dmg + [0]), 255)
        inv = m.get("intangible") or [[0, 0]]
        self.intang_from, self.intang_to = inv[0][0], inv[-1][1]


class FighterData:
    """A character's numbers (CourseFighterData), from data/framedata."""
    _cache = {}

    def __init__(self, cid):
        with open(os.path.join(ROOT, "data", "framedata", cid + ".json")) as f:
            d = json.load(f)
        a = d["attributes"]
        self.id = cid
        self.attr = a
        self.jump_squat = int(a["jump_startup_time"])
        self.landing_lag = int(a["normal_landing_lag"])
        self.weight = a["weight"]
        self.jump_v = float(a["jump_v_initial_velocity"])
        self.hop_v = float(a["hop_v_initial_velocity"])
        self.gravity = float(a["gravity"])
        self.fastfall_velocity = float(a["fast_fall_velocity"])
        self.terminal_velocity = float(a["terminal_velocity"])
        self.move = {k: MoveData(d["moves"].get(v)) for k, v in _MOVES.items()}

    @classmethod
    def of(cls, cid):
        if cid not in cls._cache:
            cls._cache[cid] = cls(cid)
        return cls._cache[cid]


# ---- the context a drill sees -------------------------------------------------------


class Ctx:
    def __init__(self, session):
        self.s = session
        self.n = session.n
        self.me = self.cpu = None
        self.phase = self.timer = 0
        self.scenario = 0
        self.entry = None
        self.side, self.toward = 1.0, -1.0
        self.hmn_hit = self.cpu_hit = False
        self.state = self.prev_state = -1
        self.state_frames = 0
        self.held = self.down = 0
        self.cpu_state = -1
        self.rng = random.Random(0)
        self._pad = None

    # ---- what the drill knows -------------------------------------------------

    @property
    def fd(self):
        """The player's character's numbers."""
        return self.s.fd

    @property
    def cfd(self):
        """The opponent's."""
        cpu = self.s.cpu_char
        return FighterData.of(cpu) if cpu else None

    def opt(self, i):
        """The value of the drill's option `i` (an index among its own
        options, as `Options_Main[OPT_COMMON_COUNT + i].val` in C)."""
        return self.s.opts[i]

    def leniency(self, i):
        return LENIENCY_FRAMES[self.s.opts[i]]

    @property
    def is_demo(self):
        return self.s.demo_pass != 0

    @property
    def demo_count(self):
        return self.s.demo_count

    def randi(self, n):
        """A number from 0 to n - 1 (HSD_Randi). The C drills draw from
        the game's random stream, these from Python's: the same choices
        come in other orders. A test can pin the first draws (`draws`)."""
        if self.s.draws:
            return self.s.draws.pop(0) % n if n > 0 else 0
        return self.rng.randrange(n) if n > 0 else 0

    # ---- placing ------------------------------------------------------------------

    def set_phase(self, phase):
        self.phase = phase
        self.timer = 0

    def place(self, hmn_x, cpu_x, cpu_faces_away=False, cpu_percent=0.0,
              hmn_percent=0.0):
        """Both on the main floor, the player facing the CPU; the CPU faces
        the player unless `cpu_faces_away` (course_Place)."""
        s = self.side
        self.n.place(self.s.person, hmn_x, 0.0, s, False, hmn_percent)
        if self.s.cpu_port is not None:
            self.n.place(self.s.cpu_port, cpu_x, 0.0,
                         s if cpu_faces_away else -s, False, cpu_percent)

    def place_solo(self, x, percent=0.0):
        """The player alone at x, facing right: a reference script's
        positive stick X is forward."""
        self.side, self.toward = 1.0, -1.0
        self.n.place(self.s.person, x, 0.0, 1, False, percent)
        self._park_cpu()

    def place_on_ledge(self, percent=0.0):
        """The player hanging on the stage's left ledge, fresh: positive
        stick X is toward the stage."""
        self.side, self.toward = 1.0, -1.0
        self.n.ledge(self.s.person, percent)

    def ledge_pos(self):
        """Where the stage's left ledge is, or None."""
        try:
            return self.n.ledge()
        except Exception:
            return None

    def place_in_air(self, port, x, y, facing, percent=0.0):
        """A fighter falling from (x, y) with its double jump."""
        self.n.place(port, x, y, facing, True, percent)

    def place_cpu(self, x, facing, percent=0.0):
        if self.s.cpu_port is not None:
            self.n.place(self.s.cpu_port, x, 0.0, facing, False, percent)

    def place_on_platform(self, x, above_y, facing=1.0, percent=0.0):
        """The player standing on what is straight below (x, above_y)."""
        self.side, self.toward = 1.0, -1.0
        self.n.place(self.s.person, x, above_y - 10.0, facing, False, percent)

    def _park_cpu(self):
        pass

    def fell(self):
        """The player died or is far below the stage."""
        return self.me.state <= DEAD_LAST or self.me.pos[1] < -70.0

    def set_shield(self, port, health):
        self.n.shield(port, health)

    # ---- the CPU's controller, this frame -----------------------------------------------

    def cpu_press(self, buttons=0, lx=None, ly=None, cx=None, cy=None,
                  trigger=None):
        """Add to what the CPU holds this frame (`cd->cpu.held |= ...`).
        Stick values as the C drills give the CPU's (`cd->cpu.lstickX`,
        -127..127, read as v / 127): converted to the pad's (cpu_axis).
        Absolute, not turned toward the player (script() does that)."""
        p = self._pad
        p["buttons"] |= buttons
        if lx is not None:
            p["lx"] = cpu_axis(lx)
        if ly is not None:
            p["ly"] = cpu_axis(ly)
        if cx is not None:
            p["cx"] = cpu_axis(cx)
        if cy is not None:
            p["cy"] = cpu_axis(cy)
        if trigger is not None:
            p["rt"] = max(p["rt"], int(trigger))

    def cpu_shield(self):
        """A target that shields (course_CpuShield): call every frame. The
        CPU holds full shield and the shield never shrinks."""
        self.cpu_press(R, trigger=255)
        if self.s.cpu_port is not None:
            self.n.shield(self.s.cpu_port, 60.0)

    def script(self, inputs, frame):
        """Apply the entries of a CPU script active on `frame`
        (course_Script); X is turned toward the player."""
        for i in inputs:
            hold = i.hold or 1
            if frame < i.frame or frame >= i.frame + hold:
                continue
            self.cpu_press(i.buttons, int(i.lx * self.toward), i.ly,
                           int(i.cx * self.toward), i.cy)

    # ---- the attempt ---------------------------------------------------------------------

    def mark(self, mark, back=0):
        """Announce a moment the reference script places inputs against.
        `back=1`: it happened during the last frame, not this one. The C
        drills look at the player part-way through a frame and see a change
        the animation makes (shieldstun ending, a jump squat ending) in the
        frame it happens; here the state is read between frames, so such a
        change is seen a frame later, and the moment is one frame back."""
        s = self.s
        if 0 < mark < MAX_MARKS and s.marks[mark] < 0:
            s.marks[mark] = s.attempt_frame - back
            if back and s.d.live_marks:
                # this frame's reference was played before the mark was
                # known: play it again after the think (an input one frame
                # after the mark is due now, as the C sends it)
                s.replay = True

    def measure(self, measured, target):
        self.s.measure = (measured, target)

    def report(self, key, value):
        self.s.report[key] = value

    def result(self, success, words):
        self.s.end(bool(success), words)

    def retry(self, words):
        self.s.end(None, words)

    def message(self, words):
        """A message that is not a verdict (the C engine's white ones)."""
        self.s.messages.append(words)


# ---- a drill being played -------------------------------------------------------------


class Session:
    """A game with one drill set up in it.

    `run()` plays one attempt and returns its result: {"success" (True,
    False), "words" (the verdict, first line), "skip" (a retry: the
    situation did not come about, nothing is counted), "measured",
    "target", "scenario", "report", "frames", "demo", "checks": []}.

    `person`: the player's port. `live`: their pad is a person's (the window
    build reads it); otherwise whatever drives the game sets it (a test, a
    demonstration). `options`: {index or name: value} for the drill's own
    options, `common`: {OPT_*: value} for the engine's. `on_load(fn)`: called
    around loading a match (the client turns its live input and pacing off
    for it); by default fn() is just called.
    """

    LIMIT = 3600                  # frames: an attempt that runs longer ends

    def __init__(self, drill, game, person=0, character="fox", options=None,
                 common=None, live=True, seed=1, on_load=None, dpad=True,
                 draws=None):
        self.d = drill
        self.n = game
        self.dpad = dpad          # the D-pad is the drill's (as in C)
        self.draws = list(draws or [])   # Ctx.randi's first answers
        self.replay = False
        self.person = person
        self.live = live
        self.char = character
        self.fd = FighterData.of(character)
        self.on_load = on_load or (lambda fn: fn())
        self.opts = [o.default for o in drill.options]
        for k, v in (options or {}).items():
            if isinstance(k, str):
                k = [o.name for o in drill.options].index(k)
            self.opts[k] = v
        self.common = {OPT_SCENARIO: 0, OPT_SWITCH: SWITCH_EVERY,
                       OPT_SIDE: SIDE_RANDOM, OPT_DEMO: DEMO_OFF}
        self.common.update(common or {})
        self.rng = random.Random(seed)
        self.seed = seed
        self.c = Ctx(self)
        self.cpu_char = None
        self.cpu_port = None
        self.scenario = -1
        self.last_success = False
        self.attempts = 0
        self.demo_pass = 0
        self.demo_count = 0
        self.flowing = False      # a flow drill carrying on from a verdict
        self.bag, self.bag_pos = [], 0
        self.player_pad = dict(buttons=0, lx=0, ly=0, cx=0, cy=0, lt=0, rt=0)
        self.prev_buttons = 0
        drill.init()
        first = drill.deck[0].cpu if drill.deck else drill.cpu
        self._load(first)

    def close(self):
        pass

    # ---- the match ----------------------------------------------------------------------

    def _load(self, cpu):
        if self.cpu_char == cpu and self.cpu_char is not None:
            return
        n = self.n

        def go():
            n.start(self.char, cpu, self.d.stage, self.seed)
        self.on_load(go)
        self.cpu_char = cpu
        self.cpu_port = None if cpu is None else 1 - self.person

    # ---- scenarios -------------------------------------------------------------------------

    def _next(self, previous):
        """The deck's rotation (tm_rot_Next): a shuffled bag, no repeat
        across a reshuffle."""
        count = len(self.d.deck)
        if self.bag_pos >= len(self.bag):
            self.bag = list(range(count))
            self.rng.shuffle(self.bag)
            self.bag_pos = 0
        if self.bag[self.bag_pos] == previous and len(self.bag) > 1:
            k = self.bag_pos + 1 if self.bag_pos + 1 < len(self.bag) else 0
            self.bag[self.bag_pos], self.bag[k] = \
                self.bag[k], self.bag[self.bag_pos]
        out = self.bag[self.bag_pos]
        self.bag_pos += 1
        return out

    def _pick(self):
        if not self.d.deck:
            return 0
        fixed = self.common[OPT_SCENARIO]
        if fixed > 0:
            return fixed - 1
        if self.scenario < 0:
            return self._next(-1)
        sw = self.common[OPT_SWITCH]
        if sw == SWITCH_ON_SUCCESS:
            return self._next(self.scenario) if self.last_success \
                else self.scenario
        if sw == SWITCH_MANUAL:
            return self.scenario
        return self._next(self.scenario)

    def scenario_names(self):
        return [e.name for e in self.d.deck] if self.d.deck else [self.d.name]

    def change_scenario(self, step):
        """D-pad left or right: another scenario, kept from then on."""
        if not self.d.deck:
            return
        self.scenario = (self.scenario + step) % len(self.d.deck)
        if self.common[OPT_SCENARIO] > 0:
            self.common[OPT_SCENARIO] = self.scenario + 1
        else:
            self.common[OPT_SWITCH] = SWITCH_MANUAL
        self.last_success = False
        self.flowing = False

    # ---- pads ---------------------------------------------------------------------------------

    def _set_pad(self, port, p):
        pads = self.n.h.pads[port]
        pads.update(buttons=p["buttons"], lx=p["lx"], ly=p["ly"], cx=p["cx"],
                    cy=p["cy"], lt=p.get("lt", 0), rt=p.get("rt", 0),
                    connected=True)
        self.n._dirty.add(port)

    def set_player_pad(self, buttons=0, lx=0, ly=0, cx=0, cy=0, trigger=0):
        """The player's pad, when it is not a person's (tests, demos)."""
        self.player_pad = dict(buttons=buttons, lx=lx, ly=ly, cx=cx, cy=cy,
                               lt=0, rt=trigger)
        self._set_pad(self.person, self.player_pad)

    def _play_reference(self, ref, marks):
        """A demonstration: the player's pad is the reference script
        (PlayReference)."""
        c = self.c
        lx = ly = cx = cy = buttons = trigger = 0
        if self.attempt_frame < REF_LEAD:
            self.set_player_pad()
            return
        js = self.fd.jump_squat
        for i in ref:
            hold = i.hold or 1
            if i.mark == 0:
                base = REF_LEAD
            elif self.d.live_marks:
                if self.marks[i.mark] < 0:
                    continue
                base = self.marks[i.mark]
            elif marks is not None and marks[i.mark] >= 0:
                base = marks[i.mark]
            else:
                continue
            t = self.attempt_frame - (base + i.frame + i.js * js)
            if t < 0 or t >= hold:
                continue
            if i.lx or i.ly:
                lx, ly = ref_axis(int(i.lx * -c.toward)), ref_axis(i.ly)
            if i.cx or i.cy:
                cx, cy = ref_axis(int(i.cx * -c.toward)), ref_axis(i.cy)
            buttons |= i.buttons
            trigger = max(trigger, i.trigger)
        self.set_player_pad(buttons, lx, ly, cx, cy, trigger)

    # ---- an attempt -----------------------------------------------------------------------------

    def _dpad(self, down):
        if not down & (DUP | DLEFT | DRIGHT | DDOWN):
            return None
        if self.demo_pass and down & (DLEFT | DRIGHT | DDOWN):
            self.common[OPT_DEMO] = DEMO_OFF
        if down & DUP and not self.demo_pass:
            return ("guide", "Guide")
        if down & (DLEFT | DRIGHT):
            self.change_scenario(1 if down & DRIGHT else -1)
            return ("scenario", self.scenario_names()[self.scenario]
                    if self.d.deck else "Reset")
        if down & DDOWN:
            self.last_success = False
            return ("reset", "Reset")
        return None

    def end(self, success, words):
        if self.verdict is None:
            self.verdict = (success, words)

    def _reset(self, attempt_seed, scenario=None):
        c, d = self.c, self.d
        idx = self._pick() if scenario is None else scenario
        self.scenario = idx
        c.scenario = idx
        c.entry = d.deck[idx] if d.deck else None
        self._load(c.entry.cpu if c.entry else d.cpu)
        c.rng = random.Random(attempt_seed)
        side = self.common[OPT_SIDE]
        if side == SIDE_RANDOM:
            side = SIDE_LEFT if c.randi(2) else SIDE_RIGHT
        c.side = -1.0 if side == SIDE_LEFT else 1.0
        c.toward = -c.side
        c.phase = c.timer = 0
        c.hmn_hit = c.cpu_hit = False
        c.state = c.prev_state = -1
        c.state_frames = 0
        c.held = c.down = 0
        c.cpu_state = -1
        self.n.pad(self.person)
        if self.cpu_port is not None:
            self.n.pad(self.cpu_port)
        self.n.seed(attempt_seed & 0xFFFFFFFF or 1)
        st = self.n.state()
        c.me = Fighter(st["p"][self.person])
        c.cpu = Fighter(st["p"][self.cpu_port]) \
            if self.cpu_port is not None and st["p"][self.cpu_port] else None
        c._pad = dict(buttons=0, lx=0, ly=0, cx=0, cy=0, lt=0, rt=0)
        d.setup(c)

    def run(self, jitter=0.0, run=0, each_frame=None, demo=None,
            scenario=None):
        """One attempt (a demonstration: its two passes, the second's
        result). `each_frame(game, frame)` is called before every frame
        (the client's way out, a test's player). `run` numbers the attempt:
        the same number draws the same random numbers."""
        d = self.d
        if demo is None:
            demo = self.common[OPT_DEMO] != DEMO_OFF
        seed = (self.seed * 1000003 + run * 7919) & 0x7FFFFFFF
        if scenario is None and getattr(self, "_forced", None) is not None:
            scenario, self._forced = self._forced, None
        if demo and (d.reference or type(d).build_reference is not
                     Drill.build_reference):
            self.demo_count += 1
            if self.common[OPT_DEMO] == DEMO_ONCE:
                self.common[OPT_DEMO] = DEMO_OFF
            self.flowing = False
            first = self._attempt(seed, each_frame, demo_pass=1,
                                  scenario=scenario)
            if first.get("ui"):
                return first
            if first.get("demo_marks") is None:
                first["demo"] = True
                return first
            out = self._attempt(seed, each_frame, demo_pass=2,
                                scenario=first["scenario_index"],
                                marks=first["demo_marks"])
            out["demo"] = True
            return out
        return self._attempt(seed, each_frame, scenario=scenario)

    def _attempt(self, seed, each_frame, demo_pass=0, scenario=None,
                 marks=None):
        c, d, n = self.c, self.d, self.n
        self.demo_pass = demo_pass
        self.verdict = None
        self.ui = None
        self.measure = None
        self.report = {}
        self.messages = []
        self.marks = [-1] * MAX_MARKS
        self.attempt_frame = 0
        ref = None
        if d.flow and self.flowing and not demo_pass:
            c.phase = c.timer = 0
        else:
            self._reset(seed, scenario)
            self.flowing = d.flow
            n.step()                  # the frame the placement takes
        if demo_pass:
            ref = d.build_reference(c) or []
            if demo_pass == 1 and (d.live_marks or
                                   all(i.mark == 0 for i in ref)):
                demo_pass = self.demo_pass = 2   # nothing to observe
        st = n.state()
        hmn_percent = st["p"][self.person]["percent"] \
            if st["p"][self.person] else 0.0
        cpu_percent = st["p"][self.cpu_port]["percent"] \
            if self.cpu_port is not None and st["p"][self.cpu_port] else 0.0
        frame = 0
        while True:
            st = n.state()
            mine = st["p"][self.person]
            theirs = st["p"][self.cpu_port] if self.cpu_port is not None \
                else None
            if mine is None:
                n.step()
                frame += 1
                if frame > 600:
                    self.end(None, "The fighter is gone")
                    break
                continue
            c.me = Fighter(mine)
            c.cpu = Fighter(theirs) if theirs else None
            # what the end of the last frame was (the C engine's Sample)
            if c.me.state != c.state:
                c.prev_state, c.state = c.state, c.me.state
                c.state_frames = 0
            c.state_frames += 1
            c.cpu_state = c.cpu.state if c.cpu else -1
            if self.live:
                held = n.pads()[self.person]["buttons"]
            else:
                held = self.player_pad["buttons"]
            c.down = held & ~self.prev_buttons
            c.held = held
            self.prev_buttons = held
            c.hmn_hit = c.me.percent > hmn_percent
            c.cpu_hit = bool(c.cpu) and c.cpu.percent > cpu_percent
            hmn_percent = c.me.percent
            cpu_percent = c.cpu.percent if c.cpu else 0.0
            if each_frame is not None:
                each_frame(n, frame)
            # The D-pad, as the C engine reads it (Event_Think): up opens
            # the guide, left and right change scenario, down resets; any
            # of them stops a demonstration. The attempt ends uncounted
            # and the caller does the rest ("ui" in the result).
            ui = self._dpad(c.down) if self.dpad else None
            if ui is not None:
                self.verdict = (None, ui[1])
                self.ui = ui
                break
            if demo_pass:
                self._play_reference(ref, marks)
            c.timer += 1
            c._pad = dict(buttons=0, lx=0, ly=0, cx=0, cy=0, lt=0, rt=0)
            self.replay = False
            d.think(c)
            if self.replay and demo_pass:
                self._play_reference(ref, marks)
            if self.cpu_port is not None:
                self._set_pad(self.cpu_port, c._pad)
            self.attempt_frame += 1
            if self.verdict is None and self.attempt_frame > self.LIMIT:
                self.end(None, "Nothing happened")
            if self.verdict is not None:
                break
            n.step()
            frame += 1
        if self.cpu_port is not None:
            n.pad(self.cpu_port)
        if not self.live:
            self.set_player_pad()
        success, words = self.verdict
        out = dict(success=bool(success), skip=success is None,
                   words=words.split("\n")[0], full_words=words,
                   measured=self.measure[0] if self.measure else None,
                   target=self.measure[1] if self.measure else None,
                   scenario=(d.deck[self.scenario].name if d.deck
                             else d.name),
                   scenario_index=self.scenario, report=dict(self.report),
                   frames=frame, demo=bool(demo_pass), checks=[],
                   messages=list(self.messages),
                   ui=self.ui[0] if self.ui else None)
        if self.ui:
            self.flowing = False
            if self.ui[0] == "scenario":
                # the change is kept: the next attempt plays it
                self._forced = self.scenario
            return out
        if demo_pass == 1:
            out["demo_marks"] = list(self.marks)
        elif success is not None and not demo_pass:
            self.attempts += 1
            self.last_success = bool(success)
        if d.flow and success is not None and not demo_pass:
            self.flowing = True
        elif not d.flow or success is None or demo_pass:
            self.flowing = False
        return out
