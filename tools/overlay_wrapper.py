"""Pick the command prefix that runs the Windows compiler tools on this host.

Shared by tools/overlay_build.py and tools/overlay_link.py.

- macOS: tools/wibo_macos_wrapper.py (wibo-macos, with its own Shift JIS
  handling because sjiswrap.exe does not load there).
- Linux: build/tools/wibo, downloaded by the normal ninja build.
- Windows: the tools run directly.

Set MELEE_WRAPPER to override (a path, or an empty string for none).
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SJISWRAP = "build/tools/sjiswrap.exe"


def wrapper():
    """Returns the wrapper as a list of leading arguments (possibly empty)."""
    env = os.environ.get("MELEE_WRAPPER")
    if env is not None:
        return [env] if env else []
    if sys.platform == "darwin":
        return ["tools/wibo_macos_wrapper.py"]
    if os.name == "nt":
        return []
    wibo = ROOT / "build" / "tools" / "wibo"
    if wibo.exists():
        return [str(wibo.relative_to(ROOT))]
    return ["wine"]


def compiler_prefix():
    """Wrapper plus sjiswrap, for compiling UTF-8 sources as Shift JIS."""
    return [*wrapper(), SJISWRAP]
