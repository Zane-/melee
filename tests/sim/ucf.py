"""UCF 0.84 in C (src/melee/tm/ucf/) against the UCF that Slippi ships.

The same inputs are played three times from one saved match start:

    ours     the overlay as built: the C rules
    slippi   Slippi's eight UCF codes injected at their vanilla addresses,
             as its Dolphin does it; the C steps aside by itself
    vanilla  the C switched off, nothing injected

"ours" has to equal "slippi" on every frame, for both fighters. "vanilla"
has to differ somewhere, and the injected code is watched to count how often
each rule fired, or the inputs prove nothing.

Slippi's codes are read from a Slippi Launcher install (not kept in this
repository); without one the test says so and stops.

    OVERLAY_OUT=build/overlay-tmtest TM_TEST=1 python tools/overlay_build.py
    python tests/sim/ucf.py [--seeds N] [--frames N] [--stage NAME]

The default (5 seeds of 2,700 frames, three runs each) takes about seven
minutes. With fewer seeds the rare rules (tumble, the two SDI ones) may not
come up, which the test reports as a failure of the inputs, not of the code.
"""
import argparse
import math
import random
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, "tools/melee_sim")
import unicorn                        # noqa: E402
from sim import Sim                   # noqa: E402

INI = Path.home() / ".config/Slippi Launcher/netplay/Sys/GameSettings/GALE01r2.ini"
CODE_AT = 0x80001800                  # where a Gecko code handler lives

# address -> (rule, {offset in the code: what reaching it means})
SITES = {
    0x8006B460: ("pad buffer, cardinals", {0x60: "x snapped to 1.0",
                                            0x98: "y snapped to 1.0",
                                            0x26C: "drop counter running"}),
    0x800C9A44: ("dash back", {0xAC: "dash back"}),
    0x800D65EC: ("crouch turn", {0x74: "crouch line lowered"}),
    0x8008E54C: ("SDI", {0xD8: "SDI by flick"}),
    0x80093294: ("shield SDI", {0x90: "shield SDI by flick"}),
    0x800908F4: ("tumble", {0x08: "wiggle, second frame", 0x88: "wiggle by flick"}),
    0x800998A4: ("shield drop", {0xB0: "spot dodge held back"}),
    0x8009A0B8: ("shield drop, held", {0x3C: "drop from a held position"}),
}


def slippi_codes():
    """{address: code bytes} of the C2 codes at SITES, from Slippi's ini."""
    words, on = [], False
    for ln in INI.read_text(errors="replace").splitlines():
        if ln.startswith("$"):
            on = ln.startswith("$Required: General Codes")
            continue
        m = re.match(r"^([0-9A-Fa-f]{8}) ([0-9A-Fa-f]{8})", ln)
        if on and m:
            words.append((int(m[1], 16), int(m[2], 16)))
    out, i = {}, 0
    while i < len(words):
        a, b = words[i]
        kind, addr = a >> 24, 0x80000000 | (a & 0x01FFFFFF)
        if kind == 0xC2:
            data = b"".join(struct.pack(">II", *w) for w in words[i + 1:i + 1 + b])
            if addr in SITES:
                out[addr] = data
            i += 1 + b
        elif kind == 0x06:
            i += 1 + (b + 7) // 8
        else:
            i += 1
    return out


def inject(s, codes, counts):
    """Put each code where a Gecko handler would and branch to it from its
    site; the code's last word becomes the branch back."""
    m, at = s.m, CODE_AT
    for addr, data in sorted(codes.items()):
        back = (addr + 4 - (at + len(data) - 4)) & 0x03FFFFFC
        m.write(at, data[:-4] + struct.pack(">I", 0x48000000 | back))
        m.w32(addr, 0x48000000 | ((at - addr) & 0x03FFFFFC))
        m.uc.ctl_remove_cache(addr, addr + 4)
        for off, what in SITES[addr][1].items():
            def hit(uc, a, size, user, what=what):
                counts[what] = counts.get(what, 0) + 1
            m.uc.hook_add(unicorn.UC_HOOK_CODE, hit, begin=at + off, end=at + off)
        at += (len(data) + 7) & ~7


