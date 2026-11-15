"""Every item of the game's Item Switch on the native build, headless:
spawned, picked up, used, thrown; the containers opened; every Pokemon out
of a Poke Ball.

    python tests/native/items.py [--no-draw | --window] [--only NAME ...]

The owner, 2026-11-14: items in Versus "just like the original game". Each
item is put into a match through the game's own spawn path (the host's
`item`, src/host/items.c: the developers' item menu) by Fox on Final
Destination, with Marth standing by to be hit, the match's random items
off. With every item at once on Pokemon Stadium the game had stopped on
"item dynamics hit num over!", and the Bunny Hood, the Fire Flower and the
Party Ball crashed it when they came; a Poke Ball's Pokemon did not move,
and Chikorita's leaves stood in the air. This proves the game now plays
each of them:

- bare: every one of the 31 items and the four containers comes and lands
  (the Starman bounces);
- picked up with A: the weapons, shooters and throwing items are held; the
  Bunny Hood is worn, the Metal Box makes Fox metal, the Cloaking Device
  hides him; the Heart Container, the Maxim Tomato and the food heal him;
  the Hammer, the Warp Star and the Screw Attack do what they do;
- used: the battering items swing (A) and smash (forward and A), hitting
  Marth; the shooters fire (the Ray Gun, the Super Scope, the Fire Flower
  shoot their projectiles), the Star Rod and the Lip's Stick fire theirs;
  the Parasol opens in the air; a jump with the Screw Attack is a screw
  attack; the mushrooms and the Starman change Fox when they reach him;
- thrown: everything held leaves Fox's hand with Z (the throwing items
  with A); a Bob-omb, a shell, Mr. Saturn hit Marth; the Barrel Cannon
  takes Marth in; the Motion-Sensor Bomb goes off under him; the Party
  Ball opens; the containers break, and what they hold comes out;
- every one of the 30 Pokemon comes out of a thrown Poke Ball, does its
  part (the ten with projectiles of their own make them) and leaves;
- the match the game stopped in, every item at very high on Pokemon
  Stadium, plays a minute, a CPU Marth picking items up.

The draw pass runs too (the game's render callbacks into the no-op
graphics; --no-draw leaves it out); --window plays the bare items, the
Pokemon and the minute in the window build, drawn (on a virtual display,
by the software renderer), as the client's Versus is (the rest needs
snapshots, which the window build does not take). Every wait has a frame budget and fails saying what it
waited for.
"""
import argparse
import os
import sys
import time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))

import native  # noqa: E402

ALL = (1 << 64) - 1
FOX, MARTH = 0, 1
HEAVY = {0x01, 0x02, 0x04, 0x05}     # crate, barrel, Party Ball, cannon

# Fighter motion states (ftCommon's motion ids)
WAIT = 14
LIGHT_GET, HEAVY_GET = 92, 93
LIGHT_THROW_F, HEAVY_THROW_F = 94, 104
THROWS = range(94, 120)               # LightThrowF to HeavyThrowLw4
PARASOL_OPEN = 144
SHOOT = {0x10: (148, 149), 0x19: (152, 153),
         0x15: tuple(range(158, 174))}
SCREW = (154, 155)
BARREL = (293, 340)
WARP_STAR = (305, 306)
HAMMER = tuple(range(307, 314))
GROW, SHRINK = (314, 315), (318, 319)
# (swing with A, forward smash), and what a smash fires
SWING = {0x0C: (120, 122, None), 0x0B: (124, 126, None),
         0x0D: (128, 130, None), 0x18: (132, 134, None),
         0x16: (136, 138, 0x24), 0x17: (140, 142, 0x25)}
SHOT = {0x10: 0x23, 0x15: 0x26, 0x19: 0x27}   # what each shooter fires
THROWN = {0x06: "Bob-omb", 0x07: "Mr. Saturn", 0x0E: "Green Shell",
          0x0F: "Red Shell", 0x11: "Freezie", 0x14: "Flipper"}
