"""The overlay's course drill specs, run against the native port of the drills.

    python tests/course/specs.py [DRILL ...] [--spec NAME] [-v]

tests/tmtest/course/<drill>/*.json are the automated proof of the C drills
(src/tmce/events/course): each sets the drill's options, plays the player's
inputs (or the drill's own demonstration) and says what the first verdict
must be. Here the same files run on the native build against
tools/melee_course: the same options by the same indexes, the same inputs at
the same match frames (or on the same fighter state changes), the same
expectations. A spec passes when its "event_result" and every other
expected field that the port reports come out the same.

Spec timing (docs/ai/testing.md): `at` is the match frame, 1 being the frame
the first attempt is set up; `on_enter` / `on_exit` fire on the frame after
a fighter's state change is visible, plus `delay`; `exact` puts the input on
the frame of the change itself (found by a first run). Fields that only the
C engine reports are listed as "not reported", not failed.

Specs that open Training Mode's pause menu (a START input: its options,
its Help entry) test the overlay's menus, which the native client does not
have; they are listed as not applicable, with that reason, and not run.
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, ROOT)

from native import CHARACTERS, Native  # noqa: E402
from tools import tmtest  # noqa: E402
from melee_course import engine, registry  # noqa: E402

BY_NUMBER = {v: k for k, v in CHARACTERS.items()}

# The drills draw random choices (HSD_Randi in C, Ctx.randi here) from
# different streams, so the same seed gives the same choices in another
# order. A spec that depends on one particular draw gets the C's here: the
# draw it names, as the C made it with that spec's seed.
DRAWS = {
    # the CPU's DI: the C's first draw was 0, away (-127)
    "fox-uthrow-uair/player_di_away": [0],
    "fox-kill-confirm/waveshine_usmash_110": [0],
}


# Drills the owner asked to change on the native build after the overlay's
# specs were written (2026-11-13): the options that play them as the C does,
# so the specs still prove the rest. By option name, before the spec's own.
NATIVE_AS_C = {
    # levels 1 to 4 ("1 is shortest ... 4 is longest"); the C took any
    # shortening
    "fox-illusion-shorten": {"Level": 5},
    # up to 5 frames late; the C's default was 2
    "fox-waveshine": {"Leniency": 2},
    # starts falling to the ledge; the C's on it
    "universal-ledgedash": {"Start": 0},
    # the shielding opponent held in place; the C's was pushed back
    "fox-shffl-nair-shine": {"Opponent": 1},
    # the opponent's attack is the Melee Actor's, aimed so it lands
    # (melee_course/react.py); the C's is a table of inputs by frame
    "fox-wavedash-back-punish": {"Opponent": 1},
    "fox-anti-air": {"Opponent": 1},
    "fox-shine-oos": {"Opponent": 1},
}
# The same for the common options (by index): a deck the C did not have.
NATIVE_AS_C_COMMON = {
    # platforms and starts in turn; the C's: Battlefield's left platform,
    # standing (the deck's first)
    "universal-shield-drop": {engine.OPT_SCENARIO: 1},
}


# Specs of the C's behaviour that the owner changed on the native build
# (2026-11-13); tests/course/native_changes.py checks the new behaviour.
SUPERSEDED = {
    "universal-dash-dance/six": "the dance is no longer cut at six dashes",
    "universal-dash-dance/stop": "a dance of one switch now counts",
    "universal-dash-dance/demo_fox": "the demonstration dances all twenty",
    # one drill became two, ASDI down (standing, the C-stick) and crouch
    # cancel, each with a deck of moves at percents they hold to
    # (tests/course/asdi.py checks them)
    "universal-asdi-down/demo": "split into ASDI down and crouch cancel",
    "universal-asdi-down/no_punish": "split into ASDI down and crouch cancel",
    "universal-asdi-down/high_percent": "split into ASDI down and crouch "
                                        "cancel",
}


def character(name):
    return BY_NUMBER[tmtest.ident(tmtest.CKIND, name, "character")]


class Player:
    """The spec's inputs for the player, applied frame by frame."""

    def __init__(self, session, inputs):
        self.s = session
        self.inputs = []
        for e in inputs:
            e = dict(e)
            for kind in ("on_enter", "on_exit"):
                if kind in e:
                    e[kind] = dict(e[kind])
                    e[kind]["state"] = tmtest.ident(
                        tmtest.STATE, e[kind]["state"], "state")
            self.inputs.append(e)
        self.fired = {}           # input index -> the frame it starts on
        self.last = {}            # port -> state at the end of the last frame
        self.count = {}           # (kind, port, state) -> times seen
        self.changes = []         # (frame of the change, kind, port, state)

    def __call__(self, game, frame):
        mf = frame + 2            # match frame: 1 is the setup frame
        st = game.state()
        for port in (0, 1):
            p = st["p"][port]
            now = p["state"] if p else None
            was = self.last.get(port)
            if was is not None and now != was:
                for kind, state in (("on_exit", was), ("on_enter", now)):
                    key = (kind, port, state)
                    self.count[key] = self.count.get(key, 0) + 1
                    # the change happened during the last frame
                    self.changes.append((mf - 1, kind, port, state,
                                         self.count[key]))
                    for i, e in enumerate(self.inputs):
                        t = e.get(kind)
                        if t is None or i in self.fired:
                            continue
                        if t.get("port", 0) == port and t["state"] == state \
                                and e.get("occurrence", 1) == self.count[key] \
                                and not e.get("exact"):
                            self.fired[i] = mf + e.get("delay", 0)
            self.last[port] = now
        buttons = lx = ly = cx = cy = trigger = 0
        for i, e in enumerate(self.inputs):
            start = e["at"] if "at" in e else self.fired.get(i)
            if start is None or not start <= mf < start + e.get("hold", 1):
                continue
            for b in e.get("buttons", []):
                buttons |= tmtest.BUTTON[b.upper()]
            if "stick" in e:
                lx, ly = e["stick"]
            if "cstick" in e:
                cx, cy = e["cstick"]
            trigger = max(trigger, e.get("r", 0), e.get("l", 0))
        if not self.s.demo_pass:
            self.s.set_player_pad(buttons, lx, ly, cx, cy, trigger)


