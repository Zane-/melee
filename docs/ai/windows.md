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
| `ucontext` coroutines (`engine.c`'s search) | fibers (`compat.c`) | none (`tests/native/engine.py` 18 of 18) |
| sockets (`net.c`) | Winsock, in `net.c` behind `_WIN32` | none |
| `sigaction` crash handler (`main.c`) | unhandled-exception filter (`compat.c`); prints the faulting instruction and callers for `addr2line` | none |
| stdout line-buffered | unbuffered (Windows' C library has no line buffering) | none for readers of lines |
| `fork()` snapshots (`control.c`) | the whole state copied into a page-file section, outside the 32-bit address space (`compat.c` blobs) | none for the game's state; the host's own side goes on, as with `load` |
| `engine fork` (`engine.c`) | `engine fork-state` + another process of the program, `--fork-child NAME`, loaded at its first frame boundary (`tools/melee_engine/fork.py`) | none |
| linker script gathering the game's statics | `.data$gs*` section names, sorted by the PE linker (`native_build.py` `gather_win32`) | none |
| `/proc/self/pagemap` soft-dirty (`rollback.c`) | `MEM_WRITE_WATCH` / `GetWriteWatch` on the fixed mappings; the statics compared page by page with the mirror | none |
| `-mms-bitfields` (MinGW's default) | `-mno-ms-bitfields` | the Linux build's struct layout |
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
## Snapshots, rollback and the engine (branch `port/windows-snapshots`)

- **The statics** are gathered by section name (above). The block is about
  1.1 MB; `tests/native/state.py` 8 of 8.
- **Snapshots** (`snap`, `restore`, `drop`): each is the game's whole state
  (some 70 MB) in a page-file section of its own, mapped only while it is
  written or read, so many fit beside a 32-bit process.
- **Rollback** (`rollback.c`): Windows' write watching in place of
  soft-dirty. `tests/native/rollback.py` 6 of 6, `tests/native/netplay.py`
  11 of 11 (with lag, loss and jitter: no desync).
- **The game heap and audio RAM at fixed addresses** (`host.h`:
  `0x90000000`, `0xA0000000`), so that a forked game, another process, sees
  the same pointers. The scene loop's `on_frame` is kept in a global too
  (`native_build.py`, gmscene.c's patch): the child loads the state inside
  the boot scene's loop. The disc's file table (`dvd.c`) stays the child's
  own; audio RAM is copied up to the highest address the game reached.
  `tests/native/engine.py` 18 of 18.
- **Two bugs found on the way, both fixed:**
  - MinGW's default bitfield layout (`-mms-bitfields`) gave the game's
    structs another layout than on Linux (`engine.py`'s jab check read the
    fighter's flag at `0x2218` as 0).
  - `dvd.c`'s file table left four fields as the C heap held them, so a
    `.dat` file could be taken for words and byte-swapped (`EfMnData.dat`,
    only in some environments). Not Windows' alone: Linux happened to get
    zeroed memory. Found with the reads and parses `dvd.c` and `archive.c`
    now remember and print when an archive does not parse;
    `MELEE_WATCH_FILE=NAME` reports what writes over a file once read
    (`compat.c`; it makes the page read-only, so a later read into the same
    page fails: for debugging only).

## The window in tests (`tools/melee_native/win32ui.py`)

There is no virtual display: a test's window opens on the desktop.
`window.shot()` takes the window's client area from the screen (posting the
window to the top first; nothing is ever sent to it, since between frames
the game does not answer its window's messages: a sent `SetWindowPos` or
`PrintWindow` waited about two minutes). The process is DPI aware, so a
scaled display gives the window's real pixels. `key()` posts `WM_KEYDOWN`
and `WM_KEYUP` with scan codes; `close_window()` posts `WM_CLOSE`. Each
driver gets its own Aurora state directory (two games sharing the shader
cache found its database locked). The client tests compare pictures with
ImageMagick: `pacman -S mingw-w64-x86_64-imagemagick` and
`C:\msys64\mingw64\bin` on PATH.

Checked 2026-11-17: `tests/client/menu.py` 20 of 20, `tests/native/env.py`
11 of 11 (7,300 frames a second through the driver, a state each: the
game's stdout is fully buffered and flushed when it waits for a command; it
was unbuffered, and one write per `printf` gave 1,100).

A GameCube controller on the adapter wins over the keyboard for a port
whose source is `auto`, as tests' windows are: a controller touched during
a client test moves the menu too. Unplug it, or leave it alone, for tests.

### The client tests on Windows (2026-11-17)

Keys reach the game by the control protocol as well as the window
(`vkey 1|0 NAME`, `window.c`): a posted left Shift (the light push) never
reached SDL's state there, so a stand-in dashed where it meant to walk.
Each test game has its own Aurora state directory.

| Passing | |
|-|-|
| all checks | close 5, course 22, coach 10, menu 20, modes_format 20, online_lobby 8, online_modes 9, rules 14, settings_menu 55, shine_oos 11, short_hop 16, sound 12, versus_select 14, whiff_punish 13 |
| skipped, as on Linux (their drills not rebuilt yet) | between, loading, pausekeys |

| Not all passing | Why |
|-|-|
| controls 6 of 8, fullscreen 17 of 18, online 9 of 10 | checks that measure the window's picture (`window.shot` from the screen): not yet as exact as X's virtual display |
| versus_modes 44 of 45 | each Fox's stock icon in its costume: not looked into |
| stage_select 17 of 25, portraits | the stages' and Sheik's pictures, which the client draws on its first runs, were not there yet |
| input_display | the controller is made from a drawing that is not in the repository (`padart.py`); without it `toggle_column` ended the client: fixed, it now skips the controller |
| versus | needs a slippi-ai checkout with its models |
| vselkeys | not a test: keys for other tests |

## Not done on Windows yet

- **The trained-model opponent:** `opponents.py` is ported (reader thread,
  job object, `venv\Scripts\python.exe`) but untried: it needs a slippi-ai
  checkout with its models.
- **Rumble:** the shared code, untried with a controller.
- **Sheik's portraits and the stage previews** are drawn by the client's
  background jobs with `window.shot`, which works; a whole run of them has
  not been watched through.
- Most of `tests/client/` has not been run on Windows (only `menu.py`).
- `tests/native/place.py`'s "same placement after another past" compares
  the fall counter, which random play can raise (10 of 11).