CONTAINERS = {0x00: "Capsule", 0x01: "Crate", 0x02: "Barrel", 0x03: "Egg"}
ITEMS = {
    0x04: "Party Ball", 0x05: "Barrel Cannon", 0x06: "Bob-omb",
    0x07: "Mr. Saturn", 0x08: "Heart Container", 0x09: "Maxim Tomato",
    0x0A: "Starman", 0x0B: "Home-Run Bat", 0x0C: "Beam Sword",
    0x0D: "Parasol", 0x0E: "Green Shell", 0x0F: "Red Shell",
    0x10: "Ray Gun", 0x11: "Freezie", 0x12: "Food",
    0x13: "Motion-Sensor Bomb", 0x14: "Flipper", 0x15: "Super Scope",
    0x16: "Star Rod", 0x17: "Lip's Stick", 0x18: "Fan",
    0x19: "Fire Flower", 0x1A: "Super Mushroom", 0x1B: "Poison Mushroom",
    0x1C: "Hammer", 0x1D: "Warp Star", 0x1E: "Screw Attack",
    0x1F: "Bunny Hood", 0x20: "Metal Box", 0x21: "Cloaking Device",
    0x22: "Poke Ball"}
POKEMON = ["Goldeen", "Chikorita", "Snorlax", "Blastoise", "Weezing",
           "Charizard", "Moltres", "Zapdos", "Articuno", "Wobbuffet",
           "Scizor", "Unown", "Entei", "Raikou", "Suicune", "Bellossom",
           "Electrode", "Lugia", "Ho-Oh", "Ditto", "Clefairy", "Togepi",
           "Mew", "Celebi", "Staryu", "Chansey", "Porygon2", "Cyndaquil",
           "Marill", "Venusaur"]
POKEMON_START = 0xA1
# what the Pokemon with projectiles of their own make (ItemKind)
POKEMON_MAKE = {0xA2: {0xBF}, 0xA4: {0xC0}, 0xA5: {0xC1, 0xC2},
                0xA6: {0xC3, 0xC4, 0xC5, 0xC6}, 0xAC: {0xC7},
                0xB2: {0xC8, 0xC9, 0xCA}, 0xB3: {0xCB}, 0xB9: {0xCC},
                0xBA: {0xCD}, 0xBC: {0xCE}}

checks = []


class Failed(Exception):
    pass


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""), flush=True)


