"""A slippi-ai policy as a process of its own, for the native client.

    ~/Games/Melee/slippi-ai/venv/bin/python tools/melee_actor/policy_server.py

The client runs in the project's Python; slippi-ai needs its own (its
packages do not load in the other). So the policy sits here, in slippi-ai's
interpreter, and the two talk in lines of JSON over this process's
standard input and output (tools/melee_client/opponents.py is the other
end):

    {"load": MODEL, "port": 1, "opponent": 0, "stage": NAME}  ->  {"ready": true, "delay": N}
    {"frame": {"p": [fighter, fighter], "pads": [pad, pad]}}  ->  {"pad": {buttons, stick, cstick, l}}
    {"again": true}                                            a new match: -> {"ok": true}

The game is never made to wait for an answer: the client asks about the
frame just played and uses the answer one frame later, which the policy is
told about (`console_delay=1`: it reacts one frame sooner to make up).
Anything a library prints goes to standard error; the answers have this
process's original standard output to themselves.
"""
import json
import os
import sys

answers = os.fdopen(os.dup(1), "w")
os.dup2(2, 1)                      # stray prints: to standard error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import policy  # noqa: E402  (sets up the paths to slippi-ai and our tools)
from native import BUTTONS, Fighter  # noqa: E402


class Game:
    """What the policy bridge asks of a game, filled from a message."""

    class _Pads:
        def __init__(self):
            self.pads = [dict(buttons=0, lx=0, ly=0, cx=0, cy=0, lt=0, rt=0)
                         for _ in range(4)]

    def __init__(self):
        self.h = Game._Pads()
        self.p = [None, None]
        self.out = None

    def fighter(self, i):
        return Fighter(self.p[i] if i < len(self.p) else None)

    def pad(self, port, buttons=(), stick=(0, 0), cstick=(0, 0), l=0, r=0):
        self.out = dict(buttons=list(buttons), stick=list(stick),
                        cstick=list(cstick), l=l)
        p = self.h.pads[port]
        p["buttons"] = sum(BUTTONS[b.upper()] for b in buttons)
        p["lx"], p["ly"] = (int(round(max(-1, min(1, v)) * 127))
                            for v in stick)
        p["cx"], p["cy"] = (int(round(max(-1, min(1, v)) * 127))
                            for v in cstick)
        p["lt"] = int(l * 255)


def say(message):
    answers.write(json.dumps(message) + "\n")
    answers.flush()


def main():
    game, player, port, opponent = Game(), None, 1, 0
    for line in sys.stdin:
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if "load" in msg:
            from slippi_ai import eval_lib, saving
            port, opponent = msg.get("port", 1), msg.get("opponent", 0)
            try:
                player = policy.PolicyPlayer(
                    game, port, opponent,
                    os.path.join(policy.SLIPPI_AI, "deployed_models",
                                 msg["load"]),
                    stage=msg.get("stage", "final-destination"))
                # one frame of the answer's own lateness is ours
                state = saving.load_state_from_disk(os.path.join(
                    policy.SLIPPI_AI, "deployed_models", msg["load"]))
                player.agent = eval_lib.build_delayed_agent(
                    state, console_delay=1, batch_size=1, name=None)
                player.delay = player.agent.policy.delay
                say(dict(ready=True, delay=int(player.delay)))
            except Exception as e:      # a model that does not load
                player = None
                say(dict(ready=False, error="%s: %s" % (
                    type(e).__name__, str(e)[:300])))
        elif "again" in msg:
            if player is not None:
                player.first = True
            say(dict(ok=True))
        elif "frame" in msg and player is not None:
            frame = msg["frame"]
            game.p = frame["p"]
            for i, pad in enumerate(frame.get("pads", [])):
                if pad is not None and i != port:
                    game.h.pads[i].update(pad)
            if not (game.p[port] and game.p[opponent]):
                say(dict(pad=None))
                continue
            player.act()
            say(dict(pad=game.out))


if __name__ == "__main__":
    main()
