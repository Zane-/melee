#!/bin/sh
# Build Aurora, with Dawn (WebGPU) and SDL3 from source, as 32-bit x86, for
# the native build's window (docs/ai/native-ai.md, "The window").
#
#   tools/aurora32/build.sh            # into build/aurora32/build
#
# Prebuilt Dawn exists for 64-bit Linux only and the game is a 32-bit
# process, so Dawn is built here. RmlUi (the menus' HTML-and-CSS-like UI
# library) is switched on. First time: fetches Dawn, SDL3 and RmlUi (about
# 1.8 GB of build tree, 2.5 minutes at -j 10). Runs niced; nothing opens a
# window.
set -e
root=$(cd "$(dirname "$0")/../.." && pwd)
out="$root/build/aurora32"
src="$out/aurora-src"
jobs=${JOBS:-10}

mkdir -p "$out"
[ -d "$src" ] || cp -r "$root/build/deps/aurora" "$src"

# Aurora draws its RmlUi layer over the game's picture only, and centres
# that picture. The client wants the layer over the whole 16:9 window with
# the 4:3 game at the left of it (aurora_set_ui_full_window).
if ! grep -q aurora_set_ui_full_window "$src/include/aurora/aurora.h"; then
    patch -d "$src" -p1 < "$root/tools/aurora32/aurora-0001-ui-full-window.patch"
fi

configure() {
    nice -n 15 cmake -S "$src" -B "$out/build" -G Ninja \
        -DCMAKE_TOOLCHAIN_FILE="$root/tools/aurora32/i686-linux-gcc.cmake" \
        -DCMAKE_BUILD_TYPE=Release \
        -DAURORA_DAWN_PROVIDER=vendor -DAURORA_SDL3_PROVIDER=vendor \
        -DAURORA_ENABLE_DVD=OFF -DAURORA_ENABLE_CARD=OFF \
        -DAURORA_ENABLE_RMLUI=ON \
        -DDAWN_USE_GLFW=OFF -DDAWN_BUILD_PROTOBUF=OFF \
        -DTINT_BUILD_IR_BINARY=OFF
}
# DAWN_USE_GLFW=OFF is required: GLFW's Wayland support needs a 32-bit
# xkbcommon, and Dawn's CMake turns GLFW back on whatever Aurora asked for.
configure

# One line of Dawn does not compile for 32-bit: there a raw Vulkan handle is
# a uint64_t, and Dawn's VK_NULL_HANDLE is a nullptr_t.
dawn="$out/build/_deps/dawn-src"
if ! grep -q "dedicatedInfo.buffer = {};" \
        "$dawn/src/dawn/native/vulkan/ResourceMemoryAllocatorVk.cpp"; then
    patch -d "$dawn" -p1 < "$root/tools/aurora32/dawn-0001-vk-null-handle-32bit.patch"
fi

nice -n 15 ninja -C "$out/build" -j "$jobs"
echo "built: $out/build (libaurora_*.a, _deps/dawn-build, _deps/sdl-build)"