class Lab:
    """A match with items whose random items are off: Fox and Marth on
    Final Destination, kept as a snapshot each check starts from."""

    def __init__(self, exe, draw, window=False):
        self.exe, self.draw, self.window = exe, draw, window
        self.boot()

    def boot(self):
        if self.window:
            from window import Window
            self.n = Window()
        else:
            self.n = native.Native(exe=self.exe, draw=self.draw)
        self.n.start("fox", "marth", "final-destination", seed=3,
                     rules=dict(items=4, mask=ALL))
        self.n.item("spawns", 0)
        for it in self.n.item("list"):      # what came before they stopped
            self.n.item("remove", it["id"])
        self.n.step(2)
        # the window build's game is not forked (its graphics would not
        # come along): there each check starts from the match as it is
        self.base = None if self.window else self.n.snapshot()

    def close(self):
        self.n.close()

    def fresh(self, fox=-30.0, marth=-16.0, percent=0.0, seed=None):
        n = self.n
        if self.base is not None:
            n.restore(self.base)
        else:
            for it in self.items():
                if it["holder"] < 0:
                    n.item("remove", it["id"])
        n.item("pokemon", 0)
        if seed is not None:
            n.seed(seed)
        n.place(FOX, fox, 0, facing=1, percent=percent)
        n.place(MARTH, marth, 0, facing=-1)
        n.step(2)

    # ---- reading ----------------------------------------------------------

    def items(self, kind=None):
        return [i for i in self.n.item("list")
                if kind is None or i["kind"] == kind]

    def fox(self):
        return self.n.item("fighter", FOX)

    def marth_percent(self):
        return self.n.fighter(MARTH).percent

    # ---- waiting and pressing --------------------------------------------

    def until(self, cond, frames, what):
        """Frames until cond() holds; fails after `frames`."""
        for f in range(frames):
            self.n.step()
            if cond():
                return f + 1
        raise Failed("waited %d frames for %s" % (frames, what))

    def press(self, buttons=(), stick=(0, 0), frames=2):
        """Held at least two frames: one pressed and let go inside a
        frame is not seen."""
        self.n.pad(FOX, buttons=buttons, stick=stick)
        self.n.step(frames)
        self.n.pad(FOX)

    def spawn(self, kind, x, y=12.0):
        return self.n.item(kind, float(x), float(y))

    def landed(self, kind, frames=150):
        self.until(lambda: any(not i["air"] for i in self.items(kind)),
                   frames, "item 0x%02x to land" % kind)

    def pick_up(self, kind):
        """Spawned at Fox's feet, landed, picked up with A: held."""
        fx = self.fox()["x"]
        self.spawn(kind, fx + 6)
        self.landed(kind)
        self.press(["A"])
        self.until(lambda: self.fox()["held"] == kind,
                   120 if kind in HEAVY else 60,
                   "Fox to hold item 0x%02x" % kind)
        self.until(lambda: self.fox()["motion"] not in (LIGHT_GET, HEAVY_GET),
                   90, "the pick-up to end")

    def motions_while(self, frames, until=None):
        """Fox's motion states over the next frames, and the item kinds
        there were."""
        motions, kinds = [], set()
        for _ in range(frames):
            self.n.step()
            m = self.fox()["motion"]
            if not motions or motions[-1] != m:
                motions.append(m)
            kinds |= {i["kind"] for i in self.items()}
            if until is not None and until():
                break
        return motions, kinds

    def throw_z(self, kind):
        """Z, once Fox is done with what he was doing: a throw, the item
        out of his hand and his (or gone at once: a thrown Screw Attack
        breaks)."""
        self.until(lambda: self.fox()["motion"] == WAIT, 150,
                   "Fox to stand before Z")
        self.press(["Z"])
        motions, _ = self.motions_while(
            40, until=lambda: self.fox()["held"] != kind)
        if self.fox()["held"] == kind:
            raise Failed("Z: still held, motions %s" % motions)
        if not set(motions) & set(THROWS):
            raise Failed("Z: no throw, motions %s" % motions)
        its = self.items(kind)
        if its and (its[0]["holder"] != -1 or its[0]["owner"] != FOX):
            raise Failed("after Z: %s" % its)
        return its[0] if its else None


# ---- the checks ----------------------------------------------------------

def bare(lab, kind, name):
    lab.fresh(fox=-60.0, marth=40.0)
    lab.spawn(kind, -24.0, 20.0)
    if not lab.items(kind):
        raise Failed("no item after the spawn")
    if kind == 0x0A:      # the Starman bounces: it is there a while
        lab.n.step(120)
        return "it bounces, %d frame(s)" % 120
    f = lab.until(lambda: any(not i["air"] for i in lab.items(kind)), 150,
                  "it to land")
    lab.n.step(120)
    return "landed in %d frames" % f


