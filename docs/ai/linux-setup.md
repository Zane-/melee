# Setting up the native build on Linux without Nix (Steam Deck)

The native build (`native-port.md`) and its client (`native-ai.md`) on a
machine with no Nix and no system compiler: a Steam Deck on SteamOS, set up
2026-11-18. It is the same build as on the owner's desktop, with the
Windows recipe's way round Nix (`windows.md`): the type table from a clang
DWARF build and `melee-dat` from cargo. What was run on the Deck, and what
it showed, is under "Verified".

## The toolchain: an Arch container

SteamOS's root is read-only and an update wipes what pacman put on it, so
everything that builds lives in a distrobox (distrobox and podman ship with
SteamOS 3.5+). The game is a 32-bit process: it needs Arch's `multilib`
repository, which the container's `pacman.conf` has switched off.

```sh
distrobox create -n meleedev -i docker.io/library/archlinux:latest
distrobox enter meleedev
printf '\n[multilib]\nInclude = /etc/pacman.d/mirrorlist\n' | sudo tee -a /etc/pacman.conf
sudo pacman -Syu --needed base-devel git cmake ninja python patch wget unzip \
    clang lld llvm rust multilib-devel \
    lib32-gcc-libs lib32-glibc lib32-mesa lib32-vulkan-icd-loader \
    lib32-vulkan-radeon lib32-vulkan-swrast lib32-libx11 lib32-libxext \
    lib32-libxkbcommon lib32-libdecor lib32-libxcursor lib32-libxi \
    lib32-libxrandr lib32-libxss lib32-wayland lib32-libpulse lib32-alsa-lib \
    lib32-libusb libxss xorg-server-xvfb imagemagick
```

Every command below runs inside the container (`distrobox enter
meleedev`). The home directory is shared with the host, so the checkout,
`build/` and the models are the same files outside it. `lib32-libxss` (and
`libxss`) is needed by SDL3's configure (`SDL_X11_XSCRNSAVER`);
`lib32-vulkan-radeon` is the Deck's GPU driver (another GPU wants its own);
`lib32-vulkan-swrast` is the software Vulkan the tests can use.
`imagemagick` (its `import`) takes the pictures the client draws for
itself (portraits, Sheik, the stages: `window.shot`); without it, drawing
them fails on the first picture.

## The build, in order

```sh
# 1. The matching build (needs the retail 1.02 disc: orig/GALE01)
python3 -m venv .venv && .venv/bin/pip install ninja numpy
.venv/bin/python configure.py --ninja .venv/bin/ninja
.venv/bin/ninja build/tools/dtk
build/tools/dtk disc extract "<your 1.02 iso>" orig/GALE01
.venv/bin/ninja                                   # must print the SHA-1 match

# 2. TM-CE beside the checkout, and the disc the native game reads
git clone https://github.com/Zane-/TrainingMode ../TrainingMode
.venv/bin/python tools/overlay_build.py
.venv/bin/python tools/tmce_disc.py --iso "<your 1.02 iso>"   # build/disc

# 3. Aurora's source at the pinned revision, and newlib's headers
git clone https://github.com/r-burns/aurora build/deps/aurora
git -C build/deps/aurora checkout e6a6f02ace4146e8a2f648d5c274dbb7dd89665c
curl -LO https://sourceware.org/pub/newlib/newlib-4.5.0.20241231.tar.gz
mkdir -p build/deps/newlib-src && tar xzf newlib-*.tar.gz -C build/deps/newlib-src
.venv/bin/python tools/windows/newlib_headers.py \
    build/deps/newlib-src/newlib-4.5.0.20241231 build/deps/newlib-ppc/include

# 4. The type table: a PowerPC DWARF build, and melee-dat from cargo
export AURORA_SRC=$PWD/build/deps/aurora
export NEWLIB_INCLUDE=$PWD/build/deps/newlib-ppc/include
cmake --preset ppc-dwarf -B build/dwarf \
    "-DCMAKE_C_FLAGS=-Wno-error=incompatible-function-pointer-types"
cmake --build build/dwarf
CARGO_TARGET_DIR=$PWD/build/cargo cargo build --release -p melee-dat
build/cargo/release/melee-dat types export -o build/GALE01/dat/types.bin \
    --dwarf build/dwarf/melee.elf

# 5. Aurora, Dawn and SDL3 as 32-bit (the long step: Dawn is most of it;
#    JOBS=6 left the Deck usable), then the game
JOBS=6 tools/aurora32/build.sh
.venv/bin/python tools/native_build.py            # build/native/melee_headless
.venv/bin/python tools/native_build.py --window   # build/native-window/melee_native
```

