"""Persistent agent banks: the SAME virtual person plays every game.

For each persona method we sample N personas ONCE (seed 1000) and freeze them
in agents_bank/<method>.json as {"agent_id": persona_text}. Every later run —
any game, any model — reuses these, so within-person consistency can be
analyzed across games. Growing a bank keeps existing ids stable.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from personas import sample_personas  # noqa: E402

BANK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents_bank")
BANK_SEED = 1000


def bank(method, n):
    """Return {agent_id: persona_text} with at least n agents, frozen on disk."""
    path = os.path.join(BANK_DIR, f"{method}.json")
    agents = {}
    if os.path.exists(path):
        with open(path) as f:
            agents = json.load(f)
    if len(agents) < n:
        texts = sample_personas(method, n, seed=BANK_SEED)  # deterministic prefix
        agents = {f"{method}-{i:03d}": t for i, t in enumerate(texts)}
        with open(path, "w") as f:
            json.dump(agents, f, indent=1)
    return dict(list(agents.items())[:n])
