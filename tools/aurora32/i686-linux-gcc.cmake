# 32-bit x86 Linux on a multilib x86_64 host (Arch/CachyOS layout: /usr/lib32).
# The binaries run on this machine, so this is not treated as cross-compiling.
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR i686)
set(CMAKE_CROSSCOMPILING FALSE)

set(CMAKE_C_COMPILER gcc)
set(CMAKE_CXX_COMPILER g++)
set(CMAKE_C_FLAGS_INIT "-m32")
set(CMAKE_CXX_FLAGS_INIT "-m32")
set(CMAKE_EXE_LINKER_FLAGS_INIT "-m32")
set(CMAKE_SHARED_LINKER_FLAGS_INIT "-m32")
set(CMAKE_MODULE_LINKER_FLAGS_INIT "-m32")

# Find 32-bit libraries and their pkg-config files, never the 64-bit ones.
set(CMAKE_LIBRARY_PATH /usr/lib32)
set(ENV{PKG_CONFIG_LIBDIR} "/usr/lib32/pkgconfig:/usr/share/pkgconfig")
