"""The client's settings (Settings, in the main menu): kept in the progress
file under "settings" and given to the game process.

Input delay is Slippi's online delay, offline: 2 frames unless changed, so
that practice keeps the timing of the matches it is for (the owner,
2026-11-13: "We need that so practice is consistent. Normally it defaults
to 2 frames of input delay"). The menus the client draws read the
controller directly and are not delayed.
"""

DEFAULTS = {
    "delay": 2,                  # frames
    "rumble": [True, True, True, True],
    "ucf": True,
    "music": 100,                # volumes, 0 to 100
    "effects": 100,              # the game's sounds in matches and drills
    "menus": 100,                # the menus' own sounds
    "sidebar": True,             # the column beside the game's picture
    "size": [1280, 720],         # the window's, when it is not fullscreen
    "inputs": "off",             # TM-CE's input display: whose (INPUTS)
    "coach": 3,                  # misses in a row before the coach; 0 off
}
SIZES = ([1280, 720], [1600, 900], [1920, 1080], [2560, 1440])
INPUTS = ("off", "you", "opponent", "both")
COACH = (0, 2, 3, 4, 5)          # the coach's card after this many misses
DELAY_MAX = 9                    # as far as Slippi's own setting goes
FRAME_MS = 1000.0 * 1001 / 60000  # the console's 59.94 frames a second


def get(progress):
    """The settings, defaults filled in (kept in `progress.data`)."""
    s = progress.data.setdefault("settings", {})
    for key, value in DEFAULTS.items():
        if key not in s:
            s[key] = list(value) if isinstance(value, list) else value
    s["delay"] = max(0, min(DELAY_MAX, int(s["delay"])))
    s["rumble"] = [bool(x) for x in (list(s["rumble"]) + [True] * 4)[:4]]
    for key in ("music", "effects", "menus"):
        s[key] = max(0, min(100, int(s[key])))
    if list(s["size"]) not in [list(x) for x in SIZES]:
        s["size"] = list(DEFAULTS["size"])
    if s["inputs"] not in INPUTS:
        s["inputs"] = DEFAULTS["inputs"]
    if s["coach"] not in COACH:
        s["coach"] = DEFAULTS["coach"]
    return s


def apply(w, s):
    """Give the game process the settings. A build without one of the
    commands keeps going without it."""
    for fn in (lambda: w.delay(s["delay"]),
               lambda: [w.rumble(p, on) for p, on in enumerate(s["rumble"])],
               lambda: w.ucf(bool(s["ucf"])),
               lambda: w.volume(s["music"], s["menus"])):
        try:
            fn()
        except Exception:
            pass


def delay_ms(frames):
    return frames * FRAME_MS
