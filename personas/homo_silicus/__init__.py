"""A8/A9 — Homo Silicus types + calibrated mixture (Horton 2023/2026 + GSA selection).

Each persona = one GSA "humanizing" sentence + one Horton-style preference
one-liner. The population is a MIXTURE over 6 social-preference types, all
grounded in Charness & Rabin (2002, QJE) — the theory Horton's personas come from:

  self_interested / efficient / inequity_averse : Horton's exact types
      (arXiv:2301.07543 Fig. 3; "both players" -> "all players" for n-player games)
  competitive : CR 2002 "competitive preferences" (payoff relative to others)
  reciprocal  : CR 2002 reciprocity ("sometimes punish unfair behavior", abstract)
  selfish_but_fair : verbatim GSA example prompt "You are self-interested but fair."
      (Manning et al., General Social Agents, Sec. 2.1)

The PREFIX sentence is the one GSA prepends to all its prompts (GSA Table 2
notes); it pushes the model off deterministic corner behavior.

Weights come from OUR calibration (weights.json, written by calibrate.py:
fitted on the 6 Charness-Rabin allocation menus, validated on Engel-2011
dictator moments). If weights.json is missing or its types are stale, we fall
back to Horton's published GPT-4o weights for his 3 types (paper Sec. 2.2.1)
and 0 for the new types.

Sampling: deterministic largest-remainder quotas (the most representative
group of n), shuffled by seed. Horton samples personas randomly instead; with
n=4 that drops 10%-types two times out of three, so we quota. One-line change
to revert.
"""

import json
import os
import random

PREFIX = ("You are a human being with all the cognitive biases and heuristics "
          "that come with it.")

TYPES = {
    "self_interested": "You only care about your own pay-off.",
    "efficient": "You only care about the total pay-off of all players.",
    "inequity_averse": "You only care about fairness between players.",
    "competitive": "You only care about doing better than the other players.",
    "reciprocal": ("You only care about reciprocity: you are generous to those "
                   "who act fairly, and you punish unfair behavior even at a "
                   "cost to yourself."),
    "selfish_but_fair": "You are self-interested but fair.",
}

PERSONAS = {t: f"{PREFIX} {s}" for t, s in TYPES.items()}

# Horton's GPT-4o mixture (w_E=.37, w_I=.10, w_S=.53), Sec. 2.2.1 of the paper;
# types Horton didn't have start at 0 until calibrate.py fits them.
FALLBACK_WEIGHTS = {
    "self_interested": 0.53, "efficient": 0.37, "inequity_averse": 0.10,
    "competitive": 0.0, "reciprocal": 0.0, "selfish_but_fair": 0.0,
}


def weights():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weights.json")
    try:
        with open(path) as f:
            w = json.load(f)["weights"]
        if set(w) == set(TYPES):
            return w
        print("homo_silicus: weights.json types are stale — using fallback weights")
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
    return FALLBACK_WEIGHTS


def _quota(w, n):
    """Largest-remainder rounding of weights into integer counts summing to n."""
    raw = {t: w[t] * n for t in w}
    counts = {t: int(raw[t]) for t in w}
    leftover = n - sum(counts.values())
    for t in sorted(raw, key=lambda t: raw[t] - counts[t], reverse=True)[:leftover]:
        counts[t] += 1
    return counts


def sample(n, seed=None):
    rng = random.Random(seed)
    pool = [t for t, c in _quota(weights(), n).items() for _ in range(c)]
    rng.shuffle(pool)
    return [PERSONAS[t] for t in pool]