def session_for(spec, game, name=None):
    drill = registry.get(spec["drill"])
    hmn = character(spec.get("hmn", "fox"))
    if spec.get("cpu") and not drill.deck and drill.cpu:
        drill.cpu = character(spec["cpu"])
    common = dict(NATIVE_AS_C_COMMON.get(spec["drill"], {}))
    options = dict(NATIVE_AS_C.get(spec["drill"], {}))
    for idx, val in spec.get("options", []):
        if idx < engine.OPT_COMMON_COUNT:
            common[idx] = val
        else:
            options[idx - engine.OPT_COMMON_COUNT] = val
    return engine.Session(drill, game, character=hmn, options=options,
                          common=common, live=False,
                          seed=spec.get("seed", 1),
                          draws=DRAWS.get("%s/%s" % (spec["drill"], name)))


def first_result(spec, game, inputs, name=None):
    """The first verdict, as the C test harness logs it. The D-pad works as
    the C engine's: up opens the guide (the attempt is dropped), and in the
    guide up closes it and right plays a demonstration; left and right
    change scenario and down resets (no verdict either)."""
    s = session_for(spec, game, name)
    player = Player(s, inputs)
    limit = spec.get("max_frames", 900)
    s.LIMIT = limit
    frames = [0]

    def counted(game, frame):
        frames[0] += 1
        player(game, frames[0] - 2)

    demo = None
    while frames[0] < limit:
        result = s.run(each_frame=counted, demo=demo)
        demo = None
        if result.get("ui") != "guide":
            if result.get("ui") is None:
                return result, player
            continue
        # the guide is open: frames pass until up or right
        was = s.prev_buttons
        while frames[0] < limit:
            counted(game, 0)
            held = s.player_pad["buttons"]
            down = held & ~was
            was = held
            game.step()
            if down & engine.DUP:
                break
            if down & engine.DRIGHT:
                demo = True
                break
        s.prev_buttons = was
    return result, player


