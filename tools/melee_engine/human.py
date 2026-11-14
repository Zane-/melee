"""slippi-ai policies in the engine (docs/ai/melee-engine.md, E4): the
model of the player, and the opponent's body.

The policies imitate people. Played on the player's port, fed what the
person really pressed, a policy is a model of what a person in that spot
does next; and with its 18 frames of delay, what it will press in the next
17 frames is already decided (tools/melee_actor/policy_server.py, `peek`):
a sample of the person's next 17 frames, which the search plays against
instead of "they hold what they hold" (engine.c, `engine player`).

Played on the opponent's port, a policy moves like a person: dash dances,
wavedashes, jumps, shields. `ModelBody` gives its pads with the attacks
taken out (A, B, Z, the C-stick): the body moves, the engine decides what
to hit with and when (opponent.Blend).

Both run in slippi-ai's own Python, a process each (melee_client.opponents
.Bot), on the GPU if there is one.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "melee_client"))
sys.path.insert(0, os.path.join(HERE, "..", "melee_native"))

from native import BUTTONS  # noqa: E402

# Several models at once (the opponent's body, the model of the player):
# each process takes the GPU memory it needs, not most of it up front.
os.environ.setdefault("XLA_PYTHON_CLIENT_PREALLOCATE", "false")
os.environ.setdefault("TF_FORCE_GPU_ALLOW_GROWTH", "true")

ATTACKS = BUTTONS["A"] | BUTTONS["B"] | BUTTONS["Z"]


def find_model(character, against):
    """A deployed model file for `character` against `against` (data/
    character ids, e.g. "marth", "fox"); a ditto or any of the character's
    if there is no specialist."""
    import opponents
    short = {"captain-falcon": "falcon", "jigglypuff": "puff",
             "ice-climbers": "ics", "donkey-kong": "dk",
             "mr-game-and-watch": "gnw", "dr-mario": "doc"}
    c, a = short.get(character, character), short.get(against, against)
    files = sorted(os.listdir(opponents.MODELS)) if \
        opponents.MODELS.exists() else []
    for prefix in ("%s_d18_vs_%s" % (c, a), "%s_d18_ditto" % c,
                   "%s_d18_vs_" % c, "%s_d" % c):
        hits = [f for f in files if f.startswith(prefix)]
        if hits:
            return hits[-1]
    return None


def raw_of(pad):
    """A policy's pad (the server's keywords) as a raw pad."""
    b = sum(BUTTONS[x.upper()] for x in pad.get("buttons", ())
            if x.upper() in BUTTONS)
    lx, ly = (int(round(max(-1, min(1, v)) * 127)) for v in pad["stick"])
    cx, cy = (int(round(max(-1, min(1, v)) * 127)) for v in pad["cstick"])
    lt = int(pad.get("l", 0) * 255)
    if b & (BUTTONS["L"] | BUTTONS["R"]) and lt == 0:
        lt = 255
    return (b, lx, ly, cx, cy, lt, 0)


class _Model:
    def __init__(self, model, port, opponent, stage="final-destination",
                 load_wait=180):
        import opponents
        self.bot = opponents.Bot(model, port=port, opponent=opponent,
                                 stage=stage)
        self.port = port
        t = time.time()
        while self.bot.ready() is None and time.time() - t < load_wait:
            time.sleep(0.1)
        if not self.bot.loaded:
            raise RuntimeError("model %s did not load: %s" % (model,
                                                              self.bot.error))

    def _ask(self, state, pads=None, own=False, peek=0, wait=1.0):
        msg = dict(frame=dict(p=state["p"], pads=pads or [None, None]))
        if own:
            msg["own"] = True
        if peek:
            msg["peek"] = peek
        self.bot._send(msg)
        self.bot.asked += 1
        while True:
            line = self.bot._line(wait)
            if line is None:
                return None
            if "pad" in line:
                self.bot.answered += 1
                return line

    def close(self):
        self.bot.close()


class ModelPlayer(_Model):
    """A model of the person on `port`: each frame told what they really
    pressed, it says what it expects them to press in the coming frames."""

    def predict(self, state, their_pad, frames=17):
        """Raw pads for the next `frames` frames (the person's port), or
        [] if the model did not answer. `their_pad`: what the person had
        this frame (dict buttons, lx, ly, cx, cy, lt, rt as raw values)."""
        pads = [None, None, None, None]
        b = their_pad
        pads[self.port] = dict(buttons=b["buttons"], lx=b["lx"], ly=b["ly"],
                               cx=b["cx"], cy=b["cy"], lt=b.get("lt", 0),
                               rt=b.get("rt", 0))
        line = self._ask(state, pads[:2], own=True, peek=frames)
        if line is None or not line.get("next"):
            return []
        return [raw_of(p) for p in line["next"]]


class ModelBody(_Model):
    """The opponent's movement: the model's pads with the attacks taken
    out (A, B, Z and the C-stick), so it dash dances, jumps, wavedashes and
    shields like a person, and the engine chooses the attacks."""

    def step(self, state, pads=None):
        line = self._ask(state, pads)
        if line is None or line.get("pad") is None:
            return (0, 0, 0, 0, 0, 0, 0)
        b, lx, ly, cx, cy, lt, rt = raw_of(line["pad"])
        return (b & ~ATTACKS, lx, ly, 0, 0, lt, rt)
