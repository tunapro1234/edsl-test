"""A6 — GPS economic preference profile (Falk et al. 2018 QJE) + SVO dial.

Persona = the six Global Preferences Survey traits (risk taking, patience,
altruism, trust, positive/negative reciprocity) + a prosociality (SVO) dial,
stated numerically on a 0-10 scale in Big5-Scaler format. Trait wordings follow
the GPS survey items.

Sampling: GPS variables are standardized (world mean 0, sd 1); we draw each
trait from N(0,1) independently and map +-2.5 sd onto 0-10.
TODO: replace with real GPS individual-level JOINT data (briq registration) —
independence is wrong in humans; Turkey subset enables the B9 idea.
"""

import random

TRAITS = {
    "risk taking": "willingness to take risks",
    "patience": "willingness to give up something today in order to gain more in the future",
    "altruism": "willingness to give to good causes without expecting anything in return",
    "trust": "belief that other people have only the best intentions",
    "positive reciprocity": "willingness to return a favor",
    "negative reciprocity": "willingness to punish unfair treatment, even at a cost to yourself",
    "prosociality": "concern for others' payoffs relative to your own",
}


def _dial(rng):
    return max(0, min(10, round(5 + 2 * rng.gauss(0, 1))))


def _one(rng):
    lines = [f"Your {t} ({gloss}) is {_dial(rng)} out of 10." for t, gloss in TRAITS.items()]
    lines.append("You are a person with these preferences, and you decide based on them.")
    return " ".join(lines)


def sample(n, seed=None):
    rng = random.Random(seed)
    return [_one(rng) for _ in range(n)]
