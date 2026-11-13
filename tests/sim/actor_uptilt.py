"""The Melee Actor's up tilt proof on the Python simulator. The script and
its four situations are in tests/actor/uptilt.py, which runs on the native
build by default.

    python tests/sim/actor_uptilt.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "actor"))
import uptilt  # noqa: E402

if __name__ == "__main__":
    sys.exit(uptilt.main("sim"))
