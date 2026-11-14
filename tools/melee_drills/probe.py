"""A drill's scenario with some inputs played, frame by frame: what the game
did, for writing a drill's numbers from the game rather than from memory.

    python tools/melee_drills/probe.py universal-wavedash \\
        --inputs '[{"press": "jump", "frame": 1}, {"press": "R", "frame": 4}]'
    python tools/melee_drills/probe.py universal-wavedash --char marth --part 2

Prints, for each frame from the example's frame 1: the player's action
state (by name when the format has one), in the air or not, position,
velocity, hitlag, invulnerability, and the attempt's frames as the drill
counts them. Without --inputs, the part's example is played. Headless.
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
from melee_drills.drill import JsonDrill, REF_START, inputs_to_refs  # noqa


def state_name(s):
    for name, v in F.STATES.items():
        if (s in v) if isinstance(v, tuple) else s == v:
            if not isinstance(v, tuple):
                return name
    for name, v in F.STATES.items():
        if isinstance(v, tuple) and s in v:
            return name
    return str(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("drill")
    ap.add_argument("--inputs", help="a JSON list of the format's inputs")
    ap.add_argument("--char", default="fox")
    ap.add_argument("--part", type=int, default=1, help="from 1")
    ap.add_argument("--frames", type=int, default=60,
                    help="frames shown from the example's frame 1")
    args = ap.parse_args()
    spec = F.load(args.drill)
    drill = JsonDrill(spec)
    drill.set_part(args.part - 1)
    inputs = json.loads(args.inputs) if args.inputs else \
        drill.part_now["example"]
    with Native() as game:
        s = engine.Session(drill, game, character=args.char, live=False,
                           seed=1, dpad=False)
        drill.build_reference = lambda c: inputs_to_refs(inputs,
                                                         drill.nums(c))
        lines = []
        lead = engine.REF_LEAD + REF_START - 1

        def each(n, frame):
            if s.demo_pass != 2 or frame <= lead - 3 or \
                    frame > lead + args.frames:
                return
            f = n.fighter(s.person)
            if not f.fp:
                return
            log = s.tl_log[-1] if s.tl_log else {}
            lines.append(
                "%4d  %-16s %-3s x %7.2f y %7.2f vx %6.2f vy %6.2f "
                "hl %4.1f %s  stick %4d %4d  %s%s" % (
                    frame - lead - 1, state_name(f.state),
                    "air" if f.airborne else "gnd", f.pos[0], f.pos[1],
                    f.vel[0], f.vel[1], f.hitlag,
                    "inv" if f.invulnerable else "   ",
                    log.get("lx", 0), log.get("ly", 0),
                    "phase %d" % s.c.phase,
                    "  opp %s" % state_name(s.c.cpu.state)
                    if s.c.cpu else ""))
        r = s.run(demo=True, each_frame=each)
    print("frame state            ...  (frame 1: the example's first)")
    print("\n".join(lines))
    print("result:", r.get("words"), "|", r.get("fix") or "")


if __name__ == "__main__":
    sys.exit(main())
