"""Sound in the native client, checked off screen (nothing on the speakers:
the virtual display's runs use SDL's dummy audio driver).

    python tests/client/sound.py

The owner (2026-11-13): "Let's add the native sound effects to our menu
navigation + button clicks as well as the main menu music and ensure
in-game audio works as well!" The game's mix is written to a file
(MELEE_AUDIO_RAW). Checked: the main menu's music on the menus, the game's
own menu sounds for moving, choosing and going back (as its menus use
them), the stage's music in a match, the menu music again after it, and in
a drill that reuses the match the stage's music put back.
"""
import math
import os
import struct
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))

import client  # noqa: E402
import window  # noqa: E402
import pausekeys  # noqa: E402
from pausekeys import Chooser  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def loudness(path, seconds=0.5):
    """RMS of the mix's last `seconds`."""
    data = open(path, "rb").read()
    n = int(32000 * seconds) * 4
    s = struct.unpack("<%dh" % (len(data[-n:]) // 2), data[-n:])
    return math.sqrt(sum(x * x for x in s) / max(1, len(s)))


def main():
    tmp = tempfile.mkdtemp(prefix="melee-sound-")
    raw = os.path.join(tmp, "mix.raw")
    save = os.path.join(tmp, "client.json")
    w = c = None
    played = []

    def frames(n):
        for _ in range(n):
            c.frame()

    def tap(key, after=6):
        w.key(key)
        frames(2)
        w.key(key, False)
        frames(after)

    try:
        w = window.Window(window=(1280, 720), sound_file=raw)
        w.step(30)
        c = client.Client(w, source="keyboard", save=save,
                          out=tempfile.mkdtemp(prefix="melee-ui-"))
        real = c.sfx
        c.sfx = lambda n: (played.append(n), real(n))
        w.pace(False)
        frames(90)
        check("the main menu plays the main menu's music",
              w.song() == "menu01.hps" and loudness(raw) > 300,
              "%s, rms %.0f" % (w.song(), loudness(raw)))

        del played[:]
        tap("Right")
        tap("Left")
        check("moving between panels: the game's move sound each time",
              played == [c.SFX_MOVE, c.SFX_MOVE], str(played))
        del played[:]
        tap("x")
        check("A on Train: its forward sound", played == [c.SFX_FORWARD]
              and c.screen == "chars", "%s %s" % (played, c.screen))
        del played[:]
        tap("z")
        check("B: its back sound", played == [c.SFX_BACK] and
              c.screen == "main", "%s %s" % (played, c.screen))
        del played[:]
        tap("Right")
        tap("Right")
        tap("Right")                  # into the panel at the edge: no move
        check("pushing past the last panel makes no sound",
              played.count(c.SFX_MOVE) <= 2, str(played))
        while c.focus != "train":
            tap("Left")

        # ---- free play: the stage's music, then the menus' again ----------
        tap("x")
        tap("Down")
        tap("Right")                  # Marth: free play
        tap("x", after=150)
        stage_song = w.song()
        check("a match plays its stage's music, not the menu's",
              c.screen == "match" and stage_song not in (None, "menu01.hps")
              and loudness(raw) > 300, "%s, %s, rms %.0f" % (
                  c.screen, stage_song, loudness(raw)))
        del played[:]
        pausekeys.leave(c, w, "back", frames)
        frames(30)
        check("the pause menu sounds its moves and the choice",
              c.SFX_MOVE in played and c.SFX_FORWARD in played, str(played))
        check("back at the character select: the menu music again",
              c.screen == "chars" and w.song() == "menu01.hps",
              "%s, %s" % (c.screen, w.song()))

        # ---- a drill on a match it keeps: the stage's music back ---------
        tap("z")
        tap("x")                      # Train: the character select at Fox?
        tap("Up")                     # from Marth, the row above
        tap("Left")
        for _ in range(30):
            if c.roster[c.at]["id"] == "fox":
                break
            tap("Left", after=2)
        if c.roster[c.at]["id"] != "fox":
            raise RuntimeError("Fox not found: at %s" % c.roster[c.at]["id"])
        tap("x")                      # Fox's course hub
        tap("x")                      # the first part's drills
        seen = dict(n=0)

        def person(game, frame):
            seen["n"] += 1
            if seen["n"] == 1:
                game.key("x", False)
            if seen["n"] == 60:
                seen.setdefault("songs", []).append(game.song())
                seen["out"] = Chooser(c, "list")
            if "out" in seen:
                seen["out"](game)

        c.person = person
        for k in range(2):            # the same drill twice: the same match
            seen.update(n=0)
            seen.pop("out", None)
            w.key("x")
            for _ in range(20):
                c.frame()
                if c.screen == "list" and "out" in seen:
                    break
            w.key("x", False)
            frames(20)
            seen.setdefault("menu", []).append(w.song())
        songs = seen.get("songs", [])
        check("a drill plays its stage's music, and again when it is "
              "played again on the same match after the menus",
              len(songs) == 2 and songs[0] == songs[1] and
              songs[0] not in (None, "menu01.hps"), str(songs))
        check("and the drill list has the menu music",
              seen.get("menu") == ["menu01.hps", "menu01.hps"],
              str(seen.get("menu")))
        bad = [line.strip()[:160] for line in w.log
               if "aurora" in line and ("warn" in line or "error" in line)]
        check("the interface raised no warnings", not bad,
              "; ".join(bad[:3]))
    finally:
        if w is not None:
            w.close()
        left = window.leftovers()
        check("nothing left running", not left, str(left))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
