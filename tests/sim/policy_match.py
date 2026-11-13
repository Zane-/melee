"""slippi-ai policies playing in the headless simulator.

    ~/Games/Melee/slippi-ai/venv/bin/python tests/sim/policy_match.py [frames]

Fox (port 1) and Marth (port 2) are each played by a trained policy for a
number of frames on Final Destination. Prints what happened: damage, the
variety of action states, stocks lost, and how fast it ran.
"""
import collections
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..",
                                "tools"))
from melee_actor import policy as pol                       # noqa: E402
from sim import Sim                                         # noqa: E402

MODELS = os.path.join(pol.SLIPPI_AI, "deployed_models")


def main():
    frames = int(sys.argv[1]) if len(sys.argv) > 1 else 1800
    s = Sim.match("lab", "fox", "marth", free=True)
    s.step(30)
    t0 = time.time()
    fox = pol.PolicyPlayer(s, 0, 1, os.path.join(MODELS,
                                                 "fox_d18_vs_marth_v3.1"))
    marth = pol.PolicyPlayer(s, 1, 0, os.path.join(MODELS,
                                                   "marth_d18_vs_fox_v3.1"))
    print("loaded in %.1fs; delays %d and %d frames"
          % (time.time() - t0, fox.delay, marth.delay))
    states = [collections.Counter(), collections.Counter()]
    peak = [0.0, 0.0]
    falls = [0, 0]
    last = [0.0, 0.0]
    t0 = time.time()
    for f in range(frames):
        fox.act()
        marth.act()
        s.step()
        for i in (0, 1):
            ft = s.fighter(i)
            states[i][ft.state] += 1
            pct = ft.percent
            if pct < last[i] - 20:
                falls[i] += 1
            last[i] = pct
            peak[i] = max(peak[i], pct)
        if (f + 1) % 300 == 0:
            a, b = s.fighter(0), s.fighter(1)
            print("frame %4d  Fox %3.0f%% x%5.0f y%4.0f st %3d | "
                  "Marth %3.0f%% x%5.0f y%4.0f st %3d"
                  % (f + 1, a.percent, a.pos[0], a.pos[1], a.state,
                     b.percent, b.pos[0], b.pos[1], b.state))
    dt = time.time() - t0
    print("%d frames in %.1fs (%.0f frames/s)" % (frames, dt, frames / dt))
    for i, name in ((0, "Fox"), (1, "Marth")):
        print("%-5s peak %3.0f%%, lost %d stocks, %d different action "
              "states, most common %s"
              % (name, peak[i], falls[i], len(states[i]),
                 states[i].most_common(5)))


if __name__ == "__main__":
    main()
