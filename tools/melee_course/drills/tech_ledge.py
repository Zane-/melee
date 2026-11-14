"""universal-ledgedash, fox-ledge-stall (start on the ledge) and
universal-shield-drop (start on a platform).

Port of src/tmce/events/course/drills/tech_ledge.inc.h (specs:
data/courses/fox.md, Tech 7, 11, 15). These reset after every verdict: the
start position is the drill.

The C drills read the ledge intangibility the game has left
(`hd->hurt.intang_frames.ledge`, the fighter's x1990), which the native
host does not report. `LedgeIntang` counts it the way the game does
(see there).
"""
from melee_course.engine import (
    A, B, L, R, X, Y, Drill, Entry, Option, Ref, Row, CLIFF_CATCH, CLIFF_WAIT, WAIT,
    KNEEBEND, JUMP_AERIAL_F, JUMP_AERIAL_B, LANDING, ESCAPE_F, ESCAPE_B,
    ESCAPE, ATTACK_AIR_N, ATTACK_AIR_LW, FOX_FIREFOX_FIRST, FOX_FIREFOX_LAST,
    STICK_SMASH)

LANDING_FALL_SPECIAL = 43
CLIFF_CLIMB_SLOW, CLIFF_JUMP_QUICK2 = 254, 263   # the ledge options
GUARD_ON, GUARD_OFF, GUARD_REFLECT = 178, 180, 182
PASS = 244                                        # dropping through a platform


def on_ledge(state):
    return state in (CLIFF_CATCH, CLIFF_WAIT)


def is_ledge_option(state):
    """Getting up, attacking, rolling or jumping from the ledge."""
    return CLIFF_CLIMB_SLOW <= state <= CLIFF_JUMP_QUICK2


def is_double_jump(state):
    return state in (JUMP_AERIAL_F, JUMP_AERIAL_B)


def is_aerial(state):
    return ATTACK_AIR_N <= state <= ATTACK_AIR_LW


# ---- the ledge intangibility ------------------------------------------------

# p_ftCommonData->x49C (PlCo.dat): the intangibility a ledge grab gives on
# entering CliffWait (ftCo_8009A804). Measured on the native build: after
# the host's `ledge` (which applies this + 1, as course_PlaceOnLedge does)
# the fighter is intangible to the end of the 30th frame and not the 31st.
CLIFF_INVULN = 30


class LedgeIntang:
    """The ledge intangibility frames left, as a C drill reads them
    (lg_Intangible: `hd->hurt.intang_frames.ledge`, part-way through the
    frame, after Fighter_procAnim).

    The game counts it down by one at the top of Fighter_procAnim, every
    frame, and a ledge grab sets it to at least CLIFF_INVULN when the
    catch animation ends and CliffWait begins (later in the same
    procAnim). A placement on the ledge sets CLIFF_INVULN + 1. Call
    `place()` with the placement and `frame(c)` once at the start of every
    think; `left` is then what the C drill's Think saw on the frame whose
    sample (c.state) this think has.

    Checked against the game's own flag (Fighter.invulnerable, which a
    LandingFallSpecial or a CliffWait does not set by script): after a
    placement `left` is the game's count at the end of the last frame (the
    C engine places after its frame's procAnim, the native one before a
    whole frame: the two offsets cancel), e.g. 8 at the end of the fast
    ledgedash, after which the flag stays on for 7 frames. After a
    re-grab the game has CLIFF_INVULN at the end of the frame CliffWait
    began, and the C Think that first samples CliffWait sees one less, as
    `left` does. `kind_game` (hurt.kind_game, the game-set hurtbox kind)
    is 2 while ledge intangibility lasts and 0 after (ftColl_8007B760,
    Fighter_procAnim)."""

    def __init__(self):
        self.left = 0

    def place(self):
        self.left = CLIFF_INVULN + 1

    def frame(self, c):
        if self.left > 0:
            self.left -= 1
        if c.state == CLIFF_WAIT and c.prev_state == CLIFF_CATCH and \
                c.state_frames == 1:
            # CliffWait began in the frame that just ended: the C Think
            # of that frame saw CLIFF_INVULN (still sampling CliffCatch),
            # this one one less.
            self.left = max(self.left, CLIFF_INVULN - 1)

    @property
    def kind_game(self):
        return 2 if self.left > 0 else 0


TIMEOUT = 200

# ---- universal-ledgedash ----------------------------------------------------

