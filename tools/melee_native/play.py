"""Play the native build yourself: a window on this desktop, a match, your
controller or the keyboard.

    python tools/melee_native/play.py                    # Fox against a standing Marth
    python tools/melee_native/play.py falco sheik --stage battlefield --cpu
    python tools/melee_native/play.py --input keyboard   # or pad0, pad1, ...
    python tools/melee_native/play.py --input2 pad1      # a second person

Needs the window build (tools/aurora32/build.sh once, then
tools/native_build.py --window). There is no sound yet. Close the window or
press Ctrl-C here to stop.

The keyboard as a controller: arrows are the stick (with left shift, a
light push); I J K L the C stick; X is A; Z is B; C and V are Y and X
(jump); A and S are L and R; D is Z; Return is Start; T F G H the D-pad.

A controller is read through SDL: the buttons are taken by where they are
(the bottom one is A, the left one B, the right one X, the top one Y; the
right shoulder is Z), the left stick is the stick and the right one the C
stick. A GameCube controller on an adapter needs SDL to be able to open the
adapter (the same permissions Dolphin needs).

--offscreen runs the same thing on a virtual display for a number of
frames, with nothing on the desktop: that is how this file is tested.
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import window  # noqa: E402
from native import CHARACTERS, STAGES, NativeError  # noqa: E402


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.split("\n")[0],
        epilog="characters: %s\nstages: %s" % (
            " ".join(sorted(CHARACTERS)), " ".join(sorted(STAGES))),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("p1", nargs="?", default="fox")
    ap.add_argument("p2", nargs="?", default="marth")
    ap.add_argument("--stage", default="final-destination")
    ap.add_argument("--input", default="auto",
                    help="who plays port 1: auto (the first controller, "
                         "else the keyboard), keyboard, pad0, pad1, ...")
    ap.add_argument("--input2", default=None,
                    help="a second person on port 2 (pad1, keyboard, ...)")
    ap.add_argument("--cpu", action="store_true",
                    help="the game's own CPU plays port 2")
    ap.add_argument("--vsync", action="store_true",
                    help="present with the display's refresh")
    ap.add_argument("--offscreen", action="store_true",
                    help="on a virtual display (a test of this file)")
    ap.add_argument("--software", action="store_true",
                    help="with --offscreen: draw without the GPU")
    ap.add_argument("--frames", type=int, default=0,
                    help="stop after this many frames of the match")
    ap.add_argument("-v", action="store_true")
    args = ap.parse_args()
    for name, table in ((args.p1, CHARACTERS), (args.p2, CHARACTERS),
                        (args.stage, STAGES)):
        if name not in table:
            sys.exit("unknown: %s (see --help)" % name)
    if args.cpu and args.input2:
        sys.exit("--cpu and --input2 both want port 2")

    w = None
    frames = 0
    began = None
    try:
        w = window.Window(real=not args.offscreen, vsync=args.vsync,
                          gpu=not args.software, verbose=args.v)
        for line in w.log:
            if line.strip().startswith(("Device:", "API:")):
                print(line.strip())
        w.start(args.p1, args.p2, args.stage, p2_human=not args.cpu,
                settle=False)
        w.live(0, args.input)
        if args.input2:
            w.live(1, args.input2)
        w.pace(True)
        print("%s against %s on %s. Close the window to stop." % (
            args.p1, args.p2, args.stage))
        began = time.time()
        while not args.frames or frames < args.frames:
            w.step()
            frames += 1
    except KeyboardInterrupt:
        pass
    except NativeError as e:
        if "the window was closed" not in "".join(w.log[-5:] if w else []):
            print(str(e)[-1500:], file=sys.stderr)
            return 1
    finally:
        if w is not None:
            w.close()
        left = window.leftovers()
        if left:
            print("still running: %s" % left, file=sys.stderr)
    if began and frames:
        took = time.time() - began
        print("%d frames in %.1f s (%.2f a second)" % (
            frames, took, frames / took))
    return 0


if __name__ == "__main__":
    sys.exit(main())
