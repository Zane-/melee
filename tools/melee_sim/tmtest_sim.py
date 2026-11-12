#!/usr/bin/env python3
"""Run tools/tmtest.py specs in the simulator instead of Dolphin.

    python tools/melee_sim/tmtest_sim.py tests/tmtest/shineoos/*.json
    python tools/melee_sim/tmtest_sim.py --json SPEC.json

Same specs, same test build (build/overlay-tmtest, TM_TEST=1), same result
records: only the thing that executes the DOL differs. See
docs/ai/testing.md for the spec format and docs/ai/simulator.md for what
the simulator is and is not.
"""

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import tmtest  # noqa: E402
from sim import Sim, GuestError, ROOT  # noqa: E402

OUT = ROOT / "build" / "overlay-tmtest"


def run(spec, timeout=180, keep_log=False):
    started = time.time()
    s = Sim(dol=OUT / "main.dol", overlay_map=OUT / "overlay.map")
    s.m.write(s.m.sym.addr("tm_test_config"), tmtest.pack_config(spec))
    records, other, seen = [], [], 0
    status = "timeout"
    budget = spec.get("max_frames", 600) + 3000
    try:
        s.boot()
        while s.frame < budget and time.time() - started < timeout:
            # no memory card: confirm the prompt until the match is up
            started_match = any("match" in r for r in records)
            s.pad(0, ["A"] if not started_match and s.frame % 20 < 3 else [])
            s.step()
            for text in s.h.reports[seen:]:
                for line in text.splitlines():
                    line = line.strip()
                    if line.startswith("TMTEST "):
                        try:
                            records.append(json.loads(line[7:]))
                        except json.JSONDecodeError:
                            records.append({"bad_json": line[7:]})
                    elif line:
                        other.append(line)
            seen = len(s.h.reports)
            if any(r.get("done") for r in records):
                status = "done"
                break
    except (GuestError, RuntimeError) as e:
        status = "crash"
        other.append(str(e))
    result = {"status": status, "seconds": round(time.time() - started, 1),
              "frames": s.frame, "backend": "melee_sim", "records": records}
    if status != "done":
        result["log_tail"] = other[-25:]
    return result


if __name__ == "__main__":
    tmtest.run = run
    if "--no-build" not in sys.argv:
        sys.argv.append("--no-build")     # the simulator never builds
    tmtest.main()
