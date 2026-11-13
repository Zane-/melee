"""Where may the game's code read a local variable it never assigned?

    python tools/native_uninit_warnings.py [--json FILE]

Compiles every game file once with gcc's uninitialised-variable warnings
(they need optimisation, so at -O1; nothing is linked) and lists the
places. Most are false alarms: the compiler cannot see that a loop always
runs. The ones that matter in play are found by running the game
(tests/native/uninit.py); this list is where to look when that test names
a file.
"""
import argparse
import collections
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import native_build as nb

flags = [f for f in nb.BASE_FLAGS if f not in ("-w", "-g")] + [
    "-O1", "-Wuninitialized", "-Wmaybe-uninitialized", "-fdiagnostics-color=never"]
common = flags + nb.DEFINES + nb.includes()
shim = ["-include", str(ROOT / "src/host/shim.h")]
files = [p for d in ("src/melee", "src/sysdolphin") for p in sorted((ROOT / d).rglob("*.c"))
         if "/melee/tm/" not in str(p)]

def one(src):
    for extra in ([], shim):
        r = subprocess.run(["gcc", "-c", "-o", "/dev/null", str(src)] + common + extra,
                           capture_output=True, text=True)
        if r.returncode == 0:
            break
    return src, r.returncode, r.stderr

ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
ap.add_argument("--json", help="write the places to this file")
ap.add_argument("--file", help="only list places in files whose path "
                               "contains this")
args = ap.parse_args()
os.environ["LC_ALL"] = "C"   # plain quotes in the compiler's messages
found, failed = [], []
with ThreadPoolExecutor(8) as ex:
    for src, code, err in ex.map(one, files):
        rel = str(src.relative_to(ROOT))
        if code:
            failed.append(rel)
            continue
        fn = None
        for line in err.splitlines():
            m = re.search(r"In function '(\w+)'", line)
            if m: fn = m.group(1)
            m = re.match(r"(.+?):(\d+):\d+: warning: '(.+?)' (is used uninitialized|may be used uninitialized)", line)
            if m and m.group(1).endswith(rel.split("/")[-1]):
                found.append(dict(file=rel, line=int(m.group(2)), function=fn, name=m.group(3),
                                  sure=m.group(4).startswith("is used")))
if args.json:
    json.dump(dict(found=found, failed=failed), open(args.json, "w"),
              indent=1)
if args.file:
    for f in found:
        if args.file in f["file"]:
            print("%s:%d  %s in %s" % (f["file"], f["line"], f["name"],
                                       f["function"]))
print("%d files, %d did not compile this way" % (len(files), len(failed)))
print("%d places: %d certain, %d possible, in %d files" % (
    len(found), sum(f["sure"] for f in found), sum(not f["sure"] for f in found),
    len({f["file"] for f in found})))
by = collections.Counter(f["file"].split("/")[2] if f["file"].startswith("src/melee") else "sysdolphin" for f in found)
print("by module:", dict(by.most_common(14)))
