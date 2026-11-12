#!/usr/bin/env python3
"""Run a scripted, deterministic test of a training event in headless Dolphin.

    tools/tmtest.py tests/tmtest/shineoos_marth_dtilt.json      # build + run
    tools/tmtest.py --no-build SPEC.json [--json] [--keep-log]
    tools/tmtest.py --list-states fox                             # helper

A test build (TM_TEST=1, src/melee/tm/test/) boots straight into one
event's match with the characters, stage and RNG seed from the spec, plays
the spec's input script on port 1 frame-exactly (no menus, no wall-clock
timing) and reports "TMTEST {json}" lines through OSReport. This script
writes the spec into the DOL's `tm_test_config`, runs Dolphin with no
window, no audio and unlimited speed in an isolated user directory, and
returns the JSON records. The same test build runs in tools/melee_sim.

Spec (JSON):
  {
    "event": "shineoos",            # EventDesc.eventFile
    "hmn": "fox", "hmn_color": 0,   # character ids: names below or numbers
    "cpu": "marth",                 # optional; the event's choice otherwise
    "stage": "fd",                  # optional
    "seed": 1, "max_frames": 600, "trace": 0,   # trace: log fighters every N
    "options": [[0, 1]],            # [menu option index, value]
    "inputs": [                      # port 1 script
      {"at": 0, "hold": 600, "buttons": ["R"], "r": 255},
      {"on_exit": {"port": 0, "state": "GuardSetOff"}, "delay": 0,
       "buttons": ["X"]},
      {"on_exit": {"port": 0, "state": "GuardSetOff"}, "delay": 3,
       "buttons": ["B"], "stick": [0, -127], "exact": true}
    ],
    # on_exit/on_enter fire on the frame after the change is seen (a
    # 1-frame reaction); "exact": true places the input on the frame of the
    # change itself, found by traced dry runs (deterministic), in order, so
    # later exact triggers may depend on earlier exact inputs.
    "expect": {"event_result": "success"}   # optional, checked by the event's
  }                                          # own TMTEST result lines
"""

import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dolphin_harness import Overlay  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "overlay-tmtest"
WORK = ROOT / "build" / "tmtest"
OWNER_CARD = Path.home() / ".local/share/dolphin-emu/GC/USA/Card A"

MAGIC = 0x544D5453
MAX_INPUTS = 128
MAX_OPTIONS = 16

CKIND = {"falcon": 0, "captain-falcon": 0, "dk": 1, "fox": 2, "gnw": 3,
         "kirby": 4, "bowser": 5, "link": 6, "luigi": 7, "mario": 8,
         "marth": 9, "mewtwo": 10, "ness": 11, "peach": 12, "pikachu": 13,
         "ics": 14, "ice-climbers": 14, "jigglypuff": 15, "puff": 15,
         "samus": 16, "yoshi": 17, "zelda": 18, "sheik": 19, "falco": 20,
         "young-link": 21, "dr-mario": 22, "roy": 23, "pichu": 24,
         "ganondorf": 25}
STAGE = {"fod": 2, "stadium": 3, "ps": 3, "yoshis": 8, "dreamland": 28,
         "battlefield": 31, "bf": 31, "fd": 32, "final-destination": 32}
BUTTON = {"A": 0x100, "B": 0x200, "X": 0x400, "Y": 0x800, "START": 0x1000,
          "Z": 0x10, "R": 0x20, "L": 0x40, "DLEFT": 1, "DRIGHT": 2,
          "DDOWN": 4, "DUP": 8}
# Common action states (decomp src/melee/ft/kinds/ftCommon/forward.h order).
STATE = {"Wait": 0x0E, "KneeBend": 0x18, "Landing": 0x2A,
         "LandingFallSpecial": 0x2B, "AttackHi4": 0x3F, "GuardOn": 0xB2,
         "Guard": 0xB3, "GuardOff": 0xB4, "GuardSetOff": 0xB5,
         "GuardReflect": 0xB6, "EscapeAir": 0xEC,
         "ShineGround": 0x168, "ShineAir": 0x16D}

