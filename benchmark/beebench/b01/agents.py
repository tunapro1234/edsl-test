"""Persistent agent banks: the SAME virtual person plays every game.

Banks are APPEND-ONLY (reviewer finding #1): an existing id is NEVER re-bound
to a different persona. Growing a bank from k to n appends n-k fresh agents
drawn with an increment-specific seed (BANK_SEED + k), leaving entries
0..k-1 byte-identical. This protects every method — including the
quota/balanced samplers (homo_silicus, construction) whose sample(n)
composition depends on n BY DESIGN, and twin2k, whose prefix-stability would
otherwise rest on a CPython random.sample implementation detail.

Documented trade-off: an increment is an independent draw, so a GROWN bank's
composition only approximates a single-draw quota for mixture methods —
acceptable, because agent_id stability across results.csv is the binding
contract here.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
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
        k = len(agents)
        extra = sample_personas(method, n - k, seed=BANK_SEED + k)
        for i, text in enumerate(extra, start=k):
            agents[f"{method}-{i:03d}"] = text  # append-only: 0..k-1 untouched
        with open(path, "w") as f:
            json.dump(agents, f, indent=1)
    return dict(list(agents.items())[:n])
