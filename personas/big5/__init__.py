"""A5 — Big Five numeric dials (Big5-Scaler, arXiv:2508.06149).

Persona = short prompt stating each trait's score on a 0-10 scale (their best
config: coarse scale, trait-level not facet-level). Scores are sampled from
human population norms (means/SDs on a 1-5 BFI scale, same as
replicant/src/replicant/sampling/big5.py) and rescaled to 0-10.

Known limits: BFI factor structure is invalid in LLMs (control method, expected
weak); Neuroticism expression is suppressed by safety training.
"""

import random

NORMS = {  # BFI-2 domain norms on a 1-5 scale: (mean, sd)
    "extraversion": (3.2, 0.9),
    "agreeableness": (3.7, 0.7),
    "conscientiousness": (3.4, 0.7),
    "negative emotionality": (2.9, 0.8),
    "open-mindedness": (3.7, 0.7),
}

GLOSS = {
    "extraversion": "sociable and assertive",
    "agreeableness": "compassionate and cooperative",
    "conscientiousness": "disciplined and dependable",
    "negative emotionality": "anxious and easily stressed",
    "open-mindedness": "imaginative and curious",
}


def _one(rng):
    lines = []
    for trait, (mean, sd) in NORMS.items():
        score = min(5.0, max(1.0, rng.gauss(mean, sd)))
        score10 = round((score - 1) / 4 * 10)  # 1-5 -> 0-10
        lines.append(
            f"People with a high {trait} score are {GLOSS[trait]}. "
            f"Your {trait} score is {score10} out of 10."
        )
    lines.append("You are a person with this personality, and you respond based on it.")
    return " ".join(lines)


def sample(n, seed=None):
    rng = random.Random(seed)
    return [_one(rng) for _ in range(n)]