def resolve_exact(spec, game, name=None):
    """Inputs marked "exact" go on the frame of the state change itself:
    found by a run without them (runs are deterministic)."""
    inputs = spec.get("inputs", [])
    exact = [i for i, e in enumerate(inputs) if e.get("exact")]
    if not exact:
        return inputs
    plain = [e for e in inputs if not e.get("exact")]
    _, player = first_result(spec, game, plain, name)
    out = list(inputs)
    for i in exact:
        e = inputs[i]
        kind = "on_enter" if "on_enter" in e else "on_exit"
        state = tmtest.ident(tmtest.STATE, e[kind]["state"], "state")
        port = e[kind].get("port", 0)
        nth = e.get("occurrence", 1)
        hit = next((f for f, k, p, s, n in player.changes
                    if k == kind and p == port and s == state and n == nth),
                   None)
        if hit is None:
            raise ValueError("exact input: %s %s never happened" %
                             (kind, e[kind]["state"]))
        fixed = {k: v for k, v in e.items()
                 if k not in ("exact", kind, "delay", "occurrence")}
        fixed["at"] = hit + e.get("delay", 0)
        out[i] = fixed
    return out


def check(spec, result):
    """(passed, [what differed], [expected fields not reported])"""
    bad, missing = [], []
    for key, want in spec.get("expect", {}).items():
        if key == "event_result":
            got = "retry" if result["skip"] else \
                "success" if result["success"] else "fail"
        elif key == "demo":
            got = 2 if result["demo"] else 0
        elif key == "measured":
            got = result["measured"] if result["measured"] is not None else -1
        elif key == "target":
            got = result["target"] if result["target"] is not None else -1
        elif key in result["report"]:
            got = result["report"][key]
        else:
            missing.append(key)
            continue
        if isinstance(want, float) or isinstance(got, float):
            same = abs(float(got) - float(want)) < 0.06
        else:
            same = got == want
        if not same:
            bad.append("%s: %r, the spec says %r" % (key, got, want))
    return not bad, bad, missing


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("drills", nargs="*")
    ap.add_argument("--spec", help="only specs whose file name has this")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    drills = args.drills or [d for d in registry.ids()]
    total = passed = 0
    unported = []
    with Native() as game:
        for d in drills:
            if not registry.has(d):
                unported.append(d)
                continue
            files = sorted(glob.glob(os.path.join(
                ROOT, "tests", "tmtest", "course", d, "*.json")))
            for path in files:
                name = os.path.basename(path)[:-5]
                if args.spec and args.spec not in name:
                    continue
                with open(path) as f:
                    spec = json.load(f)
                if any("START" in [b.upper() for b in e.get("buttons", [])]
                       for e in spec.get("inputs", [])):
                    print("n/a   %s/%s  (Training Mode's pause menu)" %
                          (d, name))
                    continue
                why = SUPERSEDED.get("%s/%s" % (d, name))
                if why:
                    print("n/a   %s/%s  (changed natively: %s)" % (d, name,
                                                                  why))
                    continue
                total += 1
                try:
                    inputs = resolve_exact(spec, game, name)
                    result, _ = first_result(spec, game, inputs, name)
                    ok, bad, missing = check(spec, result)
                except Exception as e:  # a spec the port cannot run
                    ok, bad, missing = False, ["%s: %s" % (
                        type(e).__name__, str(e)[:200])], []
                    result = None
                passed += ok
                line = "%s  %s/%s" % ("ok  " if ok else "FAIL", d, name)
                if result is not None:
                    line += "  (%s: %s%s)" % (
                        "success" if result["success"] else
                        "retry" if result["skip"] else "fail",
                        result["full_words"].replace("\n", " "),
                        ", measured %s of %s" % (result["measured"],
                                                 result["target"])
                        if result["measured"] is not None else "")
                print(line)
                for b in bad:
                    print("        " + b)
                if missing and args.verbose:
                    print("        not reported: " + ", ".join(missing))
    if unported:
        print("not ported: " + ", ".join(unported))
    print("%d of %d specs passed" % (passed, total))
    return 0 if passed == total and not unported else 1


if __name__ == "__main__":
    sys.exit(main())
