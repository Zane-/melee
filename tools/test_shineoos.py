#!/usr/bin/env python3
"""Automated Dolphin test of the Shine OoS event and character rotation.

    tools/test_shineoos.py [--attempts 21] [--no-build]

Builds a test overlay that boots straight into Shine OoS
(build/overlay-test), installs it on build/disc-test (hard-linked copy of
build/disc), boots it with tools/dolphin_harness.py, picks Fox, holds
shield and records, per attempt: the scenario, the CPU's character, and
whether the attack reached the shield. Reports per scenario.
"""

import argparse
import os
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dolphin_harness import Dolphin, Overlay  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "overlay-test"
DISC = ROOT / "build" / "disc-test"

CSS_CURSORS = 0x804A0BC0     # mnCharSel_804A0BC0: CSSCursorData* [4]
PLAYER_SLOTS = 0x80453080    # player_slots, 0xE90 per slot
FOX_ICON = (-20.9, 9.5)      # mncharsel.c icon bounds: middle row, column 1
PHASES = ["wait_shield", "attack", "punish", "followup", "result"]
CKINDS = {0x00: "Falcon", 0x02: "Fox", 0x09: "Marth", 0x0C: "Peach",
          0x0F: "Jigglypuff", 0x13: "Sheik", 0x14: "Falco"}
EV_STUN_DISTANCE = 48   # offset of ev.stun_distance (event.c)
SHINE_REACH = 12.0      # shine hitbox radius 8 + a typical hurtbox, units


def build():
    env = dict(os.environ, OVERLAY_OUT="build/overlay-test",
               TM_DEFINES="TM_AC_BOOT_EVENT=shineoos TM_TEST_BOT=1")
    r = subprocess.run([sys.executable, "tools/overlay_build.py", "--force"],
                       cwd=ROOT, env=env, capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)
    if not DISC.exists():
        subprocess.run(["cp", "-al", str(ROOT / "build/disc"), str(DISC)], check=True)
    dol = DISC / "sys" / "main.dol"
    dol.unlink()  # break the hard link before writing
    shutil.copyfile(OUT / "main.dol", dol)
    subprocess.run([sys.executable, "tools/tmce_disc.py", "--disc", str(DISC),
                    "--dol", str(OUT / "main.dol")], cwd=ROOT, check=True,
                   capture_output=True)


def pick_fox(d):
    if not d.wait_for(lambda: d.read_u32(CSS_CURSORS) != 0, timeout=90):
        sys.exit("never reached the character select screen")
    time.sleep(1.0)
    cur = d.read_u32(CSS_CURSORS)
    # Each memory read pauses emulation, so move for a while between reads.
    for _ in range(100):
        x, y = struct.unpack(">ff", d.read(cur + 0xC, 8))
        dx, dy = FOX_ICON[0] - x, FOX_ICON[1] - y
        if abs(dx) < 1.2 and abs(dy) < 1.2:
            break
        d.stick(max(-1, min(1, dx / 3)), max(-1, min(1, dy / 3)))
        time.sleep(0.08)
        d.neutral()
        time.sleep(0.05)
    d.neutral()
    time.sleep(0.2)
    d.press("A")
    time.sleep(0.5)
    d.press("START")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempts", type=int, default=21)
    ap.add_argument("--no-build", action="store_true")
    args = ap.parse_args()
    if not args.no_build:
        build()

    ov = Overlay(OUT / "overlay.map")
    ev = ov.addr("ev", "shineoos")
    names = []

    with Dolphin(DISC / "sys" / "main.dol") as d:
        pick_fox(d)
        if not d.wait_for(lambda: d.read_u32(PLAYER_SLOTS + 0xE90 + 0xB0) != 0,
                          timeout=60):
            sys.exit("match never started")
        d.hold("R")
        d.send("SET R 1")
        results = {}
        last = None
        seen_punish = False
        dist = 0.0
        deadline = time.time() + 40 * args.attempts
        attempts = 0
        while attempts < args.attempts and time.time() < deadline:
            if not d.alive():
                sys.exit("Dolphin exited (crash?) - see build/dolphin-test/dolphin.log")
            phase, scen = struct.unpack(">ii", d.read(ev, 8))
            ckind = d.read_u32(PLAYER_SLOTS + 0xE90 + 4)
            if phase == 2:
                seen_punish = True
                dist = d.read_f32(ev + EV_STUN_DISTANCE)
            key = (scen, ckind)
            if last is not None and (phase, scen) != last:
                if last[0] in (1, 2, 3) and phase == 4:
                    r = results.setdefault(last[1], {"hit": 0, "miss": 0, "ck": set(),
                                                     "dist": []})
                    r["hit" if seen_punish else "miss"] += 1
                    if seen_punish:
                        r["dist"].append(dist)
                    shine_hit = d.read_s32(ev + 8) == 1  # ev.last_success
                    r.setdefault("shine", 0)
                    r["shine"] += shine_hit
                    r["ck"].add(CKINDS.get(ckind, hex(ckind)))
                    attempts += 1
                    print(f"attempt {attempts}: scenario {last[1]} cpu "
                          f"{CKINDS.get(ckind, hex(ckind))}: "
                          f"{'shield hit, distance %.1f, shine %s' % (dist, 'HIT' if shine_hit else 'missed') if seen_punish else 'MISSED shield'}",
                          flush=True)
                    seen_punish = False
            last = (phase, scen)
            time.sleep(0.05)
        d.release("R")

    print("\nper scenario:")
    for s, r in sorted(results.items()):
        far = [x for x in r["dist"] if x > SHINE_REACH]
        dist = (" distance %.1f-%.1f" % (min(r["dist"]), max(r["dist"]))) if r["dist"] else ""
        print(f"  {s}: shield hit {r['hit']}, missed {r['miss']},{dist},"
              f" shine hit {r.get('shine', 0)}/{r['hit']} cpu {sorted(r['ck'])}")


if __name__ == "__main__":
    main()
