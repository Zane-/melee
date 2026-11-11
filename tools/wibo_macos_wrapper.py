#!/usr/bin/env python3
"""Compiler wrapper for macOS: runs Windows tools through wibo-macos.

Use as `python configure.py --wrapper tools/wibo_macos_wrapper.py`.

Why this exists: the build runs `<wrapper> sjiswrap.exe mwcceppc.exe ...` so
that UTF-8 sources reach the compiler as Shift JIS. sjiswrap.exe does not load
under wibo-macos 1.2.0 (it needs kernel32 FormatMessageA, which wibo does not
provide). This wrapper drops sjiswrap.exe and does the same conversion itself:
when the source file contains non-ASCII bytes it compiles a Shift JIS copy
with the same file name from a scratch directory.

The compiler also is not Shift JIS lead-byte aware in this setup, so trail
bytes equal to a backslash are escaped (see to_sjis).

Only the source file given with `-c` is converted. Headers are passed through
unchanged, which is correct as long as no header has non-ASCII text outside
comments. The matching build's SHA-1 check verifies the result.

Requires Rosetta 2 (wibo-macos is x86_64) and build/tools/wibo-macos.
"""

import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIBO = ROOT / "build" / "tools" / "wibo-macos"
SCRATCH = ROOT / "build" / "sjis_tmp"


def to_sjis(text: str) -> bytes:
    """Encode as Shift JIS for a compiler that is not lead-byte aware.

    sjiswrap also makes the compiler treat Shift JIS lead bytes correctly.
    Without it, a double-byte character whose second byte is 0x5C (a
    backslash, e.g. the katakana "so") would be read as an escape. Doubling
    that backslash yields the same bytes in the compiled string.
    """
    out = bytearray()
    for ch in text:
        b = ch.encode("cp932")
        out += b
        if len(b) == 2 and b[1] == 0x5C:
            out += b"\\"
    return bytes(out)


def main():
    args = sys.argv[1:]
    if not WIBO.exists():
        sys.exit(f"{WIBO} not found; download wibo-macos from decompals/wibo")

    if args and args[0].lower().endswith("sjiswrap.exe"):
        args = args[1:]
        if "-c" in args:
            i = args.index("-c") + 1
            src = Path(args[i])
            data = src.read_bytes()
            if any(b > 0x7F for b in data):
                key = hashlib.sha1(str(src).encode()).hexdigest()[:12]
                out_dir = SCRATCH / key
                out_dir.mkdir(parents=True, exist_ok=True)
                out = out_dir / src.name
                out.write_bytes(to_sjis(data.decode("utf-8")))
                args[i] = os.path.relpath(out)
                # `-cwd source` resolves quoted includes next to the source
                # file, so keep the original directory on the search path.
                first_i = args.index("-i") if "-i" in args else i - 1
                args[first_i:first_i] = ["-i", str(src.parent)]

    os.execv(str(WIBO), [str(WIBO), *args])


if __name__ == "__main__":
    main()