TRIGGER = {"at": 0, "on_enter": 1, "on_exit": 2}
WINDOW_OK = False  # --window: allow a visible Dolphin when xvfb-run is missing


def build():
    env = dict(os.environ, OVERLAY_OUT=str(OUT.relative_to(ROOT)), TM_TEST="1")
    r = subprocess.run([sys.executable, "tools/overlay_build.py"], cwd=ROOT, env=env,
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)


def ident(table, v, what):
    if isinstance(v, int):
        return v
    if v is None:
        return None
    key = str(v).lower() if table is not STATE else str(v)
    if key not in table:
        sys.exit(f"unknown {what} {v!r}; known: {', '.join(table)}")
    return table[key]


def pack_config(spec):
    """TmTestConfig, big-endian (src/melee/tm/test/tmtest.h)."""
    ev = spec["event"].encode()[:15]
    hmn = ident(CKIND, spec.get("hmn"), "character")
    cpu = ident(CKIND, spec.get("cpu"), "character")
    stage = ident(STAGE, spec.get("stage"), "stage")
    out = struct.pack(">I16sBBBBHHII", MAGIC, ev,
                      0xFF if hmn is None else hmn, spec.get("hmn_color", 0),
                      0xFF if cpu is None else cpu, spec.get("cpu_color", 0),
                      0xFFFF if stage is None else stage, spec.get("trace", 0),
                      spec.get("seed", 1), spec.get("max_frames", 600))
    opts = spec.get("options", [])[:MAX_OPTIONS]
    out += struct.pack(">I", len(opts))
    for i in range(MAX_OPTIONS):
        idx, val = opts[i] if i < len(opts) else (0, 0)
        out += struct.pack(">BBh", idx, 0, val)
    inputs = spec.get("inputs", [])[:MAX_INPUTS]
    out += struct.pack(">I", len(inputs))
    for i in range(MAX_INPUTS):
        if i >= len(inputs):
            out += bytes(16)
            continue
        e = inputs[i]
        if "at" in e:
            trig, port, state, frame = 0, 0, 0, e["at"]
        else:
            kind = "on_enter" if "on_enter" in e else "on_exit"
            trig = TRIGGER[kind]
            port = e[kind].get("port", 0)
            state = ident(STATE, e[kind]["state"], "state")
            frame = e.get("delay", 0)
        buttons = 0
        for b in e.get("buttons", []):
            buttons |= BUTTON[b.upper()]
        lx, ly = e.get("stick", [0, 0])
        cx, cy = e.get("cstick", [0, 0])
        out += struct.pack(">BBHHHHbbbbBB", trig, port, state, frame, e.get("hold", 1),
                           buttons, lx, ly, cx, cy, e.get("l", 0), e.get("r", 0))
    return out


def dol_offset(dol, addr):
    h = struct.unpack(">57I", dol[:0xE4])
    for i in range(18):
        if h[36 + i] and h[18 + i] <= addr < h[18 + i] + h[36 + i]:
            return h[i] + addr - h[18 + i]
    sys.exit(f"{addr:08x} not in the DOL")


def prepare_disc(spec):
    disc = WORK / "disc"
    if not disc.exists():
        WORK.mkdir(parents=True, exist_ok=True)
        subprocess.run(["cp", "-al", str(ROOT / "build/disc"), str(disc)], check=True)
        subprocess.run([sys.executable, "tools/tmce_disc.py", "--disc", str(disc),
                        "--dol", str(OUT / "main.dol")], cwd=ROOT, check=True,
                       capture_output=True)
    dol = bytearray((OUT / "main.dol").read_bytes())
    addr = Overlay(OUT / "overlay.map").addr("tm_test_config")
    blob = pack_config(spec)
    off = dol_offset(dol, addr)
    dol[off : off + len(blob)] = blob
    target = disc / "sys" / "main.dol"
    target.unlink(missing_ok=True)  # never write through a hard link
    target.write_bytes(dol)
    return target


