#!/usr/bin/env python3
"""Run the AddressSanitizer build and list the distinct bad accesses.

    python tools/native_build.py --asan
    python tools/melee_native/asan.py --match 2,9,32 --frames 600
    python tools/melee_native/asan.py --control < inputs.txt

Arguments go to build/native-asan/melee_headless. What it finds, mostly:
reads past the end of converted archive data (an array whose count the
readers were not told: heap-buffer-overflow) and globals reached through
their neighbours (global-buffer-overflow). One line per place in the source,
with how often it happened and what the address belonged to.
"""
import os
import re
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXE = ROOT / "build/native-asan/melee_headless"


def main():
    if not EXE.exists():
        sys.exit("build it first: python tools/native_build.py --asan")
    env = dict(os.environ, ASAN_OPTIONS="halt_on_error=0:detect_leaks=0:"
               "detect_stack_use_after_return=0:print_legend=0")
    r = subprocess.run([str(EXE)] + sys.argv[1:], cwd=ROOT, env=env,
                       stdin=sys.stdin, capture_output=True, text=True,
                       errors="replace")
    sites = OrderedDict()
    for report in r.stderr.split("=" * 65)[1:]:
        kind = re.search(r"AddressSanitizer: (\S+)", report)
        if not kind:
            continue
        access = re.search(r"^(READ|WRITE) of size (\d+)", report, re.M)
        frames = []
        for m in re.finditer(r"#\d+ \S+ in (\S+) (\S+?):(\d+)", report):
            if "/src/" in m.group(2) or "/build/native" in m.group(2):
                frames.append("%s:%s %s" % (
                    m.group(2).replace(str(ROOT) + "/", ""), m.group(3),
                    m.group(1)))
        frame = " <- ".join(frames[:3]) if frames else None
        where = re.search(r"^0x\w+ is located (.*)$", report, re.M)
        key = (kind.group(1), frame)
        if key not in sites:
            sites[key] = [0, access.group(0) if access else "",
                          where.group(1)[:150] if where else ""]
        sites[key][0] += 1
    for (kind, frame), (count, access, where) in sites.items():
        print("%5d  %s  %s\n       %s; %s" % (count, kind, frame, access,
                                              where))
    tail = [l for l in r.stderr.splitlines() if l.startswith("[host]")]
    print("%d distinct places; the game: %s" % (
        len(sites), tail[-1] if tail else "exit %d" % r.returncode))


if __name__ == "__main__":
    main()