LD_HANG, LD_OFF, LD_LAND, LD_START = range(4)
LD_OPT_NEED, LD_OPT_START = range(2)
LD_NEEDS = (1, 5, 10, 15)
# Where an attempt starts (TM-CE's ledgedash event, "Starting Position").
# The owner (2026-11-13): "Ledgedash judging intangibility while spawning
# them on the platform is not fair. We need options for this tech drill
# like uncle punches ... where to spawn from (platform, air, ledge, etc.).
# A refresh shouldn't count as a failure either. That is the whole point!"
# Away from the ledge the player grabs it themselves, and may drop and
# regrab it (a refresh) before the ledgedash. Native only: the overlay's C
# drill starts on the ledge and counts a regrab as a failure.
LD_START_LEDGE, LD_START_FALLING, LD_START_STAGE, LD_START_PLATFORM, \
    LD_START_RANDOM = range(5)
LD_START_NAMES = ("Ledge", "Falling", "Stage", "Respawn platform", "Random")
LD_FALL_OUT, LD_FALL_ABOVE = 8.0, 20.0     # falling: from the ledge
LD_STAGE_IN = 12.0                         # stage: from the ledge
LD_PLATFORM_IN, LD_PLATFORM_ABOVE = 45.0, 30.0
LD_START_TIMEOUT = 900   # frames to reach the ledge before "not counted"

# Timings from a sweep in the simulator (2026-11-12): with Fox, jump 1 and
# air dodge 4 frames after the drop land in 15 frames.
LD_REF_DROP = 4      # script frame of the drop
LD_REF_JUMP = 1      # jump this many frames after the drop
LD_REF_DODGE = 4     # air dodge this many frames after the drop

LD_REFERENCE = [
    Ref(0, LD_REF_DROP, 1, -127, 0),
    Ref(0, LD_REF_DROP + LD_REF_JUMP, 1, 127, 0, buttons=X),
    Ref(0, LD_REF_DROP + LD_REF_DODGE, 2, 110, -65, buttons=R, trigger=140),
]