def swing(lab, kind, name):
    one, four, fires = SWING[kind]
    lab.fresh()
    lab.pick_up(kind)
    lab.n.place(MARTH, lab.fox()["x"] + 14, 0, facing=-1)
    before = lab.marth_percent()
    lab.press(["A"])
    m1, _ = lab.motions_while(50)
    hit1 = lab.marth_percent() - before
    lab.until(lambda: lab.fox()["motion"] == WAIT, 120, "the swing to end")
    # a smash that fires: Marth further off, where its shot gets to him
    lab.n.place(MARTH, lab.fox()["x"] + (50 if fires else 14), 0,
                facing=-1)
    lab.n.step(4)
    before = lab.marth_percent()
    lab.press(["A"], stick=(1, 0))
    m4, kinds = lab.motions_while(90)
    hit4 = lab.marth_percent() - before
    if one not in m1 or four not in m4:
        raise Failed("motions %s, then %s" % (m1, m4))
    if hit1 <= 0 or hit4 <= 0:
        raise Failed("Marth took %.0f%% and %.0f%%" % (hit1, hit4))
    if fires is not None and fires not in kinds:
        raise Failed("its smash fired nothing: %s" % sorted(kinds))
    lab.throw_z(kind)
    return "swing %.0f%%, smash %.0f%%%s, thrown with Z" % (
        hit1, hit4, ", fired 0x%02x" % fires if fires else "")


def shoot(lab, kind, name):
    lab.fresh(marth=10.0)
    lab.pick_up(kind)
    before = lab.marth_percent()
    seen, motions = set(), []
    for _ in range(3):
        if kind == 0x19:
            lab.press(["A"], frames=40)          # the flower: held down
        else:
            lab.press(["A"])
        m, kinds = lab.motions_while(60)
        motions += m
        seen |= kinds
    if not set(motions) & set(SHOOT[kind]):
        raise Failed("motions %s" % motions)
    if SHOT[kind] not in seen:
        raise Failed("it fired nothing: %s" % sorted(seen))
    lab.throw_z(kind)
    return "fired 0x%02x, Marth %.0f%%, thrown with Z" % (
        SHOT[kind], lab.marth_percent() - before)


def throw_at_marth(lab, kind, name):
    lab.fresh(marth=-6.0)
    lab.pick_up(kind)
    before = lab.marth_percent()
    lab.press(["A"])
    m, _ = lab.motions_while(30)
    if LIGHT_THROW_F not in m:
        raise Failed("A: motions %s" % m)
    lab.until(lambda: lab.marth_percent() > before, 120, "it to hit Marth")
    return "thrown with A, Marth %.0f%%" % (lab.marth_percent() - before)


def worn(lab, kind, name, field, value):
    lab.fresh()
    fx = lab.fox()["x"]
    lab.spawn(kind, fx + 6)
    lab.landed(kind)
    lab.press(["A"])
    lab.until(lambda: lab.fox()[field] == value, 60,
              "Fox's %s to be %s" % (field, value))
    lab.n.step(120)
    return "%s %s" % (field, value)


def heal(lab, kind, name, to):
    lab.fresh(percent=100.0)
    fx = lab.fox()["x"]
    lab.spawn(kind, fx + 6)
    lab.landed(kind)
    lab.press(["A"])
    f = lab.until(lambda: lab.fox()["percent"] <= to, 300,
                  "Fox healed to %.0f%%" % to)
    if lab.items(kind):
        raise Failed("still there after it healed")
    return "100%% to %.0f%% in %d frames" % (lab.fox()["percent"], f)


def touch(lab, kind, name):
    """The mushrooms walk to Fox, the Starman bounces into him."""
    if kind == 0x0A:
        # it bounces away from the nearest fighter: Fox, then put where it
        # comes down
        lab.fresh(fox=-60.0, marth=70.0)
        lab.spawn(kind, -40.0, 10.0)
        lab.n.step(2)
        lab.n.place(FOX, -13.0, 0, facing=-1)
        f = lab.until(lambda: lab.fox()["star"] > 0, 240,
                      "the Starman to make Fox invincible")
        if lab.items(kind):
            raise Failed("still there after it touched Fox")
        return "invincible for %d frames, %d frames after it came" % (
            lab.fox()["star"], f)
    lab.fresh(fox=0.0, marth=60.0)
    lab.spawn(kind, -40.0, 10.0)
    big = kind == 0x1A
    lab.until(lambda: lab.fox()["motion"] in (GROW if big else SHRINK),
              300, "the mushroom to reach Fox")
    lab.until(lambda: lab.fox()["motion"] == WAIT, 120, "it to end")
    scale = lab.fox()["scale"]
    if (scale <= 1.0) if big else (scale >= 1.0):
        raise Failed("scale %.2f" % scale)
    return "scale %.2f" % scale


