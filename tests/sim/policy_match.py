"""slippi-ai policies playing each other in the Python simulator. The match
itself is tests/actor/policy_match.py, which runs on the native build by
default.

    ~/Games/Melee/slippi-ai/venv/bin/python tests/sim/policy_match.py [frames]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "actor"))
sys.argv.append("--sim")
import policy_match  # noqa: E402

if __name__ == "__main__":
    policy_match.main()