class Stick:
    """A raw control stick doing what hands do: holds, flicks, rolls along
    the rim, with the small errors real sticks have."""

    def __init__(self, rng):
        self.rng, self.x, self.y, self.todo = rng, 0, 0, []

    def point(self, kind):
        r = self.rng
        if kind == "centre":
            return r.randint(-6, 6), r.randint(-6, 6)
        if kind == "side":
            return r.choice((-1, 1)) * r.randint(60, 105), r.randint(-14, 14)
        if kind == "down":
            return r.randint(-14, 14), -r.randint(50, 105)
        if kind == "up":
            return r.randint(-14, 14), r.randint(50, 105)
        if kind == "tilt":
            a = r.uniform(0, 2 * math.pi)
            d = r.randint(18, 60)
            return int(d * math.cos(a)), int(d * math.sin(a))
        if kind == "notch":          # down and to a side, at the rim
            a = math.radians(r.choice((-1, 1)) * r.uniform(25, 65) - 90)
            d = r.randint(72, 100)
            return int(d * math.cos(a)), int(d * math.sin(a))
        raise ValueError(kind)

    def plan(self, kinds):
        r = self.rng
        tx, ty = self.point(r.choice(kinds))
        n = r.choice((1, 1, 1, 2, 2, 3, 5))        # frames to get there
        if r.random() < 0.25:                      # along the rim
            a0 = math.atan2(self.y, self.x)
            a1 = math.atan2(ty, tx)
            d = max(80, int(math.hypot(tx, ty)))
            for k in range(1, n + 1):
                a = a0 + (a1 - a0) * k / n
                self.todo.append((int(d * math.cos(a)), int(d * math.sin(a))))
        else:
            for k in range(1, n + 1):
                self.todo.append((self.x + (tx - self.x) * k // n,
                                  self.y + (ty - self.y) * k // n))
        self.todo += [(tx, ty)] * r.choice((0, 1, 2, 3, 6, 12, 25))

    def step(self, kinds):
        if not self.todo:
            self.plan(kinds)
        self.x, self.y = self.todo.pop(0)
        return (max(-127, min(127, self.x)), max(-127, min(127, self.y)))


WAIT, DAMAGE_FALL = 14, 38
# player 2's forward tilt and smash: the frame before each one lands
SWINGS = {53: 6, 60: 9}
FP_SELF_VEL, FP_KB_VEL, FP_CUR_POS, FP_GROUND_OR_AIR = 0x80, 0x8C, 0xB0, 0xE0
FP_FLOOR_SKIP, FP_PERCENT, FP_SHIELD = 0x72C, 0x1830, 0x1998
PLATFORM = (-38.0, 34.0)             # above Battlefield's left platform
ORDER = ("turns", "crouch", "platform", "hit", "shield", "sdi", "fuzz",
         "hit")
FUZZ = ("centre", "side", "side", "down", "tilt", "notch", "up")


def rim(angle_deg, radius):
    a = math.radians(angle_deg)
    return int(radius * math.cos(a)), int(radius * math.sin(a))


class Script:
    """Both pads for one run. Player 1 is the one under test; player 2
    walks up and hits it. One segment per rule, in turn (ORDER).

    Everything random is drawn per frame from the seed, never from the
    game, so the three runs get the same draws. What is read from the game
    (where the fighters are, their state) is the same in two runs for as
    long as the two runs are the same, which is what is being tested.
    Fighters that leave the stage are put back, the same way in each run.
    """

    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.stick = Stick(random.Random(seed * 7919 + 1))
        self.n, self.left, self.t, self.mode = seed, 0, 0, None
        self.p2_wait, self.sdi_at, self.sdi_step = 60, 0, 0
        self.c, self.plan, self.stood, self.n_hits = 0, None, False, 0

    # --- helpers -------------------------------------------------------------

    @staticmethod
    def airborne(s, f):
        return s.m.u32(f.fp + FP_GROUND_OR_AIR) == 1

    @staticmethod
    def put(s, f, x, y):
        m = s.m
        m.wf32(f.fp + FP_CUR_POS, x)
        m.wf32(f.fp + FP_CUR_POS + 4, y)
        for o in (0, 4, 8):
            m.wf32(f.fp + FP_SELF_VEL + o, 0.0)
            m.wf32(f.fp + FP_KB_VEL + o, 0.0)

    def rescue(self, s, f, x, y):
        if f.fp and self.airborne(s, f) and (abs(f.pos[0]) > 72 or f.pos[1] < -15):
            self.put(s, f, x, y)

    # --- player 1, by segment --------------------------------------------------

    def turns(self, s, a, d):
        """Standing still, then to a side through a halfway point: away from
        where the fighter faces is the dash back."""
        k = self.t % 36
        if k == 0:
            away = d[2] < 0.75
            self.plan = ((-1 if a.facing > 0 else 1) * (1 if away else -1),
                         28 + int(d[3] * 36), 78 + int(d[4] * 30),
                         0 if d[5] < 0.6 else 1 + int(d[5] * 5) % 2)
        side, half, full, gap = self.plan
        if abs(a.pos[0]) > 40 and k < 12:
            return (-50 if a.pos[0] > 0 else 50), 0, []     # walk back in
        if k < 14:
            return 0, 0, []
        if k <= 14 + gap:              # halfway for one frame, or longer
            return side * half, 0, []
        if k < 22 + gap:
            return side * full, int(d[1] * 10) - 5, []
        return 0, 0, []

    def crouch(self, s, a, d):
        """Crouching, then out to a side at the rim."""
        k = self.t % 44
        if k == 0:
            self.plan = rim(-(8 + d[2] * 50) if d[3] < 0.5
                            else -(172 - d[2] * 50), 80 + int(d[4] * 22))
        if abs(a.pos[0]) > 40 and k < 10:
            return (-50 if a.pos[0] > 0 else 50), 0, []
        if k < 30:
            return 0, -100, []
        if k < 36:
            return self.plan[0], self.plan[1], []
        return 0, -100, []

    def platform(self, s, a, d):
        """Shielding on a platform: the stick held to a side, then rolled or
        flicked down to a notch. Dropping through puts the fighter back."""
        buttons, x, y = [], 0, 0
        air = self.airborne(s, a)
        if air:
            # only a fighter that has stood on something since it was last
            # moved (one still dropping in at the start of a match lands on
            # nothing)
            if self.stood and (a.pos[1] < 24 or abs(a.pos[0] + 38) > 17):
                self.stood = False
                self.put(s, a, *PLATFORM)
                # a fighter that dropped through a platform keeps falling
                # through that one until told otherwise
                s.m.w32(a.fp + FP_FLOOR_SKIP, 0xFFFFFFFF)
            self.c = 0
            return 0, 0, []
        self.stood = True
        if a.pos[1] < 20:                      # on the floor: jump first
            self.c = 0
            return 0, 0, (["X"] if self.t % 30 < 3 else [])
        c, self.c = self.c, self.c + 1
        if c == 0:
            # side, frames held, angle below the horizon, frames to roll
            # there, radius, whether the stick starts from the centre
            self.plan = (1 if d[1] < 0.5 else -1, 6 + int(d[2] * 5),
                         18 + d[3] * 60, 1 + int(d[4] * 4),
                         76 + int(d[5] * 26), d[0] < 0.2)
            if 0.2 <= d[0] < 0.55:
                # the shallow notch, reached fast: too high for the game's
                # own drop, low enough for UCF's
                self.plan = (self.plan[0], self.plan[1], 36 + d[3] * 7,
                             1 + int(d[4] * 2), 82 + int(d[5] * 20), False)
        side, held, angle, n, radius, from_centre = self.plan
        if c >= 5:
            buttons.append("R")
        if c < held:
            x, y = (0, 0) if from_centre else (side * 95, 0)
        elif c < held + n and not from_centre:
            x, y = rim(-angle * (c - held + 1) / n, radius)
            x *= side
        elif c < held + n + 12:
            x, y = rim(-angle, radius)
            x *= side
        elif c < held + n + 20:
            buttons, x, y = [], 0, 0
        else:
            self.c = 0
        return x, y, buttons

    def flick(self, a, d, sideways):
        """The stick during hitlag: one of four ways of pushing it out,
        started on the first frame the hit holds the fighter."""
        if self.plan is None or self.plan[0] != "flick":
            self.plan = ("flick", d[2] * 360, 0,
                         (0, 1, 2, 3, 0, 1)[int(d[3] * (6 if sideways else 4))],
                         40 + int(d[4] * 20))
        _, angle, k, variant, half = self.plan
        self.plan = ("flick", angle, k + 1, variant, half)
        if sideways:
            angle = 180 if angle < 250 else 0
        r = ((95, 95, 0, 0, 95, 95, 0), (0, 95, 95, 0, 0, 95, 95),
             (0, half, 95, 95, 0, half, 95),
             (30, 30, 30, 95, 95, 0, 95))[variant][min(k, 6)]
        return rim(angle, r)

    def stay(self, s, a):
        """Stick to walk back to the middle, or get up; None if neither."""
        if a.hitstun > 0 or self.airborne(s, a):
            return None
        if 183 <= a.state <= 198:
            return 0, (100 if self.t % 8 == 0 else 0)
        if abs(a.pos[0]) > 35:
            return (-50 if a.pos[0] > 0 else 50), 0
        return None

    def hit(self, s, a, b, d):
        """Standing still and being hit, the stick flicked in hitlag. As the
        damage builds up the hits send the fighter tumbling."""
        if self.t == 0:
            s.m.wf32(a.fp + FP_PERCENT, 70.0)  # enough to be sent tumbling
        if a.hitlag > 0:
            x, y = self.flick(a, d, False)
            return x, y, []
        self.plan = None
        x, y = self.stay(s, a) or (0, 0)
        return x, y, []

    def shield(self, s, a, b, d):
        """Shielding the hits, the stick flicked sideways as they land."""
        if not 178 <= a.state <= 182:
            s.m.wf32(a.fp + FP_SHIELD, 60.0)   # a full shield each time
        if a.hitlag > 0:
            x, y = self.flick(a, d, True)
            return x, y, ["R"]
        self.plan = None
        back = self.stay(s, a)
        if back:
            return back[0], back[1], []
        # up only while player 2 swings, so it does not wear down and break
        return 0, 0, (["R"] if b.fp and 44 <= b.state <= 64 else [])

    def sdi(self, s, a, b, d):
        """SDI by flick needs the stick's timer used up by something else
        the frame before the hit: a tap jump, tried a frame or two either
        side of where player 2's smash lands."""
        if self.sdi_step == 2:                 # second frame of the tap jump
            self.sdi_step = 0
            return 0, 100, []
        if a.hitlag > 0:
            return 0, 100, []
        back = self.stay(s, a)
        if back:
            return back[0], back[1], []
        if b.fp and a.state == WAIT and self.sdi_step == 0 and \
                b.state in SWINGS and \
                b.state_frame == SWINGS[b.state] + (0, -1, 0, 1)[self.sdi_at % 4]:
            self.sdi_step = 2
            self.sdi_at += 1
            return 0, 54, []
        return 0, 0, []

    # --- a frame -----------------------------------------------------------------

    def frame(self, s, f):
        d = [self.rng.random() for _ in range(6)]
        a, b = s.fighter(0), s.fighter(1)
        if self.left <= 0:
            self.mode = ORDER[self.n % len(ORDER)]
            self.n += 1
            self.left, self.t, self.c, self.plan = 260 + int(d[1] * 80), 0, 0, None
            self.sdi_step = 0
        self.left -= 1
        fx, fy = self.stick.step(FUZZ)          # always drawn, used in "fuzz"
        x, y, buttons = 0, 0, []
        near = self.mode in ("hit", "shield", "sdi")
        if a.fp:
            self.rescue(s, a, -8.0, 60.0)       # high: time to tumble
            # in the segments about being hit, a fighter that was sent
            # somewhere and is done tumbling goes back to the middle
            if near and a.hitstun <= 0 and a.hitlag <= 0 and \
                    a.state != DAMAGE_FALL and \
                    (self.airborne(s, a) or 252 <= a.state <= 263) and \
                    (abs(a.pos[0]) > 25 or a.pos[1] > 12 or a.pos[1] < -9):
                # (a falling fighter's position dips under the floor for a
                # few frames before it lands)
                self.put(s, a, 0.0, 6.0)
                s.m.w32(a.fp + FP_FLOOR_SKIP, 0xFFFFFFFF)
            if a.state == DAMAGE_FALL and self.mode != "fuzz":
                # tumble: to a side in two frames, then back to the centre
                k = f % 9
                side = -1 if (f // 9) % 2 else 1
                x = side * (0, 44 + f % 20, 80 + f % 25, 90, 0, 0, 0, 0, 0)[k]
            elif self.mode == "turns":
                x, y, buttons = self.turns(s, a, d)
            elif self.mode == "crouch":
                x, y, buttons = self.crouch(s, a, d)
            elif self.mode == "platform":
                x, y, buttons = self.platform(s, a, d)
            elif self.mode == "hit":
                x, y, buttons = self.hit(s, a, b, d)
            elif self.mode == "shield":
                x, y, buttons = self.shield(s, a, b, d)
            elif self.mode == "sdi":
                x, y, buttons = self.sdi(s, a, b, d)
            else:
                x, y = fx, fy
                if d[2] < 0.3:
                    buttons.append("R")
                if d[3] < 0.03:
                    buttons.append("X")
        self.t += 1
        s.pad(0, buttons)
        s.h.pads[0]["lx"], s.h.pads[0]["ly"] = int(x), int(y)

        # player 2: stand next to player 1 and attack every so often
        b_buttons, bx, by = [], 0, 0
        if b.fp:
            self.rescue(s, b, 8.0, 22.0)
            if near and a.fp and self.airborne(s, b) and b.hitstun <= 0 and \
                    abs(a.pos[0] - b.pos[0]) > 20 and a.pos[1] < 5:
                self.put(s, b, a.pos[0] + (10 if a.pos[0] < 0 else -10), 3.0)
                s.m.w32(b.fp + FP_FLOOR_SKIP, 0xFFFFFFFF)
        if a.fp and b.fp and not self.airborne(s, b):
            dx = a.pos[0] - b.pos[0]
            self.p2_wait -= 1
            if b.pos[1] > 20 and a.pos[1] < 20:
                by = -100 if f % 8 < 2 else 0  # drop through the platform
            elif abs(dx) > 13:
                bx = 60 if dx > 0 else -60
            elif abs(dx) < 4 and self.mode == "hit":
                bx = -60 if dx > 0 else 60     # room for the up smash
            elif self.p2_wait <= 0 and self.mode not in ("turns", "crouch"):
                # a smash toward player 1; in "hit" every other one is an
                # up smash, which sends it up to tumble back down
                if self.mode == "hit" and self.n_hits % 2:
                    by = 100
                else:
                    bx = 100 if dx > 0 else -100
                self.n_hits += 1
                b_buttons = ["A"]
                self.p2_wait = 34 + int(d[4] * 30)
        s.pad(1, b_buttons)
        s.h.pads[1]["lx"], s.h.pads[1]["ly"] = bx, by


def snapshot(s):
    out = []
    for i in (0, 1):
        f = s.fighter(i)
        if not f.fp:
            out.append(None)
            continue
        out.append((f.state, f.state_frame, f.pos, f.vel, f.facing,
                    f.percent, f.hitlag, f.hitstun))
    return tuple(out)


def run(kind, seed, frames, stage, codes, counts):
    s = Sim.match("lab", "fox", "marth", stage=stage, free=True)
    m = s.m
    if kind == "slippi":
        inject(s, codes, counts)
    elif kind == "vanilla":
        m.w8(m.sym.addr("tm_ucf_off"), 1)
    active = s.call("tm_ucf_Active")
    script, trace = Script(seed), []
    for f in range(frames):
        script.frame(s, f)
        s.step()
        trace.append(snapshot(s))
    return trace, active


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--frames", type=int, default=2700)
    ap.add_argument("--stage", default="battlefield")
    args = ap.parse_args()
    if not INI.exists():
        sys.exit("no Slippi Launcher install (%s): nothing to compare with" % INI)
    codes = slippi_codes()
    if set(codes) != set(SITES):
        sys.exit("Slippi's codes are not where expected: found %s" %
                 sorted("%08X" % a for a in codes))

    ok, counts, differs = True, {}, 0
    for seed in range(1, args.seeds + 1):
        ours, on = run("ours", seed, args.frames, args.stage, codes, counts)
        theirs, off = run("slippi", seed, args.frames, args.stage, codes, counts)
        plain, _ = run("vanilla", seed, args.frames, args.stage, codes, counts)
        if not on or off:
            ok = False
            print("FAIL  seed %d: the C is %s as built and %s beside Slippi's" %
                  (seed, "on" if on else "OFF", "ON" if off else "off"))
        first = next((i for i in range(args.frames) if ours[i] != theirs[i]), None)
        vfirst = next((i for i in range(args.frames) if plain[i] != theirs[i]), None)
        differs += vfirst is not None
        if first is None:
            print("ok    seed %d: identical to Slippi's UCF for %d frames; the "
                  "vanilla game %s" % (seed, args.frames,
                                       "parts from it at frame %d" % vfirst
                                       if vfirst is not None else "never differs"))
        else:
            ok = False
            print("FAIL  seed %d: differs from Slippi's UCF at frame %d" % (seed, first))
            for who, t in (("ours  ", ours), ("slippi", theirs)):
                for i in range(max(0, first - 1), first + 1):
                    print("        %s f%d %s" % (who, i, t[i][0]))
    print("how often each rule fired in Slippi's code:")
    missing = []
    for addr, (rule, offs) in SITES.items():
        for what in offs.values():
            n = counts.get(what, 0)
            print("   %-28s %d" % (what, n))
            if n == 0:
                missing.append(what)
    if differs == 0:
        ok = False
        print("FAIL  the vanilla game never differed: these inputs test nothing")
    if missing:
        ok = False
        print("FAIL  never exercised: %s" % ", ".join(missing))
    print("PASS" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