class TechLedgedash(Drill):
    id = "universal-ledgedash"
    name = "Ledgedash"
    goal = "Onto the stage from the ledge, still intangible"
    part = "tech"
    stage = "final-destination"
    cpu = None
    options = (
        Option("Intangible Frames", ["1", "5", "10", "15"], 0,
               "How many intangible frames you must still have when you "
               "can act on the stage."),
        Option("Start", list(LD_START_NAMES), LD_START_FALLING,
               "Where each try starts: on the ledge, falling to it, on "
               "the stage by it, or on a respawn platform. Grab the "
               "ledge yourself; drop and regrab to refresh."),
    )
    help = ("Ledgedash: let go of the ledge, double jump, and",
            "air dodge onto the stage.",
            "D-Pad up: guide. D-Pad down: reset.")

    def build_reference(self, c):
        # from the ledge only: the demonstration starts there
        return LD_REFERENCE

    def guide(self, c):
        return ["Hanging on the ledge you cannot be hit for a",
                "moment. A ledgedash carries that onto the",
                "stage: you act while still intangible.",
                "1. Let go: stick down or away from the stage.",
                "2. Double jump at once, toward the stage.",
                "3. Air dodge down and forward onto the stage.",
                "The verdict shows the intangible frames you",
                "had left when you could act."]

    def start(self, c):
        start = c.opt(LD_OPT_START)
        if c.is_demo:
            return LD_START_LEDGE
        if start == LD_START_RANDOM:
            return c.randi(LD_START_RANDOM)
        return start

    def status(self, c):
        name = LD_START_NAMES[self.v.get("start", self.start(c))]
        refresh = self.v.get("refreshes", 0)
        return "Start: %s%s" % (name.lower(), "; %d refresh%s" % (
            refresh, "" if refresh == 1 else "es") if refresh else "")

    def setup(self, c):
        self.lint = LedgeIntang()
        start = self.start(c)
        self.v = dict(frame=0, jumped=False, start=start, refreshes=0,
                      intang=[])
        ledge = c.ledge_pos() or (-85.6, 0.0)
        if start == LD_START_LEDGE:
            c.place_on_ledge()
            self.lint.place()
            c.set_phase(LD_HANG)
            return
        if start == LD_START_FALLING:
            c.place_in_air(c.s.person, ledge[0] - LD_FALL_OUT,
                           ledge[1] + LD_FALL_ABOVE, 1.0)
        elif start == LD_START_STAGE:
            c.n.place(c.s.person, ledge[0] + LD_STAGE_IN, ledge[1], -1, False)
        else:
            c.n.rebirth(c.s.person, ledge[0] + LD_PLATFORM_IN,
                        ledge[1] + LD_PLATFORM_ABOVE)
        c.side, c.toward = 1.0, -1.0
        c.set_phase(LD_START)

    def timeline(self, c):
        return ([Row("Jump", test=lambda e: e["down"] & (X | Y) or (
                     e["ly"] >= STICK_SMASH > e["ply"]),
                     perfect=(1 + LD_REF_JUMP,)),
                 Row("Dodge", buttons=L | R, trigger=True,
                     perfect=(1 + LD_REF_DODGE,)),
                 Row("Land", state=lambda st: st == LANDING_FALL_SPECIAL),
                 Row("Intang", frames=self.v.get("intang", ()))],
                "Frame 1: you let go. Intang: still intangible. The marks "
                "are the demonstration's (Fox).")

    def think(self, c):
        v = self.v
        self.lint.frame(c)
        need = LD_NEEDS[c.opt(LD_OPT_NEED)]
        if c.phase == LD_START:
            # on the way to the ledge: nothing counts yet
            if on_ledge(c.state):
                c.set_phase(LD_HANG)
            elif c.fell():
                c.retry("Fell before the ledge\nnot counted")
            elif c.timer > LD_START_TIMEOUT:
                c.retry("Not on the ledge yet\nnot counted")
            return
        if c.phase == LD_HANG:
            if on_ledge(c.state) or c.state < 0:
                return
            if is_ledge_option(c.state):
                c.result(False, "A ledge option, not a dash: "
                                "let go: stick down or away")
                return
            c.set_phase(LD_OFF)
            c.tl_begin()
            v["frame"] = 0
            v["jumped"] = False
            v["intang"] = []
            # fall through
        if c.phase in (LD_OFF, LD_LAND) and self.lint.left > 0:
            v["intang"].append(c.tl_frame())
        if c.phase == LD_OFF:
            v["frame"] += 1
            if is_double_jump(c.state):
                v["jumped"] = True
            if c.state == LANDING_FALL_SPECIAL:
                c.set_phase(LD_LAND)
            elif on_ledge(c.state):
                # a refresh: back on the ledge for its intangibility
                v["refreshes"] += 1
                c.set_phase(LD_HANG)
            elif c.state in (LANDING, WAIT):
                c.report("galint", self.lint.left)
                c.result(False, "Landed without the air dodge: "
                                "%d intangible frames left" % self.lint.left)
            elif c.fell() or v["frame"] > TIMEOUT:
                c.result(False, "Fell: air dodge sooner" if v["jumped"]
                         else "Fell: jump right after letting go")
        elif c.phase == LD_LAND:
            v["frame"] += 1
            if c.state == LANDING_FALL_SPECIAL:
                return
            left = self.lint.left
            c.measure(left, need)
            c.report("galint", left)
            c.report("total", v["frame"])
            refreshed = " after %d refresh%s" % (
                v["refreshes"], "" if v["refreshes"] == 1 else "es") \
                if v["refreshes"] else ""
            c.report("refreshes", v["refreshes"])
            if left >= need:
                c.result(True, "Ledgedash! %d intangible frames left, "
                               "%d in all%s" % (left, v["frame"], refreshed))
            elif left > 0:
                c.result(False, "Only %d intangible frames left, need %d"
                         % (left, need))
            else:
                c.result(False, "No intangibility left: %d frames: "
                                "be faster" % v["frame"])


# ---- fox-ledge-stall --------------------------------------------------------

LS_HANG, LS_OFF = range(2)
LS_OPT_COUNT = 0
LS_COUNTS = (1, 3, 5)

# Drop, up+B on the next frame; Fox is back on the ledge 30 frames after
# the drop and can let go again 8 frames later. Five cycles, for the
# largest "Stalls" setting (period found in the simulator, 2026-11-12).
LS_REF_DROP = 4
LS_REF_PERIOD = 39


def _ls_cycle(n):
    return [Ref(0, LS_REF_DROP + LS_REF_PERIOD * n, 1, -127, 0),
            Ref(0, LS_REF_DROP + LS_REF_PERIOD * n + 1, 1, 0, 127,
                buttons=B)]


