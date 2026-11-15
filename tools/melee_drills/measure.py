"""The per-character numbers a drill may name that frame data does not give,
measured in the game (headless), into data/drills/numbers.json:

    python tools/melee_drills/measure.py [--chars fox,marth]

- DASH: the frames of a dash before a held stick makes it a run (the
  dash's first frame counted as 1): Sheik 7, Fox 11.
- SL: the frame a short hop lands on (the jump's press frame 1).
- LD: the earliest frame of a ledgedash's air dodge that lands on the stage
  (let go of the ledge on frame 1, jump on frame 2, the stick toward the
  stage, the air dodge down and in at 45 degrees): Fox 5, Peach 29.
- NL: the frame a short hop with a neutral air (A on its top, frame SA)
  lands on; NFL: the same with the neutral air on SA-4 and a fast fall
  (down on SA for 3 frames): where an L-cancel or a SHFFL lands.
- SHD: how far a short hop goes with the stick held forward from frame 1
  to the landing (a drill placed SHD from an edge lands at it).
- SPF, SPD: a short hop with a neutral air (A on SA) that fits on a side
  platform of Battlefield (37.6 wide): SPF the first frame of a drift
  (the stick forward to SA-1, neutral on SA for the A, forward again from
  SA+1) with which it goes at most SIDE_PLATFORM by its landing (NL), SPD
  how far it goes. SPF is 1 where the whole hop's drift fits; the floaty
  characters drift later: Samus 11, Jigglypuff 14.

format.names() adds them to a character's numbers. Each is measured with
the drills' own scenarios (data/drills/universal-*.json), as a player's
inputs are played there.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "melee_native"))

from native import Native  # noqa: E402
from melee_course import engine  # noqa: E402
from melee_drills import format as F  # noqa: E402
from melee_drills.drill import JsonDrill, inputs_to_refs  # noqa: E402

OUT = os.path.join(F.ROOT, "data", "drills", "numbers.json")
DASH, RUN, LANDING_SPECIAL = 20, 21, 43


class Enough(Exception):
    pass


def frames(game, ch, drill_id, inputs, n):
    """The player's (state, air, x) on the example's frames 1..n of
    `inputs` played in drill `drill_id`'s scenario."""
    drill = JsonDrill(F.load(drill_id))
    s = engine.Session(drill, game, character=ch, live=False, seed=1,
                       dpad=False)
    drill.build_reference = lambda c: inputs_to_refs(inputs, drill.nums(c),
                                                     drill.ref_start)
    lead = drill.ref_lead + drill.ref_start - 1
    got = []

    def each(g, frame):
        if s.demo_pass != 2 or frame <= lead + 1:
            return
        f = g.fighter(s.person)
        got.append((f.state, f.airborne, f.pos[0]))
        if len(got) >= n:
            raise Enough()
    try:
        s.run(demo=True, each_frame=each)
    except Enough:
        pass
    return got


def dash_frames(game, ch):
    rec = frames(game, ch, "universal-fast-fall",
                 [{"stick": [1, 0], "frame": 1, "hold": 60}], 50)
    first = next(i for i, r in enumerate(rec) if r[0] == DASH)
    run = next(i for i, r in enumerate(rec) if r[0] == RUN)
    return run - first


def short_hop_landing(game, ch):
    rec = frames(game, ch, "universal-fast-fall",
                 [{"press": "jump", "frame": 1, "hold": 1}], 90)
    up = next(i for i, r in enumerate(rec) if r[1])
    return next(i for i in range(up, len(rec)) if not rec[i][1]) + 1


def landing(rec):
    """The first frame on the ground after the first in the air (1 the
    example's first), and the x moved by then."""
    up = next(i for i, r in enumerate(rec) if r[1])
    down = next(i for i in range(up, len(rec)) if not rec[i][1])
    return down + 1, abs(rec[down][2] - rec[0][2])


