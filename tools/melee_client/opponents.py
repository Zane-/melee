"""Who plays the other fighter: a trained slippi-ai model, the game's own
CPU, or nobody.

The models are the ones in a slippi-ai checkout (~/Games/Melee/slippi-ai,
or $SLIPPI_AI), in deployed_models/. What each is comes from a catalog,
data/models/slippi-ai.json, made from the models' own training settings
(`python tools/melee_client/opponents.py --catalog`), so the client shows
names, not files (the owner, 2026-11-13: "No raw text. Organized by
difficulty ... Only keep the latest model"):

- a rank: trained on games of players at one Slippi rank, plays a dozen
  characters against anyone: Gold, Platinum, Diamond, Master, Grandmaster;
- a specialist: one character trained against one other (or itself), named
  for the one it is trained against: "Fox Specialist";
- a generalist: one character trained on people's games against everyone.

Each says how late it reacts: "18-frame reaction". Of the models alike
(same kind, character, opponent and reaction) only the newest version is
shown. `models(bot, player)` lists the ones for a pairing, by difficulty.

A model runs in a process of its own in slippi-ai's Python
(tools/melee_actor/policy_server.py); `Bot` is this side of it. The game
never waits for it: `ask()` about the frame just played, `answer()` a
frame later.
"""
import argparse
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
sys.path.insert(0, str(Path(__file__).resolve().parent))
from native import die_with_parent  # noqa: E402
import characters  # noqa: E402

SLIPPI_AI = Path(os.environ.get(
    "SLIPPI_AI", os.path.expanduser("~/Games/Melee/slippi-ai")))
PYTHON = SLIPPI_AI / "venv" / "bin" / "python"
MODELS = SLIPPI_AI / "deployed_models"
CATALOG = ROOT / "data" / "models" / "slippi-ai.json"
# slippi-ai's character names (in model names and training settings) ->
# the client's ids
CHARACTER = {"fox": "fox", "falco": "falco", "marth": "marth",
             "sheik": "sheik", "falcon": "captain-falcon",
             "cptfalcon": "captain-falcon", "puff": "jigglypuff",
             "jigglypuff": "jigglypuff", "peach": "peach",
             "ics": "ice-climbers", "popo": "ice-climbers",
             "samus": "samus", "yoshi": "yoshi", "pikachu": "pikachu",
             "luigi": "luigi", "doc": "dr-mario", "dk": "donkey-kong",
             "ganon": "ganondorf", "link": "link"}
# Slippi's ranks, weakest first; the ones shown are the owner's choice
TIERS = [("bronze", "Bronze"), ("silver", "Silver"), ("gold", "Gold"),
         ("plat", "Platinum"), ("diamond", "Diamond"), ("master", "Master"),
         ("gm", "Grandmaster"), ("super-gm", "Super Grandmaster")]
SHOWN_TIERS = ("gold", "plat", "diamond", "master", "gm")
NAMED = re.compile(r"^(?P<char>[a-z]+)_d(?P<delay>\d+)_(?P<kind>vs_(?P<vs>"
                   r"[a-z]+)|ditto|imitation)(?:_(?P<tag>[a-z]+))?"
                   r"(?:_v(?P<ver>[\d.]+))?$")
RANKED = re.compile(r"^(?P<tier>[a-z-]+?)(?:-v(?P<ver>\d+))?$")


def available():
    """Is there a slippi-ai to run models with?"""
    return PYTHON.exists() and MODELS.is_dir()


# ---- the catalog ---------------------------------------------------------------

def _settings(path):
    """(reaction delay, [characters it plays] or None for all) from the
    training settings pickled at the end of a model file."""
    size = path.stat().st_size
    with open(path, "rb") as f:
        f.seek(max(0, size - 400000))
        tail = f.read()
    words, i = [], 0
    while i < len(tail):       # the short strings, in order
        if tail[i] == 0x8c:
            n = tail[i + 1]
            text = tail[i + 2:i + 2 + n]
            if n and all(32 <= c < 127 for c in text):
                words.append(text.decode())
            i += 2 + n
        else:
            i += 1
    m = re.search(rb"\x8c\x05delay\x94K(.)", tail)
    delay = m.group(1)[0] if m else None
    plays = None
    if "allowed_characters" in words:
        value = words[words.index("allowed_characters") + 1]
        if value != "all":
            plays = sorted({CHARACTER[c] for c in value.split(",")
                            if c in CHARACTER})
    return delay, plays