def prepare_user():
    user = WORK / "user"
    (user / "Config").mkdir(parents=True, exist_ok=True)
    card = user / "GC" / "USA" / "Card A"
    if not card.exists() and OWNER_CARD.exists():
        shutil.copytree(OWNER_CARD, card)
    (user / "Config" / "Logger.ini").write_text(
        "[Logs]\nOSREPORT = True\nOSREPORT_HLE = True\n"
        "[Options]\nWriteToFile = True\nWriteToConsole = False\nVerbosity = 4\n")
    log = user / "Logs" / "dolphin.log"
    if log.exists():
        log.unlink()
    return user, log


def resolve_exact(spec, timeout):
    """Turn {"on_exit"/"on_enter": ..., "exact": true} inputs into absolute
    frames. A state trigger can only react on the frame after it sees the
    change (one frame late, like a human reaction); for frame-perfect
    scripts, a traced dry run finds the frame the change really happened
    (runs are deterministic) and the input is placed there; "occurrence": N
    in the trigger picks the Nth change (default 1). Exact inputs
    are resolved in order, one dry run per distinct trigger, each run
    including the inputs already placed, so a later trigger can depend on
    what an earlier exact input caused."""
    inputs = list(spec.get("inputs", []))
    while True:
        pending = [k for k, e in enumerate(inputs) if e.get("exact")]
        if not pending:
            return dict(spec, inputs=inputs)
        first = inputs[pending[0]]
        kind = "on_enter" if "on_enter" in first else "on_exit"
        key = (kind, first[kind].get("port", 0), first[kind]["state"],
               first[kind].get("occurrence", 1))
        group = [k for k in pending
                 if kind in inputs[k] and
                 (kind, inputs[k][kind].get("port", 0), inputs[k][kind]["state"],
                  inputs[k][kind].get("occurrence", 1)) == key]
        # Dry run: everything resolved or not exact, up to this trigger.
        dry_inputs = [e for e in inputs if not e.get("exact")]
        dry = dict(spec, trace=1, inputs=dry_inputs)
        res = run(dry, timeout)
        frames = [r for r in res["records"] if "p" in r]
        port, state, nth = key[1], ident(STATE, key[2], "state"), key[3]
        hit = None
        for a, b in zip(frames, frames[1:]):
            if port >= len(a["p"]) or port >= len(b["p"]):
                continue
            was, now = a["p"][port]["st"], b["p"][port]["st"]
            if (kind == "on_exit" and was == state and now != state) or \
               (kind == "on_enter" and was != state and now == state):
                nth -= 1
                if nth == 0:
                    hit = b["f"] - 1  # trace frame f shows the end of frame f-1
                    break
        if hit is None:
            raise ValueError(f"exact input: {kind} {first[kind]} never happened in the "
                             f"dry run (results: {[r for r in res['records'] if 'result' in r][:3]})")
        for k in group:
            e = inputs[k]
            fixed = {x: v for x, v in e.items() if x not in ("exact", kind, "delay")}
            fixed["at"] = hit + e.get("delay", 0)
            inputs[k] = fixed