def aerial_landings(game, ch):
    nums = JsonDrill(F.load("universal-fast-fall")).nums
    from melee_course.engine import FighterData
    sa = F.names(FighterData.of(ch))["SA"]
    nl, _ = landing(frames(game, ch, "universal-dash-dance", [
        {"press": "jump", "frame": 1, "hold": 1},
        {"press": "A", "frame": sa, "hold": 1}], 120))
    nfl, _ = landing(frames(game, ch, "universal-dash-dance", [
        {"press": "jump", "frame": 1, "hold": 1},
        {"press": "A", "frame": sa - 4, "hold": 1},
        {"stick": [0, -1], "frame": sa, "hold": 3}], 120))
    _, shd = landing(frames(game, ch, "universal-dash-dance", [
        {"press": "jump", "frame": 1, "hold": 1},
        {"stick": [1, 0], "frame": 1, "hold": 100}], 120))
    del nums
    return {"NL": nl, "NFL": nfl, "SHD": round(shd, 1)}


# a short hop on a Battlefield side platform (x 20 to 57.6): landing 2.1
# inside its outer edge, from 2.5 or more inside its inner one
SIDE_PLATFORM = 33.0


def side_platform_drift(game, ch):
    from melee_course.engine import FighterData
    sa = F.names(FighterData.of(ch))["SA"]
    for d in range(1, sa):
        _, dist = landing(frames(game, ch, "universal-dash-dance", [
            {"press": "jump", "frame": 1, "hold": 1},
            {"stick": [1, 0], "frame": d, "hold": sa - d},
            {"press": "A", "frame": sa, "hold": 1},
            {"stick": [1, 0], "frame": sa + 1, "hold": 100}], 120))
        if dist <= SIDE_PLATFORM:
            return {"SPF": d, "SPD": round(dist, 1)}
    raise RuntimeError("%s: no drift fits a side platform" % ch)


def ledgedash_frame(game, ch):
    for k in range(4, 40):
        inputs = [{"stick": [0, -1], "frame": 1, "hold": 1},
                  {"press": "jump", "frame": 2, "hold": 1},
                  {"stick": [1, 0], "frame": 2, "hold": k - 2},
                  {"stick": [0.7, -0.7], "frame": k, "hold": 1},
                  {"press": "R", "frame": k, "hold": 1}]
        rec = frames(game, ch, "universal-ledgedash", inputs, k + 20)
        # (an air dodge into the ground can land on its own first frame:
        # straight from the jump to the landing, never an air dodge frame)
        if any(r[0] == LANDING_SPECIAL and not r[1] for r in rec[k - 1:]):
            return k
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chars")
    ap.add_argument("--only", help="numbers to measure, comma separated "
                    "(the others kept): DASH,SL,LD,NL,NFL,SHD,SPF,SPD")
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None

    def want(*names):
        return only is None or any(n in only for n in names)
    chars = args.chars.split(",") if args.chars else sorted(
        f[:-5] for f in os.listdir(os.path.join(F.ROOT, "data", "framedata"))
        if f.endswith(".json"))
    have = {}
    if os.path.exists(OUT):
        with open(OUT) as f:
            have = json.load(f)
    for ch in chars:
        nums = dict(have.get(ch, {}))
        if want("DASH", "SL"):
            with Native() as game:
                nums.update(DASH=dash_frames(game, ch),
                            SL=short_hop_landing(game, ch))
        if want("NL", "NFL", "SHD"):
            with Native() as game:
                nums.update(aerial_landings(game, ch))
        if want("LD"):
            with Native() as game:
                nums["LD"] = ledgedash_frame(game, ch)
        if want("SPF", "SPD"):
            with Native() as game:
                nums.update(side_platform_drift(game, ch))
        have[ch] = nums
        print("%-18s %s" % (ch, nums), flush=True)
    with open(OUT, "w") as f:
        json.dump(dict(sorted(have.items())), f, indent=1)
        f.write("\n")
    print("wrote", OUT)


if __name__ == "__main__":
    sys.exit(main())