class FoxLedgeStall(Drill):
    id = "fox-ledge-stall"
    name = "Fire Fox Ledge Stall"
    goal = "Drop and Fire Fox back to the ledge"
    part = "tech"
    stage = "final-destination"
    cpu = None
    characters = ("fox",)
    options = (
        Option("Stalls", ["1", "3", "5"], 0,
               "How many stalls in a row count as a success."),
    )
    help = ("Ledge stall: let go of the ledge and up+B at once",
            "to grab it again.",
            "D-Pad up: guide. D-Pad down: reset.")
    reference = sum((_ls_cycle(n) for n in range(5)), [])

    def guide(self, c):
        return ["Every ledge grab makes you intangible again.",
                "Drop and Fire Fox straight back to the ledge",
                "to stay there safely while the opponent waits.",
                "1. Let go: stick down or away from the stage.",
                "2. Up+B at once. Fox rises back to the ledge.",
                "Drop as soon as the grab allows to keep the",
                "time you can be hit short: the verdict shows it."]

    def setup(self, c):
        c.place_on_ledge()
        self.lint = LedgeIntang()
        self.lint.place()
        self.v = dict(stalls=0, frame=0, firefox=False, vulnerable=0, hang=0)

    def end(self, c, words):
        v = self.v
        want = LS_COUNTS[c.opt(LS_OPT_COUNT)]
        c.measure(v["stalls"], want)
        c.report("stalls", v["stalls"])
        c.report("vulnerable", v["vulnerable"])
        c.result(False, words)

    def think(self, c):
        v = self.v
        self.lint.frame(c)
        want = LS_COUNTS[c.opt(LS_OPT_COUNT)]
        at = (v["stalls"], want)
        if c.phase == LS_HANG:
            if on_ledge(c.state) or c.state < 0:
                v["hang"] += 1
                return
            if is_ledge_option(c.state):
                self.end(c, "A ledge option at %d of %d: "
                            "let go: stick down or away" % at)
                return
            c.set_phase(LS_OFF)
            v["frame"] = 0
            v["firefox"] = False
            # fall through
        if c.phase == LS_OFF:
            v["frame"] += 1
            if self.lint.left <= 0:
                v["vulnerable"] += 1
            if FOX_FIREFOX_FIRST <= c.state <= FOX_FIREFOX_LAST:
                v["firefox"] = True
            if on_ledge(c.state):
                if not v["firefox"]:
                    self.end(c, "Regrab without Fire Fox: at %d of %d" % at)
                    return
                v["stalls"] += 1
                if v["stalls"] >= want:
                    c.measure(v["stalls"], want)
                    c.report("stalls", v["stalls"])
                    c.report("vulnerable", v["vulnerable"])
                    c.report("hang", v["hang"])
                    c.result(True, "%d stalls: hittable for %d frames"
                             % (v["stalls"], v["vulnerable"]))
                else:
                    c.set_phase(LS_HANG)
                    v["hang"] = 0
            elif c.fell() or v["frame"] > TIMEOUT:
                self.end(c, "Missed the ledge at %d of %d" % at
                         if v["firefox"] else
                         "Fell at %d of %d: up+B right after the drop" % at)
            elif c.state in (WAIT, LANDING, LANDING_FALL_SPECIAL):
                self.end(c, "Landed on stage at %d of %d" % at)


# ---- universal-shield-drop --------------------------------------------------

# Battlefield's left platform.
SD_PLATFORM_X = -38.8
SD_PLATFORM_ABOVE = 40.0

# The owner (2026-11-13): "The drill should simply cycle the player between
# platforms and different scenarios (i.e. have them jump to a platform then
# shield drop, spawn them above the platform, etc.). We should also build
# in different stages for this". Native only. The platforms' middles and
# heights, found by dropping Fox onto each stage (2026-11-13; Fountain of
# Dreams' side platforms move, so a start there finds them wherever they
# are). A start puts the player above the middle and lets the game find the
# floor below.
SD_PLATFORMS = {
    "battlefield": {"left": (-38.8, 27.2), "top": (0.0, 54.4),
                    "right": (38.8, 27.2)},
    "yoshis-story": {"left": (-43.0, 23.5), "top": (0.0, 42.0),
                     "right": (43.0, 23.5)},
    "dream-land": {"left": (-46.0, 30.1), "top": (0.0, 51.4),
                   "right": (47.0, 30.2)},
    "fountain-of-dreams": {"left": (-35.0, 19.9), "top": (0.0, 42.8),
                           "right": (34.0, 16.2)},
}
SD_STAGES = tuple(SD_PLATFORMS)
SD_STANDING, SD_ABOVE, SD_BELOW = range(3)
SD_HOW = ("standing on it", "dropping onto it", "jumping up to it")
SD_DECK = [Entry(None, (side, how), "%s platform, %s" % (
    side.title(), SD_HOW[how]))
    for how in range(3) for side in ("left", "top", "right")]
SD_FROM_ABOVE = 25.0     # dropping onto it: this far above it
# Frames after the drop in which an aerial is credited to it.
SD_AERIAL_WINDOW = 20
SD_TL_DROP = 9           # the drop's frame on the timeline

