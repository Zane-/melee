"""A slippi-ai (Phillip II) policy as a player, on the native build or in
the headless simulator.

Experiment for docs/ai/melee-actor.md, option A: no Dolphin, no Slippi, no
libmelee connection. Each frame the game state the policy was trained on
(slippi_ai.types.Game) is filled from the game, the policy is stepped, and
its controller is written to the pad. `sim` is a tools/melee_native Native
or a tools/melee_sim Sim: both give the same view of a fighter.

Needs a slippi-ai checkout with its Python environment and trained models.
Run with that environment's interpreter; this file adds the project's own
packages (the simulator needs `unicorn`) to the path:

    ~/Games/Melee/slippi-ai/venv/bin/python tests/actor/policy_match.py

The policy is not instructable: it plays its own game, `policy.delay`
frames behind. See the doc for what that means for the Melee Actor.
"""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
SLIPPI_AI = os.environ.get("SLIPPI_AI",
                           os.path.expanduser("~/Games/Melee/slippi-ai"))


def setup_path():
    """Make the simulator and slippi-ai importable from either
    environment."""
    for p in (os.path.join(ROOT, "tools", "melee_sim"),
              os.path.join(ROOT, "tools", "melee_native"),
              os.path.join(ROOT, "tools"), SLIPPI_AI):
        if p not in sys.path:
            sys.path.insert(0, p)
    # the other environment's packages, after our own
    for venv in (os.path.join(ROOT, ".venv"), os.path.join(SLIPPI_AI, "venv")):
        for sp in glob.glob(os.path.join(venv, "lib", "python*",
                                         "site-packages")):
            if sp not in sys.path:
                sys.path.append(sp)


setup_path()

import numpy as np                                    # noqa: E402

# libmelee's stage numbers (melee/enums.py), by the simulator's stage names
STAGES = {"final-destination": 0x19, "battlefield": 0x18,
          "pokemon-stadium": 0x12, "dream-land": 0x1A,
          "fountain-of-dreams": 0x08, "yoshis-story": 0x06}
# Fighters with more than one air jump (internal kind -> jumps in all)
JUMPS = {0x04: 6, 0x0F: 6}
PAD_BITS = {"A": 0x0100, "B": 0x0200, "X": 0x0400, "Y": 0x0800, "Z": 0x0010,
            "L": 0x0040, "R": 0x0020, "D_UP": 0x0008}


class PolicyPlayer:
    """One fighter played by a trained slippi-ai policy."""

    def __init__(self, sim, port, opponent, model, stage="final-destination",
                 name=None):
        from slippi_ai import eval_lib, saving
        self.sim, self.port, self.opponent = sim, port, opponent
        self.stage = STAGES[stage]
        state = saving.load_state_from_disk(model)
        self.agent = eval_lib.build_delayed_agent(
            state, console_delay=0, batch_size=1, name=name)
        self.delay = self.agent.policy.delay
        self.first = True
        self.frames = 0

    # ---- simulator -> slippi_ai.types.Game ----------------------------------

    def _controller(self, port):
        from slippi_ai.types import Buttons, Controller, Stick
        p = self.sim.h.pads[port]
        half = lambda v: np.float32(v / 127.0 * 0.5 + 0.5)
        return Controller(
            main_stick=Stick(half(p.get("lx", 0)), half(p.get("ly", 0))),
            c_stick=Stick(half(p.get("cx", 0)), half(p.get("cy", 0))),
            shoulder=np.float32(max(p.get("lt", 0), p.get("rt", 0)) / 255.0),
            buttons=Buttons(**{k: np.bool_(bool(p.get("buttons", 0) & bit))
                               for k, bit in PAD_BITS.items()}))

    def _player(self, port):
        from slippi_ai.types import Player
        from slippi_db.parse_libmelee import _EMPTY_NANA
        f = self.sim.fighter(port)
        kind = f.kind
        return Player(
            percent=np.uint16(max(0, int(f.percent))),
            facing=np.bool_(f.facing > 0),
            x=np.float32(f.pos[0]), y=np.float32(f.pos[1]),
            action=np.uint16(f.state),
            invulnerable=np.bool_(f.invulnerable),
            character=np.uint8(kind),
            jumps_left=np.uint8(max(0, JUMPS.get(kind, 2) - f.jumps_used)),
            shield_strength=np.float32(f.shield),
            on_ground=np.bool_(not f.airborne),
            controller=self._controller(port),
            nana=_EMPTY_NANA)

    def game(self):
        from slippi_ai.types import FoDPlatforms, Game, Randall
        from slippi_db.parse_libmelee import _EMPTY_ITEMS
        return Game(
            p0=self._player(self.port), p1=self._player(self.opponent),
            stage=np.uint8(self.stage),
            randall=Randall(np.float32(0), np.float32(0)),
            fod_platforms=FoDPlatforms(np.float32(0), np.float32(0)),
            items=_EMPTY_ITEMS)      # projectiles are not passed on yet

    # ---- one frame ----------------------------------------------------------

    def act(self):
        """Read the game, step the policy, set this fighter's pad. Call once
        per frame, before Sim.step()."""
        from slippi_ai import utils
        game = utils.map_single_structure(
            lambda x: np.expand_dims(np.asarray(x), 0), self.game())
        out = self.agent.step(game, np.array([self.first]))
        self.first = False
        self.frames += 1
        try:
            import jax
            out = jax.device_get(out)
        except ImportError:
            pass
        action = utils.map_single_structure(lambda x: x[0],
                                            out.controller_state)
        c = self.agent.decode_controller(action)
        buttons = [("UP" if k == "D_UP" else k)
                   for k, v in c.buttons._asdict().items() if bool(v)]
        full = lambda v: float(v) * 2.0 - 1.0
        sh = float(c.shoulder)
        self.sim.pad(self.port, buttons=buttons,
                     stick=(full(c.main_stick.x), full(c.main_stick.y)),
                     cstick=(full(c.c_stick.x), full(c.c_stick.y)), l=sh)
        return c