def run(spec, timeout=180, keep_log=False):
    dol = prepare_disc(spec)
    user, log = prepare_user()
    # Qt's offscreen platform stops Dolphin from booting; a virtual X
    # server (xvfb-run, package xorg-server-xvfb) hides the window if present.
    env = dict(os.environ)
    wrap = ["xvfb-run", "-a"] if shutil.which("xvfb-run") else []
    if not wrap and not WINDOW_OK:
        sys.exit("xvfb-run not found: a visible Dolphin window would steal the "
                 "desktop's focus. Install xorg-server-xvfb, run specs in the "
                 "simulator (tools/melee_sim/tmtest_sim.py), or pass --window.")
    cmd = wrap + ["dolphin-emu", "-u", str(user), "-b", "-v", "Null",
           "-C", "Dolphin.Interface.UsePanicHandlers=False",
           "-C", "Dolphin.Interface.ConfirmStop=False",
           "-C", "Dolphin.Core.EmulationSpeed=0",
           "-C", "Dolphin.DSP.Backend=No Audio Output",
           "-C", "Dolphin.Core.SIDevice0=6",
           "-e", str(dol)]
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    records, other, pos = [], [], 0
    started = time.time()
    status = "timeout"
    try:
        while time.time() - started < timeout:
            if proc.poll() is not None:
                status = "dolphin exited"
                break
            if log.exists():
                with open(log, errors="replace") as f:
                    f.seek(pos)
                    chunk = f.read()
                    pos = f.tell()
                for line in chunk.splitlines():
                    if "[OSREPORT]" not in line:
                        continue
                    text = line.split("[OSREPORT]:", 1)[-1].strip()
                    if text.startswith("TMTEST "):
                        try:
                            records.append(json.loads(text[7:]))
                        except json.JSONDecodeError:
                            records.append({"bad_json": text[7:]})
                    elif text:
                        other.append(text)
                if any(r.get("done") for r in records):
                    status = "done"
                    break
                if any("assertion" in t or "CAUTION" in t or "panic" in t.lower()
                       for t in other):
                    status = "crash"
                    time.sleep(0.5)
                    break
            time.sleep(0.1)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
    result = {"status": status, "seconds": round(time.time() - started, 1),
              "records": records}
    if status != "done":
        result["log_tail"] = other[-25:]
    if keep_log:
        result["log"] = str(log)
    return result


STATE_NAME = {v: k for k, v in STATE.items()}


def print_states(res):
    """One line per change: frame, then per fighter state (name), x, y."""
    prev = None
    for r in res["records"]:
        if "p" not in r:
            if "result" in r or "match" in r:
                print("   ", json.dumps(r))
            continue
        st = tuple(p["st"] for p in r["p"])
        if st == prev:
            continue
        prev = st
        cols = [f"{p['st']:#05x} {STATE_NAME.get(p['st'], ''):<18s} x{p['x']:7.1f} y{p['y']:6.1f}"
                for p in r["p"]]
        print(f"  f{r['f']:4d}  " + " | ".join(cols))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("spec", nargs="+", type=Path)
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--json", action="store_true", help="print full results as JSON")
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--keep-log", action="store_true")
    ap.add_argument("--states", action="store_true",
                    help="trace every frame and print each fighter's state changes")
    ap.add_argument("--window", action="store_true",
                    help="allow a visible Dolphin window if xvfb-run is missing")
    args = ap.parse_args()
    global WINDOW_OK
    WINDOW_OK = args.window
    if not args.no_build:
        build()
    failed = 0
    for path in args.spec:
        try:
            spec = resolve_exact(json.loads(path.read_text()), args.timeout)
        except ValueError as e:
            print(f"{path.name}: SETUP FAILED: {e}")
            failed += 1
            continue
        if args.states:
            spec = dict(spec, trace=1)
        res = run(spec, args.timeout, args.keep_log)
        res["spec"] = str(path)
        if args.states:
            print_states(res)
        if args.json:
            print(json.dumps(res))
            continue
        results = [r for r in res["records"] if "result" in r]
        print(f"{path.name}: {res['status']} in {res['seconds']}s, "
              f"{len(res['records'])} records")
        for r in results:
            print("  ", json.dumps(r))
        # "expect": fields of the FIRST event result record ("event_result"
        # is its "result" field).
        expect = dict(spec.get("expect", {}))
        if "event_result" in expect:
            expect["result"] = expect.pop("event_result")
        first = results[0] if results else {}
        wrong = {k: (v, first.get(k)) for k, v in expect.items() if first.get(k) != v}
        if wrong:
            print("   EXPECTED (want, got):", wrong)
        if res["status"] != "done" or wrong:
            failed += 1
            for t in res.get("log_tail", []):
                print("   log:", t)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
