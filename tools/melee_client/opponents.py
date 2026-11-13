"""Who plays the other fighter: a trained slippi-ai model, the game's own
CPU, or nobody.

The models are the ones in a slippi-ai checkout (~/Games/Melee/slippi-ai,
or $SLIPPI_AI), in deployed_models/: most are one character trained against
one other (falco_d18_vs_fox_v4: Falco against Fox, reacting 18 frames
late), some a character against itself (ditto) or against everyone
(imitation), and some are not tied to a character (named for a rank).
`models(bot, player)` lists the ones that fit a pairing, best fit first.

A model runs in a process of its own in slippi-ai's Python
(tools/melee_actor/policy_server.py); `Bot` is this side of it. The game
never waits for it: `ask()` about the frame just played, `answer()` a
frame later.
"""
import json
import os
import re
import select
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "melee_native"))
from native import die_with_parent  # noqa: E402

SLIPPI_AI = Path(os.environ.get(
    "SLIPPI_AI", os.path.expanduser("~/Games/Melee/slippi-ai")))
PYTHON = SLIPPI_AI / "venv" / "bin" / "python"
MODELS = SLIPPI_AI / "deployed_models"
# the client's character ids -> the names slippi-ai's models use
SHORT = {"fox": "fox", "falco": "falco", "marth": "marth", "sheik": "sheik",
         "captain-falcon": "falcon", "jigglypuff": "puff", "peach": "peach",
         "ice-climbers": "ics", "samus": "samus", "yoshi": "yoshi",
         "pikachu": "pikachu", "luigi": "luigi", "dr-mario": "doc",
         "donkey-kong": "dk", "ganondorf": "ganon", "link": "link"}
RANKS = ("super-gm", "gm", "master", "diamond", "plat", "gold", "silver",
         "bronze")


def available():
    """Is there a slippi-ai to run models with?"""
    return PYTHON.exists() and MODELS.is_dir()


def models(bot, player):
    """The models that can play `bot` against `player` (character ids),
    best fit first: [(name, what it is in a few words)]."""
    if not available():
        return []
    names = sorted(p.name for p in MODELS.iterdir())
    b, p = SHORT.get(bot), SHORT.get(player)
    out, seen = [], set()

    def add(name, what):
        if name not in seen:
            seen.add(name)
            out.append((name, what))

    def newest(found):
        # later versions and the quicker reaction first
        return sorted(found, key=lambda n: (
            [int(x) for x in re.findall(r"\d+", n.split("_", 2)[-1])],
            n), reverse=True)

    if b:
        mine = [n for n in names if n.startswith(b + "_")]
        if p:
            for n in newest([n for n in mine if "_vs_%s" % p in n and
                             re.search(r"_vs_%s(_|$)" % p, n)]):
                add(n, "trained for this pairing")
        if b == p:
            for n in newest([n for n in mine if "_ditto" in n]):
                add(n, "trained against its own character")
        for n in newest([n for n in mine if "_imitation" in n]):
            add(n, "trained on people's games")
        for n in newest(mine):
            m = re.search(r"_vs_([a-z]+)", n)
            add(n, "trained against %s" % m.group(1) if m else
                "trained against its own character" if "_ditto" in n else
                "trained for this character")
    for rank in RANKS:
        for n in newest([n for n in names if n == rank or
                         n.startswith(rank + "-")]):
            add(n, "any character, from games at that rank")
    return out


class Bot:
    """A model playing one port, in its own process."""

    def __init__(self, model, port=1, opponent=0, stage="final-destination"):
        self.model = model
        self.loaded = None        # None: loading; True or False after
        self.error = ""
        self.delay = 0
        self.asked = self.answered = 0
        self._buf = b""
        self.p = subprocess.Popen(
            [str(PYTHON), str(ROOT / "tools/melee_actor/policy_server.py")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, start_new_session=True,
            preexec_fn=die_with_parent)
        self._send(dict(load=model, port=port, opponent=opponent,
                        stage=stage))

    def _send(self, message):
        try:
            self.p.stdin.write((json.dumps(message) + "\n").encode())
            self.p.stdin.flush()
        except (BrokenPipeError, ValueError):
            self.loaded, self.error = False, "the model's process ended"

    def _line(self, wait):
        """One line from the process if there is one within `wait`."""
        fd = self.p.stdout.fileno()
        while b"\n" not in self._buf:
            if not select.select([fd], [], [], wait)[0]:
                return None
            chunk = os.read(fd, 65536)
            if not chunk:
                self.loaded, self.error = False, "the model's process ended"
                return None
            self._buf += chunk
            wait = 0
        line, _, self._buf = self._buf.partition(b"\n")
        return json.loads(line)

    def ready(self):
        """Has the model loaded? None while it is still loading."""
        if self.loaded is None:
            msg = self._line(0)
            if msg is not None and "ready" in msg:
                self.loaded = bool(msg["ready"])
                self.error = msg.get("error", "")
                self.delay = msg.get("delay", 0)
        return self.loaded

    def ask(self, fighters, pads):
        """What would you press, seeing this frame?"""
        if self.loaded:
            self._send(dict(frame=dict(p=fighters, pads=pads)))
            self.asked += 1

    def answer(self, wait=0.0):
        """The newest answer that has come (older ones are dropped), as
        keywords for Native.pad(); None if there is none."""
        pad = None
        while self.loaded and self.answered < self.asked:
            msg = self._line(wait if pad is None else 0)
            if msg is None:
                break
            if "pad" in msg:
                self.answered += 1
                if msg["pad"] is not None:
                    pad = msg["pad"]
        if pad is None:
            return None
        return dict(buttons=pad["buttons"], stick=tuple(pad["stick"]),
                    cstick=tuple(pad["cstick"]), l=pad["l"])

    def again(self):
        """A new match with the same model."""
        if self.loaded:
            self.answer(0.2)
            self._send(dict(again=True))
            self._line(1.0)

    def close(self):
        try:
            os.killpg(self.p.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            self.p.wait(timeout=5)
        except Exception:
            pass


if __name__ == "__main__":
    print("slippi-ai:", "found" if available() else "not found", SLIPPI_AI)
    for pair in (("falco", "fox"), ("fox", "fox"), ("bowser", "marth")):
        got = models(*pair)
        print("%s against %s: %d models; first: %s" % (
            pair[0], pair[1], len(got), got[:3]))
