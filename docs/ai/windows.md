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
| `/dev/bus/usb` GameCube adapter (`gcadapter.c`) | not ported | no adapter |

## Status

- Matching build: verified on Windows (SHA-1 match).
- DWARF ELF, `melee-dat`, `types.bin`: built on Windows.
- `libmelee.a` and the readers: compile with MinGW, no errors.
- `melee_headless.exe`: links statically (runs without MSYS2 on PATH), boots
  600 frames, and plays a match (`--match 2,9,32 --trace 60`: Fox lands on
  Final Destination and waits, Marth likewise), 2026-11-17. Not yet compared
  against the console's code.

Next, in order: `tools/melee_native/native.py` on Windows (it uses
`libc.so.6`'s prctl, `preexec_fn`, `select()` on a pipe and `os.killpg`, all
Linux-only), then `compare.py` against the console's code (needs `unicorn`
and `numpy`); the window build (Aurora on
Windows, `tools/aurora32/build.sh` has a Linux-only script); the Python
client; snapshots without `fork()` (copies of the state inside the process,
once the statics are gathered); rollback; the adapter over WinUSB.
