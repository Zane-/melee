"""The blended opponent (tools/melee_engine/opponent.Blend): a slippi-ai
policy moves it, the engine chooses its attacks, against a model of the
player (tools/melee_engine/human.py). Marth against a Fox model, three
ways: the Marth model alone, the engine alone, the blend.

    python tools/native_build.py
    python tests/actor/blend.py          # needs slippi-ai and its models

One run each, so the numbers move from run to run; the checks are about
the kind of play, not exact amounts.
"""
import collections
import random
import sys
import time

sys.path.insert(0, "tools/melee_native")
sys.path.insert(0, "tools")
from native import Native  # noqa: E402
from melee_engine.human import (ModelBody, ModelPlayer, _Model,  # noqa: E402
                                find_model, raw_of)
from melee_engine.opponent import Blend, Mind  # noqa: E402

FRAMES = 900
checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        ("  (" + detail + ")") if detail else ""))


def play(mode, fox_m, marth_m):
    with Native() as n:
        n.start("fox", "marth", "final-destination", seed=3)
        n.place(0, -30, 0, 1)
        n.place(1, 30, 0, -1)
        fox = ModelBody(fox_m, 0, 1)          # the "person": a Fox model
        models = [fox]
        if mode == "blend":
            body, model = ModelBody(marth_m, 1, 0), ModelPlayer(fox_m, 0, 1)
            models += [body, model]
            opp = Blend(n, 1, 0, body, model, goal=dict(contact=40),
                        rng=random.Random(1))
        elif mode == "engine":
            opp = Mind(n, 1, 0, goal=dict(contact=40), rng=random.Random(1))
            source = opp.pads()
        else:
            body = ModelBody(marth_m, 1, 0)
            models.append(body)
        states = collections.Counter()
        pct0, own0 = n.fighter(0).percent, n.fighter(1).percent
        try:
            for _ in range(FRAMES):
                st = n.state()
                line = _Model._ask(fox, st)
                fox_raw = raw_of(line["pad"]) if line and line.get("pad") \
                    else (0,) * 7
                their = dict(zip(("buttons", "lx", "ly", "cx", "cy", "lt",
                                  "rt"), fox_raw))
                if mode == "blend":
                    raw = opp.pad(their)
                elif mode == "engine":
                    raw = next(source)
                else:
                    line = _Model._ask(body, st)
                    raw = raw_of(line["pad"]) if line and line.get("pad") \
                        else (0,) * 7
                for port, r in ((0, fox_raw), (1, raw)):
                    b, lx, ly, cx, cy, lt, rt = r
                    n.h.pads[port].update(buttons=b, lx=lx, ly=ly, cx=cx,
                                          cy=cy, lt=lt, rt=rt, connected=True)
                    n._dirty.add(port)
                n.step()
                states[n.fighter(1).state] += 1
        finally:
            for m in models:
                m.close()
        out = dict(dealt=n.fighter(0).percent - pct0,
                   taken=n.fighter(1).percent - own0, kinds=len(states),
                   moving=states[20] + states[21] + states[18],
                   jumps=sum(states[s] for s in (25, 26, 27, 28)))
        if mode == "blend":
            out["commits"] = [m for _, m, _ in opp.commits]
        return out


def main():
    t0 = time.time()
    fox_m, marth_m = find_model("fox", "marth"), find_model("marth", "fox")
    if not (fox_m and marth_m):
        print("skip: no slippi-ai models for Fox and Marth")
        return 0
    r = {m: play(m, fox_m, marth_m) for m in ("policy", "engine", "blend")}
    for m, v in r.items():
        print("     %-7s dealt %.0f%% took %.0f%%, %d states, dash/run/turn "
              "%d frames, jumps %d" % (m, v["dealt"], v["taken"], v["kinds"],
                                       v["moving"], v["jumps"]))
    b, e, p = r["blend"], r["engine"], r["policy"]
    check("the blend moves like the model: dashes, turns and jumps",
          b["moving"] >= p["moving"] // 3 and b["jumps"] >= p["jumps"] // 3
          and b["moving"] > e["moving"],
          "dash/run/turn %d (model %d, engine %d), jumps %d (model %d)" % (
              b["moving"], p["moving"], e["moving"], b["jumps"], p["jumps"]))
    check("it commits to varied attacks, not one",
          len(set(b["commits"])) >= 4,
          "%d commitments: %s" % (len(b["commits"]),
                                  ", ".join(sorted(set(b["commits"])))))
    check("it deals more than it takes, and takes less than the engine "
          "alone", b["dealt"] > b["taken"] and b["taken"] < e["taken"],
          "dealt %.0f%%, took %.0f%% (engine alone took %.0f%%)" % (
              b["dealt"], b["taken"], e["taken"]))
    print("%d of %d checks passed (%.0f s)" % (sum(checks), len(checks),
                                                time.time() - t0))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