def hammer(lab, kind, name):
    lab.fresh()
    lab.pick_up(kind)
    if lab.fox()["motion"] not in HAMMER:
        raise Failed("motion %d" % lab.fox()["motion"])
    lab.n.place(MARTH, lab.fox()["x"] + 10, 0, facing=-1)
    before = lab.marth_percent()
    f = lab.until(lambda: lab.fox()["motion"] not in HAMMER, 900,
                  "the Hammer to wear off")
    hit = lab.marth_percent() - before
    if hit <= 0:
        raise Failed("Marth took nothing")
    return "swung for %d frames, Marth %.0f%%" % (f, hit)


def warp_star(lab, kind, name):
    lab.fresh(marth=-10.0)
    fx = lab.fox()["x"]
    lab.spawn(kind, fx + 6)
    lab.landed(kind)
    lab.press(["A"])
    lab.until(lambda: lab.fox()["motion"] == WARP_STAR[0], 60,
              "Fox to ride it up")
    lab.until(lambda: lab.fox()["motion"] == WARP_STAR[1], 300,
              "Fox to come down on it")
    lab.until(lambda: lab.fox()["motion"] not in WARP_STAR, 300,
              "the crash")
    return "up, down, landed; Marth %.0f%%" % lab.marth_percent()


def screw(lab, kind, name):
    lab.fresh()
    lab.pick_up(kind)
    lab.press(["X"])
    m, _ = lab.motions_while(40)
    if not set(m) & set(SCREW):
        raise Failed("jump: motions %s" % m)
    lab.until(lambda: not lab.n.fighter(FOX).airborne, 200, "landing")
    lab.n.step(20)
    lab.throw_z(kind)
    return "a jump screws (%s), thrown with Z" % m


def parasol(lab, kind, name):
    lab.fresh()
    lab.pick_up(kind)
    lab.press(["X"])
    lab.n.step(6)
    lab.n.pad(FOX, stick=(0, 1))          # up while falling: it opens
    f = lab.until(lambda: lab.fox()["motion"] == PARASOL_OPEN, 90,
                  "the Parasol to open")
    lab.n.pad(FOX)
    lab.until(lambda: not lab.n.fighter(FOX).airborne, 600, "landing")
    lab.n.step(10)
    return "opened %d frames into the jump; %s" % (f, swing(lab, kind,
                                                            name))


def barrel_cannon(lab, kind, name):
    lab.fresh(marth=-12.0)
    lab.pick_up(kind)
    lab.press(["A"])
    lab.until(lambda: lab.n.fighter(MARTH).state in BARREL, 120,
              "Marth in the cannon")
    f = lab.until(lambda: lab.n.fighter(MARTH).state not in BARREL, 900,
                  "the cannon to fire Marth")
    return "Marth in, fired out after %d frames" % f


def ms_bomb(lab, kind, name):
    lab.fresh(marth=40.0)
    lab.pick_up(kind)
    lab.press(["A"])
    lab.until(lambda: any(not i["air"] for i in lab.items(kind)), 120,
              "it to stick")
    lab.n.step(100)                        # it arms
    x = lab.items(kind)[0]["x"]
    lab.n.place(MARTH, x, 0, facing=-1)
    before = lab.marth_percent()
    f = lab.until(lambda: not lab.items(kind), 240, "it to go off")
    lab.n.step(10)
    return "went off %d frames after Marth came, Marth %.0f%%" % (
        f, lab.marth_percent() - before)


