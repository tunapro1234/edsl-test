"""A8/A9 — Homo Silicus one-liners + calibrated mixture (Horton 2023, GSA selection).

Each persona is a single sentence stating a preference type. The population is a
MIXTURE over types. Weights come from OUR calibration (weights.json, written by
calibrate.py: dictator-game probe fitted to Engel 2011 human targets); until that
file exists we fall back to Horton's published GPT-4o weights. One-liners as in
replicant/src/replicant/personas/economics/homo_silicus_2301_07543/.
"""

import json
import os
import random

TYPES = {
    "self_interested": "You only care about your own pay-off.",
    "efficient": "You only care about the total pay-off of all players.",
    "inequity_averse": "You only care about fairness between players.",
}

HORTON_WEIGHTS = {"self_interested": 0.53, "efficient": 0.37, "inequity_averse": 0.10}


def weights():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weights.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)["weights"]
    return HORTON_WEIGHTS


def sample(n, seed=None):
    rng = random.Random(seed)
    w = weights()
    types = rng.choices(list(w), weights=list(w.values()), k=n)
    return [TYPES[t] for t in types]