SD_WAIT, SD_SHIELD, SD_DROP = range(3)


def is_shield(state):
    return GUARD_ON <= state <= GUARD_REFLECT and state != GUARD_OFF


class TechShieldDrop(Drill):
    id = "universal-shield-drop"
    name = "Shield Drop"
    goal = "Fall through a platform straight out of shield"
    part = "tech"
    stage = "battlefield"
    stages = SD_STAGES
    deck = SD_DECK
    cpu = None
    help = ("Shield drop: in shield, stick fully sideways, then",
            "down to the diagonal notch. Attack as you fall.",
            "D-Pad up: guide. D-Pad down: reset.")
    # The Axe method: shield, ease the stick to full right (a fast push is
    # a roll), then down to the diagonal notch, then an aerial. Swept in
    # the simulator with the stick at X 90. With UCF (2026-11-13; always
    # on, docs/ai/ucf.md): Y -80 to about -119 (of 127) drops, and only a
    # stick pushed past the -0.8 line (-127) is a spot dodge.
    reference = [
        Ref(0, 10, 600, buttons=R, trigger=140),
        Ref(0, 20, 10, 50, 0),
        Ref(0, 30, 10, 127, 0),
        Ref(0, 40, 6, 90, -86),
        Ref(0, 43, 1, buttons=A),
    ]

    def guide(self, c):
        return ["Fall through a platform straight out of",
                "shield, and attack whoever is below.",
                "The Axe method:",
                "1. In shield, ease the stick fully left or",
                "   right. A fast push is a roll.",
                "2. Roll it down along the rim to the diagonal",
                "   notch. You drop. Further down is a spot dodge.",
                "3. Attack as you fall."]

    def setup(self, c):
        side, how = c.entry.data if c.entry else ("left", SD_STANDING)
        if c.is_demo:
            how = SD_STANDING      # the demonstration starts standing
        plats = SD_PLATFORMS.get(self.stage, SD_PLATFORMS["battlefield"])
        x, y = plats[side]
        if side == "left" and self.stage == "battlefield":
            x = SD_PLATFORM_X      # where the C drill stands
        facing = 1.0 if x <= 0 else -1.0       # toward the middle
        if how == SD_STANDING:
            # above the platform's highest place; the floor below it
            c.place_on_platform(x, y + 10.0 if side == "top" else 40.0,
                                facing)
        elif how == SD_ABOVE:
            c.place_in_air(c.s.person, x, y + SD_FROM_ABOVE, facing)
        else:
            c.n.place(c.s.person, x, 0.0, facing, False)
        c.side, c.toward = facing, -facing
        self.v = dict(frame=0)

    def timeline(self, c):
        return ([Row("Shield", test=lambda e: e["held"] & (L | R) or
                     e["trig"]),
                 Row("Drop", state=lambda st: st == PASS,
                     perfect=(SD_TL_DROP,)),
                 Row("Aerial", state=is_aerial, perfect=(SD_TL_DROP + 1,))],
                "Frame %d: you drop through. An aerial on frame %d is the "
                "soonest." % (SD_TL_DROP, SD_TL_DROP + 1))

    def think(self, c):
        v = self.v
        if c.phase == SD_WAIT:
            if is_shield(c.state):
                c.set_phase(SD_SHIELD)
            elif c.state == PASS and c.state_frames == 1:
                c.result(False, "Dropped without the shield: shield first")
        elif c.phase == SD_SHIELD:
            if is_shield(c.state):
                return
            if c.state == PASS:
                c.set_phase(SD_DROP)
                c.tl_begin(back=SD_TL_DROP - 1)
                v["frame"] = 0
            elif c.state == ESCAPE:
                c.result(False, "Spot dodge: stop at the diagonal notch")
            elif c.state in (ESCAPE_F, ESCAPE_B):
                c.result(False, "Roll: move the stick sideways slower")
            elif c.state == KNEEBEND:
                c.result(False, "Jumped out of shield")
            else:
                c.set_phase(SD_WAIT)        # let go of the shield
        elif c.phase == SD_DROP:
            v["frame"] += 1
            if is_aerial(c.state):
                c.measure(v["frame"], 1)
                c.report("aerial", v["frame"])
                c.result(True, "Shield drop! aerial %d frames after"
                         % v["frame"])
            elif v["frame"] > SD_AERIAL_WINDOW:
                c.report("aerial", 0)
                c.result(True, "Shield drop! now add an aerial")


DRILLS = [TechLedgedash, FoxLedgeStall, TechShieldDrop]