def party_ball(lab, kind, name):
    lab.fresh(marth=40.0)
    lab.pick_up(kind)
    lab.press(["A"])
    m, _ = lab.motions_while(20)
    if HEAVY_THROW_F not in m:
        raise Failed("A: motions %s" % m)
    out = set()

    def opened():
        out.update(i["kind"] for i in lab.items() if i["kind"] != kind)
        return not lab.items(kind)
    f = lab.until(opened, 900, "it to open")
    lab.n.step(240)
    return "opened after %d frames: %s" % (f, sorted(out))


def poke_ball(lab, kind, name):
    lab.fresh(marth=40.0)
    lab.pick_up(kind)
    lab.press(["A"])
    lab.until(lambda: any(POKEMON_START <= i["kind"] < POKEMON_START + 30
                          for i in lab.items()), 300, "a Pokemon")
    k = [i["kind"] for i in lab.items()
         if POKEMON_START <= i["kind"] < POKEMON_START + 30][0]
    return "out came %s (the game's own choice)" % POKEMON[k - POKEMON_START]


def container(lab, kind, name, tries=8):
    """Thrown (A), or for the heavy ones also broken by Fox's smashes: it
    opens; what it held."""
    out, how = set(), []
    for t in range(tries):
        lab.fresh(marth=60.0, seed=100 + t)
        if kind in (0x01, 0x02) and t % 2:
            lab.spawn(kind, lab.fox()["x"] + 8)
            lab.landed(kind)
            presses = [0]

            def broken():
                presses[0] += 1
                if presses[0] % 24 == 1:
                    lab.n.pad(FOX, buttons=["A"], stick=(1, 0))
                elif presses[0] % 24 == 3:
                    lab.n.pad(FOX)
                return not lab.items(kind)
            lab.until(broken, 600, "Fox's smashes to break it")
            lab.n.pad(FOX)
            how.append("smashed")
        else:
            lab.pick_up(kind)
            lab.press(["A"])
            if kind == 0x02:
                # a barrel rolls: it breaks on what it meets
                lab.n.place(MARTH, lab.fox()["x"] + 40, 0, facing=-1)
            lab.until(lambda: not lab.items(kind), 600, "it to break")
            how.append("thrown")
        lab.n.step(30)
        out |= {i["kind"] for i in lab.items()}
    return "%d opened (%s); out came %s" % (
        tries, ", ".join(sorted(set(how))),
        ", ".join(sorted(ITEMS.get(k, CONTAINERS.get(k, "0x%02x" % k))
                         for k in out)) or "nothing (explosions)")


def everything(lab, kind, name):
    """The match the game stopped in: every item at very high on Pokemon
    Stadium, a CPU Marth picking them up, a minute."""
    n = lab.n
    n.start("fox", "marth", "pokemon-stadium", seed=9, p2_human=False,
            rules=dict(items=4, mask=ALL))
    n.item("spawns", 1)          # the lab had them stop: a switch kept
    seen = set()
    for _ in range(60 * 60):
        n.step()
        seen |= {i["kind"] for i in lab.items()}
    common = {k for k in seen if k in ITEMS}
    if len(common) < 8:
        raise Failed("only %s came" % sorted(seen))
    return "%d of the 31 came, %d kinds of item in all" % (len(common),
                                                           len(seen))


def pokemon(lab, kind, name):
    lab.fresh(marth=30.0)
    lab.n.item("pokemon", kind)
    lab.pick_up(0x22)
    lab.press(["A"], stick=(0, 1))            # up: it lands by Fox
    lab.until(lambda: lab.items(kind), 300, "%s out of the ball" % name)
    made = set()

    def left():
        made.update(i["kind"] for i in lab.items() if i["kind"] >= 0xBF)
        return not lab.items(kind)
    f = lab.until(left, 2400, "%s to leave" % name)
    want = POKEMON_MAKE.get(kind, set())
    if want and not made & want:
        raise Failed("made %s, not %s" % (sorted(made), sorted(want)))
    return "out, %s, gone after %d frames" % (
        "made " + ", ".join("0x%02x" % k for k in sorted(made))
        if made else "nothing of its own", f)


