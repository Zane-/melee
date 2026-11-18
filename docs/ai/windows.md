# The native build on Windows

Started 2026-11-17 on branch `port/windows-native`. The native build
(`docs/ai/native-port.md`) was Linux-only; this is the same build with
MSYS2's 32-bit MinGW-w64 gcc, no WSL and no Nix. What works and what does
not yet is under "Status".

## Setup (once)

| Need | How |
|-|-|
| Git | `winget install --id Git.Git -e` |
| Python 3 | any recent CPython on PATH (3.14 used) |
| MSYS2 | `winget install --id MSYS2.MSYS2 -e`, then in its shell `pacman -Syu` (twice) |
| 32-bit gcc, cmake, ninja | `pacman -S mingw-w64-i686-gcc mingw-w64-i686-cmake mingw-w64-i686-ninja` |
| clang/lld for the DWARF build, Rust for the archive tool | `pacman -S mingw-w64-x86_64-clang mingw-w64-x86_64-lld mingw-w64-x86_64-llvm mingw-w64-x86_64-rust` |
| Your own Melee NTSC 1.02 image | extracted below |

In PowerShell, from the repository:

```powershell
python -m venv .venv; .venv\Scripts\pip install ninja
.venv\Scripts\python configure.py --ninja .venv\Scripts\ninja.exe
.venv\Scripts\ninja build\tools\dtk.exe
build\tools\dtk.exe disc extract <your.iso> orig\GALE01
.venv\Scripts\ninja                       # matching build: must print the SHA-1 match
```

The matching build needs no wrapper on Windows: the Metrowerks compiler and
`sjiswrap` are Windows programs. Verified 2026-11-17: SHA-1
`08e0bf20134dfcb260699671004527b2d6bb1a45`, 1,133 of 1,133 files.