`native_build.py` takes the cargo `melee-dat` by itself when there is no
Nix one. `tools/aurora32/build.sh` builds Aurora's own 32-bit sqlite: left
to CMake, it found the container's 64-bit one and the link failed.

## Playing

```sh
.venv/bin/python tools/melee_client/client.py --fullscreen
python tools/melee_client/client.py --devices     # which controllers it sees
```

- **Inside the container**: the game is linked against the container's
  32-bit libraries.
- **The screen's refresh rate**: the game makes a picture every 16.7 ms.
  The Deck OLED's screen runs at 90 Hz, where pictures are shown for one
  refresh or two in turn (11 ms, 22 ms): it judders, and `--timing`
  counts about 10 of 60 frames late. In Game Mode, set the refresh rate to
  60 Hz for the game (Quick Access, Performance, per-game profile).
  Desktop Mode offers only 90 Hz.
- **A GameCube adapter** (Nintendo's, or one in its mode such as a Lossless
  adapter in Wii U mode): read straight from USB (`gcadapter.c`). On the
  Deck the logged-in user already had access to it, with no udev rule;
  elsewhere it needs the rule Dolphin asks for. Only one program can have
  it: close Dolphin first. Not tried yet in Game Mode, where Steam Input
  may take it (turn Steam Input off for the game).
- **From Game Mode**: add a script that runs `distrobox enter meleedev --
  bash -lc 'cd ~/Projects/melee && exec .venv/bin/python
  tools/melee_client/client.py --fullscreen'` to Steam as a non-Steam
  game (Desktop Mode, Steam, "Add a Non-Steam Game").

## Trained opponents (slippi-ai)

```sh
git clone https://github.com/vladfi1/slippi-ai ~/Games/Melee/slippi-ai
cd ~/Games/Melee/slippi-ai && python3 -m venv venv && venv/bin/pip install -e ".[jax,tf]"
cd ~/Projects/melee
.venv/bin/python tools/melee_client/opponents.py --download --main fox --list
.venv/bin/python tools/melee_client/opponents.py --download --main fox
```

`--download` fetches, from the public folder slippi-ai's README links
(`data/models/slippi-ai-drive.json` has each file's id), the newest model
trained against your character for every character that has one: 15
files, 1.3 GB, for Fox. `--ranks` adds the rank models (Gold to
Grandmaster, 391 MB each). Drive sometimes refuses for a while after many
large downloads; run it again later and it fetches only what is missing.

In Versus, a card set to "AI model" starts on that character's specialist
against yours (`client.vpick_model`).

How fast a model answers decides whether it can be played: the game asks
every frame (16.7 ms) and the model must answer every frame in order.
Measured on the Deck, each answer awaited (answers per frame):

| Model | Median | 99th percentile |
|-|-|-|
| d18 specialist (42 MB) | 6.6 ms | 8.8 ms |
| d21 specialist (179 MB) | 8.6 ms | 10.5 ms |
| Rank model (391 MB) | 17.7 ms | 20.4 ms |
| Rank model, its ONNX export (196 MB, 4 threads) | 19.4 ms | (raw `session.run`) |

The rank models are about 6% too slow for the Deck's CPU (which runs at
its 3.5 GHz the whole time): over a long match they fall behind. Nothing
tried brought them under 16.7 ms: XLA's thread settings, bfloat16 or
float16 weights (slippi-ai casts them on every call: 59 ms), the ONNX
exports. The specialists have room to spare.

## Verified (2026-11-18, Steam Deck OLED, SteamOS)

- Matching build: the retail SHA-1, 1,133 of 1,133 files.
- Overlay build: "OK: vanilla layout preserved". Not booted in Dolphin.
- Native: headless and window variants built; a 600-frame match headless;
  the client at 60 frames a second (1,800 frames in 30.3 s); played in
  Game Mode with the Deck's controls.
- `tests/native/gcadapter.py`: 11 of 11, a controller on port 1 read live.
- `tests/client/versus.py` 31 of 31, `tests/client/versus_select.py` 18
  of 18.
