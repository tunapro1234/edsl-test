"""A5 — Big Five numeric dials (Big5-Scaler, arXiv:2508.06149).

Persona = short prompt stating each trait's score on a 0-10 scale (their best
config: coarse scale, trait-level not facet-level). Scores are sampled from
human population norms on the 1-5 BFI-2 scale and rescaled to 0-10. Trait
glosses are the official BFI-2 facet names (research/datasets/bfi2/, complete:
60 items + scoring key; Soto & John 2017).

Norms provenance: approximate Soto & John 2017 adult internet-sample
descriptives (via replicant/src/replicant/sampling/big5.py). Domains are
sampled INDEPENDENTLY — real BFI-2 domains correlate modestly; fine for a
control method, fix before making population claims.

Known limits: BFI factor structure is invalid in LLMs (paper 04) — this is a
CONTROL method, expected weak; Neuroticism expression is suppressed by safety
training (Big5-Scaler's own finding).
"""

import random

NORMS = {  # 1-5 scale: (mean, sd), ~Soto & John 2017 internet sample
    "extraversion": (3.2, 0.9),
    "agreeableness": (3.7, 0.7),
    "conscientiousness": (3.4, 0.7),
    "negative emotionality": (2.9, 0.8),
    "open-mindedness": (3.7, 0.7),
}

GLOSS = {  # official BFI-2 facet names per domain
    "extraversion": "high in sociability, assertiveness, and energy level",
    "agreeableness": "high in compassion, respectfulness, and trust",
    "conscientiousness": "high in organization, productiveness, and responsibility",
    "negative emotionality": "high in anxiety, depression, and emotional volatility",
    "open-mindedness": "high in intellectual curiosity, aesthetic sensitivity, and creative imagination",
}


def _one(rng):
    lines = []
    for trait, (mean, sd) in NORMS.items():
        score = min(5.0, max(1.0, rng.gauss(mean, sd)))
        score10 = round((score - 1) / 4 * 10)  # 1-5 -> 0-10
        lines.append(
            f"People with a high {trait} score are {GLOSS[trait]}. "
            f"Your {trait} score is {score10} out of 10."
        )  # one line per domain, Big5-Scaler "simple prompt" format
    lines.append("You are a person with this personality, and you respond based on it.")
    return " ".join(lines)


def sample(n, seed=None):
    rng = random.Random(seed)
    return [_one(rng) for _ in range(n)]
