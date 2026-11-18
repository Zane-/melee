# The native build as 32-bit x86 on Windows, with MSYS2's i686 MinGW-w64 gcc
# (pacman -S mingw-w64-i686-gcc; C:\msys64\mingw32\bin on PATH). The Linux
# equivalent is i686-gcc.cmake; tools/native_build.py picks this one on
# Windows.
set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_SYSTEM_PROCESSOR i686)

set(CMAKE_C_COMPILER gcc)
set(CMAKE_CXX_COMPILER g++)
set(CMAKE_C_FLAGS_INIT -m32)