def _version(text):
    return [int(x) for x in (text or "1").split(".")]


def build_catalog():
    """Every model file, what it is, and whether it is shown."""
    names = {cid: characters.character(cid)["name"]
             for cid in characters.LOOK}
    entries = []
    for path in sorted(MODELS.iterdir()):
        delay, plays = _settings(path)
        e = dict(file=path.name, delay=delay, shown=False)
        m, r = NAMED.match(path.name), RANKED.match(path.name)
        tiers = dict(TIERS)
        if m and m.group("char") in CHARACTER:
            me = CHARACTER[m.group("char")]
            if m.group("kind") == "imitation":
                e.update(kind="generalist", character=me, against=None,
                         name="Generalist")
            else:
                vs = me if m.group("kind") == "ditto" else \
                    CHARACTER.get(m.group("vs"))
                e.update(kind="specialist", character=me, against=vs,
                         name="%s Specialist" % names[vs])
            e.update(version=m.group("ver") or "1", tag=m.group("tag"))
        elif r and r.group("tier") in tiers:
            tier = r.group("tier")
            e.update(kind="rank", tier=tier, name=tiers[tier],
                     version=r.group("ver") or "1",
                     plays=plays or sorted(set(CHARACTER.values())))
        else:
            e.update(kind="other", name=path.name)
        if delay:
            e["about"] = "%d-frame reaction" % delay
        entries.append(e)
    # the newest of models alike
    groups = {}
    for e in entries:
        if e["kind"] == "rank":
            key = ("rank", e["tier"])
        elif e["kind"] in ("specialist", "generalist"):
            key = (e["kind"], e["character"], e.get("against"), e["delay"])
        else:
            continue
        best = groups.get(key)
        if best is None or _version(e["version"]) > _version(
                best["version"]):
            groups[key] = e
    for key, e in groups.items():
        e["shown"] = key[0] != "rank" or key[1] in SHOWN_TIERS
    return entries


def catalog():
    try:
        return json.loads(CATALOG.read_text())["models"]
    except (OSError, ValueError, KeyError):
        return []


def write_catalog():
    entries = build_catalog()
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(dict(
        about="What each slippi-ai model in deployed_models/ is, read from "
              "its own training settings by tools/melee_client/opponents.py "
              "--catalog. `shown`: the newest of models alike (and of the "
              "ranks, the ones the client offers).",
        models=entries), indent=1) + "\n")
    return entries


# ---- who can play a pairing ------------------------------------------------------

def models(bot, player):
    """The shown models that can play `bot` against `player` (character
    ids), by difficulty: the ranks from Gold up, then the generalist, then
    the specialists for this pairing, slowest reaction first.
    [(file, name, what it is)]."""
    if not available():
        return []
    order = [t for t, _ in TIERS]
    out = []
    for e in catalog():
        if not e.get("shown") or not (MODELS / e["file"]).exists():
            continue
        if e["kind"] == "rank" and bot in e.get("plays", ()):
            out.append((0, order.index(e["tier"]), e))
        elif e["kind"] == "generalist" and e["character"] == bot:
            out.append((1, -e["delay"], e))
        elif e["kind"] == "specialist" and e["character"] == bot and \
                e["against"] == player:
            out.append((2, -e["delay"], e))
    out.sort(key=lambda x: (x[0], x[1]))
    return [(e["file"], e["name"], e.get("about", "")) for _, _, e in out]


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


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--catalog", action="store_true",
                    help="write data/models/slippi-ai.json from the models")
    args = ap.parse_args()
    print("slippi-ai:", "found" if available() else "not found", SLIPPI_AI)
    if args.catalog:
        entries = write_catalog()
        print("%d models, %d shown: %s" % (
            len(entries), sum(e["shown"] for e in entries), CATALOG))
    for pair in (("falco", "fox"), ("fox", "fox"), ("bowser", "marth")):
        got = models(*pair)
        print("%s against %s: %s" % (pair[0], pair[1], ", ".join(
            "%s (%s)" % (n, a) for _, n, a in got) or "none"))


if __name__ == "__main__":
    main()