PLAN = []
for k in sorted(ITEMS):
    PLAN.append(("bare: " + ITEMS[k], bare, k))
for k in sorted(CONTAINERS):
    PLAN.append(("bare: " + CONTAINERS[k], bare, k))
for k in sorted(SWING):
    if k != 0x0D:
        PLAN.append(("swung: " + ITEMS[k], swing, k))
PLAN.append(("opened and swung: Parasol", parasol, 0x0D))
for k in sorted(SHOT):
    PLAN.append(("fired: " + ITEMS[k], shoot, k))
for k in sorted(THROWN):
    PLAN.append(("thrown at Marth: " + ITEMS[k], throw_at_marth, k))
PLAN += [
    ("worn: Bunny Hood", lambda l, k, n: worn(l, k, n, "hat", 0x1F), 0x1F),
    ("worn: Metal Box", lambda l, k, n: worn(l, k, n, "metal", 1), 0x20),
    ("worn: Cloaking Device", lambda l, k, n: worn(l, k, n, "cloak", 1),
     0x21),
    ("healed: Heart Container", lambda l, k, n: heal(l, k, n, 0.0), 0x08),
    ("healed: Maxim Tomato", lambda l, k, n: heal(l, k, n, 50.0), 0x09),
    ("healed: Food", lambda l, k, n: heal(l, k, n, 99.0), 0x12),
    ("touched: Super Mushroom", touch, 0x1A),
    ("touched: Poison Mushroom", touch, 0x1B),
    ("touched: Starman", touch, 0x0A),
    ("swung itself: Hammer", hammer, 0x1C),
    ("ridden: Warp Star", warp_star, 0x1D),
    ("jumped with: Screw Attack", screw, 0x1E),
    ("Marth fired: Barrel Cannon", barrel_cannon, 0x05),
    ("gone off: Motion-Sensor Bomb", ms_bomb, 0x13),
    ("opened: Party Ball", party_ball, 0x04),
    ("opened: Poke Ball", poke_ball, 0x22),
]
for k in sorted(CONTAINERS):
    PLAN.append(("opened: " + CONTAINERS[k], container, k))
for i, nm in enumerate(POKEMON):
    PLAN.append(("Pokemon: " + nm, pokemon, POKEMON_START + i))
PLAN.append(("a minute of every item at very high, Pokemon Stadium",
             everything, None))
# what the window build plays (no snapshots there: these leave the match
# as it was)
WINDOW = ("bare: ", "Pokemon: ", "a minute of every item")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--no-draw", action="store_true",
                    help="leave the draw pass out (faster)")
    ap.add_argument("--window", action="store_true",
                    help="in the window build, drawn on a virtual display")
    ap.add_argument("--exe", default=str(native.EXE),
                    help="the headless game (default %(default)s)")
    ap.add_argument("--only", nargs="*", default=[],
                    help="only the checks whose names hold one of these")
    args = ap.parse_args()
    t0 = time.time()
    lab = Lab(args.exe, not args.no_draw, args.window)
    try:
        for name, fn, kind in PLAN:
            if args.only and not any(o.lower() in name.lower()
                                     for o in args.only):
                continue
            if args.window and not name.startswith(WINDOW):
                continue
            try:
                check(name, True, fn(lab, kind, name))
            except Failed as e:
                check(name, False, str(e))
            except native.NativeError as e:
                why = [l.strip() for l in str(e).splitlines()
                       if "FATAL" in l or "assert" in l or "stopped" in l]
                check(name, False, "the game stopped: %s" % "; ".join(
                    why[:2]))
                lab.close()
                lab.boot()
    finally:
        lab.close()
    print("%d of %d checks passed (%.0f s)" % (sum(checks), len(checks),
                                              time.time() - t0))
    sys.exit(0 if checks and all(checks) else 1)


if __name__ == "__main__":
    main()
