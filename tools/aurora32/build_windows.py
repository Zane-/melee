#!/usr/bin/env python3
"""Build Aurora, with Dawn (WebGPU) and SDL3 from source, as 32-bit x86 on
Windows, for the native build's window. The Windows counterpart of
build.sh (same patches, same options, same output directory):

    python tools/aurora32/build_windows.py      # into build/aurora32/build

Needs MSYS2's i686 MinGW gcc, cmake and ninja on PATH
(C:\\msys64\\mingw32\\bin), MSYS2's GNU patch (pacman -S patch), and Git
(Dawn fetches its dependencies with it).
No prebuilt Dawn exists for 32-bit Windows. See docs/ai/windows.md.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "build/aurora32"
SRC = OUT / "aurora-src"
HERE = ROOT / "tools/aurora32"
JOBS = os.environ.get("JOBS", str(os.cpu_count() or 8))


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


# GNU patch, as build.sh uses (pacman -S patch). Not `git apply`: build/ is
# inside this repository, so git takes a patch's paths from the repository's
# root; and Git for Windows checks the .patch files out with CRLF line ends,
# which GNU patch strips by itself.
PATCH = os.environ.get("PATCH", r"C:\msys64\usr\bin\patch.exe")


def patch_tree(tree, patch):
    run([PATCH, "-d", tree, "-p1", "-i", patch])


def apply_patch(tree, patch, marker_file, marker):
    """Apply a -p1 patch once: skipped when `marker` is already in the
    patched file."""
    if marker in (tree / marker_file).read_text(encoding="utf-8",
                                                 errors="replace"):
        return
    patch_tree(tree, patch)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if not SRC.exists():
        shutil.copytree(ROOT / "build/deps/aurora", SRC,
                        ignore=shutil.ignore_patterns(".git"))

    # The same two Aurora patches as build.sh (what each does is there).
    patch = HERE / "aurora-0001-ui-full-window.patch"
    if "aurora_set_present_hold" not in (
            SRC / "include/aurora/aurora.h").read_text(encoding="utf-8"):
        # an older version of the patch may be in the tree: start again
        # from the files as they came
        for line in patch.read_text(encoding="utf-8").splitlines():
            if line.startswith("+++ b/"):
                rel = line[len("+++ b/"):]
                shutil.copy(ROOT / "build/deps/aurora" / rel, SRC / rel)
        patch_tree(SRC, patch)
    apply_patch(SRC, HERE / "aurora-0002-copy-views.patch",
                "lib/rmlui/WebGPURenderInterface.cpp",
                "aurora_rmlui_copy_view")
    # MinGW only: comsuppw is a library of MSVC's.
    apply_patch(SRC, HERE / "aurora-0003-mingw-comsuppw.patch",
                "cmake/aurora_core.cmake", "if (MSVC)")

    configure = [
        "cmake", "-S", SRC, "-B", OUT / "build", "-G", "Ninja",
        f"-DCMAKE_TOOLCHAIN_FILE={ROOT}/cmake/i686-mingw.cmake",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DAURORA_DAWN_PROVIDER=vendor", "-DAURORA_SDL3_PROVIDER=vendor",
        "-DAURORA_ENABLE_DVD=OFF", "-DAURORA_ENABLE_CARD=OFF",
        "-DAURORA_ENABLE_RMLUI=ON",
        "-DDAWN_USE_GLFW=OFF", "-DDAWN_BUILD_PROTOBUF=OFF",
        "-DTINT_BUILD_IR_BINARY=OFF",
        # Vulkan only, as on Linux: Dawn's Direct3D backends need headers
        # MinGW lacks (DXProgrammableCapture.h, WRL). Vulkan comes with the
        # graphics driver.
        "-DDAWN_ENABLE_D3D11=OFF", "-DDAWN_ENABLE_D3D12=OFF",
        # UWP/WinUI surfaces pull in the same Direct3D headers; SDL's window
        # is an ordinary HWND, which Dawn supports without them.
        "-DDAWN_USE_WINDOWS_UI=OFF",
        # Dawn fetches its own dependencies with this Python
        f"-DPython3_EXECUTABLE={sys.executable}",
    ]
    run(configure)

    # One line of Dawn does not compile for 32-bit (build.sh says why).
    dawn = OUT / "build/_deps/dawn-src"
    apply_patch(dawn, HERE / "dawn-0001-vk-null-handle-32bit.patch",
                "src/dawn/native/vulkan/ResourceMemoryAllocatorVk.cpp",
                "dedicatedInfo.buffer = {};")
    # MinGW only: Abseil (in Dawn) opens time zone files with O_NONBLOCK,
    # which MinGW does not define; MSVC takes another branch.
    apply_patch(dawn / "third_party/abseil-cpp",
                HERE / "abseil-0001-mingw-o-nonblock.patch",
                "absl/time/internal/cctz/src/time_zone_info.cc",
                "#define O_NONBLOCK 0")

    # The libraries the game links (what Aurora's example links, as
    # native_build.py's aurora_libs reads them), not the example itself:
    # under MinGW it wants a WinMain from libaurora_main, which the game
    # does not use (it has its own main).
    text = (OUT / "build/build.ninja").read_text(encoding="utf-8")
    at = text.index("build examples/simple")
    line = re.search(r"^  LINK_LIBRARIES = (.*)$", text[at:], re.M).group(1)
    build_dir = (OUT / "build").as_posix()
    targets = []
    for item in line.split():
        if item.startswith("-") or item.endswith("libaurora_main.a"):
            continue
        rel = item[len(build_dir) + 1:] if item.startswith(build_dir) \
            else item
        if not re.match(r"^[A-Za-z]:[/\\]|^/", rel):
            targets.append(rel)
    # -k 0 (KEEP_GOING=1): every failure in one run, for porting
    keep = ["-k", "0"] if os.environ.get("KEEP_GOING") else []
    run(["ninja", "-C", OUT / "build", "-j", JOBS, *keep, *targets])
    print(f"built: {OUT / 'build'} (libaurora_*.a, _deps/dawn-build, "
          "_deps/sdl-build)")


if __name__ == "__main__":
    main()