The type table (what Nix's `melee-dwarf` and `melee-dat` give on Linux):

```powershell
git clone https://github.com/r-burns/aurora build\deps\aurora
git -C build\deps\aurora checkout e6a6f02ace4146e8a2f648d5c274dbb7dd89665c
# newlib's headers for powerpc-none-eabi, from its source release
#   https://sourceware.org/pub/newlib/newlib-4.5.0.20241231.tar.gz
#   unpacked into build\deps\newlib-src
.venv\Scripts\python tools\windows\newlib_headers.py build\deps\newlib-src\newlib-4.5.0.20241231 build\deps\newlib-ppc\include

$env:PATH = "C:\msys64\mingw64\bin;C:\msys64\mingw32\bin;$env:PATH"
$env:AURORA_SRC = "$PWD\build\deps\aurora"
$env:NEWLIB_INCLUDE = "$PWD\build\deps\newlib-ppc\include"
cmake --preset ppc-dwarf -B build\dwarf "-DCMAKE_C_FLAGS=-Wno-error=incompatible-function-pointer-types"
cmake --build build\dwarf                 # build\dwarf\melee.elf

$env:CARGO_TARGET_DIR = "$PWD\build\cargo"
cargo build --release -p melee-dat        # build\cargo\release\melee-dat.exe
build\cargo\release\melee-dat.exe types export -o build\GALE01\dat\types.bin --dwarf build\dwarf\melee.elf
```

The `-Wno-error` flag is the same workaround as on Linux (`native-port.md`).

## Building

```powershell
$env:PATH = "C:\msys64\mingw32\bin;$env:PATH"
$env:AURORA_SRC = "$PWD\build\deps\aurora"
.venv\Scripts\python tools\native_build.py   # build\native\melee_headless.exe
build\native\melee_headless.exe --disc orig/GALE01 --frames 600
```

`native_build.py` notices Windows by itself (`WIN32`): the toolchain file
`cmake/i686-mingw.cmake`, the archive tool from `build/cargo`, the stand-ins
in `src/host/win32/`, Winsock, and these link options:

- `--large-address-aware`: the arena lives at the console's addresses
  (`0x80000000` and up, `os.c`), above 2 GB; a 32-bit program gets them only
  when large address aware, on 64-bit Windows.
- `--disable-dynamicbase`: no ASLR, as `-no-pie` on Linux.
- `-DDECL_WEAK=` on every compile: Aurora's headers declare `OSReport`,
  `OSPanic` and others weak. The PE linker leaves a weak definition's
  references at address 0; the game called 0 at its first `OSReport`.

## What differs from Linux (src/host/win32/)

| Linux | Windows | Effect |
|-|-|-|
| `mmap`, `mprotect` | `VirtualAlloc`, `VirtualProtect` (`compat.c`) | none |
| `ucontext` coroutines (`engine.c`'s search) | fibers (`compat.c`) | none intended; not yet exercised |
| sockets (`net.c`) | Winsock, in `net.c` behind `_WIN32` | none |
| `sigaction` crash handler (`main.c`) | unhandled-exception filter (`compat.c`); prints the faulting instruction and callers for `addr2line` | none |
| stdout line-buffered | unbuffered (Windows' C library has no line buffering) | none for readers of lines |
| `fork()` snapshots (`control.c`), engine forks (`engine.c`) | `fork()` fails (`posix.h`) | **`snap`/`restore` and `engine fork` answer with an error** |
| linker script gathering the game's statics (`state.c`) | none: the region is empty (`compat.c`) | **in-process snapshots miss the statics; rollback is off** |
| `/proc/self/pagemap` dirty-page tracking (`rollback.c`) | none | **netplay does not start** |
| `/dev/bus/usb` GameCube adapter (`gcadapter.c`) | WinUSB (`win32/winusb_adapter.c`), window build only; needs Zadig's WinUSB driver, as Dolphin does | the same reader, decoding and rumble; played with a Lossless adapter (Wii U mode) and a PhobGCC, 2026-11-17 |

## Status

- Matching build: verified on Windows (SHA-1 match).
- DWARF ELF, `melee-dat`, `types.bin`: built on Windows.
- `libmelee.a` and the readers: compile with MinGW, no errors.
- `melee_headless.exe`: links statically (runs without MSYS2 on PATH), boots
  600 frames, and plays a match (`--match 2,9,32 --trace 60`: Fox lands on
  Final Destination and waits, Marth likewise), 2026-11-17.
- `tools/melee_native/native.py` drives it (2026-11-17): a reader thread in
  place of `select()` on the pipe, a job object in place of `prctl`'s
  death signal, no process group. The game's stdout and stderr are binary
  on Windows (`main.c`), so replies end in `\n` as on Linux.
- Against the console's code, `compare.py --tolerance 1e-4` (the scripted
  exchange and `--random 3`): identical for 520 frames in all four, the
  same result as on Linux. Without the tolerance the scripted exchange
  differs at frame 152 in the last bit of a speed (2.0199999809 /
  2.01999974), as `native-port.md` describes for Linux (130 to 200 frames).
  Needs `pip install unicorn numpy` and the disc copied to `build/disc`
  (`robocopy orig\GALE01 build\disc /E`; a link would let tools that write
  there change the clean extraction).

## The window build (graphics and sound)

```powershell
$env:PATH = "C:\msys64\mingw32\bin;$env:ProgramFiles\Git\cmd;$env:PATH"
python tools\aurora32\build_windows.py       # Aurora, Dawn, SDL3, RmlUi: build\aurora32\build
python tools\native_build.py --window        # build\native-window\melee_native.exe (+ its DLLs)
build\native-window\melee_native.exe --disc build/disc --match 2,9,32 --frames 600
```

`build_windows.py` is `build.sh`'s counterpart (also needs `pacman -S patch`):
the same two Aurora patches and Dawn patch, and for MinGW:

- Dawn with **Vulkan only** (`DAWN_ENABLE_D3D11/D3D12=OFF`,
  `DAWN_USE_WINDOWS_UI=OFF`): its Direct3D code needs headers MinGW lacks
  (`DXProgrammableCapture.h`, WRL). Vulkan comes with the graphics driver,
  and is what Linux uses.
- `abseil-0001-mingw-o-nonblock.patch`: MinGW has no `O_NONBLOCK`.
- `aurora-0003-mingw-comsuppw.patch`: `comsuppw` is MSVC's library.
- Only the libraries the game links are built: Aurora's example wants a
  `WinMain` under MinGW.

What the window build needed on Windows:

- **16-byte-aligned `operator new`** (`src/host/win32/aligned_new.cpp`):
  32-bit MinGW's `malloc` aligns to 8, gcc assumed 16, and Aurora's
  `std::deque<RenderPass>` was zeroed with `movaps` into 8-aligned memory: an
  access violation "at 0xFFFFFFFF" on the third frame. (That address is how
  Windows reports a misaligned SSE access.)
- **`aurora_shutdown()` at exit** (`window.c`, Windows only): left to the C++
  statics, the device went first and Aurora aborted (exit status 3).
- **The DLLs beside the executable** (`native_build.py`, `copy_dlls`): Dawn
  and SDL3 are DLLs, and RmlUi's image and compression libraries are MSYS2's.
- SQLite's header from Aurora's copy; `gcadapter.c`'s USB reading is
  Linux-only (no GameCube adapter on Windows yet; keyboard and SDL
  controllers are the window's own).

Verified 2026-11-17: `--match 2,9,32 --frames 600` runs in a window on
Vulkan (RTX 5090) and exits 0. Not yet checked: what the picture looks
like, sound, input, the Python client on top.

## The GameCube adapter

Nintendo's adapter, or one in its mode ("Wii U mode": USB `057e:0337`), is
read as on Linux, through WinUSB (`src/host/win32/winusb_adapter.c`): found
among the devices offering the generic USB device interface, as libusb finds
it, then opened directly (the adapter has one interface). Setup is Dolphin's:
[Zadig](https://zadig.akeo.ie/) gives the adapter the WinUSB driver once.
While Dolphin has it open, the game cannot, and the other way round.
`client.py --devices` says what the reader sees: "no adapter is plugged
in", "in use by another program", "needs the WinUSB driver", or "open" with
the ports that have controllers. Checked 2026-11-17 with a Lossless adapter
in Wii U mode (shown by Windows as "Lossless adapter [WiiU/NS]", already on
WinUSB) and a PhobGCC on port 1: about 1,000 reports a second, no failed
reads, the newest at most 1 ms old when read; the owner played the client
with it (`client.py --input gcc1`). The keyboard works in the client too
(`--input keyboard`; with an adapter controller plugged in, `auto` takes
that instead). Rumble not yet tried.

## The client

```powershell
.venv\Scripts\pip install numpy pillow
.venv\Scripts\python tools\melee_client\client.py      # F11: fullscreen
```

Verified 2026-11-17: `client.py --devices` and `client.py --windowed
--frames 600` run (the first-time art, 425 files in `build\ui`, comes off
the disc as on Linux) and exit cleanly. On Windows:

- `client.py` restarts itself in Python's UTF-8 mode (the data files are
  UTF-8), as `native_build.py` does.
- `window.py`: the `.exe`; `Window(real=False)` (tests, `--devices`) opens
  an ordinary window, silent, with its own shader cache, since there is no
  Xvfb; `leftovers()` finds none (the job object ends a driver's games).
- **Not on Windows yet:** stage previews and Sheik's portraits (drawn on a
  virtual display and photographed with `window.shot`; the panels keep the
  name logos and her emblem), the tests that press keys or take pictures
  (`key()`, `shot()`, `close_window()`), snapshots
  (and so TM-CE-style instant resets), netplay, the trained-model opponent
  (`opponents.py` still uses `select()` on a pipe and `os.killpg`).

Next, in order: the picture, sound and input checked by a person; snapshots without `fork()` (copies of the state inside the process,
once the statics are gathered); rollback; the adapter over WinUSB.
